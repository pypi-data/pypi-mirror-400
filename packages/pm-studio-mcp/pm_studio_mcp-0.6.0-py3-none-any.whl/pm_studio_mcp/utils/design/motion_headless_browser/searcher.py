"""
Motion Searcher for appmotion.design

No authentication required. Scrapes public search results.
"""

import logging
from typing import List, Optional, Tuple
from urllib.parse import quote_plus

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

try:
    from .config import MotionConfig
    from .models import MotionItem, MotionSearchResult
except ImportError:
    from config import MotionConfig
    from models import MotionItem, MotionSearchResult


logger = logging.getLogger(__name__)


class MotionSearcher:
    def __init__(self, config: Optional[MotionConfig] = None):
        self.config = config or MotionConfig()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self):
        await self._setup_browser()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._cleanup()

    async def search(self, query: str, max_items: Optional[int] = None) -> MotionSearchResult:
        max_items = max_items or self.config.max_items
        max_items = max(1, min(max_items, 100))
        try:
            if not self.page:
                await self._setup_browser()
            items = await self._search_and_extract(self.page, query, max_items)
            return MotionSearchResult(query=query, items=items, total_found=len(items), status="success")
        except Exception as e:
            logger.error(f"Motion search failed: {e}")
            return MotionSearchResult(query=query, items=[], total_found=0, status="error", message=str(e))

    async def _setup_browser(self):
        self.playwright = await async_playwright().start()
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--autoplay-policy=no-user-gesture-required",
                ],
            )
            self.context = await self.browser.new_context(
                user_agent=self.config.user_agent,
                viewport={"width": 1280, "height": 900},
                java_script_enabled=True,
                accept_downloads=False,
                ignore_https_errors=True,
            )
            self.page = await self.context.new_page()
            self.page.set_default_timeout(self.config.timeout)
        except Exception:
            await self._cleanup()
            raise

    async def _search_and_extract(self, page: Page, query: str, max_items: int) -> List[MotionItem]:
        logger.info(f"🔍 Motion search (tag-based): {query}")
        # AppMotion doesn't support /search?q=...; use tags like /tag/loading
        # Build candidate tag slugs from query
        tokens = [t.strip().lower() for t in query.replace("_", " ").split() if t.strip()]
        candidates = []
        if tokens:
            # exact hyphen-joined and individual tokens
            candidates.append("-".join(tokens))
            candidates.extend(tokens)
        else:
            candidates.append(query.strip().lower())

        # Try visiting candidate tag pages to collect items
        items: List[MotionItem] = []
        seen_links = set()

        async def collect_from_current_page():
            nonlocal items, seen_links
            for _ in range(self.config.max_scrolls):
                batch = await self._extract_from_viewport(page, limit=max_items - len(items))
                for it in batch:
                    key = (it.link_url or it.media_url or it.thumb_url)
                    if key and key not in seen_links:
                        items.append(it)
                        seen_links.add(key)
                        if len(items) >= max_items:
                            break
                if len(items) >= max_items:
                    break
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await page.wait_for_timeout(self.config.scroll_delay_ms)
                await self._dismiss_overlays(page)

        base = "https://appmotion.design"
        # 1) Try /tag/<slug>
        for slug in candidates:
            try:
                url = f"{base}/tag/{quote_plus(slug)}"
                await page.goto(url, wait_until=self.config.wait_until)
                await self._dismiss_overlays(page)
                await collect_from_current_page()
                if items:
                    break
            except Exception:
                continue

        # 2) Try /tags page and click a matching tag
        if not items:
            try:
                await page.goto(f"{base}/tags", wait_until=self.config.wait_until)
                await self._dismiss_overlays(page)
                # Find a tag link whose text matches one of candidates (contains)
                for slug in candidates:
                    try:
                        link = await page.locator(f"a[href^='/tag/']").filter(has_text=lambda t: slug in (t or '').strip().lower()).first
                        if link:
                            await link.click()
                            await page.wait_for_timeout(600)
                            await self._dismiss_overlays(page)
                            await collect_from_current_page()
                            if items:
                                break
                    except Exception:
                        continue
            except Exception:
                pass

        # 3) Try homepage and click 'View all' to tags
        if not items:
            try:
                await page.goto(base, wait_until=self.config.wait_until)
                await self._dismiss_overlays(page)
                # Try to click 'View all' link to /tags
                try:
                    view_all = await page.get_by_text("View all", exact=False)
                    if view_all:
                        await view_all.click()
                        await page.wait_for_timeout(500)
                        await self._dismiss_overlays(page)
                except Exception:
                    pass
                # After that, same as /tags flow
                if page.url.endswith("/tags"):
                    for slug in candidates:
                        try:
                            link = await page.locator(f"a[href^='/tag/']").filter(has_text=lambda t: slug in (t or '').strip().lower()).first
                            if link:
                                await link.click()
                                await page.wait_for_timeout(600)
                                await self._dismiss_overlays(page)
                                await collect_from_current_page()
                                if items:
                                    break
                        except Exception:
                            continue
            except Exception:
                pass

        # Debug snapshot if nothing found
        if not items and getattr(self.config, "debug", False):
            try:
                import os
                os.makedirs(self.config.debug_dir, exist_ok=True)
                await page.screenshot(path=f"{self.config.debug_dir}/empty.png", full_page=True)
                html = await page.content()
                with open(f"{self.config.debug_dir}/empty.html", "w", encoding="utf-8") as f:
                    f.write(html)
            except Exception:
                pass

        return items[:max_items]

    async def _has_results_container(self, page: Page) -> bool:
        candidates = [
            '[data-testid*="search-result"]',
            'main section',
            'section:has(a)',
            'article a[href^="/"]',
        ]
        for sel in candidates:
            try:
                nodes = await page.query_selector_all(sel)
                if nodes and len(nodes) > 5:
                    return True
            except Exception:
                continue
        return False

    async def _dismiss_overlays(self, page: Page):
        selectors = [
            'button:has-text("Accept")',
            'button:has-text("Agree")',
            'button[aria-label="Close"]',
            'div[role="dialog"] button[aria-label="Close"]',
        ]
        for sel in selectors:
            try:
                btn = await page.query_selector(sel)
                if btn and await btn.is_visible():
                    await btn.click()
                    await page.wait_for_timeout(200)
            except Exception:
                continue

    async def _extract_from_viewport(self, page: Page, limit: int) -> List[MotionItem]:
        results: List[MotionItem] = []
        if limit <= 0:
            return results

        # Only collect candidate link URLs; do not attempt thumbnail extraction
        candidates: List[MotionItem] = []
        try:
            anchors = await page.evaluate('''() => {
                const out = [];
                const aList = Array.from(document.querySelectorAll('a[href*="/app/"]'));
                for (const a of aList) {
                    const href = a.getAttribute('href') || a.href;
                    if (!href) continue;
                    let abs = href;
                    try { abs = new URL(href, location.origin).href; } catch (e) {}
                    out.push(abs);
                }
                return Array.from(new Set(out));
            }''')
            for href in anchors:
                candidates.append(MotionItem(title=None, thumb_url=None, media_url=None, link_url=href))
        except Exception:
            pass

        # Fallback: query selector anchors
        if not candidates:
            try:
                links = await page.query_selector_all('a[href*="/app/"]')
            except Exception:
                links = []
            for link in links:
                if len(candidates) >= limit:
                    break
                try:
                    href = await link.get_attribute('href')
                    if not href:
                        href = await link.evaluate('(el)=> el.href || el.getAttribute("href")')
                    if not href:
                        continue
                    from urllib.parse import urljoin
                    link_url = href if href.startswith('http') else urljoin('https://appmotion.design/', href.lstrip('./'))
                    candidates.append(MotionItem(title=None, thumb_url=None, media_url=None, link_url=link_url))
                except Exception:
                    continue

        # Trim candidates and then enrich via detail page to get media_url
        candidates = candidates[:limit]
        if candidates:
            results = await self._maybe_enrich_with_detail(page, candidates)

        # Only keep items with media_url
        results = [it for it in results if it.media_url]
        return results[:limit]

    async def _maybe_enrich_with_detail(self, page: Page, items: List[MotionItem]) -> List[MotionItem]:
        enriched: List[MotionItem] = []
        visits = 0
        base = 'https://appmotion.design'
        for it in items:
            if it.media_url or not it.link_url:
                enriched.append(it)
                continue
            if visits >= getattr(self.config, 'max_detail_visits', 5):
                enriched.append(it)
                continue
            visits += 1
            try:
                # Open in a new tab to not lose current context
                detail = await page.context.new_page()
                detail.set_default_timeout(self.config.detail_timeout_ms)
                # Capture network responses for video candidates
                _responses = []
                def _on_response(resp):
                    try:
                        _responses.append(resp)
                    except Exception:
                        pass
                detail.on('response', _on_response)

                await detail.goto(it.link_url, wait_until=self.config.wait_until)
                await self._dismiss_overlays(detail)

                # Try to locate a video source first
                media_url = None
                try:
                    await detail.wait_for_selector('video, source[src^="http"]', state='attached', timeout=min(8000, self.config.detail_timeout_ms))
                except Exception:
                    pass

                # Try to ensure video is visible and playing (to trigger loads)
                try:
                    v = await detail.query_selector('video')
                    if v:
                        try:
                            await v.scroll_into_view_if_needed()
                        except Exception:
                            pass
                        try:
                            await v.evaluate('(el) => { el.muted = true; el.playsInline = true; el.autoplay = true; el.play && el.play().catch(()=>{}); }')
                        except Exception:
                            pass
                except Exception:
                    pass

                # 1) Direct video[src]
                try:
                    v = await detail.query_selector('video[src^="http"]')
                    if v:
                        src = await v.get_attribute('src')
                        if src and src.startswith('http'):
                            media_url = src
                        if not media_url:
                            try:
                                cur = await v.evaluate('(el) => el.currentSrc || ""')
                                if cur and isinstance(cur, str) and cur.startswith('http'):
                                    media_url = cur
                            except Exception:
                                pass
                except Exception:
                    pass

                # 2) Any source under video
                if not media_url:
                    try:
                        sources = await detail.query_selector_all('video source[src^="http"]')
                        for s in sources:
                            src = await s.get_attribute('src')
                            if src and src.startswith('http'):
                                media_url = src
                                break
                    except Exception:
                        pass

                # 3) Fallback: look for common links to mp4/webm in the DOM
                if not media_url:
                    try:
                        link = await detail.query_selector('a[href$=".mp4"], a[href$=".webm"], link[href$=".mp4"], link[href$=".webm"]')
                        if link:
                            src = await link.get_attribute('href')
                            if src and src.startswith('http'):
                                media_url = src
                    except Exception:
                        pass

                # 4) Meta tags (og:video, twitter:player:stream)
                if not media_url:
                    try:
                        metas = await detail.query_selector_all('meta[property="og:video"], meta[property="og:video:url"], meta[name="twitter:player:stream"]')
                        for m in metas:
                            content = await m.get_attribute('content')
                            if content and content.startswith('http') and (content.endswith('.mp4') or content.endswith('.webm')):
                                media_url = content
                                break
                    except Exception:
                        pass

                # 5) Network responses: prefer .mp4/.webm or video/* content-type
                if not media_url and _responses:
                    try:
                        await detail.wait_for_timeout(800)
                    except Exception:
                        pass
                    chosen = None
                    for resp in _responses:
                        try:
                            url = resp.url
                            if url and any(ext in url for ext in ('.mp4', '.webm', '.m3u8')):
                                chosen = url
                                break
                        except Exception:
                            continue
                    if not chosen:
                        for resp in _responses:
                            try:
                                ct = await resp.header_value('content-type')
                                if ct and (ct.startswith('video') or 'mpegurl' in ct.lower()):
                                    chosen = resp.url
                                    break
                            except Exception:
                                continue
                    if chosen and chosen.startswith('http'):
                        media_url = chosen

                # 6) Regex over HTML as last resort
                if not media_url:
                    try:
                        import re
                        html = await detail.content()
                        m = re.search(r'https?://[^"\s\']+\.(?:mp4|webm)', html)
                        if m:
                            media_url = m.group(0)
                    except Exception:
                        pass
                # Fallback: sometimes media is in data attributes or poster
                if not media_url:
                    try:
                        v = await detail.query_selector('video')
                        if v:
                            poster = await v.get_attribute('poster')
                            if poster and poster.startswith('http'):
                                # use poster as better thumb
                                if not it.thumb_url:
                                    it.thumb_url = poster
                    except Exception:
                        pass

                if media_url:
                    it.media_url = media_url
                enriched.append(it)
            except Exception:
                enriched.append(it)
            finally:
                try:
                    try:
                        detail.off('response', _on_response)
                    except Exception:
                        pass
                    await detail.close()
                except Exception:
                    pass

        return enriched

    async def _cleanup(self):
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception:
            pass

async def list_motion_tags(max_tags: int = 500) -> List[Tuple[str, str]]:
    """
    Scrape the /tags page and return a list of (tag_name, tag_link) tuples.
    """
    config = MotionConfig()
    tags: List[Tuple[str, str]] = []
    async with MotionSearcher(config) as s:
        page = s.page
        base = 'https://appmotion.design'
        await page.goto(f'{base}/tags', wait_until=s.config.wait_until)
        await s._dismiss_overlays(page)
        # Wait for tags to render
        try:
            await page.wait_for_selector("a[href^='/tag/']", state="attached", timeout=min(10000, s.config.timeout))
        except Exception:
            pass
        # Select all tag anchors
        links = await page.query_selector_all("a[href^='/tag/']")
        for a in links[:max_tags]:
            try:
                href = await a.get_attribute('href')
                text = await a.text_content()
                if not href:
                    continue
                link = href if href.startswith('http') else f'{base}{href}'
                name = (text or '').strip()
                if name:
                    tags.append((name, link))
            except Exception:
                continue
    return tags


async def search_motion(query: str, max_items: int = 10) -> MotionSearchResult:
    async with MotionSearcher() as s:
        return await s.search(query, max_items)

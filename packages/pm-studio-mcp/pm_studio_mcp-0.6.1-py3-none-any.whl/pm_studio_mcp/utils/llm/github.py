import requests
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from pm_studio_mcp.config import config


class GHCUtils:
    @staticmethod
    def get_ghc_prompt_result(prompt: str, model: str = "gpt-4.1", max_tokens: int = 200):
                
        # Standard Models (Included)
        # "gpt-4.1"
        # "gpt-4o"
        # Premium Models (Usage-based pricing)
        # "claude-opus-4" (10x cost)
        # "claude-sonnet-3.5" (1x cost)
        # "claude-sonnet-3.7" (1x cost)
        # "claude-sonnet-3.7-thinking" (1.25x cost)
        # "claude-sonnet-4" (1x cost) ✓ (currently selected in the image)
        # "gemini-2.0-flash" (0.25x cost)
        # "gemini-2.5-pro" (1x cost, Preview)
        # "o3" (1x cost, Preview)
        # "o3-mini" (0.33x cost)
        # "o4-mini" (0.33x cost, Preview)

        # Your GitHub token
        token = config.GITHUB_TOKEN
        
        # API call
        response = requests.post(
            "https://models.inference.ai.azure.com/chat/completions",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"role": "user", "content": prompt}],
                "model": model,
                "max_tokens": max_tokens
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(result["choices"][0]["message"]["content"])
            return result["choices"][0]["message"]["content"]
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)


# typical format of json
# {
#   "choices": [
#     {
#       "content_filter_results": {
#         "hate": {
#           "filtered": false,
#           "severity": "safe"
#         },
#         "self_harm": {
#           "filtered": false,
#           "severity": "safe"
#         },
#         "sexual": {
#           "filtered": false,
#           "severity": "safe"
#         },
#         "violence": {
#           "filtered": false,
#           "severity": "safe"
#         }
#       },
#       "finish_reason": "stop",
#       "index": 0,
#       "logprobs": null,
#       "message": {
#         "annotations": [],
#         "content": "Why did the scarecrow win an award?\n\nBecause he was outstanding in his field!",
#         "refusal": null,
#         "role": "assistant"
#       }
#     }
#   ],
#   "created": 1752051864,
#   "id": "chatcmpl-BrL0ymhZIRSAWsPUD7vQSBVWWVVgn",
#   "model": "gpt-4.1-2025-04-14",
#   "object": "chat.completion",
#   "usage": {
#     "completion_tokens": 18,
#     "prompt_tokens": 12,
#     "total_tokens": 30
#   }
# }

# Run the test
GHCUtils.get_ghc_prompt_result("write a joke please", model="gpt-4.1")
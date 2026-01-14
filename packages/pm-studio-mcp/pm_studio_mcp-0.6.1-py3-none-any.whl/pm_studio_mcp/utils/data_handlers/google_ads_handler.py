import os
import json
import logging
import pandas as pd
from pandas import json_normalize
from typing import Dict, Any
from datetime import datetime
from pm_studio_mcp.utils.data_handlers.base_handler import BaseHandler
from pm_studio_mcp.config import config

# Google Ads API imports
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.protobuf.json_format import MessageToDict
from google.ads.googleads.client import GoogleAdsClient

DEVELOPER_TOKEN = config.GOOGLE_ADS_DEVELOPER_TOKEN
LOGIN_CUSTOMER_ID = config.GOOGLE_ADS_LOGIN_CUSTOMER_ID

# 解析 JSON 字符串为 dict
CLIENT_SECRET_DICT = json.loads(config.GOOGLE_ADS_CLIENT_SECRET_JSON) if config.GOOGLE_ADS_CLIENT_SECRET_JSON else {}
GOOGLE_ADS_CREDENTIALS_DICT = json.loads(config.GOOGLE_ADS_CREDENTIALS_JSON) if config.GOOGLE_ADS_CREDENTIALS_JSON else {}

SCOPES = ["https://www.googleapis.com/auth/adwords"]

class GoogleAdsHandler(BaseHandler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def flatten_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df_flat = df.copy()
        dict_cols = []
        for col in df_flat.columns:
            if df_flat[col].apply(lambda x: isinstance(x, dict)).any():
                dict_cols.append(col)
        for col in dict_cols:
            normalized = json_normalize(df_flat[col].tolist(), sep=".")
            normalized.columns = [f"{col}.{subcol}" for subcol in normalized.columns]
            df_flat = df_flat.drop(columns=[col]).reset_index(drop=True)
            df_flat = pd.concat([df_flat.reset_index(drop=True), normalized.reset_index(drop=True)], axis=1)
        return df_flat

    def get_google_ads_credentials(self):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_info(GOOGLE_ADS_CREDENTIALS_DICT, SCOPES)
        using_existing_token = True
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                from google_auth_oauthlib.flow import InstalledAppFlow
                flow = InstalledAppFlow.from_client_config(CLIENT_SECRET_DICT, SCOPES)
                creds = flow.run_local_server(port=10086)
        return creds, using_existing_token

    def query_google_ads_api(self, query, customer_id):
        google_creds, _ = self.get_google_ads_credentials()
        api_creds = json.loads(google_creds.to_json())
        api_creds["developer_token"] = DEVELOPER_TOKEN
        api_creds["login_customer_id"] = LOGIN_CUSTOMER_ID
        api_creds["use_proto_plus"] = True
        client = GoogleAdsClient.load_from_dict(api_creds)
        ga_service = client.get_service("GoogleAdsService")
        rows_as_dicts = []
        stream = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in stream:
            for row in batch.results:
                row_dict = MessageToDict(row._pb, preserving_proto_field_name=True)
                rows_as_dicts.append(row_dict)
        rows_df = pd.DataFrame(rows_as_dicts)
        flattened_df = self.flatten_df(rows_df)
        return flattened_df

    def get_client_customer_ids(self, manager_customer_id):
        """
        获取manager账号下所有一级client account的customer_id
        """
        google_creds, _ = self.get_google_ads_credentials()
        api_creds = json.loads(google_creds.to_json())
        api_creds["developer_token"] = DEVELOPER_TOKEN
        api_creds["login_customer_id"] = LOGIN_CUSTOMER_ID
        api_creds["use_proto_plus"] = True
        client = GoogleAdsClient.load_from_dict(api_creds)
        ga_service = client.get_service("GoogleAdsService")
        query = '''
            SELECT
              customer_client.client_customer,
              customer_client.level,
              customer_client.manager,
              customer_client.descriptive_name
            FROM customer_client
            WHERE customer_client.level = 1
        '''
        client_ids = []
        stream = ga_service.search_stream(customer_id=manager_customer_id, query=query)
        for batch in stream:
            for row in batch.results:
                client_id = row.customer_client.client_customer
                if client_id:
                    client_ids.append(client_id)
        return client_ids

    def fetch_data(self, product_name: str = None, start_date: str = None, end_date: str = None, **kwargs) -> Dict[str, Any]:
        """
        Fetch Google Ads campaign data and return as standard handler output.
        Args:
            product_name: (optional) for logging
            start_date, end_date: (optional) for query construction
            kwargs: dict, must include 'query', 'customer_id', 'output_dir' (optional)
        Returns:
            dict: status, output_file, data_length, results
        """
        try:
            if kwargs is None:
                kwargs = {}
            # 打印调试 customer_id
            print(f"[GoogleAdsHandler] fetch_data received customer_id: {kwargs.get('customer_id')}")
            query = kwargs.get("query")
            customer_id = kwargs.get("customer_id")
            output_dir = kwargs.get("output_dir", "./working_dir/Report")
            # 使用用户提供的 GAQL 查询
            query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    ad_group.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.average_cpm,
                    metrics.ctr,
                    metrics.cost_micros,
                    metrics.conversions,
                    segments.date
                FROM ad_group
                WHERE segments.date DURING LAST_30_DAYS
                AND campaign.status = 'ENABLED'
                AND ad_group.status = 'ENABLED'
                ORDER BY ad_group.id
            """
            # 新增逻辑：如果未指定 customer_id，则自动获取第一个 client_id
            if not customer_id:
                client_ids = self.get_client_customer_ids(LOGIN_CUSTOMER_ID)
                self.logger.info(f"No customer_id specified, fetched client_ids: {client_ids}")
                print(f"No customer_id specified, fetched client_ids: {client_ids}")
                if not client_ids:
                    raise Exception("No client accounts found under manager account.")
                customer_id = client_ids[0].split('/')[-1] if isinstance(client_ids[0], str) and '/' in client_ids[0] else client_ids[0]
                self.logger.info(f"Using first client_id: {customer_id}")
                print(f"Using first client_id: {customer_id}")
            # 新增逻辑：如果指定了 customer_id，检查其是否在 manager 账号下的 client_ids 中
            if customer_id:
                client_ids = self.get_client_customer_ids(LOGIN_CUSTOMER_ID)
                client_ids_numeric = [cid.split('/')[-1] if isinstance(cid, str) and '/' in cid else cid for cid in client_ids]
                if customer_id not in client_ids_numeric:
                    msg = f"未找到customer id: {customer_id}，可用id列表: {client_ids_numeric}"
                    self.logger.error(msg)
                    return {"status": "error", "message": msg}
            # 只查一个 customer_id
            try:
                df = self.query_google_ads_api(query, customer_id)
            except Exception as e:
                self.logger.error(f"GoogleAdsHandler error: {str(e)}")
                return {"status": "error", "message": str(e)}
            # 输出文件目录改为 config.WORKING_PATH
            output_dir = getattr(config, 'WORKING_PATH', output_dir)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            today = datetime.now().strftime("%Y%m%d")
            output_filename = f"{today}_Googleads_rawdata.csv"
            output_path = os.path.join(output_dir, output_filename)
            df.to_csv(output_path, index=False, encoding="utf-8")
            return {
                "status": "success",
                "output_file": output_path,
                "data_length": len(df),
                "results": df.head(10).to_dict(orient="records")  # 只返回前10条样例
            }
        except Exception as e:
            self.logger.error(f"GoogleAdsHandler error: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test GoogleAdsHandler fetch_data")
    parser.add_argument('--customer_id', type=str, default=None, help='Google Ads customer ID')
    parser.add_argument('--output_dir', type=str, default='./working_dir/Report', help='Output directory for CSV')
    parser.add_argument('--query', type=str, default=None, help='GAQL query string (optional)')
    args = parser.parse_args()

    handler = GoogleAdsHandler()
    kwargs = {
        'customer_id': args.customer_id,
        'output_dir': args.output_dir
    }
    if args.query:
        kwargs['query'] = args.query
    result = handler.fetch_data(**kwargs)
    print("Fetch result:")
    print(result)
    if result.get('output_file'):
        print(f"CSV saved to: {result['output_file']}")

if __name__ == "__main__":
    main()

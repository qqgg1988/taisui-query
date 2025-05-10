import os
import json
import requests
from dotenv import load_dotenv

class FeishuTableReader:
    def __init__(self):
        load_dotenv()
        self.app_id = os.getenv('FEISHU_APP_ID')
        self.app_secret = os.getenv('FEISHU_APP_SECRET')
        self.base_id = os.getenv('BASE_ID')
        self.table_id = os.getenv('TABLE_ID')
        self.tenant_access_token = None

        # 验证必要的环境变量
        if not all([self.app_id, self.app_secret, self.base_id, self.table_id]):
            raise ValueError("请确保所有必要的环境变量都已正确设置")

    def get_tenant_access_token(self):
        """获取租户访问令牌"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if result.get('code') == 0:
                self.tenant_access_token = result.get('tenant_access_token')
                print("成功获取访问令牌")
                return True
            else:
                print(f"获取访问令牌失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"获取访问令牌时发生错误: {str(e)}")
            return False

    def get_tmp_download_url(self, file_token):
        """获取文件的临时下载链接"""
        if not self.tenant_access_token:
            if not self.get_tenant_access_token():
                raise Exception("无法获取访问令牌")

        url = f"https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}"
        }
        params = {
            "file_tokens": file_token
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                tmp_download_urls = result.get('data', {}).get('tmp_download_urls', [])
                if tmp_download_urls:
                    return tmp_download_urls[0].get('tmp_download_url')
            return None
        except Exception as e:
            print(f"获取临时下载链接时发生错误: {str(e)}")
            return None

    def get_table_records(self):
        """获取多维表格的记录"""
        if not self.tenant_access_token:
            if not self.get_tenant_access_token():
                raise Exception("无法获取访问令牌")

        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_id}/tables/{self.table_id}/records"
        headers = {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:
                records = result.get('data', {}).get('items', [])
                print(f"成功获取表格记录，共 {len(records)} 条")
                return records
            else:
                print(f"获取表格记录失败: {result.get('msg')}")
                return []
        except Exception as e:
            print(f"获取表格记录时发生错误: {str(e)}")
            return []

    def process_records(self):
        """处理表格记录并导出为JSON"""
        records = self.get_table_records()
        if not records:
            return

        print(f"开始处理 {len(records)} 条记录...")
        processed_records = []

        # 需要保留的字段
        required_fields = ["Animal", "Ganzhi", "Nayin", "Taishui", "Year"]

        for record in records:
            fields = record.get('fields', {})
            processed_record = {}

            # 处理普通字段
            for field in required_fields:
                if field in fields:
                    processed_record[field] = fields[field]

            # 处理Poster字段，获取临时下载链接
            if 'Poster' in fields and isinstance(fields['Poster'], list) and len(fields['Poster']) > 0:
                poster_data = fields['Poster'][0]  # 获取第一个附件
                if 'file_token' in poster_data:
                    file_token = poster_data['file_token']
                    processed_record['Poster'] = {
                        'file_token': file_token,
                        'tmp_download_url': self.get_tmp_download_url(file_token)
                    }

            processed_records.append(processed_record)

        # 导出为JSON文件
        with open('output.json', 'w', encoding='utf-8') as f:
            json.dump(processed_records, f, ensure_ascii=False, indent=2)
        print("数据已成功导出到 output.json")

def main():
    print("开始运行飞书表格导出程序...")
    reader = FeishuTableReader()
    reader.process_records()

if __name__ == "__main__":
    main() 
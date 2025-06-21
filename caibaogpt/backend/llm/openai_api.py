import os
import openai
from typing import Union, List, Dict
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定 OpenAI API 金鑰
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise Exception("請在 .env 檔案中設定 OPENAI_API_KEY")
openai.api_key = api_key

def ask_gpt(prompt: Union[str, List[Dict[str, str]]]) -> str:
    """
    調用 OpenAI API 獲取回應
    """
    try:
        # 如果輸入是字串，轉換為消息格式
        if isinstance(prompt, str):
            messages = [
                {"role": "system", "content": "你是一位專業的財務分析師，擅長解讀財務報表並提供深入的分析見解。"},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = prompt
            
        # 調用 API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # 返回回應文字
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"OpenAI API 錯誤：{str(e)}") 
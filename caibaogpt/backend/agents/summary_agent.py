import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Dict, Any
from llm.openai_api import ask_gpt

def format_number(number: float) -> str:
    """
    格式化數字為易讀的形式（加入千分位逗號，四捨五入到小數點後2位）
    """
    if abs(number) >= 1_000_000_000:  # 十億以上
        return f"{number/1_000_000_000:.2f}十億"
    elif abs(number) >= 1_000_000:  # 百萬以上
        return f"{number/1_000_000:.2f}百萬"
    elif abs(number) >= 1_000:  # 千以上
        return f"{number/1_000:.2f}千"
    else:
        return f"{number:.2f}"

def format_percentage(value: float) -> str:
    """
    將小數轉換為百分比格式
    """
    return f"{value * 100:.2f}%"

def generate_summary(text_content):
    """
    使用 GPT 生成財報摘要
    """
    prompt = f"""
    請根據以下財報內容生成一個簡短的中文摘要，重點包括：
    1. 公司整體財務表現
    2. 主要收入來源
    3. 重要財務指標變化
    4. 值得關注的重要事項

    財報內容：
    {text_content}

    請用 200 字以內的中文回答。
    """
    
    try:
        summary = ask_gpt(prompt)
        return summary.strip()
    except Exception as e:
        raise Exception(f"生成摘要時發生錯誤：{str(e)}")

def generate_financial_summary(indicators: Dict[str, Any]) -> str:
    """
    根據財務指標生成中文摘要
    
    Args:
        indicators: 財務指標字典
        
    Returns:
        str: 中文摘要文字
    """
    summary_parts = []
    
    # 資產負債概況
    if indicators.get('總資產') is not None:
        summary_parts.append(f"公司總資產為 {format_number(indicators['總資產'])} 元")
    
    if indicators.get('總負債') is not None and indicators.get('權益總額') is not None:
        summary_parts.append(f"其中負債 {format_number(indicators['總負債'])} 元，"
                           f"權益 {format_number(indicators['權益總額'])} 元")
    
    if indicators.get('負債比率') is not None:
        summary_parts.append(f"負債比率為 {format_percentage(indicators['負債比率'])}")
    
    # 獲利能力
    if indicators.get('營業收入') is not None:
        summary_parts.append(f"本期營業收入 {format_number(indicators['營業收入'])} 元")
    
    if indicators.get('營業利益') is not None:
        summary_parts.append(f"營業利益 {format_number(indicators['營業利益'])} 元")
    
    if indicators.get('本期淨利') is not None:
        summary_parts.append(f"本期淨利 {format_number(indicators['本期淨利'])} 元")
    
    # 報酬率
    if indicators.get('ROE') is not None:
        summary_parts.append(f"股東權益報酬率(ROE)為 {format_percentage(indicators['ROE'])}")
    
    if indicators.get('ROA') is not None:
        summary_parts.append(f"總資產報酬率(ROA)為 {format_percentage(indicators['ROA'])}")
    
    # 現金流量
    cash_flow_parts = []
    if indicators.get('營業活動現金流量') is not None:
        cash_flow_parts.append(f"營業活動現金流量 {format_number(indicators['營業活動現金流量'])} 元")
    
    if indicators.get('投資活動現金流量') is not None:
        cash_flow_parts.append(f"投資活動現金流量 {format_number(indicators['投資活動現金流量'])} 元")
    
    if indicators.get('籌資活動現金流量') is not None:
        cash_flow_parts.append(f"籌資活動現金流量 {format_number(indicators['籌資活動現金流量'])} 元")
    
    if cash_flow_parts:
        summary_parts.append("現金流量方面：" + "，".join(cash_flow_parts))
    
    # 組合完整摘要
    summary = "。".join(summary_parts) + "。"
    
    return summary 
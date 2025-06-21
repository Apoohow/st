"""
財務報表欄位別名對照模組

此模組提供財務報表中常見欄位的中文別名對照，用於：
1. PDF 擷取後的欄位對照
2. 欄位缺漏補足
3. 標準化欄位名稱
"""

from typing import Dict, List, Optional

# 資產負債表欄位別名
BALANCE_SHEET_ALIASES = {
    "流動資產": ["流動資產合計", "流動資產總額", "短期資產"],
    "非流動資產": ["非流動資產", "固定資產", "長期投資", "其他資產", "固定資產淨額"],
    "存貨": ["存貨", "商品", "在製品", "原物料", "存貨淨額"],
    "現金與約當現金": ["現金及約當現金", "現金", "約當現金", "現金及銀行存款"],
    "流動負債": ["流動負債合計", "流動負債總額", "短期負債"],
    "非流動負債": ["非流動負債", "長期負債", "其他負債", "長期負債合計"],
    "應付帳款": ["應付帳款", "應付款項", "應付票據及帳款", "應付帳款及票據"],
    "應收帳款": ["應收帳款", "應收款項", "應收票據及帳款", "應收帳款及票據"],
    "總資產": ["資產總額", "資產總計", "全部資產"],
    "總負債": ["負債總額", "負債總計", "負債合計"],
    "權益總額": ["權益總額", "淨值總額", "股東權益合計", "權益總計", "淨值"],
    "普通股股數": ["普通股股本", "股本", "實收資本", "已發行股數"],
    "折舊": ["折舊費用", "折舊", "本期折舊"],
    "攤銷": ["攤銷費用", "攤銷", "本期攤銷"],
    "利息費用": ["利息費用", "財務成本", "融資成本"]
}

# 損益表欄位別名
INCOME_STATEMENT_ALIASES = {
    "營業收入": ["營業收入", "營收", "收入總額", "營業收入淨額", "銷貨收入"],
    "營業成本": ["營業成本", "成本", "銷貨成本", "營業成本合計"],
    "毛利": ["毛利", "營業毛利", "毛利淨額", "銷貨毛利"],
    "營業利益": ["營業利益", "營業淨利", "營業損益", "營業利益（損失）"],
    "稅前淨利": ["稅前淨利", "稅前損益", "稅前利益", "稅前淨利（淨損）"],
    "本期淨利": ["本期淨利", "稅後淨利", "淨利", "淨損益", "本期損益"],
    "每股盈餘": ["每股盈餘", "每股利益", "EPS", "基本每股盈餘"],
    "前期營業收入": ["前期營業收入", "去年同期營收", "上期營業收入"],
    "前期淨利": ["前期淨利", "去年同期淨利", "上期淨利"]
}

# 現金流量表欄位別名
CASH_FLOW_ALIASES = {
    "營業活動現金流量": ["營業活動之淨現金流入", "營業活動現金流量", "營業活動之現金流量", "營運產生之現金流入"],
    "投資活動現金流量": ["投資活動之淨現金流入", "投資活動現金流量", "投資活動之現金流量", "投資活動之淨現金流量"],
    "籌資活動現金流量": ["籌資活動之淨現金流入", "籌資活動現金流量", "籌資活動之現金流量", "籌資活動之淨現金流量"],
    "本期現金增減": ["本期現金增加數", "本期現金淨流量", "現金及約當現金增加", "本期現金及約當現金增加（減少）"],
    "期末現金餘額": ["期末現金及約當現金餘額", "期末現金餘額", "期末現金及約當現金", "期末現金及約當現金餘額"]
}

# 所有欄位別名的合併字典
ALL_ALIASES = {
    **BALANCE_SHEET_ALIASES,
    **INCOME_STATEMENT_ALIASES,
    **CASH_FLOW_ALIASES
}

# 更新財務比率所需欄位
RATIO_REQUIRED_COLUMNS = {
    "ROE": ["本期淨利", "權益總額"],
    "ROA": ["本期淨利", "總資產"],
    "毛利率": ["毛利", "營業收入"],
    "營業利益率": ["營業利益", "營業收入"],
    "淨利率": ["本期淨利", "營業收入"],
    "負債比率": ["總負債", "總資產"],
    "流動比率": ["流動資產", "流動負債"],
    "速動比率": ["流動資產", "存貨", "流動負債"],
    "權益比率": ["權益總額", "總資產"],
    "長期資金適合率": ["權益總額", "非流動負債", "非流動資產"],
    "應收帳款週轉率": ["營業收入", "應收帳款"],
    "存貨週轉率": ["營業成本", "存貨"],
    "總資產週轉率": ["營業收入", "總資產"],
    "固定資產週轉率": ["營業收入", "非流動資產"],
    "營收成長率": ["營業收入", "前期營業收入"],
    "淨利成長率": ["本期淨利", "前期淨利"],
    "現金流量比率": ["營業活動現金流量", "流動負債"],
    "現金再投資比率": ["營業活動現金流量", "本期淨利"],
    "財務槓桿度": ["總負債", "權益總額"],
    "利息保障倍數": ["營業利益", "利息費用"],
    "每股盈餘": ["本期淨利", "普通股股數"],
    "每股淨值": ["權益總額", "普通股股數"],
    "EBITDA利潤率": ["營業利益", "折舊", "攤銷", "營業收入"]
}

def find_standard_name(column_name: str) -> str:
    """
    根據別名找到標準欄位名稱
    """
    # 檢查所有別名字典
    for aliases_dict in [BALANCE_SHEET_ALIASES, INCOME_STATEMENT_ALIASES, CASH_FLOW_ALIASES]:
        for standard_name, aliases in aliases_dict.items():
            if column_name == standard_name or column_name in aliases:
                return standard_name
    return column_name

def get_aliases(standard_name: str) -> List[str]:
    """
    獲取標準名稱對應的所有別名

    Args:
        standard_name (str): 標準欄位名稱

    Returns:
        List[str]: 該欄位的所有別名列表
    """
    return ALL_ALIASES.get(standard_name, [])

def get_required_columns_for_ratio(ratio_name: str) -> List[str]:
    """
    獲取計算特定財務比率所需的欄位
    """
    return RATIO_REQUIRED_COLUMNS.get(ratio_name, [])

def is_balance_sheet_item(column_name: str) -> bool:
    """
    判斷欄位是否屬於資產負債表

    Args:
        column_name (str): 欄位名稱

    Returns:
        bool: 是否屬於資產負債表
    """
    standard_name = find_standard_name(column_name)
    return standard_name in BALANCE_SHEET_ALIASES

def is_income_statement_item(column_name: str) -> bool:
    """
    判斷欄位是否屬於損益表

    Args:
        column_name (str): 欄位名稱

    Returns:
        bool: 是否屬於損益表
    """
    standard_name = find_standard_name(column_name)
    return standard_name in INCOME_STATEMENT_ALIASES

def is_cash_flow_item(column_name: str) -> bool:
    """
    判斷欄位是否屬於現金流量表

    Args:
        column_name (str): 欄位名稱

    Returns:
        bool: 是否屬於現金流量表
    """
    standard_name = find_standard_name(column_name)
    return standard_name in CASH_FLOW_ALIASES 
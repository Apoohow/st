from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
import re
from utils.column_aliases import (
    BALANCE_SHEET_ALIASES,
    INCOME_STATEMENT_ALIASES,
    CASH_FLOW_ALIASES,
    RATIO_REQUIRED_COLUMNS,
    find_standard_name,
    get_required_columns_for_ratio,
    is_balance_sheet_item,
    is_income_statement_item,
    is_cash_flow_item
)

class IndicatorExtractor:
    def __init__(self, financial_data: Dict[str, float]):
        self.financial_data = self._standardize_columns(financial_data)
        
    def _standardize_columns(self, data: Dict[str, float]) -> Dict[str, float]:
        """
        將輸入的財務數據欄位名稱標準化

        Args:
            data (Dict[str, float]): 原始財務數據

        Returns:
            Dict[str, float]: 標準化後的財務數據
        """
        standardized_data = {}
        for column_name, value in data.items():
            standard_name = find_standard_name(column_name)
            if standard_name:
                standardized_data[standard_name] = value
            else:
                standardized_data[column_name] = value  # 保留原始名稱
        return standardized_data

    def _get_value(self, column_name: str) -> Optional[float]:
        """
        獲取指定欄位的值，支援標準名稱和別名

        Args:
            column_name (str): 欄位名稱

        Returns:
            Optional[float]: 欄位值，如果不存在則返回 None
        """
        return self.financial_data.get(column_name)

    def extract_all_indicators(self) -> Dict[str, float]:
        """
        提取所有財務指標

        Returns:
            Dict[str, float]: 計算出的所有財務指標
        """
        indicators = {}
        
        # 獲利能力指標
        indicators.update(self.calculate_profitability_ratios())
        
        # 財務結構指標
        indicators.update(self.calculate_financial_structure_ratios())
        
        # 經營能力指標
        indicators.update(self.calculate_operating_performance_ratios())
        
        # 成長性指標
        indicators.update(self.calculate_growth_ratios())
        
        # 現金流量指標
        indicators.update(self.calculate_cash_flow_ratios())
        
        # 槓桿指標
        indicators.update(self.calculate_leverage_ratios())
        
        # 每股指標
        indicators.update(self.calculate_per_share_ratios())
        
        return indicators

    def calculate_profitability_ratios(self) -> Dict[str, float]:
        """
        計算獲利能力相關指標
        """
        ratios = {}
        
        # 基本指標
        net_income = self._get_value("本期淨利")
        equity = self._get_value("權益總額")
        total_assets = self._get_value("總資產")
        revenue = self._get_value("營業收入")
        gross_profit = self._get_value("毛利")
        operating_income = self._get_value("營業利益")
        
        # ROE
        if net_income is not None and equity is not None and equity != 0:
            ratios["ROE"] = net_income / equity
        
        # ROA
        if net_income is not None and total_assets is not None and total_assets != 0:
            ratios["ROA"] = net_income / total_assets
        
        # 毛利率
        if gross_profit is not None and revenue is not None and revenue != 0:
            ratios["毛利率"] = gross_profit / revenue
        
        # 營業利益率
        if operating_income is not None and revenue is not None and revenue != 0:
            ratios["營業利益率"] = operating_income / revenue
        
        # 淨利率
        if net_income is not None and revenue is not None and revenue != 0:
            ratios["淨利率"] = net_income / revenue
        
        # EBITDA 利潤率
        depreciation = self._get_value("折舊")
        amortization = self._get_value("攤銷")
        if operating_income is not None and depreciation is not None and amortization is not None and revenue is not None and revenue != 0:
            ebitda = operating_income + depreciation + amortization
            ratios["EBITDA利潤率"] = ebitda / revenue
        
        return ratios

    def calculate_financial_structure_ratios(self) -> Dict[str, float]:
        """
        計算財務結構相關指標
        """
        ratios = {}
        
        # 基本數據
        total_liabilities = self._get_value("總負債")
        total_assets = self._get_value("總資產")
        current_assets = self._get_value("流動資產")
        current_liabilities = self._get_value("流動負債")
        inventory = self._get_value("存貨")
        equity = self._get_value("權益總額")
        long_term_liabilities = self._get_value("非流動負債")
        
        # 負債比率
        if total_liabilities is not None and total_assets is not None and total_assets != 0:
            ratios["負債比率"] = total_liabilities / total_assets
        
        # 流動比率
        if current_assets is not None and current_liabilities is not None and current_liabilities != 0:
            ratios["流動比率"] = current_assets / current_liabilities
        
        # 速動比率
        if current_assets is not None and inventory is not None and current_liabilities is not None and current_liabilities != 0:
            ratios["速動比率"] = (current_assets - inventory) / current_liabilities
        
        # 權益比率
        if equity is not None and total_assets is not None and total_assets != 0:
            ratios["權益比率"] = equity / total_assets
        
        # 長期資金適合率
        fixed_assets = self._get_value("非流動資產")
        if equity is not None and long_term_liabilities is not None and fixed_assets is not None and fixed_assets != 0:
            ratios["長期資金適合率"] = (equity + long_term_liabilities) / fixed_assets
        
        return ratios

    def calculate_operating_performance_ratios(self) -> Dict[str, float]:
        """
        計算經營能力相關指標
        """
        ratios = {}
        
        # 基本數據
        revenue = self._get_value("營業收入")
        accounts_receivable = self._get_value("應收帳款")
        inventory = self._get_value("存貨")
        cost_of_goods_sold = self._get_value("營業成本")
        total_assets = self._get_value("總資產")
        fixed_assets = self._get_value("非流動資產")
        
        # 應收帳款週轉率
        if revenue is not None and accounts_receivable is not None and accounts_receivable != 0:
            ratios["應收帳款週轉率"] = revenue / accounts_receivable
            ratios["應收帳款週轉天數"] = 365 / ratios["應收帳款週轉率"]
        
        # 存貨週轉率
        if cost_of_goods_sold is not None and inventory is not None and inventory != 0:
            ratios["存貨週轉率"] = cost_of_goods_sold / inventory
            ratios["存貨週轉天數"] = 365 / ratios["存貨週轉率"]
        
        # 總資產週轉率
        if revenue is not None and total_assets is not None and total_assets != 0:
            ratios["總資產週轉率"] = revenue / total_assets
        
        # 固定資產週轉率
        if revenue is not None and fixed_assets is not None and fixed_assets != 0:
            ratios["固定資產週轉率"] = revenue / fixed_assets
        
        return ratios

    def calculate_growth_ratios(self) -> Dict[str, float]:
        """
        計算成長性指標
        """
        ratios = {}
        
        # 營收成長率
        revenue = self._get_value("營業收入")
        revenue_prev = self._get_value("前期營業收入")
        if revenue is not None and revenue_prev is not None and revenue_prev != 0:
            ratios["營收成長率"] = (revenue - revenue_prev) / revenue_prev
        
        # 淨利成長率
        net_income = self._get_value("本期淨利")
        net_income_prev = self._get_value("前期淨利")
        if net_income is not None and net_income_prev is not None and net_income_prev != 0:
            ratios["淨利成長率"] = (net_income - net_income_prev) / net_income_prev
        
        return ratios

    def calculate_cash_flow_ratios(self) -> Dict[str, float]:
        """
        計算現金流量指標
        """
        ratios = {}
        
        # 基本數據
        operating_cash_flow = self._get_value("營業活動現金流量")
        current_liabilities = self._get_value("流動負債")
        net_income = self._get_value("本期淨利")
        
        # 現金流量比率
        if operating_cash_flow is not None and current_liabilities is not None and current_liabilities != 0:
            ratios["現金流量比率"] = operating_cash_flow / current_liabilities
        
        # 現金流量允當比率
        if operating_cash_flow is not None and net_income is not None and net_income != 0:
            ratios["現金再投資比率"] = operating_cash_flow / net_income
        
        return ratios

    def calculate_leverage_ratios(self) -> Dict[str, float]:
        """
        計算槓桿指標
        """
        ratios = {}
        
        # 基本數據
        total_liabilities = self._get_value("總負債")
        equity = self._get_value("權益總額")
        operating_income = self._get_value("營業利益")
        interest_expense = self._get_value("利息費用")
        
        # 財務槓桿度
        if total_liabilities is not None and equity is not None and equity != 0:
            ratios["財務槓桿度"] = total_liabilities / equity
        
        # 利息保障倍數
        if operating_income is not None and interest_expense is not None and interest_expense != 0:
            ratios["利息保障倍數"] = operating_income / interest_expense
        
        return ratios

    def calculate_per_share_ratios(self) -> Dict[str, float]:
        """
        計算每股指標
        """
        ratios = {}
        
        # 基本數據
        net_income = self._get_value("本期淨利")
        shares_outstanding = self._get_value("普通股股數")
        equity = self._get_value("權益總額")
        
        # 每股盈餘(EPS)
        if net_income is not None and shares_outstanding is not None and shares_outstanding != 0:
            ratios["每股盈餘"] = net_income / shares_outstanding
        
        # 每股淨值(BPS)
        if equity is not None and shares_outstanding is not None and shares_outstanding != 0:
            ratios["每股淨值"] = equity / shares_outstanding
        
        return ratios

    def get_missing_columns(self, ratio_name: str) -> List[str]:
        """
        獲取計算特定比率所缺少的欄位

        Args:
            ratio_name (str): 比率名稱

        Returns:
            List[str]: 缺少的欄位列表
        """
        required_columns = get_required_columns_for_ratio(ratio_name)
        missing_columns = []
        
        for column in required_columns:
            if self._get_value(column) is None:
                missing_columns.append(column)
        
        return missing_columns

def extract_indicators(text_content):
    """
    從文字內容中提取關鍵財務指標
    
    Args:
        text_content: 財報文字內容
        
    Returns:
        Dict[str, Any]: 關鍵指標及其數值的字典
    """
    indicators = {}
    
    # 定義要搜尋的財務指標模式
    patterns = {
        '營業收入': r'營業收入[總計]*[\s:：]*([\d,]+)',
        '本期淨利': r'淨[利益][總計]*[\s:：]*([\d,]+)',
        'EPS': r'每股(盈餘|收益)[\s:：]*([\d,.]+)',
        '毛利率': r'毛利率[\s:：]*(\d+\.?\d*%?)',
        '營業利益率': r'營業利益率[\s:：]*(\d+\.?\d*%?)',
        '淨利率': r'淨利率[\s:：]*(\d+\.?\d*%?)',
        '總資產': r'資產總[額計][總計]*[\s:：]*([\d,]+)',
        '總負債': r'負債總[額計][總計]*[\s:：]*([\d,]+)',
        '權益總額': r'權益總[額計][總計]*[\s:：]*([\d,]+)',
        '營業利益': r'營業利益[總計]*[\s:：]*([\d,]+)',
        '營業活動現金流量': r'營業活動[之的]?淨現金流[入量][總計]*[\s:：]*([\d,]+)',
        '投資活動現金流量': r'投資活動[之的]?淨現金流[入量][總計]*[\s:：]*([\d,]+)',
        '籌資活動現金流量': r'籌資活動[之的]?淨現金流[入量][總計]*[\s:：]*([\d,]+)'
    }
    
    # 搜尋每個指標
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text_content)
        if matches:
            # 取第一個匹配結果
            value = matches[0]
            if isinstance(value, tuple):
                value = value[0]
            # 移除千分位逗號並轉換為浮點數
            try:
                value = float(value.replace(',', '').replace('%', ''))
                # 如果是百分比，轉換為小數
                if '%' in matches[0]:
                    value = value / 100
                indicators[name] = value
            except ValueError:
                continue
    
    # 計算財務比率
    if all(k in indicators for k in ['總資產', '權益總額', '本期淨利']):
        indicators['ROA'] = indicators['本期淨利'] / indicators['總資產']
        indicators['ROE'] = indicators['本期淨利'] / indicators['權益總額']
    
    if '總負債' in indicators and '總資產' in indicators:
        indicators['負債比率'] = indicators['總負債'] / indicators['總資產']
    
    return indicators 
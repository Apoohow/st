import pandas as pd
from typing import Tuple, Optional, Dict
import os

class FinancialDataLoader:
    def __init__(self, data_dir: str):
        """
        初始化財務數據加載器
        
        Args:
            data_dir: 財務報表數據所在的目錄
        """
        self.data_dir = data_dir

    def calculate_financial_indicators(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame, cash_flow: pd.DataFrame) -> Dict[str, float]:
        """
        計算財務指標
        
        Args:
            balance_sheet: 資產負債表數據
            income_statement: 損益表數據
            cash_flow: 現金流量表數據
            
        Returns:
            Dict[str, float]: 計算出的財務指標
        """
        indicators = {}
        
        try:
            # 1. 獲利能力指標
            # 營收相關
            indicators["營業收入"] = income_statement["營業收入"].iloc[-1]
            indicators["前期營業收入"] = income_statement["前期營業收入"].iloc[-1]
            indicators["營收成長率"] = (indicators["營業收入"] - indicators["前期營業收入"]) / indicators["前期營業收入"]
            
            # 獲利相關
            indicators["毛利"] = income_statement["毛利"].iloc[-1]
            indicators["營業利益"] = income_statement["營業利益"].iloc[-1]
            indicators["本期淨利"] = income_statement["本期淨利"].iloc[-1]
            
            indicators["毛利率"] = indicators["毛利"] / indicators["營業收入"]
            indicators["營業利益率"] = indicators["營業利益"] / indicators["營業收入"]
            indicators["淨利率"] = indicators["本期淨利"] / indicators["營業收入"]
            
            # 報酬率
            indicators["總資產"] = balance_sheet["總資產"].iloc[-1]
            indicators["權益總額"] = balance_sheet["權益總額"].iloc[-1]
            
            indicators["ROE"] = indicators["本期淨利"] / indicators["權益總額"]
            indicators["ROA"] = indicators["本期淨利"] / indicators["總資產"]
            
            # 2. 財務結構指標
            indicators["總負債"] = balance_sheet["總負債"].iloc[-1]
            indicators["流動資產"] = balance_sheet["流動資產"].iloc[-1]
            indicators["流動負債"] = balance_sheet["流動負債"].iloc[-1]
            indicators["非流動資產"] = balance_sheet["非流動資產"].iloc[-1]
            indicators["非流動負債"] = balance_sheet["非流動負債"].iloc[-1]
            
            indicators["負債比率"] = indicators["總負債"] / indicators["總資產"]
            indicators["權益比率"] = indicators["權益總額"] / indicators["總資產"]
            indicators["流動比率"] = indicators["流動資產"] / indicators["流動負債"]
            indicators["長期資金適合率"] = (indicators["權益總額"] + indicators["非流動負債"]) / indicators["非流動資產"]
            
            # 3. 營運效率指標
            indicators["存貨"] = balance_sheet["存貨"].iloc[-1]
            indicators["應收帳款"] = balance_sheet["應收帳款"].iloc[-1]
            indicators["營業成本"] = income_statement["營業成本"].iloc[-1]
            
            # 週轉率計算（假設使用年化數據）
            indicators["應收帳款週轉率"] = indicators["營業收入"] / indicators["應收帳款"]
            indicators["存貨週轉率"] = indicators["營業成本"] / indicators["存貨"]
            indicators["總資產週轉率"] = indicators["營業收入"] / indicators["總資產"]
            
            # 週轉天數
            indicators["應收帳款週轉天數"] = 365 / indicators["應收帳款週轉率"]
            indicators["存貨週轉天數"] = 365 / indicators["存貨週轉率"]
            indicators["營運週期"] = indicators["應收帳款週轉天數"] + indicators["存貨週轉天數"]
            
            # 4. 現金流量指標
            indicators["營運現金流量"] = cash_flow["營業活動現金流量"].iloc[-1]
            indicators["投資現金流量"] = cash_flow["投資活動現金流量"].iloc[-1]
            indicators["籌資現金流量"] = cash_flow["籌資活動現金流量"].iloc[-1]
            
            indicators["現金流量比率"] = indicators["營運現金流量"] / indicators["流動負債"]
            indicators["現金再投資比率"] = indicators["營運現金流量"] / indicators["本期淨利"]
            
            # 5. 槓桿指標
            indicators["利息費用"] = income_statement.get("利息費用", pd.Series([0])).iloc[-1]
            indicators["財務槓桿度"] = indicators["總負債"] / indicators["權益總額"]
            indicators["營運槓桿度"] = (indicators["營業收入"] - indicators["營業成本"]) / indicators["營業利益"]
            indicators["總槓桿度"] = indicators["營運槓桿度"] * indicators["財務槓桿度"]
            
            # 6. 每股指標
            indicators["普通股股數"] = balance_sheet["普通股股數"].iloc[-1]
            indicators["每股盈餘"] = indicators["本期淨利"] / indicators["普通股股數"]
            indicators["每股淨值"] = indicators["權益總額"] / indicators["普通股股數"]
            
            # 7. 其他指標
            indicators["折舊"] = balance_sheet.get("折舊", pd.Series([0])).iloc[-1]
            indicators["攤銷"] = balance_sheet.get("攤銷", pd.Series([0])).iloc[-1]
            indicators["EBITDA"] = indicators["營業利益"] + indicators["折舊"] + indicators["攤銷"]
            indicators["EBITDA利潤率"] = indicators["EBITDA"] / indicators["營業收入"]
            
        except Exception as e:
            print(f"計算財務指標時發生錯誤: {str(e)}")
            # 對於出錯的指標，設置為0或其他預設值
            
        return indicators

    def load_financial_statements(self, company_code: str, year: int, quarter: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        讀取指定公司和期間的財務報表數據
        
        Args:
            company_code: 公司代碼
            year: 年份
            quarter: 季度
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: 
            資產負債表、損益表、現金流量表數據
        """
        # 構建文件路徑
        base_path = os.path.join(self.data_dir, company_code, f"{year}Q{quarter}")
        
        # 讀取各個報表
        balance_sheet = self._read_csv_safely(os.path.join(base_path, "balance_sheet.csv"))
        income_statement = self._read_csv_safely(os.path.join(base_path, "income_statement.csv"))
        cash_flow = self._read_csv_safely(os.path.join(base_path, "cash_flow.csv"))
        
        return balance_sheet, income_statement, cash_flow

    def _read_csv_safely(self, file_path: str) -> pd.DataFrame:
        """
        安全地讀取CSV文件
        
        Args:
            file_path: CSV文件路徑
            
        Returns:
            pd.DataFrame: 讀取的數據框
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"讀取文件 {file_path} 時發生錯誤: {str(e)}")
            return pd.DataFrame()

def main():
    """
    測試數據加載功能
    """
    # 設置數據目錄
    data_dir = "../../data/financial_statements"
    
    # 創建數據加載器
    loader = FinancialDataLoader(data_dir)
    
    # 讀取測試數據
    company_code = "2330"  # 以台積電為例
    year = 2023
    quarter = 4
    
    balance_sheet, income_statement, cash_flow = loader.load_financial_statements(
        company_code, year, quarter
    )
    
    # 創建分析代理
    from agents.analysis_agent import AnalysisAgent
    agent = AnalysisAgent()
    
    # 生成分析報告
    analysis_report = agent.analyze_financial_statements(
        balance_sheet, income_statement, cash_flow
    )
    
    # 打印分析報告
    for section, content in analysis_report.items():
        print(f"\n{section}")
        print("=" * 50)
        print(content)
        print("\n")

if __name__ == "__main__":
    main() 
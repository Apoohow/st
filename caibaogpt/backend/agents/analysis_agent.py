from typing import Dict, Any, List
import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.openai_api import ask_gpt
from .indicator_extractor import IndicatorExtractor
from utils.financial_data_loader import FinancialDataLoader

def create_analysis_prompt(summary: str, indicators: Dict[str, Any]) -> str:
    """
    根據財報摘要和財務指標生成 GPT 提示詞
    
    Args:
        summary: 財報摘要文字
        indicators: 財務指標字典
        
    Returns:
        str: GPT 提示詞
    """
    # 格式化指標數據
    formatted_indicators = []
    for key, value in indicators.items():
        if isinstance(value, (int, float)):
            if key.endswith('率') or key in ['ROA', 'ROE']:
                formatted_value = f"{value * 100:.2f}%"
            elif abs(value) >= 1_000_000_000:
                formatted_value = f"{value / 1_000_000_000:.2f}十億"
            elif abs(value) >= 1_000_000:
                formatted_value = f"{value / 1_000_000:.2f}百萬"
            else:
                formatted_value = f"{value:,.2f}"
            formatted_indicators.append(f"{key}: {formatted_value}")

    indicators_text = "\n".join(formatted_indicators)
    
    return f"""請以專業財務分析師的角度，對以下財務報表進行深入分析，並提供詳細的分析報告。

財務報表摘要：
{summary}

關鍵財務指標：
{indicators_text}

請從以下幾個面向進行分析：

1. 獲利能力分析
   - 營收成長與品質
   - 毛利率與營業利益率趨勢
   - 淨利率表現
   - ROE 和 ROA 分析

2. 財務結構分析
   - 資產負債比率評估
   - 長短期償債能力
   - 資本結構合理性
   - 營運資金充足度

3. 營運效率分析
   - 資產運用效率
   - 營運週期
   - 現金流量品質
   - 營運槓桿程度

4. 風險評估
   - 財務風險
   - 營運風險
   - 市場風險
   - 其他潛在風險

5. 投資建議
   - 投資優勢
   - 投資風險
   - 投資建議與注意事項
   - 合理投資價位建議

請提供具體的數據支持，並使用專業但易懂的語言。回答長度不限，但請確保分析深入且全面。
"""

def analyze_financials(summary: str, indicators: Dict[str, Any] = None) -> Dict[str, str]:
    """
    使用 GPT 分析財報內容並提供建議
    
    Args:
        summary: 財報摘要
        indicators: 財務指標字典
        
    Returns:
        Dict[str, str]: 包含各個面向分析結果的字典
    """
    try:
        # 生成分析提示詞
        prompt = create_analysis_prompt(summary, indicators or {})
        
        # 獲取 GPT 分析結果
        analysis = ask_gpt(prompt)
        
        # 將分析結果分類
        sections = {
            'profitability': '獲利能力分析',
            'financial_structure': '財務結構分析',
            'operational_efficiency': '營運效率分析',
            'risk_assessment': '風險評估',
            'investment_advice': '投資建議'
        }
        
        # 為每個面向生成詳細分析
        detailed_analysis = {}
        for section_key, section_name in sections.items():
            section_prompt = f"""
            基於以下完整分析，請專注於"{section_name}"部分，提供更詳細的分析：

            {analysis}
            
            請用 200 字左右總結這個面向的關鍵發現和建議。
            """
            detailed_analysis[section_key] = ask_gpt(section_prompt).strip()
        
        return detailed_analysis
        
    except Exception as e:
        raise Exception(f"生成分析建議時發生錯誤：{str(e)}")

class AnalysisAgent:
    def __init__(self):
        self.data_loader = FinancialDataLoader("")  # 空路徑，因為我們只使用計算功能
        
    def analyze_financial_statements(self, balance_sheet: pd.DataFrame, income_statement: pd.DataFrame, cash_flow: pd.DataFrame) -> str:
        """
        分析財務報表並生成報告
        
        Args:
            balance_sheet: 資產負債表
            income_statement: 損益表
            cash_flow: 現金流量表
            
        Returns:
            str: 分析報告
        """
        # 計算財務指標
        indicators = self.data_loader.calculate_financial_indicators(
            balance_sheet, income_statement, cash_flow
        )
        
        # 生成分析報告
        report = self.analyze_financial_data(indicators)
        
        return report

    def analyze_financial_data(self, financial_data: Dict[str, float]) -> str:
        """
        生成完整的財務分析報告
        """
        profitability = self._generate_profitability_analysis(financial_data)
        financial_structure = self._generate_financial_structure_analysis(financial_data)
        operating_efficiency = self._generate_operating_efficiency_analysis(financial_data)
        risk = self._generate_risk_analysis(financial_data)
        investment = self._generate_investment_advice(financial_data)
        
        report = f"""
=== 財務分析報告 ===

一、獲利能力分析
{profitability}

二、財務結構分析
{financial_structure}

三、營運效率分析
{operating_efficiency}

四、風險評估分析
{risk}

五、投資建議分析
{investment}
"""
        return report

    def _generate_profitability_analysis(self, indicators: Dict[str, float]) -> str:
        """
        生成獲利能力分析報告
        """
        # 獲取關鍵指標
        revenue = indicators.get("營業收入", 0)
        revenue_growth = indicators.get("營收成長率", 0)
        gross_margin = indicators.get("毛利率", 0)
        operating_margin = indicators.get("營業利益率", 0)
        net_margin = indicators.get("淨利率", 0)
        roe = indicators.get("ROE", 0)
        roa = indicators.get("ROA", 0)
        
        # 格式化數據顯示
        metrics = f"""
獲利能力關鍵指標：
1. 營收規模與成長
   - 營業收入：{revenue:,.0f} 元
   - 營收成長率：{revenue_growth:.2%}

2. 獲利表現
   - 毛利率：{gross_margin:.2%}
   - 營業利益率：{operating_margin:.2%}
   - 淨利率：{net_margin:.2%}

3. 資產報酬
   - ROE：{roe:.2%}
   - ROA：{roa:.2%}
"""

        # 動態生成分析評語
        analysis = "獲利能力綜合分析：\n\n"
        
        # 1. 營收規模評估
        if revenue > 10000000000:  # 100億
            analysis += "1. 營收規模評估：公司營收規模龐大（超過百億），顯示具備相當市場地位"
        elif revenue > 1000000000:  # 10億
            analysis += "1. 營收規模評估：公司營收規模中等（超過十億），具有一定市場基礎"
        else:
            analysis += "1. 營收規模評估：公司營收規模較小，仍有成長空間"
        
        # 營收成長動能評估
        if revenue_growth > 0.3:
            analysis += "，且營收呈現高速成長（>30%），顯示業務擴張迅速。\n"
        elif revenue_growth > 0.1:
            analysis += "，且營收呈現穩健成長（>10%），業務發展態勢良好。\n"
        elif revenue_growth > 0:
            analysis += "，營收雖有成長但力道較弱，需加強業務拓展。\n"
        else:
            analysis += "，且營收呈現衰退，需審慎評估業務發展策略。\n"
        
        # 2. 獲利能力評估
        analysis += "\n2. 獲利能力評估：\n"
        
        # 毛利率評估
        if gross_margin > 0.4:
            analysis += f"   - 毛利率{gross_margin:.2%}，處於優異水準，顯示產品具備強大的價格優勢"
        elif gross_margin > 0.2:
            analysis += f"   - 毛利率{gross_margin:.2%}，處於合理水準，產品具有一定競爭力"
        else:
            analysis += f"   - 毛利率{gross_margin:.2%}，偏低，需加強產品定價能力或成本控制"
        
        # 營業利益率評估
        if operating_margin > 0.2:
            analysis += f"，營業利益率{operating_margin:.2%}，營運效率優異。\n"
        elif operating_margin > 0.1:
            analysis += f"，營業利益率{operating_margin:.2%}，營運效率尚可。\n"
        else:
            analysis += f"，營業利益率{operating_margin:.2%}，營運效率待提升。\n"
        
        # 淨利率評估
        if net_margin > 0.15:
            analysis += f"   - 淨利率{net_margin:.2%}，獲利能力強勁"
        elif net_margin > 0.05:
            analysis += f"   - 淨利率{net_margin:.2%}，獲利能力穩定"
        else:
            analysis += f"   - 淨利率{net_margin:.2%}，獲利能力較弱"
        
        # 3. 資產報酬評估
        analysis += "\n\n3. 資產報酬評估：\n"
        
        # ROE評估
        if roe > 0.2:
            analysis += f"   - ROE {roe:.2%}，股東權益報酬優異"
        elif roe > 0.1:
            analysis += f"   - ROE {roe:.2%}，股東權益報酬尚可"
        else:
            analysis += f"   - ROE {roe:.2%}，股東權益報酬偏低"
        
        # ROA評估
        if roa > 0.1:
            analysis += f"，ROA {roa:.2%}，資產運用效率高。\n"
        elif roa > 0.05:
            analysis += f"，ROA {roa:.2%}，資產運用效率中等。\n"
        else:
            analysis += f"，ROA {roa:.2%}，資產運用效率待提升。\n"
        
        # 4. 綜合建議
        analysis += "\n4. 綜合建議：\n"
        
        # 根據各項指標綜合評估
        suggestions = []
        
        if gross_margin < 0.2:
            suggestions.append("   - 建議加強產品定價策略和成本控制，提升毛利率")
        if operating_margin < 0.1:
            suggestions.append("   - 需優化營運效率，控制營業費用")
        if revenue_growth < 0.1:
            suggestions.append("   - 應強化市場開發，提升營收成長動能")
        if roe < 0.1:
            suggestions.append("   - 建議改善資本配置效率，提升股東權益報酬率")
        if roa < 0.05:
            suggestions.append("   - 需加強資產運用效率，提高資產報酬率")
        
        if not suggestions:
            analysis += "   - 公司整體獲利能力優異，建議維持現有經營策略\n"
            analysis += "   - 持續關注市場變化，確保競爭優勢\n"
        else:
            analysis += "\n".join(suggestions) + "\n"
        
        return metrics + "\n" + analysis

    def _generate_financial_structure_analysis(self, indicators: Dict[str, float]) -> str:
        """
        生成財務結構分析報告
        """
        # 獲取關鍵指標
        total_assets = indicators.get("總資產", 0)
        total_liabilities = indicators.get("總負債", 0)
        current_assets = indicators.get("流動資產", 0)
        current_liabilities = indicators.get("流動負債", 0)
        non_current_assets = indicators.get("非流動資產", 0)
        non_current_liabilities = indicators.get("非流動負債", 0)
        equity = indicators.get("權益總額", 0)
        
        debt_ratio = indicators.get("負債比率", 0)
        current_ratio = indicators.get("流動比率", 0)
        equity_ratio = indicators.get("權益比率", 0)
        long_term_funds_ratio = indicators.get("長期資金適合率", 0)
        
        # 格式化數據顯示
        metrics = f"""
財務結構關鍵指標：
1. 資產與負債規模
   - 總資產：{total_assets:,.0f} 元
   - 總負債：{total_liabilities:,.0f} 元
   - 權益總額：{equity:,.0f} 元

2. 財務結構比率
   - 負債比率：{debt_ratio:.2%}
   - 權益比率：{equity_ratio:.2%}

3. 償債能力指標
   - 流動比率：{current_ratio:.2f} 倍
   - 長期資金適合率：{long_term_funds_ratio:.2f} 倍

4. 資產配置
   - 流動資產：{current_assets:,.0f} 元 ({current_assets/total_assets:.2%})
   - 非流動資產：{non_current_assets:,.0f} 元 ({non_current_assets/total_assets:.2%})
"""

        # 動態生成分析評語
        analysis = "財務結構綜合分析：\n\n"
        
        # 1. 財務結構評估
        analysis += "1. 財務結構評估：\n"
        if debt_ratio > 0.7:
            analysis += f"   - 負債比率{debt_ratio:.2%}，處於高槓桿狀態，財務風險較高"
        elif debt_ratio > 0.5:
            analysis += f"   - 負債比率{debt_ratio:.2%}，槓桿使用中等，需注意風險控制"
        else:
            analysis += f"   - 負債比率{debt_ratio:.2%}，財務結構穩健"
        
        if equity_ratio < 0.3:
            analysis += f"，權益比率{equity_ratio:.2%}偏低，財務彈性較小。\n"
        else:
            analysis += f"，權益比率{equity_ratio:.2%}適當，具備財務彈性。\n"
        
        # 2. 償債能力評估
        analysis += "\n2. 償債能力評估：\n"
        if current_ratio > 2:
            analysis += f"   - 流動比率{current_ratio:.2f}倍，短期償債能力優異"
        elif current_ratio > 1.5:
            analysis += f"   - 流動比率{current_ratio:.2f}倍，短期償債能力良好"
        elif current_ratio > 1:
            analysis += f"   - 流動比率{current_ratio:.2f}倍，短期償債能力尚可"
        else:
            analysis += f"   - 流動比率{current_ratio:.2f}倍，短期償債能力不足"
        
        if long_term_funds_ratio > 1.2:
            analysis += f"，長期資金適合率{long_term_funds_ratio:.2f}倍，長期償債能力優異。\n"
        elif long_term_funds_ratio > 1:
            analysis += f"，長期資金適合率{long_term_funds_ratio:.2f}倍，長期償債能力尚可。\n"
        else:
            analysis += f"，長期資金適合率{long_term_funds_ratio:.2f}倍，長期資金配置需改善。\n"
        
        # 3. 資產配置評估
        analysis += "\n3. 資產配置評估：\n"
        current_assets_ratio = current_assets / total_assets
        if current_assets_ratio > 0.6:
            analysis += f"   - 流動資產占比{current_assets_ratio:.2%}，資產流動性高"
        elif current_assets_ratio > 0.4:
            analysis += f"   - 流動資產占比{current_assets_ratio:.2%}，資產流動性適中"
        else:
            analysis += f"   - 流動資產占比{current_assets_ratio:.2%}，資產流動性較低"
        
        non_current_assets_ratio = non_current_assets / total_assets
        if non_current_assets_ratio > 0.6:
            analysis += f"，非流動資產占比{non_current_assets_ratio:.2%}，長期投資比重較高。\n"
        else:
            analysis += f"，非流動資產占比{non_current_assets_ratio:.2%}，長期投資比重適中。\n"
        
        # 4. 綜合建議
        analysis += "\n4. 綜合建議：\n"
        suggestions = []
        
        if debt_ratio > 0.6:
            suggestions.append("   - 建議適度降低負債水平，減少財務風險")
        if current_ratio < 1.5:
            suggestions.append("   - 需加強短期償債能力，提高流動資產配置")
        if long_term_funds_ratio < 1:
            suggestions.append("   - 應改善長期資金結構，確保長期投資穩定性")
        if current_assets_ratio < 0.3:
            suggestions.append("   - 考慮提高流動資產比重，增加營運彈性")
        
        if not suggestions:
            analysis += "   - 整體財務結構穩健，建議維持現有財務政策\n"
            analysis += "   - 持續監控負債水平，確保償債能力穩定\n"
        else:
            analysis += "\n".join(suggestions) + "\n"
        
        return metrics + "\n" + analysis

    def _generate_operating_efficiency_analysis(self, indicators: Dict[str, float]) -> str:
        """
        生成營運效率分析報告
        """
        # 獲取關鍵指標
        revenue = indicators.get("營業收入", 0)
        total_assets = indicators.get("總資產", 0)
        accounts_receivable = indicators.get("應收帳款", 0)
        inventory = indicators.get("存貨", 0)
        
        receivables_turnover = indicators.get("應收帳款週轉率", 0)
        inventory_turnover = indicators.get("存貨週轉率", 0)
        asset_turnover = indicators.get("總資產週轉率", 0)
        
        receivables_days = indicators.get("應收帳款週轉天數", 0)
        inventory_days = indicators.get("存貨週轉天數", 0)
        operating_cycle = indicators.get("營運週期", 0)
        
        # 格式化數據顯示
        metrics = f"""
營運效率關鍵指標：
1. 資產運用效率
   - 總資產週轉率：{asset_turnover:.2f} 次
   - 應收帳款週轉率：{receivables_turnover:.2f} 次
   - 存貨週轉率：{inventory_turnover:.2f} 次

2. 營運週期
   - 應收帳款週轉天數：{receivables_days:.1f} 天
   - 存貨週轉天數：{inventory_days:.1f} 天
   - 營運週期：{operating_cycle:.1f} 天
"""

        # 動態生成分析評語
        analysis = "營運效率綜合分析：\n\n"
        
        # 1. 資產運用效率評估
        analysis += "1. 資產運用效率評估：\n"
        if asset_turnover > 1.5:
            analysis += f"   - 總資產週轉率{asset_turnover:.2f}次，資產運用效率優異"
        elif asset_turnover > 1:
            analysis += f"   - 總資產週轉率{asset_turnover:.2f}次，資產運用效率良好"
        elif asset_turnover > 0.5:
            analysis += f"   - 總資產週轉率{asset_turnover:.2f}次，資產運用效率尚可"
        else:
            analysis += f"   - 總資產週轉率{asset_turnover:.2f}次，資產運用效率待提升"
        
        # 2. 應收帳款管理評估
        analysis += "\n\n2. 應收帳款管理評估：\n"
        if receivables_days < 30:
            analysis += f"   - 應收帳款週轉天數{receivables_days:.1f}天，收款效率優異"
        elif receivables_days < 60:
            analysis += f"   - 應收帳款週轉天數{receivables_days:.1f}天，收款效率良好"
        elif receivables_days < 90:
            analysis += f"   - 應收帳款週轉天數{receivables_days:.1f}天，收款效率尚可"
        else:
            analysis += f"   - 應收帳款週轉天數{receivables_days:.1f}天，收款效率需改善"
        
        # 3. 存貨管理評估
        analysis += "\n\n3. 存貨管理評估：\n"
        if inventory_days < 30:
            analysis += f"   - 存貨週轉天數{inventory_days:.1f}天，存貨管理效率優異"
        elif inventory_days < 60:
            analysis += f"   - 存貨週轉天數{inventory_days:.1f}天，存貨管理效率良好"
        elif inventory_days < 90:
            analysis += f"   - 存貨週轉天數{inventory_days:.1f}天，存貨管理效率尚可"
        else:
            analysis += f"   - 存貨週轉天數{inventory_days:.1f}天，存貨管理效率需改善"
        
        # 4. 營運週期評估
        analysis += "\n\n4. 營運週期評估：\n"
        if operating_cycle < 60:
            analysis += f"   - 營運週期{operating_cycle:.1f}天，營運效率優異"
        elif operating_cycle < 90:
            analysis += f"   - 營運週期{operating_cycle:.1f}天，營運效率良好"
        elif operating_cycle < 120:
            analysis += f"   - 營運週期{operating_cycle:.1f}天，營運效率尚可"
        else:
            analysis += f"   - 營運週期{operating_cycle:.1f}天，營運效率需改善"
        
        # 5. 綜合建議
        analysis += "\n\n5. 綜合建議：\n"
        suggestions = []
        
        if asset_turnover < 1:
            suggestions.append("   - 建議提升資產使用效率，增加營收貢獻")
        if receivables_days > 60:
            suggestions.append("   - 需加強應收帳款管理，縮短收款天數")
        if inventory_days > 60:
            suggestions.append("   - 應優化存貨管理，降低庫存天數")
        if operating_cycle > 90:
            suggestions.append("   - 建議縮短整體營運週期，提升營運效率")
        
        if not suggestions:
            analysis += "   - 整體營運效率良好，建議維持現有管理政策\n"
            analysis += "   - 持續監控各項週轉指標，確保營運效率穩定\n"
        else:
            analysis += "\n".join(suggestions) + "\n"
        
        return metrics + "\n" + analysis

    def _generate_risk_analysis(self, indicators: Dict[str, float]) -> str:
        """
        生成風險評估報告
        """
        # 獲取關鍵指標
        debt_ratio = indicators.get("負債比率", 0)
        current_ratio = indicators.get("流動比率", 0)
        operating_leverage = indicators.get("營運槓桿度", 0)
        financial_leverage = indicators.get("財務槓桿度", 0)
        total_leverage = indicators.get("總槓桿度", 0)
        
        cash_flow_ratio = indicators.get("現金流量比率", 0)
        reinvestment_ratio = indicators.get("現金再投資比率", 0)
        
        operating_cash_flow = indicators.get("營運現金流量", 0)
        investing_cash_flow = indicators.get("投資現金流量", 0)
        financing_cash_flow = indicators.get("籌資現金流量", 0)
        
        # 格式化數據顯示
        metrics = f"""
風險評估關鍵指標：
1. 財務風險指標
   - 負債比率：{debt_ratio:.2%}
   - 流動比率：{current_ratio:.2f} 倍

2. 槓桿風險指標
   - 營運槓桿度：{operating_leverage:.2f} 倍
   - 財務槓桿度：{financial_leverage:.2f} 倍
   - 總槓桿度：{total_leverage:.2f} 倍

3. 現金流量風險指標
   - 現金流量比率：{cash_flow_ratio:.2%}
   - 現金再投資比率：{reinvestment_ratio:.2%}
   - 營運現金流量：{operating_cash_flow:,.0f} 元
   - 投資現金流量：{investing_cash_flow:,.0f} 元
   - 籌資現金流量：{financing_cash_flow:,.0f} 元
"""

        # 動態生成分析評語
        analysis = "風險評估綜合分析：\n\n"
        
        # 1. 財務風險評估
        analysis += "1. 財務風險評估：\n"
        if debt_ratio > 0.7:
            analysis += f"   - 負債比率{debt_ratio:.2%}，財務風險較高"
        elif debt_ratio > 0.5:
            analysis += f"   - 負債比率{debt_ratio:.2%}，財務風險中等"
        else:
            analysis += f"   - 負債比率{debt_ratio:.2%}，財務風險較低"
        
        if current_ratio < 1:
            analysis += f"，流動比率{current_ratio:.2f}倍，短期償債風險高。\n"
        elif current_ratio < 1.5:
            analysis += f"，流動比率{current_ratio:.2f}倍，短期償債風險中等。\n"
        else:
            analysis += f"，流動比率{current_ratio:.2f}倍，短期償債風險低。\n"
        
        # 2. 槓桿風險評估
        analysis += "\n2. 槓桿風險評估：\n"
        if operating_leverage > 3:
            analysis += f"   - 營運槓桿度{operating_leverage:.2f}倍，營運風險較高"
        elif operating_leverage > 2:
            analysis += f"   - 營運槓桿度{operating_leverage:.2f}倍，營運風險中等"
        else:
            analysis += f"   - 營運槓桿度{operating_leverage:.2f}倍，營運風險較低"
        
        if financial_leverage > 2:
            analysis += f"，財務槓桿度{financial_leverage:.2f}倍，財務風險較高。\n"
        elif financial_leverage > 1.5:
            analysis += f"，財務槓桿度{financial_leverage:.2f}倍，財務風險中等。\n"
        else:
            analysis += f"，財務槓桿度{financial_leverage:.2f}倍，財務風險較低。\n"
        
        if total_leverage > 4:
            analysis += f"   - 總槓桿度{total_leverage:.2f}倍，整體經營風險較高。\n"
        elif total_leverage > 3:
            analysis += f"   - 總槓桿度{total_leverage:.2f}倍，整體經營風險中等。\n"
        else:
            analysis += f"   - 總槓桿度{total_leverage:.2f}倍，整體經營風險較低。\n"
        
        # 3. 現金流量風險評估
        analysis += "\n3. 現金流量風險評估：\n"
        if operating_cash_flow < 0:
            analysis += "   - 營運現金流量為負，營運資金壓力大"
        elif operating_cash_flow < financing_cash_flow:
            analysis += "   - 營運現金流量不足以支應籌資需求，需關注資金壓力"
        else:
            analysis += "   - 營運現金流量充足，營運資金壓力小"
        
        if cash_flow_ratio < 0.1:
            analysis += f"，現金流量比率{cash_flow_ratio:.2%}偏低，現金流量風險較高。\n"
        elif cash_flow_ratio < 0.2:
            analysis += f"，現金流量比率{cash_flow_ratio:.2%}中等，現金流量風險中等。\n"
        else:
            analysis += f"，現金流量比率{cash_flow_ratio:.2%}良好，現金流量風險較低。\n"
        
        # 4. 綜合風險評估
        analysis += "\n4. 綜合風險評估與建議：\n"
        suggestions = []
        
        if debt_ratio > 0.6:
            suggestions.append("   - 建議降低負債水平，減少財務風險")
        if current_ratio < 1.5:
            suggestions.append("   - 需提高流動比率，降低短期償債風險")
        if operating_leverage > 2.5:
            suggestions.append("   - 應控制營運槓桿，降低營運風險")
        if financial_leverage > 1.8:
            suggestions.append("   - 建議降低財務槓桿，減少財務風險")
        if cash_flow_ratio < 0.15:
            suggestions.append("   - 需改善現金流量，增強風險承受能力")
        
        if not suggestions:
            analysis += "   - 整體風險水平可控，建議維持現有風險管理政策\n"
            analysis += "   - 持續監控各項風險指標，確保經營穩定性\n"
        else:
            analysis += "\n".join(suggestions) + "\n"
        
        return metrics + "\n" + analysis

    def _generate_investment_advice(self, indicators: Dict[str, float]) -> str:
        """
        生成投資建議報告，整合所有財務指標分析結果
        """
        # 獲取關鍵指標
        investment_metrics = {
            # 獲利能力指標
            "營業收入": indicators.get("營業收入", 0),
            "營收成長率": indicators.get("營收成長率", 0),
            "毛利率": indicators.get("毛利率", 0),
            "營業利益率": indicators.get("營業利益率", 0),
            "淨利率": indicators.get("淨利率", 0),
            "ROE": indicators.get("ROE", 0),
            "ROA": indicators.get("ROA", 0),
            
            # 財務結構指標
            "負債比率": indicators.get("負債比率", 0),
            "權益比率": indicators.get("權益比率", 0),
            "流動比率": indicators.get("流動比率", 0),
            
            # 營運效率指標
            "總資產週轉率": indicators.get("總資產週轉率", 0),
            "應收帳款週轉天數": indicators.get("應收帳款週轉天數", 0),
            "存貨週轉天數": indicators.get("存貨週轉天數", 0),
            "營運週期": indicators.get("營運週期", 0),
            
            # 現金流量指標
            "營運現金流量": indicators.get("營運現金流量", 0),
            "自由現金流量": indicators.get("自由現金流量", 0),
            "現金流量比率": indicators.get("現金流量比率", 0),
            
            # 風險指標
            "營運槓桿度": indicators.get("營運槓桿度", 0),
            "財務槓桿度": indicators.get("財務槓桿度", 0),
            "總槓桿度": indicators.get("總槓桿度", 0),
            
            # 市場表現指標
            "每股盈餘": indicators.get("每股盈餘", 0),
            "股價淨值比": indicators.get("股價淨值比", 0),
            "本益比": indicators.get("本益比", 0)
        }
        
        # 格式化數據顯示
        metrics_explanation = "\n投資關鍵指標：\n"
        
        # 獲利表現
        metrics_explanation += f"獲利表現：\n"
        metrics_explanation += f"- 營業收入：{investment_metrics['營業收入']:,.0f} 元\n"
        metrics_explanation += f"- 營收成長率：{investment_metrics['營收成長率']:.2%}\n"
        metrics_explanation += f"- 毛利率：{investment_metrics['毛利率']:.2%}\n"
        metrics_explanation += f"- 營業利益率：{investment_metrics['營業利益率']:.2%}\n"
        metrics_explanation += f"- ROE：{investment_metrics['ROE']:.2%}\n"
        metrics_explanation += f"- ROA：{investment_metrics['ROA']:.2%}\n\n"
        
        # 財務狀況
        metrics_explanation += f"財務狀況：\n"
        metrics_explanation += f"- 負債比率：{investment_metrics['負債比率']:.2%}\n"
        metrics_explanation += f"- 流動比率：{investment_metrics['流動比率']:.2f} 倍\n"
        metrics_explanation += f"- 營運週期：{investment_metrics['營運週期']:.1f} 天\n\n"
        
        # 現金流量
        metrics_explanation += f"現金流量：\n"
        metrics_explanation += f"- 營運現金流量：{investment_metrics['營運現金流量']:,.0f} 元\n"
        metrics_explanation += f"- 自由現金流量：{investment_metrics['自由現金流量']:,.0f} 元\n"
        metrics_explanation += f"- 現金流量比率：{investment_metrics['現金流量比率']:.2%}\n\n"
        
        # 市場表現
        metrics_explanation += f"市場表現：\n"
        metrics_explanation += f"- 每股盈餘：{investment_metrics['每股盈餘']:.2f} 元\n"
        metrics_explanation += f"- 本益比：{investment_metrics['本益比']:.2f} 倍\n"
        metrics_explanation += f"- 股價淨值比：{investment_metrics['股價淨值比']:.2f} 倍\n"
        
        # 生成投資建議
        analysis = f"""
投資綜合分析：

1. 營運表現評估：
   - 營收規模 {investment_metrics['營業收入']:,.0f} 元，{'顯示經營規模可觀' if investment_metrics['營業收入'] > 10000000000 else '營運規模尚待提升'}
   - 營收成長 {investment_metrics['營收成長率']:.2%}，{'成長動能強勁' if investment_metrics['營收成長率'] > 0.2 else '成長力道待加強'}
   - 毛利率 {investment_metrics['毛利率']:.2%}，{'顯示具備良好獲利能力' if investment_metrics['毛利率'] > 0.3 else '獲利能力有待提升'}
   - ROE {investment_metrics['ROE']:.2%}，{'股東權益報酬優異' if investment_metrics['ROE'] > 0.15 else '股東報酬待改善'}

2. 財務結構評估：
   - 負債比率 {investment_metrics['負債比率']:.2%}，{'財務槓桿較高需注意風險' if investment_metrics['負債比率'] > 0.5 else '財務結構相對穩健'}
   - 流動比率 {investment_metrics['流動比率']:.2f} 倍，{'短期償債能力佳' if investment_metrics['流動比率'] > 2 else '流動性風險需關注'}
   - 營運週期 {investment_metrics['營運週期']:.1f} 天，{'營運效率良好' if investment_metrics['營運週期'] < 90 else '營運效率有待提升'}

3. 現金流量評估：
   - 營運現金流量 {investment_metrics['營運現金流量']:,.0f} 元，{'營運現金創造能力強' if investment_metrics['營運現金流量'] > 0 else '營運現金流需改善'}
   - 自由現金流量 {investment_metrics['自由現金流量']:,.0f} 元，{'具備良好投資發展潛力' if investment_metrics['自由現金流量'] > 0 else '自由現金流待加強'}
   - 現金流量比率 {investment_metrics['現金流量比率']:.2%}，{'現金流量充裕' if investment_metrics['現金流量比率'] > 0.2 else '現金流量管理需加強'}

4. 風險評估：
   - 營運槓桿度 {investment_metrics['營運槓桿度']:.2f} 倍，{'營運風險較高' if investment_metrics['營運槓桿度'] > 3 else '營運風險可控'}
   - 財務槓桿度 {investment_metrics['財務槓桿度']:.2f} 倍，{'財務風險需關注' if investment_metrics['財務槓桿度'] > 2 else '財務風險可控'}
   - 總槓桿度 {investment_metrics['總槓桿度']:.2f} 倍，{'整體風險偏高' if investment_metrics['總槓桿度'] > 4 else '整體風險程度可控'}

5. 投資價值評估：
   - 每股盈餘 {investment_metrics['每股盈餘']:.2f} 元，{'獲利表現優異' if investment_metrics['每股盈餘'] > 5 else '獲利能力待提升'}
   - 本益比 {investment_metrics['本益比']:.2f} 倍，{'評價合理' if 10 <= investment_metrics['本益比'] <= 20 else '需評估投資價值'}
   - 股價淨值比 {investment_metrics['股價淨值比']:.2f} 倍，{'評價合理' if 0.8 <= investment_metrics['股價淨值比'] <= 2 else '需評估投資價值'}

投資建議：
1. {'建議投資' if (
    investment_metrics['ROE'] > 0.15 and 
    investment_metrics['負債比率'] < 0.5 and 
    investment_metrics['營收成長率'] > 0.1
) else '建議觀望'}

2. 投資重點關注：
   - {'成長性佳，' if investment_metrics['營收成長率'] > 0.1 else '成長性待觀察，'}
   - {'獲利能力強，' if investment_metrics['ROE'] > 0.15 else '獲利能力待提升，'}
   - {'財務結構穩健，' if investment_metrics['負債比率'] < 0.5 else '財務結構需改善，'}
   - {'現金流量充足，' if investment_metrics['現金流量比率'] > 0.2 else '現金流量待加強，'}
   - {'風險程度可控' if investment_metrics['總槓桿度'] < 4 else '風險程度較高'}

3. 投資風險提示：
   - {'負債比率偏高，需注意財務風險' if investment_metrics['負債比率'] > 0.5 else '財務結構相對穩健'}
   - {'營運槓桿度高，獲利波動風險大' if investment_metrics['營運槓桿度'] > 3 else '營運風險程度可控'}
   - {'現金流量不足，需關注營運資金' if investment_metrics['現金流量比率'] < 0.2 else '現金流量狀況良好'}
"""
        
        return metrics_explanation + "\n分析：" + analysis

def main():
    """
    測試分析報告生成
    """
    # 模擬財務數據
    test_data = {
        "本期淨利": 1200000000,
        "權益總額": 8000000000,
        "總資產": 12000000000,
        "營業收入": 15000000000,
        "毛利": 4500000000,
        "營業利益": 2000000000,
        "折舊": 500000000,
        "攤銷": 200000000,
        "總負債": 4000000000,
        "流動資產": 6000000000,
        "流動負債": 3000000000,
        "存貨": 2000000000,
        "非流動負債": 1000000000,
        "非流動資產": 6000000000,
        "應收帳款": 1500000000,
        "營業成本": 10500000000,
        "前期營業收入": 12000000000,
        "前期淨利": 1000000000,
        "營業活動現金流量": 1800000000,
        "利息費用": 100000000,
        "普通股股數": 1000000000
    }

    # 創建指標提取器和分析代理
    agent = AnalysisAgent()

    # 生成分析報告
    analysis_report = agent.analyze_financial_statements(pd.DataFrame([test_data]), pd.DataFrame([test_data]), pd.DataFrame([test_data]))

    # 打印分析報告
    print(analysis_report)

if __name__ == "__main__":
    main() 
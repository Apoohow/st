import pdfplumber
import pandas as pd
import re
from typing import Dict, List, Union
import PyPDF2
import io

def extract_table_from_pdf(pdf_file) -> List[pd.DataFrame]:
    """
    從 PDF 檔案中提取表格數據
    
    Args:
        pdf_file: PDF 檔案物件
        
    Returns:
        List[pd.DataFrame]: 提取出的表格列表
    """
    tables = []
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # 提取頁面中的表格
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table and len(table) > 1:  # 確保表格有內容
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append(df)
        return tables
    except Exception as e:
        print(f"PDF 解析錯誤: {str(e)}")
        raise Exception("PDF 檔案解析失敗")

def identify_statement_type(df: pd.DataFrame) -> str:
    """
    識別財務報表類型（資產負債表、損益表、現金流量表）
    
    Args:
        df: 財務報表 DataFrame
        
    Returns:
        str: 報表類型
    """
    # 搜尋關鍵字來判斷報表類型
    keywords = {
        '資產負債表': ['資產', '負債', '權益'],
        '損益表': ['營業收入', '營業成本', '稅前淨利'],
        '現金流量表': ['營業活動', '投資活動', '籌資活動']
    }
    
    text = ' '.join(df.columns.astype(str))
    for statement_type, kwords in keywords.items():
        if any(keyword in text for keyword in kwords):
            return statement_type
    return '未知報表'

def clean_numeric_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    清理數值資料，移除貨幣符號和千分位逗號
    
    Args:
        df: 原始 DataFrame
        
    Returns:
        pd.DataFrame: 清理後的 DataFrame
    """
    def clean_value(value):
        if isinstance(value, str):
            # 移除貨幣符號和千分位逗號
            value = re.sub(r'[^\d.-]', '', value)
            try:
                return float(value)
            except ValueError:
                return value
        return value

    # 對數值欄位進行清理
    numeric_columns = df.select_dtypes(include=['object']).columns
    for col in numeric_columns:
        df[col] = df[col].apply(clean_value)
    
    return df

def parse_pdf(file):
    """
    解析上傳的 PDF 檔案並返回文字內容
    """
    try:
        # 讀取上傳的檔案
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        
        # 提取所有頁面的文字
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + "\n"
            
        return text_content.strip()
        
    except Exception as e:
        raise Exception(f"PDF 解析錯誤：{str(e)}")

def parse_pdf_structured(file) -> Dict[str, pd.DataFrame]:
    """
    解析財報 PDF 並返回結構化數據
    
    Args:
        file: PDF 檔案物件
        
    Returns:
        Dict[str, pd.DataFrame]: 各報表的結構化數據
    """
    # 提取所有表格
    tables = extract_table_from_pdf(file)
    
    # 初始化結果字典
    financial_statements = {
        '資產負債表': None,
        '損益表': None,
        '現金流量表': None
    }
    
    # 處理每個表格
    for df in tables:
        # 清理數據
        df = clean_numeric_values(df)
        
        # 識別報表類型
        statement_type = identify_statement_type(df)
        
        # 儲存對應的報表
        if statement_type in financial_statements:
            financial_statements[statement_type] = df
    
    # 確保至少解析出一個報表
    if all(v is None for v in financial_statements.values()):
        raise Exception("未能識別任何財務報表")
        
    return financial_statements 
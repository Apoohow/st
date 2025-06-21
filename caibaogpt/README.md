# 📘 CaiBaoGPT - 財報 AI 分析系統

## 🎯 專案簡介
CaiBaoGPT 是一個中文財報 AI 分析系統，使用者可以上傳 PDF 格式的財務報表，系統會自動解析三大報表、提取關鍵財務數據，並使用 GPT-4 進行智能分析，最後以條列式中文呈現分析報告。

## 🛠️ 技術架構
- 前端：React + Tailwind CSS
- 後端：Flask + OpenAI GPT-4
- 資料處理：pdfplumber + pandas

## 🚀 快速開始

### 後端設定
1. 進入後端目錄：
   ```bash
   cd backend
   ```

2. 建立虛擬環境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```

4. 設定環境變數：
   - 建立 `.env` 檔案
   - 加入 OpenAI API 金鑰：`OPENAI_API_KEY=your_api_key`

5. 啟動後端：
   ```bash
   python app.py
   ```

### 前端設定
1. 進入前端目錄：
   ```bash
   cd frontend
   ```

2. 安裝依賴：
   ```bash
   npm install
   ```

3. 啟動開發伺服器：
   ```bash
   npm start
   ```

## 📋 功能特色
- PDF 財報自動解析
- 關鍵財務指標提取
- GPT-4 智能分析
- 中文分析報告生成
- 美觀的使用者介面

## 🔒 安全性考量
- API 金鑰存放於 `.env` 檔案
- 前端不直接接觸 OpenAI API
- 所有 API 請求透過後端處理

## 🔄 開發中功能
- 自動計算財務比率
- 多年度財報趨勢分析
- 視覺化圖表呈現
- 多語言支援 
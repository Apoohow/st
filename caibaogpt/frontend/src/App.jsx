import React, { useState, useEffect } from 'react';
import './App.css';
import html2pdf from 'html2pdf.js/dist/html2pdf.bundle.min';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    fetch(API_BASE_URL)
      .then(response => response.json())
      .then(data => {
        if (data.status === 'ok') {
          setApiStatus('ready');
        } else {
          setApiStatus('error');
          setError('API 服務異常');
        }
      })
      .catch(error => {
        setApiStatus('error');
        setError('無法連接到 API 服務');
      });
  }, []);

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;
    
    if (uploadedFile.type !== 'application/pdf') {
      setError('請上傳 PDF 檔案');
      return;
    }

    setFile(uploadedFile);
    setError(null);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || '分析過程發生錯誤');
      }
      
      setAnalysis(data);
    } catch (error) {
      setError(error.message);
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (value) => {
    if (typeof value !== 'number') return value;
    if (Math.abs(value) >= 1_000_000_000) {
      return `${(value / 1_000_000_000).toFixed(2)} 十億`;
    } else if (Math.abs(value) >= 1_000_000) {
      return `${(value / 1_000_000).toFixed(2)} 百萬`;
    } else if (Math.abs(value) >= 1_000) {
      return `${(value / 1_000).toFixed(2)} 千`;
    }
    return value.toFixed(2);
  };

  const formatPercentage = (value) => {
    if (typeof value !== 'number') return value;
    return `${(value * 100).toFixed(2)}%`;
  };

  const downloadPDF = () => {
    const content = document.getElementById('report-content');
    const opt = {
      margin: [10, 10, 10, 10],
      filename: '財報分析報告.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { 
        scale: 2,
        useCORS: true,
        logging: false
      },
      jsPDF: { 
        unit: 'mm', 
        format: 'a4', 
        orientation: 'portrait'
      },
      pagebreak: { 
        mode: 'avoid-all',
        avoid: ['.indicator-item', '.report-header', '.report-section h3']
      }
    };
    
    html2pdf().set(opt).from(content).save();
  };

  if (apiStatus === 'checking') {
    return (
      <div className="App">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>正在連接到 API 服務...</p>
        </div>
      </div>
    );
  }

  if (apiStatus === 'error') {
    return (
      <div className="App">
        <div className="error-message">
          <h2>服務連接錯誤</h2>
          <p>{error}</p>
          <p>請確認後端服務是否正常運行</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>財報分析 GPT</h1>
        <div className="upload-container">
          <label className="upload-button" htmlFor="file-upload">
            {file ? '重新選擇檔案' : '選擇財報 PDF'}
            <input
              id="file-upload"
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
          {file && <p className="file-name">已選擇：{file.name}</p>}
        </div>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>正在分析財報，請稍候...</p>
          </div>
        )}

        {!analysis && !loading && !error && (
          <div className="welcome-container">
            <div className="welcome-card">
              <h2>歡迎使用財報分析 GPT</h2>
              <p className="welcome-description">
                我們的 AI 系統能夠快速分析財務報告，為您提供專業的財務分析和投資建議。
              </p>
              <div className="features-grid">
                <div className="feature-item">
                  <span className="feature-icon">📊</span>
                  <h3>關鍵指標分析</h3>
                  <p>自動計算並分析重要財務指標</p>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">📈</span>
                  <h3>趨勢分析</h3>
                  <p>分析財務數據的歷史趨勢</p>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">💡</span>
                  <h3>專業建議</h3>
                  <p>提供詳細的投資建議和風險評估</p>
                </div>
                <div className="feature-item">
                  <span className="feature-icon">📝</span>
                  <h3>完整報告</h3>
                  <p>生成可下載的 PDF 分析報告</p>
                </div>
              </div>
              <div className="upload-instructions">
                <h3>使用說明</h3>
                <ol>
                  <li>點擊上方的「選擇財報 PDF」按鈕</li>
                  <li>選擇您要分析的財務報告 PDF 檔案</li>
                  <li>等待系統進行智能分析</li>
                  <li>查看詳細的分析報告</li>
                  <li>下載 PDF 格式的完整報告</li>
                </ol>
              </div>
            </div>
          </div>
        )}

        {analysis && !loading && (
          <>
            <div className="download-button-container">
              <button onClick={downloadPDF} className="download-button">
                下載 PDF 報告
              </button>
            </div>
            <div id="report-content" className="report-content">
              <div className="report-header">
                <h2>財務分析報告</h2>
                <p className="report-date">報告日期：{new Date().toLocaleDateString('zh-TW')}</p>
              </div>
              
              <section className="report-section">
                <h3>財務摘要</h3>
                <p>{analysis.summary}</p>
              </section>

              <section className="report-section">
                <h3>關鍵財務指標</h3>
                <div className="indicators-grid">
                  {analysis.indicators && Object.entries(analysis.indicators).map(([key, value]) => (
                    <div key={key} className="indicator-item">
                      <span className="indicator-label">{key}：</span>
                      <span className="indicator-value">
                        {key.includes('率') || key === 'ROA' || key === 'ROE' 
                          ? formatPercentage(value)
                          : formatNumber(value)}
                      </span>
                    </div>
                  ))}
                </div>
              </section>

              <section className="report-section">
                <h3>獲利能力分析</h3>
                <p>{analysis.analysis.profitability}</p>
              </section>

              <section className="report-section">
                <h3>財務結構分析</h3>
                <p>{analysis.analysis.financial_structure}</p>
              </section>

              <section className="report-section">
                <h3>營運效率分析</h3>
                <p>{analysis.analysis.operational_efficiency}</p>
              </section>

              <section className="report-section">
                <h3>風險評估</h3>
                <p>{analysis.analysis.risk_assessment}</p>
              </section>

              <section className="report-section">
                <h3>投資建議</h3>
                <p>{analysis.analysis.investment_advice}</p>
              </section>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App; 
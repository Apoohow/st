from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import logging
from agents.analysis_agent import analyze_financials
from agents.parser_agent import parse_pdf
from agents.summary_agent import generate_summary, generate_financial_summary
from agents.indicator_extractor import extract_indicators

# 設定日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 啟用 CORS

@app.route('/')
def health_check():
    return jsonify({'status': 'ok', 'message': '財報分析 API 服務正常運行中'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '未找到檔案'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '未選擇檔案'}), 400
            
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': '請上傳 PDF 檔案'}), 400

        logger.info(f'開始處理檔案: {file.filename}')
        
        # 解析 PDF
        try:
            text_content = parse_pdf(file)
            logger.info('PDF 解析完成')
        except Exception as e:
            logger.error(f'PDF 解析錯誤: {str(e)}')
            logger.error(traceback.format_exc())
            return jsonify({'error': f'PDF 解析錯誤: {str(e)}'}), 500
        
        # 提取指標
        try:
            indicators = extract_indicators(text_content)
            logger.info('指標提取完成')
        except Exception as e:
            logger.error(f'指標提取錯誤: {str(e)}')
            logger.error(traceback.format_exc())
            return jsonify({'error': f'指標提取錯誤: {str(e)}'}), 500
        
        # 生成摘要（使用財務指標）
        try:
            financial_summary = generate_financial_summary(indicators)
            logger.info('財務摘要生成完成')
        except Exception as e:
            logger.error(f'財務摘要生成錯誤: {str(e)}')
            logger.error(traceback.format_exc())
            return jsonify({'error': f'財務摘要生成錯誤: {str(e)}'}), 500
            
        # 生成文本摘要（使用原始文本）
        try:
            text_summary = generate_summary(text_content)
            logger.info('文本摘要生成完成')
        except Exception as e:
            logger.error(f'文本摘要生成錯誤: {str(e)}')
            logger.error(traceback.format_exc())
            return jsonify({'error': f'文本摘要生成錯誤: {str(e)}'}), 500
        
        # 進行分析（使用兩種摘要的組合）
        try:
            combined_summary = f"{financial_summary}\n\n詳細分析：\n{text_summary}"
            analysis = analyze_financials(combined_summary, indicators)
            logger.info('財報分析完成')
        except Exception as e:
            logger.error(f'財報分析錯誤: {str(e)}')
            logger.error(traceback.format_exc())
            return jsonify({'error': f'財報分析錯誤: {str(e)}'}), 500
        
        return jsonify({
            'summary': combined_summary,
            'indicators': indicators,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f'未預期的錯誤: {str(e)}')
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
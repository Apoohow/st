import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const analyzePDF = async (file) => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });

        return response.data;
    } catch (error) {
        if (error.response) {
            // 伺服器回應的錯誤
            throw new Error(error.response.data.error || '分析過程發生錯誤');
        } else if (error.request) {
            // 請求發送失敗
            throw new Error('無法連接到伺服器，請確認伺服器是否運行中');
        } else {
            // 其他錯誤
            throw new Error('請求發生錯誤，請稍後再試');
        }
    }
}; 
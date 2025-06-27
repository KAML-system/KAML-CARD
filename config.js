// إعدادات الـ API للنظام
const API_CONFIG = {
    // عنوان الـ API الخاص بالجزء الخلفي
    // يجب تحديث هذا العنوان بعد نشر الجزء الخلفي على Heroku أو أي منصة أخرى
    BASE_URL: 'https://your-backend-app.herokuapp.com',
    
    // نقاط النهاية للـ API
    ENDPOINTS: {
        LOGIN: '/login',
        CREATE_CARD: '/create_card',
        VERIFY_CARD: '/verify_card',
        DOWNLOAD_CARD: '/download_card'
    },
    
    // إعدادات الطلبات
    REQUEST_CONFIG: {
        timeout: 30000, // 30 ثانية
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    }
};

// دالة مساعدة لبناء عنوان الـ API الكامل
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + API_CONFIG.ENDPOINTS[endpoint];
}

// دالة مساعدة لإرسال طلبات الـ API
async function apiRequest(endpoint, options = {}) {
    const url = getApiUrl(endpoint);
    const config = {
        ...API_CONFIG.REQUEST_CONFIG,
        ...options
    };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// تصدير الإعدادات للاستخدام في الملفات الأخرى
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, getApiUrl, apiRequest };
}


# دليل إعداد الـ API للجزء الخلفي

## 📋 نظرة عامة

هذا الدليل يوضح كيفية إعداد وربط الجزء الخلفي (API) مع الواجهة الأمامية المنشورة على GitHub Pages.

## 🔧 الخطوات المطلوبة

### 1️⃣ نشر الجزء الخلفي

يمكنك نشر الجزء الخلفي على إحدى المنصات التالية:

#### أ) Heroku (مجاني)
```bash
# 1. إنشاء تطبيق Heroku جديد
heroku create your-app-name

# 2. رفع الكود
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 3. الحصول على الرابط
https://your-app-name.herokuapp.com
```

#### ب) Render (مجاني)
1. اذهب إلى [render.com](https://render.com)
2. ربط مستودع GitHub
3. اختيار "Web Service"
4. إعداد البيئة: Python 3.11
5. أمر البناء: `pip install -r requirements.txt`
6. أمر التشغيل: `python main.py`

#### ج) Railway (مجاني)
1. اذهب إلى [railway.app](https://railway.app)
2. ربط مستودع GitHub
3. نشر تلقائي

### 2️⃣ تحديث عناوين الـ API

بعد نشر الجزء الخلفي، قم بتحديث الروابط في الملفات التالية:

#### في `config.js`:
```javascript
const API_CONFIG = {
    BASE_URL: 'https://your-actual-backend-url.herokuapp.com', // ⚠️ حدث هذا
    // باقي الإعدادات...
};
```

#### في `login.html`:
```javascript
const API_BASE_URL = 'https://your-actual-backend-url.herokuapp.com'; // ⚠️ حدث هذا
```

#### في `admin.html`:
```javascript
const API_BASE_URL = 'https://your-actual-backend-url.herokuapp.com'; // ⚠️ حدث هذا
```

### 3️⃣ إعداد CORS في الجزء الخلفي

تأكد من أن الجزء الخلفي يدعم CORS للسماح بالطلبات من GitHub Pages:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://your-username.github.io'])
```

### 4️⃣ متغيرات البيئة

قم بإعداد متغيرات البيئة التالية في منصة الاستضافة:

```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=https://your-username.github.io
```

## 🔗 نقاط النهاية المطلوبة

يجب أن يوفر الجزء الخلفي النقاط التالية:

### تسجيل الدخول
```
POST /api/login
Content-Type: application/json

{
    "username": "admin",
    "password": "kaml2024"
}
```

### إنشاء بطاقة
```
POST /api/create_card
Content-Type: multipart/form-data

- name_en: string
- name_ar: string  
- member_id: string
- organization: string
- photo: file
```

### التحقق من البطاقة
```
POST /api/verify_card
Content-Type: application/json

{
    "qr_data": "QR code content"
}
```

### تحميل البطاقة
```
GET /api/download_card/{card_id}
```

## 🧪 اختبار الاتصال

بعد النشر، اختبر الاتصال:

```javascript
// اختبار بسيط في وحدة تحكم المتصفح
fetch('https://your-backend-url.herokuapp.com/api/health')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
```

## 🔒 الأمان

### إعدادات HTTPS
- تأكد من أن جميع الطلبات تستخدم HTTPS
- لا تعرض مفاتيح API في الكود الأمامي

### التحقق من الهوية
- استخدم JWT tokens للجلسات
- قم بتشفير كلمات المرور
- حدد معدل الطلبات (Rate Limiting)

## 🚀 النشر السريع

### خطوات سريعة للنشر على Heroku:

1. **إنشاء حساب Heroku**
   - اذهب إلى [heroku.com](https://heroku.com)
   - أنشئ حساب مجاني

2. **تثبيت Heroku CLI**
   ```bash
   # Windows
   choco install heroku-cli
   
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

3. **نشر التطبيق**
   ```bash
   # تسجيل الدخول
   heroku login
   
   # إنشاء تطبيق
   heroku create kaml-backend-api
   
   # رفع الكود
   git add .
   git commit -m "Deploy backend"
   git push heroku main
   
   # فتح التطبيق
   heroku open
   ```

4. **تحديث الروابط**
   - انسخ رابط التطبيق من Heroku
   - حدث الروابط في ملفات الواجهة الأمامية
   - ارفع التحديثات إلى GitHub

## 📞 الدعم

إذا واجهت أي مشاكل:

1. تحقق من سجلات الخادم (Server Logs)
2. تأكد من إعدادات CORS
3. تحقق من متغيرات البيئة
4. اختبر نقاط النهاية باستخدام Postman أو curl

## 🎯 الخطوات التالية

بعد إكمال الإعداد:

1. ✅ اختبر تسجيل الدخول
2. ✅ اختبر إنشاء البطاقات
3. ✅ اختبر ماسح الباركود
4. ✅ تحقق من التحميل
5. ✅ اختبر على أجهزة مختلفة

---

**ملاحظة:** هذا الدليل يفترض استخدام Flask كإطار عمل للجزء الخلفي. إذا كنت تستخدم إطار عمل آخر، قم بتعديل التعليمات وفقاً لذلك.


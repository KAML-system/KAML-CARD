# دليل النشر الكامل - نظام KAML

## 🎯 نظرة عامة

هذا الدليل يوضح كيفية نشر نظام إدارة بطاقات العضوية للجمعية الكويتية للمختبرات الطبية على الإنترنت.

---

## 📋 المتطلبات

### للواجهة الأمامية (GitHub Pages)
- حساب GitHub مجاني
- متصفح ويب

### للجزء الخلفي (Heroku)
- حساب Heroku مجاني
- Git مثبت على جهازك
- Heroku CLI

---

## 🌐 الجزء الأول: نشر الواجهة الأمامية على GitHub Pages

### الخطوة 1: إنشاء Repository على GitHub

1. اذهب إلى [GitHub.com](https://github.com)
2. سجل دخول أو أنشئ حساب جديد
3. انقر على **"New repository"**
4. اسم المشروع: `kaml-card`
5. اجعله **Public**
6. أضف **README file**
7. انقر **"Create repository"**

### الخطوة 2: رفع الملفات

#### الطريقة الأولى: عبر واجهة GitHub
1. في صفحة المشروع، انقر **"uploading an existing file"**
2. اسحب وأفلت الملفات التالية:
   - `index.html`
   - `scanner.html`
   - `login.html`
   - `README.md`
3. اكتب رسالة commit: "إضافة نظام إدارة بطاقات العضوية"
4. انقر **"Commit changes"**

#### الطريقة الثانية: عبر Git
```bash
git clone https://github.com/YOUR_USERNAME/kaml-card.git
cd kaml-card
# انسخ الملفات هنا
git add .
git commit -m "إضافة نظام إدارة بطاقات العضوية"
git push origin main
```

### الخطوة 3: تفعيل GitHub Pages

1. في صفحة المشروع، اذهب إلى **Settings**
2. انتقل إلى **Pages** في القائمة الجانبية
3. في **Source**، اختر **"Deploy from a branch"**
4. اختر **main** branch
5. اختر **/ (root)** folder
6. انقر **Save**

### الخطوة 4: الوصول للموقع

بعد بضع دقائق، سيكون موقعك متاحاً على:
```
https://YOUR_USERNAME.github.io/kaml-card/
```

---

## ⚙️ الجزء الثاني: نشر الجزء الخلفي على Heroku

### الخطوة 1: إعداد Heroku

1. أنشئ حساب على [Heroku.com](https://heroku.com)
2. ثبت [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. سجل دخول:
```bash
heroku login
```

### الخطوة 2: إعداد المشروع

1. أنشئ مجلد جديد للجزء الخلفي:
```bash
mkdir kaml-backend
cd kaml-backend
```

2. انسخ ملفات الجزء الخلفي من مجلد `deployment/backend`

3. أنشئ Git repository:
```bash
git init
git add .
git commit -m "Initial commit"
```

### الخطوة 3: إنشاء تطبيق Heroku

```bash
heroku create kaml-membership-api
```

### الخطوة 4: إعداد متغيرات البيئة

```bash
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key-here
```

### الخطوة 5: النشر

```bash
git push heroku main
```

### الخطوة 6: فتح التطبيق

```bash
heroku open
```

---

## 🔗 الجزء الثالث: ربط الواجهة الأمامية بالخلفية

### تحديث ملفات JavaScript

في ملفات `scanner.html` و `login.html`، عدل عنوان API:

```javascript
// بدلاً من
const API_BASE = 'http://localhost:5000';

// استخدم
const API_BASE = 'https://kaml-membership-api.herokuapp.com';
```

### رفع التحديثات

```bash
git add .
git commit -m "ربط الواجهة الأمامية بالخلفية"
git push origin main
```

---

## 🛡️ الجزء الرابع: إعداد الأمان

### تفعيل HTTPS

- GitHub Pages يدعم HTTPS تلقائياً
- Heroku يدعم HTTPS تلقائياً

### إعداد CORS

في ملف `main.py`، أضف:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://YOUR_USERNAME.github.io'])
```

---

## 📱 الجزء الخامس: الاختبار

### اختبار الواجهة الأمامية
1. اذهب إلى موقعك على GitHub Pages
2. تأكد من تحميل الصفحات بشكل صحيح
3. اختبر ماسح الباركود

### اختبار الجزء الخلفي
1. اذهب إلى تطبيق Heroku
2. اختبر APIs مباشرة
3. تأكد من عمل قاعدة البيانات

### اختبار التكامل
1. اختبر تسجيل الدخول
2. اختبر إنشاء البطاقات
3. اختبر مسح الباركود

---

## 🔧 استكشاف الأخطاء

### مشاكل GitHub Pages
- تأكد من أن الملفات في المجلد الصحيح
- تحقق من إعدادات Pages
- انتظر بضع دقائق للنشر

### مشاكل Heroku
```bash
heroku logs --tail
```

### مشاكل CORS
- تأكد من إعداد CORS بشكل صحيح
- تحقق من عناوين المواقع

---

## 📊 المراقبة والصيانة

### مراقبة Heroku
- استخدم Heroku Dashboard
- راقب استخدام الموارد
- تحقق من Logs بانتظام

### تحديث النظام
1. عدل الملفات محلياً
2. اختبر التغييرات
3. ارفع التحديثات:
```bash
git add .
git commit -m "وصف التحديث"
git push origin main  # للواجهة الأمامية
git push heroku main  # للجزء الخلفي
```

---

## 💰 التكلفة

### GitHub Pages
- **مجاني** للمشاريع العامة
- **محدود** للمشاريع الخاصة

### Heroku
- **مجاني** لـ 550 ساعة شهرياً
- **مدفوع** للاستخدام المكثف

---

## 🆘 الدعم

### الموارد المفيدة
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Heroku Documentation](https://devcenter.heroku.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

### للمساعدة
- **البريد الإلكتروني:** support@kaml.org.kw
- **GitHub Issues:** أنشئ issue في المشروع

---

## ✅ قائمة التحقق النهائية

- [ ] تم إنشاء GitHub Repository
- [ ] تم رفع ملفات الواجهة الأمامية
- [ ] تم تفعيل GitHub Pages
- [ ] تم إنشاء تطبيق Heroku
- [ ] تم نشر الجزء الخلفي
- [ ] تم ربط الواجهة الأمامية بالخلفية
- [ ] تم اختبار النظام بالكامل
- [ ] تم إعداد المراقبة

---

**🎉 تهانينا! نظام KAML أصبح متاحاً على الإنترنت!**


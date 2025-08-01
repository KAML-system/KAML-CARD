# دليل تسجيل الدخول باسم المستخدم

## 🔐 **بيانات تسجيل الدخول:**

### **المسؤول الرئيسي:**
- **اسم المستخدم:** `admin`
- **كلمة المرور:** `kaml2024`

### **المدير:**
- **اسم المستخدم:** `manager`
- **كلمة المرور:** `kaml123`

## 🔄 **كيف يعمل النظام:**

### **1️⃣ تحويل اسم المستخدم:**
النظام يحول اسم المستخدم تلقائياً إلى بريد إلكتروني لـ Firebase:
- `admin` → `admin@kaml.org.kw`
- `manager` → `manager@kaml.org.kw`

### **2️⃣ إنشاء الحساب التلقائي:**
عند أول تسجيل دخول، النظام:
- يتحقق من بيانات الدخول
- ينشئ حساب Firebase تلقائياً
- يسجل دخول المستخدم

### **3️⃣ تسجيل الدخول اللاحق:**
في المرات التالية، النظام:
- يحول اسم المستخدم إلى بريد إلكتروني
- يسجل الدخول مباشرة من Firebase

## ✅ **المميزات:**

- ✅ **سهولة الاستخدام:** اسم مستخدم بسيط
- ✅ **أمان Firebase:** حماية متقدمة
- ✅ **إنشاء تلقائي:** لا حاجة لإعداد يدوي
- ✅ **مرونة:** يمكن إضافة مستخدمين جدد

## 🔧 **إضافة مستخدمين جدد:**

لإضافة مستخدم جديد، عدل ملف `firebase-config.js`:

```javascript
window.defaultAdmins = [
  { username: 'admin', password: 'kaml2024', email: 'admin@kaml.org.kw' },
  { username: 'manager', password: 'kaml123', email: 'manager@kaml.org.kw' },
  { username: 'newuser', password: 'newpass', email: 'newuser@kaml.org.kw' }
];
```

## 🛡️ **الأمان:**

- كلمات المرور محمية بـ Firebase Authentication
- البيانات مشفرة في قاعدة البيانات
- جلسات آمنة ومحدودة الوقت
- حماية من الهجمات الشائعة

## 📱 **الاستخدام:**

1. افتح صفحة تسجيل الدخول
2. أدخل اسم المستخدم: `admin`
3. أدخل كلمة المرور: `kaml2024`
4. انقر "تسجيل الدخول"
5. ستنتقل لصفحة الإدارة تلقائياً

---

**ملاحظة:** هذا النظام يجمع بين سهولة اسم المستخدم وأمان Firebase!


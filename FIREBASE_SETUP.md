# دليل إعداد Firebase لنظام بطاقات العضوية

## 🔥 **خطوات إعداد Firebase**

### **1️⃣ إنشاء مشروع Firebase**

1. اذهب إلى [Firebase Console](https://console.firebase.google.com/)
2. انقر على "Add project" أو "إضافة مشروع"
3. أدخل اسم المشروع: `kaml-membership-system`
4. اختر إعدادات Google Analytics (اختياري)
5. انقر "Create project"

### **2️⃣ إعداد Authentication**

1. في Firebase Console، اذهب إلى **Authentication**
2. انقر على **Get started**
3. اذهب إلى تبويب **Sign-in method**
4. فعل **Email/Password**:
   - انقر على Email/Password
   - فعل الخيار الأول (Email/Password)
   - احفظ التغييرات

### **3️⃣ إعداد Firestore Database**

1. اذهب إلى **Firestore Database**
2. انقر على **Create database**
3. اختر **Start in test mode** (للبداية)
4. اختر الموقع الجغرافي الأقرب
5. انقر **Done**

#### **إعداد قواعد الأمان:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write access to all users for now
    // يمكن تخصيص هذه القواعد لاحقاً
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### **4️⃣ إعداد Storage**

1. اذهب إلى **Storage**
2. انقر على **Get started**
3. اختر **Start in test mode**
4. اختر الموقع الجغرافي
5. انقر **Done**

#### **إعداد قواعد Storage:**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if true;
    }
  }
}
```

### **5️⃣ إعداد Web App**

1. في الصفحة الرئيسية للمشروع، انقر على أيقونة **Web** `</>`
2. أدخل اسم التطبيق: `KAML Card System`
3. فعل **Firebase Hosting** (اختياري)
4. انقر **Register app**
5. **انسخ إعدادات Firebase** التي ستظهر

### **6️⃣ تحديث إعدادات Firebase في الكود**

افتح ملف `firebase-config.js` وحدث الإعدادات:

```javascript
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID",
  measurementId: "YOUR_MEASUREMENT_ID"
};
```

## 👤 **إنشاء حسابات المسؤولين**

### **الطريقة الأولى: من خلال Firebase Console**

1. اذهب إلى **Authentication** → **Users**
2. انقر **Add user**
3. أدخل البيانات:
   - **Email:** `admin@kaml.org.kw`
   - **Password:** `kaml2024`
4. انقر **Add user**
5. كرر العملية للمدير:
   - **Email:** `manager@kaml.org.kw`
   - **Password:** `kaml123`

### **الطريقة الثانية: من خلال الكود**

استخدم الكود التالي في console المتصفح بعد تحميل الصفحة:

```javascript
// إنشاء حساب المسؤول الرئيسي
await window.authSystem.createAdminAccount(
  'admin@kaml.org.kw', 
  'kaml2024',
  {
    name: 'مسؤول النظام',
    role: 'admin',
    permissions: ['all']
  }
);

// إنشاء حساب المدير
await window.authSystem.createAdminAccount(
  'manager@kaml.org.kw', 
  'kaml123',
  {
    name: 'مدير النظام',
    role: 'manager',
    permissions: ['manage_members', 'create_cards']
  }
);
```

## 📊 **إعداد Collections في Firestore**

سيتم إنشاء هذه Collections تلقائياً عند استخدام النظام:

### **1. Collection: `members`**
```javascript
{
  arabicName: "string",
  englishName: "string", 
  civilId: "string",
  membershipNumber: "string",
  phone: "string",
  email: "string",
  address: "string",
  membershipType: "affiliated|non-affiliated|honorary",
  status: "active|inactive",
  createdAt: "timestamp",
  cardUrl: "string" // رابط البطاقة في Storage
}
```

### **2. Collection: `admins`**
```javascript
{
  uid: "string",
  email: "string",
  name: "string",
  role: "admin|manager",
  permissions: ["array"],
  isActive: "boolean",
  createdAt: "timestamp"
}
```

### **3. Collection: `cards`**
```javascript
{
  memberId: "string",
  membershipNumber: "string",
  cardUrl: "string",
  createdAt: "timestamp",
  createdBy: "string" // UID of admin who created it
}
```

## 🔒 **تحديث قواعد الأمان (للإنتاج)**

### **Firestore Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Members collection - read only for authenticated users
    match /members/{memberId} {
      allow read: if request.auth != null;
      allow write: if isAdmin();
    }
    
    // Admins collection - admin only
    match /admins/{adminId} {
      allow read, write: if isAdmin();
    }
    
    // Cards collection - admin only
    match /cards/{cardId} {
      allow read, write: if isAdmin();
    }
    
    // Helper function to check if user is admin
    function isAdmin() {
      return request.auth != null && 
             exists(/databases/$(database)/documents/admins/$(request.auth.uid)) &&
             get(/databases/$(database)/documents/admins/$(request.auth.uid)).data.isActive == true;
    }
  }
}
```

### **Storage Rules:**
```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Member photos and cards
    match /members/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if isAdmin();
    }
    
    // Cards folder
    match /cards/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if isAdmin();
    }
    
    function isAdmin() {
      return request.auth != null && 
             firestore.exists(/databases/(default)/documents/admins/$(request.auth.uid)) &&
             firestore.get(/databases/(default)/documents/admins/$(request.auth.uid)).data.isActive == true;
    }
  }
}
```

## ✅ **اختبار الإعداد**

### **1. اختبار الاتصال:**
1. افتح الموقع في المتصفح
2. افتح Developer Tools (F12)
3. اذهب إلى Console
4. يجب أن ترى: `"Firebase initialized successfully"`

### **2. اختبار تسجيل الدخول:**
1. اذهب إلى صفحة تسجيل الدخول
2. استخدم: `admin@kaml.org.kw` / `kaml2024`
3. يجب أن تنتقل لصفحة الإدارة

### **3. اختبار إنشاء البطاقات:**
1. في صفحة الإدارة، أدخل بيانات عضو جديد
2. ارفع صورة للعضو
3. انقر "إنشاء البطاقة"
4. يجب أن تظهر البطاقة وتُحفظ في Firebase

### **4. اختبار ماسح الباركود:**
1. اذهب إلى صفحة ماسح الباركود
2. امسح باركود البطاقة المُنشأة
3. يجب أن تظهر بيانات العضو

## 🚨 **مشاكل شائعة وحلولها**

### **خطأ: "Firebase not initialized"**
- تأكد من تحديث إعدادات Firebase في `firebase-config.js`
- تحقق من صحة API Key

### **خطأ: "Permission denied"**
- تأكد من إعداد قواعد Firestore و Storage
- تحقق من تسجيل الدخول بحساب مسؤول

### **خطأ: "Network error"**
- تحقق من اتصال الإنترنت
- تأكد من تفعيل الخدمات في Firebase Console

## 📞 **الدعم**

إذا واجهت أي مشاكل في الإعداد:
1. تحقق من Firebase Console للأخطاء
2. راجع Developer Tools في المتصفح
3. تأكد من اتباع جميع الخطوات بالترتيب

---

**ملاحظة:** هذا الدليل مخصص للإعداد الأولي. يمكن تخصيص الإعدادات حسب احتياجات المؤسسة.


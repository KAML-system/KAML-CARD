// متغيرات عامة
let uploadedPhotoFilename = null;

// تبديل التبويبات
function showTab(tabName) {
    // إخفاء جميع التبويبات
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));
    
    // إظهار التبويب المحدد
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');
    
    // تحميل البيانات حسب التبويب
    if (tabName === 'members') {
        loadMembers();
    }
}

// معالجة رفع الصورة الشخصية
document.getElementById('photo').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // معاينة الصورة
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('photoPreview');
            preview.innerHTML = `<img src="${e.target.result}" style="max-width: 200px; max-height: 200px; border-radius: 8px;">`;
        };
        reader.readAsDataURL(file);
        
        // رفع الصورة للخادم
        uploadPhoto(file);
    }
});

// رفع الصورة للخادم
async function uploadPhoto(file) {
    const formData = new FormData();
    formData.append('photo', file);
    
    try {
        const response = await fetch('/api/upload-photo', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            uploadedPhotoFilename = result.filename;
            showAlert('تم رفع الصورة بنجاح', 'success');
        } else {
            showAlert(result.error, 'error');
        }
    } catch (error) {
        showAlert('خطأ في رفع الصورة: ' + error.message, 'error');
    }
}

// معالجة نموذج إنشاء البطاقة
document.getElementById('cardForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const loading = document.getElementById('generateLoading');
    const result = document.getElementById('generateResult');
    const preview = document.getElementById('cardPreview');
    
    // إظهار التحميل
    loading.classList.add('show');
    result.innerHTML = '';
    preview.innerHTML = '';
    
    // جمع البيانات
    const formData = {
        name_arabic: document.getElementById('nameArabic').value,
        name_english: document.getElementById('nameEnglish').value,
        membership_number: document.getElementById('membershipNumber').value
    };
    
    // إضافة اسم ملف الصورة إذا كانت متوفرة
    if (uploadedPhotoFilename) {
        formData.photo_filename = uploadedPhotoFilename;
    }
    
    try {
        const response = await fetch('/api/generate-card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            result.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            preview.innerHTML = `
                <h4 style="color: #000080; margin-bottom: 15px;">معاينة البطاقة</h4>
                <img src="${data.card_url}" alt="بطاقة العضوية">
                <div style="margin-top: 15px;">
                    <a href="/api/download-card/${formData.membership_number}" 
                       class="btn" style="display: inline-block; text-decoration: none;">
                        <i class="fas fa-download"></i> تحميل البطاقة
                    </a>
                </div>
            `;
        } else {
            result.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
        }
    } catch (error) {
        result.innerHTML = `<div class="alert alert-error">خطأ في إنشاء البطاقة: ${error.message}</div>`;
    } finally {
        loading.classList.remove('show');
    }
});

// معالجة نموذج مسح الباركود
document.getElementById('scanForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const loading = document.getElementById('scanLoading');
    const result = document.getElementById('scanResult');
    const fileInput = document.getElementById('qrImage');
    
    if (!fileInput.files[0]) {
        showAlert('يرجى اختيار صورة', 'error');
        return;
    }
    
    // إظهار التحميل
    loading.classList.add('show');
    result.innerHTML = '';
    
    const formData = new FormData();
    formData.append('qr_image', fileInput.files[0]);
    
    try {
        const response = await fetch('/api/scan-qr', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.is_valid) {
                result.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> ${data.message}
                    </div>
                    <div class="member-info">
                        <h3><i class="fas fa-user"></i> معلومات العضو</h3>
                        <p><strong>الاسم العربي:</strong> ${data.member_data.name_arabic || 'غير متوفر'}</p>
                        <p><strong>الاسم الإنجليزي:</strong> ${data.member_data.name_english || 'غير متوفر'}</p>
                        <p><strong>رقم العضوية:</strong> ${data.member_data.membership_number || 'غير متوفر'}</p>
                        <p><strong>المؤسسة:</strong> ${data.member_data.Organization || 'غير متوفر'}</p>
                    </div>
                `;
            } else {
                result.innerHTML = `
                    <div class="alert alert-error">
                        <i class="fas fa-times-circle"></i> ${data.message}
                    </div>
                `;
            }
        } else {
            result.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
        }
    } catch (error) {
        result.innerHTML = `<div class="alert alert-error">خطأ في مسح الباركود: ${error.message}</div>`;
    } finally {
        loading.classList.remove('show');
    }
});

// تحميل قائمة الأعضاء
async function loadMembers() {
    const loading = document.getElementById('membersLoading');
    const list = document.getElementById('membersList');
    
    loading.classList.add('show');
    list.innerHTML = '';
    
    try {
        const response = await fetch('/api/members');
        const data = await response.json();
        
        if (data.success) {
            let html = '<div class="grid">';
            
            data.members.forEach(member => {
                html += `
                    <div class="member-info">
                        <h3><i class="fas fa-user"></i> ${member.name_arabic}</h3>
                        <p><strong>الاسم الإنجليزي:</strong> ${member.name_english}</p>
                        <p><strong>رقم العضوية:</strong> ${member.membership_number}</p>
                        <div style="margin-top: 15px;">
                            <a href="/api/download-card/${member.membership_number}" 
                               class="btn" style="display: inline-block; text-decoration: none; font-size: 14px; padding: 10px 20px;">
                                <i class="fas fa-download"></i> تحميل البطاقة
                            </a>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            list.innerHTML = html;
        } else {
            list.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
        }
    } catch (error) {
        list.innerHTML = `<div class="alert alert-error">خطأ في تحميل البيانات: ${error.message}</div>`;
    } finally {
        loading.classList.remove('show');
    }
}

// عرض التنبيهات
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = message;
    
    // إضافة التنبيه في أعلى الصفحة
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // إزالة التنبيه بعد 5 ثوانٍ
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// تحديث نص رفع الملف
document.getElementById('photo').addEventListener('change', function(e) {
    const label = document.querySelector('label[for="photo"]');
    if (e.target.files.length > 0) {
        label.innerHTML = `<i class="fas fa-check"></i> تم اختيار: ${e.target.files[0].name}`;
        label.style.background = '#d4edda';
        label.style.color = '#155724';
    }
});

document.getElementById('qrImage').addEventListener('change', function(e) {
    const label = document.querySelector('label[for="qrImage"]');
    if (e.target.files.length > 0) {
        label.innerHTML = `<i class="fas fa-check"></i> تم اختيار: ${e.target.files[0].name}`;
        label.style.background = '#d4edda';
        label.style.color = '#155724';
    }
});

// تحميل قائمة الأعضاء عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // يمكن إضافة أي إعدادات أولية هنا
});


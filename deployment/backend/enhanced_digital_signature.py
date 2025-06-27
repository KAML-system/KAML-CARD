#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import hmac
import secrets
import json
from datetime import datetime, timedelta
import qrcode
from PIL import Image

class EnhancedDigitalSignature:
    def __init__(self, organization_secret="KAML_SECURE_KEY_2024"):
        self.organization_secret = organization_secret
        self.organization_name = "KAML"
        self.organization_full_name = "Kuwait Association for Medical Laboratories"
        
    def generate_secure_serial(self, membership_number, issue_date=None):
        """توليد رقم تسلسلي آمن ومشفر"""
        if issue_date is None:
            issue_date = datetime.now().strftime('%Y%m%d')
        
        # استخدام HMAC للحصول على رقم تسلسلي آمن
        message = f"{membership_number}_{issue_date}_{self.organization_name}"
        signature = hmac.new(
            self.organization_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # أخذ أول 10 أحرف وتحويلها لتنسيق جميل
        serial = signature[:10].upper()
        # تنسيق الرقم التسلسلي: XXXX-XXXX
        formatted_serial = f"{serial[:4]}-{serial[4:8]}-{serial[8:10]}"
        
        return formatted_serial
    
    def generate_organization_signature(self, issue_date=None):
        """توليد توقيع الجمعية الثابت لليوم"""
        if issue_date is None:
            issue_date = datetime.now().strftime('%Y%m%d')
        
        # توقيع ثابت للجمعية لهذا اليوم
        message = f"{self.organization_name}_{issue_date}_DAILY_SIGNATURE"
        signature = hmac.new(
            self.organization_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"KAML-{signature[:8].upper()}"
    
    def generate_member_signature(self, name_english, membership_number, issue_date=None, expiry_date=None):
        """توليد توقيع رقمي فريد لكل عضو"""
        if issue_date is None:
            issue_date = datetime.now().strftime('%Y-%m-%d')
        if expiry_date is None:
            expiry_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')  # سنة واحدة
        
        # إنشاء البيانات الأساسية للتوقيع
        core_data = f"{name_english}|{membership_number}|{issue_date}|{expiry_date}|{self.organization_name}"
        
        # استخدام HMAC للحصول على توقيع آمن
        signature = hmac.new(
            self.organization_secret.encode(),
            core_data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # تنسيق التوقيع: XXXX-XXXX-XXXX
        formatted_signature = f"{signature[:4].upper()}-{signature[4:8].upper()}-{signature[8:12].upper()}"
        
        return formatted_signature
    
    def verify_member_signature(self, name_english, membership_number, stored_signature, issue_date, expiry_date):
        """التحقق من صحة التوقيع الرقمي للعضو"""
        try:
            # إعادة حساب التوقيع المتوقع
            expected_signature = self.generate_member_signature(
                name_english, membership_number, issue_date, expiry_date
            )
            
            # مقارنة التوقيع
            is_valid = hmac.compare_digest(expected_signature, stored_signature)
            
            return is_valid, expected_signature if is_valid else "توقيع غير صحيح"
            
        except Exception as e:
            return False, f"خطأ في التحقق: {str(e)}"
    
    def create_secure_qr_data(self, name_arabic, name_english, membership_number, expiry_years=1):
        """إنشاء بيانات باركود QR آمنة مع التوقيع الرقمي"""
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=365 * expiry_years)
        
        issue_date_str = issue_date.strftime('%Y-%m-%d')
        expiry_date_str = expiry_date.strftime('%Y-%m-%d')
        
        # توليد الرقم التسلسلي الآمن
        secure_serial = self.generate_secure_serial(membership_number, issue_date.strftime('%Y%m%d'))
        
        # توليد التوقيع الرقمي الفريد
        digital_signature = self.generate_member_signature(
            name_english, membership_number, issue_date_str, expiry_date_str
        )
        
        # إنشاء البيانات الكاملة
        qr_data = {
            "name": name_english,
            "name_ar": name_arabic,
            "membership": membership_number,
            "organization": self.organization_name,
            "org_full": self.organization_full_name,
            "issued": issue_date_str,
            "expires": expiry_date_str,
            "serial": secure_serial,
            "signature": digital_signature,
            "version": "2.0"
        }
        
        return qr_data
    
    def generate_secure_qr_code(self, qr_data):
        """توليد باركود QR آمن ومحسن"""
        # تحويل البيانات إلى JSON مضغوط
        qr_content = json.dumps(qr_data, separators=(',', ':'), ensure_ascii=False)
        
        # إنشاء باركود QR بجودة عالية
        qr = qrcode.QRCode(
            version=4,  # حجم أكبر لاستيعاب البيانات الإضافية
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # أعلى مستوى تصحيح خطأ
            box_size=15,  # حجم أكبر للوضوح
            border=4,
        )
        
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # إنشاء الصورة بجودة عالية
        qr_img = qr.make_image(fill_color='black', back_color='white')
        
        return qr_img
    
    def verify_qr_data(self, qr_content):
        """التحقق من صحة بيانات الباركود QR"""
        try:
            # تحليل البيانات
            if isinstance(qr_content, str):
                data = json.loads(qr_content)
            else:
                data = qr_content
            
            # التحقق من وجود الحقول المطلوبة
            required_fields = ['name', 'membership', 'issued', 'expires', 'signature']
            for field in required_fields:
                if field not in data:
                    return False, f"حقل مفقود: {field}"
            
            # التحقق من التوقيع الرقمي
            is_valid, result = self.verify_member_signature(
                data['name'],
                data['membership'],
                data['signature'],
                data['issued'],
                data['expires']
            )
            
            if not is_valid:
                return False, "التوقيع الرقمي غير صحيح - قد تكون البيانات مزورة"
            
            # التحقق من تاريخ الانتهاء
            expiry_date = datetime.strptime(data['expires'], '%Y-%m-%d')
            if expiry_date < datetime.now():
                return False, "البطاقة منتهية الصلاحية"
            
            return True, "البطاقة صحيحة وسارية المفعول"
            
        except json.JSONDecodeError:
            return False, "خطأ في تحليل بيانات الباركود"
        except Exception as e:
            return False, f"خطأ في التحقق: {str(e)}"
    
    def get_security_info(self):
        """الحصول على معلومات الأمان المستخدمة"""
        return {
            "algorithm": "HMAC-SHA256",
            "organization": self.organization_name,
            "security_level": "عالي",
            "features": [
                "رقم تسلسلي مشفر فريد",
                "توقيع رقمي لكل عضو",
                "تاريخ انتهاء صلاحية",
                "حماية ضد التزوير",
                "تحقق فوري من الأصالة"
            ]
        }

def demonstrate_enhanced_security():
    """عرض توضيحي للنظام المحسن"""
    print("=" * 70)
    print("🔒 نظام التوقيع الرقمي المحسن للجمعية الكويتية للمختبرات الطبية")
    print("=" * 70)
    
    # إنشاء النظام
    signature_system = EnhancedDigitalSignature()
    
    # بيانات تجريبية
    test_members = [
        {
            "name_arabic": "أحمد محمد العلي",
            "name_english": "Ahmed Mohammed Al-Ali",
            "membership": "KAML-2024-001"
        },
        {
            "name_arabic": "سارة أحمد الراشد", 
            "name_english": "Sara Ahmad Al-Rashid",
            "membership": "KAML-2024-002"
        },
        {
            "name_arabic": "عمر خالد المنصوري",
            "name_english": "Omar Khalid Al-Mansouri", 
            "membership": "KAML-2024-003"
        }
    ]
    
    print("\n📋 الأعضاء التجريبيون:")
    for i, member in enumerate(test_members, 1):
        print(f"   {i}. {member['name_arabic']} - {member['membership']}")
    
    print("\n" + "=" * 70)
    print("🔢 الأرقام التسلسلية المشفرة")
    print("=" * 70)
    
    for member in test_members:
        serial = signature_system.generate_secure_serial(member['membership'])
        print(f"العضو: {member['name_arabic']}")
        print(f"رقم العضوية: {member['membership']}")
        print(f"الرقم التسلسلي: {serial}")
        print("-" * 50)
    
    print("\n" + "=" * 70)
    print("📝 التواقيع الرقمية الفريدة")
    print("=" * 70)
    
    signatures_data = []
    for member in test_members:
        qr_data = signature_system.create_secure_qr_data(
            member['name_arabic'],
            member['name_english'], 
            member['membership']
        )
        signatures_data.append(qr_data)
        
        print(f"العضو: {member['name_arabic']}")
        print(f"التوقيع الرقمي: {qr_data['signature']}")
        print(f"الرقم التسلسلي: {qr_data['serial']}")
        print(f"تاريخ الإصدار: {qr_data['issued']}")
        print(f"تاريخ الانتهاء: {qr_data['expires']}")
        print("-" * 50)
    
    print("\n" + "=" * 70)
    print("🛡️ اختبار الأمان والتحقق")
    print("=" * 70)
    
    # اختبار التحقق الصحيح
    test_data = signatures_data[0]
    is_valid, message = signature_system.verify_qr_data(test_data)
    print(f"اختبار البيانات الصحيحة:")
    print(f"العضو: {test_data['name_ar']}")
    print(f"النتيجة: {'✅ صحيح' if is_valid else '❌ خطأ'}")
    print(f"الرسالة: {message}")
    
    # اختبار البيانات المزورة
    fake_data = test_data.copy()
    fake_data['name'] = "Fake Name"
    is_fake_valid, fake_message = signature_system.verify_qr_data(fake_data)
    print(f"\nاختبار البيانات المزورة:")
    print(f"البيانات المزورة: {fake_data['name']}")
    print(f"النتيجة: {'✅ صحيح' if is_fake_valid else '❌ خطأ (تم كشف التزوير)'}")
    print(f"الرسالة: {fake_message}")
    
    print("\n" + "=" * 70)
    print("📱 بيانات الباركود QR الكاملة")
    print("=" * 70)
    
    sample_data = signatures_data[0]
    print("مثال على محتوى الباركود QR:")
    for key, value in sample_data.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("🎯 معلومات الأمان")
    print("=" * 70)
    
    security_info = signature_system.get_security_info()
    print(f"خوارزمية التشفير: {security_info['algorithm']}")
    print(f"مستوى الأمان: {security_info['security_level']}")
    print("\nالمميزات الأمنية:")
    for feature in security_info['features']:
        print(f"   ✅ {feature}")
    
    print("\n" + "=" * 70)
    print("🏆 الخلاصة")
    print("=" * 70)
    print("✅ نظام توقيع رقمي متقدم ومحسن")
    print("✅ حماية عالية ضد التزوير والتلاعب")
    print("✅ أرقام تسلسلية مشفرة وفريدة")
    print("✅ تواقيع رقمية فريدة لكل عضو")
    print("✅ تحقق فوري من صحة البطاقة")
    print("✅ تاريخ انتهاء صلاحية للتحكم")
    print("\n🔒 النظام جاهز للاستخدام الآمن!")
    
    return signatures_data

if __name__ == "__main__":
    demonstrate_enhanced_security()


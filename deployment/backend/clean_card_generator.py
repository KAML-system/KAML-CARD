#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime, timedelta
import sys
sys.path.append('/home/ubuntu')
from enhanced_digital_signature import EnhancedDigitalSignature

class CleanCardGenerator:
    def __init__(self, logo_path):
        self.logo_path = logo_path
        self.signature_system = EnhancedDigitalSignature()
        
        # أبعاد البطاقة (حجم بطاقة الائتمان)
        self.card_width = 1012  # 85.6mm * 300 DPI / 25.4
        self.card_height = 638  # 53.98mm * 300 DPI / 25.4
        
        # الألوان
        self.primary_blue = '#2E5BBA'  # أزرق أساسي
        self.light_blue = '#E8F2FF'   # أزرق فاتح للخلفية
        self.white = '#FFFFFF'
        self.dark_gray = '#2C3E50'
        self.light_gray = '#95A5A6'
        self.green = '#27AE60'
        
    def create_clean_card(self, member_data, output_path):
        """إنشاء بطاقة عضوية نظيفة بدون إطارات"""
        
        # إنشاء الصورة الأساسية
        card = Image.new('RGB', (self.card_width, self.card_height), self.white)
        draw = ImageDraw.Draw(card)
        
        # الشريط العلوي الأزرق
        header_height = 160
        draw.rectangle([0, 0, self.card_width, header_height], fill=self.primary_blue)
        
        # تحميل الشعار
        try:
            logo = Image.open(self.logo_path)
            logo_size = 120
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # وضع الشعار في الزاوية اليمنى
            logo_x = self.card_width - logo_size - 20
            logo_y = 20
            card.paste(logo, (logo_x, logo_y), logo if logo.mode == 'RGBA' else None)
        except Exception as e:
            print(f"خطأ في تحميل الشعار: {e}")
        
        # النصوص في الشريط العلوي
        try:
            # خط للعناوين الإنجليزية
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            
            # العنوان الإنجليزي في سطر واحد
            en_title = "Kuwait Association for Medical Laboratories"
            
            # حساب موضع النص
            title_bbox = draw.textbbox((0, 0), en_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            
            # رسم النصوص
            title_x = 30
            draw.text((title_x, 40), en_title, fill=self.white, font=title_font)
            
            # النص العربي
            ar_text = "الجمعية الكويتية للمختبرات الطبية"
            draw.text((title_x, 85), ar_text, fill=self.white, font=subtitle_font)
            
        except Exception as e:
            print(f"خطأ في الخطوط: {e}")
        
        # المنطقة الرئيسية
        main_y = header_height + 20
        
        # الصورة الشخصية (بدون إطار)
        photo_size = 140
        photo_x = 50
        photo_y = main_y + 20
        
        if 'photo' in member_data and member_data['photo'] and os.path.exists(member_data['photo']):
            try:
                photo = Image.open(member_data['photo'])
                photo = photo.resize((photo_size, photo_size), Image.Resampling.LANCZOS)
                
                # قص الصورة لتكون دائرية
                mask = Image.new('L', (photo_size, photo_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([0, 0, photo_size, photo_size], fill=255)
                
                # تطبيق القناع
                photo.putalpha(mask)
                card.paste(photo, (photo_x, photo_y), photo)
                
            except Exception as e:
                print(f"خطأ في معالجة الصورة: {e}")
                # رسم دائرة رمادية كبديل
                draw.ellipse([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size], 
                           fill=self.light_gray, outline=self.primary_blue, width=3)
                
                # أيقونة شخص
                person_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
                draw.text((photo_x + photo_size//2 - 15, photo_y + photo_size//2 - 30), 
                         "👤", fill=self.white, font=person_font)
        else:
            # رسم دائرة رمادية كبديل
            draw.ellipse([photo_x, photo_y, photo_x + photo_size, photo_y + photo_size], 
                       fill=self.light_gray, outline=self.primary_blue, width=3)
        
        # الاسم (بدون إطار) - تحريك 3 سطور لأسفل
        name_x = photo_x + photo_size + 40
        name_y = main_y + 30 + 60  # إضافة 60 بكسل (3 سطور تقريباً)
        
        try:
            # خط الاسم الإنجليزي
            name_en_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            name_ar_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            
            # الاسم الإنجليزي
            name_english = member_data.get('name_english', 'Member Name')
            draw.text((name_x, name_y), name_english, fill=self.primary_blue, font=name_en_font)
            
            # الاسم العربي
            name_arabic = member_data.get('name_arabic', 'اسم العضو')
            draw.text((name_x, name_y + 50), name_arabic, fill=self.dark_gray, font=name_ar_font)
            
        except Exception as e:
            print(f"خطأ في رسم الأسماء: {e}")
        
        # معلومات العضوية
        info_y = photo_y + photo_size + 30
        
        try:
            info_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            
            # رقم العضوية
            membership_number = member_data.get('membership_number', 'KAML-2024-001')
            draw.text((50, info_y), f"Membership No: {membership_number}", fill=self.dark_gray, font=info_font)
            
            # تاريخ الإصدار
            issue_date = datetime.now().strftime('%d/%m/%Y')
            draw.text((50, info_y + 30), f"Issue Date: {issue_date}", fill=self.light_gray, font=info_font)
            
            # تاريخ الانتهاء
            expiry_date = (datetime.now() + timedelta(days=365)).strftime('%d/%m/%Y')
            draw.text((50, info_y + 60), f"Expiry Date: {expiry_date}", fill=self.light_gray, font=info_font)
            
        except Exception as e:
            print(f"خطأ في معلومات العضوية: {e}")
        
        # الباركود QR (بدون إطار) - حجم أكبر وأوضح
        qr_size = 160  # زيادة الحجم من 120 إلى 160
        qr_x = self.card_width - qr_size - 30  # تقليل المسافة من الحافة
        qr_y = main_y + 20  # رفعه قليلاً لأعلى
        
        try:
            # إنشاء بيانات QR مع التوقيع الرقمي
            qr_data = self.signature_system.create_secure_qr_data(
                member_data.get('name_arabic', ''),
                member_data.get('name_english', ''),
                member_data.get('membership_number', ''),
                expiry_years=1
            )
            
            # إنشاء QR code بإعدادات محسنة للوضوح
            qr = qrcode.QRCode(
                version=1, 
                box_size=6,  # زيادة حجم المربعات من 4 إلى 6
                border=2     # زيادة الحدود من 1 إلى 2
            )
            qr.add_data(json.dumps(qr_data, ensure_ascii=False))
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color=self.dark_gray, back_color=self.white)
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            card.paste(qr_img, (qr_x, qr_y))
            
            # نص "Scan for verification"
            scan_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            draw.text((qr_x, qr_y + qr_size + 10), "Scan for verification", 
                     fill=self.light_gray, font=scan_font)
            
        except Exception as e:
            print(f"خطأ في إنشاء QR: {e}")
        
        # نقطة خضراء للعضوية الفعالة
        status_x = 50
        status_y = self.card_height - 40
        draw.ellipse([status_x, status_y, status_x + 15, status_y + 15], fill=self.green)
        
        try:
            status_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            draw.text((status_x + 25, status_y - 2), "Valid Member", fill=self.light_gray, font=status_font)
        except:
            pass
        
        # حفظ البطاقة
        card.save(output_path, 'PNG', quality=95, dpi=(300, 300))
        print(f"تم إنشاء البطاقة النظيفة: {output_path}")
        
        return output_path

def main():
    """اختبار مولد البطاقات النظيف"""
    
    # إنشاء مجلد للتصاميم النظيفة
    output_dir = "/home/ubuntu/clean_designs"
    os.makedirs(output_dir, exist_ok=True)
    
    # بيانات تجريبية
    test_members = [
        {
            "name_arabic": "أحمد محمد العلي",
            "name_english": "Ahmed Mohammed Al-Ali",
            "membership_number": "KAML-2024-001"
        },
        {
            "name_arabic": "فاطمة سالم الأحمد",
            "name_english": "Fatima Salem Al-Ahmad",
            "membership_number": "KAML-2024-002"
        },
        {
            "name_arabic": "عبرار فاضل المويل",
            "name_english": "Abrar Fadhel Almuwail",
            "membership_number": "KAML-2024-018"
        }
    ]
    
    # مسار الشعار
    logo_path = "/home/ubuntu/upload/logo.jpeg"
    
    # إنشاء مولد البطاقات
    generator = CleanCardGenerator(logo_path)
    
    # إنشاء البطاقات
    for i, member in enumerate(test_members, 1):
        output_path = os.path.join(output_dir, f"clean_card_member_{i}.png")
        generator.create_clean_card(member, output_path)
    
    print("تم إنشاء جميع البطاقات النظيفة بنجاح!")

if __name__ == "__main__":
    main()


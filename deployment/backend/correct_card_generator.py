#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import qrcode
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64

class CorrectCardGenerator:
    def __init__(self):
        # أبعاد البطاقة (بحجم بطاقة الائتمان)
        self.card_width = 1012  # 85.6mm * 300 DPI / 25.4
        self.card_height = 638  # 53.98mm * 300 DPI / 25.4
        
        # الألوان حسب التصميم المرفق
        self.colors = {
            'primary_blue': '#1e40af',
            'light_blue': '#60a5fa',
            'white': '#ffffff',
            'orange': '#f59e0b',
            'gold': '#fbbf24',
            'teal': '#14b8a6',
            'green': '#10b981',
            'text_dark': '#1f2937',
            'text_light': '#6b7280',
            'background': '#f8fafc'
        }
        
        # مسار الخطوط
        self.fonts = self._load_fonts()
        
    def _load_fonts(self):
        """تحميل الخطوط المطلوبة"""
        fonts = {}
        try:
            # خطوط مختلفة الأحجام
            fonts['title_large'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
            fonts['title_medium'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            fonts['name_large'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
            fonts['name_medium'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
            fonts['text_large'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
            fonts['text_medium'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
            fonts['text_small'] = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
            
        except Exception as e:
            print(f"تحذير: لم يتم العثور على الخطوط المخصصة، سيتم استخدام الخط الافتراضي: {e}")
            # استخدام الخط الافتراضي
            default_font = ImageFont.load_default()
            fonts = {
                'title_large': default_font,
                'title_medium': default_font,
                'name_large': default_font,
                'name_medium': default_font,
                'text_large': default_font,
                'text_medium': default_font,
                'text_small': default_font,
            }
        
        return fonts
    
    def _generate_digital_signature(self, member_id, issue_date):
        """توليد توقيع رقمي فريد"""
        secret_key = "KAML_SECRET_2024_MEDICAL_LABS"
        data = f"{member_id}_{issue_date}_{secret_key}"
        signature = hashlib.sha256(data.encode()).hexdigest()[:12].upper()
        return signature
    
    def _generate_serial_number(self, member_id, issue_date):
        """توليد رقم تسلسلي مشفر"""
        data = f"{member_id}_{issue_date}_SERIAL"
        serial = hashlib.md5(data.encode()).hexdigest()[:8].upper()
        return serial
    
    def _create_qr_code(self, data):
        """إنشاء باركود QR"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(data, ensure_ascii=False))
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color=self.colors['primary_blue'], back_color='white')
        return qr_img
    
    def _load_and_resize_photo(self, photo_path, size=(200, 250)):
        """تحميل وتغيير حجم الصورة الشخصية"""
        try:
            if photo_path and os.path.exists(photo_path):
                photo = Image.open(photo_path)
                photo = photo.convert('RGB')
                
                # قص الصورة لتكون مربعة
                width, height = photo.size
                min_size = min(width, height)
                left = (width - min_size) // 2
                top = (height - min_size) // 2
                right = left + min_size
                bottom = top + min_size
                photo = photo.crop((left, top, right, bottom))
                
                # تغيير الحجم
                photo = photo.resize(size, Image.Resampling.LANCZOS)
                return photo
            else:
                # إنشاء صورة افتراضية
                photo = Image.new('RGB', size, self.colors['light_blue'])
                draw = ImageDraw.Draw(photo)
                
                # رسم أيقونة شخص
                center_x, center_y = size[0] // 2, size[1] // 2
                
                # رأس
                head_radius = 30
                draw.ellipse([center_x - head_radius, center_y - 60 - head_radius, 
                             center_x + head_radius, center_y - 60 + head_radius], 
                            fill=self.colors['white'])
                
                # جسم
                body_width = 50
                body_height = 60
                draw.ellipse([center_x - body_width, center_y - 30, 
                             center_x + body_width, center_y + body_height], 
                            fill=self.colors['white'])
                
                return photo
        except Exception as e:
            print(f"خطأ في تحميل الصورة: {e}")
            # إنشاء صورة افتراضية في حالة الخطأ
            photo = Image.new('RGB', size, self.colors['light_blue'])
            return photo
    
    def _load_logo(self, logo_path, size=(80, 80)):
        """تحميل الشعار"""
        try:
            if logo_path and os.path.exists(logo_path):
                logo = Image.open(logo_path)
                logo = logo.convert('RGBA')
                logo = logo.resize(size, Image.Resampling.LANCZOS)
                return logo
            else:
                # إنشاء شعار افتراضي
                logo = Image.new('RGBA', size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(logo)
                draw.ellipse([5, 5, size[0]-5, size[1]-5], 
                           fill=self.colors['primary_blue'], outline=self.colors['white'], width=3)
                draw.text((size[0]//2, size[1]//2), "KAML", 
                         fill=self.colors['white'], anchor="mm", font=self.fonts['text_medium'])
                return logo
        except Exception as e:
            print(f"خطأ في تحميل الشعار: {e}")
            # إنشاء شعار افتراضي
            logo = Image.new('RGBA', size, (255, 255, 255, 0))
            return logo
    
    def _draw_rounded_rectangle(self, draw, bbox, radius, fill=None, outline=None, width=1):
        """رسم مستطيل بزوايا مدورة"""
        x1, y1, x2, y2 = bbox
        
        # رسم المستطيل الأساسي
        if fill:
            draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
            draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
            
            # رسم الزوايا المدورة
            draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
            draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
            draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
            draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)
        
        # رسم الحدود
        if outline:
            draw.arc([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=outline, width=width)
            draw.arc([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=outline, width=width)
            draw.arc([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=outline, width=width)
            draw.arc([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=outline, width=width)
            
            draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
            draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
            draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
            draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)
    
    def generate_card(self, arabic_name, english_name, member_id, photo_path=None, logo_path=None):
        """إنشاء بطاقة العضوية حسب التصميم المرفق"""
        
        # إنشاء صورة البطاقة
        card = Image.new('RGB', (self.card_width, self.card_height), self.colors['white'])
        draw = ImageDraw.Draw(card)
        
        # الشريط العلوي الأزرق
        header_height = 120
        draw.rectangle([0, 0, self.card_width, header_height], fill=self.colors['primary_blue'])
        
        # تحميل وإضافة الشعار الصحيح
        new_logo_path = '/home/ubuntu/upload/new_logo.jpeg'
        if os.path.exists(new_logo_path):
            logo = self._load_logo(new_logo_path, (70, 70))
            logo_x = self.card_width - 90
            logo_y = 25
            card.paste(logo, (logo_x, logo_y), logo)
        elif logo_path and os.path.exists(logo_path):
            logo = self._load_logo(logo_path, (70, 70))
            logo_x = self.card_width - 90
            logo_y = 25
            card.paste(logo, (logo_x, logo_y), logo)
        else:
            # إنشاء شعار KAML افتراضي إذا لم يكن متوفراً
            logo_size = (70, 70)
            logo = Image.new('RGBA', logo_size, (255, 255, 255, 0))
            draw_logo = ImageDraw.Draw(logo)
            draw_logo.ellipse([5, 5, logo_size[0]-5, logo_size[1]-5], 
                           fill=self.colors['white'], outline=self.colors['primary_blue'], width=3)
            draw_logo.text((logo_size[0]//2, logo_size[1]//2), "KAML", 
                         fill=self.colors['primary_blue'], anchor="mm", font=self.fonts['text_medium'])
            logo_x = self.card_width - 90
            logo_y = 25
            card.paste(logo, (logo_x, logo_y), logo)
        
        # اسم الجمعية بالإنجليزية (سطر واحد كامل)
        org_name_en = "Kuwait Association for Medical Laboratories"
        org_x = 30
        org_y = 35
        
        draw.text((org_x, org_y), org_name_en, fill=self.colors['white'], font=self.fonts['title_medium'])
        
        # اسم الجمعية بالعربية
        org_arabic = "الجمعية الكويتية للمختبرات الطبية"
        draw.text((org_x, org_y + 40), org_arabic, fill=self.colors['light_blue'], font=self.fonts['text_large'])
        
        # المحتوى الرئيسي
        main_y = header_height + 30
        
        # باركود QR على اليسار (أكبر وأوضح)
        qr_x = 30
        qr_y = main_y + 20
        qr_size = 160  # تكبير الباركود من 120 إلى 160
        
        # إنشاء بيانات الباركود
        issue_date = datetime.now().strftime('%Y/%m/%d')
        expiry_date = (datetime.now() + timedelta(days=365)).strftime('%Y/%m/%d')
        digital_signature = self._generate_digital_signature(member_id, issue_date)
        serial_number = self._generate_serial_number(member_id, issue_date)
        
        qr_data = {
            'name': english_name,
            'arabic_name': arabic_name,
            'member_id': member_id,
            'organization': 'KAML',
            'issue_date': issue_date,
            'expiry_date': expiry_date,
            'digital_signature': digital_signature,
            'serial_number': serial_number
        }
        
        # إنشاء باركود أوضح مع دقة عالية
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,  # تكبير حجم المربعات لوضوح أكثر
            border=2,
        )
        qr.add_data(json.dumps(qr_data, ensure_ascii=False))
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color=self.colors['primary_blue'], back_color='white')
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        card.paste(qr_img, (qr_x, qr_y))
        
        # نص "Scan for verification"
        scan_text = "🔍 Scan for verification"
        draw.text((qr_x, qr_y + qr_size + 10), scan_text, fill=self.colors['text_light'], font=self.fonts['text_small'])
        
        # الاسم ورقم العضوية في منتصف البطاقة تماماً (بدون إطارات)
        center_x = self.card_width // 2
        center_y = (header_height + self.card_height - 60) // 2  # منتصف المساحة المتاحة
        
        # الاسم الإنجليزي في المنتصف (بدون إطار)
        name_en_x = center_x
        name_en_y = center_y - 60
        draw.text((name_en_x, name_en_y), english_name, fill=self.colors['primary_blue'], 
                 font=self.fonts['name_large'], anchor="mm")
        
        # الاسم العربي في المنتصف (بدون إطار)
        name_ar_x = center_x
        name_ar_y = name_en_y + 50
        draw.text((name_ar_x, name_ar_y), arabic_name, fill=self.colors['primary_blue'], 
                 font=self.fonts['name_medium'], anchor="mm")
        
        # رقم العضوية في المنتصف (بدون إطار برتقالي)
        member_id_short = member_id.split('-')[-1] if '-' in member_id else member_id
        member_y = center_y + 20
        
        draw.text((center_x, member_y), member_id_short, 
                 fill=self.colors['orange'], anchor="mm", font=self.fonts['title_large'])
        
        # نص "Membership No:" في المنتصف
        draw.text((center_x, member_y + 30), "Membership No:", 
                 fill=self.colors['text_light'], font=self.fonts['text_medium'], anchor="mm")
        
        # تواريخ الإصدار والانتهاء في المنتصف
        draw.text((center_x, member_y + 50), f"📅 Issue: {issue_date}", 
                 fill=self.colors['teal'], font=self.fonts['text_small'], anchor="mm")
        draw.text((center_x, member_y + 65), f"📅 Expiry: {expiry_date}", 
                 fill=self.colors['teal'], font=self.fonts['text_small'], anchor="mm")
        
        # الصورة الشخصية على اليمين (بدون إطار ذهبي)
        photo = self._load_and_resize_photo(photo_path, (160, 200))
        photo_x = self.card_width - 190
        photo_y = main_y + 20
        
        card.paste(photo, (photo_x, photo_y))
        
        # الشريط الأخضر في الأسفل
        bottom_strip_y = self.card_height - 60
        draw.rectangle([0, bottom_strip_y, self.card_width, self.card_height], fill=self.colors['green'])
        
        # نص "Valid Member" في الشريط الأخضر
        draw.text((30, bottom_strip_y + 20), "✅ 🆔 Valid Member", 
                 fill=self.colors['white'], font=self.fonts['text_large'])
        
        # الرقم التسلسلي والتوقيع في الأسفل
        serial_text = f"📄 Serial: {serial_number} | Signature: {digital_signature}..."
        draw.text((self.card_width - 400, bottom_strip_y + 20), serial_text, 
                 fill=self.colors['white'], font=self.fonts['text_small'])
        
        return card, qr_data

def create_correct_membership_card(arabic_name, english_name, member_id, photo_path=None, logo_path=None, output_dir="cards"):
    """إنشاء بطاقة عضوية حسب التصميم الصحيح"""
    
    # إنشاء مجلد الحفظ إذا لم يكن موجوداً
    os.makedirs(output_dir, exist_ok=True)
    
    # إنشاء مولد البطاقات
    generator = CorrectCardGenerator()
    
    # إنشاء البطاقة
    card_image, qr_data = generator.generate_card(arabic_name, english_name, member_id, photo_path, logo_path)
    
    # حفظ البطاقة
    card_filename = f"correct_card_{member_id.replace('-', '_')}.png"
    card_path = os.path.join(output_dir, card_filename)
    card_image.save(card_path, 'PNG', dpi=(300, 300))
    
    return {
        'success': True,
        'card_path': card_path,
        'card_filename': card_filename,
        'qr_data': qr_data,
        'member_info': {
            'arabic_name': arabic_name,
            'english_name': english_name,
            'member_id': member_id,
            'issue_date': qr_data['issue_date'],
            'expiry_date': qr_data['expiry_date'],
            'digital_signature': qr_data['digital_signature'],
            'serial_number': qr_data['serial_number']
        }
    }

if __name__ == "__main__":
    # مثال للاستخدام
    result = create_correct_membership_card(
        arabic_name="إبرار المويل",
        english_name="abrar Almuwail",
        member_id="KAML-2024-543",
        photo_path=None,
        logo_path="/home/ubuntu/upload/logo.jpeg"
    )
    
    if result['success']:
        print(f"تم إنشاء البطاقة بنجاح: {result['card_path']}")
        print(f"الرقم التسلسلي: {result['member_info']['serial_number']}")
        print(f"التوقيع الرقمي: {result['member_info']['digital_signature']}")
    else:
        print("فشل في إنشاء البطاقة")


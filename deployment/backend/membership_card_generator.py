#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

class MembershipCardGenerator:
    def __init__(self, logo_path="logo.jpeg"):
        self.logo_path = logo_path
        # أبعاد بطاقة الائتمان القياسية (بالبكسل، 300 DPI)
        self.card_width = 1012  # 85.6mm
        self.card_height = 638  # 53.98mm
        
        # الألوان
        self.bg_color = "#87CEEB"  # الأزرق الفاتح
        self.text_color = "#000080"  # الأزرق الداكن
        self.white_color = "#FFFFFF"
        
    def generate_qr_code(self, name_english, membership_number):
        """توليد باركود QR يحتوي على الاسم ورقم العضوية"""
        qr_data = f"Name: {name_english}\nMembership: {membership_number}\nOrganization: KAML"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color='black', back_color='white')
        return qr_img
    
    def load_and_resize_image(self, image_path, size):
        """تحميل وتغيير حجم الصورة"""
        try:
            img = Image.open(image_path)
            img = img.convert('RGBA')
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"خطأ في تحميل الصورة {image_path}: {e}")
            # إنشاء صورة افتراضية
            img = Image.new('RGBA', size, (200, 200, 200, 255))
            draw = ImageDraw.Draw(img)
            draw.text((size[0]//2, size[1]//2), "صورة\nغير متوفرة", 
                     fill=(100, 100, 100, 255), anchor="mm")
            return img
    
    def create_card(self, member_data, output_path):
        """إنشاء بطاقة العضوية"""
        # إنشاء خلفية البطاقة
        card = Image.new('RGB', (self.card_width, self.card_height), self.bg_color)
        draw = ImageDraw.Draw(card)
        
        # إضافة إطار أبيض
        margin = 20
        draw.rectangle([margin, margin, self.card_width-margin, self.card_height-margin], 
                      fill=self.white_color, outline=self.text_color, width=3)
        
        # تحميل الشعار
        logo_size = (120, 120)
        logo = self.load_and_resize_image(self.logo_path, logo_size)
        logo_x = margin + 20
        logo_y = margin + 20
        card.paste(logo, (logo_x, logo_y), logo)
        
        # إضافة اسم المؤسسة
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            name_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            number_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            name_font = ImageFont.load_default()
            number_font = ImageFont.load_default()
        
        # عنوان المؤسسة
        org_title = "الجمعية الكويتية للمختبرات الطبية"
        org_subtitle = "Kuwait Association for Medical Laboratories"
        
        title_x = logo_x + logo_size[0] + 20
        title_y = logo_y + 10
        
        draw.text((title_x, title_y), org_title, fill=self.text_color, font=title_font)
        draw.text((title_x, title_y + 35), org_subtitle, fill=self.text_color, font=subtitle_font)
        draw.text((title_x, title_y + 60), "KAML", fill=self.text_color, font=title_font)
        
        # الصورة الشخصية
        photo_size = (100, 120)
        photo_x = margin + 20
        photo_y = logo_y + logo_size[1] + 30
        
        if 'photo' in member_data and member_data['photo']:
            photo = self.load_and_resize_image(member_data['photo'], photo_size)
        else:
            # صورة افتراضية
            photo = Image.new('RGB', photo_size, (220, 220, 220))
            photo_draw = ImageDraw.Draw(photo)
            photo_draw.text((photo_size[0]//2, photo_size[1]//2), "صورة", 
                           fill=(100, 100, 100), anchor="mm")
        
        card.paste(photo, (photo_x, photo_y))
        
        # معلومات العضو
        info_x = photo_x + photo_size[0] + 30
        info_y = photo_y
        
        # الاسم العربي
        draw.text((info_x, info_y), member_data['name_arabic'], 
                 fill=self.text_color, font=name_font)
        
        # الاسم الإنجليزي
        draw.text((info_x, info_y + 30), member_data['name_english'], 
                 fill=self.text_color, font=name_font)
        
        # رقم العضوية
        draw.text((info_x, info_y + 65), f"رقم العضوية: {member_data['membership_number']}", 
                 fill=self.text_color, font=number_font)
        draw.text((info_x, info_y + 90), f"Member ID: {member_data['membership_number']}", 
                 fill=self.text_color, font=number_font)
        
        # باركود QR
        qr_code = self.generate_qr_code(member_data['name_english'], member_data['membership_number'])
        qr_size = (120, 120)
        qr_code = qr_code.resize(qr_size, Image.Resampling.LANCZOS)
        
        qr_x = self.card_width - qr_size[0] - margin - 20
        qr_y = photo_y + 20
        
        card.paste(qr_code, (qr_x, qr_y))
        
        # حفظ البطاقة
        card.save(output_path, 'PNG', dpi=(300, 300))
        print(f"تم إنشاء البطاقة: {output_path}")
        
        return output_path
    
    def generate_cards_from_json(self, json_file, output_dir="cards"):
        """توليد البطاقات من ملف JSON"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(json_file, 'r', encoding='utf-8') as f:
            members = json.load(f)
        
        generated_cards = []
        for member in members:
            output_file = os.path.join(output_dir, f"card_{member['membership_number']}.png")
            card_path = self.create_card(member, output_file)
            generated_cards.append(card_path)
            
        return generated_cards

if __name__ == "__main__":
    # إنشاء مولد البطاقات
    generator = MembershipCardGenerator("/home/ubuntu/upload/logo.jpeg")
    
    # توليد البطاقات من البيانات التجريبية
    cards = generator.generate_cards_from_json("/home/ubuntu/sample_data.json")
    
    print(f"تم إنشاء {len(cards)} بطاقة بنجاح!")
    for card in cards:
        print(f"- {card}")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cv2
from pyzbar import pyzbar
from PIL import Image
import json
import os

class QRScanner:
    def __init__(self):
        self.members_db = {}
        
    def load_members_database(self, json_file):
        """تحميل قاعدة بيانات الأعضاء"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                members = json.load(f)
                for member in members:
                    self.members_db[member['membership_number']] = member
            print(f"تم تحميل {len(self.members_db)} عضو في قاعدة البيانات")
        except Exception as e:
            print(f"خطأ في تحميل قاعدة البيانات: {e}")
    
    def scan_qr_from_image(self, image_path):
        """مسح باركود QR من صورة"""
        try:
            # قراءة الصورة
            image = cv2.imread(image_path)
            if image is None:
                return None, "لا يمكن قراءة الصورة"
            
            # البحث عن باركود QR في الصورة
            qr_codes = pyzbar.decode(image)
            
            if not qr_codes:
                return None, "لم يتم العثور على باركود QR في الصورة"
            
            # قراءة أول باركود QR
            qr_data = qr_codes[0].data.decode('utf-8')
            return qr_data, "تم قراءة الباركود بنجاح"
            
        except Exception as e:
            return None, f"خطأ في قراءة الباركود: {e}"
    
    def parse_qr_data(self, qr_data):
        """تحليل بيانات باركود QR"""
        try:
            lines = qr_data.strip().split('\n')
            parsed_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed_data[key.strip()] = value.strip()
            
            return parsed_data
        except Exception as e:
            print(f"خطأ في تحليل بيانات QR: {e}")
            return {}
    
    def verify_member(self, qr_data):
        """التحقق من صحة بيانات العضو"""
        parsed_data = self.parse_qr_data(qr_data)
        
        if 'Membership' not in parsed_data:
            return False, "رقم العضوية غير موجود في الباركود", {}
        
        membership_number = parsed_data['Membership']
        
        if membership_number not in self.members_db:
            return False, "رقم العضوية غير مسجل في قاعدة البيانات", parsed_data
        
        member_info = self.members_db[membership_number]
        
        # التحقق من تطابق الاسم
        qr_name = parsed_data.get('Name', '')
        db_name = member_info.get('name_english', '')
        
        if qr_name.lower() != db_name.lower():
            return False, "الاسم في الباركود لا يطابق قاعدة البيانات", parsed_data
        
        return True, "تم التحقق من العضوية بنجاح", {**parsed_data, **member_info}
    
    def scan_and_verify(self, image_path):
        """مسح والتحقق من باركود QR"""
        print(f"مسح الصورة: {image_path}")
        
        # مسح الباركود
        qr_data, scan_message = self.scan_qr_from_image(image_path)
        print(f"نتيجة المسح: {scan_message}")
        
        if qr_data is None:
            return False, scan_message, {}
        
        print(f"بيانات الباركود:\n{qr_data}")
        
        # التحقق من البيانات
        is_valid, verify_message, member_data = self.verify_member(qr_data)
        print(f"نتيجة التحقق: {verify_message}")
        
        if is_valid:
            print("\n=== معلومات العضو ===")
            print(f"الاسم العربي: {member_data.get('name_arabic', 'غير متوفر')}")
            print(f"الاسم الإنجليزي: {member_data.get('name_english', 'غير متوفر')}")
            print(f"رقم العضوية: {member_data.get('membership_number', 'غير متوفر')}")
            print(f"المؤسسة: {member_data.get('Organization', 'غير متوفر')}")
        
        return is_valid, verify_message, member_data

def test_qr_scanner():
    """اختبار نظام QR scanner"""
    scanner = QRScanner()
    
    # تحميل قاعدة بيانات الأعضاء
    scanner.load_members_database("/home/ubuntu/sample_data.json")
    
    # اختبار مسح البطاقات المولدة
    cards_dir = "/home/ubuntu/cards"
    if os.path.exists(cards_dir):
        for card_file in os.listdir(cards_dir):
            if card_file.endswith('.png'):
                card_path = os.path.join(cards_dir, card_file)
                print(f"\n{'='*50}")
                print(f"اختبار البطاقة: {card_file}")
                print(f"{'='*50}")
                
                is_valid, message, data = scanner.scan_and_verify(card_path)
                
                if is_valid:
                    print("✅ البطاقة صحيحة")
                else:
                    print("❌ البطاقة غير صحيحة")
                
                print(f"{'='*50}")

if __name__ == "__main__":
    test_qr_scanner()


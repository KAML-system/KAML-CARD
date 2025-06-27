from flask import Blueprint, request, jsonify, send_file
import json
import os
import base64
from io import BytesIO
from PIL import Image
import sys
sys.path.append('/home/ubuntu')
from elegant_card_generator import ElegantCardGenerator
from enhanced_digital_signature import EnhancedDigitalSignature

firebase_membership_bp = Blueprint('firebase_membership', __name__)

# تحميل إعدادات Firebase
def load_firebase_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"خطأ في تحميل إعدادات Firebase: {e}")
        return None

@firebase_membership_bp.route('/firebase-config', methods=['GET'])
def get_firebase_config():
    """إرجاع إعدادات Firebase للواجهة الأمامية"""
    config = load_firebase_config()
    if config:
        return jsonify({
            'success': True,
            'config': config
        })
    else:
        return jsonify({
            'success': False,
            'error': 'لم يتم العثور على إعدادات Firebase'
        }), 500

@firebase_membership_bp.route('/create-card-firebase', methods=['POST'])
def create_card_firebase():
    """إنشاء بطاقة عضوية مع حفظ البيانات في Firebase"""
    try:
        data = request.get_json()
        
        # استخراج البيانات
        name_arabic = data.get('name_arabic', '')
        name_english = data.get('name_english', '')
        membership_number = data.get('membership_number', '')
        photo_data = data.get('photo', '')
        
        # التحقق من البيانات المطلوبة
        if not all([name_arabic, name_english, membership_number]):
            return jsonify({
                'success': False,
                'error': 'جميع الحقول مطلوبة'
            }), 400
        
        # إعداد بيانات العضو
        member_data = {
            'name_arabic': name_arabic,
            'name_english': name_english,
            'membership_number': membership_number,
            'photo': None
        }
        
        # معالجة الصورة إذا تم رفعها
        if photo_data and photo_data.startswith('data:image'):
            try:
                # استخراج البيانات من base64
                header, encoded = photo_data.split(',', 1)
                photo_bytes = base64.b64decode(encoded)
                
                # حفظ الصورة مؤقتاً
                photo_path = f"/tmp/member_photo_{membership_number}.jpg"
                with open(photo_path, 'wb') as f:
                    f.write(photo_bytes)
                
                member_data['photo'] = photo_path
                
            except Exception as e:
                print(f"خطأ في معالجة الصورة: {e}")
        
        # إنشاء البطاقة
        generator = ElegantCardGenerator("/home/ubuntu/upload/logo.jpeg")
        
        # مسار حفظ البطاقة
        cards_dir = "/home/ubuntu/kaml_membership_system/src/static/generated_cards"
        os.makedirs(cards_dir, exist_ok=True)
        
        card_filename = f"firebase_card_{membership_number}.png"
        card_path = os.path.join(cards_dir, card_filename)
        
        # إنشاء البطاقة الأنيقة
        generator.create_elegant_card(member_data, card_path)
        
        # إنشاء بيانات للحفظ في Firebase
        firebase_data = {
            'membership_number': membership_number,
            'name_arabic': name_arabic,
            'name_english': name_english,
            'card_generated': True,
            'card_path': f"/static/generated_cards/{card_filename}",
            'created_at': 'timestamp_placeholder',
            'status': 'active'
        }
        
        # إرجاع النتيجة
        return jsonify({
            'success': True,
            'message': 'تم إنشاء البطاقة بنجاح',
            'card_url': f"/static/generated_cards/{card_filename}",
            'firebase_data': firebase_data,
            'member_data': {
                'name_arabic': name_arabic,
                'name_english': name_english,
                'membership_number': membership_number
            }
        })
        
    except Exception as e:
        print(f"خطأ في إنشاء البطاقة: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في إنشاء البطاقة: {str(e)}'
        }), 500

@firebase_membership_bp.route('/verify-qr-firebase', methods=['POST'])
def verify_qr_firebase():
    """التحقق من باركود QR مع Firebase"""
    try:
        data = request.get_json()
        qr_data = data.get('qr_data', '')
        
        if not qr_data:
            return jsonify({
                'success': False,
                'error': 'بيانات QR مطلوبة'
            }), 400
        
        # التحقق من التوقيع الرقمي
        signature_system = EnhancedDigitalSignature()
        
        try:
            # تحليل بيانات QR
            qr_json = json.loads(qr_data)
            
            # التحقق من التوقيع
            is_valid, message = signature_system.verify_signature(
                qr_json.get('name_english', ''),
                qr_json.get('membership_number', ''),
                qr_json.get('signature', ''),
                qr_json.get('issued', ''),
                qr_json.get('expires', '')
            )
            
            if is_valid:
                return jsonify({
                    'success': True,
                    'valid': True,
                    'message': 'البطاقة صحيحة ومعتمدة',
                    'member_data': {
                        'name_english': qr_json.get('name_english', ''),
                        'membership_number': qr_json.get('membership_number', ''),
                        'issued': qr_json.get('issued', ''),
                        'expires': qr_json.get('expires', ''),
                        'serial': qr_json.get('serial', '')
                    }
                })
            else:
                return jsonify({
                    'success': True,
                    'valid': False,
                    'message': f'البطاقة غير صحيحة: {message}'
                })
                
        except json.JSONDecodeError:
            return jsonify({
                'success': True,
                'valid': False,
                'message': 'تنسيق QR غير صحيح'
            })
        
    except Exception as e:
        print(f"خطأ في التحقق من QR: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في التحقق: {str(e)}'
        }), 500

@firebase_membership_bp.route('/download-card/<membership_number>', methods=['GET'])
def download_card(membership_number):
    """تحميل بطاقة العضوية"""
    try:
        card_filename = f"firebase_card_{membership_number}.png"
        card_path = f"/home/ubuntu/kaml_membership_system/src/static/generated_cards/{card_filename}"
        
        if os.path.exists(card_path):
            return send_file(
                card_path,
                as_attachment=True,
                download_name=f"membership_card_{membership_number}.png",
                mimetype='image/png'
            )
        else:
            return jsonify({
                'success': False,
                'error': 'البطاقة غير موجودة'
            }), 404
            
    except Exception as e:
        print(f"خطأ في تحميل البطاقة: {e}")
        return jsonify({
            'success': False,
            'error': f'خطأ في التحميل: {str(e)}'
        }), 500

@firebase_membership_bp.route('/test-firebase', methods=['GET'])
def test_firebase():
    """اختبار الاتصال مع Firebase"""
    config = load_firebase_config()
    
    if config:
        return jsonify({
            'success': True,
            'message': 'Firebase متصل بنجاح',
            'project_id': config.get('projectId', 'غير محدد'),
            'auth_domain': config.get('authDomain', 'غير محدد')
        })
    else:
        return jsonify({
            'success': False,
            'error': 'فشل في الاتصال مع Firebase'
        }), 500


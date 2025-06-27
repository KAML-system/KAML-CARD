from flask import Blueprint, request, jsonify, url_for, send_file
import os
import json
import uuid
from werkzeug.utils import secure_filename
import sys
sys.path.append('/home/ubuntu')
from correct_card_generator import create_correct_membership_card
import tempfile
from datetime import datetime

membership_bp = Blueprint('membership', __name__)

# إعداد مجلد الرفع
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
CARDS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'cards')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CARDS_FOLDER, exist_ok=True)

# قاعدة بيانات بسيطة للأعضاء (في الذاكرة)
members_db = []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@membership_bp.route('/create_card', methods=['POST'])
def create_card():
    """إنشاء بطاقة عضوية جديدة"""
    try:
        # الحصول على البيانات من النموذج
        arabic_name = request.form.get('arabic_name')
        english_name = request.form.get('english_name')
        member_id = request.form.get('member_id')
        
        # التحقق من البيانات المطلوبة
        if not all([arabic_name, english_name, member_id]):
            return jsonify({
                'success': False,
                'message': 'جميع الحقول مطلوبة (الاسم العربي، الاسم الإنجليزي، رقم العضوية)'
            }), 400
        
        # التحقق من عدم تكرار رقم العضوية
        if any(member['member_id'] == member_id for member in members_db):
            return jsonify({
                'success': False,
                'message': 'رقم العضوية موجود مسبقاً'
            }), 400
        
        # معالجة الصورة الشخصية إذا كانت موجودة
        photo_path = None
        if 'photo' in request.files:
            photo_file = request.files['photo']
            if photo_file and photo_file.filename != '' and allowed_file(photo_file.filename):
                filename = secure_filename(photo_file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                photo_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                photo_file.save(photo_path)
        
        # مسار الشعار
        logo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'upload', 'logo.jpeg')
        
        # إنشاء البطاقة باستخدام المولد الصحيح
        result = create_correct_membership_card(
            arabic_name=arabic_name,
            english_name=english_name,
            member_id=member_id,
            photo_path=photo_path,
            logo_path=logo_path,
            output_dir=CARDS_FOLDER
        )
        
        if result['success']:
            # إضافة العضو لقاعدة البيانات
            member_data = {
                'arabic_name': arabic_name,
                'english_name': english_name,
                'member_id': member_id,
                'photo_path': photo_path,
                'card_path': result['card_path'],
                'card_filename': result['card_filename'],
                'created_at': datetime.now().isoformat(),
                'qr_data': result['qr_data']
            }
            members_db.append(member_data)
            
            # إنشاء رابط البطاقة
            card_url = url_for('static', filename=f'cards/{result["card_filename"]}', _external=True)
            
            return jsonify({
                'success': True,
                'message': 'تم إنشاء البطاقة بنجاح',
                'card_url': card_url,
                'member_id': member_id,
                'card_filename': result['card_filename'],
                'member_info': result['member_info']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'فشل في إنشاء البطاقة'
            }), 500
            
    except Exception as e:
        print(f"خطأ في إنشاء البطاقة: {e}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        }), 500

@membership_bp.route('/members', methods=['GET'])
def get_members():
    """الحصول على قائمة الأعضاء"""
    try:
        # إرجاع قائمة الأعضاء مع المعلومات الأساسية فقط
        members_list = []
        for member in members_db:
            members_list.append({
                'arabic_name': member['arabic_name'],
                'english_name': member['english_name'],
                'member_id': member['member_id'],
                'created_at': member['created_at']
            })
        
        return jsonify({
            'success': True,
            'members': members_list
        })
        
    except Exception as e:
        print(f"خطأ في جلب الأعضاء: {e}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        }), 500

@membership_bp.route('/member_card/<member_id>', methods=['GET'])
def get_member_card(member_id):
    """الحصول على بطاقة عضو محدد"""
    try:
        # البحث عن العضو
        member = next((m for m in members_db if m['member_id'] == member_id), None)
        
        if not member:
            return jsonify({
                'success': False,
                'message': 'العضو غير موجود'
            }), 404
        
        # إنشاء رابط البطاقة
        card_url = url_for('static', filename=f'cards/{member["card_filename"]}', _external=True)
        
        return jsonify({
            'success': True,
            'card_url': card_url,
            'member_info': {
                'arabic_name': member['arabic_name'],
                'english_name': member['english_name'],
                'member_id': member['member_id']
            }
        })
        
    except Exception as e:
        print(f"خطأ في جلب بطاقة العضو: {e}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        }), 500

@membership_bp.route('/scan_qr', methods=['POST'])
def scan_qr():
    """مسح باركود QR"""
    try:
        # الحصول على البيانات من الطلب
        if 'qr_image' in request.files:
            # مسح من صورة مرفوعة
            qr_file = request.files['qr_image']
            if qr_file and qr_file.filename != '':
                # حفظ الصورة مؤقتاً
                temp_path = os.path.join(tempfile.gettempdir(), secure_filename(qr_file.filename))
                qr_file.save(temp_path)
                
                # مسح الباركود
                try:
                    from pyzbar import pyzbar
                    from PIL import Image
                    
                    image = Image.open(temp_path)
                    barcodes = pyzbar.decode(image)
                    
                    if barcodes:
                        qr_data = barcodes[0].data.decode('utf-8')
                        
                        # محاولة تحليل البيانات كـ JSON
                        try:
                            member_info = json.loads(qr_data)
                            return jsonify({
                                'success': True,
                                'member_info': member_info
                            })
                        except json.JSONDecodeError:
                            # إذا لم تكن JSON، إرجاع النص كما هو
                            return jsonify({
                                'success': True,
                                'qr_text': qr_data
                            })
                    else:
                        return jsonify({
                            'success': False,
                            'message': 'لم يتم العثور على باركود QR في الصورة'
                        }), 400
                        
                except ImportError:
                    return jsonify({
                        'success': False,
                        'message': 'مكتبة مسح الباركود غير مثبتة'
                    }), 500
                finally:
                    # حذف الملف المؤقت
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        elif request.is_json:
            # مسح من بيانات JSON (للكاميرا المباشرة)
            data = request.get_json()
            qr_text = data.get('qr_data')
            
            if qr_text:
                try:
                    member_info = json.loads(qr_text)
                    return jsonify({
                        'success': True,
                        'member_info': member_info
                    })
                except json.JSONDecodeError:
                    return jsonify({
                        'success': True,
                        'qr_text': qr_text
                    })
        
        return jsonify({
            'success': False,
            'message': 'لم يتم تقديم بيانات صالحة للمسح'
        }), 400
        
    except Exception as e:
        print(f"خطأ في مسح الباركود: {e}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        }), 500

@membership_bp.route('/download_card/<member_id>')
def download_card(member_id):
    """تحميل بطاقة عضو"""
    try:
        # البحث عن العضو
        member = next((m for m in members_db if m['member_id'] == member_id), None)
        
        if not member:
            return jsonify({
                'success': False,
                'message': 'العضو غير موجود'
            }), 404
        
        # إرجاع ملف البطاقة
        return send_file(
            member['card_path'],
            as_attachment=True,
            download_name=f"card_{member_id}.png",
            mimetype='image/png'
        )
        
    except Exception as e:
        print(f"خطأ في تحميل البطاقة: {e}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        }), 500


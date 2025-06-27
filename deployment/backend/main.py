import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session, request, jsonify
from src.models.user import db
from src.routes.user import user_bp
from src.routes.membership import membership_bp
from src.routes.firebase_membership import firebase_membership_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SESSION_TYPE'] = 'filesystem'

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(membership_bp, url_prefix='/api')
app.register_blueprint(firebase_membership_bp, url_prefix='/api')

# بيانات تسجيل الدخول (يمكن تغييرها حسب الحاجة)
ADMIN_CREDENTIALS = {
    'admin': 'kaml2024',
    'manager': 'kaml123'
}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True, 'message': 'تم تسجيل الدخول بنجاح'})
    else:
        return jsonify({'success': False, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'تم تسجيل الخروج بنجاح'})

@app.route('/api/check_auth', methods=['GET'])
def check_auth():
    return jsonify({'logged_in': session.get('logged_in', False)})

# Middleware للتحقق من الصلاحيات للعمليات المحمية
@app.before_request
def check_admin_access():
    # المسارات المحمية التي تحتاج تسجيل دخول
    protected_paths = ['/api/create_card', '/api/members']
    
    if request.path in protected_paths:
        if not session.get('logged_in'):
            return jsonify({'error': 'يجب تسجيل الدخول للوصول لهذه الصفحة'}), 401

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

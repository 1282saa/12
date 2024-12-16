from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from SnapsAI import InstagramAPI, convert_post, RAGConverter, ThreadAPI
import os
from dotenv import load_dotenv
import logging
import requests
from datetime import datetime, timedelta
from flask_session import Session


load_dotenv()
thread_api = None

def init_thread_api():
    global thread_api
    thread_api = ThreadAPI()

init_thread_api()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
Session(app)

# MongoDB configuration
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/snaps_db')
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Environment variables
INSTAGRAM_APP_ID = os.getenv('INSTAGRAM_APP_ID')
INSTAGRAM_APP_SECRET = os.getenv('INSTAGRAM_APP_SECRET')
NGROK_URL = os.getenv('NGROK_URL')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/instagram-converter')
def instagram_converter():
    return render_template('index6.html')

@app.route('/content-conversion')
def content_conversion():
    return render_template('content_conversion.html')

@app.route('/content-management')
def content_management():
    return render_template('content_management.html')

@app.route('/statistics')
def statistics():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('access_token'):
        flash('Instagram 계정을 연동해주세요.', 'warning')
        return redirect(url_for('my_page'))
    
    return render_template('statistics.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not email or not password or not confirm_password:
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('register.html', error='모든 필드를 입력해주세요.')

        if password != confirm_password:
            flash('비밀번호가 일치하지 않습니다.', 'error')
            return render_template('register.html', error='비밀번호가 일치하지 않습니다.')

        existing_user = mongo.db.users.find_one({"email": email})
        if existing_user:
            flash('이미 사용 중인 이메일입니다.', 'error')
            return render_template('register.html', error='이미 사용 중인 이메일입니다.')

        hashed_password = generate_password_hash(password)
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "instagram_id": None,
            "access_token": None
        }

        try:
            mongo.db.users.insert_one(new_user)
            flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Error during registration: {str(e)}")
            flash('회원가입 중 오류가 발생했습니다. 다시 시도해주세요.', 'error')
            return render_template('register.html', error='회원가입 중 오류가 발생했습니다. 다시 시도해주세요.')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = mongo.db.users.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            flash('로그인 되었습니다.', 'success')
            return redirect(url_for('my_page'))
        else:
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('로그아웃 되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/my-page')
def my_page():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    instagram_linked = bool(user and user.get('access_token'))
    thread_linked = bool(user and user.get('thread_user_id'))
    return render_template('my_page.html', user=user, instagram_linked=instagram_linked, thread_linked=thread_linked)

@app.route('/instagram-auth')
def instagram_auth():
    if 'user_id' not in session:
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('login'))
    redirect_uri = f"{NGROK_URL}/auth/instagram/callback"
    return redirect(f"https://api.instagram.com/oauth/authorize?client_id={INSTAGRAM_APP_ID}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code")

@app.route('/auth/instagram/callback')
def instagram_callback():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    code = request.args.get('code')
    if not code:
        flash('Instagram authorization failed')
        return redirect(url_for('my_page'))

    redirect_uri = f"{NGROK_URL}/auth/instagram/callback"
    response = requests.post('https://api.instagram.com/oauth/access_token', data={
        'client_id': INSTAGRAM_APP_ID,
        'client_secret': INSTAGRAM_APP_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
        'code': code
    })

    if response.status_code != 200:
        flash('Failed to obtain Instagram access token')
        return redirect(url_for('my_page'))

    data = response.json()
    access_token = data['access_token']
    instagram_user_id = data['user_id']

    try:
        mongo.db.users.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"instagram_id": instagram_user_id, "access_token": access_token}}
        )
        flash('Instagram account successfully linked')
    except Exception as e:
        app.logger.error(f"Error updating user with Instagram data: {str(e)}")
        flash('Error linking Instagram account')

    return redirect(url_for('my_page'))

@app.route('/refresh_instagram_token', methods=['POST'])
def refresh_instagram_token():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('access_token'):
        return jsonify({"error": "Instagram account not linked"}), 400

    try:
        instagram_api = InstagramAPI(str(session['user_id']), mongo.db.client)
        new_token, new_expiry = instagram_api.refresh_token()
        return jsonify({"success": True, "message": "Instagram token refreshed successfully"})
    except Exception as e:
        app.logger.error(f"Error refreshing Instagram token: {str(e)}")
        return jsonify({"error": "Failed to refresh Instagram token. Please relink your account."}), 500

@app.route('/fetch_posts', methods=['POST'])
def fetch_posts():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('access_token'):
        return jsonify({"error": "Instagram account not linked"}), 400

    try:
        instagram_api = InstagramAPI(str(session['user_id']), mongo.db.client)
        media_items = instagram_api.get_user_media()
        formatted_posts = instagram_api.format_posts(media_items)
        
        app.logger.info(f"Fetched {len(formatted_posts)} posts for user {session['user_id']}")
        
        return jsonify({"posts": formatted_posts})
    except Exception as e:
        app.logger.error(f"Error fetching posts: {str(e)}", exc_info=True)
        if "Instagram 연동이 만료되었습니다" in str(e):
            return jsonify({"error": "Instagram 연동이 만료되었습니다. 다시 연동해 주세요."}), 401
        return jsonify({"error": f"Failed to fetch posts: {str(e)}"}), 500


@app.route('/fetch_instagram_stats', methods=['GET'])
def fetch_instagram_stats():
    if 'user_id' not in session:
        return jsonify({"error": "로그인이 필요합니다."}), 401
    
    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('access_token'):
        return jsonify({"error": "Instagram 계정이 연동되어 있지 않습니다."}), 400

    try:
        instagram_api = InstagramAPI(str(session['user_id']), mongo.db.client)
        stats = instagram_api.get_user_statistics(limit=30)
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Error fetching Instagram stats: {str(e)}")
        return jsonify({"error": "통계를 가져오는 데 실패했습니다. 나중에 다시 시도해 주세요."}), 500
    
@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        caption = data.get('caption')
        target_platform = data.get('targetPlatform')
        has_image = data.get('hasImage', False)

        if not caption or not target_platform:
            return jsonify({"error": "Missing required fields"}), 400

        basic_converted_post = convert_post(caption, target_platform, has_image)

        rag_converter = RAGConverter()
        rag_converted_post = rag_converter.generate_enhanced_post(caption, target_platform, has_image)

        return jsonify({
            "basicConvertedPost": basic_converted_post,
            "ragConvertedPost": rag_converted_post
        })
    except Exception as e:
        app.logger.error(f"Error in /convert route: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Thread 계정 연동 라우트
@app.route('/link_thread_account', methods=['POST'])
def link_thread_account():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    thread_user_id = request.json.get('thread_user_id')
    if not thread_user_id:
        return jsonify({"error": "Thread user ID is required"}), 400

    try:
        result = mongo.db.users.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$set": {"thread_user_id": thread_user_id}}
        )
        if result.modified_count > 0:
            return jsonify({"success": True, "message": "Thread account linked successfully"})
        else:
            return jsonify({"error": "No changes were made. User might not exist or Thread account already linked."}), 400
    except Exception as e:
        app.logger.error(f"Error linking Thread account: {str(e)}")
        return jsonify({"error": "Failed to link Thread account"}), 500

@app.route('/check_thread_account', methods=['GET'])
def check_thread_account():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"linked": bool(user.get('thread_user_id'))})

@app.route('/fetch_thread_stats', methods=['GET'])
def fetch_thread_stats():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('thread_user_id'):
        return jsonify({"error": "Thread account not linked"}), 400

    try:
        thread_api = ThreadAPI(user['thread_user_id'])
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        stats = thread_api.get_user_insights(int(start_date.timestamp()), int(end_date.timestamp()))
        return jsonify(stats)
    except Exception as e:
        app.logger.error(f"Error fetching Thread stats: {str(e)}")
        return jsonify({"error": "Failed to fetch statistics. Please try again later."}), 500

@app.route('/fetch_thread_posts', methods=['GET'])
def fetch_thread_posts():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('thread_user_id'):
        return jsonify({"error": "Thread account not linked"}), 400

    try:
        thread_api = ThreadAPI(user['thread_user_id'])
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        threads = thread_api.get_user_threads(since=start_date, until=end_date, limit=10)
        return jsonify(threads)
    except Exception as e:
        app.logger.error(f"Error fetching Thread posts: {str(e)}")
        return jsonify({"error": "Failed to fetch Thread posts. Please try again later."}), 500

@app.route('/upload_to_thread', methods=['POST'])
def upload_to_thread():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user = mongo.db.users.find_one({"_id": ObjectId(session['user_id'])})
    if not user or not user.get('thread_user_id'):
        return jsonify({"error": "Thread account not linked"}), 400

    data = request.json
    content = data.get('content')
    media_type = data.get('media_type', 'TEXT')
    image_url = data.get('image_url')
    video_url = data.get('video_url')

    if not content:
        return jsonify({"error": "Content is required"}), 400

    try:
        thread_api = ThreadAPI()
        result = thread_api.post_thread(
            user_id=user['thread_user_id'],
            content=content,
            media_type=media_type,
            image_url=image_url,
            video_url=video_url
        )
        return jsonify({"success": True, "thread_id": result.get('id')})
    except Exception as e:
        app.logger.error(f"Error uploading to Thread: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if NGROK_URL:
        app.logger.info(f"ngrok URL: {NGROK_URL}")
        app.logger.info(f"Callback URL: {NGROK_URL}/auth/instagram/callback")
        app.logger.info(f"Data Deletion URL: {NGROK_URL}/data-deletion")
        app.logger.info(f"Privacy Policy URL: {NGROK_URL}/privacy-policy")

    app.run(host='0.0.0.0', port=5000, debug=True)
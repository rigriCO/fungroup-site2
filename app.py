from flask import Flask, render_template, request, abort, redirect, url_for, session, flash
import sqlite3
import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'fungroup_secret_key_change_me'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Полный словарь локализации для интерфейса (RU, EN, UK)
TRANSLATIONS = {
    'ru': {
        'logo': 'FunGr😊up',
        'messages': 'СООБЩЕНИЯ',
        'create_ad': '+ СОЗДАТЬ АНКЕТУ',
        'login': 'Войти',
        'register': 'Регистрация',
        'settings': 'Настройки',
        'logout': 'Выйти',
        'search_games': 'Поиск игр:',
        'search_placeholder': 'Впишите игру...',
        'recent_search': 'Последний поиск:',
        'alphabet_title': 'Игры в алфавитном порядке',
        'stats_users': 'Зарегистрировано аккаунтов',
        'stats_popular': 'Самая популярная игра по поискам',
        'stats_reg_date': 'Дата регистрации вашего аккаунта',
        'no_games': 'Игры не найдены.',
        'publish_ad_btn': 'Выложить своё объявление',
        'search_desc': 'Поиск по описанию 🔍',
        'search_desc_placeholder': 'Введите ключевые слова...',
        'search_desc_hint': 'поиск работает по ключевым словам',
        'no_profiles': 'Пока нет созданных объявлений для этой игры. Станьте первыми, кто выложит своё объявление!',
        'category': 'Категория игры',
        'create_ad_title': 'Меню создания объявления игрока',
        'your_game': 'Ваша игра:',
        'select_game': 'Выберите игру...',
        'about_self': 'Информация о себе:',
        'about_placeholder': 'Введите статистику, прайм-тайм, ранг и кого ищете...',
        'photo_label': 'Фото вашего профиля / достижений (необязательно):',
        'photo_drag': 'Сюда надо перетащить фото или нажмите для выбора',
        'add_photo': '+ Добавить фото',
        'publish_btn': 'Опубликовать объявление',
        'account_settings': 'Настройки аккаунта',
        'site_theme': 'Тема оформления сайта:',
        'light_theme': 'Светлая тема ☀️',
        'dark_theme': 'Темная тема 🌙',
        'sound_notifs': 'Включить звуковые уведомления о сообщениях',
        'save_settings': 'Сохранить настройки',
        'profile_status': 'Статус профиля',
        'active': 'Активен ✅',
        'back_to_main': '← На главную',
        # Раздел сообщений
        'messages_title': 'Сообщения',
        'search_chats': 'Поиск по никнеймам...',
        'no_chats': 'У вас пока нет активных чатов.',
        'chat_with': 'Чат с пользователем:',
        'type_message': 'Введите текст ...',
        'send': 'Отправить',
        'empty_chat_select': 'Выберите чат слева, чтобы начать общение, или найдите пользователя по никнейму.',
    },
    'en': {
        'logo': 'FunGr😊up',
        'messages': 'MESSAGES',
        'create_ad': '+ CREATE PROFILE',
        'login': 'Login',
        'register': 'Register',
        'settings': 'Settings',
        'logout': 'Logout',
        'search_games': 'Search games:',
        'search_placeholder': 'Type a game...',
        'recent_search': 'Recent searches:',
        'alphabet_title': 'Games in alphabetical order',
        'stats_users': 'Registered accounts',
        'stats_popular': 'Most popular game by searches',
        'stats_reg_date': 'Account registration date',
        'no_games': 'No games found.',
        'publish_ad_btn': 'Create listing',
        'search_desc': 'Search by description 🔍',
        'search_desc_placeholder': 'Type keywords...',
        'search_desc_hint': 'search works by keywords',
        'no_profiles': 'No listings created yet for this game. Be the first to create one!',
        'category': 'Game category',
        'create_ad_title': 'Player Listing Creation Menu',
        'your_game': 'Your game:',
        'select_game': 'Select game...',
        'about_self': 'About yourself:',
        'about_placeholder': 'Enter stats, prime time, rank and who you are looking for...',
        'photo_label': 'Profile / achievement photo (optional):',
        'photo_drag': 'Drag photo here or click to select',
        'add_photo': '+ Add photo',
        'publish_btn': 'Publish listing',
        'account_settings': 'Account Settings',
        'site_theme': 'Site theme:',
        'light_theme': 'Light theme ☀️',
        'dark_theme': 'Dark theme 🌙',
        'sound_notifs': 'Enable sound notifications for messages',
        'save_settings': 'Save settings',
        'profile_status': 'Profile status',
        'active': 'Active ✅',
        'back_to_main': '← Main page',
        # Раздел сообщений
        'messages_title': 'Messages',
        'search_chats': 'Search by usernames...',
        'no_chats': 'You have no active chats yet.',
        'chat_with': 'Chat with user:',
        'type_message': 'Type a message ...',
        'send': 'Send',
        'empty_chat_select': 'Select a chat on the left to start messaging, or search for a user by username.',
    },
    'uk': {
        'logo': 'FunGr😊up',
        'messages': 'ПОВІДОМЛЕННЯ',
        'create_ad': '+ СТВОРИТИ АНКЕТУ',
        'login': 'Увійти',
        'register': 'Реєстрація',
        'settings': 'Налаштування',
        'logout': 'Вийти',
        'search_games': 'Пошук ігор:',
        'search_placeholder': 'Введіть гру...',
        'recent_search': 'Останній пошук:',
        'alphabet_title': 'Ігри в алфавітному порядку',
        'stats_users': 'Зареєстровано акаунтів',
        'stats_popular': 'Найпопулярніша гра за пошуками',
        'stats_reg_date': 'Дата реєстрації вашого акаунта',
        'no_games': 'Ігор не знайдено.',
        'publish_ad_btn': 'Створити оголошення',
        'search_desc': 'Пошук за описом 🔍',
        'search_desc_placeholder': 'Введіть ключові слова...',
        'search_desc_hint': 'пошук працює за ключовими словами',
        'no_profiles': 'Поки немає створених оголошень для цієї гри. Станьте першими, хто опублікує оголошення!',
        'category': 'Категорія гри',
        'create_ad_title': 'Меню створення оголошення гравця',
        'your_game': 'Ваша гра:',
        'select_game': 'Виберіть гру...',
        'about_self': 'Інформація про себе:',
        'about_placeholder': 'Введіть статистику, прайм-тайм, ранг та кого шукаєте...',
        'photo_label': 'Фото вашого профілю / досягнень (необов’язково):',
        'photo_drag': 'Сюди треба перетягнути фото або натисніть для вибору',
        'add_photo': '+ Додати фото',
        'publish_btn': 'Опублікувати оголошення',
        'account_settings': 'Налаштування акаунта',
        'site_theme': 'Тема оформлення сайту:',
        'light_theme': 'Світла тема ☀️',
        'dark_theme': 'Темна тема 🌙',
        'sound_notifs': 'Увімкнути звукові сповіщення про повідомлення',
        'save_settings': 'Зберегти налаштування',
        'profile_status': 'Статус профілю',
        'active': 'Активний ✅',
        'back_to_main': '← На головну',
        # Раздел сообщений
        'messages_title': 'Повідомлення',
        'search_chats': 'Пошук за нікнеймами...',
        'no_chats': 'У вас поки немає активних чатів.',
        'chat_with': 'Чат з користувачем:',
        'type_message': 'Введіть текст ...',
        'send': 'Надіслати',
        'empty_chat_select': 'Виберіть чат ліворуч, щоб почати спілкування, або знайдіть користувача за нікнеймом.',
    }
}

@app.context_processor
def inject_lang():
    lang = session.get('lang', 'ru')
    if lang not in TRANSLATIONS:
        lang = 'ru'
    return {
        't': TRANSLATIONS[lang],
        'current_lang': lang
    }

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['ru', 'en', 'uk']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

def get_db_connection():
    conn = sqlite3.connect('fungroup.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('fungroup.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            letter TEXT NOT NULL,
            icon_url TEXT,
            search_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            reg_date TEXT NOT NULL,
            is_online INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            username TEXT NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 TEXT NOT NULL,
            user2 TEXT NOT NULL,
            last_message_time TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            sender TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM games')
    if cursor.fetchone()[0] == 0:
        games_data = [
            ('Apex Legends', 'apex-legends', 'A', '/static/images/apex.png'),
            ('Among Us', 'among-us', 'A', '/static/images/amongus.png'),
            ('Brawl Stars', 'brawl-stars', 'B', '/static/images/brawlstars.png'),
            ('Battlefield', 'battlefield', 'B', '/static/images/battlefield.png'),
            ('Counter-Strike 2', 'cs2', 'C', '/static/images/cs2.png'),
            ('Call of Duty', 'cod', 'C', '/static/images/cod.png'),
            ('Dota 2', 'dota-2', 'D', '/static/images/dota2.png'),
            ('Dead by Daylight', 'dbd', 'D', '/static/images/dbd.png'),
            ('EA Sports FC', 'ea-fc', 'E', '/static/images/eafc.png'),
            ('Escape from Tarkov', 'tarkov', 'E', '/static/images/tarkov.png'),
            ('Fortnite', 'fortnite', 'F', '/static/images/fortnite.png'),
            ('Garry\'s Mod', 'garrys-mod', 'G', '/static/images/gmod.png'),
            ('Genshin Impact', 'genshin', 'G', '/static/images/genshin.png'),
            ('Lethal Company', 'lethal-company', 'L', '/static/images/lethal.png'),
            ('Roblox', 'roblox', 'R', '/static/images/roblox.png'),
            ('Soul Knight', 'soul-knight', 'S', '/static/images/soulknight.png'),
            ('Standoff 2', 'standoff-2', 'S', '/static/images/standoff2.png'),
            ('Terraria', 'terraria', 'T', '/static/images/terraria.png')
        ]
        cursor.executemany('INSERT INTO games (name, slug, letter, icon_url, search_count) VALUES (?, ?, ?, ?, 0)', games_data)
        
    conn.commit()
    conn.close()

def send_bot_welcome(username):
    conn = get_db_connection()
    bot_name = "FunGroup bot"
    chat = conn.execute('SELECT * FROM chats WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)', 
                        (username, bot_name, bot_name, username)).fetchone()
    
    now = datetime.datetime.now().strftime('%H:%M')
    full_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
    
    if not chat:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chats (user1, user2, last_message_time) VALUES (?, ?, ?)', 
                       (username, bot_name, full_time))
        chat_id = cursor.lastrowid
        conn.commit()
    else:
        chat_id = chat['id']
        
    welcome_text = "Привет! Добро пожаловать на FunGr😊up! 🎉 Пожалуйста, будь аккуратен в интернете: не сообщай никому свои пароли, личные данные и будь бдителен при общении с незнакомцами."
    conn.execute('INSERT INTO messages (chat_id, sender, text, timestamp) VALUES (?, ?, ?, ?)',
                 (chat_id, bot_name, welcome_text, now))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        games = conn.execute('SELECT * FROM games WHERE name LIKE ? ORDER BY name', (f'%{search_query}%',)).fetchall()
        for g in games:
            conn.execute('UPDATE games SET search_count = search_count + 1 WHERE id = ?', (g['id'],))
        conn.commit()
    else:
        games = conn.execute('SELECT * FROM games ORDER BY name').fetchall()
    
    grouped_games = {}
    for game in games:
        let = game['letter'].upper()
        if let not in grouped_games:
            grouped_games[let] = []
        grouped_games[let].append(game)
        
    total_users_row = conn.execute('SELECT COUNT(*) as cnt FROM users').fetchone()
    total_users = total_users_row['cnt'] if total_users_row else 0
    
    top_game_row = conn.execute('SELECT name FROM games ORDER BY search_count DESC, id ASC LIMIT 1').fetchone()
    popular_game_name = top_game_row['name'] if top_game_row and top_game_row['name'] else 'Пока нет запросов'
    
    stats = {
        'total_users': total_users,
        'popular_game': popular_game_name,
        'user_reg_date': session.get('user_reg_date', 'Не авторизован')
    }
    
    recent_games = conn.execute('SELECT * FROM games ORDER BY search_count DESC LIMIT 3').fetchall()
    conn.close()
    
    current_theme = session.get('theme', 'light')
    return render_template('index.html', grouped_games=grouped_games, stats=stats, recent_games=recent_games, search_query=search_query, theme=current_theme)

@app.route('/game/<slug>')
def game_profiles(slug):
    conn = get_db_connection()
    game = conn.execute('SELECT * FROM games WHERE slug = ?', (slug,)).fetchone()
    if game is None:
        abort(404)
        
    search_query = request.args.get('q', '').strip()
    if search_query:
        profiles = conn.execute('SELECT * FROM profiles WHERE game_id = ? AND description LIKE ?', (game['id'], f'%{search_query}%')).fetchall()
    else:
        profiles = conn.execute('SELECT * FROM profiles WHERE game_id = ?', (game['id'],)).fetchall()
        
    conn.close()
    current_theme = session.get('theme', 'light')
    return render_template('game_profile.html', game=game, profiles=profiles, search_query=search_query, theme=current_theme)

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if request.method == 'POST':
        game_id = request.form.get('game_id')
        description = request.form.get('description', '').strip()
        
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                upload_folder = app.config['UPLOAD_FOLDER']
                
                # Создаем папку с абсолютным путем, если её нет
                os.makedirs(upload_folder, exist_ok=True)
                
                try:
                    file.save(os.path.join(upload_folder, filename))
                    image_path = f'/static/uploads/{filename}'
                except Exception as e:
                    print(f"Ошибка сохранения файла: {e}")
        
        if description and game_id:
            try:
                conn.execute('''
                    INSERT INTO profiles (game_id, username, description, image_path)
                    VALUES (?, ?, ?, ?)
                ''', (game_id, username, description, image_path))
                conn.commit()
                conn.close()
                flash('Объявление успешно создано!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Ошибка базы данных: {e}")
                flash('Произошла ошибка при сохранении в базу данных.', 'error')
        else:
            flash('Заполните информацию о себе и выберите игру!', 'error')
            
    games = conn.execute('SELECT * FROM games ORDER BY name').fetchall()
    conn.close()
    current_theme = session.get('theme', 'light')
    return render_template('create_profile.html', games=games, theme=current_theme)

@app.route('/start_chat/<username>')
def start_chat(username):
    current_user = session.get('username')
    if not current_user:
        return redirect(url_for('login'))
        
    if current_user == username:
        flash('Вы не можете написать самому себе!', 'error')
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    chat = conn.execute('''
        SELECT * FROM chats 
        WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)
    ''', (current_user, username, username, current_user)).fetchone()
    
    if chat:
        chat_id = chat['id']
    else:
        full_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chats (user1, user2, last_message_time) VALUES (?, ?, ?)',
                       (current_user, username, full_time))
        chat_id = cursor.lastrowid
        conn.commit()
        
    conn.close()
    return redirect(url_for('messages_page', chat_id=chat_id))

@app.route('/messages')
def messages_page():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    user_search = request.args.get('user_search', '')
    
    if user_search:
        chats = conn.execute('''
            SELECT * FROM chats 
            WHERE (user1 = ? AND user2 LIKE ?) OR (user2 = ? AND user1 LIKE ?)
            ORDER BY last_message_time DESC
        ''', (username, f'%{user_search}%', username, f'%{user_search}%')).fetchall()
    else:
        chats = conn.execute('''
            SELECT * FROM chats 
            WHERE user1 = ? OR user2 = ?
            ORDER BY last_message_time DESC
        ''', (username, username)).fetchall()
        
    formatted_chats = []
    for chat in chats:
        partner = chat['user2'] if chat['user1'] == username else chat['user1']
        partner_obj = conn.execute('SELECT * FROM users WHERE username = ?', (partner,)).fetchone()
        is_online = partner_obj['is_online'] if partner_obj else (1 if partner == "FunGroup bot" else 0)
        
        formatted_chats.append({
            'id': chat['id'],
            'partner': partner,
            'is_online': is_online,
            'last_time': chat['last_message_time']
        })
        
    active_chat_id = request.args.get('chat_id', type=int)
    active_messages = []
    active_partner = None
    
    if active_chat_id:
        chat_check = conn.execute('SELECT * FROM chats WHERE id = ? AND (user1 = ? OR user2 = ?)', 
                                  (active_chat_id, username, username)).fetchone()
        if chat_check:
            active_partner = chat_check['user2'] if chat_check['user1'] == username else chat_check['user1']
            active_messages = conn.execute('SELECT * FROM messages WHERE chat_id = ? ORDER BY id ASC', (active_chat_id,)).fetchall()
            
    conn.close()
    current_theme = session.get('theme', 'light')
    return render_template('messages.html', 
                           chats=formatted_chats, 
                           active_chat_id=active_chat_id, 
                           active_messages=active_messages, 
                           active_partner=active_partner,
                           theme=current_theme,
                           user_search=user_search)

@app.route('/send_message/<int:chat_id>', methods=['POST'])
def send_message(chat_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
        
    text = request.form.get('text', '').strip()
    if text:
        now_time = datetime.datetime.now().strftime('%H:%M')
        full_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (chat_id, sender, text, timestamp) VALUES (?, ?, ?, ?)',
                     (chat_id, username, text, now_time))
        conn.execute('UPDATE chats SET last_message_time = ? WHERE id = ?', (full_time, chat_id))
        conn.commit()
        conn.close()
        
    return redirect(url_for('messages_page', chat_id=chat_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Пароли не совпадают! Повторите ввод.', 'error')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            conn.close()
            flash('Этот никнейм уже занят! Выберите другой, чтобы зарегистрироваться.', 'error')
            return redirect(url_for('register'))
        
        reg_date = datetime.datetime.now().strftime('%d.%m.%Y')
        conn.execute('INSERT INTO users (username, password, reg_date, is_online) VALUES (?, ?, ?, 1)',
                     (username, password, reg_date))
        conn.commit()
        conn.close()
        
        send_bot_welcome(username)
        session['username'] = username
        session['user_reg_date'] = reg_date
        
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and user['password'] == password:
            conn.execute('UPDATE users SET is_online = 1 WHERE username = ?', (username,))
            conn.commit()
            conn.close()
            
            session['username'] = user['username']
            session['user_reg_date'] = user['reg_date']
            return redirect(url_for('index'))
        else:
            conn.close()
            flash('Неверный никнейм или пароль!', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = session.get('username')
    if username:
        conn = get_db_connection()
        conn.execute('UPDATE users SET is_online = 0 WHERE username = ?', (username,))
        conn.commit()
        conn.close()
        
    session.pop('username', None)
    session.pop('user_reg_date', None)
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        session['theme'] = request.form.get('theme', 'light')
        session['notifications'] = 'notifs' in request.form
        return redirect(url_for('settings'))
    
    current_theme = session.get('theme', 'light')
    notifications = session.get('notifications', True)
    return render_template('settings.html', theme=current_theme, notifications=notifications)

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)

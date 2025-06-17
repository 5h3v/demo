from flask import Flask, request, jsonify, session, render_template, make_response
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'a-very-secure-random-key-2025'  # Уникальный ключ

# Database connection
def get_db():
    conn = sqlite3.connect('cargo.db')
    conn.row_factory = sqlite3.Row
    conn.text_factory = str  # Убедиться, что строки возвращаются как UTF-8
    return conn

# Initialize database
def init_db():
    with open('cargo_shipments.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = get_db()
    conn.executescript(sql)
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    resp = make_response(render_template('register.html'))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/register')
def register_page():
    resp = make_response(render_template('register.html'))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/login')
def login_page():
    resp = make_response(render_template('login.html'))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/shipments')
def shipments_page():
    resp = make_response(render_template('shipments.html'))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/new_shipment')
def new_shipment_page():
    resp = make_response(render_template('new_shipment.html'))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/admin')
def admin_page():
    resp = make_response(render_template('admin.html'))
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/api/register', methods=['POST'])
def register():
    data = request.form
    login = data.get('login', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()

    if len(login) < 3:
        return jsonify({'success': False, 'message': 'Логин должен содержать минимум 3 символа'})
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Пароль должен содержать минимум 6 символов'})
    if not re.match(r'^[А-Яа-я\s]+$', full_name):
        return jsonify({'success': False, 'message': 'ФИО должно содержать только кириллицу и пробелы'})
    if not re.match(r'^\+7\(\d{3}\)-\d{3}-\d{2}-\d{2}$', phone):
        return jsonify({'success': False, 'message': 'Неверный формат телефона'})
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return jsonify({'success': False, 'message': 'Неверный формат email'})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE login = ? OR email = ?", (login, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Логин или email уже занят'})

    try:
        cursor.execute(
            "INSERT INTO users (login, password, full_name, phone, email) VALUES (?, ?, ?, ?, ?)",
            (login, password, full_name, phone, email)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Регистрация успешна'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Ошибка регистрации: {str(e)}'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.form
    login = data.get('login', '').strip()
    password = data.get('password', '')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE login = ?", (login,))
    user = cursor.fetchone()
    conn.close()

    if user and user['password'] == password:
        session['user_id'] = user['id']
        # Установка is_admin только для login 'admin' и password 'gruzovik2024'
        session['is_admin'] = (login == 'admin' and password == 'gruzovik2024')
        return jsonify({'success': True, 'message': 'Авторизация успешна', 'data': {'is_admin': session['is_admin']}})
    return jsonify({'success': False, 'message': 'Неверный логин или пароль'})

@app.route('/api/create_shipment', methods=['POST'])
def create_shipment():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'})

    data = request.form
    shipment_date = data.get('shipment_date')
    cargo_weight = data.get('cargo_weight', '').strip()
    cargo_type = data.get('cargo_type', '').strip()
    origin_address = data.get('origin_address', '').strip()
    destination_address = data.get('destination_address', '').strip()

    if not shipment_date or not datetime.strptime(shipment_date, '%Y-%m-%dT%H:%M'):
        return jsonify({'success': False, 'message': 'Неверный формат даты и времени'})
    if not cargo_weight or not float(cargo_weight) > 0:
        return jsonify({'success': False, 'message': 'Укажите вес груза'})
    if not cargo_type:
        return jsonify({'success': False, 'message': 'Укажите тип груза'})
    if not origin_address:
        return jsonify({'success': False, 'message': 'Укажите адрес отправления'})
    if not destination_address:
        return jsonify({'success': False, 'message': 'Укажите адрес доставки'})

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO cargo_shipments (user_id, shipment_date, cargo_weight, cargo_type, origin_address, destination_address) VALUES (?, ?, ?, ?, ?, ?)",
            (session['user_id'], shipment_date, cargo_weight, cargo_type, origin_address, destination_address)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Заявка на перевозку создана'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Ошибка создания заявки: {str(e)}'})

@app.route('/api/get_shipments', methods=['GET'])
def get_shipments():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Требуется авторизация'})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, shipment_date, cargo_weight, cargo_type, origin_address, destination_address, status "
        "FROM cargo_shipments WHERE user_id = ?",
        (session['user_id'],)
    )
    shipments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'message': 'Заявки получены', 'data': shipments})

@app.route('/api/get_all_shipments', methods=['GET'])
def get_all_shipments():
    if 'is_admin' not in session or not session['is_admin']:
        return jsonify({'success': False, 'message': 'Доступ запрещён'})
    print(f"Session: {session}")  # Отладочный вывод

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT c.id, c.shipment_date, c.cargo_weight, c.cargo_type, c.origin_address, c.destination_address, c.status, u.full_name "
            "FROM cargo_shipments c JOIN users u ON c.user_id = u.id"
        )
        shipments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'success': True, 'message': 'Заявки получены', 'data': shipments})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Ошибка запроса: {str(e)}'})

@app.route('/api/update_shipment_status', methods=['POST'])
def update_shipment_status():
    if 'is_admin' not in session or not session['is_admin']:
        return jsonify({'success': False, 'message': 'Доступ запрещён'})

    data = request.form
    shipment_id = data.get('shipment_id')
    status = data.get('status')

    if status not in ['pending', 'in_transit', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'message': 'Неверный статус'})

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE cargo_shipments SET status = ? WHERE id = ?",
            (status, shipment_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Статус обновлён'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': f'Ошибка обновления статуса: {str(e)}'})

if __name__ == '__main__':
    import os
    if not os.path.exists('cargo.db'):
        init_db()
    app.run(debug=True)
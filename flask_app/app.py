from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Модели
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(100), nullable=False)

class PC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Создание таблицы пользователей
with app.app_context():
    db.create_all()

# Страница входа
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Успешный вход!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Неверный логин или пароль', 'error')
    return render_template('login.html')

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        if password == confirm_password:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password, first_name=first_name, last_name=last_name)
            db.session.add(new_user)
            db.session.commit()
            flash('Вы успешно зарегистрированы!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Пароли не совпадают', 'error')
    return render_template('register.html')

# Страница восстановления пароля
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Здесь нужно реализовать отправку письма с инструкцией по смене пароля
            flash('Письмо с инструкцией по смене пароля отправлено на Вашу почту.', 'success')
        else:
            flash('Пользователь с таким email не найден.', 'error')
    return render_template('forgot_password.html')

# Страница смены пароля
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if request.method == 'POST':
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Пароль успешно изменен!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Пароли не совпадают', 'error')
        return render_template('change_password.html', user=user)
    else:
        return redirect(url_for('login'))

# Главная страница
@app.route('/')
@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

# Страница профиля
@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('login'))

# Страница сотрудников
@app.route('/employees')
def employees():
    if 'user_id' in session:
        employees = Employee.query.all()
        return render_template('employees.html', employees=employees)
    else:
        return redirect(url_for('login'))

# Добавление сотрудника
@app.route('/employees/add', methods=['POST'])
def add_employee():
    if 'user_id' in session:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        position = request.form.get('position')

        new_employee = Employee(first_name=first_name, last_name=last_name, position=position)
        db.session.add(new_employee)
        db.session.commit()

        flash('Сотрудник добавлен', 'success')
        return redirect(url_for('employees'))
    else:
        return redirect(url_for('login'))

# Изменение сотрудника
@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if 'user_id' in session:
        employee = Employee.query.get_or_404(employee_id)

        if request.method == 'POST':
            employee.first_name = request.form.get('first_name')
            employee.last_name = request.form.get('last_name')
            employee.position = request.form.get('position')
            db.session.commit()
            flash('Сотрудник обновлен', 'success')
            return redirect(url_for('employees'))

        return render_template('edit_employee.html', employee=employee)
    else:
        return redirect(url_for('login'))

# Удаление сотрудника
@app.route('/employees/<int:employee_id>/delete', methods=['POST'])
def delete_employee(employee_id):
    if 'user_id' in session:
        employee = Employee.query.get_or_404(employee_id)
        db.session.delete(employee)
        db.session.commit()
        flash('Сотрудник удален', 'success')
        return redirect(url_for('employees'))
    else:
        return redirect(url_for('login'))

@app.route('/pcs', methods=['GET', 'POST'])
def pcs():
    if request.method == 'POST':
        name = request.form['name']
        new_pc = PC(name=name)
        db.session.add(new_pc)
        db.session.commit()
        flash('ПК добавлен', 'success')
        return redirect(url_for('pcs'))
    pcs = PC.query.all()
    employees = User.query.all()
    return render_template('pcs.html', pcs=pcs, employees=employees)

@app.route('/assign_pc/<int:pc_id>', methods=['POST'])
def assign_pc(pc_id):
    pc = PC.query.get_or_404(pc_id)
    employee_id = int(request.form['employee_id'])
    employee = User.query.get_or_404(employee_id)
    pc.user = employee
    db.session.commit()
    flash('ПК присвоен сотруднику', 'success')
    return redirect(url_for('pcs'))

# Выход из системы
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login'))

# Проверка аутентификации
def is_authenticated():
    return 'user_id' in session

# Декоратор для проверки аутентификации
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if is_authenticated():
            return func(*args, **kwargs)
        else:
            flash('Авторизация требуется', 'error')
            return redirect(url_for('login'))
    return wrapper

# Применение декоратора к необходимым страницам
# (кроме login, register, forgot_password)
app.add_url_rule('/home', 'home', home, methods=['GET'])
app.add_url_rule('/profile', 'profile', profile, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
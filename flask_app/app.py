from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модели
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(100), nullable=False)

class PC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='pcs')

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
            login_user(user)
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
@login_required
def change_password():
    user = current_user
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

# Главная страница
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# Страница профиля
@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)

# Страница сотрудников
@app.route('/employees')
@login_required
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

# Добавление сотрудника
@app.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    position = request.form.get('position')

    new_employee = Employee(first_name=first_name, last_name=last_name, position=position)
    db.session.add(new_employee)
    db.session.commit()

    flash('Сотрудник добавлен', 'success')
    return redirect(url_for('employees'))

# Изменение сотрудника
@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        employee.first_name = request.form.get('first_name')
        employee.last_name = request.form.get('last_name')
        employee.position = request.form.get('position')
        db.session.commit()
        flash('Сотрудник обновлен', 'success')
        return redirect(url_for('employees'))

    return render_template('edit_employee.html', employee=employee)

# Удаление сотрудника
@app.route('/employees/<int:employee_id>/delete', methods=['POST'])
@login_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    flash('Сотрудник удален', 'success')
    return redirect(url_for('employees'))

@app.route('/pcs', methods=['GET', 'POST'])
@login_required
def pcs():
    pcs = PC.query.all()
    employees = Employee.query.all()
    if request.method == 'POST':
        name = request.form['name']
        new_pc = PC(name=name)
        db.session.add(new_pc)
        db.session.commit()
        return redirect(url_for('pcs'))
    return render_template('pcs.html', pcs=pcs, employees=employees)

@app.route('/assign_pc/<int:pc_id>', methods=['POST'])
@login_required
def assign_pc(pc_id):
    pc = PC.query.get_or_404(pc_id)
    employee_id = request.form.get('employee_id')
    if employee_id:
        employee = Employee.query.get_or_404(employee_id)
        pc.user = employee
        db.session.commit()
    else:
        pc.user = None
        db.session.commit()
    return redirect(url_for('pcs'))

# Выход из системы
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('login'))

# Загрузка пользователя по ID для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    app.run(debug=True)
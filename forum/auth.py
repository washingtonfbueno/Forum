from distutils.command import check
from flask import render_template, Blueprint, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

from random import randint
from flask_login import login_user, login_required, logout_user, current_user

from forum import forumdb
auth = Blueprint('auth', __name__)
db = forumdb.ForumDatabase('forum')

@auth.route('/')
def index(): 
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('forum.index', page=1))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        requirements = {'d': 6, 'l': 1, 'u': 1, 's': 0, 'len': 8}  #digits, lowercase letters, uppercase letters, special characters, length

        if [*db.cursor.execute("SELECT * FROM users WHERE login = (?)", (login,))]:
            flash('Login already being used.', 'error')
        elif not 6 <= len(login) <= 20:
            flash('Login must have length between 6 to 20 characters.', 'error')
        elif not login.isalnum():
            flash('Login should not have special characters.', 'error')
        elif password != confirmpassword:
            flash('Both passwords should be equal.', 'error')
        elif not validPassword(password, requirements):
            flash(f'''Password should match the requirements of having at least: 
            {requirements['d']} digits,
            {requirements['l']} lowercase letters,
            {requirements['u']} uppercase letters,
            {requirements['s']} special characters and
            length >= {requirements['len']}.''', 'error')
        else:
            flash('Account created sucessfully.', 'success')
            db.cursor.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, ?)", ('User'+str(randint(10000, 99999)), url_for('static', filename='default_user.png'), login, generate_password_hash(password, 'sha256')))
            db.connection.commit()
        return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():    
    if current_user.is_authenticated:
        return redirect(url_for('forum.index', page=1))

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        db.cursor.execute("SELECT * FROM users WHERE login = ?", (login,))
        result = db.cursor.fetchone()
        user = forumdb.User(*result) if result else None
        if not user:
            flash('Invalid login,', 'error')
        elif not check_password_hash(user.password, password):
            flash('Invalid password,', 'error')
        else:
            flash('Logged in succesfully,', 'success')
            login_user(user, remember=True)
        return render_template('auth/message.html')
    
    return render_template('auth/login.html')


def validPassword(password, r):
    if len(password) >= r['len']:
        p = [0, 0, 0, 0] 
        for ch in password:
            if ch.isdigit():
                p[0] += 1
            elif ch.islower():
                p[1] += 1
            elif ch.isupper():
                p[2] += 1
            else:
                p[3] += 1
        if all([p[0] >= r['d'], p[1] >= r['l'], p[2] >= r['u'], p[3] >= r['s']]):
            return True
        return False
    return False


@auth.route('/logout')
@login_required
def logout():  
    logout_user()  
    flash('Logged out.', 'success')
    return redirect(url_for('auth.login'))
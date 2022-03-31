from flask import render_template, Blueprint, request, redirect, url_for
from flask_login import current_user, login_required
from forum import forumdb

forum = Blueprint('forum', __name__)
db = forumdb.ForumDatabase('forum')

@forum.route('/')
def base():
    return redirect(url_for('forum.index', page=1))

@forum.route('/<int:page>')
def index(page):
    db.cursor.execute("""SELECT threads.thread_id, users.name, threads.thread_subject, threads.thread_posts
                        FROM threads
                        JOIN users
                            ON threads.user_id = users.user_id 
                        ORDER BY threads.thread_last_time DESC
                        LIMIT 5 OFFSET (?)""", (page*5-5,))

    threads = db.cursor.fetchall()

    if threads:
        db.cursor.execute("SELECT COUNT(thread_id) FROM threads")
        count_threads = db.cursor.fetchone()
        pages = int(count_threads[0] / 5) + int(count_threads[0] % 5 > 0)
    else:
        pages = 1

    return render_template('index.html', threads=threads, pages=pages, page=page)

@forum.route('/new_thread', methods=['POST', 'GET'])
@login_required
def new_thread():
    if request.method == 'POST':
        thread_subject = request.form['thread_subject']
        thread_text = request.form['thread_text']
        db.cursor.execute("INSERT INTO threads VALUES (NULL, ?, ?, ?, DATETIME('now', 'localtime'))", (current_user.user_id, thread_subject, 0))
        db.cursor.execute("SELECT thread_id FROM threads WHERE user_id = (?) ORDER BY thread_id DESC", (current_user.user_id,))
        thread_id = db.cursor.fetchone()[0]
        create_post(thread_id, thread_text)

        return redirect(url_for('forum.index', page=1))
        
    return render_template('newthread.html')

@forum.route('/thread/<thread_id>/<int:page>', methods=['POST', 'GET'])
def thread(thread_id, page):
    db.cursor.execute("""SELECT threads.thread_id, threads.thread_subject, threads.thread_posts
                        FROM threads 
                        WHERE thread_id = (?)""", (thread_id,))

    thread = db.cursor.fetchone()

    db.cursor.execute("""SELECT posts.post_id, posts.post_text, posts.post_time, users.name, users.avatar_url, users.user_id
                        FROM posts
                        JOIN users
                            ON posts.user_id = users.user_id
                            WHERE thread_id = (?)
                            ORDER BY post_id
                            LIMIT 5 OFFSET (?)""", (thread_id, page*5-5))

    posts = db.cursor.fetchall()

    if posts:
        pages = int(thread[2] / 5) + int(thread[2] % 5 > 0)
    else:
        pages = 1

    return render_template('thread.html', thread=thread, posts=posts, pages=pages, page=page)

@forum.route('/makepost/<thread_id>', methods=['POST'])
@login_required
def make_post(thread_id):
    post_text=request.form['post_text']
    create_post(thread_id, post_text)

    return redirect(url_for('forum.thread', thread_id=thread_id, page=1))

def create_post(thread_id, post_text):
    db.cursor.execute("INSERT INTO posts VALUES (NULL, ?, ?, ?, DATETIME('now', 'localtime'))", (current_user.user_id, thread_id, post_text))
    db.cursor.execute("UPDATE threads SET thread_posts = thread_posts + 1, thread_last_time = DATETIME('now', 'localtime') WHERE thread_id = (?)", (thread_id,))
    db.connection.commit()

@forum.route('/my_threads/<int:page>')
@login_required
def my_threads(page):
    db.cursor.execute("""SELECT thread_id, thread_subject, thread_posts FROM threads
                        WHERE user_id = (?)
                        ORDER BY thread_id DESC
                        LIMIT 10 OFFSET (?)""", (current_user.user_id, page*10-10))

    threads = db.cursor.fetchall()
    if threads:
        db.cursor.execute("SELECT COUNT(thread_id) FROM threads WHERE user_id = (?)", (current_user.user_id,))
        count_threads = db.cursor.fetchone()
        pages = int(count_threads[0] / 10) + int(count_threads[0] % 10 > 0)
    else:
        pages = 1

    return render_template('mythreads.html', threads=threads, page=page, pages=pages)

@forum.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == 'POST':
        name = request.form['name']
        avatar_url = request.form['avatar_url']
        if not avatar_url:
            db.cursor.execute("UPDATE users SET name = (?), avatar_url = (?) WHERE user_id = (?)", (name, current_user.avatar_url, current_user.user_id))
        else:
            db.cursor.execute("UPDATE users SET name = (?), avatar_url = (?) WHERE user_id = (?)", (name, avatar_url, current_user.user_id))
        db.connection.commit()

        return redirect(url_for('forum.profile'))
    return render_template('profile.html', user_id=current_user.user_id, name=current_user.name, avatar_url=current_user.avatar_url)

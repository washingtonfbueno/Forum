
def create_app():
    from flask import Flask, flash, render_template
    from .forum import forum
    from .auth import auth
    from flask_login import LoginManager
    from forum import forumdb
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "rivao123"
    limiter = Limiter(app, key_func=get_remote_address)
    limiter.limit("1/minute", methods=["POST"])(forum)
    limiter.limit("10/minute", methods=["POST"])(auth)

    app.register_blueprint(forum, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")

    db = forumdb.ForumDatabase('forum')

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        flash('Limit of requests exceeded,', 'error')
        return render_template("auth/message.html")

    @login_manager.user_loader
    def load_user(user_id):
        db.cursor.execute("SELECT * FROM users WHERE user_id = (?)", (user_id,))
        result = db.cursor.fetchone()
        return forumdb.User(*result)

    return app
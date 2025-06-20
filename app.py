from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, BlogPost, User
from flask_ckeditor import CKEditorField
from wtforms import TextAreaField
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Admin Views
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    @login_required
    def index(self):
        return self.render('admin/admin_home.html')

class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    form_overrides = {
        'content': CKEditorField
    }

# Setup Flask-Admin
admin = Admin(app, name='MyCMS', index_view=MyAdminIndexView(), template_mode='bootstrap3')
admin.add_view(SecureModelView(BlogPost, db.session))

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    with db.session() as session:
        return session.get(User, int(user_id))

# Public Blog Home
@app.route('/')
def home():
    posts = BlogPost.query.order_by(BlogPost.date_created.desc()).all()
    return render_template('home.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/admin')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    error = None
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']

        if not check_password_hash(current_user.password, old_password):
            error = "❌ Incorrect current password."
        else:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('change_password.html', error=error)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash('admin', method='pbkdf2:sha256')
            new_user = User(username='admin', password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()

    app.run(debug=True)



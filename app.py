from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user, login_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import StringField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email
import os


class Base(DeclarativeBase):
    pass


# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Configuration
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
csrf = CSRFProtect(app)
bootstrap = Bootstrap5(app)
db.init_app(app)


# User model with flask-login support
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    family_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(unique=True, nullable=False)
    confirm: Mapped[bool] = mapped_column(nullable=False)


# User registration form
class Makeaccount(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Ex. John"})
    family_name = StringField('Family Name', validators=[DataRequired()], render_kw={"placeholder": "Ex. Smith"})
    email = EmailField('Email', validators=[DataRequired()], render_kw={"placeholder": "Ex. johnsmith1998@gmail.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your Password"})
    confirm = BooleanField('I have read and agree to terms of use and Privacy Statement.')


# User login form
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "Ex. johnsmith1998@gmail.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your Password"})


# Create tables if not already created
with app.app_context():
    db.create_all()


# Load user by ID for flask-login
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Home route
@app.route('/')
def home():  # put application's code here
    return render_template('index.html', logged=current_user)


# Creating an account route
@app.route('/join', methods=['GET', 'POST'])
def join():
    form = Makeaccount()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("User already exists with this email.", "danger")
            return redirect(url_for('join'))
        else:
            new_user = User()
            new_user.name = request.form['name']
            new_user.family_name = request.form['family_name']
            new_user.email = request.form['email']
            new_user.password = request.form['password']
            new_user.confirm = request.form['confirm']
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for("profile", id=new_user.id))
    return render_template('join.html', form=form)






# User login route
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('profile', id=user.id))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('sign_in.html', form=form)


# User profile route
@app.route('/profile/<int:id>', methods=['GET'])
def profile(id):
    user = User.query.get_or_404(id)
    return f'<h1>Welcome, {user.name} {user.family_name}</h1>'


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

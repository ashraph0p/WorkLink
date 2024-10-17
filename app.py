from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, logout_user, login_user, UserMixin
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
from forms import Makeaccount, LoginForm, Step1, Step2, Step3, Start
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import os


class Base(DeclarativeBase):
    pass


# Initialize Flask app and database
db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URI', 'sqlite:///project.db')
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
    onboarding: Mapped[bool] = mapped_column(nullable=True)
    details = relationship('Details', back_populates='user', uselist=False)


# Onboarding options model
class Details(db.Model):
    __tablename__ = 'details'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=True)
    account_type: Mapped[int] = mapped_column(nullable=True)
    specialization: Mapped[str] = mapped_column(nullable=True)
    job_title: Mapped[str] = mapped_column(nullable=True)
    biography: Mapped[str] = mapped_column(nullable=True)
    skills: Mapped[str] = mapped_column(nullable=True)
    referral: Mapped[int] = mapped_column(nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='details')


# Create tables if not already created
with app.app_context():
    db.create_all()


# Load user by ID for flask-login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# Home route
@app.route('/')
def home():  # put application's code here
    form = Start()
    return render_template('index.html', logged=current_user, form=form)


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
            confirm_bool = bool(form.confirm.data)
            new_user = User()
            new_user.name = request.form['name']
            new_user.family_name = request.form['family_name']
            new_user.email = request.form['email']
            new_user.password = request.form['password']
            new_user.confirm = confirm_bool
            new_user.onboarding = False
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        return redirect(url_for("onboarding", id=new_user.id))
    return render_template('join.html', form=form, logged=current_user)


# User login route
@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('onboarding', id=user.id))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('sign_in.html', form=form, logged=current_user)


# User onboarding route
@app.route('/onboarding/<int:id>', methods=['GET', 'POST'])
@login_required
def onboarding(id):
    user = User.query.get_or_404(id)
    form = Step1()
    form2 = Step2()
    form3 = Step3()
    if current_user.onboarding:
        return redirect(url_for("profile", id=current_user.id))
    if form.validate_on_submit():
        return render_template('onboarding.html', user=user, logged=current_user, form=form2, img='step2.svg')
    elif form2.validate_on_submit():
        return render_template('onboarding.html', user=user, logged=current_user, form=form3, img="step3.svg")
    elif form3.validate_on_submit():
        new_details = Details()
        new_details.username = form.username.data
        new_details.account_type = form.account_type.data
        new_details.specialization = form2.specifics.data
        new_details.job_title = form2.job_title.data
        new_details.biography = form2.biography.data
        new_details.skills = form2.skills.data
        new_details.referral = form3.referral.data
        new_details.user_id = current_user.id
        current_user.onboarding = True
        db.session.add(new_details)
        db.session.commit()
        return render_template('onboarding.html', user=user, logged=current_user, img="finish.svg", form=form)

    return render_template('onboarding.html', user=user, logged=current_user, form=form, img='step1.svg')


# User control panel route
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    return render_template('profile.html', user=user, logged=current_user)


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()

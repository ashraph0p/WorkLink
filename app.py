from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, current_user, logout_user, login_user
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import StringField, EmailField, PasswordField, BooleanField, RadioField, SelectField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Email
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


# Onboarding options model
class Details(db.Model):
    __tablename__ = 'details'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False)
    account_type: Mapped[int] = mapped_column(nullable=False)


# User registration form
class Makeaccount(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Ex. John"})
    family_name = StringField('Family Name', validators=[DataRequired()], render_kw={"placeholder": "Ex. Smith"})
    email = EmailField('Email', validators=[DataRequired()], render_kw={"placeholder": "Ex. johnsmith1998@gmail.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your Password"})
    confirm = BooleanField('I have read and agree to Terms of Service and Privacy Statement.',
                           validators=[DataRequired()])


# User login form
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "Ex. johnsmith1998@gmail.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your Password"})
    button = SubmitField('Log In')


# Step 1 Onboarding Form
class Step1(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Ex. johnsmith08"})
    account_type = RadioField('Account type', choices=[
        ('1', 'Freelancer (Services Seller / Project Implementer)'),
        ('2', 'Project Owner (Services Buyer)'),
        ('3', 'Company (Remote Hiring of Freelancers)')],
                              validators=[DataRequired()])
    button = SubmitField('Next')


# Step 2 Onboarding Form
class Step2(FlaskForm):
    specifics = SelectField('Specialization', choices=[
        ('translate', 'Translate'),
        ('web_design', 'Web design'),
        ('web_development', 'Web development'),
        ('illustrator', 'Illustrator'),
        ('article_writing', 'Article Writing'),
        ('graphic_design', 'Graphic Design'),
        ('logo_design', 'Logo Design')
    ])
    job_title = SelectField('Job Title', validators=[DataRequired()], choices=[('mobile_app', 'Mobile app'),
                                                                               ('web_site', 'Web site'),
                                                                               ('content_management_systems',
                                                                                'Content management systems'),
                                                                               ('other', 'Other')])
    biography = CKEditorField('Biography', validators=[DataRequired()])
    skills = SelectField('Skills', validators=[DataRequired()], choices=[
        ('translate', 'Translate'),
        ('web_design', 'Web design'),
        ('web_development', 'Web development'),
        ('illustrator', 'Illustrator'),
        ('article_writing', 'Article Writing'),
        ('graphic_design', 'Graphic Design'),
        ('logo_design', 'Logo Design')
    ])
    button = SubmitField('Next')


# Step 3 Onboarding Form
class Step3(FlaskForm):
    referral = RadioField('How do you know Worklink?', choices=[
        ('1', 'Search engine'),
        ('2', 'Social media'),
        ('3', 'Article on the internet'),
        ('4', 'Other')],
                              validators=[DataRequired()])
    button = SubmitField('Next')


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
            confirm_bool = bool(form.confirm.data)
            new_user = User()
            new_user.name = request.form['name']
            new_user.family_name = request.form['family_name']
            new_user.email = request.form['email']
            new_user.password = request.form['password']
            new_user.confirm = confirm_bool
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for("profile", id=new_user.id))
    return render_template('join.html', form=form, logged=current_user)


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
    return render_template('sign_in.html', form=form, logged=current_user)


# User profile route
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    form = Step1()
    form2 = Step2()
    form3 = Step3()
    if form.validate_on_submit():
        return render_template('profile.html', user=user, logged=current_user, form=form2, img='step2.svg')
    elif form2.validate_on_submit():
        return render_template('profile.html', user=user, logged=current_user, form=form3, img="step3.svg")
    elif form3.validate_on_submit():
        # Temporary will fix later
        return render_template('profile.html', user=user, logged=current_user, img="finish.svg", form=form)

    return render_template('profile.html', user=user, logged=current_user, form=form, img='step1.svg')


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()

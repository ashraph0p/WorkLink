import os

from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_required, current_user, logout_user, login_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from forms import Makeaccount, LoginForm, Step1, Step2, Step3ProjectOwner, Step3Freelance, Start


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
# app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///project.db'
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

    # Profile and onboarding details
    username: Mapped[str] = mapped_column(nullable=True)
    account_type: Mapped[int] = mapped_column(nullable=True)
    specialization: Mapped[str] = mapped_column(nullable=True)
    job_title: Mapped[str] = mapped_column(nullable=True)
    biography: Mapped[str] = mapped_column(nullable=True)
    skills: Mapped[str] = mapped_column(nullable=True)
    referral: Mapped[int] = mapped_column(nullable=True)



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

    # Initialize the form objects
    form = Step1()  # Step 1 form (Account Type and Username)
    form2 = Step2()  # Step 2 form (Profile Details)
    form3_project_owner = Step3ProjectOwner()  # Step 3 for Project Owners
    form3_freelancer = Step3Freelance()  # Step 3 for Freelancers

    # finalize details addition
    def finish():
        user.username = session.get('username')
        user.account_type = session.get('account_type')
        user.specialization = session.get('specialization')
        user.job_title = session.get('job_title')
        user.biography = session.get('biography')
        user.skills = session.get('skills')
        return finalize_onboarding(user)

    # Check if onboarding is already completed
    if current_user.onboarding:
        return redirect(url_for("control_panel", id=current_user.id))

    # Initialize session to track onboarding progress
    if 'step' not in session:
        session['step'] = 1  # Start with Step 1

    # Step 1: Choose Account Type & Set Username
    if session['step'] == 1:
        if form.validate_on_submit():
            # Store data from step 1 in session
            session['username'] = form.username.data
            session['account_type'] = form.account_type.data
            session['step'] = 2  # Move to step 2
            return redirect(url_for('onboarding', id=user.id))  # Redirect to keep it smooth
        return render_template('onboarding.html', user=user, logged=current_user, form=form, img='step1.svg')

    # Step 2: Add Profile Details
    elif session['step'] == 2:
        if form2.validate_on_submit():
            # Store form2 data in session
            session['specialization'] = form2.specifics.data
            session['job_title'] = form2.job_title.data
            session['biography'] = form2.biography.data
            session['skills'] = form2.skills.data

            # Retrieve account type to move to the correct next step
            if session.get('account_type') == '2':  # Project Owner
                session['step'] = 3  # Move to step 3 (Project Owner)
            elif session.get('account_type') == '1':  # Freelancer
                session['step'] = 4  # Move to step 3 (Freelancer)
            return redirect(url_for('onboarding', id=user.id))
        return render_template('onboarding.html', user=user, logged=current_user, form=form2, img='step2.svg')

    # Step 3: Project Owner
    elif session['step'] == 3:
        if form3_project_owner.validate_on_submit():
            user.referral = form3_project_owner.referral.data
            finish()
            return redirect(url_for("control_panel", id=current_user.id))
        return render_template('onboarding.html', user=user, logged=current_user, form=form3_project_owner,
                               img='step3_project_owner.svg')

    # Step 3: Freelancer
    elif session['step'] == 4:
        if form3_freelancer.validate_on_submit():
            finish()
            return redirect(url_for("control_panel", id=current_user.id))
        return render_template('onboarding.html', user=user, logged=current_user, form=form3_freelancer,
                               img='step3_project_owner.svg')

    # Default case if session tracking fails
    return redirect(url_for('onboarding', id=user.id))


# Helper function to finalize onboarding
def finalize_onboarding(user):
    user.onboarding = True
    db.session.commit()
    # Clear only the onboarding-related session data
    session.pop('step', None)
    session.pop('username', None)
    session.pop('account_type', None)
    session.pop('specialization', None)
    session.pop('job_title', None)
    session.pop('biography', None)
    session.pop('skills', None)

# User control panel route
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def control_panel(id):
    user = User.query.get_or_404(id)
    return render_template('control_panel.html', user=user, logged=current_user)


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()

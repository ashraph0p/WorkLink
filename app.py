from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from wtforms import StringField, EmailField, PasswordField, BooleanField
from wtforms.validators import DataRequired
import os


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
csrf = CSRFProtect(app)
bootstrap = Bootstrap5(app)
db.init_app(app)


class CreateUser(db.Model):
    __tablename__ = 'create_user'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    family_name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    confirm: Mapped[bool] = mapped_column(nullable=True)  # Set nullable=True if it can be None


class Makeaccount(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={"placeholder": "Ex. John"})
    family_name = StringField('Family Name', validators=[DataRequired()], render_kw={"placeholder": "Ex. Smith"})
    email = EmailField('Email', validators=[DataRequired()], render_kw={"placeholder": "Ex. johnsmith1998@gmail.com"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your Password"})
    confirm = BooleanField('I have read and agree to terms of use and Privacy Statement')


with app.app_context():
    db.create_all()


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')


@app.route('/join', methods=['GET', 'POST'])
def join():
    form = Makeaccount()
    if form.validate_on_submit():
        with app.app_context():
            new_user = CreateUser(name=form.name.data,
                                  family_name=form.family_name.data,
                                  email=form.email.data,
                                  password=form.password.data,
                                  confirm=form.confirm.data)
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for("profile", id=new_user.id))

    return render_template('join.html', form=form)


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_up():
    return render_template('sign_in.html')


@app.route('/profile/<int:id>', methods=['GET'])
def profile(id):
    user = CreateUser.query.get_or_404(id)
    return f'<h1>Welcome, {user.name} {user.family_name}</h1>'


if __name__ == '__main__':
    app.run(debug=True)

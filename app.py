from crypt import methods

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]


class Makeaccount(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    family_name = StringField('family_name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


app.config['SECRET_KEY'] = os.urandom(12)
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)


@app.route('/', methods=['GET'])
def home():  # put application's code here
    return render_template('index.html')


@app.route('/join', methods=['GET, POST'])
def join():
    form = Makeaccount()
    return render_template('join.html', form=form)

@app.route('/sign-in', methods=['GET'])
def sign_up():
    return '<h1>W.I.P</h1>'

@app.route('/profile/idplacementhere', methods=['GET'])
def profile():
    return '<h1>W.I.P</h1>'

if __name__ == '__main__':
    app.run(debug=True)

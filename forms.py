from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import (StringField, EmailField, PasswordField, BooleanField, RadioField, SelectField, FileField,
                     DateField, URLField, SelectMultipleField)
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Email, URL, Optional
from flask_wtf.file import FileAllowed, FileRequired


# User registration form
class Start(FlaskForm):
    project = StringField(render_kw={'placeholder': "Enter The Title Of Project You Want To Implement."})
    start = SubmitField('Start Now')


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
    specifics =     SelectField('Specialization', choices=[
        ('Translate', 'Translate'),
        ('Web Design', 'Web design'),
        ('Web Development', 'Web development'),
        ('Illustrator', 'Illustrator'),
        ('Article Writing', 'Article Writing'),
        ('Graphic Design', 'Graphic Design'),
        ('Logo Design', 'Logo Design')
    ])
    job_title = SelectField('Job Title', validators=[DataRequired()], choices=[('mobile_app', 'Mobile app'),
                                                                               ('web_site', 'Web site'),
                                                                               ('content_management_systems',
                                                                                'Content management systems'),
                                                                               ('other', 'Other')])
    biography = CKEditorField('Biography', validators=[DataRequired()])
    skills = SelectField('Skills', validators=[DataRequired()], choices=[
        ('Translate', 'Translate'),
        ('Web Design', 'Web design'),
        ('Web Development', 'Web development'),
        ('Illustrator', 'Illustrator'),
        ('Article Writing', 'Article Writing'),
        ('Graphic Design', 'Graphic Design'),
        ('Logo Design', 'Logo Design')
    ])
    button = SubmitField('Next')


# Step 3 Onboarding Form (Project Owner)
class Step3ProjectOwner(FlaskForm):
    referral = RadioField('How do you know Worklink?', choices=[
        ('1', 'Search engine'),
        ('2', 'Social media'),
        ('3', 'Article on the internet'),
        ('4', 'Other')],
                          validators=[DataRequired()])
    button = SubmitField('Next')


# Step 3 Onboarding Forms (Freelancers)
class Step3Freelance(FlaskForm):
    title = StringField('Work Title', validators=[DataRequired()])
    thumbnail = FileField('Thumbnail', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    uploaded_file = FileField('Upload Work File', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Only image or PDF files are allowed!')
    ])
    completion_date = DateField('Completion Date', format='%Y-%m-%d', validators=[Optional()])
    link = URLField('Work Link', validators=[Optional(), URL()])
    submit = SubmitField('Save Work')

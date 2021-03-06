from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flaskblog.models import User
from flask_login import current_user



class SignUpForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired(),Length(min=3,max=30)])
    confirm_password = PasswordField("Confirm Password",validators=[DataRequired(),EqualTo("password")])
    submit = SubmitField("Sign Up")
    # Custom Validation
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("This username is taken. Please choose a different username.")
    
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is taken. Please choose a different email.")

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired(),Length(min=3,max=30)])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class UpdateProfileForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField("Email",validators=[DataRequired(),Email()])
    picture = FileField("Update Profile Picture",validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField("Update")
    # Custom Validation
    def validate_username(self,username):
        if username.data!=current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is taken. Please choose a different username.")
        
    def validate_email(self,email):
        if email.data!=current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email is taken. Please choose a different email.")

class RequestResetForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(),Email()]) 
    submit = SubmitField("Request Password Reset")

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("There is no account with this email.")
class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password",validators=[DataRequired(),Length(min=3,max=30)])
    confirm_password = PasswordField("Confirm Password",validators=[DataRequired(),EqualTo("password")])
    submit = SubmitField("Reset Password")
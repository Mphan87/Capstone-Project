from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length



class SearchForm(FlaskForm):
    term = TextAreaField('fried rice, curry, dentist', validators=[DataRequired()])
    location = StringField('city state zipcode', validators=[DataRequired()])
    
    
class MessageForm(FlaskForm):
    text = TextAreaField('text', validators=[DataRequired()])
    image_url = StringField('(Optional) Image URL')
    


class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    

class UserEditForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')
    location = StringField('Location', validators=[DataRequired()])
    bio = TextAreaField('(Optional) Tell us about yourself')
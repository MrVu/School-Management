from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, TextAreaField
from flask_pagedown.fields import PageDownField
from wtforms.validators import Required


class SubjectsAdd(FlaskForm):
    subject_name = StringField('Subject Name', validators=[Required()])
    submit = SubmitField('Add Subject')


class StudentForm(FlaskForm):
    name = StringField('Student name')
    phone_number = StringField('Phone number')
    address = StringField('Address')
    pay_day = StringField('dd-mm-yy')
    submit = SubmitField('Add')


class AttendanceClass(FlaskForm):
    submit = SubmitField('Choose class')


class AttendanceForm(FlaskForm):
    absent = BooleanField('Absent')
    submit = SubmitField('Add')


class AttendanceQuery(FlaskForm):
    date = StringField('Date')
    submit = SubmitField('Search')


class PostForm(FlaskForm):
    body = PageDownField('Enter your post')
    submit = SubmitField('Submit')

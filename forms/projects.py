from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProjectsForm(FlaskForm):
    title = StringField('Название проекта', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    image = FileField('Изображение')
    submit = SubmitField('Применить')
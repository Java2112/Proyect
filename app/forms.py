from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import FileField

class RegistrationForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired()])
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    confirm_password = PasswordField("Confirmar Contraseña", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrarse")

class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")

class UploadForm(FlaskForm):
    file = FileField("Selecciona un archivo Excel", validators=[DataRequired()])
    submit = SubmitField("Subir")
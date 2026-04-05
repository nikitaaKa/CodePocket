import datetime
import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, 
                                      default=datetime.datetime.now)
    creator = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    publications = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    publication_ids = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'<ID {self.id}> {self.username}' + ', creator' if self.creator else ''

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class RegisterForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    username = StringField('Username', validators=[DataRequired()])
    creator = BooleanField('I want to get a creator badge')
    submit = SubmitField('Register')

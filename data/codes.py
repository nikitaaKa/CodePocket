import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import orm

class Language(SqlAlchemyBase):
    __tablename__ = 'languages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    topics = orm.relationship("Topic", back_populates='language')

    def __repr__(self):
        return f'<Language {self.name}>'

class Topic(SqlAlchemyBase):
    __tablename__ = 'topics'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    language_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("languages.id"))

    language = orm.relationship('Language', back_populates='topics')
    libraries = orm.relationship("Library", back_populates='topic')

class Library(SqlAlchemyBase):
    __tablename__ = 'libraries'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    topic_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("topics.id"))
    
    topic = orm.relationship('Topic', back_populates='libraries')
    snippets = orm.relationship("CodeSnippet", back_populates='library')

class CodeSnippet(SqlAlchemyBase):
    __tablename__ = 'code_snippets'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    library_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("libraries.id"))
    library = orm.relationship('Library', back_populates='snippets')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')


class CreateLanguageForm(FlaskForm):
    name = StringField('Language (example: Python)', validators=[DataRequired()])
    submit = SubmitField('Add language')

class EditLanguageForm(CreateLanguageForm):
    submit = SubmitField('Edit language')

class CreateTopicForm(FlaskForm):
    name = StringField('Theme (example: Telegram Bots)', validators=[DataRequired()])
    language_id = SelectField('Language', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add theme')

class EditTopicForm(CreateTopicForm):
    submit = SubmitField('Edit theme')

class CreateLibraryForm(FlaskForm):
    name = StringField('Library (example: Aiogram)', validators=[DataRequired()])
    topic_id = SelectField('Theme', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add library')

class EditLibraryForm(CreateLibraryForm):
    submit = SubmitField('Edit library')

class CreateSnippetForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Template code', validators=[DataRequired()])
    library_id = SelectField('Library', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Publish')

class EditSnippetForm(CreateSnippetForm):
    submit = SubmitField('Save changes')

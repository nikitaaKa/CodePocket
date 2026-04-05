from flask import Flask, render_template, redirect, abort, request
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data import db_session
from data.users import User, RegisterForm, LoginForm
from data.codes import (Language, Topic, Library, CodeSnippet,
                        CreateLanguageForm, CreateTopicForm, CreateLibraryForm, CreateSnippetForm,
                        EditLanguageForm, EditTopicForm, EditLibraryForm, EditSnippetForm)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fhjklh23f78dsahf3nkojesadhfdsan783fh2jkoa'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User,user_id)

from flask import request
from sqlalchemy import or_, desc

@app.route('/')
@app.route('/index')
@app.route('/index/<la>')
@app.route('/index/<la>/<to>')
@app.route('/index/<la>/<to>/<li>')
def index(la=None, to=None, li=None):
    db_sess = db_session.create_session()

    search_query = request.args.get('q', '').strip()
    sort_type = request.args.get('sort', 'new')

    query = db_sess.query(CodeSnippet).join(Library).join(Topic).join(Language)

    if la: query = query.filter(Language.name == la)
    if to: query = query.filter(Topic.name == to)
    if li: query = query.filter(Library.name == li)

    if search_query:
        words = search_query.split()
        search_filters = [CodeSnippet.title.ilike(f"%{word}%") for word in words]
        query = query.filter(or_(*search_filters))

    if sort_type == 'new':
        query = query.order_by(desc(CodeSnippet.id))
    elif sort_type == 'old':
        query = query.order_by(CodeSnippet.id)

    snippets = query.all()

    if search_query:
        snippets.sort(key=lambda s: sum(word.lower() in s.title.lower() for word in words), reverse=True)

    languages = db_sess.query(Language).all()
    
    return render_template('index.html', snippets=snippets, languages=languages, 
                           la=la, to=to, li=li, sort=sort_type, q=search_query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register',
                                   form=form,
                                   message="This user already exist")
        user = User(
            username=form.username.data,
            email=form.email.data,
            creator=form.creator.data,
            publications=0,
            publication_ids=''
        )
        user.set_password(form.password.data)
        
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
        
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/user/<username>')
def user(username):
    data = {'username': username}
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.username.ilike(username)).first()
    if user:
        query = db_sess.query(CodeSnippet)

        snippets = query.filter(CodeSnippet.user_id == user.id).all()

        languages = db_sess.query(Language).all()

        data['id'] = user.id
        data['creator'] = user.creator
        data['publications'] = user.publications
        return render_template('user.html', **data, snippets=snippets, languages=languages)
    else:
        return f"No user with username {username}"
    
@app.route('/add_language', methods=['GET', 'POST'])
def add_language():
    form = CreateLanguageForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Language).filter(Language.name == form.name.data).first():
            return render_template('form_page.html', title='Добавить язык', form=form,
                                   message="Такой язык уже есть")
        language = Language(name=form.name.data)
        db_sess.add(language)
        db_sess.commit()
        return redirect('/')
    return render_template('form_page.html', title='Add language', form=form)

@app.route('/add_topic', methods=['GET', 'POST'])
def add_topic():
    db_sess = db_session.create_session()
    form = CreateTopicForm()
    form.language_id.choices = [(l.id, l.name) for l in db_sess.query(Language).all()]

    if form.validate_on_submit():
        topic = Topic(
            name=form.name.data,
            language_id=form.language_id.data
        )
        db_sess.add(topic)
        db_sess.commit()
        return redirect('/')
    return render_template('form_page.html', title='Add topic', form=form)

@app.route('/add_library', methods=['GET', 'POST'])
def add_library():
    db_sess = db_session.create_session()
    form = CreateLibraryForm()
    form.topic_id.choices = [(t.id, f"{t.name} ({t.language.name})") 
                             for t in db_sess.query(Topic).all()]

    if form.validate_on_submit():
        library = Library(
            name=form.name.data,
            topic_id=form.topic_id.data
        )
        db_sess.add(library)
        db_sess.commit()
        return redirect('/')
    return render_template('form_page.html', title='Add library', form=form)

from flask_login import current_user, login_required

@app.route('/add_snippet', methods=['GET', 'POST'])
@login_required
def add_snippet():
    db_sess = db_session.create_session()
    form = CreateSnippetForm()
    form.library_id.choices = [(lib.id, lib.name) for lib in db_sess.query(Library).all()]

    if form.validate_on_submit():
        snippet = CodeSnippet(
            title=form.title.data,
            content=form.content.data,
            library_id=form.library_id.data,
            user_id=current_user.id
        )
        user = db_sess.query(User).get(current_user.id)
        user.publications += 1
        
        db_sess.add(snippet)
        db_sess.commit()
        return redirect('/')
    return render_template('create_snippet.html', title='Create Snippet', form=form)

@app.route('/edit_language/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_language(id):
    db_sess = db_session.create_session()
    language = db_sess.query(Language).filter(Language.id == id).first()
    if not language:
        abort(404)
    
    form = EditLanguageForm()
    if request.method == "GET":
        form.name.data = language.name
        
    if form.validate_on_submit():
        language.name = form.name.data
        db_sess.commit()
        return redirect('/')
    return render_template('form_page.html', title='Редактирование языка', form=form)

@app.route('/edit_topic/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_topic(id):
    db_sess = db_session.create_session()
    topic = db_sess.query(Topic).get(id)
    if not topic:
        abort(404)
        
    form = EditTopicForm()
    form.language_id.choices = [(l.id, l.name) for l in db_sess.query(Language).all()]
    
    if request.method == "GET":
        form.name.data = topic.name
        form.language_id.data = topic.language_id
        
    if form.validate_on_submit():
        topic.name = form.name.data
        topic.language_id = form.language_id.data
        db_sess.commit()
        return redirect('/')
    return render_template('form_page.html', title='Редактирование темы', form=form)

@app.route('/edit_library/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_library(id):
    db_sess = db_session.create_session()
    library = db_sess.query(Library).get(id)
    if not library:
        abort(404)
        
    form = EditLibraryForm()
    form.topic_id.choices = [(t.id, t.name) for t in db_sess.query(Topic).all()]
    
    if request.method == "GET":
        form.name.data = library.name
        form.topic_id.data = library.topic_id
        
    if form.validate_on_submit():
        library.name = form.name.data
        library.topic_id = form.topic_id.data
        db_sess.commit()
        return redirect('/')
    return render_template('form_page.html', title='Редактирование библиотеки', form=form)

@app.route('/edit_snippet/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_snippet(id):
    db_sess = db_session.create_session()
    snippet = db_sess.query(CodeSnippet).get(id)
    if not snippet:
        abort(404)
    if snippet.user_id != current_user.id:
        abort(403)
        
    form = EditSnippetForm()
    form.library_id.choices = [(lib.id, lib.name) for lib in db_sess.query(Library).all()]
    
    if request.method == "GET":
        form.title.data = snippet.title
        form.content.data = snippet.content
        form.library_id.data = snippet.library_id
        
    if form.validate_on_submit():
        snippet.title = form.title.data
        snippet.content = form.content.data
        snippet.library_id = form.library_id.data
        db_sess.commit()
        return redirect('/')
    return render_template('create_snippet.html', title='Редактирование заготовки', form=form)

@app.route('/code/<int:id>')
def show_code(id):
    db_sess = db_session.create_session()
    snippet = db_sess.query(CodeSnippet).filter(CodeSnippet.id == id).first()
    if not snippet:
        abort(404)
    return render_template('code.html', snippet=snippet)


if __name__ == '__main__':
    db_session.global_init('db/data.db')
    app.run(port=8080, host='127.0.0.1')

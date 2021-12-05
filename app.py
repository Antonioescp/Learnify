from flask import Flask, render_template, request, url_for, flash, redirect, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import backref
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from operator import itemgetter
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Configurations

DEFAULT_DB = os.path.join(basedir, 'data-dev.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///' + DEFAULT_DB)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'yikes'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Decorators
def logout_required(function):
    @wraps(function)
    def wrapper():
        if session.get('user_id'):
            return redirect(url_for('index'))
        else:
            return function()
    return wrapper


def login_required(function):
    @wraps(function)
    def wrapper(**kwargs):
        if not session.get('user_id'):
            flash('Primero debes iniciar sesion')
            return redirect(url_for('login'))
        else:
            return function(**kwargs)
    return wrapper


def get_user(function):
    @wraps(function)
    def wrapper(**kwargs):
        g.user = User.query.filter_by(id=session.get('user_id')).first()
        return function(**kwargs)
    return wrapper
    
# Tables
lessons_users = db.Table('lessons_users', db.Model.metadata,
    db.Column('user_id', db.ForeignKey('users.id'), nullable=False),
    db.Column('lesson_id', db.ForeignKey('lessons.id'), nullable=False),
)

# Models
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    lessons = db.relationship('Lesson', backref=db.backref('users'), secondary=lessons_users)

    @property
    def password(self):
        return ValueError("Password can't be read")


    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
    def validate_username(self):
        return not User.query.filter_by(username=self.username).first()


    def __repr__(self):
        return '<User %r>' % self.username


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    short_description = db.Column(db.String(64))
    img_path = db.Column(db.String(128))
    lessons = db.relationship('Lesson', backref='course')


    def __repr__(self):
        return '<Course %r>' % self.title


class Lesson(db.Model):
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    options = db.relationship('Option', backref='lesson')


    def __repr__(self):
        return '<Lesson %r>' % self.title


class Option(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    audio_fn = db.Column(db.String(128))
    img_fn = db.Column(db.String(128))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)


    def __repr__(self):
        return '<Option %r>' % self.title


# Routes
@app.route('/')
@get_user
def index():
    return render_template('index.html', user=g.user)


@app.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':

        username, password = itemgetter('username', 'pass')(request.form)

        if not username or not password:
            flash('Ningun campo puede estar vacio.')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            
            session['user_id'] = user.id

            flash("Has iniciado sesion con exito")
            return redirect(url_for('index'))

        else:
            flash('Usuario o contraseña incorrectos')
            return render_template('auth/login.html')
            
    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()

    flash('Has cerrado sesion con exito.')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register():

    if request.method == 'POST':

        username, password = itemgetter('username', 'pass')(request.form)

        if not username or not password:
            flash("Ningun campo puede estar vacio")
            return render_template('auth/register.html')

        user = User(username=username)
        user.password = password

        if user.validate_username():
            db.session.add(user)
            db.session.commit()

            session['user_id'] = user.id

            flash('Has creado una cuenta con exito')
            return redirect(url_for('index'))

        flash('El usuario ya existe, por favor, elige otro nombre de usuario')

    return render_template('auth/register.html')


@app.route('/courses')
@login_required
@get_user
def courses():
    courses = Course.query.all()
    return render_template('courses/index.html', user=g.user, courses=courses)

@app.route('/courses/<course_id>')
@login_required
def course(course_id):
    
    course = Course.query.filter_by(id=course_id).first()

    if not course:
        flash('Curso no encontrado.')
        return redirect(url_for('index'))

    return render_template('courses/course.html', course=course, lessons=course.lessons)


@app.route('/lessons/<id>')
@login_required
@get_user
def lesson(id):

    lesson = Lesson.query.filter_by(id=id).first()

    return render_template('courses/lesson.html', lesson=lesson)


# Shell utils
@app.shell_context_processor
def make_shell_context():
    return dict( 
        db=db, 
        migrate=migrate,
        seed=seed,
        User=User,
        Course=Course,
        Lesson=Lesson,
        Option=Option,
    )

@app.cli.command('db-seed')
def seed():

    courses = [
        Course(
            title='Colores',
            short_description='Aprende los colores fundamentales.', 
            img_path='colors.svg',
        ),
        Course(
            title='Números',
            short_description='Aprende a contar.', 
            img_path='numbers.svg',
        ),
    ]

    lessons = [
        Lesson(title='Colores básicos.', course_id=1),
        Lesson(title='Un paso a la vez, contemos del 1 al 3.', course_id=2)
    ]

    options = [
        Option(
            title='Azul', 
            audio_fn='Colores-Azul.mp3', 
            img_fn='#006cff', 
            lesson_id=1
        ),
        Option(
            title='Rojo', 
            audio_fn='Colores-Rojo.mp3', 
            img_fn='#e32522', 
            lesson_id=1
        ),
        Option(
            title='Verde', 
            audio_fn='Colores-Verde.mp3', 
            img_fn='#5cf054', 
            lesson_id=1
        ),
        Option(
            title='Amarillo', 
            audio_fn='Colores-Amarillo.mp3', 
            img_fn='#fff945', 
            lesson_id=1
        ),
        Option(
            title='Uno o 1', 
            audio_fn='Numeros-1.mp3', 
            img_fn='1.svg', 
            lesson_id=2
        ),
        Option(
            title='Dos o 2', 
            audio_fn='Numeros-2.mp3', 
            img_fn='2.svg', 
            lesson_id=2
        ),
        Option(
            title='Tres o 3', 
            audio_fn='Numeros-3.mp3', 
            img_fn='3.svg', 
            lesson_id=2
        ),
    ]

    db.session.bulk_save_objects(courses)
    db.session.bulk_save_objects(lessons)
    db.session.bulk_save_objects(options)
    db.session.commit()

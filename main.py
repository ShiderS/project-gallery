from os import abort
from flask import Flask, request, make_response, render_template, redirect, jsonify
import datetime
from data import db_session, projects_resources
from data.user import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.auth import LoginForm
from data.projects import Projects
from forms.projects import ProjectsForm
import projects_api

from flask_restful import abort, Api

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
api = Api(app)


def abort_if_projects_not_found(projects_id):
    session = db_session.create_session()
    projects = session.query(Projects).get(projects_id)
    if not projects:
        abort(404, message=f"Projects {projects_id} not found")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        projects = db_sess.query(Projects).filter(
            (Projects.user == current_user) | (Projects.is_private != True))
    else:
        projects = db_sess.query(Projects).filter((Projects.is_private != True))

    return render_template("index.html", projects=projects)


def main():
    db_session.global_init("db/project-gallerybd.db")
    app.run()

    # user = User()
    # user.name = "Пользователь 1"
    # user.about = "биография пользователя 1"
    # user.email = "email@email.ru"
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.commit()


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/projects',  methods=['GET', 'POST'])
@login_required
def add_projects():
    form = ProjectsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = Projects()
        projects.title = form.title.data
        projects.content = form.content.data
        projects.is_private = form.is_private.data
        current_user.projects.append(projects)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('projects.html', title='Добавление проекта',
                           form=form)


@app.route('/projects/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_projects(id):
    form = ProjectsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id,
                                          Projects.user == current_user
                                          ).first()
        projects.is_confirmed = False
        if projects:
            form.title.data = projects.title
            form.content.data = projects.content
            form.is_private.data = projects.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id,
                                          Projects.user == current_user
                                          ).first()
        projects.is_confirmed = False
        if projects:
            projects.title = form.title.data
            projects.content = form.content.data
            projects.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('projects.html',
                           title='Редактирование проекта',
                           form=form
                           )


@app.route('/projects_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def projects_delete(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id,
                                      Projects.user == current_user
                                      ).first()
    if projects:
        projects.is_deleted = True
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/project-gallerybd.db")
    app.register_blueprint(projects_api.blueprint)
    app.run()
    # для списка объектов
    api.add_resource(projects_resources.ProjectsListResource, '/api/v2/projects')

    # для одного объекта
    api.add_resource(projects_resources.ProjectsResource, '/api/v2/projects/<int:projects_id>')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()

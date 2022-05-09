import flask
from flask import jsonify, request

from data import db_session
from data.projects import Projects

blueprint = flask.Blueprint(
    'projects_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/projects')
def get_projects():
    '''получение списков объектов'''
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).all()
    return jsonify(
        {
            'projects':
                [item.to_dict(only=('title', 'content', 'user.name'))
                 for item in projects]
        }
    )


@blueprint.route('/api/projects/<int:projects_id>', methods=['GET'])
def get_one_projects(projects_id):
    '''получение объекта'''
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).get(projects_id)
    if not projects:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'projects': projects.to_dict(only=(
                'title', 'content', 'user_id', 'is_private'))
        }
    )


@blueprint.route('/api/projects', methods=['POST'])
def create_projects():
    '''добавление объекта'''
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['title', 'content', 'user_id', 'is_private']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    projects = Projects(
        title=request.json['title'],
        content=request.json['content'],
        user_id=request.json['user_id'],
        is_private=request.json['is_private'],
        is_confirmed=request.json['is_confirmed'],
        is_deleted=request.json['is_deleted']
    )
    db_sess.add(projects)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/projects/<int:projects_id>', methods=['DELETE'])
def delete_projects(projects_id):
    '''удаление объекта'''
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).get(projects_id)
    if not projects:
        return jsonify({'error': 'Not found'})
    db_sess.delete(projects)
    db_sess.commit()
    return jsonify({'success': 'OK'})
    print(1)
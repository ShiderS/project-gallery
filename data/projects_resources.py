from os import abort

from flask import jsonify
from flask_restful import reqparse, Resource

from data import db_session
from data.projects import Projects
from main import abort_if_projects_not_found


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('is_confirmed', required=True, type=bool)
parser.add_argument('is_deleted', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


def abort_if_projects_not_found(projects_id):
    session = db_session.create_session()
    projects = session.query(Projects).get(projects_id)
    if not projects:
        abort(404, message=f"Projects {projects_id} not found")


class ProjectsResource(Resource):
    def get(self, projects_id):
        abort_if_projects_not_found(projects_id)
        session = db_session.create_session()
        projects = session.query(Projects).get(projects_id)
        return jsonify({'projects': projects.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, projects_id):
        abort_if_projects_not_found(projects_id)
        session = db_session.create_session()
        projects = session.query(Projects).get(projects_id)
        session.delete(projects)
        session.commit()
        return jsonify({'success': 'OK'})


class ProjectsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        projects = session.query(Projects).all()
        return jsonify({'projects': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in projects]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        projects = Projects(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_confirmed=args['is_confirmed'],
            is_deleted=args['is_deleted'],
            is_private=args['is_private']
        )
        session.add(projects)
        session.commit()
        return jsonify({'success': 'OK'})
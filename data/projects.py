import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Projects(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'projects'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    is_confirmed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    is_deleted = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    # image = sqlalchemy.BLOB(sqlalchemy.BLOB)
    image = sqlalchemy.Column()

    like = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    dislike = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    # is_modification = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)

    # is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

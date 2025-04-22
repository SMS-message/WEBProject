from .db_session import sqlalchemy, SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin

class Videos(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "Videos"

    ID = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    message_id = sqlalchemy.Column(sqlalchemy.Integer)
    author_id = sqlalchemy.Column(sqlalchemy.Integer)
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer)
    day = sqlalchemy.Column(sqlalchemy.Integer)
    month = sqlalchemy.Column(sqlalchemy.Integer)
    year = sqlalchemy.Column(sqlalchemy.Integer)

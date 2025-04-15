from flask_restful import Resource, abort
from flask import send_file, jsonify
from data.videos import Videos
from data.db_session import create_session
import sqlite3
import os

def abort_if_not_found(video_id: int):
    session = create_session()

    video = session.query(Videos).get(video_id)
    if not video:
        abort(404, message=f"Video {video_id} not found.")

class VideosResource(Resource):
    @staticmethod
    def get(video_id: int):
        abort_if_not_found(video_id)
        session = create_session()
        video: Videos = session.query(Videos).get(video_id)
        return send_file(f"../videos/{video.author_id}_{video.message_id}.mp4")

    @staticmethod
    def delete(video_id: int):
        try:
            session = create_session()
            video: Videos = session.query(Videos).get(video_id)
            video_filename = f"../videos/{video.author_id}_{video.message_id}.mp4"
            session.close()

            con = sqlite3.connect("../db/VideoHoster.db")
            cur = con.cursor()
            req = "SELECT name FROM sqlite_master WHERE type='table';"

            table_names = list(filter(lambda y: y[:4] == "User" or y == "Videos", map(lambda x: x[0], cur.execute(req).fetchall())))

            for table_name in table_names:
                cur.execute(f"DELETE FROM {table_name} WHERE ID = '{video_id}';")

            con.commit()
            con.close()

            os.remove(video_filename)
            return jsonify(
                {
                    "status": "200",
                    "info": f"video {video.author_id}_{video.message_id}.mp4 succesfully deleted."
                }
            )
        except Exception as err:
            return jsonify({"error": err.__str__()})


class VideosListResource(Resource):
    @staticmethod
    def get():
        session = create_session()
        videos = session.query(Videos).all()
        return jsonify(
            {
                "videos": [item.to_dict() for item in videos]
            }
        )

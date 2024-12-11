from flask import Blueprint, Response, jsonify
from streaming import generar_frames
from db_handler import get_fruit_counts

routes = Blueprint('routes', __name__)

@routes.route('/video-feed')
def video_feed():
    return Response(generar_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@routes.route('/counts', methods=['GET'])
def get_counts():
    return jsonify(get_fruit_counts())
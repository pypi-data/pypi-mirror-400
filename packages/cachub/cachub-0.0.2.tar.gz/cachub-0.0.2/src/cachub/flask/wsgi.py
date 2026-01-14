from flask import Blueprint, jsonify

from .auth import token_required

bp = Blueprint('wsgi', __name__)


@bp.route('/home')
def page_home():
    return "Base wsgi"


@bp.route('/api', methods=['POST'])
@token_required
def page_api():
    data = "a" * 100  # open("rac5_hourly.csv").read()
    return jsonify({"status": "success", "message": "valid token", "data": data})

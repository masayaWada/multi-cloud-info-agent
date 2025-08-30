from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return jsonify({
        'message': 'Multi-Cloud Info Agent API',
        'version': '1.0.0',
        'status': 'running'
    })


@main_bp.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z'
    })

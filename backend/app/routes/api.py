from flask import Blueprint, request, jsonify
from app.services.chat_service import ChatService
from app.services.mcp_service import MCPService
from app.utils.logger import get_logger

api_bp = Blueprint('api', __name__)
logger = get_logger(__name__)


@api_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'メッセージが必要です'}), 400

        user_message = data['message']
        logger.info(f"受信メッセージ: {user_message}")

        # チャットサービスでメッセージを処理
        chat_service = ChatService()
        response = chat_service.process_message(user_message)

        logger.info(f"応答生成完了: {len(response)} 文字")

        return jsonify({
            'response': response,
            'timestamp': '2024-01-01T00:00:00Z'
        })

    except Exception as e:
        logger.error(f"チャット処理エラー: {str(e)}")
        return jsonify({
            'error': '内部サーバーエラーが発生しました',
            'details': str(e)
        }), 500


@api_bp.route('/resources/aws', methods=['GET'])
def get_aws_resources():
    try:
        resource_type = request.args.get('type', 'ec2')
        mcp_service = MCPService()
        resources = mcp_service.get_aws_resources(resource_type)

        return jsonify({
            'resources': resources,
            'type': resource_type,
            'count': len(resources)
        })

    except Exception as e:
        logger.error(f"AWS リソース取得エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/resources/azure', methods=['GET'])
def get_azure_resources():
    try:
        resource_type = request.args.get('type', 'vm')
        mcp_service = MCPService()
        resources = mcp_service.get_azure_resources(resource_type)

        return jsonify({
            'resources': resources,
            'type': resource_type,
            'count': len(resources)
        })

    except Exception as e:
        logger.error(f"Azure リソース取得エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/logs', methods=['GET'])
def get_logs():
    try:
        cloud_provider = request.args.get('provider', 'aws')
        service = request.args.get('service', 'ec2')
        mcp_service = MCPService()
        logs = mcp_service.get_logs(cloud_provider, service)

        return jsonify({
            'logs': logs,
            'provider': cloud_provider,
            'service': service
        })

    except Exception as e:
        logger.error(f"ログ取得エラー: {str(e)}")
        return jsonify({'error': str(e)}), 500

import pytest
from unittest.mock import Mock, patch
from app import create_app


class TestAPIRoutes:
    """API ルートのテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_endpoint(self):
        """ヘルスチェックエンドポイントのテスト"""
        response = self.client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    def test_index_endpoint(self):
        """インデックスエンドポイントのテスト"""
        response = self.client.get('/')

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Multi-Cloud Info Agent API'
        assert data['version'] == '1.0.0'
        assert data['status'] == 'running'

    @patch('app.routes.api.ChatService')
    def test_chat_endpoint_success(self, mock_chat_service):
        """チャットエンドポイントの成功テスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_chat_service.return_value = mock_service_instance
        mock_service_instance.process_message.return_value = "テストレスポンス"

        # テスト実行
        response = self.client.post('/api/chat',
                                    json={'message': 'テストメッセージ'})

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data['response'] == "テストレスポンス"
        assert 'timestamp' in data
        mock_service_instance.process_message.assert_called_once_with(
            'テストメッセージ')

    def test_chat_endpoint_missing_message(self):
        """チャットエンドポイントのメッセージ不足テスト"""
        response = self.client.post('/api/chat', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'メッセージが必要です' in data['error']

    def test_chat_endpoint_invalid_json(self):
        """チャットエンドポイントの無効なJSONテスト"""
        response = self.client.post('/api/chat',
                                    data='invalid json',
                                    content_type='application/json')

        assert response.status_code == 400

    @patch('app.routes.api.ChatService')
    def test_chat_endpoint_service_error(self, mock_chat_service):
        """チャットエンドポイントのサービスエラーテスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_chat_service.return_value = mock_service_instance
        mock_service_instance.process_message.side_effect = Exception("テストエラー")

        # テスト実行
        response = self.client.post('/api/chat',
                                    json={'message': 'テストメッセージ'})

        # アサーション
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert '内部サーバーエラー' in data['error']

    @patch('app.routes.api.MCPService')
    def test_get_aws_resources_success(self, mock_mcp_service):
        """AWS リソース取得の成功テスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_aws_resources.return_value = [
            {'name': 'test-instance', 'state': 'running'}
        ]

        # テスト実行
        response = self.client.get('/api/resources/aws?type=ec2')

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
        assert data['type'] == 'ec2'
        assert data['count'] == 1
        assert data['resources'][0]['name'] == 'test-instance'
        mock_service_instance.get_aws_resources.assert_called_once_with('ec2')

    @patch('app.routes.api.MCPService')
    def test_get_aws_resources_default_type(self, mock_mcp_service):
        """AWS リソース取得のデフォルトタイプテスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_aws_resources.return_value = []

        # テスト実行
        response = self.client.get('/api/resources/aws')

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data['type'] == 'ec2'  # デフォルトタイプ
        mock_service_instance.get_aws_resources.assert_called_once_with('ec2')

    @patch('app.routes.api.MCPService')
    def test_get_aws_resources_service_error(self, mock_mcp_service):
        """AWS リソース取得のサービスエラーテスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_aws_resources.side_effect = Exception(
            "AWS エラー")

        # テスト実行
        response = self.client.get('/api/resources/aws?type=ec2')

        # アサーション
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert 'AWS エラー' in data['error']

    @patch('app.routes.api.MCPService')
    def test_get_azure_resources_success(self, mock_mcp_service):
        """Azure リソース取得の成功テスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_azure_resources.return_value = [
            {'name': 'test-vm', 'status': 'running'}
        ]

        # テスト実行
        response = self.client.get('/api/resources/azure?type=vm')

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert 'resources' in data
        assert data['type'] == 'vm'
        assert data['count'] == 1
        assert data['resources'][0]['name'] == 'test-vm'
        mock_service_instance.get_azure_resources.assert_called_once_with('vm')

    @patch('app.routes.api.MCPService')
    def test_get_azure_resources_default_type(self, mock_mcp_service):
        """Azure リソース取得のデフォルトタイプテスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_azure_resources.return_value = []

        # テスト実行
        response = self.client.get('/api/resources/azure')

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data['type'] == 'vm'  # デフォルトタイプ
        mock_service_instance.get_azure_resources.assert_called_once_with('vm')

    @patch('app.routes.api.MCPService')
    def test_get_logs_success(self, mock_mcp_service):
        """ログ取得の成功テスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_logs.return_value = [
            {'timestamp': 1704067200000, 'message': 'Test log'}
        ]

        # テスト実行
        response = self.client.get('/api/logs?provider=aws&service=ec2')

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert 'logs' in data
        assert data['provider'] == 'aws'
        assert data['service'] == 'ec2'
        assert len(data['logs']) == 1
        mock_service_instance.get_logs.assert_called_once_with('aws', 'ec2')

    @patch('app.routes.api.MCPService')
    def test_get_logs_default_parameters(self, mock_mcp_service):
        """ログ取得のデフォルトパラメータテスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_logs.return_value = []

        # テスト実行
        response = self.client.get('/api/logs?provider=aws')

        # アサーション
        assert response.status_code == 200
        data = response.get_json()
        assert data['provider'] == 'aws'
        assert data['service'] == 'ec2'  # デフォルトサービス
        mock_service_instance.get_logs.assert_called_once_with('aws', 'ec2')

    @patch('app.routes.api.MCPService')
    def test_get_logs_service_error(self, mock_mcp_service):
        """ログ取得のサービスエラーテスト"""
        # モックの設定
        mock_service_instance = Mock()
        mock_mcp_service.return_value = mock_service_instance
        mock_service_instance.get_logs.side_effect = Exception("ログ取得エラー")

        # テスト実行
        response = self.client.get('/api/logs?provider=aws&service=ec2')

        # アサーション
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data
        assert 'ログ取得エラー' in data['error']

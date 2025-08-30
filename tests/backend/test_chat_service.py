import pytest
from unittest.mock import Mock, patch
from app.services.chat_service import ChatService


class TestChatService:
    """ChatService のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.chat_service = ChatService()

    @patch('app.services.chat_service.LLMService')
    @patch('app.services.chat_service.MCPService')
    def test_process_message_resource_list(self, mock_mcp_service, mock_llm_service):
        """リソース一覧取得リクエストのテスト"""
        # モックの設定
        mock_llm_instance = Mock()
        mock_llm_service.return_value = mock_llm_instance
        mock_llm_instance.generate_response.return_value = '{"type": "resource_list", "provider": "aws", "service": "ec2", "parameters": {}}'

        mock_mcp_instance = Mock()
        mock_mcp_service.return_value = mock_mcp_instance
        mock_mcp_instance.get_aws_resources.return_value = [
            {'name': 'test-instance', 'state': 'running'}
        ]

        # テスト実行
        result = self.chat_service.process_message("EC2インスタンス一覧を教えて")

        # アサーション
        assert "AWS EC2 リソース一覧" in result
        assert "test-instance" in result
        mock_mcp_instance.get_aws_resources.assert_called_once_with('ec2')

    @patch('app.services.chat_service.LLMService')
    def test_process_message_general_question(self, mock_llm_service):
        """一般的な質問のテスト"""
        # モックの設定
        mock_llm_instance = Mock()
        mock_llm_service.return_value = mock_llm_instance
        mock_llm_instance.generate_response.return_value = '{"type": "general_question", "provider": "both", "service": "unknown", "parameters": {}}'
        mock_llm_instance.generate_response.return_value = "AWSの料金について説明します..."

        # テスト実行
        result = self.chat_service.process_message("AWSの料金について教えて")

        # アサーション
        assert "AWSの料金について説明します" in result
        mock_llm_instance.generate_response.assert_called()

    def test_analyze_intent_valid_json(self):
        """有効なJSONレスポンスの意図解析テスト"""
        with patch.object(self.chat_service.llm_service, 'generate_response') as mock_generate:
            mock_generate.return_value = '{"type": "resource_list", "provider": "aws", "service": "s3", "parameters": {}}'

            intent = self.chat_service._analyze_intent("S3バケット一覧を教えて")

            assert intent['type'] == 'resource_list'
            assert intent['provider'] == 'aws'
            assert intent['service'] == 's3'

    def test_analyze_intent_invalid_json(self):
        """無効なJSONレスポンスの意図解析テスト"""
        with patch.object(self.chat_service.llm_service, 'generate_response') as mock_generate:
            mock_generate.return_value = 'Invalid JSON response'

            intent = self.chat_service._analyze_intent("テストメッセージ")

            # デフォルトの意図が返されることを確認
            assert intent['type'] == 'general_question'
            assert intent['provider'] == 'both'

    @patch('app.services.chat_service.MCPService')
    def test_handle_resource_list_request_aws(self, mock_mcp_service):
        """AWS リソース一覧取得のテスト"""
        mock_mcp_instance = Mock()
        mock_mcp_service.return_value = mock_mcp_instance
        mock_mcp_instance.get_aws_resources.return_value = [
            {'name': 'instance-1', 'state': 'running'},
            {'name': 'instance-2', 'state': 'stopped'}
        ]

        intent = {'provider': 'aws', 'service': 'ec2'}
        result = self.chat_service._handle_resource_list_request(intent)

        assert "AWS EC2 リソース一覧" in result
        assert "instance-1" in result
        assert "instance-2" in result
        mock_mcp_instance.get_aws_resources.assert_called_once_with('ec2')

    @patch('app.services.chat_service.MCPService')
    def test_handle_resource_list_request_azure(self, mock_mcp_service):
        """Azure リソース一覧取得のテスト"""
        mock_mcp_instance = Mock()
        mock_mcp_service.return_value = mock_mcp_instance
        mock_mcp_instance.get_azure_resources.return_value = [
            {'name': 'vm-1', 'state': 'running'},
            {'name': 'vm-2', 'state': 'stopped'}
        ]

        intent = {'provider': 'azure', 'service': 'vm'}
        result = self.chat_service._handle_resource_list_request(intent)

        assert "Azure VM リソース一覧" in result
        assert "vm-1" in result
        assert "vm-2" in result
        mock_mcp_instance.get_azure_resources.assert_called_once_with('vm')

    def test_handle_unknown_request(self):
        """未知のリクエストのテスト"""
        result = self.chat_service._handle_unknown_request("不明なメッセージ")

        assert "申し訳ございません" in result
        assert "利用可能な機能" in result

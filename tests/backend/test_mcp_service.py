import pytest
from unittest.mock import Mock, patch
import boto3
from app.services.mcp_service import MCPService


class TestMCPService:
    """MCPService のテストクラス"""

    def setup_method(self):
        """各テストメソッドの前に実行"""
        self.mcp_service = MCPService()

    @patch('app.services.mcp_service.boto3.Session')
    def test_initialize_aws_session(self, mock_boto3_session):
        """AWS セッション初期化のテスト"""
        mock_session = Mock()
        mock_boto3_session.return_value = mock_session

        mcp_service = MCPService()

        mock_boto3_session.assert_called_once()
        assert mcp_service.aws_session == mock_session

    @patch('app.services.mcp_service.DefaultAzureCredential')
    def test_initialize_azure_credential(self, mock_azure_credential):
        """Azure 認証情報初期化のテスト"""
        mock_credential = Mock()
        mock_azure_credential.return_value = mock_credential

        mcp_service = MCPService()

        mock_azure_credential.assert_called_once()
        assert mcp_service.azure_credential == mock_credential

    def test_get_aws_resources_ec2(self):
        """AWS EC2 リソース取得のテスト"""
        with patch.object(self.mcp_service, '_get_aws_ec2_instances') as mock_get_ec2:
            mock_get_ec2.return_value = [
                {'name': 'test-instance', 'state': 'running'}
            ]

            result = self.mcp_service.get_aws_resources('ec2')

            assert len(result) == 1
            assert result[0]['name'] == 'test-instance'
            mock_get_ec2.assert_called_once()

    def test_get_aws_resources_s3(self):
        """AWS S3 リソース取得のテスト"""
        with patch.object(self.mcp_service, '_get_aws_s3_buckets') as mock_get_s3:
            mock_get_s3.return_value = [
                {'name': 'test-bucket', 'creation_date': '2024-01-01T00:00:00Z'}
            ]

            result = self.mcp_service.get_aws_resources('s3')

            assert len(result) == 1
            assert result[0]['name'] == 'test-bucket'
            mock_get_s3.assert_called_once()

    def test_get_aws_resources_unsupported_type(self):
        """未対応のAWSリソースタイプのテスト"""
        result = self.mcp_service.get_aws_resources('unsupported')

        assert result == []

    def test_get_azure_resources_vm(self):
        """Azure VM リソース取得のテスト"""
        with patch.object(self.mcp_service, '_get_azure_vms') as mock_get_vms:
            mock_get_vms.return_value = [
                {'name': 'test-vm', 'status': 'running'}
            ]

            result = self.mcp_service.get_azure_resources('vm')

            assert len(result) == 1
            assert result[0]['name'] == 'test-vm'
            mock_get_vms.assert_called_once()

    def test_get_azure_resources_storage(self):
        """Azure ストレージリソース取得のテスト"""
        with patch.object(self.mcp_service, '_get_azure_storage_accounts') as mock_get_storage:
            mock_get_storage.return_value = [
                {'name': 'test-storage', 'status': 'available'}
            ]

            result = self.mcp_service.get_azure_resources('storage')

            assert len(result) == 1
            assert result[0]['name'] == 'test-storage'
            mock_get_storage.assert_called_once()

    def test_get_azure_resources_unsupported_type(self):
        """未対応のAzureリソースタイプのテスト"""
        result = self.mcp_service.get_azure_resources('unsupported')

        assert result == []

    @patch('app.services.mcp_service.boto3.Session')
    def test_get_aws_ec2_instances(self, mock_boto3_session):
        """EC2 インスタンス取得の詳細テスト"""
        # モックの設定
        mock_session = Mock()
        mock_boto3_session.return_value = mock_session

        mock_ec2_client = Mock()
        mock_session.client.return_value = mock_ec2_client

        mock_ec2_client.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'InstanceType': 't3.micro',
                            'State': {'Name': 'running'},
                            'LaunchTime': Mock(isoformat=lambda: '2024-01-01T00:00:00Z'),
                            'PublicIpAddress': '203.0.113.1',
                            'PrivateIpAddress': '10.0.1.100',
                            'Tags': [{'Key': 'Name', 'Value': 'test-instance'}]
                        }
                    ]
                }
            ]
        }

        mcp_service = MCPService()
        result = mcp_service._get_aws_ec2_instances()

        assert len(result) == 1
        assert result[0]['id'] == 'i-1234567890abcdef0'
        assert result[0]['name'] == 'test-instance'
        assert result[0]['state'] == 'running'

    @patch('app.services.mcp_service.boto3.Session')
    def test_get_aws_s3_buckets(self, mock_boto3_session):
        """S3 バケット取得の詳細テスト"""
        # モックの設定
        mock_session = Mock()
        mock_boto3_session.return_value = mock_session

        mock_s3_client = Mock()
        mock_session.client.return_value = mock_s3_client

        mock_s3_client.list_buckets.return_value = {
            'Buckets': [
                {
                    'Name': 'test-bucket',
                    'CreationDate': Mock(isoformat=lambda: '2024-01-01T00:00:00Z')
                }
            ]
        }

        mcp_service = MCPService()
        result = mcp_service._get_aws_s3_buckets()

        assert len(result) == 1
        assert result[0]['name'] == 'test-bucket'
        assert result[0]['creation_date'] == '2024-01-01T00:00:00Z'

    def test_get_logs_aws(self):
        """AWS ログ取得のテスト"""
        with patch.object(self.mcp_service, '_get_aws_logs') as mock_get_aws_logs:
            mock_get_aws_logs.return_value = [
                {'timestamp': 1704067200000, 'message': 'Test log message'}
            ]

            result = self.mcp_service.get_logs('aws', 'ec2')

            assert len(result) == 1
            assert result[0]['message'] == 'Test log message'
            mock_get_aws_logs.assert_called_once_with('ec2')

    def test_get_logs_azure(self):
        """Azure ログ取得のテスト"""
        with patch.object(self.mcp_service, '_get_azure_logs') as mock_get_azure_logs:
            mock_get_azure_logs.return_value = [
                {'timestamp': '2024-01-01T00:00:00Z',
                    'message': 'Azure log message'}
            ]

            result = self.mcp_service.get_logs('azure', 'vm')

            assert len(result) == 1
            assert result[0]['message'] == 'Azure log message'
            mock_get_azure_logs.assert_called_once_with('vm')

    def test_get_logs_unsupported_provider(self):
        """未対応のプロバイダーのログ取得テスト"""
        result = self.mcp_service.get_logs('unsupported', 'service')

        assert result == []

    def test_get_instance_name_with_name_tag(self):
        """Name タグがあるインスタンス名取得のテスト"""
        instance = {
            'InstanceId': 'i-1234567890abcdef0',
            'Tags': [{'Key': 'Name', 'Value': 'test-instance'}]
        }

        result = self.mcp_service._get_instance_name(instance)

        assert result == 'test-instance'

    def test_get_instance_name_without_name_tag(self):
        """Name タグがないインスタンス名取得のテスト"""
        instance = {
            'InstanceId': 'i-1234567890abcdef0',
            'Tags': [{'Key': 'Environment', 'Value': 'production'}]
        }

        result = self.mcp_service._get_instance_name(instance)

        assert result == 'i-1234567890abcdef0'

import pytest
import os
from unittest.mock import Mock, patch
from app import create_app


@pytest.fixture
def app():
    """テスト用のFlaskアプリケーション"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    # テスト用の環境変数を設定
    os.environ['OPENAI_API_KEY'] = 'test-openai-key'
    os.environ['AWS_ACCESS_KEY_ID'] = 'test-aws-key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-aws-secret'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['AZURE_CLIENT_ID'] = 'test-azure-client-id'
    os.environ['AZURE_CLIENT_SECRET'] = 'test-azure-secret'
    os.environ['AZURE_TENANT_ID'] = 'test-azure-tenant-id'
    os.environ['AZURE_SUBSCRIPTION_ID'] = 'test-azure-subscription-id'

    yield app


@pytest.fixture
def client(app):
    """テストクライアント"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """テストランナー"""
    return app.test_cli_runner()


@pytest.fixture
def mock_openai():
    """OpenAI クライアントのモック"""
    with patch('app.services.llm_service.OpenAI') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance

        # デフォルトのレスポンスを設定
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "テストレスポンス"
        mock_instance.chat.completions.create.return_value = mock_response

        yield mock_instance


@pytest.fixture
def mock_boto3():
    """Boto3 セッションのモック"""
    with patch('app.services.mcp_service.boto3.Session') as mock:
        mock_session = Mock()
        mock.return_value = mock_session

        # EC2 クライアントのモック
        mock_ec2_client = Mock()
        mock_ec2_client.describe_instances.return_value = {
            'Reservations': []
        }

        # S3 クライアントのモック
        mock_s3_client = Mock()
        mock_s3_client.list_buckets.return_value = {
            'Buckets': []
        }

        # RDS クライアントのモック
        mock_rds_client = Mock()
        mock_rds_client.describe_db_instances.return_value = {
            'DBInstances': []
        }

        # ログクライアントのモック
        mock_logs_client = Mock()
        mock_logs_client.describe_log_groups.return_value = {
            'logGroups': []
        }

        mock_session.client.side_effect = lambda service: {
            'ec2': mock_ec2_client,
            's3': mock_s3_client,
            'rds': mock_rds_client,
            'logs': mock_logs_client
        }[service]

        yield mock_session


@pytest.fixture
def mock_azure_credential():
    """Azure 認証情報のモック"""
    with patch('app.services.mcp_service.DefaultAzureCredential') as mock:
        mock_credential = Mock()
        mock.return_value = mock_credential
        yield mock_credential


@pytest.fixture
def mock_azure_compute_client():
    """Azure Compute クライアントのモック"""
    with patch('app.services.mcp_service.ComputeManagementClient') as mock:
        mock_client = Mock()
        mock.return_value = mock_client

        # VM リストのモック
        mock_vm = Mock()
        mock_vm.id = 'test-vm-id'
        mock_vm.name = 'test-vm'
        mock_vm.location = 'Japan East'
        mock_vm.provisioning_state = 'Succeeded'
        mock_vm.hardware_profile = Mock()
        mock_vm.hardware_profile.vm_size = 'Standard_B1s'
        mock_vm.storage_profile = Mock()
        mock_vm.storage_profile.os_disk = Mock()
        mock_vm.storage_profile.os_disk.os_type = Mock()
        mock_vm.storage_profile.os_disk.os_type.value = 'Linux'

        mock_client.virtual_machines.list_all.return_value = [mock_vm]

        yield mock_client


@pytest.fixture
def mock_azure_storage_client():
    """Azure Storage クライアントのモック"""
    with patch('app.services.mcp_service.StorageManagementClient') as mock:
        mock_client = Mock()
        mock.return_value = mock_client

        # ストレージアカウントのモック
        mock_account = Mock()
        mock_account.id = 'test-storage-id'
        mock_account.name = 'test-storage'
        mock_account.location = 'Japan East'
        mock_account.status_of_primary = Mock()
        mock_account.status_of_primary.value = 'available'
        mock_account.sku = Mock()
        mock_account.sku.tier = Mock()
        mock_account.sku.tier.value = 'Standard'

        mock_client.storage_accounts.list.return_value = [mock_account]

        yield mock_client


@pytest.fixture
def sample_ec2_instances():
    """サンプルのEC2インスタンスデータ"""
    return [
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


@pytest.fixture
def sample_s3_buckets():
    """サンプルのS3バケットデータ"""
    return [
        {
            'Name': 'test-bucket',
            'CreationDate': Mock(isoformat=lambda: '2024-01-01T00:00:00Z')
        }
    ]


@pytest.fixture
def sample_azure_vms():
    """サンプルのAzure VMデータ"""
    return [
        {
            'id': '/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines/myVM',
            'name': 'myVM',
            'location': 'Japan East',
            'status': 'Succeeded',
            'size': 'Standard_B1s',
            'os_type': 'Linux'
        }
    ]


@pytest.fixture
def sample_logs():
    """サンプルのログデータ"""
    return [
        {
            'timestamp': 1704067200000,
            'message': 'Instance i-1234567890abcdef0 started successfully',
            'log_group': '/aws/ec2/instances',
            'log_stream': 'i-1234567890abcdef0'
        }
    ]

import os
import boto3
from typing import List, Dict, Any, Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MCPService:
    def __init__(self):
        self.aws_session = None
        self.azure_credential = None
        self._initialize_clients()

    def _initialize_clients(self):
        """
        AWS と Azure のクライアントを初期化
        """
        # AWS クライアントの初期化
        try:
            self.aws_session = boto3.Session(
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
            logger.info("AWS セッションが初期化されました")
        except Exception as e:
            logger.error(f"AWS セッションの初期化に失敗: {str(e)}")

        # Azure クライアントの初期化
        try:
            self.azure_credential = DefaultAzureCredential()
            logger.info("Azure 認証情報が初期化されました")
        except Exception as e:
            logger.error(f"Azure 認証情報の初期化に失敗: {str(e)}")

    def get_aws_resources(self, resource_type: str = 'ec2') -> List[Dict[str, Any]]:
        """
        AWS リソース一覧を取得
        """
        if not self.aws_session:
            logger.error("AWS セッションが初期化されていません")
            return []

        try:
            if resource_type == 'ec2':
                return self._get_aws_ec2_instances()
            elif resource_type == 's3':
                return self._get_aws_s3_buckets()
            elif resource_type == 'rds':
                return self._get_aws_rds_instances()
            else:
                logger.warning(f"未対応のAWSリソースタイプ: {resource_type}")
                return []

        except Exception as e:
            logger.error(f"AWS リソース取得エラー: {str(e)}")
            return []

    def _get_aws_ec2_instances(self) -> List[Dict[str, Any]]:
        """
        EC2 インスタンス一覧を取得
        """
        try:
            ec2 = self.aws_session.client('ec2')
            response = ec2.describe_instances()

            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'id': instance['InstanceId'],
                        'name': self._get_instance_name(instance),
                        'type': instance['InstanceType'],
                        'state': instance['State']['Name'],
                        'region': self.aws_session.region_name,
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'public_ip': instance.get('PublicIpAddress', 'N/A'),
                        'private_ip': instance.get('PrivateIpAddress', 'N/A')
                    })

            return instances

        except Exception as e:
            logger.error(f"EC2 インスタンス取得エラー: {str(e)}")
            return []

    def _get_aws_s3_buckets(self) -> List[Dict[str, Any]]:
        """
        S3 バケット一覧を取得
        """
        try:
            s3 = self.aws_session.client('s3')
            response = s3.list_buckets()

            buckets = []
            for bucket in response['Buckets']:
                buckets.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'].isoformat(),
                    'region': self.aws_session.region_name
                })

            return buckets

        except Exception as e:
            logger.error(f"S3 バケット取得エラー: {str(e)}")
            return []

    def _get_aws_rds_instances(self) -> List[Dict[str, Any]]:
        """
        RDS インスタンス一覧を取得
        """
        try:
            rds = self.aws_session.client('rds')
            response = rds.describe_db_instances()

            instances = []
            for db_instance in response['DBInstances']:
                instances.append({
                    'id': db_instance['DBInstanceIdentifier'],
                    'name': db_instance['DBInstanceIdentifier'],
                    'engine': db_instance['Engine'],
                    'status': db_instance['DBInstanceStatus'],
                    'class': db_instance['DBInstanceClass'],
                    'region': self.aws_session.region_name
                })

            return instances

        except Exception as e:
            logger.error(f"RDS インスタンス取得エラー: {str(e)}")
            return []

    def get_azure_resources(self, resource_type: str = 'vm') -> List[Dict[str, Any]]:
        """
        Azure リソース一覧を取得
        """
        if not self.azure_credential:
            logger.error("Azure 認証情報が初期化されていません")
            return []

        try:
            subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
            if not subscription_id:
                logger.error("AZURE_SUBSCRIPTION_ID が設定されていません")
                return []

            if resource_type == 'vm':
                return self._get_azure_vms(subscription_id)
            elif resource_type == 'storage':
                return self._get_azure_storage_accounts(subscription_id)
            else:
                logger.warning(f"未対応のAzureリソースタイプ: {resource_type}")
                return []

        except Exception as e:
            logger.error(f"Azure リソース取得エラー: {str(e)}")
            return []

    def _get_azure_vms(self, subscription_id: str) -> List[Dict[str, Any]]:
        """
        Azure VM 一覧を取得
        """
        try:
            compute_client = ComputeManagementClient(
                self.azure_credential, subscription_id
            )

            vms = []
            for vm in compute_client.virtual_machines.list_all():
                vms.append({
                    'id': vm.id,
                    'name': vm.name,
                    'location': vm.location,
                    'status': vm.provisioning_state,
                    'size': vm.hardware_profile.vm_size if vm.hardware_profile else 'N/A',
                    'os_type': vm.storage_profile.os_disk.os_type.value if vm.storage_profile and vm.storage_profile.os_disk else 'N/A'
                })

            return vms

        except Exception as e:
            logger.error(f"Azure VM 取得エラー: {str(e)}")
            return []

    def _get_azure_storage_accounts(self, subscription_id: str) -> List[Dict[str, Any]]:
        """
        Azure ストレージアカウント一覧を取得
        """
        try:
            storage_client = StorageManagementClient(
                self.azure_credential, subscription_id
            )

            accounts = []
            for account in storage_client.storage_accounts.list():
                accounts.append({
                    'id': account.id,
                    'name': account.name,
                    'location': account.location,
                    'status': account.status_of_primary.value if account.status_of_primary else 'N/A',
                    'tier': account.sku.tier.value if account.sku else 'N/A'
                })

            return accounts

        except Exception as e:
            logger.error(f"Azure ストレージアカウント取得エラー: {str(e)}")
            return []

    def get_logs(self, provider: str, service: str) -> List[Dict[str, Any]]:
        """
        ログを取得
        """
        try:
            if provider == 'aws':
                return self._get_aws_logs(service)
            elif provider == 'azure':
                return self._get_azure_logs(service)
            else:
                logger.warning(f"未対応のプロバイダー: {provider}")
                return []

        except Exception as e:
            logger.error(f"ログ取得エラー: {str(e)}")
            return []

    def _get_aws_logs(self, service: str) -> List[Dict[str, Any]]:
        """
        AWS ログを取得
        """
        try:
            logs_client = self.aws_session.client('logs')

            # CloudWatch Logs からログを取得
            log_groups = logs_client.describe_log_groups()

            logs = []
            for log_group in log_groups['logGroups'][:5]:  # 最初の5つのロググループ
                try:
                    log_streams = logs_client.describe_log_streams(
                        logGroupName=log_group['logGroupName'],
                        orderBy='LastEventTime',
                        descending=True,
                        limit=3
                    )

                    for stream in log_streams['logStreams']:
                        events = logs_client.get_log_events(
                            logGroupName=log_group['logGroupName'],
                            logStreamName=stream['logStreamName'],
                            limit=5
                        )

                        for event in events['events']:
                            logs.append({
                                'timestamp': event['timestamp'],
                                'message': event['message'],
                                'log_group': log_group['logGroupName'],
                                'log_stream': stream['logStreamName']
                            })

                except Exception as e:
                    logger.warning(f"ログストリーム取得エラー: {str(e)}")
                    continue

            return logs[:20]  # 最大20件

        except Exception as e:
            logger.error(f"AWS ログ取得エラー: {str(e)}")
            return []

    def _get_azure_logs(self, service: str) -> List[Dict[str, Any]]:
        """
        Azure ログを取得
        """
        # Azure Monitor Logs の実装
        # 現在はモックデータを返す
        return [
            {
                'timestamp': '2024-01-01T00:00:00Z',
                'message': 'Azure VM の起動が完了しました',
                'level': 'INFO',
                'service': service
            },
            {
                'timestamp': '2024-01-01T00:01:00Z',
                'message': 'ストレージアカウントへの接続が確立されました',
                'level': 'INFO',
                'service': service
            }
        ]

    def _get_instance_name(self, instance: Dict[str, Any]) -> str:
        """
        EC2 インスタンスの名前を取得
        """
        for tag in instance.get('Tags', []):
            if tag['Key'] == 'Name':
                return tag['Value']
        return instance['InstanceId']

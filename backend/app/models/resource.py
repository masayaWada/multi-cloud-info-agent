from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Resource:
    """
    クラウドリソースのデータモデル
    """
    id: str
    name: str
    type: str
    provider: str  # 'aws' or 'azure'
    region: str
    status: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換
        """
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'provider': self.provider,
            'region': self.region,
            'status': self.status,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """
        辞書からインスタンスを作成
        """
        return cls(
            id=data['id'],
            name=data['name'],
            type=data['type'],
            provider=data['provider'],
            region=data['region'],
            status=data['status'],
            metadata=data.get('metadata')
        )

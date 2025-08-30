from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Message:
    """
    チャットメッセージのデータモデル
    """
    id: str
    content: str
    sender: str  # 'user' or 'bot'
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換
        """
        return {
            'id': self.id,
            'content': self.content,
            'sender': self.sender,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """
        辞書からインスタンスを作成
        """
        return cls(
            id=data['id'],
            content=data['content'],
            sender=data['sender'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata')
        )

# Multi-Cloud Info Agent API 仕様書

## 概要

Multi-Cloud Info Agent は、AWS と Azure のリソース情報を自然言語で取得・閲覧するための REST API を提供します。
**注意: すべての回答は日本語で提供されます。**

## ベースURL

```
http://localhost:5000
```

## 認証

現在のバージョンでは認証は実装されていません。将来的には API キーまたは JWT トークンによる認証を追加予定です。

## エンドポイント

### 1. ヘルスチェック

#### GET /health

サーバーの状態を確認します。

**レスポンス:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. チャット機能

#### POST /api/chat

自然言語でクラウドリソースに関する質問を送信し、回答を受け取ります。

**リクエスト:**

```json
{
  "message": "EC2インスタンス一覧を教えて"
}
```

**レスポンス:**

```json
{
  "response": "AWS EC2 リソース一覧:\n\n- web-server-01: running\n- db-server-01: stopped\n...",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**注意:** すべての回答は日本語で提供されます。

**エラーレスポンス:**

```json
{
  "error": "内部サーバーエラーが発生しました",
  "details": "エラーの詳細"
}
```

### 3. AWS リソース取得

#### GET /api/resources/aws

AWS リソースの一覧を取得します。

**クエリパラメータ:**

- `type` (optional): リソースタイプ (`ec2`, `s3`, `rds`)

**例:**

```
GET /api/resources/aws?type=ec2
```

**レスポンス:**

```json
{
  "resources": [
    {
      "id": "i-1234567890abcdef0",
      "name": "web-server-01",
      "type": "t3.micro",
      "state": "running",
      "region": "us-east-1",
      "launch_time": "2024-01-01T00:00:00Z",
      "public_ip": "203.0.113.1",
      "private_ip": "10.0.1.100"
    }
  ],
  "type": "ec2",
  "count": 1
}
```

### 4. Azure リソース取得

#### GET /api/resources/azure

Azure リソースの一覧を取得します。

**クエリパラメータ:**

- `type` (optional): リソースタイプ (`vm`, `storage`)

**例:**

```
GET /api/resources/azure?type=vm
```

**レスポンス:**

```json
{
  "resources": [
    {
      "id": "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/myRG/providers/Microsoft.Compute/virtualMachines/myVM",
      "name": "myVM",
      "location": "Japan East",
      "status": "Succeeded",
      "size": "Standard_B1s",
      "os_type": "Linux"
    }
  ],
  "type": "vm",
  "count": 1
}
```

### 5. ログ取得

#### GET /api/logs

クラウドサービスのログを取得します。

**クエリパラメータ:**

- `provider` (required): クラウドプロバイダー (`aws`, `azure`)
- `service` (optional): サービス名

**例:**

```
GET /api/logs?provider=aws&service=ec2
```

**レスポンス:**

```json
{
  "logs": [
    {
      "timestamp": 1704067200000,
      "message": "Instance i-1234567890abcdef0 started successfully",
      "log_group": "/aws/ec2/instances",
      "log_stream": "i-1234567890abcdef0"
    }
  ],
  "provider": "aws",
  "service": "ec2"
}
```

## エラーコード

| コード | 説明                 |
| ------ | -------------------- |
| 400    | リクエストが不正です |
| 500    | 内部サーバーエラー   |

## 使用例

### cURL での使用例

```bash
# ヘルスチェック
curl http://localhost:5000/health

# チャット機能
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "EC2インスタンス一覧を教えて"}'

# AWS EC2 リソース取得
curl "http://localhost:5000/api/resources/aws?type=ec2"

# Azure VM リソース取得
curl "http://localhost:5000/api/resources/azure?type=vm"

# AWS ログ取得
curl "http://localhost:5000/api/logs?provider=aws&service=ec2"
```

### JavaScript での使用例

```javascript
// チャット機能
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'EC2インスタンス一覧を教えて'
  })
});

const data = await response.json();
console.log(data.response);
```

## 制限事項

- 現在は読み取り専用の操作のみサポート
- リソース一覧は最大10件まで表示
- ログは最大20件まで取得
- 認証機能は未実装

## 今後の予定

- 認証機能の追加
- より多くのリソースタイプのサポート
- リアルタイム通知機能
- ログのフィルタリング機能

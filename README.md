# Multi-Cloud Info Agent

AWS と Azure のリソース情報を自然言語で取得・閲覧するための Web アプリケーションです。

## 🌟 特徴

- **自然言語インターフェース**: チャット形式でクラウドリソースに関する質問が可能
- **マルチクラウド対応**: AWS と Azure の両方のリソースを統一的に管理
- **読み取り専用**: 安全性を重視し、リソースの変更は一切行いません
- **アバター付きUI**: 親しみやすいチャットインターフェース
- **リアルタイム応答**: タイプライター風の表示でスムーズな体験

## 🏗️ アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Cloud APIs     │
│   (React)       │◄──►│   (Flask)       │◄──►│  (AWS/Azure)    │
│                 │    │                 │    │                 │
│ - Chat UI       │    │ - REST API      │    │ - EC2, S3, RDS  │
│ - Avatar        │    │ - LLM Service   │    │ - VM, Storage   │
│ - Real-time     │    │ - MCP Service   │    │ - CloudWatch    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 クイックスタート

### 前提条件

- Python 3.8 以上
- Node.js 16 以上
- AWS CLI (AWS リソースアクセス用)
- Azure CLI (Azure リソースアクセス用)

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd multi-cloud-info-agent
```

### 2. 開発環境のセットアップ

```bash
make setup-dev
```

### 3. 環境変数の設定

`env.example` を `.env` にコピーして、実際の値を設定してください：

```bash
cp env.example .env
```

### 4. アプリケーションの起動

```bash
make start
```

- フロントエンド: http://localhost:3000
- バックエンド: http://localhost:5000

## 📖 使用方法

### 基本的な質問例

- "EC2インスタンス一覧を教えて"
- "Azure VM の状態を確認して"
- "最近のエラーログを見せて"
- "S3バケットの一覧を表示して"

### 利用可能なリソースタイプ

#### AWS
- EC2 インスタンス
- S3 バケット
- RDS インスタンス
- CloudWatch ログ

#### Azure
- 仮想マシン
- ストレージアカウント
- ログ分析

## 🛠️ 開発

### プロジェクト構成

```
├── frontend/          # React アプリケーション
│   ├── src/          # コンポーネントやユーティリティ
│   └── public/       # HTML テンプレートや静的ファイル
├── backend/          # Python / Flask アプリケーション
│   └── app/          # Flask アプリケーションのエントリポイント
├── docs/             # 要件定義や設計資料、API 仕様書
├── tests/            # ユニットテストおよび統合テスト
└── README.md         # プロジェクトの説明
```

### 開発コマンド

```bash
# 依存関係のインストール
make install

# アプリケーションの起動
make start

# テストの実行
make test

# コードの品質チェック
make lint

# コードのフォーマット
make format

# 一時ファイルの削除
make clean
```

### テスト

```bash
# バックエンドテスト
cd backend
source venv/bin/activate
pytest tests/ -v

# フロントエンドテスト
cd frontend
npm test
```

## 🔧 設定

### 環境変数

| 変数名                  | 説明                           | 必須 |
| ----------------------- | ------------------------------ | ---- |
| `OPENAI_API_KEY`        | OpenAI API キー                | Yes  |
| `AWS_ACCESS_KEY_ID`     | AWS アクセスキー               | Yes  |
| `AWS_SECRET_ACCESS_KEY` | AWS シークレットキー           | Yes  |
| `AWS_DEFAULT_REGION`    | AWS デフォルトリージョン       | No   |
| `AZURE_CLIENT_ID`       | Azure クライアントID           | Yes  |
| `AZURE_CLIENT_SECRET`   | Azure クライアントシークレット | Yes  |
| `AZURE_TENANT_ID`       | Azure テナントID               | Yes  |
| `AZURE_SUBSCRIPTION_ID` | Azure サブスクリプションID     | Yes  |

### 認証設定

#### AWS
```bash
aws configure
```

#### Azure
```bash
az login
```

## 🐳 Docker での実行

```bash
# Docker イメージのビルド
make build

# アプリケーションの起動
docker-compose up -d

# ログの確認
docker-compose logs -f
```

## 📚 API ドキュメント

詳細な API 仕様については、[API仕様書](docs/API仕様書.md) を参照してください。

### 主要エンドポイント

- `GET /health` - ヘルスチェック
- `POST /api/chat` - チャット機能
- `GET /api/resources/aws` - AWS リソース取得
- `GET /api/resources/azure` - Azure リソース取得
- `GET /api/logs` - ログ取得

## 🔒 セキュリティ

- **読み取り専用**: リソースの変更操作は一切行いません
- **最小権限**: 必要最小限の権限のみを付与
- **ログ記録**: 全操作の監査ログを記録
- **認証**: 適切な認証情報の管理

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

### 開発ルール

- コードレビューは必須
- テストの追加を推奨
- ドキュメントの更新
- セキュリティの確認

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🆘 サポート

問題が発生した場合は、以下の情報を含めて報告してください：

- エラーメッセージ
- 実行環境（OS、Python バージョン、Node.js バージョン）
- 設定ファイルの内容（機密情報を除く）
- 実行したコマンド

## 🗺️ ロードマップ

### 短期目標
- [ ] 認証機能の追加
- [ ] より多くのリソースタイプのサポート
- [ ] ログのフィルタリング機能

### 長期目標
- [ ] Google Cloud Platform の対応
- [ ] リアルタイム通知機能
- [ ] ダッシュボード機能
- [ ] マルチリージョン対応

## 📊 技術スタック

### フロントエンド
- React 18
- Styled Components
- Framer Motion
- React Markdown
- Axios

### バックエンド
- Python 3.11
- Flask
- OpenAI API
- Boto3 (AWS SDK)
- Azure SDK

### インフラ
- Docker
- Docker Compose
- Nginx
- Redis

---

**注意**: このアプリケーションは読み取り専用の操作のみをサポートします。リソースの作成、更新、削除は一切行いません。

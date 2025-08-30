# Multi-Cloud Info Agent Makefile

.PHONY: help install start stop test clean build deploy

# デフォルトターゲット
help:
	@echo "Multi-Cloud Info Agent - 利用可能なコマンド:"
	@echo ""
	@echo "  install     - 依存関係をインストール"
	@echo "  start       - アプリケーションを起動"
	@echo "  stop        - アプリケーションを停止"
	@echo "  test        - テストを実行"
	@echo "  clean       - 一時ファイルを削除"
	@echo "  build       - Docker イメージをビルド"
	@echo "  deploy      - 本番環境にデプロイ"
	@echo ""

# 依存関係のインストール
install:
	@echo "依存関係をインストール中..."
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
	@echo "インストール完了"

# アプリケーションの起動
start:
	@echo "アプリケーションを起動中..."
	@echo "バックエンドを起動中..."
	cd backend && source venv/bin/activate && python run.py &
	@echo "フロントエンドを起動中..."
	cd frontend && npm start &
	@echo "アプリケーションが起動しました"
	@echo "フロントエンド: http://localhost:3000"
	@echo "バックエンド: http://localhost:5000"

# アプリケーションの停止
stop:
	@echo "アプリケーションを停止中..."
	pkill -f "python run.py"
	pkill -f "npm start"
	@echo "アプリケーションを停止しました"

# テストの実行
test:
	@echo "テストを実行中..."
	@echo "バックエンドテストを実行中..."
	cd backend && source venv/bin/activate && pytest tests/ -v
	@echo "フロントエンドテストを実行中..."
	cd frontend && npm test -- --coverage --watchAll=false
	@echo "テスト完了"

# 一時ファイルの削除
clean:
	@echo "一時ファイルを削除中..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf backend/venv
	rm -rf frontend/node_modules
	rm -rf frontend/build
	rm -rf logs/*.log
	@echo "クリーンアップ完了"

# Docker イメージのビルド
build:
	@echo "Docker イメージをビルド中..."
	docker-compose build
	@echo "ビルド完了"

# 本番環境へのデプロイ
deploy:
	@echo "本番環境にデプロイ中..."
	docker-compose -f docker-compose.prod.yml up -d
	@echo "デプロイ完了"

# 開発環境のセットアップ
setup-dev:
	@echo "開発環境をセットアップ中..."
	cp env.example .env
	@echo "環境変数ファイルを作成しました。.env ファイルを編集してください。"
	make install
	@echo "開発環境のセットアップ完了"

# コードの品質チェック
lint:
	@echo "コードの品質チェックを実行中..."
	@echo "Python コードをチェック中..."
	cd backend && source venv/bin/activate && flake8 app/ tests/
	cd backend && source venv/bin/activate && black --check app/ tests/
	@echo "JavaScript コードをチェック中..."
	cd frontend && npm run lint
	@echo "品質チェック完了"

# コードのフォーマット
format:
	@echo "コードをフォーマット中..."
	cd backend && source venv/bin/activate && black app/ tests/
	cd frontend && npm run format
	@echo "フォーマット完了"

# ログの確認
logs:
	@echo "アプリケーションログを表示中..."
	tail -f logs/app.log

# データベースのマイグレーション（将来の拡張用）
migrate:
	@echo "データベースマイグレーションを実行中..."
	@echo "現在はデータベースを使用していません"

# バックアップの作成
backup:
	@echo "バックアップを作成中..."
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude=node_modules \
		--exclude=venv \
		--exclude=.git \
		--exclude=logs \
		.
	@echo "バックアップ完了"

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# 環境変数を読み込み
load_dotenv()


def create_app():
    app = Flask(__name__)

    # CORS設定
    CORS(app, origins=["http://localhost:3000"])

    # 設定
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    app.config['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
    app.config['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
    app.config['AWS_DEFAULT_REGION'] = os.getenv(
        'AWS_DEFAULT_REGION', 'us-east-1')
    app.config['AZURE_CLIENT_ID'] = os.getenv('AZURE_CLIENT_ID')
    app.config['AZURE_CLIENT_SECRET'] = os.getenv('AZURE_CLIENT_SECRET')
    app.config['AZURE_TENANT_ID'] = os.getenv('AZURE_TENANT_ID')
    app.config['AZURE_SUBSCRIPTION_ID'] = os.getenv('AZURE_SUBSCRIPTION_ID')

    # ブループリント登録
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

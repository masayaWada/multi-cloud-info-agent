#!/usr/bin/env python3
"""
Multi-Cloud Info Agent アプリケーションのエントリーポイント
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # 環境変数から設定を取得
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"Multi-Cloud Info Agent を起動中...")
    print(f"ホスト: {host}")
    print(f"ポート: {port}")
    print(f"デバッグモード: {debug}")

    app.run(host=host, port=port, debug=debug)

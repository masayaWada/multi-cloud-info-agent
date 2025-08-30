import logging
import os
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    ロガーを取得・設定
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # ログレベルを設定
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        logger.setLevel(getattr(logging, log_level.upper()))

        # フォーマッターを設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # コンソールハンドラーを追加
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # ファイルハンドラーを追加（オプション）
        log_file = os.getenv('LOG_FILE')
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

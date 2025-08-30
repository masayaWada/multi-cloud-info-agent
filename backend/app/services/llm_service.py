import os
from typing import Optional
from openai import OpenAI
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """
        OpenAI クライアントを初期化
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY が設定されていません")
            return

        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI クライアントが初期化されました")
        except Exception as e:
            logger.error(f"OpenAI クライアントの初期化に失敗: {str(e)}")

    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        LLMを使用してレスポンスを生成
        """
        if not self.client:
            return "LLMサービスが利用できません。APIキーを確認してください。"

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたはAWSとAzureのクラウドインフラに精通した専門家です。ユーザーの質問に対して、正確で実用的な回答を日本語で提供してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM レスポンス生成エラー: {str(e)}")
            return f"レスポンス生成中にエラーが発生しました: {str(e)}"

    def analyze_user_intent(self, user_message: str) -> dict:
        """
        ユーザーメッセージの意図を解析
        """
        prompt = f"""
        以下のユーザーメッセージを解析し、意図を特定してください。
        
        メッセージ: {user_message}
        
        以下の形式でJSONを返してください:
        {{
            "type": "resource_list|log_query|metric_query|general_question",
            "provider": "aws|azure|both",
            "service": "ec2|s3|vm|storage|etc",
            "confidence": 0.0-1.0,
            "parameters": {{}}
        }}
        
        利用可能なタイプ:
        - resource_list: リソース一覧の取得
        - log_query: ログの検索・参照
        - metric_query: メトリクスの取得
        - general_question: 一般的な質問
        """

        response = self.generate_response(prompt, max_tokens=200)

        try:
            import json
            # JSONレスポンスを抽出
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"意図解析のJSONパースエラー: {str(e)}")

        # デフォルトの意図を返す
        return {
            "type": "general_question",
            "provider": "both",
            "service": "unknown",
            "confidence": 0.5,
            "parameters": {}
        }

    def format_resource_response(self, resources: list, provider: str, service: str) -> str:
        """
        リソース情報を読みやすい形式にフォーマット
        """
        if not resources:
            return f"{provider.upper()} {service.upper()} のリソースが見つかりませんでした。"

        response = f"## {provider.upper()} {service.upper()} リソース一覧\n\n"
        response += f"合計 {len(resources)} 件のリソースが見つかりました。\n\n"

        for i, resource in enumerate(resources[:10], 1):  # 最初の10件のみ表示
            response += f"### {i}. {resource.get('name', 'N/A')}\n"
            response += f"- **状態**: {resource.get('state', 'N/A')}\n"
            response += f"- **タイプ**: {resource.get('type', 'N/A')}\n"
            if resource.get('region'):
                response += f"- **リージョン**: {resource.get('region')}\n"
            response += "\n"

        if len(resources) > 10:
            response += f"... 他 {len(resources) - 10} 件\n"

        return response

    def format_log_response(self, logs: list, provider: str, service: str) -> str:
        """
        ログ情報を読みやすい形式にフォーマット
        """
        if not logs:
            return f"{provider.upper()} {service.upper()} のログが見つかりませんでした。"

        response = f"## {provider.upper()} {service.upper()} ログ\n\n"
        response += f"最新 {len(logs)} 件のログエントリ:\n\n"

        for log in logs[:5]:  # 最初の5件のみ表示
            response += f"**{log.get('timestamp', 'N/A')}**\n"
            response += f"```\n{log.get('message', 'N/A')}\n```\n\n"

        return response

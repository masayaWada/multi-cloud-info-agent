import os
import json
import re
from typing import Optional, Dict, Any
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 条件付きインポート
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama がインストールされていません。ローカルLLM機能は利用できません。")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI がインストールされていません。クラウドLLM機能は利用できません。")


class LLMService:
    def __init__(self):
        self.llm_type = os.getenv('LLM_TYPE', 'ollama')  # 'ollama' or 'openai'
        self.ollama_client = None
        self.openai_client = None
        self.model_name = os.getenv('LLM_MODEL', 'llama2')
        self._initialize_client()

    def _initialize_client(self):
        """
        LLM クライアントを初期化
        """
        if self.llm_type == 'ollama' and OLLAMA_AVAILABLE:
            self._initialize_ollama()
        elif self.llm_type == 'openai' and OPENAI_AVAILABLE:
            self._initialize_openai()
        else:
            logger.error(f"指定されたLLMタイプ '{self.llm_type}' は利用できません")

    def _initialize_ollama(self):
        """
        Ollama クライアントを初期化
        """
        try:
            self.ollama_client = ollama.Client(
                host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
            # モデルの存在確認
            models = self.ollama_client.list()
            model_names = [model['name'] for model in models['models']]

            if self.model_name not in model_names:
                logger.warning(
                    f"モデル '{self.model_name}' が見つかりません。利用可能なモデル: {model_names}")
                if model_names:
                    self.model_name = model_names[0]
                    logger.info(f"デフォルトモデル '{self.model_name}' を使用します")
                else:
                    logger.error("利用可能なモデルがありません。Ollamaでモデルをプルしてください。")
                    return

            logger.info(f"Ollama クライアントが初期化されました (モデル: {self.model_name})")
        except Exception as e:
            logger.error(f"Ollama クライアントの初期化に失敗: {str(e)}")

    def _initialize_openai(self):
        """
        OpenAI クライアントを初期化
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("OPENAI_API_KEY が設定されていません")
            return

        try:
            self.openai_client = OpenAI(api_key=api_key)
            logger.info("OpenAI クライアントが初期化されました")
        except Exception as e:
            logger.error(f"OpenAI クライアントの初期化に失敗: {str(e)}")

    def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        LLMを使用してレスポンスを生成
        """
        system_prompt = "あなたはAWSとAzureのクラウドインフラに精通した専門家です。ユーザーの質問に対して、正確で実用的な回答を日本語で提供してください。"

        if self.llm_type == 'ollama' and self.ollama_client:
            return self._generate_ollama_response(system_prompt, prompt, max_tokens)
        elif self.llm_type == 'openai' and self.openai_client:
            return self._generate_openai_response(system_prompt, prompt, max_tokens)
        else:
            return "LLMサービスが利用できません。設定を確認してください。"

    def _generate_ollama_response(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        Ollamaを使用してレスポンスを生成
        """
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                options={
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            )
            return response['message']['content']

        except Exception as e:
            logger.error(f"Ollama レスポンス生成エラー: {str(e)}")
            return f"レスポンス生成中にエラーが発生しました: {str(e)}"

    def _generate_openai_response(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """
        OpenAIを使用してレスポンスを生成
        """
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI レスポンス生成エラー: {str(e)}")
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

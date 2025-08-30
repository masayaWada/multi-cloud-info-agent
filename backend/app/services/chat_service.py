import re
from typing import Dict, List, Any
from app.services.llm_service import LLMService
from app.services.mcp_service import MCPService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    def __init__(self):
        self.llm_service = LLMService()
        self.mcp_service = MCPService()

    def process_message(self, user_message: str) -> str:
        """
        ユーザーメッセージを処理し、適切な応答を生成する
        """
        try:
            # メッセージを解析して意図を特定
            intent = self._analyze_intent(user_message)
            logger.info(f"解析された意図: {intent}")

            # 意図に基づいて適切な処理を実行
            if intent['type'] == 'resource_list':
                return self._handle_resource_list_request(intent)
            elif intent['type'] == 'log_query':
                return self._handle_log_query(intent)
            elif intent['type'] == 'metric_query':
                return self._handle_metric_query(intent)
            elif intent['type'] == 'general_question':
                return self._handle_general_question(user_message)
            else:
                return self._handle_unknown_request(user_message)

        except Exception as e:
            logger.error(f"メッセージ処理エラー: {str(e)}")
            return "申し訳ございません。処理中にエラーが発生しました。"

    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        LLMを使用してメッセージの意図を解析する
        """
        prompt = f"""
        以下のユーザーメッセージを解析し、意図を特定してください。
        
        メッセージ: {message}
        
        以下の形式でJSONを返してください:
        {{
            "type": "resource_list|log_query|metric_query|general_question",
            "provider": "aws|azure|both",
            "service": "ec2|s3|vm|storage|etc",
            "parameters": {{}}
        }}
        
        利用可能なタイプ:
        - resource_list: リソース一覧の取得
        - log_query: ログの検索・参照
        - metric_query: メトリクスの取得
        - general_question: 一般的な質問
        """

        response = self.llm_service.generate_response(prompt)

        # JSONレスポンスをパース
        try:
            import json
            intent = json.loads(response)
            return intent
        except:
            # パースに失敗した場合はデフォルトの意図を返す
            return {
                "type": "general_question",
                "provider": "both",
                "service": "unknown",
                "parameters": {}
            }

    def _handle_resource_list_request(self, intent: Dict[str, Any]) -> str:
        """
        リソース一覧取得リクエストを処理
        """
        provider = intent.get('provider', 'aws')
        service = intent.get('service', 'ec2')

        try:
            if provider in ['aws', 'both']:
                resources = self.mcp_service.get_aws_resources(service)
                aws_response = f"AWS {service.upper()} リソース一覧:\n\n"
                for resource in resources[:10]:  # 最初の10件のみ表示
                    aws_response += f"- {resource.get('name', 'N/A')}: {resource.get('state', 'N/A')}\n"

                if provider == 'aws':
                    return aws_response

            if provider in ['azure', 'both']:
                resources = self.mcp_service.get_azure_resources(service)
                azure_response = f"Azure {service.upper()} リソース一覧:\n\n"
                for resource in resources[:10]:  # 最初の10件のみ表示
                    azure_response += f"- {resource.get('name', 'N/A')}: {resource.get('state', 'N/A')}\n"

                if provider == 'azure':
                    return azure_response
                elif provider == 'both':
                    return aws_response + "\n\n" + azure_response

        except Exception as e:
            logger.error(f"リソース一覧取得エラー: {str(e)}")
            return f"リソース一覧の取得中にエラーが発生しました: {str(e)}"

    def _handle_log_query(self, intent: Dict[str, Any]) -> str:
        """
        ログクエリを処理
        """
        provider = intent.get('provider', 'aws')
        service = intent.get('service', 'ec2')

        try:
            logs = self.mcp_service.get_logs(provider, service)
            response = f"{provider.upper()} {service.upper()} のログ:\n\n"

            for log in logs[:5]:  # 最初の5件のみ表示
                response += f"**{log.get('timestamp', 'N/A')}**\n"
                response += f"{log.get('message', 'N/A')}\n\n"

            return response

        except Exception as e:
            logger.error(f"ログ取得エラー: {str(e)}")
            return f"ログの取得中にエラーが発生しました: {str(e)}"

    def _handle_metric_query(self, intent: Dict[str, Any]) -> str:
        """
        メトリクスクエリを処理
        """
        # メトリクス取得の実装
        return "メトリクス取得機能は現在開発中です。"

    def _handle_general_question(self, message: str) -> str:
        """
        一般的な質問を処理
        """
        prompt = f"""
        以下の質問に、AWSやAzureのクラウドインフラに関する専門的な観点から回答してください。
        
        質問: {message}
        
        回答は日本語で、分かりやすく、実用的な内容にしてください。
        """

        return self.llm_service.generate_response(prompt)

    def _handle_unknown_request(self, message: str) -> str:
        """
        未知のリクエストを処理
        """
        return f"申し訳ございませんが、「{message}」というリクエストを理解できませんでした。\n\n利用可能な機能:\n- リソース一覧の取得（例：「EC2インスタンス一覧を教えて」）\n- ログの確認（例：「最近のエラーログを見せて」）\n- 一般的な質問（例：「AWSの料金について教えて」）"

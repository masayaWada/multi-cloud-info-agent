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
            elif intent['type'] == 'iam_policy_creation':
                return self._handle_iam_policy_creation(user_message, intent)
            elif intent['type'] == 'general_question':
                return self._handle_general_question(user_message)
            else:
                return self._handle_unknown_request(user_message)

        except Exception as e:
            logger.error(f"メッセージ処理エラー: {str(e)}")
            return "申し訳ございません。処理中にエラーが発生しました。"

    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        メッセージの意図を解析する（キーワードベース + LLM補完）
        """
        # キーワードベースの意図解析
        intent = self._analyze_intent_by_keywords(message)

        # LLMによる補完解析（必要に応じて）
        if intent['confidence'] < 0.8:
            llm_intent = self._analyze_intent_by_llm(message)
            if llm_intent['confidence'] > intent['confidence']:
                intent = llm_intent

        return intent

    def _analyze_intent_by_keywords(self, message: str) -> Dict[str, Any]:
        """
        キーワードベースで意図を解析
        """
        message_lower = message.lower()

        # IAMポリシー作成の検出
        if any(keyword in message_lower for keyword in ['iam', 'ポリシー', 'policy', '権限', 'permission']):
            if any(keyword in message_lower for keyword in ['作成', 'create', 'json', '形式']):
                return {
                    "type": "iam_policy_creation",
                    "provider": "aws",
                    "service": "iam",
                    "confidence": 0.9,
                    "parameters": {
                        "action": "create_policy",
                        "format": "json" if "json" in message_lower else "text"
                    }
                }

        # リソース一覧取得の検出
        if any(keyword in message_lower for keyword in ['一覧', 'list', 'すべて', 'all', 'バケット', 'bucket']):
            if 's3' in message_lower:
                return {
                    "type": "resource_list",
                    "provider": "aws",
                    "service": "s3",
                    "confidence": 0.9,
                    "parameters": {}
                }
            elif 'ec2' in message_lower:
                return {
                    "type": "resource_list",
                    "provider": "aws",
                    "service": "ec2",
                    "confidence": 0.9,
                    "parameters": {}
                }

        # ログクエリの検出
        if any(keyword in message_lower for keyword in ['ログ', 'log', 'エラー', 'error']):
            return {
                "type": "log_query",
                "provider": "both",
                "service": "unknown",
                "confidence": 0.8,
                "parameters": {}
            }

        # デフォルト
        return {
            "type": "general_question",
            "provider": "both",
            "service": "unknown",
            "confidence": 0.5,
            "parameters": {}
        }

    def _analyze_intent_by_llm(self, message: str) -> Dict[str, Any]:
        """
        LLMを使用してメッセージの意図を解析する
        """
        prompt = f"""
        以下のユーザーメッセージを解析し、意図を特定してください。
        
        メッセージ: {message}
        
        以下の形式でJSONを返してください:
        {{
            "type": "resource_list|log_query|metric_query|general_question|iam_policy_creation",
            "provider": "aws|azure|both",
            "service": "ec2|s3|vm|storage|iam|etc",
            "confidence": 0.0-1.0,
            "parameters": {{}}
        }}
        
        利用可能なタイプ:
        - resource_list: リソース一覧の取得
        - log_query: ログの検索・参照
        - metric_query: メトリクスの取得
        - iam_policy_creation: IAMポリシーの作成
        - general_question: 一般的な質問
        """

        response = self.llm_service.generate_response(prompt, max_tokens=200)

        # JSONレスポンスをパース
        try:
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                intent = json.loads(json_match.group())
                return intent
        except Exception as e:
            logger.error(f"LLM意図解析のJSONパースエラー: {str(e)}")

        # パースに失敗した場合はデフォルトの意図を返す
        return {
            "type": "general_question",
            "provider": "both",
            "service": "unknown",
            "confidence": 0.3,
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
            return "申し訳ございません。リソース一覧の取得中にエラーが発生しました。"

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
            return "申し訳ございません。ログの取得中にエラーが発生しました。"

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

    def _handle_iam_policy_creation(self, message: str, intent: Dict[str, Any]) -> str:
        """
        IAMポリシー作成リクエストを処理
        """
        # テンプレートベースのIAMポリシー生成
        if intent.get('parameters', {}).get('format') == 'json':
            return self._generate_iam_policy_json(message)
        else:
            return self._generate_iam_policy_explanation(message)

    def _generate_iam_policy_json(self, message: str) -> str:
        """
        IAMポリシーをJSON形式で生成
        """
        # メッセージから要件を解析
        message_lower = message.lower()

        # 読み取り専用 + サポートリクエストのポリシー
        if '参照' in message_lower or 'read' in message_lower:
            if 'サポート' in message_lower or 'support' in message_lower:
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "ReadOnlyAccess",
                            "Effect": "Allow",
                            "Action": [
                                "iam:Get*",
                                "iam:List*",
                                "iam:Describe*",
                                "ec2:Describe*",
                                "s3:Get*",
                                "s3:List*",
                                "rds:Describe*",
                                "lambda:Get*",
                                "lambda:List*",
                                "cloudformation:Describe*",
                                "cloudformation:Get*",
                                "cloudformation:List*",
                                "cloudwatch:Get*",
                                "cloudwatch:List*",
                                "cloudwatch:Describe*"
                            ],
                            "Resource": "*"
                        },
                        {
                            "Sid": "SupportAccess",
                            "Effect": "Allow",
                            "Action": [
                                "support:*"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            else:
                # 読み取り専用のみ
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "ReadOnlyAccess",
                            "Effect": "Allow",
                            "Action": [
                                "iam:Get*",
                                "iam:List*",
                                "iam:Describe*",
                                "ec2:Describe*",
                                "s3:Get*",
                                "s3:List*",
                                "rds:Describe*",
                                "lambda:Get*",
                                "lambda:List*",
                                "cloudformation:Describe*",
                                "cloudformation:Get*",
                                "cloudformation:List*",
                                "cloudwatch:Get*",
                                "cloudwatch:List*",
                                "cloudwatch:Describe*"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
        else:
            # デフォルトの読み取り専用ポリシー
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "ReadOnlyAccess",
                        "Effect": "Allow",
                        "Action": [
                            "iam:Get*",
                            "iam:List*",
                            "ec2:Describe*",
                            "s3:Get*",
                            "s3:List*"
                        ],
                        "Resource": "*"
                    }
                ]
            }

        import json
        return f"""## AWS IAMポリシー（JSON形式）

以下のIAMポリシーは、すべてのリソースに対する読み取り権限とサポートリクエスト権限を提供します：

```json
{json.dumps(policy, indent=2, ensure_ascii=False)}
```

### 使用方法
1. AWS IAMコンソールにアクセス
2. 「ポリシー」→「ポリシーの作成」を選択
3. 上記のJSONをコピー&ペースト
4. ポリシー名を設定して保存
5. ユーザーまたはロールにポリシーをアタッチ

### 注意事項
- このポリシーは読み取り専用アクセスを提供します
- リソースの作成、変更、削除はできません
- サポートリクエストの作成が可能です"""

    def _generate_iam_policy_explanation(self, message: str) -> str:
        """
        IAMポリシーの説明を生成
        """
        return """## AWS IAMポリシー作成について

### 読み取り専用 + サポートリクエスト権限のポリシー

このポリシーは以下の権限を提供します：

#### 読み取り権限
- **IAM**: ユーザー、ロール、ポリシーの参照
- **EC2**: インスタンス、セキュリティグループ、VPCの参照
- **S3**: バケットとオブジェクトの参照
- **RDS**: データベースインスタンスの参照
- **Lambda**: 関数の参照
- **CloudFormation**: スタックの参照
- **CloudWatch**: メトリクスとログの参照

#### サポート権限
- サポートケースの作成・更新
- サポートドキュメントの参照

### セキュリティのベストプラクティス
1. **最小権限の原則**: 必要最小限の権限のみを付与
2. **定期的な見直し**: ポリシーの定期的な監査
3. **条件付きアクセス**: IPアドレスや時間による制限
4. **MFAの強制**: 多要素認証の有効化

JSON形式のポリシーが必要な場合は、「JSON形式で出力してください」とお伝えください。"""

    def _handle_unknown_request(self, message: str) -> str:
        """
        未知のリクエストを処理
        """
        return f"申し訳ございませんが、「{message}」というリクエストを理解できませんでした。\n\n利用可能な機能:\n- リソース一覧の取得（例：「EC2インスタンス一覧を教えて」）\n- ログの確認（例：「最近のエラーログを見せて」）\n- IAMポリシーの作成（例：「読み取り専用のIAMポリシーを作成してください」）\n- 一般的な質問（例：「AWSの料金について教えて」）"

import json
import logging
import uuid
from typing import Optional

import boto3

from config import config

logger = logging.getLogger(__name__)

# Simple FAQ responses - in production this would come from a database
FAQ_RESPONSES = {
    "return": "Our return policy allows returns within 30 days of purchase. Please visit the returns portal or contact support@company.com.",
    "refund": "Refunds are processed within 5-7 business days after we receive your return.",
    "shipping": "Standard shipping takes 3-5 days. Express shipping is 1-2 days.",
    "track": "You can track your order using the tracking number in your confirmation email.",
    "cancel": "To cancel an order, please contact us within 1 hour of placing it. After that, we'll process it as a return.",
    "password": "To reset your password, click 'Forgot Password' on the login page and follow the instructions.",
    "account": "For account issues, you can update your info in Account Settings or contact our support team.",
}


def check_faq(question: str) -> Optional[str]:
    """
    Check if the question matches any FAQ topics.
    Simple keyword matching - a real system would use semantic search.
    """
    question_lower = question.lower()
    for keyword, answer in FAQ_RESPONSES.items():
        if keyword in question_lower:
            return answer
    return None


def analyze_sentiment(text: str) -> float:
    """
    Simple sentiment score: positive = closer to 1.0, negative = closer to 0.0.
    Uses keyword counting as a basic approach.
    In production you'd use Comprehend or a sentiment model.
    """
    positive_words = ["great", "good", "thanks", "helpful", "happy", "love", "excellent", "perfect"]
    negative_words = ["bad", "terrible", "awful", "angry", "frustrated", "useless", "hate", "disappointed", "broken", "never"]

    text_lower = text.lower()
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return 0.5  # neutral

    return pos_count / total


class SupportChatbot:
    """
    AI customer support assistant.

    Flow:
    1. Check if question matches a FAQ (instant, no LLM cost)
    2. If not, run sentiment analysis to decide if we need to escalate
    3. If sentiment is very negative, flag for human escalation
    4. Otherwise, use Bedrock to generate a response
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.conversation_history: list[dict] = []

        self.bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )

        logger.info(f"SupportChatbot initialized, session={self.session_id}")

    def respond(self, user_message: str) -> dict:
        """
        Generate a response to the user's message.
        Returns the response along with metadata about how it was handled.
        """
        if not user_message.strip():
            raise ValueError("Message cannot be empty")

        # step 1: check FAQ
        faq_answer = check_faq(user_message)
        if faq_answer:
            self._save_to_history(user_message, faq_answer)
            return {
                "response": faq_answer,
                "session_id": self.session_id,
                "handled_by": "faq",
                "escalate": False,
                "sentiment_score": None,
            }

        # step 2: sentiment analysis
        sentiment_score = analyze_sentiment(user_message)
        should_escalate = sentiment_score < config.sentiment_threshold

        if should_escalate:
            escalation_msg = (
                "I can see you're having a frustrating experience. "
                "Let me connect you with a human agent who can help resolve this right away. "
                "You'll receive a callback within 30 minutes."
            )
            self._save_to_history(user_message, escalation_msg)
            return {
                "response": escalation_msg,
                "session_id": self.session_id,
                "handled_by": "escalation",
                "escalate": True,
                "sentiment_score": round(sentiment_score, 2),
            }

        # step 3: use Bedrock for general questions
        response = self._call_bedrock(user_message)
        self._save_to_history(user_message, response)

        return {
            "response": response,
            "session_id": self.session_id,
            "handled_by": "llm",
            "escalate": False,
            "sentiment_score": round(sentiment_score, 2),
        }

    def _call_bedrock(self, user_message: str) -> str:
        """Call Bedrock to generate a support response."""
        # build context from recent conversation
        history_text = ""
        if self.conversation_history:
            recent = self.conversation_history[-4:]
            history_text = "\n".join(
                f"Customer: {h['user']}\nAgent: {h['agent']}" for h in recent
            )

        prompt = f"""You are a friendly customer support agent for an e-commerce company.
Be helpful, professional, and concise. If you don't know something, say so.

Previous conversation:
{history_text if history_text else "None"}

Customer: {user_message}

Agent:"""

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [{"role": "user", "content": prompt}],
            })
            response = self.bedrock.invoke_model(modelId=config.bedrock_model_id, body=body)
            result = json.loads(response["body"].read())
            return result["content"][0]["text"]
        except Exception as e:
            logger.error(f"Bedrock call failed: {e}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")

    def _save_to_history(self, user_msg: str, agent_msg: str):
        self.conversation_history.append({"user": user_msg, "agent": agent_msg})

    def summarize_conversation(self) -> str:
        """Generate a summary of the current conversation - useful for ticket creation."""
        if not self.conversation_history:
            return "No conversation yet."

        conversation_text = "\n".join(
            f"Customer: {h['user']}\nAgent: {h['agent']}"
            for h in self.conversation_history
        )

        prompt = f"""Summarize this customer support conversation in 2-3 sentences.
Include: main issue, how it was resolved (or if escalated), and customer sentiment.

Conversation:
{conversation_text}

Summary:"""

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": prompt}],
            })
            response = self.bedrock.invoke_model(modelId=config.bedrock_model_id, body=body)
            result = json.loads(response["body"].read())
            return result["content"][0]["text"]
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Could not generate summary."

"""Beanie document models — registered with MongoDB on startup."""

from app.models.apc_config import APCDiscountRule, APCPricingRule, APCWaiverRequest
from app.models.chat_log import ChatLog
from app.models.conversation import Conversation
from app.models.document import Document, DocumentChunk
from app.models.faq import FAQ
from app.models.message import Message
from app.models.notification import Notification
from app.models.policy import PolicySetting, SuggestedQuestion
from app.models.user import RefreshToken, User

ALL_DOCUMENT_MODELS = [
    User,
    RefreshToken,
    Conversation,
    Message,
    Document,
    DocumentChunk,
    APCPricingRule,
    APCDiscountRule,
    APCWaiverRequest,
    FAQ,
    Notification,
    ChatLog,
    SuggestedQuestion,
    PolicySetting,
]

__all__ = [
    "ALL_DOCUMENT_MODELS",
    "User",
    "RefreshToken",
    "Conversation",
    "Message",
    "Document",
    "DocumentChunk",
    "APCPricingRule",
    "APCDiscountRule",
    "APCWaiverRequest",
    "FAQ",
    "Notification",
    "ChatLog",
    "SuggestedQuestion",
    "PolicySetting",
]

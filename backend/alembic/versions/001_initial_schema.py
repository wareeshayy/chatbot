"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2026-06-26

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    user_role = postgresql.ENUM(
        "admin", "author", "reviewer", "reader", name="userrole", create_type=False
    )
    document_category = postgresql.ENUM(
        "author_guidelines", "apc_policy", "editorial_policies", "faq",
        "published_paper", "special_issue", "journal_announcement",
        "call_for_papers", "other", name="documentcategory", create_type=False,
    )
    document_status = postgresql.ENUM(
        "pending", "processing", "indexed", "failed", name="documentstatus", create_type=False
    )
    message_role = postgresql.ENUM(
        "user", "assistant", "system", name="messagerole", create_type=False
    )
    notification_type = postgresql.ENUM(
        "call_for_papers", "special_issue", "journal_announcement", "general",
        name="notificationtype", create_type=False,
    )
    paper_type = postgresql.ENUM(
        "research_article", "review_article", "short_communication", "case_study",
        name="papertype", create_type=False,
    )
    author_category = postgresql.ENUM(
        "regular", "developing_country", "student", "ijaike_member",
        "institutional_partner", name="authorcategory", create_type=False,
    )
    discount_type = postgresql.ENUM("percentage", "fixed", name="discounttype", create_type=False)
    waiver_status = postgresql.ENUM("pending", "approved", "rejected", name="waiverstatus", create_type=False)

    for enum in [
        user_role, document_category, document_status, message_role,
        notification_type, paper_type, author_category, discount_type, waiver_status,
    ]:
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="reader"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_role", "users", ["role"])

    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(500)),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_conversations_user_id", "conversations", ["user_id"])
    op.create_index("idx_conversations_updated_at", "conversations", ["updated_at"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("category", document_category, nullable=False),
        sa.Column("status", document_status, nullable=False, server_default="pending"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("chunk_count", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("indexed_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_documents_category", "documents", ["category"])
    op.create_index("idx_documents_status", "documents", ["status"])
    op.create_index("idx_documents_is_active", "documents", ["is_active"])

    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", message_role, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB()),
        sa.Column("token_count", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("idx_messages_created_at", "messages", ["created_at"])

    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chroma_id", sa.String(255), nullable=False, unique=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("page_number", sa.Integer()),
        sa.Column("section_title", sa.String(500)),
        sa.Column("token_count", sa.Integer()),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("idx_document_chunks_chroma_id", "document_chunks", ["chroma_id"])

    op.create_table(
        "apc_pricing_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("paper_type", paper_type, nullable=False),
        sa.Column("base_rate_per_page", sa.Numeric(10, 2), nullable=False),
        sa.Column("minimum_pages", sa.Integer(), server_default="1"),
        sa.Column("maximum_pages", sa.Integer()),
        sa.Column("flat_fee", sa.Numeric(10, 2)),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date()),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "apc_discount_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("author_category", author_category, nullable=False),
        sa.Column("discount_type", discount_type, nullable=False),
        sa.Column("discount_value", sa.Numeric(10, 2), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("requires_approval", sa.Boolean(), server_default="false"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "apc_waiver_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("author_category", author_category, nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column("status", waiver_status, server_default="pending"),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "faqs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("display_order", sa.Integer(), server_default="0"),
        sa.Column("is_published", sa.Boolean(), server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("type", notification_type, nullable=False),
        sa.Column("link_url", sa.String(1000)),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id")),
        sa.Column("is_published", sa.Boolean(), server_default="false"),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "chat_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("response", sa.Text(), nullable=False),
        sa.Column("citations", postgresql.JSONB()),
        sa.Column("retrieved_chunk_ids", postgresql.JSONB()),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("model_used", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_chat_logs_created_at", "chat_logs", ["created_at"])
    op.create_index("idx_chat_logs_user_id", "chat_logs", ["user_id"])

    op.create_table(
        "suggested_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question", sa.String(500), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("target_role", user_role),
        sa.Column("display_order", sa.Integer(), server_default="0"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
    )

    op.create_table(
        "policy_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(100), nullable=False, unique=True),
        sa.Column("value", postgresql.JSONB(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("policy_settings")
    op.drop_table("suggested_questions")
    op.drop_table("chat_logs")
    op.drop_table("notifications")
    op.drop_table("faqs")
    op.drop_table("apc_waiver_requests")
    op.drop_table("apc_discount_rules")
    op.drop_table("apc_pricing_rules")
    op.drop_table("document_chunks")
    op.drop_table("messages")
    op.drop_table("documents")
    op.drop_table("conversations")
    op.drop_table("refresh_tokens")
    op.drop_table("users")

    for name in [
        "waiverstatus", "discounttype", "authorcategory", "papertype",
        "notificationtype", "messagerole", "documentstatus", "documentcategory", "userrole",
    ]:
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)

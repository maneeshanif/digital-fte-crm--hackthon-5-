# Part 2: The Specialization Phase (Hours 17-40)

## Overview

In this phase, you'll transform your Part 1 prototype into a production-grade Custom Agent. This is where **engineering meets scale** - you'll build real infrastructure, integrate with production APIs, and deploy a system that can run 24/7 handling thousands of customers.

## Your Tech Stack for Part 2

### Backend
- **Language:** Python 3.11+
- **Package Manager:** `uv` (for dependency management)
- **Agent SDK:** OpenAI Agents SDK (`from agents import Agent, Runner`)
- **API Framework:** FastAPI
- **Event Streaming:** Kafka (aiokafka)
- **Async Runtime:** asyncio
- **Database ORM:** SQLAlchemy + Alembic (for migrations)

### Database
- **Platform:** Neon DB (Serverless PostgreSQL)
- **Features:** pgvector extension for semantic search
- **Connection Pool:** asyncpg
- **Migration Tool:** Alembic

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **UI Library:** Tailwind CSS + shadcn/ui components
- **Pages:** 5 pages (support, ticket status, admin dashboard, tickets list, conversation history)
- **Purpose:** Complete Web Support Form + Admin Dashboard (required deliverables)

### Infrastructure
- **Container:** Docker (separate for API and Worker)
- **Orchestration:** Kubernetes
- **Monitoring:** Prometheus + Grafana
- **Logging:** Structured JSON logs

### Channel Integrations
- **Email:** Gmail API + Google Cloud Pub/Sub
- **WhatsApp:** Twilio API
- **Web Form:** Next.js API route

### Architecture Layers
- **Agent Layer:** `src/agent/` - Split agent, tools, prompts, formatter, sentiment
- **Worker Layer:** `src/worker/` - Kafka consumers, ticket processor, response dispatcher
- **Services Layer:** `src/services/` - Business logic (customer, ticket, conversation, metrics services)
- **Database Layer:** `src/database/` - Repositories per table (customer_repo, ticket_repo, message_repo, etc.)
- **API Layer:** `src/api/` - FastAPI with proper route organization
- **Kafka Layer:** `src/kafka/` - Separate producer, consumer, and topics

---

## Production Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PRODUCTION ARCHITECTURE                            │
│                                                                              │
│  CHANNEL INTAKE LAYER                                                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │Gmail Webhook│  │Twilio Webook│  │ Web Form    │                          │
│  │  Handler    │  │  Handler    │  │  Handler    │                          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                          │
│         │                │                │                                  │
│         └────────────────┼────────────────┘                                  │
│                          ▼                                                   │
│  EVENT STREAMING    ┌──────────┐                                            │
│                     │  Kafka   │                                            │
│                     │ (Events) │                                            │
│                     └────┬─────┘                                            │
│                          │                                                   │
│  PROCESSING LAYER        ▼                                                  │
│                    ┌───────────┐     ┌──────────┐                           │
│                    │  Agent    │────▶│ Postgres │                           │
│                    │  Worker   │     │  (State) │                           │
│                    └─────┬─────┘     └──────────┘                           │
│                          │                                                   │
│  RESPONSE LAYER          ▼                                                  │
│         ┌────────────────┼────────────────┐                                 │
│         ▼                ▼                ▼                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │ Gmail API   │  │ Twilio API  │  │  API/Email  │                          │
│  │  (Reply)    │  │  (Reply)    │  │  (Reply)    │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
│                                                                              │
│  INFRASTRUCTURE                                                              │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │                    Kubernetes Cluster                         │           │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                 │           │
│  │  │API Pod │ │Worker 1│ │Worker 2│ │Worker N│  (Auto-Scale)   │           │
│  │  └────────┘ └────────┘ └────────┘ └────────┘                 │           │
│  └──────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Production Folder Structure

### Complete Architecture

This production system follows **layered architecture** with clear separation of concerns:

```
production/
├── src/
│   ├── agent/                          ← Agent brain (OpenAI Agents SDK)
│   ├── channels/                       ← Channel intake handlers
│   ├── worker/                         ← Kafka consumer workers
│   ├── kafka/                          ← Kafka producer + consumer + topics
│   ├── api/                            ← FastAPI application
│   ├── services/                       ← Business logic layer
│   ├── database/                       ← Database layer (repositories)
│   └── core/                           ← Shared utilities
├── migrations/                         ← Alembic migrations
├── frontend/                           ← Next.js (5 pages)
├── tests/                              ← Tests per layer
├── k8s/                               ← Kubernetes manifests
├── docker/                             ← Docker configurations
├── monitoring/                          ← Monitoring setup
└── README.md
```

### Layer Breakdown

| Layer | Pattern | Files | Purpose |
|--------|---------|--------|---------|
| **Agent** | OpenAI Agents SDK | `agent/` | Core agent logic with tools |
| **Worker** | Kafka Consumer Pattern | `worker/` | Consumes events, processes tickets |
| **Services** | Repository Pattern | `services/` | Business logic, CRUD operations |
| **Database** | Repository Pattern | `database/repositories/` | Per-table query functions |
| **API** | Route Organization | `api/routes/` | Organized endpoints |
| **Frontend** | Multi-page App | `frontend/app/` | Support + Admin UI |

---

## Exercise 2.1: Database Schema - Your CRM System (2-3 hours)

### Task: Design PostgreSQL Schema

This database **IS your CRM/ticket management system**. You're building a custom solution that tracks customers, conversations, tickets, and all interactions across channels.

### Why Build Your Own CRM?
- Learn fundamentals of customer data management
- No external CRM integration required
- Full control over schema and queries
- Production-ready for Digital FTE use case

### Create Schema File

#### `database/schema.sql`

```sql
-- =============================================================================
-- CUSTOMER SUCCESS FTE - CRM/TICKET MANAGEMENT SYSTEM (NEON DB)
-- =============================================================================
-- This PostgreSQL schema serves as your complete CRM system for tracking:
-- - Customers (unified across all channels)
-- - Conversations and message history
-- - Support tickets and their lifecycle
-- - Knowledge base for AI responses
-- - Performance metrics and reporting
-- =============================================================================

-- Enable pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- CUSTOMER MANAGEMENT
-- =============================================================================

-- Customers table (unified across channels) - YOUR CUSTOMER DATABASE
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    company VARCHAR(255),
    tier VARCHAR(50) DEFAULT 'free', -- 'free', 'professional', 'enterprise'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Customer identifiers (for cross-channel matching)
CREATE TABLE IF NOT EXISTS customer_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    identifier_type VARCHAR(50) NOT NULL, -- 'email', 'phone', 'whatsapp'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    primary_identifier BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

-- =============================================================================
-- CONVERSATION MANAGEMENT
-- =============================================================================

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    initial_channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'closed', 'escalated'
    sentiment_score DECIMAL(3,2),
    sentiment_trend VARCHAR(20), -- 'improving', 'stable', 'declining'
    resolution_type VARCHAR(50),
    escalated_to VARCHAR(255),
    metadata JSONB DEFAULT '{}'
);

-- Messages table (with channel tracking)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL, -- 'email', 'whatsapp', 'web_form'
    direction VARCHAR(20) NOT NULL, -- 'inbound', 'outbound'
    role VARCHAR(20) NOT NULL, -- 'customer', 'agent', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER,
    tool_calls JSONB DEFAULT '[]',
    channel_message_id VARCHAR(255), -- External ID (Gmail message ID, Twilio SID)
    delivery_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'sent', 'delivered', 'failed'
    delivery_error TEXT
);

-- Tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    ticket_number VARCHAR(50) UNIQUE, -- Human-readable ticket number
    source_channel VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50) DEFAULT 'open', -- 'open', 'in_progress', 'resolved', 'escalated'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    first_response_at TIMESTAMP WITH TIME ZONE,
    sla_target TIMESTAMP WITH TIME ZONE, -- SLA deadline
    metadata JSONB DEFAULT '{}'
);

-- =============================================================================
-- KNOWLEDGE BASE
-- =============================================================================

-- Knowledge base entries
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[], -- Array of tags for filtering
    embedding VECTOR(1536), -- For semantic search (OpenAI embeddings)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0
);

-- =============================================================================
-- CONFIGURATION
-- =============================================================================

-- Channel configurations
CREATE TABLE IF NOT EXISTS channel_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) UNIQUE NOT NULL, -- 'email', 'whatsapp', 'web_form'
    enabled BOOLEAN DEFAULT TRUE,
    config JSONB NOT NULL, -- API keys, webhook URLs, etc.
    response_template TEXT,
    max_response_length INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Escalation rules
CREATE TABLE IF NOT EXISTS escalation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) NOT NULL,
    trigger_conditions JSONB NOT NULL, -- Conditions that trigger escalation
    action JSONB NOT NULL, -- What to do when triggered
    priority INTEGER DEFAULT 1, -- Higher priority = checked first
    enabled BOOLEAN DEFAULT TRUE
);

-- =============================================================================
-- ANALYTICS & MONITORING
-- =============================================================================

-- Agent performance metrics
CREATE TABLE IF NOT EXISTS agent_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL, -- 'response_time', 'escalation_rate', 'sentiment_score', etc.
    metric_value DECIMAL(10,4) NOT NULL,
    channel VARCHAR(50), -- Optional: channel-specific metrics
    dimensions JSONB DEFAULT '{}', -- Additional dimensions for grouping
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily summary metrics
CREATE TABLE IF NOT EXISTS daily_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    channel VARCHAR(50),
    total_conversations INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    avg_response_time_ms DECIMAL(10,2),
    avg_sentiment_score DECIMAL(3,2),
    escalation_count INTEGER DEFAULT 0,
    resolution_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, channel)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Customer indexes
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customer_identifiers_value ON customer_identifiers(identifier_value);

-- Conversation indexes
CREATE INDEX IF NOT EXISTS idx_conversations_customer ON conversations(customer_id);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_channel ON conversations(initial_channel);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at DESC);

-- Message indexes
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at DESC);

-- Ticket indexes
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_channel ON tickets(source_channel);
CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority, created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_number ON tickets(ticket_number);

-- Knowledge base indexes (vector search)
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_tags ON knowledge_base USING GIN(tags);

-- Metrics indexes
CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON agent_metrics(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_metrics_date ON daily_metrics(date);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Update customer updated_at timestamp
CREATE OR REPLACE FUNCTION update_customer_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE FUNCTION update_customer_updated_at();

-- Update ticket updated_at timestamp
CREATE TRIGGER trigger_tickets_updated_at
BEFORE UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION update_customer_updated_at();

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- Insert default channel configurations
INSERT INTO channel_configs (channel, enabled, config, max_response_length)
VALUES
    ('email', TRUE, '{"greeting_style": "formal", "include_signature": true}', 2000),
    ('whatsapp', TRUE, '{"greeting_style": "casual", "emojis_allowed": true}', 1600),
    ('web_form', TRUE, '{"greeting_style": "semi-formal"}', 1000)
ON CONFLICT (channel) DO NOTHING;

-- Insert default escalation rules
INSERT INTO escalation_rules (rule_name, trigger_conditions, action, priority)
VALUES
    ('Negative Sentiment', '{"sentiment_threshold": 0.3, "consecutive_negative": 2}', '{"escalate": true, "priority": "high"}', 1),
    ('Billing Issues', '{"keywords": ["refund", "payment dispute", "pricing negotiation"]}', '{"escalate": true, "assign_to": "billing"}', 2),
    ('Legal/Compliance', '{"keywords": ["legal", "lawyer", "compliance", "HIPAA", "GDPR"]}', '{"escalate": true, "assign_to": "legal"}', 1),
    ('Feature Requests', '{"category": "feature_request"}', '{"escalate": true, "assign_to": "product"}', 3)
ON CONFLICT DO NOTHING;
```

### Setup Neon DB Connection

Create `database/connection.py`:

```python
"""
Neon DB connection pool management
"""

import os
import asyncpg
from typing import Optional

NEON_DB_URL = os.getenv(
    "NEON_DB_URL",
    "postgresql://user:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require"
)

# Connection pool
_pool: Optional[asyncpg.Pool] = None

async def get_db_pool() -> asyncpg.Pool:
    """
    Get or create a connection pool to Neon DB.

    Returns:
        asyncpg.Pool: Database connection pool
    """
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            NEON_DB_URL,
            min_size=5,
            max_size=20,
            command_timeout=60,
            timeout=30
        )

    return _pool

async def close_db_pool():
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
```

### Apply Schema to Neon DB

```bash
# Apply schema to Neon DB
psql $NEON_DB_URL -f database/schema.sql

# Or use uv run with your migration script
uv run alembic upgrade head
```

---

## Database Layer Summary

### Repository Pattern
Each database table has its own repository file with clean CRUD operations:
- `database/repositories/customer_repo.py` — Customer operations
- `database/repositories/ticket_repo.py` — Ticket lifecycle
- `database/repositories/message_repo.py` — Message storage
- `database/repositories/conversation_repo.py` — Conversation management
- `database/repositories/knowledge_repo.py` — Knowledge base queries

### Alembic Migrations

#### Setup Alembic

Initialize Alembic in your project:

```bash
# Initialize Alembic
uv run alembic init migrations

# This creates:
# - migrations/alembic.ini (configuration)
# - migrations/env.py (migration environment)
# - migrations/script.py.mako (migration template)
# - migrations/versions/ (migration files)
```

#### Configure Alembic (`migrations/alembic.ini`)

```ini
# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
timezone = UTC

# max length of characters to apply to the
# "slug" field
truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version location specification; This defaults
# to migrations/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
version_locations = %(here)s/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### Configure Alembic Environment (`migrations/env.py`)

```python
"""Alembic environment configuration."""
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your base and models
from src.database.models import Base
from src.core.config import settings

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# Set sqlalchemy.url from environment
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration['sqlalchemy.url'] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### Create Base Models (`src/database/models.py`)

```python
"""
SQLAlchemy models for Customer Success FTE
"""
from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, JSON, ForeignKey, Text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY, VECTOR
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Customer(Base):
    """Customer table."""
    __tablename__ = "customers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_contact_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, default={})
    total_tickets = Column(Integer, default=0)
    total_conversations = Column(Integer, default=0)
    satisfaction_score = Column(Float, nullable=True)


class Conversation(Base):
    """Conversation table."""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    initial_channel = Column(String(50), nullable=False)  # 'email', 'whatsapp', 'web_form'
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default='active')  # 'active', 'closed', 'escalated'
    sentiment_score = Column(Float, nullable=True)
    sentiment_trend = Column(String(20), nullable=True)  # 'improving', 'stable', 'declining'
    resolution_type = Column(String(50), nullable=True)
    escalated_to = Column(String(255), nullable=True)
    metadata = Column(JSON, default={})

    __table_args__ = (
        Index('idx_customer_id', 'customer_id'),
        Index('idx_status', 'status'),
    )


class Message(Base):
    """Message table."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    channel = Column(String(50), nullable=False)  # 'email', 'whatsapp', 'web_form'
    direction = Column(String(20), nullable=False)  # 'inbound', 'outbound'
    role = Column(String(20), nullable=False)  # 'customer', 'agent', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    tool_calls = Column(JSON, default=[])
    channel_message_id = Column(String(255), nullable=True)  # External ID
    delivery_status = Column(String(50), default='pending')  # 'pending', 'sent', 'delivered', 'failed'
    delivery_error = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_conversation_id', 'conversation_id'),
        Index('idx_channel', 'channel'),
        Index('idx_created_at', 'created_at'),
    )


class Ticket(Base):
    """Ticket table."""
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    ticket_number = Column(String(50), unique=True, nullable=True)
    source_channel = Column(String(50), nullable=False)
    category = Column(String(100), nullable=True)
    priority = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    status = Column(String(50), default='open')  # 'open', 'in_progress', 'resolved', 'escalated'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    sla_target = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON, default={})

    __table_args__ = (
        Index('idx_customer_id', 'customer_id'),
        Index('idx_status', 'status'),
        Index('idx_priority', 'priority'),
        Index('idx_ticket_number', 'ticket_number'),
    )


class KnowledgeBase(Base):
    """Knowledge base table."""
    __tablename__ = "knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), default=[])
    embedding = Column(VECTOR(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_tags', 'tags', postgresql_using='gin'),
    )
```

#### Core Configuration (`src/core/config.py`)

```python
"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "fte-consumer-group"

    # Channels
    GMAIL_CREDENTIALS_PATH: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None

    # Application
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

#### Initial Migration (`migrations/versions/001_initial_schema.py`)

```python
"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('last_contact_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB, server_default=sa.text('{}'), nullable=True),
        sa.Column('total_tickets', sa.Integer(), server_default='0', nullable=True),
        sa.Column('total_conversations', sa.Integer(), server_default='0', nullable=True),
        sa.Column('satisfaction_score', sa.Float(), nullable=True)
    )
    op.create_index('ix_customers_email', 'customers', ['email'], unique=True)
    op.create_index('ix_customers_phone', 'customers', ['phone'], unique=True)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('initial_channel', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(50), server_default='active', nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('sentiment_trend', sa.String(20), nullable=True),
        sa.Column('resolution_type', sa.String(50), nullable=True),
        sa.Column('escalated_to', sa.String(255), nullable=True),
        sa.Column('metadata', postgresql.JSONB, server_default=sa.text('{}'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE')
    )
    op.create_index('idx_conversations_customer_id', 'conversations', ['customer_id'])
    op.create_index('idx_conversations_status', 'conversations', ['status'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel', sa.String(50), nullable=False),
        sa.Column('direction', sa.String(20), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('tool_calls', postgresql.JSONB, server_default=sa.text('[]'), nullable=True),
        sa.Column('channel_message_id', sa.String(255), nullable=True),
        sa.Column('delivery_status', sa.String(50), server_default='pending', nullable=True),
        sa.Column('delivery_error', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE')
    )
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_channel', 'messages', ['channel'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])

    # Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ticket_number', sa.String(50), unique=True, nullable=True),
        sa.Column('source_channel', sa.String(50), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('priority', sa.String(20), server_default='medium', nullable=True),
        sa.Column('status', sa.String(50), server_default='open', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('first_response_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sla_target', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB, server_default=sa.text('{}'), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='SET NULL')
    )
    op.create_index('idx_tickets_customer_id', 'tickets', ['customer_id'])
    op.create_index('idx_tickets_status', 'tickets', ['status'])
    op.create_index('idx_tickets_priority', 'tickets', ['priority'])
    op.create_index('idx_tickets_ticket_number', 'tickets', ['ticket_number'])

    # Create knowledge_base table
    op.create_table(
        'knowledge_base',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), server_default='{}', nullable=True),
        sa.Column('embedding', postgresql.VECTOR(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        sa.Column('published', sa.Boolean(), server_default=True, nullable=True),
        sa.Column('view_count', sa.Integer(), server_default='0', nullable=True)
    )
    op.create_index('idx_knowledge_base_category', 'knowledge_base', ['category'])
    op.create_index('idx_knowledge_base_tags', 'knowledge_base', ['tags'], postgresql_using='gin')


def downgrade() -> None:
    op.drop_table('knowledge_base')
    op.drop_table('tickets')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('customers')
```

#### Migration Commands

```bash
# Create new migration
uv run alembic revision --autogenerate -m "add customer preferences table"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# Check current version
uv run alembic current

# View migration history
uv run alembic history

# SQL preview (don't execute)
uv run alembic upgrade head --sql
```

---

## Repository Layer Implementation

### Database Connection (`src/database/connection.py`)

```python
"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_session() -> AsyncSession:
    """Get database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Base Repository (`src/database/base.py`)

```python
"""
Base repository with common CRUD operations
"""
from typing import TypeVar, Type, Generic, Optional, List
from uuid import UUID
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**kwargs)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get(self, session: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get record by ID."""
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, id: UUID) -> Optional[ModelType]:
        """Get record by ID (alias for get)."""
        return await self.get(session, id)

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """Get multiple records with filters."""
        query = select(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        id: UUID,
        **kwargs
    ) -> Optional[ModelType]:
        """Update record by ID."""
        query = update(self.model).where(self.model.id == id).values(**kwargs).returning(self.model)
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one_or_none()

    async def delete(self, session: AsyncSession, id: UUID) -> bool:
        """Delete record by ID."""
        query = delete(self.model).where(self.model.id == id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0

    async def count(self, session: AsyncSession, **filters) -> int:
        """Count records with filters."""
        query = select(func.count()).select_from(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        result = await session.execute(query)
        return result.scalar()
```

### Customer Repository (`src/database/repositories/customer_repo.py`)

```python
"""
Customer repository - Customer operations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.base import BaseRepository
from src.database.models import Customer, Conversation, Ticket


class CustomerRepository(BaseRepository[Customer]):
    """Repository for customer operations."""

    def __init__(self):
        super().__init__(Customer)

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[Customer]:
        """Get customer by email."""
        result = await session.execute(select(Customer).where(Customer.email == email))
        return result.scalar_one_or_none()

    async def get_by_phone(self, session: AsyncSession, phone: str) -> Optional[Customer]:
        """Get customer by phone."""
        result = await session.execute(select(Customer).where(Customer.phone == phone))
        return result.scalar_one_or_none()

    async def get_or_create_by_email(
        self,
        session: AsyncSession,
        email: str,
        **kwargs
    ) -> Customer:
        """Get existing customer or create new one."""
        customer = await self.get_by_email(session, email)
        if customer:
            return customer

        return await self.create(session, email=email, **kwargs)

    async def get_with_conversations(
        self,
        session: AsyncSession,
        customer_id: UUID
    ) -> Optional[Customer]:
        """Get customer with their conversations."""
        result = await session.execute(
            select(Customer)
            .options(selectinload(Customer.conversations))
            .where(Customer.id == customer_id)
        )
        return result.scalar_one_or_none()

    async def update_last_contact(self, session: AsyncSession, customer_id: UUID) -> Customer:
        """Update customer's last contact timestamp."""
        from datetime import datetime
        return await self.update(session, customer_id, last_contact_at=datetime.now())

    async def increment_tickets(self, session: AsyncSession, customer_id: UUID) -> Customer:
        """Increment customer's total ticket count."""
        customer = await self.get(session, customer_id)
        if customer:
            return await self.update(session, customer_id, total_tickets=customer.total_tickets + 1)
        return customer

    async def increment_conversations(self, session: AsyncSession, customer_id: UUID) -> Customer:
        """Increment customer's total conversation count."""
        customer = await self.get(session, customer_id)
        if customer:
            return await self.update(session, customer_id, total_conversations=customer.total_conversations + 1)
        return customer

    async def search(
        self,
        session: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Customer]:
        """Search customers by name or email."""
        result = await session.execute(
            select(Customer)
            .where(
                (Customer.name.ilike(f"%{search_term}%")) |
                (Customer.email.ilike(f"%{search_term}%"))
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_customers(
        self,
        session: AsyncSession,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List[Customer]:
        """Get customers who had contact in the last N days."""
        from datetime import timedelta, datetime
        cutoff_date = datetime.now() - timedelta(days=days)

        result = await session.execute(
            select(Customer)
            .where(Customer.last_contact_at >= cutoff_date)
            .order_by(Customer.last_contact_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
```

### Ticket Repository (`src/database/repositories/ticket_repo.py`)

```python
"""
Ticket repository - Ticket lifecycle management
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.base import BaseRepository
from src.database.models import Ticket, Customer, Conversation


class TicketRepository(BaseRepository[Ticket]):
    """Repository for ticket lifecycle management."""

    def __init__(self):
        super().__init__(Ticket)

    async def get_by_number(self, session: AsyncSession, ticket_number: str) -> Optional[Ticket]:
        """Get ticket by ticket number."""
        result = await session.execute(
            select(Ticket).where(Ticket.ticket_number == ticket_number)
        )
        return result.scalar_one_or_none()

    async def get_by_customer(
        self,
        session: AsyncSession,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Ticket]:
        """Get all tickets for a customer."""
        result = await session.execute(
            select(Ticket)
            .where(Ticket.customer_id == customer_id)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        session: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Ticket]:
        """Get tickets by status."""
        result = await session.execute(
            select(Ticket)
            .where(Ticket.status == status)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_priority(
        self,
        session: AsyncSession,
        priority: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Ticket]:
        """Get tickets by priority."""
        result = await session.execute(
            select(Ticket)
            .where(Ticket.priority == priority)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_conversation(
        self,
        session: AsyncSession,
        ticket_id: UUID
    ) -> Optional[Ticket]:
        """Get ticket with conversation details."""
        result = await session.execute(
            select(Ticket)
            .options(selectinload(Ticket.conversation))
            .where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, session: AsyncSession, ticket_id: UUID, status: str) -> Optional[Ticket]:
        """Update ticket status."""
        from datetime import datetime
        kwargs = {"status": status}
        if status == "resolved":
            kwargs["resolved_at"] = datetime.now()
        return await self.update(session, ticket_id, **kwargs)

    async def update_first_response_at(self, session: AsyncSession, ticket_id: UUID) -> Optional[Ticket]:
        """Set first response timestamp."""
        from datetime import datetime
        return await self.update(session, ticket_id, first_response_at=datetime.now())

    async def get_overdue_tickets(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[Ticket]:
        """Get tickets past SLA target."""
        from datetime import datetime
        result = await session.execute(
            select(Ticket)
            .where(
                and_(
                    Ticket.status.in_(["open", "in_progress"]),
                    Ticket.sla_target < datetime.now()
                )
            )
            .order_by(Ticket.sla_target.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_open_tickets_count(self, session: AsyncSession) -> int:
        """Count open tickets."""
        return await self.count(session, status="open")

    async def get_by_category(
        self,
        session: AsyncSession,
        category: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Ticket]:
        """Get tickets by category."""
        result = await session.execute(
            select(Ticket)
            .where(Ticket.category == category)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_channel(
        self,
        session: AsyncSession,
        channel: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Ticket]:
        """Get tickets by source channel."""
        result = await session.execute(
            select(Ticket)
            .where(Ticket.source_channel == channel)
            .order_by(Ticket.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
```

### Message Repository (`src/database/repositories/message_repo.py`)

```python
"""
Message repository - Message storage and retrieval
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.base import BaseRepository
from src.database.models import Message


class MessageRepository(BaseRepository[Message]):
    """Repository for message operations."""

    def __init__(self):
        super().__init__(Message)

    async def get_by_conversation(
        self,
        session: AsyncSession,
        conversation_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages for a conversation."""
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_channel(
        self,
        session: AsyncSession,
        channel: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages by channel."""
        result = await session.execute(
            select(Message)
            .where(Message.channel == channel)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_direction(
        self,
        session: AsyncSession,
        direction: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """Get messages by direction (inbound/outbound)."""
        result = await session.execute(
            select(Message)
            .where(Message.direction == direction)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_channel_message_id(
        self,
        session: AsyncSession,
        channel_message_id: str
    ) -> Optional[Message]:
        """Get message by external channel message ID."""
        result = await session.execute(
            select(Message).where(Message.channel_message_id == channel_message_id)
        )
        return result.scalar_one_or_none()

    async def update_delivery_status(
        self,
        session: AsyncSession,
        message_id: UUID,
        status: str,
        error: Optional[str] = None
    ) -> Optional[Message]:
        """Update message delivery status."""
        kwargs = {"delivery_status": status}
        if error:
            kwargs["delivery_error"] = error
        return await self.update(session, message_id, **kwargs)

    async def get_failed_deliveries(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[Message]:
        """Get messages with failed delivery."""
        result = await session.execute(
            select(Message)
            .where(Message.delivery_status == "failed")
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_conversation(self, session: AsyncSession, conversation_id: UUID) -> int:
        """Count messages in a conversation."""
        return await self.count(session, conversation_id=conversation_id)
```

### Conversation Repository (`src/database/repositories/conversation_repo.py`)

```python
"""
Conversation repository - Conversation management
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.database.base import BaseRepository
from src.database.models import Conversation, Customer, Message


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for conversation management."""

    def __init__(self):
        super().__init__(Conversation)

    async def get_by_customer(
        self,
        session: AsyncSession,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get conversations for a customer."""
        result = await session.execute(
            select(Conversation)
            .where(Conversation.customer_id == customer_id)
            .order_by(Conversation.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        session: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get conversations by status."""
        result = await session.execute(
            select(Conversation)
            .where(Conversation.status == status)
            .order_by(Conversation.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_conversations(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get all active conversations."""
        return await self.get_by_status(session, "active", skip, limit)

    async def get_with_messages(
        self,
        session: AsyncSession,
        conversation_id: UUID
    ) -> Optional[Conversation]:
        """Get conversation with all messages."""
        result = await session.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_with_customer(
        self,
        session: AsyncSession,
        conversation_id: UUID
    ) -> Optional[Conversation]:
        """Get conversation with customer details."""
        result = await session.execute(
            select(Conversation)
            .options(selectinload(Conversation.customer))
            .where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, session: AsyncSession, conversation_id: UUID, status: str) -> Optional[Conversation]:
        """Update conversation status."""
        from datetime import datetime
        kwargs = {"status": status}
        if status in ["closed", "escalated"]:
            kwargs["ended_at"] = datetime.now()
        return await self.update(session, conversation_id, **kwargs)

    async def get_by_channel(
        self,
        session: AsyncSession,
        channel: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get conversations by channel."""
        result = await session.execute(
            select(Conversation)
            .where(Conversation.initial_channel == channel)
            .order_by(Conversation.started_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_active(self, session: AsyncSession) -> int:
        """Count active conversations."""
        return await self.count(session, status="active")

    async def get_escalated_conversations(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get escalated conversations."""
        return await self.get_by_status(session, "escalated", skip, limit)
```

### Knowledge Repository (`src/database/repositories/knowledge_repo.py`)

```python
"""
Knowledge repository - Knowledge base queries with semantic search
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.base import BaseRepository
from src.database.models import KnowledgeBase


class KnowledgeRepository(BaseRepository[KnowledgeBase]):
    """Repository for knowledge base operations."""

    def __init__(self):
        super().__init__(KnowledgeBase)

    async def search_by_category(
        self,
        session: AsyncSession,
        category: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[KnowledgeBase]:
        """Search knowledge base by category."""
        result = await session.execute(
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.category == category,
                    KnowledgeBase.published == True
                )
            )
            .order_by(KnowledgeBase.view_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def search_by_tags(
        self,
        session: AsyncSession,
        tags: List[str],
        skip: int = 0,
        limit: int = 20
    ) -> List[KnowledgeBase]:
        """Search knowledge base by tags (any tag match)."""
        result = await session.execute(
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.tags.overlap(tags),
                    KnowledgeBase.published == True
                )
            )
            .order_by(KnowledgeBase.view_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def semantic_search(
        self,
        session: AsyncSession,
        query_embedding: List[float],
        limit: int = 5
    ) -> List[tuple[KnowledgeBase, float]]:
        """Perform semantic search using vector similarity."""
        # This uses PostgreSQL's <=> operator for cosine distance
        result = await session.execute(
            select(
                KnowledgeBase,
                KnowledgeBase.embedding.op('<=>')(query_embedding).label('distance')
            )
            .where(KnowledgeBase.published == True)
            .order_by('distance')
            .limit(limit)
        )
        return [(row[0], row.distance) for row in result.all()]

    async def full_text_search(
        self,
        session: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[KnowledgeBase]:
        """Full text search in title and content."""
        result = await session.execute(
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.published == True,
                    or_(
                        KnowledgeBase.title.ilike(f"%{search_term}%"),
                        KnowledgeBase.content.ilike(f"%{search_term}%")
                    )
                )
            )
            .order_by(KnowledgeBase.view_count.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_published(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[KnowledgeBase]:
        """Get all published knowledge base entries."""
        result = await session.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.published == True)
            .order_by(KnowledgeBase.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_view_count(self, session: AsyncSession, knowledge_id: UUID) -> Optional[KnowledgeBase]:
        """Increment view count for knowledge base entry."""
        kb_entry = await self.get(session, knowledge_id)
        if kb_entry:
            return await self.update(session, knowledge_id, view_count=kb_entry.view_count + 1)
        return kb_entry

    async def update_embedding(
        self,
        session: AsyncSession,
        knowledge_id: UUID,
        embedding: List[float]
    ) -> Optional[KnowledgeBase]:
        """Update embedding vector for knowledge base entry."""
        return await self.update(session, knowledge_id, embedding=embedding)

    async def get_by_category_with_limit(
        self,
        session: AsyncSession,
        category: str,
        limit: int = 10
    ) -> List[KnowledgeBase]:
        """Get top entries from a category by view count."""
        result = await session.execute(
            select(KnowledgeBase)
            .where(
                and_(
                    KnowledgeBase.category == category,
                    KnowledgeBase.published == True
                )
            )
            .order_by(KnowledgeBase.view_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
```

### Repository Usage Example

```python
"""
Example usage of repositories in services
"""
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.repositories.customer_repo import CustomerRepository
from src.database.repositories.ticket_repo import TicketRepository
from src.database.repositories.message_repo import MessageRepository

async def handle_customer_inquiry(session: AsyncSession, email: str, message: str):
    """Example of repository usage in business logic."""
    customer_repo = CustomerRepository()
    ticket_repo = TicketRepository()
    message_repo = MessageRepository()

    # Get or create customer
    customer = await customer_repo.get_or_create_by_email(
        session,
        email,
        name="John Doe",
        phone="+1234567890"
    )

    # Create ticket
    ticket = await ticket_repo.create(
        session,
        customer_id=customer.id,
        source_channel="email",
        category="general",
        priority="medium",
        status="open"
    )

    # Create message
    message = await message_repo.create(
        session,
        conversation_id=None,  # Will be linked later
        channel="email",
        direction="inbound",
        role="customer",
        content=message
    )

    return {
        "customer": customer,
        "ticket": ticket,
        "message": message
    }
```

---

## Exercise 2.2: Channel Integrations (4-5 hours)

### Task: Build Intake Handlers for Each Channel

You'll create three handlers to accept messages from all channels and normalize them into a unified format.

### Setup Dependencies

```bash
# Install channel integration dependencies
uv add google-api-python-client google-auth-oauthlib twilio aiokafka
```

### Create Channel Handlers Directory

```bash
mkdir -p src/channels
```

### Gmail Integration

#### `src/channels/gmail_handler.py`

```python
"""
Gmail integration handler
Handles incoming emails via Pub/Sub push notifications
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.cloud import pubsub_v1
import base64
import email
from email.mime.text import MIMEText
from datetime import datetime
import os
from typing import Optional

class GmailHandler:
    """Handle Gmail API interactions for customer support."""

    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize Gmail handler with credentials."""
        if credentials_path and os.path.exists(credentials_path):
            self.credentials = Credentials.from_authorized_user_file(credentials_path)
        else:
            # Use service account or environment variable
            self.credentials = self._get_credentials_from_env()

        self.service = build('gmail', 'v1', credentials=self.credentials)
        self.pubsub_publisher = pubsub_v1.PublisherClient()

    def _get_credentials_from_env(self) -> Credentials:
        """Get credentials from environment variables."""
        # In production, use service account or OAuth flow
        # For prototype, we'll use a simplified approach
        from google.oauth2 import service_account

        credentials_json = os.getenv('GMAIL_CREDENTIALS_JSON')
        if credentials_json:
            import json
            return service_account.Credentials.from_service_account_info(
                json.loads(credentials_json)
            )

        raise ValueError("Gmail credentials not configured")

    async def setup_push_notifications(self, topic_name: str) -> dict:
        """
        Set up Gmail push notifications via Pub/Sub.

        Args:
            topic_name: Pub/Sub topic for Gmail notifications

        Returns:
            Dict with watch result
        """
        request = {
            'labelIds': ['INBOX'],
            'topicName': topic_name,
            'labelFilterAction': 'include'
        }

        result = self.service.users().watch(
            userId='me',
            body=request
        ).execute()

        return {
            'history_id': result.get('historyId'),
            'expiration': result.get('expiration')
        }

    async def process_notification(self, pubsub_message: dict) -> list[dict]:
        """
        Process incoming Pub/Sub notification from Gmail.

        Args:
            pubsub_message: Pub/Sub message data

        Returns:
            List of parsed email messages
        """
        history_id = pubsub_message.get('historyId')

        # Get new messages since last history ID
        history = self.service.users().history().list(
            userId='me',
            startHistoryId=history_id,
            historyTypes=['messageAdded']
        ).execute()

        messages = []
        for record in history.get('history', []):
            for msg_added in record.get('messagesAdded', []):
                msg_id = msg_added['message']['id']
                message = await self.get_message(msg_id)
                messages.append(message)

        return messages

    async def get_message(self, message_id: str) -> dict:
        """
        Fetch and parse a Gmail message.

        Args:
            message_id: Gmail message ID

        Returns:
            Dict with normalized message data
        """
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}

        # Extract body
        body = self._extract_body(msg['payload'])

        return {
            'channel': 'email',
            'channel_message_id': message_id,
            'customer_email': self._extract_email(headers.get('From', '')),
            'customer_name': self._extract_name(headers.get('From', '')),
            'subject': headers.get('Subject', ''),
            'content': body,
            'received_at': datetime.utcnow().isoformat(),
            'thread_id': msg.get('threadId'),
            'metadata': {
                'headers': headers,
                'labels': msg.get('labelIds', []),
                'snippet': msg.get('snippet', '')
            }
        }

    def _extract_body(self, payload: dict) -> str:
        """Extract text body from email payload."""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    return base64.urlsafe_b64decode(
                        part['body']['data']
                    ).decode('utf-8')

        return ''

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from From header."""
        import re
        match = re.search(r'<(.+?)>', from_header)
        return match.group(1) if match else from_header

    def _extract_name(self, from_header: str) -> str:
        """Extract name from From header."""
        # Extract from "John Doe <john@example.com>"
        match = re.search(r'(.+?)\s*<', from_header)
        if match:
            return match.group(1).strip('"')

        # Fallback to email
        return self._extract_email(from_header)

    async def send_reply(
        self,
        to_email: str,
        subject: str,
        body: str,
        thread_id: Optional[str] = None
    ) -> dict:
        """
        Send email reply via Gmail API.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            thread_id: Gmail thread ID for threading

        Returns:
            Dict with message ID and delivery status
        """
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}" if not subject.startswith('Re:') else subject

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        send_request = {'raw': raw}
        if thread_id:
            send_request['threadId'] = thread_id

        result = self.service.users().messages().send(
            userId='me',
            body=send_request
        ).execute()

        return {
            'channel_message_id': result['id'],
            'delivery_status': 'sent',
            'thread_id': result.get('threadId')
        }
```

### WhatsApp Integration (Twilio)

#### `src/channels/whatsapp_handler.py`

```python
"""
WhatsApp integration handler via Twilio
Handles incoming WhatsApp messages and sends replies
"""

from twilio.rest import Client
from twilio.request_validator import RequestValidator
from fastapi import Request, HTTPException
import os
from datetime import datetime
from typing import Optional

class WhatsAppHandler:
    """Handle WhatsApp interactions via Twilio API."""

    def __init__(self):
        """Initialize WhatsApp handler with Twilio credentials."""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
        self.client = Client(self.account_sid, self.auth_token)
        self.validator = RequestValidator(self.auth_token)

    async def validate_webhook(self, request: Request) -> bool:
        """
        Validate incoming Twilio webhook signature.

        Args:
            request: FastAPI request object

        Returns:
            bool: True if signature is valid
        """
        signature = request.headers.get('X-Twilio-Signature', '')
        url = str(request.url)
        form_data = await request.form()
        params = dict(form_data)

        return self.validator.validate(url, params, signature)

    async def process_webhook(self, form_data: dict) -> dict:
        """
        Process incoming WhatsApp message from Twilio webhook.

        Args:
            form_data: Twilio webhook form data

        Returns:
            Dict with normalized message data
        """
        return {
            'channel': 'whatsapp',
            'channel_message_id': form_data.get('MessageSid'),
            'customer_phone': form_data.get('From', '').replace('whatsapp:', ''),
            'customer_name': form_data.get('ProfileName', ''),
            'content': form_data.get('Body', ''),
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'num_media': form_data.get('NumMedia', '0'),
                'profile_name': form_data.get('ProfileName'),
                'wa_id': form_data.get('WaId'),
                'status': form_data.get('SmsStatus')
            }
        }

    async def send_message(self, to_phone: str, body: str) -> dict:
        """
        Send WhatsApp message via Twilio.

        Args:
            to_phone: Phone number (with or without country code)
            body: Message content

        Returns:
            Dict with message SID and delivery status
        """
        # Ensure phone number is in WhatsApp format
        if not to_phone.startswith('whatsapp:'):
            to_phone = f'whatsapp:{to_phone}'

        message = self.client.messages.create(
            body=body,
            from_=self.whatsapp_number,
            to=to_phone
        )

        return {
            'channel_message_id': message.sid,
            'delivery_status': message.status  # 'queued', 'sent', 'delivered', 'failed'
        }

    def format_response(self, response: str, max_length: int = 1600) -> list[str]:
        """
        Format and split response for WhatsApp (max 1600 chars per message).

        Args:
            response: Full response to send
            max_length: Maximum characters per message

        Returns:
            List of message parts
        """
        if len(response) <= max_length:
            return [response]

        # Split into multiple messages
        messages = []
        while response:
            if len(response) <= max_length:
                messages.append(response)
                break

            # Find a good break point
            break_point = response.rfind('. ', 0, max_length)
            if break_point == -1:
                break_point = response.rfind(' ', 0, max_length)
            if break_point == -1:
                break_point = max_length

            messages.append(response[:break_point + 1].strip())
            response = response[break_point + 1:].strip()

        return messages
```

### Web Form Integration

#### `src/channels/web_form_handler.py`

```python
"""
Web Support Form handler
Handles form submissions from Next.js frontend
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List
import uuid

router = APIRouter(prefix="/support", tags=["support-form"])

class SupportFormSubmission(BaseModel):
    """Support form submission model with validation."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    subject: str = Field(..., min_length=5, max_length=200)
    category: str = Field(
        ...,
        description="Support category: general, technical, billing, feedback, bug_report"
    )
    message: str = Field(..., min_length=10, max_length=2000)
    priority: Optional[str] = Field('medium', description="low, medium, high")
    attachments: Optional[List[str]] = Field(default_factory=list)

    @field_validator('category')
    @classmethod
    def category_must_be_valid(cls, v):
        valid_categories = ['general', 'technical', 'billing', 'feedback', 'bug_report']
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v

    @field_validator('priority')
    @classmethod
    def priority_must_be_valid(cls, v):
        valid_priorities = ['low', 'medium', 'high']
        if v and v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

class SupportFormResponse(BaseModel):
    """Response model for form submission."""
    ticket_id: str
    ticket_number: str
    message: str
    estimated_response_time: str
    status_url: str

@router.post("/submit", response_model=SupportFormResponse, status_code=201)
async def submit_support_form(submission: SupportFormSubmission):
    """
    Handle support form submission.

    This endpoint:
    1. Validates submission
    2. Creates a customer record if new
    3. Creates a ticket in system
    4. Returns confirmation with ticket ID

    Args:
        submission: Validated form data

    Returns:
        SupportFormResponse with ticket details
    """
    try:
        # Generate ticket IDs
        ticket_id = str(uuid.uuid4())
        ticket_number = f"TKT-{abs(hash(ticket_id)) % 100000:05d}"

        # Create normalized message for agent
        message_data = {
            'channel': 'web_form',
            'channel_message_id': ticket_id,
            'customer_email': submission.email,
            'customer_name': submission.name,
            'subject': submission.subject,
            'content': submission.message,
            'category': submission.category,
            'priority': submission.priority or 'medium',
            'received_at': datetime.utcnow().isoformat(),
            'metadata': {
                'form_version': '1.0',
                'attachments': submission.attachments,
                'submission_source': 'web_form'
            }
        }

        # Store in database (you'll implement this)
        # await create_ticket_in_db(ticket_id, message_data)

        # TODO: Publish to Kafka for agent processing
        # await publish_to_kafka('fte.tickets.incoming', message_data)

        return SupportFormResponse(
            ticket_id=ticket_id,
            ticket_number=ticket_number,
            message="Thank you for contacting TechFlow! Our AI assistant will respond shortly.",
            estimated_response_time="Usually within 5 minutes",
            status_url=f"/support/ticket/{ticket_id}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process submission: {str(e)}"
        )

@router.get("/ticket/{ticket_id}")
async def get_ticket_status(ticket_id: str):
    """
    Get status and conversation history for a ticket.

    Args:
        ticket_id: Ticket UUID

    Returns:
        Ticket status and message history
    """
    try:
        # TODO: Fetch from database
        # ticket = await get_ticket_by_id(ticket_id)

        # For now, return mock data
        return {
            "ticket_id": ticket_id,
            "status": "open",
            "messages": [
                {
                    "role": "customer",
                    "content": "Sample message",
                    "created_at": datetime.utcnow().isoformat()
                }
            ],
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="Ticket not found")

@router.get("/categories")
async def get_support_categories():
    """Get available support categories for the form."""
    return {
        "categories": [
            {"value": "general", "label": "General Question"},
            {"value": "technical", "label": "Technical Support"},
            {"value": "billing", "label": "Billing Inquiry"},
            {"value": "feedback", "label": "Product Feedback"},
            {"value": "bug_report", "label": "Bug Report"}
        ]
    }
```

---

## Exercise 2.3: Next.js Complete Frontend - 5 Pages (6-8 hours)

### Task: Build Complete 5-Page Application (REQUIRED DELIVERABLE)

This is a **required deliverable**. You must build a complete, production-ready frontend with **5 pages**:

**Customer Side (2 pages):**
- Page 1: `/support` - Support form for ticket submission
- Page 2: `/support/ticket/[id]` - Ticket status page for customers

**Admin Side (3 pages):**
- Page 3: `/admin` - Dashboard with metrics and escalation queue
- Page 4: `/admin/tickets` - All tickets table with filtering
- Page 5: `/admin/tickets/[id]` - Single ticket detail with human reply capability

---

## Complete Frontend Architecture

### File Structure

```
web-form/
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
├── .env.local
└── app/
    ├── layout.tsx                    # Root layout
    ├── page.tsx                      # Home page (redirects to /support)
    ├── globals.css                     # Global styles
    │
    ├── customer/                       # CUSTOMER SIDE
    │   ├── support/
    │   │   └── page.tsx              # /support (form page)
    │   └── ticket/
    │       └── [id]/
    │           └── page.tsx            # /support/ticket/[id] (status page)
    │
    ├── admin/                          # ADMIN SIDE
    │   ├── middleware.ts               # Admin authentication
    │   ├── page.tsx                   # /admin (dashboard)
    │   └── tickets/
    │       ├── page.tsx               # /admin/tickets (all tickets)
    │       └── [id]/
    │           └── page.tsx            # /admin/tickets/[id] (single ticket)
    │
    ├── api/                            # API routes for frontend
    │   └── tickets/
    │       └── [id]/
    │           └── route.ts             # Ticket detail API
    │
    └── components/
        ├── customer/                      # CUSTOMER COMPONENTS
        │   ├── SupportForm.tsx
        │   ├── SubmissionSuccess.tsx
        │   ├── TicketStatus.tsx
        │   └── TicketNotFound.tsx
        │
        └── admin/                          # ADMIN COMPONENTS
            ├── StatsCards.tsx
            ├── ChannelMetrics.tsx
            ├── EscalationQueue.tsx
            ├── TicketsTable.tsx
            ├── ConversationHistory.tsx
            ├── CustomerHistory.tsx
            └── ReplyBox.tsx
```

---

## Customer Side Implementation

### Page 1: Support Form (`/support`)

#### `web-form/app/customer/support/page.tsx`

```typescript
/**
 * Customer Support Page - Ticket Submission Form
 */
'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import SupportForm from '@/components/customer/SupportForm';
import SubmissionSuccess from '@/components/customer/SubmissionSuccess';

export default function SupportPage() {
  const router = useRouter();
  const [submittedTicketId, setSubmittedTicketId] = React.useState<string | null>(null);

  const handleFormSubmit = async (ticketData: any) => {
    try {
      const response = await fetch('/api/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ticketData),
      });

      const result = await response.json();
      setSubmittedTicketId(result.ticket_id);

    } catch (error) {
      console.error('Failed to submit ticket:', error);
    }
  };

  if (submittedTicketId) {
    return <SubmissionSuccess ticketId={submittedTicketId} onNewTicket={() => setSubmittedTicketId(null)} />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              TechFlow Customer Support
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300">
              Submit your inquiry and we'll get back to you within 24 hours
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="md:col-span-2">
              <SupportForm onSubmit={handleFormSubmit} />
            </div>
          </div>

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
                Contact Options
              </h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2">📧</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    Email us at support@techflow.com
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-green-600 mr-2">💬</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    Chat via WhatsApp: +1 (555) 123-4567
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-600 mr-2">🌐</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    Use this online form (fastest response time)
                  </span>
                </li>
              </ul>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-white">
                Response Times
              </h3>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <span className="text-green-500 mr-2">✓</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    Critical: 1 hour
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-yellow-500 mr-2">✓</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    High: 4 hours
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-500 mr-2">✓</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    Medium: 24 hours
                  </span>
                </li>
                <li className="flex items-start">
                  <span className="text-gray-500 mr-2">✓</span>
                  <span className="text-gray-700 dark:text-gray-300">
                    Low: 72 hours
                  </span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Page 2: Ticket Status (`/support/ticket/[id]`)

#### `web-form/app/customer/ticket/[id]/page.tsx`

```typescript
/**
 * Customer Ticket Status Page
 */
'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import TicketStatus from '@/components/customer/TicketStatus';
import TicketNotFound from '@/components/customer/TicketNotFound';

export default function TicketStatusPage() {
  const params = useParams();
  const ticketId = params.id as string;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <TicketStatus ticketId={ticketId} />
    </div>
  );
}
```

#### `web-form/app/components/customer/TicketStatus.tsx`

```typescript
/**
 * Ticket Status Display Component
 */
'use client';

import React, { useState, useEffect } from 'react';
import { ArrowLeft, Clock, MessageCircle, CheckCircle2, AlertCircle } from 'lucide-react';

interface TicketStatusProps {
  ticketId: string;
}

interface TicketData {
  id: string;
  ticket_number: string;
  status: 'open' | 'in_progress' | 'resolved' | 'escalated';
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
  messages: Array<{
    role: string;
    content: string;
    created_at: string;
  }>;
}

export default function TicketStatus({ ticketId }: TicketStatusProps) {
  const [ticket, setTicket] = useState<TicketData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTicketStatus();
  }, [ticketId]);

  const fetchTicketStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/tickets/${ticketId}`);

      if (!response.ok) {
        if (response.status === 404) {
          setError('Ticket not found');
        } else {
          setError('Failed to load ticket status');
        }
        setTicket(null);
        return;
      }

      const data = await response.json();
      setTicket(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching ticket:', err);
      setError('Failed to load ticket status');
      setTicket(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      escalated: 'bg-red-100 text-red-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority: string) => {
    const colors = {
      low: 'text-gray-600',
      medium: 'text-yellow-600',
      high: 'text-orange-600',
      critical: 'text-red-600'
    };
    return colors[priority as keyof typeof colors] || 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
      </div>
    );
  }

  if (error || !ticket) {
    return <TicketNotFound />;
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <button
        onClick={() => window.history.back()}
        className="mb-6 flex items-center text-blue-600 hover:text-blue-800 transition-colors"
      >
        <ArrowLeft className="w-5 h-5 mr-2" />
        Back to Support
      </button>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        <div className={`${getStatusColor(ticket.status)} p-6`}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">
              Ticket #{ticket.ticket_number}
            </h2>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-white dark:bg-gray-900">
              {ticket.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>
          <p className="text-gray-600 dark:text-gray-300">
            Created: {new Date(ticket.created_at).toLocaleString()}
          </p>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Category
              </label>
              <p className="text-gray-900 dark:text-white capitalize">
                {ticket.category.replace('_', ' ')}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Priority
              </label>
              <p className={`font-semibold ${getPriorityColor(ticket.priority)}`}>
                {ticket.priority.toUpperCase()}
              </p>
            </div>
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
              Conversation History
            </h3>
            <div className="space-y-4">
              {ticket.messages.slice(-5).map((message, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    message.role === 'customer' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <div
                    className={`max-w-xs p-3 rounded-lg ${
                      message.role === 'customer'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}
                  >
                    {message.role === 'customer' ? 'You' : 'AI'}
                  </div>
                  <div className="flex-1 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                    <p className="text-gray-900 dark:text-white">
                      {message.content}
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(message.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {ticket.status === 'resolved' && (
            <div className="bg-green-50 dark:bg-green-900/20 p-6 border-t border-green-200 dark:border-green-800">
              <div className="flex items-center text-green-700 dark:text-green-300">
                <CheckCircle2 className="w-6 h-6 mr-2" />
                <span className="font-semibold">
                  This ticket has been resolved!
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## Admin Side Implementation

### Admin Middleware

#### `web-form/app/admin/middleware.ts`

```typescript
/**
 * Admin Authentication Middleware
 */
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function adminMiddleware(req: NextRequest) {
  const adminPassword = req.headers.get('x-admin-password');
  const validPassword = process.env.ADMIN_PASSWORD || 'admin123';

  if (adminPassword !== validPassword) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const response = NextResponse.next();
  response.headers.set('x-admin-authenticated', 'true');
  return response;
}
```

### Page 3: Admin Dashboard (`/admin`)

#### `web-form/app/admin/page.tsx`

```typescript
/**
 * Admin Dashboard - Overview with Metrics and Escalation Queue
 */
'use client';

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Activity, Users, AlertTriangle } from 'lucide-react';
import StatsCards from '@/components/admin/StatsCards';
import ChannelMetrics from '@/components/admin/ChannelMetrics';
import EscalationQueue from '@/components/admin/EscalationQueue';

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalTickets: 0,
    resolvedToday: 0,
    escalatedToday: 0,
    avgResponseTime: 0,
    activeConversations: 0
  });

  const [escalations, setEscalations] = useState([
    { id: '1', ticketNumber: 'TKT-1234', customer: 'john@acme.com', reason: 'Refund request $50k', priority: 'CRITICAL', time: '2 hours ago' },
    { id: '2', ticketNumber: 'TKT-1235', customer: '+15551234567', reason: 'Legal query', priority: 'HIGH', time: '4 hours ago' },
    { id: '3', ticketNumber: 'TKT-1236', customer: 'mike@co.com', reason: 'HIPAA documentation', priority: 'HIGH', time: '6 hours ago' }
  ]);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('/api/admin/metrics');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              TechFlow Admin Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                {new Date().toLocaleString()}
              </span>
              <div className="flex items-center text-green-600">
                <Activity className="w-5 h-5 mr-1" />
                <span className="font-semibold">
                  3 Workers Online
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Stats Cards */}
          <StatsCards stats={stats} />

          {/* Channel Metrics */}
          <div className="lg:col-span-2">
            <ChannelMetrics />
          </div>

          {/* Escalation Queue - Most Important */}
          <div className="lg:col-span-3">
            <EscalationQueue escalations={escalations} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
            <TrendingUp className="w-5 h-5 mr-2" />
            View All Tickets
          </button>
          <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
            <Users className="w-5 h-5 mr-2" />
            Manage Customers
          </button>
          <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
            <BarChart3 className="w-5 h-5 mr-2" />
            View Analytics
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### `web-form/app/components/admin/StatsCards.tsx`

```typescript
/**
 * Stats Cards Component - Overview Metrics
 */
'use client';

import React from 'react';
import { CheckCircle2, Clock, MessageCircle, AlertTriangle, TrendingUp } from 'lucide-react';

interface StatsCardsProps {
  stats: {
    totalTickets: number;
    resolvedToday: number;
    escalatedToday: number;
    avgResponseTime: number;
    activeConversations: number;
  };
}

export default function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Tickets */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">
            Total Tickets
          </h3>
          <MessageCircle className="w-5 h-5 text-blue-600" />
        </div>
        <p className="text-3xl font-bold text-gray-900 dark:text-white">
          {stats.totalTickets}
        </p>
      </div>

      {/* Resolved Today */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">
            Resolved Today
          </h3>
          <CheckCircle2 className="w-5 h-5 text-green-600" />
        </div>
        <p className="text-3xl font-bold text-gray-900 dark:text-white">
          {stats.resolvedToday}
        </p>
      </div>

      {/* Escalated Today */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">
            Escalated Today
          </h3>
          <AlertTriangle className="w-5 h-5 text-red-600" />
        </div>
        <p className="text-3xl font-bold text-gray-900 dark:text-white">
          {stats.escalatedToday}
        </p>
      </div>

      {/* Avg Response Time */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-300">
            Avg Response Time
          </h3>
          <Clock className="w-5 h-5 text-yellow-600" />
        </div>
        <p className="text-3xl font-bold text-gray-900 dark:text-white">
          {stats.avgResponseTime.toFixed(1)}s
        </p>
      </div>
    </div>
  );
}
```

#### `web-form/app/components/admin/EscalationQueue.tsx`

```typescript
/**
 * Escalation Queue Component - Most Important Admin Feature
 */
'use client';

import React from 'react';
import { AlertTriangle, Clock, User, ExternalLink, ChevronRight } from 'lucide-react';

interface EscalationItem {
  id: string;
  ticketNumber: string;
  customer: string;
  reason: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  time: string;
}

interface EscalationQueueProps {
  escalations: EscalationItem[];
}

export default function EscalationQueue({ escalations }: EscalationQueueProps) {
  const getPriorityBadge = (priority: string) => {
    const colors = {
      LOW: 'bg-gray-100 text-gray-800',
      MEDIUM: 'bg-yellow-100 text-yellow-800',
      HIGH: 'bg-orange-100 text-orange-800',
      CRITICAL: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-bold ${colors[priority as keyof typeof colors]}`}>
        {priority}
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      <div className="bg-red-50 dark:bg-red-900/20 p-6 border-l-4 border-red-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <AlertTriangle className="w-6 h-6 text-red-600 mr-2" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Escalation Queue
            </h2>
          </div>
          <span className="bg-red-600 text-white px-3 py-1 rounded-full text-sm font-medium">
            {escalations.length} Pending
          </span>
        </div>
        <p className="text-sm text-red-700 dark:text-red-300 mt-2">
          These tickets require human intervention. Review and respond ASAP.
        </p>
      </div>

      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {escalations.map((escalation) => (
          <div
            key={escalation.id}
            className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {escalation.time}
                </span>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  #{escalation.ticketNumber}
                </h3>
              </div>
              {getPriorityBadge(escalation.priority)}
            </div>

            <div className="flex items-center mb-3">
              <User className="w-4 h-4 text-gray-400 mr-2" />
              <span className="text-gray-700 dark:text-gray-300 font-medium">
                {escalation.customer}
              </span>
            </div>

            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <div className="flex items-start mb-2">
                <AlertTriangle className="w-5 h-5 text-orange-600 mr-2 mt-0.5" />
                <span className="font-medium text-gray-900 dark:text-white">
                  Reason: {escalation.reason}
                </span>
              </div>
            </div>

            <button className="w-full mt-4 flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
              Review & Reply
              <ChevronRight className="w-5 h-5 ml-2" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Page 4: All Tickets (`/admin/tickets`)

#### `web-form/app/admin/tickets/page.tsx`

```typescript
/**
 * Admin All Tickets Page
 */
'use client';

import React, { useState, useEffect } from 'react';
import { Search, Filter, Download, Plus } from 'lucide-react';
import TicketsTable from '@/components/admin/TicketsTable';

export default function AdminTicketsPage() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: 'all',
    channel: 'all',
    priority: 'all'
  });

  useEffect(() => {
    fetchTickets();
  }, [filters]);

  const fetchTickets = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams(
        Object.entries(filters).filter(([_, v]) => v !== 'all')
      ).toString();

      const response = await fetch(`/api/admin/tickets?${queryParams}`);
      const data = await response.json();
      setTickets(data.tickets);
    } catch (error) {
      console.error('Failed to fetch tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            All Tickets
          </h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setFilters({ ...filters, status: 'all' })}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors"
            >
              All
            </button>
            <button
              onClick={() => setFilters({ ...filters, status: 'open' })}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Open
            </button>
            <button
              onClick={() => setFilters({ ...filters, status: 'resolved' })}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              Resolved
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-6">
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <Search className="w-5 h-5 text-gray-400 mr-2" />
              <input
                type="text"
                placeholder="Search tickets..."
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
              />
            </div>
            <select
              value={filters.channel}
              onChange={(e) => setFilters({ ...filters, channel: e.target.value })}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
            >
              <option value="all">All Channels</option>
              <option value="email">📧 Email</option>
              <option value="whatsapp">💬 WhatsApp</option>
              <option value="web_form">🌐 Web Form</option>
            </select>
            <select
              value={filters.priority}
              onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
            >
              <option value="all">All Priorities</option>
              <option value="critical">🔴 Critical</option>
              <option value="high">🟠 High</option>
              <option value="medium">🟡 Medium</option>
              <option value="low">🟢 Low</option>
            </select>
            <button className="px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg transition-colors">
              <Filter className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Tickets Table */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          </div>
        ) : (
          <TicketsTable tickets={tickets} />
        )}
      </div>
    </div>
  );
}
```

#### `web-form/app/components/admin/TicketsTable.tsx`

```typescript
/**
 * Tickets Table Component
 */
'use client';

import React from 'react';
import { ExternalLink, Clock, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function TicketsTable({ tickets }: { tickets: any[] }) {
  const getStatusBadge = (status: string) => {
    const badges = {
      open: 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      escalated: 'bg-red-100 text-red-800'
    };
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Ticket #
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Channel
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-4 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {tickets.map((ticket) => (
              <tr key={ticket.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <td className="px-6 py-4">
                  <span className="font-medium text-blue-600 hover:underline cursor-pointer">
                    {ticket.ticket_number}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-900 dark:text-white">
                  {ticket.customer_email}
                </td>
                <td className="px-6 py-4">
                  {ticket.channel === 'email' && '📧'}
                  {ticket.channel === 'whatsapp' && '💬'}
                  {ticket.channel === 'web_form' && '🌐'}
                  <span className="ml-2 capitalize text-gray-700 dark:text-gray-300">
                    {ticket.channel.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-900 dark:text-white capitalize">
                  {ticket.category}
                </td>
                <td className="px-6 py-4">
                  <span className={`font-semibold ${
                    ticket.priority === 'critical' ? 'text-red-600' :
                    ticket.priority === 'high' ? 'text-orange-600' :
                    ticket.priority === 'medium' ? 'text-yellow-600' : 'text-gray-600'
                  }`}>
                    {ticket.priority.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusBadge(ticket.status)}`}>
                    {ticket.status.replace('_', ' ').toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                  {new Date(ticket.created_at).toLocaleString()}
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center justify-end space-x-2">
                    <button className="p-2 text-blue-600 hover:text-blue-800 transition-colors">
                      <Clock className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-green-600 hover:text-green-800 transition-colors">
                      <CheckCircle2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

### Page 5: Single Ticket with Human Reply (`/admin/tickets/[id]`)

#### `web-form/app/admin/tickets/[id]/page.tsx`

```typescript
/**
 * Admin Single Ticket Page - Human Reply Interface
 * THIS IS THE MOST IMPORTANT ADMIN PAGE - WHERE HUMAN IN THE LOOP HAPPENS
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ConversationHistory from '@/components/admin/ConversationHistory';
import CustomerHistory from '@/components/admin/CustomerHistory';
import ReplyBox from '@/components/admin/ReplyBox';
import { ArrowLeft, Send, CheckCircle2, RotateCcw, AlertTriangle } from 'lucide-react';

export default function AdminTicketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticketId = params.id as string;

  const [ticket, setTicket] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [sendingReply, setSendingReply] = useState(false);

  useEffect(() => {
    fetchTicketDetails();
  }, [ticketId]);

  const fetchTicketDetails = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/admin/tickets/${ticketId}`);
      const data = await response.json();
      setTicket(data);
    } catch (error) {
      console.error('Failed to fetch ticket:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async (replyData: any) => {
    try {
      setSendingReply(true);
      const response = await fetch(`/api/admin/tickets/${ticketId}/reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(replyData),
      });

      if (response.ok) {
        // Update ticket locally
        setTicket({
          ...ticket,
          status: 'resolved',
          resolved_at: new Date().toISOString()
        });

        // Show success message
        alert('Reply sent successfully!');
      } else {
        alert('Failed to send reply');
      }
    } catch (error) {
      console.error('Error sending reply:', error);
      alert('Failed to send reply');
    } finally {
      setSendingReply(false);
    }
  };

  const handleMarkResolved = async () => {
    try {
      const response = await fetch(`/api/admin/tickets/${ticketId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'resolved' }),
      });

      if (response.ok) {
        setTicket({
          ...ticket,
          status: 'resolved',
          resolved_at: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Error marking resolved:', error);
    }
  };

  if (loading || !ticket) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="flex items-center text-blue-600 hover:text-blue-800 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to All Tickets
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Ticket Details */}
          <div className="space-y-6">
            {/* Ticket Header */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Ticket #{ticket.ticket_number}
                </h1>
                {ticket.status === 'escalated' && (
                  <span className="flex items-center bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                    <AlertTriangle className="w-4 h-4 mr-1" />
                    ESCALATED
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    Customer
                  </label>
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-2">
                      👤
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {ticket.customer_name}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {ticket.customer_email}
                      </p>
                    </div>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    Channel
                  </label>
                  <div className="flex items-center">
                    {ticket.channel === 'email' && '📧'}
                    {ticket.channel === 'whatsapp' && '💬'}
                    {ticket.channel === 'web_form' && '🌐'}
                    <span className="ml-2 capitalize text-gray-900 dark:text-white font-medium">
                      {ticket.channel.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    Category
                  </label>
                  <p className="text-gray-900 dark:text-white capitalize">
                    {ticket.category}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
                    Priority
                  </label>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${
                    ticket.priority === 'critical' ? 'bg-red-100 text-red-800' :
                    ticket.priority === 'high' ? 'bg-orange-100 text-orange-800' :
                    ticket.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {ticket.priority.toUpperCase()}
                  </span>
                </div>
              </div>

              {ticket.status === 'escalated' && (
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border border-red-200 dark:border-red-800">
                  <div className="flex items-start">
                    <AlertTriangle className="w-5 h-5 text-red-600 mr-2 mt-0.5" />
                    <div>
                      <p className="font-semibold text-gray-900 dark:text-white mb-1">
                        Escalation Reason
                      </p>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        {ticket.escalation_reason || 'Agent escalated this ticket'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
            </div>

            {/* Customer History */}
            <CustomerHistory customerId={ticket.customer_id} />

            {/* Conversation History */}
            <ConversationHistory conversationId={ticket.conversation_id} />
          </div>

          {/* Right Column - Reply Interface */}
          <div className="space-y-6">
            {/* Reply Box - THE MOST IMPORTANT PART */}
            <ReplyBox
              ticket={ticket}
              onReply={handleReply}
              sending={sendingReply}
            />

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <button
                  onClick={handleMarkResolved}
                  disabled={ticket.status === 'resolved' || sendingReply}
                  className="w-full flex items-center justify-center bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-3 rounded-lg font-medium transition-colors"
                >
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  Mark as Resolved
                </button>
                <button className="w-full flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-medium transition-colors">
                  <RotateCcw className="w-5 h-5 mr-2" />
                  Reassign to Another Agent
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

#### `web-form/app/components/admin/ReplyBox.tsx`

```typescript
/**
 * Reply Box Component - Human In The Loop Interface
 * THIS IS WHERE THE HUMAN REPLY ACTUALLY HAPPENS
 */
'use client';

import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ReplyBoxProps {
  ticket: any;
  onReply: (replyData: any) => Promise<void>;
  sending: boolean;
}

export default function ReplyBox({ ticket, onReply, sending }: ReplyBoxProps) {
  const [reply, setReply] = useState('');
  const [selectedChannel, setSelectedChannel] = useState(ticket.channel);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!reply.trim()) {
      return;
    }

    await onReply({
      message: reply,
      channel: selectedChannel
    });

    setReply('');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      <div className="bg-blue-600 p-4">
        <h2 className="text-xl font-bold text-white mb-2">
          💬 Reply to Customer
        </h2>
        <p className="text-blue-100 text-sm">
          Send via: {selectedChannel.replace('_', ' ').toUpperCase()}
        </p>
      </div>

      <div className="p-6">
        {/* Customer Message */}
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 mb-6">
          <div className="flex items-start mb-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              👤
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                Customer's Message
              </p>
              <p className="text-gray-900 dark:text-white">
                {ticket.latest_message || 'No recent message'}
              </p>
            </div>
          </div>
        </div>

        {/* Reply Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Channel Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Send Reply Via
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="channel"
                  value="email"
                  checked={selectedChannel === 'email'}
                  onChange={(e) => setSelectedChannel('email')}
                  className="mr-2"
                />
                <span className="text-gray-900 dark:text-white">📧 Email</span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="channel"
                  value="whatsapp"
                  checked={selectedChannel === 'whatsapp'}
                  onChange={(e) => setSelectedChannel('whatsapp')}
                  className="mr-2"
                />
                <span className="text-gray-900 dark:text-white">💬 WhatsApp</span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="channel"
                  value="web_form"
                  checked={selectedChannel === 'web_form'}
                  onChange={(e) => setSelectedChannel('web_form')}
                  className="mr-2"
                />
                <span className="text-gray-900 dark:text-white">🌐 Web Form</span>
              </label>
            </div>
          </div>

          {/* Reply Text Area */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Your Reply
            </label>
            <textarea
              value={reply}
              onChange={(e) => setReply(e.target.value)}
              placeholder="Type your reply here... The customer will receive this via the selected channel."
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-900 dark:text-white"
              rows={6}
            />
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={sending || !reply.trim()}
            className="w-full flex items-center justify-center bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            {sending ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="w-5 h-5 mr-2" />
                Send Reply
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## Frontend API Routes

### `web-form/app/api/tickets/[id]/route.ts`

```typescript
/**
 * API Route for Ticket Detail - Used by Customer Status Page
 */
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const ticketId = params.id;

  try {
    // Fetch ticket details from backend
    const response = await fetch(`${process.env.BACKEND_URL}/api/tickets/${ticketId}`);

    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json({ error: 'Ticket not found' }, { status: 404 });
      }
      return NextResponse.json({ error: 'Failed to fetch ticket' }, { status: 500 });
    }

    const ticket = await response.json();

    return NextResponse.json(ticket);
  } catch (error) {
    console.error('Error fetching ticket:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

### `web-form/app/api/tickets/route.ts`

```typescript
/**
 * API Route for Creating Tickets
 */
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // Forward to backend API
    const response = await fetch(`${process.env.BACKEND_URL}/api/tickets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to create ticket' }, { status: 500 });
    }

    const result = await response.json();

    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    console.error('Error creating ticket:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

---

## Frontend Deliverables Checklist

Before completing the frontend, ensure you have:

### ☐ Customer Side Pages
- [ ] `/support` page - Support form with validation
- [ ] `/support/ticket/[id]` page - Ticket status display
- [ ] Form components with react-hook-form + zod validation
- [ ] Success/error states with proper UI feedback
- [ ] Responsive design with Tailwind CSS
- [ ] Loading states for better UX

### ☐ Admin Side Pages
- [ ] `/admin` page - Dashboard with metrics overview
- [ ] Stats cards showing total, resolved, escalated, avg response time
- [ ] Channel metrics with visual charts
- [ ] Escalation queue (MOST IMPORTANT) with pending items
- [ ] `/admin/tickets` page - All tickets table with filters
- [ ] Tickets table with sorting and filtering
- [ ] `/admin/tickets/[id]` page - Single ticket detail
- [ ] Reply box with channel selection (email/WhatsApp/web)
- [ ] Conversation history display
- [ ] Customer history across all channels
- [ ] Quick actions (Mark resolved, Reassign)
- [ ] Admin authentication middleware

### ☐ Integration
- [ ] API routes connecting to backend
- [ ] Environment variables configured
- [ ] TypeScript configurations set up
- [ ] Tailwind CSS properly configured
- [ ] All components properly organized (customer/ vs admin/)

### ☐ Polish
- [ ] Loading states on all pages
- [ ] Error handling and user feedback
- [ ] Responsive design for mobile/tablet/desktop
- [ ] Dark mode support
- [ ] Accessibility (ARIA labels, keyboard navigation)
- [ ] Consistent styling across all pages

---

## How All 5 Pages Connect Together

```
Customer Journey:
/support → fills form → creates ticket → /support/ticket/[id] → checks status
                                                        ↓
                                                    (if not resolved, customer can reply)

Admin Workflow:
/admin → sees dashboard & escalation queue
        ↓
/admin/tickets → sees all tickets → clicks ticket
        ↓
/admin/tickets/[id] → reads full conversation + customer history
        ↓
                     types reply → selects channel → clicks Send Reply
        ↓
          Backend sends reply via Gmail API (if email selected)
                          OR Twilio API (if WhatsApp selected)
                          OR saves response (if web form)
        ↓
          Updates ticket to "resolved" in database
        ↓
        Customer receives human reply via original channel
        ↓
        Admin goes back to /admin/tickets → next ticket
```

**This is the complete 5-page Next.js implementation with proper customer/admin separation!**

### Task: Build Complete Web Form (REQUIRED DELIVERABLE)

This is a **required deliverable**. You must build a complete, production-ready support form in Next.js.

### Setup Next.js Project

```bash
# Create Next.js project in web-form directory
cd web-form
npx create-next-app@latest . --typescript --tailwind --eslint --app --no-src-dir

# Install additional dependencies
npm install @radix-ui/react-dialog @radix-ui/react-select @radix-ui/react-label
npm install class-variance-authority clsx tailwind-merge lucide-react
npm install react-hook-form zod @hookform/resolvers
```

### Form Component

#### `web-form/app/components/SupportForm.tsx`

```typescript
/**
 * Web Support Form Component
 * Complete, production-ready support form with validation
 */

'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2, Send, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

const CATEGORIES = [
  { value: 'general', label: 'General Question' },
  { value: 'technical', label: 'Technical Support' },
  { value: 'billing', label: 'Billing Inquiry' },
  { value: 'feedback', label: 'Product Feedback' },
  { value: 'bug_report', label: 'Bug Report' }
] as const;

const PRIORITIES = [
  { value: 'low', label: 'Low - Not urgent' },
  { value: 'medium', label: 'Medium - Need help soon' },
  { value: 'high', label: 'High - Urgent issue' }
] as const;

const formSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  subject: z.string().min(5, 'Subject must be at least 5 characters'),
  category: z.enum(['general', 'technical', 'billing', 'feedback', 'bug_report']),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
  message: z.string().min(10, 'Message must be at least 10 characters')
});

type FormData = z.infer<typeof formSchema>;

export default function SupportForm() {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');
  const [ticketId, setTicketId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      category: 'general',
      priority: 'medium'
    }
  });

  const onSubmit = async (data: FormData) => {
    setStatus('submitting');
    setError(null);

    try {
      const response = await fetch('/api/support/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Submission failed');
      }

      const result = await response.json();
      setTicketId(result.ticket_id);
      setStatus('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStatus('error');
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setTicketId(null);
    setError(null);
    reset();
  };

  if (status === 'success') {
    return (
      <div className="max-w-2xl mx-auto p-8 bg-white rounded-lg shadow-lg">
        <div className="text-center space-y-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="w-10 h-10 text-green-600" />
          </div>

          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Thank You!
            </h2>
            <p className="text-lg text-gray-600">
              Your support request has been submitted successfully.
            </p>
          </div>

          <div className="bg-gray-50 rounded-lg p-6 space-y-4">
            <div>
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Your Ticket Number
              </p>
              <p className="text-2xl font-mono font-bold text-gray-900">
                {ticketId ? `TKT-${Math.abs(hash(ticketId || '')) % 100000:05d}` : 'N/A'}
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>
                Our AI assistant will respond to your email within 5 minutes.
              </span>
            </div>
          </div>

          <button
            onClick={handleReset}
            className="mt-8 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Submit Another Request
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-8 bg-white rounded-lg shadow-lg">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Contact Support
        </h2>
        <p className="text-lg text-gray-600">
          Fill out the form below and our AI-powered support team will get back to you shortly.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium">Error</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Name Field */}
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Your Name <span className="text-red-500">*</span>
          </label>
          <input
            {...register('name')}
            type="text"
            id="name"
            className={cn(
              "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all",
              errors.name ? "border-red-300 focus:ring-red-500" : "border-gray-300"
            )}
            placeholder="John Doe"
            disabled={status === 'submitting'}
          />
          {errors.name && (
            <p className="mt-2 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        {/* Email Field */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email Address <span className="text-red-500">*</span>
          </label>
          <input
            {...register('email')}
            type="email"
            id="email"
            className={cn(
              "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all",
              errors.email ? "border-red-300 focus:ring-red-500" : "border-gray-300"
            )}
            placeholder="john@example.com"
            disabled={status === 'submitting'}
          />
          {errors.email && (
            <p className="mt-2 text-sm text-red-600">{errors.email.message}</p>
          )}
        </div>

        {/* Subject Field */}
        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
            Subject <span className="text-red-500">*</span>
          </label>
          <input
            {...register('subject')}
            type="text"
            id="subject"
            className={cn(
              "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all",
              errors.subject ? "border-red-300 focus:ring-red-500" : "border-gray-300"
            )}
            placeholder="Brief description of your issue"
            disabled={status === 'submitting'}
          />
          {errors.subject && (
            <p className="mt-2 text-sm text-red-600">{errors.subject.message}</p>
          )}
        </div>

        {/* Category and Priority Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              Category <span className="text-red-500">*</span>
            </label>
            <select
              {...register('category')}
              id="category"
              className={cn(
                "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all",
                errors.category ? "border-red-300 focus:ring-red-500" : "border-gray-300"
              )}
              disabled={status === 'submitting'}
            >
              {CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="mt-2 text-sm text-red-600">{errors.category.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <select
              {...register('priority')}
              id="priority"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              disabled={status === 'submitting'}
            >
              {PRIORITIES.map(pri => (
                <option key={pri.value} value={pri.value}>
                  {pri.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Message Field */}
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
            How can we help? <span className="text-red-500">*</span>
          </label>
          <textarea
            {...register('message')}
            id="message"
            rows={6}
            className={cn(
              "w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none",
              errors.message ? "border-red-300 focus:ring-red-500" : "border-gray-300"
            )}
            placeholder="Please describe your issue or question in detail..."
            disabled={status === 'submitting'}
          />
          <p className="mt-2 text-sm text-gray-500">
            {register('message').value?.length || 0}/2000 characters
          </p>
          {errors.message && (
            <p className="mt-2 text-sm text-red-600">{errors.message.message}</p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={status === 'submitting'}
          className={cn(
            "w-full py-4 px-6 rounded-lg font-medium text-white transition-all",
            status === 'submitting'
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-blue-600 hover:bg-blue-700"
          )}
        >
          {status === 'submitting' ? (
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Submitting...</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-2">
              <Send className="w-5 h-5" />
              <span>Submit Support Request</span>
            </div>
          )}
        </button>

        <p className="text-center text-sm text-gray-500">
          By submitting, you agree to our{' '}
          <a href="/privacy" className="text-blue-600 hover:underline">
            Privacy Policy
          </a>
        </p>
      </form>
    </div>
  );
}
```

### API Route for Form

#### `web-form/app/api/support/submit/route.ts`

```typescript
/**
 * API route for support form submissions
 * Handles form data and sends to backend
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward to FastAPI backend
    const response = await fetch('http://localhost:8000/support/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(errorData, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { detail: 'Failed to process submission' },
      { status: 500 }
    );
  }
}
```

---

## Exercise 2.4: OpenAI Agents SDK Implementation (4-5 hours)

### Task: Transform Prototype into Production Agent

Transform your Part 1 prototype into a production agent using OpenAI Agents SDK with multi-channel support.

### Install Dependencies

```bash
# Install OpenAI Agents SDK and dependencies
uv add openai anthropic psycopg2-binary
```

### Create Production Agent (Multi-File Architecture)

The agent implementation should be split into multiple files for better organization and maintainability:

#### File Structure:
```
src/agent/
├── __init__.py           # Package initialization
├── agent.py              # Main agent implementation
├── tools.py             # Agent tools (search_knowledge_base, create_ticket, etc.)
├── prompts.py           # Prompt templates for different channels
├── formatter.py         # Response formatter for channels
└── sentiment.py         # Sentiment analysis logic
```

#### `src/agent/customer_success_agent.py` (Legacy - See Multi-File Implementation Below)

```python
"""
Production Customer Success Agent using OpenAI Agents SDK
Transformed from Part 1 prototype to production-grade implementation
"""

from openai import OpenAI
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncpg
from datetime import datetime
import json

# Import database connection
from database.connection import get_db_pool

class Channel(str, Enum):
    """Supported communication channels."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class Priority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CustomerSuccessAgent:
    """Production-grade Customer Success Agent using OpenAI."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize agent with OpenAI client."""
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    async def process_message(
        self,
        message: str,
        channel: Channel,
        customer_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a customer message through the agent.

        Args:
            message: Customer's message content
            channel: Source channel
            customer_id: Customer's unique identifier
            conversation_id: Conversation ID for context

        Returns:
            Dict with response, sentiment, and escalation decision
        """
        # Get conversation history if available
        history = await self._get_conversation_history(conversation_id) if conversation_id else []

        # Get customer history across all channels
        customer_history = await self._get_customer_history(customer_id) if customer_id else []

        # Build messages for OpenAI
        messages = self._build_messages(
            message=message,
            history=history,
            customer_history=customer_history,
            channel=channel
        )

        # Call OpenAI with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self._get_tools(),
            temperature=0.7,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message

        # Analyze sentiment
        sentiment = await self._analyze_sentiment(message)

        # Determine escalation
        should_escalate, escalation_reason = await self._check_escalation(
            message=message,
            sentiment=sentiment,
            channel=channel,
            tool_calls=assistant_message.tool_calls or []
        )

        # Format response for channel
        formatted_response = self._format_for_channel(
            response_content=assistant_message.content or "",
            channel=channel,
            sentiment=sentiment
        )

        return {
            "response": formatted_response,
            "raw_response": assistant_message.content,
            "sentiment": sentiment,
            "should_escalate": should_escalate,
            "escalation_reason": escalation_reason,
            "tool_calls": assistant_message.tool_calls or [],
            "tokens_used": response.usage.total_tokens,
            "model": self.model
        }

    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        Define tools available to the agent.

        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search product documentation for relevant information. Use this when customer asks questions about product features, how to use something, or needs technical information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The customer's question or search terms"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_ticket",
                    "description": "Create a support ticket for tracking. ALWAYS create a ticket at the start of every conversation. Include source channel for proper tracking.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "Unique customer identifier (email or phone)"
                            },
                            "issue": {
                                "type": "string",
                                "description": "Description of the issue or question"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Priority level of the ticket"
                            },
                            "category": {
                                "type": "string",
                                "description": "Category of the inquiry",
                                "enum": ["general", "technical", "billing", "feedback", "bug_report"]
                            },
                            "channel": {
                                "type": "string",
                                "enum": ["email", "whatsapp", "web_form"],
                                "description": "Source channel of the inquiry"
                            }
                        },
                        "required": ["customer_id", "issue", "channel"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_customer_history",
                    "description": "Get customer's complete interaction history across ALL channels. Use this to understand context from previous conversations, even if they happened on a different channel.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "string",
                                "description": "Unique customer identifier (email or phone)"
                            }
                        },
                        "required": ["customer_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_human",
                    "description": "Escalate conversation to human support. Use this when: Customer asks about pricing or refunds, Customer sentiment is negative, You cannot find relevant information, Customer explicitly requests human help.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {
                                "type": "string",
                                "description": "The ticket ID being escalated"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Reason for escalation"
                            },
                            "urgency": {
                                "type": "string",
                                "enum": ["low", "normal", "high", "critical"],
                                "description": "Urgency level of the escalation",
                                "default": "normal"
                            }
                        },
                        "required": ["ticket_id", "reason"]
                    }
                }
            }
        ]

    def _build_messages(
        self,
        message: str,
        history: List[Dict],
        customer_history: List[Dict],
        channel: Channel
    ) -> List[Dict[str, str]]:
        """
        Build message list for OpenAI API.

        Args:
            message: Current customer message
            history: Current conversation history
            customer_history: Full customer history across channels
            channel: Source channel

        Returns:
            List of messages for OpenAI API
        """
        system_prompt = self._get_system_prompt(channel)

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 10 messages)
        for msg in history[-10:]:
            messages.append({
                "role": "user" if msg['role'] == 'customer' else "assistant",
                "content": msg['content']
            })

        # Add current message
        messages.append({"role": "user", "content": message})

        # Add customer history context if available
        if customer_history:
            context_msg = f"""
Customer History Summary:
- Total interactions: {len(customer_history)}
- Previous channels: {', '.join(set(m['channel'] for m in customer_history))}
- Average sentiment: {sum(m.get('sentiment_score', 0.5) for m in customer_history) / len(customer_history):.2f}
"""
            messages.append({"role": "system", "content": context_msg})

        return messages

    def _get_system_prompt(self, channel: Channel) -> str:
        """
        Generate system prompt with channel awareness.

        Args:
            channel: The communication channel

        Returns:
            System prompt string
        """
        channel_instructions = {
            Channel.EMAIL: {
                "style": "Formal and detailed",
                "max_length": 2000,
                "include_signature": True,
                "greeting": "Dear Customer,",
                "closing": "Best regards,\nTechFlow AI Support Team"
            },
            Channel.WHATSAPP: {
                "style": "Conversational and concise",
                "max_length": 160,
                "include_signature": False,
                "greeting": "Hi there!",
                "closing": "Let me know if you need more help!"
            },
            Channel.WEB_FORM: {
                "style": "Semi-formal and helpful",
                "max_length": 1000,
                "include_signature": False,
                "greeting": "Hello,",
                "closing": "Thanks for reaching out!"
            }
        }[channel]

        return f"""You are a Customer Success agent for TechFlow SaaS.

# Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

# Channel Awareness
You are responding via: {channel.value.upper()}
Communication Style: {channel_instructions['style']}
Maximum Response Length: {channel_instructions['max_length']} characters

# Channel-Specific Guidelines
- Greeting: {channel_instructions['greeting']}
- Closing: {channel_instructions['closing']}
- Signature: {"Include" if channel_instructions['include_signature'] else "Do not include"} a signature

# Core Behaviors
1. ALWAYS create a ticket at conversation start (include channel!)
2. Check customer history ACROSS ALL CHANNELS before responding
3. Search knowledge base before answering product questions
4. Be concise on WhatsApp, detailed on email
5. Monitor sentiment - escalate if customer becomes frustrated

# Hard Constraints
- NEVER discuss pricing - escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds - escalate to billing
- NEVER share internal processes or systems
- Use appropriate tools (search_knowledge_base, create_ticket, etc.)

# Escalation Triggers
- Customer mentions "lawyer", "legal", or "sue"
- Customer uses profanity or aggressive language
- You cannot find relevant information after 2 searches
- Customer explicitly requests human help
- Sentiment score below 0.3 (very negative)

# Cross-Channel Continuity
If a customer has contacted us before (any channel), acknowledge it:
"I see you contacted us previously about X. Let me help you further..."
"""

    async def _get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Retrieve conversation history from database."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT role, content, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT 20
            """, conversation_id)

            return [
                {
                    "role": row['role'],
                    "content": row['content'],
                    "created_at": row['created_at'].isoformat()
                }
                for row in rows
            ]

    async def _get_customer_history(self, customer_id: str) -> List[Dict]:
        """Retrieve customer's full history across all channels."""
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT c.initial_channel, c.started_at, c.status,
                       m.content, m.role, m.channel, m.created_at,
                       c.sentiment_score
                FROM conversations c
                JOIN messages m ON m.conversation_id = c.id
                WHERE c.customer_id = $1
                ORDER BY m.created_at DESC
                LIMIT 20
            """, customer_id)

            return [
                {
                    "channel": row['initial_channel'],
                    "role": row['role'],
                    "content": row['content'],
                    "created_at": row['created_at'].isoformat(),
                    "sentiment_score": float(row['sentiment_score']) if row['sentiment_score'] else 0.5
                }
                for row in rows
            ]

    async def _analyze_sentiment(self, message: str) -> str:
        """Analyze sentiment using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analyzer. Classify the sentiment as 'positive', 'neutral', or 'negative'. Return only the classification."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0
            )

            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return "neutral"

    async def _check_escalation(
        self,
        message: str,
        sentiment: str,
        channel: Channel,
        tool_calls: List[Any]
    -> tuple[bool, str]:
        """Determine if escalation is needed."""
        # Check negative sentiment
        if sentiment == "negative":
            return True, "Negative customer sentiment detected"

        # Check for billing/legal keywords
        billing_keywords = ['refund', 'payment dispute', 'pricing negotiation', 'legal', 'lawyer', 'sue']
        if any(kw in message.lower() for kw in billing_keywords):
            return True, "Billing or legal inquiry"

        # Check if tools couldn't find information
        if tool_calls and len(tool_calls) > 2:
            return True, "Unable to find relevant information after multiple searches"

        # Check for human request
        if 'human' in message.lower() or 'agent' in message.lower():
            return True, "Customer explicitly requested human support"

        return False, ""

    def _format_for_channel(
        self,
        response_content: str,
        channel: Channel,
        sentiment: str
    ) -> str:
        """Format response for specific channel."""
        # Truncate for WhatsApp if needed
        if channel == Channel.WHATSAPP and len(response_content) > 160:
            response_content = response_content[:157] + "..."

        # Add escalation note for negative sentiment
        if sentiment == "negative":
            escalation_note = "\n\nI understand this is frustrating. A human specialist will review your case shortly."
            response_content += escalation_note

        return response_content
```

---

### Production-Grade Multi-File Agent Implementation

For production, replace the single-file implementation with this multi-file architecture:

#### `src/agent/agent.py`

```python
"""
Main Agent implementation using OpenAI Agents SDK
Production-grade Customer Success Agent
"""

from agents import Agent, Runner, function_tool
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

# Import agent components
from src.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    update_ticket_status,
    escalate_to_human,
    check_sla_status
)
from src.agent.prompts import get_system_prompt, get_context_prompt
from src.agent.sentiment import analyze_sentiment, SentimentAnalyzer
from src.agent.formatter import ResponseFormatter

class Channel(str, Enum):
    """Supported communication channels."""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class Priority(str, Enum):
    """Ticket priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CustomerSuccessAgent:
    """Production-grade Customer Success Agent using OpenAI Agents SDK."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.7):
        """Initialize customer success agent."""
        self.model = model
        self.temperature = temperature
        self.sentiment_analyzer = SentimentAnalyzer()
        self.formatter = ResponseFormatter()

        # Create the agent with tools
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create an OpenAI Agents SDK agent with tools."""
        return Agent(
            name="customer_success_agent",
            instructions=self._get_base_instructions(),
            model=self.model,
            tools=[
                search_knowledge_base,
                create_ticket,
                get_customer_history,
                update_ticket_status,
                escalate_to_human,
                check_sla_status
            ]
        )

    def _get_base_instructions(self) -> str:
        """Get base agent instructions."""
        return """You are a Customer Success agent for TechFlow SaaS.

# Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

# Core Behaviors
1. ALWAYS create a ticket at conversation start (include channel!)
2. Check customer history ACROSS ALL CHANNELS before responding
3. Search knowledge base before answering product questions
4. Be concise on WhatsApp, detailed on email
5. Monitor sentiment - escalate if customer becomes frustrated

# Hard Constraints
- NEVER discuss pricing - escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds - escalate to billing
- NEVER share internal processes or systems
- Use appropriate tools for information gathering

# Escalation Triggers
- Customer mentions "lawyer", "legal", or "sue"
- Customer uses profanity or aggressive language
- You cannot find relevant information after 2 searches
- Customer explicitly requests human help
- Sentiment score below 0.3 (very negative)

# Cross-Channel Continuity
If a customer has contacted us before (any channel), acknowledge it.
"""

    async def process_message(
        self,
        message: str,
        channel: Channel,
        customer_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a customer message through the agent.

        Args:
            message: Customer's message content
            channel: Source channel
            customer_id: Customer's unique identifier
            conversation_id: Conversation ID for context
            ticket_id: Existing ticket ID if applicable

        Returns:
            Dict with response, sentiment, and escalation decision
        """
        start_time = datetime.now()

        try:
            # Analyze sentiment of the message
            sentiment_result = await self.sentiment_analyzer.analyze(message)
            sentiment = sentiment_result["sentiment"]
            sentiment_score = sentiment_result["score"]

            # Build context for the agent
            context = await get_context_prompt(
                message=message,
                channel=channel,
                customer_id=customer_id,
                conversation_id=conversation_id,
                ticket_id=ticket_id
            )

            # Add channel-specific instructions
            system_instructions = get_system_prompt(channel)

            # Create input for the agent
            agent_input = {
                "message": message,
                "channel": channel.value,
                "context": context,
                "sentiment": sentiment
            }

            # Run the agent
            result = await Runner.run(
                self.agent,
                input=agent_input
            )

            # Extract the response
            response_content = result.final_output

            # Format response for channel
            formatted_response = self.formatter.format_for_channel(
                response=response_content,
                channel=channel,
                sentiment=sentiment
            )

            # Calculate processing time
            latency = int((datetime.now() - start_time).total_seconds() * 1000)

            # Determine if escalation is needed
            should_escalate, escalation_reason = self._check_escalation(
                sentiment=sentiment,
                sentiment_score=sentiment_score,
                message=message
            )

            return {
                "response": formatted_response,
                "raw_response": response_content,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "should_escalate": should_escalate,
                "escalation_reason": escalation_reason,
                "latency_ms": latency,
                "model": self.model,
                "tools_used": result.tool_calls,
                "tokens_used": result.usage.total_tokens if hasattr(result, 'usage') else 0
            }

        except Exception as e:
            # Handle errors gracefully
            return {
                "response": self.formatter.format_error(channel, str(e)),
                "raw_response": "",
                "sentiment": "unknown",
                "sentiment_score": 0.0,
                "should_escalate": True,
                "escalation_reason": f"Agent error: {str(e)}",
                "latency_ms": int((datetime.now() - start_time).total_seconds() * 1000),
                "model": self.model,
                "error": str(e)
            }

    def _check_escalation(
        self,
        sentiment: str,
        sentiment_score: float,
        message: str
    ) -> tuple[bool, str]:
        """
        Check if conversation should be escalated to human.

        Args:
            sentiment: Sentiment label (positive, neutral, negative)
            sentiment_score: Sentiment score (0.0 to 1.0)
            message: Original message content

        Returns:
            Tuple of (should_escalate, reason)
        """
        # Check for escalation keywords
        escalation_keywords = ["lawyer", "legal", "sue", "complaint", "unacceptable"]
        message_lower = message.lower()

        for keyword in escalation_keywords:
            if keyword in message_lower:
                return True, f"Escalation keyword detected: '{keyword}'"

        # Check sentiment score
        if sentiment_score < 0.3:
            return True, f"Very negative sentiment detected (score: {sentiment_score:.2f})"

        # Check sentiment label
        if sentiment == "negative":
            return True, "Negative sentiment detected"

        return False, ""

    async def process_with_history(
        self,
        message: str,
        channel: Channel,
        conversation_history: List[Dict[str, Any]],
        customer_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        ticket_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process message with explicit conversation history.

        Args:
            message: Current message
            channel: Source channel
            conversation_history: List of previous messages
            customer_id: Customer ID
            conversation_id: Conversation ID
            ticket_id: Ticket ID

        Returns:
            Dict with response and metadata
        """
        # Add conversation history to context
        history_context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-10:]  # Last 10 messages
        ])

        # Add history to message
        message_with_history = f"""
Previous conversation:
{history_context}

Current message: {message}
"""

        return await self.process_message(
            message=message_with_history,
            channel=channel,
            customer_id=customer_id,
            conversation_id=conversation_id,
            ticket_id=ticket_id
        )
```

#### `src/agent/tools.py`

```python
"""
Agent tools for OpenAI Agents SDK
Functional tools that the agent can use
"""

from agents import function_tool
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

# Import repositories
from src.database.repositories.knowledge_repo import KnowledgeRepository
from src.database.repositories.customer_repo import CustomerRepository
from src.database.repositories.ticket_repo import TicketRepository
from src.core.database import get_session


@function_tool
async def search_knowledge_base(
    query: str,
    max_results: int = 5,
    category: Optional[str] = None
) -> str:
    """
    Search product documentation for relevant information.

    Use this when customer asks questions about product features, how to use something,
    or needs technical information.

    Args:
        query: The customer's question or search terms
        max_results: Maximum number of results to return (default: 5)
        category: Optional category filter (e.g., 'technical', 'billing')

    Returns:
        Formatted search results with relevant information
    """
    async with get_session() as session:
        knowledge_repo = KnowledgeRepository()

        try:
            # Try semantic search first
            results = await knowledge_repo.full_text_search(
                session=session,
                search_term=query,
                limit=max_results
            )

            if not results:
                return "I couldn't find specific information about that in our knowledge base. Would you like me to escalate this to a specialist who can provide more detailed assistance?"

            # Format results
            formatted_results = []
            for i, kb in enumerate(results[:max_results], 1):
                formatted_results.append(
                    f"{i}. {kb.title}\n"
                    f"{kb.content[:500]}...\n"
                    f"Category: {kb.category}\n"
                )

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"


@function_tool
async def create_ticket(
    customer_id: str,
    issue: str,
    priority: str = "medium",
    category: str = "general",
    channel: str = "web_form"
) -> str:
    """
    Create a support ticket for tracking.

    ALWAYS create a ticket at the start of every conversation.
    Include the source channel for proper tracking.

    Args:
        customer_id: Unique customer identifier (email or phone)
        issue: Description of the issue or question
        priority: Priority level (low, medium, high, critical)
        category: Category of inquiry (general, technical, billing, feedback, bug_report)
        channel: Source channel (email, whatsapp, web_form)

    Returns:
        Ticket creation confirmation with ticket number
    """
    async with get_session() as session:
        ticket_repo = TicketRepository()
        customer_repo = CustomerRepository()

        try:
            # Get or create customer
            customer = await customer_repo.get_by_email(session, customer_id)
            if not customer:
                customer = await customer_repo.create(
                    session,
                    email=customer_id,
                    name="Customer"
                )

            # Create ticket
            ticket = await ticket_repo.create(
                session,
                customer_id=customer.id,
                ticket_number=f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                source_channel=channel,
                category=category,
                priority=priority,
                status="open"
            )

            return f"Ticket created successfully! Your ticket number is {ticket.ticket_number}. We'll get back to you as soon as possible."

        except Exception as e:
            return f"Error creating ticket: {str(e)}"


@function_tool
async def get_customer_history(
    customer_identifier: str
) -> str:
    """
    Get customer's support history across all channels.

    Use this to understand if a customer has contacted us before
    and what previous issues were resolved.

    Args:
        customer_identifier: Customer email or phone number

    Returns:
        Summary of customer's support history
    """
    async with get_session() as session:
        customer_repo = CustomerRepository()
        ticket_repo = TicketRepository()

        try:
            # Get customer
            customer = await customer_repo.get_by_email(session, customer_identifier)
            if not customer:
                return "No previous support history found for this customer."

            # Get customer's tickets
            tickets = await ticket_repo.get_by_customer(session, customer.id, limit=10)

            if not tickets:
                return f"Customer {customer.name} has no previous tickets."

            # Format history
            history_summary = f"Customer: {customer.name} ({customer.email})\n"
            history_summary += f"Total Tickets: {len(tickets)}\n"
            history_summary += f"Previous Contacts: {customer.total_conversations}\n\n"
            history_summary += "Recent Tickets:\n"

            for ticket in tickets[:5]:
                history_summary += f"- {ticket.ticket_number}: {ticket.category} ({ticket.status})\n"

            return history_summary

        except Exception as e:
            return f"Error retrieving customer history: {str(e)}"


@function_tool
async def update_ticket_status(
    ticket_number: str,
    status: str,
    resolution_notes: Optional[str] = None
) -> str:
    """
    Update ticket status.

    Use this when resolving a ticket or changing its status.

    Args:
        ticket_number: Ticket number to update
        status: New status (open, in_progress, resolved, escalated)
        resolution_notes: Optional notes about the resolution

    Returns:
        Update confirmation
    """
    async with get_session() as session:
        ticket_repo = TicketRepository()

        try:
            ticket = await ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                return f"Ticket {ticket_number} not found."

            # Update status
            kwargs = {"status": status}
            if resolution_notes:
                kwargs["resolution_notes"] = resolution_notes

            updated_ticket = await ticket_repo.update(session, ticket.id, **kwargs)

            return f"Ticket {ticket_number} updated to status: {status}"

        except Exception as e:
            return f"Error updating ticket: {str(e)}"


@function_tool
async def escalate_to_human(
    ticket_number: str,
    reason: str,
    priority: str = "high"
) -> str:
    """
    Escalate ticket to human specialist.

    Use this when an issue requires human intervention.

    Args:
        ticket_number: Ticket number to escalate
        reason: Reason for escalation
        priority: Escalation priority (medium, high, critical)

    Returns:
        Escalation confirmation
    """
    async with get_session() as session:
        ticket_repo = TicketRepository()

        try:
            ticket = await ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                return f"Ticket {ticket_number} not found."

            # Update ticket status and priority
            await ticket_repo.update(session, ticket.id, status="escalated", priority=priority)

            return f"Ticket {ticket_number} has been escalated to a human specialist. Reason: {reason}. A specialist will review your case shortly."

        except Exception as e:
            return f"Error escalating ticket: {str(e)}"


@function_tool
async def check_sla_status(
    ticket_number: str
) -> str:
    """
    Check if ticket is within SLA (Service Level Agreement) timeframe.

    Use this to ensure timely response to high-priority tickets.

    Args:
        ticket_number: Ticket number to check

    Returns:
        SLA status information
    """
    async with get_session() as session:
        ticket_repo = TicketRepository()

        try:
            ticket = await ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                return f"Ticket {ticket_number} not found."

            if not ticket.sla_target:
                return f"No SLA target set for ticket {ticket_number}."

            from datetime import datetime
            time_remaining = (ticket.sla_target - datetime.now()).total_seconds()

            if time_remaining < 0:
                return f"⚠️ Ticket {ticket_number} is OVERDUE by {abs(time_remaining):.0f} seconds!"

            hours = int(time_remaining // 3600)
            minutes = int((time_remaining % 3600) // 60)

            return f"✓ Ticket {ticket_number} is within SLA. Time remaining: {hours}h {minutes}m"

        except Exception as e:
            return f"Error checking SLA status: {str(e)}"
```

#### `src/agent/prompts.py`

```python
"""
Prompt templates for the agent
Channel-specific and contextual prompts
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

# Channel-specific instructions
CHANNEL_INSTRUCTIONS = {
    "email": {
        "style": "Professional and detailed",
        "max_length": 1000,
        "include_signature": True,
        "greeting": "Dear Customer,",
        "closing": "Best regards,\nCustomer Support Team"
    },
    "whatsapp": {
        "style": "Conversational and concise",
        "max_length": 160,
        "include_signature": False,
        "greeting": "Hi there! 👋",
        "closing": "Let me know if you need more help!"
    },
    "web_form": {
        "style": "Semi-formal and helpful",
        "max_length": 1000,
        "include_signature": False,
        "greeting": "Hello,",
        "closing": "Thanks for reaching out!"
    }
}

# Escalation triggers
ESCALATION_TRIGGERS = [
    "lawyer", "legal", "sue", "complaint", "unacceptable",
    "refund", "cancel subscription", "billing dispute"
]

# Restricted topics
RESTRICTED_TOPICS = [
    "pricing", "enterprise plans", "discounts", "refunds",
    "legal", "compliance", "security audit", "custom features"
]


def get_system_prompt(channel: str) -> str:
    """
    Get system prompt for a specific channel.

    Args:
        channel: Channel identifier

    Returns:
        System prompt string
    """
    instructions = CHANNEL_INSTRUCTIONS.get(channel, CHANNEL_INSTRUCTIONS["email"])

    return f"""You are a Customer Success agent for TechFlow SaaS.

# Channel Context
You are responding via: {channel.upper()}
Communication Style: {instructions['style']}
Maximum Response Length: {instructions['max_length']} characters

# Channel-Specific Guidelines
- Greeting: {instructions['greeting']}
- Closing: {instructions['closing']}
- Signature: {"Include" if instructions['include_signature'] else "Do not include"} a signature

# Core Behaviors
1. ALWAYS create a ticket at conversation start (include channel!)
2. Check customer history ACROSS ALL CHANNELS before responding
3. Search knowledge base before answering product questions
4. Be concise on WhatsApp, detailed on email
5. Monitor sentiment - escalate if customer becomes frustrated

# Hard Constraints
- NEVER discuss pricing - escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds - escalate to billing
- NEVER share internal processes or systems
- Use appropriate tools for information gathering

# Escalation Triggers
- Customer mentions: {', '.join(ESCALATION_TRIGGERS)}
- Customer uses profanity or aggressive language
- You cannot find relevant information after 2 searches
- Customer explicitly requests human help
- Sentiment score below 0.3 (very negative)

# Cross-Channel Continuity
If a customer has contacted us before (any channel), acknowledge it:
"I see you contacted us previously about X. Let me help you further..."
"""


def get_context_prompt(
    message: str,
    channel: str,
    customer_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    ticket_id: Optional[str] = None
) -> str:
    """
    Build context prompt for the agent.

    Args:
        message: Current message
        channel: Source channel
        customer_id: Customer ID
        conversation_id: Conversation ID
        ticket_id: Ticket ID

    Returns:
        Context string
    """
    context_parts = []

    # Add channel information
    context_parts.append(f"Message from {channel.upper()}")
    context_parts.append(f"Timestamp: {datetime.now().isoformat()}")

    # Add customer information
    if customer_id:
        context_parts.append(f"Customer ID: {customer_id}")

    # Add conversation information
    if conversation_id:
        context_parts.append(f"Conversation ID: {conversation_id}")

    # Add ticket information
    if ticket_id:
        context_parts.append(f"Ticket ID: {ticket_id}")

    return "\n".join(context_parts)


def build_conversation_context(
    history: List[Dict[str, Any]],
    max_messages: int = 10
) -> str:
    """
    Build conversation context from history.

    Args:
        history: List of conversation messages
        max_messages: Maximum number of messages to include

    Returns:
        Formatted conversation context
    """
    if not history:
        return "No previous conversation history."

    recent_history = history[-max_messages:]

    context_lines = ["# Previous Conversation"]
    for msg in recent_history:
        role = msg.get("role", "unknown").title()
        content = msg.get("content", "")
        timestamp = msg.get("created_at", "")

        context_lines.append(f"{role}: {content}")
        if timestamp:
            context_lines.append(f"Time: {timestamp}")

    return "\n".join(context_lines)


def get_customer_history_prompt(customer_history: Dict[str, Any]) -> str:
    """
    Build customer history prompt.

    Args:
        customer_history: Customer history data

    Returns:
        Formatted customer history prompt
    """
    if not customer_history or not customer_history.get("tickets"):
        return "No previous customer history."

    prompt = "# Customer Support History\n"

    # Add customer info
    if "name" in customer_history:
        prompt += f"Customer: {customer_history['name']}\n"
    if "email" in customer_history:
        prompt += f"Email: {customer_history['email']}\n"
    if "total_tickets" in customer_history:
        prompt += f"Total Tickets: {customer_history['total_tickets']}\n"

    prompt += "\n# Previous Tickets\n"

    # Add tickets
    for ticket in customer_history.get("tickets", [])[:5]:
        prompt += f"- {ticket.get('ticket_number', 'N/A')}: "
        prompt += f"{ticket.get('category', 'general')} "
        prompt += f"({ticket.get('status', 'unknown')})\n"

    return prompt


def get_escalation_prompt(reason: str, ticket_number: str) -> str:
    """
    Build escalation prompt for human agents.

    Args:
        reason: Reason for escalation
        ticket_number: Ticket number

    Returns:
        Escalation prompt
    """
    return f"""# Escalation Required

Ticket: {ticket_number}
Reason: {reason}
Escalated at: {datetime.now().isoformat()}

This ticket requires human intervention. Please review the conversation history and take appropriate action.
"""
```

#### `src/agent/formatter.py`

```python
"""
Response formatter for different channels
Format responses appropriately for each channel
"""

from typing import Dict, Any
from enum import Enum

class ResponseFormatter:
    """Format agent responses for different channels."""

    # Channel-specific configurations
    CHANNEL_CONFIGS = {
        "email": {
            "max_length": 10000,  # No strict limit
            "truncate_suffix": "...",
            "include_signature": True,
            "signature": "\n\nBest regards,\nCustomer Support Team\nTechFlow SaaS"
        },
        "whatsapp": {
            "max_length": 160,  # SMS/WhatsApp character limit
            "truncate_suffix": "...",
            "include_signature": False,
            "signature": ""
        },
        "web_form": {
            "max_length": 2000,
            "truncate_suffix": "...",
            "include_signature": False,
            "signature": ""
        }
    }

    def format_for_channel(
        self,
        response: str,
        channel: str,
        sentiment: str = "neutral"
    ) -> str:
        """
        Format response for a specific channel.

        Args:
            response: Raw agent response
            channel: Target channel
            sentiment: Message sentiment for adjustments

        Returns:
            Formatted response
        """
        config = self.CHANNEL_CONFIGS.get(channel, self.CHANNEL_CONFIGS["email"])

        # Add sentiment-based adjustments
        formatted = self._adjust_for_sentiment(response, sentiment)

        # Truncate if necessary
        if len(formatted) > config["max_length"]:
            formatted = formatted[:config["max_length"] - len(config["truncate_suffix"])]
            formatted += config["truncate_suffix"]

        # Add signature if required
        if config["include_signature"]:
            formatted += config["signature"]

        # Add emoji for WhatsApp
        if channel == "whatsapp":
            formatted = self._add_whatsapp_emoji(formatted)

        return formatted

    def _adjust_for_sentiment(self, response: str, sentiment: str) -> str:
        """
        Adjust response based on sentiment.

        Args:
            response: Original response
            sentiment: Sentiment category

        Returns:
            Adjusted response
        """
        if sentiment == "negative":
            # Add empathetic language for negative sentiment
            if "sorry" not in response.lower():
                response = "I'm sorry you're experiencing this issue. " + response
            if "help" not in response.lower():
                response += " I'm here to help you resolve this."

        elif sentiment == "positive":
            # Keep positive responses natural
            pass

        return response

    def _add_whatsapp_emoji(self, response: str) -> str:
        """
        Add appropriate emojis for WhatsApp responses.

        Args:
            response: Response text

        Returns:
            Response with emojis
        """
        # Add helpful emojis
        emoji_map = {
            "help": "🙋",
            "solved": "✅",
            "issue": "🔧",
            "question": "❓",
            "thanks": "😊",
            "sorry": "😔",
            "escalated": "📢"
        }

        for keyword, emoji in emoji_map.items():
            if keyword in response.lower():
                response = response.replace(keyword, f"{keyword} {emoji}")
                break  # Only add one emoji

        return response

    def format_error(self, channel: str, error: str) -> str:
        """
        Format error message for channel.

        Args:
            channel: Target channel
            error: Error message

        Returns:
            Formatted error message
        """
        if channel == "whatsapp":
            return f"⚠️ Sorry, I encountered an issue. Please try again or contact support directly."

        return f"I apologize, but I encountered an error: {error}. Please try again or contact our support team directly."

    def format_escalation(self, channel: str, ticket_number: str, reason: str) -> str:
        """
        Format escalation message for channel.

        Args:
            channel: Target channel
            ticket_number: Ticket number
            reason: Escalation reason

        Returns:
            Formatted escalation message
        """
        if channel == "whatsapp":
            return f"📢 Your ticket {ticket_number} has been escalated to a specialist. They'll review your case shortly."

        return f"Your ticket {ticket_number} has been escalated to a human specialist. Reason: {reason}. A specialist will review your case shortly."

    def format_ticket_created(self, channel: str, ticket_number: str) -> str:
        """
        Format ticket creation confirmation.

        Args:
            channel: Target channel
            ticket_number: Ticket number

        Returns:
            Formatted confirmation
        """
        if channel == "whatsapp":
            return f"✅ Ticket created! Reference: {ticket_number}"

        return f"Thank you! Your ticket has been created successfully.\n\nTicket Number: {ticket_number}\n\nWe'll get back to you as soon as possible."
```

#### `src/agent/sentiment.py`

```python
"""
Sentiment analysis for the agent
Analyze message sentiment to improve responses
"""

from typing import Dict, Any
from enum import Enum
import re

class Sentiment(Enum):
    """Sentiment categories."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class SentimentAnalyzer:
    """Analyze sentiment of customer messages."""

    # Positive sentiment indicators
    POSITIVE_WORDS = [
        "great", "good", "excellent", "perfect", "amazing", "love",
        "helpful", "thanks", "thank you", "appreciate", "wonderful",
        "fantastic", "awesome", "happy", "pleased", "satisfied"
    ]

    # Negative sentiment indicators
    NEGATIVE_WORDS = [
        "bad", "terrible", "awful", "horrible", "hate", "dislike",
        "frustrating", "frustrated", "annoying", "annoyed", "angry",
        "upset", "disappointed", "broken", "doesn't work", "not working",
        "useless", "waste", "stupid", "ridiculous", "unacceptable",
        "complaint", "refund", "cancel", "worst", "never again"
    ]

    # Profanity indicators (simplified list)
    PROFANITY_PATTERNS = [
        r"\bdamn\b", r"\bhell\b", r"\bshit\b", r"\bfuck\b",
        r"\bastupid\b", r"\bidiot\b", r"\bdumb\b"
    ]

    def __init__(self):
        """Initialize sentiment analyzer."""
        self.positive_set = set(word.lower() for word in self.POSITIVE_WORDS)
        self.negative_set = set(word.lower() for word in self.NEGATIVE_WORDS)
        self.profanity_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.PROFANITY_PATTERNS]

    async def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a message.

        Args:
            message: Message text to analyze

        Returns:
            Dict with sentiment category and score
        """
        # Calculate sentiment score
        score = self._calculate_sentiment_score(message)

        # Determine category
        if score > 0.1:
            category = Sentiment.POSITIVE.value
        elif score < -0.1:
            category = Sentiment.NEGATIVE.value
        else:
            category = Sentiment.NEUTRAL.value

        # Check for profanity
        has_profanity = self._check_profanity(message)

        return {
            "sentiment": category,
            "score": abs(score),  # Return absolute value for intensity
            "raw_score": score,
            "has_profanity": has_profanity,
            "confidence": self._calculate_confidence(score)
        }

    def _calculate_sentiment_score(self, message: str) -> float:
        """
        Calculate sentiment score from -1.0 (negative) to 1.0 (positive).

        Args:
            message: Message text

        Returns:
            Sentiment score
        """
        words = message.lower().split()
        positive_count = 0
        negative_count = 0

        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)

            if clean_word in self.positive_set:
                positive_count += 1
            elif clean_word in self.negative_set:
                negative_count += 1

        # Calculate score
        total = positive_count + negative_count
        if total == 0:
            return 0.0

        return (positive_count - negative_count) / total

    def _check_profanity(self, message: str) -> bool:
        """
        Check if message contains profanity.

        Args:
            message: Message text

        Returns:
            True if profanity detected
        """
        for pattern in self.profanity_patterns:
            if pattern.search(message):
                return True
        return False

    def _calculate_confidence(self, score: float) -> str:
        """
        Calculate confidence level for sentiment analysis.

        Args:
            score: Sentiment score

        Returns:
            Confidence level string
        """
        abs_score = abs(score)

        if abs_score < 0.1:
            return "low"
        elif abs_score < 0.3:
            return "medium"
        else:
            return "high"

    def get_sentiment_emoji(self, sentiment: str) -> str:
        """
        Get emoji for sentiment.

        Args:
            sentiment: Sentiment category

        Returns:
            Emoji character
        """
        emoji_map = {
            Sentiment.POSITIVE.value: "😊",
            Sentiment.NEUTRAL.value: "😐",
            Sentiment.NEGATIVE.value: "😔"
        }
        return emoji_map.get(sentiment, "😐")

    def should_escalate(self, sentiment_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Determine if message should trigger escalation.

        Args:
            sentiment_data: Sentiment analysis result

        Returns:
            Tuple of (should_escalate, reason)
        """
        # Check for profanity
        if sentiment_data.get("has_profanity", False):
            return True, "Profanity detected in message"

        # Check for very negative sentiment with high confidence
        if sentiment_data["sentiment"] == "negative":
            if sentiment_data["confidence"] == "high" and sentiment_data["score"] > 0.5:
                return True, "Strong negative sentiment detected"

        return False, ""
```

#### `src/agent/__init__.py`

```python
"""
Agent package initialization
"""

from src.agent.agent import CustomerSuccessAgent, Channel, Priority
from src.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    update_ticket_status,
    escalate_to_human,
    check_sla_status
)
from src.agent.prompts import (
    get_system_prompt,
    get_context_prompt,
    build_conversation_context,
    get_customer_history_prompt,
    get_escalation_prompt
)
from src.agent.formatter import ResponseFormatter
from src.agent.sentiment import SentimentAnalyzer, Sentiment

__all__ = [
    "CustomerSuccessAgent",
    "Channel",
    "Priority",
    "search_knowledge_base",
    "create_ticket",
    "get_customer_history",
    "update_ticket_status",
    "escalate_to_human",
    "check_sla_status",
    "get_system_prompt",
    "get_context_prompt",
    "build_conversation_context",
    "get_customer_history_prompt",
    "get_escalation_prompt",
    "ResponseFormatter",
    "SentimentAnalyzer",
    "Sentiment"
]
```

---

## Services Layer Implementation

The Services layer contains business logic that orchestrates between repositories and the agent/worker layers.

### File Structure:
```
src/services/
├── __init__.py           # Package initialization
├── customer_service.py    # Customer business logic
├── ticket_service.py      # Ticket lifecycle management
├── conversation_service.py # Conversation handling
└── metrics_service.py    # Analytics and metrics
```

### `src/services/customer_service.py`

```python
"""
Customer service - Customer-related business logic
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

# Import repositories
from src.database.repositories.customer_repo import CustomerRepository
from src.core.database import get_session


class CustomerService:
    """Service for customer-related business logic."""

    def __init__(self):
        """Initialize customer service."""
        self.customer_repo = CustomerRepository()

    async def get_or_create_customer(
        self,
        email: str,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get existing customer or create new one.

        Args:
            email: Customer email
            name: Customer name
            phone: Customer phone
            company: Customer company

        Returns:
            Customer data dictionary
        """
        async with get_session() as session:
            customer = await self.customer_repo.get_or_create_by_email(
                session,
                email,
                name=name or "Customer",
                phone=phone,
                company=company
            )

            return {
                "id": str(customer.id),
                "email": customer.email,
                "name": customer.name,
                "phone": customer.phone,
                "company": customer.company,
                "total_tickets": customer.total_tickets,
                "total_conversations": customer.total_conversations,
                "last_contact_at": customer.last_contact_at.isoformat() if customer.last_contact_at else None,
                "satisfaction_score": customer.satisfaction_score
            }

    async def update_customer_contact(
        self,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update customer's last contact timestamp and metadata.

        Args:
            customer_id: Customer ID
            metadata: Optional metadata to update

        Returns:
            Updated customer data
        """
        import uuid
        async with get_session() as session:
            customer = await self.customer_repo.get(session, uuid.UUID(customer_id))
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")

            # Update last contact
            updated_customer = await self.customer_repo.update_last_contact(session, uuid.UUID(customer_id))

            # Update metadata if provided
            if metadata:
                updated_customer = await self.customer_repo.update(
                    session,
                    uuid.UUID(customer_id),
                    metadata={**updated_customer.metadata, **metadata}
                )

            return {
                "id": str(updated_customer.id),
                "email": updated_customer.email,
                "name": updated_customer.name,
                "phone": updated_customer.phone,
                "company": updated_customer.company,
                "total_tickets": updated_customer.total_tickets,
                "total_conversations": updated_customer.total_conversations,
                "last_contact_at": updated_customer.last_contact_at.isoformat() if updated_customer.last_contact_at else None
            }

    async def search_customers(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search customers by name or email.

        Args:
            search_term: Search term
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of customer dictionaries
        """
        async with get_session() as session:
            customers = await self.customer_repo.search(session, search_term, skip, limit)

            return [
                {
                    "id": str(customer.id),
                    "email": customer.email,
                    "name": customer.name,
                    "phone": customer.phone,
                    "company": customer.company,
                    "total_tickets": customer.total_tickets,
                    "last_contact_at": customer.last_contact_at.isoformat() if customer.last_contact_at else None
                }
                for customer in customers
            ]

    async def get_customer_with_history(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Get customer with their full support history.

        Args:
            customer_id: Customer ID

        Returns:
            Customer with history
        """
        import uuid
        async with get_session() as session:
            customer = await self.customer_repo.get_with_conversations(session, uuid.UUID(customer_id))
            if not customer:
                raise ValueError(f"Customer {customer_id} not found")

            return {
                "id": str(customer.id),
                "email": customer.email,
                "name": customer.name,
                "phone": customer.phone,
                "company": customer.company,
                "total_tickets": customer.total_tickets,
                "total_conversations": customer.total_conversations,
                "conversations": [
                    {
                        "id": str(conv.id),
                        "initial_channel": conv.initial_channel,
                        "status": conv.status,
                        "started_at": conv.started_at.isoformat() if conv.started_at else None,
                        "ended_at": conv.ended_at.isoformat() if conv.ended_at else None
                    }
                    for conv in customer.conversations
                ]
            }
```

### `src/services/ticket_service.py`

```python
"""
Ticket service - Ticket lifecycle management
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

# Import repositories
from src.database.repositories.ticket_repo import TicketRepository
from src.database.repositories.customer_repo import CustomerRepository
from src.core.database import get_session


class TicketService:
    """Service for ticket-related business logic."""

    def __init__(self):
        """Initialize ticket service."""
        self.ticket_repo = TicketRepository()
        self.customer_repo = CustomerRepository()

    async def create_ticket(
        self,
        customer_email: str,
        issue: str,
        category: str = "general",
        priority: str = "medium",
        channel: str = "web_form"
    ) -> Dict[str, Any]:
        """
        Create a new support ticket.

        Args:
            customer_email: Customer email
            issue: Issue description
            category: Ticket category
            priority: Ticket priority
            channel: Source channel

        Returns:
            Created ticket data
        """
        async with get_session() as session:
            # Get or create customer
            customer = await self.customer_repo.get_or_create_by_email(
                session,
                customer_email,
                name="Customer"
            )

            # Generate ticket number
            ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # Set SLA based on priority
            sla_target = self._calculate_sla(priority)

            # Create ticket
            ticket = await self.ticket_repo.create(
                session,
                customer_id=customer.id,
                ticket_number=ticket_number,
                source_channel=channel,
                category=category,
                priority=priority,
                status="open",
                sla_target=sla_target
            )

            # Increment customer ticket count
            await self.customer_repo.increment_tickets(session, customer.id)

            return {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "customer_id": str(ticket.customer_id),
                "category": ticket.category,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
                "sla_target": ticket.sla_target.isoformat() if ticket.sla_target else None,
                "first_response_at": ticket.first_response_at.isoformat() if ticket.first_response_at else None
            }

    def _calculate_sla(self, priority: str) -> Optional[datetime]:
        """
        Calculate SLA target based on priority.

        Args:
            priority: Ticket priority

        Returns:
            SLA target datetime
        """
        sla_hours = {
            "critical": 1,   # 1 hour
            "high": 4,        # 4 hours
            "medium": 24,     # 24 hours
            "low": 72          # 72 hours (3 days)
        }

        hours = sla_hours.get(priority, 24)
        return datetime.now() + timedelta(hours=hours)

    async def update_ticket_status(
        self,
        ticket_number: str,
        status: str,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update ticket status.

        Args:
            ticket_number: Ticket number
            status: New status
            resolution_notes: Optional resolution notes

        Returns:
            Updated ticket data
        """
        async with get_session() as session:
            ticket = await self.ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                raise ValueError(f"Ticket {ticket_number} not found")

            # Update status
            updated_ticket = await self.ticket_repo.update_status(session, ticket.id, status)

            # Add resolution notes if provided
            if resolution_notes:
                updated_ticket = await self.ticket_repo.update(
                    session,
                    ticket.id,
                    resolution_notes=resolution_notes
                )

            return {
                "id": str(updated_ticket.id),
                "ticket_number": updated_ticket.ticket_number,
                "status": updated_ticket.status,
                "resolved_at": updated_ticket.resolved_at.isoformat() if updated_ticket.resolved_at else None,
                "resolution_notes": updated_ticket.resolution_notes
            }

    async def get_tickets_by_customer(
        self,
        customer_email: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all tickets for a customer.

        Args:
            customer_email: Customer email
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of ticket dictionaries
        """
        async with get_session() as session:
            customer = await self.customer_repo.get_by_email(session, customer_email)
            if not customer:
                return []

            tickets = await self.ticket_repo.get_by_customer(session, customer.id, skip, limit)

            return [
                {
                    "id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "created_at": ticket.created_at.isoformat(),
                    "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                    "sla_target": ticket.sla_target.isoformat() if ticket.sla_target else None
                }
                for ticket in tickets
            ]

    async def get_ticket_by_number(
        self,
        ticket_number: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get ticket details by number.

        Args:
            ticket_number: Ticket number

        Returns:
            Ticket data dictionary
        """
        async with get_session() as session:
            ticket = await self.ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                return None

            return {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "customer_id": str(ticket.customer_id),
                "category": ticket.category,
                "priority": ticket.priority,
                "status": ticket.status,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
                "resolution_notes": ticket.resolution_notes,
                "first_response_at": ticket.first_response_at.isoformat() if ticket.first_response_at else None,
                "sla_target": ticket.sla_target.isoformat() if ticket.sla_target else None
            }

    async def record_first_response(
        self,
        ticket_number: str
    ) -> Dict[str, Any]:
        """
        Record first response time for ticket.

        Args:
            ticket_number: Ticket number

        Returns:
            Updated ticket data
        """
        async with get_session() as session:
            ticket = await self.ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                raise ValueError(f"Ticket {ticket_number} not found")

            # Update first response time
            updated_ticket = await self.ticket_repo.update_first_response_at(session, ticket.id)

            return {
                "id": str(updated_ticket.id),
                "ticket_number": updated_ticket.ticket_number,
                "first_response_at": updated_ticket.first_response_at.isoformat() if updated_ticket.first_response_at else None
            }

    async def escalate_ticket(
        self,
        ticket_number: str,
        reason: str,
        priority: str = "high"
    ) -> Dict[str, Any]:
        """
        Escalate ticket to human.

        Args:
            ticket_number: Ticket number
            reason: Escalation reason
            priority: New priority for escalation

        Returns:
            Updated ticket data
        """
        async with get_session() as session:
            ticket = await self.ticket_repo.get_by_number(session, ticket_number)
            if not ticket:
                raise ValueError(f"Ticket {ticket_number} not found")

            # Update status to escalated
            updated_ticket = await self.ticket_repo.update_status(session, ticket.id, "escalated")

            # Update priority if needed
            if priority != ticket.priority:
                updated_ticket = await self.ticket_repo.update(session, ticket.id, priority=priority)

            return {
                "id": str(updated_ticket.id),
                "ticket_number": updated_ticket.ticket_number,
                "status": updated_ticket.status,
                "priority": updated_ticket.priority,
                "escalation_reason": reason
            }

    async def get_overdue_tickets(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get tickets past SLA target.

        Args:
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of overdue ticket dictionaries
        """
        async with get_session() as session:
            tickets = await self.ticket_repo.get_overdue_tickets(session, skip, limit)

            return [
                {
                    "id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "status": ticket.status,
                    "created_at": ticket.created_at.isoformat(),
                    "sla_target": ticket.sla_target.isoformat() if ticket.sla_target else None,
                    "hours_overdue": (datetime.now() - ticket.sla_target).total_seconds() / 3600 if ticket.sla_target else 0
                }
                for ticket in tickets
            ]
```

### `src/services/conversation_service.py`

```python
"""
Conversation service - Conversation handling
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

# Import repositories
from src.database.repositories.conversation_repo import ConversationRepository
from src.database.repositories.message_repo import MessageRepository
from src.core.database import get_session


class ConversationService:
    """Service for conversation-related business logic."""

    def __init__(self):
        """Initialize conversation service."""
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()

    async def start_conversation(
        self,
        customer_id: str,
        channel: str,
        initial_message: str
    ) -> Dict[str, Any]:
        """
        Start a new conversation.

        Args:
            customer_id: Customer ID
            channel: Channel type
            initial_message: First message content

        Returns:
            Conversation data
        """
        async with get_session() as session:
            # Create conversation
            conversation = await self.conversation_repo.create(
                session,
                customer_id=uuid.UUID(customer_id),
                initial_channel=channel,
                status="active"
            )

            # Create initial message
            message = await self.message_repo.create(
                session,
                conversation_id=conversation.id,
                channel=channel,
                direction="inbound",
                role="customer",
                content=initial_message
            )

            return {
                "id": str(conversation.id),
                "customer_id": str(conversation.customer_id),
                "initial_channel": conversation.initial_channel,
                "status": conversation.status,
                "started_at": conversation.started_at.isoformat(),
                "message_id": str(message.id)
            }

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        direction: str = "inbound",
        tokens_used: Optional[int] = None,
        latency_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a message to conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (customer, agent, system)
            content: Message content
            direction: Message direction (inbound, outbound)
            tokens_used: Optional tokens used
            latency_ms: Optional processing latency

        Returns:
            Message data
        """
        async with get_session() as session:
            message = await self.message_repo.create(
                session,
                conversation_id=uuid.UUID(conversation_id),
                channel="agent",  # Assuming agent sends this
                direction=direction,
                role=role,
                content=content,
                tokens_used=tokens_used,
                latency_ms=latency_ms
            )

            return {
                "id": str(message.id),
                "conversation_id": str(message.conversation_id),
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "tokens_used": message.tokens_used,
                "latency_ms": message.latency_ms
            }

    async def get_conversation_with_messages(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get conversation with all messages.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation with messages
        """
        async with get_session() as session:
            conversation = await self.conversation_repo.get_with_messages(session, uuid.UUID(conversation_id))
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            messages = await self.message_repo.get_by_conversation(session, conversation.id)

            return {
                "id": str(conversation.id),
                "customer_id": str(conversation.customer_id),
                "initial_channel": conversation.initial_channel,
                "status": conversation.status,
                "started_at": conversation.started_at.isoformat(),
                "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
                "sentiment_score": conversation.sentiment_score,
                "messages": [
                    {
                        "id": str(msg.id),
                        "role": msg.role,
                        "content": msg.content,
                        "direction": msg.direction,
                        "channel": msg.channel,
                        "created_at": msg.created_at.isoformat(),
                        "tokens_used": msg.tokens_used,
                        "latency_ms": msg.latency_ms
                    }
                    for msg in messages
                ]
            }

    async def update_conversation_status(
        self,
        conversation_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update conversation status.

        Args:
            conversation_id: Conversation ID
            status: New status

        Returns:
            Updated conversation data
        """
        async with get_session() as session:
            updated_conversation = await self.conversation_repo.update_status(
                session,
                uuid.UUID(conversation_id),
                status
            )

            return {
                "id": str(updated_conversation.id),
                "status": updated_conversation.status,
                "ended_at": updated_conversation.ended_at.isoformat() if updated_conversation.ended_at else None
            }

    async def get_active_conversations(
        self,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all active conversations.

        Args:
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of active conversations
        """
        async with get_session() as session:
            conversations = await self.conversation_repo.get_active_conversations(session, skip, limit)

            return [
                {
                    "id": str(conv.id),
                    "customer_id": str(conv.customer_id),
                    "initial_channel": conv.initial_channel,
                    "status": conv.status,
                    "started_at": conv.started_at.isoformat(),
                    "sentiment_score": conv.sentiment_score
                }
                for conv in conversations
            ]
```

### `src/services/metrics_service.py`

```python
"""
Metrics service - Analytics and metrics
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

# Import repositories
from src.database.repositories.ticket_repo import TicketRepository
from src.database.repositories.conversation_repo import ConversationRepository
from src.database.repositories.message_repo import MessageRepository
from src.core.database import get_session


class MetricsService:
    """Service for analytics and metrics."""

    def __init__(self):
        """Initialize metrics service."""
        self.ticket_repo = TicketRepository()
        self.conversation_repo = ConversationRepository()
        self.message_repo = MessageRepository()

    async def get_dashboard_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard metrics.

        Args:
            start_date: Start date for metrics (default: 7 days ago)
            end_date: End date for metrics (default: now)

        Returns:
            Dashboard metrics dictionary
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        async with get_session() as session:
            # Get ticket metrics
            total_tickets = await self.ticket_repo.count(session)
            open_tickets = await self.ticket_repo.count(session, status="open")
            resolved_tickets = await self.ticket_repo.count(session, status="resolved")
            escalated_tickets = await self.ticket_repo.count(session, status="escalated")

            # Get conversation metrics
            active_conversations = await self.conversation_repo.count_active(session)

            # Calculate resolution rate
            resolution_rate = (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0

            # Get overdue tickets
            overdue_tickets = await self.ticket_repo.get_overdue_tickets(session, 0, 10)

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": (end_date - start_date).days
                },
                "tickets": {
                    "total": total_tickets,
                    "open": open_tickets,
                    "resolved": resolved_tickets,
                    "escalated": escalated_tickets,
                    "resolution_rate": round(resolution_rate, 2),
                    "overdue": len(overdue_tickets)
                },
                "conversations": {
                    "active": active_conversations
                },
                "overdue_tickets": [
                    {
                        "ticket_number": ticket.ticket_number,
                        "priority": ticket.priority,
                        "hours_overdue": round((datetime.now() - ticket.sla_target).total_seconds() / 3600, 1) if ticket.sla_target else 0
                    }
                    for ticket in overdue_tickets
                ]
            }

    async def get_channel_metrics(
        self,
        channel: str
    ) -> Dict[str, Any]:
        """
        Get metrics for a specific channel.

        Args:
            channel: Channel name (email, whatsapp, web_form)

        Returns:
            Channel-specific metrics
        """
        async with get_session() as session:
            tickets = await self.ticket_repo.get_by_channel(session, channel, 0, 100)

            # Calculate metrics
            total = len(tickets)
            open_count = sum(1 for t in tickets if t.status == "open")
            resolved_count = sum(1 for t in tickets if t.status == "resolved")
            escalated_count = sum(1 for t in tickets if t.status == "escalated")

            return {
                "channel": channel,
                "total_tickets": total,
                "open_tickets": open_count,
                "resolved_tickets": resolved_count,
                "escalated_tickets": escalated_count,
                "resolution_rate": round(resolved_count / total * 100, 2) if total > 0 else 0
            }

    async def get_ticket_trends(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get ticket creation trends.

        Args:
            days: Number of days to analyze

        Returns:
            Ticket trend data
        """
        async with get_session() as session:
            start_date = datetime.now() - timedelta(days=days)

            # Get tickets created in period
            all_tickets = await self.ticket_repo.get_by_status(session, "open", 0, 1000)
            recent_tickets = [t for t in all_tickets if t.created_at >= start_date]

            # Group by date
            daily_counts = {}
            for ticket in recent_tickets:
                date_str = ticket.created_at.strftime("%Y-%m-%d")
                daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

            return {
                "period_days": days,
                "total_tickets": len(recent_tickets),
                "average_per_day": round(len(recent_tickets) / days, 2),
                "daily_breakdown": daily_counts
            }
```

### `src/services/__init__.py`

```python
"""
Services package initialization
"""

from src.services.customer_service import CustomerService
from src.services.ticket_service import TicketService
from src.services.conversation_service import ConversationService
from src.services.metrics_service import MetricsService

__all__ = [
    "CustomerService",
    "TicketService",
    "ConversationService",
    "MetricsService"
]
```

---

## Exercise 2.5: Kafka Event Streaming (2-3 hours)

### Task: Set Up Kafka Topics for Multi-Channel Processing

Create Kafka topics for unified event streaming across all channels.

### Install Dependencies

```bash
uv add aiokafka
```

### Create Kafka Client

#### `src/kafka/client.py`

```python
"""
Kafka client for multi-channel event streaming
"""

import json
from datetime import datetime
from typing import Dict, Any, Callable
import os

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)

# Topic definitions for multi-channel FTE
TOPICS = {
    # Incoming tickets from all channels
    'tickets_incoming': 'fte.tickets.incoming',

    # Channel-specific inbound
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',

    # Channel-specific outbound
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',

    # Escalations
    'escalations': 'fte.escalations',

    # Metrics and monitoring
    'metrics': 'fte.metrics',

    # Dead letter queue for failed processing
    'dlq': 'fte.dlq'
}

class FTEKafkaProducer:
    """Kafka producer for FTE event publishing."""

    def __init__(self):
        self.producer = None

    async def start(self):
        """Initialize and start the producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        """Stop the producer."""
        await self.producer.stop()

    async def publish(self, topic: str, event: Dict[str, Any]):
        """
        Publish an event to a Kafka topic.

        Args:
            topic: Kafka topic name
            event: Event data to publish
        """
        if not self.producer:
            await self.start()

        event["timestamp"] = datetime.utcnow().isoformat()
        await self.producer.send_and_wait(topic, event)

class FTEKafkaConsumer:
    """Kafka consumer for FTE event processing."""

    def __init__(self, topics: list, group_id: str):
        """
        Initialize consumer with topics and group ID.

        Args:
            topics: List of topics to consume
            group_id: Consumer group ID
        """
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

    async def start(self):
        """Start the consumer."""
        await self.consumer.start()

    async def stop(self):
        """Stop the consumer."""
        await self.consumer.stop()

    async def consume(self, handler: Callable[[str, Dict[str, Any]], None]):
        """
        Consume messages from subscribed topics.

        Args:
            handler: Async function to handle each message
        """
        async for msg in self.consumer:
            await handler(msg.topic, msg.value)
```

---

## Worker Layer & Split Kafka Implementation

### Worker Layer Structure:
```
src/worker/
├── __init__.py               # Package initialization
├── ticket_processor.py       # Process incoming tickets
├── response_dispatcher.py    # Dispatch responses to channels
└── metrics_collector.py     # Collect and publish metrics
```

### Split Kafka Structure:
```
src/kafka/
├── __init__.py           # Package initialization
├── topics.py             # Topic definitions and configuration
├── producer.py           # Kafka producer implementation
└── consumer.py           # Kafka consumer implementation
```

### `src/kafka/topics.py`

```python
"""
Kafka topics configuration and definitions
Multi-channel topic management
"""

from typing import Dict, Any
import os

class KafkaTopics:
    """Kafka topic definitions for multi-channel FTE."""

    # Incoming tickets from all channels
    TICKETS_INCOMING = "fte.tickets.incoming"

    # Channel-specific inbound topics
    EMAIL_INBOUND = "fte.channels.email.inbound"
    WHATSAPP_INBOUND = "fte.channels.whatsapp.inbound"
    WEBFORM_INBOUND = "fte.channels.webform.inbound"

    # Channel-specific outbound topics
    EMAIL_OUTBOUND = "fte.channels.email.outbound"
    WHATSAPP_OUTBOUND = "fte.channels.whatsapp.outbound"

    # Escalations
    ESCALATIONS = "fte.escalations"

    # Metrics and monitoring
    METRICS = "fte.metrics"
    PERFORMANCE_METRICS = "fte.metrics.performance"

    # Dead letter queue for failed processing
    DLQ = "fte.dlq"

    # Agent events
    AGENT_EVENTS = "fte.agent.events"

    # Topic configuration
    TOPIC_CONFIG: Dict[str, Dict[str, Any]] = {
        TICKETS_INCOMING: {
            "partitions": 3,
            "replication_factor": 2,
            "retention_ms": 604800000  # 7 days
        },
        EMAIL_INBOUND: {
            "partitions": 2,
            "replication_factor": 2,
            "retention_ms": 604800000
        },
        WHATSAPP_INBOUND: {
            "partitions": 2,
            "replication_factor": 2,
            "retention_ms": 604800000
        },
        WEBFORM_INBOUND: {
            "partitions": 2,
            "replication_factor": 2,
            "retention_ms": 604800000
        },
        ESCALATIONS: {
            "partitions": 1,
            "replication_factor": 2,
            "retention_ms": 2592000000  # 30 days
        }
    }

    @classmethod
    def get_all_topics(cls) -> Dict[str, str]:
        """Get all topic mappings."""
        return {
            "tickets_incoming": cls.TICKETS_INCOMING,
            "email_inbound": cls.EMAIL_INBOUND,
            "whatsapp_inbound": cls.WHATSAPP_INBOUND,
            "webform_inbound": cls.WEBFORM_INBOUND,
            "email_outbound": cls.EMAIL_OUTBOUND,
            "whatsapp_outbound": cls.WHATSAPP_OUTBOUND,
            "escalations": cls.ESCALATIONS,
            "metrics": cls.METRICS,
            "performance_metrics": cls.PERFORMANCE_METRICS,
            "dlq": cls.DLQ,
            "agent_events": cls.AGENT_EVENTS
        }

    @classmethod
    def get_topic_by_channel(cls, channel: str, direction: str = "inbound") -> str:
        """
        Get topic name for channel and direction.

        Args:
            channel: Channel name (email, whatsapp, webform)
            direction: Direction (inbound, outbound)

        Returns:
            Topic name
        """
        if direction == "outbound":
            return {
                "email": cls.EMAIL_OUTBOUND,
                "whatsapp": cls.WHATSAPP_OUTBOUND
            }.get(channel, cls.EMAIL_OUTBOUND)
        else:
            return {
                "email": cls.EMAIL_INBOUND,
                "whatsapp": cls.WHATSAPP_INBOUND,
                "webform": cls.WEBFORM_INBOUND
            }.get(channel, cls.EMAIL_INBOUND)


# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092"
)
KAFKA_CONSUMER_GROUP = os.getenv(
    "KAFKA_CONSUMER_GROUP",
    "fte-worker-group"
)
KAFKA_AUTO_OFFSET_RESET = os.getenv(
    "KAFKA_AUTO_OFFSET_RESET",
    "earliest"
)
```

### `src/kafka/producer.py`

```python
"""
Kafka producer implementation
Event publishing for multi-channel FTE
"""

import json
from datetime import datetime
from typing import Dict, Any
import logging

from aiokafka import AIOKafkaProducer
from src.kafka.topics import (
    KAFKA_BOOTSTRAP_SERVERS,
    KafkaTopics
)

logger = logging.getLogger(__name__)


class FTEKafkaProducer:
    """Kafka producer for FTE event publishing."""

    def __init__(self):
        """Initialize Kafka producer."""
        self.producer = None
        self.is_started = False

    async def start(self):
        """Initialize and start the producer."""
        if self.is_started:
            return

        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            await self.producer.start()
            self.is_started = True
            logger.info("Kafka producer started successfully")
        except Exception as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise

    async def stop(self):
        """Stop the producer."""
        if not self.is_started or not self.producer:
            return

        try:
            await self.producer.stop()
            self.is_started = False
            logger.info("Kafka producer stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Kafka producer: {e}")

    async def publish_ticket_event(
        self,
        event_type: str,
        ticket_data: Dict[str, Any]
    ):
        """
        Publish ticket event to tickets_incoming topic.

        Args:
            event_type: Event type (created, updated, resolved, escalated)
            ticket_data: Ticket data
        """
        event = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": ticket_data
        }

        await self.publish(KafkaTopics.TICKETS_INCOMING, event)

    async def publish_channel_event(
        self,
        channel: str,
        direction: str,
        message_data: Dict[str, Any]
    ):
        """
        Publish channel event to appropriate topic.

        Args:
            channel: Channel name (email, whatsapp, webform)
            direction: Direction (inbound, outbound)
            message_data: Message data
        """
        topic = KafkaTopics.get_topic_by_channel(channel, direction)
        event = {
            "channel": channel,
            "direction": direction,
            "timestamp": datetime.utcnow().isoformat(),
            "data": message_data
        }

        await self.publish(topic, event)

    async def publish_escalation_event(
        self,
        escalation_data: Dict[str, Any]
    ):
        """
        Publish escalation event.

        Args:
            escalation_data: Escalation information
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": escalation_data
        }

        await self.publish(KafkaTopics.ESCALATIONS, event)

    async def publish_metric_event(
        self,
        metric_type: str,
        metric_data: Dict[str, Any]
    ):
        """
        Publish metric event.

        Args:
            metric_type: Type of metric
            metric_data: Metric data
        """
        event = {
            "metric_type": metric_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": metric_data
        }

        await self.publish(KafkaTopics.METRICS, event)

    async def publish_performance_metric(
        self,
        performance_data: Dict[str, Any]
    ):
        """
        Publish performance metric.

        Args:
            performance_data: Performance data
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": performance_data
        }

        await self.publish(KafkaTopics.PERFORMANCE_METRICS, event)

    async def publish_agent_event(
        self,
        agent_data: Dict[str, Any]
    ):
        """
        Publish agent processing event.

        Args:
            agent_data: Agent processing data
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": agent_data
        }

        await self.publish(KafkaTopics.AGENT_EVENTS, event)

    async def publish_to_dlq(
        self,
        error_data: Dict[str, Any]
    ):
        """
        Publish failed event to dead letter queue.

        Args:
            error_data: Error information
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_data
        }

        await self.publish(KafkaTopics.DLQ, event)

    async def publish(self, topic: str, event: Dict[str, Any]):
        """
        Generic publish method.

        Args:
            topic: Kafka topic name
            event: Event data to publish
        """
        if not self.is_started:
            await self.start()

        try:
            # Add metadata
            event["published_at"] = datetime.utcnow().isoformat()
            event["producer_id"] = "fte-producer"

            await self.producer.send_and_wait(topic, event)
            logger.debug(f"Published event to {topic}: {event.get('event_type', 'generic')}")
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            # Publish to DLQ on failure
            await self.publish_to_dlq({
                "topic": topic,
                "event": event,
                "error": str(e)
            })
```

### `src/kafka/consumer.py`

```python
"""
Kafka consumer implementation
Event consumption for multi-channel FTE
"""

import json
import logging
from typing import Dict, Any, Callable, Optional
from aiokafka import AIOKafkaConsumer

from src.kafka.topics import (
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_CONSUMER_GROUP,
    KAFKA_AUTO_OFFSET_RESET,
    KafkaTopics
)

logger = logging.getLogger(__name__)


class FTEKafkaConsumer:
    """Kafka consumer for FTE event processing."""

    def __init__(
        self,
        topics: list[str],
        group_id: Optional[str] = None
    ):
        """
        Initialize consumer with topics.

        Args:
            topics: List of topics to consume
            group_id: Consumer group ID
        """
        self.topics = topics
        self.group_id = group_id or KAFKA_CONSUMER_GROUP
        self.consumer = None
        self.is_started = False

    async def start(self):
        """Initialize and start the consumer."""
        if self.is_started:
            return

        try:
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                auto_offset_reset=KAFKA_AUTO_OFFSET_RESET,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            self.consumer.subscribe(self.topics)
            self.is_started = True
            logger.info(f"Kafka consumer started for topics: {self.topics}")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise

    async def stop(self):
        """Stop the consumer."""
        if not self.is_started or not self.consumer:
            return

        try:
            await self.consumer.stop()
            self.is_started = False
            logger.info("Kafka consumer stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Kafka consumer: {e}")

    async def consume(self, handler: Callable):
        """
        Consume messages from subscribed topics.

        Args:
            handler: Async function to handle each message
        """
        if not self.is_started:
            await self.start()

        try:
            async for msg in self.consumer:
                try:
                    await handler(msg.topic, msg.value, msg.key)
                except Exception as e:
                    logger.error(f"Error processing message from {msg.topic}: {e}")
                    # Continue processing other messages
                    continue
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            raise

    async def get_consumer(self) -> AIOKafkaConsumer:
        """Get the underlying consumer instance."""
        return self.consumer
```

### `src/worker/ticket_processor.py`

```python
"""
Ticket processor worker
Process incoming tickets from Kafka
"""

import asyncio
import logging
from typing import Dict, Any

from src.kafka.consumer import FTEKafkaConsumer
from src.kafka.producer import FTEKafkaProducer
from src.kafka.topics import KafkaTopics
from src.services.ticket_service import TicketService
from src.services.customer_service import CustomerService

logger = logging.getLogger(__name__)


class TicketProcessorWorker:
    """Worker that processes incoming tickets."""

    def __init__(self):
        """Initialize ticket processor worker."""
        self.consumer = FTEKafkaConsumer([KafkaTopics.TICKETS_INCOMING], "ticket-processor")
        self.producer = FTEKafkaProducer()
        self.ticket_service = TicketService()
        self.customer_service = CustomerService()
        self.is_running = False

    async def start(self):
        """Start the ticket processor worker."""
        if self.is_running:
            return

        logger.info("Starting ticket processor worker...")

        # Start producer
        await self.producer.start()

        # Start consumer
        await self.consumer.start()
        self.is_running = True

        # Start consuming
        await self.consumer.consume(self._handle_ticket_event)

    async def stop(self):
        """Stop the ticket processor worker."""
        if not self.is_running:
            return

        logger.info("Stopping ticket processor worker...")
        self.is_running = False

        # Stop consumer and producer
        await self.consumer.stop()
        await self.producer.stop()

        logger.info("Ticket processor worker stopped")

    async def _handle_ticket_event(self, topic: str, event: Dict[str, Any], key: bytes):
        """
        Handle ticket events from Kafka.

        Args:
            topic: Topic name
            event: Event data
            key: Message key
        """
        try:
            event_type = event.get("event_type", "unknown")
            ticket_data = event.get("data", {})

            logger.info(f"Processing ticket event: {event_type}")

            # Handle different event types
            if event_type == "created":
                await self._handle_ticket_created(ticket_data)
            elif event_type == "updated":
                await self._handle_ticket_updated(ticket_data)
            elif event_type == "resolved":
                await self._handle_ticket_resolved(ticket_data)
            elif event_type == "escalated":
                await self._handle_ticket_escalated(ticket_data)
            else:
                logger.warning(f"Unknown ticket event type: {event_type}")

        except Exception as e:
            logger.error(f"Error handling ticket event: {e}")
            # Publish to DLQ on error
            await self.producer.publish_to_dlq({
                "topic": topic,
                "event": event,
                "error": str(e)
            })

    async def _handle_ticket_created(self, ticket_data: Dict[str, Any]):
        """
        Handle ticket creation event.

        Args:
            ticket_data: Ticket data from event
        """
        try:
            # Create ticket using service
            customer_email = ticket_data.get("customer_email")
            issue = ticket_data.get("issue")
            category = ticket_data.get("category", "general")
            priority = ticket_data.get("priority", "medium")
            channel = ticket_data.get("channel", "web_form")

            created_ticket = await self.ticket_service.create_ticket(
                customer_email=customer_email,
                issue=issue,
                category=category,
                priority=priority,
                channel=channel
            )

            logger.info(f"Created ticket: {created_ticket['ticket_number']}")

            # Publish ticket created event
            await self.producer.publish_ticket_event("created", created_ticket)

            # Publish metric
            await self.producer.publish_metric_event("ticket_created", {
                "ticket_number": created_ticket["ticket_number"],
                "channel": channel,
                "priority": priority
            })

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            raise

    async def _handle_ticket_updated(self, ticket_data: Dict[str, Any]):
        """
        Handle ticket update event.

        Args:
            ticket_data: Ticket data from event
        """
        try:
            ticket_number = ticket_data.get("ticket_number")
            status = ticket_data.get("status")
            resolution_notes = ticket_data.get("resolution_notes")

            # Update ticket status
            updated_ticket = await self.ticket_service.update_ticket_status(
                ticket_number=ticket_number,
                status=status,
                resolution_notes=resolution_notes
            )

            logger.info(f"Updated ticket {ticket_number} to status: {status}")

            # Publish metric
            await self.producer.publish_metric_event("ticket_updated", {
                "ticket_number": ticket_number,
                "new_status": status
            })

        except Exception as e:
            logger.error(f"Error updating ticket: {e}")
            raise

    async def _handle_ticket_resolved(self, ticket_data: Dict[str, Any]):
        """
        Handle ticket resolution event.

        Args:
            ticket_data: Ticket data from event
        """
        try:
            ticket_number = ticket_data.get("ticket_number")
            resolution_notes = ticket_data.get("resolution_notes", "")

            # Update ticket to resolved
            await self.ticket_service.update_ticket_status(
                ticket_number=ticket_number,
                status="resolved",
                resolution_notes=resolution_notes
            )

            logger.info(f"Resolved ticket: {ticket_number}")

            # Publish metric
            await self.producer.publish_metric_event("ticket_resolved", {
                "ticket_number": ticket_number
            })

        except Exception as e:
            logger.error(f"Error resolving ticket: {e}")
            raise

    async def _handle_ticket_escalated(self, ticket_data: Dict[str, Any]):
        """
        Handle ticket escalation event.

        Args:
            ticket_data: Ticket data from event
        """
        try:
            ticket_number = ticket_data.get("ticket_number")
            reason = ticket_data.get("reason", "")
            priority = ticket_data.get("priority", "high")

            # Escalate ticket
            await self.ticket_service.escalate_ticket(
                ticket_number=ticket_number,
                reason=reason,
                priority=priority
            )

            logger.info(f"Escalated ticket: {ticket_number}, reason: {reason}")

            # Publish escalation event
            await self.producer.publish_escalation_event({
                "ticket_number": ticket_number,
                "reason": reason,
                "escalated_at": ticket_data.get("escalated_at")
            })

            # Publish metric
            await self.producer.publish_metric_event("ticket_escalated", {
                "ticket_number": ticket_number,
                "priority": priority
            })

        except Exception as e:
            logger.error(f"Error escalating ticket: {e}")
            raise
```

### `src/worker/response_dispatcher.py`

```python
"""
Response dispatcher worker
Dispatch agent responses to appropriate channels
"""

import asyncio
import logging
from typing import Dict, Any

from src.kafka.consumer import FTEKafkaConsumer
from src.kafka.producer import FTEKafkaProducer
from src.kafka.topics import KafkaTopics
from src.agent.agent import CustomerSuccessAgent

logger = logging.getLogger(__name__)


class ResponseDispatcherWorker:
    """Worker that dispatches agent responses to channels."""

    def __init__(self):
        """Initialize response dispatcher worker."""
        self.consumer = FTEKafkaConsumer([KafkaTopics.AGENT_EVENTS], "response-dispatcher")
        self.producer = FTEKafkaProducer()
        self.agent = CustomerSuccessAgent()
        self.is_running = False

        # Channel handlers (would be implemented)
        self.channel_handlers = {
            "email": self._send_email_response,
            "whatsapp": self._send_whatsapp_response,
            "web_form": self._send_webform_response
        }

    async def start(self):
        """Start the response dispatcher worker."""
        if self.is_running:
            return

        logger.info("Starting response dispatcher worker...")

        # Start producer
        await self.producer.start()

        # Start consumer
        await self.consumer.start()
        self.is_running = True

        # Start consuming
        await self.consumer.consume(self._handle_agent_event)

    async def stop(self):
        """Stop the response dispatcher worker."""
        if not self.is_running:
            return

        logger.info("Stopping response dispatcher worker...")
        self.is_running = False

        # Stop consumer and producer
        await self.consumer.stop()
        await self.producer.stop()

        logger.info("Response dispatcher worker stopped")

    async def _handle_agent_event(self, topic: str, event: Dict[str, Any], key: bytes):
        """
        Handle agent processing events.

        Args:
            topic: Topic name
            event: Event data
            key: Message key
        """
        try:
            agent_data = event.get("data", {})
            response = agent_data.get("response")
            channel = agent_data.get("channel")
            conversation_id = agent_data.get("conversation_id")
            ticket_id = agent_data.get("ticket_id")

            if not response or not channel:
                logger.warning(f"Invalid agent event: missing response or channel")
                return

            logger.info(f"Dispatching response for channel: {channel}")

            # Dispatch to appropriate channel
            handler = self.channel_handlers.get(channel)
            if handler:
                await handler(response, conversation_id, ticket_id)
            else:
                logger.warning(f"No handler for channel: {channel}")

            # Publish performance metric
            await self.producer.publish_performance_metric({
                "channel": channel,
                "latency_ms": agent_data.get("latency_ms", 0),
                "tokens_used": agent_data.get("tokens_used", 0),
                "model": agent_data.get("model", "")
            })

        except Exception as e:
            logger.error(f"Error handling agent event: {e}")
            # Publish to DLQ on error
            await self.producer.publish_to_dlq({
                "topic": topic,
                "event": event,
                "error": str(e)
            })

    async def _send_email_response(self, response: str, conversation_id: str, ticket_id: str):
        """
        Send response via email.

        Args:
            response: Agent response text
            conversation_id: Conversation ID
            ticket_id: Ticket ID
        """
        logger.info(f"Sending email response for ticket: {ticket_id}")
        # TODO: Implement email sending via Gmail API
        await self.producer.publish_channel_event(
            "email",
            "outbound",
            {
                "response": response,
                "conversation_id": conversation_id,
                "ticket_id": ticket_id,
                "status": "sent"
            }
        )

    async def _send_whatsapp_response(self, response: str, conversation_id: str, ticket_id: str):
        """
        Send response via WhatsApp.

        Args:
            response: Agent response text
            conversation_id: Conversation ID
            ticket_id: Ticket ID
        """
        logger.info(f"Sending WhatsApp response for ticket: {ticket_id}")
        # TODO: Implement WhatsApp sending via Twilio API
        await self.producer.publish_channel_event(
            "whatsapp",
            "outbound",
            {
                "response": response,
                "conversation_id": conversation_id,
                "ticket_id": ticket_id,
                "status": "sent"
            }
        )

    async def _send_webform_response(self, response: str, conversation_id: str, ticket_id: str):
        """
        Send response for web form (typically for admin dashboard).

        Args:
            response: Agent response text
            conversation_id: Conversation ID
            ticket_id: Ticket ID
        """
        logger.info(f"Processing web form response for ticket: {ticket_id}")
        # For web forms, we might store the response or send notification
        await self.producer.publish_channel_event(
            "web_form",
            "outbound",
            {
                "response": response,
                "conversation_id": conversation_id,
                "ticket_id": ticket_id,
                "status": "processed"
            }
        )
```

### `src/worker/metrics_collector.py`

```python
"""
Metrics collector worker
Collect and aggregate system metrics
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from src.kafka.consumer import FTEKafkaConsumer
from src.kafka.producer import FTEKafkaProducer
from src.kafka.topics import KafkaTopics
from src.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


class MetricsCollectorWorker:
    """Worker that collects and aggregates metrics."""

    def __init__(self):
        """Initialize metrics collector worker."""
        self.consumer = FTEKafkaConsumer([KafkaTopics.METRICS, KafkaTopics.PERFORMANCE_METRICS], "metrics-collector")
        self.producer = FTEKafkaProducer()
        self.metrics_service = MetricsService()
        self.is_running = False

        # Metrics buffer
        self.metrics_buffer = {
            "performance": [],
            "tickets": [],
            "channels": {}
        }

    async def start(self):
        """Start the metrics collector worker."""
        if self.is_running:
            return

        logger.info("Starting metrics collector worker...")

        # Start producer
        await self.producer.start()

        # Start consumer
        await self.consumer.start()
        self.is_running = True

        # Start consuming and periodic aggregation
        consume_task = asyncio.create_task(self.consumer.consume(self._handle_metric_event))
        aggregate_task = asyncio.create_task(self._aggregate_metrics())

        await asyncio.gather([consume_task, aggregate_task])

    async def stop(self):
        """Stop the metrics collector worker."""
        if not self.is_running:
            return

        logger.info("Stopping metrics collector worker...")
        self.is_running = False

        # Stop consumer and producer
        await self.consumer.stop()
        await self.producer.stop()

        logger.info("Metrics collector worker stopped")

    async def _handle_metric_event(self, topic: str, event: Dict[str, Any], key: bytes):
        """
        Handle metric events.

        Args:
            topic: Topic name
            event: Event data
            key: Message key
        """
        try:
            metric_type = event.get("metric_type", "unknown")
            metric_data = event.get("data", {})

            # Buffer metrics for aggregation
            if topic == KafkaTopics.PERFORMANCE_METRICS:
                self.metrics_buffer["performance"].append(metric_data)
            elif metric_type == "ticket_created":
                self.metrics_buffer["tickets"].append(metric_data)
            elif metric_type == "channel_metric":
                channel = metric_data.get("channel", "unknown")
                if channel not in self.metrics_buffer["channels"]:
                    self.metrics_buffer["channels"][channel] = []
                self.metrics_buffer["channels"][channel].append(metric_data)

            logger.debug(f"Buffered metric: {metric_type}")

        except Exception as e:
            logger.error(f"Error handling metric event: {e}")
            # Publish to DLQ on error
            await self.producer.publish_to_dlq({
                "topic": topic,
                "event": event,
                "error": str(e)
            })

    async def _aggregate_metrics(self):
        """
        Periodically aggregate and publish metrics.
        """
        while self.is_running:
            try:
                # Wait for aggregation interval (e.g., 5 minutes)
                await asyncio.sleep(300)

                if not self.metrics_service.is_running:
                    continue

                # Get dashboard metrics
                dashboard_metrics = await self.metrics_service.get_dashboard_metrics()

                # Clear buffer after aggregation
                aggregated = {
                    "aggregated_at": datetime.utcnow().isoformat(),
                    "dashboard_metrics": dashboard_metrics,
                    "performance_samples": len(self.metrics_buffer["performance"]),
                    "ticket_samples": len(self.metrics_buffer["tickets"])
                }

                # Publish aggregated metrics
                await self.producer.publish_metric_event("dashboard", dashboard_metrics)

                # Clear buffer
                self.metrics_buffer["performance"] = []
                self.metrics_buffer["tickets"] = []
                self.metrics_buffer["channels"] = {}

                logger.info("Metrics aggregated and published")

            except Exception as e:
                logger.error(f"Error aggregating metrics: {e}")
```

### `src/worker/__init__.py`

```python
"""
Worker package initialization
"""

from src.worker.ticket_processor import TicketProcessorWorker
from src.worker.response_dispatcher import ResponseDispatcherWorker
from src.worker.metrics_collector import MetricsCollectorWorker

__all__ = [
    "TicketProcessorWorker",
    "ResponseDispatcherWorker",
    "MetricsCollectorWorker"
]
```

### `src/kafka/__init__.py`

```python
"""
Kafka package initialization
"""

from src.kafka.topics import KafkaTopics
from src.kafka.producer import FTEKafkaProducer
from src.kafka.consumer import FTEKafkaConsumer

__all__ = [
    "KafkaTopics",
    "FTEKafkaProducer",
    "FTEKafkaConsumer"
]
```

---

## Exercise 2.6: FastAPI Service with Channel Endpoints (3-4 hours)

### Task: Build API Layer

Create a FastAPI application that exposes endpoints for all channels and webhook handlers.

### Install Dependencies

```bash
uv add fastapi uvicorn
```

### Create FastAPI Application

#### `src/api/main.py`

```python
"""
FastAPI service for Customer Success FTE
Exposes endpoints for all channels and webhooks
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uuid

from channels.gmail_handler import GmailHandler
from channels.whatsapp_handler import WhatsAppHandler
from channels.web_form_handler import router as web_form_router
from kafka.client import FTEKafkaProducer, TOPICS

app = FastAPI(
    title="Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web",
    version="2.0.0"
)

# CORS for web form
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include web form router
app.include_router(web_form_router)

# Initialize handlers
gmail_handler = GmailHandler()
whatsapp_handler = WhatsAppHandler()
kafka_producer = FTEKafkaProducer()

@app.on_event("startup")
async def startup():
    """Initialize Kafka producer on startup."""
    await kafka_producer.start()

@app.on_event("shutdown")
async def shutdown():
    """Clean up resources on shutdown."""
    await kafka_producer.stop()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active"
        }
    }

@app.get("/metrics/channels")
async def get_channel_metrics():
    """Get performance metrics by channel."""
    # TODO: Implement with database queries
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "channels": {
            "email": {
                "total_conversations": 0,
                "avg_sentiment": 0.75,
                "escalations": 0
            },
            "whatsapp": {
                "total_conversations": 0,
                "avg_sentiment": 0.82,
                "escalations": 0
            },
            "web_form": {
                "total_conversations": 0,
                "avg_sentiment": 0.70,
                "escalations": 0
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Core Utilities Folder

The core utilities folder contains shared functionality used across the application.

### File Structure:
```
src/core/
├── __init__.py           # Package initialization
├── database.py           # Database connection management
├── config.py            # Application configuration
├── logging.py           # Logging configuration
├── exceptions.py        # Custom exceptions
└── utils.py            # Utility functions
```

### `src/core/database.py`

```python
"""
Database connection management
Provides async database sessions and connection pooling
"""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from src.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=NullPool
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_database():
    """Initialize database connection."""
    try:
        # Test connection
        async with get_session() as session:
            await session.execute("SELECT 1")
        logger.info("Database connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connections."""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
```

### `src/core/logging.py`

```python
"""
Logging configuration
Structured JSON logging for production
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any

from src.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def setup_logging():
    """Setup application logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    # Create application logger
    app_logger = logging.getLogger("fte")
    app_logger.setLevel(log_level)

    # Add JSON formatter for structured logging
    if settings.LOG_LEVEL == "INFO":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        app_logger.addHandler(handler)

    return app_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(f"fte.{name}")
```

### `src/core/exceptions.py`

```python
"""
Custom exceptions for the application
"""


class FTEDomainException(Exception):
    """Base exception for FTE domain errors."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        """
        Initialize domain exception.

        Args:
            message: Error message
            details: Optional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class CustomerNotFoundException(FTEDomainException):
    """Exception when customer is not found."""

    def __init__(self, customer_id: str):
        super().__init__(
            message=f"Customer not found: {customer_id}",
            details={"customer_id": customer_id}
        )


class TicketNotFoundException(FTEDomainException):
    """Exception when ticket is not found."""

    def __init__(self, ticket_number: str):
        super().__init__(
            message=f"Ticket not found: {ticket_number}",
            details={"ticket_number": ticket_number}
        )


class ConversationNotFoundException(FTEDomainException):
    """Exception when conversation is not found."""

    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation not found: {conversation_id}",
            details={"conversation_id": conversation_id}
        )


class AgentProcessingException(FTEDomainException):
    """Exception during agent processing."""

    def __init__(self, message: str, error_details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            details=error_details or {}
        )


class ChannelIntegrationException(FTEDomainException):
    """Exception during channel integration."""

    def __init__(self, channel: str, error: str):
        super().__init__(
            message=f"Channel integration error: {channel}",
            details={"channel": channel, "error": error}
        )


class DatabaseException(FTEDomainException):
    """Exception during database operations."""

    def __init__(self, operation: str, error: str):
        super().__init__(
            message=f"Database operation failed: {operation}",
            details={"operation": operation, "error": error}
        )
```

### `src/core/utils.py`

```python
"""
Utility functions for the application
"""

import re
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime


def generate_ticket_number() -> str:
    """Generate a unique ticket number."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"TKT-{timestamp}-{unique_id}"


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise
    """
    # Remove common formatting
    cleaned = re.sub(r'[\s\-\(\)]+', '', phone)

    # Check if it's all digits and reasonable length
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        input_string: Input to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not input_string:
        return ""

    # Remove potential SQL injection patterns
    sanitized = re.sub(r"(''|--|;|\/\*|\*\/)", "", input_string)

    # Remove HTML tags
    sanitized = re.sub(r"<[^>]*>", "", sanitized)

    # Limit length
    return sanitized[:max_length]


def format_timestamp(timestamp: datetime) -> str:
    """
    Format timestamp for display.

    Args:
        timestamp: Datetime object

    Returns:
        Formatted timestamp string
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def calculate_duration(start_time: datetime, end_time: datetime) -> str:
    """
    Calculate human-readable duration.

    Args:
        start_time: Start datetime
        end_time: End datetime

    Returns:
        Human-readable duration string
    """
    duration = end_time - start_time
    total_seconds = int(duration.total_seconds())

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


def mask_sensitive_data(data: str, mask_char: str = "*") -> str:
    """
    Mask sensitive data like emails, phone numbers.

    Args:
        data: Data to mask
        mask_char: Character to use for masking

    Returns:
        Masked data
    """
    if not data or len(data) <= 4:
        return data

    # Show first 2 and last 2 characters
    masked = data[:2] + (len(data) - 4) * mask_char + data[-2:]
    return masked


def parse_priority(priority: str) -> int:
    """
    Convert priority string to numeric value.

    Args:
        priority: Priority string (low, medium, high, critical)

    Returns:
        Numeric priority value (1-4)
    """
    priority_map = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    return priority_map.get(priority.lower(), 2)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def safe_json_dumps(data: Any) -> str:
    """
    Safely serialize data to JSON.

    Args:
        data: Data to serialize

    Returns:
        JSON string or empty object on failure
    """
    try:
        import json
        return json.dumps(data, default=str)
    except Exception as e:
        # Log error but don't fail
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"JSON serialization error: {e}")
        return "{}"


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text.

    Args:
        text: Text to extract from

    Returns:
        List of hashtags (without # symbol)
    """
    return re.findall(r'#(\w+)', text)


def extract_mentions(text: str) -> List[str]:
    """
    Extract mentions from text.

    Args:
        text: Text to extract from

    Returns:
        List of mentions (without @ symbol)
    """
    return re.findall(r'@(\w+)', text)
```

### `src/core/__init__.py`

```python
"""
Core package initialization
"""

from src.core.database import get_session, init_database, close_database
from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.core.exceptions import (
    FTEDomainException,
    CustomerNotFoundException,
    TicketNotFoundException,
    ConversationNotFoundException,
    AgentProcessingException,
    ChannelIntegrationException,
    DatabaseException
)
from src.core.utils import (
    generate_ticket_number,
    validate_email,
    validate_phone,
    sanitize_input,
    format_timestamp,
    calculate_duration,
    mask_sensitive_data,
    parse_priority,
    truncate_text,
    safe_json_dumps,
    extract_hashtags,
    extract_mentions
)

__all__ = [
    # Database
    "get_session",
    "init_database",
    "close_database",
    # Config
    "settings",
    # Logging
    "setup_logging",
    "get_logger",
    # Exceptions
    "FTEDomainException",
    "CustomerNotFoundException",
    "TicketNotFoundException",
    "ConversationNotFoundException",
    "AgentProcessingException",
    "ChannelIntegrationException",
    "DatabaseException",
    # Utils
    "generate_ticket_number",
    "validate_email",
    "validate_phone",
    "sanitize_input",
    "format_timestamp",
    "calculate_duration",
    "mask_sensitive_data",
    "parse_priority",
    "truncate_text",
    "safe_json_dumps",
    "extract_hashtags",
    "extract_mentions"
]
```

---

## Exercise 2.7: Docker Configuration (2-3 hours)

### Task: Create Docker Configuration

Create Dockerfile and docker-compose for containerizing the application.

### Create Dockerfile

#### `Dockerfile`

```dockerfile
# Multi-stage Dockerfile for Customer Success FTE
FROM python:3.11-slim as base

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/
COPY database/ ./database/

# Install remaining dependencies
RUN uv add fastapi uvicorn aiokafka

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create docker-compose.yml

#### `docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL (Neon DB - for local development)
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: fte_db
      POSTGRES_USER: fte_user
      POSTGRES_PASSWORD: fte_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fte_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Kafka
  kafka:
    image: bitnami/kafka:3.5
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_CFG_ZOOKEEPER_CONNECT_STRING: zookeeper:2181
      KAFKA_CFG_LISTENERS: PLAINTEXT://:9092
      KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE: true
    depends_on:
      - zookeeper
    healthcheck:
      test: ["CMD", "kafka-topics.sh", "--bootstrap-server", "localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 5

  # Zookeeper (required by Kafka)
  zookeeper:
    image: bitnami/zookeeper:3.7
    environment:
      ALLOW_ANONYMOUS_LOGIN: yes
    healthcheck:
      test: ["CMD", "ncz", "-z", "localhost", "2181"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FTE API Service
  fte-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      NEON_DB_URL: ${NEON_DB_URL}
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GMAIL_CREDENTIALS_JSON: ${GMAIL_CREDENTIALS_JSON}
      TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID}
      TWILIO_AUTH_TOKEN: ${TWILIO_AUTH_TOKEN}
      TWILIO_WHATSAPP_NUMBER: ${TWILIO_WHATSAPP_NUMBER}
    depends_on:
      - kafka
      - zookeeper
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Next.js Web Form (for local development)
  web-form:
    build: ./web-form
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    depends_on:
      - fte-api

volumes:
  postgres_data:
```

---

## Exercise 2.8: Kubernetes Deployment (4-5 hours)

### Task: Deploy to Kubernetes

Create Kubernetes manifests for production deployment with auto-scaling.

### Create Kubernetes Directory

```bash
mkdir -p k8s
```

### Namespace

#### `k8s/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: customer-success-fte
  labels:
    app: customer-success-fte
    environment: production
```

### ConfigMap

#### `k8s/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fte-config
  namespace: customer-success-fte
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  KAFKA_BOOTSTRAP_SERVERS: "kafka.kafka.svc.cluster.local:9092"
  NEON_DB_URL: "${NEON_DB_URL}"
  # Channel configs
  GMAIL_ENABLED: "true"
  WHATSAPP_ENABLED: "true"
  WEBFORM_ENABLED: "true"
  # Response limits
  MAX_EMAIL_LENGTH: "2000"
  MAX_WHATSAPP_LENGTH: "1600"
  MAX_WEBFORM_LENGTH: "1000"
```

### Secret

#### `k8s/secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fte-secrets
  namespace: customer-success-fte
type: Opaque
stringData:
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  GMAIL_CREDENTIALS_JSON: "${GMAIL_CREDENTIALS_JSON}"
  TWILIO_ACCOUNT_SID: "${TWILIO_ACCOUNT_SID}"
  TWILIO_AUTH_TOKEN: "${TWILIO_AUTH_TOKEN}"
  TWILIO_WHATSAPP_NUMBER: "${TWILIO_WHATSAPP_NUMBER}"
```

### API Deployment

#### `k8s/deployment-api.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fte-api
  namespace: customer-success-fte
  labels:
    app: customer-success-fte
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-success-fte
      component: api
  template:
    metadata:
      labels:
        app: customer-success-fte
        component: api
    spec:
      containers:
      - name: fte-api
        image: your-registry/customer-success-fte:latest
        command: ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fte-config
        - secretRef:
            name: fte-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fte-api-hpa
  namespace: customer-success-fte
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fte-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Service

#### `k8s/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: customer-success-fte
  namespace: customer-success-fte
spec:
  selector:
    app: customer-success-fte
    component: api
  ports:
  - port: 80
    targetPort: 8000
    name: http
  type: ClusterIP
```

---

## Part 2 Deliverables Checklist

Before moving to Part 3 (Integration & Testing), ensure you have:

### ☐ Database & Schema
- [ ] PostgreSQL schema in `database/schema.sql`
- [ ] All tables created (customers, conversations, messages, tickets, etc.)
- [ ] Vector search configured (pgvector)
- [ ] Connection pooling configured (asyncpg)
- [ ] Schema deployed to Neon DB

### ☐ Channel Integrations
- [ ] Gmail handler in `src/channels/gmail_handler.py`
- [ ] WhatsApp handler in `src/channels/whatsapp_handler.py`
- [ ] Web form handler in `src/channels/web_form_handler.py`
- [ ] All handlers normalize messages to unified format
- [ ] All handlers support sending responses

### ☐ Web Support Form (REQUIRED)
- [ ] Next.js form component in `web-form/app/components/SupportForm.tsx`
- [ ] Form validation with zod
- [ ] All fields: name, email, subject, category, priority, message
- [ ] Submission handling with loading states
- [ ] Success/error states displayed
- [ ] Ticket ID returned to user
- [ ] Responsive design with Tailwind CSS

### ☐ OpenAI Agents SDK Implementation
- [ ] Production agent in `src/agent/customer_success_agent.py`
- [ ] Channel-aware prompts
- [ ] Tool definitions (search, create ticket, escalate, etc.)
- [ ] Sentiment analysis
- [ ] Escalation logic
- [ ] Response formatting per channel

### ☐ Kafka Event Streaming
- [ ] Kafka client in `src/kafka/client.py`
- [ ] All topics defined
- [ ] Producer and consumer implementations
- [ ] Event schema defined

### ☐ FastAPI Service
- [ ] FastAPI app in `src/api/main.py`
- [ ] All channel endpoints exposed
- [ ] Health check endpoint
- [ ] Metrics endpoint
- [ ] CORS configured for web form
- [ ] Web form router included

### ☐ Docker Configuration
- [ ] Dockerfile created
- [ ] docker-compose.yml created
- [ ] All services configured (API, Kafka, Postgres, Web Form)
- [ ] Environment variables documented

### ☐ Kubernetes Deployment
- [ ] Namespace manifest
- [ ] ConfigMap created
- [ ] Secret manifest
- [ ] API deployment
- [ ] Service definition
- [ ] HPA (Horizontal Pod Autoscaler)
- [ ] Health probes configured
- [ ] Resource limits set

### ☐ Configuration & Documentation
- [ ] Environment variables documented
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Deployment guide
- [ ] Architecture diagram

---

## Part 2 Success Criteria

You're ready to move to Part 3 when:

✅ PostgreSQL schema deployed to Neon DB with all tables
✅ All three channel handlers working (Gmail, WhatsApp, Web Form)
✅ Web Support Form complete and functional in Next.js
✅ OpenAI Agents SDK agent implemented with all tools
✅ Kafka topics created and event streaming working
✅ FastAPI service running with all endpoints
✅ Docker containers build and run successfully
✅ Kubernetes manifests created and deploy to cluster
✅ Health checks passing for all services
✅ HPA configured for auto-scaling

---

## Next Steps: Part 3 - Integration & Testing

Once Part 2 is complete, you'll move to:
- Multi-channel E2E testing
- Load testing for 24/7 readiness
- Monitoring and alerting setup
- Documentation finalization

Good luck with Part 2! 🚀

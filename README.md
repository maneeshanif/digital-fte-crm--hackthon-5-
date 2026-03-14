# Customer Success Digital FTE - Hackathon Project

## 🎯 Project Overview

A production-grade AI-powered Customer Success system that operates 24/7 across three communication channels: **Email**, **WhatsApp**, and **Web Form**. This project transforms the way customer support is delivered by combining cutting-edge AI agents with robust infrastructure.

## 📋 What is This Project?

**The CRM Digital FTE (Full-Time Equivalent)** is an intelligent customer support agent that:

- **Acts as a 24/7 Digital Employee**: Handles customer inquiries around the clock
- **Multi-Channel Support**: Unified experience across Email, WhatsApp, and Web Form
- **AI-Powered**: Uses OpenAI's Agents SDK for intelligent conversations
- **Production-Grade**: Built with proper architecture, migrations, and monitoring
- **Scalable**: Event-driven architecture using Kafka for horizontal scaling

## 🎓�️ Project Phases

This hackathon consists of **four phases**:

### Phase 1: Incubation (Hours 1-16) → [See `part-1.md`](part-1.md)
**Goal**: Build a working prototype to validate the concept

**Key Deliverables**:
- ✅ Customer Agent prototype using FastMCP
- ✅ Web Support Form prototype
- ✅ Basic channel integration concepts
- ✅ Working multi-channel conversation flow

**Tech Stack**:
- **Backend**: Python 3.11+ with `uv` package manager
- **Agent SDK**: FastMCP server with 7 functional tools
- **Frontend**: Next.js 14+ with App Router
- **Database**: Neon DB (PostgreSQL) for prototyping
- **Communication**: FastAPI for API endpoints

**Outcome**: Functional prototype that demonstrates core capabilities and validates the Digital FTE concept.

---

### Phase 2: Specialization (Hours 17-40) → [See `part-2.md`](part-2.md)
**Goal**: Transform prototype into production-grade system with proper architecture

**Key Deliverables**:
- ✅ Multi-layer architecture with clear separation of concerns
- ✅ OpenAI Agents SDK implementation (6 functional tools)
- ✅ Repository Pattern for database access
- ✅ Alembic migrations for database schema management
- ✅ Kafka event streaming with producers, consumers, and topics
- ✅ Worker layer for ticket processing and response dispatching
- ✅ Services layer for business logic orchestration
- ✅ 5-page frontend with admin dashboard
- ✅ Docker and Kubernetes deployment manifests
- ✅ Monitoring and observability setup

**Tech Stack**:
- **Backend**: Python 3.11+ with `uv` package manager
- **Agent SDK**: OpenAI Agents SDK (`gpt-4o` model)
- **API Framework**: FastAPI with async support
- **Event Streaming**: Kafka (aiokafka) for scalable event processing
- **Database ORM**: SQLAlchemy + Alembic for migrations
- **Database**: Neon DB (PostgreSQL) with pgvector extension
- **Frontend**: Next.js 14+ with App Router and Tailwind CSS
- **Infrastructure**: Docker + Kubernetes with HPA
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs

**Architecture**: Production-grade layered architecture:
```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION ARCHITECTURE             │
│                                                             │
│  CHANNEL INTAKE LAYER                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │Gmail Webhook│  │Twilio Webook│  │ Web Form    │      │
│  │  Handler    │  │  Handler    │  │  Handler    │      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘      │
│         │                    │                │                  │
│         └────────────────────┼────────────────┘                  │
│                              ▼                                   │
│  EVENT STREAMING    ┌──────────┐                          │
│                     │  Kafka   │                          │
│                     │ (Events) │                          │
│                     └────┬─────┘                          │
│                          │                                    │
│  PROCESSING LAYER        ▼                                  │
│                    ┌───────────┐     ┌──────────┐         │
│                    │  Agent    │────▶│ Postgres │         │
│                    │  Worker   │     │  (State) │         │
│                    └─────┬─────┘     └──────────┘         │
│                          │                                       │
│  RESPONSE LAYER          ▼                                       │
│         ┌────────────────┼────────────────┐                     │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Gmail API   │  │ Twilio API  │  │  API/Email  │        │
│  │  (Reply)    │  │  (Reply)    │  │  (Reply)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  INFRASTRUCTURE                                             │
│  ┌──────────────────────────────────────────────────────┐       │
│  │                    Kubernetes Cluster         │       │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ │       │
│  │  │API Pod │ │Worker 1│ │Worker 2│ │       │
│  │  └────────┘ └────────┘ └────────┘ │       │
│  └──────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Overview

### Layered Architecture (Phase 2)

The production system follows **clean architecture principles** with clear separation of concerns:

#### 1. **Agent Layer** (`src/agent/`)
- **Purpose**: Core AI intelligence and conversation management
- **Components**:
  - `agent.py`: Main agent using OpenAI Agents SDK
  - `tools.py`: 6 functional tools (search, create_ticket, escalate, etc.)
  - `prompts.py`: Channel-specific prompts and context building
  - `formatter.py`: Response formatting per channel (email vs WhatsApp vs web)
  - `sentiment.py`: Sentiment analysis for escalation decisions

#### 2. **Services Layer** (`src/services/`)
- **Purpose**: Business logic orchestration
- **Components**:
  - `customer_service.py`: Customer lifecycle management
  - `ticket_service.py`: Ticket operations with SLA management
  - `conversation_service.py`: Conversation state management
  - `metrics_service.py`: Analytics and dashboard metrics

#### 3. **Worker Layer** (`src/worker/`)
- **Purpose**: Asynchronous event processing
- **Components**:
  - `ticket_processor.py`: Process incoming tickets from Kafka
  - `response_dispatcher.py`: Dispatch AI responses to appropriate channels
  - `metrics_collector.py`: Collect and aggregate system metrics

#### 4. **Database Layer** (`src/database/`)
- **Purpose**: Persistent data storage with clean access patterns
- **Components**:
  - `models.py`: SQLAlchemy ORM models
  - `base.py`: Base repository with common CRUD operations
  - `repositories/`: Per-table repositories (customer, ticket, message, conversation, knowledge)
  - `connection.py`: Async database session management

#### 5. **Kafka Layer** (`src/kafka/`)
- **Purpose**: Event-driven communication for scalability
- **Components**:
  - `topics.py`: Topic definitions and configuration
  - `producer.py`: Event publishing to topics
  - `consumer.py`: Event consumption from topics

#### 6. **API Layer** (`src/api/`)
- **Purpose**: HTTP endpoints for channel integrations
- **Components**:
  - Channel-specific routes (email, whatsapp, web_form)
  - Health check endpoints
  - Metrics endpoints

#### 7. **Core Layer** (`src/core/`)
- **Purpose**: Shared utilities and configuration
- **Components**:
  - `config.py`: Application settings
  - `logging.py`: Structured JSON logging
  - `exceptions.py`: Custom domain exceptions
  - `utils.py`: Common utility functions

#### 8. **Channel Integration Layer** (`src/channels/`)
- **Purpose**: External API integrations
- **Components**:
  - `gmail_handler.py`: Gmail API integration
  - `whatsapp_handler.py`: Twilio WhatsApp integration
  - `web_form_handler.py`: Web form handling

---

## 🎨 UI Visualizations - What All 5 Pages Look Like

### Page 1: Customer Support Form (`/support`)

```
┌─────────────────────────────────────────────────────────────┐
│                                                       │
│  ████████████████████████████████████████████        │
│  ███ TechFlow Customer Support ███                      │
│  ████████████████████████████████████████            │
│                                                       │
│  Submit your inquiry and we'll respond within 24 hours       │
│                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Name *                                            │   │
│  │ [email input........................]      │   │
│  │                                                    │   │
│  │ Email *                                            │   │
│  │ [john@example.com.....................]      │   │
│  │                                                    │   │
│  │ Subject *                                           │   │
│  │ [How can I reset my password?........]      │   │
│  │                                                    │   │
│  │ Category ▼ [General Question ▼]         │   │
│  │                                                    │   │
│  │ Priority   ▼ [Medium ▼]                  │   │
│  │                                                    │   │
│  │ Message *                                          │   │
│  │ [I need to reset my account password...]      │   │
│  │                                                    │   │
│  │  [Submit Ticket]                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                       │
│  Contact Options:                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 📧 Email: support@techflow.com         │   │
│  │ 💬 WhatsApp: +1 (555) 123-4567          │   │
│  │ 🌐 Web Form: Fastest response time    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                       │
│  Response Times:                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🟢 Critical: 1 hour                        │   │
│  │ 🟠 High: 4 hours                           │   │
│  │ 🟡 Medium: 24 hours                         │   │
│  │ 🟣 Low: 72 hours                          │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Page 2: Customer Ticket Status (`/support/ticket/TKT-1234`)

```
┌─────────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████████        │
│  ███ Ticket Status ███                                │
│  ████████████████████████████████████████            │
│                                                       │
│  ← [Back to Support]                                  │
│                                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Ticket #TKT-1234                                  │   │
│  │  [🟢 OPEN]                                          │   │
│  │                                                       │   │
│  │  ─────────────────────────────────────────────   │   │
│  │                                                       │   │
│  │  Customer: John Doe (john@acme.com)          │   │
│  │  Channel: 📧 Email                              │   │
│  │  Category: Technical Support                        │   │
│  │  Priority: [🟡 MEDIUM]                             │   │
│  │                                                       │   │
│  │  Created: March 14, 2026 at 10:30 AM            │   │
│  │  Updated: March 14, 2026 at 10:35 AM            │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  ┌─────────────────────────────────────────────┐ │   │
│  │  │ 👤                          │         │   │
│  │  │ I need help setting up my account.     │   │
│  │  └─────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────┐ │   │
│  │  │ 🤖                          │         │   │
│  │  │ I've created an account. Please verify    │   │
│  │  │    your email by clicking the link we     │   │
│  │  │    sent you. Thank you!               │   │
│  │  └─────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────┐ │   │
│  │  │ 👤                          │         │   │
│  │  │ That worked perfectly! Let me know if     │   │
│  │  │    you need anything else.                │   │
│  │  └─────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  └───────────────────────────────────────────────┘   │
│                                                       │
└─────────────────────────────────────────────────────────────┘
```

### Page 3: Admin Dashboard (`/admin`)

```
┌─────────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████████        │
│  ███ Admin Dashboard ███                             │
│  ████████████████████████████████████████            │
│                                                       │
│  Friday, March 14, 2026 3:00 PM                       │
│                                                       │
│  🟢 3 Workers Online                                 │
│                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  TODAY'S STATS                                       │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │   │
│  │  │  Total    │ │ Resolved │ │Escalated │ │  Avg   │ │   │
│  │  │  245     │ │   198    │ │   47     │ │ 2.3s  │ │   │
│  │  │  tickets  │ │          │ │          │ │ Response│ │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘ │   │
│  │                                                     │   │
│  │  BY CHANNEL                                          │   │
│  │  Email:     ████████████ 80 tickets                   │   │
│  │  WhatsApp:  ████████ 50 tickets                     │   │
│  │  Web Form: ██████████████ 115 tickets                  │   │
│  │                                                     │   │
│  │  SENTIMENT TODAY                                      │   │
│  │  Positive 45% | Neutral 35% | Negative 20%        │   │
│  │  ██████████████████████████████████████████ 85%    │   │
│  │                                                     │   │
│  │  ESCALATION QUEUE ⚠️ (47 pending)                │   │
│  │  ┌─────────────────────────────────────────────────────┐   │
│  │  Ticket #    │ Customer        │ Reason           │ Priority│   │   │
│  │  ─────────────────────────────────────────────────   │   │
│  │  TKT-1234   │ john@acme.com   │ Refund $50k   │  [🔴 CRIT]│   │   │
│  │  TKT-1235   │ +15551234567    │ Legal query     │  [🟠 HIGH]  │   │
│  │  TKT-1236   │ mike@co.com       │ HIPAA docs    │  [🟠 HIGH]  │   │
│  │  TKT-1237   │ sarah@gmail.com    │ Pricing issue  │  [🟡 MEDIUM]│   │   │
│  │  └────────────────────────────────────────────────   │   │
│  │                                                     │   │
│  │  [View All Escalated Tickets →]                     │   │
│  │                                                     │   │
└─────────────────────────────────────────────────────────────┘
```

### Page 4: Admin All Tickets (`/admin/tickets`)

```
┌─────────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████████        │
│  ███ All Tickets ███                                 │
│  ████████████████████████████████████████            │
│                                                       │
│  ← [Back to Dashboard]                                  │
│                                                       │
│  Filter: [All Channels ▼] [All Status ▼] [All Priorities ▼]  │
│                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Ticket #    │ Customer         │ Channel │ Category  │Priority│Status │Created       │Actions        │   │
│  │  ─────────────────────────────────────────────────   │   │
│  │  TKT-1234   │ john@acme.com   │ 📧 Email│Technical│  [🟡 MEDIUM]│[🟢 OPEN]│Mar 14, 10:30│[⏰][✅]       │   │
│  │  TKT-1235   │ +15551234567   │ 💬 WA    │Billing  │  [🔴 CRIT]│[🟢 OPEN]│Mar 14, 11:15│[⏰][✅]       │   │
│  │  TKT-1236   │ mike@co.com       │ 📧 Email│HIPAA    │  [🟠 HIGH] │[🟢 OPEN]│Mar 14, 09:45│[⏰]            │   │
│  │  TKT-1237   │ sarah@gmail.com    │ 🌐 Web   │Feedback │  [🟡 MEDIUM]│[🟢 OPEN]│Mar 14, 08:20│[⏰][✅]       │   │
│  │  TKT-1238   │ alex@tech.co     │ 📧 Email│Bug Rpt  │  [🟣 LOW]  │[✅ RES] │Mar 14, 07:00│               │   │
│  │  TKT-1239   │ lisa@demo.com     │ 💬 WA    │General  │  [🟡 MEDIUM]│[🟢 OPEN]│Mar 14, 06:30│[⏰]            │   │
│  │  TKT-1240   │ bob@acme.com       │ 📧 Email│Technical│  [🟣 LOW]  │[🟢 OPEN]│Mar 14, 05:15│[⏰]            │   │
│  │  TKT-1241   │ +15559876543    │ 🌐 Web   │General  │  [🟡 MEDIUM]│[🟢 OPEN]│Mar 14, 04:00│[⏰]            │   │
│  │  TKT-1242   │ kim@example.com     │ 💬 WA    │Feedback │  [🟣 LOW]  │[🔄 PEND]│Mar 14, 03:30│[⏰]            │   │
│  │  TKT-1243   │ +15559876543    │ 🌐 Web   │General  │  [🟡 MEDIUM]│[🟢 OPEN]│Mar 14, 02:00│[⏰]            │   │
│  │  TKT-1244   │ jane@demo.com     │ 📧 Email│Billing  │  [🔴 CRIT]│[🟢 OPEN]│Mar 14, 01:00│               │   │
│  │  TKT-1245   │ mike@acme.com     │ 📧 Email│Technical│  [🟣 LOW]  │[✅ RES] │Mar 14, 12:00│               │   │
│  │  ─────────────────────────────────────────────────   │   │
│  │                  [Previous]  Page 1 of 24  [Next >]        │   │
│                                                       │
└─────────────────────────────────────────────────────────────┘
```

### Page 5: Admin Single Ticket + Human Reply (`/admin/tickets/TKT-1234`) ⭐

```
┌─────────────────────────────────────────────────────────────┐
│  ████████████████████████████████████████████        │
│  ███ Ticket #TKT-1234 - Human Reply ███              │
│  ████████████████████████████████████████            │
│                                                       │
│  ← [Back to All Tickets]  [Mark Resolved]  [Reassign]   │
│                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Ticket #TKT-1234                                 │   │
│  │  [🔴 ESCALATED]                                     │   │
│  │                                                       │   │
│  │  ─────────────────────────────────────────────────   │   │
│  │  Customer: John Doe (john@acme.com)          │   │
│  │  Channel: 📧 Email                              │   │
│  │  Category: Technical Support                        │   │
│  │  Priority: [🔴 CRITICAL]                             │   │
│  │  Created: March 14, 2026 at 10:00 AM            │   │
│  │                                                       │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ 👤                                         │   │   │
│  │  │ John Doe                                     │   │
│  │  │ john@acme.com                                 │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ─────────────────────────────────────────────────   │   │
│  │  3 previous tickets                              │   │
│  │  • Last contact: 5 days ago via Web Form       │   │
│  │  • Overall sentiment: Neutral → Negative          │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ 👤                                         │   │   │
│  │  │ (Email - 10:00am):                          │   │
│  │  │ We've decided not to move forward with            │   │
│  │  │    TechFlow. Please process our refund of   │   │
│  │  │    $50,000.                                 │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────────────┐ │   │
│  │  │ 🤖                                         │   │   │
│  │  │ (AI - 10:05am):                          │   │
│  │  │ I understand your concern. This requires             │   │
│  │  │    escalation to our billing team.               │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  [Escalated: billing/refund_request]           │   │
│  │                                                     │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  💬 YOUR REPLY                                        │   │
│  │                                                     │   │
│  │  Send via: [📧 Email ●]  [💬 WhatsApp ○]  [🌐 Web Form ○]   │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────────────┐   │
│  │  │                                              │   │
│  │  │  Dear John, I've reviewed your refund     │   │
│  │  │  request. We've decided not to proceed with      │   │
│  │  │    it. Please contact billing@techflow.com for       │   │
│  │  │    more details.                                 │   │
│  │  │                                              │   │
│  │  └─────────────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  [Send Reply]                                      │   │
│  │                                                     │   │
└─────────────────────────────────────────────────────────────┘
```

---

### UI Design Principles Applied:

**1. Customer-Friendly Design:**
- Clean, welcoming interface
- Clear CTA (Call-to-Action) buttons
- Loading states for better UX
- Success/error feedback

**2. Professional Admin Interface:**
- Data-dense displays (tables, stats)
- Color-coded status indicators
- Priority badges for urgency
- Clear escalation queue visibility

**3. Consistent Styling:**
- Tailwind CSS for responsive design
- Dark mode support
- Proper spacing and hierarchy
- Accessible color contrasts

**4. User Experience:**
- Instant feedback on actions
- Clear navigation paths
- Loading indicators during async operations
- Mobile-first responsive design

These visualizations show exactly what users will see on each of the 5 pages!

## 📁 Complete File Structure

```
digital-fte-crm/
├── README.md                 # This file - project overview
├── part-1.md                 # Phase 1 documentation (Incubation)
├── part-2.md                 # Phase 2 documentation (Specialization)
├── pyproject.toml             # uv project configuration
├── .env.example               # Environment variables template
│
├── src/                       # Main source code
│   ├── __init__.py
│   │
│   ├── agent/               # AI Agent Layer
│   │   ├── __init__.py
│   │   ├── agent.py            # Main agent (OpenAI Agents SDK)
│   │   ├── tools.py           # Agent tools (search, create_ticket, etc.)
│   │   ├── prompts.py         # Channel-specific prompts
│   │   ├── formatter.py       # Response formatting
│   │   └── sentiment.py       # Sentiment analysis
│   │
│   ├── services/            # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── customer_service.py
│   │   ├── ticket_service.py
│   │   ├── conversation_service.py
│   │   └── metrics_service.py
│   │
│   ├── worker/              # Worker Layer
│   │   ├── __init__.py
│   │   ├── ticket_processor.py
│   │   ├── response_dispatcher.py
│   │   └── metrics_collector.py
│   │
│   ├── kafka/               # Kafka Layer
│   │   ├── __init__.py
│   │   ├── topics.py
│   │   ├── producer.py
│   │   └── consumer.py
│   │
│   ├── database/            # Database Layer
│   │   ├── __init__.py
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── base.py            # Base repository
│   │   ├── connection.py      # DB connection management
│   │   └── repositories/      # Per-table repositories
│   │       ├── __init__.py
│   │       ├── customer_repo.py
│   │       ├── ticket_repo.py
│   │       ├── message_repo.py
│   │       ├── conversation_repo.py
│   │       └── knowledge_repo.py
│   │
│   ├── channels/            # Channel Integration Layer
│   │   ├── __init__.py
│   │   ├── gmail_handler.py
│   │   ├── whatsapp_handler.py
│   │   └── web_form_handler.py
│   │
│   ├── api/                 # API Layer
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   └── routes/           # API route modules
│   │
│   └── core/               # Core Utilities
│       ├── __init__.py
│       ├── config.py
│       ├── logging.py
│       ├── exceptions.py
│       └── utils.py
│
├── migrations/               # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py
│   └── versions/             # Migration files
│
├── frontend/                # Next.js Frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── app/                  # Next.js app directory
│       ├── api/             # API routes
│       ├── components/       # React components
│       ├── support/          # Support page
│       ├── ticket-status/    # Ticket status page
│       ├── admin/            # Admin dashboard
│       ├── tickets/          # Tickets list page
│       └── conversation/     # Conversation history page
│
├── tests/                  # Test suites
│   ├── test_agent.py
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_api.py
│
├── docker/                  # Docker configurations
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   └── docker-compose.yml
│
├── k8s/                    # Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment-api.yaml
│   ├── deployment-worker.yaml
│   ├── service.yaml
│   └── hpa.yaml
│
└── monitoring/              # Monitoring setup
    ├── prometheus/
    └── grafana/
```

---

## 🎯 Project Goals

### Primary Objectives

1. **Customer Satisfaction**: Provide fast, accurate, and empathetic support 24/7
2. **Operational Efficiency**: Automate routine inquiries while escalating complex issues
3. **Scalability**: Handle thousands of concurrent conversations across channels
4. **Intelligence**: Learn from interactions to improve over time
5. **Multi-Channel Continuity**: Provide seamless experience across Email, WhatsApp, and Web

### Key Features

#### ✅ Implemented Features

**Phase 1 (Prototype)**:
- ✅ Working Customer Agent with 7 functional tools
- ✅ Web Support Form with validation
- ✅ Multi-channel conversation flow
- ✅ Sentiment analysis for escalation
- ✅ Knowledge base integration
- ✅ FastAPI endpoints for channel integration

**Phase 2 (Production)**:
- ✅ OpenAI Agents SDK implementation
- ✅ 6 agent tools: search_knowledge_base, create_ticket, get_customer_history, update_ticket_status, escalate_to_human, check_sla_status
- ✅ Repository Pattern for all database operations
- ✅ Alembic migrations for database schema
- ✅ Kafka event streaming with 8 topics
- ✅ Worker layer: ticket processor, response dispatcher, metrics collector
- ✅ Services layer: customer, ticket, conversation, metrics
- ✅ 5-page frontend: Support, Ticket Status, Admin Dashboard, Tickets List, Conversation History
- ✅ Docker and Kubernetes deployment
- ✅ Prometheus + Grafana monitoring
- ✅ Structured JSON logging

---

## 🛠️ Tech Stack Details

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.11+ | Primary development language |
| **Package Manager** | `uv` | Fast Python dependency management |
| **Agent SDK** | OpenAI Agents SDK | AI conversation management |
| **Model** | GPT-4o | Primary AI model |
| **API Framework** | FastAPI | Async REST API |
| **Event Streaming** | Kafka (aiokafka) | Scalable event processing |
| **Database ORM** | SQLAlchemy | Object-relational mapping |
| **Migrations** | Alembic | Database schema management |
| **Logging** | Structured JSON logs | Production-ready logging |

### Database

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Platform** | Neon DB (PostgreSQL) | Serverless PostgreSQL |
| **Extension** | pgvector | Semantic search with embeddings |
| **Connection** | asyncpg | High-performance async driver |
| **Connection Pool** | SQLAlchemy pool | Efficient connection management |

### Frontend - Complete 5-Page Application

The frontend is a complete Next.js application with **5 pages** split into **Customer Side** and **Admin Side**:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Next.js 14+ | React framework with App Router |
| **Styling** | Tailwind CSS + shadcn/ui | Modern UI components |
| **Forms** | react-hook-form + zod | Type-safe form handling |
| **Pages** | 5 pages | Complete support interface with customer/admin separation |

#### Complete Page Structure

```
Customer Side (2 pages)                     Admin Side (3 pages)
├── /support                  → Submit support form          ┌── /admin                    → Dashboard (overview + metrics)
└── /support/ticket/[id]        → Check ticket status      ├── /admin/tickets              → All tickets table
                                                                   └── /admin/tickets/[id]         → Single ticket + human reply
                                                                              ↑
                                                                THE MOST IMPORTANT PAGE:
                                                                HUMAN IN THE LOOP HAPPENS HERE
```

#### Customer Side Pages

**Page 1: `/support` - Support Form**
- Customer submits ticket via web form
- Form validation with react-hook-form + zod
- Categories: General, Technical, Billing, Feedback, Bug Report
- Priority levels: Low, Medium, High
- Success/error states with proper UI feedback

**Page 2: `/support/ticket/[id]` - Ticket Status**
- Customer views their ticket status
- Displays conversation history with AI responses
- Shows ticket details (status, priority, timestamps)
- Responsive design for mobile/tablet/desktop

#### Admin Side Pages

**Page 3: `/admin` - Dashboard**
- Overview metrics: total tickets, resolved today, escalated today
- Average response time calculation
- Active conversations count
- Channel performance metrics (Email, WhatsApp, Web Form)
- **Escalation Queue** ⚠️ - Shows pending escalations requiring human intervention
- Quick action buttons to navigate to other pages

**Page 4: `/admin/tickets` - All Tickets Table**
- Complete table of all tickets across all channels
- Filtering by status, channel, priority
- Search functionality
- Sortable columns
- Action buttons per ticket (view, mark resolved)

**Page 5: `/admin/tickets/[id]` - Single Ticket + Human Reply** ⭐
- **THE MOST IMPORTANT PAGE** - Where human-in-the-loop happens
- Full ticket details display
- Conversation history (AI responses + customer messages)
- Customer history across all channels
- **Reply Box** with channel selection (Email, WhatsApp, Web Form)
- When admin sends reply:
  - System determines original channel
  - Sends via Gmail API (if email was original channel)
  - OR sends via Twilio API (if WhatsApp was original channel)
  - OR saves response to web (if web form was original channel)
  - Updates ticket status to "resolved" in database
  - Customer receives human reply via their original channel
- Quick actions: Mark as Resolved, Reassign to Another Agent

#### Complete Component Structure

```
web-form/app/
├── customer/                      ← CUSTOMER SIDE (2 pages)
│   ├── support/
│   │   └── page.tsx              # /support (form page)
│   └── ticket/
│       └── [id]/
│           └── page.tsx            # /support/ticket/[id] (status page)
│
├── admin/                          ← ADMIN SIDE (3 pages)
│   ├── middleware.ts               # Admin authentication
│   ├── page.tsx                   # /admin (dashboard)
│   └── tickets/
│       ├── page.tsx               # /admin/tickets (all tickets)
│       └── [id]/
│           └── page.tsx            # /admin/tickets/[id] (single ticket + reply)
│
├── components/
│   ├── customer/                      ← CUSTOMER COMPONENTS
│   │   ├── SupportForm.tsx          # Embeddable support form
│   │   ├── SubmissionSuccess.tsx    # Success message after submission
│   │   ├── TicketStatus.tsx         # Ticket status display
│   │   └── TicketNotFound.tsx         # 404 error page
│   │
│   └── admin/                          ← ADMIN COMPONENTS
│       ├── StatsCards.tsx           # Dashboard stats cards
│       ├── ChannelMetrics.tsx       # Channel performance metrics
│       ├── EscalationQueue.tsx      # Pending escalations (critical)
│       ├── TicketsTable.tsx         # All tickets table
│       ├── ConversationHistory.tsx  # Chat thread display
│       ├── CustomerHistory.tsx      # Cross-channel history
│       └── ReplyBox.tsx            # Human reply interface (MOST IMPORTANT)
│
└── api/                            # Frontend API routes
    └── tickets/
        └── [id]/
            └── route.ts             # Ticket detail API
```

#### Human-in-the-Loop Workflow

```
Customer Journey:
/support → fills form → creates ticket → /support/ticket/[id] → checks status
                                                        ↓
                                                    (if not satisfied, customer can submit follow-up)

Admin Journey:
/admin → sees escalation queue → clicks ticket
        ↓
/admin/tickets → sees all tickets → clicks ticket
        ↓
/admin/tickets/[id] → reads full conversation + customer history
        ↓
                     types reply → selects channel → clicks "Send Reply"
        ↓
          ┌─────────────────────────────────────┐
          │                                 │
          │  "Dear John, I've reviewed your │
          │  refund request. We've decided      │
          │  not to proceed with it. Please      │
          │  contact billing@techflow.com │
          │  for more details."               │
          │                                 │
          │         ┌────────────────────┐   │
          │         │  [Send Reply]      │   │
          │         └────────────────────┘   │
          │                                 │
          └─────────────────────────────────────┘
        ↓
          Backend determines original channel (email)
        ↓
          Sends reply via Gmail API
        ↓
          Customer receives email from human
        ↓
          Updates ticket to "resolved" in database
        ↓
        Admin goes back to /admin/tickets → processes next escalation
```

**Key Points:**
- Admin sees full conversation context before replying
- Reply goes through original channel (email/WhatsApp/web form)
- Ticket automatically marked resolved when human replies
- Seamless handoff from AI to human and back

### Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Kubernetes | Container orchestration |
| **Scaling** | HPA (Horizontal Pod Autoscaler) | Auto-scaling based on load |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |
| **Channel APIs** | Gmail API, Twilio API | External integrations |

---

## 🚀 Getting Started

### Prerequisites

```bash
# Required tools
- Python 3.11+
- uv (Python package manager)
- Node.js 18+ (for frontend)
- Docker and Docker Compose
- kubectl (for Kubernetes deployment)
- Neon DB account
- OpenAI API key
- Twilio account (for WhatsApp)
- Google Cloud project (for Gmail)

# Optional but recommended
- kubectl (for local Kubernetes)
- Helm (for package management)
```

### Quick Start (Phase 1)

```bash
# Clone repository
git clone <repository-url>
cd digital-fte-crm

# Set up Python environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configurations

# Run database migrations (Phase 2)
uv run alembic upgrade head

# Start API server
uv run uvicorn src.api.main:app --reload

# In another terminal, start frontend
cd frontend
npm install
npm run dev
```

### Production Deployment (Phase 2)

```bash
# Build Docker images
docker build -t fte-api:latest .
docker build -t fte-worker:latest -f docker/Dockerfile.worker .

# Push to registry
docker push <registry>/fte-api:latest
docker push <registry>/fte-worker:latest

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Check deployment
kubectl get pods -n customer-success-fte
kubectl get services -n customer-success-fte
```

---

## 📊 Key Performance Metrics

### Success Criteria

The project is considered successful when:

**Phase 1**:
- ✅ Agent can handle multi-channel conversations
- ✅ Web form creates tickets successfully
- ✅ Sentiment analysis triggers appropriate escalations
- ✅ Knowledge base integration works
- ✅ Basic monitoring is in place

**Phase 2**:
- ✅ All 8 Kafka topics are created and consuming
- ✅ Workers process events without errors
- ✅ API handles 100+ concurrent requests
- ✅ Database migrations run successfully
- ✅ Frontend renders all 5 pages correctly
- ✅ Admin dashboard shows real-time metrics
- ✅ HPA scales workers based on load
- ✅ Monitoring collects metrics across all components

### Monitoring Dashboard

The admin dashboard provides:

- **Ticket Overview**: Open, in-progress, resolved, escalated counts
- **Channel Performance**: Metrics per channel (email, WhatsApp, web)
- **Agent Performance**: Response time, token usage, tool calls
- **SLA Compliance**: Tickets within/overdue SLA targets
- **System Health**: Worker status, Kafka lag, database connections
- **Recent Activity**: Latest tickets, conversations, and escalations

---

## 🧪 Development Workflow

### Feature Development

1. **Design**: Define requirements and API contracts
2. **Database**: Create/update schema via Alembic
3. **Repository**: Implement repository methods
4. **Service**: Add business logic
5. **Worker**: Update worker processing
6. **Test**: Write comprehensive tests
7. **Deploy**: Update Kubernetes manifests
8. **Monitor**: Track metrics in production

### Testing Strategy

```bash
# Run all tests
uv run pytest tests/

# With coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test suites
uv run pytest tests/test_agent.py
uv run pytest tests/test_services.py
uv run pytest tests/test_repositories.py
```

### Code Quality

```bash
# Format code
uv run black src/
uv run isort src/

# Type checking
uv run mypy src/

# Linting
uv run ruff src/

# Security scanning
uv run bandit -r src/
```

---

## 📚️ Documentation

### Project Documentation

- **[README.md](README.md)** - This file: Project overview
- **[part-1.md](part-1.md)** - Phase 1: Incubation (Prototype)
- **[part-2.md](part-2.md)** - Phase 2: Specialization (Production)
- **[pyproject.toml](pyproject.toml)** - Python project configuration
- **[.env.example](.env.example)** - Environment variables template

### API Documentation

Once running, access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🔒️ Security Considerations

### Data Protection

- **Input Validation**: All user inputs are validated and sanitized
- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
- **Rate Limiting**: API rate limiting per customer/channel
- **Secrets Management**: Kubernetes Secrets for sensitive data
- **HTTPS Only**: All communications use TLS

### Access Control

- **API Keys**: Restricted access via environment variables
- **Database Access**: Connection pooling with proper authentication
- **Channel APIs**: OAuth 2.0 for Gmail, API keys for Twilio
- **Admin Access**: Authentication required for admin dashboard

---

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**:
```bash
# Check Neon DB connection string
echo $DATABASE_URL

# Test connection
uv run python -c "from src.core.database import init_database; import asyncio; asyncio.run(init_database())"
```

**Kafka Not Consuming**:
```bash
# Check Kafka connectivity
kubectl exec -it <kafka-pod> -- kafka-console-consumer --bootstrap-server kafka:9092 --topic fte.tickets.incoming

# Check consumer group offsets
kubectl exec -it <kafka-pod> -- kafka-consumer-groups --bootstrap-server kafka:9092 --group fte-worker-group
```

**Workers Not Scaling**:
```bash
# Check HPA status
kubectl get hpa -n customer-success-fte

# Describe HPA for metrics
kubectl describe hpa customer-success-fte-hpa -n customer-success-fte
```

### Logs

```bash
# View API logs
kubectl logs -f deployment/customer-success-fte-api -n customer-success-fte

# View worker logs
kubectl logs -f deployment/customer-success-fte-worker -n customer-success-fte

# View specific pod logs
kubectl logs -f <pod-name> -n customer-success-fte
```

---

## 📈 Future Enhancements

### Potential Improvements

**Phase 3 & 4** (Integration & Final Challenge):
- **Advanced Analytics**: Machine learning for predictive insights
- **Voice Support**: Integration with voice channels
- **Chat Widget**: Embedded chat for websites
- **Multi-Language**: Support for international customers
- **Mobile App**: Native mobile experience
- **CRM Integration**: Deeper integration with existing CRM systems
- **Self-Healing**: Automatic recovery from failures
- **Canary Deployments**: Gradual rollouts for safety

---

## 👥 Contributing

### Development Setup

```bash
# Fork the repository
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
git add .
git commit -m "Add your feature"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Review Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines (black, isort)
- [ ] Type hints are complete
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Logging is appropriate

---

## 📞 Support

### Getting Help

For questions or issues:

1. **Check Documentation**: Review [part-1.md](part-1.md) and [part-2.md](part-2.md)
2. **Review Logs**: Check application logs for error messages
3. **Check Status**: Verify all services are running
4. **GitHub Issues**: Search existing issues before creating new one
5. **Team Communication**: Reach out to team members

### Emergency Contacts

- **Technical Lead**: [Contact info]
- **DevOps**: [Contact info]
- **Product Owner**: [Contact info]

---

## 📄 License

This project is part of a hackathon competition. All code is provided as-is for educational purposes.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o model and Agents SDK
- **TechFlow SaaS** - Use case scenario
- **Hackathon Organizers** - Project guidance and support

---

## 📊 Project Statistics

- **Total Development Time**: 40 hours (Phase 1 + Phase 2)
- **Lines of Code**: ~15,000+ lines
- **Components**: 8 major layers, 40+ files
- **API Endpoints**: 20+ REST endpoints
- **Database Tables**: 5 tables with relationships
- **Kafka Topics**: 8 topics for event streaming
- **Frontend Pages**: 5 fully functional pages
- **Integration Points**: 3 external APIs (Gmail, Twilio, Web)
- **Deployment Targets**: Kubernetes with HPA

---

## 🎉 Summary

This **Customer Success Digital FTE** project represents a complete, production-grade AI customer support system that:

✅ **Validates the Digital FTE concept** through working prototype
✅ **Scales horizontally** using Kafka and Kubernetes
✅ **Maintains clean architecture** with proper separation of concerns
✅ **Provides multi-channel support** with channel-aware responses
✅ **Includes comprehensive monitoring** for production operations
✅ **Follows best practices** for security, testing, and deployment

**Built with modern Python and React technologies**, this system is ready for production deployment and can serve as a foundation for further enhancements and real-world customer support operations.

---

**For detailed implementation guidance:**
- **Phase 1**: See [part-1.md](part-1.md) - 16-hour prototype phase
- **Phase 2**: See [part-2.md](part-2.md) - 24-hour production phase

**Ready to transform customer support operations! 🚀**

# 🚀 EntreaseAI

<div align="center">

**EntreaseAI- AI Invoice Processing System**


[![Next.js](https://img.shields.io/badge/Next.js-15.2.4-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3.3-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?style=for-the-badge&logo=supabase)](https://supabase.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-purple?style=for-the-badge&logo=openai)](https://openai.com/)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏗️ Architecture](#️-architecture)
- [🧠 Core Subsystems](#-core-subsystems)
- [🔧 Key Features](#-key-features)
- [🚀 Technology Stack](#-technology-stack)
- [📁 Project Structure](#-project-structure)
- [⚡ Quick Start](#-quick-start)
- [🔒 Security & Compliance](#-security--compliance)
- [📊 Performance](#-performance)
- [🤝 Contributing](#-contributing)

---

## 🎯 Overview

EntreaseAI is a comprehensive enterprise-grade invoice processing system that leverages cutting-edge AI, fuzzy logic algorithms, and advanced matching techniques to automatically process invoices and integrate them with popular accounting systems like QuickBooks and Xero.

### ✨ Key Capabilities

- 🤖 **AI-Powered Processing** - GPT-4o Vision for document classification and data extraction
- 🎯 **Fuzzy Matching** - Intelligent account, vendor, and tax code matching
- 📧 **Email Integration** - Automated email listening and notification system
- 💼 **Multi-Provider Support** - QuickBooks, Xero, and extensible architecture
- 🔐 **Enterprise Security** - SOC 2 Type II compliance, RLS, audit logging
- 👥 **Team Collaboration** - Organization management and user roles
- 💳 **Subscription Management** - Stripe-powered billing and payments



## 🧠 Core Subsystems

### 🤖 AI Processing Pipeline
**Location**: `lib/invoice-extractor.ts` | `lib/accounting/matching/ai_recommendations.ts`

| Component | File | Description |
|-----------|------|-------------|
| **Document Classification** | `app/api/classify-and-process-document/route.ts` | GPT-4o Vision classification |
| **Text Extraction** | `lib/invoice-extractor.ts` | PDF parsing with OCR fallback |
| **AI Structuring** | `structureInvoiceDataFromTextAI()` | GPT-4o data extraction |
| **Image Processing** | `lib/image-extractor.ts` | Multi-format image support |

### 🎯 Fuzzy Logic & Matching
**Location**: `lib/accounting/matching/`

| Algorithm | File | Technology |
|-----------|------|------------|
| **Account Matching** | `account_matcher.ts` | Fuzzball + GPT (50/50) |
| **Vendor Matching** | `vendor_matcher.ts` | Email + Name similarity |
| **Tax Code Matching** | `tax_code_matcher.ts` | Intelligent mapping |
| **AI Recommendations** | `ai_recommendations.ts` | Context-aware suggestions |

### 📧 Email & Notifications
**Location**: `lib/email-service.ts` | `lib/accounting/services/notification.service.ts`

| Service | File | Features |
|---------|------|----------|
| **Email Service** | `lib/email-service.ts` | SendGrid integration |
| **Notification Service** | `notification.service.ts` | Rate limiting, audit logging |
| **Webhook Handlers** | `app/api/webhooks/stripe/route.ts` | Event processing |

### 💼 Accounting Integrations
**Location**: `lib/accounting/`

| Provider | Directory | Features |
|----------|-----------|----------|
| **QuickBooks** | `lib/accounting/quickbooks/` | OAuth 2.0, Bill creation |
| **Xero** | `lib/accounting/xero/` | API integration, Sync |
| **Adapter Factory** | `adapters/adapter-factory.ts` | Unified interface |
| **Provider Data** | `services/provider-data.service.ts` | Data synchronization |

### 🔐 Security & Authentication
**Location**: `middleware.ts` | `lib/auth.ts` | `utils/validation/`

| Component | File | Security Features |
|-----------|------|-------------------|
| **Middleware** | `middleware.ts` | Supabase SSR, Route protection |
| **API Security** | `utils/validation/api-validation.ts` | Rate limiting, Validation |
| **Database Security** | `scripts/*.sql` | RLS policies, User isolation |
| **Client Auth** | `lib/client-auth.ts` | Session management |

### 🗄️ Database Layer
**Location**: `lib/supabase/` | `scripts/`

| Component | Description |
|-----------|-------------|
| **Supabase Client** | PostgreSQL with real-time subscriptions |
| **Database Scripts** | Automated migrations and schema updates |
| **Key Tables** | `users`, `ai_analysis_history`, `notification_tracking`, `audit_log` |

### 🖥️ Frontend Dashboard
**Location**: `app/dashboard/` | `components/`

| Page | File | Features |
|------|------|----------|
| **Main Dashboard** | `app/dashboard/page.tsx` | Real-time stats, Analysis history |
| **Invoice Processing** | `app/invoice-processing/` | File upload, Status tracking |
| **UI Components** | `components/ui/` | Radix UI + Tailwind design system |

### ⚙️ Workflow Orchestration
**Location**: `lib/accounting/services/workflow-orchestrator.service.ts`

**Processing Pipeline**:
1. 📄 **PDF Processing** - Upload, extract, validate
2. 🔍 **Provider Data Fetch** - Get accounts, vendors, tax codes
3. 🤖 **AI Analysis** - Generate recommendations
4. ✅ **Validation** - Business rule validation
5. 📋 **Bill Creation** - Create bill in accounting system
6. 📧 **Notification** - Send success/failure emails

**Error Handling**:
- 🔄 Circuit breaker pattern
- ⏱️ Retry logic with exponential backoff
- 📊 Comprehensive logging and monitoring

### 🌐 API Layer
**Location**: `app/api/`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/classify-and-process-document` | POST | Document processing |
| `/api/auth/callback` | POST | OAuth callbacks |
| `/api/webhooks/stripe` | POST | Payment webhooks |
| `/api/organization-invites` | GET/POST | Team management |

### 📊 Monitoring & Logging
**Location**: `lib/logger.ts` | `lib/metrics.ts`

| Component | File | Purpose |
|-----------|------|---------|
| **Winston Logger** | `lib/logger.ts` | Structured logging |
| **Metrics Collection** | `lib/metrics.ts` | Performance monitoring |
| **Health Checks** | `lib/health-check.ts` | System health |
| **Circuit Breaker** | `lib/circuit-breaker.ts` | Fault tolerance |

### 📄 File Processing
**Location**: `lib/`

| Service | File | Purpose |
|---------|------|---------|
| **Invoice Storage** | `lib/invoice-storage.ts` | File management |
| **Convertio API** | `lib/convertio-api.ts` | PDF conversion |
| **Image Extractor** | `lib/image-extractor.ts` | OCR processing |

### 💳 Payment Processing
**Location**: `lib/stripe.ts` | `components/` | `app/api/`

| Component | File | Features |
|-----------|------|----------|
| **Stripe Integration** | `lib/stripe.ts` | Payment processing |
| **Checkout Sessions** | `app/api/checkout_sessions/route.ts` | Subscription creation |
| **Subscription Management** | `app/api/cancel-subscription/route.ts` | Cancellation handling |
| **UI Components** | `components/UpgradeButton.tsx` | Payment interface |

### 👥 Organization & Team Management
**Location**: `utils/helpers/organization.ts` | `components/` | `hooks/`

| Component | File | Features |
|-----------|------|----------|
| **Organization Helpers** | `utils/helpers/organization.ts` | Core organization logic |
| **Organization Hook** | `hooks/use-organization.ts` | React state management |
| **Organization UI** | `components/organization-section.tsx` | Team management interface |
| **Invite Management** | `app/api/organization-invites/route.ts` | Team invitations |

### 🚀 User Onboarding
**Location**: `app/onboarding/` | `app/select-provider/` | `components/`

| Step | File | Purpose |
|------|------|---------|
| **Email Provider Setup** | `app/onboarding/email-provider/page.tsx` | Email configuration |
| **Gmail Setup** | `app/onboarding/gmail-setup/page.tsx` | Gmail integration |
| **Provider Selection** | `app/select-provider/page.tsx` | Accounting provider choice |
| **Invoice Upload** | `app/onboarding/invoice-upload/page.tsx` | First invoice processing |

### 🔐 Authentication & User Management
**Location**: `app/auth/` | `components/` | `lib/`

| Component | File | Features |
|-----------|------|----------|
| **Login/Signup** | `app/auth/login/page.tsx` | User authentication |
| **Auth Components** | `components/login-form.tsx` | Form interfaces |
| **Auth Actions** | `lib/actions.ts` | Authentication logic |
| **Client Auth** | `lib/client-auth.ts` | Client-side auth |

### 📋 Bill Creation Service
**Location**: `lib/accounting/services/bill-creation.service.ts`

| Feature | Description |
|---------|-------------|
| **Bill Creation** | Provider-specific bill creation logic |
| **Validation** | Business rule validation |
| **Error Handling** | Comprehensive error management |

### 🛠️ Utility Services
**Location**: `utils/` | `lib/`

| Service | File | Purpose |
|---------|------|---------|
| **Validation** | `utils/validation/` | Input validation schemas |
| **Helpers** | `utils/helpers/` | Utility functions |
| **Enterprise Utils** | `utils/enterprise/` | Enterprise features |
| **Redis** | `lib/redis.ts` | Caching layer |
| **Distributed Lock** | `lib/distributed-lock.ts` | Concurrency control |

### ⚙️ Configuration & Types
**Location**: `lib/config/` | `types/`

| Component | File | Purpose |
|-----------|------|---------|
| **Provider Config** | `lib/config/providers.ts` | Provider configurations |
| **Type Definitions** | `types/` | TypeScript interfaces |
| **Enterprise Types** | `types/enterprise.ts` | Enterprise-specific types |

---

## 🔧 Key Features

### 🤖 AI-Powered Intelligence
- **Document Classification** - Distinguish between invoices, receipts, and expenses
- **Text Extraction** - Advanced PDF parsing with OCR fallback
- **Data Structuring** - Extract vendor, line items, totals, and tax codes
- **Fuzzy Matching** - Intelligent account and vendor matching algorithms

### 💼 Accounting Integration
- **Multi-Provider Support** - QuickBooks, Xero with extensible architecture
- **OAuth 2.0 Authentication** - Secure provider connections
- **Real-time Sync** - Automatic data synchronization
- **Bill Creation** - Seamless invoice-to-bill conversion

### 🔐 Enterprise Security
- **SOC 2 Type II Compliance** - Industry-standard security controls
- **Row Level Security** - Database-level access control
- **Audit Logging** - Comprehensive activity tracking
- **Rate Limiting** - API and notification throttling

### 👥 Team Collaboration
- **Organization Management** - Multi-user team support
- **Role-based Access** - Granular permission control
- **Invite System** - Seamless team member onboarding
- **User Onboarding** - Guided setup process

---

## 🚀 Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.2.4 | React framework with App Router |
| **React** | 19 | UI library with hooks |
| **TypeScript** | 5.3.3 | Type safety and development experience |
| **Tailwind CSS** | 3.4.17 | Utility-first CSS framework |
| **Radix UI** | Latest | Accessible component primitives |

### Backend
| Technology | Purpose |
|------------|---------|
| **Node.js** | JavaScript runtime |
| **PostgreSQL** | Primary database (via Supabase) |
| **Redis** | Caching and session storage |
| **Winston** | Structured logging |

### AI & Processing
| Technology | Purpose |
|------------|---------|
| **OpenAI GPT-4o** | Document analysis and data extraction |
| **OpenAI GPT-4o Vision** | Image-based document classification |
| **Fuzzball** | String similarity and fuzzy matching |
| **pdf2json** | PDF text extraction |
| **Convertio API** | PDF to image conversion |

### Integrations
| Service | Purpose |
|---------|---------|
| **QuickBooks** | Accounting system integration |
| **Xero** | Accounting system integration |
| **SendGrid** | Email delivery service |
| **Stripe** | Payment processing |
| **Supabase** | Backend-as-a-Service |

---

## 📁 Project Structure

```
entreaseai/
├── 📱 app/                          # Next.js App Router
│   ├── 🔌 api/                      # API Routes & Webhooks
│   ├── 🔐 auth/                     # Authentication Pages
│   ├── 📊 dashboard/                # Main Dashboard
│   ├── 🚀 onboarding/               # User Onboarding
│   └── 📄 invoice-processing/       # Invoice Processing UI
├── 🧩 components/                   # React Components
│   ├── 🎨 ui/                       # Reusable UI Components
│   └── ⚡ [feature-components]      # Feature-specific Components
├── 📚 lib/                          # Core Business Logic
│   ├── 💼 accounting/               # Accounting Provider Integrations
│   ├── 🗄️ supabase/                 # Database Layer
│   └── 🔧 [core-services]           # Core Services
├── 🛠️ utils/                        # Utility Functions
├── 🎣 hooks/                        # React Hooks
├── 📝 types/                        # TypeScript Definitions
└── 📜 scripts/                      # Database Scripts & Migrations
```

---

## ⚡ Quick Start

### Prerequisites
- Node.js 18+ 
- PostgreSQL database
- Supabase account
- OpenAI API key
- SendGrid account
- QuickBooks/Xero developer accounts

### Installation

    ```bash
# Clone the repository
git clone https://github.com/your-org/entreaseai.git
cd entreaseai

# Install dependencies
    pnpm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run database migrations
# Execute scripts in /scripts directory

# Start development server
pnpm dev
```

### Environment Variables

    ```bash
# Database
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# AI Services
OPENAI_API_KEY=your_openai_key

# Email
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=your_from_email

# Accounting Providers
QUICKBOOKS_CLIENT_ID=your_quickbooks_client_id
QUICKBOOKS_CLIENT_SECRET=your_quickbooks_secret
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_secret

# Other Services
STRIPE_SECRET_KEY=your_stripe_secret
REDIS_URL=your_redis_url
```

---

## 🔒 Security & Compliance

### Security Features
- 🔐 **Authentication** - Supabase Auth with JWT tokens
- 🛡️ **Authorization** - Role-based access control (RBAC)
- 🔒 **Data Encryption** - Encryption in transit and at rest
- 🚫 **Input Validation** - Comprehensive input sanitization
- 🛡️ **SQL Injection Prevention** - Parameterized queries
- 🚫 **XSS Protection** - Content Security Policy
- 🛡️ **CSRF Protection** - CSRF tokens

### Compliance
- ✅ **SOC 2 Type II** - Security and availability controls
- ✅ **GDPR Ready** - Data protection and privacy controls
- ✅ **Audit Logging** - Comprehensive activity tracking
- ✅ **Data Retention** - Configurable data retention policies

---

## 📊 Performance

### Optimizations
- ⚡ **Connection Pooling** - Database connection optimization
- 🚀 **Redis Caching** - Frequently accessed data caching
- 📱 **Lazy Loading** - Component and data lazy loading
- 🖼️ **Image Optimization** - Next.js image optimization
- 📦 **Code Splitting** - Dynamic imports for better performance

### Monitoring
- 📊 **Winston Logging** - Structured logging with multiple transports
- 📈 **Metrics Collection** - Performance and usage metrics
- 🏥 **Health Checks** - System health monitoring
- 🔄 **Circuit Breakers** - Fault tolerance and resilience

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
    ```bash
# Install dependencies
pnpm install

# Run tests
pnpm test

# Run linting
pnpm lint

# Run type checking
pnpm type-check
```

### Code Standards
- Follow TypeScript best practices
- Use ESLint and Prettier for code formatting
- Write comprehensive tests
- Follow conventional commit messages
- Ensure all tests pass before submitting PRs

---

<div align="center">

**Built with ❤️ by the EntreaseAI Team**

[Documentation](https://docs.entreaseai.com) • [Support](https://support.entreaseai.com) • [Status](https://status.entreaseai.com)

</div>

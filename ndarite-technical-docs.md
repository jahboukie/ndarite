# NDARite Platform: Complete Technical Production Documentation
## Comprehensive Development Specification for Augment Code Implementation

**Status: IMPLEMENTATION IN PROGRESS**
**Implementation Date: {{ current_date }}**
**Developer: Augment Agent (AI Coding Master)**

---

## 1. Project Overview & Architecture

### 1.1 Product Summary
**NDARite** is a SaaS platform that generates legally-compliant, industry-specific Non-Disclosure Agreements through an intelligent questionnaire system, eliminating the need for expensive attorney consultations for standard NDA requirements.

### 1.2 System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Services      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (External)    │
│                 │    │                 │    │                 │
│ - React UI      │    │ - Auth Service  │    │ - DocuSign API  │
│ - Form Engine   │    │ - Doc Generator │    │ - Stripe API    │
│ - PDF Preview   │    │ - Template Mgmt │    │ - Email Service │
│ - Dashboard     │    │ - User Mgmt     │    │ - File Storage  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────────┐
                    │   Database      │
                    │   (PostgreSQL)  │
                    │                 │
                    │ - Users         │
                    │ - Templates     │
                    │ - Documents     │
                    │ - Subscriptions │
                    └─────────────────┘
```

### 1.3 Technology Stack

#### Frontend Stack
- **Framework**: Next.js 14+ (App Router)
- **UI Library**: React 18+ with TypeScript
- **Styling**: Tailwind CSS 3.4+
- **Form Management**: React Hook Form + Zod validation
- **State Management**: Zustand (lightweight alternative to Redux)
- **PDF Generation**: React-PDF or jsPDF
- **Authentication**: NextAuth.js
- **Deployment**: Vercel (optimized for Next.js)

#### Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with asyncpg
- **ORM**: SQLAlchemy 2.0+ (async)
- **Authentication**: JWT with bcrypt password hashing
- **Document Generation**: Jinja2 templates + WeasyPrint for PDF
- **File Storage**: AWS S3 or Google Cloud Storage
- **Task Queue**: Celery with Redis
- **Deployment**: Docker containers on AWS ECS or Google Cloud Run

#### External Integrations
- **Payment Processing**: Stripe API
- **Electronic Signatures**: DocuSign API
- **Email Service**: SendGrid or AWS SES
- **Analytics**: PostHog or Mixpanel
- **Error Tracking**: Sentry
- **Monitoring**: DataDog or New Relic

---

## 2. Database Schema Design

### 2.1 PostgreSQL Database Schema

```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(255),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user', -- 'user', 'admin', 'legal_partner'
    subscription_tier VARCHAR(20) DEFAULT 'free', -- 'free', 'starter', 'professional', 'enterprise'
    stripe_customer_id VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Subscription Management
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan_type VARCHAR(20) NOT NULL, -- 'starter', 'professional', 'enterprise'
    status VARCHAR(20) NOT NULL, -- 'active', 'canceled', 'past_due', 'trialing'
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- NDA Template Categories and Templates
CREATE TABLE template_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE nda_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES template_categories(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(20) NOT NULL, -- 'bilateral', 'unilateral', 'multilateral'
    jurisdiction VARCHAR(100) DEFAULT 'United States',
    industry_focus VARCHAR(100),
    complexity_level VARCHAR(20) DEFAULT 'standard', -- 'basic', 'standard', 'advanced'
    template_content JSONB NOT NULL, -- Template structure and fields
    legal_clauses JSONB, -- Predefined legal clauses
    required_fields JSONB NOT NULL, -- Field definitions and validation
    optional_fields JSONB,
    tier_requirement VARCHAR(20) DEFAULT 'starter', -- Minimum tier required
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id), -- Legal review
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Generated Documents
CREATE TABLE generated_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    template_id UUID REFERENCES nda_templates(id),
    document_name VARCHAR(255) NOT NULL,
    document_data JSONB NOT NULL, -- User responses and generated content
    pdf_file_path VARCHAR(500),
    docx_file_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'draft', -- 'draft', 'generated', 'signed', 'completed'

    -- Parties Information
    disclosing_party JSONB NOT NULL,
    receiving_party JSONB NOT NULL,
    additional_parties JSONB,

    -- Document Metadata
    effective_date DATE,
    expiration_date DATE,
    governing_law VARCHAR(100),

    -- Electronic Signature Integration
    docusign_envelope_id VARCHAR(255),
    signature_status VARCHAR(20), -- 'pending', 'signed', 'declined', 'expired'
    signed_at TIMESTAMP,

    -- Tracking
    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Document Signers
CREATE TABLE document_signers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES generated_documents(id) ON DELETE CASCADE,
    signer_name VARCHAR(255) NOT NULL,
    signer_email VARCHAR(255) NOT NULL,
    signer_role VARCHAR(100), -- 'Disclosing Party', 'Receiving Party', 'Witness'
    signature_status VARCHAR(20) DEFAULT 'pending',
    signed_at TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage Analytics and Billing
CREATE TABLE usage_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL, -- 'document_generated', 'template_used', 'signature_sent'
    resource_id UUID, -- Reference to document, template, etc.
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- API Keys (for Enterprise/Partner integrations)
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    key_name VARCHAR(100) NOT NULL,
    api_key_hash VARCHAR(255) NOT NULL,
    permissions JSONB NOT NULL, -- Array of permitted actions
    rate_limit INTEGER DEFAULT 1000, -- Requests per hour
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_generated_documents_user ON generated_documents(user_id);
CREATE INDEX idx_generated_documents_template ON generated_documents(template_id);
CREATE INDEX idx_generated_documents_status ON generated_documents(status);
CREATE INDEX idx_usage_tracking_user_date ON usage_tracking(user_id, created_at);
CREATE INDEX idx_audit_logs_user_date ON audit_logs(user_id, created_at);
```

### 2.2 Database Relationships
```
users (1) ←→ (M) subscriptions
users (1) ←→ (M) generated_documents
users (1) ←→ (M) usage_tracking
users (1) ←→ (M) api_keys

template_categories (1) ←→ (M) nda_templates
nda_templates (1) ←→ (M) generated_documents

generated_documents (1) ←→ (M) document_signers
```

---

## 3. Backend API Specification

### 3.1 FastAPI Application Structure
```
app/
├── main.py                 # FastAPI app initialization
├── config.py              # Configuration management
├── database.py            # Database connection and session management
├── dependencies.py        # Common dependencies (auth, db session)
├── middleware.py          # Custom middleware (CORS, logging, etc.)
├──
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── subscription.py
│   ├── template.py
│   ├── document.py
│   └── audit.py
├──
├── schemas/               # Pydantic schemas for request/response validation
│   ├── __init__.py
│   ├── user.py
│   ├── auth.py
│   ├── template.py
│   ├── document.py
│   └── common.py
├──
├── api/                   # API route handlers
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── templates.py
│   │   ├── documents.py
│   │   ├── subscriptions.py
│   │   └── analytics.py
│   └── webhooks/
│       ├── __init__.py
│       ├── stripe.py
│       └── docusign.py
├──
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   ├── template_service.py
│   ├── document_service.py
│   ├── pdf_generator.py
│   ├── email_service.py
│   └── signature_service.py
├──
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── security.py
│   ├── validators.py
│   ├── formatters.py
│   └── constants.py
├──
├── templates/             # Jinja2 templates for document generation
│   ├── nda/
│   │   ├── bilateral_basic.html
│   │   ├── bilateral_standard.html
│   │   ├── unilateral_basic.html
│   │   ├── multilateral.html
│   │   └── components/
│   │       ├── header.html
│   │       ├── signature_block.html
│   │       └── legal_clauses.html
│   └── email/
│       ├── welcome.html
│       ├── document_ready.html
│       └── signature_request.html
└──
└── tests/                 # Test suite
    ├── __init__.py
    ├── conftest.py
    ├── test_auth.py
    ├── test_templates.py
    ├── test_documents.py
    └── test_integrations.py
```

### 3.2 Core API Endpoints

#### Authentication Endpoints
```python
# auth.py
@router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db))

@router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db))

@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db))

@router.post("/auth/forgot-password")
async def forgot_password(email: EmailStr, db: AsyncSession = Depends(get_db))

@router.post("/auth/reset-password")
async def reset_password(reset_data: PasswordReset, db: AsyncSession = Depends(get_db))

@router.post("/auth/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db))
```

#### Template Management Endpoints
```python
# templates.py
@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    category: Optional[str] = None,
    industry: Optional[str] = None,
    complexity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.get("/templates/{template_id}", response_model=TemplateDetailResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.get("/template-categories", response_model=List[CategoryResponse])
async def get_categories(db: AsyncSession = Depends(get_db))

@router.post("/templates", response_model=TemplateResponse)
async def create_template(
    template_data: TemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
)
```

#### Document Generation Endpoints
```python
# documents.py
@router.post("/documents/generate", response_model=DocumentResponse)
async def generate_document(
    document_data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.get("/documents", response_model=List[DocumentResponse])
async def get_user_documents(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID,
    format: str = "pdf",  # pdf, docx
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.post("/documents/{document_id}/send-for-signature")
async def send_for_signature(
    document_id: UUID,
    signature_request: SignatureRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_update: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)
```

#### User Management Endpoints
```python
# users.py
@router.get("/users/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user))

@router.put("/users/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.get("/users/usage-stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)

@router.post("/users/upgrade-subscription")
async def upgrade_subscription(
    upgrade_data: SubscriptionUpgrade,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
)
```

### 3.3 Pydantic Schemas

#### User Schemas
```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    role: str
    subscription_tier: str
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
```

#### Template Schemas
```python
# schemas/template.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str  # bilateral, unilateral, multilateral
    jurisdiction: str = "United States"
    industry_focus: Optional[str] = None
    complexity_level: str = "standard"

class TemplateCreate(TemplateBase):
    category_id: UUID
    template_content: Dict[str, Any]
    legal_clauses: Optional[Dict[str, Any]] = None
    required_fields: Dict[str, Any]
    optional_fields: Optional[Dict[str, Any]] = None
    tier_requirement: str = "starter"

class TemplateResponse(TemplateBase):
    id: UUID
    category_id: UUID
    tier_requirement: str
    version: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TemplateDetailResponse(TemplateResponse):
    template_content: Dict[str, Any]
    legal_clauses: Optional[Dict[str, Any]]
    required_fields: Dict[str, Any]
    optional_fields: Optional[Dict[str, Any]]

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    slug: str
    sort_order: int

    class Config:
        from_attributes = True
```

#### Document Schemas
```python
# schemas/document.py
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, date

class PartyInfo(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    address: str
    email: str
    phone: Optional[str] = None

class DocumentBase(BaseModel):
    document_name: str
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    governing_law: str = "United States"

class DocumentCreate(DocumentBase):
    template_id: UUID
    disclosing_party: PartyInfo
    receiving_party: PartyInfo
    additional_parties: Optional[List[PartyInfo]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class DocumentUpdate(BaseModel):
    document_name: Optional[str] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    disclosing_party: Optional[PartyInfo] = None
    receiving_party: Optional[PartyInfo] = None

class DocumentResponse(DocumentBase):
    id: UUID
    user_id: UUID
    template_id: UUID
    status: str
    pdf_file_path: Optional[str]
    signature_status: Optional[str]
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SignerInfo(BaseModel):
    signer_name: str
    signer_email: str
    signer_role: str

class SignatureRequest(BaseModel):
    signers: List[SignerInfo]
    message: Optional[str] = None
    reminder_days: int = 3
```

---

## 4. Frontend Application Architecture

### 4.1 Next.js Application Structure
```
frontend/
├── app/                           # Next.js 14+ App Router
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Homepage
│   ├── globals.css               # Global styles
│   ├──
│   ├── (auth)/                   # Auth route group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   ├── forgot-password/
│   │   │   └── page.tsx
│   │   └── reset-password/
│   │       └── page.tsx
│   ├──
│   ├── dashboard/                # Protected dashboard routes
│   │   ├── layout.tsx           # Dashboard layout
│   │   ├── page.tsx             # Dashboard home
│   │   ├── documents/
│   │   │   ├── page.tsx         # Document list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx     # Document detail
│   │   │   └── new/
│   │   │       └── page.tsx     # Create new document
│   │   ├── templates/
│   │   │   ├── page.tsx         # Template browser
│   │   │   └── [id]/
│   │   │       └── page.tsx     # Template detail
│   │   ├── profile/
│   │   │   └── page.tsx         # User profile
│   │   └── billing/
│   │       └── page.tsx         # Subscription management
│   ├──
│   ├── generate/                 # Document generation flow
│   │   ├── [templateId]/
│   │   │   ├── page.tsx         # Template selection
│   │   │   ├── form/
│   │   │   │   └── page.tsx     # Document form
│   │   │   ├── preview/
│   │   │   │   └── page.tsx     # Document preview
│   │   │   └── complete/
│   │   │       └── page.tsx     # Generation complete
│   │   └── success/
│   │       └── page.tsx         # Success page
│   ├──
│   ├── api/                      # API routes (for NextAuth, webhooks)
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts
│   │   └── webhooks/
│   │       └── stripe/
│   │           └── route.ts
│   └──
│   └── pricing/
│       └── page.tsx              # Pricing page
├──
├── components/                   # Reusable UI components
│   ├── ui/                      # Base UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── form.tsx
│   │   ├── table.tsx
│   │   ├── badge.tsx
│   │   ├── toast.tsx
│   │   └── loading.tsx
│   ├──
│   ├── layout/                  # Layout components
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   ├── sidebar.tsx
│   │   └── navigation.tsx
│   ├──
│   ├── forms/                   # Form components
│   │   ├── document-form.tsx
│   │   ├── party-info-form.tsx
│   │   ├── template-selector.tsx
│   │   └── signature-form.tsx
│   ├──
│   ├── documents/               # Document-related components
│   │   ├── document-list.tsx
│   │   ├── document-card.tsx
│   │   ├── document-preview.tsx
│   │   ├── pdf-viewer.tsx
│   │   └── status-badge.tsx
│   ├──
│   ├── templates/               # Template components
│   │   ├── template-grid.tsx
│   │   ├── template-card.tsx
│   │   ├── category-filter.tsx
│   │   └── template-preview.tsx
│   └──
│   └── dashboard/               # Dashboard components
│       ├── stats-cards.tsx
│       ├── recent-documents.tsx
│       ├── usage-chart.tsx
│       └── quick-actions.tsx
├──
├── lib/                         # Utility libraries
│   ├── api.ts                  # API client
│   ├── auth.ts                 # NextAuth configuration
│   ├── utils.ts                # Utility functions
│   ├── constants.ts            # App constants
│   ├── validations.ts          # Form validation schemas
│   └── types.ts                # TypeScript type definitions
├──
├── hooks/                       # Custom React hooks
│   ├── use-api.ts              # API interaction hooks
│   ├── use-auth.ts             # Authentication hooks
│   ├── use-documents.ts        # Document management hooks
│   ├── use-templates.ts        # Template hooks
│   └── use-subscription.ts     # Subscription hooks
├──
├── store/                       # State management (Zustand)
│   ├── auth-store.ts
│   ├── document-store.ts
│   ├── template-store.ts
│   └── ui-store.ts
├──
├── styles/                      # Additional styles
│   └── components.css
├──
├── public/                      # Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
├──
├── middleware.ts                # Next.js middleware
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies
```

### 4.2 Key Frontend Components

#### Document Generation Form Component
```typescript
// components/forms/document-form.tsx
'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { PartyInfoForm } from './party-info-form'

const documentSchema = z.object({
  documentName: z.string().min(1, 'Document name is required'),
  effectiveDate: z.string().optional(),
  expirationDate: z.string().optional(),
  governingLaw: z.string().default('United States'),
  disclosingParty: z.object({
    name: z.string().min(1, 'Name is required'),
    title: z.string().optional(),
    company: z.string().optional(),
    address: z.string().min(1, 'Address is required'),
    email: z.string().email('Invalid email'),
    phone: z.string().optional()
  }),
  receivingParty: z.object({
    name: z.string().min(1, 'Name is required'),
    title: z.string().optional(),
    company: z.string().optional(),
    address: z.string().min(1, 'Address is required'),
    email: z.string().email('Invalid email'),
    phone: z.string().optional()
  }),
  customFields: z.record(z.any()).optional()
})

type DocumentFormData = z.infer<typeof documentSchema>

interface DocumentFormProps {
  templateId: string
  onSubmit: (data: DocumentFormData) => void
  isLoading?: boolean
}

export function DocumentForm({ templateId, onSubmit, isLoading }: DocumentFormProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const totalSteps = 4

  const {
    register,
    handleSubmit,
    watch,
    control,
    formState: { errors, isValid }
  } = useForm<DocumentFormData>({
    resolver: zodResolver(documentSchema),
    mode: 'onChange'
  })

  const watchedData = watch()

  const nextStep = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleFormSubmit = (data: DocumentFormData) => {
    onSubmit(data)
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Document Information</h3>
            <div className="space-y-4">
              <Input
                {...register('documentName')}
                placeholder="Enter document name"
                label="Document Name"
                error={errors.documentName?.message}
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  {...register('effectiveDate')}
                  type="date"
                  label="Effective Date (Optional)"
                  error={errors.effectiveDate?.message}
                />
                <Input
                  {...register('expirationDate')}
                  type="date"
                  label="Expiration Date (Optional)"
                  error={errors.expirationDate?.message}
                />
              </div>
              <Input
                {...register('governingLaw')}
                placeholder="United States"
                label="Governing Law"
                error={errors.governingLaw?.message}
              />
            </div>
          </Card>
        )
      case 2:
        return (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Disclosing Party Information</h3>
            <PartyInfoForm
              namePrefix="disclosingParty"
              register={register}
              errors={errors.disclosingParty}
            />
          </Card>
        )
      case 3:
        return (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Receiving Party Information</h3>
            <PartyInfoForm
              namePrefix="receivingParty"
              register={register}
              errors={errors.receivingParty}
            />
          </Card>
        )
      case 4:
        return (
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Review & Generate</h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium">Document: {watchedData.documentName}</h4>
                <p className="text-sm text-gray-600">
                  Between {watchedData.disclosingParty?.name} and {watchedData.receivingParty?.name}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm">
                  By clicking "Generate Document", you agree to our terms of service and
                  acknowledge that this document is for informational purposes only.
                </p>
              </div>
            </div>
          </Card>
        )
      default:
        return null
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Step {currentStep} of {totalSteps}</span>
          <span className="text-sm text-gray-500">{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentStep / totalSteps) * 100}%` }}
          />
        </div>
      </div>

      <form onSubmit={handleSubmit(handleFormSubmit)}>
        {renderStep()}

        {/* Navigation Buttons */}
        <div className="flex justify-between mt-6">
          <Button
            type="button"
            variant="outline"
            onClick={prevStep}
            disabled={currentStep === 1}
          >
            Previous
          </Button>

          {currentStep < totalSteps ? (
            <Button type="button" onClick={nextStep}>
              Next
            </Button>
          ) : (
            <Button type="submit" disabled={!isValid || isLoading}>
              {isLoading ? 'Generating...' : 'Generate Document'}
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}
```

#### PDF Preview Component
```typescript
// components/documents/pdf-viewer.tsx
'use client'

import { useState, useEffect } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { Button } from '@/components/ui/button'
import { ZoomIn, ZoomOut, Download, Share } from 'lucide-react'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

interface PDFViewerProps {
  pdfUrl: string
  documentId: string
  onDownload?: () => void
  onShare?: () => void
}

export function PDFViewer({ pdfUrl, documentId, onDownload, onShare }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.0)
  const [loading, setLoading] = useState<boolean>(true)

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setLoading(false)
  }

  const goToPrevPage = () => setPageNumber(pageNumber - 1)
  const goToNextPage = () => setPageNumber(pageNumber + 1)
  const zoomIn = () => setScale(scale * 1.2)
  const zoomOut = () => setScale(scale / 1.2)

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b bg-gray-50">
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm" onClick={zoomOut} disabled={scale <= 0.5}>
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm font-medium">{Math.round(scale * 100)}%</span>
          <Button variant="outline" size="sm" onClick={zoomIn} disabled={scale >= 3}>
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-sm">
            Page {pageNumber} of {numPages}
          </span>
          <Button variant="outline" size="sm" onClick={goToPrevPage} disabled={pageNumber <= 1}>
            Previous
          </Button>
          <Button variant="outline" size="sm" onClick={goToNextPage} disabled={pageNumber >= numPages}>
            Next
          </Button>
        </div>

        <div className="flex items-center space-x-2">
          {onDownload && (
            <Button variant="outline" size="sm" onClick={onDownload}>
              <Download className="h-4 w-4 mr-1" />
              Download
            </Button>
          )}
          {onShare && (
            <Button variant="outline" size="sm" onClick={onShare}>
              <Share className="h-4 w-4 mr-1" />
              Share
            </Button>
          )}
        </div>
      </div>

      {/* PDF Display */}
      <div className="flex-1 overflow-auto bg-gray-100 p-4">
        <div className="flex justify-center">
          {loading && (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}
          <Document
            file={pdfUrl}
            onLoadSuccess={onDocumentLoadSuccess}
            loading={null}
            className="shadow-lg"
          >
            <Page
              pageNumber={pageNumber}
              scale={scale}
              className="border border-gray-300"
            />
          </Document>
        </div>
      </div>
    </div>
  )
}
```

### 4.3 State Management (Zustand)

#### Authentication Store
```typescript
// store/auth-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  companyName?: string
  role: string
  subscriptionTier: string
  emailVerified: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  login: (tokens: { accessToken: string; refreshToken: string }, user: User) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: (tokens, user) => {
        set({
          user,
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
          isAuthenticated: true,
          isLoading: false
        })
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false
        })
      },

      updateUser: (userData) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData }
          })
        }
      },

      setLoading: (loading) => {
        set({ isLoading: loading })
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)
```

#### Document Store
```typescript
// store/document-store.ts
import { create } from 'zustand'

interface Document {
  id: string
  templateId: string
  documentName: string
  status: string
  pdfFilePath?: string
  signatureStatus?: string
  createdAt: string
  updatedAt: string
}

interface DocumentState {
  documents: Document[]
  currentDocument: Document | null
  isLoading: boolean
  error: string | null

  // Actions
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  updateDocument: (id: string, updates: Partial<Document>) => void
  setCurrentDocument: (document: Document | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  currentDocument: null,
  isLoading: false,
  error: null,

  setDocuments: (documents) => set({ documents }),

  addDocument: (document) => {
    const { documents } = get()
    set({ documents: [document, ...documents] })
  },

  updateDocument: (id, updates) => {
    const { documents } = get()
    const updatedDocuments = documents.map(doc =>
      doc.id === id ? { ...doc, ...updates } : doc
    )
    set({ documents: updatedDocuments })
  },

  setCurrentDocument: (document) => set({ currentDocument: document }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error })
}))
```

### 4.4 API Client
```typescript
// lib/api.ts
import axios, { AxiosResponse, AxiosError } from 'axios'
import { useAuthStore } from '@/store/auth-store'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const { refreshToken } = useAuthStore.getState()
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          })

          const { access_token } = response.data
          useAuthStore.getState().login({
            accessToken: access_token,
            refreshToken
          }, useAuthStore.getState().user!)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// API functions
export const api = {
  // Authentication
  auth: {
    login: (email: string, password: string) =>
      apiClient.post('/auth/login', { email, password }),
    register: (userData: any) =>
      apiClient.post('/auth/register', userData),
    forgotPassword: (email: string) =>
      apiClient.post('/auth/forgot-password', { email }),
    resetPassword: (token: string, password: string) =>
      apiClient.post('/auth/reset-password', { token, password }),
    verifyEmail: (token: string) =>
      apiClient.post('/auth/verify-email', { token })
  },

  // Templates
  templates: {
    getAll: (params?: any) =>
      apiClient.get('/templates', { params }),
    getById: (id: string) =>
      apiClient.get(`/templates/${id}`),
    getCategories: () =>
      apiClient.get('/template-categories')
  },

  // Documents
  documents: {
    generate: (documentData: any) =>
      apiClient.post('/documents/generate', documentData),
    getAll: (params?: any) =>
      apiClient.get('/documents', { params }),
    getById: (id: string) =>
      apiClient.get(`/documents/${id}`),
    update: (id: string, updates: any) =>
      apiClient.put(`/documents/${id}`, updates),
    delete: (id: string) =>
      apiClient.delete(`/documents/${id}`),
    download: (id: string, format = 'pdf') =>
      apiClient.get(`/documents/${id}/download?format=${format}`, {
        responseType: 'blob'
      }),
    sendForSignature: (id: string, signatureRequest: any) =>
      apiClient.post(`/documents/${id}/send-for-signature`, signatureRequest)
  },

  // Users
  users: {
    getProfile: () =>
      apiClient.get('/users/profile'),
    updateProfile: (userData: any) =>
      apiClient.put('/users/profile', userData),
    getUsageStats: () =>
      apiClient.get('/users/usage-stats'),
    upgradeSubscription: (planData: any) =>
      apiClient.post('/users/upgrade-subscription', planData)
  }
}

export default apiClient
```

---

## 5. Document Generation Engine

### 5.1 PDF Generation Service
```python
# services/pdf_generator.py
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import uuid
import os

class PDFGenerator:
    def __init__(self, templates_dir: str = "app/templates"):
        self.templates_dir = Path(templates_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        self.font_config = FontConfiguration()

    async def generate_nda_pdf(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate PDF from NDA template and context data
        """
        try:
            # Load and render HTML template
            template = self.jinja_env.get_template(f"nda/{template_name}.html")
            html_content = template.render(**context)

            # Generate unique filename if not provided
            if not output_path:
                file_id = str(uuid.uuid4())
                output_path = f"generated_documents/{file_id}.pdf"

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # CSS for PDF styling
            css_content = """
            @page {
                size: letter;
                margin: 1in;
                @top-center {
                    content: "CONFIDENTIAL - NON-DISCLOSURE AGREEMENT";
                    font-size: 10px;
                    color: #666;
                }
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10px;
                    color: #666;
                }
            }

            body {
                font-family: 'Times New Roman', serif;
                font-size: 12px;
                line-height: 1.6;
                color: #000;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #000;
                padding-bottom: 10px;
            }

            .title {
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 10px;
            }

            .parties {
                margin-bottom: 20px;
            }

            .party-info {
                margin-bottom: 15px;
                padding: 10px;
                border-left: 3px solid #333;
                background-color: #f9f9f9;
            }

            .clause {
                margin-bottom: 20px;
            }

            .clause-title {
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 10px;
                text-decoration: underline;
            }

            .signature-block {
                margin-top: 40px;
                page-break-inside: avoid;
            }

            .signature-line {
                border-bottom: 1px solid #000;
                width: 300px;
                margin: 20px 0 5px 0;
            }

            .signature-info {
                font-size: 10px;
                margin-bottom: 30px;
            }

            .legal-notice {
                font-size: 10px;
                color: #666;
                border-top: 1px solid #ccc;
                padding-top: 10px;
                margin-top: 30px;
            }
            """

            # Generate PDF
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=css_content, font_config=self.font_config)

            # Write PDF to file
            html_doc.write_pdf(output_path, stylesheets=[css_doc])

            return output_path

        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")

    def _format_party_info(self, party: Dict[str, Any]) -> Dict[str, str]:
        """Format party information for template rendering"""
        formatted = {
            'name': party.get('name', ''),
            'title': party.get('title', ''),
            'company': party.get('company', ''),
            'address': party.get('address', ''),
            'email': party.get('email', ''),
            'phone': party.get('phone', '')
        }

        # Create formatted address block
        address_parts = []
        if formatted['company']:
            address_parts.append(formatted['company'])
        if formatted['address']:
            address_parts.append(formatted['address'])

        formatted['address_block'] = '\n'.join(address_parts)

        # Create signature line with name and title
        signature_line = formatted['name']
        if formatted['title']:
            signature_line += f", {formatted['title']}"
        formatted['signature_line'] = signature_line

        return formatted

    async def generate_docx(
        self,
        template_name: str,
        context: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate DOCX from template (for editing)
        """
        # This would use python-docx library for DOCX generation
        # Implementation would be similar to PDF but using docx templates
        pass
```

### 5.2 NDA Template Examples
```html
<!-- templates/nda/bilateral_standard.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bilateral Non-Disclosure Agreement</title>
</head>
<body>
    <div class="header">
        <div class="title">Mutual Non-Disclosure Agreement</div>
        <div class="subtitle">Confidential Information Exchange Agreement</div>
    </div>

    <div class="parties">
        <p><strong>This Mutual Non-Disclosure Agreement</strong> ("Agreement") is entered into on
        <strong>{{ effective_date or "_____________" }}</strong> by and between:</p>

        <div class="party-info">
            <strong>First Party ("Disclosing/Receiving Party"):</strong><br>
            {{ disclosing_party.name }}<br>
            {% if disclosing_party.title %}{{ disclosing_party.title }}<br>{% endif %}
            {% if disclosing_party.company %}{{ disclosing_party.company }}<br>{% endif %}
            {{ disclosing_party.address }}<br>
            Email: {{ disclosing_party.email }}<br>
            {% if disclosing_party.phone %}Phone: {{ disclosing_party.phone }}{% endif %}
        </div>

        <div class="party-info">
            <strong>Second Party ("Receiving/Disclosing Party"):</strong><br>
            {{ receiving_party.name }}<br>
            {% if receiving_party.title %}{{ receiving_party.title }}<br>{% endif %}
            {% if receiving_party.company %}{{ receiving_party.company }}<br>{% endif %}
            {{ receiving_party.address }}<br>
            Email: {{ receiving_party.email }}<br>
            {% if receiving_party.phone %}Phone: {{ receiving_party.phone }}{% endif %}
        </div>
    </div>

    <div class="preamble">
        <p><strong>WHEREAS,</strong> both parties wish to explore potential business opportunities
        that may be of mutual benefit and interest;</p>

        <p><strong>WHEREAS,</strong> in connection with such discussions, each party may disclose
        to the other certain confidential and proprietary information;</p>

        <p><strong>NOW, THEREFORE,</strong> in consideration of the mutual covenants contained herein
        and for other good and valuable consideration, the parties agree as follows:</p>
    </div>

    <div class="clause">
        <div class="clause-title">1. DEFINITION OF CONFIDENTIAL INFORMATION</div>
        <p>For purposes of this Agreement, "Confidential Information" means any and all non-public,
        confidential or proprietary information disclosed by either party (the "Disclosing Party")
        to the other party (the "Receiving Party"), whether orally, in writing, or in any other form,
        including but not limited to:</p>
        <ul>
            <li>Technical data, trade secrets, know-how, research, product plans, products, services, customers</li>
            <li>Customer lists, markets, software, developments, inventions, processes, formulas</li>
            <li>Technology, designs, drawings, engineering, hardware configuration information</li>
            <li>Marketing strategies, finances, or other business information</li>
        </ul>
    </div>

    <div class="clause">
        <div class="clause-title">2. OBLIGATIONS OF RECEIVING PARTY</div>
        <p>The Receiving Party agrees to:</p>
        <ul>
            <li>Hold all Confidential Information in strict confidence</li>
            <li>Not disclose Confidential Information to any third parties without prior written consent</li>
            <li>Use Confidential Information solely for the purpose of evaluating potential business opportunities</li>
            <li>Take reasonable precautions to protect the confidentiality of such information</li>
        </ul>
    </div>

    <div class="clause">
        <div class="clause-title">3. EXCEPTIONS</div>
        <p>The obligations set forth in Section 2 shall not apply to information that:</p>
        <ul>
            <li>Is or becomes publicly available through no breach of this Agreement</li>
            <li>Is rightfully known by the Receiving Party prior to disclosure</li>
            <li>Is rightfully obtained by the Receiving Party from a third party without breach of any confidentiality obligation</li>
            <li>Is independently developed by the Receiving Party without use of or reference to Confidential Information</li>
        </ul>
    </div>

    <div class="clause">
        <div class="clause-title">4. TERM</div>
        <p>This Agreement shall remain in effect for a period of
        {% if expiration_date %}
            until {{ expiration_date }}
        {% else %}
            three (3) years from the date first written above
        {% endif %}
        , unless terminated earlier by mutual written consent of the parties.</p>
    </div>

    <div class="clause">
        <div class="clause-title">5. RETURN OF INFORMATION</div>
        <p>Upon termination of this Agreement or upon written request, each party shall promptly
        return or destroy all documents, materials, and other tangible manifestations of
        Confidential Information received from the other party.</p>
    </div>

    <div class="clause">
        <div class="clause-title">6. GOVERNING LAW</div>
        <p>This Agreement shall be governed by and construed in accordance with the laws of
        {{ governing_law or "the State of Delaware, United States" }}.</p>
    </div>

    <div class="clause">
        <div class="clause-title">7. ENTIRE AGREEMENT</div>
        <p>This Agreement constitutes the entire agreement between the parties concerning the
        subject matter hereof and supersedes all prior agreements, whether written or oral,
        relating to such subject matter.</p>
    </div>

    <div class="signature-block">
        <div style="display: flex; justify-content: space-between;">
            <div style="width: 45%;">
                <strong>FIRST PARTY:</strong><br><br>
                <div class="signature-line"></div>
                <div class="signature-info">
                    {{ disclosing_party.name }}<br>
                    {% if disclosing_party.title %}{{ disclosing_party.title }}<br>{% endif %}
                    Date: _______________
                </div>
            </div>

            <div style="width: 45%;">
                <strong>SECOND PARTY:</strong><br><br>
                <div class="signature-line"></div>
                <div class="signature-info">
                    {{ receiving_party.name }}<br>
                    {% if receiving_party.title %}{{ receiving_party.title }}<br>{% endif %}
                    Date: _______________
                </div>
            </div>
        </div>
    </div>

    <div class="legal-notice">
        <p><em>This document was generated by NDARite. This template is provided for informational
        purposes only and does not constitute legal advice. Please consult with a qualified attorney
        for legal guidance specific to your situation.</em></p>
    </div>
</body>
</html>
```

---

## 6. External Integrations

### 6.1 DocuSign Integration
```python
# services/signature_service.py
import asyncio
from typing import List, Dict, Any
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition
from docusign_esign.client.api_exception import ApiException
import base64

class DocuSignService:
    def __init__(self, access_token: str, account_id: str, base_path: str):
        self.access_token = access_token
        self.account_id = account_id
        self.api_client = ApiClient()
        self.api_client.host = base_path
        self.api_client.set_default_header("Authorization", f"Bearer {access_token}")

    async def send_envelope(
        self,
        document_path: str,
        document_name: str,
        signers: List[Dict[str, str]],
        email_subject: str = "Please sign this document",
        email_body: str = "Please review and sign the attached NDA."
    ) -> str:
        """
        Send document for electronic signature via DocuSign

        Args:
            document_path: Path to PDF document
            document_name: Name of the document
            signers: List of signer information
            email_subject: Email subject line
            email_body: Email body content

        Returns:
            Envelope ID from DocuSign
        """
        try:
            # Read document content
            with open(document_path, 'rb') as file:
                document_content = file.read()

            # Encode document as base64
            document_base64 = base64.b64encode(document_content).decode('utf-8')

            # Create document object
            document = {
                "documentBase64": document_base64,
                "name": document_name,
                "fileExtension": "pdf",
                "documentId": "1"
            }

            # Create signer objects
            envelope_signers = []
            for idx, signer in enumerate(signers, 1):
                envelope_signer = {
                    "email": signer['email'],
                    "name": signer['name'],
                    "recipientId": str(idx),
                    "routingOrder": str(idx)
                }
                envelope_signers.append(envelope_signer)

            # Create envelope definition
            envelope_definition = {
                "emailSubject": email_subject,
                "emailBlurb": email_body,
                "documents": [document],
                "recipients": {
                    "signers": envelope_signers
                },
                "status": "sent"
            }

            # Send envelope
            envelopes_api = EnvelopesApi(self.api_client)
            results = envelopes_api.create_envelope(
                self.account_id,
                envelope_definition=envelope_definition
            )

            return results.envelope_id

        except ApiException as e:
            raise Exception(f"DocuSign API error: {e}")
        except Exception as e:
            raise Exception(f"Signature service error: {str(e)}")

    async def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get the current status of an envelope"""
        try:
            envelopes_api = EnvelopesApi(self.api_client)
            envelope = envelopes_api.get_envelope(self.account_id, envelope_id)

            return {
                "envelope_id": envelope.envelope_id,
                "status": envelope.status,
                "created_date": envelope.created_date_time,
                "completed_date": envelope.completed_date_time,
                "status_changed_date": envelope.status_changed_date_time
            }
        except ApiException as e:
            raise Exception(f"DocuSign API error: {e}")
```

### 6.2 Stripe Payment Integration
```python
# services/payment_service.py
import stripe
from typing import Dict, Any, Optional
from decimal import Decimal

class StripePaymentService:
    def __init__(self, api_key: str):
        stripe.api_key = api_key

    async def create_customer(
        self,
        email: str,
        name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_period_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a new subscription"""
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"]
            }

            if trial_period_days:
                subscription_data["trial_period_days"] = trial_period_days

            subscription = stripe.Subscription.create(**subscription_data)

            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def create_payment_intent(
        self,
        amount: int,  # Amount in cents
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a payment intent for one-time payments"""
        try:
            intent_data = {
                "amount": amount,
                "currency": currency,
                "metadata": metadata or {}
            }

            if customer_id:
                intent_data["customer"] = customer_id

            intent = stripe.PaymentIntent.create(**intent_data)

            return {
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    async def handle_webhook(self, payload: str, sig_header: str, endpoint_secret: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )

            return {
                "event_type": event["type"],
                "event_data": event["data"]["object"],
                "event_id": event["id"]
            }
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")
```

---

## 7. Deployment & Infrastructure

### 7.1 Docker Configuration

#### Backend Dockerfile
```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        libcairo2-dev \
        libpango1.0-dev \
        libgdk-pixbuf2.0-dev \
        libffi-dev \
        shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create directories for file storage
RUN mkdir -p /app/generated_documents /app/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
# Dockerfile.frontend
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build application
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ndarite
      POSTGRES_USER: ndarite_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ndarite_user -d ndarite"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Redis for caching and task queue
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql://ndarite_user:${POSTGRES_PASSWORD}@db:5432/ndarite
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - DOCUSIGN_CLIENT_ID=${DOCUSIGN_CLIENT_ID}
      - DOCUSIGN_CLIENT_SECRET=${DOCUSIGN_CLIENT_SECRET}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_S3_BUCKET=${AWS_S3_BUCKET}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/generated_documents:/app/generated_documents
      - ./backend/uploads:/app/uploads
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Celery Worker
  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://ndarite_user:${POSTGRES_PASSWORD}@db:5432/ndarite
      - REDIS_URL=redis://redis:6379
      - SECRET_KEY=${SECRET_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - DOCUSIGN_CLIENT_ID=${DOCUSIGN_CLIENT_ID}
      - DOCUSIGN_CLIENT_SECRET=${DOCUSIGN_CLIENT_SECRET}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/generated_documents:/app/generated_documents

  # Frontend Application
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=http://localhost:3000
    ports:
      - "3000:3000"
    depends_on:
      backend:
        condition: service_healthy

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 7.2 Kubernetes Deployment (Production)
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ndarite-prod

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ndarite-config
  namespace: ndarite-prod
data:
  POSTGRES_DB: "ndarite"
  POSTGRES_USER: "ndarite_user"
  REDIS_URL: "redis://redis:6379"
  NEXT_PUBLIC_API_URL: "https://api.ndarite.com/api/v1"

---
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ndarite-secrets
  namespace: ndarite-prod
type: Opaque
data:
  postgres-password: <base64-encoded-password>
  secret-key: <base64-encoded-secret>
  stripe-secret-key: <base64-encoded-stripe-key>
  docusign-client-id: <base64-encoded-docusign-id>
  docusign-client-secret: <base64-encoded-docusign-secret>

---
# k8s/postgresql.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: ndarite-prod
spec:
  serviceName: postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: ndarite-config
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            configMapKeyRef:
              name: ndarite-config
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ndarite-secrets
              key: postgres-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgresql-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgresql-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi

---
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ndarite-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ndarite/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgresql:5432/$(POSTGRES_DB)"
        - name: POSTGRES_USER
          valueFrom:
            configMapKeyRef:
              name: ndarite-config
              key: POSTGRES_USER
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: ndarite-config
              key: POSTGRES_DB
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ndarite-secrets
              key: postgres-password
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ndarite-secrets
              key: secret-key
        - name: STRIPE_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ndarite-secrets
              key: stripe-secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ndarite-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: ndarite/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: ndarite-config
              key: NEXT_PUBLIC_API_URL
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 8. Testing Strategy

### 8.1 Backend Testing
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base
from app.config import get_settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost/test_ndarite"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

@pytest.fixture
async def test_client(test_session):
    """Create test client with database dependency override."""
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(test_session):
    """Create test user."""
    from app.services.user_service import UserService

    user_service = UserService(test_session)
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User"
    }

    user = await user_service.create_user(user_data)
    return user

@pytest.fixture
async def auth_headers(test_client, test_user):
    """Create authentication headers for test requests."""
    login_response = await test_client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "testpassword123"
    })

    token_data = login_response.json()
    return {"Authorization": f"Bearer {token_data['access_token']}"}
```

```python
# tests/test_document_generation.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_generate_document_success(test_client: AsyncClient, auth_headers: dict):
    """Test successful document generation."""
    document_data = {
        "template_id": "123e4567-e89b-12d3-a456-426614174000",
        "document_name": "Test NDA Agreement",
        "disclosing_party": {
            "name": "John Doe",
            "title": "CEO",
            "company": "Test Company Inc.",
            "address": "123 Main St, Test City, TC 12345",
            "email": "john@testcompany.com"
        },
        "receiving_party": {
            "name": "Jane Smith",
            "title": "CTO",
            "company": "Another Company LLC",
            "address": "456 Oak Ave, Another City, AC 67890",
            "email": "jane@anothercompany.com"
        },
        "effective_date": "2024-01-15",
        "governing_law": "Delaware, United States"
    }

    response = await test_client.post(
        "/api/v1/documents/generate",
        json=document_data,
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.json()
    assert result["document_name"] == "Test NDA Agreement"
    assert result["status"] == "generated"
    assert "pdf_file_path" in result

@pytest.mark.asyncio
async def test_generate_document_invalid_template(test_client: AsyncClient, auth_headers: dict):
    """Test document generation with invalid template ID."""
    document_data = {
        "template_id": "invalid-template-id",
        "document_name": "Test NDA",
        "disclosing_party": {"name": "Test", "email": "test@test.com", "address": "123 Test St"},
        "receiving_party": {"name": "Test2", "email": "test2@test.com", "address": "456 Test Ave"}
    }

    response = await test_client.post(
        "/api/v1/documents/generate",
        json=document_data,
        headers=auth_headers
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_generate_document_missing_fields(test_client: AsyncClient, auth_headers: dict):
    """Test document generation with missing required fields."""
    document_data = {
        "template_id": "123e4567-e89b-12d3-a456-426614174000",
        "document_name": "Test NDA",
        # Missing required party information
    }

    response = await test_client.post(
        "/api/v1/documents/generate",
        json=document_data,
        headers=auth_headers
    )

    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_get_user_documents(test_client: AsyncClient, auth_headers: dict):
    """Test retrieving user's documents."""
    response = await test_client.get(
        "/api/v1/documents",
        headers=auth_headers
    )

    assert response.status_code == 200

    result = response.json()
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_download_document(test_client: AsyncClient, auth_headers: dict):
    """Test document download functionality."""
    # First create a document
    document_data = {
        "template_id": "123e4567-e89b-12d3-a456-426614174000",
        "document_name": "Download Test NDA",
        "disclosing_party": {
            "name": "Download Test",
            "email": "download@test.com",
            "address": "123 Download St"
        },
        "receiving_party": {
            "name": "Download Test 2",
            "email": "download2@test.com",
            "address": "456 Download Ave"
        }
    }

    create_response = await test_client.post(
        "/api/v1/documents/generate",
        json=document_data,
        headers=auth_headers
    )

    document = create_response.json()
    document_id = document["id"]

    # Test PDF download
    download_response = await test_client.get(
        f"/api/v1/documents/{document_id}/download?format=pdf",
        headers=auth_headers
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
```

### 8.2 Frontend Testing
```typescript
// __tests__/components/DocumentForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DocumentForm } from '@/components/forms/document-form'
import '@testing-library/jest-dom'

// Mock API calls
jest.mock('@/lib/api', () => ({
  api: {
    templates: {
      getById: jest.fn(() => Promise.resolve({
        data: {
          id: 'test-template-id',
          name: 'Test Template',
          required_fields: {}
        }
      }))
    }
  }
}))

describe('DocumentForm', () => {
  const mockOnSubmit = jest.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  it('renders document form with all steps', () => {
    render(
      <DocumentForm
        templateId="test-template-id"
        onSubmit={mockOnSubmit}
      />
    )

    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument()
    expect(screen.getByText('Document Information')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter document name')).toBeInTheDocument()
  })

  it('advances to next step when Next button is clicked', async () => {
    const user = userEvent.setup()

    render(
      <DocumentForm
        templateId="test-template-id"
        onSubmit={mockOnSubmit}
      />
    )

    // Fill required field
    await user.type(
      screen.getByPlaceholderText('Enter document name'),
      'Test Document'
    )

    // Click next
    await user.click(screen.getByText('Next'))

    await waitFor(() => {
      expect(screen.getByText('Step 2 of 4')).toBeInTheDocument()
      expect(screen.getByText('Disclosing Party Information')).toBeInTheDocument()
    })
  })

  it('validates required fields before submission', async () => {
    const user = userEvent.setup()

    render(
      <DocumentForm
        templateId="test-template-id"
        onSubmit={mockOnSubmit}
      />
    )

    // Try to advance without filling required fields
    await user.click(screen.getByText('Next'))

    // Should still be on step 1
    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument()
  })

  it('calls onSubmit with correct data when form is completed', async () => {
    const user = userEvent.setup()

    render(
      <DocumentForm
        templateId="test-template-id"
        onSubmit={mockOnSubmit}
      />
    )

    // Fill out step 1
    await user.type(
      screen.getByPlaceholderText('Enter document name'),
      'Test NDA Document'
    )
    await user.click(screen.getByText('Next'))

    // Fill out step 2 (disclosing party)
    await user.type(screen.getByPlaceholderText('Full Name'), 'John Doe')
    await user.type(screen.getByPlaceholderText('Email Address'), 'john@example.com')
    await user.type(screen.getByPlaceholderText('Address'), '123 Main St')
    await user.click(screen.getByText('Next'))

    // Fill out step 3 (receiving party)
    await user.type(screen.getByPlaceholderText('Full Name'), 'Jane Smith')
    await user.type(screen.getByPlaceholderText('Email Address'), 'jane@example.com')
    await user.type(screen.getByPlaceholderText('Address'), '456 Oak Ave')
    await user.click(screen.getByText('Next'))

    // Submit form
    await user.click(screen.getByText('Generate Document'))

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          documentName: 'Test NDA Document',
          disclosingParty: expect.objectContaining({
            name: 'John Doe',
            email: 'john@example.com',
            address: '123 Main St'
          }),
          receivingParty: expect.objectContaining({
            name: 'Jane Smith',
            email: 'jane@example.com',
            address: '456 Oak Ave'
          })
        })
      )
    })
  })
})
```

### 8.3 Integration Tests
```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
import tempfile
import os

@pytest.mark.asyncio
async def test_full_document_generation_workflow(test_client: AsyncClient, auth_headers: dict):
    """Test complete document generation workflow from template selection to PDF creation."""

    # 1. Get available templates
    templates_response = await test_client.get(
        "/api/v1/templates",
        headers=auth_headers
    )
    assert templates_response.status_code == 200
    templates = templates_response.json()
    assert len(templates) > 0

    template_id = templates[0]["id"]

    # 2. Generate document
    document_data = {
        "template_id": template_id,
        "document_name": "Integration Test NDA",
        "disclosing_party": {
            "name": "Integration Test Corp",
            "title": "CEO",
            "company": "Test Company",
            "address": "123 Integration St, Test City, TC 12345",
            "email": "ceo@integrationtest.com",
            "phone": "+1-555-0123"
        },
        "receiving_party": {
            "name": "Partner Company Inc",
            "title": "CTO",
            "company": "Partner Corp",
            "address": "456 Partner Ave, Partner City, PC 67890",
            "email": "cto@partner.com",
            "phone": "+1-555-0456"
        },
        "effective_date": "2024-02-01",
        "expiration_date": "2027-02-01",
        "governing_law": "California, United States"
    }

    generate_response = await test_client.post(
        "/api/v1/documents/generate",
        json=document_data,
        headers=auth_headers
    )
    assert generate_response.status_code == 200

    document = generate_response.json()
    document_id = document["id"]
    assert document["status"] == "generated"
    assert document["pdf_file_path"] is not None

    # 3. Retrieve generated document
    get_response = await test_client.get(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200

    retrieved_document = get_response.json()
    assert retrieved_document["id"] == document_id
    assert retrieved_document["document_name"] == "Integration Test NDA"

    # 4. Download PDF
    download_response = await test_client.get(
        f"/api/v1/documents/{document_id}/download",
        headers=auth_headers
    )
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert len(download_response.content) > 0

    # 5. Update document
    update_data = {
        "document_name": "Updated Integration Test NDA"
    }
    update_response = await test_client.put(
        f"/api/v1/documents/{document_id}",
        json=update_data,
        headers=auth_headers
    )
    assert update_response.status_code == 200

    updated_document = update_response.json()
    assert updated_document["document_name"] == "Updated Integration Test NDA"

@pytest.mark.asyncio
async def test_signature_workflow(test_client: AsyncClient, auth_headers: dict):
    """Test electronic signature workflow."""

    # First generate a document
    document_data = {
        "template_id": "test-template-id",
        "document_name": "Signature Test NDA",
        "disclosing_party": {
            "name": "Signature Test",
            "email": "signature@test.com",
            "address": "123 Signature St"
        },
        "receiving_party": {
            "name": "Signature Recipient",
            "email": "recipient@test.com",
            "address": "456 Recipient Ave"
        }
    }

    generate_response = await test_client.post(
        "/api/v1/documents/generate",
        json=document_data,
        headers=auth_headers
    )
    document = generate_response.json()
    document_id = document["id"]

    # Send for signature
    signature_request = {
        "signers": [
            {
                "signer_name": "Signature Test",
                "signer_email": "signature@test.com",
                "signer_role": "Disclosing Party"
            },
            {
                "signer_name": "Signature Recipient",
                "signer_email": "recipient@test.com",
                "signer_role": "Receiving Party"
            }
        ],
        "message": "Please review and sign this NDA.",
        "reminder_days": 3
    }

    signature_response = await test_client.post(
        f"/api/v1/documents/{document_id}/send-for-signature",
        json=signature_request,
        headers=auth_headers
    )

    # In real implementation, this would integrate with DocuSign
    # For testing, we'll verify the request was processed correctly
    assert signature_response.status_code == 200

    # Verify document status was updated
    updated_doc_response = await test_client.get(
        f"/api/v1/documents/{document_id}",
        headers=auth_headers
    )
    updated_doc = updated_doc_response.json()
    assert updated_doc["signature_status"] == "pending"
```

---

## 9. Monitoring & Analytics

### 9.1 Application Monitoring
```python
# monitoring/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure application logging."""

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger

# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
document_generation_counter = Counter(
    'document_generations_total',
    'Total number of documents generated',
    ['template_type', 'user_tier']
)

document_generation_duration = Histogram(
    'document_generation_duration_seconds',
    'Time spent generating documents',
    ['template_type']
)

active_users_gauge = Gauge(
    'active_users_current',
    'Current number of active users'
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint', 'status_code']
)

subscription_revenue_gauge = Gauge(
    'subscription_revenue_total',
    'Total subscription revenue',
    ['tier']
)

class MetricsMiddleware:
    """Middleware to collect API metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            # Process request
            await self.app(scope, receive, send)

            # Record metrics
            duration = time.time() - start_time
            method = scope["method"]
            path = scope["path"]

            # This would be set by the response
            status_code = "200"  # Simplified for example

            api_request_duration.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).observe(duration)
        else:
            await self.app(scope, receive, send)
```

### 9.2 Business Analytics
```python
# analytics/business_metrics.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.models import User, GeneratedDocument, Subscription, UsageTracking

class BusinessAnalytics:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get user-related metrics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Total users
        total_users = await self.db.scalar(
            select(func.count(User.id))
        )

        # New users in period
        new_users = await self.db.scalar(
            select(func.count(User.id))
            .where(User.created_at >= start_date)
        )

        # Active users (users who generated documents)
        active_users = await self.db.scalar(
            select(func.count(func.distinct(GeneratedDocument.user_id)))
            .where(GeneratedDocument.created_at >= start_date)
        )

        # Users by subscription tier
        tier_breakdown = await self.db.execute(
            select(User.subscription_tier, func.count(User.id))
            .group_by(User.subscription_tier)
        )

        return {
            "total_users": total_users,
            "new_users": new_users,
            "active_users": active_users,
            "tier_breakdown": dict(tier_breakdown.fetchall())
        }

    async def get_document_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get document generation metrics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Total documents generated
        total_documents = await self.db.scalar(
            select(func.count(GeneratedDocument.id))
            .where(GeneratedDocument.created_at >= start_date)
        )

        # Documents by status
        status_breakdown = await self.db.execute(
            select(GeneratedDocument.status, func.count(GeneratedDocument.id))
            .where(GeneratedDocument.created_at >= start_date)
            .group_by(GeneratedDocument.status)
        )

        # Popular templates
        template_usage = await self.db.execute(
            select(GeneratedDocument.template_id, func.count(GeneratedDocument.id))
            .where(GeneratedDocument.created_at >= start_date)
            .group_by(GeneratedDocument.template_id)
            .order_by(func.count(GeneratedDocument.id).desc())
            .limit(10)
        )

        return {
            "total_documents": total_documents,
            "status_breakdown": dict(status_breakdown.fetchall()),
            "popular_templates": dict(template_usage.fetchall())
        }

    async def get_revenue_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue-related metrics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Active subscriptions by tier
        active_subscriptions = await self.db.execute(
            select(Subscription.plan_type, func.count(Subscription.id))
            .where(Subscription.status == 'active')
            .group_by(Subscription.plan_type)
        )

        # Monthly recurring revenue (simplified calculation)
        tier_pricing = {
            'starter': 29,
            'professional': 39,
            'enterprise': 199
        }

        mrr_by_tier = {}
        total_mrr = 0

        for plan_type, count in active_subscriptions.fetchall():
            monthly_revenue = count * tier_pricing.get(plan_type, 0)
            mrr_by_tier[plan_type] = monthly_revenue
            total_mrr += monthly_revenue

        return {
            "total_mrr": total_mrr,
            "mrr_by_tier": mrr_by_tier,
            "active_subscriptions": dict(active_subscriptions.fetchall())
        }

    async def get_usage_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get usage analytics."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Usage by action type
        usage_breakdown = await self.db.execute(
            select(UsageTracking.action_type, func.count(UsageTracking.id))
            .where(UsageTracking.created_at >= start_date)
            .group_by(UsageTracking.action_type)
        )

        # Daily usage trend
        daily_usage = await self.db.execute(
            select(
                func.date(UsageTracking.created_at).label('date'),
                func.count(UsageTracking.id).label('count')
            )
            .where(UsageTracking.created_at >= start_date)
            .group_by(func.date(UsageTracking.created_at))
            .order_by(func.date(UsageTracking.created_at))
        )

        return {
            "usage_breakdown": dict(usage_breakdown.fetchall()),
            "daily_usage": [
                {"date": str(date), "count": count}
                for date, count in daily_usage.fetchall()
            ]
        }
```

---

## 10. Security Implementation

### 10.1 Authentication & Authorization
```python
# security/auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.models import User
from app.database import get_db

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        """Create an access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """Verify and decode a token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                return None
            return payload
        except JWTError:
            return None

auth_service = AuthService()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = auth_service.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def require_subscription_tier(min_tier: str):
    """Decorator to require a minimum subscription tier."""
    tier_hierarchy = {"free": 0, "starter": 1, "professional": 2, "enterprise": 3}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_tier_level = tier_hierarchy.get(current_user.subscription_tier, 0)
        required_tier_level = tier_hierarchy.get(min_tier, 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"This feature requires {min_tier} subscription or higher"
            )

        return current_user

    return dependency
```

### 10.2 Data Validation & Sanitization
```python
# security/validation.py
import re
from typing import Any, Dict
from pydantic import validator, BaseModel
import bleach

class SecurityValidators:
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format and normalize."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower().strip()

    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")

        return password

    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML content."""
        allowed_tags = ['p', 'br', 'strong', 'em', 'u']
        allowed_attributes = {}

        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate and normalize phone number."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)

        # Check if it's a valid US phone number (10 or 11 digits)
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            return f"+{digits_only}"
        else:
            raise ValueError("Invalid phone number format")

    @staticmethod
    def validate_company_name(name: str) -> str:
        """Validate company name."""
        if len(name.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")

        if len(name.strip()) > 255:
            raise ValueError("Company name must be less than 255 characters")

        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', name.strip())
        return sanitized

class SecureUserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: Optional[str] = None
    phone: Optional[str] = None

    @validator('email')
    def validate_email(cls, v):
        return SecurityValidators.validate_email(v)

    @validator('password')
    def validate_password(cls, v):
        return SecurityValidators.validate_password(v)

    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")
        return SecurityValidators.sanitize_html(v.strip())

    @validator('company_name')
    def validate_company_name(cls, v):
        if v:
            return SecurityValidators.validate_company_name(v)
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            return SecurityValidators.validate_phone(v)
        return v
```

### 10.3 Rate Limiting & Security Headers
```python
# security/rate_limiting.py
import asyncio
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_limit = 100  # requests per window
        self.default_window = 3600  # 1 hour in seconds

    async def is_allowed(
        self,
        key: str,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> bool:
        """Check if request is allowed based on rate limit."""
        limit = limit or self.default_limit
        window = window or self.default_window

        current_time = int(time.time())
        pipeline = self.redis.pipeline()

        # Use sliding window rate limiting
        pipeline.zremrangebyscore(key, 0, current_time - window)
        pipeline.zcard(key)
        pipeline.zadd(key, {str(current_time): current_time})
        pipeline.expire(key, window)

        results = pipeline.execute()
        current_requests = results[1]

        return current_requests < limit

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: redis.Redis):
        super().__init__(app)
        self.rate_limiter = RateLimiter(redis_client)

        # Define rate limits for different endpoints
        self.endpoint_limits = {
            "/api/v1/auth/login": (5, 300),  # 5 requests per 5 minutes
            "/api/v1/auth/register": (3, 3600),  # 3 requests per hour
            "/api/v1/documents/generate": (10, 3600),  # 10 documents per hour
        }

    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self.get_client_ip(request)

        # Check if endpoint has specific rate limit
        path = request.url.path
        if path in self.endpoint_limits:
            limit, window = self.endpoint_limits[path]
            key = f"rate_limit:{client_ip}:{path}"

            if not await self.rate_limiter.is_allowed(key, limit, window):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )

        # Check global rate limit
        global_key = f"rate_limit:global:{client_ip}"
        if not await self.rate_limiter.is_allowed(global_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Global rate limit exceeded"
            )

        response = await call_next(request)
        return response

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
```

---

## 11. Performance Optimization

### 11.1 Database Optimization
```python
# optimization/database.py
from sqlalchemy import Index, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from app.models import GeneratedDocument, User, NdaTemplate

# Database indexes for performance
class DatabaseOptimization:
    @staticmethod
    def create_performance_indexes():
        """Define database indexes for optimal query performance."""

        # Compound indexes for common queries
        user_subscription_idx = Index(
            'idx_user_subscription_active',
            User.subscription_tier,
            User.is_active
        )

        document_user_status_idx = Index(
            'idx_document_user_status_date',
            GeneratedDocument.user_id,
            GeneratedDocument.status,
            GeneratedDocument.created_at.desc()
        )

        template_category_active_idx = Index(
            'idx_template_category_active_tier',
            NdaTemplate.category_id,
            NdaTemplate.is_active,
            NdaTemplate.tier_requirement
        )

        # Partial indexes for specific conditions
        active_subscriptions_idx = Index(
            'idx_active_subscriptions',
            Subscription.user_id,
            Subscription.status,
            postgresql_where=text("status = 'active'")
        )

        return [
            user_subscription_idx,
            document_user_status_idx,
            template_category_active_idx,
            active_subscriptions_idx
        ]

    @staticmethod
    async def get_user_documents_optimized(
        db: AsyncSession,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ):
        """Optimized query for user documents with minimal database hits."""

        # Use selectinload to avoid N+1 query problem
        result = await db.execute(
            select(GeneratedDocument)
            .options(selectinload(GeneratedDocument.template))
            .where(GeneratedDocument.user_id == user_id)
            .order_by(GeneratedDocument.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        return result.scalars().all()

    @staticmethod
    async def get_dashboard_data_optimized(
        db: AsyncSession,
        user_id: str
    ):
        """Single query to get all dashboard data."""

        # Use a single query with CTEs for efficiency
        query = text("""
            WITH user_stats AS (
                SELECT
                    COUNT(*) as total_documents,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_documents,
                    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '30 days' THEN 1 END) as recent_documents
                FROM generated_documents
                WHERE user_id = :user_id
            ),
            usage_stats AS (
                SELECT
                    action_type,
                    COUNT(*) as count
                FROM usage_tracking
                WHERE user_id = :user_id
                AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY action_type
            )
            SELECT * FROM user_stats, usage_stats
        """)

        result = await db.execute(query, {"user_id": user_id})
        return result.fetchall()

# Caching strategies
from functools import wraps
import json
import hashlib

class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour

    def cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_hash = hashlib.md5(
            json.dumps(key_data, sort_keys=True).encode()
        ).hexdigest()
        return f"{prefix}:{key_hash}"

    async def get(self, key: str):
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None

    async def set(self, key: str, value: any, ttl: int = None):
        """Set value in cache."""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized_value)
        except Exception:
            pass

    def cached(self, prefix: str, ttl: int = None):
        """Decorator for caching function results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                cache_key = self.cache_key(prefix, *args, **kwargs)

                # Try to get from cache first
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result

            return wrapper
        return decorator

# Example usage of caching
cache_service = CacheService(redis_client)

@cache_service.cached("templates", ttl=1800)  # Cache for 30 minutes
async def get_templates_cached(category: str = None, industry: str = None):
    """Cached template retrieval."""
    # This would be the actual database query
    pass

@cache_service.cached("user_documents", ttl=300)  # Cache for 5 minutes
async def get_user_documents_cached(user_id: str, limit: int = 20):
    """Cached user documents retrieval."""
    # This would be the actual database query
    pass
```

### 11.2 Frontend Performance Optimization
```typescript
// hooks/use-optimized-api.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'

// Optimized hooks with proper caching and error handling
export function useTemplates(category?: string, industry?: string) {
  return useQuery({
    queryKey: ['templates', { category, industry }],
    queryFn: () => api.templates.getAll({ category, industry }),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}

export function useUserDocuments(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['documents', 'user', { page, limit }],
    queryFn: () => api.documents.getAll({
      skip: (page - 1) * limit,
      limit
    }),
    staleTime: 2 * 60 * 1000, // 2 minutes
    keepPreviousData: true, // For pagination
  })
}

export function useGenerateDocument() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: api.documents.generate,
    onSuccess: (newDocument) => {
      // Invalidate and refetch documents list
      queryClient.invalidateQueries(['documents', 'user'])

      // Optimistically update the cache
      queryClient.setQueryData(['documents', 'user'], (old: any) => {
        if (!old) return old
        return {
          ...old,
          data: [newDocument, ...old.data.slice(0, 19)] // Keep only 20 items
        }
      })
    },
    onError: (error) => {
      console.error('Document generation failed:', error)
    }
  })
}

// Optimized component with lazy loading and virtualization
// components/documents/document-list-optimized.tsx
import { useMemo } from 'react'
import { FixedSizeList as List } from 'react-window'
import { DocumentCard } from './document-card'
import { useUserDocuments } from '@/hooks/use-optimized-api'
import { Skeleton } from '@/components/ui/skeleton'

interface DocumentListProps {
  searchTerm?: string
  statusFilter?: string
}

export function DocumentListOptimized({ searchTerm, statusFilter }: DocumentListProps) {
  const { data, isLoading, error } = useUserDocuments()

  // Memoized filtering to avoid unnecessary re-computations
  const filteredDocuments = useMemo(() => {
    if (!data?.data) return []

    return data.data.filter(doc => {
      const matchesSearch = !searchTerm ||
        doc.document_name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = !statusFilter || doc.status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [data?.data, searchTerm, statusFilter])

  // Virtual list item renderer
  const Row = ({ index, style }) => (
    <div style={style}>
      <DocumentCard document={filteredDocuments[index]} />
    </div>
  )

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Failed to load documents</p>
      </div>
    )
  }

  if (filteredDocuments.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No documents found</p>
      </div>
    )
  }

  return (
    <List
      height={600}
      itemCount={filteredDocuments.length}
      itemSize={100}
      itemData={filteredDocuments}
    >
      {Row}
    </List>
  )
}

// Progressive Web App configuration
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\.ndarite\.com\/api\/v1\/templates/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'api-templates',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 60 * 60 * 24 // 24 hours
        }
      }
    },
    {
      urlPattern: /^https:\/\/api\.ndarite\.com\/api\/v1\/documents/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-documents',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 60 * 60 // 1 hour
        }
      }
    }
  ]
})

module.exports = withPWA({
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['api.ndarite.com'],
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Bundle analyzer for optimization
      if (process.env.ANALYZE === 'true') {
        const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer')
        config.plugins.push(
          new BundleAnalyzerPlugin({
            analyzerMode: 'server',
            openAnalyzer: true,
          })
        )
      }

      // Optimize bundle size
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }

    return config
  },
})
```

---

## 12. CI/CD Pipeline

### 12.1 GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [ published ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME_BACKEND: ndarite/backend
  IMAGE_NAME_FRONTEND: ndarite/frontend

jobs:
  # Backend Testing
  test-backend:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_ndarite
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run database migrations
      working-directory: ./backend
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_ndarite
      run: |
        alembic upgrade head

    - name: Run tests with coverage
      working-directory: ./backend
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_ndarite
        REDIS_URL: redis://localhost:6379
        SECRET_KEY: test-secret-key
      run: |
        pytest --cov=app --cov-report=xml --cov-report=html

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: backend
        name: backend-coverage

    - name: Run security scan
      working-directory: ./backend
      run: |
        pip install bandit safety
        bandit -r app/
        safety check

  # Frontend Testing
  test-frontend:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: './frontend/package-lock.json'

    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Run linting
      working-directory: ./frontend
      run: npm run lint

    - name: Run type checking
      working-directory: ./frontend
      run: npm run type-check

    - name: Run tests
      working-directory: ./frontend
      run: npm run test:ci

    - name: Build application
      working-directory: ./frontend
      run: npm run build

    - name: Run E2E tests
      working-directory: ./frontend
      run: |
        npm run e2e:ci

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          frontend/test-results/
          frontend/coverage/

  # Security Scanning
  security-scan:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend]

    steps:
    - uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

    - name: Run CodeQL Analysis
      uses: github/codeql-action/init@v2
      with:
        languages: python, javascript

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2

  # Build and Push Docker Images
  build-and-push:
    runs-on: ubuntu-latest
    needs: [test-backend, test-frontend, security-scan]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    permissions:
      contents: read
      packages: write

    steps:
    - uses: actions/checkout@v4

    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2

    - name: Extract metadata for backend
      id: meta-backend
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}
        tags: |
          type=ref,event=branch
          type=sha,prefix=sha-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        file: ./backend/Dockerfile.backend
        push: true
        tags: ${{ steps.meta-backend.outputs.tags }}
        labels: ${{ steps.meta-backend.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Extract metadata for frontend
      id: meta-frontend
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}
        tags: |
          type=ref,event=branch
          type=sha,prefix=sha-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        file: ./frontend/Dockerfile.frontend
        push: true
        tags: ${{ steps.meta-frontend.outputs.tags }}
        labels: ${{ steps.meta-frontend.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # Deploy to Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: [build-and-push]
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to staging
      env:
        KUBECONFIG_DATA: ${{ secrets.STAGING_KUBECONFIG }}
        IMAGE_TAG: sha-${{ github.sha }}
      run: |
        echo "$KUBECONFIG_DATA" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

        # Update deployment images
        kubectl set image deployment/backend backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}:${{ env.IMAGE_TAG }} -n ndarite-staging
        kubectl set image deployment/frontend frontend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}:${{ env.IMAGE_TAG }} -n ndarite-staging

        # Wait for rollout
        kubectl rollout status deployment/backend -n ndarite-staging --timeout=300s
        kubectl rollout status deployment/frontend -n ndarite-staging --timeout=300s

    - name: Run smoke tests
      run: |
        # Add smoke tests for staging environment
        curl -f https://staging-api.ndarite.com/health || exit 1
        curl -f https://staging.ndarite.com || exit 1

  # Deploy to Production
  deploy-production:
    runs-on: ubuntu-latest
    needs: [build-and-push]
    if: github.event_name == 'release'
    environment: production

    steps:
    - uses: actions/checkout@v4

    - name: Deploy to production
      env:
        KUBECONFIG_DATA: ${{ secrets.PRODUCTION_KUBECONFIG }}
        IMAGE_TAG: ${{ github.event.release.tag_name }}
      run: |
        echo "$KUBECONFIG_DATA" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

        # Blue-green deployment strategy
        kubectl apply -f k8s/production/ -n ndarite-prod

        # Update deployment images
        kubectl set image deployment/backend backend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}:${{ env.IMAGE_TAG }} -n ndarite-prod
        kubectl set image deployment/frontend frontend=${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}:${{ env.IMAGE_TAG }} -n ndarite-prod

        # Wait for rollout
        kubectl rollout status deployment/backend -n ndarite-prod --timeout=600s
        kubectl rollout status deployment/frontend -n ndarite-prod --timeout=600s

    - name: Run production health checks
      run: |
        # Comprehensive health checks
        curl -f https://api.ndarite.com/health || exit 1
        curl -f https://www.ndarite.com || exit 1

        # Check critical endpoints
        curl -f https://api.ndarite.com/api/v1/templates || exit 1

    - name: Notify deployment success
      if: success()
      uses: 8398a7/action-slack@v3
      with:
        status: success
        text: 'Production deployment successful! :rocket:'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

    - name: Notify deployment failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        text: 'Production deployment failed! :x:'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 12.2 Infrastructure as Code (Terraform)
```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
  }

  backend "s3" {
    bucket = "ndarite-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.environment}-ndarite-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Environment = var.environment
    Project     = "ndarite"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = "${var.environment}-ndarite-cluster"
  cluster_version = "1.27"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Managed node groups
  eks_managed_node_groups = {
    main = {
      desired_size = 3
      max_size     = 10
      min_size     = 1

      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"

      k8s_labels = {
        Environment = var.environment
        NodeGroup   = "main"
      }
    }
  }

  # Cluster access entry
  enable_cluster_creator_admin_permissions = true

  tags = {
    Environment = var.environment
    Project     = "ndarite"
  }
}

# RDS PostgreSQL Database
resource "aws_db_subnet_group" "ndarite" {
  name       = "${var.environment}-ndarite-db-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name        = "${var.environment}-ndarite-db-subnet-group"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.environment}-ndarite-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-ndarite-rds-sg"
    Environment = var.environment
  }
}

resource "aws_db_instance" "ndarite" {
  identifier = "${var.environment}-ndarite-db"

  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "ndarite"
  username = "ndarite_admin"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.ndarite.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"

  skip_final_snapshot = var.environment != "production"
  deletion_protection = var.environment == "production"

  performance_insights_enabled = true
  monitoring_interval         = 60
  monitoring_role_arn        = aws_iam_role.rds_monitoring.arn

  tags = {
    Name        = "${var.environment}-ndarite-db"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "ndarite" {
  name       = "${var.environment}-ndarite-cache-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.environment}-ndarite-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [module.vpc.vpc_cidr_block]
  }

  tags = {
    Name        = "${var.environment}-ndarite-redis-sg"
    Environment = var.environment
  }
}

resource "aws_elasticache_replication_group" "ndarite" {
  replication_group_id       = "${var.environment}-ndarite-redis"
  description                = "Redis cluster for NDARite ${var.environment}"

  node_type            = var.redis_node_type
  port                 = 6379
  parameter_group_name = "default.redis7"

  num_cache_clusters = 2

  subnet_group_name  = aws_elasticache_subnet_group.ndarite.name
  security_group_ids = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name        = "${var.environment}-ndarite-redis"
    Environment = var.environment
  }
}

# S3 Bucket for Document Storage
resource "aws_s3_bucket" "documents" {
  bucket = "${var.environment}-ndarite-documents-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.environment}-ndarite-documents"
    Environment = var.environment
  }
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "documents" {
  bucket = aws_s3_bucket.documents.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    id     = "document_lifecycle"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555  # 7 years for legal document retention
    }
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "ndarite" {
  origin {
    domain_name = aws_s3_bucket.documents.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.documents.id}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.ndarite.cloudfront_access_identity_path
    }
  }

  enabled = true

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.documents.id}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name        = "${var.environment}-ndarite-cdn"
    Environment = var.environment
  }
}

resource "aws_cloudfront_origin_access_identity" "ndarite" {
  comment = "NDARite ${var.environment} OAI"
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.ndarite.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = aws_elasticache_replication_group.ndarite.primary_endpoint_address
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name for documents"
  value       = aws_s3_bucket.documents.id
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.ndarite.domain_name
}
```

---

## 13. Documentation & API Reference

### 13.1 API Documentation Generation
```python
# docs/api_documentation.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
import json

def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="NDARite API",
        version="1.0.0",
        description="""
        ## NDARite API Documentation

        The NDARite API provides comprehensive endpoints for generating, managing, and signing
        Non-Disclosure Agreements through an intelligent platform.

        ### Authentication
        All endpoints require authentication via Bearer token except for public endpoints.

        ### Rate Limiting
        API requests are rate-limited to ensure fair usage:
        - Authentication endpoints: 5 requests per 5 minutes
        - Document generation: 10 requests per hour
        - General endpoints: 100 requests per hour

        ### Error Handling
        The API returns standard HTTP status codes and structured error responses:
        ```json
        {
            "detail": "Error message",
            "error_code": "SPECIFIC_ERROR_CODE",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        ```

        ### Webhooks
        NDARite supports webhooks for important events:
        - Document generation completion
        - Signature status updates
        - Subscription changes
        """,
        routes=app.routes,
        contact={
            "name": "NDARite API Support",
            "url": "https://www.ndarite.com/support",
            "email": "api@ndarite.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[
            {"url": "https://api.ndarite.com", "description": "Production server"},
            {"url": "https://staging-api.ndarite.com", "description": "Staging server"},
        ]
    )

    # Add custom schemas
    openapi_schema["components"]["schemas"].update({
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "description": "Error message"},
                "error_code": {"type": "string", "description": "Specific error code"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["detail", "timestamp"]
        },
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Success message"},
                "data": {"type": "object", "description": "Response data"},
                "timestamp": {"type": "string", "format": "date-time"}
            },
            "required": ["message", "timestamp"]
        }
    })

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Enhanced endpoint documentation examples
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(tags=["Documents"])

@router.post(
    "/documents/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate NDA Document",
    description="""
    Generate a new NDA document based on a template and provided information.

    This endpoint creates a legally formatted NDA document using the specified template
    and party information. The document is generated as both PDF and DOCX formats.

    **Process Flow:**
    1. Validate template access based on user subscription tier
    2. Process and validate party information
    3. Generate document using template engine
    4. Create PDF and DOCX versions
    5. Store document metadata in database
    6. Return document information with download links

    **Business Rules:**
    - Users must have appropriate subscription tier for template
    - All required fields must be provided
    - Email addresses are validated and normalized
    - Generated documents are retained for 7 years for legal compliance

    **Rate Limiting:**
    - Starter tier: 10 documents per month
    - Professional tier: 50 documents per month
    - Enterprise tier: Unlimited
    """,
    responses={
        201: {
            "description": "Document generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "document_name": "Mutual NDA - Tech Partnership",
                        "status": "generated",
                        "pdf_file_path": "documents/123e4567-e89b-12d3-a456-426614174000.pdf",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {
            "description": "Invalid request data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Validation error: disclosing_party.email is required",
                        "error_code": "VALIDATION_ERROR",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        402: {
            "description": "Subscription tier insufficient",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "This template requires Professional subscription or higher",
                        "error_code": "INSUFFICIENT_SUBSCRIPTION",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        404: {
            "description": "Template not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Template with ID 123 not found",
                        "error_code": "TEMPLATE_NOT_FOUND",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Document generation limit reached for your subscription tier",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        }
    }
)
async def generate_document(
    document_data: DocumentCreate = Body(
        ...,
        example={
            "template_id": "123e4567-e89b-12d3-a456-426614174000",
            "document_name": "Partnership NDA - Q1 2024",
            "disclosing_party": {
                "name": "John Smith",
                "title": "CEO",
                "company": "TechCorp Inc.",
                "address": "123 Innovation Drive, San Francisco, CA 94105",
                "email": "john.smith@techcorp.com",
                "phone": "+1-555-123-4567"
            },
            "receiving_party": {
                "name": "Jane Doe",
                "title": "CTO",
                "company": "StartupCo LLC",
                "address": "456 Startup Lane, Austin, TX 78701",
                "email": "jane.doe@startupco.com",
                "phone": "+1-555-987-6543"
            },
            "effective_date": "2024-02-01",
            "expiration_date": "2027-02-01",
            "governing_law": "Delaware, United States"
        }
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Implementation would go here"""
    pass
```

### 13.2 README and Setup Documentation
```markdown
# NDARite Platform - Technical Documentation

## Project Overview

NDARite is a comprehensive SaaS platform for generating legally-compliant Non-Disclosure Agreements through an intelligent questionnaire system and AI-powered template engine.

## Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 14+ with TypeScript
- **Database**: PostgreSQL 15+ with async SQLAlchemy
- **Cache**: Redis for session management and rate limiting
- **File Storage**: AWS S3 for document storage
- **Container**: Docker with Kubernetes orchestration
- **CI/CD**: GitHub Actions with automated testing and deployment

### System Requirements
- **Development**:
  - Python 3.11+
  - Node.js 18+
  - Docker Desktop
  - PostgreSQL 15+
  - Redis 7+

- **Production**:
  - Kubernetes cluster
  - AWS S3 bucket
  - External PostgreSQL database
  - Redis cluster
  - Load balancer with SSL termination

## Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ndarite.git
   cd ndarite
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Production Deployment

1. **Configure infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan -var-file="production.tfvars"
   terraform apply
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/production/
   ```

3. **Configure DNS and SSL**
   - Point DNS to load balancer
   - Configure SSL certificates
   - Update environment variables

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use Black formatter, type hints required
- **TypeScript**: Use ESLint + Prettier, strict mode enabled
- **Testing**: Minimum 80% code coverage required
- **Documentation**: All public APIs must be documented

### Git Workflow
1. Create feature branch from `develop`
2. Implement changes with tests
3. Submit pull request with description
4. Code review and approval required
5. Merge to `develop` for staging deployment
6. Release to `main` for production deployment

### Testing Strategy
- **Unit Tests**: All business logic functions
- **Integration Tests**: API endpoints and database operations
- **E2E Tests**: Critical user workflows
- **Performance Tests**: Load testing for key endpoints

## Security Considerations

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Subscription tier validation for features
- API key authentication for enterprise integrations

### Data Protection
- All passwords hashed with bcrypt
- Sensitive data encrypted at rest
- TLS 1.3 for data in transit
- Regular security audits and dependency updates

### Compliance
- GDPR compliance for EU users
- SOC 2 Type II certification in progress
- Data retention policies implemented
- Audit logging for all sensitive operations

## Monitoring & Observability

### Metrics Collection
- Application metrics via Prometheus
- Business metrics via custom analytics
- Infrastructure monitoring via DataDog
- Error tracking via Sentry

### Logging
- Structured JSON logging
- Centralized log aggregation
- Log retention policies
- Security event monitoring

### Alerting
- Critical system alerts via PagerDuty
- Business metric alerts via Slack
- Performance degradation alerts
- Security incident notifications

## API Integration Guide

### Authentication
```python
import requests

# Get access token
response = requests.post('https://api.ndarite.com/api/v1/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Use token in subsequent requests
headers = {'Authorization': f'Bearer {token}'}
```

### Document Generation
```python
# Generate NDA document
document_data = {
    'template_id': 'template-uuid',
    'document_name': 'Partnership NDA',
    'disclosing_party': {
        'name': 'Company A',
        'email': 'contact@companya.com',
        'address': '123 Business St'
    },
    'receiving_party': {
        'name': 'Company B',
        'email': 'contact@companyb.com',
        'address': '456 Corporate Ave'
    }
}

response = requests.post(
    'https://api.ndarite.com/api/v1/documents/generate',
    json=document_data,
    headers=headers
)
document = response.json()
```

### Webhook Integration
```python
from fastapi import FastAPI, Request
import hmac
import hashlib

app = FastAPI()

@app.post("/ndarite-webhook")
async def handle_webhook(request: Request):
    # Verify webhook signature
    signature = request.headers.get('X-NDARite-Signature')
    payload = await request.body()

    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process webhook event
    event_data = await request.json()
    if event_data['event_type'] == 'document.signed':
        # Handle document signing completion
        document_id = event_data['data']['document_id']
        # Your business logic here

    return {"status": "processed"}
```

## Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check database status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

**Frontend Build Failures**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

**API Authentication Issues**
```python
# Verify token format
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)

# Check token expiration
import datetime
exp = datetime.datetime.fromtimestamp(decoded['exp'])
print(f"Token expires: {exp}")
```

### Performance Optimization

**Database Query Optimization**
```python
# Use indexes for common queries
# Enable query logging to identify slow queries
# Implement connection pooling
# Use read replicas for read-heavy operations
```

**Frontend Performance**
```typescript
// Implement code splitting
const DocumentList = lazy(() => import('./DocumentList'))

// Use React.memo for expensive components
const ExpensiveComponent = memo(({ data }) => {
  // Component implementation
})

// Implement virtual scrolling for large lists
import { FixedSizeList } from 'react-window'
```

## Contributing

### Getting Started
1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make changes with tests
5. Submit pull request

### Code Review Process
- All code requires review from maintainer
- Automated tests must pass
- Security scan must pass
- Documentation updates required for new features

### Release Process
- Semantic versioning (MAJOR.MINOR.PATCH)
- Automated changelog generation
- Staged deployment (staging → production)
- Rollback procedures documented

## Support

### Documentation
- API Reference: https://docs.ndarite.com/api
- User Guide: https://docs.ndarite.com/guide
- Integration Examples: https://docs.ndarite.com/examples

### Community
- GitHub Issues: Bug reports and feature requests
- Discord: Real-time community support
- Stack Overflow: Technical questions (tag: ndarite)

### Enterprise Support
- Dedicated support team
- SLA guarantees
- Custom integration assistance
- Priority feature requests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a complete list of changes and releases.
```

---

## Conclusion

This comprehensive technical documentation provides a complete blueprint for building the NDARite platform. The architecture is designed for:

- **Scalability**: Microservices architecture with Kubernetes orchestration
- **Security**: Enterprise-grade authentication, encryption, and compliance
- **Performance**: Optimized database queries, caching, and CDN integration
- **Maintainability**: Clean code structure, comprehensive testing, and documentation
- **Reliability**: Monitoring, alerting, and automated deployment pipelines

The platform is ready for immediate development with Augment Code and can scale from MVP to enterprise-grade SaaS serving thousands of users generating millions of legal documents.

**Key Implementation Priorities:**
1. Core document generation engine
2. User authentication and subscription management
3. Payment integration and billing
4. DocuSign integration for electronic signatures
5. Admin dashboard and analytics
6. API documentation and developer tools

This technical specification provides everything needed to build a production-ready NDA generation platform that can compete with established legal tech companies while offering superior user experience and technological innovation.
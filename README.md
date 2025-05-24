# NDARite - Legal NDA Generation Platform

A comprehensive SaaS platform for generating legally-compliant Non-Disclosure Agreements through an intelligent questionnaire system.

## 🚀 Features

### Core Functionality
- **Intelligent NDA Generation**: Multi-step questionnaire system for creating customized NDAs
- **Multiple Template Types**: Bilateral, unilateral, and multilateral agreements
- **Legal Compliance**: Templates reviewed by legal experts and compliant with current regulations
- **Multiple Output Formats**: Generate documents in PDF and DOCX formats
- **Electronic Signatures**: Integration with DocuSign for seamless signing workflow

### User Management
- **Subscription Tiers**: Free, Starter, Professional, and Enterprise plans
- **Usage Tracking**: Monitor document creation, storage, and API usage
- **Role-Based Access**: User, admin, and legal partner roles
- **Secure Authentication**: JWT-based authentication with refresh tokens

### Advanced Features
- **Document Management**: Version control, status tracking, and document history
- **Template Library**: Categorized templates for different industries and use cases
- **Payment Processing**: Stripe integration for subscription management
- **API Access**: RESTful API for enterprise integrations
- **Analytics Dashboard**: Usage statistics and document insights

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh mechanism
- **Document Generation**: Jinja2 templates with WeasyPrint for PDF generation
- **Task Queue**: Celery with Redis for background processing
- **File Storage**: AWS S3 integration for document storage

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for client-side state
- **Forms**: React Hook Form with Zod validation
- **UI Components**: Custom component library with Radix UI primitives

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 15
- **Caching**: Redis for session management and task queue
- **Monitoring**: Sentry for error tracking
- **Deployment**: Production-ready with Nginx reverse proxy

## 📋 Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **PostgreSQL** 15+
- **Redis** 7+
- **Docker** and **Docker Compose** (recommended)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ndarite.git
   cd ndarite
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   
   # Frontend
   cd ../frontend
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```

3. **Start the services**
   ```bash
   cd backend
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec backend python init_db.py
   ```

5. **Start the frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb ndarite
   
   # Run migrations
   python init_db.py
   ```

4. **Start the backend**
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

## 🔧 Configuration

### Backend Environment Variables

```env
# Core Settings
ENVIRONMENT=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ndarite

# External Services
STRIPE_SECRET_KEY=sk_test_...
DOCUSIGN_INTEGRATION_KEY=your-key
SENDGRID_API_KEY=SG...
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# Subscription Limits
FREE_TIER_DOCUMENT_LIMIT=3
STARTER_TIER_DOCUMENT_LIMIT=25
PROFESSIONAL_TIER_DOCUMENT_LIMIT=100
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/templates/` - List available templates
- `POST /api/v1/documents/generate` - Generate new document
- `GET /api/v1/documents/` - List user documents
- `GET /api/v1/subscriptions/plans` - Get subscription plans

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
cd frontend
npm run test:e2e
```

## 📦 Deployment

### Production Deployment

1. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy with Docker**
   ```bash
   cd backend
   docker-compose --profile production up -d
   ```

3. **Set up SSL certificates**
   ```bash
   # Place SSL certificates in backend/ssl/
   # Update nginx.conf with your domain
   ```

### Environment-Specific Configurations

- **Development**: Local database, file storage, and email simulation
- **Staging**: Cloud database, S3 storage, real email service
- **Production**: Full cloud infrastructure with monitoring and backups

## 🔒 Security

- **Authentication**: JWT tokens with secure refresh mechanism
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Encryption at rest and in transit
- **Input Validation**: Comprehensive validation using Pydantic and Zod
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS**: Properly configured cross-origin resource sharing

## 📈 Monitoring and Analytics

- **Error Tracking**: Sentry integration for error monitoring
- **Performance**: Application performance monitoring
- **Usage Analytics**: User behavior and feature usage tracking
- **Health Checks**: Automated health monitoring for all services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Write tests for new features
- Update documentation for API changes
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.ndarite.com](https://docs.ndarite.com)
- **Email Support**: support@ndarite.com
- **Community**: [Discord Server](https://discord.gg/ndarite)
- **Issues**: [GitHub Issues](https://github.com/your-org/ndarite/issues)

## 🙏 Acknowledgments

- Legal templates reviewed by qualified attorneys
- Built with modern web technologies and best practices
- Inspired by the need for accessible legal document generation
- Community feedback and contributions

---

**NDARite** - Making legal document generation accessible to everyone.

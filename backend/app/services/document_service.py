"""
Document Generation Service
Core business logic for NDA document generation and management
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
import logging
import asyncio
from datetime import datetime, timezone

from app.models.user import User
from app.models.template import NDATemplate
from app.models.document import GeneratedDocument, DocumentSigner
from app.models.audit import UsageTracking
from app.schemas.document import DocumentCreate, SignatureRequest
from app.services.pdf_generator import PDFGenerator
from app.utils.security import generate_secure_filename
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document generation and management"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.pdf_generator = PDFGenerator()

    async def generate_document(
        self,
        user: User,
        document_data: DocumentCreate
    ) -> GeneratedDocument:
        """
        Generate a new NDA document from template and user data
        """
        try:
            # Check user's document limit
            await self._check_document_limit(user)

            # Get and validate template
            template = await self._get_template(document_data.template_id, user)

            # Create document record
            document = await self._create_document_record(user, template, document_data)

            # Generate PDF in background
            asyncio.create_task(self._generate_pdf_async(document))

            # Track usage
            await self._track_usage(user, "document_generated", document.id)

            logger.info(f"Document generation started: {document.id} for user {user.email}")

            return document

        except Exception as e:
            logger.error(f"Document generation error: {e}")
            await self.db.rollback()
            raise

    async def _check_document_limit(self, user: User) -> None:
        """Check if user can create more documents"""
        # Get current document count for this month
        from datetime import datetime, timezone
        current_month_start = datetime.now(timezone.utc).replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )

        result = await self.db.execute(
            select(func.count(GeneratedDocument.id))
            .where(
                GeneratedDocument.user_id == user.id,
                GeneratedDocument.created_at >= current_month_start
            )
        )
        current_count = result.scalar() or 0

        if not user.can_create_documents(current_count):
            raise ValueError(f"Document limit reached for {user.subscription_tier} tier")

    async def _get_template(self, template_id: UUID, user: User) -> NDATemplate:
        """Get and validate template access"""
        result = await self.db.execute(
            select(NDATemplate)
            .where(NDATemplate.id == template_id, NDATemplate.is_active == True)
        )
        template = result.scalar_one_or_none()

        if not template:
            raise ValueError("Template not found")

        if not template.can_access(user.subscription_tier):
            raise ValueError(f"Template requires {template.tier_requirement} subscription")

        return template

    async def _create_document_record(
        self,
        user: User,
        template: NDATemplate,
        document_data: DocumentCreate
    ) -> GeneratedDocument:
        """Create document database record"""

        # Prepare document data
        doc_data = {
            "template_id": template.id,
            "template_name": template.name,
            "template_type": template.template_type,
            "user_responses": document_data.custom_fields or {},
            "generation_timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Create document
        document = GeneratedDocument(
            user_id=user.id,
            template_id=template.id,
            document_name=document_data.document_name,
            document_data=doc_data,
            disclosing_party=document_data.disclosing_party.model_dump(),
            receiving_party=document_data.receiving_party.model_dump(),
            additional_parties=[party.model_dump() for party in document_data.additional_parties] if document_data.additional_parties else None,
            effective_date=document_data.effective_date,
            expiration_date=document_data.expiration_date,
            governing_law=document_data.governing_law,
            status="draft"
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def _generate_pdf_async(self, document: GeneratedDocument) -> None:
        """Generate PDF file asynchronously"""
        try:
            # Get template for PDF generation
            result = await self.db.execute(
                select(NDATemplate).where(NDATemplate.id == document.template_id)
            )
            template = result.scalar_one()

            # Prepare context for PDF generation
            context = self._prepare_pdf_context(document, template)

            # Generate PDF filename
            pdf_filename = generate_secure_filename(
                f"{document.document_name}.pdf",
                str(document.user_id)
            )
            pdf_path = f"documents/{pdf_filename}"

            # Generate PDF
            await self.pdf_generator.generate_nda_pdf(
                template_name=self._get_template_file_name(template),
                context=context,
                output_path=pdf_path
            )

            # Update document record
            document.pdf_file_path = pdf_path
            document.status = "generated"
            await self.db.commit()

            logger.info(f"PDF generated successfully: {document.id}")

        except Exception as e:
            logger.error(f"PDF generation failed for document {document.id}: {e}")
            # Update document status to indicate failure
            document.status = "error"
            await self.db.commit()

    def _prepare_pdf_context(self, document: GeneratedDocument, template: NDATemplate) -> Dict[str, Any]:
        """Prepare context data for PDF generation"""
        return {
            "document_name": document.document_name,
            "effective_date": document.effective_date.strftime("%B %d, %Y") if document.effective_date else None,
            "expiration_date": document.expiration_date.strftime("%B %d, %Y") if document.expiration_date else None,
            "governing_law": document.governing_law,
            "disclosing_party": document.disclosing_party,
            "receiving_party": document.receiving_party,
            "additional_parties": document.additional_parties,
            "template_type": template.template_type,
            "template_content": template.template_content,
            "legal_clauses": template.legal_clauses,
            "custom_fields": document.document_data.get("user_responses", {}),
            "generation_date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
            "document_id": str(document.id)
        }

    def _get_template_file_name(self, template: NDATemplate) -> str:
        """Get template file name for PDF generation"""
        type_mapping = {
            "bilateral": "bilateral_standard",
            "unilateral": "unilateral_standard",
            "multilateral": "multilateral_standard"
        }

        base_name = type_mapping.get(template.template_type, "bilateral_standard")

        if template.complexity_level == "basic":
            return f"{template.template_type}_basic"
        elif template.complexity_level == "advanced":
            return f"{template.template_type}_advanced"
        else:
            return base_name

    async def _track_usage(self, user: User, action: str, resource_id: UUID) -> None:
        """Track user action for analytics"""
        usage_record = UsageTracking(
            user_id=user.id,
            action_type=action,
            resource_id=resource_id,
            metadata={"timestamp": datetime.now(timezone.utc).isoformat()}
        )

        self.db.add(usage_record)
        await self.db.commit()

    async def send_for_signature(
        self,
        document: GeneratedDocument,
        signature_request: SignatureRequest,
        user: User
    ) -> Dict[str, Any]:
        """Send document for electronic signature"""
        try:
            # Validate document is ready for signature
            if document.status != "generated" or not document.pdf_file_path:
                raise ValueError("Document must be generated before sending for signature")

            # Create signer records
            signers = []
            for signer_info in signature_request.signers:
                signer = DocumentSigner(
                    document_id=document.id,
                    signer_name=signer_info.signer_name,
                    signer_email=signer_info.signer_email,
                    signer_role=signer_info.signer_role,
                    signature_status="pending"
                )
                signers.append(signer)
                self.db.add(signer)

            # TODO: Integrate with DocuSign API
            # For now, just update document status
            document.signature_status = "pending"

            await self.db.commit()

            # Track usage
            await self._track_usage(user, "signature_sent", document.id)

            logger.info(f"Document sent for signature: {document.id}")

            return {
                "message": "Document sent for signature",
                "signers_count": len(signers),
                "status": "pending"
            }

        except Exception as e:
            logger.error(f"Send for signature error: {e}")
            await self.db.rollback()
            raise

"""
Document Models
Database models for generated documents and signers
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Date, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class GeneratedDocument(Base):
    """Generated document model"""
    
    __tablename__ = "generated_documents"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("nda_templates.id"), nullable=False, index=True)
    
    # Document information
    document_name = Column(String(255), nullable=False)
    document_data = Column(JSONB, nullable=False)  # User responses and generated content
    
    # File paths
    pdf_file_path = Column(String(500), nullable=True)
    docx_file_path = Column(String(500), nullable=True)
    
    # Status tracking
    status = Column(String(20), default="draft", nullable=False, index=True)  # draft, generated, signed, completed
    
    # Parties information (JSON)
    disclosing_party = Column(JSONB, nullable=False)
    receiving_party = Column(JSONB, nullable=False)
    additional_parties = Column(JSONB, nullable=True)
    
    # Document metadata
    effective_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True)
    governing_law = Column(String(100), nullable=True)
    
    # Electronic signature integration
    docusign_envelope_id = Column(String(255), nullable=True, index=True)
    signature_status = Column(String(20), nullable=True)  # pending, signed, declined, expired
    signed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage tracking
    view_count = Column(Integer, default=0, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="generated_documents")
    template = relationship("NDATemplate", back_populates="generated_documents")
    signers = relationship("DocumentSigner", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GeneratedDocument(id={self.id}, name={self.document_name}, status={self.status})>"
    
    @property
    def is_draft(self) -> bool:
        """Check if document is in draft status"""
        return self.status == "draft"
    
    @property
    def is_generated(self) -> bool:
        """Check if document has been generated"""
        return self.status in ["generated", "signed", "completed"]
    
    @property
    def is_signed(self) -> bool:
        """Check if document is signed"""
        return self.status in ["signed", "completed"]
    
    @property
    def has_pdf(self) -> bool:
        """Check if document has PDF file"""
        return bool(self.pdf_file_path)
    
    @property
    def has_docx(self) -> bool:
        """Check if document has DOCX file"""
        return bool(self.docx_file_path)


class DocumentSigner(Base):
    """Document signer model"""
    
    __tablename__ = "document_signers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    document_id = Column(UUID(as_uuid=True), ForeignKey("generated_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Signer information
    signer_name = Column(String(255), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_role = Column(String(100), nullable=True)  # Disclosing Party, Receiving Party, Witness
    
    # Signature status
    signature_status = Column(String(20), default="pending", nullable=False)  # pending, signed, declined
    signed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking information
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    document = relationship("GeneratedDocument", back_populates="signers")
    
    def __repr__(self):
        return f"<DocumentSigner(id={self.id}, name={self.signer_name}, status={self.signature_status})>"
    
    @property
    def is_signed(self) -> bool:
        """Check if signer has signed"""
        return self.signature_status == "signed"
    
    @property
    def is_pending(self) -> bool:
        """Check if signature is pending"""
        return self.signature_status == "pending"

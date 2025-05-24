"""
Document Schemas
Pydantic models for document-related requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, date


class PartyInfo(BaseModel):
    """Schema for party information"""
    name: str = Field(..., min_length=1, max_length=255)
    title: Optional[str] = Field(None, max_length=100)
    company: Optional[str] = Field(None, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    
    @validator('name')
    def validate_name(cls, v):
        """Validate party name"""
        if not v or not v.strip():
            raise ValueError("Party name cannot be empty")
        return v.strip()
    
    @validator('address')
    def validate_address(cls, v):
        """Validate address"""
        if not v or not v.strip():
            raise ValueError("Address cannot be empty")
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number"""
        if v:
            import re
            digits_only = re.sub(r'\D', '', v)
            if len(digits_only) < 10:
                raise ValueError("Phone number must contain at least 10 digits")
        return v


class DocumentBase(BaseModel):
    """Base document schema"""
    document_name: str = Field(..., min_length=1, max_length=255)
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    governing_law: str = Field(default="United States", max_length=100)
    
    @validator('expiration_date')
    def validate_expiration_date(cls, v, values):
        """Validate expiration date is after effective date"""
        if v and 'effective_date' in values and values['effective_date']:
            if v <= values['effective_date']:
                raise ValueError("Expiration date must be after effective date")
        return v


class DocumentCreate(DocumentBase):
    """Schema for creating documents"""
    template_id: UUID
    disclosing_party: PartyInfo
    receiving_party: PartyInfo
    additional_parties: Optional[List[PartyInfo]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @validator('additional_parties')
    def validate_additional_parties(cls, v):
        """Validate additional parties list"""
        if v and len(v) > 10:  # Reasonable limit
            raise ValueError("Too many additional parties (maximum 10)")
        return v


class DocumentUpdate(BaseModel):
    """Schema for updating documents"""
    document_name: Optional[str] = Field(None, min_length=1, max_length=255)
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    governing_law: Optional[str] = Field(None, max_length=100)
    disclosing_party: Optional[PartyInfo] = None
    receiving_party: Optional[PartyInfo] = None
    additional_parties: Optional[List[PartyInfo]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, regex="^(draft|generated|signed|completed)$")


class DocumentResponse(DocumentBase):
    """Schema for document responses"""
    id: UUID
    user_id: UUID
    template_id: UUID
    status: str
    pdf_file_path: Optional[str]
    docx_file_path: Optional[str]
    signature_status: Optional[str]
    view_count: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    last_accessed: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    """Schema for detailed document responses"""
    document_data: Dict[str, Any]
    disclosing_party: Dict[str, Any]
    receiving_party: Dict[str, Any]
    additional_parties: Optional[List[Dict[str, Any]]]
    docusign_envelope_id: Optional[str]
    signed_at: Optional[datetime]


class DocumentListResponse(BaseModel):
    """Schema for document list responses"""
    documents: List[DocumentResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class SignerInfo(BaseModel):
    """Schema for signer information"""
    signer_name: str = Field(..., min_length=1, max_length=255)
    signer_email: EmailStr
    signer_role: str = Field(..., max_length=100)
    
    @validator('signer_name')
    def validate_signer_name(cls, v):
        """Validate signer name"""
        if not v or not v.strip():
            raise ValueError("Signer name cannot be empty")
        return v.strip()


class SignatureRequest(BaseModel):
    """Schema for signature requests"""
    signers: List[SignerInfo] = Field(..., min_items=1, max_items=10)
    message: Optional[str] = Field(None, max_length=1000)
    reminder_days: int = Field(default=3, ge=1, le=30)
    
    @validator('signers')
    def validate_signers(cls, v):
        """Validate signers list"""
        if not v:
            raise ValueError("At least one signer is required")
        
        # Check for duplicate emails
        emails = [signer.signer_email for signer in v]
        if len(emails) != len(set(emails)):
            raise ValueError("Duplicate signer emails are not allowed")
        
        return v


class DocumentSearchRequest(BaseModel):
    """Schema for document search requests"""
    query: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, regex="^(draft|generated|signed|completed)$")
    template_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at", regex="^(created_at|updated_at|document_name|status)$")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")


class DocumentGenerationResponse(BaseModel):
    """Schema for document generation response"""
    document_id: UUID
    status: str
    pdf_url: Optional[str]
    docx_url: Optional[str]
    generation_time_seconds: float
    
    class Config:
        from_attributes = True

"""
Document Management API Routes
Document generation, management, and signature handling
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import logging
import os

from app.database import get_db
from app.models.user import User
from app.models.document import GeneratedDocument, DocumentSigner
from app.schemas.document import (
    DocumentCreate, DocumentResponse, DocumentDetailResponse,
    DocumentListResponse, DocumentUpdate, SignatureRequest,
    DocumentSearchRequest, DocumentGenerationResponse
)
from app.dependencies import get_current_user, rate_limiter
from app.services.document_service import DocumentService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate", response_model=DocumentGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_document(
    document_data: DocumentCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Generate a new NDA document from template
    """
    try:
        import time
        start_time = time.time()
        
        # Create document service
        document_service = DocumentService(db)
        
        # Generate document
        document = await document_service.generate_document(current_user, document_data)
        
        generation_time = time.time() - start_time
        
        logger.info(f"Document generation initiated: {document.id} for user {current_user.email}")
        
        return DocumentGenerationResponse(
            document_id=document.id,
            status=document.status,
            pdf_url=f"/api/v1/documents/{document.id}/download?format=pdf" if document.pdf_file_path else None,
            docx_url=f"/api/v1/documents/{document.id}/download?format=docx" if document.docx_file_path else None,
            generation_time_seconds=generation_time
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document generation failed"
        )


@router.get("/", response_model=DocumentListResponse)
async def get_user_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of documents to return"),
    status: Optional[str] = Query(None, description="Filter by document status"),
    template_id: Optional[str] = Query(None, description="Filter by template ID"),
    search: Optional[str] = Query(None, description="Search in document names"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's documents with filtering and pagination
    """
    try:
        # Build query
        query = select(GeneratedDocument).where(GeneratedDocument.user_id == current_user.id)
        
        # Apply filters
        if status:
            query = query.where(GeneratedDocument.status == status)
        
        if template_id:
            query = query.where(GeneratedDocument.template_id == template_id)
        
        if search:
            query = query.where(GeneratedDocument.document_name.ilike(f"%{search}%"))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(GeneratedDocument.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()
        
        # Calculate pagination info
        has_next = (skip + limit) < total
        has_prev = skip > 0
        page = (skip // limit) + 1
        
        return DocumentListResponse(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            page=page,
            per_page=limit,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Get documents error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific document
    """
    try:
        # Get document
        result = await db.execute(
            select(GeneratedDocument)
            .where(
                GeneratedDocument.id == document_id,
                GeneratedDocument.user_id == current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update view count and last accessed
        document.view_count += 1
        from datetime import datetime, timezone
        document.last_accessed = datetime.now(timezone.utc)
        await db.commit()
        
        return DocumentDetailResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    document_update: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Update document information
    """
    try:
        # Get document
        result = await db.execute(
            select(GeneratedDocument)
            .where(
                GeneratedDocument.id == document_id,
                GeneratedDocument.user_id == current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if document can be updated
        if document.status in ["signed", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update signed or completed documents"
            )
        
        # Update document
        update_data = document_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["disclosing_party", "receiving_party", "additional_parties"]:
                # Convert Pydantic models to dict for JSON storage
                if value is not None:
                    if isinstance(value, list):
                        setattr(document, field, [item.dict() if hasattr(item, 'dict') else item for item in value])
                    else:
                        setattr(document, field, value.dict() if hasattr(value, 'dict') else value)
            else:
                setattr(document, field, value)
        
        await db.commit()
        await db.refresh(document)
        
        logger.info(f"Document updated: {document.id} by user {current_user.email}")
        
        return DocumentResponse.from_orm(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update document error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document update failed"
        )


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """
    Delete a document
    """
    try:
        # Get document
        result = await db.execute(
            select(GeneratedDocument)
            .where(
                GeneratedDocument.id == document_id,
                GeneratedDocument.user_id == current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Check if document can be deleted
        if document.status in ["signed", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete signed or completed documents"
            )
        
        # Delete associated files
        if document.pdf_file_path and os.path.exists(document.pdf_file_path):
            os.remove(document.pdf_file_path)
        
        if document.docx_file_path and os.path.exists(document.docx_file_path):
            os.remove(document.docx_file_path)
        
        # Delete document
        await db.delete(document)
        await db.commit()
        
        logger.info(f"Document deleted: {document_id} by user {current_user.email}")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document deletion failed"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    format: str = Query("pdf", regex="^(pdf|docx)$", description="File format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download document file
    """
    try:
        # Get document
        result = await db.execute(
            select(GeneratedDocument)
            .where(
                GeneratedDocument.id == document_id,
                GeneratedDocument.user_id == current_user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get file path based on format
        if format == "pdf":
            file_path = document.pdf_file_path
        else:
            file_path = document.docx_file_path
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document file not found in {format} format"
            )
        
        # Update download count
        document.download_count += 1
        await db.commit()
        
        # Return file
        filename = f"{document.document_name}.{format}"
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf" if format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download document error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document download failed"
        )

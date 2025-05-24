'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Edit,
  Trash2,
  FileText,
  MoreHorizontal
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api, handleApiError, downloadBlob } from '@/lib/api'
import { formatDate, formatDateTime, getStatusColor } from '@/lib/utils'

interface Document {
  id: string
  document_name: string
  status: string
  pdf_file_path?: string
  docx_file_path?: string
  signature_status?: string
  view_count: number
  download_count: number
  created_at: string
  updated_at: string
  last_accessed?: string
}

interface DocumentsResponse {
  documents: Document[]
  total: number
  page: number
  per_page: number
  has_next: boolean
  has_prev: boolean
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [pagination, setPagination] = useState({
    page: 1,
    total: 0,
    hasNext: false,
    hasPrev: false
  })

  useEffect(() => {
    loadDocuments()
  }, [searchQuery, statusFilter, pagination.page])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      
      const params: any = {
        skip: (pagination.page - 1) * 20,
        limit: 20
      }
      
      if (searchQuery) {
        params.search = searchQuery
      }
      
      if (statusFilter) {
        params.status = statusFilter
      }
      
      const response = await api.documents.getAll(params)
      const data: DocumentsResponse = response.data
      
      setDocuments(data.documents)
      setPagination({
        page: data.page,
        total: data.total,
        hasNext: data.has_next,
        hasPrev: data.has_prev
      })
      
    } catch (error) {
      console.error('Failed to load documents:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (documentId: string, format: 'pdf' | 'docx', filename: string) => {
    try {
      const response = await api.documents.download(documentId, format)
      downloadBlob(response.data, `${filename}.${format}`)
    } catch (error) {
      console.error('Download failed:', handleApiError(error))
    }
  }

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return
    }
    
    try {
      await api.documents.delete(documentId)
      loadDocuments() // Reload the list
    } catch (error) {
      console.error('Delete failed:', handleApiError(error))
    }
  }

  const statusOptions = [
    { value: '', label: 'All Status' },
    { value: 'draft', label: 'Draft' },
    { value: 'generated', label: 'Generated' },
    { value: 'signed', label: 'Signed' },
    { value: 'completed', label: 'Completed' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600">
            Manage your generated NDA documents
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/documents/new">
            <Plus className="mr-2 h-4 w-4" />
            Create New NDA
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents List */}
      {loading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-20 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      ) : documents.length > 0 ? (
        <div className="space-y-4">
          {documents.map((document) => (
            <Card key={document.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {document.document_name}
                      </h3>
                      <Badge className={getStatusColor(document.status)}>
                        {document.status}
                      </Badge>
                      {document.signature_status && (
                        <Badge variant="outline">
                          {document.signature_status}
                        </Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span>Created {formatDate(document.created_at)}</span>
                      <span>Updated {formatDate(document.updated_at)}</span>
                      <span>{document.view_count} views</span>
                      <span>{document.download_count} downloads</span>
                      {document.last_accessed && (
                        <span>Last accessed {formatDateTime(document.last_accessed)}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="sm" asChild>
                      <Link href={`/dashboard/documents/${document.id}`}>
                        <Eye className="h-4 w-4" />
                      </Link>
                    </Button>
                    
                    {document.status !== 'draft' && (
                      <>
                        {document.pdf_file_path && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDownload(document.id, 'pdf', document.document_name)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        )}
                        
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/dashboard/documents/${document.id}/edit`}>
                            <Edit className="h-4 w-4" />
                          </Link>
                        </Button>
                      </>
                    )}
                    
                    {document.status === 'draft' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(document.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">No documents found</h3>
            <p className="text-gray-600 mb-6">
              {searchQuery || statusFilter 
                ? 'Try adjusting your search criteria or filters.'
                : 'Get started by creating your first NDA document.'
              }
            </p>
            {!searchQuery && !statusFilter && (
              <Button asChild>
                <Link href="/dashboard/documents/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First NDA
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {pagination.total > 20 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {((pagination.page - 1) * 20) + 1} to {Math.min(pagination.page * 20, pagination.total)} of {pagination.total} documents
          </p>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.hasPrev}
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.hasNext}
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

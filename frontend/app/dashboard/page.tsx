'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  FileText, 
  Plus, 
  TrendingUp, 
  Users, 
  Clock,
  ArrowRight,
  Download,
  Eye
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api, handleApiError } from '@/lib/api'
import { useUser } from '@/store/auth-store'
import { formatDate, getStatusColor } from '@/lib/utils'

interface DashboardStats {
  documents_created: number
  documents_signed: number
  templates_used: number
  storage_used_mb: number
  api_calls_this_month: number
  subscription_tier: string
  tier_limits: {
    documents_per_month: number
    storage_gb: number
    api_calls_per_month: number
  }
}

interface RecentDocument {
  id: string
  document_name: string
  status: string
  created_at: string
  template_id: string
}

export default function DashboardPage() {
  const user = useUser()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentDocuments, setRecentDocuments] = useState<RecentDocument[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load usage stats
      const statsResponse = await api.users.getUsageStats()
      setStats(statsResponse.data)
      
      // Load recent documents
      const documentsResponse = await api.documents.getAll({ limit: 5 })
      setRecentDocuments(documentsResponse.data.documents)
      
    } catch (error) {
      console.error('Failed to load dashboard data:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const quickActions = [
    {
      title: 'Create New NDA',
      description: 'Generate a new non-disclosure agreement',
      href: '/dashboard/documents/new',
      icon: Plus,
      color: 'bg-blue-500'
    },
    {
      title: 'Browse Templates',
      description: 'Explore available NDA templates',
      href: '/dashboard/templates',
      icon: FileText,
      color: 'bg-green-500'
    },
    {
      title: 'View Documents',
      description: 'Manage your generated documents',
      href: '/dashboard/documents',
      icon: Eye,
      color: 'bg-purple-500'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">
            Manage your NDAs and track your usage
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/documents/new">
            <Plus className="mr-2 h-4 w-4" />
            Create NDA
          </Link>
        </Button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Documents Created</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.documents_created}</div>
              <p className="text-xs text-muted-foreground">
                {stats.tier_limits.documents_per_month === -1 
                  ? 'Unlimited' 
                  : `${stats.tier_limits.documents_per_month} limit`
                }
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Documents Signed</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.documents_signed}</div>
              <p className="text-xs text-muted-foreground">
                {stats.documents_created > 0 
                  ? `${Math.round((stats.documents_signed / stats.documents_created) * 100)}% completion rate`
                  : 'No documents yet'
                }
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Templates Used</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.templates_used}</div>
              <p className="text-xs text-muted-foreground">
                Unique templates
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(stats.storage_used_mb / 1024).toFixed(1)} GB
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.tier_limits.storage_gb === -1 
                  ? 'Unlimited' 
                  : `${stats.tier_limits.storage_gb} GB limit`
                }
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <Card key={action.title} className="hover:shadow-md transition-shadow cursor-pointer">
              <Link href={action.href}>
                <CardContent className="p-6">
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${action.color}`}>
                      <action.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{action.title}</h3>
                      <p className="text-sm text-gray-600">{action.description}</p>
                    </div>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                  </div>
                </CardContent>
              </Link>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Documents */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
          <Button variant="outline" asChild>
            <Link href="/dashboard/documents">View All</Link>
          </Button>
        </div>
        
        {recentDocuments.length > 0 ? (
          <Card>
            <CardContent className="p-0">
              <div className="divide-y">
                {recentDocuments.map((document) => (
                  <div key={document.id} className="p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{document.document_name}</h3>
                        <p className="text-sm text-gray-600">
                          Created {formatDate(document.created_at)}
                        </p>
                      </div>
                      <div className="flex items-center space-x-3">
                        <Badge className={getStatusColor(document.status)}>
                          {document.status}
                        </Badge>
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/dashboard/documents/${document.id}`}>
                            <Eye className="h-4 w-4" />
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-8 text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No documents yet</h3>
              <p className="text-gray-600 mb-4">
                Get started by creating your first NDA document.
              </p>
              <Button asChild>
                <Link href="/dashboard/documents/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First NDA
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Subscription Status */}
      {user && (
        <Card>
          <CardHeader>
            <CardTitle>Subscription Status</CardTitle>
            <CardDescription>
              You are currently on the <strong>{user.subscription_tier}</strong> plan
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">
                  {user.subscription_tier === 'free' 
                    ? 'Upgrade to unlock more features and higher limits'
                    : 'Thank you for being a premium subscriber!'
                  }
                </p>
              </div>
              {user.subscription_tier === 'free' && (
                <Button asChild>
                  <Link href="/dashboard/billing">
                    Upgrade Plan
                  </Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

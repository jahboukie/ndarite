'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { 
  Search, 
  Filter, 
  FileText, 
  ArrowRight,
  Star,
  Clock,
  Users,
  Shield
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { api, handleApiError } from '@/lib/api'
import { useUser } from '@/store/auth-store'

interface Template {
  id: string
  name: string
  description: string
  template_type: string
  jurisdiction: string
  industry_focus?: string
  complexity_level: string
  tier_requirement: string
  version: number
  is_active: boolean
  created_at: string
  updated_at: string
}

interface Category {
  id: string
  name: string
  description?: string
  slug: string
  sort_order: number
  template_count?: number
}

export default function TemplatesPage() {
  const user = useUser()
  const [templates, setTemplates] = useState<Template[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [templateTypeFilter, setTemplateTypeFilter] = useState('')
  const [complexityFilter, setComplexityFilter] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    loadTemplates()
  }, [searchQuery, selectedCategory, templateTypeFilter, complexityFilter])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Load categories
      const categoriesResponse = await api.templates.getCategories()
      setCategories(categoriesResponse.data)
      
      // Load templates
      await loadTemplates()
      
    } catch (error) {
      console.error('Failed to load data:', handleApiError(error))
    } finally {
      setLoading(false)
    }
  }

  const loadTemplates = async () => {
    try {
      const params: any = {}
      
      if (searchQuery) {
        params.query = searchQuery
      }
      
      if (selectedCategory) {
        params.category = selectedCategory
      }
      
      if (templateTypeFilter) {
        params.template_type = templateTypeFilter
      }
      
      if (complexityFilter) {
        params.complexity = complexityFilter
      }
      
      const response = await api.templates.getAll(params)
      setTemplates(response.data.templates)
      
    } catch (error) {
      console.error('Failed to load templates:', handleApiError(error))
    }
  }

  const canAccessTemplate = (template: Template) => {
    if (!user) return false
    
    const tierHierarchy: Record<string, number> = {
      free: 0,
      starter: 1,
      professional: 2,
      enterprise: 3
    }
    
    const userLevel = tierHierarchy[user.subscription_tier] || 0
    const requiredLevel = tierHierarchy[template.tier_requirement] || 1
    
    return userLevel >= requiredLevel
  }

  const getComplexityColor = (level: string) => {
    switch (level) {
      case 'basic':
        return 'bg-green-100 text-green-800'
      case 'standard':
        return 'bg-blue-100 text-blue-800'
      case 'advanced':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'bilateral':
        return <Users className="h-4 w-4" />
      case 'unilateral':
        return <Shield className="h-4 w-4" />
      case 'multilateral':
        return <Star className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">NDA Templates</h1>
          <p className="text-gray-600">
            Choose from our library of legally-compliant NDA templates
          </p>
        </div>
      </div>

      {/* Categories */}
      {categories.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Browse by Category</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((category) => (
              <Card 
                key={category.id} 
                className="hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedCategory(category.slug)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{category.name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{category.description}</p>
                      {category.template_count !== undefined && (
                        <p className="text-xs text-gray-500 mt-2">
                          {category.template_count} templates
                        </p>
                      )}
                    </div>
                    <ArrowRight className="h-4 w-4 text-gray-400" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Categories</option>
              {categories.map((category) => (
                <option key={category.id} value={category.slug}>
                  {category.name}
                </option>
              ))}
            </select>
            
            <select
              value={templateTypeFilter}
              onChange={(e) => setTemplateTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Types</option>
              <option value="bilateral">Bilateral</option>
              <option value="unilateral">Unilateral</option>
              <option value="multilateral">Multilateral</option>
            </select>
            
            <select
              value={complexityFilter}
              onChange={(e) => setComplexityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Complexity</option>
              <option value="basic">Basic</option>
              <option value="standard">Standard</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Templates Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-48 bg-gray-200 rounded-lg"></div>
            </div>
          ))}
        </div>
      ) : templates.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => {
            const canAccess = canAccessTemplate(template)
            
            return (
              <Card 
                key={template.id} 
                className={`hover:shadow-md transition-shadow ${!canAccess ? 'opacity-75' : ''}`}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(template.template_type)}
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                    </div>
                    <Badge className={getComplexityColor(template.complexity_level)}>
                      {template.complexity_level}
                    </Badge>
                  </div>
                  <CardDescription className="text-sm">
                    {template.description}
                  </CardDescription>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Type:</span>
                      <span className="font-medium capitalize">{template.template_type}</span>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Jurisdiction:</span>
                      <span className="font-medium">{template.jurisdiction}</span>
                    </div>
                    
                    {template.industry_focus && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Industry:</span>
                        <span className="font-medium">{template.industry_focus}</span>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Required Plan:</span>
                      <Badge variant="outline" className="capitalize">
                        {template.tier_requirement}
                      </Badge>
                    </div>
                    
                    <div className="pt-3 border-t">
                      {canAccess ? (
                        <Button asChild className="w-full">
                          <Link href={`/dashboard/documents/new?template=${template.id}`}>
                            Use This Template
                          </Link>
                        </Button>
                      ) : (
                        <div className="text-center">
                          <p className="text-sm text-gray-600 mb-2">
                            Requires {template.tier_requirement} plan
                          </p>
                          <Button variant="outline" asChild className="w-full">
                            <Link href="/dashboard/billing">
                              Upgrade to Access
                            </Link>
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="p-12 text-center">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">No templates found</h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your search criteria or filters.
            </p>
            <Button 
              variant="outline"
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('')
                setTemplateTypeFilter('')
                setComplexityFilter('')
              }}
            >
              Clear Filters
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

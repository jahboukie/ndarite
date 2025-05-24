'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  CheckCircle, 
  XCircle, 
  Loader2, 
  Server, 
  Database,
  Zap,
  RefreshCw
} from 'lucide-react'
import { useBackendConnection, useTemplates, useTemplateCategories } from '@/hooks/useApi'

export default function BackendStatus() {
  const { isConnected, loading, backendInfo } = useBackendConnection()
  const { templates, loading: templatesLoading } = useTemplates()
  const { categories, loading: categoriesLoading } = useTemplateCategories()
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const refresh = () => {
    window.location.reload()
  }

  if (loading) {
    return (
      <Card className="border-blue-200 bg-blue-50/50">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
            <CardTitle className="text-lg">Connecting to Backend...</CardTitle>
          </div>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* Connection Status */}
      <Card className={`border-2 ${isConnected ? 'border-green-200 bg-green-50/50' : 'border-red-200 bg-red-50/50'}`}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {isConnected ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              <CardTitle className="text-lg">
                Backend Connection
              </CardTitle>
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? "Connected" : "Disconnected"}
              </Badge>
            </div>
            <Button variant="outline" size="sm" onClick={refresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
          <CardDescription>
            {isConnected 
              ? "Successfully connected to NDARite backend API"
              : "Unable to connect to backend. Please check if the server is running."
            }
          </CardDescription>
        </CardHeader>
        
        {isConnected && backendInfo && (
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Health Status */}
              <div className="flex items-center space-x-2">
                <Server className="h-4 w-4 text-green-600" />
                <div>
                  <div className="font-medium text-sm">Service</div>
                  <div className="text-xs text-gray-600">
                    {backendInfo.health?.service || 'NDARite Backend'}
                  </div>
                </div>
              </div>
              
              {/* Database Status */}
              <div className="flex items-center space-x-2">
                <Database className="h-4 w-4 text-blue-600" />
                <div>
                  <div className="font-medium text-sm">Database</div>
                  <div className="text-xs text-gray-600">
                    {backendInfo.status?.database || 'Connected'}
                  </div>
                </div>
              </div>
              
              {/* Environment */}
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4 text-purple-600" />
                <div>
                  <div className="font-medium text-sm">Environment</div>
                  <div className="text-xs text-gray-600">
                    {backendInfo.status?.environment || 'Development'}
                  </div>
                </div>
              </div>
            </div>
            
            {/* API Features */}
            {backendInfo.status?.features && (
              <div className="mt-4">
                <div className="font-medium text-sm mb-2">Available Features:</div>
                <div className="flex flex-wrap gap-1">
                  {backendInfo.status.features.map((feature: string, index: number) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        )}
      </Card>

      {/* Live Data Display */}
      {isConnected && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Templates Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Live Templates</span>
              </CardTitle>
              <CardDescription>
                Real-time data from backend API
              </CardDescription>
            </CardHeader>
            <CardContent>
              {templatesLoading ? (
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Loading templates...</span>
                </div>
              ) : (
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {templates.length}
                  </div>
                  <div className="text-sm text-gray-600">
                    Available NDA Templates
                  </div>
                  {templates.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {templates.slice(0, 3).map((template: any, index: number) => (
                        <div key={index} className="text-xs text-gray-500">
                          • {template.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Categories Status */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Live Categories</span>
              </CardTitle>
              <CardDescription>
                Template categories from API
              </CardDescription>
            </CardHeader>
            <CardContent>
              {categoriesLoading ? (
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Loading categories...</span>
                </div>
              ) : (
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {categories.length}
                  </div>
                  <div className="text-sm text-gray-600">
                    Template Categories
                  </div>
                  {categories.length > 0 && (
                    <div className="mt-2 space-y-1">
                      {categories.slice(0, 3).map((category: any, index: number) => (
                        <div key={index} className="text-xs text-gray-500">
                          • {category.name}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Connection Details */}
      <div className="text-xs text-gray-500 text-center">
        Last updated: {lastUpdated.toLocaleTimeString()} | 
        Backend: http://localhost:8000 | 
        Frontend: http://localhost:3000
      </div>
    </div>
  )
}

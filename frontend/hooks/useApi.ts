/**
 * Custom React hooks for NDARite API integration
 */

import { useState, useEffect } from 'react';
import { api, handleApiError } from '@/lib/api';

// Generic API hook for loading states
export function useApiCall<T>(
  apiFunction: () => Promise<any>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await apiFunction();
        
        if (isMounted) {
          setData(response.data || response);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(handleApiError(err));
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, dependencies);

  return { data, loading, error, refetch: () => setLoading(true) };
}

// Hook for backend status
export function useBackendStatus() {
  return useApiCall(() => api.templates.getAll(), []);
}

// Hook for templates
export function useTemplates() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.templates.getAll();
        setTemplates(response.data?.templates || []);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, []);

  return { templates, loading, error };
}

// Hook for template categories
export function useTemplateCategories() {
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.templates.getCategories();
        setCategories(response.data || []);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  return { categories, loading, error };
}

// Hook for backend connection test
export function useBackendConnection() {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [backendInfo, setBackendInfo] = useState<any>(null);

  useEffect(() => {
    const testConnection = async () => {
      try {
        setLoading(true);
        
        // Test basic connection
        const healthResponse = await fetch('http://localhost:8000/health');
        const healthData = await healthResponse.json();
        
        // Test API status
        const statusResponse = await fetch('http://localhost:8000/api/v1/status');
        const statusData = await statusResponse.json();
        
        setIsConnected(true);
        setBackendInfo({
          health: healthData,
          status: statusData
        });
      } catch (err) {
        setIsConnected(false);
        console.error('Backend connection failed:', err);
      } finally {
        setLoading(false);
      }
    };

    testConnection();
  }, []);

  return { isConnected, loading, backendInfo };
}

// Hook for documents
export function useDocuments() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.documents.getAll();
        setDocuments(response.data?.documents || []);
      } catch (err) {
        setError(handleApiError(err));
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  return { documents, loading, error };
}

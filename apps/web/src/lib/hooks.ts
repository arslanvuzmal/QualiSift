'use client';

import useSWR from 'swr';
import type { Lead, CriteriaConfig, DigestRun } from './types';
import { apiClient } from './api';

// The API client already unwraps StandardResponse.data, so these hooks read
// the unwrapped payloads directly.

interface LeadListData {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
}

export function useLeads(page = 1, pageSize = 20) {
  const { data, error, isLoading, mutate } = useSWR<LeadListData>(
    `/api/v1/leads?page=${page}&page_size=${pageSize}`,
    (url: string) => apiClient.get<LeadListData>(url),
    { refreshInterval: 5000 } // live-update as background scoring completes
  );

  const size = data?.page_size ?? pageSize;
  const total = data?.total ?? 0;

  return {
    leads: data?.items ?? [],
    meta: {
      total,
      page: data?.page ?? page,
      page_size: size,
      total_pages: Math.max(1, Math.ceil(total / size)),
    },
    isLoading,
    isError: error,
    mutate,
  };
}

export function useLead(id: string | null) {
  const { data, error, isLoading, mutate } = useSWR<Lead>(
    id ? `/api/v1/leads/${id}` : null,
    (url: string) => apiClient.get<Lead>(url),
    { refreshInterval: 4000 }
  );
  return { lead: data, isLoading, isError: error, mutate };
}

export function useCriteria() {
  const { data, error, isLoading, mutate } = useSWR<CriteriaConfig[]>(
    '/api/v1/criteria?active_only=false',
    (url: string) => apiClient.get<CriteriaConfig[]>(url)
  );
  return { criteria: data ?? [], isLoading, isError: error, mutate };
}

export function useDigestHistory() {
  const { data, error, isLoading, mutate } = useSWR<DigestRun[]>(
    '/api/v1/digest/history',
    (url: string) => apiClient.get<DigestRun[]>(url)
  );
  return { digestRuns: data ?? [], isLoading, isError: error, mutate };
}

export function useHealth() {
  const { data, error, isLoading } = useSWR<unknown>(
    '/api/v1/health',
    (url: string) => apiClient.get(url)
  );
  return { health: data, isLoading, isError: error };
}

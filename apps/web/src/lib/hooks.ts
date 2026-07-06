'use client';

import useSWR from 'swr';
import type { Lead, CriteriaConfig, DigestRun, StandardResponse } from './types';
import { apiClient } from './api';

export function useLeads(page = 1, perPage = 20) {
  const { data, error, isLoading, mutate } = useSWR<StandardResponse<{ data: Lead[]; meta: unknown }>>(
    `/api/v1/leads?page=${page}&per_page=${perPage}`,
    (url) => apiClient.get(url)
  );

  return {
    leads: data?.data?.data || [],
    meta: data?.data?.meta,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useCriteria() {
  const { data, error, isLoading, mutate } = useSWR<StandardResponse<CriteriaConfig[]>>(
    '/api/v1/criteria',
    (url) => apiClient.get(url)
  );

  return {
    criteria: data?.data || [],
    isLoading,
    isError: error,
    mutate,
  };
}

export function useDigestHistory() {
  const { data, error, isLoading, mutate } = useSWR<StandardResponse<DigestRun[]>>(
    '/api/v1/digest/history',
    (url) => apiClient.get(url)
  );

  return {
    digestRuns: data?.data || [],
    isLoading,
    isError: error,
    mutate,
  };
}

export function useHealth() {
  const { data, error, isLoading } = useSWR<StandardResponse<unknown>>(
    '/api/v1/health',
    (url) => apiClient.get(url)
  );

  return {
    health: data?.data,
    isLoading,
    isError: error,
  };
}

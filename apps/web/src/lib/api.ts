import type { StandardResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      response.status,
      errorData.error || errorData.detail || 'An error occurred',
      errorData
    );
  }

  const result: StandardResponse<T> = await response.json();
  
  if (!result.success) {
    throw new ApiError(response.status, result.error || 'Request failed', result);
  }

  return result.data;
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  return handleResponse<T>(response);
}

export const apiClient = {
  async get<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint, { method: 'GET' });
  },

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  async delete<T>(endpoint: string): Promise<T> {
    return request<T>(endpoint, { method: 'DELETE' });
  },
};

// API Functions
export async function fetchLeads(page = 1, pageSize = 20) {
  return apiClient.get<{ items: unknown[]; total: number; page: number; page_size: number }>(
    `/api/v1/leads?page=${page}&page_size=${pageSize}`
  );
}

export async function fetchLead(id: string) {
  return apiClient.get<StandardResponse<unknown>>(`/api/v1/leads/${id}`);
}

export async function createLead(data: unknown) {
  return apiClient.post<StandardResponse<unknown>>('/api/v1/leads', data);
}

export async function scoreLead(id: string) {
  return apiClient.post<StandardResponse<unknown>>(`/api/v1/leads/${id}/score`);
}

export async function fetchCriteria() {
  return apiClient.get<StandardResponse<unknown[]>>('/api/v1/criteria');
}

export async function updateCriteria(id: string, data: unknown) {
  return apiClient.put<StandardResponse<unknown>>(`/api/v1/criteria/${id}`, data);
}

export async function generateDigest() {
  return apiClient.post<StandardResponse<unknown>>('/api/v1/digest/generate');
}

export async function fetchDigestHistory() {
  return apiClient.get<StandardResponse<unknown[]>>('/api/v1/digest/history');
}

export async function checkHealth() {
  return apiClient.get<StandardResponse<unknown>>('/api/v1/health');
}

export async function saveConfig(data: unknown) {
  return apiClient.post<StandardResponse<unknown>>('/api/v1/config', data);
}

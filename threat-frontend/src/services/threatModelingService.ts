/**
 * API service for threat modeling - threat-modeling-api (orchestrator).
 */

import axios from 'axios';
import type {
  AnalysisCreateResponse,
  AnalysisListItem,
  AnalysisDetailResponse,
  AnalysisStatus,
  NotificationsUnreadResponse,
} from '../types/analysis';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// Create analysis (async - returns immediately)
export async function createAnalysis(file: File): Promise<AnalysisCreateResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<AnalysisCreateResponse>('/analyses', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

// List analyses (paginated response from fastapi-pagination)
interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export async function listAnalyses(status?: AnalysisStatus): Promise<AnalysisListItem[]> {
  const params: Record<string, string | number> = { size: 100 };
  if (status) params.status = status;
  const response = await api.get<PaginatedResponse<AnalysisListItem>>('/analyses', { params });
  return response.data?.items ?? [];
}

// Get analysis detail
export async function getAnalysis(id: string): Promise<AnalysisDetailResponse> {
  const response = await api.get<AnalysisDetailResponse>(`/analyses/${id}`);
  return response.data;
}

// Get analysis image URL (relative)
export function getAnalysisImageUrl(id: string): string {
  return `${API_BASE_URL}/analyses/${id}/image`;
}

// Get processing logs
export async function getAnalysisLogs(id: string): Promise<{ logs: string }> {
  const response = await api.get<{ logs: string }>(`/analyses/${id}/logs`);
  return response.data;
}

// Delete analysis (irreversible; stops processing if running)
export async function deleteAnalysis(id: string): Promise<void> {
  await api.delete(`/analyses/${id}`);
}

// Notifications
export async function getUnreadNotifications(): Promise<NotificationsUnreadResponse> {
  const response = await api.get<NotificationsUnreadResponse>('/notifications/unread');
  return response.data;
}

export async function markNotificationRead(id: string): Promise<void> {
  await api.post(`/notifications/${id}/read`);
}


export async function checkHealth(): Promise<boolean> {
  try {
    const response = await api.get('/health');
    return response.data?.status === 'healthy';
  } catch {
    return false;
  }
}

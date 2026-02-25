/**
 * API service for threat modeling - threat-modeling-api (orchestrator).
 */

import axios, { AxiosError } from 'axios';
import type {
  AnalysisResponse,
  AnalysisError,
  AnalysisCreateResponse,
  AnalysisListItem,
  AnalysisDetailResponse,
  AnalysisStatus,
  NotificationsUnreadResponse,
} from '../types/analysis';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

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

// List analyses
export async function listAnalyses(status?: AnalysisStatus): Promise<AnalysisListItem[]> {
  const params = status ? { status_filter: status } : {};
  const response = await api.get<AnalysisListItem[]>('/analyses', { params });
  return Array.isArray(response.data) ? response.data : [];
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

// Notifications
export async function getUnreadNotifications(): Promise<NotificationsUnreadResponse> {
  const response = await api.get<NotificationsUnreadResponse>('/notifications/unread');
  return response.data;
}

export async function markNotificationRead(id: string): Promise<void> {
  await api.post(`/notifications/${id}/read`);
}

// Legacy sync analyze (calls threat-analyzer directly - kept for fallback or dev)
export interface AnalyzeResult {
  success: true;
  data: AnalysisResponse;
}

export interface AnalyzeErrorResult {
  success: false;
  error: string;
  details?: Record<string, unknown>;
}

export type AnalyzeResponse = AnalyzeResult | AnalyzeErrorResult;

export async function analyzeDiagramSync(
  file: File,
  confidence?: number,
  iou?: number
): Promise<AnalyzeResponse> {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (confidence !== undefined) formData.append('confidence', String(confidence));
    if (iou !== undefined) formData.append('iou', String(iou));

    const response = await api.post<AnalysisResponse>(
      '/threat-model/analyze',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 }
    );
    return { success: true, data: response.data };
  } catch (err) {
    const error = err as AxiosError<AnalysisError>;
    if (error.response?.data) {
      return {
        success: false,
        error: error.response.data.error || 'Analysis failed',
        details: error.response.data.details,
      };
    }
    if (error.code === 'ECONNABORTED') {
      return {
        success: false,
        error: 'Request timed out. The analysis is taking longer than expected.',
      };
    }
    return {
      success: false,
      error: error.message || 'An unexpected error occurred',
    };
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await api.get('/health');
    return response.data?.status === 'healthy';
  } catch {
    return false;
  }
}

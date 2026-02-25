import { useState, useCallback } from 'react';
import type { AnalysisResponse } from '../types/analysis';
import { analyzeDiagramSync } from '../services/threatModelingService';

export interface UseThreatAnalysisState {
  file: File | null;
  analysis: AnalysisResponse | null;
  loading: boolean;
  error: string | null;
  confidence: number;
  iou: number;
  sidebarOpen: boolean;
}

export interface UseThreatAnalysisActions {
  setFile: (file: File | null) => void;
  runAnalysis: () => Promise<void>;
  setConfidence: (v: number) => void;
  setIou: (v: number) => void;
  setSidebarOpen: (v: boolean) => void;
  reset: () => void;
}

export type UseThreatAnalysisReturn = UseThreatAnalysisState & UseThreatAnalysisActions;

export function useThreatAnalysis(): UseThreatAnalysisReturn {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0.35);
  const [iou, setIou] = useState(0.45);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const runAnalysis = useCallback(async () => {
    if (!file) {
      setError('Selecione um arquivo primeiro');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await analyzeDiagramSync(file, confidence, iou);

      if (result.success) {
        setAnalysis(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      setError('Falha na análise. Tente novamente.');
    } finally {
      setLoading(false);
    }
  }, [file, confidence, iou]);

  const reset = useCallback(() => {
    setFile(null);
    setAnalysis(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    file,
    analysis,
    loading,
    error,
    confidence,
    iou,
    sidebarOpen,
    setFile,
    runAnalysis,
    setConfidence,
    setIou,
    setSidebarOpen,
    reset,
  };
}

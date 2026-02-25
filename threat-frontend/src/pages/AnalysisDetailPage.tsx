import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Loader2, ArrowLeft } from 'lucide-react';
import {
  getAnalysis,
  getAnalysisImageUrl,
  getAnalysisLogs,
} from '../services/threatModelingService';
import { ResultsSection } from '../components';
import type { AnalysisDetailResponse } from '../types/analysis';

const POLL_INTERVAL_MS = 5000;

export function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<AnalysisDetailResponse | null>(null);
  const [logs, setLogs] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchAnalysis = async () => {
    if (!id) return;
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
      setError(null);
      return data.status;
    } catch (e) {
      setError('Falha ao carregar análise');
      return null;
    }
  };

  const fetchLogs = async () => {
    if (!id) return;
    try {
      const { logs: l } = await getAnalysisLogs(id);
      setLogs(l || '');
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (!id) return;
    let mounted = true;

    const load = async () => {
      setLoading(true);
      const status = await fetchAnalysis();
      if (mounted) setLoading(false);
      if (status === 'PROCESSANDO' && mounted) {
        await fetchLogs();
        pollRef.current = setInterval(async () => {
          if (!mounted) return;
          const s = await fetchAnalysis();
          await fetchLogs();
          if (s !== 'PROCESSANDO') {
            if (pollRef.current) clearInterval(pollRef.current);
          }
        }, POLL_INTERVAL_MS);
      }
    };
    load();
    return () => {
      mounted = false;
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [id]);

  if (!id) return null;
  if (loading && !analysis) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
      </div>
    );
  }
  if (error || !analysis) {
    return (
      <div className="text-center py-16">
        <p className="text-red-400 mb-4">{error || 'Análise não encontrada'}</p>
        <Link to="/analyses" className="text-indigo-400 hover:underline">
          Voltar para listagem
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Link
        to="/analyses"
        className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar
      </Link>

      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          {analysis.code}
          <span className="ml-2 text-sm font-normal text-gray-500">
            {new Date(analysis.created_at).toLocaleString('pt-BR')}
          </span>
        </h1>
        <span
          className={`px-3 py-1 rounded-full text-sm ${
            analysis.status === 'PROCESSANDO'
              ? 'bg-amber-600/30 text-amber-300 animate-pulse'
              : analysis.status === 'ANALISADO'
                ? 'bg-emerald-600/30 text-emerald-300'
                : analysis.status === 'FALHOU'
                  ? 'bg-red-600/30 text-red-300'
                  : 'bg-slate-600/50 text-slate-300'
          }`}
        >
          {analysis.status}
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="glass-card">
            <h2 className="text-lg font-semibold mb-4">Diagrama</h2>
            <div className="rounded-lg overflow-hidden border border-white/10">
              <img
                src={getAnalysisImageUrl(analysis.id)}
                alt={analysis.code}
                className="w-full object-contain bg-slate-900/50"
              />
            </div>
          </div>
        </div>
        <div className="lg:col-span-2 space-y-6">
          {analysis.status === 'PROCESSANDO' && (
            <div className="glass-card">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin" /> Logs
              </h2>
              <pre className="text-xs text-gray-400 whitespace-pre-wrap max-h-48 overflow-y-auto font-mono bg-black/30 p-4 rounded">
                {logs || 'Aguardando logs...'}
              </pre>
            </div>
          )}

          {analysis.status === 'FALHOU' && analysis.error_message && (
            <div className="glass-card border-red-500/30">
              <h2 className="text-lg font-semibold text-red-400 mb-2">Erro</h2>
              <p className="text-sm text-gray-400">{analysis.error_message}</p>
            </div>
          )}

          {analysis.status === 'ANALISADO' && analysis.result && (
            <ResultsSection analysis={analysis.result} />
          )}
        </div>
      </div>
    </div>
  );
}

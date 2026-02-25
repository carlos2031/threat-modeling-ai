import { useEffect, useState, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Loader2, ArrowLeft, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import {
  getAnalysis,
  getAnalysisImageUrl,
  getAnalysisLogs,
} from '../services/threatModelingService';
import { ResultsSection } from '../components';
import type { AnalysisDetailResponse } from '../types/analysis';

const POLL_INTERVAL_MS = 5000;

const STATUS_DISPLAY = {
  EM_ABERTO: { icon: Clock, label: 'Em Aberto', className: 'bg-slate-600/50 text-slate-300' },
  PROCESSANDO: { icon: Loader2, label: 'Processando', className: 'bg-amber-500/20 text-amber-300' },
  ANALISADO: { icon: CheckCircle, label: 'Analisado', className: 'bg-emerald-500/20 text-emerald-300' },
  FALHOU: { icon: XCircle, label: 'Falhou', className: 'bg-red-500/20 text-red-300' },
} as const;

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
    } catch {
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
      /* ignore */
    }
  };

  useEffect(() => {
    if (!id) return;
    let mounted = true;

    const load = async () => {
      setLoading(true);
      const status = await fetchAnalysis();
      if (mounted) setLoading(false);

      if ((status === 'PROCESSANDO' || status === 'EM_ABERTO') && mounted) {
        await fetchLogs();
        pollRef.current = setInterval(async () => {
          if (!mounted) return;
          const s = await fetchAnalysis();
          await fetchLogs();
          if (s && s !== 'PROCESSANDO' && s !== 'EM_ABERTO') {
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
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-20 space-y-4">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto" />
        <p className="text-red-400">{error || 'Análise não encontrada'}</p>
        <Link to="/analyses" className="inline-block text-indigo-400 hover:text-indigo-300 text-sm">
          ← Voltar para listagem
        </Link>
      </div>
    );
  }

  const statusInfo = STATUS_DISPLAY[analysis.status] ?? STATUS_DISPLAY.EM_ABERTO;
  const StatusIcon = statusInfo.icon;
  const isProcessing = analysis.status === 'PROCESSANDO' || analysis.status === 'EM_ABERTO';

  return (
    <div className="space-y-6">
      <Link
        to="/analyses"
        className="inline-flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Voltar
      </Link>

      <div className="glass-card !p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold font-mono text-indigo-400">{analysis.code}</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Criada em {new Date(analysis.created_at).toLocaleString('pt-BR')}
              {analysis.finished_at && (
                <> · Concluída em {new Date(analysis.finished_at).toLocaleString('pt-BR')}</>
              )}
            </p>
          </div>
          <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium self-start ${
              statusInfo.className
            } ${isProcessing ? 'animate-pulse' : ''}`}
          >
            <StatusIcon className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
            {statusInfo.label}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="glass-card !p-4 sticky top-24">
            <h2 className="text-sm font-semibold text-gray-300 mb-3">Diagrama</h2>
            <div className="rounded-lg overflow-hidden border border-white/10 bg-slate-900/50">
              <img
                src={getAnalysisImageUrl(analysis.id)}
                alt={analysis.code}
                className="w-full object-contain"
              />
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {isProcessing && (
            <div className="glass-card !p-5">
              <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                Processando análise...
              </h2>
              <pre className="text-xs text-gray-400 whitespace-pre-wrap max-h-48 overflow-y-auto font-mono bg-black/30 p-3 rounded-lg">
                {logs || 'Aguardando início do processamento...'}
              </pre>
            </div>
          )}

          {analysis.status === 'FALHOU' && analysis.error_message && (
            <div className="glass-card !p-5 border-red-500/30">
              <h2 className="text-sm font-semibold text-red-400 mb-2 flex items-center gap-2">
                <XCircle className="w-4 h-4" /> Erro no processamento
              </h2>
              <p className="text-sm text-gray-400">{analysis.error_message}</p>
            </div>
          )}

          {analysis.status === 'ANALISADO' && analysis.result && (
            <ResultsSection analysis={analysis.result} />
          )}

          {analysis.status === 'ANALISADO' && !analysis.result && (
            <div className="glass-card !p-5">
              <p className="text-gray-400 text-center py-4">
                Análise concluída, mas sem resultados detalhados.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

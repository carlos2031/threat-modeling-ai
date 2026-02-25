import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import { listAnalyses, getAnalysisImageUrl } from '../services/threatModelingService';
import type { AnalysisListItem, AnalysisStatus } from '../types/analysis';
import { RISK_LEVEL_CONFIG } from '../constants/riskLevels';

const STATUS_CONFIG: Record<
  AnalysisStatus,
  { icon: typeof Loader2; label: string; className: string }
> = {
  EM_ABERTO: { icon: Clock, label: 'Em aberto', className: 'bg-slate-600/50 text-slate-300' },
  PROCESSANDO: {
    icon: Loader2,
    label: 'Processando',
    className: 'bg-amber-600/30 text-amber-300',
  },
  ANALISADO: { icon: CheckCircle, label: 'Analisado', className: 'bg-emerald-600/30 text-emerald-300' },
  FALHOU: { icon: XCircle, label: 'Falhou', className: 'bg-red-600/30 text-red-300' },
};

export function AnalysesListPage() {
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAnalyses()
      .then(setAnalyses)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Análises</h1>
      {analyses.length === 0 ? (
        <p className="text-gray-400 text-center py-16">Nenhuma análise ainda. Envie um diagrama na página inicial.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {analyses.map((a) => {
            const statusCfg = STATUS_CONFIG[a.status];
            const StatusIcon = statusCfg.icon;
            const riskCfg = a.risk_level ? RISK_LEVEL_CONFIG[a.risk_level] : null;

            return (
              <Link
                key={a.id}
                to={`/analyses/${a.id}`}
                className="glass-card block hover:border-indigo-500/50 transition-colors"
              >
                <div className="aspect-video rounded-lg overflow-hidden bg-slate-900/50 mb-4 flex items-center justify-center">
                  <img
                    src={getAnalysisImageUrl(a.id)}
                    alt={a.code}
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-mono text-sm text-indigo-400">{a.code}</span>
                  <span
                    className={`flex items-center gap-1 px-2 py-0.5 rounded text-xs ${
                      statusCfg.className
                    } ${a.status === 'PROCESSANDO' ? 'animate-pulse' : ''}`}
                  >
                    {a.status === 'PROCESSANDO' && <StatusIcon className="w-3 h-3 animate-spin" />}
                    {a.status !== 'PROCESSANDO' && <StatusIcon className="w-3 h-3" />}
                    {statusCfg.label}
                  </span>
                </div>
                <p className="text-xs text-gray-500">
                  {new Date(a.created_at).toLocaleString('pt-BR')}
                </p>
                {a.status === 'ANALISADO' && riskCfg && (
                  <div className="mt-2 flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${riskCfg.bgColor} ${riskCfg.textColor}`}
                    >
                      {a.risk_level} ({a.risk_score?.toFixed(1)}/10)
                    </span>
                    <span className="text-xs text-gray-500">{a.threat_count} ameaças</span>
                  </div>
                )}
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

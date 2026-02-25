import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle, Clock, AlertTriangle, LayoutList } from 'lucide-react';
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
    className: 'bg-amber-500/20 text-amber-300',
  },
  ANALISADO: { icon: CheckCircle, label: 'Analisado', className: 'bg-emerald-500/20 text-emerald-300' },
  FALHOU: { icon: XCircle, label: 'Falhou', className: 'bg-red-500/20 text-red-300' },
};

export function AnalysesListPage() {
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAnalyses = () => {
    setLoading(true);
    listAnalyses()
      .then(setAnalyses)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAnalyses();
    const interval = setInterval(fetchAnalyses, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading && analyses.length === 0) {
    return (
      <div className="flex items-center justify-center py-24">
        <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <LayoutList className="w-6 h-6 text-indigo-400" />
          Análises
        </h1>
        <span className="text-sm text-gray-500">{analyses.length} análise{analyses.length !== 1 ? 's' : ''}</span>
      </div>

      {analyses.length === 0 ? (
        <div className="text-center py-20 space-y-4">
          <AlertTriangle className="w-12 h-12 text-gray-600 mx-auto" />
          <p className="text-gray-400">Nenhuma análise ainda.</p>
          <Link to="/" className="inline-block text-indigo-400 hover:text-indigo-300 text-sm">
            Enviar um diagrama →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
          {analyses.map((a) => {
            const statusCfg = STATUS_CONFIG[a.status];
            const StatusIcon = statusCfg.icon;
            const riskCfg = a.risk_level ? RISK_LEVEL_CONFIG[a.risk_level] : null;

            return (
              <Link
                key={a.id}
                to={`/analyses/${a.id}`}
                className="group glass-card !p-0 overflow-hidden hover:border-indigo-500/40 transition-all duration-200 hover:-translate-y-0.5"
              >
                <div className="aspect-video bg-slate-900/80 flex items-center justify-center overflow-hidden">
                  <img
                    src={getAnalysisImageUrl(a.id)}
                    alt={a.code}
                    className="w-full h-full object-contain p-2 opacity-80 group-hover:opacity-100 transition-opacity"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>

                <div className="p-4 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-sm text-indigo-400 font-medium">{a.code}</span>
                    <span
                      className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium ${
                        statusCfg.className
                      } ${a.status === 'PROCESSANDO' ? 'animate-pulse' : ''}`}
                    >
                      <StatusIcon className={`w-3 h-3 ${a.status === 'PROCESSANDO' ? 'animate-spin' : ''}`} />
                      {statusCfg.label}
                    </span>
                  </div>

                  <p className="text-xs text-gray-500">
                    {new Date(a.created_at).toLocaleString('pt-BR')}
                  </p>

                  {a.status === 'ANALISADO' && riskCfg && (
                    <div className="flex items-center gap-2 pt-1">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[11px] font-medium ${riskCfg.bgColor} ${riskCfg.textColor}`}
                      >
                        {a.risk_level} ({a.risk_score?.toFixed(1)}/10)
                      </span>
                      <span className="text-xs text-gray-500">{a.threat_count} ameaça{(a.threat_count ?? 0) !== 1 ? 's' : ''}</span>
                    </div>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

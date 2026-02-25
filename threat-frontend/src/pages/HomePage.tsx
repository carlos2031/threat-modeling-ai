import { UploadSection, ErrorMessage } from '../components';
import { useCreateAnalysis } from '../hooks/useCreateAnalysis';
import { Shield, Zap, BarChart3 } from 'lucide-react';

export function HomePage() {
  const { file, loading, error, setFile, createAnalysis } = useCreateAnalysis();

  return (
    <div className="max-w-4xl mx-auto space-y-10">
      <div className="text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          Análise de Ameaças em Diagramas
        </h1>
        <p className="text-gray-400 max-w-2xl mx-auto">
          Envie um diagrama de arquitetura e receba uma análise completa de segurança
          usando metodologia STRIDE/DREAD com inteligência artificial.
        </p>
      </div>

      <div className="max-w-2xl mx-auto">
        <UploadSection
          file={file}
          loading={loading}
          onFileSelect={setFile}
          onAnalyze={createAnalysis}
          submitLabel="Enviar para Análise"
        />
        {error && <ErrorMessage message={error} onDismiss={() => setFile(null)} />}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <FeatureCard
          icon={<Shield className="w-6 h-6 text-indigo-400" />}
          title="STRIDE"
          description="Identifica ameaças usando as 6 categorias STRIDE automaticamente."
        />
        <FeatureCard
          icon={<BarChart3 className="w-6 h-6 text-purple-400" />}
          title="DREAD"
          description="Prioriza riscos com pontuação detalhada em 5 dimensões."
        />
        <FeatureCard
          icon={<Zap className="w-6 h-6 text-amber-400" />}
          title="Multimodal AI"
          description="Análise por LLMs com visão computacional e fallback automático."
        />
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="glass-card !p-5 flex items-start gap-3">
      <div className="shrink-0 mt-0.5">{icon}</div>
      <div>
        <h3 className="font-semibold text-sm mb-1">{title}</h3>
        <p className="text-xs text-gray-400 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

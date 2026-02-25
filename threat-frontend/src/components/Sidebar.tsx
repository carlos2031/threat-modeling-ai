import { Shield, Brain, FileSearch } from 'lucide-react';

interface SidebarProps {
  onClose?: () => void;
  isMobile?: boolean;
  standalone?: boolean;
}

export function Sidebar({
  onClose,
  isMobile = false,
}: SidebarProps) {
  return (
    <aside
      className={`space-y-6 ${
        isMobile
          ? 'fixed inset-y-0 left-0 z-50 w-72 p-6 overflow-y-auto bg-slate-900/95 backdrop-blur-xl border-r border-white/10'
          : 'w-64 shrink-0 p-5'
      }`}
    >
      {isMobile && onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white"
          aria-label="Close"
        >
          ×
        </button>
      )}

      <div>
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">
          Como funciona
        </h2>
        <div className="space-y-4">
          <InfoItem
            icon={<FileSearch className="w-4 h-4 text-indigo-400" />}
            title="1. Upload"
            description="Envie um diagrama de arquitetura (PNG, JPEG, WebP)."
          />
          <InfoItem
            icon={<Brain className="w-4 h-4 text-purple-400" />}
            title="2. Análise AI"
            description="LLMs multimodais identificam componentes e conexões."
          />
          <InfoItem
            icon={<Shield className="w-4 h-4 text-emerald-400" />}
            title="3. Relatório"
            description="Ameaças STRIDE e priorização DREAD são geradas."
          />
        </div>
      </div>

      <div className="pt-4 border-t border-white/10">
        <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
          Tecnologias
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {['Gemini', 'OpenAI', 'STRIDE', 'DREAD', 'RAG', 'LangChain'].map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 bg-white/5 border border-white/10 rounded text-xs text-gray-400"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </aside>
  );
}

function InfoItem({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="flex items-start gap-2.5">
      <div className="mt-0.5 shrink-0">{icon}</div>
      <div>
        <p className="text-sm font-medium text-gray-200">{title}</p>
        <p className="text-xs text-gray-500 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

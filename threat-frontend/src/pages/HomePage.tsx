import { UploadSection, ErrorMessage, Sidebar } from '../components';
import { useCreateAnalysis } from '../hooks/useCreateAnalysis';

export function HomePage() {
  const { file, loading, error, setFile, createAnalysis } = useCreateAnalysis();

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
      <div className="space-y-6">
        <UploadSection
          file={file}
          loading={loading}
          onFileSelect={setFile}
          onAnalyze={createAnalysis}
          submitLabel="Enviar para Análise"
        />
        {error && <ErrorMessage message={error} onDismiss={() => setFile(null)} />}
      </div>
      <div className="hidden xl:block">
        <Sidebar standalone />
      </div>
    </div>
  );
}

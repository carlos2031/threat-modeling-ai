import { useCallback, useRef, useState } from 'react';
import { Upload, ImageIcon, X, Loader2 } from 'lucide-react';

interface UploadSectionProps {
  file: File | null;
  loading: boolean;
  onFileSelect: (file: File | null) => void;
  onAnalyze: () => void;
  submitLabel?: string;
}

export function UploadSection({
  file,
  loading,
  onFileSelect,
  onAnalyze,
  submitLabel = 'Enviar para Análise',
}: UploadSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const prevUrlRef = useRef<string | null>(null);

  const setFileAndPreview = useCallback(
    (f: File | null) => {
      onFileSelect(f);
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      prevUrlRef.current = f ? URL.createObjectURL(f) : null;
      setPreviewUrl(prevUrlRef.current);
    },
    [onFileSelect],
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setFileAndPreview(e.target.files?.[0] || null);
    },
    [setFileAndPreview],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragOver(false);
      const droppedFile = e.dataTransfer.files?.[0] || null;
      if (droppedFile?.type.startsWith('image/')) {
        setFileAndPreview(droppedFile);
      }
    },
    [setFileAndPreview],
  );

  const handleClear = useCallback(() => {
    setFileAndPreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, [setFileAndPreview]);

  return (
    <section className="glass-card">
      <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Upload className="w-5 h-5 text-indigo-400" />
        Upload de Diagrama
      </h2>

      <div
        className={`relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 min-h-[140px] flex items-center justify-center ${
          dragOver
            ? 'border-indigo-400 bg-indigo-500/10'
            : file
              ? 'border-indigo-500/40 bg-indigo-500/5'
              : 'border-slate-600 hover:border-indigo-500/50 hover:bg-white/[0.02]'
        }`}
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileChange}
        />

        {file ? (
          <div className="space-y-1">
            <ImageIcon className="w-8 h-8 text-indigo-400 mx-auto" />
            <p className="text-indigo-300 font-medium text-sm">{file.name}</p>
            <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="w-8 h-8 text-gray-500 mx-auto" />
            <p className="text-gray-400 text-sm">
              Clique ou arraste a imagem do diagrama
            </p>
            <p className="text-xs text-gray-600">PNG, JPEG ou WebP</p>
          </div>
        )}
      </div>

      {previewUrl && (
        <div className="relative mt-4 rounded-xl overflow-hidden border border-white/10">
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full max-h-56 object-contain bg-slate-900/50"
          />
          {!loading && (
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); handleClear(); }}
              className="absolute top-2 right-2 p-1.5 bg-slate-900/80 hover:bg-red-500/80 rounded-lg transition-colors"
              aria-label="Remover imagem"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          {loading && (
            <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center">
              <div className="flex flex-col items-center gap-2">
                <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                <span className="text-sm text-indigo-300">Enviando...</span>
              </div>
            </div>
          )}
        </div>
      )}

      <button
        className="btn-primary w-full mt-5"
        disabled={!file || loading}
        onClick={onAnalyze}
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Enviando...
          </span>
        ) : (
          submitLabel
        )}
      </button>
    </section>
  );
}

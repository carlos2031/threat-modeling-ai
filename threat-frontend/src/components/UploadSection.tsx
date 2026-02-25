import { useCallback, useRef, useState } from 'react';
import { Upload, Scan } from 'lucide-react';

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
  submitLabel = 'Analyze',
}: UploadSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const prevUrlRef = useRef<string | null>(null);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0] || null;
      onFileSelect(selectedFile);
      if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
      prevUrlRef.current = selectedFile ? URL.createObjectURL(selectedFile) : null;
      setPreviewUrl(prevUrlRef.current);
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      const droppedFile = e.dataTransfer.files?.[0] || null;
      if (droppedFile?.type.startsWith('image/')) {
        onFileSelect(droppedFile);
        if (prevUrlRef.current) URL.revokeObjectURL(prevUrlRef.current);
        prevUrlRef.current = droppedFile ? URL.createObjectURL(droppedFile) : null;
        setPreviewUrl(prevUrlRef.current);
      }
    },
    [onFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <section className="glass-card">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Upload className="w-5 h-5" /> Upload Diagram
      </h2>

      <div
        className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center cursor-pointer hover:border-indigo-500/60 transition-colors min-h-[120px]"
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleFileChange}
        />
        {file ? (
          <div className="space-y-2">
            <p className="text-indigo-400 font-medium">{file.name}</p>
            <p className="text-sm text-gray-500">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ) : (
          <p className="text-gray-400">
            Clique ou arraste a imagem do diagrama de arquitetura
          </p>
        )}
      </div>

      {previewUrl && (
        <div className="relative mt-4 rounded-lg overflow-hidden border border-white/10">
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full max-h-48 object-contain bg-slate-900/50"
          />
          {loading && (
            <div className="absolute inset-0 bg-slate-900/80 flex items-center justify-center">
              <div className="flex flex-col items-center gap-2">
                <Scan className="w-10 h-10 text-indigo-400 animate-pulse" />
                <span className="text-sm text-indigo-300">Processando IA...</span>
              </div>
            </div>
          )}
        </div>
      )}

      <button
        className="btn-primary w-full mt-6"
        disabled={!file || loading}
        onClick={onAnalyze}
      >
        {loading ? 'Enviando...' : submitLabel}
      </button>
    </section>
  );
}

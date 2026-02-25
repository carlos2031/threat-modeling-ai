import { Routes, Route } from 'react-router-dom';
import { Header } from './components';
import { HomePage, AnalysesListPage, AnalysisDetailPage } from './pages';

function App() {
  return (
    <div className="min-h-screen bg-slate-950">
      <Header />

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyses" element={<AnalysesListPage />} />
          <Route path="/analyses/:id" element={<AnalysisDetailPage />} />
        </Routes>
      </main>

      <footer className="border-t border-slate-800/50 py-6 text-center text-sm text-gray-500">
        <p>Powered by multimodal LLMs com metodologia STRIDE/DREAD</p>
      </footer>
    </div>
  );
}

export default App;

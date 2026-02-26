import { useState } from 'react';
import UploadPanel from './components/UploadPanel';
import ResultsTable from './components/ResultsTable';
import ComparisonPanel from './components/ComparisonPanel';
import { scoreResumes } from './api';
import { ResumeResult, ScoringMode } from './types';
import { exportToCsv } from './utils/exportCsv';
import { Download, BrainCircuit } from 'lucide-react';

export default function App() {
  const [results, setResults]       = useState<ResumeResult[]>([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState<string | null>(null);
  const [currentMode, setCurrentMode] = useState<ScoringMode>('algorithmic');

  const handleAnalyze = async (jd: File, resumes: File[], mode: ScoringMode) => {
    setLoading(true);
    setError(null);
    setResults([]);
    setCurrentMode(mode);
    try {
      const data = await scoreResumes(jd, resumes, mode);
      setResults(data.results);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string };
      setError(err?.response?.data?.detail ?? err?.message ?? 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BrainCircuit className="text-blue-600" size={24} />
            <div>
              <h1 className="text-xl font-bold text-gray-900 leading-tight">JD Matcher</h1>
              <p className="text-xs text-gray-400">
                Match resumes to job descriptions · Algorithmic &amp; AI scoring
              </p>
            </div>
          </div>
          {results.length > 0 && (
            <button
              onClick={() => exportToCsv(results)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition font-medium"
            >
              <Download size={14} /> Export CSV
            </button>
          )}
        </div>
      </header>

      {/* Main */}
      <main className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        <UploadPanel onAnalyze={handleAnalyze} loading={loading} />

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-16 text-gray-400">
            <div className="animate-spin inline-block w-10 h-10 border-[3px] border-blue-500 border-t-transparent rounded-full mb-4" />
            <p className="text-sm font-medium">
              {currentMode === 'ai'
                ? 'Analyzing with GPT-4o — this may take a moment…'
                : 'Scoring algorithmically…'}
            </p>
          </div>
        )}

        {results.length > 0 && !loading && (
          <>
            <ComparisonPanel results={results} />
            <ResultsTable results={results} />
          </>
        )}
      </main>
    </div>
  );
}

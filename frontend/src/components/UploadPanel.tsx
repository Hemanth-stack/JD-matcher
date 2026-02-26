import { useRef, useState } from 'react';
import { Upload, X, FileText, Cpu, Brain } from 'lucide-react';
import { ScoringMode } from '../types';

interface Props {
  onAnalyze: (jd: File, resumes: File[], mode: ScoringMode) => void;
  loading: boolean;
}

export default function UploadPanel({ onAnalyze, loading }: Props) {
  const [jd, setJd]           = useState<File | null>(null);
  const [resumes, setResumes]  = useState<File[]>([]);
  const [mode, setMode]        = useState<ScoringMode>('algorithmic');
  const jdRef     = useRef<HTMLInputElement>(null);
  const resumeRef = useRef<HTMLInputElement>(null);

  const accept = '.pdf,.docx,.txt';

  const handleAnalyze = () => {
    if (!jd || resumes.length === 0) return;
    onAnalyze(jd, resumes, mode);
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-5">
      <h2 className="text-lg font-semibold text-gray-800">Upload Files</h2>

      {/* JD Drop Zone */}
      <div
        onClick={() => jdRef.current?.click()}
        className="border-2 border-dashed border-blue-300 rounded-xl p-5 text-center cursor-pointer hover:bg-blue-50 transition"
      >
        <Upload className="mx-auto text-blue-400 mb-2" size={24} />
        {jd ? (
          <p className="text-sm font-medium text-blue-600">{jd.name}</p>
        ) : (
          <>
            <p className="text-sm font-medium text-gray-600">Job Description</p>
            <p className="text-xs text-gray-400 mt-0.5">PDF, DOCX or TXT — click to browse</p>
          </>
        )}
        <input
          ref={jdRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={e => setJd(e.target.files?.[0] ?? null)}
        />
      </div>

      {/* Resumes Drop Zone */}
      <div
        onClick={() => resumeRef.current?.click()}
        className="border-2 border-dashed border-green-300 rounded-xl p-5 text-center cursor-pointer hover:bg-green-50 transition"
      >
        <FileText className="mx-auto text-green-400 mb-2" size={24} />
        {resumes.length > 0 ? (
          <p className="text-sm font-medium text-green-600">{resumes.length} resume(s) selected</p>
        ) : (
          <>
            <p className="text-sm font-medium text-gray-600">Resumes (up to 10)</p>
            <p className="text-xs text-gray-400 mt-0.5">PDF, DOCX or TXT — click to browse</p>
          </>
        )}
        <input
          ref={resumeRef}
          type="file"
          accept={accept}
          multiple
          className="hidden"
          onChange={e => {
            const files = Array.from(e.target.files ?? []).slice(0, 10);
            setResumes(files);
          }}
        />
      </div>

      {/* Resume chips */}
      {resumes.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {resumes.map((r, i) => (
            <span
              key={i}
              className="flex items-center gap-1 bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
            >
              {r.name}
              <X
                size={12}
                className="cursor-pointer hover:text-red-500"
                onClick={e => {
                  e.stopPropagation();
                  setResumes(prev => prev.filter((_, j) => j !== i));
                }}
              />
            </span>
          ))}
        </div>
      )}

      {/* Mode Toggle */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-600 font-medium">Scoring Mode:</span>
        <button
          onClick={() => setMode('algorithmic')}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium border transition ${
            mode === 'algorithmic'
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
          }`}
        >
          <Cpu size={14} /> Algorithmic
        </button>
        <button
          onClick={() => setMode('ai')}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium border transition ${
            mode === 'ai'
              ? 'bg-purple-600 text-white border-purple-600'
              : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
          }`}
        >
          <Brain size={14} /> AI (GPT-4o)
        </button>
      </div>

      <button
        onClick={handleAnalyze}
        disabled={!jd || resumes.length === 0 || loading}
        className="w-full py-2.5 rounded-xl bg-blue-600 text-white font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? 'Analyzing…' : 'Analyze'}
      </button>
    </div>
  );
}

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { ResumeResult } from '../types';
import ScoreBar from './ScoreBar';

interface Props {
  results: ResumeResult[];
}

function ScoreBadge({ score }: { score: number }) {
  const cls =
    score >= 70
      ? 'bg-green-100 text-green-700'
      : score >= 40
      ? 'bg-yellow-100 text-yellow-700'
      : 'bg-red-100 text-red-700';
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-sm font-bold ${cls}`}>
      {score}%
    </span>
  );
}

export default function ResultsTable({ results }: Props) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const toggle = (i: number) =>
    setExpanded(prev => {
      const s = new Set(prev);
      s.has(i) ? s.delete(i) : s.add(i);
      return s;
    });

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">
          Results — {results.length} Candidate{results.length !== 1 ? 's' : ''}
        </h2>
        <span className="text-xs text-gray-400">Sorted by best match</span>
      </div>

      <div className="divide-y divide-gray-50">
        {results.map((r, i) => (
          <div key={i}>
            {/* Row header */}
            <div
              className="px-6 py-4 flex items-center gap-4 cursor-pointer hover:bg-gray-50 transition"
              onClick={() => toggle(i)}
            >
              <span className="text-sm font-medium text-gray-400 w-5 shrink-0">
                #{i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-800 truncate">
                  {r.candidate_name}
                </p>
                <p className="text-xs text-gray-400 truncate">{r.filename}</p>
              </div>
              <div className="hidden md:flex gap-5 text-xs text-gray-500">
                <span>
                  Skills <strong>{r.skills_score}%</strong>
                </span>
                <span>
                  Exp <strong>{r.experience_score}%</strong>
                </span>
                <span>
                  Loc <strong>{r.location_score}%</strong>
                </span>
                <span>
                  Edu <strong>{r.education_score}%</strong>
                </span>
              </div>
              <ScoreBadge score={r.total_score} />
              {expanded.has(i) ? (
                <ChevronUp size={16} className="text-gray-400 shrink-0" />
              ) : (
                <ChevronDown size={16} className="text-gray-400 shrink-0" />
              )}
            </div>

            {/* Expanded detail */}
            {expanded.has(i) && (
              <div className="px-6 pb-5 pt-2 bg-gray-50 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <ScoreBar score={r.skills_score} label="Skills Match" />
                  <ScoreBar score={r.experience_score} label="Experience Match" />
                  <ScoreBar score={r.location_score} label="Location Match" />
                  <ScoreBar score={r.education_score} label="Education Match" />
                </div>

                {r.recommendation && (
                  <div className="bg-purple-50 border border-purple-100 rounded-lg p-3 text-sm text-purple-800">
                    <strong>AI Recommendation:</strong> {r.recommendation}
                  </div>
                )}

                {(r.skills_reasoning ||
                  r.experience_reasoning ||
                  r.location_reasoning ||
                  r.education_reasoning) && (
                  <ul className="text-xs text-gray-600 space-y-1.5 list-disc pl-4">
                    {r.skills_reasoning && (
                      <li>
                        <strong>Skills:</strong> {r.skills_reasoning}
                      </li>
                    )}
                    {r.experience_reasoning && (
                      <li>
                        <strong>Experience:</strong> {r.experience_reasoning}
                      </li>
                    )}
                    {r.location_reasoning && (
                      <li>
                        <strong>Location:</strong> {r.location_reasoning}
                      </li>
                    )}
                    {r.education_reasoning && (
                      <li>
                        <strong>Education:</strong> {r.education_reasoning}
                      </li>
                    )}
                  </ul>
                )}

                {r.error && (
                  <div className="bg-red-50 border border-red-100 rounded-lg p-3 text-sm text-red-700">
                    <strong>Error:</strong> {r.error}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

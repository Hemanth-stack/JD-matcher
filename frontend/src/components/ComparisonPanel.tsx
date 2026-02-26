import { ResumeResult } from '../types';
import ScoreBar from './ScoreBar';

interface Props {
  results: ResumeResult[];
}

export default function ComparisonPanel({ results }: Props) {
  const top = results.slice(0, 3);
  if (top.length < 2) return null;

  const colClass =
    top.length === 3 ? 'grid-cols-3' : 'grid-cols-2';

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-5">
        Top {top.length} Candidates — Side by Side
      </h2>
      <div className={`grid ${colClass} gap-5`}>
        {top.map((r, i) => (
          <div key={i} className="space-y-3">
            <div className="text-center pb-3 border-b border-gray-100">
              <div className="text-3xl font-bold text-gray-800">
                {r.total_score}%
              </div>
              <div className="text-sm font-medium text-gray-700 truncate mt-1">
                {r.candidate_name}
              </div>
              <div className="text-xs text-gray-400 truncate">{r.filename}</div>
              {i === 0 && (
                <span className="inline-block mt-1.5 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
                  Best Match
                </span>
              )}
            </div>
            <ScoreBar score={r.skills_score} label="Skills" />
            <ScoreBar score={r.experience_score} label="Experience" />
            <ScoreBar score={r.location_score} label="Location" />
            <ScoreBar score={r.education_score} label="Education" />
          </div>
        ))}
      </div>
    </div>
  );
}

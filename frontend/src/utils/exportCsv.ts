import { ResumeResult } from '../types';

export function exportToCsv(results: ResumeResult[]) {
  const headers = [
    'Rank',
    'Candidate',
    'File',
    'Total Score',
    'Skills Score',
    'Experience Score',
    'Location Score',
    'Education Score',
    'Mode',
  ];

  const rows = results.map((r, i) => [
    i + 1,
    `"${r.candidate_name.replace(/"/g, '""')}"`,
    `"${r.filename.replace(/"/g, '""')}"`,
    r.total_score,
    r.skills_score,
    r.experience_score,
    r.location_score,
    r.education_score,
    r.mode,
  ]);

  const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'jd_matcher_results.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

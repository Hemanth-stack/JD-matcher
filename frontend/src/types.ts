export type ScoringMode = 'algorithmic' | 'ai';

export interface ResumeResult {
  filename: string;
  candidate_name: string;
  total_score: number;
  skills_score: number;
  experience_score: number;
  location_score: number;
  education_score: number;
  // AI-only fields
  skills_reasoning?: string;
  experience_reasoning?: string;
  location_reasoning?: string;
  education_reasoning?: string;
  recommendation?: string;
  mode: ScoringMode;
  error?: string;
}

export interface ScoreResponse {
  results: ResumeResult[];
  mode: ScoringMode;
}

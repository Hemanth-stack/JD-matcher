import axios from 'axios';
import { ScoreResponse, ScoringMode } from './types';

export async function scoreResumes(
  jd: File,
  resumes: File[],
  mode: ScoringMode,
): Promise<ScoreResponse> {
  const form = new FormData();
  form.append('jd', jd);
  resumes.forEach(r => form.append('resumes', r));
  const { data } = await axios.post<ScoreResponse>(
    `/api/score?mode=${mode}`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  );
  return data;
}

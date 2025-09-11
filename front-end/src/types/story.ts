export interface StoryResponse {
  title: string;
  characters: string | string[] | { name: string; description?: string }[];
  setting: string;
  story: string;
  moral: string;
}

export interface ApiError {
  error: string;
  details?: string;
}

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  source?: string;
  url: string;
  image_url?: string;
  category?: string;
  language?: string;
  published_at?: string;
  ai_summary?: string;
  content?: string;
  key_highlights?: string[];
  full_coverage?: string[];
  why_it_matters?: string;
  is_saved?: boolean;
}

export interface SavedNewsResponse extends Omit<NewsArticle, 'id'> {
  id: number;
  article_id?: string;
  saved_at?: string;
}

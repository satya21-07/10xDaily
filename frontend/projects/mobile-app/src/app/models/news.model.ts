export interface NewsArticle {
  id: number;
  title: string;
  summary: string;
  source?: string;
  url?: string;
  image_url?: string;
  category?: string;
  published_at?: string;
  ai_summary?: string;
}

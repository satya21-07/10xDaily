export type FeedbackType = 'bug_report' | 'feature_request' | 'content_issue' | 'general';

export interface FeedbackRequest {
  subject: string;
  message: string;
  feedback_type?: FeedbackType;
  category?: string;
  rating?: number;
  user_name?: string;
  user_email?: string;
  device_info?: string;
}

export interface FeedbackItem {
  id: number;
  user_id?: number;
  user_email: string;
  user_name?: string;
  feedback_type: FeedbackType;
  category?: string;
  subject: string;
  message: string;
  rating?: number;
  device_info?: string;
  status: 'pending' | 'in_review' | 'resolved';
  created_at?: string;
  updated_at?: string;
}

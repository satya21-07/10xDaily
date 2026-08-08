export interface VocabularyWord {
  id: number;
  word: string;
  meaning: string;
  pronunciation?: string;
  audio_url?: string;
  synonyms?: string;
  antonyms?: string;
  origin?: string;
  example?: string;
  difficulty?: string;
  usage_tips?: string;
}

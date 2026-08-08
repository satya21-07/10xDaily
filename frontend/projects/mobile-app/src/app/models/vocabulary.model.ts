export interface DefinitionItem {
  part_of_speech?: string;
  definition?: string;
  example?: string;
}

export interface VocabularyWord {
  id: number;
  word: string;
  definitions?: DefinitionItem[];
  part_of_speech?: string[];
  pronunciation?: string;
  audio_url?: string;
  synonyms?: string[];
  antonyms?: string[];
  origin?: string;
  difficulty?: string;
  usage_tips?: string;
  source?: string;
  
  // Backwards compatibility
  meaning?: string;
  example?: string;
  
  // Progress
  bookmarked?: boolean;
  learned?: boolean;
}

export interface DailyVocabularyResponse {
  date: string;
  total: number;
  words: VocabularyWord[];
}

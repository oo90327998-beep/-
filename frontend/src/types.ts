export type Section = {
  name: string;
  content: string;
};

export type OcrResponse = {
  resumeId: number;
  extractedTextPreview: string;
  sections: Section[] | any;
  images?: string[];
};

export type SuggestionsItem = {
  name: string;
  issues: string[];
  recommendations: string[];
  rewrite_example?: string;
};

export type SuggestionsResponse = {
  resumeId: number;
  overall_summary: string;
  items: SuggestionsItem[];
};

export type ExperienceQuestion = {
  key: string;
  question: string;
  hint: string;
  type: string;
};

export type RefinedExperience = {
  title: string;
  type: string;
  time: string;
  description: string;
  achievements: string[];
};

export type RefinedExperienceResponse = {
  experiences: RefinedExperience[];
  skills: string[];
  certificates: string[];
  suggestions: string[];
};

export type StyleInfo = {
  name: string;
  description: string;
};

export type StyleTransformResponse = {
  resumeId: number;
  styleType: string;
  styleName: string;
  sections: Section[];
  styleNotes: string[];
};

export type ResumeListItem = {
  resumeId: number;
  filename: string;
  createdAt: string;
  hasContent: boolean;
  hasSuggestions: boolean;
};

export type ATSReport = {
  score: number;
  issues: string[];
  suggestions: string[];
  keywordsFound: string[];
  keywordsMissing: string[];
};

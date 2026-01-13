export interface NiceToHave {
  importance: number;
  nice_to_have: string;
}

export interface Requirement {
  importance: number;
  requirement: string;
}

export interface JobAnalysis {
  description: string;
  resume_questions: string[];
  nice_to_have: NiceToHave[];
  requirements: Requirement[];
  required_industry: string;
  minimum_years_is_assumed: boolean;
  industry_match_importance: number;
  minimum_years_of_experience: number;
  industry_match_importance_justification: string;
}

export interface ResumeAnswers {
  [questionIndex: number]: string;
}
import { createContext, useContext } from "react";
import { CVData } from "../types/cv.types";
import { JobAnalysis, ResumeAnswers } from "../types/jobAnalysis.types";

export const DEFAULT_CV: CVData = {
  cv: {
    state: "",
    city: "",
    name: "",
    label: "",
    location: "",
    email: "",
    phone: "",
    website: "",
    social_networks: [],
    sections: {},
  },
  design: {
    theme: "classic",
  },
};

export interface CVContextType {
  cvData: CVData;
  cvCode: string;
  appError: string | null;
  jobAnalysis: JobAnalysis | null;
  resumeAnswers: ResumeAnswers;
  showAIReview: boolean;
  isPollingStatus: boolean;
  hasAnalysisStarted: boolean;
  hasAnalysisCompleted: boolean;
  apiResponse: any;
  setShowAIReview: (show: boolean) => void;
  startStatusPolling: (cvCode: string) => void;
  updateCV: (data: Partial<CVData>) => void;
  updatePersonalInfo: (info: Partial<CVData["cv"]>) => void;
  updateDesign: (design: Partial<CVData["design"]>) => void;
  updateSection: (sectionName: string, entries: any[]) => void;
  addSection: (sectionName: string) => void;
  removeSection: (sectionName: string) => void;
  resetCV: () => void;
  loadCV: (data: CVData) => void;
  setJobAnalysis: (analysis: JobAnalysis | null) => void;
  setResumeAnswers: (answers: ResumeAnswers) => void;
  setCvCode: (code: string) => void;
  setAppError: (error: string | null) => void;
}

export const CVContext = createContext<CVContextType | undefined>(undefined);

export function useCV() {
  const context = useContext(CVContext);
  if (context === undefined) {
    throw new Error("useCV must be used within a CVProvider");
  }
  return context;
}

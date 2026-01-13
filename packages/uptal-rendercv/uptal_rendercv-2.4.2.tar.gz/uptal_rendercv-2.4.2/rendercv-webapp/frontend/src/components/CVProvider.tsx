import React, { useState, useEffect, ReactNode } from "react";
import { CVContext, CVContextType, DEFAULT_CV } from "../hooks/useCV";
import { CVData } from "../types/cv.types";
import { JobAnalysis, ResumeAnswers } from "../types/jobAnalysis.types";
import { cvApi } from "../services/api";
import toast from "react-hot-toast";

export function CVProvider({ children }: { children: ReactNode }) {
  const [cvCode, setCvCode] = useState<string>(() => {
    // First, try to get from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const urlCvCode = urlParams.get("id");

    if (urlCvCode) {
      // Save to localStorage if found in URL
      return urlCvCode;
    }

    // Default cvCode
    const defaultCode = "";
    return defaultCode;
  });

  const [cvData, setCvData] = useState<CVData>(() => {
    // Load from localStorage if available

    const saved = localStorage.getItem("rendercv_data");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return DEFAULT_CV;
      }
    }
    return DEFAULT_CV;
  });

  const [appError, setAppError] = useState<string | null>(null);

  // Listen for URL changes and update cvCode if id parameter changes
  useEffect(() => {
    const handleUrlChange = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const urlCvCode = urlParams.get("id");

      if (urlCvCode && urlCvCode !== cvCode) {
        setCvCode(urlCvCode);
        localStorage.setItem("rendercv_cv_code", urlCvCode);
      }
    };

    // Check on mount
    handleUrlChange();

    // Listen for popstate events (back/forward navigation)
    window.addEventListener("popstate", handleUrlChange);

    return () => {
      window.removeEventListener("popstate", handleUrlChange);
    };
  }, [cvCode]);

  const loadSampleCV = async (cvCode: string) => {
    try {
      const cvData = await cvApi.getSampleCVByCode(cvCode);

      if (!cvData) {
        throw new Error("No CV data received");
      }

      // Use the cvData in your component
      setCvData(cvData);
      setAppError(null);
    } catch (error: any) {
      console.error("Error loading CV:", error);

      // Clear localStorage data since the CV is invalid
      localStorage.removeItem("rendercv_data");

      // Display error message to user
      const errorMessage =
        error.response?.data?.error ||
        error.message ||
        "Failed to load CV. Please check if the CV ID is correct.";

      setAppError(errorMessage);
      toast.error(errorMessage, {
        duration: 5000,
        id: "cv-load-error",
      });

      // Reset to default CV data
      setCvData(DEFAULT_CV);
    }
  };

  useEffect(() => {
    loadSampleCV(cvCode);
  }, [cvCode]);

  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(() => {
    // Load job analysis from localStorage if available
    const saved = localStorage.getItem("rendercv_job_analysis");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return null;
      }
    }
    return null;
  });

  const [resumeAnswers, setResumeAnswers] = useState<ResumeAnswers>(() => {
    // Load resume answers from localStorage if available
    const saved = localStorage.getItem("rendercv_resume_answers");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        return {};
      }
    }
    return {};
  });

  const [showAIReview, setShowAIReview] = useState<boolean>(false);
  const [isPollingStatus, setIsPollingStatus] = useState<boolean>(false);
  const [hasAnalysisStarted, setHasAnalysisStarted] = useState<boolean>(false);
  const [hasAnalysisCompleted, setHasAnalysisCompleted] =
    useState<boolean>(false);
  const [apiResponse, setApiResponse] = useState<any>(null);
  const pollingTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(
    null
  );
  const pollingIntervalRef = React.useRef<ReturnType<
    typeof setInterval
  > | null>(null);
  const attemptCountRef = React.useRef<number>(0);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingTimeoutRef.current) {
        clearTimeout(pollingTimeoutRef.current);
      }
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const startStatusPolling = React.useCallback((cvCodeToPoll: string) => {
    // Clear any existing polling
    if (pollingTimeoutRef.current) {
      clearTimeout(pollingTimeoutRef.current);
      pollingTimeoutRef.current = null;
    }
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    setIsPollingStatus(true);
    setHasAnalysisStarted(true);
    const maxAttempts = 12;
    const pollInterval = 7000; // 7 seconds

    // Reset attempt count for new polling session
    attemptCountRef.current = 0;

    const checkStatus = async () => {
      try {
        attemptCountRef.current++;
        console.log(
          `Checking CV status (attempt ${attemptCountRef.current}/${maxAttempts})...`
        );

        const infoResponse = await cvApi.getCVInfo(cvCodeToPoll);
        console.log("CV info response:", infoResponse);

        // Store the full API response for AI Review
        setApiResponse(infoResponse);

        // Check the response structure - it might be nested in 'data'
        const data = infoResponse?.data || infoResponse;

        const analysisStatus = data?.analysis_status;
        const enhancementStatus = data?.enhancement_status;
        const enhancementResult = data?.enhancement_result;

        console.log("Status check:", {
          analysisStatus,
          enhancementStatus,
          hasEnhancementResult: !!enhancementResult,
        });

        if (analysisStatus === "done" && enhancementStatus === "completed") {
          // Status matches! Update CV data and show AI review
          console.log("Status matches! Updating CV data...");

          // If enhancement_result contains CV data, update it
          if (enhancementResult && typeof enhancementResult === "object") {
            // Check if it's a valid CVData structure
            if (enhancementResult.cv || enhancementResult.design) {
              setCvData(enhancementResult as CVData);
              console.log("CV data updated from enhancement result");
            }
          }

          // Stop polling
          setIsPollingStatus(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          if (pollingTimeoutRef.current) {
            clearTimeout(pollingTimeoutRef.current);
            pollingTimeoutRef.current = null;
          }

          // Show AI Review
          setShowAIReview(true);
          setHasAnalysisCompleted(true);
          toast.success("CV analysis and enhancement completed!");
        } else if (attemptCountRef.current >= maxAttempts) {
          // Max attempts reached
          console.log("Max polling attempts reached");
          setIsPollingStatus(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          if (pollingTimeoutRef.current) {
            clearTimeout(pollingTimeoutRef.current);
            pollingTimeoutRef.current = null;
          }
          toast.error(
            "Status check timed out. Please refresh the page to check the latest status.",
            { duration: 5000 }
          );
        }
        // Otherwise, continue polling (handled by setInterval)
      } catch (error: any) {
        console.error("Failed to fetch CV info:", error);

        if (attemptCountRef.current >= maxAttempts) {
          setIsPollingStatus(false);
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          if (pollingTimeoutRef.current) {
            clearTimeout(pollingTimeoutRef.current);
            pollingTimeoutRef.current = null;
          }
          toast.error("Failed to check CV status. Please try again later.", {
            duration: 5000,
          });
        }
        // Continue polling on error (up to max attempts)
      }
    };

    // First call after 5 seconds
    pollingTimeoutRef.current = setTimeout(() => {
      checkStatus();

      // Then poll every 3 seconds
      pollingIntervalRef.current = setInterval(() => {
        checkStatus();
      }, pollInterval);
    }, 5000);
  }, []);

  // Save to localStorage whenever cvData changes
  useEffect(() => {
    localStorage.setItem("rendercv_data", JSON.stringify(cvData));
  }, [cvData]);

  // Save job analysis to localStorage whenever it changes
  useEffect(() => {
    if (jobAnalysis) {
      localStorage.setItem(
        "rendercv_job_analysis",
        JSON.stringify(jobAnalysis)
      );
    } else {
      localStorage.removeItem("rendercv_job_analysis");
    }
  }, [jobAnalysis]);

  // Save resume answers to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(
      "rendercv_resume_answers",
      JSON.stringify(resumeAnswers)
    );
  }, [resumeAnswers]);

  // Save cvCode to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("rendercv_cv_code", cvCode);
  }, [cvCode]);

  const updateCV = (data: Partial<CVData>) => {
    setCvData((prev) => ({ ...prev, ...data }));
  };

  const updatePersonalInfo = (info: Partial<CVData["cv"]>) => {
    setCvData((prev) => ({
      ...prev,
      cv: { ...prev.cv, ...info },
    }));
    console.log(cvData, "ss");
  };

  const updateDesign = (design: Partial<CVData["design"]>) => {
    setCvData((prev) => ({
      ...prev,
      design: { ...prev.design, ...design },
    }));
  };

  const updateSection = (sectionName: string, entries: any[]) => {
    setCvData((prev) => ({
      ...prev,
      cv: {
        ...prev.cv,
        sections: {
          ...prev.cv.sections,
          [sectionName]: entries,
        },
      },
    }));
  };

  const addSection = (sectionName: string) => {
    setCvData((prev) => ({
      ...prev,
      cv: {
        ...prev.cv,
        sections: {
          ...prev.cv.sections,
          [sectionName]: [],
        },
      },
    }));
  };

  const removeSection = (sectionName: string) => {
    setCvData((prev) => {
      const newSections = { ...prev.cv.sections };
      delete newSections[sectionName];
      return {
        ...prev,
        cv: {
          ...prev.cv,
          sections: newSections,
        },
      };
    });
  };

  const resetCV = () => {
    setCvData(DEFAULT_CV);
  };

  const loadCV = (data: CVData) => {
    setCvData(data);
  };

  const contextValue: CVContextType = {
    cvData,
    cvCode,
    appError,
    jobAnalysis,
    resumeAnswers,
    showAIReview,
    isPollingStatus,
    hasAnalysisStarted,
    hasAnalysisCompleted,
    apiResponse,
    setShowAIReview,
    startStatusPolling,
    updateCV,
    updatePersonalInfo,
    updateDesign,
    updateSection,
    addSection,
    removeSection,
    resetCV,
    loadCV,
    setJobAnalysis,
    setResumeAnswers,
    setCvCode,
    setAppError,
  };

  return (
    <CVContext.Provider value={contextValue}>{children}</CVContext.Provider>
  );
}

import axios from "axios";
import { CVData, Theme } from "../types/cv.types";
import { JobAnalysis, ResumeAnswers } from "../types/jobAnalysis.types";

const getFilenameFromDisposition = (disposition?: string): string | null => {
  if (!disposition) return null;
  const match = disposition.match(/filename=\"?([^\";]+)\"?/i);
  return match && match[1] ? match[1] : null;
};

const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:4000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
    // Authorization: `Bearer uApWzzzfgygAiaybL7wcYx92Qz2JLm5Vbkb0ZcCri9tB`,
  },
});

export const cvApi = {
  // Render CV to PDF
  renderCV: async (
    cvData: CVData,
    hash?: string
  ): Promise<{ blob: Blob; filename: string }> => {
    // get redirectUrl value
    const redirectUrl = new URLSearchParams(window.location.search).get("redirectUrl");
    let url = hash ? `/render/${hash}` : "/render";

    if (redirectUrl) {
      url += `?redirectUrl=${redirectUrl}`;
    }

    const response = await api.post(url, cvData, {
      responseType: "blob",
    });

    const filename =
      getFilenameFromDisposition(response.headers["content-disposition"]) ||
      "cv.pdf";

    return { blob: response.data, filename };
  },

  // Download helper for render endpoint
  downloadRenderedPdf: async (
    cvData: CVData,
    hash?: string,
    filename?: string
  ): Promise<void> => {
    const { blob, filename: serverFilename } = await cvApi.renderCV(
      cvData,
      hash
    );
    downloadBlob(blob, filename || serverFilename);
  },

  // Validate CV data
  validateCV: async (
    cvData: CVData
  ): Promise<{ valid: boolean; errors?: string[] }> => {
    const response = await api.post("/validate", cvData);
    return response.data;
  },

  // Get available themes
  getThemes: async (): Promise<Theme[]> => {
    const response = await api.get("/themes");
    return response.data;
  },

  // Get sample CV
  getSampleCV: async (): Promise<CVData> => {
    const response = await api.get("/sample");
    return response.data;
  },

  // Get sample CV by code
  getSampleCVByCode: async (cvCode: string): Promise<CVData> => {
    const redirectUrl = new URLSearchParams(window.location.search).get("redirectUrl");
    let url = `/sample/${cvCode}`;

    if (redirectUrl) {
      url += `?redirectUrl=${redirectUrl}`;
    }

    const response = await api.get(url);
    return response.data;
  },

  // Export CV
  exportCV: async (
    cvData: CVData,
    format: "yaml" | "json" | "markdown"
  ): Promise<Blob | any> => {
    const response = await api.post(`/export/${format}`, cvData, {
      responseType: format === "json" ? "json" : "blob",
    });
    return response.data;
  },

  // Import CV from YAML
  importCV: async (file: File): Promise<CVData> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/import", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data.cv_data;
  },

  // Parse CV using GPT-4o-mini
  parseCV: async (
    file: File,
    jobAnalysis?: JobAnalysis | null,
    resumeAnswers?: ResumeAnswers
  ): Promise<{ success: boolean; cv_data?: CVData; error?: string }> => {
    const formData = new FormData();
    formData.append("file", file);
    if (jobAnalysis) {
      formData.append("job_analysis", JSON.stringify(jobAnalysis));
    }
    if (resumeAnswers && Object.keys(resumeAnswers).length > 0) {
      formData.append("resume_answers", JSON.stringify(resumeAnswers));
    }

    try {
      const response = await api.post("/parse-cv", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error: any) {
      if (error.response?.data) {
        return error.response.data;
      }
      return { success: false, error: error.message || "Failed to parse CV" };
    }
  },

  // Update CV edits
  updateCVEdits: async (
    cvCode: string,
    cvData: CVData
  ): Promise<{
    status: string | boolean;
    data?: any;
    error?: string;
    message?: string;
    redirect_url?: string;
  }> => {
    try {
      console.log("Updating CV with code:", cvCode);
      console.log("CV Data:", cvData);

      const redirectUrl = new URLSearchParams(window.location.search).get("redirectUrl");
      let url = `/cv-enhance/${cvCode}/edits`;

      if (redirectUrl) {
        url += `?redirectUrl=${redirectUrl}`;
      }

      const response = await api.post(url, cvData, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      console.log("Response received:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("Update CV error:", error);
      console.error("Error response:", error.response?.data);
      if (error.response?.data) {
        // Return the error data from the backend
        return error.response.data;
      }
      return {
        status: "error",
        error: error.message || "Failed to update CV",
      };
    }
  },

  // Get CV info by code
  getCVInfo: async (cvCode: string): Promise<any> => {
    try {
      const redirectUrl = new URLSearchParams(window.location.search).get("redirectUrl");
      let url = `/info/${cvCode}`;

      if (redirectUrl) {
        url += `?redirectUrl=${redirectUrl}`;
      }

      const response = await api.get(url);
      return response.data;
    } catch (error: any) {
      console.error("Get CV info error:", error);
      if (error.response?.data) {
        return error.response.data;
      }
      throw error;
    }
  },
};

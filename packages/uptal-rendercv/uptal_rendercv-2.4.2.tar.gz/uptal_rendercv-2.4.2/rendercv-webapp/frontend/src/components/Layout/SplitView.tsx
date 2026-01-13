import React, { useState, useEffect, useMemo } from "react";
import FormBuilder from "../FormBuilder/FormBuilder";
import PdfViewer from "../PdfViewer/PdfViewer";
import AIReview from "../AIReview";
import { transformAPIResponseToAIReviewData } from "../AIReview/AIReview";
import { IconEye, IconEdit } from "@tabler/icons-react";
import { useCV } from "../../hooks/useCV";
import { CircularProgress, Box, Typography } from "@mui/material";
import ScoreNotificationBar from "../../components/ScoreNotificationBar";

const SplitView: React.FC = () => {
  const [activeView, setActiveView] = useState<
    "sections" | "preview" | "ai-review"
  >("sections");
  const { showAIReview, setShowAIReview, isPollingStatus, apiResponse } =
    useCV();

  // Transform API response to AIReviewData format
  const aiReviewData = useMemo(() => {
    if (apiResponse) {
      return transformAPIResponseToAIReviewData(apiResponse);
    }
    return undefined;
  }, [apiResponse]);

  // Update activeView when showAIReview changes
  useEffect(() => {
    if (showAIReview) {
      setActiveView("ai-review");
    }
  }, [showAIReview]);

  const handleBackFromAIReview = () => {
    setShowAIReview(false);
    setActiveView("preview");
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-64px)] relative">
      {/* Polling Status Overlay */}
      {isPollingStatus && (
        <Box
          sx={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            height: "100vh",
            width: "100vw",
            backgroundColor: "rgba(255, 255, 255, 0.9)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 9999,
            gap: 2,
          }}
        >
          <CircularProgress size={48} />
          <Typography variant="body1" sx={{ color: "#666", mt: 2 }}>
            Checking CV status...
          </Typography>
          <Typography variant="body2" sx={{ color: "#999" }}>
            Please wait while we process your CV
          </Typography>
        </Box>
      )}

      {/* Mobile View Toggle */}
      <div className="lg:hidden flex bg-gray-100 p-1 rounded-lg mx-4 mt-4">
        <button
          onClick={() => setActiveView("sections")}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all duration-200 ${
            activeView === "sections"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <IconEdit size={16} />
          <span className="font-medium text-sm">Sections</span>
        </button>
        <button
          onClick={() => setActiveView("preview")}
          className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all duration-200 ${
            activeView === "preview"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <IconEye size={16} />
          <span className="font-medium text-sm">Preview</span>
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Left Panel - Form Builder (Sections) */}
        <div
          className={`w-full lg:w-1/2 overflow-y-auto border-r-0 lg:border-r border-gray-300 bg-white ${
            activeView === "sections" ? "block" : "hidden lg:block"
          } min-h-[calc(50vh-80px)] lg:min-h-0`}
        >
          <ScoreNotificationBar />

          <FormBuilder />
        </div>

        {/* Right Panel - PDF Viewer (Preview) or AI Review */}
        <div
          className={`w-full lg:w-1/2 bg-white ${
            activeView === "preview" || activeView === "ai-review"
              ? "block"
              : "hidden lg:block"
          } min-h-[calc(100vh-180px)] lg:min-h-0 overflow-hidden`}
        >
          {showAIReview ? (
            <AIReview onBack={handleBackFromAIReview} data={aiReviewData} />
          ) : (
            <PdfViewer />
          )}
        </div>
      </div>
    </div>
  );
};

export default SplitView;

import React, { useState } from "react";
import { AppBar, Toolbar, Typography, Button, IconButton } from "@mui/material";
import toast from "react-hot-toast";
import { IconArrowLeft, IconDeviceFloppy } from "@tabler/icons-react";
import { useCV } from "../../hooks/useCV";
import { cvApi } from "../../services/api";
import { prepareCVData } from "../../utils/cvHelpers";
import { IconPalette } from "@tabler/icons-react";
import TemplateGallery from "../PdfViewer/TemplateGallery";

const Header: React.FC = () => {
  const {
    cvData,
    cvCode,
    startStatusPolling,
    showAIReview,
    isPollingStatus,
    hasAnalysisStarted,
  } = useCV();
  const [templateGalleryOpen, setTemplateGalleryOpen] = useState(false);

  const handleDownloadPDF = async () => {
    try {
      toast.loading("Downloading latest PDF...", { id: "pdf-download" });
      const dataToSend = prepareCVData(cvData);
      const pdfFilename = `${cvData?.cv?.name || "cv"}_resume.pdf`;
      await cvApi.downloadRenderedPdf(dataToSend, cvCode || undefined, pdfFilename);
      toast.success("PDF downloaded successfully!", { id: "pdf-download" });
    } catch (error: any) {
      console.error("PDF download error:", error);
      toast.error(error.response?.data?.error || "Failed to download PDF", {
        id: "pdf-download",
      });
    }
  };

  const handleSaveAndContinue = async () => {
    try {
      // Show loading toast
      toast.loading("Saving CV...", { id: "save-cv" });

      // Prepare CV data using the helper function
      const dataToSend = prepareCVData(cvData);

      // Send CV data as JSON to update CV edits
      console.log("Saving CV data to cvCode:", cvCode);

      const saveResponse = await cvApi.updateCVEdits(cvCode, dataToSend);

      console.log("Save response:", saveResponse);
      toast.success("CV saved successfully!", { id: "save-cv" });

      if (saveResponse.status === "success" || saveResponse.status === true) {
        startStatusPolling(cvCode);
      } else {
        const errorMsg =
          saveResponse.error ||
          saveResponse.message ||
          "Failed to save CV. Please try again.";
        toast.error(errorMsg, {
          id: "save-cv",
        });
      }
    } catch (error: any) {
      console.error("Save CV error:", error);
      const errorMsg =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        "Failed to save CV. Please try again.";
      toast.error(errorMsg, {
        id: "save-cv",
      });
    }
  };

  const getRedirectUrl = (): string | null => {
    const queryString = window.location.search.substring(1);
    const redirectUrlIndex = queryString.indexOf("redirectUrl=");
    
    if (redirectUrlIndex === -1) {
      return null;
    }
    
    // Get everything after "redirectUrl="
    // Since redirectUrl contains query parameters with &, we need to get the full value
    // This assumes redirectUrl is the last parameter in the query string
    let redirectUrlValue = queryString.substring(redirectUrlIndex + "redirectUrl=".length);
    
    // Check if URLSearchParams truncated the value
    const urlParams = new URLSearchParams(window.location.search);
    const encodedRedirectUrl = urlParams.get("redirectUrl");
    
    console.log("Manual extraction:", redirectUrlValue);
    console.log("URLSearchParams result:", encodedRedirectUrl);
    console.log("Manual length:", redirectUrlValue.length, "URLSearchParams length:", encodedRedirectUrl?.length);
    
    // If the manually extracted value is longer than URLSearchParams result,
    // it means URLSearchParams truncated it at the first &, so use manual extraction
    if (!encodedRedirectUrl || redirectUrlValue.length > encodedRedirectUrl.length) {
      // Use manually extracted value (full URL with all query parameters)
      // Try to decode it first
      try {
        const decoded = decodeURIComponent(redirectUrlValue);
        console.log("Decoded manual value:", decoded);
        if (decoded.startsWith("http://") || decoded.startsWith("https://")) {
          return decoded;
        }
      } catch (e) {
        // If decoding fails, check if the raw value is a valid URL
        console.log("Decoding failed, using raw value:", redirectUrlValue);
        if (redirectUrlValue.startsWith("http://") || redirectUrlValue.startsWith("https://")) {
          return redirectUrlValue;
        }
      }
    } else {
      // URLSearchParams got the full value (redirectUrl was properly URL-encoded)
      try {
        const decoded = decodeURIComponent(encodedRedirectUrl);
        if (decoded.startsWith("http://") || decoded.startsWith("https://")) {
          return decoded;
        }
      } catch (e) {
        // If decoding fails, use the original value
        if (encodedRedirectUrl.startsWith("http://") || encodedRedirectUrl.startsWith("https://")) {
          return encodedRedirectUrl;
        }
      }
    }
    
    return null;
  };

  const handleBackToApplication = () => {
    const redirectUrl = getRedirectUrl();
    console.log(redirectUrl,"redirectUrl")

    if (redirectUrl) {
      window.location.href = redirectUrl;
    } else {
      // Fallback to going back if no redirect URL
      window.history.back();
    }
  };

  const handleContinue = () => {
    const redirectUrl = getRedirectUrl();
    if (redirectUrl) {
      window.location.href = redirectUrl;
    } else {
      // Fallback to going back if no redirect URL
      window.history.back();
    }
  };

  return (
    <AppBar
      position="static"
      sx={{
        backgroundColor: "#fff",
        boxShadow: "none",
        borderBottom: "1px solid #e0e0e0",
      }}
    >
      <Toolbar className="justify-between min-h-16 px-4 sm:px-6">
        {/* Left side - Back to Application */}
        <div className="flex items-center">
          <IconButton
            onClick={handleBackToApplication}
            className="text-black hover:bg-gray-100 transition-colors duration-200"
            size="small"
          >
            <IconArrowLeft color="#000000" size={20} />
          </IconButton>
          <Typography
            className="text-black text-sm hidden sm:block cursor-pointer"
            onClick={handleBackToApplication}
          >
            Back to Application
          </Typography>
        </div>

        {/* Center - CV Title with edit icon */}
        <div className="flex items-center space-x-2 flex-1 justify-center"></div>

        {/* Right side - Buttons */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Desktop only buttons */}
          <div className="hidden sm:flex items-center space-x-3">
            {/* Select Template - hide when analysis is complete */}
            {!showAIReview && !isPollingStatus && (
              <Button
                variant="outlined"
                startIcon={<IconPalette />}
                onClick={() => setTemplateGalleryOpen(true)}
                sx={{
                  textTransform: "none",
                  borderColor: "#E5E7EBB8",
                  color: "#11181C",
                }}
              >
                Select Template
              </Button>
            )}

            {/* Download PDF - always visible on desktop */}
            {!isPollingStatus && (
              <Button
                variant="outlined"
                startIcon={<IconDeviceFloppy />}
                onClick={handleDownloadPDF}
                sx={{
                  textTransform: "none",
                  borderColor: "#E5E7EBB8",
                  color: "#11181C",
                }}
              >
                Download PDF
              </Button>
            )}
          </div>

          {/* Analyze button - visible when analysis has not started */}
          {!hasAnalysisStarted && (
            <Button
              variant="contained"
              onClick={handleSaveAndContinue}
              className="bg-blue-600 hover:bg-blue-700 text-white normal-case transition-colors duration-200"
              sx={{
                textTransform: "none",
              }}
            >
              Analyze
            </Button>
          )}

          {/* Continue button - visible once analysis has started */}
          {hasAnalysisStarted && (
            <Button
              variant="contained"
              onClick={handleContinue}
              className="bg-green-600 hover:bg-green-700 text-white normal-case transition-colors duration-200"
              sx={{
                textTransform: "none",
              }}
            >
              Continue
            </Button>
          )}
        </div>
      </Toolbar>
      {/* Template Gallery Drawer */}
      <TemplateGallery
        open={templateGalleryOpen}
        onClose={() => setTemplateGalleryOpen(false)}
      />
    </AppBar>
  );
};

export default Header;

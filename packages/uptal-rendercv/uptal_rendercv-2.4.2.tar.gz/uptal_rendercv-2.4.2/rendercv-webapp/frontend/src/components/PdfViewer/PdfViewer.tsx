import React, { useEffect, useState } from "react";
import { Box, CircularProgress, Typography, Paper, Alert } from "@mui/material";
import { useCV } from "../../hooks/useCV";
import { useDebounce } from "../../hooks/useDebounce";
import { cvApi } from "../../services/api";
import { prepareCVData } from "../../utils/cvHelpers";

const PdfViewer: React.FC = () => {
  const { cvData, cvCode, setAppError } = useCV();
  const debouncedCvData = useDebounce(cvData, 1000); // Debounce for 1 second
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    // Only generate PDF if there's a name
    if (debouncedCvData.cv.name) {
      generatePdf();
    }
  }, [debouncedCvData]);

  const generatePdf = async () => {
    setLoading(true);
    setError(null);
    setAppError(null);

    // Declare dataToSend outside try block so it's accessible in catch block
    let dataToSend: any;

    try {
      // Prepare CV data using the helper function
      dataToSend = prepareCVData(debouncedCvData);

      // Pass cvCode as hash if available and get blob
      const { blob } = await cvApi.renderCV(dataToSend, cvCode || undefined);
      const url = window.URL.createObjectURL(blob);

      // Clean up previous object URL to avoid leaks
      if (objectUrl) {
        window.URL.revokeObjectURL(objectUrl);
      }

      setObjectUrl(url);
      setPdfUrl(url);
    } catch (err: any) {
      console.error("PDF generation error:", err);
      console.error("Error response data:", err.response?.data);
      if (dataToSend) {
        console.error("Request data that failed:", dataToSend);
      }

      let errorMessage =
        err.response?.data?.error ||
        err.response?.data?.errors ||
        err.message ||
        "Failed to generate PDF";

      if (err.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          try {
            const parsed = JSON.parse(text);
            errorMessage = parsed.error || parsed.errors || text || errorMessage;
          } catch {
            errorMessage = text || errorMessage;
          }
        } catch {
          // Keep the original errorMessage.
        }
      }
      const formattedError =
        typeof errorMessage === "string"
          ? errorMessage
          : JSON.stringify(errorMessage);
      setError(formattedError);
      setAppError(formattedError);
    } finally {
      setLoading(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (objectUrl) {
        window.URL.revokeObjectURL(objectUrl);
      }
    };
  }, [objectUrl]);

  if (!cvData.cv.name) {
    return (
      <Paper sx={{ p: 4, textAlign: "center", height: "100%" }}>
        <div className="flex w-full h-full justify-center items-center align-middle">
          <div>
            <Typography variant="h6" gutterBottom>
              Welcome to CV Enhancement
            </Typography>
            <Typography color="text.secondary">
              Start by entering your name in the Personal Information section
            </Typography>
          </div>
        </div>
      </Paper>
    );
  }

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography>Generating PDF...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2, maxWidth: 500 }}>
        <Alert severity="error" sx={{ mb: 2, whiteSpace: "pre-wrap" }}>
          {error}
        </Alert>
        <Typography color="text.secondary">
          Please check your CV data and try again.
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Box
        sx={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          position: "relative",
          backgroundColor: "white",
        }}
      >
        {/* PDF Display */}
        {pdfUrl && (
          <>
            <embed
              src={pdfUrl}
              type="application/pdf"
              width="100%"
              height="100%"
              style={{
                border: "none",
                outline: "none",
                backgroundColor: "white",
                boxShadow: "none",
                padding: "0px",
              }}
              title="CV Preview"
            />

            {/* Fallback message */}
            <Box
              sx={{
                position: "absolute",
                bottom: 16,
                left: "50%",
                transform: "translateX(-50%)",
                bgcolor: "background.paper",
                p: 2,
                borderRadius: 1,
                boxShadow: 1,
                display: "none", // Will be shown via CSS if embed fails
              }}
            >
              <Typography variant="body2" color="text.secondary">
                If the PDF doesn't display, try the download button above
              </Typography>
            </Box>
          </>
        )}
      </Box>
    </>
  );
};

export default PdfViewer;

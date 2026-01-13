import React, { useState, useRef } from "react";
import {
  Box,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Stepper,
  Step,
  StepLabel,
  TextField,
  Card,
  CardContent,
  Collapse,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import DescriptionIcon from "@mui/icons-material/Description";
import CloseIcon from "@mui/icons-material/Close";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import InfoIcon from "@mui/icons-material/Info";
import QuestionAnswerIcon from "@mui/icons-material/QuestionAnswer";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import { cvApi } from "../../services/api";
import { useCV } from "../../hooks/useCV";
import { ResumeAnswers } from "../../types/jobAnalysis.types";

const CVUploaderWithQuestions: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [tempAnswers, setTempAnswers] = useState<ResumeAnswers>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { loadCV, jobAnalysis, setResumeAnswers } = useCV();

  const hasQuestions =
    jobAnalysis?.resume_questions && jobAnalysis.resume_questions.length > 0;
  const questions = jobAnalysis?.resume_questions || [];

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Validate file type
    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
      "text/plain",
    ];

    const allowedExtensions = [".pdf", ".docx", ".doc", ".txt"];
    const fileExtension = file.name
      .substring(file.name.lastIndexOf("."))
      .toLowerCase();

    if (
      !allowedTypes.includes(file.type) &&
      !allowedExtensions.includes(fileExtension)
    ) {
      setError("Please upload a PDF, Word document, or text file");
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("File size must be less than 5MB");
      return;
    }

    setSelectedFile(file);
    setError(null);
    setSuccess(false);

    // Move to next step if there are questions, otherwise stay for upload
    if (hasQuestions) {
      setActiveStep(1);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setError(null);
    setSuccess(false);
    setActiveStep(0);
    setCurrentQuestionIndex(0);
    setTempAnswers({});
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleAnswerChange = (answer: string) => {
    setTempAnswers((prev) => ({
      ...prev,
      [currentQuestionIndex]: answer,
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // Move to review step
      setActiveStep(2);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      // Save answers to context
      setResumeAnswers(tempAnswers);

      // Upload with job analysis and answers
      const result = await cvApi.parseCV(
        selectedFile,
        jobAnalysis,
        tempAnswers
      );

      if (result.success && result.cv_data) {
        // Load the parsed data into the form
        loadCV(result.cv_data);
        setSuccess(true);

        // Clear selection after successful upload
        setTimeout(() => {
          clearSelection();
        }, 3000);
      } else {
        setError(result.error || "Failed to parse resume");
      }
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(
        err.response?.data?.error || "Failed to upload and parse resume"
      );
    } finally {
      setUploading(false);
    }
  };

  const getStepContent = () => {
    switch (activeStep) {
      case 0:
        // File upload step
        return (
          <Paper
            sx={{
              p: 3,
              border: dragActive ? "2px dashed #1976d2" : "2px dashed #ccc",
              borderRadius: 2,
              bgcolor: dragActive ? "action.hover" : "background.paper",
              transition: "all 0.3s ease",
              cursor: !selectedFile ? "pointer" : "default",
            }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={!selectedFile ? handleButtonClick : undefined}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileSelect}
              style={{ display: "none" }}
            />

            {!selectedFile ? (
              <Box sx={{ textAlign: "center" }}>
                <CloudUploadIcon
                  sx={{ fontSize: 48, color: "action.active", mb: 2 }}
                />
                <Typography variant="h6" gutterBottom>
                  Upload Your Resume
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Drag and drop or click to browse
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Supported formats: PDF, DOC, DOCX, TXT (Max 5MB)
                </Typography>
              </Box>
            ) : (
              <Box>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "center", flex: 1 }}>
                    <DescriptionIcon sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body1" sx={{ fontWeight: 500 }}>
                      {selectedFile.name}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{ ml: 1, color: "text.secondary" }}
                    >
                      ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </Typography>
                  </Box>
                  <IconButton size="small" onClick={clearSelection}>
                    <CloseIcon fontSize="small" />
                  </IconButton>
                </Box>

                {hasQuestions && (
                  <Box sx={{ mt: 2 }}>
                    <Alert severity="info" icon={<QuestionAnswerIcon />}>
                      {questions.length} tailoring questions available for this
                      position
                    </Alert>
                    <Button
                      variant="contained"
                      sx={{ mt: 2 }}
                      onClick={() => setActiveStep(1)}
                      endIcon={<NavigateNextIcon />}
                    >
                      Continue to Questions
                    </Button>
                  </Box>
                )}
              </Box>
            )}
          </Paper>
        );

      case 1:
        // Questions step
        if (!hasQuestions) return null;

        return (
          <Box>
            {currentQuestionIndex === 0 && (
              <Alert severity="info" sx={{ mb: 3 }} icon={<InfoIcon />}>
                <Typography variant="subtitle2" gutterBottom>
                  <strong>Tailoring Questions</strong>
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  The following questions will help tailor your resume to this
                  specific position. For best results:
                </Typography>
                <List dense sx={{ mt: 1 }}>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 28 }}>
                      <FiberManualRecordIcon sx={{ fontSize: 8 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          Use brief bullet points for clarity
                        </Typography>
                      }
                    />
                  </ListItem>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 28 }}>
                      <FiberManualRecordIcon sx={{ fontSize: 8 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          Focus on specific achievements and experiences
                        </Typography>
                      }
                    />
                  </ListItem>
                  <ListItem disableGutters>
                    <ListItemIcon sx={{ minWidth: 28 }}>
                      <FiberManualRecordIcon sx={{ fontSize: 8 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2">
                          Include metrics and results where possible
                        </Typography>
                      }
                    />
                  </ListItem>
                </List>
              </Alert>
            )}

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    mb: 2,
                  }}
                >
                  <Typography variant="h6">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </Typography>
                  <Chip
                    label={`${Object.keys(tempAnswers).length} answered`}
                    color={
                      Object.keys(tempAnswers).length === questions.length
                        ? "success"
                        : "default"
                    }
                    size="small"
                  />
                </Box>

                <Typography variant="body1" sx={{ mb: 3, fontWeight: 500 }}>
                  {questions[currentQuestionIndex]}
                </Typography>

                <TextField
                  fullWidth
                  multiline
                  rows={6}
                  variant="outlined"
                  placeholder="Enter your answer using bullet points for clarity..."
                  value={tempAnswers[currentQuestionIndex] || ""}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  helperText="Tip: Start each point with '•' or '-' for better formatting"
                />

                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    mt: 3,
                  }}
                >
                  <Button
                    onClick={handlePreviousQuestion}
                    disabled={currentQuestionIndex === 0}
                    startIcon={<NavigateBeforeIcon />}
                  >
                    Previous
                  </Button>

                  <Box sx={{ display: "flex", gap: 1 }}>
                    {questions.map((_, index) => (
                      <Box
                        key={index}
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          bgcolor:
                            index === currentQuestionIndex
                              ? "primary.main"
                              : tempAnswers[index]
                              ? "success.main"
                              : "action.disabled",
                          transition: "all 0.3s",
                        }}
                      />
                    ))}
                  </Box>

                  <Button
                    variant="contained"
                    onClick={handleNextQuestion}
                    endIcon={
                      currentQuestionIndex === questions.length - 1 ? (
                        <CheckCircleIcon />
                      ) : (
                        <NavigateNextIcon />
                      )
                    }
                  >
                    {currentQuestionIndex === questions.length - 1
                      ? "Review"
                      : "Next"}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Box>
        );

      case 2:
        // Review and upload step
        return (
          <Box>
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Ready to Parse & Tailor
                </Typography>

                <Box sx={{ mt: 2, mb: 3 }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                    <DescriptionIcon sx={{ mr: 1, color: "primary.main" }} />
                    <Typography variant="body2">
                      <strong>File:</strong> {selectedFile?.name}
                    </Typography>
                  </Box>

                  {jobAnalysis && (
                    <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                      <InfoIcon sx={{ mr: 1, color: "info.main" }} />
                      <Typography variant="body2">
                        <strong>Job Analysis:</strong> Active
                      </Typography>
                    </Box>
                  )}

                  {hasQuestions && (
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <QuestionAnswerIcon
                        sx={{ mr: 1, color: "success.main" }}
                      />
                      <Typography variant="body2">
                        <strong>Questions Answered:</strong>{" "}
                        {Object.keys(tempAnswers).length} of {questions.length}
                      </Typography>
                    </Box>
                  )}
                </Box>

                {hasQuestions &&
                  Object.keys(tempAnswers).length < questions.length && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      You haven't answered all questions. The resume will still
                      be tailored, but answering all questions provides better
                      results.
                    </Alert>
                  )}

                <Box sx={{ display: "flex", gap: 2 }}>
                  {hasQuestions && (
                    <Button
                      onClick={() => {
                        setActiveStep(1);
                        setCurrentQuestionIndex(0);
                      }}
                      startIcon={<NavigateBeforeIcon />}
                    >
                      Review Questions
                    </Button>
                  )}

                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleUpload}
                    disabled={uploading}
                    startIcon={
                      uploading ? (
                        <CircularProgress size={20} />
                      ) : (
                        <CloudUploadIcon />
                      )
                    }
                    sx={{ flex: 1 }}
                  >
                    {uploading
                      ? "Processing with AI..."
                      : "Parse & Tailor Resume"}
                  </Button>
                </Box>
              </CardContent>
            </Card>

            {uploading && (
              <Box sx={{ textAlign: "center", mt: 3 }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography variant="body1">
                  Analyzing your resume with AI...
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  This may take a few seconds
                </Typography>
              </Box>
            )}
          </Box>
        );

      default:
        return null;
    }
  };

  // Determine if we should show stepper
  const showStepper = selectedFile && hasQuestions;

  return (
    <Box sx={{ mb: 3 }}>
      {showStepper ? (
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          <Step>
            <StepLabel>Upload Resume</StepLabel>
          </Step>
          <Step>
            <StepLabel>Answer Questions</StepLabel>
          </Step>
          <Step>
            <StepLabel>Review & Parse</StepLabel>
          </Step>
        </Stepper>
      ) : (
        jobAnalysis && (
          <Alert severity="info" sx={{ mb: 2 }} icon={<InfoIcon />}>
            Job analysis active - your resume will be tailored to match the
            position requirements
          </Alert>
        )
      )}

      {getStepContent()}

      <Collapse in={!!error}>
        <Alert
          severity="error"
          sx={{ mt: 2 }}
          action={
            <IconButton size="small" onClick={() => setError(null)}>
              <CloseIcon fontSize="small" />
            </IconButton>
          }
        >
          {error}
        </Alert>
      </Collapse>

      <Collapse in={success}>
        <Alert severity="success" sx={{ mt: 2 }} icon={<CheckCircleIcon />}>
          Resume successfully parsed and tailored! Your information has been
          loaded into the form.
        </Alert>
      </Collapse>

      {!selectedFile && !hasQuestions && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            <strong>Tip:</strong> Add a job analysis to enable advanced CV
            tailoring with role-specific questions.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default CVUploaderWithQuestions;

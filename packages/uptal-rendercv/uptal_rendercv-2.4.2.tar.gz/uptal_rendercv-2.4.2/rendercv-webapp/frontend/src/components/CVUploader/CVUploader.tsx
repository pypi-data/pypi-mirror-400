import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Collapse
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import CloseIcon from '@mui/icons-material/Close';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import InfoIcon from '@mui/icons-material/Info';
import { cvApi } from '../../services/api';
import { useCV } from '../../hooks/useCV';

const CVUploader: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { loadCV, jobAnalysis, resumeAnswers } = useCV();

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
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/msword',
      'text/plain'
    ];
    
    const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      setError('Please upload a PDF, Word document, or text file');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setSuccess(false);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await cvApi.parseCV(selectedFile, jobAnalysis, resumeAnswers);
      
      if (result.success && result.cv_data) {
        // Load the parsed data into the form
        loadCV(result.cv_data);
        setSuccess(true);
        
        // Clear selection after successful upload
        setTimeout(() => {
          setSelectedFile(null);
          setSuccess(false);
        }, 3000);
      } else {
        setError(result.error || 'Failed to parse resume');
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'Failed to upload and parse resume');
    } finally {
      setUploading(false);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setError(null);
    setSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <Box sx={{ mb: 3 }}>
      <Paper
        sx={{
          p: 3,
          border: dragActive ? '2px dashed #1976d2' : '2px dashed #ccc',
          borderRadius: 2,
          bgcolor: dragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          cursor: 'pointer'
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={!selectedFile && !uploading ? handleButtonClick : undefined}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {!selectedFile && !uploading && (
          <Box sx={{ textAlign: 'center' }}>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'action.active', mb: 2 }} />
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
        )}

        {selectedFile && !uploading && (
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                <DescriptionIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="body1" sx={{ fontWeight: 500 }}>
                  {selectedFile.name}
                </Typography>
                <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>
                  ({(selectedFile.size / 1024).toFixed(1)} KB)
                </Typography>
              </Box>
              <IconButton size="small" onClick={clearSelection}>
                <CloseIcon fontSize="small" />
              </IconButton>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleUpload}
                disabled={uploading}
                startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
                fullWidth
              >
                {uploading ? 'Processing with AI...' : jobAnalysis ? 'Parse & Tailor Resume' : 'Parse Resume'}
              </Button>
            </Box>
            {jobAnalysis && !uploading && (
              <Box sx={{ mt: 2, p: 1.5, bgcolor: 'info.lighter', borderRadius: 1, display: 'flex', alignItems: 'flex-start' }}>
                <InfoIcon sx={{ fontSize: 18, mr: 1, mt: 0.25, color: 'info.main' }} />
                <Typography variant="caption" color="text.secondary">
                  Job analysis detected - resume will be tailored to match requirements
                  {resumeAnswers && Object.keys(resumeAnswers).length > 0 && 
                    ` (with ${Object.keys(resumeAnswers).length} answered questions)`
                  }
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {uploading && (
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="body1">
              Analyzing your resume with AI...
            </Typography>
            <Typography variant="caption" color="text.secondary">
              This may take a few seconds
            </Typography>
          </Box>
        )}
      </Paper>

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
        <Alert 
          severity="success" 
          sx={{ mt: 2 }}
          icon={<CheckCircleIcon />}
        >
          Resume successfully parsed! Your information has been loaded into the form.
        </Alert>
      </Collapse>

      <Box sx={{ mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          <strong>Tip:</strong> Upload your existing resume to automatically fill the form. 
          The AI will extract your information and format it properly. You can then edit any field manually.
        </Typography>
      </Box>
    </Box>
  );
};

export default CVUploader;
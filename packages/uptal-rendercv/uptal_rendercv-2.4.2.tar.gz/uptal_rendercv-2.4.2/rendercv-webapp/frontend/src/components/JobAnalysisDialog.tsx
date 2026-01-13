import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  IconButton,
  Tooltip,
  Typography,
  Box,
  Tabs,
  Tab,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemText,
  Paper
} from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';
import CloseIcon from '@mui/icons-material/Close';
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import QuestionAnswerIcon from '@mui/icons-material/QuestionAnswer';
import { useCV } from '../hooks/useCV';
import { JobAnalysis } from '../types/jobAnalysis.types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`job-analysis-tabpanel-${index}`}
      aria-labelledby={`job-analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 2 }}>{children}</Box>}
    </div>
  );
}

const JobAnalysisDialog: React.FC = () => {
  const { jobAnalysis, setJobAnalysis } = useCV();
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [tempAnalysis, setTempAnalysis] = useState<string>('');
  const [parsedAnalysis, setParsedAnalysis] = useState<JobAnalysis | null>(null);
  const [parseError, setParseError] = useState<string>('');

  const handleOpen = () => {
    setTempAnalysis(jobAnalysis ? JSON.stringify(jobAnalysis, null, 2) : '');
    setParsedAnalysis(jobAnalysis);
    setActiveTab(jobAnalysis ? 1 : 0);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    setParseError('');
  };

  const handleParseAnalysis = () => {
    try {
      const parsed = JSON.parse(tempAnalysis) as JobAnalysis;
      
      // Validate required fields
      if (!parsed.description) {
        throw new Error('Job analysis must include a description field');
      }
      
      setParsedAnalysis(parsed);
      setParseError('');
      setActiveTab(1);
    } catch (error: any) {
      setParseError(error.message || 'Invalid JSON format');
    }
  };

  const handleSave = () => {
    if (parsedAnalysis) {
      setJobAnalysis(parsedAnalysis);
      setOpen(false);
    }
  };

  const handleClear = () => {
    setJobAnalysis(null);
    setParsedAnalysis(null);
    setTempAnalysis('');
    setActiveTab(0);
  };

  const extractJobTitle = (description: string) => {
    // Try to extract job title from HTML description
    const textContent = description.replace(/<[^>]*>/g, ' ').trim();
    const lines = textContent.split('\n').filter(line => line.trim());
    if (lines.length > 0) {
      const firstLine = lines[0].replace(/Job Description:?/i, '').trim();
      const words = firstLine.split(' ').slice(0, 5).join(' ');
      return words || 'Job Position';
    }
    return 'Job Position';
  };


  return (
    <>
      <Tooltip title={jobAnalysis ? "Edit job analysis" : "Add job analysis for advanced CV tailoring"}>
        <IconButton
          onClick={handleOpen}
          color={jobAnalysis ? "primary" : "default"}
          sx={{ 
            position: 'relative',
            '&::after': jobAnalysis ? {
              content: '""',
              position: 'absolute',
              bottom: 4,
              right: 4,
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: 'primary.main'
            } : {}
          }}
        >
          <WorkIcon />
        </IconButton>
      </Tooltip>

      <Dialog 
        open={open} 
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WorkIcon color="primary" />
            <Typography variant="h6">Job Analysis</Typography>
          </Box>
          <IconButton
            onClick={handleClose}
            size="small"
            sx={{ color: 'text.secondary' }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </DialogTitle>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
            <Tab label="Import Analysis" icon={<ContentPasteIcon />} iconPosition="start" />
            <Tab 
              label="Review & Questions" 
              icon={<QuestionAnswerIcon />} 
              iconPosition="start"
              disabled={!parsedAnalysis}
            />
          </Tabs>
        </Box>
        
        <DialogContent sx={{ minHeight: 400 }}>
          <TabPanel value={activeTab} index={0}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Paste a job analysis JSON object that includes the job description, requirements, 
              and optional resume questions for enhanced CV tailoring.
            </Alert>
            
            <TextField
              fullWidth
              multiline
              rows={12}
              variant="outlined"
              placeholder='Paste job analysis JSON here...'
              value={tempAnalysis}
              onChange={(e) => setTempAnalysis(e.target.value)}
              error={!!parseError}
              helperText={parseError || `${tempAnalysis.length} characters`}
              sx={{
                '& .MuiOutlinedInput-root': {
                  fontFamily: 'monospace',
                  fontSize: '0.85rem'
                }
              }}
            />
            
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
              <Button 
                onClick={() => setTempAnalysis('')}
                disabled={!tempAnalysis}
              >
                Clear
              </Button>
              <Button 
                variant="contained"
                onClick={handleParseAnalysis}
                disabled={!tempAnalysis}
              >
                Parse & Continue
              </Button>
            </Box>
          </TabPanel>

          <TabPanel value={activeTab} index={1}>
            {parsedAnalysis && (
              <Box>
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    {extractJobTitle(parsedAnalysis.description)}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                    {parsedAnalysis.required_industry && (
                      <Chip 
                        label={`Industry: ${parsedAnalysis.required_industry}`} 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    )}
                    {parsedAnalysis.minimum_years_of_experience > 0 && (
                      <Chip 
                        label={`${parsedAnalysis.minimum_years_of_experience}+ years experience`} 
                        size="small" 
                        color="secondary" 
                        variant="outlined"
                      />
                    )}
                    <Chip 
                      label={`${parsedAnalysis.requirements?.length || 0} requirements`} 
                      size="small"
                    />
                    {parsedAnalysis.resume_questions?.length > 0 && (
                      <Chip 
                        label={`${parsedAnalysis.resume_questions.length} questions`} 
                        size="small"
                        icon={<QuestionAnswerIcon />}
                      />
                    )}
                  </Box>
                </Paper>

                {parsedAnalysis.resume_questions && parsedAnalysis.resume_questions.length > 0 ? (
                  <Box>
                    <Alert severity="info" icon={<QuestionAnswerIcon />}>
                      <Typography variant="subtitle2" gutterBottom>
                        {parsedAnalysis.resume_questions.length} Tailoring Questions Available
                      </Typography>
                      <Typography variant="body2">
                        These questions will be presented during the CV upload process to help tailor 
                        your resume to this specific role.
                      </Typography>
                    </Alert>
                    
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom color="text.secondary">
                        Questions Preview:
                      </Typography>
                      <List dense>
                        {parsedAnalysis.resume_questions.slice(0, 3).map((question, index) => (
                          <ListItem key={index}>
                            <ListItemText 
                              primary={`${index + 1}. ${question}`}
                              primaryTypographyProps={{ variant: 'body2' }}
                            />
                          </ListItem>
                        ))}
                        {parsedAnalysis.resume_questions.length > 3 && (
                          <ListItem>
                            <ListItemText 
                              primary={`... and ${parsedAnalysis.resume_questions.length - 3} more questions`}
                              primaryTypographyProps={{ variant: 'body2', color: 'text.secondary' }}
                            />
                          </ListItem>
                        )}
                      </List>
                    </Box>
                  </Box>
                ) : (
                  <Alert severity="info">
                    No resume questions provided. The CV will be tailored based on the job requirements 
                    and description only.
                  </Alert>
                )}
              </Box>
            )}
          </TabPanel>
        </DialogContent>
        
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={handleClear}
            disabled={!parsedAnalysis}
            color="error"
          >
            Clear Analysis
          </Button>
          <Box sx={{ flex: 1 }} />
          <Button onClick={handleClose}>
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            variant="contained"
            color="primary"
            disabled={!parsedAnalysis}
          >
            Save Analysis
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default JobAnalysisDialog;
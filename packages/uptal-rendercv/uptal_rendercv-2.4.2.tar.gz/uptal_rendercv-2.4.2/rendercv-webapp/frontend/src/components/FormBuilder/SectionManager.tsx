import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import { useCV } from '../../hooks/useCV';
import SectionEntry from './SectionEntry';
import { EntryType } from '../../types/cv.types';

const SECTION_TEMPLATES = {
  summary: 'BulletEntry',
  experience: 'ExperienceEntry',
  education: 'EducationEntry',
  skills: 'BulletEntry',
  languages: 'BulletEntry',
  projects: 'NormalEntry',
  publications: 'PublicationEntry',
  references: 'BulletEntry',
  custom: 'TextEntry'
} as const;

const SectionManager: React.FC = () => {
  const { cvData, addSection, removeSection, updateSection } = useCV();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newSectionName, setNewSectionName] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState<keyof typeof SECTION_TEMPLATES>('experience');

  const sections = cvData.cv.sections || {};
  
  // Order sections with summary first
  const orderedSectionEntries = React.useMemo(() => {
    const sectionEntries = Object.entries(sections);
    const priorityOrder = ['summary', 'experience', 'education', 'skills', 'languages', 'projects', 'publications', 'references'];
    
    // Sort sections based on priority order
    return sectionEntries.sort(([a], [b]) => {
      const aIndex = priorityOrder.indexOf(a.toLowerCase());
      const bIndex = priorityOrder.indexOf(b.toLowerCase());
      
      // If both are in priority list, sort by their index
      if (aIndex !== -1 && bIndex !== -1) {
        return aIndex - bIndex;
      }
      // If only a is in priority list, it comes first
      if (aIndex !== -1) return -1;
      // If only b is in priority list, it comes first
      if (bIndex !== -1) return 1;
      // Otherwise, maintain alphabetical order
      return a.localeCompare(b);
    });
  }, [sections]);

  const handleAddSection = () => {
    if (newSectionName.trim()) {
      addSection(newSectionName.trim());
      setNewSectionName('');
      setDialogOpen(false);
    }
  };

  const handleRemoveSection = (sectionName: string) => {
    if (window.confirm(`Are you sure you want to remove the "${sectionName}" section?`)) {
      removeSection(sectionName);
    }
  };

  const handleAddEntry = (sectionName: string) => {
    const currentEntries = sections[sectionName] || [];
    const entryType = detectEntryType(sectionName, currentEntries);
    const newEntry = createEmptyEntry(entryType);
    updateSection(sectionName, [...currentEntries, newEntry]);
  };

  const handleRemoveEntry = (sectionName: string, entryIndex: number) => {
    const currentEntries = sections[sectionName] || [];
    const newEntries = currentEntries.filter((_, i) => i !== entryIndex);
    updateSection(sectionName, newEntries);
  };

  const handleUpdateEntry = (sectionName: string, entryIndex: number, updatedEntry: any) => {
    const currentEntries = sections[sectionName] || [];
    const newEntries = [...currentEntries];
    newEntries[entryIndex] = updatedEntry;
    updateSection(sectionName, newEntries);
  };

  const detectEntryType = (sectionName: string, entries: any[]): EntryType => {
    // Try to detect from existing entries
    if (entries.length > 0) {
      const firstEntry = entries[0];
      if ('company' in firstEntry) return 'ExperienceEntry';
      if ('institution' in firstEntry) return 'EducationEntry';
      if ('bullet' in firstEntry) return 'BulletEntry';
      if ('title' in firstEntry && 'authors' in firstEntry) return 'PublicationEntry';
      if ('name' in firstEntry) return 'NormalEntry';
    }
    
    // Guess from section name
    const nameLower = sectionName.toLowerCase();
    if (nameLower.includes('experience') || nameLower.includes('work')) return 'ExperienceEntry';
    if (nameLower.includes('education')) return 'EducationEntry';
    if (nameLower.includes('skill')) return 'BulletEntry';
    if (nameLower.includes('publication')) return 'PublicationEntry';
    if (nameLower.includes('project')) return 'NormalEntry';
    
    return 'TextEntry';
  };

  const createEmptyEntry = (entryType: EntryType): any => {
    switch (entryType) {
      case 'ExperienceEntry':
        return { company: '', position: '', highlights: [] };
      case 'EducationEntry':
        return { institution: '', area: '', degree: '' };
      case 'BulletEntry':
        return { bullet: '' };
      case 'PublicationEntry':
        return { title: '', authors: '' };
      case 'NormalEntry':
        return { name: '', summary: '' };
      default:
        return { text: '' };
    }
  };

  return (
    <Box>
      {orderedSectionEntries.map(([sectionName, entries]) => (
        <Card key={sectionName} sx={{ mb: 2 }}>
          <CardHeader
            title={sectionName}
            action={
              <Box>
                <IconButton
                  color="primary"
                  onClick={() => handleAddEntry(sectionName)}
                  title="Add Entry"
                >
                  <AddIcon />
                </IconButton>
                <IconButton
                  color="error"
                  onClick={() => handleRemoveSection(sectionName)}
                  title="Remove Section"
                >
                  <DeleteIcon />
                </IconButton>
              </Box>
            }
          />
          <CardContent>
            {entries.length === 0 ? (
              <Typography color="text.secondary" align="center">
                No entries yet. Click + to add one.
              </Typography>
            ) : (
              entries.map((entry, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <SectionEntry
                    entry={entry}
                    entryType={detectEntryType(sectionName, entries)}
                    onChange={(updatedEntry) => handleUpdateEntry(sectionName, index, updatedEntry)}
                    onRemove={() => handleRemoveEntry(sectionName, index)}
                  />
                </Box>
              ))
            )}
          </CardContent>
        </Card>
      ))}

      <Button
        variant="contained"
        startIcon={<AddIcon />}
        onClick={() => setDialogOpen(true)}
        fullWidth
      >
        Add Section
      </Button>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Add New Section</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Section Name"
            fullWidth
            variant="outlined"
            value={newSectionName}
            onChange={(e) => setNewSectionName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <FormControl fullWidth>
            <InputLabel>Template</InputLabel>
            <Select
              value={selectedTemplate}
              label="Template"
              onChange={(e) => setSelectedTemplate(e.target.value as keyof typeof SECTION_TEMPLATES)}
            >
              <MenuItem value="experience">Experience</MenuItem>
              <MenuItem value="education">Education</MenuItem>
              <MenuItem value="skills">Skills</MenuItem>
              <MenuItem value="projects">Projects</MenuItem>
              <MenuItem value="publications">Publications</MenuItem>
              <MenuItem value="custom">Custom</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleAddSection} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SectionManager;
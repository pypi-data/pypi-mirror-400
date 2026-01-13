import React from "react";
import { Box, TextField, IconButton, Paper, Grid, Chip } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import AddIcon from "@mui/icons-material/Add";
import { EntryType } from "../../types/cv.types";

interface SectionEntryProps {
  entry: any;
  entryType: EntryType;
  onChange: (entry: any) => void;
  onRemove: () => void;
}

const SectionEntry: React.FC<SectionEntryProps> = ({
  entry,
  entryType,
  onChange,
  onRemove,
}) => {
  const handleFieldChange =
    (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
      onChange({ ...entry, [field]: event.target.value });
    };

  const addHighlight = () => {
    const highlights = entry.highlights || [];
    onChange({ ...entry, highlights: [...highlights, ""] });
  };

  const updateHighlight = (index: number, value: string) => {
    const highlights = [...(entry.highlights || [])];
    highlights[index] = value;
    onChange({ ...entry, highlights });
  };

  const removeHighlight = (index: number) => {
    const highlights = (entry.highlights || []).filter(
      (_: any, i: number) => i !== index
    );
    onChange({ ...entry, highlights });
  };

  const renderFields = () => {
    switch (entryType) {
      case "ExperienceEntry":
        return (
          <>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Company"
                  value={entry.company || ""}
                  onChange={handleFieldChange("company")}
                  size="small"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Position"
                  value={entry.position || ""}
                  onChange={handleFieldChange("position")}
                  size="small"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Location"
                  value={entry.location || ""}
                  onChange={handleFieldChange("location")}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  fullWidth
                  label="Start Date"
                  value={entry.start_date || ""}
                  onChange={handleFieldChange("start_date")}
                  placeholder="YYYY-MM"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  fullWidth
                  label="End Date"
                  value={entry.end_date || ""}
                  onChange={handleFieldChange("end_date")}
                  placeholder="YYYY-MM or present"
                  size="small"
                />
              </Grid>
            </Grid>
            {renderHighlights()}
          </>
        );

      case "EducationEntry":
        return (
          <>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Institution"
                  value={entry.institution || ""}
                  onChange={handleFieldChange("institution")}
                  size="small"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Field of Study"
                  value={entry.area || ""}
                  onChange={handleFieldChange("area")}
                  size="small"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Degree"
                  value={entry.degree || ""}
                  onChange={handleFieldChange("degree")}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Start Date"
                  value={entry.start_date || ""}
                  onChange={handleFieldChange("start_date")}
                  placeholder="YYYY-MM"
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="End Date"
                  value={entry.end_date || ""}
                  onChange={handleFieldChange("end_date")}
                  placeholder="YYYY-MM"
                  size="small"
                />
              </Grid>
            </Grid>
            {renderHighlights()}
          </>
        );

      case "BulletEntry":
        return (
          <TextField
            fullWidth
            label="Bullet Point"
            value={entry.bullet || ""}
            onChange={handleFieldChange("bullet")}
            size="small"
            required
          />
        );

      case "OneLineEntry":
        return (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Label"
                value={entry.label || ""}
                onChange={handleFieldChange("label")}
                size="small"
                required
              />
            </Grid>
            <Grid item xs={12} sm={8}>
              <TextField
                fullWidth
                label="Details"
                value={entry.details || ""}
                onChange={handleFieldChange("details")}
                size="small"
                required
              />
            </Grid>
          </Grid>
        );

      case "PublicationEntry":
        return (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={entry.title || ""}
                onChange={handleFieldChange("title")}
                size="small"
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Authors"
                value={entry.authors || ""}
                onChange={handleFieldChange("authors")}
                size="small"
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Journal"
                value={entry.journal || ""}
                onChange={handleFieldChange("journal")}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date"
                value={entry.date || ""}
                onChange={handleFieldChange("date")}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="DOI"
                value={entry.doi || ""}
                onChange={handleFieldChange("doi")}
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="URL"
                value={entry.url || ""}
                onChange={handleFieldChange("url")}
                size="small"
              />
            </Grid>
          </Grid>
        );

      case "NormalEntry":
        return (
          <>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={8}>
                <TextField
                  fullWidth
                  label="Name"
                  value={entry.name || ""}
                  onChange={handleFieldChange("name")}
                  size="small"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  label="Location"
                  value={entry.location || ""}
                  onChange={handleFieldChange("location")}
                  size="small"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Summary"
                  value={entry.summary || ""}
                  onChange={handleFieldChange("summary")}
                  multiline
                  rows={2}
                  size="small"
                />
              </Grid>
            </Grid>
            {renderHighlights()}
          </>
        );

      default:
        return (
          <TextField
            fullWidth
            label="Text"
            value={entry.text || ""}
            onChange={handleFieldChange("text")}
            multiline
            rows={3}
            size="small"
          />
        );
    }
  };

  const renderHighlights = () => {
    if (
      !["ExperienceEntry", "EducationEntry", "NormalEntry"].includes(entryType)
    ) {
      return null;
    }

    const highlights = entry.highlights || [];

    return (
      <Box sx={{ mt: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
          <Chip label="Highlights" size="small" />
          <IconButton size="small" onClick={addHighlight} sx={{ ml: 1 }}>
            <AddIcon fontSize="small" />
          </IconButton>
        </Box>
        {highlights.map((highlight: string, index: number) => (
          <Box
            key={index}
            sx={{ display: "flex", alignItems: "center", mb: 1 }}
          >
            <TextField
              fullWidth
              value={highlight}
              onChange={(e) => updateHighlight(index, e.target.value)}
              placeholder="Add a highlight..."
              size="small"
              sx={{ mr: 1 }}
            />
            <IconButton
              size="small"
              color="error"
              onClick={() => removeHighlight(index)}
            >
              <DeleteIcon fontSize="small" />
            </IconButton>
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <Paper sx={{ p: 2, position: "relative" }}>
      <IconButton
        size="small"
        color="error"
        onClick={onRemove}
        sx={{ position: "absolute", top: 8, right: 8 }}
      >
        <DeleteIcon />
      </IconButton>
      <Box sx={{ pr: 5 }}>{renderFields()}</Box>
    </Paper>
  );
};

export default SectionEntry;

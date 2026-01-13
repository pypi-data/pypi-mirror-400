import React, { useState, useEffect } from "react";
import {
  Box,
  Drawer,
  Typography,
  IconButton,
  List,
  ListItem,
  Paper,
  CircularProgress,
  Alert,
  Button,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import RefreshIcon from "@mui/icons-material/Refresh";
import { useCV } from "../../hooks/useCV";
import { CVDesign, Theme } from "../../types/cv.types";
import { cvApi } from "../../services/api";

interface TemplateGalleryProps {
  open: boolean;
  onClose: () => void;
}

const TemplateGallery: React.FC<TemplateGalleryProps> = ({ open, onClose }) => {
  const { cvData, updateDesign } = useCV();
  const [selectedTemplate, setSelectedTemplate] = useState<CVDesign["theme"]>(
    cvData.design.theme
  );
  const [templates, setTemplates] = useState<Theme[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      fetchTemplates();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const fetchTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const themes = await cvApi.getThemes();
      setTemplates(themes);
    } catch (err: any) {
      console.error("Failed to fetch themes:", err);
      setError("Failed to load templates. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId as CVDesign["theme"]);
    updateDesign({ theme: templateId as CVDesign["theme"] });
    onClose();
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        "& .MuiDrawer-paper": {
          width: 400,
          bgcolor: "#f8f9fa",
        },
      }}
    >
      <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
        {/* Header */}
        <Box
          sx={{
            p: 3,
            borderBottom: 1,
            borderColor: "divider",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            bgcolor: "white",
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            Resume Template Gallery
          </Typography>
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        {/* Template List */}
        <Box sx={{ flex: 1, overflowY: "auto", p: 2 }}>
          {loading && (
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                py: 8,
                gap: 2,
              }}
            >
              <CircularProgress />
              <Typography variant="body2" color="text.secondary">
                Loading templates...
              </Typography>
            </Box>
          )}

          {error && (
            <Box sx={{ p: 2 }}>
              <Alert
                severity="error"
                action={
                  <Button
                    color="inherit"
                    size="small"
                    startIcon={<RefreshIcon />}
                    onClick={fetchTemplates}
                  >
                    Retry
                  </Button>
                }
              >
                {error}
              </Alert>
            </Box>
          )}

          {!loading && !error && templates.length > 0 && (
            <List sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              {templates.map((template) => (
                <ListItem
                  key={template.id}
                  disablePadding
                  onClick={() => handleTemplateSelect(template.id)}
                  sx={{ cursor: "pointer" }}
                >
                  <Paper
                    sx={{
                      width: "100%",
                      p: 2,
                      border: 2,
                      borderColor:
                        selectedTemplate === template.id
                          ? "primary.main"
                          : "transparent",
                      "&:hover": {
                        borderColor:
                          selectedTemplate === template.id
                            ? "primary.main"
                            : "grey.300",
                        boxShadow: 2,
                      },
                      transition: "all 0.2s",
                    }}
                  >
                    <Typography
                      variant="subtitle1"
                      sx={{ mb: 1, fontWeight: 500 }}
                    >
                      {template.name}
                    </Typography>
                    <Box
                      sx={{
                        width: "100%",
                        bgcolor: "white",
                        border: 1,
                        borderColor: "grey.200",
                        borderRadius: 1,
                        overflow: "hidden",
                      }}
                    >
                      {template.image ? (
                        <Box
                          component="img"
                          src={template.image}
                          alt={template.name}
                          sx={{
                            width: "100%",
                            height: "auto",
                            display: "block",
                          }}
                        />
                      ) : (
                        <Box
                          sx={{
                            width: "100%",
                            height: 200,
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          <Typography variant="body2" color="text.secondary">
                            {selectedTemplate === template.id
                              ? "Selected"
                              : "Preview"}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  </Paper>
                </ListItem>
              ))}
            </List>
          )}
        </Box>
      </Box>
    </Drawer>
  );
};

export default TemplateGallery;

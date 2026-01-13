import React, { useEffect, useState } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  SelectChangeEvent,
  Typography
} from '@mui/material';
import { useCV } from '../../hooks/useCV';
import { cvApi } from '../../services/api';
import { Theme } from '../../types/cv.types';

const ThemeSelector: React.FC = () => {
  const { cvData, updateDesign } = useCV();
  const [themes, setThemes] = useState<Theme[]>([]);

  useEffect(() => {
    // Load available themes
    cvApi.getThemes().then(setThemes).catch(console.error);
  }, []);

  const handleThemeChange = (event: SelectChangeEvent) => {
    updateDesign({ theme: event.target.value as any });
  };

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <FormControl fullWidth size="small">
          <InputLabel>Theme</InputLabel>
          <Select
            value={cvData.design.theme}
            label="Theme"
            onChange={handleThemeChange}
          >
            {themes.map((theme) => (
              <MenuItem key={theme.id} value={theme.id}>
                {theme.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Grid>
      <Grid item xs={12}>
        <Typography variant="caption" color="text.secondary">
          Theme colors and fonts are pre-configured. Advanced customization coming soon!
        </Typography>
      </Grid>
    </Grid>
  );
};

export default ThemeSelector;
import { CVData } from "../types/cv.types";

// Helper function to clean entry objects - converts empty strings to undefined
const cleanEntryFields = (entry: any): any => {
  const cleaned = { ...entry };

  // Convert empty strings to undefined for all fields
  Object.keys(cleaned).forEach((key) => {
    if (cleaned[key] === "") {
      delete cleaned[key];
    }
  });

  // Clean highlights array - remove empty strings
  if (cleaned.highlights) {
    cleaned.highlights = cleaned.highlights.filter((h: string) => h.trim() !== "");
    if (cleaned.highlights.length === 0) {
      delete cleaned.highlights;
    }
  }

  return cleaned;
};

export const prepareCVData = (cvData: CVData): CVData => {
  // Clean up the data before sending - remove empty strings and empty objects
  const cleanedCV = { ...cvData.cv };

  // Remove empty string fields from CV
  Object.keys(cleanedCV).forEach((key) => {
    if (cleanedCV[key as keyof typeof cleanedCV] === "") {
      delete cleanedCV[key as keyof typeof cleanedCV];
    }
  });

  // Remove empty social networks array
  if (cleanedCV.social_networks?.length === 0) {
    delete cleanedCV.social_networks;
  }

  // Clean all section entries - convert empty strings to undefined
  if (cleanedCV.sections) {
    Object.keys(cleanedCV.sections).forEach((sectionName) => {
      const section = cleanedCV.sections![sectionName];
      if (Array.isArray(section)) {
        cleanedCV.sections![sectionName] = section.map(cleanEntryFields);
      }
    });
  }

  // Reorder sections with summary first
  if (cleanedCV.sections) {
    const sections = cleanedCV.sections;
    const orderedSections: any = {};

    // Define the preferred order of sections
    const sectionOrder = [
      "summary",
      "experience",
      "education",
      "skills",
      "languages",
      "projects",
      "publications",
      "references",
    ];

    // Add sections in the preferred order
    sectionOrder.forEach((sectionName) => {
      if (sections[sectionName] && sections[sectionName].length > 0) {
        orderedSections[sectionName] = sections[sectionName];
      }
    });

    // Add any remaining custom sections
    Object.keys(sections).forEach((sectionName) => {
      if (
        !sectionOrder.includes(sectionName) &&
        sections[sectionName].length > 0
      ) {
        orderedSections[sectionName] = sections[sectionName];
      }
    });

    // Only include sections if there are any
    if (Object.keys(orderedSections).length > 0) {
      cleanedCV.sections = orderedSections;
    } else {
      delete cleanedCV.sections;
    }
  }

  return {
    cv: cleanedCV,
    design: cvData.design,
  };
};

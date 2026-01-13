import React, { useState, useEffect } from "react";
import { CalendarToday, Add } from "@mui/icons-material";
import { useCV } from "../../hooks/useCV";
import { ExperienceEntry } from "../../types/cv.types";
import { IconPencil, IconTrashX } from "@tabler/icons-react";
interface LocalWorkExperienceEntry {
  id: string;
  company: string;
  position: string;
  location?: string;
  startDate: string;
  endDate: string;
  description: string;
}

// Helper function to normalize date format for input fields
const normalizeDateForInput = (date: string): string => {
  if (!date) return "";
  // If date is in YYYY-MM format, append -01 to make it YYYY-MM-DD
  if (/^\d{4}-\d{2}$/.test(date)) {
    return `${date}-01`;
  }
  // If already in YYYY-MM-DD format, return as is
  if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return date;
  }
  return date;
};

// Helper function to normalize date format for API
const normalizeDateForApi = (date: string): string => {
  if (!date) return "";
  // Remove the day part if present (YYYY-MM-DD -> YYYY-MM)
  if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    return date.substring(0, 7);
  }
  return date;
};

const WorkExperienceForm: React.FC = () => {
  const { cvData, updateSection } = useCV();
  const [workEntries, setWorkEntries] = useState<LocalWorkExperienceEntry[]>([
    {
      id: "1",
      company: "",
      position: "",
      location: "",
      startDate: "",
      endDate: "",
      description: "",
    },
  ]);

  // Load work experience data from CV provider on component mount
  useEffect(() => {
    const experienceSection = cvData.cv.sections?.experience || [];
    if (experienceSection.length > 0) {
      const localEntries: LocalWorkExperienceEntry[] = experienceSection.map(
        (entry, index) => ({
          id: (index + 1).toString(),
          company: (entry as any).company || "",
          position: (entry as any).position || "",
          location: (entry as any).location || "",
          startDate: normalizeDateForInput((entry as any).start_date || ""),
          endDate: normalizeDateForInput((entry as any).end_date || ""),
          description: (entry as any).highlights?.join("\n") || "",
        })
      );
      setWorkEntries(localEntries);
    }
  }, [cvData.cv.sections?.experience]);

  const handleInputChange = (
    id: string,
    field: keyof LocalWorkExperienceEntry,
    value: string
  ) => {
    setWorkEntries((prev) => {
      const updatedEntries = prev.map((entry) =>
        entry.id === id ? { ...entry, [field]: value } : entry
      );

      // Convert to CV format and save to provider
      const cvExperienceEntries: ExperienceEntry[] = updatedEntries.map(
        (entry) => ({
          company: entry.company,
          position: entry.position,
          location: entry.location,
          start_date: normalizeDateForApi(entry.startDate),
          end_date: normalizeDateForApi(entry.endDate),
          highlights: entry.description
            ? entry.description.split("\n").filter((line) => line.trim())
            : [],
        })
      );

      updateSection("experience", cvExperienceEntries);
      return updatedEntries;
    });
  };

  const addWorkExperience = () => {
    const newId = (workEntries.length + 1).toString();
    const newEntries = [
      ...workEntries,
      {
        id: newId,
        company: "",
        position: "",
        location: "",
        startDate: "",
        endDate: "",
        description: "",
      },
    ];
    setWorkEntries(newEntries);

    // Update CV provider
    const cvExperienceEntries: ExperienceEntry[] = newEntries.map((entry) => ({
      company: entry.company,
      position: entry.position,
      location: entry.location,
      start_date: normalizeDateForApi(entry.startDate),
      end_date: normalizeDateForApi(entry.endDate),
      highlights: entry.description
        ? entry.description.split("\n").filter((line) => line.trim())
        : [],
    }));
    updateSection("experience", cvExperienceEntries);
  };

  const deleteWorkExperience = (id: string) => {
    const newEntries = workEntries.filter((entry) => entry.id !== id);
    setWorkEntries(newEntries);

    // Update CV provider
    const cvExperienceEntries: ExperienceEntry[] = newEntries.map((entry) => ({
      company: entry.company,
      position: entry.position,
      location: entry.location,
      start_date: normalizeDateForApi(entry.startDate),
      end_date: normalizeDateForApi(entry.endDate),
      highlights: entry.description
        ? entry.description.split("\n").filter((line) => line.trim())
        : [],
    }));
    updateSection("experience", cvExperienceEntries);
  };


  return (
    <div className=" py-2 ">
      <div className="space-y-4">
        {workEntries.map((entry) => (
          <div
            key={entry.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-gray-100">
              <div className="flex items-center space-x-3">
                <h3 className="text-lg font-semibold text-gray-900">
                  Work experience
                </h3>
                <IconPencil className="text-gray-400 cursor-pointer hover:text-gray-600" />
              </div>
              <IconTrashX
                className=" cursor-pointer text-red-500 hover:text-red-700"
                onClick={() => deleteWorkExperience(entry.id)}
              />
            </div>

            {/* Form Fields */}
            <div className="p-4 space-y-4">
              {/* Company and Position Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Company Field */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Company
                  </label>
                  <input
                    type="text"
                    value={entry.company}
                    onChange={(e) =>
                      handleInputChange(entry.id, "company", e.target.value)
                    }
                    placeholder="Company name"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  />
                </div>

                {/* Position Field */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Position
                  </label>
                  <input
                    type="text"
                    value={entry.position}
                    onChange={(e) =>
                      handleInputChange(entry.id, "position", e.target.value)
                    }
                    placeholder="UI/UX Designer"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  />
                </div>
              </div>

              {/* Location Field */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Location
                </label>
                <input
                  type="text"
                  value={entry.location || ""}
                  onChange={(e) =>
                    handleInputChange(entry.id, "location", e.target.value)
                  }
                  placeholder="City, Country"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>

              {/* Date Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Start Date */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Start date
                  </label>
                  <div className="relative">
                    <input
                      type="date"
                      value={entry.startDate}
                      onChange={(e) =>
                        handleInputChange(entry.id, "startDate", e.target.value)
                      }
                      className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-0 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:right-3 [&::-webkit-calendar-picker-indicator]:w-5 [&::-webkit-calendar-picker-indicator]:h-5"
                    />
                    <CalendarToday 
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm pointer-events-none" 
                    />
                  </div>
                </div>

                {/* End Date */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    End date
                  </label>
                  <div className="relative">
                    <input
                      type="date"
                      value={entry.endDate}
                      onChange={(e) =>
                        handleInputChange(entry.id, "endDate", e.target.value)
                      }
                      className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:opacity-0 [&::-webkit-calendar-picker-indicator]:absolute [&::-webkit-calendar-picker-indicator]:right-3 [&::-webkit-calendar-picker-indicator]:w-5 [&::-webkit-calendar-picker-indicator]:h-5"
                    />
                    <CalendarToday 
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm pointer-events-none" 
                    />
                  </div>
                </div>
              </div>

              {/* Description Field */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  What did you do?
                </label>
                <div className="relative">
                  <textarea
                    value={entry.description}
                    onChange={(e) =>
                      handleInputChange(entry.id, "description", e.target.value)
                    }
                    placeholder="Enter your responsibilities and achievements..."
                    rows={6}
                    className="w-full px-4 py-2 pb-12 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none"
                  />
                  {/* <button
                    onClick={() => handleAIRewrite(entry.id)}
                    className="absolute bottom-2 right-2 flex items-center space-x-1 px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors duration-200"
                  >
                    <AutoFixHigh className="text-xs" />
                    <span>Rewrite with AI</span>
                  </button> */}
                </div>
              </div>
            </div>

            {/* AI Suggestion Section */}
            {/* <div className="bg-gray-50 p-4 border-t border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AutoFixHigh className="text-blue-500 text-sm" />
                  <span className="text-sm font-medium text-gray-700">
                    AI Suggestion
                  </span>
                </div>
                <button
                  onClick={handleResolveSuggestion}
                  className="px-3 py-1 text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Resolve
                </button>
              </div>
              <div className="mt-2 flex items-start space-x-2">
                <Warning className="text-red-500 text-sm mt-0.5" />
                <p className="text-sm text-gray-600">
                  Education Dates Missing in license degree In Business
                  Management at University of Hassiba Benbouali
                </p>
              </div>
            </div> */}
          </div>
        ))}

        {/* Add Work Experience Button */}
        <div className="w-full flex justify-center ">
          <button
            onClick={addWorkExperience}
            className="w-full text-center flex items-center justify-center space-x-2 px-6 py-3 border-2 border-dashed border-gray-300 rounded-lg bg-white text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-all duration-200  "
          >
            <Add className="text-lg" />
            <span className="font-medium">Add Work Experience</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkExperienceForm;

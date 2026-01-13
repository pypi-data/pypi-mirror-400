import React, { useState, useEffect } from "react";
import { DragIndicator, CalendarToday, Add } from "@mui/icons-material";
import { useCV } from "../../hooks/useCV";
import { EducationEntry } from "../../types/cv.types";
import { IconPencil, IconTrashX } from "@tabler/icons-react";

interface LocalEducationEntry {
  id: string;
  university: string;
  degree?: string;
  area: string;
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

const EducationForm: React.FC = () => {
  const { cvData, updateSection } = useCV();
  const [educationEntries, setEducationEntries] = useState<
    LocalEducationEntry[]
  >([
    {
      id: "1",
      university: "",
      degree: "",
      area: "",
      location: "",
      startDate: "",
      endDate: "",
      description: "",
    },
  ]);

  // Load education data from CV provider on component mount
  useEffect(() => {
    const educationSection = cvData.cv.sections?.education || [];
    if (educationSection.length > 0) {
      const localEntries: LocalEducationEntry[] = educationSection.map(
        (entry, index) => ({
          id: (index + 1).toString(),
          university: (entry as any).institution || "",
          degree: (entry as any).degree || "",
          area: (entry as any).area || "",
          location: (entry as any).location || "",
          startDate: normalizeDateForInput((entry as any).start_date || ""),
          endDate: normalizeDateForInput((entry as any).end_date || ""),
          description: (entry as any).highlights?.join("\n") || "",
        })
      );
      setEducationEntries(localEntries);
    }
  }, [cvData.cv.sections?.education]);

  const handleInputChange = (
    id: string,
    field: keyof LocalEducationEntry,
    value: string
  ) => {
    setEducationEntries((prev) => {
      const updatedEntries = prev.map((entry) =>
        entry.id === id ? { ...entry, [field]: value } : entry
      );

      // Convert to CV format and save to provider
      const cvEducationEntries: EducationEntry[] = updatedEntries.map(
        (entry) => ({
          institution: entry.university,
          degree: entry.degree,
          area: entry.area,
          location: entry.location,
          start_date: normalizeDateForApi(entry.startDate),
          end_date: normalizeDateForApi(entry.endDate),
          highlights: entry.description
            ? entry.description.split("\n").filter((line) => line.trim())
            : [],
        })
      );

      updateSection("education", cvEducationEntries);
      return updatedEntries;
    });
  };

  const addEducation = () => {
    const newId = (educationEntries.length + 1).toString();
    const newEntries = [
      ...educationEntries,
      {
        id: newId,
        university: "",
        degree: "",
        area: "",
        location: "",
        startDate: "",
        endDate: "",
        description: "",
      },
    ];
    setEducationEntries(newEntries);

    // Update CV provider
    const cvEducationEntries: EducationEntry[] = newEntries.map((entry) => ({
      institution: entry.university,
      degree: entry.degree,
      area: entry.area,
      location: entry.location,
      start_date: normalizeDateForApi(entry.startDate),
      end_date: normalizeDateForApi(entry.endDate),
      highlights: entry.description
        ? entry.description.split("\n").filter((line) => line.trim())
        : [],
    }));
    updateSection("education", cvEducationEntries);
  };

  const deleteEducation = (id: string) => {
    const newEntries = educationEntries.filter((entry) => entry.id !== id);
    setEducationEntries(newEntries);

    // Update CV provider
    const cvEducationEntries: EducationEntry[] = newEntries.map((entry) => ({
      institution: entry.university,
      degree: entry.degree,
      area: entry.area,
      location: entry.location,
      start_date: normalizeDateForApi(entry.startDate),
      end_date: normalizeDateForApi(entry.endDate),
      highlights: entry.description
        ? entry.description.split("\n").filter((line) => line.trim())
        : [],
    }));
    updateSection("education", cvEducationEntries);
  };

  return (
    <div className="  ">
      <div className="space-y-4">
        {educationEntries.map((entry, index) => (
          <div
            key={entry.id}
            className="bg-white rounded-lg shadow-sm border border-gray-200"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-gray-100">
              <div className="flex items-center space-x-3">
                <DragIndicator className="text-gray-400 cursor-move" />
                <h3 className="text-lg font-medium text-gray-900">
                  Education {index + 1}
                </h3>
                <IconPencil className="text-gray-400 cursor-pointer hover:text-gray-600" />
              </div>
              <IconTrashX
                className=" cursor-pointer text-red-500 hover:text-red-700"
                onClick={() => deleteEducation(entry.id)}
              />
            </div>

            {/* Form Fields */}
            <div className="p-4 space-y-4">
              {/* University Field */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  University
                </label>
                <input
                  type="text"
                  value={entry.university}
                  onChange={(e) =>
                    handleInputChange(entry.id, "university", e.target.value)
                  }
                  placeholder="University name"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
              </div>

              {/* Degree and Area Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Degree Field */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Degree
                  </label>
                  <input
                    type="text"
                    value={entry.degree || ""}
                    onChange={(e) =>
                      handleInputChange(entry.id, "degree", e.target.value)
                    }
                    placeholder="BS, BA, MS, PhD, etc."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  />
                </div>

                {/* Area/Field of Study */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Field of Study
                  </label>
                  <input
                    type="text"
                    value={entry.area}
                    onChange={(e) =>
                      handleInputChange(entry.id, "area", e.target.value)
                    }
                    placeholder="Computer Science, Business, etc."
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
                    <CalendarToday className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm pointer-events-none" />
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
                    <CalendarToday className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 text-sm pointer-events-none" />
                  </div>
                </div>
              </div>

              {/* Description Field */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  value={entry.description}
                  onChange={(e) =>
                    handleInputChange(entry.id, "description", e.target.value)
                  }
                  placeholder="Enter a description..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none"
                />
              </div>
            </div>
          </div>
        ))}

        {/* Add Education Button */}
        <div className="flex justify-center">
          <button
            onClick={addEducation}
            className="w-full flex justify-center text-center items-center space-x-2 px-6 py-2 border-2 border-dashed border-gray-300 rounded-lg bg-white text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-all duration-200"
          >
            <Add className="text-lg" />
            <span className="font-medium">Add Education</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default EducationForm;

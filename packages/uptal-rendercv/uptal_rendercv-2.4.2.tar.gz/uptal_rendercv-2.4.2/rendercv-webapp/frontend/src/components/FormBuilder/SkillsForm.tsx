import React, { useState, useEffect } from "react";
import { DragIndicator, Close } from "@mui/icons-material";
import { useCV } from "../../hooks/useCV";
import { BulletEntry } from "../../types/cv.types";

interface LocalSkillEntry {
  id: string;
  category: string;
  skills: string[];
}

const SkillsForm: React.FC = () => {
  const { cvData, updateSection } = useCV();
  const [skillEntries, setSkillEntries] = useState<LocalSkillEntry[]>([
    {
      id: "1",
      category: "Skills",
      skills: ["UI UX Desginer", "UI UX Desginer", "User researcher"],
    },
    {
      id: "2",
      category: "Languages",
      skills: ["French", "English"],
    },
  ]);

  // Load skills and languages data from CV provider on component mount
  useEffect(() => {
    const skillsSection = cvData.cv.sections?.skills || [];
    const languagesSection = cvData.cv.sections?.languages || [];

    // Always show both Skills and Languages entries
    setSkillEntries([
      {
        id: "1",
        category: "Skills",
        skills: skillsSection.map((entry) => (entry as BulletEntry).bullet),
      },
      {
        id: "2",
        category: "Languages",
        skills: languagesSection.map((entry) => (entry as BulletEntry).bullet),
      },
    ]);
  }, [cvData.cv.sections?.skills, cvData.cv.sections?.languages]);

  const [newSkillByCategory, setNewSkillByCategory] = useState<{
    [key: string]: string;
  }>({
    "1": "",
    "2": "",
  });

  const addSkill = (entryId: string) => {
    const skillToAdd = newSkillByCategory[entryId];
    if (skillToAdd && skillToAdd.trim()) {
      setSkillEntries((prev) => {
        const updatedEntries = prev.map((entry) =>
          entry.id === entryId
            ? { ...entry, skills: [...entry.skills, skillToAdd.trim()] }
            : entry
        );

        // Convert to CV format and save to provider
        const skillsEntry = updatedEntries.find(
          (entry) => entry.category === "Skills"
        );
        const languagesEntry = updatedEntries.find(
          (entry) => entry.category === "Languages"
        );

        if (skillsEntry) {
          const cvSkillsEntries: BulletEntry[] = skillsEntry.skills.map(
            (skill) => ({
              bullet: skill,
            })
          );
          updateSection("skills", cvSkillsEntries);
        }

        if (languagesEntry) {
          const cvLanguagesEntries: BulletEntry[] = languagesEntry.skills.map(
            (language) => ({
              bullet: language,
            })
          );
          updateSection("languages", cvLanguagesEntries);
        }

        return updatedEntries;
      });
      setNewSkillByCategory((prev) => ({ ...prev, [entryId]: "" }));
    }
  };

  const removeSkill = (entryId: string, skillIndex: number) => {
    setSkillEntries((prev) => {
      const updatedEntries = prev.map((entry) =>
        entry.id === entryId
          ? {
              ...entry,
              skills: entry.skills.filter((_, index) => index !== skillIndex),
            }
          : entry
      );

      // Convert to CV format and save to provider
      const skillsEntry = updatedEntries.find(
        (entry) => entry.category === "Skills"
      );
      const languagesEntry = updatedEntries.find(
        (entry) => entry.category === "Languages"
      );

      if (skillsEntry) {
        const cvSkillsEntries: BulletEntry[] = skillsEntry.skills.map(
          (skill) => ({
            bullet: skill,
          })
        );
        updateSection("skills", cvSkillsEntries);
      }

      if (languagesEntry) {
        const cvLanguagesEntries: BulletEntry[] = languagesEntry.skills.map(
          (language) => ({
            bullet: language,
          })
        );
        updateSection("languages", cvLanguagesEntries);
      }

      return updatedEntries;
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent, entryId: string) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addSkill(entryId);
    }
  };

  return (
    <div className="bg-white py-2">
      <div className="space-y-6">
        {skillEntries.map((entry) => (
          <div key={entry.id} className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <DragIndicator className="text-gray-400 cursor-move" />
                <h3 className="text-lg font-medium text-gray-900">
                  {entry.category}
                </h3>
              </div>
            </div>

            {/* Form Fields */}
            <div className="px-3">
              {/* Skills/Languages Field */}
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  {entry.category}
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={newSkillByCategory[entry.id] || ""}
                    onChange={(e) =>
                      setNewSkillByCategory((prev) => ({
                        ...prev,
                        [entry.id]: e.target.value,
                      }))
                    }
                    onKeyPress={(e) => handleKeyPress(e, entry.id)}
                    placeholder={`Add ${entry.category.toLowerCase()}...`}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  />
                  <button
                    onClick={() => addSkill(entry.id)}
                    className="px-4 py-2 border border-gray-300 rounded-md bg-white text-gray-700 hover:bg-gray-50 transition-colors duration-200 text-sm"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>

            {/* Skill Tags */}
            {entry.skills.length > 0 && (
              <div className="flex flex-wrap gap-2 px-3">
                {entry.skills.map((skill, skillIndex) => (
                  <div
                    key={skillIndex}
                    className="flex items-center space-x-1 bg-blue-50 text-blue-500 font-semibold px-3 py-0 rounded-full text-sm"
                  >
                    <span>{skill}</span>
                    <button
                      onClick={() => removeSkill(entry.id, skillIndex)}
                      className="hover:bg-blue-200 rounded-full p-0.5 transition-colors duration-200"
                    >
                      <Close className="text-xs" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default SkillsForm;

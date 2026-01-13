import React, { useState, useEffect } from "react";
import { useCV } from "../../hooks/useCV";
import { BulletEntry } from "../../types/cv.types";

const SummaryForm: React.FC = () => {
  const { cvData, updateSection } = useCV();
  const [summary, setSummary] = useState<string>("");

  // Load summary data from CV provider on component mount
  useEffect(() => {
    const summarySection = cvData.cv.sections?.summary || [];
    if (summarySection.length > 0) {
      // Join all summary bullet points into a single text
      const summaryText = summarySection
        .map((entry) => (entry as BulletEntry).bullet)
        .join("\n");
      setSummary(summaryText);
    }
  }, [cvData.cv.sections?.summary]);

  const handleSummaryChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newSummary = e.target.value;
    setSummary(newSummary);

    // Convert to CV format and save to provider
    const summaryEntries: BulletEntry[] = newSummary
      .split("\n")
      .filter((line) => line.trim())
      .map((line) => ({
        bullet: line.trim(),
      }));

    updateSection("summary", summaryEntries);
  };

  return (
    <div className="  ">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white     ">
          {/* Summary Input Field */}
          <div className="space-y-2 pt-2">
            <label className="block text-sm font-medium text-gray-800">
              Write a professional summary
            </label>
            <textarea
              value={summary}
              onChange={handleSummaryChange}
              placeholder="E.g 5+ years experience with react"
              rows={8}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 resize-none"
            />
          </div>

          {/* Character Count (Optional) */}
          {/* <div className="mt-2 text-right">
            <span className="text-xs text-gray-500">
              {summary.length} characters
            </span>
          </div> */}

          {/* Help Text */}
          {/* <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              💡 <strong>Tip:</strong> Keep your summary concise (2-3 sentences)
              and highlight your most relevant experience and skills for the
              position you're applying for.
            </p>
          </div> */}
        </div>
      </div>
    </div>
  );
};

export default SummaryForm;

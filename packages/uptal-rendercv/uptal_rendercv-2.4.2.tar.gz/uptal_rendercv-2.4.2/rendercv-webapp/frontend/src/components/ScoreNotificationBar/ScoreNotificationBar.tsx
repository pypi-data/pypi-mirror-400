import React, { useMemo } from "react";
import { useCV } from "../../hooks/useCV";
import { transformAPIResponseToAIReviewData } from "../AIReview/AIReview";

const ScoreNotificationBar: React.FC = () => {
  const { hasAnalysisCompleted, setShowAIReview, apiResponse } = useCV();

  // Extract position_match from analysis
  const score = useMemo(() => {
    if (apiResponse) {
      const aiReviewData = transformAPIResponseToAIReviewData(apiResponse);
      return aiReviewData.score || 0;
    }
    return 0;
  }, [apiResponse]);

  if (!hasAnalysisCompleted) {
    return null;
  }

  const handleScoreDetailsClick = () => {
    setShowAIReview(true);
  };

  return (
    <div className="bg-white border-b border-gray-200 px-4 sm:px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-4 flex-1">
        {/* Circular Score Icon */}
        <div className="relative flex-shrink-0 w-12 h-12">
          <svg
            width="48"
            height="48"
            viewBox="0 0 48 48"
            className="transform -rotate-90"
          >
            {/* Background circle (light gray) */}
            <circle
              cx="24"
              cy="24"
              r="20"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="4"
            />
            {/* Progress arc (dynamic score, starting from top) */}
            <circle
              cx="24"
              cy="24"
              r="20"
              fill="none"
              stroke="#f97316"
              strokeWidth="4"
              strokeDasharray={`${(score / 100) * 125.66} 125.66`}
              strokeLinecap="round"
              strokeDashoffset="0"
            />
          </svg>
          {/* Score text in center */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-[#ea580c] font-semibold text-sm leading-none">
              {score}%
            </span>
          </div>
        </div>

        {/* Message */}
        <span className="text-gray-700 text-sm sm:text-base">
          This score is outdated.
        </span>
      </div>

      {/* Score Details Button */}
      <button
        onClick={handleScoreDetailsClick}
        className="flex-shrink-0 px-4 py-2 border border-gray-300 rounded-lg bg-white text-blue-600 hover:bg-gray-50 transition-colors duration-200 font-medium text-sm sm:text-base"
      >
        Score Details
      </button>
    </div>
  );
};

export default ScoreNotificationBar;

import React from "react";
import {
  IconArrowLeft,
  IconRefresh,
  IconTrendingUp,
} from "@tabler/icons-react";
import { IconBulb, IconAlertCircle } from "@tabler/icons-react";
// @ts-ignore - react-apexcharts type issue
import ReactApexChart from "react-apexcharts";

const Chart = ReactApexChart as any;

export interface AIReviewData {
  score: number;
  previousScore?: number;
  summary?: string;
  strengths?: string[];
  weaknesses?: string[];
  suggestions?: Array<{
    icon: "bulb" | "alert";
    title: string;
    description: string;
  }>;
  comparisonData?: number[]; // Distribution data for histogram
}

// API Response structure (what we expect from backend)
interface APIResponse {
  data?: {
    analysis?: {
      analysis?: {
        position_match?: number;
        original_position_match?: number;
        ai_review_summary?: string;
        ai_review_strengths?: string[];
        ai_review_weaknesses?: string[];
      };
    };
    position_match?: number;
    original_position_match?: number;
    previous_score?: number;
    related_cvs?: Array<{
      position_match?: number;
    }>;
  };
  // Also support direct structure for backward compatibility
  analysis?: {
    analysis?: {
      position_match?: number;
      original_position_match?: number;
      ai_review_summary?: string;
      ai_review_strengths?: string[];
      ai_review_weaknesses?: string[];
    };
  };
  position_match?: number;
  original_position_match?: number;
  previous_score?: number;
  related_cvs?: Array<{
    position_match?: number;
  }>;
}

/**
 * Transform API response to AIReviewData format
 * @param apiResponse - The API response object
 * @returns Transformed AIReviewData object
 */
export const transformAPIResponseToAIReviewData = (
  apiResponse: APIResponse
): AIReviewData => {
  // Handle both nested (data.analysis.analysis) and direct (analysis.analysis) structures
  const data = apiResponse.data || apiResponse;
  const analysis = data.analysis?.analysis;
  const score =
    data.position_match ??
    analysis?.position_match ??
    apiResponse.position_match ??
    0;

  // Get previous score from API response using original_position_match
  const previousScore =
    analysis?.original_position_match ??
    data.original_position_match ??
    apiResponse.original_position_match ??
    (() => {
      // Fallback: get from related CVs if original_position_match is not available
      const relatedCvs = data.related_cvs || apiResponse.related_cvs;
      return relatedCvs && relatedCvs.length > 1
        ? relatedCvs[relatedCvs.length - 2]?.position_match
        : undefined;
    })();

  return {
    score,
    previousScore,
    summary: analysis?.ai_review_summary,
    strengths: analysis?.ai_review_strengths,
    weaknesses: analysis?.ai_review_weaknesses,
    // suggestions and comparisonData can be added later if needed
  };
};

interface AIReviewProps {
  onBack: () => void;
  onRefresh?: () => void;
  data?: AIReviewData;
}

const AIReview: React.FC<AIReviewProps> = ({ onBack, onRefresh, data }) => {
  if (!data) {
    return (
      <div className="h-full bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  const score = data.score;
  const previousScore = data.previousScore;
  const improvement = previousScore ? score - previousScore : 0;
  const radialBarState = React.useMemo(
    () => ({
      series: [score],
      options: {
        chart: {
          type: "radialBar",
          offsetY: -20,
          sparkline: {
            enabled: true,
          },
        },
        plotOptions: {
          radialBar: {
            startAngle: -90,
            endAngle: 90,
            hollow: {
              margin: 0,
              size: "70%",
              background: "#fff",
              image: undefined,
              position: "front",
              dropShadow: {
                enabled: false,
              },
            },
            track: {
              background: "#e7e7e7",
              strokeWidth: "67%",
              margin: 0,
            },
            dataLabels: {
              show: false,
            },
          },
        },
        colors: ["#ABE5A1"],
        fill: {
          type: "gradient",
          gradient: {
            shade: "light",
            type: "horizontal",
            shadeIntensity: 0.5,
            gradientToColors: ["#3B82F6"],
            inverseColors: false,
            opacityFrom: 1,
            opacityTo: 1,
            stops: [0, 100],
          },
        },
        stroke: {
          lineCap: "round",
        },
      },
    }),
    [score]
  );

  return (
    <div className="h-full bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between sticky top-0 z-10">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
        >
          <IconArrowLeft size={20} />
          <span className="font-medium">Back</span>
        </button>
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
          >
            <IconRefresh size={20} />
            <span className="font-medium">Refresh</span>
          </button>
        )}
      </div>

      {/* Title */}
      <div className="bg-white px-6 py-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">AI Review</h1>
      </div>

      {/* Content */}
      <div className="bg-white flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {/* Resume Match Score Section */}
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Resume Match Score
          </h2>

          <div className="flex flex-col lg:flex-row gap-8">
            {/* Left - Score Gauge (RadialBar) */}
            <div className="flex-1 flex flex-col items-center relative">
              <div className="relative w-full">
                {/* @ts-ignore */}
                <Chart
                  options={radialBarState.options}
                  series={radialBarState.series}
                  type="radialBar"
                  width={"100%"}
                  height={200}
                />
                {/* Score Label and Value Overlay */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <div className="text-[#9CA3AF] text-base font-normal mb-1">
                    Score
                  </div>
                  <div className="text-[#111111] text-[42px] font-bold leading-none">
                    {Math.round(score)}%
                  </div>
                </div>
              </div>
              {/* Improvement Indicator */}
              { previousScore && (
                <div className="flex flex-col items-center ">
                  <div className="flex items-center gap-1 text-green-600 font-medium">
                    <IconTrendingUp size={20} />
                    <span>+{Math.round(improvement)}%</span>
                  </div>
                  <div className="text-sm text-gray-600 ">
                    from previous score of {Math.round(previousScore)}%
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Summary Section */}
        {data.summary && (
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Summary
            </h2>
            <p className="text-gray-700 leading-relaxed">{data.summary}</p>
          </div>
        )}

        {/* Strengths Section */}
        {data.strengths && data.strengths.length > 0 && (
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Strengths
            </h2>
            <ul className="space-y-3">
              {data.strengths.map((strength, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-gray-500 mt-2 flex-shrink-0" />
                  <span className="text-gray-700">{strength}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Weaknesses Section */}
        {data.weaknesses && data.weaknesses.length > 0 && (
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Weaknesses
            </h2>
            <ul className="space-y-3">
              {data.weaknesses.map((weakness, idx) => (
                <li key={idx} className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 rounded-full bg-gray-500 mt-2 flex-shrink-0" />
                  <span className="text-gray-700">{weakness}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Boost Your Score Section */}
        {data.suggestions && data.suggestions.length > 0 && (
          <div className="bg-white rounded-lg p-5 shadow-sm  border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Boost Your Score
            </h2>
            <div className="">
              {data.suggestions.map((suggestion, idx) => (
                <div
                  key={idx}
                  className="   p-2 flex items-start gap-4 hover:border-gray-300 transition-colors"
                >
                  <div className="flex-shrink-0 mt-1">
                    {suggestion.icon === "bulb" ? (
                      <IconBulb
                        size={24}
                        className="text-yellow-500"
                        style={{
                          filter: "drop-shadow(0 0 4px rgba(234, 179, 8, 0.5))",
                        }}
                      />
                    ) : (
                      <IconAlertCircle size={24} className="text-red-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-900 font-medium mb-1">
                      {suggestion.title}
                    </p>
                    <p className="text-gray-600 text-sm">
                      {suggestion.description}
                    </p>
                  </div>
                  {/* <button className="flex-shrink-0 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium text-sm">
                    Resolve
                  </button> */}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIReview;

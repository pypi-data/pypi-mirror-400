import React from "react";
import { useCV } from "../../hooks/useCV";
import { SocialNetworkName } from "../../types/cv.types";
import { IconTrashX } from "@tabler/icons-react";
import { Add } from "@mui/icons-material";

const PersonalInfo: React.FC = () => {
  const { cvData, updatePersonalInfo } = useCV();
  const { cv } = cvData;

  const handleChange =
    (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      updatePersonalInfo({ [field]: value } as any);
    };

  const handleSocialNetworkChange = (
    index: number,
    field: "network" | "username",
    value: string
  ) => {
    const existing = cv.social_networks || [];
    const updated = [...existing];
    updated[index] = {
      ...updated[index],
      [field]: value as any,
    };
    updatePersonalInfo({ social_networks: updated });
  };

  const addSocialNetwork = () => {
    const existing = cv.social_networks || [];
    const updated = [...existing, { network: "LinkedIn" as SocialNetworkName, username: "" }];
    updatePersonalInfo({ social_networks: updated });
  };

  const removeSocialNetwork = (index: number) => {
    const existing = cv.social_networks || [];
    const updated = existing.filter((_, i) => i !== index);
    updatePersonalInfo({ social_networks: updated });
  };

  const socialNetworkOptions: SocialNetworkName[] = [
    "LinkedIn",
    "GitHub",
    "GitLab",
    "Instagram",
    "ORCID",
    "Mastodon",
    "StackOverflow",
    "ResearchGate",
    "YouTube",
    "Google Scholar",
    "Telegram",
    "X",
  ];

  const getPlaceholder = (network: SocialNetworkName): string => {
    switch (network) {
      case "Mastodon":
        return "@username@domain";
      case "StackOverflow":
        return "user_id/username";
      case "ORCID":
        return "0000-0000-0000-0000";
      case "YouTube":
        return "username (no @)";
      default:
        return "username";
    }
  };

  const formFields = [
    {
      id: "name",
      label: "Full name",
      placeholder: "Full name",
      value: cv.name || "",
      required: true,
    },
    {
      id: "email",
      label: "Email address",
      placeholder: "your.email@example.com",
      value: cv.email || "",
      type: "email",
    },
    {
      id: "phone",
      label: "Phone number",
      placeholder: "Phone number",
      value: cv.phone || "",
    },
    {
      id: "website",
      label: "Personal website or relevant link",
      placeholder: "mywebsite.com",
      value: cv.website || "",
      type:"url"
    },
    {
      id: "location",
      label: "Location",
      placeholder: "City, Country",
      value: cv.location || "",
    },
  ];

  return (
    <div className=" bg-white">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {formFields.map((field) => (
          <div key={field.id} className="space-y-1">
            <label
              htmlFor={field.id}
              className="block text-sm font-medium text-gray-700"
            >
              {field.label}
              {field.required && <span className="text-orange-500 ml-1">*</span>}
            </label>
            <input
              id={field.id}
              type={field.type || "text"}
              value={field.value}
              onChange={handleChange(field.id)}
              placeholder={field.placeholder}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
            />
          </div>
        ))}
      </div>

      {/* Social Networks Section */}
      <div className="mt-6 space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Social Networks
        </label>

        {cv.social_networks && cv.social_networks.length > 0 && (
          <div className="space-y-3">
            {cv.social_networks.map((social, index) => (
              <div key={index} className="flex gap-3 items-start">
                <select
                  value={social.network}
                  onChange={(e) =>
                    handleSocialNetworkChange(
                      index,
                      "network",
                      e.target.value
                    )
                  }
                  className="w-40 px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                >
                  {socialNetworkOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  value={social.username}
                  onChange={(e) =>
                    handleSocialNetworkChange(index, "username", e.target.value)
                  }
                  placeholder={getPlaceholder(social.network)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                />
                <button
                  onClick={() => removeSocialNetwork(index)}
                  className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-all duration-200"
                >
                  <IconTrashX size={20} />
                </button>
              </div>
            ))}
          </div>
        )}

        <button
          onClick={addSocialNetwork}
          className="flex items-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg bg-white text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-all duration-200"
        >
          <Add className="text-lg" />
          <span className="text-sm font-medium">Add Social Network</span>
        </button>
      </div>
    </div>
  );
};

export default PersonalInfo;

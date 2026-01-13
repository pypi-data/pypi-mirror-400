export type SocialNetworkName =
  | "LinkedIn"
  | "GitHub"
  | "GitLab"
  | "Instagram"
  | "ORCID"
  | "Mastodon"
  | "StackOverflow"
  | "ResearchGate"
  | "YouTube"
  | "Google Scholar"
  | "Telegram"
  | "X";

export interface SocialNetwork {
  network: SocialNetworkName;
  username: string;
}

export interface CVPersonalInfo {
  name: string;
  label?: string;
  location?: string;
  email?: string;
  phone?: string;
  website?: string;
  social_networks?: SocialNetwork[];
}

export interface ExperienceEntry {
  company: string;
  position: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  highlights?: string[];
}

export interface EducationEntry {
  institution: string;
  area: string;
  degree?: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  highlights?: string[];
}

export interface BulletEntry {
  bullet: string;
}

export interface OneLineEntry {
  label: string;
  details: string;
}

export interface NormalEntry {
  name: string;
  location?: string;
  summary?: string;
  highlights?: string[];
}

export interface PublicationEntry {
  title: string;
  authors: string;
  journal?: string;
  date?: string;
  doi?: string;
  url?: string;
}

export type CVEntry =
  | ExperienceEntry
  | EducationEntry
  | BulletEntry
  | OneLineEntry
  | NormalEntry
  | PublicationEntry;

export interface CVSections {
  [key: string]: CVEntry[];
}

export interface CVDesign {
  theme:
    | "classic"
    | "sb2nov"
    | "moderncv"
    | "engineeringresumes"
    | "engineeringclassic";
  colors?: {
    text?: string;
    name?: string;
    connections?: string;
    section_titles?: string;
    links?: string;
  };
  text?: {
    font_family?: string;
    font_size?: string;
    alignment?: string;
  };
  page?: {
    size?: string;
    top_margin?: string;
    bottom_margin?: string;
    left_margin?: string;
    right_margin?: string;
  };
}

export interface CVData {
  cv: {
    state: string;
    city: string;
    name: string;
    label?: string;
    location?: string;
    email?: string;
    phone?: string;
    website?: string;
    social_networks?: SocialNetwork[];
    sections?: CVSections;
  };
  design: CVDesign;
  locale?: string;
}

export type EntryType =
  | "ExperienceEntry"
  | "EducationEntry"
  | "BulletEntry"
  | "NormalEntry"
  | "PublicationEntry"
  | "TextEntry"
  | "OneLineEntry";

export interface Theme {
  id: string;
  name: string;
  image?: string;
}

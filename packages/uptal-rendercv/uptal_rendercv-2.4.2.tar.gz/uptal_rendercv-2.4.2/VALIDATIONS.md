# RenderCV Validations

This file summarizes the validation rules enforced by the RenderCV Python models and
utilities. It is derived from the Pydantic models and custom validators in `rendercv/`.

## Global model rules

- Extra keys are forbidden for models that inherit from
  `rendercv/data/models/base.py:RenderCVBaseModelWithoutExtraKeys`.
- Extra keys are allowed for models that inherit from
  `rendercv/data/models/base.py:RenderCVBaseModelWithExtraKeys`.

## CV (`cv`) validations

Source: `rendercv/data/models/curriculum_vitae.py`

- `email`: must be a valid email address (`pydantic.EmailStr`).
- `website`: free text (no URL validation).
- `photo`: converted to an absolute path based on the input file directory.
- `phone`: no validation (accepted as a string).
- `social_networks`: validated list of `SocialNetwork` entries (see below).
- `sections` (alias of `sections_input`):
  - must be a mapping of section title -> list of entries.
  - each section list is validated as a single entry type (see "Section entry rules").

## Social network validations

Source: `rendercv/data/models/curriculum_vitae.py`

- `network`: free text (no validation).
- `username`: free text (no validation).
- Derived `url`:
  - if `network` is one of the built-ins, its base URL is used.
  - otherwise, `username` is treated as the URL.

## Section entry rules

Source: `rendercv/data/models/curriculum_vitae.py`

- Each section must be a list.
- The first recognizable entry determines the section's entry type.
- All entries in the section are validated against that entry type model.
- If no entry type can be determined, validation fails.

## Entry types and date validations

Source: `rendercv/data/models/entry_types.py`

- `date` (EntryWithDate):
  - accepts `YYYY-MM-DD`, `YYYY-MM`, or `YYYY` (string or int).
  - accepts arbitrary strings (not rejected if not date-like).
  - `datetime.date` inputs are converted to ISO strings.
- `start_date` and `end_date`:
  - accept `YYYY-MM-DD`, `YYYY-MM`, or `YYYY`.
  - `end_date` may also be `"present"`.
  - if `start_date` is provided and `end_date` is missing, `end_date` becomes
    `"present"`.
  - if `start_date` is after `end_date`, validation fails.
  - if `date` is provided, `start_date`/`end_date` are ignored.
- `highlights`:
  - must be a list of strings.
  - occurrences of `" - "` are converted to nested bullets (`"\n    - "`).
- `PublicationEntry`:
  - `doi` must match pattern `10.*` (`\b10\..*`).
  - `url` must be a valid HTTP/HTTPS URL if provided.
  - if `doi` is provided, `url` is cleared (ignored).

## Design and theme validations

Source: `rendercv/data/models/design.py`

- Built-in themes (`classic`, `sb2nov`, `engineeringresumes`, `engineeringclassic`,
  `moderncv`) are validated against their theme option models.
- Custom theme name must be alphanumeric only.
- Custom theme folder must exist alongside the input file.
- Required template files must exist in the custom theme folder:
  `Preamble.j2.typ`, `Header.j2.typ`, `SectionBeginning.j2.typ`,
  `SectionEnding.j2.typ`, plus one `*.j2.typ` template for each entry type.
- If a custom theme has an `__init__.py`, it must import cleanly and expose a
  `ThemeOptions` model; syntax or import errors cause validation to fail.

## RenderCV settings validations

Source: `rendercv/data/models/rendercv_settings.py`

- `output_folder_name`: placeholders are replaced (see descriptions in code).
- Path fields (`design`, `rendercv_settings`, `locale`, `pdf_path`, `typst_path`,
  `html_path`, `png_path`, `markdown_path`):
  - placeholders are replaced.
  - relative paths are converted to absolute paths.
- `date`: stored as a `datetime.date` and also sets the global `DATE_INPUT` used for
  computed dates.

## Locale validations

Source: `rendercv/data/models/locale.py`

- `language`: must be ISO 639 alpha-2 (`LanguageAlpha2`).
- `phone_number_format`: must be `national`, `international`, or `E164`.
- `abbreviations_for_months` and `full_names_of_months`:
  - must be lists of length 12.

## Theme options validations

Source: `rendercv/themes/options.py`

- `TypstDimension`: must match `number + unit` where unit is one of
  `cm`, `in`, `pt`, `mm`, `ex`, `em` (e.g., `0.5cm`).
- `FontFamily`:
  - if a local `fonts` directory exists, any value is allowed.
  - otherwise, must be one of the allowed built-in font families.
- `Color` fields: must be valid color values (name, hex, rgb, hsl), as enforced by
  `pydantic_extra_types.color.Color`.
- Enumerated fields:
  - `BulletPoint`, `PageSize`, `Alignment`, `TextAlignment`, `SectionTitleType` are
    fixed literal sets.
- `header.separator_between_connections`: `None` is coerced to an empty string.

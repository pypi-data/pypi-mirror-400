# Backend Configuration

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

### Required Variables

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# CV API Configuration
CV_API_BASE_URL=https://api-v2.uptal.com/cv-enhance
CV_API_TIMEOUT=10
```

## Variable Descriptions

- **OPENAI_API_KEY**: Your OpenAI API key for resume parsing functionality
- **CV_API_BASE_URL**: Base URL for the CV enhancement API (default: https://api-v2.uptal.com/cv-enhance)
- **CV_API_TIMEOUT**: Timeout in seconds for CV API requests (default: 10)

## Usage

The CV service will automatically read these environment variables when initialized. If `CV_API_BASE_URL` is not set, it will default to `https://api-v2.uptal.com/cv-enhance`.


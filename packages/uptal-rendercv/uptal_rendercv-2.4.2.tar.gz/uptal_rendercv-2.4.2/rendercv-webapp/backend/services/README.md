# Backend Services

This directory contains service modules that handle external API integrations and business logic.

## CV Service (`cv_service.py`)

Handles interaction with the Uptal CV API.

### Features

- Fetches CV data using a unique CV code
- Updates CV with new file uploads
- Configurable base URL via environment variables
- Comprehensive error handling with custom exceptions
- Timeout configuration support

### Usage

```python
from services import CVService, CVServiceException

# Initialize the service (reads from environment variables)
cv_service = CVService()

# Fetch CV data
try:
    cv_data = cv_service.get_cv_by_code("Cv9E#nH4$xTz8!pY2aW^mK6rL")
    print(cv_data)
except CVServiceException as e:
    print(f"Error: {e.message} (Status: {e.status_code})")

# Update CV with new file
try:
    with open('updated_resume.pdf', 'rb') as cv_file:
        result = cv_service.update_cv_edits("Cv9E#nH4$xTz8!pY2aW^mK6rL", cv_file)
        print(result)
except CVServiceException as e:
    print(f"Error: {e.message} (Status: {e.status_code})")
```

### Exception Hierarchy

- `CVServiceException` - Base exception for all CV service errors
  - `CVNotFoundException` - CV not found (404)
  - `CVTimeoutException` - Request timeout (504)
  - `CVAPIException` - General API errors (500 or custom status)

### Configuration

Set these environment variables in your `.env` file:

```env
CV_API_BASE_URL=https://api-v2.uptal.com/cv-enhance
CV_API_TIMEOUT=10
```

### API Endpoints

The service calls:

#### 1. Get CV Data
```
GET {CV_API_BASE_URL}/{cv_code}
```

Example:
```
GET https://api-v2.uptal.com/cv-enhance/Cv9E%23nH4%24xTz8%21pY2aW%5EmK6rL
```

#### 2. Update CV with New File
```
POST {CV_API_BASE_URL}/{cv_code}/edits
```

Example:
```bash
curl -X POST https://api-v2.uptal.com/cv-enhance/ABC123XYZ/edits \
  -F "cv=@updated_resume.pdf"
```

**What Happens on Update:**
1. ✅ Old CV file deleted from storage
2. ✅ New CV uploaded
3. ✅ CV text extracted
4. ✅ CV data re-parsed
5. ✅ Database record updated:
   - `cv_path`: new file path
   - `cv_data`: new parsed data
   - `status`: `processing`
   - `cv_enhance_status`: `processing`
6. ✅ CV Enhancement Job dispatched
7. ✅ CV Analysis Job dispatched
8. 📡 Socket Event: `cv_updated` emitted

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "cv_code": "ABC123XYZ",
    "cv_id": 456,
    "application_id": null,
    "status": "draft",
    "cv_updated": true,
    "message": "CV updated and enhancement started"
  }
}
```

Note: Special characters in the cv_code should be URL-encoded.


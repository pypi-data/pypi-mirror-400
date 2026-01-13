"""Service for fetching CV data from external API."""
import os
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse


class CVService:
    """Service class for interacting with the CV API."""
    
    def __init__(self):
        """Initialize the CV service with base URL from environment."""
        self.default_base_url = os.getenv('CV_API_BASE_URL', 'https://api.uptal.com/cv-enhance')
        self.timeout = int(os.getenv('CV_API_TIMEOUT', '10'))

    def _resolve_base_url(self, redirect_url: Optional[str]) -> str:
        """
        Decide which CV API host to use based on the redirect URL domain.

        Mapping:
        - dev.uptal.com -> api-v2.uptal.com
        - staging.uptal.com -> api-staging.uptal.com
        - anything else -> api.uptal.com
        """
        if not redirect_url:
            return self.default_base_url

        try:
            host = urlparse(redirect_url).netloc.lower()
        except Exception:
            return self.default_base_url

        if "dev.uptal.com" in host:
            return "https://api-v2.uptal.com/cv-enhance"
        if "staging.uptal.com" in host:
            return "https://api-staging.uptal.com/cv-enhance"
        return "https://api.uptal.com/cv-enhance"
    
    def get_cv_by_code(self, cv_code: str, redirect_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch CV data from the API using cv_code.

        Args:
            cv_code: The unique CV code identifier

        Returns:
            Dictionary containing CV data

        Raises:
            CVNotFoundException: When CV is not found (404)
            CVAPIException: For other API errors
            CVTimeoutException: When request times out
        """
        try:
            base_url = self._resolve_base_url(redirect_url)
            api_url = f"{base_url}/{cv_code}"
            print(f"Fetching CV from: {api_url}")

            response = requests.get(api_url, timeout=self.timeout)

            # Handle different status codes
            if response.status_code == 404:
                raise CVNotFoundException(f"CV not found: {cv_code}")
            elif response.status_code != 200:
                raise CVAPIException(
                    f"API returned status code {response.status_code}",
                    status_code=response.status_code
                )

            # Parse and return the JSON response
            cv_data = response.json()
            print(f"Successfully fetched CV data for code: {cv_code}")

            return cv_data

        except requests.exceptions.Timeout:
            raise CVTimeoutException(f"Request to CV API timed out after {self.timeout}s")
        except requests.exceptions.RequestException as e:
            raise CVAPIException(f"Failed to fetch CV: {str(e)}")
        except ValueError as e:
            # JSON decode error
            raise CVAPIException(f"Invalid response format from CV API: {str(e)}")

    def update_cv_edits(self, cv_code: str, cv_file, redirect_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Update CV with new file via the API.

        This method posts the updated CV file to the API, which will:
        1. Delete old CV file from storage
        2. Upload new CV file
        3. Extract CV text
        4. Re-parse CV data
        5. Update database record
        6. Dispatch CV Enhancement Job
        7. Dispatch CV Analysis Job
        8. Emit socket event: cv_updated

        Args:
            cv_code: The unique CV code identifier
            cv_file: File object containing the updated CV (PDF)

        Returns:
            Dictionary containing update response with:
            - status: success/error
            - data: {cv_code, cv_id, application_id, status, cv_updated, message}

        Raises:
            CVNotFoundException: When CV is not found (404)
            CVAPIException: For other API errors
            CVTimeoutException: When request times out
        """
        try:
            base_url = self._resolve_base_url(redirect_url)
            api_url = f"{base_url}/{cv_code}/edits"
            print(f"Updating CV at: {api_url}")

            # Prepare multipart file upload
            files = {'cv': cv_file}

            response = requests.post(
                api_url,
                files=files,
                timeout=self.timeout * 3  # Longer timeout for file upload and processing
            )

            # Handle different status codes
            if response.status_code == 404:
                raise CVNotFoundException(f"CV not found: {cv_code}")
            elif response.status_code not in [200, 201]:
                raise CVAPIException(
                    f"API returned status code {response.status_code}: {response.text}",
                    status_code=response.status_code
                )

            # Parse and return the JSON response
            result = response.json()
            print(f"Successfully updated CV for code: {cv_code}")

            return result

        except requests.exceptions.Timeout:
            raise CVTimeoutException(f"Request to CV API timed out after {self.timeout * 3}s")
        except requests.exceptions.RequestException as e:
            raise CVAPIException(f"Failed to update CV: {str(e)}")
        except ValueError as e:
            # JSON decode error
            raise CVAPIException(f"Invalid response format from CV API: {str(e)}")


# Custom exceptions for better error handling
class CVServiceException(Exception):
    """Base exception for CV Service."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class CVNotFoundException(CVServiceException):
    """Exception raised when CV is not found."""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class CVTimeoutException(CVServiceException):
    """Exception raised when request times out."""
    def __init__(self, message: str):
        super().__init__(message, status_code=504)


class CVAPIException(CVServiceException):
    """Exception raised for API errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, status_code=status_code)


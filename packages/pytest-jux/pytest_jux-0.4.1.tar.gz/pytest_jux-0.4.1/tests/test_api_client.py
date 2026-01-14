# SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
# SPDX-License-Identifier: Apache-2.0

"""Tests for Jux API client (Jux API v1.0.0).

Tests the HTTP client for publishing signed JUnit XML reports to the
Jux API Server v1.0.0 /junit/submit endpoint.
"""

import pytest
import responses
from requests.exceptions import HTTPError, RequestException, Timeout

from pytest_jux.api_client import JuxAPIClient, PublishResponse


class TestJuxAPIClient:
    """Test suite for JuxAPIClient (Jux API v1.0.0)."""

    @pytest.fixture
    def api_url(self) -> str:
        """Base API URL for testing."""
        return "http://localhost:4000/api/v1"

    @pytest.fixture
    def bearer_token(self) -> str:
        """Test Bearer token."""
        return "test-bearer-token-12345"

    @pytest.fixture
    def client(self, api_url: str) -> JuxAPIClient:
        """Create API client without authentication (localhost)."""
        return JuxAPIClient(api_url=api_url)

    @pytest.fixture
    def authenticated_client(self, api_url: str, bearer_token: str) -> JuxAPIClient:
        """Create API client with Bearer token authentication."""
        return JuxAPIClient(api_url=api_url, bearer_token=bearer_token)

    @pytest.fixture
    def signed_xml(self) -> str:
        """Sample signed JUnit XML with metadata and XMLDsig signature."""
        return """<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <SignedInfo>
      <CanonicalizationMethod Algorithm="http://www.w3.org/2006/12/xml-c14n11"/>
      <SignatureMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
      <Reference URI="">
        <Transforms>
          <Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"/>
        </Transforms>
        <DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <DigestValue>base64-digest</DigestValue>
      </Reference>
    </SignedInfo>
    <SignatureValue>base64-signature</SignatureValue>
    <KeyInfo>
      <X509Data>
        <X509Certificate>base64-cert</X509Certificate>
      </X509Data>
    </KeyInfo>
  </Signature>
  <testsuite name="Tests" tests="10" failures="2" errors="1" time="5.5">
    <properties>
      <property name="project" value="my-application"/>
      <property name="git:branch" value="main"/>
      <property name="git:commit" value="abc123def456"/>
      <property name="jux:pytest_jux_version" value="0.3.0"/>
    </properties>
    <testcase classname="TestClass" name="test_example" time="0.1"/>
  </testsuite>
</testsuites>"""

    def test_client_initialization_without_auth(self, api_url: str) -> None:
        """Test client initialization for localhost (no authentication)."""
        client = JuxAPIClient(api_url=api_url)
        assert client.api_url == api_url
        assert client.timeout == 30  # default
        assert "Authorization" not in client.session.headers
        assert client.session.headers["Content-Type"] == "application/xml"

    def test_client_initialization_with_bearer_token(
        self, api_url: str, bearer_token: str
    ) -> None:
        """Test client initialization with Bearer token authentication."""
        client = JuxAPIClient(api_url=api_url, bearer_token=bearer_token)
        assert client.api_url == api_url
        assert client.session.headers["Authorization"] == f"Bearer {bearer_token}"
        assert client.session.headers["Content-Type"] == "application/xml"

    def test_client_initialization_custom_timeout(self, api_url: str) -> None:
        """Test client initialization with custom timeout."""
        client = JuxAPIClient(api_url=api_url, timeout=60)
        assert client.timeout == 60

    def test_client_initialization_strips_trailing_slash(self) -> None:
        """Test that trailing slash is removed from API URL."""
        client = JuxAPIClient(api_url="http://localhost:4000/api/v1/")
        assert client.api_url == "http://localhost:4000/api/v1"

    @responses.activate
    def test_publish_report_success_201(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test successful report publishing (201 Created)."""
        # Mock API response (Jux API v1.0.0 format)
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "message": "Test report submitted successfully",
                "status": "success",
                "test_run": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "time": 5.5,
                    "errors": 1,
                    "branch": "main",
                    "project": "my-application",
                    "failures": 2,
                    "skipped": 0,
                    "success_rate": 70.0,
                    "commit_sha": "abc123def456",
                    "total_tests": 10,
                    "created_at": "2025-10-25T00:00:00.000000Z",
                },
            },
            status=201,
        )

        # Call publish_report
        response = client.publish_report(signed_xml)

        # Verify response
        assert isinstance(response, PublishResponse)
        assert response.message == "Test report submitted successfully"
        assert response.status == "success"
        assert response.test_run.id == "550e8400-e29b-41d4-a716-446655440000"
        assert response.test_run.total_tests == 10
        assert response.test_run.failures == 2
        assert response.test_run.errors == 1
        assert response.test_run.skipped == 0
        assert response.test_run.success_rate == 70.0
        assert response.test_run.project == "my-application"
        assert response.test_run.branch == "main"

        # Verify request
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "http://localhost:4000/api/v1/junit/submit"
        assert responses.calls[0].request.headers["Content-Type"] == "application/xml"
        assert responses.calls[0].request.body.decode("utf-8") == signed_xml

    @responses.activate
    def test_publish_report_with_bearer_token(
        self, authenticated_client: JuxAPIClient, signed_xml: str, bearer_token: str
    ) -> None:
        """Test report publishing with Bearer token authentication."""
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "message": "Test report submitted successfully",
                "status": "success",
                "test_run": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "time": 5.5,
                    "errors": 1,
                    "branch": "main",
                    "project": "my-application",
                    "failures": 2,
                    "skipped": 0,
                    "success_rate": 70.0,
                    "commit_sha": None,
                    "total_tests": 10,
                    "created_at": "2025-10-25T00:00:00.000000Z",
                },
            },
            status=201,
        )

        response = authenticated_client.publish_report(signed_xml)

        assert response.test_run.id == "550e8400-e29b-41d4-a716-446655440000"
        # Verify Bearer token sent
        assert responses.calls[0].request.headers["Authorization"] == f"Bearer {bearer_token}"

    @responses.activate
    def test_publish_report_400_bad_request(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test 400 Bad Request (empty/invalid XML)."""
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "error": "Invalid JUnit XML",
                "details": {"message": "Request body is empty or missing required data"},
                "suggestions": ["Ensure request body contains valid JUnit XML"],
            },
            status=400,
        )

        with pytest.raises(HTTPError) as exc_info:
            client.publish_report(signed_xml)

        assert "400" in str(exc_info.value)
        assert "Invalid JUnit XML" in str(exc_info.value)

    @responses.activate
    def test_publish_report_401_unauthorized(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test 401 Unauthorized (missing/invalid Bearer token)."""
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "error": "Authentication required",
                "details": {"message": "Authorization header is required"},
                "suggestions": ["Include 'Authorization: Bearer <api_key>' header"],
            },
            status=401,
        )

        with pytest.raises(HTTPError) as exc_info:
            client.publish_report(signed_xml)

        assert "401" in str(exc_info.value)
        assert "Authentication required" in str(exc_info.value)

    @responses.activate
    def test_publish_report_422_unprocessable_entity(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test 422 Unprocessable Entity (malformed XML)."""
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "error": "Invalid JUnit XML",
                "details": {
                    "message": "XML parsing failed: unexpected end of file",
                    "line": 15,
                    "column": 5,
                },
                "suggestions": ["Ensure XML is well-formed with proper closing tags"],
            },
            status=422,
        )

        with pytest.raises(HTTPError) as exc_info:
            client.publish_report(signed_xml)

        assert "422" in str(exc_info.value)
        assert "Invalid JUnit XML" in str(exc_info.value)

    @responses.activate
    def test_publish_report_500_internal_server_error(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test 500 Internal Server Error (retryable)."""
        # First two attempts fail, third succeeds (retry logic)
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={"error": "Internal server error"},
            status=500,
        )
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={"error": "Internal server error"},
            status=500,
        )
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "message": "Test report submitted successfully",
                "status": "success",
                "test_run": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "completed",
                    "time": None,
                    "errors": 0,
                    "branch": "main",
                    "project": "my-application",
                    "failures": 0,
                    "skipped": 0,
                    "success_rate": 100.0,
                    "commit_sha": None,
                    "total_tests": 10,
                    "created_at": "2025-10-25T00:00:00.000000Z",
                },
            },
            status=201,
        )

        # Should succeed after retries
        response = client.publish_report(signed_xml)
        assert response.test_run.id == "550e8400-e29b-41d4-a716-446655440000"
        # Verify retry happened (3 requests total)
        assert len(responses.calls) == 3

    @responses.activate
    def test_publish_report_timeout(self, signed_xml: str) -> None:
        """Test request timeout handling."""
        client = JuxAPIClient(api_url="http://localhost:4000/api/v1", timeout=1)

        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            body=Timeout("Request timeout after 1s"),
        )

        with pytest.raises(RequestException) as exc_info:
            client.publish_report(signed_xml)

        assert "timeout" in str(exc_info.value).lower()

    @responses.activate
    def test_publish_report_network_error(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test network error handling."""
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            body=RequestException("Connection refused"),
        )

        with pytest.raises(RequestException) as exc_info:
            client.publish_report(signed_xml)

        assert "Connection refused" in str(exc_info.value)

    @responses.activate
    def test_publish_report_429_rate_limit(
        self, client: JuxAPIClient, signed_xml: str
    ) -> None:
        """Test 429 Too Many Requests (rate limit exceeded)."""
        responses.post(
            "http://localhost:4000/api/v1/junit/submit",
            json={
                "error": "Rate limit exceeded",
                "details": {
                    "message": "Maximum of 100 submissions per minute exceeded",
                    "retry_after": 60,
                },
                "suggestions": ["Wait 60 seconds before retrying"],
            },
            status=429,
            headers={
                "Retry-After": "60",
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "1678901234",
            },
        )

        with pytest.raises(HTTPError) as exc_info:
            client.publish_report(signed_xml)

        assert "429" in str(exc_info.value)
        assert "Rate limit exceeded" in str(exc_info.value)

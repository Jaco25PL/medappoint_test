"""Thin API client used for test setup, teardown and backend assertions.

UI tests should create/verify data through the API instead of the UI whenever
possible: it is faster, less flaky and keeps each test focused on one flow.
"""

from playwright.sync_api import APIRequestContext, APIResponse, Playwright


class ApiClient:
    LOGIN_PATH = "/api/auth/login"

    def __init__(self, playwright: Playwright, base_url: str) -> None:
        self._playwright = playwright
        self._base_url = base_url
        self._context: APIRequestContext = playwright.request.new_context(base_url=base_url)
        self._token: str | None = None

    @property
    def token(self) -> str:
        if self._token is None:
            raise RuntimeError("ApiClient is not authenticated. Call login() first.")
        return self._token

    def login(self, email: str, password: str) -> str:
        response = self._context.post(self.LOGIN_PATH, data={"email": email, "password": password})
        assert response.ok, f"Login failed: {response.status} {response.text()}"
        self._token = response.json()["token"]

        # Re-create the context so every following request carries the token.
        self._context.dispose()
        self._context = self._playwright.request.new_context(
            base_url=self._base_url,
            extra_http_headers={"Authorization": f"Bearer {self._token}"},
        )
        return self._token

    # Generic helpers; endpoint-specific methods (appointments, slots, ...) are
    # added once the API contract is mapped from Swagger.
    def get(self, path: str, **kwargs) -> APIResponse:
        return self._context.get(path, **kwargs)

    def post(self, path: str, **kwargs) -> APIResponse:
        return self._context.post(path, **kwargs)

    def put(self, path: str, **kwargs) -> APIResponse:
        return self._context.put(path, **kwargs)

    def patch(self, path: str, **kwargs) -> APIResponse:
        return self._context.patch(path, **kwargs)

    def dispose(self) -> None:
        self._context.dispose()

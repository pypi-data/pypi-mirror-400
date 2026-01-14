from __future__ import annotations

from screenshot._shared.errors import ErrorCategory


def test_error_category_classification() -> None:
    assert ErrorCategory.from_error_type("timeout") is ErrorCategory.TIMEOUT
    assert ErrorCategory.from_error_type("NavigationFailure") is ErrorCategory.NAVIGATION
    assert ErrorCategory.from_error_type("browser.crash") is ErrorCategory.BROWSER
    assert ErrorCategory.from_error_type("storage.write") is ErrorCategory.STORAGE
    assert ErrorCategory.from_error_type("") is ErrorCategory.UNKNOWN
    assert ErrorCategory.from_error_type(None) is ErrorCategory.UNKNOWN

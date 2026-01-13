# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["BrandAIProductsParams"]


class BrandAIProductsParams(TypedDict, total=False):
    domain: Required[str]
    """The domain name to analyze"""

    max_products: Annotated[int, PropertyInfo(alias="maxProducts")]
    """Maximum number of products to extract."""

    timeout_ms: Annotated[int, PropertyInfo(alias="timeoutMS")]
    """Optional timeout in milliseconds for the request.

    If the request takes longer than this value, it will be aborted with a 408
    status code. Maximum allowed value is 300000ms (5 minutes).
    """

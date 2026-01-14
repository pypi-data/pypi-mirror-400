from typing import Any, Callable, List, Literal, Optional, Tuple

from uplink import Body, Query, delete, get, json, post, put, response_handler, returns

from bpkio_api.caching import cache_api_results
from bpkio_api.consumer import BpkioSdkConsumer
from bpkio_api.exceptions import (
    ResourceExistsError,
)
from bpkio_api.helpers.list import get_all_with_pagination
from bpkio_api.helpers.search import SearchMethod, search_array_with_filters
from bpkio_api.helpers.upsert import UpsertOperationType, upsert_status
from bpkio_api.models.Categories import Category, CategoryIn
from bpkio_api.response_handler import extract_count, postprocess_response


@response_handler(postprocess_response)
class CategoriesApi(BpkioSdkConsumer):
    """API client for managing categories in the broadpeak.io platform.

    This class provides methods to create, retrieve, update, and delete categories,
    as well as list and search through existing categories.
    """

    def __init__(self, base_url: str = "", **kwargs) -> None:
        """Initialize the Categories API client.

        Args:
            base_url: Base URL for the API endpoints.
            **kwargs: Additional configuration options passed to the consumer.
        """
        super().__init__(base_url, **kwargs)

    @response_handler(extract_count)
    @get("categories")
    def count(self) -> int:
        """Get a count of all categories"""

    @returns.json(List[Category])
    @get("categories")
    def _get_page(self, offset: Query = 0, limit: Query = 5) -> List[Category]:  # type: ignore
        """Get a paginated list of categories.

        This method corresponds to the [`GET /categories`](https://developers.broadpeak.io/reference/categorycontroller_findall_v1) endpoint of the broadpeak.io API.

        Args:
            offset (int): Number of items to skip before starting to collect results.
            limit (int): Maximum number of items to return in a single page.

        Returns:
            A list of Category objects for the requested page.
        """

    @returns.json(Category)
    @get("categories/{category_id}")
    def retrieve(self, category_id: int) -> Optional[Category]:
        """Get a single category by its ID.

        This method corresponds to the [`GET /categories/{category_id}`](https://developers.broadpeak.io/reference/categorycontroller_getbyid_v1) endpoint of the broadpeak.io API.

        Args:
            category_id: Unique identifier of the category to retrieve.

        Returns:
            Optional[[Category][bpkio_api.models.Categories.Category]]: The requested Category object if found, None otherwise.

        Raises:
            ResourceNotFoundError: If the category does not exist.
        """

    @json
    @returns.json(Category)
    @post("categories")
    def create(self, category: Body(type=CategoryIn)) -> Category:  # type: ignore
        """Create a new category.

        Args:
            category ([CategoryIn][bpkio_api.models.Categories.CategoryIn]): Category data for creating a new category. Must include required
                fields like name and can include optional fields like description.

        Returns:
            [Category][bpkio_api.models.Categories.Category]: The newly created Category object.

        Raises:
            ResourceExistsError: If a category with the same name already exists.
            ValidationError: If the category data is invalid.
        """

    @json
    @returns.json(Category)
    @put("categories/{category_id}")
    def update(self, category_id: int, category: Body(type=CategoryIn)) -> Category:  # type: ignore
        """Update an existing category.

        Args:
            category_id: Unique identifier of the category to update.
            category ([CategoryIn][bpkio_api.models.Categories.CategoryIn]): Updated category data. All fields will be replaced with
                the provided values.

        Returns:
            [Category][bpkio_api.models.Categories.Category]: The updated Category object.

        Raises:
            ResourceNotFoundError: If the category does not exist.
            ValidationError: If the category data is invalid.
        """

    @delete("categories/{category_id}")
    def delete(self, category_id: int) -> None:
        """Delete a category by its ID.

        Args:
            category_id: Unique identifier of the category to delete.

        Returns:
            None

        Raises:
            ResourceNotFoundError: If the category does not exist.
        """

    # === Higher-order functions ===

    @cache_api_results("list_categories")
    def list(self, progress_hook: Callable[[int, Any, str | None], None] | None = None, **kwargs) -> List[Category]:
        """Get the complete list of categories.

        Results are automatically paginated and cached for better performance.
        The cache is invalidated when categories are modified.

        Returns:
            List[[Category][bpkio_api.models.Categories.Category]]: Complete list of all Category objects.
        """
        return get_all_with_pagination(self._get_page, count_fn=self.count, progress_hook=progress_hook)

    def search(
        self,
        value: Optional[Any] = None,
        field: Optional[str] = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: Optional[
            List[Tuple[Any, Optional[str], Optional[SearchMethod]]]
        ] = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[Category]:
        """Search for categories matching specific criteria.

        This method allows flexible searching through categories using various matching methods.
        You can search for full or partial matches in all or specific fields.

        Args:
            value: The value to search for. Can be used alone or combined with `field`.
            field: The specific field to search in. If None, searches across all fields.
            method: The search method to use:
                - STRING_SUB: Partial string match (case-insensitive)
                - STRING_MATCH: Exact string match (case-sensitive)
                - STRICT: Exact match including type
            filters: Alternative to using individual parameters. A list of tuples, where each
                tuple contains (value, field, method). Multiple filters are combined with AND logic.
                Use this when you need multiple search criteria.

        Returns:
            List[[Category][bpkio_api.models.Categories.Category]]: List of Category objects matching the search criteria.

        Examples:
            >>> # Search by name
            >>> api.search("News", field="name")
            >>> # Search with multiple criteria
            >>> api.search(filters=[
            ...     ("News", "name", SearchMethod.STRING_SUB),
            ...     ("active", "status", SearchMethod.STRICT)
            ... ])
        """
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook)
        return search_array_with_filters(sources, filters=filters)

    def upsert(
        self,
        category: CategoryIn,
        if_exists: Optional[Literal["error", "retrieve", "update"]] = None,
    ) -> Category:
        """Create, retrieve, or update a category based on existence.

        This method provides flexible handling of category creation with different
        behaviors when the category already exists.

        Args:
            category: The category data to create or update.
            if_exists: Controls behavior when a category with the same name exists:

                - `error`: Raise an error (default)
                - `retrieve`: Return the existing category
                - `update`: Update the existing category with new data

        Returns:
            The Category object (created, retrieved, or updated)

        Raises:
            ResourceExistsError: If the category exists and if_exists="error".
            ValidationError: If the category data is invalid.

        Examples:
            ```python
            from bpkio_api.helpers.upsert import UpsertOperationType, upsert_status
            
            # Create or update
            category = CategoryIn(name="News", description="News content")
            result = api.upsert(category, if_exists="update")            
            
            # Optional: Check the status of the operation
            status = upsert_status.get()
            if status == UpsertOperationType.CREATED:
                print("Created new category")
            elif status == UpsertOperationType.UPDATED:
                print("Updated existing category")
            ```
        """

        try:
            created_category = self.create(category)
            upsert_status.set(UpsertOperationType.CREATED)
            return created_category
        except ResourceExistsError:
            if if_exists == "error":
                upsert_status.set(UpsertOperationType.ERROR)
                return category

            existing_category = self.search(value=category.name, field="name")[0]

            if if_exists == "retrieve":
                upsert_status.set(UpsertOperationType.RETRIEVED)
                return existing_category
            elif if_exists == "update":
                updated_category = self.update(existing_category.id, category)
                upsert_status.set(UpsertOperationType.UPDATED)
                return updated_category

        raise ValueError(f"Invalid value for if_exists: {if_exists}")

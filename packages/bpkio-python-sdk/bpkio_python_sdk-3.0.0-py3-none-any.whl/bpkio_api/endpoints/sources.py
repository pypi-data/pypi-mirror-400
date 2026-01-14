from typing import Any, Callable, List, Tuple
from urllib.parse import urlparse, urlunparse

from uplink import Body, Query, delete, get, json, post, put, response_handler, returns

from bpkio_api.caching import cache_api_results
from bpkio_api.consumer import BpkioSdkConsumer
from bpkio_api.exceptions import BroadpeakIoHelperError, ResourceExistsError
from bpkio_api.helpers.list import (
    collect_from_ids,
    collect_from_sparse_resources,
    get_all_with_pagination,
)
from bpkio_api.helpers.objects import find_duplicates_of
from bpkio_api.helpers.search import SearchMethod, search_array_with_filters
from bpkio_api.helpers.upsert import UpsertOperationType, upsert_status
from bpkio_api.models import Sources as S
from bpkio_api.response_handler import extract_count, postprocess_response


@response_handler(postprocess_response)
class SourcesApi(BpkioSdkConsumer):
    def __init__(self, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)

        self.asset = AssetSourcesApi(parent_api=self, base_url=base_url, **kwargs)
        self.live = LiveSourcesApi(parent_api=self, base_url=base_url, **kwargs)
        self.asset_catalog = AssetCatalogSourcesApi(
            parent_api=self, base_url=base_url, **kwargs
        )
        self.ad_server = AdServerSourcesApi(
            parent_api=self, base_url=base_url, **kwargs
        )
        self.slate = SlateSourcesApi(parent_api=self, base_url=base_url, **kwargs)
        self.origin = OriginSourcesApi(parent_api=self, base_url=base_url, **kwargs)

    def _mappings(self, model):
        match model:
            case S.AssetSourceIn():
                return self.asset
            case S.LiveSourceIn():
                return self.live
            case S.AdServerSourceIn():
                return self.ad_server
            case S.AssetCatalogSourceIn():
                return self.asset_catalog
            case S.SlateSourceIn():
                return self.slate
            case _:
                raise Exception(
                    f"Model {model.__class__.__name__} not recognised as a valid source type"
                )

    @returns.json()
    @get("sources")
    def _get_page(self, offset: Query = 0, limit: Query = 5) -> List[S.SourceSparse]:  # type: ignore
        """Get a partial list of Sources"""

    @response_handler(extract_count)
    @get("sources")
    def count(self) -> int:
        """Get a count of all sources"""

    @returns.json()
    @post("sources/{type}/check")
    def check(
        self, type: S.SourceType, body: Body(type=S.SourceStatusCheck)
    ) -> S.SourceStatusCheckResult:
        """Check a URL for compliance as a Source"""

    # === Helpers ===

    @cache_api_results("list_sources", key_suffix_from_arg="sparse")
    def list(
        self,
        sparse: bool = True,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ):
        """List all sources

        Args:
            sparse (bool, optional): Whether to return sparse sources, or resolve them into fully qualified resources. Defaults to True. Note that resolving sources will incur a performance penalty.

        Returns:
            List[S.SourceSparse | S.AssetSource | S.LiveSource | S.AdServerSource | S.AssetCatalogSource | S.SlateSource | S.OriginSource]: List of sources
        """
        sparse_sources = get_all_with_pagination(
            self._get_page, count_fn=self.count, progress_hook=progress_hook
        )
        if sparse:
            return sparse_sources
        else:
            return collect_from_sparse_resources(
                sparse_resources=sparse_sources,
                get_fn=self._get_by_type,
                progress_hook=progress_hook,
            )

    def _get_by_type(
        self,
        source_id: int,
        source_type: S.SourceType,
    ) -> S.SourceSparse:
        match source_type:
            case S.SourceType.ASSET:
                return self.asset.retrieve(source_id)
            case S.SourceType.ASSET_CATALOG:
                return self.asset_catalog.retrieve(source_id)
            case S.SourceType.LIVE:
                return self.live.retrieve(source_id)
            case S.SourceType.SLATE:
                return self.slate.retrieve(source_id)
            case S.SourceType.AD_SERVER:
                return self.ad_server.retrieve(source_id)
            case S.SourceType.ORIGIN:
                return self.origin.retrieve(source_id)
            case _:
                raise BroadpeakIoHelperError(
                    message=f"Source type not supported: {source_type}",
                    original_message="",
                )

    def search_by_type(self, type: S.SourceType) -> List[S.SourceSparse]:
        all_items = self.list()
        return [i for i in all_items if i.type == type]

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        sparse: bool = True,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.SourceSparse]:
        """Searches the list of sources for those matching a particular filter query

        You can search for full or partial matches in all or specific fields.
        All searches are done as string matches (regarding of the actual type of each field)

        Args:
            value (Any, optional): The string value to search. Defaults to None.
            field (str, optional): The field name in which to search for the value.
                Defaults to None.
            method (SearchMethod, optional): How to perform the search.
                SearchMethod.STRING_SUB searches for partial string match. This is the default.
                SearchMethod.STRING_MATCH searches for a complete match (after casting to string).
                SearchMethod.STRICT searches for a strict match (including type)
            filters (List[Tuple[Any, Optional[str], Optional[SearchMethod]]], optional):
                Can be used as an alternatitve to using `value`, `field` and `method`,
                in particular if multiple search patterns need to be specified
                (which are then treated as logical `AND`). Defaults to None.

        Returns:
            List[Svc.SourceSpare]: List of matching sources
        """
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(sparse=sparse, progress_hook=progress_hook)
        return search_array_with_filters(sources, filters=filters)

    def retrieve(
        self, source_id: int
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
        | None
    ):
        """Gets a source by its ID

        This is a helper method that allows you to get the full Source sub-type (eg. asset, asset-catalog)
        without having to know its type in advance and calling the specific endpoint

        Args:
            source_id (int): The source identifier

        Raises:
            e: _description_

        Returns:
            AssetSource | AssetCatalogSource | LiveSource | AdServerSource | SlateSource : A specific sub-type of source
        """

        candidates = self.search(int(source_id), field="id", method=SearchMethod.STRICT)
        try:
            source = candidates[0]
            return self._get_by_type(source_id, source.type)
        except IndexError as e:
            raise BroadpeakIoHelperError(
                message=f"There is no source with ID {source_id}",
                original_message=e.args[0],
            )

    def create(
        self, source: S.SourceIn
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
    ):
        """Create a source"""
        endpoint = self._mappings(source)
        return endpoint.create(source)

    def delete(self, source_id: int):
        """Delete a source"""
        source = self.retrieve(source_id)
        if not source:
            raise BroadpeakIoHelperError(
                message=f"There is no source with ID {source_id}",
            )
        endpoint = self._mappings(source)
        return endpoint.delete(source_id)

    def _update(
        self, source_id: int, source: S.SourceIn
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
    ):
        """Update a source"""
        endpoint = self._mappings(source)
        return endpoint.update(source_id, source)

    def upsert(
        self,
        source: S.SourceIn,
        if_exists: str = "retrieve",
        unique_fields: List[str | Tuple] = [],
    ) -> (
        S.AssetSource
        | S.AdServerSource
        | S.AssetCatalogSource
        | S.SlateSource
        | S.LiveSource
        | S.SourceIn
    ):
        """Create, retrieve, or update a source based on existence.

        This method provides flexible handling of source creation with different
        behaviors when the source already exists.

        Args:
            source: The source data to create or update.
            if_exists: Controls behavior when a source with the same name exists:

                - `error`: Raise an error (default)
                - `retrieve`: Return the existing source
                - `update`: Update the existing source with new data

        Returns:
            The Source object (created, retrieved, or updated)

        Raises:
            ResourceExistsError: If the source exists and if_exists="error".
            ValidationError: If the source data is invalid.

        Examples:
            ```python
            from bpkio_api.helpers.upsert import UpsertOperationType, upsert_status

            # Create or update
            source = LiveSourceIn(name="News", description="News content")
            result = api.upsert(source, if_exists="update")

            # Optional: Check the status of the operation
            status = upsert_status.get()
            if status == UpsertOperationType.CREATED:
                print("Created new source")
            elif status == UpsertOperationType.UPDATED:
                print("Updated existing source")
            ```
        """

        try:
            created_source = self.create(source)
            upsert_status.set(UpsertOperationType.CREATED)
            return created_source
        except ResourceExistsError as e:
            if if_exists == "error":
                upsert_status.set(UpsertOperationType.ERROR)
                return source

            unique_fields = list(set(unique_fields + ["name"]))
            for fld in unique_fields:
                # single field
                if isinstance(fld, str):
                    fld = (fld,)

                # find duplicates
                dupes = find_duplicates_of(
                    obj=source, in_list=self.list(), by_fields=fld
                )
                if dupes:
                    existing_resource = self.retrieve(dupes[0][1].id)

                    if if_exists == "retrieve":
                        upsert_status.set(UpsertOperationType.RETRIEVED)
                        return existing_resource
                    elif if_exists == "update":
                        updated_resource = self._update(existing_resource.id, source)
                        upsert_status.set(UpsertOperationType.UPDATED)
                        return updated_resource

    def check_by_id(self, source_id: int) -> List[S.SourceStatusCheckResult]:
        source = self.retrieve(source_id=source_id)

        if source:
            url = source.url

            # Ad proxy cannot be checked
            if not url.startswith("http"):
                raise ValueError("This type of source cannot be checked")

            if source.type == S.SourceType.ASSET_CATALOG:
                url = url + source.assetSample

            payload = S.SourceStatusCheck(url=url)
            if (
                hasattr(source, "origin")
                and source.origin
                and len(source.origin.customHeaders)
            ):
                payload.origin = source.origin

            return self.check(
                type=source.type,
                body=payload,
            )


# === ASSET SOURCES ===


@response_handler(postprocess_response)
class AssetSourcesApi(BpkioSdkConsumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.AssetSource)
    @get("sources/asset/{source_id}")
    def retrieve(self, source_id):
        """Get a single asset source, by ID"""

    @json
    @returns.json(S.AssetSource)
    @post("sources/asset")
    def create(self, source: Body(type=S.AssetSourceIn)) -> S.AssetSource:  # type: ignore
        """Create a new asset source"""

    @json
    @returns.json(S.AssetSource)
    @put("sources/asset/{source_id}")
    def update(
        self, source_id: int, source: Body(type=S.AssetSourceIn)
    ) -> S.AssetSource:  # type: ignore
        """Update an asset source"""

    @delete("sources/asset/{source_id}")
    def delete(self, source_id: int):
        """Delete an asset source, by ID"""

    def upsert(
        self, source: S.AssetSourceIn, if_exists: str = "retrieve"
    ) -> Tuple[S.AssetSource, UpsertOperationType]:
        """Conditionally create, retrieve or update an Asset source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_assets")
    def list(
        self,
        sparse: bool = False,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.AssetSource]:
        """List all Asset sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.ASSET,
            field="type",
            method=SearchMethod.STRICT,
            progress_hook=progress_hook,
            sparse=sparse,
        )
        if sparse:
            return sparse_sources
        return collect_from_ids(
            ids=[src.id for src in sparse_sources],
            get_fn=self.retrieve,
            progress_hook=progress_hook,
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.AssetSource]:
        """Search the list of Asset sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook, sparse=False)
        return search_array_with_filters(sources, filters=filters)


# === LIVE SOURCES ===


@response_handler(postprocess_response)
class LiveSourcesApi(BpkioSdkConsumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.LiveSource)
    @get("sources/live/{source_id}")
    def retrieve(self, source_id):
        """Get a single live source, by ID"""

    @json
    @returns.json(S.LiveSource)
    @post("sources/live")
    def create(self, source: Body(type=S.LiveSourceIn)) -> S.LiveSource:  # type: ignore
        """Create a new live source"""

    @json
    @returns.json(S.LiveSource)
    @put("sources/live/{source_id}")
    def update(self, source_id: int, source: Body(type=S.LiveSourceIn)) -> S.LiveSource:  # type: ignore
        """Update a live source"""

    @delete("sources/live/{source_id}")
    def delete(self, source_id: int):
        """Delete a live source, by ID"""

    def upsert(
        self, source: S.LiveSourceIn, if_exists: str | None = None
    ) -> Tuple[S.LiveSource, UpsertOperationType]:
        """Conditionally create, retrieve or update a Live source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_live")
    def list(
        self,
        sparse: bool = False,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.LiveSource]:
        """List all Live sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.LIVE,
            field="type",
            method=SearchMethod.STRICT,
            progress_hook=progress_hook,
            sparse=True,
        )
        if sparse:
            return sparse_sources
        return collect_from_ids(
            ids=[src.id for src in sparse_sources],
            get_fn=self.retrieve,
            progress_hook=progress_hook,
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.LiveSource]:
        """Search the list of Live sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook, sparse=False)
        return search_array_with_filters(sources, filters=filters)


# === ASSET CATALOG SOURCES ===


@response_handler(postprocess_response)
class AssetCatalogSourcesApi(BpkioSdkConsumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.AssetCatalogSource)
    @get("sources/asset-catalog/{source_id}")
    def retrieve(self, source_id):
        """Get a single asset catalog source, by ID"""

    @json
    @returns.json(S.AssetCatalogSource)
    @post("sources/asset-catalog")
    def create(self, source: Body(type=S.AssetCatalogSourceIn)) -> S.AssetCatalogSource:  # type: ignore
        """Create a new asset catalog source"""

    @json
    @returns.json(S.AssetCatalogSource)
    @put("sources/asset-catalog/{source_id}")
    def update(
        self, source_id: int, source: Body(type=S.AssetCatalogSourceIn)
    ) -> S.AssetCatalogSource:  # type: ignore
        """Updates an asset source"""

    @delete("sources/asset-catalog/{source_id}")
    def delete(self, source_id: int):
        """Delete an asset catalog source, by ID"""

    def upsert(
        self, source: S.AssetCatalogSourceIn, if_exists: str | None = None
    ) -> Tuple[S.AssetCatalogSource, UpsertOperationType]:
        """Conditionally create, retrieve or update an Asset Catalog source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_assetcatalogs")
    def list(
        self,
        sparse: bool = False,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.AssetCatalogSource]:
        """List all Asset Catalog sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.ASSET_CATALOG,
            field="type",
            method=SearchMethod.STRICT,
            progress_hook=progress_hook,
            sparse=sparse,
        )
        if sparse:
            return sparse_sources
        return collect_from_ids(
            ids=[src.id for src in sparse_sources],
            get_fn=self.retrieve,
            progress_hook=progress_hook,
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.AssetCatalogSource]:
        """Search the list of Asset Catalog sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook, sparse=False)
        return search_array_with_filters(sources, filters=filters)


# === AD SERVER SOURCES ===


@response_handler(postprocess_response)
class AdServerSourcesApi(BpkioSdkConsumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.AdServerSource)
    @get("sources/ad-server/{source_id}")
    def retrieve(self, source_id):
        """Get a single ad server source, by ID"""

    @json
    @returns.json(S.AdServerSource)
    @post("sources/ad-server")
    def create(self, source: Body(type=S.AdServerSourceIn)) -> S.AdServerSource:  # type: ignore
        """Create a new ad server source"""

    @json
    @returns.json(S.AdServerSource)
    @put("sources/ad-server/{source_id}")
    def update(
        self, source_id: int, source: Body(type=S.AdServerSourceIn)
    ) -> S.AdServerSource:  # type: ignore
        """Update an Ad Server source"""

    @delete("sources/ad-server/{source_id}")
    def delete(self, source_id: int):
        """Delete an ad server source, by ID"""

    def upsert(
        self, source: S.AdServerSourceIn, if_exists: str | None = None
    ) -> Tuple[S.AdServerSource, UpsertOperationType]:
        """Conditionally create, retrieve or update an Ad Server source"""
        return self.parent_api.upsert(source, unique_fields=[], if_exists=if_exists)

    def create_from_url(self, name: str, url: str) -> S.AdServerSource:
        """Convenience function to create an ad-server from a full URL

        Args:
            name (str): Name of the Ad Server source
            url (str): The full URL, including query parameters

        Returns:
            AdServerSource: the created Ad Server source
        """

        def split_url(url: str):
            parsed_url = urlparse(url)

            # Reconstruct the URL without the query part
            first_part = urlunparse(parsed_url._replace(query=""))

            # Get the query part
            second_part = parsed_url.query

            return first_part, second_part

        parts = split_url(url)
        queries = parts[1] or ""
        individual_queries = queries.split("&") if queries else []

        query_params = [
            S.AdServerQueryParameter(
                type=S.AdServerQueryParameterType.custom, name=qp_name, value=qp_value
            )
            for qp_name, qp_value in (
                indiv_qp.split("=") for indiv_qp in individual_queries
            )
        ]

        ad_server_source = S.AdServerSourceIn(
            name=name, url=parts[0], queryParameters=query_params, description=None
        )
        return self.create(ad_server_source)

    @cache_api_results("list_adservers")
    def list(
        self,
        sparse: bool = False,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.AdServerSource]:
        """List all Ad Server sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.AD_SERVER,
            field="type",
            method=SearchMethod.STRICT,
            progress_hook=progress_hook,
            sparse=sparse,
        )
        if sparse:
            return sparse_sources
        return collect_from_ids(
            ids=[src.id for src in sparse_sources],
            get_fn=self.retrieve,
            progress_hook=progress_hook,
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.AdServerSource]:
        """Searches the list of Ad Server sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook, sparse=False)
        return search_array_with_filters(sources, filters=filters)


# === SLATE SOURCES ===


@response_handler(postprocess_response)
class SlateSourcesApi(BpkioSdkConsumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.SlateSource)
    @get("sources/slate/{source_id}")
    def retrieve(self, source_id):
        """Get a single slate source, by ID"""

    @json
    @returns.json(S.SlateSource)
    @post("sources/slate")
    def create(self, source: Body(type=S.SlateSourceIn)) -> S.SlateSource:  # type: ignore
        """Create a new slate source"""

    @json
    @returns.json(S.SlateSource)
    @put("sources/slate/{source_id}")
    def update(
        self, source_id: int, source: Body(type=S.SlateSourceIn)
    ) -> S.SlateSource:  # type: ignore
        """Update a slate source"""

    @delete("sources/slate/{source_id}")
    def delete(self, source_id: int):
        """Delete a slate source, by ID"""

    def upsert(
        self, source: S.SlateSourceIn, if_exists: str | None = None
    ) -> Tuple[S.SlateSource, UpsertOperationType]:
        """Conditionally create, retrieve or update a slate source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_slates")
    def list(
        self,
        sparse: bool = False,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.SlateSource]:
        """List all Slate sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.SLATE,
            field="type",
            method=SearchMethod.STRICT,
            progress_hook=progress_hook,
            sparse=sparse,
        )
        if sparse:
            return sparse_sources
        return collect_from_ids(
            ids=[src.id for src in sparse_sources],
            get_fn=self.retrieve,
            progress_hook=progress_hook,
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.SlateSource]:
        """Searches the list of Slate sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook, sparse=False)
        return search_array_with_filters(sources, filters=filters)


# === ORIGIN SOURCES ===


@response_handler(postprocess_response)
class OriginSourcesApi(BpkioSdkConsumer):
    def __init__(self, parent_api: SourcesApi, base_url="", **kwargs):
        super().__init__(base_url, **kwargs)
        self.parent_api = parent_api

    @returns.json(S.OriginSource)
    @get("sources/origin/{source_id}")
    def retrieve(self, source_id):
        """Get a single origin source, by ID"""

    @json
    @returns.json(S.OriginSource)
    @post("sources/origin")
    def create(self, source: Body(type=S.OriginSourceIn)) -> S.OriginSource:  # type: ignore
        """Create a new origin source"""

    @json
    @returns.json(S.OriginSource)
    @put("sources/origin/{source_id}")
    def update(
        self, source_id: int, source: Body(type=S.OriginSourceIn)
    ) -> S.OriginSource:  # type: ignore
        """Update an origin source"""

    @delete("sources/origin/{source_id}")
    def delete(self, source_id: int):
        """Delete a origin source, by ID"""

    def upsert(
        self, source: S.OriginSourceIn, if_exists: str | None = None
    ) -> Tuple[S.OriginSource, UpsertOperationType]:
        """Conditionally create, retrieve or update an origin source"""
        return self.parent_api.upsert(
            source, unique_fields=["url"], if_exists=if_exists
        )

    @cache_api_results("list_origins")
    def list(
        self,
        sparse: bool = False,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.OriginSource]:
        """List all Origin sources"""
        sparse_sources = self.parent_api.search(
            S.SourceType.ORIGIN,
            field="type",
            method=SearchMethod.STRICT,
            progress_hook=progress_hook,
            sparse=sparse,
        )
        if sparse:
            return sparse_sources
        return collect_from_ids(
            ids=[src.id for src in sparse_sources],
            get_fn=self.retrieve,
            progress_hook=progress_hook,
        )

    def search(
        self,
        value: Any | None = None,
        field: str | None = None,
        method: SearchMethod = SearchMethod.STRING_SUB,
        filters: List[Tuple[Any, str | None, SearchMethod | None]] | None = None,
        progress_hook: Callable[[int, Any, str | None], None] | None = None,
    ) -> List[S.OriginSource]:
        """Searches the list of Origin sources for those matching a particular filter query"""
        if not filters:
            filters = [(value, field, method)]

        sources = self.list(progress_hook=progress_hook, sparse=False)
        return search_array_with_filters(sources, filters=filters)

import math
import re
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sanic import response
from sanic.views import HTTPMethodView

from bakit.utils.db import fetch_all_sql, fetch_one_sql
from bakit.utils.metrics import view_metrics_context


def serialize(obj):
    """Recursively serialize objects for JSON serialization.
    Currently handles datetime, date and Decimal objects.
    """
    if isinstance(obj, datetime | date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        # Avoid returning scientific notation for 0 values ("0E-18" -> "0")
        if obj.is_zero():
            return "0"
        return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    else:
        return obj


class BadRequestError(Exception):
    """Custom exception for bad request errors with status code 400."""

    def __init__(self, message="Bad request", status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def route(bp, path):
    """Custom decorator to register class-based views with routes."""

    if not path.startswith("/"):
        raise ValueError(f"Route path must start with '/': {path!r}")

    if path != "/" and not path.endswith("/"):
        raise ValueError(f"Route path must end with '/': {path!r}")

    def decorator(cls):
        bp.add_route(cls.as_view(), path)
        return cls

    return decorator


class Response:
    """Structured response class for API endpoints."""

    def __init__(self, data, status=200, message=None):
        self.data = data
        self.status = status
        self.message = message

    def to_dict(self):
        # Serialize datetime objects in data only
        serialized_data = serialize(self.data)

        result = {
            "data": serialized_data,
            "status": self.status,
            "success": 200 <= self.status < 300,
        }

        if self.message:
            result["message"] = self.message

        return result


class DaysAgoMixin:
    days_ago = None
    days_ago_default = 30
    days_ago_required = False
    days_ago_options = [1, 7, 30, 90, 365, 9999]
    days_ago_dt = None
    days_ago_date = None

    def _handle_days_ago(self, request):
        days_ago = request.args.get("days_ago", self.days_ago_default)
        if days_ago == "null" or days_ago is None or days_ago == "None":
            days_ago = self.days_ago_default
        if days_ago:
            try:
                self.days_ago = int(days_ago)
                self.days_ago_dt = datetime.now(UTC) - timedelta(days=self.days_ago)
                self.days_ago_date = datetime.now(UTC).date() - timedelta(
                    days=self.days_ago
                )
            except (TypeError, ValueError):
                raise ValueError("Wrong value for days_ago") from None

            if self.days_ago_options and self.days_ago not in self.days_ago_options:
                raise ValueError("Wrong value for days_ago") from None
        elif self.days_ago_required:
            raise ValueError("days_ago is a required param") from None


class APIView(DaysAgoMixin, HTTPMethodView):
    async def dispatch_request(self, request, *args, **kwargs):
        self._handle_days_ago(request)
        handler = getattr(self, request.method.lower(), None)

        if not handler:
            return response.json(
                {"message": "Method not allowed", "status": 405, "success": False},
                status=405,
            )

        try:
            result = await handler(request, *args, **kwargs)
            if isinstance(result, Response):
                return response.json(result.to_dict(), status=result.status)

            if isinstance(result, tuple):
                data, status = result
                if isinstance(data, dict | list):
                    result = Response(data=data, status=status)
                    return response.json(result.to_dict(), status=result.status)
                return response.text(str(data), status=status)

            if isinstance(result, dict | list):
                raise TypeError(
                    "APIView handler must return a Response object or a (data, status) "
                    "tuple, not a raw dict or list."
                )

            return result
        except BadRequestError as e:
            return response.json(
                {"message": e.message, "status": e.status_code, "success": False},
                status=e.status_code,
            )


class PaginatedAPIView(APIView):
    allowed_filters = ()
    sortable_fields = ()
    default_sort = ""
    include_count = True

    def get_allowed_filters(self):
        return self.allowed_filters

    def get_sortable_fields(self):
        return self.sortable_fields

    def get_base_query(self):
        raise NotImplementedError

    def get_count_query(self):
        return None

    def get_filters(self, request, values=None):
        filters = []
        if values is None:
            values = {}

        for filter_item in self.get_allowed_filters():
            # Handle both simple field names and custom filter clauses
            if (
                "=" in filter_item
                or ">" in filter_item
                or "<" in filter_item
                or "!=" in filter_item
                or "LIKE" in filter_item.upper()
                or "ILIKE" in filter_item.upper()
            ):
                # Custom filter clause with %(name)s pattern
                filter_clause = filter_item
                param_match = re.search(r"%\(([^)]+)\)s", filter_clause)
                if param_match:
                    param_name = param_match.group(1)
                    if param_name in request.args:
                        filters.append(filter_clause)
                        if isinstance(request.args[param_name], list):
                            values[param_name] = request.args[param_name][0]
                        else:
                            values[param_name] = request.args[param_name]
                    if param_name in request.match_info:
                        filters.append(filter_clause)
                        values[param_name] = request.match_info[param_name]
            else:
                # Simple field name - default to equality
                field_name = filter_item
                # Extract the parameter name from the field
                # (e.g., "a.network" -> "network")
                param_name = field_name.split(".")[-1]
                if param_name in request.args:
                    filter_clause = f"{field_name} = %({param_name})s"
                    filters.append(filter_clause)
                    if isinstance(request.args[param_name], list):
                        values[param_name] = request.args[param_name][0]
                    else:
                        values[param_name] = request.args[param_name]

        return filters, values

    def get_sorting(self, request):
        sort_param = request.args.get("sort")
        if not sort_param and not self.default_sort:
            return ""

        sort_param = sort_param or self.default_sort

        allowed = self.get_sortable_fields()
        sort_parts = []

        for field in sort_param.split(","):
            direction = "ASC"
            if field.startswith("-"):
                field = field[1:]
                direction = "DESC"

            for allowed_field in allowed:
                if allowed_field.endswith(f".{field}") or allowed_field == field:
                    sort_parts.append(f"{allowed_field} {direction}")
                    break

        parts = f" ORDER BY {', '.join(sort_parts)}" if sort_parts else ""
        return f"{parts} NULLS LAST" if parts else ""

    async def paginate(self, request):
        # Validate page parameter
        page_param = request.args.get("page", "1")
        try:
            page = int(page_param)
            if page < 1:
                raise BadRequestError("Page must be a positive integer")
        except ValueError as e:
            raise BadRequestError("Page must be a valid integer") from e

        # Validate limit parameter
        limit_param = request.args.get("limit", "20")
        try:
            limit = int(limit_param)
            if limit < 1:
                raise BadRequestError("Limit must be a positive integer")
        except ValueError as e:
            raise BadRequestError("Limit must be a valid integer") from e

        if limit > 1000:
            raise BadRequestError("Limit must be <= 1000")

        offset = (page - 1) * limit

        # Check if count is requested (default to True for backward compatibility)
        include_count = self.include_count
        if include_count is True:
            include_count = request.args.get("count", "true").lower() == "true"

        base_sql, values = self.get_base_query()
        count_sql = self.get_count_query()

        filters, filter_values = self.get_filters(request)

        values.update(filter_values)

        filter_clause = f" WHERE {' AND '.join(filters)}" if filters else ""
        sort_clause = self.get_sorting(request)

        final_query = (
            f"{base_sql}{filter_clause}{sort_clause} LIMIT {limit} OFFSET {offset}"
        )

        rows = await fetch_all_sql(final_query, values)

        # Initialize pagination metadata
        pagination = {
            "page": page,
            "limit": limit,
            "total": None,
            "pages": None,
            "next": None,
            "previous": None,
        }

        # Only run count query if requested
        if include_count:
            if count_sql:
                final_count = f"{count_sql}{filter_clause}"
            else:
                # Wrap the filtered base query for counting
                final_count = (
                    f"SELECT COUNT(*) as count FROM ({base_sql}{filter_clause}) AS sub"
                )

            total_result = await fetch_one_sql(final_count, values)
            total = total_result["count"] if total_result else 0

            pagination.update(
                {
                    "total": total,
                    "pages": math.ceil(total / limit),
                }
            )

        # Add previous/next links
        base_url = request.url.split("?")[0]
        query_params = dict(request.args)

        # Convert list values to single values for URL generation
        clean_params = {}
        for k, v in query_params.items():
            if isinstance(v, list):
                clean_params[k] = v[0] if v else ""
            else:
                clean_params[k] = v

        def build_url(page_num):
            """Helper function to build pagination URLs"""
            params = clean_params.copy()
            params["page"] = page_num
            return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        # Previous page link
        if page > 1:
            pagination["previous"] = build_url(page - 1)

        # Next page link (only if we have count info or if we got a full page of
        # results)
        if include_count:
            if page < pagination.get("pages", 0):
                pagination["next"] = build_url(page + 1)
        else:
            # If no count, check if we got a full page of results to determine
            # if there's a next page
            if len(rows) == limit:
                pagination["next"] = build_url(page + 1)

        return {
            "results": rows,
            "pagination": pagination,
        }

    async def get(self, request, *args, **kwargs):
        with view_metrics_context(self.__class__.__name__):
            return await self.paginate(request), 200

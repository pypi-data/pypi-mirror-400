"""Tags API for DFlow SDK."""

from dflow.types import CategoryTags
from dflow.utils.http import HttpClient


class TagsAPI:
    """API for retrieving category tags.

    Tags provide a way to categorize and filter events by topic
    (e.g., 'crypto', 'politics', 'sports').

    Example:
        >>> dflow = DFlowClient()
        >>> tags = dflow.tags.get_tags_by_categories()
        >>> for category, tag_list in tags.items():
        ...     print(f"{category}: {', '.join(tag_list)}")
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def get_tags_by_categories(self) -> CategoryTags:
        """Get all tags organized by category.

        Returns:
            Tags grouped by their categories (dict mapping category to list of tags)

        Example:
            >>> tags = dflow.tags.get_tags_by_categories()
            >>> for category, tag_list in tags.items():
            ...     print(f"{category}: {', '.join(tag_list)}")
        """
        return self._http.get("/tags_by_categories")

"""Tests for pagination utilities."""

import pytest

from dflow.utils.pagination import collect_all, count_all, find_first, paginate


class MockResponse:
    """Mock paginated response."""

    def __init__(self, items: list, cursor: str | None = None):
        self.items = items
        self.cursor = cursor


class TestPaginate:
    """Tests for paginate function."""

    def test_single_page(self):
        """Test pagination with single page."""
        def fetch_page(params):
            return MockResponse(items=[1, 2, 3], cursor=None)
        
        results = list(paginate(
            fetch_page,
            get_items=lambda r: r.items,
        ))
        
        assert results == [1, 2, 3]

    def test_multiple_pages(self):
        """Test pagination with multiple pages."""
        pages = [
            MockResponse(items=[1, 2, 3], cursor="cursor1"),
            MockResponse(items=[4, 5, 6], cursor="cursor2"),
            MockResponse(items=[7, 8, 9], cursor=None),
        ]
        page_index = [0]
        
        def fetch_page(params):
            response = pages[page_index[0]]
            page_index[0] += 1
            return response
        
        results = list(paginate(
            fetch_page,
            get_items=lambda r: r.items,
        ))
        
        assert results == [1, 2, 3, 4, 5, 6, 7, 8, 9]

    def test_max_items(self):
        """Test pagination with max_items limit."""
        pages = [
            MockResponse(items=[1, 2, 3], cursor="cursor1"),
            MockResponse(items=[4, 5, 6], cursor="cursor2"),
        ]
        page_index = [0]
        
        def fetch_page(params):
            response = pages[page_index[0]]
            page_index[0] += 1
            return response
        
        results = list(paginate(
            fetch_page,
            get_items=lambda r: r.items,
            max_items=5,
        ))
        
        assert results == [1, 2, 3, 4, 5]

    def test_empty_response(self):
        """Test pagination with empty response."""
        def fetch_page(params):
            return MockResponse(items=[], cursor=None)
        
        results = list(paginate(
            fetch_page,
            get_items=lambda r: r.items,
        ))
        
        assert results == []


class TestCollectAll:
    """Tests for collect_all function."""

    def test_collect_all_items(self):
        """Test collecting all items."""
        pages = [
            MockResponse(items=["a", "b"], cursor="c1"),
            MockResponse(items=["c", "d"], cursor=None),
        ]
        page_index = [0]
        
        def fetch_page(params):
            response = pages[page_index[0]]
            page_index[0] += 1
            return response
        
        results = collect_all(
            fetch_page,
            get_items=lambda r: r.items,
        )
        
        assert results == ["a", "b", "c", "d"]

    def test_collect_all_with_limit(self):
        """Test collecting with max_items."""
        def fetch_page(params):
            return MockResponse(items=[1, 2, 3, 4, 5], cursor=None)
        
        results = collect_all(
            fetch_page,
            get_items=lambda r: r.items,
            max_items=3,
        )
        
        assert results == [1, 2, 3]


class TestCountAll:
    """Tests for count_all function."""

    def test_count_all_items(self):
        """Test counting all items."""
        pages = [
            MockResponse(items=[1, 2, 3], cursor="c1"),
            MockResponse(items=[4, 5], cursor=None),
        ]
        page_index = [0]
        
        def fetch_page(params):
            response = pages[page_index[0]]
            page_index[0] += 1
            return response
        
        count = count_all(
            fetch_page,
            get_items=lambda r: r.items,
        )
        
        assert count == 5


class TestFindFirst:
    """Tests for find_first function."""

    def test_find_first_match(self):
        """Test finding first matching item."""
        def fetch_page(params):
            return MockResponse(items=[1, 2, 3, 4, 5], cursor=None)
        
        result = find_first(
            fetch_page,
            get_items=lambda r: r.items,
            predicate=lambda x: x > 3,
        )
        
        assert result == 4

    def test_find_first_no_match(self):
        """Test when no item matches."""
        def fetch_page(params):
            return MockResponse(items=[1, 2, 3], cursor=None)
        
        result = find_first(
            fetch_page,
            get_items=lambda r: r.items,
            predicate=lambda x: x > 10,
        )
        
        assert result is None

    def test_find_first_across_pages(self):
        """Test finding item across multiple pages."""
        pages = [
            MockResponse(items=[1, 2], cursor="c1"),
            MockResponse(items=[3, 4], cursor="c2"),
            MockResponse(items=[5, 6], cursor=None),
        ]
        page_index = [0]
        
        def fetch_page(params):
            response = pages[page_index[0]]
            page_index[0] += 1
            return response
        
        result = find_first(
            fetch_page,
            get_items=lambda r: r.items,
            predicate=lambda x: x == 4,
        )
        
        assert result == 4

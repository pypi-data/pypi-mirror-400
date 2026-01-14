"""Tests for ID expression parsing."""

from taskng.core.id_parser import expand_id_args, parse_id_expression


class TestParseIdExpression:
    """Tests for parse_id_expression function."""

    def test_single_id(self):
        """Should parse single ID."""
        assert parse_id_expression("5") == [5]

    def test_range(self):
        """Should parse ID range."""
        assert parse_id_expression("1-5") == [1, 2, 3, 4, 5]

    def test_range_reversed(self):
        """Should handle reversed range."""
        assert parse_id_expression("5-1") == [1, 2, 3, 4, 5]

    def test_list(self):
        """Should parse comma-separated list."""
        assert parse_id_expression("1,3,5") == [1, 3, 5]

    def test_combined(self):
        """Should parse combined range and list."""
        assert parse_id_expression("1-3,7,10-12") == [1, 2, 3, 7, 10, 11, 12]

    def test_duplicates_removed(self):
        """Should remove duplicates."""
        assert parse_id_expression("1,1,2,2,3") == [1, 2, 3]

    def test_overlapping_ranges(self):
        """Should handle overlapping ranges."""
        assert parse_id_expression("1-5,3-7") == [1, 2, 3, 4, 5, 6, 7]

    def test_sorted_output(self):
        """Should return sorted list."""
        assert parse_id_expression("10,1,5") == [1, 5, 10]

    def test_empty_string(self):
        """Should return empty list for empty string."""
        assert parse_id_expression("") == []

    def test_whitespace(self):
        """Should handle whitespace."""
        assert parse_id_expression("1, 2, 3") == [1, 2, 3]

    def test_single_in_list(self):
        """Should handle single item list."""
        assert parse_id_expression("42") == [42]

    def test_large_range(self):
        """Should handle large range."""
        result = parse_id_expression("1-100")
        assert len(result) == 100
        assert result[0] == 1
        assert result[-1] == 100


class TestExpandIdArgs:
    """Tests for expand_id_args function."""

    def test_single_arg(self):
        """Should expand single argument."""
        assert expand_id_args(["5"]) == [5]

    def test_multiple_args(self):
        """Should expand multiple arguments."""
        assert expand_id_args(["1", "2", "3"]) == [1, 2, 3]

    def test_range_arg(self):
        """Should expand range argument."""
        assert expand_id_args(["1-5"]) == [1, 2, 3, 4, 5]

    def test_mixed_args(self):
        """Should expand mixed arguments."""
        assert expand_id_args(["1-3", "10"]) == [1, 2, 3, 10]

    def test_deduplicates(self):
        """Should deduplicate across arguments."""
        assert expand_id_args(["1-3", "2-4"]) == [1, 2, 3, 4]

    def test_empty_list(self):
        """Should return empty list for empty input."""
        assert expand_id_args([]) == []

    def test_invalid_ignored(self):
        """Should ignore invalid expressions."""
        assert expand_id_args(["abc", "1", "xyz"]) == [1]

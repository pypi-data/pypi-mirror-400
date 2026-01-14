"""Tests for nikkei225 data source"""

from pykabu.sources.nikkei225 import (
    ScheduleItem,
    _ScheduleTableParser,
    filter_schedule_by_importance,
)


class TestScheduleParser:
    """Tests for schedule HTML parsing"""

    def test_parse_schedule_items(self, sample_schedule_html):
        """Test parsing schedule items from HTML"""
        parser = _ScheduleTableParser()
        parser.feed(sample_schedule_html)

        assert len(parser.items) == 3

    def test_parse_schedule_first_item(self, sample_schedule_html):
        """Test first parsed item has correct data"""
        parser = _ScheduleTableParser()
        parser.feed(sample_schedule_html)

        item = parser.items[0]
        assert item.date_str == "1/8(水)"
        assert item.time == "08:50"
        assert item.importance == "★★★"
        assert item.indicator == "日銀金融政策決定会合"

    def test_parse_schedule_date_inheritance(self, sample_schedule_html):
        """Test that date is inherited from previous row"""
        parser = _ScheduleTableParser()
        parser.feed(sample_schedule_html)

        # Second item should inherit date from first
        assert parser.items[1].date_str == "1/8(水)"
        # Third item has new date
        assert parser.items[2].date_str == "1/9(木)"


class TestScheduleItem:
    """Tests for ScheduleItem dataclass"""

    def test_star_count(self):
        """Test star_count property"""
        item = ScheduleItem(
            date_str="1/8",
            time="08:50",
            importance="★★★",
            indicator="Test",
            result="-",
            forecast="-",
            previous="-",
        )
        assert item.star_count == 3

    def test_star_count_five(self):
        """Test star_count with 5 stars"""
        item = ScheduleItem(
            date_str="1/8",
            time="08:50",
            importance="★★★★★",
            indicator="Test",
            result="-",
            forecast="-",
            previous="-",
        )
        assert item.star_count == 5

    def test_star_count_empty(self):
        """Test star_count with no stars"""
        item = ScheduleItem(
            date_str="1/8",
            time="08:50",
            importance="",
            indicator="Test",
            result="-",
            forecast="-",
            previous="-",
        )
        assert item.star_count == 0


class TestFilterByImportance:
    """Tests for filter_schedule_by_importance function"""

    def test_filter_by_importance(self):
        """Test filtering items by star count"""
        items = [
            ScheduleItem("1/8", "08:00", "★", "Low", "-", "-", "-"),
            ScheduleItem("1/8", "09:00", "★★★", "Medium", "-", "-", "-"),
            ScheduleItem("1/8", "10:00", "★★★★★", "High", "-", "-", "-"),
        ]

        filtered = filter_schedule_by_importance(items, 3)
        assert len(filtered) == 2
        assert filtered[0].indicator == "Medium"
        assert filtered[1].indicator == "High"

    def test_filter_by_importance_none_match(self):
        """Test filtering when no items match"""
        items = [
            ScheduleItem("1/8", "08:00", "★", "Low", "-", "-", "-"),
            ScheduleItem("1/8", "09:00", "★★", "Low2", "-", "-", "-"),
        ]

        filtered = filter_schedule_by_importance(items, 5)
        assert len(filtered) == 0

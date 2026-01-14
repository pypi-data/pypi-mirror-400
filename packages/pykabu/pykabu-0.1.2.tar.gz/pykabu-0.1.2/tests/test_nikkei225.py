"""Tests for nikkei225 data source"""

from pykabu.sources.nikkei225 import (
    RankItem,
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


class TestRankItem:
    """Tests for RankItem dataclass"""

    def test_rank_item_creation(self):
        """Test creating a RankItem"""
        item = RankItem(
            name="東京エレクトロン",
            contribution="+82.23",
            price="38,170",
            change="▲2.20%",
        )
        assert item.name == "東京エレクトロン"
        assert item.contribution == "+82.23"
        assert item.price == "38,170"
        assert item.change == "▲2.20%"

    def test_rank_item_negative_contribution(self):
        """Test RankItem with negative contribution"""
        item = RankItem(
            name="アドバンテスト",
            contribution="-254.03",
            price="20,605",
            change="▼4.41%",
        )
        assert item.name == "アドバンテスト"
        assert item.contribution == "-254.03"
        assert item.change == "▼4.41%"

    def test_rank_item_equality(self):
        """Test RankItem equality comparison"""
        item1 = RankItem("Test", "+10.00", "1,000", "▲1.00%")
        item2 = RankItem("Test", "+10.00", "1,000", "▲1.00%")
        assert item1 == item2

    def test_rank_item_with_empty_values(self):
        """Test RankItem with empty values"""
        item = RankItem(
            name="",
            contribution="",
            price="",
            change="",
        )
        assert item.name == ""
        assert item.contribution == ""

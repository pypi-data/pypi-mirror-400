"""
nikkei225jp.com data source

Usage:
    from pykabu.sources import nikkei225

    # Get economic schedule
    schedule = nikkei225.get_schedule()
    today = nikkei225.get_today_schedule()

    # Get market indices
    indices = nikkei225.get_indices()
"""

from dataclasses import dataclass
from datetime import date, timedelta
from html.parser import HTMLParser

from pykabu.utils.http import fetch_page

BASE_URL = "https://nikkei225jp.com"


# =============================================================================
# Schedule
# =============================================================================

@dataclass
class ScheduleItem:
    """A single schedule item from the economic calendar"""
    date_str: str
    time: str
    importance: str
    indicator: str
    result: str
    forecast: str
    previous: str

    @property
    def star_count(self) -> int:
        """Count the number of stars in importance"""
        return self.importance.count("★")


class _ScheduleTableParser(HTMLParser):
    """Custom HTML parser for the schedule table"""

    def __init__(self):
        super().__init__()
        self.items: list[ScheduleItem] = []
        self.in_table = False
        self.in_row = False
        self.current_cell_class = ""
        self.current_cell_data = ""
        self.current_date = ""
        self.current_row: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        attrs_dict = dict(attrs)
        if tag == "table" and attrs_dict.get("id") == "SihyoT":
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.in_row = True
            self.current_row = {}
        elif self.in_row and tag == "td":
            self.current_cell_class = attrs_dict.get("class", "")
            self.current_cell_data = ""

    def handle_endtag(self, tag: str):
        if tag == "table" and self.in_table:
            self.in_table = False
        elif tag == "tr" and self.in_row:
            self._process_row()
            self.in_row = False
        elif tag == "td" and self.in_row:
            data = self.current_cell_data.strip()
            cell_class = self.current_cell_class
            if "date" in cell_class:
                self.current_date = data
            elif "time" in cell_class:
                self.current_row["time"] = data
            elif "priority" in cell_class:
                self.current_row["priority"] = data
            elif "event" in cell_class:
                self.current_row["event"] = data
            elif "result" in cell_class:
                self.current_row["result"] = data
            elif "expectation" in cell_class:
                self.current_row["forecast"] = data
            elif "last" in cell_class:
                self.current_row["previous"] = data
            self.current_cell_class = ""
            self.current_cell_data = ""

    def handle_data(self, data: str):
        if self.in_row and self.current_cell_class:
            self.current_cell_data += data

    def _process_row(self):
        if "time" in self.current_row and "event" in self.current_row:
            self.items.append(ScheduleItem(
                date_str=self.current_date,
                time=self.current_row.get("time", ""),
                importance=self.current_row.get("priority", ""),
                indicator=self.current_row.get("event", ""),
                result=self.current_row.get("result", "") or "-",
                forecast=self.current_row.get("forecast", "") or "-",
                previous=self.current_row.get("previous", "") or "-",
            ))


def _date_patterns(target: date) -> list[str]:
    return [
        f"{target.month}/{target.day}",
        f"{target.month:02d}/{target.day:02d}",
        f"{target.month}月{target.day}日",
    ]


def _matches_date(item: ScheduleItem, target: date) -> bool:
    patterns = _date_patterns(target)
    return any(pattern in item.date_str for pattern in patterns)


def get_schedule() -> list[ScheduleItem]:
    """Fetch all schedule items from nikkei225jp.com/schedule/"""
    html = fetch_page(BASE_URL, "/schedule/")
    parser = _ScheduleTableParser()
    parser.feed(html)
    return parser.items


def get_schedule_for_date(target: date) -> list[ScheduleItem]:
    """Get schedule items for a specific date."""
    return [item for item in get_schedule() if _matches_date(item, target)]


def get_today_schedule() -> list[ScheduleItem]:
    """Get schedule items for today."""
    return get_schedule_for_date(date.today())


def get_tomorrow_schedule() -> list[ScheduleItem]:
    """Get schedule items for tomorrow."""
    return get_schedule_for_date(date.today() + timedelta(days=1))


def get_week_schedule() -> list[ScheduleItem]:
    """Get schedule items for this week (today through 7 days)."""
    all_items = get_schedule()
    today = date.today()
    week_dates = [today + timedelta(days=i) for i in range(7)]
    return [item for item in all_items if any(_matches_date(item, d) for d in week_dates)]


def filter_schedule_by_importance(items: list[ScheduleItem], min_stars: int) -> list[ScheduleItem]:
    """Filter schedule items by minimum importance (star count)."""
    return [item for item in items if item.star_count >= min_stars]


# =============================================================================
# Indices
# =============================================================================

@dataclass
class IndexItem:
    """A market index item"""
    name: str
    value: str
    change: str
    percent: str


# Default indices shown by `kabu index`
DEFAULT_INDEX_CODES = {
    "111": "日経平均",
    "211": "NYダウ",
    "511": "ドル円",
    "514": "ユーロ円",
    "621": "VIX恐怖指数",
    "811": "米国債10年",
    "921": "WTI原油",
    "931": "NY金",
}

# All known indices available on nikkei225jp.com
# Updated periodically via CI/CD (see .github/workflows/update-indices.yml)
ALL_KNOWN_INDICES = {
    # Japanese
    "111": "日経平均",
    "112": "TOPIX",
    "121": "グロース250",
    # US
    "211": "NYダウ",
    "212": "NASDAQ",
    "213": "S&P500",
    "214": "NASDAQ100",
    "611": "フィラデルフィア半導体",
    "613": "ラッセル2000",
    # International
    "313": "韓国KOSPI",
    "321": "中国上海総合",
    "331": "香港ハンセン",
    "352": "インドNifty",
    "411": "仏CAC40",
    "412": "独DAX",
    "413": "英FTSE100",
    # Bonds/VIX
    "151": "日本国債10年",
    "621": "VIX恐怖指数",
    "811": "米国債10年",
    # Commodities
    "921": "WTI原油",
    "931": "NY金",
    # Forex
    "511": "ドル円",
    "514": "ユーロ円",
    "523": "ユーロドル",
    # Crypto
    "1001": "ビットコイン",
    "1011": "イーサリアム",
}

# Backward compatibility alias
INDEX_CODES = DEFAULT_INDEX_CODES


def get_default_indices() -> dict[str, str]:
    """Return the default index codes."""
    return DEFAULT_INDEX_CODES.copy()


def get_all_known_indices() -> dict[str, str]:
    """Return all known index codes."""
    return ALL_KNOWN_INDICES.copy()


def get_indices(codes: dict[str, str] | None = None) -> list[IndexItem]:
    """Fetch market index data from nikkei225jp.com (requires playwright).

    Args:
        codes: Optional dict of code->name mappings. If None, uses DEFAULT_INDEX_CODES.
    """
    from playwright.sync_api import sync_playwright

    if codes is None:
        codes = DEFAULT_INDEX_CODES

    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")

        try:
            page.wait_for_function(
                "document.querySelector('#V511')?.textContent?.trim().length > 0",
                timeout=500
            )
        except Exception:
            pass

        for code, name in codes.items():
            try:
                value = page.locator(f"#V{code}").text_content(timeout=500) or "-"
                change = page.locator(f"#Z{code}").text_content(timeout=500) or "-"
                percent = page.locator(f"#P{code}").text_content(timeout=500) or "-"
                items.append(IndexItem(
                    name=name,
                    value=value.strip(),
                    change=change.strip(),
                    percent=percent.strip(),
                ))
            except Exception:
                pass

        browser.close()

    return items

# pykabu

Python library and CLI for Japanese stock market data.

## Requirements

- Python 3.10+

## Installation

### Quick Install (Global)

```bash
# 1. Install pykabu
pip install pykabu

# 2. Install browser for market index feature
playwright install chromium
```

### Recommended: Virtual Environment with uv

[uv](https://docs.astral.sh/uv/) is a fast Python package manager written in Rust.

**Step 1: Install uv** (one-time setup)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Step 2: Create virtual environment and install**

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows (PowerShell)

# Install pykabu
uv pip install pykabu

# Install browser for market index feature
playwright install chromium
```

### Alternative: pip + venv

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows (PowerShell)

# Install pykabu
pip install pykabu

# Install browser for market index feature
playwright install chromium
```

### Platform Notes

- **macOS**: Works out of the box
- **Windows**: Use PowerShell (not CMD)
- **Linux**: If playwright fails, run: `playwright install-deps chromium`

## CLI Usage

```bash
kabu sche              # Today's schedule
kabu sche -t           # Tomorrow's schedule
kabu sche -w           # This week's schedule
kabu sche -i 3         # Filter by importance (>= 3 stars)

# Market indices
kabu index             # Default 8 indices
kabu index --all       # All known indices (~25)
kabu index --custom    # Custom configured indices
kabu index --merged    # Default + custom indices

# Configuration
kabu config show                      # Show current config
kabu config set default_importance 3  # Set default star filter

# Custom indices
kabu config index list                # List all available codes
kabu config index add 212             # Add NASDAQ
kabu config index add 1001            # Add Bitcoin
kabu config index remove 212          # Remove an index
```

## Library Usage

```python
from pykabu.sources import nikkei225

# Schedule data
schedule = nikkei225.get_schedule()
today = nikkei225.get_today_schedule()
tomorrow = nikkei225.get_tomorrow_schedule()
week = nikkei225.get_week_schedule()

# Market indices (requires playwright)
indices = nikkei225.get_indices()
```

## Data Sources

- [nikkei225jp.com](https://nikkei225jp.com) - Economic calendar and market indices

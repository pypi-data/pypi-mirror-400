# v2.1.0 Release Notes

## Description
Major update to align with Nimble Search API backend improvements (v1.4.0-v1.6.0). This release introduces breaking changes for API parameter names, adds AI-powered Web Search Agent (WSA) focus modes, improves the driver parameter system, and adds time-based filtering capabilities.

## Breaking Changes

### API Parameter Renames
- **`num_results` → `max_results`**: Primary parameter name changed (backward compatible via alias)
- **`parsing_type` → `output_format`**: Renamed for clarity (default changed to `markdown`)
- **`topic` → `focus`**: Renamed to better describe search specialization modes (backward compatible via alias)

### Response Structure Updates
- **`body` → `results`**: Top-level response key flattened
- **`snippet` → `description`**: Metadata field renamed for consistency

### Driver Parameter Improvements
- **Type changed from `str` to `BrowserlessDriver` enum**: Type-safe driver selection
- **Default changed from `"vx6"` to `None`**: API now auto-selects optimal driver
- **New driver variants**: Added `vx8-pro`, `vx10-pro`, `vx12`, `vx12-pro` options

## New Features

### AI-Powered Web Search Agents (WSA)
Added three new focus modes powered by AI search engines:
- **`shopping`**: E-commerce product search across major platforms
- **`geo`**: Generative Engine Optimization search
- **`social`**: Social media content discovery

Traditional SERP-based modes remain: `general`, `news`, `location`

### Time-Based Filtering
- **`time_range` parameter**: Quick recency filters (`hour`, `day`, `week`, `month`, `year`)
- Alternative to `start_date`/`end_date` for fast time-based queries

### Enhanced Driver System
- **`BrowserlessDriver` enum**: Type-safe driver selection with 7 variants
- **Auto-selection**: API intelligently selects driver when not specified
- **Extended options**: Support for pro variants and premium vx12 drivers

## Migration Guide

### Update Parameter Names
```python
# Before (v2.0.0)
retriever = NimbleSearchRetriever(
    num_results=5,
    topic="news"
)

# After (v2.1.0)
retriever = NimbleSearchRetriever(
    max_results=5,  # renamed
    focus="news"    # renamed
)

# Backward compatibility maintained via aliases
retriever = NimbleSearchRetriever(
    num_results=5,  # still works!
    topic="news"    # still works!
)
```

### Update Driver Usage
```python
# Before (v2.0.0)
retriever = NimbleExtractRetriever(driver="vx6")
tool = NimbleExtractTool()
tool.invoke({"urls": [...], "driver": "vx8"})

# After (v2.1.0) - Recommended
from langchain_nimble import BrowserlessDriver

retriever = NimbleExtractRetriever(driver=BrowserlessDriver.VX8)
tool = NimbleExtractTool()
tool.invoke({"urls": [...], "driver": BrowserlessDriver.VX8})

# Or let API auto-select (new default)
retriever = NimbleExtractRetriever()  # driver=None, API chooses best
tool.invoke({"urls": [...]})  # no driver specified
```

### Use New Focus Modes
```python
# AI-powered WSA modes
shopping_retriever = NimbleSearchRetriever(focus="shopping")
geo_retriever = NimbleSearchRetriever(focus="geo")
social_retriever = NimbleSearchRetriever(focus="social")
```

### Use Time Range Filtering
```python
# Quick recency filter
recent_retriever = NimbleSearchRetriever(
    time_range="week",  # last 7 days
    focus="news"
)

# Alternative to start_date/end_date
docs = recent_retriever.invoke("latest AI developments")
```

## Technical Improvements
- **Type safety**: Enum-based driver selection with mypy strict mode
- **API alignment**: 100% compatibility with backend v1.6.0 schema
- **Documentation**: Updated all examples, docstrings, and parameter tables
- **Testing**: All 30 unit tests pass, backward compatibility verified

## Full Changelog
**Breaking Changes**:
- Rename `num_results` to `max_results` (alias maintained for backward compatibility)
- Rename `parsing_type` to `output_format` (default changed to markdown)
- Rename `topic` to `focus` (alias maintained for backward compatibility)
- Update response parsing for flattened structure (`body`→`results`, `snippet`→`description`)
- Change driver parameter to `BrowserlessDriver | None` type with `None` default

**New Features**:
- Add `time_range` parameter for quick recency filtering
- Add AI-powered WSA focus modes: `shopping`, `geo`, `social`
- Add `BrowserlessDriver` enum with 7 driver variants
- Export `BrowserlessDriver` enum for user access

**Improvements**:
- API auto-selects optimal driver when not specified
- Enhanced driver options with pro variants and vx12 support
- Updated all documentation and examples
- Improved type safety with strict mypy checking

---

**Full Changelog**: https://github.com/Nimbleway/langchain-nimble/compare/v2.0.0...v2.1.0

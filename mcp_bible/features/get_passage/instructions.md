# Bible Passage Retrieval Tool

Get Bible passages from multiple translations with automatic content parsing and cleaning.

This tool retrieves Bible passages from BibleGateway.com, supporting multiple Bible versions and passage formats. The content is automatically cleaned and formatted for easy reading.

**Legal Notice**: All Bible text content is sourced from BibleGateway.com. All copyright, licensing, and other legal concerns regarding the Bible translations and text content are covered by BibleGateway.com's terms of service and licensing agreements with the respective publishers. This tool serves as an interface to publicly available content and respects all applicable copyright restrictions.

## Parameters

### passage (required)
- **Type**: string
- **Description**: Bible reference(s) to retrieve
- **Format**: Book Chapter:Verse or Book Chapter
- **Examples**:
  - `"John 3:16"` - Single verse
  - `"John 3:16-21"` - Verse range
  - `"John 3"` - Entire chapter
  - `"Mark 2:1-12"` - Specific verse range
  - `"John 3:16; Romans 8:28"` - Multiple references

### version (optional)
- **Type**: string  
- **Default**: the server's configured default (ESV unless changed)
- **Description**: Bible translation version. Any BibleGateway version abbreviation works and is passed through as-is (e.g. `ESV`, `NIV`, `KJV`, `NASB`, `LSB`). See https://www.biblegateway.com/versions/ for the full list.

## Usage Examples

### Single verse:
```json
{
  "passage": "John 3:16",
  "version": "NIV"
}
```

### Chapter range:
```json
{
  "passage": "Mark 2:1-12",
  "version": "ESV"
}
```

### Entire chapter:
```json
{
  "passage": "Psalm 23",
  "version": "KJV"
}
```

### Multiple passages:
```json
{
  "passage": "John 3:16; Romans 8:28; Philippians 4:13",
  "version": "ESV"
}
```

## Response Format

Returns a structured response containing:
- `success`: Whether the request was successful
- `passage`: The requested Bible reference
- `version`: The Bible version used
- `text`: The passage text (cleaned and formatted)
- `error`: Error message if request failed

If BibleGateway doesn't offer the requested version, the response has `success: false` and the error in `error`.

## When to Use This Tool

- Scripture study and research
- Sermon preparation and biblical analysis
- Cross-referencing verses across translations
- Gathering biblical supporting material
- Comparing different translation renderings

## Content Processing

The tool automatically:
- Removes HTML formatting and ads
- Cleans up spacing and formatting
- Preserves verse numbers and structure  
- Handles chapter headings appropriately
- Supports multi-passage requests

## Legal Compliance and Copyright

**Content Source**: All Bible text is retrieved from BibleGateway.com (https://www.biblegateway.com/)

**Copyright Protection**: BibleGateway.com handles all copyright, licensing, and legal compliance for Bible translations. Each translation (ESV, NIV, KJV, etc.) has specific copyright holders and licensing terms that are managed and enforced by BibleGateway.com.

**Fair Use**: This tool accesses publicly available content through BibleGateway.com's web interface for educational, research, and personal study purposes. All copyright and licensing obligations are covered by BibleGateway.com's agreements with publishers.

**Compliance**: Users should be aware that while this tool provides access to Bible content, all legal responsibilities regarding copyright, attribution, and proper use remain with the respective copyright holders as managed by BibleGateway.com.
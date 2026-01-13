# epubkit

A comprehensive EPUB processing toolkit for Python.

## Features

- **EPUB Reading**: Parse EPUB files with support for EPUB2/3 standards
- **Table of Contents**: Extract and navigate book structure
- **Content Access**: Read chapters and access metadata
- **CFI Support**: Canonical Fragment Identifier parsing and generation
- **Layout Properties**: Access EPUB3 layout and rendering properties
- **Enhanced Spine**: Rich spine item information with properties
- **Hook System**: Extensible event system for customization
- **Extensible**: Plugin architecture for different content sources

## Installation

```bash
pip install epubkit
```

## Quick Start

```python
import epubkit

# Open an EPUB file
book = epubkit.open("my_book.epub")

# Access metadata
print(f"Title: {book.title}")

# Navigate chapters
for chapter in book.spine:
    print(f"- {chapter['title']}")

# Read content
content = book.read_chapter("chapter1.xhtml")

# CFI support
cfi = epubkit.CFIGenerator.generate_cfi(spine_index, node, offset)
```

## Enhanced Features

### Layout Properties

Access EPUB3 layout and rendering properties from the OPF file:

```python
# Get layout properties
layout = book.layout_properties
print(f"Layout: {layout.get('layout')}")           # pre-paginated/reflowable
print(f"Flow: {layout.get('flow')}")               # paginated/scrolled
print(f"Reading direction: {layout.get('page_progression_direction')}")  # ltr/rtl
```

### Enhanced Spine Items

Access rich spine item information with properties:

```python
# Get enhanced spine items
for item in book.spine_items:
    print(f"Chapter: {item.href}")
    print(f"Linear: {item.linear}")                # True/False
    print(f"Properties: {item.properties}")        # ['rendition:layout-pre-paginated']
```

### Spine CFI Generation

Generate CFIs for spine items (useful for bookmarks):

```python
# Generate CFI for first chapter
cfi = book.get_spine_cfi(0)
print(f"Chapter CFI: {cfi}")  # epubcfi(/6/2[chapter1]/)
```

### Hook System

Use the extensible hook system for customization:

```python
# Register event handlers
def on_toc_built(epub_instance, toc_data):
    print(f"TOC built with {len(toc_data['raw_chapters'])} chapters")

def on_chapter_loaded(epub_instance, href, content):
    print(f"Loaded chapter: {href}")

book.hooks.toc_built.register(on_toc_built)
book.hooks.chapter_loaded.register(on_chapter_loaded)

# Hooks are triggered automatically during normal operations
_ = book.toc  # Triggers toc_built hook
content = book.read_chapter("chapter1.xhtml")  # Triggers chapter_loaded hook
```

Available hooks:
- `toc_built`: After TOC is built
- `toc_parsed`: After TOC structure is parsed
- `metadata_extracted`: After metadata is extracted
- `layout_parsed`: After layout properties are parsed
- `spine_processed`: After spine items are processed
- `content_parsed`: After chapter content is parsed
- `chapter_loaded`: After chapter is loaded from disk

## License

MIT License

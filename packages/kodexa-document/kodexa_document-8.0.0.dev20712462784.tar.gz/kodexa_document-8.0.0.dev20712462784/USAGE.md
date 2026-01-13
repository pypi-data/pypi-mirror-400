# Kodexa Document Python - Usage Guide

This guide provides comprehensive examples of using the Kodexa Document Python wrapper, which provides Python bindings for the Go-based Kodexa Document library using CFFI.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Basic Document Operations](#basic-document-operations)
3. [Working with ContentNodes](#working-with-contentnodes)
4. [Features and Tags](#features-and-tags)
5. [Document Queries and Selectors](#document-queries-and-selectors)
6. [Document Persistence](#document-persistence)
7. [Metadata and Labels](#metadata-and-labels)
8. [Processing Steps and Validations](#processing-steps-and-validations)
9. [Spatial Operations](#spatial-operations)
10. [Error Handling](#error-handling)
11. [Performance and Memory Management](#performance-and-memory-management)

## Installation and Setup

### Prerequisites

- Python 3.12+
- Virtual environment with CFFI and pytest
- Compiled Go shared library

### Setup Steps

```bash
# 1. Set up virtual environment (from repository root)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install cffi pytest

# 3. Build the Go library (from lib/go)
cd lib/go
make linux  # or: make darwin, make windows

# 4. Test the installation
cd ../python
python -c "import kodexa_document; print('Success!')"
```

### Basic Import

```python
from kodexa_document import Document, ContentNode, DocumentError
from kodexa_document.errors import DocumentNotFoundError
```

## Basic Document Operations

### Creating Documents

```python
from kodexa_document import Document

# Create an empty in-memory document (fastest)
doc = Document(inmemory=True)
print(f"Created document with UUID: {doc.uuid}")
print(f"Document version: {doc.version}")

# Create with metadata
metadata = {
    "title": "My Document",
    "author": "John Doe",
    "created_date": "2024-01-15",
    "tags": ["important", "draft"]
}
doc = Document(metadata=metadata, inmemory=True)
print(f"Document metadata: {doc.metadata}")

# Create from text (creates document structure)
text = "Line 1\nLine 2\nLine 3"
doc = Document.from_text(text, separator="\n", inmemory=True)

# Always close documents when done
doc.close()
```

### Using Context Manager (Recommended)

```python
# Automatic cleanup with context manager
with Document(inmemory=True) as doc:
    print(f"Working with document: {doc.uuid}")
    # Document operations here
    json_output = doc.to_json()
# Document automatically closed after context
```

### Document Properties

```python
with Document(inmemory=True) as doc:
    # Access document properties
    uuid = doc.uuid  # Document UUID
    version = doc.version  # Document version (6.0.0)

    # Document reference (for platform tracking)
    doc.ref = "myorg/document-store:1.0.0"
    print(f"Document ref: {doc.ref}")

    # Export to different formats
    json_str = doc.to_json(indent=2)
    doc_dict = doc.to_dict()  # Legacy Python compatible format

    print(f"UUID: {uuid}")
    print(f"Version: {version}")
```

## Working with ContentNodes

ContentNodes form the hierarchical structure of documents (like DOM for web pages).

### Creating and Managing Nodes

```python
with Document(inmemory=True) as doc:
    # Create root document node
    root = doc.create_node("document", "Root Document")
    doc.content_node = root  # Set as document root

    # Create child nodes
    section = doc.create_node("section", "Introduction", parent=root)
    para1 = doc.create_node("paragraph", "First paragraph", parent=section)
    para2 = doc.create_node("paragraph", "Second paragraph", parent=section)

    # Create node with specific properties
    special_node = doc.create_node(
        "highlight",
        "Important text",
        parent=section,
        virtual=True,    # Virtual node (not persisted in some contexts)
        index=10         # Specific index/order
    )

    print(f"Document has {root.child_count} children")
    print(f"Section content: {section.content}")
```

### Node Navigation

```python
with Document(inmemory=True) as doc:
    root = doc.create_node("document", "Root")
    doc.content_node = root

    # Create hierarchy
    chapter = doc.create_node("chapter", "Chapter 1", parent=root)
    para1 = doc.create_node("paragraph", "First para", parent=chapter)
    para2 = doc.create_node("paragraph", "Second para", parent=chapter)

    # Navigate hierarchy
    parent = para1.get_parent()  # Returns chapter
    children = chapter.get_children()  # Returns [para1, para2]
    siblings = para1.get_siblings()  # Returns [para2]

    # Navigate siblings
    next_node = para1.next_node()  # Returns para2
    prev_node = para2.previous_node()  # Returns para1

    # Get path from root
    path = para1.get_path()  # Returns [root, chapter, para1]

    # Access by index
    first_child = chapter.get_child(0)  # Returns para1

    print(f"Chapter has {len(children)} children")
    print(f"Para1 has {len(siblings)} siblings")
```

### Content Operations

```python
with Document(inmemory=True) as doc:
    node = doc.create_node("paragraph", "Original content")

    # Content access and modification
    print(f"Content: {node.content}")
    node.content = "Modified content"

    # Content parts (for complex content)
    node.set_content_parts(["Part 1", "Part 2", "Part 3"])
    parts = node.get_content_parts()
    print(f"Content parts: {parts}")

    # Get all content from node and descendants
    root = doc.create_node("document", "Title")
    doc.content_node = root
    child = doc.create_node("paragraph", "Body text", parent=root)

    all_content = root.get_all_content(separator=" | ")
    print(f"All content: {all_content}")  # "Title | Body text"
```

## Features and Tags

Features and tags provide metadata and annotations for content nodes.

### Working with Features

```python
with Document(inmemory=True) as doc:
    node = doc.create_node("paragraph", "Styled text")

    # Add features (key-value metadata)
    node.add_feature("style", "font-family", "Arial")
    node.add_feature("style", "font-size", "12pt")
    node.add_feature("layout", "margin", {"top": 10, "bottom": 5})

    # Get specific feature
    font_feature = node.get_feature("style", "font-family")
    if font_feature:
        print(f"Font: {font_feature.get_value()}")

    # Get features by type
    style_features = node.get_features_of_type("style")
    print(f"Found {len(style_features)} style features")

    # Get all features
    all_features = node.get_features()
    print(f"Total features: {len(all_features)}")

    # Remove feature
    node.remove_feature("style", "font-size")

    # Feature values are always stored as arrays (single=True by default)
    node.add_feature("tags", "keyword", "python")
    node.add_feature("tags", "keyword", "document")  # Appends to array

    keyword_feature = node.get_feature("tags", "keyword")
    print(f"Keywords: {keyword_feature.value}")  # ['python', 'document']
```

### Working with Tags

```python
with Document(inmemory=True) as doc:
    node = doc.create_node("paragraph", "Important text")

    # Simple tagging
    node.tag("important")
    node.tag("reviewed")

    # Tag with metadata
    node.tag("entity",
            confidence=0.95,
            value="person",
            tag_uuid="unique-id-123")

    # Check for tags
    if node.has_tag("important"):
        print("Node is tagged as important")

    # Get specific tag details
    entity_tag = node.get_tag("entity")
    if entity_tag:
        print(f"Entity confidence: {entity_tag.get('Confidence', 'N/A')}")
        print(f"Entity value: {entity_tag.get('Value', 'N/A')}")

    # Get all tags
    all_tags = node.get_tags()  # Returns list of tag names
    print(f"All tags: {all_tags}")

    # Remove tag
    node.remove_tag("reviewed")

    # Check if node has any tags
    has_any_tags = node.has_tags()
    print(f"Has tags: {has_any_tags}")
```

## Document Queries and Selectors

Use XPath-like selectors to query document structure.

### Basic Selectors

```python
with Document.from_text("Para 1\nPara 2\nPara 3", separator="\n", inmemory=True) as doc:
    # Find all nodes
    all_nodes = doc.select("//*")
    print(f"Total nodes: {len(all_nodes)}")

    # Find by node type
    paragraphs = doc.select("//paragraph")
    print(f"Found {len(paragraphs)} paragraphs")

    # Find first match
    first_para = doc.select_first("//paragraph")
    if first_para:
        print(f"First paragraph: {first_para.content}")

    # Find with content filter
    specific_nodes = doc.select("//paragraph[contains(@content, 'Para 2')]")
    print(f"Matching nodes: {len(specific_nodes)}")

    # Use first_only parameter
    first_only = doc.select("//paragraph", first_only=True)
    print(f"First only result: {len(first_only)} nodes")
```

### Advanced Selectors

```python
with Document(inmemory=True) as doc:
    root = doc.create_node("document", "Root")
    doc.content_node = root

    # Create tagged content
    section = doc.create_node("section", "Section 1", parent=root)
    para = doc.create_node("paragraph", "Important text", parent=section)
    para.tag("important")
    para.add_feature("style", "weight", "bold")

    # Select with variables
    variables = {"tag_name": "important"}
    tagged_nodes = doc.select("//paragraph[@tag=$tag_name]", variables)

    # Select from specific node (relative queries)
    section_content = section.select(".//paragraph")
    print(f"Paragraphs in section: {len(section_content)}")

    # Get all tagged nodes in document
    all_tagged = doc.get_all_tagged_nodes()
    print(f"All tagged nodes: {len(all_tagged)}")
```

## Document Persistence

### Saving and Loading Documents

```python
import tempfile
import os

# Save to file
with Document.from_text("Important data", inmemory=True) as doc:
    root = doc.content_node
    root.tag("processed")

    # Save to KDDB file
    output_path = "/tmp/important.kddb"
    doc.save(output_path)
    print(f"Saved document {doc.uuid} to {output_path}")

# Load from file
try:
    # Load with detached copy (safe, default)
    with Document.from_kddb(output_path, detached=True, inmemory=True) as doc:
        print(f"Loaded document: {doc.uuid}")

        # Access the content
        root = doc.content_node
        if root.has_tag("processed"):
            print("Document was previously processed")

except DocumentNotFoundError as e:
    print(f"Document not found: {e}")
```

### Working with Bytes

```python
with Document.from_text("Sample content", inmemory=True) as doc:
    # Get document as bytes
    kddb_bytes = doc.to_kddb()  # Returns bytes when no path specified
    print(f"KDDB size: {len(kddb_bytes)} bytes")

    # Create document from bytes
    with Document.from_kddb(kddb_bytes, inmemory=True) as loaded_doc:
        print(f"Loaded from bytes: {loaded_doc.uuid}")

# Round-trip through JSON
with Document(inmemory=True) as doc:
    doc.set_metadata("test_key", "test_value")

    json_str = doc.to_json()

    with Document.from_json(json_str, inmemory=True) as json_doc:
        print(f"From JSON: {json_doc.get_metadata('test_key')}")
```

## Metadata and Labels

### Document Metadata

```python
with Document(inmemory=True) as doc:
    # Set individual metadata items
    doc.set_metadata("title", "My Document")
    doc.set_metadata("author", "John Doe")
    doc.set_metadata("complex_data", {"nested": "value", "array": [1, 2, 3]})

    # Get metadata items
    title = doc.get_metadata("title")
    author = doc.get_metadata("author")
    print(f"Title: {title}, Author: {author}")

    # Get all metadata as dict
    all_metadata = doc.metadata
    print(f"All metadata: {all_metadata}")

    # Set metadata from dict
    doc.metadata = {
        "project": "Analysis",
        "version": "1.0",
        "tags": ["important", "processed"]
    }
```

### Labels and Mixins

```python
with Document(inmemory=True) as doc:
    # Add labels (categories/classifications)
    doc.add_label("invoice")
    doc.add_label("financial")
    doc.add_label("Q4-2023")

    # Get labels
    labels = doc.labels
    print(f"Document labels: {labels}")

    # Remove label
    doc.remove_label("Q4-2023")

    # Add mixins (capabilities/behaviors)
    doc.add_mixin("extractable")
    doc.add_mixin("searchable")
    doc.add_mixin("reportable")

    # Get mixins
    mixins = doc.mixins
    print(f"Document mixins: {mixins}")
```

### External Data

```python
with Document(inmemory=True) as doc:
    # Store arbitrary external data by key
    doc.set_external_data({"source": "scanner", "dpi": 300}, "scan_info")
    doc.set_external_data({"user": "john", "timestamp": "2024-01-15"}, "processing_info")
    doc.set_external_data({"pipeline": "v2", "version": 1.2})  # Default key

    # Retrieve external data
    scan_info = doc.get_external_data("scan_info")
    processing_info = doc.get_external_data("processing_info")
    default_data = doc.get_external_data()  # Default key

    # Get all external data keys
    keys = doc.get_external_data_keys()
    print(f"External data keys: {keys}")

    print(f"Scan DPI: {scan_info.get('dpi', 'Unknown')}")
```

## Processing Steps and Validations

### Processing Steps

```python
from kodexa_document.models import ProcessingStep

with Document(inmemory=True) as doc:
    # Create processing steps
    ocr_step = ProcessingStep("OCR", "Text extraction from images")
    nlp_step = ProcessingStep("NLP", "Natural language processing")
    validation_step = ProcessingStep("Validation", "Data validation")

    # Build processing hierarchy
    ocr_step.add_child(nlp_step)
    nlp_step.add_child(validation_step)

    # Add to document
    doc.add_processing_step(ocr_step)

    # Get processing steps
    steps = doc.get_processing_steps()
    print(f"Processing steps: {len(steps)}")
```

### Validations

```python
with Document(inmemory=True) as doc:
    # Define validations
    validations = [
        {
            "taxonomy_ref": "myorg/business-taxonomy:1.0.0",
            "taxon_path": "document/invoice",
            "validation": {
                "name": "InvoiceNumberRequired",
                "description": "Invoice must have a number",
                "ruleFormula": "invoice_number != null",
                "messageFormula": "Invoice number is required"
            }
        },
        {
            "taxonomy_ref": "myorg/business-taxonomy:1.0.0",
            "taxon_path": "document/invoice/amount",
            "validation": {
                "name": "AmountPositive",
                "description": "Amount must be positive",
                "ruleFormula": "amount > 0",
                "messageFormula": "Amount must be greater than zero"
            }
        }
    ]

    # Set validations
    doc.set_validations(validations)

    # Get validations
    retrieved_validations = doc.get_validations()
    print(f"Document has {len(retrieved_validations)} validations")
```

## Spatial Operations

### Bounding Boxes

```python
with Document(inmemory=True) as doc:
    node = doc.create_node("text", "Positioned text")

    # Set bounding box (x1, y1, x2, y2)
    node.set_bbox(10.0, 20.0, 100.0, 40.0)

    # Get bounding box
    bbox = node.get_bbox()
    if bbox:
        x1, y1, x2, y2 = bbox
        print(f"Bounding box: ({x1}, {y1}) to ({x2}, {y2})")

        # Calculate dimensions
        width = x2 - x1
        height = y2 - y1
        print(f"Dimensions: {width} x {height}")
```

### Rotation and Spatial Methods

```python
with Document(inmemory=True) as doc:
    node = doc.create_node("text", "Rotated text")
    node.set_bbox(0.0, 0.0, 100.0, 50.0)

    # Rotation operations (if implemented)
    try:
        # These methods may be available for spatial operations
        rotated_bbox = node.rotate_bbox(45.0)  # Rotate 45 degrees
        print(f"Rotated bounding box: {rotated_bbox}")
    except AttributeError:
        print("Advanced spatial operations not available")
```

## Error Handling

### Common Error Patterns

```python
from kodexa_document.errors import DocumentError, DocumentNotFoundError

# Handle file operations
try:
    doc = Document.from_kddb("/nonexistent/file.kddb")
except DocumentNotFoundError as e:
    print(f"File not found: {e}")
except DocumentError as e:
    print(f"Document error: {e}")

# Handle closed document access
doc = Document(inmemory=True)
doc.close()

try:
    uuid = doc.uuid  # Will raise RuntimeError
except RuntimeError as e:
    print(f"Cannot access closed document: {e}")

# Handle invalid operations
with Document(inmemory=True) as doc:
    root = doc.create_node("root")
    child = doc.create_node("child", parent=root)
    other_node = doc.create_node("other")

    try:
        # Try to remove a non-child
        root.remove_child(other_node)
    except DocumentError as e:
        print(f"Invalid operation: {e}")
```

### Safe Operations Pattern

```python
def safe_document_operation(file_path):
    """Safely load and process a document."""
    try:
        with Document.from_kddb(file_path, inmemory=True) as doc:
            # Validate document
            if not doc.uuid:
                raise DocumentError("Document has no UUID")

            # Process document
            result = {
                "uuid": doc.uuid,
                "version": doc.version,
                "node_count": len(doc.select("//*")),
                "json": doc.to_json()
            }
            return result

    except DocumentNotFoundError:
        print(f"Document not found: {file_path}")
        return None
    except DocumentError as e:
        print(f"Document error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Use the safe function
result = safe_document_operation("/path/to/document.kddb")
if result:
    print(f"Successfully processed document {result['uuid']}")
```

## Performance and Memory Management

### In-Memory vs File-Based Documents

```python
import time

# In-memory documents (fastest, ~100x faster)
start_time = time.time()
with Document(inmemory=True) as doc:
    root = doc.create_node("document", "Fast processing")
    doc.content_node = root
    for i in range(100):
        doc.create_node("item", f"Item {i}", parent=root)
inmemory_time = time.time() - start_time

# File-based documents (persistent)
start_time = time.time()
with Document(inmemory=False) as doc:
    root = doc.create_node("document", "Persistent processing")
    doc.content_node = root
    for i in range(100):
        doc.create_node("item", f"Item {i}", parent=root)
file_time = time.time() - start_time

print(f"In-memory: {inmemory_time:.3f}s, File-based: {file_time:.3f}s")
print(f"Speed improvement: {file_time/inmemory_time:.1f}x faster")
```

### Memory Management Best Practices

```python
import gc

# Use context managers for automatic cleanup
def process_many_documents(count):
    results = []

    for i in range(count):
        with Document(inmemory=True) as doc:
            # Process document
            root = doc.create_node("document", f"Doc {i}")
            doc.content_node = root

            results.append({
                "index": i,
                "uuid": doc.uuid,
                "size": len(doc.to_json())
            })

            # Document automatically closed by context manager

    return results

# Process batch efficiently
batch_results = process_many_documents(50)
print(f"Processed {len(batch_results)} documents safely")

# Force garbage collection if needed
gc.collect()
```

### Finalizer Cleanup

```python
import weakref

# Documents have automatic finalizer cleanup
def create_document_without_close():
    doc = Document(inmemory=True)
    uuid = doc.uuid
    # Document will be cleaned up by finalizer when GC runs
    return uuid

# This is safe (finalizer will clean up) but not recommended
uuid = create_document_without_close()
print(f"Created document: {uuid}")

# Force GC to demonstrate finalizer cleanup
gc.collect()
print("Finalizer cleanup completed")
```

## Complete Example Application

```python
#!/usr/bin/env python3
"""
Complete example: Document processing pipeline.
"""

import sys
import json
from pathlib import Path
from kodexa_document import Document
from kodexa_document.errors import DocumentError, DocumentNotFoundError


def analyze_document(doc):
    """Analyze document structure and content."""
    analysis = {
        "uuid": doc.uuid,
        "version": doc.version,
        "node_count": 0,
        "tagged_nodes": 0,
        "features_count": 0,
        "content_length": 0
    }

    # Count all nodes
    all_nodes = doc.select("//*")
    analysis["node_count"] = len(all_nodes)

    # Analyze each node
    for node in all_nodes:
        # Count content
        analysis["content_length"] += len(node.content or "")

        # Count tags
        if node.has_tags():
            analysis["tagged_nodes"] += 1

        # Count features
        features = node.get_features()
        analysis["features_count"] += len(features)

    return analysis


def process_text_file(text_path, output_dir):
    """Process text file into structured document."""
    # Read text
    with open(text_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create document
    with Document.from_text(content, separator="\n", inmemory=True) as doc:
        # Add metadata
        doc.set_metadata("source_file", text_path.name)
        doc.set_metadata("char_count", len(content))
        doc.set_metadata("line_count", content.count('\n') + 1)

        # Add labels
        doc.add_label("text-document")
        doc.add_label("processed")

        # Process content nodes
        root = doc.content_node
        if root:
            # Tag important paragraphs (example logic)
            paragraphs = doc.select("//paragraph")
            for i, para in enumerate(paragraphs):
                if len(para.content) > 50:  # Long paragraphs
                    para.tag("long-content")
                    para.add_feature("analysis", "length", len(para.content))

                if i == 0:  # First paragraph
                    para.tag("introduction")

        # Analyze document
        analysis = analyze_document(doc)

        # Save outputs
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = text_path.stem

        # Save KDDB
        kddb_path = output_dir / f"{base_name}.kddb"
        doc.save(str(kddb_path))

        # Save JSON
        json_path = output_dir / f"{base_name}.json"
        with open(json_path, 'w') as f:
            f.write(doc.to_json(indent=2))

        # Save analysis
        analysis_path = output_dir / f"{base_name}_analysis.json"
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)

        print(f"Successfully processed: {text_path}")
        print(f"  Document UUID: {doc.uuid}")
        print(f"  Nodes: {analysis['node_count']}")
        print(f"  Tagged nodes: {analysis['tagged_nodes']}")
        print(f"  Features: {analysis['features_count']}")
        print(f"  Content length: {analysis['content_length']} chars")
        print(f"  Saved to: {kddb_path}")

        return doc.uuid


def main():
    """Main application."""
    if len(sys.argv) != 3:
        print("Usage: python process_document.py <text_file> <output_dir>")
        sys.exit(1)

    text_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not text_file.exists():
        print(f"Error: Text file not found: {text_file}")
        sys.exit(1)

    try:
        # Process the file
        uuid = process_text_file(text_file, output_dir)
        print(f"\nProcessing complete. Document UUID: {uuid}")

        # Verify by loading
        kddb_path = output_dir / f"{text_file.stem}.kddb"
        with Document.from_kddb(str(kddb_path), inmemory=True) as doc:
            print(f"Verification: Successfully loaded {doc.uuid}")

            # Quick analysis of loaded document
            node_count = len(doc.select("//*"))
            tagged_count = len(doc.get_all_tagged_nodes())
            print(f"Loaded document has {node_count} nodes, {tagged_count} tagged")

    except DocumentError as e:
        print(f"Error: Document processing failed - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Best Practices

1. **Always use `inmemory=True`** for maximum performance (unless persistence is required)
2. **Use context managers** (`with` statements) for automatic cleanup
3. **Handle errors appropriately** - catch specific exception types
4. **Structure documents hierarchically** with proper parent-child relationships
5. **Use features and tags** for rich metadata annotation
6. **Leverage selectors** for efficient document querying
7. **Set meaningful metadata** for document tracking and organization
8. **Test with various document sizes** to understand performance characteristics

## Testing and Validation

The Python wrapper includes comprehensive test coverage (413+ tests) covering all features:

```bash
# Run the test suite
cd lib/python
source ../../venv/bin/activate
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_document.py -v          # Document operations
python -m pytest tests/test_contentnode_basic.py -v # ContentNode basics
python -m pytest tests/test_contentnode_features_tags.py -v # Features and tags
python -m pytest tests/test_extraction.py -v       # Advanced extraction
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'cffi'**
   - Solution: `pip install cffi`

2. **Failed to load Go native library**
   - Solution: Build library with `cd lib/go && make linux`

3. **Document is closed error**
   - Solution: Use context managers or check document state

4. **Performance issues**
   - Solution: Use `inmemory=True` for 100x speed improvement

5. **Memory usage with large documents**
   - Solution: Use context managers and process in batches

### Getting Help

- Check the comprehensive test suite in `tests/` for usage examples
- See `test_minimal.py` for basic functionality overview
- Refer to the main repository documentation for architecture details
- Review test files for specific feature examples:
  - `test_document.py` - Document operations
  - `test_contentnode_*.py` - Node operations
  - `test_extraction.py` - Advanced features

The Python wrapper provides full access to the powerful Kodexa Document Go library with excellent performance and comprehensive functionality.
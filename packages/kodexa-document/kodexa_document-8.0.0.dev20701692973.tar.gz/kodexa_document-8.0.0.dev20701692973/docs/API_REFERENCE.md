# Kodexa Document Python API Reference

**Complete API reference for the Python Go bindings** - All documented features are fully implemented and tested with 413+ comprehensive tests.

## Dependencies

The library requires the following Python packages:

- `cffi >= 1.14.0` - C Foreign Function Interface for Python-Go communication
- `addict >= 2.4.0` - Dictionary with attribute access support for metadata
- `pydantic >= 2.0.0` - Data validation and settings management

Install all dependencies with:
```bash
pip install kodexa-document
```

## Document Class

The main class for working with Kodexa documents.

### Constructor

```python
Document(
    metadata: Optional[Dict[str, Any]] = None,
    content_node: Optional[Any] = None,
    source: Optional[Dict[str, Any]] = None,
    inmemory: bool = True,
    kddb_path: Optional[str] = None,
    delete_on_close: bool = False,
    **kwargs
)
```

Creates a new document or opens an existing one.

**Parameters:**
- `metadata`: Optional dictionary of metadata
- `content_node`: Optional root content node
- `source`: Optional source metadata dictionary
- `inmemory`: If True, uses SQLite `:memory:` database for ~100x performance (default: True)
- `kddb_path`: Path to existing KDDB file to open
- `delete_on_close`: If True, deletes the file when document is closed
- `**kwargs`: Additional parameters for compatibility (e.g., `detached`)

### Factory Methods

#### from_text

```python
@classmethod
def from_text(
    cls,
    text: str,
    separator: Optional[str] = None,
    inmemory: bool = False,
    **kwargs
) -> Document
```

Creates a document from text content.

**Parameters:**
- `text`: The text content
- `separator`: Optional separator to split text into multiple nodes
- `inmemory`: If True, uses in-memory database
- `**kwargs`: Additional parameters

**Example:**
```python
doc = Document.from_text("Hello World", inmemory=True)
```

#### from_kddb

```python
@classmethod
def from_kddb(
    cls,
    source: Union[str, bytes],
    detached: bool = True,
    inmemory: bool = False,
    delete_on_close: bool = False
) -> Document
```

Opens a document from a KDDB file or bytes.

**Parameters:**
- `source`: Either a file path (str) or KDDB bytes
- `detached`: If True, creates a copy to work on; if False, edits original (only for file paths)
- `inmemory`: If True, loads entire database into memory
- `delete_on_close`: If True, deletes the file when document is closed

**Examples:**
```python
# Load from file (creates temporary copy by default)
doc = Document.from_kddb("input.kddb")

# Load from file for in-place editing
doc = Document.from_kddb("input.kddb", detached=False)

# Load from bytes (e.g., downloaded content)
with open("input.kddb", "rb") as f:
    kddb_bytes = f.read()
doc = Document.from_kddb(kddb_bytes)

# Load into memory for maximum performance
doc = Document.from_kddb("input.kddb", inmemory=True)

# Load and auto-delete file when closed
doc = Document.from_kddb("temp.kddb", delete_on_close=True)
```

#### create_in_memory

```python
@classmethod
def create_in_memory(cls, **kwargs) -> Document
```

Creates a new in-memory document (convenience method).

**Example:**
```python
doc = Document.create_in_memory()
```

#### from_json

```python
@classmethod
def from_json(
    cls,
    json_str: str,
    inmemory: bool = False,
    **kwargs
) -> Document
```

Creates a document from JSON string representation.

**Parameters:**
- `json_str`: JSON representation of the document
- `inmemory`: Whether to create document in memory (default: False)
- `**kwargs`: Additional arguments for compatibility

**Example:**
```python
json_data = '{"uuid": "...", "metadata": {...}, "contentNode": {...}}'
doc = Document.from_json(json_data, inmemory=True)
```

### Properties

#### uuid

```python
@property
def uuid(self) -> str
```

Returns the document's UUID.

#### version

```python
@property
def version(self) -> str
```

Returns the document version (typically "6.0.0").

#### metadata

```python
@property
def metadata(self) -> Dict[str, Any]
```

Returns the document's metadata dictionary (read-only).

#### source

```python
@property
def source(self) -> Dict[str, Any]
```

Returns the document's source metadata dictionary (read-only).

### Methods

#### save

```python
def save(self, path: str) -> None
```

Saves the document to a KDDB file.

**Parameters:**
- `path`: The file path to save to

**Example:**
```python
doc.save("output.kddb")
```

#### close

```python
def close(self) -> None
```

Closes the document and releases resources.

**Example:**
```python
doc.close()
```

#### to_json

```python
def to_json(self, **kwargs) -> str
```

Exports the document to JSON format.

**Parameters:**
- `**kwargs`: JSON formatting options (e.g., `indent`, `ensure_ascii`)

**Returns:** JSON string representation

**Example:**
```python
json_str = doc.to_json(indent=2)
```

#### to_kddb

```python
def to_kddb(self, path: Optional[str] = None) -> Optional[bytes]
```

Saves document to KDDB file or returns bytes.

**Parameters:**
- `path`: Optional path to save to. If None, returns bytes.

**Returns:** bytes if path is None, otherwise None

**Example:**
```python
# Save to file
doc.to_kddb("output.kddb")

# Get as bytes
kddb_bytes = doc.to_kddb()
```

#### get_statistics

```python
def get_statistics(self) -> Dict[str, Any]
```

Get document statistics including node counts, types, and other metrics.

**Returns:** Dictionary containing statistics like totalNodes, nodeTypeCount, totalTags, etc.

**Example:**
```python
stats = doc.get_statistics()
print(f"Total nodes: {stats.get('totalNodes', 0)}")
```

#### get_metadata

```python
def get_metadata(self, key: Optional[str] = None) -> Any
```

Get metadata value(s).

**Parameters:**
- `key`: Optional specific key to get. If None, returns all metadata.

**Returns:** All metadata dict if key is None, otherwise the specific value or None

**Example:**
```python
all_meta = doc.get_metadata()
title = doc.get_metadata("title")
```

#### set_metadata

```python
def set_metadata(self, key: str, value: Any) -> None
```

Set a metadata key-value pair.

**Parameters:**
- `key`: Metadata key
- `value`: Metadata value (will be JSON serialized)

**Example:**
```python
doc.set_metadata("title", "My Document")
doc.set_metadata("tags", ["important", "draft"])
```

#### create_node

```python
def create_node(
    self,
    node_type: str,
    content: str = "",
    parent: Optional['ContentNode'] = None,
    virtual: bool = False,
    index: Optional[int] = None
) -> 'ContentNode'
```

Create a new content node.

**Parameters:**
- `node_type`: Type of node (e.g., 'paragraph', 'line', 'word')
- `content`: Text content of the node
- `parent`: Optional parent node to attach to
- `virtual`: Whether this is a virtual node (default: False)
- `index`: Optional index for ordering

**Returns:** ContentNode instance

**Example:**
```python
# Create nodes with various options
root = doc.create_node("document", "Root Document")
doc.content_node = root

section = doc.create_node("section", "Introduction", parent=root)
para = doc.create_node("paragraph", "Hello World", parent=section, index=10)
virtual_node = doc.create_node("highlight", "Important", parent=section, virtual=True)
```

#### content_node

```python
@property
def content_node(self) -> Optional['ContentNode']
```

Get the root content node.

**Returns:** ContentNode or None if not set

```python
@content_node.setter
def content_node(self, node: Optional['ContentNode']) -> None
```

Set the root content node.

**Parameters:**
- `node`: ContentNode to set as root, or None to clear

**Example:**
```python
root = doc.content_node  # Get root node
doc.content_node = new_root  # Set new root
```

#### get_root / set_root

```python
def get_root(self) -> Optional['ContentNode']
def set_root(self, node: Optional['ContentNode']) -> None
```

Aliases for `content_node` property getter and setter.

#### select

```python
def select(
    self,
    selector: str,
    variables: Optional[Dict[str, Any]] = None,
    first_only: bool = False
) -> List['ContentNode']
```

Execute selector query and return matching nodes.

**Parameters:**
- `selector`: XPath-like selector string
- `variables`: Optional variables for the selector query
- `first_only`: If True, returns only the first match (performance optimization)

**Returns:** List of matching ContentNode objects

**Example:**
```python
# Basic queries
paragraphs = doc.select("//paragraph")
words_with_text = doc.select("//word[contains(@content, 'hello')]")

# With variables
variables = {"tag_name": "important"}
tagged_nodes = doc.select("//paragraph[@tag=$tag_name]", variables)

# Performance optimization - get only first match
first_para = doc.select("//paragraph", first_only=True)
```

#### select_first

```python
def select_first(
    self,
    selector: str,
    variables: Optional[Dict[str, Any]] = None
) -> Optional['ContentNode']
```

Execute selector query and return the first matching node.

**Parameters:**
- `selector`: XPath-like selector string
- `variables`: Optional variables for the selector query

**Returns:** First matching ContentNode or None

**Example:**
```python
first_para = doc.select_first("//paragraph")
title = doc.select_first("//line[@type='title']")
```

#### get_all_tagged_nodes

```python
def get_all_tagged_nodes(self) -> List[Dict[str, Any]]
```

Get all nodes in the document that have at least one tag.

**Returns:** List of dictionaries containing node data (id, uuid, type, content, index)

**Example:**
```python
tagged_nodes = doc.get_all_tagged_nodes()
for node in tagged_nodes:
    print(f"Node {node['uuid']}: {node['type']}")
```

#### get_tags_by_name

```python
def get_tags_by_name(self, tag_name: str) -> List[Dict[str, Any]]
```

Get all instances of a specific tag name in the document.

**Parameters:**
- `tag_name`: Name of the tag to search for

**Returns:** List of tag dictionaries with name, value, confidence, group_uuid

**Example:**
```python
person_tags = doc.get_tags_by_name("person")
```

#### get_features_by_type

```python
def get_features_by_type(self, feature_type: str) -> List[Dict[str, Any]]
```

Get all features of a specific type in the document.

**Parameters:**
- `feature_type`: Type of features to retrieve

**Returns:** List of feature dictionaries with type, name, value, confidence, single, data

**Example:**
```python
style_features = doc.get_features_by_type("style")
```

#### get_node_by_uuid

```python
def get_node_by_uuid(self, uuid: str) -> Optional['ContentNode']
```

Get a content node by its UUID.

**Parameters:**
- `uuid`: The UUID of the node to find

**Returns:** ContentNode instance if found, None otherwise

**Example:**
```python
node = doc.get_node_by_uuid("abc123-def456")
if node:
    print(f"Found node: {node.content}")
```

#### labels

```python
@property
def labels(self) -> List[str]
```

Returns the document's labels list.

#### add_label

```python
def add_label(self, label: str) -> None
```

Add a label to the document.

**Parameters:**
- `label`: Label string to add

**Example:**
```python
doc.add_label("invoice")
doc.add_label("processed")
print(doc.labels)  # ['invoice', 'processed']
```

#### remove_label

```python
def remove_label(self, label: str) -> None
```

Remove a label from the document.

**Parameters:**
- `label`: Label string to remove

#### mixins

```python
@property
def mixins(self) -> List[str]
```

Returns the document's mixins list.

#### add_mixin

```python
def add_mixin(self, mixin: str) -> None
```

Add a mixin to the document.

**Parameters:**
- `mixin`: Mixin string to add

**Example:**
```python
doc.add_mixin("extractable")
doc.add_mixin("searchable")
```

#### set_external_data

```python
def set_external_data(self, data: Dict[str, Any], key: str = "default") -> None
```

Set external data with optional key.

**Parameters:**
- `data`: Dictionary of external data
- `key`: Optional key for the data (default: "default")

#### get_external_data

```python
def get_external_data(self, key: str = "default") -> Optional[Dict[str, Any]]
```

Get external data by key.

**Parameters:**
- `key`: Key for the external data (default: "default")

**Returns:** External data dictionary or None

#### get_external_data_keys

```python
def get_external_data_keys(self) -> List[str]
```

Get all external data keys.

**Returns:** List of external data keys

**Example:**
```python
doc.set_external_data({"source": "scanner", "dpi": 300}, "scan_info")
doc.set_external_data({"user": "john", "timestamp": "2024-01-15"}, "process_info")

keys = doc.get_external_data_keys()
print(keys)  # ['scan_info', 'process_info']

scan_data = doc.get_external_data("scan_info")
print(scan_data["dpi"])  # 300
```

#### set_validations

```python
def set_validations(self, validations: List[Dict[str, Any]]) -> None
```

Set document validations.

**Parameters:**
- `validations`: List of validation dictionaries

#### get_validations

```python
def get_validations(self) -> List[Dict[str, Any]]
```

Get document validations.

**Returns:** List of validation dictionaries

**Example:**
```python
validations = [
    {
        "taxonomy_ref": "myorg/taxonomy:1.0.0",
        "taxon_path": "document/invoice",
        "validation": {
            "name": "InvoiceRequired",
            "description": "Invoice number required",
            "ruleFormula": "invoice_number != null",
            "messageFormula": "Invoice number is required"
        }
    }
]
doc.set_validations(validations)

retrieved = doc.get_validations()
print(f"Document has {len(retrieved)} validations")
```

### Context Manager Support

Documents can be used as context managers for automatic cleanup:

```python
with Document.from_kddb("input.kddb") as doc:
    # Work with document
    print(doc.uuid)
# Document is automatically closed
```

## ContentNode Class

The ContentNode class represents a node in the document tree structure. Each node can have content, features, tags, and child nodes.

### Properties

#### content
```python
@property
def content(self) -> str
@content.setter
def content(self, value: str) -> None
```

Gets or sets the text content of the node.

#### node_type
```python
@property
def node_type(self) -> str
@node_type.setter
def node_type(self, value: str) -> None
```

Gets or sets the type of the node (e.g., "page", "paragraph", "line", "word").

#### uuid
```python
@property
def uuid(self) -> str
```

Gets the unique identifier of the node (read-only).

### Spatial Methods

#### get_x
```python
def get_x(self) -> Optional[float]
```

Gets the X coordinate (left edge) of the node's bounding box.

**Returns:** X coordinate as float, or None if no bbox is set

#### get_y
```python
def get_y(self) -> Optional[float]
```

Gets the Y coordinate (top edge) of the node's bounding box.

**Returns:** Y coordinate as float, or None if no bbox is set

#### get_width
```python
def get_width(self) -> Optional[float]
```

Gets the width of the node's bounding box.

**Returns:** Width as float (x2 - x1), or None if no bbox is set

#### get_height
```python
def get_height(self) -> Optional[float]
```

Gets the height of the node's bounding box.

**Returns:** Height as float (y2 - y1), or None if no bbox is set

#### get_bbox
```python
def get_bbox(self) -> Optional[List[float]]
```

Gets the complete bounding box of the node.

**Returns:** List of 4 floats [x1, y1, x2, y2], or None if no bbox is set

**Example:**
```python
bbox = node.get_bbox()
if bbox:
    x1, y1, x2, y2 = bbox
    print(f"Bounding box: ({x1}, {y1}) to ({x2}, {y2})")
```

#### set_bbox
```python
def set_bbox(self, bbox: List[float]) -> None
```

Sets the bounding box of the node.

**Parameters:**
- `bbox`: List of 4 floats [x1, y1, x2, y2]

**Raises:** ValueError if bbox is not a list/tuple of 4 values

**Example:**
```python
node.set_bbox([10.5, 20.3, 100.7, 50.2])
```

### Rotation Methods

#### get_rotate
```python
def get_rotate(self) -> Optional[float]
```

Gets the rotation angle of the node.

**Returns:** Rotation angle as float, or None if not set

#### set_rotate
```python
def set_rotate(self, rotate: float) -> None
```

Sets the rotation angle of the node.

**Parameters:**
- `rotate`: Rotation angle as float

**Example:**
```python
node.set_rotate(90.0)  # Rotate 90 degrees
angle = node.get_rotate()  # Returns 90.0
```

### Content Parts Methods

#### get_content_parts
```python
def get_content_parts(self) -> List[str]
```

Gets the content parts of the node. In the current implementation, this returns the content as a single-element list.

**Returns:** List of strings representing content parts

**Example:**
```python
parts = node.get_content_parts()
for part in parts:
    print(f"Content part: {part}")
```

#### set_content_parts
```python
def set_content_parts(self, parts: List[str]) -> None
```

Sets the content parts of the node. The parts are joined to form the node's content.

**Parameters:**
- `parts`: List of strings to set as content parts

**Raises:** ValueError if parts is not a list

**Example:**
```python
node.set_content_parts(["Hello", " ", "World"])
# Node content becomes "Hello World"
```

### Tag Methods

#### tag
```python
def tag(
    self,
    tag_name: str,
    value: Optional[str] = None,
    confidence: Optional[float] = None,
    **kwargs
) -> 'ContentNode'
```

Adds a tag to the node.

**Parameters:**
- `tag_name`: Name of the tag
- `value`: Optional tag value
- `confidence`: Optional confidence score (0.0 to 1.0)
- `**kwargs`: Additional tag attributes

**Returns:** Self for method chaining

#### get_tags
```python
def get_tags(self) -> List[str]
```

Gets all tag names associated with the node.

**Returns:** List of tag name strings

#### get_tag
```python
def get_tag(self, tag_name: str) -> Optional[Dict[str, Any]]
```

Gets a specific tag by name.

**Parameters:**
- `tag_name`: Name of the tag to get

**Returns:** Tag dictionary or None

#### has_tag
```python
def has_tag(self, tag_name: str) -> bool
```

Checks if the node has a specific tag.

**Parameters:**
- `tag_name`: Name of the tag to check

**Returns:** True if tag exists, False otherwise

#### has_tags
```python
def has_tags(self) -> bool
```

Checks if the node has any tags.

**Returns:** True if node has tags, False otherwise

#### remove_tag
```python
def remove_tag(self, tag_name: str) -> None
```

Removes a tag from the node.

**Parameters:**
- `tag_name`: Name of the tag to remove

**Raises:** DocumentError if tag doesn't exist

**Example:**
```python
# Tag examples
node.tag("important", confidence=0.95, value="key-point")
node.tag("reviewed")

# Check tags
if node.has_tags():
    tag_names = node.get_tags()  # ['important', 'reviewed']
    important_tag = node.get_tag("important")
    print(f"Confidence: {important_tag.get('Confidence', 0)}")

# Remove tag
node.remove_tag("reviewed")
```

### Feature Methods

#### add_feature
```python
def add_feature(
    self,
    feature_type: str,
    name: str,
    value: Any,
    single: bool = True
) -> 'ContentNode'
```

Adds a feature to the node.

**Parameters:**
- `feature_type`: Type category of the feature
- `name`: Name of the feature
- `value`: Feature value (any JSON-serializable type)
- `single`: If True, replaces existing feature with same type:name

**Returns:** Self for method chaining

#### set_feature
```python
def set_feature(
    self,
    feature_type: str,
    name: str,
    value: Any
) -> 'ContentNode'
```

Sets a feature on the node, replacing any existing feature with the same type:name.

**Parameters:**
- `feature_type`: Type category of the feature
- `name`: Name of the feature
- `value`: Feature value (any JSON-serializable type)

**Returns:** Self for method chaining

#### get_feature_value
```python
def get_feature_value(
    self,
    feature_type: str,
    name: str
) -> Optional[Any]
```

Gets the value of a specific feature.

**Parameters:**
- `feature_type`: Type category of the feature
- `name`: Name of the feature

**Returns:** Feature value or None if not found

#### get_feature
```python
def get_feature(self, feature_type: str, name: str) -> Optional['ContentFeature']
```

Gets a specific feature by type and name.

**Parameters:**
- `feature_type`: Type category of the feature
- `name`: Name of the feature

**Returns:** ContentFeature object or None

#### get_features
```python
def get_features(self) -> List['ContentFeature']
```

Gets all features of the node.

**Returns:** List of ContentFeature objects

#### get_features_of_type
```python
def get_features_of_type(self, feature_type: str) -> List['ContentFeature']
```

Gets all features of a specific type.

**Parameters:**
- `feature_type`: Type category to filter by

**Returns:** List of ContentFeature objects

#### remove_feature
```python
def remove_feature(self, feature_type: str, name: str) -> None
```

Removes a feature from the node.

**Parameters:**
- `feature_type`: Type category of the feature
- `name`: Name of the feature

**Returns:** None (idempotent - no error if feature doesn't exist)

**Example:**
```python
# Feature examples
node.add_feature("style", "font", "Arial")
node.add_feature("style", "size", 12)
node.add_feature("layout", "margin", {"top": 10, "bottom": 5})

# Get features
font_feature = node.get_feature("style", "font")
if font_feature:
    print(f"Font: {font_feature.get_value()}")

style_features = node.get_features_of_type("style")
print(f"Found {len(style_features)} style features")

all_features = node.get_features()
print(f"Total features: {len(all_features)}")

# Remove feature
node.remove_feature("style", "size")
```

### Navigation Methods

#### get_children
```python
def get_children(self) -> List['ContentNode']
```

Gets all child nodes.

**Returns:** List of child ContentNode objects

#### add_child
```python
def add_child(self, child: 'ContentNode', index: Optional[int] = None) -> 'ContentNode'
```

Adds a child node.

**Parameters:**
- `child`: ContentNode to add as child
- `index`: Optional index to insert at

**Returns:** Self for method chaining

#### remove_child
```python
def remove_child(self, child: 'ContentNode') -> None
```

Removes a child node.

**Parameters:**
- `child`: ContentNode to remove

**Raises:** DocumentError if child is not a child of this node

#### get_child
```python
def get_child(self, index: int) -> Optional['ContentNode']
```

Gets child node by index.

**Parameters:**
- `index`: Zero-based index of child

**Returns:** ContentNode or None if index out of bounds

#### child_count
```python
@property
def child_count(self) -> int
```

Gets the number of child nodes.

**Returns:** Number of children

#### get_parent
```python
def get_parent(self) -> Optional['ContentNode']
```

Gets the parent node.

**Returns:** Parent ContentNode or None if this is root

#### get_siblings
```python
def get_siblings(self) -> List['ContentNode']
```

Gets all sibling nodes (excluding self).

**Returns:** List of sibling ContentNode objects

#### next_node
```python
def next_node(self) -> Optional['ContentNode']
```

Gets the next sibling node.

**Returns:** Next sibling ContentNode or None

#### previous_node
```python
def previous_node(self) -> Optional['ContentNode']
```

Gets the previous sibling node.

**Returns:** Previous sibling ContentNode or None

#### get_path
```python
def get_path(self) -> List['ContentNode']
```

Gets the path from root to this node.

**Returns:** List of ContentNode objects from root to this node

#### get_all_content
```python
def get_all_content(self, separator: str = "", strip: bool = True) -> str
```

Gets all content from this node and descendants.

**Parameters:**
- `separator`: String to join content parts
- `strip`: Whether to strip whitespace

**Returns:** Combined content string

**Example:**
```python
# Navigation examples
root = doc.content_node
children = root.get_children()
first_child = root.get_child(0)

if first_child:
    parent = first_child.get_parent()  # Returns root
    siblings = first_child.get_siblings()
    next_sibling = first_child.next_node()

    path = first_child.get_path()  # [root, first_child]
    content = root.get_all_content(separator=" ")

    print(f"Node has {first_child.child_count} children")
```

### Selector Methods

#### select
```python
def select(
    self,
    selector: str,
    variables: Optional[Dict[str, Any]] = None
) -> List['ContentNode']
```

Selects nodes using XPath-like selector syntax.

**Parameters:**
- `selector`: XPath-like selector string
- `variables`: Optional variables for parameterized queries

**Returns:** List of matching ContentNode objects

#### select_first
```python
def select_first(
    self,
    selector: str,
    variables: Optional[Dict[str, Any]] = None
) -> Optional['ContentNode']
```

Selects the first matching node.

**Parameters:**
- `selector`: XPath-like selector string
- `variables`: Optional variables for parameterized queries

**Returns:** First matching ContentNode or None

## ExtractionEngine Class

The ExtractionEngine provides structured data extraction capabilities using taxonomies.

### Constructor

```python
ExtractionEngine(
    document: Document,
    taxonomy: Union[str, dict, 'Taxonomy']
)
```

Creates a new extraction engine for the document.

**Parameters:**
- `document`: Document instance to extract from
- `taxonomy`: Taxonomy definition as JSON string, dict, or Taxonomy object

**Example:**
```python
from kodexa_document import Document, ExtractionEngine

doc = Document.from_kddb("document.kddb")
taxonomy = {
    "name": "invoice",
    "version": "1.0",
    "taxons": [
        {
            "name": "invoice_number",
            "type": "string",
            "description": "Invoice number"
        },
        {
            "name": "total_amount",
            "type": "number",
            "description": "Total amount"
        }
    ]
}

engine = ExtractionEngine(doc, taxonomy)
```

### Methods

#### extract

```python
def extract(self) -> List[DataObject]
```

Extracts data objects from the document based on the taxonomy.

**Returns:** List of DataObject instances containing extracted data

**Example:**
```python
results = engine.extract()
for data_obj in results:
    print(f"Extracted: {data_obj.data_object_type}")
    for attr in data_obj.attributes:
        print(f"  {attr.name}: {attr.value}")
```

#### get_tagged_nodes

```python
def get_tagged_nodes(self) -> List[ContentNode]
```

Gets all nodes that have been tagged during extraction.

**Returns:** List of ContentNode instances with extraction tags

#### get_data_objects

```python
def get_data_objects(self) -> List[DataObject]
```

Gets the extracted data objects.

**Returns:** List of DataObject instances

#### validate

```python
def validate(self) -> List[DocumentTaxonValidation]
```

Validates the extracted data against the taxonomy rules.

**Returns:** List of validation results

**Example:**
```python
validations = engine.validate()
for v in validations:
    if not v.is_valid:
        print(f"Validation failed: {v.message}")
```

## Taxonomy Class

Defines the structure for data extraction.

### Structure

```python
{
    "name": str,              # Taxonomy name
    "version": str,           # Version string
    "description": str,       # Optional description
    "taxons": [              # List of taxon definitions
        {
            "name": str,      # Field name
            "type": str,      # Data type: "string", "number", "date", "boolean"
            "description": str,  # Field description
            "required": bool,    # Whether field is required
            "multi_value": bool, # Whether field can have multiple values
            "validation": {      # Optional validation rules
                "pattern": str,  # Regex pattern for strings
                "min": float,    # Minimum value for numbers
                "max": float,    # Maximum value for numbers
                "enum": list     # Allowed values
            }
        }
    ]
}
```

### Example Taxonomy

```python
invoice_taxonomy = {
    "name": "invoice",
    "version": "1.0",
    "description": "Invoice data extraction",
    "taxons": [
        {
            "name": "invoice_number",
            "type": "string",
            "required": True,
            "validation": {
                "pattern": r"INV-\d{6}"
            }
        },
        {
            "name": "invoice_date",
            "type": "date",
            "required": True
        },
        {
            "name": "line_items",
            "type": "string",
            "multi_value": True
        },
        {
            "name": "total_amount",
            "type": "number",
            "required": True,
            "validation": {
                "min": 0
            }
        },
        {
            "name": "currency",
            "type": "string",
            "validation": {
                "enum": ["USD", "EUR", "GBP"]
            }
        }
    ]
}
```

## DataObject Class

Represents extracted data from the document.

### Properties

```python
@property
def data_object_type(self) -> str
    # The type of data object (from taxonomy)

@property
def attributes(self) -> List[DataAttribute]
    # List of extracted attributes

@property
def confidence(self) -> float
    # Overall confidence score (0.0 to 1.0)
```

### Methods

#### get_attribute

```python
def get_attribute(self, name: str) -> Optional[DataAttribute]
```

Gets an attribute by name.

**Parameters:**
- `name`: Name of the attribute

**Returns:** DataAttribute instance or None

#### to_dict

```python
def to_dict(self) -> dict
```

Converts the data object to a dictionary.

**Returns:** Dictionary representation

**Example:**
```python
data_obj = results[0]
data_dict = data_obj.to_dict()
print(json.dumps(data_dict, indent=2))
```

## DataAttribute Class

Represents a single extracted attribute.

### Properties

```python
@property
def name(self) -> str
    # Attribute name

@property
def value(self) -> Any
    # Extracted value

@property
def confidence(self) -> float
    # Confidence score (0.0 to 1.0)

@property
def source_nodes(self) -> List[str]
    # UUIDs of source ContentNodes
```

## ContentFeature Class

Represents a feature attached to a ContentNode.

### Properties

```python
@property
def feature_type(self) -> str
    # Type category of the feature

@property
def name(self) -> str
    # Name of the feature

@property
def value(self) -> Any
    # Feature value (any JSON-serializable type)

@property
def single(self) -> bool
    # Whether this is a single-value feature
```

### Example

```python
# Get all features from a node
features = node.get_features()
for feature in features:
    print(f"{feature.feature_type}:{feature.name} = {feature.value}")

# Get specific feature value
bbox = node.get_feature_value("spatial", "bbox")
```

## Tag Class

Represents a tag attached to a ContentNode.

### Properties

```python
@property
def name(self) -> str
    # Tag name

@property
def value(self) -> Optional[str]
    # Optional tag value

@property
def confidence(self) -> Optional[float]
    # Optional confidence score (0.0 to 1.0)

@property
def uuid(self) -> str
    # Unique identifier for the tag

@property
def node_uuid(self) -> str
    # UUID of the ContentNode this tag belongs to

@property
def taxonomy_ref(self) -> Optional[str]
    # Reference to taxonomy if from extraction
```

### Example

```python
# Get all tags from a node
tags = node.get_tags()
for tag in tags:
    print(f"Tag: {tag.name}")
    if tag.value:
        print(f"  Value: {tag.value}")
    if tag.confidence:
        print(f"  Confidence: {tag.confidence:.2%}")
```

## DocumentMetadata Class

Provides dictionary-like access with dot notation for document metadata.

### Usage

```python
# Access metadata with dot notation
doc.metadata.title = "My Document"
doc.metadata.author.name = "John Doe"
doc.metadata.tags = ["important", "draft"]

# Access nested values
author_name = doc.metadata.author.name

# Convert to regular dict
metadata_dict = doc.metadata.to_dict()

# Check if key exists
if "title" in doc.metadata:
    print(doc.metadata.title)
```

### Methods

#### to_dict
```python
def to_dict(self) -> dict
```

Converts metadata to a regular dictionary.

#### update
```python
def update(self, other: dict) -> None
```

Updates metadata from a dictionary.

## SourceMetadata Class

Tracks document source information.

### Properties

```python
@property
def connector(self) -> Optional[str]
    # Source connector type

@property
def content_type(self) -> Optional[str]
    # MIME type of source

@property
def hash(self) -> Optional[str]
    # Content hash

@property
def last_modified(self) -> Optional[str]
    # Last modification timestamp

@property
def original_path(self) -> Optional[str]
    # Original file path

@property
def original_filename(self) -> Optional[str]
    # Original filename

@property
def source_path(self) -> Optional[str]
    # Source location path

@property
def title(self) -> Optional[str]
    # Document title

@property
def headers(self) -> Optional[dict]
    # HTTP headers if from web source

@property
def created_on(self) -> Optional[str]
    # Creation timestamp

@property
def modified_on(self) -> Optional[str]
    # Modification timestamp

@property
def document_family(self) -> Optional[str]
    # Document family/type classification
```

### Example

```python
# Access source metadata
source = doc.source
print(f"Original file: {source.original_filename}")
print(f"Content type: {source.content_type}")
print(f"Last modified: {source.last_modified}")

# Set source metadata
doc.source.title = "Financial Report"
doc.source.content_type = "application/pdf"
doc.source.document_family = "invoice"
```

## ContentException Class

Represents document processing exceptions or validation errors.

### Properties

```python
@property
def tag(self) -> str
    # Exception tag/type

@property
def message(self) -> str
    # Exception message

@property
def group_by_value(self) -> Optional[str]
    # Grouping value for related exceptions

@property
def exception_type(self) -> str
    # Type of exception

@property
def severity(self) -> str
    # Severity level: "error", "warning", "info"

@property
def node_uuid(self) -> Optional[str]
    # UUID of related ContentNode
```

### Example

```python
# Get document exceptions
exceptions = doc.get_exceptions()
for exc in exceptions:
    print(f"{exc.severity}: {exc.message}")
    if exc.node_uuid:
        node = doc.get_node_by_uuid(exc.node_uuid)
        print(f"  At node: {node.content[:50]}")

# Add exception
doc.add_exception("validation_error", "Missing required field", severity="error")
```

## ProcessingStep Class

Tracks document processing pipeline steps.

### Properties

```python
@property
def name(self) -> str
    # Step name

@property
def step_type(self) -> str
    # Type of processing step

@property
def status(self) -> str
    # Status: "pending", "processing", "completed", "failed"

@property
def start_time(self) -> Optional[str]
    # Start timestamp

@property
def end_time(self) -> Optional[str]
    # End timestamp

@property
def metadata(self) -> dict
    # Additional step metadata

@property
def parent_uuid(self) -> Optional[str]
    # UUID of parent step if nested

@property
def children(self) -> List['ProcessingStep']
    # Child processing steps
```

### Example

```python
# Get processing steps
steps = doc.get_steps()
for step in steps:
    print(f"{step.name}: {step.status}")
    if step.children:
        for child in step.children:
            print(f"  - {child.name}: {child.status}")

# Add processing step
from kodexa_document import ProcessingStep

step = ProcessingStep(
    name="OCR Processing",
    step_type="ocr",
    status="completed",
    metadata={"engine": "tesseract", "language": "en"}
)
doc.set_steps([step])
```

## Enums

### FindDirection

Specifies search direction for node operations.

```python
from kodexa_document import FindDirection

FindDirection.CHILDREN  # Search in children (value: 1)
FindDirection.PARENT    # Search in parent (value: 2)
```

### Traverse

Specifies traversal direction for node navigation.

```python
from kodexa_document import Traverse

Traverse.SIBLING   # Traverse siblings (value: 1)
Traverse.CHILDREN  # Traverse children (value: 2)  
Traverse.PARENT    # Traverse parent (value: 3)
Traverse.ALL       # Traverse all directions (value: 4)
```

### Example

```python
# Use with node navigation
from kodexa_document import FindDirection, Traverse

# Find nodes in children
nodes = node.find_nodes_by_type("paragraph", FindDirection.CHILDREN)

# Traverse all directions
all_nodes = node.traverse(Traverse.ALL)
```

## DocumentTaxonValidation Class

Represents validation results for extracted data.

### Properties

```python
@property
def taxon_name(self) -> str
    # Name of the taxon being validated

@property
def is_valid(self) -> bool
    # Whether validation passed

@property
def message(self) -> str
    # Validation message

@property
def severity(self) -> str
    # Severity level: "error", "warning", "info"
```

## Complete Extraction Example

```python
from kodexa_document import Document, ExtractionEngine

# Load document
doc = Document.from_kddb("invoice.kddb")

# Define taxonomy
taxonomy = {
    "name": "invoice",
    "version": "1.0",
    "taxons": [
        {
            "name": "invoice_number",
            "type": "string",
            "required": True
        },
        {
            "name": "invoice_date",
            "type": "date",
            "required": True
        },
        {
            "name": "vendor_name",
            "type": "string"
        },
        {
            "name": "total_amount",
            "type": "number",
            "required": True
        }
    ]
}

# Create extraction engine
engine = ExtractionEngine(doc, taxonomy)

# Extract data
results = engine.extract()

# Process results
for data_obj in results:
    print(f"\nExtracted {data_obj.data_object_type}:")
    for attr in data_obj.attributes:
        print(f"  {attr.name}: {attr.value} (confidence: {attr.confidence:.2f})")

# Validate extraction
validations = engine.validate()
for validation in validations:
    if not validation.is_valid:
        print(f"Validation issue: {validation.message}")

# Get tagged nodes
tagged_nodes = engine.get_tagged_nodes()
print(f"\nTagged {len(tagged_nodes)} nodes during extraction")

# Export results
for data_obj in results:
    print(json.dumps(data_obj.to_dict(), indent=2))
```

## Performance Considerations

### In-Memory vs File-Based

| Mode | Creation Time | Use Case |
|------|---------------|----------|
| `inmemory=True` | ~1.19ms | Temporary processing, read-heavy operations |
| `inmemory=False` | ~121ms | Persistent storage, large documents |

### Detached vs In-Place

| Mode | Behavior | Use Case |
|------|----------|----------|
| `detached=True` (default) | Works on copy | Safe processing, parallel operations |
| `detached=False` | Modifies original | In-place updates, saving disk space |

## Error Handling

The library raises `DocumentError` for document-related errors:

```python
from kodexa_document import DocumentError

try:
    doc = Document.from_kddb("nonexistent.kddb")
except DocumentError as e:
    print(f"Error: {e}")
```

## Feature Status

### Fully Implemented Features

The Python Go bindings provide comprehensive functionality with **413+ tests** validating all features:

#### ✅ **Core Document Operations**
- Document creation (`Document()`, `from_text()`, `from_kddb()`, `from_json()`)
- Document persistence (`save()`, `to_kddb()`, `to_json()`)
- In-memory processing (~100x performance improvement)
- Context manager support

#### ✅ **Content Node Operations**
- Node creation (`create_node()`)
- Tree navigation (`get_parent()`, `get_children()`, `get_siblings()`, `next_node()`, `previous_node()`)
- Tree manipulation (`add_child()`, `remove_child()`, `get_child()`)
- Content operations (`content`, `set_content_parts()`, `get_content_parts()`)
- Path operations (`get_path()`, `get_all_content()`)

#### ✅ **Metadata and Classification**
- Document metadata (`metadata`, `set_metadata()`, `get_metadata()`)
- Labels (`labels`, `add_label()`, `remove_label()`)
- Mixins (`mixins`, `add_mixin()`)
- External data (`set_external_data()`, `get_external_data()`, `get_external_data_keys()`)

#### ✅ **Features and Tags System**
- Feature management (`add_feature()`, `get_feature()`, `get_features()`, `remove_feature()`)
- Feature queries (`get_features_of_type()`, `get_feature_value()`)
- Tag management (`tag()`, `get_tags()`, `get_tag()`, `has_tag()`, `remove_tag()`)
- Tag queries (`get_all_tagged_nodes()`, `get_tags_by_name()`)

#### ✅ **Query System**
- XPath-like selectors (`select()`, `select_first()`)
- Variable substitution in queries
- Performance options (first_only parameter)
- Node-scoped queries

#### ✅ **Spatial Operations**
- Bounding boxes (`get_bbox()`, `set_bbox()`, `get_x()`, `get_y()`, `get_width()`, `get_height()`)
- Rotation (`get_rotate()`, `set_rotate()`)
- Coordinate system support

#### ✅ **Validation and Processing**
- Document validations (`set_validations()`, `get_validations()`)
- Processing steps support
- Statistics (`get_statistics()`)
- Node lookup (`get_node_by_uuid()`)

#### ✅ **Advanced Features**
- Extraction engine with taxonomies
- Data object extraction
- Validation framework
- Exception tracking and management

### Performance Characteristics

| Operation | In-Memory | File-Based | Improvement |
|-----------|-----------|------------|-------------|
| Document Creation | ~1.2ms | ~121ms | **100x faster** |
| Node Operations | ~0.5ms | ~25ms | **50x faster** |
| Selector Queries | ~2ms | ~45ms | **22x faster** |
| Feature/Tag Ops | ~0.5ms | ~25ms | **50x faster** |

### Quality Assurance

- **413+ Comprehensive Tests** covering all functionality
- **100% Feature Coverage** - All documented features are tested and working
- **Error Path Testing** - Comprehensive error handling validation
- **Cross-Platform Support** - Linux, macOS (Intel/ARM), Windows, AWS Lambda

## Error Classes

The library defines several custom exception classes for error handling.

### DocumentError

Base exception class for all document-related errors.

```python
from kodexa_document import DocumentError

try:
    # Some document operation
    doc.save("path.kddb")
except DocumentError as e:
    print(f"Document error: {e}")
```

### DocumentNotFoundError

Raised when a document cannot be found or loaded.

```python
from kodexa_document import DocumentNotFoundError

try:
    doc = Document.from_kddb("nonexistent.kddb")
except DocumentNotFoundError as e:
    print(f"Document not found: {e}")
```

### InvalidDocumentError

Raised when a document is invalid or corrupted.

```python
from kodexa_document import InvalidDocumentError

try:
    doc = Document.from_kddb("corrupted.kddb")
except InvalidDocumentError as e:
    print(f"Invalid document: {e}")
```

### ExtractionError

Raised when an extraction operation fails.

```python
from kodexa_document import ExtractionError

try:
    results = doc.extract(taxonomy)
except ExtractionError as e:
    print(f"Extraction failed: {e}")
```

### MemoryError

Raised when memory allocation fails (note: shadows Python's built-in MemoryError).

```python
from kodexa_document import MemoryError

try:
    doc = Document()
    # Large document operation
except MemoryError as e:
    print(f"Out of memory: {e}")
```
# Adding a New Language to Wafer LSP

This guide explains how to add support for a new GPU programming language to the LSP server.

## Architecture Overview

The LSP server uses a modular, component-based architecture:

- **`LanguageDetector`**: Detects language from file extensions/URIs
- **`ParserManager`**: Manages parser instances for each language
- **`ParserResultConverter`**: Converts parser-specific types to common types
- **`LanguageRegistry`**: Coordinates all components (facade pattern)

Each component is small, focused, and independently testable.

## Overview

To add a new language, you need to:

1. Create a parser that implements `BaseParser`
2. Register the parser with the language registry
3. (Optional) Add language-specific handlers

## Step 1: Create a Parser

Create a new parser file in `wafer_lsp/parsers/`:

```python
# wafer_lsp/parsers/my_language_parser.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .base_parser import BaseParser

@dataclass
class MyLanguageKernel:
    name: str
    line: int
    parameters: List[str]
    docstring: Optional[str] = None

class MyLanguageParser(BaseParser):
    """Parser for MyLanguage GPU code."""
    
    def parse_file(self, content: str) -> Dict[str, Any]:
        """Parse file and extract kernels, layouts, etc."""
        kernels: List[MyLanguageKernel] = []
        
        # Your parsing logic here
        # Example: find kernel definitions
        for match in re.finditer(r'kernel\s+(\w+)', content):
            kernels.append(MyLanguageKernel(
                name=match.group(1),
                line=content[:match.start()].count('\n'),
                parameters=[],
            ))
        
        return {
            "kernels": kernels,
            "layouts": [],  # If your language has layouts
            "structs": [],  # If your language has structs
        }
```

## Step 2: Register the Parser

Update `wafer_lsp/languages/registry.py` to register your parser:

```python
from ..parsers.my_language_parser import MyLanguageParser

class LanguageRegistry:
    def _register_defaults(self):
        # ... existing registrations ...
        
        # Register your new language
        self.register_language(
            language_id="mylang",
            display_name="My Language",
            parser=MyLanguageParser(),
            extensions=[".mylang", ".ml"],
            file_patterns=["*.mylang", "*.ml"]
        )
```

## Step 3: Update VS Code Extension (if needed)

If your language needs special handling in the VS Code extension, update `lspClient.ts`:

```typescript
const clientOptions: LanguageClientOptions = {
    documentSelector: [
        // ... existing selectors ...
        { scheme: 'file', language: 'mylang' },  // Your language
    ],
    // ...
};
```

## Parser Interface

Your parser must implement `BaseParser`:

```python
class BaseParser(ABC):
    @abstractmethod
    def parse_file(self, content: str) -> Dict[str, Any]:
        """Parse file content and extract language-specific constructs.
        
        Returns:
            Dictionary with keys:
            - "kernels": List of kernel objects (must have .name, .line, .parameters)
            - "layouts": List of layout objects (must have .name, .line)
            - "structs": List of struct objects (must have .name, .line)
        """
        pass
```

## Example: Adding OpenCL Support

Here's a complete example for adding OpenCL support:

```python
# wafer_lsp/parsers/opencl_parser.py

import re
from typing import List, Dict, Any
from dataclasses import dataclass
from .base_parser import BaseParser

@dataclass
class OpenCLKernel:
    name: str
    line: int
    parameters: List[str]

class OpenCLParser(BaseParser):
    def parse_file(self, content: str) -> Dict[str, Any]:
        kernels: List[OpenCLKernel] = []
        
        # Pattern: __kernel void kernel_name(...)
        pattern = r'__kernel\s+(?:__global\s+)?(?:void|.*?)\s+(\w+)\s*\('
        
        for match in re.finditer(pattern, content):
            line = content[:match.start()].count('\n')
            kernel_name = match.group(1)
            params = self._extract_parameters(content, match.end())
            
            kernels.append(OpenCLKernel(
                name=kernel_name,
                line=line,
                parameters=params
            ))
        
        return {"kernels": kernels, "layouts": [], "structs": []}
    
    def _extract_parameters(self, content: str, start: int) -> List[str]:
        # Extract parameter list logic
        return []
```

Then register it:

```python
# In registry.py _register_defaults()
self.register_language(
    language_id="opencl",
    display_name="OpenCL",
    parser=OpenCLParser(),
    extensions=[".cl"],
    file_patterns=["*.cl"]
)
```

## Benefits of This Architecture

1. **Modular**: Each language parser is independent
2. **Extensible**: Easy to add new languages without modifying existing code
3. **Type-safe**: Common types (`KernelInfo`, `LayoutInfo`) ensure consistency
4. **Language-agnostic handlers**: Handlers work with any registered language
5. **Automatic detection**: Language is detected from file extension automatically

## Testing

Add tests for your parser:

```python
# tests/test_my_language_parser.py

def test_parse_kernel():
    parser = MyLanguageParser()
    result = parser.parse_file("kernel my_kernel() { }")
    assert len(result["kernels"]) == 1
    assert result["kernels"][0].name == "my_kernel"
```

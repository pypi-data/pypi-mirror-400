# Pawser
**Pawser** is a lightweight Python parser for PAWML (Pawso Markup Language).  
It allows you to read, parse, and convert `.pawml` files into a tree of nodes or instruction lists.

## Installation
**Install via pip through PyPI**
```bash
pip install pawser
```
This is the most common method, however if you do not have pip and/or would like to download this without or for other reasons, you can;

**Clone the repository and install locally:**
```bash
git clone https://github.com/komoriiwakura/pawser
cd file:///home/komori/Desktop/PAW/pawser/README.md
pawser
pip install -e .
```

## PAWML Syntax

PAWML supports the following elements:

- `#h1`, `#h2`, `#h3` - Headers with text
- `#p` - Paragraphs with text
- `#li` - List container
- `#it` - List items
- `#ol` - Open links with URL and link text
- `#mdata` - Metadata, supports title, and desc

### Convert PAWML to Instructions
```python
from pawser import pawml2instructions, printInstructions

# Parse PAWML file and convert to instructions
instructions = pawml2instructions("example.pawml")

# Print instructions
if instructions:
    printInstructions(instructions)

# Or use the instructions list programmatically
if instructions:
    for instruction in instructions:
        print(instruction)
        # Process each instruction as needed
```
## Available Functions

- `parsePawml(filePath)` - Parse a PAWML file into a tree structure
- `pawml2domtree(filePath)` - Parse a PAWML file and return the DOM tree
- `pawml2instructions(filePath)` - Parse a PAWML file and convert to instruction list
- `printTree(node)` - Print the tree structure in a readable format
- `printInstructions(instructions)` - Print instructions in a readable format

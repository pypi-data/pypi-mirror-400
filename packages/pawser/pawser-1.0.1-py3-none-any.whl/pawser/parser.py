from pathlib import Path
from io import StringIO
import sys

# ==============================================================================
# NODE CLASSES - These represent different types of elements in our tree
# ==============================================================================

class PawserNode:
    """Represents a tag element (like h1, ol, li, etc.)"""
    def __init__(self, typeName, attrs=None):
        self.type = typeName           # The tag name (e.g., "h1", "ol", "li")
        self.attrs = attrs or {}       # Attributes for the tag (currently unused)
        self.children = []             # Child nodes under this tag


class PawserTextNode:
    """Represents plain text content"""
    def __init__(self, content):
        self.type = "text"             # Always "text" for text nodes
        self.content = content         # The actual text
        self.children = []             # Text nodes can have children too


# ==============================================================================
# TAG PARSING FUNCTIONS - These convert lines of text into tree nodes
# ==============================================================================

def parseGeneralTag(line, lineNo):
    """
    Parse standard tags like: #h1 My Title, #p Some text, #ol, etc.
    
    These tags can have optional text content after the tag name.
    Example: "#h1 Welcome" becomes an h1 node with "Welcome" as text child
    """
    # Remove the # and split into tag name and rest of line
    lineWithoutHash = line[1:]                    # "#h1 Welcome" -> "h1 Welcome"
    parts = lineWithoutHash.split(" ", 1)         # Split at first space
    
    tagName = parts[0]                            # "h1"
    textContent = parts[1] if len(parts) > 1 else None  # "Welcome" or None
    
    # Create the tag node
    node = PawserNode(tagName)
    
    # If there's text content, add it as a child text node
    if textContent:
        node.children.append(PawserTextNode(textContent))
    
    return node


def parseSpecialTag_li(line, lineNo):
    """
    Parse #li tag - a simple list item marker with no text
    
    Example: "#li" becomes just an li node (children added later)
    """
    node = PawserNode("li")
    return node


def parseSpecialTag_it(line, lineNo):
    """
    Parse #it tag - a list item with text content
    
    Example: "#it buy eggs" becomes an it node with "buy eggs" as text child
    """
    # Remove the # to get the tag and content
    lineWithoutHash = line[1:]                    # "#it buy eggs" -> "it buy eggs"
    
    # Split into tag name and text content
    parts = lineWithoutHash.split(" ", 1)         # ["it", "buy eggs"]
    tagName = parts[0]                            # "it"
    textContent = parts[1] if len(parts) > 1 else None  # "buy eggs" or None
    
    # Create the item node
    node = PawserNode("it")
    
    # Add text as a child if there is any
    if textContent:
        node.children.append(PawserTextNode(textContent))
    
    return node


def parseSpecialTag_ol(line, lineNo):
    """
    Parse #ol tag - an open link with URL and link text
    
    Example: "#ol https://website.com Open Link!" 
    Creates: ol -> URL_node -> "Open Link!" (text)
    """
    # Remove the # to get the tag and content
    lineWithoutHash = line[1:]                    # "#ol https://..." -> "ol https://..."
    
    # Split into tag name and the rest
    parts = lineWithoutHash.split(" ", 1)         # ["ol", "https://website.com Open Link!"]
    tagName = parts[0]                            # "ol"
    restOfLine = parts[1] if len(parts) > 1 else None
    
    # Create the ol node
    node = PawserNode("ol")
    
    # If there's content, split into URL and link text
    if restOfLine:
        # Split the URL from the link text
        urlParts = restOfLine.split(" ", 1)       # ["https://website.com", "Open Link!"]
        url = urlParts[0]                          # "https://website.com"
        linkText = urlParts[1] if len(urlParts) > 1 else None  # "Open Link!" or None
        
        # Create URL node as child of ol
        urlNode = PawserNode(url)
        node.children.append(urlNode)
        
        # Add link text as child of URL node
        if linkText:
            urlNode.children.append(PawserTextNode(linkText))
    
    return node


# ==============================================================================
# MAIN PARSING FUNCTION - Reads the file and builds the tree
# ==============================================================================

def parsePawml(filePath):
    """
    Main function to parse a Pawml file into a tree structure
    
    Returns: Root PawserNode representing the entire document
    Raises: ValueError if file format is invalid
    """
    # Read all lines from the file
    with open(filePath, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    
    # --- Step 1: Validate file structure ---
    # Find first non-empty line - it must be "#pawml"
    firstLine = next((line.strip() for line in lines if line.strip()), None)
    if firstLine != "#pawml":
        raise ValueError("Error: File must start with #pawml")
    
    # Find last non-empty line - it must also be "#pawml"
    lastLine = next((line.strip() for line in reversed(lines) if line.strip()), None)
    if lastLine != "#pawml":
        raise ValueError("Error: File must end with #pawml")
    
    # --- Step 2: Set up the root node and parsing stack ---
    root = PawserNode("pawml")
    # Stack tracks where we are in the tree: [(node, indentation_level), ...]
    stack = [(root, -1)]
    
    # Define which tags we support
    generalTags = ["h1", "h2", "h3", "p"]
    specialTags = {
        "li": parseSpecialTag_li,
        "it": parseSpecialTag_it,
        "ol": parseSpecialTag_ol
    }
    
    # --- Step 3: Process each line (skip first and last #pawml lines) ---
    for lineNo, line in enumerate(lines[1:-1], start=2):
        # Skip empty lines
        if not line.strip():
            continue
        
        # Count how many tabs indent this line
        indent = 0
        while line.startswith("\t"):
            indent += 1
            line = line[1:]  # Remove the tab
        
        # Stop if we hit closing #pawml early
        if line == "#pawml":
            break
        
        # --- Parse different types of content ---
        
        # METADATA: Lines like "#mdata title="My Page""
        if line.startswith("#mdata"):
            try:
                # Extract the key=value part
                metadataContent = line[6:].strip()        # Remove "#mdata"
                parts = metadataContent.split("=", 1)     # Split at = sign
                
                if len(parts) != 2:
                    raise ValueError
                
                key = parts[0].strip()                    # e.g., "title"
                value = parts[1].strip().strip('"')       # e.g., "My Page"
                
                if not value:
                    raise ValueError
                
                # Build metadata node structure: mdata -> key -> text
                node = PawserNode("mdata")
                node.children.append(PawserNode(key))
                node.children[-1].children.append(PawserTextNode(value))
                
            except:
                raise ValueError(f"Error: Invalid mdata on line {lineNo}: '{line}'")
        
        # TAGS: Lines starting with # (like #h1, #li, #it)
        elif line.startswith("#"):
            # Extract the tag name
            tagName = line[1:].split(" ", 1)[0]
            
            # Use the appropriate parser
            if tagName in generalTags:
                node = parseGeneralTag(line, lineNo)
            elif tagName in specialTags:
                node = specialTags[tagName](line, lineNo)
            else:
                raise ValueError(f"Error: Unknown tag '{tagName}' on line {lineNo}")
        
        # PLAIN TEXT: Any line not starting with #
        else:
            node = PawserTextNode(line)
        
        # --- Step 4: Add node to tree at correct position ---
        # Pop stack until we find the right parent based on indentation
        while stack and stack[-1][1] >= indent:
            stack.pop()
        
        if not stack:
            raise ValueError(f"Error: Invalid indentation on line {lineNo}")
        
        # Add this node as a child of the current parent
        parentNode = stack[-1][0]
        parentNode.children.append(node)
        
        # Push this node onto the stack for future children
        stack.append((node, indent))
    
    return root


# ==============================================================================
# TREE TO STRING CONVERSION
# ==============================================================================

def treeToString(node, indent=0):
    """
    Convert tree structure to string format (like printTree but returns string)
    
    Returns the tree as a string with proper indentation
    """
    indentSpace = "    " * indent
    result = []
    
    # Text nodes display their content in quotes
    if node.type == "text":
        result.append(indentSpace + f'"{node.content}"')
    else:
        # Regular nodes display their type and attributes
        attrs = f" {node.attrs}" if node.attrs else ""
        result.append(indentSpace + node.type + attrs)
    
    # Recursively process all children
    for child in node.children:
        result.append(treeToString(child, indent + 1))
    
    return "\n".join(result)


# ==============================================================================
# TREE SIMPLIFICATION
# ==============================================================================

def simplifyPawTree(tree_string):
    """
    Simplify a Paw tree structure by removing root node, reducing indentation,
    and replacing tags with simplified names.
    
    Args:
        tree_string: String representation of the tree
        
    Returns:
        Simplified text as a string, or None if there was an error
    """
    try:
        lines = tree_string.splitlines()
        
        # 1. Remove empty lines
        lines = [line for line in lines if line.strip() != ""]
        
        # 2. Remove ONLY the first line (the root "pawml")
        if len(lines) >= 1:
            lines = lines[1:]
        else:
            lines = []
        
        # 3. Remove ONLY ONE level of indentation (one tab or 4 spaces)
        simplified_lines = []
        for line in lines:
            # Check if line starts with a tab
            if line.startswith("\t"):
                line = line[1:]  # Remove just ONE tab
            else:
                # Count leading spaces
                space_count = len(line) - len(line.lstrip(" "))
                
                # If spaces are a multiple of 4, remove just 4
                if space_count > 0 and space_count % 4 == 0:
                    line = line[4:]  # Remove just the first 4 spaces
            
            # Only add non-empty lines
            if line.strip():
                simplified_lines.append(line)
        
        # 4. Join back for replacement
        simplified_text = "\n".join(simplified_lines)
        
        # 5. Replace PawML tags
        replacements = {
           "h1": "HEADER1",
           "h2": "HEADER2",
           "h3": "HEADER3",
           "li": "LIST",
           "it": "ITEM",
           "ol": "LINK",
           "p": "PARAGRAPH",
           "mdata": "METADATA",
           "title": "TITLE"
        }
        
        # Go through each line and replace tags
        result_lines = []
        for line in simplified_text.splitlines():
            new_line = line
            stripped = line.lstrip()
            
            for old_tag, new_tag in replacements.items():
                if stripped == old_tag:
                    new_line = line.replace(old_tag, new_tag, 1)
                    break
                
                if stripped.startswith(old_tag + " "):
                    new_line = line.replace(old_tag, new_tag, 1)
                    break
            
            result_lines.append(new_line)
        
        simplified_text = "\n".join(result_lines)
        
        return simplified_text
            
    except Exception as e:
        print(f"Error in simplifyPawTree: {e}")
        return None


# ==============================================================================
# PAWSED TO INSTRUCTIONS CONVERSION
# ==============================================================================

def pawsedToInstructions(pawsed_string):
    """
    Parse a Pawsed string and return instructions as a list of strings.
    
    Args:
        pawsed_string: String representation of pawsed content
        
    Returns:
        List of instruction strings, or None if there was an error
    """
    try:
        lines = pawsed_string.splitlines()
        instructions = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            stripped = line.lstrip()
            indent = len(line) - len(stripped)
            
            if stripped == "LIST":
                # Check if this is opening or closing
                j = i + 1
                is_opening = False
                while j < len(lines):
                    next_line = lines[j]
                    if not next_line.strip():
                        j += 1
                        continue
                    next_stripped = next_line.lstrip()
                    next_indent = len(next_line) - len(next_stripped)
                    
                    if next_indent > 0 and next_stripped == "ITEM":
                        is_opening = True
                        break
                    elif next_indent == 0:
                        break
                    j += 1
                
                if is_opening:
                    instructions.append("BEGIN LIST")
                else:
                    instructions.append("END LIST")
            
            elif stripped.startswith("HEADER"):
                i += 1
                if i < len(lines):
                    content = lines[i].strip().strip('"')
                    instructions.append(f'ADD {stripped} "{content}"')
            
            elif stripped == "PARAGRAPH":
                i += 1
                if i < len(lines):
                    content = lines[i].strip().strip('"')
                    instructions.append(f'ADD PARAGRAPH "{content}"')

            elif stripped == "METADATA":
                i += 1
                if i < len(lines) and lines[i].strip() == "TITLE":
                    i += 1
                    if i < len(lines):
                        content = lines[i].strip().strip('"')
                        instructions.append(f'METADATA TITLE "{content}"')
            
            elif stripped == "ITEM":
                i += 1
                if i < len(lines):
                    content = lines[i].strip().strip('"')
                    instructions.append(f'ADD ITEM "{content}"')
            
            elif stripped == "LINK":
                i += 1
                url = lines[i].strip() if i < len(lines) else ""
                i += 1
                link_text = lines[i].strip().strip('"') if i < len(lines) else ""
                instructions.append(f'ADD LINK "{link_text}" TO {url}')
            
            i += 1
        
        return instructions
    
    except Exception as e:
        print(f"Error in pawsedToInstructions: {e}")
        return None


# ==============================================================================
# MAIN PIPELINE FUNCTION
# ==============================================================================

def pawml2instructions(filePath):
    """
    Complete pipeline: Parse Pawml file and convert to instructions
    
    Args:
        filePath: Path to the Pawml file
        
    Returns:
        List of instruction strings, or None if there was an error
    """
    try:
        # Step 1: Parse Pawml file to tree
        tree = parsePawml(filePath)
        if not tree:
            return None
        
        # Step 2: Convert tree to string
        tree_string = treeToString(tree)
        
        # Step 3: Simplify the tree string
        simplified = simplifyPawTree(tree_string)
        if not simplified:
            return None
        
        # Step 4: Convert to instructions
        instructions = pawsedToInstructions(simplified)
        
        return instructions
        
    except Exception as e:
        print(f"Error: {e}")
        return None


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def printInstructions(instructions):
    """
    Print instructions in a readable format.
    
    Args:
        instructions: List of instruction strings
    """
    if instructions:
        for instruction in instructions:
            print(instruction)


def printTree(node, indent=0):
    """
    Print the tree structure in a readable format
    
    Shows the hierarchy with indentation
    """
    indentSpace = "    " * indent
    
    # Text nodes display their content in quotes
    if node.type == "text":
        print(indentSpace + f'"{node.content}"')
        return
    
    # Regular nodes display their type and attributes
    attrs = f" {node.attrs}" if node.attrs else ""
    print(indentSpace + node.type + attrs)
    
    # Recursively print all children
    for child in node.children:
        printTree(child, indent + 1)


def pawml2domtree(filePath):
    """
    Main entry point - parse a Pawml file and return the tree
    
    Returns: Root node if successful, None if there was an error
    """
    try:
        return parsePawml(filePath)
    except Exception as e:
        print(e)
        return None
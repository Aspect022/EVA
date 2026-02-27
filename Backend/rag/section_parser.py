import re
import os

def parse_sections(file_path: str) -> dict:
    """
    Parses a markdown file into a dictionary of sections based on # [SECTION_NAME] headers.
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        content = f.read()

    # Match sections like # [SECTION_NAME]
    pattern = r"#\s*\[([A-Z0-9_]+)\]\n(.*?)(?=\n#\s*\[|$)"
    matches = re.finditer(pattern, content, re.DOTALL)

    sections = {}
    for match in matches:
        section_name = match.group(1)
        section_content = match.group(2).strip()
        sections[section_name] = section_content

    return sections

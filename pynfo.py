import os
import re
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

def indent_xml(elem, level=0):
    """
    Add proper indentation and newlines to XML elements for readability.
    """
    indent_str = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent_str + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent_str
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent_str
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent_str

# Constants for valid tags
PLATFORM_TAGS = ["(NES)", "(SNES)", "(N64)", "(GCN)", "(Wii)", "(Wii U)", "(NSW)", "(NS2)", "(GB)", "(GBC)", "(GBA)", "(NDS)", "(3DS)", "(Genesis)", "(Saturn)", "(Dreamcast)", "(PSX)", "(PS2)", "(PS3)", "(PS4)", "(PS5)", "(PSP)", "(Vita)", "(XBOX)", "(X360)", "(XB1)", "(XBS)", "(PC)", "(Jaguar)", "(NeoGeo)", "(Arcade)", "(3DO)"]
REGION_TAGS = ["(U)", "(UK)", "(A)", "(NZ)", "(E)", "(K)", "(J)"]
ALL_TAGS = PLATFORM_TAGS + REGION_TAGS

# Tag to XML element mapping
TAG_TO_ELEMENT = {
    "platform": PLATFORM_TAGS,
    "countrycode": REGION_TAGS,
}

# Statistics tracking
stats = {
    "processed": 0,
    "passed": 0,
    "failed": 0,
    "fixed": 0,
    "missing_studio": 0,
    "missing_year": 0,
}

def extract_studio_from_filename(filename):
    """
    Extract studio name from filename pattern: 'by <company> - ' or 'by <company> ('
    Returns the studio name or None if not found.
    """
    match = re.search(r' by ([^-\(]+?)(?:\s*[-\(])', filename)
    if match:
        return match.group(1).strip()
    return None

def get_platform_from_tag(tag):
    """Convert platform tag to expected XML genre value."""
    platform_mapping = {
        "(NES)": "Nintendo NES",
        "(SNES)": "Nintendo SNES",
        "(N64)": "Nintendo 64",
        "(GCN)": "Nintendo GameCube",
        "(Wii)": "Nintendo Wii",
        "(Wii U)": "Nintendo Wii U",
        "(NSW)": "Nintendo Switch",
        "(NS2)": "Nintendo Switch 2",
        "(GB)": "Nintendo Game Boy",
        "(GBC)": "Nintendo Game Boy Color",
        "(GBA)": "Nintendo Game Boy Advance",
        "(NDS)": "Nintendo DS",
        "(3DS)": "Nintendo 3DS",
        "(Genesis)": "Sega Genesis",
        "(Saturn)": "Sega Saturn",
        "(Dreamcast)": "Sega Dreamcast",
        "(PSX)": "Sony Playstation",
        "(PS2)": "Sony Playstation 2",
        "(PS3)": "Sony Playstation 3",
        "(PS4)": "Sony Playstation 4",
        "(PS5)": "Sony Playstation 5",
        "(PSP)": "Sony Playstation Portable",
        "(Vita)": "Sony Playstation Vita",
        "(XBOX)": "Microsoft Xbox",
        "(X360)": "Microsoft Xbox 360",
        "(XB1)": "Microsoft Xbox One",
        "(XBS)": "Microsoft Xbox Series X｜S",
        "(PC)": "PC",
        "(Jaguar)": "Atari Jaguar",
        "(NeoGeo)": "SNK NeoGeo",
        "(Arcade)": "Arcade",
        "(3DO)": "Panasonic 3DO",
    }
    return platform_mapping.get(tag)

def extract_year_from_filename(filename):
    """Extract year value from year in filename."""
    match = re.search(r'\((\d{4})\)', filename)
    if match:
        return match.group(1)
    return None

def extract_tags_from_filename(filename):
    """Extract all tags value from filename."""
    match = re.findall(r"\([^()]*\)", filename)
    if match:
        return match
    return None

def extract_region_code(tag):
    """Convert region tag to country code."""
    region_mapping = {
        "(U)": "US",
        "(UK)": "UK",
        "(A)": "AU",
        "(NZ)": "NZ",
        "(E)": "EU",
        "(K)": "KR",
        "(J)": "JP",
    }
    return region_mapping.get(tag)

def insert_element_after_runtime(root, tag_name, tag_value):
    """
    Insert a new element after the runtime element.
    If the element already exists, update it instead.
    """
    # Allow multiple <genre> tags
    if tag_name == "genre":
        new_element = ET.Element(tag_name)
        new_element.text = tag_value
        # Insert after runtime or append
        runtime_element = root.find("runtime")
        if runtime_element is not None:
            runtime_index = list(root).index(runtime_element)
            root.insert(runtime_index + 1, new_element)
        else:
            root.append(new_element)
        return new_element

    # Find runtime element
    runtime_element = root.find("runtime")

    if runtime_element is not None:
        # Find the index of runtime element
        runtime_index = list(root).index(runtime_element)
        # Insert new element after runtime
        new_element = ET.Element(tag_name)
        new_element.text = tag_value
        root.insert(runtime_index + 1, new_element)
    else:
        # If no runtime, just append to root
        new_element = ET.SubElement(root, tag_name)
        new_element.text = tag_value

    return new_element

def process_nfo_file(nfo_path, tag, fix=False):
    """
    Validate and optionally fix tags in an NFO file.
    Returns a tuple of (success: bool, message: str)
    """
    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        messages = []

        if tag in PLATFORM_TAGS:
            platform_value = get_platform_from_tag(tag)
            genre_elements = root.findall("genre")
            genre_found = any(g.text == platform_value for g in genre_elements)

            if not genre_found:
                if fix:
                    # Always add a new <genre> tag
                    insert_element_after_runtime(root, "genre", platform_value)
                    indent_xml(root)
                    tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
                    messages.append(f"✓ FIXED: Added <genre>{platform_value}</genre>")
                    stats["fixed"] += 1
                    return True, messages
                else:
                    messages.append(f"✗ MISSING: <genre>{platform_value}</genre> not found")
                    return False, messages
            else:
                messages.append(f"✓ FOUND: <genre>{platform_value}</genre>")
                return True, messages

        elif tag in REGION_TAGS:
            region_code = extract_region_code(tag)
            country_element = root.find("countrycode")

            if country_element is None or country_element.text != region_code:
                if fix:
                    insert_element_after_runtime(root, "countrycode", region_code)
                    indent_xml(root)
                    tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
                    messages.append(f"✓ FIXED: Set <countrycode>{region_code}</countrycode>")
                    stats["fixed"] += 1
                    return True, messages
                else:
                    messages.append(f"✗ MISSING: <countrycode>{region_code}</countrycode>")
                    return False, messages
            else:
                messages.append(f"✓ FOUND: <countrycode>{region_code}</countrycode>")
                return True, messages

    except Exception as e:
        return False, [f"✗ ERROR: {str(e)}"]

def check_studio_tag(filename, nfo_path, fix=False):
    """
    Check for 'by <company>' pattern in filename and ensure <studio> tag in NFO.
    Returns True if valid, False otherwise.
    """
    studio_name = extract_studio_from_filename(filename)

    if not studio_name:
        stats["missing_studio"] += 1
        return False, f"✗ MISSING STUDIO TAG: No 'by <company>' pattern found in filename"

    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        studio_element = root.find("studio")

        if studio_element is None or studio_element.text != studio_name:
            if fix:
                insert_element_after_runtime(root, "studio", studio_name)
                indent_xml(root)
                tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
                stats["fixed"] += 1
                return True, f"✓ FIXED: Set <studio>{studio_name}</studio>"
            else:
                return False, f"✗ MISSING: <studio>{studio_name}</studio>"
        else:
            return True, f"✓ FOUND: <studio>{studio_name}</studio>"

    except Exception as e:
        return False, f"✗ ERROR: {str(e)}"

def check_year_tag(filename, nfo_path, fix=False):
    """
    Check for '(YYYY)' pattern in filename and ensure <year> tag in NFO.
    Returns True if valid, False otherwise.
    """
    year_value = extract_year_from_filename(filename)

    if not year_value:
        stats["missing_year"] += 1
        return False, f"✗ MISSING YEAR TAG: No '(YYYY)' pattern found in filename"

    try:
        tree = ET.parse(nfo_path)
        root = tree.getroot()
        year_element = root.find("year")

        if year_element is None or year_element.text != year_value:
            if fix:
                insert_element_after_runtime(root, "year", year_value)
                indent_xml(root)
                tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
                stats["fixed"] += 1
                return True, f"✓ FIXED: Set <year>{year_value}</year>"
            else:
                return False, f"✗ MISSING: <year>{year_value}</year>"
        else:
            return True, f"✓ FOUND: <year>{year_value}</year>"

    except Exception as e:
        return False, f"✗ ERROR: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Manage Jellyfin .nfo files.')
    parser.add_argument('--fix', action='store_true', help='Automatically fix missing tags.')
    parser.add_argument('folder', help='Path to the folder containing .nfo files.')
    args = parser.parse_args()

    folder_path = Path(args.folder)
    if not folder_path.is_dir():
        print(f"Error: {args.folder} is not a valid directory.")
        return

    # Iterate through all .nfo files
    nfo_files = list(folder_path.glob('*.nfo'))

    if not nfo_files:
        print(f"No .nfo files found in {folder_path}")
        return

    for nfo_file in sorted(nfo_files):
        filename_base = nfo_file.stem  # filename without .nfo extension

        stats["processed"] += 1
        print(f"\n[{stats['processed']}] {nfo_file.name}")
        failed = False

        # Validate studio tag
        success, message = check_studio_tag(filename_base, str(nfo_file), fix=args.fix)
        print(f"  {message}")
        if not success:
            failed = True

        # Validate year tag
        success, message = check_year_tag(filename_base, str(nfo_file), fix=args.fix)
        print(f"  {message}")
        if not success:
            failed = True

        # Get all parenthetical tags
        filename_tags = extract_tags_from_filename(filename_base)

        # Validate platform and region tags
        for tag in filename_tags:
            # Ignore tags we don't use'
            if tag in ALL_TAGS:
                success, messages = process_nfo_file(str(nfo_file), tag, fix=args.fix)
                for msg in messages:
                    print(f"  {msg}")
                if not success:
                    failed = True

        # Tally success/fail
        if failed:
            stats["failed"] += 1
        else:
            stats["passed"] += 1

    # Print detailed report
    print(f"\n{'='*80}")
    print(f"Processing NFO files in: {folder_path.absolute()}")
    print(f"Fix mode: {'ENABLED' if args.fix else 'DISABLED (read-only)'}")
    print(f"{'='*80}")
    print(f"Files processed:  {stats['processed']}")
    print(f"Files Passed:     {stats['passed']}")
    print(f"Files Failed:     {stats['failed']}")
    print(f"Tags Fixed:       {stats['fixed']}")
    print(f"{'-'*10}FILENAME AUDIT{'-'*10}")
    print(f"Missing studio:   {stats['missing_studio']}")
    print(f"Missing year:     {stats['missing_year']}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

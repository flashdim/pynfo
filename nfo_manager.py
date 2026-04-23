import os
import re
import xml.etree.ElementTree as ET
import argparse
from pathlib import Path

# Constants for valid tags
PLATFORM_TAGS = ["(NES)", "(SNES)", "(N64)", "(NSW)", "(NS2)", "(GB)", "(GBC)", "(GBA)", "(NDS)", "(3DS)", "(Genesis)", "(Saturn)", "(Dreamcast)", "(PSX)", "(PS2)", "(PS3)", "(PS4)", "(PS5)", "(PSP)", "(Vita)", "(XBOX)", "(X360)", "(XB1)", "(XSX|S)", "(PC)", "(Jaguar)", "(NeoGeo)", "(Arcade)", "(3DO)"]
YEAR_TAGS = ["(19XX)", "(20XX)"]
REGION_TAGS = ["(U)", "(UK)", "(A)", "(NZ)", "(E)", "(K)", "(J)"]

# Tag to XML element mapping
TAG_TO_ELEMENT = {
    "platform": PLATFORM_TAGS,
    "year": YEAR_TAGS,
    "countrycode": REGION_TAGS,
}

# Statistics tracking
stats = {
    "processed": 0,
    "passed": 0,
    "failed": 0,
    "fixed": 0,
    "missing_studio": 0,
}

def extract_studio_from_filename(filename):
    """
    Extract studio name from filename pattern: 'by <company> - ' or 'by <company> ('
    Returns the studio name or None if not found.
    """
    match = re.search(r' by ([^-
\(]+?)(?:\s*[-\(])', filename)
    if match:
        return match.group(1).strip()
    return None

def get_platform_from_tag(tag):
    """Convert platform tag to expected XML genre value."""
    platform_mapping = {
        "(NES)": "Nintendo NES",
        "(SNES)": "Nintendo SNES",
        "(N64)": "Nintendo 64",
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
        "(XSX|S)": "Microsoft Xbox Series X|S",
        "(PC)": "PC",
        "(Jaguar)": "Atari Jaguar",
        "(NeoGeo)": "SNK NeoGeo",
        "(Arcade)": "Arcade",
        "(3DO)": "Panasonic 3DO",
    }
    return platform_mapping.get(tag)

def extract_year_from_tag(tag):
    """Extract year value from year tag."""
    match = re.search(r'\((\d{4})\)', tag)
    if match:
        return match.group(1)
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
                    genre = ET.SubElement(root, "genre")
                    genre.text = platform_value
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
                
        elif tag in YEAR_TAGS or re.match(r'\(\d{4}\)', tag):
            year_value = extract_year_from_tag(tag)
            year_element = root.find("year")
            
            if year_element is None or year_element.text != year_value:
                if fix and year_value:
                    if year_element is None:
                        year_element = ET.SubElement(root, "year")
                    year_element.text = year_value
                    tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
                    messages.append(f"✓ FIXED: Set <year>{year_value}</year>")
                    stats["fixed"] += 1
                    return True, messages
                else:
                    messages.append(f"✗ MISSING: <year>{year_value}</year>")
                    return False, messages
            else:
                messages.append(f"✓ FOUND: <year>{year_value}</year>")
                return True, messages
                
        elif tag in REGION_TAGS:
            region_code = extract_region_code(tag)
            country_element = root.find("countrycode")
            
            if country_element is None or country_element.text != region_code:
                if fix:
                    if country_element is None:
                        country_element = ET.SubElement(root, "countrycode")
                    country_element.text = region_code
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
                if studio_element is None:
                    studio_element = ET.SubElement(root, "studio")
                studio_element.text = studio_name
                tree.write(nfo_path, encoding='utf-8', xml_declaration=True)
                stats["fixed"] += 1
                return True, f"✓ FIXED: Set <studio>{studio_name}</studio>"
            else:
                return False, f"✗ MISSING: <studio>{studio_name}</studio>"
        else:
            return True, f"✓ FOUND: <studio>{studio_name}</studio>"
            
    except Exception as e:
        return False, f"✗ ERROR: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Manage Jellyfin .nfo files.')
    parser.add_argument('-t', '--tag', help='Tag to validate or update (e.g., "(SNES)", "(2022)", "(U)"). Use "studio" to check studio tags.')
    parser.add_argument('--fix', action='store_true', help='Automatically fix missing tags.')
    parser.add_argument('folder', help='Path to the folder containing .nfo files.')
    args = parser.parse_args()

    # If no tag specified, check studio tags for all files
    if not args.tag:
        args.tag = "studio"

    folder_path = Path(args.folder)
    if not folder_path.is_dir():
        print(f"Error: {args.folder} is not a valid directory.")
        return

    print(f"\n{'='*80}")
    print(f"Processing NFO files in: {folder_path.absolute()}")
    print(f"Tag: {args.tag}")
    print(f"Fix mode: {'ENABLED' if args.fix else 'DISABLED (read-only)'}")
    print(f"{'='*80}\n")

    # Iterate through all .nfo files
    nfo_files = list(folder_path.glob('*.nfo'))
    
    if not nfo_files:
        print(f"No .nfo files found in {folder_path}")
        return

    for nfo_file in sorted(nfo_files):
        filename_base = nfo_file.stem  # filename without .nfo extension
        
        # Filter by tag if it's in the filename (except for studio)
        if args.tag != "studio" and args.tag not in filename_base:
            continue

        stats["processed"] += 1
        print(f"\n[{{stats['processed']}}] {{nfo_file.name}}")

        if args.tag == "studio":
            success, message = check_studio_tag(filename_base, str(nfo_file), fix=args.fix)
            print(f"  {{message}}")
            if success:
                stats["passed"] += 1
            else:
                stats["failed"] += 1
        else:
            success, messages = process_nfo_file(str(nfo_file), args.tag, fix=args.fix)
            for msg in messages:
                print(f"  {{msg}}")
            if success:
                stats["passed"] += 1
            else:
                stats["failed"] += 1

    # Print detailed report
    print(f"\n{'='*80}")
    print(f"DETAILED REPORT")
    print(f"{'='*80}")
    print(f"Files processed:  {{stats['processed']}}")
    print(f"Passed:           {{stats['passed']}}")
    print(f"Failed:           {{stats['failed']}}")
    print(f"Fixed:            {{stats['fixed']}}")
    if args.tag == "studio":
        print(f"Missing studio tag: {{stats['missing_studio']}}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
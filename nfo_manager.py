import os
import xml.etree.ElementTree as ET
import argparse

# Constants for valid tags
PLATFORM_TAGS = ["(NES)", "(SNES)", "(N64)", "(NSW)", "(NS2)", "(GB)", "(GBC)", "(GBA)", "(NDS)", "(3DS)", "(Genesis)", "(Saturn)", "(Dreamcast)", "(PSX)", "(PS2)", "(PS3)", "(PS4)", "(PS5)", "(PSP)", "(Vita)", "(XBOX)", "(X360)", "(XB1)", "(XSX|S)", "(PC)", "(Jaguar)", "(NeoGeo)", "(Arcade)", "(3DO)"]
YEAR_TAGS = ["(19XX)", "(20XX)"]
REGION_TAGS = ["(U)", "(UK)", "(A)", "(NZ)", "(E)", "(K)", "(J)"]

# Function to validate/update tags in NFO files

def validate_nfo_tags(filename, tag):
    tree = ET.parse(filename)
    root = tree.getroot()

    # Depending on the tag, check for existence
    if tag in PLATFORM_TAGS:
        element = root.find("platform")
        if element is None:
            raise ValueError(f"'{tag}' tag not found in {filename}.")
    elif tag in YEAR_TAGS:
        element = root.find("year")
        if element is None:
            raise ValueError(f"'{tag}' tag not found in {filename}.")
    elif tag in REGION_TAGS:
        element = root.find("region")
        if element is None:
            raise ValueError(f"'{tag}' tag not found in {filename}.")

# Command-line arguments parsing

def main():
    parser = argparse.ArgumentParser(description='Manage Jellyfin .nfo files.')
    parser.add_argument('-t', '--tag', required=True, help='Tag to validate or update.')
    parser.add_argument('folder', help='Path to the folder containing .nfo files.')
    args = parser.parse_args()

    # Iterate through the provided folder
    for filename in os.listdir(args.folder):
        if filename.endswith('.nfo') and args.tag in filename:
            full_path = os.path.join(args.folder, filename)
            try:
                validate_nfo_tags(full_path, args.tag)
                print(f"'{args.tag}' tag exists in {full_path}.")
            except ValueError as e:
                print(e)

if __name__ == '__main__':
    main()
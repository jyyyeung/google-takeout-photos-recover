import os
import zipfile
from pathlib import Path


def extract_and_merge_zips(zip_folder: str, output_folder: str) -> str:
    """
    Extract all zip files from zip_folder and merge their contents into output_folder.
    Returns the path to the merged directory.
    """
    zip_folder_path = Path(zip_folder)
    zip_files = sorted(zip_folder_path.glob("*.zip"))

    if not zip_files:
        raise ValueError(f"No zip files found in {zip_folder}")

    print(f"Found {len(zip_files)} zip file(s) to extract")

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Extract all zip files
    for zip_file in zip_files:
        print(f"Extracting {zip_file.name}...")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            # Get all members
            members = zip_ref.namelist()

            # Extract each member, handling path conflicts
            for member in members:
                # Skip directories
                if member.endswith("/"):
                    continue

                # Get the destination path (remove the takeout-* prefix if present)
                # Google Takeout zips typically have a top-level directory like "takeout-20251108T080515Z-1"
                parts = Path(member).parts
                if len(parts) > 1 and parts[0].startswith("takeout-"):
                    # Remove the takeout-* prefix and reconstruct path
                    relative_path = Path(*parts[1:])
                else:
                    relative_path = Path(member)

                dest_path = Path(output_folder) / relative_path

                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Extract file (skip if already exists to avoid overwriting)
                if not dest_path.exists():
                    with zip_ref.open(member) as source:
                        with open(dest_path, "wb") as target:
                            target.write(source.read())

    print(f"Merged contents extracted to {output_folder}")
    return output_folder

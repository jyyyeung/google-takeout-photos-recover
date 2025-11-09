import argparse
import os
import tempfile

from src.recover_metadata import Metadata
from src.zip_extractor import extract_and_merge_zips


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "takeout_folder",
        help="Folder where your google photos are located (or folder containing zip files)",
    )
    parser.add_argument(
        "output_folder",
        help="Output folder where the photos and videos with metadata recovered will be saved",
    )
    parser.add_argument(
        "--zip-folder",
        action="store_true",
        help="If set, takeout_folder is treated as a directory containing split zip files to extract and merge",
    )
    parser.add_argument(
        "--extract-dir",
        help="Directory to extract zip files to (only used with --zip-folder). If not specified, uses a temporary directory that is cleaned up after processing.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.takeout_folder):
        raise FileNotFoundError(
            f"The takeout_folder {args.takeout_folder} does not exist"
        )
    if args.extract_dir and not args.zip_folder:
        raise ValueError("--extract-dir can only be used with --zip-folder")
    return args


def main():
    args = parse_args()

    if args.zip_folder:
        # Extract and merge zip files first
        if args.extract_dir:
            # Use user-specified directory
            os.makedirs(args.extract_dir, exist_ok=True)
            merged_folder = extract_and_merge_zips(
                args.takeout_folder, args.extract_dir
            )
            Metadata.recover(merged_folder, args.output_folder)
        else:
            # Use temporary directory that will be cleaned up
            with tempfile.TemporaryDirectory() as temp_dir:
                merged_folder = extract_and_merge_zips(args.takeout_folder, temp_dir)
                Metadata.recover(merged_folder, args.output_folder)
    else:
        # Use takeout_folder directly
        Metadata.recover(args.takeout_folder, args.output_folder)


if __name__ == "__main__":
    main()

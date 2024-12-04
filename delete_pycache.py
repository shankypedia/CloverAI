import os
import shutil
import argparse
import logging


def delete_pycache_directories(directory, recursive, dry_run):
    """
    Deletes __pycache__ directories.

    Args:
        directory (str): Directory to start searching from.
        recursive (bool): Recursively delete __pycache__ directories.
        dry_run (bool): Show what would be deleted without actually deleting.

    Returns:
        bool: True if any __pycache__ directories were found, False otherwise.
    """
    found_pycache = False
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                found_pycache = True
                pycache_path = os.path.join(root, dir_name)
                if dry_run:
                    logging.info(f"Would delete: {pycache_path}")
                else:
                    try:
                        logging.info(f"Deleting: {pycache_path}")
                        shutil.rmtree(pycache_path)
                    except Exception as e:
                        logging.error(f"Error deleting {pycache_path}: {e}")
        if not recursive:
            break
    return found_pycache


def main():
    """
    Main function to parse arguments and delete __pycache__ directories.

    Example usage:
    1. Dry Run (Non-Recursive):
       python delete_pycache.py -d -v
       Description: This command will show what __pycache__ directories would be deleted without actually deleting them, with verbose output.

    2. Dry Run (Recursive):
       python delete_pycache.py -d -r -v
       Description: This command will show what __pycache__ directories would be deleted recursively without actually deleting them, with verbose output.

    3. Actual Deletion (Non-Recursive):
       python delete_pycache.py -v
       Description: This command will delete __pycache__ directories in the current directory without recursion, with verbose output.

    4. Actual Deletion (Recursive):
       python delete_pycache.py -r -v
       Description: This command will delete __pycache__ directories recursively starting from the current directory, with verbose output.
    """
    parser = argparse.ArgumentParser(description="Delete __pycache__ directories.")
    parser.add_argument(
        "directory", nargs="?", default=".",
        help="Directory to start searching from (default: current directory)."
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", default=True,
        help="Recursively delete __pycache__ directories (default: True)."
    )
    parser.add_argument(
        "-d", "--dry-run", action="store_true", default=False,
        help="Show what would be deleted without actually deleting (default: False)."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=True,
        help="Enable verbose output (default: True)."
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    found_pycache = delete_pycache_directories(args.directory, args.recursive, args.dry_run)

    if found_pycache:
        if not args.dry_run:
            logging.info("All __pycache__ directories have been deleted.")
        else:
            logging.info("Dry run complete. No directories were deleted.")
    else:
        logging.info("No __pycache__ directories found.")


if __name__ == "__main__":
    main()

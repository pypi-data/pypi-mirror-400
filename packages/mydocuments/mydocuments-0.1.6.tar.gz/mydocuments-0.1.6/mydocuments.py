import os
import sys
from glob import glob

if sys.platform == "win32":
    import ctypes
    from ctypes.wintypes import MAX_PATH

VERSION = "0.1.6"


def print_version_info():
    """Print version information."""
    print(f"mydocuments v{VERSION}")


def print_usage():
    print("Usage: mydocuments [-f | -w | -h | -v]")
    print("Options:")
    print("  --help, -h    Show this help message and exit.")
    print("  --version, -v Show version information and exit.")
    print("  --fuzzy, -f   Use a fuzzy multiplatform method.")
    print("  --winapi, -w  Use Windows API method.")


def main():

    path = None

    # check for command line args
    if len(sys.argv) > 1:
        switch = sys.argv[1]
        if switch == "--help" or switch == "-h":
            print_version_info()
            print_usage()
            sys.exit(0)
        elif switch == "--version" or switch == "-v":
            print_version_info()
            sys.exit(0)
        elif switch == "--fuzzy" or switch == "-f":
            path = get_documents_path_fuzzy()
        elif switch == "--winapi" or switch == "-w":
            path = get_documents_path_winapi()
        else:
            print(f"Unknown argument: {switch}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.platform == "win32":
            path = get_documents_path_winapi()
        else:
            path = get_documents_path_fuzzy()

    if path:
        print(path)
        sys.exit(0)
    else:
        print("Could not determine the path to Documents.", file=sys.stderr)
        sys.exit(1)


def get_documents_path_fuzzy():
    """Multi platform function to get the path to the Documents folder.
    Checks for OneDrive locations first."""

    documents_path = None

    if sys.platform == "win32":

        # Check if OneDrive location exists
        onedrive_locations = glob(os.path.expanduser("~\\*\\Documents"))
        for path in onedrive_locations:
            if "OneDrive" in path:
                documents_path = path
                break

        # If not found in OneDrive, default to the standard location
        if documents_path is None:
            documents_path = os.path.join(os.environ["USERPROFILE"], "Documents")
    else:
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")

    # Check if the path exists
    if not os.path.exists(documents_path):
        return None
    else:
        return documents_path


def get_documents_path_winapi():
    """ Get the path to the Documents folder using Windows API calls.
    This should work eve if the Documents folder was manually relocated"""

    if sys.platform != "win32":
        print("Sorry, this only works on Windows.", file=sys.stderr)
        sys.exit(1)

    dll = ctypes.windll.shell32
    buf = ctypes.create_unicode_buffer(MAX_PATH + 1)
    # CSIDL_PERSONAL (0x0005) corresponds to the Documents folder
    if dll.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
        return buf.value
    else:
        return None


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# This script takes two arguments: a file path and a value that is major, minor
# or patch. It searches the file for a version string in the format
# "major.minor.patch" and increments the specified part of the version.

import os
import re
import sys

VERSION = "0.1.2"


def increment_version(file_path, part):

    # check if file_path exists and exit if it doesn't
    if not os.path.isfile(file_path):
        print(f"File {file_path} does not exist.")
        exit(1)

    with open(file_path, 'r') as file:
        content = file.read()

    version_pattern = r'(\d+)\.(\d+)\.(\d+)'
    match = re.search(version_pattern, content)

    if not match:
        print("No version string found in the file.")
        exit(1)

    major, minor, patch = map(int, match.groups())

    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    else:
        print("Invalid part specified. Use major, minor, or patch.")
        exit(1)

    new_version = f"{major}.{minor}.{patch}"
    new_content = re.sub(version_pattern, new_version, content, count=1)

    with open(file_path, 'w') as file:
        file.write(new_content)

    print(f"{file_path} bumped to version {new_version}")


def main():
    if len(sys.argv) != 3:
        print("Usage: bmp <file_path> <major|minor|patch>")
    else:
        if sys.argv[1] in ['-v', '--version']:
            print(f"bmp v{VERSION}")
            exit(0)
        else:
            increment_version(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()

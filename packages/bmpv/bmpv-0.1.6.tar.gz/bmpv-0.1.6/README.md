# bmpv

A simple command line tool for bumping the version of your project.

## Usage

```bash
Usage:
        bmpv <file> <part>

        <file> Path to the file containing the version string.
        <part> Part to increment: major, minor, or patch.

Options:
        -v, --version   Show version information
        -h, --help      Show this help message
```

The program will search your code for a line that looks something like a semantic version number:

    "1.2.3"

It will parse out the major, minor and patch parts and increment the appropriate digits.


| Version Part | Current Version | New Version |
| --- | --- | --- |
| `patch` | `A.B.C` | `A.B.C+1` |
| `minor` | `A.B.C` | `A.B+1.0` |
| `major` | `A.B.C` | `A+1.0.0` |

## Installation

You can install using `uv`:

```bash
uv tool install bmpv
```

You can run without installing:

```bash
uv tool run bmpv
```

On Windows, this tool is distributed via `scoop` (see [scoop.sh](https://scoop.sh)).

First, you need to add my bucket:

    scoop bucket add maciak https://github.com/maciakl/bucket
    scoop update

Next simply run:
 
    scoop install bmpv

If you don't want to use `scoop` you can simply download the executable from the release page and extract it somewhere in your path.

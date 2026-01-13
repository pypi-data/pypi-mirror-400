# 🦋 bfly

The `bfly` tool is a simplistic command line tool for posting short messages or links to BlueSky social network.

## Purpose

The main purpose of this tool, and the reason it was built was the need to have a quick and easy tool for posting
BlueSky announcements as part of a build and release script.

## Usage


```bash
Usage:
        bfly <subcommand> [argumens]

Subcommands:
        post <text>             Post to Bsky. Enclose <text> in quotes.
        annouce <text> <url>    Post a link. Put <text> in quotes.

Options:
        -h, --help      Show this help message
        -v, --version   Show version information

Options must be used as the first argument.
```

## Configuration

To use `bfly`, you need to set two environment variables:

- `BFLY_HANDLE` - your BlueSky username (e.g. `user.bsky.social`)
- `BFLY_APP_PASSWORD` - an app password generated via your BlueSky account settings


## Installation

You can install `bfly` via `uv`:

```bash
uv tool install bfly
```

You can also run `bfly` directly without installation:

```bash
uv tool run bfly <subcommand> [arguments]
```

On Windows, this tool is distributed via `scoop` (see [scoop.sh](https://scoop.sh)).

First, you need to add my bucket:

    scoop bucket add maciak https://github.com/maciakl/bucket
    scoop update

Next simply run:
 
    scoop install bmpv

If you don't want to use `scoop` you can simply download the executable from the release page and extract it somewhere in your path.

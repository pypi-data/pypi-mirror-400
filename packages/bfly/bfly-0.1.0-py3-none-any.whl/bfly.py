import os
import sys
import atproto
import termcolor

VERSION = "0.1.0"


def main():
    if len(sys.argv) < 2:
        banner()
        usage()
        return

    if sys.argv[1] == "post":
        banner()
        post(sys.argv[2:])
    elif sys.argv[1] == "announce":
        banner()
        announce(sys.argv[2:])
    elif sys.argv[1] in ("-h", "--help"):
        banner()
        usage()
    elif sys.argv[1] in ("-v", "--version"):
        banner()
    else:
        banner()
        err(f"Unknown subcommand: {sys.argv[1]}")
        usage()


def get_handle():
    msg("Getting handle from BLUESKY_HANDLE environment variable...")
    handle = os.getenv("BLUESKY_HANDLE")

    if not handle:
        err("BLUESKY_HANDLE environment variable not set.")
        sys.exit(1)
    else:
        return handle


def get_password():
    msg("Getting password from BLUESKY_APP_PASSWORD environment variable...")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not password:
        err("BLUESKY_APP_PASSWORD environment variable not set.")
        sys.exit(1)
    else:
        return password


def login():

    msg("Attempting to log in...")

    client = atproto.Client()

    handle = get_handle()
    password = get_password()

    msg(f"Logging in as {handle}...")

    try:
        client.login(handle, password)
    except Exception as e:
        err(f"Authentication failed: {e}.")
        sys.exit(1)

    return client


def post(args):

    if len(args) < 1:
        err("post subcommand requires <text> argument.")
        sys.exit(1)

    text = args[0]
    client = login()

    try:
        client.send_post(text)
        msg("Successfully posted.")
    except Exception as e:
        err(f"Failed to post: {e}")
        sys.exit(1)


def announce(args):

    if len(args) < 2:
        err("announce subcommand requires <text> and <url> arguments.")
        sys.exit(1)

    text = args[0]
    url = args[1]

    content = atproto.client_utils.TextBuilder()
    content.text(text+" ")  # Add a trailing space

    # make sure that url starts with http:// or https://, bail if it does not
    if not (url.startswith("http://") or url.startswith("https://")):
        err("the url must start with http:// or https://")
        sys.exit(1)

    content.link(url, url)

    client = login()

    try:
        client.send_post(content)
        msg("Successfully posted the announcement.")
    except Exception as e:
        err(f"Failed to post announcement: {e}")
        sys.exit(1)


def msg(text, color="cyan"):
    print(termcolor.colored(text, color))


def err(text):
    sys.stderr.write(termcolor.colored(text + '\n', 'red'))


def banner():
    msg(f"🦋 bfly v{VERSION}")


def usage():
    msg("")
    msg("Usage:")
    msg("\tbfly <subcommand> [argumens]")
    msg("")
    msg("Subcommands:")
    msg("\tpost <text>\t\tPost to Bsky. Enclose <text> in quotes.")
    msg("\tannouce <text> <url>\tPost a link. Put <text> in quotes.")
    msg("")
    msg("Options:")
    msg("\t-h, --help\tShow this help message")
    msg("\t-v, --version\tShow version information")
    msg("")
    msg("Options must be used as the first argument.")


if __name__ == "__main__":
    main()

import json
import os
import sys
import tempfile
from pathlib import Path
import datetime as dt
from subprocess import call, check_output

import requests
import tomli
import humanize


CONFIG_DIRNAME = "lolbin"
CONFIG_FILENAME = "config.toml"
DEFAULT_DOMAIN = "api.omg.lol"
USAGE_STRING = """
usage: lolbin [-h] [--delete PASTE_NAME] [-e PASTE_NAME] [--paste PASTE_NAME] [--file FILE] [--list]
              [--public] [--user USERNAME] [--show PASTE_NAME] [--debug] [--help] [-L] [-P] [-u]

A command-line interface tool for managing pastes on paste.lol.

optional arguments:
  -h, --help            show this help message and exit
  --edit PASTE_NAME, -e PASTE_NAME
                        Opens the content of a specific paste in an editor for editing.
  --paste PASTE_NAME    Create or update a paste with specified title and content from standard input.
  --file FILE           Specify a file to read the content for creating/updating a paste instead of standard input.
  --list                Lists all your pastes along with their titles and modification time (default action).
  --user USERNAME, -u USERNAME
                        THe username to request the past from
  --show PASTE_NAME     Displays the content of a specific paste by its title.
  --delete PASTE_NAME, -d PASTE_NAME
                        Deletes a specific paste by its title.
  --debug               Print actions, paste name, username, and bearer token without performing any action.
  --listed, -L          List only public (listed) pastes. Opposite of private (non-listed).
  --public, -P          Alias for --listed.

Very quick use examples:
- List Pastes: lolbin
- List Public Pastes: lolbin -P
- Show Paste: lolbin paste-name
- Create Paste: echo 'My paste' | lolbin paste-name
- Create Listed Paste: echo 'My paste' | lolbin paste-name -L
- Edit Paste: lolbin -e paste-name
- Delete Paste: lolbin -d paste-name

WARNING: Every paste on paste.lol is public.
If you have the URL of a paste, you can fetch it without authentication."""

# TODO: Add type hints to all functions


def get_token(token_cmd):
    if (token_cmd[0] == "`" and token_cmd[-1] == "`") or token_cmd[0] == "$":
        token_cmd = (
            check_output(token_cmd.strip("$`").strip(), shell=True)
            .decode("utf-8")
            .rstrip("\n")
        )

    return token_cmd


def get_config():
    """
    Retrieve the config file from the user's home directory.
    Example: ~/.config/lolbin/config.toml

    Returns:
        dict: The config file as a dict.
    """
    config_path = (
        Path(
            os.environ["XDG_CONFIG_HOME"]
            if "XDG_CONFIG_HOME" in os.environ
            else (Path(os.environ["HOME"]) / ".config")
        )
        / CONFIG_DIRNAME
        / CONFIG_FILENAME
    )
    if not config_path.exists():
        print("Config file doesn't exists.", file=sys.stderr)
        # WARN: That is false, should return empty config and a link to the documentation section "config.toml".
        print("Configure lolbin <https://source.tube/ache/lolbin#configuration>")
        return {}

    with open(config_path, "rb") as f:
        return tomli.load(f)


def create_paste(paste, content, username, token, public):
    """
    Create a paste on omg.lol.

    Args:
        paste (str): The paste name (id). An string of characters (ASCII only without spaces).
        content (str): The content of the paste.
        username (str): The username of the user.
        token (str): The authentification token. You can get it from <https://home.omg.lol/account>
        public (bool): True to make the paste listed.
    """
    headers = {"Authorization": f"Bearer {get_token(token)}"}
    data_send = {"title": paste, "content": content}
    if public:
        data_send["listed"] = "true"  # NOTE: It's a not documented feature
    response = requests.post(
        f"https://{DEFAULT_DOMAIN}/address/{username}/pastebin/",
        headers=headers,
        data=json.dumps(data_send),
    )
    data = response.json()

    if data["request"]["status_code"] != 200:
        print(f"Error status code {data['request']['status_code']}.", file=sys.stderr)
        if "response" in data:
            if "message" in data["response"]:
                print(data["response"]["message"], file=sys.stderr)

        if data["request"]["status_code"] >= 400:
            sys.exit(1)
        else:
            return

    if "response" in data:
        if "message" in data["response"]:
            message = data["response"]["message"]
            print(message[: message.index(".") + 1])
            print(
                f"This paste is {f'listed on https://paste.lol/{username}' if public else 'non-listed'}"
            )
            message = message[message.index(".") + 1 :]
            message = message[message.index('"') + 1 :]
            last = message.index('"')
            print(f"URL: {message[:last]}")
        else:
            print("No message returned")
    else:
        print("No reponse returned")


def list_paste(username, token, public):
    """
    List all pastes for a user.

    Args:
        username (str): The username of the user.
        token (str): The authentification token. You can get it from <https://home.omg.lol/account>
        public (bool): Whether to list public pastes or not.
    """

    headers = (
        {}
        if public or token is None
        else {"Authorization": f"Bearer {get_token(token)}"}
    )
    response = requests.get(
        f"https://{DEFAULT_DOMAIN}/address/{username}/pastebin", headers=headers
    )
    data = response.json()

    if data["request"]["status_code"] != 200:
        print(f"Error status code {data['request']['status_code']}.", file=sys.stderr)
        if "response" in data:
            if "message" in data["response"]:
                print(data["response"]["message"], file=sys.stderr)

        if data["request"]["status_code"] >= 400:
            sys.exit(1)
        else:
            return

    if "response" in data:
        if "message" in data["response"]:
            print(data["response"]["message"])
        else:
            print("No message returned")
    else:
        print("No reponse returned")

    for paste in data["response"]["pastebin"]:
        modified_on_date = dt.datetime.fromtimestamp(paste["modified_on"])
        modified_on_string = humanize.naturaltime(dt.datetime.now() - modified_on_date)
        print(f" - {paste['title']} ({modified_on_string})")


def get_paste(paste, username, token):
    """
    Get a paste.

    Returns:
        String: The paste content or None if an error occured.
        Boolean: True if the paste is public, False otherwise.
    """
    headers = {} if token is None else {"Authorization": f"Bearer {get_token(token)}"}
    response = requests.get(
        f"https://{DEFAULT_DOMAIN}/address/{username}/pastebin/{paste}", headers=headers
    )
    data = response.json()

    if data["request"]["status_code"] != 200:
        return None, None

    if (
        "response" in data
        and "paste" in data["response"]
        and "content" in data["response"]["paste"]
    ):
        return data["response"]["paste"]["content"], (
            "listed" in data["response"]["paste"]
            and data["response"]["paste"]["listed"] == 1
        )

    return None, None


def show_paste(paste, username, token):
    """
    Show a paste.

    Args:
        paste (str): The paste name (id). An string of characters (ASCII only without spaces).
        username (str): The username of the user.
        token (str): The authentification token. You can get it from <https://home.omg.lol/account>
    """

    headers = {} if token is None else {"Authorization": f"Bearer {get_token(token)}"}
    response = requests.get(
        f"https://{DEFAULT_DOMAIN}/address/{username}/pastebin/{paste}", headers=headers
    )
    data = response.json()

    if data["request"]["status_code"] != 200:
        print(f"Error status code {data['request']['status_code']}.", file=sys.stderr)

        if "response" in data:
            if "message" in data["response"]:
                print(f"Message: {data['response']['message']}")

        if data["request"]["status_code"] >= 400:
            sys.exit(1)
        else:
            return

    if (
        "response" in data
        and "paste" in data["response"]
        and "content" in data["response"]["paste"]
    ):
        print(data["response"]["paste"]["content"], end="")
    else:
        print("No content found for the paste.")


def delete_paste(paste, username, token):
    """
    Delete a paste.

    Args:
        paste (str): The paste name (id). An string of characters (ASCII only without spaces).
        username (str): The username of the user.
        token (str): The authentification token. You can get it from <https://home.omg.lol/account>
    """
    headers = {"Authorization": f"Bearer {get_token(token)}"}
    response = requests.delete(
        f"https://{DEFAULT_DOMAIN}/address/{username}/pastebin/{paste}", headers=headers
    )
    data = response.json()

    if data["request"]["status_code"] != 200:
        print(f"Error status code {data['request']['status_code']}.", file=sys.stderr)
        if "response" in data:
            if "message" in data["response"]:
                print(data["response"]["message"], file=sys.stderr)
        if data["request"]["status_code"] >= 400:
            sys.exit(1)
        else:
            return

    if "response" in data:
        if "message" in data["response"]:
            print(data["response"]["message"])
        else:
            print("No message returned but the paste was succesfully deleted")
    else:
        print("No reponse found but the paste was succesfully deleted")


def debug_action(action, paste_name, content, username, token, public):
    """
    Print debug information about the action being performed.

    Args:
        action (str): The action being performed.
        paste_name (str): The name of the paste.
        content (str): The content of the paste.
        username (str): The username of the user.
        token (str): The authentification token. You can get it from <https://home.omg.lol/account>
        public (bool): Whether the paste is public or not.
    """
    print(f"Debug: Action = {action}")
    print(f"Paste Name: {paste_name}")
    print(f"Username: {username}")
    print(f"Bearer Token: {token}")
    print(f"Public: {public}")
    if content is not None:
        print(
            f"Content: {content[:100]}{'...' if len(content) > 100 else ''}"
        )  # Print first 100 characters of the content


def edit_paste(paste, username, token):
    """
    Edit a paste: It opens it in your default editor, then updates it on paste.lol.

    Args:
        paste (str): The paste name (id). An string of characters (ASCII only without spaces).
        username (str): The username of the user.
        token (str): The authentification token. You can get it from <https://home.omg.lol/account>
    """

    # Retrieve the token if it an external command
    token = get_token(token)

    editor = os.environ.get("EDITOR", "vim")  # that easy!
    content, is_listed = get_paste(paste, username, token)
    if content is None:
        print(f"Unable to retrieve the paste {paste}.")

        # If it's not possible to ask what to do exit
        if not sys.stdin.isatty():
            print("No input available: Aborting.")
            sys.exit(1)
        else:
            # Ask for clarification
            match input(f"Create a new paste named {paste} ? (yes/listed/no)"):
                case "yes" | "y":
                    is_listed = None
                case "liste" | "l":
                    is_listed = True
                case _:
                    print("Exiting.")
                    return

    with tempfile.NamedTemporaryFile(prefix=f"lolbin-{paste}", suffix=".tmp") as tf:
        if content:
            tf.write(content.encode("utf-8"))
            tf.flush()

        call([editor, tf.name])
        with open(tf.name, "r") as f:
            new_content = f.read()
            create_paste(
                paste=paste,
                content=new_content,
                username=username,
                token=token,
                public=is_listed,
            )


def help_message():
    print(USAGE_STRING)


def app():
    action = None
    paste_name = None
    content = None
    is_debug = False
    replace_username = False
    is_public = False
    config = get_config()

    to_pass = 0
    for i, arg in enumerate(sys.argv[1:]):
        if to_pass:
            to_pass -= 1

            continue

        match arg:
            case "--help" | "-h":
                if action is None:
                    action = "help"
                else:
                    print("Multiple actions specified")
                    sys.exit(1)

            case "--list" | "-l":
                if action is None:
                    action = "list"
                else:
                    print("Multiple actions specified")
                    sys.exit(1)

            case "--listed" | "-L" | "--public" | "-P":
                is_public = True

            case "--paste" | "-p":
                if action is None:
                    action = "paste"
                else:
                    print("Multiple actions specified")
                    sys.exit(1)

            case "--file" | "-f":
                if action is None:
                    action = "paste"
                    with open(sys.argv[i + 2]) as f:
                        content = f.read()
                    to_pass = 1
                else:
                    print("Multiple actions specified")
                    sys.exit(1)

            case "--show" | "-s":
                if action is None:
                    action = "show"

            case "--user" | "-u":
                if not replace_username:
                    replace_username = True
                    if "username" in config:
                        # NOTE: Otherwise the token can't be correct
                        config["bearer_token"] = None

                    config["username"] = sys.argv[i + 2]

                    to_pass = 1
                else:
                    print("Ambiguous username", file=sys.stderr)
                    sys.exit(1)

            case "--delete" | "-d":
                if action is None:
                    action = "delete"
                else:
                    print("Multiple actions specified")
                    sys.exit(1)

            case "--edit" | "-e":
                if action is None:
                    action = "edit"
                else:
                    print("Multiple actions specified")
                    sys.exit(1)

            case "--debug":
                is_debug = True

            case name:
                if paste_name is None:
                    paste_name = name
                else:
                    print(
                        f"Ambiguous paste name. Aborting. {name} or {paste_name}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

    if not sys.stdin.isatty():
        if content is None:
            content = sys.stdin.read()
            if action is None:
                action = "paste"
            elif action != "paste":
                print(
                    f"Content was send to lolbin but the action {action} doesn't use it.",
                    file=sys.stderr,
                )
        else:
            print("Ambiguous paste content source. Aborting.", file=sys.stderr)
            sys.exit(1)

    if action is None:
        if paste_name is None:
            action = "list"
        else:
            action = "show"

    if is_debug:
        debug_action(
            action,
            paste_name,
            content,
            config["username"],
            config["bearer_token"],
            is_public,
        )
        return

    match action:
        case "list":
            if "username" not in config:
                print("Error: No username provided.", file=sys.stderr)
                sys.exit(1)
            list_paste(
                config["username"],
                config["bearer_token"] if "bearer_token" in config else None,
                is_public,
            )
        case "paste":
            if "username" not in config:
                print("Error: No username provided.", file=sys.stderr)
                sys.exit(1)
            if "bearer_token" not in config:
                print(
                    f"Error: No token provided for the user {config['username']}.",
                    file=sys.stderr,
                )
                sys.exit(1)

            if paste_name is None:
                print("You must specify a paste name to paste.", file=sys.stderr)
                sys.exit(1)

            create_paste(
                paste_name,
                content,
                config["username"],
                config["bearer_token"],
                is_public,
            )
        case "delete":
            if paste_name is None:
                print("You must specify a paste name to delete.", file=sys.stderr)
                sys.exit(1)
            if "username" not in config:
                print("Error: No username provided.", file=sys.stderr)
                sys.exit(1)
            if "bearer_token" not in config:
                print(
                    f"Error: No token provided for the user {config['username']}.",
                    file=sys.stderr,
                )
                sys.exit(1)

            delete_paste(paste_name, config["username"], config["bearer_token"])
        case "show":
            if paste_name is None:
                print("You must specify a paste name to show.", file=sys.stderr)
                sys.exit(1)
            if "username" not in config:
                print("Error: No username provided.", file=sys.stderr)
                sys.exit(1)

            show_paste(
                paste_name,
                config["username"],
                config["bearer_token"] if "bearer_token" in config else None,
            )
        case "help":
            help_message()

        case "edit":
            if "username" not in config:
                print("Error: No username provided.", file=sys.stderr)
                sys.exit(1)
            if "bearer_token" not in config:
                print(
                    f"Error: No token provided for the user {config['username']}.",
                    file=sys.stderr,
                )
                sys.exit(1)

            if paste_name is None:
                print("You must specify a paste name to edit.", file=sys.stderr)
                sys.exit(1)
            edit_paste(paste_name, config["username"], config["bearer_token"])
        case _:
            print(f"Unknown action: {action}", file=sys.stderr)
            sys.exit(1)

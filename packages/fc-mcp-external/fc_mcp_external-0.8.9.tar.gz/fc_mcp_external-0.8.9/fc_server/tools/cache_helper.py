#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2025 NXP
#
# SPDX-License-Identifier: MIT


import argparse
import json
import os
import shelve
import sys

try:
    from fc_server.core.config import Config

    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False


def get_db_path(provided_path=None):
    """Get the database path from config or use the provided/default path."""
    # First try to get from Config if available
    if HAS_CONFIG:
        try:
            # Initialize Config if not already done
            if not hasattr(Config, "db_file"):
                fc_path = os.path.dirname(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                Config.parse(fc_path)

            config_db_path = Config.db_file
            if config_db_path and (provided_path is None or provided_path == ""):
                return config_db_path
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Warning: Failed to get DB path from Config: {exc}")

    # Use provided path or default
    if provided_path:
        return provided_path

    # Default path as fallback - use environment variable if available
    return os.environ.get("FC_DB_FILE", "/tmp/fc_server")


def check_shelve_exists(db_path):
    """Check if a shelve database exists by attempting to open it."""
    try:
        with shelve.open(db_path, flag="r") as _:
            return True
    except Exception:  # pylint: disable=broad-except
        return False


def display_shelve_content(db_path):
    """Display the contents of a shelve database file."""
    try:
        with shelve.open(db_path, flag="r") as shelf:
            if not shelf:
                print(f"Database file '{db_path}' exists but is empty.")
                return

            print(f"Contents of database file '{db_path}':")
            separator = "-" * 50
            print(separator)

            for key, value in shelf.items():
                print(f"Key: {key}")

                # Format the value for better readability
                if isinstance(value, (list, dict)):
                    formatted_value = json.dumps(value, indent=2)
                    print(f"Value: {formatted_value}")
                else:
                    print(f"Value: {value}")
                print(separator)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error opening database file: {exc}")
        sys.exit(1)


def update_shelve_entry(db_path, key, value):
    """Update a specific entry in the shelve database."""
    try:
        with shelve.open(db_path, writeback=True) as shelf:
            shelf[key] = value
            print(f"Successfully updated key '{key}' in database file " f"'{db_path}'")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error updating database file: {exc}")
        sys.exit(1)


def delete_shelve_entry(db_path, key):
    """Delete a specific entry from the shelve database."""
    try:
        with shelve.open(db_path, writeback=True) as shelf:
            if key in shelf:
                del shelf[key]
                print(
                    f"Successfully deleted key '{key}' from database file "
                    f"'{db_path}'"
                )
            else:
                print(f"Key '{key}' not found in database file '{db_path}'")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error deleting from database file: {exc}")
        sys.exit(1)


def add_resource_to_entry(db_path, key, resource):
    """Add a resource to a list entry in the shelve database."""
    try:
        with shelve.open(db_path, writeback=True) as shelf:
            if key not in shelf:
                shelf[key] = []
                print(f"Created new key '{key}' as empty list")

            current_value = shelf[key]
            if not isinstance(current_value, list):
                print(
                    f"Error: Key '{key}' is not a list. Current type: "
                    f"{type(current_value).__name__}"
                )
                sys.exit(1)

            if resource in current_value:
                print(f"Resource '{resource}' already exists in key '{key}'")
                return

            current_value.append(resource)
            shelf[key] = current_value
            print(f"Successfully added resource '{resource}' to key '{key}'")
            print(f"Updated list: {current_value}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error adding resource to database file: {exc}")
        sys.exit(1)


def remove_resource_from_entry(db_path, key, resource):
    """Remove a resource from a list entry in the shelve database."""
    try:
        with shelve.open(db_path, writeback=True) as shelf:
            if key not in shelf:
                print(f"Key '{key}' not found in database file '{db_path}'")
                return

            current_value = shelf[key]
            if not isinstance(current_value, list):
                print(
                    f"Error: Key '{key}' is not a list. Current type: "
                    f"{type(current_value).__name__}"
                )
                sys.exit(1)

            if resource not in current_value:
                print(f"Resource '{resource}' not found in key '{key}'")
                return

            current_value.remove(resource)
            shelf[key] = current_value
            print(f"Successfully removed resource '{resource}' from key " f"'{key}'")
            print(f"Updated list: {current_value}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error removing resource from database file: {exc}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Manage shelve database files",
        epilog="""
Common keys used by fc_server:
  - managed_disconnect_resources: List of resources disconnected by fc
  - managed_issue_disconnect_resources: List of resources with disconnect issues

Examples:
  %(prog)s show                    # Show all contents
  %(prog)s update managed_disconnect_resources '["device1", "device2"]'
  %(prog)s delete managed_disconnect_resources
  %(prog)s add-resource managed_disconnect_resources device3
  %(prog)s remove-resource managed_disconnect_resources device1
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Show command
    show_parser = subparsers.add_parser(
        "show", help="Display contents of a shelve database file"
    )
    show_parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to the shelve database file (optional if config is available)",
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update", help="Update an entry in the shelve database"
    )
    update_parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to the shelve database file (optional if config is available)",
    )
    update_parser.add_argument("key", help="Key to update")
    update_parser.add_argument("value", help="JSON-formatted value to set")

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete", help="Delete an entry from the shelve database"
    )
    delete_parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to the shelve database file (optional if config is available)",
    )
    delete_parser.add_argument("key", help="Key to delete")

    # Add resource command
    add_resource_parser = subparsers.add_parser(
        "add-resource", help="Add a resource to a list entry"
    )
    add_resource_parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to the shelve database file (optional if config is available)",
    )
    add_resource_parser.add_argument("key", help="Key (must be a list)")
    add_resource_parser.add_argument("resource", help="Resource to add to the list")

    # Remove resource command
    remove_resource_parser = subparsers.add_parser(
        "remove-resource", help="Remove a resource from a list entry"
    )
    remove_resource_parser.add_argument(
        "db_path",
        nargs="?",
        help="Path to the shelve database file (optional if config is available)",
    )
    remove_resource_parser.add_argument("key", help="Key (must be a list)")
    remove_resource_parser.add_argument(
        "resource", help="Resource to remove from the list"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Get the database path
    db_path = get_db_path(getattr(args, "db_path", None))

    print(f"Using database file: {db_path}")

    # Check if the database exists for show command
    if args.command == "show" and not check_shelve_exists(db_path):
        print(f"Database file '{db_path}' does not exist.")
        sys.exit(1)

    if args.command == "show":
        display_shelve_content(db_path)
    elif args.command == "update":
        try:
            value = json.loads(args.value)
            update_shelve_entry(db_path, args.key, value)
        except json.JSONDecodeError:
            print("Error: Value must be valid JSON")
            sys.exit(1)
    elif args.command == "delete":
        delete_shelve_entry(db_path, args.key)
    elif args.command == "add-resource":
        add_resource_to_entry(db_path, args.key, args.resource)
    elif args.command == "remove-resource":
        remove_resource_from_entry(db_path, args.key, args.resource)


if __name__ == "__main__":
    main()

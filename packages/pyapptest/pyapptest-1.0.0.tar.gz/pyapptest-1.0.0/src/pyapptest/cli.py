import argparse
from .manager import LibraryManager


def main():
    parser = argparse.ArgumentParser(
        prog="pyapptest",
        description="Manage and switch between fastapptest and flaskapptest"
    )

    parser.add_argument(
        "action",
        choices=["install", "uninstall", "options"],
        help="Action to perform"
    )

    parser.add_argument(
        "--lib",
        choices=["fastapptest", "flaskapptest"],
        help="Specify library for install or uninstall"
    )

    args = parser.parse_args()
    manager = LibraryManager()

    if args.action == "install":
        if args.lib:
            manager.install_library(args.lib)
        else:
            # default: install both
            manager.install_library("fastapptest")
            manager.install_library("flaskapptest")

    elif args.action == "uninstall":
        if not args.lib:
            print("❌ Please specify --lib fastapptest or --lib flaskapptest")
            return
        manager.uninstall_library(args.lib)

    elif args.action == "options":
        manager.select_active_library()

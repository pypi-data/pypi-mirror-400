from .types import _SubparserType


def add_list_command(subparsers: _SubparserType):
    list_parser = subparsers.add_parser("list", help="List items")
    list_subparsers = list_parser.add_subparsers(dest="list_command")
    list_subparsers.add_parser("projects", help="List projects")
    return list_parser

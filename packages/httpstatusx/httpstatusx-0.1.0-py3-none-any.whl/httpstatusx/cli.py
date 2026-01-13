# httpstatusx/cli.py

import argparse
from colorama import Fore, Style, init
from httpstatusx import HTTP
from httpstatusx.data import HTTP_STATUS

# Initialize colorama
init(autoreset=True)

# ---------------- COLOR HELPERS ---------------- #

def color_for_code(code: int) -> str:
    if 100 <= code < 200:
        return Fore.BLUE
    if 200 <= code < 300:
        return Fore.GREEN
    if 300 <= code < 400:
        return Fore.YELLOW
    if 400 <= code < 500:
        return Fore.RED
    if 500 <= code < 600:
        return Fore.MAGENTA
    return Fore.WHITE

# ---------------- DISPLAY HELPERS ---------------- #

def print_examples():
    print(f"""
{Style.BRIGHT}Examples:{Style.RESET_ALL}

  httpstatusx ok
  httpstatusx not_found
  httpstatusx 404

  httpstatusx --list
  httpstatusx --list 200
  httpstatusx --list 400
""")

def print_all_categories():
    print(f"""
{Style.BRIGHT}HTTP Status Categories:{Style.RESET_ALL}

{Fore.BLUE}100{Style.RESET_ALL} → Informational
{Fore.GREEN}200{Style.RESET_ALL} → Success
{Fore.YELLOW}300{Style.RESET_ALL} → Redirection
{Fore.RED}400{Style.RESET_ALL} → Client Error
{Fore.MAGENTA}500{Style.RESET_ALL} → Server Error
""")

def print_category(base: int):
    print(
        f"\n{Style.BRIGHT}{base}xx HTTP Status Codes{Style.RESET_ALL}\n"
    )

    for name, code in HTTP_STATUS.items():
        if base <= code < base + 100:
            color = color_for_code(code)
            print(
                f"{color}{code:<5}{Style.RESET_ALL} "
                f"{Fore.CYAN}{name}{Style.RESET_ALL}"
            )

# ---------------- MAIN CLI ---------------- #

def main():
    parser = argparse.ArgumentParser(
        description="Semantic, color-coded HTTP status lookup",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="HTTP status name (not_found) or code (404)"
    )

    parser.add_argument(
        "--list",
        nargs="?",
        const="all",
        help="List HTTP status categories or a specific category (100/200/300/400/500)"
    )

    parser.add_argument(
        "--examples",
        action="store_true",
        help="Show usage examples"
    )

    args = parser.parse_args()

    # ----- EXAMPLES ----- #
    if args.examples:
        print_examples()
        return

    # ----- LIST MODE ----- #
    if args.list is not None:
        if args.list == "all":
            print_all_categories()
            return

        if args.list.isdigit():
            base = int(args.list)
            if base not in (100, 200, 300, 400, 500):
                print(
                    f"{Fore.RED}Error:{Style.RESET_ALL} "
                    "Use one of 100, 200, 300, 400, 500"
                )
                return

            print_category(base)
            return

        print(
            f"{Fore.RED}Error:{Style.RESET_ALL} "
            "Invalid --list argument"
        )
        return

    # ----- NORMAL LOOKUP MODE ----- #
    if not args.query:
        parser.print_help()
        return

    q = args.query

    try:
        # Numeric lookup
        if q.isdigit():
            code = int(q)
            name = HTTP.name(code)
            category = HTTP.category(code)
            color = color_for_code(code)

            print(
                f"{color}{code}{Style.RESET_ALL} → "
                f"{Fore.CYAN}{name}{Style.RESET_ALL} "
                f"({category})"
            )
            return

        # Name lookup
        code = HTTP[q]
        color = color_for_code(code)

        print(
            f"{Fore.CYAN}{q}{Style.RESET_ALL} → "
            f"{color}{code}{Style.RESET_ALL}"
        )

    except Exception as e:
        print(
            f"{Fore.RED}{Style.BRIGHT}Error:{Style.RESET_ALL} {e}"
        )

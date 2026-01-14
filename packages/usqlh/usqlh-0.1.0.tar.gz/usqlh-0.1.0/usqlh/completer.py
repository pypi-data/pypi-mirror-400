import readline
from typing import List, Optional


class AliasCompleter:
    def __init__(self, aliases: List[str]):
        self.aliases = sorted(aliases)
        self.matches: List[str] = []

    def complete(self, text: str, state: int) -> Optional[str]:
        if state == 0:
            if text:
                self.matches = [a for a in self.aliases if a.startswith(text)]
            else:
                self.matches = self.aliases[:]

        if state < len(self.matches):
            return self.matches[state]
        return None


def input_with_completion(prompt: str, aliases: List[str], default: str = "") -> str:
    completer = AliasCompleter(aliases)

    old_completer = readline.get_completer()
    old_delims = readline.get_completer_delims()

    try:
        readline.set_completer(completer.complete)
        readline.set_completer_delims("")
        readline.parse_and_bind("tab: complete")

        # macOS uses libedit which needs different binding
        if "libedit" in readline.__doc__ if readline.__doc__ else False:
            readline.parse_and_bind("bind ^I rl_complete")

        prompt_text = f"{prompt} [{default}]: " if default else f"{prompt}: "

        if aliases:
            print(f"  (Tab to complete, {len(aliases)} aliases available)")

        value = input(prompt_text)
        return value if value else default
    finally:
        readline.set_completer(old_completer)
        readline.set_completer_delims(old_delims)


def select_alias(prompt: str, aliases: List[str]) -> Optional[str]:
    if not aliases:
        print("No connections available.")
        return None

    return input_with_completion(prompt, aliases)

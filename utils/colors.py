"""Códigos ANSI para colorir o terminal."""

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def success(text):
    return f"{GREEN}{text}{RESET}"

def error(text):
    return f"{RED}{text}{RESET}"

def warn(text):
    return f"{YELLOW}{text}{RESET}"

def info(text):
    return f"{CYAN}{text}{RESET}"

def bold(text):
    return f"{BOLD}{text}{RESET}"

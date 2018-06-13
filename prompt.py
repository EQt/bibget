import sys


def ask(prompt):
    """
    Ask the user `prompt` and return the answer
    """
    print('%s: ' % prompt, end='')
    sys.stdout.flush()
    return sys.stdin.readline().strip()


import os

def clear():
    if os.name == 'posix':
        os.system('clear')
    elif os.name == 'nt':
        os.system('cls')
    else:
        print(f"Clean Terminus does not support your OS: {os.name}")

def clean():
    clear()

if __name__ == "__main__":
    clear()
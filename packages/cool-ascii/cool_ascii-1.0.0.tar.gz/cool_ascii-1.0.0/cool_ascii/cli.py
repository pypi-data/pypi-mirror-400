import pyfiglet
from termcolor import colored
import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    clear_screen()

    # ASCII Banner
    font = pyfiglet.Figlet(font='standard')
    banner = font.renderText('2BITDEV')
    print(colored(banner, 'white', attrs=['bold']))

    # Project Info
    print(colored("        Project Version: v1.0.0", "white"))
    print(colored("        Project Dev: Thanaphat", "white"))
    print(colored("        Telegram: https://t.me/----", "cyan"))

    print("\n---- Main Menu ----\n")
    print("1 - Start")
    print("2 - Exit")
    print("\n>>> ", end="")

def start_program():
    clear_screen()

    heart = r"""
      ██████   ██████
    █████████ █████████
   █████████████████████
   █████████████████████
    ███████████████████
      ███████████████
        ███████████
          ███████
            ███
             █
    """

    print(colored(heart, "black", attrs=["bold"]))
    input("\nPress Enter to return menu...")

def main():
    while True:
        show_menu()
        choice = input().strip()

        if choice == "1":
            start_program()
        elif choice == "2":
            print(colored("\n[!] Exiting...", "yellow"))
            time.sleep(0.5)
            sys.exit()
        else:
            print(colored("\n[!] Invalid choice", "red"))
            time.sleep(1)

if __name__ == "__main__":
    main()

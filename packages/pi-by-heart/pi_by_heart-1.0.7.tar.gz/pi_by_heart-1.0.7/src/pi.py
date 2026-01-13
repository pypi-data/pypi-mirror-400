import os
import time
import pyfiglet
import mpmath


TITLE_TEXT = "The Pi Game!"


def _calculate_pi(num_digits):
    mpmath.mp.dps = num_digits + 2  # Set the precision to required number of digits

    # Return pi as a string with desired precision
    return str(mpmath.pi)[:-1]


def add_space_every_four_chars(input_string):
    # TODO: not sure if this the best way to do so
    result = ""
    for i in range(0, len(input_string), 4):
        result += input_string[i : i + 4] + " "
    return result.strip()


def learn_digits(num_digits, delay=None):
    pi_digits = _calculate_pi(num_digits)
    pi_after_decimal_point = add_space_every_four_chars(pi_digits[2:])
    pi_digits = pi_digits[:2] + " " + pi_after_decimal_point
    if delay:
        for digit in pi_digits:
            print(digit, end="", flush=True)
            time.sleep(delay / 1000)
    else:
        print(" ".join(pi_digits))

    print()


def score(corrections):
    # TODO: find a better scoring system :)
    hits_list = [int(c == " ") for c in corrections[2:]]
    base = 1
    multi = 1
    return sum(
        i**multi * h * base**i for i, h in enumerate(hits_list, start=2)
    ) + int(corrections[0] == " ")


def check(num):
    length_after_point = len(num) - 2
    true_pi = _calculate_pi(length_after_point)
    checked_digits = ""
    correction = ""
    for input_d, true_d in zip(num, true_pi):
        if input_d == true_d:
            checked_digits += input_d
            correction += " "
        else:
            checked_digits += "\033[91m" + input_d + "\033[0m"
            correction += true_d

    print("Enter the digits you know:")
    print(checked_digits)
    print(correction)

    correct_count = sum([1 for d in correction if d == " "])
    print(f"\nYou got {correct_count - 1} out of {len(num) - 1} right!")
    print(f"Score: {score(correction)}")


def test():
    os.system("cls" if os.name == "nt" else "clear")
    print(pyfiglet.figlet_format(TITLE_TEXT, font="small"))
    user_input = input("Enter the digits you know:\n")
    os.system("cls" if os.name == "nt" else "clear")
    print(pyfiglet.figlet_format(TITLE_TEXT, font="small"))
    check(user_input)


def learn():
    os.system("cls" if os.name == "nt" else "clear")
    print(pyfiglet.figlet_format(TITLE_TEXT, font="small"))
    num_digits = int(input("Enter the number of digits you want to learn: "))
    input_delay = input(
        "Choose the amount of delay between digits' appearance or press Enter to set it to 0:\n"
    )
    if input_delay == "":
        delay = 0
    else:
        delay = int(input_delay)

    learn_digits(num_digits, delay)


def help_info():
    print(
        """
Welcome to The Pi Game!

In this game, you can choose to learn or test your knowledge of the digits of Pi.
To choose a mode, enter the corresponding number:

1. Learn: View a specified number of digits of Pi.
2. Test: Test your knowledge by testing the digits of Pi you remember.

You can exit the game at any time by choosing the 'Exit' option.
    """
    )


def main():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(pyfiglet.figlet_format(TITLE_TEXT, font="small"))
        print("Choose mode:")
        print("1. Learn")
        print("2. Test")
        print("3. Help")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1" or choice.lower() == "learn":
            learn()
        elif choice == "2" or choice.lower() == "test":
            test()
        elif choice == "3" or choice.lower() == "help":
            help_info()
        elif choice == "4" or choice.lower() == "exit" or choice == "q":
            break
        else:
            print("Invalid choice. Please enter a valid option.")

        input("Press Enter to continue...")


if __name__ == "__main__":
    main()

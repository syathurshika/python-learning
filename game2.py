import random

print("=== Guess the Number ===")

secret_number = random.randint(1, 100)
attempts = 0

while True:
    guess = int(input("Enter your guess (1-100): "))
    attempts += 1

    if guess < secret_number:
        print("Too low!")
    elif guess > secret_number:
        print("Too high!")
    else:
        print(f"Correct! You guessed it in {attempts} attempts.")
        break
    
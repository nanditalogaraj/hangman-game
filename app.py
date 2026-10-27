
import csv
import random
import os
import uuid

from flask import Flask, render_template, request, redirect, session

# Read the words from WordList.csv
with open('WordList.csv', 'r') as file:
    reader = csv.reader(file)
    words = [row[0].lower() for row in reader if row]

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-me')

# Store a separate game for each visitor
games = {}


def start_new_game():
    return {
        'secret_word': random.choice(words),
        'lives': 10,
        'guessed_letters': [],
        'message': ''
    }


def get_game():
    # Give each browser its own game ID
    if 'game_id' not in session:
        session['game_id'] = str(uuid.uuid4())

    game_id = session['game_id']

    # Start a game if this visitor doesn't have one yet
    if game_id not in games:
        games[game_id] = start_new_game()

    return games[game_id]


@app.route('/', methods=['GET', 'POST'])
def home():
    game = get_game()

    secret_word = game['secret_word']
    lives = game['lives']
    guessed_letters = game['guessed_letters']
    message = game['message']

    if request.method == 'POST':
        guess = request.form['guess'].lower()

        if not guess.isalpha():
            message = "Please enter a letter."

        elif guess in guessed_letters:
            message = "You already guessed that letter."

        elif lives == 0 or all(
            letter in guessed_letters or letter in " -"
            for letter in secret_word
        ):
            message = "Game over! Please start a new game."

        else:
            guessed_letters.append(guess)

            if guess in secret_word:
                message = "Correct guess!"
            else:
                lives -= 1
                message = "Incorrect guess!"

            # Check whether the player has won
            if all(
                letter in guessed_letters or letter in " -"
                for letter in secret_word
            ):
                message = "You won! The word was " + secret_word

            # Check whether the player has lost
            elif lives == 0:
                message = "Game over! The word was " + secret_word

        # Save this visitor's updated game
        game['lives'] = lives
        game['guessed_letters'] = guessed_letters
        game['message'] = message

    # Display guessed letters and hide the others
    spaces = " ".join(
        letter if letter in guessed_letters or letter in " -"
        else "_"
        for letter in secret_word
    )

    display_letters = [
        letter if letter in guessed_letters or not letter.isalpha()
        else "_"
        for letter in secret_word
    ]

    return render_template(
        'index.html',
        spaces=spaces,
        guessed_letters=guessed_letters,
        lives=lives,
        message=message,
        display_letters=display_letters
    )


@app.route('/new-game', methods=['POST'])
def new_game():
    game = get_game()

    # Reset only this visitor's game
    game.update(start_new_game())

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

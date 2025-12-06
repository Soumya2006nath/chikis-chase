from flask import Flask, render_template, jsonify
import subprocess
import sys

app = Flask(__name__, template_folder='templates')

game_process = None  # track the game process


@app.route('/')
def home():
    # This loads templates/index.html
    return render_template('index.html')


@app.route('/start_game', methods=['POST'])
def start_game():
    global game_process

    # If game is not running, start it
    if game_process is None or game_process.poll() is not None:
        # Make sure 'game.py' is your pygame file name
        game_process = subprocess.Popen([sys.executable, 'game.py'])
        return jsonify({'status': 'started'})
    else:
        return jsonify({'status': 'already_running'})


if __name__ == '__main__':
    import os
    print("Flask running from folder:", os.getcwd())
    app.run(debug=True)

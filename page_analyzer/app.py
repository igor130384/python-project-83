import os

from flask import Flask
from flask import render_template

# Это callable WSGI-приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def hello_world():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('https://6starvote.me/')

@app.route('/page')
def index():
    return redirect('https://6starvote.me/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)

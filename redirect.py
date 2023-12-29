from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
@app.route('/page')
def index():
    return redirect('http://47.120.33.76:9876')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)

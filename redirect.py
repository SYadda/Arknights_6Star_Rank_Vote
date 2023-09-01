from flask import Flask, redirect
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

@app.route('/page', methods=['GET'])
@cross_origin()
def page():
    return redirect(location='http://114.132.188.253:9876/page', code=301)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)

from flask import Flask, send_file
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/a_txt', methods=['GET'])
@cross_origin()
def get_a_txt():
    return send_file('win_score.pickle', as_attachment=True)
    # return send_file('lose_score.pickle', as_attachment=True)
    # return send_file('ip_ban.pickle', as_attachment=True)
    # return send_file('ip_dict.pickle', as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
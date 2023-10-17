# -*- coding: utf-8 -*-
import pandas as pd
from flask import Flask, redirect, url_for, render_template, request, jsonify, send_file
from flask_cors import CORS, cross_origin
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

if app.debug:
    from config import DevelopmentConfig as Config
else:
    from config import ProductionConfig as Config

dict_name = Config.DICT_NAME
lst_name = list(dict_name.keys())
df = pd.read_csv('final_data.csv', index_col=0)

@app.route('/view_final_order', methods=['GET'])
@cross_origin()
def view_final_order():
    weight = int(request.args.get("weight")) or 62
    df['weight'] = df['ip_vote_num'].map(lambda _: 1 if _ <= weight else weight / _)

    win_count = [sum(_[1]['weight']) for _ in df.groupby('win_id')]
    lose_count = [sum(_[1]['weight']) for _ in df.groupby('lose_id')]
    net_win_score = [win_count[_] - lose_count[_] for _ in range(len(win_count))]
    win_rate = [win_count[_] / (win_count[_] + lose_count[_]) * 100 for _ in range(len(win_count))]

    dict_score = dict(zip(zip(lst_name, net_win_score), win_rate))

    final_n_s, final_rate = zip(*sorted(dict_score.items(), key=lambda _: -_[1]))
    final_name, final_score = zip(*final_n_s)
    final_score = ['%.1f'%_ for _ in final_score]
    final_rate = ['%.1f'%_ + ' %' for _ in final_rate]
    return jsonify({'name': final_name, 'rate': final_rate, 'score': final_score})


@app.route('/')
@cross_origin()
def index():
    return redirect(url_for('page'))


@app.route('/page', methods=['GET'])
@cross_origin()
def page():
    DATA_DICT = {'SERVER_IP': Config.SERVER_IP, 'SERVER_PORT': Config.SERVER_PORT, 'DICT_PIC_URL': Config.DICT_PIC_URL}
    return render_template('page.html', data_dict = DATA_DICT)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
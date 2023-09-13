# -*- coding: utf-8 -*-

import random, os, pickle
from flask import Flask, redirect, url_for, render_template, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

if app.debug:
    from config import DevelopmentConfig as Config
else:
    from config import ProductionConfig as Config

dict_name = Config.DICT_NAME
lst_name = list(dict_name.keys())
len_lst_name_1 = len(lst_name) - 1
set_code = set()


@app.route('/new_operator_compare', methods=['GET'])
@cross_origin()
def new_operator_compare():
    with open('list/win_score.pickle', 'rb') as f:
        lst_win_score = pickle.load(f)
    with open('list/lose_score.pickle', 'rb') as f:
        lst_lose_score = pickle.load(f)

    lst_count = [lst_win_score[i] + lst_lose_score[i] for i in range(len(lst_win_score))]
    max_count = max(lst_count) + 1
    weights = [max_count - count for count in lst_count]
    a, b = random.choices(range(len(weights)), weights, k=2)
    if a == b:
        b = (b + 1) % len(weights)

    return compare(a, b)


@app.route('/new_compare', methods=['GET'])
@cross_origin()
def new_compare():
    a = random.randint(0, len_lst_name_1)
    b = random.randint(0, len_lst_name_1)
    while a == b:
        b = random.randint(0, len_lst_name_1)
    
    return compare(a, b)


@app.route('/save_score', methods=['POST']) 
@cross_origin()
def save_score():
    if verify():
        with open('list/win_score.pickle', 'rb') as f:
            lst_win_score = pickle.load(f)
        with open('list/lose_score.pickle', 'rb') as f:
            lst_lose_score = pickle.load(f)
        
        lst_win_score[dict_name[request.args.get('win_name')]] += 1
        lst_lose_score[dict_name[request.args.get('lose_name')]] += 1

        with open('list/win_score.pickle', 'wb') as f:
            pickle.dump(lst_win_score, f)
        with open('list/lose_score.pickle', 'wb') as f:
            pickle.dump(lst_lose_score, f)

    return 'success'


@app.route('/view_final_order', methods=['GET'])
@cross_origin()
def view_final_order():
    with open('list/win_score.pickle', 'rb') as f:
        lst_win_score = pickle.load(f)
    with open('list/lose_score.pickle', 'rb') as f:
        lst_lose_score = pickle.load(f)

    lst_rate = [100 * lst_win_score[_] / (lst_win_score[_] + lst_lose_score[_]) for _ in range(len(lst_win_score))]
    lst_score = [lst_win_score[_] - lst_lose_score[_] for _ in range(len(lst_win_score))]
    dict_score = dict(zip(zip(lst_name, lst_score), lst_rate))

    final_n_s, final_rate = zip(*sorted(dict_score.items(), key=lambda _: -_[1]))
    final_name, final_score = zip(*final_n_s)
    final_rate = ['%.1f'%_ + ' %' for _ in final_rate]
    return jsonify({'name': final_name, 'rate': final_rate, 'score': final_score, 'count': '已收集数据 ' + str(sum(lst_win_score)) + ' 条'})


@app.route('/')
@cross_origin()
def index():
    return redirect(url_for('page'))


@app.route('/page', methods=['GET'])
@cross_origin()
def page():
    DATA_DICT = {'SERVER_IP': Config.SERVER_IP, 'SERVER_PORT': Config.SERVER_PORT, 'DICT_PIC_URL': Config.DICT_PIC_URL}

    return render_template('page.html', data_dict = DATA_DICT)


def compare(a:int, b:int):
    global set_code
    code_random = random.randint(100, 799)
    code = code_random + a + b
    set_code.add(code)

    return lst_name[a] + ' ' + lst_name[b] + ' ' + str(code_random)

def verify():
    global set_code
    code = int(request.args.get('code')) + dict_name[request.args.get('win_name')] + dict_name[request.args.get('lose_name')]
    if code in set_code:
        set_code.remove(code)
        return True
    else:
        return False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
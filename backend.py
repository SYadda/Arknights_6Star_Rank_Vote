# -*- coding: utf-8 -*-

import random, pickle
from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
# app.debug = True

if app.debug:
    from config import DevelopmentConfig as Config
else:
    from config import ProductionConfig as Config

dict_name = Config.DICT_NAME
lst_name = list(dict_name.keys())
len_lst_name_1 = len(lst_name) - 1
set_code = set()


@app.route('/new_compare', methods=['GET'])
@cross_origin()
def new_compare():
    # 由于本次投票开放时间不长，参与投票的六星干员从头到尾固定。
    # 为提升性能，取消了“之前抽取次数少的干员优先抽取”的功能，该功能可在1.0.4版本中找到。
    a = random.randint(0, len_lst_name_1)
    b = random.randint(0, len_lst_name_1)
    while a == b:
        b = random.randint(0, len_lst_name_1)

    return compare(a, b)


@app.route('/save_score', methods=['POST']) 
@cross_origin()
def save_score():
     # code不对，请求非法，verify() == 0
     # code对，此ip投票 <= 50 次，verify() == 1
     # code对，此ip投票 > 50 次，每票权重降为0.01票，verify() == 0.01
    vrf = verify_code()
    if vrf:
        with open('list/win_score.pickle', 'rb') as f:
            lst_win_score = pickle.load(f)
        with open('list/lose_score.pickle', 'rb') as f:
            lst_lose_score = pickle.load(f)
        
        lst_win_score[dict_name[request.args.get('win_name')]] += vrf
        lst_lose_score[dict_name[request.args.get('lose_name')]] += vrf

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
    final_score = ['%.2f'%_ for _ in final_score]
    final_rate = ['%.1f'%_ + ' %' for _ in final_rate]
    return jsonify({'name': final_name, 'rate': final_rate, 'score': final_score, 'count': '已收集数据 ' + '%.2f'%(sum(lst_win_score)) + ' 条'})


@app.route('/', methods=['GET'])
@cross_origin()
def page():
    # # DATA_DICT = {'SERVER_IP': Config.SERVER_IP, 'SERVER_PORT': Config.SERVER_PORT, 'DICT_PIC_URL': Config.DICT_PIC_URL}
    # DATA_DICT = {'SERVER_ADDRESS': Config.SERVER_ADDRESS, 'DICT_PIC_URL': Config.DICT_PIC_URL}

    # return render_template('page.html', data_dict = DATA_DICT)

    return redirect('https://vote.ltsc.vip', code=302)


def compare(a:int, b:int):
    global set_code
    code_random = random.randint(100, 799)
    code = code_random + a + b
    set_code.add(code)

    return lst_name[a] + ' ' + lst_name[b] + ' ' + str(code_random)

def get_client_ip():
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        client_ip = real_ip.split(",")[0]
    except:
        try:
            client_ip = request.META['REMOTE_ADDR']
        except:
            client_ip = request.remote_addr
    return client_ip

def verify_ip():
    # code不对，请求非法，verify() == 0
    # code对，此ip投票 <= 50 次，verify() == 1
    # code对，此ip投票 > 50 次，每票权重降为0.01票，verify() == 0.01
    client_ip = get_client_ip()
    with open('ip/ip_ban.pickle', 'rb') as f:
        ip_ban = pickle.load(f)
    if client_ip in ip_ban:
        return 0.01

    with open('ip/ip_dict.pickle', 'rb') as f:
        ip_dict = pickle.load(f)
    if not client_ip in ip_dict:
        ip_dict[client_ip] = 0

    ip_dict[client_ip] += 1

    if ip_dict[client_ip] > 50:
        del ip_dict[client_ip]
        ip_ban.add(client_ip)

        with open('ip/ip_dict.pickle', 'wb') as f:
            pickle.dump(ip_dict, f)
        with open('ip/ip_ban.pickle', 'wb') as f:
            pickle.dump(ip_ban, f)
        return 0.01
    else:
        with open('ip/ip_dict.pickle', 'wb') as f:
            pickle.dump(ip_dict, f)
        return 1

def verify_code():
    # code不对，请求非法，verify() == 0
    # code对，此ip投票 <= 50 次，verify() == 1
    # code对，此ip投票 > 50 次，每票权重降为0.01票，verify() == 0.01
    global set_code
    code = int(request.args.get('code')) + dict_name[request.args.get('win_name')] + dict_name[request.args.get('lose_name')]
    if code in set_code:
        set_code.remove(code)
        return verify_ip()
    else:
        return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
import random
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

with open('list/name.txt', 'r', encoding='utf8') as f: # 读取干员列表
    lst_name = f.read().split('\n')
    len_lst_name_1 = len(lst_name) - 1


@app.route('/new_compare', methods=['GET'])
@cross_origin()
def new_compare():
    a = random.randint(0, len_lst_name_1)
    b = random.randint(0, len_lst_name_1)
    while a == b:
        b = random.randint(0, len_lst_name_1)
    return lst_name[a] + ' ' + lst_name[b]


@app.route('/save_score', methods=['POST']) 
@cross_origin()
def save_score():
    with open('list/win_record.txt', 'a', encoding='utf8') as f:
        f.write(request.args.get('win_name') + '\n')
    with open('list/lose_record.txt', 'a', encoding='utf8') as f:
        f.write(request.args.get('lose_name') + '\n')
    return 'success'


@app.route('/view_final_order', methods=['GET'])
@cross_origin()
def view_final_order():
    with open('list/win_record.txt', 'r', encoding='utf8') as f:
        lst_win_record = f.read().strip().split('\n')
    with open('list/lose_record.txt', 'r', encoding='utf8') as f:
        lst_lose_record = f.read().strip().split('\n')

    dict_count = {_: 0 for _ in lst_name}

    for _ in lst_win_record:
        dict_count[_] = dict_count[_] + 1
    for _ in lst_lose_record:
        dict_count[_] = dict_count[_] - 1

    final_name, final_score = zip(*sorted(dict_count.items(), key=lambda _: -_[1]))
    return jsonify({'name': final_name, 'score': final_score, 'count': '已收集数据 ' + str(len(lst_win_record)) + ' 条'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876, debug=True)
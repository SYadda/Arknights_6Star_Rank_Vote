# -*- coding: utf-8 -*-
# TODO: print -> app.logger / loguru
import hashlib
import hmac
import random, pickle
import time
import json
from lzpy import LZString
from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_cors import CORS, cross_origin
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from orm import MemoryDB, Archive, DB_Init, dump_vote_records
from utils import ThreadSafeOrderedDict, get_client_ip
mem_db = DB_Init()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
# app.debug = True

if app.debug:
    from config import DevelopmentConfig as Config
else:
    from config import ProductionConfig as Config


operators_id_dict = Config.DICT_NAME
operators_id_dict_length = len(operators_id_dict)

lst_name = list(operators_id_dict.keys())
len_lst_name_1 = len(lst_name) - 1
set_code = set()

# 创建后台调度器实例
scheduler = BackgroundScheduler()

# WARNING: 投票数据安全性不能保证，在进行写入数据库前不能确保数据的安全
# 如果mem_db 非空，那么将mem_db的内容更新到数据库中
# TODO: Lock -> mq
def _process_score(id, scores, locks):
    # with locks[id]: # 不需要强一致性
    tmp_val = scores[id]
    # ...
    if tmp_val != 0:
        return (tmp_val, id)
    return None

def _process_scores_concurrently(scores, locks):
    result_list = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(_process_score, id, scores, locks) for id in range(len(locks))]
        for future in futures:
            result = future.result()
            if result is not None:
                result_list.append(result)
    return result_list

# 添加作业到调度器，每隔Config.OPERATORS_VOTE_RECORDS_DB_DUMP_INTERVAL分钟执行一次Memory_DB_Dump函数
# 持久化投票分数到OPERATORS_VOTE_RECORDS_DB
@scheduler.scheduled_job('interval', minutes=Config.OPERATORS_VOTE_RECORDS_DB_DUMP_INTERVAL)
def Memory_DB_Dump():
    global mem_db
    win_list =  _process_scores_concurrently(mem_db.score_win, mem_db.lock_score_win)
    lose_list = _process_scores_concurrently(mem_db.score_lose, mem_db.lock_score_lose)
    app.logger.info("dump_vote_records start.")
    dump_vote_records(win_list, lose_list)
    app.logger.info("dump_vote_records fin.")

@app.route('/new_compare', methods=['POST'])
@cross_origin()
def new_compare():
    # 由于本次投票开放时间不长，参与投票的六星干员从头到尾固定。
    # 为提升性能，取消了“之前抽取次数少的干员优先抽取”的功能，该功能可在1.0.4版本中找到。
    a = random.randint(0, len_lst_name_1)
    b = random.randint(0, len_lst_name_1)
    while a == b:
        b = random.randint(0, len_lst_name_1)
    result = compare(a, b)
    return result


@app.route('/save_score', methods=['POST']) 
@cross_origin()
def save_score():
     # code不对，请求非法，verify() == 0
     # code对，此ip投票 <= 50 次，verify() == 1
     # code对，此ip投票 > 50 次，每票权重降为0.01票，verify() == 0.01
    win_name = request.args.get('win_name')
    lose_name = request.args.get('lose_name')
    code = request.args.get('code')
    if not win_name or not lose_name or not code:
        return '', 400
    if win_name not in operators_id_dict or lose_name not in operators_id_dict:
        return '', 400
    vrf = verify_code(code, win_name, lose_name)
    if vrf:
        win_operator_id = operators_id_dict[win_name]
        lose_operator_id = operators_id_dict[lose_name]
        with mem_db.lock_score_win[win_operator_id]:
            mem_db.score_win[win_operator_id] += vrf
        with mem_db.lock_score_lose[lose_operator_id]:
            mem_db.score_lose[lose_operator_id] += vrf
    return 'success'

@app.route('/view_final_order', methods=['GET'])
@cross_origin()
def view_final_order():
    lst_win_score = list(mem_db.score_win.values())
    lst_lose_score = list(mem_db.score_lose.values())
    
    lst_rate = [100 * lst_win_score[_] / (lst_win_score[_] + lst_lose_score[_]) for _ in range(len(lst_win_score))]
    lst_score = [lst_win_score[_] - lst_lose_score[_] for _ in range(len(lst_win_score))]
    dict_score = dict(zip(zip(lst_name, lst_score), lst_rate))

    final_n_s, final_rate = zip(*sorted(dict_score.items(), key=lambda _: -_[1]))
    final_name, final_score = zip(*final_n_s)
    final_score = ['%.2f'%_ for _ in final_score]
    final_rate = ['%.1f'%_ + ' %' for _ in final_rate]
    return jsonify({'name': final_name, 'rate': final_rate, 'score': final_score, 'count': '已收集数据 ' + '%.2f'%(sum(lst_win_score)) + ' 条'})

# 页面
if app.debug:
    # 为了兼容历史版本
    @app.route('/origin', methods=['GET'])
    @cross_origin()
    def page_origin():
        return render_template('page.html')

    @app.route('/', methods=['GET'])
    @cross_origin()
    def page():
        return render_template('page.html')
else:
    @app.route('/', methods=['GET'])
    @cross_origin()
    def page():
        return redirect('https://vote.ltsc.vip', code=302)


@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
    data = request.get_json()
    key = data.get('key')
    result = data.get('data')
    vote_times = int(data.get('vote_times'))
    ip = get_client_ip()
    is_create = False
    if not result:
        return jsonify({'error': 'result is required'})
    if not key:
        is_create = True
        timestamp = str(time.time())
        key = hmac.new(ip.encode(), timestamp.encode(), hashlib.sha1).hexdigest()
    result = LZString.decompressFromUTF16(result)
    archive = Archive(key = key, data = result, ip = ip, vote_times = vote_times)
    archive.save(force_insert=is_create)
    return jsonify({'key': key, "updated_at": int(archive.updated_at.timestamp())}), 200

@app.route('/sync', methods=['GET'])
@cross_origin()
def sync():
    key = request.args.get('key')
    if not key:
        return jsonify({'error': '未填写秘钥'})
    if len(key) != 40:
        return jsonify({'error': '秘钥长度不合法'})
    try:
        archive = Archive.get(Archive.key == key)
    except Archive.DoesNotExist:
        return jsonify({'error': '秘钥不存在'})
    result = LZString.compressToUTF16(archive.data)
    return jsonify({'data': result, "vote_times": archive.vote_times, "updated_at": archive.updated_at})

# 流量控制返回结果
@app.errorhandler(429)
def handle_rate_limit_exceeded(e):
    return jsonify({"error": "请求频率超过限制", 'code':400}), 200

def compare(a:int, b:int):
    # 存在一致性问题，仍然不确保code_random会不会撞
    code_random = uuid.uuid4().int
    code = code_random + a + b
    set_code.add(code)

    return lst_name[a] + ' ' + lst_name[b] + ' ' + str(code_random)

def get_client_ip():
    try:
        real_ip = request.headers.get('X_FORWARDED_FOR', type=str)
        client_ip = real_ip.split(",")[0]
    except:
        try:
            client_ip = request.headers.get('X-Real-IP', type=str)
        except:
            client_ip = request.remote_addr
    return client_ip

def verify_ip():
    # code不对，请求非法，verify() == 0
    # code对，此ip投票 <= 50 次，verify() == 1
    # code对，此ip投票 > 50 次，每票权重降为0.01票，verify() == 0.01
    # ...存在严重的一致性问题
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

def verify_code(code, win_name, lose_name):
    # code不对，请求非法，verify() == 0
    # code对，此ip投票 <= 50 次，verify() == 1
    # code对，此ip投票 > 50 次，每票权重降为0.01票，verify() == 0.01
    global set_code
    code = int(code) + operators_id_dict[win_name] + operators_id_dict[lose_name]
    if code in set_code:
        set_code.remove(code)
        return verify_ip()
    else:
        return 0

# 启动调度器
scheduler.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876)
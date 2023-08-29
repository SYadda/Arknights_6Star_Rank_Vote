import random
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)

lst_name = ['纯烬艾雅法拉', '琳琅诗怀雅', '提丰', '圣约送葬人', '缪尔赛思', '霍尔海雅', '淬羽赫默', '伊内丝', '麒麟X夜刀', '仇白', '重岳', '林', '焰影苇草', '缄默德克萨斯', '斥罪', '伺夜', '白铁', '玛恩纳', '百炼嘉维尔', '鸿雪', '多萝西', '黑键', '归溟幽灵鲨', '艾丽妮', '流明', '号角', '菲亚梅塔', '澄闪', '令', '老鲤', '灵知', '耀骑士临光', '焰尾', '远牙', '琴柳', '假日威龙陈', '水月', '帕拉斯', '卡涅利安', '浊心斯卡蒂', '凯尔希', '歌蕾蒂娅', '异客', '灰烬', '夕', '嵯峨', '空弦', '山', '迷迭香', '泥岩', '瑕光', '史尔特尔', '森蚺', '棘刺', '铃兰', '早露', 'W', '温蒂', '傀影', '风笛', '刻俄柏', '年', '阿', '煌', '莫斯提马', '麦哲伦', '赫拉格', '黑', '陈', '斯卡蒂', '银灰', '塞雷娅', '星熊', '夜莺', '闪灵', '安洁莉娜', '艾雅法拉', '伊芙利特', '推进之王', '能天使']
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

@app.route('/page', methods=['GET'])
@cross_origin()
def page():
    return render_template('/page.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9876, debug=True)
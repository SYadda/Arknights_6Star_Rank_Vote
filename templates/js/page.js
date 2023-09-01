var code = "000";

const dic_pic_url = {
    '纯烬艾雅法拉': 'https://prts.wiki/images/b/bd/半身像_纯烬艾雅法拉_1.png',
    '琳琅诗怀雅': 'https://prts.wiki/images/9/99/半身像_琳琅诗怀雅_1.png',
    '提丰': 'https://prts.wiki/images/5/51/半身像_提丰_1.png',
    '圣约送葬人': 'https://prts.wiki/images/7/71/半身像_圣约送葬人_1.png',
    '缪尔赛思': 'https://prts.wiki/images/4/4a/半身像_缪尔赛思_1.png',
    '霍尔海雅': 'https://prts.wiki/images/5/5a/半身像_霍尔海雅_1.png',
    '淬羽赫默': 'https://prts.wiki/images/5/54/半身像_淬羽赫默_1.png',
    '伊内丝': 'https://prts.wiki/images/5/59/半身像_伊内丝_1.png',
    '麒麟R夜刀': 'https://prts.wiki/images/6/66/半身像_麒麟X夜刀_1.png',
    '仇白': 'https://prts.wiki/images/4/40/半身像_仇白_1.png',
    '重岳': 'https://prts.wiki/images/e/e5/半身像_重岳_1.png',
    '林': 'https://prts.wiki/images/7/75/半身像_林_1.png',
    '焰影苇草': 'https://prts.wiki/images/a/ae/半身像_焰影苇草_1.png',
    '缄默德克萨斯': 'https://prts.wiki/images/0/0d/半身像_缄默德克萨斯_1.png',
    '斥罪': 'https://prts.wiki/images/e/e7/半身像_斥罪_1.png',
    '伺夜': 'https://prts.wiki/images/f/fc/半身像_伺夜_1.png',
    '白铁': 'https://prts.wiki/images/e/e5/半身像_白铁_1.png',
    '玛恩纳': 'https://prts.wiki/images/b/b1/半身像_玛恩纳_1.png',
    '百炼嘉维尔': 'https://prts.wiki/images/e/ed/半身像_百炼嘉维尔_1.png',
    '鸿雪': 'https://prts.wiki/images/4/4d/半身像_鸿雪_1.png',
    '多萝西': 'https://prts.wiki/images/0/04/半身像_多萝西_1.png',
    '黑键': 'https://prts.wiki/images/e/e6/半身像_黑键_1.png',
    '归溟幽灵鲨': 'https://prts.wiki/images/f/f7/半身像_归溟幽灵鲨_1.png',
    '艾丽妮': 'https://prts.wiki/images/b/bd/半身像_艾丽妮_1.png',
    '流明': 'https://prts.wiki/images/9/9f/半身像_流明_1.png',
    '号角': 'https://prts.wiki/images/8/85/半身像_号角_1.png',
    '菲亚梅塔': 'https://prts.wiki/images/f/f8/半身像_菲亚梅塔_1.png',
    '澄闪': 'https://prts.wiki/images/1/17/半身像_澄闪_1.png',
    '令': 'https://prts.wiki/images/d/d6/半身像_令_1.png',
    '老鲤': 'https://prts.wiki/images/e/e8/半身像_老鲤_1.png',
    '灵知': 'https://prts.wiki/images/a/a9/半身像_灵知_1.png',
    '耀骑士临光': 'https://prts.wiki/images/d/db/半身像_耀骑士临光_1.png',
    '焰尾': 'https://prts.wiki/images/9/92/半身像_焰尾_1.png',
    '远牙': 'https://prts.wiki/images/4/4f/半身像_远牙_1.png',
    '琴柳': 'https://prts.wiki/images/2/28/半身像_琴柳_1.png',
    '假日威龙陈': 'https://prts.wiki/images/5/51/半身像_假日威龙陈_1.png',
    '水月': 'https://prts.wiki/images/2/22/半身像_水月_1.png',
    '帕拉斯': 'https://prts.wiki/images/7/72/半身像_帕拉斯_1.png',
    '卡涅利安': 'https://prts.wiki/images/3/36/半身像_卡涅利安_1.png',
    '浊心斯卡蒂': 'https://prts.wiki/images/7/7f/半身像_浊心斯卡蒂_1.png',
    '凯尔希': 'https://prts.wiki/images/c/c0/半身像_凯尔希_1.png',
    '歌蕾蒂娅': 'https://prts.wiki/images/3/33/半身像_歌蕾蒂娅_1.png',
    '异客': 'https://prts.wiki/images/d/d3/半身像_异客_1.png',
    '灰烬': 'https://prts.wiki/images/f/fa/半身像_灰烬_1.png',
    '夕': 'https://prts.wiki/images/f/f2/半身像_夕_1.png',
    '嵯峨': 'https://prts.wiki/images/a/a4/半身像_嵯峨_1.png',
    '空弦': 'https://prts.wiki/images/8/86/半身像_空弦_1.png',
    '山': 'https://prts.wiki/images/7/7b/半身像_山_1.png',
    '迷迭香': 'https://prts.wiki/images/9/9a/半身像_迷迭香_1.png',
    '泥岩': 'https://prts.wiki/images/0/08/半身像_泥岩_1.png',
    '瑕光': 'https://prts.wiki/images/a/a6/半身像_瑕光_1.png',
    '史尔特尔': 'https://prts.wiki/images/5/58/半身像_史尔特尔_1.png',
    '森蚺': 'https://prts.wiki/images/4/4a/半身像_森蚺_1.png',
    '棘刺': 'https://prts.wiki/images/0/08/半身像_棘刺_1.png',
    '铃兰': 'https://prts.wiki/images/f/fe/半身像_铃兰_1.png',
    '早露': 'https://prts.wiki/images/9/92/半身像_早露_1.png',
    'W': 'https://prts.wiki/images/4/45/半身像_W_1.png',
    '温蒂': 'https://prts.wiki/images/5/5f/半身像_温蒂_1.png',
    '傀影': 'https://prts.wiki/images/a/ad/半身像_傀影_1.png',
    '风笛': 'https://prts.wiki/images/e/ea/半身像_风笛_1.png',
    '刻俄柏': 'https://prts.wiki/images/6/69/半身像_刻俄柏_1.png',
    '年': 'https://prts.wiki/images/4/4d/半身像_年_1.png',
    '阿': 'https://prts.wiki/images/7/72/半身像_阿_1.png',
    '煌': 'https://prts.wiki/images/1/1c/半身像_煌_1.png',
    '莫斯提马': 'https://prts.wiki/images/f/fc/半身像_莫斯提马_1.png',
    '麦哲伦': 'https://prts.wiki/images/c/c7/半身像_麦哲伦_1.png',
    '赫拉格': 'https://prts.wiki/images/8/82/半身像_赫拉格_1.png',
    '黑': 'https://prts.wiki/images/2/23/半身像_黑_1.png',
    '陈': 'https://prts.wiki/images/e/e1/半身像_陈_1.png',
    '斯卡蒂': 'https://prts.wiki/images/a/a5/半身像_斯卡蒂_1.png',
    '银灰': 'https://prts.wiki/images/9/90/半身像_银灰_1.png',
    '塞雷娅': 'https://prts.wiki/images/4/44/半身像_塞雷娅_1.png',
    '星熊': 'https://prts.wiki/images/2/22/半身像_星熊_1.png',
    '夜莺': 'https://prts.wiki/images/e/e9/半身像_夜莺_1.png',
    '闪灵': 'https://prts.wiki/images/d/d6/半身像_闪灵_1.png',
    '安洁莉娜': 'https://prts.wiki/images/3/30/半身像_安洁莉娜_1.png',
    '艾雅法拉': 'https://prts.wiki/images/3/36/半身像_艾雅法拉_1.png',
    '伊芙利特': 'https://prts.wiki/images/2/23/半身像_伊芙利特_1.png',
    '推进之王': 'https://prts.wiki/images/9/98/半身像_推进之王_1.png',
    '能天使': 'https://prts.wiki/images/2/2e/半身像_能天使_1.png'
}

//获取本次进行比较干员的头像
//http方法: GET
//接口:new_compare
function new_compare() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://114.132.188.253:9876/new_compare', true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var name = xhr.responseText.split(' ');
            left_name = name[0]
            right_name = name[1]
            code = name[2]
            document.getElementById("left_png").src = dic_pic_url[left_name];
            document.getElementById("left_png").alt = left_name;
            document.getElementById("right_png").src = dic_pic_url[right_name];
            document.getElementById("right_png").alt = right_name;
        }
    }
}


//上传本次比较结果
//http方法: POST
//接口: safescore
//供给参数:win_name, lose_name
function save_score_left() {
    xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://114.132.188.253:9876/save_score?win_name=' + left_name + '&lose_name=' + right_name + '&code=' + code, true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("toupiao_success").innerText = "成功投票给：" + left_name + " !";
            new_compare()
        }
    }
}

function save_score_right() {
    xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://114.132.188.253:9876/save_score?win_name=' + right_name + '&lose_name=' + left_name + '&code=' + code, true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("toupiao_success").innerText = "成功投票给：" + right_name + " !";
            new_compare()
        }
    }
}

//获取总比较结果
//http方法: GET
function view_final_order() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', 'http://114.132.188.253:9876/view_final_order', true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const json = xhr.responseText
            obj = JSON.parse(json);
            document.getElementById("已收集数据量").innerText = obj.count;

            const star6_staff_amount = obj.name.length;
            const score_list = obj.score;

            const class_num = 6; // 聚类簇数

            const color_list = ['', '9090ff', '64ffff', '64ff64', 'ffff64', 'ffe464', 'ff9090']
            const serie = new geostats(score_list);
            const cluster_list = serie.getClassJenks2(class_num);
            console.log(cluster_list)
            const cup_size = ['超大杯上', '超大杯中', '超大杯下', '大杯上', '大杯中', '大杯下', '中杯上', '中杯中', '中杯下']
            const star6_staff_amount_div_9 = star6_staff_amount / 9;
            const cup_color = new Array(star6_staff_amount);

            // 按照聚类划分梯度
            let j = 1
            for (let i = star6_staff_amount - 1; i >= 0; i--) {
                if (score_list[i] > cluster_list[j]) {
                    j++;
                }
                cup_color[i] = color_list[j];
            }

            var table = document.getElementById("final_order_table")
            table.style.display = "inline";

            htmlStr = '';
            for (let i = 0; i < star6_staff_amount; i++) {
                var this_rank = i + 1;

                htmlStr += "<tr style=\"background:#" + cup_color[i] + ";\"><td>" + cup_size[parseInt(i / star6_staff_amount_div_9)] + "</td><td>" + this_rank + "</td><td>" + obj.name[i] + "</td><td>" + obj.rate[i] + "</td><td>" + score_list[i] + "</td></tr>";
            }
            document.getElementById("final_order_tbody").innerHTML = htmlStr;
        }
    }
}

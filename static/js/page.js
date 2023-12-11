const SERVER_ADDRESS = `http://${DATA_DICT['SERVER_IP']}:${DATA_DICT['SERVER_PORT']}`;
const DICT_PIC_URL = DATA_DICT['DICT_PIC_URL'];

// 本地评分
let vote_times = 0;
const local_scores = {};
const local_win_times = {};
const local_visit_times = {};
for (const key in DICT_PIC_URL) {
    local_scores[key] = 0;
    local_win_times[key] = 0;
    local_visit_times[key] = 0;
}

const cup_size = ['超大杯上', '超大杯中', '超大杯下', '大杯上', '大杯中', '大杯下', '中杯上', '中杯中', '中杯下'];
const star6_staff_amount = Object.keys(DICT_PIC_URL).length;
const star6_staff_amount_div = star6_staff_amount / cup_size.length;


let code = "000";
let left_name = '';
let right_name = '';
let clusterList = [];

// 调整聚类簇数
const nclasses_input = document.getElementById('nclassesInput');
nclasses_input.addEventListener('input', function () {
    let nclasses = parseInt(nclasses_input.value, 10);
    nclasses = nclasses > nclasses_input.min ? nclasses < nclasses_input.max ? nclasses : nclasses_input.max : nclasses_input.min;
    // 如果没有打开过总表，则clusterList为空，new geostats会失败
    if (clusterList.length > 0) {
        const serie = new geostats(clusterList);
        const cluster_list = get_cluster_list(serie.serie, serie.getClassJenks2(nclasses));

        const GVF = 1 - get_SDCM(cluster_list) / serie.variance();
        document.getElementById('GVF').innerText = `${(GVF * 100).toFixed(2)}%`;

        const color_list = get_color_list(cluster_list.reverse());
        document.querySelectorAll("#final_order_tbody>tr").forEach((item, i) => {
            item.style.color = `#${color_list[i]}`;
        });
    }

    const sorted_self_table = Object.entries(local_scores).sort((a, b) => b[1] - a[1]);
    const selfClusterList = [];
    for (let i = 0; i < star6_staff_amount; i++) {
        selfClusterList.push(sorted_self_table[i][1]);
    }
    const self_serie = new geostats(selfClusterList);
    const self_cluster_list = get_cluster_list(self_serie.serie, self_serie.getClassJenks2(nclasses));
    // 如果总表未启用，则计算local表区分度。
    if (close_or_view_flag) {
        const self_GVF = 1 - get_SDCM(self_cluster_list) / self_serie.variance();
        document.getElementById('GVF').innerText = `${(self_GVF * 100).toFixed(2)}%`;
    }
    const self_color_list = get_color_list(self_cluster_list.reverse());
    document.querySelectorAll("#self_order_tbody>tr").forEach((item, i) => {
        item.style.color = `#${self_color_list[i]}`;
    });
});

// 跟随鼠标的夕龙泡泡
let currentMouseTop, currentScrollTop;
const pic_mouse = document.querySelector('#mouse_follower');
document.addEventListener('mousemove', function (e) {
    currentMouseTop = e.pageY;
    currentScrollTop = document.documentElement.scrollTop;
    pic_mouse.style.left = `${e.pageX}px`;
    pic_mouse.style.top = `${e.pageY}px`;
})

// 当页面向下滚动一定距离时，显示回到顶部按钮
window.addEventListener('scroll', function () {
    const topBtn = document.getElementById('topBtn');
    const nclassesInput = document.getElementsByClassName('nclassesInput')[0];
    if (document.documentElement.scrollTop > 550) { // 当滚动超过 550 像素时显示按钮
        topBtn.style.display = 'block';
        if (close_or_view_flag === false || self_close == false) {
            nclassesInput.style.display = 'block';
        }
    } else {
        topBtn.style.display = 'none';
        nclassesInput.style.display = 'none';
    }
    // 实时更新龙泡泡坐标
    pic_mouse.style.top = `${currentMouseTop + document.documentElement.scrollTop - currentScrollTop}px`;
});

// JavaScript 函数，用于滚动到页面顶部
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth' // 使用平滑滚动效果
    });
}

// 刷新个人表
function flush_self() {
    const sorted_self_table = Object.entries(local_scores).sort((a, b) => b[1] - a[1]);

    let selfStr = '';
    const clusterList = [];
    for (let i = 0; i < star6_staff_amount; i++) {
        clusterList.push(sorted_self_table[i][1]);
    }
    // 如果总表未启用，则显示个人表的区分度，否则显示总表区分度
    const cluster_list = get_best_cluster_list(clusterList, close_or_view_flag);
    const color_list = get_color_list(cluster_list.reverse());

    for (let i = 0; i < star6_staff_amount; i++) {
        let this_rank = i + 1;
        const chr_name = sorted_self_table[i][0];
        selfStr += `<tr style="color: #${color_list[i]}; background-color: currentColor"><td class="final_table_text">${cup_size[parseInt(i / star6_staff_amount_div)]}</td><td class="final_table_text">${this_rank}</td><td class="final_table_text">${chr_name}</td><td class="final_table_text">${(local_win_times[chr_name] / local_visit_times[chr_name] * 100).toFixed(2)}%</td><td class="final_table_text" style="text-align: right; padding-right: 25px">${sorted_self_table[i][1]}</td></tr>`;
    }
    document.getElementById("self_order_tbody").innerHTML = selfStr;
}

let self_close = true;
function view_self() {
    var self_table = document.getElementById("self_table");
    var self_button = document.getElementById("self_rst_button");
    if (self_close) {
        self_close = false;
        self_table.style.display = "inline-block";
        document.getElementById("您已投票").innerText = '您已投票 ' + vote_times + ' 次';
        self_button.value = "关闭您的投票结果";
        flush_self();
    }
    else {
        self_close = true;
        self_table.style.display = "none";
        document.getElementById("您已投票").innerText = '';
        self_button.value = "查看您的投票结果";
    }
}

//控制列表出现和关闭的按钮
let close_or_view_flag = true;
function close_or_view() {
    const close = document.getElementsByClassName('close');
    const result = document.getElementsByClassName('result');
    if (close_or_view_flag) {
        close_or_view_flag = false;
        view_final_order();
        close[0].style.display = 'inline';
        result[0].style.display = 'none';
    } else {
        close_or_view_flag = true;
        document.getElementById("已收集数据量").innerText = '';
        document.getElementById("您已投票").innerText = '';
        var table = document.getElementById("final_order_table");
        table.style.display = "none";
        close[0].style.display = 'none';
        result[0].style.display = 'inline';
    }
}

//获取本次进行比较干员的头像
//http方法: GET
//接口:new_compare
function new_compare() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', `${SERVER_ADDRESS}/new_compare`, true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const name = xhr.responseText.split(' ');
            [left_name, right_name, code] = name;
            const left_png = document.getElementById("left_png");
            const right_png = document.getElementById("right_png");
            left_png.src = DICT_PIC_URL[left_name];
            left_png.alt = DICT_PIC_URL[left_name].split('/').at(-1);
            right_png.src = DICT_PIC_URL[right_name];
            right_png.alt = DICT_PIC_URL[right_name].split('/').at(-1);
            document.getElementById("left_png_name").innerText = left_name;
            document.getElementById("right_png_name").innerText = right_name;
        }
    }
}


//上传本次比较结果
//http方法: POST
//接口: safescore
//供给参数:win_name, lose_name
function save_score(win_name, lose_name) {
    local_scores[win_name]++;
    local_scores[lose_name]--;
    local_win_times[win_name]++;
    local_visit_times[win_name]++;
    local_visit_times[lose_name]++;
    vote_times++;
    flush_self();
    xhr = new XMLHttpRequest();
    xhr.open('POST', `${SERVER_ADDRESS}/save_score?win_name=${win_name}&lose_name=${lose_name}&code=${code}`, true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            document.getElementById("toupiao_success").innerText = `成功投票给：${win_name}！`;
            new_compare();
        }
    }
}

function save_score_left() {
    save_score(left_name, right_name);
}

function save_score_right() {
    save_score(right_name, left_name);
}

//获取总比较结果
//http方法: GET
function view_final_order() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', `${SERVER_ADDRESS}/view_final_order`, true);
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            const json = xhr.responseText;
            obj = JSON.parse(json);
            document.getElementById("已收集数据量").innerText = obj.count;
            const star6_staff_amount = obj.name.length;
            const rate_list = obj.rate;
            const score_list = obj.score;

            clusterList = rate_list.map((r) => parseFloat(r));
            const cluster_list = get_best_cluster_list(clusterList);
            const color_list = get_color_list(cluster_list.reverse());

            const table = document.getElementById("final_order_table");
            table.style.display = "inline-block";

            let htmlStr = '', this_rank;
            for (let i = 0; i < star6_staff_amount; i++) {
                this_rank = i + 1;
                htmlStr += `<tr style="color: #${color_list[i]}; background-color: currentColor"><td class="final_table_text">${cup_size[parseInt(i / star6_staff_amount_div)]}</td><td class="final_table_text">${this_rank}</td><td class="final_table_text">${obj.name[i]}</td><td class="final_table_text">${rate_list[i]}</td><td class="final_table_text" style="text-align: right; padding-right: 25px">${score_list[i]}</td></tr>`;
            }
            document.getElementById("final_order_tbody").innerHTML = htmlStr;

            nclasses_input.max = star6_staff_amount - 1;
            nclasses_input.value = cluster_list.length;
        }
    }
}

function get_color_list(cluster_list) {
    // 按照聚类划分梯度
    const color_list = [];
    palette('rainbow', cluster_list.length, 0, 0.5, 0.95).forEach((color, i) => {
        color_list.push.apply(color_list, new Array(cluster_list[i].length).fill(color));
    })
    return color_list;
}

function get_best_cluster_list(data_array, modify_gvf = true) {
    const serie = new geostats(data_array);
    const SDAM = serie.variance();  // the Sum of squared Deviations from the Array Mean

    let cluster_list;
    let nclasses = 3;   // 聚类簇数
    let GVF;    // The Goodness of Variance Fit 方差拟合优度
    do {
        cluster_list = get_cluster_list(serie.serie, serie.getClassJenks2(nclasses++));
        GVF = 1 - get_SDCM(cluster_list) / SDAM;
    } while (GVF < 0.8);

    if (modify_gvf) {
        document.getElementById('GVF').innerText = `${(GVF * 100).toFixed(2)}%`;
    }

    return cluster_list;
}

function get_cluster_list(data_array, bound_list) {
    let i, j, k = 0, first, last;

    const cluster_list = [];
    if (bound_list[1] === data_array[1]) {
        k = 1;
        cluster_list.push(data_array.slice(0, k));
    }
    for (i = 1, j = k; i < bound_list.length - 1; i++, j = k) {
        first = data_array.indexOf(bound_list[i], j);
        last = data_array.lastIndexOf(bound_list[i]);
        if (bound_list[i] === bound_list[i + 1]) {
            k = first + 1;
        } else {
            k = last + 1;
        }
        cluster_list.push(data_array.slice(j, k));
    }
    cluster_list.push(data_array.slice(j));

    return cluster_list;
}

function get_SDCM(cluster_list) {
    const serie = new geostats(cluster_list[0]);
    let SDCM = serie.variance();    // the Sum of squared Deviations about Class Mean

    for (let i = 1; i < cluster_list.length; i++) {
        serie.setSerie(cluster_list[i]);
        SDCM += serie.variance();
    }

    return SDCM;
}
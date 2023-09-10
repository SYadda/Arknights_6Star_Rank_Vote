const SERVER_ADDRESS = `http://${DATA_DICT['SERVER_IP']}:${DATA_DICT['SERVER_PORT']}`;
const DICT_PIC_URL = DATA_DICT['DICT_PIC_URL'];

let code = "000";
let left_name = '';
let right_name = '';
let clusterList = [];

// 调整聚类簇数
const nclasses_input = document.getElementById('nclassesInput');
function recluster() {
    const serie = new geostats(clusterList);
    const SDAM = serie.variance();

    let nclasses = parseInt(nclasses_input.value, 10);
    nclasses = nclasses > nclasses_input.min ? nclasses < nclasses_input.max ? nclasses : nclasses_input.max : nclasses_input.min;
    let cluster_bounds_list = serie.getClassJenks2(nclasses);
    const color_list = palette('rainbow', cluster_bounds_list.length - 1, 0, 0.5, 0.95);
    const SDCM = get_SDCM(serie.serie, cluster_bounds_list);
    const GVF = 1 - SDCM / SDAM;    // The Goodness of Variance Fit 方差拟合优度
    document.getElementById('GVF').innerText = `${(GVF * 100).toFixed(2)}%`;
    const tr = document.querySelectorAll("#final_order_tbody>tr");
    let j = 0;
    cluster_bounds_list = cluster_bounds_list.reverse();
    tr.forEach((item, i) => {
        if (clusterList[i] <= cluster_bounds_list[j + 1] && (j + 1) < color_list.length) { j = j + 1; }
        item.style.color = `#${color_list[j]}`;
    });
}
nclasses_input.addEventListener('input', recluster);
nclasses_input.addEventListener('change', recluster);

let currentMouseTop, currentScrollTop;
// 跟随鼠标的夕龙泡泡
const pic_mouse = document.querySelector('#mouse_follower');
document.addEventListener('mousemove', function (e) {
    currentMouseTop = e.pageY;
    currentScrollTop = document.documentElement.scrollTop;
    pic_mouse.style.left = `${e.pageX}px`;
    pic_mouse.style.top = `${e.pageY}px`;
})

// 当页面向下滚动一定距离时，显示回到顶部按钮
const topBtn = document.getElementById('topBtn');
const nclassesInput = document.getElementsByClassName('nclassesInput')[0];
window.addEventListener('scroll', function () {
    if (document.documentElement.scrollTop > 500) { // 当滚动超过 500 像素时显示按钮
        topBtn.style.display = 'block';
        nclassesInput.style.display = 'block';
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

//控制列表出现和关闭的按钮
let close_or_view_flag = true;
function close_or_view() {
    const close = document.getElementsByClassName('close');
    const result = document.getElementsByClassName('result');
    if (close_or_view_flag) {
        close_or_view_flag = false;
        view_final_order()
        result[0].style.display = 'none';
        close[0].style.display = 'inline';
    } else {
        close_or_view_flag = true;
        document.getElementById("已收集数据量").innerText = '';
        var table = document.getElementById("final_order_table");
        table.style.display = "none";
        result[0].style.display = 'inline';
        close[0].style.display = 'none';
    }
}

let new_operator_flag = false;
function new_operator() {
    const open = document.getElementsByClassName('new_compare_mode_open');
    const close = document.getElementsByClassName('new_compare_mode_close');
    if (new_operator_flag) {
        new_operator_flag = false;
        open[0].style.display = 'none';
        close[0].style.display = 'inline';
    } else {
        new_operator_flag = true;
        open[0].style.display = 'inline';
        close[0].style.display = 'none';
    }
    new_compare();
}

//获取本次进行比较干员的头像
//http方法: GET
//接口:new_compare
function new_compare() {
    xhr = new XMLHttpRequest();
    if (new_operator_flag) {
        xhr.open('GET', `${SERVER_ADDRESS}/new_operator_compare`, true);
    } else {
        xhr.open('GET', `${SERVER_ADDRESS}/new_compare`, true);
    }
    xhr.send();

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var name = xhr.responseText.split(' ');
            left_name = name[0]
            right_name = name[1]
            code = name[2]
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
            const json = xhr.responseText
            obj = JSON.parse(json);
            document.getElementById("已收集数据量").innerText = obj.count;

            const star6_staff_amount = obj.name.length;
            const rate_list = obj.rate;
            const score_list = obj.score;

            clusterList = rate_list.map((r) => parseFloat(r));
            const cluster_bounds_list = get_cluster_bounds_list(clusterList).reverse();
            const color_list = palette('rainbow', cluster_bounds_list.length - 1, 0, 0.5, 0.95);
            const cup_size = ['超大杯上', '超大杯中', '超大杯下', '大杯上', '大杯中', '大杯下', '中杯上', '中杯中', '中杯下'];
            const star6_staff_amount_div = star6_staff_amount / cup_size.length;

            var table = document.getElementById("final_order_table")
            table.style.display = "inline-block";

            let htmlStr = '', this_rank;
            for (let i = 0, j = 0; i < star6_staff_amount; i++) {
                this_rank = i + 1;
                // 按照聚类划分梯度
                if (clusterList[i] <= cluster_bounds_list[j + 1] && (j + 1) < color_list.length) { j = j + 1; }
                htmlStr += `<tr style="color: #${color_list[j]}; background-color: currentColor"><td class="final_table_text">${cup_size[parseInt(i / star6_staff_amount_div)]}</td><td class="final_table_text">${this_rank}</td><td class="final_table_text">${obj.name[i]}</td><td class="final_table_text">${rate_list[i]}</td><td class="final_table_text" style="text-align: right; padding-right: 25px">${score_list[i]}</td></tr>`;
            }
            document.getElementById("final_order_tbody").innerHTML = htmlStr;

            nclasses_input.max = star6_staff_amount - 1;
            nclasses_input.value = cluster_bounds_list.length - 1;
        }
    }
}

function get_cluster_bounds_list(data_array) {
    const serie = new geostats(data_array);

    let cluster_bounds_list;
    let nclasses = 3;   // 聚类簇数
    let SDCM;   // the Sum of squared Deviations about Class Mean
    const SDAM = serie.variance();  // the Sum of squared Deviations from the Array Mean
    let GVF = 0;    // The Goodness of Variance Fit 方差拟合优度
    while (GVF < 0.8) {
        cluster_bounds_list = serie.getClassJenks2(nclasses++);
        SDCM = get_SDCM(serie.serie, cluster_bounds_list);
        GVF = 1 - SDCM / SDAM;
    };
    document.getElementById('GVF').innerText = `${(GVF * 100).toFixed(2)}%`;
    return cluster_bounds_list;
}

function get_SDCM(data_array, bound_list) {
    const bound_index = [0];
    for (let i = 1; i < bound_list.length - 1; i++) {
        bound_index.push(data_array.indexOf(bound_list[i]));
    }
    bound_index.push(data_array.length);

    const serie = new geostats();
    let SDCM = 0;
    for (let i = 1; i < bound_index.length; i++) {
        serie.setSerie(data_array.slice(bound_index[i - 1], bound_index[i]));
        SDCM += serie.variance();
    }

    return SDCM;
}
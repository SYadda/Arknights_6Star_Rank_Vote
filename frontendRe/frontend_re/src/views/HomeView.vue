<template>
  <div class="home">
    <div class="bg">
        <div class="block">
            <div class="com">
                <table class="compare">
                    <tr>
                        <!-- 左侧干员图片 在new_compare函数GET成功后更新 -->
                        <td>
                            <div class="operator-container" @click="save_score_left()">
                                <img id="left_png">
                                <div class="zh" id="left_png_name"></div>
                            </div>
                        </td>

                        <!-- 比较核心区域 -->
                        <td>
                            <!-- 标题 -->
                            <h1 class="compare_header">明日方舟六星</h1>
                            <h1>强度投票箱</h1>
                            <br>
                            <!-- 按钮和反馈 -->
                            <div class="compare_block">
                                <h4 id="toupiao_success">&nbsp;</h4>
                                <div class="function">
                                    <input class="skip" type="button" value="跳过，换一组" @click="new_compare()">
                                </div>
                                <!-- <div class="function">
                                    <input class="result" type="button" value="查看总投票结果" onclick="close_or_view()">
                                    <input class="close" type="button" value="关闭总投票结果" onclick="close_or_view()">
                                </div> -->
                                <div class="function">
                                    <input class="result" id="self_rst_button" type="button" value="查看您的投票结果"
                                        @click="view_self()">
                                </div>
                                <div class="function">
                                    <input class="result" id="vote_1v1_matrix_trigger" type="button" value="查看1v1对位矩阵"
                                        @click="trigger_vote_1v1_matrix_visible()">
                                </div>
                            </div>
                        </td>
                        <!-- 右侧干员图片 -->
                        <td>
                            <div class="operator-container" @click="save_score_right()">
                                <img id="right_png">
                                <div class="zh" id="right_png_name"></div>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            <!-- footer部分 -->
            <div class="footer">
                <table style="width: 100%"><tr>
                    <td>
                        <h3 class="move-up-animation red_text">目前仅单机投票开放</h3>
                        <h3 class="move-up-animation red_text">正式投票将在净罪作战结束后，即02月19日05:00开启</h3>
                    </td>
                    <td>
                        <img id="playPauseBtn" src="../assets/xuelangdahui.jpg" alt="播放/暂停" style="cursor: pointer; width: 100px; height: auto;" @click="music">
                        <!-- <audio id="audio" loop></audio> -->
                        <audio id="audio" loop ref="audio" :src="playSrc" ></audio>
                    </td>
                </tr></table>
            </div>

            <div class="footer">
                <div class="link-container">
                    <h3>投票箱唯一网址:
                        <a href="https://vote.ltsc.vip">
                            https://vote.ltsc.vip
                        </a>
                    </h3>
                </div>

                <br>

                <!-- <h4>V1.4.1 净罪作战 新增血狼打灰歌！按一下播放/暂停 </h4> -->
                <h4>V1.4.2 净罪作战 新增随机血狼金曲！按一下随机播放/停止 </h4>


                <br>
                <h4>作者：董杭杭, @blackwang08, @lengyanyu258, @lpdink, @hLdont</h4>
                <h4>bgm作者: <a href="https://space.bilibili.com/22799131">@理性蒸发人</a>, <a href="https://space.bilibili.com/441494429">@埃里克茨威格</a></h4>
                <h4>服务器赞助：@不会偏微分的fw, 阿里云高校计划, @SkadiD</h4>
            </div>
            <div class="footer">
                <!-- 这里增加了动画效果，类和style的效果如下：
                     red_text：原有的类，令文字呈红色
                     move-up-animation：新建动画类，实现向上的动画，具体内容见css文件
                     animation-delay：对动画的延时，用于使文字展示成从上往下依次出现的效果
                     如果需要修改文字，增加行数，请对应修改延时描述并加上动画类   -->
                <h2 class="move-up-animation" style="animation-delay: 0s;">规则：每次投票，得票+1分，未得票-1分，最后统计所有干员的胜率和得分，以胜率排名。</h2>
                <h2 class="move-up-animation" style="animation-delay: 0.2s;">每个ip只能投100票，自第101票起，每票按0.01票计算权重。</h2>
                <h2 class="move-up-animation" style="animation-delay: 0.4s;">自己的投票结果，不受100票限制，但网页刷新/关闭时会清零。</h2>
            </div>
        </div>
        <div class="block">
            <div class="footer">
                <!-- 这里增加了动画效果 如果需要修改文字，增加行数，请对应修改延时描述并加上动画类   -->
                <h2 class="move-up-animation red_text" style="animation-delay: 0.6s;">警告：由于干员随机抽取，次数并不完全一样，且数据全部来源于网友投票，结果可能存在不少谬误。</h2>
                <h2 class="move-up-animation red_text" style="animation-delay: 0.8s;">仅供娱乐，请勿用作抽卡建议和TTK工具！</h2>
                <h2 class="move-up-animation" style="animation-delay: 0.8s;">出于服务器资源管理考虑，实时投票结果并不会实时存储，刷票等行为导致服务器崩溃将丢失投票结果。</h2>
                <h2 class="move-up-animation" style="animation-delay: 1s;">鸣谢：本投票两两比较的灵感来源于NGA，制作过程中得到了PRTS.wiki，血狼破军和各位群友、网友的支持和建议，在此向各位表示感谢！</h2>
                <h4 class="move-up-animation" style="animation-delay: 1.2s;">本投票反映干员经过实战检验，口碑稳定后的强度评价，请投票前充分考虑合约、肉鸽n12以上、演算陌域n4以上，日常S关。</h4>
                <h4 class="move-up-animation" style="animation-delay: 1.4s;">“自定义聚类数目”功能：聚类数目越多，区分度越高(图中以颜色区分) 默认区分度为 80% </h4>
                    <h4 class="move-up-animation" style="animation-delay: 1.6s;">若要尝试不同的聚类数目，可以在右下方的“分层数”中调整。</h4>
                        <br>
                        
                            <div class="link-container">
                                <h3 class="move-up-animation" style="animation-delay: 1.8s;">本项目已开源至GitHub仓库：
                                    <a href="https://github.com/SYadda/Arknights_6Star_Rank_Vote" class="move-up-animation" style="animation-delay: 1.8s;">https://github.com/SYadda/Arknights_6Star_Rank_Vote</a>
                                </h3>
                            </div>

                            <div class="link-container">
                                <h3 class="move-up-animation" style="animation-delay: 2s;">第三次6星强度投票结果：(截至艾拉)
                                    <a href="https://github.com/SYadda/Arknights_6Star_Rank_Vote/blob/main/result_V1.3.jpeg" class="move-up-animation" style="animation-delay: 2.2s;">https://github.com/SYadda/Arknights_6Star_Rank_Vote/<br>blob/main/result_V1.3.jpeg</a>
                                </h3>                                
                            </div>

                        
                            <div class="link-container">
                                <h3 class="move-up-animation" style="animation-delay: 2.2s;">6星厨力投票结果：
                                    <a href="https://nga.178.com/read.php?tid=39828466" class="move-up-animation" style="animation-delay: 2s;">https://nga.178.com/read.php?tid=39828466</a>
                                </h3> 
                            </div>

                            
                            <div class="link-container">
                                <h3 class="move-up-animation" style="animation-delay: 2.4s;">第二次6星强度投票结果：(截至锏)
                                    <a href="https://nga.178.com/read.php?tid=38662591" class="move-up-animation" style="animation-delay: 2.4s;">https://nga.178.com/read.php?tid=38662591</a>
                                </h3>
                            </div>

                            
                            <div class="link-container">
                                <h3 class="move-up-animation" style="animation-delay: 2.6s;">第一次6星强度投票结果：(截至涤火杰西卡)
                                    <a href="https://nga.178.com/read.php?tid=38050985" class="move-up-animation" style="animation-delay: 2.6s;">https://nga.178.com/read.php?tid=38050985</a>
                                </h3>
                            </div>

                            <div class="link-container">
                                <h3 class="move-up-animation" style="animation-delay: 2.8s;">萨米收藏品投票结果：(不含DLC)
                                    <a href="https://nga.178.com/read.php?tid=38174026" class="move-up-animation" style="animation-delay: 2.8s;">https://nga.178.com/read.php?tid=38174026</a>
                                </h3>
                            </div>
                            
                        
                        
            </div>
        </div>
        
        <!-- 不可见数据部分,在获取数据后展示 -->
        <div class="final">
            <br>
            <h1 id="已收集数据量">&nbsp;</h1>
            <h1 id="您已投票">&nbsp;</h1>

            <br>
            <div class="final_table_group">
                <table id="final_order_table" class="final_table">
                    <caption>总投票结果</caption>
                    <thead>
                        <tr>
                            <th>杯型</th>
                            <th>排名</th>
                            <th>干员代号</th>
                            <th>胜率</th>
                            <th>得分</th>
                        </tr>
                    </thead>
                    <tbody id="final_order_tbody"></tbody>
                </table>
                <table id="self_table" class="final_table">
                    <caption>您的投票结果</caption>
                    <thead>
                        <tr>
                            <th>杯型</th>
                            <th>排名</th>
                            <th>干员代号</th>
                            <th>胜率<span id="win_rate" class="sort-icon select down" @click="sort_table(this)"></span>
                            </th>
                            <th>得分<span id="scores" class="sort-icon down" @click="sort_table(this)"></span>
                            </th>
                        </tr>
                    </thead>
                    <tbody id="self_order_tbody"></tbody>
                </table>
            </div>
        </div>

        <!-- 不可见数据部分，在获取1v1投票矩阵后展示 -->
        <div id="vote_1v1_matrix_container" class="footer">
            <div id="operators-1v1-transfer"></div>
            <input class="operators-1v1-button" type="button" @click="calculate_operators_1v1_matrix()" value="查看所选对位数据" />
            <input class="operators-1v1-button" type="button" @click="clear_operators_1v1_matrix()" value="清空全部数据" />
            <div id="operators-1v1-table"></div>
        </div>

        <img id="mouse_follower" src='../assets/夕trans.gif' alt="夕trans">
        <div class="nclassesInput">
            <label for="nclassesInput">分层数：</label>
            <input id="nclassesInput" style="font-size: medium;" type="number" min="1" max="9" value="6">
            <br>
            <label for="tokenInput">存档秘钥：</label>
            <input id="tokenInput" style="font-size: medium;">
            <br>
            <label for="GVF">区分度:</label>
            <label id="GVF"></label>
            <br>
            <input type="button" class="ioport" @click="upload()" value="上传个人结果">
            <br>
            <input type="button" class="ioport" @click="sync()" value="同步个人结果">
            <!-- <br>
            <input type="button" class="ioport" onclick="export_rst()" value="导出个人结果">
            <br>
            <label for="uploadImage" class="ioport">导入个人结果</label>
            <input type="file" name="image" value="" id="uploadImage" hidden="hidden" onchange="import_rst(event)"
                accept=".json" multiple="false"> -->
        </div>
        <button id="topBtn" @click="scrollToTop()">回到顶部</button>
        <div class="background"></div>
    </div>
  </div>
  <!-- <script src="@/assets/compatibleJS/geostats.min.js"></script> -->
</template>

<script>
import { DATA_DICT } from '@/assets/compatibleJS/datadict.js'
import { ID_NAME_DICT } from '@/assets/compatibleJS//id_operator';
import palette from 'google-palette';
const geostats = require('geostats');
import { Hero } from '@/assets/compatibleJS/page.js';
// import { TransferComponent } from '@/assets/compatibleJS/transfer.js';
// import { TableComponent } from '@/assets/compatibleJS/table.js';
const TransferComponent = require('@/assets/compatibleJS/transfer.js');
const TableComponent = require('@/assets/compatibleJS/table.js');
import LZString from 'lz-string';
// @ is an alias to /src
export default {
  data() {
    return {
      SERVER_ADDRESS: DATA_DICT['SERVER_ADDRESS'],
      DICT_PIC_URL: DATA_DICT['DICT_PIC_URL'],
      hero_dict: new Map(),
      cache_hero_dict: JSON.parse(localStorage.getItem('hero_dict') || '{}'),
      cup_size: ['超大杯上', '超大杯中', '超大杯下', '大杯上', '大杯中', '大杯下', '中杯上', '中杯中', '中杯下'],
      star6_staff_amount: 0,
      star6_staff_amount_div: 0,
      code: "000",
      left_name: '',
      right_name: '',
      clusterList: [],
      nclasses_input: null,
      vote_times: Number(localStorage.getItem('vote_times')),
      self_close: true,
      close_or_view_flag: true,
      vote_1v1_matrix_visible_flag: false,
      operator_matrix: null,
      // 干员1v1对位穿梭框配置
      OPERATOR_NAMES_KEY_LABEL: Object.entries(ID_NAME_DICT).map(([name, oid], index) => ({
        key: oid,
        label: name,
        index: index
      })),
      sourceData: [],
      targetData: [],
      transferComponent: null,
      // 跟随鼠标的夕龙泡泡
      currentMouseTop: 0,
      currentScrollTop: 0, 
      currentScrollWidth: 0, 
      currentScrollHeight: 0,
      // 获取pic_mouse的宽度和高度
      pic_mouse: null,
      picMouseWidth: 0,
      picMouseHeight: 0,
      // 干员1v1对位展示表格配置
      table_labels: [],
      table_Data: [],
      tableComponent: null,
      operators_1v1_table: null,

      audio: null,
      playPauseBtn: null,
      playSrc: require("../assets/tongtong.mp3"),
      playList: [
          { src: "tongtong.mp3", type: "audio/mpeg" },
          { src: "xuelangdahui.mp3", type: "audio/mpeg" }
      ],
      currentTrackIndex: -1,
    };
  },
  mounted() {
    this.new_compare();
    this.star6_staff_amount = Object.keys(this.DICT_PIC_URL).length;
    this.star6_staff_amount_div = this.star6_staff_amount / this.cup_size.length;
    this.sourceData = [...this.OPERATOR_NAMES_KEY_LABEL];
    this.transferComponent = new TransferComponent(this.sourceData, this.targetData, '干员列表', '选中列表');
    this.pic_mouse = document.querySelector('#mouse_follower');
    this.picMouseWidth = this.pic_mouse.offsetWidth;
    this.picMouseHeight = this.pic_mouse.offsetHeight;
    this.tableComponent = new TableComponent(this.table_Data, this.table_labels);
    this.operators_1v1_table = document.getElementById('operators-1v1-table');
    this.audio = document.getElementById('audio');
    this.playPauseBtn = document.getElementById('playPauseBtn');
    // 本地评分
    for (const key in this.DICT_PIC_URL) {
        var hero = new Hero(key, this.cache_hero_dict[key]);
        this.hero_dict.set(key, hero);
    }
    this.nclasses_input = document.getElementById('nclassesInput');
    this.nclasses_input.addEventListener('input', this.nclassesListener);
    const key_input = document.getElementById('tokenInput');
    key_input.value = localStorage.getItem('key') || '';
    key_input.addEventListener('blur', function () {
        localStorage.setItem('key', key_input.value);
        alert('上传密钥保存成功');
    });
    document.addEventListener('mousemove', this.mouseMoveListener )
    // 当页面向下滚动一定距离时，显示回到顶部按钮
    window.addEventListener('scroll', this.scrollListener );
    this.transferComponent.mount(document.getElementById('operators-1v1-transfer'));
    this.operators_1v1_table.style.display = "none";
    this.tableComponent.mount(this.operators_1v1_table);
    // 血狼打灰歌
    // this.playPauseBtn.addEventListener('click', this.music);

  },
  methods: {

      nclassesListener() {
        let nclasses = parseInt(this.nclasses_input.value, 10);
        nclasses = nclasses > this.nclasses_input.min ? nclasses < this.nclasses_input.max ? nclasses : this.nclasses_input.max : this.nclasses_input.min;
        // 如果没有打开过总表，则clusterList为空，new geostats会失败
        if (this.clusterList.length > 0) {
            const serie = new geostats(this.clusterList);
            const cluster_list = this.get_cluster_list(serie.serie, serie.getClassJenks2(nclasses));
        
            const GVF = 1 - this.get_SDCM(cluster_list) / serie.variance();
            document.getElementById('GVF').innerText = `${(GVF * 100).toFixed(2)}%`;
        
            const color_list = this.get_color_list(cluster_list.reverse());
            document.querySelectorAll("#final_order_tbody>tr").forEach((item, i) => {
                item.style.color = `#${color_list[i]}`;
            });
        }
        // 按照分类数调整个人表颜色
        const scores_array = Array.from(this.hero_dict.values()).map(hero => hero.scores);
        // 从大到小排序
        scores_array.sort((a, b) => b - a);
        const self_serie = new geostats(scores_array);
        const self_cluster_list = this.get_cluster_list(self_serie.serie, self_serie.getClassJenks2(nclasses));
        // 如果总表未启用，则计算个人表区分度。
        if (this.close_or_view_flag) {
            const self_GVF = 1 - this.get_SDCM(self_cluster_list) / self_serie.variance();
            document.getElementById('GVF').innerText = `${(self_GVF * 100).toFixed(2)}%`;
        }
        const self_color_list = this.get_color_list(self_cluster_list.reverse());
        document.querySelectorAll("#self_order_tbody>tr").forEach((item, i) => {
            item.style.color = `#${self_color_list[i]}`;
        });
      },

      mouseMoveListener(e) {
        this.picMouseWidth = this.pic_mouse.offsetWidth;
        this.picMouseHeight = this.pic_mouse.offsetHeight;
        this.currentMouseTop = e.pageY;
        this.currentScrollTop = document.documentElement.scrollTop;
        this.currentScrollWidth = document.documentElement.scrollWidth;
        this.currentScrollHeight = document.documentElement.scrollHeight;
    
        // 计算pic_mouse的左边和顶部位置
        let left = e.pageX;
        let top = e.pageY;
    
        // 确保pic_mouse不会超出视窗
        if (left + this.picMouseWidth + 21 > this.currentScrollWidth) {
            left = e.pageX - this.picMouseWidth - 21;
        }
        if (top + this.picMouseHeight + 21 > this.currentScrollHeight) {
            top = e.pageY - this.picMouseHeight - 21;
            this.currentMouseTop = top;
        }
        this.pic_mouse.style.left = `${left}px`;
        this.pic_mouse.style.top = `${top}px`;
      },

      scrollListener () {
          const topBtn = document.getElementById('topBtn');
          const nclassesInputs = Array.from(document.getElementsByClassName('nclassesInput'));
          nclassesInputs.forEach(nclassesInput => {
              if (document.documentElement.scrollTop > 550) { // 当滚动超过 550 像素时显示按钮
                  topBtn.style.display = 'block';
                  if (this.close_or_view_flag === false || this.self_close == false) {
                      nclassesInput.style.display = 'block';
                  }
              } else {
                  topBtn.style.display = 'none';
                  nclassesInput.style.display = 'none';
              }
          })
          // 实时更新龙泡泡坐标
          this.pic_mouse.style.top = `${this.currentMouseTop + document.documentElement.scrollTop - this.currentScrollTop}px`;
      },

      music () {
        if (this.audio.paused) {      
          let nextTrackIndex;
          do {
              nextTrackIndex = Math.floor(Math.random() * this.playList.length);
          } while (nextTrackIndex === this.currentTrackIndex);
          this.currentTrackIndex = nextTrackIndex;
          this.$refs.audio.src = require("../assets/" + this.playList[this.currentTrackIndex].src);
          this.audio.play();
      } else {
          this.audio.pause();
      }
    },
      // JavaScript 函数，用于滚动到页面顶部
      scrollToTop() {
          window.scrollTo({
              top: 0,
              behavior: 'smooth' // 使用平滑滚动效果
          });
      },

      // 刷新个人表
      flush_self(sort_by = 'win_rate', desc = true) {
          const hero_array = Array.from(this.hero_dict.values());
          let second_sort_by = sort_by == 'win_rate' ? 'scores' : 'win_rate';
          if (desc) {
              hero_array.sort((hero1, hero2) => hero2[second_sort_by] - hero1[second_sort_by]);
              hero_array.sort((hero1, hero2) => hero2[sort_by] - hero1[sort_by]);
          }
          else {
              hero_array.sort((hero1, hero2) => hero1[second_sort_by] - hero2[second_sort_by]);
              hero_array.sort((hero1, hero2) => hero1[sort_by] - hero2[sort_by]);
          }
        
          let selfStr = '';
          const clusterList = [];
          for (let i = 0; i < this.star6_staff_amount; i++) {
              clusterList.push(hero_array[i].scores);
          }
          // 如果总表未启用，则显示个人表的区分度，否则显示总表区分度
          const cluster_list = this.get_best_cluster_list(clusterList, this.close_or_view_flag);
          const color_list = this.get_color_list(cluster_list.reverse());
        
          for (let i = 0; i < this.star6_staff_amount; i++) {
              let this_rank = i + 1;
              const chr_name = hero_array[i].name;
              const win_rate = hero_array[i].win_rate;
              const scores = hero_array[i].scores;
              selfStr += `<tr style="color: #${color_list[i]}; background-color: currentColor"><td class="final_table_text">${this.cup_size[parseInt(i / this.star6_staff_amount_div)]}       </td><td class="final_table_text">${this_rank}</td><td class="final_table_text">${chr_name}</td><td class="final_table_text">${win_rate}%</td><td       class="final_table_text" style="text-align: right; padding-right: 25px">${scores}</td></tr>`;
          }
          document.getElementById("self_order_tbody").innerHTML = selfStr;
          document.getElementById("您已投票").innerText = '您已投票 ' + this.vote_times + ' 次';
          new Promise(() => {
              localStorage.setItem('hero_dict', JSON.stringify(Object.fromEntries(this.hero_dict)));
              localStorage.setItem('vote_times', this.vote_times);
          });
      },
      sort_table(element) {
        let is_desc = true;
        if (!element.classList.contains('select')) {
            // 取消其他元素的selects
            const selects = document.querySelectorAll('.select');
            selects.forEach(element => {
                element.classList.remove('select');
            });
            // 本元素添加select
            element.classList.add("select");
            // 按照本元素的当前状态排序
            is_desc = element.classList.contains("down");
        }
        else {
            // 本元素有select，则对调本元素的down和up
            let is_old_desc = element.classList.contains("down");
            is_desc = !is_old_desc;
            if (is_old_desc) {
                element.classList.remove('down');
                element.classList.add("up");
            }
            else {
                element.classList.remove('up');
                element.classList.add("down");
            }
        }
        this.flush_self(element.id, is_desc);
      },

      view_self() {
          var self_table = document.getElementById("self_table");
          var self_button = document.getElementById("self_rst_button");
          if (this.self_close) {
              this.self_close = false;
              const final = document.getElementsByClassName("final");
              final[0].style.display = "block";
              self_table.style.display = "inline-block";
              self_button.value = "关闭您的投票结果";
              this.flush_self();
          }
          else {
            this.self_close = true;
              const final = document.getElementsByClassName("final");
              if(this.self_close && this.close_or_view_flag){
                  final[0].style.display = "none";
              }
              self_table.style.display = "none";
              document.getElementById("您已投票").innerText = '';
              self_button.value = "查看您的投票结果";
          }
      },

      //控制列表出现和关闭的按钮
      close_or_view() {
          const close = document.getElementsByClassName('close');
          const result = document.getElementsByClassName('result');
          if (this.close_or_view_flag) {
              this.close_or_view_flag = false;
              this.view_final_order();
              close[0].style.display = 'inline';
              result[0].style.display = 'none';
          } else {
              this.close_or_view_flag = true;
              document.getElementById("已收集数据量").innerText = '';
              document.getElementById("您已投票").innerText = '';
              var table = document.getElementById("final_order_table");
              table.style.display = "none";
              const final = document.getElementsByClassName("final");
              if(this.self_close && this.close_or_view_flag){
                  final[0].style.display = "none";
              }
              close[0].style.display = 'none';
              result[0].style.display = 'inline';
          }
      },

      //获取本次进行比较干员的头像
      //http方法: POST
      //接口:new_compare
      new_compare() {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', `${this.SERVER_ADDRESS}/new_compare`, true);
          xhr.setRequestHeader("Content-Type", "application/json");
          xhr.send(JSON.stringify({
              code: this.code
          }));
          const self = this;
          xhr.onreadystatechange = function () {
              if (xhr.readyState === 4 && xhr.status === 200) {
                  const data = JSON.parse(xhr.responseText);
                  let left_id = data.left;
                  let right_id = data.right;
                  self.code = data.code;
                  const left_png = document.getElementById("left_png");
                  const right_png = document.getElementById("right_png");
                  self.left_name = Object.keys(ID_NAME_DICT).find(key => ID_NAME_DICT[key] === left_id);
                  self.right_name = Object.keys(ID_NAME_DICT).find(key => ID_NAME_DICT[key] === right_id);
                  left_png.src = self.DICT_PIC_URL[self.left_name];
                  left_png.alt = self.DICT_PIC_URL[self.left_name].split('/').at(-1);
                  right_png.src = self.DICT_PIC_URL[self.right_name];
                  right_png.alt = self.DICT_PIC_URL[self.right_name].split('/').at(-1);
                  document.getElementById("left_png_name").innerText = self.left_name;
                  document.getElementById("right_png_name").innerText = self.right_name;
              }
          }
      },


      //上传本次比较结果
      //http方法: POST
      //接口: save_score
      //供给body: win_name, lose_name, code
      save_score(win_name, lose_name) {
          this.hero_dict.get(win_name).win();
          this.hero_dict.get(lose_name).lose();
          this.vote_times++;
          this.flush_self();
          const xhr = new XMLHttpRequest();
          xhr.open('POST', `${this.SERVER_ADDRESS}/save_score`, true);
          xhr.setRequestHeader("Content-Type", "application/json");
          // xhr.send(JSON.stringify({
          //     win_name: win_name,
          //     lose_name: lose_name,
          //     code: code
          // }));
          xhr.send(JSON.stringify({
              win_id: ID_NAME_DICT[win_name],
              lose_id: ID_NAME_DICT[lose_name],
              code: this.code
          }));
        
          const self = this;
          xhr.onreadystatechange = function () {
              if (xhr.readyState === 4 && xhr.status === 200) {
                  document.getElementById("toupiao_success").innerText = `成功投票给：${win_name}！`;
                  self.new_compare();
              }
          }
      },

      save_score_left() {
          this.save_score(this.left_name, this.right_name);
      },

      save_score_right() {
          this.save_score(this.right_name, this.left_name);
      },

      //获取总比较结果
      //http方法: GET
      view_final_order() {
          const xhr = new XMLHttpRequest();
          xhr.open('GET', `${this.SERVER_ADDRESS}/view_final_order`, true);
          xhr.send();

          const self = this;
          xhr.onreadystatechange = function () {
              if (xhr.readyState === 4 && xhr.status === 200) {
                  const json = xhr.responseText;
                  const obj = JSON.parse(json);
                  document.getElementById("已收集数据量").innerText = obj.count;
                  const star6_staff_amount = obj.name.length;
                  const rate_list = obj.rate;
                  const score_list = obj.score;
              
                  self.clusterList = rate_list.map((r) => parseFloat(r));
                  const cluster_list = self.get_best_cluster_list(self.clusterList);
                  const color_list = self.get_color_list(cluster_list.reverse());
              
                  const table = document.getElementById("final_order_table");
                  table.style.display = "inline-block";
                  const final = document.getElementsByClassName("final");
                  final[0].style.display = "block";
              
                  let htmlStr = '', this_rank;
                  for (let i = 0; i < star6_staff_amount; i++) {
                      this_rank = i + 1;
                      htmlStr += `<tr style="color: #${color_list[i]}; background-color: currentColor"><td class="final_table_text">${self.cup_size[parseInt(i /         self.star6_staff_amount_div)]}</td><td class="final_table_text">${this_rank}</td><td class="final_table_text">${obj.name[i]}</td><td         class="final_table_text">${rate_list[i]}</td><td class="final_table_text" style="text-align: right; padding-right: 25px">${score_list[i]}</td></tr>`;
                  }
                  document.getElementById("final_order_tbody").innerHTML = htmlStr;
                
                  self.nclasses_input.max = star6_staff_amount - 1;
                  self.nclasses_input.value = cluster_list.length;
              }
          }
      },

      get_color_list(cluster_list) {
          // 按照聚类划分梯度
          const color_list = [];
          palette('rainbow', cluster_list.length, 0, 0.5, 0.95).forEach((color, i) => {
              color_list.push.apply(color_list, new Array(cluster_list[i].length).fill(color));
          })
          return color_list;
      },

      get_best_cluster_list(data_array, modify_gvf = true) {
          const serie = new geostats(data_array);
          const SDAM = serie.variance();  // the Sum of squared Deviations from the Array Mean
      
          let cluster_list;
          let nclasses = 3;   // 聚类簇数
          let GVF;    // The Goodness of Variance Fit 方差拟合优度
          do {
              cluster_list = this.get_cluster_list(serie.serie, serie.getClassJenks2(nclasses++));
              GVF = 1 - this.get_SDCM(cluster_list) / SDAM;
          } while (GVF < 0.8);
        
          if (modify_gvf) {
              document.getElementById('GVF').innerText = `${(GVF * 100).toFixed(2)}%`;
          }
        
          return cluster_list;
      },

      get_cluster_list(data_array, bound_list) {
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
      },

      get_SDCM(cluster_list) {
          const serie = new geostats(cluster_list[0]);
          let SDCM = serie.variance();    // the Sum of squared Deviations about Class Mean
      
          for (let i = 1; i < cluster_list.length; i++) {
              serie.setSerie(cluster_list[i]);
              SDCM += serie.variance();
          }
          return SDCM;
      },

      // 上传同步
      upload() {
          const key = localStorage.getItem('key') || "";
          const xhr = new XMLHttpRequest();
          xhr.open('POST', `${this.SERVER_ADDRESS}/upload`, true);
          xhr.setRequestHeader("Content-Type", "application/json");
          console.log(LZString.compressToUTF16(JSON.stringify(Object.fromEntries(this.hero_dict))))
          console.log(LZString.compress(JSON.stringify(Object.fromEntries(this.hero_dict))))
          xhr.send(JSON.stringify({
              key: key, 
              data: LZString.compressToUTF16(JSON.stringify(Object.fromEntries(this.hero_dict))), 
              vote_times: this.vote_times
          }));
          const self = this;
          xhr.onreadystatechange = function () {
              if (xhr.readyState === 4 && xhr.status === 200) {
                  const result = JSON.parse(xhr.responseText); 
                  if (result?.error) {
                      alert('上传失败：' + result?.error);
                      return;
                  }
                  if (result?.key) {
                      alert('上传成功：' + self.formatTime(result?.updated_at));
                      localStorage.setItem('key', result?.key);
                      const key_input = document.getElementById('tokenInput');
                      key_input.value = result?.key;
                  } else {
                      alert('上传失败');
                  }
              }
          }
      },
      sync() {
          const key = localStorage.getItem('key') || "";
          const xhr = new XMLHttpRequest();
          xhr.open('GET', `${this.SERVER_ADDRESS}/sync?key=${key}`, true);
          xhr.send();
          const self = this;
          xhr.onreadystatechange = function () {
              if (xhr.readyState === 4 && xhr.status === 200) {
                  const result = JSON.parse(xhr.responseText); 
                  if (result?.error) {
                      alert('同步失败：' + result?.error);
                      return;
                  }
                  if (result?.data) {
                      const data = LZString.decompressFromUTF16(result?.data);
                      console.log(result?.data, data)
                      localStorage.setItem('hero_dict', data);
                      localStorage.setItem('vote_times', result?.vote_times);
                      alert('同步数据成功：' + self.formatTime(result?.updated_at));
                      location.reload();
                  } else {
                      alert('同步失败');
                  }
              }
          }
        
      },
      formatTime(timestamp) {
          if (typeof timestamp === 'string') return timestamp;
          var date = new Date(timestamp * 1000);
          var year = date.getFullYear();
          var mon = date.getMonth() + 1;
          var day = date.getDate();
          var hour = date.getHours();
          var min = date.getMinutes();
          var sec = date.getSeconds();
          mon = parseInt(mon) < 10 ? "0" + mon : mon;
          day = parseInt(day) < 10 ? "0" + day : day;
          hour = parseInt(hour) < 10 ? "0" + hour : hour;
          min = parseInt(min) < 10 ? "0" + min : min;
          sec = parseInt(sec) < 10 ? "0" + sec : sec;
          let d = year + "-" + mon + "-" + day + " " + hour + ":" + min + ":" + sec
          return d;
      },

      // // 导入导出

      // function export_rst() {
      //     const json_string = JSON.stringify(Object.fromEntries(hero_dict), null, 4);
      //     const blob = new Blob([json_string], { type: 'application/json' });
      //     const url = URL.createObjectURL(blob);
      //     const link = document.createElement('a');
      //     link.href = url;
      //     link.download = 'Arknights_6Star_Rank_Vote.json';
      //     link.click();
      // }

      // function import_rst(event) {
      //     const file = event.target.files[0];
      //     const reader = new FileReader();

      //     reader.onload = function (e) {

      //         try {
      //             const contents = e.target.result;
      //             const importedData = JSON.parse(contents);
      //             var tmp_vote_times = 0;
      //             for (var [key, value] of Object.entries(importedData)) {
      //                 if (!hero_dict.has(key)) {
      //                     // 不存在角色就new一个
      //                     var hero = new Hero(key);
      //                 } else {
      //                     var hero = hero_dict.get(key);
      //                 }
      //                 if (Number.isInteger(value["vote_times"])) {
      //                     tmp_vote_times += value["vote_times"];
      //                 }
      //                 hero.set_attr(value);
      //             }
      //         }
      //         catch (error) {
      //             alert("导入失败:" + error)
      //         }
      //         vote_times = tmp_vote_times / 2;
      //         flush_self();
      //     };

      //     reader.readAsText(file);
      // }

      // 获取干员1v1投票矩阵
      // [POST]
      // 接口:/get_operators_1v1_matrix
      async get_operators_1v1_matrix() {
          const xhr = new XMLHttpRequest();
          xhr.open('POST', `${this.SERVER_ADDRESS}/get_operators_1v1_matrix`, true);
          xhr.send();
      
          return new Promise((resolve, reject) => {
              xhr.onreadystatechange = function () {
                  if (xhr.readyState === 4) {
                      if (xhr.status === 200) {
                          let operator_matrix = JSON.parse(xhr.responseText);
                          resolve(operator_matrix);
                      } else {
                          reject(new Error('请求失败'));
                      }
                  }
              };
          })
      },

      // 控制1v1投票矩阵是否显示，修改对应trigger文本

      trigger_vote_1v1_matrix_visible() {
          const vote_1v1_matrix_trigger = document.getElementById("vote_1v1_matrix_trigger");
          const vote_1v1_matrix_container = document.getElementById("vote_1v1_matrix_container");
          // const matrix_container = document.getElementById("matrix_container");
      
          if (this.vote_1v1_matrix_visible_flag) {
              this.vote_1v1_matrix_visible_flag = false;
              vote_1v1_matrix_trigger.value = "查看1v1对位矩阵"
              vote_1v1_matrix_container.style.display = 'none'
          
          } else {
              this.vote_1v1_matrix_visible_flag = true;
              vote_1v1_matrix_trigger.value = "关闭1v1对位矩阵"
              vote_1v1_matrix_container.style.display = 'block'
          }
      },

      // 计算1v1对表格
      async calculate_operators_1v1_matrix(){
          this.operators_1v1_table.style.display = "block";
          let transferData = this.transferComponent.getSourceAndTarget()
          this.sourceData = transferData.source
          this.targetData = transferData.target
          const selectedIndices = this.targetData.map(item => item.index);
          const selectedNames = this.targetData.map(item => item.label);
          let matrix = await this.get_operators_1v1_matrix()
          const subMatrix = selectedIndices.map(rowIndex =>         selectedIndices.map(colIndex => matrix[rowIndex][colIndex] / 100));
          this.tableComponent.updateData(subMatrix, selectedNames);
      },

      clear_operators_1v1_matrix(){
          this.operators_1v1_table.style.display = "none";
          let transferData = this.transferComponent.reset()
          this.sourceData = transferData.source
          this.targetData = transferData.target
          this.tableComponent.updateData([], []);
      }
  }
}
</script>

# Arknights_6Star_Rank_Vote

明日方舟 六星干员强度投票箱

净罪作战来啦！请各位依据干员近期在战场上的风采(尤其是新合约)投票~

前端JS，后端Python Flask，数据全部来自网友投票，仅供娱乐，准确度可能很低，求轻喷。有好点子欢迎直接提issue或者Pull requests！

## 直接访问：[https://vote.ltsc.vip](https://vote.ltsc.vip)

运行正常时，界面如下图所示：

<img src="images\frontend.png" alt="frontend" width="1000px">

## 在本地电脑上部署

1. Clone 本项目

   `git clone --depth=1 https://github.com/SYadda/Arknights_6Star_Rank_Vote.git`

1. 搭建环境：

   ```powershell
   cd .\Arknights_6Star_Rank_Vote\
   # 创建虚拟环境
   python -m venv venv
   # 激活该环境
   .\venv\Scripts\activate
   # (可选) 更新 pip
   python -m pip install -U pip
   # 安装依赖
   pip install -r requirements.txt
   ```

1. 运行应用：

   `flask --app backend.py run --debug --host=0.0.0.0 --port 9876`

   （debug环境将导致关闭/重载应用时，数据库自动写入功能失效，详见[pr39](https://github.com/SYadda/Arknights_6Star_Rank_Vote/pull/39)）

1. 用浏览器打开： http://127.0.0.1:9876

## 计分规则

如图所示，从所有6星干员中，随机抽取两位，供用户投票强弱。你可以点击你认为较强的干员，为其投票。

每次投票，得票的干员+1分，未得票的干员-1分。当投票次数足够多时，可以认为所有干员之间都得到了较充分的比较。

如果你认为两位干员实力不相上下，可以点击 **跳过，换一组** 按钮，感谢你认真、负责地进行干员评价！

最后，程序将统计所有干员的胜率和得分，以胜率排名。(为避免恶意刷票，每个ip只能投50票，自第51票起，每票按0.01票计算权重。)

## 结果展示

点击 **查看总投票结果** 按钮，将根据现有全部数据和上述规则，生成排行榜。

点击 **查看您的投票结果** 按钮，将根据用户单人的投票数据，实时生成排行榜。其不受50票限制，但数据将在网页刷新/关闭时**清零**。

特别要注意的是，当数据量很少时，由于随机抽取轮到每位干员的次数不等，且较小群体的主观认知偏见较大，此时生成的排名结果质量很差，谬误甚多，完全不能反映干员的真实水平。

即使数据量较大，此种排名也并不精确，最终结果受随机分组的影响较大。因此，建议无需过分关注具体排名，而是以明日方舟的惯例“超大杯、大杯、中杯”来了解干员的大致水平。此外，也提供对胜率接近的干员进行的聚类分块，帮助衡量干员的相对强弱。

**出于服务器资源管理考虑，实时投票结果并不会实时存储，刷票等行为导致服务器崩溃将丢失投票结果。**

## 作者

[@SYadda(董杭杭)](https://github.com/SYadda)：前端和后端整体框架设计

[@blackwang08](https://github.com/blackwang08)：前端网页美化

[@lengyanyu258](https://github.com/lengyanyu258)：前端网页美化，排行聚类分块算法

[@lpdink](https://github.com/lpdink)：前端 展示自己的投票结果

@不会偏微分的fw：服务器赞助

[@SkadiD](https://github.com/SkadiD)：前端CDN加速和服务器赞助

[@hLdont](https://github.com/hLdont)：后端开发

[b站@理性蒸发人](https://space.bilibili.com/22799131)：背景音乐 血狼打灰歌

[b站@埃里克茨威格](https://space.bilibili.com/441494429)：背景音乐 兔头兔头张开嘴

## 版权及鸣谢

本投票两两比较的思路来源于NGA，在数据爬取和信息展示中，得到了PRTS.wiki和阿里云高校计划服务器的支持，在程序设计制作过程中，还得到了血狼破军和各位群友、网友的支持和建议，在此向各位表示感谢！

本程序内使用的游戏图片、文本等信息，其版权属于 Arknights/上海鹰角网络科技有限公司。

# 蕃薯藤天空部落備份工具

## 說明

蕃薯藤天空部落已[宣布](https://service.tian.yam.com/posts/224379788)於 2018 年 10 月 1 日起關閉。另根據[這篇公告](https://service.tian.yam.com/posts/194800578)，如果使用者未於 2018 年 7 月 6 日前進行「補認證」，甚至再也無法登入。為了挽救寶貴的資料，特別寫了這隻免洗程式，幫忙快速自動下載未登入能獲取到的資料。

請注意：這隻程式仍不能保證下載完整的資料，如有遺漏恕無法負責。

## 使用方法

您需要先預備 [python 3](https://en.wikipedia.org/wiki/Python_(programming_language)) 命令列執行環境。這個程式測試在 Python 3.7.0。

使用 pip3 安裝 beautifulsoup4
```console
foo@bar:~$ pip3 install beautifulsoup4
```
執行
```console
foo@bar:~$ python3 run.py {username} {task}
```

{username} 請替換為您的帳號，它將會抓取 https://{username}.tian.yam.com/

{task} 請替換為:
* `all` 表示全部抓取
* `blog` 表示只抓部落格
* `album` 表示只抓相簿

執行中會以英文於 [stderr](https://en.wikipedia.org/wiki/Standard_streams#Standard_error_(stderr)) 輸出過程，如果部落格需要密碼，會提示使用者輸入。

程式會在執行目錄中自動建立目錄 bak_{username}_{date_time}，並在內輸出抓到的資料，包括：

* /log.txt: 過程記錄檔
* /albums: 相簿資料
  * data.json: 機讀格式
  * {album_id}/index.html: 人類閱讀格式
  * {album_id}/n_{album_name}: 空檔案
* /blog: 部落格資料
  * data.json: 機讀格式
  * {blog_id}/index.html: 人類閱讀格式
  * {blog_id}/{blog_name}: 空檔案

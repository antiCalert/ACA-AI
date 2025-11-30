使用前需要下载：

Scrapy: pip install scrapy   

这个流程是在VS Code terminal 进行的。

1，在 VS Code terminal 打开 tricontinental_downloader 文件夹：
2. 在 terminal 内输入 scrapy crawl download_english
3. 等待爬虫爬完，不过有些时候会卡住，可能需要手动停下，在tricontinental的网站上2小时爬了180个pdf文件
4. 下载的 pdf 可以在在 pdf_raw 文件夹里找到
5. 有些时候还是会混进非英文文档，可能需要手动去除其他语言，如果一个文件的名字带着两个en那它一定是英文
    
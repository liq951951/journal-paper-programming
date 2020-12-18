# -*- coding:utf-8 -*-
import sys
import re
import time
import pymysql
import requests
from bs4 import BeautifulSoup
from snownlp import SnowNLP
from tools.Date_Process import time_process
from tools.Number_Process import num_process
from search_spider.hour_slice import hour_slice
from tools.Emoji_Process import filter_emoji
"""
运行环境python3.5
输入关键字和起止时间（时间格式：2019.1.1.11），爬取微博数据
"""

conn = pymysql.connect(
    user='',
    password='',
    host='',
    port=,
    database='',
    charset='utf8mb4'
)	#配置mysql


sys.path.append("..")
url_template = 'https://s.weibo.com/weibo?q={}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g&page={}'  # 要访问的微博搜索接口URL
exclude_word = ["#", "@", "收起全文", "微博视频", "网页链接"]


def fetch_weibo_data(keyword, start_time, end_time, page_id, page_num):
    """
    根据关键字，起止时间以及页面id进行数据爬取, 返回由[dict…]构成
    """

    mycookie = ""
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        "cookie": mycookie}

    resp = requests.get(url_template.format(keyword, start_time, end_time, page_id), headers=headers, allow_redirects=True)

    print("微薄url:", resp.url)
    if resp.status_code == 200:
        print("fetch_data爬取状态正常")
    else:
        print("爬取状态异常:", resp.status_code)

    if not resp.raise_for_status():
        print("网页请求无报错")  # 网页请求报错
    else:
        print("网页请求出错：", resp.raise_for_status())
        print("网页请求历史", resp.history)

    soup = BeautifulSoup(resp.text, 'lxml')
    all_contents = soup.select('.card-wrap')                 # card-feed为微博内容
    print("本页微博条数：", len(all_contents))

    wb_count = 0
    mblog = []  # 保存处理过的微博
    for z, card in enumerate(all_contents):
        try:
            mid_in = card.get('mid')
        except:
            break
        if (mid_in is not None):  # 如果微博ID不为空则开始抓取
            wb_username = card.select_one('.txt').get('nick-name')  # 微博用户
            href = card.select_one('.from').select_one('a').get('href')
            re_href = re.compile('.*com/(.*)/.*')
            wb_userid = re_href.findall(href)[0]  # 微博用户ID
            if len(card.select(".txt")) == 2:
                wb_content = card.select('.txt')[1].text.strip()  # 长篇微博会有<展开全文>
            else:
                wb_content = card.select('.txt')[0].text.strip()  # 微博全文内容
            wb_content = wb_content.replace(" ", "")              # 剔除空格
            wb_place = []

            if len(card.select(".txt")) == 2:
                tag_a = card.select('.txt')[1].select("a")        # 获取所有的a标签，组成list
                if tag_a:
                    for i in range(len(tag_a)):
                        text = tag_a[i].text.strip()

                        if "·" in text:
                            wb_place.append(text[1:])
                else:
                    wb_place = []
            else:
                tag_a = card.select('.txt')[0].select("a")
                if tag_a:
                    for i in range(len(tag_a)):
                        text = tag_a[i].text.strip()

                        if "·" in text:
                            wb_place.append(text[1:])
                else:
                    wb_place = []
            wb_create = card.select_one('.from').select_one('a').text.strip()  # 微博创建时间
            wb_url = 'https:' + str(card.select_one('.from').select_one('a').get('href'))  # 微博来源URL
            wb_id = str(card.select_one('.from').select_one('a').get('href')).split('/')[-1].split('?')[0]  # 微博ID
            wb_createtime = time_process(wb_create)
            wb_forward = str(card.select_one('.card-act').select('li')[1].text)  # 微博转发
            wb_forwardnum = num_process(wb_forward.strip())                      # 微博转发数
            wb_comment = str(card.select_one('.card-act').select('li')[2].text)  # 微博评论
            wb_commentnum = num_process(wb_comment)                              # 微博评论数
            wb_like = str(card.select_one('.card-act').select_one('em').text)    # 微博点赞数
            try:
                wb_mood = SnowNLP(wb_content).sentiments
            except:
                print("can't be 0")

            if (wb_like == ''):  # 点赞数的处理
                wb_likenum = '0'
            else:
                wb_likenum = wb_like

            blog = {'wb_id': wb_id,  # 生成一条微博记录的列表
                    'wb_username': wb_username,
                    'wb_userid': wb_userid,
                    'wb_content': wb_content,
                    'wb_createtime': wb_createtime,
                    'wb_forwardnum': wb_forwardnum,         # 转发数
                    'wb_commentnum': wb_commentnum,         # 评论数
                    'wb_likenum': wb_likenum,
                    'wb_url': wb_url,
                    'wb_place': wb_place,
                    'wb_mood': wb_mood
                    }
            mblog.append(blog)
            wb_count = wb_count + 1  # 表示此页的微博数
    print("正在爬取" + str(start_time) + "----第"+ str(page_id)+"页/共" + str(page_num) + "页 ---- 当前页微博数：" + str(wb_count))
    return mblog


def fetch_pages(keyword, start_time, end_time):
    """
    使用beatifulsoul获取网页sorce代码，来获取页码信息，获取页码信息后，使用fetch_weibo_data来循环爬取每个面信息
    返回0（爬取失败） or blogs（爬取成功的list数据）
    """
    mycookie = ""
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36', "cookie": mycookie}

    resp = requests.get(url_template.format(keyword, start_time, end_time, '1'), headers=headers, allow_redirects=False)

    if resp.status_code == 200:
        print("fetch_pages爬取状态正常")
    else:
        print("！！！爬取状态异常:", resp.status_code)

    if not resp.raise_for_status():
        print("网页请求无报错")  # 网页请求报错
    else:
        print("！！！网页请求出错：", resp.raise_for_status())
        print("！！！网页请求历史", resp.history)

    soup = BeautifulSoup(resp.text, 'lxml')


    if str(soup.select_one('.card-wrap').select_one('p').text).startswith('抱歉'):  # 此次搜索条件的判断，如果没有相关搜索结果！退出...
        print("搜索条件无相关结果...")
        return 0
    try:
        page_num = len(soup.select_one('.m-page').select('li'))  # 获取此时间单位内的搜索页面的总数量，
        page_num = int(page_num)
        print(start_time + ' 到 ' + end_time + " 时间单位内搜索结果页面总数为：%d" % page_num)
    except Exception:
        page_num = 1

    mblogs = []
    for page_id in range(page_num):
        page_id += 1
        try:
            mblogs.extend(fetch_weibo_data(keyword, start_time, end_time, page_id, page_num))  # 每页调用fetch_data函数进行微博信息的抓取
        except Exception as e:
            print(e)
        time.sleep(1)
    for i in range(len(mblogs)):
        cursor = conn.cursor()
        sql = "insert into jia(wb_id,wb_username,wb_userid,wb_content,wb_createtime,wb_forwardnum,wb_commentnum,wb_likenum,wb_url,wb_mood) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,(mblogs[i]['wb_id'], mblogs[i]['wb_username'], mblogs[i]['wb_userid'],
                            filter_emoji(mblogs[i]['wb_content']),mblogs[i]['wb_createtime'], mblogs[i]['wb_forwardnum'],
                            mblogs[i]['wb_commentnum'], mblogs[i]['wb_likenum'],mblogs[i]['wb_url'],mblogs[i]['wb_mood']))
        print('************** %s  数据保存成功 **************' )
        conn.commit()
        cursor.close()
        return mblogs

if __name__ == '__main__':
    keyword = "钾"
    start_time = "2011.1.1.0"
    end_time = "2019.12.31.23"

    time_start = time.time()
    hour_all = hour_slice(start_time, end_time)             # 提取规范的时间格式，按每小时切分[（开始时间， 结束时间）……]

    datas_list = []
    i = 0
    for i in range(len(hour_all)):
        try:

            datas = fetch_pages(keyword, hour_all[i][0], hour_all[i][1])            # 程序主要入口, 开始时间和结束时间

            if datas != 0:
                print(hour_all[i][0] + ' 到 ' + hour_all[i][1] + ' 时间内的数据爬取完成！\n\n')
                datas_list.extend(datas)
            else:
                print("该次查询结果为空\n")
        except TypeError:
            print("typeerror")
        except:
            print("process exception")
        else:
            print("Reading")



        time.sleep(1)
    time_end = time.time()
    time_delta = time_end - time_start
    print("用时:"+ str(round(time_delta, 2)) + "秒")
    print("数据爬取顺利完成!!!")

from get_session import GetSession
from bs4 import BeautifulSoup as bs
import time
import os
import pymongo
from multiprocessing import Pool

S = GetSession()
s, headers = S.get_session()

def parse_page(html):
    html = bs(html, 'lxml')
    contents = html.select('tr')
    baseUrl = 'https://bbs.byr.cn/'
    data = []

    for content in contents:
        flag = content.select('td')
        if len(flag) != 7:
            continue
        title = content.select('td')[1].select('a')[0].get_text()
        tiezi_link = content.select('td')[1].select('a')[0].get('href')
        first_time = content.select('td')[2].get_text()
        author_nick = content.select('td')[3].select('a')[0].get_text()
        author_link = content.select('td')[3].select('a')[0].get('href')
        comment_num = content.select('td')[4].get_text()
        last_reply_time = content.select('td')[5].select('a')[0].get_text()
        last_reply_link = content.select('td')[5].select('a')[0].get('href')
        last_reply_name = content.select('td')[6].select('a')[0].get_text()
        last_reply_name_link = content.select('td')[6].select('a')[0].get(
            'href')
        data_temp = [
            title, baseUrl + tiezi_link, first_time, author_nick,
                   baseUrl + author_link, comment_num, last_reply_time,
                   baseUrl + last_reply_link, last_reply_name,
                   baseUrl + last_reply_name_link
        ]
        data_temp = [d.strip().replace(',', '，') for d in data_temp]
        data.append(data_temp)
    return data


def process_plate(html, Url, name):
    temp_html = html
    temp_html.encoding = 'GBK'
    temp_html = temp_html.text
    temp_html = bs(temp_html, 'lxml')
    page_nums = temp_html.select('li.page-normal a')
    if len(page_nums) < 2:
        return
    page_nums = page_nums[-2].get_text()
    print(name)
    name = name.split('/')
    rootpath = '文件/'

    if len(name) == 1:
        filePath = rootpath + name[0] + '.csv'
    else:
        filePath = rootpath
        for i in range(len(name) - 1):
            filePath += name[i] + '/'
        if not os.path.exists(filePath):
            os.makedirs(filePath)
        filePath += name[-1] + '.csv'
    file = open(filePath, 'w', encoding='utf-8')
    file.write(','.join(['帖子标题', '帖子链接', '帖子发布时间', '帖子作者', '作者链接', '回复数', '最新评论时间', '评论链接', '最新评论人', '最新评论人链接']) + '\n')

    # time.sleep(5)
    for index in range(int(page_nums)):
        response = s.get(
            Url + '?p={}&_uid=glfryqs'.format(index + 1), headers=headers)
        response.encoding = 'GBK'
        data = parse_page(response.text)
        for d in data:
            file.write(','.join(d) + '\n')
    file.close()


def tasks(data):
    for name, link in data:
        html = s.get(link + '?p=1&_uid=glfryqs', headers=headers)
        process_plate(html, link, name)
        print('完成{}'.format(name))


def main():
    names, links = S.get_all_link()
    tasks(zip(names,links))
    #--------------多进程
    # data=[]
    # for index in range(0, len(names), 20):
    #     source_name, source_link = [], []
    #     if index + 20 < len(names):
    #         source_name.extend(names[index:index + 20])
    #         source_link.extend(links[index:index + 20])
    #     else:
    #         source_name.extend(names[index:])
    #         source_link.extend(links[index:])
    #     data.append(zip(source_name,source_link))
    # pool = Pool(len(data))  # 创建一个包含4个线程的线程池
    # pool.map(tasks, data)
    # pool.close()  # 关闭线程池的写入
    # pool.join()  # 阻塞，保证子线程运行完毕后再继续主进程


if __name__ == '__main__':
    mongo = pymongo.MongoClient(host='localhost', port=27017)
    db = mongo.BBS_BYR
    collection = db.topics
    main()

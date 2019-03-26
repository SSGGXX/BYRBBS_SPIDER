import requests
from bs4 import BeautifulSoup as bs


class GetSession():
    def __init__(self):
        """
        #初始化得到session（）对象
        """
        self.my_header = {'x-requested-with': 'XMLHttpRequest'}
        self.session = requests.Session()
        self.Name = [
            '本站站务', '北邮校园', '学术科技', '信息社会', '人文艺术', '生活时尚', '休闲娱乐', '体育健身',
            '游戏对战', '乡亲乡爱'
        ]

    def get_session(self):
        """
        :return:
        """
        login_url = 'https://bbs.byr.cn/user/ajax_login.json'
        byr_data = {'id': '', 'passwd': ''}  # 个人账号信息
        self.session.post(login_url, data=byr_data, headers=self.my_header)
        return self.session, self.my_header

    def get_link_name(self, Section, Name):
        links = []  # 分模块的名字和链接
        names = []
        response = self.session.get(
            'https://bbs.byr.cn/section/ajax_list.json?uid=glfryqs&root=sec-{}'
                .format(Section),
            headers=self.my_header)
        response.encoding = 'GBK'
        response = bs(response.text, 'lxml')
        baseUrl = 'https://bbs.byr.cn'
        contents = response.select('a')
        for content in contents:
            link = baseUrl + content.get('href').replace('\\"', '')
            name = Name + '/' + content.get_text().replace('/', ',')
            if 'section' in link:  # 大标题中还有小标题
                name, link = self.get_link_name(link.split('/')[-1], name)
                links.extend(link)
                names.extend(name)
            else:
                links.append(link)
                names.append(name)
        return names, links

    def get_all_link(self):
        Link, Name = [], []
        for index, name in enumerate(self.Name):
            names, links = self.get_link_name(index, name)
            Link.extend(links)
            Name.extend(names)
        return Name, Link

    def test(self):
        response = self.session.get(
            'https://bbs.byr.cn/section/ajax_list.json?uid=glfryqs&root=sec-1',
            headers=self.my_header)
        response.encoding = 'GBK'
        html_bs = bs(response.text, 'lxml')
        print(html_bs.prettify())  # 打印出标准网页格式


if __name__ == '__main__':
    get_session = GetSession()
    get_session.get_all_link()

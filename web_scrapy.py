#  -*-coding:utf8 -*-
import requests
from readability.readability import Document 
from selenium import webdriver
import re
import time
import datetime
from redshift_connection import ScrapyConnectToRedshift
TABLE_NAME = ''
COLUM_LIST = []
class scrapy_data:
    def __init__(self, website_list=[]):
        self.aimed_website = website_list
        self.browser = webdriver.Chrome(executable_path='/Users/sam/Downloads/chromedriver')
        self.result_list = []
        # date = today.strftime('%Y-%m-%d %H:%M:%S')
        self.now_time = datetime.datetime.now().strftime("%Y月%m日%d %H:%M:%S")

    def reponse_data(self):
        # self.browser = webdriver.Chrome(executable_path='/Users/sam/Downloads/chromedriver')
        self.browser.get(self.aimed_website[0])
        title_list = self.browser.find_elements_by_class_name('boxa')
        len_report_list = len(title_list)
        latest_flg = True
        index_num = 0 
        while latest_flg:
            element = self.browser.find_element_by_xpath('//*[@id="moreArticle"]/a')
            time.sleep(4)
            element.click()
            latest_flg = False # for test
            latest_flg = self.get_20_records(index_num)
            index_num +=1 
        self.browser.quit()
        return self.result_list

    def _split_datetime(self, str_datetime):
        list_datetime = str_datetime.split("月")
        month = list_datetime[0].split(" ")[-1:]
        rest_date = list_datetime[1]
        date_time_combined = month[0]+'-'+ rest_date        # change to date format 
        year = datetime.date.today().year
        str_rp_time = str(year)+ '-'+date_time_combined
        str_rp_time = str_rp_time.replace("日","")
        rp_date_time = datetime.datetime.strptime(str_rp_time, "%Y-%m-%d %H:%M") # 2018-09-13 14:05:15
        return rp_date_time


    def _compared_with_now_time(self, str_rp_time):
        # print('str_rp_time', str_rp_time,datetime.datetime.now(), '222. ', datetime.datetime.now() - rp_date_time )
        return (datetime.datetime.now() - str_rp_time < datetime.timedelta(days=2))

    def get_20_records(self,index_num):
        print('index_num',index_num)
        for index in range(20):
            context ={}
            # try:
            context['title'] = self.browser.find_element_by_xpath('//*[@id="listArticle"]/div['+str(index+1+index_num*20)+']/h4/a').text
            context['published_at'] = self.browser.find_element_by_xpath('//*[@id="listArticle"]/div['+str(index+1+index_num*20)+']/span').text
            print('1', context['published_at'])
            context['published_at'] = self._split_datetime(context['published_at'])
            # print(self.now_time, context['datetime'],context['datetime'] > self.now_time, self.now_time - context['datetime'])
            # context['published_at'] = datetime.datetime.strptime(context['published_at'], "%Y年%m月%d日 %H:%M")

            if not self._compared_with_now_time(context['published_at']):
                return False
            else:
                context['url'] = self.browser.find_element_by_xpath('//*[@id="listArticle"]/div['+str(index+1+index_num*20)+']/h4/a').get_attribute('href')
                dr = re.compile(r'<[^>]+>',re.S)
                context['content'] = dr.sub('',self.get_content(context['url'])).strip('&#13;\n&#13;\n\u3000\u3000').lstrip('&#13;\n       \u3000\u3000').rstrip('&#13;\n')
                context['lanuage'] = 'cn' # hard code for cai xin website 
                context['is_added_to_source'] = False # hard code for cai xin website 
                context['media'] = 'caixin'
                self.result_list.append(context)
        self.browser.quit() 
        # print('*'*20+ '== some error happened =='+'*'*20)        
        return True

            # except Exception as err:
            

    def get_content(self,url):
        response = requests.get(url)
        doc = Document(response.text)
        summary = doc.summary()
        print('*'*20+'Yes! get the content '+'*'*20)
        return summary

if __name__ == '__main__':
    scrapy_data_v1 = scrapy_data(website_list=['http://economy.caixin.com/'])
    result_data_list = scrapy_data_v1.reponse_data()
    # result_data_list = [{'title': '财新数据|外资持有人民币债券1.44万亿元', 'datetime': '11月22日 17:04', 'url': 'http://economy.caixin.com/2018-11-22/101350804.html', 'content': '据财新数据，中债登公布的数据显示，截至今年10月底，境外投资者在中债登的债券托管量为14425.52亿元，尽管债券托管量再创历史新高，但当月债券托管量较9月份仅仅增加2.53亿元，创下过去20个月以来的单月增加额最低值。&#13;\n&#13;\n\u3000\u3000财政部发布通知，自2018年11月7日起至2021年11月6日止，对境外机构投资境内债券市场取得的债券利息收入暂免征收企业所得税和增值税。&#13;\n&#13;\n\u3000\u3000欲获得上图中数据，以及更多中国/全球经济数据，点此订阅财新数据通。&#13;\n      &#13;\n     '}, {'title': '财新数据|10月央行外汇占款21.3万亿元 环比下滑915.76亿元', 'datetime': '11月22日 16:59', 'url': 'http://economy.caixin.com/2018-11-22/101350799.html', 'content': '据财新数据，央行发布数据显示，中国10月末央行外汇占款21.3万亿元，环比下滑915.76亿元。&#13;\n&#13;\n\u3000\u3000欲获得上图中数据，以及更多中国/全球经济数据，点此订阅财新数据通。&#13;\n      &#13;\n     '}, {'title': '财新数据|北京常住人口20年来首降 减少2.2万', 'datetime': '11月22日 14:49', 'url': 'http://economy.caixin.com/2018-11-22/101350725.html', 'content': '在北京控制人口规模的大背景下，北京市常住人口增幅曲线逐步下行。据财新数据，国家统计局公布的数据显示，2017年北京市常住人口规模为2170.7万人，比2016年减少2.2万人，自1997年以来首次实现负增长。&#13;\n&#13;\n&#13;\n\u3000\u3000自1999年高校扩招以来，高等教育的普及率不断升高。每万人口中在校大学生数由1999年59.4人上升至猛增到2017年的257.6人，高校毕业生数从1999年的90万猛增到2017年的795万，再创历史新高，年均增速高达12.9%。&#13;\n\u3000\u3000欲获得上图中数据，以及更多中国/全球经济数据，点此订阅财新数据通。&#13;\n      &#13;\n     '}, {'title': '焦小平：合规的10%限额内的PPP支出责任不是隐性债务', 'datetime': '11月22日 11:36', 'url': 'http://economy.caixin.com/2018-11-22/101350656.html', 'content': '【财新网】（记者 于海荣）在地方债清理规范过程中，政府和社会资本合作（PPP）项目支出责任是否计入隐性债务，一直争议较大。财政部PPP中心主任焦小平表示，财政部即将下发文件，明确依法合规的、10%限额以内的PPP支出责任不是隐性债务。&#13;\n\u3000\u3000焦小平11月22日在“2018第四届中国PPP融资论坛”上表示，过去五年来，PPP在国家深化全面改革中起到了先行先试的探索作用，但部分地方在PPP发展中出现泛化、异化等不规范现象。去年8月以来，全面清理整顿PPP市场，刹住了泛化、异化乱象。&#13;\n      &#13;\n     '}, {'title': '财新数据|10月全国地方政府债务余额升至18.4万亿元', 'datetime': '11月22日 10:30', 'url': 'http://economy.caixin.com/2018-11-22/101350632.html', 'content': '据财新数据，财政部公布的数据显示，截至2018年10月末，全国地方政府债务余额184043亿元，环比增加1451亿元，控制在全国人大批准的限额之内。其中，一般债务109269亿元，专项债务74774亿元；政府债券181478亿元，非政府债券形式存量政府债务2565亿元。&#13;\n&#13;\n&#13;\n\u3000\u3000欲获得上图中数据，以及更多中国/全球经济数据，点此订阅财新数据通。&#13;\n      &#13;\n     '}]
#     result_data_list = [
#   {
#     "title": "财新数据|外资持有人民币债券1.44万亿元",
#     "published_at": "11月22日 17:04",
#     "url": "http://economy.caixin.com/2018-11-22/101350804.html",
#     "content": "据财新数据，中债登公布的数据显示，截至今年10月底，境外投资者在中债登的债券托管量为1442",
#     "lanuage": "cn",
#     "is_added_to_source": False,
#     "media": "caixin"
#   },
#   {
#     "title": "财新数据|10月央行外汇占款21.3万亿元 环比下滑915.76亿元",
#     "published_at": "11月22日 16:59",
#     "url": "http://economy.caixin.com/2018-11-22/101350799.html",
#     "content": "据财新数据，央行发布数据显示，中国10月末央行外汇占款21.3万亿元，环比下滑915.76亿元。&#13;\n&#13;\n　　欲获得上图中数据，以及更多中国/全球经济数据，点此订阅财新数据通。",
#     "lanuage": "cn",
#     "is_added_to_source": False,
#     "media": "caixin"
#   },
#   {
#     "title": "财新数据|北京常住人口20年来首降 减少2.2万",
#     "published_at": "11月22日 14:49",
#     "url": "http://economy.caixin.com/2018-11-22/101350725.html",
#     "content": "在北京控制人口规模的大背景下，北京市常住人口增幅曲线逐步下行。据财新数据，国家统计局公布的数据显示，2017年北京市常住人口规模为2170.7万人，比2016年减少2.2万人，自1997年以来首次实现负增长", 
#     "lanuage": "cn",
#     "is_added_to_source": False,
#     "media": "caixin"
#   },
#   {
#     "title": "焦小平：合规的10%限额内的PPP支出责任不是隐性债务",
#     "published_at": "11月22日 11:36",
#     "url": "http://economy.caixin.com/2018-11-22/101350656.html",
#     "content": "【财新网】（记者于海荣）在地方债清理规范过程中，政府和社会资本合作（PPP）项目支出责任是否计入隐性债务，一直争议较大。财政部PPP中心主任焦小平表示，财政部即将下发文件，明确依法合规的、10%限额以内的PPP支出责任不是隐性债务 ",
#     "lanuage": "cn",
#     "is_added_to_source": False,
#     "media": "caixin"
#   },
#   {
#     "title": "财新数据|10月全国地方政府债务余额升至18.4万亿元",
#     "published_at": "11月22日 10:30",
#     "url": "http://economy.caixin.com/2018-11-22/101350632.html",
#     "content": "据财新数据，财政部公布的数据显示，截至2018年10月末，全国地方政府债务余额184043亿元，环比增加1451亿元，控制在全国人大批准的限额之内。其中，一般债务109269亿元，专项债务74774亿元",
#     "lanuage": "cn",
#     "is_added_to_source": False,
#     "media": "caixin"
#   }
# ]
    print('*'*20+ "begin to connect to red shift "+ '*'*20)
    print(result_data_list)
    COLUM_LIST = ["url", "title", "content", "lanuage", "published_at", "is_added_to_source", "media"]
    con_obj = ScrapyConnectToRedshift()
    con_obj.bulk_insert('media_source_content', COLUM_LIST, result_data_list)
    
    # a = scrapy_data_v1._compared_with_now_time('10月30日 10:15')
    



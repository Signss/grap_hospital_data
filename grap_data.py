import requests
import json, random, jsonpath


class GrapHospital(object):

    def __init__(self):
        headers = [
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'},
        {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13'},
        {'User-Agent':'Opera/9.27 (Windows NT 5.2; U; zh-cn)'},
        {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1'}
         ]
        self.url = 'https://www.carelink.cn/hos/getHospital.htm?pubPreId={}'
        self.headers = random.choice(headers)
        self.file = open('hospital.txt', 'w')
        self.offset = 1

    def grap_data(self, url):
        response = requests.get(url, headers=self.headers)
        jsonobj = json.loads(response.text)
        return jsonobj

    def parse_data(self, jsonobj):
        hospital_name = jsonpath.jsonpath(jsonobj, "$.data[*].name")
        hospital_address = jsonpath.jsonpath(jsonobj, "$.data[*].address")
        hospital_fhTimeStr = jsonpath.jsonpath(jsonobj, '$.data[*].fhTimeStr')
        hospital_phone = jsonpath.jsonpath(jsonobj, '$.data[*].phone')
        hospital_levelName = jsonpath.jsonpath(jsonobj, '$.data[*].levelName')
        hospital_list = []
        if hospital_name:
            for i in range(len(hospital_name)):

                data_dict = {
                    'name': hospital_name[i],
                    'address': hospital_address[i],
                    'fhTimeStr': hospital_fhTimeStr[i],
                    'phone': hospital_phone[i],
                    'levelName': hospital_levelName[i]
                }
                hospital_list.append(data_dict)
        else:
            pass
        return hospital_list

    def save_data(self, hospital_list):
        for data in hospital_list:
            data_str = json.dumps(data, ensure_ascii=False) + '\n'
            self.file.write(data_str)

    def run(self):
        while self.offset < 50:
            next_url = self.url.format(self.offset)
            jsonobj = self.grap_data(next_url)
            hospital_list = self.parse_data(jsonobj)
            if len(hospital_list) != 0:
                self.save_data(hospital_list)
            else:
                pass
            self.offset += 1

if __name__ == '__main__':
    grap_hospital = GrapHospital()
    grap_hospital.run()


from selenium import webdriver
import time, json
from selenium.webdriver.chrome.options import Options

# //*[@id="hospital-list"]/li/div/p/a 医院名
# //*[@class="hospital-li"]/div/p[2]/span[1] 放号时间
# //*[@class="hos_tel_num"] 电话
# //*[@class="hos_address"] 地址
class GrapHospital(object):

    def __init__(self):
        self.url = 'https://www.carelink.cn/hos/hospital.htm'
        self.driver = webdriver.Chrome()
        self.file = open('shospital.txt', 'w')

    def get_data(self):
        self.driver.get(self.url)
        button_more = self.driver.find_element_by_xpath('//*[@id="more-hospital"]/div')
        for i in range(21):
            button_more.click()
            time.sleep(5)
        self.driver.implicitly_wait(5)
        name_list = self.driver.find_elements_by_xpath('//*[@id="hospital-list"]/li/div/p/a')
        time_list = self.driver.find_elements_by_xpath('//*[@class="hospital-li"]/div/p[2]/span[1]')
        phone_list = self.driver.find_elements_by_xpath('//*[@class="hos_tel_num"]')
        address_list = self.driver.find_elements_by_xpath('//*[@class="hos_address"]')
        name_l = []
        firstime_l = []
        phone_l = []
        address_l = []
        hospital_data = []
        for obj in name_list:
            name_l.append(obj.text)
        for sobj in time_list:
            firstime_l.append(sobj.text)
        for pobj in phone_list:
            if pobj.text != '':
                phone_l.append(pobj.text)
            else:
                phone_l.append('暂无电话')
        for aboj in address_list:
            address_l.append(aboj.text)
        for i in range(len(name_l)):
            content_dict = {
                'name': name_l[i],
                'first_time': firstime_l[i],
                'address': address_l[i],
                'phone': phone_l[i]
            }
            hospital_data.append(content_dict)
        return hospital_data

    def save_data(self, hospital_data):
        for data in hospital_data:
            data_str = json.dumps(data, ensure_ascii=False) + '\n'
            self.file.write(data_str)
        self.file.close()

    def run(self):
        hospital_data = self.get_data()
        self.save_data(hospital_data)

if __name__ == '__main__':
    grap_hospital = GrapHospital()
    grap_hospital.run()

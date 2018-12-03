from selenium import webdriver
from pymysql import connect
import time, json
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

# //*[@id="hospital-list"]/li/div/p/a 医院名
# //*[@class="hospital-li"]/div/p[2]/span[1] 放号时间
# //*[@class="hos_tel_num"] 电话
# //*[@class="hos_address"] 地址
class GrapHospital(object):

    # 初始化信息
    def __init__(self):
        # 要抓取的目标网站
        self.url = 'https://www.carelink.cn/hos/hospital.htm'
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        # 城市开始位置
        self.offset = 3
    # 切换城市
    def switch_city(self, offset):
        # 获取点击城市按钮
        obj = self.driver.find_element_by_xpath('//*[@id="localtion-btn"]')
        obj.click()
        # 强制等待以防定位元素失败
        time.sleep(5)
        # 获取切换城市按钮
        button_select = self.driver.find_element_by_xpath('//*[@id="nav-location-list"]/div[3]/p/span[2]')
        button_select.click()
        # 强制等待以防定位元素失败
        time.sleep(5)
        # 获取所有城市元素列表
        select_citys = self.driver.find_elements_by_xpath('//*[@id="nav-location-list"]/div[3]/ul[1]/li')
        # 获取下一个指定目标城市
        target_city = select_citys[offset]
        # 切换到指定目标城市
        target_city.click()
        # 关闭选择城市窗口
        img_button = self.driver.find_element_by_xpath('//*[@id="nav-location-list"]/div[1]/p[1]/button/img')
        img_button.click()
        # 刷新界面数据
        self.driver.refresh()

    def get_data(self):
        self.driver.get(self.url)
        hospital_num = 0
        # 防止一开始城市hospital没有数据程序定位不到元素报错
        try:
            hospital_num = int(self.driver.find_element_by_xpath('//*[@id="hospitalCount"]').text)
        except:
            pass
        # 判断需要加载多少页数据
        click_num = hospital_num // 10 + 1
        if click_num > 1:
            # 防止城市hospital数据加载到最后一页没有更多按钮而程序报错
            button_more = self.driver.find_element_by_xpath('//*[@id="more-hospital"]/div')
            if button_more:
                # 加载该城市所有数据以防报错
                try:
                    for i in range(click_num):
                        button_more.click()
                        time.sleep(5)
                except:
                    print('已加载完毕')

        self.driver.implicitly_wait(5)
        # 创建hospital信息空对象
        hospital_data = None
        # 防止城市无数据程序报错
        try:
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
                # 判断是否有医院名称
                if obj.text != '':
                    name_l.append(obj.text)
                else:
                    name_l.append('暂无名称')
            for sobj in time_list:
                # 判断是否有放号时间
                if sobj.text != '':
                    firstime_l.append(sobj.text)
                else:
                    firstime_l.append('暂无放号时间')
            for pobj in phone_list:
                # 判断是否有无电话
                if pobj.text != '':
                    phone_l.append(pobj.text)
                else:
                    phone_l.append('暂无电话')
            for aboj in address_list:
                # 判断有无地址
                if aboj.text != '':
                    address_l.append(aboj.text)
                else:
                    address_l.append('暂无地址')
            for i in range(len(name_l)):
                content_dict = {
                    'name': name_l[i],
                    'first_time': firstime_l[i],
                    'address': address_l[i],
                    'phone': phone_l[i]
                }
                hospital_data.append(content_dict)
        except:
            print('此城市暂无数据')
            return None
        return hospital_data
    # 保存某一城市抓取数据到txt文件
    def save_data(self, hospital_data):
        print(hospital_data)
        if len(hospital_data) != 0:
            # 获取当前城市名称作为抓取数据文件名
            city_name = self.driver.find_element_by_xpath('//*[@id="showAddres"]').text
            with open(city_name+'hospital.txt', 'w') as f:
                for data in hospital_data:
                    data_str = json.dumps(data, ensure_ascii=False) + '\n'
                    f.write(data_str)
        else:
            # 获取当前城市名称作为抓取数据文件名
            city_name = self.driver.find_element_by_xpath('//*[@id="showAddres"]').text
            with open(city_name+'null.txt', 'w') as f:
                f.write('暂无数据')

    # 保存抓取数据到mysql数据库
    def save_data_mysql(self, hospital_data):
        # 创建Connection连接
        conn = connect(host='localhost', port=3306, database='hospital', user='root', password='mysql', charset='utf8')
        # 获得Cursor对象
        cs1 = conn.cursor()
        for data in hospital_data:
            name = data['name']
            first_time = data['first_time']
            address = data['address']
            phone = data['phone']
            cs1.execute("insert into goods(name, first_time, address, phone) values('%s','%s','%s','%s')" % (name, first_time, address, phone))
        conn.commit()
        cs1.close()
    # 运行函数
    def run(self):
        while self.offset <= 28:
            hospital_data = self.get_data()
            self.save_data(hospital_data)
            self.save_data_mysql(hospital_data)
            self.switch_city(self.offset)
            self.offset += 1

if __name__ == '__main__':
    # 创建抓取对象
    grap_hospital = GrapHospital()
    # 运行抓取程序
    grap_hospital.run()
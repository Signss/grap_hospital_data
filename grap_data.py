import requests
import json, jsonpath, random
from constant_url import url

class GrapHospital(object):

    def __init__(self):
        headers = [
        {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'},
        {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13'},
        {'User-Agent':'Opera/9.27 (Windows NT 5.2; U; zh-cn)'},
        {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1'}
         ]
        self.url = url
        self.headers = random.choice(headers)
        self.file = open('hospital.txt', 'w')
        self.offset = 3

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
        print(hospital_list)
        return hospital_list

    def to_heavy(self, hospital_list):
        heavy_data = []
        for data in hospital_list:
            if data not in heavy_data:
                heavy_data.append(data)
        return heavy_data


    def save_data(self, heavy_data):
        for data in heavy_data:
            data_str = json.dumps(data, ensure_ascii=False) + '\n'
            self.file.write(data_str)

    def run(self):
        while self.offset < 50:
            next_url = self.url.format(self.offset)
            jsonobj = self.grap_data(next_url)
            hospital_list = self.parse_data(jsonobj)
            heavy_data = self.to_heavy(hospital_list)
            if len(heavy_data) != 0:
                self.save_data(heavy_data)
            else:
                pass
            self.offset += 1

if __name__ == '__main__':
    grap_hospital = GrapHospital()
    grap_hospital.run()




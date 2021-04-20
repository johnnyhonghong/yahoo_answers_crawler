from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import os
def get_sub_category(category = "") -> dict:
    try:
        if category == "timed_out":
            return {}
        if category != "":
            category = f"?sid={category}"
        
        url = f"https://tw.answers.yahoo.com/dir/index{category}"
        print(url)
        html = urlopen(url).read()
        soup = BeautifulSoup(html, 'lxml')
        sub_category = soup.findAll(class_ = "CategoryBoard__subCategory___1lrG5")
        sid_dict = {}
        if sub_category:
            for line in sub_category:
                element = line.find("a")
                category_sid = element.get('href').split("sid=")[-1]
                category_name = element.text
                sid_dict[category_sid] = category_name
        else:
            print("no sub_category")
    except:
        print("Timed out")
        sid_dict = {"timed_out":"timed_out"}
    return sid_dict
def get_last_layer_category_sid_csv(execute=False) -> list:
    if execute:
        main_sub_dict = {}
        main_category_dict = get_sub_category()
        key_list = list(main_category_dict.keys())
        for count, key in enumerate(key_list):
            print(count+1, main_category_dict[key])
            sub_dict = get_sub_category(key)
            main_sub_dict[key] = sub_dict.keys()
            key_list.extend(sub_dict.keys())
            main_category_dict.update(sub_dict)
            #time.sleep(10)
        with open('sid.txt', 'w') as csv_file:  
            for key, value in main_sub_dict.items():
                if not value:
                    csv_file.write(key)
                    csv_file.write("\n")
        return list(main_sub_dict.keys())
    else:
        with open('sid.txt', 'r') as csv_file:
            for line in csv_file.readlines():
                print(line)
if __name__ == "__main__":
    if not os.path.isfile('./sid.txt'):
        sid_list = get_last_layer_category_sid_csv(execute=True)
        
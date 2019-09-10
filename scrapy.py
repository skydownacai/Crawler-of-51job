from selenium import webdriver
from PIL import Image as PILImage
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import xlwt
import traceback
import requests
import base64
from selenium.webdriver.common.by import By
from  selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
last_page = 268
def cut(str):
    Str=str.strip('\n')
    index = Str.index("=")
    return Str[index+1:]
with open('set.ini','r',encoding='utf-8') as f:
    o = f.readlines()
    filepath = (cut(o[0]).replace('\n','')).lstrip().rstrip()
    header = (cut(o[1])).replace('\n','').replace('\n','')
    location = []
    for item in cut(o[2]).split(';'):
        if item == '\n':
            continue
        location.append(item.replace(" ",""))
    start_page = int(cut(o[3]).replace(' ', ''))
def download_pic(src,path):
    '这个函数用于下载网址为src,保存路径为path的文件'
    r = requests.get(src).content
    with open(path,'wb') as f:
        f.write(r)
def show_pic(path):
    '根据路径显示图片'
    IM = PILImage.open(path)
    IM.show()
def search_companys(keyword,locations,start_page):
    global filepath
    global last_page
    LOCAL = []
    now_page = 1
    print('爬虫启动.搜索公司关键字:{} 驻外地点:{} 启动页数:{}'.format(keyword,locations,start_page))
    Browser.get('https://search.51job.com/')
    Total = {}
    NEED_click_city = locations
    Browser.find_element_by_id('kwdselectid').send_keys(keyword)
    print('筛选公司中...')
    Browser.find_element_by_id('work_position_input').click()
    time.sleep(4)
    SELECTED = Browser.find_elements_by_xpath('//*[@id="work_position_click_multiple_selected"]/span')
    for selected in SELECTED:
        if selected.text not in NEED_click_city:
            selected.click()
        else:
            NEED_click_city.remove(selected.text)
    if locations[0] != '全国':
       click_code = ['000000','092200','091700','220200','220900','300200','091000','171800','100700','102000','030000','360000']
       for code in click_code:
          print('筛选中')
          Browser.find_element_by_id('work_position_click_center_left_each_{}'.format(code)).click()
          citys = Browser.find_elements_by_xpath('//*[@class="js_more"]/em')
          for city in citys:
             if city.text in NEED_click_city:
                city.click()
                NEED_click_city.remove(city.text)
                if NEED_click_city == []:
                    break
    Browser.find_element_by_xpath('//*[@id="work_position_click_bottom_save"]').click()
    Browser.find_element_by_xpath('/html/body/div[2]/form/div/div[1]/button').click()
    Total_company = int(Browser.find_element_by_xpath('/html/body/div[2]/div[4]/div[2]/div[4]').text[1:-3])

    print('筛选公司完成,共:{}条'.format(Total_company))
    count = 0
    print('开始爬取公司信息....')
    write_count = 1
    Total_page = int(Total_company/50)
    if Total_company % 50 != 0:
        Total_page += 1
    if start_page > Total_page:
        print('erro : 启动页:{} 超过最大页数{}'.format(start_page,Total_page))
    INPUT = Browser.find_element_by_xpath('//*[@id="jump_page"]')
    INPUT.clear()
    INPUT.send_keys(start_page)
    Browser.find_element_by_xpath('/html/body/div[2]/div[4]/div[55]/div/div/div/span[3]').click()
    now_page = start_page
    #----------------------上面是对公司进行筛选------------------------------
    while now_page <= Total_page:
        last_page = now_page
        data = xlwt.Workbook()
        DATA = data.add_sheet('0')
        print('当前页数:{}/{}'.format(now_page,Total_page))
        page = BeautifulSoup(Browser.page_source,'html.parser')
        for i in range(50):
            print('进度{}/{}'.format(count + 50*(start_page-1),Total_company))
            company_block = Browser.find_element_by_xpath('//*[@id="resultList"]/div[{}]/p/span/a'.format(4+i))
            name = company_block.get_attribute('title')
            count += 1
            company_href  = company_block.get_attribute('href')
            js='window.open("{}");'.format(company_href)
            Browser.execute_script(js)
            Browser.switch_to_window(Browser.window_handles[-1])
            if 'jobs.51job.com' not in Browser.current_url:
                Browser.close()
                Browser.switch_to_window(Browser.window_handles[0])
                continue
            try:
                infor1 = Browser.find_element_by_class_name('ltype').text.replace(" ","").split("|")
            except:
                Browser.close()
                Browser.switch_to_window(Browser.window_handles[0])
                continue
            items= Browser.find_elements_by_class_name('sp4')
            warfares = ''
            for item in items:
                warfares += item.text
                warfares += '/'
            warfares = warfares[:-1]
            loc = infor1[0]
            exp = infor1[1]
            deg = ''
            ned = ''
            pub = ''
            pay = Browser.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/div/div[1]/strong').text
            for item in infor1[2:]:
                if '大专' in item or '本科' in item or '专科' in item or '硕士' in item or '博士' in item or '研究生' in item or '初中及以下' in item or '高中/中技/中专' in item:
                    deg = item
                if '招' in item:
                    ned = item
                if '发布' in item:
                    pub = item
            job_infor  = Browser.find_element_by_class_name('job_msg').text
            cname = Browser.find_element_by_class_name('com_name ').text
            ctags = Browser.find_element_by_class_name('com_tag')
            tags  = ctags.find_elements_by_class_name('at')
            company_statue = tags[0].text
            company_guimo  = tags[1].text
            company_field  = tags[2].text
            Browser.close()
            Browser.switch_to_window(Browser.window_handles[0])
            keywords = [name,loc,exp,deg,ned,pub,pay,cname,company_statue,company_guimo,company_field,warfares,job_infor]
            for j in range(len(keywords)):
               DATA.write(i,j,keywords[j])
            if count + 50 * (start_page - 1) == Total_company:
                exit()
        data.save('{}.xls'.format(now_page))
        now_page += 1
        try:
            Browser.find_elements_by_class_name('bk')[1].click()
        except:
            break

        time.sleep(1)
chrome_options = Options()
chrome_options.add_argument('--headless')
Browser = webdriver.Chrome(executable_path=filepath,options=chrome_options)
while True:
    try:
        search_companys(header,location,last_page)
    except:
        continue
time.sleep(10)

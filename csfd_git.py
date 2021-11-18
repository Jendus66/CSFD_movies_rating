from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
from datetime import datetime, timedelta
import mysql.connector
import requests
from lxml import html



def clear_dbtable():
    global cursor
    query = "truncate table csfd_movies_calendar"
    cursor.execute(query)
    db_conn.commit()
    print("Table cleared.")

def insert_to_db(name,category,station,order_number,movie_link,program_link,tv_date,image_link):
    global cursor
    query = f"""insert into csfd_movies_calendar
(name,category,station,order_number,movie_link,program_link,rating,tv_date,image_link) values(
'{name}','{category}','{station}',{order_number},'{movie_link}','{program_link}',0,STR_TO_DATE('{tv_date}', '%d.%m.%Y'),'{image_link}'
)
"""
    cursor.execute(query)
    db_conn.commit()

def get_links():
    global cursor
    query = """
select distinct movie_link
from csfd_movies_calendar
"""
    cursor.execute(query)
    result = cursor.fetchall()
    return result

def update_rating(link, rating):
    global cursor
    query = f"""
UPDATE csfd_movies_calendar SET rating = {rating}
where movie_link = '{link}'; 
    """
    cursor.execute(query)
    db_conn.commit()


# Connection to database and a cursor declaring
db_conn = mysql.connector.connect(host="host", user="user", passwd="password", database="db")
print("Successful connection to database.")
cursor = db_conn.cursor()

# Clear a database table where movies data are inserted during a program run
clear_dbtable()

# Selenium driver config -> Firefox browser
path = "C:\\Python_SW\\geckodriver.exe"
options = Options()
options.headless = True
driver = webdriver.Firefox(executable_path=path, options=options)

# Get a website via Selenium
driver.get("https://new.csfd.cz/televize/horizontalne/")

# Accept the cookies and waiting till a cookies window disappear
print("Waiting for an element.")
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#onetrust-accept-btn-handler')))
driver.find_element_by_css_selector('#onetrust-accept-btn-handler').click()
print("The element found.")
time.sleep(2)

select = Select(driver.find_element_by_css_selector('#frm-stationSelectForm-0-station'))

# Names of tv channels which are included in movies searching
channels = [
'ČT 1',
'ČT 2',
'Nova',
'Prima Cool',
'Prima Love',
'Prima ZOOM',
'Prima MAX',
'Seznam.cz',
'Paramount Network',
'Prima Krimi',
'AMC',
'CSfilm',
'Filmbox Premium',
'FilmBox Extra HD',
'FilmBox',
'FilmBox Stars',
'Filmbox Family',
'Nova Cinema',
'Film Europe +',
'Film+',
'JOJ Cinema'
]

# Channels selection on the website
for tv in channels:
    try:
        select = Select(driver.find_element_by_xpath('//*[@id="frm-stationSelectForm-0-station"]'))
        select.select_by_visible_text(tv)
        time.sleep(2)
    except Exception as e:
        print(f"TV channel not found: {tv}")

# Submit on the website after channels selection
driver.find_element_by_css_selector('.tab-nav-list > li:nth-child(1) > a:nth-child(1)').click()

# Change movies sorting on the website by movie rating
select = Select(driver.find_element_by_css_selector('#frm-tvTipsOrder-tvTipsOrder-sort'))
select.select_by_value('rating')
time.sleep(3)
today = datetime.today()

# Looping through 7 previous days and searching in tv channels
print("Looping through days.")
for i in range(1,8):
    driver.get(f"https://new.csfd.cz/televize/?sort=rating&day=-{str(i)}")
    a = 1
    date = (today - timedelta(days=i)).strftime('%d.%m.%Y')
    print(f"Day number: {str(i)}")
    while True:
        try:
            name = driver.find_element_by_css_selector(f'article.article:nth-child({str(a)}) > div:nth-child(2) > header:nth-child(1) > h3:nth-child(1) > a:nth-child(2)')\
                .text
            movie_link = driver.find_element_by_css_selector(f'article.article:nth-child({str(a)}) > div:nth-child(2) > header:nth-child(1) > h3:nth-child(1) > a:nth-child(2)')\
                .get_attribute('href')
            category = driver.find_element_by_css_selector(f'article.article:nth-child({str(a)}) > div:nth-child(2) > p:nth-child(2) > span:nth-child(1)').text
            station = driver.find_element_by_css_selector(f'article.article:nth-child({str(a)}) > div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > p:nth-child(1) > img:nth-child(2)')\
                .get_attribute('alt')
            tv_prog = driver.find_element_by_css_selector(f'article.article:nth-child({str(a)}) > div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > p:nth-child(1) > a:nth-child(3)')\
                .get_attribute('href')
            image_link = driver.find_element_by_css_selector(f'article.article:nth-child({str(a)}) > figure:nth-child(1) > a:nth-child(1) > img:nth-child(1)').get_attribute('src')
            if image_link[0:4] == 'data':
                image_link = r'static/no_img.png'

            insert_to_db(name,category,station,a,movie_link,tv_prog,date,image_link)
            a = a + 1

        except Exception as e:
            try:
                next_element = driver.find_element_by_css_selector(f'article.article:nth-child({str(a+1)}) > div:nth-child(2) > header:nth-child(1) > h3:nth-child(1) > a:nth-child(2)')
                print("Next movie found, continue in looping.")
                a = a + 1
            except:
                print("Next movie not found, going to next day number.")
                break
# Close a browser
driver.quit()

# Headers declaration for the request library
headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0'}

# Getting data from the database
pre_links = get_links()
links = [i[0] for i in pre_links]

print("Getting movies ratings.")
with requests.Session() as s:
    for j, link in enumerate(links):
        r = s.get(link, headers=headers)
        content = html.fromstring(r.content)
        rating_el = content.cssselect("div.rating-average:nth-child(6)")

        if not rating_el:
            rating_el = content.cssselect("div.rating-average:nth-child(5)")

        rating = ''
        for i in rating_el:
            rating = i.text_content()
            try:
                rating = int(rating.strip().replace('%',''))
            except ValueError:
                rating = 0
        if rating == '':
            rating = 0
        update_rating(link, rating)

        if j%5 == 0:
            print(f"{str((j/len(links))*100)} %")

db_conn.close()
print('Done!')

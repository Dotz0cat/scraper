import sqlite3
from selenium import webdriver

def loop_page(driver, curser):
	elements = driver.find_element_by_class_name("radio-list").find_elements_by_tag_name("li")
	for i in range(1, len(elements)+1):
		elem = driver.find_element_by_xpath("/html/body/div[3]/div[1]/div[2]/div[2]/div[1]/ul/li[{0}]/a".format(i))
		url = elem.get_attribute("href")
		print(url)
		data = [url, False]
		curser.execute("INSERT INTO Urls (Url, Parsed) VALUES (?, ?)", data)

con = sqlite3.connect("/home/seth/python/scraper/cache.db")
c = con.cursor()

c.execute("CREATE TABLE Urls(Url text, Parsed bit)")

con.commit();
con.close();

driver = webdriver.Firefox()
con = sqlite3.connect("/home/seth/python/scraper/cache.db")
c = con.cursor()

for i in range(1, 6):
	driver.get("https://mytuner-radio.com/radio/country/japan-stations?page={0}".format(i))
	loop_page(driver, c)

con.commit()
con.close()
driver.close()
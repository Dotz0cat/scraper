from selenium import webdriver
import requests
import sys
import shutil
import os
import dropbox
import sqlite3
import token

def save_file(image, directory, name):
	with open('{dirname}/{name}'.format(dirname=directory, name=name), 'wb') as out_file:
		shutil.copyfileobj(image.raw, out_file)

def save_image(elem2):
	res = requests.get(elem2.get_attribute("src"), stream=True)

	save_file(res, "/home/seth/python/scraper/imgs", name+ext)

	del res

	dbx = dropbox.Dropbox(token)
	data = open(local_path, "rb").read()
	path = "/scraper/" + name+ext
	dbx.files_upload(data, path)
	share = dbx.sharing_create_shared_link_with_settings(path)

	return share

def image_exsits(name):
	dbx = dropbox.Dropbox(token)
	try:
		dbx.files_get_metadata("/scraper/" + name)
		return True
	except:
		return False

def scrape(address, saved):

	driver = webdriver.Firefox()
	driver.get(address)
	elem = driver.find_element_by_class_name("title")
	elem2 = driver.find_element_by_class_name("thumb-img")
	name = elem.get_attribute("innerHTML").replace(" live", "")

	other, ext = os.path.splitext(elem2.get_attribute("src"))
	local_path = "/home/seth/python/scraper/imgs/" + name + ext
	del other

	if image_exsits(name+ext):
		#something
	else:
		shared = save_image(elem2)
		#save link in sql 


	# res = requests.get(elem2.get_attribute("src"), stream=True)
	# other, ext = os.path.splitext(elem2.get_attribute("src"))
	# local_path = "/home/seth/python/scraper/imgs/" + name + ext
	# del other
	# save_file(res, "/home/seth/python/scraper/imgs", name+ext)
# 
	# del res
# 
	# dbx = dropbox.Dropbox(token)
	# data = open(local_path, "rb").read()
	# path = "/imgs/imgs/" + name+ext
	# dbx.files_upload(data, path)
	# share = dbx.sharing_create_shared_link_with_settings(path)

	#print(dbx.sharing_create_shared_link_with_settings(path).url)

	address = driver.execute_script("return _playlist[0].file;")


	fp = open("info.csv", "a+")
	fp.write(name)
	fp.write(",")
	fp.write(share.url.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", ""))
	fp.write(",")
	fp.write(driver.execute_script("return _playlist[0].file;"))
	fp.write("\n")

	driver.close()

	return name, shared, address

#scrape("https://mytuner-radio.com/radio/soulful-web-station-417283/")
con = sqlite3.connect("/home/seth/python/scraper/cache.db")
c = con.cursor()
for row in c.execute("SELECT Url FROM Urls WHERE Parsed=False"):
	name, image, address = scrape(row)
	data = [name, image, address]
	c.execute("INSERT INTO stations (Name, Image, Address) VALUES (?, ?, ?)", data)
	time.sleep(10)

con.commit()
con.close()



#https://mytuner-radio.com/radio/country/japan-stations
#/html/body/div[3]/div[1]/div[2]/div[2]/div[1]/ul/li[1]/a
#/html/body/div[3]/div[1]/div[2]/div[2]/div[1]/ul/li[32]
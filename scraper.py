from selenium import webdriver
import requests
import sys
import shutil
import os
import dropbox
import sqlite3
import time
import dropkey as tok
import typer
import pendulum

def save_file(image, directory, name):
	with open('{dirname}/{name}'.format(dirname=directory, name=name), 'wb') as out_file:
		shutil.copyfileobj(image.raw, out_file)

def save_image(dbx, elem2, name, ext, local_path):
	res = requests.get(elem2.get_attribute("src"), stream=True)

	save_file(res, "/home/seth/python/scraper/imgs", name+ext)

	data = open(local_path, "rb").read()
	path = "/scraper/" + name+ext
	dbx.files_upload(data, path)
	share = dbx.sharing_create_shared_link_with_settings(path).url

	return share

def image_exsits(dbx, name):
	try:
		dbx.files_get_metadata("/scraper/" + name)
		return True
	except:
		return False

def get_exsiting(dbx, name):
	return dbx.sharing_get_file_metadata("/scraper/" + name).preview_url

def scrape(dbx, driver, page):

	driver.get(page)
	elem = driver.find_element_by_class_name("title")
	elem2 = driver.find_element_by_class_name("thumb-img")
	name = elem.get_attribute("innerHTML").replace(" live", "")

	other, ext = os.path.splitext(elem2.get_attribute("src"))
	local_path = "/home/seth/python/scraper/imgs/" + name + ext

	if image_exsits(dbx, name+ext):
		shared = get_exsiting(dbx, name+ext)
	else:
		shared = save_image(dbx, elem2, name, ext, local_path)

	share = shared.replace("www.dropbox.com", "dl.dropboxusercontent.com").replace("?dl=0", "")

	address = driver.execute_script("return _playlist[0].file;")

	#driver.close()

	print(name)
	print(share)
	print(address)
	print("\r\n\r\n")

	return name, share, address

#scrape("https://mytuner-radio.com/radio/soulful-web-station-417283/")


#https://mytuner-radio.com/radio/country/japan-stations
#/html/body/div[3]/div[1]/div[2]/div[2]/div[1]/ul/li[1]/a
#/html/body/div[3]/div[1]/div[2]/div[2]/div[1]/ul/li[32]


# def main():
# 	with dropbox.Dropbox(tok.token()) as dbx, webdriver.Firefox() as driver:
# 		con = sqlite3.connect("/home/seth/python/scraper/cache.db")
# 		c = con.cursor()

# 		c.execute("SELECT Url FROM Urls")

# 		rows = c.fetchall()

# 		for row in rows:
# 			print(row[0])
# 			name, image, address = scrape(dbx, driver, row[0])
# 			data = [name, image, address]
# 			c.execute("INSERT INTO Stations (Name, Image, Address) VALUES (?, ?, ?)", data)
# 			c.execute("UPDATE Urls SET Date_late_scraped = strftime('%Y-%m-%d', 'now') WHERE Url = ?", [row[0]])
# 			con.commit()
# 			time.sleep(10)

# 		con.close()



app = typer.Typer()

@app.command()
def force():
	with dropbox.Dropbox(tok.token()) as dbx, webdriver.Firefox() as driver:
		con = sqlite3.connect("/home/seth/python/scraper/cache.db")
		c = con.cursor()

		c.execute("SELECT Url FROM Urls")

		rows = c.fetchall()

		for row in rows:
			print(row[0])
			name, image, address = scrape(dbx, driver, row[0])
			data = [name, image, address]
			c.execute("INSERT INTO Stations (Name, Image, Address) VALUES (?, ?, ?)", data)
			c.execute("UPDATE Urls SET Date_late_scraped = strftime('%Y-%m-%d', 'now') WHERE Url = ?", [row[0]])
			con.commit()
			time.sleep(10)

		con.close()

@app.command()
def time_since(days: int, months: int = 0, years: int = 0):
	with dropbox.Dropbox(tok.token()) as dbx, webdriver.Firefox() as driver:
		con = sqlite3.connect("/home/seth/python/scraper/cache.db")
		c = con.cursor()

		today = pendulum.now()

		time = today.subtract(years=years, months=months, days=days)

		print(time.format('YYYY-MM-DD'))

		c.execute("SELECT Url FROM Urls Where Date_late_scraped <= ?", [time.format('YYYY-MM-DD')])

		rows = c.fetchall()


		for row in rows:
			print(row[0])
			name, image, address = scrape(dbx, driver, row[0])
			data = [name, image, address]
			c.execute("INSERT INTO Stations (Name, Image, Address) VALUES (?, ?, ?)", data)
			c.execute("UPDATE Urls SET Date_late_scraped = strftime('%Y-%m-%d', 'now') WHERE Url = ?", [row[0]])
			con.commit()
			time.sleep(10)

		con.close()

@app.command()
def manual(date: str):
	with dropbox.Dropbox(tok.token()) as dbx, webdriver.Firefox() as driver:
		con = sqlite3.connect("/home/seth/python/scraper/cache.db")
		c = con.cursor()

		c.execute("SELECT Url FROM Urls Where Date_late_scraped <= ?", [date])

		rows = c.fetchall()


		for row in rows:
			print(row[0])
			name, image, address = scrape(dbx, driver, row[0])
			data = [name, image, address]
			c.execute("INSERT INTO Stations (Name, Image, Address) VALUES (?, ?, ?)", data)
			c.execute("UPDATE Urls SET Date_late_scraped = strftime('%Y-%m-%d', 'now') WHERE Url = ?", [row[0]])
			con.commit()
			time.sleep(10)

		con.close()

if __name__ == '__main__':
	app()
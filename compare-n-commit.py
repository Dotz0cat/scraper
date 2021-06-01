import typer
import inquirer
import sqlite3
import pendulum
from pprint import pprint

def commit(data):
	conn = sqlite3.connect("/home/seth/c/rajio_gtk/stations")
	c = conn.cursor()

	for item in data:
		print(item)

	question = [inquirer.Confirm('correct', message="Does this look correct?")]

	ans = inquirer.prompt(question)

	if ans['correct']:
		c.execute("SELECT Id FROM Stations ORDER BY Id DESC LIMIT 1;")
		id = c.fetchone()
		stuff = [id[0]+1, data[2]]
		c.execute("INSERT INTO Addresses (Id, Address) Values (?, ?);", stuff)
		conn.commit()
		more = [id[0]+1, data[0], data[1], 1]
		c.execute("INSERT INTO Stations (Id, Name, Thumbnail, Num_of_addresses) VALUES (?, ?, ?, ?);", more)
		conn.commit()
		return True

	conn.close()

	return False

def unique(data):
	conn = sqlite3.connect("/home/seth/c/rajio_gtk/stations")
	c = conn.cursor()

	c.execute("SELECT Name FROM Stations, Addresses WHERE Stations.Id = Addresses.Id AND Addresses.Address = ?", [data[2]])

	address = c.fetchone()

	c.execute("SELECT Name FROM Stations WHERE Name = ?", [data[0]])

	name = c.fetchone()

	c.execute("SELECT Name FROM Stations WHERE Thumbnail = ?", [data[1]])

	thumbnail = c.fetchone()

	exsits = False

	conn.close()

	if not address[0] == 'None':
		q = [inquirer.Confirm('exist', message="{0} already exsits. From address".format(address[0]), default=True)]
		ans = inquirer.prompt(q)
		exsits = True
	elif not name[0] == 'None':
		q = [inquirer.Confirm('exist', message="{0} already exsits. From name".format(name[0]), default=True)]
		ans = inquirer.prompt(q)
		exsits = True
	elif not thumbnail[0] == 'None':
		q = [inquirer.Confirm('exist', message="{0} already exsits. From thumbnail".format(thumbnail[0]), default=True)]
		ans = inquirer.prompt(q)
		exsits = True

	return exsits


def incorrect(row, conn, c):
	question = [inquirer.List('incorrect_value', message="What value is incorrect?", choices=['Name', 'Image', 'Address'], carousel=False)]
	ans = inquirer.prompt(question)

	if ans['incorrect_value'] == 'Name':
		q = [inquirer.Text('fixed_name', message="Edit name", default=row[0])]
		ans2 = inquirer.prompt(q)

		print(ans2['fixed_name'])
		print(row[1])
		print(row[2])
		print("\r\n")

		q2 = [inquirer.Confirm('correct', message="Are these values correct?")]

		ans3 = inquirer.prompt(q2)

		if ans3['correct']:
			check = commit([ans2['fixed_name'], row[1], row[2]])

			finish_up(conn, c, ans2['fixed_name'], check)

		else:
			incorrect([ans2['fixed_name'], row[1], row[2]], conn, c)

	elif ans['incorrect_value'] == 'Image':
		q = [inquirer.Text('fixed_image', message="Edit image", default=row[1])]
		ans2 = inquirer.prompt(q)

		print(row[0])
		print(ans2['fixed_image'])
		print(row[2])
		print("\r\n")

		q2 = [inquirer.Confirm('correct', message="Are these values correct?")]

		ans3 = inquirer.prompt(q2)

		if ans3['correct']:
			check = commit([row[0], ans2['fixed_image'], row[2]])

			finish_up(conn, c, row[0], check)

		else:
			incorrect([row[0], ans2['fixed_image'], row[2]], conn, c)

	elif ans['incorrect_value'] == 'Address':
		q = [inquirer.Text('fixed_address', message="Edit address", default=row[2])]
		ans2 = inquirer.prompt(q)

		print(row[0])
		print(row[1])
		print(ans2['fixed_address'])
		print("\r\n")

		q2 = [inquirer.Confirm('correct', message="Are these values correct?")]

		ans3 = inquirer.prompt(q2)

		if ans3['correct']:
			check = commit([row[0], row[1], ans2['fixed_address']])

			finish_up(conn, c, row[0], check)

		else:
			incorrect([row[0], row[1], ans2['fixed_address']], conn, c)


def finish_up(conn, c, name, check):
	time = pendulum.now().format("YYYY-MM-DD")

	data = [name, time, True, check]

	c.execute("INSERT INTO Station_Flags(Name, Date_commited, Commited, Check_sation) VALUES(?, ?, ?, ?)", data)

	conn.commit()

app = typer.Typer()

@app.command()
def compare_all():
	conn = sqlite3.connect("/home/seth/python/scraper/cache.db")
	c = conn.cursor()

	c.execute("SELECT Name, Image, Address FROM Stations")
	
	rows = c.fetchall()

	for row in rows:
		if unique(row):
			continue

		question = [inquirer.Confirm('correct', message="Are these values correct?")]

		for item in row:
			print(item)

		ans = inquirer.prompt(question)

		if ans['correct']:
			check = commit(row)

			finish_up(conn, c, row[0], check)

		else:
			q = [inquirer.Confirm('skip', message="Do you want to skip?")]
			ans2 = inquirer.prompt(q)
			if not ans2['skip']:
				incorrect(row, conn, c)
			else:
				pass

@app.command()
def compare_time_since(days: int, months: int = 0, years: int = 0):
	conn = sqlite3.connect("/home/seth/python/scraper/cache.db")
	c = conn.cursor()

	today = pendulum.now()

	time = today.subtract(years=years, months=months, days=days)

	c.execute("SELECT Stations.Name, Stations.Image, Stations.Address FROM Stations, Station_Flags WHERE Stations.Name = Station_Flags.Name And Station_Flags.Date_commited <= ?", [time.format('YYYY-MM-DD')])
	
	rows = c.fetchall()

	for row in rows:
		if unique(row):
			continue

		question = [inquirer.Confirm('correct', message="Are these values correct?")]

		for item in row:
			print(item)

		ans = inquirer.prompt(question)

		if ans['correct']:
			check = commit(row)

			finish_up(conn, c, row[0], check)

		else:
			q = [inquirer.Confirm('skip', message="Do you want to skip?")]
			ans2 = inquirer.prompt(q)
			if not ans2['skip']:
				incorrect(row, conn, c)
			else:
				pass

@app.command()
def compare_time_manual(date: str):
	conn = sqlite3.connect("/home/seth/python/scraper/cache.db")
	c = conn.cursor()

	c.execute("SELECT Stations.Name, Stations.Image, Stations.Address FROM Stations WHERE Stations.Name = Station_Flags.Name And Station_Flags.Date_commited <= ?", [date])
	
	rows = c.fetchall()

	for row in rows:
		if unique(row):
			continue

		question = [inquirer.Confirm('correct', message="Are these values correct?")]

		for item in row:
			print(item)

		ans = inquirer.prompt(question)

		if ans['correct']:
			check = commit(row)

			finish_up(conn, c, row[0], check)

		else:
			q = [inquirer.Confirm('skip', message="Do you want to skip?")]
			ans2 = inquirer.prompt(q)
			if not ans2['skip']:
				incorrect(row, conn, c)
			else:
				pass



@app.command()
def epoch():
	conn = sqlite3.connect("/home/seth/python/scraper/cache.db")
	c = conn.cursor()

	c.execute("CREATE TABLE Station_Flags(Name text, Date_commited text, Commited bit, Check_sation bit);")

	conn.commit()
	conn.close()

@app.command()
def test():
	print(unique(['toyama', 'image', 'https://musicbird-hls.leanstream.co/musicbird/JCB057.stream/playlist.m3u8']))

if __name__ == '__main__':
	app()
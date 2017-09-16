import requests, cookielib
import re
import cookielib
from pymongo import MongoClient
from bs4 import BeautifulSoup




class Crawler:
	def __init__(self):
		agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36'
		headers = {
			'User-Agent': agent
		}

		self.session = requests.session()
		self.session.headers = headers
		self.session.cookie = cookielib.LWPCookieJar()
		self.website = 'https://en.wikipedia.org'
		self.resultpath = '/Users/qwer_zcc/Files/week3/crawl/result/'
		self.imgpath = '/Users/qwer_zcc/Files/week3/crawl/img/'
		self.total = 0
		self.client = MongoClient('localhost', 27017)
		self.db = self.client.wiki
		self.collection = self.db.people
		self.names = dict()




	def get_string(self, c):
		res = []
		try:
			if (c.contents[0].name == 'br'):
				res.append('<br>')

		except:
			pass

		if (len(c.contents) == 1):
			if (len(c.get_text()) > 2):
				res.append(c.get_text())
			return res


		for content in c.contents:
			s = self.get_string(BeautifulSoup(str(content.encode('utf-8')), 'html.parser'))
			for si in s:
				res.append(si)
			


		return res


	def getString(self, td):
		tdstr = ""
		s = str(td)
		valid = False 
		for i in xrange(0, len(s)):
			if (s[i] == '>'):
				if (s[i-3:i] == '<br'):
					tdstr = tdstr + "<br>"
				valid = True
			elif (s[i] == '<') :
				valid = False
			elif (valid == True and s[i] != '\n'):
				tdstr = tdstr + s[i]
		return tdstr


	def Insert(self, people):
		if (not people['name'] in self.names):
			self.total = self.total + 1
			self.names[people['name']] = True
			print self.total, people['name'], self.collection.insert_one(people).inserted_id
		

	def extractPeople(self, text):
		soup = BeautifulSoup(text, 'html.parser')
		tables = soup.find_all('table', attrs = {'class': 'infobox'})
		if (len(tables)):
			table = tables[0]
			trs = table.find_all('tr')

			imageurl =  'http:' + table.find_all('a', attrs = {'class': 'image'})[0].find_all('img')[0]['src']

			thlist = []
			tdlist = []

			valid = False


			for tr in trs:
				ths = tr.find_all('th')
				tds = tr.find_all('td')

				full_string = []

				thstr = ""
				tdstr = ""

				for th in ths:
					thstr = self.getString(th)
					if (thstr == 'Born'):
						valid = True

				for td in tds:
					tdstr = self.getString(td)

				thlist.append([thstr, tdstr])

			if (valid == False):
				return

		
			people = {
				'id': self.total,
				'name': thlist[0][0],
				'image': imageurl,
				'row': thlist,
			}
			self.Insert(people)



	def saveImage(self, url, path):
		url = 'http:' + url
		r = self.session.get(url)
		with open(path, 'wb') as code:
			for chunk in r.iter_content(chunk_size = 1024):
				code.write(chunk)


	def extractList(self, text):
		soup = BeautifulSoup(text, 'html.parser')
		for link in soup.find_all('a'):
			try:
				if (link['href'][:6] == '/wiki/'):
					self.extractPeople(self.crawl(self.website + link['href']))

			except:
			  pass

	def extractLists(self):
		s = self.pageList
		for page in s:
			print 'Start extracting ' + page
			self.extractList(self.crawl(page))

	def extractMainPage(self, text):
		self.pageList = []
		s = self.pageList
		soup = BeautifulSoup(text, 'html.parser')
		for link in soup.find_all('a'):
			try:
				if (link['href'][:10] == '/wiki/List'):
					s.append(self.website + link['href'])
				
			except:
				pass

		self.extractLists()


	
	def crawlMainPage(self, url):
		text = self.crawl(url)
		self.extractMainPage(text)



	def crawl(self, url):
		s = self.session
		page = ""
		try:
			page = s.get(url)
			return page.text.encode('utf-8')
		except:
			print 'error'
			return ""

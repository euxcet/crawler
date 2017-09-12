import requests, cookielib
import cookielib
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


	def extractPeople(self, text):
		soup = BeautifulSoup(text, 'html.parser')
		table = soup.find_all('table', attrs = {'class': 'infobox'})
		if (len(table)):
			t = table[0]

			title = t.find_all('th')
			info = t.find_all('td')


			if (len(info) > 1 and title[1].get_text() == 'Born'):

				filename = self.resultpath + "".join(title[0].get_text().split(' ')) + '.txt'
				imgname = self.imgpath + "".join(title[0].get_text().split(' ')) + '.jpg'

				img = t.find_all('a', attrs = {'class': 'image'})
				self.saveImage(img[0].find_all('img')[0]['src'], imgname)


				output = open(filename, 'w')
				output.write(title[0].get_text().encode('utf-8') + '\n')
				for i in xrange(1, len(title)):
					output.write("\n*** " + title[i].get_text().encode('utf-8') + " ***\n")
					output.write(str(info[i]) + '\n')



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
		print url
		s = self.session
		page = s.get(url, timeout = 1)
		return page.text.encode('utf-8')

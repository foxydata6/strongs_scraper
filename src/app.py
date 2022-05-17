from bs4 import BeautifulSoup, NavigableString, Comment
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import Select
from pathlib import Path
import pandas as pd
import logging
import time
import sys
import re
import os

# set logging verbosity 
logging.basicConfig(stream=sys.stdout, level=logging.INFO)  # set to logging.DEBUG in development
logger = logging.getLogger()

class ScrapeStrongConcordance(object):

	def __init__(self
		,driver
		,search_terms
		,version
		,home_page='https://www.eliyah.com/lexicon.html'):

		self.driver = driver
		self.search_terms = search_terms
		self.version = version
		self.home_page = home_page
		self.out_dir = Path.joinpath(Path(__file__).resolve().parents[1], 'scraped_docs', self.version)

	def _create_dir(self):

		if not os.path.exists(self.out_dir):

			logging.info(f'Creating dir: {self.out_dir}')
			os.makedirs(self.out_dir)

	def _load_home_page(self):
		
		# Load home page
		self.driver.get(self.home_page)

	def _search_on_term(self,search_term,version):

		# Load home page
		self._load_home_page()

		# Locate search box
		search = self.driver.find_element_by_xpath('/html/body/main/div/div[1]/div/form/div/div/div[2]/div/input')

		# If applicable, clear previous search
		search.clear()

		# Select version
		select = Select(self.driver.find_element_by_xpath('/html/body/main/div/div[1]/div/form/div/div/div[1]/select'))
		select.select_by_value(version)

		# Search on specified term
		search.send_keys(search_term, Keys.RETURN)

		time.sleep(5)

	def _build_dct(self,search_term,version):

		chp_dct = []

		# Scrape HTML soup
		soup = BeautifulSoup(self.driver.page_source,'lxml')

		# Each verse in the chapter is a row in the master table
		trows = soup.findAll('div',id=re.compile('verse_*'))

		for trow in trows:
			tcols = trow.findAll('div')

			# Each verse has a hyperlink we must click to get hebrew translation
			# Extract reference div
			reference_link_parts = tcols[1].find('a')['href']
			# Extract reference id
			referenced_link_id = reference_link_parts.split('_')[1]
			reference_link_begin = '/'.join(reference_link_parts.split('/')[:-1])
			# Finally, fully qualified URL
			reference_link_full = 'https://www.blueletterbible.org'+reference_link_begin+'/t_conc_'+referenced_link_id
			self.driver.get(reference_link_full)
			time.sleep(10)

			# Once hyperlink is open, rescrape HTML soup
			soup = BeautifulSoup(self.driver.page_source,'lxml')

			# Each verse is made up of verse parts
			verse_part_table = soup.find('div',{'id':'concTable'})

			# For each part of the verse, there is a row in the table
			for trow in verse_part_table.findAll('div',{'class':'row'}):

				# Define reference
				verse = self.driver.find_element_by_xpath('//*[@id="HebText_Formatted"]').text.split(" ")[0]

				# Initialize dct
				dct={}
				dct['bible_version'] = version
				dct['bible_book'] = search_term.split(" ")[0]
				dct['bible_chapter'] = search_term.split(" ")[1]
				dct['bible_verse'] = dct['bible_book'] + verse

				# Columns in the table are divs 
				tcols = trow.findAll('div')

				#### Column 1 = English word(s)
				english_words=tcols[0].findAll('a')
				words=[]
				for word in english_words:
					words.append(word.text)
				english_verse_part = ' '.join(words)

				if 'PHRASE' in english_verse_part:
					dct['verse_part_type'] = 'PHRASE'
				else:
					dct['verse_part_type'] = 'WORD'
				dct['verse_part'] = english_verse_part.split('PHRASE')[0].strip()

				### Column 2: Hebrew word ID
				try:
					hebrew_id = tcols[1].find('a')
					dct['hebrew_id'] = hebrew_id.text.upper()
				except:
					dct['hebrew_id'] = None

				chp_dct.append(dct)
		
		chp_dct = pd.DataFrame(chp_dct)

		return chp_dct

	def _iterate_over_search_terms(self):

		book_dct = []

		for term in self.search_terms:

			logging.info(f'****** Starting {term}:{self.version} ******')

			self._search_on_term(term,self.version)

			chp_dct = self._build_dct(term,self.version)
			book_dct.append(chp_dct)

		self.driver.close()
			
		bible_book = self.search_terms[0].split(" ")[0]
		book_dct_df = pd.concat(book_dct).reset_index(drop=True)

		# Create version directory if it does not exist yet
		self._create_dir()
		book_dct_df.to_csv(Path.joinpath(self.out_dir, f'{bible_book}.csv'),index=False)

	def _run_app(self):

		self._iterate_over_search_terms()





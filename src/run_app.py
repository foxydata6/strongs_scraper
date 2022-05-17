from src.driver.connect import define_driver
from src.app import ScrapeStrongConcordance
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import os

# load env variables
load_dotenv()
version = os.getenv('version')

driver = define_driver()
search_terms = pd.read_csv(Path.joinpath(Path(__file__).resolve().parents[1], 'documents', 'search_terms.csv'))
# Convert search_terms to list
search_terms = search_terms['search_terms'].tolist()

Scraper = ScrapeStrongConcordance(driver=driver,search_terms=search_terms,version=version)
Scraper._run_app()
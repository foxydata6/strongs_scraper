from src.driver.connect import define_driver
from src.app import ScrapeStrongConcordance
from pathlib import Path
import pandas as pd
import os

driver = define_driver()
search_terms = pd.read_csv(Path.joinpath(Path(__file__).resolve().parents[1], 'documents', 'search_terms.csv'))
versions = pd.read_csv(Path.joinpath(Path(__file__).resolve().parents[1], 'documents', 'versions.csv'))

# Convert search_terms / versions to lists
search_terms = search_terms['search_terms'].tolist()
versions = versions['versions'].tolist()
versions = versions[4:]

Scraper = ScrapeStrongConcordance(driver=driver,search_terms=search_terms,versions=versions)
Scraper._run_app()
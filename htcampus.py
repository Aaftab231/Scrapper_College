import requests
from bs4 import BeautifulSoup
import logging
from pymongo import MongoClient
from typing import List, Dict, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client.eduwise
cat_collection = db.categories
clgs_collection = db.colleges
courses_collection = db.courses

sitename = "http://www.htcampus.com/"

def safe_request(url: str) -> Optional[requests.Response]:
    """Safely make HTTP requests and handle exceptions."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch URL: {url} - {e}")
        return None

def build_full_url(link: str) -> str:
    """Ensure URLs are complete with the sitename if needed."""
    return link if 'htcampus.com' in link else sitename + link.lstrip('/')

def get_main_categories(nav: BeautifulSoup) -> List[Dict[str, str]]:
    """Scrape main categories from the navigation menu."""
    main_cat_dict = []
    main_cat_nodes = nav.find_all('li', attrs={"class": "lvl"})

    for li in main_cat_nodes:
        if 'more' in li.get('class', []):
            child_lis = li.find_all('li', attrs={'class': 'lvl1-list'})
            for cli in child_lis:
                main_cat_dict.append(build_category(cli))
        else:
            main_cat_dict.append(build_category(li))

    return main_cat_dict

def build_category(li: BeautifulSoup) -> Dict[str, str]:
    """Helper function to build category dictionaries."""
    href = li.find('a').get('href')
    return {
        'name': li.find('a').get_text(),
        'parent_id': '0',
        'description': '',
        'image': '',
        'url': build_full_url(href)
    }

def save_main_categories_to_db(main_cats: List[Dict[str, str]]):
    """Save main categories to the MongoDB collection."""
    if not main_cats:
        logger.info("No main categories to save.")
        return

    for rec in main_cats:
        if cat_collection.find_one({'url': rec['url']}):
            logger.info(f'[~] Category already saved: {rec["name"]}')
        else:
            cat_collection.insert_one(rec)
            logger.info(f'[~] Saving new category: {rec["name"]}')

def get_sub_categories(main_cat_url: str, parent_id: str) -> List[Dict[str, str]]:
    """Scrape subcategories for a given main category."""
    response = safe_request(main_cat_url)
    if not response:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    subcats = soup.find_all('div', attrs={"class": "js-stream-block"})
    subcat_list = []

    for subcat_li in subcats:
        subcathref = subcat_li.find('a').get('href')
        image = subcat_li.find('img').get('src')
        url = build_full_url(subcathref)
        subcat_list.append({
            'parent_id': parent_id,
            'description': '',
            'image': image,
            'url': url,
            'total_colleges': subcat_li.find('p').get_text().split('Colleges')[0].strip(),
            'name': subcat_li.find('h3').get_text()
        })

    return subcat_list

def save_sub_categories_to_db(sub_cats: List[Dict[str, str]]):
    """Save subcategories to the MongoDB collection."""
    if not sub_cats:
        logger.info("No subcategories to save.")
        return

    for rec in sub_cats:
        if cat_collection.find_one({'url': rec['url'], 'parent_id': rec['parent_id']}):
            logger.info(f'[~] Subcategory already saved: {rec["name"]}')
        else:
            cat_collection.insert_one(rec)
            logger.info(f'[~] Saving new subcategory: {rec["name"]}')

def get_colleges(subcat_url: str, subcat_id: str) -> List[Dict[str, str]]:
    """Scrape colleges under a specific subcategory."""
    colleges = []
    response = safe_request(subcat_url)
    if not response:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    colleges_divs = soup.find_all('div', attrs={"class": "college-item"})

    for clg_div in colleges_divs:
        if clg_div.find('div', attrs={"class": "college-tiitle"}):
            college = build_college(clg_div, subcat_id)
            colleges.append(college)

    # Handle pagination
    pagination = soup.find('ul', attrs={"class": "pagination"})
    if pagination:
        next_page = pagination.find_all('li')[-1]
        if next_page.get_text() == 'Next':
            next_url = build_full_url(next_page.find('a').get('href'))
            colleges.extend(get_colleges(next_url, subcat_id))

    return colleges

def build_college(clg_div: BeautifulSoup, subcat_id: str) -> Dict[str, str]:
    """Helper function to build college dictionaries."""
    title_div = clg_div.find('div', attrs={"class": "college-tiitle"}).find('a', attrs={"class": "f20"})
    location = clg_div.find('div', attrs={"class": "college-tiitle"}).find('p')
    link = title_div.get('href')
    url = build_full_url(link)

    college = {
        'subcat_id': subcat_id,
        'name': title_div.get_text(),
        'location': location.get_text(),
        'brochureurl': clg_div.get('data-brochure'),
        'logourl': clg_div.get('data-logo'),
        'url': url
    }

    lidata = clg_div.find('div', attrs={"class": "college-tiitle"}).find_all('li')
    for item in lidata:
        key = item.contents[0].get_text().strip().lower().replace(".", "").replace(" ", "_")
        value = item.contents[1].get_text() if len(item.contents) > 2 else item.contents[0].get_text()
        college[key] = value

    # Fetch additional details from the college page
    fetch_additional_college_details(url, college)

    return college

def fetch_additional_college_details(url: str, college: Dict[str, str]):
    """Fetch more details for a specific college."""
    response = safe_request(url)
    if not response:
        return

    soup = BeautifulSoup(response.text, "lxml")
    highlights = soup.find('div', attrs={"class": "college-highlight"}).find_all('li')
    for item in highlights:
        key = item.find('p', attrs={"class": "text-uppercase"}).get_text().strip().lower().replace(".", "").replace(" ", "_")
        value = item.find_all('div', attrs={"class": "table-cell"})[1].get_text()
        college[key] = value

    course_div = soup.find('div', attrs={"class": "courses"})
    college['total_course'] = course_div.find('h2').find('span').get_text()

def save_colleges_to_db(colleges: List[Dict[str, str]]):
    """Save colleges to the MongoDB collection."""
    if not colleges:
        logger.info("No colleges to save.")
        return

    for rec in colleges:
        if clgs_collection.find_one({'url': rec['url'], 'subcat_id': rec['subcat_id']}):
            logger.info(f'[~] College already saved: {rec["name"]}')
        else:
            clgs_collection.insert_one(rec)
            logger.info(f'[~] Saving new College: {rec["name"]}')

def main():
    logger.info("[+] Scraper is warming up...")
    response = safe_request(sitename)
    if not response:
        return

    soup = BeautifulSoup(response.text, "lxml")
    nav = soup.find(attrs={"class": "nwt"})

    logger.info("[+] Scraping main categories...")
    main_categories = get_main_categories(nav)
    save_main_categories_to_db(main_categories)

    for main_cat in cat_collection.find({'parent_id': '0'}):
        logger.info(f"[+] Scraping subcategories of: {main_cat['name']}")
        subcategories = get_sub_categories(main_cat['url'], str(main_cat['_id']))
        save_sub_categories_to_db(subcategories)

    for sub_cat in cat_collection.find({'parent_id': {"$ne": '0'}}):
        logger.info(f"[+] Scraping colleges of subcategory: {sub_cat['name']}")
        colleges = get_colleges(sub_cat['url'], str(sub_cat['_id']))
        save_colleges_to_db(colleges)

if __name__ == "__main__":
    main()

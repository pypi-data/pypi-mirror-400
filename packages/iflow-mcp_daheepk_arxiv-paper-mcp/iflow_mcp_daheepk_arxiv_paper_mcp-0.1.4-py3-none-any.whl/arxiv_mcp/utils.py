import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import time 
from bs4 import BeautifulSoup
import logging 

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) 

def fetch_arxiv_papers(category: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """arXiv API에서 특정 카테고리의 논문 데이터를 가져옵니다."""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': f'cat:{category}',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'lastUpdatedDate',
        'sortOrder': 'descending'
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return []
    
    root = ET.fromstring(response.content)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/abs/')[-1]
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
        
        authors = []
        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
            name = author.find('{http://www.w3.org/2005/Atom}name').text
            authors.append(name)
        
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
        
        categories = []
        for cat in entry.findall('{http://www.w3.org/2005/Atom}category'):
            term = cat.get('term')
            if term:
                categories.append(term)
        
        pdf_link = None
        for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
            if link.get('title') == 'pdf':
                pdf_link = link.get('href')
                break 
                
        papers.append({
            'id': paper_id,
            'title': title,
            'authors': ", ".join(authors),
            'published': published[:10],  
            'summary': summary,
            'categories': ", ".join(categories), 
            'pdf_url': pdf_link 
        })
    
    return papers

def search_by_keyword(keyword: str, max_results: int = 5, sort_by: str = 'relevance') -> List[Dict[str, Any]]:
    """키워드로 arXiv 논문을 검색합니다. sort_by 파라미터로 정렬 기준을 지정할 수 있습니다 ('relevance' 또는 'submittedDate')."""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': f'all:{keyword}',
        'start': 0,
        'max_results': max_results
    }

    if sort_by == 'submittedDate':
        params['sortBy'] = 'submittedDate'
        params['sortOrder'] = 'descending'
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return []
    
    root = ET.fromstring(response.content)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/abs/')[-1]
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
        
        authors = []
        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
            name = author.find('{http://www.w3.org/2005/Atom}name').text
            authors.append(name)
        
        summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
        published = entry.find('{http://www.w3.org/2005/Atom}published').text.strip()

        categories = []
        for cat in entry.findall('{http://www.w3.org/2005/Atom}category'):
            term = cat.get('term')
            if term:
                categories.append(term)

        pdf_link = None
        for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
            if link.get('title') == 'pdf':
                pdf_link = link.get('href')
                break 

        papers.append({
            'id': paper_id,
            'title': title,
            'authors': ", ".join(authors),
            'summary': summary,
            'published': published, 
            'categories': ", ".join(categories), 
            'pdf_url': pdf_link 
        })
    
    return papers

def get_paper_details(paper_id: str) -> Optional[Dict[str, Any]]:
    """논문 ID로 상세 정보를 가져옵니다."""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'id_list': paper_id
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return None
    
    root = ET.fromstring(response.content)
    entries = root.findall('{http://www.w3.org/2005/Atom}entry')
    
    if not entries:
        return None
    
    entry = entries[0]
    
    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
    published = entry.find('{http://www.w3.org/2005/Atom}published').text
    summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
    
    authors = []
    for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
        name = author.find('{http://www.w3.org/2005/Atom}name').text
        authors.append(name)
    
    categories = []
    for category in entry.findall('{http://www.w3.org/2005/Atom}category'):
        term = category.get('term')
        if term:
            categories.append(term)
    
    doi = None
    for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
        if link.get('title') == 'doi':
            doi = link.get('href')
    
    return {
        'id': paper_id,
        'title': title,
        'authors': ", ".join(authors),
        'published': published[:10],  
        'summary': summary,
        'categories': ", ".join(categories),
        'doi': doi
    }

def scrape_recent_papers(category: str, max_results: int = 25) -> List[Dict[str, str]]:
    """특정 카테고리의 arXiv 'recent' 페이지를 크롤링하여 오늘 날짜의 논문 ID와 제목 목록을 가져옵니다."""
    logger.debug(f"--- scrape_recent_papers function entered for category: {category} ---") 
    recent_url = f"https://arxiv.org/list/{category}/recent"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    logger.info(f"Scraping recent papers from: {recent_url}") 

    try:
        response = requests.get(recent_url, headers=headers, timeout=15)
        response.raise_for_status() 
        time.sleep(0.5) 

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error fetching {recent_url}") 
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {recent_url}: {e}") 
        return []

    soup = BeautifulSoup(response.content, 'lxml')
    papers = []

    definition_list = soup.find('dl')
    logger.debug(f"Found definition list: {definition_list}")
    if not definition_list:
        logger.warning(f"Could not find the definition list (<dl>) on {recent_url}") 
        return []

    dt_tags = definition_list.find_all('dt')
    logger.debug(f"Found dt tags: {dt_tags}")
    logger.debug(f"Found {len(dt_tags)} <dt> tags.") 

    count = 0
    for dt in dt_tags:
        if count >= max_results:
            break

        dd = dt.find_next_sibling('dd')
        if not dd:
            logger.warning(f"Warning: Could not find corresponding <dd> for a <dt> tag.") 
            continue
            
        paper_info = {}
        
        extracted_id = None
        abstract_link = dt.find('a', title='Abstract') 
        
        if abstract_link and abstract_link.get('id'):
            extracted_id = abstract_link.get('id')
            paper_info['id'] = extracted_id
            paper_info['link'] = f"https://arxiv.org/abs/{extracted_id}"
            paper_info['pdf_link'] = f"https://arxiv.org/pdf/{extracted_id}"
            logger.debug(f"Extracted ID: {extracted_id} from abstract link")
        else:
            logger.warning(f"Could not find abstract link or its ID within dt: {dt.prettify()}")

        title_div = dd.find('div', class_='list-title')
        logger.debug(f"Found title div: {title_div}")
        extracted_title = None
        if title_div:
            title_text_parts = []
            for content in title_div.contents:
                if content.name == 'span' and 'descriptor' in content.get('class', []):
                    continue
                if isinstance(content, str):
                    title_text_parts.append(content.strip())
                elif hasattr(content, 'get_text'):
                     title_text_parts.append(content.get_text(strip=True))
            
            full_title = " ".join(filter(None, title_text_parts)).strip().strip('"')
            extracted_title = full_title
            paper_info['title'] = extracted_title
            logger.debug(f"Extracted title: {extracted_title[:50]}...") 
        else:
            logger.warning(f"Could not find title div within dd: {dd}")
 
        author_div = dd.find('div', class_='list-authors')
        extracted_authors = None
        if author_div:
            author_tags = author_div.find_all('a')
            if author_tags:
                authors_list = [tag.get_text(strip=True) for tag in author_tags]
                extracted_authors = ", ".join(authors_list)
                paper_info['authors'] = extracted_authors
                logger.debug(f"Extracted Authors: {extracted_authors[:50]}...") 
            else:
                logger.debug(f"Found author div, but no anchor tags within: {author_div.prettify()}")
        else:
            logger.debug(f"Could not find author div within dd: {dd.prettify()}")
 
        category_div = dd.find('div', class_='list-subjects')
        logger.debug(f"Found category div: {category_div}") 
        extracted_categories = None
        if category_div:
            category_tags = category_div.find_all('span', class_='primary-subject')
            if category_tags:
                categories_list = [tag.get_text(strip=True) for tag in category_tags]
                extracted_categories = ", ".join(categories_list)
                paper_info['categories'] = extracted_categories
                logger.debug(f"Extracted Categories: {extracted_categories[:50]}...") 
            else:
                logger.debug(f"Found category div, but no span tags within: {category_div.prettify()}")
        else:
            logger.debug(f"Could not find category div within dd: {dd.prettify()}")
              
        if 'id' in paper_info:
            logger.debug(f"Fetching additional details for paper ID: {paper_info['id']}")
            try:
                paper_details = get_paper_details(paper_info['id'])
                if paper_details:
                    if 'summary' in paper_details:
                        paper_info['summary'] = paper_details['summary']
                        logger.debug(f"Added summary for paper ID: {paper_info['id']}")
                    
                    if 'published' in paper_details:
                        paper_info['published'] = paper_details['published']
                        logger.debug(f"Added published date for paper ID: {paper_info['id']}")
            except Exception as e:
                logger.warning(f"Error fetching additional details for paper ID {paper_info['id']}: {e}")

            papers.append(paper_info)
            count += 1
        else:
            logger.warning(f"Failed to add entry - Missing ID or Title. ID={extracted_id}, Title Exists={extracted_title is not None}, Authors Exists={extracted_authors is not None}") 

    logger.info(f"Successfully extracted {len(papers)} papers for category {category}.") 
    return papers


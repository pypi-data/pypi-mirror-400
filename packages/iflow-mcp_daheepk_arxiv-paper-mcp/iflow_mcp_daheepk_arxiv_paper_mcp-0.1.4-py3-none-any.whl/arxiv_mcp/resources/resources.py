import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

from arxiv_mcp.app import mcp
from arxiv_mcp import utils

@mcp.resource("arxiv://{category}")
def get_papers_by_category(category: str) -> str:
    """특정 카테고리의 최신 arXiv 논문을 가져옵니다."""
    papers = utils.fetch_arxiv_papers(category)
    
    if not papers:
        return f"카테고리 '{category}'에서 논문을 찾을 수 없습니다."
    
    result = f"## arXiv '{category}' 카테고리 최신 논문\n\n"
    for i, paper in enumerate(papers, 1):
        result += f"### {i}. {paper['title']}\n"
        result += f"**저자**: {paper['authors']}\n"
        result += f"**날짜**: {paper['published']}\n"
        result += f"**ID**: {paper['id']}\n"
        if 'categories' in paper and paper['categories']:
            result += f"**카테고리**: {paper['categories']}\n"
        result += f"**요약**: {paper['summary'][:300]}...\n\n"
    
    return result

@mcp.resource("author://{name}")
def get_papers_by_author(name: str) -> str:
    """특정 저자의 arXiv 논문을 가져옵니다."""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': f'au:"{name}"',
        'start': 0,
        'max_results': 10
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return f"저자 검색 중 오류 발생: {response.status_code}"
    
    root = ET.fromstring(response.content)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
        paper_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/abs/')[-1]
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        
        papers.append({
            'title': title,
            'id': paper_id,
            'published': published[:10] 
        })
    
    if not papers:
        return f"저자 '{name}'의 논문을 찾을 수 없습니다."
    
    result = f"## 저자 '{name}'의 arXiv 논문 목록\n\n"
    for i, paper in enumerate(papers, 1):
        result += f"{i}. **{paper['title']}**\n"
        result += f"   출판일: {paper['published']}\n"
        result += f"   ID: {paper['id']}\n\n"
    
    return result

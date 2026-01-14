import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

from arxiv_mcp.app import mcp
from arxiv_mcp import utils


@mcp.tool()
def scrape_recent_category_papers(category: str, max_results: int = 10) -> str:
    """[크롤링] 특정 카테고리의 'recent' 페이지를 스크랩하여 최신 논문 목록을 가져옵니다."""
    
    papers = utils.scrape_recent_papers(category, max_results)
    
    if not papers:
        return f"'{category}' 카테고리의 최신 논문 목록을 웹 페이지에서 가져올 수 없습니다."
    
    result = f"## arXiv '{category}' 카테고리 최신 논문 목록\n\n"
    for i, paper in enumerate(papers, 1):
        result += f"### {i}. {paper.get('title', '제목 없음')}\n"
        result += f"**ID**: {paper.get('id', 'ID 없음')}\n"
        result += f"**저자**: {paper.get('authors', '저자 정보 없음')}\n"
        if 'published' in paper:
            result += f"**출판일**: {paper.get('published', '출판일 정보 없음')}\n"
        if 'categories' in paper:
            result += f"**카테고리**: {paper.get('categories', '카테고리 정보 없음')}\n"
        result += f"**arXiv 링크**: {paper.get('link', '링크 없음')}\n"
        result += f"**PDF 링크**: {paper.get('pdf_link', 'PDF 링크 없음')}\n"
        if 'summary' in paper:
            summary = paper.get('summary', '')
            summary_preview = summary[:200] + ('...' if len(summary) > 200 else '')
            result += f"**초록**: {summary_preview}\n"
        result += "\n"
        
    return result

    
@mcp.tool()
def search_papers(keyword: str, max_results: int = 5) -> str:
    """키워드로 arXiv 논문을 검색합니다."""

    papers = utils.search_by_keyword(keyword, max_results)
    
    if not papers:
        return f"'{keyword}' 관련 논문을 찾을 수 없습니다."
    
    result = f"## '{keyword}' 검색 결과\n\n"
    for i, paper in enumerate(papers, 1):
        result += f"### {i}. {paper['title']}\n"
        result += f"**저자**: {paper['authors']}\n"
        result += f"**ID**: {paper['id']}\n"
        if 'categories' in paper and paper['categories']:
            result += f"**카테고리**: {paper['categories']}\n"
        result += f"**요약**: {paper['summary'][:200]}...\n"
        if 'published' in paper:
            result += f"**출판일**: {paper['published'][:10]}\n\n"
        else:
            result += "\n"

    return result

@mcp.tool()
def get_paper_info(paper_id: str) -> str:
    """논문 ID로 상세 정보를 가져옵니다."""
    paper = utils.get_paper_details(paper_id)
    
    if not paper:
        return f"ID '{paper_id}'에 해당하는 논문을 찾을 수 없습니다."
    
    result = f"## 논문 상세 정보\n\n"
    result += f"### {paper['title']}\n\n"
    result += f"**저자**: {paper['authors']}\n"
    result += f"**출판일**: {paper['published']}\n"
    result += f"**카테고리**: {paper['categories']}\n"
    result += f"**DOI**: {paper.get('doi', '정보 없음')}\n"
    result += f"**링크**: https://arxiv.org/abs/{paper_id}\n"
    result += f"**PDF**: https://arxiv.org/pdf/{paper_id}.pdf\n\n"
    result += f"**초록**:\n{paper['summary']}\n"
    
    return result

@mcp.tool()
def analyze_trends(category: str = "cs.AI", days: int = 30) -> str:
    """특정 카테고리의 최신 트렌드를 분석합니다."""
 
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': f'cat:{category}',
        'start': 0,
        'max_results': 100,  
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return f"트렌드 분석 중 오류 발생: {response.status_code}"
    
    root = ET.fromstring(response.content)

    result = f"## {category} 분야 최근 {days}일 트렌드 분석\n\n"
    result += "### 인기 키워드 (임시 데이터)\n"
    result += "1. 대규모 언어 모델 (LLM)\n"
    result += "2. 강화학습\n"
    result += "3. 자기지도학습\n"
    result += "4. 멀티모달\n"
    result += "5. 생성형 AI\n\n"
    
    result += "### 인기 논문 주제 (임시 데이터)\n"
    result += "1. AI 모델의 해석 가능성\n"
    result += "2. 효율적인 미세 조정 방법\n"
    result += "3. 인간 피드백을 통한 강화학습\n"
    
    return result


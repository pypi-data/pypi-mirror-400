from arxiv_mcp.app import mcp
from arxiv_mcp import utils

@mcp.prompt()
def summarize_paper(paper_id: str) -> str:
    """논문 ID를 입력받아 해당 논문을 쉽게 요약합니다."""
    paper = utils.get_paper_details(paper_id)
    
    if not paper:
        return f"ID '{paper_id}'에 해당하는 논문을 찾을 수 없습니다."
    
    return f"""
다음 arXiv 논문을 중학생도 이해할 수 있게 쉽게 요약해주세요:

제목: {paper['title']}

저자: {paper['authors']}

초록: {paper['summary']}

다음 형식으로 요약해주세요:
1. 이 논문이 해결하려는 문제
2. 연구자들이 사용한 방법
3. 주요 결과 및 중요성
4. 중학생을 위한 쉬운 비유나 예시
"""

@mcp.prompt()
def compare_papers(paper_id1: str, paper_id2: str) -> str:
    """두 논문을 비교 분석합니다."""
    paper1 = utils.get_paper_details(paper_id1)
    paper2 = utils.get_paper_details(paper_id2)
    
    if not paper1 or not paper2:
        return f"하나 이상의 논문 ID가 올바르지 않습니다."
    
    return f"""
다음 두 arXiv 논문을 비교 분석해주세요:

논문 1:
- 제목: {paper1['title']}
- 저자: {paper1['authors']}
- 초록: {paper1['summary']}

논문 2:
- 제목: {paper2['title']}
- 저자: {paper2['authors']}
- 초록: {paper2['summary']}

다음 항목에 따라 비교해주세요:
1. 두 논문의 주요 목표/목적 비교
2. 사용된 방법론 비교
3. 결과 및 주장 비교
4. 연구의 한계점
5. 어떤 논문이 더 혁신적인지 또는 영향력이 클지에 대한 분석
"""




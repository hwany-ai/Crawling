import os
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class UniversalCrawler:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 각 매거진별 설정 (URL과 기사 링크 판별 키워드)
        self.targets = [
            {"name": "allure", "url": "https://www.allure.com/hair-ideas", "base": "https://www.allure.com", "keywords": ["/story/", "/gallery/"]},
            {"name": "byrdie", "url": "https://www.byrdie.com/hair-styling-4628405", "base": "https://www.byrdie.com", "keywords": ["hair"]},
            {"name": "marieclaire", "url": "https://www.marieclaire.com/beauty/hair/", "base": "https://www.marieclaire.com", "keywords": ["/beauty/", "hair"]},
            {"name": "harpersbazaar", "url": "https://www.harpersbazaar.com/beauty/hair/", "base": "https://www.harpersbazaar.com", "keywords": ["/beauty/hair/a"]},
            {"name": "instyle", "url": "https://www.instyle.com/hair", "base": "https://www.instyle.com", "keywords": ["hair"]},
            {"name": "glamour", "url": "https://www.glamour.com/beauty/hair", "base": "https://www.glamour.com", "keywords": ["/story/", "/gallery/"]},
            {"name": "vogue", "url": "https://www.vogue.com/beauty/hair", "base": "https://www.vogue.com", "keywords": ["/article/"]},
            {"name": "whowhatwear", "url": "https://www.whowhatwear.com/beauty/hair", "base": "https://www.whowhatwear.com", "keywords": ["/beauty/hair/"]},
            {"name": "elle", "url": "https://www.elle.com/beauty/hair/", "base": "https://www.elle.com", "keywords": ["/beauty/hair/a", "/beauty/"]},
            {"name": "trendspotter_women", "url": "https://www.thetrendspotter.net/category/womens-hairstyles/", "base": "https://www.thetrendspotter.net", "keywords": ["hair"]},
            {"name": "gq", "url": "https://www.gq.com/about/hair", "base": "https://www.gq.com", "keywords": ["/story/", "/gallery/"]},
            {"name": "trendspotter_men", "url": "https://www.thetrendspotter.net/category/mens-hairstyles/", "base": "https://www.thetrendspotter.net", "keywords": ["hair"]},
            # 헤어 전문가용/글로벌 등 7개 소스 추가 반영
            {"name": "americansalon", "url": "https://www.americansalon.com/hair-0", "base": "https://www.americansalon.com", "keywords": ["/hair/"]},
            {"name": "beautylaunchpad_cut", "url": "https://www.beautylaunchpad.com/cut", "base": "https://www.beautylaunchpad.com", "keywords": ["/cut/"]},
            {"name": "beautylaunchpad_color", "url": "https://www.beautylaunchpad.com/color", "base": "https://www.beautylaunchpad.com", "keywords": ["/color/"]},
            {"name": "beautylaunchpad_styles", "url": "https://www.beautylaunchpad.com/styles", "base": "https://www.beautylaunchpad.com", "keywords": ["/styles/"]},
            {"name": "hypehair", "url": "https://hypehair.com/category/hair/", "base": "https://hypehair.com", "keywords": ["hair", "/20"]},
            {"name": "hji", "url": "https://hji.co.uk/trends", "base": "https://hji.co.uk", "keywords": ["/trends/"]},
            {"name": "esteticamagazine", "url": "https://www.esteticamagazine.com/category/trends/hair-collection/", "base": "https://www.esteticamagazine.com", "keywords": ["/trends", "/hair", "collection"]}
        ]

    def _is_article_link(self, href, keywords, base_url):
        if not href:
            return False
            
        # exclude basic navigation/category pages
        excludes = ['/about/', '/contact', '/privacy', 'author', 'tag', '/category/', '?page=', 'newsletter', 'subscribe']
        href_lower = href.lower()
        if any(exc in href_lower for exc in excludes):
            return False
            
        # if keywords provided, must contain at least one
        if keywords and keywords[0] != "/":
            if not any(kw in href for kw in keywords):
                return False
                
        # heuristic: article URLs are usually long
        if len(href.split('/')) < 4 and len(href) < 30:
            return False
            
        return True

    def parse_article(self, html, source_name):
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        title_elem = soup.find('h1')
        main_title = title_elem.get_text(strip=True) if title_elem else ""
        
        year = str(datetime.now().year)
        
        # h2, h3 기반 갤러리/리스트 형태 파싱
        headings = soup.find_all(['h2', 'h3'])
        
        if len(headings) >= 2: # listicle
            for heading in headings:
                trend_name = heading.get_text(strip=True)
                if len(trend_name) > 100 or len(trend_name) < 3:
                     continue
                     
                desc_paragraphs = []
                curr = heading.find_next_sibling()
                while curr and curr.name not in ['h2', 'h3', 'h1', 'div']:
                    if curr.name == 'p':
                        text = curr.get_text(strip=True)
                        if text:
                            desc_paragraphs.append(text)
                    curr = curr.find_next_sibling()
                    
                if desc_paragraphs:
                    items.append({
                        "trend_name": trend_name,
                        "year": year,
                        "hairstyle_text": "",
                        "color_text": "",
                        "description": "\n".join(desc_paragraphs),
                        "source": source_name
                    })
                    
        # 리스트 형태가 아니라면 전체 본문 추출
        if not items and main_title:
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True)]
            
            # 본문이 너무 짧으면 제외
            if len("\n".join(paragraphs)) > 100:
                items.append({
                    "trend_name": main_title,
                    "year": year,
                    "hairstyle_text": "",
                    "color_text": "",
                    "description": "\n".join(paragraphs),
                    "source": source_name
                })
                
        return items

    def crawl(self):
        print("======== [Universal Crawler] 모든 매거진 크롤링 시작 ========")
        
        with sync_playwright() as p:
            # 안티 크롤링 우회를 위해 브라우저 설정 추가
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()

            for target in self.targets:
                name = target['name']
                url = target['url']
                base_url = target['base']
                keywords = target['keywords']
                
                print(f"\n--- [{name}] 탐색 시작 ({url}) ---")
                
                try:
                    page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    time.sleep(2) # 로딩 대기
                    
                    # 스크롤해서 추가 콘텐츠 로드 유도
                    page.mouse.wheel(0, 2000)
                    time.sleep(2)
                    
                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    links = set()
                    for a in soup.find_all('a', href=True):
                        href = a['href']
                        if self._is_article_link(href, keywords, base_url):
                            full_url = href if href.startswith('http') else base_url + href
                            links.add(full_url)
                            
                    target_links = list(links)[:8] # 각 카테고리별 최대 8개 기사 탐색
                    
                    if not target_links:
                        print(f"[{name}] 기사 링크를 찾지 못했습니다.")
                        continue
                        
                    results = []
                    for act_url in target_links:
                        print(f"  -> [{name}] 수집 중: {act_url}")
                        try:
                            page.goto(act_url, timeout=30000, wait_until="domcontentloaded")
                            time.sleep(1.5)
                            
                            art_html = page.content()
                            items = self.parse_article(art_html, name.capitalize())
                            results.extend(items)
                        except Exception as e:
                            print(f"  -> [{name}] 페이지 수집 에러 ({act_url}): {e}")
                            
                    # 중복 제거
                    unique_results = []
                    seen = set()
                    for r in results:
                        key = r['trend_name'] + str(r['description'])[:30]
                        if key not in seen:
                            seen.add(key)
                            unique_results.append(r)
                            
                    output_path = os.path.join(self.data_dir, f'{name}.json')
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(unique_results, f, ensure_ascii=False, indent=2)
                    print(f"--- [{name}] 완료. {len(unique_results)}개 아이템 저장됨 ---")

                except Exception as e:
                    print(f"[{name}] 접근 실패: {e}")
                    
            browser.close()

if __name__ == '__main__':
    UniversalCrawler().crawl()

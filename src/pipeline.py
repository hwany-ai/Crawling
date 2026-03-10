import os
import time
from datetime import datetime

from .instagram_playwright import InstagramPlaywrightCrawler
from .magazine_crawler import MagazineCrawler
from .blog_crawler import BlogCrawler
from .youtube_crawler import YoutubeCrawler

def run_pipeline():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 헤어 트렌드 데이터 수집 파이프라인 시작...\n")
    
    # 현재 연도 및 계절 동적 추출
    now = datetime.now()
    current_year = now.year
    month = now.month
    
    if month in [3, 4, 5]:
        season = "봄"
        en_season = "SS" # Spring/Summer (패션 뷰티계는 보통 SS/FW로 나눔)
    elif month in [6, 7, 8]:
        season = "여름"
        en_season = "SS"
    elif month in [9, 10, 11]:
        season = "가을"
        en_season = "FW" # Fall/Winter
    else:
        season = "겨울"
        en_season = "FW"
    
    # 설정값 (실전용 대량 수집)
    # 특정 컷트 이름은 배제하고, 현재 연도/계절 기반의 남녀 대표 헤어 트렌드 키워드만 사용
    keywords = [
        f"{current_year}여자머리스타일", f"{current_year}남자머리스타일", 
        f"{current_year}{season}헤어스타일", f"{current_year}{season}염색추천", 
        f"{current_year}{en_season}헤어트렌드", f"{en_season}헤어스타일",
        f"{season}여자머리", f"{season}남자머리",
        f"{current_year}헤어트렌드", "여자헤어스타일추천", "남자헤어스타일추천"
    ]
    instagram_max_posts = 20    # 키워드당 20개 (약 160개)
    magazine_max_pages = 4      # 보그, 얼루어 각각 4페이지 분량 기사 (약 160~200개 기사)
    blog_max_posts = 15         # 키워드당 15개 (약 120개) 
    youtube_max_videos = 10     # 키워드당 10개 (약 80개)
    
    # ==== 1. 인스타그램 데이터 수집 ====
    try:
        print("\n" + "="*50)
        print("1. Instagram 데이터 수집 파이프라인 실행")
        print("="*50)
        ig_crawler = InstagramPlaywrightCrawler()
        for kw in keywords:
            ig_crawler.crawl_by_keyword(kw, max_posts=instagram_max_posts)
            time.sleep(3) # 키워드간 딜레이
    except Exception as e:
        print(f"Instagram 크롤링 중 에러 발생: {e}")

    # ==== 2. 매거진 데이터 수집 ====
    try:
        print("\n" + "="*50)
        print("2. Magazine (Vogue, Allure) 데이터 수집 파이프라인 실행")
        print("="*50)
        mg_crawler = MagazineCrawler()
        mg_crawler.crawl_magazine('vogue', max_pages=magazine_max_pages)
        time.sleep(2)
        mg_crawler.crawl_magazine('allure', max_pages=magazine_max_pages)
    except Exception as e:
        print(f"Magazine 크롤링 중 에러 발생: {e}")

    # ==== 3. 네이버 블로그 데이터 수집 ====
    try:
        print("\n" + "="*50)
        print("3. Naver Blog 데이터 수집 파이프라인 실행")
        print("="*50)
        blog_crawler = BlogCrawler()
        for kw in keywords:
            blog_crawler.crawl_naver_blog(kw, max_posts=blog_max_posts)
            time.sleep(3) # 키워드간 딜레이
    except Exception as e:
        print(f"Blog 크롤링 중 에러 발생: {e}")
        
    # ==== 4. 유튜브 데이터 수집 ====
    try:
        print("\n" + "="*50)
        print("4. YouTube 데이터 수집 파이프라인 실행")
        print("="*50)
        youtube_crawler = YoutubeCrawler()
        for kw in keywords:
            youtube_crawler.crawl_youtube(kw, max_videos=youtube_max_videos)
            time.sleep(3) # 키워드간 딜레이
    except Exception as e:
        print(f"YouTube 크롤링 중 에러 발생: {e}")
        
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 헤어 트렌드 데이터 수집 파이프라인 완료!")

if __name__ == "__main__":
    run_pipeline()

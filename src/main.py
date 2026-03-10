import time
from universal_crawler import UniversalCrawler
from data_refiner import DataRefiner

def main():
    print("====== 헤어 트렌드 크롤링 파이프라인 시작 ======")
    
    # 1. 통합 매거진 (12개 소스) 크롤러 실행
    try:
        uc = UniversalCrawler()
        uc.crawl()
    except Exception as e:
        print(f"UniversalCrawler 크롤링 실행 중 예외 발생: {e}")
        
    time.sleep(2)
        
    print("====== 전체 크롤링 파이프라인 종료 ======")
    print("====== 데이터 정제(Refiner) 파이프라인 시작 ======")
    
    # 3. 데이터 통합 및 정제 파이프라인 실행
    try:
        refiner = DataRefiner()
        refiner.refine()
    except Exception as e:
        print(f"DataRefiner 실행 중 예외 발생: {e}")

if __name__ == '__main__':
    main()

import os
import json
import re
from collections import Counter
from konlpy.tag import Okt
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib.font_manager as fm

# 한글 폰트 설정 (Mac)
plt.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False 

class KeywordAnalyzer:
    def __init__(self):
        self.okt = Okt()
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis_results')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 제외할 불용어 (Stopwords) 리스트 - 분석에 방해되는 무의미한 단어들
        self.stopwords = [
            '수', '것', '이', '그', '저', '있', '하', '같', '에', '에서', '으로', '로',
            '곳', '분', '머리', '헤어', '스타일', '스타일링', '추천', '많이', '정말', '너무',
            '진짜', '요즘', '오늘', '지금', '유행', '트렌드', '년', '월', '일', '시', '분',
            '디자이너', '원장', '미용실', '고객', '시술', '진행', '생각', '느낌', '이미지',
            '얼굴', '사람', '우리', '나', '저희', '이번', '그냥', '항상', '조금'
        ]

    def clean_text(self, text):
        """특수문자 및 영어 일부 제거, 단순 텍스트만 남기기"""
        if not isinstance(text, str):
             text = str(text)
        # 한글, 영문, 숫자 외 공백으로 치환
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
        return text

    def extract_nouns(self, text):
        """Okt 형태소 분석기를 이용해 명사 추출 후 불용어 제거"""
        cleaned_text = self.clean_text(text)
        nouns = self.okt.nouns(cleaned_text)
        # 2글자 이상, 불용어 미포함 단어만 필터링
        filtered_nouns = [word for word in nouns if len(word) >= 2 and word not in self.stopwords]
        return filtered_nouns

    def load_all_data(self):
        """data 디렉토리 하위의 모든 json 파일에서 텍스트와 해시태그 수집"""
        all_text = ""
        all_hashtags = []
        
        print("데이터 로딩 중...")
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            for item in data:
                                # 본문 텍스트 합치기
                                if 'content' in item and item['content']:
                                    all_text += " " + item['content']
                                # 해시태그 합치기
                                if 'hashtags' in item and item['hashtags']:
                                    # # 제거 후 합치기
                                    tags = [tag.replace('#', '') for tag in item['hashtags']]
                                    all_hashtags.extend(tags)
                    except Exception as e:
                        print(f"파일 읽기 에러 ({file}): {e}")
                        
        return all_text, all_hashtags

    def analyze_and_visualize(self):
        all_text, all_hashtags = self.load_all_data()
        
        if not all_text and not all_hashtags:
            print("분석할 데이터가 없습니다.")
            return

        print(f"총 {len(all_text)} 글자의 텍스트, {len(all_hashtags)}개의 해시태그 로드 완료.")
        
        # 1. 명사 추출 및 빈도 계산
        print("명사 추출 및 빈도 계산 중 (시간이 소요될 수 있습니다)...")
        nouns = self.extract_nouns(all_text)
        
        # 본문 명사 빈도 
        noun_counts = Counter(nouns)
        top_30_nouns = noun_counts.most_common(30)
        
        # 2. 해시태그 빈도 계산 (해시태그는 추출된 단어 그 자체를 하나의 묶음으로 봅니다)
        # 불용어 해시태그도 없애줌
        refined_hashtags = [t for t in all_hashtags if t not in self.stopwords and len(t) > 1]
        hashtag_counts = Counter(refined_hashtags)
        top_30_hashtags = hashtag_counts.most_common(30)
        
        # 결과 출력
        print("\n==== [TOP 20 많이 언급된 키워드 (본문)] ====")
        for word, count in top_30_nouns[:20]:
            print(f"- {word}: {count}회")
            
        print("\n==== [TOP 20 많이 쓰인 해시태그] ====")
        for tag, count in top_30_hashtags[:20]:
            print(f"- #{tag}: {count}회")
            
        # 3. 빈도 데이터 저장 (CSV 형태 저장 용도 등)
        result_dict = {
            "top_nouns": dict(top_30_nouns),
            "top_hashtags": dict(top_30_hashtags)
        }
        with open(os.path.join(self.output_dir, 'keyword_frequency.json'), 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)

        # 4. 워드클라우드 시각화 생성
        print("\n워드클라우드 생성 중...")
        wordcloud_noun = WordCloud(
            font_path='/System/Library/Fonts/AppleSDGothicNeo.ttc', # Mac 폰트 경로
            width=800, height=800, 
            background_color='white',
            colormap='viridis'
        ).generate_from_frequencies(noun_counts)
        
        wordcloud_hashtag = WordCloud(
            font_path='/System/Library/Fonts/AppleSDGothicNeo.ttc',
            width=800, height=800, 
            background_color='white',
            colormap='plasma'
        ).generate_from_frequencies(hashtag_counts)
        
        # 그림 저장
        plt.figure(figsize=(16, 8))
        
        plt.subplot(1, 2, 1)
        plt.imshow(wordcloud_noun, interpolation='bilinear')
        plt.title('Top Keywords from Contents', fontsize=20)
        plt.axis("off")
        
        plt.subplot(1, 2, 2)
        plt.imshow(wordcloud_hashtag, interpolation='bilinear')
        plt.title('Top Hashtags', fontsize=20)
        plt.axis("off")
        
        figure_path = os.path.join(self.output_dir, 'trend_wordcloud.png')
        plt.tight_layout()
        plt.savefig(figure_path)
        print(f"시각화 이미지가 저장되었습니다: {figure_path}")

if __name__ == "__main__":
    analyzer = KeywordAnalyzer()
    analyzer.analyze_and_visualize()

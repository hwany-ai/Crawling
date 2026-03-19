# Global Hair Trend RAG Pipeline

이 리포지토리는 글로벌·한국 헤어/뷰티 매거진에서 최신 트렌드 기사를 크롤링하고, LLM(Gemini)을 활용해 정제한 후, ChromaDB 벡터 DB + GPT API 기반 RAG(Retrieval-Augmented Generation) 시스템으로 헤어 트렌드를 검색·답변하는 풀 파이프라인입니다.

---

## 🚀 파이프라인 특징

- **총 27개 소스 지원**
  - **글로벌 매거진 (19개)**: `Vogue`, `Allure`, `InStyle`, `GQ`, `Elle`, `Marie Claire`, `Glamour`, `Harper's Bazaar`, `Byrdie`, `Who What Wear`, `Cosmopolitan`, `American Salon`, `Estetica`, `Beauty Launchpad` 등
  - **한국 매거진 (8개)**: `W Korea`, `Elle Korea`, `Vogue Korea`, `Harper's Bazaar Korea`, `Marie Claire Korea`, `GQ Korea`, `Cosmopolitan Korea`, `Allure Korea`
- **LLM 데이터 필터링**: 불필요한 제품 광고, 얕은 리뷰 등을 걸러내고, `style_trend`, `color_trend`, `celebrity_example`, `styling_guide`, `drop` 등의 카테고리로 엄격하게 분류합니다.
- **ChromaDB 벡터화**: 다국어 임베딩 모델(`paraphrase-multilingual-MiniLM-L12-v2`)로 한영 혼합 데이터를 벡터화합니다.
- **GPT RAG 챗봇**: ChromaDB 검색 결과를 GPT API에 컨텍스트로 전달하여 헤어 트렌드 전문 답변을 생성합니다.

---

## 🛠 환경 설정 (Prerequisites)

### 1. 패키지 설치

```bash
git pull origin main
pip install -r requirements.txt
```

주요 의존성: `playwright`, `beautifulsoup4`, `google-genai`, `chromadb`, `sentence-transformers`, `openai`, `python-dotenv`

### 2. 브라우저 엔진 설치

```bash
playwright install chromium
```

### 3. API 키 설정

프로젝트 루트에 `.env` 파일을 만들고 아래 키를 설정하세요.

```env
# .env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

---

## ⚡ 실행 순서

### STEP 1) 크롤링

27개 매거진에서 최신 헤어 트렌드 기사를 크롤링합니다.

```bash
python src/universal_crawler.py
```
> **산출물**: `data/` 폴더에 매거진별 JSON 파일 생성

### STEP 2) 1차 정제

크롤링된 JSON을 통합하고 기초 정제(특수문자, 구조 정리)를 수행합니다.

```bash
python src/data_refiner.py
```
> **산출물**: `data/refined_trends.json`

### STEP 3) LLM 정제

Gemini가 데이터를 카테고리화하고, RAG 스키마로 변환합니다.

```bash
python src/llm_refiner.py
```
> **산출물**: `data/final_rag_trends.json`

### STEP 4) 벡터DB 생성

정제된 데이터를 ChromaDB에 벡터화하여 저장합니다.

```bash
python src/vectorize_chromadb.py
```
> **산출물**: `data/chromadb/` (로컬 영속 저장)

### STEP 5) RAG 챗봇 실행

ChromaDB + GPT API 기반 대화형 헤어 트렌드 컨설턴트를 실행합니다.

```bash
python src/rag_query.py
```

---

## 🧠 벡터화 & 저장소 스택

| 구분 | 기술 | 설명 |
|------|------|------|
| **벡터 DB** | [ChromaDB](https://www.trychroma.com/) | 로컬 영속 저장 (`PersistentClient`), 별도 서버 불필요 |
| **임베딩 모델** | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 50개 이상 언어 지원, 한영 혼합 데이터에 최적화된 384차원 임베딩 |
| **검색 방식** | L2 거리 (유클리드) | ChromaDB 기본 유사도 측정, 거리가 낮을수록 관련성 높음 |
| **LLM (정제)** | Google Gemini 2.5 Flash | 크롤링 데이터 카테고리화 및 RAG 스키마 변환 |
| **LLM (답변)** | OpenAI GPT-4o-mini | 검색된 컨텍스트 기반 답변 생성 + 쿼리 확장 |

---

## 🔍 RAG 시스템 구조

```
사용자 질문
    │
    ▼
[쿼리 확장] GPT가 짧은 질문을 한영 키워드로 확장
    │
    ▼
[벡터 검색] ChromaDB에서 유사 문서 TOP 10 검색
    │
    ▼
[컨텍스트 구성] 검색 결과를 구조화된 참고 자료로 변환
    │
    ▼
[답변 생성] GPT-4o-mini가 참고 자료 기반으로 답변
    │
    ▼
헤어 트렌드 추천 (출처 포함)
```

### 주요 특징
- **쿼리 확장**: "여자머리는?" → 한영 키워드로 자동 확장하여 검색 정확도 향상
- **다국어 임베딩**: 한국어/영어 혼합 데이터를 동일 벡터 공간에서 검색
- **출처 기반 답변**: 모든 추천에 매거진 출처와 연도를 명시

---

## 📁 프로젝트 구조

```
crawling_git/
├── src/
│   ├── universal_crawler.py   # STEP 1: 27개 매거진 크롤러
│   ├── data_refiner.py        # STEP 2: 데이터 통합/1차 정제
│   ├── llm_refiner.py         # STEP 3: Gemini LLM 정제
│   ├── vectorize_chromadb.py  # STEP 4: ChromaDB 벡터화
│   └── rag_query.py           # STEP 5: GPT RAG 챗봇
├── data/
│   ├── *.json                 # 매거진별 크롤링 데이터
│   ├── refined_trends.json    # 1차 정제 데이터
│   ├── final_rag_trends.json  # 최종 RAG 데이터
│   └── chromadb/              # 벡터DB (gitignore)
├── .env                       # API 키 (gitignore)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🇰🇷 한국 매거진 소스

| 매거진 | URL | 카테고리 |
|--------|-----|----------|
| W Korea | https://www.wkorea.com/beauty/ | 뷰티 전반 |
| Elle Korea | https://www.elle.co.kr/beauty | 뷰티 전반 |
| Vogue Korea | https://www.vogue.co.kr/beauty/ | 뷰티 전반 |
| Harper's Bazaar Korea | https://www.harpersbazaar.co.kr/beauty | 뷰티 전반 |
| Marie Claire Korea | https://www.marieclairekorea.com/category/beauty/beauty_trend/ | 뷰티 트렌드 |
| GQ Korea | https://www.gqkorea.co.kr/style/grooming/ | 남성 그루밍 |
| Cosmopolitan Korea | https://www.cosmopolitan.co.kr/beauty | 뷰티 전반 |
| Allure Korea | https://www.allurekorea.com/beauty/hair/ | 헤어 전문 |

# Global Hair Trend RAG Pipeline

이 리포지토리는 글로벌 헤어/뷰티 매거진과 전문가용 살롱 매거진에서 최신 트렌드 기사를 크롤링하고, LLM(Gemini)을 활용해 RAG(Retrieval-Augmented Generation) 시스템에 직접 주입할 수 있을 정도로 문서를 완벽하게 정제 및 카테고리화하는 파이프라인입니다.

---

## 🚀 파이프라인 특징

- **총 19개 소스 지원**: `Vogue`, `Allure`, `InStyle`, `GQ` 등 하이엔드 대중 매거진부터 `American Salon`, `Estetica`, `Beauty Launchpad` 등 헤어 전문가 대상 글로벌 B2B 매거진까지 폭넓은 커버리지를 가집니다.
- **LLM 데이터 필터링**: 불필요한 제품 광고, 얕은 리뷰 등을 걸러내고, `style_trend`, `color_trend`, `celebrity_example`, `styling_guide`, `drop` 등의 카테고리로 엄격하게 분류합니다.
- **RAG 최적화 JSON 생성**: `canonical_name`(정규화된 트렌드명), `search_text`(검색/임베딩 최적화 병합 문자열) 등 벡터 DB에 가장 잘 맞도록 설계된 스키마 구조를 가집니다.

자세한 데이터 분석 및 아키텍처 문서는 프로젝트 내 `rag_data_documentation.md` (또는 아티팩트 보관함)를 확인하세요.

---

## 🛠 환경 설정 (Prerequisites)

이 프로젝트를 실행하기 위해 패키지 의존성과 외부 API 키를 설정해야 합니다.

### 1. 프로젝트 업데이트 및 패키지 설치
최신 코드를 받아온 후, 가상환경을 구성하고 필요한 패키지들을 설치하세요. 가상환경(`venv`)은 단말기/환경마다 다르고 용량이 커서 Git에 포함되지 않으므로, 직접 생성해야 합니다.

```bash
# 1. 최신 코드 불러오기 (필요시)
git pull origin main

# 2. 가상환경(venv) 생성 (최초 1회)
python -m venv venv

# 3. 가상환경 활성화
source venv/bin/activate
# (Windows의 경우: venv\Scripts\activate)

# 4. 의존성 패키지 설치
pip install -r requirements.txt
```
*(기본적으로 `playwright`, `beautifulsoup4`, `google-genai`, `python-dotenv` 등이 포함됩니다.)*

### 2. 브라우저 엔진 설치 
웹 스크래핑을 위해 Playwright가 요구하는 자체 브라우저 바이너리를 설치해야 합니다.
```bash
playwright install chromium
```

### 3. API 키 설정
최종 LLM 정제 과정을 실행하려면 구글(Gemini API) 키가 반드시 필요합니다.
프로젝트 최상단 루트 디렉터리에 `.env` 파일을 만들고 아래 코드를 기입하세요.
```env
# .env
GEMINI_API_KEY=당신의_제미나이_API_키를_여기에_붙여넣으세요
```

---

## ⚡ 스크립트 실행 순서 (How to Get Data)

파이프라인은 데이터 수집(Crawling), 물리적 정제(Refining), LLM 논리적 정제(LLM Refining) 3단계로 이루어져 있습니다. 아래의 순서대로 스크립트를 실행하면 깨끗한 RAG용 데이터가 떨어집니다.

### STEP 1) 전체 매거진 크롤링 
Playwright를 이용해 병렬/비동기적으로 19개의 타겟 사이트를 방문하여 최신 헤어 기사 내용을 긁어옵니다. 이 명령어는 수분이 소요될 수 있습니다.
```bash
python src/universal_crawler.py
```
> **산출물**: `data/` 폴더 내에 매거진별 원본 데이터 (`allure.json`, `vogue.json`, `gq.json` 등)가 저장됩니다.

### STEP 2) 데이터 통합 및 1차 정제
크롤링된 모든 사이트의 분리된 JSON들을 하나의 거대한 파일로 압축/통합하고, 가장 기초적인 특수문자 및 구조 정제를 진행합니다.
```bash
python src/data_refiner.py
```
> **산출물**: 매거진별 파일들이 통합되어 1개의 `data/refined_trends.json` 파일이 생성됩니다.

### STEP 3) LLM 카테고리화 및 RAG 스키마 변환
Gemini 2.5 Flash 모델이 이 통합된 문서(수백 건)를 모두 읽으면서 쓸데없는 데이터를 통째로 버리고(`drop`), 살아남은 데이터를 정형화된 JSON 배열 스키마로 가공합니다.
```bash
python src/llm_refiner.py
```
> **산출물**: 가장 순수하고 엄격히 정제된 최종 DB인 **`data/final_rag_trends.json`** 이 탄생합니다! 이 데이터를 Pinecone, Milvus 등의 벡터 서치나 Langchain 파이프라인에 그대로 연결하시면 됩니다.

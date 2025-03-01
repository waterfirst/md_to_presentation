# 성공 사례 연구 웹사이트

![성공 사례 웹사이트](https://via.placeholder.com/800x400?text=Success+Case+Studies+Website)

성공 사례 연구 웹사이트는 프리랜서, 1인 기업가, SaaS 비즈니스 운영자들의 성공 스토리를 공유하는 Streamlit 기반 웹 애플리케이션입니다. 마크다운 형식의 사례 연구를 쉽게 웹사이트로 변환하고 광고를 통해 수익화할 수 있습니다.

## 🚀 주요 기능

- **사례 연구 전시**: 다양한 성공 사례를 카테고리별로 제공
- **반응형 디자인**: 모바일과 데스크톱 모두에서 최적화된 사용자 경험
- **광고 통합**: Google AdSense 및 기타 광고 플랫폼 통합 지원
- **SEO 최적화**: 검색 엔진 최적화를 위한 메타데이터 및 구조화된 콘텐츠
- **뉴스레터 구독**: 사용자 이메일 수집 및 뉴스레터 구독 기능
- **소셜 미디어 공유**: 콘텐츠를 쉽게 공유할 수 있는 기능

## 📋 설치 방법

### 필수 요구 사항

- Python 3.8 이상
- Git

### 로컬 설치

1. 저장소 클론하기
```bash
git clone https://github.com/yourusername/success-case-studies.git
cd success-case-studies
```

2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 애플리케이션 실행
```bash
streamlit run app.py
```

## 🌐 Streamlit Cloud 배포

이 프로젝트는 [Streamlit Cloud](https://streamlit.io/cloud)를 통해 쉽게 배포할 수 있습니다:

1. GitHub에 프로젝트 푸시
2. Streamlit Cloud에 로그인
3. "New app" 버튼 클릭
4. GitHub 저장소 연결 및 main 브랜치 선택
5. app.py 파일 지정
6. "Deploy" 버튼 클릭

## 🗂️ 프로젝트 구조

```
success-case-studies/
├── app.py                  # 메인 Streamlit 애플리케이션
├── requirements.txt        # 필요한 Python 패키지
├── README.md               # 프로젝트 설명
├── .gitignore              # Git 무시 파일
├── assets/                 # 이미지 및 기타 정적 파일
├── data/                   # 사례 연구 마크다운 파일
│   ├── saas/               # SaaS 관련 사례 연구
│   ├── freelancers/        # 프리랜서 관련 사례 연구
│   └── solopreneurs/       # 1인 기업가 관련 사례 연구
├── components/             # 재사용 가능한 UI 컴포넌트
└── utils/                  # 유틸리티 함수 (마크다운 파서, 광고 유틸 등)
```

## 📊 광고 수익화 설정

이 웹사이트는 다음과 같은 방법으로 광고 수익화를 지원합니다:

1. **Google AdSense 통합**
   - utils/ads.py의 함수를 사용하여 AdSense 광고 코드 삽입
   - components/ads_banner.py를 통한 광고 배너 컴포넌트

2. **애필리에이트 링크 통합**
   - 사례 연구에서 언급된 제품/서비스에 대한 제휴 링크
   - components/product_card.py를 통한 제품 카드 컴포넌트

3. **맞춤형 스폰서십**
   - components/sponsor_banner.py를 통한 스폰서 배너 표시

## 📈 성능 모니터링

웹사이트 성능과 수익을 모니터링하려면:

1. `streamlit-analytics` 라이브러리를 사용하여 기본 방문자 통계 추적
2. Google Analytics 통합을 위한 components/analytics.py 사용
3. utils/revenue_tracker.py로 AdSense 및 제휴 수익 추적

## 🤝 기여하기

기여는 언제나 환영합니다! 다음과 같은 방법으로 기여할 수 있습니다:

1. 이슈 생성
2. 새로운 사례 연구 제안
3. 풀 리퀘스트 제출
4. 코드 리뷰

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

질문이나 피드백이 있으시면 [이메일](mailto:your.email@example.com) 또는 GitHub 이슈를 통해 연락해 주세요.

---

**성공 사례 연구 웹사이트**로 비즈니스 인사이트를 공유하고 영감을 주세요! 🚀

# Multi-agent-Retirement-Planner
멀티 에이전트 기반 퇴직연금 전략 분석 및 추천 서비스 
<img width="1077" alt="KakaoTalk_20250405_214427119" src="https://github.com/user-attachments/assets/45ae236e-5977-4c04-90e5-a48d8879b7dc" />

## 🧑‍💻 Contributors

|김현규|이윤아|조수현|김태한
|:----:|:----:|:----:|:----:|
|[<img src="https://avatars.githubusercontent.com/u/79504450?v=4" alt="" style="width:100px;100px;">](https://github.com/NerdCat822) <br/> | [<img src="https://avatars.githubusercontent.com/u/35857011?v=4" alt="" style="width:100px;100px;">](https://github.com/YOONAHLEE) <br/> | [<img src="https://avatars.githubusercontent.com/u/28627345?v=4" alt="" style="width:100px;100px;">](https://github.com/Suhyeon4780) <br/> | [<img src="https://avatars.githubusercontent.com/u/84124094?v=4" alt="" style="width:100px;100px;">](https://github.com/taehan79-kim) <br/> |

## 🤖 AI Agent Structure
### 1. Supervisor Agent
- 사용자의 입력을 분성하여 적절한 하위 에이전트에게 전달
- 사용자 대화 히스토리 및 메모리 관리

### 2. Pension Information Agent
- 다양한 연금 정보 및 혜택에 대한 정보 제공
- 퇴직 연금 관련 자주 묻는 질문에 답변
- 벡터 데이터베이스(Vector DB)를 기반 정보 검색 지원

### 3. Tax Strategy Agent
- 퇴직 연금 및 IRP 납입 시 세액 공제 수치 제공
- 연금 수령 방식 별 세부 절세 플랜 제공
- 벡터 데이터베이스(Vector DB)를 기반 정보 검색 지원

### 4. Finance Report Agent
- 배치 데이터 크롤링을 통한 시장 뉴스 및 지표 추출
- 시장 리서치 보고서 작성
- 마켓 리포트 요약 및 주요 시사점 제공

### 5. Pension Analytics Agent
- ETF, 펀드, 채권의 수익률 분석
- 개인 맞춤형 최적화 포트폴리오 제안
- 최적의 운용 전략 추천

# pyLoa

> 로스트아크 API를 위한 Python 래퍼 라이브러리

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-104%20passed-brightgreen.svg)]()

## 개요

`pyLoa`는 [로스트아크 공식 OpenAPI](https://developer-lostark.game.onstove.com/)를 위한 직관적이고 사용하기 쉬운 Python 래퍼 라이브러리입니다.

### 주요 기능

- **직관적인 인터페이스**: API 엔드포인트가 자연스럽게 메서드로 매핑
- **타입 안정성**: Type hints를 통한 IDE 자동완성 및 타입 체크 지원
- **자동 Rate Limiting**: API 제한(분당 100 요청)을 자동으로 처리
- **간단한 인증**: API 키만으로 쉽게 초기화
- **풍부한 모델링**: API 응답을 Python 객체로 자동 변환


## 시작하기

### API 키 발급

1. [로스트아크 개발자 포털](https://developer-lostark.game.onstove.com/)에 접속
2. 계정으로 로그인
3. [클라이언트 생성](https://developer-lostark.game.onstove.com/clients)에서 새 클라이언트 생성
4. 발급받은 JWT 토큰 복사

### 기본 사용법

```python
from pyloa import LostArkAPI

# 1. 클라이언트 초기화
api = LostArkAPI(api_key="your_jwt_token_here")

# 2. 진행 중인 이벤트 조회
events = api.news.get_events()
for event in events:
    print(f"{event.title}: {event.start_date} ~ {event.end_date}")

# 3. 캐릭터 정보 조회
siblings = api.characters.get_siblings("캐릭터명")
for char in siblings:
    print(f"{char.character_name} ({char.server_name}): {char.item_avg_level}")

# 4. 캐릭터 프로필 상세 조회
profile = api.armories.get_profile("캐릭터명")
print(f"{profile.character_name} 레벨: {profile.character_level}")
if profile.stats:
    for stat in profile.stats:
        print(f"{stat.type}: {stat.value}")

# 5. 거래소 아이템 검색
result = api.markets.search_items(ItemName="파괴강석", CategoryCode=50000)
print(f"총 {result.total_count}개 검색됨")
for item in result.items:
    print(f"{item.name}: {item.current_min_price}골드")
```

## API 문서

### 주요 엔드포인트

#### News (뉴스/공지)

```python
# 공지사항 조회
notices = api.news.get_notices(searchText="점검", type="점검")

# 진행 중인 이벤트 조회
events = api.news.get_events()
```

#### Characters (캐릭터 기본 정보)

```python
# 계정의 모든 캐릭터 목록 조회
siblings = api.characters.get_siblings("캐릭터명")
```

#### Armories (캐릭터 상세 정보)

```python
# 캐릭터 종합 정보 조회 (필터 사용)
total = api.armories.get_total_info(
    "캐릭터명",
    filters=["profiles", "equipment", "gems"]
)

# 캐릭터 프로필
profile = api.armories.get_profile("캐릭터명")

# 장비 정보
equipment = api.armories.get_equipment("캐릭터명")

# 아바타 정보
avatars = api.armories.get_avatars("캐릭터명")

# 전투 스킬
skills = api.armories.get_combat_skills("캐릭터명")

# 각인 정보
engravings = api.armories.get_engravings("캐릭터명")

# 카드 정보
cards = api.armories.get_cards("캐릭터명")

# 보석 정보
gems = api.armories.get_gems("캐릭터명")
```

#### Markets (거래소)

```python
# 거래소 검색 옵션 조회 (Dict 리턴)
options = api.markets.get_options()

# 특정 아이템 정보 조회 (MarketItem)
item = api.markets.get_item(item_id=66110221)

# 아이템 검색 (Market)
result = api.markets.search_items(
    CategoryCode=50000,
    ItemName="파괴강석",
    PageNo=1
)

# 최근 거래 내역 (List[TradeMarketItem])
trades = api.markets.get_trades(ItemName="파괴강석")
```

#### Auctions (경매장)

```python
# 경매장 검색 옵션 조회
options = api.auctions.get_options()

# 경매장 아이템 검색 (Auction)
result = api.auctions.get_items(
    CategoryCode=200000,
    ItemGrade="유물",
    ItemTier=3,
    PageNo=1
)
```

#### Game Contents (게임 컨텐츠)

```python
# 주간 캘린더 정보 (ContentsCalendar)
calendar = api.game_contents.get_calendar()
```


### 고급 사용법

#### Rate Limiting 처리

`pyLoa`는 자동으로 Rate Limiting을 처리합니다. API 제한(분당 100 요청)에 도달하면 자동으로 대기합니다.

```python
# Rate Limiting은 자동으로 처리되므로 별도 작업 불필요
for i in range(200):
    # 100번째 요청 후 자동으로 대기
    api.news.get_events()
```

#### 에러 처리

```python
from pyloa import LostArkAPI, APIError, AuthenticationError, RateLimitError

api = LostArkAPI(api_key="your_jwt_token")

try:
    character = api.characters.get_siblings("존재하지않는캐릭터")
except AuthenticationError:
    print("API 키가 잘못되었습니다.")
except APIError as e:
    print(f"API 오류 발생: {e}")
```

## 프로젝트 구조

```
pyLoa/
├── pyloa/                  # 메인 패키지
│   ├── __init__.py        # 패키지 초기화, 주요 클래스 내보내기
│   ├── client.py          # LostArkAPI 메인 클라이언트
│   ├── rate_limiter.py    # Rate Limiting 처리
│   ├── exceptions.py      # 커스텀 예외 정의
│   ├── endpoints/         # API 엔드포인트 모듈
│   │   ├── base.py       # BaseEndpoint 추상 클래스
│   │   ├── news.py       # 뉴스/공지 엔드포인트
│   │   ├── characters.py # 캐릭터 기본 정보 엔드포인트
│   │   ├── armories.py   # 캐릭터 상세 정보 엔드포인트
│   │   ├── markets.py    # 거래소 엔드포인트
│   │   ├── auctions.py   # 경매장 엔드포인트
│   │   └── game_contents.py # 게임 컨텐츠 엔드포인트
│   └── models/            # 데이터 모델
│       ├── base.py       # BaseModel 추상 클래스
│       ├── character.py  # 캐릭터 관련 모델
│       ├── armory.py     # Armory 관련 모델
│       ├── market.py     # 거래소 관련 모델
│       ├── auction.py    # 경매장 관련 모델
│       ├── news.py       # 뉴스 관련 모델
│       └── game_content.py # 게임 컨텐츠 관련 모델
├── docs/                  # 문서 및 다이어그램
│   ├── architecture.mmd   # 아키텍처 다이어그램 Mermaid 소스
│   └── architecture_diagram.png # 아키텍처 다이어그램 이미지
├── tests/                 # 테스트 코드
├── requirements.txt       # 의존성 패키지
├── setup.py              # 패키지 설정
└── README.md             # 프로젝트 문서 (본 파일)
```

## 아키텍처

`pyLoa`는 다음과 같은 계층 구조로 설계되었습니다:

![pyLoa 아키텍처 클래스 다이어그램](./docs/architecture_diagram.png)


### 핵심 계층

1. **Client Layer** (`LostArkAPI`): 모든 API 접근의 진입점
2. **Endpoint Layer** (`BaseEndpoint` 및 하위 클래스): 각 API 카테고리별 메서드 제공
3. **Model Layer** (`BaseModel` 및 하위 클래스): API 응답 데이터를 Python 객체로 변환
4. **Utility Layer** (`RateLimiter`, `exceptions`): 공통 유틸리티 기능

## 관련 링크

- [로스트아크 개발자 포털](https://developer-lostark.game.onstove.com/)

**Note**: 이 라이브러리는 비공식 프로젝트이며, Smilegate 또는 Lost Ark와 공식적인 관련이 없습니다.

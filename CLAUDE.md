# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 개발 명령어

- `npm run dev` - 핫 리로드가 있는 개발 서버 시작
- `npm run build` - 프로덕션 빌드
- `npm run preview` - 프로덕션 빌드 로컬 미리보기

## 프로젝트 개요

**인형뽑기 가게 지도 링크 웹 앱**을 개발하는 Vue 3 + Vite 프로젝트입니다.

### 주요 요구사항
- 모바일 친화적 웹 앱, 반응형 디자인
- 가게 리스트: 이름, 주소 표시
- 지도 바로가기 버튼 (Google Maps / Naver Maps)
- JSON 데이터 기반 가게 정보 관리
- 검색 필터 기능: 가게 이름/주소 검색 가능
- 정적 웹 호스팅 (GitHub Pages)
- Vue 3 + Vuetify 3 기반

### 기술 스택
- **Vue 3** - Composition API와 `<script setup>` SFC 문법 사용
- **Vite** - 빌드 도구 및 개발 서버
- **ES modules** - package.json에서 type: "module" 설정
- **Vuetify 3** - UI 컴포넌트 라이브러리

### 애플리케이션 아키텍처

#### 데이터 구조
- `public/stores.json` - 약 3.3MB 크기의 대용량 가게 데이터 (수천 개 매장)
- 각 가게 객체: `{ id, name, address, phone, google_map, naver_map }`
- 실시간 데이터 로딩 및 청크 단위 처리 구현

#### 핵심 기능 구현
- **필터링 시스템**: 대분류(시/도) → 소분류(구/군) 계층적 필터링
- **검색**: 디바운싱(300ms)을 적용한 실시간 검색
- **정렬**: 기본순/거리순/가나다순 지원
- **지오로케이션**: 사용자 위치 기반 거리순 정렬
- **페이지네이션**: 24개 아이템 단위로 페이지 분할
- **즐겨찾기**: localStorage 기반 즐겨찾기 관리
- **테마**: 라이트/다크 모드 토글

#### 상태 관리
모든 상태는 Vue 3 Composition API의 `ref`와 `computed`로 관리:
- `stores` - 전체 가게 데이터
- `filteredStores` - 필터 적용된 가게 목록
- `searchQuery` - 검색어 (디바운싱 적용)
- `selectedCategory/selectedSubCategory` - 지역 필터
- `userLocation` - 사용자 GPS 위치
- `favorites` - localStorage 연동 즐겨찾기

### 프로젝트 구조
- `src/main.js` - Vuetify 테마 설정 및 Vue 앱 진입점
- `src/App.vue` - 단일 페이지 애플리케이션의 모든 기능을 포함하는 메인 컴포넌트
- `public/stores.json` - 대용량 가게 데이터 (3.3MB)
- `tasks/` - 개발 로그 및 데이터 처리 스크립트
- `index.html` - 한국어 메타데이터가 포함된 HTML 템플릿

### 주요 개발 패턴
- 컴포넌트에서 Vue 3 `<script setup>` 문법 사용
- 스코프드 스타일이 있는 Single File Components (.vue 파일)
- 전체적으로 ES6 import/export 문법 사용
- Vite가 빌드 프로세스와 개발 서버 처리
- localStorage를 활용한 클라이언트 사이드 데이터 저장
- 대용량 데이터 최적화를 위한 청크 로딩 및 페이지네이션
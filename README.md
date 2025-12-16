# 항공권 출력 시스템
## 개요
**항공권 출력 시스템**은 표준화된 형식으로 항공권을 생성하고 출력하도록 설계된 웹 기반 애플리케이션입니다. **백엔드(Python)** 와 **프론트엔드(Node.js 기반)** 애플리케이션으로 구성되어 있으며, 함께 작동하여 원활한 티켓 생성 및 출력 환경을 제공합니다.

이 문서는 Windows 컴퓨터에서 프로젝트를 로컬로 설치, 구성 및 실행하는 방법을 설명합니다.

---

## 시스템 요구사항
시작하기 전에 시스템이 다음 요구사항을 충족하는지 확인하세요:
- **운영체제:** Windows
- **LibreOffice** (티켓 생성/출력에 필요)
- **Python:** 버전 3.11
- **Node.js:** 최신 LTS 권장
- **Git** (선택사항, 저장소 복제용)

---

## 설치 가이드

### 1. LibreOffice 설치
LibreOffice는 문서 처리 및 출력에 필요합니다.

- Windows용 LibreOffice 다운로드 및 설치:
  - 🔗 https://www.libreoffice.org/download/download-libreoffice/

설치 후 LibreOffice가 시스템에 제대로 설치되어 액세스 가능한지 확인하세요.

---

### 2. Python 및 Node.js 설치 확인
**명령 프롬프트(CMD)** 를 열고 설치된 버전을 확인하세요:

```bash
python --version
node --version
```

- Python 버전은 **3.11**이어야 합니다
- Node.js가 설치되어 있고 액세스 가능해야 합니다

Python 또는 Node.js가 설치되어 있지 않은 경우:
- **Python 3.11** 설치 https://www.youtube.com/watch?v=IZYv-4P2nLM
- **Node.js** 설치 https://www.youtube.com/watch?v=lt5D2EWZMN0

설치 후 명령 프롬프트를 다시 시작하세요.

---

### 3. 프로젝트 소스 코드 다운로드
C 드라이브에 github라는 디렉토리를 생성합니다. 디렉토리 내에서 github에서 프로젝트를 복제하거나 Google 드라이브에서 다운로드합니다.

- **옵션 A:** GitHub에서 복제
  ```bash
  git clone https://github.com/shehab-01/airline-ticket-printing-system.git
  ```

- **옵션 B:** Google 드라이브에서 다운로드
  - 🔗 https://drive.google.com/drive/folders/1JhalTYIr8r8w2Bk30BjbLQhE0ID7gmS8?usp=sharing

ZIP 파일로 다운로드한 경우 프로젝트의 압축을 풉니다.

---

### 4. 백엔드 설정 (Python)
1. **명령 프롬프트**를 열고 프로젝트 디렉토리로 이동합니다:
   ```bash
   cd C:\Github\airline-ticket-printing-system
   ```

2. 백엔드 폴더로 이동합니다:
   ```bash
   cd backend
   ```

3. Python 3.11을 사용하여 가상 환경을 생성합니다:
   ```bash
   py -3.11 -m venv .venv
   ```

4. 가상 환경을 활성화합니다:
   ```bash
   .venv\Scripts\activate
   ```

5. 백엔드 종속성을 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```

---

### 5. 프론트엔드 설정 (Node.js)
1. **새 명령 프롬프트 창**을 엽니다

2. 프론트엔드 폴더로 이동합니다:
   ```bash
   cd C:\Github\airline-ticket-printing-system\frontend
   ```

3. 프론트엔드 종속성을 설치합니다:
   ```bash
   npm install
   ```

---

## 애플리케이션 실행

### 1. 백엔드 서버 시작
**백엔드 폴더**에서 (가상 환경이 활성화된 상태로):

```bash
python main.py
```

또는

```bash
python3 main.py
```

이 터미널을 계속 실행 상태로 유지하세요.

---

### 2. 프론트엔드 개발 서버 시작
**프론트엔드 폴더**에서:

```bash
npm run dev
```

---

## 웹 애플리케이션 액세스
백엔드와 프론트엔드 서버가 모두 실행되면 브라우저를 열고 다음으로 이동합니다:

```
http://localhost:3000
```

이제 로컬에서 실행되는 **항공권 출력 시스템** 웹 애플리케이션을 볼 수 있습니다.

---

## 참고사항 및 문제 해결
- 백엔드를 실행하기 전에 **LibreOffice**가 설치되어 있는지 확인하세요.
- 백엔드를 시작하기 전에 항상 Python 가상 환경을 활성화하세요.
- 포트가 이미 사용 중인 경우 다른 서비스를 중지하거나 포트 구성을 업데이트하세요.
- 명령이 인식되지 않는 경우 Python 또는 Node.js 설치 후 CMD를 다시 시작하세요.
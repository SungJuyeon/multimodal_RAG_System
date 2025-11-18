# Node.js image
FROM node:18-alpine

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 복사 및 설치
COPY package.json package-lock.json ./
RUN npm ci

# 애플리케이션 코드 복사
COPY . .

# React 앱 실행
CMD ["npm", "start"]

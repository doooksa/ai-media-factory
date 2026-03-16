# 🚀 AiMedia Factory: Medical Content Automation

Система автоматизации создания контента для медицинского маркетинга. 
Позволяет управлять сетью аккаунтов (Reels, TikTok) и генерировать экспертные AI-сценарии.

## 🛠 Стек технологий
- **Backend:** Python 3.11, Django, DRF (REST Framework)
- **Frontend:** Vue 3 (Composition API), Tailwind CSS v4, Vite
- **Infrastructure:** Docker & Docker Compose
- **Database:** PostgreSQL

## 📦 Архитектура
Проект полностью контейнеризирован. Backend и Frontend работают в изолированных средах, взаимодействуя через REST API.

## 🚀 Быстрый запуск
1. Клонировать репозиторий: `git clone https://github.com/doooksa/ai-media-factory.git`
2. Запустить контейнеры: `docker compose up -d --build`
3. Выполнить миграции: `docker compose exec backend python manage.py migrate`
4. Открыть в браузере: `http://localhost:5173`

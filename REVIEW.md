# Проверка сайта VOYZ Travel — 5 ноября 2026

Проверены исходники и рендер всех 10 действующих страниц (RU/EN): главная, каталог, Grand Expedition, политика, авторы фото. Автоматическая проверка вёрстки: 320, 390, 768, 1024, 1440, 1920, 2560 px в Chromium. Визуально просмотрены главная и программа тура по секциям на телефоне и компьютере; остальные страницы проверены по полным снимкам. Скриншоты воспроизводятся `python visual_check.py` и сохраняются в `shots/`.

Проверка структуры по [Landing Page — Checklist Design](https://www.checklist.design/website/landing-page):

| | Пункт | Что есть |
|---|---|---|
| 🟢 | Headline — A single, clear statement of what the product does or the value it delivers | Первый экран: авторские внедорожные поездки по Кыргызстану |
| 🟢 | Subheadline — A supporting line that adds context or specificity to the headline claim | Направление, формат, небольшая группа |
| 🟢 | Hero visual — An image, illustration, or product screenshot that reinforces the headline and makes the page feel tangible | Реальные озёра/горы, фото и видео |
| 🟢 | Primary CTA — One clear action for the visitor to take (sign up, start a trial, book a demo) | На главной — переход к туру; на туре — запрос программы |
| 🟡 | Social proof — Customer logos, testimonials, review scores, or user counts that validate the claim. | Фото Павла, подтверждённое заявление 60+ поездок, ссылки на отзывы и гостей. Самих отзывов на сайте пока нет; актуальное Instagram требует входа |
| 🟢 | Key benefits — A concise breakdown of the main reasons a visitor should care, focused on outcomes not features. | 6–12 человек, внедорожники, три озера, честное описание нагрузки |
| 🟢 | Objection handling — Content that addresses the most common reasons a visitor would not convert e.g. price, complexity, commitment | FAQ, физическая нагрузка, погода, погранразрешения, ночёвки |
| 🟢 | Repeated CTA — The primary CTA repeated at the bottom of the page for visitors who scroll all the way through | Повторный призыв и форма заявки |

## Исправлено

- Слово Expedition в заголовке тура разрывалось на десктопе: заголовку дана достаточная ширина.
- «Спрашивают» в левой колонке FAQ разрывалось: поправлен масштаб шрифта.
- «Заканчиваются» в заголовке дня 6 не помещалось на 320 px: уменьшен размер заголовков дней на самых узких экранах.
- Кнопки заявки на страницах политики и авторов фото ссылались на отсутствующий блок и не открывали форму: добавлена общая модальная форма.
- В форме были варианты только до 8 человек: теперь 1–12 и «Больше 12»; границы группы флагмана закреплены в JSON и регрессионной проверке.
- Добавлены ссылка на Instagram во всех подвалах, блок о Павле, его фото и опыт из профиля, точные ссылки на актуальное и публикации.
- Instagram на телефоне — горизонтальная лента, все три карточки доступны свайпом. Никаких вымышленных гидов и отзывов.
- Добавлены отступы для якорных переходов под закреплённой навигацией.

## Проверки

`test_all.py`: 10 страниц, 63 внутренних URL, точное множество sitemap, метаданные/JSON-LD, переводы, группа и форма, FAQ, галерея. Успешная отправка проверяется через заглушку: реальных заявок не отправляли.

`test_app.py`: 16 сочетаний старых ссылок, языков и размеров экрана. Сайт остаётся адаптивным, отдельного приложения нет.

`audit.py`: 70 сочетаний страниц и ширин, без переполнения и разрывов слов. После изменения мобильной Instagram-ленты повторно проверены все 20 сочетаний на 320/390 px.

Ограничения: проверено в Chromium, без физических iPhone/Android и Safari. Форма при пустом endpoint остаётся демо-формой. Биографии других гидов и оригинал крупного портрета Павла не доступны в открытой части Instagram: добавлены только проверенные данные.

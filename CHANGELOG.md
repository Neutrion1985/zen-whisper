# Changelog / Журнал изменений

All notable changes to ZenWhisper will be documented in this file.
Все значимые изменения ZenWhisper документируются в этом файле.

---

## [1.1.4] — 2026-03-09

### Added / Добавлено
ENG - **ZenSwitch v2**: Completely redesigned toggle switches with programmatic painting.
РУС - **ZenSwitch v2**: Полная переработка переключателей с использованием программной отрисовки.

ENG - **Neon Glow**: Added a soft neon blue halo effect (glow) when the switch is ON.
РУС - **Неоновый эффект**: Добавлен эффект мягкого синего ореола (glow) при включении.

ENG - **Premium Buttons**: Created `PremiumAddButton` and `PremiumCopyButton` with manual `QPainter` drawing for pixel-perfect icons.
РУС - **Премиальные кнопки**: Созданы классы `PremiumAddButton` и `PremiumCopyButton` с ручной отрисовкой через `QPainter` для идеально четких иконок.

ENG - **Visual Feedback**: Guaranteed high-contrast "ON" state with vibrant blue background for better visibility.
РУС - **Визуальный статус**: Гарантированно яркий синий фон в режиме «Включено» для максимальной наглядности.

### Changed / Изменено
ENG - **History Table**: Increased default row height to 60px for better readability.
РУС - **Таблица истории**: Увеличена высота строк по умолчанию до 60px для комфортного чтения.

ENG - **DEB Packaging**: Updated naming convention to include version number in the filename (`zenwhisper_vX.X.X_amd64.deb`).
РУС - **Сборка DEB**: Обновлены правила именования; теперь версия официально включается в название файла.

---

## [1.1.3] — 2026-03-09

### Added / Добавлено
ENG - **ZenSwitch**: Implemented modern animated toggle switches instead of standard checkboxes.
РУС - **ZenSwitch**: Внедрены современные анимированные переключатели вместо стандартных чекбоксов.

ENG - **Sidebar Updates**: Added application version display and a "Support Project" button.
РУС - **Обновление Сайдбара**: Добавлен вывод версии приложения и кнопка «Поддержать проект».

### Fixed / Исправлено
ENG - **Stability**: Fixed critical startup crash related to incorrect QSS stylesheet references.
РУС - **Стабильность**: Устранена критическая ошибка запуска, связанная с некорректными ссылками на стили.

ENG - **Localization**: Translated missing table headers in AI Model Settings.
РУС - **Локализация**: Переведены отсутствующие заголовки столбцов в настройках моделей ИИ.

---

## [1.1.1] — 2026-03-08

### Fixed / Исправлено
ENG - **Recorder**: Implemented smart microphone fallback. Automatically switches to system default if saved ID is invalid.
РУС - **Recorder**: Реализован «умный» переход на микрофон по умолчанию, если сохраненный ID стал невалидным.

ENG - **Controller**: Added error handling for recording session initialization with tray notifications.
РУС - **Controller**: Добавлена обработка ошибок при старте записи с выводом уведомлений в трее.

---

## [1.1.0] — 2026-03-08

### Added / Добавлено
ENG - **Waveform**: Full geometric morphing between mic input and processing sine wave.
РУС - **Waveform**: Полный геометрический морфинг между входом микрофона и синусоидой обработки.

### Changed / Изменено
ENG - **Versioning**: Re-indexed SemVer history (2.1.0 -> 1.1.0) for logical consistency.
РУС - **Версионирование**: Реиндексация истории SemVer (2.1.0 -> 1.1.0) для сохранения логики.

---

## [1.0.x] — 2026-03-08

### Improved / Улучшено
ENG - **Waveform Engine**: Cinematic transitions, pulsing amplitude, and graceful fade-out effects.
РУС - **Движок Waveform**: Кинематографические переходы, пульсация амплитуды и эффекты плавного затухания.

ENG - **UI Performance**: Removed `QProxyStyle` to eliminate lags; implemented manual chevron drawing for ComboBoxes.
РУС - **Производительность**: Удален `QProxyStyle` для устранения задержек; реализована ручная отрисовка элементов интерфейса.

---

## [1.0.0] — 2026-03-07

### Added / Добавлено
ENG - **Zen Analyst**: New module for offline video and audio transcription via Drag-and-Drop.
РУС - **Zen Analyst**: Новый модуль для оффлайн транскрибации видео и аудио через Drag-and-Drop.

ENG - **Premium Design**: Global Glassmorphism overhaul with Slate-950 and Slate-900 color palette.
РУС - **Премиальный дизайн**: Глобальный редизайн в стиле Glassmorphism (Slate-950, Slate-900).

---

## [0.9.x] — 2026-03-01

### Added / Добавлено
ENG - **Initial Release**: Basic dictation engine, tray-based control, and GitHub launch.
РУС - **Первый релиз**: Базовый движок диктовки, управление через трей и запуск на GitHub.

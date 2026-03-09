# Changelog

All notable changes to ZenWhisper will be documented in this file.

---

## [1.1.4] — 2026-03-09
### Added
- **ZenSwitch v2**: Completely redesigned toggle switches with programmatic painting.
- **Neon Glow**: Added a soft neon blue halo effect when the switch is ON.
- **Premium Buttons**: Created `PremiumAddButton` and `PremiumCopyButton` with manual `QPainter` drawing for pixel-perfect icons.
- **UI States**: Guaranteed high-contrast "ON" state with vibrant blue background.

## [1.1.3] — 2026-03-09
### Added
- **ZenSwitch**: Implemented modern animated toggle switches (instead of checkboxes) for System settings.
- **Sidebar**: Added application version label and a "Support Project" button.
- **UI**: New high-visibility "+" icons for Vocabulary and Snippets.
### Fixed
- **UI State**: Guaranteed visibility of "ON" state for toggle switches with neon blue background.
- **Stability**: Fixed startup crash caused by incorrect QSS stylesheet references.
- **History**: Improved "Copy" button sizing for better accessibility (full-width in cell).
- **Localization**: Translated table headers in AI Model Settings.

## [1.1.1] — 2026-03-08
### Fixed
- **Recorder**: Implemented smart microphone fallback. If the saved microphone ID is invalid (common after reboot), it automatically switches to the system default.
- **Controller**: Added error handling for recording starup with tray notifications.

## [1.1.0] — 2026-03-08
### Added
- **Waveform**: Full geometric morphing (shape blending) between mic input and processing sine wave.
- **UI States**: Versioning lock in skill `my-skill-zenwhisper-ui-states`.

### Changed
- **Versioning**: SemVer re-indexing (2.1.0 -> 1.1.0) to maintain logical history.

---

## [1.0.5] — 2026-03-08
### Improved
- **Waveform**: Cinematic transition speed lowered to 0.015 for extra smooth state switching.

---

## [1.0.4] — 2026-03-08
### Added
- **Waveform**: Initial morphing logic (color and amplitude blending) between recording and processing.

---

## [1.0.3] — 2026-03-08
### Added
- **Waveform**: Pulsing amplitude during processing (Deep Yellow Neon).
- **Waveform**: Graceful fade-out (opacity decay) after transcription finished.

---

## [1.0.2] — 2026-03-08
### Changed
- **Performance**: Removed `QProxyStyle` to eliminate UI lags.
- **UI**: Implemented manual `paintEvent` chevron drawing for QComboBox.

---

## [1.0.1] — 2026-03-08
### Added
- **UI**: Custom dropdown arrows (chevrons) for all ComboBoxes.
- **UI**: AI Model status table (Downloaded / In Cloud) in Settings.

---

## [1.0.0] — 2026-03-07
### Added
- **Zen Analyst**: New module for offline video/audio transcription via Drag-and-Drop.
- **Premium UI**: Total Glassmorphism overhaul (Slate-950, Slate-900).
- **Styling**: Centralized design system in `styles.py`.

---

## [0.9.x] — 2026-03-01
### Added
- Initial public release on GitHub.
- Basic dictation engine and tray-based control.

---

# Журнал изменений

Все значимые изменения ZenWhisper документируются в этом файле.

---

## [1.1.4] — 2026-03-09
### Добавлено
- **ZenSwitch v2**: Полная переработка переключателей с использованием программной отрисовки.
- **Неоновый эффект**: Добавлен эффект мягкого синего ореола (glow) при включении.
- **Премиальные кнопки**: Созданы классы `PremiumAddButton` и `PremiumCopyButton` с ручной отрисовкой через `QPainter` для идеально четких иконок.
- **Визуальный статус**: Гарантированно яркий синий фон в режиме «Включено» для максимальной наглядности.

---

## [1.1.3] — 2026-03-09
### Добавлено
- **ZenSwitch**: Внедрены современные анимированные переключатели (вместо чекбоксов) в настройках системы.
- **Sidebar**: Добавлен вывод версии приложения и кнопка «Поддержать проект».
- **UI**: Новые заметные иконки «+» в разделах Словарь и Сниппеты.
### Исправлено
- **Визуальный статус**: Гарантированное отображение синего неонового фона в режиме «Включено» для переключателей.
- **Стабильность**: Устранена критическая ошибка запуска, связанная с некорректными ссылками на стили.
- **История**: Кнопка копирования теперь занимает всю ширину ячейки для удобства нажатия.
- **Локализация**: Переведены заголовки столбцов в настройках мощности ИИ.

## [1.1.1] — 2026-03-08
### Исправлено
- **Recorder**: Реализован «умный» переход на микрофон по умолчанию. Если сохраненный ID микрофона стал невалидным (часто после перезагрузки), приложение автоматически выбирает дефолтное устройство.
- **Controller**: Добавлена обработка ошибок при старте записи с выводом уведомлений в трее.

## [1.1.0] — 2026-03-08
### Добавлено
- **Waveform**: Полный геометрический морфинг (shape blending) между входом микрофона и синусоидой обработки.
- **UI States**: Фиксация правил версионирования в скилле `my-skill-zenwhisper-ui-states`.

### Изменено
- **Версионирование**: Реиндексация SemVer (2.1.0 -> 1.1.0) для сохранения логической истории.

---

## [1.0.5] — 2026-03-08
### Улучшено
- **Waveform**: Кинематографическая скорость переходов снижена до 0.015 для сверхплавного переключения состояний.

---

## [1.0.4] — 2026-03-08
### Добавлено
- **Waveform**: Внедрена первая логика морфинга (смешивание цвета и амплитуды) между записью и обработкой.

---

## [1.0.3] — 2026-03-08
### Добавлено
- **Waveform**: Пульсация амплитуды во время обработки (желтый неон).
- **Waveform**: Плавное исчезновение (fade-out) после завершения транскрибации.

---

## [1.0.2] — 2026-03-08
### Изменено
- **Производительность**: Удален `QProxyStyle` для устранения задержек интерфейса.
- **UI**: Реализована ручная отрисовка шевронов (стрелок) в `paintEvent` для QComboBox.

---

## [1.0.1] — 2026-03-08
### Добавлено
- **UI**: Кастомные стрелки (шевроны) для всех выпадающих списков.
- **UI**: Таблица статуса моделей ИИ (Скачано / В облаке) в настройках.

---

## [1.0.0] — 2026-03-07
### Добавлено
- **Zen Analyst**: Новый модуль для оффлайн транскрибации видео и аудио через Drag-and-Drop.
- **Premium UI**: Глобальный редизайн в стиле Glassmorphism (Slate-950, Slate-900).
- **Стилизация**: Централизованная система дизайна в `styles.py`.

---

## [0.9.x] — 2026-03-01
### Добавлено
- Первый публичный релиз на GitHub.
- Базовый движок диктовки и управление через трей.

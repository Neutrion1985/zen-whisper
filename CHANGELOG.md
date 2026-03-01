# Changelog

All notable changes to ZenWhisper will be documented in this file.

---

## [0.9.2] — 2026-03-01
### Changed
- **Hotkey**: Default hotkey changed from `Alt+Z` to `Ctrl+F12`. Prevents typing unwanted characters into focused applications.

---

## [0.9.1] — 2026-03-01
### Fixed
- **Hotkey**: Special keys (F1–F12, Home, End, etc.) are now properly wrapped in angle brackets for pynput compatibility. Previously, assigning `Ctrl+F9` would silently fail after restart.

---

## [0.9.0] — 2026-03-01
### Added
- **GitHub**: Project published to GitHub with GPL-3.0 license.
- **Sidebar**: Widened to 110px with 80×80 buttons (28px emoji icons) for better visibility.
- **Skill**: Saved QPainter icon generation technique to `my-skill-zenwhisper-ui-states`.

---

## [0.8.9] — 2026-03-01
### Fixed
- **Icons**: Qt QSS does not support `data:` URIs. Replaced with real PNG files generated on disk via QPainter. Checkmarks and ComboBox arrows are now always visible.

---

## [0.8.6] — 2026-03-01
### Added
- **Slider**: Neon gradient fill for the slider track (`sub-page`), square-oval handle.
- **AI Status**: "Model installed" / "Model not installed" labels.
### Changed
- **Checkbox**: Black SVG checkmark on cyan background.
- **ComboBox**: Right padding for dropdown arrow alignment.

---

## [0.8.5] — 2026-03-01
### Fixed
- **Scroll**: Mouse wheel over dropdowns/sliders now scrolls the page, not the widget.
- **Sidebar**: Expanded to 90px with 70×70 buttons. Icons fully visible.
- **Labels**: Removed duplicate parameter names in settings cards.
- **Checkbox**: Added clear SVG checkmark indicator.

---

## [0.8.4] — 2026-03-01
### Added
- **Scrollbar**: Restored QScrollArea with custom neon scrollbar.
- **Premium Cards**: Increased spacing, margins, and glassmorphism effects.

---

## [0.8.3] — 2026-02-28
### Added
- **Zen Hub**: Premium settings window with Glassmorphism design.
- **NoWheel Widgets**: ComboBox and Slider ignore mouse wheel events.
- **Smart Scroll**: Page scrolling restored with custom scrollbar.

---

## [0.7.x] — 2026-02-28
### Added
- Core voice dictation functionality.
- Tray icon with recording/processing states.
- Waveform overlay widget.
- History, Vocabulary, and Snippets pages.
- Multi-model support (tiny → large-v3).
- Sound feedback (start/stop).
- Russian/English translations.

---

---

# Журнал изменений

Все значимые изменения ZenWhisper документируются в этом файле.

---

## [0.9.2] — 2026-03-01
### Изменено
- **Горячие клавиши**: Горячая клавиша по умолчанию изменена с `Alt+Z` на `Ctrl+F12`. Теперь не печатаются нежелательные символы.

---

## [0.9.1] — 2026-03-01
### Исправлено
- **Горячие клавиши**: Специальные клавиши (F1–F12, Home, End и др.) теперь корректно оборачиваются в угловые скобки для совместимости с pynput. Ранее назначение `Ctrl+F9` молча не работало после перезапуска.

---

## [0.9.0] — 2026-03-01
### Добавлено
- **GitHub**: Проект опубликован на GitHub с лицензией GPL-3.0.
- **Сайдбар**: Расширен до 110px, кнопки 80×80 (эмодзи 28px) для лучшей видимости иконок.
- **Скилл**: Сохранена техника генерации иконок через QPainter.

---

## [0.8.9] — 2026-03-01
### Исправлено
- **Иконки**: Qt QSS не поддерживает `data:` URI. Заменено на реальные PNG-файлы, генерируемые через QPainter. Галочки и стрелки комбобоксов теперь всегда видны.

---

## [0.8.6] — 2026-03-01
### Добавлено
- **Слайдер**: Неоновая градиентная заливка пути, квадратно-овальный ползунок.
- **Статус ИИ**: Метки "Модель установлена" / "Модель не установлена".
### Изменено
- **Чекбокс**: Чёрная галочка на циановом фоне.
- **Комбобокс**: Правый отступ для стрелки выбора.

---

## [0.8.5] — 2026-03-01
### Исправлено
- **Скролл**: Колесо мыши над виджетами теперь прокручивает страницу, а не меняет значения.
- **Сайдбар**: Расширен до 90px, кнопки 70×70. Иконки видны полностью.
- **Метки**: Удалены дублирующиеся названия параметров.
- **Чекбокс**: Добавлена чёткая SVG-галочка.

---

## [0.8.4] — 2026-03-01
### Добавлено
- **Скроллбар**: Восстановлен QScrollArea с кастомным неоновым скроллбаром.
- **Премиальные карточки**: Увеличены отступы и эффекты Glassmorphism.

---

## [0.8.3] — 2026-02-28
### Добавлено
- **Zen Hub**: Премиальное окно настроек с дизайном Glassmorphism.
- **NoWheel виджеты**: ComboBox и Slider игнорируют колесо мыши.
- **Умный скролл**: Восстановлена прокрутка страницы с кастомным скроллбаром.

---

## [0.7.x] — 2026-02-28
### Добавлено
- Основная функциональность голосовой диктовки.
- Иконка в трее с состояниями записи/обработки.
- Виджет звуковой волны.
- Страницы истории, словаря и сниппетов.
- Поддержка моделей (tiny → large-v3).
- Звуковые отклики (начало/стоп).
- Переводы на русский/английский.

<h1 align="center">🧘 ZenWhisper</h1>

<p align="center">
  <b>Local AI Voice Dictation for Linux</b><br>
  <i>Privacy • Speed • Premium Design</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.9.2-cyan" alt="Version">
  <img src="https://img.shields.io/badge/license-GPL--3.0-blue" alt="License">
  <img src="https://img.shields.io/badge/platform-Linux-green" alt="Platform">
  <img src="https://img.shields.io/badge/AI-faster--whisper-orange" alt="AI Engine">
</p>

---

## ✨ What is ZenWhisper?

**ZenWhisper** is a premium desktop voice dictation app that runs **100% locally** on your computer. No data is sent to the internet.

### Key Features:
- 🔒 **100% Local** — Speech recognition runs on your PC, no cloud
- 🎙️ **High Accuracy** — Powered by faster-whisper (OpenAI Whisper)
- 🌐 **Multilingual** — 99 languages supported (Russian, English, etc.)
- 🎨 **Premium UI** — Glassmorphism + Live Neon design
- ⌨️ **Hotkey** — Press, dictate, text is inserted (default: `Ctrl + F12`)
- 🔊 **Sound Feedback** — Pleasant start/stop sounds
- 📝 **Snippets** — Quick text substitutions
- 🤖 **AI Models** — From tiny (instant) to large-v3 (max accuracy)

---

## 📦 Installation

### Method 1: Download .deb package (recommended)

> For: **Ubuntu**, **Linux Mint**, **Debian**, **Pop!_OS** and other DEB-based distros.

1. Go to **[Releases](https://github.com/Neutrion1985/zen-whisper/releases)**
2. Download `zenwhisper_amd64.deb`
3. Install:

```bash
sudo dpkg -i zenwhisper_amd64.deb
```

4. If dependency errors appear:
```bash
sudo apt-get install -f
```

5. Launch `ZenWhisper` from the app menu or run:
```bash
zenwhisper
```

---

### Method 2: Build from source

> For advanced users who want to build the app themselves.

#### Requirements:
- **Python** 3.10+
- **PyQt6**
- **FFmpeg**

#### Steps:

```bash
# 1. Clone the repository
git clone https://github.com/Neutrion1985/zen-whisper.git
cd zen-whisper

# 2. Install dependencies
pip install PyQt6 faster-whisper pynput pydub httpx sounddevice numpy

# 3. Run the app
python -m zenwhisper
```

#### Build .deb from source:
```bash
bash packaging/make_deb.sh
sudo dpkg -i dist/zenwhisper_amd64.deb
```

---

## 🚀 Quick Start

1. **Launch** ZenWhisper from the app menu
2. **Set your hotkey** (default: `Ctrl + F12`)
3. **Press the hotkey** — recording starts
4. **Speak** — text will be recognized and inserted into the active window
5. **Press again** — recording stops

---

## 🎙️ AI Models

| Model | Size | Speed | Accuracy | Best for |
|---|---|---|---|---|
| `tiny` | ~75 MB | ⚡ Instant | ★★☆☆☆ | Quick notes |
| `base` | ~150 MB | ⚡ Fast | ★★★☆☆ | Everyday use |
| `small` | ~500 MB | 🔄 Medium | ★★★★☆ | Good balance |
| `medium` | ~1.5 GB | 🐢 Slower | ★★★★★ | High accuracy |
| `large-v3` | ~3 GB | 🐢 Slow | ★★★★★ | Maximum accuracy |

> Models are downloaded automatically on first selection.

---

## 🖥️ System Requirements

- **OS**: Ubuntu 22.04+, Linux Mint, Debian 12+, Pop!_OS
- **CPU**: x86_64 (AMD64)
- **RAM**: 2 GB min (4 GB for large-v3)
- **Microphone**: Any USB or built-in
- **Python**: 3.10+ (installed automatically)

---

## 🔒 Privacy

ZenWhisper runs **completely locally**:
- ❌ No cloud services
- ❌ No API keys
- ❌ No telemetry
- ✅ Your voice stays on your computer

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **UI** | PyQt6 (Glassmorphism + Live Neon) |
| **AI** | faster-whisper (CTranslate2) |
| **Audio** | sounddevice, pydub |
| **Hotkeys** | pynput |
| **Packaging** | dpkg-deb |

---

## 💖 Support the Project

If ZenWhisper is useful to you, consider supporting development:

[![Sponsor](https://img.shields.io/badge/💖_Sponsor-GitHub-ea4aaa)](https://github.com/sponsors/Neutrion1985)

---

## 📄 License

[GPL-3.0](LICENSE) — Free and open source software.

---

---

<h1 align="center">🧘 ZenWhisper</h1>

<p align="center">
  <b>Локальное AI-приложение для голосовой диктовки на Linux</b><br>
  <i>Приватность • Скорость • Премиальный дизайн</i>
</p>

---

## ✨ Что такое ZenWhisper?

**ZenWhisper** — это премиальное десктопное приложение для голосовой диктовки, которое работает **полностью локально** на вашем компьютере. Никакие данные не отправляются в интернет.

### Основные возможности:
- 🔒 **100% Локально** — Распознавание речи работает на вашем ПК, без облака
- 🎙️ **Высокая точность** — Powered by faster-whisper (OpenAI Whisper)
- 🌐 **Мультиязычность** — Поддержка 99 языков (русский, английский и др.)
- 🎨 **Премиальный UI** — Glassmorphism + Live Neon дизайн
- ⌨️ **Горячие клавиши** — Нажал, надиктовал, текст вставлен (по умолчанию: `Ctrl + F12`)
- 🔊 **Звуковые отклики** — Приятные звуки начала и окончания записи
- 📝 **Сниппеты** — Быстрые текстовые подстановки
- 🤖 **Выбор AI-моделей** — От tiny (мгновенно) до large-v3 (максимальная точность)

---

## 📦 Установка

### Способ 1: Скачать готовый .deb пакет (рекомендуется)

> Подходит для: **Ubuntu**, **Linux Mint**, **Debian**, **Pop!_OS** и другие DEB-дистрибутивы.

1. Перейдите на страницу **[Releases](https://github.com/Neutrion1985/zen-whisper/releases)**
2. Скачайте файл `zenwhisper_amd64.deb`
3. Установите:

```bash
sudo dpkg -i zenwhisper_amd64.deb
```

4. Если появятся ошибки зависимостей:
```bash
sudo apt-get install -f
```

5. Запустите `ZenWhisper` из меню приложений или введите:
```bash
zenwhisper
```

---

### Способ 2: Собрать из исходников

> Для продвинутых пользователей.

#### Требования:
- **Python** 3.10+
- **PyQt6**
- **FFmpeg**

#### Шаги:

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/Neutrion1985/zen-whisper.git
cd zen-whisper

# 2. Установите зависимости
pip install PyQt6 faster-whisper pynput pydub httpx sounddevice numpy

# 3. Запустите приложение
python -m zenwhisper
```

#### Сборка .deb из исходников:
```bash
bash packaging/make_deb.sh
sudo dpkg -i dist/zenwhisper_amd64.deb
```

---

## 🚀 Быстрый старт

1. **Запустите** ZenWhisper из меню приложений
2. **Настройте горячую клавишу** (по умолчанию: `Ctrl + F12`)
3. **Нажмите горячую клавишу** — начнётся запись
4. **Говорите** — текст будет распознан и вставлен в активное окно
5. **Нажмите ещё раз** — запись остановится

---

## 🎙️ Поддерживаемые AI-модели

| Модель | Размер | Скорость | Точность | Рекомендация |
|---|---|---|---|---|
| `tiny` | ~75 МБ | ⚡ Мгновенно | ★★☆☆☆ | Быстрые заметки |
| `base` | ~150 МБ | ⚡ Быстро | ★★★☆☆ | Повседневное использование |
| `small` | ~500 МБ | 🔄 Средне | ★★★★☆ | Хороший баланс |
| `medium` | ~1.5 ГБ | 🐢 Медленнее | ★★★★★ | Высокая точность |
| `large-v3` | ~3 ГБ | 🐢 Медленно | ★★★★★ | Максимальная точность |

> Модели скачиваются автоматически при первом выборе.

---

## 🖥️ Системные требования

- **ОС**: Ubuntu 22.04+, Linux Mint, Debian 12+, Pop!_OS
- **Процессор**: x86_64 (AMD64)
- **RAM**: 2 ГБ минимум (4 ГБ для large-v3)
- **Микрофон**: Любой USB или встроенный
- **Python**: 3.10+ (устанавливается автоматически)

---

## 🔒 Приватность

ZenWhisper работает **полностью локально**:
- ❌ Никаких облачных сервисов
- ❌ Никаких API-ключей
- ❌ Никакой телеметрии
- ✅ Ваш голос остаётся на вашем компьютере

---

## 🛠️ Технологии

| Компонент | Технология |
|---|---|
| **UI** | PyQt6 (Glassmorphism + Live Neon) |
| **AI** | faster-whisper (CTranslate2) |
| **Аудио** | sounddevice, pydub |
| **Горячие клавиши** | pynput |
| **Пакетирование** | dpkg-deb |

---

## 💖 Поддержать проект

Если ZenWhisper вам полезен, вы можете поддержать разработку:

[![Sponsor](https://img.shields.io/badge/💖_Sponsor-GitHub-ea4aaa)](https://github.com/sponsors/Neutrion1985)

---

## 📄 Лицензия

[GPL-3.0](LICENSE) — свободное ПО с открытым исходным кодом.

---

<p align="center">
  <b>Made with ❤️ for the Linux community | Сделано с ❤️ для Linux-сообщества</b>
</p>

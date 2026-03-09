#!/bin/bash

# Скрипт для сборки .deb пакета ZenWhisper
APP_NAME="zenwhisper"
VERSION="1.1.4"
ARCH="amd64"
DEB_DIR="dist/${APP_NAME}_${VERSION}_${ARCH}"

echo "Building .deb package for ${APP_NAME} v${VERSION}..."

# 1. Создаем структуру директорий
mkdir -p "${DEB_DIR}/DEBIAN"
mkdir -p "${DEB_DIR}/usr/bin"
mkdir -p "${DEB_DIR}/usr/share/${APP_NAME}"
mkdir -p "${DEB_DIR}/usr/share/applications"
mkdir -p "${DEB_DIR}/usr/share/pixmaps"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/1024x1024/apps"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/512x512/apps"
mkdir -p "${DEB_DIR}/usr/share/icons/hicolor/scalable/apps"

# 2. Создаем файл control
cat <<EOF > "${DEB_DIR}/DEBIAN/control"
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Antigravity <antigravity@example.com>
Depends: python3, python3-pyqt6, libportaudio2, xdotool
Description: Premium private voice dictation for Linux. Zen-style voice-to-text with local models.
EOF

# 3. Копируем исходники и ресурсы
cp -r src/* "${DEB_DIR}/usr/share/${APP_NAME}/"
cp src/${APP_NAME}/assets/icon.png "${DEB_DIR}/usr/share/pixmaps/${APP_NAME}.png"
cp src/${APP_NAME}/assets/icon.png "${DEB_DIR}/usr/share/icons/hicolor/1024x1024/apps/${APP_NAME}.png"
cp src/${APP_NAME}/assets/icon.png "${DEB_DIR}/usr/share/icons/hicolor/512x512/apps/${APP_NAME}.png"
cp src/${APP_NAME}/assets/icon.png "${DEB_DIR}/usr/share/icons/hicolor/scalable/apps/${APP_NAME}.png"

# 4. Копируем .desktop файл
mkdir -p "${DEB_DIR}/usr/share/applications"
cp packaging/zenwhisper.desktop "${DEB_DIR}/usr/share/applications/"

# 4. Добавляем postinst и postrm скрипты
cp packaging/postinst "${DEB_DIR}/DEBIAN/postinst"
chmod 755 "${DEB_DIR}/DEBIAN/postinst"
cp packaging/postrm "${DEB_DIR}/DEBIAN/postrm"
chmod 755 "${DEB_DIR}/DEBIAN/postrm"

# 5. Создаем исполняемый файл в /usr/bin
cat <<EOF > "${DEB_DIR}/usr/bin/${APP_NAME}"
#!/bin/bash
export PYTHONPATH=\$PYTHONPATH:/usr/share/${APP_NAME}
# Ensure UTF-8 locale for PyAV and transcription
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export PYTHONIOENCODING=utf-8
exec /usr/bin/python3 /usr/share/${APP_NAME}/zenwhisper/main.py "\$@"
EOF
chmod 755 "${DEB_DIR}/usr/bin/${APP_NAME}"

# 6. Собираем пакет
# Согласно GEMINI.md: название должно быть НазваниеПроекта_Версия_Архитектура.deb
OUTPUT_FILE="dist/${APP_NAME}_${VERSION}_${ARCH}.deb"
dpkg-deb --build "${DEB_DIR}" "${OUTPUT_FILE}"

echo "Done! Package created at ${OUTPUT_FILE}"
rm -rf "${DEB_DIR}" # Clean up build dir

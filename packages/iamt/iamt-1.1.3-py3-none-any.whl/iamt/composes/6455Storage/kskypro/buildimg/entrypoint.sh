#!/bin/bash
set -eu

WEB_PORT=${WEB_PORT:-8089}
HTTPS_PORT=${HTTPS_PORT:-8088}
INSTALL=${INSTALL:-true}  # 添加 INSTALL 变量，默认为 true

envsubst '${WEB_PORT} ${HTTPS_PORT}' < /etc/apache2/sites-enabled/000-default.conf.template > /etc/apache2/sites-enabled/000-default.conf
envsubst '${WEB_PORT} ${HTTPS_PORT}' < /etc/apache2/ports.conf.template > /etc/apache2/ports.conf

if [ ! -e '/var/www/html/public/index.php' ]; then
    cp -a /var/www/lsky/* /var/www/html/
    cp -a /var/www/lsky/.env.example /var/www/html
fi
    chown -R www-data /var/www/html
    chgrp -R www-data /var/www/html
    chmod -R 755 /var/www/html/

# 添加的新功能：根据 INSTALL 变量决定是否创建 installed.lock 文件
if [ "${INSTALL,,}" = "false" ]; then
    # 如果 INSTALL 为 false，创建 installed.lock 文件
    touch /var/www/html/installed.lock
    # 确保文件权限与其他文件一致
    chown www-data:www-data /var/www/html/installed.lock
    chmod 755 /var/www/html/installed.lock
    echo "Created installed.lock file to skip installation"
fi

exec "$@"

FROM php:8.1 AS build
WORKDIR /build

# 安装必要的依赖
# RUN sed -i 's|http://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
    apt-get install -y curl unzip git && \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# RUN curl -OL https://github.com/lsky-org/lsky-pro/archive/refs/heads/master.zip \
#     && unzip *.zip \
#     && mv ./lsky-pro-master/* ./ \
#     && mv ./lsky-pro-master/.env.example ./ \
#     && rm -rf master.zip lsky-pro-master


RUN git clone https://KingSung509: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@github.com/KingSung509/lsky_pro_master.git \ 
    && mv ./lsky_pro_master/* ./ \
    && mv ./lsky_pro_master/.env.example ./ \
    && rm -rf master.zip lsky_pro_master

# COPY ./src /build/

    
RUN php -r "file_exists('.env') || copy('.env.example', '.env');" && composer install   

# 更换了阿里云的 composer 源结果会出现超时的情况 

FROM php:8.1-apache

# 如果构建速度慢可以换源
# RUN sed -i 's|http://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g' /etc/apt/sources.list.d/debian.sources
# 安装相关拓展
ADD https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions /usr/local/bin/

# 开启SSL
RUN a2enmod ssl && a2ensite default-ssl

RUN touch /etc/apt/sources.list.d/debian-testing.sources && \ 
    echo 'Types: deb' > /etc/apt/sources.list.d/debian-testing.sources && \
    echo 'URIs: http://deb.debian.org/debian' >> /etc/apt/sources.list.d/debian-testing.sources && \
    echo 'Suites: testing' >> /etc/apt/sources.list.d/debian-testing.sources && \
    echo 'Components: main contrib non-free non-free-firmware' >> /etc/apt/sources.list.d/debian-testing.sources && \
    echo 'Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg' >> /etc/apt/sources.list.d/debian-testing.sources \
    && apt update \
    && apt install -y -t testing imagemagick libmagickwand-dev \
    && echo "/usr/" | pecl install imagick \
    && echo "extension=imagick.so" > /usr/local/etc/php/conf.d/imagick.ini \
    && apt clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/* 

RUN apt-get update && \
    apt-get install -y gettext && \
    apt-get clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*  && \
    a2enmod rewrite && chmod +x /usr/local/bin/install-php-extensions && \
    install-php-extensions bcmath pdo_mysql pdo_pgsql redis && \
    \
    { \
    echo 'post_max_size = 12G;';\
    echo 'upload_max_filesize = 10G;';\
    echo 'max_execution_time = 1800S;';\
    } > /usr/local/etc/php/conf.d/docker-php-upload.ini; \
    \
    { \
    echo 'opcache.enable=1'; \
    echo 'opcache.interned_strings_buffer=8'; \
    echo 'opcache.max_accelerated_files=10000'; \
    echo 'opcache.memory_consumption=128'; \
    echo 'opcache.save_comments=1'; \
    echo 'opcache.revalidate_freq=1'; \
    } > /usr/local/etc/php/conf.d/opcache-recommended.ini; \
    \
    echo 'apc.enable_cli=1' >> /usr/local/etc/php/conf.d/docker-php-ext-apcu.ini; \
    \
    echo 'memory_limit=4G' > /usr/local/etc/php/conf.d/memory-limit.ini; \
    \
    mkdir /var/www/data; \
    chown -R www-data:root /var/www; \
    chmod -R g=u /var/www

# 内存限制 需要大于 单个文件的大小 要不然无法上传大的文件  

COPY ./ssl /etc/ssl

COPY --from=build /build /var/www/lsky/
COPY ./000-default.conf.template /etc/apache2/sites-enabled/
COPY ./ports.conf.template /etc/apache2/
COPY entrypoint.sh /
WORKDIR /var/www/html/
# VOLUME /var/www/html
ENV WEB_PORT=8089
ENV HTTPS_PORT=8088
EXPOSE ${WEB_PORT}
EXPOSE ${HTTPS_PORT}
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["apachectl","-D","FOREGROUND"]

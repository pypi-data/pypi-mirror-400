

FROM php:8.1 AS build
WORKDIR /build

# 安装必要的依赖
RUN apt-get update &&  apt-get install -y curl unzip &&  curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*



    

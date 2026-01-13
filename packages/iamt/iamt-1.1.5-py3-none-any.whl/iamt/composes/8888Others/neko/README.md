https://github.com/m1k1o/neko/tree/master


尝试在韩国服务器上部署 能部署成功但是登录后一直连接  
本地部署多次不成功 最后在韩国的debian服务器上面部署成功了 
https://neko.m1k1o.net/#/getting-started/troubleshooting
查看了 文档  
加了几个字段  NEKO_NET1TO1: 47.80.1.60  指定自己的公网IP地址, 这个地址只能是公网IP地址 我测试了本地地址没用
而且 云服务器 要开放端口组 8080 和  52000-52100/UDP 才能用 

这东西真挺有意思 完全不需要安装桌面啥的 就能用浏览器  
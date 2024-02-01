## Centos中Nginx平滑升级

* 原版本：1.17.1
* 升级后：1.20.1
* 下载地址：<http://nginx.org/en/download.html>

#### 1. 下载新版本（或是提前下好后上传到服务器）
```shell
wget http://nginx.org/download/nginx-1.20.1.tar.gz
```

#### 2. 解压新版nginx
```shell
tar xf nginx-1.20.1.tar.gz
```

#### 3.查看原nginx编译参数
```shell
/usr/local/nginx/sbin/nginx -V
```

如下：
```shell
# configure arguments:编译参数需要配置在新版的nginx中

[root@node01 soft]# /usr/local/nginx/sbin/nginx -V
nginx version: nginx/1.17.1
built by gcc 4.8.5 20150623 (Red Hat 4.8.5-44) (GCC)
built with OpenSSL 1.0.2k-fips  26 Jan 2017
TLS SNI support enabled
configure arguments: --add-module=/home/soft/nginx-1.17.1/nginx-rtmp-module-master
```

#### 4. 编译安装新版nginx
```shell
cd nginx-1.20.1/
```

**此时不要执行 make install，要不然就会覆盖原来的版本产生诸多问题**
```shell
# XXXXXXXX 为第3步中原nginx的编译参数

./configure  XXXXXXXX   && make
```

#### 5. 复制启动文件
**最好对原版nginx启动文件做好备份**
```shell
mv /usr/local/nginx/sbin/nginx /usr/local/nginx/sbin/nginx-1.17.1-bak 
```

```shell
cp objs/nginx /usr/local/nginx/sbin/
```

#### 6. 平滑升级
```shell
make upgrade
```

```shell
# 测试-可省略
/usr/local/nginx/sbin/nginx -t

# 重启-可省略
/usr/local/nginx/sbin/nginx -s reload
```

#### 7. 查看版本
```shell
/usr/local/nginx/sbin/nginx -V
```
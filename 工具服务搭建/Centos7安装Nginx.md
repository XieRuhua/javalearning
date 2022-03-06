# Centos7安装Nginx

[toc]

## 一、安装前环境准备
准备工作：开始前，请确认`gcc g++`开发类库是否装好

安装`make`：
```shell
yum -y install gcc automake autoconf libtool make
```

安装`g++`:
```shell
yum install gcc gcc-c++
```

### 1、选定安装文件目录
可以选择任何目录，演示选择  `/usr/local/src`
```shell
cd /usr/local/src
```

### 2、安装PCRE库
下载最新的 `PCRE` 源码包，使用下面命令下载编译和安装 `PCRE` 包：本文选择`pcre-8.39.tar.gz`
```sh
cd /usr/local/src
wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.39.tar.gz 
tar -zxvf pcre-8.37.tar.gz
cd pcre-8.34
./configure
make
make install
```

### 3、安装zlib库
下载最新的 `zlib` 源码包，使用下面命令下载编译和安装 `zlib` 包：（本文参照下载文件版本：本文选择`zlib-1.2.11.tar.gz` )
```shell
cd /usr/local/src

wget http://zlib.net/zlib-1.2.11.tar.gz
tar -zxvf zlib-1.2.11.tar.gz
cd zlib-1.2.11
./configure
make
make install
```

### 4、安装`openssl`（某些`vps`默认没装`ssl`)
```she
cd /usr/local/src
wget https://www.openssl.org/source/openssl-1.0.1t.tar.gz
tar -zxvf openssl-1.0.1t.tar.gz
```

### 5、安装nginx
`Nginx` 一般有两个版本，分别是稳定版和开发版，可以根据目的来选择这两个版本的其中一个，下面是把 `Nginx` 安装到 `/usr/local/nginx` 目录下的详细步骤：
```shell
cd /usr/local/src

wget http://nginx.org/download/nginx-1.1.10.tar.gz
tar -zxvf nginx-1.1.10.tar.gz
cd nginx-1.1.10
./configure
make
make install
```

注：这里可能会出现报错

执行以下语句
```shell
yum -y install openssl openssl-devel
```

## 二、nginx的启动、停止和重启
### 1、启动前的配置
因为`Apeache`占用`80`端口，`Apeache`尽量不要修改，演示服务器没安装`Apeache`，所以使用默认的端口`80`。

如需修改：
- `linux` 下修改路径`/usr/local/nginx/conf/nginx.conf`；
- `Windows` 下修改路径`{nginx安装路径}\conf\nginx.conf`。

默认端口为`80`，`localhost`修改为你服务器`ip`地址
                
### 2、nginx启动
- 方式一：nginx安装目录地址` -c nginx`配置文件地址
    ```shell
    [root@localhost sbin]# /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
    ```
- 方式二：进入nginx的安装目录，进入`/sbin`并执行`./nginx`命令即可
    ```shell
    [root@localhost /]# cd usr/local/nginx/sbin
    [root@localhost sbin]#./nginx
    ````
    使用命令`netstat -ntpl`查看是否启动成功
    ```shell
    [root@localhost conf]# netstat -ntpl
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name               
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      18312/nginx: master 
    ````
    即为启动成功。

### 3、nginx停止
nginx的停止有三种方式：
1. 通过命令停止
    ```shell
    [root@localhost ~]# nginx -s reload
    ````
2. 通过杀死进程
    - 查看进程号
    ```shell
    [root@localhost ~]# ps -ef|grep nginx
    ````
    - 执行`kill`命令
        - a.从容停止
        ```shell
        [root@localhost ~]# kill -QUIT 2072
        ````
        - b.快速停止
        ```shell
        [root@localhost ~]# kill -TERM 2132
        [root@localhost ~]# kill -INT 2132
        ````
        - c. 强制停止
        ```shell
        [root@localhost ~]# pkill -9 nginx
        ````

### 4、nginx重启
#### 1、验证nginx配置文件是否正确
- 方法一：进入nginx安装目录`sbin`下，输入命令`./nginx -t`或在服务器任意地方输入`nginx -t`
    ```shell    
    [root@localhost sbin/]# ./nginx -t
    [root@localhost /]# mginx -t
    nginx.conf syntax is ok
    nginx.conf test is successful
    ````
    说明配置文件正确！
- 方法二：在启动命令`-c`前加`-t`

#### 2、重启nginx服务
- 方法一：进入nginx可执行目录`sbin`下，输入命令`./nginx -s reload` 即可或者在服务器任意地方输入`nginx -s reload`
    ```shell
    [root@localhost sbin/]# ./nginx -s reload
    [root@localhost /]# mginx -s reload
    ````
- 方法二：查找当前`nginx`进程号，然后输入命令：`kill -HUP 进程号` 实现重启`nginx`服务
    ```shell
    [root@localhost /]# netstat -ntpl
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name        
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      4245/nginx: worker
    [root@localhost /]# kill -HUP 4245
    [root@localhost /]# 
    ````

## 三、测试
因为设置的端口是默认的`80`端口，所以直接输入服务器`ip`即可访问 `Http://ip:80`

 　
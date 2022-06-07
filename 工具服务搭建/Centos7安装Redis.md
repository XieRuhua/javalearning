# Centos7安装Redis

## 1. 安装前准备，安装gcc（因为redis是用C语言开发的，安装前要先安装gcc环境）
```shell
yum install -y gcc 
```

## 2. 下载redis安装包
```shell
# 安装地址（版本自行选择）
cd /usr/local/
wget http://download.redis.io/releases/redis-5.0.3.tar.gz
```

## 3. 解压
```shell
tar -zxvf redis-5.0.3.tar.gz
```

`cd`切换到`redis`解压目录下，执行编译
```shell
cd redis-5.0.3
make
```

`make`可能会出现如下错误
```shell
cd src && make all
make[1]: 进入目录“/home/soft/redis/redis-5.0.12/src”
    CC adlist.o
In file included from adlist.c:34:0:
zmalloc.h:50:31: 致命错误：jemalloc/jemalloc.h：没有那个文件或目录
 #include <jemalloc/jemalloc.h>
                               ^
编译中断。
make[1]: *** [adlist.o] 错误 1
make[1]: 离开目录“/home/soft/redis/redis-5.0.12/src”
make: *** [all] 错误 2
```

执行：
```shell
make MALLOC=libc
make install PREFIX=/usr/local/redis
```

## 4. 启动服务
```shell
cd /usr/local/redis/bin/
./redis-server
```

## 5. 后台启动
从 redis 的源码目录中复制 `redis.conf` 到 `redis` 的安装目录
```shell
cp /usr/local/redis-5.0.3/redis.conf /usr/local/redis/bin/
```

修改 `redis.conf` 文件，把 `daemonize no` 改为 `daemonize yes`  
`Redis daemonize`介绍：
`redis.conf`配置文件中`daemonize`表示 **守护线程启动** ，默认是`NO`。用来指定`redis`是否要用 **守护线程** 的方式启动（即后台启动）。

**2、daemonize 设置yes或者no区别**
- `daemonize yes`：redis采用的是单进程多线程的模式。当redis.conf中选项daemonize设置成yes时，代表开启守护进程模式。在该模式下，redis会在后台运行，并将进程pid号写入至redis.conf选项pidfile设置的文件中，此时redis将一直运行，除非手动kill该进程。
- `daemonize:no`: 当daemonize选项设置成no时，当前界面将进入redis的命令行界面，exit强制退出或者关闭连接工具(putty,xshell等)都会导致redis进程退出。

启动
```shell
cd /usr/local/redis/bin
 ./redis-server redis.conf
```

重启
```shell
cd /usr/local/redis/bin

./redis-cli shutdown
./redis-server redis.conf
```

## 6. 设置远程访问和密码
远程访问的设置和密码设置均在配置文件`redis.conf`中。

**远程访问：**
```shell
cd /usr/local/redis/bin
vim redis.conf
````
找到`bind`属性，该属性默认是`127.0.0.1`，意思是只能本机(服务器)访问，要远程连接则需要把该属性注释掉，也可以改成物理机的ip也就只有自己能访问，注释掉的意思就是所有人都可以访问

**密码设置**  
继续往下找到`requirepass`属性，该属性是设置`redis`的密码，默认是没有密码即一串空的字符串，需要设置密码  
同时把`protected-mode yes`改为`protected-mode no`（该设置表示在没有密码的情况下，关闭保护模式）

配置完成后保存退出，重启`redis`
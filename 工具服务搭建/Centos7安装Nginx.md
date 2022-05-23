# Centos7安装Nginx

[toc]

## 一、安装前环境准备
### 1. 下载
+ 切换路径
  ```shell
  cd /usr/local/
  ```
+ 下载
  ```shell
  wget http://nginx.org/download/nginx-1.18.0.tar.gz
  ```

### 2. 安装依赖
```shell
yum -y install gcc zlib zlib-devel pcre-devel openssl openssl-devel gd-devel
```

可能需要安装make
```shell
yum -y install gcc automake autoconf libtool make
```

### 3. 编译安装
+ 解压文件
  ```shell
  tar -zxvf nginx-1.18.0.tar.gz
  ```
+ 配置模块
  + 切换目录
    ```shell
    # 更名
    mv nginx-1.18.0 nginx
    cd nginx-1.18.0
    ```

  + 配置
    ```shell
    ./configure --with-http_gzip_static_module --with-http_image_filter_module --with-http_ssl_module --with-http_v2_module
    ```

+ 编译安装
```shell
make && make install
```

### 4. 添加环境变量
```shell
vim /etc/profile

# 末尾添加nginx配置
PATH=$PATH:/usr/local/nginx/sbin
export PATH

# 刷新配置文件
source /etc/profile
```

### 5. 注意事项
+ `nginx`需要添加新模块时，下载相同版本，执行解压，`configurat`时添加新的模块，然后`make`，不执行`install`，然后重启`nginx`
+ `make`出现错误时，执行`make clean`，然后添加依赖后再`make`

## 二、nginx的启动、停止和重启
### 1. 启动前的配置
因为`Apeache`占用`80`端口，`Apeache`尽量不要修改，演示服务器没安装`Apeache`，所以使用默认的端口`80`。

如需修改：
- `linux` 下修改路径`/usr/local/nginx/conf/nginx.conf`；
- `Windows` 下修改路径`nginx安装路径\conf\nginx.conf`。

默认端口为`80`，`localhost`修改为你服务器`ip`地址
                
### 2. nginx启动
- 方式一：`nginx`安装目录地址` -c nginx`配置文件地址
    ```shell
    /usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
    ```
    可能提示：
    ```shell
    nginx: [alert] could not open error log file: open() "/usr/local/nginx/logs/error.log" failed (2: No such file or directory)  
    2022/05/20 11:49:18 [emerg] 22626#0: open() "/usr/local/nginx/logs/access.log" failed (2: No such file or directory)
    ```

    **原因是缺少日志文件。** 需要在`nginx`安装目录的`logs`下创建文件`error.log`和`access.log`
    ```shell
    cd /usr/local/nginx
    mkdir logs
    cd logs
    touch access.log error.log
    ```
    重新执行启动即可。
- 方式二：进入`nginx`的安装目录，进入`/sbin`并执行`./nginx`命令即可
    ```shell
    cd usr/local/nginx/sbin
    ./nginx
    ````
    使用命令`netstat -ntpl`查看是否启动成功
    ```shell
    netstat -ntpl
    
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name               
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      18312/nginx: master 
    ````
    即为启动成功。

### 3. nginx停止
`nginx`的停止有四种方式：
1. 从容停止服务：这种方法较`stop`相比就比较温和一些了，需要进程完成当前工作后再停止
    ```shell
    nginx -s quit
    ````
2. 立即停止服务：这种方法比较强硬，无论进程是否在工作，都直接停止进程
    ```shell
    nginx -s stop
    ````
3. `systemctl` 停止：`systemctl`属于`Linux`命令
    ```shell
    systemctl stop nginx.service
    ```
4. 杀掉进程：直接杀死进程，在上面无效的情况下使用，态度强硬，简单粗暴！
    ```shell
    ps -ef|grep nginx
    kill -9 进程号
    ````
    或者直接干掉所有的`nginx`进程：
    ```shell
    killall nginx
    # 或者下面的方式
    pkill -9 nginx
    ```

### 4. nginx重启
#### 4.1 验证nginx配置文件是否正确
- 方法一：进入`nginx`安装目录`sbin`下，输入命令`./nginx -t`或在服务器任意地方输入`nginx -t`
    ```shell    
    # 安装目录sbin中
    ./nginx -t
    # 或者
    mginx -t
    nginx.conf syntax is ok
    nginx.conf test is successful
    ````
    说明配置文件正确！
- 方法二：在启动命令`-c`前加`-t`

#### 4.2 重启nginx服务
- 方法一：进入`nginx`可执行目录`sbin`下，输入命令`./nginx -s reload` 即可或者在服务器任意地方输入`nginx -s reload`
    ```shell
    # 安装目录sbin中
    ./nginx -s reload
    # 或者
    nginx -s reload
    ````
- 方法二：查找当前`nginx`进程号，然后输入命令：`kill -HUP 进程号` 实现重启`nginx`服务
    ```shell
    netstat -ntpl
    kill -HUP 4245
    ````

## 三、测试
因为设置的端口是默认的`80`端口，所以直接输入服务器`ip`即可访问 `Http://ip:80`

 　
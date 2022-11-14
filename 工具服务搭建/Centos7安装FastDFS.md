# Centos7安装FastDFS

[FastDFS官方地址](https://github.com/happyfish100/fastdfs/wiki1)

[toc]

## 一、FastDFS介绍
**`FastDFS`是一个开源的轻量级分布式文件系统，它对文件进行管理，功能包括：文件存储、文件同步、文件访问（文件上传、文件下载）等，解决了大容量存储和负载均衡的问题。特别适合以文件为载体的在线服务，如相册网站、视频网站等等。**

`FastDFS`为互联网量身定制，充分考虑了 **冗余备份** 、 **负载均衡** 、 **线性扩容等机制** ，并注重 **高可用** 、 **高性能** 等指标，使用`FastDFS`很容易搭建一套高性能的文件服务器集群提供文件上传、下载等服务。

**<font color="red">注意：`docker`安装直接看最后</font>**

## 二、安装前的准备工作
```shell
#安装git
yum install git 
```

### 1. 相关介绍及安装
| centos               | 7.x                           |
| :------------------- | :---------------------------- |
| libfatscommon        | FastDFS分离出的一些公用函数包   |
| FastDFS              | FastDFS本体                    |
| fastdfs-nginx-module | FastDFS和nginx的关联模块       |
| nginx                | nginx1.15.4                   |

### 2. 安装编译环境
```shell
yum install git gcc gcc-c++ make automake autoconf libtool pcre pcre-devel zlib zlib-devel openssl-devel wget vim -y
```
```shell
yum install -y pcre pcre-devel
```
```shell
yum install -y zlib zlib-devel
```
```shell
yum install -y openssl openssl-devel 
```

### 3. 磁盘存放目录
| 说明                  | 位置           |
| :-------------------- | :------------- |
| 所有安装包             | /usr/local/src |
| 数据存储位置           | /home/dfs/     |
| #data/logs都存在了dfs  |                |

```shell
#创建数据存储目录
mkdir /home/dfs
#切换到安装目录准备下载安装包
cd /usr/local/src
```

## 三、开始安装
### 1. 安装libfastcommon
```shell
git clone https://github.com/happyfish100/libfastcommon.git --depth 1
cd libfastcommon/
#编译安装
./make.sh && ./make.sh install
```

### 2. 安装FastDFS
```shell
#返回上一级目录
cd ../ 
#从git上拉取fastdfs
git clone https://github.com/happyfish100/fastdfs.git --depth 1
cd fastdfs/
#编译安装
./make.sh && ./make.sh install 
```

```shell
#配置文件准备
cp /etc/fdfs/tracker.conf.sample /etc/fdfs/tracker.conf
cp /etc/fdfs/storage.conf.sample /etc/fdfs/storage.conf
#客户端文件，测试用
cp /etc/fdfs/client.conf.sample /etc/fdfs/client.conf
#供nginx访问使用
cp /usr/local/src/fastdfs/conf/http.conf /etc/fdfs/
#供nginx访问使用
cp /usr/local/src/fastdfs/conf/mime.types /etc/fdfs/
```

### 3. 安装fastdfs-nginx-module
```shell
#返回上一级目录
cd ../ 
git clone https://github.com/happyfish100/fastdfs-nginx-module.git --depth 1
cp /usr/local/src/fastdfs-nginx-module/src/mod_fastdfs.conf /etc/fdfs
```

### 4. 安装nginx
```shell
#下载nginx压缩包
wget http://nginx.org/download/nginx-1.15.4.tar.gz 
#解压
tar -zxvf nginx-1.15.4.tar.gz 
cd nginx-1.15.4/
#添加fastdfs-nginx-module模块
./configure --add-module=/usr/local/src/fastdfs-nginx-module/src/ 
#编译安装
make && make install 
```

## 四、相关配置
### 1. tracker配置
```shell
vim /etc/fdfs/tracker.conf

#需要修改的内容如下
# tracker服务器端口（默认22122,一般不修改）
port=22122  
# 存储日志和数据的根目录
base_path=/home/dfs  
```

### 2. storage配置
```shell
vim /etc/fdfs/storage.conf

#需要修改的内容如下
port=23000  # storage服务端口（默认23000,一般不修改）
base_path=/home/dfs  # 数据和日志文件存储根目录
store_path0=/home/dfs  # 第一个存储目录
tracker_server=192.168.0.104:22122  # tracker服务器IP和端口
http.server_port=8888  # http访问文件的端口(默认8888,看情况修改,和nginx中保持一致)
```

### 3. niginx配置
```shell
vim /etc/fdfs/mod_fastdfs.conf

#需要修改的内容如下
tracker_server=192.168.0.104:22122  #tracker服务器IP和端口
url_have_group_name=true
store_path0=/home/dfs
```
```shell
#配置nginx.config
vim /usr/local/nginx/conf/nginx.conf
#添加如下配置
server {
    listen       8888;    ## 该端口为storage.conf中的http.server_port相同
    server_name  localhost;
    location ~/group[0-9]/ {
        ngx_fastdfs_module;
    }
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   html;
    }
}
```

### 4. client配置
```shell
vim /etc/fdfs/client.conf

#需要修改的内容如下
base_path=/home/dfs
tracker_server=192.168.0.104:22122    #tracker服务器IP和端口
```

## 五、注意事项
- 注意文件及目录权限（`/etc/fastdfs` 的权限， **可读写的权限** ）
- 关闭防火墙
- 注意`ngnix.conf`中的用户

## 六、相关命令
### 1. 防火墙
```shell
#不关闭防火墙的话无法使用
systemctl stop firewalld.service #关闭
systemctl restart firewalld.service #重启
```

### 2. tracker
```shell
/etc/init.d/fdfs_trackerd start #启动tracker服务
/etc/init.d/fdfs_trackerd restart #重启动tracker服务
/etc/init.d/fdfs_trackerd stop #停止tracker服务
chkconfig fdfs_trackerd on #自启动tracker服务
```
**注：如不在此目录下，用命令 `find / -name fdfs_trackerd` 找到即可。**

### 3. storage
```shell
/etc/init.d/fdfs_storaged start #启动storage服务
/etc/init.d/fdfs_storaged restart #重动storage服务
/etc/init.d/fdfs_storaged stop #停止动storage服务
chkconfig fdfs_storaged on #自启动storage服务
```
**注：如不在此目录下，用命令 `find / -name fdfs_storaged` 找到即可。**

### 4. nginx
```shell
/usr/local/nginx/sbin/nginx #启动nginx
/usr/local/nginx/sbin/nginx -s reload #重启nginx
/usr/local/nginx/sbin/nginx -s stop #停止nginx
```

### 5. 文件上传
```shell
#保存后测试,返回ID表示成功  
#如：group1/M00/00/00/wKgAaFyMoNKAUNcVAAWjVxW4v70993.jpg
fdfs_upload_file /etc/fdfs/client.conf /home/1.jpg 
```

### 6. 本机迁移数据（更换不同的目录）
+ 更改配置文件
+ 复制原来的数据到新的目录
+ 重启三个服务
  + ```shell
    /usr/bin/fdfs_trackerd /etc/fdfs/tracker.conf restart
    ```
  + ```shell
    /usr/bin/fdfs_storaged /etc/fdfs/storage.conf restart
    ```
  + ```shell
    cd /usr/local/nginx/sbin
    ./nginx -s reload
    ```


## 七、使用docker搭建FastDFS
### 1. 镜像下载
首先下载`FastDFS`文件系统的`docker镜像`
```bash
docker search fastdfs
```
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装FastDFS/FastDFS镜像下载.png)
</center>

```bash
docker pull delron/fastdfs
```

下载完成之后查看：
```bash
docker images
```
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装FastDFS/FastDFS镜像查看.png)
</center>

### 2. 构建tracker容器和storage容器
使用`docker镜像`构建`tracker容器`（跟踪服务器，起到调度的作用）：
```
docker run -d --network=host --name tracker -v /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker
```
> 具体文件挂载目录根据实际情况

使用`docker镜像`构建`storage容器`（存储服务器，提供容量和备份服务）：
```
docker run -d --network=host --name storage -e TRACKER_SERVER=ip:22122 -v /var/fdfs/storage:/var/fdfs -e GROUP_NAME=group1 delron/fastdfs storage
```
上面需要填写你的`tracker`服务的`ip`地址，端口默认是`22122`。

> 具体文件挂载目录根据实际情况

### 3. 服务配置
进入`storage`容器，到`storage`的配置文件中配置`http`访问的端口，配置文件在`/etc/fdfs`目录下的`storage.conf`。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装FastDFS/FastDFS的storage容器配置文件查看1.png)
</center>

 默认端口是`8888`，也可以不进行更改。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装FastDFS/FastDFS的storage容器配置文件查看2.png)
</center>

### 4. 配置nginx（容器内自带）
在`/usr/local/nginx`目录下，修改`nginx.conf`文件
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装FastDFS/FastDFS容器内nginx目录.png)
</center>

默认配置如下：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装FastDFS/FastDFS容器内nginx默认配置.png)
</center>

此时文件系统以搭建完毕，使用web模块进行文件的上传，将文件上传至`FastDFS`文件系统，此处不详细解释。
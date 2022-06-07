# Centos7安装FastDFS

[FastDFS官方地址](https://github.com/happyfish100/fastdfs/wiki1)

[toc]

## 一、FastDFS介绍
**`FastDFS`是一个开源的轻量级分布式文件系统，它对文件进行管理，功能包括：文件存储、文件同步、文件访问（文件上传、文件下载）等，解决了大容量存储和负载均衡的问题。特别适合以文件为载体的在线服务，如相册网站、视频网站等等。**

`FastDFS`为互联网量身定制，充分考虑了 **冗余备份** 、 **负载均衡** 、 **线性扩容等机制** ，并注重 **高可用** 、 **高性能** 等指标，使用`FastDFS`很容易搭建一套高性能的文件服务器集群提供文件上传、下载等服务。

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
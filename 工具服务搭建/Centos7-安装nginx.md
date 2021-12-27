### 1. 下载

+ 切换路径
  ```shell
  cd /opt/nginx/
  ```

+ 下载
  ```shell
  wget http://nginx.org/download/nginx-1.18.0.tar.gz
  ```

### 2. 安装依赖

```shell
yum -y install gcc zlib zlib-devel pcre-devel openssl openssl-devel gd-devel
```

+ 可能需要安装make
  ```shell
  yum -y install gcc automake autoconf libtool make
  ```

### 3. 编译安装
+ 解压文
  ```shell
  tar -zxvf nginx-1.18.0.tar.gz
  ```

+ 配置模块
  + 切换目录
    ```shell
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

PATH=$PATH:/usr/local/nginx/sbin
export PATH

# 属性配置文件
source /etc/profile
```

### 5. 注意事项
+ nginx需要添加新模块时，下载相同版本，执行解压，configurat时添加新的模块，然后make，不执行install，然后重启ngin
+ make出现错误时，执行make clean，然后添加依赖后再make
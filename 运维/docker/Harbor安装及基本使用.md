# Harbor安装及基本使用

[toc]

## 一、安装
### 1. 下载安装
本篇笔记下载最新版`harbor-offline-installer-v2.1.5.tgz`

首先在`harbor`的`github`仓库上下载安装包 https://github.com/goharbor/harbor/releases/tag/v2.1.5  
将下载好的压缩包上传至`Linux`服务器

也可以直接通过`wget`下载：
```bash
wget https://github.com/goharbor/harbor/releases/download/v2.1.5/harbor-offline-installer-v2.1.5.tgz
```

解压：
```bash
tar -zxvf harbor-offline-installer-v2.1.5.tgz
```

### 2. 配置及安装
解压后，进入安装目录，将配置文件模板复制一份出来：
```bash
cd harbor
cp harbor.yml.tmpl harbor.yml
```

接着就是修改`harbor.yml`的配置文件：
```bash
[root@localhost harbor] vim harbor.yml
# 本机ip
hostname：192.168.1.226

# http related config
http:
  # port for http, default is 80. If https enabled, this port will redirect to https port
  # 访问端口
  port: 80

# https根据情况配置
# https related config
#https:
  # https port for harbor, default is 443
  # port: 443
  # The path of cert and key files for nginx
  # certificate: /your/certificate/path
  # private_key: /your/private/key/path

# 设置admin账户的密码
harbor_admin_password: 123456
# external_url: 配置自己的域名映射地址，没有就不配，配置了该选项就会导致hostname失效
# 其他配置采用默认配置
```
执行`./prepare`。

**`./prepare`** 命令会生成一个`common`文件夹并在`common`文件夹下生成一个`config`文件夹，里面存放的则是`docker-compose.yml`中的那些`services`所需要的配置文件：
```bash
sudo ./prepare
```

再执行`./install.sh`，可能会有如下错误：
```bash
[root@localhost harbor]# sudo ./install.sh

[Step 0]: checking if docker is installed ...

Note: docker version: 20.10.14

[Step 1]: checking docker-compose is installed ...
✖ Need to install docker-compose(1.18.0+) by yourself first and run this script again.
```
错误的原因是未安装`docker-compose`，`docker-compose`用来启动`Harbor`。

安装`docker-compose`：
```bash
[root@localhost harbor]# yum install docker-compose -y

# 或者
[root@localhost harbor]# yum install -y python3-pip
[root@localhost harbor]# pip3 install docker-compose
```

再次执行`install.sh`，可能还会继续报错：
```
ERROR: for nginx  Cannot start service proxy: driver failed programming external connectivity on endpoint nginx (1957b0b109b950ce4674c77bec9d30b6ba283c2ce653d864b31030a48c                                                              3dd010): Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
```
端口冲突，修改`harbor.yml`中的端口重新执行`install.sh`（演示过程将端口改为`1180`）。

成功执行之后打印：
```bash
..............
Note: stopping existing Harbor instance ...
Stopping harbor-jobservice ... done
Stopping harbor-core       ... done
Stopping harbor-portal     ... done
Stopping registry          ... done
Stopping registryctl       ... done
Stopping redis             ... done
Stopping harbor-db         ... done
Stopping harbor-log        ... done
Removing harbor-jobservice ... done
Removing nginx             ... done
Removing harbor-core       ... done
Removing harbor-portal     ... done
Removing registry          ... done
Removing registryctl       ... done
Creating harbor-log ... done
Removing harbor-db         ... done
Removing harbor-log        ... done
Removing network harbor_harbor

Creating registry ... done
Creating harbor-core ... done
Creating network "harbor_harbor" with the default driver
Creating nginx ... done
Creating harbor-db ...
Creating redis ...
Creating harbor-portal ...
Creating registry ...
Creating registryctl ...
Creating harbor-core ...
Creating harbor-jobservice ...
Creating nginx ...
✔ ----Harbor has been installed and started successfully.----
```

访问 http://ip:harbor中的端口

### 3. 启动与停止
```bash
# 停止容器
docker-compose stop

# 启动容器
docker-compose start

# 后台启动容器
docker-compose up -d
```

## 二、基本使用
### 1. 系统管理
略

### 2. 创建项目及命令查看
先在`harbor`上创建项目：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/运维/docker/Harbor安装及基本使用/Harbor创建项目.png)
</center>

注意：
- 当项目设为 **公开** 后，任何人都有此项目下镜像的读权限。命令行用户不需要`“docker login”`就可以拉取此项目下的镜像。
- 容量为`-1`则表示不做限制。

创建完成之后查看此项目的推送命令：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/运维/docker/Harbor安装及基本使用/Harbor创建项目查看项目推送命令.png)
</center>

`Docker`推送命令：
```bash
# 在项目中标记镜像：
docker tag SOURCE_IMAGE[:TAG] 192.168.1.226:1180/test/REPOSITORY[:TAG]

# 推送镜像到当前项目：
docker push 192.168.1.226:1180/test/REPOSITORY[:TAG]
```

### 3. docker push到harbor
#### 3.1 docker基础配置
再使用另一台机器的`docker`。

修改本机的`docker`配置文件并重启`docker`，注意重启`docker`前先重新加载配置文件：
```bash
vim /etc/docker/daemon.json

# 添加
{
    "insecure-registries": ["192.168.1.226:1180"]
}
```

重新加载配置文件并重启docker：
```bash
#重启docker
systemctl daemon-reload
systemctl restart docker
```

#### 3.2 镜像打上tag
首先登陆`docker`仓库（由于上面的`test`项目设置的是 **不公开** ，需要登录，否则会提示权限不足）：
```bash
docker login <harbor所在服务器的IP>:<端口>
# 输入前面注册的账号密码
name:......
password:.....

# 完整如下
[root@localhost ~]# docker login 192.168.1.226:1180
Username: admin
Password:
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```
按照`harbor`上的命令格式为目标镜像打上`tag`。

假设已有`nginx:1.16.1`的镜像（没有的话可以先从公共仓库上拉取，命令`docker pull nginx:1.16.1 `）：
```bash
# nginx:1.16.1为本地镜像名 
# 192.168.1.226:1180/test/nginx:1.0.0为包含目标harbor的地址及项目名称的tag
docker tag nginx:1.16.1 192.168.1.226:1180/test/nginx:1.0.0
```

推送：
```bash
docker push 192.168.1.226:1180/test/nginx:1.0.0
```
再到`harbor`上的`test`项目中查看。

### 4. docker pull镜像

从`harbor`上拉取镜像：
```bash
# 拉取
[root@localhost ~]# docker pull 192.168.1.226:1180/test/nginx:1.0.0
1.0.0: Pulling from test/nginx
Digest: sha256:6939051946770d8ee2851bf63952236659d6b736f0d4556ed1b1071da469b3ea
Status: Downloaded newer image for 192.168.1.226:1180/test/nginx:1.0.0

# 查看
[root@localhost ~]# docker images |grep nginx
192.168.1.226:1180/test/nginx        1.0.0               64f1f7d81bd8        2 years ago         126MB
```

再到`harbor`上的`test`项目中查看。可以看到镜像`192.168.1.226:1180/test/nginx`下载数为`1`。
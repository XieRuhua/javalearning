# Docker安装及常用命令

- Docker 官方主页: [https://www.docker.com](https://www.docker.com/)
- Docker 官方博客: https://blog.docker.com/
- Docker 官方文档: https://docs.docker.com/

[toc]

## 一、安装Docker
### 1. 检查系统内核版本
**`Docker`运行在`CentOS 7`上时，要求操作系统为`64位`，内核版本为`3.10`及以上。**  
确认本机已经安装了满足要求的`Linux`内核。使用命令`uname -r`来检查内核版本信息。
```bash
[root@localhost ~]# uname -r
3.10.0-957.el7.x86_64
```

### 2. 在CentOS 7中安装Docker
使用命令`yum install -y docker`安装`Docker`，`“-y”`表示不询问，使用默认配置进行安装。
```bash
yum install -y docker
```

**备注**：`Docker`从`1.13`版本之后采用时间线的方式作为版本号，分为`社区版CE`和`企业版EE`。  
社区版是免费提供给个人开发者和小型团体使用的，企业版会提供额外的收费服务，比如经过官方测试认证过的基础设施、容器、插件等。
所以，需要将安装命令修改为`yum install -y docker-ce`。（`20201129`修改）

### 3. Docker启动、停止、重启等命令
使用下列命令：
```bash
# 启动
systemctl start docker.service
# 停止
systemctl stop docker.service
# 重启
systemctl restart docker.service

# Docker 服务开机自启
sudo systemctl enable docker.service
#  Docker 服务关闭开机自启
sudo systemctl disable docker.service
```

查看`Docker`运行状态：
```bash
[root@localhost ~]systemctl status docker.service
● docker.service - Docker Application Container Engine
   Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
   Active: active (running) since Tue 2022-02-15 13:57:39 CST; 2 months 29 days ago
     Docs: https://docs.docker.com
 Main PID: 2848 (dockerd)
    Tasks: 10
   Memory: 63.0M
   CGroup: /system.slice/docker.service
           └─2848 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
```

### 4. 查看版本信息
输入`docker -v`，返回版本信息表明`Docker`安装成功
```bash
[root@localhost ~]# docker version
Docker version 20.10.12, build e91ed57
```

### 5. 打开2375监听端口
修改`/usr/lib/systemd/system/docker.service`，在`[service]`的`ExecStart` ，添加 `-H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock`
```bash
[root@localhost ~]# vim /usr/lib/systemd/system/docker.service
.......
[service]
.......
ExecStart=/usr/bin/dockerd-current -H tcp://0.0.0.0:2375 -H unix://var/run/docker.sock \
          --add-runtime docker-runc=/usr/libexec/docker/docker-runc-current \
.......
```

刷新配置文件，并重启`Docker`
```
systemctl daemon-reload
systemctl restart docker
```

查询端口开放情况：
```bash
[root@localhost ~]# netstat -ntpl
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp6       0      0 :::2375                 :::*                    LISTEN      10373/dockerd-curre
```

## 二、卸载Docker
### 1. 准备工作
杀死`Docker`有关的容器：
```bash
docker kill $(docker ps -a -q)
```

2.删除所有`Docker`容器：
```bash
docker rm $(docker ps -a -q)
```

3.删除所有`Docker`镜像：
```bash
docker rmi $(docker images -q)
```

停止 `Docker` 服务：
```bash
systemctl stop docker
```

删除`Docker`相关存储目录：（执行以下四个命令）
```bash
rm -rf /etc/docker
rm -rf /run/docker
rm -rf /var/lib/dockershim
rm -rf /var/lib/docker
```

如果删除不掉，则先`umount`：
```bash
umount /var/lib/docker/devicemapper
```
然后再重新执行上面那步 **“删除`Docker`相关存储目录”。**

### 2. 卸载工作
查看系统已经安装了哪些`Docker`包：
```bash
[root@localhost ~]# yum list installed | grep docker
docker.x86_64                      2:1.13.1-209.git7d71120.el7.centos  @extras
docker-client.x86_64               2:1.13.1-209.git7d71120.el7.centos  @extras
docker-common.x86_64               2:1.13.1-209.git7d71120.el7.centos  @extras
```

卸载相关包：
```bash
[root@localhost ~]# yum remove docker.x86_64 docker-client.x86_64 docker-common.x86_64
```
接着会出现选择提示，直接输入`“y”`然后回车就可以。再次查看
```bash
yum list installed | grep docker
```
不再出现相关信息，证明相关包卸载成功，

再看看`Docker`命令：
```bash
[root@localhost ~]# docker version
-bash: /usr/bin/docker: No such file or directory
```
无法找到命令，表示成功卸载`Docker`

## 三、Docker常用命令
[菜鸟教程-Docker 命令大全](https://www.runoob.com/docker/docker-command-manual.html)
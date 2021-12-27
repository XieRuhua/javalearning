# ADoc搭建

## 前置条件

mindoc_linux_amd64.7z
mysql
CentOS 7+

注：软件放置位置 `/home`

MinDoc下载地址：
https://github.com/lifei6671/mindoc/releases

## 安装配置

1.创建数据库

> CREATE DATABASE mindoc DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;

2.配置文件

> /mindoc/conf/app.conf

```
db_adapter=mysql
db_host=localhost
db_port=3306
db_database=mindoc
db_username=
db_password=
...
```

3.初始化数据库

> /mindoc/mindoc_linux_amd64 install

## 启动方式

> nohup /mindoc/mindoc_linux_amd64 &

## 访问地址

地址：[https://localhost:8181](https://localhost:8181/)
管理员/密码：admin/123456
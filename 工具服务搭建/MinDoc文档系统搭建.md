# MinDoc搭建

[项目github地址](https://github.com/mindoc-org/mindoc)

[toc]

## 一、简述
`MinDoc` 是一款针对IT团队开发的简单好用的文档管理系统。

`MinDoc` 的前身是 `SmartWiki` 文档系统。`SmartWiki` 是基于 `PHP` 框架 `laravel` 开发的一款文档管理系统。因 PHP` 的部署对普通用户来说太复杂，所以改用 `Golang` 开发。可以方便用户部署和实用。

开发缘起是公司IT部门需要一款简单实用的项目接口文档管理和分享的系统。其功能和界面源于 `kancloud` 。

可以用来储存日常接口文档，数据库字典，手册说明等文档。内置项目管理，用户管理，权限管理等功能，能够满足大部分中小团队的文档管理需求。

## 二、前置条件
**mindoc_linux_amd64.7z**  
**mysql**  
**CentOS 7+**  

> 注：本篇笔记的软件放置位置 `/home`

MinDoc下载地址：https://github.com/lifei6671/mindoc/releases

## 三、安装配置

### 1.创建数据库
```java
CREATE DATABASE mindoc DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_general_ci;
```

### 2.配置文件
```shell
vim /mindoc/conf/app.conf
```
```
db_adapter=mysql
db_host=localhost
db_port=3306
db_database=mindoc
db_username=
db_password=
...
```

### 3.初始化数据库
```shell
/mindoc/mindoc_linux_amd64 install
```

## 三、启动方式
```shell
nohup /mindoc/mindoc_linux_amd64 &
```

## 四访问地址
地址：[https://localhost:8181](https://localhost:8181/)  
管理员/密码：admin/123456
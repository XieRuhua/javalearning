## centos7  yum安装mysql 5.7版本

### 1.mysql 下载
```sh
[root@localhost ~]# cd /usr/local/
[root@alibyleilei local]# wget https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
```

如果提示wget不存在则先安装 wget命令
```
yum -y install wget
```

使用wget成功下载mysql 后文件夹中会有一个mysql57----.rpm的文件(mysql5.7安装源)
```
[root@alibyleilei local]# ll
-rw-r--r--  1 root root   25680 Apr 27  2017 mysql57-community-release-el7-11.noarch.rpm
```

使用安装源安装
```
[root@alibyleilei local]# yum -y localinstall mysql57-community-release-el7-11.noarch.rpm
```

安装mysql服务端
```
[root@alibyleilei local]# yum -y install mysql-community-server
```
..................等待安装完成，可能需要一段时间


### 2.启动mysql服务
```
systemctl start mysqld
```
此方式安装完成后会给mysql设定一个初始密码 

在/var/log/mysqld.log 中可查看mysql初始密

```shell
grep 'temporary password' /var/log/mysqld.log
```

或者
```shell
cat  /var/log/mysqld.log
```

```
2020-01-17T06:56:15.867183Z 1 [Note] A temporary password is generated for root@localhost: LHwr;4qnkruE           (这是我安装时的初始密码 )
```

使用此密码进行登陆Mysql数据库后修改密码

登陆
```
[root@alibyleilei local]# mysql -u root -p
Enter password: 密码  （输入时不会显示）
```

输入成功后可看到数据库信息
```
[root@alibyleilei local]# mysql -u root -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 8
Server version: 5.7.29 MySQL Community Server (GPL)  
Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.  
Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> 
```

### 3.修改密码
必须有大小写英文以及符号
```
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY '~Rex|123@456,';
Query OK, 0 rows affected (0.01 sec)
```

### 4.开启mysql远程访问
```
mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '~Rex|123@456,' WITH GRANT OPTION;
```

刷新权限
```shell
flush privileges;
```
exit退出mysql

### 5.mysql设为开机启动
```
[root@alibyleilei local]# systemctl enable mysqld
[root@alibyleilei local]# systemctl daemon-reload
```

### 6.防火墙设置（如果有的话）
查看防火墙
```
[root@alibyleilei local]# firewall-cmd --state
running
[root@alibyleilei local]# firewall-cmd --permanent --list-port
7000-7005/udp 7000-7005/tcp 53/udp 80/tcp
[root@alibyleilei local]#
```

放开3306端口 开启后要从启防火墙 查看列表3306是否开
```
[root@alibyleilei local]# firewall-cmd --zone=public --add-port=3306/tcp --permanent
success
[root@alibyleilei local]# firewall-cmd --reload
success
[root@alibyleilei local]# firewall-cmd --permanent --list-port
7000-7005/udp 7000-7005/tcp 53/udp 80/tcp 3306/tcp
[root@alibyleilei local]#
```
如果是在云服务器上搭建mysql 还要记得安全组开放对应端口

### 7.使用navicat 连接测试
### 8. 注意事项
+ 移除系统自带数据库依赖
```shell
#移除之前的安装依赖
yum -y remove mysql-libs*
#错误：依赖检测失败：mariadb-connector-c-config 被 mysql-community-server-8.0.19-10.fc31.x86_64 取代#
yum remove mariadb-connector-c-config -y
```

+ 安装mysql5.7时Error: Unable to find a match: mysql-community-server
```sql
先执行：yum module disable mysql
再执行：yum -y install mysql-community-server
```

+ Job for mysqld.service failed because the control process exited with error code
```shell
rm -rf /var/lib/mysql 
```
### 9. 忘记密码
```
在[mysqld]的段中加上一句：skip-grant-tables
```

+ 重启后用root进入，无需输入密码

```shell
# mysql 5.7
UPDATE mysql.user SET authentication_string= password ( '~Rex|123@456,' ) WHERE User = 'root' ;
```
+ 刷新权限
```shell
flush privileges; 
```
+ 配置文件去掉 skip-grant-tables
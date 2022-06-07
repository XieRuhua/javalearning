# Centos7安装mysql5.7版本

### 1. mysql下载
```shell
[root@localhost ~]# cd /usr/local/
[root@localhost local]# wget https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm
```

如果提示`wget`不存在则先安装 `wget`命令
```shell
yum -y install wget
```

使用`wget`成功下载`mysql` 后  文件夹中会有一个`mysql57----.rpm`的文件(`mysql5.7`安装源)
```shell
[root@localhost local]# ll
-rw-r--r--  1 root root   25680 Apr 27  2017 mysql57-community-release-el7-11.noarch.rpm
```

### 2. 使用安装源安装
```shell
[root@localhost local]# yum -y localinstall mysql57-community-release-el7-11.noarch.rpm
```

### 3. 安装mysql服务端
```shell
[root@localhost local]# yum -y install mysql-community-server
```
..................等待安装完成，可能需要一段时间


如果安装过程提示：
```shell
从 file:///etc/pki/rpm-gpg/RPM-GPG-KEY-mysql 检索密钥
导入 GPG key 0x5072E1F5:
 用户ID     : "MySQL Release Engineering <mysql-build@oss.oracle.com>"
 指纹       : a4a9 4068 76fc bd3c 4567 70c8 8c71 8d3b 5072 e1f5
 软件包     : mysql57-community-release-el7-11.noarch (@/mysql57-community-release-el7-11.noarch)
 来自       : /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql


mysql-community-libs-compat-5.7.38-1.el7.x86_64.rpm 的公钥尚未安装


 失败的软件包是：mysql-community-libs-compat-5.7.38-1.el7.x86_64
 GPG  密钥配置为：file:///etc/pki/rpm-gpg/RPM-GPG-KEY-mysql
```

执行（后面的年份根据实际年份）：
```shell
rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
```

### 2.启动mysql服务
```shell
systemctl start mysqld

## 可能会提示：
## Failed to start mysqld.service: Unit not found.
## 在执行一次 yum -y install mysql-community-server 即可
```

其他命令：
```shell
# 开机启动
systemctl enable mysqld

# 关闭开机启动
systemctl disable mysqld

# 启动服务
systemctl start mysqld

# 停止服务
systemctl stop mysqld

# 重启服务
systemctl restart mysqld

# 查看服务状态
systemctl status mysqld
systemctl is-active sshd.service

# 结束服务进程(服务无法停止时)
systemctl kill mysqld
```
### 3. 查看初始密码并登录
此方式安装完成后会给`mysql`设定一个初始密码 

在`/var/log/mysqld.log` 中可查看`mysql`初始密码：

```shell
grep 'temporary password' /var/log/mysqld.log
# 或者
cat  /var/log/mysqld.log
```
```shell
2020-01-17T06:56:15.867183Z 1 [Note] A temporary password is generated for root@localhost: LHwr;4qnkruE  # (这是我安装时的初始密码 )
```
使用此密码进行登录`Mysql`数据库后修改密码

登陆
```shell
[root@localhost local]# mysql -u root -p
Enter password: 密码  （输入时不会显示）
```

输入成功后可看到数据库信息
```shell
[root@localhost local]# mysql -u root -p
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

### 4. 修改密码
**注意：必须有大小写英文以及符号，否则会提示密码过于简单，修改失败**
```shell
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'XXXXXXX';
Query OK, 0 rows affected (0.01 sec)
```

### 5. 开启mysql远程访问
```shell
mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'XXXXXXX' WITH GRANT OPTION;
```

刷新权限
```shell
flush privileges;
```

退出`mysql`：
```shell
exit;
# 或者
quit;
```

### 6. mysql设为开机启动

```shell
[root@localhost local]# systemctl enable mysqld
[root@localhost local]# systemctl daemon-reload
```

### 7.防火墙设置（开放3306端口）
查看防火墙
```shell
[root@localhost local]# firewall-cmd --state
running
[root@localhost local]# firewall-cmd --permanent --list-port
7000-7005/udp 7000-7005/tcp 53/udp 80/tcp
[root@localhost local]#
```

放开`3306`端口，开启后要重启防火墙，查看列表`3306`是否开启
```shell
# 开启3306端口
[root@localhost local]# firewall-cmd --zone=public --add-port=3306/tcp --permanent
success
# 重启防火墙
[root@localhost local]# firewall-cmd --reload
success
# 查看端口列表
[root@localhost local]# firewall-cmd --permanent --list-port
7000-7005/udp 7000-7005/tcp 53/udp 80/tcp 3306/tcp
[root@localhost local]#
```
**注意：如果是在云服务器上搭建`mysql` 还要记得安全组开放对应端口**

### 8. 使用navicat 连接测试
### 9. 注意事项
+ 移除系统自带数据库依赖
  ```shell
  #移除之前的安装依赖
  yum -y remove mysql-libs*
  #错误：依赖检测失败：mariadb-connector-c-config 被 mysql-community-server-8.0.19-10.fc31.x86_64 取代#
  yum remove mariadb-connector-c-config -y
  ```
+ 安装`mysql5.7`时`Error: Unable to find a match: mysql-community-server`
  ```shell
  先执行：yum module disable mysql
  再执行：yum -y install mysql-community-server
  ```
+ 过程中提示：`Job for mysqld.service failed because the control process exited with error code`
  ```shell
  rm -rf /var/lib/mysql 
  ```

### 9. 忘记密码
找到`my.conf`文件（一般在`/etc/my.cnf`，有些版本在`/etc/mysql/my.cnf`）在配置文件中，增加如下代码（作用是登录`mysql`的时候跳过密码验证）
```shell
[mysqld]
skip-grant-tables
```

重启后用`root`进入，无需输入密码
```
[root@localhost ~]mysql -u root
```

进入`mysql`之后执行如下语句（设置密码）：
```shell
# mysql 5.7
UPDATE mysql.user SET authentication_string= password ('XXXXXXX') WHERE User = 'root' ;
```

刷新权限
```shell
flush privileges ; 
```
然后将之前加在配置文件里面的两句代码注释或删除掉，最后重启`mysql`服务，就可以使用刚刚设置的密码登录了。

### 10. linux卸载mysql的步骤
#### 10.1 首先查看mysql的安装情况
```shell
rpm -qa|grep -i mysql
```

显示之前安装了（ **注：`xxxxxxxx`为具体版本** ）：
```shell
MySQL-client-xxxxxxxx
MySQL-server-xxxxxxxx
```

#### 10.2 停止mysql服务，并删除包
删除命令：`rpm -e –nodeps 包名`
```shell
rpm -ev MySQL-client-xxxxxxxx
rpm -ev MySQL-server-xxxxxxxx
```

如果提示依赖包错误，则使用以下命令尝试
```shell
rpm -ev MySQL-client-xxxxxxxx --nodeps
```

如果提示错误：`error: %preun(xxxxxx) scriptlet failed, exit status 1`  
则用以下命令尝试:
```shell
rpm -e --noscripts MySQL-client-xxxxxxxx
```

#### 10.3 查找之前老版本mysql的目录、并且删除老版本mysql的文件和库
查找`mysql`目录
```shell
find / -name mysql
```

查找结果如下：
```shell
/var/lib/mysql
/var/lib/mysql/mysql
/usr/lib64/mysql
```

删除对应的`mysql`目录
```shell
rm -rf /var/lib/mysql
rm -rf /var/lib/mysql
rm -rf /usr/lib64/mysql
```

注意：卸载后`/etc/my.cnf`不会删除，需要进行手工删除
```shell
rm -rf /etc/my.cnf
```

#### 10.4 再次查找机器是否安装mysql
```shell
rpm -qa|grep -i mysql
```

无结果，说明已经卸载彻底，接下来直接安装`mysql`即可。
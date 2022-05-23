# Centos7安装java


## 方式一：yum安装
1.查看当前`centos`支持的`JDK`列表
```shell
yum -y list java*
```

2.安装自己需要的版本
```shell
yum install -y java-1.8.0-openjdk.x86_64

```
**注意：默认安装到 `usr/lib/jvm/`，无需再配置环境变量**


3.安装完成之后验证是否安装成功：
```shell
java -version

openjdk version "1.8.0_332"
OpenJDK Runtime Environment (build 1.8.0_332-b09)
OpenJDK 64-Bit Server VM (build 25.332-b09, mixed mode)
```

## 方式二：解压缩安装
1.从官网下载自己所需的版本 [Oracle官网JDK8下载地址](https://www.oracle.com/java/technologies/javase/javase8u211-later-archive-downloads.html)  

2.上传到服务器

3.解压缩
```shell
tar -zxvf jdk-XXXX
```

4.配置环境变量
```shell
vim /etc/profile
```

将以下代码写入环境变量中（需要根据实际情况修改`JAVA_HOME`路径）
```shell
export JAVA_HOME=/usr/local/software/jdk/jdk1.8.0_291               
export CLASSPATH=$:CLASSPATH:$JAVA_HOME/lib/ 
export PATH=$PATH:$JAVA_HOME/bin
```

5.刷新配置文件
```shell
source /etc/profile
```

6.安装完成之后验证是否安装成功：
```shell
java -version

openjdk version "1.8.0_332"
OpenJDK Runtime Environment (build 1.8.0_332-b09)
OpenJDK 64-Bit Server VM (build 25.332-b09, mixed mode)
```
# Centos7安装Redis（含cluster方式集群部署）

[toc]

## 一、单体服务安装
### 1. 安装前准备，安装gcc（因为redis是用C语言开发的，安装前要先安装gcc环境）
```bash
yum install -y gcc 
```

### 2. 下载redis安装包
```bash
# 安装地址（版本自行选择）
cd /usr/local/
wget http://download.redis.io/releases/redis-5.0.3.tar.gz
```

### 3. 解压
```bash
tar -zxvf redis-5.0.3.tar.gz
```

`cd`切换到`redis`解压目录下，执行编译
```bash
cd redis-5.0.3
make
```

执行如下命令，创建redis目录以及lib中的启动命令等
```bash
make MALLOC=libc
make install PREFIX=/usr/local/redis
```

补充：`make`可能会出现如下错误
```bash
cd src && make all
make[1]: 进入目录“/home/soft/redis/redis-5.0.12/src”
    CC adlist.o
In file included from adlist.c:34:0:
zmalloc.h:50:31: 致命错误：jemalloc/jemalloc.h：没有那个文件或目录
 #include <jemalloc/jemalloc.h>
                               ^
编译中断。
make[1]: *** [adlist.o] 错误 1
make[1]: 离开目录“/home/soft/redis/redis-5.0.12/src”
make: *** [all] 错误 2
```

再次执行：
```bash
make MALLOC=libc
make install PREFIX=/usr/local/redis
```

### 4. 启动服务
```bash
cd /usr/local/redis/bin/
./redis-server
```

### 5. 后台启动
从 redis 的源码目录中复制 `redis.conf` 到 `redis` 的安装目录
```bash
cp /usr/local/redis-5.0.3/redis.conf /usr/local/redis/bin/
```

修改 `redis.conf` 文件，把 `daemonize no` 改为 `daemonize yes`  
`Redis daemonize`介绍：
`redis.conf`配置文件中`daemonize`表示 **守护线程启动** ，默认是`NO`。用来指定`redis`是否要用 **守护线程** 的方式启动（即后台启动）。

**2、daemonize 设置yes或者no区别**
- `daemonize yes`：redis采用的是单进程多线程的模式。当redis.conf中选项daemonize设置成yes时，代表开启守护进程模式。在该模式下，redis会在后台运行，并将进程pid号写入至redis.conf选项pidfile设置的文件中，此时redis将一直运行，除非手动kill该进程。
- `daemonize:no`: 当daemonize选项设置成no时，当前界面将进入redis的命令行界面，exit强制退出或者关闭连接工具(putty,xbash等)都会导致redis进程退出。

启动
```bash
cd /usr/local/redis/bin
 ./redis-server redis.conf
```

重启
```bash
cd /usr/local/redis/bin

./redis-cli shutdown
./redis-server redis.conf
```

### 6. 设置远程访问和密码
远程访问的设置和密码设置均在配置文件`redis.conf`中。

**远程访问：**
```bash
cd /usr/local/redis/bin
vim redis.conf
````
找到`bind`属性，该属性默认是`127.0.0.1`，意思是只能本机(服务器)访问，要远程连接则需要把该属性注释掉，也可以改成物理机的ip也就只有自己能访问，注释掉的意思就是所有人都可以访问

**密码设置**  
继续往下找到`requirepass`属性，该属性是设置`redis`的密码，默认是没有密码即一串空的字符串，需要设置密码  
同时把`protected-mode yes`改为`protected-mode no`（该设置表示在没有密码的情况下，关闭保护模式）

配置完成后保存退出，重启`redis`

## 二. Redis集群搭建（cluster模式）
### 1. redis集群简介
redis集群三种模式
- **主从模式**：可以实现读写分离，数据备份。但是并不是「高可用」的
- **哨兵模式**：可以看做是主从模式的「高可用」版本，其引入了`Sentinel`对整个`Redis`服务集群进行监控。但是由于只有一个主节点，因此仍然有写入瓶颈。
- **Cluster模式**：不仅提供了高可用的手段，同时数据是分片保存在各个节点中的，可以支持高并发的写入与读取。实现也是其中最复杂的。

下面介绍`cluster`模式的搭建过程：

### 2. 集群清单（注意：这里先只做三个节点）
> 演示用同一台机器不同端口来表示不同节点，实际以开发情况而定
```bash
x.x.x.x(内网172.17.0.13)
	IP：172.17.0.13		Port：7001
	IP：172.17.0.13		Port：7002
	IP：172.17.0.13		Port：7003
```

### 3. 配置节点
> 文档演示的集群目录为`/home/soft/redis-cluster`
```bash
mkdir -p /home/soft/redis-cluster
cd /home/soft/redis-cluster
```

集群目录复制之前安装好的`redis-server`和`redis-cli`软链接
```bash
ln -s /usr/local/redis/bin/redis-cli ./redis-cli
ln -s /usr/local/redis/bin/redis-server ./redis-server
```

创建集群节点的数据存放目录
```bash
mkdir data
cd data
mkdir 7001 7002 7003
```

复制配置文件到集群目录：
```bash
cd /home/soft/redis-cluster
cp /usr/local/redis/bin/redis.conf ./redis-7001.conf
cp /usr/local/redis/bin/redis.conf ./redis-7002.conf
cp /usr/local/redis/bin/redis.conf ./redis-7003.conf
```

修改其配置：
```bash
vim redis-7001.conf
```

部分配置如下：
```bash
# 端口
port 7001
# 设置为守护进程，配置 redis 后台运行
daemonize yes
# pid 文件，默认6379，也改为对应的端口
pidfile /var/run/redis_7001.pid
# 关闭保护模式
protected-mode no
# 密码
requirepass xrh123456
# 开启集群
cluster-enabled yes
# 集群配置文件，不需要我们维护，首次启动的时候会自动生成
cluster-config-file nodes_7001.conf
# 请求超时时间
cluster-node-timeout 10100
# 数据保存位置
dir /home/soft/redis-cluster/data/7001

########################其他配置保持不变（或视实际使用场景变化）#########################
```

其它`3`个配置文件，同样的修改方式，`7001` 对应改为`700n`

### 4. 启停脚本
#### 4.1 启动脚本
创建启动脚本：
```bash
touch start-all.sh
# 修改执行权限
chmod +x start-all.sh
```

脚本内容：
```bash
/home/soft/redis-cluster/redis-server /home/soft/redis-cluster/redis-7001.conf
/home/soft/redis-cluster/redis-server /home/soft/redis-cluster/redis-7002.conf
/home/soft/redis-cluster/redis-server /home/soft/redis-cluster/redis-7003.conf
```

启动：
```bash
./start-all.sh
```

打印如下：
```bash
[root@VM-0-13-centos redis-cluster]# ./start-all.sh
8859:C 05 Jul 2022 10:41:11.529 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
8859:C 05 Jul 2022 10:41:11.529 # Redis version=5.0.3, bits=64, commit=00000000, modified=0, pid=8859, just started
8859:C 05 Jul 2022 10:41:11.529 # Configuration loaded
8861:C 05 Jul 2022 10:41:11.533 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
8861:C 05 Jul 2022 10:41:11.533 # Redis version=5.0.3, bits=64, commit=00000000, modified=0, pid=8861, just started
8861:C 05 Jul 2022 10:41:11.533 # Configuration loaded
8863:C 05 Jul 2022 10:41:11.536 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
8863:C 05 Jul 2022 10:41:11.536 # Redis version=5.0.3, bits=64, commit=00000000, modified=0, pid=8863, just started
8863:C 05 Jul 2022 10:41:11.536 # Configuration loaded
```

#### 4.2 停止脚本
按找启动脚本的创建和赋权步骤，创建 `redis` 集群的停止脚本
```bash
stop-all.sh
```

脚本内容（如设置密码则需要加上参数 `-a 密码` ）：
```bash
/home/soft/redis-cluster/redis-cli -p 7001 -a xrh123456 shutdown
/home/soft/redis-cluster/redis-cli -p 7002 -a xrh123456 shutdown
/home/soft/redis-cluster/redis-cli -p 7003 -a xrh123456 shutdown
```

### 5. 创建集群
#### 5.1 创建
随便登录一个节点执行`redis-cli`，因为redis集群采用`P2P模式`，是完全去中心化的，不存在中心节点或者代理节点；

执行创建集群命令
```bash
./redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 --cluster-replicas 1
```

由于我们设置过密码且节点数量过少，会提示如下错误
```bash
[ERR] Node 127.0.0.1:17001 is not configured as a cluster node. 
```

需添加密码：
```bash
./redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 --cluster-replicas 1 -a xrh123456
```

此时依旧报错，内容如下：
```bash
[root@VM-0-13-centos redis-cluster]# redis-cli --cluster create 0.0.0.0:7000 0.0.0.0:7001 0.0.0.0:7002 --cluster-replicas 1 -a xrh123456
Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.
*** ERROR: Invalid configuration for cluster creation.
*** Redis Cluster requires at least 3 master nodes.
*** This is not possible with 3 nodes and 1 replicas per node.
*** At least 6 nodes are required.

# 报错内容翻译如下
***错误：创建群集的配置无效。
***Redis群集需要至少3个主节点。
***如果每个节点有3个节点和1个副本，这是不可能的。
***至少需要6个节点。
```

#### 5.2 补充：为什么redis主从集群最少需要6个节点？
首先我们既然要搭建集群，那么`master`节点 **至少** 要`3`个，`slave`节点也是 **至少** `3`个，为什么呢？  
**这是因为一个`redis`集群如果要对外提供可用的服务，那么集群中必须要有过半的`master`节点正常工作。**

基于这个特性，如果想搭建一个能够允许 `n` 个`master`节点挂掉的集群，那么就要搭建`2n+1`个`master`节点的集群。

如：
- `2`个`master`节点，挂掉`1`个，则`1`不过半，则集群`down`掉，无法使用，容错率为`0`
- `3`个`master`节点，挂掉`1`个，`2>1`，还可以正常运行，容错率为`1`
- `4`个`master`节点，挂掉`1`个，`3>1`，还可以正常运行，但是当挂掉`2`个时，`2=2`，不过半，容错率依然为`1`

如果创建集群时设置`slave`为`1`个（即命令：`--cluster-replicas 1`）  
当总节点少于`6`个时会有上述报错。所以集群搭建至少需要`6`个节点

#### 5.3 新增节点，继续创建
重复之前的步骤  再添加3个节点，并补充修改批量启动和批量停止命令。

重新执行创建集群的命令：
```bash
./redis-cli --cluster create 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 -a xrh123456 --cluster-replicas 1
```

执行命令后，可以看到在创建集群，中间需要输入 `yes` 命令。  
创建完成的截图如下：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装Redis/创建集群图片.png)
</center>

#### 5.4 登录集群并查看相关信息

登录集群，`-c`表示以集群模式登录
```bash
./redis-cli -c -h 127.0.0.1 -p 7001
```

`cluster nodes` 查看节点信息
```bash
127.0.0.1:7001> cluster nodes
NOAUTH Authentication required.
```

出现：`NOAUTH Authentication required.`，没有权限，连接时没有加上密码。  
`exit` 退出之后，重新连接并查看集群节点信息
```bash
./redis-cli -c -h 127.0.0.1 -p 7001 -a xrh123456
```
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装Redis/集群节点信息.png)
</center>

Redis集群搭建完成！
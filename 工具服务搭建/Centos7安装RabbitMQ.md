# Centos7安装RabbitMQ

[toc]

[rabbitmq官网](https://www.rabbitmq.com/)  
[RabbitMQ官方插件地址](http://www.rabbitmq.com/community-plugins.html)

## 一、 安装部署
### 1. 安装包准备

|          | 文件名及版本号                           | 下载地址                                                     | 笔记安装包下载地址 |
| -------- | --------------------------------------- | ------------------------------------------------------------ | ------------------ |
| Erlang   | esl-erlang_23.3.1-1_centos_7_amd64.rpm  | https://packages.erlang-solutions.com/erlang/rpm/centos/8/x86_64/esl-erlang_23.3.1-1\~centos\~8_amd64.rpm | [gitee仓库：esl-erlang_23.3.1-1_centos_7_amd64.rpm](https://cdn.jsdelivr.net/gh/XieRuhua/images/安装包/mq/rabbitmq/esl-erlang_23.3.1-1_centos_7_amd64.rpm)                   |
| RabbitMQ | rabbitmq-server-3.9.13-1.el8.noarch.rpm | https://github.com/rabbitmq/rabbitmq-server/releases/download/v3.9.13/rabbitmq-server-3.9.13-1.el8.noarch.rpm | [gitee仓库：rabbitmq-server-3.9.13-1.el8.noarch.rpm](https://cdn.jsdelivr.net/gh/XieRuhua/images/安装包/mq/rabbitmq/rabbitmq-server-3.9.13-1.el8.noarch.rpm)                   |

**<font color="red">注意：RabbitMQ和Erlang的版本一定要对应，否则会出现安装失败的情况</font>**

Erlang和Rabbit版本对比官网说明：[RabbitMQ Erlang Version Requirements — RabbitMQ](https://www.rabbitmq.com/which-erlang.html)
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装RabbitMQ/Erlang和Rabbit版本对比.png)
</center>

### 2. 安装Erlang

**<font color="red">注意：从官网下载erlang，建议不要用yum安装，默认yum仓库中的版本较低，通过yum安装的时候会从仓库获取，但是版本太低</font>**

RabbitMQ是用Erlang语言编写的，在本教程中我们将安装最新版本的Erlang到服务器中。

将安装包上传到linux之后，执行：
```
rpm -ivh esl-erlang_23.3.1-1_centos_7_amd64.rpm
```
### 3. 安装RabbitMQ
```
install -y rabbitmq-server-3.9.13-1.el8.noarch.rpm
```

### 4. 修改配置文件
将`/usr/share/doc/rabbitmq-server-3.9.13/rabbitmq.config.example` 复制到安装路径下 `/usr/lib/rabbitmq/rabbitmq.config`

**<font color="red">注意：需改名为 rabbitmq.config</font>**
完整命令如下：
```
cp /usr/share/doc/rabbitmq-server-3.9.13/rabbitmq.config.example /usr/lib/rabbitmq/rabbitmq.config
```

如果`/usr/share/doc/rabbitmq-server-3.9.13/rabbitmq.config.example`不存在，则在`/usr/lib/rabbitmq/`下新建一个`rabbitmq.config`，内容如下（注意最后有个 **`.`** ）：
```
[
 {rabbit,
  [%%
  %% Network Connectivity
  %% ====================
  %%
  %% By default, RabbitMQ will listen on all interfaces, using
  %% the standard (reserved) AMQP port.
  %%
  {tcp_listeners, [5672]},
  {loopback_users, []}
  ]}
].
```

如果文件存在。  
去掉对应的地方的注释和后面的逗号，修改后的配置文件如下：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装RabbitMQ/rabbitmq配置文件.png)
</center>

### 5. 启动RabbitMQ Web管理控制台
安装`RabbitMQ Web`管理控制台控制台插件：
```
rabbitmq-plugins enable rabbitmq_management
```

通过运行以下命令，将RabbitMQ文件的所有权提供给RabbitMQ用户：
```
chown -R rabbitmq:rabbitmq /var/lib/rabbitmq/
```

现在，将需要为RabbitMQ Web管理控制台创建管理用户。 运行以下命令（如忘记密码，也可以这样重新设置）：
```
rabbitmqctl add_user admin password
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin “.*” “.*” “.*”
```
- **admin：** 为新管理员账号，可以自行命名
- **password：** 为密码，可以自行设置

### 6. 服务的启动与停止
```shell
# 启动rabbitmq服务
systemctl start rabbitmq-server
# 或者
service rabbitmq-server start 

# 重启服务
systemctl restart rabbitmq-server
# 或者
service rabbitmq-server restart

# 停止服务
systemctl stop rabbitmq-server
# 或者
service rabbitmq-server stop 

# 查看启动状态
systemctl status rabbitmq-server
```
查看运行状态：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装RabbitMQ/rabbitmq运行状态.png)
</center>

**访问：** http://IP:15672  输入设置好的账号密码。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装RabbitMQ/rabbitmq主界面.png)
</center>

**安装成功。**

### 7. 卸载
```
/sbin/service rabbitmq-server stop
yum list | grep rabbitmq
yum -y remove rabbitmq-server.noarch
  
yum list | grep erlang
yum -y remove erlang-*
yum remove erlang.x86_64
rm -rf /usr/lib64/erlang
rm -rf /var/lib/rabbitmq
```

## 二、插件安装和异常处理
### 1. 插件安装
[RabbitMQ官方插件地址](http://www.rabbitmq.com/community-plugins.html)

RabbitMQ的有些插件没有集成在初始的安装中，它们需要额外安装，这些文件的后缀为.ez，安装时需要将.ez文件拷贝到安装的插件目录。以下是不同系统中默认安装的插件目录路径：

| 系统          | 插件目录                                                                           | 
| ------------- | --------------------------------------------------------------------------------- | 
| Linux         | `/usr/lib/rabbitmq/lib/rabbitmq_server-version/plugins`(version表示你安装的版本号)  |
| Windows       | `C:\Program Files\RabbitMQ\rabbitmq_server-version\plugins`(安装rabbitmq的目录)    |
| Homebrew      | `/usr/local/Cellar/rabbitmq/version/plugins`                                      |
| Generic Unix  | `rabbitmq_server-version/plugins` (安装rabbitmq的目录)                             |

将插件文件（`.ez`文件）拷贝到插件目录后可以通过命令`sudo rabbitmq-plugins enable plugin-name`启用插件。  
如安装 **死信队列** 的插件（[笔记安装包下载地址：rabbitmq_delayed_message_exchange-3.9.0.ez](https://cdn.jsdelivr.net/gh/XieRuhua/images/安装包/mq/rabbitmq/rabbitmq_delayed_message_exchange-3.9.0.ez)），将插件拷贝到指定目录之后执行`sudo rabbitmq-plugins enable rabbitmq_delayed_message_exchange`即可启用

插件安装完成后可以通过命令`sudo rabbitmq-plugins list`查看已有插件列表：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装RabbitMQ/rabbitmq插件目录.png)
</center>

至此插件安装完成。

官方链接可以找到官方提供的一些插件：[RabbitMQ官方插件地址](http://www.rabbitmq.com/community-plugins.html)

### 2. 异常情况
#### 2.1 情况1
web页面提示  **<font color="red">undefined: There is no template at js/tmpl/layout.ejs undefined</font>**
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/Centos7安装RabbitMQ/rabbitmq异常1.png)
</center>

**处理方式：**
- 当前网络不佳，切换网络环境
- 重启服务
    ```shell
    # 重启服务
    systemctl restart rabbitmq-server
    ```

#### 2.2 情况2
使用上面设置好的账户密码登录。  
web页面提示  **<font color="red">您与此网站不是私密链接</font>** 。

**处理方式：**
- 查看用户列表，是否存在登录用户
  ```bash
  [root@VM-0-13-centos rabbitmq]# rabbitmqctl list_users
  Listing users ...
  user    tags
  guest   [administrator]
  ```
  可以看到刚刚设置的admin账户没有成功。重新执行创建用户的命令并加上权限：
  ```bash
  rabbitmqctl add_user admin password
  rabbitmqctl set_user_tags admin administrator
  rabbitmqctl set_permissions -p / admin “.*” “.*” “.*”
  ```
- 再次查看用户列表
  ```bash
  [root@VM-0-13-centos rabbitmq]# rabbitmqctl list_users
  Listing users ...
  user    tags
  guest   [administrator]
  admin   [administrator]
  ```
- 其他情况：登录用户已存在且权限正常，可能是密码错误，尝试修改密码再登录。
  ```bash
  rabbitmqctl change_password admin password
  ```

  
# GitLab搭建

## 前置条件

Linux服务器
GitLab需要4G内存
gitlab-ce-12.9.0版本

## 安装步骤

需要的依赖准备：

> yum install -y curl postfix policycoreutils-python openssh-server wget

[选择一个目录] cd /home
下载，此处选择清华镜像[时间较长]

> wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el7/gitlab-ce-12.9.0-ce.0.el7.x86_64.rpm

安装[时间较长]

> rpm -i gitlab-ce-12.9.0-ce.0.el7.x86_64.rpm

配置端口、邮件等：

> vim /etc/gitlab/gitlab.rb

修改以下配置：
http 访问地址
![null](http://192.168.1.211:8888/uploads/blog/202005/attach_160ca98e00453314.png)

邮件通知，此处配置 qq 邮箱
![null](http://192.168.1.211:8888/uploads/blog/202005/attach_160ca990c1d87728.png)

代理的端口，默认 8080 会存在冲突
![null](http://192.168.1.211:8888/uploads/blog/202005/attach_160ca99409886044.png)

刷新配置：

> gitlab-ctl reconfigure

### 启动 GitLab

启动命令

> gitlab-ctl start

停止命令

> gitlab-ctl stop

重启命令

> gitlab-ctl restart

### 初始管理员密码

[新版本首次访问可以设置密码]
也可以依次执行以下命令：

> sudo gitlab-rails console production
> u=User.where(id:1).first
> u.password=’1234567890’
> u.password_confirmation=’1234567890’
> u.save!
> exit

注意：
1.root账号首次登录会要求修改密码
2.如果提示无权限，请使用 sudo
3.每次修改配置后，先执行 gitlab-ctl reconfigure 再执行 gitlab-ctl restart

访问地址：
[http://192.168.1.110:18899](http://192.168.1.110:18899/)
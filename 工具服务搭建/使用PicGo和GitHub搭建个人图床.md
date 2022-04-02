# 使用PicGo和GitHub搭建个人图床

[PicGo GitHub地址](https://github.com/Molunerfinn/PicGo)

[toc]

> 该笔记是因为2022/3/25 起，gitee图床无法正常使用，故将图床移植到github上。
## 一、图床简述
.......简述见笔记《使用PicGo和Gitee搭建个人图床》

## 二、个人图床搭建
### 1.准备工作
#### 1.1  github图床仓库创建
> `github`注册过程省略...  
> `github`仓库创建过程省略...

**注意：创建完成之后，仓库一定要选择开源，否则生成的图片外链别人会没有访问权限。（当然github免费版没有私有仓库）**

#### 1.2 PicGo安装
[PicGo GitHub下载地址](https://github.com/Molunerfinn/PicGo)

### 2. 配置
#### 生成GitHub私人令牌（token）步骤
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/工具服务搭建/使用PicGo和GitHub搭建个人图床/github设置1.png)  ![](https://xieruhua.gitee.io/images/JavaLearning/工具服务搭建/使用PicGo和GitHub搭建个人图床/github设置2.png)

![](https://xieruhua.gitee.io/images/JavaLearning/工具服务搭建/使用PicGo和GitHub搭建个人图床/github创建token-1.png)

![](https://xieruhua.gitee.io/images/JavaLearning/工具服务搭建/使用PicGo和GitHub搭建个人图床/github创建token-2.png)
</center>

说明：
- note：token备注名
- Expiration：token有效时间，根据自己的需求设置
- Select scopes：授权给token的权限，根据自己的需求设置
设置完成之后点击 **Generate token** 生成token。
**注意：如果令牌忘记则需要重新生成**

#### PicGo配置
接下来点击 **“GitHub图床”** 开始配置：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/工具服务搭建/使用PicGo和GitHub搭建个人图床/PicGo的GitHub设置.png)
</center>

**填写说明：**
- **设定仓库名:** 仓库名称，填写你在创建图床时的仓库名字，这里注意带上你的用户名，比如我的是`xieruhua/images`；
- **设定分支名：** 仓库分支，默认`master`；
- **设定Token:** 这个比较重要，就是上面创建仓库后创建的私人令牌明文，直接粘贴上去就行， **如果忘记了那么只能删除重新再创建填写了；**
- **指定存储路径:** 填写仓库下面某个文件夹名字，也就是你存放图片的位置，如果不填就是仓库根目录下；
- **设定值定义域名：** 这个比较重要，设置的就是图片上传成功之后，自动复制到剪切板中的markdown图片访问前缀，  
  这里使用的github图床，则自定义域名为 https://raw.githubusercontent.com/XieRuhua/images/master （即https://raw.githubusercontent.com/用户名/仓库名/分支名 ）。

确定之后，直接在 **“上传区”** 上传图片即可。
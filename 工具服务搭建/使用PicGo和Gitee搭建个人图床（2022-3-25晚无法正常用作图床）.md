# 使用PicGo和Gitee搭建个人图床

[PicGo GitHub地址](https://github.com/Molunerfinn/PicGo)

[toc]

## 一、图床简述
### 什么是图床？
图床一般是指储存图片的服务器。简单说就是一个存放图片的网盘，

### 为什么需要图床？
一般编辑笔记的方式用的是`Markdown`格式。

`Markdown`是一种易于上手的轻量级标记语言，由于其目的在于注重文字内容而不是排版，目前很受大家欢迎，写完一篇文档可以直接复制到其他各大平台上，不用担心格式字体等混乱问题

但是文章中如果引用了某个地址的图片，那么当在其他平台上展示时可能有些不支持，导致图片无法显示；有时所引用的目标地址失效，也无法展示。当然，可以将图片转为`base64`的格式再引用，不过这样的方式在遇到较大的图片时会导致`base64`串过长，`md`文件渲染耗时等。

**要解决这个问题就需要一个图床了**

### 为什么需要个人图床？
常用的图片存储服务器有如下这些
- 七牛云
- 又拍云
- 腾讯云
- 阿里云
- 聚合图床
- `ImageURL`
- 知乎
- 路过图床
- ……

但是上述的图片存储服务区要么收费，要么要做各种认证，或者上传有限制等等。

而本片笔记介绍的`gitee`也有限制，但是不会太影响个人使用
<center> 

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/Gitee社区版空间配额说明.png)
</center>

个人免费可以使用的仓库总容量为 `5G`，我们可以大概计算一下，假设每张图片大小为`100KB`，那么`5G` 空间可以存储多少图片呢
```text
1G = 1024MB
1MB = 1024KB
5 * 1024 * 1024 / 100 = 52,428.8
```

可以存储`5万`多张`100k`左右的图片，所以我们完全不用担心容量限制问题了，大不了容量满了之后再新创建一个小号继续存储图片。

## 二、个人图床搭建
### 1.准备工作
#### 1.1  gitee图床仓库创建

> `gitee`注册过程省略...

**新建仓库**
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/创建图床仓库.png)
</center>

**注意：创建完成之后，仓库一定要选择开源，否则生成的图片外链别人会没有访问权限。**

#### 1.2 PicGo安装
[PicGo GitHub下载地址](https://github.com/Molunerfinn/PicGo)

### 2. 配置
#### Gitee私人令牌
打开`Gitee`设置，找到私人令牌，并新建：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/Gitee私人令牌.png)
</center>

**注意：图床需要的只是上传，放开这两个功能就够了**

复制刚刚创建的私人令牌。  
**注意：如果令牌忘记则需要重新生成**

#### PicGo配置
`PicGo`安装完成后打开主界面进行`Gitee`的插件配置：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/PicGo插件配置.png)
</center>

然后在 **“图床设置”** 中可以看到Gitee选项，如果没有就重启一下`PicGo`：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/PicGo设置1.png)
</center>

可以在 **“PicGo设置”** 中关掉不需要的图床入口：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/PicGo设置.png)
</center>

接下来点击 **“gitee”** 开始配置：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/PicGo的Gitee设置.png)
</center>

**填写说明：**
- **repo:** 仓库名称，填写你在创建图床时的仓库名字，这里注意带上你的用户名，比如我的是`xieruhua/myimagesbed`；
- **branch：** 仓库分支，默认`master`；
- **token:** 这个比较重要，就是上面创建仓库后创建的私人令牌明文，直接粘贴上去就行， **如果忘记了那么只能删除重新再创建填写了；**
- **path:** 填写仓库下面某个文件夹名字，也就是你存放图片的位置，如果不填就是仓库根目录下；
- **customPath：** 自定义路径规则；
- **customUrl：** 自定义上传成功的返回地址。

确定之后，直接在 **“上传区”** 上传图片即可。

### 3. 异常
如果出现`404`，请检查一下 **repo仓库名** 是否写错了。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/工具服务搭建/使用PicGo和Gitee搭建个人图床/404.png)
</center>












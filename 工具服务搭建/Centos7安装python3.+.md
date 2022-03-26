# 一、安装过程
## 1. 安装编译相关工具
```sh
yum -y groupinstall "Development tools"
yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel
yum install libffi-devel -y
```
## 2. 下载python安装包
```sh
wget https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz
tar -zxvf  Python-3.8.3.tg
```
也可以去`python`官网选择想要的版本[python官网下载](https://www.python.org/downloads/)

## 3. 编译安装python
```sh
mkdir /usr/local/python3 #创建编译安装目录
cd Python-3.8.3
./configure --prefix=/usr/local/python3
make && make install
```
安装过程结束后，出现下面两行就成功了
```sh
.................
Installing collected packages: setuptools, pip
Successfully installed pip-19.2.3 setuptools-41.2.0
.................
```
# 4. 创建软链接
```sh
# 查看当前python软链接
ll /usr/bin/ |grep python
lrwxrwxrwx    1 root root           7 		Nov 26  2018 python -> python2
lrwxrwxrwx    1 root root           9 		Nov 26  2018 python2 -> python2.7
-rwxr-xr-x    1 root root        	7216 	Jul 13  2018 python2.7
```
默认系统安装的是`python2.7`，删除原`python`软链接
```sh
rm -rf /usr/bin/python
```
配置软链接为`python3`
```sh
#添加python3的软链接 
ln -s /usr/local/python3/bin/python3 /usr/bin/python
```
这个时候看下`python`默认版本
```sh
[root@root ~]# python
Python 3.8.3 (main, Nov 30 2021, 17:05:02) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```
## 5. 删除默认pip软链接，并添加pip3新的软链接
```sh
#删除默认pip软链接
rm -rf /usr/bin/pip
#添加 pip3 的软链接 
ln -s /usr/local/python3/bin/pip3 /usr/bin/pip
```
## 6. 更改yum配置
因为其要用到`python2`才能执行，否则会导致`yum`不能正常使用（不管安装 `python3`的哪个版本，都必须要做的）
```sh
vi /usr/bin/yum 
把 #! /usr/bin/python 修改为 #! /usr/bin/python2 

vi /usr/libexec/urlgrabber-ext-down 
把 #! /usr/bin/python 修改为 #! /usr/bin/python2

vi /usr/bin/yum-config-manager
#!/usr/bin/python 改为 #!/usr/bin/python
```

# 二、使用补充

## pip 安装第三方库
`python`第三方库搜索地址：https://pypi.org/project/
```sh
# 安装bs4(beautifulsoup4) 
pip install bs4
```
安装完成之后，测试是否可以使用
```sh
[root@root ~]# python
Python 3.8.3 (main, Nov 30 2021, 17:05:02) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from bs4 import beautifulsoup
>>>
```

## `2to3`（第三方库版本转换）
当测试`bs4`（或其他第三方库）是否安装成功（`import bs4`）时提示：
```text
············
'You are trying to run the Python 2 version of Beautiful Soup under Python 3. This will not work.'<>'You need to convert the code, either by installing it (`python setup.py install`) or by running 2to3 (`2to3 -w bs4`).'
```

**解决方式：将`beautifulsoup`文件夹下的`bs4`转换成`python3`的版本即可**  
如果将`python3`添加到了环境变量中则可以直接使用命令,如果没有则需要定位到`python3`安装目录下的`lib`目录
```sh
[root@root ~]# cd /usr/local/python3/lib
# 如果lib下没有beautifulsoup4，则需要手动下载解压，下载下载地址https://pypi.org/project/beautifulsoup4/#files
# 解压完成之后执行版本转换
[root@root lib]# 2to3 ./beautifulsoup/bs4 -w
```
测试是否可以使用
```sh
[root@root ~]# python
Python 3.8.3 (main, Nov 30 2021, 17:05:02) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-44)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from bs4 import beautifulsoup
>>>
```
打印如上语句即为可用。
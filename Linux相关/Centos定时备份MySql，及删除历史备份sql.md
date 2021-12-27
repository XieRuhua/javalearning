说明：利用系统crontab来定时执行定时脚本，按日期对备份结果进行保存，达到备份的目的。
**<font color="red">注：crontab中的脚本或者执行命令涉及的路径一定要是绝对路径，而不是相对路径</font>**

#### 一、定时备份数据库
1、创建保存备份文件的路径/mysqlData
```
mkdir /mysqlData
```

2、创建一个备份文件的shell脚本
```
vim /mysqlData/script/mysql_dump.sh
```
进入编辑，写入以下内容：
```shell
DATABASE=youDataBaseName             #备份数据库名称
DB_USERNAME=root                     #数据库账号
DB_PASSWORD=password                 #数据库密码
BACKUP_PATH=/mysqlData               #备份数据目录

#备份命令

mysqldump -u$DB_USERNAME -p$DB_PASSWORD $DATABASE > ${BACKUP_PATH}\/${DATABASE}_$(date '+%Y%m%d_%H%M').sql
```
保存。

3、修改文件属性，避免权限不足的情况。
```
chmod 777 /mysqlData/script/mysql_dump.sh
```

4、修改定时任务文件
```
vim /etc/crontab
```
在最下面添加以下内容：
```
# 每天0点同步mysql中的指定数据库
0 0 * * * root /mysqlData/script/mysql_dump.sh
```

完成。每天都会在目录/mysqlData下备份指定数据库；  
如需全量备份，修改备份的shell脚本即可。

#### 二、定时删除历史备份文件
1、创建一个删除历史文件的shell脚本
```
vim /mysqlData/script/mysql_delete.sh
```
进入编辑，写入以下内容：
```shell
##　查找并删除15天前 /xrh/mysqlBackups 以.sql为结尾的文件
rm -rf $(find /xrh/mysqlBackups/ -mtime +15 -name "*.sql")
```
2、修改文件属性，避免权限不足的情况。
```
chmod 777 /mysqlData/script/mysql_delete.sh
```

3、修改定时任务文件
```
vim /etc/crontab
```
在最下面添加以下内容：
```
# 每天2点同步mysql中的指定数据库
0 2 * * * root /mysqlData/script/mysql_delete.sh
```



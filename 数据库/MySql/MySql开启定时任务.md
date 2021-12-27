# MySql开启定时任务

*****

MySQL5.1.x版本中引入了一项新特性EVENT，顾名思义就是事件、定时任务机制，在指定的时间单元内执行特定的任务，因此今后一些对数据定时性操作不再依赖外部程序，而直接使用数据库本身提供的功能。

## 1、查看事件调度器是否打开

要查看当前是否已开启事件调度器，可执行如下SQL：

```sql
SHOW VARIABLES LIKE 'event_scheduler';
-- 或
SELECT @@event_scheduler;
```
一般是关闭状态，查询到的内容如下：
+----------------------+-------+  
| Variable_name   | Value |  
+----------------------+-------+  
| event_scheduler | OFF  |  
+----------------------+-------+  
则需要手动打开，执行语句如下

```sql
SET GLOBAL event_scheduler = 1;
-- 或
SET GLOBAL event_scheduler = ON;
```

但是这种修改值的方式只是本次启动有效，当机器或者mysql重启的时候，又会回到关闭状态，此时我，我们需要直接修改配置文件my.ini 或者 my.cnf 。在配置文件最后添加：event_scheduler=ON

## 2、创建存储过程

```sql
CREATE PROCEDURE `test_proceduce`()
BEGIN
	--向测试表test_table（id,create_time）插入一条数据
	INSERT INT test_table(create_time) VALUES(NOW());
END
```

测试存储过程，可以看到正常打印了内容：

```sql
call test_proceduce();
```

## 3、创建事件任务

```sql
create event if not exists event_test
on schedule every 30 second
on completion preserve
do call test_proceduce();
```

每隔30秒将执行存储过程test_proceduce()，向测试表test_table中插入一条当前时间的数据。

上述sql执行成功之后就可以看到test_table表中每30秒新增一条数据。

**查看事件任务状态**

```sql
select * from mysql.event;
```

上面的语句可以看到所有定时任务的状态，操作数据库等信息；

**关闭事件任务**

```sql
alter event event_test ON
COMPLETION PRESERVE DISABLE;
```

**开启事件任务**

```sql
alter event e_test ON
COMPLETION PRESERVE ENABLE;
```


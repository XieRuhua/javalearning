# MySql删除大量数据的优化方案（InnoDB）
***
官方详解方案：https://dev.mysql.com/doc/refman/8.0/en/delete.html


**注：常用且默认的引擎为InnoDB。MyISAM与InnoDB的区别参见其他笔记**

[toc]
## 一、Mysql删除数据原理及大量删除的业务场景
### 1. 删除原理
**在InndoDB存储引擎中，删除一条记录，首先锁住这条记录，数据原有的被废弃，记录头发生变化，主要是打上了删除标记。** 也就是原有的数据 **deleted_flag 变成 1**，代表数据被删除。但是数据没有被清空（**表文件大小并不会改变**），在新一行数据大小小于这一行的时候，可能会占用这一行。这样其实就是**存储碎片**。

之后，相关数据的**索引**需要更新，清除这些数据。并且，会产生对应的 **binlog 与 redolog 日志**。


### 2. 大量删除数据的弊端

* **大量数据块碎片，浪费空间：**  
数据只是被打上了删除标记，实际并没有被清空，这就是**存储碎片**；  
且产生了大量日志，可以看到被删除大量数据的表的占用空间大大增高。
* **索引维护的代价：**  
每次删除记录，数据库都要相应地更新索引，查询MySQL官方手册得知删除数据的速度和创建的索引数量是成正比的
* **事务造成主从延迟：**  
由于产生了大量 binlog 导致主从同步压力变大
* **没有合适索引或删除数据量大，持锁范围大或时间长：**   
由于修改大量的索引，可能造成部分索引失效，且产生大量的日志，导致这个更新会有很长时间，锁表锁很长时间，期间这个表无法处理线上业务。  
* **占用IO资源：**  
由于标记删除产生了大量的存储碎片，且MySQL 是按页加载数据，这些存储碎片不仅大量增加了随机读取的次数，并且让页命中率降低，导致页交换增多。

## 二、优化方案
### 1. 方案1
#### 原理解释及说明
在 delete 后加上 limit 限制控制其数量，这个数量让他会走索引，从而不会锁整个表。
```sql
DELETE FROM table_name
    [where_condition]
    [ORDER BY ...]
    [LIMIT row_count]
```
但是**存储碎片**、**主从同步日志**、**占用空间**的问题并没有解决。  
于是可以在删除完成后，通过如下语句，重建表：
```sql
alter table table_name engine=InnoDB, ALGORITHM=INPLACE, LOCK=NONE;

-- “ALGORITHM=INPLACE, LOCK=NONE” 语句解释
线上无锁添加索引：加索引的语句不加锁
ALTER TABLE tbl_name ADD PRIMARY KEY (column), ALGORITHM=INPLACE, LOCK=NONE;
ALGORITHM=INPLACE
更优秀的解决方案，在当前表加索引，步骤：
1.创建索引(二级索引)数据字典
2.加共享表锁，禁止DML，允许查询
3.读取聚簇索引，构造新的索引项，排序并插
入新索引
4.等待打开当前表的所有只读事务提交
5.创建索引结束
 
ALGORITHM=COPY
通过临时表创建索引，需要多一倍存储，还有更多的IO，步骤：
1.新建带索引（主键索引）的临时表
2.锁原表，禁止DML，允许查询
3.将原表数据拷贝到临时表
4.禁止读写,进行rename，升级字典锁
5.完成创建索引操作
 
LOCK=DEFAULT：默认方式，MySQL自行判断使用哪种LOCK模式，尽量不锁表
LOCK=NONE：无锁：允许Online DDL期间进行并发读写操作。如果Online DDL操
作不支持对表的继续写入，则DDL操作失败，对表修改无效
LOCK=SHARED：共享锁：Online DDL操作期间堵塞写入，不影响读取
LOCK=EXCLUSIVE：排它锁：Online DDL操作期间不允许对锁表进行任何操作
```

注意这句话其实就是重建你的表，**“engine=InnoDB” 指定引擎是 innodb（默认，可不写）， “ALGORITHM=INPLACE, LOCK=NONE”标识可以不用锁表就重建表。**

#### 业务场景
在实际操作过程中，如果不在乎删除消耗时间，可以利用limit分批次删除：

假设有一个表有1000万条记录（**建议单表行数不要超过500W行或者单表容量超过 2GB**），delete_id=1的所有记录，假设有600万条， 直接执行 DELETE FROM table_name WHERE delete_id=1 会发现删除失败，因为lock wait timeout exceed（锁定等待超时超过）的错误。

因为这条语句所涉及的记录数太多，因此我们通过LIMIT参数分批删除，比如每10000条进行一次删除，那么我们可以利用MySQL这样的语句来完成：
```sql
DELETE FROM table_name WHERE delete_id=1 LIMIT 10000;
```
然后使用定时任务分多次执行就可以把这些记录成功删除。

注意：
* 执行大批量删除的时候注意要使用上limit。因为如果不用limit，删除大量数据很有可能造成**死锁**。
* 如果delete的where语句不在索引上，可以先找主键，然后根据主键删除数据库。
* 平时update和delete的时候最好也加上 **limit 1** 来防止误操作。

### 2. 方案2 -- 官网例子
如果要从大表中删除许多行，则可能会超出表的锁定表大小InnoDB。为避免此问题，或只是为了最小化表保持锁定的时间，以下策略（根本不使用 DELETE）可能会有所帮助：
````sql
-- 1、选择不要删除的行与原始表具有相同结构的空表 ：
INSERT INTO t_copy SELECT * FROM t_old WHERE … ;

-- 2、用RENAME TABLE以原子方式将原始表移开，并将副本重命名为原始名称： 
RENAME TABLE t TO t_old, t_copy TO t;

--3、删掉原始表：
DROP TABLE t_old;



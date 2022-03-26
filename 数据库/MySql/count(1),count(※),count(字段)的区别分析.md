# select count(1) ,count(*),count(字段)的区别分析

[官方：COUNT(expr)、COUNT(DISTINCT expr,[expr...])](https://dev.mysql.com/doc/refman/5.6/en/aggregate-functions.html#function_count)

[文档内容参考1：数据库 select count(1) ,count(\*),count(字段) 有什么区别？！](https://mp.weixin.qq.com/s/SebyGJnuolKpeCcxQY1pOw)   
[文档内容参考2：MySQL学习笔记：count(1)、count(\*)、count（字段）的区别](https://www.cnblogs.com/hider/p/11726690.html)  
[文档内容参考3：高性能MySQL-count(1) OR count(\*)？](https://zhuanlan.zhihu.com/p/28397595)  

[toc]

## 一、官方解释
[官方：COUNT(expr)](https://dev.mysql.com/doc/refman/5.6/en/aggregate-functions.html#function_count)

>### COUNT(expr)
>
>Returns a count of the number of non-NULL values of expr in the rows retrieved by a SELECT statement. The result is a BIGINT value.
>>返回SELECT语句检索到的行中expr的非空值数的计数。结果是一个BIGINT值。  
>
>If there are no matching rows, COUNT() returns 0.
>>如果没有匹配的行，COUNT（）返回0。
>```
>mysql> SELECT student.student_name,COUNT(*)
>       FROM student,course
>       WHERE student.student_id=course.student_id
>       GROUP BY student_name;
>```
>COUNT(*) is somewhat different in that it returns a count of the number of rows >retrieved, whether or not they contain NULL values.  
>>COUNT（*）有些不同，因为它返回检索到的行数的计数，无论它们是否包含空值。
>
>For transactional storage engines such as InnoDB, storing an exact row count is problematic. Multiple transactions may be occurring at the same time, each of which may affect the count.
>>对于事务性存储引擎（如InnoDB），存储精确的行数是有问题的。多个事务可能同时发生，每个事务都可能影响计数。
>
>InnoDB does not keep an internal count of rows in a table because concurrent transactions might “see” different numbers of rows at the same time. Consequently, SELECT COUNT(*) statements only count rows visible to the current transaction.
>>InnoDB不在表中保留行的内部计数，因为并发事务可能同时“看到”不同数量的行。因此，SELECT COUNT（*）语句只对当前事务可见的行进行计数。
>
>To process a SELECT COUNT(*) statement, InnoDB scans an index of the table, which takes some time if the index is not entirely in the buffer pool. For a faster count, create a counter table and let your application update it according to the inserts and deletes it does. However, this method may not scale well in situations where thousands of concurrent transactions are initiating updates to the same counter table. If an approximate row count is sufficient, use SHOW TABLE STATUS.
>>为了处理SELECT COUNT（*）语句，InnoDB扫描表的索引，如果索引不完全在缓冲池中，这需要一些时间。为了更快地计数，请创建一个计数器表，并让应用程序根据插入和删除操作来更新它。但是，在数千个并发事务正在启动对同一计数器表的更新的情况下，此方法可能无法很好地扩展。如果近似行数足够，请使用“显示表格状态”。
>
>__<font color="red">InnoDB handles SELECT COUNT(*) and SELECT COUNT(1) operations in the same way. There is no performance difference.__
>>__InnoDB以相同的方式处理SELECT COUNT(*)和SELECT COUNT（1）操作。没有性能差异。</font>__
>
>__<font color="red">For MyISAM tables, COUNT(*) is optimized to return very quickly if the SELECT retrieves from one table, no other columns are retrieved, and there is no WHERE clause. For example:__
>>__对于MyISAM表，如果SELECT从一个表中检索，没有检索到其他列，并且没有WHERE子句，则COUNT（*）会优化为非常快速地返回。</font>__ 例如：
>```
>mysql> SELECT COUNT(*) FROM student;
>```
>
>This optimization only applies to MyISAM tables, because an exact row count is stored for this storage engine and can be accessed very quickly. COUNT(1) is only subject to the same optimization if the first column is defined as NOT NULL.
>>此优化仅适用于MyISAM表，因为此存储引擎存储了精确的行数，并且可以非常快速地访问。只有在第一列定义为NOTNULL时，count（1）才会进行相同的优化。

>### COUNT(DISTINCT expr,[expr...])
>
>Returns a count of the number of rows with different non-NULL expr values.
>>返回具有不同非空expr值的行数的计数。
>
>If there are no matching rows, COUNT(DISTINCT) returns 0.
>>如果没有匹配的行，COUNT（DISTINCT）返回0。
>```
>mysql> SELECT COUNT(DISTINCT results) FROM student;
>```
>In MySQL, you can obtain the number of distinct expression combinations that do not contain NULL by giving a list of expressions. In standard SQL, you would have to do a concatenation of all expressions inside COUNT(DISTINCT ...).
>>在MySQL中，通过给出表达式列表，可以获得不包含NULL的不同表达式组合的数量。在标准SQL中，你必须对COUNT（DISTINCT…）中的所有表达式进行串联。

## 二、整理说明
### 1. 关于 COUNT(*) 和 COUNT(1)
>官方文档：  
>InnoDB handles SELECT COUNT(*) and SELECT COUNT(1) operations in the same way. There is no performance difference.
>><font color="red">InnoDB以相同的方式处理`SELECT COUNT(*)`和`SELECT COUNT(1)`操作。没有性能差异。</font>

所以，对于`count(1)`和`count(*)`，MySQL的优化是完全一样的，根本**不存在谁更快**！  
但依旧建议使用count(*)，因为这是`SQL92`定义的标准统计行数的语法。[维基百科：SQL-92](https://zh.wikipedia.org/wiki/SQL-92)

### 2. 关于COUNT(字段)
进行全表扫描，然后判断拿到的字段的值是不是为`NULL`，不为`NULL`则累加。

### 3. 性能说明
**相比`COUNT(*)`，`COUNT(字段)`多了一个步骤就是判断所查询的字段是否为`NULL`，所以他的性能要比`COUNT(*)`和`COUNT(1)`慢。**

MySql最常见的两种数据库表引擎`MyISAM`和`Innodb`有不同的优化。

#### MyISAM引擎
`MyISAM` 引擎会在执行 `COUNT(*)`的时候会直接返回一个表的总行数（`MyISAM`把表的总行数单独记录下来）：  
这是因为`MyISAM`对于表的行数做了优化，具体做法是有一个变量存储了表的行数，如果查询条件没有`WHERE`条件则是查询表中一共有多少条数据，`MyISAM`可以做到迅速返回，所以也解释了如果加`WHERE`条件，则该优化就不起作用了。  
**`MyISAM`是表级锁，不会有`并发`的行操作，所以查到的结果是准确的。**
 
#### InnoDB引擎
`InnoDB` 的表也有这么一个存储了表行数的变量（缓存），但是这个值是一个估计值，没有什么实际意义。  
因为`InnoDB`支持事务，增加了版本控制(`MVCC`)的原因，大部分操作都是行级锁，行可能被并行修改，因为，同时有多个事务访问数据并且有更新操作的时候，每个事务需要维护自己的可见性，那么每个事务查询到的行数也是不同的，所以不能缓存具体的行数**（缓存记录不准确）**。

**但是，InnoDB还是针对`COUNT(*)`语句做了些优化的：**  
通过低成本的索引进行扫表，而不关注表的具体内容。  
`InnoDB`执行`COUNT(*)`时会优先选择最小的非聚簇索引来扫表。
>`InnoDB`中索引分为 **聚簇索引（主键索引）** 和 **非聚簇索引（非主键索引、辅助索引、二级索引）**，聚簇索引的叶子节点中保存的是整行记录，而非聚簇索引的叶子节点中保存的是该行记录的主键（聚簇索引）的值。[笔记：MySql索引](https://xieruhua.gitee.io/javalearning/#/./%E6%95%B0%E6%8D%AE%E5%BA%93/MySql/MySql%E7%B4%A2%E5%BC%95)

**优化的前提同样是查询语句中不包含`where`条件和`group by`条件。**

## 三、总结
`COUNT(expr)`函数返回的值是由`SELECT`语句检索的行中`expr`表达式非`null`的计数值，一个`BIGINT`的值。  
如果没有匹配到数据，`COUNT(expr)`将返回`0`，通常有下面这三种用法：
1. **COUNT(字段) ：** 会统计该字段在表中出现的次数，忽略字段为`null` 的情况。即不统计字段为`null` 的记录。
2. __COUNT(*) ：__ 则不同，它执行时返回检索到的行数的计数，不管这些行是否包含`null`值，
3. __COUNT(1)跟COUNT(*)类似：__ 不将任何列是否`null`列入统计标准，仅用`1`代表代码行，所以在统计结果的时候，不会忽略列值为`NULL`的行。

所以执行以下数据会出现这样的结果（这边故意给`test_column`字段设置了几个`null`值）：
```sql
select count(1),count(*),count(test_column) from test_info;
```
<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/数据库/MySql/count(1),count(※),count(字段)的区别分析/count(1),count(※),count(字段)的结果对比.png)
</center>

**小结：**  
+ `count(*)`包括了所有的列，相当于行数，在统计结果的时候，**不会忽略列值为`NULL`**
+ `count(1)`包括了忽略所有列，用`1`代表代码行，在统计结果的时候，**不会忽略列值为`NULL`**
+ `count(字段)`只包括字段那一列，在统计结果的时候，__会忽略列值为`NULL`的计数（即某个字段值为`NULL`时，不统计）。__

**从效率层面说，`COUNT(*)` = `COUNT(1)` > `COUNT(字段)`，又因为 `COUNT(*)`是`SQL92`定义的标准统计数的语法，我们建议使用 `COUNT(*)`。**

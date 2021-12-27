# select count(1) ,count(*),count(字段) 

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
>><font color="red">InnoDB以相同的方式处理SELECT COUNT(*)和SELECT COUNT（1）操作。没有性能差异。</font>

所以，对于count(1)和count(\*)，MySQL的优化是完全一样的，根本不存在谁更快！
但依旧建议使用count(*)，因为这是SQL92定义的标准统计行数的语法。[维基百科：SQL-92](https://zh.wikipedia.org/wiki/SQL-92)

### 2. 关于COUNT(字段)
进行全表扫描，然后判断拿到的字段的值是不是为NULL，不为NULL则累加。

### 3. 性能说明
**相比COUNT(\*)，COUNT(字段)多了一个步骤就是判断所查询的字段是否为NULL，所以他的性能要比COUNT(\*)和COUNT(1)慢。**

MySql最常见的两种数据库表引擎MyISAM和Innodb有不同的优化。

#### MyISAM引擎  
MyISAM 引擎会在执行 COUNT(*)的时候会直接返回一个表的总行数（MyISAM把表的总行数单独记录下来）：  
这是因为MyISAM对于表的行数做了优化，具体做法是有一个变量存储了表的行数，如果查询条件没有WHERE条件则是查询表中一共有多少条数据，MyISAM可以做到迅速返回，所以也解释了如果加WHERE条件，则该优化就不起作用了。  
**MyISAM是表级锁，不会有并发的行操作，所以查到的结果是准确的。**
 
#### InnoDB引擎
InnoDB的表也有这么一个存储了表行数的变量（缓存），但是这个值是一个估计值，没有什么实际意义。  
因为InnoDB支持事务，增加了版本控制(MVCC)的原因，大部分操作都是行级锁，行可能被并行修改，因为，同时有多个事务访问数据并且有更新操作的时候，每个事务需要维护自己的可见性，那么每个事务查询到的行数也是不同的，所以不能缓存具体的行数（缓存记录不准确）。

**但是，InnoDB还是针对COUNT(\*)语句做了些优化的：**  
通过低成本的索引进行扫表，而不关注表的具体内容。  
InnoDB执行COUNT(*)时会优先选择最小的非聚簇索引来扫表。
>InnoDB中索引分为 **聚簇索引（主键索引）** 和 **非聚簇索引（非主键索引、辅助索引、二级索引）**，聚簇索引的叶子节点中保存的是整行记录，而非聚簇索引的叶子节点中保存的是该行记录的主键（聚簇索引）的值。

**优化的前提同样是查询语句中不包含where条件和group by条件。**

## 三、总结
COUNT(expr)函数返回的值是由SELECT语句检索的行中expr表达式非null的计数值，一个BIGINT的值。  
如果没有匹配到数据，COUNT(expr)将返回0，通常有下面这三种用法：
1. **COUNT(字段) ：** 会统计该字段在表中出现的次数，忽略字段为null 的情况。即不统计字段为null 的记录。
2. __COUNT(*) ：__ 则不同，它执行时返回检索到的行数的计数，不管这些行是否包含null值，
3. __COUNT(1)跟COUNT(*)类似：__ 不将任何列是否null列入统计标准，仅用1代表代码行，所以在统计结果的时候，不会忽略列值为NULL的行。

所以执行以下数据会出现这样的结果（这边是故意给test_column字段设置了几个null值）：
```sql
select count(1),count(*),count(test_column) from test_info;
```
<center>

![avatar](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAl0AAADLCAYAAABUIiZcAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAABkrSURBVHhe7d2/ixzJ3cfxTR//NQ6MsDa4QP+CA2dmwWjBsaPjQoMUOND6EgX+AyQjeMDJYjm65MCbKDBcIO1FxyXyk1zk54Rt2l2/uquq61fPVNd2zbxf8IWbnp6anu6aqs/UzK0ufvjhh+HTp09dFQAAQG8IXQAAAA0QugAAABogdAEAADRA6Krhm0/D/3zx/1P95E//1ndgU18/G548eTZ8rW+W+3p49uTJ8Gz9A09P8hyK85S6j3MoHdwPT5Q8H0/mevBOUr+v3n/1ozPm/+YbfQeq+e7V02r9Z2pL10N2yd2Fro93r4eXL18OL99+CN4var/+M/zhywah6x//Gj47xTf6d6+Gp6VvCL3v01ff6Q2u++9/O1z87RfDxf2d3uIyb8IHnw9qq3AOv35mtn03vHqqwoQ8X16jnMNRqh+uaedYLZ+rmOg/ewhd4vRU7Kvjh+yffPHj8Id/6Nt712k/NNcsNsYXkx8Cng7HNlPLfkLXx7vh9Ri2Xt99GO5eE7qSzj50qU+uwcH8n/87XI5h6/L7u+Hm7/HQJag39YmtUNQ4h+a+MXA9ezaWmDgjgxbnMBEqOp3s6tlP6BJq9dW//Gkc47/813Cvb+/emfdD8SHyydNXY2/ch52Erg/D25evh7uP4r8/Erpyzjx0xQfPu+H6b78dbv4p/vv7bOjKTpo9OvocWora4hxGd2s5AbV8rmL7Cl21+qoMXT39hOTM+6EMXTs6oB3+pqtx6PJ/j/XFp+Ev+q5J8W+2MqGrsB3xpp72sZax/d8R2BU87gKyQ4qBSNZyNUNNLNY+TucND6puJ1f7iCVipy3rk8fiOZzyJzU1cOaXnEtCl3nu4z79nt451JOTWOl6+nR4Ko4vcY44h65V7ZT8/snfx2pj3TGXOe5a2MLXJbbduV7iNYtrY167+G89oc+vK39NfWq/w86LkQxd4qtHuQr27+E31vjsf0D2x3KnPdOGni/kf+sP2mvG+W77YfZY1l13dxxYWhx7ZF+zX3zcLHPeoatkxUi8AZyOrt5M4TddInQVtaO3OUvXY5tfee1VWekyE6vdUcfO/GrucKqT2W8Y/ZipUxYMnmYf53GRCavkU5J8Q4a/6nKVha6i54w6zXMonlu1K55XHbt8HbFGOYdhuXZkG6nXNSo9t0ddA6PGtbCFr0tsu3O9zMQrjkW+NhH+x+d1XueKa2ocep50AAqVM15b+5nxWQQse+z3by/mgkXY+nH47Mtx/0PH/dxr3l0/NDL9xzlG77qb/hMqq3+v6c9q30TfKnTeoUsGodQPIlWI+uyr/+jbyvJNY8RCV1k78XY9FULXsrP5VOdb9D1nsikYPM0+zkDu76MVvGHzx20Uhi59fIe8kU7/HIrjL9mPcxiUbCd8zhbtOq8zocJkV+da2MLXJbbduRayTf1c+rWpc2Ufw4prOgmf9zVyK1124JJ0cFLzjApYi7HbnovsNvRYr+aOyGNzOuuHs0z/Kbzu8f6wtj/XceZfL6owJD9VBMOX6uTifr/Wha6ydop/K1AhdKUHplGs4zlvqvCbwm27ZB+t4A0rBwPvzRa2LnQlz0XE6Z/DUpzDoGQ7asB3PoFPZQcffdxye2IiKDjmnDrXwhbrFwXXwn4up/1A6Eq1sxA7pnLZrxdTH5xjH/TtMd3exxnrtwhd++uHsyP6jyXaH1b35zr4TZcUC19rO3k6dKXbiT024OjQVTDw7HmyS34aN7Ze6TqHc1iKcxiUbCfyKTtKH//4mG0milrXwhZrs+Ba2M/ltF8ndG250tVj6IqergV9zsfHbNMPbUf0H0u0P6zuz3UQuhx+8FkRhKTY/mXtyDdzo68XZUdMTRqxjic7qnlcqPP721a8QUo6e+yNsrD9b7pO/xwW4hyGJdsJH09e5HFHXAOjzrWwxV5jaLu3zT6/zvMeGboqnKejQlds7LYf1zR0xa5RTuRxFc7vLHZs6657tD+s7s91ELocqlPbv70Sv7MSK2BlHT0erora0W8w9/Fjm/4P6fVx5kJcku5wbmccO7P1o9nlIKwGPPtTovuJX78ZnHbXvEFU+8E3yGR5DGFloSu3YqHOQeT5Tv4cluEcxqTbUce8doKKPW/JMWdUuhaz8DkXstdro9CV66sljgpdo+WHa2/eqR269DlLn5Md9cNJrP+su+6p/rCmP6t9422V2k3o+vB2DFriL9Evyvz9rrlqMUHILv/H7kJoP/tNF7pf7uMtI+faUdQba7o/tBQt6DfjvF/BCtmCfoNMtfzkPnU0XcvOaA2Y+n75Jp465sqB0Qz8Uy0HyOUbZXZ7PwYt8ZfoF2X+fpct9qaemQEpPlCf3jlch3MYfk1app353FhlHU/o/uVr1wqOOe/4axF8TbLstjLXa5PQle+rJY4NXYJow4zdopx5p3roGnXUD/P9Z911j/cHJdefJ7JPin0OeV/NdrjSlS+cOz0xHDl4qjd37g2kn6vqD8/3gHN4vDrnEG2U9VUgxnxQIHThHOlPU9FPJTn2J+kE86nrJOdVzuHxjj2HaKOwrwJReqXr2Pc6oQv9km+CQz51qBWKZAiYlshPfKDmHB7v4HPYgl6Ny9RpL9YV9FVsrON+OI1jdY6P0AUAANAAoQsAAKABQhcAAEADhC4AAIAGCF0AAAANELoAAAAa2FXo8v8q/dsP4f0AAAB6s5vQJQOX/e8tfngbDV4AAAC92fHXi/F/+BoAAKA3hC4AAIAGdhy6PgxvX74cXt99XNwHAADQm92GLvWj+tfD3cflfQAAAL3ZZegy/xdjaJVLFAAAQG92F7o+3r1OBi5RAAAAvdlX6NJ/JiL043m7AAAAerOf0FUYuEQBAAD0ZiehS/95CBG6AuX/gVQAAIDe7PKH9LkCAADoDaELAACgAUIXAABAA4QuAACABghdAAAADRC6AAAAGiB0AQAANEDoAgAAaIDQBQAA0AChCwAAoAFCFwAAQAOELgAAgAYIXQAAAA0QugAAABogdAEAADRA6AIAAGiA0AUAANAAoQsAAKABQhcAAEADhC4AAIAGCF0AAAANELoAAAAaIHQBAAA0QOgCAABogNAFAADQAKELAACgAUIXAABAA4QuAACABghdAAAADRC6AAAAGiB0AQAANEDoAgAAaIDQBQAA0AChCwAAoAFCFwAAQAOELgAAgAYIXQAAAA0QugAAABogdAEAADRA6AIAAGiA0AUAANAAoQsAAKABQhcAAEADhC4AAIAGCF0AAAANELoAAAAaIHQBAAA0QOgCAABogNAFAADQAKELAACgAUIXAABAA4QuAACABghdAAAADRC6AAAAGiB0AQAANEDoAgAAaIDQBQAA0AChCwAAoAFCFwAAQAOELgAAgAYIXQAAAA0QugAAABogdAEAADRA6AIAAGhAhi6KoiiKoihq2yJ0URRFURRFNShCF0VRFEVRVIMidFEURVEURTUoGbpO1fv378+mAADAvp186DoHhC4AAPbPCV32ysmp1DkIvW5qXwUAwCJ0idunUucy2Z3idQtt77UIXQAAgdB1Aghd+y5CFwBAIHSdAELXvovQBQAQCF0ngNC17yJ0AQAEQtfo/uZyuLi8Ge71bdvt9cVweRO6R7gdri8uhouiuh733gaha99F6AIACA8Tut49Hx5dXA1vQvdVrLLJTgSny0Hlqvvh5jIUmLy6NvFJPNYPU6Xb4mQInJ4jj9C17yJ0AQCE1aHrzdXF8Oj5u+w2t94Nzx8Fwkuw6oWxkskuvZKVu7/yStf9zXBp9q8Zut5cjW0+Gp6/C9xnSuzz6Pnwztr27vmj4eLqjbufV3Ifecx1r1tou1/h43szXMljEX0u85qnEo8p3Xd9EboAAMLK0BWZnOTKVWrSUqHr6k3oPqsqr4BlJ7vb6zncyMBjVrxm+dBVZ6XL/opTPGftlS4RjJMBqiB0zQHLKu8xNapW6HpzpY63db/zi9AFABDWhS49Mb8JTb6hmibkfa50+V8lypwjgpi1bVl2MKu80qVVCV0ySPjHYJW8NiagjPuXhq5UcKtUqX4oj0EfZ/B4vADl7CNX/ALnIlPZ0JYpQhcAQFgRugpXq4K105UuSf2Oa0XGsdRb6bJVW+mSIcM9n25QCYcuuY8fPsbHBEPOBpXuh+KYVV8qCV350n3z6irzFfnhRegCAAjloUuvEpjgJL+usidlv5xVk32udAnia73DAlfMuoAVUvXrRT9MOdclvdLlfyUZDGN2eY8/tNKha34dcsX16nlR34oFfvs1iv8+7ENFughdAAChMHTNoemwSWmnK132D9dlia8OM18Z6t9dyd9ghe7PVOpH+0aN0JUNxfI3eInQZX89qbcvV5asx1esXOhSx/ZouBK/2fJXuuSHg5Ifxc992l7h8oNmjSJ0AQCEotClVhauhisrOOUndXsy3udKlwlObr4RoWv5g3pJ/N4r8ve8BPWnHq7lStf1GJwOXUHb4of04YqHrun6jgHEBJHdhC5dy+OZV+PiXxWavmiCmXgN3v4yuOX+j9zyInQBAISi0CX+L7Dn7wpXq4K105WuoENCl1odU6tY89eLIjyVrGz5Hjx06dWieSVJXL+r4fkYaNwg8nChy4QrP3SJgPhI/D7LXrWz7guvgonXsdyeD3BlRegCAAgH/5B+mvRiFZj07BKPr7WSEKuyyc79g6jXt2tClwpb7v+ZOIcuwaymrQlftUJXfDXSXuVZhi7xOHGd5TW2Qo0MNA8euvRK1Xhc/vGZrx2P+4BQvwhdAADhqNAVDU2Br6rkvs728MRoJnx726GVm+xU2PIDlglSkbL/llYwnLmhy5h+A1YQpmqGruU1sld1wqHL7OuGGnG9/NWg9qHLfk2hUDjdDryeabt3zM7jTMUef0ARugAAwvahy/7KcDGRjZO2uT3dJybyOsHrsMluzUpXSDh0benw0GVVIGQ4oSYYQtqHLrsWx5cNU6oPq3PinQfr9ZnHyfYrvD5CFwBA2Dh02ZPcuD3xmy1nghT7LSb49XUuk10qdC1W6mStDV3utZ9rJ6FLBq7Aa9IB3vQruf/0GiPhUz/G7udTvzywCF0AAKHxb7pUG8H9gxPgcUXoKvl6cb4G/r5OqAkGD/H4Bw5d2b7jBX+roqG0QuC3i9AFABCa/KbroercQ1evdYqvBwCAFaGrvyJ09Vn0QwDAKSJ0nQBC176L0AUAEAhdJ4DQte8idAEABELXCSB07bsIXQAAQYYuMSmcap2D0OumKIqiKGpf5ax0AQAAYBuELgAAgAYIXQAAAA0QugAAABogdAEAADRA6AIAAGjg4ND17bffDu//7xPVqMT5Rp+4dtgKfQvoC6Grk2Jw7RfXDluhbwF9IXR1Ugyu/eLaYSv0LaAvhK5OisG1X1w7bIW+BfSF0NVJMbj2i2uHrdC3gL4QujopBtd+ce2wFfoW0BdCVyfF4Novrt2+3V5fDBePXwz3+nZP6FtAX840dH0zfP6zcaD91Z8X9/31dz9fbP/jr8Z9f/b74a/WttbV9+B6P7x4PJ7D61t9e3b/4vFie3oSrNlWG6d67U7FnkLX2mMhdAF9OeHQ9efhlxcXwy9fL++TwcoPUXe/H3467n8hahHGVEj76e++8ba3q/0PrrfD9XjuQnOzDEP+RHL/YnhszvfiQWqif/xiOfXUbKuV07p28X2Ps1W7efta6VrXXwldQF/OMHQtt9shTK5qBVbA3r/+9Tip/3r4o7+9UfU7cS+32xO5nPBCM+3t9Xi+r8dH22q21c4pXbv4vsfaqt28fYWu0Yr+SugC+lI5dKlAI1ccRKVWk3S5oUg93l9Rcr/em78alGFpamsORO52VVObIjwlviqMhi79vKGVsxYVHlzVRDW9Tn/isFeAdIUmUP9TtTsJzV8vyYAztTVPCu52VVObYgJJTGjRoKSf17mrZlsNncq1S+4r+Me8uFbuazavJ9tu0rHn0T9nJedV3/bPq74/dq7He7LXQynvr4QuoC/1QpdcCfIC0xiyPjchRd/vhBYdwubHrAhdgce5YWm5oiUqHqry9+ceu2UtBlf5aXg56b0wA7W+3xm49QQ0P2bFxB14nBtw1DZ/ojCTU0zqfv++mm21dFrXLryvOubHw3w4+rkTYeb2xRxiou2mVDmPYrf0cQruPvq2vZ9uV2ybz5lqa75dej10+wUng9AF9KVS6Ir/MF1VOEyJUqtSZpVqRejyVqvcdkSFQpd6bOg4TCWDVWaVbMtyB1c9eEcH5fDEIahP2OaTdckE40+eituOoNpyD0k9NnQcRnJyEZOmdxx12mrrtK5dfN/FS5JBRAcxHUqiLzvYbkqt8+ifs5LzurwtyG3OefX3K70eo8L+SugC+lIndOkVq+hXb6n75QrYz4fP78TtFaHLC0ZrQlf0OMfKhq4H+l2XM7jmJrDU/fLTv1mRKJlgwpPbmok7epwj+VyxHeSxmueo2VZbp3XtAvvqY5arPIFS++pjEduCYSJ0DAnVzqN/zkrOq77tNe7vI8hzvfp6jAr7K6EL6AuhyytClz95bDFxz0KT18SZeGq21da5hK7gMfv0vsvwFTqGhGrn0T9nJedV3/Ya9/cRCF0AbJW+XgyHpZL73bAUDlS1Q1f/Xy+GJ4ZZ/H53gA9PArUn7vhx6ufy2p6Iicc7jjpttXVa1y60b+41BchQYbcTajcl95zx+/3XX3LO3H307cw+gnyu1ddjVNhfCV1AX6r9kF6FHi/kjCHF3I7d72+ToccOT3qfQ0NXcNUsFqrGSt0vnyPx2C3LH1zVQO1NUuNAbW7H7ve3yYnCHvD1PusnivAkF5qcbKn75XNY99Vsq6XTunbhfYPHLFabzIbxv6/tx8hjnVebYu2mVD2PVsDJn1e9j9Pwsh1BHsPq66G3efuFELqAvlQLXbJMQDLlBxT//ulrRbt0qLLaOGylayzr+abwJbYlVqvioSu/SrZlBQdXMxmY8gdp/35nkjP0RGC14U4eKz+d63amyVNs8yYiW2jyUtTzOpNwzbYaOrlrF9p3pNpV22V5j5XHNt0feD2RdpP883TAeXTPmZA7r/ox3nMt29HnZNpWej3K+yuhC+hL3dDVRYW+diwo+bs0L9Q1rH4HV7WC4c+FWfI3OV4wqNpWO2d37XCcFf2V0AX05QxDl14VW/nbLLEC9lCrXKJ6HlzdT/tlxKpB6JN+zbZaObdrh+Os6a+ELqAvZxm6Yl9Rxsr9evNhqu/BNfy1Skzoa5pZzbbaOKdrh+Os7a+ELqAvZxq6+isG135x7Q6hvtp0f4+li5W3CX0L6Auhq5NicO0X1w5boW8BfSF0dVIMrv3i2mEr9C2gLzJ0iTcuRVEU1V8B6IcMXaGVlVzxZm/r0BVJPDyuHbZC3wL6QujqBINrv7h22Ap9C+gLoasTDK794tphK/QtoC+Erk4wuPaLa4et0LeAvhC6OsHg2i+uHbZC3wL6QujqBINrv7h22Ap9C+hLNHSJv/wc2m6K0NUWg2u/uHbYCn0L6EsydKWCV++h6/7mMvrvycl//8z8kyMXl8NN4N8ckY+f9rkYFk3d3wyX1v3+fv7j/fLbY3Cdce2wlc37lnB77exzGWqoZJ8RfQvoSzZ0iQrd323osifUwIgoBk17sxpE3QFWDb7Xw7SbHiCd5uTzhAfmFNl24LgYXEdcO2ylVd+S26zH6ed1QlXJPhp9C+hLUegS5d/fY+iSA+XljfzHcmMT5IIe8OZd1T/E6z9UtqfbluTAaQ3AJRKT/bkPrlw7bKVd37ofbi6X7dvPX7bPjL4F9KU4dPnBq/evFw8eXGOTqz9Rr5641WDL1wh5XDtsZdO+5T/GkPvox5bsY6FvAX1ZFbpEmfvPI3QFPnVGBkX5SdSaqNVt99wlny4z0TO4zrh22MqmfUvuEwhm9vaSfSz0LaAvrHQt6AFVv+bQ6oV8rD3J6gE3NfGaiTw8nqdXSgQG1xnXDlvZtG9FVqvMfvJpS/ax0LeAvpzVb7ps8cHVFZtw1QBrahxUM6sdgnxM4HcZaqBNP5bBdca1w1Y27VvyvzOrWCX7WOhbQF+KQlfo/rP5TdeoZF85CIcmZUt4H/0JOtM+g+uMa4etbNq3IqtVY0Nz0CrZx0LfAvqSDV2h+0QRumxq8s01F2wnNsh6GFxnXDtsZdu+pW77X026gb5knxl9C+hLMnSFtps6zdAl/rdv96siOdh5E+vttf2JUw2S/oDo7mPaWX5SVdvTX08JDK4zrh22snXfGndy+1IouJfso9G3gL5EQ1euTnalSw9wYkBVFZpU1d/kMfuEf0StB91kO/o4Ap9gfQyuM64dtrJ93xJNqcBmKvx0+X0E+hbQl7MNXb1hcO0X1w5boW8BfSF0dYLBtV9cO2yFvgX0hdDVCQbXfnHtsBX6FtAXQlcnGFz7xbXDVuhbQF8IXZ1gcO0X1w5boW8BfSF0dYLBtV9cO2yFvgX0RYYuEaAOKfFYiqIo6uEKQD9k6AIAAMC2CF0AAAANELoAAAAaIHQBAAA0QOgCAABogNAFAADQAKELAACgAUIXAABAA4QuAACABghdAAAADRC6AAAAGiB0AQAANEDoAgAAaIDQBQAA0AChCwAAYHPD8F+P2R5iZ/twCAAAAABJRU5ErkJggg==)
</center>

**小结：**  
+ count(*)包括了所有的列，相当于行数，在统计结果的时候，**不会忽略列值为NULL**
+ count(1)包括了忽略所有列，用1代表代码行，在统计结果的时候，**不会忽略列值为NULL**
+ count(字段)只包括字段那一列，在统计结果的时候，__会忽略列值为null的计数（即某个字段值为NULL时，不统计）。__

**从效率层面说，COUNT(\*)= COUNT(1) > COUNT(字段)，又因为 COUNT(\*)是SQL92定义的标准统计数的语法，我们建议使用 COUNT(\*)。**



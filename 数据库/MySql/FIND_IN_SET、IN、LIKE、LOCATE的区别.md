# FIND_IN_SET、IN、LIKE、LOCATE的区别
***

[官方文档：FIND_IN_SET(str,strlist)](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_find-in-set)  
[官方文档：LOCATE(substr,str), LOCATE(substr,str,pos)](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#function_locate)   

[文档内容参考1：mysql中FIND_IN_SET()函数的使用及in()用法详解](https://www.jb51.net/article/143105.htm)  
[文档内容参考2：mysql模糊查询 like与locate效率](https://blog.csdn.net/qq_33745371/article/details/106673790)  
[文档内容参考3：MySQL 关于 in,find_in_set,locate 多值匹配问题](https://blog.csdn.net/qq_21358931/article/details/90262978)

**常用的`in()`和`like()`不做过多讲解，仅介绍`find_in_set()`以及`locate()`和他们之间的区别**

在介绍三种函数或者方法之前，我们先模拟一个场景：  
常见的用户和角色的关联，假设用户和角色之间的关联不是用的中间表，而是在用户表中增加一个角色的`id串`字段的形式，那么就有如下表结构设计：
```sql
-- ----------------------------
-- Table structure for demo_user_info
-- ----------------------------
DROP TABLE IF EXISTS `demo_user_info`;
CREATE TABLE `demo_user_info`  (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT '测试名称',
  `role_ids` varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT '测试权限id串',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;
-- ----------------------------
-- Records of demo_user_info
-- ----------------------------
INSERT INTO `demo_user_info` VALUES (1, '测试名称1', 'a,b');
INSERT INTO `demo_user_info` VALUES (2, '测试名称2', 'b,d,e');
INSERT INTO `demo_user_info` VALUES (3, '测试名称3', 'aa,bb,cc');
INSERT INTO `demo_user_info` VALUES (4, '测试名称4', 'aa,bb,cc,e');
```
如**`demo_user_info`**表结构，可以看出角色和用户的关系是用一个**`role_ids`**字段表示，且用英文逗号分隔开。
对于类似这种表结构，在业务上有各种各样的查询，此时就需要使用`mysql`的一些函数了。

[toc]
### 一、FIND_IN_SET()
在`MySQL`手册中`FIND_IN_SET()`函数的语法解释：  
![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/数据库/MySql/FIND_IN_SET、IN、LIKE、LOCATE的区别/FIND_IN_SET().png)

>`FIND_IN_SET(str,strlist)`  
`str` 要查询的字符串  
`strlist` 字符串集合： 参数以`”,”`分隔 如 (1,2,6,8,10,22)  
查询字符串集合(`strlist`)中包含(`str`)的结果，返回结果为**null**或**记录**  

>假如字符串`str`在由`N`个子链组成的字符串列表`strlist` 中，则返回值的范围在 `1` 到 `N` 之间。 一个字符串列表就是一个由一些被 `‘,'` 符号分开的子链组成的字符串。  
>
>如果第一个参数是一个常数字符串，而第二个是`type SET`列，则`FIND_IN_SET()` 函数被优化，使用`比特(bit)`计算。   
>如果`str`不在`strlist` 或`strlist` 为空字符串，则返回值为 `0` 。  
>如任意一个参数为`NULL`，则返回值为 `NULL`。这个函数在第一个参数包含一个逗号(`‘,'`)时将无法正常运行。

#### 1.FIND_IN_SET()介绍
**用法一：判断需要查询的字段是否包含某一个字符串**
```sql
SELECT FIND_IN_SET('b', 'a,b,c,d');
-- 执行结果：2（因为b 在strlist集合中放在2的位置（位置索引从1开始））

SELECT FIND_IN_SET('1','1');
-- 执行结果：1

SELECT FIND_IN_SET('1','2');
-- 执行结果：0

SELECT FIND_IN_SET(NULL,'1');
SELECT FIND_IN_SET('1',NULL);
-- 执行结果：NULL
```
结合实际业务：获取包含角色id为`"aa"`的所有数据
```sql
SELECT name FROM demo_user_info WHERE FIND_IN_SET('aa',role_ids)
-- 执行结果：
-- 3	测试名称3	aa,bb,cc
-- 4	测试名称4	aa,bb,cc,e
```
**用法二：用一个英文逗号隔开的字符串查询在这个字符串中的特定字段所以对应的数据**  
如：获取id为`1`,`2`,`3`的数据
```sql
SELECT * FROM demo_user_info WHERE FIND_IN_SET(id,'1,2,3');
-- 执行结果：
-- 1	测试名称1	a,b
-- 2	测试名称2	b,d
-- 3	测试名称3	aa,bb,cc
```
这种用法类型`IN()`，但是如果用`IN()`的话，写法如下：
```
SELECT * FROM demo_user_info WHERE id IN ('1','2','3');
-- 执行结果：
-- 1	测试名称1	a,b
-- 2	测试名称2	b,d
-- 3	测试名称3	aa,bb,cc

-- 如果IN()中的参数为'1,2,3'
SELECT * FROM demo_user_info WHERE id IN ('1,2,3');
-- 执行结果：
-- 1	测试名称1	a,b
```

#### 2.FIND_IN_SET()和IN()的区别
对比`IN()`的两种参数的执行结果可以发现，当`IN()`的参数是多个常量的时候能正常放回我们想要的结果；但是当参数是一个**逗号分割的集合串**的时候，`IN()`函数只能匹配第一项，所以，在一些特殊的查询业务下可以选择使用`FIND_IN_SET()`来进行匹配

#### 3.FIND_IN_SET()和LIKE()的区别
[LIKE()官方API](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_like)  
`LIKE()`函数大家肯定已经很熟悉了，运用不同的通配符的组合以及匹配的位置不同可以查询不同格式的字符串以达到搜索过滤的目的。  
同样我们用上面的例子来说明一下`LIKE()`和`FIND_IN_SET()`二者的区别：

场景：从`demo_user_info` 表中获取包含角色`id`为`a`的数据，`like()`实现如下：
```sql
SELECT * FROM demo_user_info WHERE role_ids LIKE ('%a%');
-- 1	测试名称1	a,b
-- 3	测试名称3	aa,bb,cc
-- 4	测试名称4	aa,bb,cc,e
```
结果很明显，当出现类型"`aa`"、"`ab`"、"`aaa`"类似的干扰项的时候，查询结果往往是不准确的；

而这时用`FIND_IN_SET()`往往能达到想要的结果：
```sql
SELECT * FROM demo_user_info WHERE FIND_IN_SET("a",role_ids)
-- 执行结果：
-- 1	测试名称1	a,b
```

### 二、LOCATE()
在MySQL手册中`LOCATE()`函数的语法解释：  
![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/数据库/MySql/FIND_IN_SET、IN、LIKE、LOCATE的区别/LOCATE().png)

>第一种语法返回字符串`str`中 **第一次** 出现的子字符串`substr`的位置。  
>第二种语法返回字符串`str`中 **第一次** 出现的子字符串`substr`的位置，从位置`pos`开始。如果`substr`不在`str`中，则返回`0`。  
>如果任何参数为`NULL`，则返回`NULL`。

>此函数是多字节安全的，并且仅当至少一个参数是二进制字符串时才区分大小写。

#### 1.LOCATE()和LIKE()
##### 语法和使用方式的区别
其实`LOCATE()`函数有一点类似`Java`中`Sting`的`indexOf`函数，都是获取某字符串在目标字符串中 **第一次** 出现的索引（`mysql`索引从`1`开始）；  
不过 **`LOCATE(substr,str,pos)`** 不同于 **`LOCATE(substr,str)`** ，`LOCATE(substr,str,pos)`限制了从多少位字符开始，不过用法也是大同小异。  
同样用上面的例子来说明一下`LIKE()`和`LOCATE()`二者的区别：

场景：从`demo_user_info` 表中获取包含角色`id`为`a`的数据：
```sql
-- like实现如下：
SELECT * FROM demo_user_info WHERE role_ids LIKE ('%a%');
-- 1	测试名称1	a,b
-- 3	测试名称3	aa,bb,cc
-- 4	测试名称4	aa,bb,cc,e

-- LOCATE()实现如下：
SELECT * FROM demo_user_info WHERE LOCATE("a",role_ids)
-- 执行结果：
-- 1	测试名称1	a,b
-- 3	测试名称3	aa,bb,cc
-- 4	测试名称4	aa,bb,cc,e
```
通过执行结果可以发现，两者的结果都一样，但是需要注意的是`LIKE()`函数在这里用的是 **全匹配** 的方式（即只要出现关键字"`a`"即被筛选出来），而`LOCATE()`并没有指定模糊前或后这个概念，因此可以看出 **`LOCATE(substr,str)`等同于`LIKE ('%str%')`** 。  
所以在开发中可以根据实际情况灵活选择。

##### 性能的区别
[文档参考：mysql模糊查询 like与locate效率](https://blog.csdn.net/qq_33745371/article/details/106673790)

#### 2.LOCATE()和FIND_IN_SET()
根据两者函数参数的要求灵活选用....具体区别对比官方文档，不赘述，引用网上的博客  
[文档参考：MySQL 关于 in,find_in_set,locate 多值匹配问题](https://blog.csdn.net/qq_21358931/article/details/90262978)
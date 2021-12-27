数据库事务和框架（Spring）事务的区别和联系

[文档内容参考1：基于MySQL 8.0 对事务的深度理解](https://blog.csdn.net/weixin_39723544/article/details/91653513)  
[文档内容参考2：Spring中的事务及数据库事务的关系](https://blog.csdn.net/weixin_39723544/article/details/91877478)  
[文档内容参考3：spring的事务是什么？与数据库的事务是否一样](https://www.cnblogs.com/leijiangtao/p/11911774.html)  

[toc]
## 一、MySql事务
### 1. 数据库事务的四大基本特性(ACID)及理解
数据库事务 transanction 正确执行的四个基本要素：ACID，原子性(Atomicity)、一致性(Consistency)、隔离
性(Isolation)、持久性(Durability)。  

* **原子性（Atomicity）：** 整个事务中的所有操作，要么全部完成，要么全部不完成，不可能停滞在中间某个环节。事务在执行过程中发生错误，会被回滚（Rollback）到事务开始前的状态，就像这个事务从来没有执行过一样。
* **一致性（Consistency）：** 在事务开始之前和事务结束以后，数据库的完整性约束没有被破坏，也就是不会存在中间状态的数据。
* **隔离性（Isolation）：** 隔离状态执行事务，使它们好像是系统在给定时间内执行的唯一操作。如果有两个事务，运行在相同的时间内，执行 相同的功能，事务的隔离性将确保每一事务在系统中认为只有该事务在使用系统。这种属性有时称为串行化，为了防止事务操作间的混淆，必须串行化或序列化请求，使得在同一时间仅有一个请求用于同一数据。
* **持久性（Durability）：** 在事务完成以后，该事务所对数据库所作的更改便持久的保存在数据库之中，并不会被回滚。

### 2. MySQL中事务隔离级别
|             隔离级别             |  脏读  | 不可重复读 | 幻读(虚读) |
| :------------------------------  | :----: | :--------: | :--------: |
| **读未提交（Read uncommitted）** |  可能  |    可能    |    可能    |
|  **读已提交（Read committed）**  | 不可能 |    可能    |    可能    |
| **可重复读（Repeatable read）**  | 不可能 |   不可能   |    可能    |
|  **串行化（Serializable ）**   | 不可能 |   不可能   |   不可能   |

#### 脏读、不可重复读、幻读概念
**脏读：** 事务A读取了事务B更新的数据，然后B回滚操作，那么A读取到的数据是脏数据  
**不可重复读：** 事务 A 多次读取同一数据，事务 B 在事务A多次读取的过程中，对数据作了更新并提交，导致事务A多次读取同一数据时，结果 不一致。  
**幻读：** 系统管理员A将数据库中所有学生的成绩从具体分数改为ABCDE等级，但是系统管理员B就在这个时候插入了一条具体分数的记录，当系统管理员A改结束后发现还有一条记录没有改过来，就好像发生了幻觉一样，这就叫幻读。  

**注意：<font color="red">不可重复读的和幻读很容易混淆，不可重复读侧重于修改，幻读侧重于新增或删除。</font>解决不可重复读的问题只需锁住满足条件的行，解决幻读需要锁表**

#### 事务隔离级别概念
**读未提交（Read uncommitted）：** 一个事务可以读取另一个未提交事务的数据。

**读已提交（Read committed）：** 一个事务要等另一个事务提交后才能读取数据。

**可重复读（Repeatable read）：** 就是在开始读取数据（事务开启）时，不再允许修改操作。

**串行化（Serializable ）：**  是最高的事务隔离级别，在该级别下，事务串行化顺序执行，可以避免脏读、不可重复读与幻读。
**但是这种事务隔离级别效率低下，比较耗数据库性能，一般不使用。**

### 3. MySql事务常用语句和操作
**查看当前会话的数据库的隔离级别**  
```sql
-- MySQL 8.0
select @@transaction_isolation;
-- 或者
show variables like 'transaction_isolation'

-- MySQL 8.0之前的版本
select @@tx_isolation;
```

**查看系统级别的数据库的隔离级别**  
```sql
-- MySQL 8.0
select @@global.transaction_isolation;

-- MySQL 8.0之前的版本
select @@global.tx_isolation;
```

**修改当前会话的事务隔离级别**  
```sql
set session transaction isolation level 事务的隔离级别;

-- 如：
set session transaction isolation level read committed;
```

**修改全局的事务隔离级别**
```sql
set session global transaction isolation level 事务的隔离级别;

-- 如：
set session global transaction isolation level read committed;
```

**开启事务** 
```sql
start transaction;
```

**提交事务**
```sql
commit;
```

**回滚**
```sql
rollback;
```

### 4. 小结
* 事务隔离级别为 **已提交读（Read committed）** 时，写数据只会锁住相应的行。
* 事务隔离级别为 **可串行化（Serializable ）** 时，读写数据都会锁住整张表。
* 隔离级别越高，越能保证数据的完整性和一致性，但是对并发性能的影响也越大。

## 二、Spring事务
### 1. Spring事务的隔离级别（Isolation）
* **ISOLATION_DEFAULT：**  
这是一个PlatfromTransactionManager默认的隔离级别，使用数据库默认的事务隔离级别。
* **ISOLATION_READ_UNCOMMITTED：**  
对应数据库事务 **读未提交（Read uncommitted）；** 这是事务最低的隔离级别，它充许令外一个事务可以看到这个事务未提交的数据。这种隔离级别会产生脏读，不可重复读和幻像读。
* **ISOLATION_READ_COMMITTED：**   对应数据库事务 **读已提交（Read committed）；** 保证一个事务修改的数据提交后才能被另外一个事务读取。另外一个事务不能读取该事务未提交的数据
* **ISOLATION_REPEATABLE_READ：**  
对应数据库事务 **可重复读（Repeatable read）；** 这种事务隔离级别可以防止脏读，不可重复读。但是可能出现幻像读。它除了保证一个事务不能读取另一个事务未提交的数据外，还保证了避免下面的情况产生(不可重复读)。
* **ISOLATION_SERIALIZABLE：**  
对应数据库事务 **串行化（Serializable ）；** 这是花费最高代价但是最可靠的事务隔离级别。事务被处理为顺序执行。除了防止脏读，不可重复读外，还避免了幻读。

### 2. Spring事物的传播属性（Propagation）-7种
Spring管理的事务是逻辑事务，而且物理事务和逻辑事务最大差别就在于事务传播行为，
事务传播行为用于存在多个事务方法间调用时，事务是如何在这些方法间传播的。

**REQUIRED：**  
必须有逻辑事务，否则新建一个事务。表示如果当前存在一个逻辑事务，否则将新建一个逻辑事务。  
<font color="red">**是Spring和SpringBoot事务传播属性的默认值。**</font>

**SUPPORTS：**   
如果当前存在逻辑事务，就加入到该逻辑事务。  
如果当前没有逻辑事务，就以非事务方式执行，如果当前没有事务，就以非事务方式执行。

**MANDATORY：**
必须有事务。当运行在存在逻辑事务中则以当前事务运行，如果当前没有事务，就抛出异常。

**REQUIRES_NEW：**
每次都会创建新的逻辑事务。如果当前存在事务，把当前事务挂起。

**NOT_SUPPORTED：**  
以非事务方式执行操作。如果当前存在事务，就把当前事务挂起。

**NEVER：**  
以非事务方式执行。如果当前存在事务，则抛出异常。

**NESTED：**  
嵌套事务支持。如果当前存在事务，则在嵌套事务内执行；如果当前不存在事务，则创建一个新的事务。
嵌套事务使用数据库中的 **保存点（savepoint）** 来实现，**即嵌套事务回滚不影响外部事务，但外部事务回滚将导致嵌套事务回滚。**

#### Nested和RequiresNew的区别:
* RequiresNew每次都创建新的独立的物理事务，而Nested只有一个物理事务;
* Nested嵌套事务回滚或提交不会导致外部事务回滚或提交，但外部事务回滚将导致嵌套事务回滚；而 RequiresNew由于都是全新的事务，所以之间是无关联的；
* Nested使用JDBC 3的保存点(save point)实现，即如果使用低版本驱动将导致不支持嵌套事务;
* 使用嵌套事务，必须确保<font color="red">**具体事务管理器实现的nestedTransactionAllowed属性为true**</font>，
否则不支持嵌套事务；  
如**DataSourceTransactionManager默认支持**，而**HibernateTransactionManager默认不支持**，需要设置来开启。

<font color="red">**补充：项目中针对增删改操作一般使用Required级别。对针对查询使用Support或NotSupport。**</font>

## 三、MySql事务和Spring事务的区别和联系（总结）
**总的来说，MySql事务和Spring事务本质上其实是同一个概念。**

数据库事务有4种隔离级别，无传播行为。  
Spring事务有5种隔离级别，7种传播行为。**其中Spring多了一个DEFAULT的隔离级别， 这是一个PlatfromTransactionManager默认的隔离级别，即使用数据库默认的事务隔离级别。**

Spring的事务是对数据库的事务的封装，最后本质的实现还是在数据库，假如数据库不支持事务的话，Spring的事务是没有作用的

数据库的事务说简单就只有开启、回滚和关闭。  
而Spring就是对数据库事务的包装：原理就是获取一个数据连接，根据Spring的事务配置，操作这个数据连接对数据库进行事务开启、回滚或关闭操作。  
但是Spring除了实现这些，还配合Spring的传播行为对事务进行了更广泛的管理。

**补充：Springboot框架中编程式事务的使用方式：**
```java
/**
 * 在需要事务的方法上增加如下注解
 * isolation（隔离级别）的默认值是DEFAULT
 * propagation（传播属性）的默认值是REQUIRED
 */
@Transactional(isolation = Isolation.DEFAULT, propagation = Propagation.REQUIRED)
```
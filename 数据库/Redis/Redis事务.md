# Redis事务
**[官方文档](https://redis.io/topics/transactions)**  

[文档内容参考1：Redis 事务](https://www.runoob.com/redis/redis-transactions.html)   
[文档内容参考2：深入理解Redis事务](https://zhuanlan.zhihu.com/p/146865185)  
[文档内容参考3：详细探究Redis事务与MySQL事务的区别【转】](https://www.cnblogs.com/gjmhome/p/14409390.html)  
[文档内容参考4：Redis到底有没有ACID事务](https://blog.csdn.net/luoyang_java/article/details/100143164)  
[文档内容参考5：浅谈 Redis 事务特性和使用](https://nd.mbd.baidu.com/r/s6dl2ei8Bq?f=cp&rs=558614419&ruk=ovYnOn9sOh-Ra9yN3SXK8Q&u=7085bb70793d60f2)

[toc]
## 一、Redis事务基本概念
事务：`Transaction`

`Redis`的事务本质是 **<font color="red">一组命令的集合</font>** ，可以一次执行多个命令， **所有命令都会<font color="red">序列化，按顺序地串行化执行</font>** 而不会被其它命令插入，不许插队。  
**将一组需要一起执行的命令放到`multi`和`exec`两个命令之间。** `multi`命令代表事务开始，`exec`命令代表事务结束，它们之间的命令是 **<font color="red">原子顺序合</font>** 执行的。

## 二、Redis事务的三个特性
1. **单独的隔离操作** ：事务中的所有命令都会序列化、按顺序地执行。事务在执行的过程中，不会被其他客户端发送来的命令请求所打断；
2. **没有隔离级别** 的概念：队列中的命令没有提交之前都不会实际的被执行；  
因为事务提交前任何指令都不会被实际执行，也就不存在 **“事务内的查询要看到事务里的更新，在事务外查询不能看到”** 这个让人万分头痛的问题；
3. **不保证原子性（`ACID`事务中的`A-原子性`）**：redis同一个事务中如果有一条命令执行失败，其后的命令仍然会被执行，没有回滚；

## 三、Redis事务执行的相关命令和三个阶段
### 1. Redis 事务相关命令

`redis`事务使用了`multi`、`exec`、`discard`、`watch`、`unwatch`命令，命令的作用如下：  
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis事务/Redis事务相关命令.png)
</center>

### 2. Redis事务执行的三个阶段
1. 开启：以`MULTI`开始一个事务；
2. 入队：将多个命令入队到事务中，接到这些命令并不会立即执行，而是放到等待执行的事务队列里面；
3. 执行：由`EXEC`命令触发事务；

#### 2.1 开启事务
`MULTI`命令的执行标记着事务的开始：
```java
127.0.0.1:6379> MULTI
OK
```
这个命令唯一做的就是，将客户端的 `REDIS_MULTI` 选项打开，让客户端从非事务状态切换到事务状态。

#### 2.2 命令入队
当客户端处于非事务状态下时，所有发送给服务器端的命令都会立即被服务器执行：
```java
127.0.0.1:6379> SET msg "hello moto"
OK

127.0.0.1:6379> GET msg
"hello moto"
```

但是，当客户端进入事务状态之后，服务器在收到来自客户端的命令时，不会立即执行命令，而是将这些命令全部放进一个事务队列里，然后返回`QUEUED`，表示命令已入队：
```java
127.0.0.1:6379> MULTI
OK

127.0.0.1:6379> SET msg "hello moto"
QUEUED

127.0.0.1:6379> GET msg
QUEUED
```

此过程如下图：  
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis事务/Redis事务开启及命令入队的过程.png)
</center>

#### 2.3 执行事务
前面说到，当客户端进入事务状态之后，客户端发送的命令就会被放进事务队列里。

但其实并不是所有的命令都会被放进事务队列，其中的例外就是 **`EXEC`、 `DISCARD`、 `MULTI` 和 `WATCH`** 这四个命令，当这四个命令从客户端发送到服务器时，它们会像客户端处于非事务状态一样，直接被服务器执行：  
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis事务/Redis事务开启及命令入队到执行的过程.png)
</center>

如果客户端正处于事务状态，那么当 **`EXEC`** 命令执行时，服务器根据客户端所保存的事务队列，以`先进先出（FIFO）`的方式执行事务队列中的命令： **最先入队的命令最先执行，而最后入队的命令最后执行。**

执行事务中的命令所得的结果会以 `FIFO` 的顺序保存到一个 **回复队列** 中。  
当事务队列里的所有命令被执行完之后，`EXEC`命令会将 **回复队列** 作为自己的执行结果返回给客户端，客户端从事务状态返回到 **非事务状态** ，至此，事务执行完毕。

### 3. Redis事务各种执行情况距离
#### 3.1 正常执行
```java
127.0.0.1:6379> MULTI        # 开启事务
OK
127.0.0.1:6379> set k1 v1	# 命令1 入队
QUEUED
127.0.0.1:6379> set k2 v2	# 命令2 入队
QUEUED
127.0.0.1:6379> get k2   	# 命令3 入队
QUEUED
127.0.0.1:6379> set k3 v3	# 命令4 入队
QUEUED
127.0.0.1:6379> EXEC 		# 执行事务
1) OK						# 输出结果
2) OK
3) "v2"
4) OK
127.0.0.1:6379> 
```

#### 3.2 放弃事务
```java
127.0.0.1:6379> MULTI		 # 开启事务
OK
127.0.0.1:6379> set k1 v11	# 命令1 入队
QUEUED
127.0.0.1:6379> set k2 v22	# 命令2 入队（在事务中修改k2的值，k2原值为v2）
QUEUED
127.0.0.1:6379> set k3 v33	# 命令3 入队
QUEUED
127.0.0.1:6379> DISCARD 	  # 取消事务
OK						
127.0.0.1:6379> get k2		# 输出结果（k2的值未被成功改动）
"v2"
127.0.0.1:6379> 
```

#### 3.3 若在事务队列中存在<font color='red'>命令性错误</font>，则执行EXEC命令时，所有命令都不会执行
```java
127.0.0.1:6379> MULTI		 # 开启事务
OK
127.0.0.1:6379> set k1 v11	# 命令1 入队
QUEUED
127.0.0.1:6379> set k2 v22	# 命令2 入队（在事务中修改k2的值，k2原值为v2）
QUEUED
127.0.0.1:6379> set k3 v33	# 命令3 入队
QUEUED
127.0.0.1:6379> getset k4	 # 命令4 入队（错误命令）
(error) ERR wrong number of arguments for 'getset' command
127.0.0.1:6379> set k5 v55	# 命令5 入队
QUEUED
127.0.0.1:6379> EXEC 	 	# 执行事务（出现报错）
(error) EXECABORT Transaction discarded because of previous errors.		
127.0.0.1:6379> get k5		# 输出结果（set k5 v55未被执行，故k5不存在）
(nil)
127.0.0.1:6379> 
```

#### 3.4 若在事务队列中存在<font color='red'>语法性错误</font>，则执行EXEC命令时，其他正确命令会被执行，错误命令抛出异常。
```java
127.0.0.1:6379> MULTI		 # 开启事务
OK
127.0.0.1:6379> incr k1 	  # 命令1 入队（对k1(值为‘v1’)进行+1，由于k1的值为string类型，而incr命令只能作用于integer类型，所以最终执行会报错）
QUEUED
127.0.0.1:6379> set k2 v22	# 命令2 入队（在事务中修改k2的值，k2原值为v2）
QUEUED
127.0.0.1:6379> set k3 v33	# 命令3 入队
QUEUED
127.0.0.1:6379> set k4 v44	# 命令4 入队
QUEUED
127.0.0.1:6379> get k4		# 命令5 入队
QUEUED
127.0.0.1:6379> EXEC 	 	# 执行事务（第一条命令提示类型异常，其他命令正常执行）
1) (error) ERR value is not an integer or out of range
2) OK
3) OK
4) OK
5) "v44"
127.0.0.1:6379> 
```

### 4. 小结
**单个 `Redis` 命令的执行一定是`原子性`的，但`Redis` 没有在事务上增加任何 `维持原子性` 的机制，所以 `Redis` 事务的执行严格来说并不是 `原子性`的。**

`Redis`事务可以理解为一个打包的批量执行脚本，但批量指令并非 **原子化** 的操作，中间某条指令的失败不会导致前面已做指令的 **回滚** ，也不会造成后续的指令不做。

## 四、Redis事务与MySQL事务的区别
> **注意：这里讨论的是MySQL常用的`InnoDB`引擎（`MyISAM`不支持事务操作）**

### 1. 事务命令
**mysql：**  
* `Begin`: 显式的开启一个事务；
* `Commit`：提交事务，将对数据库进行的所有的修改变成永久性的；
* `Rollback`：结束用户的事务，并撤销现在正在进行的未提交的修改。

**redis：**
* `Multi`：标记事务的开始；
* `Exec`：执行事务的`commands队列`；
* `Discard`：结束事务，并清除`commands队列`。

### 2. 默认状态
**mysql：**  
`mysql`会默认开启一个事务，且缺省设置是自动提交，即每成功执行一次`sql`，一个事务就会马上`commit`，所以不能`rollback`；  
默认情况下如上所述，但是非默认情况下，可以`rollback`。

**redis：**  
`redis`默认不会开启事务（单一命令已经是 **原子性** 操作，不需要开启事务），即`command`会立即执行，而不会排队，并不支持`rollback`。

### 3. 使用方式
**mysql（包含两种方式）：**  
* 用`Begin`、`Rollback`、`commit`显式开启并控制一个 新的 `Transaction`；  
* 执行命令 `set autocommit=0`，用来禁止当前会话自动`commit`，控制默认开启的事务。  

**redis：**  
用 **`multi`、`exec`、`discard`** 命令显式开启并控制一个`Transaction`。（注意：这里没有强调 **“新的”** ，因为默认是不会开启事务的）。

### 4. 实现原理
**mysql：**
* mysql实现事务，是基于 **`undo log`** 和 **`redo log`** 日志；
* **`undo log`** ：记录修改前状态，`rollback`基于`undo log日志`实现；
* **`redo log`** ：记录修改后的状态，`commit`基于`redo log日志`实现；
* 在`mysql`中无论是否开启事务，`sql`都会被立即执行并返回执行结果，只是事务开启后执行后的状态只是记录在`redo日志`，执行`commit`之后，数据才会被写入磁盘；  
```java
int insertCount = orderMapper.insert(s); 
```
上述代码：  
`insertCount` 将会被立即赋值（无论是否开启事务，只是结果暂未被写入磁盘）。

**redis:**
* `redis`实现事务，是基于`commands队列`；
* 如果 **没有开启事务** ：`command`将会被立即执行并返回执行结果，并且 **<font color='red'>直接写入磁盘</font>** ；
* 如果 **事务开启** ：`command`不会被立即执行，而是排入队列，并返回排队状态（具体依赖于客户端（例如：`spring-data-redis`）自身实现）。**直到调用`exec`命令才会执行`commands队列`。**
```java
boolean a = redisTemplate.opsForZSet().add("generalService",orderId,System.currentTimeMillis());
```
* 上述代码：  
	* 如果没有开启事务：操作被立即执行，`a`将会被立即赋值（`true/false`）；
	* 如果开启事务：操作不会被立即执行，将会返回`null`值，而`a`的类型是`boolean`，所以将会抛出异常：`java.lang.NullPointerException`。

## 五、总结
### 1. Redis事务和ACID事务的区别
`Redis`事务官方解释： **[官方文档](https://redis.io/topics/transactions)**  
>**Transactions**  
>MULTI, EXEC, DISCARD and WATCH are the foundation of transactions in Redis. They allow the execution of a group of commands in a single step, with two important guarantees:
>
>* **<font color='red'>All the commands in a transaction are serialized and executed sequentially. It can never happen that a request issued by another client is served in the middle of the execution of a Redis transaction. This guarantees that the commands are executed as a single isolated operation.（事务中的所有命令都被序列化并按顺序执行。在Redis 事务的执行过程中，永远不会发生另一个客户端发出的请求。这保证了命令作为单个隔离操作执行）</font>** 
>
>* **<font color='red'>Either all of the commands or none are processed, so a Redis transaction is also atomic. （要么处理所有命令，要么不处理任何命令，因此 Redis 事务也是原子的。）</font>**  The EXEC command triggers the execution of all the commands in the transaction, so if a client loses the connection to the server in the context of a transaction before calling the EXEC command none of the operations are performed, instead if the EXEC command is called, all the operations are performed. When using the append-only file Redis makes sure to use a single write(2) syscall to write the transaction on disk. However if the Redis server crashes or is killed by the system administrator in some hard way it is possible that only a partial number of operations are registered. Redis will detect this condition at restart, and will exit with an error. Using the redis-check-aof tool it is possible to fix the append only file that will remove the partial transaction so that the server can start again.


<font color='red'>**注意：**</font>  
官方文档描述：  
* **<font color='red'>事务中的所有命令会按照顺序执行，而且在执行过程中，不会有其他的命令插入，保证事务中的命令都是单独的操作。</font>**
* **<font color='red'>事务中的所有命令要么全部执行，要么都不做处理。</font>**

**可是此原子性并非ACID事务中的原子性。**

官方文档中还有一点需要注意：
>**<font color='red'>Errors happening after EXEC instead are not handled in a special way: all the other commands will be executed even if some command fails during the transaction.
（EXEC之后，发生的错误不会以特殊方式处理：即使某些命令在事务期间失败，所有其他命令也将执行。）</font>**

**通过这里，就已经很明确知道了，`Redis`事务并不满足数据库事务（`ACID特性`）中的原子性。**

### 2. Redis事务的回滚
**`Redis`自身是不支持回滚操作的。**  
官方文档：
>**Why Redis does not support roll backs?**
>If you have a relational databases background, the fact that Redis commands can fail during a transaction, but still Redis will execute the rest of the transaction instead of rolling back, may look odd to you.
>
>However there are good opinions for this behavior:
>
>* **<font color='red'>Redis commands can fail only if called with a wrong syntax (and the problem is not detectable during the command queueing), or against keys holding the wrong data type: this means that in practical terms a failing command is the result of a programming errors, and a kind of error that is very likely to be detected during development, and not in production.（Redis 命令只有在使用错误的语法调用时才会失败（并且在命令排队期间无法检测到问题），或者针对持有错误数据类型的键：这意味着实际上失败的命令是编程错误的结果，一种很可能在开发过程中检测到的错误，而不是在生产中。）</font>**
>
>* **<font color='red'>Redis is internally simplified and faster because it does not need the ability to roll back.（Redis 内部简化，速度更快，因为它不需要回滚的能力。）</font>**  
>
>An argument against Redis point of view is that bugs happen, however it should be noted that in general the roll back does not save you from programming errors. For instance if a query increments a key by 2 instead of 1, or increments the wrong key, there is no way for a rollback mechanism to help. Given that no one can save the programmer from his or her errors, and that the kind of errors required for a Redis command to fail are unlikely to enter in production, we selected the simpler and faster approach of not supporting roll backs on errors.

**如何实现Redis事务回滚：**  
`Redis` 是支持 `LUA 脚本`的，而在执行脚本的时候也是事务性的，推荐使用 `LUA 脚本`去实现。

使用已有的命令来实现简单的类似事务隔离特性的功能，主要思路就是使用 `WATCH` 监控事务中需要操作的值，以保证事务操作前后所监控的值不发生变化，或者发生变化以后中断事务操作。

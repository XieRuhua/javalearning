# Redis详解

[Redis官方文档](https://redis.io/docs/)  
[Redis常见命令说明及使用方式](https://www.redis.net.cn/order/)
***

[文档内容参考1：小林当面试官，面你 Redis ！](https://mp.weixin.qq.com/s/IkV8YKWOxNRZGD8C6U7_aQ)   
[文档内容参考2：Redis 八股文来袭！](https://mp.weixin.qq.com/s/XFQYvVB5uJSjYrHuJP9sXg)   
[文档内容参考3：redis知识点总结](https://www.cnblogs.com/syhx/p/9618084.html)   
[文档内容参考4：不得不精Redis-超详细的教程](https://zhuanlan.zhihu.com/p/65180667)   
[文档内容参考5：彻底弄懂Redis的内存淘汰策略](https://zhuanlan.zhihu.com/p/105587132)   
[文档内容参考6：[Redis] 你了解 Redis 的三种集群模式吗？](https://zhuanlan.zhihu.com/p/145186839)   

[toc]
## 一、Redis是什么
### 1. 简介
`Redis`是一款内存高速缓存数据库。  
全称为：`Remote Dictionary Server`（远程数据服务），该软件使用`C语言`编写， **`Redis`是一个基于内存的高性能`key-value`数据库** ，不过与传统`RDBM(关系数据库)`不同，`Redis`属于`NoSQL(非关系型数据库)`，数据是存在`内存`中的，也就是`内存数据库`，所以读写速度非常快，因此被广泛应用于 **`缓存`** 方面。

`Redis` 提供了多种数据类型（`string`、`list`、`set`、`zset(sorted set)`、`hash`等）来支持不同的业务场景（除了做 **缓存** 之外，也经常用来做 **分布式锁** ，甚至是 **消息队列** ）  
另外，还支持 **事务** 、 **持久化** 、 **Lua 脚本** 、 **多种集群方案** 等。

### 2. 缓存数据处理流程
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis详解/缓存数据处理流程.png)
</center>

**流程：**  
1. 如果用户请求的数据在缓存中就直接返回；
2. 缓存中不存在的话就看数据库中是否存在；
3. 数据库中存在的话就更新缓存中的数据并返回；
4. 数据库中不存在的话就返回空数据。

### 3. 为什么要用 Redis（为什么要用缓存）
存储数据库如`mysql`通常支持完整的`ACID`特性，因为 **可靠性** 、 **持久性** 等因素，性能普遍不高，高并发的查询会给`mysql`带来压力，造成数据库系统的不稳定，同时也容易产生延迟。  
根据 **局部性原理** ，`80%`请求会落到`20%`的热点数据上，在 **`读多写少`** 的场景增加一层缓存非常有助提升系统 **吞吐量** 。

**在服务器中常用来存储一些需要频繁调取的数据，这样可以大大节省系统直接读取磁盘来获得数据的`I/O`开销，更重要的是可以极大提升数据请求速度。**

## 二、Redis的特点
### 1. 简述
`Redis`以内存作为数据 **存储介质** ，所以读写数据的效率极高，远远超过数据库。  
以设置和获取一个`256字节`字符串为例，它的读取速度可高达`110000次/s`，写速度高达`81000次/s`（是已知综合性能最快的`Key-Value DB`）。

`Redis`跟`memcache`不同的是，储存在`Redis`中的数据是 **持久化** 的，断电或重启后，数据也不会丢失。  
因为`Redis`的存储分为 **`内存存储`、`磁盘存储`、`log文件`三部分** ，重启后，`Redis`可以从磁盘重新将数据加载到内存中，这些可以通过配置文件对其进行配置（持久化及数据恢复见后文 —— 七、数据持久化）；正因为这样，`Redis`才能实现持久化（也可以定期通过异步操作把数据库数据`flush`到硬盘上进行保存）。

`Redis`的出色之处不仅仅是性能，还支持保存多种数据结构，**此外`单个value`的最大限制是`1GB`，不像 `memcached`只能保存`1MB`的数据** ，因此`Redis`可以用来实现很多有用的功能，比如 **用`List`来做`FIFO双向链表`，实现一个轻量级的高性 能消息队列服务；用它的`Set`可以做高性能的`tag系统`等等。**  
同时`Redis`支持主从模式，可以配置集群，这样更利于支撑起大型的项目，这也是`Redis`的一大亮点。  
另外`Redis`也可以对存入的`Key-Value`设置`expire时间`，因此也可以被当作一个功能加强版的`memcached`来用。

#### 高性能：
假如用户第一次访问数据库中的某些数据的话，这个过程是比较慢，毕竟是通过关系型数据库再从硬盘中读取的。但是，如果说，用户访问的数据属于高频数据并且不会经常改变的话，那么就该用户访问的数据缓存在缓存中。保证用户下一次再访问这些数据的时候就可以直接从缓存中获取了。操作缓存就是直接操作内存，所以速度相当快。  
**不过，要保持数据库和缓存中的数据的一致性。如果数据库中的对应数据改变的之后，缓存中相应的数据也必须`同步改变`！**

#### 高并发：
>**`QPS（Query Per Second）`：服务器每秒可以执行的查询次数**

一般像 `MySQL` 这类的数据库的 `QPS` 大概都在 `1w` 左右`（4 核 8g）` ，但是使用 `Redis` 缓存之后很容易达到 `10w+`，甚至最高能达到 `30w+`（就单机 `Redis` 的情况，如果是`Redis` 集群的话会更高）。

由此可见，直接操作缓存能够承受的数据库请求数量是远远大于直接访问数据库的，所以我们可以考虑把数据库中的部分数据转移到缓存中去，这样用户的一部分请求会直接到缓存这里而不用经过数据库。 **从而提高了系统整体的并发。**

<font color="red">**`Redis`的主要缺点是数据库容量受到物理内存的限制，不能用作海量数据的高性能读写，因此适合的场景主要局限在较小数据量的高性能操作和运算上。**</font>

### 2. 和Memecache的区别和共同点
**共同点：**  
* 都是基于内存的数据库，一般都用来当做缓存使用。
* 都有过期策略。
* 两者的性能都非常高。

**区别：**  
* `Redis` 支持更丰富的数据类型（支持更复杂的应用场景）。不仅仅支持简单的 `k/v` 类型的数据，同时还提供 `list`、`set`、`zset`、`hash` 等数据结构的存储；    
`Memcached` 只支持最简单的 `k/v` 数据类型。
* `Redis` 支持数据的持久化，可以将内存中的数据保持在磁盘中，重启的时候可以再次加载进行使用；  
`Memecache` 只把数据全部存在内存之中。
* `Redis` 因为可以把缓存中的数据持久化到磁盘上，所以具备灾难恢复机制。
* `Redis` 在服务器内存使用完之后，可以将不用的数据放到磁盘上；  
`Memcached` 在服务器内存使用完之后，就会直接报异常。
* `Redis` 目前是原生支持 `cluster`（集群）模式的；  
`Memcached` 没有原生的集群模式，需要依靠客户端来实现往集群中分片写入数据。
* `Redis` 使用单线程的多路 `IO` 复用模型。 （`Redis 6.0` 引入了`多线程 IO` ）；  
`Memcached` 是多线程，非阻塞 `IO` 复用的网络模型。
* `Redis` 支持`发布订阅模型`、`Lua 脚本`、`事务`等功能，同时支持更多的编程语言；而`Memcached` 不支持。
* `Redis` 同时使用了`惰性删除`与`定期删除`；  
`Memcached` 过期数据的删除策略只用了`惰性删除`。

### 3. 为什么Redis需要把所有数据放到内存中？
`Redis`为了达到最快的读写速度将数据都读到内存中，并通过异步的方式将数据写入磁盘。所以`Redis`具有快速和数据持久化的特征。如果不将数据放在内存中，磁盘`I/O速度`为严重影响`Redis`的性能。  
**如果设置了最大使用的内存，则数据已有记录数达到内存限值后不能继续插入新值（不同的删除策略处理方式会不同）**

### 4. 虚拟内存
#### 4.1 应用场景
对于大多数数据库而言，最为理想的运行方式就是将所有的数据都加载到内存中，而之后的查询操作则可以完全基于内存数据完成。但是，在现实中这样的场景并不多，更多的情况则是只有部分数据可以被加载到内存中。

在`Redis`中，有一个非常重要的概念，**即`key`一般不会被交换**
* 如果你的数据库中有 **大量的`key`，其中每个`key`仅仅关联很小的`value`** ，那么这种场景就不是非常适合使用虚拟内存。
* 如果恰恰相反，**数据库中只是包含少量的`key`，而每一个`key`所关联的`value`却非常大**，那么这种场景对于使用虚拟内存就非常合适了。

在实际的应用中，为了能让虚拟内存更为充分的发挥作用以帮助我们提高系统的运行效率，我们可以将带有很多较小值的`Key`合并为带有少量较大值的`Key`。  
**其中最主要的方法就是将原有的`Key/Value`模式改为基于`Hash`的模式，这样可以让很多原来的`Key`成为`Hash`中的属性。**

#### 4.2 配置Redis虚拟内存
1. 在配文件 **Redis.conf** 中添加以下配置项，以使当前`Redis`服务器在启动时打开虚拟内存功能（默认关闭的）。
    ```bash
    # 默认状态
    # vm-enabled no
    
    # 开启
    vm-enabled yes 
    ```

2. 同时在配置文件中设定`Redis` **最大可用的虚拟内存字节数**。  
    如果内存中的数据大于该值，则有部分对象被持久化到磁盘中，其中被持久化对象所占用的内存将被释放，直到已用内存小于该值时才停止持久化。
    ```bash
    # 默认
    # vm-max-memory (bytes) 
    
    # 配置
    vm-max-memory 1000000
    ```
    `Redis`的`key`交换规则是尽量考虑 **"最老"** 的数据（即最长时间没有使用的数据将被持久化）；如果两个对象的`age`相同，那么`value`较大的数据将先被持久化。  
    需要注意的是：`Redis`不会将`Key`持久化到磁盘，因此如果仅仅`key`的数据就已经填满了整个虚拟内存，那么这种数据模型将不适合使用虚拟内存机制，或者是将该值设置的更大，以容纳整个`Key`的数据。  
    **在实际的应用，如果考虑使用`Redis`虚拟内存，我们应尽可能的分配更多的内存交给`Redis`使用，以避免频繁`key交换`的将数据持久化到磁盘上。**

3. 在配置文件中设定页的数量及每一页所占用的字节数。为了将内存中的数据传送到磁盘上，我们需要使用交换文件。  
    这些文件与数据持久性无关，`Redis`会在退出前会将它们全部删除。由于对交换文件的访问方式大多为随机访问，因此建议将交换文件存储在固态磁盘上，这样可以大大提高系统的运行效率。
    ```bash
    vm-pages 134217728 
    vm-page-size 32     
    ```
    在上面的配置中，`Redis`将需要持久化的文件划分为`vm-pages`个页，其中每个页所占用的字节为`vm-page-size`，那么 **最终可用的交换文件大小为：`vm-pages * vm-page-size`。**  
    <font color="red">由于一个`value`可以存放在一个或多个页上，但是一个页不能持有多个`value`，鉴于此，我们在设置`vm-page-size`时需要充分考虑`Redis`的该特征。</font>

4. 在`Redis`的配置文件中还有一个非常重要的配置参数，即：
    ```bash
    vm-max-threads 4 
    ```
    该参数表示`Redis`在对交换文件执行`IO`操作时所应用的最大线程数量。  
    通常而言，我们推荐该值等于主机的`CPU cores`（核心数）。如果将该值设置为`0`，那么`Redis`在与交换文件进行`IO`交互时，将以同步的方式执行此操作。

    **注意：** 如果操作交换文件是以同步的方式进行，那么当某一客户端正在访问交换文件中的数据时，其它客户端如果再试图访问交换文件中的数据，该客户端的请求就将被挂起，直到之前的操作结束为止。
    特别是在相对较慢或较忙的磁盘上读取较大的数据值时，这种阻塞所带来的影响就更为明显了。

    **同步操作相对于多线程操作也有优点：** 从全局执行效率视角来看，同步方式要好于异步方式，毕竟同步方式节省了线程切换、线程间同步，以及线程拉起等操作产生的额外开销。
    特别是当大部分频繁使用的数据都可以直接从主内存中读取时，同步方式的表现将更为优异。

## 三、过期清除策略，内存淘汰策略
### 1. 过期清除策略
过期键清除策略有三种，分别是**定时删除**、**定期删除**和**惰性删除。**
* **定时删除：** 是在设置键的过期时间的同时，创建一个定时器，让定时器在键的过期时间来临时，立即执行对键的删除操作；
* **定期删除：** 每隔一段时间，程序就对数据库进行一次检查，删除里面的过期键；
* **惰性删除：** 是指使用的时候，发现`Key`过期了，此时再进行删除。

#### 1.1 定期删除（定期采样删除）
`Redis` 会将每个设置了过期时间的 `key` 放入到一个独立的字典中，以后会定期遍历这个字典来删除到期的 `key`。

`Redis` 默认会每秒进行十次过期扫描（`100ms`一次）， **过期扫描不会遍历过期字典中所有的 `key`，而是采用了一种简单的`贪心策略`** ：
1. 从过期字典中随机 **`20`** 个 `key`；
2. 删除这 **`20`** 个 `key` 中已经过期的 `key`；
3. 如果过期的 `key` 比率超过 `1/4`，那就重复步骤 `1`；

`Redis`默认是每隔 `100ms`就随机抽取一些 **设置了过期时间** 的`key`，检查其是否过期，如果过期就删除。  

**注意这里是随机抽取的。为什么要随机呢？**  
假如 `Redis` 存了 **几十万** 个 `key` ，每隔`100ms`就遍历所有的设置过期时间的 `key` 的话，就会给 `CPU` 带来很大的负载。

#### 1.2 惰性删除
**所谓`惰性策略`就是在客户端访问这个`key`的时候，`Redis`对`key`的过期时间进行检查，如果过期了就立即删除，不会给你返回任何东西。**

定期删除可能会导致很多过期`key`到了时间并没有被删除掉，所以就有了惰性删除。假如你的过期 `key`，靠定期删除没有被删除掉，还停留在内存里，除非你的系统去查一下那个 `key`，才会被删除掉。  
这就是所谓的惰性删除，即当你主动去查过期的`key`时，如果发现`key`过期了，就立即进行删除，不返回任何东西。

#### 1.3 总结
|          | 内存占用         | CPU占用                       | 特征               |
| -------- | ---------------- | ----------------------------- | ------------------ |
| 定时删除 | 节约内存，无占用 | 不分时段占用CPU资源，频度高   | 时间换空间         |
| 惰性删除 | 内存占用严重     | 延时执行，CPU利用率高         | 空间换时间         |
| 定期删除 | 内存定期随机清理 | 每秒花费固定的CPU资源维护内存 | 随机抽查，重点抽查 |

**定期删除是集中处理，惰性删除是零散处理。**  
**<font color="red">`Redis` 过期键采用的是`定期删除 + 惰性删除`二者结合的方式进行删除的。</font>**

### 2. 内存淘汰策略
#### 前言(内存限制)
> `maxmemory`（最大内存容量）
建议必须设置，否则可能将服务器内存占满，造成服务器宕机  
```bash
maxmemory <bytes>
```

**注意事项：**
- <font color="red">`maxmemory`的默认值是`0`</font>，也就是不限制内存的使用；生产环境中根据需求设定，通常设置在`50%`以上。
- `32bit`系统如果使用默认配置或配置为`maxmemory 0`则最大使用`3G`内存。
- `maxmemory`的值没有最小限制（但是如果低于`1MB`，会打一条`WARNING`日志）。
- 如果设置了`maxmemory`选项（值 `>= 1）`，Redis在接收命令时总是会判断当前是否已经超出最大内存限制，如果超过限制会根据驱逐策略去释放内存（如果是同步释放且释放内存很大，则会阻塞其他命令的执行）。
- 单位问题：
    - **maxmemory 100** 裸数字情况：单位是字节。
    - **maxmemory 1K**   K：代表`1000字节`。
    - **maxmemory 1KB** KB：代表`1024字节`。
    - **maxmemory 1M**   M：代表`1000000字节`。
    - **maxmemory 1MB** MB: 代表`1048576字节`。
    - **maxmemory 1G**   G：代表`1000000000字节`。
    - **maxmemory 1GB**  GB: 代表`1073741824字节`。

设置`Redis`可以使用的内存量。一旦到达内存使用上限，`Redis`将会试图移除内部数据，移除规则可以通过`maxmemory-policy`来指定。

#### 2.1 简述

**为什么需要淘汰策略？**  
如果过期键没有被访问（无法触发惰性删除），而周期性删除又跟不上新键产生的速度，内存会被慢慢耗尽；
定期删除还是惰性删除都不是一种完全精准的删除，就还是会存在key没有被删除掉的场景，所以就需要内存淘汰策略进行补充。

内存淘汰策略的配置参数 **`maxmemory_policy`** 决定了内存淘汰策略的策略。**（默认未配置，配置文件中有注释项：`# maxmemory-policy noeviction`）**  
这个参数一共有`8`个枚举值：
* **no-eviction：** 当内存使用超过配置的时候会返回错误，不会驱逐任何键
* **allkeys-lru：** 加入键的时候，如果过限，首先通过`LRU算法`驱逐最久没有使用的键
* **volatile-lru：** 加入键的时候如果过限，首先从设置了过期时间的键集合中驱逐最久没有使用的键
* **allkeys-random：** 加入键的时候如果过限，从所有键随机删除
* **volatile-random：** 加入键的时候如果过限，从过期键的集合中随机驱逐
* **volatile-ttl：** 从配置了过期时间的键中驱逐马上就要过期的键
* **volatile-lfu：** `4.0+`新增配置， 从所有配置了过期时间的键中驱逐使用频率最少的键（对有过期时间的键采用 **`LFU淘汰算法`** ）
* **allkeys-lfu：** `4.0+`新增配置，从所有键中驱逐使用频率最少的键（对全部键采用 **`LFU淘汰算法`** ）

#### 2.2 LRU（Least Recently Used 最近最少使用）算法
##### 2.2.1 标准实现
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis详解/LRU算法.png)
</center>

**实现过程：**  
1. 新增`key/value`的时候首先在`链表`结尾添加`Node节点`，如果超过`LRU`设置的阈值就淘汰队头的节点并删除掉`HashMap`中对应的节点。
2. 修改`key`对应的值的时候先修改对应的`Node`中的值，然后把`Node节点`移动 **队尾** 。
3. 访问`key`对应的值的时候把访问的`Node节点`移动到 **队尾** 即可。

##### 2.2.2 Redis的LRU实现
`Redis`维护了一个`24位时钟`，可以简单理解为当前系统的时间戳，每隔一定时间会更新这个时钟。每个`key对象`内部同样维护了一个`24位的时钟`，当新增`key对象`的时候会把系统的时钟赋值到这个内部对象时钟。  
比如我现在要进行`LRU`，那么首先拿到当前的 **全局时钟** ，然后再找到 **内部时钟**与 **全局时钟** 距离时（间空闲时间）最久的（差最大）进行淘汰，**这里值得注意的是全局时钟只有`24位`，按秒为单位来表示才能存储`194`天，所以可能会出现`key`的时钟大于全局时钟的情况，如果这种情况出现那么就两个相加<font color="red">（加上的key时钟=LRU最大时钟-key时钟）</font>而不是相减来求最久的key。**
```c
// 空闲时间的计算源码
unsigned long long estimateObjectIdleTime(robj *o) {
    unsigned long long lruclock = LRU_CLOCK();
    if (lruclock >= o->lru) {
        // 情况1：全局时钟大于等于key的时钟，计算全局时钟减去key时钟
        return (lruclock - o->lru) * LRU_CLOCK_RESOLUTION;// 当前时间-减去最后一次访问时间的时间戳 就是空闲时间
    } else {
        // 情况2：全局时钟小于key的时钟，计算全局时钟加上设置的LRU最大时钟减去key时钟
        return (lruclock + (LRU_CLOCK_MAX - o->lru)) * LRU_CLOCK_RESOLUTION;
    }
}
```

**`Redis`中的`LRU`与`常规的LRU`实现并不相同，** `常规LRU`会准确的淘汰掉队头的元素，但是`Redis`的`LRU`并不维护队列，只是根据配置的策略要么从所有的`key`中随机选择`N`个（`N`可以配置）要么从所有的设置了过期时间的`key`中选出`N个键`，然后再从这`N个键`中选出最久没有使用的一个`key`进行淘汰。

##### 2.2.3 为什么Redis要使用近似LRU？
1. **性能问题：** 由于近似LRU算法只是最多随机采样`N个key`并对其进行排序，如果精准需要对`所有key`进行排序，这样`近似LRU` **性能更高**
2. **内存占用问题：** Redis对内存要求很高，会尽量降低内存使用率，**如果是抽样排序可以有效降低内存的占用**
3. **实际效果基本相等：** **如果请求符合长尾法则（`80%`请求会落到`20%`的热点数据上）**，那么`常规LRU`与`Redis LRU`之间表现基本无差异
4. **在近似情况下提供可自配置的取样率来提升精准度：** 例如通过 **`CONFIG SET maxmemory-samples <count>`** 指令可以设置取样数，<font color="red">**取样数越高越精准**</font>，如果你的`CPU`和`内存`有足够，可以提高取样数看命中率来探测最佳的采样比例。

#### 2.3 LFU（Least Frequently Used，最不常用的）算法
`LFU`是在`Redis4.0`后出现的， **`LRU算法`的最近最少使用实际上并不精确** ，考虑下面的情况，如果在 **`|`** 处删除，那么`A`距离的时间最久，但实际上A的使用频率要比`B`频繁，所以合理的淘汰策略应该是淘汰`B`。`LFU`就是为应对这种情况而生的。
```
A~~A~~A~~A~~A~~A~~A~~A~~A~~A~~~|
B~~~~~B~~~~~B~~~~~B~~~~~~~~~~~B|
```
**`LFU`把原来的`key对象`的内部时钟的`24位`分成两部分，`前16位`还代表时钟，`后8位`代表一个`计数器`。**  
`16位`的情况下如果还按照`秒`为单位就会导致不够用，所以一般这里以`时`为单位。而`后8位`表示当前key对象的 **访问频率** ，`8位`只能代表`255`，但是`Redis`并没有采用线性上升的方式，而是通过一个复杂的公式，通过配置两个参数来调整数据的递增速度。

下图从左到右表示`key`的 **命中次数** ，从上到下表示 **影响因子** ，在 **影响因子** 为`100`的条件下，经过`10M`次命中才能把`后8位`值加满到`255`：
```
# +--------+------------+------------+------------+------------+------------+
# | factor | 100 hits   | 1000 hits  | 100K hits  | 1M hits    | 10M hits   |
# +--------+------------+------------+------------+------------+------------+
# | 0      | 104        | 255        | 255        | 255        | 255        |
# +--------+------------+------------+------------+------------+------------+
# | 1      | 18         | 49         | 255        | 255        | 255        |
# +--------+------------+------------+------------+------------+------------+
# | 10     | 10         | 18         | 142        | 255        | 255        |
# +--------+------------+------------+------------+------------+------------+
# | 100    | 8          | 11         | 49         | 143        | 255        |
# +--------+------------+------------+------------+------------+------------+
```
```c
  uint8_t LFULogIncr(uint8_t counter) {
      if (counter == 255) return 255;
      double r = (double)rand()/RAND_MAX;
      double baseval = counter - LFU_INIT_VAL;
      if (baseval < 0) baseval = 0;
      double p = 1.0/(baseval*server.lfu_log_factor+1);
      if (r < p) counter++;
      return counter;
  }
```
```bash
# 可以调整计数器counter的增长速度，lfu-log-factor越大，counter增长的越慢。
lfu-log-factor 10
# 衰减因子：是一个以分钟为单位的数值，可以调整counter的减少速度
lfu-decay-time 1
```
上面说的情况是`key`一直被命中的情况，如果一个`key`经过几分钟没有被命中，那么`后8位`的值是需要 **递减几分钟** ，具体递减几分钟根据衰减因子 **`lfu-decay-time`** 来控制，源码如下：
```c
unsigned long LFUDecrAndReturn(robj *o) {
    unsigned long ldt = o->lru >> 8;
    unsigned long counter = o->lru & 255;
    unsigned long num_periods = server.lfu_decay_time ? LFUTimeElapsed(ldt) / server.lfu_decay_time : 0;
    if (num_periods)
        counter = (num_periods > counter) ? 0 : counter - num_periods;
    return counter;
}
```
* 上面递增和衰减都有对应参数配置，那么对于新分配的`key`呢？  
    **如果新分配的`key`计数器开始为`0`，那么很有可能在`内存不足`的时候直接就给淘汰掉了，所以默认情况下新分配的`key`的`后8位`计数器的值为`5`（应该可配置），防止`新key`因为访问频率过低而直接被删除。**
* `低8位`我们描述完了，那么`高16位`的时钟是用来干嘛的呢？  
    **剩下的`16位`另作它用：用于`计数值`的衰减。** 上面说的Redis配置项 **`server.lfu_decay_time`** ，也是用于控制计数的衰减的，计数衰减的周期长度，单位是分钟。**当时间过去一个周期，计数值就会`减1`。**  
    衰减时间默认是`1`，它是计数器应该衰减的分钟数，长时间不读取`key`的话，是需要进行衰减的，当每次采样发现时计数器的时间比这个值要大。有一个特殊的值 ，`0` 表示每次扫描时计数器总是衰减，很少用到。

**计数器对数因子改变了需要多少次命中才能使频率计数器饱和，而频率计数器刚好在 0-255 范围内。因子越大，为了达到最大，需要的访问次数越多。因子越低，低访问的计数器分辨率越好。**

## 四、数据类型及其应用场景
[官网文档：Redis数据类型](https://redis.io/docs/manual/data-types/)  
[Redis常见命令说明及使用方式](https://www.redis.net.cn/order/)

`Redis`大致分为`5`种数据对象，分别是`String`、`List`、`Hash`、`Set`、`Zset`。底层实现依托于`sds`、`ziplist`、`skiplist`、`dict`等更基础数据结构。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis详解/Redis支持的数据类型.png)
</center>

### 1. string
#### 1.1 介绍：
`string` 数据结构是简单的 `key-value` 类型。虽然 `Redis` 是用 `C 语言`写的，但是 `Redis` 并没有使用 `C` 的字符串表示，而是自己构建了一种 **简单动态字符串（`simple dynamic string，SDS`）**。

**<font color="red">`Redis`的字符串如果保存的对象是整数类型，那么就用`int`存储。如果不能用整数表示，就用`SDS`来表示； `SDS`通过记录长度，和`预分配空间`，可以高效计算长度，进行`append`操作（动态增加，类比`java`里面的`StringBuffer`的`append`方法）。</font>**

相比于 `C` 的原生字符串，`Redis` 的 `SDS` 不光可以保存文本数据还可以保存二进制数据，并且获取字符串长度复杂度为 `O(1)`（C 字符串为` O(N)`），**除此之外，`Redis` 的 `SDS API` 是安全的，不会造成`缓冲区溢出`。**

#### 1.2 常用命令：
`set`，`get`，`strlen`，`exists`，`decr`，`incr`，`setex` 等等。

#### 1.3 应用场景：
一般常用在需要计数的场景，比如用户的访问次数、热点文章的点赞转发数量、常用热点数据（`json`串或其他形式存储）等等。

#### 1.4 常用操作：
##### (1) 普通字符串的基本操作：
```java
127.0.0.1:6379> set key value #设置 key-value 类型的值
OK
127.0.0.1:6379> get key       # 根据 key 获得对应的 value
"value"
127.0.0.1:6379> exists key    # 判断某个 key 是否存在
"1"
127.0.0.1:6379> strlen key    # 返回 key 所储存的字符串值的长度。
"5"
127.0.0.1:6379> del key       # 删除某个 key 对应的值
"1"
127.0.0.1:6379> get key
null                        
```

##### (2) 批量设值与取值：
```java
127.0.0.1:6379> mset key1 value1 key2 value2  # 批量设置 key-value 类型的值
OK
127.0.0.1:6379> mget key1 key2                # 批量获取多个 key 对应的 value
1) "value1"
2) "value2"
```

##### (3) 计数器（字符串的内容为整数的时候可以使用）：
```java
127.0.0.1:6379> set number 1
"OK"
127.0.0.1:6379> incr number  # 将 key 中储存的数字值增一
"2"
127.0.0.1:6379> get number
"2"
127.0.0.1:6379> decr number  # 将 key 中储存的数字值减一
"1"
127.0.0.1:6379> get number
"1"
```

##### (4) 过期（不设置则默认为永不过期）:
```java
192.168.1.213:0>set key testValue
"OK"
127.0.0.1:6379> expire key  60      # 数据在 60s 后过期
"1"
127.0.0.1:6379> setex key 60 value  # 数据在 60s 后过期 (setex:[set] + [ex]pire)
"OK"
127.0.0.1:6379> ttl key             # 查看数据还有多久过期
"54"
```

### 2. list
#### 2.1 介绍：
**`list` 即链表。**  
链表是一种非常常见的数据结构，特点是易于数据元素的插入和删除并且可以灵活调整长度，但是链表的随机访问困难。  
**许多高级编程语言都内置了链表的实现，比如 `Java` 中的 `LinkedList`。由于`C 语言`并没有实现链表，所以 `Redis` 实现了自己的链表数据结构。**  
`Redis` 的 `list` 的实现为一个 <font color="red">双向链表</font>，即可以支持反向查找和遍历，更方便操作，不过带来了部分额外的 **内存开销** 。

#### 2.2 常用命令：
`rpush`，`rpop`，`lpop`，`lpush`，`lrange`，`llen` 等。

#### 2.3 应用场景：
消息的`发布`与`订阅`或者`消息队列`、`慢查询处理`。

#### 2.4 常用操作：
`rpush`，`rpop`，`lpop`，`lpush`的操作图解
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis详解/Redis-list类型原理图示.png)
</center>

##### (1) 通过 `rpush/rpop` 实现栈（先进后出，后进先出）：
```java
127.0.0.1:6379> rpush myList2 value1 value2 value3
"3"
127.0.0.1:6379> rpop myList2        # 将 list的头部(最右边)元素取出
"value3"
```

##### (2) 通过 `rpush/lpop` 实现队列：
```java
127.0.0.1:6379> rpush myList value1         # 向 list 的头部（右边）添加元素
"1"
127.0.0.1:6379> rpush myList value2 value3  # 向list的头部（最右边）添加多个元素
"3"
127.0.0.1:6379> lpop myList                 # 将 list的尾部(最左边)元素取出
"value1"
127.0.0.1:6379> lrange myList 0 1           # 查看对应下标的list列表，0为 start，1为end（通过 lrange 命令，可以实现基于list的分页查询）
1) "value2"
2) "value3"
127.0.0.1:6379> lrange myList 0 -1          #查看列表中的所有元素，-1表示倒数第一
1) "value2"
2) "value3"
```

**但是`Redis`并不适合做消息队列。因为`Redis`本身没有支持`AMQP(Advanced Message Queuing Protocol)`协议[AMQP协议详解](https://www.zhihu.com/topic/20138354/top-answers)，消息队列该有的能力不足，消息`可靠性`不强。**

### 3. hash
#### 3.1 介绍：
**`hash` 类似于 `JDK1.8前`的 `HashMap`，内部实现也差不多(`数组` + `链表`)。**  
**`Redis`的`hash`（`dict`+`字典`） 是一个 `string` 类型的`dictht`（键：等同于`HashMap`的`数组`） 和 `dictEntry`（值：存储键值对。等同于`HashMap`的`链表`）的映射表** ，特别适合用于存储对象，后续操作的时候，你可以直接仅仅修改这个对象中的某个字段的值。比如可以 `hash` 数据结构来存储用户信息、商品信息等等。

#### 3.2 常用命令：
`hset`，`hmset`，`hexists`，`hget`，`hgetall`，`hkeys`，`hvals` 等。

#### 3.3 应用场景：
系统中对象数据的存储。

#### 3.4 常用操作：
```java
127.0.0.1:6379> hmset userInfoKey name "admin" desc "dev" age "100"
"OK"
127.0.0.1:6379> hexists userInfoKey name    # 查看 key 对应的 value中指定的字段是否存在。
"1"
127.0.0.1:6379> hget userInfoKey name       # 获取存储在哈希表中指定字段的值。
"admin"
127.0.0.1:6379> hget userInfoKey age
"100"
127.0.0.1:6379> hgetall userInfoKey         # 获取在哈希表中指定 key 的所有字段和值
1) "name"
2) "admin"
3) "desc"
4) "dev"
5) "age"
6) "100"
127.0.0.1:6379> hkeys userInfoKey           # 获取 key 列表
1) "name"
2) "desc"
3) "age"
127.0.0.1:6379> hvals userInfoKey           # 获取 value 列表
1) "admin"
2) "dev"
3) "100"
127.0.0.1:6379> hset userInfoKey name "zhangsan" # 修改某个字段对应的值
"0"
127.0.0.1:6379> hget userInfoKey name
"zhangsan"
```
#### 3.5 hash的扩容和收缩机制
在 `Java` 中 `HashMap` 扩容是个很耗时的操作，需要去申请新的数组，为了追求高性能，**而`Redis` 采用了<font color="red">渐进式 `rehash`</font> 策略** ，`rehash`操作的时候，`rehash`动作是分多次，渐进式的完成的，将`rehash键值对`所需要的计算工作均摊到字典的每个添加、删除、查找和更新操作上，从而避免了集中式`rehash`而带来的庞大计算量。

**<font color="red">这也是 `Redis hash` 中最重要的部分。</font>**

##### (1) 执行hash扩容/收缩的时机
**扩容**
* 服务器目前<font color="red">没有在执行</font> **BGSAVE（持久化）** 命令或者 **`BGREWRITEAOF`(用于异步执行一个 `AOF` 文件重写操作)** 命令，并且哈希表的负载因子大于等于 **`1`** 。
* 服务器目前<font color="red">正在执行</font> BGSAVE命令或者`BGREWRITEAOF`命专，并且哈希表的`负载因子`大于等于 **`5`** 。

区分这两种情况时因为执行`BGSAVE`与`BGREWRITEAOF`过程中，`Redis`都需要创建子进程，而大多数操作系统都采用写时复制技术来优化子进程使用效率，所以在子进程存在期间，服务器会提高执行扩展操作所需的**负载因子**，从而尽可能避免在子进程存在期间进行哈希表扩展操作，这可以避免不必要的内存写入，最大限度的节约空间。

**收缩**
* 当哈希表的`负载因子`小于`0.1`时，`Redis`会自动开始对哈希表进行缩容操作。

**其中哈希表的`负载因子`可以通过公式：<font color="red">`负载因子 = 哈希表已保存节点数量 / 哈希表大小`（`load_factor = ht[0].used / ht[0].size`）</font>**  
如：对于一个大小为`4`，包含`4个键值对`的哈希表来说，这个哈希表的负载因子为： **`load_factor - 4 /4 =1`**

##### (2) 扩容/收缩原理（过程）
`hash`的扩容通过执行 **`rehash`(重新散列)** 操作来完成。  

**当周期函数发现当前`装载因子`超过`阈值`时就会进行`Rehash`。Rehash的流程大概分成三步：**
1. 生成`新Hash表ht[1]`，为 `ht[1]` 分配空间 **（扩容时大小为`ht[0].used x 2的2^n` (2的n次方幂)；收缩时大小为`ht[0].used的2^n` (2的n次方幂)）** 。  
    此时字典同时持有`ht[0]`和`ht[1]`两个哈希表。**字典的偏移索引从静默状态 -1 ，设置为 0 ，表示Rehash 工作正式开始。**
2. 迁移`ht[0]`数据到`ht[1]`。  
    在 Rehash进行期间，每次对字典执行增删查改操作，程序会顺带迁移一个`ht[0]`上的数据，并更新 **偏移索引** 。与此同时，周期函数也会定时迁移一批。
3. `ht[1]`和`ht[0]` **指针对象** 交换。  
    随着字典操作的不断执行，最终在某个时间点上，`ht[0]`的所有键值对都会被Rehash至 `ht[1]`，此时再将`ht[1]`和`ht[0]` **指针对象** 互换，**同时把偏移索引的值设为-1，表示Rehash操作已完成。**

<font color="red">**注意：rehash后新生成的`ht[1]`的节点数组大小等于超过当前`ht[0]中`使用的key个数`向上求整的2 x 2^n` （扩容）或者`2^n` （收缩）。**</font>  
如：当前`ht[0]`以使用的key个数为`100`
* <font color="red">扩容：`100 x 2 = 200`，大于等于`200的2^n` 为`256即2^8`，所以 **扩容** 后的`ht[1]`的数组大小为`256`</font>
* <font color="red">收缩：大于等于`100的2^n` 为`128即2^7`，所以 **收缩** 后`ht[1]`的数组大小为`128`</font>

**注意：`rehash`时，对数据的增删改查的操作：**
* **新增Key：** 是往`ht[1]`里面插入。
* **读请求：** 先从`ht[0]`找，没找到再去`ht[1]`找。
* **删除和更新：** 其实本质是先找到位置，再进行操作，所以和读请求一样，先找`ht[0]`，不存在的时候再找`ht[1]`，找到之后再进行删改操作。

### 4. set
#### 4.1 介绍：
**`set` 类似于 `Java` 中的 `HashSet` 。**  
`Redis` 中的 `set` 类型是一种**无序集合**，集合中的元素没有先后顺序。当你需要存储一个列表数据，又不希望出现重复数据时，`set` 是一个很好的选择，并且 `set` 提供了判断某个成员是否在一个 `set` 集合内的重要接口，这个也是 `list` 所不能提供的。  

**可以基于 `set` 轻易实现交集、并集、差集的操作。  
比如：你可以将一个用户所有的关注人存在一个集合中，将其所有粉丝存在一个集合。`Redis` 可以非常方便的实现如共同关注、共同粉丝、共同喜好等功能。  
这个过程也就是求交集的过程。**

#### 4.2 常用命令：
`sadd`，`spop`，`smembers`，`sismember`，`scard`，`sinterstore`，`sunion`，`sdiff`等。

#### 4.3 应用场景：
需要存放的数据不能重复；需要获取多个数据源交集或并集等场景。

#### 4.4 常用操作：
```java
127.0.0.1:6379> sadd mySet value1 value2    # 添加元素进去
"2"
127.0.0.1:6379> sadd mySet value1           # 不允许有重复元素
"0"
127.0.0.1:6379> smembers mySet              # 查看 set 中所有的元素
1) "value1"
2) "value2"
127.0.0.1:6379> scard mySet                 # 查看 set 的长度
"2"
127.0.0.1:6379> sismember mySet value1      # 检查某个元素是否存在set 中，只能接收单个元素
"1"
127.0.0.1:6379> sismember mySet value3
"0"
127.0.0.1:6379> sadd mySet2 value2 value3
"2"
127.0.0.1:6379> sunion mySet2 value2 value3 # 获取两个 set 集合的并集
1)  "value2"
2)  "value3"
3)  "value1
"127.0.0.1:6379> sdiff mySet2 value2 value3 # 获取两个 set 集合的交集（差集）
1)  "value2"
127.0.0.1:6379> sinterstore mySet3 mySet mySet2     # 获取 mySet 和 mySet2 的交集并存放在 mySet3 中
"1"
127.0.0.1:6379> smembers mySet3
1) "value2"
```

### 5. Zset（sorted set）
#### 5.1 介绍：
和 `set` 相比，`sorted set` 增加了一个权重参数 **`score`** ，使得集合中的元素能够 **按 `score` 进行有序排列，还可以通过 `score` 的范围来获取元素的列表。**

**有点像是 `Java` 中 `HashMap` 和 `TreeSet` 的结合体。**

#### 5.2 常用命令：
`zadd`，`zcard`，`zscore`，`zrange`，`zrevrange`，`zrem`等。

#### 5.3 应用场景：
需要对数据根据某个权重进行排序的场景。比如推荐商品的排序展示等场景。

#### 5.4 常用操作：
```java
127.0.0.1:6379> zadd myZset 3.0 value1          # 添加元素到 sorted set 中 3.0 为权重
"1"
127.0.0.1:6379> zadd myZset 2.0 value2 1.0 value3 # 一次添加多个元素
"2"
127.0.0.1:6379> zcard myZset                    # 查看 sorted set 中的元素数量
"3"
127.0.0.1:6379> zscore myZset value1            # 查看某个 value 的权重
"3"
127.0.0.1:6379> zrange  myZset 0 -1             # 顺序输出某个范围区间的元素，0 -1 表示输出所有元素
1) "value3"
2) "value2"
3) "value1"
127.0.0.1:6379> zrange  myZset 0 1              # 顺序输出某个范围区间的元素，0 为 start  1 为 stop
1) "value3"
2) "value2"
127.0.0.1:6379> zrevrange  myZset 0 1           # 逆序输出某个范围区间的元素，0 为 start  1 为 stop
1) "value1"
2) "value2"
```
#### 5.5 Zset实现（ziplist 、 字典 + 跳表(skiplist)）
`zset`对象的存储方式有两种，分别是`ziplist`和`字典+跳表(skiplist)`。

##### (1) ziplist
**简介：**  
`ziplist`是一个经过特殊编码的`双向链表`，它的设计目标就是为了提高存储效率。  
`ziplist`可以用于存储字符串或整数，其中整数是按真正的二进制表示进行编码的，而不是编码成字符串序列。它能以`O(1)`的时间复杂度在表的两端提供`push`和`pop`操作。

**ziplist和普通双向链表的区别：**
一个普通的`双向链表`，链表中每一项都占用独立的一块内存，各项之间用`地址指针`（或引用）连接起来。这种方式会带来大量的内存碎片，而且地址指针也会占用额外的内存。  
<font color="red">而`ziplist`却是将表中每一项存放在前后连续的地址空间内，一个`ziplist`整体占用一大块内存。它更像是一个表（`list`），但其实不是一个链表（`linked list`）。</font>

##### (2) 字典（dict） + 跳表（SkipList）
**字典概念：**  
`dict`用来查询数据到分数的对应关系，而`skiplist`用来根据分数查询数据（也可能是范围查找）

**跳表概念：**  
`跳表`本质上是对`链表`的一种优化，通过逐层跳步采样的方式构建索引，以加快查找速度。  
如果只用普通链表，只能一个一个往后找。跳表就不一样了，可以高层索引（每一个节点指向多个后续节点），一次跳跃多个节点，如果找过头了，就用更下层的索引。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/数据库/Redis/Redis详解/Redis-zset跳表原理图示.png)
</center>

**每个节点的层高（即指向多少个后续节点）：**  
使用概率均衡的思路，确定新插入节点的层数。Redis使用随机函数决定层数。直观上来说，默认`1`层，和丢硬币一样，如果是正面就继续往上，这样持续迭代，最大层数`32`层。
- `50%`的概率被分配到第一层
- `25%`的概率被分配到第二层
- `12.5%`的概率被分配到第三层
- 依次类推.....

这种方式保证了越上层数量越少，自然跨越（查找）起来越方便（这种结构跟平衡树有点像）。

##### (3) 总结
**ziplist 、 字典 + 跳表(skiplist)不同的适用场景：**
* **当数据较少时**，zset是由`ziplist`来实现的。
* **当数据多的时候**，zset是由`dict` + `skiplist`来实现的。

**`ziplist`和`skiplist`的区别：**
`ziplist`节省内存，但是增删改查等操作较慢，而`skiplist`正好相反，增删改查非常快，但是相比`ziplist`会占用更多内存。  
因此`Redis`在保存`zset`时按如下的规则进行选择：
* 当`元素个数超过128`或`最大元素的长度超过64`时用`skiplist`，
* 其他情况下用`ziplist`，并且每次对zset进行插入、删除元素时都会重新判断是否需要转换保存格式。

**为什么同时需要字典和跳表来实现？**  
`Zset`是一个有序列表，当数据量大了之后，字典和跳表的组合分别可以对应两种查询场景，**字典用来支持按成员查询数据，跳表则用以实现高效的范围查询，** 这样两个场景，性能都做到了极致。

### 7. 其他特殊结构（高级结构）
在5中基础的数据类型的基础上，还有5中特殊的数据类型，分别是：**bitmap，hyperLogLog，bloomFilter，GeoHash，Stream**

#### 7.1 bitmap
##### 7.1.1 介绍：
**`bitmap` 存储的是连续的二进制数字（`0` 和 `1`）**，通过 `bitmap`, 只需要一个 **`bit`** 位来表示某个元素对应的值或者状态，`key` 就是对应元素本身 。

我们知道 `8 个 bit` 可以组成一个 `byte`，所以 `bitmap` 本身会极大的节省储存空间。

##### 7.1.2 常用命令：
`setbit`，`getbit`，`bitcount`，`bitop`等。

##### 7.1.3 应用场景：
适合需要保存状态信息（比如是否签到、是否登录...）并需要进一步对这些信息进行分析的场景。比如用户签到情况、活跃用户情况、用户行为统计（比如是否点赞过某个视频）。

##### 7.1.4 常用操作：
```java
127.0.0.1:6379> setbit mykey 7 1
"0"
127.0.0.1:6379> setbit mykey 7 0
"1"
127.0.0.1:6379> getbit mykey 7
"0"
127.0.0.1:6379> setbit mykey 6 1
"0"
127.0.0.1:6379> setbit mykey 8 1
"0"
127.0.0.1:6379> bitcount mykey      # 通过 bitcount 统计被被设置为 1 的位的数量。
"2"
```
#### 7.2 其他特殊类型查看官网文档
[官方文档：Redis数据类型](https://redis.io/docs/manual/data-types/)

### 8. 其他应用场景及实现
Redis主要应用场景为：热点数据缓存、定时操作、分布式锁、秒杀、限流等

#### 1）热点数据的缓存
由于Redis访问速度块、支持的数据类型比较丰富，所以Redis很适合用来存储热点数据；另外结合`expire`，我们可以设置过期时间然后再进行缓存更新操作，这个功能最为常见，我们几乎所有的项目都有所运用。  
如：用户的登录信息（token），App首页加载的不需要要实时更新的数据

#### 2）限时业务的运用
Redis中可以使用`expire`命令设置一个键的生存时间，到时间后Redis会删除它。利用这一特性可以运用在限时的优惠活动信息、手机验证码等业务场景。

#### 3）计数器相关问题
Redis由于 **`string`** 类型的 **`incrby`** 命令可以实现 **原子性的递增** ，所以可以运用于高并发的秒杀活动、分布式序列号的生成。  
具体业务还体现在比如限制一个手机号发多少条短信、一个接口一分钟限制多少请求、一个接口一天限制调用多少次等。

#### 4）排行榜相关问题
关系型数据库在排行榜方面查询速度普遍偏慢，所以可以借助Redis的 **SortedSet** 进行热点数据的排序（同时还可以排行分页等）。

#### 5）分布式锁
这个主要利用Redis的 **`setnx`** 命令进行，<font color="red">**`setnx："set if not exists"`**</font> 就是如果不存在则成功设置缓存同时返回`1`，否则返回`0`。  
当服务器是集群时，定时任务可能在两台机器上都会运行，所以在定时任务中首先 通过`setnx`设置一个`lock`，如果成功设置则执行，如果没有成功设置，则表明该定时任务已执行。  
这个特性也可以运用于其他需要分布式锁的场景中， **结合过期时间主要是防止死锁的出现** 。

#### 6）延时操作（订单支付过期等场景）
可以利用 **`ZSet`** 。我们可以把任务的描述序列化成字符串，放在 `ZSet` 的 `value` 中，然后把任务的执行时间戳作为 `score`，利用 `ZSet` 天然的排序特性，执行时刻越早的会排在越前面。

开一个或多个定时线程，每隔一段时间去查一下这个 `ZSet` 中 `score` 小于或等于当前时间戳的元素(通过 **`zrangebyscore`** 命令实现)，然后再执行元素对应的任务即可。**当然，执行完任务后，还要将元素从 `ZSet` 中删除，避免任务重复执行。**

如果是多个线程去轮询这个 `ZSet`，还有考虑并发问题，假如一个任务到期了，也被多个线程拿到了，这个时候必须保证只有一个线程能执行这个任务，这可以通过 `zrem` 命令来实现，只有删除成功了，才能执行任务，这样就能保证任务不被多个任务重复执行了。

**当然我们也可以利用`rabbitmq`、`activemq`等消息中间件的延迟队列服务实现该需求。**

#### 7）分页查询
Redis的 **`Zset(sorted set)`** 集合中提供了一个 **`zrange`（顺序）、`zrevrange`（逆序）** 方法，语法如下：
```java
zrange key min max 
```
**返回`key`对应的`set`中`[min,max]`的数据，当`min=0，max=-1`时即返回所有**

#### 8）队列/栈
由于Redis有`list push`和`list pop`这样的命令，所以能够很方便的执行队列和栈的操作。
* 通过 `rpush/lpop` 实现队列
* 通过 `rpush/rpop` （或`lpush/lpop`）实现栈（先进后出，后进先出）：

#### 9）消息的发布/订阅
**命令：**
* `psubscribe pattern [pattern ...]`：订阅一个或多个符合给定模式的频道。
* `pubsb subcommand [argument [argument ...]]`：查看订阅与发布系统状态。
* `publish channel message`：将信息发送到指定的频道。
* `punsubscribe [pattern [pattern ...]]`：退订所有给定模式的频道。
* `subscribe channel [channel ...]`：订阅给定的一个或多个频道的信息
* `unsubscribe [channel [channel ...]]`：指退订给定的频道。

**简单实现：**  
`客户端1`：创建了订阅频道
```java
127.0.0.1:6379> subscribe c1 c2
Reading messages... (press Ctrl-C to quit)
1) "subscribe"      # 订阅反馈
2) "c1"             # 订阅的频道
3) (integer) 1      # 目前客户端已订阅频道/模式的数量
1) "subscribe"
2) "c2"
3) (integer) 2
```

`客户端2`：向`频道c1`发送消息
```java
127.0.0.1:6379> publish c1 first
(integer) 1
```

`客户端1`：接收到`客户端2`发送的消息
```java
127.0.0.1:6379> subscribe c1 c2
Reading messages... (press Ctrl-C to quit)
1) "subscribe"      # 订阅反馈
2) "c1"             # 订阅的频道
3) (integer) 1      # 目前客户端已订阅频道/模式的数量
1) "subscribe"
2) "c2"
3) (integer) 2
1) "message"        # 消息
2) "c1"             # 接收的频道
3) "first"          # 消息内容
```

`客户端3`：新建一个`客户端3`，订阅`频道c1`
```java
127.0.0.1:6379> subscribe c1
Reading messages... (press Ctrl-C to quit)
1) "subscribe"      
2) "c1"             
3) (integer) 1      
```
`客户端3`并没有接收到消息：说明订阅频道，不能接收到之前发送的消息

**`Redis发布订阅`与`ActiveMQ`的比较**
* `ActiveMQ`支持多种消息协议，包括 **`AMQP`、`MQTT`、`Stomp`** 等，并且支持JMS规范，<font color="red">但Redis没有提供对这些协议的支持</font>；
* `ActiveMQ`提供持久化功能，但 **<font color="red">Redis无法对消息持久化存储</font>**，一旦消息被发送，不管有没有订阅者接收，那么消息就会丢失；
* `ActiveMQ`提供了消息传输保障，当客户端连接超时或事务回滚等情况发生时，消息会被重新发送给客户端，<font color="red">Redis没有提供消息传输保障</font>。 

## 五、事务
[Redis 官网相关介绍](https://redis.io/topics/transactions)

详见其他笔记 —— [《Redis事务》](https://xieruhua.gitee.io/javalearning/#/./%E6%95%B0%E6%8D%AE%E5%BA%93/Redis/Redis%E4%BA%8B%E5%8A%A1)

## 六、雪崩、穿透、击穿
详见其他笔记 —— [《缓存击穿、穿透、雪崩-概念及处理方式》](https://xieruhua.gitee.io/javalearning/#/./%E6%95%B0%E6%8D%AE%E5%BA%93/Redis/%E7%BC%93%E5%AD%98%E5%87%BB%E7%A9%BF%E3%80%81%E7%A9%BF%E9%80%8F%E3%80%81%E9%9B%AA%E5%B4%A9%E7%9A%84%E6%A6%82%E5%BF%B5%E5%8F%8A%E5%A4%84%E7%90%86%E6%96%B9%E5%BC%8F)

## 七、数据持久化
`Redis`跟`memcache`区别之一，储存在`Redis`中的数据是持久化的，断电或重启后，数据也不会丢失。（`memcache`则是直接存储在内存中，断电或重启则数据全部消息）  
很多时候我们需要持久化数据也就是将内存中的数据写入到硬盘里面，大部分原因是为了之后重用数据（比如重启机器、机器故障之后恢复数据），或者是为了防止系统故障而将数据备份到一个远程位置。

**Redis持久化的方式有两种：`RDB`和`AOF`**

### 1. RDB（Redis database）
`RDB`（快照持久化）是`Redis`的二进制快照文件，优点是文件紧凑，占用空间小，恢复速度比较快。同时，由于是子进程`Fork`的模式，对`Redis`本身读写性能的影响很小。  
**<font color="red">`RDB`是 `Redis` 默认采用的持久化方式</font>**

**Redis 可以通过创建快照来获得存储在内存里面的数据在某个时间点上的副本。**   
创建快照之后，可以对快照进行备份，可以将快照复制到其他服务器从而创建具有相同数据的服务器副本（`Redis` 主从结构，主要用来提高 `Redis` 性能），还可以将快照留在原地以便重启服务器的时候使用。

#### 1.1 RDB持久化的三种机制
`RDB`提供了三种机制： **`save`、`bgsave`、`自动触发`。**

##### 1.1.1 save
该命令会阻塞当前Redis服务器，执行`save`命令期间，`Redis`不能处理其他命令，直到`RDB`过程完成为止。  
执行完成时候如果存在老的`RDB`文件，旧的文件会被覆盖。  

**在实际开发中，客户端数据可能都是几万或者是几十万，这种方式显然不可取。**

##### 1.1.2 bgsave
执行该命令时，`Redis`会在后台异步进行快照操作，快照同时还可以响应客户端请求。  
具体操作是`Redis`进程执行`fork`操作创建子进程，`RDB`持久化过程由子进程负责，完成后自动结束。阻塞只发生在`fork`阶段，一般时间很短。  

**基本上 `Redis` 内部所有的`RDB操作`都是采用 `bgsave` 命令。**

##### 1.1.3 自动触发
自动触发是由我们的配置文件来完成的。在 **Redis.conf** 配置文件中，里面有如下配置：  
1. **save：** 是用来配置触发 Redis的 `RDB` 持久化条件，也就是什么时候将内存中的数据保存到硬盘。如 **`“save m n”`（表示`m秒内`数据集存在`n次修改`时，自动触发`bgsave`操作）** 。   
默认有如下配置：  （三选一或自行配置）：
    ```bash
    # 在900秒(15分钟)之后，如果至少有1个key发生变化，Redis就会自动触发BGSAVE命令创建快照。
    save 900 1 

    # 在300秒(5分钟)之后，如果至少有10个key发生变化，Redis就会自动触发BGSAVE命令创建快照。
    save 300 10  

    # 在60秒(1分钟)之后，如果至少有10000个key发生变化，Redis就会自动触发BGSAVE命令创建快照。
    save 60 10000       
    ```
若不需要持久化，可以注释掉所有的 `save` 行来停用保存功能。
2. **stop-writes-on-bgsave-error ：** 默认值为`yes`。即当启用了`RDB`且最后一次后台保存数据失败，`Redis`是否停止接收数据。这会让用户意识到数据没有正确持久化到磁盘上，否则没有人会注意到灾难发生了。**如果Redis重启了，那么又可以重新开始接收数据了**   
3. **rdbcompression：** 默认值是`yes`。对于存储到磁盘中的快照，可以设置是否进行压缩存储。
4. **rdbchecksum：** 默认值是`yes`。在存储快照后，我们还可以让`Redis`使用`CRC64算法`来进行数据校验，但是这样做会增加大约`10%`的性能消耗，如果希望获取到最大的性能提升，可以关闭此功能。
5. **dbfilename：** 设置快照的文件名，默认是 **dump.rdb** 
6. **dir：** 设置快照文件的存放路径，这个配置项一定是个目录，而不能是文件名。

#### 1.2 RDB的优缺点
**优点：**
* RDB文件紧凑，全量备份，非常适合用于进行备份和灾难恢复。
* RDB文件生成的时候，`Redis`主进程会`fork()一个子进程`来处理所有保存工作，主进程不需要进行任何磁盘`IO`操作。
* RDB 在恢复大数据集时的速度比 `AOF` 的恢复速度要快。

**缺点：**  
当进行快照持久化时，会开启一个子进程专门负责快照持久化，子进程会拥有父进程的内存数据，父进程修改内存子进程不会反应出来，所以在快照持久化期间修改的数据不会被保存，可能丢失数据。

### 2. AOF（append only file）
全量备份总是耗时的，有时候我们提供一种更加高效的方式`AOF`，工作机制很简单，`Redis`会将每一个收到的写命令都通过`write函数`追加到文件中（可以重放请求恢复现场）。  
通俗的理解就是日志记录，所以`AOF文件`会比`RDB文件`大很多，`AOF`的优点是故障情况下，丢失的数据会比`RDB`更少。

#### 2.1 开启AOF
默认情况下 `Redis` 没有开启 `AOF`，可以通过 **`appendonly`** 参数开启：
```bash
appendonly yes
```
`AOF文件`的保存位置和 `RDB 文件`的位置相同，都是通过 `dir` 参数设置的，默认的文件名是 **`appendonly.aof`** 。

#### 2.2 持久化模式
出于性能考虑，如果开启了`AOF`，会将命令先记录在`AOF缓冲区`，之后再刷入磁盘。数据刷入磁盘的时机根据参数决定，有三种模式：
```bash
appendfsync always    # 执行命令后立刻触：每次有数据修改发生时都会写入AOF文件,这样会严重降低Redis的速度
appendfsync everysec  # 每秒定期刷入： 每秒钟同步一次，显示地将多个写命令同步到硬盘
appendfsync no        #关闭时刷入：让操作系统决定何时进行同步
```
**如果是执行命令后立马刷入，`AOF`会拖累执行速度，所以一般都是配置为<font color="red">每秒定期刷入（`appendfsync everysec`）</font>，这样对`Redis` 性能几乎没任何影响。**  
而且这样即使出现系统崩溃，用户最多只会丢失一秒之内产生的数据。当硬盘忙于执行写入操作的时候，`Redis` 还会优雅的放慢自己的速度以便适应硬盘的最大写入速度。

#### 2.3 AOF 重写
`AOF`的方式也同时带来了另一个问题。持久化文件会变的越来越大。

为了压缩`AOF文件`，`Redis`提供了<font color="red">**`bgrewriteaof`**</font>命令。将内存中的数据以命令的方式保存到临时文件中，同时会`fork出一条新进程`来将文件 **重写** 。  
重写`AOF文件`的操作，并没有读取旧的AOF文件，而是将整个内存中的数据库内容用命令的方式 **（就是针对`相同Key`的操作，进行合并，比如同一个`Key`的`set`操作，那就是后面覆盖前面）** 写了一个新的`AOF文件`，这点和快照有点类似。

**重写AOF过程如下：**
1. 在执行 **`bgrewriteaof`** 命令时，`Redis` 服务器会维护一个 `AOF 重写缓冲区`，该缓冲区会在子进程创建新 **`AOF`** 文件期间，记录服务器执行的所有写命令。  
2. **当子进程完成创建新 `AOF 文件的`工作之后，服务器会将重写缓冲区中的所有内容追加到新 `AOF 文件`的末尾，使得新旧两个 `AOF 文件`所保存的数据库状态一致。**  
3. 最后，服务器用`新的AOF 文件`替换`旧的AOF 文件`，以此来完成 `AOF文件`重写操作。

<font color="red">注意：在重写过程中，Redis不但将新的操作记录在原有的`AOF缓冲区`，而且还会记录在 `AOF重写缓冲区`。</font>  
<font color="red">补充：AOF重写是一个有歧义的名字，该功能是通过读取数据库中的键值对来实现的，程序无须对现有AOF文件进行任何读入、分析或者写入操作。</font>

#### 2.4 AOF的优缺点
**优点：**  
* AOF可以更好的保护数据不丢失，一般`AOF`会每隔`1秒`，通过一个后台线程执行一次`fsync`（同步）操作，最多丢失`1秒`的数据。
* AOF日志文件没有任何磁盘寻址的开销，写入性能非常高，文件不容易破损。
* AOF日志文件即使过大的时候，出现后台重写操作，也不会影响客户端的读写。
* AOF日志文件的命令通过非常可读的方式进行记录，这个特性非常适合做灾难性的误删除的紧急恢复。

**缺点：**
* 对于同一份数据来说，`AOF日志文件`通常比`RDB数据快照文件`更大
* `AOF`开启后，支持的写`QPS`会比`RDB`支持的写`QPS` **低** ，因为`AOF`一般会配置成每秒`fsync`一次日志文件，当然，每秒一次`fsync`，性能也还是很高的。

### 3. Redis 数据恢复过程
如果需要恢复数据，只需将备份文件 (`RDB`或`AOF`) 移动到 `Redis` 安装目录并启动服务即可（`Redis`重启后自动完成）。

`Redis`的数据载入主要是指`Redis`重启时候恢复数据的过程，恢复的数据总共有两种：
- **AOF 数据文件**
- **RDB 数据文件**

数据恢复的过程是二选一的过程，也就是如果开启`AOF持久化`那么就会使用`AOF文件`进行恢复，如果没有才会选择`RDB文件`进行恢复。

选择过程源码如下：
```c
void loadDataFromDisk(void) {
    // 记录开始时间
    long long start = ustime();
 
    // AOF 持久化已打开？
    if (server.aof_state == REDIS_AOF_ON) {
        // 尝试载入 AOF 文件
        if (loadAppendOnlyFile(server.aof_filename) == REDIS_OK)
            // 打印载入信息，并计算载入耗时长度
            redisLog(REDIS_NOTICE,"DB loaded from append only file: %.3f seconds",(float)(ustime()-start)/1000000);
    // AOF 持久化未打开
    } else {
        // 尝试载入 RDB 文件
        if (rdbLoad(server.rdb_filename) == REDIS_OK) {
            // 打印载入信息，并计算载入耗时长度
            redisLog(REDIS_NOTICE,"DB loaded from disk: %.3f seconds",
                (float)(ustime()-start)/1000000);
        } else if (errno != ENOENT) {
            redisLog(REDIS_WARNING,"Fatal error loading the DB: %s. Exiting.",strerror(errno));
            exit(1);
        }
    }
}
```

#### 3.1 Redis AOF数据恢复过程
整个`AOF文件`载入的过程整体步骤如下：
- 打开`AOF文件`开始循环读取；
- 根据`AOF`写入的命令解析`Redis 命令行`；
- 通过 **伪命令行客户端** 执行解析的`命令行`；
- Redis接收到 **伪客户端** 发送的命令行以后找到命令对应的函数负责执行数据写入。

`AOF`保存的命令行格式类似`"*3\r\n$3\r\nSET\r\n$5\r\nmykey\r\n$7\r\nmyvalue\r\n"`， 所以解析到 **`*字符`** 就知道是一个命令的开始，然后就知道命令涉及的参数个数，每个参数都以 **`$字符`** 开始标记字符串长度，知道字符串长度就可以解析出命令字符串了。

`AOF`数据恢复过程源码：
```c
int loadAppendOnlyFile(char *filename) {

    // 为客户端
    struct redisClient *fakeClient;

    // 打开 AOF 文件
    FILE *fp = fopen(filename,"r");

    struct redis_stat sb;
    int old_aof_state = server.aof_state;
    long loops = 0;

    // 检查文件的正确性
    if (fp && redis_fstat(fileno(fp),&sb) != -1 && sb.st_size == 0) {
        server.aof_current_size = 0;
        fclose(fp);
        return REDIS_ERR;
    }

    // 检查文件是否正常打开
    if (fp == NULL) {
        redisLog(REDIS_WARNING,"Fatal error: can't open the append log file for reading: %s",strerror(errno));
        exit(1);
    }

    /**
     * 暂时性地关闭 AOF ，防止在执行 MULTI 时，
     * EXEC 命令被传播到正在打开的 AOF 文件中。
     */
    server.aof_state = REDIS_AOF_OFF;

    fakeClient = createFakeClient();

    // 设置服务器的状态为：正在载入
    // startLoading 定义于 rdb.c
    startLoading(fp);

    while(1) {
        int argc, j;
        unsigned long len;
        robj **argv;
        char buf[128];
        sds argsds;
        struct redisCommand *cmd;

        /* 
         * 间隔性地处理客户端发送来的请求
         * 因为服务器正处于载入状态，所以能正常执行的只有 PUBSUB 等模块
         */
        if (!(loops++ % 1000)) {
            loadingProgress(ftello(fp));
            processEventsWhileBlocked();
        }

        // 读入文件内容到缓存
        if (fgets(buf,sizeof(buf),fp) == NULL) {
            if (feof(fp))
                // 文件已经读完，跳出
                break;
            else
                goto readerr;
        }

        // 确认协议格式，比如 *3\r\n
        if (buf[0] != '*') goto fmterr;

        // 取出命令参数，比如 *3\r\n 中的 3
        argc = atoi(buf+1);

        // 至少要有一个参数（被调用的命令）
        if (argc < 1) goto fmterr;

        // 从文本中创建字符串对象：包括命令，以及命令参数
        // 例如 $3\r\nSET\r\n$3\r\nKEY\r\n$5\r\nVALUE\r\n
        // 将创建三个包含以下内容的字符串对象：
        // SET 、 KEY 、 VALUE
        argv = zmalloc(sizeof(robj*)*argc);
        for (j = 0; j < argc; j++) {
            if (fgets(buf,sizeof(buf),fp) == NULL) goto readerr;

            if (buf[0] != '$') goto fmterr;

            // 读取参数值的长度
            len = strtol(buf+1,NULL,10);
            // 读取参数值
            argsds = sdsnewlen(NULL,len);
            if (len && fread(argsds,len,1,fp) == 0) goto fmterr;
            // 为参数创建对象
            argv[j] = createObject(REDIS_STRING,argsds);

            if (fread(buf,2,1,fp) == 0) goto fmterr; /* discard CRLF */
        }

        /* Command lookup 
         *
         * 查找命令
         */
        cmd = lookupCommand(argv[0]->ptr);
        if (!cmd) {
            redisLog(REDIS_WARNING,"Unknown command '%s' reading the append only file", (char*)argv[0]->ptr);
            exit(1);
        }

        /* 
         * 调用伪客户端，执行命令
         */
        fakeClient->argc = argc;
        fakeClient->argv = argv;
        cmd->proc(fakeClient);

        /* The fake client should not have a reply */
        redisAssert(fakeClient->bufpos == 0 && listLength(fakeClient->reply) == 0);
        /* The fake client should never get blocked */
        redisAssert((fakeClient->flags & REDIS_BLOCKED) == 0);

        /*
         * 清理命令和命令参数对象
         */
        for (j = 0; j < fakeClient->argc; j++)
            decrRefCount(fakeClient->argv[j]);
        zfree(fakeClient->argv);
    }

    /* 
     * 如果能执行到这里，说明 AOF 文件的全部内容都可以正确地读取，
     * 但是，还要检查 AOF 是否包含未正确结束的事务
     */
    if (fakeClient->flags & REDIS_MULTI) goto readerr;

    // 关闭 AOF 文件
    fclose(fp);
    // 释放伪客户端
    freeFakeClient(fakeClient);
    // 复原 AOF 状态
    server.aof_state = old_aof_state;
    // 停止载入
    stopLoading();
    // 更新服务器状态中， AOF 文件的当前大小
    aofUpdateCurrentSize();
    // 记录前一次重写时的大小
    server.aof_rewrite_base_size = server.aof_current_size;

    return REDIS_OK;

// 读入错误
readerr:
    // 非预期的末尾，可能是 AOF 文件在写入的中途遭遇了停机
    if (feof(fp)) {
        redisLog(REDIS_WARNING,"Unexpected end of file reading the append only file");

        // 文件内容出错
    } else {
        redisLog(REDIS_WARNING,"Unrecoverable error reading the append only file: %s", strerror(errno));
    }
    exit(1);

// 内容格式错误
fmterr:
    redisLog(REDIS_WARNING");
    exit(1);
}
```

#### 3.2 Redis RDB数据恢复过程
整个`RDB文件`载入的过程和`AOF`有些许差别：
1. `RDB文件`的数据恢复直接写入内存而 **<font color="red">不是</font>通过伪装命令行执行命令生成的** ；
2. `RDB文件`的读取过程和`AOF`不一样，`RDB文件`存储按照`type+key+value`的格式存储所以读取也是这样读取的。

整体恢复步骤如下：
- 打开`RDB文件`开始恢复数据；
- 读取`type`用于判断读取`value`的格式；
- 读取`key`且`key`的第一个字节标明了`key`的 **长度** 所以可以读取准确长度的`key`；
- 读取`value`对象，读取过程根据`type`进行读取以及恢复。

`RDB`数据恢复过程源码：
```c
/*
 * 将给定 rdb 中保存的数据载入到数据库中。
 */
int rdbLoad(char *filename) {
    uint32_t dbid;
    int type, rdbver;
    redisDb *db = server.db+0;
    char buf[1024];
    long long expiretime, now = mstime();
    FILE *fp;
    rio rdb;
 
    // 打开 rdb 文件
    if ((fp = fopen(filename,"r")) == NULL) return REDIS_ERR;
 
    // 初始化写入流
    rioInitWithFile(&rdb,fp);
    rdb.update_cksum = rdbLoadProgressCallback;
    rdb.max_processing_chunk = server.loading_process_events_interval_bytes;
    if (rioRead(&rdb,buf,9) == 0) goto eoferr;
    buf[9] = '\0';
 
    // 检查版本号
    if (memcmp(buf,"REDIS",5) != 0) {
        fclose(fp);
        redisLog(REDIS_WARNING,"Wrong signature trying to load DB from file");
        errno = EINVAL;
        return REDIS_ERR;
    }
    rdbver = atoi(buf+5);
    if (rdbver < 1 || rdbver > REDIS_RDB_VERSION) {
        fclose(fp);
        redisLog(REDIS_WARNING,"Can't handle RDB format version %d",rdbver);
        errno = EINVAL;
        return REDIS_ERR;
    }
 
    // 将服务器状态调整到开始载入状态
    startLoading(fp);
    while(1) {
        robj *key, *val;
        expiretime = -1;
 
        /* Read type. 
         *
         * 读入类型指示，决定该如何读入之后跟着的数据。
         *
         * 这个指示可以是 rdb.h 中定义的所有以REDIS_RDB_TYPE_* 为前缀的常量的其中一个
         * 或者所有以 REDIS_RDB_OPCODE_* 为前缀的常量的其中一个
         */
        if ((type = rdbLoadType(&rdb)) == -1) goto eoferr;
 
        // 读入过期时间值
        if (type == REDIS_RDB_OPCODE_EXPIRETIME) {
 
            // 以秒计算的过期时间
 
            if ((expiretime = rdbLoadTime(&rdb)) == -1) goto eoferr;
 
            /* We read the time so we need to read the object type again. 
             *
             * 在过期时间之后会跟着一个键值对，我们要读入这个键值对的类型
             */
            if ((type = rdbLoadType(&rdb)) == -1) goto eoferr;
 
            /* the EXPIRETIME opcode specifies time in seconds, so convert
             * into milliseconds. 
             *
             * 将格式转换为毫秒*/
            expiretime *= 1000;
        } else if (type == REDIS_RDB_OPCODE_EXPIRETIME_MS) {
 
            // 以毫秒计算的过期时间
 
            /* Milliseconds precision expire times introduced with RDB
             * version 3. */
            if ((expiretime = rdbLoadMillisecondTime(&rdb)) == -1) goto eoferr;
 
            /* We read the time so we need to read the object type again.
             *
             * 在过期时间之后会跟着一个键值对，我们要读入这个键值对的类型
             */
            if ((type = rdbLoadType(&rdb)) == -1) goto eoferr;
        }
            
        // 读入数据 EOF （不是 rdb 文件的 EOF）
        if (type == REDIS_RDB_OPCODE_EOF)
            break;
 
        /* 
         * 读入切换数据库指示
         */
        if (type == REDIS_RDB_OPCODE_SELECTDB) {
 
            // 读入数据库号码
            if ((dbid = rdbLoadLen(&rdb,NULL)) == REDIS_RDB_LENERR)
                goto eoferr;
 
            // 检查数据库号码的正确性
            if (dbid >= (unsigned)server.dbnum) {
                redisLog(REDIS_WARNING,"FATAL: ", server.dbnum);
                exit(1);
            }
 
            // 在程序内容切换数据库
            db = server.db+dbid;
 
            // 跳过
            continue;
        }
 
        /* Read key 
         *
         * 读入键
         */
        if ((key = rdbLoadStringObject(&rdb)) == NULL) goto eoferr;
 
        /* Read value 
         *
         * 读入值
         */
        if ((val = rdbLoadObject(type,&rdb)) == NULL) goto eoferr;
 
        /* 
         *
         * 如果服务器为主节点的话，
         * 那么在键已经过期的时候，不再将它们关联到数据库中去
         */
        if (server.masterhost == NULL && expiretime != -1 && expiretime < now) {
            decrRefCount(key);
            decrRefCount(val);
            // 跳过
            continue;
        }
 
        /* Add the new object in the hash table 
         *
         * 将键值对关联到数据库中
         */
        dbAdd(db,key,val);
 
        /* Set the expire time if needed 
         *
         * 设置过期时间
         */
        if (expiretime != -1) setExpire(db,key,expiretime);
 
        decrRefCount(key);
    }
 
    /* Verify the checksum if RDB version is >= 5 
     *
     * 如果 RDB 版本 >= 5 ，那么比对校验和
     */
    if (rdbver >= 5 && server.rdb_checksum) {
        uint64_t cksum, expected = rdb.cksum;
 
        // 读入文件的校验和
        if (rioRead(&rdb,&cksum,8) == 0) goto eoferr;
        memrev64ifbe(&cksum);
 
        // 比对校验和
        if (cksum == 0) {
            redisLog(REDIS_WARNING,"RDB file was saved with checksum disabled: no check performed.");
        } else if (cksum != expected) {
            redisLog(REDIS_WARNING,"Wrong RDB checksum. Aborting now.");
            exit(1);
        }
    }
 
    // 关闭 RDB 
    fclose(fp);
 
    // 服务器从载入状态中退出
    stopLoading();
 
    return REDIS_OK;
 
eoferr: /* unexpected end of file is handled here with a fatal exit */
    redisLog(REDIS_WARNING,"Short read or OOM loading DB. Unrecoverable error, aborting now.");
    exit(1);
    return REDIS_ERR; /* Just to avoid warning */
}
```

### 4. 总结
#### 4.1 save 、bgsave和bgrewriteaof执行区别和注意事项
* `save` 会将整个Redis数据库数据保存到 **`RDB文件`** ，并在保存完成之前 **阻塞** 其他调用者。
* `save` 命令直接调用 **`save`** ，阻塞 Redis 主进程；`bgsave` 用**子进程**调用 `rdbSave` ，主进程仍可继续处理命令请求。
* `save` 执行期间， **`AOF`** 写入可以在后台线程进行， **`bgrewriteaof`** 可以在子进程进行，所以这三种操作可以同时进行。
* 为了避免产生竞争条件， `bgsave` 执行时， `save` 命令不能执行。
* 为了避免性能问题， `bgsave` 和 `bgrewriteaof` 不能同时执行。
* 调用 **`rdbLoad`** 函数载入 **`RDB文件`** 时（数据恢复），不能进行任何和数据库相关的操作；  
不过`订阅与发布`方面的命令可以正常执行，因为它们和数据库不相关联。`发布与订阅`功能和其他数据库功能是完全隔离的，前者不写入也不读取数据库，所以在服务器载入期间，`订阅与发布`功能仍然可以正常使用，而不必担心对载入数据的完整性产生影响。

#### 4.2 （补充）RDB 和 AOF 的混合持久化
`Redis 4.0` 开始支持 `RDB` 和 `AOF` 的混合持久化（默认关闭，可以通过配置项`aof-use-rdb-preamble`开启）。

如果把混合持久化打开，`AOF` 重写的时候就直接把 `RDB` 的内容写到 `AOF文件`开头。**这样做的好处是可以结合 `RDB` 和 `AOF` 的优点, 快速加载同时避免丢失过多的数据。当然缺点也是有的， `AOF` 里面的 `RDB` 部分是压缩格式不再是 `AOF` 格式，可读性较差**。

## 八、分布式部署（集群部署）
具体搭建步骤参考其他笔记：[Centos7安装Redis（含cluster方式集群部署）](https://xieruhua.github.io/javalearning/#/./%E5%B7%A5%E5%85%B7%E6%9C%8D%E5%8A%A1%E6%90%AD%E5%BB%BA/Centos7%E5%AE%89%E8%A3%85Redis%EF%BC%88%E5%90%ABcluster%E6%96%B9%E5%BC%8F%E9%9B%86%E7%BE%A4%E9%83%A8%E7%BD%B2%EF%BC%89)

### 1. Redis集群简介
**`Redis3.0`版本之前只支持单例模式，在3.0版本及以后才支持集群。**

`Redis`集群采用`P2P模式`，是完全去中心化的，不存在中心节点或者代理节点；因此`Redis`集群是没有统一的入口的，客户端（`client`）连接集群的时候连接集群中的任意节点（`node`）即可，集群内部的节点是相互通信的（`PING-PONG`机制），每个节点都是一个`Redis`实例。

为了实现集群的高可用，即判断节点是否健康（能否正常使用），`redis-cluster`有这么一个投票容错机制： **如果集群中超过半数的节点投票认为某个节点挂了，那么这个节点就挂了。**
- **那么如何判断集群是否挂了呢？**  
如果集群中任意一个节点挂了，而且该节点没有从节点（备份节点），那么这个集群就挂了；
- **那么为什么任意一个节点挂了（没有从节点）这个集群就挂了呢？**   
因为集群内置了`16384`个`slot`（哈希槽），并且把所有的物理节点映射到了这`16384[0-16383]`个`slot`上，或者说把这些`slot`均等的分配给了各个节点。  
当需要在`Redis`集群存放一个数据`（key-value）`时，`Redis`会先对这个`key`进行 **`crc16算法`** ，然后得到一个结果。再把这个结果对`16384`进行求余，这个余数会对应`[0-16383]`其中一个槽，进而决定`key-value`存储到哪个节点中。
所以一旦某个节点挂了，该节点对应的`slot`就无法使用，那么就会导致集群无法正常工作。  
**补充：每个`Redis集群`理论上最多可以有`16384`个节点。**

### 2. Redis集群三种模式
- **主从模式** ： 可以实现读写分离，数据备份。 **但是并不是`「高可用」`的**
- **哨兵模式** ：可以看做是主从模式的 **`「高可用」`** 版本，其引入了`Sentinel（哨兵）`对整个`Redis`服务集群进行监控。但是由于只有一个主节点，因此仍然有写入瓶颈。
- **Cluster模式** ： 不仅提供了高可用的手段，同时数据是分片保存在各个节点中的， **可以支持高并发的写入与读取** 。实现也是其中最复杂的。

#### 2.1 主从模式：
> 配置过程省略....

`Redis` 的主从模式，使用异步复制；`slave` 节点异步从 `master` 节点复制数据，`master`节点提供读写服务，`slave` 节点只提供读服务（这个是默认配置，可以通过修改配置文件`slave-read-only` 控制）。
- `master` 节点可以有多个从节点（`slave`节点）。
- 配置一个 `slave` 节点只需要在`redis.conf` 文件中指定 `slaveof master-ip master-port` 即可。

#### 2.2 哨兵模式：
> 配置过程省略....

##### 2.2.1 Redis-sentinel简介
`Redis` 的 `Sentinel` 系统用于管理多个 `Redis` 服务器（`instance`），为 `Redis`提供了高可用性。使用哨兵模式创建一个可以不用人为干预而应对各种故障的 `Redis` 部署。

**该系统执行以下三个任务：**
- **监控（`Monitoring`）** ：`Sentinel` 会不断地检查你的主服务器和从服务器是否允许正常。
- **提醒（`Notification`）** ：当被监控的某个 `Redis` 服务器出现问题时，`Sentinel` 可以通过 `API` 向管 理员或者其他应用程序发送通知。
- **自动故障迁移（`Automatic failover`）** : 
  - 当一个主服务器不能正常工作时，`Sentinel` 会开始一次自动故障迁移操作，他会将失效主服务器的其中一个从服务器升级为新的主服务器，并让失效主服务器的其他从服务器改为复制新的主服务器；
  - 客户端试图连接失败的主服务器时，集群也会向客服端返回新主服务器的地址，是的集群可以使用新主服务器代替失效服务器。

##### 2.2.2 sentinel 的分布式特性及注意点
**`Redis Sentinel` 是一个分布式系统。**

你可以在一个架构中运行多个 `Sentinel` 进程，这些进程使用`流言协议（gossip protocols)`来接收关于主服务器是否下线的信息， 并使用`投票协议（agreement protocols）`来决定是否执行自动故障迁移，以及选择哪个从服务器作为新的主服务器。

单个 `sentinel` 进程来监控 `Redis` 集群是不可靠的，当 `sentinel` 进程宕掉后（`sentinel` 本身也有单 点问题，`single-point-of-failure`）整个集群系统将无法按照预期的方式运行。 **所以有必要将`sentinel`也配置为集群。**

**`sentinel` 集群的好处：**
- 即使有一些`sentinel`进程宕掉了，依然可以进行`Redis`集群的主备切换；
- 如果只有一个`sentinel`进程，如果这个进程运行出错，或者是网络堵塞，那么将无法实现`Redis`集群的主备切换（单点问题）;
- 如果有多个`sentinel`，`Redis`的客户端可以随意地连接任意一个`Redis`来获得关于`Redis`集群中的信息。

补充： **一个健壮的部署至少需要三个哨兵实例。** 三个哨兵实例应该放置在客户使用独立方式确认故障的计算机或虚拟机中。例如不同的物理机或不同可用区域的虚拟机。

#### 2.3 cluster 模式
> 配置过程参考笔记：[Centos7安装Redis（含cluster方式集群部署）](https://xieruhua.github.io/javalearning/#/./%E5%B7%A5%E5%85%B7%E6%9C%8D%E5%8A%A1%E6%90%AD%E5%BB%BA/Centos7%E5%AE%89%E8%A3%85Redis%EF%BC%88%E5%90%ABcluster%E6%96%B9%E5%BC%8F%E9%9B%86%E7%BE%A4%E9%83%A8%E7%BD%B2%EF%BC%89)

##### 2.3.1 Redis-cluster简介
- `cluster` 的出现是为了解决单机 `Redis` 容量有限的问题，因此将 `Redis` 的数据根据一定的规则分配到多台机器。  
- `cluster` 可以说是 `sentinel` 和`主从模式`的结合体，不仅提供了高可用的手段，同时数据是分片保存在各个节点中的，可以支持高并发的写入与读取。  

通过 `cluster` 可以实现`主从`和 `master 重选`功能，所以如果配置`2`个副本`3`个分片的话，就需要`6`个 `Redis` 实例。  
因为 `Redis` 的数据是根据一定规则分配到 `cluster` 的不同机器的，当数据量过大时，可以新增机器进行扩容这种模式适合数据量巨大的缓存要求，当数据量不是很大使用 `sentinel模式` 即可。

##### 2.3.2 补充：为什么Redis-cluster集群最少需要6个节点？
首先我们既然要搭建集群，那么`master`节点 **至少** 要`3`个，`slave`节点也是 **至少** `3`个，为什么呢？  
**这是因为一个`Redis`集群如果要对外提供可用的服务，那么集群中必须要有过半的`master`节点正常工作。**

基于这个特性，如果想搭建一个能够允许 `n` 个`master`节点挂掉的集群，那么就要搭建`2n+1`个`master`节点的集群。

如：
- `2`个`master`节点，挂掉`1`个，则`1`不过半，则集群`down`掉，无法使用，容错率为`0`
- `3`个`master`节点，挂掉`1`个，`2>1`，还可以正常运行，容错率为`1`
- `4`个`master`节点，挂掉`1`个，`3>1`，还可以正常运行，但是当挂掉`2`个时，`2=2`，不过半，容错率依然为`1`

如果创建集群时设置`slave`为`1`个（即命令：`--cluster-replicas 1`）  
当总节点少于`6`个时会有上述报错。所以集群搭建至少需要`6`个节点

附：当总节点少于`6`个时会有如下报错：
```bash
[root@VM-0-13-centos redis-cluster]# redis-cli --cluster create 0.0.0.0:7000 0.0.0.0:7001 0.0.0.0:7002 --cluster-replicas 1
Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.
*** ERROR: Invalid configuration for cluster creation.
*** Redis Cluster requires at least 3 master nodes.
*** This is not possible with 3 nodes and 1 replicas per node.
*** At least 6 nodes are required.

# 报错内容翻译如下
***错误：创建群集的配置无效。
***Redis群集需要至少3个主节点。
***如果每个节点有3个节点和1个副本，这是不可能的。
***至少需要6个节点。
```

### 3. Redis 集群常见的性能问题都有哪些？如何解决？
1. **Master 写RDB内存快照：** save命令调度rdbSave函数，会阻塞主线程的工作，当快照比较大时对性能影响是非常大的，会间断性暂停服务，所以Master最好不要写内存快照。
2. **Master `AOF持久化`：** 如果不重写`AOF文件`，这个持久化方式对性能的影响是最小的，但是`AOF文件`会不断增大，`AOF文件`过大会影响Master **重启** 的恢复速度。  
Master最好不要做任何持久化工作，包括`RDB内存快照`和`AOF日志文件`，特别是不要启用内存快照做持久化； **如果数据比较重要，可以使用某个Slave开启`AOF备份数据`，策略为每秒同步一次。**
3. **Master调用`bgrewriteaof`重写AOF文件：** AOF在重写的时候会占大量的CPU和内存资源，导致服务响应时长过高，出现短暂服务暂停现象。
4. **Redis主从复制的性能问题：** 为了主从复制的速度和连接的稳定性，Slave和Master最好在同一个局域网内；  
同时主从复制不要用图状结构，用`单向链表结构`更为稳定，**即：Master <- Slave1 <- Slave2 <- Slave3...（这样的结构方便解决单点故障问题，实现Slave对Master的替换。如果Master挂了，可以立刻启用Slave1做Master，其他不变）**
。

原则：`Master`会将数据同步到`Slave`，而`Slave`不会将数据同步到`Master`。`Slave`启动时会连接`Master`来同步数据。

## 九、Redis的单线程和多线程介绍
虽然说 `Redis` 是单线程模型，但是，实际上，`Redis` 在 `4.0` 之后的版本中就已经加入了对多线程的支持。不过，`Redis 4.0` 增加的多线程主要是针对一些大键值对的删除操作的命令，使用这些命令就会使用主处理之外的其他线程来 **“异步处理”**。

<font color="red">补充：如果考虑到`RDB`和`AOF`的`Fork操作`，或者一些定时任务的处理，那么`Redis`也可以说支持多进程。  
**但是Redis对数据的处理，至始至终，都是单线程。**</font>

大体上来说，`Redis 6.0` 之前主要还是单线程处理。

### 1. Redis6.0 之前为什么不使用多线程？
主要原因如下：
* 单线程编程容易并且更容易维护；
* Redis 的性能瓶颈不在 CPU ，主要在内存和网络；
* 多线程增加了系统复杂度，还可能会存在死锁、线程上下文切换等问题，甚至会影响性能。
* 单线程机制使得 Redis 内部实现的复杂度大大降低，如：`Hash`的惰性 `Rehash`、`list`的`Lpush` 等等 **“线程不安全”** 的命令都可以无锁进行。

### 2. Redis6.0之后为何引入了多线程？
* 可以充分利用服务器 CPU 资源，目前主线程只能利用一个核
* 多线程任务可以分摊 Redis 同步 IO 读写负荷

**`Redis6.0` 引入多线程主要是为了提高网络 IO 读写性能，因为这个算是 `Redis` 中的一个性能瓶颈（Redis 的瓶颈主要受限于内存和网络）。**  
虽然，引入了多线程，但是多线程只是在网络数据的读写这类耗时操作上使用了，执行命令仍然是单线程顺序执行。因此，日常开发中也不需要担心线程安全问题。

`Redis6.0` 的多线程默认是禁用的，只使用主线程。如需开启需要修改配置文件：
```bash
# 默认状态
# io-threads-do-reads no

# 开启状态
io-threads-do-reads yes
```

**开启多线程后，还需要设置线程数，否则是不生效的。** 同样需要修改配置文件:
```bash
# 官网建议4核的处理器建议设置为2或3个线程，8核的处理器建议设置为6个线程
io-threads 4 
```
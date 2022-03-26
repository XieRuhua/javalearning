# 锁（Java）

***
[笔记内容参考1：【美团技术文档】不可不说的Java“锁”事](https://tech.meituan.com/2018/11/15/java-lock.html)   
[笔记内容参考2：Java中锁的解决方案](https://blog.csdn.net/publicv/article/details/106973354)   
[笔记内容参考3：Java中的锁](https://blog.csdn.net/hellozpc/article/details/80724317)  
[笔记内容参考4：面试官：你说说互斥锁、自旋锁、读写锁、悲观锁、乐观锁的应用场景](https://mp.weixin.qq.com/s/CqIXHowIDT1kxyBOO0x7TQ)  
[笔记内容参考5：Java中的对象结构和锁膨胀简介](https://blog.csdn.net/jiahuixi/article/details/107229288)  
[笔记内容参考6：volatile的适用场景](https://www.cnblogs.com/ouyxy/p/7242563.html)

[toc]

## 一、锁简介
一般将多线程的数据安全性问题分为三种：**原子性**、**可见性** 和 **有序性**。

* **原子性：** 是指一系列操作要么全部都做，要么全部不做。
* **可见性：** 是指当一个线程修改了一个共享变量后，这个修改能够及时地被另一个线程看到（即修改结果共享给其他线程）。
* **有序性：** 是指在java为了性能优化，会对程序进行"指令重排序"和"工作内存和主内存同步延迟"；在本线程中前后操作看起来是有序的，但是如果在另一个线程中观察，操作是无序的，（java中volatile变量通过内存屏障来防止指令重排序从而保证有序）。

而锁是用来控制多个线程访问共享资源的工具。作为并发控制，保证一致性的工具，锁本质上是一个标记：
* 把这个标记放在关系数据库（RDBMS）中，就可以使用数据库的方式实现锁机制。比如设计一张锁表，表中有个字段state，state有两个值，分别表示锁定/未锁定状态；
* 把这个标记放在zookeeper的节点中，就可以使用zk实现分布式锁；
* 把这个标记放在内存中，比如设置一个 volatile变量state保存锁定/未锁定状态，就可以在java程序级别实现锁。

Java是天生的并发语言。多线程在带来更高效率的同时，又带来了并发数据安全性问题：多线程访问共享资源的时候，避免不了资源竞争而导致数据错乱的问题。  

所以通常为了解决这一问题，都会在访问共享资源之前加**锁**。

Java中的锁大体分为两类： **"synchronized"关键字锁** 和 **"JUC"(java.util.concurrent包)中的locks包和atomic中提供的锁** 。

## 二、锁分类及特性描述
<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/锁分类.png)
</center>

### 1. 分类
一般分为 **乐观锁** 和 **悲观锁**，对不同场景、不同用途还可以细分：
* **乐观锁：** 假定没有冲突，在修改数据时如果发现数据与之前获取的不一致，则读取最新数据，再修改（**只在提交操作时检测是否违反数据完整性**）
* **悲观锁：** 假定会发生并发冲突，对所有操作加锁（**屏蔽一切可能违反数据完整性的操作**）
* **公平锁、非公平锁：** 争抢锁的顺序，如果是按先来后到的原则，则是公平的，否则是非公平的
* **可重入锁、不可重入锁：** 线程拿到锁后，可以自由进入同一把锁所同步的其他代码
* **独享锁（写）：** 给资源加上写锁，线程可以修改资源，其他线程不能再获取锁
* **共享锁（读）：** 给资源加上独锁后只能读不能写，其他线程也只能加读锁
* **自旋锁：** 为了不放弃CPU事件，循环使用CAS尝试对数据进行更新，直至成功。
* **互斥锁：**所谓互斥锁就是指**一次最多只能有一个线程持有的锁**。在**JDK中synchronized和JUC的Lock就是互斥锁**。　
* **无锁：** **要保证现场安全，并不是一定就要进行同步，两者没有因果关系**。**同步只是保证共享数据争用时的正确性的手段**，如果一个方法本来就不涉及共享数据，那它自然就无须任何同步措施去保证正确性，因此会有一些代码天生就是线程安全的。　

>**注：上面所列出的锁并非独立存在，有些之间是互相关联的，只是从概念做区分。如：读写锁也是互斥锁**
### 2. 部分特性描述
#### 锁消除
锁消除是虚拟机JIT（just in time：即时编译器）在运行时，对一些代码上要求同步，但是被检测到不可能存在共享数据竞争的锁进行消除。

锁消除的主要判断依据是来源于 **逃逸分析** 的数据支持：  
如果判断在一段代码中，堆上的所有数据都不会逃逸出去从而能被其他线程访问到，那就可以把他们当做栈上数据对待，认为他们是线程私有的，同步加锁自然就无需进行。　

来看这样一个方法：
```java
public String concatString(String s1, String s2, String s3){
    StringBuffer sb = new StringBuffer();
    sb.append(s1);
    sb.append(s2);
    sb.append(s3);
    return sb.toString();
}
```

可以知道`StringBuffer` 的`append(String str)` 方法定义如下：
```java
@Override
public synchronized StringBuffer append(String str) {
    toStringCache = null;
    super.append(str);
    return this;
}
```
可以观察到`sb`对象它的作用域被限制在方法的内部，也就是`sb`对象不会 **“逃逸”** 出去，其他线程无法访问。  
因此，虽然这里有锁，但是可以被安全的消除，在即时编译之后，这段代码就会忽略掉所有的同步而直接执行了。

#### 锁粗化
原则上，在编写代码的时候，总是推荐将同步块的作用范围限制的尽量小，即只在共享数据的实际作用域中才进行同步。

**这样是为了使得需要同步的操作数量尽可能变小，如果存在锁竞争，那等待的线程也能尽快拿到锁，大部分情况下，这样做是正确的。**  
但是，如果一系列的连续操作都是同一个对象反复加锁和解锁，甚至加锁操作是出现在循环体中的，那么即使没有线程竞争，频繁地进行互斥同步操作也导致不必要的性能损耗。

如：类似锁消除的`concatString()`方法。  
如果`StringBuffer sb = new StringBuffer();`定义在方法体之外，那么就会有线程竞争，但是每个`append()`操作都对同一个对象反复加锁解锁，那么虚拟机探测到有这样的情况的话，会把加锁同步的范围扩展到整个操作序列的外部，即扩展到第一个`append()`操作之前和最后一个`append()`操作之后，**这样的一个锁范围扩展的操作就称之为锁粗化。**

#### 锁膨胀（锁升级）
**可以简单理解为一个对象的锁状态：无锁 -> 偏向锁 -> 轻量级锁 -> 重量级锁 的过程**

**锁升级的过程：**   
先看一下对象头中存储内容：
<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/对象头中存储内容.png)
</center>

**每一个线程在准备获取共享资源时，执行步骤如下：**

1. 检查`Mark Word`里面是不是放的自己的`ThreadId`（线程id），如果是，表示当前线程是处于 **“偏向锁”** 装态。
2. 如果`Mark Word`不是自己的`ThreadId`，锁升级为 **轻量锁**；这时候，用`CAS机制`来执行切换，新的线程根据`Mark Word`里面现有的`ThreadId`，通知之前线程暂停，之前线程将`Mark Word`的内容置为空。
3. 两个线程都把锁对象的`HashCode`复制到自己新建的用于存储锁的记录空间，接着开始通过`CAS`操作，把锁对象的`Mark Word`的内容修改为自己新建的记录空间的地址的方式竞争`Mark Word`。
4. 第三步中成功执行`CAS`的获得资源，失败的则进入自旋（**自旋锁**）。
5. 自旋的线程在自旋过程中，成功获得资源（即之前获的资源的线程执行完成并释放了共享资源），则整个状态依然处于 **轻量级锁的状态**。
6. 如果自旋失败，进入 **重量级锁** 的状态，这个时候，自旋的线程进行阻塞，等待之前线程执行完成并唤醒自己。

## 三、不同的锁详解
### 1. 乐观锁与悲观锁
乐观锁与悲观锁应用场景主要是在更新数据的时候，更新数据这个场景也是使用锁的非常主要的场景之一。

#### 1.1 乐观锁
它是一种比较交换的机制，总是认为不会产生并发问题，每次去取数据的时候总认为不会有其他线程对数据进行修改，因此不会上锁，但是在更新时会判断其他线程在这之前有没有对数据进行修改；一般会使用版本号（version）机制或CAS操作实现。
* **version方式：** 一般是在数据表中加上一个数据版本号version字段，表示数据被修改的次数，当数据被修改时，version值会加一。当线程A要更新数据值时，在读取数据的同时也会读取version值，在提交更新时，若刚才读取到的version值为当前数据库中的version值相等时才更新，否则重试更新操作，直到更新成功。  
  核心SQL语句：`update table set x=x+1, version=version+1 where id=#{id} and version=#{version};`
* **CAS操作方式（即compare and swap 或者 compare and set）：** 涉及到三个操作数，`数据所在的内存值`，`预期值`，`新值`。  
  当需要更新时，判断当前内存值与之前取到的值是否相等，若相等，则用新值更新，若失败则重试，一般情况下是一个自旋操作（自旋锁：即不断的重试获取锁）。

看一下JAVA中最常用的 `i++`：
* `i++`它的执行顺序是什么样子的？
* 它是线程安全的吗？当多个线程并发执行`i++` 的时候，会不会有问题？ 

```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 乐观锁
 */
public class OptimisticLocking {
    private int i = 0;
    
    public static void main(String[] args) throws InterruptedException {
        for (int j = 1; j <= 5; j++) {
            new OptimisticLocking().notOptimisticLocking();
        }
    }
    
    public void notOptimisticLocking () throws InterruptedException {
        OptimisticLocking optimisticLocking = new OptimisticLocking();
        ExecutorService executorService = Executors.newFixedThreadPool(50);
        //  目的等5000个任务执行完在执行 主线程的输出语句
        CountDownLatch countDownLatch = new CountDownLatch(5000);
        for (int i = 0; i < 5000; i++) {
            executorService.execute(() -> {
                optimisticLocking.i++;
                //  5000计数器减1
                countDownLatch.countDown();
            });
        }
        //  执行完任务将线程池关闭
        executorService.shutdown();
        //  5000个任务执行完，放开主线程执行输出语句
        countDownLatch.await();
        System.out.println("执行完成后，i=" + optimisticLocking.i);
        /*
        i++ 不是原子性的  线程不安全的
        1: 取出当前的值  例如 2000
        2: 修改为2001 ,但是在这时候并不只是这个线程在执行相同步骤。存在并发性。所以有可能值被重复覆盖了
         */
    }
}
```
上面的程序中，模拟了50个线程同时执行 `i++` ，总共执行5000次。然后分别执行5次循环，预期得到的结果应该是5次5000，实际执行结果如下：
```
执行完成后，i=4988
执行完成后，i=5000
执行完成后，i=4995
执行完成后，i=4991
执行完成后，i=4990
```
可以看到每次执行的结果都不一样，且不是5000。  
**说明 `i++ `并不是一个原子性的操作，在多线程的情况下并不安全。**  

把 `i++` 的详细执行步骤拆解一下：
1. 从内存中取出 `i` 的当前值
2. 将 `i` 的值加`1`
3. 将计算好的值放入到内存当中

在多线程的场景下：线程A和线程B同时从内存取出`i`的值，假如`i`的值是 1000 ，然后线程A和线程B再同时执行 `+1` 操作，然后把值再放入内存中，这时，内存中的值是1001，而期望的是1002，正是这个原因导致了上面的错误。

如何解决呢？**在JAVA1.5以后，JDK官方提供了大量的原子类，这些类的内部都是基于 CAS机制的，也就是使用了 乐观锁。**   
将上面的程序稍微改造一下，如下：
```java

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class OptimisticLocking {
    private int i = 0;
    private AtomicInteger atomicInteger = new AtomicInteger(0);

    public static void main(String[] args) throws InterruptedException {
        for (int j = 1; j <= 5; j++) {
            // new OptimisticLocking().notOptimisticLocking();
            new OptimisticLocking().optimisticLocking();
        }
    }

    public void notOptimisticLocking() throws InterruptedException {
        OptimisticLocking optimisticLocking = new OptimisticLocking();
        ExecutorService executorService = Executors.newFixedThreadPool(50);
        //  目的等5000个任务执行完在执行 主线程的输出语句
        CountDownLatch countDownLatch = new CountDownLatch(5000);
        for (int i = 0; i < 5000; i++) {
            executorService.execute(() -> {
                optimisticLocking.i++;
                //  5000计数器减1
                countDownLatch.countDown();
            });
        }
        //  执行完任务将线程池关闭
        executorService.shutdown();
        //  5000个任务执行完，放开主线程执行输出语句
        countDownLatch.await();
        System.out.println("执行完成后，i=" + optimisticLocking.i);
        /*
        i++ 不是原子性的  线程不安全的
        1: 取出当前的值  例如 2000
        2: 修改为2001 ,但是在这时候并不只是这个线程在执行相同步骤。存在并发性。所以有可能值被重复覆盖了
         */
    }

    public void optimisticLocking() throws InterruptedException {
        OptimisticLocking optimisticLocking = new OptimisticLocking();
        ExecutorService executorService = Executors.newFixedThreadPool(50);
        CountDownLatch countDownLatch = new CountDownLatch(5000);
        for (int i = 0; i < 5000; i++) {
            executorService.execute(() -> {
                optimisticLocking.atomicInteger.incrementAndGet();
                countDownLatch.countDown();
            });
        }
        executorService.shutdown();
        countDownLatch.await();
        System.out.println("执行完成后，i=" + optimisticLocking.atomicInteger);
    }
}
```
将变量 `i` 的类型改为 `AtomicInteger` ，`AtomicInteger` 是一个原子类（后文有详细介绍）。  
在之前调用 `i++` 的地方改为了 `i.incrementAndGet()`，`incrementAndGet()` 方法采用了 `CAS 机制`（后文有详细介绍），也就是说使用了 **乐观锁**。  执行结果如下：

```
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
```
5次的结果都是5000，符合预期。这就是乐观锁。

**小结：**  
乐观锁在读取数据的时候不会做任何限制，而是在更新数据的时候，进行数据的比较，保证数据的版本一致时再更新数据。  
根据它的这个特点，可以看出 **<font color="red">乐观锁适用于读操作多，而写操作少的场景。</font>**

乐观锁虽然去除了加锁解锁的操作，但是一旦发生冲突，重试的成本非常高，所以**只有在冲突概率非常低，且加锁成本非常高的场景时，才考虑使用乐观锁。**

#### 1.2 悲观锁
悲观锁与乐观锁恰恰相反，悲观锁从读取数据的时候就显式的加锁，直到数据更新完成，释放锁为止，在这期间只能有一个线程去操作，其他的线程只能等待（阻塞）。

**悲观锁总是假设最坏的情况，每次取数据时都认为其他线程会修改，所以都会加锁（读锁、写锁、数据库种的行锁等），当其他线程想要访问数据时，都需要阻塞挂起，直到上一个持有锁的线程释放锁。**
* 可以依靠数据库实现，如行锁、读锁和写锁等，都是在操作之前加锁，  
  核心SQL语句：`select * from table A where A.id=#{id} for update;`
* 在Java中，`synchronized`的思想也是悲观锁。

在JAVA中，悲观锁可以使用 `synchronized` 关键字或者 `ReentrantLock` 类来实现。还是上面的例子，分别使用这两种方式来实现一下。  
首先是使用  `synchronized` 关键字来实现：
```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 悲观锁
 */
public class PessimisticLocking {
    private Integer i = 0;
    public static void main(String[] args) throws InterruptedException {
        for (int j = 1; j <= 5; j++) {
            new PessimisticLocking().synchronizedPessimisticLocking();
        }
    }
    public void synchronizedPessimisticLocking () throws InterruptedException {
        PessimisticLocking pessimisticLocking = new PessimisticLocking();
        ExecutorService executorService = Executors.newFixedThreadPool(50);
        CountDownLatch countDownLatch = new CountDownLatch(5000);
        for (int i = 0; i < 5000; i++) {
            executorService.execute(() -> {
                synchronized (pessimisticLocking) {
                    pessimisticLocking.i++;
                }
                countDownLatch.countDown();
            });
        }
        executorService.shutdown();
        countDownLatch.await();
        System.out.println("执行完成后，i=" + pessimisticLocking.i);
    }
}
```
唯一的改动就是增加了 `synchronized` 块，它锁住的对象是 `PessimisticLocking` ，在所有线程中，谁获得了 `PessimisticLocking` 对象的锁，谁才能执行 `i++` 操作。  
使用了 `synchronized` 悲观锁的方式，使得` i++ `线程安全。结果如下：

```
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
```
结果都是 5000，符合预期。  

接下来，再使用 `ReentrantLock` 类来实现悲观锁。代码如下：
```java
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 悲观锁
 */
public class PessimisticLocking {
    private Integer i = 0;
    private Lock lock = new ReentrantLock();
    public static void main(String[] args) throws InterruptedException {
        //        new PessimisticLocking().synchronizedPessimisticLocking();
        new PessimisticLocking().reentrantLockPessimisticLocking();
    }
    public void synchronizedPessimisticLocking () throws InterruptedException {
        PessimisticLocking pessimisticLocking = new PessimisticLocking();
        ExecutorService executorService = Executors.newFixedThreadPool(50);
        CountDownLatch countDownLatch = new CountDownLatch(5000);
        for (int i = 0; i < 5000; i++) {
            executorService.execute(() -> {
                synchronized (pessimisticLocking) {
                    pessimisticLocking.i++;
                }
                countDownLatch.countDown();
            });
        }
        executorService.shutdown();
        countDownLatch.await();
        System.out.println("执行完成后，i=" + pessimisticLocking.i);
    }

    public void reentrantLockPessimisticLocking () throws InterruptedException {
        PessimisticLocking pessimisticLocking = new PessimisticLocking();
        ExecutorService executorService = Executors.newFixedThreadPool(50);
        CountDownLatch countDownLatch = new CountDownLatch(5000);
        for (int i = 0; i < 5000; i++) {
            executorService.execute(() -> {
                pessimisticLocking.lock.lock();
                pessimisticLocking.i++;
                pessimisticLocking.lock.unlock();
                countDownLatch.countDown();
            });
        }
        executorService.shutdown();
        countDownLatch.await();
        System.out.println("执行完成后，i=" + pessimisticLocking.i);
    }
}
```
在类中显示的增加了 `Lock lock = new ReentrantLock();` 而且在 `i++` 之前增加了 `lock.lock()` 加锁操作，在 `i++` 之后增加了 `lock.unlock()` 释放锁的操作。  
同样运行5次，看看结果：

```
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
执行完成后，i=5000
```
结果都是 5000，完全符合预期。

**小结**：

悲观锁从读取数据的时候就加了锁，并且在更新数据的时候， 保证只有一个线程在执行更新操作，并没有像乐观锁那样进行数据版本的比较。  
所以  **<font color="red"> 悲观锁适用于读相对少，写相对多的操作。 </font>**

### 2. 公平锁与非公平锁
#### 2.1 对比描述即代码演示
**公平锁在多线程情况下，对待每一个线程都是公平的，保证了锁的获取按照FIFO原则（first in first out即先入先出原则）；而非公平锁恰好与之相反。**

举例：去超市买东西，在储物柜存储东西的例子。储物柜只有一个，同时来了3个人使用储物柜，这时 A 先抢到了柜子，A去使用，B和C自觉进行排队。A 使用完之后，后面排队中的第一个人将继续使用柜子，这就是公平锁。在公平锁当中，所有的线程都自觉排队，一个线程执行完之后，排在后面的线程继续使用。  
非公平锁相反，A在使用柜子的时候，B 和 C 并不会排队，A 使用完之后，将柜子的钥匙往后面一抛，B 和 C 谁抢到就谁用，甚至可能突然冒出来个 D ，这个 D 抢到了钥匙，那么D 将使用柜子 ，这个就是非公平锁。

公平锁与非公平锁都在 `ReentrantLock` 类里给出了实现，`ReentrantLock` 的部分（构造函数）源码：
```java
/**
 * Creates an instance of {@code ReentrantLock}.
 * This is equivalent to using {@code ReentrantLock(false)}.
 */
public ReentrantLock() {
    sync = new NonfairSync();
}

/**
 * Creates an instance of {@code ReentrantLock} with the
 * given fairness policy.
 *
 * @param fair {@code true} if this lock should use a fair ordering policy
 */
public ReentrantLock(boolean fair) {
    sync = fair ? new FairSync() : new NonfairSync();
}
```
`ReentrantLock` 有两个构造方法：
* 默认的构造方法中`sync = new Nonfairsync();`，可以从字面意思看出它是一个非公平锁。
* 第二个构造方法，它需要传入一个参数，参数是一个布尔型，`true` 是公平锁，`false` 是非公平锁。

可以看到 `sync` 有两个实现类，分别是 `FairSync`（公平锁） 和 `NonfairSync`（非公平锁），再看看获取锁的核心方法。  
首先是 `FairSync（公平锁）`的源码：

```java
/**
 * Sync object for fair locks
 */
static final class FairSync extends Sync {
    private static final long serialVersionUID = -3000897897090466540L;

    final void lock() {
        acquire(1);
    }

    /**
     * Fair version of tryAcquire.  Don't grant access unless
     * recursive call or no waiters or is first.
     */
    protected final boolean tryAcquire(int acquires) {
        final Thread current = Thread.currentThread();
        int c = getState();
        if (c == 0) {
            if (!hasQueuedPredecessors() &&
                compareAndSetState(0, acquires)) {
                setExclusiveOwnerThread(current);
                return true;
            }
        }
        else if (current == getExclusiveOwnerThread()) {
            int nextc = c + acquires;
            if (nextc < 0)
                throw new Error("Maximum lock count exceeded");
            setState(nextc);
            return true;
        }
        return false;
    }
}
```

然后是`NonfairSync(非公平锁)` 的源码：

```java
/**
 * Performs non-fair tryLock.  tryAcquire is implemented in
 * subclasses, but both need nonfair try for trylock method.
 */
final boolean nonfairTryAcquire(int acquires) {
    final Thread current = Thread.currentThread();
    int c = getState();
    if (c == 0) {
        if (compareAndSetState(0, acquires)) {
            setExclusiveOwnerThread(current);
            return true;
        }
    }
    else if (current == getExclusiveOwnerThread()) {
        int nextc = c + acquires;
        if (nextc < 0) // overflow
            throw new Error("Maximum lock count exceeded");
        setState(nextc);
        return true;
    }
    return false;
}
```

通过对比两个方法，可以看出唯一的不同之处在于 `!hasQueuedPredecessors()` 这个方法。  
很明显这个方法是一个队列，公平锁是将所有的线程放在一个队列中，一个线程执行完成后，从队列中取出下一个线程，而非公平锁则没有这个队列。

这个 **<font color="red">队列</font>** 是基于锁内部维护的一个双向链表，表结点`Node`的值就是每一个请求当前锁的线程。公平锁则在于每次都是依次从队首取值。而非公平锁在上一个线程释放锁之后，任意新的线程妄图获取锁，都是有很大的几率直接获取到锁的。

这些都是公平锁与非公平锁底层的实现原理，在使用的时候不用追到这么深层次的代码，只需要了解公平锁与非公平锁的含义，并且在调用构造方法时，传入 `true` 或 `false` 即可。

#### 2.2 小结

* **公平锁：**  
多个线程同时执行方法，`线程A` 抢到了锁，`A`可以执行方法。其他线程则在队列里进行排队，`A` 执行完方法后， 会从队列里面取出下一个 `线程B`，再去执行方法。  
以此类推，**对于每一个线程来说都是公平的，即遵守FIFO原则（first in first out先入先出原则），不会存在说后面加入的线程先执行的情况。**
* **非公平锁**  
  多个线程同时执行方法，`线程 A` 抢到了锁，`A` 可以执行方法。但是其他线程并不会排队，`A` 执行完方法释放锁后，其他的线程谁抢到了锁，那谁就去执行方法。  
  **会存在后面加入的线程，比之前加入的线程更先抢到锁的情况。**

**通俗解释：**

* `公平锁`是先到先得,按序进行。
* `非公平锁`就是不排队直接拿。
* `公平锁`保证了锁的获取按照FIFO原则（first in first out即先入先出原则），而代价是进行大量的线程切换（切换到指定的线程）。
* `非公平锁`虽然可能造成线程“饥饿”（存在线程可能一直获取不到锁的情况），但极少的线程切换，保证了其更大的吞吐量。

### 3. 可重入锁（又名递归锁）与不可重入锁
**可重入锁，也叫做递归锁，顾名思义，就是支持重新进入的锁。反之即为不可重入锁。**

可重入锁能够支持一个线程对资源的重复加锁，用于占有锁的线程再次获取锁的场景。  
同一线程中某个外层函数获得锁之后，其内层代码再次获取该锁，形成递归调用，而不受影响；也就是说，线程可以进入任何一个它已经拥有的锁所同步着的代码块。**可重入锁最大的作用是避免死锁**。

`JDK`中的 `ReentrantLock` 即为可重入锁，`synchronized` 也是支持重入的，而 `StampedLock`为不可重入锁（后续详细介绍）。

`StampedLock`不可重入锁演示：

```java
public class LockTest implements Runnable {
    private final StampedLock sl = new StampedLock();
    public void get() {
        long stamp = sl.writeLock();
        try {
            System.out.println("name:" + Thread.currentThread().getName() + " get();");
            set();// set方法又会获取锁，由于StampedLock不支持重入，所以会死锁
        }finally {
            sl.unlock(stamp);
        }
    }

    public  void set() {
        System.out.println("set开始获取StampedLock的写锁");
        long stamp = sl.writeLock();
        try {
            System.out.println("name:" + Thread.currentThread().getName() + " set();");
        }finally {
            sl.unlock(stamp);
        }
    }

    @Override
    public void run() {
        get();
    }

    public static void main(String[] args) {
        LockTest ls = new LockTest();
        new Thread(ls).start();
        new Thread(ls).start();
        new Thread(ls).start();
        new Thread(ls).start();
    }
}
```
执行结果：
```
name:Thread-0 get();
set开始获取StampedLock的写锁
```
可以看到程序只执行到`set`方法的第一个输入语句，即第一个线程就阻塞在了`set`获取锁的位置造成死锁，由此可见`StampedLock`是不支持可重入的。

`synchronized`实现重入锁：

```java
public class LockTest implements Runnable {
    public  synchronized void get() {
        System.out.println("name:" + Thread.currentThread().getName() + " get();");
        set();//set方法又会获取锁，由于synchronized 支持重入，所以不会死锁
    }

    public synchronized  void set() {
        System.out.println("name:" + Thread.currentThread().getName() + " set();");
    }

    @Override
    public void run() {
        get();
    }

    public static void main(String[] args) {
        LockTest ls = new LockTest();
        new Thread(ls).start();
        new Thread(ls).start();
        new Thread(ls).start();
        new Thread(ls).start();
    }
}
```
执行结果：
```
name:Thread-0 get();
name:Thread-0 set();
name:Thread-1 get();
name:Thread-1 set();
name:Thread-2 get();
name:Thread-2 set();
name:Thread-3 get();
name:Thread-3 set();
```

`ReentrantLock`实现重入锁：

```java
public class LockTest implements Runnable {
    private final ReentrantLock lock = new ReentrantLock();
    public void get() {
        lock.lock();
        System.out.println("name:" + Thread.currentThread().getName() + " get();");
        set();// set方法又会获取锁，由于ReentrantReadWriteLock 支持重入，所以不会死锁
        lock.unlock();
    }

    public  void set() {
        lock.lock();
        System.out.println("name:" + Thread.currentThread().getName() + " set();");
        lock.unlock();
    }

    @Override
    public void run() {
        get();
    }

    public static void main(String[] args) {
        LockTest ls = new LockTest();
        new Thread(ls).start();
        new Thread(ls).start();
        new Thread(ls).start();
        new Thread(ls).start();
    }
}
```
执行结果：
```
name:Thread-0 get();
name:Thread-0 set();
name:Thread-1 get();
name:Thread-1 set();
name:Thread-2 get();
name:Thread-2 set();
name:Thread-3 get();
name:Thread-3 set();
```

### 4. 读写锁
#### 4.1 对比描述即代码演示
之前提到锁（如`ReentrantLock`、`StampedLock`）基本都属于`排他锁`（即在同一时刻只允许一个线程进行访问），**而`读写锁`在同一时刻可以允许多个读线程访问，但是在写线程访问时，所有的读线程和其他写线程均被阻塞。**

读写锁维护了一对锁：一个读锁和一个写锁。  
通过分离读锁和写锁，使得并发性相比一般的排他锁有了很大提升。

假设程序中涉及到对一些共享资源的读和写操作，且写操作没有读操作那么频繁。在没有写操作的时候，两个线程同时读一个资源没有任何问题，所以应该允许多个线程能在同时读取共享资源。  
但是如果有一个线程想去写这些共享资源，就不应该再有其它线程对该资源进行读或写，即：

* **读-读能共存**
* **读-写不能共存**
* **写-写不能共存**

未使用读写锁测试读写一起执行的代码如下：
```
public class UnLockTest {
    static Map map = new HashMap<String, Object>();

    /**
     * 读锁演示（暂未加锁）
     * <p>
     * 获取一个key对应的value
     */
    public static final void get(String key) {
        try {
            Thread.sleep(100);
            Object object = map.get(key);
            System.out.println("读的操作,key:" + key + ",value:" + object + " 结束.\n");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    /**
     * 写锁演示（暂未加锁）
     * <p>
     * 设置key对应的value，并返回旧有的value
     */
    public static final void put(String key, Object value) {
        try {
            Thread.sleep(100);
            map.put(key, value);
            System.out.println("写的操作,key:" + key + ",value:" + value + "结束.");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 1; i <= 3; i++) {
                    UnLockTest.put(i + "", i);
                }
            }
        }).start();

        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 1; i <= 3; i++) {
                    UnLockTest.get(i + "");
                }
            }
        }).start();
    }
}
```
执行结果（注：线程执行的随机性，执行结果会不唯一）：
```
线程B：读的操作,key:1,value:null 结束.
线程A：写的操作,key:1,value:1结束.
线程A：写的操作,key:2,value:2结束.
线程B：读的操作,key:2,value:2 结束.
线程B：读的操作,key:3,value:null 结束.
线程A：写的操作,key:3,value:3结束.
```
可以看出读和写用两个线程分别调用`3`次，由于没有加锁，线程执行顺序是不可控的，在数据写入的过程中就执行了读操作，获取的数据即为`null`。

这就需要一个`读/写锁`来解决这个问题。`JDK5`提供了 `ReentrantReadWriteLock` 来实现读写锁。  
使用读写锁之后测试代码如下：

```java
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class LockTest {
    static Map map = new HashMap<String, Object>();
    static ReentrantReadWriteLock rwl = new ReentrantReadWriteLock();
    static Lock r = rwl.readLock();// 读锁
    static Lock w = rwl.writeLock();// 写锁
    /**
     * 读锁演示
     * <p>
     * 获取一个key对应的value
     */
    public static final void get(String threadName, String key) {
        r.lock();
        try {
            Thread.sleep(100);
            Object object = map.get(key);
            System.out.println(threadName + "读的操作,key:" + key + ",value:" + object + " 结束.");
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            r.unlock();
        }
    }

    /**
     * 写锁演示
     * <p>
     * 设置key对应的value，并返回旧有的value
     */
    public static final void put(String threadName, String key, Object value) {
        w.lock();
        try {
            Thread.sleep(100);
            map.put(key, value);
            System.out.println(threadName + "写的操作,key:" + key + ",value:" + value + "结束.");
        } catch (InterruptedException e) {
            e.printStackTrace();
        } finally {
            w.unlock();
        }
    }

    public static void main(String[] args) {
        // 线程A
        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 1; i <= 3; i++) {
                    UnLockTest.put("线程A：", i + "", i);
                }
            }
        }).start();

        // 线程B
        new Thread(new Runnable() {
            @Override
            public void run() {
                for (int i = 1; i <= 3; i++) {
                    UnLockTest.get("线程B：",i + "");
                }
            }
        }).start();
    }
}
```
执行结果（多种情况）：
```
// 1. A线程先获取执行资格
线程A：写的操作,key:1,value:1结束.
线程B：读的操作,key:1,value:1 结束.
线程A：写的操作,key:2,value:2结束.
线程B：读的操作,key:2,value:2 结束.
线程A：写的操作,key:3,value:3结束.
线程B：读的操作,key:3,value:3 结束.

// 2. B线程先获取执行资格
线程B：读的操作,key:1,value:null 结束.
线程A：写的操作,key:1,value:1结束.
线程B：读的操作,key:2,value:null 结束.
线程A：写的操作,key:2,value:2结束.
线程B：读的操作,key:3,value:null 结束.
线程A：写的操作,key:3,value:3结束.

// 或其他（A执行结束，B才开始等等）........
```
上述读写锁演示使用一个非线程安全的`HashMap`进行存取，同时使用读写锁的读锁和写锁来保证`HashMap`的存取是线程安全的。
* 在读操作`get(String threadName, String key)`方法中，需要获取读锁，这使得并发访问该方法时不会被阻塞。
* 写操作`put(String threadName, String key, Object value)`方法，在更新`HashMap`时必须提前获取写锁，当获取写锁后，其他线程对于读锁和写锁的获取均被阻塞，而只有写锁被释放之后，其他读写操作才能继续。
* 使用读写锁提升读操作的并发性，也保证每次写操作对所有的读写操作的可见性。

**一般而言，读写锁的性能都会比排它锁好，因为大多数场景读是多于写的。在读多于写的情况下，读写锁能够提供比排它锁更好的并发性和吞吐量。**

#### 4.2 读写锁几个特性
* **重入性**  
  读写锁允许读线程和写线程按照请求锁的顺序重新获取读取锁或者写入锁。当然了只有写线程释放了锁，读线程才能获取重入锁。  
  写线程获取写入锁后可以再次获取读取锁，但是读线程获取读取锁后却不能获取写入锁。   
  **另外读写锁最多支持`65535`个递归写入锁和`65535`个递归读取锁。**
* **锁降级**  
写线程获取写入锁后可以获取读取锁，然后释放写入锁，这样就从写入锁变成了读取锁，从而实现锁降级的特性。
* **锁升级**  
读取锁是不能直接升级为写入锁的。因为获取一个写入锁需要释放所有读取锁，所以如果有两个读取锁视图获取写入锁而都不释放读取锁时就会发生死锁。
* **锁获取中断**  
读取锁和写入锁都支持获取锁期间被中断。这个和独占锁一致。
* **条件变量**  
写入锁提供了条件变量 **(`Condition`)** 的支持，这个和独占锁一致，但是读取锁却不允许获取条件变量，将得到一个`UnsupportedOperationException`异常。

#### 4.3 读和写的优先级区分
根据实现的不同，读写锁可以分为 **「读优先锁」** 和 **「写优先锁」**。

**读优先锁：** 期望的是读锁能被更多的线程持有，以便提高读线程的并发性。  
它的工作方式是：当`读线程 A` 先持有了`读锁`，`写线程 B` 在获取`写锁`的时候，会被阻塞，并且在阻塞过程中，后续来的`读线程 C` 仍然可以成功获取`读锁`，最后直到`读线程 A` 和 `C` 释放`读锁`后，`写线程 B` 才可以成功获取`读锁`。如下图：

<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/读写锁：读优先锁.png)
</center>

**写优先锁** 期望的是写锁能被更多的线程持有，以便提高写线程的并发性。  
其工作方式是：当`读线程 A` 先持有了`读锁`，`写线程 B` 在获取`写锁`的时候，会被阻塞，并且在阻塞过程中，后续来的`读线程 C` 获取`读锁`时会失败，于是`读线程 C` 将被阻塞在获取`读锁`的操作，这样只要`读线程 A` 释放`读锁`后，`写线程 B` 就可以成功获取`读锁`。如下图：

<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/读写锁：写优先锁.png)
</center>

读优先锁对于读线程并发性更好，但也不是没有问题：
* 如果一直有`读线程`获取`读锁`，那么`写线程`将永远获取不到`写锁`，这就造成了`写线程`**「饥饿」**的现象。
* 如果一直有`写线程`获取`写锁`，`读线程`也会被**「饿死」**。

既然不管优先读锁还是写锁，对方可能会出现饿死问题，通过 **「公平读写锁」** 的方式不优先任何一方。

**公平读写锁比较简单的一种方式是：用队列把获取锁的线程排队（后续会讲到：`AbstractQueuedSynchronizer`（同步器）），不管是写线程还是读线程都按照先进先出的原则加锁即可，这样读线程仍然可以并发，也不会出现「饥饿」的现象。**

### 5. 偏向锁
#### 5.1 简述
大多数情况下锁不仅不存在多线程竞争，而且总是由同一线程多次获得，为了让线程获得锁的代价更低而引入了偏向锁，**偏向锁是锁状态中最乐观的一种锁：从始至终只有一个线程请求同一把锁**。

偏向锁的目的是在某个线程获得锁之后，消除这个线程锁重入（`CAS`）的开销，看起来让这个线程得到了 **偏护**。  

另外，`JVM`对那种会有多线程加锁，但不存在锁竞争的情况也做了优化，听起来比较拗口，但在现实应用中确实是可能出现这种情况：因为线程之前除了互斥关系之外也可能发生同步关系，同步的两个线程（一前一后）对共享对象锁的竞争很可能是没有冲突的。  
对这种情况，`JVM`用一个`epoch`表示一个偏向锁的时间戳（真实地生成一个时间戳代价还是蛮大的，因此这里应当理解为一种类似时间戳的`identifier`）

#### 5.2 偏向锁的设置
**开启偏向锁：**  
偏向锁在`Java 6`和`Java 7`里是默认启用的，但是它在应用程序启动几秒钟之后才激活，
可以使用`JVM`参数来关闭延迟 `-XX：BiasedLockingStartupDelay = 0`。

**关闭偏向锁：**  
如果确定应用程序里所有的锁通常情况下处于竞争状态，可以通过JVM参数关闭偏向锁 `-XX:-UseBiasedLocking=false`，那么默认会进入轻量级锁状态。

#### 5.3 偏向锁的获取
**前提：**  
`JVM`偏向锁(`-XX:+UseBiasedLocking`)默认已开启（确认`instance`可用偏向锁可用），即`Mark Word`偏向锁的标志（偏向模式）为 `1`。

<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/对象头中存储内容.png)
</center>

**具体步骤：**  
当一个线程访问同步块并获取锁时，会在对象头和栈帧中的锁记录里存储锁偏向的`线程ID`，以后该线程在进入和退出同步块时不需要花费`CAS`操作来加锁和解锁，而只需简单的测试一下对象头的`Mark Word`里是否存储着指向当前线程的偏向锁：  

* 如果测试成功，表示线程已经获得了锁，  
* 如果测试失败，则需要再测试下`Mark Word`中偏向锁的标识是否设置成`1`，锁标志位是否为`01`（表示当前是偏向锁）：  
    * 如果没有设置，则使用`CAS`竞争锁，竞争成果后为轻量级锁，
    * 如果设置了，则尝试使用`CAS`将对象头的偏向锁指向当前线程。

#### 5.4 偏向锁的撤销
偏向锁使用了一种 **等到竞争出现才释放锁** 的机制，所以当其他线程尝试竞争偏向锁时，持有偏向锁的线程才会释放锁。

偏向锁的撤销，需要等待全局安全点（在这个时间点上没有字节码正在执行），它会首先暂停拥有偏向锁的线程，然后检查持有偏向锁的线程是否活着：
* 如果线程不处于活动状态，则将对象头设置成无锁状态，
* 如果线程处于活动状态，拥有偏向锁的栈会被执行，遍历偏向对象的锁记录、栈中的锁记录和对象头的`Mark Word`：
    * 要么重新偏向于其他线程，
    * 要么恢复到无锁或者标记对象不适合作为偏向锁，最后唤醒暂停的线程。

#### 5.5 优缺点
**优点**
* 只需要执行一次`CAS`即可获取锁
* 采用延迟释放锁策略
* 锁重入时，只需要判断`Mark_Word.threadId`（持有锁的`线程id`）是否为当前`threadId`即可

**缺点**
* 总体上只针对第一个线程有效，新线程获取锁时，会导致锁膨胀
* 锁膨胀时，会导致`stop the world (STW)`
* 与原生`hashcode()`互斥，导致偏向锁并非适应于所有的`instance`

### 6. 轻量级锁和重量级锁
#### 轻量级锁
* 加锁：线程在执行同步块之前，JVM会先在当前线程的栈桢中创建用于存储锁记录的空间，并将对象头中的`Mark Word`复制到锁记录中，官方称为 `Displaced Mark Word`。  
  然后线程尝试使用`CAS`将对象头中的`Mark Word`替换为指向锁记录的指针；
    - 如果成功，当前线程获得锁，
    - 如果失败，则自旋获取锁，**当自旋获取锁仍然失败时，表示存在其他线程竞争锁（两个或两个以上的线程竞争同一个锁），则轻量级锁会膨胀成重量级锁。**
* 解锁：轻量级解锁时，会使用原子的`CAS`操作来将`Displaced Mark Word`替换回到对象头；
    * 如果成功，则表示同步过程已完成。
    * 如果失败，表示有其他线程尝试过获取该锁，则要在释放锁的同时唤醒被挂起的线程。

#### 重量级锁
重量锁在`JVM`中又叫对象`监视器（Monitor）`，它很像`C`中的`Mutex`，除了具备`Mutex(0|1)`互斥的功能，它还负责实现了 **`Semaphore(信号量)`** 的功能。  
也就是说它 **至少包含一个竞争锁的队列，和一个信号阻塞队列（wait队列）**：

* 竞争锁的队列负责做互斥
* 信号阻塞队列用于做线程同步。

### 7. 自旋锁
#### 7.1 产生背景
**`Java`的线程是映射到操作系统的原生线程之上的**，如果要阻塞或唤醒一个线程，都需要操作系统来完成，**这就需要从用户态转换到核心态中**。  
因此状态装换需要耗费很多的处理器时间，对于代码简单的同步块（如一般对象中被`synchronized`修饰的`getter()`和`setter()`方法），状态转换消耗的时间有可能比用户代码执行的时间还要长。

虚拟机的开发团队注意到在许多应用上，**共享数据的锁定状态只会持续很短的一段时间**，为了这段时间取挂起和恢复现场并不值得。  
**如果物理机器有一个以上的处理器，能让两个或以上的线程同时并行执行，就可以让后面请求锁的那个线程 “稍等一下”，但不放弃处理器的执行时间，看看持有锁的线程是否很快就会释放锁。**  

为了让线程等待，我们只需让线程执行一个忙循环（自旋操作），这项技术就是所谓的 <font color="red">**自旋锁**</font>。

#### 7.2 详述
**自旋锁：** 是指尝试获取锁的线程不会立即阻塞，而是采用循环的方式去尝试获取锁，这样的 **好处是减少线程上下文切换的消耗，缺点是循环会消耗CPU**

**线程的上下文切换：** 当两个线程是属于同一个进程，**因为虚拟内存是共享的，所以在切换时，虚拟内存这些资源就保持不动，只需要切换线程的私有数据、寄存器等不共享的数据。**

如何自旋呢？就是如果发现目标对象锁定了，不是睡眠等待持有该对象的锁释放，而是采用让当前线程不停地的在循环体内执行（尝试获取锁），当循环的条件被其他线程改变时才能进入临界区。

> **自旋是在轻量级锁中使用的**，在重量级锁中，线程不使用自旋。  

示例代码：
```java
/**
 * 自旋锁测试
 * 
 * 1.6 版本后使用了自适应自旋锁：
 * 自旋次数通常由前一次在同一个锁上的自旋时间及锁的拥有者的状态决定。
 * 如果线程A自旋成功，自旋次数为17次，那么等到下一个线程B自旋时，也会默认认为B自旋17次成功；
 * 如果B自旋了5次就成功了，那么此时这个自旋次数就会缩减到5次。
 * 
 * 自适应自旋锁随着程序运行和性能监控信息，从而使得虚拟机可以预判出每个线程大约需要的自旋次数
 */
public class SpinLockTest {
    // AtomicReference  原子方式更新对象引用，保证多线程下操作该对象进行更新时，避免出现脏读，只要有一个线程改变，其他线程不会在改变该值
    AtomicReference<Thread> atomicReference = new AtomicReference<>();

    public void myLock() {
        Thread thread = Thread.currentThread();
        System.out.println(Thread.currentThread().getName() + "\t come in...");
        /**
         * compareAndSet方法解释：
         * 如果AtomicReference对象的当前值等于期望值，则使用AtomicReference类的compareAndSet()方法以原子方式将newValue的值设置为AtomicReference对象，
         * 如果操作成功，则返回true，否则返回false。
         *
         * 此方法使用设置的内存语义更新值，就像将该变量声明为volatile一样
         */
        while (!atomicReference.compareAndSet(null, thread)) {
        }
    }

    public void myUnLock() {
        Thread thread = Thread.currentThread();
        System.out.println(atomicReference.compareAndSet(thread, null));
        System.out.println(Thread.currentThread().getName() + "\t invoked myUnLock()");
    }

    public static void main(String[] args) {
        SpinLockTest spinLockTest = new SpinLockTest();
        // 线程A
        new Thread(() -> {
            spinLockTest.myLock();
            try {
                //暂停一会线程
                TimeUnit.SECONDS.sleep(5);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            spinLockTest.myUnLock();
        }, "AA").start();

        try {
            //暂停一会线程，目的是为了A线程在B线程前面执行
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 线程B
        new Thread(() -> {
            spinLockTest.myLock();
            try {
                //暂停一会线程
                TimeUnit.SECONDS.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            spinLockTest.myUnLock();
        }, "BB").start();
    }
}
```
运行结果：
```
AA	 come in...
BB	 come in...
AA	 invoked myUnLock()
BB	 invoked myUnLock()
```
#### 7.3 总结
* **自旋等待不能代替阻塞。**   
  自旋等待本身虽然避免了线程切换的开销，但它是要占用处理器时间的：
  * **如果锁被占用的时间很短，自旋等待的效果就会非常好；**
  * **反之，如果锁被占用的时间很长，那么自旋的线程只会白白浪费处理器资源。**  
    因此，自旋等待的时间必须要有一定的限度，**如果自旋超过了限定次数（默认是`10`次，可以使用`-XX:PreBlockSpin`来更改）没有成功获得锁，就应当使用传统的方式去挂起线程了**。
* 自旋锁在`JDK1.4.2`中引入，**使用`-XX:+UseSpinning`来开启。** `JDK6`中已经变为默认开启，并且引入了自适应的自旋锁。自适应意味着自旋的时间不在固定了，而是由前一次在同一个锁上的自旋时间及锁的拥有者的状态来决定：
    * 同一对象加锁，如果`线程A`自旋成功，此时自旋次数为17次，那么等到下一个`线程B`自旋时，也会默认认为`B`自旋17次成功；
    * 如果`B`自旋了5次就成功了，那么此时这个自旋次数就会缩减到5次。
* 如果在同一个锁对象上，自旋等待刚刚成功获得过锁，并且持有锁的线程正在运行中，那么虚拟机就会认为这次自旋也是很有可能再次成功，进而它将允许自旋等待持续相对更长的时间，比如增加循环次数。    
* 如果对于某个锁，自旋很少成功获得过，那在以后要获取这个锁时将可能省略掉自旋过程，以避免浪费处理器资源（避免重复的执行很少成功的循环）。
* **由于自旋锁使用者一般保持锁时间非常短，因此选择自旋而不是睡眠是非常必要的，自旋锁的效率远高于互斥锁。**

**自旋锁与互斥锁区别：**
* 互斥锁：线程会从`sleep`（加锁）——>`running`（解锁），过程中有`线程上下文的切换`，`cpu的抢占`，`信号的发送` 等开销。
* 自旋锁：线程一直是`running`(加锁——>解锁)，死循环检测锁的标志位，目标对象无锁就获取锁。

### 补充：死锁
#### (1). 代码演示
```java
public class DieLockTest {
    public static void main(String[] args) {
        Object o1 = new Object();
        Object o2 = new Object();
        //线程1 拥有 o1 试图获取 o2
        new Thread(() -> {
            synchronized (o1) {
                System.out.println("获取 o1 成功");
                try {
                    // 这里的暂停是为了让线程2持有o2
                    TimeUnit.SECONDS.sleep(3);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                synchronized (o2) {
                    System.out.println(Thread.currentThread().getName());
                }
            }
        }).start();

        //线程2 拥有 o2 试图获取 o1
        new Thread(() -> {
            synchronized (o2) {
                System.out.println("获取 o2 成功");
                try {
                    TimeUnit.SECONDS.sleep(3);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                synchronized (o1) {
                    System.out.println(Thread.currentThread().getName());
                }
            }
        }).start();
    }
}
```
`线程1`拥有`o1`的情况下试图拥有`o2`，`线程2`有`o2`试图拥有`o1`，造成死锁。

#### (2). 主要原因和四个必要条件
**产生死锁的原因主要是：**

1. 系统资源不足：如果系统资源充足，进程的资源请求都能够得到满足，死锁出现的可能性就很低
2. 进程运行推进的顺序不合理。
3. 资源分配不当等......

**<font color="red">产生死锁的四个必要条件：</font>**
1. **互斥：** 某一资源一次只允许一个进程访问，即该资源一旦分配给某个进程，其他进程就不能再访问，直到该进程访问结束。
2. **不可抢占（不可剥夺）：** 线程已获得的资源，在末使用完之前，不能被其他线程强行剥夺。
3. **请求与保持（占有且等待）：** 一个进程本身占有资源（一种或多种），同时还有资源未得到满足，正在等待其他进程释放该资源，对已获得的资源保持不放。
4. **循环等待：** 若干进程之间形成一种头尾相接的循环等待资源关系。

当以上四个条件均满足，必然会造成死锁，发生死锁的进程无法进行下去，它们所持有的资源也无法释放。这样会导致CPU的吞吐量下降。  
所以死锁情况是会浪费系统资源和影响计算机的使用性能的。

#### (3). 避免死锁
对于以上产生死锁的 **四个必要条件**，只要破坏其中一个条件，就可以避免死锁的发生。

1. **避免多次锁定：**   
尽量避免同一个线程对多个资源的锁进行锁定（持有），即一个线程持有多个资源的锁。
2. **具有相同的加锁顺序：**   
如果多个线程需要对多个资源的锁进行锁定（持有），则应该保证它们以相同的顺序请求加锁。  
如上面的代码演示：线程1拥有o1的情况下试图拥有o2，线程2有o2试图拥有o1，造成死锁。
3. **使用定时锁：**  
线程获取锁的时候加上一定的时限，超过时限则放弃对该锁的持有，并释放自己占有的锁。
4. **死锁检测：**  
死锁检测是一种依靠算法（`银行家算法`）机制来实现的死锁预防机制，它主要是针对那些不可能实现按序加锁，也不能使用定时锁的场景的。


## 四、volatile
### 1. 简述
`volatile`作为`java`中的关键字之一，用于声明变量的值会随时被别的线程修改，使用`volatile`修饰的变量会强制将修改的值立即写入主存，**主存中的值会使缓存中的值失效**  
（`非volatile变量`不具备这样的特性，`非volatile变量`的值会被缓存，如`线程A`更新了这个值，`线程B`读取到这个变量的值可能并不是`线程A`修改后的值）。

**`volatile`具有`可见性`、`有序性（防止指令重排）`，但是`不具备原子性`：**

* **可见性：** 不会被缓存在寄存器或者对其他处理器不可见的地方，当多个线程访问同一个变量A时，线程1修改了A的值，其他线程能够立即读取到A最新的值。
* **有序性：** 即程序按照书写的先后顺序执行，这主要是防止指令重排序的问题。  
在java的内存模型中，允许编译器和处理器对指令进行重新排序。重排序的指令不会影响到单个线程的执行，却会影响并发执行的正确性。
* **原子性：** 类比事务的原子性，通常原子性指多个操作不存在只执行一部分的情况，如果全部执行完成没有问题，如果只执行了部分，那就得撤销（事务回滚）已经执行的部分。

**验证`volatile`不具备原子性**  
`i++` 的原子性问题：`i++ `的操作实际上分为三个步骤“`读`--->`改`--->`写`”

```java
public class VolatileTest {
    public static void main(String[] args) {
        // 调用5次计数方法
        for (int i = 0; i < 5; i++) {
            count();
        }
    }

    /**
     * 计数：每次10个线程分别对MyTest中的number变量自增2000，期望值是2000*10=20000
     */
    public static void count(){
        MyTest myTest = new MyTest();
        /**
         * 10个线程创建出来，每个线程执行2000次num++操作
         * i++执行的三个操作：先取值，再计算，再赋值操作
         */
        for (int i = 0; i < 10; i++) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    for (int j = 0; j < 2000; j++) {
                        myTest.add();
                    }
                }
            }, String.valueOf(i)).start();
        }

        // 这里规定线程数大于2，一般有GC线程以及main主线程
        while (Thread.activeCount() > 2) {
            // 否则让出cup时间片
            Thread.yield();
        }
        //打印number的值
        System.out.println(Thread.currentThread().getName() + " : " + myTest.number);
    }
}

class MyTest {
    // volatile修饰的number作为计数器
    volatile int number = 0;
    public void add() {
        number++;
    }
}
```
执行结果：
```
main : 17066
main : 19010
main : 17401
main : 18566
main : 19825
```
### 2. 适用场景
#### 2.1 状态标志
有时候实现 `volatile` 变量的规范使用仅仅是使用一个布尔状态标志，用于指示发生了一个重要的一次性事件。  
例如完成初始化或请求停机：

```java
// 标志停机状态
volatile boolean shutdownRequested;  
  
...  

// 停机
public void shutdown() {   
    shutdownRequested = true;   
}  

// 执行
public void doWork() {   
    // 一直循环判断是否停机
    while (!shutdownRequested) {   
        // todo  
    }  
}
```
线程A执行 `doWork()` 的过程中，可能有另外的线程B调用了`shutdown()`，所以`boolean变量`必须是`volatile`。

而如果使用 `synchronized` 块编写循环要比使用 `volatile` 状态标志编写麻烦很多。  
由于 `volatile` 简化了编码，并且状态标志并不依赖于程序内任何其他状态，因此此处非常适合使用 `volatile`。

<font color="red">这种类型的状态标记的一个公共特性是：**通常只有一种状态转换；**`shutdownRequested` 标志从 `false` 转换为 `true` ，然后程序停止。</font>  
这种模式可以扩展到来回转换的状态标志，但是只有在转换周期不被察觉的情况下才能扩展（从`false` 到`true`，再转换到`false`）。此外，还需要某些原子状态转换机制，**如原子变量（原子类）** 。

#### 2.2 一次性安全发布（one-time safe publication）
**在缺乏同步的情况下，可能会遇到某个对象引用的更新值（由另一个线程写入）和该对象状态的旧值同时存在。**

这就是造成著名的双重检查锁定（`DCL：double-checked-locking`）问题的根源，其中对象引用在没有同步的情况下进行读操作，产生的问题是您可能会看到一个更新的引用，但是仍然会通过该引用看到不完全构造的对象。

如下面的双重检查锁定的单例模式：
```java
private volatile static Singleton instace;     
    
public static Singleton getInstance(){     
    // 第一次null检查       
    if(instance == null){              
        synchronized(Singleton.class) {         
            // 第二次null检查         
            if(instance == null){             
                instance = new Singleton();    
            }    
        }             
    }    
    return instance;   
}
```
`volatile` 类型的引用可以确保对象创建的可见性，但是如果对象的状态在创建后将发生更改，那么就需要额外的同步。

#### 2.3 独立观察（independent observation）
使用 `volatile` 的另一种场景是：定期 **“发布”** 观察结果供程序内部使用。  
如：假设有一种环境传感器能够感觉环境温度，一个后台线程可能会每隔几秒读取一次该传感器，并更新当前文档的 `volatile` 变量。然后，其他线程可以读取这个变量，从而随时能够看到最新的温度值。

**使用该模式的另一种应用场景就是收集程序的统计信息。**

如下面的代码展示了身份验证机制如何记忆最近一次登录的用户的名字。将反复使用`lastUser` 引用来发布值，以供程序的其他部分使用。（主要利用了`volatile`的可见性）
```java
public class UserManager {  
    public volatile String lastUser; //发布的信息  
  
    public boolean authenticate(String user, String password) {  
        boolean valid = passwordIsValid(user, password);  
        if (valid) {  
            User u = new User();  
            activeUsers.add(u);  
            lastUser = user;  
        }  
        return valid;  
    }  
}
```

#### 2.4 “volatile bean” 模式
**`volatile bean` 模式的基本原理是：很多框架为易变数据的持有者提供了容器，但是放入这些容器中的对象必须是线程安全的。**

在 `volatile bean 模式`中，`JavaBean` 被用作一组具有 `getter` 和/或 `setter` 方法 的独立属性的容器，且该`bean`的所有数据成员都是 `volatile` 类型的，并且 `getter` 和 `setter` 方法必须非常普通——即除了获取或设置相应的属性外，不能包含任何逻辑！

此外，**对于对象引用的数据成员，引用的对象必须是有效不可变的。（这将禁止具有数组值的属性，因为当数组 引用被声明为 `volatile` 时，只有引用而不是数组本身具有 `volatile` 语义）。**   
对于任何 `volatile` 变量，不变式或约束都不能包含 `JavaBean` 属性。

如以下示例代码展示了遵守 `volatile bean` 模式的 `JavaBean`：
```java
public class Person {  
    private volatile String firstName;  
    private volatile String lastName;  
    private volatile int age;  
  
    public String getFirstName() { return firstName; }  
    public String getLastName() { return lastName; }  
    public int getAge() { return age; }  
  
    public void setFirstName(String firstName) {   
        this.firstName = firstName;  
    }  
  
    public void setLastName(String lastName) {   
        this.lastName = lastName;  
    }  
  
    public void setAge(int age) {   
        this.age = age;  
    }  
}
```

#### 2.5 开销较低的“读－写锁”策略
由于仅使用 `volatile` 的还不足以实现线程安全的计数器（在上面简述`volatile`的介绍中已验证），因为它不是原子性的，且 `++x` 实际上是三种操作（读、计算、写）的简单组合。

所以当读操作远远超过写操作，可以结合使用内部锁（如：`synchronized`）和 `volatile` 变量的方式来减少公共代码路径的开销。

如下实现了的线程安全的计数器，使用 `synchronized` 确保增量操作是原子的，并使用 `volatile` 保证当前结果的可见性。**如果更新不频繁的话，该方法可实现更好的性能，因为读路径的开销仅仅涉及 `volatile` 读操作，** 这通常要优于一个无竞争的锁获取的开销。

引入依赖：
```xml
<dependency>
    <groupId>net.jcip</groupId>
    <artifactId>jcip-annotations</artifactId>
    <version>1.0</version>
</dependency>
```
```java
public class VolatileTest {
    public static void main(String[] args) {
        // 调用5次计数方法
        for (int i = 0; i < 5; i++) {
            count();
        }
    }

    /**
     * 计数：每次10个线程分别对MyTest中的number变量自增2000，期望值是2000*10=20000
     */
    public static void count() {
        MyTest myTest = new MyTest();
        /**
         * 10个线程创建出来，每个线程执行2000次num++操作
         * i++执行的三个操作：先取值，再计算，再赋值操作
         */
        for (int i = 0; i < 10; i++) {
            new Thread(new Runnable() {
                @Override
                public void run() {
                    for (int j = 0; j < 2000; j++) {
                        myTest.add();
                    }
                }
            }, String.valueOf(i)).start();
        }

        /**
         * 这里规定线程数大于1
         * 原代码解释：这里规定线程数大于2，一般有GC线程以及main主线程
         *
         * 但是测试中发现，GC线程由于是守护线程，几乎不会和我们的测试线程竞争；
         * 并且在测试中发现此处大于2时，测试的线程还未执行完 ，故改为了线程数大于1.
         */
        // Thread.currentThread().getThreadGroup().list();
        // System.out.println(Thread.activeCount());
        while (Thread.activeCount() > 1) {
            // 否则让出cup时间片，供测试的线程执行
            Thread.yield();
        }

        //打印number的值
        System.out.println(Thread.currentThread().getName() + " : " + myTest.getNumber());
    }
}

class MyTest {
    // volatile修饰的number作为计数器
    // Employs the cheap read-write lock trick
    // All mutative operations MUST be done with the 'this' lock held
    @GuardedBy("this")
    private volatile int number;

    // 写操作：必须synchronized。因为x++不是原子操作
    public synchronized void add() {
        number++;
    }

    // 读操作，没有synchronized，提高性能
    public int getNumber() {
        return number;
    }
}
```
使用锁进行所有变化的操作，使用 `volatile` 进行只读操作。其中，锁一次只允许一个线程访问值，`volatile` 允许多个线程执行读操作。

<font color="red">**特别说明：**</font>
* 使用 **`Thread.yield();`** 的原因：
    **`Thread.yield();`** 方法先检测当前是否有相同优先级的线程处于同可运行状态，如有，则把 `CPU` 的占有权交给此线程（即上述代码测试的线程），否则继续运行原来的线程。
* **`Thread.yield();`** 处的线程让出`CPU`的限制数改为`1`是因为：
    
    * 测试中发现，`GC线程` 由于是守护线程，几乎不会和我们的测试线程竞争；
    * 当此处大于`2`时，测试的线程还未执行完 ，故改为了线程数大于`1`.
* `MyTest类`中修饰变量`number`的时候，所使用的注解 **`@GuardedBy("this")`**：表示这个状态变量，这个方法被哪个锁保护着，基本用法是 **`@GuardedBy(lock)`**，有以下几种使用形式：
    
    * **@GuardedBy("this")：** 受对象内部锁保护
    * **@GuardedBy("fieldName")：** 受与fieldName引用相关联的锁 保护。
    * **@GuardedBy("ClassName.fieldName")：** 受一个类的静态field的锁 保存。
    * **@GuardedBy("methodName()")：** 锁对象是 methodName() 方法的返值，受这个锁保护。
    * **@GuardedBy( "ClassName.class")：** 受ClassName类的直接锁对象保护。而不是这个类的某个实例的锁对象。
    
   

### 3. 补充：happens-before原则
**`happens-before原则的规则：`**

* **程序次序规则：** 一个线程内，按照代码顺序，书写在前面的操作先行发生于书写在后面的操作；
* **锁定规则：** 一个`unLock`操作先行发生于后面对同一个锁的`lock`操作；
* **volatile变量规则：** 对一个变量的写操作先行发生于后面对这个变量的读操作；
* **传递规则：** 如果`操作A`先行发生于`操作B`，而`操作B`又先行发生于`操作C`，则可以得出`操作A`一定先行发生于`操作C`；
* **线程启动规则：** `Thread`对象的`start()`方法先行发生于此线程的每个一个动作；
* **线程中断规则：** 对线程`interrupt()`方法的调用先行发生于被中断线程的代码检测到中断事件的发生；
* **线程终结规则：** 线程中所有的操作都先行发生于线程的终止检测，我们可以通过`Thread.join()`方法结束、`Thread.isAlive()`的返回值手段检测到线程已经终止执行；
* **对象终结规则：** 一个对象的初始化完成先行发生于他的`finalize()`方法的开始；  

**这里就讲到了`volatile`变量：这是一条比较重要的规则，它标志着`volatile`保证了线程可见性。**

通俗点讲就是如果一个线程先去写一个`volatile`变量，然后一个线程去读这个变量，那么这个写操作一定是 **`happens-before`** 读操作的。

## 五、synchonrize
### 简单了解线程（详细内容参考其他笔记）： 

<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/线程流程图.png)
</center>

主要是搞清楚, `sleep`, `yield`, `wait`, `notify`和`notifyAll`对于锁的处理，（线程详细介绍参考其他笔记）简单比较如下:

| 方法  | 是否释放锁 | 备注                                                         |
| ----- | ---------- | ------------------------------------------------------------ |
| wait  | 是         | wait和notify/notifyAll是成对出现的, 必须在synchronize块中被调用 |
| sleep | 否         | 可使低优先级的线程获得执行机会                               |
| yield | 否         | yield方法使当前线程让出CPU占有权, 但让出的时间是不可设定的   |
* `wait`有出让Object锁的语义, 要想出让锁, 前提是要先获得锁， 所以要先用`synchronized`获得锁之后才能调用`wait`；  

* `notify`原因类似, `Object.wait()`和`notify()`不具有原子性语义, 所以必须用`synchronized`保证线程安全。

* `yield()`方法对应了如下操作：  
  先检测当前是否有相同优先级的线程处于同可运行状态, 

  * 如有，则把 `CPU` 的占有权交给此线程, 
  * 否则继续运行原来的线程。 

  所以`yield()`方法也被称为 **“退让”** , 因为它把运行机会让给了同等优先级的其他线程。

### 1. synchronized加锁方式
`synchronized`是`jvm`中的一个关键字，它有两种使用方式（加在方法上或者代码块上）：  
加在方法上：

```java
synchronized void foo() {
    //...
}
```
* 如果加在方法上且当前方法是非"`static`"方法，则锁住的是当前类的实例
* 如果该方法是"`static`"的，则锁住的是当前类的`class`对象。 

加在代码块上：
```java
void foo() {
    synchronized(lock) {
        //...
    }
}
```
对于加在代码块的锁，锁住的是'`lock`'代表的对象。

### 2. synchronized锁特性
* `synchronized锁`是`JVM`提供的内置锁。
* `synchronized锁`是非公平的锁，并且是阻塞的，不支持锁请求中断。
* `synchronized锁`是可重入的，所谓可重入是指同一个线程获取到某个对象的锁之后在未释放锁之前还可以通过`synchronized`再次获取锁，而不会阻塞。

一个对象在`JVM`中的内存布局包括 **对象头**、**实例数据** 和 **对齐填充**，`synchronized`锁就是通过`对象头`来实现锁的。
<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/实例对象和数组对象简图.png)
</center>

**`synchronized`还支持偏向锁、轻量级锁和重量级锁。**  

`synchronized`的`偏向锁`、`轻量级锁`以及`重量级锁`都是通过**Java对象头**实现的。  
**Java对象的内存布局分为：对象头、实例数据和对其填充**，而**对象头又可以分为”`Mark Word`”和`类型指针（Class Pointer）`** 。  
`synchronized`的偏向锁、轻量级锁以及重量级锁是通过 **Java对象头** 实现的。  

**Java对象的内存布局分为：`对象头`、`实例数据`和`对其填充`；而`对象头`又可以分为`”Mark Word”`和`类型指针（Class Pointer）`** 。  

**`”Mark Word”`是关键，默认情况下（`无锁`），其存储对象的`HashCode`、`分代年龄`和`锁标记位`** 。


<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/对象头中存储内容.png)
</center>

注意到无锁和偏向锁在 **”Mark Word”** 的倒数第三bit位中中分别采用`0`和`1`标记。

整个`synchronized`锁流程如下（和`锁膨胀过程`一样）：
- 检测`Mark Word`里面是不是当前`线程的ID`，如果是，表示当前线程**处于偏向锁**；
- 如果不是，则使用`CAS`将当前线程的ID替换`Mard Word`，如果成功则表示当前线程获得`偏向锁`，置偏向标志位`1`；
- 如果失败，则说明发生竞争，`撤销偏向锁`，进而升级为**轻量级锁**；
- 当前线程使用`CAS`将对象头的`Mark Word`替换为锁记录指针，如果成功，当前线程获得锁；
- 如果失败，表示其他线程竞争锁，当前线程便尝试使用**自旋**来获取锁；
- 如果自旋成功则依然处于`轻量级`状态；
- 如果自旋失败，则升级为`重量级锁`。

### 3. synchronized和volatile比较

* 简单的说就是`synchronized`的代码块是 **确保`可见性`和`原子性`的** ，`volatile`只能确保可见性 
* **当且仅当下面条件全部满足时, 才能使用`volatile`**
    * 对变量的写入操作不依赖于变量的当前值，( `++i`/`i++`这种肯定不行)，或者能确保只有单个线程在更新；
    * 该变量不会与其他状态变量一起纳入不变性条件中；
    * 访问变量时不需要加锁。

### 4. synchonrize和juc中的锁比较
> 和其他`JUC`的锁比较，（详见：五、JUC下locks部分锁简介）

就常用的`ReentrantLock`（重入锁）在内存上的语义于`synchronize`相同, 但是它提供了额外的功能, 可以作为一种高级工具。

当需要一些 **可定时**, **可轮巡**, **可中断** 的锁获取操作, 或者希望使用公平锁, 或者使用非块结构的编码时 才应该考虑`ReetrantLock`。

### 5. 小结
* 在业务并发简单清晰的情况下推荐 `synchronized`, 
* 在业务逻辑并发复杂, 或对使用锁的扩展性要求较高时, 推荐使用 `ReentrantLock`这类锁。

**今后`JVM`的优化方向一定是基于底层`synchronize`的， 性能方面应该选择`synchronize`**

## 五、JUC下locks部分锁简介
`java.util.concurrent`（JUC）包中主要有`locks包`和`atomic包`：

* `locks包`中提供了`Lock锁`：包括 **可重入锁（`ReentrantLock`）**，**可重入读写锁（`ReentrantReadWriteLock`）**，和 **`StampedLock`** 等。
* `atomic包`中提供了基于 **"`CAS`"（Compare And Set）** 的`乐观锁`的一些`原子类`。

### 1. AbstractQueuedSynchronizer（抽象同步器队列）
`JUC中`的锁分两种：`可重入锁`、`读写锁`。

两者都用到了一个通用组件 **`AbstractQueuedSynchronizer`**

**`AbstractQueuedSynchronizer`：** 利用了一个`int`来表示状态, 内部基于`FIFO`队列及 `UnSafe` 的`CAS`原语作为操纵状态的数据结构，**AQS（即`AbstractQueuedSynchronizer`）** 以单个 int 类型的原子变量来表示其状态，定义了4个抽象方法（ `tryAcquire(int)`、`tryRelease(int)`、`tryAcquireShared(int)`、`tryReleaseShared(int)`，**前两个方法用于独占/排他模式，后两个用于共享模式** ）留给子类实现，用于自定义`同步器`的行为以实现特定的功能。

> `同步器`是实现锁的关键，利用`同步器`将锁的语义实现，然后在锁的实现中`聚合同步器`。  
>
> 可以这样理解：锁的`API`是面向使用者的，它定义了与锁交互的公共行为，而每个锁需要完成特定的操作也是透过这些行为来完成的（比如：可以允许两个线程进行加锁，排除两个以上的线程），但是实现是依托给`同步器`来完成；  
>
> `同步器`面向的是线程访问和资源控制，它定义了线程对资源是否能够获取以及线程的排队等操作；  
> 锁和`同步器`很好的隔离了二者所需要关注的领域，严格意义上讲，同步器可以适用于除了锁以外的其他同步设施上（包括锁）。

### 2. ReentrantLock（可重入锁）
**支持公平和非公平策略（`FairSync`/`NonFairSync`）, 默认非公平锁，内部`Sync`继承于 `AbstractQueuedSynchronizer`**

`FairSync`/`NonFairSync`两者代码区别是:  
`FairSync`代码中对于尝试加锁时（`tryAcquire(int)`）多了一个判断方法， 判断等待队列中是否还有比当前线程更早的， 如果为空，或者当前线程线程是等待队列的第一个时才占有锁。

`tryAcquire(int)`源码：
```java
/**
 * Sync object for fair locks
 */
static final class FairSync extends Sync {
    private static final long serialVersionUID = -3000897897090466540L;

    final void lock() {
        acquire(1);
    }

    /**
     * Fair version of tryAcquire.  Don't grant access unless
     * recursive call or no waiters or is first.
     */
    protected final boolean tryAcquire(int acquires) {
        final Thread current = Thread.currentThread();
        int c = getState();
        if (c == 0) {
            if (!hasQueuedPredecessors() &&
                compareAndSetState(0, acquires)) {
                setExclusiveOwnerThread(current);
                return true;
            }
        }
        else if (current == getExclusiveOwnerThread()) {
            int nextc = c + acquires;
            if (nextc < 0)
                throw new Error("Maximum lock count exceeded");
            setState(nextc);
            return true;
        }
        return false;
    }
}
```
更多`ReentrantLock`的介绍详见上文 **（三、不同的锁详解 —— 3. 公平锁与非公平锁）**

### 3. ReentrantReadWriteLock（可重入读写锁）
**`ReentrantLock`获取的是排它锁，而`ReentrantReadWriteLock`是一种读写锁分离的锁。**

> 读写锁详见上文（三、不同的锁详解 —— 4. 读写锁）

在写锁没有被获取的情况下，多线程并发获取写锁不会出现阻塞，在读多写少的情况下使用`ReentrantReadWriteLock`有明显的优势。

源码分析（读锁）:
```java
public static class ReadLock implements Lock, java.io.Serializable  {
    private final Sync sync;
    protected ReadLock(ReentrantReadWriteLock lock) {
        sync = lock.sync;
    }

    public void lock() {
        sync.acquireShared(1);//共享锁
    }

    public void lockInterruptibly() throws InterruptedException {
        sync.acquireSharedInterruptibly(1);
    }

    public  boolean tryLock() {
        return sync.tryReadLock();
    }

    public boolean tryLock(long timeout, TimeUnit unit) throws InterruptedException {
        return sync.tryAcquireSharedNanos(1, unit.toNanos(timeout));
    }

    public  void unlock() {
        sync.releaseShared(1);
    }

    public Condition newCondition() {
        throw new UnsupportedOperationException();
    }
}
```

源码分析（写锁）:
```java
public static class WriteLock implements Lock, java.io.Serializable  {
    private final Sync sync;
    protected WriteLock(ReentrantReadWriteLock lock) {
        sync = lock.sync;
    }
    public void lock() {
        sync.acquire(1);//独占锁
    }
    public void lockInterruptibly() throws InterruptedException {
        sync.acquireInterruptibly(1);
    }

    public boolean tryLock( ) {
        return sync.tryWriteLock();
    }

    public boolean tryLock(long timeout, TimeUnit unit) throws InterruptedException {
        return sync.tryAcquireNanos(1, unit.toNanos(timeout));
    }

    public void unlock() {
        sync.release(1);
    }

    public Condition newCondition() {
        return sync.newCondition();
    }

    public boolean isHeldByCurrentThread() {
        return sync.isHeldExclusively();
    }

    public int getHoldCount() {
        return sync.getWriteHoldCount();
    }
}
```
**对比源码可以看到，`ReadLock`获取的是共享锁，`WriteLock`获取的是独占锁。**

`WriteLock` 就是一个`独占锁（排他锁）`，这和`ReentrantLock`里面的实现几乎相同，都是使用了 `AQS`（即`AbstractQueuedSynchronizer`） 的 **`acquire（获取）/release（发布、释放）`** 操作。

`AQS`中有一个`state`字段（`int`类型，32位）用来描述有多少线程获持有锁：

* 在`独占锁`的时候这个值通常是`0`或者`1` **（如果是重入的就是重入的次数）**，
* 在`共享锁`的时候就是持有锁的数量。

`ReadWriteLock`（`ReentrantReadWriteLock`实现自`ReadWriteLock`）的读、写锁是相关但是又不一致的，所以需要两个数来描述`读锁（共享锁）`和`写锁（独占锁）`的数量。  
显然现在一个`state`就不够用了，于是在`ReentrantReadWriteLock`里面将这个字段一分为二：

* `高位16位`表示`共享锁`的数量，
* `低位16位`表示`独占锁`的数量（或者`重入数量`）。  
**`2^16-1=65536，所以共享锁和独占锁的数量最大只能是65535。`**

`ReentrantReadWriteLock`中**state** 的相关源码：
```java
/**
 * The synchronization state.
 * 同步状态。
 */
private volatile int state;

/**
 * 返回同步状态的当前值。
 * Returns the current value of synchronization state.
 * This operation has memory semantics of a {@code volatile} read.
 * @return current state value
 */
protected final int getState() {
    return state;
}
```

**获取锁（`acquire`）源码分析：**

```java
protected final boolean tryAcquire(int acquires) {
    Thread current = Thread.currentThread();
    // 同步状态（读锁线程数量、写锁重入数量）
    int c = getState();
    // 写线程数
    int w = exclusiveCount(c);
    // 1. 同步状态不为0，读和写的数量不能都为0
    if (c != 0) {
        // 2. 如果写线程数（w）为0（那么读线程数就不为0）或者独占锁线程（持有锁的线程）不是当前线程就返回失败
        if (w == 0 || current != getExclusiveOwnerThread())
            return false;
        // 3. 写锁的数量（重入数）大于65535就抛出一个Error异常
        if (w + exclusiveCount(acquires) > MAX_COUNT)
            throw new Error("Maximum lock count exceeded");
    }
    // 4. 如果当且写线程数位0（那么读线程也应该为0，因为步骤1已经处理c!=0的情况），并且当前线程需要阻塞那么就返回失败；如果当且写线程数位0（那么读线程也应该为0，因为步骤1已经处理c!=0的情况），并且当前线程需要阻塞那么就返回失败
    if ((w == 0 && writerShouldBlock(current)) || !compareAndSetState(c, c + acquires))
        return false;
    // 5.设置独占线程（写线程）为当前线程，返回true。
    setExclusiveOwnerThread(current);
    return true;
}
```

### 4. StampedLock
**首先`StampedLock`锁是不可重入的。`StampedLock`的思想是：读请求不仅不应该阻塞读请求（对应于ReentrantReadWriteLock），也不应该阻塞写请求。**

`StampedLock`控制锁有三种模式 **（写，读，乐观读）**，一个`StampedLock`状态是由版本和模式两个部分组成，锁获取方法返回一个数字作为`票据stamp`，它用相应的锁状态表示并控制访问，数字`0`表示没有写锁被授权访问。在读锁上分为悲观锁（传统的独占锁）和乐观锁。

**所谓的乐观读模式，也就是若读的操作很多，写的操作很少的情况下，可以乐观地认为，写入与读取同时发生几率很少，因此不悲观地使用完全的读取锁定（独占）。** 

**程序可以查看读取资料之后，是否遭到写入执行的变更，再采取后续的措施（重新读取变更信息，或者抛出异常） ，这一个小小改进，可大幅度提高程序的吞吐量！**


下面是`java doc`提供的`StampedLock`一个例子：
```java
class Point {
    private final StampedLock sl = new StampedLock();

    private double x, y;

    void move(double deltaX, double deltaY) { // an exclusively locked method
        long stamp = sl.writeLock();
        try {
            x += deltaX;
            y += deltaY;
        } finally {
            sl.unlockWrite(stamp);
        }
    }

    // 下面是乐观读锁案例
    double distanceFromOrigin() { // A read-only method
        long stamp = sl.tryOptimisticRead(); //获得一个乐观读锁
        double currentX = x, currentY = y; //将两个字段读入本地局部变量
        if (!sl.validate(stamp)) { //检查发出乐观读锁后同时是否有其他写锁发生？
            stamp = sl.readLock(); //如果没有，我们再次获得一个读悲观锁
            try {
                currentX = x; // 将两个字段读入本地局部变量
                currentY = y; // 将两个字段读入本地局部变量
            } finally {
                sl.unlockRead(stamp);
            }
        }
        return Math.sqrt(currentX * currentX + currentY * currentY);
    }

    // 下面是悲观读锁案例
    void moveIfAtOrigin(double newX, double newY) { // upgrade
        // Could instead start with optimistic, not read mode
        long stamp = sl.readLock();
        try {
            while (x == 0.0 && y == 0.0) { //循环，检查当前状态是否符合
                long ws = sl.tryConvertToWriteLock(stamp); //将读锁转为写锁
                if (ws != 0L) { //这是确认转为写锁是否成功
                    stamp = ws; //如果成功 替换票据
                    x = newX; //进行状态改变
                    y = newY; //进行状态改变
                    break;
                } else { //如果不能成功转换为写锁
                    sl.unlockRead(stamp); //我们显式释放读锁
                    stamp = sl.writeLock(); //显式直接进行写锁 然后再通过循环再试
                }
            }
        } finally {
            sl.unlock(stamp); //释放读锁或写锁
        }
    }
}
```
## 六、CAS
### 1. CAS简述
**CAS：Compare and Swap，即比较再交换。**

>JDK 5之前Java语言是靠`synchronized`关键字保证同步的，这是一种独占锁（排他锁/悲观锁）。  

`JDK 5`增加了并发包 `java.util.concurrent.*`，其下面的类使用`CAS算法`实现了区别于`synchronouse同步锁`的一种乐观锁。

### 2. CAS算法理解
`CAS算法`的过程是这样：  

1. 它包含三个参数`CAS`（`V`，`E`，`N`）：`V表示要更新的变量`，`E表示预期值`，`N表示新值`。  
2. 仅当`V值`等于`E值`时，才会将`V`的值设为`N`，如果`V值`和`E值`不同，则说明已经有其他线程做了更新，则当前线程什么都不做。
3. 最后，`CAS`返回当前`V的真实值`。

就是指当两者进行比较时：
* **如果相等：** 则证明共享数据没有被修改，替换成新值，然后继续往下运行；
* **如果不相等：** 说明共享数据已经被修改，放弃已经所做的操作，然后重新执行刚才的操作。

可以看出 `CAS `操作是基于共享数据不会被修改的假设，采用了类似于数据库的 `commit-retry模式`。**当同步冲突出现的机会很少时，这种假设能带来较大的性能提升。**


**小结：**  
* 与锁相比，使用`比较交换（CAS）`会使程序看起来更加复杂一些。  
  但由于其非阻塞性，它对死锁问题天生免疫，并且，线程间的相互影响也远远比基于锁的方式要小。  
  更为重要的是，使用无锁的方式完全没有锁竞争带来的系统开销，也没有线程间频繁调度带来的开销，因此，**它要比基于锁的方式拥有更好的性能。**
* `CAS`操作是抱着乐观的态度进行的，它总是认为自己可以成功完成操作：
    * 当多个线程同时使用`CAS`操作一个变量时，只有一个会胜出，并成功更新，其余均会失败。
    * 失败的线程不会被挂起，仅是被告知失败，并且允许再次尝试，当然也允许失败的线程放弃操作。

**补充：**  
原子类`AtomicInteger`底层源码：

```java
public final int getAndAddInt(Object o, long offset, int delta) {
    int v;
    do {
        v = getIntVolatile(o, offset);
    } while (!compareAndSwapInt(o, offset, v, v + delta));
    return v;
}
/** 
 * Atomically increments by one the current value. 
 * 
 * @return the updated value 
 */  
public final int incrementAndGet() {  
    for (;;) {  
        //获取当前值  
        int current = get();  
        //设置期望值  
        int next = current + 1;  
        //调用Native方法compareAndSet，执行CAS操作  
        if (compareAndSet(current, next))  
            //成功后才会返回期望值，否则无线循环  
            return next;  
    }  
}  
```

### 3. ABA问题
**`CAS`存在一个很明显的问题，即`ABA问题`。**

基于`CAS(V,E,N)`的原理，如果`变量V`初次读取的时候是`A`，并且在准备赋值的时候检查到它`仍然是A`，并不能说明它的值没有被其他线程修改过。

如果在这段期间曾经被改成`B`，然后又改回`A`，那`CAS`操作就会误认为它从来没有被修改过。这就是 **"ABA问题"**。

针对这种情况，java并发包中提供了一个带 **有标记** 的原子引用类`AtomicStampedReference`，它可以通过控制变量值的版本来保证`CAS`的正确性。

测试代码：
```java
public class ABATest {
    private static AtomicInteger atomicInt = new AtomicInteger(100);
    private static AtomicStampedReference<Integer> atomicStampedRef = new AtomicStampedReference<Integer>(100, 0);

    public static void main(String[] args) throws InterruptedException {
        atomicIntTest();
        atomicStampedRefTest();
    }

    public static void atomicIntTest() throws InterruptedException {
        // 线程1：将值改为101再改回100
        Thread intT1 = new Thread(new Runnable() {
            @Override
            public void run() {
                atomicInt.compareAndSet(100, 101);
                atomicInt.compareAndSet(101, 100);
            }
        });

        // 线程2：将值改为101
        Thread intT2 = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException e) {
                }
                boolean c3 = atomicInt.compareAndSet(100, 101);
                System.out.println(c3); // true
            }
        });

        intT1.start();
        intT2.start();
        // 等待线程1先执行完毕：确保值出现了ABA的变化
        intT1.join();
        intT2.join();
    }

    public static void atomicStampedRefTest() {
        // 线程1：将值改为101再改回100
        Thread refT1 = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    TimeUnit.SECONDS.sleep(1);
                } catch (InterruptedException e) {
                }
                atomicStampedRef.compareAndSet(100, 101, atomicStampedRef.getStamp(), atomicStampedRef.getStamp() + 1);
                atomicStampedRef.compareAndSet(101, 100, atomicStampedRef.getStamp(), atomicStampedRef.getStamp() + 1);
            }
        });

        // 线程2：将值改为101
        Thread refT2 = new Thread(new Runnable() {
            @Override
            public void run() {
                int stamp = atomicStampedRef.getStamp();
                try {
                    TimeUnit.SECONDS.sleep(2);
                } catch (InterruptedException e) {
                }
                boolean c3 = atomicStampedRef.compareAndSet(100, 101, stamp, stamp + 1);
                System.out.println(c3); // false
            }
        });
        refT1.start();
        refT2.start();
    }
}
```
执行结果：
```
true
false
```
**补充：** `AtomicStampedReference`源代码里使用的是`CopyOnWrite`的策略来保证线程安全，更改前保持`pair`的应用，每次更改都会新生成一个`pair`。
`AtomicMarkableReference`也能达到类似的效果。

### 4. 原子类（ 基于"CAS"乐观锁的atomic类）
`java.util.concurrent.atomic`包下提供了一些AtomicXXX类，例如：`AtomicInteger`，`AtomicLong`，`AtomicBoolean`等类。这些类通过`CAS自旋锁`来保证单个变量上的线程安全。

<center>

![](https://raw.githubusercontent.com/XieRuhua/images/master/JavaLearning/Java相关/Java基础等/并发/锁（Java）/原子类.png)
</center>

**如果同一个变量要被多个线程访问，则可以使用该包中的类。**

Java中的原子操作类大致可以分为4类：**原子更新`基本`类型**、**原子更新`数组类`型**、**原子更新`引用`类型**、**原子更新`属性`类型**。  
这些原子类中都是用了无锁的概念，有的地方直接使用`CAS`操作的线程安全的类型。

**小结：**  
相对于JUC locks包中的锁，优缺点：
* 优点是没有系统调用不需要挂起和唤醒线程
* 缺点：
    * 是会过度占用`CPU`：  
      在并发量比较高的情况下，如果许多线程反复尝试更新某一个变量，却又一直更新不成功，**循环往复（即：如果CAS失败，会一直进行尝试），会给CPU带来很大的压力**。
    * 无法解决 **"ABA"** 问题。
    * 不能保证代码块的原子性（同`ABA`）  
       **`CAS机制`所保证的只是一个`变量`的原子性操作，而不能保证`整个代码块`的原子性。**
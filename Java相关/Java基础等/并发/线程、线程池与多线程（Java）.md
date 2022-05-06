# 线程、线程池与多线程

[笔记内容参考1：Java线程详解](https://www.cnblogs.com/riskyer/p/3263032.html)  
[笔记内容参考2：多线程——Callable和Future的使用](https://blog.csdn.net/qq_45036591/article/details/105321053)  
[笔记内容参考3：CompletableFuture用法详解](https://zhuanlan.zhihu.com/p/344431341)

[toc]

## 前言：
**操作系统中线程和进程的概念：**  
现在的操作系统是多任务操作系统，多线程则是实现多任务的一种方式。  
- **进程：** 是指一个内存中运行的应用程序，每个进程都有自己独立的一块内存空间，一个进程中可以启动多个线程。如：在Windows系统中，一个运行的`exe`程序就是一个进程。
- **线程：** 是指进程中的一个执行流程，一个进程中可以运行多个线程。如：`java.exe`进程中可以运行很多线程。线程总是属于某个进程，进程中的多个线程共享进程的内存。

**注意：进程或者线程“同时”执行是人的感觉，在进程或者线程之间实际上在不停的切换执行。**

## 一、创建与启动
### 1. 定义线程
1. 扩展`java.lang.Thread`类。  
    此类中有个`run()`方法，`Thread`的 **子类** 应该 **重写** 该方法：
    ```java
    @Override
    public void run() {
        if (target != null) {
            target.run();
        }
    }
    ```
2. 实现`java.lang.Runnable`接口，并 **实现** 其中的`run()`方法：
    ```java
    @FunctionalInterface
    public interface Runnable {
        public abstract void run();
    }
    ```
使用实现接口`Runnable`的对象创建一个线程时，启动该线程将导致在独立执行的线程中调用对象的`run()`方法。方法`run()`可以执行任何所需的操作。

### 2. 实例化线程
1. 如果是扩展`java.lang.Thread`类的线程，则直接`new`即可。
2. 如果是实现了`java.lang.Runnable`接口的类，则需要配合`Thread`的构造方法：
    ```java
    Thread(Runnable target)
    Thread(Runnable target, String name)
    Thread(ThreadGroup group, Runnable target)
    Thread(ThreadGroup group, Runnable target, String name)
    Thread(ThreadGroup group, Runnable target, String name, long stackSize)
    ```
3. `Thread`类的有关方法：
    - **start()：** 启动线程并执行相应的`run()`方法  
    - **run()：** 子线程要执行的代码放入`run()`方法中  
    - **currentThread()：** 静态的，调取当前的线程  
    - **getName()：** 获取此线程的名字  
    - **setName()：** 设置此线程的名字  
    - **yield()：** 调用此方法的线程释放当前`CPU`的执行权，暂停当前正在执行的线程，把执行机会让给优先级相同或更高的线程；
      若队列中没有同优先级的线程，忽略此方法。
    - **join()：** 在`A线程`中调用`B线程`的`join()`方法，表示：当执行到此方法，`A线程`停止执行，直至`B线程`执行完毕；  
      当某个程序执行流中调用其他线程的 `join()` 方法时，调用线程将被阻塞，直到 `join()`方法加入的 `join` 线程执行完为止  
    - **isAlive()：** 判断当前线程是否还存活
    - **sleep(long l)：** 显式的让当前线程睡眠`l`毫秒，令当前活动线程在指定时间段内放弃对`CPU`控制,使其他线程有机会被执行,时间到后重排队。
    - **setPriority()：** 设置、改变线程的优先级
    - **getPriority()：** 返回线程优先值
    - 线程通信（属于`java.lang.Object`)： **wait()** 、 **notify()** 、 **notifyAll()**

### 3. 启动线程
在线程的`Thread`对象上调用`start()`方法，而不是`run()`或者别的方法：
- 在调用`start()`方法之前：线程处于新状态中，新状态指有一个`Thread`对象，但还没有一个真正的线程。
- 在调用`start()`方法之后，发生了一系列复杂的事情：
  - 启动新的执行线程（具有新的调用栈）；
  - 该线程从新状态转移到可运行状态；
  - 当该线程获得机会执行时，其目标`run()`方法将运行。

**注意：对Java来说，`run()`方法没有任何特别之处。像`main()`方法一样，它只是新线程知道调用的方法名称(和签名)。因此，在`Runnable`上或者`Thread`上调用`run`方法是合法的。<font color="red">但并不启动新的线程。</font>**

### 4. 示例代码
#### 1、实现Runnable接口的多线程例子
```java
/**
 * 实现Runnable接口的类
 */
public class DoSomething implements Runnable {
    private String name;

    public DoSomething(String name) {
        this.name = name;
    }

    public void run() {
        for (int i = 0; i < 5; i++) {
            for (long k = 0; k < 100000000; k++) ;
            System.out.println(name + ": " + i);
        }
    }
}
```
```java
/**
 * 测试Runnable类实现的多线程程序
 */
public class TestRunnable {
    public static void main(String[] args) {
        DoSomething ds1 = new DoSomething("阿三");
        DoSomething ds2 = new DoSomething("李四");

        Thread t1 = new Thread(ds1);
        Thread t2 = new Thread(ds2);

        t1.start();
        t2.start();
    }
}
```
执行结果：
```
阿三: 0
李四: 0
阿三: 1
李四: 1
阿三: 2
李四: 2
阿三: 3
李四: 3
阿三: 4
李四: 4
```

#### 2、扩展Thread类实现的多线程例子
```java
/**
 * 测试扩展Thread类实现的多线程程序
 */
public class TestThread extends Thread {
    public TestThread(String name) {
        super(name);
    }

    public void run() {
        for (int i = 0; i < 5; i++) {
            for (long k = 0; k < 100000000; k++) ;
            System.out.println(this.getName() + " :" + i);
        }
    }

    public static void main(String[] args) {
        Thread t1 = new TestThread("阿三");
        Thread t2 = new TestThread("李四");
        t1.start();
        t2.start();
    }
}
```
执行结果：
```
阿三 :0
李四 :0
阿三 :1
李四 :1
阿三 :2
李四 :2
阿三 :3
李四 :3
阿三 :4
李四 :4
```
对于上面的多线程程序代码来说，输出的结果是不确定的。其中的一条语句`for(long k = 0; k < 100000000; k++);`是用来模拟一个非常耗时的操作的。

### 5. 小结
1. 线程的名字：  
    - 一个运行中的线程总是有名字的，名字有两个来源：一个是`JVM`虚拟机给的名字，一个是开发人员设置的名字。  
    - 在没有指定线程名字的情况下，`JVM`虚拟机总会为线程指定名字；并且 **主线程的名字总是`main`** ，非主线程的名字不确定。
    - 线程都可以设置名字，也可以获取线程的名字，连主线程也不例外。
2. 获取当前线程的对象的方法是：`Thread.currentThread()`；
3. 在上面的示例代码中，只能保证：
    - 每个线程都将启动且都将运行直到完成；
    - 当一系列线程以某种顺序启动但并不意味着将按该顺序执行；
    - 对于任何一组启动的线程来说，调度程序不能保证其**执行次序** 和 **持续时间** 。
4. 当线程的`run()`方法结束时则该线程完成。
5. **一旦线程启动，它就永远不能再重新启动。** 只有一个新的线程可以被启动，并且只能一次。
6. 线程的调度是`JVM`的一部分，在一个`CPU`的机器上，实际上一次只能运行一个线程。`JVM`线程调度程序决定实际运行哪个处于 **可运行状态** 的线程。  
众多可运行线程中的某一个会被选中做为当前线程；且运行的顺序是没有保障的。
7. 尽管线程执行顺序通常采用队列形式，但这是没有保障的。 **队列形式是指当一个线程完成“一轮”时，它移到可运行队列的尾部等待，直到它最终排队到该队列的前端为止，它才能被再次选中**。  
事实上，我们把它称为可运行池而不是一个可运行队列，目的是帮助认识线程并不都是以某种有保障的顺序执行的事实。
8. 尽管我们没有无法控制线程调度程序，但可以通过别的方式来影响线程调度的方式。

## 二、线程的状态及其转换过程
### 1. 线程的状态
线程的状态转换是线程控制的基础。  
线程状态总的可分为五大状态：分别是`新建`、`可运行`、`运行`、`等待/阻塞`、`终止（死亡）`。

用一个图来描述如下：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java%E7%9B%B8%E5%85%B3/Java%E5%9F%BA%E7%A1%80%E7%AD%89/%E5%B9%B6%E5%8F%91/%E9%94%81%EF%BC%88Java%EF%BC%89/%E7%BA%BF%E7%A8%8B%E6%B5%81%E7%A8%8B%E5%9B%BE.png)
</center>

1. **新建状态：**  
线程对象已经创建，还没有在其上调用`start()`方法。
2. **可运行/就绪状态：**  
当`start()`方法调用时，线程首先进入可运行状态。当前线程有资格运行，但调度程序还没有把它选定为运行线程时线程所处的状态。  
在线程运行之后或者从阻塞、等待或睡眠状态回来后，也会返回到可运行状态。
3. **运行中状态：**  
线程调度程序从可运行池（上文小结第7点所说的队列）中选择一个线程作为当前线程时线程所处的状态。 **这也是线程进入运行状态的唯一一种方式** 。
4. **等待/超时等待/阻塞/睡眠状态：**  
这是线程有资格运行时它所处的状态。实际上这个四个状态组合为一种，其共同点是：线程仍旧是活的，但是当前没有条件运行。  
换句话说，它是可运行的，但是如果某个事件出现，它可能就会返回到可运行状态。
5. **终止（死亡）状态：**  
当线程的`run()`方法执行完成时就认为该线程死去。这个线程对象也许是活的，但是它已经不是一个可执行的线程。  
线程一旦死亡，就不能复生。如果在一个死去的线程上调用`start()`方法，会抛出`java.lang.IllegalThreadStateException`异常。

### 2. 阻止线程执行
#### 2.1 睡眠：`sleep()`
`Thread.sleep(long millis)`和`Thread.sleep(long millis, int nanos)`静态方法强制当前正在执行的线程休眠（暂停执行），以“减慢线程”运行速度。  
线程在苏醒之前不会返回到可运行状态。当睡眠时间到期，则返回到 **可运行状态** 。

**使用线程睡眠的原因：**  
线程执行太快，或者需要强制进入下一轮，因为Java规范不保证合理的轮换（即不保证线程有序进行）。

**睡眠的实现：** 调用静态方法
```java
try {
    // 睡眠3毫秒
    Thread.sleep(3);
} catch (InterruptedException e) {
    e.printStackTrace();
}
```
**睡眠的位置：**  
为了让其他线程有机会执行，可以将`Thread.sleep()`的调用放在目标线程`run()`方法之内。这样才能保证该线程执行过程中会睡眠。

例如，在前面的例子中，将一个耗时的操作改为睡眠，以减慢线程的执行。可以做如下修改：
```java
//    public void run() {
//        for (int i = 0; i < 5; i++) {
//            for (long k = 0; k < 100000000; k++) ;
//            System.out.println(this.getName() + " :" + i);
//        }
//    }

    public void run() {
        for (int i = 0; i < 5; i++) {

            // 很耗时的操作，用来减慢线程的执行
            // for(long k= 0; k <100000000;k++);
            try {
                Thread.sleep(3);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println(this.getName() + " :" + i);
        }
    }
```
运行结果：
```
阿三 :0
李四 :0
阿三 :1
阿三 :2
阿三 :3
李四 :1
李四 :2
阿三 :4
李四 :3
李四 :4
```
这样，线程在每次执行过程中，总会睡眠`3`毫秒；睡眠后，其他的线程就有机会执行了。

**注意：**
1. 线程睡眠是帮助所有线程获得运行机会的最好方法。
2. `sleep()`中指定的时间是线程不会运行的最短时间。 **线程睡眠到期自动苏醒，并返回到可运行状态，而不是运行状态** 。  
因此，`sleep()`不能保证该线程睡眠到期后就立即开始执行。
3. `sleep()`是静态方法，只能控制当前正在运行的线程。

示例代码：
```java
/**
 * 一个计数器，计数到100，在每个数字之间暂停1秒，每隔20个数字输出一个字符串
 */
public class MyThread extends Thread {
    public void run() {
        for (int i = 0; i < 100; i++) {
            if ((i) % 20 == 0) {
                System.out.println("-------" + i);
            }
            System.out.print(i);
            try {
                Thread.sleep(1);
                System.out.print("    线程睡眠1毫秒！\n");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public static void main(String[] args) {
        new MyThread().start();
    }
}
```
执行结果：
```
-------0
0    线程睡眠1毫秒！
1    线程睡眠1毫秒！
2    线程睡眠1毫秒！
3    线程睡眠1毫秒！
4    线程睡眠1毫秒！
5    线程睡眠1毫秒！
6    线程睡眠1毫秒！
7    线程睡眠1毫秒！
8    线程睡眠1毫秒！
9    线程睡眠1毫秒！
10    线程睡眠1毫秒！
11    线程睡眠1毫秒！
12    线程睡眠1毫秒！
13    线程睡眠1毫秒！
14    线程睡眠1毫秒！
15    线程睡眠1毫秒！
16    线程睡眠1毫秒！
17    线程睡眠1毫秒！
18    线程睡眠1毫秒！
19    线程睡眠1毫秒！
-------20
20    线程睡眠1毫秒！
21    线程睡眠1毫秒！
22    线程睡眠1毫秒！
23    线程睡眠1毫秒！
24    线程睡眠1毫秒！
25    线程睡眠1毫秒！
26    线程睡眠1毫秒！
27    线程睡眠1毫秒！
28    线程睡眠1毫秒！
29    线程睡眠1毫秒！
30    线程睡眠1毫秒！
31    线程睡眠1毫秒！
32    线程睡眠1毫秒！
33    线程睡眠1毫秒！
34    线程睡眠1毫秒！
35    线程睡眠1毫秒！
36    线程睡眠1毫秒！
37    线程睡眠1毫秒！
38    线程睡眠1毫秒！
39    线程睡眠1毫秒！
-------40
40    线程睡眠1毫秒！
41    线程睡眠1毫秒！
42    线程睡眠1毫秒！
43    线程睡眠1毫秒！
44    线程睡眠1毫秒！
45    线程睡眠1毫秒！
46    线程睡眠1毫秒！
47    线程睡眠1毫秒！
48    线程睡眠1毫秒！
49    线程睡眠1毫秒！
50    线程睡眠1毫秒！
51    线程睡眠1毫秒！
52    线程睡眠1毫秒！
53    线程睡眠1毫秒！
54    线程睡眠1毫秒！
55    线程睡眠1毫秒！
56    线程睡眠1毫秒！
57    线程睡眠1毫秒！
58    线程睡眠1毫秒！
59    线程睡眠1毫秒！
-------60
60    线程睡眠1毫秒！
61    线程睡眠1毫秒！
62    线程睡眠1毫秒！
63    线程睡眠1毫秒！
64    线程睡眠1毫秒！
65    线程睡眠1毫秒！
66    线程睡眠1毫秒！
67    线程睡眠1毫秒！
68    线程睡眠1毫秒！
69    线程睡眠1毫秒！
70    线程睡眠1毫秒！
71    线程睡眠1毫秒！
72    线程睡眠1毫秒！
73    线程睡眠1毫秒！
74    线程睡眠1毫秒！
75    线程睡眠1毫秒！
76    线程睡眠1毫秒！
77    线程睡眠1毫秒！
78    线程睡眠1毫秒！
79    线程睡眠1毫秒！
-------80
80    线程睡眠1毫秒！
81    线程睡眠1毫秒！
82    线程睡眠1毫秒！
83    线程睡眠1毫秒！
84    线程睡眠1毫秒！
85    线程睡眠1毫秒！
86    线程睡眠1毫秒！
87    线程睡眠1毫秒！
88    线程睡眠1毫秒！
89    线程睡眠1毫秒！
90    线程睡眠1毫秒！
91    线程睡眠1毫秒！
92    线程睡眠1毫秒！
93    线程睡眠1毫秒！
94    线程睡眠1毫秒！
95    线程睡眠1毫秒！
96    线程睡眠1毫秒！
97    线程睡眠1毫秒！
98    线程睡眠1毫秒！
99    线程睡眠1毫秒！
```

#### 2.2 线程的优先级和线程让步`yield()`
线程的让步是通过`Thread.yield()`来实现的。 **`yield()`方法的作用是：暂停当前正在执行的线程对象，并执行其他线程。**  

要理解`yield()`，必须了解线程的优先级的概念：
- 线程总是存在优先级，优先级范围在`1~10`之间。
- `JVM`线程调度程序是基于优先级的抢先调度机制。
- 在大多数情况下，当前运行的线程优先级将大于或等于线程池中任何线程的优先级。但这仅仅是大多数情况。

**注意：当设计多线程应用程序的时候，一定不要依赖于线程的优先级。因为线程调度优先级操作是没有保障的，只能把线程优先级作用作为一种提高程序效率的方法。**

当线程池中线程都具有相同的优先级，调度程序的`JVM`实现自由选择它喜欢的线程。  
这时候调度程序的操作有两种可能：
1. 选择一个线程运行，直到它阻塞或者运行完成为止。
2. 时间分片：为池内的每个线程提供 **均等** 的运行机会。

设置线程的优先级：线程默认的优先级是创建它的执行线程的优先级（即父级线程的优先级）。  
可以通过`setPriority(int newPriority)`更改线程的优先级，例如：
```java
Thread t = new MyThread();
// 将线程t的优先级设置为8
t.setPriority(8);
t.start();
```
**注意：线程优先级为`1~10`之间的正整数，`JVM`从不会改变一个线程的优先级。然而，`1~10`之间的值是没有保证的。一些`JVM`可能不能识别`10`个不同的值，而将这些优先级进行每两个或多个合并，变成少于`10`个的优先级，则两个或多个优先级的线程可能被映射为一个优先级。**

线程默认优先级是`5`，`Thread`类中有三个常量，定义线程优先级范围：
```java
static int MAX_PRIORITY；//线程可以具有的最高优先级。
static int MIN_PRIORITY; // 线程可以具有的最低优先级。
static int NORM_PRIORITY; // 分配给线程的默认优先级。
```

**小结：**   
- `yield()`从未导致线程转到 **等待/睡眠/阻塞状态** 。在大多数情况下，`yield()`将导致线程从运行状态转到可运行状态，但有可能没有效果。
- `yield()`应该做的是让当前运行线程回到可运行状态，以允许具有相同优先级的其他线程获得运行机会。  
因此，使用`yield()`的目的是让相同优先级的线程之间能适当的轮转执行。但是，实际中无法保证`yield()`达到让步目的，因为执行让步操作的线程还有可能被线程调度程序再次选中。

**<font color="red">`Thread.yield()`方法作用是：暂停当前正在执行的线程对象，并执行包含自己在内的其他线程。</font>**

#### 2.3 join()方法
**`Thread`的非静态方法`join()`让一个线程B“加入”到另外一个线程A的尾部。在A执行完毕之前，B不能工作。**  
例如（未使用`join()`时）：
```java
/**
 * 自定义线程输出内容
 */
class ThreadTest extends Thread {
    private String name;

    public ThreadTest(String name) {
        this.name = name;
    }

    public void run() {
        for (int i = 1; i <= 3; i++) {
            System.out.println(name + "-" + i);
        }
    }
}
```
```java
/**
 * 测试线程输出
 */
public class TestJoin {
    public static void main(String[] args) throws InterruptedException {
        ThreadTest t1 = new ThreadTest("A");
        ThreadTest t2 = new ThreadTest("B");
        t1.start();
//        t1.join();
        t2.start();
    }
}
```
执行结果：
```
A-1
B-1
B-2
B-3
A-2
A-3
```
**可以看出A线程和B线程是交替随机执行的。**

而放开`join()`的注释后执行结果为：
```
A-1
A-2
A-3
B-1
B-2
B-3
```
显然，使用`t1.join()`之后，**B线程** 需要等**A线程**执行完毕之后才能执行。需要注意的是，`t1.join()`需要等`t1.start()`执行之后执行才有效果，此外，如果`t1.join()`放在`t2.start()`之后的话，仍然会是交替执行。

补充：`join()`方法还有带超时限制的重载版本。  
如`t.join(5000);`则让线程等待`5000`毫秒，如果超过这个时间，则停止等待，变为可运行状态（即超过这个时间就不用等待被`join`的线程是否执行完毕）。

#### 小结
到目前为止，介绍了线程离开运行状态的3种方法：
1. **Thread.sleep()：** 使当前线程睡眠至少多少毫秒（尽管它可能在指定的时间之前被中断）。
2. **Thread.yield()：** 不能保障太多事情，尽管通常它会让当前运行线程回到可运行性状态，使得有相同优先级的线程（包含自己）有机会执行。
3. **join()：**保证当前线程停止执行，直到该线程所加入的线程完成为止。然而，如果它加入的线程没有存活，则当前线程不需要停止。

除了以上三种方式外，还有下面几种特殊情况可能使线程离开运行状态：
1. 线程的`run()`方法执行完成。
2. 在对象上调用`wait()`方法（该方法属于`java.lang.object`，后文会讲到）。
3. 线程不能在对象上获得锁定，它正试图运行该对象的方法代码。
4. 线程调度程序可以决定将当前运行状态移动到可运行状态，以便让另一个线程获得运行机会，而不需要任何理由。

## 三、线程同步与锁
> 关于锁的详细介绍参考其他笔记： [锁（Java）](https://xieruhua.gitee.io/javalearning/#/./Java%E7%9B%B8%E5%85%B3/Java%E5%9F%BA%E7%A1%80%E7%AD%89/%E5%B9%B6%E5%8F%91/%E9%94%81%EF%BC%88Java%EF%BC%89)

### 1. 同步问题说明
**线程的同步是为了防止多个线程访问一个数据对象时，对数据造成破坏。**

例如：两个线程`ThreadA`、`ThreadB`都操作同一个`Foo`对象，并修改`Foo`对象上的数据
```java
public class Foo {
    private int x = 100;
    
    // 获取x变量的值
    public int getX() {
        return x;
    }
    
    // 计算x与y的差值
    public int fix(int y) {
        x = x - y;
        return x;
    }
}
```
```java
public class MyRunnable implements Runnable {
    private Foo foo = new Foo();

    public static void main(String[] args) {
        MyRunnable r = new MyRunnable();
        // 创建线程ta、tb并设置线程名
        Thread ta = new Thread(r, "Thread-A");
        Thread tb = new Thread(r, "Thread-B");
        ta.start();
        tb.start();
    }

    public void run() {
        for (int i = 0; i < 3; i++) {
            this.fix(30);
            try {
                // 睡眠1毫秒
                Thread.sleep(1);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println(Thread.currentThread().getName() + " :当前foo对象的x值= " + foo.getX());
        }
    }

    public int fix(int y) {
        return foo.fix(y);
    }
}
```
执行结果：
```java
Thread-A :当前foo对象的x值= 40
Thread-A :当前foo对象的x值= 10
Thread-B :当前foo对象的x值= 10
Thread-B :当前foo对象的x值= -50
Thread-A :当前foo对象的x值= -50
Thread-B :当前foo对象的x值= -80
```
从结果发现，这样的输出值明显是不合理的。原因是两个线程不加控制的访问`Foo`对象并修改其数据所致。  
如果要保持结果的合理性，只需要达到一个目的，就是将对`Foo`的访问加以限制：即每次只能有一个线程在访问。

在具体的Java代码中需要完成以下两个操作：
- 把竞争访问的资源类`Foo`变量`x`标识为`private`；
- 对修改变量的代码进行同步，使用`synchronized`关键字同步 **方法** 或 **代码块** 。

### 2. 同步和锁定
**<font color="red">Java中每个对象都有一个内置锁</font>**   
当程序运行到非静态的`synchronized`同步方法上时，自动获得与正在执行代码类的当前实例（`this`实例）有关的锁。获得一个对象的锁也称为获取锁、锁定对象、在对象上锁定或在对象上同步。

**注意：当程序运行到`synchronized`同步方法或代码块时该对象的锁才起作用。**

**<font color="red">一个对象只有一个锁。</font>**  
所以，如果一个线程获得该锁，就没有其他线程可以获得锁，直到上一个线程释放（或返回）锁。这也意味着任何其他线程都不能进入该对象上的`synchronized`修饰的`方法`或`代码块`，直到该锁被释放（释放锁是指持锁线程退出了`synchronized`修饰的`同步方法`或`代码块`）。

关于锁和同步，有以下几个要点：
1. 只能同步方法或者代码块，而不能同步变量和类；
2. 每个对象只有一个锁；当提到同步时，应该清楚在什么地方同步？也就是说，在哪个对象上同步。
3. 不必同步类中所有的方法；类可以同时拥有同步和非同步方法。
4. 如果两个线程要执行一个类中的`synchronized`方法，并且两个线程使用相同的实例来调用方法，那么一次只能有一个线程能够执行方法，另一个需要等待，直到锁被释放。  
也就是说：如果一个线程在对象上获得一个锁，就没有任何其他线程可以进入类（该对象的）中的任何一个同步方法。
5. 如果线程拥有同步和非同步方法，则非同步方法可以被多个线程自由访问而不受锁的限制。
6. 线程睡眠时，它所持的任何锁都不会释放。
7. 一个线程可以获得多个锁。比如，在一个对象的同步方法里面调用另外一个对象的同步方法，则获取了两个对象的同步锁。
8. 同步不但可以同步整个方法，还可以同步方法中一部分代码块。同步损害并发性，应该尽可能缩小同步范围。
9. 在同步代码块时，应该指定在哪个对象上同步，也就是说要获取哪个对象的锁。例如：
```java
public int fix(int y) {
    synchronized (this) {
      x = x - y;
    }
    return x;
}
```
当然，同步代码块也可以改写为同步方法，但功能完全一样的，例如：
```java
public synchronized int getX() {
    return x++;
}
```

### 3. 静态方法同步
要同步静态方法，需要一个用于整个类对象的锁，这个对象是就是这个类（`XXX.class`)。  
例如：
```java
public static synchronized int setName(String name){
   Xxx.name = name;
}
```
等价于
```java
public static int setName(String name){
   synchronized(Xxx.class){
      Xxx.name = name;
   }
}
```

### 4. 如果线程不能获得锁会怎么样？
如果线程试图进入同步方法，而其锁已经被占用，则线程在该对象上被阻塞。  
实质上，线程进入该对象的一种池中，必须在哪里等待，直到其锁被释放，该线程再次变为可运行或运行。

当考虑阻塞时，一定要注意哪个对象正在被锁定：
1. 调用同一个对象中非静态同步方法的线程将彼此阻塞。如果是不同对象，则每个线程有自己的对象的锁，线程间彼此互不干预。
2. 调用同一个类中的静态同步方法的线程将彼此阻塞，它们都是锁定在相同的`Class`对象上。
3. 静态同步方法和非静态同步方法将永远不会彼此阻塞，因为静态方法锁定在`Class`对象上，非静态方法锁定在该类的对象上。
4. 对于同步代码块，要看清楚什么对象已经被锁定（`synchronized`后面括号的内容）。在同一个对象上进行同步的线程将彼此阻塞，在不同对象上锁定的线程将永远不会彼此阻塞。

### 5. 何时需要同步？
- 在多个线程同时访问互斥数据时，应该同步以保护数据，确保两个线程不会同时修改它。
- 对于非静态字段中可更改的数据，通常使用非静态方法访问。
- 对于静态字段中可更改的数据，通常使用静态方法访问。

### 6. 线程死锁
死锁对Java程序来说，是很复杂的，也很难发现问题。当两个线程被阻塞，每个线程在等待对方线程时就发生死锁。

死锁示例代码：
```java
public class DeadlockRisk {
    private static class Resource {
        public int value;
    }

    private Resource resourceA = new Resource();
    private Resource resourceB = new Resource();

    public int read() {
        synchronized (resourceA) {
            synchronized (resourceB) {
                return resourceB.value + resourceA.value;
            }
        }
    }

    public void write(int a,int b) {
        synchronized (resourceB) {
            synchronized (resourceA) {
                resourceA.value = a;
                resourceB.value = b;
            }
        }
    }
}
```
假设`read()方法`由一个线程启动，`write()方法`由另外一个线程启动。读线程将拥有`resourceA`锁，写线程将拥有`resourceB`锁，两者都坚持等待的话就出现死锁。

实际上，上面这个例子发生死锁的概率很小。因为在代码内的某个点，`CPU`必须从读线程切换到写线程，所以，死锁基本上不能发生。  
**<font color="red">无论代码中发生死锁的概率有多小，一旦发生死锁，程序就宕掉。</font>**

### 7. 线程同步总结
1. 线程同步的目的是为了防止多个线程访问同一个资源时对资源的破坏。
2. 当多个线程等待一个对象锁时，没有获取到锁的线程将发生阻塞。
3. 线程同步方法是通过锁来实现，每个对象都有且仅有一个锁，这个锁与一个特定的对象关联，线程一旦获取了对象锁，其他访问该对象的线程就无法再访问该对象的其他同步方法。
4. 静态和非静态方法的锁互不干预。对于静态同步方法，锁是针对这个类的，锁对象是该类的`Class`对象。一个线程获得锁后在一个同步方法中访问另外对象上的同步方法时，会获取这两个对象锁。
5. 编写线程安全的类，需要时刻注意对多个线程竞争访问资源的逻辑和安全做出正确的判断，对 **“原子”** 操作做出分析，并保证 **原子操作** 期间别的线程无法访问竞争资源。
6. 死锁是线程间相互等待锁所造成的，在实际中发生的概率非常的小。但是， **一旦程序发生死锁，程序将宕掉。**

## 四、线程的交互（通信）
### 1. 基础介绍
线程交互知识点需要从 **`java.lang.Object`** 的类的三个方法来学习：
```java
void notify(); //  唤醒正在排队等待同步资源的线程中优先级最高者结束等待
void notifyAll(); // 唤醒正在排队等待资源的所有线程结束等待.
void wait(); // 令当前线程挂起并放弃CPU、同步资源，使别的线程可访问并修改共享资源，而当前线程排队等候再次对资源的访问，直到其他线程调用此对象的 notify()方法或 notifyAll()方法。
```

当然，`wait()`还有另外两个重载方法：
```java
// 导致当前的线程等待，直到其他线程调用此对象的 notify()方法或 notifyAll()方法，或者超过指定的时间量。
void wait(long timeout)

// 导致当前的线程等待，直到其他线程调用此对象的 notify()方法或 notifyAll()方法，或者其他某个线程中断当前线程，或者已超过某个实际时间量。
void wait(long timeout, int nanos)
```
关于等待/通知，要记住的关键点是：
- 必须从同步环境内调用`wait()`、`notify()`、`notifyAll()`方法；线程不能调用对象上等待或通知的方法，除非它拥有那个对象的锁。
- `wait()`、`notify()`、`notifyAll()`都是`Object`的实例方法。与每个对象具有锁一样，每个对象可以有一个线程列表，他们等待来自该信号（通知）。
- 线程通过执行对象上的`wait()`方法获得这个等待列表。从那时候起，它不再执行任何其他指令，直到调用对象的`notify()`方法为止。
- 如果多个线程在同一个对象上等待，则将只选择一个线程（不保证以何种顺序）继续执行。如果没有线程等待，则不采取任何特殊操作。

注意：`Java.lang.Object`提供的这三个方法只有在`synchronized`修饰的的`方法`或`代码块`中才能使用，否则会报`java.lang.IllegalMonitorStateException`异常

示例代码：
```java
/**
 * 计算1+2+3 ... +100的和
 */
public class ThreadB extends Thread {
    int total;

    public void run() {
        synchronized (this) {
            for (int i = 0; i < 101; i++) {
                total += i;
            }
            //（完成计算了）唤醒在此对象监视器上等待的单个线程，在本例中线程A被唤醒
            notify();
        }
    }
}
```
```java
/**
 * 计算输出其他线程锁计算的数据
 */
public class ThreadA {
    public static void main(String[] args) {
        ThreadB b = new ThreadB();
        //启动计算线程
        b.start();
        //线程A拥有b对象上的锁。线程为了调用wait()或notify()方法，该线程必须是那个对象锁的拥有者
        synchronized (b) {
            try {
                System.out.println("等待对象b完成计算。。。");
                //当前线程A等待
                b.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("b对象计算的总和是：" + b.total);
        }
    }
}
```
执行结果：
```
等待对象b完成计算。。。
b对象计算的总和是：5050
```
**注意：**
* 当在对象上调用`wait()`方法时，执行该代码的线程立即放弃它在对象上的锁。
* 然而调用`notify()`时，并不意味着这时线程会放弃其锁。如果线程仍然在完成同步代码，则线程在移出之前不会放弃锁。因此，调用`notify()`并不意味着这时该锁变得立即可用。

### 2. 多个线程在等待一个对象锁时候使用`notifyAll()`
在多数情况下，最好通知等待某个对象的所有线程。如果这样做，可以在对象上使用`notifyAll()`让所有在此对象上等待的线程冲出等待区，返回到可运行状态。

示例代码：
```java
/**
 * 计算线程
 */
public class Calculator extends Thread {
    int total;

    public void run() {
        synchronized (this) {
            for (int i = 0; i < 101; i++) {
                total += i;
            }
        }
        //通知所有在此对象上等待的线程进入可运行状态
        notifyAll();
    }
}
```
```java
/**
 * 获取计算结果并输出
 */
public class ReaderResult extends Thread {
    Calculator c;

    public ReaderResult(Calculator c) {
        this.c = c;
    }

    public void run() {
        synchronized (c) {
            try {
                System.out.println(Thread.currentThread() + "等待计算结果。。。");
                c.wait();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println(Thread.currentThread() + "计算结果为：" + c.total);
        }
    }

    public static void main(String[] args) {
        Calculator calculator = new Calculator();

        //启动三个线程，分别获取计算结果
        new ReaderResult(calculator).start();
        new ReaderResult(calculator).start();
        new ReaderResult(calculator).start();
        //启动计算线程
        calculator.start();
    }
}
```
运行结果：
```java
Thread[Thread-1,5,main]等待计算结果。。。
Thread[Thread-3,5,main]等待计算结果。。。
Thread[Thread-2,5,main]等待计算结果。。。
Thread[Thread-2,5,main]计算结果为：5050
Thread[Thread-3,5,main]计算结果为：5050
Thread[Thread-1,5,main]计算结果为：5050
Exception in thread "Thread-0" java.lang.IllegalMonitorStateException
	at java.lang.Object.notifyAll(Native Method)
	at com.xxx.Calculator.run(Calculator.java:13)
```
运行结果表明，程序中有异常，并且多次运行结果可能有多种输出结果。  
这就是说明，这个多线程的交互程序还存在问题。究竟是出了什么问题？

实际上，上述代码期望的是读取结果的线程在计算线程调用`notifyAll()`之前等待即可。  
但是，如果计算线程先执行，并在读取结果线程等待之前调用了`notify()`方法，那么又会发生什么呢？这种情况是可能发生的。因为无法保证线程的不同部分将按照什么顺序来执行。幸运的是当读取线程运行时，它只能马上进入等待状态（它没有做任何事情来检查等待的事件是否已经发生）。   
因此，如果计算线程已经调用了`notifyAll()`方法，那么它就不会再次调用`notifyAll()`，并且等待的读取线程将永远保持等待。这当然是开发者所不愿意看到的问题。

**所以，当等待的事件发生时，需要能够检查`notifyAll()`通知事件是否已经发生。**

### 3. 小结
* 释放锁:：`wait()`;
* 不释放锁：`sleep()`、`yield()`、~`suspend()`~（可能导致死锁，已过时）

## 五、线程的调度
> <font color="red">注意：不管程序员怎么编写调度，只能最大限度的影响线程执行的次序，而不能做到精准控制。</font>

Java线程调度是Java多线程的核心，只有良好的调度，才能充分发挥系统的性能，提高程序的执行效率。

调度策略说明：
- 同优先级线程组成先进先出队列（先到先服务）
- 使用时间片策略：对高优先级，使用优先调度的抢占式策略

### 1. 休眠-`sleep()`
线程休眠的是使线程让出`CPU`的最简单的做法之一；线程休眠时候，会将`CPU`资源交给其他线程，以便能轮换执行，当休眠一定时间后，线程会苏醒，进入可运行状态等待执行。

线程休眠的方法是`Thread.sleep(long millis)`和`Thread.sleep(long millis, int nanos)`，均为静态方法；  
那调用`sleep`休眠的哪个线程呢？简单来说，在哪个线程中调用`sleep`，就休眠哪个线程。
```java
/**
 * Java线程：线程的调度-休眠
 */
public class Test {
    public static void main(String[] args) {
        Thread t1 = new MyThread1();
        Thread t2 = new Thread(new MyRunnable());
        t1.start();
        t2.start();
    }
}

class MyThread1 extends Thread {
    public void run() {
        for (int i = 0; i < 3; i++) {
            System.out.println("线程1第" + i + "次执行！");
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class MyRunnable implements Runnable {
    public void run() {
        for (int i = 0; i < 3; i++) {
            System.out.println("线程2第" + i + "次执行！");
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
```
执行结果：
```
线程1第0次执行！
线程2第0次执行！
线程1第1次执行！
线程2第1次执行！
线程2第2次执行！
线程1第2次执行！
```
从执行结果可以看出，无法精准保证线程执行次序。

### 2. 优先级
与线程休眠类似，线程的优先级仍然无法保障线程的执行次序。只不过，优先级高的线程获取`CPU`资源的概率较大，优先级低的并非没机会执行，只是概率较低而已。  
线程的优先级用 **`1~10`** 之间的整数表示，数值越大优先级越高，默认的优先级为 **`5`** 。

<font color="red">**注意： 线程创建时继承父线程的优先级**</font>

`Thread`类中有三个常量，定义线程优先级范围：
```java
// 线程可以具有的最高优先级。
static int MAX_PRIORITY
// 线程可以具有的最低优先级。
static int MIN_PRIORITY
// 分配给线程的默认优先级。  
static int NORM_PRIORITY
```
涉及的方法：
```java
// 返回线程优先值 
getPriority();
// 改变线程的优先级
setPriority(int newPriority);
```

**优先级概念说明：**
1. 线程总是存在优先级，优先级范围在`1~10`之间。JVM线程调度程序是基于优先级的 **抢先调度机制** 。  
   在大多数情况下，当前运行的线程优先级将大于或等于线程池中任何线程的优先级。但这仅仅是大多数情况。  
   **注意：线程的优先级仍然无法保障线程的执行次序。只不过，优先级高的线程获取`CPU`资源的概率较大，优先级低的并非没机会执行。**
2. 当线程池中线程都具有相同的优先级，调度程序的`JVM`实现自由选择它喜欢的线程。这时候调度程序的操作有两种可能：
   - 选择一个线程运行，直到它阻塞或者运行完成为止。
   - 时间分片，为池内的每个线程提供 **均等** 的运行机会。
3. 线程优先级为`1~10`之间的正整数，`JVM`从不会改变一个线程的优先级。然而，`1~10`之间的值是没有保证的。一些`JVM`可能不能识别`10`个不同的值，
而将这些优先级进行每两个或多个合并，变成少于`10`个的优先级，则两个或多个优先级的线程可能被映射为一个优先级。

在一个线程中开启另外一个新线程，则新开线程称为该线程的子线程，子线程初始优先级与父线程相同（ **线程创建时继承父线程的优先级** ）。  
示例代码：
```java
/**
 * Java线程：线程的调度-优先级
 */
public class Test {
    public static void main(String[] args) {
        Thread t1 = new MyThread1();
        Thread t2 = new Thread(new MyRunnable());
        t1.setPriority(10);
        t2.setPriority(1);

        t2.start();
        t1.start();
    }
}

class MyThread1 extends Thread {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("线程1第" + i + "次执行！");
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class MyRunnable implements Runnable {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("线程2第" + i + "次执行！");
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
```
执行结果：
```
线程1第0次执行！
线程2第0次执行！
线程1第1次执行！
线程2第1次执行！
线程1第2次执行！
线程2第2次执行！
线程1第3次执行！
线程2第3次执行！
线程1第4次执行！
线程2第4次执行！
```

### 3. 让步
线程的让步含义就是使当前运行着线程让出`CPU`资源，但是资源分配给谁不知道，仅仅是让出，当前线程状态回到可运行状态，等待`CPU`分配时间碎片从而重新运行。

<font color="red">**注意：并不是线程让步之后就不会继续执行，而是退回到可执行状态，后续也可能会被`CPU`继续分配时间碎片从而继续运行。**</font>  
> 其他更为详细的讲解参考上面的笔记：二、线程的状态及其转换过程 -> 2. 阻止线程执行 -> 2.2 线程的优先级和线程让步`yield()`

**线程的让步使用`Thread.yield()`方法，`yield()`为静态方法，功能是暂停当前正在执行的线程对象，并执行其他就绪状态的线程（含自己）。**
```java
/**
 * Java线程：线程的调度-让步
 */
public class Test {
    public static void main(String[] args) {
        Thread t1 = new MyThread1();
        Thread t2 = new Thread(new MyRunnable());

        t2.start();
        t1.start();
    }
}

class MyThread1 extends Thread {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("线程1第" + i + "次执行！");
        }
    }
}

class MyRunnable implements Runnable {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("线程2第" + i + "次执行！");
            Thread.yield();
        }
    }
}
```
执行结果：
```
线程2第0次执行！
线程2第1次执行！
线程2第2次执行！
线程1第0次执行！
线程1第1次执行！
线程1第2次执行！
线程1第3次执行！
线程1第4次执行！
线程2第3次执行！
线程2第4次执行！
```

### 4. 合并
线程合并的含义就是将几个并行线程的线程合并为一个单线程执行。  
应用场景是当一个线程必须等待另一个线程执行完毕才能执行时，可以使用`join()`方法。

`join()`为非静态方法，定义如下：
```java
// 等待该线程终止。 
void join()    
// 等待该线程终止的时间最长为 millis毫秒。
void join(long millis)    
// 等待该线程终止的时间最长为 millis毫秒 + nanos 纳秒。    
void join(long millis,int nanos)
```
```java
/**
 * Java线程：线程的调度-合并
 */
public class Test {
    public static void main(String[] args) {
        Thread t1 = new MyThread1();
        t1.start();

        for (int i = 0; i < 10; i++) {
            System.out.println("主线程第" + i + "次执行！");
            if (i > 2) try {
                //t1线程合并到主线程中，主线程停止执行过程，转而执行t1线程，直到t1执行完毕后继续。
                t1.join();
            } catch (InterruptedException e) { 
                e.printStackTrace();
            }
        }
    }
}

class MyThread1 extends Thread {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("线程1第" + i + "次执行！");
        }
    }
}
```
执行结果：
```
主线程第0次执行！
主线程第1次执行！
主线程第2次执行！
主线程第3次执行！
线程1第0次执行！
线程1第1次执行！
线程1第2次执行！
线程1第3次执行！
线程1第4次执行！
主线程第4次执行！
主线程第5次执行！
主线程第6次执行！
主线程第7次执行！
主线程第8次执行！
主线程第9次执行！
```

### 5. 守护线程
守护线程与普通线程写法上基本没区别，调用线程对象的方法`setDaemon(true)`，就可以将其设置为守护线程。

**守护线程使用的情况较少，但并非无用；  
如：JVM的垃圾回收、内存管理等线程都是守护线程。还有就是在做数据库应用时候，使用的数据库连接池，连接池本身也包含着很多后台线程，监控连接个数、超时时间、状态等等都是守护线程。**

`setDaemon(true)`方法的源码及示例代码：
```java
// 将该线程标记为守护线程或用户线程    
public final void setDaemon(boolean on)
```
```java
/**
 * Java线程：线程的调度-守护线程
 */
public class Test {
    public static void main(String[] args) {
        Thread t1 = new MyCommon();
        Thread t2 = new Thread(new MyDaemon());
        t2.setDaemon(true);        //设置为守护线程

        t2.start();
        t1.start();
    }
}

class MyCommon extends Thread {
    public void run() {
        for (int i = 0; i < 5; i++) {
            System.out.println("线程1第" + i + "次执行！");
            try {
                Thread.sleep(7);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

class MyDaemon implements Runnable {
    public void run() {
        for (long i = 0; i < 9999999L; i++) {
            System.out.println("后台线程第" + i + "次执行！");
            try {
                Thread.sleep(7);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
```
执行结果：
```
后台线程第0次执行！
线程1第0次执行！
线程1第1次执行！
后台线程第1次执行！
线程1第2次执行！
后台线程第2次执行！
后台线程第3次执行！
线程1第3次执行！
线程1第4次执行！
后台线程第4次执行！
后台线程第5次执行！
```
从上面的执行结果可以看出：前台线程是保证能执行完毕的，而后台线程还没有执行完毕就退出了。

**实际上：`JVM`判断程序是否执行结束的标准是所有的前台执线程行完毕了，而不管后台线程的状态；因此，在使用后台线程（守护线程）时一定要注意这个问题。**

**注意：**
- 该方法必须在启动线程前调用；
- 当正在运行的线程都是守护线程时，Java虚拟机退出；
- 该方法首先调用该线程的 `checkAccess`方法，且不带任何参数。这可能抛出异常 `SecurityException`（在当前线程中）。  

## 六、线程池
### 线程池简述
在`Java5`中，对`Java`线程的类库做了大量的扩展， **其中线程池就是`Java5`的新特征之一。**

线程池的基本思想类比对象池的思想，开辟一块内存空间，里面存放了众多（未死亡）的线程，池中线程的调度执行由池管理器（`java.util.concurrent.Executors`）来处理。  
当有线程任务时，从池中取一个，执行完成后线程对象回到池中，这样可以避免反复创建线程对象所带来的性能开销，节省了系统的资源。

在使用线程池之前，必须知道如何去创建一个线程池，在`Java5`中，需要了解的是`java.util.concurrent.Executors`类的`API`，这个类提供大量创建连接池的静态方法。

### 1. 固定大小的线程池
```java
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

/**
 * Java线程：线程池
 */
public class Test {
    public static void main(String[] args) {
        //创建一个可重用固定线程数的线程池
        ExecutorService pool = Executors.newFixedThreadPool(2);
        //创建实现了Runnable接口对象，Thread对象当然也实现了Runnable接口
        Thread t1 = new MyThread();
        Thread t2 = new MyThread();
        Thread t3 = new MyThread();
        Thread t4 = new MyThread();
        Thread t5 = new MyThread();
        //将线程放入池中进行执行
        pool.execute(t1);
        pool.execute(t2);
        pool.execute(t3);
        pool.execute(t4);
        pool.execute(t5);
        //关闭线程池
        pool.shutdown();
    }
}

class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + "正在执行。。。");
    }
}
```
执行结果：
```
pool-1-thread-2正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-1正在执行。。。
```

### 2. 单任务线程池
在上例的基础上改一行创建`pool`对象的代码为：
```java
//创建一个使用单个 worker线程的 Executor，以无界队列方式来运行该线程。
ExecutorService pool = Executors.newSingleThreadExecutor();
```
执行结果：
```
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
```

### 3. 可变尺寸的线程池
与上面的类似，只是改动下`pool`的创建方式：
```java
//创建一个可根据需要创建新线程的线程池，但是在以前构造的线程可用时将重用它们。
ExecutorService pool = Executors.newCachedThreadPool();
```
执行结果：
```
pool-1-thread-5正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-4正在执行。。。
pool-1-thread-3正在执行。。。
pool-1-thread-2正在执行。。。
```

### 4. 延迟线程池
```java
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * Java线程：线程池
 */
public class Test {
    public static void main(String[] args) {
        //创建一个线程池，它可安排在给定延迟后运行命令或者定期地执行。
        ScheduledExecutorService pool = Executors.newScheduledThreadPool(2);
        //创建实现了Runnable接口对象，Thread对象当然也实现了Runnable接口
        Thread t1 = new MyThread();
        Thread t2 = new MyThread();
        Thread t3 = new MyThread();
        Thread t4 = new MyThread();
        Thread t5 = new MyThread();
        //将线程放入池中进行执行
        pool.execute(t1);
        pool.execute(t2);
        pool.execute(t3);
        //使用延迟执行风格的方法
        pool.schedule(t4, 10, TimeUnit.MILLISECONDS);
        pool.schedule(t5, 10, TimeUnit.MILLISECONDS);
        //关闭线程池
        pool.shutdown();
    }
}

class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + "正在执行。。。");
    }
}
```
执行结果：
```
pool-1-thread-1正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-1正在执行。。。
```

### 5. 单任务延迟线程池
在实例代码4的基础上，做改动：
```java
//创建一个单线程执行程序，它可安排在给定延迟后运行命令或者定期地执行。
ScheduledExecutorService pool = Executors.newSingleThreadScheduledExecutor();
```
执行结果：
```
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-1正在执行。。。
```

### 6. 自定义线程池
```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/**
 * Java线程：线程池-自定义线程池
 */
public class Test {
    public static void main(String[] args) {
        //创建等待队列
        BlockingQueue<Runnable> bqueue = new ArrayBlockingQueue<Runnable>(20);
        //创建一个单线程执行程序，它可安排在给定延迟后运行命令或者定期地执行。
        ThreadPoolExecutor pool = new ThreadPoolExecutor(2, 3, 2, TimeUnit.MILLISECONDS, bqueue);
        //创建实现了Runnable接口对象，Thread对象当然也实现了Runnable接口
        Thread t1 = new MyThread();
        Thread t2 = new MyThread();
        Thread t3 = new MyThread();
        Thread t4 = new MyThread();
        Thread t5 = new MyThread();
        Thread t6 = new MyThread();
        Thread t7 = new MyThread();
        //将线程放入池中进行执行
        pool.execute(t1);
        pool.execute(t2);
        pool.execute(t3);
        pool.execute(t4);
        pool.execute(t5);
        pool.execute(t6);
        pool.execute(t7);
        //关闭线程池
        pool.shutdown();
    }
}

class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println(Thread.currentThread().getName() + "正在执行。。。");
        try {
            Thread.sleep(100L);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```
执行结果：
```
pool-1-thread-1正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-2正在执行。。。
pool-1-thread-1正在执行。。。
pool-1-thread-2正在执行。。。
```
**自定义连接池稍微麻烦些，不过通过创建的`ThreadPoolExecutor`线程池对象，可以获取到当前线程池的尺寸、正在执行任务的线程数、工作队列等等。**

### 7. 补充：线程池相关面试题
**什么是线程池？**  
线程池是一种多线程处理形式，处理过程中将任务提交到线程池，任务的执行交由线程池来管理。

**为什么要使用线程池？**  
创建线程和销毁线程的花销是比较大的，这些时间有可能比处理业务的时间还要长。这样频繁的创建线程和销毁线程，再加上业务工作线程，消耗系统资源的时间，可能导致系统资源不足。（线程池可以把频繁创建和销毁的线程的过程去掉）

**线程池有什么作用？**  
线程池作用就是限制系统中执行线程的数量。
1. 提高效率：提前创建好一定数量的线程放在池中，等需要使用的时候就从池中拿一个，这要比需要的时候创建一个线程对象要快的多。
2. 方便管理：可以编写线程池管理代码对池中的线程统一管理。  
比如：程序启动时创建`100`个线程，每当有请求的时候，就分配一个线程去工作，如果刚好并发有`101`个请求，那多出的这一个请求可以排队等候，避免因无休止的创建线程导致系统崩溃。

**说说几种常见的线程池及使用场景**  
1. `new SingleThreadExecutor`  
  创建一个单线程化的线程池，它只会用唯一的工作线程来执行任务，保证所有任务按照指定顺序(`FIFO-进先出`, `LIFO-后进先出`)执行。
2. `new FixedThreadPool`  
  创建一个定长线程池，可控制线程最大并发数，超出的线程会在队列中等待。
3. `new CachedThreadPool`  
  创建一个可缓存线程池，如果线程池长度超过处理需要，可灵活回收空闲线程，若无可回收，则新建线程。
4. `new ScheduledThreadPool`  
  创建一个定长线程池，支持定时及周期性任务执行。

**线程池中的几种重要的参数**  
- **corePoolSize：** 线程池中的核心线程数量。这几个核心线程，就算在没有用的时候，也不会被回收
- **maximumPoolSize：** 线程池中可以容纳的最大线程的数量
- **keepAliveTime：** 线程池中除了核心线程之外的其他线程最长可以保留的时间。  
因为在线程池中，除了核心线程即使在无任务的情况下也不能被清除，其余的都是有存活时间的，意思就是非核心线程可以保留的最长的空闲时间。
- **util：** 计算`keepAliveTime`所存活的时间单位。
- **workQueue：** 等待队列。任务可以储存在任务队列中等待被执行，执行的是`FIFIO`（先进先出）原则。
- **threadFactory：** 创建线程的线程工厂。
- **handler：** 拒绝策略。可以在任务满了之后，按照指定拒绝执行某些任务。

**说说线程池的拒绝策略**  
当请求任务不断过来，而系统此时又处理不过来的时候，我们需要采取的策略是拒绝服务。`RejectedExecutionHandler`接口提供了拒绝任务处理的自定义方法的机会。

在`ThreadPoolExecutor`中已经包含四种处理策略。
1. **`AbortPolicy`策略：** 该策略会直接抛出异常，阻止系统正常工作。
2. **`CallerRunsPolicy`策略：** 只要线程池未关闭，该策略直接在调用者线程中，运行当前的被丢弃的任务。
3. **`DiscardOleddestPolicy`策略：** 该策略将丢弃最老的一个请求，也就是即将被执行的任务，并尝试再次提交当前任务。
4. **`DiscardPolicy`策略：** 该策略默默的丢弃无法处理的任务，不予任何处理。

除了`JDK`默认提供的四种拒绝策略，我们可以根据自己的业务需求去自定义拒绝策略，自定义的方式很简单，直接实现`RejectedExecutionHandler`接口即可。

**execute和submit的区别？**  
在前面的讲解中，我们执行任务是用的`execute`方法，除了`execute`方法，还有一个`submit`方法也可以执行我们提交的任务。
- **execute：** 适用于不需要关注返回值的场景，只需要将线程丢到线程池中去执行就可以了；
- **submit：** 适用于需要关注返回值的场景。

**五种线程池的使用场景**  
1. `SingleThreadExecutor`：  
一个单线程的线程池，可以用于需要保证顺序执行的场景，并且只有一个线程在执行。
2. `FixedThreadPool`：  
一个固定大小的线程池，可以用于已知并发压力的情况下，对线程数做限制。
3. `CachedThreadPool`：  
一个可以无限扩大的线程池，比较适合处理请求比较多且执行时间比较短的情况。
4. `new ScheduledThreadPool`：  
可以延时启动、定时启动的线程池，适用于需要多个后台线程执行周期任务的场景。
5. `new WorkStealingPool`：  
一个拥有多个任务队列的线程池，可以减少连接数，创建当前可用`cpu`数量的线程来并行执行。

**线程池的关闭**  
关闭线程池可以调用`shutdownNow`和`shutdown`两个方法来实现
- **shutdownNow：** 对正在执行的任务全部发出`interrupt()`，停止执行，对还未开始执行的任务全部取消，并且返回还没开始的任务列表。
- **shutdown：** 当调用`shutdown`后，线程池将不再接受新的任务，但也不会去强制终止已经提交或者正在执行中的任务，而是让其继续执行。

**初始化线程池时线程数的选择**  
- 如果任务是`IO`密集型，一般线程数需要设置 **`2`倍`CPU`数** 以上，以此来尽量利用`CPU`资源。
- 如果任务是`CPU`密集型，一般线程数量只需要设置 **`CPU`数加`1`** 即可；更多的线程数也只能增加上下文切换，并不能增加`CPU`利用率。

上述只是一个基本思想，如果真的需要精确的控制，还是需要上线以后观察线程池中线程数量和线程队列的情况来定。

**线程池都有哪几种工作队列**  
1. `ArrayBlockingQueue`：是一个基于数组结构的有界阻塞队列。  
此队列按 `FIFO`（先进先出）原则对元素进行排序。
2. `LinkedBlockingQueue`：一个基于链表结构的阻塞队列。  
此队列按`FIFO` （先进先出） 排序元素，吞吐量通常要高于`ArrayBlockingQueue`。静态工厂方法`Executors.newFixedThreadPool()`使用了这个队列
3. `SynchronousQueue`：一个不存储元素的阻塞队列。  
每个插入操作必须等到另一个线程调用移除操作，否则插入操作一直处于阻塞状态，吞吐量通常要高于`LinkedBlockingQueue`。静态工厂方法`Executors.newCachedThreadPool()`使用了这个队列。
4. `PriorityBlockingQueue`：一个具有优先级的无限阻塞队列。

## 七、有返回值的线程 - Callable和Future
在`Java5`之前，线程是没有返回值的，常常为了 **“有”** 返回值，破费周折，而且代码很不好写。必须通过共享变量或者使用线程通信的方式来达到效果，这样使用起来就比较麻烦。

在`Java5`之前使用`Runnable`来获取返回结果的实现，示例代码如下：
```java
import java.util.Random;

public class RunnableTest {
    public static void main(String[] args) throws Exception {
        RunnableExample[] randomNumberTasks = new RunnableExample[5];

        for (int i = 0; i < 5; i++) {
            randomNumberTasks[i] = new RunnableExample();
            Thread t = new Thread(randomNumberTasks[i]);
            t.start();
        }

        for (int i = 0; i < 5; i++)
            System.out.println(randomNumberTasks[i].get());
    }
}

class RunnableExample implements Runnable {
    // 存储结果的共享对象
    private Object result = null;

    public void run() {
        Random generator = new Random();
        Integer randomNumber = generator.nextInt(5);

        try {
            Thread.sleep(randomNumber * 1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        // 完成后将返回值存储在结果中
        result = randomNumber;

        // 唤醒 get() 方法上阻塞的线程
        synchronized (this) {
            notifyAll();
        }
    }

    public synchronized Object get()
            throws InterruptedException {
        while (result == null)
            wait();
        return result;
    }
}
```
执行结果：
```
3
0
0
0
2
```

通过上面的笔记可以知道`Runnable`缺少的一项功能是，当线程终止时（即`run()`执行完成时），我们无法使线程返回结果，当需要获取结果的话，过程是很复杂的。为了支持此功能，`Java1.5`之后提供了`Callable`接口。

`Callble`源码：
```java
@FunctionalInterface
public interface Callable<V> {
    /**
     * Computes a result, or throws an exception if unable to do so.
     *
     * @return computed result
     * @throws Exception if unable to compute a result
     */
    V call() throws Exception;
}
```
执行`Callable`任务后，可以获取一个`Future`的对象，在该对象上调用`get`就可以获取到`Callable`任务返回的`Object`了，当然 **`Callable<V>`是支持泛型的。**

示例代码：
```java
import java.util.concurrent.*;

/**
 * Java线程：有返回值的线程Callable
 */
public class Test {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        //创建一个线程池
        ExecutorService pool = Executors.newFixedThreadPool(2);
        //创建两个有返回值的任务
        Callable c1 = new MyCallable("A");
        Callable c2 = new MyCallable("B");
        //执行任务并获取Future对象
        Future f1 = pool.submit(c1);
        Future f2 = pool.submit(c2);
        //从Future对象上获取任务的返回值，并输出到控制台
        System.out.println(">>>" + f1.get().toString());
        System.out.println(">>>" + f2.get().toString());
        //关闭线程池
        pool.shutdown();
    }
}

class MyCallable implements Callable {
    private String oid;

    MyCallable(String oid) {
        this.oid = oid;
    }

    @Override
    public Object call() throws Exception {
        return oid + "任务返回的内容";
    }
}
```
执行结果：
```
>>>A任务返回的内容
>>>B任务返回的内容
```

**小结：**  
对比`Callable`和`Runnable`的两者区别：  
1. 为了实现`Runnable`，需要实现不返回任何内容的`run()`方法，而对于`Callable`，需要实现在完成时返回结果的`call()`方法。**请注意，不能使用`Callable`创建线程，只能使用`Runnable`或者`线程池`来创建线程。**
2. 实现`Callable`就必须重写`call()`方法。
3. `Callable`的`call()`方法可以有返回值，而`Runnable`的`run()`方法不能有返回值。
4. `Callable`的`call()`方法可抛出异常，而`Runnable`的`run()`方法不能抛出异常。 

## 八、补充 - Future、FutureTask、CompletableFuture
上面已经介绍了`Callable`的基本使用方法以及和`Runnable`的区别。接下来介绍另一个接口`Future`。

### 1. Future
`Future`表示一个任务的生命周期，并提供了方法来判断是否已经完成或取消，以及获取任务的结果和取消任务等。

接口源码：
```java
public interface Future<V> {

    // 尝试取消此任务的执行
    boolean cancel(boolean mayInterruptIfRunning);
    
    // 如果此任务在正常完成之前被取消，则返回true
    boolean isCancelled();

    /**
     * 如果此任务完成，则返回 true 
     * 完成可能是由于正常终止、异常或取消——在所有这些情况下，此方法将返回true
     */
    boolean isDone();
    
    // 如有必要，等待计算完成，然后检索其结果。
    V get() throws InterruptedException, ExecutionException;

    // 如有必要，最多等待给定时间以完成计算，然后检索其结果
    V get(long timeout, TimeUnit unit)
        throws InterruptedException, ExecutionException, TimeoutException;
}
```
在`Future`接口中声明了`5`个方法，下面依次解释每个方法的作用：
- **`cancel(boolean mayInterruptIfRunning)`：** 用来取消任务，如果取消任务成功则返回`true`，如果取消任务失败则返回`false`。  
参数`mayInterruptIfRunning`表示是否允许取消正在执行却没有执行完毕的任务，如果设置`true`，则表示可以取消正在执行过程中的任务。  
    - 如果任务已经完成：则无论`mayInterruptIfRunning`为`true`还是`false`，此方法肯定返回`false`；
    - 如果任务还没有执行：则无论`mayInterruptIfRunning`为`true`还是`false`，肯定返回`true`；
    - 如果任务正在执行：
        - 若`mayInterruptIfRunning`设置为`true`，则返回`true`；
        - 若`mayInterruptIfRunning`设置为`false`，则返回`false`。
- **`isCancelled()`：** 表示任务是否被取消成功，如果在任务正常完成前被取消成功，则返回 `true`。
- **`isDone()`：** 表示任务是否已经完成，若任务完成，则返回`true`；
- **`get()`：** 用来获取执行结果，这个方法会产生阻塞，会一直等到任务执行完毕才返回；
- **`get(long timeout, TimeUnit unit)`：** 用来获取执行结果，如果在指定时间内，还没获取到结果，就直接返回`null`。

也就是说实际上Future提供了三种功能：
- 判断任务是否完成；
- 中断任务；
- 获取任务执行结果。

**<font color="red">Future与Callable的关系与ExecutorService与Executor的关系对应。</font>**

`Future`与`Callable`搭配使用的示例代码：
```java
 public static void main(String[] args) throws ExecutionException, InterruptedException {
    FutureTask<String> task=new FutureTask<>(new Callable<String>() {
        @Override
        public String call() throws Exception {
            System.out.println("子线程正在开始运行");
            Thread.sleep(3000);
            return "子线程执行任务完毕";
        }
    });
    new Thread(task).start();
   System.out.println(task.get());

   System.out.println("所有任务执行完毕");
}
```
执行结果：
```
子线程正在开始运行
子线程执行任务完毕
所有任务执行完毕
```

还可以配合`ExecutorService`使用：
```java
public static void main(String[] args) throws ExecutionException, InterruptedException {
    ExecutorService executor=Executors.newCachedThreadPool();
    Future<Integer> result=executor.submit(new Callable<Integer>() {
        @Override
        public Integer call() throws Exception {
            System.out.println("子线程开始执行任务");
            Thread.sleep(3000);
            int sum=0;
            for(int i=0;i<100;i++){
                sum+=i;
            }
            return sum;
        }
    });
    executor.shutdown();
    System.out.println("任务运行结果为："+result.get());
    System.out.println("所有线程执行完毕");
}
```
执行结果：
```
子线程开始执行任务
任务运行结果为：4950
所有线程执行完毕
```

**注意：`Future.get()`方法是一个阻塞方法，会阻塞当前线程，当`submit`提交多个任务时，只有所有任务都完成后，才能使用`get()`按照任务的提交顺序得到返回结果；  
所以，一般需要使用`Future.isDone()`先判断任务是否全部执行完成，完成后再使用`Future.get()`得到结果。当然也可以用`Future.get(long timeout, TimeUnit unit)`方法可以设置超时时间，防止无限时间的等待。**

### 2. FutureTask
`Future`只是一个接口，无法直接创建对象，因此有了`FutureTask`。

先来看下`FutureTask`的实现：
```java
public class FutureTask<V> implements RunnableFuture<V>
```

`FutureTask`类实现了`RunnableFuture`接口：
```java
public interface RunnableFuture<V> extends Runnable, Future<V> {
    void run();
}
```
`RunnableFuture`继承了`Runnable`和`Future`接口，而`FutureTask`实现了`RunnableFuture`接口。
`FutureTask`的继承关系和方法如图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/并发/线程、线程池与多线程（Java）/FutureTask的继承关系.jpg)
</center>

可以把`FutureTask`交给`Executor`执行；也可以通`ExecutorService.submit(…)`方法返回一个`FutureTask`，然后执行`FutureTask.get()`方法或`FutureTask.cancel(…)`方法。除此以外，还可以单独使用`FutureTask`。

**当一个线程需要等待另一个线程把某个任务执行完后它才能继续执行，此时可以使用`FutureTask`。**  
假设有多个线程执行若干任务，每个任务最多只能被执行一次。当多个线程试图同时执行同一个任务时，只允许一个线程执行任务，其他线程需要等待这个任务执行完后才能继续执行。  

示例代码：
```java
import java.util.concurrent.*;

public class Test {
    public static void main(String[] args) {
        ExecutorService service = Executors.newCachedThreadPool();
        Task task = new Task();
        FutureTask<Integer> futureTask = new FutureTask<>(task);
        service.submit(futureTask);
        service.shutdown();
        System.out.println("主线程正在执行任务。。。");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            //阻塞直至任务完成
            System.out.println("-------------------------------------");
            System.out.println("执行结果为：" + futureTask.get());
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (ExecutionException e) {
            e.printStackTrace();
        }
        System.out.println("任务执行完成。。。");
    }

    static class Task implements Callable<Integer> {
        @Override
        public Integer call() throws Exception {
            try {
                System.out.println("从线程正在执行任务。。。");
                Thread.sleep(3000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            int num = 0;
            for (int i = 0; i <= 100; i++) {
                num += i;
            }
            return num;
        }
    }
}
```
执行结果：
```
主线程正在执行任务。。。
从线程正在执行任务。。。
-------------------------------------
执行结果为：5050
任务执行完成。。。
```
`futureTask.get()`执行时如果该任务已经执行完了则直接返回执行结果，如果没有执行完则线程会阻塞在这里，直至任务执行完毕。  
当然还可以用`get(long timeout, TimeUnit unit)`来获取执行结果，如果在指定时间内，还没获取到结果，就直接返回`null`。

### 3. CompletableFuture
`completableFuture`是`JDK1.8`版本新引入的类。 实现了`CompletionStage`接口和`Future`接口，前者是对后者的一个扩展，增加了异步回调、流式处理、多个`Future`组合处理的能力，使Java在处理多任务的协同工作时更加顺畅便利。

一个`completetableFuture`就代表了一个任务。他能用`Future`的方法。还能做一些之前说的`executorService`配合`Future`做不了的：  
之前`future`需要等待`isDone()`为`true`才能知道任务跑完了。或者就是用`get()`方法调用的时候会出现阻塞。而使用`completableFuture`的使用就可以用`then`，`when`等等操作来防止以上的阻塞和轮询`isDone()`的现象出现。

具体说明：  
在`JDK1.5`已经提供了`Future`和`Callable`的实现，可以用于阻塞式获取结果，如果想要异步获取结果，通常都会以轮询的方式去获取结果，如下:
```java
//定义一个异步任务
Future<String> future = executor.submit(()->{
       Thread.sleep(2000);
       return "hello world";
});
//轮询获取结果
while (true){
    if(future.isDone()) {
         System.out.println(future.get());
         break;
     }
 }
```
从上面的形式看来轮询的方式会耗费无谓的`CPU`资源，而且也不能及时地得到计算结果。所以要实现真正的异步，上述这样是完全不够的。

而`JDK1.8`中的`CompletableFuture`就为我们提供了异步函数式编程，`CompletableFuture`提供了非常强大的`Future`的 **扩展功能** ，可以帮助我们简化异步编程的复杂性，提供了函数式编程的能力，可以通过回调的方式处理计算结果，并且提供了转换和组合`CompletableFuture`的方法。

`CompletableFuture`的更多详细讲解请参考：[CompletableFuture用法详解](https://zhuanlan.zhihu.com/p/344431341)
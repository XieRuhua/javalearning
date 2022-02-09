# ThreadLocal（JDK1.8）

***

[笔记内容参考1：ThreadLocal](https://www.jianshu.com/p/3c5d7f09dfbd)   
[笔记内容参考2：Java中ThreadLocal的实际用途是啥？](https://www.zhihu.com/question/341005993)  
[笔记内容参考3：面试官问我ThreadLocal，我一口气给他说了四种！](https://segmentfault.com/a/1190000024437984)  
[笔记内容参考4：万字长文带你深入理解ThreadLocal！ThreadLocal超详细解析！](https://blog.csdn.net/weixin_43314519/article/details/108188298)

[toc]

## 一、ThreadLocal是什么
> 线程本地变量、线程本地存储。  
> 早在JDK 1.2的版本中就提供`java.lang.ThreadLocal`，为解决多线程程序的并发问题提供了一种新的思路。使用这个工具类可以很简洁地编写出优美的多线程程序。

ThreadLocal是一个线程内部的存储类，可以在指定线程内存储数据，数据存储以后，只有指定线程可以得到存储数据，官方解释如下：
```java
/**
 * This class provides thread-local variables.  These variables differ from
 * their normal counterparts in that each thread that accesses one (via its
 * {@code get} or {@code set} method) has its own, independently initialized
 * copy of the variable.  {@code ThreadLocal} instances are typically private
 * static fields in classes that wish to associate state with a thread (e.g.,
 * a user ID or Transaction ID).
 */
```
大致意思就是`ThreadLocal`提供了线程内存储变量的能力，这些变量不同之处在于每一个线程读取的变量是对应且互相独立的。通过`get()`和`set()`方法就可以对当前线程对应的值进行存取。

当使用ThreadLocal维护变量时，ThreadLocal为每个使用该变量的线程提供独立的变量副本，所以每一个线程都可以独立地改变自己的副本，而不会影响其它线程所对应的副本。

**从线程的角度看，目标变量就象是线程的本地变量，这也是类名中“Local”所要表达的意思。**

> 注意：线程局部变量并不是Java的独有发明，很多语言（如IBM XL FORTRAN）在语法层面就提供线程局部变量。  
由于在Java中没有提供在语言级支持，而是变相地通过`ThreadLocal`的类提供支持。 所以，在Java中编写线程局部变量的代码相对来说要笨拙一些，因此造成`ThreadLocal`没有在Java开发者中得到很好的普及。

## 二、使用方式
```java
public static void main(String[] args) {
    ThreadLocal<String> localName = new ThreadLocal();
    localName.set("张三");
    String name = localName.get();
    System.out.println("localName中的值：" + name);
    localName.remove();
}
```
执行结果：
```text
localName中的值：张三
```

## 三、实现原理（源码分析）
### 1. 简述：
ThreadLocal有4个供外部调用的方法：
- **void set(Object value)**   
设置当前线程的线程局部变量的值。
- **public Object get()**  
返回当前线程所对应的线程局部变量。
- **public void remove()**  
将当前线程局部变量的值删除，目的是为了减少内存的占用；该方法是JDK 5.0新增的方法。  
需要注意的是：当线程结束后，对应该线程的局部变量将自动被垃圾回收，所以显式调用该方法清除线程的局部变量并不是必须的操作，但它可以加快内存回收的速度（后续会讲到`ThreadLocal`的内存泄露问题）。
- **protected Object initialValue()**  
返回该线程局部变量的初始值，该方法是一个protected的方法，显然是为了让子类覆盖而设计的。这个方法是一个延迟调用方法，在线程第1次调用`get()`或`set()`时才执行，并且仅执行1次。`ThreadLocal`中的缺省实现直接返回一个`null`。

**注：** 在JDK5.0中，`ThreadLocal`已经支持泛型，该类的类名已经变为`ThreadLocal<T>`。API方法也相应进行了调整，新版本的API方法分别是`void set(T value)`、`T get()`以及`T initialValue()`。

### 2. set方法

```java
//set 方法
public void set(T value) {
    //获取当前线程
    Thread t = Thread.currentThread();
    //实际存储的数据结构类型
    ThreadLocalMap map = getMap(t);
    //如果存在map就直接set，没有则创建map并set
    if (map != null)
        map.set(this, value);
    else
        createMap(t, value);
}

//getMap方法
ThreadLocalMap getMap(Thread t) {
    //thred中维护了一个ThreadLocalMap
    return t.threadLocals;
}

//createMap
void createMap(Thread t, T firstValue) {
    //实例化一个新的ThreadLocalMap，并赋值给线程的成员变量threadLocals
    t.threadLocals = new ThreadLocalMap(this, firstValue);
}
```
**执行步骤：**  
1. 首先获取到了当前线程，每个线程持有一个`ThreadLocalMap`对象；
2. 然后调用`getMap(t)`获取`ThreadLocalMap`，每一个新的线程`Thread`都会实例化一个`ThreadLocalMap`并赋值给成员变量`threadLocals`；
3. 如果`map`存在，则将当前线程对象`t`作为key，要存储的对象作为`value`存到`map`里面去；
4. 如果该`map`不存在，则初始化一个。

**注：`ThreadLocalMap`的详解见笔记最后的补充1**

### 3. get方法
```java
//ThreadLocal中get方法
public T get() {
    Thread t = Thread.currentThread();
    ThreadLocalMap map = getMap(t);
    if (map != null) {
        ThreadLocalMap.Entry e = map.getEntry(this);
        if (e != null) {
            @SuppressWarnings("unchecked")
            T result = (T)e.value;
            return result;
        }
    }
    return setInitialValue();
}
    
//ThreadLocalMap中getEntry方法
private Entry getEntry(ThreadLocal<?> key) {
    int i = key.threadLocalHashCode & (table.length - 1);
    Entry e = table[i];
    if (e != null && e.get() == key)
        return e;
    else
        return getEntryAfterMiss(key, i, e);
}
```
**执行步骤：**  
1. 首先获取当前线程；
2. 然后调用`getMap()`方法获取一个`ThreadLocalMap`；
3. 如果`map`不为null，那就使用当前线程作为`ThreadLocalMap`的`Entry`的键，然后值就作为相应的的值；
4. 如果没有那就设置一个初始值`setInitialValue()`，即为`null`。

```java
/**
 * Variant of set() to establish initialValue. Used instead
 * of set() in case user has overridden the set() method.
 * 用于建立初始值的 set() 变体。用于代替 set() 以防用户覆盖 set() 方法。
 *
 * @return the initial value
 */
private T setInitialValue() {
    T value = initialValue();
    // 获取当前线程
    Thread t = Thread.currentThread();
    // 获取当前线程对应的ThreadLocalMap对象
    ThreadLocalMap map = getMap(t);
    if (map != null)
        // 如果当前线程的ThreadLocalMap存在，将值存进去
        map.set(this, value);
    else
        // 如果当前线程的ThreadLocalMap不存在，创建一个新的ThreadLocalMap对象并保存
        createMap(t, value);
    // 返回get的值，当然，这里get的值是空
    return value;
}
```
```java
protected T initialValue() {
    return null;
}
```
```java
void createMap(Thread t, T firstValue) {
    t.threadLocals = new ThreadLocalMap(this, firstValue);
}
```

### 4. remove方法
```java
public void remove() {
    ThreadLocalMap m = getMap(Thread.currentThread());
    if (m != null)
        m.remove(this);
}
```
**执行步骤：**
1. 获取当前线程对应的`ThreadLocalMap`对象；
2. 如果`ThreadLocalMap`对象不为空，直接移除即可。

## 四、应用场景
**当很多线程需要多次使用同一个对象，并且需要该对象具有相同初始化值的时候最适合使用`ThreadLocal`。**

### 场景1：Spring实现事务隔离级别
`Spring`采用`Threadlocal`的方式，来保证单个线程中的数据库操作使用的是同一个数据库连接，同时，采用这种方式可以使业务层使用事务时不需要感知并管理`connection`对象；通过传播级别，巧妙地管理多个事务配置之间的切换，挂起和恢复。

Spring框架里面就是用的`ThreadLocal`来实现这种隔离，主要是在`org.springframework.transaction.support.TransactionSynchronizationManager`这个类里面，代码如下所示:
```java
public abstract class TransactionSynchronizationManager {

	private static final Log logger = LogFactory.getLog(TransactionSynchronizationManager.class);

	private static final ThreadLocal<Map<Object, Object>> resources =
			new NamedThreadLocal<>("Transactional resources");

	private static final ThreadLocal<Set<TransactionSynchronization>> synchronizations =
			new NamedThreadLocal<>("Transaction synchronizations");

	private static final ThreadLocal<String> currentTransactionName =
			new NamedThreadLocal<>("Current transaction name");

	private static final ThreadLocal<Boolean> currentTransactionReadOnly =
			new NamedThreadLocal<>("Current transaction read-only status");

	private static final ThreadLocal<Integer> currentTransactionIsolationLevel =
			new NamedThreadLocal<>("Current transaction isolation level");

	private static final ThreadLocal<Boolean> actualTransactionActive =
			new NamedThreadLocal<>("Actual transaction active");
	// .......................
}
```
**Spring的事务主要是`ThreadLocal`和`AOP`去做实现的。**

### 场景2：利用ThreadLocal保存登录Session信息
一般的Web应用划分为 **展现层、服务层、持久层** 三个层次（MVC：M-->业务模型，V-->用户界面，C-->控制器），在不同的层中编写对应的逻辑，下层通过接口向上层开放功能调用。**在一般情况下，从接收请求到返回响应所经过的所有程序调用都同属于一个线程。**

而在实际的项目开发中，如在APP调用服务端API接口的时候，需要`token`（登录）验证并且在具体的方法中可能会使用到当前登录账户的更多信息（比如当前登录账户的用户ID）。  
此时通常会把`token`放在http请求的`request请求头`中，然后将当前`Session`信息存储在`ThreadLocal`中，在请求处理过程中可以随时使用`Session`信息，每个请求之间的`Session`信息互不影响。当请求处理完成后通过`remove`方法将当前`Session`信息清除即可。

使用`ThreadLoacl`定义一个简单的`session`存取工具类：
```java
/**
 * 利用线程本地变量来保存登录信息
 */
public class SessionCache {
 	// 假设登录的用户信息为String，实际开发中为用户对象
	private static ThreadLocal<String> threadLocal = new ThreadLocal<>();
 
	public static <T extends String> void put(T t) {
		threadLocal.set(t);
	}
 
	@SuppressWarnings("unchecked")
	public static <T> T get() {
		return (T) threadLocal.get();
	}
 
	public static void remove() {
		threadLocal.remove();
	}
}
```

定义一个拦截器并注册到MVC的配置中：
```java
/**
 * 简易的登录拦截器
 */
public class LoginAuthInterceptor implements HandlerInterceptor {
	private static final Logger logger = LoggerFactory.getLogger(LoginAuthInterceptor.class);

	@Override
	public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
			throws Exception {
		// 从请求头中获取token
		String token = request.getHeader("token");
		// 省略校验动作.....
		
		// 将校验通过的session存入session工具类中
		SessionCache.put(token);
		logger.info("请求方法方法前拦截");
		return true;
	}
 
	@Override
	public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler,
			@Nullable Exception ex) throws Exception {
		// 请求完成之后调用remove()，防止内存溢出
		SessionCache.remove();
		logger.info("请求方法方法后处理");
	}
}

/**
 * 拦截器配置注册
 */
@Configuration
public class LoginConfig implements WebMvcConfigurer {
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        //注册LoginAuthInterceptor拦截器
        InterceptorRegistration registration = registry.addInterceptor(new LoginAuthInterceptor());
        //所有路径都被拦截
        registration.addPathPatterns("/**");
    }
}
```

写一个测试类测试一下：
```java
@RestController
public class TestController {
 
	private static final Logger logger = LoggerFactory.getLogger(TestController.class);
 
	@GetMapping(value = "/session")
	public String session() {
		String sessionStr = SessionCache.get();
		logger.info("当前登录用户ID为{}", sessionStr);
		return "success：" + sessionStr;
	}
}
```
需要注意的是，在拦截器的完成方法`afterCompletion()`中必须调用`SessionCache.remove();`也就是`ThreadLocal`的`remove()`。防止**内存溢出**。（后续会讲到）

### 场景3：使用ThreadLocal解决上下文调用SimpleDateFormat线程不安全的问题
还有一个用的比较多的场景就是用来解决`SimpleDateFormat`解决线程不安全的问题，不过现在`java8`提供了`DateTimeFormatter`它是线程安全的。

SimpleDateFormat线程不安全验证：
```java
public class SimpleDateFormatTest {
    private static SimpleDateFormat f = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
    public static void main(String[] args) {
        for (int i = 0; i < 100; i++) {
            new Thread(() -> {
                // 格式化当前时间
                String dateStr = f.format(new Date());
                try {
                    // 将当前时间转化为Date类型
                    Date parseDate = f.parse(dateStr);
                    // 再转换为String类型
                    String dateStrCheck = f.format(parseDate);
                    // 比较两个时间串是否相等
                    boolean equals = dateStr.equals(dateStrCheck);
                    if (!equals) {
                        // 如果不相等，说明线程不安全
                        System.out.println(equals + " " + dateStr + " " + dateStrCheck);
                    } else {
                        System.out.println(equals);
                    }
                } catch (ParseException e) {
                    System.out.println(e.getMessage());
                }
            }).start();
        }
    }
}
```
当 `equals` 为`false` 时，证明线程不安全。运行结果如下：
```
false 2022-01-13 22:24:18 2240-11-13 22:24:18
true
true
true
true
true
true
true
false 2022-01-13 22:24:18 2022-01-13 22:10:18
false 2022-01-13 22:24:18 2022-01-13 22:10:18
...........
```

**使用`ThreadLocal`优化：**  
为了线程安全最直接的方式，就是每次调用都直接 `new SimpleDateFormat()`。但这样的方式终究不是最好的，所以可以使用 `ThreadLocal` ，来优化这段代码：
```java
public class SimpleDateFormatTest {
    private static ThreadLocal<SimpleDateFormat> threadLocal = ThreadLocal.withInitial(() ->new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"));

    public static void main(String[] args) {
        for (int i = 0; i < 100; i++) {
            new Thread(() -> {
                // 格式化当前时间
                String dateStr = threadLocal.get().format(new Date());
                try {
                    // 将当前时间转化为Date类型
                    Date parseDate = threadLocal.get().parse(dateStr);
                    // 再转换为String类型
                    String dateStrCheck = threadLocal.get().format(parseDate);
                    // 比较两个时间串是否相等
                    boolean equals = dateStr.equals(dateStrCheck);
                    if (!equals) {
                        // 如果不相等，说明线程不安全
                        System.out.println(equals + " " + dateStr + " " + dateStrCheck);
                    } else {
                        System.out.println(equals);
                    }
                } catch (ParseException e) {
                    System.out.println(e.getMessage());
                }
            }).start();
        }
        // 清空
        threadLocal.remove();
    }
}
```
优化后的代码将`SimpleDateFormat`放到`ThreadLocal`中进行使用，既不需要重复`new`对象，也避免了线程不安全问题。  
测试结果如下：
```
true
true
true
true
......................
```

## 五、ThreadLocal内存泄漏及为何ThreadlocalMap 中key是 WeakReference类型（弱引用）
### 1. 什么是内存泄漏
> 在Java中，内存泄漏就是存在一些被分配的对象，不会被GC所回收，然而它却一直占用着内存。
>
> 这些对象有下面两个特点：
> * 这些对象是可达的：即在有向图中，存在通路可以与其相连；
> * 这些对象是无用的：即程序以后不会再使用这些对象。
>
> 如果对象满足这两个条件，这些对象就可以判定为导致Java内存泄漏的对象。

### 2. Java中的引用类型简述
首先简单说一下java中的集中引用类型（[笔记：强引用、弱引用、软引用、虚引用](https://xieruhua.github.io/javalearning/#/./Java%E7%9B%B8%E5%85%B3/Java%E5%9F%BA%E7%A1%80%E7%AD%89/%E5%BC%BA%E5%BC%95%E7%94%A8%E3%80%81%E5%BC%B1%E5%BC%95%E7%94%A8%E3%80%81%E8%BD%AF%E5%BC%95%E7%94%A8%E3%80%81%E8%99%9A%E5%BC%95%E7%94%A8)）：
- **强引用**：是使用最普遍的引用。如果一个对象具有强引用，那**垃圾回收器**绝不会回收它，当**内存空间不足**时，`Java`虚拟机宁愿抛出`OutOfMemoryError`错误，使程序**异常终止**，也不会靠随意**回收**具有**强引用**的**对象**来解决内存不足的问题。
- **软引用**：如果一个对象只具有，则**内存空间充足**时，**垃圾回收器**就**不会**回收它；如果**内存空间不足**了，就会**回收**这些对象的内存。
- **弱引用**：弱引用与软引用类似，区别在于：只具有**弱引用**的对象拥有**更短暂**的**生命周期**。在垃圾回收器线程扫描内存区域时，一旦发现了只具有**弱引用**的对象，不管当前**内存空间足够与否**，都会**回收**它的内存。不过，由于垃圾回收器是一个**优先级很低的线程**，因此**不一定**会**很快**发现那些只具有**弱引用**的对象。
- **虚引用**：顾名思义，就是**形同虚设**。与其他几种引用都不同，**虚引用**并**不会**决定对象的**生命周期**。如果一个对象**仅持有虚引用**，那么它就和**没有任何引用**一样，在任何时候都可能被垃圾回收器回收。

| 引用类型 | 被垃圾回收时间 | 用途               | 生存时间          |
| -------- | -------------- | ------------------ | ----------------- |
| 强引用   | 从来不会       | 对象的一般状态     | JVM停止运行时终止 |
| 软引用   | 当内存不足时   | 对象缓存           | 内存不足时终止    |
| 弱引用   | 正常垃圾回收时 | 对象缓存           | 垃圾回收后终止    |
| 虚引用   | 正常垃圾回收时 | 跟踪对象的垃圾回收 | 垃圾回收后终止    |

**弱引用代码示例：**
```java
public class WeakReferenceTest {
    public static void main(String[] args) {
        Object test = new Object();
        // 弱引用对象封装test
        WeakReference<Object> weakReference = new WeakReference<>(test);

        // test和弱引用指向同一个对象
        System.out.println(test);
        System.out.println(weakReference.get());

        // 将强引用angela置为null，这个对象就只剩下弱引用了,内存够用，弱引用也会被回收
        test = null;
        System.gc();// 内存够用不会自动gc，这里手动调用gc
        System.out.println(test);
        System.out.println(weakReference.get());
    }
}
```
输出结果：
```
java.lang.Object@2d3fcdbd
java.lang.Object@2d3fcdbd
null
null
```
可以看到一旦一个对象只被弱引用引用，GC的时候就会回收这个对象。

### 3. 为何ThreadlocalMap 中key是弱引用类型（防止内存泄漏的解决方案）
#### 3.1 key使用弱类型的原因
**<font color="red">为了尽最大努力避免内存泄漏。</font>**  

之所以将`key`设计成弱引用，是为了更好地对`ThreadLocal`进行回收：  
当在代码中将`ThreadLocal`对象的强引用置为`null`后，这时候`Entry`中的`ThreadLocal`理应被回收了，但是如果`Entry`的`key`也被设置成**强引用**的话，则该`ThreadLocal`就不能被回收，这就是将其设置成弱引用的目的。

在`ThreadLocalMap`中，只有`ThreadLocal<?> k`是弱引用，`value`仍然是一个强引用：
```java
/**
 * ThreadLocalMap is a customized hash map suitable only for
 * maintaining thread local values. No operations are exported
 * outside of the ThreadLocal class. The class is package private to
 * allow declaration of fields in class Thread.  To help deal with
 * very large and long-lived usages, the hash table entries use
 * WeakReferences for keys. However, since reference queues are not
 * used, stale entries are guaranteed to be removed only when
 * the table starts running out of space.
 *
 * ThreadLocalMap 是一个定制的哈希映射，仅适用于维护线程本地值。
 * 不会在 ThreadLocal 类之外导出任何操作。该类是包私有的，以允许在类 Thread 中声明字段。
 * 为了帮助处理非常大且长期存在的使用，哈希表条目使用 WeakReferences 作为键。
 * 但是，由于不使用引用队列，因此只有在表开始空间不足时才能保证删除过时的条目。
 */
public class ThreadLocal<T> {
    static class ThreadLocalMap {
        // 
        static class Entry extends WeakReference<ThreadLocal<?>> {
            Object value;
            Entry(ThreadLocal<?> k, Object v) {
                super(k);
                value = v;
            }
        }
        // .............   	
    }
    // ............. 
}
```

#### 3.2 内存泄漏产生原因
下图描述了`ThreadLocal`和`Thread`以及`ThreadLocalMap`三者的关系：  
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocal和Thread以及ThreadLocalMap三者的关系.png)
</center>

代码解释，如：
```
ThreadLocal<UserInfo> userInfoThreadLocal = new ThreadLocal<>();
userInfoThreadLocal.set(userInfo);
```
对照上图，这里的引用关系是`userInfoThreadLocal引用`指向了堆中的`ThreadLocal`对象，这是个强引用；`ThreadLocal`对象同时也被`ThreadlocalMap`的`key`引用，**这是个`WeakReference`引用**；  
前面说`GC`要回收`ThreadLocal`对象的前提是它只被`WeakReference`引用，没有任何强引用。

只要`ThreadLocal`对象如果还被 `userInfoThreadLocal引用`（强引用） 引用着，GC是不会回收被`WeakReference`引用的对象（`key`）的 。

**所以当某一条线程中的`ThreadLocal`使用完毕，没有强引用指向它的时候，这个`key`指向的对象就会被垃圾收集器回收，从而这个`key`就变成了`null`；然而，此时`value`和`value`指向的对象之间仍然是强引用关系，只要这种关系不解除，`value`指向的对象永远不会被垃圾收集器回收，从而导致内存泄漏！**

场景演示：
```java
public class WeakReferenceTest {
    public static void main(String[] args) throws InterruptedException {
        ThreadLocal<Long[]> threadLocalTest = new ThreadLocal<>();
        for (int i = 0; i < 50; i++) {
            run(threadLocalTest);
        }
        Thread.sleep(30000);
        // 去除threadLocalTest的强引用
        threadLocalTest = null;
        System.out.println("开始执行gc");
        System.gc();
        System.runFinalization();
        System.gc();
    }

    private static void run(ThreadLocal<Long[]> threadLocal) {
        new Thread(() -> {
            threadLocal.set(new Long[1024 * 1024 * 10]);
            try {
                Thread.sleep(1000000000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
    }
}
```
通过`jdk`自带的工具`jconsole.exe`会发现即使执行了`gc`内存也不会减少，因为key还被线程强引用着。

**效果图如下：**  
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/弱引用清空监控.png)
</center>

#### 3.3 ThreadLocal提供的解决方案
`ThreadLocal`在每次操作`set()`、`get()`、`remove()`方法时，都会将`key`为`null`的`Entry`清除，从而避免内存泄漏。
 
> 过期key的清除逻辑详见**补充1：ThreadLocalMap-->过期key的“探测式清理”和“启发式清理”**

那么问题又来了，如果一个**线程运行周期较长**，而且将一个**大对象**放入LocalThreadMap后便不再调用`set()`、`get()`、`remove()`方法，此时该仍然可能会导致**内存泄漏**。

这个问题确实存在，并且没办法通过`ThreadLocal`解决，而是需要程序员在完成`ThreadLocal`的使用后要养成手动调用`remove`的习惯，从而避免**内存泄漏**。

<font color="red">注意：只是尽可能的，并不是直接避免了**内存泄漏**！！！</font>

#### 3.4 小结
其实在实际生产环境中手动`remove`大多数情况并不是为了避免这种`key`为`null`的情况；更多的时候是为了保证业务以及程序的正确性。

比如：下单请求后通过`ThreadLocal`构建了订单的上下文请求信息，然后通过线程池异步去更新用户积分等操作，这时候如果更新完成，没有进行`remove`操作，即使下一次新的订单会覆盖原来的值但是也是有可能会导致业务问题。 

**补充1：** 如果不想手动清理是否还有其他方式解决方案？ `FastThreadLocal` 可以去了解下，它提供了自动回收机制。

**补充2：** 在线程池的场景，程序不停止，线程一直在复用的话，基本不会销毁，其实本质就跟上面例子是一样的。  
如果线程不被复用，用完就销毁了就不会存在泄露的情况。因为线程结束的时候`jvm`会主动调用`java.lang.Thread.exit()`方法清理：
```java
public class Thread implements Runnable {
    // .........
    
	/**
     * This method is called by the system to give a Thread
     * a chance to clean up before it actually exits.
     * 系统调用此方法使线程有机会在实际退出之前进行清理
     */
    private void exit() {
        if (group != null) {
            group.threadTerminated(this);
            group = null;
        }
        /* Aggressively null out all reference fields: see bug 4006245 */
        target = null;
        /* Speed the release of some of these resources */
        threadLocals = null;
        inheritableThreadLocals = null;
        inheritedAccessControlContext = null;
        blocker = null;
        uncaughtExceptionHandler = null;
    }
    
	//.......
}
```

## 六、ThreadLocal和Synchronized比较
`ThreadLocal`是解决线程安全问题一个很好的思路，它通过为每个线程提供一个独立的变量副本解决了变量并发访问的冲突问题；  
在很多情况下，`ThreadLocal`比直接使用`synchronized`同步机制解决线程安全问题更简单，更方便，且结果程序拥有更高的并发性。

`ThreadLocal`和`Synchronized`都是为了解决多线程中相同变量的访问冲突问题，不同的点是：
- **`Synchronized`用于线程间的数据共享：** 是通过线程等待，**牺牲时间来解决访问冲突**；
  在同步机制中，通过对象的锁机制保证同一时间只有一个线程访问变量。这时该变量是多个线程共享的，使用同步机制要求程序慎密地分析什么时候对变量进行读写，什么时候需要锁定某个对象，什么时候释放对象锁等繁杂的问题，程序设计和编写难度相对较大。
- **`ThreadLocal`用于线程间的数据隔离：** 是通过每个线程单独一份存储空间，**牺牲空间来解决冲突；**
  相比于`Synchronized`，`ThreadLocal`具有线程隔离的效果，只有在线程内才能获取到对应的值，线程外则不能访问到想要的值，在编写多线程代码时，可以把不安全的变量封装进`ThreadLocal`。

**概括起来说，对于多线程资源共享的问题，`Synchronized`同步机制采用了 “以时间换空间” 的方式，而`ThreadLocal`采用了 “以空间换时间” 的方式。前者仅提供一份变量，让不同的线程排队访问，而后者为每一个线程都提供了一份变量，因此可以同时访问而互不影响。**

**补充：**`Spring`使用`ThreadLocal`解决线程安全问题：  
在一般情况下，只有无状态的`Bean`才可以在多线程环境下共享，而在`Spring`中，绝大部分`Bean`都可以声明为`singleton(见说明)`作用域。就是因为Spring对一些Bean（如：`RequestContextHolder`、`TransactionSynchronizationManager`、`LocaleContextHolder`等）中非线程安全状态采用ThreadLocal进行处理（也是ThreadLocal的应用场景），让它们也成为线程安全的状态，因为有状态的Bean就可以在多线程中共享了。

> **singleton作用域说明：**
>
> 当一个bean的作用域设置为singleton，那么Spring IOC容器中只会存在一个共享的bean实例，并且所有对bean的请求，只要id与该bean定义相匹配，则只会返回bean的同一实例。
> 这个单一实例会被存储到**单例缓存（singleton cache）**中，并且所有针对该bean的后续请求和引用都将返回被缓存的对象实例；
>
>**要注意的是singleton作用域和GOF设计模式中的单例模式是完全不同的：**  
> 单例设计模式表示一个`ClassLoader`中只有一个`class`存在，而这里的`singleton`则表示一个容器对应一个`bean`，也就是说当一个`bean`被标识为`singleton`时候，`spring`的`IOC`容器中只会存在一个该`bean`。 

## 补充1：ThreadLocalMap
**<font color="red">对于`ThreadLocal`来说关键就是内部的`ThreadLocalMap`。</font>**

### 1. 构造方法和静态内部类Entry
数据结构如下图：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/静态内部类Entry结构图.png)
</center>

`ThreadLocalMap`有点类似`HashMap`的结构，只是`HashMap`是由 **数组+链表（+红黑树）** 实现的，而`ThreadLocalMap`中并没有 **链表（+红黑树）** 结构。
```java
//Entry为ThreadLocalMap静态内部类，对ThreadLocal的若引用
//同时让ThreadLocal和储值形成key-value的关系
static class Entry extends WeakReference<ThreadLocal<?>> {
    /** The value associated with this ThreadLocal. */
    Object value;

    Entry(ThreadLocal<?> k, Object v) {
        super(k);
        value = v;
    }
}
/**
 * The initial capacity -- MUST be a power of two.
 * 初始容量 -- 必须是 2 的幂。
 */
private static final int INITIAL_CAPACITY = 16;

//ThreadLocalMap构造方法
ThreadLocalMap(ThreadLocal<?> firstKey, Object firstValue) {
    //内部成员数组，INITIAL_CAPACITY值为16的常量
    table = new Entry[INITIAL_CAPACITY];
    //位运算，结果与取模相同，计算出需要存放的位置
    int i = firstKey.threadLocalHashCode & (INITIAL_CAPACITY - 1);
    table[i] = new Entry(firstKey, firstValue);
    size = 1;
    setThreshold(INITIAL_CAPACITY);
}
```
通过上面的代码看出在实例化`ThreadLocalMap`时创建了一个长度为16的`Entry`数组。**通过`hashCode`与`length`位运算确定出一个索引值`i`，这个`i`就是被存储在`table`数组中的位置。**

每个线程`Thread`持有一个`ThreadLocalMap`类型的实例`threadLocals`；  
结合此处的构造方法可以理解成每个线程`Thread`都持有一个`Entry`型的数组`table`，用`Entry`数组来存储键值对，`key`是`ThreadLocal`对象，`value`则是具体的值，而一切的读取过程都是通过操作这个数组`table`完成的。

**注意：`INITIAL_CAPACITY`变量必须为2的等指数次幂是为了计算索引值`i`时使用位运行算能更快的hash运算（和HashMap类似）**

### 2. set()方法
#### 2.1 set()方法的hash算法
**先看下面这段代码：**
```java
//在某一线程声明了ABC三种类型的ThreadLocal
ThreadLocal<A> sThreadLocalA = new ThreadLocal<A>();
ThreadLocal<B> sThreadLocalB = new ThreadLocal<B>();
ThreadLocal<C> sThreadLocalC = new ThreadLocal<C>();
```
对于一个`Thread`来说只有持有一个`ThreadLocalMap`，所以 **ABC** 被同一个线程持有，即 对应同一个`ThreadLocalMap`对象。为了管理 **ABC** ，于是将他们存储在一个数组的不同位置，而这个数组就是上面提到的`Entry`型的数组`table`。

那么`ABC`在`table`中的位置是如何确定的？源码如下：
```java
//ThreadLocalMap中set方法。
private void set(ThreadLocal<?> key, Object value) {
    Entry[] tab = table;
    int len = tab.length;
    //获取索引值，这个地方是比较特别的地方
    int i = key.threadLocalHashCode & (len-1);

    //遍历tab如果已经存在则更新值
    for (Entry e = tab[i];
         e != null;
         e = tab[i = nextIndex(i, len)]) {
        ThreadLocal<?> k = e.get();

        if (k == key) {
            e.value = value;
            return;
        }

        if (k == null) {
            replaceStaleEntry(key, value, i);
            return;
        }
    }

    //如果上面没有遍历成功则创建新值
    tab[i] = new Entry(key, value);
    int sz = ++size;
    //满足条件数组扩容x2
    if (!cleanSomeSlots(i, sz) && sz >= threshold)
        rehash();
}
```
在`ThreadLocalMap`中的`set`方法与构造方法能看到以下代码片段。
- set方法中：`int i = key.threadLocalHashCode & (len-1)`
- 构造函数中：`int i = firstKey.threadLocalHashCode & (INITIAL_CAPACITY - 1)`

简而言之就是将`threadLocalHashCode`进行一个位运算（取模）得到索引`i`。  
`threadLocalHashCode`源码如下：
```java
// ThreadLocal中threadLocalHashCode相关代码.
private final int threadLocalHashCode = nextHashCode();
/**
 * The next hash code to be given out. Updated atomically. Starts at
 * zero.
 * 要给出的下一个哈希码。原子更新。从零开始。
 */
private static AtomicInteger nextHashCode =
    new AtomicInteger();

/**
 * The difference between successively generated hash codes - turns
 * implicit sequential thread-local IDs into near-optimally spread
 * multiplicative hash values for power-of-two-sized tables.
 * 连续生成的哈希码之间的差异 - 将隐式顺序线程本地 ID 转换为接近最优分布的乘法哈希值，用于 2 次方大小的表。
 */
private static final int HASH_INCREMENT = 0x61c88647;

/**
 * Returns the next hash code.
 */
private static int nextHashCode() {
    //线程安全的自增 （nextHashCode是一个AtomicInteger原子类）
    return nextHashCode.getAndAdd(HASH_INCREMENT);
}
```
因为 **static** 的原因，在每次`new ThreadLocal`时因为`threadLocalHashCode`的初始化，会使`threadLocalHashCode`值自增一次，**增量为0x61c88647**（即：每当创建一个`ThreadLocal`对象，这个`ThreadLocal.nextHashCode` 这个值就会增长 **`0x61c88647`** ）。

这个值很特殊，它是**斐波那契数** 也叫 **黄金分割数**。`hash`增量为 这个数字，它的优点是通过它散列(hash)出来的结果分布会**比较均匀**，可以很大程度上避免hash冲突，已初始容量16为例：
```java
public class ThreadLocalTest {
    private static final int HASH_INCREMENT = 0x61c88647;

    public static void main(String[] args) {
        int hashcode = 0;
        for (int i = 0; i < 16; i++) {
            hashcode = i * HASH_INCREMENT + HASH_INCREMENT;
            int bucket = hashcode & 15;
            System.out.println(i + "对应的hashcode：" + Integer.toHexString(hashcode) + "，在桶中的位置：" + bucket);
        }
    }
}
```
执行结果：
```
0对应的hashcode：61c88647，在桶中的位置：7
1对应的hashcode：c3910c8e，在桶中的位置：14
2对应的hashcode：255992d5，在桶中的位置：5
3对应的hashcode：8722191c，在桶中的位置：12
4对应的hashcode：e8ea9f63，在桶中的位置：3
5对应的hashcode：4ab325aa，在桶中的位置：10
6对应的hashcode：ac7babf1，在桶中的位置：1
7对应的hashcode：e443238，在桶中的位置：8
8对应的hashcode：700cb87f，在桶中的位置：15
9对应的hashcode：d1d53ec6，在桶中的位置：6
10对应的hashcode：339dc50d，在桶中的位置：13
11对应的hashcode：95664b54，在桶中的位置：4
12对应的hashcode：f72ed19b，在桶中的位置：11
13对应的hashcode：58f757e2，在桶中的位置：2
14对应的hashcode：babfde29，在桶中的位置：9
15对应的hashcode：1c886470，在桶中的位置：0
```
可以看出每个值分布在桶的位置相对均匀，这样能有效的减少**hash冲突**。  

**小结：**
1. 对于某一`ThreadLocal`来讲，他的索引值`i`是确定的，在不同线程之间访问时访问的是不同的`table数组`的同一位置即都为`table[i]`，只不过这个不同线程之间的`table`是独立的；
2. 对于同一线程的不同`ThreadLocal`来讲，这些`ThreadLocal`实例共享一个`table数组`，然后每个`ThreadLocal`实例在`table`中的索引`i`是不同的。

#### 2.2 set()方法如何处理hash冲突
虽然`ThreadLocalMap`中使用了**黄金分隔数**来作为`hash`计算因子，大大减少了`Hash`冲突的概率，但是仍然会存在冲突。

在`HashMap`中解决冲突的方法是在数组上构造一个**链表**结构，冲突的数据挂载到链表上，如果链表长度超过一定数量则会转化成**红黑树**。

而`ThreadLocalMap`中并没有链表和红黑树结构，所以这里不能适用`HashMap`解决冲突的方式了。

> 注明： 下面所有示例图中，绿色块`Entry`代表正常数据，灰色块代表`Entry`的`key`值为`null`，已被垃圾回收。白色块表示`Entry`为`null`。

<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的hash冲突处理演示.png)
</center>

如上图所示，如果插入一个`value=27`的数据，通过`hash`计算后应该落入第4个槽位中，而槽位4已经有了`Entry`数据。  
此时就会线性向后查找，一直找到`Entry`为`null`的槽位才会停止查找，将当前元素放入此槽位中。当然迭代过程中还有其他的情况，比如遇到了`Entry`不为`null`且`key`值相等的情况，还有`Entry`中的`key`值为`null`的情况等等都会有不同的处理，见后文。

注：这里还画了一个`Entry`中的`key`为`null`的数据（**Entry=2的灰色块数据**），因为`key`值是**弱引用**类型，所以会有这种数据存在。在`set`过程中，如果遇到了`key`过期的`Entry`数据，实际上是会进行一轮**探测式清理**操作的，具体操作方式后面会讲到。

#### 2.3 不同情况下的set()插入逻辑（步骤）
往`ThreadLocalMap`中`set`数据（**新增**或者**更新**数据）分为好几种情况，针对不同的情况画图说明：

##### 第一种情况：`hash`计算后的槽位对应的`Entry`数据为空：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况1：hash计算后的槽位对应的Entry数据为空.png)
</center>
这里直接将数据放到该槽位即可。

##### 第二种情况：槽位数据不为空，`key`值与当前`ThreadLocal`通过`hash`计算获取的`key`一致（同一个线程）：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况2：槽位数据不为空，key值与当前ThreadLocal通过hash计算获取的key一致（同一个线程）.png)
</center>

这里直接更新该槽位的数据。
##### 第三种情况：槽位数据不为空，往后遍历过程中，在找到`Entry`为`null`的槽位之前，未遇到`key`过期的`Entry`：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况3：槽位数据不为空，往后遍历过程中，在找到Entry为null的槽位之前，未遇到key过期的Entry.png)
</center>

遍历散列数组，线性往后查找，如果找到`Entry`为`null`的槽位，则将数据放入该槽位中，或者往后遍历过程中，遇到了**key值相等（同一线程)**的数据，直接更新即可。

##### 第四种情况：槽位数据不为空，往后遍历过程中，在找到`Entry`为`null`的槽位之前，遇到`key`过期的`Entry`：

如下图，往后遍历过程中，到了`index=7`的槽位数据`Entry`的`key=null`：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况4：槽位数据不为空，往后遍历过程中，在找到Entry为null的槽位之前，未遇到key过期的Entry.png)
</center>

**第一步：** 初始化探测式清理过期数据扫描的开始位置：`slotToExpunge = staleSlot = 7`

散列数组下标为7位置对应的`Entry`数据`key`为`null`，表明此数据`key`值已经被垃圾回收掉了，此时就会执行`replaceStaleEntry()`方法，该方法是 **用于替换过期数据**，以 **index=7** 位起点开始遍历，进行探测式数据清理工作。

**第二步：** 以当前`staleSlot`（**staleSlot=index=7**）开始 向前迭代查找，找其他过期的数据，然后更新过期数据的下标为起始扫描下标`slotToExpunge`。`for`循环迭代，直到碰到`Entry`为`null`槽位才停止迭代。

如下图所示，**slotToExpunge最终被更新为0**：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况4：第二步.png)
</center>

上面向前迭代的操作是为了更新探测清理过期数据的起始下标`slotToExpunge`的值，这个值在后面会讲解，它是用来判断当前过期槽位`staleSlot`之前是否还有过期元素。

**第三步（情况1）：** 接着开始以`staleSlot`位置(`index=7`)向后迭代，如果找到了相同`key`值的`Entry`数据，更新`Entry`的值并交换`staleSlot`元素的位置(**staleSlot位置为过期元素**)，更新`Entry`数据，如下图：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况4：第三步1.png)
</center>

**第四步（情况1）：** 然后开始进行过期`Entry`的清理工作，如下图所示：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况4：第四步1.png)
</center>

**第三步（情况2）：向后遍历过程中，如果没有找到相同key值的Entry数据：**
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况4：第三步2.png)
</center>

从当前节点`staleSlot`向后查找`key`值相等的`Entry`元素，直到`Entry`为`null`则停止寻找。通过上图可知，此时`table`中没有`key`值相同的`Entry`。

**第四步（情况2）：** 创建新的`Entry`，替换`table[stableSlot]`位置：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的set()插入逻辑情况4：第四步2.png)
</center>

替换完成后也是进行过期元素清理工作，清理工作主要是有两个方法：`expungeStaleEntry()`和`cleanSomeSlots()`，具体细节后面会讲到，请继续往后看。

#### 2.4 ThreadLocalMap.set()源码详解
`java.lang.ThreadLocal.ThreadLocalMap.set()`:
```java
private void set(ThreadLocal<?> key, Object value) {
    Entry[] tab = table;
    int len = tab.length;
    int i = key.threadLocalHashCode & (len-1);
    for (Entry e = tab[i];
         e != null;
         e = tab[i = nextIndex(i, len)]) {
        ThreadLocal<?> k = e.get();

        if (k == key) {
            e.value = value;
            return;
        }

        if (k == null) {
            replaceStaleEntry(key, value, i);
            return;
        }
    }

    tab[i] = new Entry(key, value);
    int sz = ++size;
    if (!cleanSomeSlots(i, sz) && sz >= threshold)
        rehash();
}
```

```java
// 这里会通过key来计算在散列表中的对应位置，
// 然后以当前key对应的桶的位置向后查找(nextIndex方法)，找到可以使用的桶。
Entry[] tab = table;
int len = tab.length;
int i = key.threadLocalHashCode & (len-1);
```
什么情况下桶才是可以使用的呢？
1. `k = key` 说明是替换操作，可以使用；
2. 碰到一个过期的桶，执行替换逻辑，占用过期桶；
3. 查找过程中，碰到桶中`Entry=null`的情况，直接使用。

接着就是执行`for`循环遍历，向后查找，先看下`nextIndex()`、`prevIndex()`方法实现：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的nextIndex()和prevIndex()方法实现.png)
</center>

```java
private static int nextIndex(int i, int len) {
    return ((i + 1 < len) ? i + 1 : 0);
}

private static int prevIndex(int i, int len) {
    return ((i - 1 >= 0) ? i - 1 : len - 1);
}
```

接着看for循环中剩下的逻辑：
```java
for (Entry e = tab[i];
     e != null;// 1. 遍历当前key值对应的桶，且桶不能为空，
     e = tab[i = nextIndex(i, len)]) {// 2. 如果key值对应的桶中Entry数据不为空，调用nextIndex()方法往后遍历
    ThreadLocal<?> k = e.get();

    // 2.1 如果k = key，说明当前set操作是一个替换操作，做替换逻辑，直接返回
    if (k == key) {
        e.value = value;
        return;
    }
	// 2.2 如果key = null，说明当前桶位置的Entry是过期数据，执行replaceStaleEntry()方法替换掉过期的值，然后返回
    if (k == null) {
        replaceStaleEntry(key, value, i);
        return;
    }
}
// 3. for循环的判断条件中 e != null 不成立，跳出for循环，直接set数据到对应的桶中
tab[i] = new Entry(key, value);
int sz = ++size;
// 4. set之后，判断当前容量size是否大于当前map容量的阈值threshold（即当前容量的2/3，threshold的赋值见setThreshold()方法）
if (!cleanSomeSlots(i, sz) && sz >= threshold)
    // 4.1 超过阈值，执行“假扩容”-->先执行expungeStaleEntries()方法清理一次数组，再执行“真扩容”的resize()方法
    rehash();
```
**详细步骤如下：**
1. 遍历当前`key`值对应的桶，桶中的`Entry`数据如果为空，这说明散列数组这里没有数据冲突，跳出`for`循环，直接`set`数据到对应的桶中
2. 如果`key`值对应的桶中`Entry`数据不为空
   * 如果`k = key`，说明当前set操作是一个替换操作，做替换逻辑，直接返回
   * 如果`key = null`，说明当前桶位置的`Entry`是过期数据，执行`replaceStaleEntry()`方法**（核心方法）**，然后返回
3. for循环执行完毕，继续往下执行说明向后迭代的过程中遇到了`entry`为`null`的情况
   * 在`Entry`为`null`的桶中创建一个新的Entry对象
   * 执行`++size`操作
4. 调用`cleanSomeSlots()`做一次**启发式清理工作**，清理散列数组中`Entry`的`key`过期的数据
   * 如果清理工作完成后，未清理到任何数据，且`size`超过了阈值**（数组长度的2/3）**，进行`rehash()`操作
   * `rehash()`中会先进行一轮**探测式清理`expungeStaleEntries()`**，清理过期`key`，清理完成后如果`size >= threshold - threshold / 4`，就会执行真正的扩容逻辑`resize()`;（扩容逻辑参考后文）

接着重点看下`replaceStaleEntry()`方法，`replaceStaleEntry()`方法提供替换过期数据的功能，对应上面**第四种情况**的原理图来看，具体代码如下：  
`java.lang.ThreadLocal.ThreadLocalMap.replaceStaleEntry()`:
```java
private void replaceStaleEntry(ThreadLocal<?> key, Object value,
                                       int staleSlot) {
    Entry[] tab = table;
    int len = tab.length;
    Entry e;
    
	// 1. slotToExpunge表示开始探测式清理过期数据的开始下标，默认从当前的staleSlot开始
    int slotToExpunge = staleSlot;
    // 以当前的staleSlot开始，向前(prevIndex)迭代查找
    for (int i = prevIndex(staleSlot, len);
         (e = tab[i]) != null;// 碰到`Entry`为`null`才会结束
         i = prevIndex(i, len))
		// 2. 如果向前找到了过期数据，更新探测清理过期数据的开始下标为i，即`slotToExpunge=i`
        if (e.get() == null)
            slotToExpunge = i;

    // 3. 接着开始从`staleSlot`向后查找(nextIndex)
    for (int i = nextIndex(staleSlot, len);
         (e = tab[i]) != null;// 也是碰到`Entry`为`null`的桶结束。
         i = nextIndex(i, len)) {

        ThreadLocal<?> k = e.get();
		// 4. 如果迭代过程中遇到k == key，这说明这里是替换逻辑，替换新数据并交换当前`staleSlot`位置。
        if (k == key) {
            e.value = value;

            tab[i] = tab[staleSlot];
            tab[staleSlot] = e;
			// 4.1 如果`slotToExpunge ==staleSlot`，说明`replaceStaleEntry()`一开始向前查找过期数据时并未找到过期的`Entry`数据，接着向后查找过程中也未发现过期数据，修改开始探测式清理过期数据的下标为当前循环的`key`对应的下标`index`，即`slotToExpunge = i`
            if (slotToExpunge == staleSlot)
                // 将当前key对应的下标复制给slotToExpunge
                slotToExpunge = i;
            // 4.2 最后调用`cleanSomeSlots(expungeStaleEntry(slotToExpunge), len);`进行启发式过期数据清理，结束当前替换过期数据的逻辑
            cleanSomeSlots(expungeStaleEntry(slotToExpunge), len);
            return;
        }

        // 5. 如果k != key，则开始判断当前key是否对应一个过期数据（k == null），且`slotToExpunge == staleSlot`（说明，一开始的向前查找数据并未找到过期的`Entry`）
        if (k == null && slotToExpunge == staleSlot)
            // 更新`slotToExpunge` 为当前位置
            slotToExpunge = i;
    }

    // 6. 往后迭代的过程中如果没有找到`k == key`的数据，且碰到`Entry`为`null`的数据，则结束当前的迭代操作。
    // 此时说明这里是一个添加的逻辑，将新的数据添加到`table[staleSlot]` 对应的`slot`中。
    tab[staleSlot].value = null;
    tab[staleSlot] = new Entry(key, value);

    // 7. 最后判断除了`staleSlot`以外，还发现了其他过期的`slot`数据，就要开启清理数据的逻辑：
    if (slotToExpunge != staleSlot)
        cleanSomeSlots(expungeStaleEntry(slotToExpunge), len);
}
```
**详细步骤如下：**
1. `slotToExpunge`表示开始探测式清理过期数据的开始下标，默认从当前的`staleSlot`开始。以当前的`staleSlot`开始，向前迭代查找（`for`循环一直碰到`Entry`为`null`才会结束）；
2. 如果向前找到了过期数据`if (e.get() == null)`，更新探测清理过期数据的开始下标为i，即`slotToExpunge=i`；
3. 接着开始从`staleSlot`向后查找，也是碰到`Entry`为`null`的桶结束；
4. 如果迭代过程中，**碰到k == key**，这说明这里是替换逻辑，替换新数据并交换当前`staleSlot`位置；
   * 如果`slotToExpunge ==staleSlot`，说明`replaceStaleEntry()`一开始向前查找过期数据时并未找到过期的`Entry`数据，
   接着向后查找过程中也未发现过期数据，修改开始探测式清理过期数据的下标为当前循环的`key`对应的下标`index`，即`slotToExpunge = i`
   * 最后调用`cleanSomeSlots(expungeStaleEntry(slotToExpunge), len);`，进行启发式过期数据清理。
   > `cleanSomeSlots()`和`expungeStaleEntry()`方法后面都会细讲，这两个都是和清理相关的方法：  
   一个是过期`key`相关`Entry`的启发式清理(`Heuristically scan`)；  
   另一个是过期`key`相关`Entry`的探测式清理。
5. **如果k != key**则会接着往下走，`k == null`说明当前遍历的`Entry`是一个过期数据，`slotToExpunge == staleSlot`说明，一开始的向前查找数据并未找到过期的`Entry`。如果条件成立，则更新`slotToExpunge` 为当前位置（这个前提是前驱节点扫描时未发现过期数据）
6. 往后迭代的过程中如果没有找到`k == key`的数据，且碰到`Entry`为`null`的数据，则结束当前的迭代操作。  
此时说明这里是一个添加的逻辑，将新的数据添加到`table[staleSlot]` 对应的`slot`中。
7. 最后判断除了`staleSlot`以外，还发现了其他过期的`slot`数据，就要开启清理数据的逻辑。

#### 2.5 ThreadLocalMap过期key的“探测式清理”和“启发式清理”

`ThreadLocalMap`的有两种过期`key`数据清理方式：**探测式清理**和**启发式清理**。

##### 探测式清理——expungeStaleEntry()
遍历散列数组，从开始位置向后探测清理过期数据，将过期数据的`Entry`设置为`null`，沿途中碰到未过期的数据则将此数据`rehash()`后重新在`table`数组中定位，如果定位的位置已经有了数据，则会将未过期的数据放到最靠近此位置的`Entry=null`的桶中，使`rehash`后的`Entry`数据距离正确的桶的位置更近一些。  

操作逻辑如下：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的探测式清理expungeStaleEntry()2.png)
</center>

如上图，`set(27)` 经过hash计算后应该落到`index=4`的桶中，由于`index=4`桶已经有了数据，所以往后迭代最终数据放入到`index=7`的桶中，放入后一段时间后`index=5`中的`Entry`数据`key`变为了`null`；

<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的探测式清理expungeStaleEntry()1.png)
</center>

如果再有其他数据`set`到`map`中，就会触发**探测式清理**操作。

如上图，执行**探测式清理**后，`index=5`的数据被清理掉，继续往后迭代，到`index=7`的元素时，经过`rehash`后发现该元素正确的`index=4`，而此位置已经已经有了数据，往后查找离`index=4`最近的`Entry=null`的节点 **（刚被探测式清理掉的数据：index=5）**，找到后移动`index= 7`的数据到`index=5`中；此时桶的位置离正确的位置`index=4`更近了。

**经过一轮探测式清理后，`key`过期的数据会被清理掉，没过期的数据经过`rehash`重定位后所处的桶位置理论上更接近`i= key.hashCode & (tab.len - 1)`的位置。这种优化会提高整个散列表查询性能。**

**源码分析：**
```java
private int expungeStaleEntry(int staleSlot) {
    Entry[] tab = table;
    int len = tab.length;
	// 1. 清空当前staleSlot位置的数据，index=3位置的Entry变成了null。
    tab[staleSlot].value = null;
    tab[staleSlot] = null;
    size--;

    Entry e;
    int i;
    // 2. 接着以staleSlot位置往后迭代
    for (i = nextIndex(staleSlot, len);
         (e = tab[i]) != null;
         i = nextIndex(i, len)) {
        ThreadLocal<?> k = e.get();
        // 2.1 如果遇到k==null的过期数据
        if (k == null) {
            // 清空该槽位数据，然后size--
            e.value = null;
            tab[i] = null;
            size--;
        } else {
            // 2.2 如果key没有过期，重新计算当前key的下标位置
            int h = k.threadLocalHashCode & (len - 1);
            // 2.2.1 当前重新计算的下标不是当前槽位的下标，产生了hash冲突
            if (h != i) {
                tab[i] = null;
				// 2.2.2 此时以新计算出来正确的槽位位置往后迭代，直到找到最近一个可以存放entry的位置（即entry为空的位置）。
                while (tab[h] != null)
                    h = nextIndex(h, len);
                tab[h] = e;
            }
        }
    }
    return i;
}
```
**详细步骤如下：**
1. 首先是将`tab[staleSlot]`槽位的数据清空，然后设置`size--`
2. 接着以`staleSlot`位置往后迭代，
   * 如果遇到`k==null`的过期数据，也是清空该槽位数据，然后`size--`；
   * 如果`key`没有过期，重新计算当前`key`的下标位置是不是当前槽位下标位置，
     * 如果不是，那么说明产生了`hash`冲突，此时以新计算出来正确的槽位位置往后迭代；
     * 直到找到最近一个可以存放`entry`的位置。

##### 启发式清理——cleanSomeSlots()
源码如下：
```java
/**
 * 主要作用：
 * 进行一定次数的循环，从当位置i开始往后寻找脏entry并清理掉，当清理脏entry时，使用expungeStaleEntry方法，
 * 从当前脏entry会再 往后寻找国企entry进行清理，碰到null时结束。
 * 
 * 可以看到这个清理的过程只是覆盖了一段范围（参数i往后的下标），并不是全部区间。
*/
private boolean cleanSomeSlots(int i, int n) {
    // 定义变量表示是否删除过entry元素
    boolean removed = false;
    Entry[] tab = table;
    int len = tab.length;
    do {
        // 1. 向后（nextIndex）迭代获取entry对象
        i = nextIndex(i, len);
        Entry e = tab[i];
        // 如果entry对象不为空且此引用对象已被程序或垃圾收集器清除为空
        if (e != null && e.get() == null) {
            n = len;
            // 设置是否删除元素的状态为true
            removed = true;
            // 2. 再调用探测式清理（expungeStaleEntry），将找出来的过期key对应的entry传递给expungeStaleEntry进行清空处理，下次GC操作的时候即会被清理掉
            i = expungeStaleEntry(i);
        }
    } while ( (n >>>= 1) != 0);
    // n >>>= 1 说明要循环log2N次。在没有发现过期Entry时，会一直往后找下个位置的entry是否是过期的，如果是的话，就会使 n = 数组的长度。然后继续循环log2新N 次。
    return removed;
}
```
**详细步骤如下：**
1. 向后（调用`nextIndex()`方法）迭代获取`entry`对象，如果`entry`对象不为空且此引用对象已被程序或垃圾收集器清除为空；
2. 再调用探测式清理（`expungeStaleEntry`），将找出来的过期`key`对应的`entry`传递给`expungeStaleEntry`进行清空处理，下次GC操作的时候即会被清理掉。

##### 探测式清理和启发式清理的触发时机和区别
* 探测式清理找到过期`key`的位置往后清理，遇到值为null则结束清理，属于线性探测清理。
* 而启发式清理则会循环 `log2 `的`n`次 ，如果遇到过期`key`，会进行 **探测式清理** ，继续循环`log2`的新n（遇到过期`key`会重新计算`n`）次。

### 3. getEntry()方法
**第一种情况：** 通过查找`key`值计算出散列表中`slot`位置，然后该`slot`位置中的`Entry.key`和查找的`key`一致，则直接返回：

<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的getEntry()方法情况1.png)
</center>

**第二种情况：** `slot`位置中的`Entry.key`和要查找的`key`不一致：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的getEntry()方法情况2.png)
</center>

以`get(ThreadLocal1)`为例，通过`hash`计算后，正确的`slot`位置应该是4，而`index=4`的槽位已经有了数据，且`key`值不等于`ThreadLocal1`，所以需要继续往后迭代查找。

迭代到`index=5`的数据时，此时`Entry.key=null`，触发一次探测式数据回收操作，执行`expungeStaleEntry()`方法，执行完后`5,8`的数据都会被回收，而`index 6,7`的数据都会前移，此时继续往后迭代，到`index = 6`的时候即找到了`key`值相等的`Entry`数据，如下图所示：

<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap的getEntry()方法情况2-1.png)
</center>

**源码分析：**
```java
private Entry getEntry(ThreadLocal<?> key) {
    // 1. 通过查找key值计算出散列表中的位置
    int i = key.threadLocalHashCode & (table.length - 1);
    Entry e = table[i];
    // 1.1 如果当前位置中的Entry.key和查找的key一致，则直接返回
    if (e != null && e.get() == key)
        return e;
    else
        // 1.2 如果当前位置中的Entry.key和要查找的key不一致，调用getEntryAfterMiss()方法
        return getEntryAfterMiss(key, i, e);
}
// 2. 调用getEntryAfterMiss()方法
private Entry getEntryAfterMiss(ThreadLocal<?> key, int i, Entry e) {
    Entry[] tab = table;
    int len = tab.length;
	// 2.1 如果当前key对应的entry不为空，则一直迭代
    while (e != null) {
        ThreadLocal<?> k = e.get();
        // 2.2 迭代到当前位置中的Entry.key和查找的key一致，则返回，结束
        if (k == key)
            return e;
        // 2.3 如果发现此时的key为空，触发一次探测式数据回收操作
        if (k == null)
            expungeStaleEntry(i);
        else// 2.4 key不为空，继续往后寻找
            i = nextIndex(i, len);
        e = tab[i];
    }
    // 3. 当前entry没有需要的table，返回空
    return null;
}
```
**详细步骤：**
1.  通过查找`key`值计算出散列表中的位置：
    * 如果当前位置中的`Entry.key`和查找的`key`一致，则直接返回
    * 如果当前位置中的`Entry.key`和要查找的`key`不一致，调用`getEntryAfterMiss()`方法
2.  调用`getEntryAfterMiss()`方法：
    * 如果当前key对应的`entry`不为空，则一直迭代：
      * 如果迭代到当前位置中的`Entry.key`和查找的key一致，则返回，**结束**
      * 如果发现此时的key为空，触发一次探测式数据回收操作，否则继续往后（`nextIndex`）寻找
3.  如果`entry`对象中未找到目标元素，返回`null`，**结束**。

### 4. 扩容
在`ThreadLocalMap.set()`方法的最后，如果执行完启发式清理工作后，未清理到任何数据，且当前散列数组中`Entry`的数量已经达到了列表的扩容阈值`(len*2/3)`，就开始执行`rehash()`逻辑：
```java
if (!cleanSomeSlots(i, sz) && sz >= threshold)
    rehash();
```

**rehash()具体实现：**
```java
private void rehash() {
    // 1. 调用expungeStaleEntry()方法，进行探测式清理
    expungeStaleEntries();
	
    // 2. 判断是否超过阈值
    if (size >= threshold - threshold / 4)
        // 3. 执行扩容
        resize();
}

private void expungeStaleEntries() {
    Entry[] tab = table;
    int len = tab.length;
    for (int j = 0; j < len; j++) {
        Entry e = tab[j];
        if (e != null && e.get() == null)
            expungeStaleEntry(j);
    }
}
```
**详细步骤：**
1. 首先是会进行 **探测式清理** 工作，从`table`的起始位置往后清理（上面有分析清理的详细流程）；
2. 清理完成之后，`table`中可能有一些key为`null`的`Entry`数据被清理掉，所以此时通过判断`size >= threshold - threshold / 4` 也就是`size >= threshold* 3/4` 来决定是否 **扩容**。

**上面进行`rehash()`的阈值是`size >= threshold`，所以当面试官套路`ThreadLocalMap`扩容机制的时候，一定要说清楚下图这两个步骤：**
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap扩容.png)
</center>

接着看看具体的`resize()`方法，为了方便演示，以`oldTab.len=8`来举例：
<center>

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）/ThreadLocalMap扩容示例.png)
</center>

**扩容** 后的`tab`的大小为`oldLen * 2`，然后遍历老的散列表，重新计算`hash`位置，然后放到新的`tab`数组中，如果出现`hash`冲突则往后寻找最近的`entry`为`null`的槽位，遍历完成之后，`oldTab`中所有的`entry`数据都已经放入到新的`tab`中了，最后重新计算`tab`下次扩容的**阈值**。  
具体代码如下：
```java
private void resize() {
    Entry[] oldTab = table;
    int oldLen = oldTab.length;
    int newLen = oldLen * 2;// 1. 创建一个新的Entry对象为老对象的两倍大小；
    Entry[] newTab = new Entry[newLen];
    int count = 0;
	
    // 2. 循环遍历老Entry对象，重新计算`hash`位置，然后将对应的值放到新的`tab`数组中；
    for (int j = 0; j < oldLen; ++j) {
        Entry e = oldTab[j];
        if (e != null) {
            ThreadLocal<?> k = e.get();
            if (k == null) {
                e.value = null;
            } else {
                // 3. 如果出现`hash`冲突则往后寻找最近的`entry`为`null`的槽位；
                int h = k.threadLocalHashCode & (newLen - 1);
                while (newTab[h] != null)
                    h = nextIndex(h, newLen);
                newTab[h] = e;
                count++;
            }
        }
    }
	// 4. 遍历完成之后，`oldTab`中所有的`entry`数据都已经放入到新的`tab`中了。重新计算`tab`下次扩容的**阈值**。
    setThreshold(newLen);
    size = count;
    table = newTab;
}
```
**详细步骤：**
1. 创建一个新的Entry对象为老对象的两倍大小；
2. 循环遍历老Entry对象，重新计算`hash`位置，然后将对应的值放到新的`tab`数组中；
3. 如果出现`hash`冲突则往后寻找最近的`entry`为`null`的槽位；
4. 遍历完成之后，`oldTab`中所有的`entry`数据都已经放入到新的`tab`中了。重新计算`tab`下次扩容的**阈值**。

## 补充2：父子线程的数据传递：
在使用`ThreadLocal`的时候，在异步场景下是无法给子线程共享父线程中创建的线程副本数据的。

为了解决这个问题，JDK中还有一个`InheritableThreadLocal`类，代码示例：
```java
public class InheritableThreadLocalDemo {
    public static void main(String[] args) {
        ThreadLocal<String> threadLocal = new ThreadLocal<>();
        ThreadLocal<String> inheritableThreadLocal = new InheritableThreadLocal<>();
        threadLocal.set("父类数据:threadLocal");
        inheritableThreadLocal.set("父类数据:inheritableThreadLocal");

        new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("子线程获取父类threadLocal数据：" + threadLocal.get());
                System.out.println("子线程获取父类inheritableThreadLocal数据：" + inheritableThreadLocal.get());
            }
        }).start();
    }
}
```
从执行结果可以看到子线程是拿不到父线程中的`ThreadLocal`的数据的：
```
子线程获取父类threadLocal数据：null
子线程获取父类inheritableThreadLocal数据：父类数据:inheritableThreadLocal
```

**`InheritableThreadLocal`实现原理：**  
子线程是通过在父线程中通过调用`new Thread()`方法来创建子线程，`Thread#init()`方法在`Thread`的构造方法中被调用。在`init`方法中拷贝父线程数据到子线程中:
```java
private void init(ThreadGroup g, Runnable target, String name,
                      long stackSize, AccessControlContext acc,
                      boolean inheritThreadLocals) {
    if (name == null) {
        throw new NullPointerException("name cannot be null");
    }

    if (inheritThreadLocals && parent.inheritableThreadLocals != null)
        this.inheritableThreadLocals =
            ThreadLocal.createInheritedMap(parent.inheritableThreadLocals);
    this.stackSize = stackSize;
    tid = nextThreadID();
}
```
但`InheritableThreadLocal`仍然有缺陷，一般做异步化处理都是使用的线程池，而`InheritableThreadLocal`是在`new Thread`中的`init()`方法给赋值的，而线程池是线程复用的逻辑，所以这里会存在问题（线程复用，后面的线程会沿用之前线程里面的数据）。

当然，有问题出现就会有解决问题的方案，阿里巴巴开源了一个`TransmittableThreadLocal`组件就可以解决这个问题，这里就不再延伸，感兴趣的可自行查阅资料。
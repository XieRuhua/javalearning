# ConcurrentHashMap详解（JDK1.7和JDK1.8）

[笔记内容参考1：java集合-ConcurrentHashMap源码详解（基于JDK1.7）](https://blog.csdn.net/baidu_32689899/article/details/107059041)  
[笔记内容参考2：java集合-ConcurrentHashMap源码概述（基于JDK1.8）](https://blog.csdn.net/baidu_32689899/article/details/107085175)  
[笔记内容参考3：Java集合篇：ConcurrentHashMap详解（JDK1.8）](https://blog.csdn.net/a745233700/article/details/83123359)  
[笔记内容参考4：Java集合篇：ConcurrentHashMap详解（JDK1.6）](https://blog.csdn.net/a745233700/article/details/83120464)  
[笔记内容参考5：还不懂 ConcurrentHashMap ？这份源码分析了解一下](https://snailclimb.gitee.io/javaguide/#/docs/java/collection/concurrent-hash-map-source-code?id=_3-put)    
[笔记内容参考6：java ConcurrentHashMap源码解析 (jdk1.7)](https://blog.csdn.net/qq_41786692/article/details/79837903) 

[toc]

## 一、ConcurrentHashMap-JDK1.7
### 1. 概述
**`ConcurrentHashMap`是由`Segment数组`和`HashEntry数组`组成。`Segment`继承了`ReentrantLock`，所以它可以实现锁的功能，`HashEntry`则用于存储键值对数据。**

一个`ConcurrentHashMap`里包含一个`Segment数组`，而其中的 **元素`Segment`的结构和`HashMap`类似，是一种数组和链表结构** ， 一个`Segment`里包含一个`HashEntry数组`，每个`HashEntry`是一个 **`链表`** 结构的元素， 每个`Segment`对一个`HashEntry数组`进行锁控制。
当对`HashEntry数组`的数据进行 **修改** 时，必须首先获得它对应的`Segment锁`， **以此达到线程安全的目的。**

### 2. 存储结构（ConcurrentHashMap 在 JDK 中的定义）
为了更好的理解 `ConcurrentHashMap` 高并发的具体实现，先了解它在JDK中的定义。

`ConcurrentHashMap`类中包含两个静态内部类 `HashEntry` 和 `Segment`：
- `HashEntry` 用来封装具体的 **K/V键值对** ；
- `Segment` 用来充当 **锁** 的角色，**每个 `Segment` 对象守护整个`ConcurrentHashMap`的若干个桶 (可以把Segment看作是一个小型的哈希表)** ，其中每个 **桶** 是由若干个 `HashEntry` 对象链接起来的 **链表（1.7的HashMap和ConcurrentHashMap都只有链表加数组，而1.8加入了红黑树）**。

总的来说，一个`ConcurrentHashMap`实例中包含由若干个`Segment`实例组成的数组，而一个`Segment`实例又包含由若干个`桶`，每个`桶`中都包含一条由若干个 `HashEntry` 对象链接起来的`链表`。  
**<font color="red">注意：ConcurrentHashMap 在默认并发级别下会创建`16`个Segment对象的数组，如果键能均匀散列，每个 Segment 大约守护整个散列表中桶总数的 `1/16`。</font>**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/ConcurrentHashMap-JDK7存储结构.png)
</center>

Java 7 中 `ConcurrentHashMap` 的存储结构如上图，`ConcurrnetHashMap` 由很多个 `Segment` 组合，而每一个 `Segment` 是一个类似于 `HashMap` 的结构，所以每一个 `HashMap` 的内部可以进行扩容。

**<font color="red">但是 `Segment` 的个数一旦初始化就不能改变，默认 `Segment` 的个数是 `16` 个，所以可以认为 `ConcurrentHashMap` 默认支持最多 `16` 个线程并发。</font>**

#### 2.1 类结构定义：
`ConcurrentHashMap` 继承了`AbstractMap`并实现了`ConcurrentMap`接口，其在JDK中的定义为：
```java
public class ConcurrentHashMap<K, V> extends AbstractMap<K, V>
        implements ConcurrentMap<K, V>, Serializable {
    ......
}
```

#### 2.2 成员变量定义：
同`HashMap`相比，`ConcurrentHashMap` 增加了两个属性用于定位段，分别是 `segmentMask` 和 `segmentShift`。  
此外，不同于`HashMap`的是，`ConcurrentHashMap` **底层结构** 是一个`Segment数组`，而不是`Object数组`，具体源码如下：
```java
/**
 * Mask value for indexing into segments. The upper bits of a
 * key's hash code are used to choose the segment.
 */
final int segmentMask;  // 用于定位段，大小等于segments数组的大小减 1，是不可变的

/**
 * Shift value for indexing within segments.
 */
final int segmentShift;    // 用于定位段，大小等于32(hash值的位数)减去对segments的大小取以2为底的对数值，是不可变的

/**
 * The segments, each of which is a specialized hash table
 */
final Segment<K, V>[] segments;   // ConcurrentHashMap的底层结构是一个Segment数组
```

#### 2.3 段的定义Segment：
**`Segment` 类继承于 `ReentrantLock` 类，从而使得 `Segment` 对象能充当锁的角色。** 每个 `Segment` 对象用来守护它的成员对象 `table` 中包含的若干个桶（链表数组）。table 是一个由 `HashEntry` 对象组成的链表数组，`table数组`的每一个数组成员就是一个桶。

在`Segment`类中，有一个`count` 变量，它是一个计数器： **它表示每个 `Segment` 对象管理的 `table` 数组包含的 `HashEntry` 对象的个数，** 也就是 `Segment` 中包含的 `HashEntry` 对象的总数。  

注意：之所以在每个 `Segment` 对象中包含一个计数器，而不是在 `ConcurrentHashMap` 中使用全局的计数器，是对 `ConcurrentHashMap` **<font color="red">并发性</font>** 的考虑：**因为这样当需要更新计数器时，不用锁定整个`ConcurrentHashMap`。** 
- 每次对段进行结构上的改变：如在段中进行增加/删除节点 **（修改节点的值不算结构上的改变）** ，都要更新`count`的值；  
此外，在JDK1.7的实现中每次读取操作开始都要先读取`count`的值。 
- `count`是 **`volatile`** 的，这使得对`count`的任何更新对其它线程都是立即可见的。  
- `modCount`用于统计 **段结构改变的次数** ，主要是为了检测对多个段进行遍历过程中某个段是否发生改变，这一点具体在谈到跨段操作时会详述。
- `threashold`用来表示段需要进行重哈希的阈值。
- `loadFactor`表示段的负载因子，其值等同于`ConcurrentHashMap`的负载因子的值。table是一个典型的链表数组，而且也是  **`volatile`**  的，这使得对`table`的任何更新对其它线程也都是立即可见的。

段（Segment）的定义源码如下：
```java
/**
 * Segments are specialized versions of hash tables.  This
 * subclasses from ReentrantLock opportunistically, just to
 * simplify some locking and avoid separate construction.
 */
static final class Segment<K,V> extends ReentrantLock implements Serializable {

    /**
     * The number of elements. Accessed only either within locks
     * or among other volatile reads that maintain visibility.
     */
    transient volatile int count;    // Segment中元素的数量，只能在锁中访问或者在其他保持可见性的易变读取中。

    /**
     * The total number of mutative operations in this segment.
     * Even though this may overflows 32 bits, it provides
     * sufficient accuracy for stability checks in CHM isEmpty()
     * and size() methods.  Accessed only either within locks or
     * among other volatile reads that maintain visibility.
     */
    transient int modCount;  //对count的大小造成影响的操作的次数（比如put或者remove操作）

    /**
     * The table is rehashed when its size exceeds this threshold.
     * (The value of this field is always <tt>(int)(capacity *
     * loadFactor)</tt>.)
     */
    transient int threshold;      // 阈值，段中元素的数量超过这个值就会对Segment进行扩容

    /**
     * The per-segment table.
     */
    transient volatile HashEntry<K,V>[] table;  // 链表数组

    /**
     * The load factor for the hash table.  Even though this value
     * is same for all segments, it is replicated to avoid needing
     * links to outer object.
     * @serial
     */
    final float loadFactor;  // 段的负载因子，其值等同于ConcurrentHashMap的负载因子
        ......
}
```
**小结：**  
**`ConcurrentHashMap`允许多个修改（写）操作并发进行，其关键在于使用了锁分段技术，它使用了不同的锁来控制对哈希表的不同部分进行的修改（写），而 `ConcurrentHashMap` 内部使用段（`Segment`）来表示这些不同的部分。**   
实际上，每个段实质上就是一个小的哈希表，每个段都有自己的锁(`Segment` 类继承了 `ReentrantLock` 类)。这样，只要多个修改（写）操作发生在不同的段上，它们就可以并发进行。

#### 2.4 基本元素：HashEntry
`HashEntry`用来封装具体的键值对，是个典型的四元组。与`HashMap`中的`Entry`类似，`HashEntry`也包括同样的四个域，分别是`key`、`hash`、`value`和`next`。  
**不同的是，在HashEntry类中，key、hash以及HashEntry本身都被声明为final的，value域被volatile所修饰，因此HashEntry对象几乎是不可变的，这是ConcurrentHashmap读操作并不需要加锁的一个重要原因。** 

**注意：由于`value域`被`volatile`修饰，所以其可以确保被读线程读到最新的值，这是`ConcurrentHashmap`读操作并不需要加锁的另一个重要原因。实际上，`ConcurrentHashMap`完全允许多个读操作并发进行，读操作并不需要加锁。**

`HashEntry`代表`hash链`中的一个节点，其结构如下所示：
```java
/**
 * ConcurrentHashMap 中的 HashEntry 类
 * 
 * ConcurrentHashMap list entry. Note that this is never exported
 * out as a user-visible Map.Entry.
 */
static final class HashEntry<K,V> {
    final K key;                    // 声明 key 为 final 的
    final int hash;                 // 声明 hash 值为 final 的
    volatile V value;               // 声明 value 被volatile所修饰
    volatile HashEntry<K,V> next;      // 声明 next 被volatile所修饰

    HashEntry(K key, int hash, HashEntry<K,V> next, V value) {
        this.key = key;
        this.hash = hash;
        this.next = next;
        this.value = value;
    }

    @SuppressWarnings("unchecked")
    static final <K,V> HashEntry<K,V>[] newArray(int i) {
        return new HashEntry[i];
    }
}
```
与`HashMap`类似，在`ConcurrentHashMap`中，如果在散列时发生碰撞，也会将碰撞的 `HashEntry` 对象链成一个链表。

下图是在一个空桶中依次插入 `A`，`B`，`C` 三个 `HashEntry` 对象后的步骤图 **（由于ConcurrentHashMap在JDK1.7中采用的头插法————详见后文的put方法解析，所以链表中节点的顺序和插入的顺序相反）：**
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/ConcurrentHashMap1.7的HashEntry插入步骤.png)
</center>

**与`ConcurrentHashMap`的`HashEntry`不同的是，`HashMap` 中的 `Entry` 只有`key`是`final`的** ，其结构如下所示：
```java
/**
 * HashMap 中的 Entry 类
 */
static class Entry<K,V> implements Map.Entry<K,V> {
    final K key;
    V value;
    Entry<K,V> next;
    int hash;

    /**
    * Creates new entry.
    */
    Entry(int h, K k, V v, Entry<K,V> n) {
        value = v;
        next = n;
        key = k;
        hash = h;
    }
    ......
}
```

#### 2.5 小结
`ConcurrentHashMap`的高效并发机制是通过以下三方面来保证的：
- 通过锁分段技术保证并发环境下的写操作；
- 通过`HashEntry`的不变性、`volatile`变量的内存可见性和加锁重读机制保证高效、安全的读操作；
- 通过读操作不加锁和写操作加锁，两种方案控制跨段操作的安全性。

### 3. 构造函数
`ConcurrentHashMap` 一共提供了五个构造函数，其中包含默认无参的构造函数和参数为`Map`的构造函数 （Java Collection Framework 规范的推荐实现），其余三个构造函数则是 `ConcurrentHashMap` 专门提供的。

#### 3.1 ConcurrentHashMap(int initialCapacity, float loadFactor, int concurrencyLevel)：
该构造函数意在构造一个具有指定 **容量** 、指定 **负载因子** 和指定 **段数目/并发级别** (若不是2的幂次方，则会调整为2的幂次方)的空`ConcurrentHashMap`，其相关源码如下：
```java
/**
 * Creates a new, empty map with the specified initial
 * capacity, load factor and concurrency level.
 *
 * @param initialCapacity the initial capacity. The implementation
 * performs internal sizing to accommodate this many elements.
 * @param loadFactor  the load factor threshold, used to control resizing.
 * Resizing may be performed when the average number of elements per
 * bin exceeds this threshold.
 * @param concurrencyLevel the estimated number of concurrently
 * updating threads. The implementation performs internal sizing
 * to try to accommodate this many threads.
 * @throws IllegalArgumentException if the initial capacity is
 * negative or the load factor or concurrencyLevel are
 * nonpositive.
 */
@SuppressWarnings("unchecked")
public ConcurrentHashMap(int initialCapacity,
                         float loadFactor, int concurrencyLevel) {
    // 参数校验：判断传入的参数是否合法，如果不合法则会抛出异常
    if (!(loadFactor > 0) || initialCapacity < 0 || concurrencyLevel <= 0)
        throw new IllegalArgumentException();
    // 校验并发级别大小：并发级别最大支持2的16次幂，如果超多这个数则使用最大值：MAX_SEGMENTS = 1 << 16;
    if (concurrencyLevel > MAX_SEGMENTS) concurrencyLevel = MAX_SEGMENTS;
    // 寻找一个最佳匹配的2的n次幂的数
    int sshift = 0;// 记录循环（左移）了多少次
    int ssize = 1;// Segment数组的大小
    while (ssize < concurrencyLevel) {
        // concurrencyLevel为传入的并发级别，每次循环都左移一位，相当于2的的n次幂
        // 当ssize这个数大于等于传入的并发级别时，就找到了最佳匹配的一个2的次方数
        ++sshift;
        ssize <<= 1;
    }
    // 记录段偏移量：int占32位，减去1左移了多少位，比如说传入的是默认参数值concurrencyLevel等于16，就是左移了4位
    this.segmentShift = 32 - sshift;
    // 记录段掩码
    this.segmentMask = ssize - 1;
    // 设置容量：如果初始容量大于最大值则取最大值
    if (initialCapacity > MAXIMUM_CAPACITY) initialCapacity = MAXIMUM_CAPACITY;
    // 使用初始容量除以分段数，得到每段小数组的大小（c = 容量 / ssize ，默认 16 / 16 = 1，这里是计算每个 Segment 中的类似于 HashMap 的容量）
    int c = initialCapacity / ssize;
    if (c * ssize < initialCapacity)
        ++c;
    // 每个段Entry数组的最小容量，默认值是2 
    int cap = MIN_SEGMENT_TABLE_CAPACITY;
    // 计算出每段entry数组的大小（Segment 中的类似于 HashMap 的容量至少是2或者2的倍数）
    while (cap < c)
        cap <<= 1;
    // 创建一个segment对象模版，初始化该断Entry数组，并指定该Entry数组的大小和加载因子
    Segment<K,V> s0 = new Segment<K,V>(loadFactor, (int)(cap * loadFactor), (HashEntry<K,V>[])new HashEntry[cap]);
    // 创建segment数组，元素都为null
    Segment<K,V>[] ss = (Segment<K,V>[])new Segment[ssize];
    // 设置 segments[0]：使用unsafe类设置segment数组下标为0的值为模版对象
    UNSAFE.putOrderedObject(ss, SBASE, s0); // ordered write of segments[0]
    this.segments = ss;
}
```
**大致执行步骤：**
- 对传入的`Map` **容量** 、 **加载因子** 和 **并发级别（分段数）** 进行处理；
- 对`segment数组`（分段数）进行初始化；
- 对`segment数组`下标为`0`的位置初始化`entry`数组。

初始化之后的结构如下图：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/ConcurrentHashMap1.7构造函数初始化.png)
</center>

#### 3.2 ConcurrentHashMap(int initialCapacity, float loadFactor)：
该构造函数意在构造一个具有 **指定容量** 、 **指定负载因子** 和 **默认并发级别(16)** 的空`ConcurrentHashMap`，其相关源码如下：
```java
/**
 * Creates a new, empty map with the specified initial capacity
 * and load factor and with the default concurrencyLevel (16).
 *
 * @param initialCapacity The implementation performs internal
 * sizing to accommodate this many elements.
 * @param loadFactor  the load factor threshold, used to control resizing.
 * Resizing may be performed when the average number of elements per
 * bin exceeds this threshold.
 * @throws IllegalArgumentException if the initial capacity of
 * elements is negative or the load factor is nonpositive
 *
 * @since 1.6
 */
public ConcurrentHashMap(int initialCapacity, float loadFactor) {
    this(initialCapacity, loadFactor, DEFAULT_CONCURRENCY_LEVEL);  // 默认并发级别为16
}
```

#### 3.3 ConcurrentHashMap(int initialCapacity)：
该构造函数意在构造一个具有 **指定容量** 、 **默认负载因子(0.75)** 和 **默认并发级别(16)** 的空`ConcurrentHashMap`，其相关源码如下：
```java
/**
 * Creates a new, empty map with the specified initial capacity,
 * and with default load factor (0.75) and concurrencyLevel (16).
 *
 * @param initialCapacity the initial capacity. The implementation
 * performs internal sizing to accommodate this many elements.
 * @throws IllegalArgumentException if the initial capacity of
 * elements is negative.
 */
public ConcurrentHashMap(int initialCapacity) {
    this(initialCapacity, DEFAULT_LOAD_FACTOR, DEFAULT_CONCURRENCY_LEVEL);
}
```

#### 3.4 ConcurrentHashMap()：
该构造函数意在构造一个具有 **默认初始容量(16)** 、 **默认负载因子(0.75)** 和 **默认并发级别(16)** 的空`ConcurrentHashMap`，其相关源码如下：
```java
/**
 * Creates a new, empty map with a default initial capacity (16),
 * load factor (0.75) and concurrencyLevel (16).
 */
public ConcurrentHashMap() {
    this(DEFAULT_INITIAL_CAPACITY, DEFAULT_LOAD_FACTOR, DEFAULT_CONCURRENCY_LEVEL);
}
```

默认的构造函数里，调用了三个参数的构造函数，传入了默认值：
```java
// 默认初始容量
static final int DEFAULT_INITIAL_CAPACITY = 16;
 
// 默认的加载因子
static final float DEFAULT_LOAD_FACTOR = 0.75f;
 
// 默认并发级别
static final int DEFAULT_CONCURRENCY_LEVEL = 16;
 
public ConcurrentHashMap() {
    this(DEFAULT_INITIAL_CAPACITY, DEFAULT_LOAD_FACTOR, DEFAULT_CONCURRENCY_LEVEL);
}
```
和`HashMap`相比，默认的 **初始容量** 和 **加载因子** 都是一样的。  
`ConcurrentHashMap`多了一个 **并发级别** ，这个可以理解为把`Segments数组`分为多少段，每段数组单独的控制锁。

#### 3.5 ConcurrentHashMap(Map<? extends K, ? extends V> m)：
该构造函数意在构造一个与指定 `Map` 具有相同映射的 `ConcurrentHashMap`，其 **初始容量不小于 `16`** (具体依赖于指定Map的大小)， **负载因子是 `0.75`** ， **并发级别是 `16`** ，是 Java Collection Framework 规范推荐提供的，其源码如下：
```java
/**
 * Creates a new map with the same mappings as the given map.
 * The map is created with a capacity of 1.5 times the number
 * of mappings in the given map or 16 (whichever is greater),
 * and a default load factor (0.75) and concurrencyLevel (16).
 *
 * @param m the map
 */
public ConcurrentHashMap(Map<? extends K, ? extends V> m) {
    this(Math.max((int) (m.size() / DEFAULT_LOAD_FACTOR) + 1,
                  DEFAULT_INITIAL_CAPACITY),
         DEFAULT_LOAD_FACTOR, DEFAULT_CONCURRENCY_LEVEL);
    putAll(m);
}
```
在这里，提到了三个非常重要的参数： **初始容量** 、 **负载因子** 和 **并发级别** ，这三个参数是影响`ConcurrentHashMap`性能的重要参数。  
从上述源码可以看出，`ConcurrentHashMap` 也正是通过`initialCapacity(初始容量)`、`loadFactor(负载因子)`和`concurrencyLevel(并发级别)`这三个参数进行构造并初始化`segments数组`、`段偏移量segmentShift`、`段掩码segmentMask`和每个`segment`的。

#### 小结：
总结一下在 Java 7 中 `ConcurrnetHashMap` 的初始化逻辑。
1. 必要参数校验；
2. 校验并发级别 `concurrencyLevel(并发级别)` 大小，如果大于最大值，重置为最大值，无参构造 **默认值是 `16`** ；
3. 寻找并发级别 `concurrencyLevel(并发级别)` 之上最近的 **`2` 的幂次方** 值，作为初始化容量大小， **默认是 `16`** ；
4. 记录 `segmentShift` 偏移量， **这个值为【容量 = 2 的N次方】中的 N** ，在后面 `Put` 时计算位置时会用到， **默认是 `32 - sshift = 28`** ；
5. 记录 `segmentMask`，默认是 `ssize - 1 = 16 -1 = 15`；
6. **初始化 `segments[0]`** ，**默认大小为 `2`** ，**负载因子 `0.75`** ，**扩容阀值是 `2*0.75=1.5`** ，插入第二个值时才会进行扩容。

### 4. 方法解析
#### 4.1 put
```java
public V put(K key, V value) {
    Segment<K,V> s;
    // 1.如果value为null则抛出异常
    if (value == null)
        throw new NullPointerException();
    // 2.和HashMap一样，要计算出hash值，这里没有判断key是否为null，但是如果key为null，则会报错
    int hash = hash(key);
    // 3.计算出要放到哪个segment[]下标：hash 值无符号右移 28位（初始化时获得），然后与 segmentMask=15 做与运算（其实也就是把高4位与segmentMask（1111）做与运算）
    int j = (hash >>> segmentShift) & segmentMask;
    // 4.使用unsafe取出j下标处的对象，如果为null则创建
    if ((s = (Segment<K,V>)UNSAFE.getObject          // nonvolatile; recheck
         (segments, (j << SSHIFT) + SBASE)) == null) //  in ensureSegment
        // 4.1 如果查找到的 Segment 为空，初始化
        s = ensureSegment(j);
    // 5.调用segment的put方法来设置数据（entry对象）
    return s.put(key, hash, value, false);
}
```
**执行步骤：**
1. 判断`value`是否为空，为空则抛出异常`NullPointerException()`；
2. 计算`key`的`hash值`，即要 `put` 的 `key` 的位置 **（注意：这一步`key`如果为空，也会抛出异常`NullPointerException()`）；**
3. 根据 `hash`值判断该 `entry` 所对应的 `Segment` 位置。
4. 如果指定位置的 `Segment` 为空，则初始化这个 `Segment` **（第4.1步调用`ensureSegment`方法）**
5. `Segment.put` 插入 `key/value` 值。

下面再看一下在 **第4.1步初始化segment对象** 的方法和`segment`对象的`put`方法

##### 4.1.1  ensureSegment
在`ConcurrnetHashMap`的`put`方法的第4.1步初始化`segment`对象：
```java
private Segment<K,V> ensureSegment(int k) {
    // 1.将segment数组赋值为局部变量ss
    final Segment<K,V>[] ss = this.segments;
    // 2.k为角标位置，计算出该角标元素的内存地址偏移量
    long u = (k << SSHIFT) + SBASE; // raw offset
    Segment<K,V> seg;
    // 3.判断 u 位置的 Segment 是否为null，如果不为空则返回该对象
    if ((seg = (Segment<K,V>)UNSAFE.getObjectVolatile(ss, u)) == null) {
        // 3.1 使用segment[0]位置的模版对象（在初始化的时候创建了一个模版对象）
        Segment<K,V> proto = ss[0]; // use segment 0 as prototype
        // 3.2 segment[0] 里的 HashEntry<K,V> 初始化长度
        int cap = proto.table.length;
        //     segment[0] 里的 hash 表里的扩容负载因子（注：所有的 segment 的 loadFactor 是相同的）
        float lf = proto.loadFactor;
        //     计算扩容阀值
        int threshold = (int)(cap * lf);
        // 3.3 创建一个 cap 容量的 HashEntry 数组
        HashEntry<K,V>[] tab = (HashEntry<K,V>[])new HashEntry[cap];
        // 3.4 再检查一遍内存中该对象有没有被初始化（因为这个是可以并发访问的，其他线程可能会进行初始化）
        if ((seg = (Segment<K,V>)UNSAFE.getObjectVolatile(ss, u)) == null) { // recheck
            // 3.4.1 创建出segment对象
            Segment<K,V> s = new Segment<K,V>(lf, threshold, tab);
            // 3.4.2 自旋检查 u 位置的 Segment 是否为null，并把segment对象放入到指定的下标位置
            while ((seg = (Segment<K,V>)UNSAFE.getObjectVolatile(ss, u)) == null) {// 该位置为null才需要方segment对象进行
                // 3.4.3 使用原子操作设置segment对象到下标为k的位置，为null是才需要设置
                if (UNSAFE.compareAndSwapObject(ss, u, null, seg = s))
                    break;// 设置成功，跳出循环
            }
        }
    }
    // 4. 在segment[k]位置初始化了segment对象后，返回该对象
    return seg;
}
```
**执行步骤：**
1. 将全局变量`segment数组`赋值为局部变量
2. 计算出下标元素的 **内存地址偏移量**
3. 判断元素下标对应的`Segment` 是否为`null`，不为空则返回该对象，如果为空则执行下面的初始化流程：  
    - 3.1. 使用 `Segment[0]` 的 **容量** 和 **负载因子** 创建一个 `HashEntry数组`  
    - 3.2. 使用 `segment[0]` 位置的模版来得到分段`entry数组`的 **大小** 、 **加载因子** 和 **扩容阈值** ，并初始化该数组  
    - 3.3. 创建一个获取的初始化大小容量的 `HashEntry` 数组  
    - 3.4. 再次检查计算得到的指定位置的 `Segment` 是否为`null` **（因为这个是可以并发访问的，其他线程可能会进行初始化）** ，如不为`null`，则停止初始化，返回对应的`Segment`，为空则继续初始化：  
        - 3.4.1. 根据上面获取的 **数组的大小** 、 **加载因子** 和 **扩容阈值** 创建出新的`segment对象`  
        - 3.4.2. 使用`cas`操作对`segment[k]`进行赋值，然后跳出循环  
4. 最后返回该`segment对象`

##### 4.1.2 segment的put方法
在`ConcurrnetHashMap`的`put`方法第5步：
```java
// 5.调用segment的put方法来设置数据（entry对象）
// return s.put(key, hash, value, false);
final V put(K key, int hash, V value, boolean onlyIfAbsent) {
    // 尝试获取 ReentrantLock 独占锁，如果获取锁失败，则先使用scanAndLockForPut方法来初始化entiry对象
    HashEntry<K,V> node = tryLock() ? null : scanAndLockForPut(key, hash, value);
    ......
}
```
执行 `segment`的`put`方法分两种情况：

**1）尝试获取锁成功：**
```java
// 初始化该段的加载因子和扩容阈值以及Entry数组对象
Segment(float lf, int threshold, HashEntry<K,V>[] tab) {
    this.loadFactor = lf;
    this.threshold = threshold;
    this.table = tab;
}
final V put(K key, int hash, V value, boolean onlyIfAbsent) {
    // 1. 尝试获取 ReentrantLock 独占锁，如果获取锁失败，则先使用scanAndLockForPut方法来初始化entiry对象
    HashEntry<K,V> node = tryLock() ? null : scanAndLockForPut(key, hash, value);
    V oldValue;
    // 成功获取到锁对象之后：
    try {
        // 2. 将该段的entry数组赋值给局部变量
        HashEntry<K,V>[] tab = table;
        // 3. 计算要put的数据位置
        int index = (tab.length - 1) & hash;
        // 4. CAS 获取 index 坐标的值：使用unsafe对象获取entry数组index下标的entry对象
        HashEntry<K,V> first = entryAt(tab, index);
        // 5. 对该entry对象进行遍厉（单向链表结构）
        for (HashEntry<K,V> e = first;;) {
            // 5.1 该位置上的HashEntry不为空
            if (e != null) {
                K k;
                // 5.1.1 检查是否 key 已经存在，如果找到key和hash相同的entry对象，则说明key重复，则对该数据进行覆盖，然后跳出循环
                if ((k = e.key) == key || (e.hash == hash && key.equals(k))) {
                    oldValue = e.value;
                    if (!onlyIfAbsent) {
                        e.value = value;
                        ++modCount;
                    }
                    break;// 替换之后跳出循环
                }
                //  5.1.2 如果没有找到相同的key则继续遍厉查找
                e = e.next;
            }
            // 5.2 该位置上的HashEntry为空，即该entry链表进行遍厉没有找到相同key的对象或者本身该链表就是null，则进入
            else {
                if (node != null)// 不为null，则说明没有获取到锁，但是在scanAndLockForPut中初始化了该对象，注意：这里的初始化直接给node的next属性设置为上面获取的first，即头插法
                    node.setNext(first);
                else// 为null，则初始化该entry对象，注意这里：初始化的node的next属性为上面获取的first，所以可以看出ConcurrentHashMap在1.7的put方法中使用的是头插法
                    node = new HashEntry<K,V>(hash, key, value, first);
                int c = count + 1;
                // 5.2.1 判断是否需要扩容（容量大于扩容阀值，小于最大容量，进行扩容）
                if (c > threshold && tab.length < MAXIMUM_CAPACITY)
                    rehash(node);
                else// 5.2.2 如果不需要扩容，则把该entry对象放到entry数组的指定下标位置即可
                    setEntryAt(tab, index, node);
                ++modCount;
                count = c;
                oldValue = null;
                break;// 插入之后跳出循环
            }
        }
    } finally {
        unlock();// 释放锁
    }
    return oldValue;// 6. 如果是替换则返回旧的值
}
```
由于 `Segment` 继承了 `ReentrantLock`，所以 `Segment` 内部可以很方便的获取锁（重入锁），`Segment`的`put` 方法就用到了这个功能。

**执行流程：**
1. 调用 `tryLock()` 尝试获取 `ReentrantLock` 独占锁，获取不到使用 **`scanAndLockForPut`** 方法继续获取；
2. 将该段的`entry数组`赋值给局部变量；
3. 计算 `put` 的数据要放入的 `index` 位置；
4. 通过`CAS`获取这个位置上的 `HashEntry` ；
5. 遍历 `put` 新元素，为什么要遍历？ **因为这里获取的 `HashEntry` 可能是一个空元素，也可能是已存在的链表，所以要区别对待。**
    - 5.1. 如果这个位置上的 **`HashEntry` 存在**（不为空）：
        - 5.1.1. 判断链表当前元素 `Key` 和 `hash` 值是否和要 `put` 的 `key` 和 `hash` 值一致。一致则说明`key`重复，则对该数据进行覆盖，然后跳出循环；
        - 5.1.2. 不一致，获取链表下一个节点，直到发现相同进行值替换，或者链表里没有相同的；
    - 5.2. 如果这个位置上的 **`HashEntry` 不存在**（为空）：
        - 5.2.1. 判断是否需要扩容（容量大于扩容阀值，小于最大容量，进行扩容）；
        - 5.2.2. 如果不需要扩容，直接 **头插法** 插入，插入之后跳出循环  
        **（注意：初始化的`node对象`的`next`属性为上面获取的`first`，所以可以看出`ConcurrentHashMap`在`JDK1.7`的`put`方法中使用的是头插法）** ；
6. 如果要插入的位置之前已经存在，替换后返回旧值，否则返回 `null`。

**2）尝试获取锁失败**  
尝试获取 `ReentrantLock` 独占锁，获取锁失败进入`scanAndLockForPut(key, hash, value)`方法
```java
final V put(K key, int hash, V value, boolean onlyIfAbsent) {
    // 尝试获取 ReentrantLock 独占锁，如果获取锁失败，则先使用scanAndLockForPut方法来初始化entiry对象
    HashEntry<K,V> node = tryLock() ? null : scanAndLockForPut(key, hash, value);
    ......
}
```
```java
/**
 * 扫描指定的节点元素，同时尝试获取锁，在返回的时候确保获取锁成功
 */
private HashEntry<K,V> scanAndLockForPut(K key, int hash, V value) {
    // 1. 在没有获取锁的情况下取出entry数组的entry链表头元素
    HashEntry<K,V> first = entryForHash(this, hash);
    HashEntry<K,V> e = first;// 赋值给局部变量e
    HashEntry<K,V> node = null;// 定义将要插入的数据node
    int retries = -1; // negative while locating node
    // 2. 自旋获取锁
    while (!tryLock()) {
        HashEntry<K,V> f; // to recheck first below
        // 第一次尝试获取锁
        if (retries < 0) {
            if (e == null) {// 3. 如果链表的头节点为null，则初始化将要插入的entry数据
                if (node == null) // speculatively create node
                    node = new HashEntry<K,V>(hash, key, value, null);
                retries = 0;// 设置为0后，第二次尝试获取锁就不会进入该代码块
            }
            else if (key.equals(e.key))// 如果key相同，说明可能要覆盖，但是不在这里处理
                retries = 0;
            else// 链表头节点不为null，并且还没有找到需要key相同的节点，则继续遍厉该链表
                e = e.next;
        }
        // MAX_SCAN_RETRIES默认值与cup核心数有关，多核是MAX_SCAN_RETRIES值为64
        else if (++retries > MAX_SCAN_RETRIES) {
            // 尝试获取锁的次数超过一定次数后，则阻塞获取锁
            lock();
            break;
        }
        // 4. retries等于0，并且获取的链表头元素被与entry数组内存中对象不相同时
        // 说明该entry数组index位置被其他线程更新过数据，则对局部变量e和first进行重新赋值，然后让循环进入遍厉链表
        else if ((retries & 1) == 0 && (f = entryForHash(this, hash)) != first) {
            e = first = f; // re-traverse if entry changed
            retries = -1;
        }
    }
    // 5. 最终方法返回HashEntry，结束的时候会保证获取到锁的
    return node;
}
```
**执行步骤：**
1. 在没有获取锁的情况下取出`entry数组`的`entry链表头元素`（即从内存中取出将要插入`entry`数组下标位置的链表）
2. 不断的尝试获取锁，同时对`链表e`进行遍厉
3. 如果链表和将要插入的`entry对象`都为`null`则初始化`entry`对象，然后继续不断的获取锁 **（直到超过指定次数后，调用`lock方`法阻塞获取锁，退出循环）** ；
4. 对`entry对象`初始化之后，每次尝试获取锁的同时都会对局部变量`链表e`的头元素与内存中的链表头元素进行比较，如果不同的话，需要对局部变量`链表e`进行重新复制，然后对`链表e`进行重新遍厉
5. 最终方法返回`HashEntry`，结束的时候会保证获取到锁的（自旋次数大于指定次数时：`MAX_SCAN_RETRIES`默认值与`cup`核心数有关，多核时`MAX_SCAN_RETRIES`值为`64`）

**`scanAndLockForPut`方法做的操作就是不断的自旋 `tryLock()` 获取锁。当自旋次数大于指定次数时，使用 `lock()` 阻塞从而成功获取锁。在自旋时顺便获取 `hash` 位置的 `HashEntry`（初始化好的entry对象）。**

#### 4.2 扩容 rehash
`ConcurrentHashMap` 的扩容只会扩容到原来的 **两倍** 。

老数组里的数据移动到新的数组时，位置要么不变，要么变为 `index+ oldSize`，参数里的 `node` 会在扩容之后使用链表 **头插法** 插入到指定位置。
```java
private void rehash(HashEntry<K,V> node) {
    // 1. 将entry数组赋值给局部变量
    HashEntry<K,V>[] oldTable = table;
    // 老容量
    int oldCapacity = oldTable.length;
    // 新容量，扩大两倍
    int newCapacity = oldCapacity << 1;
    // 新的扩容阀值 
    threshold = (int)(newCapacity * loadFactor);
    // 2. 创建新的entry空数组
    HashEntry<K,V>[] newTable = (HashEntry<K,V>[]) new HashEntry[newCapacity];
    // 新的掩码，默认2扩容后是4，-1是3，二进制就是11。
    int sizeMask = newCapacity - 1;
    // 3. 遍厉老的数组，然后迁移到新数组
    // 大概步骤就是判断当前节点的下一节点是否和自己被迁移到新数组的同一个下标，
    // 并且下一个节点必须是尾节点，相当于一次迁移了多个节点的数据，减少迁移次数和减少新节点的创建
    for (int i = 0; i < oldCapacity ; i++) {
        // 遍历老数组
        HashEntry<K,V> e = oldTable[i];
        if (e != null) {
            HashEntry<K,V> next = e.next;
            // 3.1 计算新的位置，新的位置只可能是不便或者是老的位置+老的容量。
            int idx = e.hash & sizeMask;
            if (next == null)   //  Single node on list
                // 3.1.1 如果当前位置还不是链表，只是一个元素，直接赋值
                newTable[idx] = e;
            else { // Reuse consecutive sequence at same slot
                // 3.1.2 如果是链表了
                HashEntry<K,V> lastRun = e;
                int lastIdx = idx;
                // 新的位置只可能是不变或者是老的位置+老的容量。
                // 遍历结束后，lastRun 后面的元素位置都是相同的
                for (HashEntry<K,V> last = next; last != null; last = last.next) {
                    int k = last.hash & sizeMask;
                    if (k != lastIdx) {
                        lastIdx = k;
                        lastRun = last;
                    }
                }
                // 直接作为链表赋值到新位置。
                newTable[lastIdx] = lastRun;
                // Clone remaining nodes
                for (HashEntry<K,V> p = e; p != lastRun; p = p.next) {
                    // 遍历剩余元素，头插法到指定 k 位置。
                    V v = p.value;
                    int h = p.hash;
                    int k = h & sizeMask;
                    HashEntry<K,V> n = newTable[k];
                    newTable[k] = new HashEntry<K,V>(h, p.key, v, n);
                }
            }
        }
    }
    // 扩容之后插入新数据（头插法插入新的节点）
    int nodeIndex = node.hash & sizeMask; // add the new node
    node.setNext(newTable[nodeIndex]);
    newTable[nodeIndex] = node;
    // 4. 将hashEntry数组更新为扩容之后的数组
    table = newTable;
}
```
**执行步骤：**
1. 将`entry数组`赋值给局部变量，并获取老容量，定义新容量 **（老容量的两倍）** 以及新容量的 **扩容阈值** ；
2. 创建新的`entry空数组`
3. 遍厉老的数组，开始将元素迁移到新数组：
    - 3.1. 计算新的位置，新的位置只可能是 **不变** 或者是 **老的位置+老的容量** ；
        - 3.1.1. 如果当前位置还不是 **链表** ，只是一个元素，直接赋值
        - 3.1.2. 如果是 **链表** 了，开始链表的迁移 **（头插法插入新的节点）** 
4. 最后将`hashEntry数组`更新为扩容之后的数组

**补充：**
- 这里扩容只是对`segment`里的一个`hashEntry数组`进行扩容，而不是对`整个map`进行扩容。
- 扩容方法是在获取锁之后进行调用的，所以不会存在并发扩容的问题。
- 扩容和`HashMap`一样，都是 **翻倍** 的扩容。  
  **但是在数据迁移的时候做了一点优化：如果链表尾的多个元素在新数组中放在相同下标的话，可以对这多个元素进行一次迁移，可以减少新元素的创建。**
- 最后的两个 `for` 循环：
  - 第一个 `for` 是为了寻找这样一个节点：这个节点后面的所有 `next` 节点的新位置都是相同的，然后把这个作为一个链表赋值到新位置。
  - 第二个 `for` 循环是为了把剩余的元素通过 **头插法** 插入到指定位置链表。

#### 4.3 get
`ConcurrentHashMap` 的 `get` 操作也就是`segment对象`的`get`操作，源码分析如下：
```java
public V get(Object key) {
    Segment<K,V> s; // manually integrate access methods to reduce overhead
    HashEntry<K,V>[] tab;
    int h = hash(key);
    // 1. 计算得到 key 的存放位置（key对应的segment对象内存地址偏移量）
    long u = (((h >>> segmentShift) & segmentMask) << SSHIFT) + SBASE;
    // 2. 如果该segment对象和segment对象中的hashEntry数组都不为null，才会去获取key对应的value
    if ((s = (Segment<K,V>)UNSAFE.getObjectVolatile(segments, u)) != null &&
        (tab = s.table) != null) {
        // ((long)(((tab.length - 1) & h)) << TSHIFT) + TBASE：计算出hashEntry数组下标为h的内存地址偏移量
        // (HashEntry<K,V>) UNSAFE.getObjectVolatile：获取内存中的hashEntry对象
        // 3. 对获取的对象进行遍厉（如果不为null的话）
        for (HashEntry<K,V> e = (HashEntry<K,V>) UNSAFE.getObjectVolatile
                 (tab, ((long)(((tab.length - 1) & h)) << TSHIFT) + TBASE);
             e != null; e = e.next) {
            K k;
            // 如果是链表，找到该链表中key和hash值相同的对象，返回value值
            if ((k = e.key) == key || (e.hash == h && key.equals(k)))
                return e.value;
        }
    }
    // 4. 如果没有找到则返回null
    return null;
}
```
**执行步骤：**
1. 计算得到 `key` 的存放位置（`key`对应的`segment对象内存地址偏移量`）；
2. 如果该`segment对象`和`segment对象`中的`hashEntry数组`都不为`null`，才会去获取`key`对应的`value`；
3. 对获取的对象进行遍厉，找到该链表中`key`和`hash`值相同的对象，返回`value`值；
4. 如果没有找到则返回`null`。

**补充：`ConcurrentHashMap` 读操作（`get`方法）不需要加锁的奥秘：**  
通过`HashEntry对象`的定义可以知道`HashEntry`中的`key`、`hash`和`HashEntry本身`都是`final`修饰的，所以`HashEntry`几乎是不可变的。  
**这意味着，不能把节点添加到链表的中间和尾部，当然也不能在链表的中间和尾部删除节点。**   这个特性可以保证：在访问某个节点时，这个节点之后的链接不会被改变，这样就可以大大降低处理链表时的复杂性。  

与此同时，由于`HashEntry`类的`value`字段被声明是`Volatile`的，因此Java的内存模型就可以保证：某个写线程对`value`字段的 **写入** 马上就可以被后续的某个读线程看到。  
此外，由于在`ConcurrentHashMap`中不允许用`null`作为键和值（均会抛出`NullPointerException`异常），所以当 **读线程** 读到某个`HashEntry`的`value`为`null`时，便知道产生了冲突 ——— 发生了重排序现象，**此时便会加锁重新读入这个`value`值。**  
这些特性互相配合，使得 **读线程(get方法)** 即使在不加锁状态下，也能正确访问 `ConcurrentHashMap`。

总的来说，`ConcurrentHashMap`读操作不需要加锁的奥秘在于以下三点：
- **用`HashEntery对象`的不变性来降低读操作对加锁的需求；**
- **用`Volatile变量`协调读写线程间的内存可见性；**
- **若读时发生指令重排序现象，则加锁重读。**

#### 4.4 remove
`ConcurrentHashMap` 的 `remove` 操作也交给了`segment对象`的`remove`，源码分析如下：
```java
// ConcurrentHashMap的remove方法，最终还是调用Segment的remove方法
// 1. 删除某个key值所在的结点--只要key值相等就删除
public V remove(Object key) {
    int hash = hash(key);
    Segment<K,V> s = segmentForHash(hash);
    return s == null ? null : s.remove(key, hash, null);
}

// 2. 删除某个键为key，值为value的结点--需要key和value都匹配上才删除
public boolean remove(Object key, Object value) {
    int hash = hash(key);
    Segment<K,V> s;
    return value != null && (s = segmentForHash(hash)) != null &&
        s.remove(key, hash, value) != null;
}
```
```java
// Segment的remove方法：删除某个结点
final V remove(Object key, int hash, Object value) {
    // 1. 同put一样，先获取锁，所锁获取失败则调用scanAndLock方法进行自旋获取
    if (!tryLock())
        scanAndLock(key, hash);
    V oldValue = null;
    try {
        HashEntry<K,V>[] tab = table;
        int index = (tab.length - 1) & hash;
        HashEntry<K,V> e = entryAt(tab, index);
        HashEntry<K,V> pred = null;
        // 2. 遍历key对应的链表
        while (e != null) {
            K k;
            HashEntry<K,V> next = e.next;
            // 3. 如果找到对应的key值
            if ((k = e.key) == key ||
                (e.hash == hash && key.equals(k))) {
                V v = e.value;
                //4. 如果value值相等
                if (value == null || value == v || value.equals(v)) {
                    // 4.1 如果移除的是表头结点，则更新数组项的值
                    if (pred == null)
                        setEntryAt(tab, index, next);
                    else// 4.2 如果移除的的中间结点，那么直接将该节点的前面的结点的next结点指向该节点的next结点，这也是hashEntry中next结点未设置成final的原因
                        pred.setNext(next);
                    ++modCount;
                    --count;
                    oldValue = v;
                }
                // 5. 如果value值不相等，不做删除操作，直接返回
                break;
            }
            pred = e;
            e = next;
        }
    } finally {
        unlock();
    }
    // 6. 返回旧值
    return oldValue;
}
```
**执行步骤：**
1. 同`put`一样，先获取锁，所若获取失败则调用`scanAndLock`方法进行自旋获取；
2. 遍历`key`对应的链表；
3. 如果找到对应的`key`值；
4. 如果`value`值相等，判断节点位置：
    - 4.1. 如果移除的是 **表头结点** ，则更新数组项的值；
    - 4.2. 如果移除的是 **中间结点** ，那么直接将该节点的前面的结点的`next结点`指向该节点的`next结点`，这也是`hashEntry`中`next结点`未设置成`final`的原因（见下图）；
5. 如果`value`值不相等，不做删除操作，直接返回；
6. 释放锁，返回旧值。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/ConcurrentHashMap1.7删除节点.png)
</center>

**补充：**  
**在`remove`中如果获取锁失败也会像`put`操作一样进入自旋操作，这里调用的`scanAndLock方法`与`scanAndLockForPut方法`类似，只是`scanAndLock`不会预创建结点。**

#### 4.5 clear
```java
/**
 * Removes all of the mappings from this map.
 */
public void clear() {
    final Segment<K,V>[] segments = this.segments;
    for (int j = 0; j < segments.length; ++j) {//循环clear掉每个段中的内容
        Segment<K,V> s = segmentAt(segments, j);
        if (s != null)
            s.clear();
    }
}
final void clear() {
    lock();// 段内加锁
    try {
        HashEntry<K,V>[] tab = table;
        for (int i = 0; i < tab.length ; i++)
            setEntryAt(tab, i, null);
        ++modCount;
        count = 0;
    } finally {
        unlock();
    }
}
```
因为没有全局的锁，在清除完一个`segment数组`之后，正在清理下一个`segment数组`的时候，已经清理`segment数组`可能又被加入了数据，因此`clear`返回的时候，`ConcurrentHashMap`中是可能存在数据的。   
**因此，clear方法是弱一致的。**

#### 4.6 size
```java
public int size() {
    // Try a few times to get accurate count. On failure due to
    // continuous async changes in table, resort to locking.
    final Segment<K,V>[] segments = this.segments; //map数据从segments中拿取
    int size;		 // 统计的大小
    boolean overflow; // true if size overflows 32 bits size过大的溢出情况
    long sum;         // sum of modCounts  统计modCounts的值
    long last = 0L;   // previous sum 最近的一个sum值
    int retries = -1; // first iteration isn't retry  重试的次数：第一次迭代不是重试
    try {
        for (;;) {//一直循环统计size直至segment结构没有发生变化
            // 遍历segment数组，对每个segment加锁
            if (retries++ == RETRIES_BEFORE_LOCK) {//如果已经重试2次，到达第三次
                for (int j = 0; j < segments.length; ++j)
                    ensureSegment(j).lock(); // force creation //把segment加上锁
            }
            sum = 0L;
            size = 0;
            overflow = false;
            // 遍历segment数组，取得每个segment
            for (int j = 0; j < segments.length; ++j) {
                Segment<K,V> seg = segmentAt(segments, j);
                if (seg != null) {
                    // sum为Segment数组结构修改的次数和
                    sum += seg.modCount;
                    // c为当前segment的个数
                    int c = seg.count;
                    if (c < 0 || (size += c) < 0)
                        overflow = true;
                }
            }
            // 前后两次遍历时segment结构修改的次数相等，那么认为遍历过程中没有新的元素的插入，停止遍历
            if (sum == last)
                break;
            last = sum;
        }
    } finally {
        if (retries > RETRIES_BEFORE_LOCK) {//有重试3次以上的情况
            for (int j = 0; j < segments.length; ++j)
                segmentAt(segments, j).unlock(); //把segment解锁
        }
    }
    return overflow ? Integer.MAX_VALUE : size;
}
```
**如果要统计整个`ConcurrentHashMap`里元素的大小，就必须统计所有`Segment`里元素的大小后求和。**  

**问题一：`Segment`里的全局变量`count`是一个`volatile`变量，那么在多线程场景下，是不是直接把所有`Segment`的`count`相加就可以得到整个`ConcurrentHashMap`大小了呢？**  
不是的，虽然相加时可以获取每个`Segment`的`count`的最新值， **但是拿到之后可能累加前使用的`count`发生了变化** ，那么统计结果就不准了。  
所以最安全的做法，是在统计`size`的时候把所有`Segment`的`put`，`remove`和`clean`方法全部锁住，但是这种做法显然非常低效，因为在累加`count`操作过程中，之前累加过的`count`发生变化的几率非常小，所以`ConcurrentHashMap`的做法是先尝试`RETRIES_BEFORE_LOCK次（2次）`通过不锁住`Segment`的方式来统计各个`Segment`大小，如果统计的过程中，容器的`count`发生了变化，则最后再采用加锁的方式来统计所有`Segment`的大小。

**问题二：`ConcurrentHashMap`是如何判断在统计的时候容器是否发生了变化呢？**  
使用`modCount`变量。在`put`、`remove`和`clear`方法里操作前都会将变量`modCount`进行`加1`，在统计`size`前后比较`modCount`是否发生变化，从而得知容器的大小是否发生变化。 

`size()`的实现还有一点需要注意，必须要先`segments[i].count`，才能`segments[i].modCount`，这是因为`segment[i].count`是对`volatile`变量的访问，而接下来`segments[i].modCount`才能得到几乎最新的值，  **这里和`get`方法的方式是一样的，也是一个`volatile写` `happens-before volatile读`的问题。**

`size()`方法主要思路是先在没有锁的情况下对所有段大小求和，这种求和策略最多执行`RETRIES_BEFORE_LOCK次(默认是两次)`：
- 在没有达到`RETRIES_BEFORE_LOCK`之前，求和操作会不断尝试执行（这是因为遍历过程中可能有其它线程正在对已经遍历过的段进行结构性更新）；
- 在超过`RETRIES_BEFORE_LOCK`之后，如果还不成功就在持有所有段锁的情况下再对所有段大小求和。

### 5. ConcurrentHashMap -JDK1.7的总结
1. `ConcurrentHashMap`是线程安全的，可并发访问，`key`和`value`都不允许为`null`；
2. `ConcurrentHashMap`使用了分段锁技术，`Segment`继承了可重入锁`ReentrantLock`，对`HashTable`的修改操作都要使用锁，只有在同一个`Segment`中才存在竞争关系，不同的`Segment`之间没有所竞争；相对于整个`Map`加锁的设计分段锁大大的提高了高并发环境下的处理能力；
3. `ConcurrentHashMap`的`put`、`get`、`remove`和`replace`操作都是对某一个`segment`进行操作，而`clear`是锁住整个`table`，`size`和`contains`方法则是给一定的机会不使用锁；
4. `ConcurrentHashMap`中`segment数`和每个`segment`中的`table长度`都是`2`的 **次幂** ；
5. `ConcurrentHashMap`中如果`segment`数设置的过小，会带来严重的所竞争问题，如果设置的过大，会使原本在同一个`Segment`中的访问扩散到不同的`Segment`中，命中率过低，从而引起程序性能下降；
6. `ConcurrentHashMap`中初始化时只会初始化第一个`segment`，剩下的`segment`采用的是延迟初始化的机制，因此在每次`put`操作时都需要检查`key`对应的`segment`是否为`null`，如果为空则需要初始化。

## 二、ConcurrentHashMap-JDK1.8
### 1.  概述
与`JDK1.7`的版本有很大的差异。实现线程安全的思想也已经完全变了，**它摒弃了`Segment`（锁段）的概念，而是启用了一种全新的方式实现，即利用`CAS`算法。** 它沿用了与它同时期的`HashMap`版本的思想，底层依然由 **“数组”+链表+红黑树** 的方式思想，但是为了做到 **并发** ，又增加了很多辅助的类，例如`TreeBin`，`Traverser`等对象内部类。

`JDK1.8`的`ConcurrentHashMap`，取消了分段锁的概念，虽然在构造函数中可以指定 **并发级别** 这个参数，但是实际 **只是判断了如果初始容量小于并发级别，则把初识容量的值设置为并发级别的值，然后就没有用到并发级别这个参数了。**    
因为在`JDK1.8`中，锁更加的细化了，使用对`Node数组`的每个下标中的头节点元素进行加锁。就相当于容量有多少就有多少锁，锁住的是每一个桶。同时在进行扩容的时候还支持部分数据的访问不阻塞。

### 2. 存储结构
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/ConcurrentHashMap1.8的存储结构.png)
</center>

可以发现 `JDK1.8` 的 `ConcurrentHashMap` 相对于 `JDK1.7` 来说变化比较大，不再是之前的 **`Segment 数组` + `HashEntry 数组` + `链表`**，而是 **`Node 数组` + `链表` / `红黑树`**。当冲突链表达到一定长度时，链表会转换成红黑树（这一点同`JDK1.8`的`HashMap`一样）。

#### 2.1 重要的内部类
##### 2.1.1 Node：
`Node`是最核心的内部类，它包装了`key-value键值`对，所有插入`ConcurrentHashMap`的数据都包装在这里面。它与HashMap中的定义很相似，但是但是有一些差别它对`value`和`next`属性设置了`volatile`同步锁，它不允许调用`setValue`方法直接改变`Node`的`value`域，它增加了`find`方法辅助`map.get()`方法。
```java
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    volatile V val;         //带有同步锁的value
    volatile Node<K,V> next;//带有同步锁的next指针
    Node(int hash, K key, V val, Node<K,V> next) {
        this.hash = hash;
        this.key = key;
        this.val = val;
        this.next = next;
    }

    public final K getKey()       { return key; }
    public final V getValue()     { return val; }
    public final int hashCode()   { return key.hashCode() ^ val.hashCode(); }
    public final String toString(){ return key + "=" + val; }

    //不允许直接改变value的值
    public final V setValue(V value) {
        throw new UnsupportedOperationException();
    }

    public final boolean equals(Object o) {
        Object k, v, u; Map.Entry<?,?> e;
        return ((o instanceof Map.Entry) &&
                (k = (e = (Map.Entry<?,?>)o).getKey()) != null &&
                (v = e.getValue()) != null &&
                (k == key || k.equals(key)) &&
                (v == (u = val) || v.equals(u)));
    }

    /**
    * Virtualized support for map.get(); overridden in subclasses.
    */
    Node<K,V> find(int h, Object k) {
        Node<K,V> e = this;
        if (k != null) {
            do {
                K ek;
                if (e.hash == h &&
                    ((ek = e.key) == k || (ek != null && k.equals(ek))))
                    return e;
            } while ((e = e.next) != null);
        }
        return null;
    }
}
```
这个`Node内部类`与`HashMap`中定义的`Node类`很相似，但是有一些差别：
- 对`value`和`next`属性设置了`volatile同步锁`
- 不允许调用`setValue`方法直接改变`Node的value域`
- 增加了`find方法`辅助`map.get()`方法

##### 2.1.2 TreeNode：
**树节点类，另外一个核心的数据结构。**

当链表长度过长的时候，会转换为`TreeNode`。但是与`HashMap`不相同的是，它并不是直接转换为红黑树，而是把这些结点包装成`TreeNode`放在`TreeBin`对象中，由`TreeBin`完成对红黑树的包装。  
而且`TreeNode`在`ConcurrentHashMap`继承自`Node`类，而并非`HashMap`中的继承自`LinkedHashMap.Entry<K,V>`类，也就是说`TreeNode`带有`next指针`，这样做的目的是方便基于`TreeBin`的访问。
```java
// JDK1.8 ConcurrentHashMap 中的TreeNode
static final class TreeNode<K,V> extends Node<K,V> {
    TreeNode<K,V> parent;  // red-black tree links
    TreeNode<K,V> left;
    TreeNode<K,V> right;
    TreeNode<K,V> prev;    // needed to unlink next upon deletion
    boolean red;

    TreeNode(int hash, K key, V val, Node<K,V> next,
             TreeNode<K,V> parent) {
        super(hash, key, val, next);
        this.parent = parent;
    }

    ......
}

// JDK1.8 HashMap 中的TreeNode
static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
    TreeNode<K,V> parent;  // red-black tree links
    TreeNode<K,V> left;
    TreeNode<K,V> right;
    TreeNode<K,V> prev;    // needed to unlink next upon deletion
    boolean red;
    TreeNode(int hash, K key, V val, Node<K,V> next) {
        super(hash, key, val, next);
    }

    /**
     * Returns root of tree containing this node.
     */
    final TreeNode<K,V> root() {
        for (TreeNode<K,V> r = this, p;;) {
            if ((p = r.parent) == null)
                return r;
            r = p;
        }
    }

    ......
}
```

##### 2.1.3 TreeBin：
这个类并不负责包装`key`、`value`信息，而是包装的多个`TreeNode`节点。  
它代替了`TreeNode`的根节点，也就是说在实际的`ConcurrentHashMap`中，存放的是`TreeBin`对象，而不是`TreeNode`对象，这是与`HashMap`的区别。 **另外这个类还带有了读写锁。**

这里仅贴出它的构造方法，可以看到在构造`TreeBin`节点时，仅仅指定了它的`hash`值为`TREEBIN常量`，这也就是个标识。同时也看到红黑树构造方法:
```java
/**
 * Creates bin with initial set of nodes headed by b.
 * 使用以 b 为首的初始节点集创建 bin。
 */
TreeBin(TreeNode<K,V> b) {
    super(TREEBIN, null, null, null);
    this.first = b;
    TreeNode<K,V> r = null;
    for (TreeNode<K,V> x = b, next; x != null; x = next) {
        next = (TreeNode<K,V>)x.next;
        x.left = x.right = null;
        if (r == null) {
            x.parent = null;
            x.red = false;
            r = x;
        }
        else {
            K k = x.key;
            int h = x.hash;
            Class<?> kc = null;
            for (TreeNode<K,V> p = r;;) {
                int dir, ph;
                K pk = p.key;
                if ((ph = p.hash) > h)
                    dir = -1;
                else if (ph < h)
                    dir = 1;
                else if ((kc == null &&
                          (kc = comparableClassFor(k)) == null) ||
                         (dir = compareComparables(kc, k, pk)) == 0)
                    dir = tieBreakOrder(k, pk);
                TreeNode<K,V> xp = p;
                if ((p = (dir <= 0) ? p.left : p.right) == null) {
                    x.parent = xp;
                    if (dir <= 0)
                        xp.left = x;
                    else
                        xp.right = x;
                    r = balanceInsertion(r, x);
                    break;
                }
            }
        }
    }
    this.root = r;
    assert checkInvariants(root);
}
```

##### 2.1.4 ForwardingNode：
一个用于连接两个`table`的 **节点类** 。  
它包含一个`nextTable指针`，用于指向 **下一张表** 。而且这个节点的`key` `value` `next指针`全部为`null`，它的`hash值`为`-1`。这里面定义的`find`的方法是从`nextTable`里进行查询节点，而不是以自身为头节点进行查找。
```java
/**
 * A node inserted at head of bins during transfer operations.
 */
static final class ForwardingNode<K,V> extends Node<K,V> {
    final Node<K,V>[] nextTable;
    ForwardingNode(Node<K,V>[] tab) {
        super(MOVED, null, null, null);
        this.nextTable = tab;
    }

    Node<K,V> find(int h, Object k) {
        // loop to avoid arbitrarily deep recursion on forwarding nodes
        outer: for (Node<K,V>[] tab = nextTable;;) {
            Node<K,V> e; int n;
            if (k == null || tab == null || (n = tab.length) == 0 ||
                (e = tabAt(tab, (n - 1) & h)) == null)
                return null;
            for (;;) {
                int eh; K ek;
                if ((eh = e.hash) == h &&
                    ((ek = e.key) == k || (ek != null && k.equals(ek))))
                    return e;
                if (eh < 0) {
                    if (e instanceof ForwardingNode) {
                        tab = ((ForwardingNode<K,V>)e).nextTable;
                        continue outer;
                    }
                    else
                        return e.find(h, k);
                }
                if ((e = e.next) == null)
                    return null;
            }
        }
    }
}
```

### 3. 构造函数
```java
// 1. 创建一个空表，默认初始大小为16
public ConcurrentHashMap()
// 2. 创建一个空表，指定了默认大小
public ConcurrentHashMap(int initialCapacity)  
// 3. 创建了一个表，并将复制参数中的所有表元素
public ConcurrentHashMap(Map<? extends K, ? extends V> m)
// 4. 创建一个表，指定了初始大小以及加载因子
public ConcurrentHashMap(int initialCapacity, float loadFactor) 
// 5. 创建一个表，指定了初始大小，加载因子和并发等级（默认为1）；
public ConcurrentHashMap(int initialCapacity,
                         float loadFactor, int concurrencyLevel) 
```

这里就只对有三个参数的构造函数进行说明， **注意一个地方：初始容量会与加载因子有关（最后一个构造函数）。**
```java
public ConcurrentHashMap(int initialCapacity, float loadFactor, int concurrencyLevel) {
    // 对传入的参数进行校验
    if (!(loadFactor > 0.0f) || initialCapacity < 0 || concurrencyLevel <= 0)
        throw new IllegalArgumentException();
    // 如果容量小于并发级别，则把容量设置为与并发级别一样大小
    if (initialCapacity < concurrencyLevel)   // Use at least as many bins
        initialCapacity = concurrencyLevel;   // as estimated threads
    // 这里会根据传入的指定容量和加载因子来计算出了size
    long size = (long)(1.0 + (long)initialCapacity / loadFactor);
    // 然后会找到一个大于等于size的2的幂次方数
    int cap = (size >= (long)MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : tableSizeFor((int)size);
    // 对容量进行赋值
    this.sizeCtl = cap;
}
```

### 4. 方法解析
#### 4.1 put
**`ConcurrentHashMap`最常用的就是`put`和`get`两个方法。**

`put`方法依然沿用`HashMap`的`put`方法的思想，根据`hash值`计算这个新插入的点在`table`中的位置`i`，如果`i`位置是空的，直接放进去，否则进行判断，如果`i`位置是树节点，按照树的方式插入新的节点，否则把`i`插入到链表的末尾。

**有一个最重要的不同点就是`ConcurrentHashMap`不允许`key`或`value`为`null`值。**

另外由于涉及到多线程，`put`方法就要复杂一点。在多线程中可能有以下两个情况：
1. **如果一个或多个线程正在对`ConcurrentHashMap`进行扩容操作，则当前线程也要进入扩容的操作中** 。这个扩容的操作之所以能被检测到，是因为`transfer`方法中在空结点上插入`forward节点`，如果检测到需要插入的位置被`forward节点`占有，就帮助进行扩容；
2. 如果检测到要插入的节点是`非空`且不是`forward节点`，就对这个节点加锁，这样就保证了线程安全。  
尽管这个有一些影响效率，但是还是会比`hashTable`的`synchronized`要好得多。

```java
public V put(K key, V value) {
    return putVal(key, value, false);
}

/** Implementation for put and putIfAbsent */
final V putVal(K key, V value, boolean onlyIfAbsent) {
    // 不允许NULL的键和值，因为并发情况下无法分辨是不存在Key还是没有找到，
    // 以及Value本身就为空，所以不允许NULL的存在；HashMap可以判断，因为containsKey方法存在。而在多线程中，contains后去get，可能会发生修改或者删除，无法判断，故不支持；
    // 1. 判断key和value是否为null，如果是则抛出异常，说明该Map是不支持null值的
    if (key == null || value == null) throw new NullPointerException();
    // 2. 根据key计算出hash值
    int hash = spread(key.hashCode());
    int binCount = 0;
    // 3. 把Node数组赋值给局部变量tab之后，进入一个死循环，进行CAS不断竞争，或者协助扩容后出来继续干活等等
    for (Node<K,V>[] tab = table;;) {
        // f = 目标位置元素，fh 后面存放目标位置的元素 hash 值
        Node<K,V> f; int n, i, fh;
        // 3.1 如果tab为null则需要初始化该数组
        if (tab == null || (n = tab.length) == 0)
            // 数组桶为空，这里对Node数组进行初始化，该方法里会保证线程安全（自旋+CAS)
            // 只有一个线程会成功执行数组的初始化，其他线程会直接返回初始化好的数组
            // 然后结束本次循环，进入下一次循环，下一次循环判断tab不为null之后就不会再执行到这里了
            tab = initTable();
        // 3.2 如果该下标下的元素为null，则创建一个新的Node元素，使用cas操作设置到数组中，当产生并发时，只会与一个线程设置成功，然后跳出循环
        // (n - 1) & hash 计算出数组下标
        // tabAt方法为根据下标从内存取出Node数组中的元素
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            // 桶内为空，CAS 放入，不加锁，成功了就直接 break 跳出
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;                   // no lock when adding to empty bin
        }
        // 3.3 如果取出的f不为空，并且被标记为正在调整大小则进入此分支
        else if ((fh = f.hash) == MOVED)
            // 帮助数据转移。
            tab = helpTransfer(tab, f);
        // 3.4 如果node数组已经初始化了，并且要插入的下标位置已经有了数据，
        // 那么就需要对链表或者红黑树进行插入节点或者替换节点的操作
        else {
            V oldVal = null;
            // 使用synchronized锁，锁对象为该下标下的元素
            synchronized (f) {
                // 3.4.1 拿到锁之后再判断一下这个f对象有没有被其他线程修改
                // 如果被修改了的话，就先不做修改，等下次循环到这里的时候再判断能不能改
                if (tabAt(tab, i) == f) {
                    // 3.4.2 说明是链表
                    if (fh >= 0) {
                        binCount = 1;
                        // 循环加入新的或者覆盖节点
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            // 如果是key相同是覆盖操作的话，这里if就成立
                            if (e.hash == hash && ((ek = e.key) == key || (ek != null && key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            Node<K,V> pred = e;
                            // 使用尾插发插入元素
                            if ((e = e.next) == null) {
                                pred.next = new Node<K,V>(hash, key,
                                                          value, null);
                                break;
                            }
                        }
                    }
                    // 3.4.3 红黑树：如果是树结构则调用树结构的插入方法
                    else if (f instanceof TreeBin) {
                        Node<K,V> p;
                        binCount = 2;
                        if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key, value)) != null) {
                            oldVal = p.val;
                            if (!onlyIfAbsent)
                                p.val = value;
                        }
                    }
                }
            }// 同步代码块结束
            // 3.5 操作完成之后判断一下是否需要对链表进行转换为树结构
            if (binCount != 0) {
                // 3.5.1 如果链表的长度大于等于8，则把链表转换为树
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);// 该方法中有同步代码块来解决并发问题
                // 如果进入了这个if，则说明之前的put操作成功了
                if (oldVal != null)// 如果是替换操作则直接返回旧值
                    return oldVal;
                break;
            }
        }
    }
    // 4. 如果不是替换操作，并且新增元素成功的话就会执行到这里
    // 这里会对node的数据进行统计，如果需要扩容则扩容
    // binCount，如果为0，说明是在空节点新增
    addCount(1L, binCount);
    return null;
}
```
**执行步骤：**  
`put方法`中调用`putVal方法`
1. 判断`key`和`value`是否为`null`，如果是则抛出异常（`ConcurrentHashMap`是不支持 **键或值** 为`null`值的）；
2. 根据`key`计算出`hash值`；
3. 把`Node数组`赋值给局部变量`tab`之后，进入一个死循环，进行`CAS`不断竞争（保证并发安全）， **或者协助扩容** ；  
   对`tab`进行判断：
    - 3.1. 如果`tab`为`null`则需要 **初始化** 该数组，调用`initTable()`方法，该方法里会保证线程安全 **（自旋+CAS)** ；
    - 3.2. 如果该下标下的元素为`null`，则创建一个新的`Node`元素，使用`cas`操作设置到数组中，当产生并发时，只会与一个线程设置成功，然后跳出循环；
    - 3.3. 如果取出的`f`不为空，并且被标记为正在调整大小，则进行数据转移；
    - 3.4. 如果`node数组`已经初始化了，并且要插入的下标位置已经有了数据，那么就需要 **先获取锁（防止其他线程一起操作当前数据）** ，然后对 **链表** 或者 **红黑树** 进行插入节点或者替换节点的操作：
        - 3.4.1. 先拿到锁之后再判断一下这个`f`对象有没有被其他线程修改，如果被其他线程修改了的话，当前线程就先不做修改，等下次循环到这里的时候再判断能不能改；
        - 3.4.2. 再判断如果是 **链表** ，循环加入新的或者覆盖节点；
        - 3.4.3. 如果是 **红黑树** 则调用树结构的插入方法；
    - 3.5. **操作完成之后判断一下是否需要对链表进行转换为树结构（链表的长度大于等于 `TREEIFY_THRESHOLD(8)`，且`treeifyBin()`方法中会判断当前数组长度≥`MIN_TREEIFY_CAPACITY(64)`，才会把链表转换为树）** ；
4. 最后调用`addCount()`方法对`Node数组`中的`Node元素`进行统计，如果需要扩容则扩容。

##### 4.1.1 initTable() 初始化Node数组
对于`ConcurrentHashMap`来说，调用它的构造方法仅仅是设置了一些参数而已。  
而整个`table`的初始化是在向`ConcurrentHashMap`中插入元素的时候发生的。如调用`put`、`computeIfAbsent`、`compute`、`merge`等方法的时候，调用时机是检查`table==null`。  
**（如上述笔记中put方法第3.1步）**
```java
/**
 * Table initialization and resizing control.  When negative, the
 * table is being initialized or resized: -1 for initialization,
 * else -(1 + the number of active resizing threads).  Otherwise,
 * when table is null, holds the initial table size to use upon
 * creation, or 0 for default. After initialization, holds the
 * next element count value upon which to resize the table.
 * 表初始化和调整大小控制。
 * 1. 如果为负数，则表正在初始化或调整大小：-1 表示初始化，
 * 2. 否则 -(1 + 活动调整大小线程的数量)。
 * 3. 否则，当 table 为 null 时，保存要在创建时使用的初始表大小，或者默认为 0。
 * 4. 初始化后，保存下一个元素计数值，根据该值调整表的大小。
 */
private transient volatile int sizeCtl;
```
```java
private final Node<K,V>[] initTable() {
    Node<K,V>[] tab; int sc;
    // 1. 死循环判断tab是否已经初始化，知道初始化完成
    while ((tab = table) == null || tab.length == 0) {
        // 2. 如果 sizeCtl < 0 ,说明另外的线程执行CAS 成功，则让出cpu（因为已经有线程在进行初始化了）
        // sizeCtl就是初始容量的大小，把它赋值给局部变量sc，sc记录下了容量
        if ((sc = sizeCtl) < 0)
            // 让出 CPU 使用权
            Thread.yield(); // lost initialization race; just spin
        // 3. 使用cas操作把sizeCtl的值设置为-1，只会有一个线程能设置成功
        else if (U.compareAndSwapInt(this, SIZECTL, sc, -1)) {
            try {
                // 3.1 当其他线程也执行到这里的时候，判断table就不为null，会直接返回初始化好的数组
                if ((tab = table) == null || tab.length == 0) {
                    // sc记录下了容量大小，把容量大小赋值给n，如果在new ConcurrentHashMap的时候没有指定容量，那么这里就使用默认的容量16
                    int n = (sc > 0) ? sc : DEFAULT_CAPACITY;
                    @SuppressWarnings("unchecked")
                    Node<K,V>[] nt = (Node<K,V>[])new Node<?,?>[n];// 创建出Node数组
                    table = tab = nt;// 将Node数组赋值给table属性
                    sc = n - (n >>> 2);
                }
            } finally {
                // 3.2 初始化之后，保存要调整表大小的下一个元素计数值。
                sizeCtl = sc;
            }
            break;
        }
    }
    // 4. 返回初始化好的元素
    return tab;
}
```
从源码中可以发现 `ConcurrentHashMap` 的初始化是通过 **自旋和 CAS** 操作完成的。里面需要注意的是变量 `sizeCtl` ，它的值决定着当前的初始化状态：
- `1` 说明正在初始化
- `N` 说明有`N-1`个线程正在进行扩容
- 如果 `table` **没有初始化** ，表示 `table` **初始化大小**
- 如果 `table` **已经初始化** ，表示 `table` **容量**

`正数`或`0`代表`hash`表还没有被初始化，这个数值表示初始化或下一次进行扩容的大小，这一点类似于扩容阈值的概念。  
后面还可以看到，它的值始终是当前`ConcurrentHashMap容量`的`0.75倍`，这与`loadfactor（负载因子）`属性是对应的。

**在这也可以看出`ConcurrentHashMap`的初始化只能由一个线程完成。如果获得了初始化权限，就用`CAS`方法将`sizeCtl`置为`-1`，防止其他线程进入。**

##### 4.1.2 addCount(long x, int check)   
在`put`方法结尾处调用了`addCount`方法 **（上述笔记put方法第4步）** ，把当前`ConcurrentHashMap`的元素个数`+1`。这个方法一共做了两件事：
- 更新`baseCount`的值；
- 检测是否进行扩容。

```java
/**
 * 表初始化和调整大小控件。
 * 当为负数时，表正在初始化或调整大小:-1表示初始化，否则为-(1 +活动调整大小的线程数)。
 * 当表为null时，保存创建时要使用的初始表大小，或默认为0。
 * 初始化之后，保存扩容阈值。
 */
private transient volatile int sizeCtl;
```
```java
private final void addCount(long x, int check) {
    CounterCell[] as; long b, s;
    // 如果单元计数器不为空 或者对基础计数器值原子更新失败时 ：if成立
    if ((as = counterCells) != null || !U.compareAndSwapLong(this, BASECOUNT, b = baseCount, s = b + x)) {
        CounterCell a; long v; int m;
        boolean uncontended = true;// 默认无竞争
        // ThreadLocalRandom.getProbe()：返回当前线程的探针哈希值
        // 如果单元计数器还没有初始化 或者计数器的长度为0 或者该线程对应的计数元素还没有创建
        if (as == null || (m = as.length - 1) < 0 || (a = as[ThreadLocalRandom.getProbe() & m]) == null ||
            // CELLVALUE 为CounterCell计数器对象的value值
            // 获取对计数器对象的原子+1操作失败
            !(uncontended = U.compareAndSwapLong(a, CELLVALUE, v = a.value, v + x))) {
            // 总之就是如果统计未成功就执行到这里，然后使用fullAddCount方法来进行统计
            // uncontended：如果原子操作失败则为false，说明有竞争；如果线程计数器对象还没有初始化则默认为true无竞争
            fullAddCount(x, uncontended);
            return;
        }
        if (check <= 1)
            return;
        s = sumCount();// 计算出当前的数据量
    }
    // 对数组进行扩容
    if (check >= 0) {
        Node<K,V>[] tab, nt; int n, sc;
        //检查当前集合元素个数 s 是否达到扩容阈值 sizeCtl ，扩容时 sizeCtl 为负数，依旧成立，
        // 同时还得满足数组非空且数组长度不能大于允许的数组最大长度这两个条件才能继续
        //这个 while 循环除了判断是否达到阈值从而进行扩容操作之外还有一个作用就是当一条线程完成自己的迁移任务后，
        // 如果集合还在扩容，则会继续循环，加入迁移任务
        while (s >= (long)(sc = sizeCtl) && (tab = table) != null && (n = tab.length) < MAXIMUM_CAPACITY) {
            int rs = resizeStamp(n);
            if (sc < 0) {// sc < 0 说明集合正在扩容当中
                //判断扩容是否结束或者并发扩容线程数是否已达最大值，如果是的话直接结束while循环
                if ((sc >>> RESIZE_STAMP_SHIFT) != rs || sc == rs + 1 || sc == rs + MAX_RESIZERS || (nt = nextTable) == null || transferIndex <= 0)
                    break;
                //扩容还未结束，并且允许扩容线程加入
                if (U.compareAndSwapInt(this, SIZECTL, sc, sc + 1))
                    transfer(tab, nt);
            }
            //如果集合还未处于扩容状态中，则进入扩容方法，并首先初始化 nextTab 数组，也就是新数组
            else if (U.compareAndSwapInt(this, SIZECTL, sc, (rs << RESIZE_STAMP_SHIFT) + 2))
                transfer(tab, null);
            s = sumCount();
        }
    }
}

// See LongAdder version for explanation
private final void fullAddCount(long x, boolean wasUncontended) {
    int h;
    if ((h = ThreadLocalRandom.getProbe()) == 0) {
        ThreadLocalRandom.localInit(); // 如果为0则需要对这个值进行初始化
        h = ThreadLocalRandom.getProbe();// 获取线程的探针哈希值
        wasUncontended = true;// 如果没有初始化则设置为无竞争
    }
    boolean collide = false;                // True if last slot nonempty
    for (;;) {
        CounterCell[] as; CounterCell a; int n; long v;
        // 如果单元计数器数组已经初始化过了 if成立
        if ((as = counterCells) != null && (n = as.length) > 0) {
            if ((a = as[(n - 1) & h]) == null) {// 判断该线程对应的计数器元素是否为空 如果为空if成立
                if (cellsBusy == 0) {            // Try to attach new Cell
                    // 创建计数器元素
                    CounterCell r = new CounterCell(x); // Optimistic create
                    if (cellsBusy == 0 && U.compareAndSwapInt(this, CELLSBUSY, 0, 1)) {
                        boolean created = false;
                        try {               // Recheck under lock
                            CounterCell[] rs; int m, j;
                            if ((rs = counterCells) != null && (m = rs.length) > 0 && rs[j = (m - 1) & h] == null) {
                                rs[j] = r;// 将计数器元素赋值到指定下标下
                                created = true;// 为true下面会跳出循环
                            }
                        } finally {
                            cellsBusy = 0;// 将标记重置为0
                        }
                        if (created)// 赋值操作成功后created为true，跳出循环
                            break;
                        continue;           // Slot is now non-empty
                    }
                }
                collide = false;
            }
            else if (!wasUncontended)       // CAS already known to fail
                wasUncontended = true;      // Continue after rehash
            // 直接对计数器元素的值进行+1操作 如果成功则跳出循环
            else if (U.compareAndSwapLong(a, CELLVALUE, v = a.value, v + x))
                break;
            else if (counterCells != as || n >= NCPU)
                collide = false;            // At max size or stale
            else if (!collide)
                collide = true;
            // 如果没有其他线程操作 并且原子操作成功（相当于上锁）
            else if (cellsBusy == 0 && U.compareAndSwapInt(this, CELLSBUSY, 0, 1)) {
                try {
                    if (counterCells == as) {// 检查计数器数组有没有被修改过
                        CounterCell[] rs = new CounterCell[n << 1];
                        for (int i = 0; i < n; ++i)
                            rs[i] = as[i];
                        counterCells = rs;
                    }
                } finally {
                    cellsBusy = 0;// 置为0（相当于释放锁）
                }
                collide = false;
                continue;                   // Retry with expanded table
            }
            h = ThreadLocalRandom.advanceProbe(h);
        }
        // 如果数组没有被修改并且上锁成功 此分支成立
        else if (cellsBusy == 0 && counterCells == as &&  U.compareAndSwapInt(this, CELLSBUSY, 0, 1)) {
            boolean init = false;
            try {                           // Initialize table
                if (counterCells == as) {// 再次判断
                    CounterCell[] rs = new CounterCell[2];
                    rs[h & 1] = new CounterCell(x);
                    counterCells = rs;
                    init = true;
                }
            } finally {
                cellsBusy = 0;// 置为0（相当于释放锁）
            }
            if (init)
                break;
        }
        // 如果对计数器+1成功则跳出循环
        else if (U.compareAndSwapLong(this, BASECOUNT, v = baseCount, v + x))
            break;                          // Fall back on using base
    }
```
**大致执行步骤：**
1. 对`node`的数据进行统计，如果需要扩容则扩容；
2. 对`node`元素`+1`成功之后（使用`fullAddCount`方法`CAS`操作保证并发安全）计算出当前的`node`元素个数；
3. 判断当前元素个数是否达到扩容阈值，如果是则进行扩容；

##### 4.1.3 treeifyBin()方法
这个方法用于将过长的`链表`转换为`TreeBin`对象 **（上述笔记put方法第3.5.1步）** 。但是他并不是直接转换，而是进行一次容量判断：
- 如果容量没有达到转换的要求，直接进行扩容操作并返回（判断`table`的长度是否大于`MIN_TREEIFY_CAPACITY(64)`）
- 如果满足条件才链表的结构抓换为`TreeBin`。

这与`HashMap`不同的是，它并没有把`TreeNode`直接放入 **红黑树** ，而是利用了`TreeBin`这个小容器来封装所有的`TreeNode`。
```java
/**
 * Replaces all linked nodes in bin at given index unless table is
 * too small, in which case resizes instead.
 * 在给定索引处替换 bin 中的所有链接节点，除非表太小，在这种情况下调整大小。
 */
private final void treeifyBin(Node<K,V>[] tab, int index) {
    Node<K,V> b; int n, sc;
    if (tab != null) {
        if ((n = tab.length) < MIN_TREEIFY_CAPACITY)//如果table.length<64 就扩大一倍 返回
            tryPresize(n << 1);
        else if ((b = tabAt(tab, index)) != null && b.hash >= 0) {
            synchronized (b) {
                if (tabAt(tab, index) == b) {
                    TreeNode<K,V> hd = null, tl = null;
                    //构造了一个TreeBin对象 把所有Node节点包装成TreeNode放进去
                    for (Node<K,V> e = b; e != null; e = e.next) {
                        TreeNode<K,V> p =
                            new TreeNode<K,V>(e.hash, e.key, e.val,
                                              null, null);//这里只是利用了TreeNode封装 而没有利用TreeNode的next域和parent域
                        if ((p.prev = tl) == null)
                            hd = p;
                        else
                            tl.next = p;
                        tl = p;
                    }
                    //在原来index的位置 用TreeBin替换掉原来的Node对象
                    setTabAt(tab, index, new TreeBin<K,V>(hd));
                }
            }
        }
    }
}
```

#### 4.2 get
```java
public V get(Object key) {
    Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
    // 1. 获取 key 所在的 hash 位置
    int h = spread(key.hashCode());
    // 2. 如果该下标下的元素不为null
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (e = tabAt(tab, (n - 1) & h)) != null) {
        // 2.1 在头节点找到了key相同的Node，则返回node的value值即可
        if ((eh = e.hash) == h) {
            if ((ek = e.key) == key || (ek != null && key.equals(ek)))
                // key hash 值相等，key值相同，直接返回元素 value
                return e.val;
        }
        // 2.2 如果节点的hash值小于0 ，说明正在扩容或者是红黑树，调用find查找key节点的方法
        else if (eh < 0)
            return (p = e.find(h, key)) != null ? p.val : null;
        // 2.3 是链表，遍历查找
        while ((e = e.next) != null) {
            // 找到key对应的val直接返回
            if (e.hash == h &&
                ((ek = e.key) == key || (ek != null && key.equals(ek))))
                return e.val;
        }
    }
    // 3. 如果都没有找到则返回null
    return null;
}
```

#### 4.3 size方法
```java
public int size() {
    // 调用sumCount方法进行计算
    long n = sumCount();
    return ((n < 0L) ? 0 :
            (n > (long)Integer.MAX_VALUE) ? Integer.MAX_VALUE :
            (int)n);
}

final long sumCount() {
    CounterCell[] as = counterCells; CounterCell a;
    long sum = baseCount;
    if (as != null) {
        // 如果单元计数器数组不为空，则遍厉该数组进行统计
        for (int i = 0; i < as.length; ++i) {
            if ((a = as[i]) != null)
                sum += a.value;
        }
    }
    // 最终返回统计结果
    return sum;
}
```
**执行步骤：**
1. 调用`sumCount`方法进行计算
2. 遍厉`CounterCell数组`，把多个线程在`CounterCell数组`中统计的数据进行求和，得到总数

#### 4.4 remove方法
```java
// 根据key删除
public V remove(Object key) {
    return replaceNode(key, null, null);
}

// 根据key和value删除
public boolean remove(Object key, Object value) {
    if (key == null)
        throw new NullPointerException();
    return value != null && replaceNode(key, null, value) != null;
}

/**
 * Implementation for the four public remove/replace methods:
 * Replaces node value with v, conditional upon match of cv if
 * non-null.  If resulting value is null, delete.
 * 四种公共 removereplace 方法的实现：用 v 替换节点值，如果非空，则以 cv 匹配为条件。如果结果值为空，则删除。
 */
final V replaceNode(Object key, V value, Object cv) {
    // 根据key计算出hash值
    int hash = spread(key.hashCode());
    for (Node<K,V>[] tab = table;;) {// 死循环
        Node<K,V> f; int n, i, fh;
        // 如果node数组为空，或者该hash对应的数组下标没有数据则跳出循环，最终返回null
        if (tab == null || (n = tab.length) == 0 || (f = tabAt(tab, i = (n - 1) & hash)) == null)
            break;
        // 如果该集合当前正在进行扩容数据迁移则帮助迁移，完成后得到新的node数组数据
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);
        else {
            V oldVal = null;
            boolean validated = false;
            // 对hash下标的头元素进行加锁
            synchronized (f) {
                // 在同步代码块中再次判断头元素是否被修改
                if (tabAt(tab, i) == f) {
                    if (fh >= 0) { // 如果是链表
                        // 遍厉该链表找到需要删除的元素，记录旧值，维护链表结构
                        validated = true;
                        for (Node<K,V> e = f, pred = null;;) {
                            K ek;
                            if (e.hash == hash && ((ek = e.key) == key || (ek != null && key.equals(ek)))) {
                                V ev = e.val;
                                if (cv == null || cv == ev ||
                                    (ev != null && cv.equals(ev))) {
                                    oldVal = ev;
                                    if (value != null)
                                        e.val = value;
                                    else if (pred != null)
                                        pred.next = e.next;
                                    else
                                        setTabAt(tab, i, e.next);
                                }
                                break;
                            }
                            pred = e;
                            if ((e = e.next) == null)
                                break;
                        }
                    }
                    // 如果是红黑树，则调用findTreeNode查找元素，记录旧值
                    // 如果删除数据后node数量小于8则恢复为链表结构
                    else if (f instanceof TreeBin) {
                        validated = true;
                        TreeBin<K,V> t = (TreeBin<K,V>)f;
                        TreeNode<K,V> r, p;
                        if ((r = t.root) != null &&
                            (p = r.findTreeNode(hash, key, null)) != null) {
                            V pv = p.val;
                            if (cv == null || cv == pv ||
                                (pv != null && cv.equals(pv))) {
                                oldVal = pv;
                                if (value != null)
                                    p.val = value;
                                else if (t.removeTreeNode(p))
                                    setTabAt(tab, i, untreeify(t.first));
                            }
                        }
                    }
                }
            }
            // 该key对应的元素存在
            if (validated) {
                if (oldVal != null) {
                    if (value == null)
                        // 对统计数减一
                        addCount(-1L, -1);
                    return oldVal;
                }
                break;
            }
        }
    }
    return null;
}
```
**执行步骤：**
1. 根据`key`找到`Node数组`对应下标的头元素（如果没有找到则直接返回`null`）；
2. 对该头元素加锁保证并发安全；
3. 从链表或者 **红黑树** 中找到该`key`的`node`数据，记录数据后删除，然后维护 **链表** 或者 **红黑树** 结构；
4. 如果 **红黑树** 在删除了一个节点之后`node`数量小于`8`，则把 **红黑树** 转为 **链表** ；
5. 如果删除成功，需要对计数器进行`-1`操作；
6. 最后返回被删除的值。

#### 4.5 三个核心方法（tabAt、casTabAt、setTabAt）
`ConcurrentHashMap`定义了三个原子操作，用于对指定位置的节点进行操作。 **正是这些原子操作保证了`ConcurrentHashMap`的线程安全。**
```java
@SuppressWarnings("unchecked")
//获得在i位置上的Node节点
static final <K,V> Node<K,V> tabAt(Node<K,V>[] tab, int i) {
    return (Node<K,V>)U.getObjectVolatile(tab, ((long)i << ASHIFT) + ABASE);
}

//利用CAS算法设置i位置上的Node节点。之所以能实现并发是因为他指定了原来这个节点的值是多少
//在CAS算法中，会比较内存中的值与你指定的这个值是否相等，如果相等才接受你的修改，否则拒绝你的修改
//因此当前线程中的值并不是最新的值，这种修改可能会覆盖掉其他线程的修改结果  有点类似于SVN
static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i,
                                    Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}

//利用volatile方法设置节点位置的值
static final <K,V> void setTabAt(Node<K,V>[] tab, int i, Node<K,V> v) {
    U.putObjectVolatile(tab, ((long)i << ASHIFT) + ABASE, v);
}
```

## 三、 补充：HashMap 线程不安全的典型表现
`JDK1.7`在并发情况下使用 `HashMap` 时（ **头插法** 插入数据），程序经常占了 `100%` 的 `CPU`，查看堆栈，会发现程序都 `Hang` 在了 `“HashMap.get()”` 这个方法上了，重启程序后问题消失。具体分析可以查看这篇文章：[疫苗：JAVA HASHMAP的死循环](https://coolshell.cn/articles/9606.html)，有人将这个问题当成一个 `bug` 提给了 `Sun`，但是 `Sun` 认为这并不是个 `bug`，**因为`HashMap` 本来就不保证并发的线程安全性，在并发下，要用 `ConcurrentHashMap` 来代替**。

**下面进行HashMap死循环分析：**  
`HashMap`是一个`数组+链表`（JDK1.8之前，JDK1.8之后结构改为`数组+链表+红黑树`）的结构，当一个`key/value对`被加入时，首先会通过`Hash`算法定位出这个键值对要被放入的桶，然后就把它插到相应桶中。如果这个桶中已经有元素了，那么发生了碰撞，这样会在这个桶中形成一个链表。

一般来说，当有数据要插入`HashMap`时，都会检查容量有没有超过设定的`thredhold（扩容阈值）`，如果超过，需要增大`HashMap`的尺寸（扩容），但是这样一来，就需要对整个`HashMap`里的节点进行重哈希操作。在重哈希的过程中，就会出现`HashMap`线程不安全的典型表现 ———— 死循环。

`HashMap`重哈希的关键源码如下：
```java
/**
 * Transfers all entries from current table to newTable.
 */
void transfer(Entry[] newTable) {
    // 将原数组 table 赋给数组 src
    Entry[] src = table;
    int newCapacity = newTable.length;
    // 将数组 src 中的每条链重新添加到 newTable 中
    for (int j = 0; j < src.length; j++) {
        Entry<K, V> e = src[j];
        if (e != null) {
            src[j] = null;   // src 回收
            // 将每条链的每个元素依次添加到 newTable 中相应的桶中
            do {
                Entry<K, V> next = e.next;
                // e.hash指的是 hash(key.hashCode())的返回值;
                // 计算在newTable中的位置，注意原来在同一条子链上的元素可能被分配到不同的桶中
                int i = indexFor(e.hash, newCapacity);
                e.next = newTable[i];
                newTable[i] = e;
                e = next;
            } while (e != null);
        }
    }
}
```
### 1. 单线程环境下的重哈希过程演示：
单线程情况下，`rehash` 不会出现任何问题，步骤如下图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/HashMap单线程扩容演示.png)
</center>

假设`hash`算法就是最简单的 `key mod table.length`（也就是和桶的个数取模）。最上面的是`old hash表`，其中的`Hash表桶`的个数为`2`，所以对于 `key = 3、7、5` 的键值对在 `mod 2`以后都冲突在`table[1]`这里了。  
接下来的三个步骤是，`Hash`表`resize`成`4` **（原容量的2倍）** ，然后对所有的键值对重哈希的过程。

**<font color='red'>头插法设计思想：局部性原理，HashMap采用头插法而没有采用尾插法有一点考虑是性能优化，认为最近put进去的元素，被get的概率相对较其他元素大，采用头插法能够更快得获取到最近插入的元素。</font>**  
**<font color='red'>但头插法的设计有一个特点，就是扩容之后，链表上的元素顺序会反过来，这也是死循环的一个重要原因。</font>**

### 2. 多线程环境下的重哈希过程演示：
假设有两个线程，分别用 **紫色** 和 **蓝色** 标注不同的线程扩容后的`HashMap`对象，被这两个线程共享的资源正是要被重哈希的原来`1号桶`中的`Entry链（key = 3、7、5）`。  
再看一下`transfer`方法中的这个细节：
```java
do {
    Entry<K,V> next = e.next;       // <--假设线程一执行到这里就被调度挂起了
    int i = indexFor(e.hash, newCapacity);
    e.next = newTable[i];
    newTable[i] = e;
    e = next;
} while (e != null);
```
假设`线程1`执行到定义`next`处被阻塞挂起，而`线程2`执行完成了，于是`线程2`执行完成之后如下图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/HashMap多线程扩容演示（死循环）1.png)
</center>

注意：在`线程2`重哈希后，`线程1`的`指针e`和`指针next`分别指向了`线程2`重组后的`链表`中的元素**（`e`指向了`key3`，而`next`指向了`key7`）。**   
此时，`线程1`被调度回来继续执行：
1. `线程1`先是执行 `newTalbe[i] = e;`
2. 然后执行 `e = next;`，导致了`e`指向了`key7`；
3. 接下来下一次循环的`next = e.next`导致了`next`指向了`key3`

如下图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/HashMap多线程扩容演示（死循环）2.png)
</center>


这时，`线程1`有条不紊的工作着：把`key7`摘下来，放到`newTable数组`的第一个，然后把`e`和`next`往下移，如下图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/HashMap多线程扩容演示（死循环）3.png)
</center>

在此时，特别需要注意的是，当执行`e.next = newTable[i]`后，会导致 `key3.next` 指向了 `key7`，但是此时的`key7.next` 已经指向了`key3`，环形链表就这样出现了，如下图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/ConcurrentHashMap详解（JDK1.7和JDK1.8）/HashMap多线程扩容演示（死循环）4.png)
</center>

于是，当`线程1`调用`HashMap.get(11)`（说明：`11`是因为假设的取模的方式定位桶的话，`11`对应的桶就是`key3`和`key7`所在的桶）时，就进入了 **`环形链表`** 中一直死循环，因为一直找不到`Key=11`的元素，而又发现一直有 **后继节点** ，所以永远也跳不出循环悲剧就出现了 —— Infinite Loop。

**这是`HashMap`在并发环境下使用中最为典型的一个问题，就是在`HashMap`进行扩容重哈希时导致`Entry链`形成`环形链表`。就会导致在同一个桶中进行`插入`、`查询`、`删除`等操作时陷入`死循环`。**

## 四、总结
- **JDK1.7** 中 `ConcurrentHashMap` 使用的分段锁，也就是每一个 `Segment` 上同时只有一个线程可以操作，每一个 `Segment` 都是一个类似 `HashMap` 数组的结构，它可以扩容，它的冲突会转化为`链表`。 但是 **`Segment` 的个数一但初始化就不能改变。**
- **JDK1.8** 中的 `ConcurrentHashMap` 使用的 `Synchronized` 锁加 `CAS` 的机制。结构也由 `JDK1.7` 中的 **`Segment 数组`+`HashEntry 数组`+`链表`** 进化成了 **`Node 数组`+`链表`/`红黑树`**`，Node` 是类似于一个 `HashEntry` 的结构。  
    **它的冲突再达到一定大小时会转化成 `红黑树`，在冲突小于`UNTREEIFY_THRESHOL(6)`时又退回`链表`。**

**<font color="red">说明：为什么个当冲突的数量小于 6 时才会从红黑树转换为链表，而和链表转换为红黑树时的阈值不一样是 8 呢？这样做是为了避免频繁来回转化。</font>**


**并发级别**
- **JDK1.7** 中使用`segment数组`来控制并发级别（默认为`16`）
- **JDK1.8** 中使用`Node数组`的头几点来作为锁对象，并发级别为`Node数组`的长度，即为`Map集合`的容量。

**数据结构**
- **JDK1.7** 中如果一个`Node`下标对应了多个数据，则这多个数据的数据结构表现为 **`链表`**
- **JDK1.8** 中如果一个`Node`下标对应了多个数据，这多个数据的数量如果`大于等于8`则为 **`红黑树`** ，`小于8`则为 **`数组`** 。

**数据的插入**
- **JDK1.7** 使用头插法，可能会造成循环链表的原因
- **JDK1.8** 使用尾插法

**扩容**
- **JDK1.7** 的扩容是对`segment`对象中的一小段`node数组`进行扩容
- **JDK1.8** 的扩容是对整个`node数组`进行扩容，**同时支持多线程扩容，并且在扩容的时候没有锁死整个node数组，可以支持部分数据的访问。**
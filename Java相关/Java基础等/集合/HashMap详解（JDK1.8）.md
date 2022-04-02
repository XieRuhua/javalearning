# HashMap详解（JDK1.8）
***
[笔记内容参考1：HashMap源码+底层数据结构分析 单](https://snailclimb.gitee.io/javaguide/#/docs/java/collection/hashmap-source-code)  
[笔记内容参考2：史上最详细的 JDK 1.8 HashMap 源码解析述](https://blog.csdn.net/v123411739/article/details/78996181)  
[笔记内容参考3：HashMap 的 7 种遍历方式与性能分析！(强烈推荐)述](https://blog.csdn.net/belongtocode/article/details/106018417)

[toc]
## 一、HashMap简介
**`HashMap` 主要用来存放键值对，它基于哈希表的 `Map` 接口实现，是常用的 `Java` 集合之一，是非线程安全的。**

**`HashMap`可以存储 `null` 的 `key` 和 `value`，但 `null` 作为键只能有一个，`null` 作为值可以有多个。**

`JDK1.8` 之前 `HashMap` 由 `数组+链表` 组成的，数组是 `HashMap` 的主体，链表则是主要为了解决哈希冲突而存在的（“拉链法”解决冲突）。   
`JDK1.8` 以后 `HashMap` 在解决哈希冲突时有了较大的变化，当链表长度大于阈值（默认为 `8`）（将链表转换成红黑树前会判断，如果当前数组的长度小于 `64`，那么会选择先进行数组扩容，而不是转换为`红黑树`）时，将`链表`转化为`红黑树`，以减少搜索时间。

`HashMap` 默认的初始化大小为 `16`。之后每次扩充，容量变为原来的 `2` 倍。并且， `HashMap` 总是使用 `2的幂`作为哈希表的大小。

### 1. HashMap 和 Hashtable、LinkedHashMap、TreeMap 的区别
#### HashTable
`Hashtable`与`HashMap`类似，不同的是：它不允许记录的键或者值为空；它支持线程的同步，即任一时刻只有一个线程能写`Hashtable`，因此也导致了`Hashtable`在写入时会比较慢。  
**几乎不会用到**

#### LinkedHashMap
**`LinkedHashMap`是继承于`HashMap`，是基于`HashMap`和`双向链表`来实现的。**
* `HashMap`无序；`LinkedHashMap`有序，可分为插入顺序和访问顺序两种。如果是访问顺序，那`put`和`get`操作已存在的`Entry`时，都会把`Entry`移动到双向链表的表尾(其实是先删除再插入)。
* `LinkedHashMap`存取数据，还是跟`HashMap`一样使用的`Entry[]`的方式，双向链表只是为了保证顺序。
* `LinkedHashMap`输出时元素是有顺序的，而`HashMap`输出时是随机的。
* `LinkedHashMap`和`HashMap`都是线程不安全的。

#### TreeMap
**`TreeMap`基于`红黑二叉树`的`NavigableMap`的实现，`TreeMap`是`SortedSet`接口的一个实现类。**
* `TreeMap`是线程不安全的。
* `key`不允许`null`且不可以重复，`value`允许重复。
* **存入`TreeMap`的元素应当实现`Comparable接口`或者实现 `Comparator接口`** ，会按照排序后的顺序迭代元素，两个相比较的`key`不得抛出`classCastException`。  
  主要用于存入元素的时候对元素进行自动排序，迭代输出的时候就按排序顺序输出
* 在遍历的时候会比`HashMap`慢，`TreeMap`能够把它保存的记录根据键排序，默认是按升序排序，也可以指定排序的比较器。当用`Iterator`遍历`TreeMap`时，得到的记录是排过序的。

## 二、HashMap (JDK 1.8)核心源码解读（注释）
```java
package java.util;

import sun.misc.SharedSecrets;

import java.io.IOException;
import java.io.InvalidObjectException;
import java.io.Serializable;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * HashMap是常用的Java集合之一，是基于哈希表的Map接口的实现。与HashTable主要区别为不支持同步和允许null作为key和value。
 * HashMap非线程安全，即任一时刻可以有多个线程同时写HashMap，可能会导致数据的不一致。
 * 如果需要满足线程安全，可以用 Collections的synchronizedMap方法使HashMap具有线程安全的能力，或者使用ConcurrentHashMap。
 * 在JDK1.6中，HashMap采用数组+链表实现，即使用链表处理冲突，同一hash值的链表都存储在一个链表里。
 * 但是当位于一个数组中的元素较多，即hash值相等的元素较多时，通过key值依次查找的效率较低。
 * 而JDK1.8中，HashMap采用数组+链表+红黑树实现，当链表长度超过阈值8时，将链表转换为红黑树，这样大大减少了查找时间。
 * 原本Map.Entry接口的实现类Entry改名为了Node。转化为红黑树时改用另一种实现TreeNode。
 */
public class HashMap<K, V> extends AbstractMap<K, V>
        implements Map<K, V>, Cloneable, Serializable {

    private static final long serialVersionUID = 362498820763181265L;


    /**
     * 默认的初始容量（容量为HashMap中槽的数目）是16，且实际容量必须是2的整数次幂。
     */
    static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; // aka 16

    /**
     * 最大容量（必须是2的幂且小于2的30次方，传入容量过大将被这个值替换）
     */
    static final int MAXIMUM_CAPACITY = 1 << 30;

    /**
     * 默认装填因子0.75，如果当前键值对个数 >= HashMap最大容量*装填因子，进行rehash操作
     */
    static final float DEFAULT_LOAD_FACTOR = 0.75f;

    /**
     * JDK1.8 新加，Entry链表最大长度，当桶中节点数目大于该长度时，将链表转成红黑树存储；
     */
    static final int TREEIFY_THRESHOLD = 8;

    /**
     * JDK1.8 新加，当桶中节点数小于该长度，将红黑树转为链表存储；
     */
    static final int UNTREEIFY_THRESHOLD = 6;

    /**
     * 桶可能被转化为树形结构的最小容量。当哈希表的大小超过这个阈值，才会把链式结构转化成树型结构，否则仅采取扩容来尝试减少冲突。
     * 应该至少4*TREEIFY_THRESHOLD来避免扩容和树形结构化之间的冲突。
     */
    static final int MIN_TREEIFY_CAPACITY = 64;

    /**
     * JDK1.6用Entry描述键值对，JDK1.8中用Node代替Entry
     */
    static class Node<K, V> implements Map.Entry<K, V> {
        // hash存储key的hashCode
        final int hash;
        // final:一个键值对的key不可改变
        final K key;
        V value;
        //指向下个节点的引用
        Node<K, V> next;

        //构造函数
        Node(int hash, K key, V value, Node<K, V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }

        public final K getKey() {
            return key;
        }

        public final V getValue() {
            return value;
        }

        public final String toString() {
            return key + "=" + value;
        }

        public final int hashCode() {
            return Objects.hashCode(key) ^ Objects.hashCode(value);
        }

        public final V setValue(V newValue) {
            V oldValue = value;
            value = newValue;
            return oldValue;
        }

        public final boolean equals(Object o) {
            if (o == this)
                return true;
            if (o instanceof Map.Entry) {
                Map.Entry<?, ?> e = (Map.Entry<?, ?>) o;
                if (Objects.equals(key, e.getKey()) &&
                        Objects.equals(value, e.getValue()))
                    return true;
            }
            return false;
        }
    }

    /* ---------------- Static utilities -------------- */

    /**
     * HashMap中键值对的存储形式为链表节点，hashCode相同的节点（位于同一个桶）用链表组织
     * hash方法分为三步:
     * 1.取key的hashCode
     * 2.key的hashCode高16位异或低16位
     * 3.将第一步和第二步得到的结果进行取模运算。
     */
    static final int hash(Object key) {
        int h;
        //计算key的hashCode, h = Objects.hashCode(key)
        //h >>> 16表示对h无符号右移16位，高位补0，然后h与h >>> 16按位异或
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }

    /**
     * 如果参数x实现了Comparable接口，返回参数x的类名，否则返回null
     */
    static Class<?> comparableClassFor(Object x) {
        if (x instanceof Comparable) {
            Class<?> c;
            Type[] ts, as;
            Type t;
            ParameterizedType p;
            if ((c = x.getClass()) == String.class) // bypass checks
                return c;
            if ((ts = c.getGenericInterfaces()) != null) {
                for (int i = 0; i < ts.length; ++i) {
                    if (((t = ts[i]) instanceof ParameterizedType) &&
                            ((p = (ParameterizedType) t).getRawType() ==
                                    Comparable.class) &&
                            (as = p.getActualTypeArguments()) != null &&
                            as.length == 1 && as[0] == c) // type arg is c
                        return c;
                }
            }
        }
        return null;
    }

    /**
     * 如果x的类型为kc，则返回k.compareTo(x)，否则返回0
     */
    @SuppressWarnings({"rawtypes", "unchecked"}) // for cast to Comparable
    static int compareComparables(Class<?> kc, Object k, Object x) {
        return (x == null || x.getClass() != kc ? 0 :
                ((Comparable) k).compareTo(x));
    }

    /**
     * 结果为>=cap的最小2的自然数幂
     */
    static final int tableSizeFor(int cap) {
        //先移位再或运算，最终保证返回值是2的整数幂
        int n = cap - 1;
        n |= n >>> 1;
        n |= n >>> 2;
        n |= n >>> 4;
        n |= n >>> 8;
        n |= n >>> 16;
        return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
    }

    /* ---------------- Fields -------------- */

    /**
     * 哈希桶数组，分配的时候，table的长度总是2的幂
     */
    transient Node<K, V>[] table;

    /**
     * HashMap将数据转换成set的另一种存储形式，这个变量主要用于迭代功能
     */
    transient Set<Map.Entry<K, V>> entrySet;

    /**
     * 实际存储的数量，则HashMap的size()方法，实际返回的就是这个值，isEmpty()也是判断该值是否为0
     */
    transient int size;

    /**
     * hashmap结构被改变的次数，fail-fast机制
     */
    transient int modCount;

    /**
     * HashMap的扩容阈值，在HashMap中存储的Node键值对超过这个数量时，自动扩容容量为原来的二倍
     *
     * @serial
     */
    int threshold;

    /**
     * HashMap的负加载因子，可计算出当前table长度下的扩容阈值：threshold = loadFactor * table.length
     *
     * @serial
     */
    final float loadFactor;

    /* ---------------- Public operations -------------- */

    /**
     * 使用指定的初始化容量initial capacity 和加载因子load factor构造一个空HashMap
     *
     * @param initialCapacity 初始化容量
     * @param loadFactor      加载因子
     * @throws IllegalArgumentException 如果指定的初始化容量为负数或者加载因子为非正数
     */
    public HashMap(int initialCapacity, float loadFactor) {
        if (initialCapacity < 0)
            throw new IllegalArgumentException("Illegal initial capacity: " +
                    initialCapacity);
        if (initialCapacity > MAXIMUM_CAPACITY)
            initialCapacity = MAXIMUM_CAPACITY;
        if (loadFactor <= 0 || Float.isNaN(loadFactor))
            throw new IllegalArgumentException("Illegal load factor: " +
                    loadFactor);
        this.loadFactor = loadFactor;
        this.threshold = tableSizeFor(initialCapacity);
    }

    /**
     * 使用指定的初始化容量initial capacity和默认加载因子DEFAULT_LOAD_FACTOR（0.75）构造一个空HashMap
     *
     * @param initialCapacity 初始化容量
     * @throws IllegalArgumentException 如果指定的初始化容量为负数
     */
    public HashMap(int initialCapacity) {
        this(initialCapacity, DEFAULT_LOAD_FACTOR);
    }

    /**
     * 使用指定的初始化容量（16）和默认加载因子DEFAULT_LOAD_FACTOR（0.75）构造一个空HashMap
     */
    public HashMap() {
        this.loadFactor = DEFAULT_LOAD_FACTOR; // all other fields defaulted
    }

    /**
     * 使用指定Map m构造新的HashMap。使用指定的初始化容量（16）和默认加载因子DEFAULT_LOAD_FACTOR（0.75）
     *
     * @param m 指定的map
     * @throws NullPointerException 如果指定的map是null
     */
    public HashMap(Map<? extends K, ? extends V> m) {
        this.loadFactor = DEFAULT_LOAD_FACTOR;
        putMapEntries(m, false);
    }

    /**
     * Map.putAll and Map constructor的实现需要的方法
     * 将m的键值对插入本map中
     *
     * @param m     指定的map
     * @param evict 初始化map时使用false，否则使用true
     */
    final void putMapEntries(Map<? extends K, ? extends V> m, boolean evict) {
        int s = m.size();
        //如果参数map不为空
        if (s > 0) {
            // 判断table是否已经初始化
            if (table == null) { // pre-size
                // 未初始化，s为m的实际元素个数
                float ft = ((float) s / loadFactor) + 1.0F;
                int t = ((ft < (float) MAXIMUM_CAPACITY) ?
                        (int) ft : MAXIMUM_CAPACITY);
                // 计算得到的t大于阈值，则初始化阈值
                if (t > threshold)
                    //根据容量初始化临界值
                    threshold = tableSizeFor(t);
                // 已初始化，并且m元素个数大于阈值，进行扩容处理
            } else if (s > threshold)
                //扩容处理
                resize();
            // 将m中的所有元素添加至HashMap中
            for (Map.Entry<? extends K, ? extends V> e : m.entrySet()) {
                K key = e.getKey();
                V value = e.getValue();
                putVal(hash(key), key, value, false, evict);
            }
        }
    }

    /**
     * 返回map中键值对映射的个数
     *
     * @return map中键值对映射的个数
     */
    public int size() {
        return size;
    }

    /**
     * 如果map中没有键值对映射，返回true
     *
     * @return 如果map中没有键值对映射，返回true
     */
    public boolean isEmpty() {
        return size == 0;
    }

    /**
     * 返回指定的key映射的value，如果value为null，则返回null
     * get可以分为三个步骤：
     * 1.通过hash(Object key)方法计算key的哈希值hash。
     * 2.通过getNode( int hash, Object key)方法获取node。
     * 3.如果node为null，返回null，否则返回node.value。
     *
     * @see #put(Object, Object)
     */
    public V get(Object key) {
        Node<K, V> e;
        //根据key及其hash值查询node节点，如果存在，则返回该节点的value值
        return (e = getNode(hash(key), key)) == null ? null : e.value;
    }

    /**
     * 根据key的哈希值和key获取对应的节点
     * getNode可分为以下几个步骤：
     * 1.如果哈希表为空，或key对应的桶为空，返回null
     * 2.如果桶中的第一个节点就和指定参数hash和key匹配上了，返回这个节点。
     * 3.如果桶中的第一个节点没有匹配上，而且有后续节点
     * 3.1如果当前的桶采用红黑树，则调用红黑树的get方法去获取节点
     * 3.2如果当前的桶不采用红黑树，即桶中节点结构为链式结构，遍历链表，直到key匹配
     * 4.找到节点返回null，否则返回null。
     *
     * @param hash 指定参数key的哈希值
     * @param key  指定参数key
     * @return 返回node，如果没有则返回null
     */
    final Node<K, V> getNode(int hash, Object key) {
        Node<K, V>[] tab;
        Node<K, V> first, e;
        int n;
        K k;
        //如果哈希表不为空，而且key对应的桶上不为空
        if ((tab = table) != null && (n = tab.length) > 0 &&
                (first = tab[(n - 1) & hash]) != null) {
            //如果桶中的第一个节点就和指定参数hash和key匹配上了
            if (first.hash == hash && // always check first node
                    ((k = first.key) == key || (key != null && key.equals(k))))
                //返回桶中的第一个节点
                return first;
            //如果桶中的第一个节点没有匹配上，而且有后续节点
            if ((e = first.next) != null) {
                //如果当前的桶采用红黑树，则调用红黑树的get方法去获取节点
                if (first instanceof TreeNode)
                    return ((TreeNode<K, V>) first).getTreeNode(hash, key);
                //如果当前的桶不采用红黑树，即桶中节点结构为链式结构
                do {
                    //遍历链表，直到key匹配
                    if (e.hash == hash &&
                            ((k = e.key) == key || (key != null && key.equals(k))))
                        return e;
                } while ((e = e.next) != null);
            }
        }
        //如果哈希表为空，或者没有找到节点，返回null
        return null;
    }

    /**
     * 如果map中含有key为指定参数key的键值对，返回true
     *
     * @param key 指定参数key
     * @return 如果map中含有key为指定参数key的键值对，返回true
     * key.
     */
    public boolean containsKey(Object key) {
        return getNode(hash(key), key) != null;
    }

    /**
     * 将指定参数key和指定参数value插入map中，如果key已经存在，那就替换key对应的value
     * put(K key, V value)可以分为三个步骤：
     * 1.通过hash(Object key)方法计算key的哈希值。
     * 2.通过putVal(hash(key), key, value, false, true)方法实现功能。
     * 3.返回putVal方法返回的结果。
     *
     * @param key   指定key
     * @param value 指定value
     * @return 如果value被替换，则返回旧的value，否则返回null。当然，可能key对应的value就是null
     */
    public V put(K key, V value) {
        // 倒数第二个参数false：表示允许旧值替换
        // 最后一个参数true：表示HashMap不处于创建模式
        return putVal(hash(key), key, value, false, true);
    }

    /**
     * Map.put和其他相关方法的实现需要的方法
     * putVal方法可以分为下面的几个步骤:
     * 1.如果哈希表为空，调用resize()创建一个哈希表。
     * 2.如果指定参数hash在表中没有对应的桶，即为没有碰撞，直接将键值对插入到哈希表中即可。
     * 3.如果有碰撞，遍历桶，找到key映射的节点
     * 3.1桶中的第一个节点就匹配了，将桶中的第一个节点记录起来。
     * 3.2如果桶中的第一个节点没有匹配，且桶中结构为红黑树，则调用红黑树对应的方法插入键值对。
     * 3.3如果不是红黑树，那么就肯定是链表。遍历链表，如果找到了key映射的节点，就记录这个节点，退出循环。如果没有找到，在链表尾部插入节点。插入后，如果链的长度大于TREEIFY_THRESHOLD这个临界值，则使用treeifyBin方法把链表转为红黑树。
     * 4.如果找到了key映射的节点，且节点不为null
     * 4.1记录节点的vlaue。
     * 4.2如果参数onlyIfAbsent为false，或者oldValue为null，替换value，否则不替换。
     * 4.3返回记录下来的节点的value。
     * 5.如果没有找到key映射的节点（2、3步中讲了，这种情况会插入到hashMap中），插入节点后size会加1，这时要检查size是否大于临界值threshold，如果大于会使用resize方法进行扩容。
     *
     * @param hash         指定参数key的哈希值
     * @param key          指定参数key
     * @param value        指定参数value
     * @param onlyIfAbsent 如果为true，即使指定参数key在map中已经存在，也不会替换value
     * @param evict        如果为false，数组table在创建模式中
     * @return 如果value被替换，则返回旧的value，否则返回null。当然，可能key对应的value就是null。
     */
    final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                   boolean evict) {
        Node<K, V>[] tab;
        Node<K, V> p;
        int n, i;
        //如果哈希表为空，调用resize()创建一个哈希表，并用变量n记录哈希表长度
        if ((tab = table) == null || (n = tab.length) == 0)
            n = (tab = resize()).length;
        /**
         * 如果指定参数hash在表中没有对应的桶，即为没有碰撞
         * Hash函数，(n - 1) & hash 计算key将被放置的槽位
         * (n - 1) & hash 本质上是hash % n，位运算更快
         */
        if ((p = tab[i = (n - 1) & hash]) == null)
            //直接将键值对插入到map中即可
            tab[i] = newNode(hash, key, value, null);
        else {// 桶中已经存在元素
            Node<K, V> e;
            K k;
            // 比较桶中第一个元素(数组中的结点)的hash值相等，key相等
            if (p.hash == hash &&
                    ((k = p.key) == key || (key != null && key.equals(k))))
                // 将第一个元素赋值给e，用e来记录
                e = p;
                // 当前桶中无该键值对，且桶是红黑树结构，按照红黑树结构插入
            else if (p instanceof TreeNode)
                e = ((TreeNode<K, V>) p).putTreeVal(this, tab, hash, key, value);
                // 当前桶中无该键值对，且桶是链表结构，按照链表结构插入到尾部
            else {
                for (int binCount = 0; ; ++binCount) {
                    // 遍历到链表尾部
                    if ((e = p.next) == null) {
                        p.next = newNode(hash, key, value, null);
                        // 检查链表长度是否达到阈值，达到将该槽位节点组织形式转为红黑树
                        if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                            treeifyBin(tab, hash);
                        break;
                    }
                    // 链表节点的<key, value>与put操作<key, value>相同时，不做重复操作，跳出循环
                    if (e.hash == hash &&
                            ((k = e.key) == key || (key != null && key.equals(k))))
                        break;
                    p = e;
                }
            }
            // 找到或新建一个key和hashCode与插入元素相等的键值对，进行put操作
            if (e != null) { // existing mapping for key
                // 记录e的value
                V oldValue = e.value;
                /**
                 * onlyIfAbsent为false或旧值为null时，允许替换旧值
                 * 否则无需替换
                 */
                if (!onlyIfAbsent || oldValue == null)
                    e.value = value;
                // 访问后回调
                afterNodeAccess(e);
                // 返回旧值
                return oldValue;
            }
        }
        // 更新结构化修改信息
        ++modCount;
        // 键值对数目超过阈值时，进行rehash
        if (++size > threshold)
            resize();
        // 插入后回调
        afterNodeInsertion(evict);
        return null;
    }

    /**
     * 对table进行初始化或者扩容。
     * 如果table为null，则对table进行初始化
     * 如果对table扩容，因为每次扩容都是翻倍，与原来计算（n-1）&hash的结果相比，节点要么就在原来的位置，要么就被分配到“原位置+旧容量”这个位置
     * resize的步骤总结为:
     * 1.计算扩容后的容量，临界值。
     * 2.将hashMap的临界值修改为扩容后的临界值
     * 3.根据扩容后的容量新建数组，然后将hashMap的table的引用指向新数组。
     * 4.将旧数组的元素复制到table中。
     *
     * @return the table
     */
    final Node<K, V>[] resize() {
        //新建oldTab数组保存扩容前的数组table
        Node<K, V>[] oldTab = table;
        //获取原来数组的长度
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        //原来数组扩容的临界值
        int oldThr = threshold;
        int newCap, newThr = 0;
        //如果扩容前的容量 > 0
        if (oldCap > 0) {
            //如果原来的数组长度大于最大值(2^30)
            if (oldCap >= MAXIMUM_CAPACITY) {
                //扩容临界值提高到正无穷
                threshold = Integer.MAX_VALUE;
                //无法进行扩容，返回原来的数组
                return oldTab;
                //如果现在容量的两倍小于MAXIMUM_CAPACITY且现在的容量大于DEFAULT_INITIAL_CAPACITY
            } else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                    oldCap >= DEFAULT_INITIAL_CAPACITY)
                //临界值变为原来的2倍
                newThr = oldThr << 1;
        } else if (oldThr > 0) //如果旧容量 <= 0，而且旧临界值 > 0
            //数组的新容量设置为老数组扩容的临界值
            newCap = oldThr;
        else { //如果旧容量 <= 0，且旧临界值 <= 0，新容量扩充为默认初始化容量，新临界值为DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY
            newCap = DEFAULT_INITIAL_CAPACITY;//新数组初始容量设置为默认值
            newThr = (int) (DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);//计算默认容量下的阈值
        }
        // 计算新的resize上限
        if (newThr == 0) {//在当上面的条件判断中，只有oldThr > 0成立时，newThr == 0
            //ft为临时临界值，下面会确定这个临界值是否合法，如果合法，那就是真正的临界值
            float ft = (float) newCap * loadFactor;
            //当新容量< MAXIMUM_CAPACITY且ft < (float)MAXIMUM_CAPACITY，新的临界值为ft，否则为Integer.MAX_VALUE
            newThr = (newCap < MAXIMUM_CAPACITY && ft < (float) MAXIMUM_CAPACITY ?
                    (int) ft : Integer.MAX_VALUE);
        }
        //将扩容后hashMap的临界值设置为newThr
        threshold = newThr;
        //创建新的table，初始化容量为newCap
        @SuppressWarnings({"rawtypes", "unchecked"})
        Node<K, V>[] newTab = (Node<K, V>[]) new Node[newCap];
        //修改hashMap的table为新建的newTab
        table = newTab;
        //如果旧table不为空，将旧table中的元素复制到新的table中
        if (oldTab != null) {
            //遍历旧哈希表的每个桶，将旧哈希表中的桶复制到新的哈希表中
            for (int j = 0; j < oldCap; ++j) {
                Node<K, V> e;
                //如果旧桶不为null，使用e记录旧桶
                if ((e = oldTab[j]) != null) {
                    //将旧桶置为null
                    oldTab[j] = null;
                    //如果旧桶中只有一个node
                    if (e.next == null)
                        //将e也就是oldTab[j]放入newTab中e.hash & (newCap - 1)的位置
                        newTab[e.hash & (newCap - 1)] = e;
                        //如果旧桶中的结构为红黑树
                    else if (e instanceof TreeNode)
                        //将树中的node分离
                        ((TreeNode<K, V>) e).split(this, newTab, j, oldCap);
                    else {  //如果旧桶中的结构为链表,链表重排，jdk1.8做的一系列优化
                        Node<K, V> loHead = null, loTail = null;
                        Node<K, V> hiHead = null, hiTail = null;
                        Node<K, V> next;
                        //遍历整个链表中的节点
                        do {
                            next = e.next;
                            // 原索引
                            if ((e.hash & oldCap) == 0) {
                                if (loTail == null)
                                    loHead = e;
                                else
                                    loTail.next = e;
                                loTail = e;
                            } else {// 原索引+oldCap
                                if (hiTail == null)
                                    hiHead = e;
                                else
                                    hiTail.next = e;
                                hiTail = e;
                            }
                        } while ((e = next) != null);
                        // 原索引放到bucket里
                        if (loTail != null) {
                            loTail.next = null;
                            newTab[j] = loHead;
                        }
                        // 原索引+oldCap放到bucket里
                        if (hiTail != null) {
                            hiTail.next = null;
                            newTab[j + oldCap] = hiHead;
                        }
                    }
                }
            }
        }
        return newTab;
    }

    /**
     * 将链表转化为红黑树
     */
    final void treeifyBin(Node<K, V>[] tab, int hash) {
        int n, index;
        Node<K, V> e;
        //如果桶数组table为空，或者桶数组table的长度小于MIN_TREEIFY_CAPACITY，不符合转化为红黑树的条件
        if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
            //扩容
            resize();
            //如果符合转化为红黑树的条件，而且hash对应的桶不为null
        else if ((e = tab[index = (n - 1) & hash]) != null) {
            // 红黑树的头、尾节点
            TreeNode<K, V> hd = null, tl = null;
            //遍历链表
            do {
                //替换链表node为树node，建立双向链表
                TreeNode<K, V> p = replacementTreeNode(e, null);
                // 确定树头节点
                if (tl == null)
                    hd = p;
                else {
                    p.prev = tl;
                    tl.next = p;
                }
                tl = p;
            } while ((e = e.next) != null);
            //遍历链表插入每个节点到红黑树
            if ((tab[index] = hd) != null)
                hd.treeify(tab);
        }
    }

    /**
     * 将参数map中的所有键值对映射插入到hashMap中，如果有碰撞，则覆盖value。
     *
     * @param m 参数map
     * @throws NullPointerException 如果map为null
     */
    public void putAll(Map<? extends K, ? extends V> m) {
        putMapEntries(m, true);
    }

    /**
     * 删除hashMap中key映射的node
     * remove方法的实现可以分为三个步骤：
     * 1.通过 hash(Object key)方法计算key的哈希值。
     * 2.通过 removeNode 方法实现功能。
     * 3.返回被删除的node的value。
     *
     * @param key 参数key
     * @return 如果没有映射到node，返回null，否则返回对应的value
     */
    public V remove(Object key) {
        Node<K, V> e;
        //根据key来删除node。removeNode方法的具体实现在下面
        return (e = removeNode(hash(key), key, null, false, true)) == null ?
                null : e.value;
    }

    /**
     * Map.remove和相关方法的实现需要的方法
     * removeNode方法的步骤总结为:
     * 1.如果数组table为空或key映射到的桶为空，返回null。
     * 2.如果key映射到的桶上第一个node的就是要删除的node，记录下来。
     * 3.如果桶内不止一个node，且桶内的结构为红黑树，记录key映射到的node。
     * 4.桶内的结构不为红黑树，那么桶内的结构就肯定为链表，遍历链表，找到key映射到的node，记录下来。
     * 5.如果被记录下来的node不为null，删除node，size-1被删除。
     * 6.返回被删除的node。
     *
     * @param hash       key的哈希值
     * @param key        key的哈希值
     * @param value      如果 matchValue 为true，则value也作为确定被删除的node的条件之一，否则忽略
     * @param matchValue 如果为true，则value也作为确定被删除的node的条件之一
     * @param movable    如果为false，删除node时不会删除其他node
     * @return 返回被删除的node，如果没有node被删除，则返回null（针对红黑树的删除方法）
     */
    final Node<K, V> removeNode(int hash, Object key, Object value,
                                boolean matchValue, boolean movable) {
        Node<K, V>[] tab;
        Node<K, V> p;
        int n, index;
        //如果数组table不为空且key映射到的桶不为空
        if ((tab = table) != null && (n = tab.length) > 0 &&
                (p = tab[index = (n - 1) & hash]) != null) {
            Node<K, V> node = null, e;
            K k;
            V v;
            //如果桶上第一个node的就是要删除的node
            if (p.hash == hash &&
                    ((k = p.key) == key || (key != null && key.equals(k))))
                //记录桶上第一个node
                node = p;
            else if ((e = p.next) != null) {//如果桶内不止一个node
                //如果桶内的结构为红黑树
                if (p instanceof TreeNode)
                    //记录key映射到的node
                    node = ((TreeNode<K, V>) p).getTreeNode(hash, key);
                else {//如果桶内的结构为链表
                    do {//遍历链表，找到key映射到的node
                        if (e.hash == hash &&
                                ((k = e.key) == key ||
                                        (key != null && key.equals(k)))) {
                            //记录key映射到的node
                            node = e;
                            break;
                        }
                        p = e;
                    } while ((e = e.next) != null);
                }
            }
            //如果得到的node不为null且(matchValue为false||node.value和参数value匹配)
            if (node != null && (!matchValue || (v = node.value) == value ||
                    (value != null && value.equals(v)))) {
                //如果桶内的结构为红黑树
                if (node instanceof TreeNode)
                    //使用红黑树的删除方法删除node
                    ((TreeNode<K, V>) node).removeTreeNode(this, tab, movable);
                else if (node == p)//如果桶的第一个node的就是要删除的node
                    //删除node
                    tab[index] = node.next;
                else//如果桶内的结构为链表，使用链表删除元素的方式删除node
                    p.next = node.next;
                ++modCount;//结构性修改次数+1
                --size;//哈希表大小-1
                afterNodeRemoval(node);
                return node;//返回被删除的node
            }
        }
        return null;//如果数组table为空或key映射到的桶为空，返回null。
    }

    /**
     * 删除map中所有的键值对
     */
    public void clear() {
        Node<K, V>[] tab;
        modCount++;
        if ((tab = table) != null && size > 0) {
            size = 0;
            for (int i = 0; i < tab.length; ++i)
                tab[i] = null;
        }
    }

    /**
     * 如果hashMap中的键值对有一对或多对的value为参数value，返回true
     *
     * @param value 参数value
     * @return 如果hashMap中的键值对有一对或多对的value为参数value，返回true
     */
    public boolean containsValue(Object value) {
        Node<K, V>[] tab;
        V v;
        if ((tab = table) != null && size > 0) {
            //遍历数组table
            for (int i = 0; i < tab.length; ++i) {
                //遍历桶中的node
                for (Node<K, V> e = tab[i]; e != null; e = e.next) {
                    if ((v = e.value) == value ||
                            (value != null && value.equals(v)))
                        return true;
                }
            }
        }
        return false;
    }

    /**
     * 返回hashMap中所有key的视图。
     * 改变hashMap会影响到set，反之亦然。
     * 如果当迭代器迭代set时，hashMap被修改(除非是迭代器自己的remove()方法)，迭代器的结果是不确定的。
     * set支持元素的删除，通过Iterator.remove、Set.remove、removeAll、retainAll、clear操作删除hashMap中对应的键值对。
     * 不支持add和addAll方法。
     *
     * @return 返回hashMap中所有key的set视图
     */
    public Set<K> keySet() {
        Set<K> ks = keySet;
        if (ks == null) {
            ks = new KeySet();
            keySet = ks;
        }
        return ks;
    }

    /**
     * 内部类KeySet
     */
    final class KeySet extends AbstractSet<K> {
        public final int size() {
            return size;
        }

        public final void clear() {
            HashMap.this.clear();
        }

        public final Iterator<K> iterator() {
            return new KeyIterator();
        }

        public final boolean contains(Object o) {
            return containsKey(o);
        }

        public final boolean remove(Object key) {
            return removeNode(hash(key), key, null, false, true) != null;
        }

        public final Spliterator<K> spliterator() {
            return new KeySpliterator<>(HashMap.this, 0, -1, 0, 0);
        }

        public final void forEach(Consumer<? super K> action) {
            Node<K, V>[] tab;
            if (action == null)
                throw new NullPointerException();
            if (size > 0 && (tab = table) != null) {
                int mc = modCount;
                for (int i = 0; i < tab.length; ++i) {
                    for (Node<K, V> e = tab[i]; e != null; e = e.next)
                        action.accept(e.key);
                }
                if (modCount != mc)
                    throw new ConcurrentModificationException();
            }
        }
    }

    /**
     * 返回hashMap中所有value的collection视图
     * 改变hashMap会改变collection，反之亦然。
     * 如果当迭代器迭代collection时，hashMap被修改（除非是迭代器自己的remove()方法），迭代器的结果是不确定的。
     * collection支持元素的删除，通过Iterator.remove、Collection.remove、removeAll、retainAll、clear操作删除hashMap中对应的键值对。
     * 不支持add和addAll方法。
     *
     * @return 返回hashMap中所有key的collection视图
     */
    public Collection<V> values() {
        Collection<V> vs = values;
        if (vs == null) {
            vs = new Values();
            values = vs;
        }
        return vs;
    }

    /**
     * 内部类Values
     */
    final class Values extends AbstractCollection<V> {
        public final int size() {
            return size;
        }

        public final void clear() {
            HashMap.this.clear();
        }

        public final Iterator<V> iterator() {
            return new ValueIterator();
        }

        public final boolean contains(Object o) {
            return containsValue(o);
        }

        public final Spliterator<V> spliterator() {
            return new ValueSpliterator<>(HashMap.this, 0, -1, 0, 0);
        }

        public final void forEach(Consumer<? super V> action) {
            Node<K, V>[] tab;
            if (action == null)
                throw new NullPointerException();
            if (size > 0 && (tab = table) != null) {
                int mc = modCount;
                for (int i = 0; i < tab.length; ++i) {
                    for (Node<K, V> e = tab[i]; e != null; e = e.next)
                        action.accept(e.value);
                }
                if (modCount != mc)
                    throw new ConcurrentModificationException();
            }
        }
    }

    /**
     * 返回hashMap中所有键值对的set视图
     * 改变hashMap会影响到set，反之亦然。
     * 如果当迭代器迭代set时，hashMap被修改(除非是迭代器自己的remove()方法)，迭代器的结果是不确定的。
     * set支持元素的删除，通过Iterator.remove、Set.remove、removeAll、retainAll、clear操作删除hashMap中对应的键值对。
     * 不支持add和addAll方法。
     *
     * @return 返回hashMap中所有键值对的set视图
     */
    public Set<Map.Entry<K, V>> entrySet() {
        Set<Map.Entry<K, V>> es;
        return (es = entrySet) == null ? (entrySet = new EntrySet()) : es;
    }

    /**
     * 内部类EntrySet
     */
    final class EntrySet extends AbstractSet<Map.Entry<K, V>> {
        public final int size() {
            return size;
        }

        public final void clear() {
            HashMap.this.clear();
        }

        public final Iterator<Map.Entry<K, V>> iterator() {
            return new EntryIterator();
        }

        public final boolean contains(Object o) {
            if (!(o instanceof Map.Entry))
                return false;
            Map.Entry<?, ?> e = (Map.Entry<?, ?>) o;
            Object key = e.getKey();
            Node<K, V> candidate = getNode(hash(key), key);
            return candidate != null && candidate.equals(e);
        }

        public final boolean remove(Object o) {
            if (o instanceof Map.Entry) {
                Map.Entry<?, ?> e = (Map.Entry<?, ?>) o;
                Object key = e.getKey();
                Object value = e.getValue();
                return removeNode(hash(key), key, value, true, true) != null;
            }
            return false;
        }

        public final Spliterator<Map.Entry<K, V>> spliterator() {
            return new EntrySpliterator<>(HashMap.this, 0, -1, 0, 0);
        }

        public final void forEach(Consumer<? super Map.Entry<K, V>> action) {
            Node<K, V>[] tab;
            if (action == null)
                throw new NullPointerException();
            if (size > 0 && (tab = table) != null) {
                int mc = modCount;
                for (int i = 0; i < tab.length; ++i) {
                    for (Node<K, V> e = tab[i]; e != null; e = e.next)
                        action.accept(e);
                }
                if (modCount != mc)
                    throw new ConcurrentModificationException();
            }
        }
    }

    // JDK8重写的方法

    /**
     * 通过key映射到对应node，如果没映射到则返回默认值defaultValue
     *
     * @param key
     * @param defaultValue
     * @return key映射到对应的node，如果没映射到则返回默认值defaultValue
     */
    @Override
    public V getOrDefault(Object key, V defaultValue) {
        Node<K, V> e;
        return (e = getNode(hash(key), key)) == null ? defaultValue : e.value;
    }

    /**
     * 在hashMap中插入参数key和value组成的键值对，如果key在hashMap中已经存在，不替换value
     *
     * @param key
     * @param value
     * @return 如果key在hashMap中不存在，返回旧value
     */
    @Override
    public V putIfAbsent(K key, V value) {
        return putVal(hash(key), key, value, true, true);
    }

    /**
     * 删除hashMap中key为参数key，value为参数value的键值对。如果桶中结构为树，则级联删除
     *
     * @param key
     * @param value
     * @return 删除成功，返回true
     */
    @Override
    public boolean remove(Object key, Object value) {
        return removeNode(hash(key), key, value, true, true) != null;
    }

    /**
     * 使用newValue替换key和oldValue映射到的键值对中的value
     *
     * @param key
     * @param oldValue
     * @param newValue
     * @return 替换成功，返回true
     */
    @Override
    public boolean replace(K key, V oldValue, V newValue) {
        Node<K, V> e;
        V v;
        if ((e = getNode(hash(key), key)) != null &&
                ((v = e.value) == oldValue || (v != null && v.equals(oldValue)))) {
            e.value = newValue;
            afterNodeAccess(e);
            return true;
        }
        return false;
    }

    /**
     * 使用参数value替换key映射到的键值对中的value
     *
     * @param key
     * @param value
     * @return 替换成功，返回true
     */
    @Override
    public V replace(K key, V value) {
        Node<K, V> e;
        if ((e = getNode(hash(key), key)) != null) {
            V oldValue = e.value;
            e.value = value;
            afterNodeAccess(e);
            return oldValue;
        }
        return null;
    }

    @Override
    public V computeIfAbsent(K key,
                             Function<? super K, ? extends V> mappingFunction) {
        if (mappingFunction == null)
            throw new NullPointerException();
        int hash = hash(key);
        Node<K, V>[] tab;
        Node<K, V> first;
        int n, i;
        int binCount = 0;
        TreeNode<K, V> t = null;
        Node<K, V> old = null;
        if (size > threshold || (tab = table) == null ||
                (n = tab.length) == 0)
            n = (tab = resize()).length;
        if ((first = tab[i = (n - 1) & hash]) != null) {
            if (first instanceof TreeNode)
                old = (t = (TreeNode<K, V>) first).getTreeNode(hash, key);
            else {
                Node<K, V> e = first;
                K k;
                do {
                    if (e.hash == hash &&
                            ((k = e.key) == key || (key != null && key.equals(k)))) {
                        old = e;
                        break;
                    }
                    ++binCount;
                } while ((e = e.next) != null);
            }
            V oldValue;
            if (old != null && (oldValue = old.value) != null) {
                afterNodeAccess(old);
                return oldValue;
            }
        }
        V v = mappingFunction.apply(key);
        if (v == null) {
            return null;
        } else if (old != null) {
            old.value = v;
            afterNodeAccess(old);
            return v;
        } else if (t != null)
            t.putTreeVal(this, tab, hash, key, v);
        else {
            tab[i] = newNode(hash, key, v, first);
            if (binCount >= TREEIFY_THRESHOLD - 1)
                treeifyBin(tab, hash);
        }
        ++modCount;
        ++size;
        afterNodeInsertion(true);
        return v;
    }

    public V computeIfPresent(K key,
                              BiFunction<? super K, ? super V, ? extends V> remappingFunction) {
        if (remappingFunction == null)
            throw new NullPointerException();
        Node<K, V> e;
        V oldValue;
        int hash = hash(key);
        if ((e = getNode(hash, key)) != null &&
                (oldValue = e.value) != null) {
            V v = remappingFunction.apply(key, oldValue);
            if (v != null) {
                e.value = v;
                afterNodeAccess(e);
                return v;
            } else
                removeNode(hash, key, null, false, true);
        }
        return null;
    }

    @Override
    public V compute(K key,
                     BiFunction<? super K, ? super V, ? extends V> remappingFunction) {
        if (remappingFunction == null)
            throw new NullPointerException();
        int hash = hash(key);
        Node<K, V>[] tab;
        Node<K, V> first;
        int n, i;
        int binCount = 0;
        TreeNode<K, V> t = null;
        Node<K, V> old = null;
        if (size > threshold || (tab = table) == null ||
                (n = tab.length) == 0)
            n = (tab = resize()).length;
        if ((first = tab[i = (n - 1) & hash]) != null) {
            if (first instanceof TreeNode)
                old = (t = (TreeNode<K, V>) first).getTreeNode(hash, key);
            else {
                Node<K, V> e = first;
                K k;
                do {
                    if (e.hash == hash &&
                            ((k = e.key) == key || (key != null && key.equals(k)))) {
                        old = e;
                        break;
                    }
                    ++binCount;
                } while ((e = e.next) != null);
            }
        }
        V oldValue = (old == null) ? null : old.value;
        V v = remappingFunction.apply(key, oldValue);
        if (old != null) {
            if (v != null) {
                old.value = v;
                afterNodeAccess(old);
            } else
                removeNode(hash, key, null, false, true);
        } else if (v != null) {
            if (t != null)
                t.putTreeVal(this, tab, hash, key, v);
            else {
                tab[i] = newNode(hash, key, v, first);
                if (binCount >= TREEIFY_THRESHOLD - 1)
                    treeifyBin(tab, hash);
            }
            ++modCount;
            ++size;
            afterNodeInsertion(true);
        }
        return v;
    }

    @Override
    public V merge(K key, V value,
                   BiFunction<? super V, ? super V, ? extends V> remappingFunction) {
        if (value == null)
            throw new NullPointerException();
        if (remappingFunction == null)
            throw new NullPointerException();
        int hash = hash(key);
        Node<K, V>[] tab;
        Node<K, V> first;
        int n, i;
        int binCount = 0;
        TreeNode<K, V> t = null;
        Node<K, V> old = null;
        if (size > threshold || (tab = table) == null ||
                (n = tab.length) == 0)
            n = (tab = resize()).length;
        if ((first = tab[i = (n - 1) & hash]) != null) {
            if (first instanceof TreeNode)
                old = (t = (TreeNode<K, V>) first).getTreeNode(hash, key);
            else {
                Node<K, V> e = first;
                K k;
                do {
                    if (e.hash == hash &&
                            ((k = e.key) == key || (key != null && key.equals(k)))) {
                        old = e;
                        break;
                    }
                    ++binCount;
                } while ((e = e.next) != null);
            }
        }
        if (old != null) {
            V v;
            if (old.value != null)
                v = remappingFunction.apply(old.value, value);
            else
                v = value;
            if (v != null) {
                old.value = v;
                afterNodeAccess(old);
            } else
                removeNode(hash, key, null, false, true);
            return v;
        }
        if (value != null) {
            if (t != null)
                t.putTreeVal(this, tab, hash, key, value);
            else {
                tab[i] = newNode(hash, key, value, first);
                if (binCount >= TREEIFY_THRESHOLD - 1)
                    treeifyBin(tab, hash);
            }
            ++modCount;
            ++size;
            afterNodeInsertion(true);
        }
        return value;
    }

    @Override
    public void forEach(BiConsumer<? super K, ? super V> action) {
        Node<K, V>[] tab;
        if (action == null)
            throw new NullPointerException();
        if (size > 0 && (tab = table) != null) {
            int mc = modCount;
            for (int i = 0; i < tab.length; ++i) {
                for (Node<K, V> e = tab[i]; e != null; e = e.next)
                    action.accept(e.key, e.value);
            }
            if (modCount != mc)
                throw new ConcurrentModificationException();
        }
    }

    @Override
    public void replaceAll(BiFunction<? super K, ? super V, ? extends V> function) {
        Node<K, V>[] tab;
        if (function == null)
            throw new NullPointerException();
        if (size > 0 && (tab = table) != null) {
            int mc = modCount;
            for (int i = 0; i < tab.length; ++i) {
                for (Node<K, V> e = tab[i]; e != null; e = e.next) {
                    e.value = function.apply(e.key, e.value);
                }
            }
            if (modCount != mc)
                throw new ConcurrentModificationException();
        }
    }

    /* ------------------------------------------------------------ */
    // 克隆和序列化

    /**
     * 浅拷贝。
     * clone方法虽然生成了新的HashMap对象，新的HashMap中的table数组虽然也是新生成的，但是数组中的元素还是引用以前的HashMap中的元素。
     * 这就导致在对HashMap中的元素进行修改的时候，即对数组中元素进行修改，会导致原对象和clone对象都发生改变，但进行新增或删除就不会影响对方，因为这相当于是对数组做出的改变，clone对象新生成了一个数组。
     *
     * @return hashMap的浅拷贝
     */
    @SuppressWarnings("unchecked")
    @Override
    public Object clone() {
        HashMap<K, V> result;
        try {
            result = (HashMap<K, V>) super.clone();
        } catch (CloneNotSupportedException e) {
            // this shouldn't happen, since we are Cloneable
            throw new InternalError(e);
        }
        result.reinitialize();
        result.putMapEntries(this, false);
        return result;
    }

    // These methods are also used when serializing HashSets
    final float loadFactor() {
        return loadFactor;
    }

    final int capacity() {
        return (table != null) ? table.length :
                (threshold > 0) ? threshold :
                        DEFAULT_INITIAL_CAPACITY;
    }

    /**
     * 序列化hashMap到ObjectOutputStream中
     * 将hashMap的总容量capacity、实际容量size、键值对映射写入到ObjectOutputStream中。键值对映射序列化时是无序的。
     *
     * @serialData The <i>capacity</i> of the HashMap (the length of the
     * bucket array) is emitted (int), followed by the
     * <i>size</i> (an int, the number of key-value
     * mappings), followed by the key (Object) and value (Object)
     * for each key-value mapping.  The key-value mappings are
     * emitted in no particular order.
     */
    private void writeObject(java.io.ObjectOutputStream s)
            throws IOException {
        int buckets = capacity();
        // Write out the threshold, loadfactor, and any hidden stuff
        s.defaultWriteObject();
        //写入总容量
        s.writeInt(buckets);
        //写入实际容量
        s.writeInt(size);
        //写入键值对
        internalWriteEntries(s);
    }

    /**
     * 到ObjectOutputStream中读取hashMap
     * 将hashMap的总容量capacity、实际容量size、键值对映射读取出来
     */
    private void readObject(java.io.ObjectInputStream s)
            throws IOException, ClassNotFoundException {
        // 将hashMap的总容量capacity、实际容量size、键值对映射读取出来
        s.defaultReadObject();
        //重置hashMap
        reinitialize();
        //如果加载因子不合法，抛出异常
        if (loadFactor <= 0 || Float.isNaN(loadFactor))
            throw new InvalidObjectException("Illegal load factor: " +
                    loadFactor);
        s.readInt();                //读出桶的数量，忽略
        int mappings = s.readInt(); //读出实际容量size
        //如果读出的实际容量size小于0，抛出异常
        if (mappings < 0)
            throw new InvalidObjectException("Illegal mappings count: " +
                    mappings);
        else if (mappings > 0) { // (if zero, use defaults)
            // Size the table using given load factor only if within
            // range of 0.25...4.0
            //调整hashMap大小
            float lf = Math.min(Math.max(0.25f, loadFactor), 4.0f);            // 加载因子
            float fc = (float) mappings / lf + 1.0f;         //初步得到的总容量，后续还会处理
            //处理初步得到的容量，确认最终的总容量
            int cap = ((fc < DEFAULT_INITIAL_CAPACITY) ?
                    DEFAULT_INITIAL_CAPACITY :
                    (fc >= MAXIMUM_CAPACITY) ?
                            MAXIMUM_CAPACITY :
                            tableSizeFor((int) fc));
            //计算临界值，得到初步的临界值
            float ft = (float) cap * lf;
            //得到最终的临界值
            threshold = ((cap < MAXIMUM_CAPACITY && ft < MAXIMUM_CAPACITY) ?
                    (int) ft : Integer.MAX_VALUE);

            // Check Map.Entry[].class since it's the nearest public type to
            // what we're actually creating.
            SharedSecrets.getJavaOISAccess().checkArray(s, Map.Entry[].class, cap);
            //新建桶数组table
            @SuppressWarnings({"rawtypes", "unchecked"})
            Node<K, V>[] tab = (Node<K, V>[]) new Node[cap];
            table = tab;

            // 读出key和value，并组成键值对插入hashMap中
            for (int i = 0; i < mappings; i++) {
                @SuppressWarnings("unchecked")
                K key = (K) s.readObject();
                @SuppressWarnings("unchecked")
                V value = (V) s.readObject();
                putVal(hash(key), key, value, false, false);
            }
        }
    }

    /* ------------------------------------------------------------ */
    // iterators

    abstract class HashIterator {
        Node<K, V> next;        // next entry to return
        Node<K, V> current;     // current entry
        int expectedModCount;  // for fast-fail
        int index;             // current slot

        HashIterator() {
            expectedModCount = modCount;
            Node<K, V>[] t = table;
            current = next = null;
            index = 0;
            if (t != null && size > 0) { // advance to first entry
                do {
                } while (index < t.length && (next = t[index++]) == null);
            }
        }

        public final boolean hasNext() {
            return next != null;
        }

        final Node<K, V> nextNode() {
            Node<K, V>[] t;
            Node<K, V> e = next;
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            if (e == null)
                throw new NoSuchElementException();
            if ((next = (current = e).next) == null && (t = table) != null) {
                do {
                } while (index < t.length && (next = t[index++]) == null);
            }
            return e;
        }

        public final void remove() {
            Node<K, V> p = current;
            if (p == null)
                throw new IllegalStateException();
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
            current = null;
            K key = p.key;
            removeNode(hash(key), key, null, false, false);
            expectedModCount = modCount;
        }
    }

    final class KeyIterator extends HashIterator
            implements Iterator<K> {
        public final K next() {
            return nextNode().key;
        }
    }

    final class ValueIterator extends HashIterator
            implements Iterator<V> {
        public final V next() {
            return nextNode().value;
        }
    }

    final class EntryIterator extends HashIterator
            implements Iterator<Map.Entry<K, V>> {
        public final Map.Entry<K, V> next() {
            return nextNode();
        }
    }

    /* ------------------------------------------------------------ */
    // spliterators

    static class HashMapSpliterator<K, V> {
        final HashMap<K, V> map;
        Node<K, V> current;          //记录当前的节点
        int index;                  //当前节点的下标
        int fence;                  //堆大小
        int est;                    //估计大小
        int expectedModCount;       // for comodification checks

        HashMapSpliterator(HashMap<K, V> m, int origin,
                           int fence, int est,
                           int expectedModCount) {
            this.map = m;
            this.index = origin;
            this.fence = fence;
            this.est = est;
            this.expectedModCount = expectedModCount;
        }

        final int getFence() { // initialize fence and size on first use
            int hi;
            if ((hi = fence) < 0) {
                HashMap<K, V> m = map;
                est = m.size;
                expectedModCount = m.modCount;
                Node<K, V>[] tab = m.table;
                hi = fence = (tab == null) ? 0 : tab.length;
            }
            return hi;
        }

        public final long estimateSize() {
            getFence(); // force init
            return (long) est;
        }
    }

    static final class KeySpliterator<K, V>
            extends HashMapSpliterator<K, V>
            implements Spliterator<K> {
        KeySpliterator(HashMap<K, V> m, int origin, int fence, int est,
                       int expectedModCount) {
            super(m, origin, fence, est, expectedModCount);
        }

        public KeySpliterator<K, V> trySplit() {
            int hi = getFence(), lo = index, mid = (lo + hi) >>> 1;
            return (lo >= mid || current != null) ? null :
                    new KeySpliterator<>(map, lo, index = mid, est >>>= 1,
                            expectedModCount);
        }

        public void forEachRemaining(Consumer<? super K> action) {
            int i, hi, mc;
            if (action == null)
                throw new NullPointerException();
            HashMap<K, V> m = map;
            Node<K, V>[] tab = m.table;
            if ((hi = fence) < 0) {
                mc = expectedModCount = m.modCount;
                hi = fence = (tab == null) ? 0 : tab.length;
            } else
                mc = expectedModCount;
            if (tab != null && tab.length >= hi &&
                    (i = index) >= 0 && (i < (index = hi) || current != null)) {
                Node<K, V> p = current;
                current = null;
                do {
                    if (p == null)
                        p = tab[i++];
                    else {
                        action.accept(p.key);
                        p = p.next;
                    }
                } while (p != null || i < hi);
                if (m.modCount != mc)
                    throw new ConcurrentModificationException();
            }
        }

        public boolean tryAdvance(Consumer<? super K> action) {
            int hi;
            if (action == null)
                throw new NullPointerException();
            Node<K, V>[] tab = map.table;
            if (tab != null && tab.length >= (hi = getFence()) && index >= 0) {
                while (current != null || index < hi) {
                    if (current == null)
                        current = tab[index++];
                    else {
                        K k = current.key;
                        current = current.next;
                        action.accept(k);
                        if (map.modCount != expectedModCount)
                            throw new ConcurrentModificationException();
                        return true;
                    }
                }
            }
            return false;
        }

        public int characteristics() {
            return (fence < 0 || est == map.size ? Spliterator.SIZED : 0) |
                    Spliterator.DISTINCT;
        }
    }

    static final class ValueSpliterator<K, V>
            extends HashMapSpliterator<K, V>
            implements Spliterator<V> {
        ValueSpliterator(HashMap<K, V> m, int origin, int fence, int est,
                         int expectedModCount) {
            super(m, origin, fence, est, expectedModCount);
        }

        public ValueSpliterator<K, V> trySplit() {
            int hi = getFence(), lo = index, mid = (lo + hi) >>> 1;
            return (lo >= mid || current != null) ? null :
                    new ValueSpliterator<>(map, lo, index = mid, est >>>= 1,
                            expectedModCount);
        }

        public void forEachRemaining(Consumer<? super V> action) {
            int i, hi, mc;
            if (action == null)
                throw new NullPointerException();
            HashMap<K, V> m = map;
            Node<K, V>[] tab = m.table;
            if ((hi = fence) < 0) {
                mc = expectedModCount = m.modCount;
                hi = fence = (tab == null) ? 0 : tab.length;
            } else
                mc = expectedModCount;
            if (tab != null && tab.length >= hi &&
                    (i = index) >= 0 && (i < (index = hi) || current != null)) {
                Node<K, V> p = current;
                current = null;
                do {
                    if (p == null)
                        p = tab[i++];
                    else {
                        action.accept(p.value);
                        p = p.next;
                    }
                } while (p != null || i < hi);
                if (m.modCount != mc)
                    throw new ConcurrentModificationException();
            }
        }

        public boolean tryAdvance(Consumer<? super V> action) {
            int hi;
            if (action == null)
                throw new NullPointerException();
            Node<K, V>[] tab = map.table;
            if (tab != null && tab.length >= (hi = getFence()) && index >= 0) {
                while (current != null || index < hi) {
                    if (current == null)
                        current = tab[index++];
                    else {
                        V v = current.value;
                        current = current.next;
                        action.accept(v);
                        if (map.modCount != expectedModCount)
                            throw new ConcurrentModificationException();
                        return true;
                    }
                }
            }
            return false;
        }

        public int characteristics() {
            return (fence < 0 || est == map.size ? Spliterator.SIZED : 0);
        }
    }

    static final class EntrySpliterator<K, V>
            extends HashMapSpliterator<K, V>
            implements Spliterator<Map.Entry<K, V>> {
        EntrySpliterator(HashMap<K, V> m, int origin, int fence, int est,
                         int expectedModCount) {
            super(m, origin, fence, est, expectedModCount);
        }

        public EntrySpliterator<K, V> trySplit() {
            int hi = getFence(), lo = index, mid = (lo + hi) >>> 1;
            return (lo >= mid || current != null) ? null :
                    new EntrySpliterator<>(map, lo, index = mid, est >>>= 1,
                            expectedModCount);
        }

        public void forEachRemaining(Consumer<? super Map.Entry<K, V>> action) {
            int i, hi, mc;
            if (action == null)
                throw new NullPointerException();
            HashMap<K, V> m = map;
            Node<K, V>[] tab = m.table;
            if ((hi = fence) < 0) {
                mc = expectedModCount = m.modCount;
                hi = fence = (tab == null) ? 0 : tab.length;
            } else
                mc = expectedModCount;
            if (tab != null && tab.length >= hi &&
                    (i = index) >= 0 && (i < (index = hi) || current != null)) {
                Node<K, V> p = current;
                current = null;
                do {
                    if (p == null)
                        p = tab[i++];
                    else {
                        action.accept(p);
                        p = p.next;
                    }
                } while (p != null || i < hi);
                if (m.modCount != mc)
                    throw new ConcurrentModificationException();
            }
        }

        public boolean tryAdvance(Consumer<? super Map.Entry<K, V>> action) {
            int hi;
            if (action == null)
                throw new NullPointerException();
            Node<K, V>[] tab = map.table;
            if (tab != null && tab.length >= (hi = getFence()) && index >= 0) {
                while (current != null || index < hi) {
                    if (current == null)
                        current = tab[index++];
                    else {
                        Node<K, V> e = current;
                        current = current.next;
                        action.accept(e);
                        if (map.modCount != expectedModCount)
                            throw new ConcurrentModificationException();
                        return true;
                    }
                }
            }
            return false;
        }

        public int characteristics() {
            return (fence < 0 || est == map.size ? Spliterator.SIZED : 0) |
                    Spliterator.DISTINCT;
        }
    }

    /* ------------------------------------------------------------ */
    // LinkedHashMap support


    /*
     * The following package-protected methods are designed to be
     * overridden by LinkedHashMap, but not by any other subclass.
     * Nearly all other internal methods are also package-protected
     * but are declared final, so can be used by LinkedHashMap, view
     * classes, and HashSet.
     */

    // 创建一个链表结点
    Node<K, V> newNode(int hash, K key, V value, Node<K, V> next) {
        return new Node<>(hash, key, value, next);
    }

    // 替换一个链表节点
    Node<K, V> replacementNode(Node<K, V> p, Node<K, V> next) {
        return new Node<>(p.hash, p.key, p.value, next);
    }

    // 创建一个红黑树节点
    TreeNode<K, V> newTreeNode(int hash, K key, V value, Node<K, V> next) {
        return new TreeNode<>(hash, key, value, next);
    }

    // 替换一个红黑树节点
    TreeNode<K, V> replacementTreeNode(Node<K, V> p, Node<K, V> next) {
        return new TreeNode<>(p.hash, p.key, p.value, next);
    }

    /**
     * Reset to initial default state.  Called by clone and readObject.
     */
    void reinitialize() {
        table = null;
        entrySet = null;
        keySet = null;
        values = null;
        modCount = 0;
        threshold = 0;
        size = 0;
    }

    // Callbacks to allow LinkedHashMap post-actions
    void afterNodeAccess(Node<K, V> p) {
    }

    void afterNodeInsertion(boolean evict) {
    }

    void afterNodeRemoval(Node<K, V> p) {
    }

    // 写入hashMap键值对到ObjectOutputStream中
    void internalWriteEntries(java.io.ObjectOutputStream s) throws IOException {
        Node<K, V>[] tab;
        if (size > 0 && (tab = table) != null) {
            for (int i = 0; i < tab.length; ++i) {
                for (Node<K, V> e = tab[i]; e != null; e = e.next) {
                    s.writeObject(e.key);
                    s.writeObject(e.value);
                }
            }
        }
    }

    /* ------------------------------------------------------------ */
    // Tree bins

    /**
     * JDK1.8新增，用来支持桶的红黑树结构实现
     * 性质1. 节点是红色或黑色。
     * 性质2. 根是黑色。
     * 性质3. 所有叶子都是黑色（叶子是NIL节点）。
     * 性质4. 每个红色节点必须有两个黑色的子节点。(从每个叶子到根的所有路径上不能有两个连续的红色节点。)
     * 性质5. 从任一节点到其每个叶子的所有简单路径都包含相同数目的黑色节点。
     */

    static final class TreeNode<K, V> extends LinkedHashMap.Entry<K, V> {
        TreeNode<K, V> parent;  //节点的父亲
        TreeNode<K, V> left;    //节点的左孩子
        TreeNode<K, V> right;   //节点的右孩子
        TreeNode<K, V> prev;    //节点的前一个节点
        boolean red;            //true表示红节点，false表示黑节点

        TreeNode(int hash, K key, V val, Node<K, V> next) {
            super(hash, key, val, next);
        }

        /**
         * 获取红黑树的根
         */
        final TreeNode<K, V> root() {
            for (TreeNode<K, V> r = this, p; ; ) {
                if ((p = r.parent) == null)
                    return r;
                r = p;
            }
        }

        /**
         * 确保root是桶中的第一个元素 ，将root移到中中的第一个
         */
        static <K, V> void moveRootToFront(Node<K, V>[] tab, TreeNode<K, V> root) {
            int n;
            if (root != null && tab != null && (n = tab.length) > 0) {
                int index = (n - 1) & root.hash;
                TreeNode<K, V> first = (TreeNode<K, V>) tab[index];
                if (root != first) {
                    Node<K, V> rn;
                    tab[index] = root;
                    TreeNode<K, V> rp = root.prev;
                    if ((rn = root.next) != null)
                        ((TreeNode<K, V>) rn).prev = rp;
                    if (rp != null)
                        rp.next = rn;
                    if (first != null)
                        first.prev = root;
                    root.next = first;
                    root.prev = null;
                }
                assert checkInvariants(root);
            }
        }

        /**
         * 查找hash为h，key为k的节点
         */
        final TreeNode<K, V> find(int h, Object k, Class<?> kc) {
            TreeNode<K, V> p = this;
            do {
                int ph, dir;
                K pk;
                TreeNode<K, V> pl = p.left, pr = p.right, q;
                if ((ph = p.hash) > h)
                    p = pl;
                else if (ph < h)
                    p = pr;
                else if ((pk = p.key) == k || (k != null && k.equals(pk)))
                    return p;
                else if (pl == null)
                    p = pr;
                else if (pr == null)
                    p = pl;
                else if ((kc != null ||
                        (kc = comparableClassFor(k)) != null) &&
                        (dir = compareComparables(kc, k, pk)) != 0)
                    p = (dir < 0) ? pl : pr;
                else if ((q = pr.find(h, k, kc)) != null)
                    return q;
                else
                    p = pl;
            } while (p != null);
            return null;
        }

        /**
         * 获取树节点，通过根节点查找
         */
        final TreeNode<K, V> getTreeNode(int h, Object k) {
            return ((parent != null) ? root() : this).find(h, k, null);
        }

        /**
         * 比较2个对象的大小
         */
        static int tieBreakOrder(Object a, Object b) {
            int d;
            if (a == null || b == null ||
                    (d = a.getClass().getName().
                            compareTo(b.getClass().getName())) == 0)
                d = (System.identityHashCode(a) <= System.identityHashCode(b) ?
                        -1 : 1);
            return d;
        }

        /**
         * 将链表转为二叉树
         *
         * @return root of tree
         */
        final void treeify(Node<K, V>[] tab) {
            TreeNode<K, V> root = null;
            for (TreeNode<K, V> x = this, next; x != null; x = next) {
                next = (TreeNode<K, V>) x.next;
                x.left = x.right = null;
                if (root == null) {
                    x.parent = null;
                    x.red = false;
                    root = x;
                } else {
                    K k = x.key;
                    int h = x.hash;
                    Class<?> kc = null;
                    for (TreeNode<K, V> p = root; ; ) {
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

                        TreeNode<K, V> xp = p;
                        if ((p = (dir <= 0) ? p.left : p.right) == null) {
                            x.parent = xp;
                            if (dir <= 0)
                                xp.left = x;
                            else
                                xp.right = x;
                            root = balanceInsertion(root, x);
                            break;
                        }
                    }
                }
            }
            moveRootToFront(tab, root);
        }

        /**
         * 将二叉树转为链表
         */
        final Node<K, V> untreeify(HashMap<K, V> map) {
            Node<K, V> hd = null, tl = null;
            for (Node<K, V> q = this; q != null; q = q.next) {
                Node<K, V> p = map.replacementNode(q, null);
                if (tl == null)
                    hd = p;
                else
                    tl.next = p;
                tl = p;
            }
            return hd;
        }

        /**
         * 添加一个键值对
         */
        final TreeNode<K, V> putTreeVal(HashMap<K, V> map, Node<K, V>[] tab,
                                        int h, K k, V v) {
            Class<?> kc = null;
            boolean searched = false;
            TreeNode<K, V> root = (parent != null) ? root() : this;
            for (TreeNode<K, V> p = root; ; ) {
                int dir, ph;
                K pk;
                if ((ph = p.hash) > h)
                    dir = -1;
                else if (ph < h)
                    dir = 1;
                else if ((pk = p.key) == k || (k != null && k.equals(pk)))
                    return p;
                else if ((kc == null &&
                        (kc = comparableClassFor(k)) == null) ||
                        (dir = compareComparables(kc, k, pk)) == 0) {
                    if (!searched) {
                        TreeNode<K, V> q, ch;
                        searched = true;
                        if (((ch = p.left) != null &&
                                (q = ch.find(h, k, kc)) != null) ||
                                ((ch = p.right) != null &&
                                        (q = ch.find(h, k, kc)) != null))
                            return q;
                    }
                    dir = tieBreakOrder(k, pk);
                }

                TreeNode<K, V> xp = p;
                if ((p = (dir <= 0) ? p.left : p.right) == null) {
                    Node<K, V> xpn = xp.next;
                    TreeNode<K, V> x = map.newTreeNode(h, k, v, xpn);
                    if (dir <= 0)
                        xp.left = x;
                    else
                        xp.right = x;
                    xp.next = x;
                    x.parent = x.prev = xp;
                    if (xpn != null)
                        ((TreeNode<K, V>) xpn).prev = x;
                    moveRootToFront(tab, balanceInsertion(root, x));
                    return null;
                }
            }
        }

        /**
         * Removes the given node, that must be present before this call.
         * This is messier than typical red-black deletion code because we
         * cannot swap the contents of an interior node with a leaf
         * successor that is pinned by "next" pointers that are accessible
         * independently during traversal. So instead we swap the tree
         * linkages. If the current tree appears to have too few nodes,
         * the bin is converted back to a plain bin. (The test triggers
         * somewhere between 2 and 6 nodes, depending on tree structure).
         */
        final void removeTreeNode(HashMap<K, V> map, Node<K, V>[] tab,
                                  boolean movable) {
            int n;
            if (tab == null || (n = tab.length) == 0)
                return;
            int index = (n - 1) & hash;
            TreeNode<K, V> first = (TreeNode<K, V>) tab[index], root = first, rl;
            TreeNode<K, V> succ = (TreeNode<K, V>) next, pred = prev;
            if (pred == null)
                tab[index] = first = succ;
            else
                pred.next = succ;
            if (succ != null)
                succ.prev = pred;
            if (first == null)
                return;
            if (root.parent != null)
                root = root.root();
            if (root == null || root.right == null ||
                    (rl = root.left) == null || rl.left == null) {
                tab[index] = first.untreeify(map);  // too small
                return;
            }
            TreeNode<K, V> p = this, pl = left, pr = right, replacement;
            if (pl != null && pr != null) {
                TreeNode<K, V> s = pr, sl;
                while ((sl = s.left) != null) // find successor
                    s = sl;
                boolean c = s.red;
                s.red = p.red;
                p.red = c; // swap colors
                TreeNode<K, V> sr = s.right;
                TreeNode<K, V> pp = p.parent;
                if (s == pr) { // p was s's direct parent
                    p.parent = s;
                    s.right = p;
                } else {
                    TreeNode<K, V> sp = s.parent;
                    if ((p.parent = sp) != null) {
                        if (s == sp.left)
                            sp.left = p;
                        else
                            sp.right = p;
                    }
                    if ((s.right = pr) != null)
                        pr.parent = s;
                }
                p.left = null;
                if ((p.right = sr) != null)
                    sr.parent = p;
                if ((s.left = pl) != null)
                    pl.parent = s;
                if ((s.parent = pp) == null)
                    root = s;
                else if (p == pp.left)
                    pp.left = s;
                else
                    pp.right = s;
                if (sr != null)
                    replacement = sr;
                else
                    replacement = p;
            } else if (pl != null)
                replacement = pl;
            else if (pr != null)
                replacement = pr;
            else
                replacement = p;
            if (replacement != p) {
                TreeNode<K, V> pp = replacement.parent = p.parent;
                if (pp == null)
                    root = replacement;
                else if (p == pp.left)
                    pp.left = replacement;
                else
                    pp.right = replacement;
                p.left = p.right = p.parent = null;
            }

            TreeNode<K, V> r = p.red ? root : balanceDeletion(root, replacement);

            if (replacement == p) {  // detach
                TreeNode<K, V> pp = p.parent;
                p.parent = null;
                if (pp != null) {
                    if (p == pp.left)
                        pp.left = null;
                    else if (p == pp.right)
                        pp.right = null;
                }
            }
            if (movable)
                moveRootToFront(tab, r);
        }

        /**
         * 将结点太多的桶分割
         *
         * @param map   the map
         * @param tab   the table for recording bin heads
         * @param index the index of the table being split
         * @param bit   the bit of hash to split on
         */
        final void split(HashMap<K, V> map, Node<K, V>[] tab, int index, int bit) {
            TreeNode<K, V> b = this;
            // Relink into lo and hi lists, preserving order
            TreeNode<K, V> loHead = null, loTail = null;
            TreeNode<K, V> hiHead = null, hiTail = null;
            int lc = 0, hc = 0;
            for (TreeNode<K, V> e = b, next; e != null; e = next) {
                next = (TreeNode<K, V>) e.next;
                e.next = null;
                if ((e.hash & bit) == 0) {
                    if ((e.prev = loTail) == null)
                        loHead = e;
                    else
                        loTail.next = e;
                    loTail = e;
                    ++lc;
                } else {
                    if ((e.prev = hiTail) == null)
                        hiHead = e;
                    else
                        hiTail.next = e;
                    hiTail = e;
                    ++hc;
                }
            }

            if (loHead != null) {
                if (lc <= UNTREEIFY_THRESHOLD)
                    tab[index] = loHead.untreeify(map);
                else {
                    tab[index] = loHead;
                    if (hiHead != null) // (else is already treeified)
                        loHead.treeify(tab);
                }
            }
            if (hiHead != null) {
                if (hc <= UNTREEIFY_THRESHOLD)
                    tab[index + bit] = hiHead.untreeify(map);
                else {
                    tab[index + bit] = hiHead;
                    if (loHead != null)
                        hiHead.treeify(tab);
                }
            }
        }

        /* ------------------------------------------------------------ */
        // 红黑树方法，都是从CLR中修改的

        /**
         * 左旋转
         *
         * @param root
         * @param p
         * @param <K>
         * @param <V>
         * @return
         */
        static <K, V> TreeNode<K, V> rotateLeft(TreeNode<K, V> root,
                                                TreeNode<K, V> p) {
            TreeNode<K, V> r, pp, rl;
            if (p != null && (r = p.right) != null) {
                if ((rl = p.right = r.left) != null)
                    rl.parent = p;
                if ((pp = r.parent = p.parent) == null)
                    (root = r).red = false;
                else if (pp.left == p)
                    pp.left = r;
                else
                    pp.right = r;
                r.left = p;
                p.parent = r;
            }
            return root;
        }

        /**
         * 右旋转
         *
         * @param root
         * @param p
         * @param <K>
         * @param <V>
         * @return
         */
        static <K, V> TreeNode<K, V> rotateRight(TreeNode<K, V> root,
                                                 TreeNode<K, V> p) {
            TreeNode<K, V> l, pp, lr;
            if (p != null && (l = p.left) != null) {
                if ((lr = p.left = l.right) != null)
                    lr.parent = p;
                if ((pp = l.parent = p.parent) == null)
                    (root = l).red = false;
                else if (pp.right == p)
                    pp.right = l;
                else
                    pp.left = l;
                l.right = p;
                p.parent = l;
            }
            return root;
        }

        /**
         * 保证插入后平衡
         *
         * @param root
         * @param x
         * @param <K>
         * @param <V>
         * @return
         */
        static <K, V> TreeNode<K, V> balanceInsertion(TreeNode<K, V> root,
                                                      TreeNode<K, V> x) {
            x.red = true;
            for (TreeNode<K, V> xp, xpp, xppl, xppr; ; ) {
                if ((xp = x.parent) == null) {
                    x.red = false;
                    return x;
                } else if (!xp.red || (xpp = xp.parent) == null)
                    return root;
                if (xp == (xppl = xpp.left)) {
                    if ((xppr = xpp.right) != null && xppr.red) {
                        xppr.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    } else {
                        if (x == xp.right) {
                            root = rotateLeft(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateRight(root, xpp);
                            }
                        }
                    }
                } else {
                    if (xppl != null && xppl.red) {
                        xppl.red = false;
                        xp.red = false;
                        xpp.red = true;
                        x = xpp;
                    } else {
                        if (x == xp.left) {
                            root = rotateRight(root, x = xp);
                            xpp = (xp = x.parent) == null ? null : xp.parent;
                        }
                        if (xp != null) {
                            xp.red = false;
                            if (xpp != null) {
                                xpp.red = true;
                                root = rotateLeft(root, xpp);
                            }
                        }
                    }
                }
            }
        }

        /**
         * 删除后调整平衡
         *
         * @param root
         * @param x
         * @param <K>
         * @param <V>
         * @return
         */
        static <K, V> TreeNode<K, V> balanceDeletion(TreeNode<K, V> root,
                                                     TreeNode<K, V> x) {
            for (TreeNode<K, V> xp, xpl, xpr; ; ) {
                if (x == null || x == root)
                    return root;
                else if ((xp = x.parent) == null) {
                    x.red = false;
                    return x;
                } else if (x.red) {
                    x.red = false;
                    return root;
                } else if ((xpl = xp.left) == x) {
                    if ((xpr = xp.right) != null && xpr.red) {
                        xpr.red = false;
                        xp.red = true;
                        root = rotateLeft(root, xp);
                        xpr = (xp = x.parent) == null ? null : xp.right;
                    }
                    if (xpr == null)
                        x = xp;
                    else {
                        TreeNode<K, V> sl = xpr.left, sr = xpr.right;
                        if ((sr == null || !sr.red) &&
                                (sl == null || !sl.red)) {
                            xpr.red = true;
                            x = xp;
                        } else {
                            if (sr == null || !sr.red) {
                                if (sl != null)
                                    sl.red = false;
                                xpr.red = true;
                                root = rotateRight(root, xpr);
                                xpr = (xp = x.parent) == null ?
                                        null : xp.right;
                            }
                            if (xpr != null) {
                                xpr.red = (xp == null) ? false : xp.red;
                                if ((sr = xpr.right) != null)
                                    sr.red = false;
                            }
                            if (xp != null) {
                                xp.red = false;
                                root = rotateLeft(root, xp);
                            }
                            x = root;
                        }
                    }
                } else { // symmetric
                    if (xpl != null && xpl.red) {
                        xpl.red = false;
                        xp.red = true;
                        root = rotateRight(root, xp);
                        xpl = (xp = x.parent) == null ? null : xp.left;
                    }
                    if (xpl == null)
                        x = xp;
                    else {
                        TreeNode<K, V> sl = xpl.left, sr = xpl.right;
                        if ((sl == null || !sl.red) &&
                                (sr == null || !sr.red)) {
                            xpl.red = true;
                            x = xp;
                        } else {
                            if (sl == null || !sl.red) {
                                if (sr != null)
                                    sr.red = false;
                                xpl.red = true;
                                root = rotateLeft(root, xpl);
                                xpl = (xp = x.parent) == null ?
                                        null : xp.left;
                            }
                            if (xpl != null) {
                                xpl.red = (xp == null) ? false : xp.red;
                                if ((sl = xpl.left) != null)
                                    sl.red = false;
                            }
                            if (xp != null) {
                                xp.red = false;
                                root = rotateRight(root, xp);
                            }
                            x = root;
                        }
                    }
                }
            }
        }

        /**
         * 检测是否符合红黑树
         */
        static <K, V> boolean checkInvariants(TreeNode<K, V> t) {
            TreeNode<K, V> tp = t.parent, tl = t.left, tr = t.right,
                    tb = t.prev, tn = (TreeNode<K, V>) t.next;
            if (tb != null && tb.next != t)
                return false;
            if (tn != null && tn.prev != t)
                return false;
            if (tp != null && t != tp.left && t != tp.right)
                return false;
            if (tl != null && (tl.parent != t || tl.hash > t.hash))
                return false;
            if (tr != null && (tr.parent != t || tr.hash < t.hash))
                return false;
            if (t.red && tl != null && tl.red && tr != null && tr.red)
                return false;
            if (tl != null && !checkInvariants(tl))
                return false;
            if (tr != null && !checkInvariants(tr))
                return false;
            return true;
        }
    }

}
```

## 三、底层数据结构分析
### JDK1.8 之前
`JDK1.8` 之前 `HashMap` 底层是 **数组和链表** 结合在一起使用也就是 **链表散列**。

`HashMap` 通过 `key` 的 `hashCode` 经过`扰动函数`处理过后得到 `hash` 值，然后通过 **`(n - 1) & hash`** 判断当前元素存放的位置（这里的 `n` 指的是数组的长度），如果当前位置存在元素的话，就判断该元素与要存入的元素的 `hash值`以及 `key` 是否相同，如果相同的话，直接覆盖，不相同就通过拉链法解决冲突。

所谓 **扰动函数** 指的就是 `HashMap` 的 `hash` 方法：  
使用 `hash` 方法也就是 **扰动函数** 是为了防止一些实现比较差的 `hashCode()` 方法 换句话说 **使用扰动函数之后可以减少`hash`碰撞**。

**`JDK 1.8 HashMap` 的 `hash` 方法源码:**  
`JDK 1.8` 的 `hash` 方法 相比于 `JDK 1.7` `hash` 方法更加简化，但是原理不变。
```
static final int hash(Object key) {
    int h;
    // key.hashCode()：返回散列值也就是hashcode
    // ^ ：按位异或
    // >>>:无符号右移，忽略符号位，空位都以0补齐
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```
对比一下 `JDK1.7` 的 `HashMap` 的 `hash` 方法源码.
```
static int hash(int h) {
    // This function ensures that hashCodes that differ only by
    // constant multiples at each bit position have a bounded
    // number of collisions (approximately 8 at default load factor).

    h ^= (h >>> 20) ^ (h >>> 12);
    return h ^ (h >>> 7) ^ (h >>> 4);
}
```
**相比于 `JDK1.8` 的 `hash` 方法 ，`JDK 1.7` 的 `hash` 方法的性能会稍差一点点，因为毕竟扰动了 `4` 次。**

**所谓 “拉链法” 就是：将`链表`和`数组`相结合。** 也就是说创建一个`链表数组`，数组中每一格就是一个`链表`。若遇到哈希冲突，则将冲突的值加到`链表`中即可。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/JDK7-拉链式结构.png)
</center>

#### HashMap的属性：
```java
public class HashMap<K,V> extends AbstractMap<K,V> implements Map<K,V>, Cloneable, Serializable {
    // 序列号
    private static final long serialVersionUID = 362498820763181265L;
    // 默认的初始容量是16
    static final int DEFAULT_INITIAL_CAPACITY = 1 << 4;
    // 最大容量
    static final int MAXIMUM_CAPACITY = 1 << 30;
    // 默认的填充因子
    static final float DEFAULT_LOAD_FACTOR = 0.75f;
    // 当桶(bucket)上的结点数大于这个值时会转成红黑树
    static final int TREEIFY_THRESHOLD = 8;
    // 当桶(bucket)上的结点数小于这个值时树转链表
    static final int UNTREEIFY_THRESHOLD = 6;
    // 桶中结构转化为红黑树对应的table的最小大小
    static final int MIN_TREEIFY_CAPACITY = 64;
    // 存储元素的数组，总是2的幂次倍
    transient Node<k,v>[] table;
    // 存放具体元素的集
    transient Set<map.entry<k,v>> entrySet;
    // 存放元素的个数，注意这个不等于数组的长度。
    transient int size;
    // 每次扩容和更改map结构的计数器
    transient int modCount;
    // 临界值 当实际大小(容量*填充因子)超过临界值时，会进行扩容
    int threshold;
    // 加载因子
    final float loadFactor;
}
```
##### `loadFactor` 加载因子
`loadFactor` 加载因子是控制数组存放数据的疏密程度，
* `loadFactor` 越趋近于 `1`，那么 数组中存放的数据(`entry`)也就越多，也就越密，也就是会让链表的长度增加，
* `loadFactor` 越趋近于 `0`，数组中存放的数据(`entry`)也就越少，也就越稀疏。

**`loadFactor` 太大导致查找元素效率低，太小导致数组的利用率低，存放的数据会很分散。`loadFactor` 的默认值为 `0.75f` 是官方给出的一个比较好的临界值。**

给定的`默认容量`为 `16`，`负载因子`为 `0.75`。`Map` 在使用过程中不断的往里面存放数据，当数量达到了 `16 * 0.75 = 12` 就需要将当前 `16` 的容量进行扩容，而扩容这个过程涉及到 `rehash`、`复制数据`等操作，所以 **非常消耗性能** 。

##### `threshold`
**`threshold = capacity * loadFactor`**  
当 `size >= threshold`的时候，那么就要考虑对数组进行`扩容`了。

## 四、核心方法分析
### 1. 基本属性和构造方法
**基本属性**
```java
// 默认容量16
static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; 
 
// 最大容量
static final int MAXIMUM_CAPACITY = 1 << 30;    
 
// 默认负载因子0.75
static final float DEFAULT_LOAD_FACTOR = 0.75f; 
 
// 链表节点转换红黑树节点的阈值, 9个节点转
static final int TREEIFY_THRESHOLD = 8; 
 
// 红黑树节点转换链表节点的阈值, 6个节点转
static final int UNTREEIFY_THRESHOLD = 6;   
 
// 转红黑树时, table的最小长度
static final int MIN_TREEIFY_CAPACITY = 64; 
 
// 链表节点, 继承自Entry
static class Node<K,V> implements Map.Entry<K,V> {  
    final int hash;
    final K key;
    V value;
    Node<K,V> next;
 
    // ... ...
}
 
// 红黑树节点
static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
    TreeNode<K,V> parent;  // red-black tree links
    TreeNode<K,V> left;
    TreeNode<K,V> right;
    TreeNode<K,V> prev;    // needed to unlink next upon deletion
    boolean red;
   
    // ...
}
```

**构造方法：**
```java
// 默认构造函数。
public HashMap() {
    this.loadFactor = DEFAULT_LOAD_FACTOR; // all   other fields defaulted
}

// 包含另一个“Map”的构造函数
public HashMap(Map<? extends K, ? extends V> m) {
    this.loadFactor = DEFAULT_LOAD_FACTOR;
    putMapEntries(m, false);
}

// 指定“容量大小”的构造函数
public HashMap(int initialCapacity) {
    this(initialCapacity, DEFAULT_LOAD_FACTOR);
}

// 指定“容量大小”和“加载因子”的构造函数
public HashMap(int initialCapacity, float loadFactor) {
    if (initialCapacity < 0)
        throw new IllegalArgumentException("Illegal initial capacity: " + initialCapacity);
    if (initialCapacity > MAXIMUM_CAPACITY)
        initialCapacity = MAXIMUM_CAPACITY;
    if (loadFactor <= 0 || Float.isNaN(loadFactor))
        throw new IllegalArgumentException("Illegal load factor: " + loadFactor);
    this.loadFactor = loadFactor;
    this.threshold = tableSizeFor(initialCapacity);
}
```

### 2. get方法
#### 2.1 主代码
```java
public V get(Object key) {
    Node<K,V> e;
    return (e = getNode(hash(key), key)) == null ? null : e.value;
}
 
final Node<K,V> getNode(int hash, Object key) {
    Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
    // 1.对table进行校验：table不为空 && table长度大于0 && 
    // table索引位置(使用table.length - 1和hash值进行位与运算)的节点不为空
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (first = tab[(n - 1) & hash]) != null) {
        // 2.检查first节点的hash值和key是否和入参的一样，如果一样则first即为目标节点，直接返回first节点
        if (first.hash == hash && // always check first node
            ((k = first.key) == key || (key != null && key.equals(k))))
            return first;
        // 3.如果first不是目标节点，并且first的next节点不为空则继续遍历
        if ((e = first.next) != null) {
            if (first instanceof TreeNode)
                // 4.如果是红黑树节点，则调用红黑树的查找目标节点方法getTreeNode
                return ((TreeNode<K,V>)first).getTreeNode(hash, key);
            do {
                // 5.执行链表节点的查找，向下遍历链表, 直至找到节点的key和入参的key相等时,返回该节点
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    return e;
            } while ((e = e.next) != null);
        }
    }
    // 6.找不到符合的返回空
    return null;
}
```
* **第4步：** 如果是`红黑树节点`，则调用`红黑树`的查找目标节点方法 **`getTreeNode`<font color="red">（见代码块1详解）</font>** 。

#### 2.2 代码块1：getTreeNode
```java
final TreeNode<K,V> getTreeNode(int h, Object k) {
    // 1.首先找到红黑树的根节点；2.使用根节点调用find方法
    return ((parent != null) ? root() : this).find(h, k, null);
}
```
* **第2步：** 使用根节点调用方法 **`find`<font color="red">（见代码块2详解）</font>** 。

#### 2.3 代码块2：find
```java
/**
 * 从调用此方法的节点开始查找, 通过hash值和key找到对应的节点
 * 此方法是红黑树节点的查找, 红黑树是特殊的自平衡二叉查找树
 * 平衡二叉查找树的特点：左节点<根节点<右节点
 */
final TreeNode<K,V> find(int h, Object k, Class<?> kc) {
    // 1.将p节点赋值为调用此方法的节点，即为红黑树根节点
    TreeNode<K,V> p = this;
    // 2.从p节点开始向下遍历
    do {
        int ph, dir; K pk;
        TreeNode<K,V> pl = p.left, pr = p.right, q;
        // 3.如果传入的hash值小于p节点的hash值，则往p节点的左边遍历
        if ((ph = p.hash) > h)
            p = pl;
        else if (ph < h) // 4.如果传入的hash值大于p节点的hash值，则往p节点的右边遍历
            p = pr;
        // 5.如果传入的hash值和key值等于p节点的hash值和key值,则p节点为目标节点,返回p节点
        else if ((pk = p.key) == k || (k != null && k.equals(pk)))
            return p;
        // 6.p节点的左节点为空则将向右遍历
        else if (pl == null)    
            p = pr;
        // 7.p节点的右节点为空则向左遍历
        else if (pr == null)    
            p = pl;
        // 8.将p节点与k进行比较
        else if ((kc != null || (kc = comparableClassFor(k)) != null) && // 8.1 kc不为空代表k实现了Comparable
                 (dir = compareComparables(kc, k, pk)) != 0)// 8.2 k<pk则dir<0, k>pk则dir>0
            // 8.3 k<pk则向左遍历(p赋值为p的左节点), 否则向右遍历
            p = (dir < 0) ? pl : pr;
        // 9.代码走到此处, 代表key所属类没有实现Comparable, 直接指定向p的右边遍历
        else if ((q = pr.find(h, k, kc)) != null) 
            return q;
        // 10.代码走到此处代表“pr.find(h, k, kc)”为空, 因此直接向左遍历
        else
            p = pl;
    } while (p != null);
    return null;
}
```
* **第8步：** 将 `p` 节点与 `k` 进行比较，如果传入的 `key`（即代码中的参数 `k`）所属的类实现了`Comparable 接口`（`kc` 不为空，方法 **`comparableClassFor` <font color="red">（见代码块3详解）</font>** ），则将 `k` 跟 `p` 节点的 `key` 进行比较（`kc` 实现了 `Comparable 接口`，因此通过 `kc` 的比较方法进行比较）；  
并将比较结果赋值给 `dir`，如果 **`dir<0` 则代表 `k<pk`，则向 `p 节点`的左边遍历（`pl`）；否则，向 `p` 节点的右边遍历（`pr`）**。

#### 2.4 代码块3：comparableClassFor
```java
static Class<?> comparableClassFor(Object x) {
    // 1.判断x是否实现了Comparable接口
    if (x instanceof Comparable) {
        Class<?> c; Type[] ts, as; Type t; ParameterizedType p;
        // 2.校验x是否为String类型
        if ((c = x.getClass()) == String.class) // bypass checks
            return c;
        if ((ts = c.getGenericInterfaces()) != null) {
            // 3.遍历x实现的所有接口
            for (int i = 0; i < ts.length; ++i) {
                // 4.如果x实现了Comparable接口，则返回x的Class
                if (((t = ts[i]) instanceof ParameterizedType) &&
                    ((p = (ParameterizedType)t).getRawType() == Comparable.class) &&
                    (as = p.getActualTypeArguments()) != null &&
                    as.length == 1 && 
                    as[0] == c) // type arg is c
                    return c;
            }
        }
    }
    return null;
}
```

### 3. put方法
#### 3.1 主代码
```java
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}
 
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
               boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    // 1.校验table是否为空或者length等于0，如果是则调用resize方法进行初始化
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    // 2.通过hash值计算索引位置，将该索引位置的头节点赋值给p，如果p为空则直接在该索引位置新增一个节点即可
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = newNode(hash, key, value, null);
    else {
        // table表该索引位置不为空，则进行查找
        Node<K,V> e; K k;
        // 3.判断p节点的key和hash值是否跟传入的相等，如果相等, 则p节点即为要查找的目标节点，将p节点赋值给e节点
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        // 4.判断p节点是否为TreeNode, 如果是则调用红黑树的putTreeVal方法查找目标节点
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {
            // 5.走到这代表p节点为普通链表节点，则调用普通的链表方法进行查找，使用binCount统计链表的节点数
            for (int binCount = 0; ; ++binCount) {
                // 6.如果p的next节点为空时，则代表找不到目标节点，则新增一个节点并插入链表尾部
                if ((e = p.next) == null) {
                    p.next = newNode(hash, key, value, null);
                    // 7.校验节点数是否超过8个，如果超过则调用treeifyBin方法将链表节点转为红黑树节点，
                    // 减一是因为循环是从p节点的下一个节点开始的
                    if (binCount >= TREEIFY_THRESHOLD - 1)
                        treeifyBin(tab, hash);
                    break;
                }
                // 8.如果e节点存在hash值和key值都与传入的相同，则e节点即为目标节点，跳出循环
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;  // 将p指向下一个节点
            }
        }
        // 9.如果e节点不为空，则代表目标节点存在，使用传入的value覆盖该节点的value，并返回oldValue
        if (e != null) {
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;
            afterNodeAccess(e); // 用于LinkedHashMap
            return oldValue;
        }
    }
    ++modCount;
    // 10.如果插入节点后节点数超过阈值，则调用resize方法进行扩容
    if (++size > threshold)
        resize();
    afterNodeInsertion(evict);  // 用于LinkedHashMap
    return null;
}
```
* **第1步：** 校验 `table` 是否为`空`或者 `length 等于0`，如果是则调用 `resize` 方法进行初始化， **<font color="red">见resize方法详解</font>** 。
* **第4步：** 如果 `p节点` 不是`目标节点`，则判断 `p节点` 是否为 `TreeNode`，如果是则调用`红黑树`的 `putTreeVal` 方法查找目标节点， **<font color="red">见代码块4：putTreeVal</font>** 。
* **第7步：** 校验节点数是否超过 `8` 个，如果超过则调用 `treeifyBin` 方法 将`链表节点`转为`红黑树节点`，见代码块6详解 **<font color="red">见代码块6：treeifyBin</font>** 。

#### 3.2 代码块4：putTreeVal
```java
/**
 * 红黑树的put操作，红黑树插入会同时维护原来的链表属性, 即原来的next属性
 */
final TreeNode<K,V> putTreeVal(HashMap<K,V> map, Node<K,V>[] tab,
                               int h, K k, V v) {
    Class<?> kc = null;
    boolean searched = false;
    // 1.查找根节点, 索引位置的头节点并不一定为红黑树的根节点
    TreeNode<K,V> root = (parent != null) ? root() : this;
    // 2.将根节点赋值给p节点，开始进行查找
    for (TreeNode<K,V> p = root;;) {
        int dir, ph; K pk;
        // 3.如果传入的hash值小于p节点的hash值，将dir赋值为-1，代表向p的左边查找树
        if ((ph = p.hash) > h)
            dir = -1;
        // 4.如果传入的hash值大于p节点的hash值， 将dir赋值为1，代表向p的右边查找树
        else if (ph < h)
            dir = 1;
        // 5.如果传入的hash值和key值等于p节点的hash值和key值, 则p节点即为目标节点, 返回p节点
        else if ((pk = p.key) == k || (k != null && k.equals(pk)))
            return p;
        // 6.如果k所属的类没有实现Comparable接口 或者 k和p节点的key相等
        else if ((kc == null && (kc = comparableClassFor(k)) == null) ||
                 (dir = compareComparables(kc, k, pk)) == 0) {
            // 6.1 第一次符合条件，从p节点的左节点和右节点分别调用find方法进行查找, 如果查找到目标节点则返回
            if (!searched) {
                TreeNode<K,V> q, ch;
                searched = true;
                if (((ch = p.left) != null &&
                     (q = ch.find(h, k, kc)) != null) ||
                    ((ch = p.right) != null &&
                     (q = ch.find(h, k, kc)) != null))
                    return q;
            }
            // 6.2 否则使用定义的一套规则来比较k和p节点的key的大小, 用来决定向左还是向右查找
            dir = tieBreakOrder(k, pk); // dir<0则代表k<pk，则向p左边查找；反之亦然
        }
 
        TreeNode<K,V> xp = p;   // xp赋值为x的父节点,中间变量,用于下面给x的父节点赋值
        // 7.dir<=0则向p左边查找,否则向p右边查找,如果为null,则代表该位置即为x的目标位置
        if ((p = (dir <= 0) ? p.left : p.right) == null) {
            // 走进来代表已经找到x的位置，只需将x放到该位置即可
            Node<K,V> xpn = xp.next;    // xp的next节点
            // 8.创建新的节点, 其中x的next节点为xpn, 即将x节点插入xp与xpn之间
            TreeNode<K,V> x = map.newTreeNode(h, k, v, xpn);
            // 9.调整x、xp、xpn之间的属性关系
            if (dir <= 0)   // 如果时dir <= 0, 则代表x节点为xp的左节点
                xp.left = x;
            else        // 如果时dir> 0, 则代表x节点为xp的右节点
                xp.right = x;
            xp.next = x;    // 将xp的next节点设置为x
            x.parent = x.prev = xp; // 将x的parent和prev节点设置为xp
            // 如果xpn不为空,则将xpn的prev节点设置为x节点,与上文的x节点的next节点对应
            if (xpn != null)
                ((TreeNode<K,V>)xpn).prev = x;
            // 10.进行红黑树的插入平衡调整
            moveRootToFront(tab, balanceInsertion(root, x));
            return null;
        }
    }
}
```
* **第6.1步：** 第一次符合条件，从 `p 节点` 的`左节点`和`右节点`分别调用 `find` 方法 **<font color="red">（见代码块2：find）</font>**  进行查找，如果查找到目标节点则返回
* **第6.2步：** 否则使用定义的一套规则来比较 `k` 和 `p节点` 的 `key` 的大小，用来决定`向左`还是`向右`查找， **<font color="red">（见代码块5：tieBreakOrder）</font>** 。
* **第10步：** 进行`红黑树`的插入平衡调整（具体过程参见数据结构相关笔记）。

#### 3.3 代码块5：tieBreakOrder
```java
// 用于不可比较或者hashCode相同时进行比较的方法, 只是一个一致的插入规则，用来维护重定位的等价性。
static int tieBreakOrder(Object a, Object b) {  
    int d;
    if (a == null || b == null ||
        (d = a.getClass().getName().
         compareTo(b.getClass().getName())) == 0)
        d = (System.identityHashCode(a) <= System.identityHashCode(b) ?
             -1 : 1);
    return d;
}
```
定义一套规则用于极端情况下比较两个参数的大小。

#### 3.4 代码块6：treeifyBin
```java
/**
 * 将链表节点转为红黑树节点
 */
final void treeifyBin(Node<K,V>[] tab, int hash) {
    int n, index; Node<K,V> e;
    // 1.如果table为空或者table的长度小于64, 调用resize方法进行扩容
    if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
        resize();
    // 2.根据hash值计算索引值，将该索引位置的节点赋值给e，从e开始遍历该索引位置的链表
    else if ((e = tab[index = (n - 1) & hash]) != null) {
        TreeNode<K,V> hd = null, tl = null;
        do {
            // 3.将链表节点转红黑树节点
            TreeNode<K,V> p = replacementTreeNode(e, null);
            // 4.如果是第一次遍历，将头节点赋值给hd
            if (tl == null)	// tl为空代表为第一次循环
                hd = p;
            else {
                // 5.如果不是第一次遍历，则处理当前节点的prev属性和上一个节点的next属性
                p.prev = tl;    // 当前节点的prev属性设为上一个节点
                tl.next = p;    // 上一个节点的next属性设置为当前节点
            }
            // 6.将p节点赋值给tl，用于在下一次循环中作为上一个节点进行一些链表的关联操作（p.prev = tl 和 tl.next = p）
            tl = p;
        } while ((e = e.next) != null);
        // 7.将table该索引位置赋值为新转的TreeNode的头节点，如果该节点不为空，则以以头节点(hd)为根节点, 构建红黑树
        if ((tab[index] = hd) != null)
            hd.treeify(tab);
    }
}
```
* **第7步：** 将 `table` 该索引位置赋值为新转的` TreeNode` 的`头节点hd`，如果该`节点`不为空，则以 `hd` 为`根节点`，构建`红黑树`， **<font color="red">（见代码块7：treeify）</font>** 。

#### 3.5 代码块7：treeify
```java
/**
 * 构建红黑树
 */
final void treeify(Node<K,V>[] tab) {
    TreeNode<K,V> root = null;
    // 1.将调用此方法的节点赋值给x，以x作为起点，开始进行遍历
    for (TreeNode<K,V> x = this, next; x != null; x = next) {
        next = (TreeNode<K,V>)x.next;   // next赋值为x的下个节点
        x.left = x.right = null;    // 将x的左右节点设置为空
        // 2.如果还没有根节点, 则将x设置为根节点
        if (root == null) {
            x.parent = null;    // 根节点没有父节点
            x.red = false;  // 根节点必须为黑色
            root = x;   // 将x设置为根节点
        }
        else {
            K k = x.key;	// k赋值为x的key
            int h = x.hash;	// h赋值为x的hash值
            Class<?> kc = null;
            // 3.如果当前节点x不是根节点, 则从根节点开始查找属于该节点的位置
            for (TreeNode<K,V> p = root;;) {
                int dir, ph;
                K pk = p.key;
                // 4.如果x节点的hash值小于p节点的hash值，则将dir赋值为-1, 代表向p的左边查找
                if ((ph = p.hash) > h)
                    dir = -1;
                // 5.如果x节点的hash值大于p节点的hash值，则将dir赋值为1, 代表向p的右边查找
                else if (ph < h)
                    dir = 1;
                // 6.走到这代表x的hash值和p的hash值相等，则比较key值
                else if ((kc == null && // 6.1 如果k没有实现Comparable接口 或者 x节点的key和p节点的key相等
                          (kc = comparableClassFor(k)) == null) ||
                         (dir = compareComparables(kc, k, pk)) == 0)
                    // 6.2 使用定义的一套规则来比较x节点和p节点的大小，用来决定向左还是向右查找
                    dir = tieBreakOrder(k, pk);
 
                TreeNode<K,V> xp = p;   // xp赋值为x的父节点,中间变量用于下面给x的父节点赋值
                // 7.dir<=0则向p左边查找,否则向p右边查找,如果为null,则代表该位置即为x的目标位置
                if ((p = (dir <= 0) ? p.left : p.right) == null) {
                    // 8.x和xp节点的属性设置
                    x.parent = xp;  // x的父节点即为最后一次遍历的p节点
                    if (dir <= 0)   // 如果时dir <= 0, 则代表x节点为父节点的左节点
                        xp.left = x;
                    else    // 如果时dir > 0, 则代表x节点为父节点的右节点
                        xp.right = x;
                    // 9.进行红黑树的插入平衡(通过左旋、右旋和改变节点颜色来保证当前树符合红黑树的要求)
                    root = balanceInsertion(root, x);
                    break;
                }
            }
        }
    }
    // 10.如果root节点不在table索引位置的头节点, 则将其调整为头节点
    moveRootToFront(tab, root);
}
```
* **第3步：** 如果当前`节点 x` 不是`根节点`, 则从`根节点`开始查找属于该节点的位置，该段代码跟 **<font color="red">代码块2</font>** 和 **<font color="red">代码块4</font>** 的查找代码类似。
* **第8步：** 如果 `root节点` 不在 `table` 索引位置的`头节点`, 则将其调整为`头节点`， **<font color="red">（见代码块8：moveRootToFront）</font>** 

#### 3.6 代码块8：moveRootToFront
```java
/**
 * 将root放到头节点的位置
 * 如果当前索引位置的头节点不是root节点, 则将root的上一个节点和下一个节点进行关联,
 * 将root放到头节点的位置, 原头节点放在root的next节点上
 */
static <K,V> void moveRootToFront(Node<K,V>[] tab, TreeNode<K,V> root) {
    int n;
    // 1.校验root是否为空、table是否为空、table的length是否大于0
    if (root != null && tab != null && (n = tab.length) > 0) {
        // 2.计算root节点的索引位置
        int index = (n - 1) & root.hash;
        TreeNode<K,V> first = (TreeNode<K,V>)tab[index];
        // 3.如果该索引位置的头节点不是root节点，则该索引位置的头节点替换为root节点
        if (root != first) {
            Node<K,V> rn;
            // 3.1 将该索引位置的头节点赋值为root节点
            tab[index] = root;
            TreeNode<K,V> rp = root.prev;   // root节点的上一个节点
            // 3.2 和 3.3 两个操作是移除root节点的过程
            // 3.2 如果root节点的next节点不为空，则将root节点的next节点的prev属性设置为root节点的prev节点
            if ((rn = root.next) != null)
                ((TreeNode<K,V>)rn).prev = rp;
            // 3.3 如果root节点的prev节点不为空，则将root节点的prev节点的next属性设置为root节点的next节点
            if (rp != null)
                rp.next = rn;
            // 3.4 和 3.5 两个操作将first节点接到root节点后面
            // 3.4 如果原头节点不为空, 则将原头节点的prev属性设置为root节点
            if (first != null)
                first.prev = root;
            // 3.5 将root节点的next属性设置为原头节点
            root.next = first;
            // 3.6 root此时已经被放到该位置的头节点位置，因此将prev属性设为空
            root.prev = null;
        }
        // 4.检查树是否正常
        assert checkInvariants(root);
    }
}
```
* **第4步：** 检查`树`是否正常， **<font color="red">（见代码块9：checkInvariants）</font>**

#### 3.7 代码块9：checkInvariants
```java
/**
 * Recursive invariant check
 */
static <K,V> boolean checkInvariants(TreeNode<K,V> t) { // 一些基本的校验
    TreeNode<K,V> tp = t.parent, tl = t.left, tr = t.right,
        tb = t.prev, tn = (TreeNode<K,V>)t.next;
    if (tb != null && tb.next != t)
        return false;
    if (tn != null && tn.prev != t)
        return false;
    if (tp != null && t != tp.left && t != tp.right)
        return false;
    if (tl != null && (tl.parent != t || tl.hash > t.hash))
        return false;
    if (tr != null && (tr.parent != t || tr.hash < t.hash))
        return false;
    if (t.red && tl != null && tl.red && tr != null && tr.red)  // 如果当前节点为红色, 则该节点的左右节点不能同时为红色
        return false;
    if (tl != null && !checkInvariants(tl))
        return false;
    if (tr != null && !checkInvariants(tr))
        return false;
    return true;
}
```
将传入的`节点`作为`根节点`，遍历所有`节点`，校验`节点`的合法性，主要是保证该`树`符合`红黑树`的规则。

### 4. resize 方法
#### 4.1 主代码
```java
final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;
    // 1.老表的容量不为0，即老表不为空
    if (oldCap > 0) {
        // 1.1 判断老表的容量是否超过最大容量值：如果超过则将阈值设置为Integer.MAX_VALUE，并直接返回老表,
        // 此时oldCap * 2比Integer.MAX_VALUE大，因此无法进行重新分布，只是单纯的将阈值扩容到最大
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        // 1.2 将newCap赋值为oldCap的2倍，如果newCap<最大容量并且oldCap>=16, 则将新阈值设置为原来的两倍
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                 oldCap >= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr << 1; // double threshold
    }
    // 2.如果老表的容量为0, 老表的阈值大于0, 是因为初始容量被放入阈值，则将新表的容量设置为老表的阈值
    else if (oldThr > 0)
        newCap = oldThr;
    else {
        // 3.老表的容量为0, 老表的阈值为0，这种情况是没有传初始容量的new方法创建的空表，将阈值和容量设置为默认值
        newCap = DEFAULT_INITIAL_CAPACITY;
        newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
    }
    // 4.如果新表的阈值为空, 则通过新的容量*负载因子获得阈值
    if (newThr == 0) {
        float ft = (float)newCap * loadFactor;
        newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                  (int)ft : Integer.MAX_VALUE);
    }
    // 5.将当前阈值设置为刚计算出来的新的阈值，定义新表，容量为刚计算出来的新容量，将table设置为新定义的表。
    threshold = newThr;
    @SuppressWarnings({"rawtypes","unchecked"})
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    table = newTab;
    // 6.如果老表不为空，则需遍历所有节点，将节点赋值给新表
    if (oldTab != null) {
        for (int j = 0; j < oldCap; ++j) {
            Node<K,V> e;
            if ((e = oldTab[j]) != null) {  // 将索引值为j的老表头节点赋值给e
                oldTab[j] = null; // 将老表的节点设置为空, 以便垃圾收集器回收空间
                // 7.如果e.next为空, 则代表老表的该位置只有1个节点，计算新表的索引位置, 直接将该节点放在该位置
                if (e.next == null)
                    newTab[e.hash & (newCap - 1)] = e;
                // 8.如果是红黑树节点，则进行红黑树的重hash分布(跟链表的hash分布基本相同)
                else if (e instanceof TreeNode)
                    ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                else { // preserve order
                    // 9.如果是普通的链表节点，则进行普通的重hash分布
                    Node<K,V> loHead = null, loTail = null; // 存储索引位置为:“原索引位置”的节点
                    Node<K,V> hiHead = null, hiTail = null; // 存储索引位置为:“原索引位置+oldCap”的节点
                    Node<K,V> next;
                    do {
                        next = e.next;
                        // 9.1 如果e的hash值与老表的容量进行与运算为0,则扩容后的索引位置跟老表的索引位置一样
                        if ((e.hash & oldCap) == 0) {
                            if (loTail == null) // 如果loTail为空, 代表该节点为第一个节点
                                loHead = e; // 则将loHead赋值为第一个节点
                            else
                                loTail.next = e;    // 否则将节点添加在loTail后面
                            loTail = e; // 并将loTail赋值为新增的节点
                        }
                        // 9.2 如果e的hash值与老表的容量进行与运算为非0,则扩容后的索引位置为:老表的索引位置＋oldCap
                        else {
                            if (hiTail == null) // 如果hiTail为空, 代表该节点为第一个节点
                                hiHead = e; // 则将hiHead赋值为第一个节点
                            else
                                hiTail.next = e;    // 否则将节点添加在hiTail后面
                            hiTail = e; // 并将hiTail赋值为新增的节点
                        }
                    } while ((e = next) != null);
                    // 10.如果loTail不为空（说明老表的数据有分布到新表上“原索引位置”的节点），则将最后一个节点
                    // 的next设为空，并将新表上索引位置为“原索引位置”的节点设置为对应的头节点
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;
                    }
                    // 11.如果hiTail不为空（说明老表的数据有分布到新表上“原索引+oldCap位置”的节点），则将最后
                    // 一个节点的next设为空，并将新表上索引位置为“原索引+oldCap”的节点设置为对应的头节点
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;
                    }
                }
            }
        }
    }
    // 12.返回新表
    return newTab;
}
```
* **第2步：** 老表的容量为 `0`，并且老表的`阈值`大于 `0`：这种情况是新建 `HashMap` 时传了`初始容量`；**例如：`new HashMap<>(32)`，使用这种方式新建 `HashMap` 时，由于 `HashMap` 没有 `capacity`属性，所以此时的 `capacity` 会被暂存在 `threshold` 属性。** 因此此时的 `threshold` 的值就是我们要新创建的 `HashMap` 的 `capacity`，所以将新表的容量设置为 `threshold`。
* **第4步：** 如果新表的`阈值`为`空`，则通过新的 **容量 `x 负载因子`** 获得`阈值`（这种情况是初始化的时候传了`初始容量`，跟第2点相同情况，或者`初始容量`设置的太小导致老表的容量没有超过 `16` 导致的）。
* **第8步：** 如果是`红黑树节点`，则进行`红黑树`的`重 hash 分布`， **<font color="red">（见代码块10：split）</font>** 。
* **第9.1步：** 如果 `e` 的 `hash值` 与老表的容量进行`位与运算`为 `0`，则说明 `e 节点` 扩容后的索引位置跟老表的索引位置一样 **<font color="red">（见例子1详解）</font>** ；  
  然后进行链表拼接操作：
    - 如果 `loTail` 为空，代表该节点为第一个节点，则将 `loHead` 赋值为该节点；
    - 否则将节点添加在 `loTail` 后面，并将 `loTail` 赋值为新增的节点。
* **第9.2步：** 如果 `e` 的 `hash值` 与老表的容量进行`位与运算`为 `1`，则说明 `e 节点`扩容后的索引位置为： **老表的索引位置`＋oldCap`<font color="red">（见例子1详解）</font>** ；  
然后进行链表拼接操作：
    - 如果 `hiTail` 为`空`，代表该节点为第一个节点，则将 `hiHead` 赋值为该节点；
    - 否则将节点添加在 `hiTail` 后面，并将 `hiTail` 赋值为新增的节点。

#### 4.2 代码块10：split
```java
/**
 * 扩容后，红黑树的hash分布，只可能存在于两个位置：原索引位置、原索引位置+oldCap
 */
final void split(HashMap<K,V> map, Node<K,V>[] tab, int index, int bit) {
    TreeNode<K,V> b = this;	// 拿到调用此方法的节点
    TreeNode<K,V> loHead = null, loTail = null; // 存储索引位置为:“原索引位置”的节点
    TreeNode<K,V> hiHead = null, hiTail = null; // 存储索引位置为:“原索引+oldCap”的节点
    int lc = 0, hc = 0;
    // 1.以调用此方法的节点开始，遍历整个红黑树节点
    for (TreeNode<K,V> e = b, next; e != null; e = next) {	// 从b节点开始遍历
        next = (TreeNode<K,V>)e.next;   // next赋值为e的下个节点
        e.next = null;  // 同时将老表的节点设置为空，以便垃圾收集器回收
        // 2.如果e的hash值与老表的容量进行与运算为0,则扩容后的索引位置跟老表的索引位置一样
        if ((e.hash & bit) == 0) {
            if ((e.prev = loTail) == null)  // 如果loTail为空, 代表该节点为第一个节点
                loHead = e; // 则将loHead赋值为第一个节点
            else
                loTail.next = e;    // 否则将节点添加在loTail后面
            loTail = e; // 并将loTail赋值为新增的节点
            ++lc;   // 统计原索引位置的节点个数
        }
        // 3.如果e的hash值与老表的容量进行与运算为非0,则扩容后的索引位置为:老表的索引位置＋oldCap
        else {
            if ((e.prev = hiTail) == null)  // 如果hiHead为空, 代表该节点为第一个节点
                hiHead = e; // 则将hiHead赋值为第一个节点
            else
                hiTail.next = e;    // 否则将节点添加在hiTail后面
            hiTail = e; // 并将hiTail赋值为新增的节点
            ++hc;   // 统计索引位置为原索引+oldCap的节点个数
        }
    }
    // 4.如果原索引位置的节点不为空
    if (loHead != null) {   // 原索引位置的节点不为空
        // 4.1 如果节点个数<=6个则将红黑树转为链表结构
        if (lc <= UNTREEIFY_THRESHOLD)
            tab[index] = loHead.untreeify(map);
        else {
            // 4.2 将原索引位置的节点设置为对应的头节点
            tab[index] = loHead;
            // 4.3 如果hiHead不为空，则代表原来的红黑树(老表的红黑树由于节点被分到两个位置)
            // 已经被改变, 需要重新构建新的红黑树
            if (hiHead != null)
                // 4.4 以loHead为根节点, 构建新的红黑树
                loHead.treeify(tab);
        }
    }
    // 5.如果索引位置为原索引+oldCap的节点不为空
    if (hiHead != null) {   // 索引位置为原索引+oldCap的节点不为空
        // 5.1 如果节点个数<=6个则将红黑树转为链表结构
        if (hc <= UNTREEIFY_THRESHOLD)
            tab[index + bit] = hiHead.untreeify(map);
        else {
            // 5.2 将索引位置为原索引+oldCap的节点设置为对应的头节点
            tab[index + bit] = hiHead;
            // 5.3 loHead不为空则代表原来的红黑树(老表的红黑树由于节点被分到两个位置)
            // 已经被改变, 需要重新构建新的红黑树
            if (loHead != null)
                // 5.4 以hiHead为根节点, 构建新的红黑树
                hiHead.treeify(tab);
        }
    }
}
```
* **第2步：** 如果 `e` 的 `hash 值` 与老表的容量进行`位与运算`为 `0`，则说明 `e 节点` `扩容`后的索引位置跟老表的索引位置一样 **<font color="red">（见例子1详解）</font>** ；  
  进行链表拼接操作：
  - 如果 `loTail` 为`空`，代表该节点为第一个节点，则将 `loHead` 赋值为该节点；
  - 否则将节点添加在 `loTail` 后面，并将 `loTail` 赋值为新增的节点，并统计原索引位置的节点个数。
* **第3步：** 如果 `e` 的 `hash 值` 与老表的容量进行`位与运算`为 `1`，则说明 `e 节点` `扩容`后的索引位置为：**老表的索引位置`＋oldCap` <font color="red">（见例子1详解）</font>** ；  
进行链表拼接操作：
  - 如果 `hiTail` 为空，代表该节点为第一个节点，则将 `hiHead` 赋值为该节点；
  - 否则将节点添加在 `hiTail` 后面，并将 `hiTail` 赋值为新增的节点，并统计索引位置为原索引 `+oldCap` 的节点个数。
* **第4.1步：** 如果`节点个数 <= 6` 个则将`红黑树`转为`链表`结构， **<font color="red">（见代码块11：untreeify）</font>** 。
* **第4.4步：** 以 `loHead` 为`根节点`，构建新的`红黑树`， **<font color="red">（见代码块7：treeify）</font>** 。

#### 4.3 代码块11：untreeify
```java
/**
 * 将红黑树节点转为链表节点, 当节点<=6个时会被触发
 */
final Node<K,V> untreeify(HashMap<K,V> map) {
    Node<K,V> hd = null, tl = null; // hd指向头节点, tl指向尾节点
    // 1.从调用该方法的节点, 即链表的头节点开始遍历, 将所有节点全转为链表节点
    for (Node<K,V> q = this; q != null; q = q.next) {
        // 2.调用replacementNode方法构建链表节点
        Node<K,V> p = map.replacementNode(q, null);
        // 3.如果tl为null, 则代表当前节点为第一个节点, 将hd赋值为该节点
        if (tl == null)
            hd = p;
        // 4.否则, 将尾节点的next属性设置为当前节点p
        else
            tl.next = p;
        tl = p; // 5.每次都将tl节点指向当前节点, 即尾节点
    }
    // 6.返回转换后的链表的头节点
    return hd;
}
```

#### 4.4 例子1：扩容后，节点重 `hash` 为什么只可能分布在 “`原索引位置`” 与 “`原索引 + oldCap` 位置” ？
扩容代码中，使用 `e 节点`的 `hash 值` 跟 `oldCap` 进行`位与运算`，以此决定将节点分布到 “`原索引位置`” 或者 “`原索引 + oldCap` 位置” 上，这是为什么呢？

假设老表的容量为 `16`，即 `oldCap = 16`，则新表容量为 `16 * 2 = 32`，假设 `节点1` 的 `hash` 值为：`0000 0000 0000 0000 0000 1111 0000 1010`，`节点2` 的 `hash值` 为：`0000 0000 0000 0000 0000 1111 0001 1010`，则 `节点1` 和 `节点2` 在老表的索引位置计算如下图中的 **<font color="red">计算1</font>** ，由于老表的长度限制`节点 1` 和`节点 2` 的索引位置只取决于节点 `hash值`的最后 `4` 位。

再看 **<font color="red">计算2</font>** ， **<font color="red">计算2</font>** 为新表的索引计算，可以知道如果两个`节点`在老表的`索引位置相同`，则新表的`索引位置`只取决于`节点hash值` `倒数第5位`的值，而此位置的值刚好为`老表的容量值 16`； 此时节点在新表的索引位置只有两种情况：
* “原索引位置” 
* “原索引 + `oldCap`位置”  

在此例中即为 `10` 和 `10 + 16 = 26`。

由于结果只取决于`节点 hash 值`的倒数第 `5` 位，而此位置的值刚好为`老表的容量值 16`，因此此时新表的索引位置的计算可以替换为 **<font color="red">计算3</font>** ，直接使用`节点的 hash 值`与`老表的容量 16` 进行`位与运算`，如果结果为 `0` 则该节点在`新表的索引位置`为`原索引位置`，否则该节点在新表的`索引位置`为 “`原索引 + oldCap` 位置”。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/扩容后，节点重hash为什么只可能分布在“原索引位置”与“原索引+oldCap位置”？.png)
</center>

### 5. remove 方法
#### 5.1 主代码
```java
/**
 * 移除某个节点
 */
public V remove(Object key) {
    Node<K,V> e;
    return (e = removeNode(hash(key), key, null, false, true)) == null ?
        null : e.value;
}
 
final Node<K,V> removeNode(int hash, Object key, Object value,
                           boolean matchValue, boolean movable) {
    Node<K,V>[] tab; Node<K,V> p; int n, index;
    // 1.如果table不为空并且根据hash值计算出来的索引位置不为空, 将该位置的节点赋值给p
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (p = tab[index = (n - 1) & hash]) != null) {
        Node<K,V> node = null, e; K k; V v;
        // 2.如果p的hash值和key都与入参的相同, 则p即为目标节点, 赋值给node
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            node = p;
        else if ((e = p.next) != null) {
            // 3.否则将p.next赋值给e，向下遍历节点
            // 3.1 如果p是TreeNode则调用红黑树的方法查找节点
            if (p instanceof TreeNode)
                node = ((TreeNode<K,V>)p).getTreeNode(hash, key);
            else {
                // 3.2 否则，进行普通链表节点的查找
                do {
                    // 当节点的hash值和key与传入的相同,则该节点即为目标节点
                    if (e.hash == hash &&
                        ((k = e.key) == key ||
                         (key != null && key.equals(k)))) {
                        node = e;	// 赋值给node, 并跳出循环
                        break;
                    }
                    p = e;  // p节点赋值为本次结束的e，在下一次循环中，e为p的next节点
                } while ((e = e.next) != null); // e指向下一个节点
            }
        }
        // 4.如果node不为空(即根据传入key和hash值查找到目标节点)，则进行移除操作
        if (node != null && (!matchValue || (v = node.value) == value ||
                             (value != null && value.equals(v)))) {
            // 4.1 如果是TreeNode则调用红黑树的移除方法
            if (node instanceof TreeNode)
                ((TreeNode<K,V>)node).removeTreeNode(this, tab, movable);
            // 4.2 如果node是该索引位置的头节点则直接将该索引位置的值赋值为node的next节点，
            // “node == p”只会出现在node是头节点的时候，如果node不是头节点，则node为p的next节点
            else if (node == p)
                tab[index] = node.next;
            // 4.3 否则将node的上一个节点的next属性设置为node的next节点,
            // 即将node节点移除, 将node的上下节点进行关联(链表的移除)
            else
                p.next = node.next;
            ++modCount;
            --size;
            afterNodeRemoval(node); // 供LinkedHashMap使用
            // 5.返回被移除的节点
            return node;
        }
    }
    return null;
}
```
* **第3.1 步：** 如果 `p` 是 `TreeNode` 则调用`红黑树`的方法查找节点， **<font color="red">（见代码块1：getTreeNode）</font>** 。
* **第4.1 步：** 如果`node`是 `TreeNode` 则调用`红黑树`的移除方法， **<font color="red">（见代码块12：removeTreeNode）</font>** 。

#### 5.1 代码块12：removeTreeNode
```java
/**
 * 红黑树的节点移除
 */
final void removeTreeNode(HashMap<K,V> map, Node<K,V>[] tab,
                          boolean movable) {
    // --- 链表的处理start ---
    int n;
    // 1.table为空或者length为0直接返回
    if (tab == null || (n = tab.length) == 0)
        return;
    // 2.根据hash计算出索引的位置
    int index = (n - 1) & hash;
    // 3.将索引位置的头节点赋值给first和root
    TreeNode<K,V> first = (TreeNode<K,V>)tab[index], root = first, rl;
    // 4.该方法被将要被移除的node(TreeNode)调用, 因此此方法的this为要被移除node节点,
    // 将node的next节点赋值给succ节点，prev节点赋值给pred节点
    TreeNode<K,V> succ = (TreeNode<K,V>)next, pred = prev;
    // 5.如果pred节点为空，则代表要被移除的node节点为头节点，
    // 则将table索引位置的值和first节点的值赋值为succ节点(node的next节点)即可
    if (pred == null)
        tab[index] = first = succ;
    else
        // 6.否则将pred节点的next属性设置为succ节点(node的next节点)
        pred.next = succ;
    // 7.如果succ节点不为空，则将succ的prev节点设置为pred, 与前面对应
    if (succ != null)
        succ.prev = pred;
    // 8.如果进行到此first节点为空，则代表该索引位置已经没有节点则直接返回
    if (first == null)
        return;
    // 9.如果root的父节点不为空, 则将root赋值为根节点
    if (root.parent != null)
        root = root.root();
    // 10.通过root节点来判断此红黑树是否太小, 如果是则调用untreeify方法转为链表节点并返回
    // (转链表后就无需再进行下面的红黑树处理)
    if (root == null || root.right == null ||
        (rl = root.left) == null || rl.left == null) {
        tab[index] = first.untreeify(map);  // too small
        return;
    }
    // --- 链表的处理end ---
 
    // --- 以下代码为红黑树的处理 ---
    // 11.将p赋值为要被移除的node节点，pl赋值为p的左节点，pr赋值为p 的右节点
    TreeNode<K,V> p = this, pl = left, pr = right, replacement;
    // 12.如果p的左节点和右节点都不为空时
    if (pl != null && pr != null) {
        // 12.1 将s节点赋值为p的右节点
        TreeNode<K,V> s = pr, sl;
        // 12.2 向左一直查找，跳出循环时,s为没有左节点的节点
        while ((sl = s.left) != null)
            s = sl;
        // 12.3 交换p节点和s节点的颜色
        boolean c = s.red; s.red = p.red; p.red = c;
        TreeNode<K,V> sr = s.right; // s的右节点
        TreeNode<K,V> pp = p.parent;    // p的父节点
        // --- 第一次调整和第二次调整：将p节点和s节点进行了位置调换 ---
        // 12.4 第一次调整
        // 如果p节点的右节点即为s节点，则将p的父节点赋值为s，将s的右节点赋值为p
        if (s == pr) {
            p.parent = s;
            s.right = p;
        }
        else {
            // 将sp赋值为s的父节点
            TreeNode<K,V> sp = s.parent;
            // 将p的父节点赋值为sp
            if ((p.parent = sp) != null) {
                // 如果s节点为sp的左节点，则将sp的左节点赋值为p节点
                if (s == sp.left)
                    sp.left = p;
                // 否则s节点为sp的右节点，则将sp的右节点赋值为p节点
                else
                    sp.right = p;
            }
            // s的右节点赋值为p节点的右节点
            if ((s.right = pr) != null)
                // 如果pr不为空，则将pr的父节点赋值为s
                pr.parent = s;
        }
        // 12.5 第二次调整
        // 将p的左节点赋值为空，pl已经保存了该节点
        p.left = null;
        // 将p节点的右节点赋值为sr，如果sr不为空，则将sr的父节点赋值为p节点
        if ((p.right = sr) != null)
            sr.parent = p;
        // 将s节点的左节点赋值为pl，如果pl不为空，则将pl的父节点赋值为s节点
        if ((s.left = pl) != null)
            pl.parent = s;
        // 将s的父节点赋值为p的父节点pp
        // 如果pp为空，则p节点为root节点, 交换后s成为新的root节点
        if ((s.parent = pp) == null)
            root = s;
        // 如果p不为root节点, 并且p是pp的左节点，则将pp的左节点赋值为s节点
        else if (p == pp.left)
            pp.left = s;
        // 如果p不为root节点, 并且p是pp的右节点，则将pp的右节点赋值为s节点
        else
            pp.right = s;
        // 12.6 寻找replacement节点，用来替换掉p节点
        // 12.6.1 如果sr不为空，则replacement节点为sr，因为s没有左节点，所以使用s的右节点来替换p的位置
        if (sr != null)
            replacement = sr;
        // 12.6.1 如果sr为空，则s为叶子节点，replacement为p本身，只需要将p节点直接去除即可
        else
            replacement = p;
    }
    // 13.承接12点的判断，如果p的左节点不为空，右节点为空，replacement节点为p的左节点
    else if (pl != null)
        replacement = pl;
    // 14.如果p的右节点不为空,左节点为空，replacement节点为p的右节点
    else if (pr != null)
        replacement = pr;
    // 15.如果p的左右节点都为空, 即p为叶子节点, replacement节点为p节点本身
    else
        replacement = p;
    // 16.第三次调整：使用replacement节点替换掉p节点的位置，将p节点移除
    if (replacement != p) { // 如果p节点不是叶子节点
        // 16.1 将p节点的父节点赋值给replacement节点的父节点, 同时赋值给pp节点
        TreeNode<K,V> pp = replacement.parent = p.parent;
        // 16.2 如果p没有父节点, 即p为root节点，则将root节点赋值为replacement节点即可
        if (pp == null)
            root = replacement;
        // 16.3 如果p不是root节点, 并且p为pp的左节点，则将pp的左节点赋值为替换节点replacement
        else if (p == pp.left)
            pp.left = replacement;
        // 16.4 如果p不是root节点, 并且p为pp的右节点，则将pp的右节点赋值为替换节点replacement
        else
            pp.right = replacement;
        // 16.5 p节点的位置已经被完整的替换为replacement, 将p节点清空, 以便垃圾收集器回收
        p.left = p.right = p.parent = null;
    }
    // 17.如果p节点不为红色则进行红黑树删除平衡调整
    // (如果删除的节点是红色则不会破坏红黑树的平衡无需调整)
    TreeNode<K,V> r = p.red ? root : balanceDeletion(root, replacement);
 
    // 18.如果p节点为叶子节点, 则简单的将p节点去除即可
    if (replacement == p) {
        TreeNode<K,V> pp = p.parent;
        // 18.1 将p的parent属性设置为空
        p.parent = null;
        if (pp != null) {
            // 18.2 如果p节点为父节点的左节点，则将父节点的左节点赋值为空
            if (p == pp.left)
                pp.left = null;
            // 18.3 如果p节点为父节点的右节点， 则将父节点的右节点赋值为空
            else if (p == pp.right)
                pp.right = null;
        }
    }
    if (movable)
        // 19.将root节点移到索引位置的头节点
        moveRootToFront(tab, r);
}
```
* **第7步：** 如果 `succ节点` 不为空，则将 `succ` 的 `prev节点` 设置为 `pred`，与前面对应（`TreeNode 链表`的移除）。  
    * 链表中移除一个节点只需如下图操作，其他操作同理
    <center>

    ![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/移除节点：链表.png)
    </center>

    * `红黑树`在维护`链表结构`时，移除一个节点只需如下图操作（`红黑树`中增加了一个 `prev` 属性），其他操作同理。  
      注：此处只是`红黑树`维护`链表结构`的操作，`红黑树`还需要单独进行`红黑树`的移除或者其他操作。
    <center>
    
    ![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/移除节点：红黑树.png)
    </center>
* **第12.6 步：** 寻找 `replacement`，用来替换掉 `p 节点` 。为什么 `sr` 是 `replacement` 的首选，`p` 为备选？
    * **解析：** 首先看 `sr` 是什么？从代码中可以看到 `sr` 第一次被赋值时，是在 `s节点` 进行了`向左穷遍历`结束后，因此此时 `s节点` 是没有`左节点`的，`sr` 即为 `s节点` 的`右节点`。  
    而从上面的第一次调整和第二次调整可以知道，`p节点` 已经跟 `s节点` 进行了`位置调换`，所以此时 `sr` 其实是 `p节点` 的`右节点`，并且 `p节点` 没有`左节点`，因此要移除 `p节点`，只需要将 `p节点` 的`右节点sr` 覆盖掉 `p节点` 即可；  
    因此 `sr` 是 `replacement` 的首选，而如果 `sr` 为`空`，则代表 `p节点` 为`叶子节点`，此时将 `p节点` 直接移除即可。

**PS：代码中的第一次调整和第二次调整是将 `p节点` 和 `s节点` 进行了`位置调换`，然后找出要替换掉 `p节点` 的 `replacement`；第三次调整是将 `replacement节点` 覆盖掉 `p节点`；**   

**三次调整的例子图解：removeTreeNode 图解**
>本图解忽略红黑树的颜色，请注意。  

下面的图解是代码中的最复杂的情况，即流程最长的： **<font color="red">`p节点` 不为`根节点`，`p节点` 有`左右节点`，`s节点` 不为 `pr节点`，`s节点`有`右节点`</font>** 。

另外，第一次调整和第二次调整的是根据代码而设定的，将第一次调整和第二次调整合起来看会更容易理解，如下：
* **第一次调整 + 第二次调整：** 将 `p节点` 和 `s节点` 进行了`位置调换`，选出要替换掉 `p节点` 的 `replacement`
* **第三次调整：** 将 `replacement节点` 覆盖掉 `p节点`
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/移除节点后红黑树的调整步骤.png)
</center>

## 五、扩容和死循环分析
### 1. 死循环
在 `JDK 1.8` 以前，`Java` 语言在并发情况下使用 `HashMap` 造成 **Race Condition（紊乱情况）** ，从而导致 **死循环** 。  
程序经常占了 `100%` 的 `CPU`，查看堆栈，会发现程序都 `Hang` 在了 `“HashMap.get()”` 这个方法上了，重启程序后问题消失。具体分析可以查看这篇文章：[疫苗：JAVA HASHMAP的死循环](https://coolshell.cn/articles/9606.html)，有人将这个问题当成一个 `bug` 提给了 `Sun`，但是 `Sun` 认为这并不是个 `bug`，**因为`HashMap` 本来就不保证并发的线程安全性，在并发下，要用 `ConcurrentHashMap` 来代替**。

在`JDK 1.8` 以前，导致死循环的主要原因是扩容后，节点的顺序会反掉，如下图：**扩容前 `节点A` 在 `节点C` 前面，而扩容后 `节点C` 在 `节点A` 前面。**
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/JDK7扩容图示.png)
</center>

### 2. JDK 1.8 的HashMap扩容过程
> 进行扩容时，会伴随着一次重新 `hash` 分配，并且会遍历 `hash` 表中所有的元素，是非常耗时的。在编写程序中， **要尽量避免 `resize`** 。

`JDK1.8` 普通链表的扩容代码，在上文已经分析过了 **（四、4. resize 方法）** ：**主要是在一个 `do/while` 中处理同一个位置的`所有节点`。** 如下所示：
```java
else { // preserve order
    // 9.如果是普通的链表节点，则进行普通的重hash分布
    Node<K,V> loHead = null, loTail = null; // 存储索引位置为:“原索引位置”的节点
    Node<K,V> hiHead = null, hiTail = null; // 存储索引位置为:“原索引位置+oldCap”的节点
    Node<K,V> next;
    do {
        next = e.next;
        // 9.1 如果e的hash值与老表的容量进行与运算为0,则扩容后的索引位置跟老表的索引位置一样
        if ((e.hash & oldCap) == 0) {
            if (loTail == null) // 如果loTail为空, 代表该节点为第一个节点
                loHead = e; // 则将loHead赋值为第一个节点
            else
                loTail.next = e;    // 否则将节点添加在loTail后面
            loTail = e; // 并将loTail赋值为新增的节点
        }
        // 9.2 如果e的hash值与老表的容量进行与运算为非0,则扩容后的索引位置为:老表的索引位置＋oldCap
        else {
            if (hiTail == null) // 如果hiTail为空, 代表该节点为第一个节点
                hiHead = e; // 则将hiHead赋值为第一个节点
            else
                hiTail.next = e;    // 否则将节点添加在hiTail后面
            hiTail = e; // 并将hiTail赋值为新增的节点
        }
    } while ((e = next) != null);
    // 10.如果loTail不为空（说明老表的数据有分布到新表上“原索引位置”的节点），则将最后一个节点
    // 的next设为空，并将新表上索引位置为“原索引位置”的节点设置为对应的头节点
    if (loTail != null) {
        loTail.next = null;
        newTab[j] = loHead;
    }
    // 11.如果hiTail不为空（说明老表的数据有分布到新表上“原索引+oldCap位置”的节点），则将最后
    // 一个节点的next设为空，并将新表上索引位置为“原索引+oldCap”的节点设置为对应的头节点
    if (hiTail != null) {
        hiTail.next = null;
        newTab[j + oldCap] = hiHead;
    }
}
```
**举个例子：**  
前提：假设有`3`个节点，`节点A`，`节点B`，`节点C`，并且假设他们的 `hash值` 等于 `key值`，则按上诉代码扩容的过程模拟如下：

先看下老表和新表计算索引位置的过程：（`hash`计算省略前面 28 位 `0`，只看最后 `4` 位）
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/JDK8扩容寻找hash位置.png)
</center>

**具体扩容过程：**  
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/集合/HashMap详解（JDK1.8）/JDK8扩容图示.png)
</center>

**结果：** 可以看出，扩容后，`节点A` 和`节点C` 的先后顺序跟扩容前是一样的。  
因此，即使此时有多个线程并发扩容，也不会出现死循环的情况。**当然，这仍然改变不了 `HashMap` 仍是非并发安全，在并发下，还是要使用 <font color="red">`ConcurrentHashMap`</font> 来代替。**

## 六、扩展：HashMap的 7 种遍历方式与性能分析！
性能分析不做搬运，参见博客：[HashMap 的 7 种遍历方式与性能分析！(强烈推荐)](https://blog.csdn.net/belongtocode/article/details/106018417)

>结论：**除了并行循环的 `parallelStream`（即：<font color="red">使用 `Streams API 多线程` 遍历</font>） 性能比极高之外** ，其他方式的遍历方法在性能方面几乎没有任何差别。

### 简述
HashMap 遍历从大的方向来说，可分为以下 4 类：
* 迭代器（`Iterator`）方式遍历；
* `For Each` 方式遍历；
* `Lambda` 表达式遍历（`JDK 1.8+`）;
* `Streams API` 遍历（`JDK 1.8+`）。

但每种类型下又有不同的实现方式，因此具体的遍历方式又可以分为以下 `7` 种：
1. 使用迭代器（`Iterator`）`EntrySet` 的方式进行遍历；
2. 使用迭代器（`Iterator`）`KeySet` 的方式进行遍历；
3. 使用 `For Each EntrySet` 的方式进行遍历；
4. 使用 `For Each KeySet` 的方式进行遍历；
5. 使用 `Lambda` 表达式的方式进行遍历；
6. 使用 `Streams API 单线程`的方式进行遍历；
7. 使用 `Streams API 多线程`的方式进行遍历。

### 1. 迭代器（Iterator）EntrySet
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        Iterator<Map.Entry<Integer, String>> iterator = map.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<Integer, String> entry = iterator.next();
            System.out.print(entry.getKey());
            System.out.print(entry.getValue());
        }
    }
}
```
运行结果：
```
1 Java 2 JDK 3 Spring Framework 4 MyBatis framework 5 Java中文社群
```

### 2. 迭代器（Iterator）KeySet
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        Iterator<Integer> iterator = map.keySet().iterator();
        while (iterator.hasNext()) {
            Integer key = iterator.next();
            System.out.print(key);
            System.out.print(map.get(key));
        }
    }
}
```
运行结果：
```
1 Java 2 JDK 3 Spring Framework 4 MyBatis framework 5 Java中文社群
```

### 3. For Each EntrySet
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        for (Map.Entry<Integer, String> entry : map.entrySet()) {
            System.out.print(entry.getKey());
            System.out.print(entry.getValue());
        }
    }
}
```
运行结果：
```
1 Java 2 JDK 3 Spring Framework 4 MyBatis framework 5 Java中文社群
```

### 4. For Each KeySet
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        for (Integer key : map.keySet()) {
            System.out.print(key);
            System.out.print(map.get(key));
        }
    }
}
```
运行结果：
```
1 Java 2 JDK 3 Spring Framework 4 MyBatis framework 5 Java中文社群
```

### 5. Lambda 表达式
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        map.forEach((key, value) -> {
            System.out.print(key);
            System.out.print(value);
        });
    }
}
```
运行结果：
```
1 Java 2 JDK 3 Spring Framework 4 MyBatis framework 5 Java中文社群
```

### 6. Streams API 单线程
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        map.entrySet().stream().forEach((entry) -> {
            System.out.print(entry.getKey());
            System.out.print(entry.getValue());
        });
    }
}
```
运行结果：
```
1 Java 2 JDK 3 Spring Framework 4 MyBatis framework 5 Java中文社群
```

### 7. Streams API 多线程
```java
public class HashMapTest {
    public static void main(String[] args) {
        // 创建并赋值 HashMap
        Map<Integer, String> map = new HashMap();
        map.put(1, "Java");
        map.put(2, "JDK");
        map.put(3, "Spring Framework");
        map.put(4, "MyBatis framework");
        map.put(5, "Java中文社群");
        // 遍历
        map.entrySet().parallelStream().forEach((entry) -> {
            System.out.print(entry.getKey());
            System.out.print(entry.getValue());
        });
    }
}
```
运行结果：
```
4 MyBatis framework 5 Java中文社群 1 Java 2 JDK 3 Spring Framework
```

## 七、总结
1. `HashMap` 的底层是个 `Node` 数组（`Node<K,V>[] table`），在数组的具体索引位置，如果存在多个`节点`，则可能是以`链表`或`红黑树`的形式存在。
2. `增加`、`删除`、`查找`键值对时，定位到`哈希桶数组`的位置是很关键的一步，源码中是通过下面`3`个操作来完成这一步：
    * 1）拿到 `key` 的 `hashCode` 值；
    * 2）将 `hashCode` 的高位参与运算，重新计算 `hash` 值；
    * 3）将计算出来的 `hash` 值与 `“table.length - 1”` 进行 `&` 运算。
3. `HashMap` 的默认初始容量（`capacity`）是 `16`，`capacity` 必须为 `2` 的幂次方；默认`负载因子`（`load factor`）是 `0.75`；  
实际能存放的`节点个数（threshold，即触发扩容的阈值）= capacity * load factor`。
4. `HashMap` 在触发扩容后，阈值会变为原来的 `2` 倍，并且会对所有节点进行重 `hash` 分布，重 `hash` 分布后节点的新分布位置只可能有两个：
    * **“原索引位置”**
    * **“原索引+oldCap位置”。**
例如 `capacity` 为`16`，索引位置 `5` 的节点扩容后，只可能分布在新表 `“索引位置5”` 和 `“索引位置21（5+16）”`。
5. 导致 `HashMap` 扩容后，同一个索引位置的节点重 `hash` 最多分布在两个位置的根本原因是：
    * 1）`table`的长度始终为 `2` 的 `n` 次方；
    * 2）索引位置的计算方法为 `“(table.length - 1) & hash”`。  
`HashMap` 扩容是一个比较耗时的操作，定义 `HashMap` 时尽量给个接近的初始容量值。
6. `HashMap` 有 `threshold属性` 和 `loadFactor属性`，但是没有 `capacity属性`。  
初始化时，如果传了初始化容量值，该值是存在 `threshold` 变量，并且 `Node数组` 是在第一次 `put` 时才会进行初始化，初始化时会将此时的 `threshold`值作为新表的 `capacity` 值，然后用 `capacity` 和 `loadFactor` 计算`新表`的真正 `threshold` 值。
7. 当同一个`索引位置`的`节点`在增加后达到 `9` 个时，并且此时数组的长度大于等于 `64`，则会触发`链表节点（Node）`转`红黑树节点（TreeNode）`，转成`红黑树节点`后，其实`链表`的结构还存在，通过 `next` 属性维持。  
`链表节`点转`红黑树节点`的具体方法为源码中的 `treeifyBin()` 方法。而如果数组长度小于`64`，则不会触发`链表`转`红黑树`，而是会进行扩容。
8. 当同一个索引位置的节点在`移除`后达到 `6` 个或以下时，并且该索引位置的节点为`红黑树节点`，会触发`红黑树节点`转`链表节点`。具体方法为源码中的 `untreeify()` 方法。
9. `HashMap` 在 `JDK 1.8` 之后不再有死循环的问题，`JDK 1.8` 之前 **存在死循环的根本原因是在扩容后同一索引位置的节点顺序会反掉。**
10. **`HashMap` 是非线程安全的，在并发场景下使用 `ConcurrentHashMap` 来代替。**
# LinkedList详解（JDK1.8）
***
[笔记内容参考1：Java集合：ArrayList详解](https://joonwhee.blog.csdn.net/article/details/79247389)

[toc]
## 一、LinkedList简介
`LinkedList`是基于链表结构的一种集合长。基本数据结构如下：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/Java基础等/集合/LinkedList详解（JDK1.8）/LinkedList的链表结构.png)
</center>

`ArrayList`继承于 `AbstractSequentialList` ，实现了 `List`, `Deque`, `Cloneable`, `java.io.Serializable` 这些接口。

```java
public class LinkedList<E>
    extends AbstractSequentialList<E>
    implements List<E>, Deque<E>, Cloneable, java.io.Serializable{
}
```
* **`Deque`** 双向队列：支持插入删除元素的线性集合。有如下特性：
    * `插入`、`删除`、`获取`操作支持两种形式：快速失败和返回`null`或`true/false`
    * 既具有`FIFO`特点又具有`LIFO`特点，即是队列又是栈
    * 不推荐插入`null`元素，`null`作为特定返回值表示队列为空
    * 未定义基于元素相等的`equals`和`hashCode`
* `ArrayList` 实现了 **`Cloneable`** 接口 ，即覆盖了函数`clone()`，能被克隆。
* `ArrayList` 实现了 **`java.io.Serializable`** 接口，这意味着`ArrayList`支持序列化，能通过序列化去传输。

### 1.1. ArrayDeque 与 LinkedList 的区别?
`ArrayDeque` 和 `LinkedList` 都实现了 `Deque` 接口，两者都具有队列的功能：
* `ArrayDeque` 是基于可变长的数组和双指针来实现，而 LinkedList 则通过链表来实现。
* `ArrayDeque` 不支持存储 `null` 数据，但 `LinkedList` 支持。
* `ArrayDeque` 是在 `JDK1.6` 才被引入的，而 `LinkedList` 早在 `JDK1.2` 时就已经存在。
* `ArrayDeque` 插入时可能存在扩容过程, 不过均摊后的插入操作依然为 `O(1)`。虽然 `LinkedList` 不需要扩容，**但是每次插入数据时均需要申请新的堆空间，均摊性能相比更慢。**

从性能的角度上，选用 `ArrayDeque` 来实现队列要比 `LinkedList` 更好。**此外，`ArrayDeque` 也可以用于实现栈。**

### 1.2. Arraylist 与 LinkedList 区别?
1. **是否保证线程安全：** `ArrayList` 和 `LinkedList` 都是不同步的，也就是不保证线程安全；
2. **底层数据结构：** `Arraylist` 底层使用的是 `Object` 数组；`LinkedList` 底层使用的是 `双向链表` 数据结构（`JDK1.6` 之前为`循环链表`，`JDK1.7` 取消了`循环`。 **注意双向链表和双向循环链表的区别）**
3. **插入和删除是否受元素位置的影响：** 
    * **`ArrayList` 采用数组存储**，所以插入和删除元素的时间复杂度受元素位置的影响。 比如：执行`add(E e)`方法的时候， `ArrayList` 会默认在将指定的元素追加到此列表的末尾，这种情况时间复杂度就是 `O(1)`。但是如果要在指定位置 `i` 插入和删除元素的话（`add(int index, E element)`）时间复杂度就为 `O(n-i)`。  
    因为在进行上述操作的时候集合中第 `i` 和第 `i` 个元素之后的`(n-i)`个元素都要执行向后位移一位的操作。 
    * **`LinkedList` 采用链表存储**，所以对于`add(E e)`方法的插入，删除元素时间复杂度不受元素位置的影响，近似 `O(1)`，如果是要在指定位置`i`插入和删除元素的话（`add(int index, E element)`） 时间复杂度近似为`o(n)`因为需要先移动到指定位置再插入。
4. **是否支持快速随机访问：** `LinkedList` 不支持高效的随机元素访问，而 `ArrayList` 支持。快速随机访问就是通过元素的序号快速获取元素对象（对应于`get(int index)`方法）。
5. **内存空间占用：** `ArrayList` 的空 间浪费主要体现在在 `list` 列表的结尾会预留一定的容量空间，而 `LinkedList` 的空间花费则体现在它的每一个元素都需要消耗比 `ArrayList` 更多的空间 **（因为要存放直接后继和直接前驱以及数据）** 。

## 二、LinkedList 核心源码解读（注释）
```java
package java.util;

import java.util.function.Consumer;

/**
 * LinkedList是List和Deque接口的双向链表的实现。实现了所有可选List操作，并允许包括null值。
 * LinkedList既然是通过双向链表去实现的，那么它可以被当作堆栈、队列或双端队列进行操作。并且其顺序访问非常高效，而随机访问效率比较低。
 * 内部方法，注释会描述为节点的操作(如删除第一个节点)，公开的方法会描述为元素的操作(如删除第一个元素)
 * 注意，此实现不是同步的。 如果多个线程同时访问一个LinkedList实例，而其中至少一个线程从结构上修改了列表，那么它必须保持外部同步。
 * LinkedList不是线程安全的，如果在多线程中使用（修改），需要在外部作同步处理。
 * 这通常是通过同步那些用来封装列表的对象来实现的。
 * 但如果没有这样的对象存在，则该列表需要运用{@link Collections#synchronizedList Collections.synchronizedList}来进行“包装”，该方法最好是在创建列表对象时完成，为了避免对列表进行突发的非同步操作。
 */
public class LinkedList<E>
        extends AbstractSequentialList<E>
        implements List<E>, Deque<E>, Cloneable, java.io.Serializable {
    /**
     * 元素数量
     */
    transient int size = 0;

    /**
     * 首结点引用
     */
    transient Node<E> first;

    /**
     * 尾节点引用
     */
    transient Node<E> last;

    /**
     * 无参构造方法
     */
    public LinkedList() {
    }

    /**
     * 通过一个集合初始化LinkedList，元素顺序有这个集合的迭代器返回顺序决定
     *
     * @param c 其元素将被放入此列表中的集合
     * @throws NullPointerException 如果指定的集合是空的
     */
    public LinkedList(Collection<? extends E> c) {
        // 调用无参构造函数
        this();
        // 添加集合中所有的元素
        addAll(c);
    }

    /**
     * 头插入，即将节点值为e的节点设置为链表首节点，内部使用
     */
    private void linkFirst(E e) {
        //获取当前首结点引用
        final Node<E> f = first;
        //构建一个prev值为null,节点值为e,next值为f的新节点newNode
        final Node<E> newNode = new Node<>(null, e, f);
        //将newNode作为首节点
        first = newNode;
        //如果原首节点为null，即原链表为null，则链表尾节点也设置为newNode
        if (f == null)
            last = newNode;
        else                //否则，原首节点的prev设置为newNode
            f.prev = newNode;
        size++;             //长度+1
        modCount++;         //修改次数+1
    }

    /**
     * 尾插入，即将节点值为e的节点设置为链表的尾节点
     */
    void linkLast(E e) {
        // 获取当前尾结点引用
        final Node<E> l = last;
        //构建一个prev值为l,节点值为e,next值为null的新节点newNode
        final Node<E> newNode = new Node<>(l, e, null);
        //将newNode作为尾节点
        last = newNode;
        //如果原尾节点为null，即原链表为null，则链表首节点也设置为newNode
        if (l == null)
            first = newNode;
        else    //否则，原尾节点的next设置为newNode
            l.next = newNode;
        size++;
        modCount++;
    }

    /**
     * 中间插入，在非空节点succ之前插入节点值e
     */
    void linkBefore(E e, Node<E> succ) {
        // assert succ != null;
        final Node<E> pred = succ.prev;
        //构建一个prev值为succ.prev,节点值为e,next值为succ的新节点newNode
        final Node<E> newNode = new Node<>(pred, e, succ);
        //设置newNode为succ的前节点
        succ.prev = newNode;
        //如果succ.prev为null，即如果succ为首节点，则将newNode设置为首节点
        if (pred == null)
            first = newNode;
        else        //如果succ不是首节点
            pred.next = newNode;
        size++;
        modCount++;
    }

    /**
     * 删除首结点，返回存储的元素，内部使用
     */
    private E unlinkFirst(Node<E> f) {
        // 获取首结点存储的元素
        final E element = f.item;
        // 获取首结点的后继结点
        final Node<E> next = f.next;
        // 删除首结点
        f.item = null;
        f.next = null; //便于垃圾回收期清理
        // 原来首结点的后继结点设为首结点
        first = next;
        // 如果原来首结点的后继结点为空，则尾结点设为null
        // 否则，原来首结点的后继结点的前驱结点设为null
        if (next == null)
            last = null;
        else
            next.prev = null;
        size--;
        modCount++;
        // 返回原来首结点存储的元素
        return element;
    }

    /**
     * 删除尾结点，返回存储的元素，内部使用
     */
    private E unlinkLast(Node<E> l) {
        // 获取尾结点存储的元素
        final E element = l.item;
        // 获取尾结点的前驱结点
        final Node<E> prev = l.prev;
        // 删除尾结点
        l.item = null;
        l.prev = null; // help GC
        // 原来尾结点的前驱结点设为尾结点
        last = prev;
        // 如果原来尾结点的前驱结点为空，则首结点设为null
        // 否则，原来尾结点的前驱结点的后继结点设为null
        if (prev == null)
            first = null;
        else
            prev.next = null;
        size--;
        modCount++;
        // 返回原来尾结点存储的元素
        return element;
    }

    /**
     * 删除指定非空结点，返回存储的元素
     */
    E unlink(Node<E> x) {
        // 获取指定非空结点存储的元素
        final E element = x.item;
        // 获取指定非空结点的后继结点
        final Node<E> next = x.next;
        // 获取指定非空结点的前驱结点
        final Node<E> prev = x.prev;

        /**
         * 如果指定非空结点的前驱结点为空，则指定非空结点的后继结点设为首结点
         * 否则，指定非空结点的后继结点设为指定非空结点的前驱结点的后继结点，
         * 指定非空结点的前驱结点设为null
         */
        if (prev == null) {
            first = next;
        } else {
            prev.next = next;
            x.prev = null;
        }

        /**
         * 如果指定非空结点的后继结点为空，则指定非空结点的前驱结点设为尾结点
         * 否则，指定非空结点的前驱结点设为指定非空结点的后继结点的前驱结点，
         * 指定非空结点的后继结点设为null
         */
        if (next == null) {
            last = prev;
        } else {
            next.prev = prev;
            x.next = null;
        }

        // 指定非空结点存储的元素设为null
        x.item = null;
        size--;
        modCount++;
        // 返回指定非空结点存储的元素
        return element;
    }

    /**
     * 获取首结点存储的元素
     *
     * @return 首结点存储的元素
     * @throws NoSuchElementException 如果链表为空
     */
    public E getFirst() {
        // 获取首结点引用
        final Node<E> f = first;
        // 如果首结点为空，则抛出无该元素异常
        if (f == null)
            throw new NoSuchElementException();
        // 返回首结点存储的元素
        return f.item;
    }

    /**
     * 获取尾结点存储的元素
     *
     * @return 尾结点存储的元素
     * @throws NoSuchElementException 如果链表为空
     */
    public E getLast() {
        // 获取尾结点引用
        final Node<E> l = last;
        // 如果尾结点为空，则抛出无该元素异常
        if (l == null)
            throw new NoSuchElementException();
        // 返回尾结点存储的元素
        return l.item;
    }

    /**
     * 删除首结点，返回存储的元素
     *
     * @return 首结点存储的元素
     * @throws NoSuchElementException 如果链表为空
     */
    public E removeFirst() {
        // 获取首结点引用
        final Node<E> f = first;
        // 如果首结点为空，则抛出无该元素异常
        if (f == null)
            throw new NoSuchElementException();
        // 删除首结点，返回存储的元素
        return unlinkFirst(f);
    }

    /**
     * 删除尾结点，返回存储的元素
     *
     * @return 尾结点存储的元素
     * @throws NoSuchElementException 如果链表为空
     */
    public E removeLast() {
        // 获取尾结点引用
        final Node<E> l = last;
        // 如果尾结点为空，则抛出无该元素异常
        if (l == null)
            throw new NoSuchElementException();
        // 删除尾结点，返回存储的元素
        return unlinkLast(l);
    }

    /**
     * 头部插入指定元素
     *
     * @param e 要添加的元素
     */
    public void addFirst(E e) {
        // 通过头插法来插入指定元素
        linkFirst(e);
    }

    /**
     * 尾部插入指定元素，该方法等价于add()
     *
     * @param e the element to add
     */
    public void addLast(E e) {
        linkLast(e);
    }

    /**
     * 判断是否包含指定元素
     *
     * @param o 判断链表是否包含的元素
     * @return {@code true} 如果链表包含指定的元素
     */
    public boolean contains(Object o) {
        //返回指定元素的索引位置，不存在就返回-1，然后比较返回bool值
        return indexOf(o) != -1;
    }

    /**
     * 获取元素数量
     *
     * @return 元素数量
     */
    public int size() {
        return size;
    }

    /**
     * 插入指定元素，返回操作结果,默认添加到末尾作为最后一个元素
     *
     * @param e 要添加到此链表中的元素
     * @return {@code true} (as specified by {@link Collection#add})
     */
    public boolean add(E e) {
        // 通过尾插法来插入指定元素
        linkLast(e);
        return true;
    }

    /**
     * 删除指定元素，默认从first节点开始，删除第一次出现的那个元素
     *
     * @param o 要从该列表中删除的元素（如果存在）
     * @return {@code true} 如果这个列表包含指定的元素
     */
    public boolean remove(Object o) {
        //会根据是否为null分开处理。若值不是null，会用到对象的equals()方法
        if (o == null) {
            // 遍历链表，查找到指定元素后删除该结点，返回true
            for (Node<E> x = first; x != null; x = x.next) {
                if (x.item == null) {
                    unlink(x);
                    return true;
                }
            }
        } else {
            for (Node<E> x = first; x != null; x = x.next) {
                if (o.equals(x.item)) {
                    unlink(x);
                    return true;
                }
            }
        }
        // 查找失败
        return false;
    }

    /**
     * 将集合插入到链表尾部，即开始索引位置为size
     *
     * @param c 包含要添加到此链表中的元素的集合
     * @return {@code true} 如果该链表因添加而改变
     * @throws NullPointerException 如果指定的集合是空的
     */
    public boolean addAll(Collection<? extends E> c) {
        return addAll(size, c);
    }

    /**
     * 将集合从指定位置开始插入
     *
     * @param index 在哪个索引处前插入指定集合中的第一个元素
     * @param c     包含要添加到此链表中的元素的集合
     * @return {@code true} 如果该链表因添加而改变
     * @throws IndexOutOfBoundsException {@inheritDoc}
     * @throws NullPointerException      如果指定的集合是空的
     */
    public boolean addAll(int index, Collection<? extends E> c) {
        //检查索引是否正确（0<=index<=size）
        checkPositionIndex(index);
        //得到元素数组
        Object[] a = c.toArray();
        //得到元素个数
        int numNew = a.length;
        //若没有元素要添加，直接返回false
        if (numNew == 0)
            return false;
        //succ指向当前需要插入节点的位置，pred指向其前一个节点
        Node<E> pred, succ;
        //如果是在末尾开始添加，当前节点后一个节点初始化为null，前一个节点为尾节点
        if (index == size) {
            succ = null;
            pred = last;
        } else {    //如果不是从末尾开始添加，当前位置的节点为指定位置的节点，前一个节点为要添加的节点的前一个节点
            succ = node(index);
            pred = succ.prev;
        }
        //遍历数组并添加到列表中
        for (Object o : a) {
            @SuppressWarnings("unchecked") E e = (E) o;
            //将元素值e，前继节点pred“封装”为一个新节点newNode
            Node<E> newNode = new Node<>(pred, e, null);
            //如果原链表为null，则新插入的节点作为链表首节点
            if (pred == null)
                first = newNode;
            else
                pred.next = newNode;    //如果存在前节点，前节点会向后指向新加的节点
            pred = newNode; //pred指针向后移动，指向下一个需插入节点位置的前一个节点
        }
        //如果是从最后开始添加的，则最后添加的节点成为尾节点
        if (succ == null) {
            last = pred;
        } else {
            pred.next = succ;   //如果不是从最后开始添加的，则最后添加的节点向后指向之前得到的后续第一个节点
            succ.prev = pred;   //当前，后续的第一个节点也应改为向前指向最后一个添加的节点
        }

        size += numNew;
        modCount++;
        return true;
    }

    /**
     * 删除所有元素
     */
    public void clear() {
        //遍历链表，删除所有结点,方便gc回收垃圾
        for (Node<E> x = first; x != null; ) {
            Node<E> next = x.next;
            x.item = null;
            x.next = null;
            x.prev = null;
            x = next;
        }
        // 首尾结点置空
        first = last = null;
        // 元素数量置0
        size = 0;
        modCount++;
    }


    // 位置访问操作

    /**
     * 获取指定位置的元素
     *
     * @param index 要返回的元素的索引
     * @return 该链表中指定位置的元素
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public E get(int index) {
        // 判断指定位置是否合法
        checkElementIndex(index);
        // 返回指定位置的元素
        return node(index).item;
    }

    /**
     * 修改指定位置的元素，返回之前元素
     *
     * @param index   要替换的元素的索引
     * @param element 要存储在指定位置的元素
     * @return 之前在指定位置的元素
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public E set(int index, E element) {
        // 判断指定位置是否合法
        checkElementIndex(index);
        // 获取指定位置的结点
        Node<E> x = node(index);
        // 获取该结点存储的元素
        E oldVal = x.item;
        // 修改该结点存储的元素
        x.item = element;
        // 返回该结点存储的之前的元素
        return oldVal;
    }

    /**
     * 在指定位置前插入指定元素
     *
     * @param index   指定元素将被插入的索引
     * @param element 要插入的元素
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public void add(int index, E element) {
        // 判断指定位置是否合法
        checkPositionIndex(index);
        // 如果指定位置在尾部，则通过尾插法来插入指定元素
        if (index == size)
            linkLast(element);
        else        //如果指定位置不是尾部，则添加到指定位置前
            linkBefore(element, node(index));
    }

    /**
     * 删除指定位置的元素，返回之前元素
     *
     * @param index 要删除的元素的索引
     * @return 之前在指定位置的元素
     * @throws IndexOutOfBoundsException {@inheritDoc}
     */
    public E remove(int index) {
        // 判断指定位置是否合法
        checkElementIndex(index);
        // 删除指定位置的结点，返回之前元素
        return unlink(node(index));
    }

    /**
     * 判断指定位置是否合法
     */
    private boolean isElementIndex(int index) {
        return index >= 0 && index < size;
    }

    /**
     * 判断迭代器遍历时或插入元素时指定位置是否合法
     */
    private boolean isPositionIndex(int index) {
        return index >= 0 && index <= size;
    }

    /**
     * 获取越界异常信息
     */
    private String outOfBoundsMsg(int index) {
        return "Index: " + index + ", Size: " + size;
    }

    /**
     * 判断指定位置是否合法
     *
     * @param index
     */
    private void checkElementIndex(int index) {
        if (!isElementIndex(index))
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    /**
     * 判断指定位置是否合法
     *
     * @param index
     */
    private void checkPositionIndex(int index) {
        if (!isPositionIndex(index))
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    /**
     * 获取指定下标的结点，index从0开始
     */
    Node<E> node(int index) {
        // 如果指定下标<一半元素数量，则从首结点开始遍历
        // 否则，从尾结点开始遍历
        if (index < (size >> 1)) {
            Node<E> x = first;
            for (int i = 0; i < index; i++)
                x = x.next;
            return x;
        } else {
            Node<E> x = last;
            for (int i = size - 1; i > index; i--)
                x = x.prev;
            return x;
        }
    }

    // 查询操作
    /**
     * 获取顺序下首次出现指定元素的位置
     * 如果返回结果是-1，则表示不存在该元素
     *
     * @param o 要查找的元素
     * @return the index of the first occurrence of the specified element in
     * this list, or -1 if this list does not contain the element
     */
    public int indexOf(Object o) {
        int index = 0;
        if (o == null) {
            // 遍历链表，顺序查找指定元素
            for (Node<E> x = first; x != null; x = x.next) {
                if (x.item == null)
                    return index;
                index++;
            }
        } else {
            for (Node<E> x = first; x != null; x = x.next) {
                if (o.equals(x.item))
                    return index;
                index++;
            }
        }
        return -1;
    }

    /**
     * 获取逆序下首次出现指定元素的位置
     * 如果返回结果是-1，则表示不存在该元素
     *
     * @param o 要查找的元素
     * @return the index of the last occurrence of the specified element in
     * this list, or -1 if this list does not contain the element
     */
    public int lastIndexOf(Object o) {
        int index = size;
        if (o == null) {
            // 遍历链表，逆序查找指定元素
            for (Node<E> x = last; x != null; x = x.prev) {
                index--;
                if (x.item == null)
                    return index;
            }
        } else {
            for (Node<E> x = last; x != null; x = x.prev) {
                index--;
                if (o.equals(x.item))
                    return index;
            }
        }
        return -1;
    }

    // 队列操作
    /**
     * 出队（从前端），获得第一个元素，不存在会返回null，不会删除元素（节点）
     * 获取首元素
     *
     * @return the head of this list, or {@code null} 如果链表为空
     * @since 1.5
     */
    public E peek() {
        final Node<E> f = first;
        // 如果首结点为空，则返回null
        // 否则，返回首结点存储的元素
        return (f == null) ? null : f.item;
    }

    /**
     * 出队（从前端），不删除元素，若为null会抛出异常而不是返回null
     * 获取首元素
     *
     * @return the head of this list
     * @throws NoSuchElementException 如果链表为空
     * @since 1.5
     */
    public E element() {
        // 返回首结点存储的元素
        return getFirst();
    }

    /**
     * 出队（从前端），如果不存在会返回null，存在的话会返回值并移除这个元素（节点）
     * 获取并删除首元素
     *
     * @return the head of this list, or {@code null} 如果链表为空
     * @since 1.5
     */
    public E poll() {
        // 获取首结点引用
        final Node<E> f = first;
        // 如果首结点为空，则返回null
        // 否则，删除首结点，返回首结点存储的元素
        return (f == null) ? null : unlinkFirst(f);
    }

    /**
     * 出队（从前端），如果不存在会抛出异常而不是返回null，存在的话会返回值并移除这个元素（节点）
     * 获取并删除首元素
     *
     * @return the head of this list
     * @throws NoSuchElementException 如果链表为空
     * @since 1.5
     */
    public E remove() {
        // 删除首结点，返回首结点存储的元素
        return removeFirst();
    }

    /**
     * 入队（从后端），始终返回true
     *
     * @param e the element to add
     * @return {@code true} (as specified by {@link Queue#offer})
     * @since 1.5
     */
    public boolean offer(E e) {
        // 通过尾插法插入指定元素，返回操作结果
        return add(e);
    }

    // 双端队列操作
    /**
     * 入队（从前端），始终返回true
     *
     * @param e 要插入的元素
     * @return {@code true} (as specified by {@link Deque#offerFirst})
     * @since 1.6
     */
    public boolean offerFirst(E e) {
        //  通过尾插法来插入指定元素
        addFirst(e);
        return true;
    }

    /**
     * 入队（从后端），始终返回true
     *
     * @param e 要插入的元素
     * @return {@code true} (as specified by {@link Deque#offerLast})
     * @since 1.6
     */
    public boolean offerLast(E e) {
        // 通过尾插法来插入指定元素
        addLast(e);
        return true;
    }

    /**
     * 出队（从后端），获得最后一个元素，不存在会返回null，不会删除元素（节点）
     *
     * @return the first element of this list, or {@code null}
     * 如果链表为空
     * @since 1.6
     */
    public E peekFirst() {
        // 获取首结点引用
        final Node<E> f = first;
        // 如果首结点为空，则返回null
        // 否则，返回首结点存储的元素
        return (f == null) ? null : f.item;
    }

    /**
     * 出队（从后端），获得最后一个元素，不存在会返回null，不会删除元素（节点）
     *
     * @return the last element of this list, or {@code null}
     * 如果链表为空
     * @since 1.6
     */
    public E peekLast() {
        // 获取尾结点引用
        final Node<E> l = last;
        // 如果尾结点为空，则返回null
        // 否则，返回尾结点存储的元素
        return (l == null) ? null : l.item;
    }

    /**
     * 出队（从前端），获得第一个元素，不存在会返回null，会删除元素（节点）
     *
     * @return the first element of this list, or {@code null} if
     * this list is empty
     * @since 1.6
     */
    public E pollFirst() {
        // 获取首结点引用
        final Node<E> f = first;
        // 如果首结点为空，则返回null
        // 否则，删除首结点，返回首结点存储的元素
        return (f == null) ? null : unlinkFirst(f);
    }

    /**
     * 出队（从后端），获得最后一个元素，不存在会返回null，会删除元素（节点）
     *
     * @return the last element of this list, or {@code null} if
     * this list is empty
     * @since 1.6
     */
    public E pollLast() {
        // 获取尾结点引用
        final Node<E> l = last;
        // 如果尾结点为空，则返回null
        // 否则，删除尾结点，返回尾结点存储的元素
        return (l == null) ? null : unlinkLast(l);
    }

    /**
     * 入栈，从前面添加
     *
     * @param e the element to push
     * @since 1.6
     */
    public void push(E e) {
        // 通过头插法来插入指定元素
        addFirst(e);
    }

    /**
     * 出栈，返回栈顶元素，从前面移除（会删除）
     *
     * @return the element at the front of this list (which is the top
     * of the stack represented by this list)
     * @throws NoSuchElementException 如果链表为空
     * @since 1.6
     */
    public E pop() {
        // 删除首结点，返回首结点存储的元素
        return removeFirst();
    }

    /**
     * 删除顺序下首次出现的指定元素，返回操作结果
     *
     * @param o 要从该列表中删除的元素（如果存在）
     * @return {@code true} 如果链表包含指定的元素
     * @since 1.6
     */
    public boolean removeFirstOccurrence(Object o) {
        // 删除顺序下首次出现的指定元素对应的结点，返回操作结果
        return remove(o);
    }

    /**
     * 删除逆序下首次出现的指定元素，返回操作结果
     *
     * @param o 要从该列表中删除的元素（如果存在）
     * @return {@code true} 如果链表包含指定的元素
     * @since 1.6
     */
    public boolean removeLastOccurrence(Object o) {
        //由于LinkedList中允许存放null，因此下面通过两种情况来分别处理
        if (o == null) {
            // 遍历链表，从尾结点开始查找指定元素
            // 如果查找成功，删除该结点，返回true
            for (Node<E> x = last; x != null; x = x.prev) {
                if (x.item == null) {
                    unlink(x);
                    return true;
                }
            }
        } else {
            for (Node<E> x = last; x != null; x = x.prev) {
                if (o.equals(x.item)) {
                    unlink(x);
                    return true;
                }
            }
        }
        // 查找失败
        return false;
    }

    /**
     * Returns a list-iterator of the elements in this list (in proper
     * sequence), starting at the specified position in the list.
     * Obeys the general contract of {@code List.listIterator(int)}.<p>
     * <p>
     * The list-iterator is <i>fail-fast</i>: if the list is structurally
     * modified at any time after the Iterator is created, in any way except
     * through the list-iterator's own {@code remove} or {@code add}
     * methods, the list-iterator will throw a
     * {@code ConcurrentModificationException}.  Thus, in the face of
     * concurrent modification, the iterator fails quickly and cleanly, rather
     * than risking arbitrary, non-deterministic behavior at an undetermined
     * time in the future.
     *
     * @param index index of the first element to be returned from the
     *              list-iterator (by a call to {@code next})
     * @return a ListIterator of the elements in this list (in proper
     * sequence), starting at the specified position in the list
     * @throws IndexOutOfBoundsException {@inheritDoc}
     * @see List#listIterator(int)
     */
    public ListIterator<E> listIterator(int index) {
        checkPositionIndex(index);
        return new ListItr(index);
    }

    private class ListItr implements ListIterator<E> {
        private Node<E> lastReturned;
        private Node<E> next;
        private int nextIndex;
        private int expectedModCount = modCount;

        ListItr(int index) {
            // assert isPositionIndex(index);
            next = (index == size) ? null : node(index);
            nextIndex = index;
        }

        public boolean hasNext() {
            return nextIndex < size;
        }

        public E next() {
            checkForComodification();
            if (!hasNext())
                throw new NoSuchElementException();

            lastReturned = next;
            next = next.next;
            nextIndex++;
            return lastReturned.item;
        }

        public boolean hasPrevious() {
            return nextIndex > 0;
        }

        public E previous() {
            checkForComodification();
            if (!hasPrevious())
                throw new NoSuchElementException();

            lastReturned = next = (next == null) ? last : next.prev;
            nextIndex--;
            return lastReturned.item;
        }

        public int nextIndex() {
            return nextIndex;
        }

        public int previousIndex() {
            return nextIndex - 1;
        }

        public void remove() {
            checkForComodification();
            if (lastReturned == null)
                throw new IllegalStateException();

            Node<E> lastNext = lastReturned.next;
            unlink(lastReturned);
            if (next == lastReturned)
                next = lastNext;
            else
                nextIndex--;
            lastReturned = null;
            expectedModCount++;
        }

        public void set(E e) {
            if (lastReturned == null)
                throw new IllegalStateException();
            checkForComodification();
            lastReturned.item = e;
        }

        public void add(E e) {
            checkForComodification();
            lastReturned = null;
            if (next == null)
                linkLast(e);
            else
                linkBefore(e, next);
            nextIndex++;
            expectedModCount++;
        }

        public void forEachRemaining(Consumer<? super E> action) {
            Objects.requireNonNull(action);
            while (modCount == expectedModCount && nextIndex < size) {
                action.accept(next.item);
                lastReturned = next;
                next = next.next;
                nextIndex++;
            }
            checkForComodification();
        }

        final void checkForComodification() {
            if (modCount != expectedModCount)
                throw new ConcurrentModificationException();
        }
    }

    /**
     * 节点的数据结构，包含前后节点的引用和当前节点
     *
     * @param <E>
     */
    private static class Node<E> {
        // 存储的元素
        E item;
        // 后继结点
        Node<E> next;
        // 前驱结点
        Node<E> prev;

        // 前驱结点、存储的元素和后继结点作为参数的构造方法
        Node(Node<E> prev, E element, Node<E> next) {
            this.item = element;
            this.next = next;
            this.prev = prev;
        }
    }

    /**
     * 返回迭代器
     *
     * @since 1.6
     */
    public Iterator<E> descendingIterator() {
        return new DescendingIterator();
    }

    /**
     * 因为采用链表实现，所以迭代器很简单
     */
    private class DescendingIterator implements Iterator<E> {
        private final ListItr itr = new ListItr(size());

        public boolean hasNext() {
            return itr.hasPrevious();
        }

        public E next() {
            return itr.previous();
        }

        public void remove() {
            itr.remove();
        }
    }

    /**
     * 父类克隆方法
     */
    @SuppressWarnings("unchecked")
    private LinkedList<E> superClone() {
        try {
            return (LinkedList<E>) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new InternalError(e);
        }
    }

    /**
     * 克隆，浅拷贝
     *
     * @return a shallow copy of this {@code LinkedList} instance
     */
    public Object clone() {
        LinkedList<E> clone = superClone();

        // 链表初始化
        clone.first = clone.last = null;
        clone.size = 0;
        clone.modCount = 0;

        // 插入结点
        for (Node<E> x = first; x != null; x = x.next)
            clone.add(x.item);
        // 返回克隆后的对象引用
        return clone;
    }

    /**
     * Returns an array containing all of the elements in this list
     * in proper sequence (from first to last element).
     * <p>
     * <p>The returned array will be "safe" in that no references to it are
     * maintained by this list.  (In other words, this method must allocate
     * a new array).  The caller is thus free to modify the returned array.
     * <p>
     * <p>This method acts as bridge between array-based and collection-based
     * APIs.
     *
     * @return an array containing all of the elements in this list
     * in proper sequence
     */
    public Object[] toArray() {
        Object[] result = new Object[size];
        int i = 0;
        for (Node<E> x = first; x != null; x = x.next)
            result[i++] = x.item;
        return result;
    }

    /**
     * Returns an array containing all of the elements in this list in
     * proper sequence (from first to last element); the runtime type of
     * the returned array is that of the specified array.  If the list fits
     * in the specified array, it is returned therein.  Otherwise, a new
     * array is allocated with the runtime type of the specified array and
     * the size of this list.
     * <p>
     * <p>If the list fits in the specified array with room to spare (i.e.,
     * the array has more elements than the list), the element in the array
     * immediately following the end of the list is set to {@code null}.
     * (This is useful in determining the length of the list <i>only</i> if
     * the caller knows that the list does not contain any null elements.)
     * <p>
     * <p>Like the {@link #toArray()} method, this method acts as bridge between
     * array-based and collection-based APIs.  Further, this method allows
     * precise control over the runtime type of the output array, and may,
     * under certain circumstances, be used to save allocation costs.
     * <p>
     * <p>Suppose {@code x} is a list known to contain only strings.
     * The following code can be used to dump the list into a newly
     * allocated array of {@code String}:
     * <p>
     * <pre>
     *     String[] y = x.toArray(new String[0]);</pre>
     * <p>
     * Note that {@code toArray(new Object[0])} is identical in function to
     * {@code toArray()}.
     *
     * @param a the array into which the elements of the list are to
     *          be stored, if it is big enough; otherwise, a new array of the
     *          same runtime type is allocated for this purpose.
     * @return an array containing the elements of the list
     * @throws ArrayStoreException  if the runtime type of the specified array
     *                              is not a supertype of the runtime type of every element in
     *                              this list
     * @throws NullPointerException if the specified array is null
     */
    @SuppressWarnings("unchecked")
    public <T> T[] toArray(T[] a) {
        if (a.length < size)
            a = (T[]) java.lang.reflect.Array.newInstance(
                    a.getClass().getComponentType(), size);
        int i = 0;
        Object[] result = a;
        for (Node<E> x = first; x != null; x = x.next)
            result[i++] = x.item;

        if (a.length > size)
            a[size] = null;

        return a;
    }

    private static final long serialVersionUID = 876323262645176354L;

    /**
     * 序列化
     */
    private void writeObject(java.io.ObjectOutputStream s)
            throws java.io.IOException {
        // 默认序列化
        s.defaultWriteObject();

        // 写入元素数量
        s.writeInt(size);

        // 遍历链表，写入所有元素
        for (Node<E> x = first; x != null; x = x.next)
            s.writeObject(x.item);
    }

    /**
     * 反序列化
     */
    @SuppressWarnings("unchecked")
    private void readObject(java.io.ObjectInputStream s)
            throws java.io.IOException, ClassNotFoundException {
        // 默认反序列化
        s.defaultReadObject();

        // 读取元素数量
        int size = s.readInt();

        // 遍历链表，读取所有元素并尾部插入
        for (int i = 0; i < size; i++)
            linkLast((E) s.readObject());
    }

    /**
     * Creates a <em><a href="Spliterator.html#binding">late-binding</a></em>
     * and <em>fail-fast</em> {@link Spliterator} over the elements in this
     * list.
     * <p>
     * <p>The {@code Spliterator} reports {@link Spliterator#SIZED} and
     * {@link Spliterator#ORDERED}.  Overriding implementations should document
     * the reporting of additional characteristic values.
     *
     * @return a {@code Spliterator} over the elements in this list
     * @implNote The {@code Spliterator} additionally reports {@link Spliterator#SUBSIZED}
     * and implements {@code trySplit} to permit limited parallelism..
     * @since 1.8
     */
    @Override
    public Spliterator<E> spliterator() {
        return new LLSpliterator<E>(this, -1, 0);
    }

    /**
     * A customized variant of Spliterators.IteratorSpliterator
     */
    static final class LLSpliterator<E> implements Spliterator<E> {
        static final int BATCH_UNIT = 1 << 10;  // batch array size increment
        static final int MAX_BATCH = 1 << 25;  // max batch array size;
        final LinkedList<E> list; // null OK unless traversed
        Node<E> current;      // current node; null until initialized
        int est;              // size estimate; -1 until first needed
        int expectedModCount; // initialized when est set
        int batch;            // batch size for splits

        LLSpliterator(LinkedList<E> list, int est, int expectedModCount) {
            this.list = list;
            this.est = est;
            this.expectedModCount = expectedModCount;
        }

        final int getEst() {
            int s; // force initialization
            final LinkedList<E> lst;
            if ((s = est) < 0) {
                if ((lst = list) == null)
                    s = est = 0;
                else {
                    expectedModCount = lst.modCount;
                    current = lst.first;
                    s = est = lst.size;
                }
            }
            return s;
        }

        public long estimateSize() {
            return (long) getEst();
        }

        public Spliterator<E> trySplit() {
            Node<E> p;
            int s = getEst();
            if (s > 1 && (p = current) != null) {
                int n = batch + BATCH_UNIT;
                if (n > s)
                    n = s;
                if (n > MAX_BATCH)
                    n = MAX_BATCH;
                Object[] a = new Object[n];
                int j = 0;
                do {
                    a[j++] = p.item;
                } while ((p = p.next) != null && j < n);
                current = p;
                batch = j;
                est = s - j;
                return Spliterators.spliterator(a, 0, j, Spliterator.ORDERED);
            }
            return null;
        }

        public void forEachRemaining(Consumer<? super E> action) {
            Node<E> p;
            int n;
            if (action == null) throw new NullPointerException();
            if ((n = getEst()) > 0 && (p = current) != null) {
                current = null;
                est = 0;
                do {
                    E e = p.item;
                    p = p.next;
                    action.accept(e);
                } while (p != null && --n > 0);
            }
            if (list.modCount != expectedModCount)
                throw new ConcurrentModificationException();
        }

        public boolean tryAdvance(Consumer<? super E> action) {
            Node<E> p;
            if (action == null) throw new NullPointerException();
            if (getEst() > 0 && (p = current) != null) {
                --est;
                E e = p.item;
                current = p.next;
                action.accept(e);
                if (list.modCount != expectedModCount)
                    throw new ConcurrentModificationException();
                return true;
            }
            return false;
        }

        public int characteristics() {
            return Spliterator.ORDERED | Spliterator.SIZED | Spliterator.SUBSIZED;
        }
    }
}
```

## 三、常用方法分析
### 1. get方法
```java
public E get(int index) {   
    checkElementIndex(index);   // 校验index是否越界
    return node(index).item;    // 根据index， 调用node方法寻找目标节点，返回目标节点的item
}
```
1. 校验`index`是否越界
2. 调用`node`方法寻找目标节点，并返回目标节点的`item` **（`node方法`详解见下文）**

### 2. add方法
```java
public boolean add(E e) {
    linkLast(e);    // 调用linkLast方法, 将节点添加到尾部
    return true;
}
 
public void add(int index, E element) { // 在index位置插入节点，节点值为element
    checkPositionIndex(index);
 
    if (index == size)  // 如果索引为size，即将element插入链表尾部
        linkLast(element);
    else    // 否则，将element插入原index位置节点的前面，即：将element插入index位置，将原index位置节点移到index+1的位置
        linkBefore(element, node(index));   // 将element插入index位置
}
```
#### add(E e)：
调用`linkLast方法`将元素添加到尾部 **（`linkLast方法`详解见下文）**

#### add(int index, E element)：
1. 检查`index`是否越界
2. 比较`index`与`size`：
   * 如果`index==size`，则代表插入位置为链表尾部，调用`linkLast方法` **（linkLast方法详解见下文）** ；
   * 否则调用`linkBefore`方法 **（LinkBefore方法详解见下文）**

### 3. set方法
```java
public E set(int index, E element) {    // 替换index位置节点的值为element
    checkElementIndex(index);   // 检查index是否越界
    Node<E> x = node(index);    // 根据index， 调用node方法寻找到目标节点
    E oldVal = x.item;  // 节点的原值
    x.item = element;   // 将节点的item属性设为element
    return oldVal;  //返回节点原值
}
```
1. 检查`index`是否越界
2. 调用`node方法`寻找目标节点 **（node方法详解见下文）**
3. 将目标节点的`item`属性设为`element`

### 4. remove方法
```java
public boolean remove(Object o) {
    if (o == null) {    // 如果o为空, 则遍历链表寻找item属性为空的节点, 并调用unlink方法将该节点移除
        for (Node<E> x = first; x != null; x = x.next) {
            if (x.item == null) {
                unlink(x);
                return true;
            }
        }
    } else {    // 如果o不为空, 则遍历链表寻找item属性跟o相同的节点, 并调用unlink方法将该节点移除
        for (Node<E> x = first; x != null; x = x.next) {
            if (o.equals(x.item)) {
                unlink(x);
                return true;
            }
        }
    }
    return false;
}
 
public E remove(int index) {    // 移除index位置的节点
    checkElementIndex(index);   // 检查index是否越界
    return unlink(node(index)); // 移除index位置的节点
}
```
#### remove(Object o)：
1. 判断`o`是否为`null`，如果`o`为`null`，则遍历链表寻找`item`属性为空的节点，并调用`unlink方法`将该节点移除 **（unlink方法详解见下文）**
2. 如果`o`不为`null`, 则遍历链表寻找`item`属性跟`o`相同的节点，并调用`unlink方法`将该节点移除 **（unlink方法详解见下文）**

#### remove(int index)：
1. 检查`index`是否越界
2. 调用`unlink`方法，移除`index`位置的节点 **（unlink方法详解见下文)**

### 5. clear方法
```java
public void clear() {   // 清除链表的所有节点
    // Clearing all of the links between nodes is "unnecessary", but:
    // - helps a generational GC if the discarded nodes inhabit
    //   more than one generation
    // - is sure to free memory even if there is a reachable Iterator
    for (Node<E> x = first; x != null; ) {  // 从头结点开始遍历将所有节点的属性清空
        Node<E> next = x.next;
        x.item = null;
        x.next = null;
        x.prev = null;
        x = next;
    }
    first = last = null;    // 将头结点和尾节点设为null
    size = 0;
    modCount++;
}
```
1. 从`first节点`开始，遍历将所有节点的属性清空
2. 将`first节点`和`last节点`设为`null`

### 6. linkLast方法
```java
void linkLast(E e) {    // 将e放到链表的最后一个节点
    final Node<E> l = last; // 拿到当前的尾节点l节点
    final Node<E> newNode = new Node<>(l, e, null); // 使用e创建一个新的节点newNode, prev属性为l节点, next属性为null
    last = newNode; // 将当前尾节点设置为上面新创建的节点newNode
    if (l == null)  // 如果l节点为空则代表当前链表为空, 将newNode设置为头结点
        first = newNode;
    else    // 否则将l节点的next属性设置为newNode
        l.next = newNode;
    size++;
    modCount++;
}
```
1. 拿到当前的尾节点`l节点`
2. 使用`e`创建一个新的`节点newNode`，`prev属性`为`l节点`，`next属性`为`null`
3. 将当前尾节点设置为上面新创建的`节点newNode`
4. 如果`l节点`为`空`则代表当前链表为`空`, 将`newNode`设置为头结点，否则将`l节点`的`next属性`设置为`newNode`

**过程如图：**
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/Java基础等/集合/LinkedList详解（JDK1.8）/linkLast方法执行过程.png)
</center>

### 7. linkBefore方法
```java
void linkBefore(E e, Node<E> succ) {    // 将e插入succ节点前面
    // assert succ != null;
    final Node<E> pred = succ.prev; //　拿到succ节点的prev节点
    final Node<E> newNode = new Node<>(pred, e, succ);  // 使用e创建一个新的节点newNode，其中prev属性为pred节点，next属性为succ节点
    succ.prev = newNode;    // 将succ节点的prev属性设置为newNode
    if (pred == null)   // 如果pred节点为null，则代表succ节点为头结点，要把e插入succ前面，因此将first设置为newNode
        first = newNode;
    else    // 否则将pred节点的next属性设为newNode
        pred.next = newNode;
    size++;
    modCount++;
}
```
1. 拿到`succ节点`的`prev节点`
2. 使用`e`创建一个新的`节点newNode`，其中`prev属性`为`pred节点`，`next属性`为`succ节点`
3. 将`succ节点`的`prev属性`设置为`newNode`
4. 如果`pred节点`为`null`，则代表`succ节点`为头结点，要把`e`插入`succ`前面，因此将`first`设置为`newNode`，否则将`pred节点`的`next属性`设为`newNode`

**过程如图：**
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/Java基础等/集合/LinkedList详解（JDK1.8）/linkBefore方法执行过程.png)
</center>

### 8. unlink方法
```java
E unlink(Node<E> x) {   // 移除链表上的x节点
    // assert x != null;
    final E element = x.item;   // x节点的值
    final Node<E> next = x.next;    // x节点的下一个节点
    final Node<E> prev = x.prev;    // x节点的上一个节点
 
    if (prev == null) { // 如果prev为空，则代表x节点为头结点，则将first指向next即可
        first = next;
    } else {    // 否则，x节点不为头结点，
        prev.next = next;   // 将prev节点的next属性指向x节点的next属性
        x.prev = null;  // 将x的prev属性清空
    }
 
    if (next == null) { // 如果next为空，则代表x节点为尾节点，则将last指向prev即可
        last = prev;
    } else {    // 否则，x节点不为尾节点
        next.prev = prev;   // 将next节点的prev属性指向x节点的prev属性
        x.next = null;  // 将x的next属性清空
    }
 
    x.item = null;  // 将x的值清空，以便垃圾收集器回收x对象
    size--;
    modCount++;
    return element;
}
```
1. 定义`element`为`x节点`的值，`next`为`x节点`的下一个节点，`prev`为`x节点`的`上一个节点`
2. 如果`prev`为空，则代表`x节点`为头结点，则将`first`指向`next`即可；  
否则，`x节点`不为头结点，将`prev节点`的`next属性`指向`x节点`的`next属性`，并将`x`的`prev属性`清空
3. 如果`next`为空，则代表`x节点`为尾节点，则将`last`指向`prev`即可；  
否则，`x节点`不为尾节点，将`next节点`的`prev属性`指向`x节点`的`prev属性`，并将`x`的`next属性`清空
4. 将`x`的`item属性`清空，以便垃圾收集器回收`x对象`

**过程如图：**  
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/Java基础等/集合/LinkedList详解（JDK1.8）/unlink方法执行过程.png)
</center>
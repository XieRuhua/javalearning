# LinkedList详解（JDK1.8）
***
[笔记内容参考1：Java集合：ArrayList详解](https://joonwhee.blog.csdn.net/article/details/79247389)

[toc]
## 一、LinkedList简介
LinkedList是基于链表结构的一种集合长。基本数据结构如下：
<center>

![avatar](data:image/png;base64,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)
</center>

ArrayList继承于 `AbstractSequentialList` ，实现了 `List`, `Deque`, `Cloneable`, `java.io.Serializable` 这些接口。

```java
public class LinkedList<E>
    extends AbstractSequentialList<E>
    implements List<E>, Deque<E>, Cloneable, java.io.Serializable{
}
```
* **Deque** 双向队列：支持插入删除元素的线性集合。有如下特性：
    * 插入、删除、获取操作支持两种形式：快速失败和返回null或true/false
    * 既具有FIFO特点又具有LIFO特点，即是队列又是栈
    * 不推荐插入null元素，null作为特定返回值表示队列为空
    * 未定义基于元素相等的equals和hashCode
* ArrayList 实现了 **Cloneable** 接口 ，即覆盖了函数clone()，能被克隆。
* ArrayList 实现了 **java.io.Serializable** 接口，这意味着ArrayList支持序列化，能通过序列化去传输。

### 1.1. ArrayDeque 与 LinkedList 的区别?
ArrayDeque 和 LinkedList 都实现了 Deque 接口，两者都具有队列的功能：
* ArrayDeque 是基于可变长的数组和双指针来实现，而 LinkedList 则通过链表来实现。
* ArrayDeque 不支持存储 NULL 数据，但 LinkedList 支持。
* ArrayDeque 是在 JDK1.6 才被引入的，而LinkedList 早在 JDK1.2 时就已经存在。
* ArrayDeque 插入时可能存在扩容过程, 不过均摊后的插入操作依然为 O(1)。虽然 LinkedList 不需要扩容，但是每次插入数据时均需要申请新的堆空间，均摊性能相比更慢。

从性能的角度上，选用 ArrayDeque 来实现队列要比 LinkedList 更好。**此外，ArrayDeque 也可以用于实现栈。**

### 1.2. Arraylist 与 LinkedList 区别?
1. **是否保证线程安全：** ArrayList 和 LinkedList 都是不同步的，也就是不保证线程安全；
2. **底层数据结构：** Arraylist 底层使用的是 Object 数组；LinkedList 底层使用的是 双向链表 数据结构（JDK1.6 之前为循环链表，JDK1.7 取消了循环。注意双向链表和双向循环链表的区别）
3. **插入和删除是否受元素位置的影响：** 
    * **ArrayList 采用数组存储**，所以插入和删除元素的时间复杂度受元素位置的影响。 比如：执行`add(E e)`方法的时候， ArrayList 会默认在将指定的元素追加到此列表的末尾，这种情况时间复杂度就是 O(1)。但是如果要在指定位置 i 插入和删除元素的话（`add(int index, E element)`）时间复杂度就为 O(n-i)。  
    因为在进行上述操作的时候集合中第 i 和第 i 个元素之后的(n-i)个元素都要执行向后位/向前移一位的操作。 
    * **LinkedList 采用链表存储**，所以对于`add(E e)`方法的插入，删除元素时间复杂度不受元素位置的影响，近似 O(1)，如果是要在指定位置i插入和删除元素的话（`(add(int index, E element)`） 时间复杂度近似为o(n))因为需要先移动到指定位置再插入。
4. **是否支持快速随机访问：** LinkedList 不支持高效的随机元素访问，而 ArrayList 支持。快速随机访问就是通过元素的序号快速获取元素对象(对应于get(int index)方法)。
5. **内存空间占用：** ArrayList 的空 间浪费主要体现在在 list 列表的结尾会预留一定的容量空间，而 LinkedList 的空间花费则体现在它的每一个元素都需要消耗比 ArrayList 更多的空间（因为要存放直接后继和直接前驱以及数据）。

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
1. 校验index是否越界
2. 调用node方法寻找目标节点，并返回目标节点的item（node方法详解见下文）

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
调用linkLast方法将元素添加到尾部（linkLast方法详解见下文）

#### add(int index, E element)：
1. 检查index是否越界
2. 比较index与size，如果index==size，则代表插入位置为链表尾部，调用linkLast方法（linkLast方法详解见下文），否则调用linkBefore方法（LinkBefore方法详解见下文

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
1. 检查index是否越界
2. 调用node方法寻找目标节点（node方法详解见下文）
3. 将目标节点的item属性设为element

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
1. 判断o是否为null，如果o为null，则遍历链表寻找item属性为空的节点，并调用unlink方法将该节点移除（unlink方法详解见下文）
2. 如果o不为null, 则遍历链表寻找item属性跟o相同的节点，并调用unlink方法将该节点移除（unlink方法详解见下文）

#### remove(int index)：
1. 检查index是否越界
2. 调用unlink方法，移除index位置的节点（unlink方法详解见下文

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
1. 从first节点开始，遍历将所有节点的属性清空
2. 将first节点和last节点设为null

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
1. 拿到当前的尾节点l节点
2. 使用e创建一个新的节点newNode，prev属性为l节点，next属性为null
3. 将当前尾节点设置为上面新创建的节点newNode
4. 如果l节点为空则代表当前链表为空, 将newNode设置为头结点，否则将l节点的next属性设置为newNode

**过程如图：**
<center>

![avatar](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAxYAAAGfCAIAAABN/NPJAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABmJLR0QA/wD/AP+gvaeTAAAAB3RJTUUH5QwBEAwH2ebTKgAAgABJREFUeNrs3XlYE1fXAPATGEIIRHYJi4i7VK1CUHBBESsqClZrrUtda9VWa7XWulCtolR9X62Wz9alVmtVrPV1Ra1LQRRRlE1BRKEiIoQAQQKBJCRD5vtjbJoGxAQJCXB+T58+ZHIzOblznZzce+cOUP9WWVlJaU1/hQsLC40hDIwZY8aYMWaMGWPGmDHmevdsAgghhBBCSEeMyspKQ8dQD7FYzOFwDB0FxmyMMGaMGWPGmDFm49TWYiY0XqnTvrAwFsbCWBgLY2EsjIXbZmEcyEMIIYQQ0hmmUAghhBBCOsMUCiGEEEJIZ5hCIYQQQgjpDFMohBBCCCGdYQqFEEIIIaQzTKEQQgghhHSGKRRCCCGEkM50SKHkcvmJEycmTJjA4/EGDhz4zTffZGVljR07lsfjhYWFyWQyQ38WhBBCRufs2bM8Ho/H4509e9bQsSDUlHRIoc6cObNly5b8/HwAkMvlZmZmZmZmTRsNRVEZGRnXrl0zdLUghBBqAfLz80+dOmXoKFAbRWhZTqFQZGdnAwCbzf7++++9vb0VCoVMJrtw4UJThSKVSo8cObJ///41a9YYuloQQggZNblcfvbs2R07dkycONHQsaA2StsUqra2ViqVAkC7du1sbW0BwMzMrGkH765cubJnzx5DVwhCCKEW4OHDh+Hh4YaOArVpWqVQKSkp8+fPp/8WCASTJk0CgH379pmbm69cuVIgEIwePXrt2rUsFisyMvLQoUMAsHXr1oSEhIsXL7q4uHz77beenp6FhYUnT568fv16WVkZAHTr1i0kJGTixIkWFhYymWzjxo2XLl2i34L+VzFr1qwlS5YYun4QQgg1MYqiHj16dOjQocTERLFYTBCEp6fnlClT+vfvrypTVlb2+++/X7x4kc/nA4CLi0twcPDkyZPt7e0BQPVdAwCHDh06dOiQ6mvI0B8OtSGEWCzW2FR3i0QiqftKiURibm5OURQAkCQpFosVCoVcLqef/eGHH+hZUxYWFiwWKz09fe3atQUFBaqX5+TkfPfdd7dv3161apW5uTlJkhr7l8vldSN5Fe1LYmEsjIWxMBZuzsKq8QqZTEa/MCUlZf369aqdkCSZkZGRkZExe/bsDz/8kCCIsrKy8PDw+/fvq3bC5/P3798fFxcXHh7u4uKi+q5RUX0NGXltYOFWVZj6t8rKSqo+Uql0zZo13t7ewcHBubm59MaMjIzg4GBvb+81a9ZIpVKKouhpUt7e3pMnT3769KlCoSgqKlIqlf/3f//n7e09ZMiQGzdu0GOCP//8M13y0qVL9N7OnDlDbzlz5kxhYSGltVfF3MyFMWaMGWPGmDHmuntWP7fTWz755BNvb++vv/5aJBJRFFVaWjp//nxvb++pU6eWlZVRal8HJ06cUCgUCoXiwoULAwYM8Pb23r9/v1KppCjqxo0bdJnvv/8e6xljNkjM2s6F0tWoUaM8PDwAgMvl1tTUlJSUAIBcLn/06NHbb79tbW09d+7cuXPn6undEUIIGScOh/Pjjz8CAEmSAoHgzp07Fy5cuHfvHgCIRKKKigo7O7vCwkK6cHZ2tlAodHJyCg4ODg4ONnTsCP2LvlKobt26qf42Nzfn8XgXLlwgSXLPnj379+/38/ObNGlS//79cdwaIYTaGpFIdPTo0RMnTrxqAMXHx+fYsWMSieTkyZMnT5708vJ69913AwICrKysDB07Qv/Q1+rkbDZb/eGYMWM++eQTJpMJACRJ3rx5c+nSpaGhoUePHsU1ORFCqO2oqKgICws7cOCAWCz28vL6+uuv//e//wUFBamX8fHxWbNmDT1zHADS0tK++eabkSNH7tq1SyQSGfoTIPSSvnqhNDCZzA8++ODDDz/MzMyMi4u7detWXl5eWVnZd999V1xcvGTJEoIgCKKZgkEIIWQof/31V3JyMgDMmTNn4cKFBEHIZDITk3/9njcxMRkzZszIkSMfP36ckJBw48aNnJwcuVx+8ODBvLy88PBwNpttYmJCEETdS5EQajbNeo88FovF4/GWL19+8uTJ06dPd+3aFQDu379fVVUFAFwu19C1gRBCSL8KCgrovKdDhw70L+fKysrc3Ny6JQmC6NWr1/z5848cOXLp0qUhQ4YAQFZWVnFxMQBYW1s7ODgY+tOgNq05UqiKioqFCxcGBARMmDAhLS1NqVQqlcqysjI6c7K3t9e4UUxxcTFJkvRKngghhFoTNzc3OnOKiYkpLS2tqqqKioqi735Bk8vlGzZs4PF4AQEBMTExJElSFFVRUUEP4bVr187S0lJ9hy9evJBKpfRV4Yb+cKhtaY6xM/r6uydPnuTn58+bN0/9KQ6HM2XKFPrfg52dHZfLFQgEe/fu3bt3Ly6tiRBCrU/Xrl19fHwSExMTEhJGjx4NAARBWFtbV1RU1NTU1NTUMJnMGTNmPHjwIDc396uvvlJ/LUEQU6dOdXR0BABra2tHR0eBQBAdHR0dHY1La6Lm10wDeQMGDPjhhx/mzJlDr3QAAC4uLhMnTjxy5MiAAQPoLR4eHl9//TU9ukdfdtHAImkIIYRaImtr64iIiGnTpnE4HIIgfHx8du7cuXPnTjabLRKJ7t27R1FU586df/rpp88//9zT05PusrK3tw8KCvrll19CQkIYDAYA2NjYrFy5kl7QnMlkMhgMnBeFmlvrW+oKY8aYMWaMGWPGmDFmjFnfMTfrdHKEEEIIodYBUyiEEEIIIZ0ZLIVav359VFSUTvf2Qwgh1Mrw+fx9+/ZFRUUZOhCEdGaY1SyTk5Ojo6MBYO/evcOHD58/f76Li4uhqwIhhFDzoZMn+rvAyspq2rRpho4IId0wVHdzpHE4HO17ht6k8O3bt8+dO/fgwQP6oZ+fX0hIyNtvv92Iz9BsMTchjBljxpgx5jYbc3p6+m+//ZaRkUE/DAwMHD9+fOfOnY055uYvjDEbf8wM6t9rkYnFYg6Ho+W+3rwwn8/fu3fv+fPn6YfOzs4LFiwICAgQi8Xa90s1c8yvwufzMWaMGWPGmDHmBvYcHR2tWkjTysoqJCRk2rRpqr0ZZ8yGKowxG3/MBr4tnYuLy4YNG7788suoqKhz584VFRWtX7/eyspqxIgR8+bNw9E9hBBqBcRiMZ08FRUVwd/DdvTSUIYODaHGM4o7+3I4nAULFixYsODcuXPR0dGpqalnz549e/ZsSEjIuHHjfHx8DB0gQgihxigqKjp27NjRo0dV90JdsGBBaGiooeNCqAkYRQqlEhoaGhoa+vjx4/3798fGxtLL9nfv3n3atGkhISGGjg4hhJC21GeLA4C3t/e0adOGDx9u6LgQajLGlULRevTosWzZsmXLlqlGzdevX79t27bp06ePGzcOR/cQQsiYJScnHzt2LC4ujn44bty4kJAQHE9ArY8xplA0FxcX1eheVFRUTk4OffvhkJCQqVOn9ujRw9ABIoQQ+hd66CAlJQUArKysAgICpk+f3r17d0PHhZBeGG8KpUKP7tFLSZ0/f57+J8rj8UJCQnB0DyGEDE4sFsfFxe3du7fubHFcPxm1Yi0ghaL5+Pj4+PgsWLAgKiqK/pWTkpKyd+/e0NDQcePG4WUdCCHU/MRiMc4WR21Wi0mhaC4uLl9++eWCBQuuXbtG/+JRje7hEucIIdRs6s4WDwkJweQJtSktLIWicTgc1eheVFTU9evXVaN706ZNCwgIMHSACCHUaqWnp2/fvl01W3zYsGHTpk3D2eKoDWqRKZQKPbqXnZ199OjRuLg4enTP2dmZXgQBR/cQQqgJxcXFRUVF0bPFAWDcuHELFizA7n/UZrXsFIrm7Oy8YcMGevXbo0ePFhUVbd++HW9gjBBCTSU6Olo1W9zS0nL69Om4tjhCrSGFonE4HPoakGvXrkVFRaWmptKjewEBAVOnTm2gk5nP53M4HDwXIITapqioqFdd3VzvbPGePXviOgUIQWtKoVSGDx8+fPhw1Q2M4+Li4uLiVDcwrlue7pfet28fZlEIobbmm2++OX/+vI+Pj8YJkJ4tfu3aNTp5Up8tzufzDR01QkaBUVlZaegY6qHTbZYb3s/Jkyf/+OOP4uJiALCysho9evR7773n7OysKjB16tSqqiorK6sdO3Z069bN4DE3J4wZY8aY22zMYrF469atN2/eBIBRo0atXr2a3p6Wlnb58uVLly7RD/v27Tt79mwvLy9jiPlNPizGjDE3ecwMiqIavS/9Febz+drPYdJmz6obGNMPVTcwPnfu3IYNG+iNVlZW+/btU1/33LAxN0NhjBljxpjbZsxisXj+/PnZ2dmqLdHR0dnZ2drMFsd6xpgxZlorHMirl+oGxocOHbp8+bLqBsZ07xSdR1ZVVU2bNu2bb77BpU0QQq2YKn9S/YRmMBh0fzz8vbZ4SEgIXouDUMPaSgpF69Gjx+rVqxcvXkzfwPjx48cMBoOiKAaDAQD0Hxs2bKBzKUMHixBCTe/x48fLly8vKiqi8yf6HAgAYrHYyclpxowZuCIMQloyMXQABkDfwPj69esdO3YEADp/ArVTyfbt29evX2/oMBFCqIk9fvx4/vz56vkT/H3qYzAY7777Li5VgJD22mIKRePz+fn5+fD3KB6NPpVQFBUdHb1+/Xq8QSZCqNV4/Pjxxx9/XFVVpZ4/qVPdrQUhpI22m0Lt3bsX/s6fqL+B2mklOjp6yZIlmEUhhFqBc+fOTZs2rbq6Wn3qgsblREVFRefOnTN0pAi1GG00hRKLxfQNnhj/pipAn1mePn0aEhLy+PFjQ8eLEEKNt3fvXtWlxzSNk57qj3379hk6WIRajLY1nVzd9u3b6Wt3xWIxnSRlZ2fTF6So51L0pSsaix0ghFBLERUVpZ4Y0ec3Lpfr4uLC4XDoM5unpyebze7RowdOhEJIe602hZo/f75qdRNd1V0ra+rUqVDf1IG2jMfjtYgfrG/SEpA2eDze9u3bDR3Fa7TZZqBx2R2NwWAIBAKBQAAA169fb5I3aiknBISaUKtNod7kdImpkjZayhdSS4mz5WoRNdwigtSHukN1etJmaxi1Za02haLhv2o94fF4hg5BN9gS9KRltQRsBnrSspoBQk2ljU4nRwghhBB6E5hCIYQQQgjpDFMohBBCCCGdEXWXjtRpMcmWWLhtioyMPHTo0OjRo9euXctisTQeNm6fDVc7Hm5DkcvlmzdvPnfuHJvN3rVrV9++fZvhTY3kcGPbePr06eLFi+mr7VQIgvD09Jw6deqIESMIQl9TYF9V+UZyuLEwFm7ywoTGKiBisVj7dUFaYmHUhBqodiM53G3zC7WwsPDu3bsAIJFIYmJievXqpb9vTRUjOdx4KqgXSZIZGRkZGRmLFy+ePXu2nq7Oq7fyjeRwY2EsrI/COJCHUGuTlJSk6oRITU0tLy83dETIWFy5cqW0tNTQUSDUSmAKpUkkEs2aNYvH4504ceLEiRMTJkzg8XgLFy7MzMyk16ZTFYiKioqIiPD19Z0zZw595/PMzMxFixb5+voGBARs2rSpqKgIAEiS/O6773g83qZNmxQKBf0uJSUlU6dO5fF48fHxAJCSksLj8Xg83qsuuo6MjOTxeGFhYWlpaStWrBg4cGBAQMDBgwdlMpl6SGfPnqXLy2SysLAw+iV0GdS0zp49y+PxZs2alZqaqjoiBw4ckEqlGgUuX74cHBw8cODAqKgoAJBKpQcPHgwKCuLxeB9++OHly5dJkgSAnJycUaNG+fv7Z2RkqN4lKiqKx+N98cUX1dXVWh5T1c2LJk2a5OHhkZWVlZqaaujaarWMthkAwL59+1L+dufOndWrVwNAZWVldXW1oasNoVYCU6hXioyM3LJlS35+PgAkJSUtWrQoKSlJvcDu3btPnTpFkqStrW27du3oMomJiSRJisXi06dPf/rpp3l5eQRB+Pn5EQSRlpZWUlJCv/bx48fZ2dmenp49e/bUPqS4uLiFCxfGxsbK5XKxWLxr165jx45prKWOmtOjR48+++wz1RH54YcfNm/eLJFI1AuEh4cXFxfL5fIOHTpIJJLNmzfv2rWrrKwMALKystasWXPgwAGSJF1dXfv06SORSFTNrLq6Ojk5GQD8/PwsLS21DCk3NzcjI8PBweHdd98dPHgwAFy9elU9JNTkjLAZaCBJUi6XA4Cjo6ONjY2hKwyhVgJTqFcyNTWNjIxMSko6ffp03759xWLx77//rn5abNeuXVRUVFJS0urVq0mSPHDggFgsnjt3bkJCQmxsbHBwcH5+Pp1j9erVy8vLKy8v78GDBwCgUCjomyp4e3vb2tpqHxJJksuWLUtISLhw4YK3tzcAJCUl0ff1QwZBkmRgYGBsbOzt27dXrlxJEMTly5fv3bunXmDKlCm3b9+Oi4vz8fGJj4+/cOGCu7v70aNH7969GxkZyeFwTp48+fTpUzabPXLkSAC4e/duRUUFAOTm5iYlJTk4OHh5eWkfT0xMjEQi8fHx6dSp04gRI9hs9r179+hfAkhPjK0Z0ObPn8/72+DBg7dv387hcObOnavTOQch1ABMoV5pxowZgwYNMjExcXd3nzNnDgBkZWUVFxerCgwbNqxLly4mJiaOjo75+fmZmZlcLjc4OJjFYllbW4eEhABAenq6WCxu165d//79ASAxMVEul5eUlKSlpbHZbNXVMfQQHj2c10BInp6eo0aNYrFYXC53+PDhAFBdXV1bW2voqmq73N3dFyxYYG1tzWQyx44dO3jwYJIk6T4Dmq2t7ciRI5lMJofDIQiC7loYPnx4z549TU1Nvb29Bw4cKBQKHz58CAC9evVyd3fPzMzMy8sDgKSkJIlEMmjQoI4dOwIAi8WKiIhISUmJiIh41UWU5eXl9LDd0KFDWSyWh4dHr169ysvLExISsLdSf4ytGbyKj49P586dDV1bCLUemEK9koODg+q6FTc3Ny6XKxAIXrx4oSrg5uamutCpuLhYIpEIBIJJkybRP/s++eQTACgtLRWJRAwGY/Dgwba2tvfu3SspKcnKysrLy+vVq5eHh4dOIbm6ulpYWNB/N7pLHzWhdu3aWVlZ0X9bWlrSB7S4uFg1ScXR0dHOzo7+WyaT8fl8ADh06BDdSIYMGXLlyhUAePbsGQBwudyBAwdKJJLk5OSKigrV8A2TydQynvv372dlZQHAmjVreDxeYGAg/W197do1oVBo6NpqtYytGbzKtWvXPvvsMzozQwi9OUyhGk+bJIaiKKVSCQDu7u79+vXLz89PT09PTEwEgAEDBlhbWxv6QyD9YjKZ2nzzKZVKiqIIghgyZAhBECkpKQ8ePMjIyPDw8Ojdu7eW7yWXyxMSEup9Kisr6/79+4aujLarOZuBivp08qSkpN9//7137975+fmxsbGGrg+EWolWfpvhN/HkyROSJOl+poKCAoFA4Obm5uDgUG9he3t7giC4XG5kZCTd366BzWb7+/tfu3btt99+Kysrc3Bw8Pf3b/KYVdfa1NbWqq4JQvojEAhKS0vp+bnV1dX073tXV9d6R1iYTCbdfj766KNPP/203h16enp6enpmZGQcPnxYIpEMHjzYyclJy2CePXt269atVz2bkJAwdOjQN+/JQHUZVTOoF4PBMDU1pf/G2ZMINRXshXqlc+fOxcfHK5VKPp//66+/AkC3bt0cHR3rLezh4eHp6VlQUHD69GmpVCqVSrdt28bj8b788kvVDHQej0dPcRAIBH369HF1dVW9/LWLGjTMzMzM3t4eABITE0tLS+Vy+YULF17VIYGakFAoPHDgQFlZGUmSly9fTkhIIAiiX79+9RY2Nzen57pdvXo1PT1dqVTeu3dv7Nixvr6+qtTHxsbG39+fviBLdS0n/dRrr2ZPS0sTCoUeHh7nzp1LUbNy5UoAuHXrFj1OhJqcUTUDFfXp5D4+Pu+99x59OUu9v/EQQo2AvVCvZGJismrVKnqxFgDgcDhTp05ls9n0tcEabG1tZ8yY8fXXXx8+fPjw4cMaL6Eftm/fnh7LAwB/f3/V9jfHZrP79Olz/fr1hISE0aNHAwBBEARBqIJHesJkMm/duhUUFKTaEhISQl8sWa+AgIBr167Fx8fTFyjUfQmDwfDx8WGz2RKJhO6K0DKSiooKeoDGy8urffv26k/179+fnsl348aNrl276mll6rbMeJrBa/Xv318f/d8ItU3YC/VKixYtWrt2rbu7O/0rcPfu3Q1fLhcYGLh///4hQ4bQ8x4CAwP37t2r/hJ6IwC4u7s3vCtdMRiMqVOnfvbZZ/R4oo+Pz86dO4cOHWroKmz9unfvvnv37qCgICaTaW9v/9lnn61ataqB66Ssra03b968ePFiFxcXAHB3d1++fLnGS7p27Upfv+nv76/9Ej55eXmZmZkA4OfnZ2Zmpv6Uq6vrgAEDACApKamystLQddYKGU8zaICLi8u8efMiIiJUE9sRQm+K+rfKykpKa/orXFhY+IZ79vb29vb21n4nKuXl5TNnzvT29j5z5kwjXt5GvLZ6jadtNLolNOzMmTPe3t4zZ84sLy9v8p23IHT1Gv95A5uBXjVQvcbfNjBmjLnRe8ZeKIQQQgghnRF1b2Wv083tW2Jh1FQarnY83G2KkRxubBsG9KrKN5LDjYWxcJMXJjgcjsZzGlsa3lGLK4yaUAPVbiSHG79Qm42RHG48FRhQvZVvJIcbC2NhfRTGK/I02djYHDp0yNBRIGM3fvz48ePHGzoKZGDYDBBqy3AuFEIIIYSQzjCFQgghhBDSGaZQCCGE2hDq71uXNkwul//6669nz57VKEyS5MWLF7Ozs+vdSXV1dURExOnTp3W6sfeePXvWrl0bGxurupsFahFwLhRCCKE2pLKycuXKle7u7q9aZVQulzOZzIyMjMTERIIgKIoKDQ01MXnZ41BeXh4VFVVQUPCf//yHXrRWnUgkSk1NvXXr1ltvvfWqe6rWxWQyL1686OjoSC+/rAojPj6+V69euBqq0cIUCiGEUBvy4sWL58+fS6XS77//XrXyO0mSkZGR58+fX7lypa+vbwMrwufk5OTk5Lz//vteXl537949duxY//79J02aRN/DOzc3Ny8vLzQ0tFOnTgAgl8tLSkpcXV3pGyvV1tbev3//7t27tbW16vt89OgRAKSlpe3Zs4feUltbm5CQ8Pjx4759+27cuFH9nqrIeGAKpbPIyMhDhw6NHj167dq1LBZLJpMlJibGxcUtXbq0Se7D0Gj3799fvHixRCIJDQ1dvXo1/e8Z6Y+xtQQ6Ho2N9vb2w4YNmzt3rrOzs6ErrHUytmZAKysrO3369J9//pmTk8NkMr29vT/88ENfX19VVwrSIBAI4uPjJ0+ePGLECKlUCgBKpVIsFltbW6sXI0kyMTGRJEk7O7tvvvnm8uXLAHDjxo1bt255e3vL5fK0tDQAKC8vP3DggFwuj4mJqaioWL16dVBQEIPBMDU17du3b8+ePU1NTVW3jgaAs2fPxsfHe3l5LVy4ULVxwoQJ9C2AkNHCFOpNXb58OTw8vHfv3oYNg6Ko+Ph4ehz91q1bz54969atm6HrRi+qqqoMHUL9jKQlaCgrKzt16tS9e/d27Njh5uZm6HCajNEuAWUMzSAtLe3rr78WCAT0Q7lcnpiYmJiY+PHHH8+bN0/9mxulpaX9+OOPEydO/OuvvywsLLp3756SkiKRSFgsVkxMzIULF5YuXfr++++rUk860xo9evS0adNYLNa3334rEAj+85//XL9+ffLkyZ07d75586aHh8eKFSvofqMlS5bUfVNzc/PXBiaXy7Ozsx0cHPDHsDHDf0s6W7JkSb3/KgxLKBQmJiaq/k5LS2utKdS5c+eio6OHDx8eEBAQEBBgwEiMsyXUKzc398aNG9OmTTN0IE0mKioqKioKm0FdeXl54eHhqvxJ3cGDB7t06TJy5EhDx2hE8vPzU1NTx40b99lnn3322Wf0RrFYbGZmdv78eblc3qlTJ1X+RFHUzZs3y8vLp0yZwmKxKIoSCoVMJnPs2LHvvfeer6/v3bt3c3JyunXrlpmZyWazbWxs6PE7DWKx+OnTp3RfF+3p06cAUFRUdOfOHQCoqqo6duxYWlralClTFi1axGazDV1PqH7YqauzyMhIHo8XFhYmEonCwsLCw8MB4MGDByNGjAgLC5PJZBRFZWZmLlq0yNfXNyAgYNOmTUVFRfRrRSLRrFmzeDzeyZMnz58/P2HCBF9f3xUrVhQVFRUVFa1evXrgwIHBwcEnTpwgSZJ+SUpKCo/H4/F4KSkpDUR1//79rKwsT0/P0NBQAIiNja2oqDB0VelLVVVVdHT08uXLhw0btn79+ri4OIOEYZwtYfTo0QkJCSl/O3fuXN++fQFAp+uDWgRsBnWDoSgqJiYmPz+fIIiFCxfGxsampKTEx8evWrWKyWSSJBkXFyeTyQxSUcZJY05SXaampqq/i4uL6X9QYrH42rVrS5cuHTdu3Pnz54cNGzZ48GAAuHnzJgD0799/48aNH3744ZMnT+rdJ4fDeeutt/r16+f7N3rilLOzM/1wxIgR+/fvj46OXrFiBeZPxgx7oZpeUlLSV199Rd9aRCwWnz59OiUlZceOHR4eHqoyO3fuVF28GhsbKxKJampqMjMzAaC4uHjbtm02Njba/1iUy+UJCQkA4O3tPWbMmFu3bqWlpWVmZg4aNMjQlaEvFEXB31+i0dHRVlZWxtAhoaH5W0LdWlIoFPSXRMeOHQ1dH01PoxlYWloGBga25WZQVVVFp1bvv//+nDlz6DE7Nps9YcIEPp/PYDAmTpyozShS21FQUAAA165dU+W1ACCXy01MTLKzs9VLUhT1xx9/dO3ade7cud98841QKNy1a1enTp3EYrGpqSlJkgKB4Pbt256enkOGDLly5YqDg4ODg4NEIlEqlVZWVhrvSxCENiOqUqn02rVrfn5+eFGeccIUqvFYLFZERMSAAQPoqQ/0xR0VFRUHDhwQi8Vz58796KOPampqtm3bdvHixVOnTqn39js4OGzYsKFXr14///zz3r17U1NTg4KCduzYoVAo1qxZc//+/bS0tOHDh2s5a+HZs2e3bt0iCGLYsGFdunQZNGjQuXPnbt68OWDAgNY674HuHqcoisFgUBSlnkv5+PjQX6LNNlfGeFoCAFy6dOnSpUsaG995550RI0Y0T200J41mUF1d3cabwYsXLwoLCwHA19dXvTBBEJ9//nnzH6CWYvjw4eo36qEH8oqKinJzc9WLTZ482cLCorKykn4okUiysrKeP39+69atlJQUR0fH/Pz8Xr16Xb58ubKykiTJ7du3x8fHu7u7h4eHe3h4SKXS2NjY4uLiugtK1b0iDwBevHhx586dgoICvCjPaLXO71cDys/Pz8zM5HK5wcHBLBaLxWKFhIRcvHgxPT1dLBarxsWHDRvWp08fBoPB4/HoLRMmTLC3t6co6u23375//35FRQVJkgRBvHbgBgDS0tKEQmH//v27du3KZDL9/PzOnTt3+/ZtgUCg1xnEquANha5P+utTlUvFxcXRYzoBAQF+fn70U80fm0FaQr1sbW2HDBmi10mphu31eW0zCAgIaCPNQKlU0kN+OPrT5BgMhqWlpfoWNpttbW1tYmJy/fp1qVS6bNmympqa9u3b0+sRODg4LF++fOPGjaryFhYWgYGBBEGYm5urz6+Kjo4+ffp0t27d+vTpo5rvT1HUtWvXlixZUrcHCxkPgs/nqz/mcDgaWxqgv8IAoL8961VxcbFEIpFIJJMmTVLfXlpaKhKJbG1t6Yft27dXP6FzuVxHR0cAYDAYul51LBaL6a+KpKQk9WXZ8vPzb926NXnyZENXSTOhx3TUSaXSuhubTfO3hFcpLy9fv359UVHR3LlzW2uvpEq9zaC8vNxQ8RiqGRhkket6z8NG+J1SUlJSW1tLEERJSQl9he8ff/yhPmxnbm4ukUgePnwIAEKhkH5hbW1tTk5Oenp6VVUVn8+XSqX//e9/09LS+vXrV11dTRCERCLp0KEDABQVFdXW1ioUCoFAoHEgOByORmu8f//+9u3b+/Tp4+/vHxUVNWzYMGdnZ6VSGRsbu3v3bh8fn4ULF6raiUGqzki+u40zZkJj2QmxWKz9QhT6K8zn8/W0Z0PRuKWAxq+ZN5Gbm5uRkVHvU3FxcWPGjNHfQEYDv4Z1uuZcp8Lbtm07duwY/bfq+1L19WNlZcXj8QICAoYPH87hcMRi8datW/X08RtHfy2BplqgiH4okUjOnDmzffv2y5cvjx07Vk9jAXFxcXo63K8qvHfv3n379tF/v7YZAMD333+vjw/eaHpqBnZ2dk5OTgKB4M6dOwMHDlRlzBRFHT169MWLFxMnTlQt89jk6j0PG+F3Cj3KxuVy3d3dra2t/fz8PvroI29v76dPny5evNjBwSEiIsLBweG///1vnz59evTooXphhw4dBg8eLBaLc3JyhELhihUrOnXqVFpaunPnzrKysvbt29Mla2pqTE1NzczMuFyulZVVYWGhq6srfSw0Ys7IyNi3b5+dnd2yZcvatWsXHR0tFAq9vLzOnTsXFRX1ySefTJkyRcv+YyOs57YQcyv/Sdr87O3tCYLgcrmRkZF1J/CKRKKmfTuSJGNiYl71izMjIyM3N5e+IKuVob811b8y6fGa4cOHGzq0l5q5JbyKqg9DJpPJ5XJD10oT02gGlpaW9FUFbbYZWFpa9u7d+/79+ydOnLC2tp48ebK1tbVEIrly5cr+/fvFYvHDhw+3bt2qsVxkW1NdXV1eXm5tbU0QxKJFiwCgqqpK418Hi8Vau3Zt3deam5urL0agQpJkVlZWSUkJAAgEgpqamsrKyuvXr0dHR2dkZHz00UcafcD0Sn6bNm0qKyvbvn17ly5dACA0NPTChQuFhYUlJSVHjx6tqanBRaGMHKZQTaO2tpYkyZqamo4dO3p6emZkZJw+fXrBggUA8MMPPxw7dmz48OH01c66SklJmT9/PgDs27ev7tyj8vLy1NRUAFi0aNHcuXNV20tLS5ctW5aVlRUTE9OrV6/WN3xDf2saYeZkqJagUu90cgBwdHQ07Or5+qDRDNQ7DAzLUM2AIIiJEyfGx8fn5+fv2bNHfW4ybcyYMW08fwIAetEsNzc3+sSYkZGxbt26zp07v/vuuwAgEol+++23nj17BgQEaD8PiSAIuvlZWFg8ffrU3Ny8Xbt2w4YNU5+lriKVSo8cOZKcnOzs7FxWVqbqZ33nnXdiY2NjY2M3b95sb29vPBNU0KvgulBvir7WNCsra9SoUeHh4Ww2e8aMGUwm8/Dhw0OGDBkyZMixY8c4HM7UqVP1McEzNTU1KyuLzWb3799ffbuDg4Ofnx8AxMfH17vIXovG5XLHjRu3bdu269evb9iwwUjyJ8O2hIYRBDFp0iRtZlS0INgM6uXh4bFu3Toul1v3qSlTpuC6mhRFPX36lM54ACAtLW3VqlXV1dXjxo2j828bG5vJkyebmJhMnDgxPDw8Ozu77gV0KlKp9K+//qKn8JuYmFhYWDT87iRJxsfHf/zxx2w2e+vWrRqX+9jZ2S1atKikpCQsLOxVa0oho4Ip1Jvi8XgzZ87kcDhMJpPNZlMUFRgYuH//fvoaKCaTGRgYuHfvXn1cvEbftwEA+vTpo77GDAAwGAx/f382m01fEGToSmpKdF+38XxlqhiwJTSAvkJz586dwcHBhq6hpjRt2jRsBq/i5eX166+/zps3j84J6Dawa9eu5cuX45V6lZWVDx488PLy6tq1a05OTnh4uL29/e7du4cPH64a9TYxMQkODt66deudO3emTp26Zs2aukOuFEVdv3599erVGne7A4Campqampq6b/3s2bOjR49aWFgcPHhw+vTpqgmLNKVSmZmZSZLk5s2by8rKPvzww99//91o72eFXqL+rbKyktKa/goXFha+4Z69vb29vb213wnSyWur13jaBrYEvaKr1/jPG9gM9KqB6jW2tpGQkDBo0KAbN26kp6dPnDjxv//9r1gspp/Kzc0NDg6eOXPm8+fP6S137twZNmzYkCFD0tPTVbsqKiqaPHmyt7f3p59++uzZsx9//NHPz2/IkCE3b95UKpUURSUnJ3t7e8+cObO8vLyBmKVS6Zo1a7y9ve/cuXPr1q1PPvnk7NmzNTU1FEUJhcItW7YMGDDAz89v2bJlx48fz8zMVCgUBqm6Zv7ublkxt7YpMgghhFC9qqqqTp48OWPGDFNT0+PHj2/durVLly4URaWmph46dIi+PcugQYNU43H9+/f/6quvkpKS6NUKaO3bt1+6dOnZs2dDQ0PXrl376NGjjz76qF+/fps3b3Z3dx87diwALFq0qG/fvqWlpY8fP1YqlUVFRSNGjNCYhSYSif766y8A+OyzzyZOnLhx40Z7e3v6KXt7+6+++uqdd95JSEg4c+bMgAEDOnfu3PqmtLYCeEgQQgi1Cbdu3bKyspo5cyabzVbd/4rBYHh7e7/99tv79u2zsrKaMGGCqjyDwQgODtYYBDcxMRk4cODAgQOVSiWDwaiqqhoxYoSJicmxY8eSkpKuXr2al5dXXV39ww8/0OUdHBx27txZdxa/k5PTypUro6Ki5syZ89Zbb2msNMFgMJydnZcsWbJ48WIGg2GQhWHRa2EKhRBCqE0ICgoKCgqq9ymCID799FP6b/qGhq9F51JisZieRMVisfz9/f39/bUMhk7dvL29X/suhq429Ep4bBBCCCGEdIYpFEIIIYSQzjCFQgghhBDSGaZQCCGEEEI6wxQKIYQQQkhnRN1LD7S8GKHlFkZNpeFqx8PdphjJ4ca2YUCvqnwjOdxYGAs3eWFCdYND1XMaWxreUYsrbORkMlliYmJcXNzSpUu1vClsZGTkoUOHNDba29sPGzZs7ty5zs7O+ou2gWo3ksPdcr9QG9ESaGVlZadPn/7zzz9zcnKYTKa3t/eHH37o6+ur70ujjeRwt7hTAb048qlTp7p27dpsN+F5+vTp4sWLBQIBfa9ijYeN3m29lW8khxsLY2F9FMaBPONy+fLl5cuXP3369A33U1ZWdurUqSVLlhQUFBj6M6HGaFxLSEtLmzlz5u7du3NycuDvuyguXrx437599J1QkbGpqKgICws7dOiQQqEwdCwIId1gCtWa5ebm3rhxw9BRoGaSl5cXHh4uEAjqPnXw4MFr164ZOkCEEGpVMIXSWWRkJI/HCwsLS0tLW7FixcCBAwMCAg4ePCiTyegCFEVlZmYuWrTI19c3ICBg06ZNRUVF9FNZWVmjRo3i8Xjbtm0jSZKiqIMHD/J4vLFjx2ZmZoaFhYWHhwPAgwcPRowYERYWJpPJUlJSeDwej8dLSUlpIKrRo0cnJCSk/O3cuXN9+/YFAKFQaOgKa7WMqiVQFBUTE5Ofn08QxMKFC2NjY1NSUuLj41etWsVkMkmSjIuLUwWGdPL06dOxY8fyeLyEhISoqKgJEybweLyFCxdmZWWpykil0oMHDwYFBfF4vA8//PDy5ct0tx9Jktu2bePxeKNGjaLLFxQUvP/++zweb9euXXfv3h0xYsSDBw8AIDw8nD64MpksLCyMblr1HrLXxnP27Fkejzdr1iyRSERv0fI0ghDSCd7gpZHi4uL+/PNP+iwpl8t37doFALNnz2YwGElJSV999RU9C0csFp8+fTolJWXHjh0eHh49e/acMmXKrl27rl69OnbsWJIk6WlMH3/8cefOnZsqNoqiFApFbW0tAHTs2NHQVdXKGUlLqKqqor8d33///Tlz5tB3JGWz2RMmTODz+QwGY+LEiebm5oaurZZt1apVEomE/jspKWndunU7duxwc3OTSCRbtmy5cOEC/VRWVtaaNWsWLFgwd+5cgiCmTJly586d3NzcCxcudOzY8dChQ7m5uX379v3ggw/y8/P1EY+h6wmhtgJ7oRqJJMlly5YlJCRcuHCBvslRUlJSVVVVRUXFgQMHxGLx3LlzExISYmNjg4OD8/PzT506RZIkg8EYP358//79hULhgQMHdu/eLRaL6ds2WVhYRERErFu3DgB69+4dExMTERHBYrG0jOfSpUuDBw+mf2j6+Pi89957Dx48eOedd0aMGGHoqmrljKQlvHjxorCwEAB8fX3V7+hOEMTnn3++ZMkSNzc3vFPpG+rWrdvJkyfv3r27du1agiByc3MfPXoEAPHx8RcuXHB3dz969Ojdu3cjIyM5HM7JkyfpqWxubm6zZs0iCOL8+fP79u07d+4cm83++OOPHR0deTxeTExM7969AWDdunV0X9Gbx4MQah6YQjWSp6fnqFGjWCwWl8sdPnw4AFRXV9fW1ubn52dmZnK53ODgYBaLZW1tHRISAgDp6el0b4Sdnd2sWbPYbHZsbOydO3ccHBzo24a/6o3ovnddz60AYGtrO2TIECaTaeiqauWMpCUolUq6J6yBPaA3NH78eA8PD1NT00GDBtGdhdXV1QqFIikpCQCGDx/es2dPU1NTb2/vgQMHCoXChw8f0i8MDAwMDAwUi8WHDx8mSZLOnl/1LiwWKyIiIiUl5bWpc73xGLqSEGpDcCCvkVxdXS0sLOi/LS0tVduLi4slEolEIpk0aZJ6+dLSUpFIZGtrCwD9+/cfP378sWPHAGDmzJk9e/bUR4Tl5eXr168vKiqiRxMMXWGtlrG1BNXIDmpyqjEyJpOp+nEik8n4fD4AHDp0SGN5kWfPntF/sNnsmTNnpqamCoXCrl27fvjhh03yT7LeeBBCzQZ7oZoJRVFKpZL+u7q6WnWxempqapP8cNSYTh4fH798+XIAuHz5cnFxsaE/PfqHnlqCnZ2dk5MTANy5c0d9/QKKoo4cORIZGVlQUEBRlKE/fduiVCpVdV5QUEBP7s7Ly6OXnEAItXTYOdHE7O3tCYLgcrmRkZH1TuWmKOqPP/5ITEykH8bFxZ0/f/6DDz5o2nkqqnUUZTKZXC43dK20Rc3cEiwtLXv37n3//v0TJ05YW1tPnjzZ2tpaIpFcuXJl//79YrH44cOHW7dutba2NnTFtDZMJtPBwQEAPvroo08//bTeMgKB4ODBg6pr9Hbv3t2tWzcul6vXwORyuerfPvZNIqQP2AvVxDw8PDw9PQsKCk6fPi2VSqVSKX1J85dffkmfxR49enTw4EEAWLp06ezZswHg8OHDT548Ud9JbW0tSZI1NTUURWl5NbL6dHIejzd48ODt27cDgKOjo05rW6Om0swtgSCIiRMnuru7kyS5Z8+ewMBAHo/n7++/ceNGeurVmDFjMH/SB3Nzc3p22tWrV9PT05VK5b1798aOHevr63vr1i0AIEnyyJEjjx8/7tGjx86dO7lc7uPHj//3v/9pLHaqUCgUCgVJkq9d1OC17OzsACA3Nzc1NVWpVObn59MtDSHUtDCFamK2trYzZsxgMpmHDx8eMmTIkCFDjh07xuFwpk6dymazJRLJr7/+KhQK/fz8QkND33///R49eggEgp9//pn+WqXPffSiQeHh4TU1NW8SDEEQkyZNoqfdoGbW/C3Bw8Nj3bp19fZtTJkyZeTIkYauklYrICDA398/Pz9/zpw5/fv3/+ijjwQCwZgxY1RXaJ49e5YgiDlz5gwZMmTGjBkAcPz4cXoSupmZmb29PQBs3rzZz8/v/v37bx5Pp06dOnfuTJJkWFhY//79J0yYgEOHCOkDplBNLzAwcP/+/fTVcEwmMzAwcO/evTwej6KoK1euXLlyhcPhLFy40Nramsvl0kv40NspiuLxeDNnzuRwOEwmk81mN3ryCpPJ9PPz27lzZ7PddQvV1fwtwcvL69dff503b56Liwv83Qx27dq1fPlyvFJPf6ytrTdv3rx48WK62t3d3ZcvX75q1SoWi1VaWvrTTz9JJJLQ0NBhw4YxGIwxY8b4+flJJJKffvqptLTU0tJyxowZnp6eAODi4tIk89Xc3NzCw8P9/PwIgrC3t1+wYMHGjRsNXUkItUIMjX+xRnInPz6fT5+MGr1numsdl+LVk9dWr/G0jYCAAMCWoDd0S4iLizPy8waeEPSqgeptNd8pGDPGXHfPRN1b2et0c/uWWBg1lYarHQ93m2IkhxvbhgG9qvKN5HBjYSzc5IUJjUzNSLJC/RVGTaiBajeSw41fqM3GSA43ngoMqN7KN5LDjYWxsD4K41wohBBCCCGdYQqFEEIIIaSzVr60pq73lUOtFbYEBNgMEEJNqtX2QtErsiD9aSk13FLibLlaRA23iCBbNKxh1Aa12l6on376qd7txnlhpKEK6y9m4/GqlvCGH9BI6tl4YtaypKHUbQYttJ5bXMwItWKtthcKIYQQQkh/MIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTqCbz6NGjXbt25eTkkCRJb7l48WJkZORff/2lVCq1309aWtoXX3xx/vx547/KCSGEEGqzMIVqMgqF4uDBg5s2bRIIBKothw4d+vnnnyUSifb7USqV169f//PPPw39gRBCCCH0SphCNTE3NzcHBwf1Lc7OzlZWVhRF5efn//bbb1qmU5aWlmZmZqqHFEU9e/ZMKBTWW/jWrVu+vr48Ho/H4x0+fJiiKENXA0IIIdTKEXVHi3QaP2qzhXNzc+/evSuVSlVbCgoKAODRo0c//vgjQRAAkJ2dDQDJycmRkZHPnz+/ceMGSZIpKSmff/65tbX1q/ZM51jFxcU3btygsyilUnnz5s2LFy+6ubmtXbu2S5cu6uVJkoyNjVWNHqalpRUWFlpbWxtt1WFhLIyFsTAWxsKtoDChsSKtkax+a/yF+/bt+9ZbbwGAqq/o8uXLMTExPXv2/PTTT1ksFgCcPXv29u3bPj4+S5Ys0X7PbDYbAJycnIYOHUrvRywWjxgx4ptvvqm3fEFBQUpKiuphenp6fn7+oEGDjLbq2lThmpqaX375xdbWdtSoUXReKxKJdu7cOWTIED8/PysrKy33LJPJIiMjLSwsAgMD33rrLQaDYSQfEAtrU5huBl26dOnfv79GM+jYsaP2K32XlpYePHiwbjMw+AfEwli4bRbGgbzGMzMzUx9rexWlUqnXkbXMzMz8/HwAmD59uoODA0mSV69elcvlhq4eBABAD+Bu3br1jz/+UPUUPn36dMOGDffv39epYVRUVPzyyy+lpaUNf3EiI0Q3g5UrV9ZtBllZWdgMEGqhWu098pqfubn57NmzAwMDzc3N6S1du3bdt2+fp6cnAJSUlNjY2DCZzLovVCqVDAajgRMiRVFSqZTFYtUtI5PJbty4AQAeHh7jx48vKyu7dOnSvXv3SkpK3NzcDF0l6B/dunWjh3dp7dq1c3FxYTAYMpksNja2Q4cOffr00WY/Gr+WpFJpYWFh165dVTuPjIw8dOhQvS/09PScOXOmr6+viQn+djKMus3AycmpSZrBs2fP1JsBjaKoJ0+eHD9+PDExkc/nEwTh6ek5atSoMWPG2NjYGLoyEGrxMIVqvNra2ufPn5eWltJrFkgkkgEDBlRVVd29e1e9WEpKyrlz527cuDFu3LgVK1bQY3Pqnj17tmbNmm7dutH9+fQFfdnZ2fv376dPiE+ePLl169aCBQumTZumcYp8/vx5cnIyAHh5ebm7uw8dOvTSpUv5+fm3bt2aPHmyoWuozZFKpfHx8Xl5eaplLEiSpKfERUdHJyUlAYBMJhMIBBKJ5Pjx42w2OyYmpqCggMPhrF+/ftiwYa/tWnj06JGqG0MoFO7Zs6ekpOSjjz6aPXt2vQm6ilgsvnv37t27dz/++ON58+ZpNCTUhKRS6e3bt7VsBufPn79z584bNoN9+/YJBAKNZiCRSPbt2/f777+rSpIkmZGRkZGRceTIkU2bNnl5eRm6qhBq2fA02nimpqYeHh7Ozs6mpqYEQdB3L6f7ANatWzd+/Hi6mEwmu3TpEkmSvXr1qps/0SorK1NSUubMmdOpUycAWL9+veopmUz2zTffyGSyDh06mJqaarwwKSmJvkzPz8/PzMysd+/e7u7u+fn5cXFxY8aM0X58FzUJCwuLkSNHymQyVZehTCYrKirKzc0NCQnh8XgAIBKJ0tLShELhBx980KlTp7rz5BrWs2dPej+0oUOH6nqUf/vtt6FDh9Iz+ZA+6NQMxo0b5+vr+4bNYOzYsRoFSJI8fvx4VFRUvS8XCATh4eE7duzw8PAwdG0h1IJhf/6bMjc31/IHfd0EiGZiYqLNHtq1a6fx21QsFt+8eRMAunfv/vbbbwOAk5OTr68vAGRkZOTm5hq6btoiBoNhYWHx2l4EiqJ0WnC1Efbt25ei5tKlS4GBgQAgFotzcnIMXU+tnMGbwd27d48ePQoAHA5n1apVsbGxKSkpiYmJO3bs4HK5AJCfnx8TE4MLoCD0JrAXyvCsra1tbGxeteZTA3JzczMyMgDAy8vLzs4OAAiC8PHxOX36tEQiiYmJ6dWrF47XGBaDwejSpcvSpUu7d+9ObzEzM5s1a1aPHj2cnZ2lUml1dbXGQmIqJEk2fPgUCoVCodAyEkdHRx8fn9jYWADAVtHM6GawYcOGus2Anun4hs0A1C4NprfQC50QBLFx40Z/f3/Vmw4dOpTJZB45cuTdd9/18/PDOekIvQk8kxqeUqmsra3V9VUURcXHx9OLSB0/fvz48eMaBZKSkl68eNG+fXtDf742RywWP336VLVmWK9evcrKyh4+fKgqYGlpWVBQEB8f/+uvv5IkuXnzZvVBGZU9e/YkJyd7e3szmcy6k2nkcnlMTIyVlVVERMRrh2MoiiouLqanzXG5XBzFawZ1mwEA1G0G9+7dO3v2rJbNQCKR1NsMrK2tw8PDVc1ALBY/evQIALy8vOj+aXV+fn5+fn6Grh6EWgNMoQyvoqKivLy8pqYmPT29pKRE41m5XF5WVlb3VUKhMDExsYHdZmdnp6WljRo1ytCfr83hcDi9e/euqamxsLCgt9y5cyc8PNzBweH7779XXQlFEERxcbGnpyc9Aa4upVKZkZHh7e29cOFCAFi8eLH6sykpKYcOHfLz87O1ta335fPnz6+7kclkfvLJJzgDphnUbQZPnz5dvHixRjMQiUTaNwOxWPzFF1+oP0s3Aw8PD/VmQJ9SAMDNzY1eZw4hpA+YQhkLc3Pzt99+u+5pVCaTnT9/3t7eXuN6q5ycnNfOaLl69aq/vz+eQ5ufiYmJ6ouzYaampq9aYkCb4TYrKyvVIhraGDhwYL9+/XD4pnkYvBm0a9dOm7XrEEKNgymUvjx79iwmJiY1NdXS0vLBgwcAYGlpWW9JNpu9cePGHj161FvA3Nz8iy++YLPZ6udi9bkOO3bsUF+LXCwWK5XKlStXJiUl3bt3Lz8/v2fPnoauDNQYrq6uTb7P69evp6am/uc//xkwYIChPx/Syps0g8rKSoVCgVkUQnqCV+TpS8eOHefOnfvdd98NHjxYoVC888473t7edYtVVFSEh4cnJiZaWlqeP3/+P//5j0gkAoCCgoKFCxfevn0bACwsLGJiYhYuXJiVlUW/qri4mL6pS7du3bp166axz3bt2vXv3x8AysvLExIS8KKbFqoRM+TUaVyRFx8fv2LFCg6HIxaLf//9dy1vd40MrhHNwNLSsl27dgBQUFCABxoh/cEUSr+YTGZoaOjZs2c3b95MXzSnjqKo69evJycn09fp9OvX7/bt2x9//HFubq6rq2v//v2XLl164sQJAHjnnXesra0/+eQTet1O1U1d3n777bpTYRgMxoABA+jxu2vXrjXiWj9kDOgbVxcVFd2pDz1fWHtsNjswMHDgwIEAUFpaircAainUm0FycrI2zcDGxobue05LS9NY6RcAsrKyPv/88/Pnz1dUVBj6wyHUsuFAXnOodz4EnT999913Dg4OXbp0AQAulztw4MDjx4/fvHmzc+fOAwYM+OWXX06cOOHl5dWtW7f33nvv5s2bkZGRO3bsGDVqVMPzxPv06RMfH2/oz42agLOzM73WlwaCIAiC4HA4Wk5sUigUd+7cofs1UYtDN4O690Olm4HGonFMJnPkyJEXL14kSTIiIqK6ujooKIjNZisUiuTk5O+++y43N/fmzZuhoaGrV69ueFF7hFADGIWFheqP6X5+LV+sv8I6MaqYjx8/rlQq/f39G75FHYfDKSgo+M9//pObmztlypSxY8fSk0avXr36119/TZ482d7evrKy8tSpU0OGDOnXr19VVVVZWdnmzZuHDBkybty4BmaYtpF6NngYOhV+/vz5N998Y2dnt2rVqqysrPT0dD6fz2Qyk5OT+/Xrt3LlSisrK409kyT5+PFjOzs7R0fHeg83vSiUlZWVxtqMv/zyy8mTJxuOZ/z48bNnz27C1aGMpJ6NPGadmgFNoxnU3bNqbTCNq0ZIkjxz5ky9d0uk2dnZrV27tmvXrq2vnjFmjLn5Yqb+rbKyktKa/goXFhYaQxgYM8bcJIUTExODg4NnzpxZXl5Ob3n+/PkXX3wxcuTIy5cvK5XKunu+cuXKu+++m5eX9+LFiy+//PLWrVv0+mGHDh3asmULvZ+SkpI5c+b8/PPPUqlU9fLvv//eu0GzZ8/m8/mtsp6NPObc3Ny6zeDTTz+ttxnQNJrBn3/+WW8zmDdvnkYzoChKIBBs27ZtwIABddvAyJEjr1+/rv6OrameMWaMudlixrlQCBmAm5vb1q1bo6Ojg4KC6o7ECYXC33//3dnZ2c7Ojp7XsnTp0p9++kmpVAYGBiYmJi5btqyoqMjR0XHKlCl79+799ttvtZk13KVLl08++WTbtm3Ozs6GrgAEAODm5rZy5Urtm8GaNWvqbQYzZ86s2wzYbPYXX3zxyy+/hIaG2tvbAwBBEJ6enp9//vnvv/8+dOhQXNsCoTeEc6EQMgx6Fkvd7RUVFT/88ENqauqcOXOsrKwYDMbgwYOPHTt29erVkJAQJycnHo93+vTpq1evzpw5s2/fvv7+/hcuXOjdu/fkyZMBYMmSJa+6Z23dmTTI4AiCqHdJJ5FItH37do1mEBUVVW8z4PF4Gs2AxmAwPD09v/nmG0N/SoRaJ0yhENI7BoPh5eU1YsQIFov12sJ3796NjY3t37//uHHj6H4CBweHAQMGjBgxwsnJycTEZOjQoZ06dZo4cSIAsNnsAQMGiEQiXOfJ+OnUDG7fvl23GfB4vFGjRmEzQMhIYAqFkN65ublt2rRJy8IjR46kvxdVHBwcvv32W9XDoUOHqj87efJk9Y4HZLQ8PDy0bwZjxowZM2aM+hYHB4e1a9eq+hGxGSBkcDgXCiGEEEJIZ5hCIYQQQgjpDFMohBBCCCGdYQqFEEIIIaQzTKEQQgghhHSGKRRCCCGEkM4whUIIIYQQ0hmmUAghhBBCOsMUCiGEEEJIZ4zKykpDx1CPlngzL4wZY8aYMWaM2ThhzBizPmImNF6p076wMBbGwlgYC2NhLIyF22ZhHMhDCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTKIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTKIQQQgghnTEqKysNHUM9dLpzspHAmDFmjBljxpiNE8aMMesjZkLjlTrtCwtjYSyMhbEwFsbCWLhtFsaBPIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTKIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZo7Ky0tAx1EOnOycbCYwZY8aYMWaM2ThhzBizPmImNF6p076wMBbGwlgYC2NhLIyF22ZhHMhDCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTKIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIGSmlUtnoZ5ExwGOEUOumcwr19OnTsWPH8ni8sLAwmUwGAGfPnuXxeDwe7+zZszrtKjIyksfjjR079unTp/UWkMlkYWFhPB5v1qxZIpHIUHVUVVW1fPlyHo93+fJlABCJRLNmzeLVMW/evA0bNmRlZVEUpXptQUHBhAkTPv74Y6FQaKj4UQtVUJBXW1vbuGeRMcBjhFDrhr1Q/yKXyy9cuPDs2TP1jbdv375586anp6e3t3cDry0uLj537tzs2bMPHz5MkiS9kcvl+vv7p6amRkdHq6dWyFCUytrCwmdvvh99q6mREYSZqanpa5+trSUrK0UN7622liwtFQiFxYb+WI0kkVTX1MgMHYVuGj6CCKFWgHjzXYwfP378+PGG/iBNoKCg4L///e9ff/21a9cu1caKioozZ86QJOnn5+fg4PDanZAk+cMPP9jZ2Y0bNw4ACIIYNmzY8ePHz507N3LkSDc3N0N/yjZNIqkWCAoUCrmhA3m9kpIiZ2e31z4rlVYXFz8HYLRrZ/OqwqWlAopSlpWVMpkWhv5YOlMqawWCguJifqdO3c3NWYYORwcNH8F6yeU1xcX8Dh06aWyXSKpFojIGw6S6uqq0lMHlurHZlqpny8uFUqkEgKFQ1JiYmLq4dDA1refEXltb+/hxeqdOPSws2PW9byGH01P7qCorRbm5jzVKWlpyunV7SyOqqqpKkYitEVV5eZlIVMZkmtMPuVw3zDVRS0Tw+Xz1xxwOR2OLhpKSErprWiqVAkDDhRvec1VVFQDU1taWlJSYm5trlOfz+TU1NfS7KBQKgUAgkUi03LNOYdBqamr+7//+7+bNm46Ojqp4OBzOjRs3kpOTCYLo1q1bUVERAFRWVioUCgDo0aPHunXr2rVrBwAkSRYXF58+ffry5cskSR4+fLhjx4729vYAwGazu3Tp8vjx4xMnTkyePJnBYDRVzG9e+A2PYMuM2bSqqrrePagXlsmkLNYrEw6ZTOro2F5/MefnPxOLK01NS+stQJIK1bMcDqeioqK6uvK1+1cqGTqFoWvM+iusVJqQZK1QKKyqkry2fDPE3HDbAC2OYN2YJRKxXF4jFlewWBampv86GdbUSEWisvbtXQEYTk6upaUlGRmpzs7uBGEGANXVldXV4vbtXQHAzIz94kWJUFji5NSh7gd88aKkqqqyuLhYlbgAgOp927WzrlsbDUTF5xcyGIS1tZ2JycuhDLFYZGrKpHeiHpWzs/uzZ09UUdHPVlaWOzl1YDBMAEAqrU5PT6435iY8gmA07Rljbk0xEy4uLupPi8VijS0aampq6J8LFhYWAODi4nL27Nnw8HAAWLduHd0dpb6la9euP/74Y3JysoWFRUhIyOzZs+nEAgCsrKwAwNTUtH379i4uLiRJ7t+//6effgKAKVOmLFu2jCRJ+l3MzMy4XK6NjU29IYnFYltb21OnTkVHR+fk5ACAvb39sGHDZs2aper1USqVd+7cOXLkSGpqqlwuZzKZ3t7eH374oa+vr4mJydOnTxcvXiwQCACgtLT0008/BYB9+/ZZWFhkZWWRJNm9e3cvL6/27dsDAJvNNjMzqxsVQRBff/01RVFXrlz566+/RCJRnz59AKB9+/b9+vV7/Pjx/fv3Z8+ebWtrq00963RQGl2Yz+cbQxjNGXNlpUihkNa7B1VhpVL5/Hnuq96FfhYA9BeziQnVvbunmRmz3gIFBXmqZ8VisYODPYOhfO3+KYqUyWQttG2IxWUODg4N9LQ1W8wNtw1V4YaP4KtiLijIk8trNHael/eXo2N7V1dXes+dO3epqakyNzdzcnIBAD6/VqH457Da2to8fpxhb29nbs5S/4AVFeVmZlySrHFycqrbC1VQkCcWV77qQ9WNis/nW1lZdu/uqcqfSFLB59e6u3f+u8A/UYnF4i5duquiAoCHD4s7duzs4OCk2mFW1n0229zGxt5ozxsGKYwxG3/M+p0LFRUVNW/evMTERJIkxWJxVFTU5s2b6+1MUs+fZs6c+d577xGEtoOMEolk8+bN3333HZ0/AUBZWdmpU6c+++yzvLw8AKAo6vz580uXLk1MTJTL5QAgl8sTExOXLl165MiRBqYoVVVVPXz4EAC6detmbW392kjYbHZwcDD9tyoYgiB69eoFAE+ePCkoKNBrhaM3p1Aonj/PfdW1VA0/21QBAMCrvn3l8poGnkV6peXRb/gINoDuldGgVNa+ePGvi1FMTYna2pezLZ2dXbt29VQ9VVtLMhgMuoNKhSTJykqRnZ2jTu/b8LNOTi6q/AkABIJCOqV7bVQKhUIul2ukcRYWbJGoXNfqQsjgmmAuVAOKi4u//fbbYcOGPXny5MsvvywoKLh3715+fn7Pnv8adKco6uLFiwcPHgSAsWPHfvzxxzpdf3f37t0LFy5wOJyIiIiBAwcCwB9//LFu3br8/PzU1FQPDw+RSHTq1CmSJPv27bty5coePXoIBIJvv/02ISHh9OnTgYGBnTp1Onny5MaNGy9dusTlcnft2tWpUycASElJoZMeBweHukON9XJxcXFyciouLqaHKWlcLhcAJBJJRkYG3TWFDEsmkwoEhRSllMvlDg5O9vYvv11EojK5XK5UUjU1spKSIgAgCDM7O4e6z754USqVVqmeFYsrCgufMRgMN7dOQqGAwWAoFAo7Owdb23/NnyNJxePHD9hsq06dur0qtvLy0g4dPF71bGmpoH1757rba2pkQmFxbW1tTY3Mzs7B3r69llVBz3QxM2MyGFBTU+Pk5KI+5YiuB3NzFkkqlMpagjATCks8PLpaWbV77Z6VylqBoNDExMTExEQmk9rbt7e05Ki/b1lZCZ0NlJcL5XL522/3V30rKxTywsJ8BgPkcoVUaqN6lVQqKSjIUyprPTy6FRfz6f3Y27e3tbV/bTwar62pkRUXMzReq1TWFhUVKJVKBoNBkiSX66oas2u4bTRwBOXyGj4/XyR64eDg5OrqzmCYiEQv8vNzbWxsXV094HU6dOikPpVeqVTKZFJVG2AwTFQDcwqFvKjouZubh8a8IoGgQNdZWa+lniDK5TUkqVBvNupRkaRCKCxSi4oCAI0frgwGQyp9/SgtQsZGvynUpEmTAgICGAxGt27d/P39jx07Vl5eXl1drV6Goqjjx4/TU7aDgoK++OILNputUwoVEBCQkpICAGKx+P79+0lJSWfOnKGfohOgysrK8vJyACguLs7Ly+vcuTOXy42MjHztnsViMf3Cjh07ahmMiYkJPdtJnZ2dHZfLFQgEJSUlFEXVLYCak0IhLykp6tChk6mpqUIhz8q6b21tQ/9EtrGxBwChsBiAqpupqD9rZ+fI4fyTEHA41i4u7vn5TyorRR07dgWA2tra7OwHDAaDfhVNqVSSJNnAfHaFQk5RlPpsFY1nlUpl3WdJUiEUFru4uDMYDJJUPHqUwWSacziv7zclScWTJ486d+5Bf//J5TVPnjzq2vUteqhaqVTm5j7u2vXlgBSfn09RVMeOXRueCUSjKOqvvx45OjrRSaRUWp2Tk9Wrl5fq2/3Zs786d+5JP3RycsnJyVIo5HQYtbW1OTkPO3ToxOFYi8VigjAVCArpV1lYsJ2cXPLzn5SWFrm5eZiYmJCkIivrfrt21vXOoVan8drq6moLC5b6aymKevLksYODE51USaWSv/562KNHH/rjN9w2GjiCTKZ5x45dxeJUW1sHukfHxsZOJCpzd++iRWsFMzOmer5SVlZibs6ytrb995sqCguficUVLi4dNLLn8nIhh2NNEGb6W15BICh0dOTWVxWKwsJn5eVCd/fOqqgIwszExFQiqVZl4SSpEIsrGu4JQ8g46TeF6tChgypdUE2B0lBcXPy///2P/rt79+7ajJdpoCjq7t27+/btS0tLq7eAk5NT7969CwoKBALBmjVrOBxOSEhISEhI165d1fui641N12CUSmUDI4OlpaU1NTUsVku6sKj1MTEx7dChE90y6e8nmUxmZWX2xjsGExNT1c99U1NTBwen4uIi9RSKyTTv3du7gVZXUlKk0XGl8Wy9X95yeQ2X60Z/IoIws7GxKysr0SaFKioqaNfORtV/wGSat2tnW1T0nJ7UUl0tNjU1VX1/czjWhYXPnJ07aFMVZWUlFKVUfRYGw8TMzEyprKVzJoqipFKJ6uRgYmLq5uaheq1QWEwQZqr4LSzYGn3AJiamrq4eqs9rZsaUyaTqXVwNH6NXvVYkKlMqlapOKQsLNpttJRQWa/mRGziCDAbDxsauouKFpaUVAEgkVdocnfoOtOzFi9LOnXto/AwzMzPz8OiqVCoLCvIkkqoOHV7OSVIo5BJJtaurtr8AGxVSTVVVpWoWVN2obG0dKyrKVFExGAxHR6eSkiIOx9rCgq1QyAsLn7HZVjKZVH9BIqQnzZf4s9ns15b53//+R89e0klcXNxnn32WlpbG4XCmTZu2b98+jR4mFou1dOnSd955h35Iz8qaOnXqnDlz7t6927TLNfH5fDrxoifLIyNkamqq/g1kYmKiVDbND3SNARQWy0Iqra5b5lXdkPRg2au6oOhn672wn822Un9rFstCy2ERkahMY0jOysqqouKF6qFS+a9/HSYm2l55XlFRbmX1T5bAYll4evZVZWMMBsPa2i47+4FQWExP67G0tFJ9NLG4wsqqoXxIow4ZDIb2XSwNvLayUqS+WAAAmJuzqqurtNwzNHgEbWzsRaIXqsqxsbHTfrc0ubympKSoc+eer5plZWJi4ubmIRKVV1S8nFckEBRyufpdSEUoLGl4mn/dqJydO7i4dCgqep6b+1ggKHBxcacoSmP+FkItgn57obTk7u4+bdq0H374QSAQnDx5cunSpdq/ViaTJSQkkCTJ5XK///77rl27AgA9rqfO0dFx69atQqHw9u3b169fT09PLysre/DgwWeffbZjx45BgwYxGIw3X5iEJMk7d+7Qf3fr1u3NdoZaPHp4SPu55yUlRY6OzgoF2cCz2uzHxMRUmzdVKpW1tbUa38dmZsza2lr65RyOtZmZmVhcQXeZvHhR2sAAlgaSVNCjga/SsWOXiooXpaXFhYXPrK1tnZ07qFKo2lrSIF+oJKkAIEtLBaotFEVpM2qp0sARtLLiKJVKiaSKzbaqra197bCjBrm8prDwmbOze8O1amJiwmZbikRl1ta29Awq1XqqFKUEgBcvSul+yqZaZKu8XPjaLE09KnqLnZ2j+vR2ubxGm9l1CBkbw6dQtra2mzZt6tGjR3Fx8cGDB8+fPz98+HBnZ23P1DKZrLCwEAAcHBxUS18+fvy43sIODg4BAQEhISFKpfLatWtfffUVSZLJycmDBg0yNzevu3Km9hc6UhRVVlZ27ty5EydOAICnp6fGlHmak5MTjuK1HbW1JINh0vBgsQpJkiRJslgWCoW4gWe1fF9tfg+YmJiYmJhq9MCRJElPAAcAiqLMzVkSSZVEUg0AdnaO2g8/qV819irW1nbW1nY1NTKhsCQ7O7Nbt7foD2hqatpU/YI6MTUlzMyY9U7r0UbDR5Aeyysvf0FRlK7pAj3a5e7eWSKRqrbQua9QWCyVSjTWvaT71czNWQ4OjuobBYJCOzvHuosaNFpNjUyhkDOZmr1iDURVb73V1Mj0OtqIkJ4YPoUyNzdns9kEQbz77rvXr1/Pzc2NiopauHChepkHDx6MGDGi7mtnzZo1f/58V1fXrKysR48eJSYmvvPOOxkZGXQeo3L//v3FixdLJJKgoKD58+dzOBy5XK6a56SROdFzz+kFpaytrenL6zRu+dJwVARBTJkyxdHxn5PXixcv6EWncHXyFsHU1FR9eLeqqlL9O6+BZzXGhCWSqroDUrW1tfVec1BaWtTAl3fDz2r0OWk/Mcja2kZ9Yi8ds6qrQCKpqqqq7Nixi7m5Rd1EkKIouk+l3nFJKyuOWFypsVEoLKZXA6qsFDEYDDohMzdnubq6MxhQUVFOp1BsNkdjZozqjkmv1XBUDbOyaicSlWlslEiq1Uf3Gjj6DR8jALCxsc/P/8vExITL1fa3GQDQM5w6dOik6riiKKqkRODq6g4AL16UkqRCvXxNjUx1ham+0bk1gGZVNxwVPSLp6tqRPkYiUZm5Oatxk8MQMiwjugjC1dV1+vTpAHDz5s3U1FQtX8VisQYPHkwQBEmSYWFhvr6+8+bNe/HiBf3DSCaTkSTZq1evGTNmEARx5cqVSZMm8Xi8wYMHb9++HQC8vb2DgoLoXdGX3Ukkko8//tjPzy89PZ2+kg4AhEJhTU2NNvEQBLFo0aLRo0erb6TzJzabjaN7LQKLxZbJpPQ3pUj0QmPMpYFnZTKJKm+gO1c0xjjk8poHD1Jzch5qvGNtbW3dxXK0fBYApNJ/biGnUMjFYpGWI27Ozh1evBCqrhAkSVIkeqGaPc1mWzGZrOzsh+npSZmZaU+eZBUX81XpGp+fn5PzsKjoeb17dnDgyuUy1fQXiqKKip6rsg0TExOBoFA9F1EqlWz2y+mDjo5OVVWVMtnL6VxCYTFJKrScs9hwVA2zs3MkSbK8/J9FmEpKijRyx1cd/dceIwCwsuJQFJCk4lVXn1FUbd0R2IKCPDs7R3q5Crm8RiaTFhY+MzV9uQdbWwczs3+mXpWXCxkMhoMDt76dK6HOagKq922geuuNika3HHrP6hqOqrpaLBQW08eXvjy2Y8cueJ0yaokM3wulwmAwhg8ffvXq1cTExAsXLowYMULLGdkBAQGOjo4//PBDVlaWvb39hAkTJkyYsH///tOnT9+7d08oFHK53Hnz5vXv3//3339PTk5+8eIFfcOWMWPGTJw4kV4AHQBGjRr14sWLQ4cO0cuPSiQSS0vL3r17379/Pzc3t7q6uuGloZycnAYPHvzBBx906fKv0wFFUfQym126dMFeKMOSyaRCYbFMJlVd2lZSUiSTyUpLBepTgC0s2HZ2Djk5D83NzenrhtR3Qj+bn/+Ew+FoPGthwa6pkYrFotraWrm8pmPHLvQVWCoMhglBmNadzvImXVAA4O7eRSQqq62l10yoVb+dHEVRpaUCAKqyslwuV5SU8AEYjo5cuokymeadOnUrKiowM2PSCwR06tRdVRUiUZm5uXmnTj5KZa1MJpPJpC9elMrlMvrSKnNzlomJyaum1BAE0a1bLz7/OT35BoCys2uvGogkCLPqanFW1n1ra1szM6ZSqbSwsORwXiZYZmbMLl16Fhbmm5qaKhSkvb0Dm20lEpUxmUwGw6ThI9hAVA0ffRbLwsTEpGvXt4qK8svLywjCjMFg2Nk5aAyevqptvPYY0Wxs7DTWI/i7ql9IJFUvXgiVSuXz509ZLAvV3l68EL548fJGMSRJ0msOd+z4ckEER0euqSlRUJBnYmJKd/x06/aWxjCuUqkUCourq8UAQM88c3R0otM41fvK5XKN9204KhpdaXXbs3pU1dVic3OWelTW1nb29pXFxXwm01yhkHt4dNOYxY9Qi0H9W2VlJaU1/RUuLCw0hjAqKysTEhIGDBgwZMiQ9PT0xsVcWVn5ySefeHt7/9///R+95IG+Y9a+sPHUcyuIuaKi/NGj+htJwzHX1pJ5eTmv2rPGs832AQsLCx8+vEf3uKjtoSI7+0FzhtEi2kbDR9A4Y36Twhgzxowx04xoIM849erVy8vLSyKRJCUlNW4PhYWF2dnZbDbb398fO6tbN6pRC2RQFDRwTVPDz+qVhYVlZaVIfYtUWm1trfPV+K2eAY8RQsiAMIV6DWtr6wkTJgDA3bt3KyoqdH05RVEJCQnl5eXvvPOOp6enri9HLYVEUk0PEhUVFei6DLSpqWkDV5g3/Kxeubt3rq2t5fPzi4v5xcV8eoKR9usatB0GPEYIIQNiVFZWvvlempxYLFa/e4ZhVVRUbNq0KS0tLSIiwtfXV6eYhUJhWFgYn8/funXrW2+9ZeiPolXMRg5jxpgxZowZYzZObS1mQuOVOu2rjRTmcDh79uxp3J45HE5UVJSRf0AsjIWxMBbGwlgYC+taGAfyEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTKIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeMyspKQ8dQD53unGwkMGaMGWPGmDFm44QxY8z6iJnQeKVO+8LCWBgLY2EsjIWxMBZum4VxIA8hhBBCSGeYQiGEEEII6QxTKIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTKIQQQgghnWEKhRBCCCGkM0yhEEIIIYR0xqisrDR0DPXQ6c7JRgJjxpgxZowZYzZOGDPGrI+YCY1X6rQvLIyFsTAWxsJYGAtj4bZZGAfyEEIIIYR01mQplFwuP3HixIQJE3g83sCBA7/55pvMzMyxY8fyeLywsDCZTGboT4oQQgihlufs2bMBAQE8Hu/s2bOGjuVfmiyFOnPmzJYtW/Lz8wFALpebmZmZmZk1bawURWVkZFy7dq2Z6wghhBBCrVJhYeGpU6ca91qiSSJQKBTZ2dkAwGazv//+e29vb4VCYWZmduHCBfUyb/IWUqn0yJEj+/fvX7NmTZPVHEIIIYTaJLlc/scff3z33Xfvvfde4/bQNClUbW2tVCoFgHbt2tna2gJAk3dBXblyZc+ePU27T4QQQgi1TRkZGeHh4W+yhyYYyEtJSRk8ePClS5cAQCAQTJo0icfjpaSkPH36VGMuVGRkJI/H4/F4f/7554YNG3x9fSdMmJCVlQUABQUFERERQUFBdIElS5YcPXqUTstkMllYWJjqc4aHh/N4vMjISENXPkIIIYQMgKKorKysVatW0XOkfH19Z8+efenSJblcripTVla2e/fukJAQOq8ICQnZvXt3WVkZ/WxkZOT8+fPpvw8dOtS4edtN0wulq927d+fl5QGApaWlg4PDkydPvvzyS3oeFe3p06ffffddUlLShg0bzM3NDRIkQgghhIxQUlLSV199JRaL6YckSWZkZGRkZCxYsGDu3LkAIBQKV69enZqaqnoJn8/fv3//jRs3tm3b5urq2iRhNEEvFI/HS0hIGD16NABwudz//e9/KSkpPB6vgZcQBHHy5Mk7d+5s27bNwcHhjz/+yM/PZ7PZO3fuTEpKSkhImDFjBgDEx8cnJiayWKyIiIh169bRr123bl1KSsqSJUv0cVQQQgghZMzEYvEvv/wiFouDg4NjY2NTUlIuX77s4+MDADdu3KAXDE9ISKDzp9WrV9+5c+fOnTsbN24kCCI7O/vSpUsURS1ZsmTfvn30DmfNmpWSkhIREcFisXSKxDC9UKNGjfLw8AAALpdbU1NTUlICAHK5/NGjR2+//ba1tfXkyZOXLl1qkNgQQgghZLQ4HM6PP/4IACRJCgSCO3fuXLhw4d69ewBQXl5eUVHh4OBQWFhIF87OzhYKhU5OTsHBwcHBwU0biWFSqG7duqn+Njc35/F4Fy5cIElyz549+/fv9/PzGz58+OjRo3XNBxFCCCHU6olEoqNHj544cUI1lqfBx8fn2LFjEonk5MmTJ0+e9PLyevfddwMCAqysrJowDMOsTs5ms9UfjhkzZunSpUwmEwBIkrx58+bGjRtDQ0OPHj2Ka3IihBBCSKWioiIsLOzAgQNisdjLy+vrr7/+3//+FxQUpF7Gx8dnzZo19vb29MO0tLRvvvlm5MiRu3btEolETRWJYXqhNDCZzBkzZrz//vuZmZlxcXG3bt3Ky8srKyv77rvviouLlyxZQhAEQRhFqAghhBAyoL/++is5ORkA5syZs3DhQoIgZDKZicm/uoRMTEzGjBkzcuTIx48fJyQk3LhxIycnRy6XHzx4MC8vLzw8nM1mm5iYEARBkmSjIzGie+SxWCwej7d8+fKTJ0/u2bOna9euAHD//v2qqioA4HK5hg4QIYQQQgZWUFBA5z0dOnSgu1cqKytzc3PrliQIolevXvPnzz9y5MilS5eGDBkCAFlZWcXFxQBgY2Pj4ODwJpEQfD5f/TGHw9HY0gBV4ZqaGnoNp9ra2pKSEnoZgpKSktraWgCQSqVFRUUODg50MgQAQqFQ9S6VlZVbt25NT093cXFZsmSJp6cnAIhEooqKCgCwtLQUCoUSiUQoFNLl//rrr/z8fJIkVTOlGhdzkxcGAGMIA2PGmDFmjBljxphbU8yqoTeRSMTn81ksFt17dPHixc6dO7NYrOPHj9O3SKGTkHbt2q1cufLPP/+0srJavHixr6+vqalpYWFhaWkpAFhYWIjFYj6fr8pSCgoK6AzM3NycwWBoHzPh4uKi/rRYLNbY0gBVYZlMZmFhAQCmpqbt27enN9bU1JiamtLhOjs7KxQK1TQuBwcH1bu4uLh88sknX3/9NZ/PX7VqlUass2fPprujampquFyuQCCIioqKioqaNWuWal2DxsXc5IX5fL4xhIExY8wYM8aMMWPMrSlmGxsb1R8uLi6WlpY+Pj6JiYnJycmzZ88GAIIgrK2tKyoqSJK0trZmMpkLFizIzc3Nzc3dsmWL+q4Igpg5c2afPn0YDIaFhQWXyy0tLY2JiYmJiRk9evTatWsbvo5NI2ajGMgbMGDAL7/8MmfOHHqlAwBwcnKaOHHikSNHBgwYQG/x8PD4+uuv6XSKw+HAG990DyGEEEItjrW1dURExLRp0zgcDkEQPj4+O3fu3LlzJ5vNLi8vv3fvHkVRnTt3/umnnz7//HNPT096sM/e3j4oKOiXX34JCQmhu5psbW1Xrlz59ttvAwCTyWQwGDrPi6L+rbKyktKa/goXFhYaQxgYM8aMMWPMGDPGjDFjzPXu2Sh6oRBCCCGEWhZMoRBCCCGEdGakKdTOnTujoqJeteooQgghhNosPp+/ffv2qKgow4ZhjOtVJicn09Pj9+7dO3z48Pnz52s/wx8hhBBCrVVycvL58+ejo6MBwMrKatq0aQYMxhhTKHpd9kuXLqWmpkZHR0dHRwcEBEydOpW+DzNCCCGE2pq4uLioqKiUlBT64bhx4wybP4FxplAAMHDgwPfee4/P5+/du/f8+fNxcXFxcXHOzs4LFiwICAigFzVACCGEUOsmFovj4uL27NkjEAjg756nkJAQYxieMtIUiubi4rJhw4Yvv/wyKirq3LlzRUVF69evt7KyCg0NnTp1qjFUH0IIIYT0gc/nnz9//ujRo6r7vC1YsGD48OHG041i1CkUjcPhLFiwYMGCBefOnYuOjk5NTaUXKA8JCRk3bhyO7iGEEEKtCZ/P37dvHz3hCQC8vb1Hjhw5efJkQ8elqQWkUCqhoaGhoaGPHz+OioqiZ5NFR0d379594sSJ77//vqGjQwghhNAbSU5O3rdvn/qEp5CQEB8fH+O8Qr8lpVC0Hj16bNiwYcGCBdHR0VFRUdnZ2Vu2bNm1a9f06dPHjRuHo3sIIYRQixMdHb13796ioiIAsLKyCgkJmTZtmpF/p7e8FIrm4uKiGt07cuTIkydP9u7du3fv3pCQkKlTp/bo0cPQASKEEELoNcRi8bFjx9QnPIWGhtL3vzN0aK/HqKysNHQM9RCLxTpVX1pa2qVLly5fvkw/7Nev3+jRo0ePHm3MMRsDjBljxpgxZozZOLX6mIuKig4dOnTz5k06eerSpcukSZPGjBljzDFrYFAU1eh96a8wn8/XvvtOtWc+nx8VFRUdHU0fD2dnZ/raPfX3NbaYDVsYY8aYMWaMGWPGmJs55uTk5GPHjsXFxdEPhw0bNm3atIYvDjN4zPXuuaUO5NXLxcXlyy+/XLBgwbVr1+ghVdXoHi5xjhBCCBmWahIz/XDcuHELFixoud/OrSqFonE4HPraveTk5KioqOvXr9PX7vF4vGnTpvF4PEMHiBBCCLUhYrGYTp5Us8WNZ3nMN9EKUygVHx8fHx8feonzuLi4lJSUlJQULpc7ffr0kJCQFjfGjBBCCLUsfD7/2LFj586dU18eMzQ0FACMc50CnbTmFIpGL3FOp8BHjx4VCATbt2/HGxgjhBBC+qN+P2AA8Pb2XrBgQStbDbv1p1A0Doczbdq0adOmXbx48fTp09rfwJjP53M4HOyyQgghhGjJyckNfG/Wez/gVrnYUFtJoVT8/f2Dg4O1v4Ex3Q727duHWRRCCCG0bdu2Y8eORUVFaWRFYrE4Jibm+PHjrWzCUwPaXApF0/IGxvTwX1VV1bhx4/bt29cqk2iEEEJIS99888358+cBICoqasOGDfRG478fsJ600RSK9tobGKuW/Kqqqpo/fz5mUQghhNomsVi8fft2On8CgPPnzy9YsAAA1O8H3Lt37/fee4+eLd4WtOkUSuVVNzAWCAQAQK8+WlVVNW3atG+++abtNA6EEEIIAMRi8fz58+n1nOjvRAaDMX/+fHrMDv6+H7CLi0srHrarC1Oof2jcwPjx48cMBoOiKAaDAQD0Hxs2bKBzKUMHixBCCDUHjfyJ/mYEAD6fT0+AUd0PmM/nGzrYZmVi6ACMDn0D4+vXr3fs2BEA6PyJ/oNuNNu3b1+/fr2hw0QIIYT0LicnZ9y4cdnZ2RRFqfoUVP0Ls2fP/vLLL9tUz5M6TKHqx+fz8/Pz4e8eSxrdaCiKio6OXr9+fStYFgwhhBB6lcePHy9btqyqqko1eKdR4NSpU4aO0ZAwharf3r174e/8ifobqDWg6Ojojz76CLMohBBCrdK1a9fmzJmjnj+pfxvSioqKzp07Z+hIDYZRWVlp6BjqodNtlvXx7lOnTqWvxatLPZeysrLasWNHt27dDB5zoz8pxowxY8wYM8ZshAwb88GDBw8dOkT/rRq/q1e/fv127txpDDE3zpvETGi8Uqd9teLC27dvT0lJkcvlNTU1jx8/BoDs7Gw6qVJvSVVVVcuWLaMXOzB4zFgYC2NhLIyFsfCbF46KilLlT6D2reft7Q0A9GV3HA6ne/fuAKC+THlL+YBNVbiNXpE3f/581drzulLvw4S/u6ygvkHitqxfv34///yzoaN4vTdpCUgbPB5v3759ho7iNbAZ6JuxNQM84g1QH7ZTbaS/4FJTU1X/b5ixHXE9aaMp1Jv848FUSRv37t0zdAhawdOovrWIGm4RQbZoxlbDxhaPUVG/Dr3RO2kjNdxGUyhaGznGzY/H4xk6BN1gS9CTltUSsBnoidE2AzziemK0R7zJ4RV5CCGEEEI6wxQKIYQQQkhnmEIhhBBCCOkMUygEABAZGcnj8cLCwmQyWd2HqDWRy+UbNmzg8Xj+/v737983dDioeWVlgYcHMBj/+o/JhEGD4LffgCQNHR/SD6USYmJg4kSwswMGAzp3hnXroLjY0GG1eJhCIdS2FBYW3r17FwAkEklMTAyJ35pIoYDbt2HqVNi2Df69aAtqDaqqYNkyeOcdOH0ayssBAJ4+hY0bYehQyMw0dHAtG6ZQCLUtSUlJAoGA/js1NbWcPqUiBADHjwOfb+ggUJMiSfjuO4iMrOep7Gz44gt48cLQIbZgmELpRiQSzZo1i8fjnThx4sSJExMmTODxeAsXLszMzKRXIVMViIqKioiI8PX1nTNnTlFREUVRmZmZixYt8vX1DQgI2LRpU1FREQCQJPndd9/xeLxNmzYpFAr6XUpKSqZOncrj8eLj4wEgJSWFx+PxeLxXXYKrGndLS0tbsWLFwIEDAwICDh48SA/DqUI6e/YsXV4mk4WFheFQnf6cPXuWx+PNmjUrNTVVdUQOHDgglUo1Cly+fDk4OHjgwIFRUVEAIJVKDx48GBQUxOPxPvzww8uXL9O9RDk5OaNGjfL398/IyFC9S1RUFI/H++KLL6qrq7U8pmKxOC4uDgAmTZrk4eGRlZWlzSp5qJEOHAAGA/z84MYNmDQJLCzAzg6+/RaqqzUL/PYbuLuDhQV8/z0AQHU1bNkCzs7AYICPzz9DbOnp4OoK7drBnTv/vMv33wODAe++C2IxSCQwfTowGDB9OkgkDcUWFwcU9fI/hQJ27wYAKC8Ho7zlV4thhEf82TM4ehQAYMAAuHULFAqorYXMTAgMBAC4dg3UTilIV5hCNVJkZOSWLVvy8/MBICkpadGiRUlJSeoFdu/eferUKZIkbW1t27VrR5dJTEwkSVIsFp8+ffrTTz/Ny8sjCMLPz48giLS0tJKSEvq1jx8/zs7O9vT07Nmzp/YhxcXFLVy4MDY2Vi6Xi8XiXbt2HTt2jMJuecN59OjRZ599pjoiP/zww+bNmyVqp7lHjx6Fh4cXFxfL5fIOHTpIJJLNmzfv2rWrrKwMALKystasWXPgwAGSJF1dXfv06SORSFTNrLq6Ojk5GQD8/PwsLS21DCk3NzcjI8PBweHdd98dPHgwAFy9elXS8HctekOpqTBmDJw8CTIZlJdDWBh8+imo34IzNRU++giePweZDLp2haoq+PRTWL0a6M7ClBSYOhW+/RZIEjp3Bj8/EIshJubla8ViuHYNACAoCBp9bzKFAui028UFHBwMXV8tn1Ed8bQ0yM4GFxfYvRsGDgSCABMTeOst+O9/YexYOHECBgwwdH21YJhCNZKpqWlkZGRSUtLp06f79u0rFot///139a+idu3aRUVFJSUlrV69miTJAwcOiMXiuXPnJiQkxMbGBgcH5+fn0zlWr169vLy88vLyHjx4AAAKheL69esA4O3tbWtrq31IJEkuW7YsISHhwoUL9J2MkpKSXnWzZNQMSJIMDAyMjY29ffv2ypUrCYK4fPmy+rrtJElOmTLl9u3bcXFxPj4+8fHxFy5ccHd3P3r06N27dyMjIzkczsmTJ58+fcpms0eOHAkAd+/eraioAIDc3NykpCQHBwcvLy/t44mJiZFIJD4+Pp06dRoxYgSbzb537x79SwDpi0IBEydCWRnIZLBrF5iZwbFjcPPmvwosWfLy6zYgAM6fh19/he7dITUVSBIuXgRbW9i7Fx4+BCsreP99AICYmJfjLw8fQmwsuLjAkCG6RRUQ8M90cjYbli0DW1tYvRocHQ1dXy2fUR1x+pKR/v2hW7d/bff2hvPnYfx4sLAwdH21YJhCNdKMGTMGDRpkYmLi7u4+Z84cAMjKyipWu8Bh2LBhXbp0MTExcXR0zM/Pz8zM5HK5wcHBLBbL2to6JCQEANLT08Vicbt27fr37w8AiYmJcrm8pKQkLS2NzWaPGDGCIAgAoIfw6OG8BkLy9PQcNWoUi8XicrnDhw8HgOrq6traWkNXVdvl7u6+YMECa2trJpM5duzYwYMHkyRJdx3RbG1tR44cyWQyORwOQRB0D9Pw4cN79uxpamrq7e09cOBAoVD48OFDAOjVq5e7u3tmZmZeXh4AJCUlSSSSQYMGdezYEQBYLFZERERKSkpERASLxao3nvLycnrYbujQoSwWy8PDo1evXuXl5QkJCdhbqUfdu8P69WBnB+bmMHMmBAeDQgFxcf8UaN8eJk8Gc3OwsQEzM4iNBQCYMAG8vMDUFIYOhaAg4POBbjn9+0P37pCUBI8eAQDExIBYDKNHQ48eAABsNhw9ChQFR48Cm61bnMOHQ69ehq6sVsGojjg9P8TSEkxNDV0vrRAhFos1NtXd0oBWX/hVHBwcVPcPcnNz43K5AoHgxYsXqn4jNzc3OgECgOLiYolEIpFIJk2apL6T0tJSkUhka2s7ePDgY8eO3bt3r6Sk5NGjR3l5ef379/fw8NApJFdXV4u/f09oP7KjP0ZyBJvkcDdOu3btrKys6L8tLS09PDyuX79eXFysmqvk6OhoZ2dH/y2Tyfh8PgAcOnRI/R7pAPDs2TMA4HK5AwcOPH78eHJysoeHh2oUj8lkahnP/fv3s7KyAGDNmjVr1qxRbb927VpoaKij3rofWsdJpvFsbcHa+uXfHA707Alnz8Lz5//MXHFxgfbtX/4tkUBeHgDA1q2wdeu/9pOdDQDQsSOMGgX/939w7Rr07Pnyi3nkSDA3f9M4T52CBw/g7FnQZf6A9rSs7RZ/uMEoj3h1NTT7z2ltKtxIDnejCxOcfw+misVijtYD6q2+8JvQJomhKEqpVAKAu7t7v379rl27lp6eTvcTDBgwwFr1j7BlMoYj2GyHu3GYTKY2CZBSqaQoiiCIIUOGnDx5MiUlpWfPnhkZGR4eHr1799byveRyeUJCQr1PZWVl3b9//5133tHTx2wFJxn9MjfX6uuwthYoCggCgoNhzx64fh28vSExETw9wddX5zeNi4Nhw17+rVRCVhZ89BHcuQOnToFaet2EtKntNnG4oXmPON2zmJQEOTng7f3P9idPICwMpk6FoCA9jeW9tsKN5HC/SeE2fZvhN/HkyROSJOl+poKCAoFA4Obm5vCKmZj29vYEQXC53MjISHrYRQObzfb397927dpvv/1WVlbm4ODg7+/f5DFX/31VSG1trerSMKQ/AoGgtLTUxsYGAKqrq+kBOFdX13oH2phMJt1+Pvroo08//bTeHXp6enp6emZkZBw+fFgikQwePNjJyUnLYJ49e3br1q1XPZuQkDB06FDtO7SQDp4/Bz7/5TRtsfjlcEznzvUPu7BY4OwMAPD117BxY/075PHAxwcSE2HbNhCLYcwY6NDhjSJkMP4Z5cEr8t6cUR3xvn3BxQX4fPjkE9i5E/r3BxMTyMmB5cvhwgU4fhyOHYMpUwxdZS0VzoVqpHPnzsXHxyuVSj6f/+uvvwJAt27dXjUU4uHh4enpWVBQcPr0aalUKpVKt23bxuPxvvzyS9UMdB6PR890EQgEffr0cXV1Vb38tYsaNMzMzMze3h4AEhMTS0tL5XL5hQsXXtUhgZqQUCg8cOBAWVkZSZKXL19OSEggCKJfv371FjY3N6fnul29ejU9PV2pVN67d2/s2LG+vr6q1MfGxsbf35++Lk91LSf91GsXNUhLSxMKhR4eHufOnUtRs3LlSgC4desWPVyImh6fD5s3Q3ExkCT89htcvAhmZjB4cP2FWayXnUO//w63b4NSCQkJ4OEBTCZcuvSyjIMDjB0LYjHExoKZGYwcCX83Ax0WNVCfTm5iAp6eLy+b797d0PXV8hnVEX/rLViwAADg7l0YNAjMzMDUFHr2hAsXAACGDoWAAEPXVwuGvVCNZGJismrVKtXKzhwOZ+rUqWw2Wy6X1y1sa2s7Y8aMr7/++vDhw4cPH9Z4Cf2wffv2/fr1o6+N8vf3Z+s6FfTV2Gx2nz59rl+/npCQMHr0aAAgCIIgCFyWWt+YTOatW7eCgoJUW0JCQrzV+9L/LSAg4Nq1a/Hx8fQFCnVfwmAwfHx82Gy2RCKhe6S0jKSioiI2NhYAvLy82qsmYQAAQP/+/emZfDdu3Ojatatqhh9qMiwW/PEH/PbbP1tmz4ahQ19Z/t134fRpOH8eBg2q/yUMBgwfDhwOiMXg4wMNXmWim8BAGDfO0PXV8hnVEScI+OILKCurZ3XNjh1h0ybgcg1dXy0Y9kI10qJFi9auXevu7k53Buzevbvhy+UCAwP3798/ZMgQevpLYGDg3r171V9CbwQAd3d3XhOeEwEYDMbUqVM/++wzejzRx8dn586dQxv494yaSPfu3Xfv3h0UFMRkMu3t7T/77LNVq1a96nI5ALC2tt68efPixYtdXFwAwN3dffny5Rov6dq1K339pr+/Pz1EqI28vLzMzEwA8PPzMzMzU3/K1dV1wIABAJCUlFSJgzj60Lcv/PknTJkCLBZwubBlC/z4Y0OXy9nZwW+/webN0KkTAED37rBjh+ZL+vR5uTTi2LFNs5JTp06wdi1ERcG/M2zUGMZ2xK2sYMcOuHwZgoKAPpnQh/vOHdDDjJG2hfq3yspKSmv6K1xYWKjXMLy9vb29vbV/lUp5efnMmTO9vb3PnDnTiJe3EbpWrwHbRqNbQsPOnDnj7e09c+bM8vLyJt95C1Jv9RrheUNPzYD6+WcKgPL1pUpLm37nLYf21dtsbQOPuF5pWb2tIN/AXiiEEEIIIZ1hCoUQQgghpDNMoRBCCCGEdIZX5OnGxsZGY+VohOoaP378+PHjDR0FMrS5c2HuXEMHgZoRHvE2BnuhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjoj+Hy++mMOh6OxpQH6KwwARhIGarQW1zaQnjTbSQawbRgxbWrbSNoGahKvrfBWkG8Q9K0kVMRiscaWBuivMJ/PN4YwGiEyMvLQoUOjR49eu3Yti8WSyWSJiYlxcXFLly7V/nYc+nD//v3FixdLJJLQ0NDVq1czmUx9v2OLaxtNy9haAh2PxkZ7e/thw4bNnTvXmb5XvH4020nGGNvGqlWwdStMmwY//QRsNkilcOUKnDkD//1v09yYpXGKi+Gnn+DECUhPBxYLhg6F5cvhnXfARI/jEtrUtpG0jTdibEecjkedrS2MHAlLlsCgQaDPe2K+tsJbQb6BA3n6dfny5eXLlz99+tSwYVAUFR8fL5FIAODWrVvPnj0zdMXoi1gsNnQI9TOSlqChrKzs1KlTS5YsKSgoMHQsTclomwEcOwbvvgtZWYaMIT4efH1h7VpITwcAkMngyhUYNQo2bIAWe+txPOI6KC+H33+H4cNh376We8SNBKZQTWzJkiUpKSkREREN3E22+QmFwsTERNXfaWlpho5IX6KiooYNG7Z+/fq4uDjDRmKcLaFeubm5N27cMHQUTcl4mgFs2QIUBUePNnSX2eb06BHMmwf1/ojavBlOnzZ0fI2ER1xnCgWsXg3JyYaOo2XDFKqJRUZG8ni8sLAwkUgUFhYWHh4OAA8ePBgxYkRYWJhMJqMoKjMzc9GiRb6+vgEBAZs2bSoqKqJfKxKJZs2axePxTp48ef78+QkTJvj6+q5YsaKoqKioqGj16tUDBw4MDg4+ceIE+fdPh5SUFB6Px+PxUlJSGojq/v37WVlZnp6eoaGhABAbG1tRUWHoqtKXqqqq6Ojo5cuXDxs2bMuWLYY6pRpnSxg9enRCQkLK386dO9e3b18AEAqFBqkl/VFvBob8Zl21ChgMmD4dhEKYPh0++ggA4M4dcHSE6dNBIgGKgqQkGDUKmEyws4P58//Jb4RC8PMDBgP27oVff4UePYDJhEmT4NkzePYMpk4FCwtwd4fdu//pS7h+HRgMYDDg+vV6gqEoOHkSsrPBzAzCw6GsDCgKxGL48UdgsUChgDNnQCIxTEW9MTziDUU1bRpUVwNFAUVBWRns2AEsFpSXQ1QUdkS9CVydvLklJSV99dVXdLezWCw+ffp0SkrKjh07PDw8VGV27twp+ftEFhsbKxKJampqMjMzAaC4uHjbtm02NjYjR47U8h3lcnlCQgIAeHt7jxkz5tatW2lpaZmZmYMGDTJ0ZegLRVEAUFVVdenSpUuXLllZWQ0fPjwgICAgIMDQof2j+VtC3VpSKBS1tbUA0LFjR0PXR9NTNYPo6Ojo6GjjbAYQGwvvvw/l5QAA5eXw009w/TqcPQs9e/5TZsUKUA1UnTwJQiFIpXD3LgDA8+fw+efg4ADvv//696qoePlF++mnsHo1EAQAgJUVfPwxPH0KJiYwfz5YWBi6RhoPj7hW7Oxg8WIoK4NNm+DuXRCJDDktr4XDXih9YbFYERER69atA4DevXvHxMRERETU1NQcOHBALBbPnTs3ISEhNjY2ODg4Pz//1KlTpNpPAQcHh4MHD969e3fBggUAkJqa6urqeuXKlQsXLvTt25ckybS0NFLrnw7Pnj27desWQRDDhg3r0qXLoEGDSJK8efMNcviHAAAn+UlEQVSm9ntocRgMBoPBoM+nFEWp/zxdvnx5dHR0c86cMJ6WAACXLl0aPHgw3V/l4+Pz3nvvPXjw4J133hkxYkSzVUizabgZXLp0qVkn0LDZcPQo/PwzAICvL5SWwtGjIJPBt99CeTmEhYFEAmVl8OGHkJ0NP/30r74BZ2e4dQtIEtavBwC4fh06dwaBAPLzYfBgUCggPl6rvoSSEsjNBQAYOfJl/kQjCPjPf2DLFujcWa/zi/WtgSMeERHRzP/wjeKIvwpBAJ1WCgRQWtp8ddLqYC9Us8rPz8/MzORyucHBwSwWi8VihYSEXLx4MT09XSwWM/4+eQ0bNqxPnz4MBoPH49FbJkyYYG9vT1HU22+/ff/+/YqKCpIkCYJ47cANAKSlpQmFwv79+3ft2pXJZPr5+Z07d+727dsCgcDNzU1/H1YVvKHQ9UmfUun/V1VVxcXF0T389G9T+qnmj80gLaFetra2Q4YM0esVmoZtCQ00gy1bthi2GUBODiQlQceOMH06WFiAhQXMng1HjsDt21Be/k82Exr6cnxH1Zsybx44OQFFwcCBkJAAZWUglwNBwLBhQFGvfLva2pffu1ZWzf9Zm60Z1HvEExMT6fmgbeuIN4DAb/8mgJXYrIqLiyUSiUQimTRpkvr20tJSkUhka2tLP2zfvr36P28ul+vo6AgADAbDRMerjsViMZ0xJCUlBQYGqrbn5+ffunVr8uTJhq6SZkLVOctQFEU17tTTFJq/JbxKeXn5+vXri4qK5s6dS7T2s6qxNQN4/hzEYhCL4a23/rWdzwehEBwdXz50c/tX51DHjkBfVs1ggKlpY963qspgH7l54RF/pdY7CtGcWvkZs6WgKEqpVKoeWlpaNtWec3NzMzIy6n0qLi5uzJgxHA5HTx9K+04RsVisfRgNr+Gxd+/effv20X+rTpSqLMTKyorH4wUEBAwfPpx+xw0bNujp4zeO/loCTbVOFf1QIpGcOXNm+/btly9fHjt2rKurqz4+lEZL0OlwN65taNMM/Pz8VO3f2JoBKJWg1gygqf6ROjmBmxs8ewZXr8KoUf/0Q1AU7NgBJSUwfz506qSnsTxtTgiNbhuvPeK9evUaPXq00f7D19cRfxWKAvoabUdHsLc39IdvwTCFalb29vYEQXC53MjIyLoTeEUiUdO+HUmSMTExkldcYpORkZGbm0tfkNXK0OdQ9RMo3Xs/fPhwQ4f2UjO3hFdRdWXJZDK5XG7oWmliDTcDnb6t9YXLBTMzcHeHixehe3fNZ5v8Msl27cDXFxIS4Mcfwd4eFi0COzuoqoLjx2HTJigvh6QkOHEC7OwMXC2N1cARb76lNRvWzEe8XlIpnD4N27cDAHh5gUHXfG7pcDp5c6itrSVJsqampmPHjp6engUFBadPn5ZKpVKpdNu2bTwe78svv5Q06lrihi9lLy8vT01NBYBFixalqLl06ZKnp6dEIomJiWmVk8rpWaVWVlajRo3atm3b9evXN2zYYAz5k6Fagor6dHIejzd48ODt27cDgKOjo2FXz9cHVTMYN26cUTUDIEkgSZDJoHt38PGBJ0/gp5+guhqqq2HpUmAw4L33GjnW1vAl7gQBH38M3buDQgHr1oG9PTAYwOHAvHkvLxCbPr3l5k+AR7wBUVFgafmyJJsN06dDeTnY2sLcuaD/O1W0YtgLpV92dnYAkJWVNWrUKHoMZcaMGV9//fXhw4cPHz5Ml+FwOFOnTmWz2U3eDZCampqVlcVms/v376++3cHBwc/PLysrKz4+fvLkyXqdVN78uFyuj48P/dPTKHoaAMDQLaFhBEFMmjRJNQGrdVBvBoaORY2TEwBASgo4O7+8B8jy5fDhh7BtG2zb9rKMrS0sWQJWViCTNX0APXvC/v0wY0Y9q2suWQIteXIkHnHdmJnB2rXg42PoCmrZsBdKv3g83syZMzkcDpPJZLPZFEUFBgbu37+fvgaKyWQGBgbu3btXH9eqyOVy+gqUPn36qC81BAAMBsPf35/NZtPXhRm6kprStGnTLly4YCw/PdUYsCU0gL5Cc+fOncHBwYauoaZktM0Ahg2DFSvA1hZYLLCyAoqCiRPhxg0YOxZYLGCx4L33IDYWhg3TYwz+/nDnDqxdC506AQCwWBAUBJcvw44dBrlSr0ngEdeBrS1MngyJibB0KV6X94YYGtcm6G+mZxNOGX7zMOgvqsZdBI5eS9fqNWDbwJagV/VWrxGeN7AZ6JX21dtsbQOPuF5pWb2tIN8g6i41ptPiY62+MGo0IzmCeLgNrnWcZNAb0rK28XC3GtpUuJEc7kYXJjQyNSPJCo2kMHoTxnAE8XAbg1ZwkkFvTpvaxsPdmry2wo3kcL9JYZwLhRBCCCGkM0yhEEIIIYR0hikUQgghhJDOMIVCCCGEENIZplAIIYQQQjrDFAohhBBCSGeYQiGEEEII6QxTqJZEJpPFxcWtX79eJBJp+ZLIyEheHUFBQREREUVFRYb+QKiRGtESaGVlZfv3758yZQqPxxs4cOCiRYtu376tVCoN/YFQo0ilcPYszJkDQqG2L1m16uW9ZlX/2dnBBx9AQgL8+04VyDAoCnJzYdUqOHKk+d40Kws8PP65V7HGQ/RqmEK1JJcvX16+fPnTp0/fcD9lZWWnTp1asmRJQUGBoT8TaozGtYS0tLSZM2fu3r07JycH/r6L4uLFi/ft20eSpKE/E9LdsWPw7ruQlfVGOykvh99/h+HDYd8+wGZgcGVlMG0abN0KzXuvcdQ4mEK1Xbm5uTdu3DB0FKiZ5OXlhYeHCwSCuk8dPHjw2rVrhg4QGZRCAatXQ3KyoeNAqCXBFKqJ0QNnYWFhaWlpK1asGDhwYEBAwMGDB2UyGV2AoqjMzMxFixb5+voGBARs2rRJNaCWlZU1atQoHo+3bds2kiQpijp48CCPxxs7dmxmZmZYWFh4eDgAPHjwYMSIEWFhYTKZLCUlhR6ba/iGjqNHj05ISEj527lz5/r27QsAQu37/5GOjKolUBQVExOTn59PEMTChQtjY2NTUlLi4+NXrVrFZDJJkoyLi1MFhpoSPXA2fTrcvAmTJoGFBdjZwZYtIJW+LEBRkJQEo0YBkwl2djB/Pjx79vKp1FRwdQUGA5YuBZIEioItW4DBAA8PSEqC6dPho48AAO7cAUdHmD4dJBK4fv3l8FzDQzDTpkF1NVAUUBSUlcGOHcBiQXk5REVhR9Trqca5/vgDdu6EHj2AwYARI0D9n151NWzZAs7OwGCAjw/89tvLiiVJWLoUGAxwdYXUVACAJ0+gd29gMGDNGoiNBUdHuHMHAOCjj14eR4kEpk9/2YokksbEc+AAMBjg5/fPgK+W7QS9DmHoAFqnuLi4P//8kx4ckcvlu3btAoDZs2czGIykpKSvvvqKvk+hWCw+ffp0SkrKjh07PDw8evbsOWXKlF27dl29enXs2LEkSR46dAgAPv74486dOzdVbBRFKRSK2tpaAOjYsaOhq6qVM5KWUFVVRadW77///pw5cwiCAAA2mz1hwgQ+n89gMCZOnGhubm7o2mq9zpyBEydAoQAAkMlg9WoAgJUrgcGA2Fh4/30oLwcAKC+Hn36C69fh7Fno2RO8vOCzz2D1ajhxAmbOBLkc/vMfAIC1a+Gtt5osNjs7WLwYyspg0ya4exdEInBwMHR9tRAffACqO87GxsKsWXD2LHTpAlVVsGgR/Prry6dSUmDqVMjOhjVrgCDgs8/gzz8hMxN+/RW6d4f//hcyM2HwYFi8GHJy9BIP0hvshdILkiSXLVuWkJBw4cIFb29vAEhKSqqqqqqoqDhw4IBYLJ47d25CQkJsbGxwcHB+fv6pU6dIkmQwGOPHj+/fv79QKDxw4MDu3bvFYnFQUFBQUJCFhUVERMS6desAoHfv3jExMRERESwWS8t4Ll26NHjwYLqXwsfH57333nvw4ME777wzYsQIQ1dVK2ckLeHFixeFhYUA4OvrS+dPNIIgPv/88yVLlri5uTEYDEPXVuulUMD27SCRQH4+DBsGABAbCxUV8OIFfPstlJdDWBhIJFBWBh9+CNnZ8NNPQJLAYMDcuRAYCHw+fPstrFsH5eUwZQp88AFYWsLRo/DzzwAAvr5QWgpHjwKb3cjwCAICAgAABAIoLTV0ZbUcb78Njx4BScL+/WBmBpmZkJYGAHD+/Mv0KDUVSBIuXgRbW9i7Fx4+BADo0gW++grMzODXX2HDBjhwADgcWLsWXFxg2DAoLQVfXwCAn38GinrZWt4wHqQ3hFiVtP6t7pYGtPrCjePp6Tlq1CgWi8XlcocPH56amlpdXV1bW/v8+fPMzEwulxscHMxisVgsVkhIyMWLF9PT08Visa2trZ2d3axZszIzM2NjYwHAwcFh5syZ7FefGV87hPcqtra2Q4YMYTKZ+qsEIzmCzXC4G2AkLUGpVNI9YexGf8u+gdZxknkjPj4wZQpYWECHDjBhAly/DpWVQJLw5AkkJUHHjjB9OlhYgIUFzJ4NR47A7dtQXg6OjtC+PXz1FSQlwcmTAAAuLrBiBVhZvfKNhg1r5IV1hN5HJLSs7ZZ0uOfOhR49AABGj4ZeveDePaisBLkcYmMBACZMAC8vAIChQyEoCI4fh+RkePttAICJE+GPP+C332DbNgCATz+FBn7Nstlw9CgcPdrIeAxHmwo3ksPd6MIEh8PReE5jS8M7at2FG83V1dXCwoL+29LSUrW9uLhYIpFIJJJJkyaply8tLRWJRLa2tgDQv3//8ePHHzt2DABmzpzZs2dPfURYXl6+fv36oqKiuXPnEvo5exrDEWyew90AY2sJknrnUuhZKzjJvKlOnUB19NXf9PlzEItBLNYcmOPzQSgER0cAgBEjYO5c+P57AIAvv3z5rdzk9D8FSpvabmGHWzVGZm4OqnFwiQTy8gAAtm6FrVv/VT47++UfVlawYgXcuAF8PvTpA8uXN00KW288hvPaCjeSw/0mhXEgzyhQFKVam6e6ulp1sTrdafHm+9eYTh4fH798+XIAuHz5cnFxsaE/PfqHnlqCnZ2dk5MTANy5c0d9/QKKoo4cORIZGVlQUEDhskDGQ6kE1WJdlZX/LFtw44Ze+hUoChITAQAcHcHe3tAfvvWqrf2nj/DJk5djpo8eQXq6oSNDjYTTyZuVvb09QRBcLjcyMrLeqdwURf3xxx+J9OkMIC4u7vz58x988EHTzlMxMXmZOstkMjmuPmIIzdwSLC0te/fuff/+/RMnTlhbW0+ePNna2loikVy5cmX//v1isfjhw4dbt261trY2dMW0MVwumJmBuztcvAjdu9dTgKLg6FG4cuXlwzNn4NdfYfFiaMITglQKp0/D9u0AAF5eYGNj6Epp4VgscHYGAPj6a9i4sf4yz5/D5s0vLy9QKGDtWnj7bejQQb+B1dRATc3Lv6uqDF1NrQT2QjUrDw8PT0/PgoKC06dPS6VSqVS6bds2Ho/35Zdf0iMsjx49OnjwIAAsXbp09uzZAHD48OEnT56o76S2tpYkyZqaGoqitFzUQH06OY/HGzx48Pbt2wHA0dHRBs+YhtDMLYEgiIkTJ7q7u5MkuWfPnsDAQB6P5+/vv3HjRnpcf8yYMZg/GUCPHuDjA0+ewE8/QXU1VFe/vOL9vfdefsmlpcGWLQAA27bBqlUAANu3Q2bmv3ZCkkCSIJMBRWl7sXpUFFhavizJZsP06VBeDra2MHcu6HN+ZJvAYr2cA/7773D7NiiVkJAAHh7AZMKlSwAAJAnbt0NaGnh5wfnz0LEjpKXB7t2aY6lyOcjloFC8flGD13JyAgDIzIQbN0CphJwc2LzZ0NXUSmAK1axsbW1nzJjBZDIPHz48ZMiQIUOGHDt2jMPhTJ06lc1mSySSX3/9VSgU+vn5hYaGvv/++z169BAIBD///DP9tWpnZwd/LxoUHh5eo/pJ0SgEQUyaNImedoOaWfO3BA8Pj3Xr1nG53LpPTZkyZeTIkYaukjbJ0RGWLwcWC7ZtAysrsLKC778HW1tYsgSsrKCqCv77X+DzISgI5syBTz8FLy949gwiIl4mWPRXY0oKODvDRx/9s9ZUI5iZwdq14ONj6BppFd59F8aNg+xsGDQITE1hyBB49gymT4ehQwEAYmLgwAEwM4PVqyE4GJYvBwDYtQtiYgAAzM2B/kf6ySdgbg63bjVBPD17Qq9eoFDAtGlgagrdu+PQYVPBFKq5BQYG7t+/n74ajslkBgYG7t27l8fjURR15cqVK1eucDichQsXWltbc7lcegkfejtFUTweb+bMmRwOh8lkstnsRk9eYTKZfn5+O3fuDA4ONnR9tF3N3xK8vLx+/fXXefPmubi4wN/NYNeuXcuXLzfIlXoIAGDiRLhxA8aOBRYLWCx47z2IjX15Yd3x4/Dbb2BrCxs2gJ0ddOgAq1eDmRn89hscP/7yivcVK8DWFlgssLJq5LV4trYweTIkJsLSpc1wXV6bYGcHv/0GmzdDp04AAN27w44d8OOPwGYDnw8bN4JYDHPnQmjoy76loCAQi2HjRuDzgcOBL78EHg8AoFOnprlxYZcucOgQBAWBmRlwubB+PRw+bOg6aiUYGidfI5n0zufz6bO8nsLg8XgA0LjlANBr6Vq9Bmwb2BL0qt7qNcLzBjYDvdK+eputbeAR1ystq7cV5BvYC4UQQgghpDNMoRBCCCGEdIYpFEIIIYSQzjCFQgghhBDSWZu+/oKe8oYQtgQE2AzaHjzi6A210V4ob29vQ4fQyvXt29fQIWgFW4K+tYgabhFBtmjGVsPGFk/r00ZquI32Qv3000/aFDOqhRj0UVivMWtZ0rDUW0ILrecWF7MReu0JoSXWc0uMudk0fMRbfT0bScytAKNSHzetfGPG+a8OYzYGGDPGjDFjzBizcWprMRMarzSSTBYLY2EsjIWxMBbGwljYmAu30blQCCGEEEJvAlMohBBCCCGdYQqFEEIIIaQzTKH0q6KiYvv27YmJiRKJhN6Sl5e3fv36pKQkmUym/X5EItHq1asPHDiQl5dn6M+EEEJIBxkZGbt27crJySFJkt5y8eLFyMjIv/76S6lUar+ftLS0L7744vz58y3lkudWD1Mo/aIoKj09fcWKFXfu3KEoit6SlJS0bdu2Z8+e6bQrPp8fFRVVXV1t6M+EEEJIB3K5/ODBg5s2bSouLqa3KBSKQ4cO/fzzz6pf19pQKpXXr1//888/Df2B0EttdF2oZtauXTsPDw8Gg6HaYmdn5+TkBABVVVWXLl3y8fHx8PB47X7Mzc3ZbLb6FpFIVFZW1rlzZ/Wd03JychYvXiwUCgEgNDR09erVTCbT0DWBEEJtlJubm729vfoWZ2dnKysriqKeP39+69at0NBQjTN8vSwtLc3MzFQPKYrKz8+nKEp1pdjTp08XL14sEAg0Xujh4TFo0KAPPvjA2tra0JXRSmAK1ZREItH169eLiopUW2QymUAgkEgkx48ft7GxoctUVlYqFIpffvlFoVBcvXq1rKzM3d09PDy8T58+De+/pqYmPT29pKSEfvjkyZNffvlFLBavXr163LhxJib/6lNMSkqi8ycAuHfvXklJiZubm6FrCCGEWrn/b+9cg5o62ji+uZCQkGCCiSZGbnKRiDiiggLVMYgMioCK6BSGFi9VWzutFSytiqM41modbR2q1Eup2hlAxCmImmoFQ1BBjRERxaKSIBcvKJdQCbm+H7ZzJu9JwFCUgO7vU7Jnz2az53/OeXb32WcfPHhw5coV0+ElaM38/fffx48fh0ZSTU0NAEAul2dmZiqVyuLiYp1OV1lZmZqaCt8UvdDS0nL9+nXYJTYYDCUlJQUFBaNHj/7++++9vLx6OVGhUCgUitOnT69duzYmJsa8443oK8iEepOwWKyoqKju7m4ajQZT2tra5HJ5S0vLkiVL3N3dAQB1dXVSqZTNZiclJbFYrPXr11tfPpVKnTBhAiwHADB16tT4+HiLOdvb20tLS7Gv9fX1V65cWbx4sa1bCPEvxcXFSqUyPDycz+dD2/fIkSNEIjEiIsLBwcH6ci5cuCCXy0NDQ4OCguzt7W39txB9o7i4uKqqatGiReYy4PF41r/hzp49e/XqVSSDQYKnp6erqysAABsrkslkp0+f9vb2TkxM5HK5AICCggKpVOrv77969eq+ls/hcAICArALHRQUtGHDBuuDG6lUqh9//NHZ2RltEdh/kC/UG4ZIJGL2Uy8YDIY+eRH2FYVCUV1dDQCIjo4WCoUAgOLi4vb2dls3D+JfVCpVRkbG3r17se0B/vnnn4yMjJMnT2q1WuvL0Wq1Z8+eraioIJNRd2jooVKpjh07hmTw7mFnZ2c619YTBoMB+si+JSIiIi5fviyTyWQyWXl5+e+///7BBx8AAFQqVXZ2dp/csBAWQffb24VAIEyZMmX8+PF8Ph+mMBiM1NRUZ2dnNpsNbRqL09JGo9FoNOLm5nB0d3eTSCTzh6bRaJRKpa9evaLT6QsXLpRIJPfu3auurlYoFENl99/3BBcXF9ygvYuLC4VCMRgM8HrNmTPHmpcinU43zWYwGB4+fMjj8bBeaUFBQXp6uvmJFArF19d30aJFoaGhyFXOVrw9GdTW1prKAKOpqenUqVMlJSVwha+Xl1dISEhsbOx7tbvZQGJvb5+UlBQaGkqlUmGKp6fnwYMHYf/22bNnLBbL4g1oMBgIBEIv45FGo1GtVlsz9GhnZycUCjdt2pSamlpZWXnr1q36+nofHx9bt83QBplQb56WlpbHjx9rNBr4NTAwEABQWVmJZaBSqQqF4vz589nZ2Vwud/fu3XDU15Tu7u7vvvvuxYsX48aN0+v1BoMB51OlUqkuXLgwfvz4TZs2OTk54SpQXl4OAPDz83NzczMYDLm5ua9evbp48aKvry/qpw4wer2+pqZGLBZjkgD/7wkBU+RyOQCgpKREqVTev38fXsFHjx6tWrXqtc/H5ubmiooK+Fmj0fzxxx+XLl2aNm1aWloaj8fr5USNRiOXy+VyeWRk5DfffGONKyviv6HX6+/evXv9+nUrZdDc3FxVVdUfGZw8ebKsrAwnA51Ol5ubm5GRYVqN2tra2tra/Pz8b7/9Njw8HLnI9B+9Xv/48ePnz59jsw2BgYGdnZ0ymcz0LpPJZIWFhaWlpfPmzVu/fr35JVYqlRs2bPDy8oLWLeZTdfjwYfgkVyqVpaWlq1atioqKsqZiXC43LCyssrKytbW1oaEBmVD9BL1N3zwcDofFYun1eqzDIZPJVq5cGRERkZaWBm8SlUrV0dGhUqmCgoJGjBhhsRy9Xl9eXh4eHh4aGspkMteuXWt6tKCgICcnh8PhMBgM3Ik1NTX37t0DAEyZMoXJZI4ZM8bPz6+iouLy5ctLliwRCAS2bqH3CxKJ5OPjExISYjpkaO4JodFobt++LRKJ4OXu00/w+fypU6diX6dPn97XSv75558ikUgkEtm6td5ZSCSSn5+ft7e3lTKIiYnp60/gZDBx4kSckIxGIwxHhEUnMkWlUu3YsYPD4SAXmf5DIpHc3Nz4fL7p5d63b9/Ro0c3b96MXVy1Wi0Wi3U6na+vb08mckdHh0wmW7p0KfSC3bJlC3ZIrVZv27ZNrVY7OzuTSCQr6+bp6Qk/oBA5/Qf5Qr0VyGQyZj/1DpFItNjnIxAI1twSDAYDN/yr1WolEgkAgM1mBwcHAwCYTObMmTMBAAqF4s6dO7Zum/cUKpVqzfifXq9/q9XYvHmzzASJRJKYmAgA0Ol0VVVVtm6kdx/byuDBgwc///yzTqcjk8mffPKJWCy+ceNGRUVFVlYWHI1QqVRFRUWmA1SI/mDl5QYA9PS0JxKJ1pTg6Oho/dih9cYW4rWQm5qaTL8zmUxcSi+8vcwAgMFQjTdVZxhcoKurq7m5GZpWTCazra0Nl4gDdkpgNvOSYXpnZyfuUEdHBxzM9/b2JpP/vb4CgcDJyenly5enT5/29PQ0dXgfDE33HmpDr9cnJiZOmzYNS/fw8Pjhhx88PDwMBsOtW7c4HI5FTziLvhGmMjAYDBqNBtejhWqBH3A1gd4YAICuri7cocHQdO+2NnqRQUNDQ0tLC04GWMk4GZg/DQwGA4VCwcWwPnPmDHwWLVu2bN68eVqtFkZg4XA4X3/9dUZGRnBwcEBAABYM5Z1p50FS587OTvD/92B3d3dXVxewdGNCurq6HBwcXr58+ezZM/PXBHZ6S0uLt7c3VsKzZ8+gFW7x/YKFxenpR4d6Ow9knck4/0GVSmW9R+Hby9zU1DQYqvGm6gyfUzQajc/nYxN50KXJNNEUo9EIp8xhNvOSYTqDwcAdkkql8AJXVFQsWbIEd1ZNTY1Wq/Xw8Hgn23kw15nL5SoUitbWVrgARyAQCAQCGFIP5uFwOACABw8e5OTk3L59e+XKlR9//LF5B1Qmk23ZsiU4OJjNZgMA4LBibW1tYWEhzFBVVVVdXY1zasG8lVkslmm129vb4ZwvnU4XiUSmh4ZoOw+GavSSWavV4mRgb29vUQZ5eXlyuRwnA6xknAygT1XvMujq6oKhsV1cXCIjI3ET+kwm89ChQ+9MOw/OOkOnC9N7UK1Www4t7sbE6jxixAgikUgikUaMGGGeATsdygbLAFcagR7eL5cuXYIfBAKBNTUfcu08kHVGvlCDlO7u7ufPnwMA6urqbty4Ye7nW1dXZ37Wq1evrl692kuxra2tly9fHjt2LPIYHWDs7Oy8vLy6urqoVCocV4B+DGKx+ODBg5j3SVtbW1ZWlk6n8/Pz62kAv6mpqaam5qeffmKxWLhgMG1tbVevXiWTyaNGjbJ4idPT082X5pHJ5MTExEmTJtm6kd59zGVQV1d3+PBhcxkcO3bMehngDkEZkEgkUxl0d3fDzhWfz0fBqYcK7e3tra2tuKDKGBqNxpohQ1OgSzsAgM1mo2DL/QeZUIMdd3d36BWOS3/y5AmFQsH5kjc2Nt69e7f3AktKSqKjo2F4N8QAY03MMEh/fCOoVKr5IoNewLzdbd087wu2lQGbzbYmZBFi8IALqowBvdGHDx9uTUQSg8HQ2Nh49OhROAo1ceJEFxcXW/+zIQ8yoQaUzs7Oc+fOwXjlarUaAECj0Xp6Ss6fP/+rr75ycnKyuG4iIiJi1qxZuMeoVCp98eIFACA1NRUXi1yj0ezYsaOwsPDevXs1NTXIhBqisFgsOGj/Brlz586yZcs2btwYFRWFhieHBP2RQWtrq1arRUHMbYhSqbx48eLNmzcdHBzgXHxPexLQ6fRt27aNHTvWYgYqlbpx40a9Xk+j0aBTFA6xWCwWi83TmUzmhx9+iIKY9B+0Im9AYTAYCxYs2Lp1a1JSEpFIHD16dGRkpHmP0Gg0ZmdnHzhwwM7Orr6+Pi0tDTqsdHd379ix49dff1Wr1VQq9cmTJ0uXLi0sLIRLlNvb269duwYA4HA4/v7+uDIpFMq0adPg5+LiYrToZojSz3DGuBV55eXle/fu5fF4Op3uxIkTfZ0UQNiK/yADOzs7uMdtc3Mz2qjAtri6ui5btmzPnj0hISFarTYsLMziNHpHR0d6enp5ebmDg0NRUdGuXbvguoGGhobVq1dDnw0ajXbx4sXVq1ffv3/fyl+HIXLQxP0bAY1C2QACgSAUCg8cOABMNlEy5dGjR4WFhZMnT6bT6TQajcFgwEGCyMjIuXPnfv755/fv309LS/Pw8IiJidm6dWtTU9OKFSuwTV18fX0tOseNHz/ezc1NoVBcuXJFqVT2viElYnDS1tb29OlTKpUqk8kYDAaMQY8d7ezsxLYKsQY7O7vp06ffvHnz+PHjra2tnZ2daHhySICTAe6oRRnQ6XRfX1+JRFJfX3/hwoWkpCTTEcenT5+mpaVNnTo1LCyMw+GgwcgBgEKhREdHz549G3OMM8VoNF67du3GjRsLFiwAAEycOPHIkSPXr1/fuXOnu7t7QEDA2rVrk5OT4+LiwsLCpFJpSkrKrl27YCTnnnBzcxOJRAsXLmQymegSvxGQCWUzenJHaGxs3L59e319fVJSEswzY8aMc+fOicXimTNnwjiZf/31V0REhEgkmjVrVlFRUVZW1oQJE4KDg6VSaS+bTQoEgvz8fFv/b8QbwNHRcfLkyRbdyR0dHfV6vZXRaGA4KBhIDDHkwGSAS4cy0Gq1pjIgEAgzZsyAY42ZmZk6nW7x4sXDhg3T6XS1tbV79uy5efOmVCqVSCQ7d+5E/uYDhkXHOKPRKJFIjhw5wuFw4AJqHo8XFBSUm5tbVlY2ZsyYwMDA3377LS8vb/r06Xw+PzY2tqysbN++fXv37uVyue7u7mfOnOnlR3HRLhD/GWRCDQREInHevHmRkZGvfbEZDAaxWFxdXR0eHo7FmObxeCKRKCEhAU6Hi0Si6OjokJAQAACbzZ40aZJAIEBx+oc0VVVVcDdQDofT0NBAp9Mt+ocajUYOh3P06FFPT0+LviyOjo779+83GAw9uVZYXJEHEQqFI0eOtHVLvNeYykCpVPZTBu3t7bjtfTw9PdesWbN9+3adTpeZmYntKoNBJpMTEhKQ/fSWcHBwSEpKsmaj0ra2tpycHABAQkKCs7MzAIBMJo8dOzYuLm7OnDkAABcXl7i4uNmzZ8NL7OXl5e3tHRERAYNcIAYMZEINBP7+/ubOSRYhEonLly9fvny5aaK7u/vu3buxr3FxcdhnMpm8bt06W/8/RH/x8/Pz8/Pr6urKzs4uKyubP38+FrvLlMbGxpSUlKSkpHHjxh06dIhEIkVFRTGZzMrKykOHDq1Zs0YoFFKp1MzMzLq6upSUFGxz69fC4/FWrFiB3Etty3+WQXx8vL29PU4GOTk5MCcmAwKBMHfuXJVKhdsjD0KhUFJSUoKCgmzdDO8sy5cv72WWwBQ2m52ZmYmLVxQTE4PtDDNs2LAvvvgCO8Tlcvfv39/XjaEQ/Qe5kyMQgwUajbZ06dL8/Px169aZWzM6na6oqOjJkycuLi5EIjEwMDArKystLa2lpUUoFHK53E8//bS0tJRMJi9atKi5ufmzzz57+PDha3901KhR8fHxv/zyCxrIHCRAGZw/f956GSQnJ5vLIDo62lwGcJwpLy8vPj4eez27ubklJCTk5+fHxsaibcgRCOtBdwsCMYggEAg0Gs3c01On0506dSorK0soFMKAeJ6engEBARKJpKqqSiQShYSEFBYWnjhxYtKkSTweb/78+Tt37jxw4EB6ejqdTof9Vyt7wAibA2Vgnt4nGYwcORInA6yc0aNHJycnJycnYylIGwjEfwCZUAiEzXByclq3bp2rq+trczY2Nubm5g4fPjw+Ph66D1OpVB8fH7g2BwAgFAo/+uij2NhYuD7L399/zJgx4eHh1kdxRNgK62XQ3NxsUQY+Pj7mMlCpVEgGCMRbBZlQCIRtsLe3Nx0G6B1XV1fcakoymbxy5UqVSgVtJoFA8OWXX2JHvby88vLybP0XEa+HSqVaLwNnZ2eLMsC+IhkgEAMJ8oVCIBAIBAKB6DOEPgXiGzCG4sQ8qjOqM6ozqjOq8+AE1RnV+W3UmYw7s09locwoM8qMMqPMKDPKjDK/n5nRRB4CgUAgEAhEn0EmFAKBQCAQCESfQSYUAoFAIBAIRJ9BJhQCgUAgEAhEn0EmFAKBQCAQCESfQSYUAoFAIBAIRJ/5H8CNdtRcNghkAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDIxLTEyLTAxVDA4OjEyOjA3KzA4OjAwO2Rk5QAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyMS0xMi0wMVQwODoxMjowNyswODowMEo53FkAAAAASUVORK5CYII=)
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
1. 拿到succ节点的prev节点
2. 使用e创建一个新的节点newNode，其中prev属性为pred节点，next属性为succ节点
3. 将succ节点的prev属性设置为newNode
4. 如果pred节点为null，则代表succ节点为头结点，要把e插入succ前面，因此将first设置为newNode，否则将pred节点的next属性设为newNode

**过程如图：**
<center>

![avatar](data:image/png;base64,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)
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
1. 定义element为x节点的值，next为x节点的下一个节点，prev为x节点的上一个节点
2. 如果prev为空，则代表x节点为头结点，则将first指向next即可；否则，x节点不为头结点，将prev节点的next属性指向x节点的next属性，并将x的prev属性清空
3. 如果next为空，则代表x节点为尾节点，则将last指向prev即可；否则，x节点不为尾节点，将next节点的prev属性指向x节点的prev属性，并将x的next属性清空
4. 将x的item属性清空，以便垃圾收集器回收x对象

**过程如图：**  
<center>

![avatar](data:image/png;base64,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)
</center>
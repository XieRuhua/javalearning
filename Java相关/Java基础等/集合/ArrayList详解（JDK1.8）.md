# ArrayList详解（JDK1.8）
***
[笔记内容参考1：Java集合：ArrayList详解](https://joonwhee.blog.csdn.net/article/details/79190114)  
[笔记内容参考2：JavaGuide：ArrayList](https://snailclimb.gitee.io/javaguide/#/docs/java/collection/arraylist-source-code)

[toc]
## 一、ArrayList 简介
`ArrayList` 的底层是数组队列，相当于动态数组。与 `Java` 中的数组相比，它的容量能动态增长。 

**在添加大量元素前，应用程序可以使用 `arraylist.ensureCapacity(int minCapacity)` 操作来增加 ArrayList 实例的容量。这可以减少递增式再分配的数量。(最后有讲到)**

`ArrayList`继承于 `AbstractList` ，实现了 `List`, `RandomAccess`, `Cloneable`, `java.io.Serializable` 这些接口。
```java
public class ArrayList<E> extends AbstractList<E> 
    implements List<E>, RandomAccess, Cloneable, java.io.Serializable{
    // ...........
}
```
* **RandomAccess** 是一个标志接口，表明实现这个这个接口的 `List集合`是支持快速随机访问的。在 `ArrayList` 中，我们即可以通过元素的序号快速获取元素对象，这就是快速随机访问。
* `ArrayList` 实现了 **Cloneable** 接口 ，即覆盖了函数`clone()`，能被克隆。
* `ArrayList` 实现了 **java.io.Serializable** 接口，这意味着`ArrayList`支持`序列化`，能通过序列化去传输。

### 1.1. Arraylist 和 Vector 的区别?
* `ArrayList` 是 `List` 的主要实现类，底层使用 `Object[ ]存储`，适用于频繁的查找工作，线程不安全 ；
* `Vector` 是 `List` 的古老实现类，底层使用 `Object[ ]存储`，线程安全的。

### 1.2. Arraylist 与 LinkedList 区别?
1. **是否保证线程安全：** `ArrayList` 和 `LinkedList` 都是不同步的，也就是不保证线程安全；
2. **底层数据结构：** `Arraylist` 底层使用的是 `Object数组`；`LinkedList` 底层使用的是 `双向链表`（`JDK1.6` 之前为循环链表，`JDK1.7` 取消了循环。注意`双向链表`和`双向循环链表`的区别）
3. **插入和删除是否受元素位置的影响：** 
    * **`ArrayList` 采用数组存储**，所以插入和删除元素的时间复杂度受元素位置的影响。 比如：执行`add(E e)`方法的时候， `ArrayList` 会默认在将指定的元素追加到此列表的末尾，这种情况时间复杂度就是 `O(1)`。但是如果要在指定位置 `i` 插入和删除元素的话（`add(int index, E element)`）时间复杂度就为 `O(n-i)`。  
    因为在进行上述操作的时候集合中第 `i` 和第 `i` 个元素之后的`(n-i)`个元素都要执行向后位/向前移一位的操作。 
    * **`LinkedList` 采用链表存储**，所以对于`add(E e)`方法的插入，删除元素时间复杂度不受元素位置的影响，近似 `O(1)`，如果是要在指定位置i插入和删除元素的话（`(add(int index, E element)`） 时间复杂度近似为`o(n)`)因为需要先移动到指定位置再插入。
4. **是否支持快速随机访问：** `LinkedList` 不支持高效的随机元素访问，而 `ArrayList` 支持。快速随机访问就是通过元素的序号快速获取元素对象(对应于`get(int index)`方法)。
5. **内存空间占用：** `ArrayList` 的空 间浪费主要体现在在 `list` 列表的结尾会预留一定的容量空间，而 `LinkedList` 的空间花费则体现在它的每一个元素都需要消耗比 `ArrayList` 更多的空间（因为要存放直接后继和直接前驱以及数据）。

## 二、ArrayList 核心源码解读（注释）
```java
package java.util;

import java.util.function.Consumer;
import java.util.function.Predicate;
import java.util.function.UnaryOperator;


public class ArrayList<E> extends AbstractList<E>
        implements List<E>, RandomAccess, Cloneable, java.io.Serializable
{
    private static final long serialVersionUID = 8683452581122892189L;

    /**
     * 默认初始容量大小为10
     */
    private static final int DEFAULT_CAPACITY = 10;

    /**
     * 空数组（用于空实例）。
     */
    private static final Object[] EMPTY_ELEMENTDATA = {};

    // 用于默认大小空实例的共享空数组实例。
    // 我们把它从EMPTY_ELEMENTDATA数组中区分出来，以知道在添加第一个元素时容量需要增加多少。
    // 在第一次调用ensureCapacityInternal时会初始化长度为10
    private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};

    /**
     * 保存ArrayList数据的数组
     */
    transient Object[] elementData; // non-private to simplify nested class access

    /**
     * ArrayList 所包含的元素个数
     */
    private int size;

    /**
     * 带初始容量参数的构造函数（用户可以在创建ArrayList对象时自己指定集合的初始大小）
     */
    public ArrayList(int initialCapacity) {
        if (initialCapacity > 0) {
            // 如果传入的参数大于0，创建initialCapacity大小的数组
            this.elementData = new Object[initialCapacity];
        } else if (initialCapacity == 0) {
            // 如果传入的参数等于0，创建空数组
            this.elementData = EMPTY_ELEMENTDATA;
        } else {
            //其他情况，抛出异常
            throw new IllegalArgumentException("Illegal Capacity: "+
                                               initialCapacity);
        }
    }

    /**
     * 默认无参构造函数
     * DEFAULTCAPACITY_EMPTY_ELEMENTDATA 为0.初始化为10，也就是说初始其实是空数组 当添加第一个元素的时候数组容量才变成10
     */
    public ArrayList() {
        this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
    }

    /**
     * 构造一个包含指定集合的元素的列表，按照它们由集合的迭代器返回的顺序。
     */
    public ArrayList(Collection<? extends E> c) {
        // 将指定集合转换为数组
        elementData = c.toArray();
        // 如果elementData数组的长度不为0
        if ((size = elementData.length) != 0) {
            // 如果elementData不是Object类型数据（c.toArray可能返回的不是Object类型的数组所以加上下面的语句用于判断）
            if (elementData.getClass() != Object[].class)
                // 将原来不是Object类型的elementData数组的内容，赋值给新的Object类型的elementData数组
                elementData = Arrays.copyOf(elementData, size, Object[].class);
        } else {
            // 其他情况，用空数组代替
            this.elementData = EMPTY_ELEMENTDATA;
        }
    }

    /**
     * 修改这个ArrayList实例的容量是列表的当前大小。应用程序可以使用此操作来最小化ArrayList实例的存储。
     */
    public void trimToSize() {
        modCount++;
        if (size < elementData.length) {
            elementData = (size == 0)
              ? EMPTY_ELEMENTDATA
              : Arrays.copyOf(elementData, size);
        }
    }
    
    // 下面是ArrayList的扩容机制
    // ArrayList的扩容机制提高了性能，如果每次只扩充一个，
    // 那么频繁的插入会导致频繁的拷贝，降低性能，而ArrayList的扩容机制避免了这种情况。
    /**
     * 如有必要，增加此ArrayList实例的容量，以确保它至少能容纳元素的数量
     * @param minCapacity 所需的最小容量
     */
    public void ensureCapacity(int minCapacity) {
        // 如果是true，minExpand的值为0，如果是fal，minExpand的值为10
        int minExpand = (elementData != DEFAULTCAPACITY_EMPTY_ELEMENTDATA)
            // any size if not default element table
            ? 0
            // larger than default for default empty table. It's already
            // supposed to be at default size.
            : DEFAULT_CAPACITY;
        //如果最小容量大于已有的最大容量
        if (minCapacity > minExpand) {
            ensureExplicitCapacity(minCapacity);
        }
    }
    
    // 得到最小扩容量
    private void ensureCapacityInternal(int minCapacity) {
        if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
            // 获取“默认的容量”和“传入参数”两者之间的最大值
            minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
        }

        ensureExplicitCapacity(minCapacity);
    }
    
    // 判断是否需要扩容
    private void ensureExplicitCapacity(int minCapacity) {
        modCount++;

        // overflow-conscious code
        if (minCapacity - elementData.length > 0)
            // 调用grow方法进行扩容，调用此方法代表已经开始扩容了
            grow(minCapacity);
    }

    /**
     * 要分配的最大数组大小
     */
    private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;

    /**
     * ArrayList扩容的核心方法。
     */
    private void grow(int minCapacity) {
        // oldCapacity为旧容量，newCapacity为新容量
        int oldCapacity = elementData.length;
        // 将oldCapacity 右移一位，其效果相当于oldCapacity /2，
        // 我们知道位运算的速度远远快于整除运算，整句运算式的结果就是将新容量更新为旧容量的1.5倍，
        int newCapacity = oldCapacity + (oldCapacity >> 1);
        // 然后检查新容量是否大于最小需要容量，若还是小于最小需要容量，那么就把最小需要容量当作数组的新容量，
        if (newCapacity - minCapacity < 0)
            newCapacity = minCapacity;
            // 再检查新容量是否超出了ArrayList所定义的最大容量，
            // 若超出了，则调用hugeCapacity()来比较minCapacity和 MAX_ARRAY_SIZE，
            // 如果minCapacity大于MAX_ARRAY_SIZE，则新容量则为Interger.MAX_VALUE，否则，新容量大小则为 MAX_ARRAY_SIZE。
        if (newCapacity - MAX_ARRAY_SIZE > 0)
            newCapacity = hugeCapacity(minCapacity);
        // minCapacity is usually close to size, so this is a win:
        elementData = Arrays.copyOf(elementData, newCapacity);
    }
    
    // 比较minCapacity和 MAX_ARRAY_SIZE
    private static int hugeCapacity(int minCapacity) {
        if (minCapacity < 0) // overflow
            throw new OutOfMemoryError();
        return (minCapacity > MAX_ARRAY_SIZE) ?
            Integer.MAX_VALUE :
            MAX_ARRAY_SIZE;
    }

    /**
     * 返回此列表中的元素数。
     */
    public int size() {
        return size;
    }

    /**
     * 如果此列表不包含元素，则返回 true 。
     */
    public boolean isEmpty() {
        //注意=和==的区别
        return size == 0;
    }

    /**
     * 如果此列表包含指定的元素，则返回true 。
     */
    public boolean contains(Object o) {
        // indexOf()方法：返回此列表中指定元素的首次出现的索引，如果此列表不包含此元素，则为-1
        return indexOf(o) >= 0;
    }

    /**
     * 返回此列表中指定元素的首次出现的索引，如果此列表不包含此元素，则为-1
     */
    public int indexOf(Object o) {
        if (o == null) {
            for (int i = 0; i < size; i++)
                if (elementData[i]==null)
                    return i;
        } else {
            for (int i = 0; i < size; i++)
                //equals()方法比较
                if (o.equals(elementData[i]))
                    return i;
        }
        return -1;
    }

    /**
     * 返回此列表中指定元素的最后一次出现的索引，如果此列表不包含元素，则返回-1。.
     */
    public int lastIndexOf(Object o) {
        if (o == null) {
            for (int i = size-1; i >= 0; i--)
                if (elementData[i]==null)
                    return i;
        } else {
            for (int i = size-1; i >= 0; i--)
                if (o.equals(elementData[i]))
                    return i;
        }
        return -1;
    }

    /**
     * 返回此ArrayList实例的浅拷贝。 （元素本身不被复制。）
     */
    public Object clone() {
        try {
            ArrayList<?> v = (ArrayList<?>) super.clone();
            // Arrays.copyOf功能是实现数组的复制，返回复制后的数组。参数是被复制的数组和复制的长度
            v.elementData = Arrays.copyOf(elementData, size);
            v.modCount = 0;
            return v;
        } catch (CloneNotSupportedException e) {
            // 这不应该发生，因为我们是可以克隆的
            throw new InternalError(e);
        }
    }

    /**
     * 以正确的顺序（从第一个到最后一个元素）返回一个包含此列表中所有元素的数组。
     * 返回的数组将是“安全的”，因为该列表不保留对它的引用。 （换句话说，这个方法必须分配一个新的数组）。
     * 因此，调用者可以自由地修改返回的数组。 此方法充当基于阵列和基于集合的API之间的桥梁。
     */
    public Object[] toArray() {
        return Arrays.copyOf(elementData, size);
    }

    /**
     * 以正确的顺序返回一个包含此列表中所有元素的数组（从第一个到最后一个元素）;
     * 返回的数组的运行时类型是指定数组的运行时类型。 如果列表适合指定的数组，则返回其中。
     * 否则，将为指定数组的运行时类型和此列表的大小分配一个新数组。
     * 如果列表适用于指定的数组，其余空间（即数组的列表数量多于此元素），则紧跟在集合结束后的数组中的元素设置为null 。
     * （这仅在调用者知道列表不包含任何空元素的情况下才能确定列表的长度。）
     */
    @SuppressWarnings("unchecked")
    public <T> T[] toArray(T[] a) {
        if (a.length < size)
            // 新建一个运行时类型的数组，但是ArrayList数组的内容
            return (T[]) Arrays.copyOf(elementData, size, a.getClass());
            // 调用System提供的arraycopy()方法实现数组之间的复制
        System.arraycopy(elementData, 0, a, 0, size);
        if (a.length > size)
            a[size] = null;
        return a;
    }

    // Positional Access Operations

    @SuppressWarnings("unchecked")
    E elementData(int index) {
        return (E) elementData[index];
    }

    /**
     * 返回此列表中指定位置的元素。
     */
    public E get(int index) {
        rangeCheck(index);

        return elementData(index);
    }

    /**
     * 用指定的元素替换此列表中指定位置的元素。
     */
    public E set(int index, E element) {
        //对index进行界限检查
        rangeCheck(index);

        E oldValue = elementData(index);
        elementData[index] = element;
        //返回原来在这个位置的元素
        return oldValue;
    }

    /**
     * 将指定的元素追加到此列表的末尾。
     */
    public boolean add(E e) {
        ensureCapacityInternal(size + 1);  // Increments modCount!!
        //这里看到ArrayList添加元素的实质就相当于为数组赋值
        elementData[size++] = e;
        return true;
    }

    /**
     * 在此列表中的指定位置插入指定的元素。
     * 先调用 rangeCheckForAdd 对index进行界限检查；然后调用 ensureCapacityInternal 方法保证capacity足够大；
     * 再将从index开始之后的所有成员后移一个位置；将element插入index位置；最后size加1。
     */
    public void add(int index, E element) {
        rangeCheckForAdd(index);

        ensureCapacityInternal(size + 1);  // Increments modCount!!
        // arraycopy()这个实现数组之间复制的方法一定要看一下，下面就用到了arraycopy()方法实现数组自己复制自己
        System.arraycopy(elementData, index, elementData, index + 1,
                         size - index);
        elementData[index] = element;
        size++;
    }

    /**
     * 删除该列表中指定位置的元素。 将任何后续元素移动到左侧（从其索引中减去一个元素）。
     */
    public E remove(int index) {
        rangeCheck(index);

        modCount++;
        E oldValue = elementData(index);

        int numMoved = size - index - 1;
        if (numMoved > 0)
            System.arraycopy(elementData, index+1, elementData, index,
                             numMoved);
        elementData[--size] = null; // clear to let GC do its work
        // 从列表中删除的元素
        return oldValue;
    }

    /**
     * 从列表中删除指定元素的第一个出现（如果存在）。 如果列表不包含该元素，则它不会更改。
     * 返回true，如果此列表包含指定的元素
     */
    public boolean remove(Object o) {
        if (o == null) {
            for (int index = 0; index < size; index++)
                if (elementData[index] == null) {
                    fastRemove(index);
                    return true;
                }
        } else {
            for (int index = 0; index < size; index++)
                if (o.equals(elementData[index])) {
                    fastRemove(index);
                    return true;
                }
        }
        return false;
    }

    /*
     * Private remove method that skips bounds checking and does not
     * return the value removed.
     */
    private void fastRemove(int index) {
        modCount++;
        int numMoved = size - index - 1;
        if (numMoved > 0)
            System.arraycopy(elementData, index+1, elementData, index,
                             numMoved);
        elementData[--size] = null; // clear to let GC do its work
    }

    /**
     * 从列表中删除所有元素。
     */
    public void clear() {
        modCount++;

        // 把数组中所有的元素的值设为null
        for (int i = 0; i < size; i++)
            elementData[i] = null;

        size = 0;
    }

    /**
     * 按指定集合的Iterator返回的顺序将指定集合中的所有元素追加到此列表的末尾。
     */
    public boolean addAll(Collection<? extends E> c) {
        Object[] a = c.toArray();
        int numNew = a.length;
        ensureCapacityInternal(size + numNew);  // Increments modCount
        System.arraycopy(a, 0, elementData, size, numNew);
        size += numNew;
        return numNew != 0;
    }

    /**
     * 将指定集合中的所有元素插入到此列表中，从指定的位置开始。
     */
    public boolean addAll(int index, Collection<? extends E> c) {
        rangeCheckForAdd(index);

        Object[] a = c.toArray();
        int numNew = a.length;
        ensureCapacityInternal(size + numNew);  // Increments modCount

        int numMoved = size - index;
        if (numMoved > 0)
            System.arraycopy(elementData, index, elementData, index + numNew,
                             numMoved);

        System.arraycopy(a, 0, elementData, index, numNew);
        size += numNew;
        return numNew != 0;
    }

    /**
     * 从此列表中删除所有索引为fromIndex （含）和toIndex之间的元素。
     * 将任何后续元素移动到左侧（减少其索引）。
     */
    protected void removeRange(int fromIndex, int toIndex) {
        modCount++;
        int numMoved = size - toIndex;
        System.arraycopy(elementData, toIndex, elementData, fromIndex,
                         numMoved);

        // clear to let GC do its work
        int newSize = size - (toIndex-fromIndex);
        for (int i = newSize; i < size; i++) {
            elementData[i] = null;
        }
        size = newSize;
    }

    /**
     * 检查给定的索引是否在范围内。
     */
    private void rangeCheck(int index) {
        if (index >= size)
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    /**
     * add和addAll使用的rangeCheck的一个版本
     */
    private void rangeCheckForAdd(int index) {
        if (index > size || index < 0)
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
    }

    /**
     * 返回IndexOutOfBoundsException细节信息
     */
    private String outOfBoundsMsg(int index) {
        return "Index: "+index+", Size: "+size;
    }

    /**
     * 从此列表中删除指定集合中包含的所有元素。
     */
    public boolean removeAll(Collection<?> c) {
        Objects.requireNonNull(c);
        // 如果此列表被修改则返回true
        return batchRemove(c, false);
    }

    /**
     * 仅保留此列表中包含在指定集合中的元素。
     * 换句话说，从此列表中删除其中不包含在指定集合中的所有元素。
     */
    public boolean retainAll(Collection<?> c) {
        Objects.requireNonNull(c);
        return batchRemove(c, true);
    }


    /**
     * 从列表中的指定位置开始，返回列表中的元素（按正确顺序）的列表迭代器。
     * 指定的索引表示初始调用将返回的第一个元素为next 。初始调用previous将返回指定索引减1的元素。
     * 返回的列表迭代器是fail-fast 。
     */
    public ListIterator<E> listIterator(int index) {
        if (index < 0 || index > size)
            throw new IndexOutOfBoundsException("Index: "+index);
        return new ListItr(index);
    }

    /**
     * 返回列表中的列表迭代器（按适当的顺序）。
     * 返回的列表迭代器是fail-fast 。
     */
    public ListIterator<E> listIterator() {
        return new ListItr(0);
    }

    /**
     * 以正确的顺序返回该列表中的元素的迭代器。
     * 返回的迭代器是fail-fast 。
     */
    public Iterator<E> iterator() {
        return new Itr();
    }
```

## 三、常用方法分析
### 1. get方法
```java
@SuppressWarnings("unchecked")
E elementData(int index) {
    return (E) elementData[index];
}
 
/**
 * Returns the element at the specified position in this list.
 *
 * @param  index index of the element to return
 * @return the element at the specified position in this list
 * @throws IndexOutOfBoundsException {@inheritDoc}
 */
public E get(int index) {   // 根据索引获取元素
    rangeCheck(index);  // 校验索引是否越界
 
    return elementData(index);  // 直接根据index返回对应位置的元素（底层elementData是个数组）
}
```
由于底层是数组实现的，先检查下索引是否越界，然后直接返回对应索引位置的元素即可。

### 2. set方法
```java
/**
 * Replaces the element at the specified position in this list with
 * the specified element.
 *
 * @param index index of the element to replace
 * @param element element to be stored at the specified position
 * @return the element previously at the specified position
 * @throws IndexOutOfBoundsException {@inheritDoc}
 */
public E set(int index, E element) { // 用指定的元素（element）替换指定位置（index）的元素
    rangeCheck(index); // 校验索引是否越界

    E oldValue = elementData(index); // 根据index获取指定位置的元素
    elementData[index] = element; // 用传入的element替换index位置的元素
    return oldValue; // 返回index位置原来的元素
}

/**
 * Checks if the given index is in range.  If not, throws an appropriate
 * runtime exception.  This method does *not* check if the index is
 * negative: It is always used immediately prior to an array access,
 * which throws an ArrayIndexOutOfBoundsException if index is negative.
 */
private void rangeCheck(int index) { // 校验索引是否越界，越界直接抛出异常
    if (index >= size)
        throw new IndexOutOfBoundsException(outOfBoundsMsg(index));
}
```
1. 校验索引是否越界
2. 根据`index`获取指定位置的元素
3. 用传入的`element`替换`index`位置的元素
4. 返回`index`位置原来的元素

### 3. add方法
```java
/**
 * Appends the specified element to the end of this list.
 *
 * @param e element to be appended to this list
 * @return <tt>true</tt> (as specified by {@link Collection#add})
 */
public boolean add(E e) { // 增加一个元素
    ensureCapacityInternal(size + 1);  // Increments modCount!! // 将modCount+1，并校验添加元素后是否需要扩容
    elementData[size++] = e; // 在数组尾部添加元素，并将size+1
    return true;
}

/**
 * Inserts the specified element at the specified position in this
 * list. Shifts the element currently at that position (if any) and
 * any subsequent elements to the right (adds one to their indices).
 *
 * @param index index at which the specified element is to be inserted
 * @param element element to be inserted
 * @throws IndexOutOfBoundsException {@inheritDoc}
 */
public void add(int index, E element) { // 将指定的元素（element）插入此列表中的指定位置（index）。将index位置及后面的所有元素（如果有的话）向右移动一个位置
    rangeCheckForAdd(index); // 校验索引是否越界

    ensureCapacityInternal(size + 1);  // Increments modCount!! // 将modCount+1，并校验添加元素后是否需要扩容
    System.arraycopy(elementData, index, elementData, index + 1,
                     size - index); // 将index位置及之后的所有元素向右移动一个位置（为要添加的元素腾出1个位置）
    elementData[index] = element; // index位置设置为element元素
    size++; // 元素数量+1
}
```
#### add(E e)：
1. 调用`ensureCapacityInternal()`方法，将`modCount+1`，并校验添加元素后是否需要扩容。
2. 在`elementData`数组尾部添加元素即可（`size`位置）。

#### add(int index, E element)：
1. 检查索引是否越界，再调用`ensureCapacityInternal()`方法，将`modCount+1`，并校验添加元素后是否需要扩容。
2. 将`index`位置及之后的所有元素向右移动一个位置（为要添加的元素腾出1个位置）。
3. 将`index`位置设置为`element`元素，将`size+1`

**`add(int index, E element)`的过程如下图所示**  
<center>

![image](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAtwAAAEeCAYAAAC5YcJLAAAAAXNSR0IArs4c6QAADMV0RVh0bXhmaWxlACUzQ214ZmlsZSUyMGhvc3QlM0QlMjJhcHAuZGlhZ3JhbXMubmV0JTIyJTIwbW9kaWZpZWQlM0QlMjIyMDIyLTAxLTE1VDExJTNBMDglM0EwNy4wNDdaJTIyJTIwYWdlbnQlM0QlMjI1LjAlMjAoV2luZG93cyUyME5UJTIwMTAuMCUzQiUyMFdpbjY0JTNCJTIweDY0KSUyMEFwcGxlV2ViS2l0JTJGNTM3LjM2JTIwKEtIVE1MJTJDJTIwbGlrZSUyMEdlY2tvKSUyMENocm9tZSUyRjk3LjAuNDY5Mi43MSUyMFNhZmFyaSUyRjUzNy4zNiUyMiUyMGV0YWclM0QlMjJleUdObGY1dlFWRVo1cTRPYU00ViUyMiUyMHZlcnNpb24lM0QlMjIxNi4yLjclMjIlMjB0eXBlJTNEJTIyZGV2aWNlJTIyJTNFJTNDZGlhZ3JhbSUyMGlkJTNEJTIyTnNzaXBEQzhHNFlqTF9wbzh2TDIlMjIlMjBuYW1lJTNEJTIyUGFnZS0xJTIyJTNFN1YxZGI2TTRGUDAxbG5ZZlpvWDVDanhDUG1ha25WbFZxbGI3ekFTU29DRWhROGkwblYlMkIlMkZOcGdrY0VtYk5uRjhTYWdxRlF3WU9PZlljQSUyRjJMVEdHeSUyQmZQV2JCZWZFdkRLQ0c2Rmo0VFkwUjBuV3FHdyUyRjd3a3BleXhCcTRaY0U4aThPeVNOc1hQTWElMkZvJTJCcElVYnFOdzJnanlzcWlQRTJUUEY3WEM2ZnBhaFZOODFwWmtHWHBVMzIzV1pxRXRZSjFNSTlBd2VNMFNHRHBmM0dZTDhwU1J4JTJGc3k3OUU4WHhSblpuYTR2NiUyQkI5TWY4eXpkcnNUNWlHNU1pcDl5OHpLbzZoSTN1bGtFWWZwMFVHU01pVEhNMGpRdmw1YlB3eWpoMk5aaG14elp1cnZ1TEZybHRSUDlpamZ4OSUyQnIyWHE5azQlMkY0Mkp2OThwbjh2clllSFNVYXo1WVB6U2RUOEswaTJvaEpQM0VIJTJCVWxYN3RJano2SEVkVFBuNkUxTUdNZnhGdmt6WUdtV0x3V1pkY2pXTG55TjJMbiUyQldydkpIY1RpdDFrc3RVSk90YjM1RSUyQlhRaE5oYWc4c05HR2xzVFZ4TmxlZlI4OU5icERsQW0xQ2hkUm5uMnduYXBEakFGTkMlMkJOOWFjOTQ0WW9XaHlRWFpVRlFtUHpYYzE3VE5tQ2dQVWRFT3NBWXIlMkZyRUElMkJRUVd3QWlJY2RoMWpYa0VGc0FvakhYWWZZUUFheEJTQ2VkQjFpR3huRU5vRDRjOWNoZHBGQlBBQVFkeHhoUTBlR3NITnpDRnZJRUhadkRtRUhHY0pWUkhoSmlPVkNhRkpzRU1MWURUdUUyRUl6Q21NejdCQmlDNzNzTzNBUVhOVVkzNEdGb0J6ak8lMkZBUWxHTU1UWVN1UTl6MEVKUkRERTBFJTJCVDROWHglMkJtU1pvVjFSdVRpY1olMkJybTh1S01jZXVndnlEUnhGMkRkZEIlMkJYWVE5dEJ2ck9qQm52Z1J5akglMkZ2WU5DZVVRMzc0am9Scmk2b1cwUTdGZzA1RlFEbUgzSFFubEVIYmZrVkFPSVl6a2JzMlIwQWVxTVlhUjNLMDVFdW94aHFIY3JUa1M2akdHSWR0SU9zYUtRallERyUyRll3Wk92OGtCSWJHOFl3Tk92OG1CSVhHOFl3TnV2Nm9KS214YUFjNHlwWXZLSDQxOElHc1lUZ0RaZkZvQjdpN2dWM0ZCdUVNTGpERGlHMjJNMlI4Qlh1dWhhRGVnaGhhRWJHTm5FbXhHVUxGbUhiUFl1TUo4UWZFdGZqSmU2UWVBNFpENGh2RXElMkZZaDIlMkJ5akxiRGlnVW1kTEUzdXdrN3lVWHZTZmprbUNwMHNIOXUlMkJZUVNCckV4bXhWQnhFSFJBWjFWSWElMkZnMDZib2Z6MjJBN1hYejhXdSUyQjRQc09mODdxczdJd0NsUFdwYUxPM0tHeFRXT2lHOWMlMkZkS0NNUHlEblhXNDMzSlF5WiUyRkhycnNwYnliRnZLSG9KSjZ2MlBLVVNUSml0JTJCQnp3Y2JUSVBIRWhtVWNodnh3UDR2WVpRYmxuQnV1NzNVYXIlMkZKQ1lKWlByQkd2YTV1bkclMkZHVTQyMGp6OUlmVVJYd3JkSVZyMlVXSjBtejZPRGhhRiUyRmRVcUphVzV0cWFWUzZ0RVlGWSUyRkZUNUtWcFRYbFZZbVVhSFJOM3dwdVl5OXFiVmpRb24lMkZEJTJCNzRaa29zWk5zTUJvU0F2SXg3Nm1ldHkyTDJSbnFvZjlPa1ZYclJFbVR0QjVrN0ZKV1BmRE9rSyUyQmFVUzhjWEhVaERobGw2OXglMkZZMWQ0bzZLb3diOFVjREVCJTJGdDNYcyUyQlk3OGFVNnJFSEJSV0h1JTJGU2duZ0h4Q3ZueXd6MzJNS0hGWVE3eHZKYnI2QVYlMkJjWUc3VU9ER1ZSVyUyQjY2RXZLWEc3a00xTzRreE9ySVJ5SWZxSGF0TmVsYSUyRkZKZXY1QjY4d2JHZSUyRmFBODIzOEVabk5SNGV0RmVXclQ2QUlwMjklMkZKOEpkR2VZQ3RFcTlEanM3czVoVW13MmNUVE9yOTFuRDVrcDVmbmpFSXdQJTJGeE5hQSUyQmdzMXFRcThxeUtBbnklMkJGZTklMkJqWTR4UmtldVBMSWNYZmViREN5U2JmWk5CSkg3VWtCRlpsdlZaUUgyVHpLUVVVRnU3dmJQb2Z3RnBQalF3ODRLQlBHM3RmZ2U1VElhJTJGMkgydEtndGtSWCUyQnJGbUxKSWFCSTNwJTJCalVOdnRhR2pyWjY3UyUyQjlTc3dnU0slMkZtbko4cHlrJTJGVWJhMjJxaUdkelRhUkhCVzF6TXo0ZDVYSGVjSncxcld2d1F0akdxQ24xVnZHYVNkU01Wb2c0U3IyZHprbEtvV0YwU3pZRnMlMkZBY3g4VHI0RjZla2hvVVBqS2MwMmJoVklWd3d5UWt0TWNacU9lSEJYakUzQ1NBMlphcUNjSG1pbnlQNjRqSmFjNVIwTTlPWERrZyUyRnl2OGtqSmFVN2lVRThPSERJaCUyRjNNJTJCVW5LYXN6elVrNk5nSER4T2JzQXNFT1hjN0ZLUzlkdzBwNCUyQm81MGJCNEE2azNEVG5uYWpucHNVd09aY2JuTmlEQ1N2cXNaY3duQVFwOXVpQ2UxM0NPQlNrMktPTDNYVVl1OSUyQnQ2MlVNYXVUb3BxT2FIQmk3MzYzclphTWpCOGJ1OSUyQnA2VVJjZE9RcG1vdVBrUnRmUmNRTkRkM1daU1pDU1ptRWp6WUF4dmJxVUpraEpjOUNSQm9OOWRibFFjSkptVUhTa1NYQUJ1dm5vTWt4MDNFaHdDVHJLelFBZE4lMkZmakltam9zRyUyQlpCbk9qMktNekNZeTIyUkszaVQwNkQ4Q0FIa0R2bmduUWRlWGtRQSUyQmdkOCUyRlFrQU5OZ040OXcwS09DWVA5a1hSeXVoVTNObTAxQktUQllQOXVCJTJGcFo2TWlCUWYzZER2UnowSkVEbyUyRnA3SGVqWHRNTVFrS01nVlR4U2JreDAzRWdJJTJCenZLelFBZE4lMkZkakMyam9zSmZ3ciUyQiUyQlFZbzh1NmpjbGZQbEhpajI2b041c0daVGZaMFBxc3lGZE5LRUN6c1lJQmc5V2cxcVZaVkdpRm5SeCUyQmpSS0gwJTJGWWdWTjNJRHROOVRsSVZmb2xhclhOTU9uekwlMkZVdDQ5b3RvJTJGbVYzREpnajN6bHBnRmR3RDV2VXk5MkNXSTNEQ2oySyUyQmQ3c2s0WUt5VW4zOVA3S0NvdjZ0V0VVTyUyQmo1RXA1b3ByanVsMm5Yc1hKZWFMZXFraDJuaWlyeGVIdDgwU1JjJTJGSkVsVzN2YUc5eGkzbWlyQlA4enMwaVdQUEY2VFpMWHZ5TTlSQVI3dzdlc0lQMmJCViUyQmRCS3Z2NGpsOTNVMHAwb2xTM1BHUWNxRjZNcE9pS0xYbTc0TkhTUzk3YUZCOWVQS09QT3BjZG5zcmVKRllOQyUyRm1xajczbHZsN3FwZVRWem9qRlNOdHlZeWFScXoyNHlSdnF0NGc4VjZ6JTJCNmMxbE5RUjlyN3BYMVpuMEcwUzd2dktkVDFGRnE5cDZDT0s2dW5ZS3RaeXZuZnY0T3d4cno0bG9iOFpYSDhQdyUzRCUzRCUzQyUyRmRpYWdyYW0lM0UlM0MlMkZteGZpbGUlM0XjirWFAAAgAElEQVR4XuydBbRexfX2JzgheHB3K4Xi7l4KBYq7u0OB4lpcghUJ7gX+QLFA0eAEKFICBA0aCBIIFiTf+g3fvp177pF55c57782z1zrrvHLOyDNzzjx7z549vUaPHj3aBdKrVy831lhjufHGG8+NPfbYbsIJJ/TnX375xf+G/PDDD27cccf1v/3000/u559/bjt+/fVXfz3pIJNOOqn78ssvwywcWVq2mezbrrP7yf/HH3/0ZbLfyIO8+Y1ycIwzzjj+sLy5lrS51q4Py8n9/M41XMt9YVqWJr9b3paepUPd7eA3S88qQbpWZvuNNDbffHN33XXX+XQnmGAC17t3b48zx/jjj+/rwXWkTd2//fZbj/l3333nceZ6O6aYYgr/O9eNGjWq7eA6fkOoa4i5tbHhZecQ47Cu5E3dEPoAZTR8rF/kYWw4GS5h+mHbUW/q06dPH/fhhx+6RRZZxH/mmHjiid0kk0zi6zLjjDP66wwjS4/yjRw50g0bNszf/95777mhQ4e6Tz/91P9u5aastCeYI9ZnwIP6IGG/AU9w4Ewe3M91YEDeCP9bX+Ic9itLz/DmTNmt74Z9grJQR/4DN76TzxxzzOHrYu1n/dnO1k6cuW6mmWbydbC6ZdvWymv50Mf4DVw4rE6UAQGr6aabzn3xxRftniWra9i3wMTKTT0pv71HSDvsU+RruHLmO/fb8xiWv+j5s2curG/4DFud7BnM1j18H/CZukw++eRuxIgRbX0hfKatb7R7mWW+gBftSN7hO2maaaZxX3/9tX9WJ5tsMt9Gdljbch+/he8XK1eIM30RfCVCQAgIASHQfRDoFRJuBj0GyOeff94NGTLE3XXXXW6uuebyA+N///tfN+ecc/oB8a233nLzzz+/J4gTTTSRJ0QMyMsss4ybaqqp/GDAweDD9XwOBxgbAO23jz/+2BOFZ5991g9GEEwGHyONNgAx6BghYED75ptv/AD2/fffe0Jk5N9IvJE66mSkDgJHHgysTz31lNtll1183ahPM+Srr75qI8mUzYgaaVMesIBEUQ7wXXvttWvKFgyszpz/85//uLnnnrsDwQoJi5EucO3bt69XgCCiVj7D2kh1iJsRYdqYz/UI+dBP6FMQD1MOXn/9df87fYcycX7sscfcDDPM4MAR4sOZgzJ99tlnbQoFbT377LO7l19+2RcJXMGU/jfzzDO7+eabz0055ZTu8MMPdy+99JInjQh9hXy5jrbheOKJJ9xCCy3kCVd4QODpJ/Yb5f7ggw+8ImBkzvoW9UC5RAEC21VWWcW98MILvgwQLepihNieD1NeOIPRtNNO20ZS68H5888/9+1LvpQZTMk7fJ5oY7Ck/FZ2U6R5bqxfUB4+2zNG3bnXlAYwoG7gSlvsuOOOvm1Mcamn/LQ/5f3kk0+88kT5reymLFk7U0/aYtddd/Xtx/uDa8P3AWXmMKXY2tEIbqh4mqJAf6DNaU/a0t4bfKf/c88777zj34Wvvvqqm3feedtVFQw6iwxTP55D3pMopRIhIASEgBDoPgi0I9xGjBodOGutPqRxscUWc88995wnPqnk73//u/vb3/7mifeSSy6ZKlufDwP8pZde6rbbbrtk+WL5nXXWWTtYWDu7ABAnyMvTTz/tllhiiaZnB6HKI3o333yz23777d2//vUvt9JKKzU936IE+/Xr5/bdd1/3wAMPeOKdSt544w1PAFFgUWxSyQ033OBnbXh/QFBTyRlnnOEOOuggd++997o111wzVbbu0Ucf9f3p7rvvdmuttVayfJmxQZm8+uqr3cYbb5wsX2UkBISAEBACjSPQjnBjhcP6m3rK8v7773d/+tOf3L///W+33HLLNV6ryBT22GMP949//MPdd999brXVVou8qzmXYf0/6aST3AEHHNCcBCNSwdKLQsOMgbkPRNzW8CVYK7He3nHHHb6dU8mZZ57pTjnlFAcB3nTTTVNl64wIQoy22mqrZPli6V1++eXd+++/76affvpk+R555JHuxBNP9FZ8ZhlSyW677eYuueQSd8UVV7itt946Vbbuxhtv9AoG7w5myFIJlvWFF17YHXfccV6hkwgBISAEhED3QaAd4WbKHssYU5cpLVVYyHbeeWd300031exi0QjUf/nLX9ytt97qieC6667bSFI138sUNda5Y489tuZ7670Bdw0IGRZhLOypBIsrBPDKK69022yzTapsfV4DBw50Bx98sEO5SiUHHnigO/vss91pp52WVKHCkv/nP//Zu67glpNKINwnnHCCw6WFmYxUgvKGdRvFau+9906VrTv//PPdPvvs42fHjj/++GT54j61+uqr+3dlynyTVVAZCQEhIAR6MALtCPczzzzjll56ae9HCSFMJVh6sQpedNFFDhKcSlZeeWVPyG655Ra3/vrrp8rW54O/70477eTrnUqYAkexwK+1EV/bWsv70UcfeQJ4+umnO8hoKsGdBDeWLbfc0vtyp5LNNtvM96m//vWv3vKbSlBo8KV+9913/QLTVLLffvu5c845x7uyMJORSpZaain34osvuqOPPtodeuihqbL1bUqeKHSXXXZZsnz79+/vcIPjGUahkwgBISAEhED3QaAd4cZCxWKy1FPDDNYnn3yyP7bddttk6LHw6JVXXnH//Oc/kxNuFn1tsskm7oILLkhWX2YS8BkfPny4X/iXSoxwQxh22GGHVNm6DTbYwJNP/HvpW6lkxRVX9ESfuqZsX54jZk1wPUhJuFEcIZ6DBw9288wz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ECGbpQBLSCx1gRwROcEILekx7c1/RniyCkpW8TIihysG1j4jt4Y1ZaJfQNzoh3ynfSgDC8nwh+cz5WeGhnbnXpuV4VprT8oHFrQ/bWvtCwbW3vQ7yxussGaG5MoUSnDgmH766X270x/NVSiLI32vSPloVj8w8mpnYoLj0kN57ZltxgxHWF7ww8JNv+LgWQIz+oVZgGkHMOda62M8A7hmEHHEFCI7U1Zw5ZmxM+XGmk4ahCIEX9qQdC1te3/Rlmy6xL20qbU5fZ78SSNsf55Tym4zLJzp7zy79EfaFRyxsmNppq93plBG+luotHV23+nM+ihtISAEhMCYjEAHwj0mg6G6CwEhkA4BsxKny1E5CQEhIASEgBBoDQIi3K3BXbkKASEgBISAEBACQkAIjCEIiHCPIQ2tagoBISAEhIAQEAJCQAi0BgER7tbgrlyFgBAQAkJACAgBISAExhAERLjHkIZWNYWAEBACQkAICAEhIARag0Ab4WYBE1FAHnroodaURLkKgSYjYGEhLdJDk5NXckJACAgBISAEhIAQiEKgHeGGmBAijrBvEiHQ3REgbBsxwAkfJxECQkAICAEhIASEQKsQaCPcxKglZjRxa+ebb75WlUf5CoGmIUCs+LvuusutvvrqTUtTCQkBISAEhIAQEAJCoFYE2gg3m0Gw9feQIUP8FugSIdDdEWADlf79+7stttiiu1dF5RcCQkAICAEhIAS6MQJthPvRRx916623nt/pkR3zJEKguyMgC3d3b0GVXwgIASEgBIRAz0CgjXCzhTVbcLNVcmdtOd4zIFMtugMCbIsN4WZ7c84SISAEhIAQEAJCQAi0CoF2YQEnnnhid+SRR7q//vWvrSqP8hUCTUFgjTXWcK+99pobOnRoU9JTIkJACAgBISAEhIAQqBeBdoR7k002cQ8//LD79NNP601P9wmBliJw0003ucMPP9x98MEH7pxzzutQPPEAACAASURBVHG77LJLS8ujzIWAEBACQkAICAEh0I5wjxo1yk033XRu9tlndzfccIObY445hJAQ6NII/Prrr27AgAHu7LPPdk8++aQjFOAUU0zhNt54Y3f88cd36bKrcEJACAgBISAEhMCYgUCHnSaxcLN4EvK90EILufXXX9+tsMIKbs4553S4nCATTTSRY6McpJZz0bXffvutT5s44PiPd9eNSj7++GP3zDPPuOeee8698sor7q233vKzBfjFEwFmmWWWcbvttptbeOGF23rXf//7Xzd8+HD3/fffeyzxowdfYqGDCcfIkSPbDrCy47vvvnN2cD+ff/jhB58WZw58mO2gTTnwb7YD333KZwcElnLYweYxCO1ibUP7UIa+ffu6ccYZx5eZwz7H/jb++OO73r17dziILlL0O+Xs06ePO/nkk92tt97qXn/9dV+uqaaayvdXMN5ggw3cAgssMGY8waqlEBACQkAICAEh0OURyN3a/ZNPPnHnn3++e+CBB9w777zjN8OBqEHGIGBGnK12Rsr4bp85h4eRtrxr5plnHh8dJSR9kLrsERI++2/mmWd2EF0jhOHZ8uc3LJ8QUIR8ECOXnKkf1/G56DAMuB+iGl5nmEAiIX+EVpxyyindLLPM4l588UU36aSTuvfff99/BleI+CmnnOK/cx31MRIMQeYz+VAHq7cRWRYBko8d1I0Domqfs+fweu7nCAkyn0PsyN8UKupmdbW6f/TRR14pCMk7n7OE3r5nz1ZHzqYIlCkDlj948BnMINfbb7+9J9gSISAEhIAQEAJCQAh0VQRyCXdZYbGeQrqwukIaP/vsM38Qx/uLL77wx5dffulGjBjhj6+//tqxqY5ZabHCGgGGFEIEIX9mITUibcQ8j+xBdjkgeBA2CJj9ZhZb7odEcpjFnLzsOxZUy58zAinmGvs9+xnCvMgii3iiyUG9sKSyYRD3TjbZZN53mOs4v/TSS54YorQsueSS7vnnn3f9+vXz14EHZV9iiSXcggsu6Oaaay4344wzeov2sGHD3GqrreYtueCVtWiHFuzQil1kwTZsspZsI7GhRdsUhzwlinYLlRhTBLKKkGFs+IfWb7OGG+kPz6FSkFUmQqXCrNxd9aFSuYSAEBACQkAICAEhECJQM+FuBnwQw9DlwSyboXuDkUAj3qGVN+u6kPe9q4Y2vPLKK912223nDjvsMHfSSSc1A06lIQSEgBAQAkJACAgBIdCFEWgJ4e7CeHR60fA9hmwzI8DiPokQEAJCQAgIASEgBIRAz0ZAhDtx+55xxhnuoIMOcoMGDXKLLrpo4tyVnRAQAkJACAgBISAEhEBqBES4EyP+1FNPuaWXXtpddtllfsGfRAgIASEgBISAEBACQqBnIyDCnbh9CRu41FJLedL9+OOPJ85d2QkBISAEhIAQEAJCQAikRkCEOzHiLBAlzjbROYg+IhECQkAICAEhIASEgBDo2QiIcCdu31VXXdU9+OCDfiOhIUOGJM5d2QkBISAEhIAQEAJCQAikRkCEOzHixAQn/vVVV13ltt5668S5KzshIASEgBAQAkJACAiB1AiIcCdE/Pjjj3fHHHOMm3322WXdToi7shICQkAICAEhIASEQCsREOFOiD67U6655pp+S/L9998/Yc7KSggIASEgBISAEBACQqBVCIhwJ0T+jjvucFNPPbWPUiIRAkJACAgBISAEhIAQGDMQEOEeM9pZtRQCQkAICAEhIASEgBBoEQIi3C0CXtkKASEgBISAEBACQkAIjBkIiHCPGe2sWgoBISAEhIAQEAJCQAi0CAER7iYBf+2117qBAwe6s846y0044YRNSjUuGXasXG655douvuaaa9yWW24Zd7OuEgJCQAgIASEgBISAEOhUBES4OxXezk/cyPZjjz3mll12Wff666+7TTfd1B188MEi3Z0Pv3IQAkJACAgBISAEhEAlAiLclRB13Qu+//57H15w+eWXb0euW2lt77poqWRCQAgIASEgBISAEGgNAiLckbgbub3ooova7jCrMj+EJPfWW291W221VYeUF1poIXfjjTe6eeaZx//HRjhHHXWU/5z9L6ZYWLP32Wcf169fv7Y0Y+7TNUJACAgBISAEhIAQEALpEBDhjsDayPYMM8zgjjzySH8Hrhx77rlnG4Eusyp//vnn3gKNy4fdD9kmDe6bcsop/Wf8sI3Eh2Q8W0Q2z+G+1157zZN2CDfEe8CAAf5S+XBHNKouEQJCQAgIASEgBIRAIgREuCOANsK89dZbF/pFlxFuSPGHH37YtqDS/KzPP/98T8JNstdVFY08saQbAYe4y4e7CjX9LwSEgBAQAkJACAiBtAiIcEfibRbnXXfdNTcSSRHh5vfTTjutnSsJv1199dVt1m0rAlZu8jGrd1XR8tLmnqL0q9LT/0JACAgBISAEhIAQEALNR0CEuwZMzaJstxx33HFtLiJ5hLvIkp1NJyxCaK2uKloZcQ/dXarS0f9CQAgIASEgBISAEBACnYeACHed2BppNn/pLOHO89u2rGIs0LX4cGct4ln/8jqrqNuEgBAQAkJACAgBISAEmoCACHcDIEKKERZCZgl3mT92ESGuNZyfkXryD33BYwh9A9XWrUJA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l56YB87aaMMNN/SuJE899ZT3K7/gggtcv3793E033eT69OnTbhFxu5mQMDoIGRLqj50gw90eY2Jsx1xTRGKzccAh4GH861jym03HAMxu7V4FbGwIw6p09L8QEAJCQAgIgS6GQEOEuyrusrkBVFlN80g3vzUzVKCR42wklbL2CH2xzYc4dG3II2zmFpEN25cXq7rI1zsmSkleuctcSorq2aw2svqRT2h1D/PN2ywmJKEhduecc46beeaZ/cLIkNzimw6pJUJIWWSYmOes0ZmNiy66yGcT1oE2ePDBB/3v2djtMWXqlGvq9YuGAF9/vXN7790pxeqQqHaaTIOzchECQkAICIHkCFQS7rwIHzGWQbNKWgSNWrdSL7KU1otQvQszwygtZlUNiWOepdlI52mnnRYdCjBLTGsha61uIyy74BC6vNTaTllrd7jNe55iEtMHq8pQFkmn7N6YmYB6laaqMtf9v22pbi4sMQlBgN96K3+r95j7a7km3Dpeu0zWgpyuFQJCQAgIgW6AQCXh7gZ1UBGFgBCoQgBrNZvknH56XLQQ0stuvV6VRyP/4+/9xhvl2883kr7uFQJCQAgIASHQQgREuFsIvrIWAkJACAgBISAEhIAQ6PkIiHD3/DZWDYWAEBACQkAICAEhIARaiIAIdwvBV9ZCQAgIASEgBISAEBACPR+Bugj3N99847799ltHxIgffvjBjRo1yp9//fVXj9g444zjxh9/fDfRRBO5SSaZxLH5ydhjj93z0VQNhYAQEAJCQAgIASEgBIRABgFPuH/55Rf35ptvunfeecdvUEIUho8//tgNGzbMvf/++55MjxgxwhnRnmCCCdy4447r7AzBhlD36tXLjR492v3888/up59+8kQcUs558sknd1NPPbWbccYZ/e6Liy66qFtttdX8b1zL8dlnn7npp5/ek/XOJuiUMXuAw/Dhw72SQD3CA2WC7ygahKrL+//tt9928803n8dmvPHG8+fsZ7Dk+PHHH/05/E4s54UXXtjjmD3GGmss/9vgwYPdAgss4JvRcDO87fu7777rFltsMde3b19/TDHFFO7DDz90H330kW9TcP7iiy/cl19+6XcIHTlypG8nykRbkZ7Vl3xpC9qYOnHQ7mDQu3dvH2uaY9JJJ/UHeXFMNdVUvh1Jy9KmfOBmdSMNruE83XTTNe3hJI8PPvjA15X2pK70XepJtBrqSVlob+rJbyiH1NPqypm2++STTxwx1imj1RXcfve737mJJ57Y14W6WluTB32Ec/iZ3+gf9C1rr7Dd7DP5cY31C8pJGcmHMoEX5eB5ArPZZpvN/f73v/fPUa1CW4MN/YHn3PCifoYV5SJv2p360p9mmGEGN8ccc7j555/f/27PkfUZysE99B36DdhQbn5rhtC+tCvvqa+++qrdu4l25neusb5M/Uzpt37Mb3PPPbdvV9qe8xtvvOFWXHFF37+LjmaUvywN+iJ4ZZ//zs5X6QsBISAEhEDnIuAJt73cGSAZaBisGEgZJDlDrEKSxW8MrgzARsjCM4OakW9IDQMfAyODO4MhZwi8DeZ2L0SNwZ7fERukIXJ8NlJjxMjKzbWUmTJxkKcRWiORlMFIFteGpID8s+W334zoGIHgPiO/WQIBScoSYSOvWTISDqhhemGaWVJv30MynJeO4cD5lFNO8eH6jPxYO0LaIBq0YUgujFSTLiTFcAU7I4EQaJvh4GyfIQs240G9Dee8Lkw+tInVNyTihn0RLmF7h+1un7Ntawqhnek/YfvSX/iexRf8qDfCNUbQOdu1VharI/UxUkefNbwhdOQB5lYv66uGLbjynHBGuJb7wcoUUHuewv7Nb1ZnrqNs1p+t3xrOlqc9Y1Y+0kAZ5lknP+qAcJ0pztbWnGlry9fyDtvZnv8Qn7AsIf58DiWr6Fp/D5+h8DlEQYFoUx7yQPlAkbT3BHWiDibWL6mb1cHIOf+Z8YC0rM3Dd8Zkk03m+znCZ9qJPOw9acq2tRnlNhxpN7CjjU0R5TdTAmkP8M0+O/QRa5POHRKUuhAQAkJACHQGAm2E+5FHHnErrLBCZ+SRmybW3KWXXtrdc889flB777333NChQ71lMrTGMvgwqBlBZEBi4LFB2gYyBkCzLELmuQfL47TTTuut5rPMMou3yjEobrXVVj4vrjNLL0Sf7wzUZg1lQDQSmbWKGskILXikbW405I8CweA/zTTTeAvakksu6e6//363xBJLeALAIBpaB/MshEaULR8GcwSSESNgy72vvfaaJ2/U0Q4smkYqKY8dlIt2oC4heQvrapZp6mVWQq7noK2wpq+zzjpt1tm8shp5JF/wpU2wrBrpNGXJFCVLw8ikWU6pF3miPFBerJSkyf+p5P/+7/8cu04+99xznoyBrVlgzVpMmcCb8tsMkc0OoNzQV7BaQ3zBNEaYiaJ/v/zyyx77Tz/91D9P9GP673//+1//v81+UIbQis+19EH6JVvTI+GMhhFya1swpu8xG7buuut6qzDltX6cVUxCskx7mrJmMyt5SlqotJC/5QlG//znP70Sac8j9QJrrO6m1MTgVnQN6dl74IUXXnCLLLKIx5X6LrXUUu6yyy7zbUeer7zyin/n0M7cw2fa3mYlTCmwWS57TsCPGQreD3ambryvOEIljXcK17z11lt+IyWJEBACQkAIdE8EPOGGANxxxx1+AE0lEBQ2xTELYlG+DMxGhiHCZhUyyxSDGAOUWWsZnBi8slYzS//f//63W2ONNdpcQ1LVF1cdXBOuuOIKty3xkBMJBAtyjDsD7gep5N5773Vrr722J39FbdEZZXn11Ve9yw0klz6RStixk42OXnzxxaTE6D//+Y/7wx/+4J5//nl/TiW4LdGfcEVDkU0lG220kbvzzjs94U4pN954o9t8883dueee6/bcc8+UWfvn56GHHvKKpEQICAEhIAS6JwKecGO5ZJvszTbbLFkt/vGPf7j999/fW5BTylVXXeW23357b0XFcpZKnnnmGW/hPvHEE93f/va3VNl6ixtWMiyRc845Z7J8r7zySrfddtslJ9yPPvqoJyYoacwypBJmTR544AGHosHOmKkEBXL11Vd3AwYM8IpkSsESjmUdX+5UwhoHrM1YlFMKVvXDDjvMHXjggV6xSikYESD69DGJEBACQkAIdE8EPOFmyvPCCy90O+20U7JasPX1GWec4YlvSsGf+ayzzvIuLExDpxIjRvvuu687++yzU2Xr3WPwgccSmXJK+vTTT/e+47gadPYC2BBM+vEee+zhXSuYnk8lK6+8sneFuvzyy92yyy6bKltnlle2qccCm1JQ1J944gnvIpVKcI9BcFlKKSjJJ598sttiiy28cSKl4EZ20kknuYMOOihltspLCAgBISAEmoiAJ9y4ZGDBgQymkrXWWsvhx52acEN2IYK4WMw000ypqutuu+02t8EGG7itt97aYWVPJUa4UTBS1veQQw5xp556qncZSrnY64ILLvBT/hCyZkY+qWqvBRdc0C82hJRhcU4lF110kVcwzjnnHLfXXnulytbng6KORX/VVVdNli+zUrQrMzYpZdddd3X9+/d3a665prvrrrtSZu3XJ5A/BgqJEBACQkAIdE8EPOHG5eCoo45yhx56aLJa7Lzzzu6+++7zluaU0q9fP28pYsETYcFSyXXXXee23HJLt95667nbb789VbZeoWFxFhZfQrqlkt13393hNpSacB955JHuhBNO8Is+U85gzDzzzH4GAZeDP/3pT6lg9oryEUcc4d0d8CNPKawNuOmmm9z666+fLFvyJAzis88+myxPMmL24JZbbvELvVlgnlJYk8IC5KuvvjpltspLCAgBISAEmoiAJ9xYUCAKxx57bBOTLk+KqdlBgwYlt1Sdf/75nnA//fTTfuBOJZdcconbZZddvH/xww8/nCpbH0EBos1i09jIF80oHIvbUCzIH5eWVLL33nu78847zytykOBUgvvK4osv7nbYYQf3l7/8JVW2nmxj+cRfHnealEJ/ol+n9C2GcC+zzDJ+EWFKQanATx4fcmbmUgqRllgXQP49VXAxRGHFKCERArUi8Pjjj3uFFHfRlONcreXsytczVvP8YbRK6RbZlTFpdtk84YYQ7bbbbt5alkr+/Oc/e7eOl156KVWWPp+LL77YT71Dehm4UwmkCFcWBmwiSqQSNjQhJKLtApoqXyLQYBEkmkVKVxYskBCi1NEzUFpZtLjxxhsn9aXeb7/9vN84m0iBd0qhzvRr3B1SCdZewvOlduv44x//6Ek+Gx6xADqlQETxXX/ssceali0EF2FwRVgDwPvYvpdlxMDMO/SYY47xm5iZNEJ6OoNwExmKMqKA029Cob4DBw5sR9CK6tU00BMkZKQpVM5Yc9BMRQZc99lnH8dscdj+1o+yuCaotqu17+X1t1rTCOtVb/8laATBI5iNjXn2qrCMbX/acNNNN/XJsQ6IduSZQGnhnH1eqvK1/zvzGaJcLFi38laVqSs+455wswqeUHUpF/PhC4m7A5bmlIL/9I477ugH7JRRHY4++mjv6kAItZT+p5B7FrXZRiepsEahAmPIScpwdRB9YjWjUKUMo4ZvMdP+hNbETz+V4Jp18803+wg0qd0siCcNoTnggANSVdf7M7P+gzqnFCzMxLJHYU79ziIKDP7yhJxshuRZshol3GUkzMps5IJ1B7UICh2WS2bpII5FaF4x0wAAIABJREFUln67ziycRYTbyrH88su3I6LggtLKOpCiQR1SZvHqY+tghDePDJWlkUeUq9Kgn2bLjtEFowdtXO9s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+WINpl+deuqp7uCDD06Vrbvpppvcpptu6h555BGvwFYJRNXcTEzZ4J7QXYb2qmpjCDzvC8gy/SOV3H///W6dddbx7ysUlpSCgkf+K620UspslZcQEAJCQAg0EQFPuBlAjj76aAdpSCVYBFdddVUHAcaynkreeOMNt8ACC3iXByyUqQRL//LLL++JgllyU+RNflgNd955Z3fxxRenyNLnATHCsn7bbbe5P/7xj8nyhfQedNBBnhhhnUwl66+/vrvjjju8QgVBSiUPPPCAn7lAybjqqqtSZev+/ve/u7/97W/urrvu8kQ0lWBBx8qNQoUilkpQMDbbbDOvHKZU5Kgf9bzssst8/hIhIASEgBDongh4ws2U6XbbbedOOeWUZLVgoF533XW9S8ncc8+dLF+mbLG4vvrqq0mnaKnveuut590jmFZOJeYPvPXWWyclZLTriiuu6InZ9ttvn6q6ngSefPLJ3rWBfp1KllhiCe/ulNryev3113uyjRvCM888k6q6bvfdd3f/+Mc/vKV74403TpYvijILNm0RbaqML7/8crfjjju6t956y80222ypsvX54GJz3HHHuX322SdpvspMCAgBISAEmoeAJ9y4WKy22mru0ksvbV7KFSndeuutbqONNnL/+c9/2iIypMgcV5blllvOPf/8894XPJVcd911bptttvE+pyktc1jkcO3485//7MA8lZAvU/8nnXRSUleHPfbYw1100UXu3XffTTqDMeecc3oyhmtMSoXq3HPPdfvtt5/HGr/pVGIW/SuvvNL361SCoowLDf75KV3RUC722msv76eOX3lKYaaIfn3MMcekzFZ5CQEhIASEQBMR8IQbF4v555/fL5xMJficHnrooQ5XCxYTphJCjq288sqOM5EvUsn555/vfahtMWeqfFnwyGIr3A7uueeeVNl6Sy9T77h3pJw5gfyh3OA6RJSUVII1HcKb2tUBa/4RRxzh3ViGDx+ezN1hmWWW8f75ENFddtklFcxeUV5yySX9Yu2UazAuuOACt++++yZ3RQNY+tYmm2ziUK4kQkAICAEh0D0R8IQbFwsiLaQkZDfeeKP3STzjjDPcAQcckAw9SAK+4xB9oiykkrPPPtsdcsghnpSlXHTF4lB8XlEy/v3vf6eqrrf0YoGkjZmOTyXMmvzrX/9yd955p1tjjTVSZesjWqBksCYhpQX02GOPdccff7xfB8G6iFRKBrNDuA3169fPW35TyRNPPOEXD6JIEkkmlRjhps6pMLa60ba47Zx11lmpqqt8uhECvGsx5uA2uOyyy3ajkneNovJMM3t03nnn+ehgEiHQWQh4wk2UAaIFPPTQQ52VT4d0jXAzgKa2cK+yyio+TB3hxVLJiSee6K2Bjz32mN/0I5XgWoGFm2n4F154IVW2PiIFRAH3HRYTphIWaBIC8Z133km6GJeIGUTiSG3hPuqoo7zbDu17ySWXeF/uFELbYmVmkSouLamERaK0MWHyUi56Bts999zTb5iVcs0JuFLPDTfc0J1zzjmpYC7Nh0hA+NIfeeSRbdelIH0YSa6++mqveIRx8msFBQWVMaBecsr9SFh/vrNQe8stt/S/15t2rXXh+lqwp4woyBDMvLC41A2Fknp0RamlrrHl7yzCXYRlUT/Je65i66DrugcCnnDjbgBB4oWWSljstcUWWyT34WZhGxYy4vimIidgevjhh7vTTz/du5SkjHLAywSXIXz077333lTN6xe1/e53v/NkH6xTCX0ZxZH42ymtFYR6JOaybcyUqr4M7ig0+OmzsC5V6DjbmAZ3IdyGUsk111zjXVhQ1FPOUBEBhjj+rDnB/S6loNwwc9Mo4YYAoKDVKvSrkFzmEYMiEhrmVW/+u+66qyfZxHrnjBGBMuBCRWhKYsIXCTu2YtwJyWUjhLuMsMYoBBa2NLYNQux5l1fVNy9dnhkj0GH5eYb5fcCAAaXFWXPNNT3e2fdpTJtnE66lDnltlyXc9p11O0Vi9ad9MADVKhjJUKCq2s6us/SLCDfl4L8sprxbcLMlr6wyFypWZXXN1q2o7WrFQNc3BwFPuLEY8fLCrzlWws6X7WgxaRCGkJcJvrZEHSgT0wjzXgy1diisvHRoyhxr4c7LP3yJxdQXtxl8MLGAVsYPHj7cuXXXdS6vPR5+2LkVV4zJ0l/DYITL0Nprr+03KamSskHRBr4Y6xL1BF+uLRsQrTxlL+LsgF9WB1xnIPgsTo1VbPJexLW2r8WPTh32keeI9RCEnGRamXZOIYRcBGN8yFPG/8ZVCJJAXGoiw6QSNhbCQDBo0CA/m5BS2OAHl5JGCXdRmWu18GUJdxWRLnqWsuQ1thxFRC+WABYR7iJCZuUvqqeNf0X/1/L+qqdf1WL1bZaFmzxRgFjXgCtLrEWcNibaDq5oZRvPFV1XS11jsYztd0XpFVmsiwh3WT8twydb92y+9T5PsTjpusYRqItwZ7XKel4o/fv39xYjrBVVLhZlhBsIaiGCTAlDQLGQsTNflTSLCDIdjUsJcZpx3ymVMsLNjf37O7fDDlVF9/+jRGH1JKrEDTfcUHlPMwk3+bK73ptvvlmZb7NwhnA//PDDhTt6ZgtSVt/Yfs1GLixaZLfC1BsbnXDCCZ70Yrmhj7GrawrBP5/dO1MTbsIQ7rbbbo4ZMpTtVIKbEoYJQi/GvDeaWS5mL1CoUDY6Q2IIR3gNM2W4lDCzgZLHmhTWp+RZQCGxZsmreo/n1S3WoFLlzhFjtGH34azLSkiasgQqJEBYixnTWFMRGiRilYDYdq3VSptVdrKkrKpNqsbWWAJt9Yu9Pntd0fhQq2EkD+eY/l/WPrUQ7vBa1tzEzDjZM0B0M543Wbhjn5aud10b4aYjsKAwRuyh52GEMCN5U05laWHtRdPFsl419W+dNJuP/c7CwOy0YVHekD9cLHAtqbJUhYpF+GBb/fOmvIryZeMZXsi4HVSKEW4uZJDt2/e3Wx55xDl2m8MHnIgjEWENCfUIzljnYsI+GgGtZ9YirBcWbsgfLzN8favEXqhLLbVUQz6auJTwIrMdK8vyLWpHm72JbV+LdU5e5Fu1W2IVFrX8j5sSigG44ZtJrPcUAs74U2NdT+lSgmWM+hL1h+n1VMJ7g4WivCNTuqJRPwg3bjSnnXZaw9VtZErfXCaYucJlC8Hfd6211vIWTsLL4vJBJBkUwKzCWqtFLiRC5BX6HlcRxRCo8N1t73QUGMoc5lEv4cbd55ZbbsldtNhswp3XAWKsvnl4QeR4npgly/PpjnGRsTGZNVExvvX1Em6rd7YPVbl5cJ+9x1HWYwhuFuOwH5cZaGJcSorcSRp5sBtVGBrJW/fWhoAn3OwUh8/tk08+GXV3SMpMS6uVoOH7ib8S8Zr79OlTmm8V4baHvoq4c92HH37oBwbcHKp8MctIYK1+gNtuu60PV8fCukopItzceOihzrFBUaRrCVPvEF9errW4lNTantk6QbiJUEKfov2qpFmEG5cKorHE4FymXNTSvljxbVfL0aNHV1W1qf9feOGF/jmCBOHakWrXx5lnntnHpE69aJJBnUWitA+W7lRCXXlv0J+ZIUspuKDhksYmUo1K3uCc91uZ60HZokmsb0UzQ40SbkgtRp6sVdPeHShhSJ5/rOHWGYSbZw8lI8/Sb1ZxU0qq/KXz2hfCSLx7nvVarJuWVmg4aLaFOzRKxYwZjSh81MeMJEV5lSkJeS4e9GVmNYoMhmFfz/adIiXAfi+aEbE1CPCVMoUsLFs91m0rR+wsUaPvFt1fjYAn3LwMIL4xiyaz5BerQJ41oyprFhEycELMqnxtq6wZMQ+6lQfFgum/wYMHV0YbsIe7GdNWWOMgvyyarJQywn3ZZc7tuGO0WwnT0Ph/sgNj3kKMbFnKNPhacKBd2WGSAQZf3yopehHHWpktfSy85Pnjjz+WZmkvz/DlV1XGov/ZhIVYyRAjfLhTCi9ldn1k1gb3EkJephA2+sGtgJkqXFlSCWSO8F1MrR522GGpsvVKIxvQ4IpGHPBUYhtI4bJB+zYqzSTcRPqwRWjZ5zTPklf1Hs+rW5YskC79zWY07Tkm9Km938pITGcQbgvHx7OYtfQW+fFS1+x/tVgqzbKbHftszCpTerIzBUVRS2Is3GaxxsqP0lFl5W7Ewh2Se8ZTDB1ZohxLuG28wUgRLijlc7hoMSTcoWIXE4Um277WNmGfLrJ45/Xrome/ln7T6PtD9zeGQFuUEogCL4sqyT7QRdbnqnR4yLFININw10LKsEAy5U/YOCxWZVL18qqqY/g/1l6iSRDFolKaSLjZXZK8WXAFMauSZhJu8iN/XC6qpFmEm/Bp+JhW4WwvNFwEsoN3aEWKUTKIvW3rEKJchqrAqOF/YufjroRP9cUXX+xdS1IIs0MorbgpseV5KjnwwAO9axZRd1jImEroLxgGINypMKZuLExjgy6s+c3YQKpRCyNliglfVka4LWxekcXQ2jSGSPC+Cv3Eubcs3az7Ra0uJXkuCSHpDcl+Vf3qIdxV7ff/2jvXUKuKNo7PKdOCTiZ2E4vuWvihqBTTrnQRgqBAEkntImFYBn7QD12tvlQS2cUggoyssCILRMMi6q2MICW7vl0/WB2M0q6Edep4Xn7z9hzGad323uuMZ7v/A5u9zz5rrZn5zay9/vPMM8/YsxCjElbReIF73RZu6sCsMWFvMaKVxQJvRXDTzszSYsDBJYgBP4mBn81qmFsQm4GxRiwrRGMRw6Lf+3iwV/bbE7av6STcWHleWMzvPP/vPE5VorJYuRrRRWV10f/rIeAFN3GwWfRVJXxbXYIMYfTCCy80JLjtxz50HbHyVBFGhozFbVUEd5lLSSPxShmRI46qWHtdjS4lLC6bNWuWF5XTp08v7TV1+nDjO07+/EiUpbpcSuC8du1a36/KUlzXrB+zKv1qdwpuBgw8cLC+8jDiRzZFYuEgYaxwk5o5c2aKLH0ezJpwHzEr9/jjjyfLl4z43cAo0UxosWYLyiJvZi2wvOG+02pq1cJt9ykWzaIZsyq+qlWOyatvPENlU+4m+EzIxCHWYoFDfWyxIxbaZhdNmsUztILiasJMjPmLh3XJ8ruuMsCIedhvWLi4MaxTFcHdrIU7tvg2YhFvNEqJDRSY6SH4QCjsw0FOWAbWtzAYKLK6x7PYRVbsMn/xIh9urrtu3Trv8hdvspM1I5M1WxIOJssGNkUuYa3+huj85gl4wc0PAz6ZL774YuGVykbXZSuaw4vT8XhwtuLDzfWaEdxECWF0XBYdpWzRJPlXdWfByoyrAy4tpSlPcP/3v84R9u2ww3ZdTFlwQSyQLLjC6ltl58W6BDfTfYsXL3bEL67iZlGX4GZwwUxClYFN0eJX+3GtIrhZFEqsZFJqC/emTZv8FCg7XRKRJtUuiLhVELED1qkio8CXaDv4UWNlTrmhEnkzM4ZbWCq3HfKkTXGTIuIPg+ZWUyuCO/w9xGWBvsb9ViXhf1xlhi3vWmEsZAY9+Etzj5uYyls4aBZYOy62HIYCrQ7BTfltBsCiuGSJoyzLZlXBHbrmxNb10AKf9Tyu08Idsy2z6MOmTEOE7R9aaE2wMtMT7qpZ1J7MDuWFILTfd3O9yTIkVrUQNxKlJKuN44FnlRmaKr78Vctf5f7VMfUQ8IKb1feIbjphUYo7qR3bTLQQHthECkGYlW11Xub712jH4sGJ7y6DjLJUFIapatg48iBKCIK7ygLCAQt3Xlz0BsICYhFENCK4qwiFohmMRhZfYGFmoRcWo5QWbuqLGwsh66qkovpW7VcMonDpIKVeNIkFlHIOHz7cT1UylZwinXbaaQ6xj1vJCSeckCJLnwfRURBGbKr0H6L2JEwM1FkTkSrWOVUjxOWVV17pLXpmCWumyo0Infj64aI9/mdRSkKf6XjnxiLrdZGgyLNMW5lia6Dlg2EBH3fKxuLK+fPnu4cffvhf8Z5jy+FgCG4ra1H0kCw+eYMhZu1wvyzbfCV+HmVZusNnKe3KdXFvaDRKSZ57RdmgoRWXErjGTGPRH7YnxyPOQ//+ovsgNp6RFxFccJlrJmZ4lv9+Fp+sWZe8rearRKSh3rJwN/MrOfjneMF99NFH+wcZPqB5qWw1cqOWZvynGYGyiPDAAw8srGmR4K4qisIMmBpGnJhVsgxzVv5VLJ/hdYlSwpTSDz/8UJadKxTcFaOTWCbEhSW6AWL/7Aob5tQpuNnyG5eSRny4Ww0LiFUHSyADuaopa1DVSPuyQHPffffdLYKbKEHcu/Rp7lFcw1IkYlLTnxu5j+ooF9PzDHBYoIrgT5nYTRQ3uJQWfeJ/06d5EY2m1VQmiOz68QM7FDIMaMOt3bMsfEWCO/yNiV0hEJd57ipxPqFwx0URcWUh+ugnPGOyFliGLh6DKbjzLJ95C+LyBHeVjWLy/Or5Hg4MxG2XShPmZS4SYV8LxaiJ1nDBYXhsnjsEx9QpuK1ONhjh+rFbSxW3paoiNu/ey7unqgpurhsOJIvWSMiHu9VfwN17vhfc+H8ybVklTnNdxcWq/sUXXzgiPJh1sK5rF13HNilB7B9xxBEpsvR5sLCNKXCLX5sqYx7S+MshzFIu9sLCzcMON6Wq1uY6mCxYsMBb1RsR3HXki+AlEY4QYZYqIXgZMOPDWsWNpq5yMVvy2muvecGNBSlVIl/cLLh3sa6nTLQrCzUvueSSZNkyqMEVg8WiCK9WU7OCOxZUoeA2IRVu/FJF6JhACn3iiwa6cdnDPEIfbmYvLVpI6Meb5WIQipu82cyqO03GbZNnBc5a6GkMY8tmXti6WNSG9cjyCS7rN+H14BRa1cNzy2YgOLYowkadgjtsZ/NVj7kUuXtQVmZpQsHNbF0cqaQRdvGmR/E6r7L7r8wyXXVwUHadsjrp/4NDwAtuLMxM/zcTFL7ZYh177LH+YY3/a6ppcMpK9ArifrNossyHu9m6ZZ3HwpTnnnsuueDG6sPMBRaKlDvkIbgZZBATu5JVvybY9OPHHnssueC2zW4QvWVx5Wuqqr8MA9YxY8b4RZNbt26t89KF17KNb7h/D2NNQaKEOwduFmx3/tVXXyXK9f/ZILi5hy+99NJk+bIAGL9VhFgd0WDKHvhWsSJh1GyUkhhaaGHF6nrZZZcNWGE5Np7iD8UUv+MII9tWPBRWPE9iq3AoAsN8whnSrEV/oZUytljG4qdspqxKRK+sGcaQgzHDvY/IU7hFIvKsbFj6YYM7Dc/zspm6vLUzVrcwilOZZTtsXzuf78JFi424NmXNXmcJzngGumhdlfEN3W+yRHnIOQw9mDXbnTfLXmThZuaZPlo1LntdayCS/XApo0wCXnBjHcD/DbGSKh188MHe8onoJoZxqmRxuHlYl4UFrLNMc+bM8X7UCKSUCSsz0Rzwl3DjvnYAABQPSURBVC/b6KfOciG4WVC1ceNGv0FKqkS8caYYU1rVqZu5ciBA6dupEpZ8ovbQl1MKUKKE4O7ALq+I/VQJQYEIZZBhu9ymynt3CG4s3IQ3I0IJC69bTUWCOxZDeYvg8wR3fH4s9mIxWSQG43VBCMusiB9hnkVrTKpE0GiVbdH5jYjVvOvE1u5Q4GeJvjzrrl0/z9Ie5m/XwCWSsJSh+0YVXnEerVq4q+SZdYzxD92V8lybwvNhzg6vVXeyDs9txKWk2XrpvPYi4AU3DxIW5qR0KeEhbYI75QMbgcAUeGrBjR8122BXilJSYx/Cb/vDDz/0U+EsbEqVENxYArds2eI+//zzVNn6Xe6YRk7pXkHliNGM9YX6pnRVshkbBlMsoEyViHhjsxdVdnitq1wMXAlFiACzOLx1XbvsOvxOsiCPSCmpEoN06oy7Rkrf8VT1Uz4iIAIi0CkEvOBmOhxBhvUoVUL0MnrG+pnSpQQLJIKoSljAOlmwKx5Ta1VC5NWZL9YxRun4y1ddJFpH/ghu3A7wacbKnSphjWC6rkoc7jrLhFWb/szGC+PGjavz0oXX6uvr864OkyZN8r7NqRJ+zKxJqBJlqM4yMQ1LVAWiBqT24SZKCXVmwWiq9Oqrr/r4+Qj9lAPmVPVTPiIgAiLQKQS6+vr6vIUba1XKH3SmhBEoLCIcNWpUMt74E+PCktoSScxxRErZluN1g2ARITE7U/vKE199ypQp3r+X2MWpElOerJ4v22my7vLYVucsJKwSDabO/BGCxGlGnKVKuDc8++yzfiYhpc86vswMqrDo4yaVMsEZizMDyVSJxX/sWcDvc8ot5VPVT/mIgAiIQKcQ6Prjjz/6WXSBdWzixInJ6o1AQfRu27bNjRw5Mlm+uHQwBY5lnYVXqRJWXqKEECUlZcKyjkAh/GJZvPM6y4XgRRQRgQBfzVSJBZPE4E09k8Dggg1ZquxgWjcLIqQwO4UVNFVi5gQ3B9o53s1uMMvw4IMP+sVG+OsiflMmZgKJ/U1YuVSJQcVZZ53lBxfEHlcSAREQARFoTwJdO3bs8IsmP/nkk6QbWCDuiaOLJRT/11SJ/BCeLF5MubiNBV6ECEq9EyFim+1wU3NG8OLCgjC76667UjWvW7VqlY9cgCtLyoTFl4U1RApJGbWDOiK42U20yu5jdTEhAg1rPliHkXIgB2NYs+ZkxYoVdVWn0nUQ3OyuyaY/qdLHH3/sowux6Ivwj0oiIAIiIALtSWBAcKeOp2t+iSw0s01DUiAkPwYYTP0zDZ8qMfWO6wwuJSnjNLO1OuKEfFNtigJTBC/hJvFbRwymSuwEyKI2fJtTJvzGcXdgBqVsI6e6y4XgbmTX0zryZ2Eqrju9vb1J+xUhAc8991wfBu3mm2+uoyqVrwHn1DtrMlAnhCoDuZSLyytD0YEiIAIiIAKVCHT19vb2s2sbvs0pow0QtYMQbjxI2InwjTfe8IIUFxN8u1nkh88kFjQWwHEMYhnLKWKOF6IKizHbafMwxAKFmGWba0Q8vqVY36gXVkciG/DwIsIC1sBWhSBloDyIDisPZeFFWaw8lBOxy+JQ6kudEOBYnakb/tUMAjiP+nA9XE84L74e17H6MTNAHXkQ8zl8Weuz4Q2bhfDghiuuJeSPKwBlJj840wc4H7GI5R9erWxIRNm55po1a9yECRN8+5Enwp/6WdtRTtqOdqNunIOLAjyoG2WinCzOg5ddwwQ1ZYcH59DOLIbFh5oZDNha3+E8+o/1ISsH1w5ZW3loO65Lmaxs4We+Q1xTN5gx5Y/lFT9q8qaduadgznG0N2Whv5A35afelJ+y87L2Y40Bwo7FeXymLSjj+eef7/tUnLgOln02q4gT7Qs3+FEWytbT0+P7HJ/pD5Qt5GrtwT1EmXD5oi/QL1h7wcwFFldiy3OfEvmHtRjWv8iLa2Kdpey0t/VpY233rd0rcAjvXdq/u7t7IG/6OC5gnEdIwmXLlvk4+ril4R4Gb/IP+zaMuQ59irbknXJQfn4XqBfv/O7QhnwmT+t3tAnn2f3Gtb788kt/DP2ZF/2Nctl9Gr8TIQhXkKz/01ZsU4+rGawpn73sb/oM5U09Q1Xp6aGDREAEREAEKhPo2rlzZz+uDjy4eJibAOAzP/o8dHjA8PDiAWeigIcPLxMLPCg4l4c1xyIqeCDx4EVw8DBETPPibx4gRCpBCHIODzUTfwgbPvNA5PqUw172AOThTH4mQDiehzkCirwRNogrE1q8mzjmWBNUVkerC3+Th9XFBDDncg0TJ1ybclNWOxbqPFgpB+fBwYQV17ctzm1XwnCQYMdyvokPBgeII6srx/MyYc455GUvE7HUwRYNEkoM0UtCSPA94glhYtezd46hPtTNBC1586LdyceY2zn8DW8bBJmgQojRr0xUcl17cU7IzOqeVR/aiWtafvwdlteYw/uUU07xx7733nsDx1heJsyNZfxO2cLrxoytbGEZQxEZD/wsXxPpll/cV7iesTNhSp2oJ32Gd64NY+tXXMu+t+/CgYLd/SbyTMiaqOe+Ik/6l4lLE3jsMsf6CspFn6fP0le4ZxHnvCOo+d7axQaWlo8JVK5BXtaH7N36kLUl9YvvX+pr97Hdt8bbRLoN0KzsNkCy+4vzONYGV/abYAMKawtraytHOBjIGtyE9234G2DtEtaXa1M+voO5tan1NfKygTvls5cN4mHMAJIZOSUREAEREIH2JeDDAlJ8LF5mqcLqgoBGHPOQxVKHZYeHBWIstg7aQ98e8Caywgc91iOEHtYghBiB+ll8lDJCiTUTogGfdaxTWMeoNwMCs6IiJswSaVZg6kZ9WByHdQ8BGg44eHjjY4lFEmFDaDgGFNQXIVA1mdAxSywDk7AsIWsTWSbQzfptFt/QasqxtBsih2siAkKha2IdwWWWRAYXuBrBh3B35GMzDZQDJhzD8WYpxBJJvZn2RzSYhRfRRr7G1rhSHkRfaN3jGEQfYg3LI5zjPhf6wseCj7qZRd0skcQCx0Jrg7K8d5tVCAVsaOGmnDb4s0En5bdXne5C9FEsnDZYpMzwtgWh9EF4H3/88b5M/I/7FG5YVrnPOIfz49fmzZu94I4HbNwTWFRNlFJfszbTFszS0MdpY2aM6BOpE2UO+5IN+KwPmyCmbKEo536gnzbSRtbPjQf9yWZN+Mz9QR6wp4/zO2qzCnxnM1m80+cptwl6e6c8MKbd4MssAqFL2cyI+4DtpmkHJREQAREQgfYlMCC427cKKrkIiIAIiIAIiIAIiIAIDF0CEtxDt21UMhEQAREQAREQAREQgT2AgAT3HtCIqoIIiIAIiIAIiIAIiMDQJSDBPXTbRiUTAREQAREQAREQARHYAwh0LVmypP+2227bA6qiKojA7iXAwkQ2GtL9tHvbQbmLgAiIgAiIwFAj0NXV1dWPUEi5+cxQg6DyiEAdBNjWncgfRLEg6oSSCIiACIiACIiACECga9iwYf2E/Uu9O57wi8CeRuCjjz5yJ598skN4E9ZNSQREQAREQAREQAS84B4xYkQ/m8+wI5ySCIhA8wTY7IeYyQxgW9mls/kS6EwREAEREAEREIGhSKCru7u7f/369e70008fiuVTmUSgbQiwIQ2b0eBSwiYrSiIgAiIgAiIgAiLgLdwXXHBB/znnnONuvPFGEREBEWiRADsS9vT0+N03lURABERABERABETAC+7Jkyf3v//++27FihVuxowZoiICItAkgVWrVrmrr77ab6vO4kklERABERABERABEfCCe8GCBf3Tp093S5YscWeeeaa7/fbbRUYERKBBAtu3b3fjxo3zlm0Et5IIiIAIiIAIiIAIGIGuU089tX/48OHuwgsvdO+88477/fff3b333usmTZokSiIgAiUEXn75Zff888+7Rx991E2YMMGtWbPGHXXUUeImAiIgAiIgAiIgAgME/E6TTIW//fbbbuPGjf7V19fnwwSOHz/eTZkyxU2bNs2dffbZ/qTe3l73119/uT///HPgM9/ZK+9/fB8et/feezte+Lzy2muvvf71Of6OxWgjR4705eB/WedkXQ/r45gxY/zx++yzj8932LBhu7zbd999950XTPyfY3kPP3P9OhNcyKfORPs18vr77793OR4LLW3PNXbu3Olf9jnvfcOGDX6QVuVYuwbRPEaPHu36+/t99e09/EyfMT5Fx33zzTfuyCOPHGjTuH1//PFH3wfC78PPW7du9W4gLHbkRVx6+8w7g9ItW7Y4BPbKlSsdbljWH7Fsc58sW7aszmbUtURABERABERABPYQAplbu69evdpt2rTJrV271iFEECuHH364I3xg1VQmTEeNGuV++umnqpfb5bgRI0Z4wd9oOuCAA9wvv/xS6TTEOeKxkUSdEYWNlI+BDbMK8Bg7dqw/H+H37bff+ljOiOHrr7/enXfeeZlFeeihh9wrr7zi3Rhoq8mTJ7vXX399l2PDtog/29/hO3Un2Xc2uMl7Z7BChI7u7m4/qLGBFELZ/rYBVjjYoQ3333//gcET/7M8fv75Z3fQQQd5oY8wtkGWlSsu97Zt2waODwcb8OP166+/etHMAIe/w3c+s/kTyQaFdh7Xok14IcIPOeQQd8wxx/h421OnTnW4YymJgAiIgAiIgAiIQBGBTMGddcJgWGLboWlCqyvlNSEGDxNtJuDY8ATrOOcg7kxkxqIz/BtRj2BmhuGDDz5wmzdv9nkgANmtEKGImMXlZ926dR4ZEWUYDH366adekB533HHu4osvdldccYU78cQTvVA2y3Qz76Fl++uvv/YiM6yvfY7fjQPf//bbb77+obgN2WV9Do/F+s1shold6m2f43f7nw2QwlkOE/g2S0G7MCDiZVZsOPNC/PNi4MDgjBcDIl6UhWspiYAIiIAIiIAIiECjBCoL7kYvrOPrI4Abw0UXXeSWL1/ubrrpJm+lnzNnjrvmmmu8RVtJBERABERABERABERg6BKQ4B66bTNQMqzdWF6x7M6cOdM9/fTTbVBqFVEEREAEREAEREAERAACEtxt0A+IgoGv8Pz5872VW0kEREAEREAEREAERKB9CEhwt0Fbff/99+7QQw91TzzxhJs9e3YblFhFFAEREAEREAEREAERMAIS3G3QF+6//363cOFCH57xpZdeaoMSq4giIAIiIAIiIAIiIAIS3G3UByxEIJEy7r77bjdv3rw2Kr2KKgIiIAIiIAIiIAKdTUAW7jZpf0IJsmhy8eLFXnATC1pJBERABERABERABERg6BOQ4B76beRLeNVVV/ktxK+99lp3zz33tEmpVUwREAEREAEREAEREAEJ7jbqA3PnznXsAtrsDp1tVFUVVQREQAREQAREQAT2GAIS3G3WlIsWLXJLly5ts1KruCIgAiIgAiIgAiLQuQQkuNuw7QkNuHLlyjYsuYosAiIgAiIgAiIgAp1HQIK7Ddv83XffdRMnTmzDkqvIIiACIiACIiACItB5BCS4O6/NVWMREAEREAEREAEREIGEBCS4E8JWViIgAiIgAiIgAiIgAp1HQIK789pcNRYBERABERABERABEUhIQII7IWxlJQIiIAIiIAIiIAIi0HkEJLg7r81VYxEQAREQAREQAREQgYQEJLgTwlZWIiACIiACIiACIiACnUdAgrvz2lw1FgEREAEREAEREAERSEhAgjshbGUlAiIgAiIgAiIgAiLQeQQkuDuvzVVjERABERABERABERCBhAQkuBPCVlYiIAIiIAIiIAIiIAKdR0CCu/PaXDUWAREQAREQAREQARFISECCOyFssnrqqafcm2++6e677z633377Jcl9w4YN7owzzsjM66STTnLPPPOMGz9+fJKyKBMREAEREAEREAER6DQCEtyd1uL/1Hf79u3u8ssvd1OnTnW33HJLh1JQtUVABERABERABERg8AlIcA8+4yGZw5133umwfGNxHz169JAsowolAiIgAiIgAiIgAnsCAQnumltxx44dbuHChe6RRx4ZuPJbb73lLcmk0KVk9erVbtasWf8qQezmgTi+9dZb/XF1uIB89tlnbsaMGW758uUD5aoZgy4nAiIgAiIgAiIgAiLwDwEJ7hq7gontsWPHDrhpYEW+7rrrBvyki3y4s9w8Yku0+WObiA/FeFyVadOmZVqwOaenpyepH3mNmHUpERABERABERABEWgrAhLcNTaXCebZs2d7/+isVCS4YyGcZ4luRTDbNRctWpRbxhqR6FIiIAIiIAIiIAIi0PEEJLhr7gJmcZ43b16mBTlPcPP90qVLd4kYwncrV678l5UaKzf5NON/nXfNmjHociIgAiIgAiIgAiIgAv8QkOAehK6AqA19s++4444BF5MswZ1nyY6vExY1z12kqDpZLi+DUH1dUgREQAREQAREQAREICAgwT3I3cFE85NPPuldOGLBXRSer4o1uhEf7iouL4OMQ5cXAREQAREQAREQgY4jIMGdoMkRxSTiXceCu8gfO15waUVtdvMcLOk33HCDe+CBB7TRTYJ2VxYiIAIiIAIiIAIiAAEJ7hr7QZYFOXYXicMCxn7bcXHiKCWthPRrxfe7Rky6lAiIgAiIgAiIgAh0FAEJ7pqb20T3+vXrB65s7iR8YYIba/fcuXNdeFxYlDB2d+w2Ev6vkeJXcVFp5Ho6VgREQAREQAREQAREoJyABHc5Ix0hAiIgAiIgAiIgAiIgAk0TkOBuGp1OFAEREAEREAEREAEREIFyAhLc5Yx0hAiIgAiIgAiIgAiIgAg0TUCCu2l0OlEEREAEREAEREAEREAEyglIcJcz0hEiIAIiIAIiIAIiIAIi0DQBCe6m0elEERABERABERABERABESgn8D94MM1ka4jMbwAAAABJRU5ErkJggg==)
</center>

### 4. remove方法
```java
public E remove(int index) {    // 删除列表中index位置的元素，将index位置后面的所有元素向左移一个位置
    rangeCheck(index);  // 校验索引是否越界
 
    modCount++; // 修改次数+1
    E oldValue = elementData(index);    // index位置的元素，也就是将要被移除的元素
 
    int numMoved = size - index - 1;    // 计算需要移动的元素个数，例如：size为10，index为9，此时numMoved为0，则无需移动元素，因为此时index为9的元素刚好是最后一个元素，直接执行下面的代码，将索引为9的元素赋值为空即可
    if (numMoved > 0)   // 如果需要移动元素
        System.arraycopy(elementData, index+1, elementData, index,
                         numMoved); // 将index+1位置及之后的所有元素，向左移动一个位置
    elementData[--size] = null; // 将size-1，并将size-1位置的元素赋值为空（因为上面将元素左移了，所以size-1位置的元素为重复的，将其移除）
 
    return oldValue;    // 返回index位置原来的元素
}
 
public boolean remove(Object o) {   // 如果存在与入参相同的元素，则从该列表中删除指定元素的第一个匹配项。如果列表不包含元素，则不变
    if (o == null) {    // 如果入参元素为空，则遍历数组查找是否存在元素为空，如果存在则调用fastRemove将该元素移除，并返回true表示移除成功
        for (int index = 0; index < size; index++)
            if (elementData[index] == null) {
                fastRemove(index);
                return true;
            }
    } else {    // 如果入参元素不为空，则遍历数组查找是否存在元素与入参元素使用equals比较返回true，如果存在则调用fastRemove将该元素移除，并返回true表示移除成功
        for (int index = 0; index < size; index++)
            if (o.equals(elementData[index])) {
                fastRemove(index);
                return true;
            }
    }
    return false;   // 不存在目标元素，返回false
}
 
/*
 * Private remove method that skips bounds checking and does not
 * return the value removed.
 */
private void fastRemove(int index) {    // 私有方法，供上面的remove方法调用，直接删除掉index位置的元素
    modCount++; // 修改次数+1
    int numMoved = size - index - 1; // 计算需要移动的元素个数，例如：size为10，index为9，此时numMoved为0，则无需移动元素，因为此时index为9的元素刚好是最后一个元素，直接执行下面的代码，将索引为9的元素赋值为空即可
    if (numMoved > 0)
        System.arraycopy(elementData, index+1, elementData, index,
                         numMoved); // 将index+1位置及之后的所有元素，向左移动一个位置
    elementData[--size] = null; // 将size-1，并将size-1位置的元素赋值为空（因为上面将元素左移了，所以size-1位置的元素为重复的，将其移除）
}
```
#### remove(int index)：
1. 检查索引是否越界，将`modCount+1`，拿到索引位置`index`的原元素。
2. 计算需要移动的元素个数。
3. 如果需要移动，将`index+1`位置及之后的所有元素，向左移动一个位置。
4. 将`size-1`位置的元素赋值为空（因为上面将元素左移了，所以`size-1`位置的元素为重复的，将其移除）。

**`remove(int index)`方法的过程如下图所示**  
<center>

![avatar](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAwYAAAFBCAYAAADNBLgpAAAAAXNSR0IArs4c6QAAEN10RVh0bXhmaWxlACUzQ214ZmlsZSUyMGhvc3QlM0QlMjJhcHAuZGlhZ3JhbXMubmV0JTIyJTIwbW9kaWZpZWQlM0QlMjIyMDIyLTAxLTE1VDExJTNBMjAlM0ExNi41NzRaJTIyJTIwYWdlbnQlM0QlMjI1LjAlMjAoV2luZG93cyUyME5UJTIwMTAuMCUzQiUyMFdpbjY0JTNCJTIweDY0KSUyMEFwcGxlV2ViS2l0JTJGNTM3LjM2JTIwKEtIVE1MJTJDJTIwbGlrZSUyMEdlY2tvKSUyMENocm9tZSUyRjk3LjAuNDY5Mi43MSUyMFNhZmFyaSUyRjUzNy4zNiUyMiUyMGV0YWclM0QlMjJWNHhnSUhjdWctblJBZE9zZ3UtVSUyMiUyMHZlcnNpb24lM0QlMjIxNi4yLjclMjIlMjB0eXBlJTNEJTIyZGV2aWNlJTIyJTNFJTNDZGlhZ3JhbSUyMGlkJTNEJTIyTnNzaXBEQzhHNFlqTF9wbzh2TDIlMjIlMjBuYW1lJTNEJTIyUGFnZS0xJTIyJTNFN1YxYmo2TTRHdjAxU0QwUGFYRVBQRUl1UGRMTXJGcHFyWGIza1FRblFVMGdRMGhYWlg3OSUyQmtvQWsxUXFLY2NtUmF1bEFnTUd6amsyZk1mbWkyWk50cSUyRmZpbWkzJTJCU3VQUWFxWmV2eXFXVlBOTkEzZDh1QWZWSElrSmM3WUp3WHJJb2xKa1g0cSUyQkpIOEE5aVJ0UFNReEdCUHkwaFJtZWRwbWV5YWhjczh5OEN5YkpSRlJaRyUyRk5IZGI1V25jS05oRmE4QVYlMkZGaEdLViUyRjZueVF1TjZUVU04ZW44dDlCc3Q2d014c3V2YjlGdFB5NUx2SkRScyUyQm5tZFljJTJGeU9idHhHcmk5N29maFBGJTJCVXV0eUpwcDFxVEk4NUlzYlY4bklFWFlObUdibjlsYVhYY0Jzckp4b2wlMkZKUGxtdzI3dGN5ZDclMkZ4NXIlMkY2NXZ4eDliNSUyRm4xZUdNWDJ1emVpTmYlMkJLMGdPdEpLQjNVQjVadFMlMkJicEFRJTJGZHRFU3JiOUFaV2hXdUNtM0tWd3o0R0swM3hHdVZza3JnT2NLVjNsVyUyRnFDSEcyeWRhTUd3NGZyJTJCSnlpWEc3b1JnNG9PbSUyQnB3alY0TktFcndldmJXalFwUUtGU1FiMEZaSE9FdTdBQ2JRbk5zcmIlMkJjR0xkbzBhWkdOaXVMcU1iV1ZjMG5UT0VDaGZVZEVKc2N4R0hmSVI0ckJySEZRVHpwT2NTbXJoakVOZ2Z4ck84UVc0cEI3SEFReiUyRnNPc2FzWXhDNEg4YmUlMkJRJTJCd3JCdkdZZzdqbkNGdW1ZZ2g3VDRld294akMlMkZ0TWg3Q21HTUlzSVB4SmlzUkRhaG1vUThyR2I2aENxRnBvWmZHeW1Pb1NxaFY3dUozQVFmTmtZZndJTFFUckduOEJEa0k0eGJ5TDBIZUsyaHlBZFl0NUVFTyUyRlRvUFZKbnVZRnJ0NmF6M1g0NyUyRkhtZ25Uc2VYZEJ2SUVqQ2Z1MjZ5QWRlOTUyRU8lMkZzeU1HZTh5T2tZJTJGJTJGOGhvUjBpSiUyRmZrWkFOTVhzaDdWRXMySFlrcEVQWWYwZENPb1Q5ZHlTa1E4aEhjcyUyRm1TSmhqMlJqemtkeXpPUkx5TWVaRHVXZHpKT1Jqeklkc1UlMkJFWVN3clpMTld3NTBPMjNrOHBjVlhEbUElMkZOZWolMkJueEZjTll6NDI2JTJGdWtrcmJGSUIxakZpdyUyQlVmenJxQWF4Z09CTkxZdEJQc1Q5QyUyQjRNMVNEa2d6dlZJVlF0ZHZNRWpNSTkxbUtRRHlFZm1ta3pWJTJGUG1tZzhYSEExdUR4eHROdGZDaWVZSHFNU2ZhSUduemNaYWFHc0IzZ2R0Y3F5dXclMkZBQ0ZEcmRHOTZFbTVhMDk5VFF4ekVzZEhEJTJGUHFBUFNpREUxbXFGZzRoYVVZMU9Wb2dxR08xeCUyRnh2QUhReDM5NHAzUFIza3J0SGZLVHNqQkllY2xKVFRPJTJGSW0lMkJCcW5XbWc5JTJGTktpT1A0Q3p6bzViYWxWOHR1NTYyN0xHMHF4YkNrNlRkWVpYRjVDU1FKNEN5RVNiTEtNMG9CdTJDWnhqQTRQQ3dBdk15TGYzQ0I5NyUyRklrSzdIQW5GQnpwcWl1UTVudjZWTU90WTJ5eUg4Q0Z2QmxlWVpxV1NWcDJpNnFQUnpkaDF0S2h0N1Zwam9hbFNtc1VmR3glMkJEWHkwdlcydkpoWW9VWm5tajlIVGN5SDdVM0hEU3JVVVAlMkYzUkRLUjR5WTQzR3hJaDVPUCUyQjBqMSUyQkYwalpIZXFCJTJGNzNjRmV0YTFDY1hPZXR6V3dOZGolMkJ3STBTYnBsb3d3MGZOTlk5MCUyQlRyUzM4elglMkZDayUyQmFvd2VCVkI4ZlAlMkJPNnBtaDNhQlNBJTJGaWdNT2podmxHclo2d0ZXTDdvOEFBJTJCVEF4OG1LY0ZRY2QxREFMJTJGY0lIN3ZNQ3RoeXE4NnFFJTJGVXVJdWxrMGxjU2duV0dJZ0lZWjF0ZWtYNWVzZ3lRWmg3UlVHN2h6aTl1Q2lIYnp4VlkxbkVPMUhpOVljODZLdFhwNGZKTm9yYkFXUXhRSDZ1aHRSbUViN2ZiSnM4dHZFNlNZN25ad1R4TnozNFc5Q1c0UE82VUNPbFJVZ2pjcmtWN1A2TGpqcEdiNGo1V25uM1htN3hjZyUyQlB4UkxRSTg2a2NKVlpMOVZVUmtWYTFCeUZXRjJxOXUlMkJoJTJGQU9rJTJCT21CeHd2RThqZW45RUNwT0phZjExYk9xOHQycFhlMW94cFVvT285YmwlMkJRNE9YMnREWlZxOSUyRk5WbGlCa282JTJCJTJCYjhUbEdPREwlMkJ6V2xaRHZscnRnUmdWZFh5WjhlJTJCc1RNb1U0bXpxZjBaSHlEU0hudDVzR2RlZFNNWnNnUlNwT0t4eVNqQ0Z4V0FWSGZBejhON0h4Q1ZRTDRTRVRicE5Oc292N3dzbkdkTU1GQ1ZuckJ3NU11WW5xRW1PcVN0SERtJTJCbWlCOWNWNVFjU3pseSUyQkprUDRrZmxGU1hIVlk0Y2ZzcUUlMkJPRjhSY254bFNOSHdqejRlN2hwMmdmMTZGUWNhNWFwR210bWwzR2xNR3NDdVhHVTQwYkN0QTlGdWZHVTQ2YkRTcm1YR3pXeHR3M2xzQmN3MFVSUjdKVUwlMkIwMEJNMVFVeFY2NXFON2tvJTJGckJENlBrc0xFTWVlVHdVZjNnaHlsRERoJTJGVkQzNllNdVR3VWIzYWZ0aTVVVTJCcExWOU12bWs4ZEclMkJ2SVFhaXJhMHRuOG1uVFNMRCUyRmJsWmVKUWxMUzJyeWFmTk40RkdFaDd3MWFUVDVvQWUlMkJDNUhtbWMzU2FmTXdHMndnTTVxeWJBQ09Tc2JjUEo1JTJCenoyQkZ0RzA0JTJCOWgxZjJqd3A5c3E1RFZiWEJ4blBpYjF5Wm9MRm13bUREVWZXMlZlOThyamh2WVRCaFZPRkc5NHlHRXc0UmJpeGVXZGdLcHliY3klMkJ3SHpxcjR3R3Z4VzEzVGo2YnZHV2d0cU1xa0J0WE5XNTRaJTJCRFRUakQwVmVPR2R3QSUyQjYlMkZ6Q3RxVW1ueHNKQ2VvVnBjWlJqUm9CUmtCUHFmRlVvJTJCYnolMkJBU0dhdEFMJTJCTFU5UmFGWHpRV3dCV1M5VnhSNjFZSjhtdyUyRnlhNThQJTJCeHA4NVF2c1d2b2xmbE5ISHFZTCUyQlEwZW12V0l5OU5RZ0czJTJCQzN5eG5pdTdrWnBTYjN1TkJrc1FYRSUyQmd3QktvTlJJb21LTEU3dkN1eVpBVzZmWUVIR3Jxem1GVG5sa1hLem1ia3VGMGZSWWlJNTNTTzdJbzFWSkt3RmRrVXMlMkJRTTZtSDZqZjFqbHhMJTJCdmlodlM3dm9OMnJmeXg3eE8zSTZKTDZCV0Y3V2doTFFxeG5Yd3NEZGlXTDRsUyUyRmk5NUxVSXJKMmx2UDIlMkIzTHhqMyUyRlRLYzdlU1NaMHhpZnJQYldnNUk1NlRoNXl4UyUyRlBya29uNlduMTlvbmJsYWVYbXRmJTJGRzEwWGhDOHQ0Q0N3dCUyRlYzVTB5QmF0eWFKRDNOMGoyRTElMkYxQnVsM05FaGJYSU84WXVLVW1EeFM3Nk9JWE5URlJGUHZvJTJCUXglMkJhY3M5cXM1VmRvb3YxbkZ0Zm1uVERacjVGeEZvdk5QT1IwZTd1WDhVMmRlRm5oNWZkYjhVNlR0bmUwdGhPV2ZZbmt5anAzSEM4dyUyQjVWemhhTzQzMFE0dExnOUZlZ3dMMkQ4QTFCbThZZm1jdU1LR2M1cnNmcWZMNyUyQnRtcmhWS2taZVFnUnpKMEJjODBHYTNYJTJCSzRSNGJaRmNLd1RGOENIaGxkeVNKdWY0ZWpid0hqSVZDUU41aHJOaDh1MWRCRCUyRlNIcFBqSk9jTHZjbWFHbmVJUEY1dFBDdFBqWmxsMWRoZUVKc3p2Y2o3VTdhTU4waDY1Q1hsZGhORjlvTGZhMWpMeXVvbXNFbSUyQmhqdjR1eXpnRUNxam8wT0ZDc0YxJTJGUUQ4akFzJTJCdW52NzloRUhVOGtMQ0t0a2w2Skh2REtxSXQ2bEZvUlVXJTJCeU1zY2J0am1XZDdlU0NxRFc2SmxUcGFYOEcwJTJGUVNrMjZZWjhUJTJGcXA2bHkxUVF1YiUyRmxTRHZxZzBNR3BkdDRrR3kxQlY5UVZ5NmUybUExS3doY3hQb3pLcXRSNENVTk1Wb0tEaFNLOEJXZ25samJic0R0bXlQSkJPN2ZJNHpDSiUyRlJYZVVaR3R5ell1OGlFRXhnc1hraUcyU2paaEk4RDElMkZkUXF3SmR0MnNHMlJmak5vdlBHaWJjUiUyQlFPV29EWkt5UGxISzJWaE9lQzhwJTJCUTRVVVprWEF5TWZ3c2hvZEIwaFE5ZENuOHBEbjZLWWd0RTd5aURoS3lWTXJuM29nQldTcnpYSTk1SHklMkZRbU9MMUNLNnFyWHRNanZrJTJCa0dHc1ZFQzdwQ1BMWVp5UTRvY2htZWlXcXhVa01mallaZU1YUHMlMkZQc2gzZ2tOZ1BoNFZMY2FzYTFQYXRQUk1odU5kYzlQZUR2YmxkM1VPMXdOeDlQSGhPJTJCSXY5elBqc0ROajF1eEdxMDZobXl4MzlVdTU0bGUweDd3U3RRdmp2ciUyQkx2SXg3d2QzUHFITzF0NnZTVDYyZHQ0aGIzNW45TERKeTViTGo2dFlkb2ZuYmZuQ1BPOHJCdExmbXJVVFIlMkZ0Tk5RNTIlMkI5aFhCMEhWMkJmRXZUaiUyQkY4bmpxOE5XJTJGMGZyd0N2VFY2b2RzblpzREYlMkZjUE5uSDFNbGttSXQ3JTJCdDJjUDJoYWtHJTJCMlJsSGNaaFZYJTJGeXhkVzV0R3F5TFIwNEpjJTJGa3VwSkl0eEUzVDdOeDUzU2N6aU9waHF5aDhqa2FXOGZXdWElMkJnWGRuZWxmNEdxUm8lMkJmRVNRUkZ0TnY4bGNkbyUyQnRYcyUyRnclM0QlM0QlM0MlMkZkaWFncmFtJTNFJTNDJTJGbXhmaWxlJTNFRfJc2wAAIABJREFUeF7snQe4XVP6xtdVghARQRBED2NmGL33PgxjEAZRoo3eMowebfReBqNGJ3o3uhhGF70nhCCIEpEQ9//8Vv7fte7ObufcfVbujXc9z3lO23uVd6299/d+bTU1Nzc3NzU1OXtNMcUU/rO987m5udn9/PPP/jV+/Hg39dRTu06dOrlpppnGHzvTTDO5aaed1v8+1VRTuSmnnNL/znmffPKJ69Kli/v+++/9a8yYMe6HH35wP/74o6/PStg+5/OiLqvP6qQO2vrpp598HePGjXNjx471feFY2rT+UnfYd/uPd8ZHfznPXoyJOviPY2iD+unzd9995/vbtWtX/5pxxhlbxpx2POfYmBkv9cw111xu2LBhLWPmg+HEu323vtn4De8kFhxvc0Jfrb+Gi/3GWKxu3sO5Ndz5ffrpp28Zp+FmWFn/OK5nz57uo48+8nUapnyebrrpPFaU9957z80///x+Hpkv1gjtgvEMM8zg+2rzDD42n6wv6rB5ZW4553e/+517/fXX/XjDvoVzav2xsVr9vNM2ryRmtMf803f6SVv8xncr1h6/86Kv9IvP9BO8+Ww421rlfGs77IutMXtPzsfo0aM9RmG7Npe0xcu+W7vUQX2sleR6sfUJdpy71FJLuYceesiPoXPnzn6szD2fmWeOs3FZe8k2bR5sfjmfa4Jrg7m264Rrn//A1dYQ18Dss8/uMUu+WAtDhgxxs8wyi/vqq6/cqFGj3DfffOPAhHVh9w1bt0lc7Xva/cswY9y8mG/mHrxsnmwN0a/k2O1+FV6rttbsnpm2Nq2v4MA9ISwcT/u0xWe7H4Rr2dZseA22qkRfhIAQEAJCQAhUhEATxICH4o033ugF1y+++MI/kMOHsQkJ9mA0YYwH1ccff+zmnXfeFiHehFcTagcPHuw23njjFkHBBAbq//3vf+/efPNN/9D/8ssv3ddff+0FUx6eCAg8vMOHM5+feeYZt+iii/r/ERTs3PBBjgBAfQhXPPgRVOaYYw638847eyFl1VVXdW+88Ybr3bt3TTDSn88//9x9+umnvn6Elm+//db31wRFKmTsCB20z3hnnXVWL5SusMIKXhAyATVs3MZDXS+99JLr3r27H59hwJhC4dMEkZA8hCQHYc+E3dlmm83df//9bp111qlpvBxMv4YOHeqGDx/eMm7mzsgd/aAPCJWMF4EOoW+ZZZbxWA8aNMiTw8cff9wLnGAHqWCc4Me4OI6+Ijwafiac0g5zzHeETBM8Z555Zt8W2NIe8wthof7tt9/eY/jZZ5+19NnWlmFqAqkJwkaAuBYYH/WZgE2/whe/06+5557bt08/ELT33ntvf+0wZ0aAbR3zWyhs23zSDxOyTTAMhV6bX2vfSIwJ89TPOr7pppvcH/7wh5Y1Q/0hUaEe6mBdIsAb5jUviP8/AXyXWGIJd9ttt/m5Q9hnXpnrESNG+OskvJfQH9ZIKIibEA0ujIM1QV1cr6x/m9s555zTzTPPPP4+wxwvueSS7rHHHnP8zlxxz7BXUgFhuNOGEQO7j9GmKTzA3JQRYERfWW/dunVzPXr08HO67bbb+vsRWJYtIXFnvZtSw4iw9cneX375ZU/caN9e9OPtt992CyywQNlmdZwQEAJCQAgIgboQ8MSAh/Xll1/utt5667oqqeek5557zi299NJeeEDIi1U+/PBDL2AgvCB4xCqvvPKKJ0IIKLUIFm3tH+0xv6effrrbf//921pd6fMR1BDin3rqKU8Ssgr9g1yZlQBBmYKQRr95N9KRRqiS9V599dVegKN9hN9Y5cADD/QYmyUkVrto11lXJ598suvfv3+sZt0NN9zg+vTp4x599FFPtIsKArURaCNFNs8QLQRm5qtojiFe3C8Q6lkfscoDDzzgNtxwQ3+/gljFLOBD+6uvvnrMZtWWEBACQkAI/AoR8MSAB91RRx3lEG5iFTSsa621lkNQx1IRq7z11ltuscUW864uaHxjFSwnq6yyihdoTDMeo23aQwu7yy67uIsuuihGk74NBDgsFbfeeqv74x//GK1dhPODDjrIC3Boe2OVTTbZxN1+++2e+CHIxSoPPvigtwRBhq688spYzbp//vOf7tBDD3V33XWXF5hjFSwSWA0gfhDGWAUitNVWW3kSG5NwMj7Geemll/r2VYSAEBACQkAINBIBTwwwle+www7upJNOamRbrepGoNhoo428K9HCCy8crV1M9WiwX3vttaimecb7pz/9ybvFoB2NVcxffbvttosqODKvq622mhcgd9xxx1jD9cLqiSee6F1aWNexyrLLLuvd3GJrsq+99lpPCnA/+d///hdruO5vf/ub+9e//uUtB1tssUW0diH0Cy20kCeeMTX3l112mevXr59799133XzzzRdtvDSEa9Uxxxzj9tlnn6jtqjEhIASEgBD49SHgiQGuNWuvvbb797//HQ2Bm2++2f3lL39xL774olt88cWjtYsL08orr+yef/55H6sQq1xzzTWub9++3ic6pqYTDScuPZtuuqkD81iFdnH5OOGEE6K6uOyxxx7uwgsvdB988EFU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hg3zwnA4XvucfDcc+P3bb7/14w+F8BC7tM/hsVgTsA6ZUM647XPy3f4zIhdajYyImNWHeYG48TKrADjzgqTwguBAInlB3HjRF+pSEQJCQAgIASEgBITA5IpAaWIwuQLQEcaF+8qGG27ozjvvPHfYYYd5q0ffvn3dLrvs4i0EKkJACAgBISAEhIAQEAJCoK0IiBi0FcEI52M9QJONpnzrrbd211xzTYRW1YQQEAJCQAgIASEgBITArwkBEYMOMNtkvcGXfY899vBWAxUhIASEgBAQAkJACAgBIVA1AiIGVSPagPo+++wz16NHD3fllVe67bbbrgEtqEohIASEgBAQAkJACAiBXzsCIgYdYAWcddZZbv/99/dpY++5554O0GN1UQgIASEgBISAEBACQqCjISBi0AFmzFKXkhnnpJNOcrvttlsH6LW6KASEgBAQAkJACAgBIdCREBAx6CCzRYpTgo///ve/e2JALn0VISAEhIAQEAJCQAgIASFQFQIiBlUh2eB6dtxxR0cQ8u677+5OPvnkBrem6oWAEBACQkAICAEhIAR+bQiIGHSgGe/Xr59jV+qvvvqqA/VaXRUCQkAICAEhIASEgBDoCAiIGHSEWQr62L9/f3fKKad0sF6ru0JACAgBISAEhIAQEALtHQERg/Y+Qyn9I2XpwIEDO2DP1WUhIASEgBAQAkJACAiB9oqAiEF7nZmcfj3zzDNumWWW6YA9V5eFgBAQAkJACAgBISAE2isCIgbtdWbULyEgBISAEBACQkAICAEhEBEBEYOIYKspISAEhIAQEAJCQAgIASHQXhEQMWivM6N+CQEhIASEgBAQAkJACAiBiAiIGEQEW00JASEgBISAEBACQkAICIH2ioCIQXudGfVLCAgBISAEhIAQEAJCQAhEREDEICLYakoICAEhIASEgBAQAkJACLRXBEQM2uvMqF9CQAgIASEgBISAEBACQiAiAiIGEcFWU0JACAgBISAEhIAQEAJCoL0iIGLQXmdG/RICQkAICAEhIASEgBAQAhEREDGICLaaEgJCQAgIASEgBISAEBAC7RUBEYP2OjPqlxAQAkJACAgBISAEhIAQiIiAiEFEsGnq6quvdo8//rg744wz3HTTTRel9cGDB7uVV145ta3FF1/cXX/99a53795R+qJGhIAQEAJCQAgIASEgBNonAiIG7XNeGt6rL774wm2zzTZupZVWckcccUTD21MDQkAICAEhIASEgBAQAu0bARGD9j0/Devdscce67AkYMHo3r17w9pRxUJACAgBISAEhIAQEAIdAwERg4rnacyYMW7//fd3F154YUvNTzzxhNfMU0JXoptvvtltu+22E/Ug6d6DEH/kkUf646pw/XnzzTddnz593HnnndfSr4phUHVCQAgIASEgBISAEBACHQwBEYMKJ8xIQc+ePVvcc9DK77nnni1+/HkxBmnuPUnNvsULGNkISUNyKOutt16qRYBzhg8fHjXOoUKYVZUQEAJCQAgIASEgBIRAAxAQMagQVBPst9tuO++/n1byiEFSYM/S7LdFsLc6+/fvn9nHCiFRVUJACAgBISAEhIAQEAIdBAERg4onyjT4u+22W6pGPosY8Pspp5zSKkMQvw0cOHAirT9WA9qpJz4gq86KYVB1QkAICAEhIASEgBAQAh0MARGDBkwYwncYO3DMMce0uBalEYMsy0CynrCrWW5CecNJc3VqwPBVpRAQAkJACAgBISAEhEAHREDEoMGTZsL9VVdd5V13ksQgL21oGe1+LTEGZVydGgyHqhcCQkAICAEhIASEgBBopwiIGESYGIR3CvsFJIlBXrxAMnDZulrvJmlYJvbZZx939tlna0OzCPOuJoSAEBACQkAICAEh0JEQEDGocLbSNPJJN6FkutJkXEGyO8msRG1JNdqW2IQKYVJVQkAICAEhIASEgBAQAu0QARGDiifFyMF9993XUrO5EfGDEQOsB/369XPhcWFXwr0Pku5C4X+1dL+Ma1It9elYISAEhIAQEAJCQAgIgckHARGDyWcuNRIhIASEgBAQAkJACAgBIVA3AiIGdUOnE4WAEBACQkAICAEhIASEwOSDgIjB5DOXGokQEAJCQAgIASEgBISAEKgbARGDuqHTiUJACAgBISAEhIAQEAJCYPJBQMRg8plLjUQICAEhIASEgBAQAkJACNSNgIhB3dDpRCEgBISAEBACQkAICAEhMPkgIGIw+cylRiIEhIAQEAJCQAgIASEgBOpGQMSgbuh0ohAQAkJACAgBISAEhIAQmHwQEDGYfOZSIxECQkAICAEhIASEgBAQAnUjIGJQN3Q6UQgIASEgBISAEBACQkAITD4IiBhMPnOpkQgBISAEhIAQEAJCQAgIgboREDGoGzqdKASEgBAQ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Sy9FFeBefPFF94c//ME9//zz/j1WwV2N9YQLIoQ7VmHDwDvvvNMTg5iF3d233nprd84557g999wzZtP++nn44Yc94VURAkJACAgBIdBIBDwxQBN81VVXua222qqRbbWq+1//+pffRRmNYcxy5ZVXuh133NFrpdFExir/+9//vMXg+OOPd4ceemisZr0GE60jmt0FF1wwWrtXXHGF22GHHaITg8cee8wLUJBJrDaxClaoBx980EGI2LE5VoHorrPOOu6+++7zhDdmwbKApYJYg1iFGBy092joYxasFP/4xz/cgQce6AlgzIKyA0LCGlMRAkJACAgBIdBIBDwxwNR9wQUXuJ133rmRbbWq+9hjj3WnnXaaF9BjFvztzzjjDO+6hPtBrGIC3L777uvOPPPMWM16tyhiNNDsxnRFOPXUU31sAy4mjQ4kD8FkHe+xxx7epQa3jFhljTXW8C5wl112mVtppZViNetMk3311Vd7jXbMgkLhySef9K5xsQpuURRc1WIWyPyJJ57o/vrXv3olSsyC+yAKBa4nFSEgBISAEBACjUTAEwNccdCIIbTGKuuvv74jziA2MUAo5wGLa83cc88da7ju1ltvdX/+85/ddttt57BaxCpGDCBCMcd78MEHu5NPPtm7isUMmjz//PO9qweCY5WZjorm63e/+50P2kV4RIMfq1x44YWeCJ111llur732itWsbweFAhaStdZaK1q7WPmYVyxgMctuu+3mLrnkErfeeuu5u+66K2bTPn6G9lGkqAgBISAEhIAQaCQCnhjganLkkUe6Qw45pJFttap7l112cffff7/X3McsZ599tjvooIN84CDpCmOVa665xm2zzTbuT3/6k7vttttiNeuJF0GOaNBJNRmr/O1vf3O4i8UmBkcccYQ77rjjfPB0TIvQPPPM4y0yuJpsvPHGsWD2hP7www/3bi7EOcQsxK7ccMMNbpNNNonWLG2SnvWZZ56J1iYNYY0ZNGiQT5hAooaYhZgpAvkHDhwYs1m1JQSEgBAQAr9CBDwxQCOFQDNgwIBoEGCSf/bZZ6Nr/s477zxPDJ5++mkvYMQqF198sdt11129//sjjzwSq1mfMQVCQNB22Uw3VXSOIFEIEO3jyhSr7L333u7cc8/1hBNhPVbBbWmZZZZxO+20k9t8881jNetJAZpk4jlwo4pZWE+s65i+7xCDFVdc0QfjxiyQH+I4iHHA0hmzkFmNuBXa/zUU3Ewh2ShSVH59CAwePNiTYFx+Yz6zqkSa5x7rF0VVTNfSKsegun69CHhigOC2++67e+1jrGngniIAACAASURBVLLpppt6d56XX345VpO+nYsuusi7XCCcI2DEKghvuDAhWJBBJlZh4ypStdqu1LHaJeMUGlay18R0YUKji+AWO1sO5Jrg3y222CKqr/9+++3n4xrYLBC8YxbGzLrGzSVWQXtO2tDY7jx//OMfPRlhYzsSCcQsCMnEVjzxxBMNaRZBnIIQQyFehXuzfc9rFAGI++nRRx/tN6600hbhrhHEgKxw9BGlAWsoLIz38ccfbyWIZo2rIROQUakJlyEhJL6lSsIELvvss4/Dkh7On62DJC4xxl/v2iGRCQlNsBSXWbvhWLLWHPjgQojSNIukcEyfPn18dcR8gSNrCnLDe3K9lcWwkWuQfpFEwfpb1Kf2eo0U9Vv/14eAJwZkvSCFZsygWHx1cXNBcx+z4N/fr18/L1jEzOJy1FFHeRcXUjvG9I+GhBAcahtaxcIa4gfGCFEx02hCSMh1D/GLmd4R33fcPUj5SxxJrIJL3k033eQzTsV2ryEfP8LWAQccEGu43t+e+CTGHLOgsWcvEIh97HsWWZ+I5yAVbtUlTbPZVmKQJ2xa/02II0amlgIJRZOMBRQBOcuKYseZMJdFDKwfq6yySiuBG1wg2sQsZQlPCLC290fZMYSCfZrgH9bDmku2jaIHRQtzVK+lLuxD1lwbLtzLsjTeRf1PYpIcD8I4Lsy1FOSGLGG7LYK0Cfco74x42W+QAmSFkBiE+Cf7lIdLeGzWHNr81DKePOKbxNfGxf0E99MiEjUpr5Fa1oaOrQ4BTwxgtDBeboJlS7io0WTVai5DaGMjozJuNWUvtDJ9v/baa/0N9eabby7tG12F5gZNBloZAifxfy8sxHtkWXD++lfnLr7Yuc6dC6sh6Jm5LZ33/fXXndtgA+fSYj8OPti5E08sbJMD0LCSvpOc82izSxV8t1dfvfWhl1zi3E47lTqdg/Dvh5C8/vrrE2nAMiupoF2IAaQAoTXmPhU8xEjRirtJbGKAQgFSUPRgKT15JQ6EjDDH3H9iFoguMVFseNYozX3WeGiTJAJvv/125UNGuCVYPxRA20IMQqEjrbN5gp0d31aLQZp2M0twKiIxSWtKOKakZjvZbhLH5LhqEfzKTjx9op0iTXXWPBmhYrNJnhtJMppGVsr2rexxZS0G9RALE7rbQqxCYTptXdEvMtQlXaGyfs/Cpez6MPmEeorm3Y5FXiNpRRl3p0l5jZRdMzquWgQ8McAHnQffv//971K1J7U9ZVhnsmJy+hMUy87HRaVIM5HUDuXVZxucEQxcZt+GvAddLePGVYtdUxFs2DW1MIVnRcTghBNO8Jly2CiuVKmIGKBhQWBlQ7cyOLu88dZASMiQQ3AoG52VCi6vqF3c8djQDatB3759S0FdxUG4w6FFhNyz2VnMAjFgbmPGNoAzO0zjPhWzQEbYHRrNMu8xCxmvuGeQQKDKUo/W3pRAJuRChM2VaOTIkZ5kEMcFmQk1rGka2ayxxCQGJsxzfyZOp4xVxoTLKiwGaW5Y9c5xlmY3rb40gTYUyEk3veaaa7ZS+BUJiLX2u9b1lySVta6TWo8vM54kjuZCRF/ZZDN0zyvrWlS0rkJFbHhsEek2vBmXkZY0xUBy3JPyGikzBzqmegRaiAEaXjalKlNsMSKQ40NOKWKqyXpxL5l33nkdOyAXlSxGbL+PGDGitK/cf//7Xx9bAAnCpSivhDeu0Pxq469Fe4IWGWsFqWFLCekmsBKo3IYdTyEG5EAfPXp0EcwT/jdiQC7+klaJtIp5qJDjnnEXuguYxr5XL+cgiosuOqHKSy91jjlK/p4zEnzAIQW82Gk6t1TYLoL5qquu6gi6rtfEX26CWh8Focc6QkrYV199tZ4q6j6HgGtcDU4//fS666j1RJQJYEzQc8xCViKsjJA/rHAxC+sKa8Enn3xSabNZftBlLAZ2bwSP6667zhNE3vHhJ4Ut1wACDAQBaylxP6FVosiykDXQ8J6bV0cZV6JaBOlagC8rgBYpvLLatGdRPRpzU2blEQOuL9yokhrvqolB1vhqsRjUEqSenJc8q0G4ds2dKjw/C3tbnyS+sHgH+liLP7/hksQ76fZncojtq5JHPOxcZK7kvOaRg0l9jdRy3enY6hBoIQZofspu3GMXBRfPQw895P0Ea3UnIoMLftEIy0WliBhwflligsC42GKLebceMtjkFXvwEOyYZhZMalTy6uLByc0WYoBbQGGpiBiQxpIc9/jklioVEQOEmeeee86n0SRzTm7JGyv/4dpUkhzhA05AO+loC3fkrbBdXMQQgniIlLKQlJqM4oNIf0ugNWlhG+FqktcDLI24T2EVilVoE4sBSQRiFpQJxMvw4Gddxyyrr766J7pVWgx44BP3hHIkLei0iuBj/O+zlCdpgqnd57mG0gJsk64VWW4zZV2JQsGK9vIE32TfirS6eeujHh/ytPpCQTUtViRNm23zmkcMsGrjGpkUusNzjPzVcx1ATnh21hqfYW0ZuQnHnzUf4fpLIwbJdR7iaKQ2jRhYX/KCjIuE8azxW59pIwwMz8t0lNcPk2MgfGbBSLo1GX5JOW5SXyP1rC+d03YEWmIMcP2oR0gnII8FXotbDd3GzYOHbRmhokizUgspwbqAEEcg8GGHHZaLYPKiaAvcXOxDhgxx008/fW3EIK3RGvzuubEgRP3www/lup/lSlSD1p6GWBMvvPCCYz8DzNKZBcKyyy7Ovfuuc3fe6Vwb91pYdNFFfZAoWGM9iNUuGiKILmSTjexiFVxcsNpBNs16F6vtHj16+DidmEI6sRSQoZhtgif+uFi+0ALmrucGgI97HGT3888/b0DtE1dZxmJgZ5mwzoaG7Fti1sHweZCmdUwKpggq3G9DBU8yc0qSGNTis51sL80anKcdLeNyYZjUYjFoiytRo4hBGNwdptvMC3DN8rUvo9HPEqBtPpLWpjSc00hi2noJ+5O2zmshBtY/7rvhug3llaIsUnlB3klM6yEGZhVJykhp104Yf8C8t4drJMoNT41MhIAnBjPNNJPf0RNTb1ExYdlu/LUEvoR1k51njTXWKBXXUEQManHpIW0n/v1cGEWa7ORYi7DJ+x8tJ25Ts802m/cXLix5vu81EAP2ToB8jRs3rrBJf0BFxADNPRps9qvIdfswYjB48C9uRPbbNdf80ueSY4Zw0i6+wrn7VFTcLqQA1xq0sFjfYhWIAYGC+HcT8BazsJZxZYoppJOKEPeVsvFQVeGB4Is7AAqFQw89tKpqS9XDTtqs5yotBm0Jvkxm1ikSbovcEbLcMvJ8pmtNTZnlC45rRZiRKM3awCRlBSHXYjlIKs/KBpdmLZI0YpDM0pTMghNaDNKCi0MXrKQFJS+wuV5iUOQOBWbsO4TFO5n2M2kxSAZdlyEGWW6fRa5EzIlp4vmMkgSNPFkAIQrcn7hXJElDci6pIysdahLvvPWSZjHII855/1ldKLiQWSblNVLqBqmDKkegZYMzYgzKEIO8C7mIHYe9x3yNQM/OqUUlj3xYf2ppe4oppvCabILk8kqRK1EZbYjVjwB39913+xzLCHKFpSJXIgLquNBxNSlVKnIlIoYEn3c0yqQPzS3JsbaBGDAn77//vg/EZX3FahdiQLAlgbj1mshLzU/iILMYfPzxx34zuZgF7T0uY2Wu4ar6hWUGDXrs4GPcJbnXkNJ53333rWo4perBpQEB48svvyx1fD0HJYXAImHe2gATXCTz8qGXrStNA5slwBQpi4piDNCKkyiAtRvex9PcifI0tWX94bO002HgdtF9Iy3dp/W9Slei0G02xB+hNyl82zpIw6Gs5cTqCGNGQg039aS57VZBDNriSsScQth52f3BLCx5xDuUVWwMKA6xRiZJati/PFe3PFeitPtBGWtbe7hG6rmX6Zy2I+CJQadOnbz7QxExKAoYqyU7EMSAbBtl8pE3ghiwQ22R1rEo+Bj4y7ox8RAi3SE38lL7GFREDPCPJAPT+PHjy62WiogBG43xICH7FNmJcktWEDAnWQBySYsBbmK4i9F24f4JFbaLdYKg8ttvvz3qjtoIE2jTzGpQbpKrOQoLCRaDmIHACy20kF9TZeOhqhmp81YgtLHnnHOOz8ITs2Ax4N5bSqFQZ8eS2skywnyYhAElC8JGmd2Zk8+JZBIJhpCmzS7rrlo2xoB2ksJr2rjzNOVtsRiEWnbcH7OEbvqZpi1upCuRZZQK28UqmbUjcRrmZYmBCdFJa0VyDaS5wxgxih1jYLiEQfdm0cjy10+SN77jzkxyEM4N10Pnzp0nIgqxiUFI/kPyHPMaqfN2ptPaiIAnBmQ0waRW5O9vF3CaSZTgrVqyA+ELDjkok+GjSDtUiysReGEx4IJGYC4qeTf+sg8q2kCwIFUq48b/vbDkuRItt1xpf3zmlb0E2EyuVKmIGJAnmSBN3tnPoLDkjbeG+AYsMmRvefbZZ30wcGGpqF2C6XFhIkMQ5CRWwd8ea8HQoUOj+aDb2CYFMSBxAEHlhVaoiieAhzeuh+z1grUxZmEfEKxg7xKH06CSdJXJIgam+bbgUe7fZCOynY/TXCPySEaWBTpNycS9mGQXRftmpLn9ZPnHpwmvSSE3T8Bti8UgPDdPG18LMajFlSi5E3TRWLL+z5rfNNxCTXXeJnVpz/Sk5aDIYpC8VJL9aUtWIrsO2FAzxNHkBa4L4oJwg4Jkpbm+hf0JrwOUHrjvJIlieyEG4BrrGmnQ7U7VFiDQNGrUqGZ8hdGCnXbaaZmHh9rzNC15rS49BIb26tXLb0ZVVPKIQa2kwIgB/oBlhYu09mtxXaJNBEcEZfpLUG5hqYgYYDHgIibGAAJYWCoiBphE2SEWywH7CpQqFWw0hnsLvths9rXUUkuVatZV0C6+vIwTdw+0PbEKlj40yZAhCELMMimIAWRvrrnm8paZmOWf//ynjy0gnoLdpmMWiAGbIqJVbkRJc0PIIwYIKFxj3FtICZyMMUgKDWWsD+G4igTUIgzSBNJaiEEogJEFKy+Goi0Wg9C9KM8qUQsxyAsWDtvLy0qUzMBneGfFX2QFZmcRA+rLI3dZvvT8DjE3YbusRcL6n0YM8lyJkpu2hudjJcX9ByuKEQM+WxYh1s1JJ53krcgoFHbeeWcv7Bu2Se8Lk6nAkpS/FDK+hdm58tZII1yJsnDj91jXSNG1rv8bg0DTp59+2jzffPP5bCpshBWr4OaBYIF7TeyCxYCYijvuuCNa02R9wmKApo33WIUYgyuvvNK7m5AqNVaxjcaWXXZZv59BrGLEoLTFoKKObbHFFt7XmuD2mIUHB7EcPIB4yMUsPPwgJjFdichkRmav2JuMDRgwwAsABCAjmMQs3DMQispsvlVLv4oSR2QJdqFbQZYQF2p3i4hBWpCruaywd0QtOeCz4gFqIQYhhkUZmsqSmGQ9yWw0k4IYFAUfhzhkBXubgNu/f/+JUswm14/NTTIdbZqLjZEx+hCm7Az7FJMYZK3hvExNWa7IRddolv9/nvAfmxjEuEaKcNL/jUOg6cMPP2zGNM/FRxR9rLL00ku7qaee2rHhWOzS1NTkfaPLbK5WVd/QKEOCcGEqkxa2qnbJSkTWg6+//trNMMMMVVVbWA+ZYzBr8xAou3FeYaUlDph77rm9drVUjEGJ+soewkZuxOiUTgtbtuKC49ixFW0Thb0bYhawxjJUxiWvqn6hPR87dqx7/PHHq6qyVD34AmM1QJtH6tKYZbXVVvOuCOyjUFUxC29ejFSaNjyZKahMZp08oQrhlBIGLyc103npH9PcQdJcPIuIAX0ouzGhbYzJfbWegpsULigEPoc70NYTfEzQay2lzAZn9IlCMGy4OWVy7g37LOt5Wkxi6CKWnFcSGXBPCeeKfrCzOwoulD60ab78ZYhB6KKT9C5IWlCMKIXjDK+BNO+EvHXF3NTibsxYkwQxy7JQy5ynHZtFPrKORRkQ+xrJsly1dew6vxiBpvfff7+Z1JLcBEi1GKuQqpTdeKt82JXtO8QATSfaqFgFC8U999zjhQozFcZoG8JHe7i4kJY2VgFf3D1YWzE3hCI7EJpzbrC4McUqzCsEqPQO0xV1DE0dOPOwjGmZofusp759+/rNAmMVslxB/GKuKcZ2yCGHuJNPPtlnnUK4iVlwQ8TaF5sMlRljHjEIhbKkUMl/YTajMgKQCZK4eBTFGST7XkQM0jZUKzP+eo9J+su31WJQph9F1o8yddgx9J8+h4J6LecnrQehdp160gTqLFemWtqt+thkALmRu7JJSaruT9n66iEGsa+RsmPRcdUj0PTOO+80o73HPF604VeVzfOAZ8dW3CBiF4gBrh8x0ywiKN92220OQQ7fw1iFnYdpD59gXD9iFW4iaAHxCY9J/tDqoDknSBFNa6zCvCI0fvfdd7Ga9O1ASCCcBLWTDjdmYYdUhGRcPWIV1hUxOuwEHLOQxYzkDMQY4C8cs5C9DXfP2HEVMceotoSAEBACQqB9IND09ttvNyO8xXYlwvWCYM3Yu7UCO8QAszF+rLEK7eFyQR50sI5VTjjhBB/8xO6R+PvHKgiMpINFOEdIj1XQ2OCeRiak1VdfPVaz7sADD/Q7v8a2GKCth/jhhx5zPQMsvv4QInzvYxUyAt17770+S0/MglsArpZYhXCPi1kw4+OyFdMlL+b41JYQEAJCQAi0HwRaiAFmcvyVYxUEZQTG2JlUjBgguCLIxSpodmkPc+jWW28dq1m/iRuBXKQ6ND/BGI0jMJLliliOmC5bCFBGDGJaDCB8ZK0hyDtmgQzgBohLz+mnnx6zaTfzzDP7tmt162hLJ7GAsbkZqZFjllNPPdX9/e9/96k58Q+PWUh/yw7ieVnjYvZHbQkBISAEhMDki0DTe++910zqUDLXkMIzVoGIoIEjm0rsgsUAAQNteqyC1p5c6Giy0e7GKlgpcL/A7x53hFiFDFcIyhAwXGxiFVw+0Kzij00Gm1gFNxOIdezgY/aogGiyvg4++OBYw/XtsDEic2vBmDEaR0DnOvrqq69iNNfSBoGmuBCBN/FCMUu3bt18jEPs+Y05RrUlBISAEBAC7QOBpmHDhjUTsEnGnJgaVjTnCHFkGIldIAZEvO+3337RmmbHVFyIEFiLsk9U2SkyA7G5Gi5b7BsRq5gghRAHQYhVcGshsIp9DEptcFZRx8g0hdb+xx9/rKjGctUQAEhqWFKGxnZxYV8MiGdMDToWEshmbMsMGczIW477I9lTYhb2xcDayPpSEQJCQAgIASHQSASaRowY0cxusezSR9rSWIVc/htuuKHfeCt2gRiwudnmm28erWkTLMhisPDCC0drl+wtBJfjshVzR14CYdGsIjCTojVWQXAkfoXNoGLizE6XBLTHJgYE4f7+97/3xD6mJYr5ZD+Q2NmfGCfrKjbOZHwiGw73SYKBYxbSOkPwY89vzDGqLSEgBISAEGgfCPidjzFV47PLDsixCq4tCyywgM9ZTLu4YPAZdxdcFKaZZhr/zosHY5UFYoDmj5zJo0aN8m4J4bt95veffvrJ981epFXjM7sSYvUYP368a25udlNOOaXvM9q9rl27ev9r8i6zSytjok1cetihtkePHhMNhzoQdqijrQVtKi/q+vzzzz3OjCVmulKyTeGiRowD8/fpp5/6lKkE54Kf4YZwieaZvrJ1PC/+Y6MwMAE3silRR/gCK34nM469mBuyL0E4aS9vPdMGGNEf3NnY54H+cR47WIIXv3MM/WUd0B/6a/PM2mQ3S9YRfSHY+a233vJ1gLutq2+//da3Y2sHKxn9t3Ey34yTNcQYbd2TopK2aYPPYEPbc845p+Oa5TVkyBAfx0FALnWQypM1ljYOSLiNgcBh1qphzjuY9+7d269PXvSPlK/gmHYN0h4ZoPifMVE/OFEPL/4HL8bFHFMH/WcstM//tRbGCxFisy+uU+aMuWOuyAjFfIGz9cdwZixWwj7ZvYY+gQf9Yr+PLl26+OuYawacmT8INkSMjRltjLZObQ6TY2bcbd0/hP6yrrDsqggBISAEhIAQaCQCTePGjWvm4cjDm4cjDzF7ICLc8qCzBxsPVx78PHQRMPjMg9cevjygOZ7/efGg5jv/2+8MJnyY2gOVByh9MGEw+eAlH/7rr7/uhQuOteN5aFK3CRl2Hn21/tJPXkmB04RSEw4Qjkw4QDCgDfLDmxAVvnMsAghjpE3DAkEO4YSsKXw2gZjjOCZZQuEIjT7HIzyZAMXxtEtfaZM+2TngCs5GWkwoMqHMcDZhEOxMwGSczGs4Jv7jZWSM+bBi84zwZ2M0wTp8N6HMBMQkxozLBHz+s3VEnSbYIYghkDEH9JM2OdbWjgn19m7j53/6mbRCJQVQW2O2bqibcds6pR6OsbWECxZEluPsxbmsDYgIxyE0Pv30062EYRP0bb2Gazesh7rCdWtriXdIBfXY+mXM1JM2Ro5LCrrgR93gae2Y+561E84Bx1K3XdNGiuw65Z05JBXtn/70p5bx2hjDd+riWMPS2rM1a3219UD/6aMdz1jpR4iHEcpQALfzjVDZuykX7B2r2TzzzNPSBu3Y2K2tUAGQJHJ2XYVt2zzadRKOlX6HZDa8tmw9Mz5TCoALdUNC7F5l1zDf7ZxGPhBUtxAQAkJACPy6EWhqbm5u5oGESwBaODRT7DSIgIqgb4KvPRR50PGAsgcegoA9iPkdLTkaXMgFfu34PyNA8WBDs4hmFS06AimCHw9BXrh+IBAiCNEmG6CgcTVtoPWF/3h4m9bVBCrTAppWEoHItH60T9u4TCHkmRBomnUTqE07HAoEpnkMhSUTTjgezaq1Hb6jMUZYBA97gcvw4cO9Ww8WGtMso/VE+xlqPWmPsYENBM2ErFDbyfgMR4Qfxoc2kxe/m+UCQsGcQlbQKJs2mTZNm22YmtY3FExMKDQh37TaRqIYF3NHu5AbhC8yIC2yyCIe61oK/Rg2bJjHyLTu9JHfEaLAgX6w5ozIWvusLdN2Mw6bMyMp4ThMSLZxDh061Ft2TLMdCvMcS3vtpbAmk/1JCrSsYXuxCzRzEZIR+4wGHtKd9h8WPLTzrC0jCkYMWHvgzZoCQ1x8sGRAlHgxdxB5+pl2nbHB4U033eQhBV/q4FhbU6xdrltbU1hlmB/cw7BEmYLCxh0S5KzPDzzwgI/vMWE7JGN59w+uP8ZKfxgT90iIImvG1inXEvcms8rYOgpJD9ck381Sw/rleHAzKwV959phTdMu65n7JXirCAEhIASEgBBoNAKeGDS6EdUvBISAEEhDIHTFq8e1SKgKASEgBISAEBAC1SEgYlAdlqpJCAgBISAEhIAQEAJCQAh0WAREDDrs1KnjQkAICAEhIASEgBAQAkKgOgREDKrDUjUJASEgBISAEBACQkAICIEOi4CIQYedOnVcCAgBISAEhIAQEAJCQAhUh4CIQXVYqiYhIASEgBAQAkJACAgBIdBhERAx6LBTp44LASEgBISAEBACQkAICIHqEBAxqA5L1SQEhIAQEAJCQAgIASEgBDosAiIGHXbq1HEhIASEgBAQAkJACAgBIVAdAiIG1WGpmoSAEBACQkAICAEhIASEQIdFQMSgw05dfR3/4osv3GGHHeaOP/541717d5f8nlcrx55//vnuoIMOctNNN11uB8aMGeOOOuoo169fP9e7d+/cYwcPHuweeughd8QRR7Qcl/ab/Xnsscc6/r/66qtd586dS7dj59cy5vpQ1llCQAgIASEgBISAEOh4CIgYdLw5a1OPs4TwDz74wG2zzTYtdSPYn3rqqW6PPfbwBILCucnjsjpTK4nYf//93XbbbedWWmkl9+abb7pLLrnEDRgwoIWAUB/9u++++9xVV13V0lfIwbbbbtuqG7vttps744wz3PPPP+9WXnnlVv898cQTbpFFFmlFjtoEqE4WAkJACAgBISAEhMBkgoCIwSScyJ9++slde+21XiCOVRCY559/fq9lf+mllzKbRYCeZZZZ3NFHH+3OPfdcr5lHeL/wwgsnOscE8ZtvvnkiIT2tAQT7pZde2vXp0ye3D+G59AfSEJITPmM9gBwYeeE74wtJTlgP/x955JGturXeeuu1qiPWXKgdISAEhIAQEAJCQAi0JwREDCbRbGy22Wbutttu861/+eWXrmvXrg3vSZoLDb/ttddengCkufyYID7vvPNO5O5Dh0NBHQGdkiWU81+ZY9KAwIqQJBII9GeffbbbZ599HHhiIVhllVVy26fuEAe+h65VDZ8ENSAEhIAQEAJCQAgIgXaKgIhBxIm57LLLvIZ72LBhrlu3bu7bb791G220kbvpppui9AKhfODAgRNp2NGghxr5pL9/Ml6AMay55poTueSY0L/++uu3uP3YwEwrf++997aQhzQ3oGOOOca7L5mwzvGQEqwFlKRFACH/pJNOcvfff7+7/vrrW8gNfU6zcGDdOPzww91xxx3n4yxEDKIsPTUiBISAEBACQkAIdAAERAwiTNKuu+7qhdbRo0e7JZZYwu29997uhRde8H70H330kRs3bpx//fjjj27s2LH+nReuRvbOZ3uNHz/eha+ff/7Z8aKOKaaYwn/m1dzc3PL67rvvvO/+119/7V2DcL1B2w9R2H333d3DDz/sll122Ylcczjn7rvv9kI2xQRuiwcI4QuJQVaAc5IYcL5ZGKytvn37phKDMM6gf//+7ptvvvGuTVgSFltssVbBy9avtFiHMIbh+++/b2mLYylNTU01v8Ddzkv7zG/2e/huv0dYhmpCCAgBISAEhIAQEAK5CIgYRFggXbp0cT/88IO75ZZbvIWAgv++CaJFXUDgzCv2/9RTT+2JhAm3dg7/QxLuueceN2jQIK8pHzlypBeozzvvPLfkkkt6wZ/A4tBfn/OJSdhwww1bNPHmhoPbkZEFa6ceYpAMHM6zGFD/e++953r06OHeeecdn/GIknQxWnzxxVusB5AfDfDoDgAAIABJREFUCmMzEhIGYIduRb169fLHgJUV+5z1Hh5f5phk/Wnfi9aD/hcCQkAICAEhIASEQCMQEDFoBKqJOl9++WXvA//hhx+6NdZYw40YMcK/sCC88sorzgTSRnfFhGC0/QjgCNCbbLKJd9NJ8/1PWgvon7kRQSzI7hPGJdTjSmTCOu95FgPaIlXq8ssv7z777DNvZUDAJ+uQuUFZHZbRiO9YRBgvlgFLtUq2JVyhGHdoUcBqYiQrS/sfav6nnHJKbwWwF9/tN/vM+1RTTeV/t8/2nXd7FZG/Rq8N1S8EhIAQEAJCQAgIARGDiGvgzDPP9G4ruPngUgRhWG655XxQb4xirjiQElybnn322Rb//WQcQVq6UtPYs99AWiBzlsUgHFtIQGqJMcDCQp8gU2j/yWpEwDQpTQk+tsxOYQyFBUZbBiT6wfHXXXddiztVWmrUGHOhNoSAEBACQkAICAEh0N4QEDGIPCP4+JNJB5LAZ4sHiNGNpDCPYD7bbLN59yKy+SBAI2TTPywCtmeBxRX07NmzlR8/QrUdj+WgTMahJDFIsxiELkocHwYfp+2lYJYDrCDhJmmWmjSZTjXLwlC0aVuMOVIbQkAICAEhIASEgBCYVAiIGEwq5J1zjz76qHfpefDBB6P0IiQGti/BU0891SqbTzJ9aVL4T3Y0PB4LRCjoh8eG+weYYG4kATcryyBkm5fZ8WG8APUlrQDsxZAkBFlghrEFRiY4NtwwLcpEqBEhIASEgBAQAkJACLRDBEQM2uGkqEtCQAgIASEgBISAEBACQiA2AiIGsRFXe0JACAgBISAEhIAQEAJCoB0iIGLQDidFXRICQkAICAEhIASEgBAQArEREDGIjbjaEwJCQAgIASEgBISAEBAC7RABEYN2OCnqkhAQAkJACAgBISAEhIAQiI2AiEFsxNWeEBACQkAICAEhIASEgBBohwiIGLTDSVGXhIAQEAJCQAgIASEgBIRAbAREDGIjrvaEgBAQAkJACAgBISAEhEA7REDEoB1OirokBISAEBACQkAICAEhIARiIyBiEBtxtScEhIAQEAJCQAgIASEgBNohAiIG7XBS1CUhIASEgBAQAkJACAgBIRAbARGD2IirPSEgBISAEBACQkAICAEh0A4REDFoh5OiLgkBISAEhIAQEAJCQAgIgdgIiBjERlztCQEhIASEgBAQAkJACAiBdoiAiEE7nBR1SQgIASEgBISAEBACQkAIxEZAxCA24mpPCAgBISAEhIAQEAJCQAi0QwREDNrhpKhLQkAICAEhIASEgBAQAkIgNgIiBrERV3tCQAgIASEgBCYBAldffbV777333BFHHDEJWleTQkAIdAQERAza0Sx98803btSoUe67775zY8eOdT///LObcsopXefOnd10003npp12Wv/Oa4oppnBNTU3tqPfqihAQAu0dgS+++MLttdde7uijj3a9e/du6e7gwYPdwIED3RlnnOHvL5NLOfbYY/1QQkH4zTff9OM/99xzXffu3Rs2VDClfYTxZDtp/WpYR4KKqyYGtdQH7vvss487++yzW629GONWG0JACJRHwBOD5ubmNgmZCLEff/yxGzp0qPvss88cD5+vv/7ajR492o0bN84LuFNNNZUXcLt16+Zmn312N++887pFF13UTT/99OV765z79NNPfb0//PCDF55//PFHN378eP+ygtCMQM1r6qmndp06dfIvBGtefB4xYoQbPny4f6e/JpCPGTPG9/mnn35y4EKh75xD/2eYYQY/hllnndUtvPDCbuaZZ3YzzjijHwfH5RX6/vzzz7tXX33Vvfvuu27YsGHuk08+cZ9//rkbOXKkP7VLly6+rmmmmca/wI7+0C9ejJv3hRZayPcZLMPXG2+84bbaaivfx3nmmcfNMsssvn8cy5xAOnhZXdSdhuF///tft+qqq3pcv/32W4/5999/79v/6KOP/IMOYgLGhg19Bw/6M/fcc7sFFljAY8u4GRP1WPu82/dHHnnELb744n6c4Yt+2XebX+aWOWUemQ/GRpvMB+3ON998br655nJTfvONc19/7Rzv333n3OjRzo0Z49zYsc79+KNzP/3kHPMLuZpySuc6dXJu2mmdYz3OOKNz3bo5N8ssE14lC3NFP+l3+Hr/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)
</center>

#### remove(Object o)：
1. 如果入参元素为空，则遍历数组查找是否存在元素为空，如果存在则调用`fastRemove()`将该元素移除，并返回`true`表示移除成功。
2. 如果入参元素不为空，则遍历数组查找是否存在元素与入参元素使用`equals`比较返回`true`，如果存在则调用`fastRemove()`将该元素移除，并返回`true`表示移除成功。
3. 否则，不存在目标元素，则返回`false`。

#### fastRemove(int index)：和remove(int index)类似
1. 将`modCount+1`，并计算需要移动的元素个数。
2. 如果需要移动，将`index+1`位置及之后的所有元素，向左移动一个位置。
3. 将`size-1`位置的元素赋值为空（因为上面将元素左移了，所以`size-1`位置的元素为重复的，将其移除）。

### 5. clear方法
```java
/**
 * Removes all of the elements from this list.  The list will
 * be empty after this call returns.
 */
public void clear() {   // 删除此列表中的所有元素。
    modCount++; // 修改次数+1
 
    // clear to let GC do its work
    for (int i = 0; i < size; i++)  // 遍历数组将所有元素清空
        elementData[i] = null;
 
    size = 0;   // 元素数量赋0
}
```
遍历数组将所有元素清空。

## 四、ArrayList 扩容机制分析（JDK8）
### 1. ArrayList 的构造函数（容量初始化）
`ArrayList` 有三种方式来初始化，构造方法源码如下：
```java
/**
 * 默认初始容量大小
 */
private static final int DEFAULT_CAPACITY = 10;

/**
 * 空数组（用于空实例）。
 */
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};

/**
 * 容量初始化1：
 * 默认构造函数，使用初始容量10构造一个空列表(无参数构造)
 */
public ArrayList() {
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}

/**
 * 容量初始化2：
 * 带初始容量参数的构造函数。（用户自己指定容量）
 */
public ArrayList(int initialCapacity) {
    if (initialCapacity > 0) {//初始容量大于0
        //创建initialCapacity大小的数组
        this.elementData = new Object[initialCapacity];
    } else if (initialCapacity == 0) {//初始容量等于0
        //创建空数组
        this.elementData = EMPTY_ELEMENTDATA;
    } else {//初始容量小于0，抛出异常
        throw new IllegalArgumentException("Illegal Capacity: "+
                                           initialCapacity);
    }
}

/**
 * 容量初始化3：
 * 构造包含指定collection元素的列表，这些元素利用该集合的迭代器按顺序返回
 * 如果指定的集合为null，throws NullPointerException。
 */
public ArrayList(Collection<? extends E> c) {
    elementData = c.toArray();
    if ((size = elementData.length) != 0) {
        // c.toArray might (incorrectly) not return Object[] (see 6260652)
        if (elementData.getClass() != Object[].class)
            elementData = Arrays.copyOf(elementData, size, Object[].class);
    } else {
        // replace with empty array.
        this.elementData = EMPTY_ELEMENTDATA;
    }
}
```
以无参数构造方法创建 `ArrayList` 时，实际上初始化赋值的是一个空数组。当真正对数组进行添加元素操作时，才真正分配容量。**即向数组中添加第一个元素时，数组初始容量扩为 `10`。**

> **补充：`JDK6` `new`一个无参构造的 `ArrayList` 对象时，直接创建了长度是 `10` 的 `Object[] 数组 elementData` 。**

### 2. 分析扩容步骤
上文`add方法`在添加元素之前会先调用 **`ensureCapacityInternal()`** 方法，
主要是有两个目的：
* 如果没初始化则进行初始化；
* 校验添加元素后是否需要扩容。

这里以无参构造函数创建的 `ArrayList` 为例分析

#### 2.1. 先来看 add 方法
```java
/**
 * 将指定的元素追加到此列表的末尾。
 */
public boolean add(E e) {
    // 添加元素之前，先调用ensureCapacityInternal方法
    ensureCapacityInternal(size + 1);  // Increments modCount!!
    // 这里看到ArrayList添加元素的实质就相当于为数组赋值
    elementData[size++] = e;
    return true;
}
```
>注意 ：`JDK11` 移除了 `ensureCapacityInternal()` 和 `ensureExplicitCapacity()` 方法

#### 2.2. 再来看看 ensureCapacityInternal() 方法
（`JDK7`）可以看到 `add` 方法 首先调用了`ensureCapacityInternal(size + 1)`
```java
//得到最小扩容量
private void ensureCapacityInternal(int minCapacity) {
    // 校验当前数组是否为DEFAULTCAPACITY_EMPTY_ELEMENTDATA，
    // 如果是则将minCapacity设为DEFAULT_CAPACITY，
    // 主要是给DEFAULTCAPACITY_EMPTY_ELEMENTDATA设置初始容量
    if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
          // 获取默认的容量和传入参数的较大值
        minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
    }

    ensureExplicitCapacity(minCapacity);
}
```
**当要`add`进第`1`个元素时，`minCapacity` 为`1`，在`Math.max()`方法比较后，`minCapacity` 为 `10`。**

>此处和后续 `JDK8` 代码格式化略有不同，核心代码基本一样。

#### 2.3. ensureExplicitCapacity() 方法
如果调用 **`ensureCapacityInternal()`** 方法就一定会进入 **`ensureExplicitCapacity()`** 这个方法
```java
//判断是否需要扩容
private void ensureExplicitCapacity(int minCapacity) {
    modCount++; // 修改次数+1

    // overflow-conscious code
    // 如果添加该元素后的大小超过数组大小，则进行扩容
    if (minCapacity - elementData.length > 0)
        // 调用grow方法进行扩容，调用此方法代表已经开始扩容了
        grow(minCapacity);
}
```
我们来仔细分析一下：

* 当我们要 `add` 进第 `1` 个元素到 `ArrayList` 时，`elementData.length` 为 `0` （因为还是一个空的 `list`），因为执行了 `ensureCapacityInternal()` 方法 ，所以 `minCapacity` 此时为 `10`。此时，`minCapacity - elementData.length > 0` 成立，所以会进入 `grow(minCapacity)` 方法。
* 当 `add` 第 `2` 个元素时，`minCapacity` 为 `2`，此时 `e lementData.length`(容量)在添加第一个元素后扩容成 `10` 了。此时，`minCapacity - elementData.length > 0` 不成立，所以不会执行`grow(minCapacity)` 方法。
* 添加第 `3、4···`到第 `10` 个元素时，依然不会执行 `grow` 方法，数组容量都为 `10`。

**直到添加第 `11` 个元素，`minCapacity(为 11)`比 `elementData.length（为 10）`要大。进入 `grow` 方法进行扩容。**

#### 2.4. grow() 方法
```java
/**
 * 要分配的最大数组大小（数组允许的最大长度）
 */
private static final int MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;

/**
 * ArrayList扩容的核心方法。
 */
private void grow(int minCapacity) {
    // oldCapacity为旧容量，newCapacity为新容量
    int oldCapacity = elementData.length;
    // 将oldCapacity 右移一位，其效果相当于oldCapacity /2，
    // 我们知道位运算的速度远远快于整除运算，整句运算式的结果就是将新容量更新为旧容量的1.5倍，
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    // 然后检查新容量是否大于最小需要容量，若还是小于最小需要容量，那么就把最小需要容量（minCapacity）当作数组的新容量，
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    // 如果新容量大于 MAX_ARRAY_SIZE，执行`hugeCapacity()` 方法来比较 minCapacity 和 MAX_ARRAY_SIZE，
    // 如果minCapacity大于最大容量，则新容量则为`Integer.MAX_VALUE`，否则，新容量大小则为 MAX_ARRAY_SIZE 即为 `Integer.MAX_VALUE - 8`。
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    // minCapacity is usually close to size, so this is a win:
    // 将原数组元素拷贝到一个容量为newCapacity的新数组（使用System.arraycopy），
    // 并且将elementData设置为新数组
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```
**`int newCapacity = oldCapacity + (oldCapacity >> 1)`**  
所以 `ArrayList` 每次扩容之后容量都会变为原来的 `1.5` 倍左右**（`oldCapacity 为偶数就是 1.5 倍，否则是 1.5 倍左右`）！** 奇偶不同，**比如：10+10/2 = 15, 33+33/2=49。如果是奇数的话会丢掉小数（0.5）**

> "`>>`"（移位运算符）：`>>1` 即右移一位（相当于除 `2`），右移 `n` 位相当于除以 `2` 的 `n` 次方。这里 `oldCapacity` 明显右移了 `1` 位所以相当于 `oldCapacity /2`。  
对于大数据的 `2` 进制运算，位移运算符比那些普通运算符的运算要快很多，因为程序仅仅移动一下而已，不去计算，这样提高了效率，节省了资源

**通过例子探究一下grow() 方法：**
* 当 add 第 1 个元素时，oldCapacity 为 0，经比较后第一个 if 判断成立，newCapacity = minCapacity(为 10)。但是第二个 if 判断不会成立，即 newCapacity 不比 MAX_ARRAY_SIZE 大，则不会进入 `hugeCapacity` 方法。数组容量为 10，add 方法中 return true,size 增为 1。
* 当 add 第 11 个元素进入 grow 方法时，newCapacity 为 15，比 minCapacity（为 11）大，第一个 if 判断不成立。新容量没有大于数组最大 size，不会进入 hugeCapacity 方法。数组容量扩为 15，add 方法中 return true,size 增为 11。

**这里补充一点比较重要，但是容易被忽视掉的知识点：**
* java 中的 **`length`** 属性是针对`数组`，比如说声明了一个数组，想知道这个数组的长度则用到了 `length` 这个属性
* java 中的 **`length()`** 方法是针对`字符串`，如果想看这个字符串的长度则用到 `length()` 这个方法
* java 中的 **`size()`** 方法是针对`泛型集合`，如果想看这个泛型有多少个元素，就调用`size()`方法来查看

#### 2.5. hugeCapacity() 方法。
从上面 `grow()` 方法源码我们知道： 
* 如果新容量大于**MAX_ARRAY_SIZE**，执行`hugeCapacity()` 方法来比较 `minCapacity` 和 `MAX_ARRAY_SIZE`，
    - 如果 `minCapacity` 大于最大容量，则新容量则为 **Integer.MAX_VALUE**，
    - 否则，新容量大小则为 **MAX_ARRAY_SIZE** 即为 **Integer.MAX_VALUE - 8**。

```java
/**
 * 设置一个合适的容量
 */
private static int hugeCapacity(int minCapacity) {
    if (minCapacity < 0) // overflow
        throw new OutOfMemoryError();// 越界
    // 对minCapacity和MAX_ARRAY_SIZE进行比较
    // 如果minCapacity大于MAX_ARRAY_SIZE，则返回Integer.MAX_VALUE，否则返回MAX_ARRAY_SIZE
    // MAX_ARRAY_SIZE = Integer.MAX_VALUE - 8;
    return (minCapacity > MAX_ARRAY_SIZE) ?
        Integer.MAX_VALUE :
        MAX_ARRAY_SIZE;
}
```

### 3. System.arraycopy() 和 Arrays.copyOf()方法
通过源码会发现 `ArrayList` 中大量调用了这两个方法。  
如：扩容操作以及`add(int index, E element)`、`toArray()` 等方法中都用到了这两个方法
#### 3.1. System.arraycopy() 方法
源码：
```java
// arraycopy 是一个 native 方
/**
* 复制数组
* @param src 源数组
* @param srcPos 源数组中的起始位置
* @param dest 目标数组
* @param destPos 目标数组中的起始位置
* @param length 要复制的数组元素的数量
*/
public static native void arraycopy(Object src,  int  srcPos,
                                    Object dest, int destPos,
                                    int length);
```
场景：
```java
/**
 * 在此列表中的指定位置插入指定的元素。
 * 先调用 rangeCheckForAdd 对index进行界限检查；然后调用 ensureCapacityInternal 方法保证capacity足够大；
 * 再将从index开始之后的所有成员后移一个位置；将element插入index位置；最后size加1。
 */
public void add(int index, E element) {
    rangeCheckForAdd(index);

    ensureCapacityInternal(size + 1);  // Increments modCount!!
    // arraycopy()方法实现数组自己复制自己
    // elementData:源数组；
    // index:源数组中的起始位；
    // elementData：目标数组；
    // index + 1：目标数组中的起始位置； 
    // size - index：要复制的数组元素的数量；
    System.arraycopy(elementData, index, elementData, index + 1, size - index);
    elementData[index] = element;
    size++;
}
```
测试：
```java
public class ArraycopyTest {

    public static void main(String[] args) {
        int[] a = new int[10];
        a[0] = 0;
        a[1] = 1;
        a[2] = 2;
        a[3] = 3;
        System.arraycopy(a, 2, a, 3, 3);
        a[2]=99;
        for (int i = 0; i < a.length; i++) {
            System.out.print(a[i] + " ");
        }
    
}
```
结果：
```
0 1 99 2 3 0 0 0 0 0
```

#### 3.2. Arrays.copyOf()方法
源码：
```java
/**
 * 复制目标数组，截断或填充以获得指定的长度的新数组
 * @param original 想要复制的数组
 * @param newLength 最终要返回的新数组的长度
 */
public static int[] copyOf(int[] original, int newLength) {
    // 申请一个新的数组
    int[] copy = new int[newLength];
    // 调用System.arraycopy,将源数组中的数据进行拷贝,并返回新的数组
    System.arraycopy(original, 0, copy, 0,
                     Math.min(original.length, newLength));
    return copy;
}
```
场景：
```java
/**
 * 以正确的顺序返回一个包含此列表中所有元素的数组（从第一个到最后一个元素）；
 * 返回的数组的运行时类型是指定数组的运行时类型。
 */
public Object[] toArray() {
    // elementData：要复制的数组；size：要复制的长度
    return Arrays.copyOf(elementData, size);
}
```
`Arrays.copyOf()`方法主要是为了给原有数组扩容或者截取`0`到`指定长度`的新数组，测试代码如下：
```java
public class ArrayscopyOfTest {
    public static void main(String[] args) {
        int[] a = new int[3];
        a[0] = 0;
        a[1] = 1;
        a[2] = 2;
        int[] b = Arrays.copyOf(a, 10);
        System.out.println("b.length"+b.length);
    }
}
```
结果：
```
10
```
#### 3.3. 两者联系和区别
**联系：**  
看两者源代码可以发现 `copyOf()` 内部实际调用了 `System.arraycopy()` 方法

**区别：**  
`arraycopy()` 需要目标数组，将原数组拷贝到自定义的数组里或者原数组，而且可以选择拷贝的起点和长度以及放入新数组中的位置 `copyOf()` 是系统自动在内部新建一个数组，并返回该数组。

## 五、补充：ensureCapacity方法
`ArrayList` 源码中有一个 **ensureCapacity**，这个方法 `ArrayList` 内部没有被调用过，所以很显然是提供给外部调用的
```java
/**
 * 如有必要，增加此 ArrayList 实例的容量，以确保它至少可以容纳由最小容量参数指定的元素数量。。
 *
 * @param minCapacity 所需的最小容量
 */
public void ensureCapacity(int minCapacity) {
    int minExpand = (elementData != DEFAULTCAPACITY_EMPTY_ELEMENTDATA)
        // any size if not default element table
        ? 0
        // larger than default for default empty table. It's already
        // supposed to be at default size.
        : DEFAULT_CAPACITY;

    if (minCapacity > minExpand) {
        ensureExplicitCapacity(minCapacity);
    }
}
```
**最好在 `add` 大量元素之前用 `ensureCapacity` 方法，以减少增量重新分配的次数**

测试：
```java
public class EnsureCapacityTest {
    public static void main(String[] args) {
        ArrayList<Object> list = new ArrayList<Object>();
        final int N = 10000000;
        long startTime = System.currentTimeMillis();
        for (int i = 0; i < N; i++) {
            list.add(i);
        }
        long endTime = System.currentTimeMillis();
        System.out.println("使用ensureCapacity方法前："+(endTime - startTime));
    }
}
```
运行结果：
```
使用ensureCapacity方法前：2158
```
```java
public class EnsureCapacityTest {
    public static void main(String[] args) {
        ArrayList<Object> list = new ArrayList<Object>();
        final int N = 10000000;
        list = new ArrayList<Object>();
        long startTime1 = System.currentTimeMillis();
        list.ensureCapacity(N);
        for (int i = 0; i < N; i++) {
            list.add(i);
        }
        long endTime1 = System.currentTimeMillis();
        System.out.println("使用ensureCapacity方法后："+(endTime1 - startTime1));
    }
}
```
运行结果：
```
使用ensureCapacity方法后：1773
```
通过运行结果，可以看出向 `ArrayList` 添加大量元素之前最好先使用`ensureCapacity` 方法，**以减少增量重新分配的次数。**
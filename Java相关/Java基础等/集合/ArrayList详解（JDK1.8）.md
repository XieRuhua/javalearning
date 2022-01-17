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

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/集合/ArrayList详解（JDK1.8）/add的过程演示.png)
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

![](https://gitee.com/xieruhua/images/raw/master/JavaLearning/Java相关/Java基础等/集合/ArrayList详解（JDK1.8）/remove的过程演示.png)
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
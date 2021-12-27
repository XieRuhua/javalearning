# ArrayList详解（JDK1.8）
***
[笔记内容参考1：Java集合：ArrayList详解](https://joonwhee.blog.csdn.net/article/details/79190114)  
[笔记内容参考2：JavaGuide：ArrayList](https://snailclimb.gitee.io/javaguide/#/docs/java/collection/arraylist-source-code)

[toc]
## 一、ArrayList 简介
ArrayList 的底层是数组队列，相当于动态数组。与 Java 中的数组相比，它的容量能动态增长。   
**在添加大量元素前，应用程序可以使用 ==ensureCapacity==操作来增加 ArrayList 实例的容量。这可以减少递增式再分配的数量。**

ArrayList继承于 `AbstractList` ，实现了 `List`, `RandomAccess`, `Cloneable`, `java.io.Serializable` 这些接口。

```java
public class ArrayList<E> extends AbstractList<E> 
    implements List<E>, RandomAccess, Cloneable, java.io.Serializable{
    
}
```
* **RandomAccess** 是一个标志接口，表明实现这个这个接口的 List 集合是支持快速随机访问的。在 ArrayList 中，我们即可以通过元素的序号快速获取元素对象，这就是快速随机访问。
* ArrayList 实现了 **Cloneable** 接口 ，即覆盖了函数clone()，能被克隆。
* ArrayList 实现了 **java.io.Serializable** 接口，这意味着ArrayList支持序列化，能通过序列化去传输。

### 1.1. Arraylist 和 Vector 的区别?
* ArrayList 是 List 的主要实现类，底层使用 Object[ ]存储，适用于频繁的查找工作，线程不安全 ；
* Vector 是 List 的古老实现类，底层使用 Object[ ]存储，线程安全的。

### 1.2. Arraylist 与 LinkedList 区别?
1. **是否保证线程安全：** ArrayList 和 LinkedList 都是不同步的，也就是不保证线程安全；
2. **底层数据结构：** Arraylist 底层使用的是 Object 数组；LinkedList 底层使用的是 双向链表 数据结构（JDK1.6 之前为循环链表，JDK1.7 取消了循环。注意双向链表和双向循环链表的区别）
3. **插入和删除是否受元素位置的影响：** 
    * **ArrayList 采用数组存储**，所以插入和删除元素的时间复杂度受元素位置的影响。 比如：执行`add(E e)`方法的时候， ArrayList 会默认在将指定的元素追加到此列表的末尾，这种情况时间复杂度就是 O(1)。但是如果要在指定位置 i 插入和删除元素的话（`add(int index, E element)`）时间复杂度就为 O(n-i)。  
    因为在进行上述操作的时候集合中第 i 和第 i 个元素之后的(n-i)个元素都要执行向后位/向前移一位的操作。 
    * **LinkedList 采用链表存储**，所以对于`add(E e)`方法的插入，删除元素时间复杂度不受元素位置的影响，近似 O(1)，如果是要在指定位置i插入和删除元素的话（`(add(int index, E element)`） 时间复杂度近似为o(n))因为需要先移动到指定位置再插入。
4. **是否支持快速随机访问：** LinkedList 不支持高效的随机元素访问，而 ArrayList 支持。快速随机访问就是通过元素的序号快速获取元素对象(对应于get(int index)方法)。
5. **内存空间占用：** ArrayList 的空 间浪费主要体现在在 list 列表的结尾会预留一定的容量空间，而 LinkedList 的空间花费则体现在它的每一个元素都需要消耗比 ArrayList 更多的空间（因为要存放直接后继和直接前驱以及数据）。

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
2. 根据index获取指定位置的元素
3. 用传入的element替换index位置的元素
4. 返回index位置原来的元素

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
1. 调用ensureCapacityInternal方法，将modCount+1，并校验添加元素后是否需要扩容。
2. 在elementData数组尾部添加元素即可（size位置）。

#### add(int index, E element)：
1. 检查索引是否越界，再调用ensureCapacityInternal方法，将modCount+1，并校验添加元素后是否需要扩容。
2. 将index位置及之后的所有元素向右移动一个位置（为要添加的元素腾出1个位置）。
3. 将index位置设置为element元素，将size+1

**add(int index, E element)的过程如下图所示**  
<center>

![avatar](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAABIUAAAE8CAIAAADR05bgAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAABmJLR0QA/wD/AP+gvaeTAAAAB3RJTUUH5QsBEigAB86vUQAAgABJREFUeNrs3XdcU1f7APCTcBNCIMwAYcoUURRBUVFxi4MqrVpX66xarVRtHdU6atW6tdXW1lXrqnVVixMH4gZBQGUJyBAZAQIJZBCSm+T3x3nf++YNIcYZ+L3P949+6s3JzXMHyXnuWUijT319vcZor1S4rKzsHe0ZYoaYIWaIGWKGmCFmiBlihpgh5pZQGGI2vjAdAQAAAAAAAAAwBcjHAAAAAAAAAMA0IB8DAAAAAAAAANOAfAwAAAAAAAAATAPyMQAAAAAAAAAwDcjHAAAAAAAAAMA0IB8DAAAAAAAAANOAfAwAAAAAAAAATAPyMQAAAAAAAAAwDcjHAAAAAAAAAMA0IB8DAAAAAAAAANOg1dfXv8/PE4vFHA7H1EcNMbdEEDPEDDFDzBBzywQxQ8wQM8QMMb87hN5PfaVooDAUhsJQGApDYSgMhaEwFIbCUBgKv0Zh6K8IAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGpCPAQAAAAAAAIBpQD4GAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGsRb3FdDQ8Nvv/3m7e3du3dvLpdLo9GaltFoNEKhMDMz8/bt23369Ondu7feYi1WcXHxwYMHR4wYERwcTBCvf/bkcvnOnTvNzMwGDRrUvn17BoPx2ruqrq5mMBi2trb4n0+ePDl27Fi/fv0cHR3fZLfp6ekXL14cMWKEgfCUSmVJSUlSUlJ5efnMmTOpGFoLuVz+448/MpnM/v37BwUFMZlMU0ekn0ajUalUb3K/AQAAAACAlult1vBoNFpNTc2ff/45c+bMGTNm4OqjRqORSCQvXrx49uzZw4cP79+/LxQKmUymt7d3cXExj8fz9/fXuzeBQLB27Vomkzl+/Pg3TH7eomfPnp0/f/7mzZtr166NiIh4k13V1dXFxcU5Ojp27NjxpYUbGhpu3LhRWVmpVqu1t4vF4mvXriGEVqxY0adPH4QQh8PJyMhITExksVh9+/Z97XRXrVafPXs2NTV169atvr6+eKNSqaysrMzMzHzy5EliYmJOTg5Jkq6urnZ2didPnpw+fbrey6RWq+Pi4o4ePTp06NDhw4dzudx3cWkUCsX58+dFItGUKVOMv1skEklcXFybNm1CQkK0d5Wenh4QENBCMsz6+vpFixY5OTl5eHjgLSqV6smTJzweb968eQ4ODg0NDZaWlnT6v5q7NRpNSkqKg4MDdeEAAAAAAEDL9E6SnLCwMIIgysvLb968KZVK/fz82Gy2WCy+ePFiz549161bZ2Nj89KdcLncr7766tatW8uWLbOzs/vmm29CQkJM25imVCqTkpIQQiNHjgwPD38r+7SxsaGq0Qih0tLS69evjx07ls1maxezsLDo378/jUZjsVjarVWpqanHjx8PDAwMCgrSLu/m5ta5c+emp0ssFp88efKff/4pLy93cHD46KOPxo4da6BdqH379m5ubiRJ3r17t7Cw0MrKytHRkSCItLS0jIyMn376qVevXtrx60Wn0yMjI52dnQ8fPvzbb799/PHHs2bNsrKyMv4slZSUxMfHNzY2UlsUCoVO2BkZGfjqSCSSzz//nMViab/K5/Pj4+PFYrH2RpIk8/LyEEJ3794VCAR4Y0NDw6NHjzIzM4ODg9euXevm5oa3x8bGrlmzpmlsDg4OnTp1+vDDD7t16/aOWthEIlFVVZVCoVi8eDFOEVNTUw8cOBAUFNTQ0IAQOnz48NOnT0NCQszMzBBCz58/v3HjhoODw44dO5p73vFKqGOfMmXKvHnzDJQsKiqKiYnh8/lBQUE7duzQTmivXbu2YsWKiIiINWvW4Ntbo9E8evTo4MGDycnJarW6c+fOU6dO7d69+0vvKB2pqamzZs1CCA0dOnTlypWPHj1asGABQojH4/3yyy/e3t4ikWj+/PmZmZk6byQIwtfXt1+/fh988IGrqyu1XS6Xr127Ni4uDiG0d+/eDh06UP/EZ6C6uvqrr76qrq7+6aefAgMD38VFBwAAAMD/iHfY6OTq6jpx4sT/fBJBIIQYDIa5ubmRe3BwcJgyZcqgQYNWrlz59ddfb9u2rUuXLiY8WVVVVenp6Ww2e+DAgU1bYCQSyeHDhzt16tSrVy/tRIjP59+8eVMkEmkXpjKBhISEiooKvLGmpubChQsKhaKgoOCbb77RyVhoNBqHw9EbmJmZmTFVWIFAsGzZsrS0NOrj9u/ff/Xq1e+//75Tp04G3kgQRL9+/fr164cQEovFDAYD103ZbLaRVWeCILp06RIcHHzmzJlt27bV19cvXbpUJ2UywNPTc8KECSqVytLSEm8Ri8XNnQ29eDzeuHHj5HK5paUldXXkcnlFRUVhYWH//v2jo6PxxqKioujoaG9vbyOT/5qamoSEhISEhL59+65YscLe3t74qIykVqtJkmy63d3dncvlyuXy6urqioqK5cuXe3t7I4RiY2OvXr0aGRnp5+f31oN5PQKB4MSJEyRJRkREUMnY+fPnf/jhB+rQHj58+PDhQ+3W9XeNJMnc3Nzc3Nxjx44tW7YsMjLSyIvO5XL79+//66+/Hj16dOXKlcbfyQAAAAAAOt5JpUetVpeUlPB4PMPNBRqNprS01NbW1nDF2s3Nbdq0aQsWLLhw4ULHjh3fzyAf7SSKqvrz+fzi4mIul5uQkJCYmKhdXqFQxMfHl5aWcjicJUuWDB06lEpUeDzemDFjjMkEEELLly9/R0dEkuThw4epZIxSUlJy4MCB9evX67TIUUQikZmZmaOjo+H9NzQ08Pl8Ly8vAzVagiCioqKSkpLi4+M/+uij4OBg4+N/8yqvRqN5/Phxdna2SqWizolOVoxTYnNz89WrV79qb89bt25ZWVktXbq0uTP5jiiVSp1sH6PT6S1ncOaNGzfS09M9PT2pRyqFhYW7du1qmmf+8ccfnTp16tmz5/sMTywWb9iwwc7Orlu3bsaUp9FoXbt2ZbPZt2/ffvLkiZHvAgAAAABo6i3kY0+fPn306JFKpaJqt8uWLRMKhQMGDNAevsLn8xFCRUVF+/fvxw+/cQezHj16fP/994bHFOGOavfv33/+/Plb6X/1UtpJVEVFhaurq0Qi+e677wiCWLRo0eDBg589e5adnd29e3dHR0eceuF+XE3bbVJTU8vKyoYNG2Z85bi+vp7FYjXNPEtLS7lc7utlJpWVlffu3UMIeXp6fv/990FBQQ8ePFi2bJlYLM7IyCgpKWnXrp1UKr127Rq+Uvi/t2/fvn37trW1dWRkJG7YVCgUdDodX+jz58+npKSgfw9jE4vFy5cvj4qKMnCkarVaLpfLZLL4+PgOHTq8z2GBDAajV69eOB/A51BvVjxv3jzDDwi0++yVlJSo1eqff/755s2bCKErV65EREQMHjz4XcTP5/MPHjyII8dXB1OpVFKp9L2dxtdQV1d348YNhFD79u2pv/TExETcR3TSpEmff/65SqXatGnTpUuXcOfYbt26GX9vMJlMNpstk8kcHR3Nzc1tbGycnZ0rKyvt7Ox0ukZTPRjxP8Vi8aVLl37//feamhqxWHzo0KGAgAAbGxszMzMLCwuEkLOzs62trbm5OfU8wt3dHf+Pl5dXhw4dUlJSLl++3Llz5xY7GQwAAAAAWjhCZ0QNpbntTbVr187b25vJZDY2Nr548aKwsPC7777r3LkzboXAA1oQQo8ePTp//ry3t/e4ceOaZhQGwtBoNLhVRyAQ3L17l8fjNReJ8TEbX1gikeDCCQkJd+/e7dGjR1BQkFgsrqmp2bJli5mZ2erVq3V6UWrvWalUnjt3LjMz89mzZ9r1S5Iknz59ihC6du3a8+fPtd9eW1t75cqVfv36zZ07V7s2KZfLf/755ydPnvTp04fqtldZWYkQUqlUEokEn2qpVKrRaHDk1MlHCIlEouDgYAaD0bVrVy8vL6lU6uvrGxYWduPGDZFIVF1djQdK9e3bFyFEEAS+Xj179ly0aBGLxVIqldS4Nblcji/0wIEDO3fujDfOnj1b+4w1d56LioqKiooQQg8ePCgpKdFpdnvzK4hn9bC1te3fv792X0qdwkqlEh8Ibp+Ry+XaBfD/19XV5ebmhoaG4gsnl8upj6AKEwSBW0TpdPqNGzdIkrx48WKnTp2aayJ7vQPE19TR0XHMmDH4lsBXhyRJsViMn1ZoNBqpVIrfgkPVjvMNw9B77HpRt5/2PZmSkpKeno4Q6tSpk/Lf7OzsunfvLhKJBgwYgK/CwIEDL126hBCqqakRCoU63xIGPpfJZHK53JKSEhsbG4lEYm9vb29vX1lZ6eLigk+RRCLBX0faZwnDE8ysXr1aJpM9fPgwJSWle/fuCCEHBweEEIfDodFoEonExcUFl7e3t8dvp9Fobdu2TUlJuXfvXnZ2tt6pU97FNxIUhsJQGApDYSgMhf+fFSb0NgW80uAcsViMn3nL5XJcc2Wz2TpvJ0mSGjbG4XCMbOHBYdTV1RUWFnp5eTEYjJSUlDFjxryVmF+psFQqPX78uIWFxYwZM3DNzMnJydramsvldu7cWXtXOnsuLS198uSJtbX19OnTqbkN5HL5nj17ysvLZ8yYMXXqVPwkHlMoFFu2bFGr1W3atGGxWNq7qq6uLikpodPp48ePpx7wZ2RkiMXiXr16Ue1mVK9IKysr7bd36NChQ4cOOoeG21WcnZ3d3d11TgjOKHC+oX296uvrmUxmcxf6pee5oqKiqqoqPDw8MTGxsLDQx8fHQGE8gUpOTo7OrJJI33weCCGVSpWcnJyZmUkQRF1d3YQJE5hMJp/Pj4uLozIKbSRJFhYWIoQSExOFQqH2nmtra69evSoWiydPnoxnB6FOApPJpOLEMXM4nI8++uj27dskSRYVFcnlcmdn5ze/66jC+JqamZlR11T76uA8mUajWVpa4ldxqNpxIoQ0Gs3Tp08PHTqUmJgokUgIgvD39x82bNioUaO070DtOTYQQr17954/f77eY0cIVVZWHj58+Nq1azU1NYGBgVOmTPHx8cG3HxUtSZJpaWkkSbLZ7Pbt21Nvj4qKGj9+vM7lwP/j4eGhs2CG4VPn7u7u7e1dUlLi5+fH4XAaGxt9fHxycnLc3NwcHR1pNJpKpcKZofZZovYcHh7evXv3hIQE3MI/aNAghBCeIMfNzc3Z2dnS0rJt27YEQdjb23t4eFBvDwsL+/PPP2tqarKzs6kHE29+uaEwFIbCUBgKQ2Eo/D9V+O33FiMIgk6n19TUpKam9u3bl8FgJCYmbt68GT9v1oZbJ146z15xcXFWVtYHH3xgZmYWGxtbXFxszATxbxFJkufOncvNzf38889faS41kiT/+eefkpKS7t27U01VEolk165d//zzz7Rp0yIjIy0sLEQi0V9//RUVFeXp6fno0aOkpKQdO3Z0795dp9cf7lnXpUsX7b6dHTt23Llz52sclFwuv3jxYmpqKkJo6NCh1ETqOszMzDQaTXJysq2tbdu2bWtqan777Tc8mb52MY1GIxKJdOaKbEqhUCQlJdnZ2UVGRhYWFiYlJeE7pLnyDAYjIiIiNDSUyWRSxXbu3Hno0KEPPvhgxYoVUqkUz5u3d+9e3Eo5d+5cnZ3weLyPPvqITqdrzwhfXFy8atWqrKysUaNGHT582MLCQq1WK5VKc3Nz6g/m22+/Nf58tmnTxt3dvbi4uLS0VCAQtGnT5jUuyjuVkpKyZMkS6tkMSZI5OTk5OTn5+fnU3CpN59i4cePG48eP27Zt23SHBQUFixYtKikpwf/MyclZsWJFWFiY9jSYCCGxWJydnY0Qcnd315um4s99/vz5sWPHEEKenp6v1LkXIWRpabl9+3bqn+bm5mvWrNE7GaZeOFFMSEhACJWVlcnlchaLFRERgf86sJCQkAcPHuh8mbq6uuKOkVlZWfhd7+E6AgAAAOD/mbefjzk4OKSkpMTGxjo5OYnF4uLi4vv370dFRbFYrMePHwuFwjNnztTX1+MRRzwe77vvvjOwSpJGo7lz545MJuvSpUtjY+Nff/2VnJwcFBT03iYqqKysPHjw4MWLF6Oioj799FMDY1pKS0uLioq0552XSCTW1tZz587t168fh8NRq9VZWVlbtmxxdHQ8deqUu7u7WCzOyspavXp1SUlJaWnpV199ZWlpuWPHDu1WI+o8PH78mCTJ9u3b62SwJElWVFS4ubkZP0s4NT84QRBz5syJjo5u7rjUavWPP/7o6Ogok8ny8/OPHj3q6Og4Z86c8+fPFxcXP378OC0tTaVSZWRkPHz48IsvvsBNUs19bllZWXJyctu2bUNCQng8XmpqamVlJTUgpzlU50x8sLili2oXMgadTqeq0Wq1+v79+xs2bOByub/88gueXV0ikezevfv69evffPNNaGjoq98myNLSkrouVFPb29V0/FhFRYVO8tOcurq6AwcOiMXi4ODgmJiYkJCQp0+fLlq0iM/n3717t7i4uF27dgihzMzM7du3kyTJ4XBWrlzZt2/f6urqEydOHDlypOkOt2/fjpOxSZMmzZgxg8VixcXFbd26Vac5vrKysrS0FCHk5eWl98mQ9uTyHTp0WLZs2ftfNo16WiQUCpVKpZGZlZ2dHe4YWVhYiMd8vuewAQAAAPD/wFvLxzQazbNnz4qKiiorK3H3vIsXL65Zs2bixImnTp2i0+n4YbOdnV10dDSLxXr06NHx48ddXFwMT39fWVl5//59T0/Pdu3aKZVKHo+XkJAwcuTIl07397bk5OTExsb6+flNmDDh8uXL1dXVeLtIJKqvrydJEleRqanqx48f/+WXX+Kama2t7eTJk3H5p0+frlmzJjc3NyAgwMfH58KFCwghPp9/5coVd3f3/fv34ySzuXlN8vPzz549ixB69uzZnj17tF/CudDo0aNnz55tbW1tzEHh+jFCiCTJpKSkwMBAne5hDQ0NDx8+RAi9ePHihx9+sLKymj9//pUrV3bs2MHj8XCbJ0IoODi4U6dOKpVq7dq1uEuqgZxQo9E8ePCAz+ePGjXKzc0tNDT0jz/+uH///tixY42/HEqlEmc72qtFGS89PX3Xrl1CoXD+/PmdO3d+8eJFSkqKRCI5dOhQbm5udHS0v7//m6f672h2DR6PN3XqVGr9sfPnzxvfSv7s2TM8gmvQoEE8Ho9Go3l7e3fu3DkuLk4oFOKANRrNrVu3cDY1adKkAQMG0Gg0KyuradOmPX36FE/cor1DfIeEhYVNmzYN56J9+vSprKz89ddftUvW19fjS2Zpaak37ZfL5dQNWVJScvv2bQ8Pj1danu4tkkql1PSbL2Vubu7k5JSTk1NdXV1bW+vk5GSSmAEAAADQqr2FfEyj0ZSUlPz8889ZWVm4Luvv709VvBgMhk4d3czMjOq8hxdQMrDz27dv5+bmjho1ysnJCa8YGxcXFx8fP27cOAP15uLi4nXr1qWnpwcGBi5cuDAkJOT1Di0jI2PHjh0IIRaL5eLiEhAQIJVKcbe3oqKiO3fucLlcqoqMp6oXi8V6H5MHBAR8+umnKSkp/fr1w/s5depUfHz8zJkzu3fvnp6ebmFh4ePj01w+07Zt27179965cwdPP0Btl0qlK1euJEmyU6dOxtfOIyMjR4wYIRQKt27devXq1WfPnm3evBnP2S2Xy69evbpv3z5cIaZWuEII0Wi0pvVpBoNB1V+1r3tTAoHgwoULHA6nW7dudDo9PDz8yJEj//zzT58+fQzM0aKjoaHhxYsX6HXzMX9/f39//8uXL9+5cwch5Obm9vDhwyNHjnh5ef388888Hs/V1fXNs6l3N2mkRqOprKw0Nzdv3779zZs38RXXO9m9ji5dujx48AAhpFQq8TJf8fHxePlsikwmw6PpCIIIDQ2l/r5sbGw6deqkk4/l5ubiPo2dOnWiZp2h0Wh4+hPtWeyp5fWsra31NmlaWVnt3buXwWDcunXr+++/37t3b1lZ2ftfNgAzMzMzPiGnpmGkcloAAAAAgFdlbA83A/BaUsXFxVu2bGk6qB0hpNFoysvL9U6oYFhlZeU///zD4XBGjhzJZDJZLNbQoUMJgjhx4oTOnIQ6Hj9+jFsDcnJycM37NWRkZOzcufPjjz/+z8mi0zkcjvHdArXRaLThw4d/99133bp1u3Tp0tSpU+Vy+b59+6ZPn96hQ4fg4ODFixdPmDAhLi5OoVDo3QOXy508ebJO+iqVSisqKuzs7Awv/KXDwsKCTqfj5bbt7OzEYvHJkydlMplQKFywYMEPP/wwYsSIr776Su97GxoaysvLX/XwNRpNfHx8Tk7O4MGDAwICEEIBAQG9e/fOzc09d+6c3sWO9SorK3v+/DmPxzOcxjfHyspq4cKF169fX7lyJYPB+Pbbb2/cuLF27dq9e/fiVH/ixIlXr159jXtVKpVSE0san16+KjzXX0xMzLVr14xfVx0hpNFocnJyFi5c2Lt375iYmO+///7u3bs6p12pVNbU1CCEuFwuNfcMhufe1Ianqm/6kq2t7ateGoIgcMtqRETE8OHDEUJXrlx59OjROzqHeuEDRwi9tMUeAAAAAODtegsP8nv27Pnll18OGTLEzs6u6avp6ekxMTFJSUleXl4IIWr8mPYCSnqRJHnhwoXc3NwJEyZQs2iEhIT07t375s2bBw8epCYhaCo4ODgkJAS3j0VERLzqEeGedXv27Fm0aNFrVM2b09DQgBc7cnV13b17d/v27SUSiVqtFovFHh4eM2bMWL9+PV6/y/jGATw4x93d3d7e/jVCMjc3x7XP6upqhUJhZ2c3c+bMysrKyMjIx48f6xSur6/ft29fSkqKRqPBTUB4/FhjYyNejsyA4uLiI0eOcLncUaNG4QFmVlZWH3744d27d48dO9alSxedNQOak5GRIZPJwsLCDFf6pVKpWq22srJqmqOKRKJLly4dP37c0dFx6dKlYWFhBEGo1eqGhoZRo0YJhcL169cfP35806ZNTUfxGcDn83Gnu5c2+b4hX1/f77//ftGiRefOnfvqq6/at29vzLvS0tIWLlwoFosJgujateuIESOCg4N//fXXq1evvrtQXxVBEPgvmiRJqmPweyCXywsKCvD/u7m5wTAwAAAAALxPbyEfY7PZU6dORVoLNGkLCQnBi+fiOSTs7OxGjhyJ5/Y4f/68gd2mpaX9888/Pj4+48ePpzqAWVlZTZw4MTU19fLly6GhoSNGjNDbKOTl5bV///7XPqKampra2tpff/3VwsJCe4611yaRSI4ePXr8+HGxWOzv729pablp0yapVFpcXNy2bdvevXt7eHj4+flt3Lhx5cqVFy9ejI6ONjI/KSkpkclkzc2UoO3QoUPx8fFCoXDChAkTJ07EG+vr6+vr67WLGfhca2vrmTNnLlu2jMFg4AkYgoODg4KC1Go1nvuxuTfKZLI//viDz+fHxMTgeSOwsLCwYcOGnT9/fvfu3Rs2bHjpwcpkMrwSXdeuXbUn+Wjq999/r6ysXLlypXbdurCwcPXq1VlZWQghnDKdOHFi48aNpaWlERERAwYM8Pb2njJlilAovHbt2sGDB5cvX25kUwlJkni2dISQv7+/9uBGhUIRGxt7+fJlBoPx0UcfDR061JgdGubr6/v1118vWrRo+vTpc+fOxW1KBiiVysuXL+OBYcuWLQsLC3Nzc5PL5Totvebm5q6urpmZmXw+v7a2llpTASFUVlams09qFhadlmqRSEQ1nRnw4sWL9evX19XV0en07du345FXCoXiHU2FYlhRUREeC0cQhN4WfgAAAACAd+ddDXQx9JEE8dIBNgKBYN++fQihxYsX68y/FxwcPH78+H379m3fvp3H4+FRT28Xl8t9aR33lVhaWrq6ujY0NAQGBg4YMCAiIsLLy+vSpUtr1qwJDw/XnqL9xx9/PHfunHZV2ACSJHF24eHhob2ElF48Hg8XPnXqVGBgYHBwcFVV1aFDh2QyGULIx8fn9YbrmJubG25C1Gg0169fv3LlSlRUlM6oPxaLNWnSJNzItnPnzilTphj+rMzMzAcPHnh6evbp08dAMaVSqZNkYq6urp6ennQ6vU+fPl27dsVzuK9du7a0tLR///4jR47ExcaNGycWi/v27WtMMqbRaKqrq48ePXrq1CmEEEEQQ4YM0T6TWVlZW7duxamara1tv379XqP5Ra1W40WW1Wr1s2fPrly5IhaLx44de+zYsfj4eHw2GhsbExISNm3aJJPJcOMz1W1SoVBQY8w8PDzwJaivr9dJoS0sLPz9/XGL2aNHj6ghZHV1dU+ePNEJyd/fn81my2Sy7Ozsuro6PIQML92u0w2S+vsVCASNjY34rFpbW5MkmZubixA6duwYnp7x2rVreNJ5NpuNm9PfNaVSmZycvHv3bpxDdu3atekafQaoVKqGhgZ8ql+vgRoAAAAAwAT5mDaqoqlNJpPt3LkzPz//m2++CQsL042YIMaMGZOampqWlrZixYo1a9Y0XaorIyNjxYoVpaWlHTt2XLVq1St1PHsXaDTaBx98MHDgQIIgrly5QpKk9sQG6enpQqGwY8eOXC43JCTE+NlHqJWd9C4PpaNLly64D2dJScmMGTO0X+JwOB988IGBeeqNpHdiupSUlO3btw8YMODrr79umvL5+PhMmzbthx9+uHjxYmNj48qVK5ubWA+n6DKZbNy4cW5ubtRgraZIkpRKpXV1dToTl7NYrHXr1ikUihMnTvz4449LlizRznuTkpJSU1N79+7dpk2bXbt2GTjMQ4cOHTp0SO9LQ4YM6dWrl/aWNm3ahIeH40GMLBaLmsnmleBpS3HbZlBQ0Jw5c3x9fSsrK1NTUzkcDt6nubl5//79P/300/379588eXLixImRkZH47UwmkxoPlpCQMGrUqLq6uj/++KNpL9P+/fv//ffffD4fz3HSt29fiURy4sQJnck8EEL+/v59+vSJi4tLSUn5448/cEJ1+/btpjPj29ra4kW6JBIJtS68jY3NoEGDcGvnkSNHdN41cOBAPMgQIRQbG4tXEpsyZQpuaX8TfD5/zJgxel/icDhTpkyh5iYxRmNjY1VVFULIzs7uld4IAAAAAEB5C/N5vIny8nKdBZRkMtmuXbuSkpI2btzYq1cvvd0RuVzu8uXLO3ToUFNT89VXX/3xxx/4KTWlsLAQD+bJyMjIyMh4b4dTWlr6559/6k0V8BrZ8+fP/+GHH3777bfi4mLqpZCQkLZt227cuHHIkCHbtm3Ly8tTq9XNfURjYyP1amZmZk5ODl4M4KWxcbncuXPnNp1qgslkxsTEvN6iWzqomfQoT548+f777/v37798+XKdKSIwPM3J3LlzCYK4fv36ggULsrKymkvR09LSPvvss1GjRhmeuQTPwSgUCnXuCoRQbW3typUrf/rpJ2tra7lcrn2ee/ToMX78eLzQ3HfffZeammr8LCPYoEGDFixYoJNz2tvbb9269eOPPyYIIiIiwvg107T16dNn6dKlTk5OK1eu3LJli5+fH41G4/F4+/bt+/HHH7W7qjKZzFmzZl2/fn3hwoXUCWcwGMOGDcPF/vrrr48//njAgAEnT56kBnxSfQ69vLzmzJnDZDLFYvGSJUu6d+/+wQcf/PXXX00HYbJYrM8++ww/6Thy5Ejfvn27d+/+3Xff+fn56dxjTk5OuLGroqJCexLCfv36jR8/vunB9ujRIyYm5j0P4nJwcPj222+bPv0xTCgU1tbWIoTatWtn/OymAAAAAADa3kL7GEmSYrG4ufE86enpu3fvRv9ewbaoqGj//v0EQeidzwMnY7m5ub/99puvr6/OwrLavLy8tm3btnXr1uvXr+/atev06dMff/zxJ598ght5goODw8LC0tPTu3bt+lYyDYFA8Oeff2o3buisP4YQwitc19TUZGRkrFy5UrtWKpFITp48eejQoaioqBUrVuAeXNoTZri7u2/YsOHy5cs//vjjsWPHevTo8f333+udFkIkEv3+++8PHjzgcDilpaUkSUZERDTNsurr6+vq6nRSoJCQkMOHD588efLSpUvl5eUcDmfQoEHjx493cnKiMhypVGpmZqa3NlxfX3/ixAk2m02n03HTyvnz51NSUkiS1DufR3p6+saNG8ePHz9u3DgDjW8EQXz66aeOjo7btm1LT0+fPn16796958yZ4+fnR529bdu23b59+7vvvhs+fLh2Z1cGg4FX8k1OTsaLCKvV6qtXr+bn55MkeerUqVmzZlEpUEFBwffff19XV7d169bQ0FBra2udZwEODg5Lly4NCAj4+eefL1y4YOAq6LyrS5cuY8eODQ4O1jv3ZlpaWlxc3LRp04wcE9gUk8n8+OOPP/roI52Ovnr/6PR2Bg4NDd21a9evv/768OFDOp0eGhr66aef2tvbz5s3TyAQ3Lt3LzIyEk9/EhUV5evre+DAgbt37yKEgoODp0+fbmZm1nSeUh8fn927d588efLs2bM1NTX+/v5DhgwZNmzYN998o/3XbWVl1b59+wcPHugs0sVms/F8j0ePHk1LS1MoFIGBgWPHjh08ePBLO9++LQRB+Pr6Dh06dOTIkXqfFxhWXl5eWVmJEOrYsePrZdoAAAAAAG+nv+LTp09///133KnJ09MTV5GxkJCQ2bNn4/9fvXp1eXk5XjkKL2irvROJRPLjjz+6ubn9/PPPxlTIHB0d165d26tXr2PHjsXExHTs2JGq9Ht5eeEk8G3hcrnjxo1jsViWlpZU6rJ06VKdYosXLxaLxdpPyhsaGi5cuHD+/PlBgwb9/fffDg4OBQUFq1evvnz5Mm5+obrnMZnM6OhoHx+fVatWJSUl3bt3Lzo6umkkzs7Oy5YtO3/+/A8//ECSZI8ePSZPnty0Ck6SpN5GNgcHhzlz5syZM0d7o3be29DQ8M8//xw9ehRvbNOmDbVza2vrcePGcblcDocTExNDvUUul+vM54EnqDx27NjKlSvDwsJeOhE/nU4fNmyYk5PTsWPHHBwcPv/8c+oWKigo2LBhg7u7+9GjR3VGEiKELC0tp02bVl9fv3//fu0ZXBwcHPr27RsdHY1ryQ0NDadOnbp+/fqnn346YMAAhNCjR4/++usvnHIQBEHNwEGn0yMjIz08PJYsWfLw4cMXL15Q+Vh0dHTTK0Ldz81JT0/fvn37rFmzxowZo5P+vao3WdaMRqN16NAB98PUjvnKlStNSwYGBm7ZsgX/k7qf9U5so3M74cI6nTnxomRHjhwRCoUFBQXabbl4Gbrw8HADkUdHR/ft2/eLL754kxWibW1tm+tiqvMH+0ry8/MRQlwu18hZLgEAAAAAmnoL+RhBEGFhYcHBwQcPHiwqKpo7dy6uNzc2Ns6dO7d379563+Xg4LBhw4YOHTpYW1ujfzf7jBo1qn379savo8VkMkeOHInbTAw0pr0JOp3evXv3sWPHWltbv+oIK6FQeP/+/Z49e44ePZpqOfHz8/vuu+86d+58+vTpIUOGaK9vhhDq2LHjxo0bi4uLDUxZQaPRBgwYYG9v7+3t7eLiotMmU1dX5+Hh0bVrV+1Z/ozH5XJnzJjRt2/fzZs3jxgxAi/4JpFI2rdvj/fZtDOhmZnZgAEDxowZQ435uXnzZnFx8aZNm0iSNP5quri4bN26VaPR4CNSq9XXr18vLCxcs2aNgZynY8eOhufSJEny8ePH/fv3nzp1KnWuevTo0bVr1+3bt1dXV3/yySfBwcHabwkLCzt06FBDQ4MxA/MMCwkJOX78OP7/N8zHDJ+6yMhI7ecgLUqHDh1CQkJSUlKysrKGDBnyqokln8/n8/menp6mPo7/IpVKMzMzEUI9e/Zs06aNqcMBAAAAQGtFazqTNUKIw+EYn968UuFX8u7CgJghZoj5fYZx8eLF3bt3e3t7r1q1Cjc5Grnnmpqa3377TaFQLFq0CD+7MeGp0y5cVFS0evXq+vr6FStWvHZP1Pcc89sFMUPMEDPEDDFDzBDz2yms0ae+vl5jtFcqXFZW9o72DDFDzBBzi425qqrqk08+CQ0NjYuLe6U9X7hwYdOmTTk5Oe8/ZsOF//zzz9DQ0K+//losFustDPcGxAwxQ8wQM8QMMZs8jFYRs4nnVwQA/C9wdHTEC7snJSUpFArj3xgVFbVkyRIjW8bem7q6utu3b3M4nIkTJ77JwDYAAAAAABOvPwYA+B/xwQcffPDBB6aO4u2wsbF5uzMGAQAAAOB/FrSPAQAAAAAAAIBpQD4GAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGpCPAQAAAAAAAIBpQD4GAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGpCPAQAAAAAAAIBpQD4GAAAAAAAAAKYB+RgAAAAAAAAAmAatvr7+fX6eWCzmcDimPmqIuSWCmCFmiBlihphbJogZYoaYIWaI+d0h9H7qK0UDhaEwFIbCUBgKQ2EoDIWhMBSGwlD4NQoTRu7lDc2aNSs1NfX9fNZbp9FoaDSaqaOA4FsZCB6Ch+BbkVYdPEKoS5cue/fuNXUUAAAAXsd7Gj/WepMxhFCr/pGG4CF4CL4VgeAh+NfTqn9kAQDgf9x7ah/DWukPRpcuXSB4CB6Cby0geAj+fzN4AAAArRTMrwgAAAAAAAAApgH5GAAAAAAAAACYBuRjAAAAAAAAAGAakI8BAAAAAAAAgGlAPgYAAAAAAAAApgH5GAAAAAAAAACYBuRjAAAAAAAAAGAakI8BAAAAAAAAgGlAPgYAAAAAAAAApgH5GAAAAAAAAACYBiEWi/W+0Nz2Ny8MAAAAgLcL/xC/u99uKAyFoTAUhsLvqDDB4XD0vkHv9ub2bnxhAAAAALx1HA7n3f12Q2EoDIWhMBR+d4WhvyIAAAAAAAAAmAbkYwAAAAD4j4aGBrVabWTJXbt2nTt3zkD5xMTERYsWJSQkSCQS7e2nTp3auXNnWVmZRqMx/ClPnjxZt27ds2fPcEmSJMVicdN3iUSi6upqU588AAB4ZYSpAwAAAABAC3L27NlTp0717t3b0tISb9Hb00alUiUnJ2dmZhIEIRKJJk6cSBD/qlTw+fxTp04NGzbM19eXyWQmJCQolcrQ0NDExMSrV69OmDChTZs2ubm5Z8+effHixfLly21tbZsLhiTJ69evnz17VqFQzJ0719raurGxcfXq1SRJBgYGUsXEYvG1a9fEYvHChQtHjRpFp8PjZgBAqwH5GAAAAAD+w9LSsqSkhMFgzJ49G28pLy93dXWVSCRZWVkdOnSwsrLC2+fOnat3D1wul0ajffLJJ3Pnzm3Xrh1CyMrKSi6XHz16NCsrq0+fPtbW1llZWVwu95NPPjGQjCGE+Hz+nTt3eDze5MmT2Ww2QkipVAoEAoTQ+PHjqfcWFRXdvHnT09Ozd+/ekIwBAFqX1p2PaTSaAwcO/PrrrwghT0/Pn3/+2d3d3dRBvURRUVFMTAyfz9fZzuFwgoKCJk+eHBYWRqPRTB3mS1RXV8fGxl6/fj0/P58giMDAwOHDh48YMcLCwsLUoRmyc+fOQ4cONffq0KFDV65cyWKxTB2mfiKRaP78+ZmZma0xeISQWq3Oyck5ffr0vXv3ampqEEJeXl49e/b8+OOPPTw8Wv49DwBITExcsWJFeHj4ihUruFyugZIEQQwZMuT8+fO//fbb5MmTEUJqtTo+Pj4/P3/jxo3du3dPS0srLCwcPny4h4eH4Q+9f/9+SUlJTEyMr68v7vEolUolEgmVE2pjsVgt+WsQAAD0at35WH19fUpKCv7/kpKSrKyslp+PNUcsFicmJqakpCxfvnzEiBEttnqq0WiuXr26YcMGatZOkiQzMjIyMjJOnTq1adMmHx8fU8cIWhyZTLZr167jx49rbywuLi4uLj59+vSiRYuio6Opnk4AgJZDrVbj3yOZTHblypVOnTppJ2MNDQ21tbWurq5Nf7PatGkzYsQIZ2dn/LucnZ1dX1+/detWBoMhkUgePXpEkmSvXr2YTCYur9FoCgoKOByOs7MztZO6urobN24EBAQMGzZMpVIdPHjQ3Ny8a9eucrlcbz4GAACtUeuuABUXF2dlZVH/vHbtWkREBO7P0EqRJHny5Mnw8HBHR0dTx6JfSkqKdjKmrbCwcPPmzevXr7e3tzd1mKAFUSgUP/7445kzZ5p79aeffvLw8OjWrZupIwUA6Hr8+PGqVavCwsKYTOaDBw/69Olz+vRp/BIeP/b06dP58+ePHz+e6iVYVlaWnJwsk8kIgqipqcE/00wmMzAwcM+ePUlJSW3btpXJZGw2++HDh9nZ2Tgle/78+Y0bN7hc7rp160JCQvCukpOTMzIyli1bxuPxcnJyzp8/r1AozM3NXzoFCAAAtCKtOB/TaDR37tyRyWRt27YNCAg4f/58RkZGWVmZv7+/qUMzypQpU+bNm0f9s7q6etOmTQkJCTk5OSUlJS0zH6urqztw4IBYLCYIYvz48ZMmTeJyuUqlMjExcdOmTXw+PyUlJSUlZciQIaaO1BAej/fLL794e3ubOpDX1PK7Jup48ODBuXPnEEIODg4zZ86MjIy0sbEhSTI7O3vnzp3p6ekymezy5cudO3emnpQDAFqI8vLy8vJygiCWLl26dOlS7Zfkcnl5eXlmZmZAQID2kC03N7eJEyfK5XJLS8u7d+/+8ccfCCEvL68pU6bgSUEeP34cExPj4+Mze/ZsMzMzgUAQExODEDp+/Lj2N3N1dfVff/3Vp0+fAQMGkCR58eLFmpqamTNn9uzZ8+TJk6Y+MQAA8Na04nxMJBI9fPgQIRQSEhIVFXX37l2BQHDnzp3Wko/pcHR0jIiISEhIIAiixY5FzsrKSk9PRwhNmjRp9uzZuIMZg8Ho06cPjUaLjY0dM2ZM586dTR0maEHkcnlcXBxJkhwOZ926dVQjGEEQnTp1Wrdu3caNG/v27RsREQHJGAAtEEmSr/EugiCsrKwKCgp+/fXXsWPHHjt2rLKy8tNPP3V3d//iiy/u3LnTpk0biUQilUqtra3VarVGo7GwsND+Eqivr//ll19yc3MHDRr04MGDtLS0CxcuBAcHjxkzBnfQ4PP5Bw8epJ5MiUSi+vp6w6PaAACgZWrF+VhOTk5OTg5CKDQ01Nvbu3PnzgkJCcnJyaNHj7axsTF1dK9Go9FUVFTEx8cjhPz9/VvsKLinT5+SJMlms/v27asz2iciIiIiIsLUAYIWp6am5unTpwih/v37N83VeTzeTz/9ZOoYAQAvkZWVtXv3bp2NJEnm5eU195bCwsJvv/129OjRXl5ex44dCwkJ8fHxWb9+/cKFC9VqdVRU1JUrV+RyubW1tUgkqqysDAoKoqbXRwgxmUySJNVqdXp6uqenJ55QcfLkyVwuF+djPB5v6tSp2vMr3rlzx9TnCQAAXkdrzcdIkkxKSiJJ0svLKzAwkM1md+vWLSEhIT09/dmzZ126dDF1gC936NChpnP9cTicefPmtczOiiRJ4l9Ed3d37fHWrQ6fzx8zZkzT7Xv37m0Vd05cXFxcXJz2lpbcg1EsFtfV1SGE/P39oQUMgFaqQ4cO1Nz3FLlcXlFRUVhY2LR8RkbGpk2bpk6dOmTIENyrQiAQfPbZZxqN5tq1aywWq2/fvleuXBGJRE5OTkKhECHk7u6u/SXGYrFWrVr1/fffEwRx7dq1GzduTJs2LTg42NRnAgAA3r7Wmo/V1tbimRVDQkKcnJwQQmFhYTwej8/n37p1Kzg4uJXO1TZ48OA2bdqYOgr9SJLEFWsmkwkVa2AkqVSKK1vaT76brvrQ2gf1AfD/lUqleqXyJEleuHChtLR08+bNrq6uCoUiOzvbz89v2rRp1tbWvXv3vnnz5hdffMHhcGxsbEpLS9u2bVtVVYUQcnZ21nmoZG5ujhAqLi7+9ddfu3btOmHChBbbmR8AAN5Eq0xaEEK5ubm4m0SPHj0YDAZCyMXFpXPnznFxcWlpaUKhsGU2Mb3UmTNnHj58uHXrVl9fX1PHosvMzAwvL6ZQKBQKhanDAa2DpaWlnZ2dUCjEa44BAFqX0tJS9Cr9FQmCGDp0qJ2dHf5nVVXVmTNnysvLHz9+7OXlxWKxNm7cyGKxpFKpi4tLUVERSZL4I9q3b9/002Uy2YEDBxBCX3/9tY2Njd6pfQEAoLUjmvt2e6Vvvff8FalUKm/duoX//5tvvtF5NScn5/Hjx4MGDXqfIb0GnfkVZTLZ1atXf/rpp5KSktjY2Hnz5rW0Jj4Gg4Ensi8tLa2srMTNkq1Ra2+Kacm9E5uyt7d3dHQUCoXZ2dl4hmtTRwTA/0/4h/it/HbL5XKEkEKhEIvFCoXCxcUlMjJy1KhRCKE9e/b89ddfS5YsGT58uFwu5/P5bm5uLBaL2pVKpcrLy0tLS1MqlQihoqKikpISW1vbvLy8TZs23bx508nJadGiRb6+vjwer7CwsKampqCgwNbW1s7OTiceuVx+8ODBhISElStXajSauLi4vLw8DofTuXNnjUajUqkkEomZmRkuLJVKm258dzUZKAyFoTAUfouFCTz5bNM36N3e3N6NL/xWVFVV4f7ozbl3716fPn1aV586Npvdr1+/s2fPZmZm1tTUkCTZ0vIxhFDHjh0RQjKZ7NatW4GBgdoRZmRk7Nu3b+TIkT169IBlOgHFzs6uQ4cOeXl5d+7cSU5O7tu3L41G8/b2vnjxIi6wc+fOpgMpAQCvisPhvK3f7srKSoSQq6srh8OZP3/+okWLSktLraysaDQa/mFlsVgcDgdPmtr07e3btw8NDVUoFCRJfvvttxwO56effgoKCjpx4sSZM2cGDx7coUMHJpMZGhr64MGDgoKC0tLS4ODgdu3aafdqJkny1KlTp0+fJknyu+++69279+jRoydMmODo6FhUVESj0aqrq0+fPq09v6JYLHZ0dLSyssLH9e5qMlAYCkNhKPx2C7e4Gr8xMjMzi4uLDRRITk4uKytrXQ0gJEmmpqY+f/4cIWRmZkaj0UwdkR6BgYEhISHp6elHjhxRKpXU+mMPHz7cvn17YWHhvXv35s+fP3nyZFNHCloKBoMxYMCA8+fPkyS5bNmymTNn4hlQ1Wp1dXX1/fv38bSiAIAWgiRJ3D6GO0EwGAyZTPbLL78wmcz58+fjMk+fPsUrnTT39I3BYDAYjNjY2KSkpM8++ywwMLCysvLcuXNcLnfEiBE4qQsMDEQI/fPPP3w+f8qUKdrJGEKIIIipU6e6ublVVlaOGjUKf5D202WYXxEA8P9G68vHFApFUlISaqbXWWxs7Jo1a/DCxC08H9M7vyIWFBSExzG3NFwud9asWUuWLBGLxUePHj169KhOgYCAgMjISFOH+RLNza/Y2vsxtljdunWbNm3avn37FArFrl27du3a1bRM586dHRwcTB0pAAA1Njby+Xw7Ozu88opMJtu4ceO1a9d8fHzwE0OEULt27by9vb/88ktvb+/x48f7+fk1nWmjoaEhOzvbwcHhxYsXaWlpKSkpubm5n3/+ObVGqJOTU0hIyNmzZz09PXv27Nk0EjqdPmTIEFOfDwAAeOda31RFVVVVjx49Qgh17tzZxcVF59VOnTrxeDyEUFJSklQqNXWwryM8PLwlD34LCwtbtmyZ3iZXHo+3ePFifP4BoBAEMXny5IkTJ+rtgstkMufOnbtixQpra2tTRwoAQFVVVbm5uZ06dfLw8JDL5fv27bt48WL//v337dsXGhpKFQsMDNy2bZtIJJowYcK0adMSExPVarX2fiwsLJYtW3blypX58+cfO3bswIEDBEGkpqbev38fzwhVUlKSmprKZrPLy8vT0tI0Go3hwORyeXZ29vHjx/XOsA8AAK1X62sfS01NLSkpQQgFBwc3ndKAmmUxJSXl2bNnrWutEn9//xEjRowaNQpPY9gy0Wi0IUOGdOzY8cyZM1euXCkvLycIwt/fPzIycuTIkVTXEQC0sdnsr7/+Ojo6OjY29ubNm9q3zfDhw7lcrqkDBAD8S15enkAgWLBggbm5+f79+48dOzZt2rThw4c3/Xq3t7dfsWIFQujWrVtLliz59ddf8RhjbbW1tb/++mt2dva2bds4HM6aNWu++uqrVatWtW/ffsmSJSEhIWPGjPnxxx83bNjQ2NgYHR2tPfBbo9HU19c/e/bs/v379+7d02g0o0ePHjZsWG1tralPEgAAvE2tLx+Ljo6Ojo5u7lUWi/XDDz/88MMPpg6zWdozGbRerq6uMTExMTExpg7k1cybN097TsvWxdbWtlXPe0Gj0fz8/BYuXLhw4UJTxwIA0E8ikVy9enXAgAFdu3bdtWvXjRs3fvrppx49euTm5paVlVlYWOjMD2Zvb//tt9+KxeK0tLTKykrtfEwul1+5cmXPnj0DBgz466+/cIfk/fv3X7lypbKycs+ePRMmTBg3blxjY+Py5ctXrVq1cePGK1euzJo1KyQkhMFg8Pn81atXp6SkEATRu3fvlStXBgYGSqVSDodjOB+rqan566+/hgwZ0lomoQUAgNaXjwEAAADgXUhMTCwuLv7hhx/OnDnj7u5+/Phx3F+DwWA8ffp0+/btfD6fw+H4+PhQb8HjitPT07t27YoQ0mg0AoHg3LlzT548iYiIOHnypPacH3Q6vaysrLq6eufOnb6+vjQarbGx0cvL69dff929e/epU6f+/PNPOp3euXNnHo+3cePGixcvRkREeHh40Gg0oVAYGxsrl8tFIlF9fT1JkgcPHtSeX7G+vl4gEEyePFkul6elpcXExLi6upr6jAIAwMtBPgYAAAAAJBQKExISVq9e3a5du3bt2mm/ZGFhMXDgQA6Hc+3atQkTJmjnYwihsLCwsLAw/P8ajcbc3HzChAmffPKJdhmZTBYbG9vQ0PDJJ5+4ubnpzCFsZWW1cOHCqVOnWllZUSmWra2t9k7s7Ow++ugjOp1uaWm5dOnSpvHrbCwvLzf1GQUAAKNAPgYAAAAAZGdnt379egMFunXr1q1bN8M7odPpHA6n6XSLbDZ7woQJBt5Io9FeOpQU79zU5wkAAN6y1je/IgAAAAAAAAD8/wD5GAAAAAAAAACYBuRjAAAAAAAAAGAakI8BAAAAAAAAgGlAPgYAAAAAAAAApkHonRCWw+EYP1HsKxUGAAAAwFtXXl7+Tn+739GeIWaIGWKGmCFmQu9qiWKx2PhVFF+pMAAAAADeOldX13f3211eXv6O9gwxQ8wQM8QMMUN/RQAAAAAAAAAwDcjHAAAAAAAAAMA0IB8DAAAAAAAAANOAfAwAAAAAAAAATAPyMQAAAAAAAAAwDcjHAAAAAAAAAMA0IB8DAAAAAAAAANMg3ueHdenSxdTHC8G3PhA8BA/BtyIQPAAAAPBK3lP7WGhoqKmP9PVpNBpThwDBtz4QPAQPwbcirTp41Mp/ZAEA4H/ce2of27dvH/6fV133msPhmLwwxAwxQ8wQM8QMMbf8mAEAALRGMH4MAAAAAAAAAEwD8jEAAAAAAAAAMA3IxwAAAAAAAADANGj19fXv8/NaY1d4iBlihpghZoi5ZYKYIWaIGWKGmFsmiNl4hN5PbSGDnqEwFIbCUBgKQ2EoDIWhMBSGwlD4/3Fh6K8IAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGpCPAQAAAAAAAIBpQD4GAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGpCPAQAAAAAAAIBpQD4GAAAAAAAAAKYB+RgAAAAAAAAAmAbkYwAAAAAAAABgGpCPAQAAAAAAAIBpQD4GAAAAAAAAAKZBq6+vf5+fJxaLORyOqY8aYm6JIGaIGWKGmCHmlglihpghZogZYn53CL2f+krRQGEoDIWhMBSGwlAYCkNhKAyFoTAUfo3C0F8RAAAAAAAAAEwD8jEAAAAAAAAAMA3IxwAAAAAAAADANIj38zGzZs1KTU019cG+Jo1GQ6PRTB0FBN/KQPAQPATfirTq4BFCXbp02bt3r6mjAAAA8DreU/tY603GEEKt+kcagofgIfhWBIKH4F9Pq/6RBQCA/3HvqX0Ma6U/GF26dIHgIXgIvrWA4CH4/83gAQAAtFIwfgwAAAAAAAAATAPyMQAAAAAAAAAwDcjHAAAAAAAAAMA0IB8DAAAAAAAAANOAfAwAAAAAAAAATAPyMQAAAAAAAAAwDcjHAAAAAAAAAMA0CLFYrPeF5ra/eWEAAAAAvF34h/jd/XZDYSgMhaEwFH5HhQkOh6P3DXq3N7d34wsDAAAA4K3jcDjv7rcbCkNhKAyFofC7Kwz9FQEAAAAAAADANCAfAwAAAAAAAADTgHwMAAAAAAAAAEwD8jEAAAAAgPdEqVQqlUpTRwEAeDWNjY0kSb6jnROmPjoAAAAAtHTp6en//PPPsGHDOnXqxGazjXyXUqnMyMjw9fW1sbGhNsrl8h07dvTs2TM8PPy1gzly5MiAAQO6d+/O5XJpNNrr7UehUPD5fHd3d/zPxsbGX375xdHRcdiwYQZ2KxKJNmzY0KNHjwEDBlhZWSGE+Hz+77//PmnSJE9Pz5d+6NOnT+fPnx8YGNi+fXszMzPtl5qO+M/Ly5NKpfPmzWvfvv1rH2YLVFBQsG/fvlmzZvn4+Oi8JBKJNm3aFB4eHhoaqnM2Tp065ezs3KNHDyaTaZKw09PT9+/fP2jQoPDwcB6P9xp7qKur27JlS5cuXSIiIszNzU1yFJhcLs/Pz/f19aW2FBUVHTp0aMaMGdRfxGvAly8oKGjAgAEajeZdRJ6SknLixIlPPvkkODiYTn+FhqVLly6lpaWNHTvWz88Pv/H06dN0Ov2DDz4w5o66c+fOunXrunbt6ufnh7coFAq9b1SpVE+ePOFwOAsWLDDyZEI+BgAAAICXUKvVFy5cePjw4Y4dO6jqyEupVKq///77+vXro0ePnj9/Pq6ApqSknDlz5vLly1999VW/fv1eL5hbt26VlZWFhIQYk6U8e/bs/v37MplMZ3tGRkZSUtKwYcO++OILDodjbm7OYDB27NiRk5PzzTff2Nra6t1bcXFxfHz8/fv3ORxO37596XQ6l8u1sLCYMWPGihUrIiIiDIdkZWVlYWEhkUg++eQTW1vb2NjYNWvWDB06dOXKlbW1tadPnz506NCqVauio6NFItH8+fMzMzPz8/Pbt2+vs5/S0tKkpKTGxkYDn4XTuSVLljg5Ob3GeabI5fLc3Nzbt28nJiYuWLCgW7dueDufzz9//rzx1W5cf62pqblw4YJCoaipqVm7dq1OYlNTU/P48eO7d+8uWLDAzc2NOplSqTQxMfHWrVshISGbN2+2t7d/kyPSaDSZmZmnT5/+8ssvuVyuke9Sq9VJSUl1dXURERE610IgEAQHB790DxUVFUlJSXfv3mWz2a/9PAIh1NjY+NNPPzk5OQ0dOpTH4xmfq6vV6rKysrNnz545c0YsFs+cOXPcuHH40hw7duz8+fPV1dXff/+98eekqfLy8pSUlE6dOjk4OLz2Tpojl8v/+eefhISEhoaG1atXOzo6Gv/Ge/fuxcXFSaXSRYsW4diCg4NjYmIePXr09ddfN/f3TrGzsxOLxebm5lOnTmWxWDt37jx06NCUKVPmzZsnl8vXrl0bFxe3d+/eLl26FBUVXbp0qb6+/sWLF5CPAQAAAOA1FRUV7d69e8yYMSEhIdRGLpf7GhU1kiT79euHk7G6urrjx48jhL7++usRI0ZIJBJcRqlUqlQqFotl/G5ZLJalpSX1T4VCce3aNR6P16VLF52Sfn5+bdq0kcvlVlZWVM0VV6EQQk3bYXr06NFc5Uyj0WRkZJAk2b9//169euGn7ARBDB8+/NKlS6tWrdq2bVvTAN6Qh4dH0wq3u7v7xIkTGQwGnU4vKiqKiYkhCGLnzp1t2rTBBe7fv//HH3/Q6fTbt2+PHDmyuZ2LxWIajYYb+ihSqZTP5xcUFKSmpt6/f7+qqsrLy8vW1rZHjx7Pnj1r166dtbU1QojH4w0bNszOzs7S0lK7pUKj0ezYsePIkSNhYWGLFy+mGmGoBsDly5c3F095eXllZeW0adMGDBigfdQvXrx48uQJQRDjxo0znIxJpdJr167x+XwDh6xQKHBO+OLFi7Vr17q5uWkXUCqVSUlJOTk5arVauw0E77O6uvro0aPUvYrTS7VavXDhwsGDBxu+lLm5uUKh8PPPPx84cGBDQ8Nr3xJ1dXWPHj3Ky8vTaDRTp059aT6GW8MSExMvX75cUlLC5XKnT58eEhJCZQupqalxcXGhoaFUMqbRaOrr662trQ3vvKGh4cmTJyEhIdotRebm5jp3lF4kSf70009//fVXUFDQDz/8YMzc8SkpKdevXw8PD29sbCwqKjI+HxMIBNnZ2Ww2e/z48VSi6O3tPXDgwBMnTtDp9KVLl77S989LWVtbG9+I2rrzMY1Gc+DAgV9//RUh5Onp+fPPP79JG+v7gb80m35NcDicoKCgyZMnh4WFtfw+CdXV1bGxsdevX8/PzycIIjAwcPjw4SNGjLCwsDB1aAYtXYo2bWr21YkT0b59yOh+OBD8KxAI0AcfoAcPWmXwCCG1GqWmot270aVLCP/xtmuHhg1Dc+YgPz/U4v9gAXgNeXl5169fLy4u3rRp05t3D8Md8zQaTUJCQlJSkqen5/Pnz/fs2YMru1KpND4+3tLScv369f7+/tS7lEplcnJydna2SqVCWr2D8G8on88/ePAgrkKpVKrk5OTMzEwOh4M7E+oEwGAwGAyGgdiMJBKJEhMT2Wz2sGHDtE+Lm5tb27ZtHzx48Pjx47eejzWH6vAmkUjq6+t9fHyofqEajSYtLY0kyaFDh06YMMHAiLW8vLyYmJgBAwZ06NChoqJCIBBYWlpyuVwfHx87O7tp06bNmzdPO+/VQRB6VrKVSCR5eXkcDmfmzJnaPeIMkMvlGo2GxWI9fvw4ICBgzJgxBEE0NDRIpVKcHjx58kQoFPbr1++lzUqWlpYffPBBQ0ODTpZIKS8vd3V1NZATMhiMiIiI0NBQJpMpl8upA0xNTT1//jyPx5s6dSrO2EmSzM/Pnz9/Pk4/dBb8FQgELBaLykzkcnlycnJwcPBHH31EEHpq4AKBgCRJYyrxlZWVpaWlnp6ekZGRL+2zp1Ao8vLynJycJkyYMGjQINwkOHLkSHwIYrG4rq7u6NGjMpnMycnp9OnT+F3Pnz+/ffv2559/PnHiRBxtdnb2jRs3tCNXKBTx8fGlpaVjx46dO3euMTkYRaPRPHjwIDY21vi3CASCw4cP29raTp06taysbN++fT4+PkY+IUpNTS0pKRk6dGhAQAC1kSCI0NDQEydOZGRk1NTU6KTl71Przsfq6+tTUlLw/5eUlGRlZbX8fKw5YrE4MTExJSVl+fLlI0aMaLEpmUajuXr16oYNG6gvHZIkMzIyMjIyTp06tWnTpqZ9wQFo3SQStHw52rnzvzY+fYqePkW//YZ++gl99hkiWvd3KQA6FApFUlISQmj06NFeXl7l5eVNy6jV6vj4eDab3bNnT+3fLIFAcPXq1X79+jXtrfT8+fNDhw6FhoZu2LAB16Jw/58tW7ZUVlZGRkbqtHswGIxevXp17tyZyWQyGAyqdaVptRghNHfu3PdwZnJycvLy8iIiIoKCgrS3W1hY9O7du1+/fiNGjKDOYXx8vL29fffu3bVL4tyJJEmcTD59+hQhlJeXt3///oaGhuzsbIRQQkJCRUWFXC7HmWdpaanhHK+hoUEmk7m6ulIZWn19fWZmJkKoT58+LBbL8AwiCoWitLR08eLFVAXd+FVuEUJ4kgPtanpxcXFGRsbcuXNDQ0Oblq+rq0MIaQ8pRAhVVFQsWLDAycmpvLzcwcHh7NmztbW1t27dYjAY69atCwgISE5ORghFRkZSlX6FQlFYWOjl5dW0WUNvlviqxGLxzZs3q6qqdNrHqAcB1FOAyMhIvR1cnz9/jnNdDw8PfFHu3bvn7e39999/oyajjxobG69evVpbW7tgwYKPP/7YcJaVkZEhk8m6dOni7Oys85JGo0lOTn7+/PnEiRPxmWEymZ06dcKvCgSCppfvxIkTSUlJ06dPnz17Nn48kZycfPz4cScnp44dO1KRBAYG2traOjo6aj/amDdvnuHTqFAo5HI5blClqNXquLi4zZs3N+1F3BySJE+fPp2WljZt2jRfX18fH5/Lly/v3Llz6dKlLx3RKpPJ7ty5QxBEVFSUzt3i7+8/bty4ESNGuLq64i2lpaV3794dOXKkzm6FQiH6958qQRDp6ekIofT09N27d5MkmZeXhxA6f/58SkqKSCSqr6+XyWS1tbXe3t7GHF3rrkMUFxdnZWVR/7x27VpERITx44xbIJIkT548GR4ebnwL7HuWkpKinYxpKyws3Lx58/r169+wVzcALUhjI1q0CO3Zo/9VuRwtXoz8/NDAgaYOFIC36fnz5/fv33d0dLS0tHzw4EFNTQ2ui2g3SeHBVwRBLFy4cNSoUVR13NbWtqioaM+ePStWrAgLC6P2KZPJDhw44ObmVl1dnZ+f7+DgQKPRNBpNXFzcuXPnPD09Z8yYoZPCSSSS2NjYXr16eXl5GRm53sof3pVMJnN0dHyTx524SyRJkgMGDCgoKEhJSVEoFDplDh06hP67vW7JkiVDhw7Vrl6HhIT06tUrOjqaqhqWlZXJ5XKCIKjehjhmW1tbV1dXvVmNttLSUoQQnU6njg5XkAIDA1/63jf3+PHjhQsXRkREUM0LT58+NTc3Lysr2/PfX574dMXHxzc0NCxatGjQoEHap4UkSYVC8eeff+LE5s6dO2fOnAkKCnJ0dMzPz3/w4IGdnV1mZmZRUZH2GY6Ojl60aNG7OC4ejzd27Fg+n8/j8XCcTR8EvPQpAD5kPOIIIbRkyRLqJZ28VyQSpaWlaTSarl274o9TqVTZ2dn4NtMurFKp7t69ixASCAS///67zic+f/78xo0buOHOwDBIDLejPnjwYPPmzZs3by4oKFixYoVQKNywYQNCaNmyZdrdlWk0GofD0dvOLBKJ4uPjq6ur8UMEmUx24sQJMzMzNpuNk0Pqr0Cj0RQUFPz22283b958pcuRkpLy559/Um2nHA5n+vTp+Hy+NCXD909ISIibm1tsbGxFRYX2q9bW1rdu3bp16xZC6MWLFzdu3FAoFMnJycuWLdOujWs0mv79+w8cOHDw4MEEQcyePVssFldWVrJYLB6PFxMTQ5WsqKhwdnb28fFp27atkUfXivMxjUZz584dmUzWtm3bgICA8+fPZ2RklJWVaXd1aMnwEEDqn9XV1Zs2bUpISMjJySkpKWmZ+VhdXd2BAwfEYjFBEOPHj580aRKXy1UqlYmJiZs2beLz+SkpKSkpKUOGDDF1pAa1aYMuX0aBgaaO438veNQauibquH4dHTiAEEI8Hlq1Co0bh+ztEUmilBT0zTfozh0kFqNjx1Dv3sgUM2Wp1WoDz1ANvwpagpZ5jTQaze3btwUCQUxMzPDhw2k0Wnl5Oa7B6DRJ6UUQRHR09LVr1xYvXkx1CVOpVIcPH66pqVm8ePHOnTsXLFiwbt26QYMGpaSkbN++3dXVdevWrU07tuExbPn5+bgHl4H+itSnJCcnV1RUrFixQmdvubm58+bN69q1a+C/vz+pR9rGw2kqm82Wy+UBAQG4vtG0caampqa8vPzzzz8nCKJpW1PHjh136rS3I/Tw4cM1a9YEBARs376d6q5mZWUVFRVVVFT00ip1SUkJDk8sFrNYLJIkr127JpPJ+vfvT7VDWlhYEG/ckl9aWpqWljZ06FCdLqxisbikpGThwoU4Gz9//rybm9tnn32G/xkTE8Plcnfs2GFmZqZSqVJTU5VKpa+vrzE3v7u7u52d3cmTJ2Uy2cKFC6Ojo3HOKRKJcItZREQEnh/lNQ5Ho9Gkp6cnJSVNnjxZb187Op3O4XCMiVOtVmdkZJibm7dr1+5NzjCNRqM+zszMrGPHju3atVMoFHV1dVQDTn5+Pn6EsWjRIr39woxs4aypqbl161ZiYuL69esdHBzu3r177tw5Ho+Xn59fXl6+fPly7ecpBigUitzc3L59+3I4nIaGhvT0dIFAMG7cOHNzc5yP4QcN+LiKi4vnz5+P/4RdXV1FIpExTWQFBQWbN282MzNbsGDBs2fPhEJh//79Q0NDx48fv2/fPolEopM7aSNJMj4+XiaT0el0MzOzESNGSKVSvX1Z09PTe/fu/cMPP+jdz+DBg5uOD7x06dKhQ4cGDx68YsUK6hbi8XgDBw6sra01vgNnK87HRCLRw4cPEUIhISFRUVF3794VCAR37txpLfmYDkdHx4iIiISEBIIgWuDPM5aVlYXbZydNmjR79mz8zc5gMPr06UOj0WJjY8eMGdO5c2dThwnAWyKToWPHkFKJ7OzQ0aP/aQQjCBQejv78E82di0aORB98YJJkDCFUWlrs5tamudEvhl8FLUHLvEZlZWVxcXFRUVHjxo17vdakNm3a9OzZ89y5czdu3MCT7x07dszGxuaHH36wtbX18/O7deuWUCi8devW2rVr7ezs1qxZ0zQZw92uZDJZSEhIdHQ0+nctMyMjY9WqVSEhIV999ZXOLPC457ynp6eFhQUeckbJzc2Vy+X+/v6ff/45fktjY2NjY2NoaKiRz7BxkoO7e2VkZAwfPpzFYmk0mqZJdXl5OZ6wcdasWf3799d+SSgUXrp0qWkfE9xrUaPRnD17ljoiah7CyZMnf/75581NNiCXyysrKwmCeP78eX5+vqOjY3Z29vXr1xFCL1682LNnD37kP2nSpBkzZjQ3FFA7uW1uFm+xWHzt2rWampqioiID8RhDO+t4qby8vCtXrkRFRUVGRja9IbUnnMjPz797967hOSeRVrpCNSU9e/YMV+h1hizqnA0DDwLS09PT09Pd3d3XrVvXsWNHvZdJo9HoDLNXq9WVlZXOzs4GzgYe+og7eSKtxyWffPKJkdNFlJaW3rhxA6c9uCsdSZI///zznTt3FArFN998g2doHDt2rJ2d3b1790pKSlauXBkVFaV9toVC4ZUrV7R7b1LHjhsqg4OD165dq3eoIU7MtLcQBDFz5sxevXotWrTopfkYn8/fuHGjUChctmxZWFjYuXPn1qxZ8/PPP69fv37q1KmNjY2HDx8uKChYsmRJeHh40zNZVlYWHx+PbyS8vgWHw1Gr1RqNRvsAlUrlxYsXz58/HxERsXDhQhcXF+2dlJSUxMfH69xaCoUC14olEsnRo0ep7fi+Qgjp9B0woBXnYzk5OTk5OQih0NBQb2/vzp07JyQkJCcnjx49WqdTcsun0WgqKirw7eLv799iR8E9ffqUJEk2m923b1+d2ysiIkJn+lcAWim1WlVRUerm1gZVVqL0dIQQ+ugj1Lu3bjkPD3TunAnjbGyUEwSjuaq89qsqFSmVSqytbQ3sTaUia2sFKhXJ47XQ7x/DZDKpmZmZufnbnB3rXTN8BU2FJMlz587Z2trOmzfvtfv/M5nMHj164Ona8C/1uHHjunfvjqtK48ePHzly5P3795ctW9a2bdsFCxZ06NCh6U4KCgrOnDmDEKJqeBqNJjU1ddWqVS4uLp9//jkel3/nzp3a2tphw4ap1erjx4/3799/4cKFVlZW2mPeGhsbccLTrl07qgZmbm6+cOFC/P96O+HrePHiRVJSUocOHbKysuzs7HAytmvXLoIgZsyYof2bWFlZKZPJ2Gx2QECATu3Qzs5u3LhxDQ0NdDrdwsICv6pUKjdt2kQQxMSJE6nhZyUlJbgC+tK8RSwWFxcXBwYG2tjY3LhxIywsrFOnTmfPnn348GFYWJharV61apVCoVAoFDo5qjbtlk8DrSuLFy9+vVvitUml0pMnT3p6ehpzQ/r7+3t5eSkUCuqeSU1NnTVrlpeX186dO93c3PAc5aNHj549e7bePeAhi3i0Hs64cNPisWPHdu3a5eDggCc0Rwg1NjbiyS11rkVzp66+vn7BggWOjo5UCy1uVnr48KGBeJqqrKyMj4/ncrnDhg0zssETT8Upl8stLS3j4+NPnTrl4+Pz5Zdfrly5Ev17gk2EEJPJfPjw4bNnz6ZPnz5s2DCd1NfOzm7s2LF1dXV2dnZVVVXz58+XyWTfffddSEiIdqfNsrIyiURibW1taWmpd/VkGo3Wo0ePCRMm+Pr6FhcXvzT4srKylStXVlZWbtu2LTQ0lEaj4Uqyi4uLn58fi8WaM2eOvb39r7/+Om/evN69e8+cObNdu3bUmSFJ8vr1646Ojjj7wj2ii4qK1q5du3z5cu3HQHK5vLy8HM+n0rSpzdPT89NPP5XL5WZmZhYWFvjklJeXP336lMvlzp8/H7cGaTSap0+fMhiM9evXv9LDLELvIF0Oh6N3u16vVPhtIUkyKSmJJEkvL6/AwEA2m92tW7eEhIT09PRnz569t6mN3sShQ4dwL3NtHA5n3rx5LbOzIkmS+Lmgu7t70/Gjrcnz56jJQi4IIXTzJurb19TB/b8OHiF07Bg6duy/trSwHowymZTPL1UqFQghJBKhmhqEEOrUyVQtYAZUVVW4uLi/9FWJRMznv0CIZiAfq67mazTqmppqa2s7Ux/WK1OpVNXVFZWV5d7ebVtXPmb4CuqlUDRWVpZ7eOgOEHdwsM/OfmJhYVFSUkiSShsbeybzP6dCKhUrlY0IIZWKpNHotrYOdLpZ099utVrN5z+Xy1VPnjyZM2eOQqGgCpCksqamEiGkVCrx4BDqXRqNJisrUywWhYWF4zoQ3rO3d5vt2zdoNBozM9LFxV4sFiQn3zE3t3B2dq+oqDhw4IBQKJg/f27Hjp1u3Ig/ffovT0+fwYMjqTYHqVT87Fnu6NHRtra2XK5taWlpQ0PDlStXzp079+mnn/bp04fJZJaUlJw8efLs2bO2trZyuTw4OLh3795t27atr6+vr69HCFHxV1RUpKenOzo6Nj1qkUhEp9Pd3NzwdtztTSQS6RTDo7tdXFxYLFZWVpZEIsEFAgMD16xZw+PxqCW5EEKpqakIoc6dO+PGEL11pLi4uEOHDoWFhTk7OysUirt371paWqalpeG8USqV3r17VygUDh8+fPr06XoXDqaOJSsrq7CwsFevXm3btv3nn38GDx6MZ4/w9fWtra3NyclJSkry8vKKiIgQCoV4HKA2/MuufWVftV6ns4eqqiqVSlVeXv7LL7+Ym5vX19fX1dXZ2Njw+Xw3Nzc+n4/XNqiqqtI+LvyupjfYnTt3cFU4PT09MDCQyn/q6+vxJCUCgaC8vFwnZqo16cWLFwghc3NzsVhcXl5OdWs0/gCVSuXevXtv3Ljx0UcfjRgxws7OrqysLCsra+fOne3atZs2bZqd3X++NnXCwGemoaGhoqICN63k5uZOnDgRXyAOh/Pzzz8nJSVZWVmJxWKxWKz3zFDKy8s1Gs2FCxdyc3NHjhxpaWnZ3FE0dwVra2vv3LnT9HKXlpbevn37wIEDzs7OLi4uBw4c4PP5em88vOfk5OS8vDwrK6ucnBwnJyftpLSkpEQikTg6OtbW1lpbW+fn59fU1GgfFJPJ/OyzzxBCFRUV+KLjeJpeFLxG3I4dO7p27bpw4UI7Ozvca7rpHTtgwIA2bdr8+eefd+/evXv3rouLy9ChQ0eOHEkQxIsXL27duhUVFYXnjcRh0Gg0R0fH7du3L1iwgErdy8rKSkpKLCwsQkJCqqqq9J5YjUbzxx9/3Lx5s0ePHjY2No2NjVlZWdbW1qdPn8bffiKR6MaNG2q1etKkSdHR0dqP2wz/WRFUb1RtYrFY73a9Xqnw21JbW4tnVgwJCcGrHIaFhfF4PD6ff+vWreDg4DfvJG0SgwcP1h7L26KQJIm/4JhM5pvPfQxAy8RmW3K5zhUVLxBCqL4e4S9l7eedOTlo2DD0/LnEu41V0XOE9A/qk0jqraysjf/cV9XYKKfT6QTBeOmrVlYcBwenmppqA3tzdOQhhJRKErVCZmZmPJ67SFRr6kD+w5irb/gKNiUU1jQ0SAWCKisr3afvTk6OoaEdAwM7SiQSDocjkdQXFua2a9eJyTRHCNXWChoaNO3b/2t2tdLS4oaGen//Dk1/u0tKCmUyWXFxeefOnfHIHIQQi8VkMMyYTLP6eglCqKamJi4ujsqaWCxmfb1IpVJUVlZXVFTPmDGDxWLhPVdWIgaDbmVlGxt7+cGDB1u29HVxcVKr0ZkzZ86dOzdhwtiuXUM7dgytrq7m8wUiUV3Pnjxqet7aWkF9fWNkZBSuzQgEVTdvXt++/RcajRYZGSmTyeLi4nAvqadPn37yySczZ87EmY/20B08pzlCiCTJ48ePl5eXc7ncxMRE3L8Iwx3wLCwsFixYgDsW4vEeeBYN7ZODs5o1a9YkJCTgYriAhYWFt7f3yZMne/TogTuPNTY2SqVShNDgwYO9vLyaqyM5ODhIJBJzc/Mvv/ySOp9UzCKRqKioSCgUfvjhh83Nz0bt+ebNmyRJBgUF9e/f//z585mZmd26dcPP5nGm19DQMHjwYNy20HQ/uI7LYDC4XC5eNkoikeiNWSgU0ul0nS5I+MTiPfB4PFtb28bGRjMzM2dn55iYGDx+LC0tDb+KEOLxeAwGw8zMzMnJSftT8LuonSCECgoKEEJdu3b97rvvmEzmsmXLAgICZs+eja8Rm83GE0twuVxXV9fmzrNarUYItWnTpk2bNhYWFtR4HmMqrrgT2vHjxyMjI//66y+VSiUQCCQSycOHDw8fPszj8aKionx9fbU7LuqEgc+thYWFi4uLXC7XOXCxWIzjcXNzc3NzE4lEes+M9r1RWlp6/fp1Ho83efJkT0/PpjGLRCKxWKzRaPQeYGlp6ZMnT9C/h2PNnDmze/fueXl5+/btk0qlK1euvHr1alxcHDV5vVqtbmhoYLPZ1J0jFottbW3v3r2LJ/JpOh84XjKha9euXl5etbW1XC5Xo9E0d1D4ouObR+ei1NTUHDhwQKPR7N+/X+eN1B1L3Sr4HPbu3TsnJycuLo7qyUmS5LFjx/CTmrNnzyKEqDB69uy5Zs2a1NRUqld2ZWVldXV1UFBQt27dDIy+s7a2FgqFTk5O8+bNE4vFK1as0H61qKjo0aNHCKGoqCicdTd3b+holUkLQig3NxcPw+3Rowe+ii4uLp07d46Li0tLSxMKhS2ziemlzpw58/DhQ73Dmk0ON9EihHC3B1OHA8C7Z22NnJxQVRVqsmCgmsGo6Rryr3ysCbVaXVNT9U7zsepqvrOz6+u9+v9Sy1kjxMir/6rXyM7Owc7OQa1WKxS6Y2PatfMXCkXUGbCysmYwmEJhDd6/XN7Q2CinCjs4OOXmZmhvwerqhBYWbGtr648+6kanE9Qz47q6uq+++orFIj7+eExqairu/RUUFLRjxw6qJlRaWqxQNPr4BGjvUKlUODq6bt++/fr1eIRQVlZWcXFBY6Oqb9++n3/+eXU1XySqoQrn5RWMGEHj8ytKSl6Ehoby+S+cnFypR8tcrpOvr+/o0R/Z2Tn06NHDycnpyZMnO3bscHR03L17d1FRUVJSUlhYWHND5wmCmDdvXlhYGE5LtG+VO3fuHD9+vEePHoZXapHL5SdOnBgyZEhgYCDOxygcDqd9+/YnTpy4fPkyXpZXKpXiSdgD38vES1Kp9OHDhwRBtGvXzs3NrVu3bnFxcUOGDMF9unJycq5fvx4QEDBo0CDDfyO4H9fGjRuzs7O7deum3eaD4cFs7u7uW7dufXcPjrWHZuGmLS6Xa29vz2KxxowZ8+233xYXF69Zs8bIaZypmU6cnZ1fY7SbpaUlHq2E190KCgoiCOL3339PT0+fOXNm3759cXvpOzoVTeEnC4WFhQRB7N27t+lVoFYD+/DDD5csWdK0dev+/fsIITs7Ox6P5+bmFhMT07t37169ei1btozNZm/dujUuLs7T05PNZuPRUBkZGVlZWcuWLdMeuZeZmfngwYMhQ4YMGDDgjz/+kMlk+EEMfvX58+cIITc3N+0zg7svGn+ktbW1eXl5c+bMeaUFzeh0eocOHbQ7Pz9+/Dg1NXXZsmVNT0VAQICdnd3ff//du3dv/MdSVFREkmTHjh3ffKWE19Aq8zGlUolnpUQIffPNNzqv5uTkPH78eNCgQaYO8yV05leUyWRXr1796aefSkpKYmNj582b19Ka+BgMBv4GLC0traysxM2SrVKrnqKwVQePWlzvxJdwckKurqiqCqWmIokE/fuHQWnJLo8erm5mbVmlUlle/hw/lH1HcI2cwWC+xqvgnTLy6r/2NaLR9AwlIgjC3f2/mlDMzAiV6l+tnS4ublzuf76uVSqSRqMRBEOh+M+CVCRJ1teLXF09y8qeEwTDwuI/f6GNjY0NDQ2WlrYG6p16o7Kystm0adPz589DQ0PT0tLMzJBYLFUoyHv37t27d49GQ3Q6/fbtJJlMlpeXx2QyysvLd+78rKamZubMmaGhHbRjQAjZ2dmPHv2Rvb3Tixcvli5dWl1dPWfOnAEDBjCZzMDAwD179nz77bfDhg2bPn263gHYBEHoHeGMa/xt2rRpOj++jjFjxvj5+TX9XSYIAtf/rl69GhUV5eTkVFVVxefzIyIijHkuTK1lhP9JjT6iVh57qcLCwpSUFH9/f39/fyaT+eGHH16/fv3cuXOzZs2Sy+WHDx9WKBTTpk0zMMoAfxA1+2JJScn48ePHjRunUyw2NvbMmTN+fn7v9NdfexjbnTt34uLiqJeCgoK8vLwSExPT0tIGDRokFAoFAgGbzTbQYQcvS40Q8vb2fo1HNjQarUuXLocPH3ZwcKioqDh48ODly5fHjRu3du1aBweH/Pz8mTNnBgYGTp061cPD4z08EkpMTMzNzR00aND169ddXFyaDjkTiUSpqamlpaURERFNMxC8MOAHH3xw5swZMzOzAQMG3Lx5U6lU9u7dm81m79q16+LFi9OmTaOSq4yMjOPHjyOEmEwmNfWFRCI5ceIEl8udMmWKlZXViBEjvvnmm02bNuFBm0qlEi+gpzOjyav2q7K3t3/pqt/GcHJy2rx5s62tbdNV11xcXDw9PR8/fnz79u2JEyfiOV3YbLbeuViawsuONZ35Bk+X8tLvk6ZaVo3fSFVVVdr9DZq6d+8e7lxu6khfAZvN7tev39mzZzMzM2tqakiSbGn5GPr3H5hMJrt161ZgYKB2hBkZGfv27Rs5cmSPHj1e6XkGAC2TXN7Al4s1kycowrtwUx85xMejkSMRjSZycVIkxKulksbGhqrQrujsWcLKinpUKxLVKBQKtVrT2CivqqpACBEEw94ezzddV1b2nEajubt7CwR8Go2mVCrt7bl2dlztz7WwYGVlpbPZVt7ezU4VW13Nd3JyedVXGxvlAkGlSqVqbJTb23MdHIytVOExSwwGk0ZDjY2Nzs6u2sO08JGam7O6du1MEASfXyoQVHl5+RnTPKhWq/j8MjqdTqfT5fIGBwcnS0uO9ufW1FTh1EIoFCgUik6dwqiBCkqloqyshEZDdPp/TePR0CArLS1Wq1VeXv6VleV4Pw4OTnZ2Di+Nx5j34ule1Go1jUYjSZLHc2OxLF569Q1fI4Wisby8RCSq5XKd3dw8aTS6SFRbUlJoa2vn5ub10gk/Hjx4yOFY/XtmCqRWq+XyBmr/NBodd1zEJ62i4oW7u+4++fzS5kayVVZWlpaWenm568wLZ1h1dfWGDRvS0tJWr1597do1KytLHx/vzp3D6HQ6nmuB+vmorq6ur68jSbmTk+ulS5dwkFlZ6XhWRi20ysqKHTt2PXz4cNq0aRMmTMDxyOVyuVw+evTooqKi2NjYGzdubN68WXsolwFKpbKwsBAh5O7ubvgHl8Vi6az+rM3V1ZUgiMLCwrKyMicnp4KCAqFQiNewfmkMbdu21W5b0O6viCcNN/z2pvPaBwYGDh069OTJk7179y4sLLx58+aIESMiIiIMrAeNRyLoNGg0R3uJs/fM3t6+bdu2paWl2nevtbW1gSpHWVlZXl6enZ0dnvqlOUqlUiaTad+W2mc4Jyfnn3/+SU5OHjdu3JkzZ3CaLZfLHR0dFy1a9O233168ePGzzz6bPn36O622PX/+/KefflqwYIHhCjCm90vj3r17CKGOHTviaXICAwMXLVrUpUsXGo22ZcuWJ0+e9OjRY/z48fg2kEgkBw8eFIvFM2fOjIiIwF+8eKGppKSkjRs34m5cjo6O48aN+/bbb1Uq1dKlSyUSSVZWlpeXF9XgjGcxfXenxTDcY1DvbD0sFsvd3f3x48dPnz5tbGyUy+VPnz719fU1cgRWSEgIXn9MpzGtqKgIj9B7VS2uxm+MzMxMw1OyJCcnl5WVGbkkdgtBkmRqaipu5zUzM2s5fW+0BQYGhoSEpKenHzlyRKlUUuuPPXz4cPv27YWFhffu3Zs/f/7kyZNNHSkAb0SpVFRVVXh4+ZsFdlKu25TzxWc2n00nvl6IZs+2tXdAarWgthZlZDrt3oeePUNanUZsbR0QQgJBJUIanaSIw7FxdfUsKSmorxe1aeOHEFKpVHl5mTQaDb8LMzMzI0nyXxOKNBObWq2mathGvkqSSoGg0tXVk0ajkaTy6dMMJtOcw3n5VLQkqSwoeOrjE4BzHoWisaDgqZ9fe9xRXK1WFxbm+vkFMhjMhw8fde3aWaPRtGnjR6UoBmg0mmfPnjo6OuOMtKFBmp+f06FDCFWTeP78mY9PO/xPZ2fX/PwcpVKBw1CpVPn52R4e3vgQGhpkfH4ZfpeFBdvZ2bWkpKC6usLd3YtOp5OkMifnsbW1jZnZS37yXvpejUZTUJDL5TrjDK2hQfbsWXZAQEfc0mXg6hu+RkymeZs2fmJxmp0dF7c12drai0Q1np5GdVyXSmVS6X/mP6ipqTI3Z9nY2P33hyrLyp6LxXWurh46qbhQKOBwbAiCoXfyvYyMDLyMsoGp7Rob5eXl5XZ2TnZ2dhqNJjs7e+vWrSUlJcuXL+/evfu1a9eCg4MYDJalpaVMJtu4cWN1dfXChQsDAwOVSmVVVZmfX5sLF+LCwnrivREEg043k8mkVEqflpaalpYkENQkJyeHhYXdvXv3xo0beIaPqKgod3f3wMDAr776isPhXLp0KTY2tlOnTsakFjKZDOdjfn5+xpzn5tja2nK5XJw7kSSZlZXF4/E6depkzHvfsH3sxYsX8fHxPj4+Q4YMoabIGzVq1O3bt7/88kuFQhEaGhoTE8NisZrLx0iSxGtJG79wrZGonoe4xQCni2/CwsIiOjp67NixwcHBRr7lyZMnQqGwb9++OiN5mhZbtWrVL7/8ol1vJEny0KFDR44cwUu64bp7Tk7Ow4cPbW1to6OjO3bs6O3tvWLFipUrV/7+++9hYWHaSyc3p76+/sSJE7gBkJot/aUEAsHu3bsHDx4cHh5u5FuaXo5Tp06NHz+earZlsVjR0dHV1dXr1q3z9/f/6aefli1bNmfOnE2bNnl6eh49evTmzZuRkZGTJ0+m7s9nz579+eefkyZNCg8PJ0lSKpWWlZWpVCpnZ+eLFy/6+fk5Ozvn5eV98sknVHusVCoVCoXUQuEth7m5ufY9WVFRUVJS8uGHHxrZtAXtY0ihUCQlJSGEeDyezh8PQig2NnbNmjV4YeIWno/pnV8RCwoKMm95k7khhLhc7qxZs5YsWSIWi48ePaq92AIWEBAQGRlp6jBfprkpCltFV8BWHXzrQaebeXh402g0NGgQIyaGUVct51hZLV+O/r24LQoLRf6+6NkzhBDq1QsZtwgM3jPVEGFmZsblOldWVmjnYxKJNCgo1MAM11VVFQbq+s29qlA08njuuMZGEAxbW/uamipj8rGKilJra1uqAYrJNLe2tquoeOHp6YMQkkrFZmZmVL+7sjJ+XZ3QxcXjpbtFCNXUVGk0aqp5kEajMxgMtVqFEzCNRtPQIKOeTNHpZu7uXtR7BYJKgmBQ8VtYsHW+M+l0Mzc3L+p4GQymXN6g3fhm+Bo1916RqEatVlPNZRYWbDbbSiCoNPKQDVwjGo1ma2tfV1draWmFEJLJJMZcnabk8oba2mofnwCdh3oMBsPLy0+tVpeWFstkEg+Pfz29VioVMpnUzU3/cCCZTJaWloYQ8vb2NvDsXywW37hxw8LCGj9rNzMzs7GxmTZt2vDhw0mSZDAIHs/JzIyBEGKz2ePHj4+JiZkzZ87PP//csWNHJye33Ny/nZwcqN3TaDRHR+eqqgoOx8bCgq1UKszNzcRimZmZWURExJAhQ/AqlwsWLBAIBJMmTaJ+6/H6UW3btjVySA+ugb35jMF2dnbOzs6jR48ODAyUSqVPnz7t3LmzzuJFzXmT9jGSJP/++2+BQLB8+XLt+m67du0mT568fft2GxsbvBCzgZ2IxeLs7GxPT883XMW4Karn4Wu3GDTVo0cP4wvj7nkIoSFDhhgevNR0zkmEEEEQeChReHh4//79O3Xq5OTkhBeP5vF4EydOxDkVj8cbN25cVVXVS+ucarVapVJZW1uPGzcOF8btNk+ePKmpqTHwRolEsmPHjrZt206dOvX1muDwIhY+Pj4DBgyorKyktpeXlx85cmTSpEl4WvIePXr88ccf165dc3Fx+eOPPzw9PWfMmEE9iKmqqlq/fj2fz09ISDhz5oyTk9OwYcN69OgxYMAAkUi0bdu25ORkqVSqdyJ+BwcHBsPYuYvemzZt2oSEhEyYMMHc3LygoEAsFoeHhxvZHALtY6iqqgpPXaL3+65Tp054lsWkpKSoqKhXGj7YQoSHh7fkwW9hYWHLli3bsGFD0/ZfHo+3ePFiI1cnBKAl+08bNUGgxYvpxw+rr97QU47FQitXovnzkdFfNTrdSFgsi4YGqeEy2khSqVarmpvV3cCrbLaV9m5ZLIvq6jpjAm7aSmNlZVVSUojQvyr0avV/+pXh3oNGnoq6OqGV1X9SDhbLIjAwWGtXNBsb+7y8TNwYZWZG4EQFE4vrmk4zqHMOtX9WaTSagZWXjH9vfb2Izf6va21uzpJKJUbuGRm8Rra2Di9eFLq6euKTYyDrbo5SqaiqKvPxaddc1YdOp7u7e2VlpVtbC+l0AiHE55fhT9QrNTX1zp07YWFhhpsXcN9C6iwFBATs3r0bIUQQBEmSDg62eAkyzNPT09fXNyMjo6SkBPeBV6vVDx6kDRs2tK5OiJv1XFw8zM1ZeJpTBoPh7x9IEIRGo1EoNPn5+RYWFnK5/N9XpP7ixYs4nWCz2dqjsl8qNzdXKBS2bdvWyMkhmmNra3vgwAH8/8XFxSUlJdHR0UbmhG/SPpaSknLq1Cmc92rfsdnZ2f/884+/vz+fz9+2bdt3331nYIawkpKSgoKC6OhoHo+nd7UokystLZXL5U3Pp0gkEggEPj4+emt6JEmePn06PT29X79+vXr1MvwReIEEaip8Srdu3c6fP//kyZOdO3eWlJR8+umn1EtisfjkyZM8Hi88PHz27NnGVOKlUqm/v3/Xrl21BxYOHz581KhRBipOEolk8+bNfn5+ffv2fe25Qx4/flxeXv7111/rtHK7urp+88031PpjwcHB06dPZ7PZ27dvd3V13bx5s/ad4+TktG7dupUrV/bo0WPUqFHaeX5ISMj06dNVKtWhQ4cWL16sndvj1lcLC4uWttAiQig6OhovNI+btQMDA318fBoaGox5L7SPodTUVDxbTnBwcNNbk5plMSUl5dmzZ8Y3arcE/v7+I0aMGDVq1Ct103/PaDTakCFDcP/jK1eulJeXEwTh7+8fGRk5cuRIarotAP7/sLJCvXujLt3RkT/RP/+goiLEYCB/fzRkMNq20/iWMb1wLzi1Wv3SJV+xqqoKR0eX13tVG51uZsyMI/iBrs60EwwGU6VS4Zg5HBsGgyEW13E4NjQazc/P2/gsgiSVhp+YtmnjW1dXW11dWVb23MbGDtfR8UsqFWn8TPFvEUkqESKrq/9TUdZoNMZ0zqQYuEZWVhy1Wi2TSdhsK5VK9dLelToUisaqqnI/v0DDT9DpdDqbbSkS1djbOzc0yNC/OljiY1EjhGprq3ELamlp2fbt2y0sLKZPn25h8V+/tjY2NtqfIpPJJBLJs2fPqIFb2q/a2nJqa4Va/7Rdvny5SqXS7iBHkqRGg0SiGqqbpb29o739f6qtSqWisLB4w4YtHA5HqVQOHDgQb7e2th48eHBcXNzixYvbtGkzYsSIfv36NTegSK1WK5VK3JQqkUhu376NEOrSpQue4f2VznZzcnNzzc3Nqc6Kcrn877//7tWrF14rtqnXbh8rKCjYtWtXVFSUdncyhUIRGxu7c+fOKVOmfPLJJ/Hx8T/88MOcOXPmzp3bs2fPprPG4eFn1tbWH374IU6e8fY7d+40bTLCC6O1HEqlkiRJvRNFaDSaS5cu/fHHH6GhoYsXLzY8ph3PwSiTyUQiUdOXrl27tmXLFhqNFhERQT0FQAhxOJwZM2bcv39/6tSpVlZWH3744eDBgw03RXp4eHz33Xc6Gw33lW1sbDxz5sy4cePat2+PJ3l/PV26dNFZmFfvRNldu3ZNT0//5ZdfQkJCVq5c2bSToZub244dO5reSIGBgWKxeMmSJdHR0SNHjtTOTnHTn6OjY8vs9oXhVuKuXbva2trifCwnJyczMzM6Orq5UaDQPvafdFYvFov1ww8//PDDD6YOs1ne3t4XL140dRRvytXVNSYmJiYmxtSBvKKNG9HGjaYO4n8yeC4XJSWZOog3QKMhX1+0fTvavv1fWwSVSFz3hskY+vf6vEYmYyRJkiTZXO3f8KtNP9eYp5V0Op1ON1Or/6tliSRJPAMHQkij0Zibs2QyiUwmDQoKzM8vsrU1tqlBew7A5tjY2NvY2Dc2ygWCqry8LH//9vgAzcx0o3o/zMwIBoOJl2t7DYavEe6yKBTWajSaV10sgc22KCt7zuN5UFVzpVKBE2mBoLKhQaazhDRuy7KwYGtvV6lUfH6Zvb2jhQU7Kytr9erVBEHs2rWrQ4cOWVlPcBkmk8lmsysrK+vq6nA1V61W45acgwcP+vr6du/eXfuDFIpGBoOhPbyNRqP5+/uXlj4vLMzz82un0WioRwN62zDVanVmZkZ6+sOUlEcrV64cOHCgubm5dtWZyWSOHDkyNDR0y5YteKGq5cuXR0VF6d1VYmLizz//bG5u3tjYWFxczOVy+/Tp07Rxo6yszPAJr6qq+vvvv6urdZf1e/DgAZPJvHDhAoPBwCukZWZmHjt2bMWKFREREa83MhwP01CpVP369cN7EAgEGzdu7N27N7V2GUmSiYmJv/zyC4/H27t3b7t27Wg0WlRUlKur6/fff79mzRonJ6cJEyYMGzaMy+VSYTx+/DguLm7evHm4GYS6FhEREXrnVzRc0dQZMEaSZNN/0ul0fMM099Sg6Xz3FHyMLBbLw8ODyWQmJiYihPCqYjpX+cKFCxs2bIiOjv7iiy90HhPjlCk/P7+0tBTfwIWFhXjK7kOHDrVt25bqvKpQKP7666+9e/cOHTp00qRJbm5uOs+P6HR67969Dx48uGHDhq1bt+7cuXP58uV9+vR51YublZWFUyM8M6f2mTE3N29uQD5un9HZaPy0nPX19XiVPO1zu3Xr1oaGhuXLlw8dOvSVpsTLz8/fsGFDVFTU3Llzzc3Njx07xufzg4KChELh9evXEUKBgYFvcVoEvf1LjUGS5MOHD69fv67zVSMSiQoKCtzc3Pbs2SMWixUKxYULFxQKRUZGxtdff/3aLQ0NDQ3Xrl3z9vY2Zs7G1pePAQCAyZmZmWnP/6az/q+BV3UmjZPJJE373alUKr2TmFVXVxjIBAy/qtMaZvxgKhsbW+2ZFXDMVCOGTCaRSOrbtPE1N7fIyMjWea9Go8GtPXp/ia2sOGJxvc5GgaCSy3VGCNXXi2g0Gh5DZW7OcnPzpNFQXZ0QJzNsNkcu/69eJcZ3tTIclWFWVtbaq2b9+yRItTsxGrj6hq8RQsjW1qGk5BmdTufxXmFpMoIgunfv4uHh3dAgp46xqorv5uaJEKqtrSbJ/5rLobFR7uDQ7FTsjY2Np06d/vvvvydPnjx8+HCdyi6e3Xv//v0jR46kNnbt2tnd3W3ixIlN+6TgJrgmkyWimpqqsrKy5cu/e/bsGUKIw+HY2HCoLqkKRWNVVYWrq2dhYeGePXu4XLvw8G4TJ04TCoVXrlz5/fffcScoLy8vqtbo7u6+adOmPXv2HD58+NSpU71799Z7ovr16xcUFLRs2bLc3Fwmk/nll1/qbaB46e3k5OT00UcfSaVSS0tL7ecpOlOQz507l3qC3tDQcOvWLWo2Mtzc9NL+imfPnt25c2dmZiZBEHPnzp04caJCodi1a9fQoUMHDBjAYrEkEsmNGzfOnj3bpUuXbdu2ubm5UTc2jUYLDQ09fvz4pUuX9u/fv2PHjl27dk2aNGnSpEk2NjYCgWDfvn1jx46lujs2NjYKhcJx48bpHUvm5+e3a9eugICA5ho6tKeqX7p0qfZL1D/FYrFKpUpPT3/69GnT9ihkcL57giDwbBYrVqzAc1rgZQy045FIJLt3787MzNy+fXv37t2bPuoaOnRoUVHRhQsXtJ/sM5nMHj16fPrpp7gnIZ6TZufOnW5ubn/99ZeNjY1MJjty5Mjx48ep1h7qxnN0dFy3bt3GjRsvXryYnJz8SiPc8EcHBweXlZUdOnQIL1g8YsQIYwYf4vYZnY1GTsupra6u7sqVK3///TeDwfjss88GDBjwSlNkazSatLS0LVu2zJo1a8iQIfiET5gwITs7e9OmTVlZWQih6OhovatNoP9uotA7C6Je2pnkKyEIomvXrvj06vSwo25R3Ea9nBorjpBIJIqPj6cevuB7z3B/RYTQkSNH8NoDHA4HL+D2kthe75AAAOB/GYvFlstL8ZIsIlGtznAgA6/K5TKxuJ7DsUb/moC+ysvrvzoyWVlZZmamWViw27btoL1dpVIpFAqdRZmMfBUh1NAgbWyU40iUSoVYLPL1NWr2FxcXj8LCPDs7B9zYQpKkSFRLrfzLZlsxmay8vGyNRv3xx9F1dfWVleWOjjz8q1xeXoIndtc7QonL5dXUVFFDhjQaDZ9fSk3vQafTKypKraysqcqlWq3mcP5VUXB0dM7NzZDLZSwWGyEkEFSSpLJppV8vw1EZZm/vKBBUCoUCKs6qqgpra1tjrv5LrxFCyMqKo9EgklTqXdELIaTRqJp2NO3evcuzZ0UqlUqhaGxsZGg0GoGgkqri29lxRaJaqrBQKKDRaFwuTyaTNdm5WiQS/fXXX717R0ycOFH7Ob1Go8afSxDEZ5999tlnn2m/sbS0SC6X+/npuaNIUslisWbPnq0zhMnV1YPNtjxy5MiePXtKSko++WQ8k2nG5f4rWZVKxQJB5YsX5XS62YoVK8rKiry8/BgMhoWFxciRI8PDw1euXOni4jJ+/HjtLlUsFuvzzz/38/MLCAjAdWi955DL5X799ddyuTwgIEBnOE1jY6NEIhk3blz//v2bu0Z4YeLBgwfT6fRXWjfWwsIiMjJSLBaz2ezmeupS/RURQgsWLNBb5smTJ2PHjvX3979z505GRoaXl1eXLl0++OCD5prZLSwsRo8ePWDAgMLCQrFY3LdvXxqNplarr169Onjw4OjoaOpC29ra4iYXvTVj7WV2ddDp9L59+44cOZJtxNqSNBqtQ4cOkyZN0smECYIYMWJE9+7dqXyAyWROnDhxxIgR1GgcgiDCwsICAwO3bt0qlUp1HgEUFBT8/fffgwcP/vrrr5s7G/Zlzv3dAAA+qUlEQVT29suXL582bZqBac1LS0vr6+u3bduGIxGLxS4uLtOnT+/evfuGDRsiIyM/+ugj7SNls9nLli376KOPvL29dfodNDY29u3bd9CgQQZ6EdPpdA8Pj/nz55uZmYWEhOBV9QycQBaLNXLkSL23KI1G8/DwMDyfpEgk8vLy6tOnT2pqanx8vLW1tbe396FDh15jcJparb5+/XpmZuauXbvweuLal3jDhg34wU1wcLCRfUCMxGAwxowZM3r0aOOHadFotPbt2+NVAV/1SPF0mvjhC0EQ2mlw0/6KqMnDCGMj1PsDpvcDmmNMYdxvNTU19TVCNDkIHoKH4FuRNwxeLm8oLy8Ri+tcXDzwUKiqqoqKilIrK46bWxvtnmZ8fml9fZ25uTmHY6M90MXAq/X1ooqKFw4OTgpFI649Ozu7ajc9denSxcKCtWfPz2y2lbd3W50dWlvb6UwmYeSrQqEAIZpCIVep1Go1SZIqZ2cXC4t/FdZoNNXVfIQ0NTXVCCEHB0eEaI6OPCoRamyU4/XH8PzvXK4zlWMIhQKZTOrq6qlWq6Kihtva2qxd+z2LxcLT9wkEleXlJW5ubZpb60yhaCwvf6HRqAmCgZDG3t6JaiGRyxuePn3CZJrb2NgxGEy1Ws1gMLVbdRoapOXlL8zMzPBUHzU11Uwm08nJhUajG76CeqPCt829e3dfevVJkqyoKFEqlQTBoNFo9vbcpi2Neq++4WtEwYPlmvZXFIlqZTKJQFCpVqsdHJxYLAuqqW3Hjs00Gq1Pnz7aC1e2aeNLJY21tQKZTEKnm+GGMldXD4JgaP92q9VqgaBSKhXX1QktLTk2NnaOjs44J8Sf++LFc3Nzps7nNheV9p7r60XFxfn+/u2p+42Co1IoFDhmHBUVT1lZsUqlYjLNlUqFo6MLPm+vVDnRzm1e6q1Xe16vMMQMMUPM/5sxQ/sYAAD8B4tlQTX+YE5OLnrnqODx3Hk89+b2Y+BV3B+vOQ0N8g4dQnU2qtWqxkZ5c1V5w68ihHSWnNZBo9HwATo56f8RMjdn4dntm+Lzy/DU6mZmRHV1TXV1DY/nzue/oI7U8MEymeZeXvqHs7NYFp07dzfwXgsLS1/f//Sq0k6JDV9BA1EZc/UJgqAmi29O06v/0mtEaW7qeVtbe1tbe71teocPn0AIzZu3uLnfe3t7rt5lqSl0Ot3JyQUhPfc5/lyECL11FANRYdbWtp06hel9CUelN2Y6nf7SkwwAAP9vvM0GRAAAAIYZ2aeuybuQgdzP8KvvlIWFZX29SHtLQ4PUxuaNZg//f8mE1wgAAEALRzQ3fs74cXWvWhgAAP4HyWRSgaBSLm+oqCh1cnJ5pcVYzMzMDJQ3/Oo75enpU1VVUV5eYmZGdOzYnsEgEEKvsXDW/3vv4RrhH+J399sNhaEwFIbCUPgdFSb09m14d/0yAQDgfxObbanTF+7/ATqdzuP9a0IFPL8iJGOmwuFwWsgADCgMhaEwFIbCr1QY+isCAAAAAAAAgGlAPgYAAAAAAAAApgH5GAAAAAAAAACYBuRjAAAAAAAAAGAakI8BAAAAAAAAgGlAPgYAAAAAAAAApgH5GAAAAAAAAACYBuRjAAAAAAAAAGAakI8BAAAAAAAAgGlAPgYAAAAAAAAApkG8zw/r0qWLqY8Xgm99IHgIHoJvRSB4AAAA4JW8p/ax0NBQUx/p69NoNKYOAYJvfSB4CB6Cb0VadfColf/IAgDA/7j31D62b98+/D/l5eWurq5GvkssFnM4HJMXhpghZogZYoaYIeaWHzMAAIDWiFZfX/8+P681/rRAzBAzxAwxQ8wtE8QMMUPMEDPE3DJBzMYj9H5qC3mICIWhMBSGwlAYCkNhKAyFoTAUhsL/jwvD/IoAAAAAAAAAYBqQjwEAAAAAAACAaUA+BgAAAAAAAACmAfkYAAAAAAAAAJgG5GMAAAAAAAAAYBqQjwEAAAAAAACAaUA+BgAAAAAAAACmAfkYAAAAAAAAAJgG5GMAAAAAAAAAYBqQjwEAAAAAAACAaUA+BgAAAAAAAACmAfkYAAAAAAAAAJgG5GMAAAAAAAAAYBq0+vr69/l5YrGYw+GY+qgh5pYIYoaYIWaIGWJumSBmiBlihpgh5neH0PuprxQNFIbCUBgKQ2EoDIWhMBSGwlAYCkPh1ygM/RUBAAAAAAAAwDQgHwMAAAAAAAAA04B8DAAAAAAAAABMA/IxAAAAAAAAADANyMcAAAAAAAAAwDSI9/Mxs2bNSk1NNfXBviaNRkOj0Uwdxf9i/K03cggegofgW5dWHTxCqEuXLnv37jV1FAAAAF7He2ofa73JGEKoVf9It+r4W2/kEDwED8G3Lq06eNTKf2QBAOB/3HtqH8Na6Q9Gly5dIHgIHoJvLSB4CP5/M3gAAACtFIwfAwAAAAAAAADTgHwMAAAAAAAAAEwD8jEAAAAAAAAAMA3IxwAAAAAAAADANCAfAwAAAAAAAADTIMrLy5tu5XA4erfr9UqFAQAAAPDWlZeXv9Pf7ne0Z4gZYoaYIWaImXB1dW26VSwW692u1ysVBgAAAMBb5+rq+u5+u8vLy9/RniFmiBlihpghZuivCAAAAAAAAACmAfkYAAAAAAAAAJgG5GMAAAAAAAAAYBqQjwEAAAAAAACAaUA+BgAAAAAAAACmQZg6AAAAAAAAAIAejY2NZmZmpo4CvFuQjwEAAADg7VMqlRkZGb6+vjY2NtRGuVy+Y8eOnj17hoeHE0Qrq4TI5fJdu3bZ2dkNGzaMx+PRaLTX249IJNq0aVN4eHjfvn21Tw5C6NSpU87Ozj169GAymSY5xuLi4i1btvTs2bN3796enp7GHGNjY2NCQoKfn5+Pjw+dTte7w3bt2g0fPtzJyen9H5FcLt+5c6eFhUWfPn3at2/PYDBee1fV1dUMBsPW1hb/88mTJ8eOHRszZkxwcLCB3V66dCktLW3s2LF+fn74/Jw+fZpOp/ft29eYD71z5866deuCgoKCgoIMl1SpVE+ePOFwODNmzGjXrt17P9Pg9UF/RQAAAAC8Mo1Gk5iY+P3339fW1uotoFKp/v7778jIyM2bNzc2NuKNKSkpZ86cWbly5cWLF9Vq9VuMp6GhYf/+/adOnSJJUnvjnj179u/fn5qaKpPJXrqT6urq77//vqCgoLkCtbW1u3btOnbsGHVEr6Gmpubx48dbtmy5d++eRqOhtstkssTExK+++uqLL75o7qy+kpKSkuXLlxcWFhr/Fo1GU1RU9OeffyoUCu1krKamJjk5Wfvcart///64ceNWrlwpFot1XpLL5bm5uQ8fPnRwcMD7z8vLKykpaS4AgUCwcOHCxYsXP3r0qLmPe1V1dXUHDx58/PixMQ1NDQ0NV69e3bt37+7du3fv3v3HH3/g/9myZcsnn3wyduzY27dv45IcDicjI2PRokU611Hn8O/du3f27Nk//vhDKBTijcHBwXv27Nm6datIJHppPHZ2dmKxmMlkTp06dfbs2QqFYt++fQqFYvbs2VOnTn3x4sW+ffvCwsJmz549fPjw0tLSBw8elJWVvZXzBt6bVvZoCgAAAADvSE5OTmJiokKh0NkuFos5HI7OxufPn9+4cYMkyefPn69du9bNzU3vPkmS7Nevn7m5OUKorq7u+PHjCKGvv/56xIgRVHVfqVSqVCoWi0W9q6Gh4datW8XFxdq7UigUzbUaqVSq5OTkzMxMgiAaGhomTpyIt1tYWEyaNGnXrl2zZs0KDw/fuHGjRCKJj4/XSRvwnhUKRXx8fGlpaWlp6YYNG7hcbnMnys/PTzvaV1VeXl5ZWTlt2rTIyEjtnKeiouLJkycEQYwbN87e3t7AHpRK5Y0bNyoqKgyUEYvF165dq6mpyc7OXrp0affu3XXOWGZmZnJyskql0t4uEonwyfn777+phiBqV5MnT/788891jt3c3Byfq27durHZ7IyMjJSUFOou4vP5QqHQzs7u6NGjarW6oqLixo0bXC53zZo1oaGhTdvfuFzusmXLLl68uGbNGnt7+2+++SYkJOS1myK12djYaDfflZaWXr9+fezYsWw2W7uYhYXF4MGDJRIJi8ViMBjUzZ+amnr8+PHAwECddqo2bdp07ty5uQgFAkF2djabzR4/fjzOSBFC3t7eAwcOPHHihLm5+dKlS9/kXmrK2tra2dn5Le4QvAetOx/TaDQHDhz49ddfEUKenp4///yzu7u7qYN6iaKiopiYGD6fr7Odw+EEBQVNnjw5LCzsrXzvvFPV1dWxsbHXr1/Pz88nCCIwMHD48OEjRoywsLAwdWjNy8lBw4ah58//ayOLhcLC0Jw5aNQoZG5u6hAN2blz56FDh5p7dejQoStXrny73+lvkUgkmj9/fmZmZmsMHiGkVqtzcnJOnz597969mpoahJCXl1fPnj0//vhjDw+Plv8HC4CRAgMD/fz8FAqFpaWl9vYrV658++23r/2nihslNBpNQkJCUlKSp6fn8+fP9+zZgxBSKBRKpTI+Pt7S0nL9+vX+/v74LRYWFkOGDJFKpSwWi+rWuHXr1kOHDq1atSo6Ohp/qwgEgl9++cXb2xshNHfuXL2fzmazP/vss/r6+oiICEtLSysrq3HjxsnlchaLtX379hMnTkybNm3q1KnW1tYIoXnz5r3GeSNJks/n83g87R6YGo2mvr5euw1QLpdrNBoWi/X48eOAgIAxY8bg7FEqleJ85unTp0KhsF+/fuHh4YY/kcFg9OvXj06nW1hYGOj2uXjxYvw/TZutzMzMgoODAwICEELa17SoqOj27ds0Gm3cuHH4xKrV6sLCwunTp1PphOFr3bFjR3wd8W6vX79+/vx53IDT0NDQNLFvisvlTpkypUePHps2bfr666+3bdvWpUsXYy4En8+/efOmTqMTSZJ5eXkIoYSEBJzBisVihUJx4cIFhUJRUFDwzTffWFlZab+FRqM1F6eZmVnTPpkGpKamlpSUDB06FJ9qjCCI0NDQEydOZGRk1NTUNPcsA/zvaN35WH19fUpKCv7/kpKSrKyslp+PNUcsFicmJqakpCxfvlz7qWFLo9Forl69umHDBurLnSTJjIyMjIyMU6dObdq0ycfHx9Qxvgq5HN25g+7cQZMno1270H9/IwOAEJLJZLt27cIP9SnFxcXFxcWnT59etGhRdHR0qxsGA0BzGAwGjUYjSfKld7VAILC0tNR5DFddXX316tWhQ4c2rbs/f/780KFDoaGh2k1PNTU1u3fvrqysjIyM1GkRotFoLBZLpVIZ8/elUCjy8/P9/f31NqDZ29uvXbtWo9FIJBIGg8FisaysrIRCYXZ2NkEQ4eHh2r+5CoUiMTGxbdu2Li4uL/1cnE3Z2toeO3bs5s2bAwcOpFLZnJychw8fjh8/fs6cOfgQKioqFixY4OTkVF5e7uDgcPbsWYlEcu3aNQaDsW7duoCAgMePHyOEIiMjqfRAoVAUFhZ6eXk1TYPpdLoxuY1hcrn81q1b2u1sVPvYiRMncPtYRkZGUlJScHCwgVZQHSwWiyRJjUZDo9GkUineQhCERqMRCoU67VTNcXV1nTZt2oIFCy5cuNCxY0djBtTxeLwxY8bI5XJLS0vqmsrl8oqKisLCwv79+0dHRyOEysvLXV1dly9f/oZn76VkMtmdO3cIgoiKitK5gv7+/h999NHo0aNdXV3xltLS0rt3744cOVKnvQ73ciwqKtq/fz9BEOnp6Qih9PT03bt3U6nm+fPnU1JSRCJRfX29TCajOkaC1qJ11yGKi4uzsrKof167di0iIkLnPm5dSJI8efJkeHi4o6OjqWPRLyUlRTsZ01ZYWLh58+b169cb7mXRQh0+jHx90bffIqhYAy0KheLHH388c+ZMc6/+9NNPHh4e3bp1M3WkALw1jx8/XrhwYUREBFX5xgOQ8vLycI0QIVRTU3PhwgUnJ6f169d36NCBeq+dnd3z588nTJiwYsWKsLAwartMJjtw4ICbm1t1dXV+fr6DgwONRtNoNPHx8efOnfP09JwxY0bTFK62tnbBggUcDqdTp05mZmZPnjxB/27lkMvlfD5fJpPhtAHnDBEREatXr6Z62emorq6eP39+QEAAj8dDCFVVVeXk5HA4nJs3b967d4+q7uNd+fj4rF69ukOHDkqlMikpKScnR61W67S04P6NDQ0Ny5YtY7FYlZWVfn5+uMYvl8vXrl0rl8v9/Py080mSJBUKxZ9//omDxF3ggoKCHB0d8/PzHz16ZGdnl5mZWVRUhLQ6YUZHRy9atOhdVG9sbW1Hjhyp3Q7ZtH3sldTU1IjF4jZt2uzevfvRo0chISH5+fno3/lDQUHB7du3BwwYsHTpUp2JTPTCg/Tu37///Plzqu3UgNTU1LKysmHDhhn/ULu+vp7FYjVN9kpLS7lc7ht23MjPz3/w4EFISIibm1tsbKxO/1Jra+tbt27dunUL/fsPSqFQJCcnL1u2TLsSqNFo+vfvHxoaOnbsWIIgZs+ejRB69uwZi8Xi8XgxMTFUyYqKCmdnZx8fH19f3zcJG7x/rbjqqdFo7ty5I5PJ2rZtGxAQcP78+YyMjLKyMmP+YluCKVOmaPeLqK6u3rRpU0JCQk5OTklJScvMx+rq6g4cOCAWiwmCGD9+/KRJk7hcrlKpTExM3LRpE5/PT0lJSUlJGTJkiKkjNeibb9DGjf/6f5EI/f03WrwYCYVozx704YeoUydTx2cIj8ejOue0Ri2/a6KOBw8enDt3DiHk4OAwc+bMyMhIGxsbkiSzs7N37tyZnp4uk8kuX77cuXNnU02GBsC7IBaLS0pKFi5ciNOGK1euxMfHt23bdsaMGfjvNzY29syZM+3bt9fpE0EQxPDhw2/durV48WKq/UGlUh0+fLimpmbx4sU7d+5csGDBunXrBg0alJSU9Ouvv7q6um7dulVvDZLJZDIYjNLS0qVLl3p7e0skkqysLNzKIRKJ0tPTBQIBTht27tyZlJTUp08f7WRMIpGoVCpra2tcO3/27BlJktOmTXNwcGCxWDt37iRJcsKECePHj1++fLm7u/uCBQuatsUxGIyIiIhu3boxmczGxkbtlpaioqIrV644OTl17NgxIyND75m0MqLbhbu7u52d3cmTJxsaGnCTOw5YJBIlJycjhCIiIt5kOEBBQcHJkydnzJiht2pBo9GMCRIhpNFoCgoKVCoV7nqHx/hlZGRwOBzcaHP27Nldu3YpFIr58+eXlZWlp6fPmTNHux/piRMnbty44ezsjHuHvvTjcC93gUCQkpLy0tqdUqm8fPny48ePS0pKdHLgpv0VcdMizoIGDx789ddfa985crn8t99+S09PHzhwIIPBwF/vTUeaGEaSZHx8vEwmo9PpZmZmI0aMkEqllpaWVNsgFUZ6erqHh0dz7XWDBw8ePHhweXm59kFdunTp0KFDgwcPXrFiBXX5eDzewIEDa2trjbygoOUg9DZ0IH1djQ14pcJvi0gkevjwIUIoJCQkKirq7t27AoHgzp07rSUf0+Ho6BgREZGQkEAQxCt1TX6fsrKy8HfupEmTZs+ejb8aGAxGnz59aDRabGzsmDFjOnfubOowX4WtLZo+HSGEZsxA5eUoIaGF52PgfZLL5XFxcSRJcjicdevWUY1gBEF06tRp3bp1Gzdu7Nu3b0REBCRjwOTwD/Fb+e3+v/buPKyJq+0f+AkGjIGAKFhkE7GIUZEtLC4IiKKCgIqtWy+uWi1dsItQH0WtAtYK7ku1LrUvVquiLRXQChaLQlEeFSiKgkVcMGyySlhCGJLfH+dtfnnDYtRqoH4/f3jh5DC5ZxKdueeccx9ah7C9vb2xsVGxHh3DMCKRqK2tjRAiFosJIVKptLGxUakInpmZmZOT07lz586fP0+Lzv3www+6urrh4eF6enrm5uZ0gFxycnJMTIyent7KlSsHDRrUaTA0oZLJZE1NTfIGYrFYJBIpvUSrR7S1tSnup7q6Ojo6ury83M/Pz8fHJysry8LCol+/fjKZrLCwMDU11dTUdPz48VKpdMaMGRs3bhQIBN3MU5JIJGKxmB4sPRVNTU30AMViMQ2AxkZ/kJ8WeUi0veKJpaeaYZg///wzOTnZ09Nz7NixjY2NiodPCGGz2fKNlZWV6enp8r8+VW1tbUpKikQiyc/PX7FixdChQ9vb2+/cuZOTk0M/SiVPnjyhAR89elSpC4uWSezXr9+KFSvGjx/PYrHGjRs3bNgwAwODxsbGGzduTJ8+3cfHhx5+VlYWISQ+Pj4zM1O+B5oXDRo0SJX4Gxoabt26ZW5urqmpeenSJQ8Pj+7HZxYXF1+7do3H482cOVMeuVgsjo2NFQqFS5YsCQwMpGktTYQkEsnu3bulUqmBgUF9fb3iV72qquru3buEkKlTpw4ZMoRuvH379uPHj11cXORfs44fqOLH/fDhw9TUVHre7t27R0MSiUQsFkvefUf/QZ0+fTo5OXns2LEhISG081ZOKBReunRJIpG0trb2VZjlTm+A6VNy+cZHjx7R2o8hISF+fn6qD6R/eff8aKxiY3anX+5OKyl1s/cXH8H8HAoKCgoKCgghDg4OQ4cOtbOzS0tLu3r1amBgoCqd4D2KTCYrLy+/cOECIcTKyqrHzoIrLCxkGIbL5bq7uyv9O3dzc3Nzc1N3gM+FxSKTJhE+nxQUkOJiwjAYsghUTU1NYWEhIcTT07PjgwYjI6MdO3aoO0aA/8Xj8f6pazcdF9enTx8dHR3FNmw2m8fj0f4x+qfiFsU9u7m5XbhwwdnZmV6mFy5c6OLiQh81BgUFzZkz5/Lly1FRUXw+f/HixU5OTl09hWxvb+/Tpw+LxdLW1pZHwuFweDye0kv0mQh9SR6GhYVFREREaGjowYMHhw0b9tdffzk7Ow8aNEgikSQkJFRWVi5fvtza2prFYtna2rq5ue3cubOrnjpKU1OTXvssLCx4PF5bW1tNTc2IESP09fWVApC3pB8N/YFOalI8sfRUt7a2njlzZsiQIe+++65iZTx6jLSZfCc8Hs/CwkIsFkulUtrLROuENTQ07N2718bGJiEhISoqSnEwQkREhNLH7eLi4uDgoFi4RT45vL29/fPPPw8MDCSE0JSy+9v6xsbGbg5/9uzZiiluXFzclStXFD/NbuTn5xcWFs6YMaNPnz4JCQk1NTXyqVYd1dXVpaamCoVCFxcXPT09uv/Gxsbvv//+9OnTixYtmj17Ns27jh8/LhAInJycrl69mp2dvXPnThcXF6XxjXfv3n3w4IGjoyNNxujeXFxclGpUdvxA5eeZYZj09HS63hqLxTIzM+PxePfv31+/fv3q1avpd4w2FolEVVVVDMOYmpoOHTpU6WzTEjtisfjx48eWlpY0TpFIVFhYaGBgEBoaSjsh6CMGTU3NTZs2sVisl3cbj8YvqXFvve9kGCYrK4thGAsLCz6fz+VynZ2d09LScnNz7969q2IdHvU6fPhwx3J5PB7v008/7ZmDFRmGqa6uJoSYmpr+20qp8niEjp2oqSESSU/OxyoqKubMmdNx+4EDB3rF1z45OTk5OVlxS08ewSgSiZ48eUII6apIAMC/WEVFRWxsLP232XH+GH1U0RUvLy8vLy+GYdavX08I0dLSkmdczc3N27dvv3z5cmho6NSpUzds2LBly5a33npr1qxZXQ3Ja2hooJPEupk/RsduKJVuJ4QYGRmtWrWqubmZw+HcunVr4cKFhJBLly4lJib6+vpOnDixurqaThNasmTJsmXLIiMjo6KiLCwsOo1EJpMp1kukM8r69eunyqpW3cjIyLC0tPz444/Ly8tHjhz51DEybDZbR0dH/qy9tbW1tbVVV1f3mUapaWpqypcwbmlpOXr0aGxs7JQpU5YsWUIfahcXF2/cuJHNZq9atcrc3PxFDvA50NXtmpubHR0dW1tbjx8/fvXq1dGjR3c1MaypqUlXVzckJIR2o0ml0lu3bm3evNnQ0PDUqVP0MfetW7ciIiJKSkqKioqGDh2qra29c+fOjkXIZDJZTk4OwzAjR47U0dFR7MpjGKa8vNzExOSpn9GjR48uXLgwb9682NhY+UYTE5MhQ4bs3bs3MjJS/mHV1taWlpZyudwpU6Z0mvrS5Hbnzp3p6emenp76+voNDQ23b9/W19dPTk6mj/LpwEupVBoSEkK/5NC79Nz7zu7V1tbSyor29vb08YOTk5ORkVFFRcWlS5dsbW17abmzKVOmyHvGexqGYei9qZaWFu5N4XXQ1NREq1Qp1v7uuGRFb5/UB9ApIyOjd999t5v5YxkZGV39Lr0E09qD8o1VVVVxcXGJiYkBAQErV640NDSkgx5LSko4HE6nyZhEIpFIJFZWVgsXLjQzM7O3t1+xYkVjY+PYsWNtbW0///xzeUsNDQ0+n9/phAW6WtSxY8cGDBhgbm5eXFy8d+/e8ePHf/755/fv3w8ODubz+R999NH48eOjo6O/+OKL4ODgpUuXTps2reOVrrW1taysrH///krrAbwggUCwbt06LS2tsLCwvLy8Dz/88Jkyq4aGhrq6Oj6f/xyDg9ra2uLj4w8fPszn8w8cOKCnp1daWlpUVFReXn7gwAEtLa33339f9RpdHStS0rp/8r/S+WCq7LCysvLq1avm5uYjRoxoa2szMjJKS0vz9/fv6oG1np5eUFAQ/bmwsDAqKurOnTvW1taWlpZnzpwhf2cspqam33333YABAwwMDLpaX66oqCguLo4Qcvfu3f379yuuenfz5s3r168HBgZ++OGH3UyBYxjm559/dnBwsLGxUdyupaVlZ2cXFRV15syZuXPn0o21tbUVFRWOjo7dlKdmsVgaGho1NTXa2tq0nsd//vMfxQb379+/fPkyIcTNze0Fnw6AWvTKpIUQcufOHToK2dXVlT7gGTx4sJ2dXXJyck5OTl1dXc/sYnqq+Pj469evdz9eQl369OlDr5f0AqnucABeOm1tbX19/bq6OrrmGACojvaD0ZwtLy/vxo0bmpqa7u7uH3zwgbxbRq5Pnz41NTXFxcUODg6Kj1MHDBgQGxtLp83Q6ggikWjEiBGKFR2p4OBgmUx2+/btrVu3Llq0SOmOv6mp6fr16yYmJrW1tVFRUXZ2dmFhYTo6OrSMoZmZGU3khg0btnfv3ujo6MjIyH379r311lszZ87U19eX74de/jpW+X8mih2P9MmOgYHBgAEDOBzO9OnTN2/e/ODBA7oUsoo7FAqF9CieIypNTU2BQHD27Nl79+79/vvvAoGAy+X+8ssvGRkZ/v7+NP9RPTnsmAn4+fl1HK+oSqHI9PT0oqKi2bNnDxo0SCqV0hu8CxcuzJ0796m1E62trd95551r1655eHhYW1s3NTWdOnUqOTn5/fffd3Fxyc3NtbS0HDx4cFd9XMOHD//xxx/PnTvn4+NjYGAgH2bW1NT05ZdfMgwzZsyY7kep5eXlZWdnf/XVVx3fwtraWl9f/+eff54wYQLNn+/fv88wjEAgUMvcH+ghemU+1tbWRsuDEkJWrFih9GpBQUFeXt7kyZPVHeZTKNVXbG5uPn/+/I4dO0pKShISEj799NOe1sWnqalJLw9CobCyspJ2S/5LiESkoYEQQrS1e/JgRdL7u2J68ujEjgYMGGBoaEgXKWpubu7Va2kAvEqNjY0xMTEPHz50cHDIyclpbGzkcDitra2ZmZmK1R0YhqFVE2hdvidPnixevPjdd99tb2/PyMh48OCB4uDAhoaG8+fP0/189913Hd/04cOHv//+O8MweXl5UVFRir1bjx49unHjhomJyY4dOxYtWuTj46N4hdXQ0JDf4g8ePHjz5s2ZmZnJyclTpkxRKp1fW1tbVVVlYmJCt9PhkYaGhoqFFp5KseMxOzs7KSlJ/tLw4cMtLCyuXLmSk5MzefLkurq66upqLpfbzZiUtra227dvE0JMTEye77/WYcOGHTx4UFNTs6Gh4eTJk0eOHJk4cWJcXJypqWlFRUVERETfvn3fe+89Pp//HMXGOu0fe6qKiorTp0/zeDx/f3967NOmTUtNTY2Li3N1de1qNKkci8Xy8fHx8fFpaWk5fvz4//zP/3h5eR0/fpyOWpRKpatWreJyuYsWLZo0aVKn59bQ0FDe2ybX1NRUXl6ur69vYWHRfU44aNCgTZs2mZmZ0YRf0eDBg83NzfPy8tLT0/38/Og/AS6Xq+KMA7psQMftdOUxVapWQs/Uo289u/L48WM6UrwrmZmZEydO7F1j6rhcroeHxy+//JKfn19TU6PKWpyvHu15b25uvnTpEp/PV4zw5s2bBw8e9Pf3d3V17X2FVv/7X1JQQAgho0aRXvW1gZdKX19/1KhRf/31V0ZGxtWrV93d3Vks1tChQ8+ePUsb7Nq1q+MsUIDXSlVV1cmTJwMDA+V3ydXV1bt3787JyYmIiPjtt98IIePHjx8xYoSGhgbtXJJfO8Ri8aNHjx48eDBr1iy6bJect7d3c3OzlpYWbUyX8xKJRMuXL5f3kEgkks2bN8fHx8+ePXv58uVKF/2ysjL6g0wmy8zMrKurmzFjxpIlS3R0dFJTU7dv3/7NN9/QBg8fPvzss8/eeeedcePGRURE6Ovrh4WFeXp6djxYoVBYV1fn4eFBxyvS4umK6dwL6t+///Dhw4VCoWJHU/cTw+rq6uhCrLa2tt2EQWcccLncjp2TUqn04cOHJ06c+O2337y8vOjaaLq6um1tbRwO57PPPouMjAwKClJxDTS6ILh8qGrH/rHCwsLuR3syDBMfH3/nzp3AwEA+n0832tvbT5gw4eLFi7GxsStXrnxq5tnS0vLrr78eOnTI2Nh43759I0eOZLFYUqlUJBKZmZnNnTv322+/Xb16ta+v78qVK1V81lZZWSkUCk1NTZ/adWlmZtbVSxwOx9TUNC8vr7Cw0NvbWyqVFhYWDhs2TMUZevb29nS8opL79+93M34Yer4ed8evivz8/AcPHnTT4OrVq6Wlpb2rD4FhmOzs7IcPHxJCaM0odUfUCT6fb29vn5ube+TIkba2Nvn6Y9evX9+2bdu9e/cyMzM/++yzjk+Vei6JhKSkkJUrCSHE2Jh0dgGG15ampuakSZOSkpIYhgkPD3///fdp+VapVFpVVXX58mU6kRrgX0Bx1WM6iE6Veh7p6enp6enNzc2///77V199ZWdnl5+fHxERIRQKV69e7eLiQvMxQoi2tnZzc3N0dHRVVVVYWJj8PrsbinfJGRkZqampkyZN8vf3l18faY14IyOjuXPndvoEVigU0rLA8fHxXC7Xy8tLR0dHIpFkZmbq6upqa2vX1tYSQszMzAYMGBAZGbl69eoFCxaEhYU9efJkzZo1SrfdDMPk5OQQQpydnRUfR/6DD085HE5AQMDbb79ta2ur4q/cvXv33r17dCHWbpqVlpauWLEiKipKqR8mKSlp9+7ddEi2paVlSUnJ1q1b6WH6+/sLBAJzc/Pw8PA1a9YkJCQ4Ojr6+voq7VkqlVZWVj5+/JgQsnnzZj8/v4CAADabTUu5dNS3b9+2trbz589PmDCh00QoJyfn5MmTlpaWs2fPlp9bHR2dBQsWZGdnnzt3zsHBwc/Pr6vbpMbGxqNHj544cUIkEllZWWlra8fExDQ1NT148GD48OETJkwwMzMzMzOLjo7+8ssvz549GxAQoGLfVElJSXNzMy2t+dwfcd++fRXnrZWXl5eUlMycObOrRcyVoH/s36r35WMSiYQuatHpwC1a5pUuTNzD87FO6ytSo0ePfqbBD6+MgYFBcHDwf/7zH5FIdPTo0aNHjyo1sLa29vb2VneYTxMTQ2JiOtn+wQdk5Eh1B/cUXdVX7O3jGHssZ2fnRYsWHTx4UCKR7NmzZ8+ePR3b2NnZDRw4UN2RArwQuuqxg4ODlpbWjRs3kpKSFIfVlZWVbdq0SbE9recxceJEpRHIbDZbV1eXjglUWpeMy+XOmzdv6dKlH3300e7du5VKHXRDKBQeOHCAzWYLBAKJRMLhcDQ0NKqrqw8ePNjc3BwWFtbVjGtTU9OBAwfu37+/oqLC1NSU3q3euXMnLS3N0tJSfp3V0NAYN25cSkrKtm3bNm3aNHHixOTkZB0dHaWek9ra2tzcXMWqIaWlpYQQExOTf/CDcHV1Vb2xWCw+e/YswzCTJ0/uftp8U1NTAx2W/3+NHj1aT09vzJgxEyZMcHR0HDx48KNHj0JCQlgs1pw5c+g1RSaTBQUFZWRkjPm/63NWVFQcOnQoLS2trq7O1NR0/fr1Hh4edO3p5uZmOsm/43jF6urqDz/8UCwW+/v701l8ivukHyshZPny5Uon1tbWdt68eQcPHty2bZuRkZF8QUgl2traxsbGLS0tfD5/0qRJbm5uFhYWv/76a1RUFF3gixBSVlZmbGy8ffv2xMREFa+bDMPQfsjnm6enaMiQIfb29vPnz+/bt29xcbFIJBo7dqyKT+HRP/Zv1fvyscePH//555+EEDs7u46VfMaMGUOrLGZlZfn6+v6zFZBejbFjx/bkyW9OTk7h4eEbN27suKqdkZHR8uXLlZYy7DUWLyahoT188hi8emw2OygoqKmp6eTJk0o3l4QQWnxs/vz5L3h5BughXvyiyefzt23bxuPx2Gx2x38y5ubmw4YNu3nzZklJier5mLGx8XfffVdaWkrHYuTl5dG1v+7evevp6Tl58uRu7mX79es3bty4I0eO9O/fX09Pr7q6eteuXSKRyNTUVDGNNDExGTNmzKVLl65fv+7p6ZmcnJyWlvbWW28pBpmbm/vXX38tX76cPn9pa2uj3Wvdj15raWl56gEKhUKxWNxxDF59fX11dbWlpWWnnwtdMSw1NdXa2trX17f7G/qWlpbm5mZaMFbR0KFDT506VVVVtWXLltu3b3/88cfyl8Ri8bFjxwgh7u7uAQEBs2bNUvrdN954w8vLKz09PSQkRP7foI2NjZWVVXt7+9KlSxmGyc3NtbGx4XA45eXlRUVFM2bM6GaF1ebm5l27dhUVFUVERDg5OSmtGc1ms+fMmZOdnZ2Tk7NmzZqoqKiO64YRQlgs1owZM7y8vNhsdkpKCsMwikM0c3Nzacm3wYMH29vb29vbP/XToUQiEZ2nN3z4cBV/pSsBAQF0dC4da8rn87uprKgE/WP/Vr3v7jM7O7ukpIQQYmtr2/E/L3mVxWvXrt29e1f1Hv+ewMrKys/Pb/bs2T353o7FYk2dOtXGxiY+Pj4lJaWsrIzNZltZWXl7e/v7+6vY4d6D6OsTZ2cSEkK8vUmP7JMEteNyuaGhoQEBAQkJCRcvXlT8ztPqW+oOEKBnYbPZXQ3h69+//+rVq9vb25/pplZDQ0NPT09PT48uqisUCr/++uvs7GwbG5vMzMwZM2YIBAJfX18nJ6dO51kp1pC4cuVKa2urQCCYNWuW4jgUDodjZGTE4/FcXFzeeOMNc3Nze3t7xW636urqU6dOOTg4TJgwgW6pr68vLCzU19dX7Jiia6MRQhiGoR1EHVMg1bW1tTEM09UaMzk5Odu2bTM2No6MjHzqk1A6m46OKlSSm5sbERHx+PHjefPmNTc3K56T+fPn3759Ozw8vLq6eubMmT4+PiYmJvIUiMViubq67tu3T6m+Bb03E4vF+/fv/+GHH2bOnBkaGmpkZFRWVhYcHGxsbDxz5kwvLy+lW53m5uY9e/ZkZWVFR0d3mmgRQgwMDFavXr127dpbt24tW7asq8dhtDT8119/nZub6+LiEhoaKn/J3t5eKBRu3LixqKho6tSpfn5+b775Zld1SlpbW+W5XH5+fkFBAa2//9wfqJLGxsbbt28LBAL5vVNBQUF+fn5AQEBXFRDQP/Zv1fvyMflzhU5xOJwNGzZs2LBB3WF2SbEYQO9lbGy8dOnSpUuXqjuQZ8Hnk26nHfZwn376qWJBzt6lf//+vbruBYvFevPNN8PCwsLCwtQdC0AvxmKxrKysmpqaWlpatLW1lZZX7p5MJistLU1ISDh9+rS5ufmOHTtcXV2bmppSUlLoqDktLa3AwMAlS5YoPhlsampSzMf8/Pz8/PzEf5Nv79Onz3vvvRcUFGRkZCSTyY4ePdqvXz/5bbpMJktNTa2pqdm8eXNZWVlkZGS/fv0qKyvv3r3r6uqqOFTH09OT3qKIxeLy8nI6705Jx3r3cgzDZGRkcDgcMzMzLS2tK1euEEKGDBmilHLIZLL//ve/GzZssLW1XblypdJYIdpfd/v27fv379OXqqurU1JSCCGnTp0SCATyZFgqlSYnJ2/atMnR0TEmJsbCwoLD4SiWBGSxWKNGjdq7d++ePXv2799/6NChxYsXv/fee4r5dt++fTvmTuXl5dHR0QUFBWvXrp06dSo9WEdHx+3bt8fExKxbt+7w4cMxMTHyfiGajN25c+fbb7/tfr0fCwuLrVu3btmyJTU1dc+ePT/99NM777yjOIy/sbHx5MmThw8f9vX1XbNmDe2Oy8vLkzcwNTVdvnx5Xl7e9u3bjx075urqGhkZ2emTtfr6+kOHDmVlZenq6gqFQoZh3NzcOqa+9fX1T5486eZ5NMMw169fT01NVVqvvKqqqri42MTEZP/+/eTvFdIkEsnNmzdDQ0Of+wF3S0vLuXPn+Hy+6l3QoHa9Lx8DAACAV08ikaSmpiYmJj558oT2Ag0cOPA5qlm0tLRkZGScOHGCFrvn8XjdjNdiGKakpOTKlSuJiYmVlZWenp7ffPONra0tfV8dHZ3AwEBfX9+UlJQ9e/YcP36cy+UqDrrr06dPx0FcUqk0Nzd3x44ddOUuehTydcZYLJbS+MCcnJxTp06tXbv2zTffJIQMGTJkz549mZmZY8eODQ8P19PTe6bEspt692w2e+zYsbm5uWvWrKF1pNlstpubm2JXnkQiiYuLO3369Mcff+zr69uxI8XR0fGDDz44duzYO++8o7hnGxubefPmyctgCoXCHTt2yGSyPXv28Pn82trac+fOxcbG0nPC5/PlnY06OjphYWF6enoHDx7MysqaO3duNwtPS6XSlJSUffv2eXt7r127VmlurbGx8aZNm8LDw3Nycs6cOUMfMjY2Nm7fvt3ExGT37t2qjA8yNDRcv379+PHjjx07tnTp0nHjxmloaLS2tra0tJw5cyYpKWny5Mk///zzwIEDi4uLIyIizp07R4fOyo9IS0srICDA0tJy7dq1WVlZmZmZnT7of+ONN8LDw0+dOrV161aGYVxdXYOCgjp+4RmG6f7Tp1MfaW6sOLBLJBJ9+eWXii1Xr14t/7m+vv7ChQtVVVX0r3T2WvfjFQkhR44cyc7OFgqFPB4vPDzc29u7Z9aHAyXIxwAAAOD/09DQcHV19fLyUip/p6Wl5ePjM3369MuXLx86dGjmzJne3t7d52MmJibr1q1T6vEwMDCYNWuWr69vbGxsQUFBcHCw0hgwhmH+/PPPwsLCoqIiPT09U1PTESNGTJs2jc1md5oJ0LKEtra2P/74o1KfAIfDWbNmzdy5c+n8MbqRy+V6enoaGRlt3bqVLlTV1tbW1SE8efLk7NmzUVFR8kWouVzu0qVLly1b1r9/f3nlfV1d3ZiYGIFAQNuw2ewlS5aspMV7/8Zms/38/FxcXBQTgwULFvj5+cmTRjab7eTkxOfzt2zZ0tTUtGDBAsWZF9XV1YcPH3Zycjp+/Hhra2uno9q4XG5wcHBwcLDiRvmixlRNTc39+/dXrlwp7xeiHwrNMG1sbBYuXKg4DpPNZr/33nvjx483NDTsJhmjtb74fH5cXFxXJekNDAw+/fTTNWvWjB8/nvzdBzV79mxakp6oRktLy9/fX3Edufr6+hs3bowbNy4wMFDesfnmm2+uW7fOzs7up59+CggI8PPzU9yJjY1NdHT0gwcPJk6c2NUbsVgsNzc3Y2PjoUOHdlxC+smTJ2ZmZl5eXl0VU2GxWCNHjnRzczM0NHzW1eH69+8fEBDQ1NREl4jw9/c3Njbupr3il03p44aejyWTyTpufaYPUpXGtJZodna2uo/3eSB4BI/gexEEj+Bf2+D/8Wu3HK1H9zL2jJgRM2JGzIiZ3bFKnvzXVHyDZ20MAAAA/yx6IX551240RmM0RmM0fkmN2Z3mai8v7wQAAIB/HI/H6yEPmNEYjdEYjdH4mRprqLgXAAAAAAAA+GchHwMAAAAAAFAP5GMAAAAAAADqgXwMAAAAAABAPZCPAQAAAAAAqAfyMQAAAAAAAPVAPgYAAAAAAKAeyMcAAAAAAADUA/kYAAAAAACAeiAfAwAAAAAAUA/kYwAAAAAAAOqBfAwAAAAAAEA92K/yzRwdHdV9vAi+90HwCB7B9yIIHgAA4JmwGhoaXsHbfPbZZ3l5eeo+2Ockk8lYLJa6o3gd4++9kSN4BI/ge5deHTwhxNbWdufOnS9v/yKRiMfjqfsoEXNPhJgRM2J+cexO3/WZolGl8ffff09/KCsrMzY2fhkn5eU1RsyIGTEjZsSMmF/nmNEYjdEYjdH45TXG/DEAAAAAAAD1QD4GAAAAAACgHsjHAAAAAAAA1AP5GAAAAAAAgHogHwMAAAAAAFAP5GMAAAAAAADqgXwMAAAAAABAPZCPwb9Hdna2o6Ojo6Pj6tWrxWKxusMBAAAAAHgK5GMAAAAAAADqgXwMAAAAAABAPdjqDgDgH+Po6Jidna3uKAAAAAAAVNWz+sfKysrUHQIAAAAAAMAr0iP6x8rKyi5evJiUlPTXX3+hfwM61dLSEh8ff+7cuaKiIoZhBgwYIBAIgoKCRowYwWKxaJvs7Ozg4GBCyLRp07788ksOh5OQkBAVFdXpDkePHr1z587+/fsTQmQyWWFh4ffff//HH39IJBIrKysfHx9/f3/6KsCLKCsrMzY2VncUAAAA0EOxSktLO27l8XgikUjFXTxTY0X37t27efPmhQsX7t+/L9+YlJT0CsJ47pjVGMbrHHNtbe3mzZvz8/OVtmtpaS1dutTT05P+9ebNm6tWrSKEuLu7f/LJJ3379v3tt9927drV6T6tra3Xrl2rq6vLMExiYuKRI0cYhlFsYG5uvmLFCnNz89fnPCPmlxHzsWPHEhMTXf/WK2JWbxiIGTEjZsSMmBHz6xWzrDMNDQ0ylT1T49LS0sLCwi1btvj6+joosLe3pz+8mjCeNeaeEMbrHHNcXJyDg4Ozs/PZs2fb2tra29vPnz/v7u7u4OCwcOHCx48f02bXr1+n36JVq1a1tLQohSGVShMSEpydnWmbb7/9tq2tTSaTpaen043Lli0rLy+vr6///fff6c5DQ0NFItHrc54R88uIed++ffL/6CZOnLhu3bq0tLQeHrN6w0DMiBkxI2bEjJhfq5hf3XjFO3funDlzJjU19fHjx4rZICGExWLJh5wBdFRRUUF/EIvFMplMQ0NDIBD4+PjExcUVFBTk5eVNnjz5qTvJycnZtm0b7QRzcHCYM2cOm80Wi8XJyckMw+jr6y9evNjIyEgkEnl4eNy7d2/v3r1//PHHjRs3xo0bp+4TAL0e/b+usbExKSmJjgLw+BuPx1N3dAAAAKA2Lz0fo2lYWlpaeXk53ULvS0gXaZijo6O6zwm8XMHBwR988MEz/YqOjg4hhGGYDRs2bN682cHBQSAQLFy48IsvvtDQUKkmTXV19b59+2hPsYGBQWhoqIGBASGkpqamsLCQEGJiYmJiYkIbs1is4cOH03csLCxEPgYvjv5fJ5PJWCwW/fPixYsXL14khHh4eLi6uk6bNg2JGQAAwGvoVfSP0Z44dR8p9GL+/v5XrlzJyckhhEgkkqysrKysrG+++eaNN974+OOPp02bxmZ3901mGCY2Npb+OpvNDgkJGTFiBH1JIpGIxWJCSH5+vpeXV8ffLSsra2tr09TU7D5CPEcAVdCsTJ6SKSZm0dHR6DEDAAB4Db30fMza2tra2vqLL764c+dOUlJSampqVVUVfUmxo0zeXrG+okgkUv2+5OU1fqbyaIj5uRt3w8DAYNeuXfHx8T/99FNJSYl8e2Vl5bp166qqqt59991uhrxeuHDh1KlT9Ofp06d7e3urPj62paWlvb39qfkYwLPq+JQKj64AAABeQ69u/hhNzBYsWCASiZKSktLS0uSTguSzyNR9NqDn6tev38KFCxcsWFBfX5+fn3/p0qX09PSamhpCSEZGxuzZs/X09Dr9xeLiYnntRFtb25CQEA6HI39VQ0OD9q3Jy98/Xw6pyjoNPSTv7Y25eq+Oef/+/QcOHKAbO30I5e7u7urqOn36dHSLAQAAvIbUsP6YvMeMLjuWmJhYVFSk7vMAPVdVVdWyZcsKCgqMjIy++eaboUOHurm52dnZzZ8//5NPPqmsrGxvb++qV6GxsXHv3r1CoZAQwuPxPvzwQ0NDQ8UGhoaGVlZWQqGwtLS0tLSULjgmkUg2btyYmJjIZrO3b9+O+WPw4jo+dXJ3d/fw8PD09KQ1cJGMAQAAvJ5UqoXwkhgbGy9YsODEiRNJSUlhYWFWVlbqPhvQExkYGMyYMYMQUlFRceDAATreVSwWX7t2jfaP2dra0oIfShiGOXr0KC2ZwGazQ0NDnZyclNpwudypU6ey2ey6urrdu3eXlJRIpdJr166lpaURQgQCwahRo9R9AuDfgJYv0tHRmTFjxpYtW7Kzs7dt2+bv7480DAAA4DWnhv6xjmhitmDBgrKyMnXHAj0Oi8Xy9/d/9OjRiRMnzp8/f/78ecVXHRwcgoKCOq3n0djYeOXKFfozwzCRkZGRkZGKDdauXRsQEODp6blo0aKDBw9eu3Zt1qxZ8lfNzc1DQ0O7GgYJoDodHR1aqEO+djkAAAAA1SPyMTnVp4jAa4XL5YaFhbm7u588efL69esikUhLS2vUqFH+/v5Tpkzp16/fi+yczWYHBwe7uLjExcVlZWWJRKKBAwfOmjXr7bffHjhwoLoPHXo9Pz+/Z13gAQAAAF4fPSsfA+iKhoaGs7Ozs7Mz/Wun820cHR0V62pwOJzDhw8TFcowaGho2Nvb29vbq9IY4JngMRMAAAB0Q53zxwAAAAAAAF5nyMcAAAAAAADUA/kYAAAAAACAerAaGhpe5fv1xsk5iBkxI2bEjJh7JsSMmBEzYkbMPRNiVh2703d9pmjQGI3RGI3RGI3RGI3RGI3RGI3R+DkaY7wiAAAAAACAeiAfAwAAAAAAUA/kYwAAAAAAAOqBfAwAAAAAAEA9kI8BAAAAAACoB/IxAAAAAAAA9UA+BgAAAAAAoB7IxwAAAAAAANQD+RgAAAAAAIB6IB8DAAAAAABQD+RjAAAAAAAA6oF8DAAAAAAAQD2QjwEAAAAAAKgHq6Gh4VW+n0gk4vF46j5qxNwTIWbEjJgRM2LumRAzYkbMiBkxvzzsTt/1maJBYzRGYzRGYzRGYzRGYzRGYzRG4+dojPGKAAAAAAAA6oF8DAAAAAAAQD3+H54Ce+7L1KgwAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDIxLTExLTAxVDEwOjQwOjAwKzA4OjAw7zuSpgAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyMS0xMS0wMVQxMDo0MDowMCswODowMJ5mKhoAAAAASUVORK5CYII=)
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
1. 检查索引是否越界，将modCount+1，拿到索引位置index的原元素。
2. 计算需要移动的元素个数。
3. 如果需要移动，将index+1位置及之后的所有元素，向左移动一个位置。
4. 将size-1位置的元素赋值为空（因为上面将元素左移了，所以size-1位置的元素为重复的，将其移除）。

**remove(int index)方法的过程如下图所示**  
<center>

![avatar](data:image/png;base64,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/scff+RwOEql8smTJ1OmTFEoFFu2bCktLaXRaOvWrQsODkYIyeVyqVTa6KZsbW379euXkpISHR3dzDvi2Zmb2siH43K5eFiLrKysJUuWxMXFKZVKDoezfPnyK1eurF271sbGhsPhjBkzZv78+QYGBkqlsra2ttHcg06nDx48GI+kgjONRimVypSUFPUOZmZmZpMnT54+fXr79u2zsrK+/vrrqVOnEgTRvn37qKiogwcPbtmyZcaMGQihI0eObN682crKqnPnzo3WVebm5uIayLy8vN9///2gmoULF44ePXrXrl01NTXaHBk8Ujz+u6qqKjo6uuEwmI0aMmTI9u3b7e3tly9ffvLkSZlM9k5npLKyEiFkY2NjYGDwrmdTLBYfPHhwypQpCKHTp08PGTIkLy/v2bNnBw4c+PbbbxFCQUFB75T7fQjcJ23OnDlz5swZPnw4Qug9hq/s0KHD6NGjydabUqn01q1bBEGYm5t/8803eHyU/v37T5o0CSH0+PFjMtEiDRs2rHv37np6enhOPLwwKCgIj7rp4OBADoRD9u8qKCi4ePEiQsjd3X3hwoXW1tZ6enpeXl7z589nMpkikeivv/7C2WCvXr0cHBwQQs+fP8ezL0il0kePHiGEmExmjx498EOEZ8+e4SqyCRMm4GAcHBwWLlzIZDJ5PN7NmzcJglCpVBUVFTiApg5UVVUVWRf38uXLpKQkjYcOJiYmeBxaLpf7rvkwAAAAAMBHRG2q31dTy9+7sEQiuXnzpqura15enr+/f15e3tdff92/f/++ffsePHiQy+Vu2LChqKioR48eeXl5+/btk8lkDx8+NDExWbNmDb6Tw+mNQqEQi8X6+vp44MerV6+Wl5eTaQ+uqUtMTIyIiMBbKC0tHTVq1IwZM8in5hKJ5OjRo3///beJicmECRO++OKLtzara2oHo6OjlUqlmZlZ27Zt27RpM3/+fH9//379+n333XeGhob79u27deuWnZ0dlUo9evQoQujVq1dZWVmLFi0KDg7GN6D4gT3uuGVgYGBpaZmSkrJ//34yx6iurq6pqZHL5ZGRkQwG49WrVwkJCR07diQPizobG5vRo0cnJyd369bNy8tLIpHgSbQmT57crVu358+fK5VKJyenhgNj4B1s167d77//fu/evUGDBql3MaqtrX316hVBEG5ubiwWSyQSaZyLhkdG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ELK0tNy/f39ycvKmTZua2nJ+fv79+/efPn1qbW3dr18/PT09KysrQ0PDGTNmfP/994GBgc3fNdJoNHNz82fPni1fvrxbt24FBQXz589HCO3bt8/Z2TkpKWnWrFmDBw9et24dg8GIiIgoLCyMi4sbOHDg+yVpIpEoIyPj0aNHqampK1as6NKlC16el5f39OlTiUTS1AtlMlnDd8RHjCAIPT29lStX4hyVVFFRER0dnZqaum3bNl9fX3J5dXX1rVu3IiIihg4dunr16vfYC43Arl27JhQKp0yZon2eI5VKr169amxs3Lt3b3KhUql8+fIlm83GZ7956enpd+/eLS0t3bhxo5OT0/sFz+VyIyMjU1NTt2zZYmdn906vlcvlqampu3fvfvz4saGh4c6dO3v06IEQ4nA4x48fLyoqIghi+vTp75374Y9VUVFRt27d3m8LzSsuLr58+TKXy2UymZMnT9b+ei4rK3v48CGPx2MwGF988QWdTjc2NnZyclq0aNGyZcvCw8Ob32UajWZiYlJWVtapU6fw8HChULhw4cL09PRDhw6RH0ArK6tffvnFzMzsypUrkZGRBgYGEydOhCQNAAAAADpHIBBs37598ODBAQEBZL2BiYkJm81+j6316tULZ2gymezSpUs8Hm/mzJlTp04l764IgpDJZOrVL29lYGCgniQolcq4uLja2tpBgwZppElsNnv06NF1dXVGRkbqNTkREREEQXh4eGjslLe3d1MZmkqlevHiBUEQffr06d27N94alUoNCwu7cePG+vXrd+/e/dHvcdu1a9fokamqqlIoFGS1Gw5PLBYXFxfn5eUlJibGx8eLRCJnZ2crK6uAgICMjAx3d3ecFbu6ujo6OkqlUmNjY/XDVVdXt3Hjxjt37gwcOHDZsmXW1tbax5mXl4cQ+vbbb318fNSXZ2dn5+TksFisr776ytDQUCQSNbWFoqKi+/fv19fXk0sa5oppaWnx8fEIIbFYPHv2bI1KLaFQeP/+/crKSo0tp6SkIITwrTleIhKJCgsL4+PjHRwcNm7c6OXl1cyuSaXSjIwMFou1cOHC987QCILg8XgIIR8fH20eLuATKhQK09PTo6OjY2JiRCJRly5dNm3a5OLi0qZNG5VKpVAo/v777/z8/JkzZ5IZmkwmk8lkb904n88vKirSqN5kMBiNVvBqEIvFP/zww4MH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)
</center>

#### remove(Object o)：
1. 如果入参元素为空，则遍历数组查找是否存在元素为空，如果存在则调用fastRemove将该元素移除，并返回true表示移除成功。
2. 如果入参元素不为空，则遍历数组查找是否存在元素与入参元素使用equals比较返回true，如果存在则调用fastRemove将该元素移除，并返回true表示移除成功。
3. 否则，不存在目标元素，则返回false。

#### fastRemove(int index)：跟remove(int index)类似
1. 将modCount+1，并计算需要移动的元素个数。
2. 如果需要移动，将index+1位置及之后的所有元素，向左移动一个位置。
3. 将size-1位置的元素赋值为空（因为上面将元素左移了，所以size-1位置的元素为重复的，将其移除）。

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
ArrayList 有三种方式来初始化，构造方法源码如下：
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
以无参数构造方法创建 ArrayList 时，实际上初始化赋值的是一个空数组。当真正对数组进行添加元素操作时，才真正分配容量。**即向数组中添加第一个元素时，数组初始容量扩为 10。**

> **补充：JDK6 new一个无参构造的 ArrayList 对象时，直接创建了长度是 10 的 Object[] 数组 elementData 。**

### 2. 分析扩容步骤
上文add方法在添加元素之前会先调用 **==ensureCapacityInternal==** 方法，
主要是有两个目的：
* 如果没初始化则进行初始化；
* 校验添加元素后是否需要扩容。

这里以无参构造函数创建的 ArrayList 为例分析
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
>注意 ：JDK11 移除了 ensureCapacityInternal() 和 ensureExplicitCapacity() 方法

#### 2.2. 再来看看 ensureCapacityInternal() 方法
（JDK7）可以看到 add 方法 首先调用了ensureCapacityInternal(size + 1)
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
**当要add进第1个元素时，minCapacity 为1，在Math.max()方法比较后，minCapacity 为 10。**

>此处和后续 JDK8 代码格式化略有不同，核心代码基本一样。

#### 2.3. ensureExplicitCapacity() 方法
如果调用 **ensureCapacityInternal()** 方法就一定会进入 **ensureExplicitCapacity()** 这个方法
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

* 当我们要 add 进第 1 个元素到 ArrayList 时，elementData.length 为 0 （因为还是一个空的 list），因为执行了 `ensureCapacityInternal()` 方法 ，所以 minCapacity 此时为 10。此时，`minCapacity - elementData.length > 0` 成立，所以会进入 `grow(minCapacity)` 方法。
* 当 add 第 2 个元素时，minCapacity 为 2，此时 e lementData.length(容量)在添加第一个元素后扩容成 10 了。此时，`minCapacity - elementData.length > 0` 不成立，所以不会执行`grow(minCapacity)` 方法。
* 添加第 3、4···到第 10 个元素时，依然不会执行 grow 方法，数组容量都为 10。

**直到添加第 11 个元素，minCapacity(为 11)比 elementData.length（为 10）要大。进入 grow 方法进行扩容。**

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
**int newCapacity = oldCapacity + (oldCapacity >> 1)**  
所以 ArrayList 每次扩容之后容量都会变为原来的 1.5 倍左右（oldCapacity 为偶数就是 1.5 倍，否则是 1.5 倍左右）！ 奇偶不同，比如 ：10+10/2 = 15, 33+33/2=49。如果是奇数的话会丢掉小数（0.5）

> ">>"（移位运算符）：>>1 即右移一位（相当于除 2），右移 n 位相当于除以 2 的 n 次方。这里 oldCapacity 明显右移了 1 位所以相当于 oldCapacity /2。  
对于大数据的 2 进制运算，位移运算符比那些普通运算符的运算要快很多，因为程序仅仅移动一下而已，不去计算，这样提高了效，节省了资源

**通过例子探究一下grow() 方法：**
* 当 add 第 1 个元素时，oldCapacity 为 0，经比较后第一个 if 判断成立，newCapacity = minCapacity(为 10)。但是第二个 if 判断不会成立，即 newCapacity 不比 MAX_ARRAY_SIZE 大，则不会进入 `hugeCapacity` 方法。数组容量为 10，add 方法中 return true,size 增为 1。
* 当 add 第 11 个元素进入 grow 方法时，newCapacity 为 15，比 minCapacity（为 11）大，第一个 if 判断不成立。新容量没有大于数组最大 size，不会进入 hugeCapacity 方法。数组容量扩为 15，add 方法中 return true,size 增为 11。

**这里补充一点比较重要，但是容易被忽视掉的知识点：**
* java 中的 **==length==** 属性是针对数组而言，比如说你声明了一个数组，想知道这个数组的长度则用到了 length 这个属性
* java 中的 **==length()==** 方法是针对字符串说的，如果想看这个字符串的长度则用到 length() 这个方法
* java 中的 **==size()==** 方法是针对泛型集合说的，如果想看这个泛型有多少个元素，就调用此方法来查看

#### 2.5. hugeCapacity() 方法。
从上面 `grow()` 方法源码我们知道： 如果新容量大于 **MAX_ARRAY_SIZE**，进入(执行) `hugeCapacity()` 方法来比较 minCapacity 和 MAX_ARRAY_SIZE，如果 minCapacity 大于最大容量，则新容量则为 **Integer.MAX_VALUE**，否则，新容量大小则为 **MAX_ARRAY_SIZE** 即为 **Integer.MAX_VALUE - 8。**
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
通过源码会发现 ArrayList 中大量调用了这两个方法。  
如：扩容操作以及add(int index, E element)、toArray() 等方法中都用到了这两个方法
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
Arrays.copyOf()方法主要是为了给原有数组扩容或者截取0到指定长度的新数组，测试代码如下：
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
ArrayList 源码中有一个 **ensureCapacity**，这个方法 ArrayList 内部没有被调用过，所以很显然是提供给外部调用的
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
**最好在 add 大量元素之前用 ensureCapacity 方法，以减少增量重新分配的次数**

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
通过运行结果，可以看出向 ArrayList 添加大量元素之前最好先使用ensureCapacity 方法，以减少增量重新分配的次数。
### Q1：BigDecimal
#### 问题描述
<font color="red">**java.lang.ArithmeticException: Non-terminating decimal expansion; no exact representable decimal result.**</font>
#### 详细描述：
在使用BigDecimal的除法计算中，有时候会出现结果为无限循环或者无限不循环小数的时候，就会报上述异常。
#### 解决方法：
**foo.divide(bar, 2,BigDecimal.ROUND_HALF_UP);**// 指定小数点长度为2（取整策略视具体情况而定）

### Q2：Arrays.asList()
#### 问题描述
<font color="red">**java.lang.UnsupportedOperationException**</font>
#### 详细描述
在使用**Arrays.asList()** 将数组转换成List集合时：
```java
public static void main(String[] args) {
    List<String> list = Arrays.asList("a", "b", "c");
    // list.clear();
    // list.remove("a");
    // list.add("g");
}
```
被注释的三行可以分别解开注释，运行后确实出现了描述中的异常。  
看看Arrays.asList()的源码：
```java
public static <T> List<T> asList(T... a) {
    return new ArrayList<>(a);
}
```
粗略一看，确实是转换成的**ArrayList**，可是我们继续看这里的**ArrayList**的实现的时候会发现：
```java
/**
 * @serial include
 */
private static class ArrayList<E> extends AbstractList<E>
    implements RandomAccess, java.io.Serializable
{
    private static final long serialVersionUID = -2764017481108945198L;
    private final E[] a;

    ArrayList(E[] array) {
        a = Objects.requireNonNull(array);
    }

    @Override
    public int size() {
        return a.length;
    }

    @Override
    public Object[] toArray() {
        return a.clone();
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T> T[] toArray(T[] a) {
        int size = size();
        if (a.length < size)
            return Arrays.copyOf(this.a, size,
                                 (Class<? extends T[]>) a.getClass());
        System.arraycopy(this.a, 0, a, 0, size);
        if (a.length > size)
            a[size] = null;
        return a;
    }

    @Override
    public E get(int index) {
        return a[index];
    }

    @Override
    public E set(int index, E element) {
        E oldValue = a[index];
        a[index] = element;
        return oldValue;
    }

    @Override
    public int indexOf(Object o) {
        E[] a = this.a;
        if (o == null) {
            for (int i = 0; i < a.length; i++)
                if (a[i] == null)
                    return i;
        } else {
            for (int i = 0; i < a.length; i++)
                if (o.equals(a[i]))
                    return i;
        }
        return -1;
    }

    @Override
    public boolean contains(Object o) {
        return indexOf(o) != -1;
    }

    @Override
    public Spliterator<E> spliterator() {
        return Spliterators.spliterator(a, Spliterator.ORDERED);
    }

    @Override
    public void forEach(Consumer<? super E> action) {
        Objects.requireNonNull(action);
        for (E e : a) {
            action.accept(e);
        }
    }

    @Override
    public void replaceAll(UnaryOperator<E> operator) {
        Objects.requireNonNull(operator);
        E[] a = this.a;
        for (int i = 0; i < a.length; i++) {
            a[i] = operator.apply(a[i]);
        }
    }

    @Override
    public void sort(Comparator<? super E> c) {
        Arrays.sort(a, c);
    }
}
```
通过源码可以看出通过**Arrays.asList()** 转换的**ArrayList** 并不是我们平时使用的**ArrayList** ，而是**Arrays**的一个内部类（**Arrays$ArrayList**），**而且这个内部类没有add，clear，remove方法，所以抛出的异常其实来自于AbstractList。**

点进**AbstractList** 就会发现抛出异常的地方，clear底层也会调用到remove所以也会抛出异常。
```java
public E remove(int index) {
    throw new UnsupportedOperationException();
}
public void add(int index, E element) {
    throw new UnsupportedOperationException();
}
```
#### 解决方法（总结）：
1. Arrays.asList()不要乱用，底层其实还是数组。
2. 如果使用了Arrays.asList()的话，最好不要使用其集合的操作方法。
3. 最简便的方法(推荐)
```java
List list = new ArrayList<>(Arrays.asList("a", "b", "c"))可以在外面这样包一层真正的ArrayList。
```
4. 使用 Java8 的Stream(推荐)
```java
Integer [] myArray = { 1, 2, 3 };
List myList = Arrays.stream(myArray).collect(Collectors.toList());
//基本类型也可以实现转换（依赖boxed的装箱操作）
int [] myArray2 = { 1, 2, 3 };
List myList = Arrays.stream(myArray2).boxed().collect(Collectors.toList());
```
5. 使用 Guava(推荐)  
    对于不可变集合，你可以使用ImmutableList类及其of()与copyOf()工厂方法：（参数不能为空）
    ```java
    List<String> il = ImmutableList.of("string", "elements");  // from varargs
    List<String> il = ImmutableList.copyOf(aStringArray);      // from array
    ```
    对于可变集合，你可以使用Lists类及其newArrayList()工厂方法：
    ```java
    List<String> l1 = Lists.newArrayList(anotherListOrCollection);    // from collection
    List<String> l2 = Lists.newArrayList(aStringArray);               // from array
    List<String> l3 = Lists.newArrayList("or", "string", "elements"); // from varargs
    ```
6. 使用 Apache Commons Collections
```java
List<String> list = new ArrayList<String>();
CollectionUtils.addAll(list, str);
```
7. 使用 Java9 的 List.of()方法
```java
/* 不支持基本数据类型 */
Integer[] array = {1, 2, 3};
List<Integer> list = List.of(array);
System.out.println(list); /* [1, 2, 3] */
```
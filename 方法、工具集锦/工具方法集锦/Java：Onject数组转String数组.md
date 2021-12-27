有时在使用集合的时候，需要将集合转换成数组，会使用到toArray()
```java
public static void main(String[] args) {
    ArrayList<String> arrayList = new ArrayList<>();
    arrayList.add("aa");
    arrayList.add("bb");
    arrayList.add("cc");
    arrayList.add("dd");
    Object[] objects = arrayList.toArray();
}
```
可以发现toArray()方法返回的是一个Object的数组，但是我们希望保留原类型，或者说将Obeject数组转换成自己想要的类型。  

直接想到的方法可能就是强制类型转换：
```java
String[] strings = (String[])objects;
```
此时会出现如下错误：
```java
Exception in thread "main" java.lang.ClassCastException: [Ljava.lang.Object; cannot be cast to [Ljava.lang.String;
```
由此可见，数组类型是无法进行强制类型转换的。  

正确的方法如下：
##### 1.System.arraycopy
把一个数组中某一段字节数据放到另一个数组中
```java
String[] strings = new String[objects.length];
System.arraycopy(objects, 0, strings, 0, objects.length);
```
System.arraycopy()的源码如下：
```java
/**
 * Copies an array from the specified source array, beginning at the
 * specified position, to the specified position of the destination array.
 * A subsequence of array components are copied from the source
 * array referenced by <code>src</code> to the destination array
 * referenced by <code>dest</code>. The number of components copied is
 * equal to the <code>length</code> argument. The components at
 * positions <code>srcPos</code> through
 * <code>srcPos+length-1</code> in the source array are copied into
 * positions <code>destPos</code> through
 * <code>destPos+length-1</code>, respectively, of the destination
 * array.
 * .................................
 * .................................
 * .................................
 * .................................
 * @param      src      the source array.
 * @param      srcPos   starting position in the source array.
 * @param      dest     the destination array.
 * @param      destPos  starting position in the destination data.
 * @param      length   the number of array elements to be copied.
 * @exception  IndexOutOfBoundsException  if copying would cause
 *               access of data outside array bounds.
 * @exception  ArrayStoreException  if an element in the <code>src</code>
 *               array could not be stored into the <code>dest</code> array
 *               because of a type mismatch.
 * @exception  NullPointerException if either <code>src</code> or
 *               <code>dest</code> is <code>null</code>.
 */
public static native void arraycopy(Object src,  int  srcPos,
                                    Object dest, int destPos,
                                    int length);
```
>从指定的源数组中复制一个数组，从指定位置开始，到目标数组的指定位置

##### 2.Arrays.copyOf
```java
String[] strings = Arrays.copyOf(objects, objects.length, String[].class);
```
Arrays.copyOf()不仅仅只是拷贝数组中的元素，在拷贝元素时，会创建一个新的数组对象。

而System.arrayCopy只拷贝已经存在数组元素。如果我们看过Arrays.copyOf()的源码就会知道，该方法的底层还是调用了System.arrayCopyOf()方法。  

Arrays.copyOf()源码如下：
```java
/**
 * Copies the specified array, truncating or padding with nulls (if necessary)
 * so the copy has the specified length.  For all indices that are
 * valid in both the original array and the copy, the two arrays will
 * contain identical values.  For any indices that are valid in the
 * copy but not the original, the copy will contain <tt>null</tt>.
 * Such indices will exist if and only if the specified length
 * is greater than that of the original array.
 * The resulting array is of the class <tt>newType</tt>.
 *
 * @param <U> the class of the objects in the original array
 * @param <T> the class of the objects in the returned array
 * @param original the array to be copied
 * @param newLength the length of the copy to be returned
 * @param newType the class of the copy to be returned
 * @return a copy of the original array, truncated or padded with nulls
 *     to obtain the specified length
 * @throws NegativeArraySizeException if <tt>newLength</tt> is negative
 * @throws NullPointerException if <tt>original</tt> is null
 * @throws ArrayStoreException if an element copied from
 *     <tt>original</tt> is not of a runtime type that can be stored in
 *     an array of class <tt>newType</tt>
 * @since 1.6
 */
public static <T,U> T[] copyOf(U[] original, int newLength, Class<? extends T[]> newType) {
    @SuppressWarnings("unchecked")
    T[] copy = ((Object)newType == (Object)Object[].class)
        ? (T[]) new Object[newLength]
        : (T[]) Array.newInstance(newType.getComponentType(), newLength);
    System.arraycopy(original, 0, copy, 0,
                     Math.min(original.length, newLength));
    return copy;
}
```
##### 3.Arrays.asList
这里我们首先将对象数组转换为对象列表，然后使用toArray(T[])方法将列表转储到新分配的String数组中
```java
String[] strings = Arrays.asList(objects).toArray(new String[0]);
// 或者
// String[] strings = Arrays.asList(objects).toArray(new String[objects.length]);
```
也可以直接将集合进行转换
```java
public static void main(String[] args) {
    ArrayList<String> arrayList = new ArrayList<>();
    arrayList.add("aa");
    arrayList.add("bb");
    arrayList.add("cc");
    arrayList.add("dd");
    // 直接
    String[] strings1 = arrayList.toArray(new String[0]);
}
```
最终效果和上面通过Object[]转换一样。  
相当于没有中间转换Object[]这一步，如果是集合转换成指定数组的话，可以直接这样使用；如果是Object数组转换成指定数组的话就需要先asList转换成集合。

##### 4.Java8中Arrays.stream
在Java 8中，我们可以使用Stream API轻松地将对象数组转换为字符串数组。  
先将指走的对象数组 转换为顺序Stream，然后使用toArray()方法将流的元素累积到新的字符串数组中。
```java
String[] strings = Arrays.stream(objects).toArray(String[]::new);
```
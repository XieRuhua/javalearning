# String

[toc]

## 一、String的hashCode()与 equals()
### 1. hashCode()和equals()相关介绍:
#### 1.1. hashCode()介绍:
`hashCode()` 的作用是获取**哈希码**，也称为**散列码**；它实际上是返回一个 `int 整数`。**这个哈希码的作用是确定该对象在哈希表中的索引位置。**  
`hashCode()`定义在 `JDK` 的 `Object` 类中，这就意味着 Java 中的任何类都包含有 `hashCode()` 函数。  
另外需要注意的是： `Object` 的 `hashcode` 方法是**本地方法（native**），也就是用 `c` 语言或 `c++` 实现的，该方法通常用来将对象的 **内存地址** 转换为整数之后返回。

```java
// Object 类中第100行
public native int hashCode();
```
散列表存储的是**键值对(key-value)** ，它的特点是：**能根据“键”快速的检索出对应的“值”。这其中就利用到了散列码！（可以快速找到所需要的对象）**

#### 1.2. 为什么要有 hashCode？
以 **“HashSet 如何检查重复”** 为例子来说明为什么要有 hashCode？

例如：当把对象加入 `HashSet` `时，HashSet` 会先计算对象的 `hashcode` 值来判断对象加入的位置，同时也会与其他已经加入的对象的 `hashcode` 值作比较，如果没有相符的 `hashcode`，`HashSet` 会假设对象没有重复出现。  
但是如果发现有相同 hashcode 值的对象，这时会再调用 **equals()** 方法来检查 `hashcode` 相等的对象是否真的相同。如果两者相同，`HashSet` 就不会让其加入操作成功。如果不同的话，就会重新散列到其他位置。  
**这样就大大减少了 equals 的次数，相应就大大提高了执行速度。**

#### 1.3.为什么重写 equals 时必须重写 hashCode 方法？
如果两个对象相等，则 `hashcode` 一定也是相同的。

两个对象相等，对两个对象分别调用 `equals` 方法都返回 `true`。但是，两个对象有相同的 `hashcode` 值时，它们也不一定是相等的 。**因此，equals 方法被覆盖过，则 hashCode 方法也必须被覆盖。**

>**`hashCode()`** 的默认行为是对堆上的对象产生独特值。如果没有重写 **`hashCode()`** ，则该 class 的两个对象无论如何都不会相等（即使这两个对象指向相同的数据）

#### 1.4. 为什么两个对象有相同的 hashcode 值，它们也不一定是相等的？
以下内容摘自《Head Fisrt Java》。

>因为 **`hashCode()`** 所使用的哈希算法也许刚好会让多个对象传回相同的哈希值。越糟糕的哈希算法越容易碰撞，但这也与数据值域分布的特性有关（所谓碰撞也就是指的是不同的对象得到相同的 `hashCode。`

刚刚提到了 `HashSet`,如果 `HashSet` 在对比的时候，同样的 `hashcode` 有多个对象，它会使用 `equals()` 来判断是否真的相同。也就是说 `hashcode` 只是用来缩小查找成本。
### 2. String重写后的hashCode()和equals()
上面说到`Object`的 **hashCode()** 方法计算出的哈希码的作用是确定该对象在哈希表中的索引位置。  
但是在使用`String`的`equals()`方法的时候比较的其实是`String`对象中的实际值，这是因为`String`方法重写了 **equals()** ，源码如下：
```java
public boolean equals(Object anObject) {
    if (this == anObject) {
        return true;
    }
    if (anObject instanceof String) {
        String anotherString = (String)anObject;
        int n = value.length;
        if (n == anotherString.value.length) {
            char v1[] = value;
            char v2[] = anotherString.value;
            int i = 0;
            while (n-- != 0) {
                if (v1[i] != v2[i])
                    return false;
                i++;
            }
            return true;
        }
    }
    return false;
}
```
这里在**Object.equals()** 方法的基础上增加了值的判断，简单说就是判断地址值是否相等，如果相等，则返回true，如果不相等，则继续判断内容是否相同，如果存在任意一个字符不相同（区分大小写），则返回false。 **<font color="red">如果长度相同而且所有字符均相同，才被认定为true</font>**  

同时也重写了**`hashCode()`** 方法
```java
/**
 * Returns a hash code for this string. The hash code for a
 * {@code String} object is computed as
 * <blockquote><pre>
 * s[0]*31^(n-1) + s[1]*31^(n-2) + ... + s[n-1]
 * </pre></blockquote>
 * using {@code int} arithmetic, where {@code s[i]} is the
 * <i>i</i>th character of the string, {@code n} is the length of
 * the string, and {@code ^} indicates exponentiation.
 * (The hash value of the empty string is zero.)
 *
 * @return  a hash code value for this object.
 */
public int hashCode() {
    int h = hash;
    if (h == 0 && value.length > 0) {
        char val[] = value;

        for (int i = 0; i < value.length; i++) {
            h = 31 * h + val[i];
        }
        hash = h;
    }
    return h;
}
```
按照上面源码举例说明：  
```java
String msg = "abcd";  // 此时value[] = {'a','b','c','d'}  
```
因此for循环会执行4次  
第一次：h = 31x0 + a = 97   
第二次：h = 31x97 + b = 3105   
第三次：h = 31x3105 + c = 96354   
第四次：h = 31x96354 + d = 2987074   

由以上代码计算可以算出 `msg` 的`hashcode = 2987074`  刚好与 **System.err.println(new String("abcd").hashCode());** 进行验证

在源码的`hashcode`的注释中还提供了一个多项式计算方式：
```
s[0]*31^(n-1) + s[1]*31^(n-2) + ... + s[n-1]      
s[0] ：表示字符串中指定下标的字符
n：表示字符串中字符长度
```
此时`msg`的`hashCode`的计算方式为：  
**ax31^3 + bx31^2 + cx31^1 + d = 2987074  + 94178 + 3069 + 100 = 2987074**

#### 问题：为什么 String hashCode 方法选择数字31作为乘子
**定义`hashcode`时要使用`31`作为乘子主要有以下几个原因：**
1. 31 有个很好的性能，即用移位和减法来代替乘法，可以得到更好的性能： `31 * i == (i << 5）- i`， 现代的 VM 可以自动完成这种优化。
2. **31是一个奇素数** ，选择素数(质数)的好处就是如果我用一个数字来乘以这个素数，那么最终出来的结果也只能被素数本身和被乘数(以及被乘数的整除因子)还有1来整除！这样，以31作为乘子参与乘法计算得出的hashcode值，在后面进行 **`取模`(实际上是与运算时)** ，得到相同`index`的概率会降低，**即降低了哈希冲突的概率** 。
3. 31作为一个既不太大又不太小的乘子，计算出来的`hashcode`值范围处于一个“适中”的区间，能够很好的降低哈希冲突，进行数据查找时可以提高效率。一方面，乘子太小容易导致计算出来的`hashcode`值范围处于一个“较小”的区间，在后面进行 **`取模`(实际上是与运算时)** ，得到相同index的概率会升高，即哈希冲突的概率会提高；另一方面，乘子太大可能会导致相乘时造成数据溢出的概率增大。
4. 31只占用`5bits`(11111B)，相乘造成数据溢出的概率较小。

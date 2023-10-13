# Java中的语法糖

[笔记内容参考1：不了解这12个语法糖，别说你会Java！](https://mp.weixin.qq.com/s?__biz=Mzg3NzU5NTIwNg==&mid=2247487974&idx=1&sn=1d66f11daaf16a04a974eaaf5648b66f&source=41#wechat_redirect)   
[笔记内容参考2：Java开发必会的反编译知识](https://mp.weixin.qq.com/s?__biz=MzI3NzE0NjcwMg==&mid=2650120609&idx=1&sn=5659f96310963ad57d55b48cee63c788&chksm=f36bbc80c41c3596a1e4bf9501c6280481f1b9e06d07af354474e6f3ed366fef016df673a7ba&scene=21#wechat_redirect)   
[笔记内容参考3：Java中的语法糖](https://www.cnblogs.com/54chensongxia/p/11665843.html)

[toc]

## 一、语法糖概述
**语法糖（`Syntactic Sugar`）**：也称糖衣语法，指在计算机语言中添加的 **某种语法** ，这种语法对语言本身的功能来说没有什么影响，只是为了方便程序员进行开发，提高开发效率，使用这种语法写出来的程序可读性也更高。说白了，**语法糖就是对现有语法的一个封装。**

**但其实，Java虚拟机是并不支持语法糖的，语法糖在程序编译阶段就会被还原成简单的基础语法结构，这个过程就是解语法糖**。所以在Java中真正支持语法糖的是`Java编译器`。

**解语法糖：** 语法糖的存在主要是方便开发人员使用。但Java虚拟机并不支持这些语法糖。这些语法糖在编译阶段就会被还原成简单的基础语法结构，这个过程就是解语法糖。

## 二、Java中的语法糖
Java编程语言提供了很多语法糖，整理了下，主要有下面几种常用的语法糖。
- `switch-case`对`String`和`枚举类`的支持
- 泛型
- 包装类自动装箱与拆箱
- 方法可变参数
- 枚举
- 内部类
- 条件编译
- 断言
- 数值字面量
- 增强`for`循环
- `try-with-resource`语法
- `Lambda`表达式
- 字符串`+`号语法

## 三、Java中的语法糖示例代码
### 前言
#### 编程语言
在介绍编译和反编译之前，我们先来简单介绍下`编程语言（Programming Language）`。`编程语言（Programming Language）`分为`低级语言（Low-level Language）`和`高级语言（High-level Language）`。
- 低级语言：`机器语言（Machine Language）`和`汇编语言（Assembly Language）`，直接用计算机指令编写程序。
- 高级语言：`C`、`C++`、`Java`、`Python`等，用`语句（Statement）`编写程序，语句是计算机指令的抽象表示。

举个例子，同样一个语句用C语言、汇编语言和机器语言分别表示如下：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的语法糖/语言表现形式示例.png)
</center>

计算机只能对数字做运算，符号、声音、图像在计算机内部都要用数字表示，指令也不例外，上表中的机器语言完全由`十六进制数字`组成。  
最早的程序员都是直接用机器语言编程，但是很麻烦，需要查大量的表格来确定每个数字表示什么意思，编写出来的程序很不直观，而且容易出错，于是有了`汇编语言`，把机器语言中一组一组的数字用`助记符（Mnemonic）`表示，直接用这些助记符写出汇编程序，然后让`汇编器（Assembler）`去查表把`助记符`替换成数字，这个过程也就是把汇编语言翻译成了机器语言。

但是，汇编语言用起来同样比较复杂，后面，就衍生出了`Java`、`C`、`C++`等 **高级语言** 。

#### 什么是编译
上面提到语言有两种，一种`低级语言`，一种`高级语言`。 **可以这样简单的理解：低级语言是计算机认识的语言、高级语言是程序员认识的语言。**

那么如何从高级语言转换成低级语言呢？这个过程其实就是 **`编译`** 。

从上面的例子还可以看出，`C语言`的语句和低级语言的指令之间不是简单的一一对应关系，一条`a=b+1;`语句要翻译成三条汇编或机器指令，这个过程称为`编译（Compile）`，由`编译器（Compiler）`来完成，显然编译器的功能比汇编器要复杂得多。  
用C语言编写的程序必须经过编译转成机器指令才能被计算机执行，编译需要花一些时间，这是用高级语言编程的一个缺点，然而更多的是优点。首先，用C语言编程更容易，写出来的代码更紧凑，可读性更强，出了错也更容易改正。

**将便于人编写、阅读、维护的高级计算机语言所写作的源代码程序，翻译为计算机能解读、运行的低阶机器语言的程序的过程就是编译。负责这一过程的处理的工具叫做`编译器`。**

现在我们知道了什么是编译，也知道了什么是编译器。不同的语言都有自己的编译器，如Java语言中负责编译的编译器是一个命令：`javac`。
> javac是收录于JDK中的Java语言编译器。该工具可以将后缀名为.java的源文件编译为后缀名为.class的可以运行于Java虚拟机的字节码。

当我们写完一个 **`HelloWorld.java`文件后，我们可以使用`javac HelloWorld.java`命令来生成`HelloWorld.class`文件，这个`class`类型的文件是JVM可以识别的文件。通常我们认为这个过程叫做Java语言的编译。其实，`class`文件仍然不是机器能够识别的语言，因为机器只能识别机器语言，还需要JVM再将这种`class`文件类型字节码转换成机器可以识别的机器语言。**

#### 什么是反编译
`反编译`的过程与`编译`刚好相反，就是将已编译好的编程语言还原到未编译的状态，也就是找出程序语言的源代码。就是将机器看得懂的语言转换成程序员可以看得懂的语言。Java语言中的反编译一般指将`class`文件转换成`java`文件，而这个过程也需要`反编译工具`。

有了反编译工具，我们可以做很多事情，最主要的功能就是有了反编译工具，我们就能读得懂Java编译器生成的字节码，从而知道底层实现逻辑。

#### Java反编译工具
[参考文章：Java开发必会的反编译知识（附支持对Lambda进行反编译的工具）](https://mp.weixin.qq.com/s?__biz=MzI3NzE0NjcwMg==&mid=2650120609&idx=1&sn=5659f96310963ad57d55b48cee63c788&chksm=f36bbc80c41c3596a1e4bf9501c6280481f1b9e06d07af354474e6f3ed366fef016df673a7ba&scene=21#wechat_redirect)

##### JAD
下载地址：[JDA-官网](https://varaneckas.com/jad/)  
使用方法：下载解压后的Readme.txt中有详细使用方式或使用命令`jad -help`查看。

该笔记使用最简单的方式即可：
```bash
// 在命令行中使用以下命令即反编译xxx.class，-o参数表示覆盖原文件
jad -o xxx.class
```
注意：`jad`已经很久不更新了，在对`Java7`生成的字节码进行反编译时，偶尔会出现不支持的问题，在对`Java 8`的`lambda表达式`反编译时就彻底失败，比如会直接报错`JavaClassFileParseException: Invalid tag value 0x12`

##### CRF
下载地址：[CFR-官网](http://www.benf.org/other/cfr/)  
使用方法：查阅官网或或使用命令`jad -help`查看。

该笔记在反编译`lambda`的时候会使用以下命令：
```bash
java -jar cfr-0.152.jar xxx.class --decodelambdas false
```

#### 补充：IDEA查看class字节码文件
注：如果直接找到`class文件`用文本编辑器打开是乱码，而IDEA自带反编译工具，因此可以直接打开`class文件`。

**使用IDEA查看class文件**  
使用编译工具`IDEA`编写好代码，运行成功之后，就可以在`src`同目录下的`target`目录中找到对应地址的编译后的`class文件`。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的语法糖/在IDEA中查看class文件1.png)  
![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的语法糖/在IDEA中查看class文件2.png)
</center>

可以看到`class文件`相较于原`java文件`增加了一个 **无参构造函数** ，说明编译器会帮助程序员实现一些默认操作。

**使用IDEA查看字节码内容**  
在`IDEA`上安装插件`bytecode Viewer`（一般默认是已安装的）

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的语法糖/IDEA-插件bytecodeViewer.png) ![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的语法糖/IDEA使用插件bytecodeViewer.png)  
![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的语法糖/IDEA查看字节码文件.png)
</center>

打开`class文件`预览，然后依次点击顶部导航栏`View-->Show ByteCode`即可查对应的字节码文件（注意：鼠标光标需要在`class文件`中或选中需要查看的`class文件`，`View`才有`Show ByteCode`选项）。

### 1. switch-case对String和枚举类的支持
Java中的swith自身原本就支持基本类型，如`int`、`char`等。  
对于`int`类型，直接进行数值的比较。对于`char`类型则是比较其`ascii码`。  
所以，对于编译器来说，switch中其实只能使用整型，任何类型的比较都要转换成整型。比如`byte`、`short`、`char`(ackii码是整型)以及`int`。

自`Java 7`之后switch开始支持`String`。有以下代码：
```java
public static void main(String[] args) {
    String str = "world";
    switch (str) {
        case "hello":
            System.out.println("hello");
            break;
        case "world":
            System.out.println("world");
            break;
        default:
            break;
    }
}
```

编译后再反编译的代码如下：
```java
public static void main(String args[]) {
    String str = "world";
    String s = str;
    byte byte0 = -1;
    switch (s.hashCode()) {
        case 99162322:
            if (s.equals("hello"))
                byte0 = 0;
            break;

        case 113318802:
            if (s.equals("world"))
                byte0 = 1;
            break;
    }
    switch (byte0) {
        case 0: // '\0'
            System.out.println("hello");
            break;

        case 1: // '\001'
            System.out.println("world");
            break;
    }
}
```
通过反编译的代码，原来`字符串`的switch是通过`equals()`和`hashCode()`方法来实现的。还好`hashCode()`方法返回的是`int`，而不是`long`。

仔细看下可以发现，字符串进行switch的实际是哈希值（`hashCode()`方法），然后通过使用`equals()`方法比较进行安全检查，这个检查是必要的，因为哈希可能会发生碰撞。因此它的性能是不如使用枚举进行switch或者使用纯整数常量，但这也不是很差。

补充：switch中的枚举使用
```java
// 枚举类
public enum EnumTest {
    A, B;
}

// 编译前
public static void main(String[] args) {
    switch (EnumTest.values()[0]) {
        case A:
            System.out.println("Enum-A");
            break;
        case B:
            System.out.println("Enum-B");
            break;
        default:
            break;
    }
}

// 编译后再反编译
public static void main(String args[]) {
    static class _cls1 {

        static final int $SwitchMap$com$test$EnumTest[];

        static {
            $SwitchMap$com$test$EnumTest = new int[EnumTest.values().length];
            try {
                $SwitchMap$com$test$EnumTest[EnumTest.A.ordinal()] = 1;
            } catch (NoSuchFieldError nosuchfielderror) {
            }
            try {
                $SwitchMap$com$test$EnumTest[EnumTest.B.ordinal()] = 2;
            } catch (NoSuchFieldError nosuchfielderror1) {
            }
        }
    }

    switch (_cls1..SwitchMap.com.test.EnumTest[EnumTest.values()[0].ordinal()])
    {
        case 1: // '\001'
            System.out.println("Enum-A");
            break;

        case 2: // '\002'
            System.out.println("Enum-B");
            break;
    }
}
```
通过字节码可以看出如果switch后面是`Enum类型`的话，编译器会将其转换为这个枚举定义的`下标`（`ordinal()`方法就是获取当前枚举元素的索引）。其实最后都是比较的整数类型。

### 2. 泛型
很多语言都是支持 **泛型** 的，但是不同的编译器对于泛型的处理方式是不同的。 **在JDK5中，Java语言引入了泛型机制。**

通常情况下，一个编译器处理泛型有两种方式：
1. `Code specialization（代码专用）`：在编译时根据泛型生成 **不同的Code** 。
2. `Code sharing（代码共享）`：所有泛型 **共享同一Code** ，通过`类型检查`、`类型擦除`、`类型转换`实现。  
   此方式为每个泛型类型创建唯一的字节码表示，并且将该泛型类型的实例都映射到这个唯一的字节码表示上。将多种泛型类形实例映射到唯一的字节码表示是通过`类型擦除（type erasue）`实现的。

<font color="red">C++和C#是使用`Code specialization（代码专用）`的处理机制，而Java使用的是`Code sharing（代码共享）`的机制。</font>

也就是说，对于Java虚拟机来说，他根本不认识`Map<String, String> map`这样的语法。需要在编译阶段通过`类型擦除`的方式进行解语法糖。

`类型擦除`的主要过程如下：
1. 将所有的泛型参数用其最左边界（最顶级的父类型）类型替换。
2. 移除所有的类型参数。

```java
// 编译前
public static void main(String[] args) {
    HashMap<String, String> map = new HashMap<String, String>();
    map.put("name", "张三");
    map.put("age", "12");

    String name = map.get("name");
}

// 编译后再反编译
public static void main(String[] args) {
    HashMap map = new HashMap();
    map.put("name", "\u5F20\u4E09");
    map.put("age", "12");
    String name = (String) map.get("name");
}
```
上述代码`HashMap`的泛型被擦除之后获取`Strng类型`的`value`需要强转（因为value的类型String为泛型，被擦除了）。

虚拟机中没有泛型，只有`普通类`和`普通方法`，所有泛型类的类型参数在编译时都会被擦除，泛型类并没有自己独有的Class类对象。比如并不存在`List<String>.class`或是`List<Integer>.class`，而只有`List.class`。

### 3. 包装类自动装箱与拆箱
自动装箱就是Java自动将原始类型值转换成对应的对象，比如将`int`的变量转换成`Integer对象`，这个过程叫做装箱，反之将`Integer对象`转换成`int`类型值，这个过程叫做拆箱。  
参考：[一文读懂什么是Java中的自动拆装箱](http://mp.weixin.qq.com/s?__biz=MzI3NzE0NjcwMg==&mid=2650121987&idx=1&sn=70bba3f7f42a269eeada9cecb34c10a5&chksm=f36bba22c41c3334b92f184e402f2f77e2d5e0a2e0a21ec5a8229773afcab4f026a0b6f47fc4&scene=21#wechat_redirect)

**因为这里的`装箱`和`拆箱`是自动进行的非人为转换，所以就称作为`自动装箱`和`自动拆箱`。**

原始类型`byte`、`short`、`char`、`int`、`long`、`float`、`double`、`boolean`  
封装类为`Byte`、`Short`、`Character`、`Integer`、`Long`、`Float`、`Double`、`Boolean`

自动装箱：
```java
// 编译前
public static void main(String[] args) {
    int i = 10;
    Integer n = i;
}

// 编译后再反编译
public static void main(String[] args) {
    int i = 10;
    Integer n = Integer.valueOf(i);
}
```

自动拆箱：
```java
// 编译前
public static void main(String[] args) {
    Integer i = 10;
    int n = i;
}

// 编译后再反编译
public static void main(String[] args) {
    Integer i = Integer.valueOf(10);
    int n = i.intValue();
}
```
从反编译的代码可以看出，在装箱的时候自动调用的是`Integer`的`valueOf方法`。而在拆箱的时候自动调用的是`Integer`的`intValue方法`。  
所以，装箱过程是通过调用包装器的`valueOf方法`实现的，而拆箱过程是通过调用包装器的`xxxValue方法`实现的。

### 4. 方法可变参数
`可变参数(variable arguments)`是在`Java 1.5`中引入的一个特性。它允许一个方法把 **任意数量** 的值作为参数。

演示代码：
```java
// 编译前
public static void main(String[] args) {
    print("参数1", "参数2", "参数3");
}
public static void print(String... strs) {
    for (int i = 0; i < strs.length; i++) {
        System.out.println(strs[i]);
    }
}

// 编译后再反编译
public static void main(String args[]) {
    print(new String[]{
        "\u53C2\u65701", "\u53C2\u65702", "\u53C2\u65703"
    });
}
public static transient void print(String strs[]) {
    for (int i = 0; i < strs.length; i++)
        System.out.println(strs[i]);

}
```
从反编译的代码可以看出，可变参数的方法在创建的时候会将参数定义为 **数组** ，在该方法被使用的时候，首先会创建一个 **数组** ，数组的长度就是调用该方法是传递的实参的个数，然后再把参数值全部放到这个 **数组** 当中，然后再把这个 **数组** 作为参数传递到被调用的方法中。

### 5. 枚举
`Java SE5`提供了一种新的类型-Java的 **枚举** 类型，关键字`enum`可以将一组具名的值的有限集合创建为一种新的类型，而这些具名的值可以作为常规的程序组件使用，这是一种非常有用的功能。参考：[Java的枚举类型用法介绍](http://mp.weixin.qq.com/s?__biz=MzI3NzE0NjcwMg==&mid=402247345&idx=1&sn=a0e1f8cc739dd8cf96ede6ec5181d244&chksm=7967d3904e105a867b1d737bc64e526756125ced5f33cc9a9b35064228f639e391d024e3abde&scene=21#wechat_redirect)

**`enum`就和`class`一样，只是一个关键字，他并不是一个类。**

定义一个枚举并编译：
```java
// 编译前
public enum EnumTest {
    A, B;
}

// 编译后再反编译
public final class EnumTest extends Enum {

    public static EnumTest[] values() {
        return (EnumTest[]) $VALUES.clone();
    }

    public static EnumTest valueOf(String name) {
        return (EnumTest) Enum.valueOf(com / test / EnumTest, name);
    }

    private EnumTest(String s, int i) {
        super(s, i);
    }

    public static final EnumTest A;
    public static final EnumTest B;
    private static final EnumTest $VALUES[];

    static {
        A = new EnumTest("A", 0);
        B = new EnumTest("B", 1);
        $VALUES = (new EnumTest[]{
                A, B
        });
    }
}
```
通过反编译的代码可以看到，`public final class EnumTest extends Enum`说明，该类是继承了`Enum类`的，同时`final`关键字声明了这个类也是不能被 **继承** 的。并且在创建对象的时候也定义了两个静态变量`A`和`B`以及两个静态方法`values（获取所有枚举值）`和`valueOf（根据参数获取匹配的枚举值）`。

当使用`enmu`来定义一个枚举类型的时候，编译器会自动帮我们创建一个`final`类型的类继承`Enum类`， **所以枚举类型不能被继承。**

### 6. 内部类
内部类又称为嵌套类，可以把内部类理解为外部类的一个普通成员。  
内部类之所以也是语法糖，是因为它仅仅是一个编译时的概念。

如下演示代码`OutClass.java`里面定义了一个内部类`InnerClass`：
```java
public class OutClass {
    private String userName;

    class InnerClass{
        private String name;
    }
}
```
使用`javac OutClass.java`命令进行编译。编译完成之后就会生成两个完全不同的`.class`文件了，分别是 **`OutClass.class`** 和 **`OutClass$InnerClass.class`** 。所以内部类的名字完全可以和它的外部类名字相同。

使用命令`jad -o OutClass.class`对`OutClass.class`反编译的时候，会把两个文件全部进行反编译，然后一起生成一个`OutClass.jad`文件。文件内容如下：
```java
public class OutClass {
    class InnerClass {

        private String name;
        final OutClass this$0;

        InnerClass() {
            this.this$0 = OutClass.this;
            super();
        }
    }

    public OutClass() {
    }

    private String userName;
}
```

分别查看两个`class`文件的字节码：
```java
/**
 * OutClass字节码文件
 */
public class com/test/OutClass {

  // compiled from: OutClass.java
  // access flags 0x0
  INNERCLASS com/test/OutClass$InClass com/test/OutClass InClass

  // access flags 0x2
  private Ljava/lang/String; userName

  // access flags 0x1
  public <init>()V
   L0
    LINENUMBER 3 L0
    ALOAD 0
    INVOKESPECIAL java/lang/Object.<init> ()V
    RETURN
   L1
    LOCALVARIABLE this Lcom/test/OutClass; L0 L1 0
    MAXSTACK = 1
    MAXLOCALS = 1

  // access flags 0x9
  public static main([Ljava/lang/String;)V
   L0
    LINENUMBER 12 L0
    RETURN
   L1
    LOCALVARIABLE args [Ljava/lang/String; L0 L1 0
    MAXSTACK = 0
    MAXLOCALS = 1
}
```

```java
/**
 * InnerClass字节码文件
 */
class com/test/OutClass$InClass {

  // compiled from: OutClass.java
  // access flags 0x0
  INNERCLASS com/test/OutClass$InClass com/test/OutClass InClass

  // access flags 0x2
  private Ljava/lang/String; name

  // access flags 0x1010
  final synthetic Lcom/test/OutClass; this$0

  // access flags 0x0
  <init>(Lcom/test/OutClass;)V
   L0
    LINENUMBER 6 L0
    ALOAD 0
    ALOAD 1
    PUTFIELD com/test/OutClass$InClass.this$0 : Lcom/test/OutClass;
    ALOAD 0
    INVOKESPECIAL java/lang/Object.<init> ()V
    RETURN
   L1
    LOCALVARIABLE this Lcom/test/OutClass$InClass; L0 L1 0
    LOCALVARIABLE this$0 Lcom/test/OutClass; L0 L1 1
    MAXSTACK = 2
    MAXLOCALS = 2
}
```
可以看到`OutClass.class`和`InnerClass.class`的字节码中`INNERCLASS属性`后面的值表示引用的内部类列表。

### 7. 条件编译
—般情况下，程序中的每一行代码都要参加编译。但有时候出于对程序代码优化的考虑，希望只对其中一部分内容进行编译，此时就需要在程序中加上条件，让编译器只对满足条件的代码进行编译，将不满足条件的代码舍弃，这就是条件编译。

如在`C`或`CPP`中，可以通过预处理语句来实现条件编译。在Java中也可实现条件编译。

如下测试代码：
```java
// 编译前
public static void main(String[] args) {
    final boolean DEBUG = true;
    if(DEBUG) {
        System.out.println("Hello, DEBUG!");
    }

    final boolean ONLINE = false;

    if(ONLINE){
        System.out.println("Hello, ONLINE!");
    }
}

// 编译后再反编译
public static void main(String args[]) {
    boolean DEBUG = true;
    System.out.println("Hello, DEBUG!");
    boolean ONLINE = false;
}
```
首先，在反编译后的代码中没有`System.out.println("Hello, ONLINE!");`，这其实就是条件编译。

因为当`if(ONLINE)`为`false`的时候，编译器就没有对其内的代码进行编译。所以，Java语法的条件编译，是通过判断条件为常量的`if语句`实现的。根据`if`判断条件的真假，编译器直接把分支为`false`的代码块消除。  
通过该方式实现的条件编译，必须在方法体内实现，而无法在正整个`Java`类的结构或者类的属性上进行条件编译。

这与`C/C++`的条件编译相比，确实更有局限性。在Java语言设计之初并没有引入条件编译的功能，虽有局限，但是总比没有更强。

### 8. 断言
在Java中，`assert`关键字是从`JAVA SE 1.4`引入的，为了避免和老版本的Java代码中使用了`assert`关键字导致错误，Java在执行的时候 **默认是不启动** 断言检查的（此时，所有的断言语句都将忽略！）。

如果要开启断言检查，则需要用开关`-enableassertions`或`-ea`来开启（启动参数中添加）。

如下测试代码（不打开断言开关）：
```java
// 编译前
public static void main(String args[]) {
    int a = 1;
    int b = 1;
    assert a == b;
    System.out.println("断言通过");
    assert a != b : "ErrorMessage";
    System.out.println("断言不通过");
}

// 编译后再反编译
public static void main(String args[]) {
    int a = 1;
    int b = 1;
    if (!$assertionsDisabled && a != b)
        throw new AssertionError();
    System.out.println("\u65AD\u8A00\u901A\u8FC7");
    if (!$assertionsDisabled && a == b) {
        throw new AssertionError("ErrorMessage");
    } else {
        System.out.println("\u65AD\u8A00\u4E0D\u901A\u8FC7");
        return;
    }
}

static final boolean $assertionsDisabled = !com / test / Demo.desiredAssertionStatus();
```

执行结果：
```
success
fail
```

通过反编译的代码可以发现其实断言的底层实现就是`if`语言，如果断言结果为`true`，则什么都不做，程序继续执行；如果断言结果为`false`，则程序抛出`AssertError`（判断语句后面的值为断言false的异常提示）来打断程序的执行。

上述代码开启断言开关之后的执行结果：
```
success
Exception in thread "main" java.lang.AssertionError: ErrorMessage
```
可以看到异常信息为指定的`ErrorMessage`。

### 9. 数值字面量
在`java 7`中，不管是 **整数** 还是 **浮点数** ，都允许在数字之间插入任意多个 **下划线** 。这些下划线不会对字面量的数值产生影响，目的就是方便阅读。

如下测试代码：
```java
// 编译前
public static void main(String[] args) {
    int i = 10_000;
    System.out.println(i);
}

// 编译后再反编译
public static void main(String[] args) {
    int i = 10000;
    System.out.println(i);
}
```

执行结果：
```
10000
```

编译过程就是把`_`删除了。也就是说编译器并不认识在数字字面量中的`_`，需要在编译阶段把他去掉。

注意： **下划线只能出现在数字中间，前后必须是数字。** 所以`“_100”`、`“0b_101“`是不合法的，无法通过编译。这样限制的动机就是可以降低实现的复杂度。有了这个限制，Java编译器只需在扫描源代码的时候将所发现的数字中间的下划线直接删除就可以了。如果不添加这个限制，编译器需要进行语法分析才能做出判断。比如：`_100`,可能是一个整数字面量100，也可能是一个变量名称。这就要求编译器的实现做出更复杂的改动。

```java
// 编译提示：Illegal underscore （非法下划线）
int i = 10000_;

// 编译提示：Cannot resolve symbol '_10000'（无法解析符号 '_10000'）
int i = _10000;
```

### 10. 增强for循环
增强for循环（`for-each`）日常开发经常会用到的，相比普通for循环要少写很多代码。

如下测试代码：
```java
// 编译前
public static void main(String[] args) {
    // 数据增强for循环
    String[] strs = {"数据1","数据2","数据3"};
    for (String str : strs) {
        System.out.println(str);
    }

    // 集合增强for循环
    List<String> strList = Arrays.asList(strs);
    for (String str : strList) {
        System.out.println(str);
    }
}

// 编译后再反编译
public static void main(String args[]) {
    String strs[] = {
        "\u6570\u636E1", "\u6570\u636E2", "\u6570\u636E3"
    };
    String args1[] = strs;
    int i = args1.length;
    for (int j = 0; j < i; j++) {
        String str = args1[j];
        System.out.println(str);
    }

    List strList = Arrays.asList(strs);
    String str;
    for (Iterator iterator = strList.iterator(); iterator.hasNext(); System.out.println(str))
        str = (String) iterator.next();
}
```
通过反编译后的代码可以看出`for-each`的实现原理其实就是使用了普通的`for循环`和`迭代器`。

### 11. try-with-resource语法
Java里，对于文件操作IO流、数据库连接等开销非常昂贵的资源，用完之后必须及时通过`close`方法将其关闭，否则资源会一直处于打开状态，可能会导致内存泄露等问题。

关闭资源的常用方式就是在`finally`块里是释放，即在`finally`块里调用close方法。

如下测试代码（手动关闭流）：
```java
public static void main(String[] args) {
    BufferedReader br = null;
    try {
        String line;
        br = new BufferedReader(new FileReader("d:\\temp.txt"));
        while ((line = br.readLine()) != null) {
            System.out.println(line);
        }
    } catch (IOException e) {
        // handle exception
    } finally {
        try {
            if (br != null) {
                // 关闭流
                br.close();
            }
        } catch (IOException ex) {
            // handle exception
        }
    }
}
```

从`Java 7`开始，jdk提供了一种更好的方式关闭资源，使用`try-with-resources`语句，改写上面的代码，如下：
```java
// 编译前
public static void main(String[] args) {
    try (BufferedReader br = new BufferedReader(new FileReader("d:\\temp.txt"))) {
        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(line);
        }
    } catch (IOException e) {
        // handle exception
    }
}
```
这种方式并不需要使用在`finally`中写很多代码的方式，`try-with-resource`语法糖优雅很多。

查看编译后的代码（`class文件`）：
```java
public static void main(String[] args) {
    BufferedReader br = null;
    try {
        br = new BufferedReader(new FileReader("d:\\temp.txt"));

        String line;
        while((line = br.readLine()) != null) {
            System.out.println(line);
        }
    } catch (IOException var11) {
    } finally {
        try {
            if (br != null) {
                br.close();
            }
        } catch (IOException var10) {
        }
    }
}
```
其实背后的原理也很简单，那些我们没有做的关闭资源的操作，编译器都帮我们做了。

### 12. Lambda表达式
`Labmda`表达式并不是匿名内部类的语法糖（前面的内部类语法糖中，内部类在编译之后会有两个`class文件`，但是包含`lambda表达式`的类编译后只有一个文件），但是他也是一个语法糖。 **实现方式其实是依赖了一些JVM底层提供的lambda相关api。**

先来看一个简单的`lambda表达式`。遍历一个list：
```java
// 编译前
public static void main(String[] args) {
    List<String> strList = Arrays.asList("数据1","数据2","数据3");
    strList.forEach(str->{
        System.out.println(str);
    });
}
```

```java
// 编译后再反编译
// 使用命令java -jar cfr-0.152.jar Demo.class --decodelambdas false进行反编译
public static void main(String[] args) {
    List<String> strList = Arrays.asList("\u6570\u636e1", "\u6570\u636e2", "\u6570\u636e3");
    strList.forEach((Consumer<String>)LambdaMetafactory.metafactory(null, null, null, (Ljava/lang/Object;)V, lambda$main$0(java.lang.String ), (Ljava/lang/String;)V)());
}

private static /* synthetic */ void lambda$main$0(String str) {
    System.out.println(str);
}
```

可以看到，在`forEach`方法中，其实是调用了`java.lang.invoke.LambdaMetafactory#metafactory`方法，该方法的第四个参数`implMethod`指定了方法实现。可以看到这里其实是调用了一个`lambda$main$0`方法进行了输出。  
**而`lambda$main$0`方法就是一个简单的输出方法。**

再来看一个稍微复杂一点的，先对List进行过滤，然后再输出：
```java
// 编译前
public static void main(String[] args) {
    List<String> strList = Arrays.asList("数据1", "数据2", "数据3");

    // 过滤
    List filterList = strList.stream().filter(string -> string.contains("数据2")).collect(Collectors.toList());

    // 循环打印
    filterList.forEach(s -> {
        System.out.println(s);
    });
}
```

```java
// 编译后再反编译
// 使用命令java -jar cfr-0.152.jar Demo.class --decodelambdas false进行反编译
public static void main(String[] args) {
    List<String> strList = Arrays.asList("\u6570\u636e1", "\u6570\u636e2", "\u6570\u636e3");
    List<Object> filterList = strList.stream().filter((Predicate<String>)LambdaMetafactory.metafactory(null, null, null, (Ljava/lang/Object;)Z, lambda$main$0(java.lang.String ), (Ljava/lang/String;)Z)())
        .collect(Collectors.toList());
    filterList.forEach((Consumer<Object>)LambdaMetafactory.metafactory(null, null, null, (Ljava/lang/Object;)V, lambda$main$1(java.lang.Object ), (Ljava/lang/Object;)V)());
}

private static /* synthetic */ void lambda$main$1(Object s) {
    System.out.println(s);
}

private static /* synthetic */ boolean lambda$main$0(String string) {
    return string.contains("\u6570\u636e2");
}
```

通过反编译的代码看出两个lambda表达式分别调用了`lambda$main$1`和`lambda$main$0`两个方法。其中`lambda$main$1`方法只是普通的打印，而`lambda$main$0`方法则是调用`String的contains`方法对数据进行筛选，并返回符合条件的数据。

**所以，lambda表达式的实现其实是依赖了一些底层的api，在编译阶段，编译器会把lambda表达式进行解糖，转换成调用内部api的方式。**

### 13.字符串+号语法
如下测试代码：
```java
// 编译前
public static void main(String[] args) {
    String s = null;
    s = s + "abc";
    System.out.println(s);
}

// 编译后再反编译
public static void main(String[] args) {
    String s = null;
    s = (new StringBuilder()).append(s).append("abc").toString();
    System.out.println(s);
}
```
字符串`+`号拼接原理：运行时，两个字符串`str1`, `str2`的拼接首先会`new`一个`StringBuilder`对象，然后分别对字符串进行`append`操作，最后调用`toString()`方法（ **字节码L1部分** ）。

**但是如果在编译期能确定字符相加的结果，则会进行编译期优化。** 如下：
```java
// 编译前
public static void main(String[] args) {
    String s = "a" + "b";
    System.out.println(s);
}

// 编译后再反编译
public static void main(String[] args) {
    String s = "ab";
    System.out.println(s);
}
```

## 四、补充：语法糖相关的注意事项
### 1. 泛型
#### 1.1 泛型遇到重载
```java
public class Demo {
    public static void method(List<String> list) {  
        System.out.println("invoke method(List<String> list)");  
    }  

    public static void method(List<Integer> list) {  
        System.out.println("invoke method(List<Integer> list)");  
    }  
}
```

编译失败，提示：
```
java: 名称冲突: method(java.util.List<java.lang.String>)和method(java.util.List<java.lang.Integer>)具有相同疑符
```

上面这段代码，有两个 **参数类型不同** 的重载函数，一个是`List<String>`另一个是`List<Integer>`，但是，这段代码是编译通不过的。因为参数`List<String>`和`List<Integer>`编译之后泛型都被擦除了，变成了一样的 **原生类型`List`** ， **泛型擦除** 后导致这两个方法的 **参数列表** 变得一模一样。

#### 1.2 泛型内包含静态变量
```java
public class Demo {
    public static void main(String[] args) {
        GT<Integer> gti = new GT<Integer>();
        gti.var = 1;

        GT<String> gts = new GT<String>();
        gts.var = 2;
        System.out.println(gti.var);
    }
}

class GT<T> {
    public static int var = 0;
}
```

执行结果：
```
2
```

由于经过 **泛型擦除** ，所有的泛型类实例都关联到同一份字节码上，泛型类的所有静态变量是共享的，因此定义的`gti.var = 1;`会被后面的`gts.var = 2;`覆盖。

### 2. 自动装箱与拆箱
#### 2.1 对象相等比较
```java
public static void main(String[] args) {
    Integer a = 1000;
    Integer b = 1000;
    Integer c = 100;
    Integer d = 100;
    System.out.println("a == b is " + (a == b));
    System.out.println(("c == d is " + (c == d)));
}
```

执行结果：
```
a == b is false
c == d is true
```
在`Java 5`中，在`Integer`的操作上引入了一个新功能来节省内存和提高性能： **整型对象通过使用相同的对象引用实现了缓存和重用。**

**注意：该缓存适用于整数值区间`-128` 至 `+127`。且只适用于自动装箱，使用构造函数创建对象时不适用。**

补充：Integer缓存源码，可以看到Integer缓存的范围是`[-127,128]`
```java
private static class IntegerCache {
    static final int low = -128;
    static final int high;
    static final Integer cache[];

    static {
        // high value may be configured by property
        int h = 127;
        String integerCacheHighPropValue =
            sun.misc.VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
        if (integerCacheHighPropValue != null) {
            try {
                int i = parseInt(integerCacheHighPropValue);
                i = Math.max(i, 127);
                // Maximum array size is Integer.MAX_VALUE
                h = Math.min(i, Integer.MAX_VALUE - (-low) -1);
            } catch( NumberFormatException nfe) {
                // If the property cannot be parsed into an int, ignore it.
            }
        }
        high = h;

        cache = new Integer[(high - low) + 1];
        int j = low;
        for(int k = 0; k < cache.length; k++)
            cache[k] = new Integer(j++);

        // range [-128, 127] must be interned (JLS7 5.1.7)
        assert IntegerCache.high >= 127;
    }

    private IntegerCache() {}
}
```

### 3. 增强for循环
在循环中删除元素：
```java
public static void main(String[] args) {
    List<String> strList = Arrays.asList("数据1","数据2","数据3");
    // 移除元素
    for (String str : strList) {
        if("数据2".equals(str)){
            strList.remove(str);
        }
    }

    // 打印元素
    for (String str : strList) {
        System.out.println(str);
    }
}
```

抛出异常：
```
Exception in thread "main" java.lang.UnsupportedOperationException
```

原因：  
`Iterator`是工作在一个独立的线程中，并且拥有一个 `mutex 锁`。 `Iterator`被创建之后会建立一个指向原来对象的单链索引表，当原来的对象数量发生变化时（原集合元素变化），这个索引表的内容不会同步改变，所以当索引指针往后移动的时候就找不到要迭代的对象，所以按照 `fail-fast` 原则 `Iterator` 会马上抛出`java.util.ConcurrentModificationException异常`。参考：[一不小心就让Java开发者踩坑的fail-fast是个什么鬼？](http://mp.weixin.qq.com/s?__biz=MzI3NzE0NjcwMg==&mid=2650123769&idx=2&sn=87d070e0a1a5e66a87eed4e22a99aa63&chksm=f36bb0d8c41c39ce80af4ff385a75f762a7f73850589517cb1ba28a42e9eb09eeb3bd81d4201&scene=21#wechat_redirect)

所以 `Iterator` 在工作的时候是不允许被迭代的对象被改变的。但你可以使用 `Iterator` 本身的方法`remove()`来删除对象，`Iterator.remove()` 方法会在删除当前迭代对象的同时维护索引的一致性。

修改后的代码：
```java
public static void main(String[] args) {
    List<String> strList = Arrays.asList("数据1", "数据2", "数据3");
    // 移除元素
    Iterator<String> iterator = strList.iterator();
    while (iterator.hasNext()) {
        if ("数据2".equals(iterator.next())) {
            iterator.remove();
        }
    }

    // 打印元素
    for (String str : strList) {
        System.out.println(str);
    }
}
```
依旧报错`Exception in thread "main" java.lang.UnsupportedOperationException`。

由于`Arrays.asList`这个方法只是对 `array` 数组进行了一次包装，以便于在程序中可以使用 `List`，在这个包装中并没有数据被拷贝或者创建。
同时，我们也不能对新创建的 `List` 的长度进行修改，因为添加或者删除 `List` 中的元素是不被允许的 。

这是因为 **`Arrays`中并没有实现`List`的`remove`方法，默认调用的还是`Iterator`的`remove()`方法：**
```java
default void remove() {
    throw new UnsupportedOperationException("remove");
}
```

再次修改（使用`new ArrayList<>()`来创建集合）：
```java
public static void main(String[] args) {
    List<String> strList = new ArrayList<String>();
    strList.add("数据1");
    strList.add("数据2");
    strList.add("数据3");

    // 移除元素
    Iterator<String> iterator = strList.iterator();
    while (iterator.hasNext()) {
        if ("数据2".equals(iterator.next())) {
            iterator.remove();
        }
    }

    // 打印元素
    for (String str : strList) {
        System.out.println(str);
    }
}
```

执行结果：
```
数据1
数据3
```
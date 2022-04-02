# Java类加载的过程（类的生命周期）和双亲委派模型

[官方文档：Chapter 5. Loading, Linking, and Initializing](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-5.html)

[笔记内容参考1：Java类的加载机制和双亲委派模型](http://blog.chinaunix.net/uid-31429544-id-5759997.html)  
[笔记内容参考2：java类加载机制详解](https://www.iteye.com/blog/smallbug-vip-2275284)  
[笔记内容参考3：Java-类加载（类的生命周期）](https://www.cnblogs.com/jhxxb/p/10900405.html)  
[笔记内容参考4：JVM：类加载的过程——解析。](https://blog.csdn.net/en_joker/article/details/79961560)  
[笔记内容参考5：java什么是简单名称、全限定名和描述符。](https://blog.csdn.net/weixin_32482133/article/details/114817547)  
[笔记内容参考6：tomcat类加载器为什么要破坏双亲委派机制？](https://www.cnblogs.com/june0816/p/10090428.html)  
[笔记内容参考7：Tomcat是如何打破双亲委派模型的](https://www.jianshu.com/p/9b2d43c9a09a)  
[笔记内容参考8：聊聊SPI机制以及为什么说SPI破坏了双亲委派模型](https://www.freesion.com/article/38751373091/)  

[toc]

## 一、类加载过程（机制）
>**Java虚拟机把描述类的数据从`Class`文件加载到内存，并对数据进行校验、转换解析和初始化，最终形成可以被虚拟机直接使用的`Java`类型，这就是虚拟机的`加载机制`。**

类从被加载到虚拟机内存中开始，到卸载出内存为止，它的整个生命周期包括了：**加载（Loading）**、**验证（Verification）**、**准备（Preparation）**、**解析（Resolution）**、**初始化（Initialization）**、**使用（using）**、和 **卸载（Unloading）** 七个阶段。  
其中 **验证、准备和解析三个部分统称为连接（Linking）**，这七个阶段的发生顺序如下图所示：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java类加载的过程（类的生命周期）和双亲委派模型/类加载的七个阶段.png)
</center>

其中`加载`、`验证`、`准备`、`初始化`和`卸载`这五个阶段的顺序是确定的，类的加载过程必须按照这个顺序来按部就班地进行；  
**而`解析`阶段则不一定，它在某些情况下可以在`初始化`阶段后再开始，这是为了支持 `Java` 语言的运行时绑定（类的生命周期的每一个阶段通常都是互相交叉混合式进行的，通常会在一个阶段执行的过程中调用或激活另外一个阶段）**。

### 1. 加载
在加载阶段，虚拟机需要完成以下三件事情：
1. 通过一个类的`全限定名称`来 **获取定义此类的二进制字节流**；
2. 将这个`字节流`所代表的`静态存储结构`转化为`方法区`的`运行时数据结构`；
3. 在java`堆`中生成一个代表这个类的`java.lang.Class`对象，作为`方法区`这些数据的 **访问入口** 。

相对于类加载过程的其他阶段，加载阶段是开发期相对来说可控性比较强的阶段，**该阶段既可以使用系统提供的类加载器完成，也可以由用户自定义的类加载器来完成**，开发人员可以通过定义自己的类加载器去控制字节流的获取方式。

**补充1：怎样获取类的二进制字节流，`JVM` 没有限制。除了从编译好的 `.class` 文件中读取，还有以下几种方式：**
* 从 `zip` 包中读取，如 `jar`、`war` 等
* 从网络中获取
* 通过动态代理生成代理类的二进制字节流
* 从数据库中读取
* ............

**补充2： `数组类`本身不通过类加载器创建，由 `JVM` 直接创建，再由`类加载器`创建数组中的元素类。**  
**补充3： `加载`阶段与`连接`（验证、准备、解析）阶段的部分内容交叉进行，但这两个阶段的开始仍然保持先后顺序。**

### 2. 验证
`验证`阶段的作用是保证`Class文件`的`字节流`包含的信息符合`JVM`规范，不会给`JVM`造成危害。  
**如果验证失败，就会抛出一个`java.lang.VerifyError`异常或其子类异常。**

不同的虚拟机对类验证的实现可能会有所不同，但大致都会完成以下四个阶段的验证：**文件格式的验证**、**元数据的验证**、**字节码验证** 和 **符号引用验证**。
* **文件格式的验证：**  
验证字节流是否符合`Class文件`格式的规范，并且能被当前版本的虚拟机处理，该验证的主要目的是保证输入的`字节流`能正确地被解析并存储于`方法区`之内。  
经过该阶段的验证后，`字节流`才会进入内存的`方法区`中进行存储，**后面的三个验证都是基于<font color="red">方法区</font>的存储结构进行的。**
* **元数据验证：**  
对类的`元数据`信息进行`语义校验`（其实就是对类中的各数据类型进行语法校验），保证不存在不符合`Java语法规范`的元数据信息。
* **字节码验证：**  
该阶段验证的主要工作是进行`数据流`和`控制流`分析，对类的方法体进行校验分析，以保证被校验的类的方法在运行时不会做出危害虚拟机安全的行为。
* **符号引用验证：**  
这是最后一个阶段的验证，**它发生在虚拟机将符号引用转化为直接引用的时候（解析阶段中发生该转化，后面会有讲解）**，主要是对类自身以外的信息（常量池中的各种符号引用）进行匹配性的校验。

### 3. 准备
准备阶段是正式为`类变量`（ **含静态成员变量** ）分配内存并设置类变量`初始值`的阶段，这些内存都将在`方法区`中进行分配。

这些`变量`（ **不含实例变量** ）所使用的内存都在`方法区`中进行分配。[官方解释：基本类型初始值（JDK8）](https://docs.oracle.com/javase/specs/jls/se8/html/jls-4.html#jls-4.12.5)
```
对于 byte 类型，默认值为零，即（byte）0。
对于 short 类型，默认值为零，即（short）0。
对于 int 类型，默认值为零，即 0。
对于 long 类型，默认值为零，即 0L。
对于 float 类型，默认值为正零，即 0.0f。
对于 double 类型，默认值为正零，即 0.0d。
对于 char 类型，默认值为空字符，即 '\u0000'。
对于 boolean 类型，默认值为 false。
对于所有引用类型，默认值为 null。
```
**注：**
* 这时候进行内存分配的仅包括`类变量（static）`，而不包括`实例变量（对象属性）`，实例变量会在对象实例化时随着对象一块分配在`Java堆`中。
* 这里所设置的初始值通常情况下是数据类型默认的`零值`（如0、0L、null、false等），而不是被在`Java`代码中被显式地赋予的值。
* 对于`非final`的变量，`JVM`会将其设置成`“零值”`，而不是其赋值语句的值：  
    - **pirvate static int size = 12;** 在这个阶段，`size`的值为`0`，而不是`12`。
* 对于`final`修饰的类变量将会赋值成真实的值：
    - **pirvate final static int size = 12;** 在这个阶段，`size`的值为`12`，而不是`非final`时的`0`。

```java
/**
 * 准备阶段过后的初始值为 0 而不是 123，这时候尚未开始执行任何 Java 方法
 */
public static int value = 123;

/**
 * 同时使用 final 、static 来修饰的变量（常量），并且这个变量的数据类型是基本类型或者 String 类型，就生成 ConstantValue 属性来进行初始化。
 * 没有 final 修饰或者并非基本类型及 String 类型，则选择在 <clinit> 方法中进行初始化。
 * 准备阶段虚拟机会根据 ConstantValue 的设置将 value 赋值为 123
 */
public static final int value = 123;
```

**补充：`ConstantValue`属性**  
* ConstantValue属于属性表集合中的一个属性，属性表集合中一共有`21`个不同属性。
* ConstantValue属性的使用位置：`字段表`；（含义：`final`关键字定义的常量值。）
* ConstantValue属性作用：通知虚拟机自动为静态变量赋值。
```java
int x =123;
static int x = 123;
static final int x = 123;
```

对虚拟机来说上面的变量赋值的方式和时刻都有所不同：
* 非`static`类型变量（实例变量）  
赋值是在实例构造器 **<font color="red">`<init>`</font>** 方法中进行的。
* `static`类型变量（类变量）  
有两种选择：在 **<font color="red">类构造器`<clinit>`方法或者使用ConstantValue属性</font>** 。  
    * 同时使用`final` 、`static`来修饰的变量（常量），并且这个变量的数据类型是基本类型或者`String类型`，就生成 **<font color="red">ConstantValue属性</font>** 来进行初始化；
    * 没有`final`修饰或者并非基本类型及`String类型`，则选择在 **<font color="red">`<clinit>`方法</font>** 中进行初始化。

### 4. 解析
#### 4.1 解析描述（符号引用、直接引用）
解析阶段是虚拟机将常量池内的 **符号引用** 替换为 **直接引用** 的过程。  
会把该类所引用的其他类全部加载进来 **（ 引用方式：继承、实现接口、域变量、方法定义、方法中定义的本地变量）**
* **符号引用（Symbolic Reference）：**  
符号引用以一组符号来描述所引用的目标，可以是任何形式的字面量，与虚拟机实现的内存布局无关，引用的目标并不一定已经在内存中。
* **直接引用（Direct Reference）：**  
    * 可以是直接指向目标的指针、相对偏移量或是一个能间接定位到目标的句柄。  
    * 是与虚拟机实现的内存布局相关的，同一个符号引用在不同的虚拟机实例上翻译出来的直接引用一般都不相同，**如果有了直接引用，那引用的目标必定已经在内存中存在。**

#### 4.2 不同对象的解析（只介绍前四种）
解析动作主要针对以下7类符号引用进行（括号中为各种对应的常量池中的常量类型）  
**类或接口（CONSTANT_Class_info）**  
**字段（CONSTANT_Fieldref_info）**  
**类方法（CONSTANT_Methodref_info）**  
**接口方法（CONSTANT_InterfaceMethodref_info）**  
**方法类型（CONSTANT_MethodType_info）**  
**方法句柄（CONSTANT_MethodHandle_info）**  
**调用点限定符（CONSTANT_InvokeDynamic_info）** 

下面将讲解前面4种引用的解析过程。

##### 4.2.1 类或接口的解析：
**判断所要转化成的直接引用是对于数组类型，还是普通的对象类型的引用，从而进行不同的解析。**

假设当前代码所处的`类为D`，如果要把一个从未解析过的符号`引用N`解析为一个`类或接口C`的`直接引用`，那虚拟机完成整个解析的过程需要以下3个步骤：
1. **如果`C`不是一个数组类型，** 那虚拟机将会把代表`N`的`全限定名`（全限定名：见名词解释一栏）传递给`D`的类加载器去加载这个`类C`。  
在加载过程中，由于元数据验证、字节码验证的需要，又可能触发其他相关类的加载动作（例如加载这个类的父类或实现的接口）。  
    **一旦这个加载过程出现了任何异常，解析过程就宣告失败。** 
2. **如果`C`是一个数组类型，** 并且数组的元素类型为对象，也就是`N`的描述符（描述符：见名词解释一栏）会是类似 **“`[Ljava/lang/Integer`”** 的形式，那将会按照 **第1点** 的规则加载`数组元素类型`。  
如果`N`的描述符如前面所假设的形式，需要加载的元素类型就是 **`java.lang.Integer`** ，接着由虚拟机生成一个代表此数组维度和元素的数组对象。
3. 如果上面的步骤没有出现任何异常，那么`C`在虚拟机中实际上已经成为一个有效的`类或接口`了，但在解析完成之前还要进行符号引用验证，也就是确认`D`是否具备对`C`的访问权限。  
    **如果发现不具备访问权限，将抛出java.lang.IllegalAccessError（无权访问）异常。**

##### 4.2.2 字段解析：
要解析一个未被解析过的字段符号引用，首先将会对字段表内`class_index`项中索引的`CONSTANT_Class_info（类或接口）`符号引用进行解析，也就是字段所属的类或接口的符号引用。  
* 如果在解析这个类或接口符号引用的过程中出现了任何异常，都会导致字段符号引用解析的失败。  
* 如果解析成功，那将这个字段所属的类或接口用`C`表示，虚拟机规范要求按照如下步骤对`C`进行后续字段的搜索：
    1. 如果`C`本身就包含了简单名称和字段描述符都与目标相匹配的字段，则返回这个字段的直接引用，查找结束。
    2. 否则，如果在`C`中实现了接口，将会按照继承关系从下往上递归搜索各个接口和他的父接口，如果接口中包含了简单名称和字段描述符都与目标相匹配的字段，则返回这个字段的直接引用，查找结束。
    3. 否则，如果`C`不是`java.lang.Object`的话，将会按照继承关系从下往上递归搜索其父类，如果在父类中包含了简单名称和字段描述符都与目标相匹配的字段，则返回这个字段直接引用，查找失败。
    4. **否则，查找失败，抛出java.lang.NoSuchFieldError（未找到该字段）异常。**

**注：就算查找过程成功返回了引用，还将会对这个字段进行权限验证，如果发现不具备对字段的访问权限，将抛出`java.lang.IllegalAccessError`异常。**

在实际应用中，虚拟机的编译器实现可能会比上述规范要求的更加严格一些，如果有一个同名字段同时出现在C的`接口`和`父类`中，或者同时在`自己`或`父类`的多个接口中出现，那编译器将可能拒绝编译。  
在下面代码示例中，如果注释了`Sub类`中的 `public static int A=4;` ，接口与父类同时存在`字段A`，那编译器将提示 **The field Sub.A is ambiguous（字段 Sub.A 不明确）**，并且拒绝编译这段代码（编译出错）。
```java
public class FieldResolution {
    interface Interface0 {
        int A = 0;
    }
 
    interface Interface1 extends Interface0 {
        int A = 1;
    }
 
    interface Interface2 {
        int A = 2;
    }
 
    static class Parent implements Interface1 {
        public static int A = 3;
    }
 
    static class Sub extends Parent implements Interface2 {
        public static int A = 4;
    }
 
    public static void main(String[] args) {
        System.out.println(Sub.A);
    }
}
```
编译后，编译器提示：
```
java: 对A的引用不明确
  test.FieldResolution.Parent 中的变量 A 和 test.FieldResolution.Interface2 中的变量 A 都匹配
```

##### 4.2.3 类方法解析：
类方法解析的第一个步骤与字段解析一样，也需要先解析出类方法表的`class_index`项中索引的方法所属的类或接口的符号引用，如果解析成功，我们依然用`C`表示这个类，接下来虚拟机将会按照如下步骤进行后续的类方法搜索：
1. 类方法和接口方法符号引用的常量类型定义是分开的，**如果在类方法表中发现`class_index`中索引的`C`是个`接口`，那就直接抛出`java.lang.IncompatibleClassChangeError`（不兼容的类更改错误）异常**。
2. 如果通过了第1步，在`类C`中查找是否有简单名称和描述符都与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。
3. 否则，在`类C`的父类中递归查找是否有简单名称和描述符都与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。
4. 否则，在`类C`实现的接口列表及他们的父接口之中递归查找是否有简单名称和描述符都与目标相匹配的方法，如果存在匹配的方法，说明`类C`是一个抽象，这时查找结束，抛出`java.lang.AbstractMethodError`异常。
5. **否则，宣告方法查找失败，抛出java.lang.NoSuchMethodError（未找到该字段）。**

**注：和字段解析一样，就算查找过程成功返回了引用，还将会对这个字段进行权限验证，如果发现不具备对字段的访问权限，将抛出`java.lang.IllegalAccessError`异常。**

##### 4.2.4 接口方法解析：
接口方法也需要先解析出接口方法表的`class_index`项中索引的方法所属的类或接口的符号引用，如果解析成功，依然用`C`表示这个接口，接下来虚拟机将会按照如下步骤进行后续的接口方法搜索：
1. 与类方法解析不同，**如果在接口方法表中发现`class_index`中的`索引C`是个类而不是接口，那就直接抛出java.lang.IncompatibleClassChangeError（不兼容的类更改错误）异常**。
2. 否则，在`接口C`中查找是否有简单名称和描述符都与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。
3. 否则，在`接口C`的父接口中递归查找，直到`java.lang.Object`（查找范围会包括Object类）为止，看是否有简单名称和描述符都与目标相匹配的方法，如果有则返回这个方法的直接引用，查找结束。
4. **否则，宣告方法查找失败，抛出java.lang.NoSuchMethodError（未找到该字段）。**

**注：和字段解析、类方法解析不一样的是，由于接口中的所有方法默认都是`public`，所以不存在访问权限的问题，因此接口方法的符号解析应当不会抛出`java.lang.IllegalAccessError`异常。**

#### 附：名词解释
##### 全限定名：
全限定名 = 包名 + 类型，即把类全名中的`"."`替换成了`"/"`；如`Integer`的全限定名就是 **`java/lang/Integer`**

##### 简单名称：
指没有类型和参数修饰的方法或字段名称，比如一个类的`test()`方法，它的简单名称是`test`

##### 描述符：(字段描述符、方法描述符)
* 字段描述符包含`BaseType`（基本数据类型）、`ObjectType`（对象类型）、`ArrayType`（数组类型）三部分
    * 基本数据类型(byte、char、double、float、int、long、short、boolean)都用一个大写字母来表示， **如`double`的描述符为`"D"`** 。
    * 而对象用字符`"L"`加对象的全限定名和来表示， **如`Integer`的描述符为`"Ljava/lang/Integer"`** 。
    * 数组类型描述，每一个维度使用一个前置的`"["`来描述， **如一个定义为`java.lang.String[][]类型`的二维数组，描述符为`"[[Ljava/lang/String"`；一个`double`型三维数组`double[][][]`将被记录为`"[[[D"`** 。
* 方法描述符用来描述方法，一个方法既有参数，又有返回值，那么在用描述符描述方法时，按照 **先参数列表，后返回值的顺序描述** 。参数列表按照参数的严格顺序放在一组小括号`()`内，
    * 有返回值有参数的方法：
    ```java
    // 原方法
    public ReturnDescriptor returnDescriptor(){}
    
    // 对应的方法描述符
    ({ParameterDescriptor}) ReturnDescriptor;    
    ```
    * 如果返回值为`void`，那么就是一个大写字母V表：
    ```java
    // 原方法
    Object m(int i, double d, Thread t) {...}
    
    // 对应的方法描述符
    (IDLjava/lang/Thread;)Ljava/lang/Object;
    ```
    * 如过方法的参数列表和返回值都为空（`void`）:
    ```java
    // 原方法
    void test()
    
    // 对应的方法描述符
    ()V;
    ```

### 5. 初始化
#### 5.1 初始化简述
类初始化阶段是类加载过程的最后一步，前面的类加载过程中，除了加载（`Loading`）阶段用户应用程序可以通过自定义类加载器参与之外，其余动作完全由虚拟机主导和控制。**到了初始化阶段，才真正开始执行类中定义的Java程序代码。**

**初始化阶段就是执行类构造器<font color="red">`<clinit>()`</font>方法的过程。** [官方解释：\<init>()与\<clinit>()介绍](https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-2.html#jvms-2.9)

* **（实例初始化方法）`<init>()`：** 为 `Class 类`实例构造器，对 **非静态变量** 解析初始化。Java编译器会为它的每一个类都至少生成一个实例初始化方法（一个类构造器对应一个）。在`Class`文件中，这个实例化方法被称为`<init>()`方法。
* **（类与接口初始化方法）`<clinit>()`：** 为 `Class 类`构造器 **对静态变量、静态代码块** 进行初始化，通常一个类对应一个，不带参数，且是 `void` 返回。当一个类没有静态语句块，也没有对类变量的赋值操作，那么编译器可以不为这个类生成 `<clinit>()` 方法

#### 5.2 初始化的加载过程
1. `<clinit>()` 方法是由编译器自动收集类中的所有类变量的赋值动作语句和静态块（`static {}`）中的语句合并产生的，编译器收集的顺序由语句在源文件中出现的顺序所决定。  
静态语句块中只能访问定义在静态语句块之前的变量；定义在它之后的变量，在前面的静态语句块中可以赋值，但不能访问。
```java
static {
    i = 0;  // 给后面的变量赋值，可以正常编译通过
    System.out.println(i);  // 使用后面的变量，编译器会提示“非法向前引用”
}
static int i = 1;
```
2. 虚拟机会保证在子类的 `<clinit>()` 方法执行之前，父类的 `<clinit>()` 方法已经执行完毕。  
    * 由于父类的 `<clinit>()` 方法先执行，意味着父类中定义的静态语句块要优先于子类的变量赋值操作。
    ```java
    static class Parent {
        static {
            A = 2;
        }
        public static int A = 1;
    }
    
    static class Sub extends Parent {
        public static int B = A;
    }
    
    public static void main(String[] args) {
        System.out.println(Sub.B);  // 输出 1
    }
    ```

    * 来看一个类属性加载顺序的例子：
    ```java
    public class JvmTest {
    
        public static JvmTest jt = new JvmTest();
    
        public static int a;
        public static int b = 0;
    
        static {
            a++;
            b++;
        }
    
        public JvmTest() {
            a++;
            b++;
        }
    
        public static void main(String[] args) {
            /**
             - 准备阶段：为 jt、a、b 分配内存并赋初始值 jt=null、a=0、b=0
             - 解析阶段：将 jt 指向内存中的地址
             - 初始化：jt 代码位置在最前面，这时候 a=1、b=1
             -          a 没有默认值，不执行，a还是1，b 有默认值，b赋值为0
             -          静态块过后，a=2、b=1
             */
            System.out.println(a);  // 输出 2
            System.out.println(b);  // 输出 1
        }
    }
    ```
3. 关于接口初始化：接口中不能使用静态代码块，但接口也需要通过 `<clinit>() 方法`为接口中定义的静态成员变量显式初始化。 

**接口与类不同，接口的 `<clinit>() 方法`不需要先执行父类的 `<clinit>() 方法`，只有当父接口中定义的变量被使用时，父接口才会初始化。**

#### 5.3 `<clinit>()`方法和`<init>()`方法补充总结
##### `<clinit>()`方法：
* 是由编译器自动收集类中的所有类变量的赋值动作和静态语句块`（static{}块）`中的语句合并产生的，编译器收集的顺序由语句在源文件中出现的顺序所决定。
* 与类的构造函数不同，它不需要显式地调用父类构造器，虚拟机会保证在子类的`<clinit>()`方法执行之前，父类的`<clinit>()`方法已经执行完毕；**因此在虚拟机中第一个执行的`<clinit>()`方法的类一定是`java.lang.Object`。**
* 由于父类的`<clinit>()`方法先执行，也就意味着父类中定义的静态语句块要优先于子类的变量赋值操作。
* `<clinit>()`方法对于类或者接口来说并不是必需的，如果一个类中没有静态语句块也没有对变量的赋值操作，那么编译器可以不为这个类生成`<clinit>()`方法。
* 接口中可能会有变量赋值操作，因此接口也会生成`<clinit>()`方法。但是接口与类不同，执行接口的`<clinit>()`方法不需要先执行父接口的`<clinit>()`方法。只有当父接口中定义的变量被使用时，父接口才会被初始化。另外，接口的实现类在初始化时也不会执行接口的`<clinit>()`方法。
* 虚拟机会保证一个类的`<clinit>()`方法在多线程环境中被正确地加锁和同步。如果有多个线程去同时初始化一个类，那么只会有一个线程去执行这个类的`<clinit>()`方法，其它线程都需要阻塞等待，直到活动线程执行`<clinit>()`方法完毕。**如果在一个类的`<clinit>()`方法中有耗时很长的操作，那么就可能造成多个进程阻塞。**

##### `<init>()`方法：
`<init>()`方法是在一个类进行 **对象实例化** 时调用的。实例化一个类有四种途径：
* 调用 `new` 操作符
* 调用 `Class`或`java.lang.reflect.Constructor`对象的 `newInstance()` 方法
* 调用任何现有对象的 `clone()` 方法
* 通过 `java.io.ObjectInputStream 类` 的`getObject()` 方法反序列化

### 6. 使用
`Class`初始化过程完后就可以被任意调用。

### 7. 卸载
`JVM`中的`Class`只有满足以下三个条件，才能被`GC`回收，也就是该Class被卸载:
* 该类所有的`实例`都已经被`GC`。
* 加载该类的`ClassLoader实例`已经被`GC`。
* 该类的`java.lang.Class`对象没有在任何地方 **被引用** 。

## 二、类加载时机
### 1. 主动引用：
**一个类被主动引用之后会触发初始化过程（加载，验证，准备需再此之前开始）**
1. 遇到 **`new`** 、 **`getstatic`** 、 **`putstatic`** 或 **`invokestatic`** 这4条字节码指令时，如果类没有进行过初始化，则需要先触发其初始化。  
生成这4条指令最常见的Java代码场景是：
    * 使用new关键字实例化对象时；
    * 读取或者设置一个类的静态字段（被final修饰、已在编译器把结果放入常量池的静态字段除外）时；
    * 以及调用一个类的静态方法的时候。
2. 使用 **`java.lang.reflect包`的方法对类进行`反射`调用的时候** ，如果类没有进行过初始化，**则需要先触发其初始化。**
3. 当初始化一个类的时候，如果发现其父类还没有进行过初始化， **则需要触发父类的初始化**。
4. 当虚拟机启动时，用户需要指定一个执行的主类（包含`main()方法`的类），**虚拟机会先初始化这个类**。
5. 当使用`jdk7+`的`动态语言支持`时，如果`java.lang.invoke.MethodHandle实例`最后的解析结果`REF_getStatic`、`REF_putStatic`、`REF_invokeStatic`的`方法句柄`，并且这个`方法句柄`所对应的类没有进行过初始化，**则需要先触发器初始化**。

### 2.被动引用：
**一个类如果是被动引用的话，该类不会触发初始化过程**
1. **通过子类引用父类的静态字段，不会导致子类初始化。**  
对于静态字段，只有直接定义该字段的类才会被初始化，因此当通过子类来引用父类中定义的静态字段时，只会触发父类的初始化，而不会触发子类的初始化：
    ```java
    class SuperClass {
        static {
            System.out.println("SuperClass init!");
        }
        public static int value = 123;
    }
    
    class SubClass extends SuperClass {
        static {
            System.out.println("SubClass init!");
        }
    }
    
    public class NotInitialization {
        public static void main(String[] args) {
            System.out.println(SubClass.value);
            // SuperClass init!
        }
    }
    ```

2. **通过数组定义来引用类，不会触发此类的初始化：**
    ```java
    class SuperClass2 {
        static {
            System.out.println("SuperClass init!");
        }
        public static int value = 123;
    }
    
    public class NotInitialization2 {
        public static void main(String[] args) {
            SuperClass2[] superClasses = new SuperClass2[10];
        }
    }
    ```

3. **常量在编译阶段会存入调用类的常量池中，本质上没有直接引用到定义常量的类，因此不会触发定义常量的类的初始化：**
    ```java
    class SuperClass2 {
        static {
            System.out.println("SuperClass init!");
        }
        public static int value = 123;
    }
    /**
     - 编译通过之后，常量存储到 NotInitialization 类的常量池中，
     - NotInitialization 的 Class 文件中并没有 ConstClass 类的符号引用入口，
     - 这两个类在编译成 Class 之后就没有任何联系了。
     */
    public class NotInitialization2 {
        public static void main(String[] args) {
            SuperClass2[] superClasses = new SuperClass2[10];
        }
    }
    ```

### 3. 关于接口加载
当一个类在初始化时，前提是其父类全部都已经初始化过了；**但是一个接口在初始化时，并不要求其父接口全部都完成了初始化，当真正用到父接口的时候才会初始化。**

## 三、双亲委派模型
> ps：双亲委派（`parents delegate`）的 **“双亲”** 并非中文意义的父母，而是翻译成中文的说法，本意指父辈（如`继承`和`实现`）。

**类加载器的双亲委派模型在`JDK1.2` 期间被引入并被广泛应用于之后的所有Java程序中，但他并不是个<font color="red">强制性的约束模型</font>，而是Java设计者推荐给开发者的一种类加载器实现方式。**

### 1. 类型加载器分类
#### 1.1 JVM预定义的三种类型类加载器
1. **启动（`Bootstrap`）类加载器：** 是用本地代码实现的类装入器（HotSpot虚拟机中），是虚拟机自身的一部分，它负责将 `<Java_Runtime_Home>/lib`下面的类库加载到内存中（比如`rt.jar`）。  
    由于引导类加载器涉及到虚拟机本地实现细节，开发者无法直接获取到启动类加载器的引用，**所以不允许直接通过引用进行操作**。
2. **标准扩展（`Extension`）类加载器：** 是由 Sun 的 `ExtClassLoader（sun.misc.Launcher$ExtClassLoader）`实现的。它负责将`<Java_Runtime_Home >/lib/ext`或者由系统变量 `java.ext.dir`指定位置中的类库加载到内存中。**开发者可以直接使用标准扩展类加载器。**
3. **系统（`System`）类加载器：** 是由 `Sun` 的 `AppClassLoader（sun.misc.Launcher$AppClassLoader）`实现的。它负责将系统类路径（`CLASSPATH`）中指定的类库加载到内存中。**开发者可以直接使用系统类加载器。**

#### 1.2 从开发者的角度，类加载器可以细分为
1. **启动（`Bootstrap`）类加载器：**   
负责将 `Java_Home/lib`下面的类库加载到内存中（比如rt.jar）。由于引导类加载器涉及到虚拟机本地实现细节，开发者无法直接获取到启动类加载器的引用，所以不允许直接通过引用进行操作。
2. **标准扩展（`Extension`）类加载器：**   
是由 Sun 的 `ExtClassLoader（sun.misc.Launcher$ExtClassLoader）`实现的。它负责将`Java_Home/lib/ext`或者由系统变量 `java.ext.dir`指定位置中的类库加载到内存中。 开发者可以直接使用标准扩展类加载器。
3. **应用程序（`Application`）类加载器：**   
是由 Sun 的 `AppClassLoader（sun.misc.Launcher$AppClassLoader）`实现的。它负责将系统类路径（`CLASSPATH`）中指定的类库加载到内存中。  
由于这个类加载器是`ClassLoader`中的`getSystemClassLoader()方`法的返回值，因此一般称为系统（`System`）加载器。开发者可以直接使用系统类加载器。
4. **自定义(`Custom ClassLoader`)类加载器：**  
应用程序根据自身需要自定义的`ClassLoader`，如`tomcat`、`jboss`都会根据j2ee规范自行实现`ClassLoader`加载过程中会先检查类是否被已加载，检查顺序是自底向上，从`Custom ClassLoader`到`BootStrap ClassLoader`逐层检查，只要某个`classloader`已加载就视为已加载此类，保证此类只所有`ClassLoader`加载一次。而加载的顺序是自顶向下，也就是由上层来逐层尝试加载此类。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java类加载的过程（类的生命周期）和双亲委派模型/类型加载器分类.png)
</center>

### 2. 双亲委派模型描述
#### 简述
**启动、标准扩展、应用程序和自定义类加载器，它们之间的层次关系被称为类加载器的双亲委派模型。**

该模型要求除了顶层的`启动类加载器（ **Bootstrap ClassLoader** ）`外，其余的类加载器都应该有自己的父类加载器，而这种父子关系一般通过`组合（Composition）关系`来实现，而不是通过`继承（Inheritance）`。

某个特定的类加载器在接到加载类的请求时，首先将加载任务委托给父类加载器，依次递归，如果父类加载器可以完成类加载任务，就成功返回；只有父类加载器无法完成此加载任务时，才自己去加载。

#### 为何采用双亲委派机制（好处）
首先明确一点：`jvm`如何认定两个对象同属于一个类型？必须同时满足下面两个条件：
* 都是用同名的类完成实例化的。
* 两个实例各自对应的同名的类的`加载器`必须是同一个。  
如：两个相同名字的类，一个是**用系统加载器加载的**，一个**扩展类加载器加载的**，两个类生成的对象将被jvm认定为不同类型的对象。

**避免重复加载 + 避免核心类篡改（保证JDK核心类的优先加载）**  
* 采用`双亲委派模式`的是好处是Java类随着它的类加载器一起具备了一种带有`优先级的层次关系`，通过这种层级关可以避免类的**重复加载**，当父亲已经加载了该类时，就没有必要`子ClassLoader`再加载一次。  
* 其次是考虑到安全因素，java核心`api`中定义类型不会被随意替换，假设通过网络传递一个名为`java.lang.Integer`的类，通过`双亲委托模式`传递到启动类加载器，而启动类加载器在核心Java
API发现这个名字的类，发现该类已被加载，并不会重新加载网络传递的过来的`java.lang.Integer`，而直接返回已加载过的`Integer.class`，**这样便可以防止核心`API库`被随意篡改。**

**因此，如果开发者尝试编写一个与`rt.jar`类库中重名的Java类，可以正常编译，但是永远无法被加载运行。**

#### 补充1：jdk的`ClassLoader.loadClass()`方法
**该方法的方法注释（执行过程/原理）：**  
* 使用指定的二进制名称来加载类，这个方法的默认实现按照以下顺序查找类：
    * 调用`findLoadedClass(String)`方法检查这个类是否被加载过
    * 使用父加载器调用`loadClass(String)`方法，如果父加载器为`Null`，类加载器装载虚拟机内置的加载器调用`findClass(String)`方法装载类，
    * 如果，按照以上的步骤成功的找到对应的类，并且该方法接收的`resolve`参数的值为true,那么就调用`resolveClass(Class)`方法来处理类。
    * `ClassLoader`的子类最好覆盖`findClass(String)`而不是这个方法。
* **除非被重写，这个方法默认在整个装载过程中都是同步的（线程安全的）。**

`java.lang.ClassLoader.loadClass()`方法源码：
```java
protected Class<?> loadClass(String name, boolean resolve)
    throws ClassNotFoundException
{
    synchronized (getClassLoadingLock(name)) {
        // First, check if the class has already been loaded
        //检查类是否被当前加载器加载过
        Class<?> c = findLoadedClass(name);
        //没有加载过
        if (c == null) {
            long t0 = System.nanoTime();
            try {
                //有上级对象嘛
                if (parent != null) {
                    //如果有上级对象,让上级对象尝试加载,上级对象还是这个方法，递归的,逻辑一样
                    c = parent.loadClass(name, false);
                } else {
                    //没有上级对象,自己加载吧
                    c = findBootstrapClassOrNull(name);
                }
            } catch (ClassNotFoundException e) {
                // ClassNotFoundException thrown if class not found
                // from the non-null parent class loader
            }
            
            //还是没有，那就抛ClassNotFound异常
            if (c == null) {
                // If still not found, then invoke findClass in order
                // to find the class.
                long t1 = System.nanoTime();
                c = findClass(name);

                // this is the defining class loader; record the stats
                sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                sun.misc.PerfCounter.getFindClasses().increment();
            }
        }
        if (resolve) {
            resolveClass(c);
        }
        //加载好了，返回
        return c;
    }
}
```

**可以看出`jdk`自带的`ClassLoader`的实现是完全符合双亲委派模型的。**

**可以继承`java.lang.ClassLoader`类，实现自己的类加载器。**
* 如果想`保持`双亲委派模型，就应该重写<font color="red">`findClass(name)`</font>方法；
* 如果想`破坏`双亲委派模型，可以重写<font color="red">`loadClass(name)`</font>方法。

#### 补充2：父类委托机制(全盘负责委托机制)
**全盘负责委托机制：** 是指当一个`ClassLoader`装载一个类时，除非显示地使用另一个`ClassLoader`，则该类所依赖及引用的类也由这个`CladdLoader`载入（即：如果A类调用了B类,则B类由A类的加载器进行加载）。
* **全盘负责：** 即是当一个`classloader`加载一个Class的时候，这个Class所依赖的和引用的其它Class通常也由这个`classloader`负责载入。
* **委托机制：** 先让`parent（父）类加载器` 寻找，只有在`parent`找不到的时候才从自己的类路径中去寻找。

如：`系统类加载器AppClassLoader`加载入口类（含有`main()`方法的类）时，会把`main()`方法所依赖的类及引用的类也载入，依此类推。**“全盘负责委托机制”也可称为当前类加载器负责机制。** 显然，入口类所依赖的类及引用的类的当前类加载器就是入口类的类加载器。

**以上步骤只是调用了`ClassLoader.loadClass(name)`方法，并没有真正定义类。真正加载`class字节码文件`生成`Class对象`由“双亲委派”机制完成。**

**全盘负责委托机制为什么可以保证一个类只被加载一次：**  
类加载采用了`cache机制`：如果 `cache`中保存了这个`Class`就直接返回它，如果没有才从文件中读取和转换成`Class`，并存入`cache`；  
这就是为什么修改了`Class`但是必须重新启动`JVM`才能生效，并且类只加载一次的原因。

## 四、打破双亲委派模型
### 1. 如何打破？  
因为加载class核心的方法在`LoaderClass类`的`loadClass方法`上**（双亲委派机制的核心实现），**
那么自定义个`ClassLoader`（继承`java.lang.ClassLoader类`），重写`loadClass方法`（不依照往上开始寻找类加载器），那就算是打破双亲委派机制了。

**即：只要加载类的时候，不是从`APPClassLoader（应用程序类加载器）`--->`Ext ClassLoader（标准扩展类加载器）`--->`BootStrap ClassLoader（启动类加载器）` 这个顺序找，那就算是打破了**

### 2. tomcat加载是如何打破双亲委派模型的
#### 2.1 Tomcat为什么不能使用默认的类加载机制（为什么打破双亲委派模型）
1. 一个web容器可能需要部署两个应用程序，**不同的应用程序可能会依赖同一个第三方类库的不同版本，** 不能要求同一个类库在同一个服务器只有一份，因此要保证每个应用程序的类库都是独立的，保证相互隔离。
2. 部署在同一个web容器中相同的类库相同的版本可以共享。否则，如果服务器有10个应用程序，那么要有10份相同的类库加载进虚拟机，这是不可能的。
3. web容器也有自己依赖的类库，不能于应用程序的类库混淆。基于安全考虑，应该让容器的类库和程序的类库隔离开来。
4. web容器要支持`jsp`的热部署。`jsp 文件`最终也是要编译成`class文件`才能在虚拟机中运行，但程序运行后修改`jsp`后需要支持`jsp` 修改后不用重启。

#### 2.2 Tomcat 如何实现自己独特的类加载机制？
##### 2.2.1 Tomcat自定义的类加载器
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java类加载的过程（类的生命周期）和双亲委派模型/Tomcat自定义的类加载器.png)  
`Tomcat加载器架构图`
</center>

* **`CommonLoader：`** Tomcat最基本的类加载器，加载路径中的class可以被Tomcat容器本身以及各个Webapp访问；
* **`CommonClassLoader：`** tomcat私有的类加载器，webapp不能访问其加载路径下的class，即对webapp不可见
* **`SharedClassLoader：`** 各个Webapp共享的类加载器，加载路径中的class对于所有Webapp可见，但是对于Tomcat容器不可见；
* **`WebappClassLoader：`** 各个Webapp私有的类加载器，加载路径中的class只对当前Webapp可见；
* **`JasperLoader（Jsp类加载器）：`** 每一个web应用程序对应一个WebappClassLoader，每一个jsp文件对应一个JspClassLoader，所以这两个类加载器有多个实例

**补充：多个应用共享的Java类文件和JAR包，分别放在Web容器指定的共享目录（与加载器相对应）**  
```
// 可以在Tomcat/conf目录下的Catalina.properties文件里配置各种类加载器的加载路径。
CommonClassLoader 对应 <Tomcat>/common/*
CatalinaClassLoader 对应 <Tomcat >/server/*
SharedClassLoader 对应 <Tomcat >/shared/*  
WebAppClassloader 对应 <Tomcat >/webapps/<app>/WEB-INF/*
```
默认情况下，`conf目录`下的 **`catalina.properties文件`** 没有指定 **`server.loader`** 以及 **`shared.loader`** ，所以tomcat没有建立`CatalinaClassLoader`和`SharedClassLoader`的实例，这两个都会使用`CommonClassLoader`来代替。  
**Tomcat6之后，把common、shared、server目录合成了一个lib目录。所以在新版本的服务器里看不到common、shared、server目录。**

##### 2.2.2 工作原理
1. `CommonClassLoader`能加载的类都可以被`Catalina ClassLoader`和`SharedClassLoader`使用，**从而实现了公有类库的共用**。
2. `CatalinaClassLoader`和`Shared ClassLoader`自己能加载的类则与对方相互隔离。
3. `WebAppClassLoader`可以使用SharedClassLoader加载到的类，但各个`WebAppClassLoader`实例之间相互隔离。
4. `JasperLoader`的加载范围仅仅是这个`JSP文件`所编译出来的那一个`.Class文件`，它出现的目的就是为了被丢弃：  
    当Web容器检测到`JSP文件`被修改时，会替换掉目前的`JasperLoader`的实例，并通过再建立一个新的Jsp类加载器来**实现`JSP文件`的HotSwap功能。 （JSP热部署原理）**

**Tomcat 为了实现隔离性，没有遵守双亲委派模型，每个`WebAppClassLoader`加载自己的目录下的`class文件`，不会传递给父类加载器。**


#### 2.3 总结
`Tomcat`的`Context组件`为每个Web应用创建一个`WebAppClassLoader类加载器`，由于**不同类加载器实例加载的类是互相隔离的**，因此达到了隔离Web应用的目的，同时通过`CommonClassLoader`等父加载器来共享第三方JAR包。

而共享的第三方JAR包怎么加载特定Web应用的类呢？可以通过设置 **线程上下文加载器** 来解决。
> 线程上下文加载器在后文分析（四-->3-->3.6 双亲委派模型的妥协（线程上下文类加载器：Thread Context ClassLoader））

#### 2.4 延伸思考: jsp如何实现热部署？
**tomcat自定义的类加载器中, 还有一个jsp类加载器：jsp是可以实现热部署的, 那么他是如何实现的呢?**  
我们都知道`Jsp文件`其实是一个`servlet容器`, tomcat会为每一个jsp生成一个类加载器，这样每个类加载器都加载自己的jsp；  
当`Jsp文件`内容修改时, tomcat会有一个监听程序来监听jsp的改动用来监听不同文件夹中文件的内容是否修改, **查看文件夹的updateTime（修改时间）有没有变化, 如果有变化了, 那么就会重新加载。**

### 3. 为什么说JDBC破坏了双亲委派机制?
双亲委派模型让我们加载基础类的时候都是同一个基础类，但我们有时候可能需要在 **基础类中回调用户代码** 怎么办呢？

如：Java提供了很多 **<font color="red">服务提供者接口（SPI，Service Provider Interface）</font>** ，允许独立厂商（第三方）为此提供实现。  
**其中常见的SPI有**：`JNDI`、`JDBC`、`JAXP`等。这些 **接口** 由Java的核心库来提供。

`SPI`的接口是Java核心库的一部分，它们是由启动类加载器来加载的。`SPI`实现的Java类一般是由应用`程序类加载器（Application ClassLoader）`来加载的。  
启动类无法找到`SPI`的实现类，**因为它只加载核心库（SPI的实现类由第三方提供）。** 它也不能代理给`应用程序类加载器（Application ClassLoader）`，因为**它又是应用程序类加载器的父类**，双亲委派模型又会将它交给`启动类`来加载。

**所以在这个时候就要“打破”这个“双亲委派模型”。**

#### 3.1 SPI的概念
**`SPI（Service Provider Interface）`，是JDK内置的一种`服务提供发现机制`，可以用来启用框架`扩展`和`替换`组件，主要是被框架的开发人员使用。**

#### 3.2 SPI典型应用：JDBC
`java.sql.Driver接口`由核心类库提供，但是它的实现很明显不是Java提供的，而是各大服务商来提供。

当服务的提供者提供了一种接口的实现之后，需要在`classpath`下的`META-INF/services/目录`里创建一个以服务接口命名的文件，这个文件里的内容就是这个接口的具体的实现类。

**JDK中查找服务的实现的工具类是：`java.util.ServiceLoader`。**

那为什么配置文件为什么要放在`META-INF/services`下面？可以打开`ServiceLoader`的代码，里面定义了文件的PREFIX如下：
```java
public final class ServiceLoader<S>
    implements Iterable<S>
{

    private static final String PREFIX = "META-INF/services/";
    ..........................
}
```
而我们在引入的jar包里也确实能找到这个东西：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java类加载的过程（类的生命周期）和双亲委派模型/mysql-spi文件地址.png)
</center>

点开这个文件可以看到实现的类和类的路径：
```yml
com.mysql.cj.jdbc.Driver
```
点进 **`com.mysql.cj.jdbc.Driver`** 类可以看到对 **`java.sql.Driver`** 的实现：
```java
package com.mysql.cj.jdbc;

import java.sql.SQLException;
public class Driver extends NonRegisteringDriver implements java.sql.Driver {
    //
    // Register ourselves with the DriverManager
    //
    static {
        try {
            java.sql.DriverManager.registerDriver(new Driver());
        } catch (SQLException E) {
            throw new RuntimeException("Can't register driver!");
        }
    }

    /**
     * Construct a new driver and register it with DriverManager
     * 
     * @throws SQLException
     *             if a database error occurs.
     */
    public Driver() throws SQLException {
        // Required for Class.forName().newInstance()
    }
}
```

#### 3.3 SPI机制的通俗理解
到这里对`SPI机制`已经有了一个大概的了解，实际上它可以理解为一个 **<font color="red">规范</font>** 。

举个通俗一点的例子：我有一台手机，需要打电话但是没得卡怎么办？总不可能我做手机的还得负责把你电话卡问题也解决吧？那后面岂不是还有手机壳、耳机等问题？

很明显`手机开发商（JDK）`不会给你一条龙服务，它在出厂的时候定义好`卡槽大小（接口定义）`，不管你是移动还是联通还是电信，只要你根据我的`规范设计好电话卡（接口实现）`，那我直接放进去手机就能使用。

#### 3.4 加载器可见性原则
我们都知道，Java的类加载器结构是这样的：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java类加载的过程（类的生命周期）和双亲委派模型/类型加载器分类.png)
</center>

`启动类加载器`作为应用程序类加载器的上级，`启动类加载器`加载的类 对`应用程序类加载器`是可见的。然而`应用程序类加载器`加载的类对`启动类加载器`却是不可见的，以此类推。

**这是由 `classloader` 加载模型中的`可见性(visibility)`决定的。** 可见性原则允许子类加载器查看父ClassLoader加载的所有类，但父类加载器看不到子类加载器的类。

#### 3.5 为什么说SPI破坏了双亲委派模型
`双亲委派模型`很好的解决了各个类记载器的基础类统一问题（越基础的类由越上层的类加载器加载）。

基础类之所以称为基础，是因为它们总是作为被用户调用的`API`，**而不能反过来调由API调用用户的代码。**  
但如果基础类又要回调用户的代码，那该怎么办呢？

#### 3.6 双亲委派模型的妥协（线程上下文类加载器：Thread Context ClassLoader）：
先看看·的`DriverManager`实现**（管理一组 JDBC 驱动程序的基本服务）**的部分源码：
```java
public class DriverManager {
    .......................
    .......................
    
    /**
     * Load the initial JDBC drivers by checking the System property
     * jdbc.properties and then use the {@code ServiceLoader} mechanism
     *
     * 在加载java.sql.DriverManager类的时候，会执行静态块：
     * 通过检查系统属性 jdbc.properties 加载初始 JDBC 驱动程序
     */
    static {
        loadInitialDrivers();
        println("JDBC DriverManager initialized");
    }

    .......................
    .......................
    
    /**
     * 加载的静态代码实现
     */
    private static void loadInitialDrivers() {
        .......................
        .......................
        
        AccessController.doPrivileged(new PrivilegedAction<Void>() {
            public Void run() {
                ServiceLoader<Driver> loadedDrivers = ServiceLoader.load(Driver.class);
                Iterator<Driver> driversIterator = loadedDrivers.iterator();
    
                try{
                    while(driversIterator.hasNext()) {
                        driversIterator.next();
                    }
                } catch(Throwable t) {
                // Do nothing
                }
                return null;
            }
        });

        .......................
        .......................
        
    }
    .......................
    .......................
    
}
```
继续看 `ServiceLoader.load(Driver.class);` 的代码：
```java
public final class ServiceLoader<S>
    implements Iterable<S>
{
    
    .......................
    .......................
    
    private ServiceLoader(Class<S> svc, ClassLoader cl) {
        service = Objects.requireNonNull(svc, "Service interface cannot be null");
        loader = (cl == null) ? ClassLoader.getSystemClassLoader() : cl;
        acc = (System.getSecurityManager() != null) ? AccessController.getContext() : null;
        reload();
    }
    
    .......................
    .......................
    
    public static <S> ServiceLoader<S> load(Class<S> service,
                                            ClassLoader loader)
    {
        return new ServiceLoader<>(service, loader);
    }
    .......................
    .......................
    
    public static <S> ServiceLoader<S> load(Class<S> service) {
        ClassLoader cl = Thread.currentThread().getContextClassLoader();
        return ServiceLoader.load(service, cl);
    }
    
    .......................
    .......................
```
可以看到`ServiceLoader.load(Driver.class);`方法依次调用了`public static <S> ServiceLoader<S> load(Class<S> service,
                                            ClassLoader loader)` 到 `private ServiceLoader(Class<S> svc, ClassLoader cl)`；  
                                            
其中`private ServiceLoader(Class<S> svc, ClassLoader cl)；`中有一段代码:
```java
loader = (cl == null) ? ClassLoader.getSystemClassLoader() : cl;
```
**表示：如果前面没有用线程上下文加载器(cl)，那么这里默认使用的是调用方的类加载器（ClassLoader.getSystemClassLoader()）**

上述源码分析， **`java.sql.DriverManager`** 通过扫包的方式拿到指定的实现类，完成 `DriverManager`的**初始化**。

但是，根据可见性原则，`java.sql.DriverManager`是`启动类加载器`负责的，根据**双亲委派的可见性原则**，启动类加载器加载的 `DriverManager` 是不可能拿到`系统应用类加载器`加载的实现类 。

为了解决这个困境，Java的引入了一个不太优雅的设计：**线程上下文类加载器（`Thread Context ClassLoader`）。**  
`Thread类`中有 `getContextClassLoader()` 和 `setContextClassLoader(ClassLoader cl)` 方法用来获取和设置上下文类加载器：
* 如果没有 `setContextClassLoader(ClassLoader cl)` 方法通过设置类加载器，那么线程将继承父线程的上下文类加载器，
* 如果在应用程序的全局范围内都没有设置的话，那么这个上下文类加载器默认就是`应用程序类加载器（Application ClassLoader）`。

**换句话说Java默认的线程上下文类加载器就是`应用程序类加载器(AppClassLoader)。`** 通过线程上下文来加载第三方库`jndi`实现，而不依赖于`双亲委派`。大部分`Java Application服务器（jboss, tomcat..）`也是采用`contextClassLoader`来处理web服务（所以理解线程上下文类加载器，更能让我们理解Tomcat等服务器的实现原理、工作方式）。

**通过这个类加载器可以实现功能，但也正是因为如此，双亲委派模型的可见性原则就被<font color="red">破坏</font>了，但这也是无可奈何的事情，所以只能说是妥协~**

#### 3.7 Java SPI 缺点总结
`Java SPI`的使用很简单。也做到了基本的加载扩展点的功能。但`Java SPI`有以下的不足:
* 需要遍历所有的实现，并实例化，然后在循环中才能找到需要的实现；
* 配置文件中只是简单的列出了所有的扩展实现，而没有给他们命名。导致在程序中很难去准确的引用它们；
* 扩展如果依赖其他的扩展，做不到自动注入和装配；
* 不提供类似于`Spring`的`IOC`和`AOP`功能；
* 扩展很难和其他的框架集成，比如扩展里面依赖了一个`Spring bean`，原生的`Java SPI`不支持。
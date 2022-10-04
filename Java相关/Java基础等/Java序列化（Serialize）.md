# Java序列化

[文档内容参考1：序列化理解起来很简单](https://zhuanlan.zhihu.com/p/40462507)
[文档内容参考2：Java序列化的机制和原理](https://www.51cto.com/article/147650.html)

[toc]

## 一、序列化概念
### 1. 概述
- **序列化：** 把对象转化为可传输的字节序列过程。
- **反序列化：** 把字节序列还原为对象的过程。

### 2. 为什么要序列化？
序列化的目的是为了对象可以 **跨平台存储、进行网络传输** 。而进行跨平台存储和网络传输的方式就是`IO`，而`IO`支持的数据格式就是字节数组。

如果只单方面的把对象转成字节数组还不行，因为没有规则的字节数组是没办法把对象的本来面目还原回来的，所以必须在 **把对象转成字节数组的时候就制定一种规则（`序列化`）** ，那么 **从IO流里面读出数据的时候再以这种规则把对象还原回来（`反序列化`）。**

如果要把一栋房子从一个地方运输到另一个地方去，**序列化** 就是把房子拆成一个个的砖块放到车子里，然后留下一张房子原来结构的图纸， **反序列化** 就是把房子运输到了目的地以后，根据图纸把一块块砖头还原成房子原来面目的过程。

### 3. 什么情况下需要序列化？
凡是需要进行`“跨平台存储”`和`“网络传输”`的数据，都需要进行序列化。  
本质上存储和网络传输都需要把一个对象状态保存成一种跨平台识别的字节格式，然后其他的平台才可以通过字节信息解析还原对象信息。

场景：当只在本地`JVM`里运行下`Java`实例，这个时候是不需要什么序列化和反序列化的, 但当需要将内存中的对象持久化到磁盘、数据库中时、需要与浏览器进行交互时、当需要实现RPC时，这个时候就需要`序列化`和`反序列化`了。

### 4. 序列化的方式
**序列化只是一种拆装组装对象的规则** ，那么这种规则肯定也可能有多种多样，比如现在常见的序列化方式有：
- JDK（不支持跨语言）
- Kryo（不支持跨语言）
- FST（不支持跨语言）
- Hessian
- JSON
- XML
- Thrift
- Protostuff

### 5. 序列化技术选型的几个关键点
序列化协议各有千秋，不能简单的说一种序列化协议是最好的，只能从当前开发环境下去选择最适合的序列化协议，如果要为项目进行序列化技术的选型，那么主要从以下几个因素：
- **协议是否支持跨平台**  
  如果有多种语言进行混合开发，那么就肯定不适合用有语言局限性的序列化协议；比如JDK序列化出来的格式，其他语言就不支持。
- **序列化的速度**  
  如果序列化的频率非常高，那么选择序列化速度快的协议会为系统性能提升不少。
- **序列化出来的大小**  
  如果频繁的在网络中传输的数据那就需要数据越小越好，小的数据传输快，也不占用太多带宽，也能提升系统整体的性能。

## 二、Java中的序列化
### 1. Java 是如何实现序列化的？
前面主要介绍了一下什么是序列化，那么下面主要讲下JAVA是如何进行序列化的，以及序列化的过程中需要注意的一些问题。

**`Java`实现序列化很简单，只需要实现`Serializable`接口即可**
```java
public class User implements Serializable{
    // 年龄
    private int age;
    // 名字
    private String name ;

    // 省略get set toString
}
```

测试类：
```java
public class SerializableTest {
    public static void main(String[] args) throws Exception {
        write();
        read();
    }

    /**
     * 把User对象赋值后写入文件
     * @throws Exception
     */
    public static void write() throws Exception {
        FileOutputStream fos = new FileOutputStream("D:\\temp.txt");
        ObjectOutputStream oos = new ObjectOutputStream(fos);

        User user = new User();
        user.setAge(18);
        user.setName("sandy");
        oos.writeObject(user);

        oos.flush();
        oos.close();
        System.out.println("序列化前的User对象："+  user);
    }

    /**
     * 把从文件读取出来的转换为对象
     * @throws Exception
     */
    public static void read() throws Exception {
        FileInputStream fis = new FileInputStream("D:\\temp.txt");
        ObjectInputStream oin = new ObjectInputStream(fis);
        User user = (User) oin.readObject();

        System.out.println("反序列化后的User对象："+  user);
    }
}
```

运行结果：
```
序列化前的User对象：User{age=18, name='sandy'}
反序列化后的User对象：User{age=18, name='sandy'}
```

如果`User类`不实现`Serializable接口`，运行上面的代码将会报错（ **提示User类未序列化** ）：
```
Exception in thread "main" java.io.NotSerializableException: com.demo.User
	at java.io.ObjectOutputStream.writeObject0(ObjectOutputStream.java:1184)
	at java.io.ObjectOutputStream.writeObject(ObjectOutputStream.java:348)
	at com.demo.SerializableTest.write(SerializableTest.java:21)
	at com.demo.SerializableTest.main(SerializableTest.java:10)
```
以上示例代码把`User对象`进行二进制的数据存储后，再从文件中读取数据出来转成`User对象`就是一个序列化和反序列化的过程。

### 2. Java序列化中常见的问题
#### 2.1 序列化版本号serialVersionUID
所有实现序列化的对象都必须要有个 **版本号** ，这个 **版本号** 可以由自己定义，当没定义的时候`JVM`会按照对象的属性生成一个对应的 **版本号** 。

**版本号有什么用？**  
其实这个版本号就和平常软件的版本号一样，当你的软件版本号和官方的服务器版本不一致的话就告诉你有新的功能更新了，主要用于提示用户进行更新。   
序列化也一样，我们的对象通常需要根据业务的需求变化要`新增`、`修改`或者`删除`一些属性，在做了一些修改后，就通过修改版本号告诉 反序列化的那一方对象有了修改你需要同步修改。

**使用JDK生成的版本号和自定义的版本号的区别？**  
`JDK`工具生成的 `serialVersionUID` 是根据对象的属性信息生成的一个编号，这就意味着只要对象的属性有一点变动那么对象对应的序列化版本号就会同步进行改变。  
这种版本号随着对象同步改变的情况有时候就不太友好，就像我们的软件一样，只要软件版本有一点改变，就必须强制更新软件，否则用户就不能使用软件。  
而期望的大多数友好情况也许是用户可以选择不更新，不更新的话用户只是无法体验新加的功能而已。

而这种方式就需要我们自定义的版本号了，这样就可以在改变或新增了对象属性后而不修改serialVersionUID，反序列化的时候只是无法获取修改的属性，而并不影响程序运行。

下面用代码测试一下：

##### （1）版本号不同进行序列化和反序列化
序列化之前设置`serialVersionUID = 1L`
```java
public class User implements Serializable{
    private static final long serialVersionUID = 1L;
    
    // 年龄
    private int age;
    // 名字
    private String name ;

    // 省略get set toString
}
```

先执行上面的`序列化方法（write）`将`User对象`存储到`temp.txt`中  
然后再反序列化之前设置`User对象`的`serialVersionUID = 2L`
```java
public class User implements Serializable{
    private static final long serialVersionUID = 2L;
    // ....
}
```

最后执行上面的`反序列化方法（read）`将`User对象`取出来，运行结果：
```
Exception in thread "main" java.io.InvalidClassException: com.demo.User; local class incompatible: stream classdesc serialVersionUID = 3816644476858169709, local class serialVersionUID = -109473675332593012
	at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
	at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:1885)
	at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1751)
	at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2042)
	at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1573)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:431)
	at com.demo.SerializableTest.read(SerializableTest.java:39)
	at com.demo.SerializableTest.main(SerializableTest.java:11)
```
最后执行结果反序列化异常，原因是对象序列化和反序列化的版本号不同导致，将`serialVersionUID`设置为`1L`就可以正常反序列化了。

##### （2）对象新增属性，版本号相同
序列化的对象信息 这里比反序列化的对象多了个`sex属性`，此时`serialVersionUID`依旧是`1L`：
```java
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    // 年龄
    private int age;
    // 名字
    private String name;
    // 性别
    private String sex;
    
    // 省略get set toString
}
```

再执行`反序列化方法（read）`将`User对象`取出来（此时`temp.txt`中存放的`User对象`是没有`sex属性`的），运行结果如下：
```
反序列化后的User对象：User{age=18, name='sandy', sex='null'}
```
结果证明，只要序列化版本一样，对象新增属性并不会影响反序列化对象。

##### （3）对象新增属性，版本号使用的JDK生成
修改`User对象`：
```java
public class User implements Serializable {
    // 注释掉自定义的serialVersionUID，使用jvm自动生成
    // private static final long serialVersionUID = 1L;
    
    // 年龄
    private int age;
    // 名字
    private String name;
    // 性别
    private String sex;
    
    // 省略get set toString
}
```

再执行`反序列化方法（read）`，运行结果：
```
Exception in thread "main" java.io.InvalidClassException: com.demo.User; local class incompatible: stream classdesc serialVersionUID = 3816644476858169709, local class serialVersionUID = -109473675332593012
	at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
	at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:1885)
	at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1751)
	at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2042)
	at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1573)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:431)
	at com.demo.SerializableTest.read(SerializableTest.java:39)
	at com.demo.SerializableTest.main(SerializableTest.java:11)
```
结果报错，原因是序列化和反序列化的 **serialVersionUID版本号** 不一致造成。

#### 2.2 static 属性不能被序列化
把`User`中的`name属性`改为`static`修饰：
```java
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    // 年龄
    private int age;
    // 名字
    private static String name;

    // 省略get set toString
}
```

运行上面的测试程序，运行结果如下：
```
序列化前的User对象：User{age=18, name='sandy'}
反序列化后的User对象：User{age=18, name='sandy'}
```

**为什么`static`还是被成功序列化了呢？**  
因为测试类的`main方法`的原因，把`序列化方法（write）`和`反序列方法（read）`都放在一个程序中执行，由于被`static`修饰的变量在类刚被加载时，就存放方法区且 **被其他对象或方法所共享** ，因此反序列化执行之后打印的`name='sandy'`其实并不是反序列化的结果，而是直接取的方法区中已有的静态变量。

验证：由于`序列化方法（write）`执行成功，接下来在`main`中只执行`反序列方法（read）`
```java
public class SerializableTest {
    public static void main(String[] args) throws Exception {
        // write();
        read();
    }
    // .......
}
```

运行结果：
```java
反序列化后的User对象：User{age=18, name='null'}
```

**`static`属性为什么不会被序列化？**  
因为序列化是针对对象而言的，而`static属性`优先于对象存在，随着类的加载而加载，所以不会被序列化。

**但是`serialVersionUID`也被`static`修饰，为什么`serialVersionUID`会被序列化？**  
其实`serialVersionUID`属性并没有被序列化，`JVM`在序列化对象时会自动生成一个`serialVersionUID`，然后将显示指定的`serialVersionUID`属性值赋给自动生成的`serialVersionUID`。

#### 2.3 Transient 属性不会被序列化
接着上面的案例，把`User`中的`name属性`改为`transient`修饰：
```java
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    
    // 年龄
    private int age;
    // 名字
    private transient String name;
    
    // 省略get set toString
}
```

先执行上面的`序列化方法（write）`：
```
序列化前的User对象：User{age=18, name='sandy'}
```

再执行`反序列化方法（read）`：
```
反序列化后的User对象：User{age=18, name='null'}
```

**`transient`属性为什么不会被序列化？**  
`transient`是序列化和反序列化时用于属性是否可序列化反序列化的 **“标记”** ，带有`transient`修饰的成员变量，在类中相当于一个普通的成员变量，对于该类的使用没有任何影响，只是在序列化的时候，带有`transient`标记的变量，无法被序列化和反序列化。

**`transient`属性应用场景：**  
在操作数据库对象实体时，不希望对某一个对象进行持久化操作，就可以用`transient`或者`@Transient`对目标属性进行修饰。
```java

@Table(name = "test_table")
@Data
public class PointExchangeLogDO implements Serializable {
    private static final long serialVersionUID = 1L;

    /**
     * 数据库自增ID
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "user_name")
    private String userNmae;

    /*不进行持久化操作的字段*/
    @Transient
    private String testColumn;
}
```

#### 2.4 父类、子类序列化问题
序列化是以正向递归的形式进行的：
- 如果父类实现了序列化那么其子类都将被序列化；
- 子类实现了序列化而父类没实现序列化，那么只有子类的属性会进行序列化，而父类的属性是不会进行序列化的。

##### （1）父类没有实现序列化，子类实现序列化
父类：
```java
public class Parent {
    //爱好
    private String like;
    
    // 省略get set toString
}
```

子类：
```java
public class User extends Parent implements Serializable {
    private static final long serialVersionUID = 1L;

    // 年龄
    private int age;
    // 名字
    private String name;

    // 省略get set 

    // toString拼接上父类属性，方便测试
    @Override
    public String toString() {
        return "User{" +
                "age=" + age +
                ", name='" + name + '\'' +
                ", like='" + super.getLike() + '\'' +
                '}';
    }
}
```

`序列化方法（write）`加上父类属性赋值：
```java
/**
 * 把User对象赋值后写入文件
 *
 * @throws Exception
 */
public static void write() throws Exception {
    FileOutputStream fos = new FileOutputStream("D:\\temp.txt");
    ObjectOutputStream oos = new ObjectOutputStream(fos);

    User user = new User();
    user.setLike("吃饭");
    user.setAge(18);
    user.setName("sandy");
    oos.writeObject(user);

    oos.flush();
    oos.close();
    System.out.println("序列化前的User对象：" + user);
}
```

先执行上面的`序列化方法（write）`：
```
序列化前的User对象：User{age=18, name='sandy', like='吃饭'}
```

再执行`反序列化方法（read）`：
```
反序列化后的User对象：User{age=18, name='sandy', like='null'}
```

通过结果可以发现， **<font color="red">父类没有实现序列化而子类实现序列化时，子类属性正常实例化，而父类属性未被序列化。</font>**

##### （2）父类实现序列化，子类不实现序列化
父类：
```java
public class Parent implements Serializable {
    private static final long serialVersionUID = 1L;
    
    // .......
}
```

子类：
```java
public class User extends Parent {
    // private static final long serialVersionUID = 1L;
	
    // .......
}
```

先执行上面的`序列化方法（write）`：
```
序列化前的User对象：User{age=18, name='sandy', like='吃饭'}
```

再执行`反序列化方法（read）`：
```
反序列化后的User对象：User{age=18, name='sandy', like='吃饭'}
```
通过结果可以发现， **<font color="red">当父类实现序列化而子类不实现序列化时，父类属性和子类属性均被序列化。</font>**

## 三、 序列化的原理
参考：[Java序列化的机制和原理](https://www.51cto.com/article/147650.html)
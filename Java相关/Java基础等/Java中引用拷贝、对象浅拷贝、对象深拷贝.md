# Java中引用拷贝、对象浅拷贝、对象深拷贝

[toc]

Java对象拷贝分为两种方式：一种是 **引用拷贝** ，一种是 **对象拷贝** 
- 引用拷贝：引用拷贝只会生成一个新的对象 `引用地址` ，但两个地址其最终指向的还是同一个对象；
- 对象拷贝：和引用拷贝的不同之处在于，这种方式会重新生成一个` 新的对象` ，生成的新对象与原来的对象没有任何关联。

其中对象拷贝又分为`浅拷贝`和`深拷贝`：
- 浅拷贝：对基本数据类型进行`值传递`，对引用数据类型进行`引用传递`的拷贝。
- 深拷贝：对基本数据类型进行`值传递`，对引用数据类型创建一个新的对象，并复制其内容。  
  深拷贝是整个独立的对象拷贝，深拷贝会拷贝所有的属性，包括属性指向的动态分配的内存。 **当对象和它所引用的对象一起拷贝时即发生深拷贝。深拷贝相比于浅拷贝速度较慢并且花销较大。**

**<font color="red">注意：Java中的对象拷贝需要实现`java.lang.Cloneable`接口，并重写`clone()`方法，这个无论对象的深、浅拷贝都需要这样做。</font>**

## 一、引用拷贝
### 1. 基本概念
引用拷贝也就是常用的对象赋值，这种方式不会生成新的对象，只会在原对象上增加了一个新的`对象引用`，两个`引用`指向的对象还是同一个；

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中引用拷贝、对象浅拷贝、对象深拷贝/引用拷贝示例.png)
</center>

`Java`中对象默认的赋值方式都是引用拷贝。比如下面代码对象赋值的过程就是引用拷贝：
```java
User user1 = new User();
User user2 = user1;
```

### 2. 引用拷贝需要注意的点
先看一下程序里面常见的例子：

首先定义一个`User`类：
```java
@Data
public class User {
    private int age;//年龄
    private String name;//姓名
}
```

测试：
```java
public class Test {
    public static void main(String[] args) {
        // 1.实例化一个user1对象，并对属性赋值
        User user1 = new User();
        user1.setName("我是user1");
        user1.setAge(18);

        // 2.然后把user1对象赋值给user2
        User user2 = user1;

        // 3.给user2的属性赋值
        user2.setAge(1);
        user2.setName("我是user2");

        // 4.输出user1和user2的属性值
        System.out.println(user1);
        System.out.println(user2);
    }
}
```

打印结果如下：
```
User(age=1, name=我是user2)
User(age=1, name=我是user2)
```
可以看到`user1`对象的值也被修改了。

结合`引用拷贝`的原理可以知道，因为`user1`和`user2`这两个引用指向的其实是同一个`User`对象，所以当修改`user2`的属性时其实修改的也是`user1`所引用的对象的属性。

在程序中如果存在这种在一个对象上多次赋值再使用的情况其实是很危险的。  
有时候调用的层次多了之后，被传递的使用者修改了对象属性会造成业务逻辑上的错误（如上面的例子：在`user2`修改属性值之后，还有业务代码需要拿`user1`来进行业务操作的话，那么此时的`user1`属性值都已经被修改了，这样势必会产生业务上的错误）， **而这样的问题又比较难发现，并且可读性也会变差，因此在开发中应尽量避免对象多层传递赋值。**

## 二、对象浅拷贝
浅拷贝只会将被复制对象的 **第一层属性** 进行复制；
- 若第一层属性为`原始类型`（如：int、char等基本数据类型）的值，则直接复制其`值`，一般称之为 **“传值”**；  
- 若第一层属性为`引用类型`（如：其他对象的引用等）的值，则复制的是其存储的指向堆内存对象的`地址指针`，一般称之为 **“传址”** 。

**因此被浅拷贝的对象是会重新生成一个新的对象，新的对象和原来的对象是没有任何关系的，但是如果对象中的某个属性是引用类型的话，那么该属性对应的对象是不会重新生成的（该属性的引用还是指向原来的对象）。**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中引用拷贝、对象浅拷贝、对象深拷贝/对象浅拷贝示例.png)
</center>

### 1. 实现浅拷贝
需要被拷贝的对象需要实现`Cloneable` 接口，再调用对象的`clone`方法可以实现对象的浅拷贝。

`Teacher`类：
```java
@Data
public class Teacher{
    //老师姓名
    private String teacherName;
}
```

`User`类，需重写`clone()`方法：
```java
@Data
public class User implements Cloneable {
    //名字
    private String name;

    //老师（该属性是User对象的中的一个引用类型的属性）
    private Teacher teacher;

    @Override
    protected User clone(){
        try {
            return (User) super.clone();
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```

测试：
```java
public class Test {
    public static void main(String args[]) throws Exception {
        // user1有一个teacher对象的属性
        Teacher teacher = new Teacher();
        teacher.setTeacherName("teacherName1");

        User user1 = new User();
        user1.setName("userName1");
        user1.setTeacher(teacher);

        // 对user1进行浅拷贝，再重新对他的属性赋值
        User user2 = user1.clone();
        user2.setName("userName2");
        user2.getTeacher().setTeacherName("teacherName2");

        // 最后我们再打印user1的对象属性
        System.out.println("user1的属性信息：" + user1);
    }
}
```

打印结果
```
user1的属性信息：User(name=userName1, teacher=Teacher(teacherName=teacherName2))
```

从打印结果可以看出：
1. `user2`修改了`name`之后并没有影响`user1`的`name`属性，这说明`user2`和`user1`对象是独立的。
2. `user2`修改了`teacher` 对象的属性之后`user1`的`teacher`对象属性也同时改变了，这说明`user`对象的`clone`方法并不会把其对象中引用的其他对象进行拷贝，这种情况就是 **浅拷贝** 。

### 2. 为什么浅拷贝不会拷贝其引用的对象？
1. 不给其他类强加意义：  
   `User类`为了能进行浅拷贝就实现了 `Cloneable` 接口，但是其引用对象`Teacher`没有实现`Cloneable` 也许说`明Teacher`类本身就不想被拷贝；如果在拷贝`User`的情况下，同时也把`Teacher`拷贝了，这就相当于实现了本不应该实现的代码。
2. 不破坏其原来对象的代码逻辑：  
   如果`User`引用的`Teacher`是个单例模式的对象，那如果在`User`拷贝的时候同时也拷贝出了一个`Teacher` 那是不是就会破坏`Teacher`这个单例模式对象的逻辑初衷。

## 三、对象深拷贝
**深拷贝相比浅拷贝的不同就是，深拷贝会把拷贝的对象和其属性引用的对象都重新生成新的对象。**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中引用拷贝、对象浅拷贝、对象深拷贝/对象深拷贝示例.png)
</center>

### 1. 实现深拷贝
创建`User`类，并实现序列化接口：
```java
@Data
public class User implements Serializable {
    //名字
    private String name;

    //老师（该属性是User对象的中的一个引用类型的属性）
    private Teacher teacher;
}
```

创建`Teacher`类，并实现序列化接口：
```java
@Data
public class Teacher implements Serializable {
    //老师姓名
    private String teacherName;
}
```

测试，把对象进行序列化后再反序列化：
```java
public class Test {
    public static void main(String args[]) throws Exception {
        // user1有一个teacher对象的属性
        Teacher teacher=new Teacher();
        teacher.setTeacherName("teacherName1");
        User user1 = new User();
        user1.setName("userName1");
        user1.setTeacher(teacher);

        // 序列化写入到流里
        ByteOutputStream bots=new ByteOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bots);
        oos.writeObject(user1);

        // 将流反序列化成user2对象
        ObjectInputStream ois=new ObjectInputStream(new ByteArrayInputStream(bots.toByteArray()));
        User user2 = (User) ois.readObject();
        user2.setName("userName2");
        user2.getTeacher().setTeacherName("teacherName2");

        //最后我们再打印user1的对象属性
        System.out.println("user1的属性信息：" + user1);
    }
}
```

打印结果
```
user1的属性信息：User(name=userName1, teacher=Teacher(teacherName=teacherName1))
```
**小结：**  
使用序列化的方式进行深拷贝后，改变`user2`对象中的属性不会对原来`user1`对象中的属性有任何影响。说明，`user1`和`user2` 不管是属性还是其引用对象都是重新生成互不关联的两个对象。

## 四、补充
上述浅拷贝中说到 **“被浅拷贝的对象是会重新生成一个新的对象，新的对象和原来的对象是没有任何关系的，但是如果对象中的某个属性是 `引用类型` 的话，那么该属性对应的对象是不会重新生成的（该属性的引用还是指向原来的对象）”。**

众所周知，`String`是一个引用类型。不过`String`比较特殊，它本身没有实现 `Cloneable`接口，传递是`引用地址`；由于它的`final`性，在拷贝时候其实都是生成`一个新的引用地址`和`一个新的被指向的堆空间`， **原对象的引用和副本（拷贝）的引用互不影响** 。  
因此对象浅拷贝的时候，`String`就和基本数据类型一样，表现出了 **"深拷贝"** 特性（即复制了新的一份`String`对象）。

`String`的这个特点在上述示例代码中均有体现。

## 附：深度拷贝工具类
```java
public class BeanUtil {
    public static <T> T cloneTo(T src) throws RuntimeException {
        ByteArrayOutputStream memoryBuffer = new ByteArrayOutputStream();
        ObjectOutputStream out = null;
        ObjectInputStream in = null;
        T dist;
        try {
            out = new ObjectOutputStream(memoryBuffer);
            out.writeObject(src);
            out.flush();
            in = new ObjectInputStream(new ByteArrayInputStream(memoryBuffer.toByteArray()));
            dist = (T) in.readObject();
        } catch (Exception e) {
            throw new RuntimeException(e);
        } finally {
            if (out != null) {
                try {
                    out.close();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
            if (in != null) {
                try {
                    in.close();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
        }
        return dist;
    }
}
```
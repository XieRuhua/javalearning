# Java的三种代理模式

## 代理模式简述
**代理模式** 的意图是为某一类对象提供一种代理，以控制对这个对象的访问，从而对被代理对象的功能进行扩展或者拦截。

同样增强扩展对象功能的设计模式还有 **装饰器模式** 

**代理模式和装饰器模式的区别：**
- `装饰器模式`在于给对象动态的添加一些额外的功能，对于这些功能的扩展是可以在对象创建完成后动态的更改的；
- `代理模式`是`组合模式`和`继承模式`的一种折衷，`代理模式`是在获取对象时确定代理对象，它的扩展功能在对象创建后已经确定了，而`装饰器模式`可以理解为装饰器和实际对象可以灵活组合。
- **`代理模式`针对的是整个类，`装饰器模式`可能更加偏向于针对某个对象。**

## 一、 静态代理
静态代理就是实现一个接口，它和被代理对象实现同样的接口，来代替原有类，以实现功能的扩展。  

简单的示例代码如下：想为`RealClass类`的`sayHello()方法`增加一个 **日志打印功能** ，于是创建了`ProxyClass`代理类
```java
/**
 * 用于代理类和被代理类实现的接口
 */
public interface IService {
    void sayHello();
}
```
```java
/**
 * 被代理的目标类
 */
public class RealClass implements IService {
    @Override
    public void sayHello() {
        System.out.println("hello word..........");
    }
}
```
```java
/**
 * 代理类
 */
public class ProxyClass implements IService {
    private RealClass realClass;

    public ProxyClass(RealClass realClass){
        this.realClass = realClass;
    }

    @Override
    public void sayHello() {
        System.out.println("hello proxy begin");
        realClass.sayHello();
        System.out.println("hello proxy end");
    }
}
```
```java
public class MainTest {
    public static void main(String[] args){
        RealClass realClass = new RealClass();

        // static proxy
        ProxyClass proxyClass = new ProxyClass(realClass);
        proxyClass.sayHello();
    }
}
```

打印：
```
hello proxy begin
hello word..........
hello proxy end
```

**静态代理总结:**  
1. 可以做到在不修改目标对象的功能前提下，对目标功能扩展。  
2. 缺点:  
   - 因为代理对象需要与目标对象实现一样的接口，使得代理类过多；
   - 一旦接口增加方法，目标对象与代理对象都要维护。

**`动态代理`即可解`决静态代理`的缺点。**

## 二、 动态代理
**动态代理解决了静态代理中同时给多个类新增一个相同的代理功能时，产生过多代理类的问题。**

动态代理的动态指的是可以根据被代理的类或接口动态的生成代理类，对于同一种代理功能我们只需要实现一次即可，从而减少代码的冗余。 **`Spring`的`AOP`就是采用动态代理的方式来达到增强原有代码的目的。**

动态代理更像一个代理对象生成器，输入参数为被代理的类或接口再加上被代理的对象（可选）来生成一个实现了代理接口的类的对象。  
`JAVA`中常用的动态代理有两种方式，一种是 **基于反射的`JDK动态代理`** ，一种是基于 **字节码生成操作的`CGLIB代理`** 。

### 1. JDK动态代理
为两个不同的类`RealClass`和`RealClass1`同时增加了 **日志打印功能** ，用`Proxy.newProxyInstance`来生成了代理对象，将代理功能的实现编码在`ProxyInvokeHandler`对象中，来起到拦截方法调用的功能，以控制对象的访问。

`JDK动态代理`必须要求代理类 **实现了某一个接口** ，该代理方式的原理是通过反射动态地实例化一个实现了该接口的对象，然后将该对象的所有方法调用都使用`InvocationHandler`进行拦截。
```java
/**
 * 用于代理类和被代理类实现的接口
 */
public interface IService {
    void sayHello();
}
```
```java
/**
 * 代理类
 */
public class ProxyClass implements IService {
    private RealClass realClass;

    public ProxyClass(RealClass realClass){
        this.realClass = realClass;
    }

    @Override
    public void sayHello() {
        System.out.println("hello proxy begin");
        realClass.sayHello();
        System.out.println("hello proxy end");
    }
}
```
```java
/**
 * 被代理类RealClass
 */
public class RealClass implements IService {
    @Override
    public void sayHello() {
        System.out.println("RealClass===hello word..........");
    }
}

/**
 * 被代理类RealClass1
 */
public class RealClass1 implements IService {
    @Override
    public void sayHello() {
        System.out.println("RealClass2===hello word..........");
    }
}
```
```java
/**
 * 测试类
 */
public class MainTest {
    public static void main(String[] args){
        RealClass realClass = new RealClass();
        RealClass1 realClass1 = new RealClass1();

        // dynamic proxy -- realClass
        MyHandler handler = new MyHandler(realClass);
        Object obj = Proxy.newProxyInstance(
                realClass.getClass().getClassLoader(),
                new Class[]{IService.class},
                handler
        );
        IService iService = (IService) obj;
        iService.sayHello();


        // dynamic proxy -- realClass1
        MyHandler handler1 = new MyHandler(realClass1);
        Object obj1 = Proxy.newProxyInstance(
                realClass1.getClass().getClassLoader(),
                new Class[]{IService.class},
                handler1
        );
        IService iService1 = (IService) obj1;
        iService1.sayHello();
    }
}
```

打印：
```
jdk dynamic proxy begin
RealClass===hello word..........
jdk dynamic proxy end
jdk dynamic proxy begin
RealClass2===hello word..........
jdk dynamic proxy end
```

`JDK动态代理`存在的问题：
1. 代理对象不需要实现接，但是被代理对象一定要实现接口，否则不能用动态代理。
2. 被代理对象内部方法互相调用不会触发拦截。
3. 当我们写`AOP`的切点拦截实现了某个接口的类时，此时使用具体的类来进行依赖注入时会报错，只能使用接口类同时指定`Bean`的名称，因为容器中保留的并不是具体的类的`Bean`，而是代理对象的`Bean`。  
   比如我们有`接口I`， `类A`和`类B`实现了`接口I`，如果使用了`JDK动态代理`，那么容器中存在的对象是实现了`接口I`的两个`$Proxy0`对象，而没有`A`、`B`两个类。

### 2. CGLIB动态代理
通过设置代理对象的父类，子类继承父类的方式对类功能进行扩展和方法调用的拦截。  
通过`MethodInterceptor接口`来拦截方法。被代理对象不需要实现特定接口，可以让内部方法互相调用也会触发方法拦截，但是`Spring`不会使用这种方法，`Spring`依然不会让内部方法互相调用产生拦截。

简单示例代码如下：
```java
public class HelloService {
    public HelloService() {
        System.out.println("HelloService构造");
    }

    /**
     * 该方法不能被子类覆盖,Cglib是无法代理final修饰的方法的
     */
    final public String sayOthers(String name) {
        System.out.println("HelloService:sayOthers>>"+name);
        return null;
    }

    public void sayHello() {
        System.out.println("HelloService:sayHello");
    }
}
```
```java
public class MyMethodInterceptor implements MethodInterceptor {

    /**
     * sub：cglib生成的代理对象
     * method：被代理对象方法
     * objects：方法入参
     * methodProxy: 代理方法
     */
    @Override
    public Object intercept(Object sub, Method method, Object[] objects, MethodProxy methodProxy) throws Throwable {
        System.out.println("======插入前置通知======");
        Object object = methodProxy.invokeSuper(sub, objects);
        System.out.println("======插入后者通知======");
        return object;
    }
}

```
```java
import net.sf.cglib.proxy.Enhancer;

public class MainTest {
    public static void main(String[] args) {
        // 通过CGLIB动态代理获取代理对象的过程
        Enhancer enhancer = new Enhancer();
        // 设置enhancer对象的父类
        enhancer.setSuperclass(HelloService.class);
        // 设置enhancer的回调对象
        enhancer.setCallback(new MyMethodInterceptor());
        // 创建代理对象
        HelloService proxy= (HelloService)enhancer.create();
        // 通过代理对象调用目标方法
        proxy.sayHello();
        proxy.sayOthers("admin");
    }
}
```

打印：
```
HelloService构造
======插入前置通知======
HelloService:sayHello
======插入后者通知======
HelloService:sayOthers>>admin
```
可以看出`HelloService$sayOthers()`方法并没有被代理，因为`final`修饰的方法无法被重写覆盖。

**CGLib动态代理小结：**  
目标对象只是一个单独的对象，并不需要实现任何的接口，此时以目标对象子类（`继承`）的方式类实现动态代理。

### 3. JDK 动态代理和 CGLIB 动态代理对比
* `JDK动态代理` 只能代理实现了接口的类或者直接代理接口  
* `CGLIB动态代理` 是通过生成一个被代理类的子类（继承）来拦截被代理类的方法调用，因此无法对`static`、`final`类进行代理  
* `CGLIB动态代理` 也无法对`private`、`static`方法进行代理
* **灵活性：** 
  - 动态代理更加灵活，不需要必须实现接口，可以直接代理实现类，并且可以不需要针对每个目标类都创建一个代理类；
  - 另外，静态代理中，接口一旦新增加方法，目标对象和代理对象都要进行修改，这是非常麻烦的！
* **JVM 层面 ：** 
  - 静态代理在编译时就将`接口`、`实现类`、`代理类`这些都变成了一个个实际的 `class` 文件；
  - 动态代理是在运行时动态生成类字节码，并加载到 `JVM` 中的。

**就二者的效率来说，大部分情况都是 `JDK` 动态代理更优秀，随着 `JDK` 版本的升级，这个优势更加明显。**

**<font color="red">补充：`Spring AOP`默认采用`JDK`动态代理，如果被代理对象没有实现任何接口，则默认是`CGLIB`</font>**    
强制使用`CGLIB`代理的方法：**指定`proxy-target-class = "true"`** 或者 **基于注解`@EnableAspectJAutoProxy(proxyTargetClass = true)`**
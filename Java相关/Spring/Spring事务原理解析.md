# Spring事务原理解析

[笔记内容参考1：Spring事务原理深入解析（AOP,Threadlocal, 隔离级别,传播级别）](https://blog.csdn.net/weixin_44366439/article/details/90381619)  
[笔记内容参考2：Spring 事务实现分析](https://www.jianshu.com/p/2449cd914e3c)

> **文档Spring版本  Spring-5.0.8.RELEASE**

[toc]

## 一、基础知识介绍
### 1. JDBC
#### 1.1 简单示例
[JDBC官方文档](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html)

`JDBC（Java DataBase Connectivity —— Java数据库连接）`，为`Java`提供了通用的数据访问`API`，可以通过它来建立`SQL`数据库连接并访问数据库。

简单事务的代码片段：
```java
try {
    // 获取数据库连接
    conn = DriverManager.getConnection("url","username","userpwd");
    // 禁止自动提交，开启事务
    conn.setAutoCommit(false);
    stmt = conn.createStatement();
    // 数据库更新操作1
    stmt.executeUpdate("update table …"); 
    // 数据库更新操作2
    stmt.executeUpdate("insert into table …"); 
    // 事务提交
    conn.commit();
} catch (Exception ex) {  
    // 操作异常，回滚事务
    conn.rollback(); // 操作不成功则回滚
}
```

#### 1.2 JDBC事务存在的问题
**分层架构中，事务控制应该放在哪一层？**  
事务是以业务逻辑为基础的，一个完整的业务应该对应服务层（`service`层）里的一个方法；如果业务操作失败，则整个事务回滚；所以，事务控制是应该放在`service`层的。  
如果把事务放在`DAO(Data Access Object)`层中，请看下面的例子：
```java
public class ClassDAO {
    private Connection conn = DBManager.getConnection;
    public void delClassAndClassStuReal(String classId) {
        try {
            conn.setAutoCommit(false);
            //班级的删除
            //班级学生关系记录的删除
            conn.commit(); //事务提交
        } catch(SQLException e) {
            conn.rollback();
        }
    }
}
```
虽然也能实现需求。

但是，`DAO`层的设计应该遵循一个很重要的原则： **DAO层应该保证操作的原子性** ，也就是说`DAO`里的每个方法都应该是不可以分割的。  
基于`DAO`层设计的细粒度原则，`classDAO`中应该是有这样两个方法：
```java
public class ClassDAO {
    public void delClass(String classId) {
        //班级的删除
    }
    public void delClassStuReals(String classId) {
        //班级学生关系记录的删除
    }
}
```
**那`JDBC`事务的问题就来了：**  
`JDBC`中事务控制是基于`Connection`的；虽说事务控制应该放在`service`层，当然也可以在`service`层实例化`connection`再将其传递给`DAO`层。  
但是`Connection`是不应该在`service`层中被实例出来的，`service`层不应该保存并感知数据库连接的， **否则将存在`service`层与`DAO`层明显的耦合。**

#### 1.3 Spring事务解决该问题的方式
`Spring`通过采用`AOP`以及`ThreadLocal`的方式，来解决这种 **耦合** 问题。

### 2. AOP设计思想
#### 2.1 代理模式
**代理模式** 的意图是为某一类对象提供一种代理，以控制对这个对象的访问，从而对被代理对象的功能进行扩展或者拦截。  
同样增强扩展对象功能的设计模式还有 **装饰器模式** 。

**`代理模式`和`装饰器模式`的区别：**
- `装饰器模式`在于给对象动态的添加一些额外的功能，对于这些功能的扩展是可以在对象创建完成后动态的更改的；
- `代理模式`是`组合模式`和`继承模式`的一种折衷，`代理模式`是在获取对象时确定代理对象，它的扩展功能在对象创建后已经确定了，而`装饰器模式`可以理解为装饰器和实际对象可以灵活组合。
- **代理模式针对的是整个类，装饰器模式可能更加偏向于针对某个对象。**

#### 2.2 静态代理
**静态代理就是它和被代理对象实现同样的接口，来代替原有类，以实现功能的扩展。**

简单的示例代码如下：想为`RealClass`类的`sayHello()`方法增加一个日志打印功能，于是创建了`ProxyClass`代理类
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
1. 可以做到在不修改目标对象功能的前提下，对目标功能扩展。  
2. 缺点:  
    - 因为代理对象需要与目标对象实现一样的接口，使得代理类过多；
    - 一旦接口增加方法，目标对象与代理对象都要维护。

**<font color="red">动态代理即可解决静态代理的缺点。</font>**

#### 2.3 动态代理
**动态代理解决了静态代理中同时给多个类新增一个相同的代理功能时，产生过多代理类的问题。**

动态代理的动态指的是可以根据被代理的`类`或`接口`动态的生成代理类，对于同一种代理功能只需要实现一次即可，从而减少代码的冗余。   
**注：`Spring`的`AOP`就是采用动态代理的方式来达到增强原有代码的目的。**

动态代理更像一个代理对象生成器，输入参数为被代理的类或接口再加上被代理的对象（可选）来生成一个实现了代理接口的类的对象。  
`Java`中常用的动态代理有两种方式：
- 一种是 **基于反射的`JDK动态代理`** ；
- 一种是基于 **字节码生成操作的`CGLIB代理`** 。

##### 2.3.1 JDK动态代理
为两个不同的类`RealClass`和`RealClass1`同时增加了日志打印功能，用`Proxy.newProxyInstance`来生成了代理对象，将代理功能的实现编码在`ProxyInvokeHandler`对象中，来起到拦截方法调用的功能，以控制对象的访问。

`JDK动态代理`必须要求代理类实现了某一个`接口`，该代理方式的原理是通过`反射`动态地实例化一个实现了该接口的对象，然后将该对象的所有方法调用都使用`InvocationHandler`进行拦截。
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
1. 代理对象不需要实现`接口`，但是被代理对象一定要实现`接口`，否则不能用JDK动态代理。
2. 被代理对象内部方法互相调用不会触发拦截。
3. 当使用`AOP`的切点拦截实现了某个接口的类时，此时使用具体的类来进行依赖注入时会报错，只能使用接口类同时指定`Bean`的名称，因为容器中保留的并不是具体的类的`Bean`，而是代理对象的`Bean`。  
   比如：有`接口I`， `类A`和`类B`实现了`接口I`，如果使用了`JDK动态代理`，那么容器中存在的对象是实现了`接口I`的两个`$Proxy0`对象，而没有`A`、`B`两个类。

##### 2.3.2 CGLIB动态代理
**通过设置代理对象的父类，子类继承父类的方式对类功能进行扩展和方法调用的拦截。**  
通过`MethodInterceptor接口`来拦截方法。被代理对象不需要实现特定接口，可以让内部方法互相调用也会触发方法拦截，但是`Spring`不会使用这种方法，并且`Spring`依然不会让内部方法互相调用产生拦截。

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

**动态代理-CGLIB小结：**  
目标对象只是一个单独的对象， **并不需要实现任何的`接口`** ，此时以目标对象子类（`继承`）的方式类实现动态代理。

##### 2.3.3 JDK 动态代理和 CGLIB 动态代理对比
* `JDK动态代理` 只能代理实现了`接口`的类或者直接代理接口  
* `CGLIB动态代理` 是通过生成一个被代理类的子类（`继承`）来拦截被代理类的方法调用，因此无法对`static`、`final`类进行代理  
* `CGLIB动态代理` 也无法对`private`、`static`方法进行代理

**就二者的效率来说，大部分情况都是 `JDK动态代` 理更优秀，随着 `JDK` 版本的升级，这个优势更加明显。**

**<font color="red">补充：`Spring AOP`默认采用`JDK`动态代理，如果被代理对象没有实现任何接口，则默认是`CGLIB`</font>**    
强制使用`CGLIB`代理的方法：**指定`proxy-target-class = "true"`** 或者 **基于注解`@EnableAspectJAutoProxy(proxyTargetClass = true)`**

##### 2.3.4 静态代理和动态代理的对比
* **灵活性：** 
    - 动态代理更加灵活，不需要必须实现接口，可以直接代理实现类，并且可以不需要针对每个目标类都创建一个代理类；
    - 静态代理中，接口一旦新增加方法，目标对象和代理对象都要进行修改，这是非常麻烦的！
* **JVM 层面 ：** 
    - 静态代理在编译时就将`接口`、`实现类`、`代理类`这些都编译成了一个个实际的 `class` 文件；
    - 动态代理是在运行时动态生成类的字节码文件，并加载到 `JVM` 中的。

#### 2.4 为什么使用AOP
**`AOP`：面向切面编程。** 所谓面向切面，就是把代码的执行流程认为是一个顺序的流，然后`AOP`增强功能 **横向的切入** 这个流，以实现相应的功能增加，对于这个流本身来说，它可以不感知切面的存在。

如下图所示，在没有`AOP`功能的情况下，在代码执行的流程中对`方法B`执行的前后新增一个日志打印功能，那么需要在`方法B`调用之前和之后新增一些代码，即在`方法B`之前和之后各新增一行日志打印代码。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/不使用AOP的代码执行流程.png)
</center>

这存在的最主要的问题在于需要修改原有的代码；假设需要加入的新功能不止是打印一行代码这么简单，而且需要新增的地方不止这里，那么在代码中到处修改或插入业务不关心的代码，将会导致代码臃肿。

如果使用了`AOP`拦截，如下图所示，可以通过定义`“切点”`来设置方法拦截的地点，定义`切点`的操作使用`AOP`代码来完成的，业务代码可以完全不修改。之后可以在`“切面”`中实现相关的拦截逻辑。
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/使用AOP的代码执行流程.png)
</center>

#### 2.5 AOP会使用哪种代理
`Spring`会根据不同的情况来选择使用`JDK动态代理`或`CGLIB代理`。具体实现可以在`DefaultAopProxyFactory类`中查看。  
首先要了解`JDK动态代理`是基于`接口interface`的，只有某个类实现了接口，才可能会使用`JDK动态代理`。

通过`DefaultAopProxyFactory类`的代码，可以明确看出默认情况下对`JDK动态代理`和`CGLIB代理`选择的逻辑，源码如下：
```java
public class DefaultAopProxyFactory implements AopProxyFactory, Serializable {
    @Override
    public AopProxy createAopProxy(AdvisedSupport config) throws AopConfigException {
        // 1-3.如果配置中开启了激进优化配置或者开启了proxy-target-class强制使用代理类或者没有使用接口
        if (config.isOptimize() || config.isProxyTargetClass() || hasNoUserSuppliedProxyInterfaces(config)) {
            Class<?> targetClass = config.getTargetClass();
            if (targetClass == null) {
                throw new AopConfigException("TargetSource cannot determine target class: " +
                                             "Either an interface or a target is required for proxy creation.");
            }
            // 4. 如果被代理的类是一个接口
            if (targetClass.isInterface() || Proxy.isProxyClass(targetClass)) {
                // 4.1 使用JDK动态代理
                return new JdkDynamicAopProxy(config);
            }
            // 4.2 使用CGLIB代理
            return new ObjenesisCglibAopProxy(config);
        }
        else {
            // 使用JDK动态代理
            return new JdkDynamicAopProxy(config);
        }
    }
}
```
判断执行过程：
1. `config.isOptimize()`判断如果开启了激进优化配置。
2. `config.isProxyTargetClass()`判断如果开启了类代理，表示目标`类本身`被代理，而不是它实现的`接口`。（默认关闭，自动配置类为`AopAutoConfiguration`可以参考其源码进行配置）。
3. `hasNoUserSuppliedProxyInterfaces`如果类没有实现接口（根据实现的代码来决定）。
4. `targetClass.isInterface()`如果被代理的类是一个接口（被代理的类是可以完全没有任何实现的`Interface`）。

**<font color="red">补充：所以`Spring AOP`默认采用`JDK`动态代理，如果被代理对象没有实现任何接口，则默认是`CGLIB`</font>**    
强制使用`CGLIB`代理的方法：**指定`proxy-target-class = "true"`** 或者 **基于注解`@EnableAspectJAutoProxy(proxyTargetClass = true)`**

#### 2.6 AOP代码编写关键及AOP执行流程
```java
@Aspect
@Component
public class MchAspect implements Advice{
    @Pointcut("within(com.xrh.demo.*)")
    public void withinPointcut(){}

    /**
     *  Any join point (method execution only in Spring AOP) where the executing method has an @Transactional annotation:
     */
    @Pointcut("@annotation(com.xrh.demo.aop.MyTransactional)")
    public void annotationPointcut(){}
    @Around(value = "annotationPointcut()")
    public Integer doAround(ProceedingJoinPoint pjp) throws Throwable {
        System.out.println("doAround");
        if (pjp.getArgs().length != 0) {
            pjp.proceed();
        }
        return 123;
    }

    @Before(value = "annotationPointcut()")
    public void doBefore(JoinPoint joinPoint) throws Throwable {
        // start stopwatch
        joinPoint.getArgs();
        System.out.println("Before");
    }
}
```
通过编写一个`切面Aspect对象`，来抽象一个拦截面。
注解描述：
- `@Component`：`Spring`启动时会将所有包含这个注解的类实例化为`Bean`放入容器中。
- `@Aspect`：表示这是一个`"切面"`，`Spring`启动时会扫描所有包含这个注解的`Bean`的定义，扫描这个`Bean`的所有方法，将其封装抽象成一个个`增强Advisor`，用来对代理对象进行增强。
- `@Pointcut`：代表一个`"切点"`，所谓切点就是抽象了那些增强的方法具体的执行位置。比如上面例子中的`annotationPointcut()`，代表着拦截所有包含了`MyTransactional注解`的方法。  
  其他还有很多种编写方式，比如拦截某个类的某个方法，或者拦截实现了某个接口的类的所有方法等等。
- `@Around`、`@Before`：代表切面逻辑执行的时机。
    + **@Around** 就是环绕，就是在业务逻辑代码执行前可以做些什么，然后执行后还可以做些什么；
    + **@Before** 就是在业务代码执行前可以做些什么，类似的还有`@After`、`@AfterReturning`等等。

`AOP`执行的流程：  
`AOP`是通过`BeanPostProcessor`来进行处理的。每当实例化一个`Bean`时，会通过这个处理器来进行增强。增强的流程分为三步：
1. 获取所有的`增强器Advisor`:
   - 获取所有的`beanName`，在`beanFactory`中所有注册的都提取出来。
   - 遍历找出所有声明了`@AspectJ注解`的类。
   - 对`AspectJ注解`的类进行增强器提取，解析其中的一些注解方法，比如`@Around`这种方法封装成`Advice对象`，`@Pointcut`这些封装成`Pointcut对象`，`Advice对象`加上`Pointcut对象`封装成一个`Advisor对象`。  
     所以一个`Advisor对象`就记录了一个增强方法的 **执行时机地点** 和 **执行内容** 。
2. 寻找与当前要创建的`bean`匹配的增强器进行匹配。
3. 通过增强器创建代理对象。

### 3. ThreadLocal实现原理
关于`ThreadLocal`详细的实现原理可参考其他笔记：[ThreadLocal（JDK1.8）](https://xieruhua.github.io/javalearning/#/./Java相关/Java基础等/并发/ThreadLocal详解（JDK1.8）)

`ThreadLocal`主要解决了： **单例对象** 中的某属性，同时被多个线程访问时互相隔离的问题。  
它的原理相当于为每个线程存储了 **仅** 属于该线程的一份拷贝。简单示例代码如下：
```java
public class SingleObject {
    private static volatile SingleObject singleObject;

    private ThreadLocal<Integer> threadLocal;

    private SingleObject() {
        threadLocal = new ThreadLocal<>();
    }

    // 创建单例的threadLocal的对象
    public static SingleObject getInstance() {
        if (singleObject == null) {
            synchronized (SingleObject.class) {
                if (singleObject == null) {
                    singleObject = new SingleObject();
                    return singleObject;
                } else {
                    return singleObject;
                }
            }
        } else {
            return singleObject;
        }
    }

    public void setValue(Integer x) {
        threadLocal.set(x);
    }

    public Integer getValue() {
        return threadLocal.get();
    }

    public static void main(String[] args) throws InterruptedException {
        SingleObject singleObject = SingleObject.getInstance();

        // 线程1
        Thread thread1 = new Thread(new Runnable() {
            @Override
            public void run() {
                singleObject.setValue(1);
                System.out.println("线程1把值设置为1");
                try {
                    Thread.sleep(2000L);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("线程1中的值为" + singleObject.getValue());
            }
        });

        // 线程2
        Thread thread2 = new Thread(new Runnable() {
            @Override
            public void run() {
                singleObject.setValue(1000);
                System.out.println("线程2把值设置为1000");
            }
        });
        thread1.start();
        Thread.sleep(1000L);
        thread2.start();
    }
}
```
入上面代码所示，对于`单例对象SingleObject`有一个`属性threadLocal`，它记录了一个整数对象。同时被多个线程访问，其实多个线程访问的是各自线程的拷贝，不会互相干扰。  
**这种情况通常用来获取数据库连接。后面讲`Spring事务`的时候会用到这一块的知识。**

实现原理（`ThreadLocal`关键类）：
```java
public T get() {
    // 获取当前正在执行的线程
    Thread t = Thread.currentThread();
    // 获取当前线程对应的ThreadLocalMap对象
    ThreadLocalMap map = getMap(t);
    if (map != null) {
        ThreadLocalMap.Entry e = map.getEntry(this);
        if (e != null) {
            @SuppressWarnings("unchecked")
            T result = (T)e.value;
            return result;
        }
    }
    return setInitialValue();
}
```
每个线程对应着一个独立的`ThreadLocalMap`对象；该`Map`以`ThreadLocal对象`为`key`（即上例中为`threadlocal`对象），以要存储的值为`value`(上例中的`Integer`对象)。

也就是说上例中，`线程1`中记录了一个`ThreadLocalMap对象`，`线程2`中也记录了一个`ThreadLocalMap对象`，当分别在两个线程中执行`threadlocal.get()`时，相当于使用相同的`key`分别在两个`map`中执行了执行了`get`操作，虽然`key`相同，但是对应的`value`不同，从而实现了数据的隔离。

### 4. MySQL存储引擎Innodb的事务
数据库事务的`ACID`特性:
- `A(Atomicity：原子性)`：要么全部完成，要么全部不完成；不可能停滞在中间某个环节或者仅失败某一个环节。   
  在存储引擎`Innodb`中通过`commit`、`rollback`机制实现。并通过`undo log日志`来完成，该`log`仅用于回滚事务，不用于数据恢复。
- `C(Consistency：一致性)`：事务保证数据不会被破坏，不会存在写了一半崩溃的情况。使用`double write buffer`实现，解决的是向磁盘文件写入时，写到一半掉电的问题。
- `I(Isolation：隔离性)`：事务的隔离级别。
- `D(Durability：持久性)`：指的是将数据持久化写入磁盘，采用了`double write buffer`，日志记录（`redo log`，`bin log`）以及`fsync()`调用写入磁盘。
    - `redo log`是 **存储引擎级别** 的，写数据之前先写`redo log`，
    - `bin log`是 **MySQL级别** 的，持久化在`redo log`之后，在存储引擎`commit`操作之前。

#### 4.1 数据库事务隔离级别
- **`read-uncommitted`（读未提交，对应的问题`脏读`）**  
  读未提交的意思就是我在`事务A`中可以读取到`事务B` **未提交** 的变更值。这样会导致的问题是，如果`事务B`最终未提交该事务，回滚了，那么`事务A`读取到`事务B`变更的值就是一个错误的值。 **这种现象叫做脏读。**  
  为了解决这个问题，必须要读取已经提交的修改才行，不能读那些还没有提交的随时可能被回滚的脏数据。于是升级为读已提交。

- **`read-committed`（读已提交，对应的问题`不可重复读`）**  
  读已提交就是会仅读取那些已经提交的变更，已经提交的变更都是有效的变更。所以不会出现读无效的脏数据的情况。但是随之而来的是另外一个问题，就是 **不可重复读** 的问题。  
  意思很简单，就是`A事务`第一次读取变量`X`的值为`100`，第二次读取`X`的值变为`200`，这中途`B事务`提交了修改将`X`变为`200`。这种情况下，`A事务`对`B事务`有所感知，受到了`B事务`的影响，两次读到的值不一样， **这种现象叫做不可重复读。**  

- **`repeatable-read`（可重复读，对应的问题`幻读`）**  
  为了解决读已经提交级别中的 **不可重复读** 问题，升级到了可重复读级别。然后存在的问题就是 **幻读** 了。  
  幻读指的是通过`Insert`后新增了记录，两次相同的查询条件而查询到的记录数不一样。   
  幻读会带来的一个影响主要是进行分页查询时，`查询总数`的sql和`查询页数`的sql查询到不同的结论，会导致分页异常。   但是`MySQL`的`innodb`存储引擎使用`gap锁`的机制来在可重复读的隔离级别下就解决了幻读问题。 具体原理可以参考`MVCC机制`和`gap锁`或者`next-key锁`。

- **`serializable`（串行化）**  
  是最高的事务隔离级别，在该级别下所有操作都上 **排它锁** ，事务串行化顺序执行，可以完全避免`脏读`、`不可重复读`与`幻读`。 **但是这种事务隔离级别效率低下，比较耗数据库性能，一般不使用。**

#### 4.2 可重复读隔离级别的实现原理
这里介绍最常用的`可重复读`的实现原理。
在这之前需要了解`Innodb`有两种读模式，分别是 **一致性非锁定读（`Consistent Nonlocking Reads`）** 和 **锁定读（`Locking Read`）** 。通常也叫`快照读`和`直接读`。

**快照**的建立是在事务启动后第一次执行查询操作时开始。参考`MySQL`官方文档：[一致性非锁定读取（Consistent Nonlocking Reads）](https://dev.mysql.com/doc/refman/5.7/en/innodb-consistent-read.html) 和 [锁定读（Locking Read）](https://dev.mysql.com/doc/refman/5.7/en/innodb-locking-reads.html)

##### 一致性非锁定读(Consistent Nonlocking Reads)
`一致性非锁定读`采用了一种多版本控制的机制，来实现`快照机制`的读，版本控制简易示例如下图：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/InndoDB事务的多版本控制的机制.png)
</center>

`InndoDB`的每行记录有一个`6字节`的`事务编号DB_TRX_ID`，存储了最近更新此记录的`事务ID`。还有`8字节`的`DB_ROLL_PTR指针`，指向事务的`undo log`。`事务ID`在执行了第一次`select`时（不管是读的哪个表）产生，是主键增长的。
- 对于 **可重复读** 级别，当发现记录的`事务ID`大于`当前事务ID`，则会根据`undo log`获取小于等于当前`事务ID`的记录版本。  
- 对于 **读已提交** 级别，则一直会读取最新已提交数据（可能会读取到被更改过的数据，因此会出现`不可重复读`的问题）。

##### 锁定读（Locking Read）
不管在何种隔离级别下，如果使用`select … for update` 或者使用`update` 语句时，都会读到最新的数据，同时给这行数据上`record行锁`。在`可重复读级别`下，可能还会给相应的索引位加上`GAP间隙锁`。

举个例子：在一个`可重复读`的事务中，使用`select * from t_user where user_id = 1` 返回空，但是执行`update t_user set user_name = “张三” where user_id = 1`时，会成功更新这条记录。
那么这里`select操作`是 **一致性非锁定读** ，`update操作`是 **锁定读** 。

**关于`MySQL`各种锁的详细介绍可参考其他笔记：[MySQL 的全局锁、表锁和行锁](https://xieruhua.gitee.io/javalearning/#/./数据库/MySql/MySql的全局锁、表锁和行锁)**

## 二、Spring事务介绍
### 1. 简介
**<font color="red">`Spring`本身并不实现事务。 `Spring事务` 的本质还是底层数据库对事务的支持，没有 `数据库事务` 的支持，`Spring事务`就不会生效。</font>**

`Spring事务`提供一套抽象的事务管理，并且结合 `Spring IOC` 和 `Spring AOP`，简化了应用程序使用数据库事务，通过声明式事务（`@Transactional注解`的方式），可以做到对应用程序无侵入的实现事务功能。

例如使用 `JDBC` 操作数据库，想要使用事务时的步骤为：
1. 获取数据库连接 `Connection con = DriverManager.getConnection()`
2. 开启事务`con.setAutoCommit(true/false);`
3. 执行`CRUD`
4. 提交事务/回滚事务 `con.commit()` / `con.rollback()`;
5. 关闭数据库连接 `conn.close()`;

而采用`Spring事务`后，只需要关注`第3步`的具体实现，其他的步骤都是`Spring事务`完成。

<font color="red">简单理解：`Spring事务`的本质其实就是 `AOP` +  `数据库事务`；`Spring` 将数据库的事务操作提取为切面，通过`AOP`的方式增强事务方法。</font>

### 2. 事务的传播级别（行为）
`Spring`事务的传播级别描述的是多个使用了`@Transactional注解`的方法互相调用时，`Spring`对事务的处理：
1. **REQUIRED：** 如果当前线程已经在一个事务中，则加入该事务，否则新建一个事务。如：
   - `方法B`的事务级别定义为`REQUIRED`, 那么由于执行`方法A`的时候，`方法A`已经开启了事务，这时`方法A`调用`方法B`，`方法B`看到自己已经运行在`方法A`的事务内部，就不再起新的事务。
   - 而`方法A`运行的时候发现自己没有在事务中，他就会为自己分配一个事务。这样，在`方法A`或者在`方法B`内的任何地方出现异常，事务都会被回滚。即使`方法B`的事务已经被提交，但是`方法A`在接下来执行失败则要回滚，`方法B`也要回滚

2. **SUPPORT：** 如果当前线程已经在一个事务中，则加入该事务，否则不使用事务（以非事务的形式运行）。

3. **MANDATORY(强制的)：** 必须在一个事务中运行。如果当前线程已经在一个事务中，则加入该事务，否则抛出异常。

4. **REQUIRES_NEW：** 无论如何都会创建一个新的事务，如果当前线程已经在一个事务中，则挂起当前事务，创建一个新的事务。  
   如：`方法A`的事务级别为`REQUIRED`，`方法B`的事务级别为`REQUIRES_NEW`，那么在同一个线程中（`A->B`的执行顺序）当执行到`方法B`的时候，`方法A`所在的事务就会挂起，`方法B`会起一个新的事务，等待`方法B`的事务完成以后，`方法A`才继续执行。

   `REQUIRES_NEW`与`REQUIRED` 的事务区别在于事务的回滚程度了。因为`方法B`是新起一个事务，那么就是存在两个不同的事务：
   - 如果`方法B` 已经提交，那么`方法A`失败回滚，`方法B`是不会回滚的。
   - 如果`方法B` 失败回滚，且抛出的异常被`方法A`捕获，`方法A`事务仍然可能提交。

5. **NOT_SUPPORTED：** 当前线程不支持事务。即如果当前线程在一个事务中，则挂起事务。  
   如：`方法A`的事务级别是`REQUIRED` ，而`方法B`的事务级别是`NOT_SUPPORTED` ，那么当执行到`方法B`时，`方法A`的事务挂起，而`方法B`以非事务的状态运行完，再继续`方法A`的事务。

6. **NEVER：** 如果当前线程在一个事务中则`抛出异常`，即不能在事务中运行。  
   假设`方法A`的事务级别是`REQUIRED`， 而`方法B`的事务级别是`NEVER` ，那么当前线程执行到`方法B`就要抛出异常了。

7. **NESTED：** 执行一个嵌套事务，有点像`REQUIRED`和`REQUIRES_NEW`，但是有些区别，在`MySQL`中是采用`SAVEPOINT`来实现的。
   - **NESTED与REQUIRES_NEW的区别** ：`REQUIRES_NEW`另起一个事务，将会与他的父事务相互独立，而`NESTED`的事务和他的父事务是相依的，他的提交是要等和他的父事务一块提交的。  
     也就是说，如果父事务最后回滚，他也要回滚的。而`NESTED`事务的好处是他有一个`savepoint`。
     ```java
     ServiceA {
         // methodA 事务属性配置为 PROPAGATION_REQUIRED
         void methodA() {
             try {
                 //savepoint
                 ServiceB.methodB(); //methodB 事务属性配置为 PROPAGATION_NESTED
             } catch (SomeException) {
                 // 执行其他业务, 如 ServiceC.methodC();
             }
         }
     }
     ```
     也就是说`方法B`失败回滚，那么`方法A`也会回滚到`savepoint`点上，`方法A`可以选择另外一个分支，比如`方法C`，继续执行，来尝试完成自己的事务。
   - **NESTED与REQUIRED的区别：** `NESTED`表示如果当前已经存在一个事务，那么该方法将会在嵌套事务中运行。嵌套的事务可以独立于当前事务进行单独地提交或回滚。如果当前事务不存在，那么其行为与`REQUIRED`一样。
   
   <font color="red">NESTED嵌套事务: 外事务异常，内事务回滚；内事务异常，外事务正常。</font>

注意： **`Spirng`默认的传播级别是`REQUIRED`** ，常用的有`REQUIRED`和`REQUIRES_NEW`这两个。

再重点介绍一下`REQUIRED`和`REQUIRES_NEW`的区别。
- `REQUIRED`表示当前方法必须在一个事务中，如果当前线程已经在一个事务中，则它会加入该事务，不会开启新的事务。  
  比如`方法A`调用`方法B`时，`方法A`和`方法B`都有`@Transactional`注解。  
  ![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/REQUIRED隔离级别图示.png)
- `REQUIRES_NEW`表示当前方法无论如何都会起一个新的事务。  
  ![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/REQUIRES_NEW隔离级别图示.png)

### 3. 使用Spring事务
#### 3.1 声明式事务
业务代码：
```java
/**
 * 在需要事务的方法上增加如下注解
 * isolation（隔离级别）的默认值是DEFAULT
 * propagation（传播属性）的默认值是REQUIRED
 */
@Transactional(isolation = Isolation.DEFAULT, propagation = Propagation.REQUIRED)
public Map<String, Object> fun() {
}
```
`@Transactional`底层通过 `AOP` 实现，对应用程序侵入较少，采用注解的方式省去 `XML` 繁琐的配置。

#### 3.2 编程式事务
工具类代码
```java
@Component
public class Utils {
    @Autowired
    private DataSourceTransactionManager dataSourceTransactionManager;

    // 开启事务
    public TransactionStatus openTx() {
        return dataSourceTransactionManager.getTransaction(new DefaultTransactionAttribute());
    }
    // 提交事务
    public void commitTx(TransactionStatus ts) {
        dataSourceTransactionManager.commit(ts);
    }
    // 回滚事务
    public void rollbackTx(TransactionStatus ts) {
        dataSourceTransactionManager.rollback(ts);
    }
}
```

业务层代码
```java
@Service
public class RegisterServiceImpl implements RegisterService {
    @Autowired
    private Utils utils;
    @Override
    public void programming(String name,String age,String studentId) {
        TransactionStatus ts = null;
        try {
            // 开启事务
            ts = utils.openTx();
            registerMapper.programming( name, age, studentId);
            // 模拟报错触发事务回滚
            int a = 1/0;
            registerMapper.programming( name, age, studentId);
            if (ts != null) {
                // 提交事务
                utils.commitTx(ts);
            }
        } catch (Exception e) {
            if (ts != null) {
                // 回滚事务
                utils.rollbackTx(ts);
            }
        }
    }
}
```

#### 3.3 编程式事务和声明式事务的区别
- 声明式事务：通过`AOP`的方式在方法前使用编程式事务的方法开启事务，在方法后提交或回滚。用配置文件的方法或注解方法（如：`@Transactional`）控制事务。
- 编程式事务：手动开启、提交、回滚事务。

**通俗地去理解两者的区别，即声明式事务只需要`“声明”`就可以达到事务的效果；编程式事务需要`“编程”`才可以达到事务效果。**

### 4. Spring事务相关组件介绍
#### 4.1事务管理器 PlatformTransactionManager
`PlatformTransactionManager` 是 `Spring` 事务结构中的核心接口，`Spring`并不直接管理事务，而是提供了多种事务管器，他们将事务管理的职责委托给`Hibernate`或者`JTA`等持久化机制所提供的相关平台框架的事务来实现。

`Spring`事务管理器的接口是`org.springframework.transaction.PlatformTransactionManager`，`Spring`通过这个接口为各个平台如`JDBC`、`Hibernate`等都提供了对应的事务管理器，但是具体的实现就是各个平台自己的事情了。

接口的内容如下：
```java
Public interface PlatformTransactionManager(){  
    // 由TransactionDefinition得到TransactionStatus对象
    TransactionStatus getTransaction(TransactionDefinition definition) throws TransactionException; 
    // 提交
    Void commit(TransactionStatus status) throws TransactionException;  
    // 回滚
    Void rollback(TransactionStatus status) throws TransactionException;  
} 
```
通过`PlatformTransactionManager`的接口 可以看出，`Spring` 事务的的三个核心方法：**事务开启** 、 **提交事务** 、 **回滚事务** ；`Spring 事务`功能的实现 都是围绕这三个方法来实现。  
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/Spring事务管理接口.png)
</center>

#### 4.2 事务信息对象 TransactionInfo
事务信息对象，包括一个事务所有的信息：`事务管理器`、`事务定义对象`、`目标方法唯一标识`、`事务状态对象`；  
外层的`TransactionInfo` 用于在应用程序中获取 `当前的TransactionInfo` 对象。  
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/Spring事务事务信息对象TransactionInfo.png)
</center>

#### 4.3 事务状态 TransactionStatus
表示一个事务状态，在应用程序中可以通过 `TransactionInterceptor.currentTransactionStatus()` 的静态函数获取到。  
事务状态的作用：
1. 持有事务对象：使用`JDBC 事务`时，事务对象为 `DataSourceTransactionObject`
2. 对保存点（`savepoint`）的支持：可以在应用程序中通过设置保存点，在事务回滚时，回滚到保存点，而不是回滚部分。

#### 4.4 事务定义对象 TransactionDefinition
事务定义对象，封装了`@Transactional 注解`中设置的各种信息，通过收集`@Transactional`属性信息，获取到一个事务定义对象；有了事务定义信息就可以通过`PlatformTransactionManager` **开启事务** 或者 **复用一个事务** 。

#### 4.5 事务同步回调接口 TransationSynchronization
事务同步回调接口，在事务周期的各个点执行回调方法，比如 **挂起** 、 **继续** 、 **提交前后** 、 **完成前后** 。用于管理应用程序在事务周期中绑定的资源。  
在`Spring - Mybatis`整合时，`Mybatis` 正是利用了`TransationSynchronization`同步器，才让`Mybatis`的事务管理交给了 `Spring 事务`来管理。

#### 4.6 事务同步回调的管理器 TransactionSynchronizationManager
在事务运行过程中，需要保存一些状态或对象，比如：数据库连接
```java
// 应用代码随事务的声明周期绑定的对象
ThreadLocal<Map<Object, Object>> resources;

// 使用的同步器，用于应用扩展
ThreadLocal<Set<TransactionSynchronization>> synchronizations;

// 事务的名称
ThreadLocal<String> currentTransactionName;

// 事务是否是只读
ThreadLocal<Boolean> currentTransactionReadOnly;

// 事务的隔离级别
ThreadLocal<Integer> currentTransactionIsolationLevel;

// 是否实际的开启了事务，如果加入到其他的事务，就不是实际开启的事务。
ThreadLocal<Boolean> actualTransactionActive;
```

#### 4.7 挂起的资源持有对象 SuspendedResourceHolder
在挂起一个事务时，用于记录被挂起事务的运行时信息，这些信息就是`TransactionSynchronizationManager`中记录的事务信息。然后将这些信息保存在新的`DefaultTransactionStatus`对象中， **便于内部事务运行结束后，恢复外层事务** 。

### 5. 事务实现过程（声明式事务）
#### AOP实现事务的主流程
`Spring事务`把 **整个事务流程** 模板化，采用`AOP`的形式 **增强到** 需要事务的方法，所以按照`AOP`的实现 一定存在一个事务的增强器（`Advisor`），而这个增强器就是 `org.springframework.transaction.interceptor.BeanFactoryTransactionAttributeSourceAdvisor`，该增强器中有个环绕通知`org.springframework.transaction.interceptor.TransactionInterceptor`，所有的事务逻辑都在这个类的`Invoke` 方法中，分析`Spring事务`实现就从这个函数开始。

AOP所有对方法拦截都会封装成一个`MethodInterceptor`放到一个责任链中执行。它对应的`Advisor是BeanFactoryTransactionAttributeSourceAdvisor`。

下面主要来分析`TransactionInterceptor`这个拦截方法。进入这个类的`invoke`方法：
```java
//invocation 维护了 AOP 拦截器链 ，执行 invocation.prcess 方法 会沿着拦截器链执行下去直到目标方法。
@Override
@Nullable
public Object invoke(final MethodInvocation invocation) throws Throwable {
    // 获取目标对象（获取到被代理的类）
    Class<?> targetClass = (invocation.getThis() != null ? AopUtils.getTargetClass(invocation.getThis()) : null);
    // Adapt to TransactionAspectSupport's invokeWithinTransaction...
    // 执行父类TransactionAspectSupport的 invokeWithinTransaction...
    return invokeWithinTransaction(invocation.getMethod(), targetClass, invocation::proceed);
}
```

执行`invokeWithinTransaction`
进入`TransactionInterceptor#invoke`中的`invokeWithinTransaction`方法，方法位于 `org.springframework.transaction.interceptor.TransactionAspectSupport#invokeWithinTransaction`
```java
@Nullable
protected Object invokeWithinTransaction(Method method, Class<?> targetClass, final InvocationCallback invocation)
    throws Throwable {
    // If the transaction attribute is null, the method is non-transactional.
    // 1. 准备事务的基本信息（获取事务的属性）
    // 事务定义 TransactionAttribute 是 TransationDefinition 的子类
    final TransactionAttribute txAttr = getTransactionAttributeSource().getTransactionAttribute(method, targetClass);
    // 2. 获取事务管理器，这里是一个策略模式，根据 事务定义 指定的 事务管理器 获取到 指定的 事务管理器。
    final PlatformTransactionManager tm = determineTransactionManager(txAttr);
    // 连接点标识
    final String joinpointIdentification = methodIdentification(method, targetClass, txAttr);
    // 如果是声明式事务
    if (txAttr == null || !(tm instanceof CallbackPreferringPlatformTransactionManager)) {
        // Standard transaction demarcation with getTransaction and commit/rollback calls.
        // 3. 收集事务信息，状态，并开启事务，在Threadlocal中设置相关变量
        // 如果必要才会开启事务，这里会根据事务的传播行为来决定是否开启事务还是加入一个已经存在的事务。这里会涉及到事务的挂起
        TransactionInfo txInfo = createTransactionIfNecessary(tm, txAttr, joinpointIdentification);
        Object retVal = null;
        try {
            执行目标方法或者 执行AOP 拦截器链中的下一个拦截器。
                // This is an around advice: Invoke the next interceptor in the chain.
                // This will normally result in a target object being invoked.
                // 4. 执行业务代码，即被@Transactional注解标注的方法
                retVal = invocation.proceedWithInvocation();
        }
        catch (Throwable ex) {
            // target invocation exception
            // 5. 如果允许出现异常，执行处理，如回滚操作
            // 是否回滚 会根据 rollback 属性判断
            completeTransactionAfterThrowing(txInfo, ex);
            throw ex;
        }
        finally {
            // 6.清理事务环境，即将3.中ThreadLocal中设置的变量清除
            cleanupTransactionInfo(txInfo);
        }
        // 7.提交事务
        commitTransactionAfterReturning(txInfo);
        return retVal;
    }
}
// 如果是编程事务处理（省略）
else {
    // ............
}
```
可以在这个方法中看到`Spring事务`处理流程：
1. 获取事务属性，即解析`@Transactional注解`中的相关参数。
2. 获取事务管理器，就是需要在`@Transactional注解`中的`transactionManager`参数。
3. 收集事务信息，状态，并开启事务，并在当前线程中（`Threadlocal`）设置事务相关参数，标注了当前线程是运行在事务中的。
4. 执行被拦截的方法，即被`@Transactional注解`标注的那个方法。
5. 如果方法执行出现异常，做一些处理，可能会执行回滚操作或者设置回滚标志位。
6. 清理事务环境，将设置到`Threadlocal`中的相关变量清除，就好像没有开启过事务一样。
7. 提交事务。

`Spring`支持 **编程式事务管理** 和 **声明式事务管理** 两种方式。
- `编程式事务`使用`TransactionTemplate`或者直接使用底层的`PlatformTransactionManager`。  
  对于编程式事务管理，`Spring`推荐使用`TransactionTemplate`。  
- `声明式事务`是建立在`AOP`之上的。其本质是对方法前后进行拦截，然后在目标方法开始之前创建或者加入一个事务，在执行完目标方法之后根据执行情况提交或者回滚事务。
- `声明式事务`最大的优点就是不需要通过编程的方式管理事务，这样就不需要在业务逻辑代码中掺杂事务管理的代码，只需在配置文件中做相关的事务规则声明（或通过基于`@Transactional`注解的方式），便可以将事务规则应用到业务逻辑中。

#### 5.1 准备事务
准备事务阶段主要是做了两件事情

##### 5.1.1 获取事务属性
收集`@Transactional`注解属性信息生成 **事务定义对象** ，由于`@Transactional`可以作用在类上 又可以作用在方法上，所以在获取属性信息的时候，就考虑到这两种情况。  
`org.springframework.transaction.annotation.AnnotationTransactionAttributeSource` 类就是用来解析类和方法上面的`@Transactional 注解`属性。

跟着代码一路找到`AnnotationTransactionAttributeSource` 的父类`AbstractFallbackTransactionAttributeSource`中的`getTransactionAttribute`方法：
```java
/**
 * 这里method和targetClass是被@Transactional注解标注的方法和类。
 */
public TransactionAttribute getTransactionAttribute(Method method, @Nullable Class<?> targetClass) {
    if (method.getDeclaringClass() == Object.class) {
        return null;
    }
    // First, see if we have a cached value.
    // 从缓存中获取值
    Object cacheKey = getCacheKey(method, targetClass);
    Object cached = this.attributeCache.get(cacheKey);
    if (cached != null) {
        // Value will either be canonical value indicating there is no transaction attribute,
        // or an actual transaction attribute.
        if (cached == NULL_TRANSACTION_ATTRIBUTE) {
            return null;
        }
        else {
            return cached;
        }
    }
    else {
        // We need to work it out.
        // 根据@Transactional注解找到事务属性对象
        TransactionAttribute txAttr = computeTransactionAttribute(method, targetClass);
        // Put it in the cache.
        if (txAttr == null) {
            this.attributeCache.put(cacheKey, NULL_TRANSACTION_ATTRIBUTE);
        }
        else {
            String methodIdentification = ClassUtils.getQualifiedMethodName(method, targetClass);
            if (txAttr instanceof DefaultTransactionAttribute) {
                ((DefaultTransactionAttribute) txAttr).setDescriptor(methodIdentification);
            }
            if (logger.isDebugEnabled()) {
                logger.debug("Adding transactional method '" + methodIdentification + "' with attribute: " + txAttr);
            }
            this.attributeCache.put(cacheKey, txAttr);
        }
        return txAttr;
    }
}
```
注意：这里首先会从缓存里取，这样不用每次调用这个方法时都去解析一遍。根据通常情况下，这里的第一次创建都是在`Bean`创建的时候，就会扫描`@Transactional`，然后把属性存到 **缓存** 中。

这里事务属性`TransactionAttribute`的相关字段：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/事务属性相关字段.png)
</center>

关键字段：
- `rollbackRules`：`rollbackFor`参数，指定根据什么异常来回滚
- `propagationBehavior`：传播级别
- `isolationLevel`：隔离级别

通过上面可以知道`@Transactional`可以作用在类上，又可以作用在方法上；  
那么到底先解析类上的注解还是先解析方法上的注解呢？如果方法和类上面同时存在呢？是完整替换？还是取并集？

定义解析`@Transactional`注解的逻辑依旧定义在`AnnotationTransactionAttributeSource`的父类`AbstractFallbackTransactionAttributeSource`的`computeTransactionAttribute`方法中，也就是上面获取事务属性中的步骤之一`TransactionAttribute txAttr = computeTransactionAttribute(method, targetClass);`

源码如下：
```java
protected TransactionAttribute computeTransactionAttribute(Method method, Class<?> targetClass) {
    // Don't allow no-public methods as required.
    if (allowPublicMethodsOnly() && !Modifier.isPublic(method.getModifiers())) {
        return null;
    }

    // Ignore CGLIB subclasses - introspect the actual user class.
    Class<?> userClass = ClassUtils.getUserClass(targetClass);
    // The method may be on an interface, but we need attributes from the target class.
    // If the target class is null, the method will be unchanged.
    Method specificMethod = ClassUtils.getMostSpecificMethod(method, userClass);
    // If we are dealing with method with generic parameters, find the original method.
    specificMethod = BridgeMethodResolver.findBridgedMethod(specificMethod);

    //首先 解析方法上面 的 属性信息
    // First try is the method in the target class.
    TransactionAttribute txAttr = findTransactionAttribute(specificMethod);
    //如果方法上面存在 就返回。
    if (txAttr != null) {
        return txAttr;
    }

    //其次 解析作用在类上面的注解属性信息，如果找到 就返回。
    // Second try is the transaction attribute on the target class.
    txAttr = findTransactionAttribute(specificMethod.getDeclaringClass());
    if (txAttr != null && ClassUtils.isUserLevelMethod(method)) {
        return txAttr;
    }

    //解析接口方法上面的注解属性信息 ，如果找到返回。
    if (specificMethod != method) {
        // Fallback is to look at the original method.
        txAttr = findTransactionAttribute(method);
        if (txAttr != null) {
            return txAttr;
        }
        //最后 解析接口上面的注解信息。
        // Last fallback is the class of the original method.
        txAttr = findTransactionAttribute(method.getDeclaringClass());
        if (txAttr != null && ClassUtils.isUserLevelMethod(method)) {
            return txAttr;
        }
    }
    return null;
}
```
通过上面的`computeTransactionAttribute`代码实现可以看出来，`@Transactional`注解定义在不同位置的 优先级为： **<font color="red">实列方法-->实列类-->接口方法-->接口类。</font>**  
不会取并集也不会覆盖， **按照优先级查找，直到找到为止。**

**小结：**
- **缓存：**  
  虽然解析注解属性不是特别耗时，但是也不能每次执行事务方法都要解析一次注解属性，所以在解析注解的时候`Spring`采用了缓存，这样就只需要一次解析注解，而后的每次执行都会存缓存中获取。  
  这是一个典型的 **拿空间换时间** 的列子。采用缓存的代码在其父类 `AbstractFallbackTransactionAttributeSource` 的`getTransactionAttribute`函数。

  注意：在使用缓存的时候难免遇到 **缓存穿透** 的现象，就是用`key`获取缓存的时候 **没有** 获取到对象，然后就直接去解析`@Transactional` ，结果发现还是没有；此后的每次调用都会持续这个现象，所以`Spring`在发现解析对象不存在的时候 就会定义一个特殊的 `value` 放到缓存中，以标识这个已经解析过了，确实不存在。

- **解析注解的时机：**  
  解析的时机是在`IOC`第一次初始化`Bean`的时候，具体点就是 **在为目标对象匹配增强器的时候，会触发注解解析。**

##### 5.1.2 获取事务管理器TransactionManager
**如果使用`@Transactional`指定了使用哪个事务管理器，就会获取相应的事务管理器。如果没有就从`IOC`容器中获取。**

首先介绍一下什么是事务管理器`TransactionManager`。  
它保存着当前的 **数据源连接** ，对外提供对该数据源的事务提交回滚操作接口，同时实现了事务相关操作的方法。一个数据源`DataSource`需要一个事务管理器（`org.springframework.jdbc.datasource.DataSourceTransactionManager`）。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring事务原理解析/Spring事务管理接口.png)
</center>

```java
// 核心属性：
private DataSource dataSource;

// 内部核心方法1（使用org.springframework.transaction.PlatformTransactionManager接口的实现方法）
public commit 提交事务
public rollback 回滚事务
public getTransaction 获得当前事务状态
    
// 内部核心方法2（实现org.springframework.transaction.support.AbstractPlatformTransactionManager抽象类的方法）
protected doSuspend 挂起事务
protected doBegin  开始事务
protected doCommit 提交事务
protected doRollback 回滚事务
protected doGetTransaction() 获取事务信息
    
// 内部核心方法3（使用org.springframework.transaction.support.DefaultTransactionStatus中的方法）  
final getTransaction 获取事务状态
```
再介绍一下`TransactionManager`是如何获取的：
1. 从注解中解析获得。
2. 如果注解中没有标明，则从容器中找到一个实现了`PlatformTransactionManager`接口的`Bean`。  
    **如果这种接口的`bean`有多个，同时没有使用`@Primary`标注的话，就会报错。**

**所以尽量在写`@Transactional`注解时指定`transactionManager`参数，以指定开启的是哪个库（数据库连接）的事务。否则当程序中有多个数据库连接时，如果使用了错误的事务管理器，会导致事务不生效。**

#### 5.2 开启事务
获取了事务定义信息（属性）和事务管理器之后，就可以调用`PlatformTransactionManager.getTransactional`方法开启事务了。  
但是开启事务时有很多情况需要考虑，如：繁多的事务传播行为、是否已经存在事务、不同的条件都会影响是否要开启一个新事务。有的传播行为还会涉及到 **挂起** 已经存在的事务等情况。

继续看上述`AOP`实现事务主流程中的第三步：`TransactionInfo txInfo = createTransactionIfNecessary(tm, txAttr, joinpointIdentification);`
```java
protected TransactionInfo createTransactionIfNecessary(
    PlatformTransactionManager tm, TransactionAttribute txAttr, final String joinpointIdentification) {

    // 采用委托的方式包装事务定义对象.
    if (txAttr != null && txAttr.getName() == null) {
        txAttr = new DelegatingTransactionAttribute(txAttr) {
            @Override
            public String getName() {
                return joinpointIdentification;
            }
        };
    }

    TransactionStatus status = null;
    if (txAttr != null) {
        if (tm != null) {
            //调用 事务管理器开启事务。
            status = tm.getTransaction(txAttr);
        }
        else {
            if (logger.isDebugEnabled()) {
                logger.debug("Skipping transactional joinpoint [" + joinpointIdentification +
                             "] because no transaction manager has been configured");
            }
        }
    }
    //封装成事务信息对象
    return prepareTransactionInfo(tm, txAttr, joinpointIdentification, status);
}
```

##### 5.2.1 获取事务状态（属性）
`org.springframework.transaction.support.AbstractPlatformTransactionManager#getTransaction`
```java
public final TransactionStatus getTransaction(TransactionDefinition definition) throws TransactionException {
    // 1. 获取事务对象（从线程绑定的信息中获取事务，抽象方法留给子类实现）
    Object transaction = doGetTransaction();
    // Cache debug flag to avoid repeated checks.
    // 缓存调试标志以避免重复检查。
    boolean debugEnabled = logger.isDebugEnabled();
    if (definition == null) {
        // Use defaults if no transaction definition given.
        // 如果没有给出事务定义，则使用默认值。
        definition = new DefaultTransactionDefinition();
    }
    // 2. 判断当前线程是否已经开启事务（存在事务）
    if (isExistingTransaction(transaction)) {
        // 2.1 已经开启（存在）事务，根据不同传播级别执行不同操作（创建事务或者加入事务）
        return handleExistingTransaction(definition, transaction, debugEnabled);
    }

    // 检查超时时间的设置是否合法
    if (definition.getTimeout() < TransactionDefinition.TIMEOUT_DEFAULT) {
        throw new InvalidTimeoutException("Invalid transaction timeout", definition.getTimeout());
    }

    // 3. 如果传播行为强制 PROPAGATION_MANDATORY ，则抛出异常
    if (definition.getPropagationBehavior() == TransactionDefinition.PROPAGATION_MANDATORY) {
        throw new IllegalTransactionStateException(
            "No existing transaction found for transaction marked with propagation 'mandatory'");
    }
    // 4. 开启新事务
    else if (definition.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRED ||
             definition.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRES_NEW ||
             definition.getPropagationBehavior() == TransactionDefinition.PROPAGATION_NESTED) {
        // 空挂起操作
        SuspendedResourcesHolder suspendedResources = suspend(null);
        if (debugEnabled) {
            logger.debug("Creating new transaction with name [" + definition.getName() + "]: " + definition);
        }
        try {
            boolean newSynchronization = (getTransactionSynchronization() != SYNCHRONIZATION_NEVER);
            // 4.1 获取事务状态 
            DefaultTransactionStatus status = newTransactionStatus(
                definition, transaction, true, newSynchronization, debugEnabled, suspendedResources);
            // 4.2 开启事务（抽象方法开启事务，留给子类实现）
            doBegin(transaction, definition);
            prepareSynchronization(status, definition);
            return status;
        }
        catch (RuntimeException ex) {
            resume(null, suspendedResources);
            throw ex;
        }
        catch (Error err) {
            resume(null, suspendedResources);
            throw err;
        }
    }
    // 5. 不运行在事务中，创建空事务。
    else {
        // Create "empty" transaction: no actual transaction, but potentially synchronization.
        if (definition.getIsolationLevel() != TransactionDefinition.ISOLATION_DEFAULT && logger.isWarnEnabled()) {
            logger.warn("Custom isolation level specified but no actual transaction initiated; " +
                        "isolation level will effectively be ignored: " + definition);
        }
        boolean newSynchronization = (getTransactionSynchronization() == SYNCHRONIZATION_ALWAYS);
        return prepareTransactionStatus(definition, null, true, newSynchronization, debugEnabled, null);
    }
}
```
这是一个模版方法，提供了两个抽象方法供子类实现。该方法主要逻辑：
1. 获得事务对象`DataSourceTransactionObject`。
2. 判断当前线程是否已经在事务中。
	如果已经在一个事务中，则调用`handleExistingTransaction`方法，根据不同的传播级别进行不同的操作。
3. 如果传播行为强制 `PROPAGATION_MANDATORY` ，则抛出异常
4. 如果不在一个事务中，则根据当前的传播行为判断是否开始新事务（传播行为是否为`PROPAGATION_REQUIRED`、`PROPAGATION_REQUIRED_NEW`、`PROPAGATION_NESTED`）。获取事务的状态，并开启事务。
5. 不运行在事务中，创建空事务。

下面详细分析每一个步骤。

###### 1). 获取事务对象
**第1步：获得事务对象`DataSourceTransactionObject`。**

`org.springframework.jdbc.datasource.DataSourceTransactionManager#doGetTransaction`
```java
@Override
protected Object doGetTransaction() {
    // 新建了一个事务对象
    DataSourceTransactionObject txObject = new DataSourceTransactionObject();
    txObject.setSavepointAllowed(isNestedTransactionAllowed());
    // 根据事务管理器中的数据源获取当前线程的事务数据库连接，如果当前线程不存在线程的话，这里返回的连接是空。
    ConnectionHolder conHolder =
        (ConnectionHolder) TransactionSynchronizationManager.getResource(obtainDataSource());
    txObject.setConnectionHolder(conHolder, false);
    return txObject;
}
```
注意到这里的`TransactionSynchronizationManager`这个类，这个类中记录了很多`Threadlocal`变量。文档说明是：
- Central delegate that manages resources and transaction synchronizations per thread.  
  管理每个线程的资源和事务同步的中央委托。
- To be used by resource management code but not by typical application code.  
  由资源管理代码使用，而不是由典型的应用程序代码使用。

这个类是每个线程事务同步管理的代理中心，用来管理事务用到的相关资源。这个类中（`org.springframework.transaction.support.TransactionSynchronizationManager`），事务组件之一。可以看到很多`Threadlocal`变量：
```java
/**
 * 记录了当前线程中的一些事务资源，已知的有根据DataSource作为key,数据库链接作为value，在执行doBegin操作时会写入新的键值对。
 */
// 应用代码随事务的声明周期绑定的对象
private static final ThreadLocal<Map<Object, Object>> resources =
    new NamedThreadLocal<>("Transactional resources");

// 使用的同步器，用于应用扩展
private static final ThreadLocal<Set<TransactionSynchronization>> synchronizations =
    new NamedThreadLocal<>("Transaction synchronizations");

// 当前事务的名称
private static final ThreadLocal<String> currentTransactionName =
    new NamedThreadLocal<>("Current transaction name");

// 事务是否是只读
private static final ThreadLocal<Boolean> currentTransactionReadOnly =
    new NamedThreadLocal<>("Current transaction read-only status");

// 当前事务的隔离级别
private static final ThreadLocal<Integer> currentTransactionIsolationLevel =
    new NamedThreadLocal<>("Current transaction isolation level");

// 是否实际的开启了事务，如果加入到别的事务，就不是实际开启事务
private static final ThreadLocal<Boolean> actualTransactionActive =
    new NamedThreadLocal<>("Actual transaction active");
```

###### 2).  判断当前线程是否已经开启事务
**第2步：判断当前线程是否已经在事务中。**

判断规则有两个，即当前线程的事务对象是否有`connectionHolder`，并且`connectionHolder`是否是事务激活状态。  
第一次进入事务方法时，`connectionHolder`是为空的。那么什么时候会不为空呢？`connectionHolder`什么时候激活事务呢？
```java
@Override
protected boolean isExistingTransaction(Object transaction) {
    DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
    return (txObject.hasConnectionHolder() &&
            txObject.getConnectionHolder().isTransactionActive());
}
```

###### 3). 如果当前线程已经存在事务
**第2.1步：如果已经在一个事务中，则调用`handleExistingTransaction`，根据不同的传播级别进行不同的操作。**

这里主要讨论常用的`REQUIRES_NEW`和`REQUIRED`的区别  
`org.springframework.transaction.support.AbstractPlatformTransactionManager#handleExistingTransaction`
```java
/**
 * Create a TransactionStatus for an existing transaction.
 */
private TransactionStatus handleExistingTransaction(
    TransactionDefinition definition, Object transaction, boolean debugEnabled)
    throws TransactionException {

    if (definition.getPropagationBehavior() == TransactionDefinition.PROPAGATION_REQUIRES_NEW) {
        if (debugEnabled) {
            logger.debug("Suspending current transaction, creating new transaction with name [" +
                         definition.getName() + "]");
        }
        // 挂起事务
        SuspendedResourcesHolder suspendedResources = suspend(transaction);
        try {
            boolean newSynchronization = (getTransactionSynchronization() != SYNCHRONIZATION_NEVER);
            DefaultTransactionStatus status = newTransactionStatus(
                definition, transaction, true, newSynchronization, debugEnabled, suspendedResources);
            doBegin(transaction, definition);
            prepareSynchronization(status, definition);
            return status;
        }
        catch (RuntimeException | Error beginEx) {
            resumeAfterBeginException(transaction, suspendedResources, beginEx);
            throw beginEx;
        }
    }
    //*****省略NESTED传播级别的部分代码,这里主要讨论PROPAGATION_REQUIRES_NEW和PROPAGATION_REQUIRED的区别
    return prepareTransactionStatus(definition, transaction, false, newSynchronization, debugEnabled, null);
}

```
从上面代码可以看到，当传播级别是`REQUIREDS_NEW`时，`Spring`会执行一个`suspend`操作，然后再创建一个新的`TransactionStatus`对象。即 **挂起当前事务开启一个新事务** 。  
然后对于传播级别`REQUIRED`时，则是直接返回，没有 **挂起** 和 **doBegin** 的操作。

**问题：** 当`A事务`调用`B事务`时，`B事务`的传播级别是`REQUIRED`，`B事务`肯定会加入`A事务`，那么此时事务的隔离级别是`B事务`设置的隔离级别还是`A事务`设置的隔离级别呢？为什么呢？  
**分析：** 当传播级别是`REQUIRED`时，会执行到`prepareTransactionStatus(definition, transaction, false, newSynchronization, debugEnabled, null);`方法。其中第三个参数`newTransaction`和第四个参数都是`false`，然后运行到后面的代码时，可以看到并不会进入将新的隔离级别设置到`Threadlocal`的操作。所以此时的隔离级别还是`A事务`的隔离级别。

`prepareSynchronization`的源码 `org.springframework.transaction.support.AbstractPlatformTransactionManager#prepareSynchronization`
```java
protected void prepareSynchronization(DefaultTransactionStatus status, TransactionDefinition definition) {
    // 第一次开启事务时会进入这里，Synchronization可以理解为一个同步作用域，
    // 后面就不会再进入了
    if (status.isNewSynchronization()) {
        TransactionSynchronizationManager.setActualTransactionActive(status.hasTransaction());
        TransactionSynchronizationManager.setCurrentTransactionIsolationLevel(
            definition.getIsolationLevel() != TransactionDefinition.ISOLATION_DEFAULT ?
            definition.getIsolationLevel() : null);
        TransactionSynchronizationManager.setCurrentTransactionReadOnly(definition.isReadOnly());
        TransactionSynchronizationManager.setCurrentTransactionName(definition.getName());
        TransactionSynchronizationManager.initSynchronization();
    }
}
```
同时，已经知道是在`doBegin`方法中执行了`begin`操作，由于`REQUIRED`传播级别是同一个事务，并没有执行额外的`doBegin`方法，因此一个事务在运行过程中是无法改变隔离级别的。

下面来看在`REQUIRED_NEW`的传播级别中，挂起事务这个操作具体做了什么。
```java
@Nullable
protected final SuspendedResourcesHolder suspend(@Nullable Object transaction) throws TransactionException {
	if (TransactionSynchronizationManager.isSynchronizationActive()) {
		List<TransactionSynchronization> suspendedSynchronizations = doSuspendSynchronization();
		try {
			Object suspendedResources = null;
			if (transaction != null) {
			    //1. 执行挂起操作
				suspendedResources = doSuspend(transaction);
			}
			// 2. 清空当前线程的事务配置
			String name = TransactionSynchronizationManager.getCurrentTransactionName();
			TransactionSynchronizationManager.setCurrentTransactionName(null);
			boolean readOnly = TransactionSynchronizationManager.isCurrentTransactionReadOnly();
			TransactionSynchronizationManager.setCurrentTransactionReadOnly(false);
			Integer isolationLevel = TransactionSynchronizationManager.getCurrentTransactionIsolationLevel();
			TransactionSynchronizationManager.setCurrentTransactionIsolationLevel(null);
			boolean wasActive = TransactionSynchronizationManager.isActualTransactionActive();
			TransactionSynchronizationManager.setActualTransactionActive(false);
			return new SuspendedResourcesHolder(
					suspendedResources, suspendedSynchronizations, name, readOnly, isolationLevel, wasActive);
		}
		catch (RuntimeException | Error ex) {
			// doSuspend failed - original transaction is still active...
			doResumeSynchronization(suspendedSynchronizations);
			throw ex;
		}
	}
	else if (transaction != null) {
		// Transaction active but no synchronization active.
		Object suspendedResources = doSuspend(transaction);
		return new SuspendedResourcesHolder(suspendedResources);
	}
	else {
		// Neither transaction nor synchronization active.
		return null;
	}
}

@Override
protected Object doSuspend(Object transaction) {
	DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
	txObject.setConnectionHolder(null);
	// 这个就是将DataSource-Connection这个键值对从Threadlocal中移除
	return TransactionSynchronizationManager.unbindResource(obtainDataSource());
}
```
从代码层面可以看到，`suspend`挂起事务，做的内容好像就是`doBegin`的逆向操作：清理当前线程绑定的一些信息，就像当前线程好像从来没有开启过事务一样。  
所以在`REQUIRES_NEW`传播级别下，它挂起了上一个事务，并开启了自己的新事务，同时执行了新的`doBegin`操作，开启了另外一个完全新的事务。

###### 4). 如果当前线程不存在事务则开启新事务
**第4步：如果不在一个事务中，则根据当前的传播行为判断是否开始新事务。**

首先要介绍一下事务状态`TransactionStatus`对象。  
`TransactionStatus`被用来做什么：`TransactionManager`对事务进行 **提交** 或 **回滚** 时需要用到该对象，记录了当前事务的上下文，主要包括：
1. 当前事务是否是一个新的事务还是加入别人的事务，事务传播级别`REQUIRED`和`REQUIRE_NEW`有用到。
2. 是否有`savepoint`。
3. 是否已经被设置了回滚标志位。回滚标志位的用途是子事务回滚时并不会真正回滚事务，而是设置一个回滚标志位，会根据相关事务的传播级别来决定何时回滚以及是否真正回滚。
4. 事务是否已经完成。

开启事务主要存在下面几步
1. 获得事务状态对象`TransactionStatus`
2. 执行`doBegin`操作（后续详细介绍）
3. 然后将当前事务的相关属性如隔离级别设置到`Threadlocal`中。

首先看获取的事务状态对象，它的构造函数：
```java
/**
 * Create a new {@code DefaultTransactionStatus} instance.
 * @param transaction underlying transaction object that can hold state
 * for the internal transaction implementation
 * @param newTransaction if the transaction is new, otherwise participating
 * in an existing transaction
 * @param newSynchronization if a new transaction synchronization has been
 * opened for the given transaction
 * @param readOnly whether the transaction is marked as read-only
 * @param debug should debug logging be enabled for the handling of this transaction?
 * Caching it in here can prevent repeated calls to ask the logging system whether
 * debug logging should be enabled.
 * @param suspendedResources a holder for resources that have been suspended
 * for this transaction, if any
 */
public DefaultTransactionStatus(
		@Nullable Object transaction, boolean newTransaction, boolean newSynchronization,
		boolean readOnly, boolean debug, @Nullable Object suspendedResources) {

	this.transaction = transaction;
	this.newTransaction = newTransaction;
	this.newSynchronization = newSynchronization;
	this.readOnly = readOnly;
	this.debug = debug;
	this.suspendedResources = suspendedResources;
}
```
构造函数这里的文档注释内容大致如下：
1. `transaction`是保存了内部事务实现的对象，这里通常是一个`DataSourceTransactionObject`类。
2. `newTransaction`：事务是否是新建的，否则加入到一个已经存在的事务。
3. `newSynchronization`：是否是新的同步器，这里通常是`false`，相当于有多少个`Threadlocal`管理的环境，通常都是一个。
4. 是否只读
5. `suspendedResources`：上一个被挂起的事务的相关信息，用于后面恢复挂起的事务。

在获取事务状态后，`transactionManager`会执行`doBegin`操作。`doBegin`操作主要做了`4`个事情：
1. 根据当前`transactionManager`保存的`DataSource`对象获取一个数据库连接`con`。
2. 设置隔离级别。
3. 执行`con.setAutoCommit(false)`，表示开启事务。
4. 将这个数据库连接`con`绑定到当前线程，绑定方式是将`DataSource`设置为`key`，数据库连接`con`为`value`，将这个键值对保存到`Threadlocal`中的一个`Map`中，即上面介绍的`resource`对象中。

**这里要思考，为什么`Spring`要以这种方式将数据库连接绑定到当前线程呢？为什么`key`是`DataSource`对象呢？**  
- 主要是了事务管理与数据访问服务的 **解耦** ；  
- 同时也保证了多线程环境下`connection`的线程安全问题。比如在写事务的时候，只需要指定`@Transactional`中的事务管理器`transactionManager`，这个事务管理器是一个单例对象，它的属性`DataSource`也是单例的，那么如何在多线程的情况下，如何让每个线程拥有自己的数据库连接呢？  
所以这里使用`Threadlocal`的方式，每个线程中存一份；同时业务代码里不需要关心数据库连接的创建问题。同时由于存在多个事务上下文切换的情况，需要有一个地方来安全地保留这些数据库连接。

执行完`doBegin`操作后，会将事务状态`TransactionStatus`，事务管理器`transactionManager`，事务属性`transactionAttrabute`，封装成一个`TransactionInfo`对象，同时这个对象还包含了上一个事务的事务信息。并且会把当前这个事务的事务信息存入`Threadlocal`中。

##### 5.2.2 doBegin方法
`DataSourceTransactionManager.doBegin`
```java
@Override
protected void doBegin(Object transaction, TransactionDefinition definition) {
    DataSourceTransactionObject txObject = (DataSourceTransactionObject) transaction;
    Connection con = null;

    try {
        // 如果当前不存在数据库 
        if (!txObject.hasConnectionHolder() ||
            txObject.getConnectionHolder().isSynchronizedWithTransaction()) {
            // 获取数据库连接，如果采用数据库连接池这里就是连接池对象。
            Connection newCon = this.dataSource.getConnection();
            // 设置连接到 事务对象中。
            txObject.setConnectionHolder(new ConnectionHolder(newCon), true);
        }

        txObject.getConnectionHolder().setSynchronizedWithTransaction(true);

        con = txObject.getConnectionHolder().getConnection();
        // 记录上一个 事务的隔离级别 ，如果没有外层事务 ，隔离级别就是null
        Integer previousIsolationLevel = DataSourceUtils.prepareConnectionForTransaction(con, definition);
        txObject.setPreviousIsolationLevel(previousIsolationLevel);

        //设置自动提交 为false,如果使用 连接池,连接池 或许已经设置自动提交为false了，所以这里先判断一下。
        if (con.getAutoCommit()) {
            txObject.setMustRestoreAutoCommit(true);
            if (logger.isDebugEnabled()) {
                logger.debug("Switching JDBC Connection [" + con + "] to manual commit");
            }
            con.setAutoCommit(false);
        }
        // 如果事务是只读事务 ，那么就会执行 SQL "SET TRANSACTION READ ONLY".
        prepareTransactionalConnection(con, definition);
        txObject.getConnectionHolder().setTransactionActive(true);

        int timeout = determineTimeout(definition);
        if (timeout != TransactionDefinition.TIMEOUT_DEFAULT) {
            txObject.getConnectionHolder().setTimeoutInSeconds(timeout);
        }

        // 如果是一个新的连接 ，绑定数据库连接到当前线程
        if (txObject.isNewConnectionHolder()) {
            // 调用 事务同步回调管理器 的 绑定资源方法，key= dataSource ,key = ConnectionHodler
            TransactionSynchronizationManager.bindResource(getDataSource(), txObject.getConnectionHolder());
        }
    }
    catch (Throwable ex) {
        if (txObject.isNewConnectionHolder()) {
            //异常之后 释放连接，
            DataSourceUtils.releaseConnection(con, this.dataSource);
            txObject.setConnectionHolder(null, false);
        }
        throw new CannotCreateTransactionException("Could not open JDBC Connection for transaction", ex);
    }
}
```
这里是实际获取数据库连接开启事务的地方，从`DataSource` 中获取连接，并且设置自动提交为`false`,
1. 获取数据库连接
2. 设置数据库连接自动提交为`false`，开启事务
3. 绑定数据库连接到线程

##### 5.2.3 事务挂起
当线程中已经存在事务,在某些事务传播行为下就需要挂起外层事务，
- `PROPAGATION_NOT_SUPPORTED`：不能运行在一个事务中，如果存在事务就挂起当前事务，执行。
- `PROPAGATION_REQUIRES_NEW`： 必须运行在一个新事务中，如果当前存在事务，则挂起当前事务，开启新事务执行。

如何实现挂起一个事务呢？挂起事务需要完成几项工作：
1. 在`TransactionSynchronizationManager` 中解除绑定的 `TransactionSynchronization` 集合
2. 重置事务名称绑定
3. 重置事务只读属性绑定
4. 重置事务隔离级别绑定
5. 重置事务激活标志绑定
6. 记录以上几步的数据，封装到 `SuspendedResourceHolder`对象中。
7. 将`SuspendedResourceHolder`对象，交给内部事务，以便内部事务执行结束后，恢复外层事务。

##### 5.2.4 事务恢复
如果 **内部事务出现异常** 或者 **内部事务完成提交** 都会触发外层事务的恢复；  
事务的恢复就是将内存事务`TransactionStauts` 中记录的挂起事务的信息，重新绑定到 `TransactionSynchronizationManager`中去。

#### 5.3 事务回滚
前面`AOP`实现事务的主流程中可以看到：假如被拦截方法没有抛出异常，则会执行`commitTransactionAfterReturning`方法（在 **5. 事务实现--AOP实现事务的主流程中的第7步** ）并最终进入到事务管理器中的`commit`方法。可以看到，当代码进入这里时，并不意味着事务会提交，也可能会执行回滚。

如果事务运行过程中出现某些异常会导致事务回滚，在`JDBC`中 执行`connection.rollback()`回滚事务；  
`Spring`事务也不例外，只是`Spring事务` 在`JDBC` 的基础之上提供了更多丰富的功能， **比如指定某些异常进行回滚。**

关于事务回滚`rollback`设置，还有一个容易被忽视和误解的地方：   
**就是如果设置`rollbackFor = IllegalArgumentException.class`（非法参数异常）那么事务运行期间出现了`IndexOutOfBoundsException`异常（索引溢出）会不会导致事务回滚？出现了`Error`错误会不会回滚？** 

处理事务回滚的在`TransactionAspectSupport.completeTransactionAfterThrowing` 函数中。
1. 首先判断异常是否需要回滚。判断逻辑最终是委托给 `org.springframework.transaction.interceptor.RuleBasedTransactionAttribute#rollbackOn`
   ```java
   public boolean rollbackOn(Throwable ex) {
       RollbackRuleAttribute winner = null;
       int deepest = Integer.MAX_VALUE;
       if (this.rollbackRules != null) {
           //遍历 查找 指定的 rollbackException　进行匹配
           for (RollbackRuleAttribute rule : this.rollbackRules) {
               int depth = rule.getDepth(ex);
               if (depth >= 0 && depth < deepest) {
                   deepest = depth;
                   winner = rule;
               }
           }
       }
   
       // 如果没有匹配到 采用默认的回滚规则进行判断。
       // 默认的规则就是 ex instanceof RuntimeException || ex instanceof Error，所以 如果指定了rollback = IllegalArgumentException，当遇到 IndexOutOfBoundsException时 或者 Error 时也会回滚事务。
       if (winner == null) {
           logger.trace("No relevant rollback rule found: applying default rules");
           return super.rollbackOn(ex);
       }
   
       return !(winner instanceof NoRollbackRuleAttribute);
   }
   ```

2. 如果需要回滚则会执行 `org.springframework.transaction.support.AbstractPlatformTransactionManager#processRollback`函数：
   - 2.1. 如果存在保存点则回滚到保存点
   - 2.2. 如果是一个新事务则执行回滚。
   - 2.3. 如果是嵌套事务设置当前数据库链接`rollbackOnly`
   - 2.4. 如果未设置回滚的异常，则会默认捕获`RuntimeException`和`Error`

   ```java
   private void processRollback(DefaultTransactionStatus status, boolean unexpected) {
       try {
           boolean unexpectedRollback = unexpected;
           try {
               triggerBeforeCompletion(status);
               // 1.  如果存在保存点 则回滚到 保存点
               if (status.hasSavepoint()) {
                   if (status.isDebug()) {
                       logger.debug("Rolling back transaction to savepoint");
                   }
                   status.rollbackToHeldSavepoint();
               }
               // 2. 如果 是一个新事务 执行回滚。
               else if (status.isNewTransaction()) {
                   if (status.isDebug()) {
                       logger.debug("Initiating transaction rollback");
                   }
                   doRollback(status);
               }
               else {
                   // Participating in larger transaction
                   // 3. 如果 是嵌套事务 设置 当前数据库链接 rollbackOnly
                   if (status.hasTransaction()) {
                       if (status.isLocalRollbackOnly() || isGlobalRollbackOnParticipationFailure()) {
                           if (status.isDebug()) {
                               logger.debug("Participating transaction failed - marking existing transaction as rollback-only");
                           }
                           doSetRollbackOnly(status);
                       }
                       else {
                           if (status.isDebug()) {
                               logger.debug("Participating transaction failed - letting transaction originator decide on rollback");
                           }
                       }
                   }
                   else {
                       logger.debug("Should roll back transaction but cannot - no transaction available");
                   }
                   // Unexpected rollback only matters here if we're asked to fail early
                   if (!isFailEarlyOnGlobalRollbackOnly()) {
                       unexpectedRollback = false;
                   }
               }
           }
           // 4. 如果未设置回滚的异常，则会默认捕获RuntimeException和Error
           catch (RuntimeException | Error ex) {
               triggerAfterCompletion(status, TransactionSynchronization.STATUS_UNKNOWN);
               throw ex;
           }
   
           triggerAfterCompletion(status, TransactionSynchronization.STATUS_ROLLED_BACK);
   
           // Raise UnexpectedRollbackException if we had a global rollback-only marker
           if (unexpectedRollback) {
               throw new UnexpectedRollbackException(
                   "Transaction rolled back because it has been marked as rollback-only");
           }
       }
       finally {
        cleanupAfterCompletion(status);
       }
   }
   ```
3. 如果不需要回滚则提交事务
4. 触发钩子函数：
    在回滚前后会分别触发 `org.springframework.transaction.support.TransactionSynchronization`的`beforeCompletion`和`afterCompletion`函数，进行资源释放，以及连接关闭等。

#### 5.4 事务提交
只有当事务是一个新事务的时候才会进行提交。  
也就是说如果有一个内嵌事务且传播行为是`PROPAGATION_SUPPORTS` 、`PROPAGATION_REQUIRED` 、`PROPAGATION_MANDATORY`  的事务执行完之后是不会提交的，它只会会随着外层事务的提交而提交 **（所以子事务提交并不会真正提交MySQL事务）** 。

**事务的提交最终是调用 `connect.commit` 函数提交事务。**

在事务提交前后也会分别触发 `org.springframework.transaction.support.TransactionSynchronization`的`beforeCompletion`（其中`mybatis`会在`beforeCommit`中执行`Sqlsession commit`），`afterCompletion`函数，进行资源释放，连接关闭等。

## 三、Spring事务相关补充
### 1. Spring事务和MySQL存储引擎Innodb事务的区别
参考其他笔记：[数据库事务和框架（Spring）事务的区别和联系](https://xieruhua.gitee.io/javalearning/#/./%E6%95%B0%E6%8D%AE%E5%BA%93/%E6%95%B0%E6%8D%AE%E5%BA%93%E4%BA%8B%E5%8A%A1%E5%92%8C%E6%A1%86%E6%9E%B6%EF%BC%88Spring%EF%BC%89%E4%BA%8B%E5%8A%A1%E7%9A%84%E5%8C%BA%E5%88%AB%E5%92%8C%E8%81%94%E7%B3%BB)

### 2. Spring如何使用Threadlocal管理连接
`Spring`为什么要用这些`Threadlocal`变量（见 **二.4.6节：TransactionSynchronizationManager事务同步回调的管理器** ）

目前只看到设置和清空，没看到在哪用？？

初步设想：  
每次执行一条`SQL`时，都需要一个`connection`对象，隔离级别等配置都是配置在一个指定的`connection`连接上的。就算使用`mybatis`，底层也是`jdbc`，也需要一个`connection`对象，那它具体用哪个对象呢？肯定不能从连接池里随便拿一个。  
`Spring`框架不应该干扰业务，所以这里`Spring`应该是通过`Threadlocal`来指定用哪一个连接来执行方法里的SQL的。  
下一步则需要看一下`mybatis`执行`sql`时是如何获取数据库连接的，是否与`Spring`之间有一定的交互。

首先定位到`mybatis`的获取连接的地方：`BaseExecutor`类。通过`transaction`对象获取连接，然后再定位`transaction`是如何获得的。`org.apache.ibatis.executor.BaseExecutor#getConnection`
```java
protected Connection getConnection(Log statementLog) throws SQLException {
    Connection connection = transaction.getConnection();
    if (statementLog.isDebugEnabled()) {
        return ConnectionLogger.newInstance(connection, statementLog, queryStack);
    } else {
        return connection;
    }
}
```
最终定位到`SpringManagedTransactionFactory`类中，这个类是在`org.mybatis.spring.transaction;`包里，说明这是`mybatis`专门为了接入`Spring`来做的一个功能。

`org.mybatis.spring.transaction.SpringManagedTransactionFactory#newTransaction(java.sql.Connection)`
```java
@Override
public Transaction newTransaction(DataSource dataSource, TransactionIsolationLevel level, boolean autoCommit) {
    return new SpringManagedTransaction(dataSource);
}
```

所以获取连接的方法就在`SpringManagedTransaction`类中。因此可以猜想，`mybatis-spring`获取数据库连接的方式，可能是之前讨论的从`Threadlocal`里面获取的！  
然后定位到获取设置连接的方法：
这里使用了`DataSourceUtils`类，这个是`org.springframework.jdbc.datasource;`包中的一个类，是`Spring`对`jdbc`的一个封装：
```java
private void openConnection() throws SQLException {
    this.connection = DataSourceUtils.getConnection(this.dataSource);
    this.autoCommit = this.connection.getAutoCommit();
    this.isConnectionTransactional = DataSourceUtils.isConnectionTransactional(this.connection, this.dataSource);

    if (LOGGER.isDebugEnabled()) {
        LOGGER.debug(
            "JDBC Connection ["
            + this.connection
            + "] will"
            + (this.isConnectionTransactional ? " " : " not ")
            + "be managed by Spring");
    }
}
```

下面看到真正获取数据库连接的地方`DataSourceUtils`类，这时候已经进入了`Spring`相关的代码：
```java
public static Connection doGetConnection(DataSource dataSource) throws SQLException {
    Assert.notNull(dataSource, "No DataSource specified");
    // 从当前线程中获取数据库连接
    ConnectionHolder conHolder = (ConnectionHolder) TransactionSynchronizationManager.getResource(dataSource);
    if (conHolder != null && (conHolder.hasConnection() || conHolder.isSynchronizedWithTransaction())) {
        conHolder.requested();
        if (!conHolder.hasConnection()) {
            logger.debug("Fetching resumed JDBC Connection from DataSource");
            conHolder.setConnection(dataSource.getConnection());
        }
        return conHolder.getConnection();
    }
    // Else we either got no holder or an empty thread-bound holder here.

    logger.debug("Fetching JDBC Connection from DataSource");
    Connection con = dataSource.getConnection();
    // 如果当前线程支持同步，已经开启了一个事务
    if (TransactionSynchronizationManager.isSynchronizationActive()) {
        logger.debug("Registering transaction synchronization for JDBC Connection");
        // Use same Connection for further JDBC actions within the transaction.
        // Thread-bound object will get removed by synchronization at transaction completion.
        ConnectionHolder holderToUse = conHolder;
        if (holderToUse == null) {
            holderToUse = new ConnectionHolder(con);
        }
        else {
            holderToUse.setConnection(con);
        }
        holderToUse.requested();
        TransactionSynchronizationManager.registerSynchronization(
            new ConnectionSynchronization(holderToUse, dataSource));
        holderToUse.setSynchronizedWithTransaction(true);
        if (holderToUse != conHolder) {
            // 绑定到当前线程
            TransactionSynchronizationManager.bindResource(dataSource, holderToUse);
        }
    }
    return con;
}
```
果然，到最后还是看到了`TransactionSynchronizationManager`类（ **二.4.6节：TransactionSynchronizationManager事务同步回调的管理器** ），它将一个以`DataSource`为`key`，`Connection`为`value`的一个`Map`存放到`Threadlocal`中，也就意味着同一个线程的同一个`DataSource`一定只会取到同一个连接。  
所以如果想写一个类似`mybatis`的框架来接入`Spring`事务管理，是需要在获取数据库连接这一块使用`Spring`的数据库连接管理的，也就是这种采用`Threadlocal`的方式。

**总结：**  
综上所述，`Spring`采用`Threadlocal`的方式，来保证线程中的数据库操作使用的是同一个数据库连接。
同时，采用这种方式可以使业务层使用事务时不需要感知并管理`connection`对象。通过传播级别，巧妙地管理多个事务配置之间的切换、挂起和恢复。

### 3. Spring事务使用的注意事项
#### 3.1 为什么事务不生效
1. 没有指定`rollbackFor`参数默认只会捕获`RuntimeException`来进行回滚。
2. 没指定`transactionManager`参数，默认的`transactionManager`可能并不是你期望的，以及一个事务中涉及到了多个数据库。
3. 对象内部方法互相调用不会被`Spring AOP`拦截，`@Transactional注解`无效，可以使用`AopContext.currentProxy()`获取代理对象，然后用代理对象调用内部方法来解决。
4. 如果`AOP`使用了`CGLIB`代理，同时事务方法或者类不是`public`，无法被外部包访问到；或者是`final`无法继承，`@transactional注解`无效。

如果一定要解决上述`3`的情况，可以使用`AopContext.currentProxy()`方法获取当前的代理对象，然后执行代理对象的方法。并且要把`expose-proxy`配置置为`true`，表示暴露代理对象到当前`Threadlocal`变量中。  
**不过通常还是不建议这么用，除非不得已而为之。因为这样很不`“AOP”`，业务代码感知到`AOP`的存在还要去感知`代理对象`的存在。**

#### 3.2 事务执行异常
1. **采用了不恰当的传播级别** ，不会造成事务不生效，但是会造成事务的回滚和提交出乎意料，隔离级别可能会被父事务覆盖。
2. **采用了不恰当的隔离级别** ，导致数据访问出乎意料，如循环`cas`操作却使用默认隔离级别（可重复读），导致每次`cas`读取一样无法更新记录。

### 4. 其他补充
1. 方法上面 `@Transaction` 注解会覆盖类上面的`@Transaction`注解信息。是完全的覆盖，而不是部分覆盖。  
也就是说，如果类上设置了事务超时时间为`10`秒，但是方法上面没有设置事务超时时间，那么最终事务就是没有超时时间，并不会采用 类上面的超时时间。
2. `事务隔离级别` 和 `超时时间` 只能作用于一个新事务。  
也就是说，当内部事务参与到一个已经存在的事务中时，`事务隔离级别` 和 `超时时间`将会被忽略。因为内部事务是参与到外层事务的。
3. 事务`rollbackFor`的含义是`默认异常`或`指定异常`。  
也就是说，回滚的是 `runtimeException` 或 `Error` 或 `自己指定的异常`。
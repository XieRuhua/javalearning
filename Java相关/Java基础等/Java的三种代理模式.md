## Java的三种代理模式
[笔记内容参考1：基于 JDK 的动态代理机制](https://www.cnblogs.com/yangming1996/p/9254412.html)  
[笔记内容参考2：【Spring基础】JDK动态代理实现原理(jdk8)](https://blog.csdn.net/yhl_jxy/article/details/80586785)  
[笔记内容参考3：【Spring基础】CGLIB动态代理实现原理](https://blog.csdn.net/yhl_jxy/article/details/80633194)  

[toc]
#### 静态代理
```java
public interface IService {
    void sayHello();
}
```

```java
public class RealClass implements IService {
    @Override
    public void sayHello() {
        System.out.println("hello word..........");
    }

    public void doService() {
        System.out.println("doing service..........");
    }
}
```

```java
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

    public void doService() {
        System.out.println("doService proxy begin");
        realClass.doService();
        System.out.println("doService proxy end");
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
        proxyClass.doService();
    }
}
```
打印：
```
hello proxy begin
hello word..........
hello proxy end
doService proxy begin
doing service..........
doService proxy end
```
**静态代理总结:**  
1. 可以做到在不修改目标对象的功能前提下，对目标功能扩展。  
2. 缺点:  
因为代理对象需要与目标对象实现一样的接口，所以会有很多代理类，类太多。同时，一旦接口增加方法，目标对象与代理对象都要维护。

动态代理即可解决静态代理的缺点。

#### 动态代理-JDK
```java
public class MyHandler implements InvocationHandler {
    private Object realObj;

    public MyHandler(Object realObj) {
        this.realObj = realObj;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("jdk dynamic proxy begin");
        Object result = method.invoke(realObj, args);
        System.out.println("jdk dynamic proxy end");
        return result;
    }
}
```

```java
public class MainTest {
    public static void main(String[] args){
        RealClass realClass = new RealClass();
        
        // dynamic proxy
        MyHandler handler = new MyHandler(realClass);
        Object obj = Proxy.newProxyInstance(
                realClass.getClass().getClassLoader(),
                new Class[]{IService.class},
                handler
        );
        IService iService = (IService) obj;
        iService.sayHello();
    }
}
```
打印：
```
jdk dynamic proxy begin
hello word..........
jdk dynamic proxy end
```
**动态代理-JDK总结：**  
代理对象不需要实现接，但是目标对象一定要实现接口，否则不能用动态代理

#### 动态代理-CGLib

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
import net.sf.cglib.proxy.MethodInterceptor;
import net.sf.cglib.proxy.MethodProxy;

import java.lang.reflect.Method;

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
可以看出HelloService$sayOthers()方法并没有被代理，因为final修饰的方法无法被重写覆盖。

**动态代理-CGLib总结：**  
目标对象只是一个单独的对象，并不需要实现任何的接口,此时以目标对象子类（继承）的方式类实现动态代理。

#### 静态代理和动态代理的对比
* **灵活性：** 动态代理更加灵活，不需要必须实现接口，可以直接代理实现类，并且可以不需要针对每个目标类都创建一个代理类。另外，静态代理中，接口一旦新增加方法，目标对象和代理对象都要进行修改，这是非常麻烦的！
* **JVM 层面 ：** 静态代理在编译时就将接口、实现类、代理类这些都变成了一个个实际的 class 文件。而动态代理是在运行时动态生成类字节码，并加载到 JVM 中的。

#### JDK 动态代理和 CGLIB 动态代理对比  
* JDK 动态代理只能代理实现了接口的类或者直接代理接口  
* CGLIB 动态代理是通过生成一个被代理类的子类（继承）来拦截被代理类的方法调用，因此无法对static、final类进行代理  
* CGLIB 也无法对private、static方法进行代理

就二者的效率来说，大部分情况都是 JDK 动态代理更优秀，随着 JDK 版本的升级，这个优势更加明显。

<font color="red">**补充：Spring AOP默认采用JDK动态代理，如果被代理对象没有实现任何接口，则默认是CGLIB**</font>    
强制使用CGLIB代理的方法：**指定proxy-target-class = "true"** 或者 **基于注解@EnableAspectJAutoProxy(proxyTargetClass = true)**


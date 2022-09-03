# Spring核心之控制反转（IOC）

[笔记内容参考1：浅谈对Spring IOC以及DI的理解](https://blog.csdn.net/luoyepiaoxue2014/article/details/72426666)  
[笔记内容参考2：Spring基础 - Spring核心之控制反转(IOC)](https://pdai.tech/md/spring/spring-x-framework-ioc.html)

> Spring 版本 Spring-5.0.8.RELEASE

[toc]

## 一、Spring简介
### 1. Spring是什么
`Spring`是分层的 `Java SE/EE` 应用 `full-stack`（全栈）轻量级开源框架，以 **`IOC`（Inverse Of Control：反转控制）** 和 **`AOP`（Aspect Oriented Programming：面向切面编程）** 为内核。

提供了 **展现层`SpringMVC`** 和 **持久层`Spring JDBCTemplate`** 以及 **业务层事务管理** 等众多的企业级应用整合技术，还能整合开源世界众多著名的第三方框架和类库，已成为使用最多的`Java EE` 企业应用开源框架。

### 2. Spring的优势
1. **方便解耦，简化开发**  
   通过 `Spring` 提供的 `IOC容器`，可以将对象间的依赖关系交由 `Spring` 进行控制，避免硬编码所造成的过度耦合。用户也不必再为单例模式类、属性文件解析等这些很底层的需求编写代码，可以更专注于上层的应用。
2. **AOP 编程的支持**  
   通过 `Spring`的 `AOP` 功能，方便进行面向切面编程，许多不容易用传统 `OOP` 实现的功能可以通过 `AOP` 轻松实现。
3. **声明式事务的支持**  
   可以将我们从单调烦闷的事务管理代码中解脱出来，通过声明式方式灵活的进行事务管理，提高开发效率和质量。
4. **方便程序的测试**  
   可以用非容器依赖的编程方式进行几乎所有的测试工作，测试不再是昂贵的操作，而是随手可做的事情。
5. **方便集成各种优秀框架**  
   `Spring`对各种优秀框架（`Struts`、`Hibernate`、`Hessian`、`Quartz`等）的支持。
6. **降低 JavaEE API 的使用难度**  
   `Spring`对 `JavaEE API`（如 `JDBC`、`JavaMail`、`远程调用`等）进行了薄薄的封装层，使这些 `API` 的使用难度大为降低。
7. **源码是经典学习范例**  
   `Spring`的源代码设计精妙、结构清晰、匠心独用，处处体现着大师对`Java` 设计模式灵活运用以及对 `Java`技术的高深造诣。它的源代码无意是 `Java` 技术的最佳实践的范例。

## 二、IOC和DI
### 1. Spring Bean是什么
在 `Spring` 中，构成应用程序的基础并由 `Spring IOC` 容器管理的对象称为 `beans`。 **每个`bean` 是由 `Spring IOC` 容器实例化、组装和管理的对象**。

### 2. IOC是什么？
**`IOC`，全称`Inversion of Control`，意为控制反转。这是`Spring`的核心，贯穿始终。**

#### 2.1 简介
以前传统应用程序都是由开发者在类内部主动创建依赖对象，而`IOC`容器将创建和查找类依赖对象的控制权交给了容器，由容器进行注入组合对象，对于`Spring`框架来说，就是由`Spring`来负责控制对象的生命周期和对象间的关系。简而言之，**获得依赖对象的过程被反转了（将原本在程序中手动创建对象的控制权，交由`Spring`框架来管理）**。

**<font color="red">注意：IOC不是一种技术，只是一种思想，一个重要的面向对象编程的法则，它能指导我们如何设计出松耦合、更优良的程序。</font>**

#### 2.2 举例说明
假设整个婚恋市场为一个程序，每个人就是一个独立的对象（类）。那每个个体是如何找男/女朋友的？常见的情况是，自己找到自己喜欢的，然后打听对方的兴趣爱好、约会等，这个过程必须自己设计和控制每个环节。
以往传统的程序开发也是如此，在一个对象中，如果要使用另外的对象，就必须先得到它（自己`new`一个），使用完之后还要主动将对象销毁。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之控制反转（IOC）/普通的对象创建过程.png)
</center>

**那么`IOC`是如何做的呢？有点类似在男女之间引入了一个第三者：婚姻介绍所。**  
婚介管理了很多男女的资料，每个人可以向婚介提出一个要求的列表，告诉它想找个什么样的男/女朋友，然后婚介就会按照要求提供，只需要去和对方约会、谈恋爱就行了。简单明了，而且如果婚介的人选不符合要求，就会抛出异常。整个获取男/女朋友（对象）信息的过程不再由自己控制，而是有婚介这样一个类似容器的机构来控制。  
`Spring`所倡导的开发方式就是如此，所有的类都会在`Spring`容器中创建，将自己也交给`Spring`创建并在程序中告诉`Spring`你需要什么对象，然后`Spring`会在系统运行到适当的时候，把你要的对象主动给你，同时也会把你交给其他需要你的对象中。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之控制反转（IOC）/IOC的对象创建过程.png)
</center>

所有的类的创建、销毁都由 `Spring`来控制，也就是说控制对象生存周期的不再是引用它的对象，而是`Spring`。对于某个具体的对象而言，以前是它控制其他对象，现在是所有对象都被`Spring`控制，这就叫 **控制反转** 。

#### 2.3 IOC的意义
传统应用程序都是由我们在类内部主动创建依赖对象，从而导致类与类之间高耦合，难于测试和维护；  
有了`IOC`容器后，把创建和查找依赖对象的控制权交给了容器，由容器进行注入组合对象，所以对象与对象之间是松散耦合，这样也方便测试，利于功能复用，更重要的是使得程序的整个体系结构变得非常灵活。

### 3. DI是什么？
**`DI`，全称`Dependency Injection`，意为依赖注入；它是一种过程，或者说它给出了实现`IOC`的方法，即由`IOC`容器在运行期间，动态的将某种依赖关系注入到对象之中。**

#### 3.1 简介
`IOC`的一个重点是在系统运行中，动态的向某个对象提供它所需要的其他对象。这一点是通过 **`DI`（Dependency Injection，依赖注入）** 来实现的。

依赖注入是组件之间依赖关系由容器在运行期决定，形象的说，即由容器动态的将某个依赖关系注入到组件之中。  
依赖注入的目的并非为软件系统带来更多功能，而是为了提升组件重用的频率，并为系统搭建一个灵活、可扩展的平台。  
通过依赖注入机制，我们只需要通过简单的配置，而无需任何代码就可指定目标需要的资源，完成自身的业务逻辑，而不需要关心具体的资源来自何处，由谁实现。

理解`DI`的关键是： **“谁依赖谁，为什么需要依赖，谁注入谁，注入了什么”：**
- **谁依赖于谁** ：当然是应用程序依赖于`IOC`容器；
- **为什么需要依赖** ：应用程序需要`IOC`容器来提供对象需要的外部资源；
- **谁注入谁** ：很明显是`IOC`容器注入应用程序某个对象，应用程序依赖的对象；
- **注入了什么** ：就是注入某个对象所需要的外部资源（包括对象、资源、常量数据）。

那么DI是如何实现的呢？`Java 1.3`之后一个重要特征是 **反射（`reflection`）** ，其实DI的底层实现是依赖`Java`的反射机制来做的，反射允许程序在运行的时候 **动态的生成对象** 、 **执行对象的方法** 、 **改变对象的属性** 。

#### 3.2 举例说明
存在一个`对象A`需要读取数据库信息，以前我们需要在`对象A`中自己编码来获得一个`Connection`对象，而有了 `IOC`容器之后，我们就只需要告诉它，`对象A`中需要一个`Connection`，在`IOC`容器运行时，它会在适当的时候创建一个`Connection`，然后注入到`对象A`当中，这样就完成了对各个对象之间关系的控制。

### 4. IOC和DI小结
- **IOC：控制反转** ，将对象的创建权由`Spring`管理，所有的类不需要自己去创建，`Spring`可以帮你创建。
- **DI：依赖注入** ，在我们创建对象的过程中，把对象依赖的属性注入到我们的类中。

**IOC和DI是什么关系呢？**  
- `IOC`是一种思想，`DI`是一种行为（实现这种思想的具体方式）。
- 另一种说法是，`IOC`是目的，`DI`是手段。`IOC`是指让生成类的方式由传统方式（`new`）反过来，既程序不调用`new`，需要类的时候由框架注入（`DI`），是同一种实现的不同层面的解读。

## 三、IOC 配置的三种方式
### 1. xml 配置
顾名思义，就是将`bean`的信息配置`.xml`文件里，通过`Spring`加载文件为我们创建`bean`。这种方式出现很多早前的`SSM`项目中，将第三方类库或者一些配置工具类都以这种方式进行配置，主要原因是由于第三方类不支持`Spring`注解。
- **优点**： 可以使用于任何场景，结构清晰，通俗易懂。
- **缺点**： 配置繁琐，不易维护，枯燥无味，扩展性差。

**举例**：
1. 配置`xx.xml`文件
2. 声明命名空间和配置`bean`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
                           http://www.springframework.org/schema/beans/spring-beans.xsd">
    <!-- services -->
    <bean id="userService" class="tech.pdai.springframework.service.UserServiceImpl">
        <property name="userDao" ref="userDao"/>
        <!-- additional collaborators and configuration for this bean go here -->
    </bean>
    <!-- more bean definitions for services go here -->
</beans>
```

### 2. Java 配置
将类的创建交给我们配置的`JavcConfig`类来完成，`Spring`只负责维护和管理，采用纯`Java`创建方式。其本质上就是把在`XML`上的配置声明转移到`Java`配置类中
- **优点**：适用于任何场景，配置方便，因为是纯`Java`代码，扩展性高，十分灵活。
- **缺点**：由于是采用`Java`类的方式，声明不明显，如果大量配置，可读性比较差。

**举例**：
1. 创建一个配置类， 添加`@Configuration`注解声明为配置类
2. 创建方法，方法上加上`@bean`，该方法用于创建实例并返回，该实例创建后会交给`Spring`管理，方法名建议与实例名相同（首字母小写）。 **注：实例类不需要加任何注解**

```java
@Configuration
public class BeansConfig {
    /**
     * @return user dao
     */
    @Bean("userDao")
    public UserDaoImpl userDao() {
        return new UserDaoImpl();
    }

    /**
     * @return user service
     */
    @Bean("userService")
    public UserServiceImpl userService() {
        UserServiceImpl userService = new UserServiceImpl();
        userService.setUserDao(userDao());
        return userService;
    }
}
```

### 3. 注解配置
通过在类上加注解的方式，来声明一个类交给`Spring`管理，`Spring`会自动扫描带有`@Component`、`@Controller`、`@Service`、`@Repository`这四个注解的类，然后帮我们创建并管理，前提是需要先配置`Spring`的注解扫描器。
- **优点**：开发便捷，通俗易懂，方便维护。
- **缺点**：具有局限性，对于一些第三方资源，无法添加注解。只能采用`XML`或`JavaConfig`的方式配置

**举例**：
1. 对类添加`@Component`相关的注解，比如`@Controller`、`@Service`、`@Repository`
2. 设置`ComponentScan`的`basePackage`。如：`<context:component-scan base-package='tech.pdai.springframework'>`, 或者`@ComponentScan("tech.pdai.springframework")`注解，或者 `new AnnotationConfigApplicationContext("tech.pdai.springframework")`指定扫描的`basePackage`。

```java
@Service
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    @Autowired
    private UserDaoImpl userDao;

    /**
     * find user list.
     * @return user list
     */
    public List<User> findUserList() {
        return userDao.findUserList();
    }
}
```

## 四、依赖注入（DI）的三种方式
> 常用的注入方式主要有三种：构造方法注入（`Construct`注入）、`setter`注入、基于注解的注入（接口注入）

### 1. setter方式
- **在`XML`配置方式中** ，`property`都是`setter`方式注入，比如下面的`xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
                           http://www.springframework.org/schema/beans/spring-beans.xsd">
    <!-- services -->
    <bean id="userService" class="tech.pdai.springframework.service.UserServiceImpl">
        <property name="userDao" ref="userDao"/>
        <!-- additional collaborators and configuration for this bean go here -->
    </bean>
    <!-- more bean definitions for services go here -->
</beans>
```
本质上包含两步：  
第一步：需要`new UserServiceImpl()`创建对象，所以需要默认构造函数；  
第二步：调用`setUserDao()`函数注入`userDao`的值, 所以需要`setUserDao()`函数。

    所以对应的`service`类是这样的：
```java
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    private UserDaoImpl userDao;

    /**
     * init.
     */
    public UserServiceImpl() {
    }

    /**
     * find user list.
     * @return user list
     */
    public List<User> findUserList() {
        return this.userDao.findUserList();
    }

    /**
     * set dao.
     * @param userDao user dao
     */
    public void setUserDao(UserDaoImpl userDao) {
        this.userDao = userDao;
    }
}
```

- **在注解和Java配置方式下：**
```java
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    private UserDaoImpl userDao;

    /**
     * find user list.
     * @return user list
     */
    public List<User> findUserList() {
        return this.userDao.findUserList();
    }

    /**
     * set dao.
     * @param userDao user dao
     */
    @Autowired
    public void setUserDao(UserDaoImpl userDao) {
        this.userDao = userDao;
    }
}
```
在`Spring3.x`刚推出的时候，推荐使用注入的就是这种, 但是这种方式比较麻烦，所以在`Spring4.x`版本中推荐 **构造函数注入** 。

### 2. 构造函数
- **在XML配置方式中**，`<constructor-arg>`是通过构造函数参数注入，比如下面的`xml`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
                           http://www.springframework.org/schema/beans/spring-beans.xsd">
    <!-- services -->
    <bean id="userService" class="tech.pdai.springframework.service.UserServiceImpl">
        <constructor-arg name="userDao" ref="userDao"/>
        <!-- additional collaborators and configuration for this bean go here -->
    </bean>
    <!-- more bean definitions for services go here -->
</beans>
```
本质上是`new UserServiceImpl(userDao)`创建对象, 所以对应的`service`类是这样的：
```java
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    private final UserDaoImpl userDao;

    /**
     * init.
     * @param userDaoImpl user dao impl
     */
    public UserServiceImpl(UserDaoImpl userDaoImpl) {
        this.userDao = userDaoImpl;
    }

    /**
     * find user list.
     * @return user list
     */
    public List<User> findUserList() {
        return this.userDao.findUserList();
    }
}
```

- **在`注解`和`Java`的配置方式下**
```java
@Service
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    private final UserDaoImpl userDao;

    /**
     * init.
     * @param userDaoImpl user dao impl
     */
    @Autowired // 这里@Autowired也可以省略
    public UserServiceImpl(final UserDaoImpl userDaoImpl) {
        this.userDao = userDaoImpl;
    }

    /**
     * find user list.
     * @return user list
     */
    public List<User> findUserList() {
        return this.userDao.findUserList();
    }
}
```
在`Spring4.x`版本中推荐的注入方式就是`注解`的方式，下文重点分析`注解`的使用。

### 3. 注解注入
以`@Autowired`（自动注入）注解注入为例，修饰符有三个属性：`Constructor`、`byType`、`byName`。默认按照`byType`注入。
- **`constructor`** ：通过构造方法进行自动注入，`Spring`会匹配与构造方法参数类型一致的`bean`进行注入；  
  如果有一个多参数的构造方法，有一个只有一个参数的构造方法，在容器中查找到多个匹配多参数构造方法的`bean`，那么`Spring`会优先将`bean`注入到多参数的构造方法中。
- **`byName`** ：被注入`bean`的`id名`必须与`set`方法后半截匹配，并且`id名`的第一个单词首字母必须小写，这一点与手动`set`注入有点不同。
- **`byType`** ：查找所有的`set`方法，将符合参数类型的`bean`注入。

比如下面的代码注入`UserDaoImpl`就是使用的`byType`：
```java
@Service
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    @Autowired
    private UserDaoImpl userDao;

    /**
     * find user list.
     * @return user list
     */
    public List<User> findUserList() {
        return userDao.findUserList();
    }
}
```

## 五、IOC和DI使用问题小结
> 总结下实际开发中会遇到的一些问题：

### 1. 为什么推荐构造器注入方式？
先来看看`Spring`在官方文档里怎么说，（[官方文档原文地址](https://docs.spring.io/spring-framework/docs/current/reference/html/core.html#beans-setter-injection)）：

> The Spring team generally advocates constructor injection as it enables one to implement application components as immutable objects and to ensure that required dependencies are not null. Furthermore constructor-injected components are always returned to client (calling) code in a fully initialized state.

简单的翻译一下：这个构造器注入的方式 **能够保证注入的组件 <font color="red">不可变</font> ，并且确保需要的 <font color="red">依赖不为空**</font>  。此外，构造器注入的依赖总是能够在返回客户端（组件/调用方）代码的时候保证 <font color="red">完全初始化的状态</font> 。

下面来简单的解释一下：
- **依赖不可变**：其实说的就是`final`关键字。
- **依赖不为空**（省去了我们对其检查）：当要实例化`UserServiceImpl`的时候，由于自己实现了有参数的构造函数，所以不会调用默认构造函数，那么就需要`Spring`容器传入所需要的参数，所以就两种情况：
  - 有该类型的参数 --> 传入，OK 。
  - 无该类型的参数 --> 报错。
- **完全初始化的状态**：这个可以跟上面的依赖不为空结合起来，向构造器传参之前，要确保注入的内容不为空，那么肯定要调用依赖组件的构造方法完成实例化。  
  而在Java类加载实例化的过程中，构造方法是最后一步（之前如果有父类先初始化父类，然后自己的成员变量，最后才是构造方法），所以返回来的都是初始化之后的状态。

所以通常是这样的：
```java
@Service
public class UserServiceImpl {
    /**
     * user dao impl.
     */
    private final UserDaoImpl userDao;

    /**
     * init.
     * @param userDaoImpl user dao impl
     */
    public UserServiceImpl(final UserDaoImpl userDaoImpl) {
        this.userDao = userDaoImpl;
    }
}
```

如果使用`setter`注入，缺点显而易见：对于`IOC`容器以外的环境，除了使用反射来提供它需要的依赖之外，将**无法复用该实现类**。
```java
// 这里只是模拟一下，正常来说我们只会暴露接口给客户端，不会暴露实现。
UserServiceImpl userService = new UserServiceImpl();
userService.findUserList(); // -> NullPointerException, 潜在的空指针隐患
```

**循环依赖的问题**：使用`field`注入可能会导致循环依赖，即`A`里面注入`B`，`B`里面又注入`A`：
```java
public class A {
    @Autowired
    private B b;
}

public class B {
    @Autowired
    private A a;
}
```

如果使用构造器注入，在`Spring`项目启动的时候，就会抛出：`BeanCurrentlyInCreationException：Requested bean is currently in creation: Is there an unresolvable circular reference？`从而提醒你避免循环依赖；  
如果是`field`注入的话，启动的时候不会报错，然而在使用那个bean的时候才会报错。

### 2. 在使用构造器注入方式时注入了太多的类导致Bad Smell怎么办？
比如当你一个`Controller`中注入了太多的`Service`类，`Sonar`（代码质量检查插件）会给你提示相关告警

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之控制反转（IOC）/类中注入太多类，编译器插件Sonar警告.png)
</center>

**对于这个问题，说明你的类当中有太多的责任，那么你要好好想一想是不是自己违反了类的`单一性职责原则`，从而导致有这么多的依赖要注入。**

### 3. @Autowired和@Resource以及@Inject等注解注入有何区别？
#### 3.1 @Autowired
##### 3.1.1 注解源码
在`Spring 2.5` 引入了 `@Autowired` 注解
```java
@Target({ElementType.CONSTRUCTOR, ElementType.METHOD, ElementType.PARAMETER, ElementType.FIELD, ElementType.ANNOTATION_TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Autowired {
    boolean required() default true;
} 
```

从`Autowired`注解源码上看，可以使用在下面这些地方：
```java
@Target(ElementType.CONSTRUCTOR) #构造函数
@Target(ElementType.METHOD) #方法
@Target(ElementType.PARAMETER) #方法参数
@Target(ElementType.FIELD) #字段、枚举的常量
@Target(ElementType.ANNOTATION_TYPE) #注解
```

还有一个`value`属性，默认是`true`。

##### 3.1.2 简单使用
在字段属性上
```java
@Autowired
private HelloDao helloDao;
```
或者：
```java
private HelloDao helloDao;
public HelloDao getHelloDao() {
    return helloDao;
}

@Autowired
public void setHelloDao(HelloDao helloDao) {
    this.helloDao = helloDao;
}
```
或者：
```java
private HelloDao helloDao;
// @Autowired--可省略
public HelloServiceImpl(@Autowired HelloDao helloDao) {
    this.helloDao = helloDao;
}
// 构造器注入也可不写@Autowired，也可以注入成功。
```
将`@Autowired`写在被注入的成员变量上，`setter`或者构造器上，就不用再`xml`文件中配置了。

**如果有多个类型一样的`Bean`候选者，则默认根据设定的属性名称进行获取。**  
如 `HelloDao` 在`Spring`中有 `helloWorldDao` 和 `helloDao` 两个`Bean`候选者。
```java
@Autowired
private HelloDao helloDao;
```
首先根据类型获取，发现多个`HelloDao`，然后根据`helloDao`进行获取，如果要获取限定的其中一个候选者，结合`@Qualifier`进行注入。
```java
@Autowired
@Qualifier("helloWorldDao")
private HelloDao helloDao;
```
注入名称为`helloWorldDao` 的`Bean`组件。`@Qualifier("XXX")` 中的 `XX`是 `Bean` 的名称，**所以 `@Autowired` 和 `@Qualifier` 结合使用时，自动注入的策略就从 `byType` 转变成 `byName` 了。**

多个类型一样的`Bean`候选者，也可以`@Primary`进行使用，设置首选的组件，也就是默认优先使用哪一个。

**注意：** 使用`@Qualifier` 时候，如何设置的指定名称的`Bean`不存在，则会抛出异常，如果防止抛出异常，可以使用`@Autowired(required = false)`：
```java
@Qualifier("xxxxyyyy")
@Autowired(required = false)
private HelloDao helloDao;
```

**补充：** 在`SpringBoot`中也可以使用`@Bean` + `@Autowired`进行组件注入，将`@Autowired`加到参数上，其实也可以省略。
```java
@Bean
public Person getPerson(@Autowired Car car){// @Autowired 可以省略
    return new Person();
}
```

##### 3.1.3 小结
1. @Autowired 是`Spring`自带的注解，通过`AutowiredAnnotationBeanPostProcessor` 类实现的依赖注入
2. @Autowired 可以作用在`CONSTRUCTOR`、`METHOD`、`PARAMETER`、`FIELD`、`ANNOTATION_TYPE` **（即：构造方法、方法、参数、字段、注解）**
3. @Autowired 默认是根据类型（`byType`）进行自动装配的
4. 如果有多个类型一样的`Bean`候选者，需要指定按照名称（`byName`）进行装配，这时则需要配合`@Qualifier`。  
  指定名称后，如果`IOC`容器中没有对应的组件`bean`就会抛出`NoSuchBeanDefinitionException`。也可以将`@Autowired`中`required`配置为`false`，如果配置为`false`之后，当没有找到相应`bean`的时候，系统不会抛异常。

#### 3.2 @Resource
##### 3.2.1 注解源码
```java
@Target({TYPE, FIELD, METHOD})
@Retention(RUNTIME)
public @interface Resource {
    String name() default "";
    // ...
}
```

从`@Resource`注解源码上看，可以使用在下面这些地方：
```java
@Target(ElementType.TYPE) #接口、类、枚举
@Target(ElementType.FIELD) #字段、枚举的常量
@Target(ElementType.METHOD) #方法
```

其中`name` 指定注入指定名称的组件。

##### 3.2.2 简单使用
```java
@Component
public class SuperMan {
    @Resource
    private Car car;
}
```

按照属性名称 `car` 注入容器中的组件。如果容器中`BMW`还有`BYD`两种类型组件，指定加入`BMW`，如下代码：
```java
@Component
public class SuperMan {
    @Resource(name = "BMW")
    private Car car;
}
```
**注意：这里`name` 的作用类似 `@Qualifier`**

##### 3.2.3 简单总结
1. @Resource是`JSR250`规范的实现，在`javax.annotation`包下
2. @Resource可以作用`TYPE`、`FIELD`、`METHOD`上 **（即：类/接口/枚举类、字段、方法）**
3. @Resource是默认根据属性名称进行自动装配的，如果有多个类型一样的`Bean`候选者，则可以通过`name`进行指定进行注入

#### 3.3 @Inject
##### 3.3.1 Inject注解源码
```java
@Target({ METHOD, CONSTRUCTOR, FIELD })
@Retention(RUNTIME)
@Documented
public @interface Inject {}
```

从`@Inject`注解源码上看，可以使用在下面这些地方：
```java
@Target(ElementType.CONSTRUCTOR) #构造函数
@Target(ElementType.METHOD) #方法
@Target(ElementType.FIELD) #字段、枚举的常量
```

##### 3.3.2 简单使用
```java
@Inject
private Car car;
```

指定加入BMW组件。
```java
@Inject
@Named("BMW")
private Car car;
```
**注意：这里的`@Named` 的作用类似 `@Qualifier`**

##### 3.3.4 小结
1. @Inject是`JSR330`（`Dependency Injection for Java`）中的规范，需要导入`javax.inject.Inject`包，才能实现注入
2. @Inject可以作用`CONSTRUCTOR`、`METHOD`、`FIELD`上 **（即：构造方法、方法、字段）**
3. @Inject是根据类型进行自动装配的，如果需要按名称进行装配，则需要配合`@Named`；

### 4. 总结
1. `@Autowired` 是 `Spring` 自带的， `@Resource` 是 `JSR250` 规范实现的， `@Inject` 是 `JSR330` 规范实现的；
2. `@Autowired`、`@Inject`用法基本一样，不同的是 `@Inject` **没有** `required` 属性；
3. `@Autowired`、`@Inject`是默认按照类型匹配的， `@Resource` 是按照名称匹配的；
4. `@Autowired` 如果需要按照名称匹配需要和 `@Qualifier` 一起使用， 而`@Inject` 和 `@Named` 一起使用， 而`@Resource` 则通过 `name` 进行指定。

如果你还期望源码层理解，可以参考这篇博客[Spring源码分析@Autowired、@Resource注解的区别](https://blog.csdn.net/qq_35634181/article/details/104802906)

## 补充：
`DI`（依赖注入）其实就是`IOC`的一种实现方式，还有一种是`DL`（`Dependency Lookup`依赖查找）。

> `DL`由`Martin Fowler` 在2004年初的一篇论文中首次提出的。

依赖查找，英文名称为：`Dependency Lookup`，它表示的是容器中的受控对象（`bean`）通过容器的`API`来查找自己所依赖的资源和协作对象。这种方式虽然降低了对象间的依赖，但是同时也使用到了容器的`API`，造成了我们无法在容器外使用和测试对象。  
依赖查找是一种主动的行为，来解决对象的依赖问题，虽然其更加直观可读，但是代码侵入性较高，较高依赖 `API`接口。

**依赖查找是一种更加传统的`IoC`实现方式。**
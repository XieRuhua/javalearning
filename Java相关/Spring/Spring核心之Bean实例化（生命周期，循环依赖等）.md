# Spring核心之Bean实例化（生命周期，循环依赖等）

[笔记内容参考1：Spring进阶- Spring IOC实现原理详解之Bean实例化(生命周期,循环依赖等)](https://pdai.tech/md/spring/spring-x-framework-ioc-source-3.html)  
[笔记内容参考2：Spring源码解析(五)Spring 加载bean 依赖注入](https://cloud.tencent.com/developer/article/1846652)  
[笔记内容参考3：图文并茂，揭秘 Spring 的 Bean 的加载过程](https://www.jianshu.com/p/9ea61d204559)  
[笔记内容参考4：Spring Bean的生命周期，你了解吗](https://baijiahao.baidu.com/s?id=1732607193313085468&wfr=spider&for=pc)  
[笔记内容参考5：深究Spring中Bean的生命周期](https://mp.weixin.qq.com/s/GczkZHJ2DdI7cf9g0e6t_w)

**笔记使用的Spring源码版本 `Spring-5.0.8.RELEASE`**

[toc]

## 一、概述
`Spring` 作为 `Ioc` 框架，实现了 **依赖注入** ，由一个中心化的 `Bean 工厂`来负责各个 `Bean` 的实例化和依赖管理。各个 `Bean` 可以不需要关心各自的复杂的创建过程，达到了很好的解耦效果。

对 `Spring` 的工作流进行一个粗略的概括，主要为两大环节：
- **解析：** 读取 `xml` 配置，扫描类文件，从配置或者注解中获取 `Bean` 的定义信息，注册一些扩展功能。
- **加载：** 通过解析完的定义信息获取 `Bean` 实例。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/Spring类的解析和加载简易示意图.png)
</center>

假设所有的配置和扩展类都已经装载到了 `ApplicationContext` 中，然后具体分析一下 `Bean` 的加载流程。

**思考一个问题，抛开 `Spring` 框架的实现，假设已经有一套完整的 `Bean Definition Map`（Bean的定义集合），然后指定一个 `beanName` 要进行实例化，需要关心什么？**  
即使没有 `Spring` 框架，也需要了解这两方面的知识：
- **作用域**：单例作用域或者原型作用域，单例的话需要全局实例化一次，原型每次创建都需要重新实例化。
- **依赖关系**：一个 `Bean` 如果有依赖，则需要初始化依赖，然后进行关联。如果多个 `Bean` 之间存在着循环依赖：`A` 依赖 `B`、`B` 依赖 `C`、`C` 又依赖 `A`，需要解这种循环依赖问题。

`Spring` 进行了抽象和封装，使得 **作用域** 和 **依赖关系** 的配置对开发者透明，开发者只需要知道当初在配置里已经明确指定了它的生命周期和依赖了谁？至于是怎么实现？依赖如何注入？这些都托付给了 `Spring` 工厂来管理。

`Spring` 只暴露了很简单的接口给调用者，比如 `getBean` ：
```java
ApplicationContext context = new ClassPathXmlApplicationContext("hello.xml");
HelloBean helloBean = (HelloBean) context.getBean("hello");
helloBean.sayHello();
```
那就从 `getBean` 方法作为入口，去理解 `Spring` 加载的流程是怎样的，以及`Bean`在容器关闭时的销毁流程。

## 二、Bean的获取/创建——getBean()方法主体思路及细节分析
### 1. getBean()的总体流程
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/Spring中gatBean方法的总体流程.png)
</center>

上图是跟踪了 `getBean` 的调用链创建的流程图，为了能够很好地理解 `Bean` 加载流程，省略一些**异常**、**日志**、**分支处理**和**一些特殊条件的判断**。

从上面的流程图中，可以看到一个 `Bean` 加载会经历几个重要阶段（用绿色标记）：
- **获取 BeanName**：对传入的 `name` 进行解析，转化为可以从 `Map` 中获取到 `BeanDefinition` 的 `BeanName`。
- **合并 Bean 定义**：对父类的定义进行合并和覆盖，如果父类还有父类，会进行递归合并，以获取完整的 `Bean` 定义信息。
- **实例化**：使用构造或者工厂方法创建 `Bean` 实例。
- **属性填充**：寻找并且注入依赖，依赖的 `Bean` 还会递归调用 `getBean` 方法获取。
- **初始化**：调用自定义的初始化方法。
- **获取最终的 Bean**：如果是 `FactoryBean` 需要调用 `getObject` 方法，如果需要类型转换调用 `TypeConverter` 进行转化。

整个流程最为复杂的是对 **<font color='red'>循环依赖</font>** 的解决方案，后续会进行重点分析。

### 2. getBean()的主体思路
`BeanFactory`在创建一个`Bean`对象实例是从上到下实现源码如下，其中从最顶层的`getBean`方法开始，调用顺序为： **`getBean --> doGetBean --> createBean --> doCreateBean`**

`BeanFactory`实现`getBean`方法在`org.springframework.beans.factory.support.AbstractBeanFactory`中，这个方法重载的都是对`doGetBean`方法进行实现的：
```java
public Object getBean(String name) throws BeansException {
    return doGetBean(name, null, null, false);
}
public <T> T getBean(String name, Class<T> requiredType) throws BeansException {
    return doGetBean(name, requiredType, null, false);
}
public Object getBean(String name, Object... args) throws BeansException {
    return doGetBean(name, null, args, false);
}
public <T> T getBean(String name, @Nullable Class<T> requiredType, @Nullable Object... args)
    throws BeansException {
    return doGetBean(name, requiredType, args, false);
}
```

接下来看`doGetBean`方法(这个方法很长，主要看它的整体思路和设计要点）：
```java
// BeanFactory中doGetBean方法使用到的部分关键属性

// 1. 从 bean 名称映射到合并的 RootBeanDefinition
/** Map from bean name to merged RootBeanDefinition */
private final Map<String, RootBeanDefinition> mergedBeanDefinitions = new ConcurrentHashMap<>(256);

// 2. 至少已经创建过一次的 bean 的名称
/** Names of beans that have already been created at least once */
private final Set<String> alreadyCreated = Collections.newSetFromMap(new ConcurrentHashMap<>(256));
```

```java
// doGetBean源码详解
// 参数typeCheckOnly：bean实例是否包含一个类型检查
protected <T> T doGetBean(final String name, @Nullable final Class<T> requiredType,
                          @Nullable final Object[] args, boolean typeCheckOnly) throws BeansException {
    // 1. 解析bean的真正name，
    // 如果bean是工厂类，name前缀会加&，需要去掉
    // 如果name是别名的话，则从canonicalName方法中的this.aliasMap.get(canonicalName)取出beanName
    final String beanName = transformedBeanName(name);
    Object bean;

    // 根据beanName得到单例实例化对象，检查单例对象是否实例化并且在创建单例对象的时候允许提前引用（这个主要是用于解决循环引用）
    // spring解决循环引用就是利用三级缓存实现的；
    // 这里会提前返回引用对象的
    Object sharedInstance = getSingleton(beanName);
    if (sharedInstance != null && args == null) {
        if (logger.isTraceEnabled()) {
            if (isSingletonCurrentlyInCreation(beanName)) {
                logger.trace("Returning eagerly cached instance of singleton bean '" + beanName +
                             "' that is not fully initialized yet - a consequence of a circular reference");
            }
            else {
                logger.trace("Returning cached instance of singleton bean '" + beanName + "'");
            }
        }
        // 2. 无参单例从缓存中获取
        bean = getObjectForBeanInstance(sharedInstance, name, beanName, null);
    }

    else {
        // Fail if we're already creating this bean instance:
        // We're assumably within a circular reference.
        // 3. 如果bean实例还在创建中，则直接抛出异常（因为此时可能在循环引用中）
        if (isPrototypeCurrentlyInCreation(beanName)) {
            throw new BeanCurrentlyInCreationException(beanName);
        }

        // Check if bean definition exists in this factory.
        // 4. 如果 bean definition 存在于父的bean工厂中，委派给父Bean工厂获取
        BeanFactory parentBeanFactory = getParentBeanFactory();
        if (parentBeanFactory != null && !containsBeanDefinition(beanName)) {
            // Not found -> check parent.
            String nameToLookup = originalBeanName(name);
            if (parentBeanFactory instanceof AbstractBeanFactory) {
                return ((AbstractBeanFactory) parentBeanFactory).doGetBean(
                    nameToLookup, requiredType, args, typeCheckOnly);
            }
            else if (args != null) {
                // Delegation to parent with explicit args.
                return (T) parentBeanFactory.getBean(nameToLookup, args);
            }
            else if (requiredType != null) {
                // No args -> delegate to standard getBean method.
                return parentBeanFactory.getBean(nameToLookup, requiredType);
            }
            else {
                return (T) parentBeanFactory.getBean(nameToLookup);
            }
        }

        if (!typeCheckOnly) {
            // 5. 将当前bean实例放入alreadyCreated集合里，标识这个bean准备创建了
            markBeanAsCreated(beanName);
        }

        try {
            // 4.1 合并父类定义
            final RootBeanDefinition mbd = getMergedLocalBeanDefinition(beanName);
            checkMergedBeanDefinition(mbd, beanName, args);

            // Guarantee initialization of beans that the current bean depends on.
            // 6. 确保当前的依赖也被初始化了.（即当前 bean 所依赖的 bean 也被初始化了）
            String[] dependsOn = mbd.getDependsOn();
            if (dependsOn != null) {
                for (String dep : dependsOn) {
                    if (isDependent(beanName, dep)) {
                        throw new BeanCreationException(mbd.getResourceDescription(), beanName,
                                                        "Circular depends-on relationship between '" + beanName + "' and '" + dep + "'");
                    }
                    registerDependentBean(dep, beanName);
                    try {
                        getBean(dep);// 初始化它依赖的Bean
                    }
                    catch (NoSuchBeanDefinitionException ex) {
                        throw new BeanCreationException(mbd.getResourceDescription(), beanName,
                                                        "'" + beanName + "' depends on missing bean '" + dep + "'", ex);
                    }
                }
            }

            // Create bean instance.
            // 7. 开始创建Bean实例
            // 7.1 创建Bean实例：单例
            if (mbd.isSingleton()) {
                // 7.1.2 createBean执行完成之后调用getSingleton方法获取已经创建成功并放入单实例缓存池的单例对象
                sharedInstance = getSingleton(beanName, () -> {
                    try {
                        // 7.1.1 真正创建bean的方法
                        return createBean(beanName, mbd, args);
                    }
                    catch (BeansException ex) {
                        destroySingleton(beanName);
                        throw ex;
                    }
                });
                // 8. 使用合并后的定义进行实例化
                bean = getObjectForBeanInstance(sharedInstance, name, beanName, mbd);
            }
            // 7.2 创建Bean实例：原型
            else if (mbd.isPrototype()) {
                // IOC容器初始化时并不会触发原型模式的初始化
                // It's a prototype -> create a new instance.
                Object prototypeInstance = null;
                try {
                    beforePrototypeCreation(beanName);
                    prototypeInstance = createBean(beanName, mbd, args);
                }
                finally {
                    afterPrototypeCreation(beanName);
                }
                // 8. 使用合并后的定义进行实例化
                bean = getObjectForBeanInstance(prototypeInstance, name, beanName, mbd);
            }
            // 7.3 创建Bean实例：根据bean的scope创建
            else {
                String scopeName = mbd.getScope();
                final Scope scope = this.scopes.get(scopeName);
                if (scope == null) {
                    throw new IllegalStateException("No Scope registered for scope name '" + scopeName + "'");
                }
                try {
                    Object scopedInstance = scope.get(beanName, () -> {
                        beforePrototypeCreation(beanName);
                        try {
                            return createBean(beanName, mbd, args);
                        }
                        finally {
                            afterPrototypeCreation(beanName);
                        }
                    });
                	// 8. 使用合并后的定义进行实例化
                    bean = getObjectForBeanInstance(scopedInstance, name, beanName, mbd);
                }
                catch (IllegalStateException ex) {
                    throw new BeanCreationException(beanName,
                            "Scope '" + scopeName + "' is not active for the current thread; consider " +
                            "defining a scoped proxy for this bean if you intend to refer to it from a singleton",
                            ex);
                }
            }
        }
        catch (BeansException ex) {
            cleanupAfterBeanCreationFailure(beanName);
            throw ex;
        }
    }

    // Check if required type matches the type of the actual bean instance.
    // 8. 检查所需类型是否与实际 bean 实例的类型匹配。
    if (requiredType != null && !requiredType.isInstance(bean)) {
        try {
            T convertedBean = getTypeConverter().convertIfNecessary(bean, requiredType);
            if (convertedBean == null) {
                throw new BeanNotOfRequiredTypeException(name, requiredType, bean.getClass());
            }
            return convertedBean;
        }
        catch (TypeMismatchException ex) {
            if (logger.isTraceEnabled()) {
                logger.trace("Failed to convert bean '" + name + "' to required type '" +
                             ClassUtils.getQualifiedName(requiredType) + "'", ex);
            }
            throw new BeanNotOfRequiredTypeException(name, requiredType, bean.getClass());
        }
    }
    // 9. 返回对象
    return (T) bean;
}
```
大致步骤：
1. 解析`bean`的真正`name`（如果`bean`是工厂类，`name`前缀会加`&`，需要去掉）
2. 无参单例先从缓存中尝试获取
3. 如果`bean`实例还在创建中，则直接抛出异常
4. 如果`bean definition`存在于父的`bean工厂`中，委派给`父Bean工厂`获取
5. 标记这个`beanName`的实例正在创建
6. 确保它的依赖也被初始化
7. 调用`createBean方法`真正创建
   - 单例模式：
     - 调用 `createBean` 方法创建`bean`对象
     - `createBean`执行完成之后调用`getSingleton`方法获取已经创建成功并放入 **单实例缓存池** 的 **单例对象**
   - 原型模式：`IOC`容器初始化时并不会触发原型模式的初始化
   - 其他情况：根据`bean`的`scope`创建
8. 使用合并后的定义进行实例化
9. 检查所需类型是否与实际 `bean` 实例的类型匹配
10. 返回对象

### 3. getBean()细节分析
#### 3.1. 解析bean的真正name
在解析完配置后创建的 `Map`，使用的是 `beanName` 作为 `key`。见 `org.springframework.beans.factory.support.DefaultListableBeanFactory`：
```java
/** Map of bean definition objects, keyed by bean name */
private final Map<String, BeanDefinition> beanDefinitionMap = new ConcurrentHashMap<String, BeanDefinition>(256);
```

`BeanFactory.getBean` 中传入的 `name`，有可能是这几种情况：
- **bean name**：`bean`本身的`name`，可以直接获取到其定义 `BeanDefinition`。
- **alias name**：别名，需要转化。
- **factorybean name**： **带 `&` 前缀** ，通过它获取 `BeanDefinition` 的时候需要去除 `&` 前缀。

为了能够获取到正确的 `BeanDefinition`，需要先对非 `bean name` 做一个转换，得到 `beanName`。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/Spring中transformedBeanName方法获取真实beanName.png)
</center>

进入`transformedBeanName`方法（ **对应`doGetBean`方法的第1步：解析bean的真正name** ）：
```java
protected String transformedBeanName(String name) {
    return canonicalName(BeanFactoryUtils.transformedBeanName(name));
}
```

通过代码跟踪可以发现`transformedBeanName`方法调用的是`SimpleAliasRegistry`中的`canonicalName`方法，其中的参数为`BeanFactoryUtils.transformedBeanName(name)`。

`transformedBeanName方法`开始判断`name`的类型：
1. 如果是 **`factorybean name`** ：表示这是个工厂 `bean`，则会携带前缀修饰符 `&` 的，直接把前缀去掉。  
   进入 `org.springframework.beans.factory.BeanFactoryUtils#transformedBeanName` :
   ```java
   public static String transformedBeanName(String name) {
       Assert.notNull(name, "'name' must not be null");
       String beanName = name;
       // 判断是否是BeanFactory.FACTORY_BEAN_PREFIX（"&"）开头的命名name，是则去掉前缀，否则直接返回
       while (beanName.startsWith(BeanFactory.FACTORY_BEAN_PREFIX)) {
           beanName = beanName.substring(BeanFactory.FACTORY_BEAN_PREFIX.length());
       }
       return beanName;
   }
   ```
2. 如果是 **`alias name`** ：在解析阶段，`alias name` 和 `bean name` 的映射关系被注册到 `SimpleAliasRegistry` 中。从该注册器中取到 `beanName`。  
   通过参数中的 `工厂bean` 判断之后进入 `org.springframework.core.SimpleAliasRegistry#canonicalName`：
   ```java
   /**
    * 确定原始名称，将别名解析为规范名称。
    */
   public String canonicalName(String name) {
       String canonicalName = name;
       // Handle aliasing...
       String resolvedName;
       do {
           // 获取别名所对应的原始名称
           resolvedName = this.aliasMap.get(canonicalName);
           if (resolvedName != null) {
               canonicalName = resolvedName;
           }
       }
       while (resolvedName != null);
       return canonicalName;
   }
   ```
3. 其他情况是`bean`本身则不需要转换`name`。

#### 3.2. 合并RootBeanDefinition
**对应`doGetBean`方法的第4步：如果`bean definition` 存在于`父的bean工厂`中，委派给`父Bean工厂`获取。**

从配置文件读取到的 `BeanDefinition` 是 **`GenericBeanDefinition`**。它的记录了一些当前类声明的属性或构造参数，但是对于父类只用了一个 `parentName` 来记录。
```java
public class GenericBeanDefinition extends AbstractBeanDefinition {
	@Nullable
	private String parentName;
    // ...
}
```

接下来会发现一个问题，在后续实例化 `Bean` 的时候，使用的 `BeanDefinition` 是 **`RootBeanDefinition`** 类型而非 **`GenericBeanDefinition`** 。  
见 `org.springframework.beans.factory.support.AbstractBeanFactory#doGetBean` ：
```java
protected <T> T doGetBean ... {
    // ...
    
    // 4.1 合并父类定义
    final RootBeanDefinition mbd = getMergedLocalBeanDefinition(beanName);
}
```

这是为什么？  
因为`GenericBeanDefinition` 在有继承关系的情况下，定义的信息不足：
- 如果不存在继承关系：`GenericBeanDefinition` 存储的信息是完整的，可以直接转化为 `RootBeanDefinition`。
- 如果存在继承关系：`GenericBeanDefinition` 存储的是 **增量信息** 而不是 **全量信息**。

**为了能够正确初始化对象，需要完整的信息才行** 。需要 **递归合并所有父类的定义** ：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/Spring中getMergedLocalBeanDefinition方法合并父类定义.png)
</center>

见 `org.springframework.beans.factory.support.AbstractBeanFactory#doGetBean` ：
```java
protected <T> T doGetBean ... {
    // ...

    // 4.1 合并父类定义
    final RootBeanDefinition mbd = getMergedLocalBeanDefinition(beanName);

    // ...
    // 使用合并后的定义进行实例化
    bean = getObjectForBeanInstance(prototypeInstance, name, beanName, mbd);

    // ...
}
```

在判断 `parentName` 存在的情况下，说明存在父类定义，启动合并。如果父类还有父类怎么办？则递归调用，继续合并。  
见`AbstractBeanFactory.getMergedBeanDefinition` 方法：
```java
// BeanFactory中getMergedBeanDefinition方法使用到的部分关键属性 

// 1. 从 bean 名称映射到合并的 RootBeanDefinition；
// xml中，配置了 parent属性需要合并；详细parent怎么使用，看文末总结部分
private final Map<String, RootBeanDefinition> mergedBeanDefinitions =
    new ConcurrentHashMap<String, RootBeanDefinition>(256);

// 2. 用于判断是缓存 bean 元数据还是为每次访问重新获取它
private boolean cacheBeanMetadata = true;
```

```java
protected RootBeanDefinition getMergedBeanDefinition(
    String beanName, BeanDefinition bd, @Nullable BeanDefinition containingBd)
    throws BeanDefinitionStoreException {

    synchronized (this.mergedBeanDefinitions) {
        RootBeanDefinition mbd = null;

        // Check with full lock now in order to enforce the same merged instance.
        if (containingBd == null) {
            mbd = this.mergedBeanDefinitions.get(beanName);
        }
        // 如果之前没有合并过
        if (mbd == null) {
            // 如果没有配置parent属性
            if (bd.getParentName() == null) {
                // Use copy of given root bean definition.
                if (bd instanceof RootBeanDefinition) {
                    mbd = ((RootBeanDefinition) bd).cloneBeanDefinition();
                }
                else {
                    mbd = new RootBeanDefinition(bd);
                }
            }
            // 如果有配置parent属性
            else {
                // Child bean definition: needs to be merged with parent.
                // 子bean定义：需要与父合并。
                BeanDefinition pbd;
                try {
                    String parentBeanName = transformedBeanName(bd.getParentName());
                    // 根据父beanName获取父类的BeanDefinition；如果父类还有父类会递归调用
                    if (!beanName.equals(parentBeanName)) {
                        // 递归调用，继续合并父类定义
                        pbd = getMergedBeanDefinition(parentBeanName);
                    }
                    else {
                        BeanFactory parent = getParentBeanFactory();
                        if (parent instanceof ConfigurableBeanFactory) {
                            pbd = ((ConfigurableBeanFactory) parent).getMergedBeanDefinition(parentBeanName);
                        }
                        else {
                            throw new NoSuchBeanDefinitionException(parentBeanName,
                                                                    "Parent name '" + parentBeanName + "' is equal to bean name '" + beanName +
                                                                    "': cannot be resolved without an AbstractBeanFactory parent");
                        }
                    }
                }
                catch (NoSuchBeanDefinitionException ex) {
                    throw new BeanDefinitionStoreException(bd.getResourceDescription(), beanName,
                                                           "Could not resolve parent bean definition '" + bd.getParentName() + "'", ex);
                }
                // Deep copy with overridden values.
                // 先使用合并后的完整定义（根据父BeanDefinition）创建 RootBeanDefinition
                mbd = new RootBeanDefinition(pbd);
                // 然后将子BeanDefinition所有已经配置的数据覆盖父类的，那么就达到了合并的目的
                mbd.overrideFrom(bd);
            }

            // Set default singleton scope, if not configured before.
            // 如果没有设置作用域 默认Singleton（即单例，RootBeanDefinition.SCOPE_SINGLETON）
            if (!StringUtils.hasLength(mbd.getScope())) {
                mbd.setScope(RootBeanDefinition.SCOPE_SINGLETON);
            }

            // A bean contained in a non-singleton bean cannot be a singleton itself.
            // Let's correct this on the fly here, since this might be the result of
            // parent-child merging for the outer bean, in which case the original inner bean
            // definition will not have inherited the merged outer bean's singleton status.
            // 一个bean中包含了一个非单例的bean，则它本身就不能够是单例的，下面的代码就是矫正它的作用域；
            if (containingBd != null && !containingBd.isSingleton() && mbd.isSingleton()) {
                mbd.setScope(containingBd.getScope());
            }

            // Cache the merged bean definition for the time being
            // (it might still get re-merged later on in order to pick up metadata changes)
            // 缓存合并之后的BeanDefinition； 为了支持metadata的更改，它之后可能仍然会重新合并 
            if (containingBd == null && isCacheBeanMetadata()) {
                this.mergedBeanDefinitions.put(beanName, mbd);
            }
        }

        return mbd;
    }
}
```
每次合并完父类定义后，都会调用 `RootBeanDefinition.overrideFrom` （上面方法中的`mbd.overrideFrom(bd);`）对父类的定义进行覆盖，直到获取到当前类能够正确实例化的 **全量信息**。

#### 3.3. 创建实例createBean()
##### 3.3.1. 完整步骤解析
获取到完整的 `RootBeanDefintion` 后，就可以拿这份定义信息来实例具体的 `Bean`。

**见doGetBean方法（第7.1.1步：真正创建bean的方法）：**
```java
// 7.1.1 真正创建bean的方法
return createBean(beanName, mbd, args);
```

该方法来自于一个抽象类`org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory`，继承了`AbstractBeanFactory`：
```java
// AbstractAutowireCapableBeanFactory中createBean方法使用到的部分关键属性

/** Cache of unfinished FactoryBean instances: FactoryBean name --> BeanWrapper */
// 未完成 FactoryBean 实例的缓存
private final Map<String, BeanWrapper> factoryBeanInstanceCache = 
    new ConcurrentHashMap<String, BeanWrapper>(16);
```

```java
/**
 * AbstractAutowireCapableBeanFactory类的核心方法：创建bean的实例；
 * 填充bean的实例，以及后置处理器等待；
 *
 * populates the bean instance, applies post-processors, etc.
 * @see #doCreateBean
 */
@Override
protected Object createBean(String beanName, RootBeanDefinition mbd, @Nullable Object[] args)
    throws BeanCreationException {

    if (logger.isDebugEnabled()) {
        logger.debug("Creating instance of bean '" + beanName + "'");
    }
    RootBeanDefinition mbdToUse = mbd;

    // Make sure bean class is actually resolved at this point, and
    // clone the bean definition in case of a dynamically resolved Class
    // which cannot be stored in the shared merged bean definition.
    Class<?> resolvedClass = resolveBeanClass(mbd, beanName);
    // 这里主要就是填充BeanClass属性
    if (resolvedClass != null && !mbd.hasBeanClass() && mbd.getBeanClassName() != null) {
        mbdToUse = new RootBeanDefinition(mbd);
        mbdToUse.setBeanClass(resolvedClass);
    }

    // Prepare method overrides.
    try {
        mbdToUse.prepareMethodOverrides();
    }
    catch (BeanDefinitionValidationException ex) {
        // ...
    }

    try {
        // Give BeanPostProcessors a chance to return a proxy instead of the target bean instance.
        // 给 BeanPostProcessors 一个机会返回一个代理对象；主要调用的是接口InstantiationAwareBeanPostProcessor里面的方法;
        Object bean = resolveBeforeInstantiation(beanName, mbdToUse);
        // 如果这里不为null；
        // 说明上面的后置处理器生成了一个代理对象直接返回，就不用在走后面的流程了（调用doCreateBean来实例化对象）
        if (bean != null) {
            return bean;
        }
    }
    catch (Throwable ex) {
        // ...
    }

    try {
        // 最终调用doCreateBean来实例化对象
        Object beanInstance = doCreateBean(beanName, mbdToUse, args);
        if (logger.isDebugEnabled()) {
            logger.debug("Finished creating instance of bean '" + beanName + "'");
        }
        return beanInstance;
    }
    // ...
}
```
该方法主要填充`bean`的实例，以及**后置处理器等待**；最终还是调用`doCreateBean方法`来实例化对象。

##### 3.3.2. doCreateBean()
继续分析`doCreateBean`方法：
```java
protected Object doCreateBean(final String beanName, final RootBeanDefinition mbd, final @Nullable Object[] args)
    throws BeanCreationException {
    // 实例化bean
    BeanWrapper instanceWrapper = null;
    if (mbd.isSingleton()) {
        // factoryBeanInstanceCache是缓存未完成的FactoryBean的实例对象的;
        instanceWrapper = this.factoryBeanInstanceCache.remove(beanName);
    }
    if (instanceWrapper == null) {
        // 为指定的bean创建一个新的实例，使用一个合适的实例化策略:工厂方法,构造函数自动装配,或者简单的实例化
        // 返回的是一个BeanWrapper包装类;
        // 后续逐个分析一下不同情况的实例化策略
        instanceWrapper = createBeanInstance(beanName, mbd, args);
    }
    // 1. 得到生成的实例；如果是cglib生成的，则是代理类；
    final Object bean = instanceWrapper.getWrappedInstance();
    Class<?> beanType = instanceWrapper.getWrappedClass();
    if (beanType != NullBean.class) {
        mbd.resolvedTargetType = beanType;
    }

    // Allow post-processors to modify the merged bean definition.
    // 允许 post-processors 修改 merged bean definition.
    synchronized (mbd.postProcessingLock) {
        // 判断 PostProcessor后置处理器 是否被执行过
        if (!mbd.postProcessed) {
            try {
                //修改一下 合并的BeanDefinition
                applyMergedBeanDefinitionPostProcessors(mbd, beanType, beanName);
            }
            catch (Throwable ex) {
                throw new BeanCreationException(mbd.getResourceDescription(), beanName,
                                                "Post-processing of merged bean definition failed", ex);
            }
            mbd.postProcessed = true;
        }
    }

    // Eagerly cache singletons to be able to resolve circular references
    // even when triggered by lifecycle interfaces like BeanFactoryAware.
    /**
     * 1.1. 提前暴露实例化的引用；主要是解决循环引用（调用addSingletonFactory方法提前将未完全实例化的bean放入缓存）
     * 1.2. 判断是单例对象&&允许循环引用&&已经开始创建单例对象了
     *      allowCircularReferences是默认为true的;ApplicationContext有个customizeBeanFactory(beanFactory);可以设置；
     * 1.3. 在什么时候开始标志创建单例对象的？
     *	    在调用getSingleton方法的时候beforeSingletonCreation(beanName);标识了创建已经开始
	 */
    boolean earlySingletonExposure = (mbd.isSingleton() && this.allowCircularReferences &&
                                      isSingletonCurrentlyInCreation(beanName));
    if (earlySingletonExposure) {
        if (logger.isDebugEnabled()) {
            logger.debug("Eagerly caching bean '" + beanName +
                         "' to allow for resolving potential circular references");
        }
        // 调用addSingletonFactory方法提前将未完全实例化的bean放入缓存
        addSingletonFactory(beanName, () -> getEarlyBeanReference(beanName, mbd, bean));
    }

    // 初始化bean实例
    Object exposedObject = bean;
    try {
        // 2. 填充属性/注入属性
        populateBean(beanName, mbd, instanceWrapper);
        // 3. 初始化
        exposedObject = initializeBean(beanName, exposedObject, mbd);
    }
    catch (Throwable ex) {
        // ...
    }

    if (earlySingletonExposure) {
        Object earlySingletonReference = getSingleton(beanName, false);
        if (earlySingletonReference != null) {
            if (exposedObject == bean) {
                exposedObject = earlySingletonReference;
            }
            else if (!this.allowRawInjectionDespiteWrapping && hasDependentBean(beanName)) {
                String[] dependentBeans = getDependentBeans(beanName);
                Set<String> actualDependentBeans = new LinkedHashSet<>(dependentBeans.length);
                for (String dependentBean : dependentBeans) {
                    if (!removeSingletonIfCreatedForTypeCheckOnly(dependentBean)) {
                        actualDependentBeans.add(dependentBean);
                    }
                }
                if (!actualDependentBeans.isEmpty()) {
                    // throw new BeanCurrentlyInCreationException.....
                    // 抛出循环引用的异常
                }
            }
        }
    }

    // 4. 注册bean的销毁逻辑
    try {
        registerDisposableBeanIfNecessary(beanName, bean, mbd);
    }
    catch (BeanDefinitionValidationException ex) {
        // ...
    }

    return exposedObject;
}
```
`doCreateBean`的核心逻辑包含：
1. 创建`bean`对象实例 -> 
2. `bean`的属性赋值`populateBean` -> 
3. 初始化`bean`：`initializeBean` -> 
4. 注册销毁拦截的`disposableBean`：调用`registerDisposableBeanIfNecessary`方法，将该`bean`保存在一个 **以`beanName`为`key`，以包装了`bean`引用的`DisposableBeanAdapter`为`value`** 的`map`中，在`spring`容器关闭时，遍历这个`map`来获取`bean`并执行销毁。

##### 3.3.3. 实例化对象的三种策略
继续分析不同情况的实例化策略，即`doCreateBean方法`中的 `instanceWrapper = createBeanInstance(beanName, mbd, args);`返回 `Bean` 的包装类 `BeanWrapper`。  
具体实例创建见 `AbstractAutowireCapableBeanFactory.createBeanInstance` ：
```java
/**
 * 为指定的bean创建一个新的实例,使用一个合适的实例化策略:工厂方法,构造函数自动装配,或者简单的实例化
 * @param args 显示的参数供给 构造函数 工厂方法调用
 */
protected BeanWrapper createBeanInstance(String beanName, RootBeanDefinition mbd, @Nullable Object[] args) {
    // 解析Bean的class类型
    Class<?> beanClass = resolveBeanClass(mbd, beanName);

    // 如果Bean不是public，而且是不允许共有权限访问，直接抛出异常.
    if (beanClass != null && !Modifier.isPublic(beanClass.getModifiers()) && !mbd.isNonPublicAccessAllowed()) {
        throw new BeanCreationException(mbd.getResourceDescription(), beanName,
                                        "Bean class isn't public, and non-public access not allowed: " + beanClass.getName());
    }

    /**
     * 通过指定的回调方法去创建bean实例，Spring5.0版本之后新增的方法。
     * 创建完成之后，会在初始化的时候指定bean的属性值转换器。即：ConversionService
     */
    Supplier<?> instanceSupplier = mbd.getInstanceSupplier();
    if (instanceSupplier != null) {
        return obtainFromSupplier(instanceSupplier, beanName);
    }

    /**
     * 1. 使用工厂方法创建
     * 如果配置了 factory-method（即：当前bean指定了对应的工厂方法） 则用工厂方法去生成对象
     * 底层会获取工厂方法【静态工厂方法|实例化方法】--> 然后解析方法入参 --> 然后执行反射调用创建实例 --> 封装为包装对象返回.
     */
    if (mbd.getFactoryMethodName() != null)  {
        return instantiateUsingFactoryMethod(beanName, mbd, args);
    }

    // Shortcut when re-creating the same bean...
    boolean resolved = false;
    boolean autowireNecessary = false;
    if (args == null) {
        synchronized (mbd.constructorArgumentLock) {
            if (mbd.resolvedConstructorOrFactoryMethod != null) {
                /** 表示构造函数的参数是否已经解析妥当 */
                resolved = true;
                autowireNecessary = mbd.constructorArgumentsResolved;
            }
        }
    }
    if (resolved) {
        // 如果构造函数的参数已经解析妥当
        if (autowireNecessary) {
            // 2. 使用有参构造函数创建
            // 则通过有参构造函数完成实例的创建
            return autowireConstructor(beanName, mbd, null, null);
        }
        else {
            /**
             * 3. 使用无参构造函数创建
             * 使用默认的bean对象创建策略进行bean对象的创建
             *  【设计模式：策略设计模式】
             */
            return instantiateBean(beanName, mbd);
        }
    }

    // 推断构造方法，获取候选的用来创建bean对象的构造函数
    Constructor<?>[] ctors = determineConstructorsFromBeanPostProcessors(beanClass, beanName);    
    // 获取到了构造函数 || 注入模式为使用构造函数 || bean定义中指定了带参数的构造函数 || 创建bean对象时的入参args[参数列表对应的值列表]不为null
    if (ctors != null ||
        mbd.getResolvedAutowireMode() == RootBeanDefinition.AUTOWIRE_CONSTRUCTOR ||
        mbd.hasConstructorArgumentValues() || !ObjectUtils.isEmpty(args))  {
        // 使用构造函数及入参进行bean对象的创建（有参构造）
        return autowireConstructor(beanName, mbd, ctors, args);
    }

    /**
     * 如果上述情况都没有：没有创建bean的回调方法 && 没有工厂方法 && 构造函数的参数未解析完毕 && 没有预先指定的默认构造函数
     * 则使用默认策略来创建bean对象（无参构造）
     */
    return instantiateBean(beanName, mbd);
}
```
从createBeanInstance方法可以知道实例化对象一共有三种策略：
- **使用工厂方法创建**：`instantiateUsingFactoryMethod` 。
- **使用有参构造函数创建**：`autowireConstructor`。
- **使用无参构造函数创建**：`instantiateBean`。

###### 1) 工厂方法`instantiateUsingFactoryMethod`
[参考详细博客：Spring 通过工厂方法(Factory Method)来配置bean](https://blog.csdn.net/nvd11/article/details/51542360)

使用工厂方法创建，会先使用 `getBean` 获取工厂类，然后通过参数找到匹配的工厂方法，调用实例化方法实现实例化。  
具体实现见`org.springframework.beans.factory.support.ConstructorResolver#instantiateUsingFactoryMethod` ：
```java
public BeanWrapper instantiateUsingFactoryMethod ... (
    // ...
    String factoryBeanName = mbd.getFactoryBeanName();
    // ...
    factoryBean = this.beanFactory.getBean(factoryBeanName);
    // ...
    // 匹配正确的工厂方法
    // ...
    beanInstance = this.beanFactory.getInstantiationStrategy().instantiate(...);
    // ...
    bw.setBeanInstance(beanInstance);
    return bw;
}
```

###### 2) 有参构造autowireConstructor
使用有参构造函数创建，整个过程比较复杂，涉及到参数和构造器的匹配。为了找到匹配的构造器，`Spring`花了大量的工作。  
具体实现见 `ConstructorResolver.autowireConstructor` ：
```java
public BeanWrapper autowireConstructor(final String beanName, final RootBeanDefinition mbd,
                                       @Nullable Constructor<?>[] chosenCtors, @Nullable final Object[] explicitArgs) {
    // ...
    try {
        final InstantiationStrategy strategy = beanFactory.getInstantiationStrategy();
        Object beanInstance;

        if (System.getSecurityManager() != null) {
            final Constructor<?> ctorToUse = constructorToUse;
            final Object[] argumentsToUse = argsToUse;
            beanInstance = AccessController.doPrivileged((PrivilegedAction<Object>) () ->
                                                         strategy.instantiate(mbd, beanName, beanFactory, ctorToUse, argumentsToUse),
                                                         beanFactory.getAccessControlContext());
        }
        else {
            // 匹配构造函数的过程
            beanInstance = strategy.instantiate(mbd, beanName, this.beanFactory, constructorToUse, argsToUse);
        }

        bw.setBeanInstance(beanInstance);
        return bw;
    }
    catch (Throwable ex) {
        // ...
    }
}           
```

###### 3) 无参构造`instantiateBean`（默认）
使用无参构造函数创建是最简单的方式。  
具体实现见 `AbstractAutowireCapableBeanFactory.instantiateBean`:
```java
// 使用默认的构造函数实例化bean；并且返回一个bean的包装类
protected BeanWrapper instantiateBean(final String beanName, final RootBeanDefinition mbd) {
    try {
        Object beanInstance;
        final BeanFactory parent = this;
        if (System.getSecurityManager() != null) {
            beanInstance = AccessController.doPrivileged(new PrivilegedAction<Object>() {
                @Override
                    public Object run() {
                    return getInstantiationStrategy().instantiate(mbd, beanName, parent);
                }
            }, getAccessControlContext());
        }
        else {
            /**
			* 默认使用的策略是Cglib；CglibSubclassingInstantiationStrategy();
			* 1. 判断是否设置lookup-method 或者replace-method，如果设置了则用Cglib策略实例化对象；
			* 2. 如果都没有设置，则利用默认的构造函数 反射生成实例化对象； 里面调用了 ctor.newInstance(args);
			*/
            beanInstance = getInstantiationStrategy().instantiate(mbd, beanName, parent);
        }
        BeanWrapper bw = new BeanWrapperImpl(beanInstance);
        initBeanWrapper(bw);
        return bw;
    }
    catch (Throwable ex) {
        // ...
    }
}
```

###### 小结
发现这三个实例化方式，最后都会走 `getInstantiationStrategy().instantiate(...)`。  
实现源码详见`SimpleInstantiationStrategy.instantiate`：
```java
@Override
public Object instantiate(RootBeanDefinition bd, @Nullable String beanName, BeanFactory owner) {
    // 判断bd对象定义里，是否包含methodOverrides列表；（Spring有两个标签参数会产生methodOverrides，分别是lookup-method、replaced-method）
    // bd对象中没有methodOverrides对象，可以直接实例化
    if (!bd.hasMethodOverrides()) {// （JDK代理）
        // 实例化对象的构造方法
        Constructor<?> constructorToUse;
        //  锁定对象，使获得实例化参数构造方法线程安全
        synchronized (bd.constructorArgumentLock) {
            // bd对象中没有methodOverrides对象是否含有resolvedConstructorOrFactoryMethod
            constructorToUse = (Constructor<?>) bd.resolvedConstructorOrFactoryMethod;
            // 没有则生成
            if (constructorToUse == null) {
                final Class<?> clazz = bd.getBeanClass();
                if (clazz.isInterface()) {
                    throw new BeanInstantiationException(clazz, "Specified class is an interface");
                }
                try {
                    if (System.getSecurityManager() != null) {
                        constructorToUse = AccessController.doPrivileged(
                            (PrivilegedExceptionAction<Constructor<?>>) clazz::getDeclaredConstructor);
                    }
                    else {
                        constructorToUse =	clazz.getDeclaredConstructor();
                    }
                    // 生成成功之后，赋值给bd对象。后续使用
                    bd.resolvedConstructorOrFactoryMethod = constructorToUse;
                }
                catch (Throwable ex) {
                    throw new BeanInstantiationException(clazz, "No default constructor found", ex);
                }
            }
        }
        // 使用反射生成对象
        return BeanUtils.instantiateClass(constructorToUse);
    }
    else {// (CGLI代理)
        // Must generate CGLIB subclass.
        // bd对象中有methodOverrides对象，使用另一种方式实现：子类的方式
        return instantiateWithMethodInjection(bd, beanName, owner);
    }
}
```
通过`instantiate`方法虽然拿到了构造函数，但并没有立即实例化。因为用户如果使用了 `lookup-method`和 `replaced-method`的配置方法，用到了动态代理加入对应的逻辑。如果没有的话，直接使用反射来创建实例。

##### 3.3.4. bean的最终实例化
通过上面的`createBean`方法执行之后的 `Bean` 还不是最终的 `Bean`。返回给调用方使用时，如果是 `FactoryBean` 的话需要使用 `getObject` 方法来创建实例。

**调用位置见doGetBean方法（第8步：使用合并后的定义进行实例化）：**
```java
bean = getObjectForBeanInstance(sharedInstance, name, beanName, mbd);
```

源码见 `AbstractBeanFactory.getObjectForBeanInstance` ，会执行到 `doGetObjectFromFactoryBean` ：
```java
protected Object getObjectForBeanInstance(
    Object beanInstance, String name, String beanName, @Nullable RootBeanDefinition mbd) {
    // 如果要获取的bean是FactoryBean的引用，但是beanInstance不是FactoryBean的就抛异常
    // 1. 判断输入的bean的name是否是工厂相关的（前缀是&） 
    if (BeanFactoryUtils.isFactoryDereference(name)) {
        if (beanInstance instanceof NullBean) {
            return beanInstance;
        }
        //name的前缀是&，但是类型不是FactoryBean，则抛出异常
        if (!(beanInstance instanceof FactoryBean)) {
            throw new BeanIsNotAFactoryException(transformedBeanName(name), beanInstance.getClass());
        }
    }

    // 2. 通过上面的判断可以确定这个bean实例，要么是个普通bean，要么是个FactoryBean
    // 第一个是判断：如果这个bean实例不是FactoryBean，就直接返回beanInstance，因为不是FactoryBean那肯定就是正常的bean了
    // 第二个是判断：如果本来期望返回的就是FactoryBean，那么也可以就直接返回了
    if (!(beanInstance instanceof FactoryBean) || BeanFactoryUtils.isFactoryDereference(name)) {
        return beanInstance;
    }

    Object object = null;
    if (mbd == null) {
        // 3. 尝试先从缓存获取bean
        object = getCachedObjectForFactoryBean(beanName);
    }
    if (object == null) {
        // 3. 强转为beanFactory。
        // 此时的beanInstance一定是FactoryBean类型的，因为如果不是，就会在上面的if中直接返回了
        FactoryBean<?> factory = (FactoryBean<?>) beanInstance;
        // 4. 检测这个bean是否已经被加载过
        // containsBeanDefinition中会返回beanDefinitionMap.containsKey(beanName)的值
        if (mbd == null && containsBeanDefinition(beanName)) {
            // 进行父类和子类的合并，把存储xml配置的GernericBeanDefinition转换为RootBeanDefinition
            mbd = getMergedLocalBeanDefinition(beanName);
        }
        // 判断mdb是否为空，以及检测是不是系统创建的
        boolean synthetic = (mbd != null && mbd.isSynthetic());
        // 5. 最终执行到这里才是需要的实例化bean（把核心功能托付给getObjectFromFactoryBean）
        object = getObjectFromFactoryBean(factory, beanName, !synthetic);
    }
    return object;
}
```

继续看`getObjectFromFactoryBean`方法的实现：
```java
// 从给定的 FactoryBean 中获取要实例化的对象。
protected Object getObjectFromFactoryBean(FactoryBean<?> factory, String beanName, boolean shouldPostProcess) {
    // 判断是否是单例，如果是单例，就不必重复创建
    if (factory.isSingleton() && containsSingleton(beanName)) {
        //加锁，避免同时创建
        synchronized (getSingletonMutex()) {
            //尝试从缓存获取
            Object object = this.factoryBeanObjectCache.get(beanName);
            if (object == null) {
                // 缓存中没有，尝试从factory中获取（获取bean的核心方法）
                object = doGetObjectFromFactoryBean(factory, beanName);
                // Only post-process and store if not put there already during getObject() call above
                // (e.g. because of circular reference processing triggered by custom getBean calls)
                //再次从缓存中获取，看有没有其他线程创建好的
                Object alreadyThere = this.factoryBeanObjectCache.get(beanName);
                // 如果有值，代表已经经过后处理了，可以直接返回
                if (alreadyThere != null) {
                    object = alreadyThere;
                }
                else {
                    //没有经过后处理，首先看是不是用户自己创建的
                    if (shouldPostProcess) {
                        if (isSingletonCurrentlyInCreation(beanName)) {
                            // Temporarily return non-post-processed object, not storing it yet..
                            return object;
                        }
                        beforeSingletonCreation(beanName);
                        try {
                            // 进行bean的后处理
                            // 对从 FactoryBean 获得的给定对象进行后处理。生成的对象将为 bean 引用公开。
                            // 默认实现只是按原样返回给定对象。子类可以覆盖它，例如，自定义后处理器。
                            object = postProcessObjectFromFactoryBean(object, beanName);
                        }
                        catch (Throwable ex) {
                            throw new BeanCreationException(beanName,
                                                            "Post-processing of FactoryBean's singleton object failed", ex);
                        }
                        finally {
                            // 将单例标记为不再处于创建状态
                            afterSingletonCreation(beanName);
                        }
                    }
                    //后处理完毕后，进行缓存
                    if (containsSingleton(beanName)) {
                        this.factoryBeanObjectCache.put(beanName, object);
                    }
                }
            }
            return object;
        }
    }
    // 不是单例的话，就直接创建新的返回就好
    else {
        // 获取bean的核心方法
        Object object = doGetObjectFromFactoryBean(factory, beanName);
        // 如果是用户自己创建的
        if (shouldPostProcess) {
            try {
                //进行后处理
                object = postProcessObjectFromFactoryBean(object, beanName);
            }
            catch (Throwable ex) {
                throw new BeanCreationException(beanName, "Post-processing of FactoryBean's object failed", ex);
            }
        }
        return object;
    }
}
```
**注意：`bean`的后处理方法`postProcessObjectFromFactoryBean`用于将`FactoryBean`中的`bean`暴露给子类进行覆写（可以通过后置处理器`post-processing`将`bean`进行替换）**

继续进入最终获取`bean`的核心方法`doGetObjectFromFactoryBean`：
```java
private Object doGetObjectFromFactoryBean(final FactoryBean<?> factory, final String beanName)
    throws BeanCreationException {
    //定义一个用于保存factory管理的对象实例的变量
    Object object;
    try {
        //如果有安全管理器
        if (System.getSecurityManager() != null) {
            //获取访问控制的上下文对象
            AccessControlContext acc = getAccessControlContext();
            try {
                //以特权方式运行来获取factory管理的对象实例赋值给object
                object = AccessController.doPrivileged((PrivilegedExceptionAction<Object>) factory::getObject, acc);
            }
            catch (PrivilegedActionException pae) {
                throw pae.getException();
            }
        }
        else {
            // 获取factory管理的对象实例赋值给object（真正的获取bean实例对象的代码）
            // 里面使用动态代理Proxy.newProxyInstance来进行bean实例对象的获取
            object = factory.getObject();
        }
    }
    //捕捉FactoryBean未初始化异常
    catch (FactoryBeanNotInitializedException ex) {
        //引用ex的异常描述，重新抛出当前正在创建Bean异常
        throw new BeanCurrentlyInCreationException(beanName, ex.toString());
    }
    //捕捉剩余的所有异常
    catch (Throwable ex) {
        //重新抛出Bean创建异常：FactoryBean在对象创建时引发异常
        throw new BeanCreationException(beanName, "FactoryBean threw exception on object creation", ex);
    }

    // Do not accept a null value for a FactoryBean that's not fully
    // initialized yet: Many FactoryBeans just return null then.
    // 不要为尚未完全初始化的 FactoryBean 接受 null 值：许多 FactoryBean 只返回 null。
    // 如果object为null
    if (object == null) {
        // 如果 beanName当前正在创建（在整个工厂内）
        if (isSingletonCurrentlyInCreation(beanName)) {
            // 抛出 当前正在创建Bean异常:当前正在创建的FactoryBean从getObject返回null
            throw new BeanCurrentlyInCreationException(
                beanName, "FactoryBean which is currently in creation returned null from getObject");
        }
        // 让object引用一个新的NullBean实例
        object = new NullBean();
    }
    // 返回 factory管理的对象实例【object】
    return object;
}
```
至此，`bean`实例创建完成；创建实例后，就可以开始 **注入属性** 和 **初始化** 等操作。

#### 3.4. 注入属性（属性填充）
实例创建完后开始进行属性的注入，如果涉及到外部依赖的实例，会自动检索并关联到当前实例。

**调用位置见doCreateBean方法（第2步：填充属性/注入属性）：**
```java
populateBean(beanName, mbd, instanceWrapper);
```

属性填充的入口方法在`org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory#populateBean`：
```java
protected void populateBean(String beanName, RootBeanDefinition mbd, @Nullable BeanWrapper bw) {
    if (bw == null) {
        if (mbd.hasPropertyValues()) {
            throw new BeanCreationException(
                mbd.getResourceDescription(), beanName, "Cannot apply property values to null instance");
        }
        else {
            // 空对象直接返回
            return;
        }
    }

    // 给InstantiationAwareBeanPostProcessors最后一次机会在属性注入前修改Bean的属性值
    // 具体通过调用postProcessAfterInstantiation方法，如果调用返回false,表示不必继续进行依赖注入，直接返回
    if (!mbd.isSynthetic() && hasInstantiationAwareBeanPostProcessors()) {
        for (BeanPostProcessor bp : getBeanPostProcessors()) {
            if (bp instanceof InstantiationAwareBeanPostProcessor) {
                InstantiationAwareBeanPostProcessor ibp = (InstantiationAwareBeanPostProcessor) bp;
                if (!ibp.postProcessAfterInstantiation(bw.getWrappedInstance(), beanName)) {
                    return;
                }
            }
        }
    }
    // pvs 是一个 MutablePropertyValues 实例，里面实现了PropertyValues接口，提供属性的读写操作实现，同时可以通过调用构造函数实现深拷贝
    PropertyValues pvs = (mbd.hasPropertyValues() ? mbd.getPropertyValues() : null);
    // 根据bean的依赖注入方式：即是否标注有 @Autowired 注解或 autowire=“byType/byName” 的标签
    // 会遍历bean中的属性，根据类型或名称来完成相应的注入
    int resolvedAutowireMode = mbd.getResolvedAutowireMode();
    if (resolvedAutowireMode == AUTOWIRE_BY_NAME || resolvedAutowireMode == AUTOWIRE_BY_TYPE) {
        // 深拷贝当前已有的配置
        MutablePropertyValues newPvs = new MutablePropertyValues(pvs);
        // 根据名称进行注入
        if (resolvedAutowireMode == AUTOWIRE_BY_NAME) {
            autowireByName(beanName, mbd, bw, newPvs);
        }
        // 根据类型进行注入
        if (resolvedAutowireMode == AUTOWIRE_BY_TYPE) {
            autowireByType(beanName, mbd, bw, newPvs);
        }
        // 结合注入后的配置，覆盖当前配置
        pvs = newPvs;
    }
    // 容器是否注册了InstantiationAwareBeanPostProcessor
    boolean hasInstAwareBpps = hasInstantiationAwareBeanPostProcessors();
    // 是否进行依赖检查
    boolean needsDepCheck = (mbd.getDependencyCheck() != AbstractBeanDefinition.DEPENDENCY_CHECK_NONE);

    PropertyDescriptor[] filteredPds = null;
    if (hasInstAwareBpps) {
        if (pvs == null) {
            // 过滤出所有需要进行依赖检查的属性编辑器
            pvs = mbd.getPropertyValues();
        }
        for (BeanPostProcessor bp : getBeanPostProcessors()) {
            // 如果有相关的后置处理器，进行后置处理
            if (bp instanceof InstantiationAwareBeanPostProcessor) {
                InstantiationAwareBeanPostProcessor ibp = (InstantiationAwareBeanPostProcessor) bp;
                PropertyValues pvsToUse = ibp.postProcessProperties(pvs, bw.getWrappedInstance(), beanName);
                if (pvsToUse == null) {
                    if (filteredPds == null) {
                        filteredPds = filterPropertyDescriptorsForDependencyCheck(bw, mbd.allowCaching);
                    }
                    pvsToUse = ibp.postProcessPropertyValues(pvs, filteredPds, bw.getWrappedInstance(), beanName);
                    if (pvsToUse == null) {
                        return;
                    }
                }
                pvs = pvsToUse;
            }
        }
    }
    if (needsDepCheck) {
        // 检查是否满足相关依赖关系，对应的depends-on属性，需要确保所有依赖的Bean先完成初始化
        if (filteredPds == null) {
            filteredPds = filterPropertyDescriptorsForDependencyCheck(bw, mbd.allowCaching);
        }
        checkDependencies(beanName, mbd, filteredPds, pvs);
    }

    if (pvs != null) {
        // 将pvs上所有的属性填充到BeanWrapper对应的Bean实例中
        applyPropertyValues(beanName, mbd, bw, pvs);
    }
}
```
可以看到主要的处理环节有：
- 应用 `InstantiationAwareBeanPostProcessor` 处理器，在属性注入前后进行处理。  
  **假设使用了 `@Autowire` 注解，这里会调用到 `AutowiredAnnotationBeanPostProcessor` 来对依赖的实例进行检索和注入的**，它是 `InstantiationAwareBeanPostProcessor` 的子类。
- 根据名称或者类型进行自动注入，存储结果到 `PropertyValues` 中。
- 应用 `PropertyValues`，填充到 `BeanWrapper`。这里在检索依赖实例的引用的时候，会递归调用 `BeanFactory.getBean` 来获得。

**注意：`InstantiationAwareBeanPostProcessor.postProcessAfterInstantiation()` 方法，可以决定程序是否继续进行属性填充。只要有一个 `InstantiationAwareBeanPostProcessor` 返回 `false`，都会终止属性填充的过程（第一步直接`return`）。**

#### 3.5. 初始化
##### 3.5.1. 触发 Aware
如果 `Bean` 需要容器的一些资源该怎么办？比如需要获取到 `BeanFactory`、`ApplicationContext` 等等。

`Spring` 提供了 `Aware` 系列接口来解决这个问题。比如有这样的 `Aware`：
- **BeanFactoryAware** ：用来获取 `BeanFactory`。
- **ApplicationContextAware** ：用来获取 `ApplicationContext`。
- **ResourceLoaderAware** ：用来获取 `ResourceLoaderAware`。
- **ServletContextAware** ：用来获取 `ServletContext`。

`Spring` 在初始化阶段，如果判断 `Bean` 实现了这几个接口之一，就会往 `Bean` 中注入它关心的资源。  
见 `org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory#invokeAwareMethods` :
```java
private void invokeAwareMethods(final String beanName, final Object bean) {
    // 如果Bean实现了Aware接口
    if (bean instanceof Aware) {
        // 如果实现了BeanNameAware接口，则调用Bean的setBeanName方法
        if (bean instanceof BeanNameAware) {
            ((BeanNameAware) bean).setBeanName(beanName);
        }
        // 如果实现了BeanClassLoaderAware接口，则调用Bean的setBeanClassLoader方法
        if (bean instanceof BeanClassLoaderAware) {
            ClassLoader bcl = getBeanClassLoader();
            if (bcl != null) {
                ((BeanClassLoaderAware) bean).setBeanClassLoader(bcl);
            }
        }
        // 如果实现了BeanFactoryAware接口，则调用Bean的setBeanFactory方法
        if (bean instanceof BeanFactoryAware) {
            ((BeanFactoryAware) bean).setBeanFactory(AbstractAutowireCapableBeanFactory.this);
        }
    }
}
```

##### 3.5.2. 触发 BeanPostProcessor
在 `Bean` 的初始化前或者初始化后，如果需要进行一些增强操作怎么办？  
这些增强操作比如 **打日志** 、 **做校验** 、 **属性修改** 、 **耗时检测** 等等。`Spring` 框架提供了 `BeanPostProcessor` 来达成这个目标，比如使用注解 `@Autowire` 来声明依赖，就是使用  `AutowiredAnnotationBeanPostProcessor` 来实现依赖的查询和注入的。

接口定义如下：
```java
public interface BeanPostProcessor {
    // 初始化前调用
    Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException;

    // 初始化后调用
    Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException;
}
```

**实现该接口的 `Bean` 都会被 `Spring` 注册到 `beanPostProcessors` 中** ，见 `AbstractBeanFactory` :
```java
/** BeanPostProcessors to apply in createBean */
private final List<BeanPostProcessor> beanPostProcessors = new ArrayList<BeanPostProcessor>();
```
只要 `Bean` 实现了 `BeanPostProcessor` 接口，加载的时候会被 `Spring` 自动识别这些 `Bean`，自动注册，非常方便。

然后在 `Bean` 实例化前后，`Spring` 会去调用已经注册的 `beanPostProcessors` 把处理器都执行一遍。
```java
public abstract class AbstractAutowireCapableBeanFactory ... {
    // ...

    @Override
    public Object applyBeanPostProcessorsBeforeInitialization ... {

        Object result = existingBean;
        for (BeanPostProcessor beanProcessor : getBeanPostProcessors()) {
            result = beanProcessor.postProcessBeforeInitialization(result, beanName);
            if (result == null) {
                return result;
            }
        }
        return result;
    }

    @Override
    public Object applyBeanPostProcessorsAfterInitialization ... {

        Object result = existingBean;
        for (BeanPostProcessor beanProcessor : getBeanPostProcessors()) {
            result = beanProcessor.postProcessAfterInitialization(result, beanName);
            if (result == null) {
                return result;
            }
        }
        return result;
    }

    // ...
}
```
这里使用了 **<font color='red'>责任链模式</font>** ，`Bean` 会在处理器链中进行传递和处理。

当我们调用 `BeanFactory.getBean` 之后，执行到 `Bean` 的初始化方法 `AbstractAutowireCapableBeanFactory.initializeBean` 会启动这些处理器。
```java
protected Object initializeBean(final String beanName, final Object bean, @Nullable RootBeanDefinition mbd) {
    if (System.getSecurityManager() != null) {
        AccessController.doPrivileged((PrivilegedAction<Object>) () -> {
            invokeAwareMethods(beanName, bean);
            return null;
        }, getAccessControlContext());
    }
    else {
        /**
         * 调用Bean实现的Aware接口的方法，主要包括下面三个接口
         * BeanNameAware ----> setBeanName()
         * BeanClassLoaderAware ----> setBeanClassLoader()
         * BeanFactoryAware  ----> setBeanFactory()
         */
        invokeAwareMethods(beanName, bean);
    }
    Object wrappedBean = bean;
    if (mbd == null || !mbd.isSynthetic()) {
        /** 调用Bean对象的postProcessBeforeInitialization方法，此处会执行标注@PostConstruct注解的方法 */
        wrappedBean = applyBeanPostProcessorsBeforeInitialization(wrappedBean, beanName);
    }
    try {
        /**
         * 执行Bean的初始化方法:
         *
         * 1.先判断Bean是否实现了InitializingBean接口，如果实现了InitializingBean接口，则调用Bean对象的afterPropertiesSet方法；
         * 2.然后判断Bean是否有指定init-method方法，如果指定了init-method方法，则调用bean对象的init-method指定的方法.
         */
        invokeInitMethods(beanName, wrappedBean, mbd);
    }
    catch (Throwable ex) {
        throw ex;// 抛异常简写.
    }
    if (mbd == null || !mbd.isSynthetic()) {
        /**
         * 调用Bean对象的postProcessAfterInitialization方法
         *
         * 如果需要创建代理，在该步骤中执行postProcessAfterInitialization方法的时候会去创建代理
         * 调用AbstractAutoProxyCreator类的postProcessAfterInitialization方法，然后调用wrapIfNecessary方法去创建代理.
         *
         * 另外还有一些Aware接口，也会在该步骤中执行，例如：ApplicationContextAwareProcessor后置处理器，对应的setApplicationContext方法会被执行.
         */
        wrappedBean = applyBeanPostProcessorsAfterInitialization(wrappedBean, beanName);
    }
    return wrappedBean;
}
```

##### 3.5.3. 触发自定义 init
自定义初始化有两种方式可以选择：
- 实现 `InitializingBean`。提供了一个很好的机会，在属性设置完成后再加入自己的初始化逻辑。
  ```java
  // 定义需要创建的bean--->MyTestBean
  // 实现了InitializingBean接口
  public class MyTestBean implements InitializingBean {
      public MyTestBean() {
          System.out.println("无参构造方法执行");
      }
      
      @Override
      public void afterPropertiesSet() throws Exception {
          // 加入自己的初始化逻辑....
      }
  }
  ```

- 定义 `init` 方法。自定义的初始化逻辑。
  ```java
  /**
   * 创建自定义的初始化方法
   */
  public void myInitMethod() {
      System.out.println("自定义的初始化方法");
  }
  
  /**
   * 创建bean时指定自定义的初始化方法
   */
  @Bean(initMethod = "myInitMethod")
  public MyTestBean myTestBean() {
      return new MyTestBean();
  }
  ```

源码见 `org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory#invokeInitMethods`：
```java
protected void invokeInitMethods(String beanName, final Object bean, @Nullable RootBeanDefinition mbd)
    throws Throwable {

    // 判断bean对象是否为InitializingBean的实例
    // 如果实现了InitializingBean接口，则只掉调用bean的afterPropertiesSet方法
    boolean isInitializingBean = (bean instanceof InitializingBean);
    if (isInitializingBean && (mbd == null || !mbd.isExternallyManagedInitMethod("afterPropertiesSet"))) {
        if (logger.isDebugEnabled()) {
            logger.debug("Invoking afterPropertiesSet() on bean with name '" + beanName + "'");
        }
        if (System.getSecurityManager() != null) {
            try {
                AccessController.doPrivileged((PrivilegedExceptionAction<Object>) () -> {
                    ((InitializingBean) bean).afterPropertiesSet();
                    return null;
                }, getAccessControlContext());
            }
            catch (PrivilegedActionException pae) {
                throw pae.getException();
            }
        }
        else {
            ((InitializingBean) bean).afterPropertiesSet();
        }
    }
    
    // 判断是否指定了init-method方法，如果指定了init-method方法，而且初始化方法不是afterPropertiesSet
    // 则通过反射执行指定的初始化方法。就是为了init-method也指定afterPropertiesSet而导致重复执行
    if (mbd != null && bean.getClass() != NullBean.class) {
        String initMethodName = mbd.getInitMethodName();
        if (StringUtils.hasLength(initMethodName) &&
            !(isInitializingBean && "afterPropertiesSet".equals(initMethodName)) &&
            !mbd.isExternallyManagedInitMethod(initMethodName)) {
            // 调用init-method方法
            invokeCustomInitMethod(beanName, bean, mbd);
        }
    }
}
```

#### 3.6. 注册销毁
上述过程执行完之后，这个`Bean`已经可以投入使用了，在返回使用之前还需要判断其在 **容器关闭** 的时候是否需要执行 **销毁** 逻辑。

该逻辑在`org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory#doCreateBean`方法最后部分调用：
```java
protected Object doCreateBean(final String beanName, final RootBeanDefinition mbd, final @Nullable Object[] args)
    throws BeanCreationException {
    
    // ...
    // Register bean as disposable.
    try {
        // 注册销毁
        registerDisposableBeanIfNecessary(beanName, bean, mbd);
    }
    catch (BeanDefinitionValidationException ex) {
        throw new BeanCreationException(
            mbd.getResourceDescription(), beanName, "Invalid destruction signature", ex);
    }

    return exposedObject;
}
```

该逻辑的源码位于`AbstractBeanFactory`类的`registerDisposableBeanIfNecessary`方法中，核心代码如下：
```java
protected void registerDisposableBeanIfNecessary(String beanName, Object bean, RootBeanDefinition mbd) {
    AccessControlContext acc = (System.getSecurityManager() != null ? getAccessControlContext() : null);
    // 1. 如果不是多例的 && 需要被销毁
    if (!mbd.isPrototype() && requiresDestruction(bean, mbd)) {
        // 2. 如果是单实例Bean
        if (mbd.isSingleton()) {
            // 如果当前的bean不是空Bean && (存在着销毁方法 || (实现了DestructionAwareBeanPostProcessor接口 && requiresDestruction后置方法返回值为true))
            // 如果存在着（销毁方法 || 需要被销毁） && 是单例Bean 
            // 则会将当前的bean保存到一个disposableBeans对应的Map集合中，map的key为bean名称，value为要被销毁的bean
            registerDisposableBean(beanName,
                                   new DisposableBeanAdapter(bean, beanName, mbd, getBeanPostProcessors(), acc));
        }
        else {
            // 除了prototype之外其他作用域的Bean，则注册自定义的bean销毁回调方法
            Scope scope = this.scopes.get(mbd.getScope());
            if (scope == null) {
                throw new IllegalStateException("No Scope registered for scope name '" + mbd.getScope() + "'");
            }
            scope.registerDestructionCallback(beanName,
                                              new DisposableBeanAdapter(bean, beanName, mbd, getBeanPostProcessors(), acc));
        }
    }
}
```

上述注册逻辑中的`requiresDestruction`方法（ **第一步：需要被销毁** ）的源码如下：
```java
protected boolean requiresDestruction(Object bean, RootBeanDefinition mbd) {
    /**
    * 这里的判断分了好几块
    * 1.首先这个bean不能使NullBean
    * 2.bean中需要包含destroy方法
    * 3.后置处理器中包含了destory方法，也就是通过@PreDestory注解的方法
    * 4.如果实现了InitDestroyAnnotationBeanPostProcessor生命周期回调的接口，那么是会有初始化的方法和销毁方法
    * spring默认添加了InitDestroyAnnotationBeanPostProcessor这个后置处理器，而这个后置处理器是表示
    * 如果找到了@PreDestroy注解的方法也会返回true（这个判断很简单，判断是否是实现了DestructionAwareBeanPostProcessor
    * 这个后置处理器，如果实现了，那么就去生命周期回调的销毁缓存中找，如果找到了销毁方法，那么就表示有销毁方法）
    * 反正逻辑都比较严谨，需要你结合上下文来理解
    */
    return (bean.getClass() != NullBean.class &&  // 1. 不是NullBean
            (DisposableBeanAdapter.hasDestroyMethod(bean, mbd) || // 2. 存在着销毁方法，实现了DisposableBean接口或者Autocloseable接口
             // 3. 实现了DestructionAwareBeanPostProcessor，而且对应的requiresDestruction方法返回了true【Spring的一个扩展点，可以自定义是否需要销毁】
             (hasDestructionAwareBeanPostProcessors()
              && DisposableBeanAdapter.hasApplicableProcessors(bean, getBeanPostProcessors()))));
}
```

那么如何判断当前`bean`中是否存在着销毁方法呢？  
通过`DisposableBeanAdapter`类的`hasDestroyMethod`方法（ **上述requiresDestruction的第二个判断条件** ）来判断，核心源码如下：
```java
/**
 * Check whether the given bean has any kind of destroy method to call.
 * @param bean the bean instance
 * @param beanDefinition the corresponding bean definition
 *  这个是判断是否有销毁方法的代码逻辑
 *  分为两段逻辑：
 *  1.如果实现了   DisposableBean或者AutoCloseable则直接返回；
 *  2.否则看是否有初始化方法，这个初始化方法是从BeanDefinition中获取的getDestroyMethodName
 *   如果getDestroyMethodName是默认的   (inferred)，则判断是否有close或者shutdown方法，有的话返回true
 *                       否则直接返回程序员手动设置的初始化方法
 */
public static boolean hasDestroyMethod(Object bean, RootBeanDefinition beanDefinition) {
    // 1. bean实现了DisposableBean接口或者AutoCloseable接口
    // 如果bean实现了DisposableBean或者AutoCloseable则表示这个bean有销毁的方法，直接返回true
    if (bean instanceof DisposableBean || bean instanceof AutoCloseable) {
        return true;
    }
    // 2. 存在着(inferred)方法【注意：一般如果未配置，默认的destroyMethod名称就是这个】，而且bean定义对应的class中存在着名称为close或者shutdown的方法
       /**
    * 否则进入下面的逻辑
    * 首先获取BeanDefinition中的销毁方法，如果这个销毁方法不为空，一般在xml中或者@Bean可以设置一个销毁方法
    * 在xml中要自己去设置销毁方法，而@Bean如果你不设置，会生成一个默认的方法
    * String destroyMethod() default AbstractBeanDefinition.INFER_METHOD
    * 还有一个地方可以设置，前面说了有一个bean的后置处理器，叫合并bean的后置处理器
    * 只要你实现了MergedBeanDefinitionPostProcessor，那么你可以实现它的方法
    * postProcessMergedBeanDefinition来获取BeanDefinition设置销毁和初始化方法
    * 这里的判断
    * 1.首先如果destroyMethodName==‘(inferred)’，那么就只需要在bean中添加一个close或者shutdown的方法
    * 那么spring的销毁的时候会自动调用close或者shutdown方法
    */
    String destroyMethodName = beanDefinition.getDestroyMethodName();
    if (AbstractBeanDefinition.INFER_METHOD.equals(destroyMethodName)) {
        return (ClassUtils.hasMethod(bean.getClass(), CLOSE_METHOD_NAME) ||
                ClassUtils.hasMethod(bean.getClass(), SHUTDOWN_METHOD_NAME));
    }
    
    return StringUtils.hasLength(destroyMethodName);
}
```

#### 3.7. 放入单实例缓存池
`Bean`的生命周期过程执行完毕之后，此时`Bean`就是一个容器中可以使用的`Bean`。这个已经创建完成的`Bean`会被保存到`Spring`的`单实例缓存池singletonObjects`中。  
（ **对应的步骤是getBean方法中的第7.1.2 步** ）
```java
// Create bean instance.
// 7. 开始创建Bean实例
// 7.1 创建Bean实例：单例
if (mbd.isSingleton()) {
    // 7.1.2 createBean执行完成之后调用getSingleton方法获取已经创建成功并放入单实例缓存池的单例对象
    sharedInstance = getSingleton(beanName, () -> {
        try {
            // 7.1.1 真正创建bean的方法
            return createBean(beanName, mbd, args);
        }
        catch (BeansException ex) {
            destroySingleton(beanName);
            throw ex;
        }
    });
    // 使用合并后的定义进行实例化
    bean = getObjectForBeanInstance(sharedInstance, name, beanName, mbd);
}
```

进入`org.springframework.beans.factory.support.DefaultSingletonBeanRegistry#getSingleton`方法中，该方法内部主要有两个方法：
```java
public Object getSingleton(String beanName, ObjectFactory<?> singletonFactory) {
    Assert.notNull(beanName, "Bean name must not be null");
    synchronized (this.singletonObjects) {
        // 创建 singletonObject
        Object singletonObject = this.singletonObjects.get(beanName);
        if (singletonObject == null) {
            // .....

            try {
                singletonObject = singletonFactory.getObject();
                newSingleton = true;
            }
            catch (IllegalStateException ex) {
                // Has the singleton object implicitly appeared in the meantime ->
                // if yes, proceed with it since the exception indicates that state.
                singletonObject = this.singletonObjects.get(beanName);
                if (singletonObject == null) {
                    throw ex;
                }
            }

            // .....

            if (newSingleton) {
                // 将 singletonObject 放入单实例缓存池singletonObjects中
                addSingleton(beanName, singletonObject);
            }
        }
        return singletonObject;
    }
}
```

继续进入`addSingleton`方法中，如下所示：
```java
protected void addSingleton(String beanName, Object singletonObject) {
    synchronized (this.singletonObjects) {
        /** 将创建好的单实例bean放入到单例缓存池中 */
        this.singletonObjects.put(beanName, singletonObject);
        /** 从三级缓存中删除 */
        this.singletonFactories.remove(beanName);
        /** 从二级缓存中删除(早期对象：已经实例化，但是未完成属性赋值的对象) */
        this.earlySingletonObjects.remove(beanName);
        /** 保存到已注册单实例Bean名称集合中 */
        this.registeredSingletons.add(beanName);
    }
}
```

#### 3.8. 类型转换
**`Bean` 已经加载完毕，属性也填充好了，初始化也完成了，注册销毁也完成了。**

在返回给调用者之前，还需要对 `Bean` 实例进行类型的转换。见 `org.springframework.beans.factory.support.AbstractBeanFactory#doGetBean` ：
```java
protected <T> T doGetBean(final String name, @Nullable final Class<T> requiredType,
                          @Nullable final Object[] args, boolean typeCheckOnly) throws BeansException {
    // ...
    // Check if required type matches the type of the actual bean instance.
    // 检查所需类型是否与实际 bean 实例的类型匹配。
    if (requiredType != null && !requiredType.isInstance(bean)) {
        try {
            T convertedBean = getTypeConverter().convertIfNecessary(bean, requiredType);
            if (convertedBean == null) {
                throw new BeanNotOfRequiredTypeException(name, requiredType, bean.getClass());
            }
            return convertedBean;
        }
        catch (TypeMismatchException ex) {
            if (logger.isDebugEnabled()) {
                logger.debug("Failed to convert bean '" + name + "' to required type '" +
                             ClassUtils.getQualifiedName(requiredType) + "'", ex);
            }
            throw new BeanNotOfRequiredTypeException(name, requiredType, bean.getClass());
        }
    }
    return (T) bean;
}
```

## 三、Bean的销毁
### 1. 关闭的时机（什么时候被销毁）
`Spring` **上下文容器** 启动时会在`JVM`中注册一个钩子函数`AbstractApplicationContext#registerShutdownHook()` ，当容器关闭时会触发该函数，源码如下：

`org.springframework.context.support.AbstractApplicationContext#registerShutdownHook`
```java
@Override
public void registerShutdownHook() {
    if (this.shutdownHook == null) {
        // No shutdown hook registered yet.
        this.shutdownHook = new Thread(SHUTDOWN_HOOK_THREAD_NAME) {
            @Override
            public void run() {
                synchronized (startupShutdownMonitor) {
                    doClose();
                }
            }
        };
        Runtime.getRuntime().addShutdownHook(this.shutdownHook);
    }
}
```
最终调用的是`doClose()`方法执行容器关闭以及容器中`bean`的销毁等一些列操作。

### 2. 源码分析
`org.springframework.context.support.AbstractApplicationContext#doClose`
```java
/**
 * Actually performs context closing: publishes a ContextClosedEvent and
 * destroys the singletons in the bean factory of this application context.
 * 实际执行上下文关闭：发布一个 ContextClosedEvent 并销毁此应用程序上下文的 bean 工厂中的单例。
 *
 * <p>Called by both {@code close()} and a JVM shutdown hook, if any.
 * @see org.springframework.context.event.ContextClosedEvent
 * @see #destroyBeans()
 * @see #close()
 * @see #registerShutdownHook()
 */
protected void doClose() {
    // 判断当前context是否处于活跃状态，如果是的话，就使用cas操作将closed设置为true，否则直接退出
    if (this.active.get() && this.closed.compareAndSet(false, true)) {
        if (logger.isDebugEnabled()) {
            logger.debug("Closing " + this);
        }
        // 取消LiveBeanView的注册
        LiveBeansView.unregisterApplicationContext(this);

        try {
            // 发布关闭事件的信号
            publishEvent(new ContextClosedEvent(this));
        }
        catch (Throwable ex) {
            logger.warn("Exception thrown from ApplicationListener handling ContextClosedEvent", ex);
        }

        // 停止所有生命周期bean，以避免单个销毁过程中的延迟
        if (this.lifecycleProcessor != null) {
            try {
                // 关闭生命周期处理器
                this.lifecycleProcessor.onClose();
            }
            catch (Throwable ex) {
                logger.warn("Exception thrown from LifecycleProcessor on context close", ex);
            }
        }

        // 销毁缓存的所有单例bean
        destroyBeans();

        // 关闭context的状态
        closeBeanFactory();

        // 子类实现的关闭方法，可以进行一些子类希望的做的操作，这个方法由子类实现
        onClose();

        // 如果监听器不为空的话，就将其清空
        if (this.earlyApplicationListeners != null) {
            this.applicationListeners.clear();
            this.applicationListeners.addAll(this.earlyApplicationListeners);
        }

        // 销毁所有的单例bean，并将监听器清空后，将active设置为false，证明context被正常关闭
        this.active.set(false);
    }
}
```

继续进入`destroyBeans`方法：  
`org.springframework.context.support.AbstractApplicationContext#destroyBeans`
```java
protected void destroyBeans() {
    getBeanFactory().destroySingletons();
}
```

继续进入`destroySingletons`方法：  
`org.springframework.beans.factory.support.DefaultSingletonBeanRegistry#destroySingletons`
```java
public void destroySingletons() {
    if (logger.isTraceEnabled()) {
        logger.trace("Destroying singletons in " + this);
    }
    // 标记当前正处于bean销毁的状态
    synchronized (this.singletonObjects) {
        this.singletonsCurrentlyInDestruction = true;
    }

    // 拿到了所有实现了DisposableBean接口的所有Bean的名字
    String[] disposableBeanNames;
    synchronized (this.disposableBeans) {
        disposableBeanNames = StringUtils.toStringArray(this.disposableBeans.keySet());
    }
    // 开始遍历这些Bean,为它们调用destroySingleton函数
    for (int i = disposableBeanNames.length - 1; i >= 0; i--) {
        destroySingleton(disposableBeanNames[i]);
    }

    // 对依赖关系的清除
    this.containedBeanMap.clear();
    this.dependentBeanMap.clear();
    this.dependenciesForBeanMap.clear();

    // 调用clearSingletonCache函数来清空单例缓存（包含解决循环依赖的缓存等）
    clearSingletonCache();
}
```

继续进入`destroySingleton`方法  
`org.springframework.beans.factory.support.DefaultSingletonBeanRegistry#destroySingleton`
```java
public void destroySingleton(String beanName) {
    // 删除给定名称的已注册单例
    // 移除singletonObjects，singletonFactories，earlySingletonObjects以及registeredSingletons这几个集合中的Bean记录
    removeSingleton(beanName);

    // 销毁该Bean对应的 DisposableBean 实例
    DisposableBean disposableBean;
    synchronized (this.disposableBeans) {
        disposableBean = (DisposableBean) this.disposableBeans.remove(beanName);
    }
    
    // 调用destroyBean来执行真正的销毁操作
    destroyBean(beanName, disposableBean);
}
```

继续进入`destroyBean`方法  
`org.springframework.beans.factory.support.DefaultSingletonBeanRegistry#destroyBean`
```java
/**
 * 注意：因为bean之间存在依赖，所以必须在销毁目标bean 本身之前销毁目标bean所依赖的beanName集合中的依赖（即dependentBeanMap）
 */
protected void destroyBean(String beanName, @Nullable DisposableBean bean) {
    // 1. 首先触发依赖bean的销毁
    Set<String> dependencies;
    synchronized (this.dependentBeanMap) {
        dependencies = this.dependentBeanMap.remove(beanName);
    }
    if (dependencies != null) {
        if (logger.isTraceEnabled()) {
            logger.trace("Retrieved dependent beans for bean '" + beanName + "': " + dependencies);
        }
        for (String dependentBeanName : dependencies) {
            // 2. 销毁依赖的bean
            destroySingleton(dependentBeanName);
        }
    }

    if (bean != null) {
        try {
            // 3. 开始执行真正的bean销毁
            bean.destroy();
        }
        catch (Throwable ex) {
            if (logger.isWarnEnabled()) {
                logger.warn("Destruction of bean with name '" + beanName + "' threw an exception", ex);
            }
        }
    }

    // ......
    // 后续的逻辑和第1步类似
    // 从其他 bean 的依赖项中销毁当前已经被销毁的 bean
}
```

继续进入`bean.destroy();`方法  
`org.springframework.beans.factory.support.DisposableBeanAdapter#destroy`
```java
@Override
public void destroy() {
    //1.先调用DestructionAwareBeanPostProcessor后置销毁逻辑
    // 如基于注解实现的销毁（被@PreDestroy注解的方法）
    if (!CollectionUtils.isEmpty(this.beanPostProcessors)) {
        for (DestructionAwareBeanPostProcessor processor : this.beanPostProcessors) {
            processor.postProcessBeforeDestruction(this.bean, this.beanName);
        }
    }
    // 2.调用bean实现的DisposableBean#destroy逻辑（bean自定义实现的destroy方法）
    if (this.invokeDisposableBean) {
        if (logger.isTraceEnabled()) {
            logger.trace("Invoking destroy() on bean with name '" + this.beanName + "'");
        }
        try {
            if (System.getSecurityManager() != null) {
                AccessController.doPrivileged((PrivilegedExceptionAction<Object>) () -> {
                    ((DisposableBean) this.bean).destroy();
                    return null;
                }, this.acc);
            }
            else {
                // 实现DisposableBean 销毁
                ((DisposableBean) this.bean).destroy();
            }
        }
        catch (Throwable ex) {
            String msg = "Invocation of destroy method failed on bean with name '" + this.beanName + "'";
            if (logger.isDebugEnabled()) {
                logger.warn(msg, ex);
            }
            else {
                logger.warn(msg + ": " + ex);
            }
        }
    }
    // 3.调用自定义销毁逻辑destroy-method（即在bean标签中声明的destroy-method，如：@Bean(destroyMethod = "destroy1")）
    if (this.destroyMethod != null) {
        // 自定义销毁方法
        invokeCustomDestroyMethod(this.destroyMethod);
    }
    else if (this.destroyMethodName != null) {
        Method methodToInvoke = determineDestroyMethod(this.destroyMethodName);
        if (methodToInvoke != null) {
            // 自定义销毁方法
            invokeCustomDestroyMethod(ClassUtils.getInterfaceMethodIfPossible(methodToInvoke));
        }
    }
}
```

`DisposableBeanAdapter的destroy()`销毁逻辑做了排序：
1. 优先调用`DestructionAwareBeanPostProcessor`的 `postProcessBeforeDestruction`方法（即被`@PreDestroy`注解的方法）
   ```java
   @Documented
   @Retention (RUNTIME)
   @Target(METHOD)
   public @interface PreDestroy {
   }
   ```

2. 然后调用`bean`自定义实现的`DisposableBean#destroy`
   ```java
   public interface DisposableBean {
   	void destroy() throws Exception;
   }
   ```

3. 最后调用`自定义销毁逻辑`
   ```java
   // @Bean注解的destroyMethod参数指定的方法destroy1为自定义销毁方法
   @Bean(destroyMethod = "destroy1")
   public static MyTestBean myTestBean() {
       return new MyTestBean();
   }
   ```

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/bean销毁顺序.png)
</center>

### 3. 小结
销毁逻辑详细流程：
1. **AbstractApplicationContext#registerShutdownHook -->** 容器运行时注册到`JVM`中的钩子函数，用于容器关闭时触发一系列关闭逻辑；
2. **AbstractApplicationContext#doClose -->** 容器关闭逻辑：包含 **关闭bean工厂** 、 **销毁bean** 、 **清空bean缓存**等操作；
3. **AbstractApplicationContext#destroyBeans -->** 调用当前`bean`对应工厂的`bean`注销逻辑；
4. **DefaultSingletonBeanRegistry#destroySingletons -->** 获取所有实现了`DisposableBean`接口的所有`Bean`、清除依赖关系、清除`bean`缓存；
5. **DefaultSingletonBeanRegistry#destroySingleton -->** 移除`singletonObjects`、`singletonFactories`、`earlySingletonObjects`以及`registeredSingletons`这几个集合中的`Bean`记录；并销毁该`Bean`对应的 `DisposableBean` 实例；
6. **DefaultSingletonBeanRegistry#destroyBean -->** 单个`bean`的销毁逻辑：包含 **销毁bean自身** 、 **清除对目标bean依赖** 和 **被依赖的关系**（`dependentBeanMap`）；  
   **注意：必须在销毁目标`bean` 本身之前销毁目标`bean`所依赖的`beanName集合`中的依赖**
7. **DisposableBeanAdapter#destroy** 实际的销毁逻辑。包含三种方式且按照顺序执行：
   - 被`@PreDestroy`注解的方法
   - 然后调用`bean`自定义实现的`DisposableBean#destroy`
   - 最后调用`自定义销毁逻辑`

### 4. 补充：销毁Bean的三种方法代码实现
通过上面的源码分析可以知道定义销毁有如下三种方式：
- `@PreDestroy` Java标准注解
- 实现`DisposableBean的Destroy()`方法
- 自定义销毁方法
  - `XML` 配置:`<bean destroy="destroy" ... />`
  - `Java注解` `@Bean(destroy="destroy")`
  - `Java API` `AbstractBeanDefinition#setDestroyMethodName(String)`

创建用于注入的测试类：
```java
/**
 * 用于注入的测试类
 *
 * 包含bean创建过程中扩展的分支处理，包括InitializingBean、DisposableBean
 * 包含自定义初始化方法initMethod以及自定义销毁方法destroy1
 */
public class MyTestBean implements InitializingBean, DisposableBean {

    public MyTestBean() {
        System.out.println("1-->无参构造方法执行");
    }

    @PostConstruct
    public void init() {
        System.out.println("2-->PostConstruct init");
    }

    public void initMethod() {
        System.out.println("4-->自定义的初始化方法");
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("3-->afterPropertiesSet");
    }

    @Override
    public void destroy() throws Exception {
        System.out.println("6-->Spring默认的bean销毁方法DisposableBean.destroy()");
    }

    public void destroy1() {
        System.out.println("7-->@Bean(destroyMethod = \"destroy1\") 自定义销毁方法");
    }

    // 使用注解配置的销毁方法
    @PreDestroy
    public void destroyAnnotation() {
        System.out.println("5-->使用@PreDestroy注解配置的销毁方法destroy执行");
    }
}
```

创建测试类：
```java
/**
 * 测试类
 *
 * 包含注解配置的销毁方法以及类的注入
 */
public class DemoApplication {
    public static void main(String[] args) {
        // 创建Spring上下文
        AnnotationConfigApplicationContext ac = new AnnotationConfigApplicationContext();
        // 将测试类注册到Spring中
        ac.register(DemoApplication.class);
        ac.refresh();
        System.out.println("Spring 上下文启动完成。。。。。");

        // 创建MyDefaultFactory对应的bean
        final MyTestBean bean = ac.getBean(MyTestBean.class);

        System.out.println("Spring 上下文准备关闭。。。。。");
        // 手动调用AnnotationConfigApplicationContext.close()方法触发销毁操作（或registerShutdownHook()方法）
        // ac.registerShutdownHook();
        ac.close();
        System.out.println("Spring 上下文已关闭。。。。。");
    }


    // 定义初始化方法（initMethod）以及自定义的销毁方法（destroy1）
    @Bean(initMethod = "initMethod", destroyMethod = "destroy1")
    public static MyTestBean myTestBean() {
        return new MyTestBean();
    }
}
```

执行结果：
```
Spring 上下文创建完成。。。。。
1-->无参构造方法执行
2-->PostConstruct init
3-->afterPropertiesSet
4-->自定义的初始化方法
Spring 上下文启动完成。。。。。
Spring 上下文准备关闭。。。。。
5-->Spring默认的bean销毁方法DisposableBean#destroy
6-->@Bean(destroyMethod = "destroy1") 自定义销毁方法
7-->使用@PreDestroy注解配置的销毁方法destroy执行
Spring 上下文已关闭。。。。。
```
以上三种 `Bean` 的销毁方式也是可以组合使用的，那么组合在一起的调用顺序是什么呢？
1. 首先 `@PreDestroy` 会被调用
2. 其次 `DisposableBean.destroy()` 会被调用
3. 最后调用通过 `XML` 配置的 `destroy-method` 方法或通过设置 `@Bean` 注解 设置 `destroyMethod` 属性的方法

**<font color='red'>@PreDestroy ---> DisposableBean#destroy() ---> 自定义销毁方法（含XML配置的自定义方法）</font>**

**注意：** 测试三种销毁方法组合使用的时候，三种销毁方法一定要写在一个类中进行测试，因为 **容器在加载 `Bean` 时是顺序的** ；如果不是在同一个类中加载，可能会出现测试结果不准确的情况。

## 四、总结
### 1. Bean生命周期概括（4步）
整体的生命周期可以概括为四个步骤：
- 创建 （`AbstractAutowireCapableBeanFactory#doCreateBean()`）
  1. **实例化 Instantiation** ：`doCreate()`中的`createBeanInstance()` 
  2. **属性赋值 Populate** ：`doCreate()`中的`populateBean()`
  3. **初始化 Initialization** ：`doCreate()`中的`initializeBean()`
- 销毁（）
  4. **销毁 Destruction** ：`DisposableBeanAdapter#destroy()`

### 2. Bean生命周期详细（关键步骤）
> **下面是Spring 中Bean的核心接口和生命周期，不包含额外的相关分支接口**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/bean生命周期概述.png)
</center>

————————————初始化————————————
1. Spring启动，查找并加载需要被Spring管理的`Bean`，进行`Bean`的实例化
2. `Bean`实例化后对将`Bean`的引入和值注入到`Bean`的属性中
3. 如果Bean实现了`BeanNameAware`接口的话：Spring将`Bean`的`Id`传递给`setBeanName()`方法
4. 如果Bean实现了`BeanFactoryAware`接口的话：Spring将调用`setBeanFactory()`方法，将`BeanFactory`容器实例传入
5. 如果Bean实现了`ApplicationContextAware`接口的话：Spring将调用`Bean`的`setApplicationContext()`方法，将`Bean`所在应用上下文引用传入进来。
6. 如果Bean实现了`BeanPostProcessor`接口：Spring就将调用他们的`postProcessBeforeInitialization()`方法。
7. 如果Bean实现了`InitializingBean`接口：Spring将调用他们的`afterPropertiesSet()`方法。类似的，如果`Bean`使用`init-method`声明了初始化方法，该方法也会被调用
8. 如果Bean实现了`BeanPostProcessor`接口：Spring就将调用他们的`postProcessAfterInitialization()`方法。
9. **此时，`Bean`已经准备就绪，可以被应用程序使用了。他们将一直驻留在应用上下文中，直到应用上下文被销毁。**

————————————销毁————————————
1. 如果bean实现了`DisposableBean`接口：Spring将调用它的`destory()`接口方法；同样，如果`Bean`使用了`destory-method` 声明销毁方法或通过设置 `@Bean` 注解并配置 `destroyMethod` 属性，该方法也会被调用。

## 附1：处理循环依赖
### 1. 简述
先将bean的实例化大致分为三步：
1. 阶段一（`createBeanInstance`）：获取完整定义并实例化，其实也就是调用对象的构造方法实例化对象
2. 阶段二（`populateBean`）： **填充属性** 、 **依赖注入（注入其他对象）** ，这一步主要是多`bean`的依赖属性进行填充
3. 阶段三（`initializeBean`）：完成初始化。

**什么是循环依赖？**  
举个例子，这里有三个类 `A`、`B`、`C`，然后 `A依赖B`，`B依赖C`，`C又依赖A`，这就形成了一个 **循环依赖** 。

**注意：如果是方法调用是不算循环依赖的，循环依赖必须要持有引用。**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/循环依赖简易示意图.png)
</center>

循环依赖根据注入的 **时机** 分成两种类型：
- **构造器循环依赖**： 依赖的对象是通过构造器传入的，发生在实例化 `Bean` 的时候。
- **设值循环依赖**： 依赖的对象是通过 `setter` 方法传入的，对象已经实例化，发生属性填充和依赖注入的时候。

**如果是构造器循环依赖，本质上是无法解决的**。比如准备调用 `A` 的构造器时，发现依赖 `B`，于是去调用 `B` 的构造器进行实例化，发现又依赖 `C`，于是调用 `C` 的构造器去初始化，结果依赖 `A`，整个形成一个死结，导致 `A` 永远无法创建。

**如果是设值循环依赖，`Spring` 框架只支持（解决）单例下的设值循环依赖**。`Spring` 通过对还在创建过程中的单例，缓存并 **<font color="red">提前</font>** 暴露该单例，使得其他实例可以引用该依赖。

### 2. 原型模式的循环依赖
**<font color='red'>Spring 不支持原型模式的任何循环依赖</font>** 。检测到循环依赖会直接抛出 `BeanCurrentlyInCreationException` 异常。

使用了一个 `ThreadLocal` 变量 `prototypesCurrentlyInCreation` 来记录当前线程正在创建中的 `Bean` 对象。  
见 `AbtractBeanFactory#prototypesCurrentlyInCreation`和`AbtractBeanFactory#doGetBean`：
```java
/** 当前正在创建的 bean 的名称 */
/** Names of beans that are currently in creation */
private final ThreadLocal<Object> prototypesCurrentlyInCreation =
    new NamedThreadLocal<>("Prototype beans currently in creation");

protected <T> T doGetBean ... {
    // ...
    // Fail if we're already creating this bean instance:
    // We're assumably within a circular reference.
    if (isPrototypeCurrentlyInCreation(beanName)) {
        throw new BeanCurrentlyInCreationException(beanName);
    }
    // ...
}
```

在 `Bean` 创建前进行记录，在 `Bean` 创建后删除记录。  
见 `AbstractBeanFactory.doGetBean`：
```java
protected <T> T doGetBean ... {
    // ...
    if (mbd.isPrototype()) {
        // It's a prototype -> create a new instance.
        Object prototypeInstance = null;
        try {
            // 向prototypesCurrentlyInCreation添加记录
            beforePrototypeCreation(beanName);
            prototypeInstance = createBean(beanName, mbd, args);
        }
        finally {
            // 从prototypesCurrentlyInCreation删除记录
            afterPrototypeCreation(beanName);
        }
        bean = getObjectForBeanInstance(prototypeInstance, name, beanName, mbd);
    }
    // ...
}
```

见 `AbtractBeanFactory.beforePrototypeCreation` 的 **记录操作** ：
```java
// 向prototypesCurrentlyInCreation添加记录
protected void beforePrototypeCreation(String beanName) {
    Object curVal = this.prototypesCurrentlyInCreation.get();
    if (curVal == null) {
        this.prototypesCurrentlyInCreation.set(beanName);
    }
    else if (curVal instanceof String) {
        Set<String> beanNameSet = new HashSet<String>(2);
        beanNameSet.add((String) curVal);
        beanNameSet.add(beanName);
        this.prototypesCurrentlyInCreation.set(beanNameSet);
    }
    else {
        Set<String> beanNameSet = (Set<String>) curVal;
        beanNameSet.add(beanName);
    }
}
```

见 `AbtractBeanFactory.afterPrototypeCreation` 的 **删除操作** ：
```java
// 从prototypesCurrentlyInCreation删除记录
protected void afterPrototypeCreation(String beanName) {
    Object curVal = this.prototypesCurrentlyInCreation.get();
    if (curVal instanceof String) {
        this.prototypesCurrentlyInCreation.remove();
    }
    else if (curVal instanceof Set) {
        Set<String> beanNameSet = (Set<String>) curVal;
                                   beanNameSet.remove(beanName);
        if (beanNameSet.isEmpty()) {
            this.prototypesCurrentlyInCreation.remove();
        }
    }
}
```
**<font color="red">注意：为了节省内存空间，在单个元素时 `prototypesCurrentlyInCreation` 对象只记录 `String` 对象，在多个依赖元素后改用 `Set` 集合。这里是 `Spring` 使用的一个节约内存的小技巧。</font>**

了解完`prototypesCurrentlyInCreation`记录的写入和删除过程，再来看看读取以及判断循环的方式。  
这里要分两种情况讨论：
- 构造函数循环依赖。
- 设值循环依赖。

这两个地方的实现略有不同：  
如果是构造函数依赖的，比如 `A` 的构造函数依赖了 `B`，会有这样的情况。实例化 `A` 的阶段中，匹配到要使用的构造函数，发现构造函数有参数 `B`，会使用 `BeanDefinitionValueResolver` 来检索 `B` 的实例。  
见 `BeanDefinitionValueResolver.resolveReference`：
```java
private Object resolveReference(Object argName, RuntimeBeanReference ref) {

    // ...
    Object bean = this.beanFactory.getBean(refName);
    // ...
}
```

可以发现这里继续调用 `beanFactory.getBean` 去加载 `B`。  
如果是设值循环依赖的的，比如这里不提供构造函数，并且使用了 `@Autowire` 的方式注解依赖（还有其他方式不举例了）：
```java
public class A {
    @Autowired
    private B b;
    ...
}
```
加载过程中，找到无参数构造函数，不需要检索构造参数的引用，实例化成功。接着执行下去，进入到属性填充阶段 `AbtractBeanFactory.populateBean` ，在这里会进行 `B` 的依赖注入。

为了能够获取到 `B` 的实例化后的引用，最终会通过检索类 `DependencyDescriptor` 中去把依赖读取出来。  
见 `DependencyDescriptor.resolveCandidate` ：
```java
public Object resolveCandidate(String beanName, Class<?> requiredType, BeanFactory beanFactory)
    throws BeansException {
    return beanFactory.getBean(beanName, requiredType);
}
```
发现 `beanFactory.getBean` 方法又被调用到了。

**在这里，两种循环依赖达成了统一** 。无论是构造函数的循环依赖还是设置循环依赖，在需要注入依赖的对象时，会继续调用 `beanFactory.getBean` 去加载对象，形成一个 **递归操作** 。  
而每次调用 `beanFactory.getBean` 进行实例化前后，都使用了 `prototypesCurrentlyInCreation` 这个变量做记录。按照这里的思路走，整体效果等同于 **建立依赖对象的构造链**。

`prototypesCurrentlyInCreation` 中的值的变化过程如下：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/循环依赖-原型模式简易示意图.png)
</center>


调用判定的地方在 `AbstractBeanFactory.doGetBean` 中，所有对象的实例化均会从这里启动。
```java
/** 当前正在创建的 bean 的名称 */
/** Names of beans that are currently in creation */
private final ThreadLocal<Object> prototypesCurrentlyInCreation =
    new NamedThreadLocal<>("Prototype beans currently in creation");

protected <T> T doGetBean ... {
    // ...
    // Fail if we're already creating this bean instance:
    // We're assumably within a circular reference.
    // 在一个循环引用中
    if (isPrototypeCurrentlyInCreation(beanName)) {
        throw new BeanCurrentlyInCreationException(beanName);
    }
    // ...
}
```

判定的实现方法为 `AbstractBeanFactory.isPrototypeCurrentlyInCreation` ：
```java
protected boolean isPrototypeCurrentlyInCreation(String beanName) {
    Object curVal = this.prototypesCurrentlyInCreation.get();
    return (curVal != null &&
            (curVal.equals(beanName) || (curVal instanceof Set && ((Set<?>) curVal).contains(beanName))));
}
```
所以在原型模式下，构造函数循环依赖和设值循环依赖，本质上使用同一种方式检测出来。`Spring`是无法解决的，直接抛出 `BeanCurrentlyInCreationException` 异常。

### 3. 单例模式的构造循环依赖
**<font color='red'>Spring也不支持单例模式的构造循环依赖</font>** 。检测到构造循环依赖也会抛出 `BeanCurrentlyInCreationException` 异常。

和原型模式相似，单例模式也用了一个数据结构来记录正在创建中的 `beanName`。  
见 `org.springframework.beans.factory.support.DefaultSingletonBeanRegistry`:
```java
/** Names of beans that are currently in creation */
/** 当前正在创建的 bean 的名称 */
private final Set<String> singletonsCurrentlyInCreation =
            Collections.newSetFromMap(new ConcurrentHashMap<String, Boolean>(16));
```

也会在创建前进行记录，创建化后删除记录。  
见 `DefaultSingletonBeanRegistry.getSingleton`：
```java
public Object getSingleton(String beanName, ObjectFactory<?> singletonFactory) {
    // ...

    // 记录正在加载中的 beanName
    beforeSingletonCreation(beanName);

    // ...

    // 通过 singletonFactory 创建 bean
    singletonObject = singletonFactory.getObject();

    //...

    // 删除正在加载中的 beanName
    afterSingletonCreation(beanName);
    
    //...
}
```

记录和判定的方式见`DefaultSingletonBeanRegistry.beforeSingletonCreation` ：
```java
/** Names of beans that are currently in creation */
/** 当前正在创建的 bean 的名称 */
/** 注意：singletonsCurrentlyInCreation是一个set集合 */
private final Set<String> singletonsCurrentlyInCreation =
    Collections.newSetFromMap(new ConcurrentHashMap<>(16));

protected void beforeSingletonCreation(String beanName) {
    // 判断如果已经存在则抛出异常
    if (!this.inCreationCheckExclusions.contains(beanName) && !this.singletonsCurrentlyInCreation.add(beanName)) {
        throw new BeanCurrentlyInCreationException(beanName);
    }
}
```
这里会尝试往 `singletonsCurrentlyInCreation` 记录当前实例化的 `bean`。我们知道 `singletonsCurrentlyInCreation` 的数据结构是 `Set`，是不允许重复元素的，**所以一旦前面记录了，这里的 `add` 操作将会返回失败**。

比如加载 `A` 的单例，和原型模式类似，单例模式也会调用匹配到要使用的构造函数，发现构造函数有参数 `B`，然后使用 `BeanDefinitionValueResolver` 来检索 `B` 的实例，根据上面的分析，继续调用 `beanFactory.getBean` 方法。

所以拿 `A`、`B`、`C` 的例子来举例 `singletonsCurrentlyInCreation` 的变化，这里可以看到和原型模式的循环依赖判断方式的算法是一样：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/循环依赖-原型模式简易示意图.png)
</center>

单例模式的构造循环依赖过程：
- 加载 A：记录 `singletonsCurrentlyInCreation = [a]`，构造依赖 B，开始加载 B。
- 加载 B：记录 `singletonsCurrentlyInCreation = [a, b]`，构造依赖 C，开始加载 C。
- 加载 C：记录 `singletonsCurrentlyInCreation = [a, b, c]`，构造依赖 A，又开始加载 A。
- 加载 A：执行到 `DefaultSingletonBeanRegistry.beforeSingletonCreation` ，`singletonsCurrentlyInCreation` 中 `a` 已经存在了，检测到构造循环依赖， **直接抛出异常结束操作** 。

### 4. 单例模式的设值循环依赖
**<font color='red'>单例模式下，构造函数的循环依赖依旧无法解决，但`setter`设值循环依赖是可以解决的</font>。**

这里有一个重要的设计： **<font color='red'>提前暴露创建中的单例</font>** 。

还是拿上面的 `A`、`B`、`C` 的的设值依赖做分析，步骤如下：
- ==> 1. A 创建 --> A 构造完成；开始注入属性，发现依赖 B，启动 B 的实例化
- ==> 2. B 创建 --> B 构造完成；开始注入属性，发现依赖 C，启动 C 的实例化
- ==> 3. C 创建 --> C 构造完成；开始注入属性，发现依赖 A

重点来了，在`阶段1`中， `A` 已经构造完成，`A`的`Bean` 对象在堆中也分配好内存了，即使后续往 `A` 中填充属性（比如填充依赖的 `B` 对象），也不会修改到 `A` 的引用地址。

所以，这个时候是否可以 **提前拿 `A` 实例的引用来先注入到 `C`** ，去完成 `C` 的实例化，于是流程就变成这样：
- ==> 3. C 创建 -->  C 构造完成； **开始注入依赖，发现依赖 A，发现 A 已经构造完成，直接引用，完成 C 的实例化。**
- ==> 4. C 完成实例化后，B 注入 C 也完成实例化，A 注入 B 也完成实例化。

这就是 `Spring` 解决单例模式设值循环依赖应用的技巧。单例模式创建流程的具体流程图为：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Spring/Spring核心之Bean实例化（生命周期，循环依赖等）/Spring解决单例模式设值循环依赖示意图.png)
</center>

补充：从上面的流程图上看，实际上注入 `C` 的 `A` 实例，还在 **填充属性阶段，并没有完全初始化** 。等递归回溯回去，`A` 顺利拿到依赖 `B`，才会真实地完成 `A` 的加载。

为了能够实现单例的提前暴露。`Spring` 使用了三级缓存，见`DefaultSingletonBeanRegistry`：
```java
/** Cache of singleton objects: bean name --> bean instance */
private final Map<String, Object> singletonObjects = new ConcurrentHashMap<String, Object>(256);

/** Cache of singleton factories: bean name --> ObjectFactory */
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<String, ObjectFactory<?>>(16);

/** Cache of early singleton objects: bean name --> bean instance */
private final Map<String, Object> earlySingletonObjects = new HashMap<String, Object>(16);
```

这三个缓存的作用及区别如下：
- **第一层缓存（`singletonObjects`）** ：单例对象缓存池，存储已经实例化并且属性赋值，这里的对象是 **成熟对象** 。
- **第二层缓存（`earlySingletonObjects`）** ：生产单例的工厂的缓存，存储工厂，也是单例对象缓存池，包含已经实例化但尚未属性赋值，这里的对象是 **半成品对象** ；。
- **第三层缓存（`singletonFactories`）** ：提前暴露的单例缓存，这时候的单例刚刚创建完，但还会注入依赖。

从 `getBean("a")` 开始，添加的 `SingletonFactory` 具体实现如下：
```java
protected Object doCreateBean ...  {

    // ...
    addSingletonFactory(beanName, new ObjectFactory<Object>() {
        @Override
        public Object getObject() throws BeansException {
            return getEarlyBeanReference(beanName, mbd, bean);
        }
    });
    // ...
}
```
可以看到如果使用该 `SingletonFactory` 获取实例，使用的是 `getEarlyBeanReference` 方法，返回一个未初始化的引用。

读取缓存的地方见 `DefaultSingletonBeanRegistry` :
```java
@Nullable
protected Object getSingleton(String beanName, boolean allowEarlyReference) {
    // 1. 先从 singletonObjects（一级缓存）尝试获取
    Object singletonObject = this.singletonObjects.get(beanName);
    // 如果没有数据
    if (singletonObject == null && isSingletonCurrentlyInCreation(beanName)) {
        synchronized (this.singletonObjects) {
            // 2. 获取不到而且对象在建立中，则尝试从earlySingletonObjects(二级缓存)中获取
            singletonObject = this.earlySingletonObjects.get(beanName);
            // 如果仍是获取不到而且容许从singletonFactories经过getObject获取
            if (singletonObject == null && allowEarlyReference) {
                ObjectFactory<?> singletonFactory = this.singletonFactories.get(beanName);
                if (singletonFactory != null) {
                    // 3. 则经过singletonFactory.getObject()(三级缓存)获取
                    singletonObject = singletonFactory.getObject();
                    // 4. 最后将获取到的singletonObject放入到earlySingletonObjects，也就是将三级缓存提高到二级缓存中
                    this.earlySingletonObjects.put(beanName, singletonObject);
                    this.singletonFactories.remove(beanName);
                }
            }
        }
    }
    return singletonObject;
}
```
执行步骤：
1. 先从 `singletonObjects`（一级缓存）尝试获取
2. 如果没有数据，获取不到而且对象在建立中，则尝试从`earlySingletonObjects`（二级缓存）中获取
3. 如果仍是获取不到而且容许从`singletonFactories`经过`getObject`获取，则经过`singletonFactory.getObject()`（三级缓存）获取
4. 最后将获取到的`singletonObject`放入到`earlySingletonObjects`，也就是将三级缓存提高到二级缓存中

补充一些方法和参数
- 这个 `this.earlySingletonObjects` 的好处是，如果此时又有其他地方尝试获取未初始化的单例，可以从 `this.earlySingletonObjects` 直接取出而不需要再调用 `getEarlyBeanReference`。
- `isSingletonCurrentlyInCreation()`：判断当前单例`bean`是否正在建立中，也就是没有初始化完成（好比 **A对象** 的构造器依赖了 **B对象** 因此得先去建立 **B对象** ， 或则在 **A对象** 的`populateBean`——属性填充过程当中依赖了 **B对象** ，得先去建立 **B对象** ，这时的 **A对象** 就是处于建立中的状态。）
- `allowEarlyReference`：是否容许从`singletonFactories`中经过`getObject`拿到对象

小结：  
从上面三级缓存的分析，`Spring`解决循环依赖的诀窍就在于`singletonFactories`这个三级`cache`。这个`cache`的类型是`ObjectFactory`：
```java
/** Cache of singleton factories: bean name --> ObjectFactory */
private final Map<String, ObjectFactory<?>> singletonFactories = new HashMap<>(16);

// ObjectFactory的定义
public interface ObjectFactory<T> {
    T getObject() throws BeansException;
}
```

在`bean`建立过程当中，有一个比较重要的 **匿名内部类** 实现了该接口:
```java
protected Object doCreateBean ...  {
    // Instantiate the bean.
    BeanWrapper instanceWrapper = null;
    if (mbd.isSingleton()) {
        instanceWrapper = this.factoryBeanInstanceCache.remove(beanName);
    }
    if (instanceWrapper == null) {
        instanceWrapper = createBeanInstance(beanName, mbd, args);
    }
    
    // ...
    
    addSingletonFactory(beanName, () -> getEarlyBeanReference(beanName, mbd, bean));
    
    // ...
}
```
此处就是解决循环依赖的关键，这段代码发生在`createBeanInstance`以后，也就是说单例对象此时已经被建立出来的。这个对象已经被生产出来了，虽然还不完美（尚未进行初始化的第二步和第三步），可是已经能被人认出来了（根据对象引用能定位到堆中的对象），因此`Spring`此时将这个对象提早曝光出来，让你们使用（循环依赖主要发生在 **第一步** 、 **第二步** 。也就是构造器循环依赖和field循环依赖。）

举例说明单例模式的设值循环依赖步骤：
1. `A对象` `setter`依赖`B对象`，`B对象` `setter`依赖`A对象`
2. `A`首先完成了初始化的第一步，而且将本身提早曝光到`singletonFactories（三级缓存）`中，
3. 此时`A`开始进行初始化的第二步，发现本身依赖`对象B`，
4. 然后`A`就尝试去`get(B)`，发现`B`尚未被`create`，因此`B`开始走`create`流程，`B`在初始化第一步的时候发现本身依赖了对象`A`，
5. 然后`B`就尝试去`get(A)`，
   1. `B`尝试一级缓存`singletonObjects`（肯定没有，因为`A`还没初始化彻底），
   2. `B`继续尝试二级缓存`earlySingletonObjects`（也没有），
   3. `B`再尝试三级缓存`singletonFactories`，因为`A`经过`ObjectFactory`将本身提早曝光了，因此`B`可以经过`ObjectFactory.getObject`拿到`A`对象( **半成品** )，
   4. `B`拿到`A对象`后顺利完成了初始化阶段一、二、三，彻底初始化以后将本身放入到一级缓存`singletonObjects`中。
   5. 最后返回`A`中
6. `A`此时能拿到`B`完整的对象顺利完成本身的初始化阶段二、三，
7. 最终`A`也完成了初始化，进去了一级缓存`singletonObjects`中，并且更加幸运的是，因为`B`拿到了`A`的对象引用，因此`B`持有`A`对象并完成了初始化。

### 5. 补充：
#### 5.1 Spring为何不能解决非单例属性（设值）之外的循环依赖？
- **Spring为什么不能解决构造器的循环依赖？**  
  - 构造器注入形成的循环依赖：  
    也就是`beanB`需要在`beanA`的构造函数中完成初始化，`beanA`也需要在`beanB`的构造函数中完成初始化，这种情况的结果就是两个`Bean`都不能完成初始化，循环依赖难以解决。
  - `Spring`解决循环依赖主要是依赖 **三级缓存** ，但是的 **在调用构造方法之前还未将其放入三级缓存之中** ，因此后续的依赖调用构造方法的时候并不能从 **三级缓存** 中获取到依赖的`Bean`，因此不能解决。

- **Spring为什么不能解决prototype作用域循环依赖？**  
  这种循环依赖同样无法解决，因为`spring`不会缓存 **‘prototype’作用域的bean** ，而`spring`中循环依赖的解决正是通过 **缓存** 来实现的。

- **Spring为什么不能解决多例的循环依赖？**  
  多实例`Bean`是每次调用一次`getBean`都会执行一次构造方法并且给属性赋值，根本没有 **三级缓存** ，因此不能解决循环依赖。

#### 5.2 其它循环依赖如何解决？
- **生成代理对象产生的循环依赖**  
  这类循环依赖问题解决方法很多，主要有：
  1. 使用`@Lazy`注解，延迟加载
  2. 使用`@DependsOn`注解，指定加载先后关系
  3. 修改文件名称，改变循环依赖类的加载顺序

- **使用`@DependsOn`产生的循环依赖**  
  这类循环依赖问题要找到`@DependsOn`注解循环依赖的地方，迫使它不循环依赖就可以解决问题。

- **多例循环依赖**  
  这类循环依赖问题可以通过把`bean`改成单例的解决。

- **构造器循环依赖**  
  这类循环依赖问题可以通过使用`@Lazy`注解解决。

## 附2：Bean的生命周期代码演示
通过上面的介绍，可以知道 `Spring`提供了非常多的扩展点穿插在整个生命周期中，具体流程如下：
- 创建`Bean`实例
- 调用`Bean`中的`setter()`方法设置属性值
- 检查`Bean`是否实现了`Aware接口`，若实现了，则调用对应的接口方法
- 若容器中有`BeanPostProcessor`，则调用其`postProcessAfterInitialization`和`postProcessBeforeInitialization`方法
- 检查`Bean`是否实现了`InitializingBean`，若实现了，则调用其`afterPropertiesSet`方法
- 检查是否指定了`@Bean`注解的`init-method`属性，若指定了，则调用其指定的方法
- 检查`Bean`是否实现了`DisposableBean`，若实现了，则调用其`destroy()`方法
- 检查是否指定了`@Bean`注解的`destroy-method`属性，若指定了，则调用其指定的方法

**具体代码测试验证如下**  
创建`user`对象：
```java
/**
 * 创建user对象
 *
 * 包含bean创建过程中扩展的分支处理，包括ApplicationContextAware、InitializingBean、DisposableBean
 */
public class User implements ApplicationContextAware, InitializingBean, DisposableBean {

    private String name;
    private Integer age;

    public User() {
        System.out.println("1--》创建User实例");
    }

    public String getName() {
        return this.name;
    }

    public Integer getAge() {
        return this.age;
    }

    public void setName(String name) {
        this.name = name;
        System.out.println("2--》设置User的name属性");
    }

    public void setAge(Integer age) {
        this.age = age;
        System.out.println("2--》设置User的age属性");
    }

    public void init() {
        System.out.println("6--》调用init-method属性指定的方法");
    }

    public void myDestroy() {
        System.out.println("9--》调用destroy-method属性指定的方法");
    }

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        System.out.println("3--》调用对应Aware接口的方法");
    }

    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("5--》调用InitializingBean接口的afterPropertiesSet方法");
    }

    @Override
    public void destroy() throws Exception {
        System.out.println("8--》调用DisposableBean接口的destroy方法");
    }
}
```

定义一个`Bean`的后置处理器：
```java
/**
 * Bean的后置处理器
 * 这个后置处理器针对的是所有的Bean
 */
public class MyBeanPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("7--》调用MyBeanPostProcessor的postProcessBeforeInitialization方法");
        return BeanPostProcessor.super.postProcessAfterInitialization(bean, beanName);
    }

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        System.out.println("4--》调用MyBeanPostProcessor的postProcessAfterInitialization方法");
        return BeanPostProcessor.super.postProcessBeforeInitialization(bean, beanName);
    }
}
```

将`User`对象注册到容器中：
```java
/**
 * 将User对象注册到容器中
 * 并且指定User-Bean对应的初始化和销毁方法以及Bean的后置处理器
 */
@Configuration
public class MyBeanConfig {

    @Bean(initMethod = "init", destroyMethod = "myDestroy")
    public User user() {
        User user = new User();
        user.setName("admin");
        user.setAge(18);
        return user;
    }

    @Bean
    public BeanPostProcessor beanPostProcessor() {
        return new MyBeanPostProcessor();
    }
}
```

测试代码：
```java
@SpringBootTest
public class AppTest {
    @Autowired
    User user;

    @Test
    public void userBeanTest() {
        System.out.println("========" + user.getName());
        System.out.println("========" + user.getAge());
    }
}
```

执行结果：
```
1--》创建User实例
2--》设置User的name属性
2--》设置User的age属性
3--》调用对应Aware接口的方法
4--》调用MyBeanPostProcessor的postProcessAfterInitialization方法
5--》调用InitializingBean接口的afterPropertiesSet方法
6--》调用init-method属性指定的方法
7--》调用MyBeanPostProcessor的postProcessBeforeInitialization方法
========admin
========18
8--》调用DisposableBean接口的destroy方法
9--》调用destroy-method属性指定的方法
```
`Spring`依次调用了每个扩展点，熟悉了整个`Bean`的 **生命周期** 和 **扩展点** 之后，就能够在每个阶段做想做的事情，实现业务的定制化。
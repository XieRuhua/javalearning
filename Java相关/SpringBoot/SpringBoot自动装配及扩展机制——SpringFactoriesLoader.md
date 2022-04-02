# SpringBoot自动装配及扩展机制 —— SpringFactoriesLoader
> **该笔记对应的SpringBoot的版本为 2.6.1**

[文档内容参考1：Springboot自动装配 ](https://www.cnblogs.com/wangstudyblog/p/15364583.html)  
[文档内容参考2：SpringBoot自动装配原理 ](https://segmentfault.com/a/1190000038810569)  

[toc]

## 一、什么是自动装配
>**`SpringBoot` 定义了一套接口规范，这套规范规定：`SpringBoot` 在启动时会扫描外部引用 jar 包中的`META-INF/spring.factories`文件，将文件中配置的类型信息加载到 `Spring` 容器中，并执行类中定义的各种操作。**

对于外部 `jar` 来说，只需要按照 `SpringBoot` 定义的标准，就能将自己的功能**装配进** `SpringBoot。`

**举例：**  
假设我们要引入redis
```xml
<dependency>
   <groupId> org.springframework.boot </groupId>
   <artifactId> spring-boot-starter-data-redis </artifactId>
</dependency>
```
然后在`application.properties`配置`Redis`数据源
```
spring.redis.host=localhost
spring.redis.port=6379
```
当我们需要操作`redis`时只需要
```java
@Autowired
RedisTemplate<String,String> redisTemplate
```
这个`RedisTemplate`实例时何时注入容器的？ 这个注入的过程就是 **自动装配**

## 二、自动装配原理
SpringBoot项目启动类一般写法：
```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class MainApplication {
    public static void main(String[] args) {
        SpringApplication.run(MainApplication.class, args);
    }
}
```
上述代码，是一个`springboot`的应用程序的**入口类**，想要了解`springboot`是如何装配的，需要了解 **`@SpringBootApplication`** 这个注解。

### @SpringBootApplication
```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@SpringBootConfiguration
@EnableAutoConfiguration
@ComponentScan(excludeFilters = {
		@Filter(type = FilterType.CUSTOM, classes = TypeExcludeFilter.class),
		@Filter(type = FilterType.CUSTOM, classes = AutoConfigurationExcludeFilter.class) })
public @interface SpringBootApplication {
    .................
}
```
**它主要加载了`@SpringBootApplication`注解主配置类，这个`@SpringBootApplication`注解主配置类里边最主要的功能就是SpringBoot开启自动配置。**

`@SpringBootApplication`其是一个合并注解，但其中最重要的三个注解分别是：
* **`@SpringBootConfiguration`：** 允许在上下文中注册额外的 `bean` 或导入其他配置类
* **`@EnableAutoConfiguration`：** 启用 `SpringBoot` 的自动配置机制
* **`@ComponentScan`：** 扫描被 **`@Component` （如`@Service`，@`Controller`）** 注解的 `bean`，注解默认会扫描启动类所在的包下所有的类 ，可以自定义不扫描某些 `bean`。容器中将排除 **`TypeExcludeFilter`** 和 **`AutoConfigurationExcludeFilter`** 。

下面来依次分析这三个主要的注解：
### 1. @SpringBootConfiguration
```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Configuration
public @interface SpringBootConfiguration {

}
```
`@SpringBootConfiguration` 也是来源于 **`@Configuration`** ，二者功能都是将当前类标注为配置类，并将当前类里以 `@Bean` 注解标记的方法的实例注入到`Spring容器`中。

至于`@Configuration`，作用是配置`Spring容器`，**用于定义配置类**。

### 2. @EnableAutoConfiguration：实现自动装配的核心注解（重点）
这个注解可以帮助我们自动载入应用程序所需要的所有默认配置。
```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@AutoConfigurationPackage // 作用：将main包下所有的组件注册到容器中
@Import(AutoConfigurationImportSelector.class)
public @interface EnableAutoConfiguration {

	String ENABLED_OVERRIDE_PROPERTY = "spring.boot.enableautoconfiguration";

	/**
	 * Exclude specific auto-configuration classes such that they will never be applied.
	 * @return the classes to exclude
	 */
	Class<?>[] exclude() default {};

	/**
	 * Exclude specific auto-configuration class names such that they will never be
	 * applied.
	 * @return the class names to exclude
	 * @since 1.3.0
	 */
	String[] excludeName() default {};

}
```
这个注解上有两个比较特殊的注解 **<font color="red">@AutoConfigurationPackage</font>** 和 **<font color="red">@Import(AutoConfigurationImportSelector.class)</font>**
#### 2.1 @AutoConfigurationPackage ：自动配置包
```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Inherited
@Import(AutoConfigurationPackages.Registrar.class)
public @interface AutoConfigurationPackage {

}
```
* **`@import`：** Spring底层注解`@import`，给容器中导入一个组件
* **`AutoConfigurationPackages.Registrar.class`：** 作用：将主启动类的所在包及包下面所有子包里面的所有组件扫描到Spring容器 ；

#### 2.2 @Import(AutoConfigurationImportSelector.class)
给容器导入组件 **`AutoConfigurationImportSelector`（自动配置导入选择器）**。

#### 2.3 @EnableAutoConfiguration装配过程
`@EnableAutoConfiguration` 注解启用自动配置，其可以帮助 `SpringBoot` 应用将所有符合条件的 `@Configuration` 配置都加载到当前 `IoC 容器`之中，如下图：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/@EnableAutoConfiguration装配过程.png)
</center>

通过源码分析一下`@EnableAutoConfiguration`的装配过程：

**@EnableAutoConfiguration 借助 AutoConfigurationImportSelector 的帮助，而后者通过实现 `selectImports()` 方法来导出 `Configuration`。**
  
`AutoConfigurationImportSelector`类的继承体系如下：
```java
// AutoConfigurationImportSelector类部分源码
public class AutoConfigurationImportSelector
		implements DeferredImportSelector, BeanClassLoaderAware, ResourceLoaderAware,
		BeanFactoryAware, EnvironmentAware, Ordered {
	....................
	....................
	....................
    public String[] selectImports(AnnotationMetadata annotationMetadata) {
        if (!this.isEnabled(annotationMetadata)) {
            return NO_IMPORTS;
        } else {
            AutoConfigurationImportSelector.AutoConfigurationEntry autoConfigurationEntry = this.getAutoConfigurationEntry(annotationMetadata);
            return StringUtils.toStringArray(autoConfigurationEntry.getConfigurations());
        }
    }
	....................
	....................
	....................
}
            ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓
                [implements]
            ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓
// DeferredImportSelector接口部分源码
public interface DeferredImportSelector extends ImportSelector {
    ...............
}
            ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓
                [implements]
            ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓ ↓
// ImportSelector接口部分源码
public interface ImportSelector {
	/**
	 * Select and return the names of which class(es) should be imported based on
	 * the {@link AnnotationMetadata} of the importing @{@link Configuration} class.
	 */
	String[] selectImports(AnnotationMetadata importingClassMetadata);
}
```
可以看出，`AutoConfigurationImportSelector` 类实现了 `ImportSelector接口`中的`selectImports方法`，**该方法主要用于获取所有符合条件的类的 `全限定类名` ，这些类需要被加载到 `IoC 容器`中。** 

`getAutoConfigurationEntry方法`注释说明：
```java
protected AutoConfigurationEntry getAutoConfigurationEntry(AutoConfigurationMetadata autoConfigurationMetadata, AnnotationMetadata annotationMetadata) {
   // 1. 检查自动装配开关
   if (!isEnabled(annotationMetadata)) {
      return EMPTY_ENTRY;
   }
   // 2. 获取EnableAutoConfiguration中的参数，exclude()/excludeName()
   AnnotationAttributes attributes = getAttributes(annotationMetadata);
   // 3. 获取需要自动装配的所有配置类，读取META-INF/spring.factories
   List<String> configurations = getCandidateConfigurations(annotationMetadata, attributes);
   // 4. 去重,List转Set再转List
   configurations = removeDuplicates(configurations);
   // 5. 从EnableAutoConfiguration的exclude/excludeName属性中获取排除项
   Set<String> exclusions = getExclusions(annotationMetadata, attributes);
   // 6. 检查需要排除的类是否在configurations中，不在报错
   checkExcludedClasses(configurations, exclusions);
   // 7. 从configurations去除exclusions
   configurations.removeAll(exclusions);
   // 8. 对configurations进行过滤，剔除掉@Conditional条件不成立的配置类
   configurations = filter(configurations, autoConfigurationMetadata);
   // 9. 把AutoConfigurationImportEvent绑定在所有AutoConfigurationImportListener子类实例上
   fireAutoConfigurationImportEvents(configurations, exclusions);
   // 10. 返回(configurations, exclusions)组
   return new AutoConfigurationEntry(configurations, exclusions);
}
```

注意 **第3步** 调用的 **`getCandidateConfigurations`** 方法，源码如下：
```java
protected List<String> getCandidateConfigurations(AnnotationMetadata metadata, AnnotationAttributes attributes) {
	List<String> configurations = SpringFactoriesLoader.loadFactoryNames(getSpringFactoriesLoaderFactoryClass(),
			getBeanClassLoader());
	Assert.notEmpty(configurations, "No auto configuration classes found in META-INF/spring.factories. If you "
			+ "are using a custom packaging, make sure that file is correct.");
	return configurations;
}
```
最终通过 **`SpringFactoriesLoader.loadFactoryNames()`** 读取了 `ClassPath` 下面的 **`META-INF/spring.factories`** 文件来获取所有导出类。

继续进入**SpringFactoriesLoader.loadFactoryNames** 方法中：
```java
/**
 * 框架内内部使用的通用工厂加载器
 */
public final class SpringFactoriesLoader {
	/**
	 * The location to look for factories.
	 * <p>Can be present in multiple JAR files.
	 */
	public static final String FACTORIES_RESOURCE_LOCATION = "META-INF/spring.factories";
	
	....................
	....................
	....................
	
	public static List<String> loadFactoryNames(Class<?> factoryType, @Nullable ClassLoader classLoader) {
		ClassLoader classLoaderToUse = classLoader;
		if (classLoaderToUse == null) {
			classLoaderToUse = SpringFactoriesLoader.class.getClassLoader();
		}
		String factoryTypeName = factoryType.getName();
		return loadSpringFactories(classLoaderToUse).getOrDefault(factoryTypeName, Collections.emptyList());
	}

	private static Map<String, List<String>> loadSpringFactories(ClassLoader classLoader) {
		Map<String, List<String>> result = cache.get(classLoader);
		if (result != null) {
			return result;
		}

		result = new HashMap<>();
		try {
			Enumeration<URL> urls = classLoader.getResources(FACTORIES_RESOURCE_LOCATION);
			while (urls.hasMoreElements()) {
				URL url = urls.nextElement();
				UrlResource resource = new UrlResource(url);
				Properties properties = PropertiesLoaderUtils.loadProperties(resource);
				for (Map.Entry<?, ?> entry : properties.entrySet()) {
					String factoryTypeName = ((String) entry.getKey()).trim();
					String[] factoryImplementationNames =
							StringUtils.commaDelimitedListToStringArray((String) entry.getValue());
					for (String factoryImplementationName : factoryImplementationNames) {
						result.computeIfAbsent(factoryTypeName, key -> new ArrayList<>())
								.add(factoryImplementationName.trim());
					}
				}
			}

			// Replace all lists with unmodifiable lists containing unique elements
			result.replaceAll((factoryType, implementations) -> implementations.stream().distinct()
					.collect(Collectors.collectingAndThen(Collectors.toList(), Collections::unmodifiableList)));
			cache.put(classLoader, result);
		}
		catch (IOException ex) {
			throw new IllegalArgumentException("Unable to load factories from location [" +
					FACTORIES_RESOURCE_LOCATION + "]", ex);
		}
		return result;
	}
	
	....................
	....................
	....................
}
```

文件`META-INF/spring.factories`的位置：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/文件factories的位置.png)
</center>

内容：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/文件factories的内容.png)
</center>

**过程简单总结：**  
从 `ClassPath`下扫描所有的 **`META-INF/spring.factories`** 配置文件，并将`spring.factories` 文件中的 **`EnableAutoConfiguration` 对应的配置项通过反射机制实例化为对应标注了 `@Configuration` 的注解的`IoC容器`配置类，然后注入到`IoC容器`中**

注： **<font color="red">每一个`xxxAutoConfiguration`类都是容器中的一个组件（`starter`都需要自定义这个类以及`META-INF/spring.factories` 配置文件），并都加入到容器中。</font>** 加入到容器中之后的作用就是用它们来做自动配置，这就是Springboot自动 **配置之源** ，也就是自动配置的开始，只有这些自动配置类进入到容器中以后，接下来这个自动配置类才开始进行启动。

### 3. @ComponentScan
`@ComponentScan` **对应于`XML`配置形式中的 `context:component-scan`，** 用于将一些标注了特定注解的`bean`定义批量采集注册到Spring的`IoC容器`之中，这些特定的注解大致包括：
* @Controller/@RestController
* @Component
* @Service
* @Repository
* ........

对于该注解，还可以通过 `basePackages` 属性来更细粒度的控制该注解的自动扫描范围，比如：
```java
@ComponentScan(basePackages = {"com.test.controller","cn.test.entity"})
```

### 4. 补充点
#### 4.1. @AutoConfigurationPackage和@ComponentScan区别
* `@AutoConfigurationPackage`在默认的情况下就是将：**主配置类(`@SpringBootApplication`)的所在包及其子包里边的组件扫描到Spring容器中。**  
比如：用了 **`Spring Data JPA`** 之后，可能会在实体类上写`@Entity`注解。这个`@Entity`注解由`@AutoConfigurationPackage`扫描并加载。
* 而平时开发用的`@Controller`/`@Service`/`@Component`/`@Repository`这些注解是由`@omponentScan`来扫描并加载的。

即：这二者扫描的对象是不一样的：
* 前者是用来扫描springboot的自动装配，
* 后者主要用于程序员写的代码中的`@service`、`@controller`等这些声明的需要被自动注入的`bean`
> **@EnableAutoConfiguration注解的文档（类注释）解释：**  
it will be used when scanning for code @Entity classes. It is generally recommended that you place EnableAutoConfiguration (if you're not using @SpringBootApplication) in a root package so that all sub-packages and classes can be searched.  
它将在扫描代码@Entity 类时使用。通常建议您将 EnableAutoConfiguration（如果您不使用 @SpringBootApplication）放在根包中，以便可以搜索所有子包和类

#### 4.2 spring.factories中所有的配置类都会被加载？
`SpringBoot`所有自动配置类都是在启动的时候进行扫描并加载，通过`spring.factories`可以找到自动配置类的路径，  
但是不是所有存在于`spring.factories`中的配置都进行加载，而是通过 **`@ConditionalOnClass`** 注解进行判断条件是否成立（只要导入相应的`stater`，条件就能成立）， **如果条件成立则加载配置类，否则不加载该配置类** 。

## 三、Spring Boot扩展机制 - Spring Factories
**`Spring Boot`中有一种非常解耦的扩展机制：`Spring Factories`。这种扩展机制类似Java中的`SPI`扩展机制**
>Java中SPI扩展机制：（详见笔记[《java类加载过程和双亲委派模型》——打破双亲委派模型部分](https://xieruhua.github.io/javalearning/#/./Java%E7%9B%B8%E5%85%B3\Java%E5%9F%BA%E7%A1%80%E7%AD%89/Java%E7%B1%BB%E5%8A%A0%E8%BD%BD%E7%9A%84%E8%BF%87%E7%A8%8B%EF%BC%88%E7%B1%BB%E7%9A%84%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F%EF%BC%89%E5%92%8C%E5%8F%8C%E4%BA%B2%E5%A7%94%E6%B4%BE%E6%A8%A1%E5%9E%8B?id=_3-%e4%b8%ba%e4%bb%80%e4%b9%88%e8%af%b4jdbc%e7%a0%b4%e5%9d%8f%e4%ba%86%e5%8f%8c%e4%ba%b2%e5%a7%94%e6%b4%be%e6%9c%ba%e5%88%b6)）

在`META-INF/spring.factories`文件中配置接口的实现类名称，然后在程序中读取这些配置文件并实例化。  

**这种自定义的SPI机制是Spring Boot Starter实现的基础。**
### 1. 原理
`spring-core`包里定义了 **`SpringFactoriesLoader`** 类，这个类实现了检索 `META-INF/spring.factories` 文件，并获取指定接口的配置的功能。  
在这个类中定义了两个对外的方法：
* **`loadFactories`** 根据接口类获取其实现类的实例，这个方法返回的是 **对象列表** 。
* **`loadFactoryNames`** 根据接口获取其接口类的名称，这个方法返回的是 **类名的列表** 。

上面的两个方法的关键都是从指定的 `ClassLoader`（类加载器）中获取 `spring.factories` 文件，并解析得到类名列表，具体代码如下↓
```java
public final class SpringFactoriesLoader {

	/**
	 * The location to look for factories.
	 * <p>Can be present in multiple JAR files.
	 * 
	 * 寻找工厂（配置）的位置。
	 * <p>可以出现在多个 JAR 文件中。
	 */
	public static final String FACTORIES_RESOURCE_LOCATION = "META-INF/spring.factories";

	private static final Log logger = LogFactory.getLog(SpringFactoriesLoader.class);

	static final Map<ClassLoader, Map<String, List<String>>> cache = new ConcurrentReferenceHashMap<>();

	private SpringFactoriesLoader() {
	}

	public static <T> List<T> loadFactories(Class<T> factoryType, @Nullable ClassLoader classLoader) {
		Assert.notNull(factoryType, "'factoryType' must not be null");
		ClassLoader classLoaderToUse = classLoader;
		if (classLoaderToUse == null) {
			classLoaderToUse = SpringFactoriesLoader.class.getClassLoader();
		}
		List<String> factoryImplementationNames = loadFactoryNames(factoryType, classLoaderToUse);
		if (logger.isTraceEnabled()) {
			logger.trace("Loaded [" + factoryType.getName() + "] names: " + factoryImplementationNames);
		}
		List<T> result = new ArrayList<>(factoryImplementationNames.size());
		for (String factoryImplementationName : factoryImplementationNames) {
			result.add(instantiateFactory(factoryImplementationName, factoryType, classLoaderToUse));
		}
		AnnotationAwareOrderComparator.sort(result);
		return result;
	}

	public static List<String> loadFactoryNames(Class<?> factoryType, @Nullable ClassLoader classLoader) {
		ClassLoader classLoaderToUse = classLoader;
		if (classLoaderToUse == null) {
			classLoaderToUse = SpringFactoriesLoader.class.getClassLoader();
		}
		String factoryTypeName = factoryType.getName();
		return loadSpringFactories(classLoaderToUse).getOrDefault(factoryTypeName, Collections.emptyList());
	}

    /**
     * 获取所有的jar包中的META-INF/spring.factories文件
     * 
     * spring.factories文件的格式为：key=value1,value2,value3
     * 然后从文件中解析出key=factoryClass类名称的所有value值
     */
	private static Map<String, List<String>> loadSpringFactories(ClassLoader classLoader) {
		Map<String, List<String>> result = cache.get(classLoader);
		if (result != null) {
			return result;
		}

		result = new HashMap<>();
		try {
		    // 取得资源文件的URL
			Enumeration<URL> urls = classLoader.getResources(FACTORIES_RESOURCE_LOCATION);
			// 遍历所有的URL
			while (urls.hasMoreElements()) {
				URL url = urls.nextElement();
				UrlResource resource = new UrlResource(url);
				// 根据资源文件URL解析properties文件
				Properties properties = PropertiesLoaderUtils.loadProperties(resource);
				for (Map.Entry<?, ?> entry : properties.entrySet()) {
					String factoryTypeName = ((String) entry.getKey()).trim();
					String[] factoryImplementationNames =
							StringUtils.commaDelimitedListToStringArray((String) entry.getValue());
					for (String factoryImplementationName : factoryImplementationNames) {
						result.computeIfAbsent(factoryTypeName, key -> new ArrayList<>())
								.add(factoryImplementationName.trim());
					}
				}
			}
            // 组装数据，并返回
			// Replace all lists with unmodifiable lists containing unique elements
			result.replaceAll((factoryType, implementations) -> implementations.stream().distinct()
					.collect(Collectors.collectingAndThen(Collectors.toList(), Collections::unmodifiableList)));
			cache.put(classLoader, result);
		}
		catch (IOException ex) {
			throw new IllegalArgumentException("Unable to load factories from location [" +
					FACTORIES_RESOURCE_LOCATION + "]", ex);
		}
		return result;
	}
    ......................
    ......................
    ......................
}
```
### 2. 执行过程
SpringBoot启动项目的启动配置 **`@SpringBootApplication`** 开始：
1. 触发 **`@SpringBootApplication`** 中的自动装配 **`@EnableAutoConfiguration`** 
2. **`@EnableAutoConfiguration`** 执行自动配置导入选择器 **`AutoConfigurationImportSelector`**
3. **`AutoConfigurationImportSelector`** 实现接口方法 **`ImportSelector`** ——> **`String[] selectImports(AnnotationMetadata importingClassMetadata);`** 用于返回类名称集合；方法具体实现过程：
    - a. 调用本类中的方法 **`getAutoConfigurationEntry()`** 获取自动配置对象
    - b. **`getAutoConfigurationEntry()`** 继续调用本类方法 **`getCandidateConfigurations()`**
    - c. **`getCandidateConfigurations()`** 调用扩展机制 **`SpringFactoriesLoader`** 的方法 **`loadFactoryNames()`** ，至此开始获取所有的`jar包`中的`META-INF/spring.factories`文件并解析

## 四、自定义starter工具包
### 1. 定义starter
所谓的 `Starter` ，其实也就是一个普通的 **`Maven`** 项目，因此我们自定义 `Starter` ，需要首先创建一个普通的 `Maven` 项目，创建完成后，添加 `Starter` 的自动化配置的依赖即可，如下：
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-autoconfigure</artifactId>
    <version>2.1.8.RELEASE</version>
</dependency>
```
完整`pom`配置：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.1.3.RELEASE</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.xrh</groupId>
    <artifactId>hello-spring-boot-starter</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>hello-spring-boot-starter</name>

    <properties>
        <java.version>1.8</java.version>
    </properties>
    <dependencies>
        <!--该项目为starter项目，用于引用，不需要启动类-->
<!--        <dependency>-->
<!--            <groupId>org.springframework.boot</groupId>-->
<!--            <artifactId>spring-boot-starter</artifactId>-->
<!--        </dependency>-->
        <!--添加 Starter 的自动化配置的依赖-->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-autoconfigure</artifactId>
            <version>2.1.8.RELEASE</version>
        </dependency>
    </dependencies>
    <!--注释掉打包方式-->
<!--    <build>-->
<!--        <plugins>-->
<!--            <plugin>-->
<!--                <groupId>org.springframework.boot</groupId>-->
<!--                <artifactId>spring-boot-maven-plugin</artifactId>-->
<!--            </plugin>-->
<!--        </plugins>-->
<!--    </build>-->
</project>
```
**注意：注释掉`springBoot`打包插件的的目的后续补充**

先创建一个 `HelloProperties` 类，用来接收 **`application.properties`** 中注入的值，如下：
```java
@ConfigurationProperties(prefix = "javaboy")
public class HelloProperties {
    private static final String DEFAULT_NAME = "TestName";
    private static final String DEFAULT_MSG = "自定义的默认值";
    private String name = DEFAULT_NAME;
    private String msg = DEFAULT_MSG;
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
    public String getMsg() {
        return msg;
    }
    public void setMsg(String msg) {
        this.msg = msg;
    }
}
```
这个配置类的目的是将 **`application.properties`** 中配置的属性值直接注入到这个实例中；  
**`@ConfigurationProperties(prefix = "javaboy")：`** 将 `application.properties` 文件中前缀为 `javaboy` 的属性注入到这个类对应的属性上。

定义一个 `HelloService`，然后定义一个简单的 `say` 方法，用于返回读取到的配置内容， `HelloService` 的定义如下:
```java
public class HelloService {
    private String msg;
    private String name;
    public String sayHello() {
        return name + " say " + msg + " !";
    }
    public String getMsg() {
        return msg;
    }
    public void setMsg(String msg) {
        this.msg = msg;
    }
    public String getName() {
        return name;
    }
    public void setName(String name) {
        this.name = name;
    }
}
```
接下来就是重要的部分：**定义自动配置类**
```java
@Configuration
@EnableConfigurationProperties(HelloProperties.class)
@ConditionalOnClass(HelloService.class)
public class HelloServiceAutoConfiguration {
    @Autowired
    HelloProperties helloProperties;

    @Bean
    HelloService helloService() {
        HelloService helloService = new HelloService();
        helloService.setName(helloProperties.getName());
        helloService.setMsg(helloProperties.getMsg());
        return helloService;
    }
}
```
配置类解释：
* **`@Configuration` 注解：** 向`IOC`说明这是一个配置类；并将当前类里以 `@Bean` 注解标记的方法的实例注入到srping容器中。
* **`@EnableConfigurationProperties` 注解：**  使我们之前配置的`HelloProperties`配置文件读取类上的注解 `@ConfigurationProperties` 生效，让配置的属性也成功的进入 `Bean` 中。
* **`@ConditionalOnClass`：** 表示当项目当前 `classpath` 下存在 `HelloService` 时，后面的配置才生效。
* 自动配置类中首先注入 `HelloProperties` ，这个实例中含有我们在 `application.properties` 中配置的相关数据。
* **`HelloService helloService()`方法：** 提供一个 `HelloService` 的实例，将 `HelloProperties` 中的值注入进去。

再定义一个 **`spring.factories`** 文件，用来告诉springboot自动注入自定义的`starter`。  
在当前`Maven`项目的 `resources` 目录下创建一个名为 **META-INF** 的文件夹，然后在文件夹中创建一个名为 **`spring.factories`** 的文件，文件内容如下：
```
org.springframework.boot.autoconfigure.EnableAutoConfiguration=com.xrh.config.HelloServiceAutoConfiguration
```

**打包：**  
```sh
# 抛弃测试用例打包
mvn clean install -Dmaven.test.skip=true  
```
**注：mvn install和mvn package的区别**
* `mvn package`：将项目打包（`jar`/`war`），将打包结果放到项目下的 `target` 目录下
* `mvn install`在`mvn package`的基础上，打包结果放到本地仓库的相应目录中，供其他项目或模块引用

附：完整项目结构如下
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/自定义start完整项目结构.png)
</center>

**注：去掉启动类的原因**  
因为这只是一个供其他项目调用的`starter`，而不是一个独立的springboot项目， **无需单独启动，故不需要启动类** 。

### 2. 调用自定义starter
另外创建一个`maven`项目，在`pom`中加入自定义的`starter`依赖：
```xml
<!--引入自定义starter-->
<dependency>
    <groupId>com.xrh</groupId>
    <artifactId>hello-spring-boot-starter</artifactId>
    <version>0.0.1-SNAPSHOT</version>
</dependency>
```
编写单元测试：
```java
@SpringBootTest
class DemoApplicationTests {
    @Autowired
    HelloService helloService;
    @Test
    void contextLoads() {
        System.out.println(helloService.sayHello());
    }
}
```
执行结果如下：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/调用自定义start的执行结果.png)
</center>

可以看到这里打印的是自定义`starter`中默认的配置文件值。  
接下来我们在项目配置文件中加入如下内容：
```yml
javaboy.name=zhangsan
javaboy.msg=java
```
再次执行，结果如下：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/调用自定义start的执行结果2.png)
</center>
可以看到正确获取了配置文件中的内容。

### 3. 补充说明
#### 3.1 去掉springBoot打包插件
自定义starter里面去掉SpringBoot的打包插件是因为该插件打包会生成一个 **BOOT-INF**文件夹：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/不去掉springBoot打包插件的打包结果示意图.png)
</center>

导致自定义的类会找不到：
<center>

![](https://xieruhua.gitee.io/images/JavaLearning/Java相关/SpringBoot/SpringBoot自动装配及扩展机制——SpringFactoriesLoader/不去掉springBoot打包插件打的包执行异常截图.png)
</center>

**因此用默认的maven打包方式即可。**
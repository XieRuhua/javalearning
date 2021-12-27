# Java注解
# 1 理解Java注解
实际上Java注解与普通修饰符(public、static、void等)的使用方式并没有多大区别，下面的例子是常见的注解：

```java
public class AnnotationDemo {
    //@Test注解修饰方法A
    @Test
    public static void A(){
        System.out.println("Test.....");
    }

    //一个方法上可以拥有多个不同的注解
    @Deprecated
    @SuppressWarnings("uncheck")
    public static void B(){

    }
}
```

[@Test](https://github.com/Test)实际上是一种标记注解，起标记作用，运行时告诉测试框架该方法为测试方法。
而对于[@Deprecated](https://github.com/Deprecated)和[@SuppressWarnings](https://github.com/SuppressWarnings)("uncheck")，则是Java本身内置的注解，在代码中，可以经常看见它们。

# 2 Java内置标准注解

JavaSE中内置三个标准注解，定义在java.lang中：
**`@Override`**：用于修饰此方法覆盖了父类的方法;
**`@Deprecated`**：用于修饰已经过时的方法;
**`@SuppressWarnnings`**：用于通知java编译器禁止特定的编译警告。

## 2.1 `@Override`

用于标明此方法覆盖了父类的方法。

## 2.2 `@Deprecated`

用于标明已经过时的方法或类。用 [@Deprecated](https://github.com/Deprecated) 注释的程序元素，不鼓励程序员使用这样的元素，通常是因为它很危险或存在更好的选择。在使用不被赞成的程序元素或在不被赞成的代码中执行重写时，编译器会发出警告。

## 2.3 `@SuppressWarnnings`

用于有选择的关闭编译器对类、方法、成员变量、变量初始化的警告。SuppressWarnings annotation类型只定义了一个单一的成员，所以只有一个简单的value={…}作为name=value对。又由于成员值是一个数组，故使用大括号来声明数组值。

其数组的值可以为下来枚举：

- **deprecation**：使用了不赞成使用的类或方法时的警告；
- **unchecked**：执行了未检查的转换时的警告，例如当使用集合时没有用泛型 (Generics) 来指定集合保存的类型;
- **fallthrough**：当 Switch 程序块直接通往下一种情况而没有 Break 时的警告;
- **path**：在类路径、源文件路径等中有不存在的路径时的警告;
- **serial**：当在可序列化的类上缺少 serialVersionUID 定义时的警告;
- **finally**：任何 finally 子句不能正常完成时的警告;
- **all**：关于以上所有情况的警告。

**注意**：我们可以在下面的情况中缩写annotation：当annotation只有单一成员，并成员命名为”value=”。这时可以省去”value=”。如：

```java
    @SuppressWarnings({"unchecked","deprecation"})
    public void test1() {
    }
```

# 3 注解基础

## 3.1 注解分类

根据注解参数的个数，注解分为标记注解、单值注解、完整注解三类。
（1）标记注解:一个没有成员定义的Annotation类型被称为标记注解。如：`@Test`，`@Inherited`，`@Documented` 等
（2）单值注解:只有一个值
（3）完整注解:拥有多个值。

根据注解使用方法和用途:
（1）JDK内置系统注解
（2）元注解
（3）自定义注解

## 3.2 元注解

所谓元注解就是标记其他注解的注解。

Java5.0定义了4个标准的meta-annotation类型，它们被用来提供对其它 annotation类型作说明。

### 3.2.1 [@Target](https://github.com/Target)

表示该注解用于什么地方，可能的值在枚举类**ElemenetType**。

| 类型枚举                     | 说明                                                 |
| :--------------------------- | :--------------------------------------------------- |
| ElemenetType.CONSTRUCTOR     | 标明注解可以用于构造函数声明                         |
| ElemenetType.FIELD           | 标明该注解可以用于字段(域)声明，包括enum实例         |
| ElemenetType.LOCAL_VARIABLE  | 标明注解可以用于局部变量声明                         |
| ElemenetType.METHOD          | 标明该注解可以用于方法声明                           |
| ElemenetType.PACKAGE         | 标明注解可以用于包声明                               |
| ElemenetType.PARAMETER       | 标明该注解可以用于参数声明                           |
| ElemenetType.TYPE            | 标明该注解可以用于类、接口（包括注解类型）或enum声明 |
| ElemenetType.ANNOTATION_TYPE | 标明注解可以用于注解声明(应用于另一个注解上)         |
| ElemenetType.TYPE_PARAMETER  | 标明注解可以用于类型参数声明（1.8新加入）            |
| ElemenetType.TYPE_USE        | 类型使用声明（1.8新加入)                             |

#### 示例1：

```java
@Target(ElementType.TYPE)
public @interface Table {
    /**
     * 数据表名称注解，默认值为类名称
     * @return
     */
    public String tableName() default "className";
}

@Target(ElementType.FIELD)
public @interface NoDBColumn {
}
```

[@Table](https://github.com/Table) 可以用于注解类、接口(包括注解类型) 或enum声明,而[@NoDBColumn](https://github.com/NoDBColumn)仅可用于注解类的成员变量。

### 3.2.2 [@Retention](https://github.com/Retention)

用来约束注解的生命周期。可选的参数值在枚举类型**RetentionPolicy**中，分别有三个值，源码级别（source），类文件级别（class）或者运行时级别（runtime）。
|类型枚举|说明|
|–|–|
|RetentionPolicy.SOURCE|注解将被编译器丢弃（该类型的注解信息只会保留在源码里，源码经过编译后，注解信息会被丢弃，不会保留在编译好的class文件里，如`@Override`）|
|RetentionPolicy.CLASS|注解在class文件中可用，但会被VM丢弃（该类型的注解信息会保留在源码里和class文件里，在执行的时候，不会加载到虚拟机中），请注意，当注解未定义Retention值时，默认值是CLASS|
|RetentionPolicy.RUNTIME|注解信息将在运行期(JVM)也保留，因此可以通过**反射机制**读取注解的信息（源码、class文件和执行的时候都有注解的信息），如SpringMvc中的[@Controller](https://github.com/Controller)、[@Autowired](https://github.com/Autowired)、[@RequestMapping](https://github.com/RequestMapping)等。这也是我们**常用**的。|

#### 示例1：

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Column {
    public String name() default "fieldName";
    public String setFuncName() default "setField";
    public String getFuncName() default "getField";
    public boolean defaultDBValue() default false;
}
```

Column注解的的RetentionPolicy的属性值是RUTIME,这样注解处理器可以通过反射，获取到该注解的属性值，从而去做一些运行时的逻辑处理。

### 3.2.3 [@Documented](https://github.com/Documented)

用于描述其它类型的annotation应该被作为被标注的程序成员的公共API，因此可以被例如javadoc此类的工具文档化。Documented是一个**标记注解**，没有成员。

### 3.2.4 [@Inherited](https://github.com/Inherited)

`@Inherited`元注解是一个**标记注解**，[@Inherited](https://github.com/Inherited)阐述了某个被标注的类型是被继承的。如果一个使用了`@Inherited`修饰的annotation类型被用于一个class，则这个annotation将被用于该class的子类。

**注意**：[@Inherited](https://github.com/Inherited) annotation类型是被标注过的class的子类所继承。类并不从它所实现的接口继承annotation，方法并不从它所重载的方法继承annotation。
　
当[@Inherited](https://github.com/Inherited) annotation类型标注的annotation的Retention是RetentionPolicy.RUNTIME，则反射API增强了这种继承性。如果我们使用java.lang.reflect去查询一个[@Inherited](https://github.com/Inherited) annotation类型的annotation时，反射代码检查将展开工作：检查class和其父类，直到发现指定的annotation类型被发现，或者到达类继承结构的顶层。

## 3.3 注解支持的数据类型

注解支持的元素数据有：

- 所有基本类型（int,float,boolean,byte,double,char,long,short）
- String
- Class
- enum
- Annotation
- 上述类型的数组

**注意**：倘若使用了其他数据类型，编译器将会丢出一个编译错误，注意，声明注解元素时可以使用基本类型但不允许使用任何包装类型，同时还应该注意到注解也可以作为元素的类型，也就是嵌套注解（SpringBoot中多为嵌套注解）。

**示例1**：

```
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@interface Reference{
    boolean next() default false;
}

public @interface AnnotationElementDemo {
    //枚举类型
    enum Status {FIXED,NORMAL};

    //声明枚举
    Status status() default Status.FIXED;

    //布尔类型
    boolean showSupport() default false;

    //String类型
    String name()default "";

    //class类型
    Class<?> testCase() default Void.class;

    //注解嵌套
    Reference reference() default @Reference(next=true);

    //数组类型
    long[] value();
}
```

## 3.4 编译器对默认值的限制

编译器对元素的默认值有些过分挑剔。首先，元素不能有不确定的值。也就是说，元素必须要么具有默认值，要么在使用注解时提供元素的值。其次，对于非基本类型的元素，无论是在源代码中声明，还是在注解接口中定义默认值，都不能以null作为值，这就是限制，没有什么利用可言，但造成一个元素的存在或缺失状态，因为每个注解的声明中，所有的元素都存在，并且都具有相应的值，为了绕开这个限制，只能定义一些特殊的值，例如空字符串或负数，表示某个元素不存在。
如：[@Test](https://github.com/Test)

```java
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.METHOD})
public @interface Test {

    /**
     * Default empty exception
     */
    static class None extends Throwable {
        private static final long serialVersionUID = 1L;

        private None() {
        }
    }

    Class<? extends Throwable> expected() default None.class;

    long timeout() default 0L;
}
```

## 3.5 注解不支持继承

注解是不支持继承的，因此不能使用关键字extends来继承某个[@interface](https://github.com/interface)，但注解在编译后，编译器会自动继承java.lang.annotation.Annotation接口。

## 3.6 快捷方式

所谓的快捷方式就是注解中定义了名为value的元素，并且在使用该注解时，如果该元素是唯一需要赋值的一个元素，那么此时无需使用key=value的语法，而只需在括号内给出value元素所需的值即可。这可以应用于任何合法类型的元素，记住，这限制了元素名必须为value。
如：2.3节的示例中。

# 4 自定义注解

使用[@interface](https://github.com/interface)自定义注解时，自动继承了java.lang.annotation.Annotation接口，由编译程序自动完成其他细节。在定义注解时，不能继承其他的注解或接口。

## 4.1 注解示例

先看一个Java的注解类`@Deprecated`的源码：

```java
import java.lang.annotation.*;
import static java.lang.annotation.ElementType.*;

@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(value={CONSTRUCTOR, FIELD, LOCAL_VARIABLE, METHOD, PACKAGE, PARAMETER, TYPE})
public @interface Deprecated {
}
```

（1）首先，使用`@interface`声明了Deprecated注解
（2）其次，使用`@Target`注解传入`{CONSTRUCTOR, FIELD, LOCAL_VARIABLE, METHOD, PACKAGE, PARAMETER, TYPE}`参数，来标明`@Deprecated`可以用在构造器，字段，局部变量，方法，包，参数，类或接口上。
（3）再者，使用`@Retention(RetentionPolicy.RUNTIME)`则用来表示该注解生存期是运行时。
（4）最后，使用`@Documented`则用来表明，当前注解在生成**javadoc**时需要展示，否则不予显示。

从代码上看注解的定义很像接口的定义，确实如此，毕竟在编译后也会生成Deprecated.class文件。对于`@Target`和`@Retention`,`@Documented`是由Java提供的元注解。

## 4.2 定义注解格式

[@interface](https://github.com/interface)用来声明一个注解，其中的每一个方法实际上是声明了一个配置参数。方法的名称就是参数的名称，返回值类型就是参数的类型（返回值类型只能是基本类型、Class、String、enum）。可以通过default来声明参数的默认值。
`public @interface 注解名{定义体s}`

## 4.3 注解参数(即方法)

注解里面的每一个方法实际上就是声明了一个配置参数，其规则如下:
**①修饰符**
只能用public或默认(default)这两个访问权修饰 ，默认为default

**②类型**
注解参数只支持以下数据类型：

- 基本数据类型（int,float,boolean,byte,double,char,long,short)；
- String类型；
- Class类型；
- enum类型；
- Annotation类型;
- 以上所有类型的数组

**③命名**
对取名没有要求，如果只有一个参数成员,最好把参数名称设为”value”,后加小括号。

**④参数**
注解中的方法不能存在参数

**⑤默认值**
可以包含默认值，使用default来声明默认值。

## 4.4 示例

以下举两个例子：
LogTreadAnnotation 使用Log4j2时，控制多线程中线程日志数据的注解。

```java
/**
 * @Description log4j多线程日志输出注解
 *    使用该注解的方法，其运行日志除了在正常的log文件中输出外。
 *    还会在 thread目录下 job:uuid-YYYYMMDD.log 文件中输出。
 */
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface LogTreadAnnotation {
}
```

DataSource 多数据源切换注解

```java
/**
 * @Description 用于aop类中当作切入点来选择数据源
 */
@Target({ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface DataSource {
    DataSourceEnum value() default DataSourceEnum.MYSQL;
}
```

# 5 注解处理器

如果没有用来读取注解的方法和工作，那么注解也就不会比注释更有用处了。使用注解的过程中，很重要的一部分就是创建于使用注解处理器。

## 5.1 反射机制

Retention.RUNTIME时，Java使用Annotation接口来代表程序元素前面的注解，该接口是所有Annotation类型的父接口。除此之外，Java在java.lang.reflect 包下新增了AnnotatedElement接口，该接口代表程序中可以接受注解的程序元素，该接口主要有如下几个实现类：

- Class：类定义
- Constructor：构造器定义
- Field：类的成员变量定义
- Method：类的方法定义
- Package：类的包定义

![AnnotatedElement](https://upload-images.jianshu.io/upload_images/9180253-412af906f8412581.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

java.lang.reflect 包下主要包含一些实现反射功能的工具类，实际上，java.lang.reflect 包所有提供的反射API扩充了读取运行时Annotation信息的能力。当一个Annotation类型被定义为运行时的Annotation后，该注解才能是运行时可见，当class文件被装载时被保存在class文件中的Annotation才会被虚拟机读取。

AnnotatedElement 接口是所有程序元素（Class、Method和Constructor）的父接口，所以程序通过反射获取了某个类的AnnotatedElement对象之后，程序就可以调用该对象的如下四个个方法来访问Annotation信息（以上5个类都实现以下的方法）：

| 返回值       | 方法名称                                                     | 说明                                                         |
| :----------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
|              | getAnnotation(Class annotationClass)                         | 该元素如果存在指定类型的注解，则返回这些注解，否则返回 null。 |
| Annotation[] | getAnnotations()                                             | 返回此元素上存在的所有注解，包括从父类继承的                 |
| boolean      | isAnnotationPresent(Class<? extends Annotation> annotationClass) | 如果指定类型的注解存在于此元素上，则返回 true，否则返回 false。 |
| Annotation[] | getDeclaredAnnotations()                                     | 返回直接存在于此元素上的所有注解，注意，不包括父类的注解，调用者可以随意修改返回的数组；这不会对其他调用者返回的数组产生任何影响，没有则返回长度为0的数组 |
| Annotation[] | getAnnotationsByType(Class annotationClass)                  | JDK1.8新增                                                   |
| Annotation[] | getDeclaredAnnotationsByType(Class annotationClass)          | JDK1.8新增                                                   |

### 示例：

```java
/***********注解声明***************/
/**
 * 水果名称注解
 */
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface FruitName {
    String value() default "";
}
/**
 * 水果颜色注解
 */
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface FruitColor {
    /**
     * 颜色枚举
     */
    public enum Color{ BULE,RED,GREEN};
    /**
     * 颜色属性
     * @return
     */
    Color fruitColor() default Color.GREEN;
}

/**
 * 水果供应者注解
 */
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface FruitProvider {
    /**
     * 供应商编号
     * @return
     */
    public int id() default -1;
    /**
     * 供应商名称
     * @return
     */
    public String name() default "";
    /**
     * 供应商地址
     * @return
     */
    public String address() default "";
}
/***********注解使用***************/
public class Apple {
    @FruitName("Apple")
    private String appleName;
    @FruitColor(fruitColor=Color.RED)
    private String appleColor;
    @FruitProvider(id=1,name="陕西红富士集团",address="陕西省西安市延安路89号红富士大厦")
    private String appleProvider;
}
/***********注解处理器***************/
public class FruitInfoUtil {
    public static void getFruitInfo(Class</> clazz){

        String strFruitName=" 水果名称：";
        String strFruitColor=" 水果颜色：";
        String strFruitProvicer="供应商信息：";

        Field[] fields = clazz.getDeclaredFields();

        for(Field field :fields){
            if(field.isAnnotationPresent(FruitName.class)){
                FruitName fruitName = (FruitName) field.getAnnotation(FruitName.class);
                strFruitName=strFruitName+fruitName.value();
                System.out.println(strFruitName);
            }
            else if(field.isAnnotationPresent(FruitColor.class)){
                FruitColor fruitColor= (FruitColor) field.getAnnotation(FruitColor.class);
                strFruitColor=strFruitColor+fruitColor.fruitColor().toString();
                System.out.println(strFruitColor);
            }
            else if(field.isAnnotationPresent(FruitProvider.class)){
                FruitProvider fruitProvider= (FruitProvider) field.getAnnotation(FruitProvider.class);
                strFruitProvicer=" 供应商编号："+fruitProvider.id()+" 供应商名称："+fruitProvider.name()+" 供应商地址："+fruitProvider.address();
                System.out.println(strFruitProvicer);
            }
        }
    }
}
/***********输出结果***************/
public class FruitRun {
    /**
     * @param args
     */
    public static void main(String[] args) {
        FruitInfoUtil.getFruitInfo(Apple.class);
    }
}
```

## 5.2 SpringAOP

除了通过反射工具自定义注解解释器外，在日常开发中用的最多的就是注解与Spring AOP结合完成特定的工作。

### 示例

下面以4.4节中的日志注解为例介绍。
LogTreadAnnotation主要的通途就是，当标注`@LogTreadAnnotation`方法执行时，会根据方法参数判断，如果参数不一致，则整个方法及后续方法的日志都输出在一个log文件中，即每次标注`@LogTreadAnnotation`方法的日志都会在不同的日志文件中。

```java
/**
 * @Description log4j多线程日志输出注解
 *    使用该注解的方法，其运行日志除了在正常的log文件中输出外。
 *    还会在 thread目录下 job:uuid-YYYYMMDD.log 文件中输出。
 */
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface LogTreadAnnotation {
}

/**
 * @Description log4j多线程日志控制切面
 */
@Component      //声明组件
@Aspect         //声明切面
@ComponentScan  //组件自动扫描
@EnableAspectJAutoProxy //spring自动切换JDK动态代理和CGLIB
public class LogTreadRecordAspect {

    @Pointcut("@annotation(com.zznode.gum.task.core.aop.LogTreadAnnotation)")
    public void addLogTread(){}

    @Before("addLogTread()")
    public void beforeAdvide(){
        //TODO 操作日志@Before 方法执行前
    }

    @After("addLogTread()")
    public void afterAdvide() {
        //TODO 操作日志@After 方法执行后
    }

    @Around("addLogTread()")
    public void aroundAvide(ProceedingJoinPoint pjp) throws Throwable {
        //操作日志@Around 方法执行前
        Object[] args = pjp.getArgs();
        if(args != null && args.length >1) {
           String jobId = args[0].toString();
           String uuid = args[1].toString();
           LogUtils.logThreadBegin(jobId+":"+uuid);
        }
        //方法执行
        pjp.proceed();

        //操作日志@Around 方法执行后
        LogUtils.logTreadEnd();
    }
}

/**
 * @Description Log4j2多线程输出日志工具类
 */
public class LogUtils {

    /**
     * 开始日志输出到指定线程
     * @param key
     */
    public static void logThreadBegin(String key) {
        ThreadContext.put("JobUUID",key);
    }

    /**
     * 结束日志输出
     */
    public static void logTreadEnd() {
        ThreadContext.remove("JobUUID");
    }
}
```

使用

```java
/**
 * @Description 数据汇聚计算Controller
 */
@Slf4j
@RestController
@RequestMapping("/dataConverge")
@Api(value = "数据计算任务RESTFUL")
public class DataConvergeController {

    @Autowired
    private DataConvergeService dataConvergeService;

    @ApiOperation(value = "报表指标天汇聚计算任务", notes = "报表指标天汇聚计算任务")
    @GetMapping("/rptIndexDayConverge")
    @ApiImplicitParams({
            @ApiImplicitParam(name = "jobId", value = "任务编号", required = true, dataType = "String", paramType = "query"),
            @ApiImplicitParam(name = "uuid", value = "任务实例编号", required = true, dataType = "String", paramType = "query")
    })
    @ResponseBody
    @LogTreadAnnotation
    protected Result<String> rptIndexDayConverge(@RequestParam(name="jobId") String  jobId,
                                                 @RequestParam(name="uuid") String  uuid) {
        dataConvergeServiceAh.rptIndexDayConverge(jobId,uuid);
        //返回处理中
        return new Result<>(EnumResult.EXECUTING.getIndex(), EnumResult.EXECUTING.getName());
    }
```

另附 log4j2.xml配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration status="WARN" monitorInterval="60">
    <Properties>
        <Property name="PATTERN">%d{DEFAULT} [%t] %-5p %c{1.}.%M %L - %msg%xEx%n</Property>
    </Properties>
    <appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <ThresholdFilter level="info" onMatch="ACCEPT" onMismatch="DENY" />
            <PatternLayout pattern="${PATTERN}" />
        </Console>

        <RollingFile name="TRACE" fileName="${sys:app.log.home}/task-all.log" filePattern="${sys:app.log.home}/$${date:yyyy-MM}/task-all-%d{MM-dd-yyyy}-%i.log.gz">
            <ThresholdFilter level="trace" onMatch="ACCEPT" onMismatch="DENY" />
            <PatternLayout pattern="${PATTERN}" />
            <SizeBasedTriggeringPolicy size="20MB" />
        </RollingFile>

        <RollingFile name="DEBUG" fileName="${sys:app.log.home}/task-debug.log" filePattern="${sys:app.log.home}/$${date:yyyy-MM}/task-debug-%d{MM-dd-yyyy}-%i.log.gz">
            <ThresholdFilter level="debug" onMatch="ACCEPT" onMismatch="DENY" />
            <PatternLayout pattern="${PATTERN}" />
            <SizeBasedTriggeringPolicy size="20MB" />
        </RollingFile>

        <RollingFile name="INFO" fileName="${sys:app.log.home}/task-info.log" filePattern="${sys:app.log.home}/$${date:yyyy-MM}/task-info-%d{MM-dd-yyyy}-%i.log.gz">
            <ThresholdFilter level="info" onMatch="ACCEPT" onMismatch="DENY" />
            <PatternLayout pattern="${PATTERN}" />
            <SizeBasedTriggeringPolicy size="20MB" />
        </RollingFile>

        <RollingFile name="ERROR" fileName="${sys:app.log.home}/task-error.log" filePattern="${sys:app.log.home}/$${date:yyyy-MM}/task-error-%d{MM-dd-yyyy}-%i.log.gz">
            <ThresholdFilter level="error" onMatch="ACCEPT" onMismatch="DENY" />
            <PatternLayout pattern="${PATTERN}" />
            <SizeBasedTriggeringPolicy size="20MB" />
        </RollingFile>

        <Routing name="thread">
            <Routes pattern="$${ctx:JobUUID}">
                <Route>
                    <File name="File-${ctx:JobUUID}" fileName="${sys:app.log.home}/threads/${ctx:JobUUID}.log">
                        <ThresholdFilter level="debug" onMatch="ACCEPT" onMismatch="DENY" />
                        <PatternLayout pattern="${PATTERN}" />
                    </File>
                </Route>
            </Routes>
        </Routing>
    </appenders>

    <!--然后定义logger，只有定义了logger并引入的appender，appender才会生效 -->
    <loggers>
        <!--过滤掉spring和mybatis的一些无用的DEBUG信息 -->
        <logger name="org.springframework" level="INFO" />
        <logger name="org.mybatis" level="debug" />
        <logger name="springfox.documentation" level="ERROR" />
        <logger name="io.netty" level="INFO" />
        <logger name="org.apache" level="info" />
        <logger name="reactor.util" level="info" />
        <logger name="org.flowable" level="info" />
        <logger name="com.test" level="debug" />
        <logger name="io.lettuce" level="info" />
        <logger name="org.quartz" level="info" />
        <logger name="org.hibernate.validator" level="info" />

        <root level="trace">
            <appender-ref ref="Console" />
            <appender-ref ref="TRACE" />
            <appender-ref ref="DEBUG" />
            <appender-ref ref="INFO" />
            <appender-ref ref="ERROR" />
            <appender-ref ref="thread" />
        </root>
    </loggers>
</configuration>
```

## 5.3 Spring IOC

除了配置AOP之外，其次就是结合IOC，直接从IOC容器中拿取标注了指定注解的Bean。

### 5.3.1 注解

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface ColumnCommandOrder {
    /**
     * 默认值处理顺序
     * @return 序号
     */
    int valueOrder() default 99;

    /**
     * 检查处理顺序
     * @return 序号
     */
    int checkOrder() default 99;

    /**
     * 指定报文类型。
     * 只有指定的报文类型，才使用该Command
     * @return 报文类型数组
     */
    String[] telexType() default {AnalyseConstants.TELEX_TYPE_NOTAMNCR};
}
```

### 5.3.2 注解解析

通过IOC获取标注了该注解的类实例。
（1）ApplicationContext的工具类

```java
@Component
public class AnalyseServiceContext implements ApplicationContextAware {

    private static ApplicationContext applicationContext=null;

    @Override
    public void setApplicationContext(ApplicationContext applicationContext) throws BeansException {
        AnalyseServiceContext.applicationContext = applicationContext;
    }

    public static <T> T getBean(String beanName) {
        return (T)applicationContext.getBean(beanName);
    }

    public static <T> T getBean(Class<T> clazz) {
        return applicationContext.getBean(clazz);
    }

    public static Map<String,Object> getBeanMap(Class<? extends Annotation> tClass) {
          return applicationContext.getBeansWithAnnotation(tClass);
    }

    public static <T> Map<String,T> getBeansOfType(Class<T> clazz) {
        return applicationContext.getBeansOfType(clazz);
    }
}
```

注解解析

```java
public class TelexBusinessCheckParserHandler implements ITelexParserHandler{
    @Override
    public void parserTelex(ITelexBusinessHandler businessHandler) {
        if (businessHandler.isErrorOut()) {
            return;
        }
        TreeMap<Integer, ITelexColumnParserCommand> commandTreeMap= Maps.newTreeMap();
        Map<String,Object> maps = AnalyseServiceContext.getBeanMap(ColumnCommandOrder.class);
        for (Map.Entry<String, Object> bean: maps.entrySet()) {
            Object obj = bean.getValue();
            ColumnCommandOrder annotation = obj.getClass().getAnnotation(ColumnCommandOrder.class);
            if (null!=annotation) {
                int order = annotation.checkOrder();
                commandTreeMap.put(order, (ITelexColumnParserCommand) obj);
            }
        }

        commandTreeMap.forEach((k,v)->{
            v.setBusinessHandler(businessHandler);
            if (log.isDebugEnabled()) {
                log.debug("业务规则判断{},处理类{}",k,v.getClass().getSimpleName());
            }
            try {
                ColumnCommandOrder annotation = v.getClass().getAnnotation(ColumnCommandOrder.class);
                if (ArrayUtils.contains(annotation.telexType(),
                        businessHandler.getOutputType().getApplicationCode())) {
                    v.columnCheckHandler();
                }
            } catch (Exception e) {
                log.error("业务规则判断{},处理类{},异常{}",k,v.getClass().getSimpleName(),e);
            }
        });
    }
}
```

### 5.3.3 注解标注

```java
@Slf4j
@Component
@ColumnCommandOrder(valueOrder = 12,checkOrder = 12)
public class ItemBParserCommand extends AbstractColunmParserCommand {
...
}
```

# 6 Java 8中注解增强

对于元注解，Java 8 主要有两点改进：类型注解和重复注解。

## 6.1 重复注解

元注解[@Repeatable](https://github.com/Repeatable)是JDK1.8新加入的，它表示在同一个位置重复相同的注解。在没有该注解前，一般是无法在同一个类型上使用相同的注解的。

```java
//Java8前无法这样使用
@FilterPath("/web/update")
@FilterPath("/web/add")
public class A {}
```

Java8前如果是想实现类似的功能，我们需要在定义[@FilterPath](https://github.com/FilterPath)注解时定义一个数组元素接收多个值如下:

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface FilterPath {
    String [] value();
}

//使用
@FilterPath({"/update","/add"})
public class A { }
```

但在Java8新增了[@Repeatable](https://github.com/Repeatable)注解后就可以采用如下的方式定义并使用了

```java
//使用Java8新增@Repeatable原注解
@Target({ElementType.TYPE,ElementType.FIELD,ElementType.METHOD})
@Retention(RetentionPolicy.RUNTIME)
@Repeatable(FilterPaths.class)//参数指明接收的注解class
public @interface FilterPath {
    String  value();
}

// 自定义一个包装类FilterPaths注解用来放置一组具体的FilterPath注解
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@interface FilterPaths {
    FilterPath[] value();
}

// 使用案例新方法
@FilterPath("/web/update")
@FilterPath("/web/add")
class AA{ }

// 使用案例旧方法
@FilterPaths ({@FilterPath("/web/update"), @FilterPath("/web/add")}) 
class AA{ }
```

见5.1节，为了处理上述的新增注解，Java8还在AnnotatedElement接口新增了`getDeclaredAnnotationsByType()`和 `getAnnotationsByType()`两个方法并在接口给出了默认实现，在指定`@Repeatable`的注解时，可以通过这两个方法获取到注解相关信息。

**注意：**

- 旧版API中的`getDeclaredAnnotation()`和 `getAnnotation()`是不对`@Repeatable`注解的处理的(除非该注解没有在同一个声明上重复出现)。
- `getDeclaredAnnotationsByType`方法获取到的注解不包括父类，其实当 `getAnnotationsByType()`方法调用时，其内部先执行了`getDeclaredAnnotationsByType`方法，只有当前类不存在指定注解时，`getAnnotationsByType()`才会继续从其父类寻找，但请注意如果`@FilterPath`和`@FilterPaths`没有使用了`@Inherited`的话，仍然无法获取。

## 6.2 类型注解

### 6.2.1 注解使用的范围。

在java 8之前，注解只能是在声明的地方所使用，java8开始，注解可以应用在任何地方。

- TYPE_USE则可以用于标注任意类型(不包括class)
  \```java
  // 用于构造函数，创建类实例
  new[@Interned](https://github.com/Interned) MyObject();

// 用于强制类型转换和instanceof检查,注意这些注解中用于外部工具，它们不会对类型转换或者instanceof的检查行为带来任何影响。
myString = ([@NonNull](https://github.com/NonNull) String) str;
if(input instanceof [@NonNull](https://github.com/NonNull) String)

// 用于父类或者接口
class Image implements [@Rectangular](https://github.com/Rectangular) Shape { }

// 用于指定异常
void monitorTemperature() throws [@Critical](https://github.com/Critical) TemperatureException { … }

```
* TYPE_PARAMETER 标注在类型参数上
```java
// 标注在类型参数上
class D<@Parameter T> { }
```

**注意：**

- 在Java 8里面，当类型转化甚至分配新对象的时候，都可以在声明变量或者参数的时候使用注解。
- Java注解可以支持任意类型。
- 类型注解只是语法而不是语义，并不会影响java的编译时间，加载时间，以及运行时间，也就是说，编译成class文件的时候并不包含类型注解。

由上面的注解使用范围的变更，引出ElementType新增的两个类型。

### 6.2.2 新增的两种ElementType

新增的两个注释的程序元素类型 `ElementType.TYPE_USE` 和 `ElementType.TYPE_PARAMETER`用来描述注解的新场合 。

- ElementType.TYPE_PARAMETER 表示该注解能写在类型变量的声明语句中。
- ElementType.TYPE_USE 表示该注解能写在使用类型的任何语句中（eg：声明语句、泛型和强制转换语句中的类型）。

```java
@Target({ElementType.TYPE_PARAMETER, ElementType.TYPE_USE})
@interface MyAnnotation {}
```

### 6.2.3 类型注解的作用

类型注解被用来支持在Java的程序中做强类型检查。配合第三方插件工具`Checker Framework`，可以在编译的时候检测出runtime error（eg：UnsupportedOperationException； NumberFormatException；NullPointerException异常等都是runtime error），以提高代码质量。这就是类型注解的作用。

**注意：**
使用Checker Framework可以找到类型注解出现的地方并检查。
#  java8 流式处理集合，数组等

## 1.什么是Stream流？
Stream流是数据渠道，用于操作数据源（集合、数组等）所生成的元素序列。

它完全不同于 java.io 包的 **Input/Output Stream**，也不是大数据实时处理的 **Stream 流**。  
这个 Stream 流操作是 Java 8 对集合操作功能的增强，专注于对集合的各种高效、便利、优雅的聚合操作。借助于 Lambda 表达式，显著的提高编程效率和可读性。且 Stream 提供了并行计算模式，可以简洁的编写出并行代码，能充分发挥如今计算机的多核处理优势。

**lambda表达式：expression = (variable) -> action**  
**variable：** 这是一个变量,一个占位符。像x、y、z可以是多个变量。  
**action：** 这里我称它为action, 这是我们实现的代码逻辑部分，它可以是一行代码也可以是一个代码片段


## 2.Stream 流优点
### 2.1. 简洁优雅
正确使用并且正确格式化的 Stream 流操作代码不仅简洁优雅，更让人赏心悦目。

### 2.2.惰性计算
在调用方法时并不会立即调用，而是在真正使用的时候才会生效，这样可以让操作延迟到真正需要使用的时刻。
```java
// 生成自己的随机数流
List<Integer> numberLIst = Arrays.asList(1, 2, 3, 4, 5, 6);
// 找出偶数
Stream<Integer> integerStream = numberLIst.stream()
        .filter(number -> {
            int temp = number % 2;
            if (temp == 0 ){
                System.out.println(number);
            }
            return temp == 0;
        });

System.out.println("分割线");
List<Integer> collect = integerStream.collect(Collectors.toList());
//如果没有 惰性计算，那么很明显会先输出偶数，然后输出 分割线。而实际的效果是。
```
### 2.3.特定性能优势
1.针对简单的操作，比如基础类型的遍历，使用for循环性能要明显高于串行Stream操作。但Stream的并行操作随着服务器的核数增加，会优于for循环。
2.针对复杂操作，串行Stream性能与for循环不差上下，但并行Stream的性能已经是无法匹敌了。
3.特别是针对一个集合进行多层过滤并归约操作，无论从写法上或性能上都要明显优于for循环。
参考性能测试：https://zhuanlan.zhihu.com/p/158794416
https://www.cnblogs.com/secbro/p/11653574.html

## 3.stream抽象流程步骤
数据源（source） -> 数据处理/转换（intermedia） -> 结果处理（terminal ）
### 3.1. 数据源
数据源（source）也就是数据的来源，可以通过多种方式获得 Stream 数据源，下面列举几种常见的获取方式。

**Collection.stream()：** 从集合获取流；  
**Collection.parallelStream()：** 从集合获取并行流；  
**Arrays.stream(T array)：** 通过Arrays中的静态方法获取数据流；  
**Stream.of()：** 从数组获取流；  
**BufferedReader.lines()：** 从输入流中获取流；  
**IntStream.of()：** 从静态方法中获取流；  
**Stream.generate()：** 自己生成流。

```java
// 1、通过Collection系列提供的stream()（串行） 或parallelStream()（并行）获取
List<String> list = new ArrayList<>();
Stream<String> stream1 = list.stream();//串行流
Stream<String> stream2 = list.parallelStream();//并行流

// 2、通过Arrays中的静态方法stream() 获取数据流
User[] u = new User[2];
Stream<User> stream3 = Arrays.stream(u);

// 3、通过Stream；类中的静态方法of()
Stream<String> stream4 = Stream.of("11","2");
```
### 3.2. 数据处理
**数据处理/转换（intermedia）** 步骤可以有多个操作，这步也被称为**intermedia（中间操作）**。在这个步骤中不管怎样操作，它返回的都是一个新的流对象，原始数据不会发生任何改变，而且这个步骤是惰性计算处理的，也就是说只调用方法并不会开始处理，只有在真正的开始收集结果时，中间操作才会生效，而且如果遍历没有完成，想要的结果已经获取到了（比如获取第一个值），会停止遍历，然后返回结果。

**惰性计算可以显著提高运行效率。**

**中间操作大体又分为筛选和切片等其他具体操作**  
* **filter(predicate)：** 接收lambda，从流中排除某些元素。  
* **limit(n)：** 截断流，使其元素不超过给定数量。  
* **skip(n)：** 跳过元素，返回一个扔掉了前n个元素的流。若流中元素不足n个，则返回一个空流，与limit(n)互补。  
* **distinct：** 筛选，通过流所生成元素的hashcode()和equals()去重复元素。

数据处理演示。
```java
@Test
public void streamDemo(){
    List<String> nameList = Arrays.asList("Darcy", "Chris", "Linda", "Sid", "Kim", "Jack", "Poul", "Peter");
    // 1. 筛选出名字长度为4的
    // 2. 名字前面拼接 This is
    // 3. 遍历输出
    nameList.stream()
            .filter(name -> name.length() == 4)
            .map(name -> "This is "+name)
            .forEach(name -> System.out.println(name));
}

// 输出结果
// This is Jack
// This is Poul
```
数据处理/转换操作自然不止是上面演示的过滤 filter 和 map映射两种，**另外还有 map (mapToInt, flatMap 等)、 filter、 distinct、 sorted、 peek、 limit、 skip、 parallel、 sequential、 unordered 等。**

### 3.3. 收集结果
**结果处理（terminal ）** 是流处理的最后一步，执行完这一步之后流会被彻底用尽，流也不能继续操作了。  
也只有到了这个操作的时候，流的数据处理/转换等中间过程才会开始计算，也就是上面所说的惰性计算。结果处理也必定是流操作的最后一步。

常见的结果处理操作有 **forEach、 forEachOrdered、 toArray、 reduce、 collect、 min、 max、 count、 anyMatch、 allMatch、 noneMatch、 findFirst、 findAny、 iterator 等**。

下面演示了简单的结果处理的例子。
```java
/**
 * 转换成为大写然后收集结果，遍历输出
 */
@Test
public void toUpperCaseDemo() {
    List<String> nameList = Arrays.asList("Darcy", "Chris", "Linda", "Sid", "Kim", "Jack", "Poul", "Peter");
    List<String> upperCaseNameList = nameList.stream()
            .map(String::toUpperCase)
            .collect(Collectors.toList());
    upperCaseNameList.forEach(name -> System.out.println(name + ","));
}

// 输出结果
// DARCY,CHRIS,LINDA,SID,KIM,JACK,POUL,PETER,
```

### 3.4. short-circuiting
有一种 Stream 操作被称作 **short-circuiting** ，它是指当 Stream 流无限大但是需要返回的 Stream 流是有限的时候，而又希望它能在有限的时间内计算出结果，那么这个操作就被称为short-circuiting。例如 **findFirst** 操作。

## 4. Stream 流常见使用
### 4.1. forEach
forEach 是 Stream 流中的一个重要方法，用于遍历 Stream 流，它支持传入一个标准的 Lambda 表达式。  
但是它的遍历不能通过 return/break 进行终止。同时它也是一个 **terminal** 操作，执行之后 Stream 流中的数据会被消费掉。

如输出对象：
```java
List<Integer> numberList = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
numberList.stream().forEach(number -> System.out.println(number+","));
// 输出结果
// 1,2,3,4,5,6,7,8,9,
```

### 4.2. map / flatMap

使用 map 把对象一对一映射成另一种对象或者形式

```java
/**
 * 把数字值乘以2
 */
@Test
public void mapTest() {
    List<Integer> numberList = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
    // 映射成 2倍数字
    List<Integer> collect = numberList.stream()
            .map(number -> number * 2)
            .collect(Collectors.toList());
    collect.forEach(number -> System.out.print(number + ","));
    System.out.println();

    numberList.stream()
            .map(number -> "数字 " + number + ",")
            .forEach(number -> System.out.println(number));
}
// 输出结果
// 2,4,6,8,10,12,14,16,18,
// 数字 1,数字 2,数字 3,数字 4,数字 5,数字 6,数字 7,数字 8,数字 9,
```

上面的 map 可以把数据进行一对一的映射，而有些时候关系可能不止 1对 1那么简单，可能会有1对多。这时可以使用 **flatMap**。

下面演示使用 flatMap把对象扁平化展开。
```java
/**
 * flatmap把对象扁平化
 */
@Test
public void flatMapTest() {
    Stream<List<Integer>> inputStream = Stream.of(
            Arrays.asList(1),
            Arrays.asList(2, 3),
            Arrays.asList(4, 5, 6)
    );
    List<Integer> collect = inputStream
            .flatMap((childList) -> childList.stream())
            .collect(Collectors.toList());
    collect.forEach(number -> System.out.print(number + ","));
}
// 输出结果
// 1,2,3,4,5,6,
```

### 4.3. filter
使用 filter 进行数据筛选，挑选出想要的元素，下面的例子演示怎么挑选出偶数数字。
```java
/**
 * filter 数据筛选
 * 筛选出偶数数字
 */
@Test
public void filterTest() {
    List<Integer> numberList = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
    List<Integer> collect = numberList.stream()
            .filter(number -> number % 2 == 0)
            .collect(Collectors.toList());
    collect.forEach(number -> System.out.print(number + ","));
}
```

### 4.4. findFirst
findFirst 可以查找出 Stream 流中的第一个元素，它返回的是一个 Optional 类型；
```java
/**
 * 查找第一个数据
 * 返回的是一个 Optional 对象
 */
@Test
public void findFirstTest(){
    List<Integer> numberList = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9);
    Optional<Integer> firstNumber = numberList.stream()
            .findFirst();
    System.out.println(firstNumber.orElse(-1));
}
// 输出结果
// 1
```

### 4.5. collect / toArray
Stream 流可以轻松的转换为其他结构，下面是几种常见的示例。
```java
/**
 * Stream 转换为其他数据结构
 */
@Test
public void collectTest() {
    List<Integer> numberList = Arrays.asList(1, 1, 2, 2, 3, 3, 4, 4, 5);
    // to array
    Integer[] toArray = numberList.stream()
            .toArray(Integer[]::new);
    // to List
    List<Integer> integerList = numberList.stream()
            .collect(Collectors.toList());
    // to set
    Set<Integer> integerSet = numberList.stream()
            .collect(Collectors.toSet());
    System.out.println(integerSet);
    // to string
    String toString = numberList.stream()
            .map(number -> String.valueOf(number))
            .collect(Collectors.joining()).toString();
    System.out.println(toString);
    // to string split by ,
    String toStringbJoin = numberList.stream()
            .map(number -> String.valueOf(number))
            .collect(Collectors.joining(",")).toString();
    System.out.println(toStringbJoin);
}
// 输出结果
// [1, 2, 3, 4, 5]
// 112233445
// 1,1,2,2,3,3,4,4,5
```

### 4.6. limit / skip
获取或者扔掉前 n 个元素
```java
/**
 * 获取 / 扔掉前 n 个元素
 */
@Test
public void limitOrSkipTest() {
    // 生成自己的随机数流
    List<Integer> ageList = Arrays.asList(11, 22, 13, 14, 25, 26);
    ageList.stream()
            .limit(3)
            .forEach(age -> System.out.print(age+","));
    System.out.println();

    ageList.stream()
            .skip(3)
            .forEach(age -> System.out.print(age+","));
}
// 输出结果
// 11,22,13,
// 14,25,26,
```

### 4.7. Statistics（数学统计）
数学统计功能，求一组数组的最大值、最小值、个数、数据和、平均数等。
```java
/**
 * 数学计算测试
 */
@Test
public void mathTest() {
    List<Integer> list = Arrays.asList(1, 2, 3, 4, 5, 6);
    IntSummaryStatistics stats = list.stream().mapToInt(x -> x).summaryStatistics();
    System.out.println("最小值：" + stats.getMin());
    System.out.println("最大值：" + stats.getMax());
    System.out.println("个数：" + stats.getCount());
    System.out.println("和：" + stats.getSum());
    System.out.println("平均数：" + stats.getAverage());
}
// 输出结果
// 最小值：1
// 最大值：6
// 个数：6
// 和：21
// 平均数：3.5
```

### 4.8. groupingBy（按某个条件分组）
```java
/**
 * groupingBy
 * 按年龄分组
 */
@Test
public void groupByTest() {
    List<Integer> ageList = Arrays.asList(11, 22, 13, 14, 25, 26);
    Map<String, List<Integer>> ageGrouyByMap = ageList.stream()            
        .collect(Collectors.groupingBy(age -> String.valueOf(age / 10)));
    ageGrouyByMap.forEach((k, v) -> {
        System.out.println("年龄" + k + "0多岁的有：" + v);
    });
}
// 输出结果
// 年龄10多岁的有：[11, 13, 14]
// 年龄20多岁的有：[22, 25, 26]
```

### 4.9. partitioningBy（按某个条件分组）
```java
/**
 * partitioningBy
 * 按某个条件分组
 * 给一组年龄，分出成年人和未成年人
 */
public void partitioningByTest() {
    List<Integer> ageList = Arrays.asList(11, 22, 13, 14, 25, 26);
    Map<Boolean, List<Integer>> ageMap = ageList.stream()
            .collect(Collectors.partitioningBy(age -> age > 18));
    System.out.println("未成年人：" + ageMap.get(false));
    System.out.println("成年人：" + ageMap.get(true));
}
// 输出结果
// 未成年人：[11, 13, 14]
// 成年人：[22, 25, 26]
```
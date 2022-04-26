# MayBatis的一二级缓存

[笔记内容参考1：mybatis一级缓存二级缓存](https://www.cnblogs.com/happyflyingpig/p/7739749.html)   
[笔记内容参考2：MyBatis一级缓存介绍](http://www.mybatis.cn/archives/744.html)     
[笔记内容参考3：MyBatis二级缓存介绍](http://www.mybatis.cn/archives/746.html)     
[笔记内容参考4：Mybatis一二级缓存](https://blog.csdn.net/qq_49313444/article/details/107287374)    
[笔记内容参考5：Mybatis - 二级缓存的利弊](https://blog.huati365.com/b43bad4ea76d6491)    

[toc]

## 一、什么是缓存
**什么是缓存：**
所谓的缓存，就是将程序或系统经常要调用的对象存在内存中，以便其使用时可以快速调用，而不必再去创建新的重复的实例。如redis就是将数据保存在内存中，以便于高速访问。

**为什么使用缓存：**
使用缓存可以减少和数据库的交互次数，提高执行效率，并且可以保护数据库不被高并发的影响。

**适用于缓存的数据：**
- 经常查询并且不经常被改变的数据
- 时效性要求不高的数据
- 数据的正确与否对最终结果影响不大的数据

**不适用于缓存的数据：**
- 经常改变的数据
- 对时效性有一定要求的数据
- 数据的正确与否对最终结果影响很大的数据

## 二、Mybatis的一级缓存
### 1. 简述
**Mybatis的一级缓存是默认开启的，** 但是MyBatis在没有配置的默认情况下只启用了本地的会话 **（`SqlSession`作用域）** 缓存， **它仅仅对一个会话中的数据进行缓存，这也就是大家常说的MyBatis一级缓存。**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/MyBatis/MayBatis的一二级缓存/mybatis一级缓存示意图.png)
</center>

MyBatis一级缓存的运行过程： 
- 当执行`SQL`语句查询之后，查询的结果会同时存入到 `SqlSession`为我们提供的一块区域（该区域的结构是一个`Map`）中。
- 当再次查询同样的数据，Mybatis会先去`SqlSession`中查询是否存在，存在的话直接返回（如果没有声明需要刷新，并且缓存没有超时的情况下），`SqlSession`都会取出当前缓存的数据，而不会再次发送`SQL`到数据库查询。

这里要注意一个点，因为一级缓存是依赖于`SqlSession对象`的，当 **`SqlSession对象消失时，Mybaits的一级缓存也就消失了`** 。

补充：MyBatis提供了默认下基于`Java HashMap`的缓存实现。实现代码如下（`org.apache.ibatis.cache.impl.PerpetualCache`）：
```java
// org.apache.ibatis.cache.impl
/**
 * @author Clinton Begin
 */
public class PerpetualCache implements Cache {

  private final String id;

  private final Map<Object, Object> cache = new HashMap<>();

  // ......
}
```

**一级缓存的生命周期有多长？**
1. MyBatis在开启一个数据库会话时，会 创建一个新的`SqlSession对象`，`SqlSession对象`中会有一个新的`Executor对象`，`Executor对象`中持有一个新的`PerpetualCache`对象。  
当会话结束时，`SqlSession对象`及其内部的`Executor对象`还有`PerpetualCache对象`也一并释放掉。
2. 如果`SqlSession`调用了`close()方法`，会释放掉一级缓存`PerpetualCache对象`，一级缓存将不可用。
3. 如果`SqlSession`调用了`clearCache()`，会清空`PerpetualCache对象`中的 **数据** ，但是该对象仍可使用。
4. `SqlSession`中执行了任何一个`update`操作 **(`update()`、`delete()`、`insert()`)** ，都会清空`PerpetualCache对象`的 **数据** ，但是该对象可以继续使用。

**怎么判断某两次查询是完全相同的查询？**  
MyBatis认为，对于两次查询，如果以下条件都完全一样，那么就认为它们是完全相同的两次查询（详细解读参考后文：关闭一级缓存的方式补充）：
- 传入的`statementId`
- 查询时要求的结果集中的结果范围
- 这次查询所产生的最终要传递给`JDBC java.sql.Preparedstatement`的`Sql`语句字符串（`boundSql.getSql()` ）
- 传递给`java.sql.Statement`要设置的参数值

### 2. 代码实现
**重点是要明白：MyBatis执行`SQL`语句之后，这条语句的执行结果被缓存，以后再执行这条语句的时候，会直接从缓存中拿结果，而不是再次执行`SQL`。  
但是一旦执行`新增`或`更新`或`删除`操作，缓存就会被清除。**

#### 准备工作（测试项目搭建）：
`maven`依赖：
```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter</artifactId>
    </dependency>

    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>

    <!--MyBatis依赖-->
    <dependency>
        <groupId>org.mybatis.spring.boot</groupId>
        <artifactId>mybatis-spring-boot-starter</artifactId>
        <version>2.1.4</version>
    </dependency>

    <!--mysql驱动-->
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
    </dependency>

    <!--lombok依赖-->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
    </dependency>
</dependencies>
```

测试`sql`：
```sql
-- ----------------------------
-- Table structure for user_info
-- ----------------------------
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info`  (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '姓名',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_info
-- ----------------------------
INSERT INTO `user_info` VALUES (1, '小明');
INSERT INTO `user_info` VALUES (2, '小王');

SET FOREIGN_KEY_CHECKS = 1;
```

`Springboot`启动类：
```java
@SpringBootApplication
// mapper扫描
@MapperScan(basePackages = "com.example.mybatis")
public class DocDemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DocDemoApplication.class, args);
    }
}
```

`User`实体和`mapper`对象：
```java
// 实体类
@Data
public class User {
    private Integer id;
    private String name;
}

// mapper
@Mapper
public interface UserMapper {
    User getUserById(Integer id);
    int updateUser(User user);
}
```

`UserMapper.xml`
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mybatis.UserMapper">
    <select id="getUserById" resultType="com.example.mybatis.User">
        select id,name from user_info where id = #{id}
    </select>
    <select id="updateUser" parameterType="com.example.mybatis.User">
        update user_info set name = #{name} where id = #{id}
    </select>
</mapper>
```

`application.yml`
```yaml
#数据库链接
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/demo?useUnicode=true&characterEncoding=UTF-8&useSSL=true&serverTimezone=GMT%2B8
    driver-class-name: com.mysql.cj.jdbc.Driver
    username: root
    password: 123456
    
#MyBatis扫描相关
mybatis:
  type-aliases-package: com.example.mybatis
  mapper-locations: classpath*:/mapper/*.xml
  
#日志打印
logging:
  level:
    com.example.mybatis: debug
```
下面将分情况来验证一下：

#### 情况1：同session进行两次相同查询
```java
@SpringBootTest
class DocDemoApplicationTests {

    @Autowired
    SqlSessionFactory factory;

    @Test
    public void userTest() {
        // 获取SqlSession
        SqlSession session = factory.openSession();
        String getUserById = "com.example.mybatis.UserMapper.getUserById";
        
        // 同session进行两次相同查询
        User user1 = session.selectOne(getUserById, 1);
        User user2 = session.selectOne(getUserById, 1);
        System.out.println(user1);
        System.out.println(user2);
        session.commit();
        session.close();
    }
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=1, name=小明)
```
结论：MyBatis只进行 **1** 次数据库查询。

#### 情况2：同session进行两次相同查询，间隔执行commit()/rollback()：
```java
@SpringBootTest
class DocDemoApplicationTests {

    @Autowired
    SqlSessionFactory factory;

    @Test
    public void userTest() {
        // 获取SqlSession
        SqlSession session = factory.openSession();
        String getUserById = "com.example.mybatis.UserMapper.getUserById";
        
        // 同session进行两次相同查询
        User user1 = session.selectOne(getUserById, 1);
        // session.commit();
        session.rollback();
        User user2 = session.selectOne(getUserById, 1);
        System.out.println(user1);
        System.out.println(user2);
        session.commit();
        session.close();
    }
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=1, name=小明)
```
结论：当对`SqlSession`执行`commit()`/`rollback()`时会清空一级缓存，MyBatis进行 **2** 次数据库查询。

#### 情况3：同session进行两次相同查询，间隔执行clearCache()
```java
@SpringBootTest
class DocDemoApplicationTests {

    @Autowired
    SqlSessionFactory factory;

    @Test
    public void userTest() {
        // 获取SqlSession
        SqlSession session = factory.openSession();
        String getUserById = "com.example.mybatis.UserMapper.getUserById";
        
        // 同session进行两次相同查询
        User user1 = session.selectOne(getUserById, 1);
        session.clearCache();// 清空一级缓存
        User user2 = session.selectOne(getUserById, 1);
        System.out.println(user1);
        System.out.println(user2);
        session.commit();
        session.close();
    }
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=1, name=小明)
```
结论：当对`SqlSession`执行`clearCache`时会清空一级缓存，MyBatis进行 **2** 次数据库查询。

#### 情况4：同session进行两次不同的查询
```java
@Test
public void userTest() {
    // 获取SqlSession
    SqlSession session = factory.openSession();
    String getUserById = "com.example.mybatis.UserMapper.getUserById";
    
    // 同session进行两次不同的查询
    User user1 = session.selectOne(getUserById, 1);
    User user2 = session.selectOne(getUserById, 2);
    System.out.println(user1);
    System.out.println(user2);
    session.commit();
    session.close();
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 2(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=2, name=小王)
```
结论：MyBatis进行 **2** 次数据库查询。

#### 情况5：不同session，进行相同查询
```java
@Test
public void userTest() {
    // 获取SqlSession
    SqlSession session1 = factory.openSession();
    SqlSession session2 = factory.openSession();
    String getUserById = "com.example.mybatis.UserMapper.getUserById";
    
    // 不同session，进行相同查询
    User user1 = session1.selectOne(getUserById, 1);
    User user2 = session2.selectOne(getUserById, 1);
    System.out.println(user1);
    System.out.println(user2);
    session1.commit();
    session2.commit();
    session1.close();
    session2.close();
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=1, name=小明)
```
结论：MyBatis进行 **2** 次数据库查询。

#### 情况6：同session，查询后更新数据，再查询相同的语句
```java
@Test
public void userTest() {
    // 获取SqlSession
    SqlSession session = factory.openSession();
    String getUserById = "com.example.mybatis.UserMapper.getUserById";
    String updateUser = "com.example.mybatis.UserMapper.updateUser";

    // 同session，查询之后更新数据，再次查询相同的语句
    // 1.查询
    User userBefore = session.selectOne(getUserById, 1);
    // 2.修改（新增和删除不做演示）
    userBefore.setName("小明-修改后");
    session.update(updateUser, userBefore);
    // 3.再查询
    User userAfter = session.selectOne(getUserById, 1);
    System.out.println(userBefore);
    System.out.println(userAfter);
    session.commit();
    session.close();
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
: ==>  Preparing: update user_info set name = ? where id = ?
: ==> Parameters: 小明-修改后(String), 1(Integer)
: <==    Updates: 1
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明-修改后)
User(id=1, name=小明-修改后)
```
结论：更新操作之后缓存会被清除，MyBatis进行 **2** 次数据库查询。

### 3. 小结
很明显，以上各种情况验证了一级缓存的概念，在同个`SqlSession`中，查询语句相同的`sql`会被缓存，但是一旦执行 **新增** 或 **更新** 或 **删除**操作，就会清空当前的一级缓存。

**并且当对`SqlSession`执行`commit()`/`rollback()`或者`clearCache()`时，也会清空其自身的一级缓存（和执行更新操作的效果一样）。**

### 4. 补充：关闭一级缓存
场景：执行 **2** 次相同`sql`，但是第一次查询`sql`结果会加工处理，比如解析加密字段，或者反编译加密解密用户名/密码字符串等等；如果不关闭一级缓存，等第二次再查询相同`sql`时不会去数据库表重新查询，而是直接使用缓存，从而导致后面拿到的不是原始数据而处理出错

#### 4.1 分析关闭的方式
通过上面的 **情况2、3** 可以知道`commit()`和`clearCache()`会导致缓存清空。  
接下来看源码有哪些 **清空缓存** 的操作，首先是`commit()`源码跟踪：
```java
// 1. 首先是SqlSession接口
public interface SqlSession extends Closeable {
    // ......
	void commit();
    // ......
}

// 2. 找到DefaultSqlSession类对它的实现
public class DefaultSqlSession implements SqlSession {
    // ......
    @Override
    public void commit() {
        commit(false);
    }
    
    // ......
	
    // 2.1 找到commit(false)的方法实现
    @Override
    public void commit(boolean force) {
        try {
            executor.commit(isCommitOrRollbackRequired(force));
            dirty = false;
        } catch (Exception e) {
            throw ExceptionFactory.wrapException("Error committing transaction.  Cause: " + e, e);
        } finally {
            ErrorContext.instance().reset();
        }
    }
    // ......
}

// 3.  继续找executor.commit(isCommitOrRollbackRequired(force));这句代码的方法实现
public abstract class BaseExecutor implements Executor {
    // ......
    @Override
    public void commit(boolean required) throws SQLException {
        if (closed) {
            throw new ExecutorException("Cannot commit, transaction is already closed");
        }
        // 注意这一行代码
        clearLocalCache();
        flushStatements();
        if (required) {
            transaction.commit();
        }
    }
    // ......
    // 3.1. 继续查看clearLocalCache();方法 
    @Override
    public void clearLocalCache() {
        if (!closed) {
            // 清空本地缓存（一级缓存）
            localCache.clear();
            localOutputParameterCache.clear();
        }
    }
    // ......
}

```
可以发现`commit()`除了 **事务提交** 外，最终还调用了 **`clearLocalCache();方法`**

接下来看`clearCache()`源码跟踪：
```java
// 1. 首先是SqlSession接口
public interface SqlSession extends Closeable {
    // ......
    void clearCache();
    // ......
}

// 2. 找到DefaultSqlSession类对它的实现
public class DefaultSqlSession implements SqlSession {
    // ......
    @Override
    public void clearCache() {
        executor.clearLocalCache();
    }
    // ......
}
// 3.  继续找executor.clearLocalCache();这句代码的方法实现
public abstract class BaseExecutor implements Executor {
    // ......
    @Override
    public void clearLocalCache() {
        if (!closed) {
            // 清空本地缓存（一级缓存）
            localCache.clear();
            localOutputParameterCache.clear();
        }
    }
    // ......
}
```
可以发现`clearCache()`最终也是调用了 **`clearLocalCache();方法`。**

#### 4.2 缓存清空方法clearCache()调用说明
那么接下来只需要查看MyBatis中那些地方调用的`clearLocalCache()`方法，阻止调用即可达到关闭`LocalCache`（本地缓存/一级缓存）的目的。

调用的`clearLocalCache()`方法地方如下 **（MyBatis版本2.1.4）** ：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/MyBatis/MayBatis的一二级缓存/mybatis中调用clearLocalCache的地方.png)
</center>

**第1个：BaseExecutor第116行**  
调用`BaseExecutor`的`update方法`的时候：
```java
@Override
public int update(MappedStatement ms, Object parameter) throws SQLException {
    ErrorContext.instance().resource(ms.getResource()).activity("executing an update").object(ms.getId());
    if (closed) {
        throw new ExecutorException("Executor was closed.");
    }
    clearLocalCache();// BaseExecutor第116行
    return doUpdate(ms, parameter);
}
```

**第2个：BaseExecutor第147行**  
调用`BaseExecutor.query`， **判断是否第一次查询** 的时候，且配置了`flushCache`为`true`时：
```java
@Override
public <E> List<E> query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql) throws SQLException {
    ErrorContext.instance().resource(ms.getResource()).activity("executing a query").object(ms.getId());
    if (closed) {
        throw new ExecutorException("Executor was closed.");
    }
    if (queryStack == 0 && ms.isFlushCacheRequired()) {
        clearLocalCache();// BaseExecutor第147行
    }
    // ......
}
```

**第3个：BaseExecutor第169行**  
同样是调用`BaseExecutor.query`，查询后，缓存的作用域不是`STATEMENT`，且这里 **必须要是第一次查询，子查询是不会清空缓存的。** 
```java
@Override
public <E> List<E> query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql) throws SQLException {
    // ......
    // issue #601
    deferredLoads.clear();
    if (configuration.getLocalCacheScope() == LocalCacheScope.STATEMENT) {
        // issue #482
        clearLocalCache();// BaseExecutor第169行
    }
    // ......
}
```

**第4个：BaseExecutor第241行**  
调用`BaseExecutor.commit`时：
```java
@Override
public void commit(boolean required) throws SQLException {
    if (closed) {
        throw new ExecutorException("Cannot commit, transaction is already closed");
    }
    clearLocalCache();// BaseExecutor第241行
    flushStatements();
    if (required) {
        transaction.commit();
    }
}
```

**第5个：BaseExecutor第252行**  
调用`BaseExecutor.rollback`时：
```java
@Override
public void rollback(boolean required) throws SQLException {
    if (!closed) {
        try {
            clearLocalCache();// BaseExecutor第252行
            flushStatements(true);
        } finally {
            if (required) {
                transaction.rollback();
            }
        }
    }
}
```

**第6个`CachingExecutor`的161行和第7个`DefaultSqlSessiond`的252行最终指向的就是`clearLocalCache()`方法，这里不再赘述**

#### 4.3 关闭一级缓存方法实现（方式1）
通过上面的分析，我们可以发现缓存清空的地方有如下几点：
1. 调用`BaseExecutor.update`时；
2. 调用`BaseExecutor.query`时，判断是否第一次查询的时候，且配置了`flushCache`为`true`；
3. 调用`BaseExecutor.query`时，查询后，缓存的作用域不是`STATEMENT`，且这里必须要是第一次查询，子查询是不会清空缓存的；
4. 调用`BaseExecutor.commit`时；
5. 调用`BaseExecutor.rollback`时。

**其中 query第一次查询、update、commit、rollback是无法干预的（重写可以实现，这里不做延伸解读），因此可以通过修改缓存的作用域来达到不清空缓存的目的。**

通过源码可以发现作用域的枚举值如下：
```java
// 枚举值
public enum LocalCacheScope {
  SESSION,STATEMENT
}

// 默认配置
public class Configuration {
    // ......
	protected LocalCacheScope localCacheScope = LocalCacheScope.SESSION;
    // ......
}
```

通过`yml`修改默认配置：
```yaml
mybatis:
  configuration:
    local-cache-scope: STATEMENT
```
修改配置之后，在执行笔记中的 **一级缓存情况1：同`session`进行两次相同查询** 。可以发现执行了两次数据库操作，因此达到了关闭一级缓存的目的。

#### 4.4 关闭一级缓存的方式补充（方式2）
上述的关闭方法为 **全局** 关闭一级缓存，当然也有方法只对需要的`sql`进行缓存关闭。  
即通过变更`localcache`的`CacheKey key`，使`this.localCache.getObject(key)`取到的值为`null`。

缓存针对的是查询操作，我们依旧用上面 **情况1：同`session`进行两次相同查询** 中调用的`session.selectOne()`方法进行逐步分析。  
源码跟踪：
```java
// 1. 进入session.selectOne()方法实现--->DefaultSqlSession.selectOne()
public class DefaultSqlSession implements SqlSession {
    // ......
    @Override
    public <T> T selectOne(String statement, Object parameter) {
        // Popular vote was to return null on 0 results and throw exception on too many.
        List<T> list = this.selectList(statement, parameter);
        if (list.size() == 1) {
            return list.get(0);
        } else if (list.size() > 1) {
            throw new TooManyResultsException("Expected one result (or null) to be returned by selectOne(), but found: " + list.size());
        } else {
            return null;
        }
    }

    // ......

    // 1.1 进入 this.selectList()
    @Override
    public <E> List<E> selectList(String statement, Object parameter) {
        return this.selectList(statement, parameter, RowBounds.DEFAULT);
    }

    // 1.2 进入 this.selectList()
    @Override
    public <E> List<E> selectList(String statement, Object parameter, RowBounds rowBounds) {
        try {
            MappedStatement ms = configuration.getMappedStatement(statement);
            return executor.query(ms, wrapCollection(parameter), rowBounds, Executor.NO_RESULT_HANDLER);
        } catch (Exception e) {
            throw ExceptionFactory.wrapException("Error querying database.  Cause: " + e, e);
        } finally {
            ErrorContext.instance().reset();
        }
    }

    // ......
}

// 2. 继续进入executor.query()方法的实现 --- > BaseExecutor.query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler)
public abstract class BaseExecutor implements Executor {
    // ......

    @Override
    public <E> List<E> query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler) throws SQLException {
        BoundSql boundSql = ms.getBoundSql(parameter);
        // 注意这里创建了一个CacheKey
        CacheKey key = createCacheKey(ms, parameter, rowBounds, boundSql);
        return query(ms, parameter, rowBounds, resultHandler, key, boundSql);
    }

    // ......

    // 2.1 继续进入BaseExecutor.query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql)方法
    @Override
    public <E> List<E> query(MappedStatement ms, Object parameter, RowBounds rowBounds, ResultHandler resultHandler, CacheKey key, BoundSql boundSql) throws SQLException {
        ErrorContext.instance().resource(ms.getResource()).activity("executing a query").object(ms.getId());
        if (closed) {
            throw new ExecutorException("Executor was closed.");
        }
        if (queryStack == 0 && ms.isFlushCacheRequired()) {
            clearLocalCache();
        }
        List<E> list;
        try {
            queryStack++;
            list = resultHandler == null ? (List<E>) localCache.getObject(key) : null;
            // 判断list是否为null，如果为null，则调用queryFromDatabase从数据库中获取，否则调用缓存
            if (list != null) {
                handleLocallyCachedOutputParameters(ms, key, parameter, boundSql);
            } else {
                list = queryFromDatabase(ms, parameter, rowBounds, resultHandler, key, boundSql);
            }
        } finally {
            queryStack--;
        }
        if (queryStack == 0) {
            for (DeferredLoad deferredLoad : deferredLoads) {
                deferredLoad.load();
            }
            // issue #601
            deferredLoads.clear();
            if (configuration.getLocalCacheScope() == LocalCacheScope.STATEMENT) {
                // issue #482
                clearLocalCache();
            }
        }
        return list;
    }
}

```

截取关键代码块：
```java
list = resultHandler == null ? (List<E>) localCache.getObject(key) : null;
// 判断list是否为null，如果为null，则调用queryFromDatabase从数据库中获取，否则调用缓存
if (list != null) {
    handleLocallyCachedOutputParameters(ms, key, parameter, boundSql);
} else {
    list = queryFromDatabase(ms, parameter, rowBounds, resultHandler, key, boundSql);
}
```
通过这段代码可以发现只要`localCache.getObject(key)`为`null`，则每次查询必定调用`queryFromDatabase`方法，从而不使用缓存。

那么接下来就回去看一下`key`的创建方法：`BaseExecutor.createCacheKey();`源码如下：
```java
@Override
public CacheKey createCacheKey(MappedStatement ms, Object parameterObject, RowBounds rowBounds, BoundSql boundSql) {
    if (closed) {
        throw new ExecutorException("Executor was closed.");
    }
    CacheKey cacheKey = new CacheKey();
    cacheKey.update(ms.getId());
    cacheKey.update(rowBounds.getOffset());
    cacheKey.update(rowBounds.getLimit());
    cacheKey.update(boundSql.getSql());
    List<ParameterMapping> parameterMappings = boundSql.getParameterMappings();
    TypeHandlerRegistry typeHandlerRegistry = ms.getConfiguration().getTypeHandlerRegistry();
    // mimic DefaultParameterHandler logic
    for (ParameterMapping parameterMapping : parameterMappings) {
        if (parameterMapping.getMode() != ParameterMode.OUT) {
            Object value;
            String propertyName = parameterMapping.getProperty();
            if (boundSql.hasAdditionalParameter(propertyName)) {
                value = boundSql.getAdditionalParameter(propertyName);
            } else if (parameterObject == null) {
                value = null;
            } else if (typeHandlerRegistry.hasTypeHandler(parameterObject.getClass())) {
                value = parameterObject;
            } else {
                MetaObject metaObject = configuration.newMetaObject(parameterObject);
                value = metaObject.getValue(propertyName);
            }
            cacheKey.update(value);
        }
    }
    if (configuration.getEnvironment() != null) {
        // issue #176
        cacheKey.update(configuration.getEnvironment().getId());
    }
    return cacheKey;
}
```
从源码可以看出 **key是由`statementId`+原生`sql`+`value`（查询出来的对象）+ `sqlsession.hashcode`组成。** 

因此变更`key`，可以从原生`sql`入手。

但是我们查询的时候，如果查询条件一样，怎么保证参数值不一样，但是又不能影响查询结果呢？  
给sql查询加上一个 **随机数** 即可，如上面测试案例中的`getUserById方法`中的`sql`可以修改为：
```sql
select id,name from user_info where id = #{id} and #{uuid}=#{uuid}
```

对应的`mapper`和测试方法方法做如下修改：
```java
// mapper
User getUserById(Integer id, String uuid);

// 测试方法
@Test
public void userTest() {
    // 获取SqlSession
    SqlSession session = factory.openSession();
    String getUserById = "com.example.mybatis.UserMapper.getUserById";

    // 同session进行两次相同查询
    Map param1 = new HashMap();
    param1.put("id",1);
    param1.put("uuid",UUID.randomUUID());
    User user1 = session.selectOne(getUserById, param1);

    Map param2 = new HashMap();
    param2.put("id",1);// 用户id相同
    param2.put("uuid",UUID.randomUUID());// 随机uuid不同
    User user2 = session.selectOne(getUserById, param2);

    System.out.println(user1);
    System.out.println(user2);
    session.commit();
    session.close();
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ? and ?=?
: ==> Parameters: 1(Integer), 78c73b95-b7f8-41ac-bde4-d50fe8486b04(UUID), 78c73b95-b7f8-41ac-bde4-d50fe8486b04(UUID)
: <==      Total: 1
: ==>  Preparing: select id,name from user_info where id = ? and ?=?
: ==> Parameters: 1(Integer), 1a2d6661-61a2-44cc-a5f8-f137aea96458(UUID), 1a2d6661-61a2-44cc-a5f8-f137aea96458(UUID)
: <==      Total: 1
User(id=1, name=小明-修改后)
User(id=1, name=小明-修改后)
```
可以发现每次产生的`sql`就会不一样，导致取到不一样`CacheKey key`，进而使`this.localCache.getObject(key) = null`，这样就可以让MyBatis每次都进行数据库查询，从而达到禁用一级缓存的目的。

**<font color="red">注意：这个`CacheKey key`是否相等就是MyBatis用来判断两次查询是否完全相同的依据。</font>**

#### 4.5 小结
- 关闭方式1是基于 **全局** 配置；
- 关闭方式2是基于 **局部** 配置。

缓存存在的意义不再赘述，因此再开发中若非业务需要，不建议关闭MyBatis的一级缓存，因为MyBatis配置一级缓存的意义，本身就是出于提供性能考虑。  
但是如果由于业务原因一定需要关闭，也建议采用 **方式2（通过添加随机值的方式）** ，因为这种方式可以针对具体的业务`sql`，而不是全局。  **不过这种方式肯定对性能有一定的影响，这就要看实际应用的取舍了。**

## 三、MyBatis的二级缓存
### 1. 简述
MyBatis的二级缓存的工作模式如下图：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/MyBatis/MayBatis的一二级缓存/mybatis二级缓存示意图.png)
</center>

#### 1.1 二级缓存出现的原因
**之所以称之为“二级缓存”，是相对于“一级缓存”而言的。**

既然有了一级缓存，那么为什么要提供二级缓存呢？  
我们知道，在一级缓存中，不同`sqlSession`进行相同`SQL`查询的时候，是查询两次数据库的。显然这是一种浪费，既然`SQL`查询相同，不同的只是`sqlSession`，完全没有必要再次查库了，直接利用缓存数据即可，这种思想就是MyBatis二级缓存的初衷。

另外，`Spring（SpringBoot）`和`MyBatis`整合时，每次查询之后都要进行关闭`sqlSession`，关闭之后缓存数据被清空（数据库连接池可以做到`sqlSession`的复用，这里不做延伸）。所以`MyBatis`和`Spring（SpringBoot）`整合之后，一级缓存是没有意义的。  
如果开启二级缓存，关闭`sqlSession`后，会把该`sqlSession`一级缓存中的数据添加到 **`mapper namespace`** 的二级缓存中（**一个`namespace`对应一个二级缓存**）。这样，缓存数据在`sqlSession`关闭之后依然存在。

#### 1.2 二级缓存工作机制
- 一个会话`sqlSession`查询一条数据，这个数据就会被放在当前会话的一级缓存中；
- 如果当前会话 **关闭** 了，这个会话对应的一级缓存就会被清空；此时一级缓存中的数据被保存到二级缓存中；
- 新的会话查询信息，就可以从二级缓存中获取内容；
- 不同的`mapper`查出的数据会放在自己对应的`缓存`中。

#### 1.3 二级缓存的设置
**默认情况下，MyBatis只启用了本地的会话缓存（一级缓存），它仅仅对一个会话`sqlSession`中的数据进行缓存。**

二级缓存是`Mapper(namespace)级别`的缓存，多个`SqlSession`去操作同一个`Mapper`的`sql`语句，多个`SqlSession`可以共用二级缓存，二级缓存是跨`SqlSession`的。要启用全局的二级缓存，只需要在`SQL`映射文件（`xxxMapper.xml`）中添加一行：

```xml
<cache/>
```
上面这个简单语句的效果如下（即不配置任何参数的默认效果）:
- 映射语句文件中的所有 `select` 语句的结果将会被缓存。
- 映射语句文件中的所有 `insert`、`update` 和 `delete` 语句会 **刷新缓存**。
- 缓存会使用最近 **最少使用算法（`LRU, Least Recently Used`）** 来清除不需要的缓存。
- 缓存不会定时进行刷新（也就是说，没有固定的刷新间隔）。
- 缓存会保存列表或对象的`1024`个引用。
- 缓存会被视为 **读/写** 缓存，这意味着获取到的对象并不是 **共享** 的，可以安全地被调用者修改，而不干扰其他调用者或线程所做的潜在修改。

> 提示：缓存只作用于 `cache` 标签所在的映射文件中的语句。如果你混合使用 `Java API` 和 `XML 映射文件`，在共用接口中的语句将不会被默认缓存。你需要使用 `@CacheNamespaceRef`注解指定缓存作用域。

上述默认属性可以通过 `cache` 元素的属性来修改。比如：
```xml
<cache
  eviction="FIFO"
  flushInterval="60000"
  size="512"
  readOnly="true"/>
```
这个更高级的配置创建了一个 `FIFO` 缓存，每隔 `60` 秒刷新，最多可以存储结果对象或列表的 `512` 个引用，而且返回的对象被认为是`只读`的，因此对它们进行修改可能会在不同线程中的调用者产生冲突。
- `eviction`：回收策略（清除策略）	默认的清除策略是 LRU。可用的清除策略有：
  - `LRU` – 最近最少使用：移除最长时间不被使用的对象。（默认）
  - `FIFO` – 先进先出：按对象进入缓存的顺序来移除它们。
  - `SOFT` – 软引用：基于垃圾回收器状态和软引用规则移除对象。
  - `WEAK` – 弱引用：更积极地基于垃圾收集器状态和弱引用规则移除对象。
- `flushInterval`（刷新间隔）属性可以被设置为任意的正整数，设置的值应该是一个以毫秒为单位的合理时间量。 默认情况是不设置，也就是没有刷新间隔，缓存仅仅会在调用语句时刷新。
- `size`（引用数目）属性可以设置为任意正整数，要注意缓存对象的大小和运行环境中可用的内存资源。默认值是 `1024`。
- `readOnly`（只读）属性可以被设置为 `true` 或 `false`，默认值时`false`。  
只读的缓存会给所有调用者返回缓存对象的相同实例，因此这些对象不能被修改。这就提供了可观的性能提升。而可读写的缓存会（通过序列化）返回缓存对象的拷贝速度上会慢一些，但是更安全，因此默认值是 `false`。

> 提示：二级缓存是事务性的。这意味着，当 `SqlSession` **完成并提交时，或是完成并回滚，** 但没有执行 `flushCache=true` 的 `insert/delete/update` 语句时，缓存会获得 **更新**。

**<font color="red">注意：实现二级缓存的时候，MyBatis要求返回的POJO必须是可序列化的。 也就是要求实现Serializable接口</font>**

**补充：二级缓存其他相关配置**  
`mapper.xml`中 **增删改查** 语句有两个属性`useCache`和`flushCache`需要注意：
1. 当为`select`语句时：
    - `flushCache`默认为`false`，表示任何时候语句被调用，都不会去清空本地缓存（一级缓存）和二级缓存；改为`true`则会清空二级缓存 **（一级缓存一直可用）** 。
    - `useCache`默认为`true`，表示会将本条语句的结果进行二级缓存；改为`false`则不使用缓存 **（一级缓存依然可以使用，二级缓存不可用）** 。
2. 当为`insert`、`update`、`delete`语句时：
    - `flushCache`默认为`true`，表示任何时候语句被调用，都会导致本地缓存（一级缓存）和二级缓存被清空；改为`false`则不会清空缓存。
    - **`useCache`属性在该情况下没有。**

### 2. 代码实现
创建一个`Bean`并序列化  
> 由于二级缓存的数据不一定都是存储到内存中，它的存储介质多种多样，所以需要给缓存的对象执行序列化(如果存储在内存中的话，不序列化也是可以的)。  

修改后的实体类如下：
```java
@Data
public class User implements Serializable {
    private Integer id;

    private String name;
}
```

在映射文件`UserMapper.xml`中开启二级缓存：
```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper
        PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mybatis.UserMapper">
    <!--开启本mapper的namespace下的二级缓存-->
    <!--
        eviction:代表的是缓存回收策略，目前MyBatis提供以下策略。
        (1) LRU,最近最少使用的，一处最长时间不用的对象
        (2) FIFO,先进先出，按对象进入缓存的顺序来移除他们
        (3) SOFT,软引用，移除基于垃圾回收器状态和软引用规则的对象
        (4) WEAK,弱引用，更积极的移除基于垃圾收集器状态和弱引用规则的对象。这里采用的是LRU，
                移除最长时间不用的对形象

        flushInterval:刷新间隔时间，单位为毫秒，这里配置的是60秒刷新，如果你不配置它，那么当
        SQL被执行的时候才会去刷新缓存。

        size:引用数目，一个正整数，代表缓存最多可以存储多少个对象，不宜设置过大。设置过大会导致内存溢出。
        这里配置的是1024个对象

        readOnly:只读，意味着缓存数据只能读取而不能修改，这样设置的好处是我们可以快速读取缓存，缺点是我们没有
        办法修改缓存，他的默认值是false
    -->
    <cache
           eviction="LRU"
           flushInterval="60000"
           size="1024"
           readOnly="true"/>

    <select id="getUserById" resultType="com.example.mybatis.User">
        select id, name from user_info where id = #{id}
    </select>
</mapper>
```

测试：
```java
@Test
public void secondCacheUserTest() {
    // 获取SqlSession
    SqlSession session1 = factory.openSession();
    SqlSession session2 = factory.openSession();
    String getUserById = "com.example.mybatis.UserMapper.getUserById";

    User user1 = session1.selectOne(getUserById, 1);
    session1.commit();
    session1.close();

    User user2 = session2.selectOne(getUserById, 1);
    session2.commit();
    session2.close();

    System.out.println(user1);
    System.out.println(user2);
}
```

执行结果：
```
Cache Hit Ratio [com.example.mybatis.UserMapper]: 0.0
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=1, name=小明)
..............
Cache Hit Ratio [com.example.mybatis.UserMapper]: 0.5
```
可以从结果看到，`sql`只执行了一次，证明我们的二级缓存生效了。

**注意：上面打印了一个`Cache Hit Ratio`（缓存命中率）为`0.0`，后面则是`0.5`。**

解释：
- 第一查询数据时:
  由于是从数据库中查询的数据，还没有进入缓存，此时的缓存命中率为了`0`，关闭此数据库连接后（或`commit()`之后）
- 第二次再查询相同的数据时：
  由于二级缓存将数据缓存进内存中，第二次将会直接从内存中去取这条相同的数据，缓存将命中，所以此时的缓存命中率为`0.5`
- 第三次查询相同的数据，则命中率为`0.66666`，以此类推…

**验证：如果将同样的查询执行三次，测试代码如下：**
```java
@Test
public void secondCacheUserTest() {
    // 获取SqlSession
    SqlSession session1 = factory.openSession();
    SqlSession session2 = factory.openSession();
    SqlSession session3 = factory.openSession();
    String getUserById = "com.example.mybatis.UserMapper.getUserById";

    User user1 = session1.selectOne(getUserById, 1);
    session1.commit();
    session1.close();

    User user2 = session2.selectOne(getUserById, 1);
    session2.commit();
    session2.close();

    User user3 = session3.selectOne(getUserById, 1);
    session3.commit();
    session3.close();

    System.out.println(user1);
    System.out.println(user2);
    System.out.println(user3);
}
```

执行结果：
```
: ==>  Preparing: select id,name from user_info where id = ?
: ==> Parameters: 1(Integer)
: <==      Total: 1
User(id=1, name=小明)
User(id=1, name=小明)
..............
Cache Hit Ratio [com.example.mybatis.UserMapper]: 0.5
Cache Hit Ratio [com.example.mybatis.UserMapper]: 0.6666666666666666
```
可以发现：第一次命中率为`0.5`，第二次为`0.66666666`，即： **<font color="red">Cache Hit Ratio=从内存中查询的次数 / 总查询次数</font>**

### 3. 二级缓存复用cache-ref
对某一命名空间（`namespace`）的语句，只会使用该命名空间的缓存进行缓存或刷新。但你可能会想要在多个命名空间中共享相同的缓存配置和实例。  
要实现这种需求，可以在指定`mapper.xml`使用 `cache-ref` 元素来引用另一个缓存。
```xml
<cache-ref namespace="cn.mybatis.mapper.XXXMapper"/>
```

### 4. 二级缓存应用场景和局限性
#### 4.1 应用场景
**对查询频率高，变化频率低，用户对查询结果实时性要求不高的数据建议使用二级缓存。** 如：耗时较高的统计分析`sql`、电话账单查询`sql`等。  
通过设置刷新间隔时间，由MyBatis每隔一段时间自动清空缓存，根据数据变化频率设置缓存刷新间隔`flushInterval`，比如设置为`30`分钟、`60`分钟、`24`小时等，根据需求而定。

#### 4.2 局限性
**MyBatis二级缓存对细粒度的数据级别的缓存实现不好。比如针对一个表的某些操作并不在他独立的namespace下进行。**

例如在`UserMapper.xml`中有大多数针对`user表`的操作。但是在某一个`XXXMapper.xml`中，还有针对`user单表`的操作。  
这会导致`user`在两个命名空间（`namespace`）下的数据不一致。如果在`UserMapper.xml`中做了刷新缓存的操作，在`XXXMapper.xml`中缓存仍然有效，此时如果有针对`user`的单表查询，使用缓存的结果可能会不正确。

更危险的情况是在`XXXMapper.xml`做了`insert`、`update`、`delete`操作时，会导致`UserMapper.xml`中的各种操作充满未知和风险。

上述有关这样单表的操作可能不常见。但是有一种常见的情况 ===> **一个命名空间中进行多表操作。**

**多表操作一定不能使用缓存**  
首先不管多表操作写到那个`namespace`下，都会存在某个表的其他操作不在这个`namespace`下的情况。  
例如两个表：`role`和`user_role`，如果想查询出某个用户的全部角色`role`，就一定会涉及到多表的操作：
```xml
<select id="selectUserRoles" resultType="UserRoleVO">
    select * from user_role a,role b where a.roleid = b.roleid and a.userid = #{userid}
</select>
```
像上面这个查询，你会写到那个`xml`中呢？？  
不管是写到`RoleMapper.xml`还是`UserRoleMapper.xml`，或者是一个独立的`XxxMapper.xml`中。如果使用了二级缓存，都会导致上面这个查询结果可能不正确；
如果你正好在其他的`Mapper.xml`中修改了这个用户的角色，上面这个查询使用缓存的时候结果就是错的。

不过也可以让它们都使用同一个`namespace`（通过`<cache-ref>`复用）来避免脏数据，但是当遇到复杂的操作时过多的复用缓存，那就失去了缓存的意义。 

**<font color="red">也就是说，二级缓存尽量不要使用。</font>**

#### 4.3 局限性补救措施
解决多表操作避免脏数据还是有法解决的。

解决思路就是通过拦截器判断执行的`sql`涉及到那些表（可以用`jsqlparser`解析），然后把相关表的缓存自动清空。 **但是这种方式对缓存的使用效率是很低的。**  
设计这样一个插件是相当复杂的， **还是建议，放弃二级缓存，在业务层使用可控制的缓存代替更好** 。

## 四、总结
**一级缓存与二级缓存的不同之处：**
1. 一级缓存默认开启，而二级缓存默认关闭。
2. 一级缓存指的是Mybaits中`SqlSession`对象的缓存，不同的`SqlSession`之间的缓存数据区域（`HashMap`）是互相不影响的；  
二级缓存指的是一个命名空间（`namespace`）或一个`mapper`中的缓存，多个`SqlSession`可以共用二级缓存，二级缓存是跨`SqlSession`的。
3. **Mybatis和Spring整合的时候， 一级缓存与事务有关，而二级缓存与事务无关。**
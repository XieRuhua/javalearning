# swagger的集成与使用

版本说明

| 名称         | 版本          | 备注            |
| :----------- | :------------ | :-------------- |
| springboot   | 2.3.0.RELEASE |                 |
| swagger      | 2.9.2         |                 |
| swagger-ui   | 2.9.2         | swagger的页面ui |
| bootstrap-ui | 1.9.3         | swagger美化ui   |

## 一、swagger集成

### 1. pom依赖引入
```xml
        <!-- swagger-ui start-->
        <dependency>
            <groupId>io.springfox</groupId>
            <artifactId>springfox-swagger2</artifactId>
            <version>2.9.2</version>
        </dependency>
        <dependency>
            <groupId>io.springfox</groupId>
            <artifactId>springfox-swagger-ui</artifactId>
            <version>2.9.2</version>
        </dependency>
        <!--        swagger美化ui-->
        <dependency>
            <groupId>com.github.xiaoymin</groupId>
            <artifactId>swagger-bootstrap-ui</artifactId>
            <version>1.9.3</version>
        </dependency>
        <!-- swagger-ui end-->
```

### 2. 相关配置
#### 2.1 swagger启动引擎等配置
```java
@Configuration
@EnableSwagger2
public class SwaggerConfig {
    /**
     * 创建一个Docket对象
     * 调用select()方法，
     * 生成ApiSelectorBuilder对象实例，该对象负责定义外漏的API入口
     * 通过使用RequestHandlerSelectors和PathSelectors来提供Predicate，在此我们使用any()方法，将所有API都通过Swagger进行文档管理
     * @return
     */
    @Bean
    public Docket createRestApi() {
        return new Docket(DocumentationType.SWAGGER_2)
                .apiInfo(apiInfo())
                .select()
//                .apis(RequestHandlerSelectors.any())
                .apis(RequestHandlerSelectors.basePackage("com.example.swaggertest.controller"))
                .paths(PathSelectors.any())
                .build();
    }

    /**
     * 首页相关信息配置
     * @return
     */
    private ApiInfo apiInfo() {
        return new ApiInfoBuilder()
                //标题
                .title("测试swagger 相关")
                //简介
                .description("")
                //服务条款
                .termsOfServiceUrl("")
                //作者个人信息
                .contact(new Contact("avie","",""))
                //版本
                .version("1.0")
                .build();
    }
}
```

#### 2.2 swaggerui配置
```java
@Configuration
public class WebMvcSwaggerConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // 解决 swagger-ui.html 404报错
        registry.addResourceHandler("/swagger-ui.html").addResourceLocations("classpath:/META-INF/resources/");
        // 解决 doc.html 404 报错  美化ui 需要pom依赖
        registry.addResourceHandler("/doc.html").addResourceLocations("classpath:/META-INF/resources/");
    }
    /**
     * 如果有过滤器与拦截器相关全局代码，应该放开以下路径
     * "/swagger-resources/**", "/webjars/**", "/v2/**", "/swagger-ui.html/**"
     */
}
```

## 二、swagger的使用
### 1. swagger的常用注解
**作用于类：**  
[@Api](https://github.com/Api)(description = “测试swagger”, tags = “测试相关”)  
//[@Api](https://github.com/Api)（）用于类：表示标识这个类是swagger的资源

**作用于controller方法定义接口信息：**  
[@ApiOperation](https://github.com/ApiOperation)(value = “测试get获取数据接口”, notes = “该接口是用户获取 测试数据”)

**作用controller方法定义方法参数信息：**  
[@ApiImplicitParam](https://github.com/ApiImplicitParam)(name = “token”, value = “Authorization token”, dataType = “string”, paramType = “header”)

**作用于实体类：**  
[@ApiModel](https://github.com/ApiModel)(value = “测试getData接口请求实体model”)

**作用于实体类熟悉：**  
[@ApiModelProperty](https://github.com/ApiModelProperty)(value = “用户id”,name = “name”,example = “123456789”)

### 2. swagger的页面访问
常用ui：http://localhost:8081/swagger-ui.html  
推荐使用美化ui(标准api风格knife4j)：http://localhost:8081/doc.html  

[**knife4j**：是为Java MVC框架集成Swagger生成Api文档的增强解决方案](https://doc.xiaominfo.com/knife4j/)

## 三、swagger的注意点
### 1. ApiModel名字重复，swagger-ui会展示异常
#### 1.1 问题描述：
使用swagger时，在swagger稳文档页面展示的入参参数异常

#### 1.2 详细描述：
如：两个参数类为嵌套关系parent->child
```java
@Data
@ApiModel("入参参数对象")
public class ParentClass{
    @ApiModelProperty(value = "父名称")
    private String parentName;
    
    @ApiModelProperty(value = "父年龄")
    private String parentAge;
    
    @ApiModelProperty(value = "所有子项")
    private List<ChildClass> childClassList;
}

@Data
@ApiModel("入参参数对象")
public class ChildClass{
    @ApiModelProperty(value = "子名称")
    private String childName;

    @ApiModelProperty(value = "子年龄")
    private String childAge;
}
```
此时在swagger看到的入参参数格式将会是：
```json
{
	"childClassList": [
		{
			"childAge": "",
			"childClassList": [],
			"childName": "",
			"parentAge": "",
			"parentName": ""
		}
	],
	"childName": "",
	"childAge": "",
	"parentAge": "",
	"parentName": ""
}
```
然而这种格式明显时错误的。我们希望的格式是如下这种：
```json
{
	"parentAge": "",
	"parentName": "",
	"childClassList": [
		{
			"childAge": "",
			"childName": ""
		}
	]
}
```
#### 1.3 解决方法：
**因为 @ApiModel 直接使用不规范导致的**

错误用法: 两个关联的类的 **@ApiModel** 属性值一样
```java
@Data
@ApiModel("入参参数对象")
public class ChildClass{
    ........
}

@Data
@ApiModel("入参参数对象")
public class ChildClass{
    ........
}
```
正确用法: 两个关联对象的 **@ApiModel** 属性值不允许重复
```java
@Data
@ApiModel("父级入参参数对象")
public class ChildClass{
    ........
}

@Data
@ApiModel("子级入参参数对象")
public class ChildClass{
    ........
}
```
**说明：**  
**@ApiModel** 属性在同一个服务全局中保持唯一的, swagger 会把所有的 API 中的出入参实体列在 swagger 文档的最下方；  
如果存在多个实体的 **@ApiModel** 注解相同，那么 swagger 只会识别一个，其他的实体会被覆盖，不会被显示， 其他被覆盖的实体在API 被引用的地方在文档中会被识别的相同名称的实体替代， 导致文档展示错乱问题
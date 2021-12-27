### Q1：打包maven依赖为 scope system 时无法将 jar 打进包的问题
#### 详细描述：
当我们使用的jar包不能从maven中央仓库下载的时候，这时候就会将jar包下载在本地，然后通过文件方式引用（假设存放的路径为：/src/main/resources/lib/）。此时包的pom依赖写法为：
```xml
<dependency>
	<groupId>jarGroupId</groupId>
	<artifactId>jarArtifactId</artifactId>
	<version>0.0.0</version>
	<scope>system</scope>
	<systemPath>${project.basedir}/src/main/resources/lib/jar包名.jar</systemPath>
</dependency>
```
此时不论将项目打成jar包还是war包，则外部引用的jar包均不会被打入到WEB-INF/lib/文件夹中。  
导致运行jar包或者war包项目的时候出现ClassNotFoundException的错误。
#### 解决方法：
##### 方式1：
采用私服的形式，将jar上传至maven私服，然后使用普通方式引入pom依赖，打包的时候也能正常打进WEB-INF/lib/文件夹中
##### 方式2：
修改maven打包的插件属性，将本地包也打进去  
**jar包：**
```xml
<packaging>jar</packaging>
```
```xml
<plugins> 
  <plugin> 
    <groupId>org.springframework.boot</groupId>  
    <artifactId>spring-boot-maven-plugin</artifactId>  
    <configuration> 
      <includeSystemScope>true</includeSystemScope> 
    </configuration> 
  </plugin> 
</plugins>
```
**war包：**
```xml
<packaging>war</packaging>
```
```xml
<plugins> 
    <plugin> 
        <groupId>org.apache.maven.plugins</groupId>  
        <artifactId>maven-war-plugin</artifactId>  
        <configuration> 
          <webResources> 
            <resource> 
              <directory>src/main/resources/lib</directory>  
              <targetPath>WEB-INF/lib/</targetPath>  
              <includes> 
                <include>**/*.jar</include> 
              </includes> 
            </resource> 
          </webResources> 
        </configuration> 
    </plugin> 
</plugins>
```
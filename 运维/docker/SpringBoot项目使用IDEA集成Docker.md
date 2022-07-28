# Spring Boot项目使用IDEA集成Docker

**`DockerFile`官方文档：[Dockerfile reference](https://docs.docker.com/engine/reference/builder/)**

### 1. 新建SpringBoot项目
新增一个测试的`Controller`
```java
@RestController
public class HelloController {
    @RequestMapping("/")
    public String hello() {
        return "Hello, SpringBoot With Docker";
    }
}
```

### 2. pom添加插件
#### 2.1 Docker支持（docker插件）
在 `pom.xml`中添加`Docker`镜像名称和其他属性
```xml
<properties>
    <java.version>1.8</java.version>
    <project.framework.version>1.0.0-RELEASE</project.framework.version>
    <maven.antrun.plugin>1.8</maven.antrun.plugin>
    <!-- docker镜像名称-->
    <docker.image.prefix>springboot-test</docker.image.prefix>
    <!-- docker插件版本-->
    <docker.plugin.version>1.0.0</docker.plugin.version>
    <!--jar包原始目录-->
    <directory>${project.basedir}/target</directory>
</properties>
```

添加 `Docker`插件：
```xml
<!--
 docker-maven-plugin插件
 作用：docker打包相关配置，配置和dockerfile文件对标
 注意：dockerfile和此插件中configuration设置同样的属性会报错
 -->
<plugin>
    <groupId>com.spotify</groupId>
    <artifactId>docker-maven-plugin</artifactId>
    <version>${docker.plugin.version}</version>
    <!--配置部分-->
    <configuration>
        <!--指定远程docker地址-->
        <dockerHost>http://192.168.1.226:2375</dockerHost>
        <!--修改imageName节点的内容，改为私有仓库地址和端口，再加上镜像id和TAG,我们要直接传到私服-->
        <!--配置最后生成的镜像名，docker images里的，我们这边取项目名:版本-->
        <imageName>${docker.image.prefix}/${project.name}:${project.framework.version}</imageName>
        <imageTags>
            <imageTag>${project.framework.version}</imageTag>
        </imageTags>
        <!--指定包含 Dockerfile 的目录-->
        <dockerDirectory>${project.basedir}/docker</dockerDirectory>
    </configuration>
</plugin>
```

#### 2.2 添加maven-antrun-plugin插件
插件作用：复制`jar`包到指定目录，复制文件到服务器，连接服务器执行命令等
```xml
<plugin>
    <!--
      maven-antrun-plugin插件
      作用：复制jar包到指定目录，复制文件到服务器，连接服务器执行命令；
           这里是将jar包通过install命令从target复制到docker目录中
     -->
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-antrun-plugin</artifactId>
    <version>${maven.antrun.plugin}</version>
    <executions>
        <execution>
            <id>deploy</id>
            <phase>install</phase>
            <goals>
                <goal>run</goal>
            </goals>
            <configuration>
                <target>
                    <!--删除docker目录中jar包-->
                    <delete failonerror="false">
                        <fileset dir="${project.basedir}/docker/" includes="*.jar"></fileset>
                        <fileset dir="${project.build.directory}/docker/" includes="*.jar"></fileset>
                    </delete>
                    <!--将jar包通过install命令从target复制到docker目录中-->
                    <copy file="${project.build.directory}/${project.build.finalName}.${project.packaging}" todir="${project.basedir}/docker"></copy>
                </target>
            </configuration>
        </execution>
    </executions>
</plugin>
```

#### 2.3 附：pom.xml完整配置
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.6.2</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.xrh</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <properties>
        <java.version>1.8</java.version>
        <project.framework.version>1.0.0-RELEASE</project.framework.version>
        <maven.antrun.plugin>1.8</maven.antrun.plugin>
        <!-- docker镜像名称-->
        <docker.image.prefix>springboot-test</docker.image.prefix>
        <!-- docker插件版本-->
        <docker.plugin.version>1.0.0</docker.plugin.version>
        <!--jar包原始目录-->
        <directory>${project.basedir}/target</directory>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <includeSystemScope>true</includeSystemScope>
                    <mainClass>com.xrh.DemoApplication</mainClass>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <!--可以把依赖的包都打包到生成的Jar包中-->
                            <goal>repackage</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <!--
                maven-antrun-plugin插件
                作用：复制jar包到指定目录，复制文件到服务器，连接服务器执行命令；
                     这里是将jar包通过install命令从target复制到docker目录中
                -->
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-antrun-plugin</artifactId>
                <version>${maven.antrun.plugin}</version>
                <executions>
                    <execution>
                        <id>deploy</id>
                        <phase>install</phase>
                        <goals>
                            <goal>run</goal>
                        </goals>
                        <configuration>
                            <target>
                                <!--删除docker目录中jar包-->
                                <delete failonerror="false">
                                    <fileset dir="${project.basedir}/docker/" includes="*.jar"></fileset>
                                    <fileset dir="${project.build.directory}/docker/" includes="*.jar"></fileset>
                                </delete>
                                <!--将jar包通过install命令从target复制到docker目录中-->
                                <copy file="${project.build.directory}/${project.build.finalName}.${project.packaging}" todir="${project.basedir}/docker"></copy>
                            </target>
                        </configuration>
                    </execution>
                </executions>
            </plugin>

            <!--
            docker-maven-plugin插件
            作用：docker打包相关配置，配置和dockerfile文件对标
            注意：dockerfile和此插件中configuration设置同样的属性会报错
            -->
            <plugin>
                <groupId>com.spotify</groupId>
                <artifactId>docker-maven-plugin</artifactId>
                <version>${docker.plugin.version}</version>
                <!--配置部分-->
                <configuration>
                    <!--指定远程docker地址-->
                    <dockerHost>http://192.168.1.226:2375</dockerHost>
                    <!--修改imageName节点的内容，改为私有仓库地址和端口，再加上镜像id和TAG,我们要直接传到私服-->
                    <!--配置最后生成的镜像名，docker images里的，我们这边取项目名:版本-->
                    <imageName>${docker.image.prefix}/${project.name}:${project.framework.version}</imageName>
                    <imageTags>
                        <imageTag>${project.framework.version}</imageTag>
                    </imageTags>
                    <!--指定包含 Dockerfile 的目录-->
                    <dockerDirectory>${project.basedir}/docker</dockerDirectory>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### 3. 编写Dockerfile文件
在目录`src/main/`下创建`docker`文件夹，并创建`Dockerfile` 文件，`Dockerfile` 文件用来说明如何来构建镜像：
```bash
# 镜像基于java:8（基础镜像）
FROM java:8

# 维护者
MAINTAINER xrh

# docker容器时区设置
ENV TIME_ZONE Asia/Shanghai
RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

#创建项目日志存放的文件夹
ENV APP_HOME /app
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# 将jar包添加到容器中
COPY demo-0.0.1-SNAPSHOT.jar $APP_HOME/demo-0.0.1.jar
# 等同于
# ADD demo-0.0.1-SNAPSHOT.jar $APP_HOME/demo-0.0.1.jar

# 指定容器启动程序及参数  <ENTRYPOINT> "<CMD>"
# 运行jar包命令 "nohup" "&" 可省略
ENTRYPOINT ["java","-jar","/app/demo-0.0.1.jar"]
```

- `FROM`：指定一个已经存在的镜像，告诉Docker后续的指令都是在这个基础上进行的。例如：`FROM java:8`表示使用 Jdk1.8 环境为基础镜像进行构建镜像。
- `ADD或COPY`：拷贝文件并且重命名
- `ENTRYPOINTl`：指定容器启动程序及参数  <ENTRYPOINT> <CMD>

**其他更多配置参考官方文档：[Dockerfile reference](https://docs.docker.com/engine/reference/builder/)**

### 4. 项目打包
使用IDEA打包步骤依次如下：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/运维/docker/docker打包顺序.png)
</center>

最终打印如下：
```bash
[INFO] Scanning for projects...
[INFO] 
[INFO] ----------------------------< com.xrh:demo >----------------------------
[INFO] Building demo 0.0.1-SNAPSHOT
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- docker-maven-plugin:1.0.0:build (default-cli) @ demo ---
[INFO] Using authentication suppliers: [ConfigFileRegistryAuthSupplier]
[INFO] Copying E:\private\demo-docker\docker\demo-0.0.1-SNAPSHOT.jar -> E:\private\demo-docker\target\docker\demo-0.0.1-SNAPSHOT.jar
[INFO] Copying E:\private\demo-docker\docker\Dockerfile -> E:\private\demo-docker\target\docker\Dockerfile
[INFO] Building image springboot-test/demo:1.0.0-RELEASE
Step 1/9 : FROM java:8

 ---> d23bdf5b1b1b
Step 2/9 : MAINTAINER xrh

 ---> Using cache
 ---> 7570f2cff6c6
Step 3/9 : ENV TIME_ZONE Asia/Shanghai

 ---> Using cache
 ---> da90272bdba3
Step 4/9 : RUN /bin/cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

 ---> Using cache
 ---> 8d5dffe94e81
Step 5/9 : ENV APP_HOME /app

 ---> Using cache
 ---> b00f6a54a583
Step 6/9 : RUN mkdir -p $APP_HOME

 ---> Using cache
 ---> ef2204dedad8
Step 7/9 : WORKDIR $APP_HOME

 ---> Using cache
 ---> d04ac8d2edcb
Step 8/9 : COPY demo-0.0.1-SNAPSHOT.jar $APP_HOME/demo-0.0.1.jar

 ---> 1f0cd43d1171
Step 9/9 : ENTRYPOINT ["java","-jar","/app/demo-0.0.1.jar"]

 ---> Running in 984edbfa0dfe
Removing intermediate container 984edbfa0dfe
 ---> 643631012037
ProgressMessage{id=null, status=null, stream=null, error=null, progress=null, progressDetail=null}
Successfully built 643631012037
Successfully tagged springboot-test/demo:1.0.0-RELEASE
[INFO] Built springboot-test/demo:1.0.0-RELEASE
[INFO] Tagging springboot-test/demo:1.0.0-RELEASE with 1.0.0-RELEASE
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time: 17.985 s
[INFO] Finished at: 2022-07-28T17:24:54+08:00
[INFO] ------------------------------------------------------------------------

Process finished with exit code 0
```

<font color="red">注意：镜像名称不能出现大写</font>

如下配置：
```xml
<properties>
	<docker.image.prefix>springBoot-test</docker.image.prefix>
</properties>
```

会出现以下错误：
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/运维/docker/docker镜像名大写异常.png)
</center>

### 5. 镜像查看
`docker`插件配置中设置了`docker`服务地址，到对应地址中查看镜像。
```bash
[root@localhost ~]# docker images
REPOSITORY                                                             TAG                  IMAGE ID       CREATED         SIZE
springboot-test/demo                                                   1.0.0-RELEASE        643631012037   3 minutes ago   661MB
java                                                                   8                    d23bdf5b1b1b   5 years ago     643MB
```

**注意：如果没有`java8`的基础镜像，我们的目标镜像会运行失败，需要先`pull`下来**

搜索`docker`中的`java`镜像：
```bash
[root@localhost ~]# docker search java
NAME                                 DESCRIPTION                                     STARS     OFFICIAL   AUTOMATED
node                                 Node.js is a JavaScript-based platform for s…   11734     [OK]
tomcat                               Apache Tomcat is an open source implementati…   3368      [OK]
openjdk                              "Vanilla" builds of OpenJDK (an open-source …   3362      [OK]
...........................
```

下载所需的`java8`镜像：
```bash
docker pull docker.io/lwieske/java-8
```

下载完成之后，将`dockerfile`中的基础镜像改为对应的镜像名，然后重新`build`。

### 6. 镜像运行
因为之前在`dockerfile`中加入了`jar`包的命令`ENTRYPOINT ["java","-jar","/app/demo-0.0.1.jar"]`。

在服务器上直接使用`docker run` 执行（创建一个新的容器并运行一个命令）。

语法为：`docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`
- **-a stdin：** 指定标准输入输出内容类型，可选 STDIN/STDOUT/STDERR 三项；
- **-d：** 后台运行容器，并返回容器ID；
- **-i：** 以交互模式运行容器，通常与 -t 同时使用；
- **-P：** 随机端口映射，容器内部端口**随机**映射到主机的端口
- **-p：** 指定端口映射，格式为：**主机(宿主)端口:容器端口**
- **-t：** 为容器重新分配一个伪输入终端，通常与 -i 同时使用；
- **--name="nginx-lb"：** 为容器指定一个名称；
- **--dns 8.8.8.8：** 指定容器使用的DNS服务器，默认和宿主一致；
- **--dns-search example.com：** 指定容器DNS搜索域名，默认和宿主一致；
- **-h "mars"：** 指定容器的hostname；
- **-e username="ritchie"：** 设置环境变量；
- **--env-file=[]：** 从指定文件读入环境变量；
- **--cpuset="0-2" or --cpuset="0,1,2"：** 绑定容器到指定CPU运行；
- **-m ：**设置容器使用内存最大值；
- **--net="bridge"：** 指定容器的网络连接类型，支持 bridge/host/none/container四种类型；
- **--link=[]：** 添加链接到另一个容器；
- **--expose=[]：** 开放一个端口或一组端口；
- **--volume , -v：** 绑定一个卷

因此完整启动命令为：
```bash
docker run -p 2222:2222 -d --name springboot-docker-demo springboot-test/demo:1.0.0-RELEASE 
```

该命令表示后台启动`springboot-test/demo:1.0.0-RELEASE`镜像，且将镜像端口`2222`映射为`2222`，并将容器命名为`springboot-docker-demo`。

这时候可以通过ip访问项目中写好的接口：http://ip:2222/  
成功打印：`Hello, SpringBoot With Docker`

### 7. 容器查看与停止
#### 7.1 查看运行中的容器
```
[root@localhost ~]# docker ps
CONTAINER ID   IMAGE                                COMMAND                 CREATED        STATUS        PORTS                                     NAMES
45ac051d8a8c   springboot-test/demo:1.0.0-RELEASE   "java -jar /app/demo…"  5 seconds ago  Up 3 seconds  0.0.0.0:2222->2222/tcp, :::2222->2222/tcp springboot-docker-demo
```

输出详情介绍：
- **CONTAINER ID：** 容器 ID。
- **IMAGE：** 使用的镜像。
- **COMMAND：** 启动容器时运行的命令。
- **CREATED：** 容器的创建时间。
- **STATUS：** 容器状态。状态有7种：
    + created（已创建）
    + restarting（重启中）
    + running（运行中）
    + removing（迁移中）
    + paused（暂停）
    + exited（停止）
    + dead（死亡）
- **PORTS:** 容器的端口信息和使用的连接类型（`tcp`\·）。
- **NAMES:** 自动分配的容器名称。

#### 7.2 停止/启动 容器
```bash
# 启动：docker stop容器名
docker stop springboot-docker-demo
```
- `docker start` :启动一个或多个已经被停止的容器
- `docker stop` :停止一个运行中的容器
- `docker restart` :重启容器
#  Maven私服配置
## 配置maven环境

请使用指定的文件，配置环境变量并配置 IDEA 或 eclips

> apache-maven-3.6.3

配置 settings.xml

## Maven相关操作命令

常用命令

> mvn clean  
> mvn install  
> mvn package  
> mvn deploy  
> mvn -Dmaven.test.skip=true  
> mvn source:jar  
> mvn javadoc:jar  
> mvn -e 显示详细错误 信息  
> mvn -U 强制更新依赖包  
> mvn -B 该参数表示让Maven使用批处理模式构建项目  
> mvn validate 验证工程是否正确，所有需要的资源是否可用  
> mvn test-compile 编译项目测试代码  
> mvn integration-test 在集成测试可以运行的环境中处理和发布包  
> mvn verify 运行任何检查，验证包是否有效且达到质量标准

示例：

> mvn clean -Dmaven.test.skip=true source:jar javadoc:jar -e -U install

## 项目pom.xml增加配置

> 注：需要发布到Maven私服仓库的jar配置如下

```
<distributionManagement>
    <repository>
        <id>releases</id>
        <name>Releases</name>
        <url>http://192.168.1.211:8081/repository/maven-releases/</url>
    </repository>
    <snapshotRepository>
        <id>snapshots</id>
        <name>Snapshot</name>
        <url>http://192.168.1.211:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
</distributionManagement>
``
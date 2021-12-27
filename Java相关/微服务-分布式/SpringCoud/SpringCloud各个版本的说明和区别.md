# SpringCloud各个版本的说明和区别
***
[SpringCloud的maven地址](https://mvnrepository.com/artifact/org.springframework.cloud/spring-cloud-dependencies?__cf_chl_captcha_tk__=cd2377cfccca747ae31410c55be9164df2a32104-1608707556-0-Ady-kyNtAXLZj5DfIQvQ8maeowJMB27eLdUK6JegldTY4-fSsQMLuuPlujEE2AvLO07KvPpHVIq9OiEmAY4id9Em4mowp1CAoQeuKiwPCRGvXWBaYFLzlDW2s6MNgVjlX7BIQGYmbGbxNyGQDv2Bx4xM2ukoXAW3t3yNAOA8C6gTM9awaHhGNS1ILvGQ5gJBuwRkZAfyKqT5TpQux_PEMKtXODD8kRlpsVzQzWOR1cB43uZE1p7b93Kzw87HckKmwrJfcT5g4zm6tTU_d6LBmF0MBM2q3OcKxgJa-XCmYmUcr_BsZ63rTl087S0uwd0lyRTiiO0TS8qK7gtx4WDM3Ygzt7eJrnt6CCIDNMn2xlwYxHI1EtHxUlGQU2cDg_tL4iBbHD71s7aS3s3j-WJXbB_soG7jAdTN_jLZdRI0QfdA5HsoSHVZ1wYFmu2K65jo7yOH7wQGo-Waut2UqUt2-5swbmySMskr-1kevuOH9Yx0z7Rm1DUkkEmE4dCTFZi7mhiwKJCoQQteEJhfE4pKipdVaVEyEHfKrwtJZ0vr8UwF2BOqLzlZLjYOe-5KMF50uTxfwlB9KZezL5AiusLEK48DJDajgwhAAwxySHgDEPEVLGY_AlA2QQR7ub9epcx-eN39Yotz__zjqMJF7H6VE9E6z-kzVfZIgkEcvK7tpiNS)  
[SpringCloud和SpringBoot版本对应关系](https://start.spring.io/actuator/info)

[toc]
## 一、常见的版本号说明
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.0.3.RELEASE</version>
    <relativePath/>
</parent>
```
其中<version>2.0.3.RELEASE</version>表示具体的版本。  
2：主版本号，当功能模块有较大更新或者整体架构发生变化时，主版本号会更新。  
0：次版本号。次版本表示只是局部的一些变动。  
3：修改版本号。一般是bug的修改或者是小的变动。  
**RELEASE：** 希腊字母版本号。此版本号用户标注当前版本的软件处于哪个开发阶段  
## 二、希腊字母版本号说明
**Base：** 设计阶段。只有相应的设计没有具体的功能实现。  
**Alpha：** 软件的初级版本。基本功能已经实现，但存在较多的bug。  
**Bate：** 相对于Alpha已经有了很大的进步，消除了严重的BUG，但还存在一些潜在的BUG，还需要不断测试。  
**RELEASE：** 最终版本，没有太大的问题。
## 三、SpringCloud的版本号
### 1. 为什么springcloud版本用的是单词而不是数字呢？
设计的目的是为了更好的管理每个SpringCloud子项目的清单，避免自己的版本号与子项目的版本号混淆。
### 2. SpringCloud的版本号规则？
（常用了英国伦敦地铁站的名称来命名）首字母越靠后表示版本号越大。  
如以下版本，依次版本越旧（截至文档书写，版本最新为"2020.0.0"，发布日期Dec, 2020）：
> 2020.0.0  
Hoxton.SR9  
Hoxton.SR8  
.......  
Hoxton.SR3  
Hoxton.RELEASE  
Greenwich.SR6  
Greenwich.SR5  
.......  
Finchley.SR4  
.......

### 3. 关于版本发布说明

版本号后缀 | 说明 | 描述
:--- | :---: | :--
BUILD-XXX       | 开发版        | 开发团队内部使用，不是很稳定
GA              | 稳定版        | 相比于开发版，基本上可以使用了
PRE（M1、M2）   | 里程碑版      | 主要是修复了一些BUG的版本，一个GA后通常有多个里程碑版
RC              | 候选发布版    | 该阶段的软件类似于最终版的一个发行观察期，基本只修复比较严重的BUG
SR              | 正式发布版    | ----
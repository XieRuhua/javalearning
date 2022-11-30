# Java中的IO和NIO

[文档内容参考1：5种I/O模型](https://blog.csdn.net/qq_44836676/article/details/124672227)  
[文档内容参考2：100%弄明白5种IO模型](https://zhuanlan.zhihu.com/p/115912936)  
[文档内容参考3：java之NIO简介](https://blog.csdn.net/K_520_W/article/details/123454627)

[toc]

## 一、IO简述
### 1. 什么是IO
IO在计算机中指`Input/Output`，也就是 **输入** 和 **输出** 。  
**<font color="red">I/O操作是相对于内存而言的</font>** ，从外部设备进入内存就叫`Input`，从内存输出到外部设备就叫`Output`
- Input指从外部读入数据到内存；如：把文件从磁盘读取到内存，从网络读取数据到内存等等。
- Output指把数据从内存输出到外部；如：把数据从内存写入到文件，把数据从内存输出到网络等等。

Java程序在执行的时候，是在内存中进行的，外部的数据需要读写到内存才能处理；而在内存中的数据是随着程序结束就消失的，有时候也需要把数据输出到外部文件。涉及到数据交换的地方通常是磁盘、网络等，就需要IO接口。

比如打开浏览器访问某个网页，浏览器这个程序就需要通过网络IO获取网页内容。
- 浏览器首先会发送数据给对应网页的服务器，告诉它我想要首页的HTML数据，这个动作是往外发数据，即`Output`；
- 目标服务器把网页发过来，浏览器获取发送内容的这个动作是从外面（网络中）接收数据，即`Input`。

所以，通常程序完成IO操作会有`Input`和`Output`两个数据流。当然也有只用一个的情况，比如，从磁盘读取文件到内存，就只有Input操作；反过来把数据写到磁盘文件里，就只是一个Output操作。

再Java中，是通过 **流** 处理`IO`的，这种处理模式称为 **`IO流`** ，IO流是一种顺序读写数据的模式。  
**流的特点：**
1. **先进先出** ：最先写入输出流的数据最先被输入流读取到。
2. **顺序存取** ：可以一个接一个地往流中写入一串字节，读出时也将按写入顺序读取一串字节，不能随机访问中间的数据。（`RandomAccessFile`除外，后续会做介绍）
3. **只读或只写** ：每个流只能是`输入流`或`输出流`的一种，不能同时具备两个功能。输入流只能进行读操作，输出流只能进行写操作。  
在一个数据传输通道中，如果既要写入数据，又要读取数据，则要分别提供两个流。

### 2. IO的分类
**`IO`有`内存IO`、`网络IO`和`磁盘IO`三种，通常说的`IO`指的是后两者。**

#### 2.1 按照流的方向进行分类:
按数据流的方向分为 **输入流、输出流** ，都是相对内存来说的。
- **输入流/读** ：从外部（数据源）把数据输入到程序（内存）。
- **输出流/写** ：把程序的数据（内存）输出到外部（数据源）。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO流分类：输入流、输出流.png)
</center>

#### 2.2 按照读取数据方式（数据类型）不同进行分类:
按处理的数据类型可分为 **字节流、字符流** 
> `1`字符 = `2`字节 、 `1`字节(byte) = `8`位(bit) 

- **字节流** ：每次读（写）一个`字节`，当传输的资源文件有中文时，就会出现乱码，读写的单位是`byte`，在`InputStream`/`OutputStream`中单向流动
- **字符流** ：每次读（写）两个`字节`，有中文时，使用该流就可以正确传输显示中文，读写的单位是`char`，在`Reader`/`Writer`中单向流动

按照字节的方式读取数据，一次读取`1`个字节`byte`，等同于一次读取`8`个二进制位。这种流是万能的，什么类型的文件都可以读取。包括:文本文件、图片、声音文件、视频文件。

- 例1：假设文件`file1.txt`（内容为：a中国bo张三fe），采用 **字节流** 的话是这样读的：
  + 第一次读：一个字节，正好读"a"。
  + 第二次读：一个字节，正好读到"中"字符的一半（乱码）。
  + 第三次读：一个字节，正好读到"中字符的另外一半（乱码）。  
- 例2：假设文件`file1.txt`（内容为：a中国bo张三fe），采用 **字符流** 的话是这样读的：
  + 第一次读：`'a’`字符（`'a’`字符在windows系统中占用`1`个字节。）
  + 第二次读：`'中’`字符（`'中’`字符在windows系统中占用`2`个字节。）

按照字符的方式读取数据，一次读取一个字符，这种流是为了方便读取普通文本文件而存在的，这种流不能读取：图片、声音、视频等文件。只能读取纯文本文件，连word文件都无法读取。  
**字节流和字符流的原理是相同的，只不过处理的单位不同而已。<font color="red">后缀是`Stream`是字节流，而后缀是`Reader`、`Writer`是字符流。</font>**

**为什么要有字符流？**  
- Java中的字符是采用`Unicode`标准，在`Unicode` 编码中，一个英文为`1`个字节，一个中文为`2`个字节。  
但是由于编码不同，中文字符占的字节数不一样，在`UTF-8`编码中，一个中文字符是`3`个字节。
- 如果统一使用字节流处理中文，因为读写是一个字节一个字节，这样就会对中文字符有影响，就会出现乱码。
- 为了更方便地处理中文字符，Java就推出了字符流。

**字节流和字符流的其他区别：**
- 字节流一般用来处理图像、视频、音频、PPT、Word等类型的文件。字符流一般用于处理纯文本类型的文件，如TXT文件等，但不能处理图像视频等非文本文件。
- 字节流本身没有`缓冲区`，因此 **缓冲字节流** 相对于 **字节流** ，效率提升非常高。而 **字符流** 本身就带有缓冲区，因此 **缓冲字符流**相对于字符流效率提升就不是那么大了。

> 用一句话说就是：字节流可以处理一切文件，而字符流只能处理纯文本文件。

#### 2.3 按功能分
按功能不同分为 **节点流、处理流**
- 节点流：以从或向一个特定的地方（节点）读写数据。如`FileInputStream`
- 处理流：是对一个已存在的流的连接和封装，通过所封装的流的功能调用实现数据读写。如`BufferedReader`处理流的构造方法总是要带一个其他的流对象做参数。即一个流对象经过其他流的多次包装。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO流分类：节点流、处理流.png)
</center>

#### 2.4 按有无缓冲分
还有一种流是 **缓冲流** ，区别于没有缓冲的流。

由于程序和内存交互很快，而程序和磁盘交互是很慢的，这样会导致程序出现性能问题。为了减少程序与磁盘的交互，是提升程序效率，引入了 **缓冲流** 。

普通流每次只读写一个字节；而缓冲流在内存中设置一个缓存区，缓冲区先存储足够的待操作数据后，再与内存或磁盘进行交互。这样，在总数据量不变的情况下，通过提高每次交互的数据量，从而减少了交互次数，提高效率。

有缓冲的流，类名前缀是带有Buffer的，比如`BufferedInputStream`、`BufferedReader`等。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO流分类：有无缓冲区.png)
</center>

#### 2.5 按照目标设备来分
1. 一种是`网络I/O`，也就是通过网络进行数据的拉取和输出。
2. 一种是`磁盘I/O`，主要是对磁盘进行读写工作。

### 3. 网络输入操作的两个阶段
等待网络数据到达网卡→把数据读取到内核缓冲区。
从内核缓冲区复制数据到进程空间。

### 4. 用户空间和内核空间
通常`用户进程`中的一个完整IO分为两阶段： **用户进程空间<-->内核空间** 、 **内核空间<- ->设备空间(磁盘、网络等)** 。

虚拟内存被操作系统划分成两块：`内核空间`和`用户空间`。
- 为了安全，它们是隔离的，因此即使用户的程序崩溃了，内核也不会受影响。
- 内核空间是内核代码运行的地方，用户空间是用户程序代码运行的地方。
- 当进程运行在内核空间时就处于 **内核态** ，当进程运行在用户空间时就处于 **用户态** 。

### 5. 同步和异步
由于`CPU`和`内存`的速度远远高于外设的速度，所以在`IO`编程中，就存在速度严重不匹配的问题。
- **同步请求** ：`A`调用`B`，`B`的处理是同步时，在处理完之前他不会通知`A`，只有处理完之后才会明确的通知`A`。
- **异步请求** ：`A`调用`B`，`B`的处理是异步时，`B`在接到请求后先告诉`A`我已经接到请求了，然后再去处理，处理完之后通过回调等方式再通知`A`获取处理结果。

**同步** 和 **异步** 最大的区别就是被调用方的执行方式和返回时机。同步指的是被调用方做完事情之后再返回，异步指的是被调用方先返回，然后再做事情，做完之后再想办法通知调用方。

### 6. 阻塞和非阻塞
- **阻塞请求** ：`A`调用`B`，`A`一直等着`B`的返回，别的事情什么也不干。  
- **非阻塞请求** ：`A`调用`B`，`A`不用一直等着`B`的返回，先去忙别的事情了。

阻塞和非阻塞最大的区别就是在被调用方返回结果之前的这段时间内，调用方是否一直等待。阻塞指的是调用方一直等待别的事情什么都不做；非阻塞指的是调用方先去忙别的事情。
> `I/O` 大致分为两个过程：
> 1. 数据准备的过程
> 2. 数据从`内核空间`拷贝到`用户进程（用户进程缓冲区）`的过程

**<font color="red">根据上面两个步骤的实现细节不同，IO操作可以进一步细分为下面五种</font>**

## 二、五种IO模型
### 前言
**从TCP发送数据的流程说起**

要深入的理解各种IO模型，那么必须先了解下产生各种IO的原因是什么，要知道这其中的本质问题那么就必须要直到一条消息是如何从一个程序发送到另外一个程序的；

以两个应用程序通讯为例，当`"应用A"`向`"应用B"` 发送一条消息，简单来说会经过如下流程：
1. **第一步：** `应用A`把消息发送到 `TCP发送缓冲区`。
2. **第二步：** `TCP发送缓冲区`再把消息发送出去，经过网络传递后，消息会发送到`B服务器`的`TCP接收缓冲区`。
3. **第三步：** `应用B`再从`TCP接收缓冲区`去读取属于自己的数据。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型前言：TCP发送数据简易流程.png)
</center>

根据上图基本上了解消息发送要经过 `应用A`、`应用A对应服务器的TCP发送缓冲区`、经过网络传输后消息发送到了`应用B对应服务器TCP接收缓冲区`、然后最终`应用B`读取到消息。

理解了上面的消息发送流程之后，接下来开始进入5种IO模型的主题；

**<font color="red">5种IO模型分别是：`阻塞IO模型`、`非阻塞IO模型`、`IO复用模型`、`信号驱动IO模型`、`异步IO模型`。</font>**

### 1. 阻塞IO模型
把关注点切换到上面图中的 **第3步** ，也就是`应用B`从`应用B对应服务器TCP接收缓冲区`中读取数据。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型前言：TCP发送数据简易流程第3步.png)
</center>

**思考两个问题：**
1. 因为应用之间发送消息是间断性的，也就是说在上图中`应用B对应服务器TCP接收缓冲区`还没有接收到属于`应用B`该读取的消息时，那么此时`应用B`向`应用B对应服务器TCP接收缓冲区`发起读取申请，`应用B对应服务器TCP接收缓冲区`是应该马上告诉`应用B` 现在没有你的数据，还是说让`应用B`在这里等着，直到有数据再把数据交给`应用B`？
2. 把这个问题应用到 **第1步** 也是一样，`应用A`在向`应用A对应服务器的TCP发送缓冲区`发送数据时，如果`应用A对应服务器的TCP发送缓冲区`已经满了，那么是告诉`应用A`现在没空间了，还是让`应用A`等待着，等`应用A对应服务器的TCP发送缓冲区`有空间了再把`应用A`的数据访拷贝到发送缓冲区?

所谓阻塞IO就是当`应用B`发起读取数据申请时，在 **内核数据** 没有准备好之前，`应用B`会一直处于等待数据状态，直到 **内核** 把数据准备好了交给`应用B`才结束。

**阻塞IO术语描述**：在应用调用`recvfrom`读取数据时，其系统调用直到数据包到达且被复制到`应用缓冲区`中或者发送错误时才返回，在此期间一直会等待，进程从调用到返回这段时间内都是被阻塞的称为 **阻塞IO** 。

**流程：**
1. 应用进程向内核发起`recvfrom`读取数据。
2. 准备数据报（应用进程被阻塞）。
3. 将数据从内核复制到应用空间（转到`内核空间`处理）。
4. 复制完成后，返回成功提示（进程获取到数据）。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型1：阻塞IO模型.png)
</center>

### 2. 非阻塞IO模型
按照上面的思路，所谓`非阻塞IO`就是当`应用B`发起读取数据申请时，如果 **内核数据** 没有准备好会即刻告诉`应用B`，不会让`应用B`在这里等待。

**非阻塞IO术语描述**：非阻塞IO是在应用调用`recvfrom`读取数据时，如果该`缓冲区`没有数据的话，就会直接返回一个`EWOULDBLOCK错误`，不会让应用一直等待中。  
即在没有数据的时候会即刻返回错误标识，那也意味着如果应用要读取数据就需要不断的调用`recvfrom`请求（直到读取到它数据要的数据为止）。

**流程：**
1. 应用进程向 **内核** 发起`recvfrom`读取数据。
2. 没有数据报准备好，即刻返回`EWOULDBLOCK错误码`。
3. 应用进程向 **内核** 发起`recvfrom`读取数据。
4. 如果 **内核** 已有数据包准备好就进行后续步骤，否则还是返回错误码。
5. 将数据从 **内核** 拷贝到 **用户空间** 。
6. 完成后，返回成功提示。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型2：非阻塞IO模型.png)
</center>

**<font color="red">⚠️注意：这种工作方式下需要不断轮询查看状态</font>**

### 3. IO复用模型
**思考一个问题：**  
在`应用B`从`应用B对应服务器TCP接收缓冲区`中读取数据这个环节（使用`非阻塞IO模型`）。  
如果在并发的环境下，可能会`N`个人向`应用B`发送消息，这种情况下`应用B`就必须创建多个线程去读取数据，每个线程都会自己调用`recvfrom`去读取数据。那么此时情况可能如下图：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型3：问题-多线程情况.png)
</center>

在并发情况下服务器很可能一瞬间会收到几十上百万的请求，在这种情况下`应用B`就需要创建几十上百万的线程去读取数据，同时又因为应用线程是不知道什么时候会有数据读取，为了保证消息能及时读取到，那么这些线程自己必须不断（轮询）的向`内核`发送`recvfrom请求`来读取数据。  
那么问题来了，这么多的线程不断调用`recvfrom`请求数据，先不说服务器能不能扛得住这么多线程，就算扛得住那么很明显这种方式太浪费资源了，线程是操作系统的宝贵资源，大量的线程用来去读取数据了，那么就意味着能做其它事情的线程就会少。

所以，有人就提出了一个思路： **能不能提供一种方式，可以由一个线程监控多个网络请求（后面将称为`fd文件描述符`，`linux`系统把所有网络请求以一个`fd`来标识），这样就可以只需要一个或几个线程就可以完成数据状态询问的操作，当有数据准备就绪之后再分配对应的线程去读取数据，这么做就可以节省出大量的线程资源出来，这个就是IO复用模型的思路。**

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型3：IO复用模型示意图.png)
</center>

正如上图，`IO复用模型`的思路就是系统提供了一种 **函数** 可以同时监控多个`fd`的操作，这个 **函数** 也就是常说到的`select`、`poll`、`epoll`函数，有了这个函数后，应用线程通过调用`复用器(select)函数`就可以同时监控多个`fd`；`select函数`监控的`fd`中只要有任何一个数据状态准备就绪了，`select函数`就会返回可读状态，这时 **询问线程** 再去通知处理数据的线程，对应线程此时再发起`recvfrom请求`去读取数据。

**IO复用模型术语描述：** 进程通过将一个或多个`fd`传递给`select`，阻塞在`select`操作上，`select`帮我们侦测多个`fd`是否准备就绪，当有`fd`准备就绪时，`select`通过 **询问线程** 返回数据 **可读状态** ，应用程序再调用`recvfrom`读取数据。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型3：IO复用模型.png)
</center>

`Linux`中`IO复用`的实现方式主要有`Select`，`Poll`和`Epoll`：
- `Select`：注册IO、阻塞扫描，监听的IO最大连接数不能多于`FD_ SIZE（1024）`。
- `Poll`：原理和Select相似，没有数量限制，但IO数量大，扫描性能下降。
- `Epoll` ：事件驱动不阻塞，`mmap`实现内核与用户空间的消息传递，数量很大，`Linux2.6`后内核支持。

**<font color="red">总结：复用IO的基本思路就是通过`select`或`poll`、`epoll` 来监控多`fd` ，来达到不必为每个`fd`创建一个对应的监控线程，从而减少线程资源创建的目的。</font>**

### 4. 信号驱动IO模型
`复用IO模型`解决了一个线程可以监控多个`fd`的问题，但是`select`是采用 **<font color="red">轮询</font>** 的方式来监控多个`fd`的，通过不断的轮询`fd`的可读状态来知道是否就可读的数据，而无脑的轮询就显得有点暴力，因为大部分情况下的轮询都是无效的。  
所以有人就想： **能不能不要我总是去问你是否数据准备就绪，而是我发出请求后等你数据准备好了就通知我，所以就衍生了`信号驱动IO模型`。**

于是`信号驱动IO模型`不是用轮询的方式去监控数据就绪状态，而是在调用`sigaction`时候建立一个`SIGIO`的信号联系；当 **内核数据** 准备好之后再通过`SIGIO`信号通知线程数据已经是准备好后的可读状态，当线程收到可读状态的信号后，此时再向内核发起`recvfrom`读取数据的请求。  
因为`信号驱动IO模型`下应用线程在发出信号监控后即可返回， **不会阻塞** ，所以这样的方式下，一个应用线程也可以同时监控多个fd。

如下图所示：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型4：信号驱动IO模型示意图.png)
</center>

**术语描述：** 首先开启套接口`信号驱动IO`功能，并通过系统调用`sigaction`执行一个信号处理函数，此时请求即刻返回；当数据准备就绪时，就生成对应进程的`SIGIO信号`，通过信号回调通知应用线程调用`recvfrom`来读取数据。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型4：信号驱动IO模型.png)
</center>

**<font color="red">总结：IO复用模型里面的`select`虽然可以监控多个`fd`了，但`select`其实现的本质上还是通过不断的轮询`fd`来监控数据状态， 由于大部分轮询请求其实都是无效的，所以信号驱动IO意在通过这种建立信号关联的方式，实现了发出请求后只需要等待数据就绪的通知即可，这样就可以避免大量无效的数据状态轮询操作。</font>**

### 5. 异步IO模型
其实经过了`IO复用模型`和`信号驱动IO模型`的优化，当前`I/O`效率有了很大的提升，但不管是`IO复用`还是`信号驱动`，读取一个数据总是要发起两阶段的请求：
1. 第一次发送`select请求`，询问数据状态是否准备好；
2. 第二次发送`recevform`请求读取数据。

**思考一个问题：**  
也许一开始就有一个疑问，明明是想读取数据，为什么非得要先发起一个`select询问`数据状态的请求，然后再发起真正的读取数据请求？能不能有一种方式，只要发送一个请求告诉内核我要读取数据，然后就什么都不管了，最后内核去帮我去完成剩下的所有事情（把数据从内核复制到用户空间）？  
于是有人设计了一种方案，应用只需要向内核发送一个`read请求`，告诉内核它要读取数据后即刻返回；内核收到请求后会建立一个信号联系，当数据准备就绪，内核会主动把数据从内核复制到用户空间；等所有操作都完成之后，内核会发起一个通知告诉应用，称这种一劳永逸的模式为`异步IO模型`。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型5：异步IO模型示意图.png)
</center>

**术语描述：** 应用告知内核启动某个操作，并让内核在整个操作完成之后通知应用。这种模型与`信号驱动模型`的主要区别在于，信号驱动IO只是由内核通知线程何时可以开始下一个IO操作，而异步IO模型是由内核通知线程操作什么时候完成。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型5：异步IO模型.png)
</center>

**<font color="red">总结：`异步IO`的优化思路是解决了应用程序需要先后发送询问请求、发送接收数据请求两个阶段的模式，在异步IO的模式下，只需要向内核发送一次请求就可以完成状态询问和数拷贝的所有操作。</font>**

注意：
此模型和前面模型最大的区别是： **前4个模型从内核空间拷贝数据这一过程是`阻塞`的，需要自己把准备好的数据，拷贝到用户空间。<font color="red">而全异步不同，异步IO是「内核数据准备好」和「数据从`内核态`拷贝到`用户态`」这两个过程都不用等待</font>** 。

**<font color="red">在`异步IO模型`下，用户线程完全不需要关心实际的整个IO操作是如何进行的，只需要先发起一个请求，当接收内核返回的成功信号时表示IO操作已经完成，可以直接去使用数据，它是最理想的模型。</font>**

### 6. 5种IO模型比较
<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/IO模型：5种IO模型比较.png)
</center>

### 7. 同步与异步、阻塞与非阻塞小结
#### 7.1 概念简述
**同步和异步**  
`同步`和`异步`是针对应用程序和内核的交互而言的。
- `同步`是指用户进程触发IO操作并 **等待** 或者 **轮询** 的去查看IO操作是否就绪。
- `异步`是指用户进程触发IO操作以后便开始做自己的事情（应用发送完指令后就不再参与这个过程了），而当IO操作已经完成的时候会得到IO完成的通知。

**阻塞和非阻塞**  
`阻塞`和`非阻塞`是针对于进程在访问数据的时候，根据IO操作的就绪状态来采取的不同方式，是一种读取或者写入操作方法的实现方式。
- 阻塞方式下读取或者写入函数将一直等待，直到获取到数据。
- 而非阻塞方式下，读取或者写入方法在未获取到数据的时候会被立即返回一个状态值，不需要一直等待。

**同步阻塞、同步非阻塞**
- 不同点：发起读取请求的时候一个请求阻塞，一个请求不阻塞。
- 相同点：是都需要应用自己监控整个数据完成的过程。

补充：为什么只有异步非阻塞而没有异步阻塞呢，因为异步模型下请求指定发送完后就即刻返回了，没有任何后续流程了，所以它注定不会阻塞，所以也就只会有异步非阻塞模型了。

**生活中的例子对照解读：**  
老张爱喝茶，需要煮开水。  
出场人物：老张，水壶两把（普通水壶，简称水壶；会响的水壶，简称响水壶）。
1. 老张把水壶放到火上，站在炉子前等水开。`（同步阻塞）`
2. 老张把水壶放到火上，去客厅看电视，时不时去厨房看看水开没有。`（同步非阻塞）`

老张还是觉得自己有点傻，于是变高端了，买了把会响笛的那种水壶。水开之后，能大声发出嘀~~~~ 的噪音。 
1. 老张把响水壶放到火上，站在炉子前等水开。`（异步阻塞）`老张觉得这样傻等意义不大
2. 老张把响水壶放到火上，去客厅看电视，水壶响之前不再去看它了，响了再去拿壶。`（异步非阻塞）`

#### 7.2 区别及使用场景
`同步IO`会`阻塞`当前的调用线程，而`异步IO`则允许发起IO请求的调用线程继续执行，等到IO请求被处理后，会通知 **调用线程** 。

> 对于异步的IO请求，其最大的好处是：慢速的IO请求相对于应用程序而言是异步执行，这样可以极大提高应用程序的处理吞吐量。
> 
> 发起IO请求的应用程序**需要关心的是IO执行完成的结果**，而不必忙等IO请求执行的过程。**它只需要提交一个IO操作，当内核执行这个IO操作时，线程可以去运行其他逻辑，也不需要定期去查看IO是否完成**，当内核完成这个IO操作后会以某种方式通知应用。
>
> 此时**应用的运行和IO执行变成了并行的关系，可以批量的进行IO操作，让设备的能力得到最大发挥**      

在`“发出IO请求”`到`“收到IO完成”`的这段时间里， **`同步IO模型`下，主线程只能挂起，但`异步IO模型`下，主线程并没有休息，而是继续处理其他任务。** 这样，在`异步IO模型`下，一个线程就可以同时处理多个IO请求，并且没有切换线程的操作。对于大多数IO密集型的应用程序，使用异步IO将大大提升系统的多任务处理能力。

> - 同步的执行效率会比较低，耗费时间，但 **有利于对流程进行控制** ，避免很多不可掌控的意外情况；
> - 异步的执行效率高，节省时间，但是会占用更多的资源，也 **不利于对进程进行控制** 。

**同步IO的优点** 
1. 同步流程对结果处理通常更为简单，可以就近处理。
2. 同步流程对结果的处理始终和前文保持在一个上下文内。
3. 同步流程可以很容易捕获、处理异常。
4. 同步流程是最天然的控制过程顺序执行的方式。

**异步IO的优点**
1. 异步流程可以立即给调用方返回初步的结果。
2. 异步流程可以延迟给调用方最终的结果数据，在此期间可以做更多额外的工作，例如结果记录等等。
3. 异步流程在执行的过程中，可以释放占用的线程等资源，避免阻塞，等到结果产生再重新获取线程处理。
4. 异步流程可以等多次调用的结果出来后，再统一返回一次结果集合，提高响应效率。

**异步IO使用场景**
1. 不涉及共享资源，或对共享资源只读，即非互斥操作
2. 没有时序上的严格关系
3. 不需要原子操作，或可以通过其他方式控制原子性
4. 常用于IO操作等耗时操作，因为比较影响客户体验和使用性能
5. 不影响主线程逻辑 

## 三、NIO简述
### 1. 概念
**NIO** (New lO)也有人称之为`java non-blocking lO`是从Java 1.4版本开始引入的一个新的IO [API](https://so.csdn.net/so/search?q=API&spm=1001.2101.3001.7020)，可以替代标准的`Java lO API`。在`Java API`中提供了 **两套NIO** ：一套是针对 **标准输入输出NIO** ，另一套就是 **网络编程NIO** 。

`NIO`与原来的`IO`有同样的作用和目的，但是使用的方式完全不同： **NIO支持面向缓冲区的、基于通道的IO操作** 。  
`NIO`将以更加高效的方式进行文件的读写操作。**NIO可以理解为非阻塞IO**，传统的IO的`read`和`write`只能阻塞执行，线程在读写IO期间不能干其他事情，比如调用`socket.read()`时，如果服务器一直没有数据传输过来，线程就一直阻塞，而`NIO`中可以配置`socket`为非阻塞模式。

- `NIO`相关类都被放在`java.nio`包及子包下，并且对原`java.io`包中的很多类进行改写。
- `NIO`有三大 **核心** 部分：`Channel(通道)`，`Buffer(缓冲区)`， `Selector(选择器)` 。
- `NlO`的非阻塞模式，使一个线程从某通道发送请求或者读取数据，但是它仅能得到目前可用的数据，如果目前没有数据可用时，就什么都不会获取，而不是保持线程阻塞，所以直至数据变的可以读取之前，该线程可以继续做其他的事情。  
  非阻塞写也是如此，一个线程请求写入一些数据到某通道，但不需要等待它完全写入，这个线程同时可以去做别的事情。
- **通俗理解：`NIO`是可以做到用一个线程来处理多个操作的。** 假设有`1000`个请求过来,根据实际情况，可以分配`20`或者`80`个线程来处理。不像之前的`阻塞IO`那样，非得分配`1000`个。

### 2. NIO三大核心
`NIO`有三大核心部分: **`Channel(通道)`，`Buffer(缓冲区)`，`Selector(选择器)`**

- **Buffer(缓冲区)**  
缓冲区本质上是一块可以写入数据，然后可以从中读取数据的内存。这块内存被包装成`NIO Buffer`对象，并提供了一组方法，用来方便的访问该块内存。 **相比较直接对数组的操作，`Buffer APl`更加容易操作和管理。**
- **Channel(通道)**  
NIO的通道类似流，但又有些不同：既可以从通道中读取数据，又可以写数据到通道。但流的(`input`或`output`)读写通常是单向的。  
通道可以非阻塞读取和写入通道，通道可以支持 **读取** 或 **写入** 缓冲区，也支持 **异步地读写** 。
- **Selector(选择器)**  
Selector是一个`NIO组件`，可以能够检查 **一个** 或 **多个** `NIO通道`，并确定哪些通道已经准备好进行读取或写入。这样，一个单独的线程可以管理多个`channel`，从而管理多个网络连接，提高效率。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/NIO三大组件关系示意图.png)
</center>

- 一个线程对应`Selector`，一个`Selector`对应多个`Channel`，每个`Channel`都会对应一个 `Buffer`
- 切换到哪个`Channel`是由事件决定的，`Selector` 会根据不同的事件，在各个通道上切换
- `Buffer` 是一个内存块，底层是一个 **数组** 
- 数据的 **读取写入** 是通过 `Buffer`完成的。`普通lO`中要么是输入流或输出流，不能双向，而`NIO`的`Buffer`是可以读也可以写，双向的。
- NIO的核心在于:`通道(Channel)`和`缓冲区(Buffer)`。通道表示打开到`lO`设备(例如:文件、套接字)的连接。若需要使用NIO，则需要获取用于连接IO设备的`通道`以及用于容纳数据的`缓冲区`。然后操作缓冲区，对数据进行处理。 **<font color="red">简而言之，Channel负责传输，Buffer负责存取数据</font>**。

#### 2.1 缓冲区 (Buffer)
**`缓冲区（Buffer）`** 一个用于特定基本数据类型的容器。由 `java.nio` 包定义的，所有缓冲区都是 `Buffer抽象类` 的子类。`Java NIO` 中的 `Buffer` 主要用于与 `NIO通道`进行交互，数据是从通道读入缓冲区，从缓冲区写入通道中的。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/NIO三大核心-Buffer示意图.png)
</center>

##### 2.1.1 缓冲区类型
缓冲区底层是 **数组** ，用于存储不同类型的数据。根据数据类型的不同，提供不同的缓冲区：
- ByteBuffer
- CharBuffer
- ShortBuffer
- IntBuffer
- LongBuffer
- FloatBuffer
- DoubleBuffer

##### 2.1.2  缓冲区的核心属性
```java
public abstract class Buffer {
	// ......
    // Invariants: mark <= position <= limit <= capacity
    private int mark = -1;
    private int position = 0;
    private int limit;
    private int capacity;
    
    // ......
}
```

- **`容量 (capacity) `：** 作为一个内存块，Buffer具有一定的固定大小， 也称为"容量"，缓冲区容量不能为负，并且创建后不能更改。
- **`限制 (limit)`：** 表示缓冲区中可以操作数据的大小（`limit`后数据不能进行读写）。缓冲区的限制不能为负，并且不能大于其容量。 写入模式下，限制等于 `Buffer`的容量。读取模式下，`limit`等于写入的数据量。
- **`位置 (position)`：** 下一个要读取或写入的数据的索引。 缓冲区的位置不能为负，并且不能大于其限制。
- **`标记 (mark)属性`与`重置 (reset)方法`：** 标记是一个索引， 通过 `Buffer` 中的 `mark()方法` 指定 `Buffer` 中一个 特定的`position`（即：设定`mark=position`），之后可以通过调用 `reset()方法`恢复到这个`position`。注意：标记在设定前是未定义的(`undefined`)。  
  `reset()方法`定义如下：
  ```java
  /**
   * Resets this buffer's position to the previously-marked position.
   *
   * <p> Invoking this method neither changes nor discards the mark's
   * value. </p>
   *
   * @return  This buffer
   * @throws  InvalidMarkException
   *          If the mark has not been set
   */
  public final Buffer reset() {
      int m = mark;
      if (m < 0)
          throw new InvalidMarkException();
      position = m;
      return this;
  }
  ```

**四个属性值的大小遵守以下不变式关系:**
```java
0 <= mark <= position <= limit <= capacity
```

如：
```java
// 创建一个ByteBuffer，容量为10
ByteBuffer byteBuffer = ByteBuffer.allocate(10);
```
`位置(position)`被设为`0`，而且`容量(capacity)`和`界限(limit)`被设为`10`，刚好经过缓冲区能够容纳的最后一个字节，其中标记(mark)最初未定义。容量是固定的，但另外的三个属性可以在使用缓冲区时改变。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/NIO三大核心-Buffer缓冲区核心属性之间的关系示意图.png)
</center>

##### 2.1.3  缓冲区常用方法及代码示例
**Buffer常见方法：**
1. **Buffer clear()：** 清空缓冲区并返回对缓冲区的引用。
2. **Buffer flip()：** 为将缓冲区的界限设置为当前位置，并将当前·重置为 `0`。
3. **int capacity()：** 返回Buffer的容量大小。
4. **boolean hasRemaining()：** 判断缓冲区中是否还有元素。
5. **int limit()：** 返回Buffer的界限的位置。
6. **Buffer limit(int n)** 将设置缓冲区界限为 n, 并返回一个具有新 limit 的缓冲区对象。
7. **Buffer mark()：** 对缓冲区设置标记。
8. **int position()：** 返回缓冲区的当前位置 position。
9. **Buffer position(int n)：** 将设置缓冲区的当前位置为 n， 并返回修改后的 Buffer 对象。
10. **int remaining()：** 返回 position 和 limit 之间的元素个数。
11. **Buffer reset()：** 将位置 position 转到以前设置的mark 所在的位置。
12. **Buffer rewind()：** 将位置设为为 0， 取消设置的mark。

**缓冲区的数据操作 Buffer 所有子类提供了两个用于数据操作的方法：**
1. **get()：** 读取单个字节。
2. **get(byte[] dst)：** 批量读取多个字节到dst变量中。
3. **get(int index)：** 读取指定索引位置的字节（不会移动 position）放到入数据到Buffer中。
4. **put(byte b)：** 将给定单个字节写入缓冲区的当前位置。
5. **put(byte[] src)：** 将 `src` 中的字节写入缓冲区的当前位置。
6. **put(int index, byte b)：** 将指定字节写入缓冲区的索引位置(不会移动 position)。

**使用Buffer读写数据一般遵循以下四个步骤：**
1. 写入数据到`Buffer`；
2. 调用`flip()方法`，转换为读取模式；
3. 从`Buffer`中读取数据；
4. 调用`buffer.clear()方法`或者`buffer.compact()方法`清除缓冲区。

部分常用方法演示代码：
```java
/**
 * Buffer测试类
 */
public class TestBuffer {
   public static void main(String[] args) {
      test1();
      test2();
      test3();
   }
   public static void test1(){
      //1. 分配一个指定大小的缓冲区
      ByteBuffer buf = ByteBuffer.allocate(1024);
      System.out.println("-----------------allocate()----------------");
      System.out.println(buf.position());// 0: 表示当前的位置为0
      System.out.println(buf.limit());// 1024: 表示界限为1024，前1024个位置是允许读写的
      System.out.println(buf.capacity());//1024：表示容量大小为1024

      //2. 利用 put() 存入数据到缓冲区中
      System.out.println("-----------------put()----------------");
      String str = "itheima";
      buf.put(str.getBytes());
      System.out.println(buf.position());// 7表示下一个可以写入的位置是7,因为写入的字节是7个,从0开始已经写了7个，位置为8的position为7
      System.out.println(buf.limit());// 1024：表示界限为1024，前1024个位置是允许读写的
      System.out.println(buf.capacity());//1024：表示容量大小为1024

      //3. 切换读取数据模式
      System.out.println("-----------------flip()----------------");
      buf.flip();
      System.out.println(buf.position());// 0: 读取的起始位置为0
      System.out.println(buf.limit());// 7: 表示界限为7，前7个位置有数据可以读取
      System.out.println(buf.capacity());// 1024:表示容量大小为1024

      //4. 利用 get() 读取缓冲区中的数据
      System.out.println("-----------------get()----------------");
      byte[] dst = new byte[buf.limit()];//创建一个界限为limit大小的字节数组
      buf.get(dst);//批量将limit大小的字节写入到dst字节数组中
      System.out.println(new String(dst, 0, dst.length));//结果为itheima

      System.out.println(buf.position());//7: 读取的位置变为7,因为前面的7个字节数据已经全部读取出去,下一个可读取的位置为7，从0开始的
      System.out.println(buf.limit());//7: 可读取的界限大小为7
      System.out.println(buf.capacity());// 1024: 表示容量大小为1024

      //5. rewind() : 可重复读
      System.out.println("-----------------rewind()----------------");
      buf.rewind();// 将位置设为为 0,从头开始读取
      System.out.println(buf.position());// 0
      System.out.println(buf.limit());// 7
      System.out.println(buf.capacity());// 1024

      //6. clear() : 清空缓冲区. 但是缓冲区中的数据依然存在，但是处于“被遗忘”状态
      System.out.println("-----------------clear()----------------");
      buf.clear();
      System.out.println(buf.position());// 0
      System.out.println(buf.limit());// 1024
      System.out.println(buf.capacity());// 1024
      System.out.println((char)buf.get());//i

   }

   public static void test2(){
      String str = "itheima";
      ByteBuffer buf = ByteBuffer.allocate(1024);

      buf.put(str.getBytes());// 将str写入到buf缓冲区中
      buf.flip();//转换为读模式

      byte[] dst = new byte[buf.limit()];//定义一个字节数组
      buf.get(dst, 0, 2);//将前2个字节批量写入到dst字节数组中
      System.out.println(new String(dst, 0, 2));//打印结果为it
      System.out.println(buf.position());//当前下一个读取的位置为2

      //mark() : 标记
      buf.mark();

      buf.get(dst, 2, 2);//从第3个位置开始将2个字节批量写入到dst字节数组中
      System.out.println(new String(dst, 2, 2));//打印结果为he
      System.out.println(buf.position());// 当前下一个读取的位置为4

      //reset() : 恢复到 mark 的位置
      buf.reset();
      System.out.println(buf.position());// 2

      //判断缓冲区中是否还有剩余数据
      if(buf.hasRemaining()){
         //获取缓冲区中可以操作的数量
         System.out.println(buf.remaining());// 5: 返回 position 和 limit 之间的元素个数
      }
   }

   public static void test3(){
      //分配直接缓冲区
      ByteBuffer buf = ByteBuffer.allocateDirect(1024);
      System.out.println(buf.isDirect());
   }
}
```

##### 2.1.4 直接缓冲区\非直接缓冲区
`Buffer`可以是两种类型：
- 另一种是**非直接内存（也就是堆内存）**。
  而 **非直接内存，也就是堆内存中的数据，如果要作IO操作，需要先从本进程内存复制到直接内存** ，再利用本地IO处理。通过`allocation()方法`分配缓冲区，将缓冲区建立在`JVM`内存中（即 **传统IO** ）。  
  作用链是： **`本地IO`-->`直接内存`-->`非直接内存`-->`直接内存`-->`本地IO`**
- 一种是基于 **直接内存（也就是非堆内存）** 。
  对于 **直接内存来说，`JVM`将会在IO操作上具有更高的性能，因为它直接作用于本地系统内存的IO操作** 。通过`allocationDirect()方法`直接分配缓冲区，将缓冲区建立在物理内存（直接内存区域）中（即 **NIO** ）。  
  作用链是： **`本地IO`-->`直接内存`-->`本地IO`**

很明显，在做IO处理时， **<font color="red">比如网络发送大量数据时，直接内存会具有更高的效率。直接内存使用`allocateDirect()方法`创建，但是它比申请普通的堆内存需要耗费更高的性能。不过，这部分的数据是在JVM之外的，因此它不会占用应用的内存。所以当有很大的数据要缓存，并且它的生命周期又很长，那么就比较适合使用直接内存。</font>**

**只是一般来说，如果不是能带来很明显的性能提升，还是推荐使用堆内存（非直接内存）。其中`字节缓冲区`是`直接缓冲区`还是`非直接缓冲区`可通过调用其 `isDirect()方法`来确定**。

**直接缓冲区使用场景：**
1. 有很大的数据需要存储，它的生命周期又很长。
2. 适合**频繁** 的IO操作，比如网络并发场景。

`直接缓冲区`与`非直接缓冲区`示意图：

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/非直接缓冲区.png)
</br>
</br>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/直接缓冲区.png)
</center>

#### 2.2 通道(Chanel)
##### 2.1.1 概述
`通道（Channel）`：由 `java.nio.channels包`定义的。`Channel`表示 **IO源** 与 **目标** 打开的连接，类似于传统的`“流”`。只不过 **<font color="red">`Channel`本身不能直接访问数据</font>** ，只能与 `Buffer` 进行交互。

`NIO` 的通道类似于流，但有些区别如下：
- `通道`可以同时进行读写，而`流`只能读或者只能写。
- `通道`可以实现异步读写数据。
- `通道`可以从缓冲读数据，也可以写数据到缓冲。

**⚠️注意：IO中的`stream(流)`是单向的，例如 `FileInputStream` 对象只能进行读取数据的操作；而 `NIO` 中的`通道(Channel)`是双向的，可以读操作，也可以写操作。**

##### 2.1.2 Channel 接口及实现类
`Channel`是一个`接口`，在`java.nio.channels包`中定义。
```java
public interface Channel extends Closeable{}
```

**常用的Channel实现类：**
- `FileChannel`：用于 **读取** 、 **写入** 、 **映射** 和 **操作** 文件的通道。
- `DatagramChannel`：通过 `UDP` 读写网络中的数据通道。
- `SocketChannel`：通过 `TCP` 读写网络中的数据（类似 `Socket`）。
- `ServerSocketChannel`：可以监听新进来的 `TCP` 连接，对每一个新进来的连接都会创建一个 `SocketChannel`（类似 `ServerSocket`）。

##### 2.1.3 获取通道的方式
**方式一：对支持通道的对象调用`getChannel()`方法。支持通道的类如下：**
- FileInputStream
- FileOutputStream
- RandomAccessFile
- DatagramSocket
- Socket
- ServerSocket
  ```java
  RandomAccessFile aFile = new RandomAccessFile("data/nio-data.txt", "rw");
  FileChannel inChannel = aFile.getChannel();
  ```

**方式二：使用 `Files` 类的静态方法 `newByteChannel()` 获取字节通道。**
```java
// public static SeekableByteChannel newByteChannel(Path path, OpenOption... options)
ByteChannel inputStream = Files.newByteChannel(Paths.get(""), StandardOpenOption.CREATE_NEW);
```
参数解释：
- **Path参数：**  
是用来取代`File`的，`Path`用于来表示文件路径和文件。可以有多种方法来构造一个`Path`对象来表示一个文件路径，或者一个文件
- **OpenOption参数：**  
`StandardOpenOptions`指定如何打开文件的选项，支持的枚举如下：
  + `WRITE` - 打开文件以进行写访问。
  + `APPEND` - 将新数据附加到文件的末尾。该选项用于`WRITE`或`CREATE`选项。
  + `TRUNCATE_EXISTING` - 将文件截断为零字节。该选项与`WRITE`选项一起使用。
  + `CREATE_NEW` - 创建一个新文件，如果文件已经存在，则会引发异常。
  + `CREATE` - 如果文件存在，打开文件，如果没有，则创建一个新文件。
  + `DELETE_ON_CLOSE` - 流关闭时删除文件。此选项对临时文件很有用。
  + `SPARSE` - 提示新创建的文件将是稀疏的。这种高级选项常用在某些文件系统（例如NTFS），其中具有据 **“间隙”** 的大型文件可以以更有效的方式存储，因为这些空隙不占用磁盘空间。
  + `SYNC` - 保持与底层存储设备同步的文件（内容和元数据）。
  + `DSYNC` - 保持与底层存储设备同步的文件内容。

**方式三：通过通道的静态方法 `open()` 打开并返回指定通道。**  
如：`SocketChannel.open();`
```java
public void openSocket(){
    try {
        // 1、打开一个套接字通道
        SocketChannel sc = SocketChannel.open();
        // 根据主机名和端口号创建套接字地址
        InetSocketAddress socketAddress = new InetSocketAddress("192.168.1.102",8080);
        // 连接套接字
        sc.connect(socketAddress);

        // 2、打开一个server-socket通道
        ServerSocketChannel ssc = ServerSocketChannel.open();
        ssc.socket().bind(new InetSocketAddress(8080));

        // 3、打开一个datagram通道
        DatagramChannel dc = DatagramChannel.open();
        RandomAccessFile raf = new RandomAccessFile("/usr/local/swk/dump.txt", "r");
        FileChannel fc = raf.getChannel();

    } catch (IOException e) {
        e.printStackTrace();
    }
}
```

##### 2.1.4 FileChannel类常用方法（文件操作通道）
FileChannel用于读取、写入、映射和操作文件的通道。
- **`int read(ByteBuffer dst)`：** 从Channel中将 **读取** 数据到ByteBuffer。
- **`long read(ByteBuffer[] dsts)`：** 将Channel中的数据 **“分散”** 到ByteBuffer[]。
- **`int write(ByteBuffer src)`：** 将ByteBuffer中的数据 **写入** 到Channel。
- **`long write(ByteBuffer[] srcs)`：** 将ByteBuffer[] 到中的数据 **“聚集”** 到Channel。
- **`long position()`：** 返回此通道的文件位置。
- **`FileChannel position(long p)`：** 设置此通道的文件位置。
- **`long size()`：** 返回此通道的文件的当前大小。
- **`FileChannel truncate(long s)`：** 将此通道的文件截取为给定大小。
- **`void force(boolean metaData)`：** 强制将所有对此通道的文件更新写入到存储设备中。

##### 2.1.5 FileChannel类代码示例
**本地文件写数据：**
```java
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;

/***
 * 需求：使用ByteBuffer(缓冲)和 FileChannel(通道)， 将数据写入到 data.txt 中.
 */
public class ChannelTest {
    public static void main(String[] args) {
        write();
    }

    public static void write() {
        try {
            // 1、字节输出流通向目标文件
            FileOutputStream fos = new FileOutputStream("F:\\data.txt");
            // 2、得到字节输出流对应的通道Channel
            FileChannel channel = fos.getChannel();
            // 3、分配缓冲区
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            for (int i = 0; i < 10; i++) {
                buffer.clear();//清空缓冲区
                buffer.put(("hello，使用Buffer和channel实现写数据到文件中" + i + "\r\n").getBytes());// 循环写入10条数据
                // 4、把缓冲区切换成写出模式
                buffer.flip();
                channel.write(buffer);//将缓冲区的数据写入到文件通道
            }
            channel.close();
            System.out.println("写数据到文件中！");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

**本地文件读数据：**
```java
import java.io.FileInputStream;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.Charset;

/**
 * 需求：设置两个缓冲区，一大一小，大的缓冲区为每次读取的量，小的缓冲区存放每行的数据（确保大小可存放文本中最长的那行）。
 *
 * 读取的时候判断是不是换行符13或回车10，是的话则返回一行数据，不是的话继续读取，直到读完文件。
 */
public class ChannelTest {
    public static void main(String[] args) throws Exception {
        read();
    }

    public static void read() throws Exception {
        // 1、定义一个文件字节输入流与源文件接通
        FileInputStream is = new FileInputStream("F:\\data.txt");
        // 2、需要得到文件字节输入流的文件通道
        FileChannel channel = is.getChannel();
        // 3、定义两个缓冲区
        ByteBuffer buffer = ByteBuffer.allocate(1024 * 1024);
        ByteBuffer bb = ByteBuffer.allocate(2);// data.txt中的每一行字符是33个，因此设置较小的值方便测试扩容方法

        // 4、读取数据到缓冲区
        int bytesRead = channel.read(buffer);
        while (bytesRead != -1) {
            buffer.flip();// 切换模式，写->读
            while (buffer.hasRemaining()) {//返回 position 和 limit 之间的元素个数
                byte b = buffer.get();
                if (b == 10 || b == 13) { // 换行或回车
                    bb.flip();
                    // 这里就是一个行
                    final String line = Charset.forName("utf-8").decode(bb).toString();
                    System.out.println(line);// 解码已经读到的一行所对应的字节
                    bb.clear();
                } else {
                    if (bb.hasRemaining())
                        bb.put(b);
                    else { // 空间不够扩容
                        bb = reAllocate(bb);
                        System.out.println("扩容后的容量：" + bb.capacity());
                        bb.put(b);
                    }
                }
            }
            buffer.clear();// 清空,position位置为0，limit=capacity
            //  继续往buffer中写
            bytesRead = channel.read(buffer);
        }
        channel.close();
    }

    /**
     * ByteBuffer扩容：每次扩容为之前的2倍
     */
    public static ByteBuffer reAllocate(ByteBuffer original) {
        // 扩容为原始的2倍
        int afterCapacity = original.capacity() * 2;

        // 创建与原始类型相同的克隆缓冲
        final ByteBuffer clone = (original.isDirect()) ? // 判断此字节缓冲区是否是直接缓冲
            ByteBuffer.allocateDirect(afterCapacity) :// 创建直接缓冲区
        	ByteBuffer.allocate(afterCapacity);// 创建非直接缓冲流区

        // 创建原始文件的只读副本。这样可以在不修改原缓冲的情况下读取缓冲
        final ByteBuffer readOnlyCopy = original.asReadOnlyBuffer();

        // 读取并写入原文到扩容后的缓冲中
        readOnlyCopy.flip();
        clone.put(readOnlyCopy);

        return clone;
    }
}
```

执行结果：
```
扩容后的容量：4
扩容后的容量：8
扩容后的容量：16
扩容后的容量：32
扩容后的容量：64
hello，使用Buffer和channel实现写数据到文件中0

hello，使用Buffer和channel实现写数据到文件中1

hello，使用Buffer和channel实现写数据到文件中2

hello，使用Buffer和channel实现写数据到文件中3

hello，使用Buffer和channel实现写数据到文件中4

hello，使用Buffer和channel实现写数据到文件中5

hello，使用Buffer和channel实现写数据到文件中6

hello，使用Buffer和channel实现写数据到文件中7

hello，使用Buffer和channel实现写数据到文件中8

hello，使用Buffer和channel实现写数据到文件中9
```

**使用`Buffer`完成文件复制：**
```java
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;

/***
 * 需求：使用 FileChannel(通道) ，完成文件的拷贝。
 */
public class ChannelTest {
    public static void main(String[] args) throws Exception {
        copy();
    }

    public static void copy() throws Exception {
        // 源文件
        File srcFile = new File("F:\\data.txt");
        File destFile = new File("F:\\data_copy.txt");
        // 得到一个字节字节输入流
        FileInputStream fis = new FileInputStream(srcFile);
        // 得到一个字节输出流
        FileOutputStream fos = new FileOutputStream(destFile);
        
        // 得到的是文件通道
        FileChannel isChannel = fis.getChannel();
        FileChannel osChannel = fos.getChannel();

        // 分配缓冲区
        ByteBuffer buffer = ByteBuffer.allocate(1024);
        while (isChannel.read(buffer) > 0) {
            // 已经读取了数据 ，把缓冲区的模式切换成可读模式
            buffer.flip();
            // 把数据写出到
            osChannel.write(buffer);//将buffer缓冲区中的数据写入到osChannel中
            // 必须先清空缓冲然后再写入数据到缓冲区
            buffer.clear();
        }
        isChannel.close();
        osChannel.close();
        System.out.println("复制完成！");
    }
}
```

**`分散 (Scatter) `和`聚集 (Gather)`：**
- **分散读取（Scatter ）:** 是指将`Channel通道`的数据 **读入** 到 **多个缓冲区** 中去
- **聚集写入（Gathering ）：** 是指将 **多个Buffer** 中的数据 **“聚集”** 到 `Channel通道` 中。

注：下面的演示代码中`test1.txt`的文本数据为单行`0123456789`。（10个字符）
```java
public class ChannelTest {
    public static void main(String[] args) throws Exception {
        scatterAndGathering();
    }

    //分散和聚集
    public static  void scatterAndGathering () throws IOException {
        /**
         * “r”：仅供阅读。调用结果对象的任何写入方法都会引发IOException。
         * “rw”：开放阅读和写作。如果文件不存在，则将尝试创建它。
         * “rws”：与“rw”一样，开放读写，并且还要求对文件内容或元数据的每次更新都同步写入底层存储设备。
         * “rwd”：与“rw”一样，可读取和写入，并且还要求对文件内容的每次更新都同步写入底层存储设备。
         */
        RandomAccessFile raf1 = new RandomAccessFile("F:\\test1.txt", "rw");
        //1. 获取通道
        FileChannel channel1 = raf1.getChannel();

        //2. 分配指定大小的缓冲区
        ByteBuffer buf1 = ByteBuffer.allocate(8);// 分配8个是因为test1.txt中一共10个字符，便于截取测试
        ByteBuffer buf2 = ByteBuffer.allocate(8);

        //3. 分散读取
        ByteBuffer[] bufs = {buf1, buf2};
        channel1.read(bufs);

        for (ByteBuffer byteBuffer : bufs) {
            byteBuffer.flip();
        }

        System.out.println(new String(bufs[0].array(), 0, bufs[0].limit()));
        System.out.println("-----------------");
        System.out.println(new String(bufs[1].array(), 0, bufs[1].limit()));

        //4. 聚集写入
        RandomAccessFile raf2 = new RandomAccessFile("F:\\test2.txt", "rw");
        FileChannel channel2 = raf2.getChannel();

        channel2.write(bufs);
    }
}
```

#### 2.3 选择器(Selector)
##### 2.3.1 概述
`选择器（Selector)`是 `SelectableChannle对象`的 **多路复用器** ，Selector可以 **同时监控多个** `SelectableChannel`的IO状况，因此利用Selector可使 **一个单独的线程管理多个`Channel`** 。 <font color="red">Selector是非阻塞IO的核心。</font>
- **Java 的 NIO，用非阻塞的IO方式。** 可以用一个线程，处理多个的客户端连接，就会使用到 `Selector(选择器)`。
- Selector 能够检测多个注册的通道上是否有 **事件** 发生（注意：多个 `Channel` 以 **事件** 的方式可以注册到同一个`Selector(选择器)`)上。如果有 **事件** 发生，便获取 **事件** 然后针对每个 **事件** 进行相应的处理。这样就可以只用一个单线程去管理多个通道，也就是管理多个连接和请求。
- 只有在`连接/通道`真正有 **读写事件** 发生时，才会进行读写，就大大地减少了系统开销；并且不必为每个连接都创建一个线程，也就不用去维护多个线程，从而避免了多线程之间的上下文切换导致的开销。

**Selector 示意图和特点说明：**  
**Selector可以实现：** `1`个`I/O线程`可以并发处理 `N` 个客户端连接和读写操作，这从根本上解决了`传统同步阻塞I/O` 一个线程管理一个连接的模型，从而使架构的性能、弹性伸缩能力和可靠性都得到了极大的提升。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/NIO三大组件关系示意图.png)
</center>

##### 2.3.2 选择器的应用
**创建Selector** ：通过调用 `Selector.open()` 方法创建一个 `Selector`。
```java
Selector selector = Selector.open();
```

向选择器注册通道：`SelectableChannel.register(Selector sel, int ops)`
```java
//1. 获取通道
ServerSocketChannel ssChannel = ServerSocketChannel.open();
//2. 切换非阻塞模式
ssChannel.configureBlocking(false);
//3. 绑定连接
ssChannel.bind(new InetSocketAddress(9898));
//4. 获取选择器
Selector selector = Selector.open();
//5. 将通道注册到选择器上, 并且指定“监听接收事件”
ssChannel.register(selector, SelectionKey.OP_ACCEPT);
```

当调用 `register(Selector sel, int ops)` 将通道注册选择器时，选择器对通道的监听事件，需要通过第二个参数 `ops` 指定。可以监听的事件类型（可使用 `SelectionKey` 的四个常量表示）：
- **读 :` SelectionKey.OP_READ （1）`**
- **写 : `SelectionKey.OP_WRITE （4）`**
- **连接 : `SelectionKey.OP_CONNECT （8）`**
- **接收 : `SelectionKey.OP_ACCEPT （16）`**

若注册时不止监听一个事件，则可以使用 **`“位或”`** 操作符连接。
```java
// 同时监听读和写的事件
int interestSet = SelectionKey.OP_READ|SelectionKey.OP_WRITE
```

##### 2.3.3 服务端流程
**1)、获取通道。当客户端连接服务端时，服务端会通过 `ServerSocketChannel` 得到 `SocketChannel`：**
```java
 ServerSocketChannel ssChannel = ServerSocketChannel.open();
```

**2)、切换非阻塞模式**
```java
 ssChannel.configureBlocking(false);
```

**3)、绑定连接**
```java
 ssChannel.bind(new InetSocketAddress(8888));
```

**4)、获取选择器**
```java
Selector selector = Selector.open();
```

**5)、将通道注册到选择器上, 并且指定“监听接收事件”**
```java
ssChannel.register(selector, SelectionKey.OP_ACCEPT);
```

**6)、轮询式的获取选择器上已经“准备就绪”的事件**
```java
while (selector.select() > 0) {
    System.out.println("开启事件处理");
    //7.获取选择器中所有注册的通道中已准备好的事件
    Iterator<SelectionKey> it = selector.selectedKeys().iterator();
    //8.开始遍历事件
    while (it.hasNext()){
        SelectionKey selectionKey = it.next();
        System.out.println("--->" + selectionKey);
        //9.判断这个事件具体是什么
        if (selectionKey.isAcceptable()) {
            //10.获取当前接入事件的客户端通道
            SocketChannel socketChannel = serverSocketChannel.accept();
            //11.切换成非阻塞模式
            socketChannel.configureBlocking(false);
            //12.将本客户端注册到选择器
            socketChannel.register(selector,SelectionKey.OP_READ);
        } else if (selectionKey.isReadable()) {
            //13.获取当前选择器上的读
            SocketChannel socketChannel = (SocketChannel) selectionKey.channel();
            //14.读取
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            int len;
            while ((len = socketChannel.read(buffer)) > 0) {
                buffer.flip();
                System.out.println(new String(buffer.array(),0,len));
                //清除之前的数据（覆盖写入）
                buffer.clear();
            }
        }
        //15.处理完毕后，移除当前事件
        it.remove();
    }
}
```

##### 2.3.4 客户端流程
**1)、获取通道**
```java
SocketChannel sChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 8888));
```

**2)、切换非阻塞模式**
```java
sChannel.configureBlocking(false);
```

**3)、分配指定大小的缓冲区**
```java
ByteBuffer buffer = ByteBuffer.allocate(1024);
```

**4)、发送数据给绑定的服务端**
```java
Scanner scan = new Scanner(System.in);
while (scan.hasNext()) {
	String str = scan.nextLine();
	buf.put((new SimpleDateFormat("yyyy/MM/dd HH:mm:ss").format(System.currentTimeMillis()) + "\n" + str).getBytes());
	buf.flip();
	sChannel.write(buf);
	buf.clear();
}
//关闭通道
sChannel.close();
```

##### 2.3.5 NIO非阻塞式网络通信示例代码
参考笔记最后的代码实现示例。

### 4. 总结
#### 4.1 NIO的优势
1. 优势在于 **一个线程管理多个通道** ；但是数据的处理将会变得复杂；
2. 如果需要管理同时打开的成千上万个连接，这些连接每次只是发送少量的数据，例如聊天服务器，则采用`NIO`；

#### 4.2 传统IO的优势
1. 适用于 **一个线程管理一个通道** 的情况；因为其中的流数据的读取是 **阻塞** 的；
2. 管理同时打开不太多的连接，且这些连接会发送大量的数据；

#### 4.3 NIO和IO的主要区别
##### 面向流与面向缓冲
**<font color="red">`IO`和`NIO`之间第一个最大的区别是：`IO`是面向流的，`NIO`是面向缓冲区的。</font>**
1. IO流是阻塞的，NIO流是不阻塞的。
2. **`IO` 是面向流的而Java NIO是面向缓冲区的，就如同一个的重点在于过程，另一个重点在于有一个阶段。**  
   在`IO`中读取数据和写入数据是面向`流（Stream）`的，就如同河流一样。所有的数据不停地向前的流淌，我们只能触碰到当前的流水。  
   如果需要获取某个数据的前一项或后一项数据那就必须自己缓存数据（将水从河流中打出来），而不能直接从流中获取（因为面向流就意味着我们只能获取数据流的切面）
3. **`NIO`中数据的读写是面向`缓冲区（Buffer）`的，读取时可以将整块的数据读取到缓冲区中，在写入时则可以将整个缓冲区中的数据一起写入。**  
   这就好像是在河流上建立水坝，面向流的数据读写只提供了一个数据流切面，而面向缓冲区的`IO`则使我们能够看到所有的水（数据的上下文），也就是说在缓冲区中获取某项数据的前一项数据或者是后一项数据十分方便。这种便利是有代价的，因为 **必须管理好缓冲区** ，这包括不能让新的数据覆盖了缓冲区中还没有被处理的有用数据；将缓冲区中的数据正确的分块，分清哪些被处理过哪些还没有等等。
4. **选择器：**  
  `NIO`的选择器允许 **一个单独的线程来监视多个通道** ，可以注册多个`通道`使用一个`选择器`，然后使用 **一个单独的线程** 来 **“选择”** 通道：这些通道里已经有可以处理的输入，或者选择已准备写入的通道。这种选择机制，使得一个单独的线程很容易来管理多个通道。

##### 阻塞与非阻塞IO
- **`IO`是阻塞的。** 这意味着，当一个线程调用`read()` 或` write()`时数据还没有准备好或者目前不可写，该线程会被阻塞，那么 **读写操作就会被阻塞直到数据准备好或目标可写为止** 。该线程在此期间不能再干任何事情了。
- **`NIO`是非阻塞的。** 使一个线程从某通道发送请求读取数据，但是它仅能得到目前可用的数据，如果目前没有数据可用时，就什么都不会获取，而不是保持线程阻塞，所以直至数据变的可以读取之前，该线程可以继续做其他的事情。
- **非阻塞写** 也是如此。一个线程请求写入一些数据到某通道，但不需要等待它完全写入，这个线程同时可以去做别的事情。 线程通常将`非阻塞IO`的空闲时间用于在其它通道上执行`IO`操作，所以一个单独的线程现在可以管理多个输入和输出`通道（channel）`。

**举个例子：**  
`IO`和`NIO`去超市买东西，如果超市中没有需要的商品或者数量还不够，`IO`会一直等到超市中需要的商品数量足够了就将所有需要的商品带回来。`NIO`则不同，不论超市中有多少需要的商品，它都将有需要的商品，立即全部买下并返回，甚至是没有需要的商品也会立即返回。

**<font color="red">IO 要求一次完成任务，NIO允许多次完成任务。</font>**

## 四、补充：代码实现示例
### 1. Java IO 流对象详解
Java中最基础的流是以下四种：

|            | 输入流      | 输出流       |
| ---------- | ----------- | ------------ |
| **字节流** | InputStream | OutputStream |
| **字符流** | Reader      | Writer       |

这四个都是抽象类，都位于 `java.io` 包目录。
- `java.io.InputStream` 字节输入流
- `java.io.OutputStream` 字节输出流
- `java.io.Reader` 字符输入流
- `java.io.Writer` 字符输出流

其中：
- **所有的流都实现了：`java.io.Colseable`接口**  
  都是可 **关闭** 的，都有`close()`方法。流毕竟是一个管道，这个是内存和硬盘之间的通道，在日常编码中养成一个好习惯，用完流将其关闭。
- **所有的输出流都实现了：`java.io.Flushable`接口**  
  都是可 **刷新** 的，都有`flush()`方法。在日常编码中养养成一个好习惯，输出流在最终输出之后，一定要记得`flush()`刷新一下。这个刷新表示将`通道/管道`当中剩余未输出的数据强行输出完（即清空管道），刷新的作用就是清空管道。<font color="red">如果没有`flush()`可能会导致数据丢失。</font>

**<font color="red">⚠️注意：在java中只要"类名"以`Stream`结尾的都是字节流。以`Reader/Writer`结尾的都是字符流。</font>**

而平时处理数据使用的流，**都是通过这四个流的子类展开的（均是抽象类）**。

<center>

![](https://cdn.jsdelivr.net/gh/XieRuhua/images/JavaLearning/Java相关/Java基础等/Java中的IO和NIO/Java中的IO流常用类.png)
</center>

`java.io` 包下需要掌握的流有16个:
```java
文件专属
java.io.FileinputStream   (用得最多)
java.io.FileOutputStream  (用得最多)
java.io.FileReader
java.io.FileWriter

转换流:(将字节流转换成字符流)
java.io.InputStreamReader
java.io.outputStreamWriter

缓冲流专属:
java.io.BufferedReader
java.io.BufferedWriter
java.io.BufferedInputStream
java.io.BufferedOutputStream

数据流专属:
java.io.DataInpoutStream
java.io.DataOutputStream

标准输出流:
java.io.PrintWriter
java.io.PrintStream
    
对象专属流:（掌握）
java.io.ObjectInputStream
java.io.ObjectOutputStream
```

下面对一些常用的流做代码演示：

#### 1.1 InputStream（字节流输入流）
`InputStream` 这个 **抽象类** 是表示以上输入字节流的所有类的超类（父类）。

`InputStream` 中的三个基本的读方法：
- `abstract int read()` ：读取一个字节数据，并返回读到的数据，如果返回 `-1`，表示读到了输入流的末尾。
- `int read(byte[] b)` ：将数据读入一个字节数组，同时返回实际读取的字节数。如果返回`-1`，表示读到了输入流的末尾。
- `int read(byte[] b, int off, int len)` ：将数据读入一个字节数组，同时返回实际读取的字节数。如果返回 `-1`，表示读到了输入流的末尾。`off` 指定在`数组b` 中存放数据的起始偏移位置；`len` 指定读取的最大字节数。

> `read()`方法 如果已读到末尾，返回`-1`表示不能继续读取了。

`InputStream` 的子类有：
- ByteArrayInputStream
- **FileInputStream**
- FilterInputStream
- PushbackInputStream
- DataInputStream
- **BufferedInputStream**
- LineNumberInputStream
- ObjectInputStream
- PipedInputStream
- SequenceInputStream
- StringBufferInputStream

这么多子类不需要每一个都记住，只需要记住两个最常用的：
- **FileInputStream**  
`FileInputStream`是文件字节输入流，就是对文件数据以字节的方式来处理，如音乐、视频、图片等。
- **BufferedInputStream**  
使用方式基本和`FileInputStream`一致。  
但是`BufferedInputStream`相对于`FileInputStream`来说有一个内部缓冲区数组，一次性读取较多的字节缓存起来，默认读取`defaultBufferSize = 8192`，在读文件时可以提高性能。

#### 1.2 OutputStream（字节输出流）
`OutputStream` 和 `InputStream` 是相对的，既然有输入就有输出。`OutputStream` 这个 **抽象类** 是表示以上输出字节流的所有类的超类（父类）。

`OutputStream` 中的三个基本的写方法：
- `abstract void write(int b)`：往输出流中写入一个字节。
- `void write(byte[] b)` ：往输出流中写入`数组b`中的所有字节。
- `void write(byte[] b, int off, int len)`：往输出流中写入`数组b` 中从偏移量 `off` 开始的 `len` 个字节的数据。

其它重要方法：
- `void flush()`：刷新输出流，强制缓冲区中的输出字节被写出。
- `void close()`：关闭输出流，释放和这个流相关的系统资源。

`OutputStream` 的子类有：
- ByteArrayOutputStream
- **FileOutputStream**
- FilterOutputStream
- **BufferedOutputStream**
- DataOutputStream
- PrintStream
- ObjectOutputStream
- PipedOutputStream
- ~~StringBufferInputStream~~

`FileOutputStream`、`BufferedOutputStream` 和 `FileInputStream`、`BufferedInputStream` 是相对的。

#### 1.3 Reader（字符输入流）
`Reader` 这个 **抽象类** 是表示以上输入字符流所有类的超类（父类）。

常见的子类有：
- **BufferedReader**
- LineNumberReader
- CharArrayReader
- FilterReader
- PushbackReader
- **InputStreamReader**
- **FileReader**
- PipedReader
- StringReader

补充：
1. `BufferedReader` 很明显就是一个装饰器，它和其子类负责装饰其它 `Reader` 对象。
2. **`InputStreamReader` 是一个连接字节流和字符流的桥梁，它将字节流转变为字符流。**

Reader 基本的三个读方法（和字节流对应）：
- `public int read() throws IOException`：读取一个字符，返回值为读取的字符。
- `public int read(char cbuf[]) throws IOException`：读取一系列 `字符到数组cbuf[]`中，返回值为实际读取的字符的数量。
- `public abstract int read(char cbuf[],int off,int len) throws IOException`：读取 `len` 个字符，从 `数组cbuf[]` 的下标 `off` 处开始存放，返回值为实际读取的字符数量，该方法必须由子类实现。

#### 1.4 Writer（字符输出流）
`Writer` 这个 **抽象类** 是表示以上输出字符流所有类的超类（父类）。

常见的子类有：
- **BufferedWriter**
- CharArrayWriter
- FilterWriter
- OutputStreamWriter
- **FileWriter**
- PipedWriter
- PrintWriter
- StringWriter

补充：
1. `OutputStreamWriter` 是 `OutputStream` 到 `Writer` 转换的桥梁，它的子类 `FileWriter` 其实就是一个实现此功能的具体类。
2. `BufferedWriter` 是一个装饰器为 `Writer` 提供缓冲功能。

writer 的主要写方法：
1. `public void write(int c) throws IOException`：写单个字符
2. `public void write(char cbuf[]) throws IOException`：将`字符数组cbuf[]`写到输出流 。
3. `public abstract void write(char cbuf[],int off,int len) throws IOException`：将`字符数组cbuf[]`中的从索引为`off`的位置处开始的`len`个字符写入输出流 。
4. `public void write(String str) throws IOException`：将字符串str中的字符写入输出流 。
5. `public void write(String str,int off,int len) throws IOException`：将 `字符串str` 中从索引 `off` 开始处的 `len` 个字符写入输出流 。

### 2. Java中常用的流的使用方法
#### 2.1 FileOutputStream写文件、FileInputStream读文件
分别为 `单个字节写`、`字节数字写`、`单个字节读取`、`字节数组读取`、`一次性读取`：
```java
import java.io.*;
import java.nio.charset.StandardCharsets;

public class OutputStreamTest {
    public static void main(String[] args) throws IOException {
        String filePath = "F:\\hello.txt";
        // 单个字节写入
        writeFile(filePath);

        readFile1(filePath);// 单个字节读取
        readFile2(filePath);// 字节数组读取
        readFile3(filePath);// 一次性读取
        readFile4(filePath);// 一次性读取，中文乱码处理
    }

    static void writeFile(String filePath) throws IOException {
        // 1、第一种方法写，单个字节写
        // 会自动创建文件，目录不存在会报错， true 表示 追加写，默认是false
        FileOutputStream fileOutputStream = new FileOutputStream(filePath, false);
        // 往文件里面一个字节一个字节的写入数据
        fileOutputStream.write((int) 'H');
        fileOutputStream.write((int) 'a');
        fileOutputStream.write((int) 'C');

        // 2、第二种方法写 字节数组写
        String s = " HelloCoder\n 测试中文乱码";
        // 入文件里面一个字节数组的写入文件，文件为UTF_8格式
        fileOutputStream.write(s.getBytes(StandardCharsets.UTF_8));
        // 刷新流
        fileOutputStream.flush();
        // 关闭流
        fileOutputStream.close();
    }

    /**
     * 第一种读的方法，单字节读
     */
    static void readFile1(String filePath) throws IOException {
        System.out.println("------一个字节读------");
        // 传文件夹的名字来创建对象
        FileInputStream fileInputStream = new FileInputStream(filePath);
        int by = 0;
        // 一个字节一个字节的读出数据
        while ((by = fileInputStream.read()) != -1) {
            System.out.print((char) by);
        }
        // 关闭流
        fileInputStream.close();
    }

    /**
     * 第二种读的方法，字节数组读
     */
    static void readFile2(String filePath) throws IOException {
        System.out.println();
        System.out.println("------字节数组读------");
        FileInputStream fileInputStream = new FileInputStream(filePath);
        // 通过File对象来创建对象
        fileInputStream = new FileInputStream(new File(filePath));
        int by = 0;
        byte[] bytes = new byte[10];
        // 一个字节数组的读出数据，高效
        while ((by = fileInputStream.read(bytes)) != -1) {
            for (int i = 0; i < by; i++) {
                System.out.print((char) bytes[i]);
            }
        }
        // 关闭流
        fileInputStream.close();
    }

    /**
     * 第三种读方法，一次性读
     */
    static void readFile3(String filePath) throws IOException {
        System.out.println();
        System.out.println("------一次性读文件------");
        FileInputStream fileInputStream = new FileInputStream(filePath);
        fileInputStream = new FileInputStream(new File(filePath));
        // 一次性读文件
        int iAvail = fileInputStream.available();
        int by = 0;
        byte[] bytesAll = new byte[iAvail];
        while ((by = fileInputStream.read(bytesAll)) != -1) {
            for (int i = 0; i < by; i++) {
                System.out.print((char) bytesAll[i]);
            }
        }
        fileInputStream.close();
    }

    /**
     * 补充：中文乱码处理
     */
    static void readFile4(String filePath) throws IOException {
        System.out.println();
        System.out.println("------一次性读文件（中文乱码处理）------");
        FileInputStream fileInputStream = new FileInputStream(filePath);
        InputStreamReader reader = new InputStreamReader(fileInputStream, StandardCharsets.UTF_8); //使用中文编码UTF-8
        BufferedReader br = new BufferedReader(reader);
        String line;
        while ((line = br.readLine()) != null) {
            System.out.println(line);
        }
        br.close();
        reader.close();
        fileInputStream.close();
    }
}
```

输出：
```text
------一个字节读------
HaC HelloCoder
 æµè¯ä¸­æä¹±ç 
------字节数组读------
HaC HelloCoder
 ￦ﾵﾋ￨ﾯﾕ￤ﾸﾭ￦ﾖﾇ￤ﾹﾱ￧ﾠﾁ
------一次性读文件------
HaC HelloCoder
 ￦ﾵﾋ￨ﾯﾕ￤ﾸﾭ￦ﾖﾇ￤ﾹﾱ￧ﾠﾁ
------一次性读文件（中文乱码处理）------
HaC HelloCoder
 测试中文乱码
```
**<font color="red">⚠️注意：字符串如果包含中文，就会出现乱码，这是因为`FileOutputStream`是字节流，将文本按字节写入。</font>**

#### 2.2 FileWriter写文件、FileReader读文件
分别为 `字符串写`、`单字符读`、`字符数组读`：
```java
import java.io.*;

public class ReaderTest {
    public static void main(String[] args) throws IOException {
        write();// 字符串写

        read1();// 单个char读取
        read2();// char数组[]读取
    }

    static void write() throws IOException {
        FileWriter fileWriter = new FileWriter("F:\\Hello1.txt");
        // 为防止乱码，可以这样写，字符流和字节流互转
        // Writer fileWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("F:\\Hello1.txt"), StandardCharsets.UTF_8));
        fileWriter.write("一二三四五\n" + "六七八九十");

        // 如果没有刷新，也没有关闭流的话 数据是不会写入文件的
        fileWriter.flush();
        fileWriter.close();
    }

    static void read1() throws IOException {
        System.out.println("------单个char读取-------");
        FileReader fileReader = new FileReader("F:\\Hello1.txt");
        int ch = 0;
        String str = "";
        // 单个char读取
        while ((ch = fileReader.read()) != -1) {
            str += (char) ch;
        }
        System.out.println(str);
    }

    static void read2() throws IOException {
        System.out.println("------char数组[]读取-------");
        FileReader fileReader = new FileReader(new File("F:\\Hello1.txt"));
        int len = 0;
        char[] chars = new char[10];
        while ((len = fileReader.read(chars)) != -1) {
            //这种读有误
//            System.out.print(new String(chars));
            // len 是这次读到的字符长度，只需要截取这次的字符即可
            System.out.print((new String(chars, 0, len)));
        }
        fileReader.close();
    }
}
```

输出：
```text
------单个char读取-------
一二三四五
六七八九十
------char数组[]读取-------
一二三四五
六七八九十
```
`FileWriter`、`FileReader` 可以用来读写一个含中文字符的文件。

**注意点：**  
**1、流转换**
```java
Writer fileWriter = new BufferedWriter(new OutputStreamWriter(new FileOutputStream("F:\\Hello1.txt"), StandardCharsets.UTF_8));
```
这里其实是把`字节流`转换为`字符流`，可用来解决乱码问题。

**2、读的位置**  
这里的写法需要注意，因为这里读写是一次性读`10`个`char`类型的字符，如果换成以下代码：
```java
int len = 0;
char[] chars = new char[10];
while ((len = fileReader.read(chars)) != -1) {
    //不能这样写
    System.out.print(new String(chars));
    //System.out.print((new String(chars, 0, len)));
}
```

则输出：
```text
------char数组[]读取-------
一二三四五
六七八九十二三四五
六七八九
```

可以看到输出不正确，因为一次性读`10`个`char`
- 第一次读的数组内容是：`[一, 二, 三, 四, 五, \n, 六, 七, 八, 九]`（⚠️ **注意：换行符也占用一个位置** ）
- 第二次读的数组内容是： `[十, 二, 三, 四, 五, \n, 六, 七, 八, 九]` 
  其实这一次它只读了`十`这 一个字符，其中 `二, 三, 四, 五, \n, 六, 七, 八, 九` 是上一个数组的内容，因为它是已存在在数组的旧数据（因为数组长度是10，读到字符 **`十`** 的时候已经读完了，而后续的就数组的值未被覆盖）。

所以需要`new String(chars, 0, len)` ，`len` 是这次读到的字符长度，只需要截取这次的字符即可。

以上这两个例子中，还需要注意的几个地方：
1. 只有在写文件的时候才需要`flush()`方法，而读是不需要的。
2. **读、写** 完毕都需要调用`close()` 方法关闭流。
3. **单个字节、字符** 读写效率较慢，建议使用 **字节、字符数组** 读取。

#### 2.3 BufferedInputStream、BufferedOutputStream 缓冲字节流
`BufferedInputStream` 是带`缓冲区`的，在 **复制**、**移动** 文件时会快一点。

> 建议使用缓冲字节流操作文件，但是其构造方法入参还是`InputStream`和`OutputStream`。

`Java`使用`IO` 读取文件时，会进入 **核心态** （核心态是操作系统内核所运行的模式，运行在该模式的代码，可以无限制地对系统存储、外部设备进行访问），在调用驱动进行`IO`操作时，本身就会缓存在系统级别的缓存中；当你第二次读取时，会由 **用户态** 进入**核心态** ，读取系统缓存。  
而`BufferedInputStream`就是一次性读取较多并且缓存起来，下次就直接从 **核心态的缓存** 中读，而不用在`用户态`和`核心态`之间切换，从而提升效率。

如：
```java
public class InputStreamAndBufferInputStreamCopyFile {
    public static void main(String[] args) throws IOException {
        useInputStreamCopyFile(); // 缓冲流复制文件
        useBufferInputStream(); // 普通流复制文件
    }

    static void useInputStreamCopyFile() throws IOException {
        File file = new File("F:\\hello.txt");
        InputStream is = new FileInputStream(file);

        File file2 = new File("F:\\hello_copy.txt");
        OutputStream os = new FileOutputStream(file2);
        int len = 0;
        byte[] bytes = new byte[1024];
        while ((len = is.read(bytes)) != -1) {
            os.write(bytes);
        }
        is.close();
        os.close();
    }

    static void useBufferInputStream() throws IOException {
        BufferedInputStream bis = new BufferedInputStream(new FileInputStream("F:\\hello.txt"));
        BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream("F:\\hello_copy2.txt"));
        int len = 0;
        byte[] bytes = new byte[1024];
        while ((len = bis.read(bytes)) != -1) {
            bos.write(bytes, 0, len);
        }
        bos.close();
        bis.close();
    }
}
```
输出结果：F盘下生成两个复制文件

#### 2.4 BufferedReader、BufferedWriter 字符缓冲流
`BufferedReader` 有一个好处，就是它提供了`readline()`、`newLine()`方法，可以 **按行读取文件** 。

如：
```java
public class BufferedReaderTest {
    public static void main(String[] args) throws IOException {
        useInputStreamCopyFile(); // 这种方法适用于任何文件

        // 下面两种方法copy的文件变大了，因为是使用字符流处理的
        useBufferedReaderCopyFile(); // 这种方法只适用于字符文件
        useFileReaderCopyFile(); // 这种方法一步到位，只适用于字符文件

    }

    static void useInputStreamCopyFile() throws IOException {
        File file = new File("F:\\Hello1.txt");
        InputStream is = new FileInputStream(file);

        File file2 = new File("F:\\Hello1_copy1.txt");
        OutputStream os = new FileOutputStream(file2);
        int len = 0;
        byte[] bytes = new byte[1024];
        while ((len = is.read(bytes)) != -1) {
            os.write(bytes, 0, len);
        }
        is.close();
        os.close();
    }

    static void useBufferedReaderCopyFile() throws IOException {
        File file = new File("F:\\Hello1.txt");
        InputStream is = new FileInputStream(file);
        Reader reader = new InputStreamReader(is);
        // 创建字符流缓冲区，BufferedReader 的构造入参是一个 Reader
        BufferedReader bufferedReader = new BufferedReader(reader);

        File file2 = new File("F:\\Hello1_copy2.txt");
        OutputStream os = new FileOutputStream(file2);
        Writer writer = new OutputStreamWriter(os);
        // 创建字符流缓冲区，BufferedWriter 的构造入参是一个 Writer
        BufferedWriter bufferedWriter = new BufferedWriter(writer);

        String line = null;
        // readLine()方法 是根据\n 换行符读取的
        while ((line = bufferedReader.readLine()) != null) {
            bufferedWriter.write(line);
            // 这里要加换行
            bufferedWriter.newLine();
        }
        bufferedReader.close();
        bufferedWriter.close();
    }

    static void useFileReaderCopyFile() throws IOException {
        // 使用FileReader、FileWriter 一步到位
        Reader reader = new FileReader("F:\\Hello1.txt");
        BufferedReader bufferedReader = new BufferedReader(reader);
        Writer writer = new FileWriter("F:\\Hello1_copy3.txt");
        BufferedWriter bufferedWriter = new BufferedWriter(writer);
        String line = null;
        while ((line = bufferedReader.readLine()) != null) {
            bufferedWriter.write(line);
            bufferedWriter.newLine();
        }
        bufferedReader.close();
        bufferedWriter.close();
    }
}
```

### 3. close() 与flush()
有如下代码：
```java
public class FlushTest {
    public static void main(String[] args) throws IOException {
        FileReader fileReader = new FileReader("F:\\test1.txt"); //大文件
        FileWriter fileWriter = new FileWriter("F:\\test2.txt");
        int readerCount = 0;
        //一次读取1024个字符
        char[] chars = new char[1024];
        while (-1 != (readerCount = fileReader.read(chars))) {
            fileWriter.write(chars, 0, readerCount);
        }
    }
}
```
这里并没有调用`close()`方法。
> `close()`方法包含`flush()`方法 ，即调用`close()`方法会自动触发`flush()`

通过结果可以看到，复制的文件变小了。很明显，数据有丢失，丢失的就是 **缓冲区“残余”的数据** 。

在计算机层面，`Java`对磁盘进行操作，`IO`是有缓存的，并不是真正意义上的一边读一边写，底层的**落盘（数据真正写到磁盘）**另有方法。  
所以，最后会有一部分数据还是在内存中的，如果不调用`flush()`方法，数据会随着查询结束而消失，这就是为什么数据丢失使得文件变小了。

> `BufferedOutputStream`、`BufferedFileWriter` 同理

再举个例子：
```java
class FlushTest2{
    public static void main(String[] args) throws IOException {
        FileWriter fileWriter = new FileWriter("F:\\Hello3.txt");
        fileWriter.write("测试内容");
    }
}
```
不调用`flush()方法`会发现，`Hello3.txt`文件是空白的，没有把数据写进来，也是因为数据还在内存中而不是落盘到磁盘了。

所以为了实时性和安全性，`IO`在写操作的时候，需要调用`flush()`或者`close()`。

`close()` 和`flush()`的区别：
- `close()`是关闭流对象，但是会先刷新一次缓冲区（调用一次`flush()`方法），**流关闭之后，流对象不可以继续再使用了，否则报空指针异常。**
- `flush()`仅仅是刷新缓冲区，准确的说是 **<font color="red">"强制写出缓冲区的数据"</font>** ，流对象还可以继续使用。

总结一下：
- Java的`IO`有一个 `缓冲区` 的概念，但不是`NIO`中的`Buffer`概念的缓冲区。
- 如果是文件读写完的同时缓冲区 **刚好装满** , 那么缓冲区会把里面的数据朝目标文件自动进行读或写（这就是为什么总剩下有一点没写完） , 这种时候你不调用`close()`方法也不会出现问题; 
- 如果文件在读写完成时, 缓冲区 **没有装满** ，也没有调用`flush()`， 这个时候装在缓冲区的数据就不会自动的朝目标文件进行 **读** 或 **写** , 从而造成缓冲区中的这部分数据丢失 , 所以这个是时候就需要在`close()`之前先调用`flush()`方法, 手动使缓冲区数据读写到目标文件。

### 4. 总结
一般的业务需求不是读写文件，更多的是 **生成文件** 、 **复制文件** 、 **移动文件** 。所以如何选择`IO流`，是需要掌握的。
1. `字节流`是原生的操作，`字符流`是经过处理后的操作。
2. `字节流`一般用来处理 **图像** 、 **视频** 、 **音频** 、 **PPT** 、 **Word** 等类型的文件。字符流一般用于处理 **纯文本类型** 的文件，如 **TXT文件** 等，但不能处理图像视频等非文本文件。  
   <font color="red">用一句话说就是：字节流可以处理一切文件，而字符流只能处理纯文本文件。含有汉字的文件就使用字符流处理。</font>
3. 流对象需要转换使用转换流；需要高效则使用缓冲流。
4. 使用流之后一定要调用`close()`方法。

### 5. 补充1：NIO非阻塞式网络通信入门案例
需求：服务端接收客户端的连接请求，并接收多个客户端发送过来的事件。

**Server端代码实现：**
```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.Iterator;

public class Server {
    public static void main(String[] args) {
        try {
            //1.获取管道
            ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
            //2.设置非阻塞模式
            serverSocketChannel.configureBlocking(false);
            //3.绑定端口
            serverSocketChannel.bind(new InetSocketAddress(8888));
            //4.获取选择器
            Selector selector = Selector.open();
            //5.将通道注册到选择器上，并且开始指定监听的接收事件
            serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
            //6.轮询已经就绪的事件
            while (selector.select() > 0) {
                System.out.println("开启事件处理");
                //7.获取选择器中所有注册的通道中已准备好的事件
                Iterator<SelectionKey> it = selector.selectedKeys().iterator();
                //8.开始遍历事件
                while (it.hasNext()) {
                    SelectionKey selectionKey = it.next();
                    System.out.println("--->" + selectionKey);
                    //9.判断这个事件具体是啥
                    if (selectionKey.isAcceptable()) {
                        //10.获取当前接入事件的客户端通道
                        SocketChannel socketChannel = serverSocketChannel.accept();
                        //11.切换成非阻塞模式
                        socketChannel.configureBlocking(false);
                        //12.将本客户端注册到选择器
                        socketChannel.register(selector, SelectionKey.OP_READ);
                    } else if (selectionKey.isReadable()) {
                        //13.获取当前选择器上的读
                        SocketChannel socketChannel = (SocketChannel) selectionKey.channel();
                        //14.读取
                        ByteBuffer buffer = ByteBuffer.allocate(1024);
                        int len;
                        while ((len = socketChannel.read(buffer)) > 0) {
                            buffer.flip();
                            System.out.println(new String(buffer.array(), 0, len));
                            //清除之前的数据（覆盖写入）
                            buffer.clear();
                        }
                    }
                    //15.处理完毕后，移除当前事件
                    it.remove();
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

**Client端代码实现：**
```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.util.Scanner;

public class Client {
    public static void main(String[] args) {
        try {
            // 获取通道
            SocketChannel socketChannel = SocketChannel.open(new InetSocketAddress("127.0.0.1", 8888));
            socketChannel.configureBlocking(false);
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            Scanner scanner = new Scanner(System.in);
            while (true) {
                System.out.print("请输入:");
                String msg = scanner.nextLine();
                buffer.put(msg.getBytes());
                buffer.flip();
                socketChannel.write(buffer);
                buffer.clear();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

先运行server，再运行client。在cliten端控制台输入如下：
```
请输入:1
请输入:测试
请输入:
```

server端控制台对应打印如下：
```
开启事件处理
--->sun.nio.ch.SelectionKeyImpl@5faeada1
开启事件处理
--->sun.nio.ch.SelectionKeyImpl@2bbf4b8b
1
开启事件处理
--->sun.nio.ch.SelectionKeyImpl@2bbf4b8b
测试
```

### 6. 补充2：NIO网络编程应用实例-群聊系统
**需求:进一步理解 `NIO` 非阻塞网络编程机制，实现多人群聊**
- 编写一个 `NIO` 群聊系统，实现客户端与客户端的通信需求（ **非阻塞** ）；
- 服务器端：可以监测用户上线，离线，并实现消息转发功能；
- 客户端：通过 `channel` 可以无阻塞发送消息给其它所有客户端用户，同时可以接受其它客户端用户通过服务端转发来的消息。

**服务端代码：**
```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.Iterator;

public class Server {
    //定义属性
    private Selector selector;
    private ServerSocketChannel ssChannel;
    private static final int PORT = 9999;

    //构造器
    //初始化工作
    public Server() {
        try {
            // 1、获取通道
            ssChannel = ServerSocketChannel.open();
            // 2、切换为非阻塞模式
            ssChannel.configureBlocking(false);
            // 3、绑定连接的端口
            ssChannel.bind(new InetSocketAddress(PORT));
            // 4、获取选择器Selector
            selector = Selector.open();
            // 5、将通道都注册到选择器上去，并且开始指定监听接收事件
            ssChannel.register(selector, SelectionKey.OP_ACCEPT);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //监听
    public void listen() {
        System.out.println("监听线程:" + Thread.currentThread().getName());
        try {
            while (selector.select() > 0) {
                // 7、获取选择器中的所有注册的通道中已经就绪好的事件
                Iterator<SelectionKey> it = selector.selectedKeys().iterator();
                // 8、开始遍历这些准备好的事件
                while (it.hasNext()) {
                    // 提取当前这个事件
                    SelectionKey sk = it.next();
                    // 9、判断这个事件具体是什么
                    if (sk.isAcceptable()) {
                        // 10、直接获取当前接入的客户端通道
                        SocketChannel schannel = ssChannel.accept();
                        // 11 、切换成非阻塞模式
                        schannel.configureBlocking(false);
                        // 12、将本客户端通道注册到选择器
                        System.out.println(schannel.getRemoteAddress() + " 上线 ");
                        schannel.register(selector, SelectionKey.OP_READ);
                        //提示
                    } else if (sk.isReadable()) {
                        //处理读 (专门写方法..)
                        readData(sk);
                    }

                    it.remove(); // 处理完毕之后需要移除当前事件
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            //发生异常处理....

        }
    }

    //读取客户端消息
    private void readData(SelectionKey key) {
        //获取关联的channel
        SocketChannel channel = null;
        try {
            //得到channel
            channel = (SocketChannel) key.channel();
            //创建buffer
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            int count = channel.read(buffer);
            //根据count的值做处理
            if (count > 0) {
                //把缓存区的数据转成字符串
                String msg = new String(buffer.array());
                //输出该消息
                System.out.println("来自客户端---> " + msg);
                //向其它的客户端转发消息(去掉自己), 专门写一个方法来处理
                sendInfoToOtherClients(msg, channel);
            }
        } catch (IOException e) {
            try {
                System.out.println(channel.getRemoteAddress() + " 离线了..");
                e.printStackTrace();
                //取消注册
                key.cancel();
                //关闭通道
                channel.close();
            } catch (IOException e2) {
                e2.printStackTrace();
                ;
            }
        }
    }

    //转发消息给其它客户(通道)
    private void sendInfoToOtherClients(String msg, SocketChannel self) throws IOException {
        System.out.println("服务器转发消息中...");
        System.out.println("服务器转发数据给客户端线程: " + Thread.currentThread().getName());
        //遍历 所有注册到selector 上的 SocketChannel,并排除 self
        for (SelectionKey key : selector.keys()) {
            //通过 key  取出对应的 SocketChannel
            Channel targetChannel = key.channel();
            //排除自己
            if (targetChannel instanceof SocketChannel && targetChannel != self) {
                //转型
                SocketChannel dest = (SocketChannel) targetChannel;
                //将msg 存储到buffer
                ByteBuffer buffer = ByteBuffer.wrap(msg.getBytes());
                //将buffer 的数据写入 通道
                dest.write(buffer);
            }
        }
    }

    public static void main(String[] args) {
        //创建服务器对象
        Server groupChatServer = new Server();
        groupChatServer.listen();
    }
}
```

**客户端代码：**
```java
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Scanner;

public class Client {
    //定义相关的属性
    private final String HOST = "127.0.0.1"; // 服务器的ip
    private final int PORT = 9999; //服务器端口
    private Selector selector;
    private SocketChannel socketChannel;
    private String username;

    //构造器, 完成初始化工作
    public Client() throws IOException {
        selector = Selector.open();
        //连接服务器
        socketChannel = socketChannel.open(new InetSocketAddress("127.0.0.1", PORT));
        //设置非阻塞
        socketChannel.configureBlocking(false);
        //将channel 注册到selector
        socketChannel.register(selector, SelectionKey.OP_READ);
        //得到username
        username = socketChannel.getLocalAddress().toString().substring(1);
        System.out.println(username + " is ok...");
    }

    //向服务器发送消息
    public void sendInfo(String info) {
        info = username + " 说：" + info;
        try {
            socketChannel.write(ByteBuffer.wrap(info.getBytes()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //读取从服务器端回复的消息
    public void readInfo() {
        try {
            int readChannels = selector.select();
            if (readChannels > 0) {//有可以用的通道

                Iterator<SelectionKey> iterator = selector.selectedKeys().iterator();
                while (iterator.hasNext()) {

                    SelectionKey key = iterator.next();
                    if (key.isReadable()) {
                        //得到相关的通道
                        SocketChannel sc = (SocketChannel) key.channel();
                        //得到一个Buffer
                        ByteBuffer buffer = ByteBuffer.allocate(1024);
                        //读取
                        sc.read(buffer);
                        //把读到的缓冲区的数据转成字符串
                        String msg = new String(buffer.array());
                        System.out.println(msg.trim());
                    }
                }
                iterator.remove(); //删除当前的selectionKey, 防止重复操作
            } else {
                //System.out.println("没有可以用的通道...");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws Exception {
        //启动客户端
        Client chatClient = new Client();
        //启动一个线程, 每个3秒，读取从服务器发送数据
        new Thread() {
            public void run() {
                while (true) {
                    chatClient.readInfo();
                    try {
                        Thread.currentThread().sleep(3000);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
            }
        }.start();

        //发送数据给服务器端
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNextLine()) {
            String s = scanner.nextLine();
            chatClient.sendInfo(s);
        }
    }
}
```

操作步骤：
1. 启动`server服务`，再启动两个`client服务`  
   `server`打印如下：
   ```
   监听线程:main
   /127.0.0.1:2698 上线 
   /127.0.0.1:2710 上线 
   ```

   `client1`打印如下：
   ```
   127.0.0.1:2698 is ok...
   ```

   `client2`打印如下：
   ```
   127.0.0.1:2710 is ok...
   ```

2. 在`client1`服务的控制台中输入内容  
   `client1`输入：
   ```
   127.0.0.1:2698 is ok...
   你好，我是client1
   ```

   `server`：
   ```
   监听线程:main
   /127.0.0.1:2698 上线 
   /127.0.0.1:2710 上线 
   来自客户端---> 127.0.0.1:2698 说：你好，我是client1

   服务器转发消息中...
   服务器转发数据给客户端线程: main
   ```

   `client2`接收：
   ```
   127.0.0.1:2710 is ok...
   127.0.0.1:2698 说：你好，我是client1
   ```

3. 在client2服务的控制台中输入内容  
   `client2`输入:
   ```
   127.0.0.1:2710 is ok...
   127.0.0.1:2698 说：你好，我是client1
   你好，我是client2，很高兴认识你
   ```

   `server`：
   ```
   监听线程:main
   /127.0.0.1:2698 上线 
   /127.0.0.1:2710 上线 
   来自客户端---> 127.0.0.1:2698 说：你好，我是client1

   服务器转发消息中...
   服务器转发数据给客户端线程: main
   来自客户端---> 127.0.0.1:2710 说：你好，我是client2，很高兴认识你

   服务器转发消息中...
   服务器转发数据给客户端线程: main
   ```

   `client1`接收：
   ```
   127.0.0.1:2698 is ok...
   你好，我是client1
   127.0.0.1:2710 说：你好，我是client2，很高兴认识你
   ```
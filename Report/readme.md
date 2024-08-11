## 1. 任务背景

针对Parallel GC，编写程序模拟内存分配与垃圾回收场景，能够反应出该GC的特点。解释它的GC日志。修改程序或JVM参数以达成特定目标，如更低的GC延迟。
## 2. 研究计划
- [X] 实现GC测试用例
- [x] 选择ParrallelGC进行实验，记录实验结果
- [x] 改变参数配置，优化GC延迟
## 3. GC日志分析
### 3.1 Java程序
```java
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * GC测试用例
 */
public class TestGC {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=========================GC测试用例=========================");
        long start= System.currentTimeMillis();
        List<byte[]> list = new ArrayList<>();
        int maxIterations = 3000;
        for(int i=1;i<=maxIterations;i++){
            //新增1M
            list.add(new byte[1*1024*1024]);
            //每隔100 clear一次
            if(i%100==0){
                list.clear();
                System.out.printf("iteration:%5d\t\t清空List\n",i);
            }
            //休眠10ms
            Thread.sleep(10);
        }
        long end= System.currentTimeMillis();
        System.out.printf("耗费时间"+(end-start)+'s');
        System.out.println("测试完成");
    }
}
```
### 3.2 JVM参数
```
# 使用ParallelGC
-XX:+UseParallelGC
# 最大堆空间1G                                              
-Xmx1024m 
# 最小堆空间512M
-Xms512m 
# 新生代空间256M
-Xmn256m
# 控制台输出日志 
-XX:+PrintGCDetails
# 打印日志 
-Xlog:gc*=debug:file=./log/gcParallel.log
```
### 3.3 测试参数
|  参数名字  |       详细配置        |
| :--------: | :-------------------: |
|  操作系统  |      Windows 11       |
|  JDK 版本  | 17.0.2+8-86 (release) |
|    内存    |          16G          |
|    CPU     |          12           |
|   线程数   |          10           |
|   最大堆   |          1G           |
|   最小堆   |         512M          |
| 年轻代大小 |         256M          |
### 3.4 GC日志
#### 3.4.1 启动命令

使用Intellij IDEA运行程序，JVM参数如下:

```log

-XX:+UseSerialGC -Xmx1024m -Xms512m -Xmn256m -XX:+PrintGCDetails -Xlog:gc*=debug:file=./log/gcSerial.log

```
#### 3.4.2 日志分析
##### 年轻代的GC
一共执行了17次Young GC，Young GC发生的原因是年轻代空间不足，触发垃圾回收机制，将存活对象转移到survivor区域
或老年区域。**以GC(10)为例**:

```
[33.309s][debug  ][gc,heap        ] GC(10) Heap before GC invocations=11 (full 0):
[33.309s][debug  ][gc,heap        ] GC(10)  PSYoungGen      total 209408K, used 208168K [0x00000000f0000000, 0x0000000100000000, 0x0000000100000000)
[33.310s][debug  ][gc,heap        ] GC(10)   eden space 168960K, 99% used [0x00000000f0000000,0x00000000fa449e30,0x00000000fa500000)
[33.310s][debug  ][gc,heap        ] GC(10)   from space 40448K, 98% used [0x00000000fd880000,0x00000000fff80270,0x0000000100000000)
[33.310s][debug  ][gc,heap        ] GC(10)   to   space 46592K, 0% used [0x00000000fa500000,0x00000000fa500000,0x00000000fd280000)
[33.310s][debug  ][gc,heap        ] GC(10)  ParOldGen       total 262144K, used 190103K [0x00000000c0000000, 0x00000000d0000000, 0x00000000f0000000)
[33.310s][debug  ][gc,heap        ] GC(10)   object space 262144K, 72% used [0x00000000c0000000,0x00000000cb9a5cf8,0x00000000d0000000)
[33.310s][debug  ][gc,heap        ] GC(10)  Metaspace       used 1026K, committed 1216K, reserved 1056768K
[33.310s][debug  ][gc,heap        ] GC(10)   class space    used 83K, committed 192K, reserved 1048576K
```

在GC之前eden区空间使用率为99%，from区使用率为98%，说明年轻代空间不足，无法容纳新建对象，因此触发Young GC进行垃圾回收。

```
[33.313s][info   ][gc             ] GC(10) Pause Young (Allocation Failure) 388M->201M(437M) 3.620ms
[33.313s][info   ][gc,cpu         ] GC(10) User=0.00s Sys=0.00s Real=0.00s
[33.313s][debug  ][gc,heap        ] GC(10) Heap after GC invocations=11 (full 0):
[33.314s][debug  ][gc,heap        ] GC(10)  PSYoungGen      total 185856K, used 16384K [0x00000000f0000000, 0x0000000100000000, 0x0000000100000000)
[33.314s][debug  ][gc,heap        ] GC(10)   eden space 168960K, 0% used [0x00000000f0000000,0x00000000f0000000,0x00000000fa500000)
[33.314s][debug  ][gc,heap        ] GC(10)   from space 16896K, 96% used [0x00000000fa500000,0x00000000fb500100,0x00000000fb580000)
[33.314s][debug  ][gc,heap        ] GC(10)   to   space 47616K, 0% used [0x00000000fd180000,0x00000000fd180000,0x0000000100000000)
[33.314s][debug  ][gc,heap        ] GC(10)  ParOldGen       total 262144K, used 190103K [0x00000000c0000000, 0x00000000d0000000, 0x00000000f0000000)
[33.314s][debug  ][gc,heap        ] GC(10)   object space 262144K, 72% used [0x00000000c0000000,0x00000000cb9a5cf8,0x00000000d0000000)
[33.314s][debug  ][gc,heap        ] GC(10)  Metaspace       used 1026K, committed 1216K, reserved 1056768K
[33.314s][debug  ][gc,heap        ] GC(10)   class space    used 83K, committed 192K, reserved 1048576K
```

垃圾回收后eden区域由168231K(168960k)变为0K(168960k)，from区域由39936K(40448K)变为16384K(16896K)，老年代不变，堆空间由388M变为201M。说明本次垃圾回收将eden中的存活对象移动到from区，并清除年轻代中的垃圾对象，没有新对象加入老年代。

##### Full GC
一共进行了1次Full GC，Full GC的原因是老年代的空间不足，触发全局的垃圾的回收机制，同时回收年轻代和老年代的垃圾对象，并按需拓展堆内存空间。
**以GC(12)为例**:

```
[36.007s][debug  ][gc,heap        ] GC(12) Heap before GC invocations=13 (full 1):
[36.007s][debug  ][gc,heap        ] GC(12)  PSYoungGen      total 205312K, used 47104K [0x00000000f0000000, 0x0000000100000000, 0x0000000100000000)
[36.007s][debug  ][gc,heap        ] GC(12)   eden space 157696K, 0% used [0x00000000f0000000,0x00000000f0000000,0x00000000f9a00000)
[36.007s][debug  ][gc,heap        ] GC(12)   from space 47616K, 98% used [0x00000000fd180000,0x00000000fff802e0,0x0000000100000000)
[36.007s][debug  ][gc,heap        ] GC(12)   to   space 52224K, 0% used [0x00000000f9a00000,0x00000000f9a00000,0x00000000fcd00000)
[36.007s][debug  ][gc,heap        ] GC(12)  ParOldGen       total 262144K, used 224919K [0x00000000c0000000, 0x00000000d0000000, 0x00000000f0000000)
[36.007s][debug  ][gc,heap        ] GC(12)   object space 262144K, 85% used [0x00000000c0000000,0x00000000cdba5f18,0x00000000d0000000)
[36.007s][debug  ][gc,heap        ] GC(12)  Metaspace       used 1026K, committed 1216K, reserved 1056768K
[36.007s][debug  ][gc,heap        ] GC(12)   class space    used 83K, committed 192K, reserved 1048576K
```

在GC之前eden区空间使用率为0%，from区使用率为98%，老年代使用率85%，说明老年代空间不足，无法容纳新增的对象，因此触发Full GC进行垃圾回收

```
[36.022s][debug  ][gc,ergo        ] GC(12) Old promo_size: 201326592 desired_promo_size: 196083712
[36.022s][debug  ][gc             ] GC(12) Expanding ParOldGen from 262144K by 67072K to 329216K
[36.022s][debug  ][gc,ergo        ] GC(12) AdaptiveSizeStop: collection: 13 
[36.022s][info   ][gc,heap        ] GC(12) PSYoungGen: 47104K(205312K)->0K(209920K) Eden: 0K(157696K)->0K(157696K) From: 47104K(47616K)->0K(52224K)
[36.022s][info   ][gc,heap        ] GC(12) ParOldGen: 224919K(262144K)->83557K(329216K)
[36.022s][info   ][gc,metaspace   ] GC(12) Metaspace: 1026K(1216K)->1026K(1216K) NonClass: 942K(1024K)->942K(1024K) Class: 83K(192K)->83K(192K)
[36.022s][info   ][gc             ] GC(12) Pause Full (Ergonomics) 265M->81M(526M) 14.670ms
[36.022s][info   ][gc,cpu         ] GC(12) User=0.00s Sys=0.02s Real=0.01s
[36.022s][debug  ][gc,heap        ] GC(12) Heap after GC invocations=13 (full 1):
[36.022s][debug  ][gc,heap        ] GC(12)  PSYoungGen      total 209920K, used 0K [0x00000000f0000000, 0x0000000100000000, 0x0000000100000000)
[36.022s][debug  ][gc,heap        ] GC(12)   eden space 157696K, 0% used [0x00000000f0000000,0x00000000f0000000,0x00000000f9a00000)
[36.022s][debug  ][gc,heap        ] GC(12)   from space 52224K, 0% used [0x00000000f9a00000,0x00000000f9a00000,0x00000000fcd00000)
[36.022s][debug  ][gc,heap        ] GC(12)   to   space 52224K, 0% used [0x00000000fcd00000,0x00000000fcd00000,0x0000000100000000)
[36.022s][debug  ][gc,heap        ] GC(12)  ParOldGen       total 329216K, used 83557K [0x00000000c0000000, 0x00000000d4180000, 0x00000000f0000000)
[36.022s][debug  ][gc,heap        ] GC(12)   object space 329216K, 25% used [0x00000000c0000000,0x00000000c51995b0,0x00000000d4180000)
[36.022s][debug  ][gc,heap        ] GC(12)  Metaspace       used 1026K, committed 1216K, reserved 1056768K
[36.022s][debug  ][gc,heap        ] GC(12)   class space    used 83K, committed 192K, reserved 1048576K
[36.022s][debug  ][gc,task,time   ] GC(12) VM-Thread 360074838 360106685 360221758
```

由于Full GC同时对年轻代和老年代进行垃圾回收，因此两个区域的空间使用情况均发生变化。垃圾回收后from区域由47104K(47616K)变为0K(52224K), 老年代由224919K(262144K)变为83557K(329216K)，堆空间由265M变为81M。本次垃圾回收，JVM尝试将from中的存活对象移入老年代，但老年代的空间不足，因此触发了空间拓展，老年代的空间由262144K变为329216K，之后通过标记-清除法清理老年代中垃圾对象。

#### 3.4.3 性能指标
|    GC配置    | 代码运行时间 | GC运行时间 | GC最大延迟 | 吞吐率 |Young GC次数|Full GC次数|
|:----------:|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|
| ParallelGC |49667ms|149.133ms|19.017ms|99.701%|17|1|
## 4. GC性能优化
### 4.1 年轻代大小对GC性能的影响
当年轻代空间使用率达到某一个阈值时，JVM会主动触发Young GC进行垃圾回收，通过增大年轻代的内存空间，可以减少GC的频率。

**启动命令:**

使用Intellij IDEA运行程序，JVM参数如下:

```
-XX:+UseParallelGC -Xmx1024m -Xms1024m -Xmn年轻代大小m -XX:+PrintGCDetails -Xlog:gc*=debug:file=./log/gcParallel_new.log
```

**参数配置**:

|  参数名字  |       详细配置        |
| :--------: | :-------------------: |
|  操作系统  |      Windows 11       |
|  JDK 版本  | 17.0.2+8-86 (release) |
|    内存    |          16G          |
|    CPU     |          12           |
|   线程数   |          10           |
|   最大堆   |          1G           |
|   最小堆   |          1G           |
| 年轻代大小 |  128M,256M,384M,512M  |

**实验结果如下表所示**:

| 年轻代大小 | 代码运行时间 | GC运行时间 | GC最大延迟 | 吞吐率  | Young GC次数 | Full GC次数 |
| :--------: | :----------: | :--------: | :--------: | :-----: | :----------: | :---------: |
|    128M    |   48355ms    | 459.256ms  |  67.149ms  | 99.059% |      45      |      2      |
|    256M    |   47835ms    |  123.68ms  |  11.498ms  | 99.742% |      17      |      0      |
|    384M    |   47621ms    |  74.260ms  |  12.546ms  | 99.844% |      11      |      0      |
|    512M    |   47722ms    |  69.994ms  |  14.179ms  | 99.854% |      8       |      0      |

**结论如下:**

从表中可以看出，在堆内存不变的情况下，随着年轻的增大，GC的频率显著下降，吞吐率有所提升。但年轻代不是越大越好，当年轻代的大小达到一定阈值后，GC的最大延迟反而回随着年轻代增大而提升，因此需要配置合理的年轻代大小。

### 4.2 幸存区大小对GC性能的影

当年轻代进行GC时，存活对象会先移动到survivor区中，经过多次GC仍然存在于survivor区中的幸存对象会被移动到老年代，当survivor区满时，也会触发GC进行垃圾回收。因此，合理的survivor区大小，能够保留尽可能多的存活对象，减少GC的频率。

**启动命令:**

使用Intellij IDEA运行程序，JVM参数如下:

```
-XX:+UseParallelGC -Xmx1024m -Xms1024m -Xmn256m -XX:SurvivorRatio=存活区与Eden区的比 -XX:+PrintGCDetails -Xlog:gc*=debug:file=./log/gcParallel_survivor_存活区与Eden区的比.log
```

**参数配置**:

|  参数名字  |       详细配置        |
| :--------: | :-------------------: |
|  操作系统  |      Windows 11       |
|  JDK 版本  | 17.0.2+8-86 (release) |
|    内存    |          16G          |
|    CPU     |          12           |
|   线程数   |          10           |
|   最大堆   |          1G           |
|   最小堆   |          1G           |
| 年轻代大小 |         256M          |

**实验结果如下表所示**:

| survivor区:Eden区 | 代码运行时间 | GC运行时间 | GC最大延迟 | 吞吐率  | Young GC次数 | Full GC次数 |
| :---------------: | :----------: | :--------: | :--------: | :-----: | :----------: | :---------: |
|        2:4        |   47705ms    | 179.447ms  |  67.149ms  | 99.625% |      23      |      0      |
|        2:6        |   47935ms    | 139.860ms  |  15.785ms  | 99.709% |      15      |      0      |
|        2:8        |   47438ms    | 109.087ms  |  26.049ms  | 99.771% |      14      |      0      |
|       2:10        |   47736ms    | 112.413ms  |  13.562ms  | 99.765% |      14      |      0      |

**结论如下:**

从表中可以看出，survivor对GC性能的影响不大，但考虑到survivor与eden区共享年轻代的内存，为了保证eden有充足的空间防止频繁的进行Young GC，survivor大小应该小于eden。

### 4.3 堆内存大小对GC性能的影响

堆空间决定了年轻代和老年代的可分配空间，当堆空间较小时，JVM需要频繁的进行GC释放堆空间，合理的堆空间有助于提高GC的性能。

**为了方便实验将代码修改如下:**

```java
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * GC测试用例
 */
public class TestGC {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("=========================GC测试用例=========================");
        long start= System.currentTimeMillis();
        List<byte[]> list = new ArrayList<>();
        int maxIterations = 3000;
        for(int i=1;i<=maxIterations;i++){
            //新增1M
            list.add(new byte[10*1024*1024]);
            //每隔100 clear一次
            if(i%100==0){
                list.clear();
                System.out.printf("iteration:%5d\t\t清空List\n",i);
            }
            //休眠10ms
            Thread.sleep(10);
        }
        long end= System.currentTimeMillis();
        System.out.printf("耗费时间"+(end-start)+'s');
        System.out.println("测试完成");
    }
}
```



**启动命令:**

使用Intellij IDEA运行程序，JVM参数如下:

```
-XX:+UseParallelGC -Xmx堆内存m -Xms堆内存m -Xmn256m -XX:+PrintGCDetails -Xlog:gc*=debug:file=./log/gcParallel_heap_堆内存.log
```

**参数配置**:

|  参数名字  |       详细配置        |
| :--------: | :-------------------: |
|  操作系统  |      Windows 11       |
|  JDK 版本  | 17.0.2+8-86 (release) |
|    内存    |          16G          |
|    CPU     |          12           |
|   线程数   |          10           |
|   最大堆   |      2G,3G,4G,8G      |
|   最小堆   |      2G,3G,4G,8G      |
| 年轻代大小 |         256M          |

**实验结果如下表所示**:

| 堆内存大小 | 代码运行时间 | GC运行时间 | GC最大延迟 | 吞吐率  | Young GC次数 | Full GC次数 |
| :--------: | :----------: | :--------: | :--------: | :-----: | :----------: | :---------: |
|     2G     |   53112ms    | 5267.310ms | 123.484ms  | 90.977% |     162      |     31      |
|     3G     |   51736ms    | 3962.964ms | 185.612ms  | 92.885% |     161      |     20      |
|     4G     |   52495ms    | 4651.435ms | 299.785ms  | 91.860% |     164      |     26      |
|     8G     |   53338ms    | 5396.496ms | 813.341ms  | 90.812% |     166      |     22      |

**结论如下:**

堆空间存在一个最优大小，不能无限的增大，在没发生堆溢出的情况下，Young GC的次数取决于年轻代的大小，与堆空间无关；堆空间主要影响Full GC的频率。

### 4.4 线程数对GC性能的影响

Parallel GC采用多线程的方式进行GC，提高线程的数量，可以充分利用CPU的资源，改善GC的效率。

**启动命令:**

使用Intellij IDEA运行程序，JVM参数如下:

```
-XX:+UseParallelGC -Xmx2048m -Xms2048m -Xmn256m -XX:ParallelGCThreads=线程数 -XX:+PrintGCDetails -Xlog:gc*=debug:file=./log/gcParallel_parallel_12.log 
```

**参数配置**:

|  参数名字  |       详细配置        |
| :--------: | :-------------------: |
|  操作系统  |      Windows 11       |
|  JDK 版本  | 17.0.2+8-86 (release) |
|    内存    |          16G          |
|    CPU     |          12           |
|   线程数   |       6,8,10,12       |
|   最大堆   |          2G           |
|   最小堆   |          2G           |
| 年轻代大小 |         256M          |

**实验结果如下表所示**:

| 线程数 | 代码运行时间 | GC运行时间 | GC最大延迟 | 吞吐率  | Young GC次数 | Full GC次数 |
| :----: | :----------: | :--------: | :--------: | :-----: | :----------: | :---------: |
|   6    |   53155ms    | 5211.111ms | 118.715ms  | 91.072% |     164      |     31      |
|   8    |   53067ms    | 5172.987ms | 118.895ms  | 91.118% |     164      |     31      |
|   10   |   52949ms    | 5187.480ms | 125.105ms  | 91.077% |     132      |     31      |
|   12   |   52892ms    | 5197.726ms | 121.270ms  | 91.052% |     162      |     31      |

**结论如下:**

从实验结果可以看出，线程数对GC性能影响并不明显，在年轻代和堆空间合理的情况下，不同线程数的GC性能差距不大。

## 5. 结论

对Parallel GC性能影响最大的是年轻代和堆空间的大小，在实际生产中应该针对这两部分进行优化。

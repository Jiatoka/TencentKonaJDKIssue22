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

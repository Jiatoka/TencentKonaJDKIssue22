/**
 * 优化后的GC测试用例
 */
public class Main {
    public static void PrintMem(String log){
        System.out.println("============="+log+"=============");
        System.out.println("Xmx=" + Runtime.getRuntime().maxMemory() / 1024.0 / 1024 + "M");     //系统的最大空间
        System.out.println("free mem=" + Runtime.getRuntime().freeMemory() / 1024.0 / 1024 + "M");   //系统的空闲空间
        System.out.println("total mem=" + Runtime.getRuntime().totalMemory() / 1024.0 / 1024 + "M");   //当前可用的总空间
    }
    public static void main(String[] args) {
        System.out.println("Hello world!");
        PrintMem("初始化打印内存");
        byte[] b = new byte[10 * 1024 * 1024];
        System.out.println("分配了100M空间给数组");
        PrintMem("对象使用中");
        System.gc();
        PrintMem("第一次GC");
        b=null;
        PrintMem("对象不再使用后");
        System.gc();
        PrintMem("第二次GC");

    }
}
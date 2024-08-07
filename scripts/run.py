import matplotlib.pyplot as plt
import numpy as np
import argparse
import re
gc_pattern=r'\[gc\s+\]'
def GCSummary(data):
    '''
    计算GC运行时间
    '''
    res=0
    pattern=r'M\)\s+(.*?)ms'
    for line in data:
        if re.search(gc_pattern,line):
            if "Using" in line:
                continue
            if "ms" not in line:
                continue
            gc_time=float(re.findall(pattern,line)[0])
            res+=gc_time
    return res
def GCMax(data):
    '''
    计算GC最大延迟
    '''
    res=-1
    pattern=r'M\)\s+(.*?)ms'
    for line in data:
        if re.search(gc_pattern,line):
            if "Using" in line:
                continue
            if "ms" not in line:
                continue
            gc_time=float(re.findall(pattern,line)[0])
            res=max(gc_time,res)
    return res
def Runtime(data):
    '''
    计算程序运行时间
    '''
    line=data[-1]
    pattern=r'\[(.*?)s\]'
    gc_time=float(re.findall(pattern,line)[0])
    return gc_time
def YoungGC(data):
    '''
    计算young GC次数
    '''
    res=0
    pattern=r'GC\((.*?)\)'
    gc_list=[]
    for line in data:
        if re.search(gc_pattern,line):
            if "Pause Young" in line:
                res+=1
                gc_list.append(re.findall(pattern,line))
            if "ms" not in line:
                continue
    return res,gc_list
def FullGC(data):
    '''
    计算young GC次数
    '''
    res=0
    pattern=r'GC\((.*?)\)'
    gc_list=[]
    for line in data:
        if re.search(gc_pattern,line):
            if "Pause Full" in line:
                res+=1
                gc_list.append(re.findall(pattern,line))
            if "ms" not in line:
                continue
    return res,gc_list
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument("--log",type=str,help="日志路径")
    args=parser.parse_args()
    log_path=args.log
    with open(f"{log_path}","r") as f:
        data=f.readlines()
        gc_summary=GCSummary(data)
        gc_max=GCMax(data)
        runtime=Runtime(data)
        young_gc_num,young_gc_list=YoungGC(data)
        fullgc_num,full_gc_list=FullGC(data)
        print("==========================================")
        print(f'''Runtime:{runtime*1000}ms\t\tGCSummary:{gc_summary}ms\nGCMax:{gc_max}ms\t\tRatio:{runtime*1000/(gc_summary+runtime*1000)*100}%\nYoung GC NUM:{young_gc_num}\t\tYong GC:{young_gc_list}\nFull GC NUM:{fullgc_num}次\t\tFUll GC:{full_gc_list}''')
    

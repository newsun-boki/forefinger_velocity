from multiprocessing import Process,Queue
def fun2(q,i):
    print('子进程%s 开始put数据' %i)
    print(q.get())
def fun1(q,i):
    while True:
        fun2(q,i)

if __name__ == '__main__':
    q = Queue()

    process_list = []
    for i in range(3):
        p = Process(target=fun1,args=(q,i,))  #注意args里面要把q对象传给我们要执行的方法，这样子进程才能和主进程用Queue来通信
        p.start()
        process_list.append(p)
        q.put([3,3,5])

    for i in process_list:
        p.join()

    print('主进程获取Queue数据')
    # print(q.get())
    # print(q.get())
    # print(q.get())
    print('结束测试')
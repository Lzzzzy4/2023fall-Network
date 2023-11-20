# 计算机网络Lab2实验报告

### PB21000164 来泽远

## 实验目的

本实验需要实现一个搭建在OpenNetLab上的使用GBN协议的发送端。这个发送端需 要将一个字符串中的每个字符封装为分组发送给接收端，并且遵循GBN协议：

- 开始时发送滑动窗口内所有可以发送的分组。
- 每发送一个分组，保存该分组在缓冲区中，表示已发送但还未被确认。
- 缓冲区使用一个定时器，当定时器超时的时候，重新发送缓冲区中的所有分组。
- 当收到接收方的确认后，判断该确认是否有效。如果无效的话，什么也不做；如果 有效的话，采取累计确认，移动滑动窗口，将已经被确认的分组从缓冲区中删除， 并且发送接下来可以发送的分组，重置定时器。

## 代码展示

```python
def put(self, packet: Packet):
        ackno = packet.packet_id
        i=self.pos_ack(ackno)
        if i >= 0:
            for j in range(0,i+1):
                self.outbound.popleft()
                self.seqno_start = (self.seqno_start + 1) % self.seqno_range
        self.send_available()

        if len(self.outbound) == 0 and self.absno == len(self.message):
            self.finish_channel.put(True)

    def send_available(self):
        if(self.window_size > len(self.outbound)):
            for i in range(0,self.window_size - len(self.outbound)):
                if(self.absno == len(self.message)):
                    break  
                p = self.new_packet(self.seqno,self.message[self.absno])
                self.seqno = (self.seqno + 1) % self.seqno_range
                self.outbound.append(p)
                self.send_packet(p)
                self.absno += 1
        self.timer.restart(self.timeout)
        
        pass
    
    def timeout_callback(self):
        self.dprint("timeout")
        for i in range(0,len(self.outbound)):
            self.send_packet(self.outbound[i])
```

当从接收端收到Ack时调用put函数，我们根据`packet_id`找到在滑动窗口中的位置，然后移动滑动窗口，即修改`seqno_start`，清理缓存区`outbound`。并且将滑动窗口中没有发送的分组发送。注意在send_available函数中重设定时器，在put函数中不用重设定时器。最后我们检查是否完成发送，即所有分组均被发送且被确认，分别检查`outbound`和`absno`即可。

在send_available函数中，我们需要把滑动窗口中未发送的分组都发送，并且将发送的分组加入`outbound`缓存中。同时需要维护`seqno`和`absno`两个变量，一个是循环+1，一个直接+1。在函数的最后，重设计时器。

在timeout_callback函数中，需要做的就是重发移动窗口中所有的分组，也可以认为就是重发`outbound`中所有的分组。

## 测试结果

本地测试

![image-20231120143937738](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20231120143937738.png)

oj测试

![image-20231120144013680](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20231120144013680.png)


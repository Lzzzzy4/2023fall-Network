from typing import Deque
from collections import deque
from onl.packet import Packet
from onl.device import Device, OutMixIn
from onl.sim import Environment, Store
from onl.utils import Timer


class GBNSender(Device, OutMixIn):
    def __init__(
        self,
        env: Environment,
        seqno_width: int,
        timeout: float,
        window_size: int,
        message: str,
        debug: bool = False,
    ):
        self.env = env
        # the bits of the sequence number, which decides the sequence
        self.seqno_width = seqno_width
        # number range and window size of GBN
        self.seqno_range = 2**self.seqno_width
        self.window_size = window_size
        assert self.window_size <= self.seqno_range - 1
        self.timeout = timeout
        self.debug = debug
        self.message = message
        # the sequence number of the next character to be sent
        self.seqno = 0
        # the absolute index of the next character to be sent
        self.absno = 0
        # sequence number of first packet in outbound buffer
        self.seqno_start = 0
        # packet buffer to save the packets that havn't been acknowledged by receiver
        self.outbound: Deque[Packet] = deque()
        # use `self.finish_channel.put(True)` to terminate the sending process
        self.finish_channel: Store = Store(env)
        # A timer. Call the timeout_callback function when timeout occurs
        self.timer = Timer(
            self.env,
            self.timeout,
            auto_restart=True,
            timeout_callback=self.timeout_callback,
        )
        self.proc = env.process(self.run(env))

    def new_packet(self, seqno: int, data: str) -> Packet:
        return Packet(time=self.env.now, size=40, packet_id=seqno, payload=data)

    def send_packet(self, packet: Packet):
        self.dprint(f"send {packet.payload} on seqno {packet.packet_id}")
        assert self.out
        self.out.put(packet)

    def run(self, env: Environment):
        self.send_available()
        print("A")
        yield self.finish_channel.get()

    def put(self, packet: Packet):
        """从接收端收到ACK
        TODO: 
        （1）检查收到的ACK
        （2）采取累积确认，移动滑动窗口，并发送接下来可以发送的分组
        （3）重置定时器: self.timer.restart(self.timeout)
        （4）检查是否发送完message，若发送完毕则告知结束: self.finish_channel.put(True)
        """
        ackno = packet.packet_id
        print(ackno)
        i = 0
        for i in range(0,len(self.outbound)):
            if ackno == self.outbound[i].packet_id:
                break
        if i == len(self.outbound):
            return
        else:
            for j in range (0,i+1):
                self.outbound.popleft()
        # self.seqno_start = self.outbound[0].packet_id
        
        self.send_available()
        self.timer.restart(self.timeout)
        if(self.absno == self.message.__len__ and len(self.outbound) == 0):#all sended and acked
            self.finish_channel.put(True)
        return

    def send_available(self):
        """
        TODO: 
        （1）检查滑动窗口是否已满，来产生分组并发送（发送滑动窗口内所有可以发送的分组）
        （2）每发送一个分组，保存该分组在缓冲区中，表示已发送但还未被确认
        （3）记得在规定的时机重置定时器: self.timer.restart(self.timeout)
        通过`self.finish_channel.get()`获取状态
        即当`self.finish_channel.put(True)`时发送端模拟结束
        """
        if(self.window_size == len(self.outbound)):
            return
        else:
            for i in range(0,self.window_size - len(self.outbound)):
                if(self.absno == len(self.message)):
                    break
                p = self.new_packet(self.absno,self.message[self.absno])
                self.outbound.append(p)
                self.send_packet(p)
                self.absno = self.absno + 1
        self.timer.restart(self.timeout)
        # if(self.finish_channel.get() == True):
            
        pass
    
    def timeout_callback(self):
        while 1:
            pass
        self.dprint("timeout")
        """
        TODO: 
        （1）超时重传所有已发送但还未被确认过的分组
        （2）注意这个函数结束会自动重置定时器，不用手动重置
        """
        for i in range(0,len(self.outbound)):
            self.send_packet(self.outbound[i])

    def dprint(self, s):
        if self.debug:
            print(f"[sender](time: {self.env.now:.2f})", end=" -> ")
            print(s)

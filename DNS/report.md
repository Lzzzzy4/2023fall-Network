# 计算机网络Lab1实验报告

### PB21000164 来泽远

## 实验目的

本实验需要实现一个搭建在OpenNetLab上的DNS服务器，该服务 器具备以下功能：

- 拦截特定域名
- 返回域名对应的IP地址

## 代码展示

```python
def recv_callback(self, data: bytes):
        recvdp = DNSPacket(data)
        if recvdp.qtype >= 0:
            if recvdp.name in self.url_ip:
                if self.url_ip[recvdp.name] == "0.0.0.0":
                    senddp = recvdp.generate_response(self.url_ip[recvdp.name], True)
                else:
                    senddp = recvdp.generate_response(self.url_ip[recvdp.name], False)
            else:
                senddp = recvdp.generate_request(recvdp.name)
            
            self.send(senddp)
        pass
```

首先，我们把收到的数据转化为DNS数据包，然后我们需要判断该数据包是否为一个请求。

若是，我们再根据其请求名字判断是否在本地配置文件中。如果ip为`0.0.0.0`则为非法，将`intercepted`标记为`true`代表拦截；否则，返回对应的ip值。如果不在本地配置文件中，则向公网DNS服务器返送请求，并且将收到的应答返回给客户端。

## 测试结果

本地测试

![image-20231120143234297](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20231120143234297.png)

oj测试

![image-20231120143355551](C:\Users\lenovo\AppData\Roaming\Typora\typora-user-images\image-20231120143355551.png)


# **CheeseSignal**

一款简单的信号系统。

## **示例**

### **基础用法**

```python
from CheeseSignal import Signal

signal = Signal()

def handle_1():
    print('Handler 1 executed')
signal.connect(handle_1)

@signal.connect()
def handle_2():
    print('Handler 2 executed')

if __name__ == '__main__':
    signal.send()
```

### **异步用法**

```python
import asyncio

from CheeseSignal import Signal

signal = Signal()

async def handle_1():
    print('Handler 1 executed')
signal.connect(handle_1)

@signal.connect()
async def handle_2():
    print('Handler 2 executed')

if __name__ == '__main__':
    asyncio.run(signal.async_send())
```

### **期望接收数与自动删除**

```python
from CheeseSignal import Signal

signal = Signal()

@signal.connect(receive_num_expected = 3)
def handle_1():
    print('Handler 1 executed')

@signal.connect(receive_num_expected = 3, auto_remove = True)
def handle_2():
    print('Handler 2 executed')

if __name__ == '__main__':
    for i in range(5):
        signal.send()
        print(list(signal.receivers.keys()))
```

## **更多...**

### 1. [**Signal**](https://github.com/CheeseUnknown/CheeseSignal/blob/master/documents/Signal.md)

### 2. [**Receiver**](https://github.com/CheeseUnknown/CheeseSignal/blob/master/documents/Receiver.md)

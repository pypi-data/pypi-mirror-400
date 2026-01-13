import uuid, concurrent.futures, asyncio, threading
from typing import Callable, Iterable, overload, Literal
from collections import OrderedDict

class Receiver:
    __slots__ = ('_key', 'fn', 'run_type', '_receive_num_expected', 'auto_remove', '_receive_num')

    def __init__(self, fn: Callable, key: str | None = None, *, run_type: Literal['SEQUENTIAL', 'PARALLEL', 'NO_BLOCK'] = 'SEQUENTIAL', receive_num_expected: int = 0, auto_remove: bool = False):
        '''
        - Args
            - fn: 接收函数
            - key: 若不设置则自动生成一个uuid格式的字符串
            - run_type: 运行方式
                - SEQUENTIAL: 顺序执行，等待函数执行完成后再执行下一个函数
                - PARALLEL: 并行执行，等待所有函数执行完成后再继续
                - NO_BLOCK: 非阻塞执行，函数在后台执行，不等待函数执行完成
            - receive_num_expected: 期望接收总数
            - auto_remove: 是否在达到期望接收总数后自动移除接收器
        '''

        self._key: str = key or str(uuid.uuid4())
        self.fn: Callable = fn
        self.run_type: Literal['SEQUENTIAL', 'PARALLEL', 'NO_BLOCK'] = run_type
        '''
        运行方式
        - SEQUENTIAL: 顺序执行，等待函数执行完成后再执行下一个函数
        - PARALLEL: 并行执行，等待所有函数执行完成后再继续
        - NO_BLOCK: 非阻塞执行，函数在后台执行，不等待函数执行完成
        '''
        self._receive_num_expected: int = receive_num_expected
        ''' 期望接收总数 '''
        self.auto_remove: bool = auto_remove
        ''' 是否在达到期望接收总数后自动移除接收器 '''

        self._receive_num: int = 0
        ''' 接收总数 '''

    def reset(self):
        ''' 重置统计数据 '''

        self._receive_num = 0

    @property
    def key(self) -> str:
        return self._key

    @property
    def receive_num(self) -> int:
        ''' 接收总数 '''

        return self._receive_num

    @property
    def receive_num_expected(self) -> int:
        ''' 期望接收总数 '''

        return self._receive_num_expected

    @property
    def receive_num_remaining(self) -> int | None:
        ''' 剩余接收总数 '''

        return self._receive_num_expected - self._receive_num if self._receive_num_expected > 0 else None

    @property
    def is_active(self) -> bool:
        ''' 是否处于激活状态 '''

        return self._receive_num_expected == 0 or self.receive_num_remaining > 0

class Signal:
    __slots__ = ('receivers', '_send_num')

    def __init__(self):
        '''
        - Examples
```python
""" 基础用法 """
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


""" 异步用法 """
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


""" 期望接收数与自动删除 """
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
'''

        self.receivers: OrderedDict[str, Receiver] = OrderedDict()
        ''' 连接的接收器'''
        self._send_num: int = 0
        ''' 发送总数 '''

    @overload
    def get_receiver(self, key: str) -> Receiver | None:
        ''' 获取接收器 '''

    @overload
    def get_receiver(self, fn: Callable) -> Receiver | None:
        ''' 获取接收器 '''

    def get_receiver(self, arg: str | Callable) -> Receiver | None:
        if type(arg) == str:
            return self.receivers.get(arg, None)
        elif callable(arg):
            for receiver in self.receivers.values():
                if receiver.fn == arg:
                    return receiver

    def _connect(self, fn: Callable, key: str | None = None, *, index: int = -1, insert: tuple[str | Callable | Receiver, Literal['BEFORE', 'AFTER']] | None = None, run_type: Literal['SEQUENTIAL', 'PARALLEL', 'NO_BLOCK'] = 'SEQUENTIAL', receive_num_expected: int = 0, auto_remove: bool = False):
        if key in self.receivers:
            raise ValueError(f'Receiver "{key}" already exists')

        receiver = Receiver(fn, key, run_type = run_type, receive_num_expected = receive_num_expected, auto_remove = auto_remove)
        items = list(self.receivers.items())
        if index > -1:
            items.insert(index, (receiver.key, receiver))
            self.receivers.clear()
            self.receivers.update(items)
        elif insert:
            if isinstance(insert[0], Receiver):
                key = insert[0].key
                if key not in self.receivers:
                    raise ValueError(f'Receiver "{key}" does not exist')
            elif callable(insert[0]):
                _receiver = self.get_receiver(insert[0])
                if not _receiver:
                    raise ValueError(f'Receiver "{insert[0]}" does not exist')
                key = _receiver.key
            elif isinstance(insert[0], str):
                key = insert[0]
                if key not in self.receivers:
                    raise ValueError(f'Receiver "{key}" does not exist')

            for i, (_key, _) in enumerate(items):
                if _key == key:
                    if insert[1] == 'BEFORE':
                        items.insert(i, (receiver.key, receiver))
                    elif insert[1] == 'AFTER':
                        items.insert(i + 1, (receiver.key, receiver))
                    break
        else:
            self.receivers[receiver.key] = receiver

    @overload
    def connect(self, fn: Callable, key: str | None = None, *, index: int = -1, insert: tuple[str | Callable | Receiver, Literal['BEFORE', 'AFTER']] | None = None, run_type: Literal['SEQUENTIAL', 'PARALLEL', 'NO_BLOCK'] = 'SEQUENTIAL', receive_num_expected: int = 0, auto_remove: bool = False):
        '''
        连接接收器

        - Args
            - key: 接收器键值，若不设置则自动生成一个uuid格式的字符串
            - run_type: 运行类型
                - SEQUENTIAL: 顺序执行，等待函数执行完成后再执行下一个函数
                - PARALLEL: 并行执行，等待所有函数执行完成后再继续
                - NO_BLOCK: 非阻塞执行，函数在后台执行，不等待函数执行完成
            - receive_num_expected: 期望接收总数
            - auto_remove: 是否在达到期望接收总数后自动移除接收器
            - index: 插入位置索引（仅对run_type为SEQUENTIAL的接收器有效）
            - insert: 插入位置；若设置index，则忽略此参数（仅对run_type为SEQUENTIAL的接收器有效）
                - BEFORE: 插入到指定接收器之前
                - AFTER: 插入到指定接收器之后

        - Examples
```python
from CheeseSignal import Signal

signal = Signal()

def handler():
    print('Handler executed')
signal.connect(handler)
```
        '''

    @overload
    def connect(self, key: str | None = None, *, index: int = -1, insert: tuple[str | Callable | Receiver, Literal['BEFORE', 'AFTER']] | None = None, run_type: Literal['SEQUENTIAL', 'PARALLEL', 'NO_BLOCK'] = 'SEQUENTIAL', receive_num_expected: int = 0, auto_remove: bool = False):
        '''
        连接接收器

        - Args
            - key: 接收器键值，若不设置则自动生成一个uuid格式的字符串
            - run_type: 运行类型
                - SEQUENTIAL: 顺序执行，等待函数执行完成后再执行下一个函数
                - PARALLEL: 并行执行，等待所有函数执行完成后再继续
                - NO_BLOCK: 非阻塞执行，函数在后台执行，不等待函数执行完成
            - receive_num_expected: 期望接收总数
            - auto_remove: 是否在达到期望接收总数后自动移除接收器
            - index: 插入位置索引（仅对run_type为SEQUENTIAL的接收器有效）
            - insert: 插入位置；若设置index，则忽略此参数（仅对run_type为SEQUENTIAL的接收器有效）
                - BEFORE: 插入到指定接收器之前
                - AFTER: 插入到指定接收器之后

        - Examples
```python
from CheeseSignal import Signal

signal = Signal()

@signal.connect()
def handler():
    print('Handler executed')
```
        '''

    def connect(self, arg1: Callable | str | None = None, *args, index: int = -1, insert: tuple[str | Callable | Receiver, Literal['BEFORE', 'AFTER']] | None = None, run_type: Literal['SEQUENTIAL', 'PARALLEL', 'NO_BLOCK'] = 'SEQUENTIAL', receive_num_expected: int = 0, auto_remove: bool = False):
        if callable(arg1):
            self._connect(arg1, *args, index = index, insert = insert, run_type = run_type, receive_num_expected = receive_num_expected, auto_remove = auto_remove)
        else:
            def decorator(fn: Callable):
                self._connect(fn, arg1, index = index, insert = insert, run_type = run_type, receive_num_expected = receive_num_expected, auto_remove = auto_remove)
                return fn
            return decorator

    @overload
    def disconnect(self, key: str):
        ''' 断开接收器 '''

    @overload
    def disconnect(self, fn: Callable):
        ''' 断开接收器 '''

    @overload
    def disconnect(self, receiver: Receiver):
        ''' 断开接收器 '''

    def disconnect(self, arg):
        if isinstance(arg, str):
            key = arg
            if key in self.receivers:
                del self.receivers[key]
        elif callable(arg):
            for key in [key for key, receiver in self.receivers.items() if receiver.fn == arg]:
                del self.receivers[key]
        elif isinstance(arg, Receiver):
            if arg.key in self.receivers:
                del self.receivers[arg.key]

    def disconnect_all(self):
        ''' 断开所有接收器 '''

        self.receivers.clear()

    def reset(self):
        ''' 重置统计数据 '''

        self._send_num = 0
        for receiver in self.receivers.values():
            receiver.reset()

    @overload
    def send(self, key: str, *, args: tuple[any, ...], kwargs: dict[str, any]):
        '''
        发送信号

        - Args
            - args: *args参数
            - kwargs: **kwargs参数
        '''

    @overload
    def send(self, keys: Iterable[str], *, args: tuple[any, ...], kwargs: dict[str, any]):
        '''
        发送信号

        - Args
            - args: *args参数
            - kwargs: **kwargs参数
        '''

    @overload
    def send(self, *, args: tuple[any, ...], kwargs: dict[str, any]):
        '''
        发送信号

        - Args
            - args: *args参数
            - kwargs: **kwargs参数
        '''

    def send(self, arg: str | list[str] | None = None, **kwargs):
        if arg is None:
            arg = self.receivers.keys()
        elif type(arg) == str:
            arg = [arg]

        self._send_num += 1

        sequential_receivers = [self.receivers[key] for key in arg if key in self.receivers and self.receivers[key].run_type == 'SEQUENTIAL' and self.receivers[key].is_active]
        if sequential_receivers:
            for receiver in sequential_receivers:
                self._send_handle(receiver, **kwargs)

        parallel_receivers = [self.receivers[key] for key in arg if key in self.receivers and self.receivers[key].run_type == 'PARALLEL' and self.receivers[key].is_active]
        if parallel_receivers:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(parallel_receivers)) as executor:
                futures = [executor.submit(self._send_handle, receiver, **kwargs) for receiver in parallel_receivers]
                for future in concurrent.futures.as_completed(futures):
                    future.result()

        noBlock_receivers = [self.receivers[key] for key in arg if key in self.receivers and self.receivers[key].run_type == 'NO_BLOCK' and self.receivers[key].is_active]
        if noBlock_receivers:
            for receiver in noBlock_receivers:
                thread = threading.Thread(target=self._send_handle, args = (receiver,), kwargs = kwargs, daemon = True)
                thread.start()

    def _send_handle(self, receiver: Receiver, **kwargs):
        receiver.fn(*kwargs.get('args', ()), **kwargs.get('kwargs', {}))
        receiver._receive_num += 1
        if receiver.auto_remove and not receiver.is_active:
            self.disconnect(receiver.key)

    @overload
    def async_send(self, key: str, *, args: tuple[any, ...], kwargs: dict[str, any]):
        '''
        发送信号

        - Args
            - args: *args参数
            - kwargs: **kwargs参数
        '''

    @overload
    def async_send(self, keys: Iterable[str], *, args: tuple[any, ...], kwargs: dict[str, any]):
        '''
        发送信号

        - Args
            - args: *args参数
            - kwargs: **kwargs参数
        '''

    @overload
    def async_send(self, *, args: tuple[any, ...], kwargs: dict[str, any]):
        '''
        发送信号

        - Args
            - args: *args参数
            - kwargs: **kwargs参数
        '''

    async def async_send(self, arg: str | list[str] | None = None, **kwargs):
        if arg is None:
            arg = self.receivers.keys()
        elif type(arg) == str:
            arg = [arg]

        self._send_num += 1

        sequential_receivers = [self.receivers[key] for key in arg if key in self.receivers and self.receivers[key].run_type == 'SEQUENTIAL' and self.receivers[key].is_active]
        if sequential_receivers:
            for receiver in sequential_receivers:
                await self._async_send_handle(receiver, **kwargs)

        parallel_receivers = [self.receivers[key] for key in arg if key in self.receivers and self.receivers[key].run_type == 'PARALLEL' and self.receivers[key].is_active]
        if parallel_receivers:
            await asyncio.gather(*[asyncio.create_task(self._async_send_handle(receiver, **kwargs)) for receiver in parallel_receivers])

        noBlock_receivers = [self.receivers[key] for key in arg if key in self.receivers and self.receivers[key].run_type == 'NO_BLOCK' and self.receivers[key].is_active]
        if noBlock_receivers:
            for receiver in noBlock_receivers:
                asyncio.create_task(self._async_send_handle(receiver, **kwargs))

    async def _async_send_handle(self, receiver: Receiver, **kwargs):
        await receiver.fn(*kwargs.get('args', ()), **kwargs.get('kwargs', {}))
        receiver._receive_num += 1
        if receiver.auto_remove and receiver.receive_num_remaining == 0:
            self.disconnect(receiver.key)

    @property
    def send_num(self) -> int:
        ''' 发送总数 '''

        return self._send_num

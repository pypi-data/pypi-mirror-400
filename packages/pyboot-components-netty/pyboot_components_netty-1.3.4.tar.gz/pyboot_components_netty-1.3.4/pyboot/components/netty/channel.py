
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
from pyboot.commons.utils.bytes import ByteBuffer,ByteBufAllocator,PooledByteBufferAllocator
from typing import Optional
from pyboot.commons.utils.log import Logger
from pyboot.commons.coroutine.task import CoroutineWorkGroup
import socket
import struct
from pyboot.commons.utils.utils import isWin,str2Num
from typing import TypeVar, Generic


_logger = Logger('pyboot.components.netty.channel')

class ChannelOption(Enum):
    SO_REUSEADDR='SO_REUSEADDR'
    SO_KEEPALIVE='SO_KEEPALIVE'
    SO_BACKLOG='SO_BACKLOG'
    TCP_NODELAY='TCP_NODELAY'
    ALLOCATOR='ALLOCATOR'
    WRITE_BUFFER_WATER_MARK='WRITE_BUFFER_WATER_MARK'
    SO_SNDBUF='SO_SNDBUF'
    SO_RCVBUF='SO_RCVBUF'
    SO_LINGER='SO_LINGER'
    SO_CHUNKSIZE='SO_CHUNKSIZE'
    SO_TIMEOUT='SO_TIMEOUT'

# @dataclass
# class ChannelConfig:
#     """Channel 配置"""
#     read_idle_timeout: int = 30
#     write_idle_timeout: int = 30
#     all_idle_timeout: int = 60
#     auto_read: bool = True
#     write_buffer_high_water_mark: int = 64 * 1024
#     write_buffer_low_water_mark: int = 32 * 1024


class ChannelEvent(Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    EXCEPTION_CAUGHT = "EXPCETION_CAUGHT"
    READ_IDLE = "READ_IDLE"
    WRITE_IDLE = "WRITE_IDLE"
    READ_DO = "READ_DO"
    WRITE_DO = "WRITE_DO"
    UDF_EVENT = "UDF_EVENT"
    # ADD = "HANDLE_ADD"
    # REMOVE = "HANDLE_REMOVE"
    
# 在子类里扩展
# class UDFChannelEvent(ChannelEvent): ...

class NettyBaseError(BaseException):
    def __init__(self, msg: str = "", cause:BaseException=None):
        super().__init__(msg)   # BaseException 只接受位置参数        
        self._cause = cause
        self.msg = msg
        
    def __repr__(self):
        return f'{super().__repr__()} msg={self.msg} cause={self._cause}'
    
    def __str__(self):
        return f'{super().__str__()} msg={self.msg} cause={self._cause}'

class NetWorkError(IOError): ...
    
class ChannelError(NettyBaseError): ...

class ChannelHandleError(NettyBaseError): ...

class SocketChannel():    
    _channel_counter = 0
    """网络通道"""        
    def __init__(self, reader: asyncio.StreamReader,        
                        writer: asyncio.StreamWriter, attributes:dict[str,any]):
        
        SocketChannel._channel_counter += 1
        self.channel_id = SocketChannel._channel_counter        
        self._channel_option = attributes
                
        self.is_active = False                
        self.bytes_read = 0         
        self.bytes_write = 0
        
        self._reader = reader
        self._writer = writer
        
        if ChannelOption.ALLOCATOR.name in self._channel_option and self._channel_option[ChannelOption.ALLOCATOR.name]:
            pa:PooledByteBufferAllocator = self._channel_option[ChannelOption.ALLOCATOR.name]
            self._pa = pa
            self._write_buffer:ByteBuffer = pa.allocate(str2Num(self._channel_option[ChannelOption.SO_SNDBUF.name]))            
        else:
            self._write_buffer:ByteBuffer = ByteBufAllocator.DIRECT.buffer(str2Num(self._channel_option[ChannelOption.SO_SNDBUF.name]))
                        
        self.w_lock = asyncio.Lock()
        self._pipeline = ChannelPipeline(self)
        
    def __repr__(self):
        return f'{id(self)} channel_id={self.channel_id} address={self.remote_address()} bytes_read={self.bytes_read} bytes_write={self.bytes_write}'
        
    def allocate_bytebuffer(self, size:int=1024)->ByteBuffer:
        if self._pa:
            return self._pa.allocate(size)            
        else:
            return ByteBufAllocator.DIRECT.buffer(size)
        
    def release_bytebuffer(self, buffer:ByteBuffer):
        if buffer:
            if self._pa:
                self._pa.release(buffer)
            else:            
                buffer.destroy()
        
    def setSocketChannelInitializer(self, socketChannelInitializer:'SocketChannelInitializer'):
        self._socketChannelInitializer = socketChannelInitializer
        
    def _channel_Initialize(self):        
        socketChannelInitializer = self._socketChannelInitializer
        
        self._pipeline.add_first(DefaultByteBufferOutboundHandler())
        
        if not socketChannelInitializer:
            _logger.WARN('没有初始化Channel对象，没有数据包可以进行接收处理')
            return
        
        # assert socketChannelInitializer, '不能使用None对象'        
        assert isinstance(socketChannelInitializer, SocketChannelInitializer) or callable(socketChannelInitializer), f'必须是SocketChannelInitializer对象或者def initChannel(self, socketChannel:SocketChannel)方法，但是为{socketChannelInitializer}'
        if isinstance(socketChannelInitializer, SocketChannelInitializer):
            socketChannelInitializer.initChannel(self)
        elif callable(socketChannelInitializer):
            socketChannelInitializer(self)
        else:
            raise ValueError(f'必须是SocketChannelInitializer对象或者def initChannel(self, socketChannel:SocketChannel)方法，但是为{socketChannelInitializer}')
        
    # def setAttributes(self, attributes:dict[str,any]): 
    #     self._channel_option = attributes             
        
    def bind(self, address:tuple[str,int]): ...

    def connect(self, address:tuple[str,int]): ...    
    
    # write data with pipeline
    async def write(self, data: any):
        """写入数据到缓冲区"""
        await self._pipeline.fire_channel_write(data)
        
    # write data directly into socket
    async def write_directlly(self, data:bytes | bytearray | memoryview):        
        if self._writer:            
            await self._pipeline.fire_channel_event(ChannelEvent.WRITE_DO, data)            
            self.bytes_write += len(data)
            self._writer.write(data)
            await self._writer.drain()
            await self._pipeline.fire_channel_write_complete()
            
    async def write_to_bytebuffer(self, data:bytes | bytearray | memoryview):
        async with self.w_lock:
            if self._write_buffer.writable_bytes()>0 and self._writer:
                self._write_buffer.write_byte(data)
                
    async def _flush(self):
        """刷新缓冲区"""
        if self._write_buffer.readable_bytes() > 0 and self._writer:
            data = self._write_buffer.read_bytes(self._write_buffer.readable_bytes())
            self._write_buffer.reset()
            self.bytes_write += len(data)
            self._writer.write(data)                
        await self._writer.drain()
                        
    async def flush(self):
        """刷新缓冲区"""
        async with self.w_lock:
            await self._flush()
            
    async def write_and_flush(self, data: bytes | bytearray | memoryview):
        """写入并立即刷新"""   
        async with self.w_lock:     
            await self.write_directlly(data)
            await self._flush()

    # 业务协程：集成pipeline进行处理
    async def handle_rw(self, reader: asyncio.StreamReader,        
                        writer: asyncio.StreamWriter):
        revchunk = str2Num(self._channel_option['SO_CHUNKSIZE'])                
        try:            
            if ChannelOption.ALLOCATOR.name in self._channel_option and self._channel_option[ChannelOption.ALLOCATOR.name]:
                pa:PooledByteBufferAllocator = self._channel_option[ChannelOption.ALLOCATOR.name]
                _pa = pa                
                _read_buffer:ByteBuffer = pa.allocate(str2Num(self._channel_option[ChannelOption.SO_RCVBUF.name]))
            else:                
                _read_buffer:ByteBuffer = ByteBufAllocator(True).buffer(str2Num(self._channel_option[ChannelOption.SO_RCVBUF.name]))
            
            await self._pipeline.fire_channel_active()
            
            while self.is_active:                              
                chunk = await reader.read(revchunk)
                if not chunk:
                    break
                
                _read_buffer.compact()                
                """处理读缓冲区中的数据"""
                if _read_buffer.readable_bytes():
                    _logger.WARN(f'缓存空间已经溢出, 缓冲池里丢弃{_read_buffer.readable_bytes()}个字节数据，请检查是否正确处理读取字节')
                    _read_buffer.clear()
                    
                self.bytes_read += len(chunk)
                _read_buffer.write_bytes(chunk)
                
                try:
                    await self._pipeline.fire_channel_event(ChannelEvent.READ_DO,chunk)
                    await self._pipeline.fire_channel_read(_read_buffer)
                    await self._pipeline.fire_channel_read_complete()
                except ChannelHandleError as e:
                    if _logger.canDebug():
                        _logger.DEBUG(f'处理数据发生异常{e}')
                    await self._pipeline.fire_exception_caught(e)
                except ChannelError as e:
                    if _logger.canDebug():
                        _logger.DEBUG(f'Channel发生异常{e}')
                    raise e
                
        except GeneratorExit:
            if _logger.canDebug():
                _logger.DEBUG("取消任务，关闭客户端")
            raise                
        except asyncio.IncompleteReadError as e:
            if _logger.canDebug():
                _logger.DEBUG(f"关闭客户端读通道{e}")
        except BaseException as e:            
            raise e
        finally:            
            if _pa:
                _pa.release(_read_buffer)
            else:
                _read_buffer.destroy()
            pass    
        
    # # 业务协程：echo 回显 + 简单拆包（\n 结尾）
    # async def handle_echo(self, reader: asyncio.StreamReader,        
    #                     writer: asyncio.StreamWriter):
    #     try:
    #         addr = writer.get_extra_info('peername')        
        
    #         while self.is_active:
    #             data = await reader.readline()   # 行协议
    #             line = data.decode()
    #             _logger.DEBUG(f"{addr}:收到数据:{line.strip()}")
    #             if line.strip().upper() == 'CLOSE':
    #                 _logger.DEBUG('收到退出命令，马上退出')
    #                 break               
    #             writer.write(data.upper())
    #             await writer.drain()
    #     except asyncio.IncompleteReadError as e:
    #         _logger.DEBUG(f"关闭客户端{e}")
    #     except GeneratorExit:
    #         raise        
    #     except BaseException as e:
    #         raise e
    #     finally:
    #         pass
    
    async def close(self):
        """关闭 Channel"""                
        if self.is_active:
            try:
                if _logger.canDebug():
                    _logger.DEBUG('开始fire_channel_inactive')
                    
                await self._pipeline.fire_channel_inactive()
                
                self.is_active = False            
                if self._writer:
                    await self.flush()
                    
                    self._writer.close()
                    await self._writer.wait_closed()                
                                    
            except BaseException as e:
                _logger.DEBUG(f'关闭连接异常{e}')
            finally:
                if self._pa:
                    self._pa.release(self._write_buffer)
                else:
                    self._write_buffer.clear()
                
    async def start(self):    
        """在自定义循环中处理连接的函数"""
        try:
            # work_group.submit(handle_echo(r, w))        
            w = self._writer
            r = self._reader
            
            addr = w.get_extra_info('peername')
            sock = w.get_extra_info('socket')  
            
            if self._channel_option[ChannelOption.SO_KEEPALIVE.name]:
                _logger.DEBUG(f'{ChannelOption.SO_KEEPALIVE.name}={self._channel_option[ChannelOption.SO_KEEPALIVE.name]}')
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)                    
                # 设置KeepAlive参数（Linux）
                if hasattr(socket, 'TCP_KEEPIDLE'):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                if hasattr(socket, 'TCP_KEEPINTVL'):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                if hasattr(socket, 'TCP_KEEPCNT'):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)   
            
            if self._channel_option[ChannelOption.TCP_NODELAY.name]:                
                # sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                _logger.DEBUG(f'{ChannelOption.TCP_NODELAY.name}={self._channel_option[ChannelOption.TCP_NODELAY.name]}')
        
            try:
                if self._channel_option[ChannelOption.SO_LINGER.name] and self._channel_option[ChannelOption.SO_LINGER.name] >= 0:
                    v = self._channel_option[ChannelOption.SO_LINGER.name]
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('hh', 1, v) if isWin() else struct.pack('ii', 1, v))     
            except Exception as e:
                _logger.ERROR(f"设置客户端SO_LINGER错误: {e}", e)                              
            _logger.DEBUG(f'开始处理协议通道{addr} reader={r} writer={w} socket={sock}')
            s = sock                   
            # _logger.INFO("服务器配置参数:")
            _logger.INFO(f"SO_REUSEADDR: {s.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)}")                    
            try:
                _logger.INFO(f"SO_KEEPALIVE: {s.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)}")
            except BaseException:
                pass                    
            _logger.INFO(f"SO_SNDBUF: {s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)}")
            _logger.INFO(f"SO_RCVBUF: {s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)}")                    
            try:
                _logger.INFO(f"TCP_NODELAY: {s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)}")
            except BaseException:
                pass
            try:
                _logger.INFO(f"SO_LINGER: {s.getsockopt(socket.SOL_SOCKET, socket.SO_LINGER)}")
            except BaseException as e:
                _logger.ERROR('', e)
                pass
                
            """启动 Channel"""
            self.is_active = True
            self._channel_Initialize()
            
            await self._pipeline.fire_channel_event(ChannelEvent.CONNECTED, r, w)
            
            try:                    
                # await self.handle_echo(r, w)     
                await self.handle_rw(r, w)                
                await self._pipeline.fire_channel_event(ChannelEvent.DISCONNECTED, r, w)
            except (asyncio.exceptions.CancelledError, GeneratorExit):
                pass
            except BaseException as e:
                await self._pipeline.fire_channel_event(ChannelEvent.DISCONNECTED, r, w)
                
                if _logger.canDebug():
                    _logger.ERROR(f'************** {e}', e)
                # await self._pipeline.fire_exception_caught(e)
            finally:                                                
                if _logger.canDebug():
                    _logger.DEBUG(f"关闭客户端{addr}")
                await self.close()
                # w.close()
                # await w.wait_closed()
                
        except BaseException as e:
            if _logger.canError():
                _logger.ERROR(f'处理新客户端出现错误{e}, 断开客户端')
            w.close()
        # await handle_echo(r,w)


    def pipeline(self):
        return self._pipeline
    
    def local_address(self) -> Optional[tuple]:
        if self._writer:
            return self._writer.get_extra_info('sockname')       
        else:
            return None
        
    def socket(self):
        if self._writer:
            return self._writer.get_extra_info('socket')  
        return None
    
    def remote_address(self) -> Optional[tuple]:
        if self._writer:
            return self._writer.get_extra_info('peername')   
        else:
            return None

class SocketChannelInitializer(ABC):
    @abstractmethod
    def initChannel(self, socketChannel:SocketChannel): ...


class ChannelHandlerContext:
    """Channel 上下文，用于在 Handler 之间传递数据"""    
    def __init__(self, channel: 'SocketChannel', pipeline: 'ChannelPipeline'):
        self._channel = channel
        self._pipeline = pipeline        
        self._handler = None
        
    def __repr__(self):
        return f'{id(self)} channel={self.channel} pipeline={self.pipeline} handler={self._handler}'
        
    @property
    def channel(self)->SocketChannel:
        return self._channel
    
    @property
    def pipeline(self)->'ChannelPipeline':
        return self._pipeline
    
    async def fire_channel_read(self, data: any):
        await self._pipeline.fire_channel_read(data, self)
    
    async def fire_channel_write(self, data: any):
        await self._pipeline.fire_channel_write(data, self)
    
    async def fire_exception_caught(self, exception: BaseException):
        await self._pipeline.fire_exception_caught(exception, self)
    
    async def fire_channel_event(self, event: ChannelEvent, *args):
        await self._pipeline.fire_channel_event(event, *args, context=self)
        
    async def fire_channel_active(self):
        await self._pipeline.fire_channel_active(self)
    
    async def fire_channel_inactive(self):
        await self._pipeline.fire_channel_inactive(self)
    
    async def fire_channel_read_complete(self):
        await self._pipeline.fire_channel_read_complete(self)
    
    async def fire_channel_write_complete(self):
        await self._pipeline.fire_channel_write_complete(self)
        
    # async def write_and_flush(self, chunk: bytes | bytearray | memoryview):
    #     await self._channel._pipeline.fire_channel_event(ChannelEvent.WRITE_DO, chunk)        
    #     await self._channel.write_and_flush(chunk)
    #     await self._channel._pipeline.fire_channel_write_complete()
        
T = TypeVar('T')        
K = TypeVar('K')    
L = TypeVar('L')    
M = TypeVar('M')    
N = TypeVar('N')    
P = TypeVar('P')    

T_BYTES_BYTEBUFFER = TypeVar('T', bytes, ByteBuffer, bytearray) 

class ChannelHandler(ABC, Generic[T]):
    """Handler 基类"""    
    async def channel_read(self, ctx: ChannelHandlerContext, data: T):
        await ctx.fire_channel_read(data)
        
    async def channel_read_complete(self, ctx: ChannelHandlerContext):
        await ctx.fire_channel_read_complete()
    
    async def channel_write(self, ctx: ChannelHandlerContext, data: T):
        await ctx.fire_channel_write(data)
    
    async def channel_write_complete(self, ctx: ChannelHandlerContext):
        await ctx.fire_channel_write_complete()
        
    async def channel_active(self, ctx: ChannelHandlerContext):
        await ctx.fire_channel_active()
    
    # @abstractmethod
    async def channel_inactive(self, ctx: ChannelHandlerContext):
        await ctx.fire_channel_inactive()
    
    async def exception_caught(self, ctx: ChannelHandlerContext, exception: BaseException):
        await ctx.fire_exception_caught(exception)
    
    async def channel_event(self, ctx: ChannelHandlerContext, event: ChannelEvent, *args):
        await ctx.fire_channel_event(event, *args)


class DefaultByteBufferOutboundHandler(ChannelHandler[T_BYTES_BYTEBUFFER]):
    async def channel_write(self, ctx: ChannelHandlerContext, data: T_BYTES_BYTEBUFFER):
        if data:            
            if isinstance(data, (bytes, bytearray)):
                await ctx.channel.write_and_flush(data)
            elif isinstance(data, ByteBuffer):
                data:ByteBuffer = data
                _mv = data.get_readable_memoryview()
                data.reset()
                await ctx.channel.write_and_flush(_mv)                
            else:
                if hasattr(data, '__bytes__'):
                    if callable(getattr(data, '__bytes__')):
                        await ctx.channel.write_and_flush(getattr(data, '__bytes__')())
                    else:
                        raise ChannelHandleError(f'对象需要转成bytes，但是当前[{type(data)}]是{data}, 可以添加Handler进行Encode处理')
        else:
            await ctx.channel.flush()
        # await ctx.fire_channel_write(data)
    
    # async def handler_added(self, ctx: ChannelHandlerContext):
    #     """Handler 被添加到 Pipeline 时调用"""
    #     pass
    
    # async def handler_removed(self, ctx: ChannelHandlerContext):
    #     """Handler 从 Pipeline 移除时调用"""
    #     pass

class ChannelPipeline:
    """处理器管道"""    
    def __init__(self, channel: SocketChannel):
        self.channel = channel
        self.handlers: list[ChannelHandler] = []        
        self.contexts: dict[ChannelHandler, ChannelHandlerContext] = {}
    
    def _add_context(self, handler: ChannelHandler):        
        ctx = ChannelHandlerContext(self.channel, self)
        ctx._handler = handler
        self.contexts[handler] = ctx
        
        # 触发 handler_added 事件
        # asyncio.create_task(handler.handler_added(ctx))
        
    def add_handler(self, handler: ChannelHandler) -> 'ChannelPipeline':
        """添加处理器"""        
        self.handlers.append(handler)
        self._add_context(handler)
        
        return self
    
    def add_last(self, handler: ChannelHandler) -> 'ChannelPipeline':
        """添加Last处理器"""        
        self.add_handler(handler)
        
    
    def add_first(self, handler: ChannelHandler) -> 'ChannelPipeline':
        """在开头添加处理器"""
        self.handlers.insert(0, handler)
        self._add_context(handler)
        
        return self
    
    def remove_handler(self, handler: ChannelHandler) -> 'ChannelPipeline':
        """移除处理器"""
        if handler in self.handlers:            
            self.handlers.remove(handler)
            ctx = self.contexts.pop(handler)                                    
            # 触发 handler_removed 事件
            asyncio.create_task(handler.handler_removed(ctx))            
                    
        return self
    
    async def fire_channel_read(self, data: any, current_ctx: Optional[ChannelHandlerContext] = None)->any:
        """触发读取事件"""
        start_index = 0
        if current_ctx:
            try:
                start_index = self.handlers.index(current_ctx._handler) + 1
            except ValueError:
                start_index = 0
        _data = data              
         
        if start_index > len(self.handlers) - 1:
            return
                 
        # for i in range(start_index, len(self.handlers)):
        #     handler = self.handlers[i]            
        #     ctx = self.contexts[handler]
        #     try:
        #         _data_temp = await handler.channel_read(ctx, _data)
        #         if not _data_temp:
        #             break
        #         else:
        #             _data = _data_temp
        #     except BaseException as e:
        #         await self.fire_exception_caught(e, ctx)
        #         _data = None
        #         break
        # return _data
        handler = self.handlers[start_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_read(ctx, _data)
        except ChannelHandleError as e:    
            await self.fire_exception_caught(e)
                            
    
    async def fire_channel_write(self, data: any, current_ctx: Optional[ChannelHandlerContext] = None)->any:
        """触发写入事件"""
        end_index = len(self.handlers) - 1
        if current_ctx:
            try:
                end_index = self.handlers.index(current_ctx._handler) - 1
            except ValueError:
                end_index = len(self.handlers) - 1
        _data = data        
        if end_index < 0:
            return
        # for i in range(end_index, -1, -1):
        #     handler = self.handlers[i]
        #     ctx = self.contexts[handler]
        #     try:
        #         _data_temp = await handler.channel_write(ctx, _data)
        #         if not _data_temp:
        #             break 
        #         else:
        #             _data = _data_temp
        #     except BaseException as e:
        #         await self.fire_exception_caught(e, ctx)
        #         break
        # return _data        
        handler = self.handlers[end_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_write(ctx, _data)
        except ChannelHandleError as e:
            await self.fire_exception_caught(e)
        
    
    async def fire_exception_caught(self, exception: BaseException, current_ctx: Optional[ChannelHandlerContext] = None):
        """触发异常事件"""        
        start_index = 0
        if current_ctx:
            try:
                start_index = self.handlers.index(current_ctx._handler)+1
            except ValueError:
                start_index = 0
        
        if start_index > len(self.handlers) - 1:
            return
        
        # for i in range(start_index, len(self.handlers)):
        #     handler = self.handlers[i]
        #     ctx = self.contexts[handler]
        #     try:
        #         await handler.exception_caught(ctx, exception)
        #         return
        #     except BaseException as e:
        #         _logger.ERROR(f"BaseException in exception handler {handler}: {e}")
        #         continue
        
        handler = self.handlers[start_index] 
        ctx = self.contexts[handler]
        try:
            await handler.exception_caught(ctx, exception)
        except BaseException as e:
            _logger.ERROR(f"BaseException in exception handler {handler}: {e}")
    
    async def fire_channel_event(self, event: ChannelEvent, *args, context: Optional[ChannelHandlerContext] = None):
        """触发 Channel 事件"""
        # _logger.DEBUG(f'触发 Channel 事件 event={event} args={args} context={context}')
        start_index = 0
        if context:
            try:
                start_index = self.handlers.index(context._handler)+1
            except ValueError:
                start_index = 0
        
        if start_index > len(self.handlers) - 1:
            return
        
        # for i in range(start_index, len(self.handlers)):
        #     handler = self.handlers[i]
        #     ctx = self.contexts[handler]
        #     try:
        #         await handler.channel_event(ctx, event, *args)
        #     except BaseException as e:
        #         await self.fire_exception_caught(e, ctx)    
        
        handler = self.handlers[start_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_event(ctx, event, *args)
        except BaseException as e:
            _logger.ERROR(f"BaseException in exception handler {handler}: {e}")
    
    async def fire_channel_active(self, context: Optional[ChannelHandlerContext] = None):        
        start_index = 0
        if context:
            try:
                start_index = self.handlers.index(context._handler)+1
            except ValueError:
                start_index = 0
        
        if start_index > len(self.handlers) - 1:
            return
        
        # for i in range(start_index, len(self.handlers)):
        #     handler = self.handlers[i]
        #     ctx = self.contexts[handler]
        #     try:
        #         await handler.channel_event(ctx, event, *args)
        #     except BaseException as e:
        #         await self.fire_exception_caught(e, ctx)    
        
        handler = self.handlers[start_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_active(ctx)
        except BaseException as e:
            _logger.ERROR(f"BaseException in active handler {handler}: {e}")
            
    async def fire_channel_inactive(self, context: Optional[ChannelHandlerContext] = None):        
        start_index = 0
        if context:
            try:
                start_index = self.handlers.index(context._handler)+1
            except ValueError:
                start_index = 0
        
        if start_index > len(self.handlers) - 1:
            return
        
        # for i in range(start_index, len(self.handlers)):
        #     handler = self.handlers[i]
        #     ctx = self.contexts[handler]
        #     try:
        #         await handler.channel_event(ctx, event, *args)
        #     except BaseException as e:
        #         await self.fire_exception_caught(e, ctx)    
        
        handler = self.handlers[start_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_inactive(ctx)
        except BaseException as e:
            _logger.ERROR(f"BaseException in inactive handler {handler}: {e}")
            
    async def fire_channel_read_complete(self, context: Optional[ChannelHandlerContext] = None):        
        start_index = 0
        if context:
            try:
                start_index = self.handlers.index(context._handler)+1
            except ValueError:
                start_index = 0
        
        if start_index > len(self.handlers) - 1:
            return
                
        handler = self.handlers[start_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_read_complete(ctx)
        except BaseException as e:
            _logger.ERROR(f"BaseException in read_complete handler {handler}: {e}")
            
    async def fire_channel_write_complete(self, current_ctx: Optional[ChannelHandlerContext] = None):        
        """触发写入事件"""
        end_index = len(self.handlers) - 1
        if current_ctx:
            try:
                end_index = self.handlers.index(current_ctx._handler) - 1
            except ValueError:
                end_index = len(self.handlers) - 1
        
        if end_index < 0:
            return
                
        handler = self.handlers[end_index] 
        ctx = self.contexts[handler]
        try:
            await handler.channel_write_complete(ctx)
        except BaseException as e:
            _logger.ERROR(f"BaseException in write_complete handler {handler}: {e}")
            
class ServerSocketChannel():
    
    # def __init__(self, boss_eventloopGroup:CoroutineWorkGroup=None, worker_eventloopGroup:CoroutineWorkGroup=None):
    def __init__(self, worker_eventloopGroup:CoroutineWorkGroup=None):
        # assert boss_eventloopGroup, 'boss_eventloopGroup 必须 非None' 
        # assert isinstance(boss_eventloopGroup, CoroutineWorkGroup) , 'boss_eventloopGroup 必须 CoroutineWorkGroup实例' 
        assert worker_eventloopGroup, 'worker_eventloopGroup 必须 非None' 
        assert isinstance(worker_eventloopGroup, CoroutineWorkGroup) , 'worker_eventloopGroup 必须 CoroutineWorkGroup实例'         
        # self._boss_eventloopGroup = boss_eventloopGroup
        self._worker_eventloopGroup = worker_eventloopGroup        
        
    def setChildAttributes(self, attributes:dict[str,any]):
        self._childchannel_option = attributes
        
    def setAttributes(self, attributes:dict[str,any]):
        self._channel_option = attributes       
        
    def setSocketChannelInitializer(self, socketChannelInitializer:SocketChannelInitializer):  
        self._socketChannelInitializer = socketChannelInitializer
        
    def newSocketChannel(self, reader: asyncio.StreamReader,        
                        writer: asyncio.StreamWriter, attributes:dict[str,any])->SocketChannel:
        _sc = SocketChannel(reader, writer, attributes)
        return _sc    
            
    async def _process_client_handler(self):
        pass
    
    def local_address(self) -> Optional[tuple]:        
        return self._address
    
    def _accept_client_handler(self):        
        def on_client_connected(r: asyncio.StreamReader, w:asyncio.StreamWriter):                    
            try:
                socketChannel:SocketChannel  = self.newSocketChannel(r, w, self._childchannel_option)      
                socketChannel.setSocketChannelInitializer(self._socketChannelInitializer)
                
                self._worker_eventloopGroup.submit(socketChannel.start())
            except BaseException as e:
                _logger.DEBUG(f'处理新客户端出现错误{e}')
                w.close()
            
        return on_client_connected
    
    async def bind(self, address:tuple[str,int]):
        self._address = address
        
        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
        if self._channel_option[ChannelOption.SO_REUSEADDR.name]:
            serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)                                                      
        if self._channel_option[ChannelOption.SO_SNDBUF.name] > 0:
            try:
                serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self._channel_option[ChannelOption.SO_SNDBUF.name])     
            except Exception as e:
                _logger.ERROR(f"设置服务端SO_SNDBUF错误: {e}", e)                                       
        if self._channel_option[ChannelOption.SO_RCVBUF.name] > 0:
            try:
                serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self._channel_option[ChannelOption.SO_RCVBUF.name])     
            except Exception as e:
                _logger.ERROR(f"设置服务端SO_RCVBUF错误: {e}", e)                              
        if self._channel_option[ChannelOption.SO_RCVBUF.name] > 0:
            try:
                serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self._channel_option[ChannelOption.SO_RCVBUF.name])     
            except Exception as e:
                _logger.ERROR(f"设置服务端SO_RCVBUF错误: {e}", e)                            
        if self._channel_option[ChannelOption.SO_KEEPALIVE.name]:
            try:
                serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, self._channel_option[ChannelOption.SO_KEEPALIVE.name])     
            except Exception as e:
                _logger.ERROR(f"设置服务端SO_RCVBUF错误: {e}", e)  
                                            
        try:
            if self._channel_option[ChannelOption.TCP_NODELAY.name]:
                serv_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except Exception as e:
            _logger.ERROR(f"设置服务端TCP_NODELAY错误: {e}", e)                      
        try:
            if self._channel_option[ChannelOption.SO_LINGER.name] and self._channel_option[ChannelOption.SO_LINGER.name] >= 0:
                v = self._channel_option[ChannelOption.SO_LINGER.name]
                serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('hh', 1, v) if isWin() else struct.pack('ii', 1, v))     
        except Exception as e:
            _logger.ERROR(f"设置服务端SO_LINGER错误: {e}", e)        

        try:                                                
            serv_sock.bind(self._address)
            serv_sock.listen(self._channel_option[ChannelOption.SO_BACKLOG.name])
        except IOError as e:
            raise NetWorkError(f'{e}')
                
        serv_sock.setblocking(False)
        _logger.DEBUG("主服务器启动 ......")
        # 在默认事件循环中创建服务器        
        _logger.DEBUG(f'Options={self._channel_option}')
        _logger.DEBUG(f'ChildOptions={self._childchannel_option}')
        
        self._serv_sock = serv_sock
        return self._serv_sock
            
    async def start(self):                
        try:             
            # 必须使用_worker_eventloopGroup 保证accept和r，w处理在一个事件循环环境里
            server = await asyncio.start_server(
                self._accept_client_handler(),
                # new_client_handler(self._worker_eventloopGroup),
                sock=self._serv_sock
                # '0.0.0.0', 
                # 8888
            )
            self._server = server
            server_sockets = server.sockets                
            _logger.DEBUG(f"主服务器启动监听{self._address[0]}:{self._address[1]}")
            if server_sockets:                    
                for s in server_sockets:
                    addr = s.getsockname()
                    _logger.INFO(f"{addr[0]}:{addr[1]}")
                                            
                # _logger.INFO("服务器配置参数:")
                _logger.INFO(f"SO_REUSEADDR: {s.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)}")                    
                try:
                    _logger.INFO(f"SO_KEEPALIVE: {s.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)}")
                except BaseException:
                    pass                    
                _logger.INFO(f"SO_SNDBUF: {s.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)}")
                _logger.INFO(f"SO_RCVBUF: {s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)}")                    
                try:
                    _logger.INFO(f"TCP_NODELAY: {s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY)}")
                except BaseException:
                    pass
                try:
                    _logger.INFO(f"SO_LINGER: {s.getsockopt(socket.SOL_SOCKET, socket.SO_LINGER)}")
                except BaseException as e:
                    _logger.ERROR('', e)
                    pass
            
            async with server:
                await server.serve_forever()
                                         
        except asyncio.exceptions.CancelledError:
            pass
        except BaseException as e:
            if _logger.canDebug():
                _logger.ERROR(f'服务端遇到异常{e}', e)
            pass
        except GeneratorExit:                
            if _logger.canDebug():
                _logger.DEBUG('服务端遇到GeneratorExit')
            pass
            # raise     
    
    def close(self):
        self._serv_sock.close()
        
            
    
    
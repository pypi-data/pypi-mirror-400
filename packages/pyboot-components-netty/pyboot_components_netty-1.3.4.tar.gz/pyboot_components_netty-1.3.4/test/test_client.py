import asyncio
from pyboot.commons.utils.log import Logger
from pyboot.commons.coroutine.tools import AsyncStdin,AsyncStdinProcess,getOrCreate_eventloop,is_coroutine_func  # noqa: F401
from pyboot.commons.coroutine.task import CoroutineWorkGroup

from pyboot.components.netty.bootstrap import Bootstrap
from pyboot.components.netty.channel import SocketChannel,ChannelOption

from pyboot.components.netty.handler import IdleStateHandler,LoggingHandler,WriteTimeoutHandler # noqa: F401
from pyboot.components.netty.codec import StringDecoder,ByteDelimiterBasedFrameDecoder,DelimiterBasedFrameDecoder  # noqa: F401
from pyboot.components.netty.codec import LineBasedFrameDecoder,StringEncoder,JsonEncoder  # noqa: F401
from pyboot.components.netty.codec import LengthFieldBasedFrameDecoder,SimpleBytesLengthFieldBasedFrameEncoder # noqa: F401
from pyboot.components.netty.channel import ChannelHandler,ChannelHandlerContext,ChannelEvent,ChannelHandleError  # noqa: F401
from pyboot.commons.utils.bytes import PooledByteBufferAllocator

HOST, PORT = "127.0.0.1", 8888
ENC = "utf8"
BUFSIZE = 1024


_logger = Logger('pyboot.components.netty')

# ---------- 客户端 ----------
class EchoClient:
    def __init__(self):
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._closed = False
        self._max_retry = 4

    async def _connect(self):
        """建立一条新连接，带指数退避重试"""
        delay = 1
        times = 0
        while not self._closed:
            try:
                self._reader, self._writer = await asyncio.open_connection(HOST, PORT)
                _logger.DEBUG("[C] 已连接到服务器")
                return
            except OSError as e:
                times += 1
                if times > self._max_retry:
                    _logger.DEBUG(f'连接失败超过最大数{self._max_retry}, 退出连接：')
                    raise OSError(f'连接失败超过最大数{self._max_retry}.')
                               
                _logger.DEBUG(f"[C] 连接失败: {e}，{delay}s 后重试")
                await asyncio.sleep(delay)                
                delay = min(delay + 1, 16)

    async def _readloop(self):
        """异步收数据并打印"""
        try:
            while data := await self._reader.read(BUFSIZE):
                _logger.DEBUG(f"[C] 收到: {data.decode(ENC).rstrip()}")
        except (asyncio.CancelledError):
            # _logger.DEBUG(f'{e}')
            pass
        except (ConnectionResetError) as e:    
            _logger.DEBUG(f'读出现问题{e}')
        finally:
            _logger.DEBUG("[C] 读循环结束")

    async def _sendloop(self):
        """从 stdin 读一行发一行"""
        loop = asyncio.get_event_loop()
        # _stdid = AsyncStdin(loop=loop)
        self._stdid = AsyncStdin(loop=loop)        
        try:
            while not self._closed:                
                line = await self._stdid.readline()
                if not line:        # Ctrl-D / EOF
                   break                    
                if not line.strip():
                    continue
                self._writer.write(line.encode(ENC))
                await self._writer.drain()
                if line.strip().upper() == 'CLOSE':
                    break        
        except Exception as e:
            _logger.Error(f'异常：{e}', e)
            pass
        finally:            
            _logger.DEBUG("[C] 发送循环结束")
            await self.close()

    async def close(self):
        if self._stdid:
            self._stdid.close()
            
        if self._closed:
            return        
        self._closed = True
        if self._writer:
            self._writer.close()        

    async def run(self):        
        await self._connect()
                        
        # 并发读写
        read_task = asyncio.create_task(self._readloop())
        send_task = asyncio.create_task(self._sendloop())
        # 任意一个退出即整体结束
        done, pending = await asyncio.wait(
            {read_task, send_task}, return_when=asyncio.FIRST_COMPLETED
        )
        
        for t in pending:
            t.cancel()
        
        await asyncio.gather(*pending, return_exceptions=True)    
        await self.close()

        
async def main():
    def print_exit(s, f):        
        import time
        time.sleep(1)
        # echoclient.close()
        _logger.DEBUG('退出程序11111')
    
    async def async_print_exit(s, f):
        # echoclient.close()        
        asyncio.sleep(0.001)
        _logger.DEBUG('退出程序11111')
        
    echoclient = EchoClient()
    await echoclient.run()
        
def start_with_common():
    # asyncio.run(main())
    _logger.DEBUG('使用asyncio进行客户端连接')
    try:
        asyncio.run(main())
        # main2()
    except asyncio.exceptions.CancelledError:
        _logger.DEBUG('任务取消')
    except Exception as e:
        _logger.DEBUG(f'{e}')
    finally:
        _logger.DEBUG('退出程序')

class StdinTask:            
    def __init__(self):
        self._stdid:AsyncStdin = None
        
    def set_callback(self, callback=None):
        self.callback = callback        
        
    def close(self):
        if self._stdid:
            self._stdid.close()
        
    async def start(self):
        """从 stdin 读一行发一行"""
        self._stdid = AsyncStdin()
        
        async def _start():                                        
            try:
                while True:
                    line = await self._stdid.readline()
                    if not line:
                        break
                    
                    if self.callback:
                        if is_coroutine_func(self.callback):
                            rtn = await self.callback(line)
                        else:
                            rtn = self.callback(line)
                        if rtn:
                            break
                    else:
                        _logger.DEBUG(f'读取输入字符:{line.strip()}')
            except Exception as e:
                _logger.ERROR(f'异常：{e}', e)
                pass
            finally:            
                _logger.DEBUG("[C] 发送循环结束")
                self._stdid.close()       
        
        getOrCreate_eventloop()[0].create_task(_start())
        
    
class EchoClientHandler(ChannelHandler[str]):
    def __init__(self, name:str='Davidliu',stdintask:StdinTask=None):
        self.name = name        
        self.stdintask = stdintask        
    
    def close(self):        
        self.stdintask.close()
            
    async def channel_read(self, ctx: ChannelHandlerContext, line:str):
        _logger.DEBUG(f'收到数据：{line}')
            
    async def channel_active(self, ctx: ChannelHandlerContext):
        def new_callback(ctx:ChannelHandlerContext):
            async def _callback(line:str):
                # await ctx.channel.write(line.strip())
                # await ctx.channel.write(l_bytes(line.strip().encode(), 20, b' ', True))
                # 配合 SimpleBytesLengthFieldBasedFrameEncoder和LengthFieldBasedFrameDecoder使用
                # 使用bytes作为in
                await ctx.channel.write(line.strip().encode('utf-8'))
                pass
            return _callback
            
        self.stdintask.set_callback(new_callback(ctx=ctx))
        await self.stdintask.start()
        _logger.DEBUG(f'激活Channel的StdIn线程：{ctx.channel}')
        await ctx.fire_channel_active()
    
    async def channel_inactive(self, ctx: ChannelHandlerContext):
        self.stdintask.close()                
        _logger.DEBUG(f'关闭Channel的StdIn线程：{ctx.channel}')
        await ctx.fire_channel_inactive()
        # 退出bootstrap
        self.close()
        
    async def channel_event(self, ctx: ChannelHandlerContext, event: ChannelEvent, *args):
        if event == ChannelEvent.READ_IDLE:
            _logger.DEBUG('读数据超时')
            await ctx.channel.close()
            return
        elif event == ChannelEvent.WRITE_IDLE:
            _logger.DEBUG('写数据超时')
            await ctx.channel.close()
            return
        elif event == ChannelEvent.UDF_EVENT:
            if args[0]==IdleStateHandler.ALLIDLE_EVENT_TYPE:
                _logger.DEBUG('读写数据超时')
                await ctx.channel.close()
                return         
        await ctx.fire_channel_event(event, *args)    
            

def buildBootstrap()->Bootstrap:
    
    work_group = CoroutineWorkGroup(1,"WorkGroup")
    bs:Bootstrap = Bootstrap().group(work_group)        
    t = StdinTask()
    handler = EchoClientHandler('Liuyong', t)
    
    async def _connect_suc(b:Bootstrap, r, w):
        _logger.DEBUG(f'Bootstrap={b} reader={r} writer={w}')
        
    async def _connect_suc(b:Bootstrap, r, w):
        _logger.DEBUG(f'Bootstrap={b} reader={r} writer={w}')
        
    async def _connect_fail(b:Bootstrap, e):
        _logger.DEBUG(f'Bootstrap={b} exception={e}')
        fail_count = 1
        times = 3
        while fail_count < times:
            try:
                bf = await b.connect()
                return bf
            except BaseException as e2:
                _logger.DEBUG(f'Bootstrap={b} exception={e2}')
            finally:
                fail_count += 1
                if fail_count >= times:
                    break
                await asyncio.sleep(3)
                
        raise IOError(f'连接失败{fail_count}次，退出程序')
                
        
    def initChannel(sc:SocketChannel):
        _pipeline = sc.pipeline()
        _pipeline.add_last(IdleStateHandler(0,120,0))
        _pipeline.add_last(LoggingHandler(Logger.LEVEL.INFO))
        _pipeline.add_last(WriteTimeoutHandler(5,False))
        # _pipeline.add_last(DelimiterBasedFrameDecoder([b'\n',b'\r\n'], stripDelimiter=False))        
        # _pipeline.add_last(ByteDelimiterBasedFrameDecoder([b'\n',b'\r\n'], stripDelimiter=False))
        
        # _pipeline.add_last(LineBasedFrameDecoder(stripDelimiter=False))
        # 长度帧解析方式
        _pipeline.add_last(LengthFieldBasedFrameDecoder(length_field_length=4, length_adjustment=0, length_field_offset=4,initial_bytes_to_strip=8))        
        _pipeline.add_last(StringDecoder(charset='utf-8', strip=True))        
        # _pipeline.add_last(EchoHandler('DavidLiu'))     
        _pipeline.add_last(SimpleBytesLengthFieldBasedFrameEncoder())   
        # _pipeline.add_last(StringEncoder(charset='utf-8'))
        # _pipeline.add_last(JsonEncoder())
        _pipeline.add_last(handler)
    
    # work_group = CoroutineWorkGroup(1,"WorkGroup")
    bs.channel(SocketChannel).handler(initChannel)\
            .option(ChannelOption.SO_BACKLOG, 1024)\
                .option(ChannelOption.SO_TIMEOUT, 6).option(ChannelOption.ALLOCATOR, PooledByteBufferAllocator.DEFAULT)\
                .address((HOST, PORT)).when_connect_sucess(_connect_suc).when_connect_fail(_connect_fail)
    return bs
    
            
def start_with_bootstrap_with_sync():    
    bs:Bootstrap = buildBootstrap()
    bs.grace()            
    
       
if __name__ == "__main__":    
    import sys
    if len(sys.argv)>1:
        HOST = sys.argv[1]
    _logger.DEBUG(f'host = {HOST}')        
    
    # start_with_common()
    start_with_bootstrap_with_sync()
            
            
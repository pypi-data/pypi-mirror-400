import asyncio
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.bytes import ByteBuffer
from pyboot.commons.coroutine.task import CoroutineWorkGroup
import time
from pyboot.commons.coroutine.tools import GracefulShutdown
import socket
from pyboot.components.netty.channel import ChannelOption,SocketChannel,ServerSocketChannel  # noqa: F401
from pyboot.components.netty.bootstrap import ServerBootstrap
from pyboot.commons.utils.bytes import PooledByteBufferAllocator
from pyboot.components.netty.handler import IdleStateHandler,LoggingHandler,WriteTimeoutHandler,ListRemoteAddressFilter # noqa: F401
from pyboot.components.netty.codec import StringDecoder,ByteDelimiterBasedFrameDecoder,DelimiterBasedFrameDecoder  # noqa: F401
from pyboot.components.netty.codec import LineBasedFrameDecoder,StringEncoder,JsonEncoder,FixedLengthFrameDecoder  # noqa: F401
from pyboot.components.netty.codec import LengthFieldBasedFrameDecoder, SimpleBytesLengthFieldBasedFrameEncoder  # noqa: F401
from pyboot.components.netty.channel import ChannelHandler,ChannelHandlerContext,ChannelEvent,ChannelHandleError  # noqa: F401
from pyboot.commons.utils.utils import date_datetime_cn, date2str_yyyymmddhhmmsss,json_to_str

_logger = Logger('pyboot.components.netty.bootstrap')

# 启动函数
def main():
    HOST, PORT = '0.0.0.0', 8888
    
    # 业务协程：echo 回显 + 简单拆包（\n 结尾）
    async def handle_echo(reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')        
        try:
            while data := await reader.readline():   # 行协议
                line = data.decode()
                _logger.DEBUG(f"{addr}:收到数据:{line.strip()}")
                if line.strip().upper() == 'CLOSE':
                    _logger.DEBUG('收到退出命令，马上退出')
                    break               
                writer.write(data.upper())
                await writer.drain()
        except asyncio.IncompleteReadError as e:
            _logger.DEBUG(f"关闭客户端{e}")
        except GeneratorExit:
            raise        
        finally:
            _logger.DEBUG(f"关闭客户端{addr}")
            
            writer.close()
            await writer.wait_closed()

        
    def new_client_handler(work_group: CoroutineWorkGroup):        
        def on_client_connected(r, w):
            """在自定义循环中处理连接的函数"""
            # work_group.submit(handle_echo(r, w))        
            addr = w.get_extra_info('peername')
            sock = w.get_extra_info('socket')        
            _logger.DEBUG(f'开始处理协议通道{addr} reader={r} writer={w} socket={sock}')
            work_group.submit(handle_echo(r, w))
            # await handle_echo(r,w)
        
        return on_client_connected
        # try:                
        #     # 抛给业务协程
        #     loop.create_task(handle_echo(reader, writer))
        #     work_group.submit(worker_serve(conn.fileno()))
            
        # except Exception as e:
        #     _logger.DEBUG(f'进行连接操作报错{e}')
            
        pass        

    # Boss 主协程：只做 accept，然后 round-robin 把 fd 送给 worker
    async def boss(boss_group: CoroutineWorkGroup,
                work_group: CoroutineWorkGroup, gf:GracefulShutdown):            
        gf.start_shutdown_gracefully_await()        
            
        async def _listen_handler(_work_group: CoroutineWorkGroup):      
            
            serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serv_sock.bind((HOST, PORT))
            serv_sock.listen(1024)
            serv_sock.setblocking(False)
        
            _logger.DEBUG("主服务器启动 ......")
            # 在默认事件循环中创建服务器        
            server = await asyncio.start_server(
                new_client_handler(_work_group),
                sock=serv_sock
                # '0.0.0.0', 
                # 8888
            )
            _logger.DEBUG(f"主服务器启动在 {HOST}:{PORT}")
            async with server:
                await server.serve_forever()            
        boss_group.submit(_listen_handler(work_group))                        
        await gf.wait_event() 
        
        
    async def _shutdown_gracefully(boss_group: CoroutineWorkGroup,work_group: CoroutineWorkGroup):    
        await asyncio.sleep(1)            
        # serv_sock.close()
    
    # 1. 创建监听 socket（SO_REUSEPORT 可多进程复用）
    # serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # serv_sock.bind((HOST, PORT))
    # serv_sock.listen(1024)

    
    # 2. 创建 worker loops（每个跑在独立线程）
    
    # work_group = CoroutineWorkGroup(1,"WorkGroup")    
    boss_group = CoroutineWorkGroup(1,"BossGroup")
    
    # worker_loops:list[asyncio.AbstractEventLoop] = []
    # for _ in range(WORKER_THREADS):
    #     w_loop = asyncio.new_event_loop()
    #     worker_loops.append(w_loop)
    #     # 后台线程跑 loop
    #     import threading
    #     t = threading.Thread(target=w_loop.run_forever, daemon=True)
    #     t.start()

    # 3. 主线程跑 boss loop
    boss_loop = asyncio.new_event_loop()
    # boss_loop.create_server
    asyncio.set_event_loop(boss_loop)
    
    gf:GracefulShutdown = GracefulShutdown(boss_loop,None,_shutdown_gracefully,boss_group, boss_group)
    gf.emit()
    
    try:
        boss_loop.run_until_complete(boss(boss_group, boss_group, gf))
    except KeyboardInterrupt:
        _logger.DEBUG('退出程序')
    finally:    
        time.sleep(1)
        # _logger.DEBUG('停止 worker loop')
        # work_group.stop()
            
        _logger.DEBUG('停止 boss loop')
        boss_loop.stop()            
            
        _logger.DEBUG('资源关闭结束')                

class EchoTest(ChannelHandler[ByteBuffer]):
    async def channel_read(self, ctx: ChannelHandlerContext, data: ByteBuffer):
        await ctx.channel.write(data)

class EchoHandler(ChannelHandler[str]):
    def __init__(self, name:str='Davidliu'):
        self.name = name
        
    async def channel_read(self, ctx: ChannelHandlerContext, line:str):        
        # raise ChannelHandleError('dddd')
        _logger.DEBUG(f'收到数据：{line}')
        if line.strip().upper() == 'CLOSE':
            _logger.DEBUG('收到退出命令，马上退出')
            await ctx.channel.close()
        else:            
            # await ctx.channel.write(f'{self.name}:{line.upper()}\n'.encode('utf-8'))
            # await ctx.channel.write(f'{self.name}:{line.upper()}\n')
            # await ctx.channel.write(f'原文:{line}')
            # await ctx.channel.write({
            #     'name':self.name,
            #     'value':line,
            #     'upper':line.upper(),
            #     'time':date2str_yyyymmddhhmmsss(date_datetime_cn())
            # })
            
            # 配合 SimpleBytesLengthFieldBasedFrameEncoder和LengthFieldBasedFrameDecoder使用
            # 使用bytes作为in
            await ctx.channel.write(f'{self.name}:{line.upper()}\n'.encode('utf-8'))
            await ctx.channel.write(f'{self.name}:{line.upper()}\n'.encode('utf-8'))
            await ctx.channel.write(f'原文:{line}'.encode('utf-8'))
            await ctx.channel.write(json_to_str({
                'name':self.name,
                'value':line,
                'upper':line.upper(),
                'time':date2str_yyyymmddhhmmsss(date_datetime_cn())
            }).encode('utf-8'))
            
            pass
             
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
        
      
def buildServerBootstrap()->ServerBootstrap:
    
    def initChannel2(sc:SocketChannel):
        _pipeline = sc.pipeline()
        _pipeline.add_last(ListRemoteAddressFilter(white_ips=['127.0.0.1','192.168.56.119','192.168.56.1']))
        _pipeline.add_last(IdleStateHandler(60,0,0))
        _pipeline.add_last(LoggingHandler(Logger.LEVEL.INFO))
        _pipeline.add_last(WriteTimeoutHandler(5,False))
        # # _pipeline.add_last(DelimiterBasedFrameDecoder([b'\n',b'\r\n'], stripDelimiter=False))
        # 
        # # _pipeline.add_last(ByteDelimiterBasedFrameDecoder([b'\n',b'\r\n'], stripDelimiter=False))
        
        # _pipeline.add_last(LineBasedFrameDecoder(stripDelimiter=False))
        # _pipeline.add_last(StringDecoder(charset='utf-8', strip=True))           
        
        # 固定长度解析方式
        # _pipeline.add_last(FixedLengthFrameDecoder(20))
        # 长度帧解析方式
        _pipeline.add_last(LengthFieldBasedFrameDecoder(length_field_length=4, length_adjustment=0, length_field_offset=4,initial_bytes_to_strip=8))        
        _pipeline.add_last(StringDecoder(charset='utf-8', strip=True))        
        _pipeline.add_last(EchoHandler('DavidLiu'))                
        _pipeline.add_last(SimpleBytesLengthFieldBasedFrameEncoder())
        # _pipeline.add_last(StringEncoder(charset='utf-8'))
        # _pipeline.add_last(JsonEncoder())
    
    def initChannel(sc:SocketChannel):
        _pipeline = sc.pipeline()
        # _pipeline.add_last(ListRemoteAddressFilter(white_ips=['127.0.0.1','192.168.56.119','192.168.56.1']))
        # _pipeline.add_last(IdleStateHandler(60,0,0))
        # _pipeline.add_last(LoggingHandler(Logger.LEVEL.INFO))
        # _pipeline.add_last(WriteTimeoutHandler(5,False))
        # # _pipeline.add_last(DelimiterBasedFrameDecoder([b'\n',b'\r\n'], stripDelimiter=False))
        # 
        # # _pipeline.add_last(ByteDelimiterBasedFrameDecoder([b'\n',b'\r\n'], stripDelimiter=False))
        
        # _pipeline.add_last(LineBasedFrameDecoder(stripDelimiter=False))
        # _pipeline.add_last(StringDecoder(charset='utf-8', strip=True))           
        
        # 固定长度解析方式
        # _pipeline.add_last(FixedLengthFrameDecoder(20))
        # 长度帧解析方式
        # _pipeline.add_last(LengthFieldBasedFrameDecoder(length_field_length=4, length_adjustment=0, length_field_offset=4,initial_bytes_to_strip=8))        
        # _pipeline.add_last(StringDecoder(charset='utf-8', strip=True))        
        # _pipeline.add_last(EchoHandler('DavidLiu'))
        # _pipeline.add_last(SimpleBytesLengthFieldBasedFrameEncoder())
        # _pipeline.add_last(StringEncoder(charset='utf-8'))
        # _pipeline.add_last(JsonEncoder())    
        _pipeline.add_last(EchoTest())
    
    boss_group = CoroutineWorkGroup(1,"BossGroup")
    server:ServerBootstrap = ServerBootstrap().group(boss_group)\
        .channel(ServerSocketChannel).childHandler(initChannel)\
            .option(ChannelOption.SO_BACKLOG, 1024).option(ChannelOption.ALLOCATOR, PooledByteBufferAllocator.DEFAULT)\
                .address(('0.0.0.0', 8888))
    return server
      
def start_with_serverbootstrap_with_async():
    sbs:ServerBootstrap = buildServerBootstrap()    
    try:
        asyncio.run(sbs.bind())
    except KeyboardInterrupt:
        _logger.DEBUG('收到 Ctrl-C，开始关闭...')
    finally:
        _logger.DEBUG('Stop')
        sbs.close()      
            
def start_with_serverbootstrap_with_sync():
    sbs:ServerBootstrap = buildServerBootstrap()
    sbs.grace()    
    
if __name__ == '__main__':
    # main()    
    start_with_serverbootstrap_with_sync()
    
from pyboot.components.netty.channel import ChannelHandler,ChannelHandlerContext,ChannelEvent,ChannelHandleError
from pyboot.commons.utils.log import Logger
import asyncio
from pyboot.commons.utils.maths import PHI
from pyboot.commons.coroutine.tools import sleep,gather_with_timeout

_logger = Logger('pyboot.components.netty.handler')

class IdleStateHandler(ChannelHandler[any]):
    ALLIDLE_EVENT_TYPE:str = 'ALLIDLE_EVENT_TYPE'
    def __init__(self, readerIdleTimeSeconds:int, writerIdleTimeSeconds:int, allIdleTimeSeconds:int):
        assert readerIdleTimeSeconds>=0, f'readerIdleTimeSeconds必须大于等于0,但是获得{readerIdleTimeSeconds}'
        assert writerIdleTimeSeconds>=0, f'writerIdleTimeSeconds必须大于等于0,但是获得{writerIdleTimeSeconds}'
        assert allIdleTimeSeconds>=0, f'allIdleTimeSeconds必须大于等于0,但是获得{allIdleTimeSeconds}'
        
        self.readerIdleTimeSeconds = readerIdleTimeSeconds
        self.writerIdleTimeSeconds = writerIdleTimeSeconds
        self.allIdleTimeSeconds = allIdleTimeSeconds
        
        self._last_read_time = 0
        self._last_write_time = 0        
        self._running = False
        self._sleep_stop = None
     
    # async def channel_read(self, ctx: ChannelHandlerContext, data: any):        
    #     self._last_read_time = asyncio.get_event_loop().time()
    #     await ctx.fire_channel_read(data)
    
    # async def channel_write(self, ctx: ChannelHandlerContext, data: any):
    #     self._last_write_time = asyncio.get_event_loop().time()
    #     await ctx.fire_channel_write(data)
        
    async def _schedule_check(self, sleep_s:int, loop:asyncio.AbstractEventLoop, ctx: ChannelHandlerContext):
        nt = loop.time()
        self._last_read_time = nt
        self._last_write_time = nt
        self._running = True
        self._sleep_stop = asyncio.Event()
        
        while self._running:
            nt = loop.time()
            
            if _logger.canDebug():            
                _logger.DEBUG(f'当前秒数{nt:.9f}, 下一次心跳检查{sleep_s:.3f}秒, last_read_time={self._last_read_time:.9f}[{nt - self._last_read_time:.9f}] last_write_time={self._last_write_time:.9f}[{nt - self._last_write_time:.9f}]')    
            
            # _logger.DEBUG(f'当前秒数{nt:.9f}, last_read_time={self._last_read_time:.9f}[{nt - self._last_read_time:.9f}] last_write_time={self._last_write_time:.9f}[{nt - self._last_write_time:.9f}]')
            if self.readerIdleTimeSeconds > 0 and nt - self._last_read_time > self.readerIdleTimeSeconds:
                await ctx.fire_channel_event(ChannelEvent.READ_IDLE)
                _break = True
                
            if self.writerIdleTimeSeconds > 0 and nt - self._last_write_time > self.writerIdleTimeSeconds:
                await ctx.fire_channel_event(ChannelEvent.WRITE_IDLE)
                _break = True
            
            if self.allIdleTimeSeconds > 0 and (nt - self._last_write_time > self.allIdleTimeSeconds and nt - self._last_read_time > self.allIdleTimeSeconds):
                await ctx.fire_channel_event(ChannelEvent.UDF_EVENT, IdleStateHandler.ALLIDLE_EVENT_TYPE)
                _break = True
            
            # 加上这句是，读写超时时，先fire_channel_event, 在后面handle中channel.close后，触发channel_inactive，　
            # 但是还在向下进行，还是会调用到这里。不加上，还会sleep一个周期
            if not self._running: 
                break
            
            if not ctx.channel.is_active:
                if _logger.canDebug():
                    _logger.DEBUG('Channel已经关闭，跳出Idle循环')
                break
            
            await sleep(sleep_s, self._sleep_stop)
        
        if _logger.canDebug():    
            _logger.DEBUG(f'{ctx.channel}退出IdleStateHandler时间检查循环')

    def _judge_sleep_s(self):
        d = [self.readerIdleTimeSeconds, self.writerIdleTimeSeconds, self.allIdleTimeSeconds]
        d = [i for i in d if i>0]
        min_s = min(d, default=0)
        return min_s / PHI
        
    async def channel_active(self, ctx: ChannelHandlerContext):
        loop:asyncio.AbstractEventLoop = asyncio.get_event_loop()        
        loop.create_task(self._schedule_check(self._judge_sleep_s(), loop, ctx))
        # await self._schedule_task
        await ctx.fire_channel_active()
    
    async def channel_inactive(self, ctx: ChannelHandlerContext):
        if self._running:
            self._running = False
            if self._sleep_stop:
                self._sleep_stop.set()
                
            if _logger.canDebug():
                _logger.DEBUG('发送关闭时间检查关闭信号')
            await ctx.fire_channel_inactive()
                    
    async def channel_event(self, ctx: ChannelHandlerContext, event: ChannelEvent, *args):
        if event == ChannelEvent.READ_DO:
            self._last_read_time = asyncio.get_event_loop().time()
        elif event == ChannelEvent.WRITE_DO:
            self._last_write_time = asyncio.get_event_loop().time() 
        
        await ctx.fire_channel_event(event, *args)


class WriteTimeoutHandler(ChannelHandler[any]):
    def __init__(self, writerTimeout:int,fastFail:bool=True):
        assert writerTimeout > 0, f'writerTimeout必须大于0，但是{writerTimeout}'        
        self.writerTimeout = writerTimeout
        self.fastFail = fastFail
    
    async def channel_write(self, ctx: ChannelHandlerContext, data: any):
        try:
            await gather_with_timeout([ctx.fire_channel_write(data)], self.writerTimeout)
        except asyncio.TimeoutError:
            await ctx.channel.close()
                        
            if self.fastFail:
                raise ChannelHandleError(f'写超时(writerTimeout={self.writerTimeout})')
        except BaseException as e:
            if _logger.canDebug():
                _logger.ERROR(f'{e}', e)
            raise e
    


class LoggingHandler(ChannelHandler[any]):
    def __init__(self, level:Logger.LEVEL=Logger.LEVEL.DEBUG):
        self.level = level
        
    def _logger(self):
        if self.level.value == Logger.LEVEL.CRITICAL.value:
            return _logger.CRITICAL
        elif self.level.value == Logger.LEVEL.ERROR.value:
            return _logger.ERROR
        elif self.level.value == Logger.LEVEL.FATAL.value:
            return _logger.FATAL
        elif self.level.value == Logger.LEVEL.INFO.value:
            return _logger.INFO
        elif self.level.value == Logger.LEVEL.WARN.value:
            return _logger.WARN
        elif self.level.value == Logger.LEVEL.WARNING.value:
            return _logger.WARN
        elif self.level.value == Logger.LEVEL.DEBUG.value:
            return _logger.DEBUG
        else:
            return _logger.DEBUG
        
    def _canlogger(self):
        if self.level.value == Logger.LEVEL.CRITICAL.value:
            return _logger.canCritical
        elif self.level.value == Logger.LEVEL.ERROR.value:
            return _logger.canError
        elif self.level.value == Logger.LEVEL.FATAL.value:
            return _logger.canFatal
        elif self.level.value == Logger.LEVEL.INFO.value:
            return _logger.canInfo
        elif self.level.value == Logger.LEVEL.WARN.value:
            return _logger.canWarn
        elif self.level.value == Logger.LEVEL.WARNING.value:
            return _logger.canWarn
        elif self.level.value == Logger.LEVEL.DEBUG.value:
            return _logger.canDebug
        else:
            return _logger.canDebug
    
    async def channel_read(self, ctx: ChannelHandlerContext, data: any):
        if self._canlogger():
            self._logger()(f'ctx.fire_channel_read(data) ctx={ctx} data={data}')
        await ctx.fire_channel_read(data)
        
    async def channel_read_complete(self, ctx: ChannelHandlerContext):
        if self._canlogger():
            self._logger()(f'ctx.fire_channel_read_complete() ctx={ctx}')
        await ctx.fire_channel_read_complete()
    
    async def channel_write(self, ctx: ChannelHandlerContext, data: any):
        if self._canlogger():
            self._logger()(f'ctx.fire_channel_write(data) ctx={ctx} data={data}')
        await ctx.fire_channel_write(data)
    
    async def channel_write_complete(self, ctx: ChannelHandlerContext):
        if self._canlogger():
            self._logger()(f'ctx.fire_channel_write_complete() ctx={ctx}')        
        await ctx.fire_channel_write_complete()
        
    async def channel_active(self, ctx: ChannelHandlerContext):
        if self._canlogger():
            self._logger()(f'ctx.fire_channel_active() ctx={ctx}')
        await ctx.fire_channel_active()
    
    # @abstractmethod
    async def channel_inactive(self, ctx: ChannelHandlerContext):
        if self._canlogger():
            self._logger()(f'ctx.channel_inactive() ctx={ctx}')
        await ctx.fire_channel_inactive()
    
    async def exception_caught(self, ctx: ChannelHandlerContext, exception: BaseException):
        if self._canlogger():
            self._logger()(f'ctx.fire_exception_caught(exception) ctx={ctx} exception={exception}')
        await ctx.fire_exception_caught(exception)
    
    async def channel_event(self, ctx: ChannelHandlerContext, event: ChannelEvent, *args):
        if self._canlogger():
            self._logger()(f'ctx.fire_channel_event(event, *args) ctx={ctx} event={event} args={args}')
        await ctx.fire_channel_event(event, *args)
        
class FlushConsolidationHandler(ChannelHandler[any]): ...

class AbstractRemoteAddressFilter(ChannelHandler[any]):     
    async def channel_active(self, ctx: ChannelHandlerContext):
        address = ctx.channel.remote_address()[0]
        if _logger.canDebug():
            _logger.DEBUG(f'AbstractRemoteAddressFilter检查IP:{address}')
        if await self.allow_address(ctx, address):
            await ctx.fire_channel_active()
        else:
            await ctx.channel.close()
    
    async def channel_inactive(self, ctx: ChannelHandlerContext):
        await ctx.fire_channel_inactive()
                
    async def allow_address(self, ctx: ChannelHandlerContext, address:str): 
        if _logger.canDebug():
            _logger.DEBUG(f'AbstractRemoteAddressFilter检查IP:{address}')
        return True

class ListRemoteAddressFilter(AbstractRemoteAddressFilter):
    def __init__(self, black_ips:list=None, white_ips:list=None):
        super().__init__()
        self._black_ips = black_ips
        self._white_ips = white_ips
    
    async def allow_address(self, ctx: ChannelHandlerContext, address:str):
        if self._black_ips:
            if address in self._black_ips:
                return False
            else:
                return True
        
        if self._white_ips:
            if address in self._white_ips:
                return True
            else:
                return False
            
        return True
        
    

async def test_idelhandler():        
    ih = IdleStateHandler(10,0,0)
    _logger.DEBUG(ih._judge_sleep_s())    
    await ih.channel_active(None)
    await sleep(100)
    
if __name__ == "__main__":        
    asyncio.run(test_idelhandler())
    
    

import asyncio
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.reflect import get_fullname
from pyboot.commons.coroutine.task import CoroutineWorkGroup
import time
from pyboot.commons.coroutine.tools import GracefulShutdown,is_coroutine_func,TripleFuture,gather_with_timeout
from pyboot.components.netty.channel import ChannelOption,ServerSocketChannel,SocketChannelInitializer,SocketChannel,NettyBaseError,NetWorkError
from pyboot.commons.utils.bytes import PooledByteBufferAllocator
import warnings

# 忽略特定的垃圾回收错误--在linux环境下，有事由于GC时机的问题，会产生圾回收错误
# 如下
'''
Exception ignored in: <function BaseEventLoop.__del__ at 0x7f12170a93a0>
Traceback (most recent call last):
  File "/usr/local/python-3.12.10/lib/python3.12/asyncio/base_events.py", line 732, in __del__
    self.close()
  File "/usr/local/python-3.12.10/lib/python3.12/asyncio/unix_events.py", line 68, in close
    super().close()
  File "/usr/local/python-3.12.10/lib/python3.12/asyncio/selector_events.py", line 104, in close
    self._close_self_pipe()
  File "/usr/local/python-3.12.10/lib/python3.12/asyncio/selector_events.py", line 111, in _close_self_pipe
    self._remove_reader(self._ssock.fileno())
  File "/usr/local/python-3.12.10/lib/python3.12/asyncio/selector_events.py", line 298, in _remove_reader
    key = self._selector.get_key(fd)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/python-3.12.10/lib/python3.12/selectors.py", line 190, in get_key
    return mapping[fileobj]
           ~~~~~~~^^^^^^^^^
  File "/usr/local/python-3.12.10/lib/python3.12/selectors.py", line 71, in __getitem__
    fd = self._selector._fileobj_lookup(fileobj)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/python-3.12.10/lib/python3.12/selectors.py", line 225, in _fileobj_lookup
    return _fileobj_to_fd(fileobj)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/python-3.12.10/lib/python3.12/selectors.py", line 42, in _fileobj_to_fd
    raise ValueError("Invalid file descriptor: {}".format(fd))
ValueError: Invalid file descriptor: -1
'''
def ignore_gc_warning():
    warnings.filterwarnings('ignore', 
        message='.*Invalid file descriptor.*')


_logger = Logger('pyboot.components.netty.bootstrap')

class BootstrapFuture:
    def __init__(self):        
        self.future = TripleFuture()
        self._result = None
        
    async def sync(self):                
        await self.future.started()        
        try:
            # await future_await_threadsafe(w_loop, stop_f)
            await self.future.wait_ended()
        except BaseException as e:            
            raise e
        
    def result(self):
        return self.future.result()

class ServerBootstrap:
    _default_channel_config:dict = {
        ChannelOption.SO_BACKLOG.name:1024,
        ChannelOption.SO_REUSEADDR.name:True,
        ChannelOption.SO_KEEPALIVE.name:True,
        ChannelOption.ALLOCATOR.name:PooledByteBufferAllocator.DEFAULT,
        ChannelOption.WRITE_BUFFER_WATER_MARK.name:True,
        ChannelOption.SO_SNDBUF.name:32 * 1024,
        ChannelOption.SO_RCVBUF.name:32 * 1024,
        ChannelOption.SO_LINGER.name:None,        
        ChannelOption.TCP_NODELAY.name:True,
        ChannelOption.SO_CHUNKSIZE.name:1024
    }
    _default_childchannel_config:dict = {
        ChannelOption.SO_BACKLOG.name:1024,
        ChannelOption.SO_KEEPALIVE.name:True,
        ChannelOption.ALLOCATOR.name:PooledByteBufferAllocator.DEFAULT,
        ChannelOption.TCP_NODELAY.name:True,
        ChannelOption.WRITE_BUFFER_WATER_MARK.name:True,
        ChannelOption.SO_SNDBUF.name:32 * 1024,
        ChannelOption.SO_RCVBUF.name:32 * 1024,
        ChannelOption.SO_LINGER.name:None,        
        ChannelOption.SO_CHUNKSIZE.name:1024
    }
    def __init__(self):
        self._channel_option = ServerBootstrap._default_channel_config.copy()
        self._childchannel_option = ServerBootstrap._default_childchannel_config.copy()
        # self._boss_eventloopGroup = None
        self._worker_eventloopGroup = None
        self._channelcls = ServerSocketChannel  
        self._channel:ServerSocketChannel = None
        self._handler = None
        self._address = None        
        self._shutdown_func = None
        self._shutdown_func_args = None
        self._shutdown_func_kargs = None
        self._server = None
        self._socketChannelInitializer = None
        # self.gf = None
        self._callback_fail = None
        self._callback_sucess = None
        
    def group(self, worker_eventloopGroup:CoroutineWorkGroup=None)->'ServerBootstrap':
        # assert boss_eventloopGroup, 'boss_eventloopGroup 必须 非None' 
        # assert isinstance(boss_eventloopGroup, CoroutineWorkGroup) , 'boss_eventloopGroup 必须 CoroutineWorkGroup实例' 
        assert worker_eventloopGroup, 'worker_eventloopGroup 必须 非None' 
        assert isinstance(worker_eventloopGroup, CoroutineWorkGroup) , 'worker_eventloopGroup 必须 CoroutineWorkGroup实例' 
        
        # self._boss_eventloopGroup = boss_eventloopGroup
        self._worker_eventloopGroup = worker_eventloopGroup
        # self._worker_eventloopGroup = self._boss_eventloopGroup
        
        return self
    def channel(self, serverSocketChannel:type[ServerSocketChannel]=ServerSocketChannel)->'ServerBootstrap':
        assert serverSocketChannel, 'serverSocketChannel 必须 非None' 
        assert isinstance(serverSocketChannel, type), f'必须是类型对象, 当前{serverSocketChannel}[{type(serverSocketChannel)}]'            
        assert issubclass(serverSocketChannel, ServerSocketChannel), f'必须是ServerSocketChannel或者子类的类型对象, 当前{serverSocketChannel}'
            
        self._channelcls = serverSocketChannel
        return self
    def option(self, option:ChannelOption, v:any)->'ServerBootstrap':
        self._channel_option.update({
            option.name:v
        })
        return self
    def childOption(self, option:ChannelOption, v:any)->'ServerBootstrap':
        self._childchannel_option.update({
            option.name:v
        })
        return self
    def childHandler(self, socketChannelInitializer:SocketChannelInitializer)->'ServerBootstrap':
        assert socketChannelInitializer, '不能使用None对象'
        assert isinstance(socketChannelInitializer, SocketChannelInitializer) or callable(socketChannelInitializer), f'必须是SocketChannelInitializer对象或者def initChannel(self, socketChannel:SocketChannel)方法，但是为{socketChannelInitializer}'
        self._socketChannelInitializer = socketChannelInitializer
        return self
    def address(self, address:tuple[str,int])->'ServerBootstrap':
        self._address = address
        return self
    def shutdown_callback(self, shutdown_func:callable, *args, **kargs)->'ServerBootstrap':
        assert callable(shutdown_func), f'参数需要一个可调用对象，当前{shutdown_func}'                    
        assert not is_coroutine_func(shutdown_func),'务必使用同步方法释放资源，async方法可能不能执行完全就退出'
        
        self._shutdown_func = shutdown_func
        self._shutdown_func_args = args
        self._shutdown_func_kargs = kargs
        
        return self
        
    def when_connect_fail(self, callback)->'Bootstrap':
        assert callback and callable(callback),f'callback必须是callable对象，但是获得{callback}'
        self._callback_fail = callback
        return self
    def when_connect_sucess(self, callback)->'Bootstrap':
        assert callback and callable(callback),f'callback必须是callable对象，但是获得{callback}'
        self._callback_sucess = callback
        return self
    
    def _close_group(self):    
        # try:
        #     if self._boss_eventloopGroup:
        #         self._boss_eventloopGroup.stop()
        # except Exception:
        #     pass
        
        # if self._boss_eventloopGroup != self._worker_eventloopGroup:
        if self._worker_eventloopGroup:
            try:
                if self._worker_eventloopGroup:
                    self._worker_eventloopGroup.stop(abort=False)
            except Exception:
                pass  
            
            self._worker_eventloopGroup = None            
    
    def _close_serverchannel(self):                        
        try:
            if self._shutdown_func:
                if _logger.canDebug():    
                    _logger.DEBUG(">>> 释放所有serv_sock资源")                
                    
                self._shutdown_func(*self._shutdown_func_args, **self._shutdown_func_kargs)
                
            if _logger.canDebug():                                        
                _logger.DEBUG('资源关闭结束')    
        except Exception as e:
            if _logger.canDebug():    
                _logger.DEBUG(f'关闭遭遇错误:{e}')            
    
    def close(self):      
        if self.gf:
            self.gf.shutdown()
        else:    
            self._close_group()                   
        # self._close()   
            
    async def bind(self):        
        bootstrapFuture:BootstrapFuture = BootstrapFuture()
        bf:TripleFuture = bootstrapFuture.future       
         
        async def _bind(bootstrapFuture:BootstrapFuture):
            if self._address is None:
                raise NettyBaseError('ServerBootstrap启动必须指定Address，请使用address(address)指定监听地址')
            
            try:
                try:
                    _channel:ServerSocketChannel = self._channelcls(self._worker_eventloopGroup)        
                    self._channel = _channel
                    _channel.setAttributes(self._channel_option)
                    _channel.setChildAttributes(self._childchannel_option)
                    _channel.setSocketChannelInitializer(self._socketChannelInitializer)        
                    _server_socket = await _channel.bind(self._address)                
                    await bf.inited(_server_socket)
                except NetWorkError as e:
                    raise e          
                except BaseException as e:
                    raise e
            except BaseException as e:
                await bf.raise_init_exception(e)
                return
            
            await bf.wait_started()  
                
            try:      
                await _channel.start()           
                await bf.ended()
            except asyncio.exceptions.CancelledError as e:            
                if _logger.canDebug():
                    _logger.DEBUG(f'监听事件取消 {e}')
                await bf.ended()
                pass            
            except BaseException as e:
                _logger.DEBUG(f'{e}')
                # await future_set_exception_threadsafe(loop, f_stop, e)
                await bf.raise_end_exception(e)
                # raise e
            finally:
                self._close_serverchannel()
                                
        # 必须使用_worker_eventloopGroup 保证accept和r，w处理在一个事件循环环境里 
        self._worker_eventloopGroup.submit(_bind(bootstrapFuture))                
        
        try:
            try:
                # await future_await_threadsafe(w_loop, f)
                await bf.wait_inited()
                _logger.DEBUG('服务端口初始化成功')                
                return bootstrapFuture
            except BaseException as e:            
                raise NetWorkError(f'服务端口初始化出现故障{e}')        
        except BaseException as e:
            raise e        
    
    def grace(self):        
        async def _run(_gf:GracefulShutdown):           
            # _gf.start_shutdown_gracefully_await()                                                   
            # async def _bind(_gf:GracefulShutdown):
            #     await self.bind()            
            # # 必须使用_worker_eventloopGroup 保证accept和r，w处理在一个事件循环环境里 
            # self._worker_eventloopGroup.submit(_bind(_gf))
            # await _gf.wait_event()               
            try:                
                bf:BootstrapFuture = await self.bind()      
                rtn = bf.result()
                # rtn = await bf.future.wait_inited()
                if self._callback_sucess:
                    if is_coroutine_func(self._callback_sucess):
                        await self._callback_sucess(self, rtn)
                    else:
                        self._callback_sucess(self, rtn)                              
            except BaseException as e:
                # _logger.DEBUG(f'{get_fullname(e)}:{e}')                
                if self._callback_fail:
                    try:
                        if is_coroutine_func(self._callback_fail):
                            rtn = await self._callback_fail(self, e)
                        else:
                            rtn = self._callback_fail(self, e)
                        if isinstance(rtn, BootstrapFuture):
                            bf = rtn
                        else:
                            raise e
                    except BaseException as e:
                        raise e                        
                else:
                    raise e
                
            _logger.INFO('按下Ctrl-C，退出程序') 
            
            try:
                await bf.sync()
            except BaseException as e:    
                _logger.DEBUG(f'{get_fullname(e)}:{e}')
                raise e
            
        boss_loop = asyncio.new_event_loop()        
        asyncio.set_event_loop(boss_loop)   
         
        _gf:GracefulShutdown = GracefulShutdown(boss_loop,None, self._close_group)
        _gf.emit()        
        self.gf:GracefulShutdown = _gf
        _logger.INFO('按下Ctrl-C，退出服务器') 
        try:            
            boss_loop.run_until_complete(_run(_gf))        
        except BaseException as e:
            _logger.DEBUG(f'服务端异常{get_fullname(e)}:{e}')
        finally:           
            # _logger.DEBUG('停止 worker loop')
            # work_group.stop()                
            try:
                _logger.INFO('退出服务器程序')            
                boss_loop.stop()            
                boss_loop.close()
                _logger.INFO('退出服务器程序2')            
                self._close_group()
            except BaseException as e:
                _logger.DEBUG(f'{e}')
            # self._close()   
        pass


class Bootstrap:    
    _default_channel_config:dict = {
        ChannelOption.SO_BACKLOG.name:1024,
        ChannelOption.SO_REUSEADDR.name:True,
        ChannelOption.SO_KEEPALIVE.name:True,
        ChannelOption.ALLOCATOR.name:PooledByteBufferAllocator.DEFAULT,
        ChannelOption.WRITE_BUFFER_WATER_MARK.name:True,
        ChannelOption.SO_SNDBUF.name:32 * 1024,
        ChannelOption.SO_RCVBUF.name:32 * 1024,
        ChannelOption.SO_LINGER.name:None,        
        ChannelOption.TCP_NODELAY.name:True,
        ChannelOption.SO_CHUNKSIZE.name:1024,
        ChannelOption.SO_TIMEOUT.name:60
    }
    def __init__(self):        
        self._channel_option = Bootstrap._default_channel_config.copy()                        
        self._channel:SocketChannel = None
        self._channelcls = SocketChannel
        self._handler = None
        self._address = None
        self._shutdown_func = None
        self._shutdown_func_args = None
        self._shutdown_func_kargs = None        
        self._socketChannelInitializer = None
        self._worker_eventloopGroup = None
        self._callback_fail = None
        self._callback_sucess = None
        
    def when_connect_fail(self, callback)->'Bootstrap':
        assert callback and callable(callback),f'callback必须是callable对象，但是获得{callback}'
        self._callback_fail = callback
        return self
    def when_connect_sucess(self, callback)->'Bootstrap':
        assert callback and callable(callback),f'callback必须是callable对象，但是获得{callback}'
        self._callback_sucess = callback
        return self
    def group(self, eventloopGroup:CoroutineWorkGroup=None)->'Bootstrap':
        self._worker_eventloopGroup = eventloopGroup
        return self   
    def channel(self, socketChannel:type[SocketChannel]=SocketChannel)->'Bootstrap':
        assert socketChannel, 'socketChannel 必须 非None' 
        assert isinstance(socketChannel, type), f'必须是类型对象, 当前{socketChannel}[{type(socketChannel)}]'            
        assert issubclass(socketChannel, SocketChannel), f'必须是SocketChannel或者子类的类型对象, 当前{socketChannel}'            
        self._channelcls = socketChannel
        return self
    def option(self, option:ChannelOption, v:any)->'Bootstrap':
        self._channel_option.update({
            option.name:v
        })
        return self  
    def handler(self, socketChannelInitializer:SocketChannelInitializer)->'Bootstrap':        
        assert socketChannelInitializer, '不能使用None对象'
        assert isinstance(socketChannelInitializer, SocketChannelInitializer) or callable(socketChannelInitializer), f'必须是SocketChannelInitializer对象或者def initChannel(self, socketChannel:SocketChannel)方法，但是为{socketChannelInitializer}'
        self._socketChannelInitializer = socketChannelInitializer
        return self
    
    def address(self, address:tuple[str,int]):        
        self._address = address
        return self
    
    def shutdown_callback(self, shutdown_func:callable, *args, **kargs)->'Bootstrap':
        assert callable(shutdown_func), f'参数需要一个可调用对象，当前{shutdown_func}'                    
        assert not is_coroutine_func(shutdown_func),'务必使用同步方法释放资源，async方法可能不能执行完全就退出'
        
        self._shutdown_func = shutdown_func
        self._shutdown_func_args = args
        self._shutdown_func_kargs = kargs
        
        return self
    
    def _close_group(self):            
        if self._worker_eventloopGroup:
            try:
                if self._worker_eventloopGroup:
                    self._worker_eventloopGroup.stop()
            except Exception:
                pass  
            
        time.sleep(1)
        _logger.DEBUG('等待1s')
    
    def _close_channel(self):                        
        try:
            if self._shutdown_func:
                if _logger.canDebug():    
                    _logger.DEBUG(">>> 释放所有sock资源")                                    
                self._shutdown_func(*self._shutdown_func_args, **self._shutdown_func_kargs)
                
            if _logger.canDebug():                                        
                _logger.DEBUG('资源关闭结束')    
        except Exception as e:
            if _logger.canDebug():    
                _logger.DEBUG(f'关闭遭遇错误:{e}')            
    
    def close(self):     
        self._close_group()
        
    async def connect(self)->BootstrapFuture:
        bootstrapFuture:BootstrapFuture = BootstrapFuture()
        bf:TripleFuture = bootstrapFuture.future
        
        async def _connect(bootstrapFuture:BootstrapFuture):
            bf:TripleFuture = bootstrapFuture.future
            
            if self._address is None:
                raise NettyBaseError('Bootstrap启动必须指定Address，请使用address(address)指定监听地址')
            
            try:
                reader, writer = (await gather_with_timeout([asyncio.open_connection(self._address[0], self._address[1])], timeout=self._channel_option[ChannelOption.SO_TIMEOUT.name]))[0]                                  
                # reader, writer = await asyncio.open_connection(self._address[0], self._address[1]) 
                # f.set_result(True)
                # await future_set_value_threadsafe(loop, f, True) 
                await bf.inited((reader, writer))
            # except OSError as e:            
            #     raise NetWorkError(f'{e}')
            #     # future.set_result(True)
            except BaseException as e:
                # future.set_exception(e)
                # f.set_exception(e)
                # await future_set_exception_threadsafe(loop, f, e)
                await bf.raise_init_exception(e)
                return
            
            await bf.wait_started()            
            # await future_await_threadsafe(loop, f_start)
                
            try:     
                _logger.DEBUG('初始化Channel')
                socketChannel:SocketChannel = self._channelcls(reader, writer, self._channel_option)                
                socketChannel.setSocketChannelInitializer(self._socketChannelInitializer)
                self._channel = socketChannel              
                await socketChannel.start()                
                # await future_set_value_threadsafe(loop, f_stop, True)
                await bf.ended()
            except asyncio.exceptions.CancelledError as e:            
                if _logger.canDebug():
                    _logger.DEBUG(f'监听事件取消 {e}')
                # await future_set_value_threadsafe(loop, f_stop, True)
                # await bf.raise_end_exception(e)
                await bf.ended()
            except BaseException as e:
                _logger.DEBUG(f'{e}')
                # await future_set_exception_threadsafe(loop, f_stop, e)
                await bf.raise_end_exception(e)
                # raise e
            finally:            
                self._close_channel()
                                
        self._worker_eventloopGroup.submit(_connect(bootstrapFuture))
        
        try:
            try:
                # await future_await_threadsafe(w_loop, f)
                await bf.wait_inited()
                _logger.DEBUG('连接服务器成功')                
                return bootstrapFuture
            except TimeoutError:
                raise NetWorkError(f'连接事件超过{self._channel_option[ChannelOption.SO_TIMEOUT.name]}s，连接超时')
            except BaseException as e:            
                raise NetWorkError(f'连接出现故障{e}')        
        except BaseException as e:
            raise e        
    
    def grace(self):                
        async def _run(_gf:GracefulShutdown):     
            # _gf.start_shutdown_gracefully_await()
            try:
                bf:BootstrapFuture = await self.connect()      
                # rtn = await bf.future.wait_inited()
                rtn = bf.result()
                if self._callback_sucess:
                    if is_coroutine_func(self._callback_sucess):
                        await self._callback_sucess(self, *rtn)
                    else:
                        self._callback_sucess(self, *rtn)                              
            except BaseException as e:
                # _logger.DEBUG(f'{get_fullname(e)}:{e}')                
                if self._callback_fail:
                    try:
                        if is_coroutine_func(self._callback_fail):
                            rtn = await self._callback_fail(self, e)
                        else:
                            rtn = self._callback_fail(self, e)
                        if isinstance(rtn, BootstrapFuture):
                            bf = rtn
                        else:
                            raise e
                    except BaseException as e:
                        raise e                        
                else:
                    raise e
                
            _logger.INFO('按下Ctrl-C，退出程序') 
            
            try:
                await bf.sync()
            except BaseException as e:    
                _logger.DEBUG(f'{get_fullname(e)}:{e}')
                raise e
                
        work_loop = asyncio.new_event_loop()        
        asyncio.set_event_loop(work_loop)   
         
        _gf:GracefulShutdown = GracefulShutdown(work_loop,None, self._close_group)
        _gf.emit()   
        self.gf:GracefulShutdown = _gf        
        try:            
            work_loop.run_until_complete(_run(_gf))
        except KeyboardInterrupt: 
            if _logger.canDebug():               
                _logger.DEBUG('....')            
        except BaseException as e:
            if _logger.canDebug():
                _logger.DEBUG(f'{get_fullname(e)}:{e}')    
        finally:           
            # _logger.DEBUG('停止 worker loop')
            # work_group.stop()                
            _logger.INFO('退出程序')
            
            if _logger.canDebug():    
                _logger.DEBUG('停止EventLoop')
            work_loop.stop()
            
        pass

    
                
                    
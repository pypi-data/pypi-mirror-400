from pyboot.components.netty.channel import ChannelHandler,ChannelHandlerContext,T_BYTES_BYTEBUFFER,T,K   # noqa: F401
from pyboot.components.netty.channel import ChannelHandleError, ChannelError
from pyboot.commons.utils.bytes import ByteBuffer, PooledByteBufferAllocator,Endian,BytesUtils
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.utils import str_to_json,json_to_str
from pyboot.commons.coroutine.tools import is_coroutine_func
from pyboot.commons.utils.reflect import inspect_obj_generic_type
import asyncio  # noqa: F401
from typing import Generic,Callable
from abc import abstractmethod  
import os

_logger = Logger('pyboot.components.netty.codec')



class ByteToMessageError(ChannelHandleError): ...

class MessageToByteError(ChannelHandleError): ...

class ByteToMessageDecoder(ChannelHandler[ByteBuffer],Generic[T]):        
    async def channel_read(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer):
        if isinstance(bytebuffer, ByteBuffer):
            while bytebuffer.readable_bytes():
                # read_idx = bytebuffer.reader_index
                out:T = None                                
                try:
                    try:
                        out = await self.decode(ctx, bytebuffer)                
                    except ByteToMessageError as e:
                        if _logger.canDebug():
                            _logger.WARN(f'Decode出现错误{e}, 剩余{bytebuffer.readable_bytes()}字节数据, 数据内容{bytebuffer.get_readable_bytes()}')
                        # bytebuffer.clear()
                        raise e
                    except BaseException as e:                    
                        if _logger.canDebug():
                            _logger.WARN(f'Decode出现错误{e}, 剩余{bytebuffer.readable_bytes()}字节数据, 数据内容{bytebuffer.get_readable_bytes()}')
                        # bytebuffer.clear()
                        raise ChannelHandleError('Decode出现错误', e)
                            
                    if out is None:
                        if _logger.canDebug():
                            _logger.DEBUG('Decode没有解析到数据，重新读取数据到bytebuffer')
                        break
                    else:
                        try:
                            await ctx.fire_channel_read(out)
                        finally:
                            await self.close_decode(ctx, out)   
                except ChannelHandleError as e: 
                    raise e         
                except BaseException as e:                
                    if _logger.canDebug():
                        _logger.DEBUG(f'fire_channel_read或者close_decode出现错误{e}, 进行下一个进行处理')                    
                    raise e
        else:
            await ctx.fire_channel_read(bytebuffer)
                                    
    @abstractmethod
    async def decode(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->T:
        raise ChannelError(f'{type(self)}必须实现decode(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->T方法')
    
    async def close_decode(self, ctx: ChannelHandlerContext, out:T): ...
    
class MessageToMessageDecoder(ChannelHandler,Generic[T,K]): 
    def __init__(self):
        self._T_CLS = inspect_obj_generic_type(self)[0]
        # self._K_CLS = get_args(orig_cls)[0] if orig_cls else object
        
    async def channel_read(self, ctx: ChannelHandlerContext, data:T):
        if isinstance(data, self._T_CLS):
            out = []        
            try:
                try:
                    await self.decode(ctx, data, out)                                         
                except ByteToMessageError as e:
                    if _logger.canDebug():
                        _logger.WARN(f'Decode出现错误{e}, 数据内容{data}')
                    raise e                
                except BaseException as e:                    
                    if _logger.canDebug():
                        _logger.WARN(f'Decode出现错误{e}, 数据内容{data}')
                    raise ChannelHandleError('Decode出现错误', e)
            
                if out:
                    try:
                        for o in out:                        
                            await ctx.fire_channel_read(o)                        
                    except BaseException as e:                
                        if _logger.canDebug():
                            _logger.DEBUG(f'fire_channel_read出现错误{e}, 进行下一个进行处理')                    
                        raise e
                    finally:
                        await self.close_decode(ctx, out)
            except ChannelHandleError as e: 
                raise e         
            except BaseException as e:                
                if _logger.canDebug():
                    _logger.DEBUG(f'fire_channel_read或者close_decode出现错误{e}, 进行下一个进行处理')
                
                raise e  
        else:
            await ctx.fire_channel_read(data)
            
    @abstractmethod
    async def decode(self, ctx: ChannelHandlerContext, data:T, out:list[K]):
        raise ChannelError(f'{type(self)}必须实现decode(self, ctx: ChannelHandlerContext, data:T, out:list[K])方法')
        
    async def close_decode(self, ctx: ChannelHandlerContext, out:list[K]): ...


class MessageToByteEncoder(ChannelHandler[T],Generic[T]):        
    def __init__(self):
        self._T_CLS = inspect_obj_generic_type(self)[0]
        # self.pool_bucket_size = pool_bucket_size
        # self.buffer_size = buffer_size
    
    # def allocate_bytebuffer(self, size)->ByteBuffer:
    #     size = allocate_size(size, self.pool_bucket_size)
    #     buf = ByteToByteBufferMessageDecoder._BYTEBUFFER_POOL.allocate(size)
    #     return buf
    
    # def release_bytebuffer(self, out:ByteBuffer):
    #     ByteToByteBufferMessageDecoder._BYTEBUFFER_POOL.release(out)
    
    async def channel_write(self, ctx: ChannelHandlerContext, data:T):
        if isinstance(data, self._T_CLS):
            out:ByteBuffer = ctx.channel._write_buffer
            # out:ByteBuffer = self.allocate_bytebuffer(self.buffer_size)
            try:
                try:
                    await self.encode(ctx, data, out)
                    await ctx.fire_channel_write(out)
                except MessageToByteError as e:
                    if _logger.canDebug():
                        _logger.WARN(f'Encode出现错误{e}, 数据内容{data}')
                    raise e                
                except BaseException as e:                    
                    if _logger.canDebug():
                        _logger.WARN(f'Encode出现错误{e}, 数据内容{data}')
                    raise ChannelHandleError('Encode出现错误', e)            
            except ChannelHandleError as e: 
                raise e         
            except BaseException as e:                
                if _logger.canDebug():
                    _logger.DEBUG(f'fire_channel_write或者close_encode出现错误{e}, 进行下一个进行处理')
                
                raise ChannelHandleError('fire_channel_write或者close_encode出现错误, 进行下一个进行处理', e)   
            finally:
                # self.release_bytebuffer(out)
                pass
        else:
            await ctx.fire_channel_write(data)    
            
    @abstractmethod
    async def encode(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer):
        raise ChannelError(f'{type(self)}必须实现encode(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer)方法')    

class MessageToMessageEncoder(ChannelHandler[T],Generic[T,K]):        
    def __init__(self):
        self._T_CLS = inspect_obj_generic_type(self)[0]
        
    async def channel_write(self, ctx: ChannelHandlerContext, data:T):
        if isinstance(data, self._T_CLS):
            out = []        
            try:
                try:
                    await self.encode(ctx, data, out)                                         
                except ByteToMessageError as e:
                    if _logger.canDebug():
                        _logger.WARN(f'Encode出现错误{e}, 数据内容{data}')
                    raise e                
                except BaseException as e:                    
                    if _logger.canDebug():
                        _logger.WARN(f'Encode出现错误{e}, 数据内容{data}')
                    raise ChannelHandleError('Encode出现错误', e)
            
                if out:
                    try:
                        for o in out:
                            await ctx.fire_channel_write(o)                            
                    except BaseException as e:                
                        if _logger.canDebug():
                            _logger.DEBUG(f'fire_channel_write出现错误{e}, 进行下一个进行处理')                    
                        raise e
                    finally:
                        await self.close_encode(ctx, out)
            except ChannelHandleError as e: 
                raise e         
            except BaseException as e:                
                if _logger.canDebug():
                    _logger.DEBUG(f'fire_channel_write或者close_encode出现错误{e}, 进行下一个进行处理')
                
                raise ChannelHandleError('fire_channel_write或者close_encode出现错误, 进行下一个进行处理', e)   
        else:
            await ctx.fire_channel_write(data)
            
    @abstractmethod
    async def encode(self, ctx: ChannelHandlerContext, data:T, out:list[K]):
        raise ChannelError(f'{type(self)}必须实现encode(self, ctx: ChannelHandlerContext, data:T, out:list[K])方法')
        
    async def close_encode(self, ctx: ChannelHandlerContext, out:list[K]): ...
    
def allocate_size(len:int, chunk:int=1024)->int:    
    return int((len+chunk-1)/chunk) * chunk

class ByteToByteBufferMessageDecoder(ByteToMessageDecoder[ByteBuffer]):       
    _BYTEBUFFER_POOL:PooledByteBufferAllocator = PooledByteBufferAllocator.DEFAULT  
    def __init__(self, pool_bucket_size:int=1024):        
        self.pool_bucket_size = pool_bucket_size
        
    async def decode(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->ByteBuffer:
        out = self.decodeByteBuffer(ctx, bytebuffer)
        return out
    
    def allocate_bytebuffer(self, size)->ByteBuffer:
        size = allocate_size(size, self.pool_bucket_size)
        buf = ByteToByteBufferMessageDecoder._BYTEBUFFER_POOL.allocate(size)
        return buf
    
    # def release_bytebuffer(self, out:ByteBuffer):
    #     ByteToByteBufferMessageDecoder._BYTEBUFFER_POOL.release(out)
        
    async def decodeByteBuffer(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->ByteBuffer:
        raise ChannelError(f'{type(self)}必须实现decodeByteBuffer(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->ByteBuffer方法')
    
    async def close_decode(self, ctx: ChannelHandlerContext, out:ByteBuffer):
        if out is not None:
            ByteToByteBufferMessageDecoder._BYTEBUFFER_POOL.release(out)


class FixedLengthFrameDecoder(ByteToByteBufferMessageDecoder):
    def __init__(self, fix_length:int,pool_bucket_size:int=1024):        
        super().__init__(pool_bucket_size=pool_bucket_size)
        assert fix_length>0, f'Frame长度必须大于0，但是获得{fix_length}'
        self._fix_length = fix_length
        
    async def decode(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->ByteBuffer:
        if bytebuffer.readable_bytes()>=self._fix_length:
            buf = self.allocate_bytebuffer(self._fix_length)
            buf.write_from_reader(bytebuffer, self._fix_length)
            return buf
        else:
            return None

class LengthFieldBasedFrameDecoder(ByteToByteBufferMessageDecoder):
    # int maxFrameLength,      // 单帧最大字节数（防恶意包）
    # int lengthFieldOffset,   // “长度域”从第几个字节开始
    # int lengthFieldLength,   // 长度域本身占几个字节（1/2/4/8）
    # int lengthAdjustment,    // 长度数值需要修正多少（= 头部长度）
    # int initialBytesToStrip) // 解码后去掉前几个字节（常把头去掉）
    def __init__(self, 
                 length_field_length: int,                 
                 max_frame_length: int = 65536,
                 length_field_offset: int = 0,
                 length_adjustment: int = 0,
                 initial_bytes_to_strip: int = 0,
                 endian:Endian=Endian.BIG_ENDIAN,
                 fail_fast:bool=False,
                 pool_bucket_size:int=1024):
        super().__init__(pool_bucket_size=pool_bucket_size)
        assert length_field_length in (1,2,3,4,8), f'长度域本身占几个字节只能使用1/2/3/4/8,但是获得{length_field_length}'
        assert max_frame_length > 0, f'单帧最大字节数不能为0,但是获得{max_frame_length}'
        assert length_field_offset >= 0, f'“长度域”从第几个字节开始不能小于0,但是获得{length_field_offset}'
        assert initial_bytes_to_strip >= 0, f' 解码后去掉前几个字节不能小于0,但是获得{initial_bytes_to_strip}'
        assert length_field_offset <= max_frame_length - length_field_length, '长度域”从第几个字节开始超过了最大帧长度限制'
        
        self._max_frame_length = max_frame_length
        self._length_field_length = length_field_length
        self._length_field_offset = length_field_offset
        self._length_adjustment = length_adjustment
        self._initial_bytes_to_strip = initial_bytes_to_strip
        self._length_field_length = length_field_length
        self._endian = endian
        self._fail_fast = fail_fast
        
        
        # 长度字段过大标记
        self._discarding_too_long_frame = False
        self._too_long_frame_length = 0
        self._bytes_to_discard = 0
    
    
    async def decode(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->ByteBuffer:        
        """
        解码方法        
        返回:
        - 完整的帧缓冲区，如果帧不完整则返回None
        """        
        # 如果正在丢弃过长的帧
        if self._discarding_too_long_frame:
            return await self._handle_discarding_frame(bytebuffer)
        
        # 检查是否有足够的字节读取长度字段
        if bytebuffer.readable_bytes() < self._length_field_offset + self._length_field_length:
            return None
        
        # 读取长度字段
        actual_length_field_offset = bytebuffer.reader_index + self._length_field_offset
        frame_length = self._get_unadjusted_frame_length(bytebuffer, actual_length_field_offset)
        
        # 如果长度字段为负数
        if frame_length < 0:
            bytebuffer.skip_bytes(self._length_field_offset + self._length_field_length)
            raise ChannelHandleError(f"负长度字段: {frame_length}")
        
        # 计算调整后的帧长度
        frame_length += self._length_adjustment + self._length_field_offset + self._length_field_length
        
        # 检查帧长度是否超过最大限制
        if frame_length > self._max_frame_length:
            # 记录要丢弃的字节数
            exceed_length = frame_length - bytebuffer.readable_bytes()
            if exceed_length < 0:
                exceed_length = 0
                
            self._discarding_too_long_frame = True
            self._too_long_frame_length = frame_length
            self._bytes_to_discard = exceed_length
            
            # 跳过当前已读取的字节
            bytebuffer.skip_bytes(self._length_field_offset + self._length_field_length)
            
            # 快速失败
            if self._fail_fast:
                self._fail(ctx, frame_length)
                return None
                
            return None
        
        # 检查是否有完整的帧
        if bytebuffer.readable_bytes() < frame_length:
            return None
        
        # 如果有足够的字节，提取帧
        if self._initial_bytes_to_strip > frame_length:
            raise ChannelHandleError(f"initial_bytes_to_strip丢弃参数字节数({self._initial_bytes_to_strip})大于帧字节数({frame_length})")
        
        # 跳过指定的字节数
        bytebuffer.skip_bytes(self._initial_bytes_to_strip)
        
        # 计算实际要读取的字节数
        actual_frame_length = frame_length - self._initial_bytes_to_strip
        
        # 分配缓冲区并读取帧
        buf = self.allocate_bytebuffer(actual_frame_length)
        buf.write_from_reader(bytebuffer, actual_frame_length)
        
        return buf
        
    async def _handle_discarding_frame(self, bytebuffer: ByteBuffer) -> ByteBuffer:
        """
        处理丢弃过长的帧
        """
        readable_bytes = bytebuffer.readable_bytes()
        
        if readable_bytes < self._bytes_to_discard:
            # 还没有足够的数据丢弃，继续等待
            self._bytes_to_discard -= readable_bytes
            bytebuffer.skip_bytes(readable_bytes)
            return None
        
        # 丢弃足够的字节
        bytebuffer.skip_bytes(self._bytes_to_discard)        
        # 重置状态
        self._discarding_too_long_frame = False
        self._bytes_to_discard = 0        
        # 如果快速失败已经抛出异常，这里不需要再处理
        return None
    
    def _get_unadjusted_frame_length(self, bytebuffer: ByteBuffer, offset: int) -> int:
        """
        从指定偏移量读取未调整的长度字段值
        
        返回:
        - 长度字段的值
        """
        # 保存当前位置
        old_reader_index = bytebuffer.reader_index
        bytebuffer.reader_index = offset
        
        try:
            length = bytebuffer.read_int_n(self._length_field_length, self._endian)            
            return length
        finally:
            # 恢复原来的位置
            bytebuffer.reader_index = old_reader_index
    
    def _fail(self, ctx: ChannelHandlerContext, frame_length: int) -> None:
        """
        处理帧过长的失败情况
        
        参数:
        - ctx: 通道处理器上下文
        - frame_length: 帧长度
        """
        error_msg = f"帧长度({frame_length})超过了最大限制({self._max_frame_length})"
        
        # 如果通道可用，通过通道发送异常
        if ctx.channel and ctx.channel.is_active():
            ctx.fire_exception_caught(ValueError(error_msg))
            ctx.channel.close()
        else:
            raise ValueError(error_msg)
    
    
    async def exception_caught(self, ctx: ChannelHandlerContext, exception: BaseException):
        """
        异常处理
        
        参数:
        - ctx: 通道处理器上下文
        - cause: 异常
        """
        # 重置状态
        self._discarding_too_long_frame = False
        self._bytes_to_discard = 0
        
        # 传递异常
        await ctx.fire_exception_caught(exception)

class DelimiterBasedFrameDecoderError(ByteToMessageError) :...

class DelimiterBasedFrameDecoder(ByteToByteBufferMessageDecoder):
    #  maxLength Maximum length of a frame we're willing to decode. 
    #  failFast Whether or not to throw an exception as soon as we exceed maxLength
    #  stripDelimiter Whether or not to strip delimiter as soon as we exceed maxLength   
    #  ignoreEmpty 是否忽略空Frame
    #  pool_bucket_size ByteBuffer池化的桶大小    
    def __init__(self, delimiter:list[bytes], maxLength:int=None, failFast:bool=True, stripDelimiter:bool=True,ignoreEmpty:bool=True,pool_bucket_size:int=1024):
        assert delimiter, f'基于分隔符的字节流，分隔符不能为空，但是获得{delimiter}'
        super().__init__(pool_bucket_size=pool_bucket_size)
        
        if not maxLength or maxLength < 0:
            maxLength = 0
        self.maxLength = maxLength
        self.delimiter = delimiter
        self.failFast = failFast
        self.stripDelimiter = stripDelimiter
        self.ignoreEmpty = ignoreEmpty
        self.pool_bucket_size = pool_bucket_size
        
    async def decode(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer)->ByteBuffer:                
        # 查找所有分隔符的位置                                        
        while True:
            delimiter_positions = -1
            delimiter_positions_delimiter:bytes = None
            # data = None
            buf:ByteBuffer = None
            
            for delim in self.delimiter:
                if delim:  # 确保分隔符不为空         
                    # if last_start_positions == 0:
                    #     pos = bytebuffer.find(delim, 0)
                    # else:
                    #     pos = bytebuffer.find(delim, last_start_positions)
                    pos = bytebuffer.find(delim, 0)
                                                    
                    if pos >= 0:
                        if pos <= delimiter_positions or delimiter_positions==-1:
                            delimiter_positions = pos - bytebuffer.reader_index
                            delimiter_positions_delimiter = delim  # noqa: F841
                            
            if delimiter_positions <= -1 :   
                bytes_len = bytebuffer.readable_bytes()
                if self.maxLength > 0 and bytes_len > self.maxLength:
                    if self.failFast:
                        raise DelimiterBasedFrameDecoderError(f'没有找到分隔符号，当前缓存长度{bytes_len},最大长度{self.maxLength}')
                    
                _logger.WARN(f'没有找到分隔符号，当前缓存长度{bytes_len} , 字节数据{bytebuffer.get_readable_bytes()}')
                return None
            else:
                # needRead_len = delimiter_positions - last_start_positions
                needRead_len = delimiter_positions
                if self.maxLength > 0 and needRead_len > self.maxLength:
                    if self.failFast:
                        raise DelimiterBasedFrameDecoderError(f'当前长度{needRead_len},最大长度{self.maxLength}')
                
                if needRead_len > 0:
                    if self.stripDelimiter:
                        # size = allocate_size(needRead_len, self.pool_bucket_size)
                        # buf = DelimiterBasedFrameDecoder._BYTEBUFFER_POOL.allocate(size)
                        buf = self.allocate_bytebuffer(needRead_len)
                        buf.write_from_reader(bytebuffer, needRead_len)
                        # data = bytebuffer.read_bytes(needRead_len)
                        bytebuffer.read_bytes(len(delimiter_positions_delimiter))
                    else:
                        needRead_len = needRead_len + len(delimiter_positions_delimiter)                        
                        # size = allocate_size(needRead_len, self.pool_bucket_size)
                        # buf = DelimiterBasedFrameDecoder._BYTEBUFFER_POOL.allocate(size)
                        buf = self.allocate_bytebuffer(needRead_len)
                        buf.write_from_reader(bytebuffer, needRead_len)                        
                else:                    
                    bytebuffer.read_bytes(len(delimiter_positions_delimiter))  
                    if self.ignoreEmpty:
                        _logger.WARN('空数据获不做处理')
                    else:    
                        if self.stripDelimiter:
                            # buf = DelimiterBasedFrameDecoder._BYTEBUFFER_POOL.allocate(allocate_size(0, self.pool_bucket_size))
                            buf = self.allocate_bytebuffer(0)
                            # data = b''                                                      
                        else:
                            # buf = DelimiterBasedFrameDecoder._BYTEBUFFER_POOL.allocate(allocate_size(len(delimiter_positions_delimiter), self.pool_bucket_size))
                            buf = self.allocate_bytebuffer(len(delimiter_positions_delimiter))
                            buf.write_bytes(delimiter_positions_delimiter)
                            # data = delimiter_positions_delimiter                            
                
                # if data is not None:               
                #     if _logger.canDebug():    
                #         _logger.DEBUG(f'解析到字节数据{data},进行ctx.fire_channel_read(bytes)')
                #     size = allocate_size(len(data), 1024)
                #     buf = DelimiterBasedFrameDecoder._BYTEBUFFER_POOL.allocate(size)
                #     buf.write_bytes(data)
                #     return buf 
                
                if buf is not None:
                    if _logger.canDebug():    
                        _logger.DEBUG(f'解析到字节数据{buf.to_bytes()},进行ctx.fire_channel_read(bytes)')
                    return buf 
                             
                bytes_len = bytebuffer.readable_bytes()                     
                if bytes_len==0:
                    break
                
        bytes_len = bytebuffer.readable_bytes() 
        if 0 == bytes_len:
            pass
        else:
            if _logger.canDebug():    
                _logger.DEBUG(f'未解析字节{bytes_len}, 字节数据{bytebuffer.to_bytes()}')
        return None
        
        
class ByteDelimiterBasedFrameDecoder(ChannelHandler[T_BYTES_BYTEBUFFER]):
    
    #  maxLength Maximum length of a frame we're willing to decode. 
    #  failFast Whether or not to throw an exception as soon as we exceed maxLength
    #  stripDelimiter Whether or not to strip delimiter as soon as we exceed maxLength    
    def __init__(self, delimiter:list[bytes], maxLength:int=None, failFast:bool=True, stripDelimiter:bool=True,ignoreEmpty:bool=True):
        assert delimiter, f'基于分隔符的字节流，分隔符不能为空，但是获得{delimiter}'
        if not maxLength or maxLength < 0:
            maxLength = 0
        self.maxLength = maxLength
        self.delimiter = delimiter
        self.failFast = failFast
        self.stripDelimiter = stripDelimiter
        self.ignoreEmpty = ignoreEmpty
        
    async def channel_read(self, ctx: ChannelHandlerContext, bytebuffer: ByteBuffer|bytes):        
        if isinstance(bytebuffer, (bytes, bytearray)):
            bytebuffer:bytes = bytebuffer
            
                # 查找所有分隔符的位置
            last_start_positions = 0
            
            bytes_len = len(bytebuffer) 
            
            while True:
                delimiter_positions = -1
                delimiter_positions_delimiter = None
                data = None
                
                for delim in self.delimiter:
                    if delim:  # 确保分隔符不为空
                        if last_start_positions == 0:
                            pos = bytebuffer.find(delim, 0)
                        else:
                            pos = bytebuffer.find(delim, last_start_positions)
                            
                        if pos >= 0:
                            if pos <= delimiter_positions or delimiter_positions==-1:
                                delimiter_positions = pos
                                delimiter_positions_delimiter = delim  # noqa: F841
                                
                if delimiter_positions == -1 :                    
                    if self.maxLength > 0 and bytes_len - last_start_positions > self.maxLength:
                        if self.failFast:
                            raise DelimiterBasedFrameDecoderError(f'没有找到分隔符号，当前缓存长度{len(bytebuffer) - last_start_positions},最大长度{self.maxLength}')
                        
                    _logger.WARN(f'没有找到分隔符号，当前缓存长度{len(bytebuffer) - last_start_positions} , 字节数据{bytebuffer[last_start_positions:]}')
                    break
                else:
                    if self.maxLength > 0 and delimiter_positions - last_start_positions > self.maxLength:
                        if self.failFast:
                            raise DelimiterBasedFrameDecoderError(f'当前长度{delimiter_positions - last_start_positions},最大长度{self.maxLength}')
                    
                    if delimiter_positions > last_start_positions:
                        if self.stripDelimiter:
                            data = bytebuffer[last_start_positions:delimiter_positions]
                        else:
                            data = bytebuffer[last_start_positions:delimiter_positions+len(delimiter_positions_delimiter)]                        
                    else:
                        if self.ignoreEmpty:
                            _logger.WARN('空数据获不做处理')
                        else:    
                            if self.stripDelimiter:
                                data = b''
                            else:
                                data = delimiter_positions_delimiter
                            
                    last_start_positions = delimiter_positions + len(delimiter_positions_delimiter)                                            
                    
                    if data is not None:
                        if _logger.canDebug():    
                            _logger.DEBUG(f'解析到字节数据{data},进行ctx.fire_channel_read(bytes)')
                        if ctx:                        
                            await ctx.fire_channel_read(data)
                    
                    if bytes_len<=last_start_positions:
                        break
                    
            length = (last_start_positions)
            if length == bytes_len:
                pass
            else:
                if _logger.canDebug():    
                    _logger.DEBUG(f'未解析字节{len(bytebuffer) - length}, 字节数据{bytebuffer[length:]}')
                                
        elif isinstance(bytebuffer, ByteBuffer):
            bytebuffer:ByteBuffer = bytebuffer
            last_start_positions = 0
            # 查找所有分隔符的位置                                        
            while True:
                delimiter_positions = -1
                delimiter_positions_delimiter = None
                data = None
                
                for delim in self.delimiter:
                    if delim:  # 确保分隔符不为空         
                        # if last_start_positions == 0:
                        #     pos = bytebuffer.find(delim, 0)
                        # else:
                        #     pos = bytebuffer.find(delim, last_start_positions)
                        pos = bytebuffer.find(delim, 0)
                                                       
                        if pos >= 0:
                            if pos <= delimiter_positions or delimiter_positions==-1:
                                delimiter_positions = pos - bytebuffer.reader_index
                                delimiter_positions_delimiter = delim  # noqa: F841
                                
                if delimiter_positions <= -1 :   
                    bytes_len = bytebuffer.readable_bytes()
                    if self.maxLength > 0 and bytes_len > self.maxLength:
                        if self.failFast:
                            raise DelimiterBasedFrameDecoderError(f'没有找到分隔符号，当前缓存长度{bytes_len},最大长度{self.maxLength}')
                        
                    _logger.WARN(f'没有找到分隔符号，当前缓存长度{bytes_len} , 字节数据{bytebuffer.get_readable_bytes()}')
                    break
                else:
                    # needRead_len = delimiter_positions - last_start_positions
                    needRead_len = delimiter_positions
                    if self.maxLength > 0 and needRead_len > self.maxLength:
                        if self.failFast:
                            raise DelimiterBasedFrameDecoderError(f'当前长度{needRead_len},最大长度{self.maxLength}')
                    
                    if needRead_len > 0:
                        if self.stripDelimiter:
                            data = bytebuffer.read_bytes(needRead_len)
                            bytebuffer.read_bytes(len(delimiter_positions_delimiter))
                        else:
                            data = bytebuffer.read_bytes(needRead_len+len(delimiter_positions_delimiter))
                    else:
                        
                        bytebuffer.read_bytes(len(delimiter_positions_delimiter))  
                        if self.ignoreEmpty:
                            _logger.WARN('空数据获不做处理')
                        else:    
                            if self.stripDelimiter:
                                data = b''                                                      
                            else:
                                data = delimiter_positions_delimiter                            
                    
                    # last_start_positions = delimiter_positions + len(delimiter_positions_delimiter)     
                    if data is not None:               
                        if _logger.canDebug():    
                            _logger.DEBUG(f'解析到字节数据{data},进行ctx.fire_channel_read(bytes)')
                        if ctx:
                            await ctx.fire_channel_read(data)
                    
                    bytes_len = bytebuffer.readable_bytes()                     
                    if bytes_len==0:
                        break
                    
            bytes_len = bytebuffer.readable_bytes() 
            if 0 == bytes_len:
                pass
            else:
                if _logger.canDebug():    
                    _logger.DEBUG(f'未解析字节{bytes_len}, 字节数据{bytebuffer.get_readable_bytes()}')
                            
            # # 查找所有分隔符的位置
            # delimiter_positions = []
            # for delim in self.delimiter:
                
            # await ctx.fire_channel_read(data)
        else:
            if _logger.canDebug():            
                _logger.WARN(f'{bytebuffer}不是{T_BYTES_BYTEBUFFER}类型，直接跳过并进行下一个处理')
            await ctx.fire_channel_read(bytebuffer)


class LineBasedFrameDecoder(DelimiterBasedFrameDecoder):
    def __init__(self, maxLength:int=None, failFast:bool=True, stripDelimiter:bool=True,ignoreEmpty:bool=True):
        super().__init__([b'\n',b'\r\n'], maxLength=maxLength, failFast=failFast, stripDelimiter=stripDelimiter, ignoreEmpty=ignoreEmpty)
       
          
class StringDecoder(MessageToMessageDecoder[T_BYTES_BYTEBUFFER, str]):
    def __init__(self, charset:str='utf-8', strip:bool=True):
        super().__init__()
        
        charset = charset or 'utf-8'
        self.charset = charset
        self.strip = strip    
                
    async def decode(self, ctx: ChannelHandlerContext, data:T_BYTES_BYTEBUFFER, out:list[str]):
        buf = None
        if isinstance(data, (bytes, bytearray)):
            buf = data
        elif isinstance(data, ByteBuffer):
            data:ByteBuffer = data
            buf = data.read_bytes(data.readable_bytes())
        
        if buf is not None:            
            str = buf.decode(encoding=self.charset).strip() if self.strip else buf.decode(encoding=self.charset)
            if _logger.canDebug():
                _logger.DEBUG(f'处理字节数据{buf}, 字符串数据[charset={self.charset},strip={self.strip}]={str}')
            out.append(str)
                        
class JsonDecoder(MessageToMessageDecoder[T_BYTES_BYTEBUFFER, dict]):
    def __init__(self, charset:str='utf-8'):
        super().__init__()
        
        charset = charset or 'utf-8'
        self.charset = charset
    
    async def decode(self, ctx: ChannelHandlerContext, data:T_BYTES_BYTEBUFFER, out:list[dict]):
        buf = None
        if isinstance(data, (bytes, bytearray)):
            buf = data
        elif isinstance(data, ByteBuffer):
            data:ByteBuffer = data
            buf = data.read_bytes(data.readable_bytes())
        
        if buf is not None:            
            str = buf.decode(encoding=self.charset).strip() if self.strip else buf.decode(encoding=self.charset)
            obj = str_to_json(str)
            if _logger.canDebug():
                _logger.DEBUG(f'处理字节数据{buf}, 字符串数据[charset={self.charset},strip={self.strip}]={obj}')
            out.append(obj)
            

class LengthFieldBasedFrameEncoder(MessageToByteEncoder[T],Generic[T]):
    def __init__(self):
        super().__init__()
    
    @abstractmethod
    async def encode_header(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer):    
        raise ChannelError(f'{type(self)}必须实现encode_header(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer)方法')
    
    @abstractmethod
    async def encode_data(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer):
        raise ChannelError(f'{type(self)}必须实现encode_data(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer)方法') 
                    
    async def encode(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer):
        await self.encode_header(ctx, data, out)
        await self.encode_data(ctx, data, out)

class SimpleBytesLengthFieldBasedFrameEncoder(LengthFieldBasedFrameEncoder[T_BYTES_BYTEBUFFER]):
    @staticmethod
    def default_fill_header_callback(data_length:int, data:T_BYTES_BYTEBUFFER, out:ByteBuffer):
        out.write_bytes(b'\1\0\2\2')
        out.write_int(data_length, Endian.BIG_ENDIAN)
    
    def __init__(self, fix_header_callback:Callable=None):
        fix_header_callback = fix_header_callback or SimpleBytesLengthFieldBasedFrameEncoder.default_fill_header_callback
        super().__init__()
        assert callable(fix_header_callback), f'fix_header_callback必须是一个函数,但是获得{fix_header_callback}'
        self._fix_header_callback = fix_header_callback        
        
    async def encode_header(self, ctx: ChannelHandlerContext, data:T_BYTES_BYTEBUFFER, out:ByteBuffer): 
        data_length = 0
        if isinstance(data, (bytes, bytearray)):            
            data_length = len(data)
        elif isinstance(data, ByteBuffer):
            data:ByteBuffer = data
            data_length = data.readable_bytes()
            
        if is_coroutine_func(self._fix_header_callback):
            await self._fix_header_callback(data_length, data, out)
        else:
            self._fix_header_callback(data_length, data, out)
                    
    async def encode_data(self, ctx: ChannelHandlerContext, data:T_BYTES_BYTEBUFFER, out:ByteBuffer):     
        if isinstance(data, (bytes, bytearray)):            
            out.write_bytes(data)
        elif isinstance(data, ByteBuffer):
            out.write_from_reader(data)

class FixedLengthFrameEncoder(MessageToByteEncoder[T_BYTES_BYTEBUFFER]):
    def __init__(self, fix_length:int, left_padding:bool=True, fill:bytes=b'\0'):        
        super().__init__()
        assert len(fill) == 1, f'fill必须是一个字节，但是获得{fill}'
        assert fix_length>0, f'Frame长度必须大于0，但是获得{fix_length}'
        self._fix_length = fix_length
        self._left_padding = left_padding        
        self._fill = fill
        
    async def encode(self, ctx: ChannelHandlerContext, data:T_BYTES_BYTEBUFFER, out:ByteBuffer):
        if isinstance(data, (bytes, bytearray)):
            if self._left_padding:
                data = BytesUtils.r_bytes(data, self._fix_length, trim=True)
            else:
                data = BytesUtils.l_bytes(data, self._fix_length, trim=True)            
            out.write_bytes(data)
        elif isinstance(data, ByteBuffer):
            data:ByteBuffer = data
            readable = data.readable_bytes()
            if readable >= self._fix_length:
                out.write_from_reader(data, self._fix_length)
            else:
                fillcount = self._fix_length - readable
                if self._left_padding:                    
                    for i in range(fillcount):
                        out.write_bytes(self._fill)
                    out.write_from_reader(data, readable)
                else:
                    out.write_from_reader(data, readable)
                    for i in range(fillcount):
                        out.write_bytes(self._fill)            

class StringEncoder(MessageToByteEncoder[str]):
    def __init__(self, charset:str='utf-8', end:str=os.linesep):
        super().__init__()        
        charset = charset or 'utf-8'
        self.charset = charset
        self.end = end
    
    async def encode(self, ctx: ChannelHandlerContext, data:T, out:ByteBuffer):
        data = f'{data}{self.end if self.end else ''}'.encode(self.charset)
        out.write_bytes(data)
    # async def encode(self, ctx: ChannelHandlerContext, data:str, out:list[bytes]):
    #     data = f'{data}{self.end if self.end else ''}'
    #     out.append(data.encode(self.charset))

class JsonEncoder(MessageToMessageEncoder[dict, str]):
    def __init__(self):
        super().__init__()
        
    async def encode(self, ctx: ChannelHandlerContext, data:dict, out:list[bytes]):        
        out.append(json_to_str(data))
    
# class StringDecoder(ChannelHandler[bytes]):
#     def __init__(self, charset:str='utf-8', strip:bool=True):
#         charset = charset or 'utf-8'
#         self.charset = charset
#         self.strip = strip
            
#     async def channel_read(self, ctx: ChannelHandlerContext, data:bytes):                
#         str = data.decode(encoding=self.charset).strip() if self.strip else data.decode(encoding=self.charset)
        
#         _logger.DEBUG(f'处理字节数据{data}, 字符串数据[charset={self.charset},strip={self.strip}]={str}')
        
#         if ctx:
#             await ctx.fire_channel_read(str)        



async def testStringDecoder(data:bytes, charset:str='utf-8', strip:bool=True):
    s = StringDecoder(charset, strip)
    await s.channel_read(None, data)

async def testString():
    await testStringDecoder('1234567890中国\r\n'.encode())    

async def testparse(d:list[bytes], data:bytes, strip:bool=True, maxLength:int=0,fail:bool=True,ignoreEmpty:bool=True):
    _logger.DEBUG(f'测试Bytes解析{data}, 分隔符={d};strip={strip}')
    dh = ByteDelimiterBasedFrameDecoder(d, stripDelimiter=strip, maxLength=maxLength, failFast=fail, ignoreEmpty=ignoreEmpty)
    await dh.channel_read(None, data)
    _logger.DEBUG('解析结束')
    _logger.DEBUG('')
    
async def testparse_bytebuffer(d:list[bytes], datas:bytes, bf:ByteBuffer, strip:bool=True, maxLength:int=0,fail:bool=True,ignoreEmpty:bool=True):
    bf.write_bytes(datas)
    _logger.DEBUG(f'测试ByteBuffer解析{datas}, 分隔符={d};strip={strip}')
    _logger.DEBUG(f'ByteBuffer数据:{bf.get_readable_bytes()}')
    dh = ByteDelimiterBasedFrameDecoder(d, stripDelimiter=strip, maxLength=maxLength, failFast=fail, ignoreEmpty=ignoreEmpty)
    await dh.channel_read(None, bf)
    _logger.DEBUG(f'ByteBuffer未读数据:{bf.get_readable_bytes()}')
    _logger.DEBUG('解析结束')
    _logger.DEBUG('')
                
async def test():
    await testparse([b'40', b'80'], b'1112222333340777789898980', False)    
    await testparse([b'44', b'84'], b'1112222333340777789898980',maxLength=10, fail=False)
    await testparse([b'44', b'80'], b'1112222333340777789898980', False)
    await testparse([b'44', b'8980'], b'1112222333340777789898980')
    await testparse([b'44', b'89'], b'111222233334077778989898011', False)
    await testparse([b'44', b'89'], b'44111222233334077778989898011', False,ignoreEmpty=True)
    await testparse([b'44', b'89'], b'44111222233334077778989898011', True,ignoreEmpty=False)
    
    buf:ByteBuffer = ByteBuffer.buffer(256)    
    await testparse_bytebuffer([b'40', b'80'], b'1112222333340777789898980', buf, False,ignoreEmpty=False)    
    await testparse_bytebuffer([b'44', b'84'], b'1112222333340777789898980', buf, maxLength=10, fail=False)
    await testparse_bytebuffer([b'44', b'80'], b'1112222333340777789898980', buf, False)
    await testparse_bytebuffer([b'44', b'8980'], b'1112222333340777789898980', buf)
    await testparse_bytebuffer([b'44', b'89'], b'111222233334077778989898011', buf, False)
    await testparse_bytebuffer([b'44', b'89'], b'4411122223333407777898989', buf, False, ignoreEmpty=True)
    await testparse_bytebuffer([b'44', b'89'], b'4411122223333407777898989', buf, False, ignoreEmpty=False)
    await testparse_bytebuffer([b'44', b'89'], b'4411122223333407777898989', buf, False)
    
    await testparse_bytebuffer([b'\r\n', b'\n'], 'This is a test，中文\r\n英文orThis is a 中文\nhello world\n\n\n'.encode(), buf, False)

    
if __name__ == "__main__":        
    asyncio.run(test())
    
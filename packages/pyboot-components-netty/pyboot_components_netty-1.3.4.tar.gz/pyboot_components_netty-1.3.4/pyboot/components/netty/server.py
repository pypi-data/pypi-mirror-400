from pyboot.components.netty.channel import ChannelOption,SocketChannel,ServerSocketChannel
from pyboot.components.netty.bootstrap import ServerBootstrap,ignore_gc_warning
from pyboot.components.netty.handler import LoggingHandler
from pyboot.components.netty.codec import MessageToMessageDecoder,StringDecoder
from typing import Self
from pyboot.commons.coroutine.task import CoroutineWorkGroup
from pyboot.commons.utils.bytes import ByteBuffer,PooledByteBufferAllocator
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.utils import str2Num,str_to_json,r_str
from pyboot.components.netty.channel import ChannelHandler,ChannelHandlerContext,ChannelHandleError
from pyboot.commons.utils.utils import parse_long_args_plus

_logger = Logger('pyboot.components.netty.server')

ignore_gc_warning()

class Server:
    def __init__(self, name:str, address:tuple[str,int]):
        self._address = address        
        self._logging = False
        self._log_level = None
        self._name = name
        self._bs = None
        
    def log(self, log_level:Logger.LEVEL=Logger.LEVEL.INFO)->Self:
        self._logging = True            
        self._log_level = log_level or Logger.LEVEL.INFO
        return self
    
    def option(self, option:ChannelOption, v:any)->Self:
        self._bs.option(option, v)
        return self
    
    def childOption(self, option:ChannelOption, v:any)->Self:
        self._bs.childOption(option, v)
        return self
    
    def initHandler(self, sc:SocketChannel):
        raise ValueError(f'{type(self)}initHandler(self, sc:SocketChannel)方法')
    
    def start(self):
        def initChannel(sc:SocketChannel):
            if self._logging:
                sc.pipeline().add_last(LoggingHandler(self._log_level))
            self.initHandler(sc)       
        
        boss_group = CoroutineWorkGroup(1,f"{self._name}-BossGroup")                
        
        self._bs = ServerBootstrap().group(boss_group)\
        .channel(ServerSocketChannel).childHandler(initChannel)\
            .option(ChannelOption.SO_BACKLOG, 1024).option(ChannelOption.ALLOCATOR, PooledByteBufferAllocator.DEFAULT)\
                .address(self._address)        
        self._bs.grace()
        
class EchoServer(Server):    
    def __init__(self, address:tuple[str,int]=('0.0.0.0',1234)):
        super().__init__('EchoServer', address)    
    def initHandler(self, sc:SocketChannel):
        _pipeline = sc.pipeline()
        _pipeline.add_last(EchoHandler())

def echo_server():
    args = parse_long_args_plus()
    port = 1234
    host = '0.0.0.0'
    if 'port' in args:
        port = args['port']
    if 'host' in args:
        host = args['host']        
    es:EchoServer = EchoServer((host, port))    
    if 'log_level' in args:
        log_level = args['log_level']
        log_level = Logger.level(log_level)
        es.log(log_level)        
    es.start()

class EchoHandler(ChannelHandler[ByteBuffer]):
    async def channel_read(self, ctx: ChannelHandlerContext, data: ByteBuffer):
        await ctx.channel.write(data)

class HJ212Frame: 
    def __init__(self):        
        self.mn = None
        self.size = 0        
        self.headdata = {}
        self.data = {}
        self.raw = None
        self.crc = None
        
    def __repr__(self):
        return f'MN={self.mn} Header={self.headdata} Data={self.data} Raw={self.raw} Crc={self.crc}'
        
    @staticmethod
    def parse_frame(msg:str,ignore_crc:bool=False)->Self:
        
        if not msg.startswith(HJ212FrameDecoder.FIX_SPLIT_CHAR):
            msg = HJ212FrameDecoder.FIX_SPLIT_CHAR + msg
        
        msg = msg.replace(";"+HJ212FrameDecoder.FIX_COMMAND_CHAR, HJ212FrameDecoder.FIX_COMMAND_CHAR)
        sub_msg = msg.split(HJ212FrameDecoder.FIX_COMMAND_CHAR)
        headStr = sub_msg[0][HJ212FrameDecoder.FIX_LENGTH_INDEX:].replace(";CP=", "").replace("=", "\":\"").replace(",", "\",\"").replace(";", "\",\"")
        frame = HJ212Frame()
        frame.raw = sub_msg[0][HJ212FrameDecoder.FIX_SPLIT_LENGTH:] + HJ212FrameDecoder.FIX_COMMAND_CHAR + sub_msg[1] + HJ212FrameDecoder.FIX_COMMAND_CHAR
        frame.size = str2Num(headStr[0:4])
        frame.headdata = str_to_json("{\"" + headStr[4:] + "\"}")
        assert "MN" in frame.headdata, f'格式错误，请查看HJ212协议格式参考，MN必须有值，但是获得{sub_msg[0]}'
        frame.mn = frame.headdata["MN"]
        paramStr = sub_msg[1].replace("=", "\":\"").replace(",", "\",\"").replace(";", "\",\"")
        # assert paramStr, f'格式错误，请查看HJ212协议格式参考，数据区必须有值，但是获得{sub_msg[1]}'        
        if paramStr:
            frame.data = str_to_json("{\"" + paramStr + "\"}")
        else:
            frame.data = {}
        frame.crc = sub_msg[2]
        
        if not ignore_crc:
            crc = HJ212Frame.crcCheckCode(frame.raw)
            if crc != frame.crc:
                raise ChannelHandleError(f'CRC冗余验证错误，当前CRC={crc}，不正确')
        
        return frame
        
    @staticmethod
    def crcCheckCode(cnt:str):
        datas = cnt.encode()        
        crc_reg = 65535
        
        for b in datas:
            crc_reg = crc_reg >> 8 ^ b
            for j in range(8):
                check = crc_reg & 0x1
                crc_reg >>= 1
                if (check == 1):
                    crc_reg ^= 0xA001
        
        return r_str(format(crc_reg, 'x'), 4, '0').upper()
        
        

class HJ212FrameDecoder(MessageToMessageDecoder[str, HJ212Frame]):
    MAX_FRAME_LENGTH = 1024 * 8
    LEN_LENGTH = 4
    CRC_LENGTH = 4
    FIX_SPLIT_CHAR = "##"
    FIX_SPLIT_LENGTH = len(FIX_SPLIT_CHAR)+LEN_LENGTH
    FIX_LENGTH_INDEX = len(FIX_SPLIT_CHAR)
    FIX_SPLIT_CHAR_BYTES = b'##'
    FIX_COMMAND_CHAR = '&&'
    FIX_FRAME_END_CHAR = '\r\n'
    
    def __init__(self):
        super().__init__()
        self._sb = []
        
    def clear(self):
        self._sb.clear()
        
    def append(self, chunk:str):
        self._sb.append(chunk)
        
    def getSb(self)->str:
        return ''.join(self._sb)
        
    def getLength(self, msg:str):        
        return str2Num(msg[HJ212FrameDecoder.FIX_LENGTH_INDEX:HJ212FrameDecoder.FIX_SPLIT_LENGTH],None)    
    
    async def decode(self, ctx: ChannelHandlerContext, msg:str, out:list[HJ212Frame]):
        if _logger.canInfo():
            _logger.INFO(f'=== Receive({len(self._sb)}) === {msg}')
            
        msg = msg.strip()
        
        if not msg.startswith(HJ212FrameDecoder.FIX_SPLIT_CHAR):
            self.append(msg)
            msg = ''.join(self._sb)
        else:
            self.clear()
            
        n_length:int = self.getLength(msg)
        
        if n_length is None:
            raise ChannelHandleError(f'{msg} : {self.getSb()}')
        
        if len(msg) >= n_length + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH:
            if _logger.canDebug():
                _logger.DEBUG(f"=== Full Receive({n_length},{n_length + HJ212FrameDecoder.FIX_SPLIT_LENGTH  + HJ212FrameDecoder.CRC_LENGTH -len(msg)}) === {msg}")
            self.clear()
            
            if n_length + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH == len(msg) :
                if _logger.canDebug():
                    _logger.DEBUG(f"=== Full Receive({n_length},{n_length + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH - len(msg)}) === {msg}")
                self.dealmsg(ctx, msg, out)
            else:
                multiplemsg = msg.split(HJ212FrameDecoder.FIX_FRAME_END_CHAR)
                # count = len(multiplemsg)
                for idx, one in enumerate(multiplemsg):
                    if _logger.canDebug():
                        _logger.DEBUG(f'[{len(multiplemsg)},{idx}]={multiplemsg[idx]}')
                    if idx != len(multiplemsg) - 1 :
                        len2 = self.getLength(one)
                        if _logger.canDebug():
                            _logger.DEBUG(f'=== Full Receive({len2},{len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH - len(one)}) === {one}')
                        self.dealmsg(ctx, one, out)
                    else:
                        if len(one) >= HJ212FrameDecoder.FIX_SPLIT_LENGTH:
                            len2 = self.getLength(one)
                            if len(one) >= len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH:
                                if len(one) > len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH:
                                    one = one[:len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH]
                                    if _logger.canDebug():
                                        _logger.DEBUG(f"=== Full Receive***({len2},{len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH - len(one)}) === {one}")                                     
                                else:
                                    if _logger.canDebug():
                                        _logger.DEBUG(f"=== Full Receive({len2},{len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH - len(one)}) === {one}")
                                self.dealmsg(ctx, one, out)
                            else:
                                if _logger.canDebug():
                                    _logger.DEBUG(f'=== Split*({len2}, {len2 + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH - len(one)}) Receive === {one}')
                        else:
                            if _logger.canDebug():
                                _logger.DEBUG(f'=== Split**({len(one)}, {HJ212FrameDecoder.FIX_SPLIT_LENGTH}) Receive === {one}')
                            self.append(one)
        else:
            if _logger.canDebug():        
                _logger.DEBUG(f"=== Split({n_length}, {n_length + HJ212FrameDecoder.FIX_SPLIT_LENGTH + HJ212FrameDecoder.CRC_LENGTH -len(msg)}) Receive === {msg}")
            # self.clear()            
            self.append(msg)
            return
        
    def dealmsg(self, ctx: ChannelHandlerContext, msg:str, out:list[HJ212Frame]):
        frame:HJ212Frame = HJ212Frame.parse_frame(msg)
        out.append(frame)
        
    async def close_decode(self, ctx: ChannelHandlerContext, out:list[HJ212Frame]): ...
    
class HJ212Server(Server):    
    def __init__(self, address:tuple[str,int]=('0.0.0.0',1234)):
        super().__init__('HJ212Server', address)
        
    def initHandler(self, sc:SocketChannel):
        class HJ212FrameHandler(ChannelHandler[HJ212Frame]):
            def __init__(self):
                super().__init__()
                
            async def on_frame(self, ctx: ChannelHandlerContext, data:HJ212Frame):
                if _logger.canDebug():
                    _logger.DEBUG(data)
                
            async def channel_read(self, ctx: ChannelHandlerContext, data:HJ212Frame):
                if isinstance(data, HJ212Frame):
                    await self.on_frame(ctx, data)
                else:
                    await ctx.fire_channel_read(data)
                    
        _pipeline = sc.pipeline()
        _pipeline.add_last(StringDecoder())
        _pipeline.add_last(HJ212FrameDecoder())
        _pipeline.add_last(HJ212FrameHandler())
    

def hj212_server():
    args = parse_long_args_plus()
    port = 60000
    host = '0.0.0.0'
    if 'port' in args:
        port = args['port']
    if 'host' in args:
        host = args['host']        
    hs:HJ212Server = HJ212Server((host, port))    
    if 'log_level' in args:
        log_level = args['log_level']
        log_level = Logger.level(log_level)
        hs.log(log_level)        
    hs.start()

def echoserver_main():
    _logger.DEBUG('开始EchoServer')
    echo_server()

def hj212server_main():
    _logger.DEBUG('开始HJ212Server')
    hj212_server()

                    
if __name__ == "__main__":
    msg = "##0492QN=20230421175500246;ST=22;CN=2011;PW=123456;MN=2023041803100001;Flag=5;CP=&&DataTime=20230421175400;LA-Rtd=50.7,LA-Flag=N;a01007-Rtd=0.8,a01007-Flag=N;a01008-Rtd=150.0,a01008-Flag=N;a01001-Rtd=26.0,a01001-Flag=N;a01002-Rtd=76.3,a01002-Flag=N;a01006-Rtd=100.4,a01006-Flag=N;LeqT-Rtd=52.5,LeqT-Flag=N;L5-Rtd=56.8,L5-Flag=N;L10-Rtd=54.1,L10-Flag=N;L50-Rtd=48.4,L50-Flag=N;L90-Rtd=46.5,L90-Flag=N;L95-Rtd=46.2,L95-Flag=N;Lmin-Rtd=44.5,Lmin-Flag=N;Lmax-Rtd=87.9,Lmax-Flag=N;SD-Rtd=3.5,SD-Flag=N&&35C0"
    print(msg)    
    frame:HJ212Frame = HJ212Frame.parse_frame(msg)    
    print(frame)
    print(frame.crc)
    print(frame.raw)
    print(HJ212Frame.crcCheckCode(frame.raw))
    
    # _logger.DEBUG('开始Server')
    # echo_server()    
    
    hj212_server()
    
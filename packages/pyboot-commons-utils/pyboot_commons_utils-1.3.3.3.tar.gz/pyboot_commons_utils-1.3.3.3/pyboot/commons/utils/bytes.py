import struct
from enum import Enum
from typing import Union

from pyboot.commons.utils.log import Logger
from collections import defaultdict

_logger = Logger('pyboot.commons.utils.bytes')

class Endian(Enum):
    BIG_ENDIAN = 'BIG_ENDIAN'
    LITTLE_ENDIAN = 'LITTLE_ENDIAN'

class EndianUtils:
    @staticmethod
    def endian_signal_long(endian:Endian=Endian.BIG_ENDIAN):
        return '>q' if endian == Endian.BIG_ENDIAN else '<q'    
    
    @staticmethod
    def endian_signal_ulong(endian:Endian=Endian.BIG_ENDIAN):
        return '>Q' if endian == Endian.BIG_ENDIAN else '<Q'
    
    @staticmethod
    def endian_signal_int(endian:Endian=Endian.BIG_ENDIAN):
        return '>i' if endian == Endian.BIG_ENDIAN else '<i'    
    
    @staticmethod
    def endian_signal_uint(endian:Endian=Endian.BIG_ENDIAN):
        return '>I' if endian == Endian.BIG_ENDIAN else '<I'
        
    @staticmethod
    def endian_signal_short(endian:Endian=Endian.BIG_ENDIAN):
        return '>h' if endian == Endian.BIG_ENDIAN else '<h'
        
    @staticmethod
    def endian_signal_ushort(endian:Endian=Endian.BIG_ENDIAN):
        return '>H' if endian == Endian.BIG_ENDIAN else '<H'
        
    @staticmethod
    def endian_signal_float(endian:Endian=Endian.BIG_ENDIAN):
        return '>f' if endian == Endian.BIG_ENDIAN else '<f'
        
    @staticmethod
    def endian_signal_double(endian:Endian=Endian.BIG_ENDIAN):
        return '>d' if endian == Endian.BIG_ENDIAN else '<d'                

class BytesUtils:                
    @staticmethod
    def l_bytes(d:bytes|bytearray, width:int, fillchar=b'\0', trim:bool=False):
        if d is not None:
            if trim and len(d) >= width:
                return d[:width]
            return d.ljust(width, fillchar)
        return d

    @staticmethod
    def r_bytes(d:bytes|bytearray, width:int, fillchar=b'\0', trim:bool=False):
        if d is not None:
            if trim and len(d) >= width:
                return d[:width]
            return d.rjust(width, fillchar)
        return d
    
    @staticmethod
    def readable_bytes(datas:bytes|bytearray, idx:int=0) -> int:
        return len(datas) - idx
    
    # 读取方法
    @staticmethod
    def read_byte(datas:bytes|bytearray, idx:int=0) -> int:
        if BytesUtils.readable_bytes(datas, idx) < 1:
            raise IndexError(f"读取数索引{idx}超过可读取字节数范围[0,{BytesUtils.readable_bytes(datas, idx)}]")
        
        value = datas[idx]        
        return value
    
    @staticmethod
    def read_bytes(datas:bytes|bytearray, length:int, idx:int=0) -> bytes:
        """读取指定长度的字节"""
        if BytesUtils.readable_bytes(datas, idx) < length:
            raise IndexError(f"读取数{length}超过可读取字节数范围[0,{BytesUtils.readable_bytes(datas, idx)}]")
        
        # data = self._buffer[self._reader_index:self._reader_index + length]
        # self._reader_index += length
        
         # 使用memoryview切片，然后转换为bytes
        data = bytes(datas[idx:idx + length])
        return data
        # return bytearray(data)
        
    @staticmethod
    def read_bytes_view(datas:bytes|bytearray, length:int, idx: int) -> memoryview:
        """读取指定长度的字节（返回memoryview，零拷贝）"""
        if BytesUtils.readable_bytes(datas, idx) < length:
            raise IndexError(f"读取数{length}超过可读取字节数范围[0,{BytesUtils.readable_bytes(datas, idx)}]")
        
        # 直接返回memoryview切片（零拷贝）
        data_view = memoryview[bytes(datas[idx:idx + length])]        
        return data_view
    
    @staticmethod
    def read_int_n(datas:bytes|bytearray, n:int, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:
        assert n > 0, f'读取数必须大于0，但是获得{n}'
        if n == 1:
            length = BytesUtils.read_byte(datas, idx)
            if length < 0:
                length += 256
        elif n ==2:
            length = BytesUtils.read_short(datas, idx, endian)
        elif n == 3:
            if endian == Endian.BIG_ENDIAN:            
                b1 = datas[idx+0] & 0xFF
                b2 = datas[idx+1] & 0xFF
                b3 = datas[idx+2] & 0xFF
                length = (b1 << 16) | (b2 << 8) | b3            
            else:
                b1 = datas[idx+0] & 0xFF
                b2 = datas[idx+1] & 0xFF
                b3 = datas[idx+2] & 0xFF
                length = (b3 << 16) | (b2 << 8) | b1
        elif n == 4:
            length = BytesUtils.read_int(datas, idx, endian)
        elif n == 8:
            length = BytesUtils.read_long(datas, idx, endian)
        else:
            # data = BytesUtils.read_bytes(datas, n, idx)
            length = 0
            if endian == Endian.BIG_ENDIAN:
                for i in range(n):
                    b = datas[idx+i]  & 0xFF
                    length = length|(b << (8*(n-i-1)))
            else:
                for i in range(n):
                    b = datas[idx+i]  & 0xFF
                    length = length|(b << (8*i))
        return length
        
    @staticmethod
    def read_long(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节整数"""
        data = BytesUtils.read_bytes(datas, 8, idx)
        return struct.unpack(EndianUtils.endian_signal_long(endian), data)[0]
        
    @staticmethod
    def read_ulong(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节无符号整数"""
        data = BytesUtils.read_bytes(datas, 8, idx)
        return struct.unpack(EndianUtils.endian_signal_ulong(endian), data)[0]
    
    @staticmethod
    def read_int(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节整数"""
        data = BytesUtils.read_bytes(datas, 4, idx)
        return struct.unpack(EndianUtils.endian_signal_int(endian), data)[0]
        
    @staticmethod
    def read_uint(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节无符号整数"""
        data = BytesUtils.read_bytes(datas, 4, idx)
        return struct.unpack(EndianUtils.endian_signal_uint(endian), data)[0]
    
    @staticmethod        
    def read_short(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取2字节短整数"""
        data = BytesUtils.read_bytes(datas, 2, idx)
        return struct.unpack(EndianUtils.endian_signal_short(endian), data)[0]
    
    @staticmethod    
    def read_ushort(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取2字节无符号短整数"""
        data = BytesUtils.read_bytes(datas, 2, idx)
        return struct.unpack(EndianUtils.endian_signal_ushort(endian), data)[0]
    
    @staticmethod    
    def read_int8(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取1字节短整数"""
        data = BytesUtils.read_byte(datas, idx)
        return struct.unpack('b', data)[0]
    
    @staticmethod    
    def read_uint8(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取1字节无符号短整数"""
        data = BytesUtils.read_byte(datas, idx)
        return struct.unpack('B', data)[0]
    
    @staticmethod    
    def read_int16(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取2字节整数"""
        data = BytesUtils.read_bytes(datas, 2, idx)
        return struct.unpack(EndianUtils.endian_signal_short(endian), data)[0]
    
    @staticmethod
    def read_uint16(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取2字节无符号整数"""
        data = BytesUtils.read_bytes(datas, 2, idx)
        return struct.unpack(EndianUtils.endian_signal_ushort(endian), data)[0]
    
    @staticmethod
    def read_float(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取单精度浮点数 (4字节)"""
        data = BytesUtils.read_bytes(datas, 4, idx)
        return struct.unpack(EndianUtils.endian_signal_float(endian), data)[0]
    
    @staticmethod
    def read_double(datas:bytes|bytearray, idx:int=0, endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取双精度浮点数 (8字节)"""
        data = BytesUtils.read_bytes(datas, 8, idx)
        return struct.unpack(EndianUtils.endian_signal_double(endian), data)[0]
    
    @staticmethod
    def read_string(datas:bytes|bytearray, length: int = None, idx:int=0, encode:str='utf-8') -> str:
        """读取字符串"""
        if length is None:
            length = BytesUtils.read_byte(datas, idx)
            idx = idx + 1
        
        data = BytesUtils.read_bytes(datas, length, idx)        
        return data.decode(encode)
    
    # 写入方法
    @staticmethod
    def write_byte(value: int) -> bytes:
        """写入一个字节"""        
        # self._ensure_writable(1)
        return [value & 0xFF]            
    
    @staticmethod
    def write_bytes(data: bytes|bytearray) -> bytes:
        """写入字节数据"""
        return bytes(data)
    
    @staticmethod
    def write_int_n(value: int, n:int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:  
        assert n > 0, f'读取数必须大于0，但是获得{n}'
        if n == 1:
            return BytesUtils.write_byte(value)
        elif n ==2:
            return BytesUtils.write_short(value, endian)
        elif n == 3:
            byte1 = (value >> 16) & 0xFF  # 最高字节
            byte2 = (value >> 8) & 0xFF   # 中间字节
            byte3 = value & 0xFF          # 最低字节
            if endian == Endian.BIG_ENDIAN:            
                return bytes([byte1, byte2, byte3])            
            else:
                return bytes([byte3, byte2, byte1])
        elif n == 4:
            return BytesUtils.write_int(value, endian)
        elif n == 8:
            return BytesUtils.write_long(value, endian)
        else:
            # data = BytesUtils.read_bytes(datas, n, idx)
            b = []
            for i in range(n):
                b.append( (value >> (8 * (n-i-1)))  & 0xFF )
            if endian == Endian.BIG_ENDIAN:
                return bytes(b)
            else:
                b.reverse()
                return bytes(b)
    
    @staticmethod
    def write_long(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:        
        data = bytes(struct.pack(EndianUtils.endian_signal_long(endian), value))        
        return data
    
    @staticmethod
    def write_ulong(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入4字节无符号整数"""
        data = bytes(struct.pack(EndianUtils.endian_signal_ulong(endian), value))
        return data
    
    @staticmethod
    def write_int(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:   
        """写入4字节整数"""     
        data = bytes(struct.pack(EndianUtils.endian_signal_int(endian), value))        
        return data
    
    @staticmethod
    def write_uint(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入4字节无符号整数"""
        data = bytes(struct.pack(EndianUtils.endian_signal_uint(endian), value))
        return data
    
    """写入2字节短整数"""
    @staticmethod
    def write_short(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入2字节短整数"""
        data = bytes(struct.pack(EndianUtils.endian_signal_short(endian), value))        
        return data
    
    """写入2字节短整数"""
    @staticmethod
    def write_ushort(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入2字节无符号短整数"""
        data = bytes(struct.pack(EndianUtils.endian_signal_ushort(endian), value))        
        return data
    
    @staticmethod
    def write_int8(value: int) -> bytes:
        """写入1字节整数"""
        data = bytes(struct.pack('b', value))
        return data
    
    @staticmethod
    def write_uint8(value: int) -> bytes:
        """写入1字节无符号整数"""
        data = bytes(struct.pack('B', value))
        return data
    
    @staticmethod
    def write_int16(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入2字节整数"""
        data = bytes(struct.pack(EndianUtils.endian_signal_short(endian), value))
        return data
    
    @staticmethod
    def write_uint16(value: int, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入2字节无符号整数"""
        data = bytes(struct.pack(EndianUtils.endian_signal_ushort(endian), value))
        return data
    
    @staticmethod
    def write_float(value: float, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """写入单精度浮点数 (4字节)"""
        data = bytes(struct.pack(EndianUtils.endian_signal_float(endian), value))
        return data
    
    @staticmethod
    def write_double(value: float, endian:Endian=Endian.BIG_ENDIAN) -> bytes:
        """ 写入双精度浮点数 (8字节)"""
        data = bytes(struct.pack(EndianUtils.endian_signal_double(endian), value))
        return data
    
    @staticmethod
    def write_string(value: str, encoding:str='utf-8') -> bytes:
        """写入字符串（带长度前缀）"""
        data = value.encode(encoding)
        return [len(data)] + data        
    
    @staticmethod
    def write_terminated_string(value: str,encoding:str='utf-8') -> bytes:
        """写入字符串（带长度前缀）"""
        data = value.encode(encoding)        
        return data
    
    @staticmethod
    def write_null_terminated_string(value: str, encoding: str = 'utf-8') -> bytes:
        """写入以空字符结尾的字符串"""        
        data = value.encode(encoding)
        return [len(data)] + data +[0]                   
    
    @staticmethod
    def hex(datas:bytes):
        return datas.hex()
    
    def find(datas:bytes, key:bytes, idx:int = 0):
        return datas.find(key)



class ByteBuffer:
    """支持池化的字节缓冲区，类似Netty的ByteBuffer"""
    
    def __init__(self, capacity: int = 1024, direct: bool = False):
        """
        初始化ByteBuffer
        
        Args:
            capacity: 初始容量
            direct: 是否使用直接内存（模拟，Python中实际还是bytearray）
            big_endian: 是否大端读写
        """
        self._buffer = bytearray(capacity)
        self._mv = memoryview(self._buffer)  # 创建memoryview用于高效操作
         
        self._reader_index = 0
        self._writer_index = 0
        self._capacity = capacity
        self._direct = direct
        # self._big_endian = big_endian        
        # self._endian_signal_long = '>q' if self._big_endian else '<q'
        # self._endian_signal_ulong = '>Q' if self._big_endian else '<Q'
        # self._endian_signal_int = '>i' if self._big_endian else '<i'
        # self._endian_signal_uint = '>I' if self._big_endian else '<I'
        # self._endian_signal_short = '>h' if self._big_endian else '<h'
        # self._endian_signal_ushort = '>H' if self._big_endian else '<H'
        # self._endian_signal_float = '>f' if self._big_endian else '<f'
        # self._endian_signal_double = '>d' if self._big_endian else '<d'
        
        self._ref_count = 1  # 引用计数
        self._max_capacity = 1024 * 1024  # 1MB 最大容量
        
    @classmethod
    def buffer(cls, capacity: int = 1024, direct: bool = False) -> 'ByteBuffer':        
        return cls(capacity, direct)
    
    def retain(self) -> 'ByteBuffer':
        """增加引用计数"""
        self._ref_count += 1
        return self
    
    def _reset(self) -> None:
        """重置缓冲区状态"""
        self._reader_index = 0
        self._writer_index = 0
    
    def _ensure_writable(self, min_writable: int) -> None:
        """确保有足够的可写空间"""
        if self.writable_bytes() >= min_writable:
            return
            
        new_capacity = max(self._capacity * 2, self._writer_index + min_writable)
        if new_capacity > self._max_capacity:
            raise MemoryError(f"缓冲区容量已经超过范围[0,{self._max_capacity}]: {new_capacity}")
            
        new_buffer = bytearray(new_capacity)
        new_mv = memoryview(new_buffer)
        
        # new_buffer[:len(self._buffer)] = self._buffer
        # 使用memoryview高效复制数据
        new_mv[:len(self._buffer)] = self._mv[:len(self._buffer)]        
        
        self._buffer = new_buffer
        self._mv = new_mv
        self._capacity = new_capacity
    
    # 读取方法
    def read_byte(self) -> int:
        """读取一个字节"""
        if self.readable_bytes() < 1:
            raise IndexError("Not enough readable bytes")
        
        # value = self._buffer[self._reader_index]
        value = self._mv[self._reader_index]
        self._reader_index += 1
        return value
    
    def read_bytes(self, length: int) -> bytes:
        """读取指定长度的字节"""
        if self.readable_bytes() < length:
            raise IndexError(f"读取数{length}超过可读取字节数范围[0,{self.readable_bytes()}]")
        
        # data = self._buffer[self._reader_index:self._reader_index + length]
        # self._reader_index += length
        
         # 使用memoryview切片，然后转换为bytes
        data = bytes(self._mv[self._reader_index:self._reader_index + length])
        self._reader_index += length
        
        return data
        # return bytearray(data)
    
    def read_bytes_view(self, length: int) -> memoryview:
        """读取指定长度的字节（返回memoryview，零拷贝）"""
        if self.readable_bytes() < length:
            raise IndexError(f"读取数{length}超过可读取字节数范围[0,{self.readable_bytes()}]")
        
        # 直接返回memoryview切片（零拷贝）
        data_view = self._mv[self._reader_index:self._reader_index + length]
        self._reader_index += length
        return data_view
        
    def read_long(self,endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取8字节长整数"""
        data = self.read_bytes(8)
        return struct.unpack(EndianUtils.endian_signal_long(endian), data)[0]
    
    def read_ulong(self,endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取8字节长整数"""
        data = self.read_bytes(8)
        return struct.unpack(EndianUtils.endian_signal_ulong(endian), data)[0]    
    
    
    def read_int_n(self,n:int,endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节整数"""
        data = self.read_bytes(n)
        return BytesUtils.read_int_n(data, n, 0, endian)
        # return struct.unpack(EndianUtils.endian_signal_int(endian), data)[0]
        
    def read_int(self,endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节整数"""
        data = self.read_bytes(4)
        return struct.unpack(EndianUtils.endian_signal_int(endian), data)[0]
    
    def read_uint(self,endian:Endian=Endian.BIG_ENDIAN) -> int:        
        """读取4字节整数"""
        data = self.read_bytes(4)
        return struct.unpack(EndianUtils.endian_signal_uint(endian), data)[0]
    
    def read_short(self,endian:Endian=Endian.BIG_ENDIAN) -> int:
        """读取2字节短整数"""
        data = self.read_bytes(2)
        return struct.unpack(EndianUtils.endian_signal_short(endian), data)[0]
    
    def read_ushort(self,endian:Endian=Endian.BIG_ENDIAN) -> int:
        """读取2字节无符号短整数"""
        data = self.read_bytes(2)
        return struct.unpack(EndianUtils.endian_signal_ushort(endian), data)[0]
    
    def read_int8(self) -> int:
        """读取1字节短整数"""
        data = self.read_bytes(1)
        return struct.unpack('b', data)[0]
    
    def read_uint8(self) -> int:
        """读取1字节无符号短整数"""
        data = self.read_bytes(1)
        return struct.unpack('B', data)[0]
    
    def read_int16(self,endian:Endian=Endian.BIG_ENDIAN) -> int:
        """读取2字节整数"""
        data = self.read_bytes(2)
        return struct.unpack(EndianUtils.endian_signal_short(endian), data)[0]
    
    def read_uint16(self,endian:Endian=Endian.BIG_ENDIAN) -> int:
        """读取2字节无符号整数"""
        data = self.read_bytes(2)
        return struct.unpack(EndianUtils.endian_signal_ushort(endian), data)[0]
    
    def read_float(self,endian:Endian=Endian.BIG_ENDIAN) -> float:
        """读取单精度浮点数 (4字节)"""
        data = self.read_bytes(4)
        return struct.unpack(EndianUtils.endian_signal_float(endian), data)[0]
    
    def read_double(self,endian:Endian=Endian.BIG_ENDIAN) -> float:
        """读取双精度浮点数 (8字节)"""
        data = self.read_bytes(8)
        return struct.unpack(EndianUtils.endian_signal_double(endian), data)[0]
    
    def read_string(self, length: int = None, encode:str='utf-8') -> str:
        """读取字符串"""
        if length is None:
            length = self.read_int()
        
        data = self.read_bytes(length)
        return data.decode(encode)
    
    # 写入方法
    def write_byte(self, value: int) -> 'ByteBuffer':
        """写入一个字节"""
        self._ensure_writable(1)
        # self._ensure_writable(1)
        self._mv[self._writer_index] = value & 0xFF
        self._writer_index += 1
        return self
    
    def write_bytes(self, data: Union[bytes, bytearray]) -> 'ByteBuffer':
        """写入字节数据"""
        length = len(data)
        self._ensure_writable(length)
        
        # 使用memoryview高效写入
        self._mv[self._writer_index:self._writer_index + length] = data
        self._writer_index += length
        return self
    
    def write_long(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入8字节长整数"""
        data = struct.pack(EndianUtils.endian_signal_long(endian), value)
        self.write_bytes(data)
        return self
    
    def write_ulong(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入8字节无符号长整数"""
        data = struct.pack(EndianUtils.endian_signal_ulong(endian), value)
        self.write_bytes(data)
        return self
    
    def write_int(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入4字节整数"""
        data = struct.pack(EndianUtils.endian_signal_int(endian), value)
        self.write_bytes(data)
        return self
    
    def write_uint(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入4字节无符号整数"""
        data = struct.pack(EndianUtils.endian_signal_uint(endian), value)
        self.write_bytes(data)
        return self
    
    """写入2字节短整数"""
    def write_short(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入2字节短整数"""
        data = struct.pack(EndianUtils.endian_signal_short(endian), value)
        self.write_bytes(data)
        return self
    
    """写入2字节短整数"""
    def write_ushort(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入2字节无符号短整数"""
        data = struct.pack(EndianUtils.endian_signal_ushort(endian), value)
        self.write_bytes(data)
        return self
    
    def write_int8(self, value: int) -> 'ByteBuffer':
        """写入1字节整数"""
        data = struct.pack('b', value)
        self.write_bytes(data)
        return self
    
    def write_uint8(self, value: int) -> 'ByteBuffer':
        """写入1字节无符号整数"""
        data = struct.pack('B', value)
        self.write_bytes(data)
        return self
    
    def write_int16(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入2字节整数"""
        data = struct.pack(EndianUtils.endian_signal_short(endian), value)
        self.write_bytes(data)
        return self
    
    def write_uint16(self, value: int,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入2字节无符号整数"""
        data = struct.pack(EndianUtils.endian_signal_ushort(endian), value)
        self.write_bytes(data)
        return self
    
    def write_float(self, value: float,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """写入单精度浮点数 (4字节)"""
        data = struct.pack(EndianUtils.endian_signal_float(endian), value)
        self.write_bytes(data)
        return self
    
    def write_double(self, value: float,endian:Endian=Endian.BIG_ENDIAN) -> 'ByteBuffer':
        """ 写入双精度浮点数 (8字节)"""
        data = struct.pack(EndianUtils.endian_signal_double(endian), value)
        self.write_bytes(data)
        return self
    
    def write_string(self, value: str,encoding:str='utf-8') -> 'ByteBuffer':
        """写入字符串（带长度前缀）"""
        data = value.encode(encoding)
        self.write_int(len(data))
        self.write_bytes(data)
        return self
    
    def write_terminated_string(self, value: str,encoding:str='utf-8') -> 'ByteBuffer':
        """写入字符串（带长度前缀）"""
        data = value.encode(encoding)
        self.write_bytes(data)
        return self
    
    def write_null_terminated_string(self, value: str, encoding: str = 'utf-8') -> 'ByteBuffer':
        """写入以空字符结尾的字符串"""
        self.write_string(value, encoding)
        self.write_byte(0)  # 写入空字符        
        return self
        
    # 获取方法（不移动指针）
    def get_byte(self, index: int) -> int:
        """获取指定位置的字节"""
        return self._mv[index]
    
    def get_readable_bytes(self) -> bytes:
        """获取指定位置的字节数据"""
        return bytes(self._mv[self._reader_index:self._writer_index])
    
    def get_bytes(self, index: int, length: int) -> bytes:
        """获取指定位置的字节数据"""
        return bytes(self._mv[index:index + length])
    
    def get_bytes_view(self, index: int, length: int) -> memoryview:
        """获取指定位置的字节数据（返回memoryview，零拷贝）"""
        return self._mv[index:index + length]
    
    # 批量操作方法
    def write_from_reader(self, source: 'ByteBuffer', length: int = None) -> int:
        """从另一个ByteBuf的读位置复制数据到当前写位置"""
        if length is None:
            length = source.readable_bytes()
        
        if length > source.readable_bytes():
            raise ValueError(f"源ByteBuf的读长度{length}超过读范围[0, {source.readable_bytes()}]")
        
        # 使用memoryview实现零拷贝传输
        source_data = source._mv[source._reader_index:source._reader_index + length]
        self.write_bytes(source_data)
        source._reader_index += length
        return length
    
    def slice(self, start: int = None, length: int = None) -> 'ByteBuffer':
        """创建当前缓冲区的切片（共享底层数据）"""
        if start is None:
            start = self._reader_index
        if length is None:
            length = self._writer_index - start
        
        if start + length > len(self._buffer):
            raise IndexError(f"切片操作了边界: {start} + {length} > {len(self._buffer)}")
        
        # 创建新的ByteBuf，但共享底层buffer
        sliced = ByteBuffer(0, self._direct, False)
        sliced._buffer = self._buffer  # 共享同一个bytearray
        sliced._mv = self._mv[start:start + length]  # 创建新的memoryview切片
        sliced._reader_index = 0
        sliced._writer_index = length
        sliced._capacity = length
        
        # 增加引用计数
        self.retain()
        sliced._ref_count = 1
        
        return sliced
    
    def duplicate(self) -> 'ByteBuffer':
        """复制ByteBuf（共享底层数据，但有独立的读写指针）"""
        dup = ByteBuffer(0, self._direct, False)
        dup._buffer = self._buffer
        dup._mv = self._mv
        dup._reader_index = self._reader_index
        dup._writer_index = self._writer_index
        dup._capacity = self._capacity
        
        # 增加引用计数
        self.retain()
        dup._ref_count = 1        
        return dup
    
    # 属性访问
    @property
    def reader_index(self) -> int:
        return self._reader_index
    
    @reader_index.setter
    def reader_index(self, value: int):
        if value < 0 or value > self._writer_index:
            raise IndexError(f"读取索引超过范围[0,{self._writer_index}]: {value}")
        self._reader_index = value
    
    @property
    def writer_index(self) -> int:
        return self._writer_index
    
    @writer_index.setter
    def writer_index(self, value: int):
        if value < self._reader_index or value > self._capacity:
            raise IndexError(f"写入索引超过范围[{self._reader_index},{self._capacity}]: {value}")
        self._writer_index = value
        
    @property
    def capacity(self) -> int:
        return self._capacity
    
    def readable_bytes(self) -> int:
        return self._writer_index - self._reader_index
    
    def writable_bytes(self) -> int:
        return self._capacity - self._writer_index
    
    def to_bytes(self) -> bytes:
        """转换为bytes（从读指针到写指针）"""
        return bytes(self._buffer[self._reader_index:self._writer_index])
    
    def to_bytearray(self) -> bytearray:
        """转换为bytearray（从读指针到写指针）"""
        return bytearray(self._mv[self._reader_index:self._writer_index])
    
    def get_memoryview(self) -> memoryview:
        """获取整个缓冲区的memoryview"""
        return self._mv
    
    def get_readable_memoryview(self) -> memoryview:
        """获取可读区域的memoryview（零拷贝）"""
        return self._mv[self._reader_index:self._writer_index]
    
    def clear(self) -> None:
        """清空缓冲区"""
        self._reset()
    
    def __len__(self) -> int:
        return self.readable_bytes()
    
    def __str__(self) -> str:
        return f"ByteBuf(reader_index={self._reader_index}, writer_index={self._writer_index}, " \
               f"capacity={self._capacity}, readable={self.readable_bytes()})"
    
    # def __repr__(self):
    #     return f"ByteBuf(reader_index={self._reader_index}, writer_index={self._writer_index}, " \
    #            f"capacity={self._capacity}, readable={self.readable_bytes()}, big_endian={self._big_endian} mv={self._mv} buffer={self._buffer})"
    
    def __enter__(self):
        """上下文管理器支持"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动释放"""
        self.release()
    
    def reset(self):
        # 重置所有状态
        self._reader_index = 0
        self._writer_index = 0        
        
    def destroy(self) -> bool:         
        try:
            # 1. 首先释放 memoryview
            if self._mv is not None:
                # memoryview 有 release() 方法（Python 3.2+）
                if hasattr(self._mv, 'release'):
                    self._mv.release()
                self._mv = None
            
            # 2. 释放 bytearray
            self._buffer = None
            
            # 3. 重置所有状态
            self._reader_index = 0
            self._writer_index = 0
            self._capacity = 0
            
            return True
                
        except Exception as e:
            print(f"释放内存时出错: {e}")
            return False
        
#     这个方法将缓冲区中从position到limit之间的数据复制到缓冲区的开始处，
#     然后将position设置为复制的数据长度之后，limit设置为capacity。
#           这样，未读的数据（position到limit之间）被移动到缓冲区的开头，
#           然后我们就可以在它们后面追加新的数据。这通常用于在读取部分数据后，腾出空间继续写入。
    def compact(self):
        """丢弃已读字节，压缩缓冲区"""
        """
        压缩缓冲区：将未读数据移动到缓冲区开头
        类似Java ByteBuffer的compact()
        
        Returns:
            ByteBuffer: 压缩后的缓冲区自身
        """
        if self._reader_index == 0:
            return
        
        # 移动未读数据到缓冲区开头
        readable = self.readable_bytes()
        if readable > 0:
            self._buffer[:readable] = self._buffer[self._reader_index:self._writer_index]
        
        self._reader_index = 0
        self._writer_index = readable
        # self._marked_reader_index = max(0, self._marked_reader_index - self._reader_index)
        # self._marked_writer_index = max(0, self._marked_writer_index - self._reader_index)
    
    def flip(self) -> 'ByteBuffer':
        """
        翻转缓冲区：将写模式切换到读模式
        将limit设置为当前的writer_index，position设置为0
        类似Java ByteBuffer的flip()
        """
        # 将读取索引重置为0，限制读取范围为已写入的数据
        self._reader_index = 0
        return self
    
    def rewind(self) -> 'ByteBuffer':
        """
        倒回缓冲区：重置读取位置，重新读取
        类似Java ByteBuffer的rewind()
        """
        self._reader_index = 0
        return self
    
    # ========== 查找和跳过 ==========
    
    def skip_bytes(self, length: int):
        """跳过指定长度的字节"""
        if length > self.readable_bytes():
            raise BufferError(f"不能跳过{length}字节, 可读字节{self.readable_bytes()}个")
        self._reader_index += length
    
    def index_of(self, value: Union[int, bytes], start: int = 0) -> int:
        """查找字节或字节序列的位置"""
        if isinstance(value, int):
            # 查找单个字节
            try:
                return self._buffer.index(value, self._reader_index + start, self._writer_index)
            except ValueError:
                return -1
        else:
            # 查找字节序列
            try:
                return self._buffer.index(value, self._reader_index + start, self._writer_index)
            except ValueError:
                return -1
    
    def find(self, value: Union[int, bytes], start: int = 0) -> int:
        """查找字节或字节序列的位置"""
        if isinstance(value, int):
            # 查找单个字节
            try:
                return self._buffer.find(value, self._reader_index + start, self._writer_index)
            except ValueError:
                return -1
        else:
            # 查找字节序列
            try:
                return self._buffer.find(value, self._reader_index + start, self._writer_index)
            except ValueError:
                return -1

class PooledByteBufferAllocator:    
    _instance = None    
    DEFAULT:'PooledByteBufferAllocator' = None
    # def __new__(cls):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance.pools = defaultdict(list)
    #     return cls._instance
        
    def __init__(self):
        self.pools = defaultdict(list)
    
    def allocate(self, size: int = 1024) -> ByteBuffer:
        """分配缓冲区"""
        key = size        
        if self.pools[key]:
            buf:ByteBuffer = self.pools[key].pop()
            buf.clear()
            return buf
        else:
            return ByteBufAllocator(True).buffer(size)
    
    def release(self, buffer: ByteBuffer):        
        """释放缓冲区"""
        if buffer is not None:
            key = buffer.capacity
            self.pools[key].append(buffer)
            
        if _logger.canDebug():
            _logger.DEBUG(f'{self}')
    
    def allocate_direct(self, size: int = 1024) -> ByteBuffer:
        """分配直接缓冲区（这里简单实现，实际Python中内存管理不同）"""
        return self.allocate(size)   
    
    def __repr__(self):
        count_infos = [f'[{k}]={len(v)}' for k, v in self.pools.items()]
        
        return f'Size池个数:{len(self.pools)} {','.join(count_infos)} {self.pools}'


class ByteBufAllocator:
    """ByteBuf分配器，类似Netty的ByteBufAllocator"""
    DIRECT:'ByteBufAllocator' = None
    HEAP:'ByteBufAllocator' = None
    
    def __init__(self, prefer_direct: bool = False):
        self.prefer_direct = prefer_direct
    
    def buffer(self, capacity: int = 1024) -> ByteBuffer:
        """分配缓冲区"""
        return ByteBuffer.buffer(capacity, self.prefer_direct)
    
    def heap_buffer(self, capacity: int = 1024) -> ByteBuffer:
        """分配堆缓冲区"""
        return ByteBuffer.buffer(capacity, False)
    
    def direct_buffer(self, capacity: int = 1024) -> ByteBuffer:
        """分配直接缓冲区（模拟）"""
        return ByteBuffer.buffer(capacity, True)
    
PooledByteBufferAllocator.DEFAULT = PooledByteBufferAllocator()    
ByteBufAllocator.DIRECT = ByteBufAllocator(True)            
ByteBufAllocator.HEAP = ByteBufAllocator(False)
        
def test_bytebuffer():        
    def print_info(buf:ByteBuffer):
        _logger.DEBUG(f'ByteBuf={buf} ')
        
    def test_bytebuf(buf:ByteBuffer):
        print_info(buf)
        # 写入各种浮点数
        buf.write_float(3.14159)           # 默认大端字节序    
        print_info(buf)
        buf.write_double(3.14159)           # 默认大端字节序    
        print_info(buf)
        buf.write_double(1.41421356)       # 双精度，大端
        print_info(buf)
        
        
        print(f"写入后缓冲区大小: {len(buf)} 字节")
        
        # # 重置读指针并读取
        # buf.reader_index = 0
        
        # 按写入顺序读取
        pi = buf.read_float()           # 大端读取    
        print_info(buf)
        pi2 = buf.read_double()           # 大端读取    
        print_info(buf)
        sqrt2 = buf.read_double()       # 双精度大端读取    
        print_info(buf)
        
        print("读取的浮点数:")
        print(f"  π ≈ {pi:.8f} (实际: 3.14159)")
        print(f"  π ≈ {pi2:.8f} 双精(实际: 3.14159)")
        print(f"  √2 ≈ {sqrt2:.8f} (实际: 1.41421356)")

        
        # 验证精度
        print("\n精度验证:")
        print(f"  float 误差: |{pi - 3.14159}|")
        print(f"  double 误差: |{pi2 - 3.14159}|")
        print(f"  double 误差: |{sqrt2 - 1.41421356}|")
    
    """演示浮点数操作"""    
    print("=== 浮点数操作演示 ===")    
    # buf = ByteBuffer.buffer(256)       
    print(PooledByteBufferAllocator.DEFAULT)
    
    buf = PooledByteBufferAllocator.DEFAULT.allocate(256)
    
    test_bytebuf(buf)
    
    buf.reset()
    
    test_bytebuf(buf)
    
    buf.reset()
    
    buf.write_bytes(BytesUtils.write_int_n(1022,2,Endian.BIG_ENDIAN))
    buf.write_bytes(BytesUtils.write_int_n(1022,2,Endian.LITTLE_ENDIAN))
    buf.write_bytes(BytesUtils.write_int_n(1022,3,Endian.BIG_ENDIAN))
    buf.write_bytes(BytesUtils.write_int_n(1022,3,Endian.LITTLE_ENDIAN))
    
    print(buf.read_int_n(2, Endian.BIG_ENDIAN))
    print(buf.read_int_n(2, Endian.LITTLE_ENDIAN))
    print(buf.read_int_n(3, Endian.BIG_ENDIAN))
    print(buf.read_int_n(3, Endian.LITTLE_ENDIAN))
    print_info(buf)
    
    buf.destroy()
    print_info(buf)
    
    
    PooledByteBufferAllocator.DEFAULT.release(buf)
    
    print(PooledByteBufferAllocator.DEFAULT)
            

if __name__ == "__main__":        
    def print_info(datas):
        print(f'{datas} {BytesUtils.hex(datas)}')
        
    def test():
        print_info(BytesUtils.write_float(3.14159))
        print(BytesUtils.read_float(BytesUtils.write_float(3.14159)))
        
        print_info(BytesUtils.write_double(3.14159))
        print(BytesUtils.read_double(BytesUtils.write_double(3.14159)))
        
        print_info(BytesUtils.write_double(1.41421356))
        print(BytesUtils.read_double(BytesUtils.write_double(1.41421356)))
        # # 重置读指针并读取
        # buf.reader_index = 0
        
        # 按写入顺序读取
        pi = BytesUtils.read_float(BytesUtils.write_float(3.14159))           # 大端读取    
        
        pi2 = BytesUtils.read_double(BytesUtils.write_double(3.14159))           # 大端读取    
        
        sqrt2 = BytesUtils.read_double(BytesUtils.write_double(1.41421356))       # 双精度大端读取    
        
        
        print("读取的浮点数:")
        print(f"  π ≈ {pi:.8f} (实际: 3.14159)")
        print(f"  π ≈ {pi2:.8f} 双精(实际: 3.14159)")
        print(f"  √2 ≈ {sqrt2:.8f} (实际: 1.41421356)")

        
        # 验证精度
        print("\n精度验证:")
        print(f"  float 误差: |{pi - 3.14159}|")
        print(f"  double 误差: |{pi2 - 3.14159}|")
        print(f"  double 误差: |{sqrt2 - 1.41421356}|")    
        
        
        datas = BytesUtils.write_int_n(-1022, 2, Endian.LITTLE_ENDIAN)        
        d = BytesUtils.read_int_n(datas, 2, 0, Endian.LITTLE_ENDIAN)
        print(f'{datas} = {d}')
        
        
        datas = BytesUtils.write_int_n(-1022, 2, Endian.BIG_ENDIAN)        
        d = BytesUtils.read_int_n(datas, 2, 0, Endian.BIG_ENDIAN)
        print(f'{datas} = {d}')
        
        datas = BytesUtils.write_int_n(16776194, 3, Endian.BIG_ENDIAN)
        d = BytesUtils.read_int_n(datas, 3, 0, Endian.BIG_ENDIAN)
        print(f'{datas} = {d}')
        
        
        datas = BytesUtils.write_int_n(1022, 3, Endian.LITTLE_ENDIAN)
        d = BytesUtils.read_int_n(datas, 3, 0, Endian.LITTLE_ENDIAN)
        print(f'{datas} = {d}')
        
    test()
    
    test_bytebuffer()
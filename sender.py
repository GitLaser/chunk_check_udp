import socket
import struct
import time
import zlib  # 用于计算CRC32校验和

# UDP服务器地址和端口
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 数据分块大小
CHUNK_SIZE = 1024

# 当前块编号


while True:
    # 从标准输入读取数据
    data = input("Enter data to send (or type 'quit' to exit): ")
    chunk_number = 0
    if data.lower() == 'quit':
        break

    # 获取当前时间戳（秒级）
    timestamp = int(time.time())
    mod_val = divmod(len(data), CHUNK_SIZE)
    chunk_nums = mod_val[0] + 1 if mod_val[1] else mod_val[0]

    # 将数据分块
    for i in range(0, len(data), CHUNK_SIZE):
        chunk = data[i:i + CHUNK_SIZE]

        # 计算CRC32校验和
        checksum = zlib.crc32(chunk.encode('utf-8'))

        # 构建消息头：时间戳（4字节，大端序）+ 块编号（4字节，大端序）+ 数据长度（2字节，大端序）+ 校验和（4字节，大端序）
        print(f'timestamp:{timestamp}\nchunk_number:{chunk_number}\nchunk_nums:{chunk_nums}\nlen_chunk:{len(chunk)}')

        struct_timestamp = struct.pack('>I', timestamp)
        struct_chunk_number = struct.pack('>I', chunk_number)
        struct_len_chunk = struct.pack('>h', chunk_nums)
        struct_checksum = struct.pack('>I', checksum)

        # header = struct.pack('>II', timestamp, chunk_number)

        # header = struct.pack('>III', timestamp, chunk_number, len(chunk), checksum)

        # 构建UDP数据报
        message = struct_timestamp + struct_chunk_number + struct_len_chunk + chunk.encode('utf-8') + struct_checksum

        # 发送UDP数据报
        sock.sendto(message, (UDP_IP, UDP_PORT))

        # 打印发送的数据信息
        print(f"Sent data (chunk {chunk_number}): {chunk}")

        # 更新块编号
        chunk_number += 1

# 关闭套接字
sock.close()

import socket
import struct
import zlib
from collections import defaultdict

# UDP服务器地址和端口
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# 创建UDP套接字
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# 存储已接收的数据块
received_chunks = defaultdict(list)

while True:
    # 接收UDP数据报
    data, addr = sock.recvfrom(1024)

    # 解析消息头
    timestamp, chunk_number, data_length = struct.unpack('>IIh', data[:10])
    checksum = struct.unpack('>I', data[-4:])[0]
    print(f'timestamp:{timestamp}\nchunk_number:{chunk_number}\nchecksum:{checksum}')

    payload = data[10:-4]

    # 计算校验和
    calculated_checksum = zlib.crc32(payload)

    # 校验校验和
    if calculated_checksum != checksum:
        print(f"Checksum mismatch for chunk {chunk_number}. Dropping the chunk.")
        continue  # 校验和不匹配，丢弃该数据块

    # 将数据块加入相应时间戳的组中
    received_chunks[timestamp].append((chunk_number, payload))

    # 检查是否组内数据全部接收完毕
    if len(received_chunks[timestamp]) == data_length:
        # 对该组数据进行完整性和索引校验
        sorted_chunks = sorted(received_chunks[timestamp], key=lambda x: x[0])
        expected_chunk_number = 0
        missing_chunks = []

        for chunk_number, payload in sorted_chunks:
            if chunk_number != expected_chunk_number:
                missing_chunks.extend(range(expected_chunk_number, chunk_number))
            expected_chunk_number = chunk_number + 1

        if missing_chunks:
            print(f"Missing chunks in group with timestamp {timestamp}: {missing_chunks}")
            # 触发纠错机制
            # 例如，重新请求缺失的数据块
        else:
            print(f"All chunks received successfully for group with timestamp {timestamp}.")
            # 执行后续的处理流程
            # 例如，对数据进行解码或其他操作

        # 清空该组数据
        del received_chunks[timestamp]

# 关闭套接字
sock.close()

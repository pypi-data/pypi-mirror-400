
def get_local_ip():
    import socket
    try:
        # 对于IPv4，使用socket.AF_INET
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 使用UDP协议的一个不需要的端口号来触发socket错误
        sock.connect(('10.255.255.255', 1))
        local_ip = sock.getsockname()[0]
    except Exception as e:
        local_ip = '127.0.0.1'
    finally:
        sock.close()
    return local_ip


def get_public_ip():
    import requests
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()  # 检查请求是否成功
        ip = response.json()['origin']
        return ip
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None


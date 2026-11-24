import socket
def build(q, ip):
    tid = q[:2]
    i = 12
    while i < len(q) and q[i] != 0: i += q[i]+1
    i += 1 + 4
    question = q[12:i]
    ans = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04" + socket.inet_aton(ip)
    return tid + b"\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00" + question + ans
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", 53))
print("DNS listening")
while True:
    data, addr = s.recvfrom(512)
    s.sendto(build(data, "127.0.0.1"), addr)

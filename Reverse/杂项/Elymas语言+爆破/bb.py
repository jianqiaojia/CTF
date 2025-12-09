import subprocess

ans = [36, 30, 156, 30, 43, 6, 116, 22, 211, 66, 151, 89, 36, 82, 254, 81, 182,
       134, 24, 90, 119, 6, 88, 137, 64, 197, 251, 15, 116, 220, 161, 94, 154, 252,
       139, 11, 41, 215, 27, 158, 143, 140, 54, 189, 146, 48, 167, 56, 84, 226, 15,
       188, 126, 24]

p = subprocess.Popen("./ey_or",
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

# 输入所有48个正确值
for x in ans:
    p.stdin.write((str(x) + '\n').encode())
p.stdin.close()

# 读取输出
output = p.stdout.read().decode()
print(output)
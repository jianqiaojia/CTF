#!/usr/bin/env python3

def solve_flag():
    print("=== 根据正确分析求解Flag ===")
    print()
    
    # 正确的迷宫数据 (8行8列)
    maze = [
        "  ******",  # row 0
        "*   *  *",  # row 1
        "*** * **",  # row 2
        "**  * **",  # row 3
        "*  *#  *",  # row 4  # 在 (4,4)
        "** *** *",  # row 5
        "**     *",  # row 6
        "********"   # row 7
    ]
    
    print("迷宫布局:")
    for i, row in enumerate(maze):
        print(f"Row {i}: '{row}'")
    print()
    
    # 找到 # 的位置
    target_x = target_y = None
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == '#':
                target_x, target_y = x, y
                break
        if target_x is not None:
            break
    
    print(f"目标位置 '#': ({target_x}, {target_y})")
    print()
    
    # 移动函数定义 (根据你的分析)
    # O: go_left (x--)
    # o: go_right (x++)  
    # .: go_up (y--)
    # 0: go_down (y++)
    
    print("移动命令:")
    print("  'O': go_left (x--)")
    print("  'o': go_right (x++)")
    print("  '.': go_up (y--)")
    print("  '0': go_down (y++)")
    print()
    
    # 使用BFS寻找从(0,0)到(4,4)的路径
    from collections import deque
    
    def find_path():
        queue = deque([(0, 0, "")])  # (x, y, path)
        visited = set()
        visited.add((0, 0))
        
        directions = {
            'O': (-1, 0),  # left (x--)
            'o': (1, 0),   # right (x++)
            '.': (0, -1),  # up (y--)
            '0': (0, 1)    # down (y++)
        }
        
        while queue:
            x, y, path = queue.popleft()
            
            # 如果到达目标
            if (x, y) == (target_x, target_y):
                return path
            
            # 如果路径太长，停止搜索
            if len(path) >= 20:
                continue
                
            # 尝试每个方向
            for move, (dx, dy) in directions.items():
                nx, ny = x + dx, y + dy
                
                # 检查边界
                if 0 <= nx < 8 and 0 <= ny < 7 and (nx, ny) not in visited:
                    # 检查是否可以移动到该位置
                    if maze[ny][nx] in [' ', '#']:
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + move))
        
        return None
    
    print("寻找路径...")
    path = find_path()
    
    if path:
        print(f"找到路径: '{path}'")
        print(f"路径长度: {len(path)}")
        
        # 验证路径
        print("\n验证路径:")
        x, y = 0, 0
        print(f"起始位置: ({x}, {y}) = '{maze[y][x]}'")
        
        for i, move in enumerate(path):
            if move == 'O':
                x -= 1
            elif move == 'o':
                x += 1
            elif move == '.':
                y -= 1
            elif move == '0':
                y += 1
            
            print(f"步骤 {i+1}: '{move}' -> ({x}, {y}) = '{maze[y][x]}'")
        
        # 构造flag
        flag = f"nctf{{{path}}}"
        print(f"\nFlag: {flag}")
        print(f"Flag长度: {len(flag)}")
        
        if len(flag) == 24:
            print("✅ Flag长度正确!")
            return flag
        else:
            print("❌ Flag长度不正确，需要24个字符")
    else:
        print("❌ 没有找到路径")
    
    return None

if __name__ == "__main__":
    result = solve_flag()
    if result:
        print(f"\n🎉 最终Flag: {result}")
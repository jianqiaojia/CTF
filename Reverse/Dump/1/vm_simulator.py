#!/usr/bin/env python3
"""
VM 模拟器 - 分析没有 maze_data 时的执行规律
"""
import struct

class VMSimulator:
    def __init__(self):
        self.regs = [0] * 10  # reg0-reg9，预留更多空间
        self.memory = {}  # 模拟内存
        self.pc = 0  # 程序计数器
        self.loop_start = 0
        self.input_data = []
        self.input_index = 0
        
        # 字节码程序（从 0x180005038 提取）
        self.bytecode = bytes([
            0x81, 0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # 从固定地址加载
            0x31, 0x00, 0x00, 0x00, 0x00,                          # reg1 = 0
            0x32, 0x01, 0x00, 0x00, 0x00,                          # reg2 = 1
            0x33, 0xC2, 0x00, 0x00, 0x00,                          # reg3 = 194 (0xC2)
            0x50,                                                   # 标记循环开始
            0x07, 0xC2, 0x00, 0x00,                                # reg3 += 194
            0x82,                                                   # 从输入读取
            0x83,                                                   # 根据输入移动
            0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # 从内存加载并累加
            0x34, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # 存储到内存
            0x05, 0x01, 0x00, 0x00,                                # reg1 += 1
            0x40, 0x01, 0xC0, 0x00, 0x00, 0x00,                    # 比较 reg1 和 192
            0x51,                                                   # 条件跳转
        ])
        
    def set_input(self, input_str):
        """设置输入字符串"""
        self.input_data = [ord(c) for c in input_str]
        self.input_index = 0
        
    def read_u32(self, offset):
        """从字节码读取 32 位整数"""
        return struct.unpack('<I', self.bytecode[offset:offset+4])[0]
    
    def read_u64(self, offset):
        """从字节码读取 64 位整数"""
        return struct.unpack('<Q', self.bytecode[offset:offset+8])[0]
    
    def execute_instruction(self):
        """执行一条指令，返回 (继续执行, 指令描述)"""
        if self.pc >= len(self.bytecode):
            return False, "程序结束"
        
        opcode = self.bytecode[self.pc]
        
        # 0x31-0x33: 加载立即数到寄存器
        if 0x30 <= opcode <= 0x33:
            reg = opcode - 0x30
            value = self.read_u32(self.pc + 1)
            self.regs[reg] = value
            self.pc += 5
            return True, f"reg{reg} = {value}"
        
        # 0x05-0x07: 24位立即数加法
        elif 0x04 <= opcode <= 0x07:
            reg = opcode - 0x04
            value = self.read_u32(self.pc + 1) & 0xFFFFFF
            self.regs[reg] += value
            self.pc += 4
            return True, f"reg{reg} += {value} (现在 = {self.regs[reg]})"
        
        # 0x50: 标记循环位置
        elif opcode == 0x50:
            self.loop_start = self.pc
            self.pc += 1
            return True, f"标记循环位置: PC={self.loop_start}"
        
        # 0x82: 从输入数组读取
        elif opcode == 0x82:
            if self.input_index < len(self.input_data):
                input_char = self.input_data[self.input_index]
                self.regs[0] = input_char
                self.pc += 1
                return True, f"读取输入[{self.input_index}] = '{chr(input_char)}' (0x{input_char:02x})"
            else:
                self.pc += 1
                return True, f"读取输入[{self.input_index}] = EOF"
        
        # 0x83: 根据输入移动
        elif opcode == 0x83:
            input_char = self.regs[0]
            # 这是关键指令！让我们分析它的行为
            if input_char == ord('0'):
                # 假设 '0' 导致某种移动
                action = "输入='0': 可能向上或向左移动"
                # 从反汇编看，可能修改 reg2 或 reg3
                # 让我们假设向上移动（Y-1）
                move_result = f"reg2 可能变化 (当前={self.regs[2]})"
            elif input_char == ord('1'):
                # 假设 '1' 导致另一种移动
                action = "输入='1': 可能向下或向右移动"
                move_result = f"reg3 可能变化 (当前={self.regs[3]})"
            else:
                action = f"未知输入: 0x{input_char:02x}"
                move_result = ""
            
            self.input_index += 1
            self.pc += 1
            return True, f"0x83: {action}. {move_result}"
        
        # 0x08: 从内存加载并累加
        elif opcode == 0x08:
            addr = self.read_u64(self.pc + 1)
            # 这里会从 maze_data 读取
            # 没有 maze_data，我们无法模拟具体值
            self.pc += 9
            return True, f"从内存[0x{addr:x}]加载值并累加到reg4 (需要maze_data)"
        
        # 0x34: 存储到内存
        elif opcode == 0x34:
            addr = self.read_u64(self.pc + 1)
            self.memory[addr] = self.regs[4]
            self.pc += 9
            return True, f"存储 reg4={self.regs[4]} 到内存[0x{addr:x}]"
        
        # 0x81: 从固定地址加载（指令格式：81 [8字节地址]）
        elif opcode == 0x81:
            # 0x81 后面直接是 8 字节地址，没有寄存器参数
            # 结果存储到 reg4（根据指令集文档）
            addr = self.read_u64(self.pc + 1)
            # 这会从某个固定地址加载初始值
            self.regs[4] = 0  # 没有数据，用 0，存储到 reg4
            self.pc += 9
            return True, f"reg4 = load from 0x{addr:x} (需要maze_data，暂用0)"
        
        # 0x40: 比较指令
        elif opcode == 0x40:
            reg = self.bytecode[self.pc + 1]
            value = self.read_u32(self.pc + 2)
            cmp_result = self.regs[reg] >= value
            self.pc += 6
            return True, f"比较 reg{reg}({self.regs[reg]}) >= {value}: {cmp_result}"
        
        # 0x51: 条件跳转
        elif opcode == 0x51:
            # 根据上一次比较结果跳转
            if self.regs[1] < 192:  # 如果计数器 < 192，继续循环
                self.pc = self.loop_start + 1
                return True, f"跳转回循环开始 (PC={self.loop_start}), reg1={self.regs[1]}"
            else:
                self.pc += 1
                return True, f"退出循环, reg1={self.regs[1]}"
        
        else:
            return False, f"未知操作码: 0x{opcode:02x}"
    
    def run(self, input_str, max_steps=1000):
        """运行 VM"""
        self.set_input(input_str)
        self.pc = 0
        self.regs = [0] * 10  # 匹配 __init__
        self.memory = {}
        
        print(f"\n{'='*70}")
        print(f"执行 VM 模拟 - 输入: {input_str[:20]}... (长度={len(input_str)})")
        print(f"{'='*70}\n")
        
        step = 0
        traces = []
        
        while step < max_steps:
            continue_exec, desc = self.execute_instruction()
            
            if step < 50 or step % 50 == 0:  # 只显示前50步和每50步
                print(f"步骤 {step:4d}: PC={self.pc:3d} | {desc}")
                print(f"           寄存器: reg0={self.regs[0]:3d}, reg1={self.regs[1]:3d}, "
                      f"reg2={self.regs[2]:3d}, reg3={self.regs[3]:4d}, reg4={self.regs[4]:5d}")
            
            traces.append({
                'step': step,
                'pc': self.pc,
                'desc': desc,
                'regs': self.regs.copy()
            })
            
            if not continue_exec:
                break
            
            step += 1
        
        print(f"\n{'='*70}")
        print(f"执行完成！总步数: {step}")
        print(f"最终寄存器状态:")
        print(f"  reg0={self.regs[0]}, reg1={self.regs[1]}, reg2={self.regs[2]}, "
              f"reg3={self.regs[3]}, reg4={self.regs[4]}")
        print(f"{'='*70}\n")
        
        return traces


def main():
    vm = VMSimulator()
    
    # 测试不同的输入模式
    test_cases = [
        ("0" * 10, "全0 (前10个)"),
        ("1" * 10, "全1 (前10个)"),
        ("01" * 5, "交替01 (前10个)"),
    ]
    
    for input_str, desc in test_cases:
        print(f"\n\n" + "="*80)
        print(f"测试用例: {desc}")
        print("="*80)
        traces = vm.run(input_str)
        
        # 分析 reg2 和 reg3 的变化模式
        print("\n分析寄存器变化:")
        print(f"{'步骤':<8} {'reg1':<6} {'reg2':<8} {'reg3':<10} {'说明'}")
        print("-" * 60)
        for i, t in enumerate(traces):
            if i < 30 or (i > len(traces) - 10):  # 显示前30步和最后10步
                print(f"{t['step']:<8} {t['regs'][1]:<6} {t['regs'][2]:<8} "
                      f"{t['regs'][3]:<10} {t['desc'][:40]}")

if __name__ == '__main__':
    main()
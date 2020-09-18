"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0 # counter
        self.sp = self.reg[7]
        self.flag = 0b00000000

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue

                    try:
                        n = int(n, 2)
                    except ValueError:
                        print(f"Invalid number '{n}'")
                        sys.exit(1)

                    self.ram[address] = n
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)
        
         # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            self.flag = 0b00000000

            if self.ram[reg_a] == self.ram[reg_b]:
                self.flag = 0b00000001
            else:
                self.flag = 0b00000000
            
            if self.ram[reg_a] < self.ram[reg_b]:
                self.flag = 0b00000100
            else:
                self.flag = 0b00000000

            if self.ram[reg_a] > self.ram[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000000

        else:
            raise Exception("Unsupported ALU operation")

    
    def jump(self, operand_a):
        self.pc = self.reg[operand_a]

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def push(self, operand_a):
        self.sp -= 1
        self.ram[self.sp] = self.reg[operand_a]

    def pop(self, operand_a):
        self.reg[operand_a] = self.ram[self.sp]
        self.sp += 1

        return self.sp

    def run(self):
        """Run the CPU."""
        self.trace()

        HLT = 0b00000001
        LDI = 0b10000010
        PRN = 0b01000111
        MUL = 0b10100010
        PUSH = 0b01000101
        POP = 0b01000110
        CALL = 0b01010000
        RET = 0b00010001
        CMP = 0b10100111
        JMP = 0b01010100
        JNE = 0b01010110
        JEQ = 0b01010101

        running = True

        while running:
            self.trace()
            IR = self.ram[self.pc]

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            elif IR == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif IR == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            elif IR == PUSH:
                self.push(operand_a)
                self.pc += 2
            elif IR == POP:
                self.pop(operand_a)
                self.pc += 2
            elif IR == CALL:
                self.push(operand_a)
                self.ram[self.sp] = self.pc + 2
                self.pc = self.reg[operand_a]
            elif IR == RET:
                self.pc = self.ram[self.sp]
            elif IR == CMP:
                self.alu("CMP", self.reg[operand_a], self.reg[operand_b])
                self.pc += 3
            elif IR == JMP:
                self.pc = self.reg[operand_a]
            elif IR == JNE:
                if self.flag == 0b00000000:
                    self.jump(operand_a)
                else:
                    self.pc += 2
            elif IR == JEQ:
                if self.flag == 0b00000001:
                    self.jump(operand_a)
                else:
                    self.pc += 2
            elif IR == HLT:
                running = False
            else:
                print("Invalid command")
                running = False

"""CPU functionality."""

import sys

HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MUL = 0b10100010
ADD = 0b10100000
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
IRET = 0b00010011
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # STEP 1 - Add list properties to the CPU class to hold 256 bytes of memory and 8 general purpose registers
        self.ram = [0] * 256
        self.register = [0] * 8
        self.flag = [0] * 8
        self.pc = 0  # program counter
        self.sp = 0xf3  # 243 # stack pointer

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) < 2:
            print(
                "Please pass in a second filename: py ls8.py [second_filename.py] <-- file to load")
            sys.exit()

        filename = sys.argv[1]

        # opening filename and assigning it to program variable
        with open(filename) as program:
            try:
                # for every line in the program
                for line in program:
                    # separating the #
                    line = line.split('#')[0]
                    # removes spaces at the ZEROith index
                    command = line.strip()

                    if command == '':
                        continue
                    self.ram[address] = int(command, 2)
                    address += 1

            except FileNotFoundError:
                print(f"{sys.argv[0]:}{sys.argv[1]} file was not found")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        if op == 'MUL':
            self.register[reg_a] *= self.register[reg_b]
        if op == 'CMP':
            # if they are equal, set flag to 1
            if self.register[reg_a] == self.register[reg_b]:
                self.flag = 0b00000001
            # if register A is less than register b set L flag to 1
            if self.register[reg_a] < self.register[reg_b]:
                self.flag = 0b00000100
            # if register A is greater than B set the G flag to 1
            if self.register[reg_a] > self.register[reg_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # STEP 3 - Implement the core of RUN
        running = True
        while running:
            # instruction = the ram AT wherever the pc is
            instruction = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if instruction == HLT:
                # HALTS THE CPU AND EXIT THE EMULATOR
                running = False

            if instruction == CALL:
                # calls a function at the ADDRESS stored in the register
                # the address of the instruction DIRECTLY after call gets pushed to stack
                # PC is set to the address stored in given register
                self.sp -= 1
                self.ram[self.sp] = self.pc + 2
                self.pc = self.register[operand_a]

            if instruction == RET:
                # registers r6-r0 popped off stack
                # FL register popped off stack
                # return address popped off stack and stored = in PC
                # interrupts are re-enabled
                self.pc = self.ram[self.sp]
                self.sp += 1

            if instruction == PUSH:

                # r7 is the stack pointer
                # SP is the top of the stack
                # decrement the SP
                self.sp -= 1
                # copy the value in the given register to the address pointed by SP
                # taking the STACK POINTER address(index) and assigning the first argument of the instruction
                self.ram[self.sp] = self.register[operand_a]
                self.pc += 2

            if instruction == POP:
                # Copy the value from the address pointed to by SP to the given register.
                # from the address --- to the register
                self.register[operand_a] = self.ram[self.sp]
                # Increment SP
                self.sp += 1
                self.pc += 2

            if instruction == LDI:
                # LDI SETS THE VALUE OF A REGISTER TO AN INTEGER
                # the register at whatever index you are given = the value/argument 2
                self.register[operand_a] = operand_b
                self.pc += 3

            if instruction == MUL:
                self.alu('MUL', operand_a, operand_b)
                self.pc += 3

            if instruction == ADD:
                self.alu('ADD', operand_a, operand_b)
                self.pc += 3

            if instruction == CMP:
                # instruction handled by alu
                self.alu('CMP', operand_a, operand_b)
                self.pc += 3

            if instruction == JMP:
                self.pc = self.register[self.ram_read(self.pc + 1)]

            if instruction == JNE:
                if not self.flag_check():
                    reg_num = self.ram[self.pc + 1]
                    self.pc = self.register[reg_num]
                else:
                    self.pc += 2

            if instruction == JEQ:
                if self.flag_check():
                    reg_num = self.ram[self.pc + 1]
                    self.pc = self.register[reg_num]
                else:
                    self.pc += 2

            if instruction == PRN:
                # PRINTS NUMERIC VALUE STORED IN THE GIVEN REGISTER
                value = self.register[operand_a]
                print(value)
                self.pc += 2

# STEP 2: Add RAM functions ram_read and ram_write
    # These access the RAM inside the CPU object

    def ram_read(self, address):
        # RR should accept the address to read and return the value
        return self.ram[address]

    def ram_write(self, address, value):
        # RW should accept a value to write and the address to write it to
        self.ram[address] = value

    def flag_check(self):
        return (self.flag == 1)

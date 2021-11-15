import sys

MIPS = {16: "J", 17: "JR", 18: "BEQ", 19: "BLTZ", 20: "BGTZ", 21: "BREAK",
        22: "SW", 23: "LW", 24: "SLL", 25: "SRL", 26: "SRA", 27: "NOP",
        48: "ADD", 49: "SUB", 50: "MUL", 51: "AND", 52: "OR", 53: "XOR",
        54: "NOR", 55: "SLT", 56: "ADDI", 57: "ANDI", 58: "ORI", 59: "XORI"}

I_type = ["ADDI", "ANDI", "ORI", "XORI", "BEQ", "BLTZ", "BGTZ", "SW", "LW"]
R_type = ["ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOR", "SLT", "JR", "SLL", "SRL",
          "SRA", "NOP"]
J_type = ["J"]
Branch = ["J", "JR", "BEQ", "BLTZ", "BGTZ", "Break", "NOPs"]

REGISTERS = [0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0]
MEMORY = []
PC = 256

CodeWithData = {}

PreIssueQueue = ["", "", "", ""]
# PreIssueQueue[0]: Entry 0
# PreIssueQueue[1]: Entry 1
# PreIssueQueue[2]: Entry 2
# PreIssueQueue[3]: Entry 3

PreALU1Queue = ["", ""]
PreALU2Queue = ["", ""]
PreMEMQueue = [""]
PostALU2Queue = ["", ""]
PostMEMQueue = [""]

RegState = ["", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", ]

IFUnit = ["", ""]
# IFUnit[0]: Waiting Waiting Instruction
# IFUnit[1]: Executed Instruction
WaitSignal = False


def IsFull(Queue, length):
    for i in range(length):
        if Queue[i] == "":  # 若
            return i

    return -1


def IsEmpty(Queue, length):
    cnt = 0
    for i in range(length):
        if Queue[i] == "":
            cnt += 1
    if cnt == length:
        return 1
    else:
        return 0


def EnQueue(Queue, length, elem):
    i = IsFull(Queue, length)
    if i >= 0:
        Queue[i] = elem


def DeQueue(Queue, length):
    if not IsEmpty(Queue, length):
        command = Queue.pop(0)
        Queue.append("")
        return command
    return None


def Simulation(Memory, pc):
    # Issue Unit
    cycle = 1

    while cycle < 3:  # 当 IF Unit 中执行的指令为 Break 时退出
        # 每次 Issue 两条指令
        IFetch(Memory, pc)
        IFetch(Memory, pc + 4)
        Issue()
        if cycle == 1:
            Print(cycle)
            cycle += 1
            continue
        # Issue 指令
        Issue()
        # 执行
        Execute()
        # Mem
        MemOperate()
        # 写回
        pc1 = WriteBack(pc)
        if pc != pc1:
            pc = pc1
        else:
            pc = pc + 4
        cycle += 1


def Print(cycle):
    print("--------------------\n")
    print("Cycle:{}\n".format(cycle))
    print("\n")
    print("IF Unit:\n")
    print("\tWaiting Instruction:{}\n".format(IFUnit[0]))
    print("\tExecuted Instruction:{}\n".format(IFUnit[1]))
    print("Pre-Issue Queue:\n")
    print("\tEntry 0:{}\n".format(PreIssueQueue[0]))
    print("\tEntry 1:{}\n".format(PreIssueQueue[1]))
    print("\tEntry 2:{}\n".format(PreIssueQueue[2]))
    print("\tEntry 3:{}\n".format(PreIssueQueue[3]))
    print("Pre-ALU1 Queue:\n")
    print("\tEntry 0:{}\n".format(PreALU1Queue[0]))
    print("\tEntry 1:{}\n".format(PreALU1Queue[1]))
    print("Pre-MEM Queue:{}\n".format(PreMEMQueue[0]))
    print("Post-MEM Queue:{}\n".format(PostMEMQueue))
    print("Pre-ALU2 Queue:\n")
    print("\tEntry 0:{}\n".format(PreALU2Queue[0]))
    print("\tEntry 1:{}\n".format(PreALU2Queue[1]))
    print("Post-ALU2 Queue:{}\n".format(PostALU2Queue[0]))
    print("Registers\n")
    print("R00:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[0], REGISTERS[1],
                                                          REGISTERS[2], REGISTERS[3],
                                                          REGISTERS[4], REGISTERS[5],
                                                          REGISTERS[6], REGISTERS[7]))
    print("R08:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[8], REGISTERS[9],
                                                          REGISTERS[10], REGISTERS[11],
                                                          REGISTERS[12], REGISTERS[13],
                                                          REGISTERS[14], REGISTERS[15]))
    print("R16:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[16], REGISTERS[17],
                                                          REGISTERS[18], REGISTERS[19],
                                                          REGISTERS[20], REGISTERS[21],
                                                          REGISTERS[22], REGISTERS[23]))
    print("R24:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[24], REGISTERS[25],
                                                          REGISTERS[26], REGISTERS[27],
                                                          REGISTERS[28], REGISTERS[29],
                                                          REGISTERS[30], REGISTERS[31]))
    print("\nData\n")
    print("300:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[11], MEMORY[12],
                                                          MEMORY[13], MEMORY[14],
                                                          MEMORY[15], MEMORY[16],
                                                          MEMORY[17], MEMORY[18]) +
          "332:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[19], MEMORY[20],
                                                          MEMORY[21], MEMORY[22],
                                                          MEMORY[23], MEMORY[24],
                                                          MEMORY[25], MEMORY[26]))
    print("\n")


def IFetch(Memory, pc):
    i = int((pc - 256) / 4)
    if not IsFull(PreIssueQueue, 4) and IFUnit[0] == "":  # PreIssueQueue未满，且IFUnit中没有等待的指令
        OP1 = Memory[i][:3]
        print("1")
        if OP1 not in Branch:
            EnQueue(PreIssueQueue, 4, Memory[i])
            print("2")
            print(PreIssueQueue[0])
            return 1
        else:
            if OP1 == "J" or OP1 == "Break":
                if IFUnit[1] == "":  # 若执行单元为空，则放入IFUnit执行单元
                    IFUnit[1] = Memory[i]
                else:  # 若有指令占用执行单元，则放入IFUnit等待单元
                    IFUnit[0] = Memory[i]

            elif OP1 == "JR":
                ls = CodeWithData(Memory[i])
                rs = ls[0]
                if RegState[rs] == "" and IFUnit[1] == "":  # 首先检查含有跳转地址的寄存器是否被占用
                    IFUnit[1] = Memory[i]
                else:
                    IFUnit[0] = Memory[i]
            else:  # "BEQ","BLTZ", "BGTZ"
                ls = CodeWithData(Memory[i])
                rs = ls[0]
                rt = ls[0]
                if RegState[rs] == "" and RegState[rt] == "" and IFUnit[1] == "":  # 先检查寄存器是否被占用
                    IFUnit[1] = Memory[i]  # IFUnit 执行单元可用
                else:
                    IFUnit[0] = Memory[i]  # IFUnit 执行单元不可用


def Issue():
    if PreIssueQueue[0] != '':
        command = PreIssueQueue[0]
        OP = command[:3]

        if OP == "LW" or OP == "SW":
            if CheckRegState(command) and IFUnit[0] == "":
                DeQueue(PreIssueQueue, 4)
                EnQueue(PreALU1Queue, 2, command)

        else:
            if CheckRegState(command) and IFUnit[0] == "":
                DeQueue(PreIssueQueue, 4)
                EnQueue(PreALU2Queue, 2, command)


def Execute():
    if IFUnit[0] != "":
        code = IFUnit[0]
        IFUnit[0] = ""
        IFUnit[1] = code

    if PreALU1Queue[0] != '' and IsEmpty(PreMEMQueue, 1):
        command = PreALU1Queue[0]
        if CheckRegState(command):
            ModifyRegState(command)
            EnQueue(PreMEMQueue, 1, command)
            DeQueue(PreALU1Queue, 2)
    if PreALU2Queue[0] != '' and IsEmpty(PostALU2Queue, 1):
        command = PostALU2Queue[0]
        if CheckRegState(command):
            ModifyRegState(command)
            EnQueue(PostALU2Queue, 1, command)
            DeQueue(PostALU2Queue, 2)


def MemOperate():
    if PreMEMQueue[0] != "" and IsEmpty(PostMEMQueue, 1):
        command = PreMEMQueue[0]
        EnQueue(PostMEMQueue, 1, command)
        DeQueue(PostMEMQueue, 1)


def WriteBack(pc):
    if PostALU2Queue[0] != "":
        command = PostALU2Queue[0]
        if CheckRegState(command):
            pc = Operation(command, pc)
            ResetRegState(command)
    if PostMEMQueue[0] != "":
        command = PostMEMQueue[0]
        if CheckRegState(command, pc):
            pc = Operation(command, pc)
            ResetRegState(command)
    return pc


def CheckRegState(code):  # 检查要访问的寄存器位置
    ls = CodeWithData[code]
    for i in range(len(ls)):
        if RegState[ls[i]] != "":
            return -1
    return 1


def ModifyRegState(code):  # 修改寄存器状态
    ls = CodeWithData[code]
    OP = code[:3]
    for i in range(len(ls)):
        if REGISTERS[ls[i]] == "":
            REGISTERS[ls[i]] = OP


def ResetRegState(code):
    ls = CodeWithData[code]
    for i in range(len(ls)):
        REGISTERS[ls[i]] = ""


def Decode(MachineCode, op):  #
    """
    :param MachineCode: 机器码
    :param op: 操作码
    :return:
    """
    if 16 <= op <= 59:  # 读取到的是指令
        OP = MIPS[op]

        if OP in R_type:
            if OP == "SLL" or OP == "SRL" or OP == "SRA" or OP == "NOP":
                rt = int(MachineCode[11:16], 2)
                rd = int(MachineCode[16:21], 2)
                sa = int(MachineCode[21:26], 2)
                ls = [rt, rd, sa]

                AssemblyCode = "{} R{}, R{}, #{}".format(OP, rd, rt, sa)

            elif OP == "JR":  # PC <- rs
                rs = int(MachineCode[11:16], 2)
                ls = [rs]
                AssemblyCode = "{} R{}".format(OP, rs)

            elif OP == "SLT":  # rd <- (rs < rt)
                rs = ComToDec(MachineCode[6:11])
                rt = ComToDec(MachineCode[11:16])
                rd = ComToDec(MachineCode[16:21])
                ls = [rs, rt, rd]
                AssemblyCode = "{} R{}, R{}, R{}".format(OP, rd, rs, rt)

            else:
                rs = int(MachineCode[6:11], 2)
                rt = int(MachineCode[11:16], 2)
                rd = int(MachineCode[16:21], 2)
                ls = [rs, rt, rd]
                AssemblyCode = "{} R{}, R{}, R{}".format(OP, rd, rs, rt)

        if OP in I_type:
            rs = int(MachineCode[6:11], 2)
            rt = int(MachineCode[11:16], 2)
            imm = MachineCode[16:]
            imm_value = ComToDec(imm)
            ls = [rs, rt, imm_value]
            if OP == "BEQ":
                AssemblyCode = "{} R{}, R{}, #{}".format(OP, rs, rt, imm_value * 4)
            if OP == "BLTZ":
                AssemblyCode = "{} R{}, #{}".format(OP, rs, imm_value * 4)
            if OP == "BGTZ":
                AssemblyCode = "{} R{}, #{}".format(OP, rs, imm_value * 4)
            if OP == "SW":
                AssemblyCode = "{} R{}, {}(R{})".format(OP, rt, imm_value, rs)
            if OP == "LW":
                AssemblyCode = "{} R{}, {}(R{})".format(OP, rt, imm_value, rs)
            if OP == "ADDI":
                AssemblyCode = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)
            if OP == "ANDI":
                AssemblyCode = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)
            if OP == "ORI":
                AssemblyCode = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)
            if OP == "XORI":
                AssemblyCode = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)

        if OP in J_type:
            addr = int(MachineCode[6:], 2)
            ls = [addr]
            AssemblyCode = "{} #{}".format(OP, addr * 4)

        if OP == "BREAK":
            ls = []
            AssemblyCode = "{}".format(OP)

        CodeWithData[AssemblyCode] = ls
    else:  # 读取到数据
        value = ComToDec(MachineCode)
        AssemblyCode = "{}".format(value)

    return AssemblyCode


def Operation(AssemblyCode, pc):
    OP = AssemblyCode[:3]
    ls = CodeWithData[AssemblyCode]
    if OP == "SLL" or OP == "NOP":  # SLL R16, R1, #2
        rt = ls[0]
        rd = ls[1]
        sa = ls[2]
        REGISTERS[rd] = REGISTERS[rt] * (2 ** sa)
    if OP == "SRL" or OP == "SRA":
        rt = ls[0]
        rd = ls[1]
        sa = ls[2]
        REGISTERS[rd] = REGISTERS[rt] / (2 ** sa)  # rd <- rt >> sa
    if OP == "JR":
        rs = ls[0]
        pc = REGISTERS[rs]
    if OP == "SLT":
        rd = ls[3]
        if rs < rt:
            REGISTERS[rd] = 1
        else:
            REGISTERS[rd] = 0
    if OP == "ADD":  # rd <- rs + rt
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = REGISTERS[rs] + REGISTERS[rt]
    if OP == "SUB":  # rd <- rs - rt
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = REGISTERS[rs] - REGISTERS[rt]
    if OP == "MUL":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = REGISTERS[rs] * REGISTERS[rt]
    if OP == "AND":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = REGISTERS[rs] and REGISTERS[rt]
    if OP == "OR":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = REGISTERS[rs] or REGISTERS[rt]
    if OP == "XOR":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = REGISTERS[rs] ^ REGISTERS[rt]
    if OP == "NOR":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = not (REGISTERS[rs] or REGISTERS[rt])
    if OP == "BEQ":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        if REGISTERS[rs] == REGISTERS[rt]:
            pc += imm_value * 4 + 4
    if OP == "BLTZ":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        if REGISTERS[rs] < 0:
            pc += imm_value * 4 + 4
    if OP == "BGTZ":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        if REGISTERS[rs] > 0:
            pc += imm_value * 4 + 4
    if OP == "SW":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        base = REGISTERS[rs]
        addr = base + imm_value
        MEMORY[int((addr - 256) / 4)] = REGISTERS[rt]
    if OP == "LW":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        base = REGISTERS[rs]
        addr = base + imm_value
        REGISTERS[rt] = MEMORY[int((addr - 256) / 4)]
    if OP == "ADDI":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        REGISTERS[rt] = REGISTERS[rs] + imm_value
    if OP == "ANDI":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        REGISTERS[rt] = REGISTERS[rs] and imm_value
    if OP == "ORI":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        REGISTERS[rt] = REGISTERS[rs] or imm_value
    if OP == "XORI":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        REGISTERS[rt] = REGISTERS[rs] ^ imm_value
    if OP == "J":
        addr = ls[0]
        pc = addr * 4

    return pc


def ComToDec(com_str):  # 补码求真值
    if com_str[0] == '0':
        DecValue = int(com_str[1:], 2)
    else:
        ori_str = ""
        for i in com_str:
            if i == "0":
                ori_str += "1"
            else:
                ori_str += "0"
        DecValue = - (int(ori_str[1:], 2) + 1)

    return DecValue


def ReadfileToMemory(FilePath):  # 将机器码文件读入到Memory中
    with open("{}".format(FilePath), 'r') as f:
        pc = PC
        for MachineCode in f:
            # 去除换行符
            if MachineCode.endswith("\n"):
                MachineCode = MachineCode.replace("\n", "")
            if MachineCode.endswith("\r\n"):
                MachineCode = MachineCode.replace("\r\n", "")

            # 将机器码翻译成汇编指令和数据
            op = int(MachineCode[:6], 2)
            AssemblyCode = Decode(MachineCode, op)

            # 将汇编指令和数据存入内存
            MEMORY.append(AssemblyCode)

    return MEMORY


def CommandToFile(memory, pc):  # 将汇编代码写入到 disassembly.txt
    with open("./disassembly.txt", 'w') as f:
        for MachineCode in memory:
            op = int(MachineCode[:6], 2)
            AssemblyCode = Decode(MachineCode, op, pc)
            line = "{}\t{}\t{}".format(MachineCode, pc, AssemblyCode)
            pc += 4
            f.write(line + '\n')


if __name__ == '__main__':
    # file_name = sys.argv[1]
    # file_path = './' + file_name  # 输入sample.txt
    file_path = ".\sample1.txt"
    MEMORY = ReadfileToMemory(file_path)
    OP = MEMORY[0][:3]
    print(OP)
    pc = 256
    Simulation(MEMORY, pc)

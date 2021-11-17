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
CodeWithOP = {}

PreIssueQueue = []
# PreIssueQueue[0]: Entry 0
# PreIssueQueue[1]: Entry 1
# PreIssueQueue[2]: Entry 2
# PreIssueQueue[3]: Entry 3

PreALU1Queue = ["", ""]
PreALU2Queue = ["", ""]
PreMEMQueue = [""]
PostALU2Queue = [""]
PostMEMQueue = [""]

RegState = ["", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", ""]
IFUnit = ["", ""]
# IFUnit[0]: Waiting Waiting Instruction
# IFUnit[1]: Executed Instruction
WaitSignal = False
ExecuteSignal = False
RegResetFlag = False
WARSignal = False
WAWSignal = False
WARSignal = False
flag4break = False
TempList = []
TempList1 = []


def IsFull(Queue, length):
    for i in range(length):
        if Queue[i] == "":  # 若
            return False

    return True


def IsEmpty(Queue, length):
    cnt = 0
    for i in range(length):
        if Queue[i] == "":
            cnt += 1
    if cnt == length:
        return True
    else:
        return False


def EnQueue(Queue, length, elem):
    if not IsFull(Queue, length):
        for i in range(length):
            if Queue[i] == "":
                Queue[i] = elem
                break


def DeQueue(Queue, length):
    if not IsEmpty(Queue, length):
        command = Queue.pop(0)
        Queue.append("")
        return command
    return None


def Simulation():
    # Issue Unit
    cycle = 1
    global flag4break
    with open("./test.txt", "w") as f:
        while not flag4break:  # 当 IF Unit 中执行的指令为 Break 时退出
            WriteBack()
            MemOperate()
            Execute()
            OccupiedSlot = Issue()
            IFetch(OccupiedSlot)
            CheckTempList()
            WriteToFile(cycle, f)
            #Print(cycle)
            cycle += 1


def CheckTempList():
    if TempList:
        for code in TempList:
            ResetRegState(code)
            TempList.remove(code)
    if TempList1:
        for code in TempList1:
            ResetRegState(code)
            TempList1.remove(code)


def Print(cycle):
    print("--------------------\n")
    print("Cycle:{}\n".format(cycle))
    print("\n")
    print("IF Unit:\n")
    print("\tWaiting Instruction: {}\n".format(IFUnit[0]))
    print("\tExecuted Instruction: {}\n".format(IFUnit[1]))
    print("Pre-Issue Queue:\n")
    if len(PreIssueQueue) == 1:
        print("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        print("\tEntry 1:\n")
        print("\tEntry 2:\n")
        print("\tEntry 3:\n")
    if len(PreIssueQueue) == 2:
        print("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        print("\tEntry 1: {}\n".format(PreIssueQueue[1]))
        print("\tEntry 2:\n")
        print("\tEntry 3:\n")
    if len(PreIssueQueue) == 3:
        print("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        print("\tEntry 1: {}\n".format(PreIssueQueue[1]))
        print("\tEntry 2: {}\n".format(PreIssueQueue[2]))
        print("\tEntry 3:\n")
    if len(PreIssueQueue) == 4:
        print("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        print("\tEntry 1: {}\n".format(PreIssueQueue[1]))
        print("\tEntry 2: {}\n".format(PreIssueQueue[2]))
        print("\tEntry 3: {}\n".format(PreIssueQueue[3]))
    print("Pre-ALU1 Queue:\n")
    print("\tEntry 0: {}\n".format(PreALU1Queue[0]))
    print("\tEntry 1: {}\n".format(PreALU1Queue[1]))
    print("Pre-MEM Queue: {}\n".format(PreMEMQueue[0]))
    print("Post-MEM Queue: {}\n".format(PostMEMQueue[0]))
    print("Pre-ALU2 Queue:\n")
    print("\tEntry 0: {}\n".format(PreALU2Queue[0]))
    print("\tEntry 1: {}\n".format(PreALU2Queue[1]))
    print("Post-ALU2 Queue: {}\n".format(PostALU2Queue[0]))
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


def WriteToFile(cycle, f):
    f.writelines("--------------------\n")
    f.writelines("Cycle:{}\n".format(cycle))
    f.writelines("\n")
    f.writelines("IF Unit:\n")
    f.writelines("\tWaiting Instruction: {}\n".format(IFUnit[0]))
    f.writelines("\tExecuted Instruction: {}\n".format(IFUnit[1]))
    f.writelines("Pre-Issue Queue:\n")
    if len(PreIssueQueue) == 0:
        f.writelines("\tEntry 0:\n")
        f.writelines("\tEntry 1:\n")
        f.writelines("\tEntry 2:\n")
        f.writelines("\tEntry 3:\n")
    if len(PreIssueQueue) == 1:
        f.writelines("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        f.writelines("\tEntry 1:\n")
        f.writelines("\tEntry 2:\n")
        f.writelines("\tEntry 3:\n")
    if len(PreIssueQueue) == 2:
        f.writelines("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        f.writelines("\tEntry 1: {}\n".format(PreIssueQueue[1]))
        f.writelines("\tEntry 2:\n")
        f.writelines("\tEntry 3:\n")
    if len(PreIssueQueue) == 3:
        f.writelines("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        f.writelines("\tEntry 1: {}\n".format(PreIssueQueue[1]))
        f.writelines("\tEntry 2: {}\n".format(PreIssueQueue[2]))
        f.writelines("\tEntry 3:\n")
    if len(PreIssueQueue) == 4:
        f.writelines("\tEntry 0: {}\n".format(PreIssueQueue[0]))
        f.writelines("\tEntry 1: {}\n".format(PreIssueQueue[1]))
        f.writelines("\tEntry 2: {}\n".format(PreIssueQueue[2]))
        f.writelines("\tEntry 3: {}\n".format(PreIssueQueue[3]))
    f.writelines("Pre-ALU1 Queue:\n")
    f.writelines("\tEntry 0: {}\n".format(PreALU1Queue[0]))
    f.writelines("\tEntry 1: {}\n".format(PreALU1Queue[1]))
    f.writelines("Pre-MEM Queue: {}\n".format(PreMEMQueue[0]))
    f.writelines("Post-MEM Queue: {}\n".format(PostMEMQueue[0]))
    f.writelines("Pre-ALU2 Queue:\n")
    f.writelines("\tEntry 0: {}\n".format(PreALU2Queue[0]))
    f.writelines("\tEntry 1: {}\n".format(PreALU2Queue[1]))
    f.writelines("Post-ALU2 Queue: {}\n\n".format(PostALU2Queue[0]))
    f.writelines("Registers\n")
    f.writelines("R00:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[0], REGISTERS[1],
                                                                 REGISTERS[2], REGISTERS[3],
                                                                 REGISTERS[4], REGISTERS[5],
                                                                 REGISTERS[6], REGISTERS[7]))
    f.writelines("R08:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[8], REGISTERS[9],
                                                                 REGISTERS[10], REGISTERS[11],
                                                                 REGISTERS[12], REGISTERS[13],
                                                                 REGISTERS[14], REGISTERS[15]))
    f.writelines("R16:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[16], REGISTERS[17],
                                                                 REGISTERS[18], REGISTERS[19],
                                                                 REGISTERS[20], REGISTERS[21],
                                                                 REGISTERS[22], REGISTERS[23]))
    f.writelines("R24:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(REGISTERS[24], REGISTERS[25],
                                                                 REGISTERS[26], REGISTERS[27],
                                                                 REGISTERS[28], REGISTERS[29],
                                                                 REGISTERS[30], REGISTERS[31]))
    f.writelines("\nData\n")
    f.writelines("300:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[11], MEMORY[12],
                                                                 MEMORY[13], MEMORY[14],
                                                                 MEMORY[15], MEMORY[16],
                                                                 MEMORY[17], MEMORY[18]) +
                 "332:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[19], MEMORY[20],
                                                                 MEMORY[21], MEMORY[22],
                                                                 MEMORY[23], MEMORY[24],
                                                                 MEMORY[25], MEMORY[26]))


def IFetch(Occupied):
    global PC
    global WaitSignal
    global ExecuteSignal
    global flag4break
    for j in range(2):
        i = int((PC - 256) / 4)
        command = MEMORY[i]
        OP = CodeWithOP[command]
        flag = False  # 是否修改PC值
        flag1 = False  # 跳转
        if IFUnit[0] == "":
            if Occupied < 4:
                if OP == "J" or OP == "JR" or OP == "BREAK" or OP == "BEQ" or OP == "BGTZ" or OP == "BLTZ":
                    if flag4break:
                        break
                    if CheckRegState(command):
                        if IFUnit[1] == "":
                            if OP == "BREAK":
                                flag4break = True
                            IFUnit[1] = command
                            Operation(command)
                            Occupied += 1
                            ExecuteSignal = True
                            flag1 = True
                        else:
                            IFUnit[0] = command
                            flag = True
                            Occupied += 1
                            WaitSignal = True
                    else:
                        IFUnit[0] = command
                        flag = True
                        Occupied += 1
                        WaitSignal = True
                else:
                    PreIssueQueue.append(command)
                    Occupied += 1
                    flag = True
        else:
            command = IFUnit[0]
            if CheckRegState(command):
                if WARSignal:
                    WaitSignal = False
                    return
                IFUnit[1] = IFUnit[0]
                Operation(command)
                IFUnit[0] = ""
                ExecuteSignal = True
                break
        if flag and not flag1:
            PC += 4


def Issue():
    n1 = 0
    n2 = 0
    global ExecuteSignal
    Occupied = 0
    if ExecuteSignal and IFUnit[1] != "":
        IFUnit[1] = ""
        ExecuteSignal = False
    Occupied = len(PreIssueQueue)  # 记录上个状态的PreIssue的占用情况

    for i in range(len(PreIssueQueue)):
        if PreIssueQueue[i] is not None:
            command = PreIssueQueue[i]
            OP = CodeWithOP[command]

            if OP == "LW":
                if CheckRegState(command) and not IsRAW(command) and not IsWAR(command):
                    ModifyRegState(command)
                    PreIssueQueue.remove(command)
                    EnQueue(PreALU1Queue, 2, command)
                    n1 += 1
                    break
            elif OP == "SW":
                if CheckRegState(command) and not IsRAW(command):
                    ModifyRegState(command)
                    PreIssueQueue.remove(command)
                    EnQueue(PreALU1Queue, 2, command)
                    n1 += 1
                    break
            else:
                if CheckRegState(command) and not IsRAW(command) and not IsWAR(command):
                    ModifyRegState(command)
                    PreIssueQueue.remove(command)
                    EnQueue(PreALU2Queue, 2, command)
                    n2 += 1
                    break
            if n1 + n2 > 2:
                break

    return Occupied


def Execute():
    if PreALU1Queue[0] != "" and IsEmpty(PreMEMQueue, 1):
        command = PreALU1Queue[0]
        EnQueue(PreMEMQueue, 1, command)
        DeQueue(PreALU1Queue, 2)
    if PreALU2Queue[0] != "" and IsEmpty(PostALU2Queue, 1):
        command = PreALU2Queue[0]
        EnQueue(PostALU2Queue, 1, command)
        DeQueue(PreALU2Queue, 2)


def MemOperate():
    if PreMEMQueue[0] != "" and IsEmpty(PostMEMQueue, 1):
        command = PreMEMQueue[0]
        EnQueue(PostMEMQueue, 1, command)
        DeQueue(PreMEMQueue, 1)
        OP = CodeWithOP[command]
        if OP == "SW":
            Operation(command)
            DeQueue(PostMEMQueue, 1)
            TempList1.append(command)


def WriteBack():
    flag = True
    flag1 = True
    if PostALU2Queue[0] != "":
        command = PostALU2Queue[0]
        Operation(command)
        TempList.append(command)
        DeQueue(PostALU2Queue, 1)

    if PostMEMQueue[0] != "":
        command = PostMEMQueue[0]
        Operation(command)
        TempList1.append(command)
        DeQueue(PostMEMQueue, 1)


def ListRegState(code):  # 检查要访问的寄存器位置
    ls = CodeWithData[code]
    OP = CodeWithOP[code]
    if OP in R_type:
        if OP == "SLL" or OP == "SRL" or OP == "SRA" or OP == "NOP":
            rt = ls[0]
            rd = ls[1]
            return {"R": [rt], "W": rd}

        elif OP == "JR":  # PC <- rs
            rs = ls[0]
            return rs
        else:
            rs = ls[0]
            rt = ls[1]
            rd = ls[2]
            return {"R": [rs, rt], "W": rd}

    if OP in I_type:
        rs = ls[0]
        rt = ls[1]

        if OP == "BLTZ" or OP == "BGTZ":
            return {"R": [rs], "W": None}
        elif OP == "SW":
            return {"R": [rs, rt], "W": None}
        else:
            return {"R": [rs], "W": rt}
    return None


def IsRAW(command):
    i = PreIssueQueue.index(command)
    if i == 0:
        return False

    ToVisitReg = ListRegState(command)
    if ToVisitReg is not None:
        ToWrite = ToVisitReg["W"]  # 当前指令要写的寄存器
        ToRead = ToVisitReg["R"]  # 当前指令要访问的寄存器
    else:
        return False

    for j in range(i):
        code = PreIssueQueue[j]
        ToVisitReg1 = ListRegState(code)
        if ToVisitReg1 is None:
            continue
        ToWrite1 = ToVisitReg1["W"]  # 当前指令之前的指令要写的寄存器
        if ToWrite1 is None:
            continue
        if ToWrite1 in ToRead:  # 若之前指令要写的寄存器在当前指令要读的寄存器的list里
            return True

    return False


def IsWAR(command):
    i = PreIssueQueue.index(command)
    if i == 0:
        return False

    ToVisitReg = ListRegState(command)
    if ToVisitReg is not None:
        ToWrite = ToVisitReg["W"]  # 当前指令要写的寄存器
        ToRead = ToVisitReg["R"]  # 当前指令要访问的寄存器
    else:
        return False

    for j in range(i):
        code = PreIssueQueue[j]
        ToVisitReg1 = ListRegState(code)
        if ToVisitReg1 is None:
            continue
        ToRead1 = ToVisitReg1["R"]  # 当前指令之前的指令要写的寄存器
        if ToRead1 is None:
            continue
        if ToWrite in ToRead1:  # 若之前指令要写的寄存器在当前指令要读的寄存器的list里
            return True

    return False


def CheckRegState(code, WhetherReturn=False):  # 检查要访问的寄存器位置
    ls = CodeWithData[code]

    OP = CodeWithOP[code]
    if OP in R_type:
        if OP == "SLL" or OP == "SRL" or OP == "SRA" or OP == "NOP":
            rt = ls[0]
            rd = ls[1]
            if RegState[rt] != "" or RegState[rd] != "":
                return False

        elif OP == "JR":  # PC <- rs
            rs = ls[0]
            if RegState[rs] != "":
                return False
        else:
            rs = ls[0]
            rt = ls[1]
            rd = ls[2]
            if RegState[rs] != "" or RegState[rt] != "" or RegState[rd] != "":
                return False

    if OP in I_type:
        rs = ls[0]
        rt = ls[1]

        if OP == "BLTZ" or OP == "BGTZ":
            if RegState[rs] != "":
                return False
        else:
            if RegState[rs] != "" or RegState[rt] != "":
                return False

    return True


def ModifyRegState(code):  # 修改寄存器状态
    ls = CodeWithData[code]
    OP = CodeWithOP[code]
    if OP in R_type:
        if OP == "SLL" or OP == "SRL" or OP == "SRA" or OP == "NOP":
            rt = ls[0]
            rd = ls[1]
            if RegState[rd] == "":
                RegState[rd] = OP

        elif OP == "JR":  # PC <- rs
            rs = ls[0]
            if RegState[rs] == "":
                RegState[rs] = OP

        else:
            rs = ls[0]
            rt = ls[1]
            rd = ls[2]
            if RegState[rd] == "":
                RegState[rd] = OP

    if OP in I_type:
        rs = ls[0]
        rt = ls[1]

        if OP != "BLTZ" or OP != "BGTZ":
            if RegState[rt] == "":
                RegState[rt] = OP


def ResetRegState(code):
    ls = CodeWithData[code]
    OP = CodeWithOP[code]
    if OP in R_type:
        if OP == "SLL" or OP == "SRL" or OP == "SRA" or OP == "NOP":
            rt = ls[0]
            rd = ls[1]
            if RegState[rd] != "":
                RegState[rd] = ""

        elif OP == "JR":  # PC <- rs
            rs = ls[0]
            if RegState[rs] != "":
                RegState[rs] = ""

        else:
            rs = ls[0]
            rt = ls[1]
            rd = ls[2]
            if RegState[rd] != "":
                RegState[rd] = ""

    if OP in I_type:
        rs = ls[0]
        rt = ls[1]

        if OP != "BLTZ" or OP != "BGTZ":
            if RegState[rt] != "":
                RegState[rt] = ""


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

        CodeWithData["[{}]".format(AssemblyCode)] = ls
        CodeWithOP["[{}]".format(AssemblyCode)] = OP
        return "[{}]".format(AssemblyCode)

    else:  # 读取到数据
        value = ComToDec(MachineCode)
        AssemblyCode = "{}".format(value)
        return AssemblyCode


def Operation(AssemblyCode):
    global PC
    OP = CodeWithOP[AssemblyCode]
    ls = CodeWithData[AssemblyCode]
    if OP == "SLL" or OP == "NOP":  # SLL R16, R1, #2
        rt = ls[0]
        rd = ls[1]
        sa = ls[2]
        REGISTERS[rd] = REGISTERS[rt] * (2 ** int(sa))
    if OP == "SRL" or OP == "SRA":
        rt = ls[0]
        rd = ls[1]
        sa = ls[2]
        REGISTERS[rd] = REGISTERS[rt] / (2 ** int(sa))  # rd <- rt >> sa
    if OP == "JR":
        rs = ls[0]
        PC = REGISTERS[rs]
    if OP == "SLT":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        if int(REGISTERS[rs]) < int(REGISTERS[rt]):
            REGISTERS[rd] = 1
        else:
            REGISTERS[rd] = 0
    if OP == "ADD":  # rd <- rs + rt
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = int(REGISTERS[rs]) + int(REGISTERS[rt])
    if OP == "SUB":  # rd <- rs - rt
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = int(REGISTERS[rs]) - int(REGISTERS[rt])
    if OP == "MUL":
        rs = ls[0]
        rt = ls[1]
        rd = ls[2]
        REGISTERS[rd] = int(REGISTERS[rs]) * int(REGISTERS[rt])
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
        if int(REGISTERS[rs]) == int(REGISTERS[rt]):
            PC += int(imm_value) * 4
    if OP == "BLTZ":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        if REGISTERS[rs] < 0:
            PC += imm_value * 4 + 4
    if OP == "BGTZ":
        rs = ls[0]
        rt = ls[1]
        imm_value = ls[2]
        if REGISTERS[rs] > 0:
            PC += imm_value * 4 + 4
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
        REGISTERS[rt] = int(MEMORY[int((addr - 256) / 4)])
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
        PC = addr * 4


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
    Simulation()

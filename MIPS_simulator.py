import sys
MIPS = {16: "J", 17: "JR", 18: "BEQ", 19: "BLTZ", 20: "BGTZ", 21: "BREAK",
        22: "SW", 23: "LW", 24: "SLL", 25: "SRL", 26: "SRA", 27: "NOP",
        48: "ADD", 49: "SUB", 50: "MUL", 51: "AND", 52: "OR", 53: "XOR",
        54: "NOR", 55: "SLT", 56: "ADDI", 57: "ANDI", 58: "ORI", 59: "XORI"}

I_type = ["ADDI", "ANDI", "ORI", "XORI", "BEQ", "BLTZ", "BGTZ", "SW", "LW"]
R_type = ["ADD", "SUB", "MUL", "AND", "OR", "XOR", "NOR", "SLT", "JR", "SLL", "SRL",
          "SRA", "NOP"]
J_type = ["J"]

REGISTERS = [0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0]
MEMORY = []
PC = 256


def readfile2memory(file_path):  # 将机器码文件读入到Memory中
    with open("{}".format(file_path), 'r') as f:
        for line in f:
            if line.endswith("\n"):
                line = line.replace("\n", "")
            if line.endswith("\r\n"):
                line = line.replace("\r\n", "")
            MEMORY.append(line)

    return MEMORY


def command2file(memory, pc):  # 将汇编代码写入到 disassembly.txt
    with open("./disassembly.txt", 'w') as f:
        for machine_code in memory:
            op = int(machine_code[:6], 2)
            assembly_code, pc = disassembly(machine_code, op, pc)
            line = "{}\t{}\t{}".format(machine_code, pc, assembly_code)
            pc += 4
            f.write(line + '\n')


def simulator(memory, pc):  # 将代码执行情况写入到 simulation.txt
    with open("./simulation.txt", 'w') as f:
        addr = int((pc - 256) / 4)
        machine_command = memory[addr]
        op = int(machine_command[:6], 2)
        cycle = 1
        while op != 21:
            assembly_code, pc1 = disassembly(machine_command, op, pc, False)
            print_func(cycle, pc, assembly_code, f)
            if pc1 == pc:  # 未发生跳转
                pc += 4
            else:  # 发生了跳转
                pc = pc1
            addr = int(pc % 256 / 4)
            machine_command = memory[addr]
            op = int(machine_command[:6], 2)
            cycle += 1

        assembly_code, pc1 = disassembly(machine_command, op, pc, False)
        print_func(cycle, pc, assembly_code, f)


def print_func(cycle, pc, assembly_code, f):
    """
    :param cycle:
    :param pc:
    :param assembly_code:
    :param f: 写入simulation.txt
    :return:
    """
    f.writelines("--------------------\n")
    f.writelines("Cycle:{}\t{}\t{}".format(cycle, pc, assembly_code))
    f.writelines("\n")
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
    f.writelines("340:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[21], MEMORY[22],
                                                                 MEMORY[23], MEMORY[24],
                                                                 MEMORY[25], MEMORY[26],
                                                                 MEMORY[27], MEMORY[28]) +
                 "372:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[29], MEMORY[30],
                                                                 MEMORY[31], MEMORY[32],
                                                                 MEMORY[33], MEMORY[34],
                                                                 MEMORY[35], MEMORY[36]) +
                 "404:\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(MEMORY[37], MEMORY[38],
                                                                 MEMORY[39], MEMORY[40],
                                                                 MEMORY[41], MEMORY[42],
                                                                 MEMORY[43], MEMORY[44]))
    f.writelines("\n")


def disassembly(machine_code, op, pc, readonly=True):  # 反汇编函数
    """

    :param machine_code: 机器码
    :param op: 操作码
    :param pc: 程序计数器的值
    :param readonly: 若为真，只进行反汇编，不对内存或寄存器进行操作
    :return:
    """
    if 16 <= op <= 59:  # 读取到的是指令
        OP = MIPS[op]
        if OP in R_type:
            if OP == "SLL" or OP == "SRL" or OP == "SRA" or OP == "NOP":
                rt = int(machine_code[11:16], 2)
                rd = int(machine_code[16:21], 2)
                sa = int(machine_code[21:26], 2)
                if not readonly:
                    if OP == "SLL" or OP == "NOP":  # rd <- rt << sa
                        REGISTERS[rd] = REGISTERS[rt] * (2 ** sa)
                    if OP == "SRL" or OP == "SRA":
                        REGISTERS[rd] = REGISTERS[rt] / (2 ** sa)  # rd <- rt >> sa

                assembly_code = "{} R{}, R{}, #{}".format(OP, rd, rt, sa)
            elif OP == "JR":  # PC <- rs
                if not readonly:
                    rs = int(machine_code[11:16], 2)
                    pc = REGISTERS[rs]
                assembly_code = "{} R{}".format(OP, rs)
            elif OP == "SLT":  # rd <- (rs < rt)
                rs = com2dec(machine_code[6:11])
                rt = com2dec(machine_code[11:16])
                rd = com2dec(machine_code[16:21])
                if not readonly:
                    if rs < rt:
                        REGISTERS[rd] = 1
                    else:
                        REGISTERS[rd] = 0
                assembly_code = "{} R{}, R{}, R{}".format(OP, rd, rs, rt)
            else:
                rs = int(machine_code[6:11], 2)
                rt = int(machine_code[11:16], 2)
                rd = int(machine_code[16:21], 2)
                if not readonly:
                    if OP == "ADD":  # rd <- rs + rt
                        REGISTERS[rd] = REGISTERS[rs] + REGISTERS[rt]
                    if OP == "SUB":  # rd <- rs - rt
                        REGISTERS[rd] = REGISTERS[rs] - REGISTERS[rt]
                    if OP == "MUL":
                        REGISTERS[rd] = REGISTERS[rs] * REGISTERS[rt]
                    if OP == "AND":
                        REGISTERS[rd] = REGISTERS[rs] and REGISTERS[rt]
                    if OP == "OR":
                        REGISTERS[rd] = REGISTERS[rs] or REGISTERS[rt]
                    if OP == "XOR":
                        REGISTERS[rd] = REGISTERS[rs] ^ REGISTERS[rt]
                    if OP == "NOR":
                        REGISTERS[rd] = not (REGISTERS[rs] or REGISTERS[rt])
                assembly_code = "{} R{}, R{}, R{}".format(OP, rd, rs, rt)

        if OP in I_type:
            rs = int(machine_code[6:11], 2)
            rt = int(machine_code[11:16], 2)
            imm = machine_code[16:]
            imm_value = com2dec(imm)
            if OP == "BEQ":
                if not readonly:
                    if REGISTERS[rs] == REGISTERS[rt]:
                        pc += imm_value * 4 + 4
                assembly_code = "{} R{}, R{}, #{}".format(OP, rs, rt, imm_value * 4)
            if OP == "BLTZ":
                if not readonly:
                    if REGISTERS[rs] < 0:
                        pc += imm_value * 4 + 4
                assembly_code = "{} R{}, #{}".format(OP, rs, imm_value * 4)
            if OP == "BGTZ":
                if not readonly:
                    if REGISTERS[rs] > 0:
                        pc += imm_value * 4 + 4
                assembly_code = "{} R{}, #{}".format(OP, rs, imm_value * 4)
            if OP == "SW":
                if not readonly:
                    base = REGISTERS[rs]
                    addr = base + imm_value
                    MEMORY[int((addr - 256) / 4)] = REGISTERS[rt]
                assembly_code = "{} R{}, {}(R{})".format(OP, rt, imm_value, rs)
            if OP == "LW":
                if not readonly:
                    base = REGISTERS[rs]
                    addr = base + imm_value
                    REGISTERS[rt] = MEMORY[int((addr - 256) / 4)]
                assembly_code = "{} R{}, {}(R{})".format(OP, rt, imm_value, rs)
            if OP == "ADDI":
                if not readonly:
                    REGISTERS[rt] = REGISTERS[rs] + imm_value
                assembly_code = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)
            if OP == "ANDI":
                if not readonly:
                    REGISTERS[rt] = REGISTERS[rs] and imm_value
                assembly_code = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)
            if OP == "ORI":
                if not readonly:
                    REGISTERS[rt] = REGISTERS[rs] or imm_value
                assembly_code = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)
            if OP == "XORI":
                if not readonly:
                    REGISTERS[rt] = REGISTERS[rs] ^ imm_value
                assembly_code = "{} R{}, R{}, #{}".format(OP, rt, rs, imm_value)

        if OP in J_type:
            addr = int(machine_code[6:], 2)
            if not readonly:
                pc = addr * 4
            assembly_code = "{} #{}".format(OP, addr * 4)

        if OP == "BREAK":
            assembly_code = "{}".format(OP)

    else:  # 读取到数据
        value = com2dec(machine_code)
        MEMORY[int((pc - 256) / 4)] = value  # 将真值替换内存中的机器码
        assembly_code = "{}".format(value)

    return assembly_code, pc


def com2dec(com_str):  # 补码求真值
    if com_str[0] == '0':
        dec_value = int(com_str[1:], 2)
    else:
        ori_str = ""
        for i in com_str:
            if i == "0":
                ori_str += "1"
            else:
                ori_str += "0"
        dec_value = - (int(ori_str[1:], 2) + 1)

    return dec_value


if __name__ == '__main__':
    file_name = sys.argv[1]
    file_path = './' + file_name  # 输入sample.txt
    MEMORY = readfile2memory(file_path)
    command2file(MEMORY, PC)  # 生成 disassembly.txt
    simulator(MEMORY, PC)  # 生成 simulation.txt

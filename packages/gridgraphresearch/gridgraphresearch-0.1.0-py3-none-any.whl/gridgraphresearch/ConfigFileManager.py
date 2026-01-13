# -*- coding: utf-8 -*-
"""
Power System Configuration File Parser
电力系统配置文件解析器
"""


def read_control_info_LFL0(file_path):
    """
    读取电力系统控制信息文件 LF.L0 并解析数据

    参数:
        file_path (str): 文件路径

    返回:
        dict: 包含所有字段及其对应值的字典

    """
    # 定义字段名称
    line1_fields = [
        'NBB', 'NLL', 'NTT', 'NDC', 'NGG', 'NLOAD',
        'Narea', 'NUD', 'NEQ', 'NSS', 'NFACT'
    ]

    line2_fields = [
        'SB', 'Vmax', 'Vmin', 'Eps', 'Meth', 'Iter',
        'Area', 'UD', 'Meq', 'ISS', 'NUP', 'Ctrl_RmXm', 'Ctrl_Matitf'
    ]

    data = {}

    with open(file_path, 'r') as f:
        # 处理第一行（整型数据）
        line1 = f.readline().strip()
        values = [v.strip() for v in line1.split(',') if v.strip()]

        # 校验字段数量
        if len(values) != len(line1_fields):
            raise ValueError("第一行字段数量不匹配，期望 {} 个，实际 {} 个".format(
                len(line1_fields), len(values)))

        # 转换并存储数据
        for field, value in zip(line1_fields, values):
            data[field] = int(value)

        # 处理第二行（混合类型）
        line2 = f.readline().strip()
        values = [v.strip() for v in line2.split(',') if v.strip()]

        # 校验字段数量
        if len(values) != len(line2_fields):
            raise ValueError("第二行字段数量不匹配，期望 {} 个，实际 {} 个".format(
                len(line2_fields), len(values)))

        # 处理前4个浮点型字段
        for i in range(4):
            data[line2_fields[i]] = float(values[i])

        # 处理后续整型字段（从第4个索引开始）
        for i in range(4, len(line2_fields)):
            data[line2_fields[i]] = int(values[i])

    return data


def parse_bus_data_LFL1(file_path):
    """
    解析母线数据文件 LF.L1
    格式：'Bus-Name',Vbase,Area,Vmax,Vmin,CB1,CB3
    """
    bus_list = []
    fields = [
        ('Bus-Name', str),
        ('Vbase', float),
        ('Area', int),
        ('Vmax', float),
        ('Vmin', float),
        ('CB1', float),
        ('CB3', float),
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # 清洗数据并去除首尾引号
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()][:len(fields)]
            if len(parts) != len(fields):
                raise ValueError(f"LF.L1 第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            bus = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    bus[field] = dtype(value) if dtype != str else value
                # 添加行号到当前bus字典
                bus['Line_Number'] = line_num
            except ValueError as e:
                raise ValueError(f"LF.L1 第{line_num}行数据类型错误: {e}")

            bus_list.append(bus)

    return bus_list


def parse_ac_line_data_LFL2(file_path):
    """
    解析交流线数据文件 LF.L2
    格式：Mark, I_Name, J_name, No., R, X, B/2, F/T, Type, PL, CB, CL, VQP, LIM, name_ctrl, type_ctrl, IDName
    """
    line_list = []
    fields = [
        ("Mark", int),
        ("I_Name", int),
        ("J_name", int),
        ("No", int),
        ("R", float),
        ("X", float),
        ("B_half", float),
        ("F_T", int),
        ("Type", int),
        ("PL", int),
        ("CB", int),
        ("CL", int),
        ("VQP", float),
        ("LIM", float),
        ('LC', float),
        ("name_ctrl", str),
        ("type_ctrl", int),
        ("IDName", str),
    ]

    with open(file_path, "r", encoding='utf8') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(",") if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(f"LF.L2 第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            line_data = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    line_data[field] = dtype(value) if dtype != str else value
                line_data["Line_Number"] = line_num
            except ValueError as e:
                raise ValueError(f"LF.L2 第{line_num}行数据类型错误: {e}")

            line_list.append(line_data)

    return line_list


def parse_transformer_data_LFL3(file_path):
    """
    解析变压器数据文件 LF.L3
    """
    transformer_list = []
    fields = [
        ("Mark", int),
        ("I_Name", int),
        ("J_name", int),
        ("No", int),
        ("R", float),
        ("X", float),
        ("Tk", float),
        ("Rm", float),
        ("Xm", float),
        ("F_T", int),
        ("Type", int),
        ("PL", int),
        ("TP", float),
        ("CB", int),
        ("CL", int),
        ("VQP", float),
        ("Theta", float),
        ("LIM", float),
        ('TC', float),
        ("ID", int),
        ("J", int),
        ("TrsType", int),
        ("name_ctrl", str),
        ("type_ctrl", int),
        ("IDName", str),
    ]

    with open(file_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(",") if p.strip()][:len(fields)]
            if len(parts) != len(fields):
                raise ValueError(f"LF.L3 第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            transformer = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    transformer[field] = dtype(value) if dtype != str else value
                transformer["Line_Number"] = line_num
            except ValueError as e:
                raise ValueError(f"LF.L3 第{line_num}行数据类型错误: {e}")

            transformer_list.append(transformer)

    return transformer_list


def parse_generator_data_LFL5(file_path):
    """解析发电机数据文件LF.L5"""
    generators = []
    fields = [
        ('Mark', int), ('Bus_Name', int), ('Type', int),
        ('Pg', float), ('Qg', float), ('V0', float),
        ('theta', float), ('Qmax', float), ('Qmin', float),
        ('Pmax', float), ('Pmin', float), ('PL', int),
        ('CB', int), ('CL', int), ('VQP', float),
        ('K%', float), ('name_ctrl', str),
        ('type_ctrl', int), ('IDName', str)
    ]

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]

            if len(parts) != len(fields):
                raise ValueError(f"发电机数据第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            gen = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    gen[field] = dtype(value) if dtype != str else value
                    gen['Line_Number'] = line_num
                generators.append(gen)
            except ValueError as e:
                raise ValueError(f"发电机数据第{line_num}行解析错误: {str(e)}")

    return generators


def parse_load_data_LFL6(file_path):
    """解析负荷数据文件"""
    loads = []
    fields = [
        ('Mark', int), ('Bus_Name', int), ('No.', int),
        ('Type', float), ('Pl', float), ('Ql', float),
        ('V0', float), ('θ', float), ('Qmax', float),
        ('Qmin', float), ('Pmax', float), ('Pmin', int),
        ('PL', int), ('CB', int), ('CL', int),
        ('VQP', float), ('name_ctrl', str),
        ('type_ctrl', int), ('IDName', str)
    ]

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]

            if len(parts) != len(fields):
                raise ValueError(f"负荷数据第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            load = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    load[field] = dtype(value) if dtype != str else value
                    load['Line_Number'] = line_num
                loads.append(load)
            except ValueError as e:
                raise ValueError(f"负荷数据第{line_num}行解析错误: {str(e)}")

    return loads


def parse_area_power_data_LFL7(file_path):
    """解析区域功率交换数据"""
    areas = []
    fields = [
        ('Mark', int), ('No.', int), ('Area_Name', str),
        ('Adj_G', int), ('Schedule', float),
        ('Tole', float), ('Pmax', float)
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]

            if len(parts) != len(fields):
                raise ValueError(f"区域数据第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            area = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    area[field] = dtype(value) if dtype != str else value
                    area['Line_Number'] = line_num
                areas.append(area)
            except ValueError as e:
                raise ValueError(f"区域数据第{line_num}行解析错误: {str(e)}")

    return areas


def parse_ud_data_LFL9(file_path):
    """解析用户自定义模型数据"""
    ud_records = []
    fields = [
        ('M', int), ('XX', int), ('L', int),
        ('B1', int), ('X0', float), ('Y0', float),
        ('Z0', float), ('I', int), ('J', int),
        ('No.', int), ('IJType', int), ('B2', int),
        ('B3', int), ('B4', int)
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]

            if len(parts) != len(fields):
                raise ValueError(f"UD数据第{line_num}行字段数量错误，期望 {len(fields)} 个，实际 {len(parts)} 个")

            record = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    if field in ['ID1', 'ID2', 'ID3', 'ID4']:
                        record[field] = -abs(int(value))
                    else:
                        record[field] = dtype(value) if dtype != str else value

                record['Line_Number'] = line_num
                ud_records.append(record)
            except ValueError as e:
                raise ValueError(f"UD数据第{line_num}行解析错误: {str(e)}")

    return ud_records


def parse_dc_line_data_LFNL4(file_path):
    """
    解析直流线数据文件 LF.NL4（每个元件占8行）
    """
    dc_list = []
    fields = [
        ("Mark", int), ("I_Name", int), ("J_name", int),
        ("No", int), ("F_T", int), ("dcname", str),
        ("Rpi", float), ("Lpi", float), ("Rpj", float),
        ("Lpj", float), ("Rl", float), ("Ll", float),
        ("Rei", float), ("Rej", float), ("Lsi", float), ("Lsj", float),
        ("Vdn", float),
        ("Vhi", float), ("Vli", float), ("Bi", int),
        ("Sti", float), ("Rti", float), ("Xti", float),
        ("Vtimax", float), ("Vtimin", float), ("Ntapi", float),
        ("R0i", float), ("X0i", float),
        ("Vhj", float), ("Vlj", float), ("Bj", int),
        ("Stj", float), ("Rtj", float), ("Xtj", float),
        ("Vtjmax", float), ("Vtjmin", float), ("Ntapj", float),
        ("R0j", float), ("X0j", float),
        ("OP", int), ("Qci", float), ("Qcj", float),
        ("Pd1", float), ("Vd1", float), ("A1min", float),
        ("A10", float), ("Gama1min", float), ("Gama10", float),
        ("Pd2", float), ("Vd2", float), ("A2min", float),
        ("A20", float), ("Gama2min", float), ("Gama20", float),
    ]

    with open(file_path, "r") as f:
        line_iter = enumerate(f, 1)
        while True:
            lines = []
            line_nums = []
            try:
                for _ in range(8):
                    line_num, line = next(line_iter)
                    lines.append(line.strip())
                    line_nums.append(line_num)
            except StopIteration:
                if lines:
                    raise ValueError(
                        f"LF.NL4 文件末尾存在不完整的直流线记录，起始行号 {line_nums[0]}，"
                        f"期望8行，实际读取{len(lines)}行"
                    )
                else:
                    break

            all_parts = []
            for idx, line in enumerate(lines):
                parts = [p.strip().strip("'") for p in line.split(",") if p.strip()]
                all_parts.extend(parts)
                if idx == 0 and len(parts) != 6:
                    raise ValueError(
                        f"LF.NL4 第{line_nums[0]}行（首行）字段数量错误，应为6，实际{len(parts)}"
                    )

            if len(all_parts) != len(fields):
                raise ValueError(
                    f"LF.NL4 行号 {line_nums[0]}-{line_nums[-1]} 字段总数错误，"
                    f"期望 {len(fields)}，实际 {len(all_parts)}"
                )

            dc_data = {}
            try:
                for (field, dtype), value in zip(fields, all_parts):
                    dc_data[field] = dtype(value) if dtype != str else value
                dc_data["Line_Start"] = line_nums[0]
            except ValueError as e:
                error_field = fields[len(dc_data)][0]
                raise ValueError(
                    f"LF.NL4 行号 {line_nums[0]}-{line_nums[-1]} 字段 '{error_field}' 格式错误：{str(e)}"
                )
            dc_data['Line_Number'] = line_num
            dc_list.append(dc_data)

    return dc_list


def parse_cal_data_LFCAL(file_path):
    """解析计算标识文件 LF.CAL"""
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
        if len(lines) != 4:
            raise ValueError(f"LF.CAL 文件行数错误，期望4行，实际{len(lines)}行")

    line1 = [p.strip().strip("'") for p in lines[0].split(',') if p.strip()]
    if len(line1) != 2:
        raise ValueError(f"LF.CAL 第1行字段数量错误，期望2个，实际{len(line1)}个")

    line2 = [p.strip().strip("'") for p in lines[1].split(',') if p.strip()]
    if len(line2) != 2:
        raise ValueError(f"LF.CAL 第2行字段数量错误，期望2个，实际{len(line2)}个")

    line3 = [p.strip().strip("'") for p in lines[2].split(',') if p.strip()]
    if len(line3) != 2:
        raise ValueError(f"LF.CAL 第3行字段数量错误，期望2个，实际{len(line3)}个")

    line4 = [p.strip().strip("'") for p in lines[3].split(',') if p.strip()]
    if len(line4) != 6:
        raise ValueError(f"LF.CAL 第4行字段数量错误，期望6个，实际{len(line4)}个")

    cal_data = {
        'Mcal': int(line1[0]),
        'ML23': int(line1[1]),
        'Date': line2[0],
        'Time': line2[1],
        'NUD': int(line3[0]),
        'NUP': int(line3[1]),
        'NBB': int(line4[0]),
        'NGG': int(line4[1]),
        'NLOAD': int(line4[2]),
        'NAC': int(line4[3]),
        'NDC': int(line4[4]),
        'Ntrans': int(line4[5]),
    }
    return cal_data


def parse_LFLP1_data(file_path):
    """解析母线结果文件 LF.LP1"""
    bus_results = []
    fields = [
        ('Bus', int),
        ('V', float),
        ('Theta', float),
        ('Busname', str)
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line_num == 1:
                continue
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(f"LF.LP1 第{line_num}行字段数量错误，期望{len(fields)}个，实际{len(parts)}个")

            result = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    result[field] = dtype(value) if dtype != str else value
                result['Line_Number'] = line_num
            except ValueError as e:
                raise ValueError(f"LF.LP1 第{line_num}行数据类型错误: {e}")

            bus_results.append(result)

    return bus_results


def parse_STCAL_data(file_path):
    """解析计算标识文件 ST.CAL"""
    result = {}
    fields_per_line = [
        [('Mcal', int)],
        [('Date', str), ('Time', str)],
        [('NUD', int), ('NUP', int)],
        [('NBB', int), ('NGG', int), ('NLOAD', int), ('NDC', int),
         ('NSVC', int), ('Nfault', int), ('Ndist', int)],
        [('Istable', int), ('Tstable', float), ('Ngroup', int)]
    ]

    with open(file_path, 'r') as f:
        lines = []
        for _ in range(5):
            line = f.readline()
            if not line:
                raise ValueError("ST.CAL 文件行数不足5行")
            lines.append(line.strip())

    for line_num, (line_content, expected_fields) in enumerate(zip(lines, fields_per_line), 1):
        parts = [p.strip().strip("'") for p in line_content.split(',') if p.strip()]

        if len(parts) != len(expected_fields):
            raise ValueError(
                f"ST.CAL 第{line_num}行字段数量错误，期望{len(expected_fields)}个，实际{len(parts)}个。"
                f"行内容：{line_content}"
            )

        for idx, (field_name, dtype) in enumerate(expected_fields):
            try:
                value = parts[idx]
                if dtype != str and value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                result[field_name] = dtype(value)
            except ValueError as e:
                raise ValueError(
                    f"ST.CAL 第{line_num}行字段 '{field_name}' 转换错误，值 '{value}'：{e}"
                )

    return result


def parse_fault_data_STS11(file_path):
    """解析故障设置文件 ST.S11"""
    bus_results = []
    fields = [
        ('Mark', int),
        ('I_Name', int),
        ('J_Name', int),
        ('No', int),
        ('K%', float),
        ('Add_Name', str),
        ('A', int),
        ('B', int),
        ('C', int),
        ('D', int),
        ('K', float),
        ('M', int),
        ('Ts', float),
        ('Te', float),
        ('R', float),
        ('QX', float),
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(f"ST.S11 第{line_num}行字段数量错误，期望{len(fields)}个，实际{len(parts)}个")

            result = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    result[field] = dtype(value) if dtype != str else value
                result['Line_Number'] = line_num
            except ValueError as e:
                raise ValueError(f"ST.S11 第{line_num}行数据类型错误: {e}")

            bus_results.append(result)

    return bus_results


def parse_LFLP2_data(file_path):
    """解析交流线结果文件 LF.LP2"""
    line_results = []
    fields = [
        ('I', int),
        ('J', int),
        ('No', int),
        ('Pi', float),
        ('Qi', float),
        ('Pj', float),
        ('Qj', float),
        ('Qci', float),
        ('Qcj', float),
        ('ACLinename', str)
    ]

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(f"LF.LP2 第{line_num}行字段数量错误，期望{len(fields)}个，实际{len(parts)}个")

            result = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    result[field] = dtype(value) if dtype != str else value
                result['Line_Number'] = line_num
            except ValueError as e:
                raise ValueError(f"LF.LP2 第{line_num}行数据类型错误: {e}")

            line_results.append(result)

    return line_results


def parse_LFLP3_data(file_path):
    """解析变压器结果文件 LF.LP3"""
    transformer_results = []
    fields = [
        ('I', int),
        ('J', int),
        ('No', int),
        ('Pi', float),
        ('Qi', float),
        ('Pj', float),
        ('Qj', float),
        ('Pm', float),
        ('Qm', float),
        ('Transname', str)
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip().strip("'") for p in line.strip().split(',') if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(f"LF.LP3 第{line_num}行字段数量错误，期望{len(fields)}个，实际{len(parts)}个")

            result = {}
            try:
                for (field, dtype), value in zip(fields, parts):
                    result[field] = dtype(value) if dtype != str else value
                result['Line_Number'] = line_num
            except ValueError as e:
                raise ValueError(f"LF.LP3 第{line_num}行数据类型错误: {e}")

            transformer_results.append(result)

    return transformer_results


def parse_STANADAT_data(file_path):
    """解析自动分析结果文件 STANA.DAT"""
    results = []
    fields = [
        ('T', float), ('Grp_No', int), ('GenAMax', int),
        ('GenAMin', int), ('Ang', float), ('BusVMin', int),
        ('Vmin', float), ('GenWMin', int), ('WMin', float),
        ('Var1', float), ('Var2', float), ('Var3', float),
        ('Var4', float), ('Var5', float), ('Var6', float),
        ('Var7', float), ('Var8', float),
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split(',') if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(
                    f"STANA.DAT 第{line_num}行字段错误，应有{len(fields)}个，实际{len(parts)}个\n"
                    f"行内容：{line}"
                )

            record = {'Line_Number': line_num}
            try:
                for (field, dtype), value in zip(fields, parts):
                    record[field] = dtype(value)
            except ValueError as e:
                raise ValueError(
                    f"STANA.DAT 第{line_num}行数据转换错误: {e}\n"
                    f"问题字段：{field} 值：{value}"
                )
            results.append(record)
    return results


def parse_STB12_data(file_path):
    """解析母线120电压数据文件 ST.B12"""
    results = []
    fields = [
        ('T', float), ('I', int),
        ('V1R', float), ('V1I', float),
        ('V2R', float), ('V2I', float),
        ('V0R', float), ('V0I', float)
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split(',') if p.strip()]
            if len(parts) != len(fields):
                raise ValueError(
                    f"ST.B12 第{line_num}行字段错误，应有{len(fields)}个，实际{len(parts)}个\n"
                    f"行内容：{line}"
                )

            record = {'Line_Number': line_num}
            try:
                for (field, dtype), value in zip(fields, parts):
                    record[field] = dtype(value)
            except ValueError as e:
                raise ValueError(
                    f"ST.B12 第{line_num}行数据转换错误: {e}\n"
                    f"问题字段：{field} 值：{value}"
                )
            results.append(record)
    return results


def parse_STR12_data(file_path):
    """解析线路120电流数据文件 ST.R12"""
    results = []
    fields = [
        ('T', float), ('I', int), ('J', int), ('No', int),
        ('I1R', float), ('I1I', float),
        ('I2R', float), ('I2I', float),
        ('I0R', float), ('I0I', float)
    ]

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            parts = []
            temp_parts = line.split(',')
            for i, p in enumerate(temp_parts):
                p = p.strip()
                if i == 3 and p.endswith('.'):
                    parts.append(p.rstrip('.').strip())
                else:
                    parts.append(p) if p else None

            if len(parts) != len(fields):
                raise ValueError(
                    f"ST.R12 第{line_num}行字段错误，应有{len(fields)}个，实际{len(parts)}个\n"
                    f"行内容：{line}"
                )

            record = {'Line_Number': line_num}
            try:
                for (field, dtype), value in zip(fields, parts):
                    record[field] = dtype(value)
            except ValueError as e:
                raise ValueError(
                    f"ST.R12 第{line_num}行数据转换错误: {e}\n"
                    f"问题字段：{field} 值：{value}"
                )
            results.append(record)
    return results


def parse_st_sme(file_path):
    """解析ST.SME文件，返回VAR_INF和ST_OUT表的数据"""
    var_inf = []
    st_out = []
    last_records = {}

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            parts = [p.strip() for p in line.strip().split(',')]
            while len(parts) < 19:
                parts.append('0')
            parts = parts[:19]

            try:
                mark = int(parts[0])
                iterm = int(parts[1])
            except ValueError as e:
                raise ValueError(f"Line {line_num}: Invalid Mark or Iterm. {e}")

            if iterm == 99:
                if mark not in last_records:
                    raise ValueError(f"Line {line_num}: Continuation line without previous record (Mark={mark})")
                last_info = last_records[mark]
                last_iterm = last_info['iterm']
                record = last_info['record']
                elements = parts[2:]
                _handle_continuation(last_iterm, record, elements, line_num)
                continue

            elements = parts[2:]
            if iterm in {1, 2, 3, 4, 5, 6, 7, 12}:
                record = _parse_var_inf(iterm, elements, line_num)
                record['Mark'] = mark
                var_inf.append(record)
                last_records[mark] = {'iterm': iterm, 'record': record}
            elif iterm in {8, 9, 10, 11}:
                record = _parse_st_out(iterm, elements, line_num)
                record['Mark'] = mark
                st_out.append(record)
                last_records[mark] = {'iterm': iterm, 'record': record}
            else:
                raise ValueError(f"Line {line_num}: Unknown Iterm value {iterm}")

    return {'VAR_INF': var_inf, 'ST_OUT': st_out}


def _parse_var_inf(iterm, elements, line_num):
    try:
        if iterm == 1:
            i_names = []
            j_names = []
            for i in range(0, 16, 2):
                i_names.append(int(elements[i]))
                j_names.append(int(elements[i + 1]))
            return {'Type': 1, 'I_name': i_names, 'J_Name': j_names, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm == 2:
            i_names = [int(elements[i]) for i in range(8)]
            return {'Type': 2, 'I_name': i_names, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm in (3, 5):
            i_name = int(elements[0])
            sub_types = [int(elements[i]) for i in range(1, 9)]
            return {'Type': iterm, 'I_name': i_name, 'sub_type': sub_types, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm == 4:
            i_name = int(elements[0])
            id_no = int(elements[1])
            sub_types = [int(elements[i]) for i in range(2, 10)]
            return {'Type': 4, 'I_name': i_name, 'id_no': id_no, 'sub_type': sub_types, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm in (6, 7):
            i_name = int(elements[0])
            j_name = int(elements[1])
            id_no = int(elements[2])
            sub_types = [int(elements[i]) for i in range(3, 11)]
            pairs = []
            for i in range(11, 19, 2):
                if i < len(elements):
                    pairs.append({'I': int(elements[i]), 'J': int(elements[i + 1])})
            return {'Type': iterm, 'I_name': i_name, 'J_name': j_name, 'id_no': id_no, 'sub_type': sub_types, 'pairs': pairs, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm == 12:
            return {'Type': 12, 'data': [int(elements[i]) for i in range(16)], 'Iterm': iterm, 'Line_Number': line_num}
        else:
            raise ValueError(f"Iterm {iterm} not implemented for VAR_INF")
    except IndexError as e:
        raise ValueError(f"Line {line_num}: Insufficient elements for Iterm {iterm}") from e
    except ValueError as e:
        raise ValueError(f"Line {line_num}: Invalid data format: {e}") from e


def _parse_st_out(iterm, elements, line_num):
    try:
        if iterm == 8:
            type_ks = [int(elements[i]) for i in range(4)]
            return {'Type_k': type_ks, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm == 9:
            buses = [int(elements[i]) for i in range(10)]
            return {'Buses': buses, 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm == 10:
            return {'FaultData': [int(elements[0]), int(elements[1])], 'Iterm': iterm, 'Line_Number': line_num}
        elif iterm == 11:
            return {'Steps': int(elements[0]), 'Iterm': iterm, 'Line_Number': line_num}
        else:
            raise ValueError(f"Iterm {iterm} not implemented for ST_OUT")
    except (IndexError, ValueError) as e:
        raise ValueError(f"Line {line_num}: Error parsing ST_OUT Iterm {iterm}: {e}") from e


def _handle_continuation(last_iterm, record, elements, line_num):
    try:
        if last_iterm == 1:
            for i in range(0, 16, 2):
                record['I_name'].append(int(elements[i]))
                record['J_Name'].append(int(elements[i + 1]))
        elif last_iterm == 2:
            for i in range(8):
                record['I_name'].append(int(elements[i]))
        elif last_iterm in (3, 5):
            for i in range(1, 9):
                record['sub_type'].append(int(elements[i]))
        elif last_iterm == 4:
            for i in range(2, 10):
                record['sub_type'].append(int(elements[i]))
        elif last_iterm in (6, 7):
            for i in range(3, 11):
                record['sub_type'].append(int(elements[i]))
            for i in range(11, 19, 2):
                record['pairs'].append({'I': int(elements[i]), 'J': int(elements[i + 1])})
        elif last_iterm == 12:
            record['data'].extend(int(e) for e in elements[:16])
        elif last_iterm in (8, 9, 10, 11):
            if last_iterm == 8:
                record['Type_k'].extend(int(e) for e in elements[:4])
            elif last_iterm == 9:
                record['Buses'].extend(int(e) for e in elements[:10])
        else:
            raise ValueError(f"Continuation for Iterm {last_iterm} not supported")
    except (IndexError, ValueError) as e:
        raise ValueError(f"Line {line_num}: Error in continuation line: {e}") from e

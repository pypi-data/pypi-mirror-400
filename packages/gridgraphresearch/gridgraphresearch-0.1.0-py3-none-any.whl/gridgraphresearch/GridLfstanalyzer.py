# -*- coding: utf-8 -*-
"""
Power System Load Flow and Transient Stability Analyzer
电力系统潮流计算与暂态稳定分析器
"""

import os
import pprint
import subprocess
import time
from typing import TextIO
from dataclasses import dataclass, asdict

from .ConfigFileManager import (
    read_control_info_LFL0,
    parse_bus_data_LFL1,
    parse_ac_line_data_LFL2,
    parse_transformer_data_LFL3,
    parse_generator_data_LFL5,
    parse_load_data_LFL6,
    parse_fault_data_STS11,
    parse_cal_data_LFCAL,
    parse_LFLP1_data,
    parse_LFLP2_data,
    parse_LFLP3_data,
    parse_STCAL_data,
    parse_STANADAT_data,
    parse_STB12_data,
    parse_STR12_data,
)


@dataclass
class FaultST11Config:
    """Fault configuration dataclass"""
    A: int
    B: int
    C: int
    D: int
    K: int
    M: int


class GridLFSTAnalyzer:
    """
    Power System Load Flow and Transient Stability Analyzer
    电力系统潮流计算与暂态稳定分析器
    """

    def __init__(self, file_path, cal_delay=7):
        """
        Initialize the analyzer with configuration files.

        Args:
            file_path: Directory path containing configuration files
            cal_delay: Calculation delay time in seconds (default: 7)
        """
        self.LFL1_name = 'LF.L1'
        self.LFL2_name = 'LF.L2'
        self.LFL3_name = 'LF.L3'
        self.LFL0_name = 'LF.L0'
        self.LFL5_name = 'LF.L5'
        self.LFL6_name = 'LF.L6'
        self.STS11_name = 'ST.S11'
        self.LFCAL_name = "LF.CAL"
        self.LFLP1_name = "LF.LP1"
        self.LFLP2_name = "LF.LP2"
        self.LFLP3_name = "LF.LP3"
        self.STB12_name = "ST.B12"
        self.STCAL_name = "ST.CAL"
        self.STR12_name = "ST.R12"
        self.STANADAT_name = "STANA.DAT"
        self.STANAGRPDAT_name = "STANAGRP.DAT"
        self.cal_delay = cal_delay

        self.file_path = file_path
        self.control_info = read_control_info_LFL0(os.path.join(file_path, self.LFL0_name)).copy()
        print("已经读取系统信息：")
        pprint.pprint(self.control_info, sort_dicts=False)
        self.bus_data_LFL1 = parse_bus_data_LFL1(os.path.join(file_path, self.LFL1_name)).copy()
        self.ac_line_data_LFL2 = parse_ac_line_data_LFL2(os.path.join(file_path, self.LFL2_name)).copy()
        self.transformer_data_LFL3 = parse_transformer_data_LFL3(os.path.join(file_path, self.LFL3_name)).copy()
        self.generator_data_LFL5 = parse_generator_data_LFL5(os.path.join(file_path, self.LFL5_name)).copy()
        self.load_data_LFL6 = parse_load_data_LFL6(os.path.join(file_path, self.LFL6_name)).copy()
        self.cal_data_LFCAL = None
        self.LFLP1_data = None
        self.LFLP2_data = None
        self.LFLP3_data = None
        self.STCAL_data = None
        self.STANADAT_data = None
        self.STB12_data = None
        self.STR12_data = None
        self.STS11_data = parse_fault_data_STS11(os.path.join(file_path, self.STS11_name)).copy()
        self.filter_available_item()

        # Fault type configurations
        self.fault_AG_key_info = FaultST11Config(A=1, B=0, C=0, D=1, K=0, M=0)
        self.fault_BG_key_info = FaultST11Config(A=0, B=1, C=0, D=1, K=0, M=0)
        self.fault_CG_key_info = FaultST11Config(A=0, B=0, C=1, D=1, K=0, M=0)
        self.fault_AB_key_info = FaultST11Config(A=1, B=1, C=0, D=0, K=1, M=0)
        self.fault_AC_key_info = FaultST11Config(A=1, B=0, C=1, D=0, K=1, M=0)
        self.fault_BC_key_info = FaultST11Config(A=0, B=1, C=1, D=0, K=1, M=0)
        self.fault_ABC_key_info = FaultST11Config(A=1, B=1, C=1, D=0, K=1, M=0)
        self.fault_ABG_key_info = FaultST11Config(A=1, B=1, C=0, D=1, K=1, M=0)
        self.fault_ACG_key_info = FaultST11Config(A=1, B=0, C=1, D=1, K=1, M=0)
        self.fault_BCG_key_info = FaultST11Config(A=0, B=1, C=1, D=1, K=1, M=0)
        self.fault_ABCG_key_info = FaultST11Config(A=1, B=1, C=1, D=1, K=1, M=0)

        self.graph_tools = GraphTools(self, init_make_graph=False)
        self.fault_key_map = {
            'AG': self.fault_AG_key_info,
            'BG': self.fault_BG_key_info,
            'CG': self.fault_CG_key_info,
            'AB': self.fault_AB_key_info,
            'AC': self.fault_AC_key_info,
            'BC': self.fault_BC_key_info,
            'ABG': self.fault_ABG_key_info,
            'ACG': self.fault_ACG_key_info,
            'BCG': self.fault_BCG_key_info,
            'ABCG': self.fault_ABCG_key_info,
        }

    def filter_available_item(self):
        """Filter available items based on Mark field"""
        self.ac_line_data_LFL2 = [x for x in self.ac_line_data_LFL2 if x['Mark'] == 1]
        self.transformer_data_LFL3 = [x for x in self.transformer_data_LFL3 if x['Mark'] == 1]
        self.generator_data_LFL5 = [x for x in self.generator_data_LFL5 if x['Mark'] == 1]
        self.load_data_LFL6 = [x for x in self.load_data_LFL6 if x['Mark'] == 1]
        self.bus_data_LFL1 = [x for x in self.bus_data_LFL1 if 'NULL' not in x['Bus-Name']]

    @staticmethod
    def find_by_IDName(name, data):
        """Find element by IDName"""
        res = [x for x in data if x['IDName'] == name][0]
        return res

    @staticmethod
    def find_by_line_number(line_number, data):
        """Find element by line number"""
        res = [x for x in data if str(x['Line_Number']) == str(line_number)]
        res = res[0] if res != [] else []
        return res

    @staticmethod
    def find_ac_line_by_ij_name(I_name, J_name, data_list: list):
        """Find AC line by I and J names"""
        res = []
        for data in data_list:
            data: dict
            if str(data['I_Name']) == str(I_name) and str(data['J_name']) == str(J_name):
                res.append(data.copy())
        return res

    def find_ac_line_by_bus_i_name(self, bus: dict):
        """Find AC line by bus I name"""
        I_name = bus['Line_Number']
        ac_line = list(filter(lambda x: str(x['I_Name']) == str(I_name), self.ac_line_data_LFL2))
        return ac_line

    def find_ac_line_by_bus_j_name(self, bus: dict):
        """Find AC line by bus J name"""
        J_name = bus['Line_Number']
        ac_line = list(filter(lambda x: str(x['J_name']) == str(J_name), self.ac_line_data_LFL2))
        return ac_line

    def find_2bus_by_ij_name(self, I_name, J_name):
        """Find two buses by I and J names"""
        bus_i = list(filter(lambda x: str(x['Line_Number']) == str(I_name), self.bus_data_LFL1))[0]
        bus_j = list(filter(lambda x: str(x['Line_Number']) == str(J_name), self.bus_data_LFL1))[0]
        return bus_i, bus_j

    def find_bus_by_generator(self, gen: dict):
        """Find bus by generator"""
        bus_name = gen['Bus_Name']
        bus_init = list(filter(lambda x: str(bus_name) == str(x['Line_Number']), self.bus_data_LFL1))[0]
        bus_name = bus_init['Bus-Name'].split('/')[0]
        bus = list(filter(lambda x: str(bus_name) in x['Bus-Name'] and '母线' in x['Bus-Name'], self.bus_data_LFL1))
        if bus:
            return bus
        else:
            return None

    @staticmethod
    def __file_line_write_processor(file: TextIO, line_number, new_content):
        str_content = list(map(str, list(new_content.values())))
        str_content[-1] = f"'{str_content[-1]}'"
        str_content[-3] = f"'{str_content[-3]}'"
        new_content = ",".join(str_content)
        lines = file.readlines()

        if line_number < 1:
            raise ValueError("行号必须从1开始。")
        if line_number > len(lines):
            raise IndexError(f"文件只有{len(lines)}行，无法覆盖第{line_number}行。")
        lines[line_number - 1] = new_content + '\n'
        file.seek(0)
        file.writelines(lines)
        file.truncate()

    def change_write_line(self, line_number, new_content, file_name):
        """Change a specific line in a configuration file"""
        file_path = os.path.join(self.file_path, file_name)
        try:
            with open(file_path, 'r+', encoding='utf-8') as file:
                self.__file_line_write_processor(file, line_number, new_content)
        except UnicodeError:
            with open(file_path, 'r') as file:
                self.__file_line_write_processor(file, line_number, new_content)

    def __write_data(self, file_name, data_dict: dict):
        data_line = int(data_dict['Line_Number'])
        del data_dict['Line_Number']
        self.change_write_line(data_line, data_dict, file_name)

    def change_bus_data_LFL1(self, data_dict):
        """Update bus data"""
        self.__write_data(self.LFL1_name, data_dict)
        self.bus_data_LFL1 = parse_bus_data_LFL1(os.path.join(self.file_path, self.LFL5_name)).copy()

    def change_line_data_LFL2(self, **kwargs):
        """Reserved interface for line data changes"""
        ...

    def change_transformer_data_LFL3(self, **kwargs):
        """Reserved interface for transformer data changes"""
        ...

    def change_generator_data_LFL5(self, data_dict):
        """Update generator data"""
        self.__write_data(self.LFL5_name, data_dict)
        self.generator_data_LFL5 = parse_generator_data_LFL5(os.path.join(self.file_path, self.LFL5_name)).copy()

    def change_load_data_LFL6(self, data_dict):
        """Update load data"""
        self.__write_data(self.LFL6_name, data_dict)
        self.load_data_LFL6 = parse_load_data_LFL6(os.path.join(self.file_path, self.LFL6_name)).copy()

    def set_generator_fault(self, IDname: str, fault_type: str, fault_begin_time, fault_during_time, fault_R, fault_X):
        """
        Set fault on generator.

        Args:
            IDname: Generator ID name
            fault_type: Fault type (AG, BG, CG, AB, AC, BC, ABG, ACG, BCG, ABCG)
            fault_begin_time: Fault start time
            fault_during_time: Fault duration
            fault_R: Fault resistance
            fault_X: Fault reactance
        """
        gen = self.find_by_IDName(str(IDname), self.generator_data_LFL5)
        buses = self.find_bus_by_generator(gen)
        pprint.pprint(buses, sort_dicts=False)
        res_list_to_file = []
        if not buses:
            return
        else:
            for bus in buses:
                lin_buses_i, lin_buses_j = self.find_ac_line_by_bus_i_name(bus), self.find_ac_line_by_bus_j_name(bus)
                if lin_buses_i:
                    for lin_bus_i in lin_buses_i:
                        fault_st11_dict = self.change_STcal_config_STS11(
                            fault_line_I=lin_bus_i['I_Name'],
                            fault_line_J=lin_bus_i['J_name'],
                            fault_type=fault_type,
                            K_percent=0,
                            fault_begin_time=fault_begin_time,
                            fault_during_time=fault_during_time,
                            fault_R=fault_R,
                            fault_X=fault_X
                        )
                        res_list_to_file.append(fault_st11_dict)
                if lin_buses_j:
                    for lin_bus_j in lin_buses_j:
                        fault_st11_dict = self.change_STcal_config_STS11(
                            fault_line_I=lin_bus_j['I_Name'],
                            fault_line_J=lin_bus_j['J_name'],
                            fault_type=fault_type,
                            K_percent=100,
                            fault_begin_time=fault_begin_time,
                            fault_during_time=fault_during_time,
                            fault_R=fault_R,
                            fault_X=fault_X
                        )
                        res_list_to_file.append(fault_st11_dict)

        keys = list(res_list_to_file[0].keys()) if res_list_to_file else []
        with open(os.path.join(self.file_path, self.STS11_name), 'w') as file:
            for d in res_list_to_file:
                row = [str(d[key]) for key in keys]
                file.write(','.join(row) + '\n')

    def change_STcal_config_STS11(self, fault_line_I, fault_line_J,
                                  fault_type, K_percent, fault_begin_time, fault_during_time,
                                  fault_R, fault_X):
        """Configure transient fault simulation"""
        init_dict = self.find_ac_line_by_ij_name(str(fault_line_I), str(fault_line_J), self.ac_line_data_LFL2)
        fault_key_dataclass = self.fault_key_map[fault_type]
        init_dict = init_dict[0]
        res_dict = {
            "Mark": init_dict['Mark'],
            'I_Name': init_dict['I_Name'],
            'J_Name': init_dict['J_name'],
            'No': init_dict['No'],
            "K%": str(K_percent),
            'Add_Name': '0',
            'A': fault_key_dataclass.A,
            'B': fault_key_dataclass.B,
            'C': fault_key_dataclass.C,
            'D': fault_key_dataclass.D,
            'K': fault_key_dataclass.K,
            'M': fault_key_dataclass.M,
            'Ts': fault_begin_time,
            'Te': fault_during_time + fault_begin_time,
            'R': fault_R,
            'QX': fault_X
        }
        return res_dict

    def generate_STANAGRPDAT_data(self):
        """Generate STANAGRP.DAT file"""
        buses = self.bus_data_LFL1
        with open(os.path.join(self.file_path, self.STANAGRPDAT_name), 'w') as file:
            i = 0
            for bus in buses:
                row = [str(i), str(bus['Line_Number']), f"'{str(i)}'"]
                i += 1
                file.write(','.join(row) + '\n')

    def LF_is_converge(self):
        """Check if load flow calculation converged"""
        self.LFLP1_data = parse_cal_data_LFCAL(os.path.join(self.file_path, self.LFCAL_name))
        if self.LFLP1_data['Mcal'] == 1:
            return True
        else:
            return False

    def ST_is_converge(self):
        """Check if transient stability calculation converged"""
        self.STCAL_data = parse_STCAL_data(os.path.join(self.file_path, self.STCAL_name))
        if self.STCAL_data['Mcal'] > 0:
            return True
        else:
            return False

    def execute_LFcal(self):
        """Execute load flow calculation"""
        self.__LFcal()
        if self.LF_is_converge():
            print('潮流收敛')
            self.cal_data_LFCAL = parse_cal_data_LFCAL(os.path.join(self.file_path, self.LFCAL_name))
            self.LFLP1_data = parse_LFLP1_data(os.path.join(self.file_path, self.LFLP1_name))
            self.LFLP2_data = parse_LFLP2_data(os.path.join(self.file_path, self.LFLP2_name))
            self.LFLP3_data = parse_LFLP3_data(os.path.join(self.file_path, self.LFLP3_name))
        else:
            print("潮流计算不收敛！跳过本次结果")

    def execute_STcal(self):
        """Execute transient stability calculation"""
        self.__STcal()
        if self.ST_is_converge():
            print("暂态稳定收敛")
            self.STANADAT_data = parse_STANADAT_data(os.path.join(self.file_path, self.STANADAT_name))
            self.STCAL_data = parse_STCAL_data(os.path.join(self.file_path, self.STCAL_name))
            self.STB12_data = parse_STB12_data(os.path.join(self.file_path, self.STB12_name))
            self.STR12_data = parse_STR12_data(os.path.join(self.file_path, self.STR12_name))
        else:
            print("稳定性计算不收敛！跳过本次结果")

    def get_LFcal_data(self):
        """Get load flow calculation results"""
        return self.cal_data_LFCAL, self.LFLP1_data, self.LFLP2_data, self.LFLP3_data

    def get_STcal_data(self):
        """Get transient stability calculation results"""
        return self.STANADAT_data, self.STCAL_data, self.STB12_data, self.STR12_data

    def __STcal(self):
        """Execute transient stability calculation (internal)"""
        pausetime = self.cal_delay
        filepath = self.file_path
        fileexe = os.path.join(filepath, "wmudrt.exe")
        cmd = f'cd "{filepath}" && "{fileexe}"'
        subprocess.Popen(cmd, shell=True)
        time.sleep(pausetime)
        subprocess.call('taskkill /f /t /im cmd.exe', shell=True)

    def __LFcal(self):
        """Execute load flow calculation (internal)"""
        pausetime = self.cal_delay
        filepath = self.file_path
        fileexe = os.path.join(filepath, "WMLFRTMsg.exe")
        cmd = f'cd "{filepath}" && "{fileexe}"'
        subprocess.Popen(cmd, shell=True)
        time.sleep(pausetime)
        subprocess.call('taskkill /f /t /im cmd.exe', shell=True)


try:
    import networkx as nx
    import matplotlib.pyplot as plt

    plt.rcParams['font.sans-serif'] = ['SimSun']
    plt.rcParams['axes.unicode_minus'] = False

    class GraphTools:
        """Power grid topology graph tools"""

        def __init__(self, solver: GridLFSTAnalyzer, init_make_graph=False):
            self.graph = nx.MultiGraph()
            self.solver = solver
            self.node_500 = self.get_U_inrange()
            print("符合条件的数量有：", len(self.node_500))
            if init_make_graph:
                self.make_graph()
            print("图初始化完了")

        def get_U_inrange(self, v_range=100):
            """Get buses within specified voltage range"""
            return [x for x in self.solver.bus_data_LFL1.copy() if float(x['Vmin']) >= v_range]

        def make_graph(self):
            """Build power grid graph"""
            self.add_nodes()
            print("母线节点添加完成")
            self.add_line_edge()
            print("交流输电线添加完成")
            self.add_transformer_edge()
            print("变压器输电线添加完成")
            self.add_load_edge()
            print("负荷添加完成")

        def add_nodes(self):
            """Add bus nodes"""
            node_key = self.node_500
            for node in node_key:
                node_name = node['Bus-Name']
                self.graph.add_node(str(node_name), size=0.1, node_color="black")

        def add_line_edge(self):
            """Add AC line edges"""
            for ac_line in self.solver.ac_line_data_LFL2:
                i_bus_num = ac_line['I_Name']
                j_bus_num = ac_line['J_name']
                i_bus_find = self.solver.find_by_line_number(i_bus_num, self.node_500)
                j_bus_find = self.solver.find_by_line_number(j_bus_num, self.node_500)

                if i_bus_find != [] and j_bus_find != []:
                    bus_name_i, bus_name_j = i_bus_find['Bus-Name'], j_bus_find['Bus-Name']
                    if str(bus_name_i) == str(bus_name_j):
                        continue
                    ac_line_name = ac_line['IDName']
                    self.graph.add_edge(str(bus_name_i), str(bus_name_j), key=ac_line_name, edge_color="yellow")

        def add_transformer_edge(self):
            """Add transformer edges"""
            for ac_line in self.solver.transformer_data_LFL3:
                i_bus_num = ac_line['I_Name']
                j_bus_num = ac_line['J_name']
                i_bus_num, j_bus_num = str(abs(int(i_bus_num))), str(abs(int(j_bus_num)))
                i_bus_find = self.solver.find_by_line_number(i_bus_num, self.node_500)
                j_bus_find = self.solver.find_by_line_number(j_bus_num, self.node_500)
                if i_bus_find != [] and j_bus_find != []:
                    bus_name_i, bus_name_j = i_bus_find['Bus-Name'], j_bus_find['Bus-Name']
                    if str(bus_name_i) == str(bus_name_j):
                        continue
                    transformer_name = ac_line['IDName']
                    self.graph.add_edge(str(bus_name_i), str(bus_name_j), key=transformer_name, edge_color="green")

        def add_load_edge(self):
            """Add load edges"""
            for ac_line in self.solver.load_data_LFL6:
                bus_num = ac_line['Bus_Name']
                bus_find = self.solver.find_by_line_number(bus_num, self.node_500)
                if bus_find:
                    bus_name = bus_find['Bus-Name']
                    load_name = ac_line['IDName']
                    self.graph.add_node(str(load_name), color='green', size=0.1)
                    self.graph.add_edge(str(load_name), str(bus_name), key="L" + load_name, edge_color="black")

        def visualize_graph(self, name='graph.png'):
            """Visualize and save graph"""
            plt.figure(figsize=(200, 200))
            pos = nx.spring_layout(self.graph, k=0.05, iterations=150)
            nx.draw(self.graph, pos, with_labels=True)
            plt.savefig(name)

except ImportError:
    class GraphTools:
        """Placeholder when networkx/matplotlib not available"""

        def __init__(self, solver, init_make_graph=False):
            print("Warning: networkx or matplotlib not installed. GraphTools disabled.")
            self.solver = solver

        def make_graph(self):
            raise ImportError("networkx and matplotlib required for graph functionality")

        def visualize_graph(self, name='graph.png'):
            raise ImportError("networkx and matplotlib required for graph functionality")

        def get_U_inrange(self, v_range=100):
            return []

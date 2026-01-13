# -*- coding: utf-8 -*-
"""
GridGraphResearch 测试用例
Tests for GridGraphResearch package
"""

import unittest
import os
import tempfile
import shutil
from io import StringIO

# Import the modules to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ConfigFileManager import (
    read_control_info_LFL0,
    parse_bus_data_LFL1,
    parse_ac_line_data_LFL2,
    parse_transformer_data_LFL3,
    parse_generator_data_LFL5,
    parse_load_data_LFL6,
    parse_area_power_data_LFL7,
    parse_fault_data_STS11,
    parse_cal_data_LFCAL,
    parse_LFLP1_data,
    parse_LFLP2_data,
    parse_LFLP3_data,
    parse_STCAL_data,
)


class TestConfigFileManager(unittest.TestCase):
    """Test cases for ConfigFileManager module"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_read_control_info_LFL0(self):
        """Test reading LF.L0 control info file"""
        # Create test file
        test_file = os.path.join(self.test_dir, 'LF.L0')
        with open(test_file, 'w') as f:
            f.write("100,50,30,5,20,80,3,0,0,0,1\n")
            f.write("100.0,1.1,0.9,0.0001,1,50,1,0,0,0,0,0,0\n")

        result = read_control_info_LFL0(test_file)

        # Verify first line fields
        self.assertEqual(result['NBB'], 100)
        self.assertEqual(result['NLL'], 50)
        self.assertEqual(result['NTT'], 30)
        self.assertEqual(result['NDC'], 5)
        self.assertEqual(result['NGG'], 20)
        self.assertEqual(result['NLOAD'], 80)

        # Verify second line fields
        self.assertEqual(result['SB'], 100.0)
        self.assertEqual(result['Vmax'], 1.1)
        self.assertEqual(result['Vmin'], 0.9)
        self.assertEqual(result['Eps'], 0.0001)
        self.assertEqual(result['Meth'], 1)
        self.assertEqual(result['Iter'], 50)

    def test_read_control_info_LFL0_invalid_fields(self):
        """Test LF.L0 with invalid field count raises error"""
        test_file = os.path.join(self.test_dir, 'LF.L0')
        with open(test_file, 'w') as f:
            f.write("100,50,30\n")  # Too few fields
            f.write("100.0,1.1,0.9,0.0001,1,50,1,0,0,0,0,0,0\n")

        with self.assertRaises(ValueError) as context:
            read_control_info_LFL0(test_file)
        self.assertIn("字段数量不匹配", str(context.exception))

    def test_parse_bus_data_LFL1(self):
        """Test parsing LF.L1 bus data file"""
        test_file = os.path.join(self.test_dir, 'LF.L1')
        with open(test_file, 'w') as f:
            f.write("'BUS001',500.0,1,1.1,0.9,0.0,0.0\n")
            f.write("'BUS002',220.0,2,1.05,0.95,0.0,0.0\n")

        result = parse_bus_data_LFL1(test_file)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Bus-Name'], 'BUS001')
        self.assertEqual(result[0]['Vbase'], 500.0)
        self.assertEqual(result[0]['Area'], 1)
        self.assertEqual(result[0]['Line_Number'], 1)
        self.assertEqual(result[1]['Bus-Name'], 'BUS002')
        self.assertEqual(result[1]['Vbase'], 220.0)
        self.assertEqual(result[1]['Line_Number'], 2)

    def test_parse_ac_line_data_LFL2(self):
        """Test parsing LF.L2 AC line data file"""
        test_file = os.path.join(self.test_dir, 'LF.L2')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("1,1,2,1,0.01,0.1,0.02,1,0,0,0,0,0.0,1.5,0.0,'BUS001','0','Line001'\n")

        result = parse_ac_line_data_LFL2(test_file)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Mark'], 1)
        self.assertEqual(result[0]['I_Name'], 1)
        self.assertEqual(result[0]['J_name'], 2)
        self.assertEqual(result[0]['R'], 0.01)
        self.assertEqual(result[0]['X'], 0.1)
        self.assertEqual(result[0]['IDName'], 'Line001')

    def test_parse_generator_data_LFL5(self):
        """Test parsing LF.L5 generator data file"""
        test_file = os.path.join(self.test_dir, 'LF.L5')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("1,1,2,100.0,50.0,1.0,0.0,200.0,-50.0,150.0,50.0,0,0,0,0.0,100.0,'BUS001',0,'Gen001'\n")

        result = parse_generator_data_LFL5(test_file)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Mark'], 1)
        self.assertEqual(result[0]['Bus_Name'], 1)
        self.assertEqual(result[0]['Type'], 2)
        self.assertEqual(result[0]['Pg'], 100.0)
        self.assertEqual(result[0]['Qg'], 50.0)
        self.assertEqual(result[0]['IDName'], 'Gen001')

    def test_parse_load_data_LFL6(self):
        """Test parsing LF.L6 load data file"""
        test_file = os.path.join(self.test_dir, 'LF.L6')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("1,1,1,1.0,50.0,20.0,1.0,0.0,100.0,-20.0,80.0,0,0,0,0,0.0,'BUS001',0,'Load001'\n")

        result = parse_load_data_LFL6(test_file)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Mark'], 1)
        self.assertEqual(result[0]['Bus_Name'], 1)
        self.assertEqual(result[0]['Pl'], 50.0)
        self.assertEqual(result[0]['Ql'], 20.0)
        self.assertEqual(result[0]['IDName'], 'Load001')

    def test_parse_fault_data_STS11(self):
        """Test parsing ST.S11 fault data file"""
        test_file = os.path.join(self.test_dir, 'ST.S11')
        with open(test_file, 'w') as f:
            f.write("1,1,2,1,50.0,'0',1,0,0,1,0,0,1.0,1.5,0.001,0.0\n")

        result = parse_fault_data_STS11(test_file)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['Mark'], 1)
        self.assertEqual(result[0]['I_Name'], 1)
        self.assertEqual(result[0]['J_Name'], 2)
        self.assertEqual(result[0]['A'], 1)  # Phase A fault
        self.assertEqual(result[0]['D'], 1)  # Ground fault
        self.assertEqual(result[0]['Ts'], 1.0)
        self.assertEqual(result[0]['Te'], 1.5)

    def test_parse_LFLP1_data(self):
        """Test parsing LF.LP1 bus results file"""
        test_file = os.path.join(self.test_dir, 'LF.LP1')
        with open(test_file, 'w') as f:
            f.write("Header line to skip\n")
            f.write("1,1.05,0.5,'BUS001'\n")
            f.write("2,0.98,-1.2,'BUS002'\n")

        result = parse_LFLP1_data(test_file)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Bus'], 1)
        self.assertEqual(result[0]['V'], 1.05)
        self.assertEqual(result[0]['Theta'], 0.5)
        self.assertEqual(result[0]['Busname'], 'BUS001')

    def test_parse_LFLP2_data(self):
        """Test parsing LF.LP2 AC line results file"""
        test_file = os.path.join(self.test_dir, 'LF.LP2')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("1,2,1,100.0,50.0,-98.0,-48.0,2.0,2.0,'Line001'\n")

        result = parse_LFLP2_data(test_file)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['I'], 1)
        self.assertEqual(result[0]['J'], 2)
        self.assertEqual(result[0]['Pi'], 100.0)
        self.assertEqual(result[0]['Qi'], 50.0)
        self.assertEqual(result[0]['ACLinename'], 'Line001')


class TestFaultTypes(unittest.TestCase):
    """Test cases for fault type configurations"""

    def test_fault_type_mapping(self):
        """Test that all fault types are properly defined"""
        from GridLfstanalyzer import FaultST11Config

        # Test single phase ground faults
        ag = FaultST11Config(A=1, B=0, C=0, D=1, K=0, M=0)
        self.assertEqual(ag.A, 1)
        self.assertEqual(ag.D, 1)  # Ground

        # Test two phase short circuit
        ab = FaultST11Config(A=1, B=1, C=0, D=0, K=1, M=0)
        self.assertEqual(ab.A, 1)
        self.assertEqual(ab.B, 1)
        self.assertEqual(ab.K, 1)  # Short circuit

        # Test three phase short circuit with ground
        abcg = FaultST11Config(A=1, B=1, C=1, D=1, K=1, M=0)
        self.assertEqual(abcg.A, 1)
        self.assertEqual(abcg.B, 1)
        self.assertEqual(abcg.C, 1)
        self.assertEqual(abcg.D, 1)
        self.assertEqual(abcg.K, 1)


class TestDataValidation(unittest.TestCase):
    """Test cases for data validation"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_invalid_bus_data_field_count(self):
        """Test that invalid field count raises error"""
        test_file = os.path.join(self.test_dir, 'LF.L1')
        with open(test_file, 'w') as f:
            f.write("'BUS001',500.0,1\n")  # Missing fields

        with self.assertRaises(ValueError) as context:
            parse_bus_data_LFL1(test_file)
        self.assertIn("字段数量错误", str(context.exception))

    def test_invalid_data_type(self):
        """Test that invalid data type raises error"""
        test_file = os.path.join(self.test_dir, 'LF.L1')
        with open(test_file, 'w') as f:
            f.write("'BUS001','invalid',1,1.1,0.9,0.0,0.0\n")  # Vbase should be float

        with self.assertRaises(ValueError) as context:
            parse_bus_data_LFL1(test_file)
        self.assertIn("数据类型错误", str(context.exception))


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions"""

    def test_find_by_line_number(self):
        """Test finding data by line number"""
        from GridLfstanalyzer import GridLFSTAnalyzer

        data = [
            {'Line_Number': 1, 'name': 'item1'},
            {'Line_Number': 2, 'name': 'item2'},
            {'Line_Number': 3, 'name': 'item3'},
        ]

        result = GridLFSTAnalyzer.find_by_line_number(2, data)
        self.assertEqual(result['name'], 'item2')

        result = GridLFSTAnalyzer.find_by_line_number(999, data)
        self.assertEqual(result, [])

    def test_find_by_IDName(self):
        """Test finding data by IDName"""
        from GridLfstanalyzer import GridLFSTAnalyzer

        data = [
            {'IDName': 'Gen001', 'Pg': 100},
            {'IDName': 'Gen002', 'Pg': 200},
        ]

        result = GridLFSTAnalyzer.find_by_IDName('Gen001', data)
        self.assertEqual(result['Pg'], 100)

    def test_find_ac_line_by_ij_name(self):
        """Test finding AC line by I and J names"""
        from GridLfstanalyzer import GridLFSTAnalyzer

        data = [
            {'I_Name': 1, 'J_name': 2, 'IDName': 'Line1'},
            {'I_Name': 1, 'J_name': 3, 'IDName': 'Line2'},
            {'I_Name': 2, 'J_name': 3, 'IDName': 'Line3'},
        ]

        result = GridLFSTAnalyzer.find_ac_line_by_ij_name(1, 2, data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['IDName'], 'Line1')


if __name__ == '__main__':
    unittest.main()

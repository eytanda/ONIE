#!/usr/bin/python3
"""
author: Eytan Dagry
mail: eytan@silicom.co.il
Update by: Eytan Dagry



update date 07.04.2024    - ONIE_tool
"""

# included in python
import random
import datetime
import os
import subprocess
import sys
import time
import traceback
import binascii
from collections import OrderedDict
import re
from datetime import datetime
import pyudev
#from smbus2 import SMBus

# Constants
SCRIPT_VERSION = 6.5
global actual_mem_size
actual_mem_size = 512


def compare_bin_files(file1, file2):
    buffer_size = 4096  # Read in chunks for large files

    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        while True:
            b1 = f1.read(buffer_size)
            b2 = f2.read(buffer_size)

            if b1 != b2:
                return False  # Files are different

            if not b1:  # End of both files
                return True  # Files are the same

def check_py_ver():
    command = ["python3", "--version"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str = result.stdout.decode('utf-8')

        # Extract major version
        major_version = get_major_version(stdout_str)
        return major_version

    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}. Output: {e.output.decode('utf-8')}")
        return None


def get_major_version(version_string):
    # Parse the version string and extract major version
    version_parts = version_string.strip().split()
    if len(version_parts) >= 2:
        version_number = version_parts[1]
        major_version = '.'.join(version_number.split('.')[:2])
        return major_version
    else:
        return None


def check_if_ubuntu():
    command = [
        "hostnamectl"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str = result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}. Output: {e.output.decode('utf-8')}")
        # return "", e.output.decode('utf-8')

    pattern = r'^Operating System: (.+)$'

    match = re.search(pattern, stdout_str, re.MULTILINE)

    if match:
        operating_system_line = match.group(1)
        os = operating_system_line.split()[0]
        if os == 'Ubuntu' or os == 'Debian':
            os_command = 'apt'
            return True   # os is Ubunto  or Debian
        else:
            return False


# not included in python



# Colors
BLUE_COLOR = "\033[1;34;40m"
PURPLE_COLOR = "\033[1;35;40m"
YELLOW_COLOR = "\033[1;33;40m"
CYAN_COLOR = "\033[1;36;40m"
RED_COLOR = "\033[1;31;40m"
GREEN_COLOR = "\033[1;32;40m"
ALL_COLORS = [BLUE_COLOR, PURPLE_COLOR, YELLOW_COLOR, CYAN_COLOR, RED_COLOR, GREEN_COLOR]
RESET_STYLE_BLACK_BG = "\033[0;0;40m"
RESET_STYLE = "\033[0;0;0m"
# IP
#BMC_IP = "192.168.0.10"
#IP_HOST = "192.168.0.100"
# FRU
VENDOR = b"Silicom"
HEADER_STRING = b"TlvInfo\x00"
HEADER_VERSION = b"\x01"
# PRODUCT_NAME = b"DU-ICXSP-ES0"
# PART_NUMBER_32 = b"90500-0169-E5"
# PART_NUMBER_16 = b"90500-0169-E6"
# LABEL_REVISION = b"R101"
# MANUFACTURER = b"Silicom"
# COUNTRY_CODE = b"IL"
# SILICOM_ONIE_VERSION = b"R002"
#IANA_CODE_OF_SILICOM = b"\x00\x00\x3d\x4e"
#NUMBER_OF_MACS = b"\x00\x09"
#

ALLOWED_CODES = ["21", "22", "23", "24", "25", "26", "27", "28", "29",
                 "2a", "2b", "2c", "2d", "2e", "2f", "51", "52", "53",
                 "54", "55", "56", "57", "58", "59", "5a", "5b", "5c",
                 "5d", "5e", "5f", "60", "61", "62", "fd",  "81",
                 "82", "83", "84", "85", "86", "87", "fe"]
NOT_ALLOWED_CODES = ["00", "ff"]
CODES_MEANING = {"21": "Product Name: ",
                 "22": "Part Number: ",
                 "23": "Serial Number: ",
                 "24": "MAC: ",
                 "25": "Manufacture Date: ",
                 "26": "Device Version: ",
                 "27": "Label Revision: ",
                 "28": "Platform Name: ",
                 "29": "ONIE Version",
                 "2a": "Number Of MACs: ",
                 "2b": "Manufacturer: ",
                 "2c": "Country Code: ",
                 "2d": "Vendor: ",
                 "2e": "Diag Version: ",
                 "2f": "Service Tag: ",
                 "51": "sys manufacture: ",
                 "52": "sys product name: ",
                 "53": "sys serial number: ",
                 "54": "UUID (hex): ",
                 "55": "sys version: ",
                 "56": "sys SKU: ",
                 "57": "sys family: ",
                 "58": "sys wake-up type: ",
                 "59": "board manufacture: ",
                 "5a": "board product name: ",
                 "5b": "board version: ",
                 "5c": "board serial number: ",
                 "5d": "board asset tag: ",
                 "5e": "chassis manufacture: ",
                 "5f": "chassis serial number: ",
                 "60": "chassis version: ",
                 "61": "chassis asset tag: ",
                 "62": "Chassis type: ",
                 "fd": "Vendor Extension: ",
                 "81": "silicom_onie_version: ",
                 "82": "TNB1: ",
                 "83": "IMEI1: ",
                 "84": "IMEI2: ",
                 "85": "TNB1: ",
                 "86": "TNB2: ",
                 "87": "TNB3: ",
                 "fe": "CRC-32 (checksum): "}
ALLOWED_CHARS = [chr(num) for num in range(65, 91)]  # A - Z
ALLOWED_CHARS += [chr(num) for num in range(97, 123)]  # a - z
ALLOWED_CHARS += [chr(num) for num in range(32, 65)]  # sings
ALLOWED_CHARS += [chr(num) for num in range(91, 97)]  # more sings
ALLOWED_CHARS += [chr(num) for num in range(123, 127)]  # more sings
# Globals
i2c_bus_number = None
os_clear = True




def scan_i2c_addresses():
    """Detect available I2C buses using pyudev."""
    available_buses = []

    context = pyudev.Context()  # Initialize pyudev context
    # Iterate through all devices in the 'i2c-dev' subsystem
    for device in context.list_devices(subsystem='i2c-dev'):
        # Get the device path and extract bus number (e.g., /dev/i2c-0, /dev/i2c-1)
        device_path = device.device_node
        if device_path.startswith('/dev/i2c-'):
            bus_number = int(device_path.split('-')[1])
            available_buses.append(bus_number)

    return available_buses




def get_i2c_bus_number_and_enable_access():
    """ checks what's the i2c bus number and return it """
    global i2c_bus_number
    global smbus_device_id
    i2c_addresses = scan_i2c_addresses()
    if len(i2c_addresses) == 1:
        i2c_bus_number = int(i2c_addresses[0])
        # print("Found i2c_bus_number= ", i2c_bus_number)
    elif len(i2c_addresses) == 0:
        print(RED_COLOR + "Couldn't Find Active I2C Bus" + RESET_STYLE)
        exit()
    else:
        print("There Is More Then 1 Active I2C Bus.\n"
              "Available Addresses:\n"
              "[%s]" % ", ".join(map(str, i2c_addresses)))
        chosen_i2c_address = input(YELLOW_COLOR + "Please Chose The Desired BUS Address:" + RESET_STYLE)
        try:
            chosen_i2c_address = int(chosen_i2c_address)
        except Exception as err:
            print(RED_COLOR + "PLease Enter Only Numbers." + RESET_STYLE_BLACK_BG)
            chosen_i2c_address = input(YELLOW_COLOR + "Please Chose The Desired BUS Address:" + RESET_STYLE)
        while chosen_i2c_address not in i2c_addresses:
            print("Please Look Above For Active I2C Busses.\n")
            chosen_i2c_address = input("Address: ")
            try:
                chosen_i2c_address = int(chosen_i2c_address)
            except Exception as err:
                print(RED_COLOR + "PLease Enter Only Numbers." + RESET_STYLE_BLACK_BG)
        i2c_bus_number = int(chosen_i2c_address)
        print("i2c_bus_number= ", i2c_bus_number)


def get_smbus_device_id(num_of_required_I2C_devices):
    """ Get the smbus device IDs from the user """

    addresses = []

    # In case that in read process and found that FRU is > 256, Prompt for the first I2C device address
    if num_of_required_I2C_devices == 3:
        while True:
            try:
                address = input(YELLOW_COLOR +
                                "The FRU Data includes more then 256  bytes.\n"
                                "Enter a second I2C device address in hexadecimal format (e.g., 0x20): " + RESET_STYLE)
                if address.strip():  # Check if the input is not empty
                    address = int(address, 16)
                    if 0 <= address <= 0x7F:  # Ensure the address is within the valid range
                        return address
                    else:
                        print(RED_COLOR + "Error: Invalid I2C address."
                                          " Please enter a value between 0 and 0x7F." + RESET_STYLE)
                else:
                    print(RED_COLOR + "Error: Please enter a valid I2C address." + RESET_STYLE)

            except ValueError:
                print(RED_COLOR + "Error: Please enter a valid integer"
                                  " or hexadecimal value (e.g., 0x20)." + RESET_STYLE)

    # Prompt for the first I2C device address
    if num_of_required_I2C_devices >= 1:
        while True:
            try:
                address = input(YELLOW_COLOR + "Enter the I2C device #1 address in hexadecimal format (e.g., 0x20): "
                                + RESET_STYLE)
                if address.strip():  # Check if the input is not empty
                    address = int(address, 16)
                    if 0 <= address <= 0x7F:  # Ensure the address is within the valid range
                        addresses.append(address)
                        break
                    else:
                        print(RED_COLOR + f"Error: Invalid I2C address."
                                          f" Please enter a value between 0 and 0x7F." + RESET_STYLE)
                else:
                    print(RED_COLOR + f"Error: Please enter a valid I2C address." + RESET_STYLE)

            except ValueError:
                print(RED_COLOR + f"Error: Please enter a valid integer"
                                  f" or hexadecimal value (e.g., 0x20)." + RESET_STYLE)

    if num_of_required_I2C_devices == 2:
        # Prompt for the second I2C device address (optional)
        while True:
            try:
                address = input(YELLOW_COLOR + "Enter the I2C device #2 address in hexadecimal format (e.g., 0x20): "
                                + RESET_STYLE)
                if address.strip():  # Check if the input is not empty
                    address = int(address, 16)
                    if 0 <= address <= 0x7F:  # Ensure the address is within the valid range
                        addresses.append(address)
                        break
                    else:
                        print(RED_COLOR + f"Error: Invalid I2C address."
                                          f" Please enter a value between 0 and 0x7F." + RESET_STYLE)
                else:
                    print(RED_COLOR + f"Error: Please enter a valid I2C address." + RESET_STYLE)

            except ValueError:
                print(RED_COLOR + "Error: Please enter a valid integer"
                                  " or hexadecimal value (e.g., 0x20)." + RESET_STYLE)
    else:
        addresses.append(None)

    return tuple(addresses)



def output_fru_data_to_bin_file(file_name="take system time", verbose=True, i2c_check=True):
    """
    outputs the system fru to file_name.bin
    :param file_name: the name of the file that the data will be saved to, default is 'onie_eeprom' + '.bin'
                      file_name should be only the name with no extension.
    :param verbose: if verbose is True this func will print what it's doing, if verbose is False nothing will be printed
    :type file_name: str
    :type verbose: bool
    :return: the output file name, if there was a problem creating a file with the supplied file_name it will output
             the data to another file, so it returns the name of the output file.
    :rtype: str
    """
    global i2c_bus_number
    global smbus_device_id1
    global smbus_device_id2
    if i2c_check:
        get_i2c_bus_number_and_enable_access()
        smbus_device_id1, smbus_device_id2 = get_smbus_device_id(1)
    if file_name == "take system time":
        file_name = "fru_" + datetime.now().strftime("%m.%d.%Y__%H_%M_%S")
    else:
        file_name = "compare_write" +  datetime.now().strftime("%m.%d.%Y__%H_%M_%S")

    # read all the data in the fru
    fru_data = []
    if verbose:
        print(GREEN_COLOR + "Reading From FRU" + RESET_STYLE_BLACK_BG)
    count_to_go_row_down = 64
    for i in range(0, 256):
        if count_to_go_row_down == 0 and verbose:
            count_to_go_row_down = 64
            print()
        bus = SMBus(i2c_bus_number)
        try:
            byte = bus.read_byte_data(smbus_device_id1, i)
        except IOError as e:
            print(RED_COLOR + f"Failed to read from BUS {i2c_bus_number},"
                              f"  I2C device {smbus_device_id1}." + RESET_STYLE)
            sys.exit(1)

        if verbose:
            print(ALL_COLORS[random.randint(0, len(ALL_COLORS) - 1)] + "-" + RESET_STYLE_BLACK_BG, end="")
        fru_data.append(byte)
        count_to_go_row_down -= 1
    if verbose:
        print()

    id_bytes = bytes(fru_data[:8])
    # Convert bytes to a string
    # id_string = id_bytes.decode('utf-8')
    is_id_string_ok = id_bytes == HEADER_STRING
    if is_id_string_ok:
        if verbose:
            print(GREEN_COLOR + "FRU Data Is Valid - ID String - Ok" + RESET_STYLE_BLACK_BG)

    else:
        print(RED_COLOR + "FRU Data Isn't Valid - ID String - Not Ok" + RESET_STYLE_BLACK_BG)
        sys.exit(1)

    # check if the len of fru_data is 10 or more
    # because if it is not it means the len of the entire fru data is missing and the data isn't valid
    if not len(fru_data) >= 10:
        print(RED_COLOR + "FRU Data Isn't Valid" + RESET_STYLE_BLACK_BG)
        time.sleep(13)
        loop_main()
        print(RESET_STYLE)
        exit()
    # get data len in hex from the data that we read
    data_len_hex_msb = str(hex(fru_data[9]))[2:]  # get the hex number
    data_len_hex_lsb = str(hex(fru_data[10]))[2:]  # get the hex number
    # if the hex number is 0x9 for example it will become 9
    if len(data_len_hex_lsb) == 1:
        data_len_hex_lsb = "0" + data_len_hex_lsb
    if len(data_len_hex_msb) == 1:
        data_len_hex_msb = "0" + data_len_hex_msb
    # convert data len to decimal

    data_len = (int(data_len_hex_lsb, 16) & 0xFF) + ((int(data_len_hex_msb, 16) & 0xFF) << 8)
    if (data_len + 11) < 256:
        # check if fru_data really contains data_len + 11
        if not len(fru_data) >= data_len + 11:
            print(RED_COLOR + "FRU Data Isn't Valid" + RESET_STYLE_BLACK_BG)
            time.sleep(13)
            loop_main()
            print(RESET_STYLE)
            exit()
    else:
        # ## FRU > 256 , ask for additional I2C device
        smbus_device_id2 = get_smbus_device_id(3)

        x = data_len + 11 - 256
        for i in range(0, x):
            if count_to_go_row_down == 0 and verbose:
                count_to_go_row_down = 64
                print()
            try:
                byte = bus.read_byte_data(smbus_device_id2, i)
            except IOError as e:
                print(RED_COLOR + f"Failed to read from BUS {i2c_bus_number},"
                                  f"  I2C device {smbus_device_id2}." + RESET_STYLE)
                sys.exit(1)
            if verbose:
                print(ALL_COLORS[random.randint(0, len(ALL_COLORS) - 1)] + "-" + RESET_STYLE_BLACK_BG, end="")
            fru_data.append(byte)
            count_to_go_row_down -= 1
        if verbose:
            print()
        # close the smbus
        bus.close()

    # save the part of the fru that actually has data
    fru_data = fru_data[:data_len + 11]
    fru_data_byte_array = bytearray(fru_data)  # convert the data to byte array
    # save the data to a temp file
    current_directory = os.getcwd()
    try:
        with open(f"{current_directory}/FRU_Backup_files/{file_name}.bin", "wb") as file:
            file.write(fru_data_byte_array)
        output_file_name = f"{current_directory}/FRU_Backup_files/{file_name}.bin"
    except OSError as err:
        print(RED_COLOR + "Couldn't Open '%s'" % file_name, RESET_STYLE_BLACK_BG)
        with open("errors.log", "a") as errors_file:
            errors_file.write(traceback.format_exc() + "\n")
        with open("onie_eeprom.bin", "wb") as file:
            file.write(fru_data_byte_array)
        output_file_name = "onie_eeprom"
    return output_file_name


def print_fru_file_in_hex(file_name="onie_eeprom", read_from_fru=True):
    """
    Print FRU Data/FRU File In Hex
    :param file_name: if read_from_fru == False, this will be the file that this func will print
                      if read_from_fru == True, this will be the file name of the output data from the fru
                      and this func will print the data in that file in hex
    :param read_from_fru: if True, the printed data will be the data that is in the fru
                          if False, the printed data will be the data in file_name
    :type file_name: str
    :type read_from_fru: bool
    """

    if file_name.endswith(".bin"):
        file_name = file_name[:-4]
    if read_from_fru:
        output_file_name = output_fru_data_to_bin_file(verbose=False)
        output_file_name = output_file_name[:-4]
    else:
        if os.path.isfile(file_name + ".bin"):
            output_file_name = file_name
        else:
            print(RED_COLOR + "ERROR File Doesn't Exist" + RESET_STYLE_BLACK_BG)
            time.sleep(3)
            loop_main()
            print(RESET_STYLE)
            exit()
    # open the file with the fru data
    with open(output_file_name + ".bin", "rb") as file:
        fru_data = file.read()
    # print
    print(" " * 9, end="")
    for i in range(0, 16):
        print(hex(i) + " " * (6 - len(hex(i))), end="")
    print("\n")
    count = 0
    for i in range(0, len(fru_data)):
        data = fru_data[i]
        if count == 16 or count == 0:
            if count == 16:
                data_list_in_ascii = [chr(char) for char in fru_data[i - 16:i]]
                for j in range(0, len(data_list_in_ascii)):
                    char = data_list_in_ascii[j]
                    if r"\x" in char:
                        data_list_in_ascii[j] = "."
                    elif char not in ALLOWED_CHARS:
                        data_list_in_ascii[j] = "."
                print("".join(data_list_in_ascii))
                # print(fru_data[i-16:i])
                # print(len(fru_data[i-16:i]))
            print(hex(i) + ":" + " " * (8 - len(hex(i))), end="")
            count = 0
        value = hex(data)[2:]
        if len(value) == 1:
            value = "0" + value
        print(value + " " * (6 - len(value)), end="")
        count += 1
    print(" " * (16 - count) * 6, end="")
    data_list_in_ascii = [chr(char) for char in fru_data[i - count:i]]
    for j in range(0, len(data_list_in_ascii)):
        char = data_list_in_ascii[j]
        if r"\x" in char:
            data_list_in_ascii[j] = "."
        elif char not in ALLOWED_CHARS:
            data_list_in_ascii[j] = "."
    print("".join(data_list_in_ascii))


def write_to_host_fru(file_name='non', fru_data='', config_file="non"):
    """
    Write Data To Host FRU
    :param fru_data: the data to write to the FRU
    :type fru_data: list (of int)
    """
    global smbus_device_id1
    global smbus_device_id2
    global i2c_bus_number
    global actual_mem_size
    get_i2c_bus_number_and_enable_access()
    if len(fru_data) <= 256 and actual_mem_size == 256:
        mem_size_required = 256
        smbus_device_id1, smbus_device_id2 = get_smbus_device_id(1)
    else:
        if len(fru_data) > 256 and actual_mem_size == 256:
            print(RED_COLOR + f"The FRU Data includes more then 256 but the actual_mem_size defined in the fru_config"
                          f" file is {actual_mem_size}. Please fix and try again." + RESET_STYLE)
            sys.exit(1)
        else:
            mem_size_required = 512
            smbus_device_id1, smbus_device_id2 = get_smbus_device_id(2)
    # open smbus to the i2c_bus_number
    bus = SMBus(i2c_bus_number)
    print(GREEN_COLOR + "Starting To Write To HOST FRU" + RESET_STYLE_BLACK_BG + "\n")
    count_to_go_row_down = 64
    for i in range(0, mem_size_required):
        time.sleep(0.01)
        if count_to_go_row_down == 0:
            count_to_go_row_down = 64
            print()
        if len(fru_data) > i:
            count = 0
            ok = False
            while not ok:
                if count == 10:
                    print("\n\n\n--------------------------------------------------\n\n")
                    print(" " * 13 + RED_COLOR + "1Couldn't Write To FRU" + RESET_STYLE_BLACK_BG)
                    print(RED_COLOR + "!!!!!!!!!!!! FRU Creation Failed !!!!!!!!!!!!!" + RESET_STYLE_BLACK_BG)
                    print("\n\n--------------------------------------------------\n\n\n")
                    time.sleep(3)
                    loop_main()
                    print(RESET_STYLE)
                    exit()
                try:
                    if i < 256:

                        try:
                            bus.write_byte_data(smbus_device_id1, i, fru_data[i])
                        except IOError as e:
                            print(RED_COLOR + f"Failed to write to BUS {i2c_bus_number},"
                                              f"I2C device {smbus_device_id1}." + RESET_STYLE)
                            sys.exit(1)

                        print(ALL_COLORS[random.randint(0, len(ALL_COLORS) - 1)] + "-" + RESET_STYLE_BLACK_BG, end="")

                    else:
                        try:
                            bus.write_byte_data(smbus_device_id2, i, fru_data[i])
                        except IOError as e:
                            print(RED_COLOR + f"Failed to write to BUS {i2c_bus_number},"
                                              f"I2C device {smbus_device_id2}." + RESET_STYLE)
                            sys.exit(1)

                        print(ALL_COLORS[random.randint(0, len(ALL_COLORS) - 1)] + "-" + RESET_STYLE_BLACK_BG, end="")

                    ok = True
                except Exception as err:
                    with open("errors.log", "a") as errors_file:
                        errors_file.write(traceback.format_exc() + "\n")
                    count += 1
                    print(RED_COLOR + "Error Trying To Write Data '%s' To Offset '%s', Trying Again" %
                          (str(fru_data[i]), str(i)), RESET_STYLE_BLACK_BG)
                    ok = False
        else:
            count = 0
            ok = False
            while not ok:
                if count == 10:
                    print("\n\n\n--------------------------------------------------\n\n")
                    print(" " * 13 + RED_COLOR + "Couldn't Write To FRU" + RESET_STYLE_BLACK_BG)
                    print(RED_COLOR + "!!!!!!!!!!!! FRU Creation Failed !!!!!!!!!!!!!" + RESET_STYLE_BLACK_BG)
                    print("\n\n--------------------------------------------------\n\n\n")
                    time.sleep(3)
                    loop_main()
                    print(RESET_STYLE)
                    exit()
                try:
                    if i < 256:
                        bus.write_byte_data(smbus_device_id1, i, 255)
                        print(ALL_COLORS[random.randint(0, len(ALL_COLORS) - 1)] + "-" + RESET_STYLE_BLACK_BG, end="")
                        ok = True
                    else:
                        if actual_mem_size == 512:
                            bus.write_byte_data(smbus_device_id2, i, 255)
                            print(ALL_COLORS[random.randint(0, len(ALL_COLORS) - 1)] + "-" + RESET_STYLE_BLACK_BG, end="")
                            ok = True
                except Exception as err:
                    with open("errors.log", "a") as errors_file:
                        errors_file.write(traceback.format_exc() + "\n")
                    count += 1
                    print(RED_COLOR + "Error Trying To Write Data '%s' To Offset '%s', Trying Again" %
                          (str(255), str(i)), RESET_STYLE_BLACK_BG)
                    ok = False
        count_to_go_row_down -= 1
    print()
    # close the smbus
    bus.close()
    print(GREEN_COLOR + "Finished Writing To HOST FRU" + RESET_STYLE_BLACK_BG + "\n")
    if config_file != 'non':
        print("\n\nPrinting Current Data In FRU\n\n")
        time.sleep(2)
        print_123(file_name=file_name, read_from_fru=False)


def write_to_host_and_bmc_fru(file_name="onie_eeprom", config_file="333"):
    """
    writes the data in file_name to the host fru and to the bmc fru
    :param file_name: the name of the file that has the FRU data, only the file name, no need for extention
    :type file_name: str
    """
    if file_name.endswith(".bin"):
        file_name = file_name[:-4]

    # Write to FRUs
    try:
        with open(file_name + ".bin", "rb") as file:
            fru_data = file.read()
    except OSError as err:
        print(RED_COLOR + traceback.format_exc() + RESET_STYLE_BLACK_BG)
        print(RED_COLOR + "Couldn't Open the File '%s'" % file_name, RESET_STYLE_BLACK_BG)
        time.sleep(3)
        loop_main()
        print(RESET_STYLE)
        exit()
    # HOST
    write_to_host_fru(file_name=file_name, fru_data=fru_data, config_file=config_file)


def get_list_of_bin_or_txt_files_in_current_dir(file_type, sub_dir=""):
    """ Return A List Of All Bin or TXT Files In Current Directory
    :param file_type: can be ".bin" or ".txt"
    :type file_type: str
    :return: list of all bin or TXT file in current dir
    :rtype list: (of str)
    """
    process = subprocess.Popen(["pwd"], stdout=subprocess.PIPE)
    output, error = process.communicate()
    path = output.decode()
    path = path.split("\n")[0]
    path = path + sub_dir
    # print(path)
    process = subprocess.Popen(["ls", "-l", "%s" % path], stdout=subprocess.PIPE)
    output, error = process.communicate()
    output_lines = output.decode().split("\n")
    bin_or_txt_files = []
    for line in output_lines:
        file_name = line.split(" ")[-1]
        if file_name.endswith(file_type):
            bin_or_txt_files.append(path + "/" + file_name)
    # print("bin_or_txt_files=", bin_or_txt_files)
    return bin_or_txt_files


def print_list_of_bin_or_txt_files_and_ask_user_to_chose(file_type, sub_dir):
    """ Prints A List Of Bin or Txt Files And Asks The User To Choose One
    param file_type: can be "bin" or "txt"
    :type file_type: str
    :return: the chosen file name
    :rtype: str
    """
    files = get_list_of_bin_or_txt_files_in_current_dir("." + file_type, sub_dir)
    # print(files)
    if not files:  # if there are no bin file in current dir
        print(RED_COLOR + "There Are No %s Files In Current Dir." % file_type + RESET_STYLE_BLACK_BG)
        return True
    files_index_list = []
    print("%s Files In Current Directory:\n" % file_type)
    for file in files:
        #print(str(files.index(file) + 1) + ". " + file)
        print(str(files.index(file) + 1) + ". "  + file.split("/")[-1] + RESET_STYLE_BLACK_BG)  # Modified to print only the file name

        files_index_list.append(str(files.index(file) + 1))
    print("\n\n")
    ok = False
    while not ok:
        file_number = input(YELLOW_COLOR + "Please Enter The Desired File Number: " + RESET_STYLE)

        if len(files) >= int(file_number) and file_number in files_index_list:
            file_name = files[int(file_number) - 1]
            ok = True
        else:
            print(RED_COLOR + "Please Enter A Number That Is In The List." + RESET_STYLE_BLACK_BG)
    return file_name


def is_valid_mac_address(mac_address):
    """
        Check if the given string is a valid MAC address.

        This function utilizes a regular expression to verify if the provided string adheres to the
         standard MAC address format.
        A valid MAC address consists of exactly 12 hexadecimal digits (0-9, a-f, A-F).

        Parameters:
        - mac_address (str): The string to be checked as a MAC address.

        Returns:
        - bool: True if the string is a valid MAC address, False otherwise.

        """
    # Use a regular expression to check if the MAC address has exactly 12 hex digits
    pattern = re.compile(r'^[0-9a-fA-F]{12}$')
    return bool(pattern.match(str(mac_address)))


def is_valid_serial_number(serial_number):
    pattern = re.compile(r'^[0-9a-zA-Z]{10}$')
    return bool(pattern.match(str(serial_number)))

def is_valid_chasiss_type(chasiss_type):
    return bool(re.fullmatch(r"^0x[0-9A-Fa-f]{1,2}$", chasiss_type))


def is_valid_wake_up_type(chasiss_type):
    return bool(re.fullmatch(r"^0x[0-9A-Fa-f]{1,2}$", chasiss_type))


def is_valid_number_of_mac(mac_num):
    pattern = r"^(?!0\d+$)(?:6553[0-5]|655[0-2]\d|65[0-4]\d{2}|6[0-4]\d{3}|[1-5]\d{0,4})$"
    return bool(re.match(pattern, mac_num))


def is_valid_TN(tracking_number):
    pattern = re.compile(r'^[0-9a-zA-Z]{13}$')
    return bool(pattern.match(str(tracking_number)))


def is_valid_IMEI(IMEI_number):
    pattern = re.compile(r'^\d{15}$')
    return bool(pattern.match(str(IMEI_number)))


def is_valid_version(version):
    pattern = re.compile(r'^[0-9a-zA-Z]{4}$')
    return bool(pattern.match(str(version)))


def is_valid_datetime(date_string):
    # Regular expression for the format MM/DD/YYYY HH:NN:SS
    pattern = re.compile(r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$')

    if not pattern.match(date_string):
        return False

    # Try to parse the date string using datetime
    try:
        datetime.strptime(date_string, '%m/%d/%Y %H:%M:%S')
        return True
    except ValueError:
        return False


def create_dic(file_name="xxx"):
    """

    :param file_name:
    :return:
    """
    global actual_mem_size


    data_dict = OrderedDict()

    with open(file_name, 'r') as file:
        for line in file:

            # Skip empty lines
            if not line.strip():
                continue

            # Skip lines that start with #
            if line.startswith('#'):
                continue

            # Split the line into words
            words = line.strip().split()

            # Check if there are at least two words (key and at least one value)
            if len(words) >= 2:
                key = (words[0]).lower()  # convert the key to lowercase
                values = words[1:]
            else:
                key = words[0]
                if key == '0x25' or key == '0x54':
                    if key == '0x25':
                        values = [datetime.now().strftime("%m/%d/%Y %H:%M:%S")]


                    # UUID
                    if key == '0x54':
                        uuid_bytes = subprocess.check_output(["uuidgen", "-r"])
                        # Decode bytes to string and remove hyphens
                        values = [uuid_bytes.decode().strip().replace("-", "")]
                        #print("UUID =", values)







                else:
                    data_ok = False
                    while data_ok == False:
                        values = [input(YELLOW_COLOR + f"Enter Data for the " + RESET_STYLE + GREEN_COLOR +
                                        f" {CODES_MEANING[key[2:]]}" + RESET_STYLE)]
                        if key == '0x24':
                            if not is_valid_mac_address(str(values[0])):
                                print(RED_COLOR + f"Wrong MAC Address Format,"
                                                  f" Should be 12 chars 0-9 A-F Please try again:\n" + RESET_STYLE)
                                data_ok = False
                                continue

                        if key == '0x23' or key == '0x53' or key == '0x5c' :
                            if not is_valid_serial_number(str(values[0])):
                                print(RED_COLOR + f"Wrong Serial number Format, "
                                                  f"Should be 10 Digits, Please try again:\n" + RESET_STYLE)
                                data_ok = False
                                continue
                            else:
                                data_ok =True

                        if key == '0x27' or key == '0x81':
                            if not is_valid_version(str(values[0])):
                                print(RED_COLOR + f"Wrong Version Format in filed {key} , {CODES_MEANING[key[2:]]},"
                                                  f" Should be 4 Characters, Please try again:\n" + RESET_STYLE)
                                data_ok = False
                                continue
                            else:
                                data_ok = True

                        if key == '0x2a':
                            if not is_valid_number_of_mac(str(values[0])):

                            #if not 1 <= int(values[0]) <= 65535:

                                print(RED_COLOR + f"Wrong Format in filed {key}  {CODES_MEANING[key[2:]]},"
                                                  f" Number must be between 1 and 65535, "
                                                  f"Please try again:\n" + RESET_STYLE)
                                data_ok = False
                                continue
                            else:
                                data_ok = True

                        if key == '0x82' or key == '0x86' or key == '0x87': # or key == '0x5c':
                            if not is_valid_TN(str(values[0])):
                                print(RED_COLOR + f"Wrong Tracking number Format in filed {key},"
                                                  f" {CODES_MEANING[key[2:]]},"
                                                  f" Should be 13 Digits, Please try again:\n" + RESET_STYLE)
                                data_ok = False
                                continue
                            else:
                                data_ok =True

                        if key == "0x83" or key == "0x84":
                            if not is_valid_IMEI(str(values[0])):
                                print(
                                    RED_COLOR + f"Wrong IMEI len for {key} , {CODES_MEANING[key[2:]]},"
                                                f"  should be 15 char" + RESET_STYLE)
                                data_ok = False
                                continue
                            else:
                                data_ok = True

                        data_ok = True

                # Add key-value pair to the OrderedDict

            data_dict[key] = values
            if key == 'actual_mem_size':
                actual_mem_size = int(values [0])
                print(values)
                data_dict.pop('actual_mem_size')
                print("actual_mem_size=", actual_mem_size)
    #print(data_dict)

    return data_dict


def read_config_file(config_file, burn=False):
    """ Read the fru_config.txt and create bin file according to the config file + burn the FRU
        :params file_name
        :type: file_name:
            :rtype: str
    """
    global os_clear
    if os_clear:
        os.system("clear")
    if config_file.endswith(".bin"):
        file_name = config_file[:-4]
    print("config_file=", config_file)
    result_dict = create_dic(config_file)
    print(GREEN_COLOR + "Building The Bin file ." + RESET_STYLE_BLACK_BG + "\n")

    # for supported_code in ["21", "22", "23", "24", "25", "27", "2a", "2b", "2c", "2d", "fd"]:
    fru_data_list = []
    header_string = HEADER_STRING
    header_version = HEADER_VERSION
    new_data_len = 0
    fru_data_list.append(header_string)  # index 0
    fru_data_list.append(header_version)  # index 1
    # the 2 bytes of the data len (zero for now)
    fru_data_list.append(b"\x00\x00")  # index 2

    for key in result_dict:
        if key == '0xfd':
            break

        if key == "0x25":

            if not is_valid_datetime(str(' '.join(result_dict.get("0x25")))):
                print(
                    RED_COLOR + f"Wrong DATE Format in filed {key} , {CODES_MEANING[key[2:]]},"
                                f" Should MM/DD/YYYY HH:NN:SS" + RESET_STYLE)
                sys.exit(1)
            else:
                manufacture_date = str(' '.join(result_dict.get("0x25")))
                fru_data_list.append(b"\x25\x13" + manufacture_date.encode())  # index 9
                new_data_len += 2 + 19
                continue

        if key == '0x27' or key == '0x81':
            if not is_valid_version(str(result_dict[key][0])):
                print(
                    RED_COLOR + f"Wrong Version Format in filed {key} ,"
                                f" {CODES_MEANING[key[2:]]}, Should be 4 Characters, Please try again:\n" + RESET_STYLE)
                sys.exit(1)

        if key == '0x58':
            value = result_dict.get(key)
            value = (value[0])

            if is_valid_wake_up_type(str(value)):
                # if 1 <= value <= 65535:
                # Convert the number to hexadecimal and represent it as a 2-byte number

                value = int(value, 16)
                hex_representation = value.to_bytes(1, byteorder='big')
                # print("hex_representation" , hex_representation)

                # Convert the key to bytes
                hex_value_key = int(key, 16)
                binary_value_key = bytes([hex_value_key])
                # print(binary_value_key)

                # Get the length of the hexadecimal representation
                hex_len = len(hex_representation)
                # print(hex_len)
                # Append the binary key, length, and hexadecimal representation to the fru_data_list
                fru_data_list.append(binary_value_key + hex_len.to_bytes(1, "big") + hex_representation)

                # Update the length of the code leng byte + new data
                new_data_len += 2 + len(hex_representation)
                continue

            else:
                print(RED_COLOR + f"Wrong Format in filed {key} {CODES_MEANING[key[2:]]},"
                                  f" Number must be 1 byte HEX format 0x ), "
                                  f"Please try again:\n" + RESET_STYLE)
                sys.exit(1)


        if key == '0x62':
            value = result_dict.get(key)
            value = (value[0])

            if is_valid_chasiss_type(str(value)):
                # if 1 <= value <= 65535:
                # Convert the number to hexadecimal and represent it as a 2-byte number

                value =int(value ,16)
                #print("value2" , value)
                hex_representation = value.to_bytes(1, byteorder='big')
                #print("hex_representation" , hex_representation)

                # Convert the key to bytes
                hex_value_key = int(key, 16)
                binary_value_key = bytes([hex_value_key])
                #print(binary_value_key)

                # Get the length of the hexadecimal representation
                hex_len = len(hex_representation)
                #print(hex_len)
                # Append the binary key, length, and hexadecimal representation to the fru_data_list
                fru_data_list.append(binary_value_key + hex_len.to_bytes(1, "big") + hex_representation)

                # Update the length of the code leng byte + new data
                new_data_len += 2 + len(hex_representation)
                continue

            else:
                print(RED_COLOR + f"Wrong Format in filed {key} {CODES_MEANING[key[2:]]},"
                                  f" Number must be 1 bytes HEX format 0x (x17 for Rackmount and  0x3 for Desktop ), "
                                  f"Please try again:\n" + RESET_STYLE)
                sys.exit(1)



        if key == '0x82' or key == '0x86' or key == '0x87': # or key == '0x5c':
            if not is_valid_TN(str(result_dict[key][0])):
                print(RED_COLOR + f"Wrong Tracking number Format in filed {key} ,"
                                  f" {CODES_MEANING[key[2:]]}, Should be 13 Digits" + RESET_STYLE)
                sys.exit(1)

        # verify Serial number format ####
        if key == "0x23" or key == '0x53' or key == '0x5c':
            if not is_valid_serial_number(str(result_dict[key][0])):
                print(RED_COLOR + f"The Config File Include a Wrong Serial number Format\n" + RESET_STYLE)
                sys.exit(1)

        # verify MAC address format ####

        if key == "0x24":

            if not is_valid_mac_address(str(result_dict[key][0])):
               print(RED_COLOR + f"The Config File Include a Wrong MAC Address Format\n" + RESET_STYLE)
            #   sys.exit(1)

        # number of MAC - convert to hex and set it as 2  bytes
        if key == '0x2a':
            value = result_dict.get(key)
            value = (value[0])
            if is_valid_number_of_mac(str(value)):
            #if 1 <= value <= 65535:
                # Convert the number to hexadecimal and represent it as a 2-byte number
                value = int(value[0])
                hex_representation = value.to_bytes(2, byteorder='big')

                # Convert the key to bytes
                hex_value_key = int(key, 16)
                binary_value_key = bytes([hex_value_key])

                # Get the length of the hexadecimal representation
                hex_len = len(hex_representation)

                # Append the binary key, length, and hexadecimal representation to the fru_data_list
                fru_data_list.append(binary_value_key + hex_len.to_bytes(1, "big") + hex_representation)

                # Update the length of the code leng byte + new data
                new_data_len += 2 + len(hex_representation)
                continue

            else:
                print(RED_COLOR + f"Wrong Format in filed {key} {CODES_MEANING[key[2:]]},"
                                  f" Number must be between 1 and 65535, "
                                  f"Please try again:\n" + RESET_STYLE)
                sys.exit(1)

        if key == "0x24" or key == "0x54" or key == "0x83" or key == "0x84":
            # all other FD values that are hex
            value = (result_dict.get(key))
            value = value[0]
            if key == "0x83" or key == "0x84":
                if not is_valid_IMEI(str(result_dict[key][0])):

                    print(RED_COLOR + f"Wrong IMEI len for {key} ,"
                                      f" {CODES_MEANING[key[2:]]},  should be 15 char actual {len(value)}")
                    sys.exit(1)
                else:
                    value = value.zfill(16)
            # convert key to integer and interpreting it as a hexadecimal number
            hex_value_key = int(key, 16)
            # Convert the integer value to a single-byte bytes object
            binary_value_key = bytes([hex_value_key])
            value_integer = int(value, 16)  # Convert the string to an integer
            # print(mac_integer)
            new_value = value_integer.to_bytes(int(len(value) / 2), "big")  # Convert the integer to bytes

            fru_data_list.append(binary_value_key + len(new_value).to_bytes(1, "big") + new_value)
            new_data_len += 2 + (len(value) / 2)
            continue

        # All other keys that are ASCIIe
        value = (result_dict.get(key))
        value = value[0]
        # convert key to integer and interpreting it as a hexadecimal number
        hex_value_key = int(key, 16)
        # Convert the integer value to a single-byte bytes object
        binary_value_key = bytes([hex_value_key])
        fru_data_list.append(binary_value_key + len(value.encode()).to_bytes(1, "big") + value.encode())  # index 3
        new_data_len += 2 + len(value.encode())

    # ###   for FD and all other keys after FD #######
    # start_loop = False
    # fru_data_list.append(b"\xfd")
    # new_data_len += 1
    # fd_data_len_in = int(float(fd_data_len)).to_bytes(1, "big")
    # fru_data_list.append(fd_data_len_in)
    # fru_data_list.append(
    #    len(IANA_CODE_OF_SILICOM).to_bytes(1, "big") + IANA_CODE_OF_SILICOM)  # IANA code of Silicom
    # new_data_len += 1 + len(IANA_CODE_OF_SILICOM)
    # fru_data_list.extend(fd_vendor_extension)  # index 13
    fru_data_list.append(b"\xfe\x04")  # index 14
    new_data_len += 2 + 4    # b"\xfe\x04 + checksum
    new_data_len = int(new_data_len)
    fru_data_list[2] = new_data_len.to_bytes(2, "big")
    fru_data = b"".join(fru_data_list)
    # create backup file with all the data ()
    if not os.path.isdir("FRU_Backup_files"):
        os.mkdir("FRU_Backup_files")
    file_name = "fru_" + datetime.now().strftime("%m.%d.%Y__%H_%M_%S") + ".bin"
    file_path = os.path.join("FRU_Backup_files", file_name)
    # current_directory = os.getcwd()
    # write data to file and read from file (the data changes)
    with open(file_path, "wb") as file:
        file.write(fru_data)
    with open(file_path, "rb") as file:
        data = file.read()
    # calculate the checksum
    checksum = binascii.crc32(data)
    checksum = checksum.to_bytes(4, "big")
    data += checksum
    # write data to file with the checksum
    with open(file_path, "wb") as file:
        file.write(data)

    # write data to host and bmc FRUs
    if burn:
        # file_ready = True
        write_to_host_and_bmc_fru(file_name=f"FRU_Backup_files/{file_name}",
                                  config_file=config_file)

    else:
        # file_ready = True
        # os.system('clear')
        print(GREEN_COLOR + f"A binary file has been generated and saved at the"
                            f" following location: FRU_Backup_files/{file_name}" + RESET_STYLE_BLACK_BG + "\n")
        # print_config_fru_file_data(file_name=file_path, read_from_fru=False, config_file=config_file)
        print_123(file_name=file_path, read_from_fru=False)
    return


def ask_what_to_do_and_call_the_right_func():
    """ asks the user what to do """
    global os_clear
    print(CYAN_COLOR + "Script Version: '%s'" % SCRIPT_VERSION + RESET_STYLE_BLACK_BG)

    what_to_do = input("1. Create a Bin File Based On fru_config.txt File data\n"
                       "2. Program Fru Based On The Data In the fru_config.txt File \n"
                       "3. Display The Information Stored In Fru Backup File \n"
                       "4. Program a Bin File To Host Fru\n"
                       "5. Display Hex output of the Data Stored In The Fru\n"
                       "6. Display Hex output of Data stored In a Backup Bin File \n"
                       "7. Create a Bin File From The Data Stored In The FRU)\n"
                       "8. Change a field on the HOST Fru\n\n" 


                       "Mode = ")
    # delete input line and rewrite to add ' before and after the input
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    # check user input
    if what_to_do in [str(i) for i in range(1, 9)]:
        print(GREEN_COLOR + "Mode = '%s'." % what_to_do + RESET_STYLE_BLACK_BG + "\n\n")
    else:
        print(RED_COLOR + "Unknown Mode '%s'." % what_to_do + RESET_STYLE_BLACK_BG + "\n\n")
    # call the function that does what the user wants

    if what_to_do == "7":  # create a file of the fru
        output_file_name = output_fru_data_to_bin_file(file_name="take system time")
        print(GREEN_COLOR + "FRU Data Has Been Dumped To '%s'" % output_file_name, RESET_STYLE_BLACK_BG)
        print_123(file_name=output_file_name, read_from_fru=False)

        return True
    elif what_to_do == "3":  # print fru data of desired file
        file_name = print_list_of_bin_or_txt_files_and_ask_user_to_chose(file_type='bin', sub_dir='/FRU_Backup_files')
        print_123(file_name=file_name, read_from_fru=False)
        return True
    elif what_to_do == "8":  # print fru data of desired file
        print(CYAN_COLOR + f"Reading The Current DATA Stored In The FRU\n" + RESET_STYLE)
        output_file_name = output_fru_data_to_bin_file(file_name="take system time")
        recoverd_dict = print_123(file_name=output_file_name, read_from_fru=False)
        new_dict, burn = update_data_dict(recoverd_dict)
        if burn:
            file_path = backup_config_file(new_dict)
            print(GREEN_COLOR + "\n\n     ***** Burning the FRU With The Newly Modified Fields *****\n" + RESET_STYLE)
            os_clear = False
            read_config_file(file_path, True)
        else:
            print(GREEN_COLOR + "No Field Was Modified ")

        return True
    elif what_to_do == "4":  # program desired file to host fru
        file_name = print_list_of_bin_or_txt_files_and_ask_user_to_chose(file_type='bin', sub_dir='/FRU_Backup_files')
        with open(file_name, "rb") as file:
            fru_data = file.read()
        write_to_host_fru(fru_data=fru_data)
        #####
        print(YELLOW_COLOR + "**************************************************************************" + RESET_STYLE)
        print(YELLOW_COLOR + "Validate the written data by comparing the FRU with the original binary file" + RESET_STYLE)
        print(YELLOW_COLOR + "**************************************************************************\n" + RESET_STYLE)

        output_file_name = output_fru_data_to_bin_file(file_name="compare_write")
        print(GREEN_COLOR + "FRU Data Has Been Dumped To '%s'" % output_file_name, RESET_STYLE_BLACK_BG)
        print_123(file_name=output_file_name, read_from_fru=False)
        if compare_bin_files(output_file_name , file_name):
            print(GREEN_COLOR + "******************************************************" + RESET_STYLE)
            print(GREEN_COLOR + "FRU programming and comparison completed successfully." + RESET_STYLE)
            print(GREEN_COLOR + "******************************************************" + RESET_STYLE)

        else:
            print(RED_COLOR + "*****************************" + RESET_STYLE)
            print(RED_COLOR + "ERRR - FRU compare was failed" + RESET_STYLE)
            print(RED_COLOR + "*****************************" + RESET_STYLE)




        return True
    elif what_to_do == "5":
        print_fru_file_in_hex()
        return True
    elif what_to_do == "6":
        file_name = print_list_of_bin_or_txt_files_and_ask_user_to_chose(file_type='bin', sub_dir='/FRU_Backup_files')
        print_fru_file_in_hex(read_from_fru=False, file_name=file_name)
        return True
    elif what_to_do == "2":
        file_name = print_list_of_bin_or_txt_files_and_ask_user_to_chose(file_type='txt', sub_dir="")
        read_config_file(file_name, True)
        return True
    elif what_to_do == "1":
        file_name = print_list_of_bin_or_txt_files_and_ask_user_to_chose(file_type='txt', sub_dir="")
        read_config_file(file_name, False)
        return True

    return False


def print_123(verbose=True, file_name="onie_eeprom", read_from_fru=True):
    """
    prints the fru data from the file_name.bin file
    :param verbose: print everything or just return the codes and codes_data from the file
    :param file_name: the name of the file to read the data from (and possibly out put the fru data to)
    :param read_from_fru: output data from fru or read directly from a file
    :type verbose: bool
    :type file_name: str
    :type read_from_fru: bool
    :return: a tuple of 2 lists, the first list contains all the fields codes, the second list contains all the fields
             data (in the same order as the first list)
    :rtype: tuple (of 2 lists that contain str)
    """
    recover_dict = {}
    checksum_in_fru = None
    checksum_should_be = 0
    codes = []
    codes_data = []
    if file_name.endswith(".bin"):
        file_name = file_name[:-4]
    if read_from_fru:
        output_file_name = output_fru_data_to_bin_file(file_name=file_name, verbose=verbose)
    else:
        if os.path.isfile(file_name + ".bin"):
            output_file_name = file_name
        else:
            print(RED_COLOR + "ERROR File Doesn't Exist" + RESET_STYLE_BLACK_BG)
            time.sleep(3)
            loop_main()
            print(RESET_STYLE)
            exit()
    # open the file with the fru data
    with open(output_file_name + ".bin", "rb") as file:
        data = file.read()
    if not len(data) >= 11:
        print(RED_COLOR + "FRU File Isn't Valid." + RESET_STYLE_BLACK_BG)
        time.sleep(3)
        loop_main()
        print(RESET_STYLE)
        exit()
    # get ID String and check
    index = 0
    id_string = data[index:index + 8]
    index += 8
    is_id_string_ok = id_string == HEADER_STRING
    if is_id_string_ok:
        if verbose:
            print(GREEN_COLOR + "ID String - OK" + RESET_STYLE_BLACK_BG)
    else:
        print(RED_COLOR + "ID String - Not Ok" + RESET_STYLE_BLACK_BG)
        time.sleep(3)
        loop_main()
        print(RESET_STYLE)
        exit()
    # get Header Version and check
    header_version = data[index:index + 1]
    index += 1
    is_header_version_ok = header_version == HEADER_VERSION
    if is_header_version_ok:
        if verbose:
            print(GREEN_COLOR + "Header Version - OK" + RESET_STYLE_BLACK_BG)
    else:
        print(RED_COLOR + "Header Version - Not Ok" + RESET_STYLE_BLACK_BG)
        time.sleep(3)
        loop_main()
        print(RESET_STYLE)
        exit()
    data_len = 0
    # get data len in hex from the data that we read
    data_len_hex_msb = str(hex(data[index]))[2:]  # get the hex number
    index += 1
    data_len_hex_lsb = str(hex(data[index]))[2:]  # get the hex number
    index += 1
    # if the hex number is 0x9 for example it will become 9
    if len(data_len_hex_lsb) == 1:
        data_len_hex_lsb = "0" + data_len_hex_lsb
    if len(data_len_hex_msb) == 1:
        data_len_hex_msb = "0" + data_len_hex_msb
    # convert data len to decimal

    data_len = ((int(data_len_hex_lsb, 16) & 0xFF) + ((int(data_len_hex_msb, 16) & 0xFF) << 8))

    if len(data) > data_len + 11:
        checksum_should_be = binascii.crc32(data[:data_len + 11 - 4])
    elif len(data) == data_len + 11:
        checksum_should_be = binascii.crc32(data[:-4])
    else:
        print(RED_COLOR + "Erorr Getting File Checksum." + RESET_STYLE_BLACK_BG)
        time.sleep(3)
        loop_main()
        print(RESET_STYLE)
        exit()
    if verbose:
        print("-" * 73)
        print(" " * 3 + "Code Meaning" + " " * 7 + "|     " + "Code" + "     |" + " " * 9 + "Data" + " " * 24 + "|")
        print()
    while index - 8 - 1 - 2 < data_len:
        code = data[index:index + 1].hex()
        index += 1
        if code not in ALLOWED_CODES or code not in CODES_MEANING:
            print("Unknown Code '%s'." % code)
            time.sleep(3)
            loop_main()
            print(RESET_STYLE)
            exit()
        code_meaning = CODES_MEANING[code]
        if verbose:
            if code == "fd":  # if code == "fd" add row space
                print()
            print(code_meaning, end="")
            print(" " * (22 - len(code_meaning)), end="|      ")
            print(code, end="")
            print(" " * 7, end="|    ")
            if code == "fd":  # if code == "fd" skip data in this row as the data will be printed in multiple rows
                print(" " * 22 + "|\n")
        else:
            codes.append(code)
        if code in ALLOWED_CODES:
            pass
        elif code in NOT_ALLOWED_CODES:
            print(RED_COLOR + "EEPROM data isn't valid" + RESET_STYLE_BLACK_BG)
            time.sleep(3)
            loop_main()
            print(RESET_STYLE)
            exit()
        else:
            print(RED_COLOR + "Unrecognized code at position %d, code =" % (index - 1), code, RESET_STYLE_BLACK_BG)
            time.sleep(3)
            loop_main()
            print(RESET_STYLE)
            exit()
        ok = False
        if code is None:
            pass
        elif code in ALLOWED_CODES:
            ok = True
            len_of_current_field_hex = data[index:index + 1].hex()
            index += 1

            len_of_current_field_decimal = int(len_of_current_field_hex, 16)

        else:
            print(RED_COLOR + "EEPROM data isn't valid" + RESET_STYLE_BLACK_BG)
            time.sleep(3)
            loop_main()
            print(RESET_STYLE)
            exit()
        if ok:
            field_data = data[index:index + len_of_current_field_decimal]
            index += len_of_current_field_decimal
            if code == "24" or code == "54"  or code == "58" or code == "83" or code == "84" or code == "62":
                if verbose:
                    print(field_data.hex().upper() + " " * (32 - len(field_data.hex().upper())) + "|")
                    if code == '83':
                        IMEI = field_data.hex().upper()
                        IMEI_fixed = IMEI[1:]
                        recover_dict.update({code: IMEI_fixed})
                    else:
                        recover_dict.update({code: field_data.hex().upper()})
                else:
                    codes_data.append(field_data.hex().upper())



            elif code == "2a":
                field_data = field_data.hex().upper()
                field_data = int(field_data, 16)

                if verbose:
                    field_data_str = str(field_data)  # Convert integer to string
                    print(field_data_str + " " * (32 - (len(field_data_str))) + "|")
                    recover_dict.update({code: field_data})
                else:
                    codes_data.append(field_data)
            elif code == "fd":
                if verbose:
                    line = field_data.hex()
                    for i in range(0, len(line), 60):
                        print(line[i:i + 60])

                else:
                    codes_data.append(field_data)
            elif code == "fe":
                if verbose:
                    print(field_data.hex().upper() + " " * (32 - len(field_data.hex().upper())) + "|")

                else:
                    codes_data.append(field_data.hex().upper())
                checksum_in_fru = field_data.hex().upper()
            elif code == "ff":
                break
            else:
                if verbose:
                    print(field_data.decode() + " " * (32 - len(field_data.decode())) + "|")
                    recover_dict.update({code: field_data.decode()})

                else:
                    codes_data.append(field_data.decode())
            if code in ["fd", "fe"]:  # ["22", "23", "24", "2c", "fd", "fe"]:
                if verbose:
                    print()
    if checksum_in_fru == hex(checksum_should_be)[2:].upper():
        is_checksum_correct = "Checksum is ok"
    else:
        is_checksum_correct = "Checksum is incorrect !!!!!!!!!!!!!!!!!!"
    if verbose:
        print("-" * 74)
        if "ok" not in is_checksum_correct:
            print("Checksum should be %s\n" % hex(checksum_should_be)[2:].upper() +
                  RED_COLOR + "%s" % is_checksum_correct + RESET_STYLE_BLACK_BG)
        else:
            print("Checksum should be %s\n" % hex(checksum_should_be)[2:].upper() +
                  GREEN_COLOR + "%s" % is_checksum_correct + RESET_STYLE_BLACK_BG)

    return recover_dict


def backup_config_file(data_dict):
    file_name = "fru_" + datetime.now().strftime("%m.%d.%Y__%H_%M_%S") + "_backup" + ".txt"
    file_path = os.path.join("FRU_Backup_files", file_name)

    with open(file_path, "w") as file:
        for key, data in data_dict.items():
            if key in ("0x58", "0x62") and not str(data).startswith("0x"):
                data = f"0x{data}"
            file.write(f"{key}  {data}\n")
    return file_path


def update_data_dict(recovered_dict):
    """
    THis function is used in case that the user would like to change a specific value within the FRU
    :param recovered_dict:
    :return:
    """
    # add 0x to the keys
    data_dict = {f"0x{key}": value for key, value in recovered_dict.items()}

    while True:
        # Ask the user which field to change
        #for key in data_dict.keys():
        #    print(key, end=' ')
        selected_key = input(YELLOW_COLOR + "Please select the code from the provided table"
                                            " for the field you'd like to modify:" + RESET_STYLE)
        selected_key = "0x" + selected_key.zfill(2)  # Add "0x" and ensure 2-digit format

        # Check if the selected key exists
        if (selected_key in data_dict) and (selected_key != '0x54'):

            data_ok = False
            while data_ok == False:



                new_data = input(YELLOW_COLOR + f"Enter Data for the " + RESET_STYLE + GREEN_COLOR +
                                 f" {CODES_MEANING[selected_key[2:]]}" + RESET_STYLE)




                if selected_key == '0x24':
                    if not is_valid_mac_address(str(new_data)):
                        print(
                            RED_COLOR + f"Wrong MAC Address Format,"
                                        f" Should be 12 chars 0-9 A-F Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue

                if selected_key == '0x23' or selected_key == '0x53' or selected_key == '0x5c':
                    if not is_valid_serial_number(str(new_data)):
                        print(
                            RED_COLOR + f"Wrong Serial number Format,"
                                        f" Should be 10 Digits, Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                if selected_key == '0x2a':
                    if not is_valid_number_of_mac(str(new_data)):
                    #if not 1 <= int(new_data) <= 65535:
                        print(
                            RED_COLOR + f"Wrong Format in filed {selected_key}  {CODES_MEANING[selected_key[2:]]},"
                                        f" Number must be between 1 and 65535, Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True





                if selected_key == '0x82' or selected_key == '0x86' or selected_key == '0x87': # or selected_key == '0x5c':
                    if not is_valid_TN(str(new_data)):
                        print(
                            RED_COLOR + f"Wrong Tracking number Format in filed {selected_key} , "
                                        f"{CODES_MEANING[selected_key[2:]]}, Should be 13 Digits,"
                                        f" Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                if selected_key == "0x83" or selected_key == "0x84":
                    if not is_valid_IMEI(str(new_data)):
                        print(
                            RED_COLOR + f"Wrong IMEI len for {selected_key} ,"
                                        f" {CODES_MEANING[selected_key[2:]]},  should be 15 char" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                data_ok = True

            # Update the data in the dictionary
            data_dict[selected_key] = new_data
            burn = True

        else:
            # UUID
            if selected_key == '0x54':
                print(
                    RED_COLOR + f"UUID is a system-generated field. Kindly choose an alternative code to modify:\n" + RESET_STYLE)
                if  burn:
                    pass
                else:
                    burn = False
            else:
                print(RED_COLOR + "Selected key does not exist in the file. Please try again." + RESET_STYLE)



        update_more = input(YELLOW_COLOR + "Do you want to update another key? (yes/no): " + RESET_STYLE).lower()
        if update_more != "yes":
            break
    return data_dict, burn


def main():
    try:

        time.sleep(0.5)
        ok = ask_what_to_do_and_call_the_right_func()
        while not ok:
            if os_clear:
                os.system("clear")
            time.sleep(0.5)

            ok = ask_what_to_do_and_call_the_right_func()
    except Exception as err:
        with open("errors.log", "a") as errors_file:
            errors_file.write(traceback.format_exc() + "\n")


def menu_or_exit():
    """ Asks The User If He/She Wants To Go Back To The Menu Or Exit """
    what_to_do2 = input(YELLOW_COLOR + "Type 'm' To Go Back To Menu.\n"
                        "Type 'e' To Exit.\n" + RESET_STYLE)
    while what_to_do2 not in ["m", "e"]:
        what_to_do2 = input(YELLOW_COLOR + "Type 'm' To Go Back To Menu.\n"
                            "Type 'e' To Exit.\n" + RESET_STYLE)
    if what_to_do2 == "m":
        if os_clear:
            os.system("clear")
    elif what_to_do2 == "e":
        return True
    return False


def loop_main():
    """ Keeps Calling The main Function Until The User Says He/She Wants To Quit """
    global i2c_bus_number
    global smbus_device_id
    print(CYAN_COLOR + "Script Version: '%s'" % SCRIPT_VERSION + RESET_STYLE_BLACK_BG)
    # get_i2c_bus_number_and_enable_access()
    # smbus_device_id = get_smbus_device_id()
    try:
        stop = False
        if os_clear:
            os.system("clear")
        while not stop:
            main()
            stop = menu_or_exit()
    except (Exception, KeyboardInterrupt) as err:
        with open("errors.log", "a") as errors_file:
            errors_file.write(traceback.format_exc() + "\n")


if __name__ == '__main__':

    print(RESET_STYLE_BLACK_BG, end="")
    if len(sys.argv) == 1:
        pass
    elif len(sys.argv) == 2:
        if sys.argv[1] in ["-v", "v", "--v", "V", "-V", "--V"]:
            if os_clear:
                os.system("clear")
            print(CYAN_COLOR + "Script Version:", SCRIPT_VERSION, RESET_STYLE)
            exit()
        elif sys.argv[1] in ["help", "-help", "--help"]:
            if os_clear:
                os.system("clear")
            print(YELLOW_COLOR + "To Run Normal:                ./ONIE_tools.py\n"
                                 "To View Script Version:       ./ONIE_tools.py -v\n"
                                 "To View This Help Screen:     ./ONIE_tools.py --help\n" + RESET_STYLE)
            exit()
        else:
            if os_clear:
                os.system("clear")
            print(RED_COLOR + "Unknown Option" + RESET_STYLE_BLACK_BG)
            time.sleep(8)
    elif len(sys.argv) == 3:
        if sys.argv[1] in ["-", "--"] and sys.argv[2] in ["v", "V"]:
            if os_clear:
                os.system("clear")
            print(CYAN_COLOR + "Script Version:", SCRIPT_VERSION, RESET_STYLE)
            exit()
        elif sys.argv[1] in ["c", "-c", "--c", "C", "-C", "--C"] and \
                sys.argv[2].lower() in ["off", "0"]:
            os_clear = False
        elif sys.argv[1] in ["-", "--"] and sys.argv[2].lower() == "help":
            if os_clear:
                os.system("clear")
            print(YELLOW_COLOR + "To Run Normal:                ./ONIE_tool.py\n"
                                 "To View Script Version:       ./ONIE_tool.py -v\n"
                                 "To View This Help Screen:     ./ONIE_tool.py --help\n" + RESET_STYLE)
            exit()
    elif len(sys.argv) == 4:
        if sys.argv[1] in ["-", "--"] and sys.argv[2].lower() in "c" and sys.argv[3].lower() in ["off", "0"]:
            os_clear = False
        else:
            if os_clear:
                os.system("clear")
            print(RED_COLOR + "Unknown Option" + RESET_STYLE_BLACK_BG)
            time.sleep(8)
    else:
        if os_clear:
            os.system("clear")
        print(RED_COLOR + "Unknown Option" + RESET_STYLE_BLACK_BG)
        time.sleep(8)
    try:
        loop_main()
    except (Exception, KeyboardInterrupt) as err:
        with open("errors.log", "a") as errors_file:
            errors_file.write(traceback.format_exc() + "\n")

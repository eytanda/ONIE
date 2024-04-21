# ONIE / FRU Tool

This utility writes/reads information to/from the FRU.
The fru_config.txt specifies the field and the data to be written to the FRU.
note:
1) if the configuration file contains a field without an assigned data value, the utility will prompt the user to input the value.
2) The tool also offers an option to modify data for a specific field.
3) If the 0x25 code(DATE)  is devoid of value, the utility adds the Host current date and time 
4) Leave the 0x54 (UUID) devoid of value the utility calculates the UUID value
5) The utility default FRU memory size is 512. It can be  modified to 256 by adding the line "actual_mem_size 256" to the fru_config.txt file


## Below are the available options:



1. Create a Bin File Based On fru_config.txt File data
2. Program Fru Based On The Data In the fru_config.txt File
3. Display The Information Stored In Fru Backup File
4. Program a Bin File To Host Fru
5. Display Hex output of the Data Stored In The Fru
6. Display Hex output of Data stored In a Backup Bin File
7. Create a Bin File From The Data Stored In The FRU)
8. Change a field on the HOST Fru

Mode =

## Example of the fru_config.txt file:

0x24 00E0ED123456
#######################################################################################
#### Leave the 0x25 code devoid of value, the utility add the Host current date and time
0x25  
#######################################################################################
0x27 R101
0x2a 120
0x2b Silicom
0x2c IL
0x2d Silicom
0x51 Silicom
0x52 90500-0171-G00
0x53 0123456789
#########################################################################
#### Leave the 0x54 devoid of value the utility calculate the UUID value
0x54
#########################################################################
0x55 R101
0x58 00
0x59 Silicom
0x5a 90300-0171-G00
0x5b R100
0x5c 1234567890123
0x5e Silicom
0x81 R001
0x82 123456789012R
0x83 123456789012312
# ONIE / FRU Tool

This utility writes/reads information to/from the FRU.
The fru_config.txt specifies the field and the data to be written to the FRU.
If the configuration file contains a field without an assigned data value, the utility will prompt the user to input the value.
The tool also offers an option to modify data for a specific field.
For the filed code 0x25 (Date), if no date is provided, it will default to the current date and time.
Below are the available options:



1. Create a Bin File Based On fru_config.txt File data
2. Program Fru Based On The Data In the fru_config.txt File
3. Display The Information Stored In Fru Backup File
4. Program a Bin File To Host Fru
5. Display Hex output of the Data Stored In The Fru
6. Display Hex output of Data stored In a Backup Bin File
7. Create a Bin File From The Data Stored In The FRU)
8. Change a field on the HOST Fru

Mode =

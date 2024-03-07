#!/bin/bash

# Script Name  : onie_eeprom_info.sh
# Description  : Convert the onie_eeprom [file] to readeble format
# autor        : igor Godgelf (igorg@silicom.co.il)
# date         : 18.12.2018
# version      : 1.5
# usage        : onie_eeprom_info.sh [<onie eeprom file>]
# notes        : the the 'cksfv' packet needs for CRC check 


help()
{
echo -e "\nusage        : onie_eeprom_info.sh [<onie eeprom file>]\n"
exit
}

pass()
{
echo -e "\033[1m\033[4G$1:\033[32m\033[20G$2\033[0m"
}
read_byte()
{
#echo -n start_byte=$start_byte end_byte=$end_byte
unset string
a=1
for i in $work_file
do
if [ "$a" -ge "$start_byte" ]; then
 if [ "$name" = "Vendor extension" ]; then
  string="$string $i"
 else
  string=$string$i
 fi
fi  
let a=a+1

[ "$a" -gt "$end_byte" ] && break
done
let start_byte=$end_byte+1
# echo " string=$string"
}

get_type_code()
{
case $1 in
21) name="Product name"; format=ascii ;;
22) name="Part number"; format=ascii ;;
23) name="Serial number"; format=ascii ;; 
24) name="Base MAC address"; format=hex ;;
25) name="Manufacture date"; format=ascii ;;
# 26) name="Device version"; format=ascii ;;
27) name="Label revision"; format=ascii ;;
28) name="Platform name"; format=ascii ;;
29) name="ONIE version"; format=ascii ;;
2a) name="MAC addresses"; format=dec;;
2b) name="Manufacturer"; format=ascii ;;
2c) name="Country code"; format=ascii ;;
2d) name="vendor name"; format=ascii ;;
2e) name="Diag version"; format=ascii ;;
2f) name="Service tag"; format=ascii ;;
fd) name="Vendor extension" ;;
fe) name="CRC-32"; format=hex ;;
ff) exit ;;
*) echo; echo -e "\033[31m Wrong type code $1!!!\033[0m"; exit ;;
esac
}

first_ven_ext()
{
echo -e "$type_code \033[4;1mVendor Extension Value:\033[0m"
n=1

for i in $string
do
field="${field}$i"
case $n in
4) field=`echo $field |tr [a-f] [A-F]`
   field=`echo " ibase=16; $field" |bc`
   if [ "$field" = "$xxx" ]; then
    pass "IANA" $field
   else
    fail "The IANA \"$field\" does not equal to \"$iana\"!"
   fi
   field="" ;;
8) field=`echo $field |xxd -p -r`
   pass "ONIE version" $field warning
   field="" ;;  
21) field=`echo $field |xxd -p -r`
    pass "CBT" $field
    field="" ;;    
34) field=`echo $field |xxd -p -r`
    pass "FPBT" $field
    field="" ;;
44)field=`echo $field |xxd -p -r`
    pass "FPBS" $field
    field="" ;;        
    
    
    
esac
let n=n+1
[ $n -gt $long ] && break
done
}
check_crc()
{
which cksfv > /dev/null || {
echo; echo -e "\033[31m please install \"cksfv\" utility\033[0m"
exit
}
# ************** CRC ************
echo "546c76496e666f0001${long_hex}${crc32_range}" |xxd -p -r > /tmp/file_crc32

file_CRC=$string

new_CRC=`cksfv -b /tmp/file_crc32 |tail -1 |awk '{print $2}' |tr A-Z a-z`
if [ "$file_CRC" = "$new_CRC" ]; then
echo -e "\033[1m$name:\033[20G\033[32m$new_CRC\033[0m"
else
echo -e "\033[1m$name:\033[20G\033[32m$new_CRC \033[31m$file_CRC\033[0m"
fi
exit
}
check_command()
{
which $1 > /dev/null
if [ "$?" != "0" ]; then
 echo
 echo -e "\033[31m The \"$1\" command is not found! \033[0m"
 exit
fi
}
# ###################### M A I N #########################################
echo

if [ -z $1 ]; then
 check_command i2cdetect
 check_command i2cget
 lsmod |grep -q i2c_i801 || modprobe i2c-i801
 lsmod |grep -q i2c_dev ||	modprobe i2c-dev

 i2c_bus=` i2cdetect -l |grep -i I801 |cut -d$'\t' -f 1 |cut -d "-" -f2`
 i2c_dev=0x54

 while :
 do
  i2cdetect -y $i2c_bus |grep -q " `echo $i2c_dev |cut -d 'x' -f2` "
  if [ $? -ne 0 ]; then
   echo -e "\n \033[31m Wrong i2c device address $i2c_dev\n \033[0m"
   read -p "please insert i2c device address: " i2c_dev
   echo $i2c_dev |grep -q 0x || i2c_dev=0x$i2c_dev  
  else
   break
  fi 
 done

 ls /tmp|grep -q file && rm -f /tmp/file
 for i in {0..255}
 do
  i2cget -y $i2c_bus $i2c_dev $i |cut -d "x" -f2 |xxd -p -r  >> /tmp/file
 done
 # work_file=`od -t x1 --endian=big /tmp/file |colrm 1 8`
 work_file=`od -t x1  /tmp/file |colrm 1 8`
 echo -e "\033[1mi2c_bus:\033[20G\0033[32m $i2c_bus\033[0m"
 echo -e "\033[1mi2c_dev:\033[20G\0033[32m $i2c_dev\033[0m"
else
 if [ "$1" = "help" ]; then
  help
 else 
 work_file=`od -t x1 $1 |colrm 1 8`
 fi
fi

start_byte=1
end_byte=9

read_byte     # read header
if [ "$string" != "546c76496e666f0001" ];then
 echo; echo -e "\033[31m Wrong file format $1\033[0m"
 exit
else
 echo -e "\033[1mID String:\033[20G\033[32m TlvInfo\033[0m"
 echo -e "\033[1mHeader Version:\033[20G\033[32m 01\033[0m"
fi

let end_byte=$start_byte+1
read_byte # 10 11 (long of file)

a=1
fe=0
long=0
# set -x
for i in $work_file #from 12 till "fe"
do
if [ "$a" -ge "$start_byte" ]; then
 if [ $fe -eq 1 ] && [ "$i" = "04" ]; then
  let long=long+1
  crc32_range="${crc32_range}$i"
  break 
 else
  if [ $i = "fe" ]; then
   fe=1
  fi  
  let long=long+1
  crc32_range="${crc32_range}$i"
 fi
fi
 let a=a+1 
done
# set +x
let long=long+4;  # echo long=$long              
printf -v long_hex "%x" $long; # echo long_hex=$long_hex; exit

while [ `echo $long_hex |wc -c` -lt 5 ]
do
long_hex=0$long_hex
done 
if [ "$string" != "$long_hex" ]; then
 echo -e "\033[1mTotal Length:\033[20G\0033[31m $string \033[32m$long_hex\033[0m"
else
 echo -e "\033[1mTotal Length:\033[20G\0033[32m $long_hex\033[0m"
fi

while :                            # main cycle
do
end_byte=$start_byte
read_byte                     # get type code
type_code=$string # ; echo type_code=$type_code
get_type_code $string
end_byte=$start_byte
read_byte                    #get length od field
string=`echo $string |tr a-z A-Z`
long=`echo " ibase=16; $string" |bc` # ; echo "long=$long; string=$string"
end_byte=$(($start_byte+$long-1))
read_byte                             # get content
[ "$type_code" = " fe" ] && check_crc
if [ "$type_code" = "fd" ]; then
xxx=`echo $string |sed 's/ //g' |cut -c 1-8`        # ; echo xxx=$xxx
string=${string#$xxx}                 # ; echo string=$string
xxx=`echo $xxx |tr a-z A-Z`           #  ; echo xxx=$xxx
 if [ "$xxx" = "00003D4E" ]; then
  xxx=`echo " ibase=16; $xxx" |bc`
 else
  echo; echo -e "\033[31m The Silicom IANA \($xxx\) is failed!!!\033[0m"
  exit
 fi
first_ven_ext
else
 if [ "$format" = "ascii" ]; then
  which xxd > /dev/null
   if [ "$?" != "0" ]; then
    echo -e "\n xxd command not found!"
    exit
   fi
  string=`echo $string |sed -e 's/^[0]*//g'|xxd -r -p` # " &> /dev/null
 elif [ "$format" = "dec" ]; then
  string=`echo $string |tr [a-f] [A-F]`
  string=`echo " ibase=16; $string" |bc`
 fi
 echo -e "$type_code \033[1m$name:\033[20G\0033[32m ${xxx}${string}\033[0m"
fi
done
echo

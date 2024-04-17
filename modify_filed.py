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


def update_data_dict(data_dict):
    while True:
        # Ask the user which field to change
        print("Fields available for update:")
        for key in data_dict.keys():
            print(key)
        selected_key = input("Enter the key you would like to change: ")

        # Check if the selected key exists
        if selected_key in data_dict:
            new_data = input("Enter the new data: ")

            data_ok = False
            while data_ok == False:
                values = [
                    input(f"Enter Data for the " + GREEN_COLOR + f" {CODES_MEANING[selected_key[2:]]}" + RESET_STYLE)]
                if selected_key == '0x24':
                    if not is_valid_mac_address(str(values[0])):
                        print(
                            RED_COLOR + f"Wrong MAC Address Format, Should be 12 chars 0-9 A-F Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue

                if selected_key == '0x23':
                    if not is_valid_serial_number(str(values[0])):
                        print(
                            RED_COLOR + f"Wrong Serial number Format, Should be 10 Digits, Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                if selected_key == '0x27' or selected_key == '0x81':
                    if not is_valid_version(str(values[0])):
                        print(
                            RED_COLOR + f"Wrong Version Format in filed {selected_key} , {CODES_MEANING[selected_key[2:]]}, Should be 4 Characters, Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                if selected_key == '0x82' or selected_key == '0x86' or selected_key == '0x87':
                    if not is_valid_TN(str(values[0])):
                        print(
                            RED_COLOR + f"Wrong Tracking number Format in filed {selected_key} , {CODES_MEANING[selected_key[2:]]}, Should be 13 Digits, Please try again:\n" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                if selected_key == "0x83" or selected_key == "0x84":
                    if not is_valid_IMEI(str(values[0])):
                        print(
                            RED_COLOR + f"Wrong IMEI len for {selected_key} , {CODES_MEANING[selected_key[2:]]},  should be 15 char" + RESET_STYLE)
                        data_ok = False
                        continue
                    else:
                        data_ok = True

                data_ok = True

            # Update the data in the dictionary
            data_dict[selected_key] = new_data
            print(data_dict)
            update_more = input("Do you want to update another key? (yes/no): ").lower()
            if update_more != "yes":
                break
        else:
            print("Selected key does not exist in the file. Please try again.")


# Example usage:
update_data(data_dict)

import re
import sys
import smtplib
from argparse import Namespace, ArgumentParser
from email.message import EmailMessage

EMAILS_TO_SEND = ['brojas@gemini.edu']


class ConfigurationError(Exception):
    """
    Raised when a syntax error is found in a configuration file.
    """
    pass


def search_duplicates(dict_tables):
    """
    Function that compare and search on dict_tables duplicate values and return on a new dict the duplicate values.
    :param dict_tables: Dictionary with the three steps values of each instrument on the lookup table.
    :type dict_tables: dict
    :return: Entries that has duplicate values on the lookup table
    :rtype: dict
    """
    duplicate_dict = {}

    for key, value in dict_tables.items():
        if tuple(value) not in duplicate_dict:
            duplicate_dict[tuple(value)] = [key]
        else:
            duplicate_dict[tuple(value)].append(key)

    return duplicate_dict


def create_dict_for_search_duplicates(instruments_list):
    """
    This function create an additional dictionary who has the three steps values of each instrument on the lookup table
    for compare later.
    :param instruments_list: A list with lines found inside agSeqPorts.pv.
    :type instruments_list: list
    :return: Dictionary with the three steps values of each instrument on the lookup table.
    :rtype: dict
    """
    instrument_dict = {}

    for line_instrument in instruments_list:

        value_list = []
        line_instrument_split = line_instrument.split()
        key = line_instrument_split[0]
        del line_instrument_split[0:2]

        for x in range(0, 8, 3):
            value_list.append(line_instrument_split[x])

        instrument_dict[key] = value_list

    return instrument_dict


def search_instruments(instruments_list, instruments_ports_list):
    """
    Function that search and check that each instrument and port associated to it, exist on the lookup table inside
    agSeqPorts.pv
    :param instruments_list: A list with lines found inside agSeqPorts.pv.
    :type instruments_list: list
    :param instruments_ports_list: The name of each instrument and the port where is it.
    :type instruments_ports_list: list
    :return: Instruments that could not be found on the lookup table
    :rtype: dict
    """
    finded_dict = {}

    for instrument_port in instruments_ports_list:
        key = ''
        value = ''
        for instrument in instruments_list:
            instrument_split = instrument.split()

            if 'gcal2' + instrument_port == instrument_split[0]:
                value = 'gcal2' + instrument_port
            elif instrument_port == instrument_split[0]:
                key = instrument_port

        if not key:
            finded_dict['emptyKey_' + instrument_port] = value
        else:
            finded_dict[key] = value

    return finded_dict


def rescue_port_and_instrument_name(ports_list):
    """
    Function that separate the number of each port and merge the name of the instrument with it. Also return an
    string in case that CANOPUS aren't in port 4.
    :param ports_list: List with the lines that contain the ports and the instrument associated to it.
    :type ports_list: list
    :return: The name of each instrument and the port where is it. Also return an string in case that
    CANOPUS aren't in port 4.
    :rtype: tuple
    """
    canopus_error = ''
    instrument_to_search_list = []
    for port_line in ports_list:
        port_line_list = port_line.split()
        number_port = (port_line_list[1])[-1].strip()
        instrument_name = port_line_list[3].replace('"', '').lower().strip()

        if not instrument_name + number_port == 'gcal2':
            if not number_port == '4':
                instrument_to_search_list.append(instrument_name + number_port)
            elif not instrument_name + number_port == 'canopus4':
                canopus_error = "CANOPUS it's not in port 4, instead it's '" + instrument_name + "'"

    return instrument_to_search_list, canopus_error


def read_configuration(file_name):
    """
    This function read the file that have the actual instruments that are already functioning on differents ports and
    read the file who has the lookup tables.
    :param file_name: The name of the path file who has the configuration.
    :type file_name: str
    :return: A list with lines found inside the configuration file.
    :rtype: list
    :raises: ConfigurationError
    """
    found_file_list = []
    f = open(file_name, 'r')

    for line in f:

        # Skip blank lines and comments
        line = line.strip()
        if not line:
            continue
        if re.search(r'^#', line):
            continue
        line_split_list = line.split()
        if len(line_split_list) >= 2:

            if re.search(r'port:port[1-5]', line_split_list[1]):
                found_file_list.append(line)

            elif line_split_list[1] == '3':
                found_file_list.append(line)

    f.close()

    if not found_file_list:
        raise ConfigurationError('ports and instruments lines missing')

    return found_file_list


def print_list(input_list):
    """
    Function that iterates over a list and print each element.
    :param input_list: list which wanna print.
    :type input_list: list
    """
    for element in input_list:
        print(element)


def get_arguments(argv):
    """
    Process command line arguments
    :param argv: command line arguments from sys.argv
    :type argv: list
    :return: command line arguments
    :rtype: Namespace
    """
    parser = ArgumentParser()

    parser.add_argument(action='store',
                        nargs='+',
                        dest='file_list',
                        default=[],
                        help='list of configuration files')

    return parser.parse_args(argv[1:])


def configure_email(instrument, duplicates):
    """
    This function iterates over the dictionaries for structure the message to send on each value found
    on the dictionaries
    :param instrument: Instruments that could not be found on the lookup table
    :type instrument: dict
    :param duplicates: Entries that has duplicate values on the lookup table
    :type duplicates: dict
    :return: Two strings that contain information about the issues. One, in case instruments could not be found
    on the lookup table. And other, in case there exist duplicate values.
    :rtype: tuple
    """
    duplicates_problems = ''
    instruments_problems = ''

    for key, value in instrument.items():
        empty_key = ''
        empty_value = ''
        if re.search('emptyKey_', key) or not value:
            if re.search('emptyKey_', key):
                empty_key_split = key.split('_')
                empty_key = empty_key_split[-1] + ' could not be found on the table' + '\n'
                if not value:
                    empty_value = 'gcal2' + empty_key_split[-1] + ' could not be found on the table' + '\n'
            elif not value:
                empty_value = 'gcal2' + key + ' could not be found on the table' + '\n'
            instruments_problems = instruments_problems + empty_key + empty_value

    for key, value in duplicates.items():
        if len(value) > 1:
            duplicates_problems = duplicates_problems + 'Entries ' + str(value) + ' has duplicate values: ' + str(
                key) + '\n'

    return instruments_problems, duplicates_problems


def format_to_send(instruments_problems, duplicates_problems, canopus_problems):
    """
    This function choose which format message will be send
    :param instruments_problems: The message of instruments that could not be found on the lookup table.
    :type instruments_problems: str
    :param duplicates_problems: The message of duplicates values on the lookup table.
    :type duplicates_problems: str
    :param canopus_problems: String in case that CANOPUS aren't in port 4
    :type canopus_problems: str
    """
    if instruments_problems and duplicates_problems:
        head_instruments = 'Instruments not found:' + "\n" + instruments_problems
        head_duplicates = 'Duplicates issues:' + "\n" + duplicates_problems

        if canopus_problems:
            head_canopus = 'Warning in port 4:' + "\n" + canopus_problems + "\n"
            content = head_canopus + "\n" + head_instruments + "\n" + head_duplicates
        else:
            content = head_instruments + "\n" + head_duplicates

        print_format(content)
        # send_email(content)

    elif instruments_problems and not duplicates_problems:
        head_instruments = 'Instruments not found:' + "\n" + instruments_problems

        if canopus_problems:
            head_canopus = 'Warning in port 4:' + "\n" + canopus_problems + "\n"
            content = head_canopus + "\n" + head_instruments
        else:
            content = head_instruments

        print_format(content)
        # send_email(content)

    elif not instruments_problems and duplicates_problems:
        head_duplicates = 'Duplicates issues:' + "\n" + duplicates_problems

        if canopus_problems:
            head_canopus = 'Warning in port 4:' + "\n" + canopus_problems + "\n"
            content = head_canopus + "\n" + head_duplicates
        else:
            content = head_duplicates

        print_format(content)
        # send_email(content)

    elif canopus_problems:
        head_canopus = 'Warning in port 4:' + "\n" + canopus_problems + "\n"
        print_format(head_canopus)
        # send_email(head_canopus)

    else:
        print('Issues not detected')


def print_format(content):
    """
    Function that print at the output the following format
    :param content: The content of the message
    :type content: str
    """
    print('---------------------------------------------------------------------------------')
    print('Issues detected in ag_sf.lut')
    print('---------------------------------------------------------------------------------')
    print(content)
    print('\n' + '\n' + 'NOTE: Please check each port with the instrument in agSeqPorts.pv')
    print('---------------------------------------------------------------------------------')


def send_email(content):
    """
    Function that send the email of the issues that were detected to a specifics persons.
    :param content: The content of the message
    :type content: str
    """
    for email in EMAILS_TO_SEND:
        print('Email send to ' + email)
        msg = EmailMessage()
        msg['Subject'] = 'Issues detected in ag_sf.lut'
        msg['From'] = 'brojas@gemini.edu'
        msg['To'] = email
        note = '\n' + '\n' + 'NOTE: Please check each port with the instrument in agSeqPorts.pv'
        message = content + note
        msg.set_content(message)
        s = smtplib.SMTP('localhost')
        s.send_message(msg)
        s.quit()


if __name__ == '__main__':

    # Get file list from the command line. Terminate if no files are specified.
    # args = get_arguments(['program', 'rtconfig.config', 'gea.config'])  # instruments_duplicates_detector
    # args = get_arguments(['program', '-h'])  # instruments_duplicates_detector
    # args = get_arguments(sys.argv)
    # if not args.file_list:
    #     print('no configuration files specified')
    #     exit(0)

    port_list = []
    error_canopus = ''
    instrument_list = []

    instrument_port_list = []
    instruments_finded = {}

    tables_dict = {}
    duplicate_entries = []

    instruments_message = ''
    duplicates_message = ''

    # Read configuration file(s)
    try:
        port_list = read_configuration('agSeqPorts.pv')
        instrument_list = read_configuration('ag_sf.lut')
    except FileNotFoundError as e:
        print(e)
        exit(0)
    except ConfigurationError as e:
        print(e)
        exit(0)
    except IndexError as e:
        print(e)
        exit(0)

    # print_list(port_list)
    # print_list(instrument_list)

    instrument_port_list, error_canopus = rescue_port_and_instrument_name(port_list)
    instruments_finded = search_instruments(instrument_list, instrument_port_list)

    try:
        tables_dict = create_dict_for_search_duplicates(instrument_list)
    except IndexError as e:
        print(e)
        print('Please check that lines on lookup tables are in the following format:')
        print('name,nval,steps,lowtol,hightol,steps,lowtol,hightol,steps,lowtol,hightol')
        exit(0)
    duplicate_entries = search_duplicates(tables_dict)

    instruments_message, duplicates_message = configure_email(instruments_finded, duplicate_entries)

    format_to_send(instruments_message, duplicates_message, error_canopus)

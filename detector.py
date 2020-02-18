import re
import sys
from argparse import Namespace, ArgumentParser


class ConfigurationError(Exception):
    """
    Raised when a syntax error is found in a configuration file.
    """
    pass


def search_duplicates(dict_tables):
    """

    :param dict_tables:
    :type dict_tables: dict
    :return:
    :rtype:
    """
    compare_dict = {}

    for key, value in dict_tables.items():
        compare_dict.setdefault(tuple(value), set()).add(key)

    result = [values for key, values in compare_dict.items()
              if len(values) > 1]

    # print("duplicates", result)
    return result


def create_dict_for_search_duplicates(instruments_list):
    """

    :param instruments_list:
    :type instruments_list: list
    :return:
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


def search_instrument(instruments_list, instruments_ports_list):
    """

    :param instruments_list:
    :type instruments_list: list
    :param instruments_ports_list:
    :type instruments_ports_list: list
    :return:
    :rtype: dict
    """
    finded_dict = {}
    key = ''
    value = ''

    finded_gcal2_list = []
    finded_list = []
    not_finded__gcal2_list = []
    not_finded_list = []
    for instrument_port in instruments_ports_list:
        for instrument in instruments_list:
            instrument_split = instrument.split()

            if 'gcal2' + instrument_port == instrument_split[0]:
                # finded_gcal2_list.append('gcal2' + instrument_port)
                # print('match', 'gcal2' + instrument_port)
                value = 'gcal2' + instrument_port
            elif instrument_port == instrument_split[0]:
                # finded_list.append(instrument_port)
                key = instrument_port

        if not key:
            finded_dict['emptyKey_' + instrument_port] = value
        elif not value:
            finded_dict[key] = 'emptyValue_' + instrument_port
        else:
            finded_dict[key] = value

        # if 'gcal2' + instrument_port not in finded_gcal2_list:
        #     not_finded__gcal2_list.append('gcal2' + instrument_port)
        #     # print("don't match", 'gcal2' + instrument_port)
        # elif instrument_port not in finded_list:
        #     not_finded_list.append(instrument_port)

    print(finded_dict)
    # print(finded_list, finded_gcal2_list, not_finded_list, not_finded__gcal2_list)
    return finded_dict


def instrument_to_search(ports_list):
    """

    :param ports_list:
    :type ports_list: list
    :return:
    :rtype: list
    """
    instrument_to_search_list = []
    for port_line in ports_list:
        port_line_list = port_line.split()
        number_port = (port_line_list[1])[-1].strip()
        instrument_name = port_line_list[3].replace('"', '').lower().strip()

        if not instrument_name + number_port == 'gcal2':
            instrument_to_search_list.append(instrument_name + number_port)

    if 'canopus4' not in instrument_to_search_list:
        print("CANOPUS it's not in port 4")
    else:
        instrument_to_search_list.remove('canopus4')

    return instrument_to_search_list


def read_configuration(file_name):
    """

    :param file_name: The name of the path file who has the configuration.
    :type file_name: str
    :return: A list with files found inside the configuration file.
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


if __name__ == '__main__':

    # Get file list from the command line. Terminate if no files are specified.
    # args = get_arguments(['program', 'rtconfig.config', 'gea.config'])  # instruments_duplicates_detector
    # args = get_arguments(['program', '-h'])  # instruments_duplicates_detector
    # args = get_arguments(sys.argv)
    # if not args.file_list:
    #     print('no configuration files specified')
    #     exit(0)

    # Read configuration file(s)
    port_list = []
    instrument_port_list = []
    instrument_list = []

    instruments_finded = {}

    tables_dict = {}
    duplicate_entries = []

    try:
        port_list = read_configuration('agSeqPorts.pv')
        instrument_list = read_configuration('ag_sf.lut')
    except FileNotFoundError as e:
        print(e)
        exit(0)
    except ConfigurationError as e:
        print(e)
        exit(0)

    instrument_port_list = instrument_to_search(port_list)
    instruments_finded = search_instrument(instrument_list, instrument_port_list)

    tables_dict = create_dict_for_search_duplicates(instrument_list)
    duplicate_entries = search_duplicates(tables_dict)

    print_list(port_list)
    print_list(instrument_list)

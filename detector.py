import re
import sys
from argparse import Namespace, ArgumentParser


class ConfigurationError(Exception):
    """
    Raised when a syntax error is found in a configuration file.
    """
    pass


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
        number_port = (port_line_list[1])[-1]
        instrument_name = port_line_list[3].replace('"', '').lower()
        instrument_to_search_list.append(instrument_name + number_port)
    return instrument_to_search_list


def read_configuration(file_name):
    """
    This function read the file configuration and have an state machine that separate
    the host and root folder from the folders who has the files to analyze, and as result
    have all files found inside the configuration file.
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

    print_list(port_list)
    print_list(instrument_list)






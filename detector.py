import re
import sys
from argparse import Namespace, ArgumentParser

FILE_CONF_LIST = ['agSeqPorts.pv', 'ag_sf.lut']


class ConfigurationError(Exception):
    """
    Raised when a syntax error is found in a configuration file.
    """
    pass


def read_configuration_file_list(conf_list):
    """
    This function iterates over a list who has the configuration files for later appended
    into only one file list.
    :param conf_list: The configurations files list.
    :type conf_list: list
    :return: A list with files found inside the configurations files.
    :rtype:list
    """
    final_list = []
    for config in conf_list:
        final_list.append(config)
        for config_files_list in read_configuration(config):
            final_list.append(config_files_list)
    return final_list


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
            # print(line_list)
            if re.search(r'port:port[1-5]', line_split_list[1]):
                print(line)
            elif line_split_list[1] == '3':
                print(line)

        # if re.search(PATTERN_HOST, line):  # [host=host_name]
        #     value = return_value(line)
        #     if value:
        #         if not host_name:
        #             host_name = value
        #         else:
        #             raise ConfigurationError('duplicate host definition')
        #     else:
        #         raise ConfigurationError('host name missing')
        #
        # elif re.search(PATTERN_ROOT, line):  # [root_folder=directory]
        #     root_folder = return_value(line)
        #     if root_folder:
        #         root_folder = append_delimiter(root_folder)
        #     else:
        #         raise ConfigurationError('root folder missing')
        #
        # elif re.search(PATTERN_FOLDER, line):  # [folder=directory]
        #     folder = return_value(line)
        #     if folder:
        #         folder = append_delimiter(folder)
        #         folder_defined = True
        #     else:
        #         raise ConfigurationError('folder missing')
        #
        # else:
        #     new_file_name = line    # file name
        #     if root_folder and folder_defined:
        #         found_file_list.append(root_folder + folder + new_file_name)
        #     else:
        #         raise ConfigurationError('root_folder or folder not defined for ' + new_file_name)

    f.close()
    return found_file_list


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
    file_list = []
    try:
        file_list = read_configuration_file_list(FILE_CONF_LIST)
    except FileNotFoundError as e:
        print(e)
        exit(0)
    except ConfigurationError as e:
        print(e)
        exit(0)

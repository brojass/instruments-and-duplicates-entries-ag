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

    :param dict_tables:
    :type dict_tables: dict
    :return:
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

    print(finded_dict)
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


def configure_email(instrument, duplicates):
    """

    :param instrument:
    :type instrument: dict
    :param duplicates:
    :type duplicates: dict
    """
    duplicates_problems = ''
    instruments_problems = ''

    for key, value in instrument.items():
        emptykey = ''
        emptyvalue = ''
        if re.search('emptyKey_', key) or not value:
            if re.search('emptyKey_', key):
                emptykey_split = key.split('_')
                emptykey = emptykey_split[-1] + ' could not be found'
                if not value:
                    emptyvalue = ' and gcal2' + emptykey_split[-1] + ' neither'
            elif not value:
                emptyvalue = 'gcal2' + key + ' could not be found'
            instruments_problems = instruments_problems + emptykey + emptyvalue + '\n'

    print(instruments_problems)

    for key, value in duplicates.items():
        if len(value) > 1:
            duplicates_problems = duplicates_problems + 'Elements ' + str(value) + ' has duplicate values: ' + str(
                key) + '\n'
    print(duplicates_problems)

    if instruments_problems and duplicates_problems:

        head_instruments = 'Instruments not found:' + "\n" + instruments_problems
        head_duplicates = 'Duplicates issues:' + "\n" + duplicates_problems
        content = head_instruments + "\n" + head_duplicates
        send_email(content)

    elif instruments_problems and not duplicates_problems:

        head_instruments = 'Instruments not found:' + "\n" + instruments_problems
        send_email(head_instruments)

    elif not instruments_problems and duplicates_problems:

        head_duplicates = 'Duplicates issues:' + "\n" + duplicates_problems
        send_email(head_duplicates)


def send_email(content):
    """

    :param content:
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

    configure_email(instruments_finded, duplicate_entries)

    print_list(port_list)
    print_list(instrument_list)

MESSAGE_LENGTHS = [2, 3, 4, 5]
FILE_REQUEST = '1'
FILE_RESPONSE = '2'
PART_REQUEST = '3'
PART_RESPONSE = '4'
COMMANDS_NUMS = [FILE_REQUEST, FILE_RESPONSE, PART_REQUEST, PART_RESPONSE]


def convert_message(message):
    message = message.split(';')

    if len(message) not in MESSAGE_LENGTHS:
        return ['Protocol Error: Wrong Structure']

    command = message[0]

    if command not in COMMANDS_NUMS:
        return ['Protocol Error: Unknown Command']

    if len(message) == 2:
        if command != FILE_REQUEST:
            return ['Protocol Error: Wrong Structure']
        return message

    if len(message) == 5:
        if command != FILE_RESPONSE:
            return ['Protocol Error: Wrong Structure']
        return message

    if len(message) == 3:
        if command != PART_REQUEST:
            return ['Protocol Error: Wrong Structure']
        return message

    if len(message) == 4:
        if command != PART_RESPONSE:
            return ['Protocol Error: Wrong Structure']
        return message

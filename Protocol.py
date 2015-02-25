MESSAGE_LENGTHS = [2, 3]
FILE_REQUEST = '1'
FILE_RESPONSE = '2'
PART_REQUEST = '3'
PART_RESPONSE = '4'
COMMANDS_NUMS = [FILE_REQUEST, FILE_RESPONSE, PART_REQUEST, PART_RESPONSE]


def Convert_Message(message):
    message = message.split(';*;')

    if len(message) not in MESSAGE_LENGTHS:
        return ['Protocol Error: Wrong Structure']

    command = message[0]
    file_name = message[1]

    if command not in COMMANDS_NUMS:
        return ['Protocol Error: Unknown Command']

    if len(message) == 2:
        if command == FILE_REQUEST:
            return [FILE_REQUEST, file_name]
        return ['Protocol Error: Wrong Structure']

    if len(message) == 3:
        if command == FILE_RESPONSE:
            hashed = message[2]
            return [FILE_RESPONSE, file_name, hashed]

        if command == PART_REQUEST:
            partition = message[2].split('/')
            if len(partition) != 2:
                return ['Protocol Error: Wrong Structure']

            (part, parts) = (partition[0], partition[1])
            if (not part.isdigit()) or (not part.isdigit()):
                return ['Protocol Error: Wrong Structure']

            return [PART_REQUEST, file_name, partition]

        if command == PART_RESPONSE:
            partition = message[2].split('/')
            if len(partition) != 2:
                return ['Protocol Error: Wrong Structure']

            (part, file) = (partition[0], partition[1])
            if not part.isdigit():
                return ['Protocol Error: Wrong Structure']

            return [PART_REQUEST, file_name, partition]

        return ['Protocol Error: Wrong Structure']


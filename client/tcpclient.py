# IS496: Computer Networks (Spring 2022)
# Programming Assignment 2 - Starter Code
# Name and Netid of each member:
# Member 1: xiuyuan7
# Member 2: shaojun3
# Member 3: boyu4

# Note: 
# This starter code is optional. Feel free to develop your own solution to Part 1. 
# The finished code for Part 1 can also be used for Part 2 of this assignment. 


# Import any necessary libraries below
import socket
import sys
import os
import time
import subprocess


# TODO: define a buffer size for the message to be read from the TCP socket
BUFFER = 4096


# main function for Part 1
def part1():
    # TODO: fill in the hostname and port number
    hostname = 'student00.ischool.illinois.edu'
    port = 41025

    # A dummy message (in bytes) to test the code
    message = "Hello World"

    # TODO: convert the host name to the corresponding IP address
    try:
        host = socket.gethostbyname(hostname)
    except socket.error:
        print("Unknown hostname: %s" % hostname)
    sin = (host, port)

    # TODO: create a datagram socket for TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket.')
        sys.exit()

    # TODO: connect to the server
    try:
        s.connect(sin)
    except socket.error:
        print('Failed to connect to server.')
        sys.exit()

    # TODO: send the message to the server
    try:
        s.sendall(message.encode())
    except socket.error:
        print('Failed to send to server.')
        sys.exit()

    # TODO: receive the acknowledgement from the server
    try:
        ack = s.recv(BUFFER)
    except socket.error:
        print('Failed to receive from server.')
        sys.exit()

    # TODO: print the acknowledgement to the screen
    ack = socket.ntohl(int(ack.decode()))
    print(f'Acknowledgement: {ack}')

    # TODO: close the socket
    try:
        s.close()
    except socket.error:
        print('Failed to close socket.')
        sys.exit()


# main function for Part 2
def part2():
    print("********** PART 2 **********")
    # TODO: fill in the hostname and port number
    hostname = sys.argv[1]

    if sys.argv[2] == '41025':
        port = int(sys.argv[2])
    else:
        print('Wrong port number.')
        sys.exit()

    # TODO: convert the host name to the corresponding IP address
    try:
        host = socket.gethostbyname(hostname)
    except socket.error:
        print("Unknown hostname: %s" % hostname)
    sin = (host, port)

    # TODO: create a datagram socket for TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Failed to create socket.')
        sys.exit()

    # TODO: connect to the server
    try:
        s.connect(sin)
    except socket.error:
        print('Failed to connect to server.')
        sys.exit()

    print('Connection established.')

    while True:

        # get operation from user
        operation = input('> ')

        # split operation into arguments
        arguments = operation.split()
        if not arguments:
            continue
        command = arguments[0]

        # send command to server
        try:
            s.send(command.encode())
        except socket.error:
            print('Failed to send command to server.')
            sys.exit()

        # TODO: handle DN command
        if command == 'DN' and len(arguments) == 2:

            file_name = arguments[1]

            try:
                s.send(file_name.encode())
            except socket.error:
                print('Failed to send file name to server.')
                sys.exit()

            try:
                file_size = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive file size from server.')
                sys.exit()

            if file_size == '-1':

                print('File not found.')
                continue

            else:

                file_size = socket.ntohl(int(file_size))

                start_time = time.time()
                received_size = 0

                with open(file_name, 'wb') as f:
                    summ = 0
                    while received_size <= file_size:
                        try:
                            packet = s.recv(BUFFER)
                        except socket.error:
                            print('Failed to receive packet from server.')
                            sys.exit()
                        summ += 1
                        received_size += BUFFER
                        f.write(packet)

                    print(summ)

                end_time = time.time()
                time_consumed = end_time - start_time
                throughput = file_size / time_consumed / 2 ** 20

                try:
                    md5sum_server = s.recv(BUFFER)
                except socket.error:
                    print('Failed to receive file size from server.')
                    sys.exit()

                md5sum_client = subprocess.check_output(['md5sum', file_name])

                if md5sum_client == md5sum_server:

                    print(f'File confirmed with MD5: {md5sum_server}')
                    print(f'{file_size} bytes transferred in {round(time_consumed, 4)} seconds: {round(throughput, 4)} Megabytes/sec')

                else:

                    print('MD5 hash does not match, please download again.')

        # TODO: handle UP command
        elif command == 'UP' and len(arguments) == 2:

            file_name = arguments[1]
            file_size = os.path.getsize(file_name)

            try:
                s.send(file_name.encode())
            except socket.error:
                print('Failed to send file name to server.')
                sys.exit()

            try:
                ack = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive acknowledgment from server.')
                sys.exit()

            if ack == '1':
                start_time = time.time()

                try:
                    s.send(f'{socket.htonl(file_size)}'.encode())
                except socket.error:
                    print('Failed to send file size to server.')
                    sys.exit()

                with open(file_name, 'rb') as f:
                    packet = f.read(BUFFER)
                    while packet:
                        try:
                            s.send(packet)
                        except socket.error:
                            print('Failed to send packet to client.')
                            sys.exit()
                        packet = f.read(BUFFER)

                end_time = time.time()
                time_consumed = end_time - start_time

                try:
                    throughput = float(s.recv(BUFFER).decode())
                except socket.error:
                    print('Failed to receive throughput from server.')
                    sys.exit()

                md5sum_client = subprocess.check_output(['md5sum', file_name])

                try:
                    s.send(md5sum_client)
                except socket.error:
                    print('Failed to send md5sum to server.')
                    sys.exit()

                try:
                    con = s.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive confirmation from server.')
                    sys.exit()

                if con == '1':

                    print(f'File confirmed with MD5: {md5sum_client}')
                    print(f'{file_size} bytes transferred in {round(time_consumed, 4)} seconds: {round(throughput, 4)} Megabytes/sec')

                else:

                    print('MD5 hash does not match, please upload again.')

            else:
                print('Server is not ready to receive the file.')
                sys.exit()

        # TODO: handle RM command
        elif command == 'RM' and len(arguments) == 2:

            file_name = arguments[1]

            try:
                s.send(file_name.encode())
            except socket.error:
                print('Failed to send name to server.')
                sys.exit()

            try:
                con = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive confirmation from server.')
                sys.exit()

            if con == '-1':

                print('File does not exist.')
                continue

            elif con == '1':

                confirmation = input('Are you sure you want to delete the file? "Yes" to delete, "No" to ignore.\n')

                if confirmation == 'Yes':

                    try:
                        s.send(confirmation.encode())
                    except socket.error:
                        print('Failed to send confirmation to server.')
                        sys.exit()

                    try:
                        con = int(s.recv(BUFFER).decode())
                    except socket.error:
                        print('Failed to receive confirmation from server.')
                        sys.exit()

                    if con == -1:

                        print('File not deleted.')

                    else:

                        print('File deleted.')

                elif confirmation == 'No':

                    try:
                        s.send(confirmation.encode())
                    except socket.error:
                        print('Failed to send confirmation to server.')
                        sys.exit()

                    print('Delete abandoned by the user!')

                else:

                    try:
                        s.send(confirmation.encode())
                    except socket.error:
                        print('Failed to send confirmation to server.')
                        sys.exit()

                    print('Wrong confirmation.')

        # TODO: handle LS command
        elif command == 'LS' and len(arguments) == 1:

            try:
                listing = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive listing from server.')
                sys.exit()

            print(listing)

        # TODO: handle MKDIR command
        elif command == 'MKDIR' and len(arguments) == 2:

            directory_name = arguments[1]

            try:
                s.send(directory_name.encode())
            except socket.error:
                print('Failed to send directory name to server.')
                sys.exit()

            try:
                con = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive confirmation from server.')
                sys.exit()

            if con == '-2':

                print('The directory already exists on server.')

            elif con == '-1':

                print('Error in making directory.')

            else:

                print('The directory was successfully made.')

        # TODO: handle RMDIR command
        elif command == 'RMDIR' and len(arguments) == 2:

            directory_name = arguments[1]

            try:
                s.send(directory_name.encode())
            except socket.error:
                print('Failed to send directory name to server.')
                sys.exit()

            try:
                con = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive confirmation from server.')
                sys.exit()

            if con == '-1':

                print('The directory does not exist on server.')

            elif con == '-2':

                print('The directory is not empty')

            else:

                confirmation = input('Are you sure you want to remove the directory? "Yes" to remove, "No" to ignore.\n')

                if confirmation == 'Yes':

                    try:
                        s.send(confirmation.encode())
                    except socket.error:
                        print('Failed to send confirmation to server.')
                        sys.exit()

                    try:
                        con = int(s.recv(BUFFER).decode())
                    except socket.error:
                        print('Failed to receive confirmation from server.')
                        sys.exit()

                    if con == -1:

                        print('Failed to delete directory.')

                    else:

                        print('Directory deleted.')

                elif confirmation == 'No':

                    try:
                        s.send(confirmation.encode())
                    except socket.error:
                        print('Failed to send confirmation to server.')
                        sys.exit()

                    print('Delete abandoned by the user!')

                else:

                    try:
                        s.send(confirmation.encode())
                    except socket.error:
                        print('Failed to send confirmation to server.')
                        sys.exit()

                    print('Wrong confirmation.')

        # TODO: handle CD command
        elif command == 'CD' and len(arguments) == 2:

            directory_name = arguments[1]

            try:
                s.send(directory_name.encode())
            except socket.error:
                print('Failed to send directory name to server.')
                sys.exit()

            try:
                con = s.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive confirmation from server.')
                sys.exit()

            if con == '-2':

                print('The directory does not exist on server.')

            elif con == '-1':

                print('Error in changing directory.')

            else:

                print('Changed current directory.')

        # TODO: handle QUIT command
        elif command == 'QUIT' and len(arguments) == 1:

            try:
                s.close()
            except socket.error:
                print('Failed to close socket.')
                sys.exit()
            sys.exit()

        # TODO: handle unknown command
        else:
            print('Command not right.')


if __name__ == '__main__':
    # Your program will go with function part1() if there is no command line input. 
    # Otherwise, it will go with function part2() to handle the command line input 
    # as specified in the assignment instruction. 
    if len(sys.argv) == 1:
        part1()
    elif len(sys.argv) == 3:
        part2()
    else:
        print('Wrong number of arguments.')

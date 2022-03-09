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
import subprocess
import time


# TODO: define a buffer size for the message to be read from the TCP socket
BUFFER = 4096


# main function for Part 1
def part1():
    print("********** PART 1 **********")
    # TODO: fill in the hostname and port number
    hostname = 'student00.ischool.illinois.edu'
    port = 41025

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

    # TODO: Bind the socket to address
    try:
        s.bind(sin)
    except socket.error:
        print('Failed to bind socket.')
        sys.exit()

    # TODO: start listening
    try:
        s.listen()
    except socket.error:
        print('Failed to listen to client.')
        sys.exit()

    # TODO: accept the connection and record the address of the client socket
    try:
        conn, addr = s.accept()
    except socket.error:
        print('Failed to accept connection from client.')
        sys.exit()

    # TODO: receive message from the client 
    try:
        data = conn.recv(BUFFER)
    except socket.error:
        print('Failed to receive from client.')
        sys.exit()

    # TODO: print the message to the screen
    print(f'Client Message: {data.decode()}')

    # TODO: send an acknowledgement (e.g., integer of 1) to the client
    ack = socket.htonl(1)
    try:
        conn.sendall(f'{ack}'.encode())
    except socket.error:
        print('Failed to send to client.')
        sys.exit()

    # TODO: close the socket
    try:
        s.close()
    except socket.error:
        print('Failed to close s socket.')
        sys.exit()

    try:
        conn.close()
    except socket.error:
        print('Failed to close conn socket.')
        sys.exit()


# main function for Part 2
def part2():
    print("********** PART 2 **********")
    # TODO: fill in the hostname and port number
    hostname = 'student00.ischool.illinois.edu'

    if sys.argv[1] == '41025':
        port = int(sys.argv[1])
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

    # TODO: Bind the socket to address
    try:
        s.bind(sin)
    except socket.error:
        print('Failed to bind socket.')
        sys.exit()

    # TODO: start listening
    try:
        s.listen()
    except socket.error:
        print('Failed to listen to client.')
        sys.exit()

    while True:
        print(f'Waiting for connections on port {port}')

        # TODO: accept the connection and record the address of the client socket
        try:
            conn, addr = s.accept()
        except socket.error:
            print('Failed to accept connection from client.')
            sys.exit()

        print('Connection established.')

        while True:
            # receive command from client
            try:
                command = conn.recv(BUFFER).decode()
            except socket.error:
                print('Failed to receive command from client.')
                sys.exit()

            # if client break the process, break to new connection
            if not command:
                break

            # TODO: handle DN command
            if command == 'DN':

                try:
                    file_name = conn.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive file name from client.')
                    sys.exit()

                if os.path.exists(file_name) and os.path.isfile(file_name):

                    file_size = os.path.getsize(file_name)

                    try:
                        conn.send(f'{socket.htonl(file_size)}'.encode())
                    except socket.error:
                        print('Failed to send file size to client.')
                        sys.exit()

                    with open(file_name, 'rb') as f:
                        packet = f.read(BUFFER)
                        summ = 0
                        while packet:

                            try:
                                conn.send(packet)
                            except socket.error:
                                print('Failed to send packet to client.')
                                sys.exit()
                            summ += 1

                            packet = f.read(BUFFER)

                        print(summ)

                    md5sum_server = subprocess.check_output(['md5sum', file_name])

                    try:
                        conn.send(md5sum_server)
                    except socket.error:
                        print('Failed to send md5sum to client.')
                        sys.exit()

                else:
                    try:
                        conn.send(b'-1')
                    except socket.error:
                        print('Failed to send -1 to client.')
                        sys.exit()

            # TODO: handle UP command
            elif command == 'UP':

                try:
                    file_name = conn.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive file name from client.')
                    sys.exit()

                try:
                    conn.send('1'.encode())
                except socket.error:
                    print('Failed to send acknowledgment to client.')
                    sys.exit()

                try:
                    file_size = socket.ntohl(int(conn.recv(BUFFER).decode()))
                except socket.error:
                    print('Failed to receive file size from client.')
                    sys.exit()

                start_time = time.time()
                received_size = 0
                with open(file_name, 'wb') as f:
                    while received_size < file_size:
                        try:
                            packet = conn.recv(BUFFER)
                        except socket.error:
                            print('Failed to receive packet from server.')
                            sys.exit()
                        received_size += BUFFER
                        f.write(packet)

                end_time = time.time()
                time_consumed = end_time - start_time
                throughput = file_size / time_consumed / 2 ** 20

                try:
                    conn.send(f'{throughput}'.encode())
                except socket.error:
                    print('Failed to send throughput to client.')
                    sys.exit()

                try:
                    md5sum_client = conn.recv(BUFFER)
                except socket.error:
                    print('Failed to receive md5sum from server.')
                    sys.exit()

                md5sum_server = subprocess.check_output(['md5sum', file_name])

                if md5sum_client == md5sum_server:

                    try:
                        conn.send('1'.encode())
                    except socket.error:
                        print('Failed to send MD5 hash confirmation to client.')
                        sys.exit()

                else:

                    try:
                        conn.send('-1'.encode())
                    except socket.error:
                        print('Failed to send MD5 hash confirmation to client.')
                        sys.exit()

            # TODO: handle RM command
            elif command == 'RM':

                try:
                    file_name = conn.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive name from client.')
                    sys.exit()

                if os.path.exists(file_name):

                    try:
                        conn.send(b'1')
                    except socket.error:
                        print('Failed to send 1 confirmation to client.')
                        sys.exit()

                    try:
                        confirmation = conn.recv(BUFFER).decode()
                    except socket.error:
                        print('Failed to receive confirmation from client.')
                        sys.exit()

                    if confirmation == 'Yes':

                        os.remove(file_name)

                        if os.path.exists(file_name):

                            try:
                                conn.send(b'-1')
                            except socket.error:
                                print('Failed to send -1 confirmation to client.')
                                sys.exit()

                        else:

                            try:
                                conn.send(b'1')
                            except socket.error:
                                print('Failed to send 1 confirmation to client.')
                                sys.exit()

                    elif confirmation == 'No':

                        continue

                    else:

                        continue

                else:

                    try:
                        conn.send(b'-1')
                    except socket.error:
                        print('Failed to send -1 confirmation to client.')
                        sys.exit()

            # TODO: handle LS command
            elif command == 'LS':

                try:
                    conn.send(subprocess.check_output(['ls', '-l']))
                except socket.error:
                    print('Failed to send listing to client.')
                    sys.exit()

            # TODO: handle MKDIR command
            elif command == 'MKDIR':

                try:
                    directory_name = conn.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive directory name from client.')
                    sys.exit()

                if os.path.exists(directory_name):

                    try:
                        conn.send(b'-2')
                    except socket.error:
                        print('Failed to send confirmation to client.')
                        sys.exit()

                else:

                    os.makedirs(directory_name)

                    if os.path.exists(directory_name):

                        try:
                            conn.send(b'1')
                        except socket.error:
                            print('Failed to send confirmation to client.')
                            sys.exit()

                    else:

                        try:
                            conn.send(b'-1')
                        except socket.error:
                            print('Failed to send confirmation to client.')
                            sys.exit()

            # TODO: handle RMDIR command
            elif command == 'RMDIR':

                try:
                    directory_name = conn.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive directory name from client.')
                    sys.exit()

                if os.path.exists(directory_name) and len(os.listdir(directory_name)) == 0:

                    try:
                        conn.send(b'1')
                    except socket.error:
                        print('Failed to send confirmation to client.')
                        sys.exit()

                    try:
                        con = conn.recv(BUFFER).decode()
                    except socket.error:
                        print('Failed to receive confirmation from client.')
                        sys.exit()

                    if con == 'Yes':

                        os.rmdir(directory_name)

                        if os.path.exists(directory_name):

                            try:
                                conn.send(b'-1')
                            except socket.error:
                                print('Failed to send confirmation to client.')
                                sys.exit()

                        else:

                            try:
                                conn.send(b'1')
                            except socket.error:
                                print('Failed to send confirmation to client.')
                                sys.exit()

                    elif con == 'No':

                        continue

                    else:

                        continue

                elif os.path.exists(directory_name):

                    try:
                        conn.send(b'-2')
                    except socket.error:
                        print('Failed to send confirmation to client.')
                        sys.exit()

                else:

                    try:
                        conn.send(b'-1')
                    except socket.error:
                        print('Failed to send confirmation to client.')
                        sys.exit()

            # TODO: handle CD command
            elif command == 'CD':

                try:
                    directory_name = conn.recv(BUFFER).decode()
                except socket.error:
                    print('Failed to receive directory name from client.')
                    sys.exit()

                if os.path.exists(directory_name):

                    path_old = os.getcwd()
                    os.chdir(directory_name)
                    path_new = os.getcwd()

                    if path_old != path_new:

                        try:
                            conn.send(b'1')
                        except socket.error:
                            print('Failed to send confirmation to client.')
                            sys.exit()

                    else:

                        try:
                            conn.send(b'-1')
                        except socket.error:
                            print('Failed to send confirmation to client.')
                            sys.exit()

                else:

                    try:
                        conn.send(b'-2')
                    except socket.error:
                        print('Failed to send confirmation to client.')
                        sys.exit()

            # TODO: handle QUIT command
            elif command == 'QUIT':

                try:
                    conn.close()
                except socket.error:
                    print('Failed to close socket.')
                    break

                break


if __name__ == '__main__':
    # Your program will go with function part1() if there is no command line input. 
    # Otherwise, it will go with function part2() to handle the command line input 
    # as specified in the assignment instruction. 
    if len(sys.argv) == 1:
        part1()
    elif len(sys.argv) == 2:
        part2()
    else:
        print('Wrong number of arguments.')

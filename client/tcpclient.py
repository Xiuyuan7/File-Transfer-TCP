# IS496: Computer Networks (Spring 2022)
# Programming Assignment 2 - Starter Code
# Name and Netid of each member:
# Member 1: 
# Member 2: 
# Member 3: 

# Note: 
# This starter code is optional. Feel free to develop your own solution to Part 1. 
# The finished code for Part 1 can also be used for Part 2 of this assignment. 


# Import any necessary libraries below
import socket
import sys
import os


############## Beginning of Part 1 ##############
# TODO: define a buffer size for the message to be read from the TCP socket
BUFFER = 4096


def part1 ():
    # TODO: fill in the hostname and port number
    HOSTNAME = 'student00.ischool.illinois.edu'
    PORT = 41025

    # A dummy message (in bytes) to test the code
    message = "Hello World"

    # TODO: convert the host name to the corresponding IP address
    try:
        HOST = socket.gethostbyname(HOSTNAME)
    except socket.error as e:
        print("Unknown hostname: %s" % HOSTNAME)
    sin = (HOST, PORT)


    # TODO: create a datagram socket for TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()


    # TODO: connect to the server
    try:
        s.connect(sin)
    except socket.error as e:
        print('Failed to connect to server.')
        sys.exit()

    # TODO: send the message to the server
    try:
        s.sendall(message.encode())
    except socket.error as e:
        print('Failed to send to server.')
        sys.exit()

    # TODO: receive the acknowledgement from the server
    try:
        ack = s.recv(BUFFER)
    except socket.error as e:
        print('Failed to receive from server.')
        sys.exit()

    # TODO: print the acknowledgement to the screen
    ack = socket.ntohl(int(ack.decode()))
    print(f'Acknowledgement: {ack}')

    # TODO: close the socket
    try:
        s.close()
    except socket.error as e:
        print('Failed to close socket.')
        sys.exit()


############## End of Part 1 ##############




############## Beginning of Part 2 ##############

handler = {}

def handleLS(res, s):
    print(res.decode())

def handleRM(res, s):
    respond = int(res.decode())
    if respond < 0:
        print('File does not exist.')
    elif respond > 0:
        confirmation = input('Are you sure you want to delete the file? "Yes" to delete, "No" to ignore.\n')
        if confirmation.lower() == 'no' or confirmation.lower() == 'n':
            print('Delete abandoned by the user!')
            s.sendall(b'no')
            s.recv(BUFFER)
        elif confirmation.lower() == 'yes' or confirmation.lower() == 'y':
            s.sendall(b'yes')
            mesg = s.recv(BUFFER).decode()
            respond1 = int(mesg)
            if respond1 > 0:
                print('Successfully delete the file')
            else:
                print('Fail to delete the file')
        else:
            print('wrong confirmation')
            s.sendall(b'no')
            s.recv(BUFFER)

def handleCD(res, s):
    respond = int(res.decode())
    if respond == -2:
        print('The directory does not exist on server')
    elif respond == -1:
        print('Error in changing directory')
    elif respond == 1:
        print('Changed current directory')

def handleMKDIR(res, s):
    respond = int(res.decode())
    if respond == -2:
        print('The directory already exists on server')
    elif respond == -1:
        print('Error in making directory')
    elif respond > 0:
        print('The directory was successfully made')

def handleRMDIR(res, s):
    respond = int(res.decode())
    if respond == -1:
        print("The directory does not exist on server")
    elif respond == -2:
        print("The directory is not empty")
    elif respond > 0:
        confirmation = input('Please confirm that you want to delete the directory. "Yes" to delete, "No" to ignore.\n')
        if confirmation.lower() == 'yes' or confirmation.lower() == 'y':
            s.sendall(b'yes')
            respond1 = int(s.recv(BUFFER).decode())
            if respond1 == 1:
                print('The directory is successfully deleted')
            else:
                print('Fail to delete the directory')
        elif confirmation.lower() == 'no' or confirmation.lower() == 'n':
            print('Delete abandoned by the user')
            s.sendall(b'no')
            s.recv(BUFFER)

def handleQ(res, s):
    s.close()

def handleUP(res, s):
    filename = res.decode()
    if os.path.exists(filename) and os.path.isfile(filename):
        filesize = os.path.getsize(filename)
        s.sendall(str(filesize).encode())
        with open(filename, 'rb') as f:
            l = f.read(BUFFER)
            while l:
                s.sendall(l)
                l = f.read(BUFFER)


    else:
        s.sendall(b'-1')
        print('File does not exist')

def handleDN(res, s):
    response = res.decode()
    if response == '-1':
        print('file does not exist')
    else:
        filesize, filename = response.split()
        filesize = int(filesize)
        size = 0

        with open(filename, 'w+b') as f:
            while size < filesize:
                l = s.recv(BUFFER)
                f.write(l)
                size += BUFFER
        print('file received successfully, size: {} bytes'.format(str(filesize)))

handler['LS'] = handleLS
handler['RM'] = handleRM
handler['CD'] = handleCD
handler['RMDIR'] = handleRMDIR
handler['MKDIR'] = handleMKDIR
handler['QUIT'] = handleQ
handler['UP'] = handleUP
handler['DN'] = handleDN

# main function for Part 2
def part2 ():
    print("********** PART 2 **********")
    # TODO: fill in the hostname and port number
    HOSTNAME = sys.argv[1]
    PORT = int(sys.argv[2])

    # TODO: convert the host name to the corresponding IP address
    try:
        HOST = socket.gethostbyname(HOSTNAME)
    except socket.error as e:
        print("Unknown hostname: %s" % HOSTNAME)
    sin = (HOST, PORT)

    # TODO: create a datagram socket for TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()

    # TODO: connect to the server
    try:
        s.connect(sin)
    except socket.error as e:
        print('Failed to connect to server.')
        sys.exit()

    print('Connection established.')

    while True:

        # get command from user
        command = input('> ')

        # send command to server
        try:
            s.sendall(command.encode())
        except socket.error as e:
            print('Failed to send to server.')
            sys.exit()

        # receive respond from server
        try:
            respond = s.recv(BUFFER)
        except socket.error as e:
            print('Failed to receive respond from server.')
            sys.exit()

        params = [respond, s]
        handlerLabel = command.split()[0]
        if handlerLabel not in handler:
            print('command not found')
            continue
        handler[handlerLabel](*params)
        if s.fileno() == -1:
            break


############## End of Part 2 ##############


if __name__ == '__main__':
    # Your program will go with function part1() if there is no command line input. 
    # Otherwise, it will go with function part2() to handle the command line input 
    # as specified in the assignment instruction. 
    if len(sys.argv) == 1:
        part1()
    else:
        part2()

   
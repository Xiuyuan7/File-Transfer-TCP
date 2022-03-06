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
import subprocess


############## Beginning of Part 1 ##############
# TODO: define a buffer size for the message to be read from the TCP socket
BUFFER = 4096


def part1 ():
    print("********** PART 1 **********")
    # TODO: fill in the IP address of the host and the port number
    HOST = '127.0.0.1'
    PORT = 8000
    sin = (HOST, PORT)

    # TODO: create a datagram socket for TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()


    # TODO: Bind the socket to address
    try:
        s.bind(sin)
    except socket.error as e:
        print('Failed to bind socket.')
        sys.exit()


    # TODO: start listening 
    try:
        s.listen()
    except socket.error as e:
        print('Failed to listen to client.')
        sys.exit()

    # TODO: accept the connection and record the address of the client socket
    try:
        conn, addr = s.accept()
    except socket.error as e:
        print('Failed to accept connection from client.')
        sys.exit()

    # TODO: receive message from the client 
    try:
        data = conn.recv(BUFFER)
    except socket.error as e:
        print('Failed to receive from client.')
        sys.exit()

    # TODO: print the message to the screen
    print(f'Client Message: {data.decode()}')

    # TODO: send an acknowledgement (e.g., integer of 1) to the client
    ack = socket.htonl(1)
    try:
        conn.sendall(f'{ack}'.encode())
    except socket.error as e:
        print('Failed to send to client.')
        sys.exit()

    # TODO: close the socket
    try:
        s.close()
    except socket.error as e:
        print('Failed to close s socket.')
        sys.exit()

    try:
        conn.close()
    except socket.error as e:
        print('Failed to close conn socket.')
        sys.exit()

############## End of Part 1 ##############




############## Beginning of Part 2 ##############

def changeWD(dirname, conn):
    if os.path.exists(dirname) and os.path.isdir(dirname):
        try:
            os.chdir(dirname)
            conn.sendall(b'1')
        except Exception:
            conn.sendall(b'-1')
    else:
        conn.sendall(b'-2')


def removeFiles(filename, conn):
    if os.path.exists(filename) and os.path.isfile(filename):
        conn.sendall(b'1')
        confirmation = conn.recv(BUFFER).decode()
        if confirmation == 'yes':
            os.remove(filename)
            conn.sendall(b'1')
        elif confirmation == 'no':
            conn.sendall( b'-1')
    else:
        conn.sendall(b'-1')

def removeDir(dirname, conn):
    if os.path.exists(dirname) and os.path.isdir(dirname):
        if len(os.listdir(dirname)) > 0:
            conn.sendall(b'-2')
        else:
            conn.sendall(b'1')
            confirmation = conn.recv(BUFFER).decode()
            if confirmation == 'yes':
                os.rmdir(dirname)
                conn.sendall(b'1')
            elif confirmation == 'no':
                conn.sendall(b'-1')
    else:
        conn.sendall(b'-1')

def listFiles(conn):
    conn.sendall(subprocess.check_output(['ls', '-l']))


def makeDirectory(dirname, conn):
    if os.path.exists(dirname) and os.path.isdir(dirname):
        conn.sendall(b'-2')

    try:
        os.makedirs(dirname)
        conn.sendall(b'1')
    except subprocess.CalledProcessError:
        conn.sendall(b'-1')


def handleQ(conn):
    os.chdir('/'.join(__file__.split('/')[:-1])) # change the working directory to initial state
    conn.close()

def handleDN(filename, conn):
    if os.path.exists(filename) and os.path.isfile(filename):
        response = str(os.path.getsize(filename))+' '+filename
        conn.sendall(response.encode())
        str(os.path.getsize(filename)).encode()
        with open(filename,'rb') as f:
            chunk = f.read(BUFFER)
            while chunk:
                print(chunk)
                conn.sendall(chunk)
                chunk = f.read(BUFFER)
            conn.sendall(b'-1')
    else:
        conn.sendall(b'-1')


def handleUP(filename, conn):
    conn.sendall(filename.encode())
    response = conn.recv(BUFFER).decode()
    if response == '-1':
        pass
    else:
        filesize = int(response)
        size = 0
        with open(filename, 'wb') as f:
            while size < filesize:
                l = conn.recv(BUFFER)
                f.write(l)
                size += BUFFER

handler = {}
handler['LS'] = listFiles
handler['MKDIR'] = makeDirectory
handler['RMDIR'] = removeDir
handler['RM'] = removeFiles
handler['CD'] = changeWD
handler['QUIT'] = handleQ
handler['DN'] = handleDN
handler['UP'] = handleUP

# main function for Part 2
def part2 ():
    print("********** PART 2 **********")

    # TODO: fill in the IP address of the host and the port number
    HOST = '127.0.0.1'
    PORT = int(sys.argv[1])
    sin = (HOST, PORT)

    # TODO: create a datagram socket for TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()

    # TODO: Bind the socket to address
    try:
        s.bind(sin)
    except socket.error as e:
        print('Failed to bind socket.')
        sys.exit()

    # TODO: start listening
    try:
        s.listen()
    except socket.error as e:
        print('Failed to listen to client.')
        sys.exit()

    while True:
        print(f'Waiting for connections on port {PORT}')

        # TODO: accept the connection and record the address of the client socket
        try:
            conn, addr = s.accept()
        except socket.error as e:
            print('Failed to accept connection from client.')
            sys.exit()

        print('Connection established.')

        while True:
            # receive command from client
            try:
                message = conn.recv(BUFFER).decode()
            except socket.error as e:
                print('Failed to receive command from client.')
                sys.exit()

            params = message.split()
            handlerlabel = params[0]
            arguments = params[1:] + [conn]
            if handlerlabel not in handler:
                respond = b'command not found'
            else:
                handler[handlerlabel](*arguments)
            if conn.fileno() == -1:
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





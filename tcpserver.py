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


############## Beginning of Part 1 ##############
# TODO: define a buffer size for the message to be read from the TCP socket
BUFFER = 


def part1 ():
    print("********** PART 1 **********")
    # TODO: fill in the IP address of the host and the port number
    HOST = 
    PORT = 
    sin = (HOST, PORT)

    # TODO: create a datagram socket for TCP
    try:

    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()


    # TODO: Bind the socket to address
    try:

    except socket.error as e:
        print('Failed to bind socket.')
        sys.exit()


    # TODO: start listening 


    # TODO: accept the connection and record the address of the client socket


    # TODO: receive message from the client 


    # TODO: print the message to the screen


    # TODO: send an acknowledgement (e.g., interger of 1) to the client


    # TODO: close the socket


############## End of Part 1 ##############




############## Beginning of Part 2 ##############

# main function for Part 2
def part2 ():



############## End of Part 2 ##############



if __name__ == '__main__':
    # Your program will go with function part1() if there is no command line input. 
    # Otherwise, it will go with function part2() to handle the command line input 
    # as specified in the assignment instruction. 
    if len(sys.argv) == 1:
        part1()
    else:
        part2()





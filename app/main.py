# Uncomment this to pass the first stage
import socket
from threading import Thread
from os.path import isfile, exists
from sys import argv

def get_directory_cmd():
    return argv[2]

def sock_handler(conn, addr):
    print(f"Connected by {addr}")
    # data = bytes object
    data = conn.recv(1024)
    # data_str = str
    if data:
        data_str = data.decode()
        # METHOD /path <-- We get path
        path = data_str.split(" ")[1]
        if path == "/":
            conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
        elif path.startswith("/echo"):
            splitPath = path.split("/")
            wordToEcho = splitPath[2]
            if(wordToEcho):
                echoBytes = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(wordToEcho)}\r\n\r\n{wordToEcho}".encode()
            conn.send(echoBytes)
        elif path == "/user-agent":
            userAgent = (data_str.split('User-Agent:')[1].split('\r\n')[0]).strip()
            userAgentBytes = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(userAgent)}\r\n\r\n{userAgent}".encode()
            conn.send(userAgentBytes)
        elif path.startswith('/files'):
            filename = data_str.split(' ')[1].split('/')[2]
            print(filename)
            directory = get_directory_cmd()
            if not directory:
                conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            else: 
                file_exists = exists(f"{directory}/{filename}")
            
            if not file_exists:
                conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            else:
                file_contents = open(f"{directory}/{filename}", 'r').read()
                send_string = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_contents)}\r\n\r\n{file_contents}"
                conn.send(send_string.encode())
        else:
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
    print(f"Closing Client Connection for {addr}")
    conn.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server Starting...")
    while True:
        try:
            (conn, addr) = server_socket.accept()  # wait for client
            Thread(target=sock_handler, args=(conn, addr)).start()
        except (KeyboardInterrupt):
            print("Server Quitting...")
            server_socket.close()
        
if __name__ == "__main__":
    main()

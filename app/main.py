# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    (conn, addr) = server_socket.accept()  # wait for client
    with conn:
        print(f"Connected by {addr}")
        # data = bytes object
        data = conn.recv(1024)
        # data_str = str
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
        else:
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        print("Closing Client Connection...")
        conn.close()
    print("Closing Server Connection...")
    server_socket.close()


if __name__ == "__main__":
    main()

# Uncomment this to pass the first stage
import socket
from threading import Thread
from os.path import isfile, exists
from sys import argv


class Server:
    def __init__(self):
        self.server_socket = socket.create_server(
            ("localhost", 4221), reuse_port=True)
        self.conn_list = list()
        self.ACCEPTED_ENCODINGS = ['gzip']

    def listen_loop(self):
        print("Server Starting...")
        while True:
            try:
                (conn, addr) = self.server_socket.accept()  # wait for client
                Thread(target=self._sock_handler,
                       args=(conn, addr)).start()
            except (Exception, KeyboardInterrupt):
                self._cleanup()
                return

    def _get_directory_cmd(self) -> str:
        return argv[2]

    def _get_path(self, data: bytes) -> str:
        return data.decode().split(" ")[1]

    def _get_user_agent(self, data: bytes) -> str:
        if ('User-Agent' not in data.decode()):
            return ""
        return (data.decode().split('User-Agent:')[1].split('\r\n')[0]).strip()

    def _get_filename(self, data: bytes) -> str:
        return "/".join(data.decode().split(' ')[1].split('/')[2:])

    def _get_method(self, data: bytes) -> str:
        return data.decode().split(' ')[0]

    def _get_accept_encoding(self, data: bytes) -> str:
        # Check if the content encoding is specified
        data_str = data.decode()
        if 'Accept-Encoding' not in data_str:
            return ""
        # Check if multiple encodings are specified
        # If so check if one is in the accepted encodings
        if ',' in data_str.split('Accept-Encoding:')[1].split('\r\n')[0]:
            encodings = data_str.split('Accept-Encoding:')[1].split('\r\n')[0].split(',')
            for encoding in encodings:
                if encoding.strip() in self.ACCEPTED_ENCODINGS:
                    return encoding.strip()
            return ""
        # If only one encoding is specified
        encoding = data_str.split('Accept-Encoding:')[1].split('\r\n')[0].strip()
        if encoding in self.ACCEPTED_ENCODINGS:
            return encoding
        return ""

    def _sock_handler(self, conn: socket, addr: str):
        self.conn_list.append(conn)
        print(f"Connected by {addr}")
        # data = bytes object
        data = conn.recv(1024)
        # path = str
        path = self._get_path(data)
        match(path):
            case '/':
                conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
            case s if s.startswith('/echo'):
                self._echo_handler(conn, data)
            case s if s.startswith('/user-agent'):
                self._user_agent_handler(conn, data)
            case s if s.startswith('/files') and self._get_method(data) == 'GET':
                self._files_get_handler(conn, data)
            case s if s.startswith('/files') and self._get_method(data) == 'POST':
                self._files_post_handler(conn, data)
            case _:
                conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
        print(f"Closing Client Connection for {addr}")
        self.conn_list.remove(conn)
        conn.close()

    def _echo_handler(self, conn: socket, data: bytes) -> None:
        path = self._get_path(data)
        # Check if the path has a word to echo
        if len(path.split("/")) < 3:
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return
        wordToEcho = path.split("/")[2]
        accept_encoding = self._get_accept_encoding(data)
        if accept_encoding:
            echoBytes = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Encoding: {accept_encoding}\r\nContent-Length: {len(wordToEcho)}\r\n\r\n{wordToEcho}".encode(
            )
        else:
            echoBytes = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(wordToEcho)}\r\n\r\n{wordToEcho}".encode(
            )
        conn.send(echoBytes)

    def _user_agent_handler(self, conn: socket, data: bytes):
        userAgent = self._get_user_agent(data)
        if not userAgent:
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return
        userAgentBytes = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(userAgent)}\r\n\r\n{userAgent}".encode(
        )
        conn.send(userAgentBytes)

    def _files_get_handler(self, conn: socket, data: bytes):
        filename = self._get_filename(data)
        directory = self._get_directory_cmd()
        if not directory:
            print("No directory specified.")
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return
        file_exists = exists(f"{directory}/{filename}")
        if not file_exists:
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return
        file = open(f"{directory}/{filename}", 'r')
        file_contents = file.read()
        file.close()
        send_string = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(file_contents)}\r\n\r\n{file_contents}"
        conn.send(send_string.encode())

    def _files_post_handler(self, conn: socket, data: bytes):
        fileName = self._get_filename(data)
        directory = self._get_directory_cmd()
        if not directory:
            print("No directory specified.")
            conn.send(b"HTTP/1.1 404 Not Found\r\n\r\n")
            return
        file_exists = exists(f"{directory}/{fileName}")
        if file_exists:
            conn.send(b"HTTP/1.1 409 Conflict\r\n\r\n")
            return
        contents_to_file = data.decode().split('\r\n\r\n')[1]
        file = open(f"{directory}/{fileName}", 'w')
        file.write(contents_to_file)
        file.close()
        conn.send(b"HTTP/1.1 201 Created\r\n\r\n")

    def _cleanup(self):
        print("Cleaning up...")
        for conn in self.conn_list:
            conn.close()
        self.server_socket.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    server = Server()
    server.listen_loop()


if __name__ == "__main__":
    main()

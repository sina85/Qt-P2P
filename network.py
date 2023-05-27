import socket
import threading
import time

class NetworkManager:
    def __init__(self, local_ip, local_port):
        self.local_ip = local_ip
        self.local_port = local_port
        self.chat_window = None


        # Create a UDP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.local_ip, self.local_port))

        # Initialize a list to store active connections
        self.active_connections = []

        # Initialize a boolean to control the receiving thread
        self.receiving = True

        # Message ID tracking
        self.last_message_id_sent = 0
        self.last_message_id_received = 0

        # Store messages with their IDs for potential retransmission
        self.sent_messages = {}

        # Start the thread for receiving messages
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()

    def add_connection(self, ip, port):
        self.active_connections.append((ip, port))
    def set_chat_window(self, chat_window):
        self.chat_window = chat_window

    def send(self, message, header, ip, port):
        # Encrypt the message

        # Increase the message id
        self.last_message_id_sent += 1

        # The message format is as follows: id|header|data
        full_message = f"{self.last_message_id_sent}|{header}|{message}"
        self.sent_messages[self.last_message_id_sent] = full_message

        self.sock.sendto(full_message.encode(), (ip, port))

    def receive(self):
        while self.receiving:
            data, addr = self.sock.recvfrom(1024)

            # Decrypt the message

            # Parse the id, header and data
            message_id, header, data = data.decode().split("|", 2)

            # If the message id is not the expected one, request the missing message
            if int(message_id) != self.last_message_id_received + 1:
                self.request_missing_message(self.last_message_id_received + 1, addr[0], addr[1])
            else:
                # Increase the last received message id
                self.last_message_id_received += 1

                # Process the message based on the header
                self.process_message(header, data, addr[0], addr[1])

    def request_missing_message(self, message_id, ip, port):
        # The header for requesting a missing message is 'request'
        self.send(f"{message_id}", "request", ip, port)

    def resend_message(self, message_id, ip, port):
        # Get the message associated with the message id and resend it
        message_to_resend = self.sent_messages.get(message_id)
        if message_to_resend:
            self.sock.sendto(message_to_resend.encode(), (ip, port))


    def process_message(self, header, data, ip, port):
        if header == 'request':
            # If a request is received, resend the requested message
            self.resend_message(int(data), ip, port)
        elif header == 'keep_alive':
            # If a keep-alive message is received, handle it accordingly
            pass
        else:
            # Otherwise, handle the message based on its type
            # Find the conversation related to this ip and port
            for conversation in self.chat_window.conversations:
                if conversation.ip == ip and conversation.port == port:
                    # Add the received message to the conversation
                    self.chat_window.add_message_to_conversation("Friend", data)

    def keep_alive(self):
        while self.receiving:
            for ip, port in self.active_connections:
                # Send a keep-alive message to each active connection
                self.send("", "keep_alive", ip, port)
            time.sleep(10)

    def close(self):
        self.receiving = False
        self.receive_thread.join()
        self.sock.close()
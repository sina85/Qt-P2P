from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QListWidget, QListWidgetItem, QMessageBox
from PyQt5 import QtCore
from cryptography.fernet import Fernet
from network import NetworkManager
from crypto import CryptoProvider
import os
import json

class Conversation:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.history = []

    def add_message(self, sender, message):
        self.history.append((sender, message))

    def to_json(self):
        return json.dumps({
            'ip': self.ip,
            'port': self.port,
            'name': self.name,
            'history': self.history
        })


class ChatWindow(QWidget):
    def __init__(self, network_manager, crypto_provider):
        super().__init__()

        # Create a horizontal main layout
        self.layout = QHBoxLayout()

        # Create a vertical layout for the list of conversations
        self.conversationsLayout = QVBoxLayout()

        # Create a list for conversations
        self.conversationsList = QListWidget()
        self.conversationsList.itemClicked.connect(self.load_conversation)

        # Add the list to the conversations layout
        self.conversationsLayout.addWidget(self.conversationsList)

        # Create a vertical layout for the chat window
        self.chatLayout = QVBoxLayout()

        # Create text edit for chat history, line edit for typing messages, and send button
        self.chatHistory = QTextEdit()
        self.chatHistory.setReadOnly(True)
        self.messageField = QLineEdit()
        self.sendButton = QPushButton('Send')
        self.sendButton.clicked.connect(self.send_message)

        # Add widgets to chat layout
        self.chatLayout.addWidget(self.chatHistory)
        self.chatLayout.addWidget(self.messageField)
        self.chatLayout.addWidget(self.sendButton)

        # Add conversations and chat layouts to the main layout
        self.layout.addLayout(self.conversationsLayout)
        self.layout.addLayout(self.chatLayout)

        # Set the layout
        self.setLayout(self.layout)

        # Initialize a blank conversation
        self.current_conversation = Conversation("", 0, "")

        # Create fields for adding a new friend
        self.friendIpField = QLineEdit()
        self.friendPortField = QLineEdit()
        self.friendNameField = QLineEdit()
        self.addFriendButton = QPushButton('Add Friend')
        self.addFriendButton.clicked.connect(self.add_friend_button_clicked)

        # Add friend fields and button to the conversations layout
        self.conversationsLayout.addWidget(QLabel("Add a new friend:"))
        self.conversationsLayout.addWidget(QLabel("IP:"))
        self.conversationsLayout.addWidget(self.friendIpField)
        self.conversationsLayout.addWidget(QLabel("Port:"))
        self.conversationsLayout.addWidget(self.friendPortField)
        self.conversationsLayout.addWidget(QLabel("Name:"))
        self.conversationsLayout.addWidget(self.friendNameField)
        self.conversationsLayout.addWidget(self.addFriendButton)

        self.network_manager = network_manager
        self.crypto_provider = crypto_provider
        self.conversations = []
        self.load_conversations()
        self.load_friends()
    
    def display_conversation(self, conversation):
        # Create a QListWidgetItem and set its data to the conversation
        item = QListWidgetItem(conversation.name if conversation.name else f"{conversation.ip}:{conversation.port}")
        item.setData(QtCore.Qt.UserRole, conversation)

        # Add the item to the conversations list
        self.conversationsList.addItem(item)


    def load_conversations(self):
        if os.path.exists('conversations.json'):
            with open('conversations.json', 'r') as f:
                conversations_data = json.load(f)
                for conversation_data in conversations_data:
                    conversation = Conversation(conversation_data['ip'], conversation_data['port'])
                    conversation.name = conversation_data['name']
                    conversation.history = conversation_data['history']
                    self.conversations.append(conversation)
                    self.add_conversation_to_list(conversation)

    def add_conversation(self, conversation):
        self.conversations.append(conversation)
        self.add_conversation_to_list(conversation)
        self.save_conversations()

    def add_conversation_to_list(self, conversation):
        item = QListWidgetItem(conversation.name)
        item.setData(QtCore.Qt.UserRole, conversation)
        self.conversationsList.addItem(item)

    def save_conversations(self):
        with open('conversations.json', 'w') as f:
            json.dump([conversation.to_json() for conversation in self.conversations], f)

    def load_conversation(self, item):
        # Get the selected conversation
        self.current_conversation = item.data(QtCore.Qt.UserRole)

        # Load chat history into the text edit
        self.chatHistory.setText("\n".join(f"{message[0]}: {message[1]}" for message in self.current_conversation.history))

    def send_message(self):
        message = self.messageField.text()
        if message:
            header = "text"
            for ip, port in self.network_manager.active_connections:
                self.network_manager.send(message, header, ip, port)
            self.add_message_to_conversation("You", message)

    def add_message_to_conversation(self, sender, message):
        self.current_conversation.add_message(sender, message)
        self.chatHistory.append(f"{sender}: {message}")
        self.save_conversations()


    def add_friend(self, ip, port, name):
        try:
            # Add the new friend to the network manager's active connections
            self.network_manager.add_connection(ip, port)
            
            new_friend = Conversation(ip, port, name)
            self.conversations.append(new_friend)
            self.display_conversation(new_friend)


            # Save the new friend's information into a file
            self.save_friends()
            QMessageBox.information(self, 'Success', f"Successfully added {ip}:{port} as a new friend.")
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"An error occurred: {str(e)}")

    def save_friends(self): #FIXME: create a better save functionality based on conversations list
        with open('friends.txt', 'w') as f:
            for ip, port in self.network_manager.active_connections:
                f.write(f"{ip}:{port}\n")
    def add_friend_button_clicked(self):
        ip = self.friendIpField.text()
        port = int(self.friendPortField.text())  # Convert the text input to an integer
        name = self.friendNameField.text()
        self.add_friend(ip, port, name)

    def load_friends(self):
        if os.path.exists('friends.txt'):
            with open('friends.txt', 'r') as f:
                for line in f.readlines():
                    ip, port = line.strip().split(':')
                    self.network_manager.add_connection(ip, int(port))


# Create the Qt Application
app = QApplication([])
local_ip = '127.0.0.1'
local_port = 29152
crypto_provider = CryptoProvider()
network_manager = NetworkManager(local_ip, local_port)

window = ChatWindow(network_manager, crypto_provider)
network_manager.set_chat_window(window)  # set the chat_window reference in NetworkManager after creating the ChatWindow
window.show()

# Run the main Qt loop
app.exec_()

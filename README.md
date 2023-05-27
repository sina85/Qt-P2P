# P2P Encrypted Chat Application

This project is an encrypted peer-to-peer chat application built with Python and PyQt5. It uses UDP for network communication and the Cryptography library for message encryption.

## Features

- **End-to-end Encryption**: All messages are encrypted locally before transmission and decrypted at the receiver's end, ensuring security and privacy.
- **Peer-to-Peer Communication**: Direct communication between peers without the need for a centralized server.
- **User-friendly Interface**: The application features a GUI built with PyQt5, offering intuitive controls for adding friends, sending messages, and viewing conversation history.
- **Persistent Conversations**: Conversation history is stored locally and loaded upon startup, preserving past chats.
- **Network Resilience**: The application handles network errors and packet loss by requesting missing packets, ensuring message delivery.
- **Multi-threaded**: The application uses multi-threading to handle network communication and user interaction simultaneously.

## Future Improvements

- Implement file sending and video chat functionality
- Implement a GUI for adding friends
- Better error handling

## Getting Started

### Prerequisites

You need Python 3.x and pip installed on your system. You will also need the following Python libraries:
- PyQt5
- Cryptography

You can install them using pip:
```pip install PyQt5 cryptography```
### Running the application
To run the application, navigate to the directory containing the project files and run:

```python main.py```

Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

License
MIT

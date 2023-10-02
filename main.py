import subprocess
import socket
import pickle
import os

# Константы для путей к файлам
SERVER_PORT = 3001
ROOT_KEYPAIR_PATH = 'C:/Users/trudo/PycharmProjects/zi_lab7_client/root_keypair.pem'
ROOT_CSR_PATH = 'C:/Users/trudo/PycharmProjects/zi_lab7_client/root_csr.pem'
ROOT_CERT_PATH = 'C:/Users/trudo/PycharmProjects/zi_lab7_client/root_cert.pem'
FILE_PATH = 'C:/Users/trudo/PycharmProjects/zi_lab7_client/file_to_server.txt'
ENCRYPTED_FILE_PATH = 'C:/Users/trudo/PycharmProjects/zi_lab7_client/encrypted_file.txt'

def generate_rsa_key():
    # Генерация приватного и публичного ключей RSA с помощью OpenSSL
    command_to_send = f'openssl genpkey -algorithm RSA -out {ROOT_KEYPAIR_PATH}'
    subprocess.run(command_to_send, check=True)

def generate_root_csr():
    # Создание запроса на сертификат (CSR) с использованием ключей RSA с помощью OpenSSL
    command_to_send = f'openssl req -new -subj "/CN=Root CA" -addext "basicConstraints=critical,CA:TRUE" -key {ROOT_KEYPAIR_PATH} -out {ROOT_CSR_PATH}'
    subprocess.run(command_to_send, check=True)

def generate_root_cert():
    # Генерация сертификата с использованием CSR и ключей RSA с помощью OpenSSL
    command_to_send = f'openssl x509 -req -in {ROOT_CSR_PATH} -copy_extensions copyall -key {ROOT_KEYPAIR_PATH} -days 3650 -out {ROOT_CERT_PATH}'
    subprocess.run(command_to_send, check=True)

def encrypt_file():
    # Зашифровка файла с использованием сертификата с помощью OpenSSL
    command_to_send = f'openssl smime -encrypt -binary -aes-256-cbc -in {FILE_PATH} -out {ENCRYPTED_FILE_PATH} -outform DER {ROOT_CERT_PATH}'
    subprocess.run(command_to_send, check=True)

def start_server(SERVER_PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', SERVER_PORT))
    server_socket.listen(1)
    print("Сервер запущен и ожидает подключения...")
    return server_socket

server_socket = start_server(SERVER_PORT)

def run_server():
    generate_rsa_key()
    generate_root_csr()
    generate_root_cert()

    while True:
        client_socket, client_address = server_socket.accept()
        print("Подключение от: ", client_address)

        # Принимаем файл от клиента
        file_data = client_socket.recv(1024)
        file_name, file_content = pickle.loads(file_data)

        # Сохраняем полученный файл
        with open(file_name, 'wb') as file:
            file.write(file_content)

        # Зашифровываем файл
        encrypt_file()

        # Отправляем зашифрованный файл клиенту
        with open(ENCRYPTED_FILE_PATH, 'rb') as file:
            encrypted_file_content = file.read()

        response = pickle.dumps((ENCRYPTED_FILE_PATH, encrypted_file_content))
        client_socket.sendall(response)

        # Закрываем соединение
        client_socket.close()

run_server()

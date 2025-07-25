"""
@module
"""
import ftplib
import os
import io
import time
from settings import read_yaml

class FTPConnection:
    def __init__(self,album_path,filename):
        self.album_path = album_path
        self.filename = filename
        self.ftp_server = None
        self.errors = []
        self.connect()

    def connect(self):
        ftp_config = read_yaml(os.path.join(os.getcwd(), ".ftp_connect.yml"))
        HOSTNAME = ftp_config.get('hostname')
        USERNAME = ftp_config.get('user')
        PASSWORD = ftp_config.get('password')
        MUSIC_DIR = ftp_config.get('music_dir')
        try:
            self.ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
            print(f"Connected to FTP server {HOSTNAME}")
            # print(self.ftp_server.dir())
            self.ftp_server.cwd(f'{MUSIC_DIR}')
            self.ftp_server.cwd(f'{self.album_path}')
            print(self.ftp_server.dir())
        except ConnectionError:
            print("Connection to FTP server failed. Exiting...")
            self.errors.append(ConnectionError)

    def get_io_stream(self):
        try:
            memory_buffer = io.BytesIO()
            file_size = ftplib.size(f"{self.filename}")
            self.ftp_server.retrbinary(f"RETR {self.filename}",memory_buffer.write)
            memory_buffer.seek(0)
            return memory_buffer
        except ftplib.error_perm as e:
            print(f"Error reading remote file '{self.album_path}/{self.filename}': {e} (Permission denied or file not found)")

        except Exception as e:
            print(f"An unexpected error occurred while reading remote file '{self.album_path}/{self.filename}': {e}")

    def close(self):
        self.ftp_server.quit()


def print_contents(chunk):
    print(chunk)


if __name__ == '__main__':
    start = time.time()
    connection = FTPConnection('Albinoni_TG_-_[1988]_12_Concerti_A_Cinque_Op_5__Pina_Carmirelli_I_Musici',
                               '05_Concerto_A_Cinque_5_In_A_Minor_Op_5_5.flac')
    connection.get_io_stream()
    connection.close()
    print(time.time()-start,"s")


"""
@module
"""
import ftplib
import os
import io
import time
from settings import read_yaml

class FTPConnection:
    """
    This class represents an FTP connection to the FTP server.
    """
    def __init__(self,album_path,filename):
        self.album_path = album_path
        self.filename = filename
        self.ftp_server = None
        self.errors = []
        self.connect()

    def connect(self):
        """
        This method connects to the database.
        :return: void
        """
        ftp_config = read_yaml(os.path.join(os.getcwd(), ".ftp_connect.yml"))
        hostname = ftp_config.get('hostname')
        username = ftp_config.get('user')
        password = ftp_config.get('password')
        music_dir = ftp_config.get('music_dir')
        try:
            self.ftp_server = ftplib.FTP(hostname, username, password)
            print(f"Connected to FTP server {hostname}")
            # print(self.ftp_server.dir())
            self.ftp_server.cwd(f'{music_dir}')
            self.ftp_server.cwd(f'{self.album_path}')
            print(self.ftp_server.dir())
        except ConnectionError:
            print("Connection to FTP server failed. Exiting...")
            self.errors.append(ConnectionError)

    def get_io_stream(self):
        """
        This method gets an I/O stream
        :return: A memory buffer on success or None on error.
        """
        try:
            memory_buffer = io.BytesIO()
            # file_size = ftplib.size(f"{self.filename}")
            self.ftp_server.retrbinary(f"RETR {self.filename}",memory_buffer.write)
            memory_buffer.seek(0)
            return memory_buffer
        except ftplib.error_perm as e:
            print(f"Error reading remote file '{self.album_path}/{self.filename}': "
                  f"{e} (Permission denied or file not found)")
            return None

        except Exception as e:  # pylint: disable=broad-except
            print("An unexpected error occurred while reading remote file " + \
                      f"'{self.album_path}/{self.filename}': {e}")
            return None

    def close(self):
        """
        Close FTP connection.
        :return:
        """
        self.ftp_server.quit()


def print_contents(chunk):
    """
    This method output chung contents
    :param chunk: Chunk whose contents to output
    """
    print(chunk)


if __name__ == '__main__':
    start = time.time()
    connection = FTPConnection(
        'Albinoni_TG_-_[1988]_12_Concerti_A_Cinque_Op_5__Pina_Carmirelli_I_Musici',
        '05_Concerto_A_Cinque_5_In_A_Minor_Op_5_5.flac')
    connection.get_io_stream()
    connection.close()
    print(time.time()-start,"s")

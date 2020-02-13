import ftplib
from io import BytesIO

def get_ftp_client(ftp_server, ftp_username, ftp_password):
    ftp_client = ftplib.FTP(ftp_server, ftp_username, ftp_password)
    return ftp_client

def get_file_from_ftp(ftp_client, filename):
    r = BytesIO()
    ftp_client.retrbinary('RETR ' + filename, r.write)
    return r
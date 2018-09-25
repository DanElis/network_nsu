import socket
import argparse
import os
import struct
import threading

BUFFER_SIZE = 1024
UPLOAD_DIR = 'uploads/'
#conn = socket()
def main():
	parser = argparse.ArgumentParser(description="Receive files from clients")
	parser.add_argument('port', type=int, help='Port to listen to', metavar='Port')
	args = parser.parse_args()

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', args.port))
	sock.listen(10)
	while (True):
		conn, addr = sock.accept()
		print(type(conn))
		print('Connection address: {0}'.format(addr))
		#threading.Thread(target=my_tcp_server).start()
		my_tcp_server(conn)
		break

def my_tcp_server(conn):
	data = conn.recv(BUFFER_SIZE)
	conn.setblocking(0)
	conn.settimeout(2)
	size_file,filename_size = struct.unpack('qH', data[:10])
	
	filename = str(data[10:], "utf8")
	file = open(UPLOAD_DIR + filename[:filename_size], 'wb+')
	if(len(filename) == filename_size):
		data = conn.recv(BUFFER_SIZE)
	else:
		data = bytes(filename[filename_size:],"utf8")
	while(size_file > 0):
		size_file -= BUFFER_SIZE
		file.write(data)
		try:
			data = conn.recv(BUFFER_SIZE)
		except socket.timeout:
			continue
	file.close()
	conn.send(struct.pack('!b', 0))
	conn.close()

if __name__ == "__main__":
	main()

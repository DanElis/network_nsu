import socket
import argparse
import os
import struct
from os.path import basename
BUFFER_SIZE = 4096

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Send file to remote server")
	parser.add_argument('file', type=str, help='File to send', metavar='File')
	parser.add_argument('host', type=str, help='Destination host', metavar='Server')
	parser.add_argument('port', type=int, help='Destination port', metavar='Port')
	args = parser.parse_args()

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((args.host, args.port))
	try:
		with open(args.file, 'rb') as file:
			sock.send(struct.pack("qH", os.path.getsize(args.file),len(bytes(args.file,'utf-8')))+bytes(basename(file.name), 'utf-8'))
			data = file.read(BUFFER_SIZE)
			while len(data) > 0:
				sock.send(data)
				data = file.read(BUFFER_SIZE)
		data = sock.recv(1)
	finally:
		sock.close()

	info = struct.unpack('!b', data[:1])
	if(info[0] == 1):
		print("EXISTS")
	else:
		print("NOT EXISTS")


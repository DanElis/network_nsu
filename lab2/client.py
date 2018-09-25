import socket
import argparse
import os
import struct

BUFFER_SIZE = 1024

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Send file to remote server")
	parser.add_argument('file', type=str, help='File to send', metavar='File')
	parser.add_argument('host', type=str, help='Destination host', metavar='Server')
	parser.add_argument('port', type=int, help='Destination port', metavar='Port')
	args = parser.parse_args()

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((args.host, args.port))

	with open(args.file, 'rb') as file:
		sock.send(struct.pack("q", os.path.getsize(args.file)))
		sock.send(struct.pack('H', len(args.file)))
		sock.send(bytes(file.name, 'utf8'))
		data = file.read(BUFFER_SIZE)
		while len(data) > 0:
			sock.send(data)
			data = file.read(BUFFER_SIZE)
	'''data = sock.recv(5)
	print(data.decode("utf8"))
	if(data.decode("utf8") == ""):
		print("EXISTS")
	else:
		print("NOT EXISTS")'''

import socket
import argparse
import os
import struct
from _thread import start_new_thread
import threading
import signal
import time
import traceback

BUFFER_SIZE = 4096
UPLOAD_DIR = 'uploads/'
TIMEOUT_SECONDS = 3
FILE_INFO_SIZE = 10
INSTANT_SPEED = 0
AVERAGE_SPEED = 1
START_TIME = 2
lock = threading.Lock()
info_speed = dict()
def main():
	parser = argparse.ArgumentParser(description="Receive files from clients")
	parser.add_argument('port', type=int, help='Port to listen to', metavar='Port')
	args = parser.parse_args()

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', args.port))
	sock.listen(10)

	try:	
		signal.signal(signal.SIGALRM, handle_timeout)
		signal.alarm(TIMEOUT_SECONDS)
		while(True):
			conn, addr = sock.accept()
			print('Connection address: {0}'.format(addr))
			start_new_thread(client_thread, (conn,))
			
	except KeyboardInterrupt:
		print("")
	finally:
		sock.close()
		conn.close()

def client_thread(conn):
	conn.settimeout(60)
	try:
		init_speed(conn)
		data = read_file_info(conn)
		size_file,filename_size = struct.unpack('qH', data[:10])
		filename = read_filename(filename_size,conn)
		file = open(UPLOAD_DIR + filename[:filename_size], 'wb+')
			
		while (file.tell() < size_file):
			data = conn.recv(BUFFER_SIZE)
			update_speed(key = conn,length_data = len(data))
			if not data:
				break
			file.write(data)
		conn.send(struct.pack('!b', 1))
	except BaseException:
		conn.send(struct.pack('!b', 2))
	finally:
		delete_speed(conn)
		file.close()
		conn.close()
def init_speed(key):
	lock.acquire()
	info_speed[key] = [0,0,time.time()]
	lock.release()
def delete_speed(key):
	lock.acquire()
	del(info_speed[key])
	lock.release()
def read_file_info(conn):
	data = conn.recv(FILE_INFO_SIZE)
	while(len(data) != 10):
		data += conn.recv(FILE_INFO_SIZE - len(data))
	return data
def update_speed(key,length_data):
	lock.acquire()
	info_speed[key][INSTANT_SPEED] += length_data
	info_speed[key][AVERAGE_SPEED] += length_data
	lock.release()
def handle_timeout(signum,frame):
	lock.acquire()
	for key in info_speed:
		print(key)
		print("Instant speed bytes/s")
		print(info_speed[key][INSTANT_SPEED]/TIMEOUT_SECONDS)
		print("Average speed bytes/s")
		print(info_speed[key][AVERAGE_SPEED]/(time.time()-info_speed[key][START_TIME]))
		info_speed[key][INSTANT_SPEED] = 0
	lock.release()
	signal.alarm(TIMEOUT_SECONDS)
def read_filename(filename_size,conn):
	filename = conn.recv(filename_size)
	while(len(filename) != filename_size):
		filename += conn.recv(filename_size-len(filename))

	return str(filename[:filename_size], "utf-8")

if __name__ == "__main__":
	main()
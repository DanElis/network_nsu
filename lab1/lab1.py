MYPORT = 8123

import time
import struct
import socket
import sys
import ipaddress

def main():
	joinedCopies = {}
	try:
		group = sys.argv[1]
		ipaddress.ip_address(sys.argv[1])
	except ValueError:
		print('Invalid multicast IP')
		return
	addrinfo = socket.getaddrinfo(group, None)[0]
	s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
	s.setblocking(0)
	s.settimeout(1)

	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
	add = socket.getaddrinfo(group, MYPORT, 0, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
	ttl_bin = struct.pack('@i', 1)
	if addrinfo[0] == socket.AF_INET: # IPv4
		s.bind((group, MYPORT))
		mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
		s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
		s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
	else: # IPv6
		s.bind(("",MYPORT))
		mreq = group_bin + struct.pack('@I', 0)
		s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)
		s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
	my_key = repr(int(time.time()))

	sendmsg = "live"+my_key
	s.sendto((sendmsg + '\0').encode(), (addrinfo[4][0], MYPORT))
	try:
		while True:
			try:
				start = time.time()
				data, sender = s.recvfrom(1500)
				while data[-1:] == '\0': data = data[:-1]
				if (str(data).find('live') != -1):
					key = str(data)[6::]
					if(not(key in joinedCopies)):
						joinedCopies[key] = (time.time(),sender)
						print_list(joinedCopies)
					else:
						joinedCopies[key] = (time.time(),sender)
					is_live(joinedCopies)

				elif(str(data).find('leave') != -1):
					key = str(data)[7::]
					del(joinedCopies[key])
					print_list(joinedCopies)
					is_live(joinedCopies)			
					
			except socket.timeout:
				time.sleep(3-time.time()+start)
				s.sendto((sendmsg + '\0').encode(), (addrinfo[4][0], MYPORT))
	except KeyboardInterrupt:
		s.sendto(("leave" + my_key+'\0').encode(), (addrinfo[4][0], MYPORT))
		return 

def print_list(joinedCopies):
	print("\nJoined copies")
	for key in joinedCopies:
		print(joinedCopies[key][1])

	#print([joinedCopies[key][1] for key in joinedCopies.keys()])	

def is_live(joinedCopies):
	now = time.time()
	for key in joinedCopies.copy():
		if(now - joinedCopies[key][0] > 15):
			del(joinedCopies[key])
			print_list(joinedCopies)


if __name__ == '__main__':
	main()
from ctypes import *

class Ethdll():
	"""Rewrite functions in ETHDLL.dll

	Make a class to simplify doing with ETHDLL.dll
	"""

	def __init__(self, path, ip):
		'''init this object

		path: ETHDLL.dll 's path (string)
			Plus '\\\\' at the end!
		ip: the instrument's ip address (string)
		'''

		self.path = path
		self.dll = WinDLL(path + 'ETHDLL.dll')
		ip = c_char_p(ip)
		self.ip = self.dll.IP_StrToInt(ip)

	def SysInit(self):
		'''Init system before you use the instrument

		return 1 if init successfully and 0 for fail
		'''

		c_ints = c_int * 1
		ips = c_ints(self.ip)

		return self.dll.SysInit(ips, len(ips))

	def SysClose(self):
		'''Close sys
		'''
		
		self.dll.SysClose()

	def ConnectCreate(self, report, loport, type, outtime, trytime):
		'''Create Connections

		Inputs:
		report: port of instrument, it should be 1600
		loport: local port to connect, 0 for automatically choose
		type: type of connection, 0 for UDP, 1 for TCP
		outtime: overtime set, it should be larger than 100(ms)
		num: try times, 3 maybe a good choice

		save socket and return
		if socket >= 0: connect successful
		if socket == -1: overtime
		if socket == -2: can't make more socket connection
		if socket == -3: haven't SysInit()
		if socket == -4: UDP faild
		if socket == -5: TCP faild
		if socket == -6: in TCP type, build socket successfully but connect faild
		'''

		self.socket = self.dll.ConnectCreate(self.ip, report, loport, type, outtime, trytime)
		return self.socket
		# if self.socket >= 0:
		# 	return "connect successful"
		# elif self.socket == -1:
		# 	return "overtime"
		# elif self.socket == -2:
		# 	return "can't make more socket connection"
		# elif self.socket == -3:
		# 	return "haven't SysInit()"
		# elif self.socket == -4:
		# 	return "UDP faild"
		# elif self.socket == -5:
		# 	return "TCP faild"
		# elif self.socket == -6:
		# 	return "in TCP type, build socket successfully but connect faild"
		# else:
		# 	return: 'What happened???'

	def Version(self):
		'''retrun version

		if ip error return -1
		if para error return 0
		if overtimes return 2
		'''

		s = ''
		p = c_char_p(s)
		status = self.dll.VersionRead(p, self.socket)

		if status != 1:
			return status

		self.version = p.value

		return self.version

	def Name(self):
		'''return name and user's manual name

		return a list as [status, name, user's name]
		status: 1 if success, -1 for IP error, 0 for para error, 2 for overtime
		'''

		strTemp1 = ''
		strTemp2 = ''
		name1 = c_char_p(strTemp1)
		name2 = c_char_p(strTemp2)
		stat = self.dll.NameRead(name1, name2, self.socket)

		return [stat, name1.value, name2.value]

	def  ADSyncParaWrite(self, freq, range, select, enabled, flag):
		'''Sync A/D setings

		return 1 if success, -1 for IP error, 0 for para error, 2 for overtime
		'''
		self.range = self.ADRange(range)
		self.enabled = enabled
		
		enabled = '1' * enabled + '0' * (16 - enabled)
		enabled = int(enabled, 2)
		stat = self.dll.ADSyncParaWrite(freq, range, select, enabled, flag, self.socket)

		return stat

	def ADTriggerWrite(self, enabled, type, clk, num, vol):
		pass

	def ADStart(self):
		'''Start A/D

		return 1 if success, -1 for IP error, 0 for para error, 2 for overtime
		'''

		return self.dll.ADStart(self.socket)

	def  ADStop(self):
		'''Stop A/D

		return 1 if success, -1 for IP error, 0 for para error, 2 for overtime
		'''

		return self.dll.ADStop(self.socket)

	def ADDataRead(self, count):
		'''Read A/D Data

		count: numbers of data Read
		
		return status and datas
		format: [stat, datas]
		stat: 1 if success, -1 for IP error, 0 for para error, 2 for overtime
		'''

		c_shorts = c_short * int(count)
		c_data = c_shorts()
		data = []
		stat = self.dll.ADDataRead(c_data, count, self.socket)
		for i in c_data:
			data.append(i)

		return [stat, data]

	def ADRange(self, range):
		'''Save A/D Range 10 or 5
		'''
		
		if range == 1:
			return 10
		elif range == 0:
			return 5
		else:
			return 'Range Error'

	def RealData(self, data):
		'''Calcuate real data
		'''

		real = []
		
		for i in data:
			real.append(float(i) * self.range / int('7fff', 16))

		return real
	
	def Format(self, data):
		'''Format data from list to dict
		'''

		datas = {}
		for i in range(0, self.enabled):
			datas['ch' + str(i)] = []
		for i in range(0, len(data)):
			datas['ch' + str(i%self.enabled)].append(data[i])

		return datas

	def FormatShow(self, data):
		'''Show data ( with dict format ) pretty!
		'''
		if(len(data) > 7):
			self.PrintTitle(0, len(data)/2)
			self.PartShow(data, 0, len(data)/2)
			print '\n',
			
			self.PrintTitle(len(data)/2, len(data))
			self.PartShow(data, len(data)/2, len(data))
			print '\n',
		else:
			self.PartShow(data, 0, len(data))
		
	def PartShow(self, data, start, end):
		'''Show part of data for print pretty
		'''
		
		for i in range(0, len(data['ch0'])):
			for j in range(start, end):
				print '%5.4f\t' % data['ch' + str(j)][i],
			print '\n',

	def PrintTitle(self, start, end):
		'''Print Title likes: ch0, ch1, ...
		'''
		for i in range(start, end):
			print 'ch' + str(i), '\t',
		print '\n', '-'*80
			
# if __name__ == '__main__':
	
# 	dll = Ethdll('F:\\wangwei\\', '172.22.49.252')

# 	print 'SysInit:', dll.SysInit()
# 	print 'ConnectCreate:', dll.ConnectCreate(1600, 0, 1, 500, 3)
# 	print 'Version:', dll.Version()
# 	print 'Name:', dll.Name()
# 	print 'ParaWrite:', dll.ADSyncParaWrite(40, 1, 0, 16, 0)
# 	print 'ADStart:', dll.ADStart()

# 	# One time show ~~
# 	stat, data = dll.ADDataRead(10 * dll.enabled)
# 	real = dll.RealData(data)
# 	real = dll.Format(real)
# 	dll.FormatShow(real)

# 	# Real time show ~~
# 	# dll.ADSyncParaWrite(40, 1, 0, 4, 0)
# 	# dll.PrintTitle(0, 4)
# 	# while 1:
# 	# 	stat, data = dll.ADDataRead(10*16)
# 	# 	data = dll.RealData(data)
# 	# 	data = dll.Format(data)
# 	# 	dll.PartShow(data, 0, 4)
	
# 	print 'ADStop:', dll.ADStop()
# 	print 'Close:', dll.SysClose()

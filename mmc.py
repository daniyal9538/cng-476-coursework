import time
import numpy as np
import operator as op
import csv
import os
import matplotlib.pyplot as plt

qLen = 0

class Q:
	
	def __init__(self):
		self.q= []#processes in queue
		self.lastArrival = 0#time at which the the most recent process arrives
		self.totalBusy = 0#the amount of time the server has been busy
		self.totalIdle = 0#amount of time the server has been idle
		self.totalWait = 0#the amount of time the processes in the server have had to wait
		self.lastProcess = 0#the time at which the most recent process finished
	def addProcess(self, Process):
		self.q.append(Process)

		
	def removeProcess(self, Process):
		self.q.remove(Process)
		
	def reset(self):
		del self.q[:] #processes in queue

	def populate(self, n, lbd):#populates the queue with processes and defines their arrival time
		totalTime = 0 	
		for i in range(0, n):
			if(len(self.q)==0):
				p = Process(0)
				self.addProcess(p)
				#print ("=====", self.q[len(self.q)-1].pId)
			else:
				totalTime = totalTime + randExp(lbd)
				p=Process(totalTime)
				self.addProcess(p)
				#print ("=====", self.q[len(self.q)-1].pId)
			#print ("=====", self.q[len(self.q)-1].pId)

		
		self.lastArrival = totalTime
	
	def processQ(self, lbd):#takes the populated queue and sets the time taken to process each item in queue
		for i in range(len(self.q)):
			self.q[i].updateProcessTime(randExp(lbd))

	def calculate(self):
		for i in range(len(self.q)):
			if(i==0):
				self.q[i].computeCompleteTime(0)
				#self.serverBusy += self.q[i].processTime
			else:
				self.q[i].computeCompleteTime(self.q[i-1].completeTime)
	
		"""NOTE: The total time the server is busy is the cummulative time it takes for the processes to be completed(processTime)
		The total time the server is idle, is the cummulative time the server was idle before each process
		The total time the server was active is the time between the recieving the first process, and finishing the last process"""
		


		for x in self.q:
			self.totalIdle+=x.idle
			self.totalBusy+=x.processTime
			self.totalWait+=x.wait
			self.lastProcess=x.completeTime
			self.lastArrival=x.arrival
		
class Process:
	pId=0

	def __init__(self, arrival):
		self.arrival = arrival#the time the process arrives to queue
		self.startTime = None#the time the process exits queue and goes to server
		self.completeTime = None#the time at which the process is completed and exits the server
		self.processTime = None#time taken for server to complete process
		self.wait  = None#time the process had to wait in queue after arrival
		self.id = Process.pId#ID of process
		Process.pId+=1
		self.idle = None#the time that the server was idle before dealing with the current process
		#NOTE: if the process had to wait in queue to get to the server, it means the server was not idle before dealing with that process
		self.qLen = 0 #the length of the queue at the chosen server when the process arrives
		self.serverID = None
		self.rejected = False
	def updateProcessTime(self, processTime):#set the time it takes for a process to be completed at the server
		self.processTime=processTime
	
	def computeCompleteTime(self, startTime):#takes arrival time of process and computes and updates it's completition time
		"""Only 2 possibilities:
        process arrives and is immedeately pushed to the server, (server is idle)
        process arrives and has to wait (server is busy)
        if startTime>arrival time, serve was busy
        else server was idle"""
		if(startTime>self.arrival):
			self.startTime = startTime
			self.completeTime=self.startTime+self.processTime
			self.wait=self.startTime-self.arrival
			self.idle=0
		else:
			self.startTime = self.arrival
			self.completeTime = self.startTime+self.processTime
			self.wait = 0
			self.idle = self.arrival - startTime

class Server:
	sId=0
	def __init__(self):
		self.id=Server.sId
		Server.sId+=1
		self.qu=Q()
		#self.lastArrival = 0#time at which the the most recent process arrives at the server
		self.totalBusy = 0#the amount of time the server has been busy
		#self.totalIdle = 0#amount of time the server has been idle
		self.totalWait = 0#the amount of time the processes in the server have had to wait before being sent to the server
		#self.lastProcess = 0#the time at which the most recent process finished
		self.serverUtil = 0#the percentage the server was busy during its operation
		self.avgWait = 0#the avg wait of the processes before they were sent to the server
		self.avgPtime = 0 #the average time each process took to be completed in the server
		self.upTime = 0#the amount of time th server was active
		self.firstProcess = 0#the time at which the first process arrives to the servers
		self.dropped = 0#the number of packets dropped due to bounded queue length l
		self.accepted = 0#the number of packets accepted into queue for server
		self.throughput = 0
		self.breakdowns = []
		self.repairs = []
		self.lastBreakdownAndRepair = 0
		self.brokenDown = False
		""""upTime is the moment the first process arrives to the server, 
		to the completion of the last process in the shared queue
				"""
		self.avgQLen = 0
		

	def enqueueProcess(self, Process):
		self.qu.addProcess(Process)
		self.qu.calculate()

	def calcStats(self, finalProcess):
		self.firstProcess = self.qu.q[0].arrival
		self.upTime = self.qu.q[len(self.qu.q)-1].completeTime - self.firstProcess
		for x in self.qu.q:
			self.totalWait +=x.wait
			self.totalBusy+=x.processTime
			self.avgQLen+=x.qLen


		self.avgWait = self.totalWait/len(self.qu.q)
		self.serverUtil = 100.00*(self.totalBusy)/(finalProcess-self.firstProcess)
		self.avgPtime = self.totalBusy/(len(self.qu.q))
		self.avgQLen = float(self.avgQLen/(len(self.qu.q)))
		self.throughput = self.upTime/self.accepted


	def printStats(self):
		print('Server ID:',self.id)
		print ("Start Time: {0:.2f}|Total time the server was busy: {1:.2f}|server Utilization(%): {2:.2f}|average Process completion Time in server: {3:.2f}|total Wait time for all the processes: {4:.2f}|Number Of Processes in server: {5}|average Wait time in server: {6:.2f}|NUmber of packets dropped: {7}|Number of packets accepted: {8}"
			.format(self.firstProcess, self.totalBusy, self.serverUtil, self.avgPtime, self.totalWait, len(self.qu.q), self.avgWait, self.dropped, self.accepted))
		stats = [self.serverUtil, self.avgPtime, self.avgWait, self.avgQLen, self.accepted, self.dropped, self.upTime, self.throughput]
		print("Average Queue Length {0:.2f}".format(self.avgQLen))
		print("Breakdown times", self.breakdowns)
		print("Repair times", self.repairs)
		return (stats)

	def printQData(self):
		print("ID\t\t||arrival\t||start\t\t||pTime\t\t||finish\t||wait\t\t||idleTime\t||Q Len\t\t||Broken Down")
		for x in self.qu.q:	
			print ("{0}\t\t||{1:.2f}\t\t||{2:.2f}\t\t||{3:.2f}\t\t||{4:.2f}\t\t||{5:.2f}\t\t||{6:.2f}\t\t||{7}\t\t||{8}".format(x.id, x.arrival, x.startTime, x.processTime,  x.completeTime, x.wait, x.idle, x.qLen, x.rejected))

	def exportServerData(self):
		name = "raw_server_{}_data.csv".format(self.id)
		if os.path.exists(name):
  			os.remove(name)
		a=[]
		a.append(['id', 'arrival time', 'start time', 'complete time', 'service time', 'wait time', 'q len at arrival', 'server id'])
		for i in self.qu.q:
			a.append( [i.id, i.arrival, i.startTime, i.completeTime, i.processTime, i.wait, i.qLen, i.serverID])
			
	#print('sas')
		with open(name, 'a') as wf:
			writer = csv.writer(wf)
			writer.writerows(a)
			

	
def printQData(x):
		#print("ID	||arrival||start||pTime	||finish||wait	||idleTime")
		#for x in self.qu.q:	
		print("ID	||arrival||start||pTime	||finish||wait	||")

		print ("{0}	||{1:.2f}	||{2:.2f}	||{3:.2f}	||{4:.2f}	||{5:.2f}	||".format(x.id, x.arrival, x.startTime, x.processTime,  x.completeTime, x.wait))



def randExp(lbd):
	R = np.random.uniform(0, 1)
	return float( np.log(1-R)*(-1.0/lbd))

def createServer(numOfServers):
	servers=[]
	for i in range(numOfServers):		
		servers.append(Server())
	return servers

def chooseServer(servers, q):#gets queue of all incoming processes and sends it to the available servers according to which one is idle or busy
		"""Servers can either be busy or idle
		The function loops through all servers and records the server with the earliest finish time 
		i.e, min(lastProcess)
		it send process to the server with the earliest finish time
		"""
		if(len(servers)!=0):#check if there are any servers intialized
			
			minServer = 0
			for i in range(len(q)):#go through all the processes in queue
				minTime = servers[0].qu.lastProcess
				for x in range(len(servers)):#loop through all the intialized servers
					
					if(minTime >= servers[x].qu.lastProcess):#get min(lastProcess)
						minServer = x
						minTime = servers[minServer].qu.lastProcess
				
				#printQData(q[i])
				if(len(servers[minServer].qu.q)== 0):
					servers[minServer].lastBreakdownAndRepair = q[i].arrival
				q[i].serverID = minServer
				servers[minServer].enqueueProcess(q[i])
				
				#printQData(q[i])
				t1 = 0
				t2 = q[i].arrival
				tRecent = 0

				for l in range(0, len(servers[minServer].qu.q)):
					temp = servers[minServer].qu.q[l]
					if(temp.completeTime>tRecent):
						tRecent=temp.completeTime
					#print(temp.id)
					if((tRecent)>t2):
						t1+=1
					#print(temp.id, t1, t2, temp.completeTime, tRecent)

				t1-=1
				q[i].qLen = t1
				#print("----", t1)
				if (breakdownEnabled == True):
					if(servers[minServer].brokenDown == False):
						#tempTime = 5
						tempTime = genBreakdown(b)
						#print(b, r)
						breakdownTime = tempTime + servers[minServer].lastBreakdownAndRepair
						if (q[i].arrival >= breakdownTime):
							servers[minServer].brokenDown = True
							servers[minServer].lastBreakdownAndRepair = breakdownTime
							servers[minServer].breakdowns.append(breakdownTime)
							print(1, breakdownTime, q[i].arrival )

					if(servers[minServer].brokenDown == True):
						#tempTime = 5
						tempTime = genRepair(r)
						#print(1, tempTime)
						repairTime = tempTime + servers[minServer].lastBreakdownAndRepair
						if (q[i].arrival >= repairTime):
							servers[minServer].brokenDown = False
							servers[minServer].lastBreakdownAndRepair = repairTime
							servers[minServer].repairs.append(repairTime)
							print(2, repairTime, q[i].arrival )

				servers[minServer].qu.removeProcess(q[i])
				if(t1 <= lq and servers[minServer].brokenDown == False):
					servers[minServer].enqueueProcess(q[i])
					servers[minServer].accepted +=1
				else:
					servers[minServer].dropped +=1
					q[i].rejected = True
				

				
			return servers[minServer].qu.lastProcess		

		else:
			print ("Error! No servers were intialized")
			exit()

def exportData(qu):
	a=[]
	a.append(['id', 'arrival time', 'start time', 'complete time', 'service time', 'wait time', 'q len at arrival', 'server id', 'Packet Rejected'])
	for i in qu.q:
		a.append( [i.id, i.arrival, i.startTime, i.completeTime, i.processTime, i.wait, i.qLen, i.serverID, i.rejected])
	
	name ='raw_data.csv'
	if os.path.exists(name):
  		os.remove(name)
	#print('sas')
	with open(name, 'a') as wf:
		writer = csv.writer(wf)
		writer.writerows(a)

def genBreakdown (shape):
	R = np.random.uniform(0, 1)
	return float( np.log(1-R)*(-1.0/shape))

def genRepair(mean):
	R = np.random.uniform(0, 1)
	return float( np.log(1-R)*(-1.0/mean))

for xi in range(1):
	breakdownEnabled = False
	filename = 'system_stats.csv'
	if os.path.exists(filename):
  		os.remove(filename)
	n = input("Enter number of processes in shared queue: ")
	c = input("Enter number of servers: ")
	lbd1 = input("Enter Mean Arrival Rate(lambda): ")
	lbd2 = input("Enter Mean Service Rate(mu): ")
	lq = input("Enter Queue Length (Enter -1 for infinite queue): ")
	b = input("Enter breakdowns per hour (Enter -1 to disable breakdowns and repairs): ")
	r = input("Enter repairs per hour (Enter -1 to disable breakdowns and repairs): ")
	b = float(b)
	r=float(r)
	if(b>0 and r >0):
		breakdownEnabled = True
		r=r/3600
		b=b/3600
		print("Breakdown rate: {}\nRepair Rate: {}".format(b, r))
	else:
		print("Breakdown and repair disabled")
	n = int(n)
	c=int(c)
	lbd1=float(lbd1)
	lbd2 = float(lbd2)
	lq = int(lq)
	
	#convert from /hour to /seconds
	
	# n = 10
	# c=1
	# lbd1 = 2
	# lbd2 = 2
	qu=Q()#shared queue
	qu.populate(n,lbd1)

	qu.processQ(lbd2)

	print ("Number of processes: {0}\nNumber of servers: {1}\nMean Arrival Rate(mu): {2}\nMean Service Rate(lambda): {3}\n".format(n, c, lbd1, lbd2))
	if(lq<0):
		print("Queue Length: Infinite")
		lq = 1e100
	else:
		print("Queue Length: {}".format(lq))
	
	servers = createServer(c)
	finishTime = chooseServer(servers, qu.q)

	wf = open(filename, 'a')
	writer = csv.writer(wf)
	t1 = [['server id', 'utilization', 'average service time', 'average wait time in queue', 'average queue length', 'number of packets processed', 'number of packets dropped', 'server uptime', 'server throughput', 'breakdown times', 'repair times']]
	writer.writerows(t1)
	t1.clear()
	stats = [float(0)]*8
	exportData(qu)
	for x in servers:
		print("-------------------------------------")
		x.printQData()
		x.calcStats(finishTime)
		temp = x.printStats()
		
		t1 = temp.copy()
		t1.insert(0, x.id)
		t1.append(x.breakdowns)
		t1.append(x.repairs)
		writer.writerows([t1])
		t1.clear()
		x.exportServerData()
		for i in range(len(temp)):
			stats[i] += temp[i]
		temp.clear()
	#print(stats)
	t1.append( ['Observed System Statistics'])
	# writer.writerows(t1)
	# tl.clear()
	t1.append(['Mean Server Utilization', 'Mean Average Service Time', 'Mean Average Wait Time in Queue',  'Mean System Response Time', 'Average Mean Queue Length of server queues', 'Average number of packet processed', 'Average number of packets dropped', 'System Throughput'])
	for i in range(len(stats)):
		stats[i] = stats[i]/c
	#print(stats)
	print("--------------------------------------")
	print("Observed stats")
	print("Mean Server Utilization: {0:.3f}". format(stats[0]))
	print("Mean Average Service Time: {0:.3f}". format(stats[1]))
	print("Mean Average Wait Time in Queue: {0:.3f}". format(stats[2]))
	print("Mean System Response Time: {0:.3f}". format(stats[2]+stats[1]))
	print("Average Mean Queue Length of server queues: {0:.3f}". format(stats[3]))
	print("Average Number of Packets Processed: {0:.3f}". format(stats[4]))
	print("Average Number of Packets Dropped: {0:.3f}". format(stats[5]))
	print("Average Server Uptime: {0:.3f}". format(stats[6]))
	print("Average Server Throughput: {0:.3f}". format(stats[7]))
	print("--------------------------------------")
	t1.append([stats[0],stats[1], stats[2], stats[2]+stats[1], stats[3], stats[4], stats[5], stats[7]])
	print("Calculated stats")
	ro = float(lbd1/(lbd2*c))
	lq = float((ro*ro)/(1-ro))
	wq = float(lq/lbd1)
	w = float(wq+(1/lbd2))
	t1.append( ['Calculated Statistics'])
	# writer.writerows(t1)
	# tl.clear()
	t1.append(['Mean Server Utilization', 'Mean Queue Length', 'Mean Average Wait Time in Queue',  'Mean System Response Time', 'Average System Throughput'])
	t1.append([ro*100, lq, wq, w, lbd2])
	print("Mean Server Utilization: {0:.3f}". format(ro*100))
	print("Mean Queue Length: {0:.3f}". format(lq))
	print("Mean Wait Time in Queue: {0:.3f}". format(wq))
	print("Mean Time in System: {0:.3f}". format(w))
	print("Average System Throughput: {0:.3f}". format(lbd2))
	print("--------------------------------------")
	print("Loss Factors")
	c1 = float((((stats[0]-(ro*100))**2)**(0.5))/100)
	c3= float(((((stats[2]+stats[1])-w)**2)**(0.5)))
	c2 = float(((((stats[2]-wq))**2)**(0.5)))
	c4 = float(((stats[3]-lq)**2)**0.5)
	c5 =float(((stats[7]-lbd2)**2)**0.5)
	c6 = float((c1+c2+c3+c4+c5)/5)
	t1.append( ['Loss Factors'])
	# writer.writerows(t1)
	# tl.clear()
	t1.append(['Mean Server Utilization', 'Mean Wait Time in Queue', 'Mean System Response Time',  'Mean Queue Length', 'System Throughput', 'Mean Loss Factor'])
	t1.append([c1, c2, c3, c4, c5, c6])
	print("Mean Server Utilization: {0:.3f}". format(c1))
	print("Mean Wait Time in Queue: {0:.3f}". format(c2))
	print("Mean System Response Time: {0:.3f}". format(c3))
	print("Mean Queue Length : {0:.3f}". format(c4))
	print("System Throughput : {0:.3f}". format(c5))
	writer.writerows(t1)
	wf.close()
	objects  =['Mean Server Utilization', 'Mean Wait Time in Queue', 'Mean System Response Time',  'Mean Queue Length', 'System Throughput', 'Mean Loss Factor']
	lf = [c1, c2, c3, c4, c5, c6]
	plt.figure(figsize=(20 ,3))
	plt.bar(objects, lf,  align='center')
	#plt.xticks(lf, objects)
	print(breakdownEnabled)
	plt.ylabel('Loss Factor')
	plt.title('Loss Factor Graph (The closer to 0 the better)')
 
	plt.show()

import subprocess
import threading

class Ping(object):
    status = [] # Populated while we are running
    hosts = [] # List of all hosts/ips in our input queue

    # How many ping process at the time.
    #thread_count = 4

    # Lock object to keep track the threads in loops, where it can potentially be race conditions.
    lock = threading.Lock()

    def ping(self, ip):
        # Use the system ping command with count of 10.
        ret = subprocess.call(['ping', '-c', '10', ip],
                              stdout=open('/dev/null', 'w'), stderr=open('/dev/null', 'w'))
        return ret == 0 # Return True if our ping command succeeds

    def pop_queue(self):
        host = None

        self.lock.acquire() # Grab or wait+grab the lock.

        if self.hosts:
            host = self.hosts.pop()

        self.lock.release() # Release the lock, so another thread could grab it.
        return host

    def dequeue(self):
        while True:
            host = self.pop_queue()

            if not host:
                return None

            if not self.ping(host[2]):
                self.status.append(host)

    def start(self, hosts):
        
        self.hosts = hosts
        threads = []
        for i in range(self.thread_count):
            # Create self.thread_count number of threads that together will
            # cooperate removing every ip in the list. Each thread will do the
            # job as fast as it can.
            t = threading.Thread(target=self.dequeue)
            t.start()
            threads.append(t)

        # Wait until all the threads are done. .join() is blocking.
        [ t.join() for t in threads ]

        # Clear variable
        result = self.status[:]
        del self.status[:]
        return result
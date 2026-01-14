from multiprocessing import Process, Queue
import sys
import traceback

class WorkerProcess(Process):
    def __init__(self, target, args, error_queue):
        super().__init__(target=target, args=args)
        self.error_queue = error_queue

    def run(self):
        try:
            super().run()
        except Exception as e:
            print(f"Worker error: {e}")
            self.error_queue.put((str(e), traceback.format_exc()))
            sys.exit(1)

class ProcessManager:
    def __init__(self):
        self.processes = []
        self.error_queue = Queue()

    def start_worker(self, target, args):
        self.processes.append(WorkerProcess(target, args, self.error_queue))
        self.processes[-1].start()

    def running(self):
        return any([p.is_alive() for p in self.processes])

    def check_processes(self):
        for p in self.processes:
            if not p.is_alive() and p.exitcode != 0:
                print("Worker process crashed!")
                return False

        if not self.error_queue.empty():
            error, tb = self.error_queue.get()
            print(f"Worker error: {error}")
            self.shutdown()
        return True

    def shutdown(self):
        for i, p in enumerate(self.processes):
            if p.is_alive():
                p.terminate()
                p.join()

    def handle_signal(self, signum, frame):
        print("Received shutdown signal")
        self.shutdown()
        sys.exit(1)

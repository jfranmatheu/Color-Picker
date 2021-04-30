from io import StringIO 
import sys

class PrintCaptor(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

class PrintRedirector():
    def __init__(self):
        self.old_stdout = sys.stdout
        self.new_stdout = StringIO()
        sys.stdout = self.new_stdout
        
    def get(self):
        sys.stdout = self.old_stdout
        return self.new_stdout.getvalue()

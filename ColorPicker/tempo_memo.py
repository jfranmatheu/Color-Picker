# Memoria temporal.
global_tempo_memo = {}

class TempoMemo:
    def __init__(self, data, attr: str, memo_size: int, can_remember: bool = False, id: str = '') -> object:
        self._data = data
        self._attr = attr
        self._memo_size = memo_size
        self._data_blocks = []
        self._can_remember = can_remember
        self._taken_size = 0
        if can_remember:
            self._id = id
            self.remember()
            
    def get_data(self):
        return getattr(self._data, self._attr)
    
    def set_memo_size(self, memo_size: int):
        self._memo_size = memo_size
        
    def learn(self):
        self._data_blocks.append(self.get_data())
        self._taken_size += 1
        if self._taken_size > self._memo_size:
            self.forget()
        else:
            self.book()
    
    def forget(self):
        del self._data_blocks[0]
        self.book()
        self._taken_size -= 1
    
    def remember(self):
        memo = global_tempo_memo.get(self._id, None)
        if memo:
            self._data_blocks = memo
            self._taken_size = len(self._data_blocks)
    
    def book(self):
        if self._can_remember:
           global_tempo_memo[self._id] = self._data_blocks

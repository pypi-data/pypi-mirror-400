from contextlib import contextmanager

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise KeyError(name)

    def set(self, name, value):
        self.vars[name] = value

    def update(self, mapping):
        self.vars.update(mapping)

    def contains(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.contains(name)
        return False

    def keys(self):
        keys = set(self.vars.keys())
        if self.parent:
            keys.update(self.parent.keys())
        return keys

    def clear(self):
        self.vars.clear()

@contextmanager
def new_scope(interpreter, initial_vars=None):
    parent = interpreter.env
    interpreter.env = Scope(parent)
    if initial_vars:
        interpreter.env.update(initial_vars)
    try:
        yield
    finally:
        interpreter.env.clear()
        interpreter.env = parent

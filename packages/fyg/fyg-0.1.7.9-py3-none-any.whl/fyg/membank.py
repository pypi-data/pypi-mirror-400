import os
from .util import read, write, Named
from .config import config

class MemBank(Named):
	def __init__(self, bank="default"):
		self.root = config.membank.root
		self.name = bank
		self.path = os.path.join(self.root, bank)
		self.bank = {}
		self.load()

	def load(self):
		if not os.path.isdir(self.root):
			self.log("load() creating root", self.root)
			movebank = os.path.isfile(self.root)
			rt = movebank and "%s-tmp"%(self.root,)
			movebank and self.log("load() renaming default")
			movebank and os.rename(self.root, rt)
			os.mkdir(self.root)
			movebank and os.rename(rt, os.path.join(self.root, "default"))
		remembered = read(self.path, isjson=True, b64=True)
		remembered and self.bank.update(remembered)
		self.log("loaded", self.name, "bank")

	def remember(self, key, data, ask=True):
		if ask and input("remember %s for next time? [Y/n] "%(key,)).lower().startswith("n"):
			return self.log("ok, not remembering", key)
		self.bank[key] = data
		write(self.bank, self.path, isjson=True, b64=True)

	def recall(self, key):
		return self.bank.get(key, None)

	def get(self, key, default=None):
		val = self.recall(key)
		if not val:
			pstr = "%s? "%(key,)
			if default:
				pstr = "%s[default: %s] "%(pstr, default)
			val = input(pstr) or default
			self.remember(key, val)
		return val

membanks = {}

def setbank(name=None, root=None):
	name and config.membank.update("default", name)
	root and config.membank.update("root", root)

def getbank(name=None):
	name = name or config.membank.default
	if name not in membanks:
		membanks[name] = MemBank(name)
	return membanks[name]

def remember(key, data, ask=True, bank=None):
	getbank(bank).remember(data, ask)

def recall(key, bank=None):
	return getbank(bank).recall(key)

def memget(key, default=None, bank=None):
	return getbank(bank).get(key, default)
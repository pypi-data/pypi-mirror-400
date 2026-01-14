import json

class Config(object):
	def __init__(self, cfg):
		self._cfg = {}
		for key, val in list(cfg.items()):
			self.update(key, val)

	def __getattr__(self, key):
		return self._cfg.get(key)

	def __getitem__(self, key):
		return self._cfg.get(key)

	def __setitem__(self, key, val):
		self._cfg[key] = val

	def __contains__(self, key):
		return key in self._cfg

	def obj(self):
		obj = {}
		for k, v in list(self.items()):
			if v.__class__ == Config:
				obj[k] = v.obj()
			else:
				obj[k] = v
		return obj

	def json(self):
		return json.dumps(self.obj(), indent=4)

	# dict compabitility
	def get(self, key, fallback=None):
		return self._cfg.get(key, fallback)

	def values(self):
		return list(self._cfg.values())

	def items(self):
		return list(self._cfg.items())

	def keys(self):
		return list(self._cfg.keys())

	def update(self, key, val={}):
		self._cfg[key] = isinstance(val, dict) and Config(val) or val

	def sub(self, key):
		if key not in self._cfg:
			self.update(key)
		return self._cfg.get(key)

	def cast(self, key, val):
		oval = self.get(key)
		t = type(oval)
		if t == type(val) or oval == None:
			return val
		if oval == "auto" or t is bool:
			if val == "False":
				return False
			if val == "True":
				return True
			return val
		return t(val)

	def set(self, ups, autoCast=True):
		for k, v in ups.items():
			if type(v) is dict:
				self.sub(k).set(v, autoCast)
			else:
				if autoCast:
					v = self.cast(k, v)
				self.update(k, v)

config = Config({
	"membank": {
		"root": ".membank",
		"default": "default"
	},
	"log": {
		"deep": False,
		"flush": False,
		"timestamp": True,
		"allow": ["info", "log", "warn", "error"] # access,info,log,warn,error,detail,db,query,kernel
	}
})
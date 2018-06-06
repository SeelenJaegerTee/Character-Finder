import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Pango

from random import randint

filePath = 'settings.txt'
DEBUG = False

#-----------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------
def tokenize(inputString, delimStart, delimEnd):	#e.g tokenize('[Foo][Bar]', '[', ']')
#	if DEBUG:
#		print("Tokenizing String: ", inputString)
	tokenList = []
	mode = 'scan'	# modes: 'scan', 'accum'
	buffer = ''
	for c in inputString:
		if c == delimStart:
			buffer = ''
			mode = 'accum'
		elif c == delimEnd:
			mode = 'scan'
			if buffer != '':
				tokenList.append(buffer)
			buffer = ''
		elif mode == 'accum':
			buffer = buffer+c
#	if DEBUG:
#		print("generated token List: ", tokenList)
	return tokenList

def d10(no):
	accum = 0
	for d in range(0,no):
		accum = accum + randint(1,10)
	return int(accum)

def d5(no):
	accum = 0
	for d in range(0,no):
		accum = accum + randint(1,5)
	return int(accum)

#-----------------------------------------------------------------------------------
# Classes: Graphics
#-----------------------------------------------------------------------------------
class MainWindow(Gtk.Window):
	def __init__(self, DataObj):
		if DEBUG:
			print('Main window init')
		self.linkedData = DataObj
		Gtk.Window.__init__(self, title="Character Finder (generator)")
		self.set_size_request(200, 100)
		self.timeout_id = None
		self.connect("destroy", Gtk.main_quit)
		
		self.contentFrame = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 5)
		self.add(self.contentFrame)

		self.hbox = Gtk.Box(spacing = 5)
		self.contentFrame.add(self.hbox)
		
		self.leftSide  = SettingDisplay(self, self.linkedData)
		self.rightSide = StatBlockDisplay(self, self.linkedData)
		self.hbox.add(self.leftSide)
		self.hbox.add(self.rightSide)
		
		self.contentFrame.add(Gtk.Separator())
		self.contentFrame.add(DiceTool(self))
		
		self.update()
		

	def update(self):
		if DEBUG:
			print('updated')
			print('bounds are')
			for i in self.linkedData.bounds.limits:
				print(i.name, i.minValue, i.maxValue, i.diceCup.diceString)
		self.show_all()

		
class SettingDisplay(Gtk.Box):
	def __init__(self, parent, DataObj):
		if DEBUG:
			print('SettingDisplay init')
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		self.linkedData = DataObj
		self.parent = parent
		#if type(Data(StatBounds())) == type(self.linkedData):
		if True:
			self.graphics = Gtk.Grid()
			self.add(self.graphics)
			l = Gtk.Label('')
			m = Gtk.Label('Min')
			r = Gtk.Label('Max')
			
			self.graphics.add(l)
			self.graphics.attach_next_to(m, l, Gtk.PositionType.RIGHT, 1, 1)
			self.graphics.attach_next_to(r, m, Gtk.PositionType.RIGHT, 1, 1)
			self.graphicsEntry = []
			for i in self.linkedData.bounds.limits:
				a = Gtk.Label(i.name)
				b = Gtk.Entry()
				b.set_width_chars(4)
				b.set_text(str(i.minValue))
				c = Gtk.Entry()
				c.set_width_chars(4)
				c.set_text(str(i.maxValue)) 
				d = Gtk.Entry()
				d.set_width_chars(22)
				d.set_text(str(i.diceCup.diceString))
				
				self.graphicsEntry.append({'a':a, 'b':b, 'c':c, 'd':d})
			
			for i in self.graphicsEntry:
				a = i['a']
				b = i['b']
				c = i['c']
				d = i['d']
				self.graphics.attach_next_to(a, l, Gtk.PositionType.BOTTOM, 1, 1)
				self.graphics.attach_next_to(b, a, Gtk.PositionType.RIGHT, 1, 1)
				self.graphics.attach_next_to(c, b, Gtk.PositionType.RIGHT, 1, 1)
				self.graphics.attach_next_to(d, c, Gtk.PositionType.RIGHT, 1, 1)
				l=a
			
			button = Gtk.Button(label = "save changes")
			button.connect("clicked", self.updateDataClicked)
			self.graphics.attach_next_to(button, l, Gtk.PositionType.BOTTOM, 4, 1)


	def updateDataClicked(self, widget):
		if DEBUG:
			print('updateDataClicked')
		for i in self.graphicsEntry:
			name = i['a'].get_text()
			minValue = i['b'].get_buffer().get_text()
			maxValue = i['c'].get_buffer().get_text()
			diceString = i['d'].get_buffer().get_text()
			self.linkedData.bounds.setBound(name, int(minValue), int(maxValue), diceString)
		self.parent.update()

		
class StatBlockDisplay(Gtk.Box):
	def __init__(self, parent, DataObj):
		if DEBUG:
			print('StatBlockDisplay init')
		self.linkedData = DataObj
		self.parent = parent
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		
		self.graphics = Gtk.Grid()
		self.add(self.graphics)
		self.label = Gtk.Label('Character conforming to request')
		self.graphics.add( self.label )
		
		self.textview = Gtk.TextView()
		self.textview.set_monospace(True)
		self.textbuffer = self.textview.get_buffer()
		self.textbuffer.set_text('')
	
		self.info = Gtk.TextView()
		self.info.set_monospace(True)
		self.info.set_editable(False)
		self.infobuffer = self.info.get_buffer()
		self.infobuffer.set_text('')
		
		self.updateCharacter()
		self.graphics.attach_next_to(self.textview, self.label, Gtk.PositionType.BOTTOM, 1, 1)

		self.button = Gtk.Button(label = "Find Character")
		self.button.connect("clicked", self.rerollClicked)
		self.graphics.attach_next_to(self.button, self.textview, Gtk.PositionType.BOTTOM, 1, 1)
		self.graphics.attach_next_to(self.info, self.button, Gtk.PositionType.BOTTOM, 1, 1)
		
	def rerollClicked(self, widget):
		if DEBUG:
			print('searched for new characters')
		for c in self.linkedData.char:
			c.regen()
		self.updateCharacter()
		self.parent.update()
		
	def updateCharacter(self):
		buff = ''
		for c in self.linkedData.char:
			if c.checkConformity():
				for attr in c.attribute:
					print(attr.name, ': ', attr.value)
					buff = buff + attr.name + ':\t' + str(attr.value) + '\n'
				break
				buff = 'conforming characters (out of 1000)\n'
		n = 0
		self.textbuffer.set_text(buff)
		buff = ''
		for ch in self.linkedData.char:
			n += 1
			if ch.checkConformity():
				buff = buff+'X'
			else:
				buff = buff+'.'
			if n == 50:
				n = 0
				buff = buff+'\n'
		self.infobuffer.set_text(buff)


class DiceTool(Gtk.Box):
	def __init__(self, parent):
		if DEBUG:
			print('DiceTool init')
		self.parent = parent
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
		self.add(Gtk.Label('Dice roller Tool'))
		
		self.diceString = Gtk.Entry()
#		self.textbuffer = self.textview.get_buffer()
		self.diceString.set_text('[1d100+0]')
		self.add(self.diceString)
		
		self.info = Gtk.Entry()
		self.info.set_editable(False)
#		self.infobuffer = self.info.get_buffer()
		self.info.set_text('')
		self.add(self.info)

		button = Gtk.Button(label = "roll")
		button.connect("clicked", self.roll)
		self.add(button)


	def roll(self, widget):
		if DEBUG:
			print('roll clicked')
		diceCup = DiceCup(self.diceString.get_text())
		self.info.set_text(str(diceCup.throw()))
#		self.parent.update()

#-----------------------------------------------------------------------------------
# Classes: Data Structures
#-----------------------------------------------------------------------------------
class Die:
	def __init__(self, low, high):
#		if DEBUG:
#			print('die init')
		self.low = low
		self.high = high
	def roll(self):
		return int(randint(self.low, self.high))


class DiceCup:
	def __init__(self, diceString):	#dice string is sth. like '[2d10+2][1d5]' to roll two 10sided dice one 5 sided die and add 2
#		if DEBUG:
#			print('diceCup init')
		self.diceString = diceString	# warning this will not be equivalent to diceList (see dice List three rows below)
#		if DEBUG:
#			print("init: diceString = ", diceString)
		self.diceList = []				# warning this will not be equivalent to diceString: dice String would be 3d10+2, dice list will be three dice one with range 3-12 and two with range 1-10 (alike [1d10+2][1d10][1d10])
		self.parseTokenList(tokenize(diceString, '[', ']'))

	def throw(self):
#		if DEBUG:
#			print('throw')
		accum = 0
		for d in self.diceList:
			accum = accum + d.roll()
#		if DEBUG:
#			print(accum)
		return int(accum)
			
	def parseTokenList(self, tokenList):
#		if DEBUG:
#			print('parseTokenList')
		self.diceList = []
		for t in tokenList:
			self.parseToken(t)
		
	def parseToken(self, token):
#		if DEBUG:
#			print('parseToken')
		number 	= ''
		size 	= ''
		bonus 	= ''
		mode 	= 'number'		# modes: number, size, bonus
		for c in token:
			if c == 'd' or c == 'D':
				mode = 'size'
				if number =='':
					number = '1'
			elif c == '+' or c == '-':
				mode = 'bonus'
				bonus = c
			elif c.isdecimal():
				if mode == 'number':
					number = number+c
				elif mode == 'size':
					size = size+c
				elif mode == 'bonus':
					bonus = bonus+c
		number 	= int(number)
		size	= int(size)
		if bonus == '':
			bonus = '0'
		bonus 	= int(bonus)
		if number == 0 or size == 0:
			self.diceList.append(Die(bonus,bonus))
		for n in range(number):
			if bonus != 0:
				self.diceList.append(Die(1+bonus,size+bonus))
				bonus = 0
			else:
				self.diceList.append(Die(1,size))


class Bound:
	def __init__(self, name='NA', minValue=0, maxValue=99999, diceString = '[2d10]+20'):
#		if DEBUG:
#			print('bound init')
		self.name = name
		self.minValue = minValue
		self.maxValue = maxValue
		self.diceCup = DiceCup(diceString)
		
	def fromTokenList(self, tokenList): #like e.g. ['name:KG','min:20','max:40','dice:[2d10]']
#		if DEBUG:
#			print('fromTokenList')
		for t in tokenList:
			if 'name:' in t:
				buff = t[5:]
				self.name = buff
			elif 'min:' in t:
				buff = t[4:]
				self.minValue = int(buff)
			elif 'max:' in t:
				buff = t[4:]
				self.maxValue = int(buff)
			elif 'dice:' in t:
				buff = t[5:]
				self.diceCup = DiceCup(buff)


class StatBounds:
	def __init__(self):
		if DEBUG:
			print('statbounds init')
		self.limits = []
	
	def setBound(self, Name, minValue, maxValue, diceString):
#		if DEBUG:
#			print('setBound')
		for l in self.limits:
			if l.name == Name:
				l.minValue = minValue
				l.maxValue = maxValue
				l.diceCup = DiceCup(diceString)

	def fromFileBuffer(self, lineArray):
		if DEBUG:
			print('from Line buffer')
		minDefault = '<min:0>'
		maxDefault = '<max:99999>'
		diceStringDefault = '<dice:[2d10+20]>'
		for ln in lineArray:
			setDefault 	= False
			nameFound 	= False
			minFound 	= False
			maxFound 	= False
			diceFound 	= False

			tkns = tokenize(ln,'<','>')
			for t in tkns:
				if 'default' in t:
					setDefault = True
				elif 'name:' in t:
					nameFound = True
				elif 'min:' in t:
					minFound = True
					if setDefault:
						minDefault = '<'+t+'>'
				elif 'max:' in t:
					maxFound = True
					if setDefault:
						maxDefault = '<'+t+'>'
				elif 'dice:' in t:
					diceFound = True
					if setDefault:
						diceDefaultString = '<'+t+'>'
			l = ln.rstrip()
			if nameFound:
				if not minFound:
					l = l+minDefault
				if not maxFound:
					l = l+maxDefault
				if not diceFound:
					l = l+diceStringDefault
			if not '<default>' in l:
				bnd = Bound()
				bnd.fromTokenList(tokenize(l,'<','>'))
				self.limits.append(bnd)

class StatEntry:
	def __init__(self, name, value):
#		if DEBUG:
#			print('statEntry init')
		self.name = name
		self.value = value
		

class StatBlock:
	def __init__(self, StatBounds):
#		if DEBUG:
#			print('statBounds init')
		self.attribute = []
		self.linkedBounds = StatBounds
		self.regen()#StatBounds)

	def regen(self):#, StatBounds = self.linkedBounds):
#		if DEBUG:
#			print('regen')
		self.attribute = []
		for i in self.linkedBounds.limits:
			self.attribute.append( StatEntry(i.name, i.diceCup.throw() ))

	def checkConformity(self):#, StatBounds = self.linkedBounds):
#		if DEBUG:
#			print('check conformity')
		for lim in self.linkedBounds.limits:
			for val in self.attribute:
				if lim.name == val.name:
					if val.value < lim.minValue or val.value > lim.maxValue:
						return False
		return True

class Data:
	def __init__(self, StatBoundsObj):
		if DEBUG:
			print('data init')
		self.bounds = StatBoundsObj
		self.char = []
		self.findCharacter()
		
	def findCharacter(self):
		if DEBUG:
			print('findCharacter')
		self.char = []
		for i in range(0, 1000):
			self.char.append(StatBlock(self.bounds))

		print("conforming characters (out of 1000)")
		n = 0
		buff = ''
		for ch in self.char:
			n += 1
			if ch.checkConformity():
				buff = buff+'X'
			else:
				buff = buff+'.'
			if n == 50:
				n = 0
				print(buff)
				buff = ''

		for ch in self.char:
			if ch.checkConformity():
				return ch

#-----------------------------------------------------------------------------------
# Program
#-----------------------------------------------------------------------------------
line = []
print('loading File:')
with open(filePath, "r") as fileHandle:
	for ln in fileHandle:
		line.append(ln.lstrip().rstrip())		# now we have the file in the "line"buffer
print('done!')

print('stripping empty lines and comments:')
it = len(line)-1
while it >= 0:
	if len(line[it]) == 0:
		del(line[it])
	elif line[it][0] == '#':
		del(line[it])
	it -= 1
print('done: \n\nfile buffer is now:')
for l in line:
	print(l)
print('\n\n')
			
bnds = StatBounds()
bnds.fromFileBuffer(line)
data = Data(bnds)
win = MainWindow(data)
Gtk.main()

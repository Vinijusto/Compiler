from sly import Lexer,Parser
import sys

class CLexer(Lexer):
	tokens = {'HEXCOLOR','INT','NINT','NUMERAL','LETTERS','COMMENT','TAG','NEWLINE'}
	ignore = ' \t'
	
	@_(r'\$[a-fA-F0-9]+')
	def HEXCOLOR(self,t):
		t.value = str(int(t.value[1:],16))
		return t

	INT = r'\d+'
	NINT = r'\-\d+'
	NUMERAL = r'\#'
	LETTERS = r'[a-zA-Z_][a-zA-Z_]*'
	ignore_COMMENT = r'//.*$'
	ignore_NEWLINE = r'\n+'
	TAG = r'@[a-zA-Z_][a-zA-Z_0-9_]*'
	
	def ignore_NEWLINE(self, t):
		self.lineno += t.value.count('\n+')

	def error(self, t):
		print("Illegal character" + t.value)
		self.index += 1

class CParser(Parser):
	tokens = CLexer.tokens
	def __init__(self):
		self.lines = 1
		self.lines = 1
		self.lexer = lexer
		self.lineacompleta = None
		self.json = {'name' : '',
		    'color' : '',
		    'tcolor': '',
		    'equip': {
			    'weapon' : [],
			    'ammo' : [],
			    'scanner' : [],
			    'arcd' : [],
			    'arcp' : [],
			    'arcw' : [],
			    'hull' : [],
			    'material' : [],
			    'engine' : [],
			    'extension' : [],
			    'turret' : []
		    },
		    'code':[], 
		    'labels':{}
    	}
    	self.componentes_irrepetibles = ("hull","material","engine","extension")
		self.estado = "normal" #Estados posibles: begin, equip, normal o desconocid
		self.calls = {"normal": self.normal_func, "begin": self.begin_func, "equip": self.equip_func}
		self.errors = []
		self.warnings = []
		self.labels_calleados={}

	@_('NUMERAL LETTERS')
	def declar(self, p):
		self.trans,self.estadoactual = self.estados(p[1].lower())
		if self.trans:
			self.estado = self.estadoactual
		else:
			self.error_2("Error: cambio de estado incorrecto.")

	def estados(self,etadotentativo):
		self.estados_posibles = ["begin","equip"]
		if etadotentativo in self.estados_posibles:
			if self.estado == "normal":
				return True,etadotentativo
			elif self.estado == etadotentativo:
				return True,"normal"
			else:
				return False,"error"
		else:
			return False,"error"

	@_('NUMERAL LETTERS LETTERS','NUMERAL LETTERS HEXCOLOR')
	def declar(self, p):
		if self.calls[self.estado]([(p[0] + p[1]).lower(),p[2].lower()]) == True:
			self.json[p[1]] = p[2]
		else: 
			self.error_2("Error: característica o parámetro inexistente o incorrecto, declaración incorrecta en este estado.")

	def returntrue(self,strnum):
		return True

	def validnum(self,strnum,numdelimitador):
		return (strnum.isnumeric() == True) * (int(strnum) < numdelimitador)

	def normal_func(self,p):
		self.caracteristicas = {"#tcolor": self.validnum,"#color": self.validnum,"#name": self.returntrue}
		if p[0] in self.caracteristicas:
			return self.caracteristicas[p[0]](p[1],16777216)
		else:
			return False

	@_('LETTERS',
		'LETTERS LETTERS',
		'LETTERS TAG',
		'LETTERS LETTERS LETTERS',
		'LETTERS INT LETTERS',
		'LETTERS NINT LETTERS',
		'LETTERS LETTERS INT',
		'LETTERS LETTERS NINT',
		'LETTERS INT',
		'LETTERS NINT',
		'LETTERS INT INT',
		'LETTERS INT NINT')
	def declar(self, p):
		self.lineaorg = []
		for element in p:
			self.lineaorg.append(element.lower())
		if self.calls[self.estado](self.lineaorg) == True:
			self.json[p[1]] = p[2]
		else: 
			self.error_2("Error: caracteristica inexistente o parámetro incorrecto.")

	def equip_func(self,p):
		self.piezas = {
		    'weapon' : 2,
		    'ammo' : 2,
		    'scanner' : 2,
		    'arcd' : 2,
		    'arcp' : 2,
		    'arcw' : 2,
		    'hull' : 2,
		    'material' : 1,
		    'engine' : 1,
		    'extension' : 1,
		    'turret' : 1
		}
		self.validacion = 0
		if p[0] in piezas:
			for i in range(1,self.piezas[p[0]][0] + 1)
				self.validacion += validnum(p[i])
			if self.validacion = self.piezas[p[0]][0]:
				return True,
		else:
			return False,"Error"
	@_('TAG LETTERS',
		'TAG LETTERS LETTERS',
		'TAG LETTERS TAG',
		'TAG LETTERS LETTERS LETTERS',
		'TAG LETTERS INT LETTERS',
		'TAG LETTERS NINT LETTERS',
		'TAG LETTERS LETTERS INT',
		'TAG LETTERS LETTERS NINT',
		'TAG LETTERS INT',
	 	'TAG LETTERS NINT',
		'TAG LETTERS INT INT',
		'TAG LETTERS INT NINT')
	def declar(self, p):
		pass

	def begin_func(self,p):
		pass
	
	def error(self,p="Error: redacción incorrecta."):
		self.errors.append(p + " Línea(" + str(self.lines) + "). Estado(" + self.estado + ")\n" + "      " + str(self.lineacompleta))

	def error_2(self,p):
		self.errors.append(p + " Línea(" + str(self.lines) + "). Estado(" + self.estado + ")\n" + "      " + str(self.lineacompleta))

	def mostrardous(self):
		print(self.json)
		print(self.errors)

if __name__ == "__main__":
	lexer = CLexer()
	parser = CParser()
	robot_source = sys.argv[1]
	with open(robot_source, "r") as f:
		lineas = f.readlines()
	for linea in lineas:
		linea = linea.strip()
		if len(linea) != 0:
			print(linea)
			parser.lineacompleta = linea
			parser.parse(lexer.tokenize(linea))
			parser.lines += 1
	parser.mostrardous()


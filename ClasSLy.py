from sly import Lexer,Parser
import sys
import random

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
		print("Token ilegal" + t.value)
		self.index += 1

class CParser(Parser):
	tokens = CLexer.tokens
	def __init__(self):
		self.lines = 1
		self.lines_begin = 0
		self.lineacompleta = None
		self.json = {'name' : '',
		    'color' : '',
		    'tcolor': '',
		    'equip':{'weapon' : [],'ammo' : [],'scanner' : [],'arcd' : [],'arcp' : [],'arcw' : [],'hull' : [],'material' : [],'engine' : [],'extension' : [],'turret' : []},
		    'begin':[], 
		    'labels':{}
		}
		self.rules =  {
			"normal" : {"n!#tcolor": (1,"=",(self.validnum,)),
				"n!#color": (1,"=",(self.validnum,)),
				"n!#name": (1,"=",(self.returntrue,))
			},
			"equip" : {'e!weapon' : (2,"append",(self.validnum,),(self.validnum,)),
				'e!ammo' : (2,"append",(self.validnum,),(self.validnum,)),
				'e!scanner' : (2,"append",(self.validnum,),(self.validnum,)),
				'e!arcd' : (2,"append",(self.validnum,),(self.validnum,)),
				'e!arcp' : (2,"append",(self.validnum,),(self.validnum,)),
				'e!arcw' : (2,"append",(self.validnum,),(self.validnum,)),
				'e!hull' : (2,"=",(self.validnum,),(self.validnum,)),
				'e!material' : (1,"=",(self.validnum,)),
				'e!engine' : (1,"=",(self.validnum,)),
				'e!extension' : (1,"=",(self.validnum,)),
				'e!turret' : (1,"append",(self.validnum,))
			},
			"begin" : {'b!nop' : (0,"append"),
				'b!ret' : (0,"append"),
				'b!cle' : (0,"append"),
				'b!ste' : (0,"append"),
				'b!clg' : (0,"append"),
				'b!stg' : (0,"append"),
				'b!cll' : (0,"append"),
				'b!stl' : (0,"append"),
				'b!saxf' : (0,"append"),
				'b!laxf' : (0,"append"),
				'b!jmp' :(1,"append",(self.validlabel,)),
				'b!je' :(1,"append",(self.validlabel,)),
				'b!jne' :(1,"append",(self.validlabel,)),
				'b!jl' :(1,"append",(self.validlabel,)),
				'b!jle' :(1,"append",(self.validlabel,)),
				'b!jg' :(1,"append",(self.validlabel,)),
				'b!jge' :(1,"append",(self.validlabel,)),
				'b!loop' :(1,"append",(self.validlabel,)),
				'b!call' :(1,"append",(self.validlabel,)),
				'b!lex' :(1,"append",(self.validlabel,)),
				'b!inc' : (1,"append",(self.register,)),
				'b!dec' : (1,"append",(self.register,)),
				'b!neg' : (1,"append",(self.register,)),
				'b!not' : (1,"append",(self.register,)),
				'b!pop' : (1,"append",(self.register,)),
				'b!mov' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!add' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!sub' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!mul' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!div' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!shl' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!shr' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!rol' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!ror' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!sal' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!sar' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!and' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!or' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!xor' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!test' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!cmp' : (2,"append",(self.register,),(self.register,self.validnum)),
				'b!xchg' : (2,"append",(self.register,),(self.register,)),
				'b!out' : (2,"append",(self.validnum, self.register),(self.validnum, self.register)),
				'b!in' : (2,"append",(self.validnum, self.register),(self.register,)),
				'b!push' : (1,"append",(self.validnum, self.register)),
				'b!int': (1,"append",(self.validnum, self.register)),
				'b!dly': (1,"append",(self.validnum, self.register)),
				'b!msg': (1,"append",(self.validnum, self.register))
			}
		}
		self.estados_posibles = ["begin","equip"]
		self.componentes_irrepetibles =("hull","material","engine","extension")
		self.estado = "normal" #Estados posibles: begin, equip, normal o desconocid
		self.prefijos = {"normal": "n!", "begin": "b!", "equip": "e!"}
		self.errors = []
		self.warnings = []
		self.labels_calleados={}

	@_('NUMERAL LETTERS')
	def declar(self, p):
		self.trans,self.estadoactual = self.estados(p[1].lower())
		if self.trans:
			self.estado = self.estadoactual
		else:
			self.errorautoc("Error: cambio de estado incorrecto.")

	@_('NUMERAL LETTERS LETTERS',
		'NUMERAL LETTERS HEXCOLOR',
		'LETTERS',
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
		'LETTERS INT NINT',
		'LETTERS NINT INT',
		'LETTERS NINT NINT')
	def declar(self, p):
		self.lineaorg = []
		for element in p:
			self.lineaorg.append(element)
		self.lineaorg[0] = (self.prefijos[self.estado] + self.lineaorg[0]).lower()
		if p[0] == '#':
			self.lineaorg[0] += self.lineaorg[1].lower()
			self.lineaorg.pop(1)
		self.validacion, self.tipodesett, self.setter, self.params = self.funcion_analisis(self.lineaorg)
		if self.validacion == True:
			if self.estado == 'begin':
				self.lines_begin += 1
			if len(self.seter) == 1:
				if self.tipodesett == "=":
					self.json[self.setter[0]] = self.params
				elif self.tipodesett == "append":
					self.json[self.setter[0]].append(self.params)
			else:
				if self.tipodesett == "=":
					self.json[self.setter[0]][self.setter[1]] = self.params
				elif self.tipodesett == "append":
					self.json[self.setter[0]][self.setter[1]].append(self.params)
		else:
			self.errorautoc("Error: declaración de caracteristicas incorrecto en estado actual.")

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
		'TAG LETTERS INT NINT',
		'TAG LETTERS NINT INT',
		'TAG LETTERS NINT NINT')
	def declar(self, p):
		self.lineaorg = []
		for index in range(1,len(p)):
			self.lineaorg.append(p[index])
		self.lineaorg[0] = (self.prefijos[self.estado] + self.lineaorg[0]).lower()
		self.validacion, self.tipodesett,self.setter, self.params = self.funcion_analisis(self.lineaorg)
		if self.validacion == True:
			self.lines_begin += 1
			self.json["begin"].append(self.params)
			self.json["labels"][p[0]] = self.lines_begin
		else:
 			self.errorautoc("Error: declaración de caracteristicas incorrecto en estado actual.")

	def funcion_analisis(self,parseds):
		""" Esto returnea, un true/false, tipo de sett, una variable a setear y el valor de la variables"""
		self.valid = False
		self.tiposet = None
		self.seter = []
		self.params = []
		self.indexparam = 1
		self.oks = 0
		if parseds[0] in self.rules[self.estado]:
			if self.estado == "begin":
				self.params.append(parseds[0])
			if self.rules[self.estado][parseds[0]][0] == len(parseds) - 1 and len(parseds) > 1:
				self.cparam = self.rules[self.estado][parseds[0]][0]
				for i in range(2,2 + self.cparam):
					for l in range(0,len(self.rules[self.estado][parseds[0]][i])):
						self.aprobado,self.vartransformada = self.rules[self.estado][parseds[0]][i][l](parseds[self.indexparam],16777216)
						if self.aprobado == True:
							self.oks += self.aprobado
							self.params.append(self.vartransformada)
					self.indexparam += 1
				if self.oks >= self.cparam:
					self.valid = True
				if self.estado == "normal":
					self.seter = [parseds[0][3:],]
				elif self.estado == "equip":
					self.seter.append(self.estado)
					self.seter.append(parseds[0][2:])
				elif self.estado == "begin":
					self.seter = [self.estado,]
					self.params[0] = self.params[0][2:]
			elif len(parseds) == 1:
				self.valid = True
				self.tiposet = "append"
				self.seter = [self.estado,]
				self.params = [parseds[0][2:],]
			self.tiposet = self.rules[self.estado][parseds[0]][1]
		return self.valid,self.tiposet,self.seter,self.params

	def estados(self,etadotentativo):
		if etadotentativo in self.estados_posibles:
			if self.estado == "normal":
				return True,etadotentativo
			elif self.estado == etadotentativo:
				return True,"normal"
			else:
				return False,"error"
		else:
			return False,"error"

	def returntrue(self,string,pad):
		return True,string

	def validlabel(self,label,pad):
		try:
			if label[0] == '@' and len(label) > 1:
				return True,label
			else: 
				return False,""
		except ValueError:	
			return False,""

	def validnum(self,strnum,numdelimitador):
		try:
			if int(strnum) <= numdelimitador:
				return True,int(strnum)
			else: 
				return False,""
		except ValueError:
			return False,""
	
	def register(self,reg,pad):
		try:
			for element in ("ax","bx","cx","dx","ex","fx"):
				if reg.lower() == element:
					return True,reg.lower()
			return False,""
		except ValueError:
			return False,""

	def error(self,p):
		self.errors.append("Syntaxis error. Línea " + str(self.lines) + ", estado " + self.estado + ".\n" + "      " + str(self.lineacompleta)+ "\n" )
		return None
	
	def errorautoc(self,parrafo):
		self.errors.append(parrafo+ " Línea " + str(self.lines) + ", estado " + self.estado + ".\n" + "      " + str(self.lineacompleta) + "\n" )

	def errorestructural(self,parrafo):
		self.errors.append("Error estructural: " + parrafo + "\n")
	
	def warnings(self,parrafo):
		self.warnings.append("warnings:" + parrafo + "\n")

	def mostrardous(self):
		print('\n\n\n\n',self.json,'\n\n\n\n','Cant Errors:',len(self.errors))
		for i in self.errors:
			print(i)
	
	def cleanwarnsanderrors(self):
		#Retoques de chars name color tcolor
		nombres = ('Miguel','Ignacio','Tuco','Pedro','Lolo','Jerusalen','Juan','Hermenejildo','Papastotopulus','Camila','Flora','Patricia','Elisabet','Margara','Cecilia','Chota')
		apodos = (' el bromas',' el pana',' el waton quleao', ' el sultano', ' de la salada', ' la falla', ' el precursor', ' la reconchisima de la lorax', ' el gambeta', ' el rapido', ' la masa', ' el chungo')
		hexanums = ('A','B','C','D','E','F','0','3','1','2','4','5','6','7','8','9')
		if self.json['name'] == '' or self.json['name'][0].lower() == 'random':
			self.json['name'] = random.choice(nombres) + random.choice(apodos)
		else:
			self.json['name'] = self.json['name'][0]
		
		for element in ('tcolor','color'):
			raux = ''
			raux2 = '' 
			if self.json[element] == '' or self.json[element] == 'random':
				for i in range(0,7):
					raux += random.choice(hexanums)
				self.json[element] = ('0x' + raux)
			else:
				raux = str(hex(self.json[element][0]))[2:]
				if len(raux[2:]) < 6:
					for i in range(0,6 - len(raux)):
						raux2 += '0'
				self.json[element] = ('0x' + raux2 + raux)
		
		if len(self.json['begin']) > 0:
			aux3 = None
			aux4 = None
			for i in range(0,len(self.json['begin'])):
				if len(self.json['begin'][i]) > 1:
					aux3 = self.json['begin'][i]
					aux4 = aux3[0]
					aux3.pop(0)
					self.json['begin'][i] = [aux4,aux3]
		else:
			self.errorestructural("no ha declarado ningun begin.")
		if self.json['equip']['engine'] == [] or self.json['equip']['material'] == [] or self.json['equip']['hull'] == []:
 			self.errorestructural("caracteristicas basicas no declaradas(hull,material,engine).")

		auxdict = self.json['labels'].copy()
		auxlsit = []
		auxexis = []
		for i in self.json['begin']:
			if len(i) > 1:
				if isinstance(i[1][0],int) == False:
					label = i[1][0]
					if label in auxdict:						
						del auxdict[label]
						auxexis.append(label)
					elif not label in auxdict and not label in auxexis and label[0] == '@':
						auxlsit.append(label)
		if len(auxlsit) > 0:
			self.errorestructural("TAG/s usado/s como parametro/s sin declarar.")

def compilar(lineas):
	lexer = CLexer()
	parser = CParser()
	for linea in lineas:
		linea = linea.strip()
		if len(linea) != 0:
			print(linea)
			parser.lineacompleta = linea
			parser.parse(lexer.tokenize(linea))
			parser.lines += 1
	parser.cleanwarnsanderrors()
	parser.mostrardous()
	return parser.json, parser.errors

if __name__ == "__main__":
	lexer = CLexer()
	parser = CParser()
	robot_source = sys.argv[1]
	with open(robot_source, "r") as f:
		lineas = f.readlines()
	#random.shuffle(lineas)
	for linea in lineas:
		linea = linea.strip()
		if len(linea) != 0:
			print(linea)
			parser.lineacompleta = linea
			parser.parse(lexer.tokenize(linea))
			parser.lines += 1
	parser.cleanwarnsanderrors()
	parser.mostrardous()

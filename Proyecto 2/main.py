#!/usr/bin/python

import sys, getopt, random, math

# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
#                                    CLASES                                   #
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #

################################### INDIVIDUO ###################################
class Individual:
  fit = 0
  chosen = False
  AddAlt = False
  DropCond = False
  genot = []
  # Creador de individuo a partir de valores especificos, si no se le pasa
  # ningun valor se genera con valores aleatorios
  def __init__(self,genot,a,d):
    self.genot = genot
    if len(genot) == 0:
      self.fit = 0
    else:
      self.fit = fitness(self.genot)
    self.chosen = False
    self.AddAlt = a
    self.DropCond = d

  def random_ind(self):
    self.genot = []
    r = random.randint(1,maxRules)
    for i in range(r):
      self.genot.append(randrule())
    self.fit = fitness(self.genot)
    self.chosen = False
    self.AddAlt = False
    self.DropCond = False

  # Funcion para imprimir un individuo
  def print_indiv(self, complete = False):
    print '     Fitness:',self.fit, ' Elegido:',self.chosen,
    print ' AddAlt:',self.AddAlt,' DropCond:',self.DropCond,' NumRegl:',len(self.genot)
    if complete:
      for x in self.genot:
        print_gen(x)

  # Funcion de Mutacion: recibe un conjunto de reglas y aplica mutaciones
  # sobre cada bit (y los atributos de AddAlternative y DropCondition) con 
  # una probabilidad de mutationP
  def mutation(self):
    for x in range(len(self.genot)):
      for i in range(23):
        r = random.random()
        if r<=mutationP/math.log(len(self.genot)+1):
          if self.genot[x][i]=='0':
            #print 'false->true'
            self.genot[x] = self.genot[x][0:i]+'1'+self.genot[x][i+1:]
          elif self.genot[x][i]=='1':
            #print 'true->false'
            self.genot[x] = self.genot[x][0:i]+'0'+self.genot[x][i+1:]
    r = random.random()
    if r<=mutationP: self.AddAlt = not self.AddAlt
    r = random.random()
    if r<=mutationP: self.DropCond = not self.DropCond
    if aaydc == 1:
      if self.AddAlt and addP>random.random():
        self.addAlt()
      if self.DropCond and dropP>random.random():
        self.dropCond()

  # Funcion de operador AddAlternative, elige una regla para cambiarle un bit en
  # uno de los rasgos (ai) de 0 a 1. En caso de que el bit seleccionado no es 0
  # elige otro bit, intenta hasta tries(10) veces para que el cambio sea significativo
  def addAlt(self):
    tries = 10
    r1 = random.randint(0,len(self.genot)-1)
    r2 = random.randint(0,22)
    while self.genot[r1][r2] != '0' and tries>0:
      r2 = random.randint(0,22)
      tries = tries-1
    self.genot[r1] = self.genot[r1][0:r2]+'1'+self.genot[r1][r2+1:]

  # Funcion de operador DropCondition, elige una regla para cambiarle todo un
  # rasgo a unos, no revisa que el cambio sea significativo.
  def dropCond(self):
    r1 = random.randint(0,len(self.genot)-1)
    r2 = random.randint(0,3)
    if r2 == 0:
      self.genot[r1] = '111111'+self.genot[r1][6:]
    elif r2 == 1:
      self.genot[r1] = self.genot[r1][0:6]+'11111'+self.genot[r1][11:]
    elif r2 == 2:
      self.genot[r1] = self.genot[r1][0:11]+'1111111'+self.genot[r1][18:]
    elif r2 == 3:
      self.genot[r1] = self.genot[r1][0:18]+'11111'+self.genot[r1][23:]


################################### POBLACION ###################################
class Population:
  fitT = 0 # Fitness total de la poblacion (suma)
  nindiv = 0 # Numero de individuos de la poblacion
  nrule = 0 # Numero de reglas total de la poblacion
  popul = [] # Individuos de la poblacion
  def __init__(self):
    self.fitT = 0
    self.nrule = 0
    self.nindiv = 0
    self.popul = []

  # Funcion que agrega un individuo a la poblacion asumiendo que su
  # fitness ya fue calculado
  def add(self,indiv):
    self.popul.append(indiv)
    self.nindiv += 1
    self.nrule += len(indiv.genot)
    self.fitT += indiv.fit
    if self.nindiv > popn : print 'Error, maximo de poblacion superado' # No deberia pasar

  # Elimina de la poblacion el individuo en la posicion index
  def delete(self,index):
    self.nrule = self.nrule - len(self.popul[index].genot)
    self.nindiv = self.nindiv-1
    self.fitT = self.fitT - self.popul[index].fit
    del self.popul[index]

  # Funcion para imprimir la poblacion
  def print_pop(self,completeP = False,completeI = False):
    print 'FitTot:',self.fitT,', FitProm:',self.fitT/self.nindiv,', NumIndiv:',self.nindiv,
    print 'PromReglas:',self.nrule/float(self.nindiv)
    if completeP:
      if completeI:
        for x in self.popul:
          x.print_indiv(True)
      else:
        for x in self.popul:
          x.print_indiv()


  # Funcion que calcula el fitness de cada individuo y el fitness total
  # de la poblacion
  def recalc(self):
    i = 0
    self.fitT = 0
    self.nrule = 0
    while i<self.nindiv:
      self.popul[i].chosen = False
      self.popul[i].fit = fitness(self.popul[i].genot)
      self.fitT += self.popul[i].fit
      self.nrule += len(self.popul[i].genot)
      i += 1

  # Selecciona un individuo por rueda de ruleta
  def roulette(self):
    p = random.random()
    i = 0
    j = 0
    while i<p and j<popn:
      i += self.popul[j].fit/float(popn)
      j += 1
    return self.popul[j-1]

  # Seleccion por torneo de 1 entre k individuos elegidos aleatoriamente
  def tournament(self,k):
    if k>self.nindiv or k<1:
      print 'Error en el numero de individuos a elegir por torneo'
      return []
    i = 0
    eleg = []
    champion = False
    # Eleccion de los k participantes en el torneo
    while i<k:
      p = random.randint(0,popn-1)
      if not self.popul[p].chosen:
        eleg.append(p)
        i += 1
    # Eleccion del ganador del torneo, cada ciclo es una ronda
    while not champion:
      i = 0
      losers = []
      while i<len(eleg):
        # Probabilidad de que el competidor 1 gane es su fitness entre la suma del fitness de los
        # dos competidores
        if self.popul[eleg[i+1]].fit == 0 or \
           self.popul[eleg[i]].fit/(self.popul[eleg[i]].fit+self.popul[eleg[i+1]].fit) > random.random():
          losers.append(i+1)
        else:
          losers.append(i)
        i = i+2
      i = len(losers)-1
      # Los perdedores dejan de estar entre los elegidos
      while i>-1:
        del eleg[losers[i]]
        del losers[i]
        i = i-1
      if len(eleg)==1: champion = True
    return self.popul[eleg[0]]

  # Funcion que a partir de una poblacion de individuos resultantes del
  # crossover y mutacion elige de la poblacion actual los individuos
  # que no fueron elegidos como padres (reemplazo de los padres por los hijos)
  # (un padre pudo contribuir en mas de un hijo) con mayor fitness
  def nextgen(self,hijos):
    j = 0
    while hijos.nindiv<popn and j<self.nindiv:
      if not self.popul[j].chosen:
        hijos.add(self.popul[j])
      j += 1
    hijos.recalc()
    hijos.order()
  
  # Elimina de la poblacion de hijos los que tienen fitness menor al promedio de
  # fitness de la poblacion actual y luego agrega a la poblacion de hijos a los que
  # sirvieron como padres, si queda espacio rellena con individuos aleatorios de
  # la poblacion actual que no fuesen padres de los actuales
  def siggen(self,hijos):
    i = 0
    while i<hijos.nindiv:
      if hijos.popul[i].fit<self.fitT/self.nindiv:
        hijos.delete(i)
      i += 1
    i = 0
    while i<self.nindiv:
      if self.popul[i].chosen:
        hijos.add(self.popul[i])
        self.delete(i)
      i += 1
    while hijos.nindiv<popn:
      i = random.randint(0,self.nindiv-1)
      hijos.add(self.popul[i])
      self.delete(i)
    hijos.recalc()
    hijos.order()

  # Aplica mutacion sobre la poblacion
  def mutatepop(self):
    for i in range(self.nindiv-1):
      self.popul[i].mutation()
    self.recalc()
    
  # Funcion que a partir de dos poblaciones
  # Ordena los individuos en la lista de forma descendiente respecto
  # al fitness
  def order(self):
    self.popul.sort(key=lambda x: x.fit, reverse=True)

  # Funcion que genera la poblacion aleatoriamente de tamano popn
  # y la ordena
  def randpop(self):
    while self.nindiv<popn:
      ind = Individual([],False,False)
      ind.random_ind()
      self.add(ind)
    self.order()

  # Copia una poblacion
  def clone(self,other):
    self.popul = other.popul
    self.nindiv = other.nindiv
    self.fitT = other.fitT
    self.nrule = other.nrule


# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
#                                   GLOBALES                                  #
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
# Seleccion 0.Ruleta 
#           1.Torneo
# En ambos casos un individuo puede ser padre de mas de uno de la siguiente generacion
selection = 1
# Supervivencia 0.Reemplazo de todos los padres y de los de menor fitness entre los viejos
#                 No muy elitista
#               1.Hijos con fitness mayor que el promedio + padres +
#                 demas individuos con mayor fitness
#                 Mas elitista
survival = 1
# Uso de las funciones de AddAlternative y DropCondtion
#         0.Disabled
#         1.Enabled
aaydc = 1
# Fitness maximo objetivo (10000 es el fitness maximo posible, el individuo obtenido
# clasifica bien el 100% del conjunto de entrenamiento)
fitThresh = 10000
# Promedio de fitness objetivo de la poblacion
fitPThresh = 7000
# Maximo de generaciones (en caso de que la poblacion se estanque)
MaxGen = 500
# Maximo tamano en reglas de un individuo (no estricto pero los individuos finales
# tienden a estar cerca de este numero de reglas)
maxRules = 15
# Probabilidad de crossover
crossoverP = 0.8
# Probabilidad de mutacion
mutationP = 0.08
# Tamano de la poblacion
popn = 50
# Probabilidad de aplicar Add Alternative
addP = 0.04
# Probabilidad de aplicar Drop Condition
dropP = 0.005
# Cantidad de individuos que participan en el torneo (debe ser potencia de 2)
tourN = 16
# Candidatos a crossover
Pnum = 0.7
candP = (int(Pnum*popn)/2)*2
# Coeficiente de penalidad por cantidad de reglas
rpenalty = 10
# Porcentaje de datos que van al conjunto de entrenamiento, el resto va al conjunto de
# validacion, esta seleccion no es aleatoria
train_perc = 0.4
# Conjuntos de reglas
input_rules = []
train_set = []
val_set = []
# Conjunto de individuos de la generacion actual
poblacion = Population()
# Conjunto de individuos generacion siguiente
poblacionh = Population()


# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
#                                     MAIN                                    #
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
def main(argv):
  input_file = 'iris.data'
  output_file = ''

  f = open(input_file, 'r')
  input_rules = []
  for line in f:
    values = line.split(',')
    if (values[0] != '\n'):
      input_rules.append(values)

  print 'Parametros (editar en el script, parte de var globales):'
  print 'Crossover de 2 puntos y mutacion simple'
  print 'Prob Crossover:',crossoverP,'Prob Mutacion:',mutationP
  print 'Tamano Poblacion:',popn,'Porcentaje a elegir como candidatos a padre:',Pnum*100
  print 'Maximo de generaciones:',MaxGen
  print 'Fitness promedio objetivo:',fitPThresh,'Fitness maximo objetivo:',fitThresh
  print 'Seleccion(0.Ruleta,1.Torneo):',selection
  if selection == 1: print 'Participantes de Torneo:',tourN
  print 'Supervivencia(0.ReemplazoPadres+FittestOld,1.FittestChildren+NoReemplazo):',survival
  print 'AddAlternative y DropCondtion:',aaydc
  if aaydc == 1: print 'AddAlt Prob:',addP,'DropCond Prob:',dropP
  print 'Maximo (no estricto) de Reglas por Indiv:',maxRules
  definetrainval(input_rules)
  poblacion.randpop()
  it = 0
  while poblacion.fitT/poblacion.nindiv<fitPThresh and \
        poblacion.popul[0].fit<fitThresh and \
        it<=MaxGen:
    print 'POBLACION',it
    poblacion.print_pop()
    poblacionh = Population()
    candidatos = []
    i = 0
    while i<candP:
      if selection == 0:
        candidatos.append(poblacion.roulette())
      elif selection == 1:
        candidatos.append(poblacion.tournament(tourN))
      i += 1
    i = 0
    while i<candP:
      if random.random()<crossoverP:
        hij1,hij2 = crossover(candidatos[i],candidatos[i+1])
        poblacionh.add(hij1)
        poblacionh.add(hij2)
      i = i+2
    poblacionh.mutatepop()
    if survival == 0:
      poblacion.nextgen(poblacionh)
    elif survival == 1:
      poblacion.siggen(poblacionh)
    poblacion.clone(poblacionh)
    it += 1
    
  poblacion.recalc()
  poblacion.order()
  print 'POBLACION',it
  poblacion.print_pop(False,False)
  poblacion.popul[0].print_indiv(True)
  clasificarval(val_set,poblacion.popul[0])


# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #
#                                  FUNCIONES                                  #
# ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### #

# Funcion para obtener el conjunto de entrenamiento y validacion
def definetrainval(input_rules):
  i = 0
  n = int(train_perc*len(input_rules))
  while i<n:
    train_set.append(fentogen(input_rules[0]))
    train_set.append(fentogen(input_rules[50-i/3]))
    train_set.append(fentogen(input_rules[100-(i*2)/3]))
    del input_rules[100-(i*2)/3]
    del input_rules[50-i/3]
    del input_rules[0]
    i += 3
  while len(input_rules)>0:
    val_set.append(fentogen(input_rules[0]))
    del input_rules[0]

# Funcion que dice el porcentaje de ejemplos del conjunto de validacion que son bien
# clasificados por un individuo.
def clasificarval(val_set,indiv):
  p = 0
  for r in val_set:
    if clasificabien(indiv.genot,r):
      p += 1
  print 'El individuo mas apto clasifica correctamente un',p*100/len(val_set),'porciento del conjunto de validacion'


# Funcion que recibe una lista de strings que representan a un individuo como en el archivo de input
# y devuelve su representacion binaria para ser usada en GABIL
def fentogen(fenot):
  genot = ''
  # a0 sepal length 0-5
  if float(fenot[0])<4.9:
    genot += '100000'
  elif 4.9<=float(fenot[0])<5.5:
    genot += '010000'
  elif 5.5<=float(fenot[0])<6.1:
    genot += '001000'
  elif 6.1<=float(fenot[0])<6.7:
    genot += '000100'
  elif 6.7<=float(fenot[0])<7.3:
    genot += '000010'
  elif 7.3<=float(fenot[0]):
    genot += '000001'
  # a1 sepal width 6-10
  if float(fenot[1])<2.5:
    genot += '10000'
  elif 2.5<=float(fenot[1])<3:
    genot += '01000'
  elif 3<=float(fenot[1])<3.5:
    genot += '00100'
  elif 3.5<=float(fenot[1])<4:
    genot += '00010'
  elif 4<=float(fenot[1]):
    genot += '00001'
  # a2 petal length 11-17
  if float(fenot[2])<1.85:
    genot += '1000000'
  elif 1.85<=float(fenot[2])<2.7:
    genot += '0100000'
  elif 2.7<=float(fenot[2])<3.55:
    genot += '0010000'
  elif 3.55<=float(fenot[2])<4.4:
    genot += '0001000'
  elif 4.4<=float(fenot[2])<5.25:
    genot += '0000100'
  elif 5.25<=float(fenot[2])<6.1:
    genot += '0000010'
  elif 6.1<=float(fenot[2]):
    genot += '0000001'
  # a3 petal width 18-22
  if float(fenot[3])<0.6:
    genot += '10000'
  elif 0.6<=float(fenot[3])<1.1:
    genot += '01000'
  elif 1.1<=float(fenot[3])<1.6:
    genot += '00100'
  elif 1.6<=float(fenot[3])<2.1:
    genot += '00010'
  elif 2.1<=float(fenot[3]):
    genot += '00001'
  # c Setosa/Verdicolor/Virginica 23-25
  if fenot[4]=='Iris-setosa\n':
    genot += '100'
  elif fenot[4]=='Iris-versicolor\n':
    genot += '010'
  elif fenot[4]=='Iris-virginica\n':
    genot += '001'
  return genot

# Funcion para imprimir una regla con espacios entre cada seccion de la misma
def print_gen(genot):
  print '        '+genot[0:6]+' '+genot[6:11]+' '+genot[11:18]+' '+genot[18:23]+' '+genot[23:26]

# Funcion que verifica que un individuo (genotipo) clasifique bien un ejemplo
# Un individuo clasifica bien un ejemplo si el ejemplo hace match para alguna regla del individuo
def clasificabien(indiv,ejem):
  cb = False
  i = 0
  while i<len(indiv) and not cb:
    if matches(ejem,indiv[i]):
      cb = True
    i += 1
  return cb

# Funcion que verifica que un individuo (genotipo) clasifique bien un ejemplo
# Un individuo clasifica bien un ejemplo si el ejemplo hace match para toda regla del individuo
# def clasificabien(indiv,ejem):
  # cb = True
  # i = 0
  # while i<len(indiv) and cb:
  #   if not matches(ejem,indiv[i]):
  #     cb = False
  #   i += 1
  # return cb

# Funcion para ver si un ejemplo (regla) hace match con una regla de un individuo
def matches(r_ejm,r_ind):
  i = 0
  a = True
  c = True
  while i<23 and a:
    if r_ejm[i] == '1' and r_ind[i] != '1':
      a = False
    i+=1
  c = r_ejm[23:]==r_ind[23:]
  if a:
    if c:
      return True
    else:
      return False
  else:
    if c:
      return False
    else:
      return False
    

def matches2(r_ejm,r_ind):
  return r_ejm == ruleand(r_ejm,r_ind)

# Funcion que genera una regla aleatoriamente
def randrule(n = 1):
  fen = []
  global random1
  a0 = random.uniform(4.3,7.9)
  a1 = random.uniform(2.0,4.5)
  a2 = random.uniform(1,6.95)
  a3 = random.uniform(0.1,2.6)
  c = random.randint(0,2)
  fen.append(a0)
  fen.append(a1)
  fen.append(a2)
  fen.append(a3)
  if c == 0:
    fen.append('Iris-setosa\n')
  elif c == 1:
    fen.append('Iris-versicolor\n')
  elif c == 2:
    fen.append('Iris-virginica\n')
  gen = fentogen(fen)
  # Estas dos lineas se supone que agreguen mas aleatoriedad a las reglas
  #if random.random()<(float(1)/float(n+2)):
  #  gen = ruleor(gen,randrule(n+2))
  return gen

# Aplica OR bit a bit entre dos reglas sin cambiar la clase de la primera
def ruleor(rule1,rule2):
  rule = ''
  for i in range(0,len(rule1)-3):
    if rule1[i] == rule2[i]:
      rule = rule + rule1[i]
    else:
      rule = rule + '1'
  rule = rule + rule1[i:]
  return rule

# Aplica AND bit a bit entre dos reglas
def ruleand(rule1,rule2):
  rule = ''
  for i in range(0,len(rule1)-1):
    if rule1[i] == rule2[i]:
      rule = rule + rule1[i]
    else:
      rule = rule + '0'
  return rule

# Funcion de Crossover: recibe dos individuos con genotipos que pueden ser de distintos
# tamanos retorna los dos individuos hijos resultantes de aplicar crossover de 2 puntos.
# Para el cruce de la posibilidad de AddAlternative y DropCondition en caso de que el valor
# sea igual para los padres el hijo heredara ese valor, en caso de que sean diferentes
# se elige el valor estocasticamente con igual probabilidad para ambos por cada hijo
def crossover(indiv1,indiv2):
  ghij1 = []
  ghij2 = []
  gindiv1 = indiv1.genot
  gindiv2 = indiv2.genot
  x1 = random.randint(0,len(gindiv1)-1)
  x2 = random.randint(x1,len(gindiv1)-1)
  y1 = random.randint(0,len(gindiv2)-1)
  y2 = random.randint(y1,len(gindiv2)-1)
  if x1==x2 or y1==y2:
    a = random.randint(0,25)
    b = random.randint(a+1,26)
  else:
    a = random.randint(0,26)
    b = random.randint(0,26)

  #print 'Puntos elegidos:',a,b
  #print 'Reglas indiv1:',x1,x2
  #print 'Reglas indiv2:',y1,y2

  # Creacion del genotipo del hijo 1
  i = 0
  j = 0
  while i<x1:
    ghij1.append(gindiv1[i])
    i+=1
  if y1!=y2:
    ghij1.append(gindiv1[x1][0:a]+gindiv2[y1][a:])
    j = y1+1
    while j<y2:
      ghij1.append(gindiv2[j])
      j+=1
    ghij1.append(gindiv2[y2][0:b]+gindiv1[x2][b:])
    i = x2+1
    while i<len(gindiv1):
      ghij1.append(gindiv1[i])
      i+=1
  else:
    ghij1.append(gindiv1[x1][0:a]+gindiv2[y1][a:b]+gindiv1[x2][b:])
    i = x2+1
    while i<len(gindiv1):
      ghij1.append(gindiv1[i])
      i+=1

  # Creacion del genotipo del hijo 2
  i = 0
  j = 0
  while j<y1:
    ghij2.append(gindiv2[j])
    j+=1
  if x1!=x2:
    ghij2.append(gindiv2[y1][0:a]+gindiv1[x1][a:])
    i = x1+1
    while i<x2:
      ghij2.append(gindiv1[i])
      i+=1
    ghij2.append(gindiv1[x2][0:b]+gindiv2[y2][b:])
    j = y2+1
    while j<len(gindiv2):
      ghij2.append(gindiv2[j])
      j+=1
  else:
    ghij2.append(gindiv2[y1][0:a]+gindiv1[x1][a:b]+gindiv2[y2][b:])
    j = y2+1
    while j<len(gindiv2):
      ghij2.append(gindiv2[j])
      j+=1

  # Creacion de los individuos
  # Hijo 1
  if indiv1.AddAlt == indiv2.AddAlt:
    aa = indiv1.AddAlt
  else:
    aa = (random.random()<0.5)
  if indiv1.DropCond == indiv2.DropCond:
    dc = indiv1.DropCond
  else:
    dc = (random.random()<0.5)
  hij1 = Individual(ghij1,aa,dc)
  # Hijo 2
  if indiv1.AddAlt == indiv2.AddAlt:
    aa = indiv1.AddAlt
  else:
    aa = (random.random()<0.5)
  if indiv1.DropCond == indiv2.DropCond:
    dc = indiv1.DropCond
  else:
    dc = (random.random()<0.5)
  hij2 = Individual(ghij2,aa,dc)

  # Marcar a los padres como elegidos
  indiv1.chosen = True
  indiv2.chosen = True

  return hij1, hij2

# Funcion que calcula la cantidad de reglas con clase invalida en un conjunto de reglas
# ademas de la cantidad de reglas por encima de maxRules/x (x = 1.8) en cada clase
def nrules(h):
  c000 = 1
  c001 = 0
  c010 = 0
  c100 = 0
  for i in h:
    if i[23:]=='000' or i[23:]=='011' or i[23:]=='101' or i[23:]=='110' or i[23:]=='111':
      c000 += 2
    elif i[23:]=='001':
      c001 += 1
    elif i[23:]=='010':
      c010 += 1
    elif i[23:]=='100':
      c100 += 1
  if c001>maxRules/1.8:
    c000+=c001 
  if c010>maxRules/1.8:
    c000+=c010 
  if c100>maxRules/1.8:
    c000+=c100 
  return c000

# Funcion de Fitness
# fitness(h) = correct(h)^2
# Donde correct(h) es el porcentaje de ejemplos de entrenamiento clasificados
# correctamente por la hipotesis h (genotipo del individuo a calcular su fitness)
def fitness(h):
  c = 0
  for x in train_set:
    if clasificabien(h,x):
      c+=1
  c = c*100/float(len(train_set))
  c = c**2

  # Penalidad al fitness por cantidad de reglas
  
  # Este metodo restringe mucho las reglas, tiende a producir individuos de
  # pocas reglas como los mas aptos
  #if maxRules/3>len(h):
  #  c = c/math.log(len(h)+1)
  #elif 2*(maxRules/3)>len(h)>=maxRules/3:
  #  c = c*3/math.log(len(h)+1)
  #elif maxRules>len(h)>=2*(maxRules/3):
  #  c = c*2/math.log(len(h)+1)
  #if len(h)>=maxRules:
  #  c = c/len(h)
  
  # Este metodo restringe muy poco las reglas
  #c = c/math.log(len(h)+1)

  # Este metodo causa que los individuos mas aptos tiendan a tener carca de maxRules
  c = c/nrules(h)

  # Este metodo a veces produce fitness negativo
  #c = c - rpenalty * (len(h))

  return c


if __name__ == "__main__":
  try:
    main(sys.argv[1:])
  except KeyboardInterrupt:
    print
    pass
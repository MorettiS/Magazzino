#!/usr/bin/env python
from __future__ import generators
__doc__=""" simAGV.py
This is a very basic model, demonstrating the ease
of interfacing to SimGUI.
"""
from SimPy.Simulation  import *
#from random import *
import random
from SimPy.SimGUI import *
from xml.dom import minidom
import math

import time

#Moduli necessari per visualizzazione magazzino
import os, pygame, sys
from pygame.locals import *
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


def print_text(txt,x,y,size,colore=(0,0,255)):
	#scrive testo che si sviluppa verso basso, dx rispetto all'origine (X,Y)
	f = pygame.font.Font(None, size)
	s = f.render(txt, 1, colore)
	screen.blit(s,(x,y))

	
def print_xcentered_text(txt,x,y,size,colore=(0,0,255)):
	#scrive testo centrato orizzontalmente rispetto all'origine (X,Y)
	f = pygame.font.Font(None, size)
	s = f.render(txt, 1, colore)
	screen.blit(s,(x-pygame.Surface.get_width(s)/2,y))

	
def print_ycentered_text(txt,x,y,size,colore=(0,0,255)):
	#scrive testo centrato verticalmente rispetto all'origine (X,Y)
	f = pygame.font.Font(None, size)
	s = f.render(txt, 1, colore)
	screen.blit(s,(x,y-pygame.Surface.get_height(s)/2))

	
def print_xycentered_text(txt,x,y,size,colore=(0,0,255)):
	#scrive testo centrato orizzontalmente e verticalmente rispetto all'origine (X,Y)
	f = pygame.font.Font(None, size)
	s = f.render(txt, 1, colore)
	screen.blit(s,(x-pygame.Surface.get_width(s)/2,y-pygame.Surface.get_height(s)/2))

	
class template ():
	def __init__ (self,larghezza,foro,dmedio,verniciato):
		self.larghezza=larghezza # misure in mm
		self.foro=foro # misure in mm
		self.dmedio=dmedio # misure in mm
		self.sigma=300 # misure in mm
#		self.ID=1000 # misure in mm
		self.ID=0
		self.diam_min=self.foro*1.10
		self.verniciato=verniciato
		
		
	def produci (self):
#		gui.writeConsole("Prodotto id= %s "%(str(self.ID)))
		d=-100
		while(d < self.diam_min/100):
			d=random.gauss(self.dmedio,self.sigma)/100.0 #misura in dm
		p=(3.14/4.0)*(d**2-(self.foro/100)**2)*(self.larghezza/100) * 7.85 # peso in kg  (peso specifico in kg/dm^3)
#		coils.add(str(self.ID),0,self.larghezza,diametro,peso,False)
#		self.ID=self.ID+1
		self.ID=int(random.random()*150000)
		return ([self.ID,self.larghezza,d*100,p,self.verniciato])
#-----------------------------------------------------------------			
#-----------------------------------------------------------------			
#-----------------------------------------------------------------			
#-----------------------------------------------------------------			

def intersezione_cerchi (r1,r2,x1,z1,x2,z2):
	if (math.sqrt((x2-x1)**2+(z2-z1)**2) > (r1+r2)):
		#distanza fra i due centri superiore alla somma dei raggi delle circonferenze!
		return [-1,-1]

	alfa1=-2.0*x1
	beta1=-2.0*z1
	gamma1=1.0*(x1**2+z1**2-r1**2)
	alfa2=-2.0*x2
	beta2=-2.0*z2
	gamma2=1.0*(x2**2+z2**2-r2**2)
	#gui.writeConsole("DEBUG:\nalfa1 = %.2f\nbeta1 = %.2f\ngamma1 = %.2f\nalfa2 = %.2f\nbeta2 = %.2f\ngamma2 = %.2f\n" % (alfa1, beta1, gamma1, alfa2, beta2, gamma2))
	
	k1=(gamma2-gamma1)/(alfa1-alfa2) 
	k2=(beta2-beta1)/(alfa1-alfa2)
	delta=(2*k1*k2+alfa2*k2+beta2)**2-4*(k2**2+1)*(k1**2+alfa2*k1+gamma2)
	
	#gui.writeConsole("DEBUG: k1 = %.2f, k2 = %.2f, delta = %.2f" % (k1, k2, delta))
	zp=((-2*k1*k2-alfa2*k2-beta2)+math.sqrt(delta))/(2*(k2**2+1))
	zm=((-2*k1*k2-alfa2*k2-beta2)-math.sqrt(delta))/(2*(k2**2+1))
	xp=k1+k2*zp
	xm=k1+k2*zm
	#gui.writeConsole("Pp=(%.2f,%.2f) Pm=(%.2f,%.2f)"%(xp,zp,xm,zm))

	if (zp > zm):
		return [xp,zp]
	else:
		return [xp,zm]

	
#-----------------------------------------------------------------			
#-----------------------------------------------------------------

			
class magazzino ():
# definisce il layout del magazzino
# file = numero di file
# box = numero di box per fila
# org : misura di origine delle file org[0] e dei box org[1]
# passo : distanza tra le file passo[0] e tra i box passo[1]
# Una cella e' rappresentata da uno stato di occupazione (True,False) ,
# una quota di file e una quota di box

	def __init__(self,nome,file,box,org,passo,peso_max,cp_ass,screen=None,background=None):
		self.me=[]
		self.cp_associato=cp_ass
		self.id=nome
		self.screen=screen
		self.background=background
		self.n_file=file
		self.n_box=box
		self.origine=org
		self.passo_celle=passo

		for i in range(0,file):
			self.peso_max=peso_max
			fila=[]
			quota_f=org[0]+passo[0]*i
			for j in range (0,box):
				quota_b=org[1]+passo[1]*j
				fila.append([False,quota_f,quota_b,self.peso_max,-1])	
			self.me.append(fila)
		if (self.screen):	# Attivata interfaccia grafica
			self.screen_length=0
			self.screen_height=0
			self.background_color=(255,255,255)
			background_transparency=False
			self.font_size=10
			self.font_color=(0,0,0)
			self.cell_length=25
			self.cell_height=25
			self.busy_cell_color=(150, 222, 209)
			self.free_cell_color=(127,127,127)
			self.window_title="Magazzino"
			self.show_window_title=False
			self.scale_factor=1.0
			#self.draw()
	
			gui.writeConsole("Creato magazzino: %s"%(self.id))	#DEBUG
	
	def inizializza_grafica(self, window_title, show_window_title, background_color, background_transparency, font_size, font_color, cell_length, cell_height, busy_cell_color, free_cell_color, scale_factor):
		self.window_title=window_title							# titolo finestra, es. "Magazzino 1 - Ground Level"
		self.show_window_title=show_window_title				# se =1 visualizza titolo, altrimenti no.
		#self.screen_length=screen_length 						# larghezza finestra grafica, es. 1024
		#self.screen_height=screen_height 						# altezza finestra grafica, es. 768
		self.background_color=background_color 					# colore di sfondo finestra, es. (230,240,250)
		self.background_transparency=background_transparency 	# sfondo trasparente: 1 = trasparenza ON, 0 = trasparenza OFF
		self.font_size=font_size 								# dimensione caratteri standard, es. 10
		self.font_color=font_color 								# colore caratteri standard, es. (0,0,0)
		self.cell_length=cell_length 							# larghezza cella magazzino, es. 25
		self.cell_height=cell_height 							# altezza cella magazzino, es. 25
		self.busy_cell_color=busy_cell_color					# colore assegnato alla cella OCCUPATA
		self.free_cell_color=free_cell_color					# colore assegnato alla cella LIBERA
		self.scale_factor=scale_factor							# rapporto pixel/mm

		pygame.display.set_caption("Layout Magazzino")
		pygame.mouse.set_visible(1)

		
		if (self.background_transparency):	# Genera uno sfondo TRASPARENTE
			background = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
			background = background.convert_alpha()
		else:
			background = pygame.Surface(screen.get_size())
			background.convert()
			background.fill(background_color)
		
		screen.blit(background, (0, 0))
		#self.draw()
		
	def set_cella_occupata(self,fila,box,id):
		m=self.me[fila][box]
		m[0]=True
		m[3]=id
		self.me[fila][box]=m
		if (self.screen):
			self.draw_cella(m,id)
		
	def set_cella_libera(self,fila,box):
		m=self.me[fila][box]
		m[0]=False
		ret=m[3]
		m[3]=-1
		self.me[fila][box]=m
		if (self.screen):
			self.draw_cella(m)
		return (ret)

	def get_fila (self,fila):
		return (self.me[fila])
		
	def get_numero_file(self):
		return (len(self.me[0]))

	def draw_cella(self, cl,id=0):
		if (self.screen):
			if(cl[0]):
				#Cella PIENA
				txt =str(id)
				pygame.draw.rect(self.screen, self.busy_cell_color, (cl[1]*self.scale_factor, cl[2]*self.scale_factor,self.cell_length*self.scale_factor, self.cell_height*self.scale_factor), 0)	#pygame.draw.rect(screen, color, (x,y,width,height), thickness)
				#gui.writeConsole("Piena: cl[1]=%d cl[2]=%d"%(cl[1],cl[2]))	#DEBUG
			else:
				#Cella VUOTA
				txt = ""
				# "Cancella" la cella prima di sovrascriverla
				#pygame.draw.rect(self.screen, self.background_color, (cl[1]*self.scale_factor, cl[2]*self.scale_factor,self.cell_length*self.scale_factor, self.cell_height*self.scale_factor), 0)	#Rettangolo pieno dello stesso colore del bordo
				pygame.draw.rect(self.screen, self.free_cell_color, (cl[1]*self.scale_factor, cl[2]*self.scale_factor,self.cell_length*self.scale_factor, self.cell_height*self.scale_factor), 1)	#pygame.draw.rect(screen, color, (x,y,width,height), thickness)
				#gui.writeConsole("Vuota: cl[1]=%d cl[2]=%d"%(cl[1],cl[2]))	#DEBUG
			
			#def print_xcentered_text(txt,x,y,size,colore=(0,0,255)):
			print_xycentered_text(txt, (cl[1]+self.cell_length/2)*self.scale_factor, (cl[2]+self.cell_height/2)*self.scale_factor, self.font_size, self.font_color)

		return ()
		
	def	draw (self):
		if (self.screen):
			if (not self.background_transparency):
				self.screen.fill(self.background_color)
			for f in self.me:
				for b in f:
					self.draw_cella(b, b[3])
			pygame.display.update()
		
			#Scrive n. fila e n. box in ascissa e ordinata
			for i in range(0, self.n_file):
				print_xcentered_text(str(i),(self.origine[0]+i*self.passo_celle[0]+self.cell_length/2)*self.scale_factor, (self.origine[1]-self.font_size)*self.scale_factor,self.font_size,self.font_color)
			for j in range(0, self.n_box):
				print_ycentered_text(str(j),(self.origine[0]-self.font_size)*self.scale_factor, (self.origine[1]+j*self.passo_celle[1]+self.cell_height/2)*self.scale_factor,self.font_size,self.font_color)
			
			
			if (self.show_window_title):	#Mostra titolo finestra in alto al centro
				print_xcentered_text(self.window_title,screen.get_width()/2, 10,self.font_size*2,self.font_color)
			pygame.display.flip()
		return ()
		

		
# Scandisce tutto il magazzino e seleziona la cella 
# per la quale la differenza diametro con quello accanto e' minore
# restituisce numero fi fila e numero di box sotto forma di lista
# [fila,box]	
	def parcatura_per_diametro (self,diametro):
		f=0;
		for fila in self.me:
			b=0
			d_min=1000000
			box_prec=[]
			for box in fila:
				if (not box[0]): #la cella e' libera
					if (len(box_prec)):
						d=coils.cerca(box_prec[3])["diametro"]
						if ((abs(diametro-d)< d_min)):
							cella=box
				b=b+1
			f=f+1
			return([f,b])		
	

		return ()
	
	
class BaseDati():
	def __init__(self):
		self.me = dict()

	def aggiorna_posizione(self,id,fila,box,livello):
		if (id in self.me):
			self.me[id]={"fila":fila,"box":box,"livello":livello,}
			return True
		else:
			return False
			
	def add(self,id,spessore,larghezza,diametro,peso,verniciato):
		if not(id in self.me):
			self.me[id]={"diametro":diametro,"larghezza":larghezza,"peso":peso,"verniciato":verniciato,"fila":-1,"box":-1,"livello":-1,}
			return True
		else:
			return False
	
	def cerca(self,id):
		if (id in self.me):
			return self.me[id]
		else:
			return False

	def cancella(self,id):
		if (id in self.archivio):
			del self.archivio[id]
			return True
		else:
			return False
#-----------------------------------------------------------------			
class producer(Process):

	def __init__ (self,nome,out_buffer,rate,sigma, tipo_rotolo, db=None):
		Process.__init__(self,name=nome)
		self.id=nome
		self.tipo="producer"
		self.db=db
		self.tipo_rotolo=tipo_rotolo
		self.out=out_buffer
		self.rate=int(rate)
		self.sigma=int(sigma)
		self.stato="IDLE"
		#self.count=0
		gui.writeConsole("Definita macchina %s  %s deposita sulla stazione %s ogni %s s "% (self.tipo,self.id,self.out,self.rate))

	def produce(self):
		self.buffer=cerca_elemento(self.out,percorso)
		
		while True:
			self.actualrate=random.gauss(self.rate,self.sigma)
			
			#gui.writeConsole("DEBUG: %d"% (int(self.tipo_rotolo[4:])))	#Estrae numero N dalla stringa "TipoN"
			rotolo=vetrina[int(self.tipo_rotolo[4:])-1]	#Estrae numero N dalla stringa "TipoN" --> Diventa indice del vettore vetrina
			gui.writeConsole("Tipo rotolo: %s"% (self.tipo_rotolo))
			r=rotolo.produci()
			
#			gui.writeConsole("%.2f %s: In  attesa per %s"% (now(),self.id,self.actualrate))
			yield hold,self,self.actualrate
			#self.count=self.count+1
#			gui.writeConsole("%.2f %s: Prodotto un Coil %s "% (now(),self.id,self.count))

			yield put,self,self.buffer.store,["coil ID: "+str(r[0])] #r[0]= ID del coil generato dal metodo rotolo.produci()
			#gui.writeConsole("%.2f %s: Depositato un Coil Codice_%s # su %s"% (now(),self.id,self.count,self.buffer.id))
			gui.writeConsole("%.2f %s: Depositato Coil ID: %s su %s"% (now(),self.id,str(r[0]),self.buffer.id))
			self.db.add(r[0],0,r[1],r[2],r[3],(r[4]=="True"))
			
			#Comunica ID coil prodotto al carico e al database
			self.buffer.set_id_coil(r[0])
			gui.writeConsole("%.2f %s: Aggiunto Coil ID: %s al database - %s, Verniciato: %s"% (now(),self.id,str(r[0]), self.tipo_rotolo, r[4]))
			
	def define_new_consumer (sef,consumer):
		self.consumer=consumer
		gui.writeConsole("Definita Nuovo Consumer % per  %s"% (self.consumer,self.id))
		
		
	
class consumer (Process):

	def __init__ (self,nome,in_buffer,rate,sigma):
		Process.__init__(self, name=nome)
		self.id=nome
		self.tipo="consumer"
		self.inp=in_buffer
		self.rate=int(rate)
		self.sigma=int(sigma)
		self.stato="IDLE"
            	gui.writeConsole("Definita macchina %s  %s preleva dalla stazione %s ogni %s s "% (self.tipo,self.id,self.inp,self.rate))

	def consume(self):
		self.buffer=cerca_elemento(self.inp,percorso)
		while True:
			self.actualrate=random.gauss(self.rate,self.sigma)
			yield hold,self,self.actualrate
			gui.writeConsole("%.2f %s: In attesa di prelievo  Coil su %s"% (now(),self.id,self.buffer.id))
			yield get,self,self.buffer.store,
	            	gui.writeConsole("%.2f %s: Prelevato un Coil da %s"% (now(),self.id,self.buffer.id))
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------- Processo di Gestione Movimentazione (CP) ---------------------------------------------------------------------------
class cp (Process):

	def __init__(self,nome,velmax,ini_staz,index,mag_associato=None,db=None):
		Process.__init__(self, name=nome)
		self.id=nome
		self.db=db
		self.tipo="cp"
		self.mag_associato=mag_associato
		self.pos=ini_staz
		self.park=ini_staz
		self.dest="Nessuna"
		self.load=0		 
		self.stato = "LIBERO"
		self.v_max=int(velmax)
		self.vel=0 
		self.verso="*" 		##may be "+" , "-" or "*"
		self.Ti=0
		self.Tlibero=0
		self.Ttraveling=0
		self.Tmission=0
		self.mlibero=index
		self.mtraveling=index+1
		self.mmission=index+2
		self.durata_prelievo=60
		self.sigma_prelievo=1
		self.durata_scarico=55
		self.sigma_scarico=2
		self.posizione_corrente=stazione("POS",0,0)  #[nome,x,y]
		#self.magazzini=[]
		gui.writeConsole("Definita macchina %s  %s in attesa alla stazione = %s "% (self.tipo,self.id,self.pos))

	def crane_driver (self):
		self.locate=cerca_elemento(self.pos,percorso) #Posizione iniziale
		self.posizione_corrente.id=self.locate.id
		self.posizione_corrente.xpos=self.locate.xpos
		self.posizione_corrente.ypos=self.locate.ypos
		gui.writeConsole("Posizione iniziale carroponte %s: (%d,%d) "% (self.posizione_corrente.id, self.posizione_corrente.xpos, self.posizione_corrente.ypos)) #DEBUG
		
		self.Tcambio=now()
		self.cambio_stato=1
		gui.writeConsole("Associato magazzino %s a carroponte %s"% (self.mag_associato.id, self.id)) #DEBUG 
		while True:
			if self.cambio_stato:
				gui.writeConsole("%.2f %s: Stato %s "% (now(),self.id,self.stato))
				gui.simulation[self.mlibero].observe(self.Tlibero)
				gui.simulation[self.mtraveling].observe(self.Ttraveling)
				gui.simulation[self.mmission].observe(self.Tmission)
				self.cambio_stato=0
			if (self.stato =="LIBERO"):
				yield hold,self,1
				self.Tlibero=self.Tlibero+now()-self.Ti
				self.Ti=now()
				if (self.dest!="Nessuna"):
					gui.writeConsole("Posizione corrente carroponte %s: (%d,%d) "% (self.posizione_corrente.id, self.posizione_corrente.xpos, self.posizione_corrente.ypos)) #DEBUG
					
					if (self.locate):
						self.stato="MISSION"
						self.cambio_stato= 1
					
			elif (self.stato=="TRAVELING") or (self.stato =="MISSION"):
				if (self.stato=="TRAVELING"):
					self.Ttraveling=self.Ttraveling+now()-self.Ti
				else:
					self.Tmission=self.Tmission+now()-self.Ti
				
				#Stato: MISSION
				self.Ti=now()
				self.dst=cerca_elemento(self.dest,percorso)
				self.Tmission=self.Tmission+now()-self.Ti
				gui.writeConsole("Sono qui: %s coordinate: (%d,%d) "% (self.posizione_corrente.id,self.posizione_corrente.xpos,self.posizione_corrente.ypos)) #DEBUG 
				gui.writeConsole("Devo andare qui: %s coordinate: (%d,%d) "% (self.dest,self.dst.xpos,self.dst.ypos)) #DEBUG 
				gui.writeConsole("Distanza: %f "% (self.calcola_distanza(self.posizione_corrente.xpos,self.posizione_corrente.ypos,self.dst.xpos,self.dst.ypos))) #DEBUG
				
				#Attesa proporzionale alla distanza percorsa per andare al punto di prelievo + tempo di prelievo
				self.t_attesa=self.calcola_distanza(self.posizione_corrente.xpos,self.posizione_corrente.ypos,self.dst.xpos,self.dst.ypos)/self.v_max+random.gauss(self.durata_prelievo,self.sigma_prelievo)
				gui.writeConsole("%.2f Tempo di attesa: %f"% (now(), self.t_attesa)) #DEBUG 
				yield hold,self,self.t_attesa
				
				#Arrivato a destinazione (stazione di PRELIEVO)
				self.id_coil_prelevato=self.dst.get_id_coil()
				gui.writeConsole("%.2f %s: Prelevato coil ID %s da %s"% (now(),self.id,self.id_coil_prelevato,self.dst.id)) #DEBUG 
				
				#Aggiorna posizione carroponte
				#self.locate=self.dst
				self.posizione_corrente.id=self.dst.id
				self.posizione_corrente.xpos=self.dst.xpos
				self.posizione_corrente.ypos=self.dst.ypos
							
				#Carico
				if (self.dst.tipo =="carico"):
					reactivate(self.dst,at=now())
					self.stato="MISSION"
					self.cambio_stato=1
					self.load=self.load+self.dst.nrpeek
					yield get,self,self.dst.store,self.dst.nrpeek
					yield hold,self,self.dst.delay
				
				
				
				
				
				#Individua sella di destinazione all'interno del magazzino secondo un criterio di parcatura da stabilire
				#
				# DA FARE...
				#
				
				#DEBUG: per semplicita' al momento la cella di destinazione e' CASUALE
				self.cella_dest_x=int(random.random()*self.mag_associato.n_file)
				self.cella_dest_y=int(random.random()*self.mag_associato.n_box)
				
				
				#Calcola distanza da posizione attuale a sella destinazione e aspetta un tempo proporzionale a tale distanza + tempo di scarico
				gui.writeConsole("Distanza da posizione attuale (%s) a sella di destinazione (%d,%d): %f "% (self.posizione_corrente.id, self.cella_dest_x,self.cella_dest_y,self.calcola_distanza(self.posizione_corrente.xpos,self.posizione_corrente.ypos,self.cella_dest_x,self.cella_dest_y)))
				
				self.t_attesa=self.calcola_distanza(self.posizione_corrente.xpos,self.posizione_corrente.ypos,self.cella_dest_x,self.cella_dest_y)/self.v_max+random.gauss(self.durata_scarico,self.sigma_scarico)
				gui.writeConsole("%.2f Tempo di attesa: %f"% (now(), self.t_attesa)) #DEBUG 
				yield hold,self,self.t_attesa
				
				#Aggiorna posizione carroponte
				self.posizione_corrente.id="CELLA_MAG"
				self.posizione_corrente.xpos=self.cella_dest_x
				self.posizione_corrente.ypos=self.cella_dest_y
				
				#Deposita il coil nella sella di destinazione
				self.mag_associato.set_cella_occupata(self.cella_dest_x,self.cella_dest_y,self.id_coil_prelevato)
				gui.writeConsole("%.2f %s: Depositato coil ID %s su %s (%d,%d)"% (now(),self.id,self.id_coil_prelevato,self.mag_associato.id,self.posizione_corrente.xpos,self.posizione_corrente.ypos)) #DEBUG 
				
				
				#Aggiorna nel database le coordinate del coil depositato all'interno del magazzino
				#Servono funzioni set_fila, set_box, ecc.
				#
				# DA FARE...
				#
				#self.db.cerca(self.id_coil_prelevato)
				self.db.aggiorna_posizione(self.id_coil_prelevato,self.cella_dest_x,self.cella_dest_y,self.mag_associato.id) #DEBUG 
				gui.writeConsole("%.2f %s: Aggiunto Coil ID: %s al database"% (now(),self.id,self.id_coil_prelevato)) #DEBUG 
				#gui.writeConsole("DEBUG -------> %s "% (self.db.cerca(self.id_coil_prelevato))) #DEBUG 
	
				self.stato="LIBERO"
				self.cambio_stato=1

			#sys.exit()
				
	def set_magazzino (self,magazzino):
		#self.magazzini.append(magazzino)
		pass
		
		
					
# #					gui.writeConsole("%.2f  Trovata Postazione iniziale:  %s in  %s"% (now(),self.id,self.locate.id))
					# if (self.locate):
						# self.stato="MISSION"
						# self.cambio_stato= 1
			# elif (self.stato=="TRAVELING") or (self.stato =="MISSION"):
# #				yield hold,self,1
				# if (self.stato=="TRAVELING"):
					# self.Ttraveling=self.Ttraveling+now()-self.Ti
				# else:
					# self.Tmission=self.Tmission+now()-self.Ti
				# self.Ti=now()
				# self.pos=self.locate.id
				# if (self.locate.id == self.dest): #----------------- Arrivato a destinazione
					# gui.writeConsole("%.2f %s: Arrivato a Destinazione %s(%s) "% (now(),self.id,self.locate.id,self.locate.tipo))
					# if (self.locate.tipo =="carico"):
						# gui.writeConsole("%.2f %s: Carica da %s (Coils = %d) per scaricare in %s "% (now(),self.id,self.locate.id,self.locate.store.nrBuffered,self.locate.consumer))
						# self.destinazione(self.locate.consumer)
						# self.locate=cerca_elemento(self.pos,percorso) 
						# reactivate(self.locate,at=now())
						# self.stato="MISSION"
						# self.cambio_stato=1
						# self.load=self.load+self.locate.nrpeek
						# yield get,self,self.locate.store,self.locate.nrpeek
						# yield hold,self,self.locate.delay
					# elif(self.locate.tipo=="scarico"):
						# gui.writeConsole("%.2f %s: Scarica su %s (coils=%d) "% (now(),self.id,self.locate.id,self.locate.store.nrBuffered+self.load))
						# self.destinazione(self.park)	
						# self.locate=cerca_elemento(self.pos,percorso) 
						# self.stato="TRAVELING"
						# self.cambio_stato = 1
						# yield hold,self,self.locate.delay
						# for i in range(1,self.load+1):
							# yield put,self,self.locate.store,["coil"]
						# self.load=0
					# elif(self.locate.tipo=="park"):
# #						gui.writeConsole("%.2f %s: Arrivato a Destinazione %s "% (now(),self.id,self.locate.id))
						# self.stato="LIBERO"
						# self.cambio_stato=1
						# self.dest="Nessuna"
					# else:
# #						gui.writeConsole("MARK ????? ")
						# gui.writeConsole("%.2f %s: Arrivato a Destinazione %s"% (now(),self.id,self.locate.id))
						# self.stato="LIBERO"
						# self.cambio_stato=1
						# self.dest="Nessuna"
				# else: 
					# if self.locate.tipo=="tratto":
						# self.vel=self.v_max
						# if self.locate.v_max<self.vel:
							# self.vel=self.locate.v_max

						# gui.writeConsole("Velocita' %s: %.0f m/min nel tratto %s" %  (self.id, self.vel, self.locate.id))
						# self.T=60.0*self.locate.lunghezza/(self.vel)

						# if len(self.locate.r.activeQ)<> 0:
                    					# gui.writeConsole("%.2f %s: In attesa di percorrere il Tratto %s che e' occupato"% (now(),self.id,self.locate.id))
                				# yield request,self,self.locate.r 
# #                				gui.writeConsole("%.2f %s: sta percorrendo il Tratto %s con verso %s"% (now(),self.id,self.locate.id,self.verso))
                				# yield hold,self,self.T
                				# yield release,self,self.locate.r
						# if (self.verso=="+"):
							# self.verso=self.locate.next_p[-1]
							# self.locate=cerca_elemento(self.locate.next_p[:-1],percorso) #----- Si posiziona sul tratto successivo
						# elif (self.verso=="-"):
							# self.verso=self.locate.next_m[-1]
							# self.locate=cerca_elemento(self.locate.next_m[:-1],percorso) #----- Si posiziona sul tratto successivo
					# elif self.locate.tipo=="incrocio":
# #						gui.writeConsole("%.2f %s: all'incrocio %s Cerca direzione per %s"% (now(),self.id,self.locate.id,self.dest))
						# i=self.locate.id
						# self.verso=self.locate.cerca_per(self.dest)[-1]
						# self.locate=cerca_elemento(self.locate.cerca_per(self.dest)[:-1],percorso)
# #                    				gui.writeConsole("%.2f %s: all'incrocio %s presa direzione %s "% (now(),self.id,i,self.locate.id))
					# else:
						# self.verso=self.locate.next[-1]
# #                  				gui.writeConsole("%.2f %s cerca %s"% (now(),self.id,self.locate.next[:-1]))
						# self.locate=cerca_elemento(self.locate.next[:-1],percorso) #----- Si posiziona sul (punta al)  tratto successivo
# #                  				gui.writeConsole("%.2f %s Trovato %s"% (now(),self.id,self.locate.id))
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------


	def calcola_distanza (self,x1,y1,x2,y2):
		return math.sqrt((x2-x1)**2+(y2-y1)**2)

		
	def destinazione(self,dest):
		self.dest=dest
		gui.writeConsole("%.2f %s: Acquisita Missione: Destinazione %s"% (now(),self.id,self.dest))
		

	def distanza (self,staz):
		self.dist=0
		self.v="*"
		self.a=cerca_elemento(self.pos,percorso) 
		self.b=cerca_elemento(staz,percorso)
		self.v= self.verso
#		gui.writeConsole("A = %s a  B = %s Distanza = %d"% (self.a.id,self.b.id,self.dist))
		while self.a.id!=self.b.id:
#			gui.writeConsole("A = %s a  B = %s verso %s Distanza = %d"% (self.a.id,self.b.id,self.v,self.dist))
			if self.a.tipo =="tratto":
				self.dist=self.dist+int(self.a.lunghezza)
				if (self.v=="+"):
					self.v=self.a.next_p[-1]
					self.a=cerca_elemento(self.a.next_p[:-1],percorso) #----- Si posiziona sul tratto successivo
				elif (self.v=="-"):
					self.v=self.a.next_m[-1]
					self.a=cerca_elemento(self.a.next_m[:-1],percorso) #----- Si posiziona sul tratto successivo
			elif self.a.tipo =="incrocio":
				self.v=self.a.cerca_per(self.b.id)[-1]	
				self.a=cerca_elemento(self.a.cerca_per(self.b.id)[:-1],percorso)				
			else:
				self.v=self.a.next[-1]
				self.a=cerca_elemento(self.a.next[:-1],percorso)
		gui.writeConsole("%.2f %s: Distanza da %s  = %d"% (now(),self.id,staz,self.dist))
		return self.dist

	def mission (self,stazLoad):
		self.stato="MISSION"
		self.cambio_stato=1;
		self.destinazione(stazLoad)
			
			
#---------- Fine Classe CP ---------------------------------------------------------------------------------------------------------------------------				




	
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

class tratto (object):
	def __init__(self,nome,l,v,next_p="",next_m="",fullduplex="N"):
		self.id=nome
		self.tipo="tratto"
		self.lunghezza=int(l)
		self.v_max=int(v)
		if fullduplex=="Y" :
			self.r=Resource(capacity=4,name="tratto",unitName=self.id)
			self.percorrenza="Bidirezionale"
		else:
			self.r=Resource(capacity=1,name="tratto",unitName=self.id)
			self.percorrenza="Monodirezionale"

		if (next_p[-1]=="+") or (next_p[-1]=="-"):
			self.next_p=next_p
		else:
			self.next_p=next_p+"*"

		if (next_m[-1]=="+") or (next_m[-1]=="-"):
			self.next_m=next_m
		else:
			self.next_m=next_m+"*"

            	gui.writeConsole("Definito Tratto %s next+= %s next-= %s lunghezza= %s m velocita = %s m/s %s"% (self.id,self.next_p,self.next_m,self.lunghezza,self.v_max,self.percorrenza))
		
class scarico (Process):

	def __init__(self,nome,s,next,delay,xpos,ypos):

		self.tipo="scarico"
		self.id=nome
		self.capacity=int(s)
		self.container=[]
		self.store=Store(capacity=self.capacity,initialBuffered=self.container,monitored=True)
#		self.r=Resource(capacity=self.capacity,name="scarico",unitName=self.id)
		self.next=next
		self.delay=int(delay)
            	gui.writeConsole("Definito Scarico %s Capacity= %s next= %s Tempo di scarico = %d s"% (self.id,self.capacity,self.next,self.delay))
		self.xpos=xpos
		self.ypos=ypos

class carico (Process):

	def __init__(self,nome,s,next,consumer,delay,monitor,nrpeek,xpos,ypos):
		Process.__init__(self, name=nome)
		self.tipo="carico"
		self.id_coil_da_producer="XXX"
		self.id=nome
		self.capacity=int(s)
		self.container=[]
		self.store=Store(capacity=self.capacity,initialBuffered=self.container,monitored=True)
#		self.r=Resource(capacity=s,name="carico",unitName=self.id)
		self.next=next
		self.cp=[] # Macchine CARROPONTE
		self.consumer= consumer
		self.delay=int(delay)
		self.monitor = monitor
		self.nrpeek=int(nrpeek)
            	gui.writeConsole("Definito Carico %s Capacity= %s next= %s consumer=%s Tempo di Carico = %d s"% (self.id,self.capacity,self.next,self.consumer,self.delay))
         	gui.writeConsole("    ........Numero di pezzi prelevati ad ogni ciclo %s"% (self.nrpeek))
		self.xpos=xpos
		self.ypos=ypos

	
	def set_id_coil(self,id_coil):
		#gui.writeConsole("id_coil in carico: %s"% (id_coil))
		self.id_coil_da_producer=id_coil
		
	def get_id_coil(self):
		return self.id_coil_da_producer
	
	# ------ da fare ----- # adattare logica selezione AGV a quella del CARROPONTE # ------ da fare ----- #
	def automate(self):
		for self.e in movimentazione:
			if self.e.tipo=="cp":
				self.cp.append(self.e)
		self.flag=0
		while True:
			yield hold,self,1
			if (self.store.nrBuffered >= self.nrpeek):
				if not self.flag:
					gui.writeConsole("%.2f %s: Disponibili %d coils"% (now(),self.id,self.store.nrBuffered))
					gui.simulation[self.monitor].observe(self.store.nrBuffered)
				self.distanza = 10000 # distanza non raggiungibile in nessuna configurazione di calcolo
				self.i=0
				self.cp_id=-1
				for self.m in self.cp:
#					if not self.flag:
#						gui.writeConsole("%.2f %s: Calcolo distanza per %s"% (now(),self.id,self.m.id))
					if (self.m.stato == "LIBERO") or (self.m.stato=="TRAVELING"):
						self.d = self.m.distanza (self.id)
						if ( self.d < self.distanza):
							self.distanza = self.d
							self.cp_id=self.i
					self.i=self.i+1
				self.flag=1
				#gui.writeConsole("----- DEBUG: ID coil da assegnare: %s "% (self.id_coil_da_producer)) #DEBUG
				if (self.cp_id > -1):
					self.flag=0
					self.cp[self.cp_id].mission(self.id)
#					gui.writeConsole("%.2f Stazione di Carico %s Assegnata Missione a  %s "% (now(),self.id,self.agv[self.agv_id].id))
					yield passivate,self


class incrocio (object):
	def __init__(self,nome,nexts):
		self.tipo="incrocio"
		self.id=nome
		self.nexts=destination_parser(nexts)
#		self.r=Resource(capacity=1,name="incrocio",unitName=self.id)
            	gui.writeConsole("Definito incrocio %s"% (self.id))
		for i in self.nexts:
			gui.writeConsole("        Per %s  segui  %s"% (i[0],i[1]))

	def cerca_per(self,dest):
#            	gui.writeConsole("su %s si cerca direzione  %s"% (self.id,dest))
		for e in self.nexts:
			if e[0]==dest:
				return e[1]
		return None


class park(object):
	def __init__(self,nome,next,xpos,ypos):
		self.id=nome
		self.tipo="park"
		self.xpos=xpos
		self.ypos=ypos
		if (next[-1]=="+") or (next[-1]=="-"):
			self.nex=next
		else:
			self.next=next+"*"

            	gui.writeConsole("Definita Posizione di Home %s "% (self.id))


class stazione(object):
	def __init__(self,nome,xpos,ypos):
		self.id=nome
		self.xpos=xpos
		self.ypos=ypos

				
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#  PICCOLA LIBRERIA LOCALE di funzioni ausiliarie 
#        **************************
# 
# - Ricerca una elemento nel percorso in base al nome (id)
# - Conversione delle unita' di tempo della simulazione in Giorni:Ore:Minuti:Secondi
# - Calcola la distanza temporale assoluta (unita' di tempo di simulazione) tra due orari
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#Ricerca una elemento nella lista in base al nome (id)
#----------------------------------------------------------------------------------------------

def cerca_elemento(nome,lista):
	
#	gui.writeConsole("Ricerca di  %s"% (nome))
	for e in lista:
		if e.id == nome:
#			gui.writeConsole("Trovato %s"% (nome))
			return e
	return None
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
# Converte il valore di unita' di tempo (assunte come secondi)
# in Giorno Ore:minuti:secondi (ggg-hh:mm:ss)
#----------------------------------------------------------------------------------------------
def ora (s):
    g = int(s/86400)
    s=s%86400
    h= int(s/3600)
    s=s%3600
    m=int(s/60)
    s=int(s%60)
    return "%3d-%02d:%02d:%02d"%(g,h,m,s)
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
# Calcola la distanza temporale assoluta (unita' di tempo di simulazione) tra due orari
#  hh:mm:ss
#----------------------------------------------------------------------------------------------
def tempo_distanza(a,b):
    return (3600*int(b[:2])+60*int(b[3:5])+int(b[6:]))-(3600*int(a[:2])+60*int(a[3:5])+int(a[6:]))
#----------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------
# Analizza la stringa di destinazione di un incrocio e restituisce una lista di coppie destinazione;direzione
# 
#-------------------------------------------------------------------------------------------------------------
def destination_parser(destinations):
	d=[]
	dest=destinations.split(",")
	for e in dest:
		if (e.split("=")[1][-1]!="+") and (e.split("=")[1][-1]!="-"):
			d.append([e.split("=")[0],e.split("=")[1]+"*"])
		else:
			d.append([e.split("=")[0],e.split("=")[1]])
	return d
#----------------------------------------------------------------------------------------------

class Launcher(Process):
    nrLaunched=0
    def launch(self,id):
        while True:
            tof = uniform(1,gui.params.maxFlightTime)
            gui.writeConsole("%d: Launch at %.1f, going %.1f"% (id,now(),tof) )
            Launcher.nrLaunched+=1
            gui.launchmonitor.observe(Launcher.nrLaunched)
            yield hold,self,tof
            gui.writeConsole("%d: Boom!!! Aaaah!! at %.1f"% (id,now()))

def read_layout():
	xml_data = minidom.parse("impianto.xml")
	for l in xml_data.getElementsByTagName("layout"):
		for e in l.childNodes:
#			gui.writeConsole(e.nodeName)
			if (e.nodeName=="tratto"):
				a= e.getAttribute("nome")
				c= e.getAttribute("vmax") 
				b= e.getAttribute("lunghezza")
				d= e.getAttribute("next_p")
				f= e.getAttribute("next_m")
				g= e.getAttribute("full")
				percorso.append(tratto(a,b,c,d,f,g))
			if (e.nodeName=="incrocio"):
				a= e.getAttribute("nome")
				b=e.getAttribute("destmap")
				percorso.append(incrocio(a,b))
			if (e.nodeName=="carico"):
				a= e.getAttribute("nome")
				b= e.getAttribute("size") 
				c= e.getAttribute("next")
				d= e.getAttribute("to")
				ee= e.getAttribute("delay")
				gui.simulation.append(Monitor(name=a+" Queue",ylab="Coils",tlab="time"))
				f=len(gui.simulation)-1
				g=e.getAttribute("nrpeek")
				x=e.getAttribute("xpos")
				y=e.getAttribute("ypos")
				percorso.append(carico(a,b,c,d,ee,f,g,int(x),int(y)))
			if (e.nodeName=="scarico"):
				a= e.getAttribute("nome")
				b= e.getAttribute("size") 
				c= e.getAttribute("next")
				d= e.getAttribute("delay")
				x=e.getAttribute("xpos")
				y=e.getAttribute("ypos")
				percorso.append(scarico(a,b,c,d,int(x),int(y)))
			if (e.nodeName=="park"):
				a= e.getAttribute("nome")
				b= e.getAttribute("next")
				x=e.getAttribute("xpos")
				y=e.getAttribute("ypos")
				percorso.append(park(a,b,int(x),int(y)))

def read_prodotti():
	xml_data = minidom.parse("impianto.xml")
	for l in xml_data.getElementsByTagName("prodotto"):
		for e in l.childNodes:
			if (e.nodeName=="tipo"):
				a=e.getAttribute("nome")
				b=e.getAttribute("diametro")
				c=e.getAttribute("larghezza")
				d=e.getAttribute("foro")
				f=e.getAttribute("verniciato")
				vetrina.append(template(int(c),int(d),int(b),f))

def read_magazzini():
	xml_data = minidom.parse("impianto.xml")
	for l in xml_data.getElementsByTagName("magazzini"):
		for e in l.childNodes:
#			gui.writeConsole(e.nodeName)
			if (e.nodeName=="magazzino"):
				n= e.getAttribute("nome")
				f= e.getAttribute("n_file") 
				b= e.getAttribute("n_box")
				xo= e.getAttribute("x_origine")
				yo= e.getAttribute("y_origine")
				xp= e.getAttribute("x_passo")
				yp= e.getAttribute("y_passo")
				p= e.getAttribute("peso_max")
				cp= e.getAttribute("cp_associato")
				magazzini.append(magazzino(n,int(f),int(b),(xo,yo),(xp,yp),p,cp))
						
def read_handling():
	xml_data = minidom.parse("impianto.xml")
	for h in xml_data.getElementsByTagName("handler"):
		for m in h.childNodes:
			#gui.writeConsole(m.nodeName)
			if (m.nodeName == "cp"):
				a= m.getAttribute("nome")
				b= m.getAttribute("vel_max") 
				d= m.getAttribute("pos")
				gui.simulation.append(Monitor(name=a+" LIBERO Time",ylab=" Secondi",tlab="time"))
				f=len(gui.simulation)-1
				gui.simulation.append(Monitor(name=a+" TRAVELING Time",ylab=" Secondi",tlab="time"))
				gui.simulation.append(Monitor(name=a+" MISSION Time",ylab=" Secondi",tlab="time"))
				for mg in magazzini:
					if (mg.cp_associato == a): #Trovato magazzino da associare al cp corrente
						movimentazione.append(cp(a,b,d,f,mg,db_rotoli))
						#gui.writeConsole("------------DEBUG: a=%s, mg.cp_associato=%s"%(a, mg.cp_associato))
			if (m.nodeName == "producer"):
				a= m.getAttribute("nome")
				b= m.getAttribute("to") 
				c= m.getAttribute("rate")
				d= m.getAttribute("sigma")
				e= m.getAttribute("tipo_prodotto")
				movimentazione.append(producer(a,b,c,d,e, db_rotoli))
			if (m.nodeName == "consumer"):
				a= m.getAttribute("nome")
				b= m.getAttribute("from") 
				c= m.getAttribute("rate")
				d= m.getAttribute("sigma")
				movimentazione.append(consumer(a,b,c,d))

				
				
def visualizza_magazzini(magazzini):
    #DEBUG
    #Visualizza contenuto magazzini
    stringa=""
    for mg in magazzini:
		gui.writeConsole("\n\nContenuto magazzino %s:\n"%(mg.id))
		for b in range(0,mg.n_box):
			#gui.writeConsole("\n")
			for f in range(0,mg.n_file):
				stringa = stringa + str(mg.get_fila(f)[b][0])[:1] + " "
			gui.writeConsole("%s"%(stringa))
			stringa=""


			
def model():
    global db_rotoli
    initialize()
    db_rotoli=BaseDati()	#Crea database coils
    del movimentazione[:]
    del percorso[:]
    del magazzini[:]
    del gui.simulation[:]
    read_prodotti()
    read_layout()
    read_magazzini()
    read_handling()

    
    #rotolo=template (800,600,1100)
    
    # #crea magazzino
    # passo=[40,30]
    # org=[70,70]
    # n_file=20
    # n_box=10
    # mag=magazzino ("MAG1",n_file,n_box,org,passo,10,"CP1")
	
    
    # # vengono riempite 10 celle a caso
    # for i in range(1,10):
		# mag.set_cella_occupata(int(random.random()*n_file),int(random.random()*n_box),int(random.random()*1000))
	
	
	
    for p in movimentazione:
        if (p.tipo =="producer"):
	       	activate(p,p.produce(),at=0)
        	gui.writeConsole("Attivato Processo %s %s"%(p.tipo,p.id))
        if (p.tipo =="consumer"):
        	activate(p,p.consume(),at=0)
        	gui.writeConsole("Attivato Processo %s %s"%(p.tipo,p.id))
        if (p.tipo =="cp"):
        	activate(p,p.crane_driver(),at=0)
        	gui.writeConsole("Attivato Processo %s %s"%(p.tipo,p.id))

    for p in percorso:
        if (p.tipo =="carico"):
        	activate(p,p.automate(),at=0)
        	gui.writeConsole("Attivato Processo %s %s"%(p.tipo,p.id))
	
	#i=0
	for r in vetrina:
		#DEBUG
		#da fare
		pass
	
    simulate(until=gui.params.duration)
#    simulate(until=10000)
    gui.noRunYet=False
    gui.writeConsole("Simulazione Terminata")
    gui.writeConsole("%d"%(len(gui.simulation)))
    # for m in gui.simulation :
	# t= m.tseries()
	# i=0
	# gui.writeConsole("%s"%(m.name))
	# for x in m.yseries():
		# gui.writeConsole("%s : %s"%(t[i] ,x))
		# i=i+1
#    gui.writeStatusLine("%s rockets launched in %.1f minutes"%(Launcher.nrLaunched,now()))
    visualizza_magazzini(magazzini)
	
    


				
def db_gen():
	db_rotoli = BaseDati()
#	id,spessore,larghezza,diametro,peso
	rotolo=template (1000,600,1100)
	for i in range(1,5000):
		r=rotolo.produci()
		if(not db_rotoli.cerca(r[0])):
			db_rotoli.add(r[0],0,r[1],r[2],r[3],(r[4]=="True"))
			res = db_rotoli.cerca(r[0])
			if res <> 0 :
				gui.writeConsole("id= %s   larghezza = %d diametro = %d peso = %d"%(r[0],res["larghezza"],res["diametro"],res["peso"]))
			else:
				gui.writeConsole("%s Non Trovato"%(id))
		else:
			gui.writeConsole("id= %s   Esiste "%(r[0]))
			
	gui.writeConsole("DataBase Creato")
	
def  intersezione ():
	
	punti=intersezione_cerchi (15,15,20,10,30,10)
	gui.writeConsole("x= %.2f z = %.2f"%(punti[0],punti[1]))
	

	
def  magazzino_gen ():
	global screen
	
	#Initializza ambiente grafico Pygame
	pygame.init()
	# screen = pygame.display.set_mode((1024, 768), RESIZABLE)
	screen = pygame.display.set_mode((0,0), RESIZABLE)	#Inizializza una finestra con la stessa risoluzione dello schermo in uso (es. 1440 x 900) ridimensionabile
	
	#Prepare Objects
	clock = pygame.time.Clock()

	# ---------------------------------------- MAGAZZINO 1 ----------------------------------------	
	#Definisce oggetto magazzino #1
	passo=[40,30]
	org=[70,70]
	n_file=20
	n_box=10
	mag=magazzino ("MAG1",n_file,n_box,org,passo,10,"CP1",screen)

	# Preferenze ambiente grafico magazzino #1
	window_title="Warehouse 1: Ground Level"
	show_window_title = 1
	background_color=(240,250,250)
	background_transparency = 0
	font_size=15
	font_color=(0,0,0)
	cell_length=30
	cell_height=30
	busy_cell_color=(150, 222, 209)
	free_cell_color=(127,127,127)
	scale_factor=1

	#def inizializza_grafica(self, window_title, show_window_title, background_color, background_transparency, font_size, font_color, cell_length, cell_height, busy_cell_color, free_cell_color, scale_factor):
	mag.inizializza_grafica(window_title, show_window_title, background_color, background_transparency, font_size, font_color, cell_length, cell_height, busy_cell_color, free_cell_color, scale_factor)
	
	# vengono riempite 10 celle a caso
	for i in range(1,10):
		mag.set_cella_occupata(int(random.random()*n_file),int(random.random()*n_box),int(random.random()*1000))


	
	# Aggiorna lo schermo: usare ogni volta che viene modificata la configurazione del magazzino
	mag.draw()
	pygame.display.flip()
	
	
	#time.sleep(3)
	
	# ---------------------------------------- MAGAZZINO 2 ----------------------------------------
	#Definisce oggetto magazzino #2
	passo=[40,30]
	org=[70,85]
	n_file=10
	n_box=10
	mag2=magazzino ("MAG2",n_file,n_box,org,passo,10,"CP2",screen)


	# Preferenze ambiente grafico magazzino #2
	window_title="Warehouse 1: Level 1"
	show_window_title = 1
	background_color=(240,240,240)
	background_transparency = 0
	font_size=15
	font_color=(50,50,50)
	cell_length=30
	cell_height=30
	busy_cell_color=(180, 110, 130)
	free_cell_color=(127,100,150)
	scale_factor=1

	#def inizializza_grafica(self, window_title, show_window_title, background_color, background_transparency, font_size, font_color, cell_length, cell_height, busy_cell_color, free_cell_color, scale_factor):
	mag2.inizializza_grafica(window_title, show_window_title, background_color, background_transparency, font_size, font_color, cell_length, cell_height, busy_cell_color, free_cell_color, scale_factor)
	
	# vengono riempite 10 celle a caso
	for i in range(1,10):
		mag2.set_cella_occupata(int(random.random()*n_file),int(random.random()*n_box),int(random.random()*1000))

	
	
	# Aggiorna lo schermo: usare ogni volta che viene modificata la configurazione del magazzino
	mag2.draw()
	pygame.display.flip()

	# Event loop
	while 1:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
			if event.type == KEYUP:
				if event.key == K_1:	# Se premuto tasto '1', mostra magazzino #1
					mag.draw()
				if event.key == K_2:	# Se premuto tasto '2', mostra magazzino #2
					mag2.draw()




class MyGUI(SimGUI):
    def __init__(self,win,**par):
		SimGUI.__init__(self,win,**par)
		self.run.add_command(label="Acquisisci Layout",command=read_layout,underline=0)
		self.run.add_command(label="Acquisisci Handling System", command=read_handling,underline=0)
		self.run.add_command(label="Avvia Simulazione", command=model,underline=0)
		self.run.add_command(label="Crea DataBase", command=db_gen,underline=0)
		self.run.add_command(label="Intersezione Circonferenze", command=intersezione,underline=0)
		self.run.add_command(label="Riempi magazzino (PROVA)", command=magazzino_gen,underline=0)
		self.params=Parameters(duration=28800,destinazione="C2",nrLaunchers=3)
      
# Variabili GLOBALI
root=Tk()
gui=MyGUI(root,title="SimCoilMag",doc=__doc__,consoleHeight=50)
gui.simulation=[]
vetrina=[]
magazzini=[]
movimentazione=[]
percorso=[]
archivio=[]
gui.mainloop()

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
from SimPy.Simulation import *
from xml.dom import minidom
#----------------------------------------------------------------------------------------------
mark ="================================================================================\n"
#----------------------------------------------------------------------------------------------
# Tratta di linea :
#
#  Una serie di tratte forma una linea ferroviaria
#  Solo un treno alla volta puo' occupare questa risorsa
#      
#     La configurazione della tratta e' data da questi parametri
#        ordine = numero o codice identificativo
#        v_max = velocita' massima di percorrenza km/h
#        length = Lunghezza in metri
#        next = numero o codice di riferimento (opzionale)
#----------------------------------------------------------------------------------------------
class tratta (object):
    print "\n\n\n========================\n Definita Classe Tratta\n========================"

    def __init__(self,ordine,v,l,next=0):
        if str(type(ordine)) <> "<type 'str'>":
            self.id = str(ordine)
        else:
            self.id=ordine
        self.nome="tratta"
        self.r = Resource(capacity=1, name='tratta', unitName=self.id)
        self.v_max= v
        self.length =l
        if str(type(next)) != "<type 'str'>":
            self.next = str(next)
        else:
            self.next=next
        out_file3.write(" |%s|%s|%s|%s|\n" %(self.id.center(8, ' '),str(self.v_max).center(14, ' '),str(self.length).center(11, ' '),self.next.ljust(24, ' '))) 
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
# Scambio di Tratta :
#
#  Elemento che serve a deviare una risorsa Treno su una tratta
#  ad un bivio
#      
#     La configurazione dello scambio e' data da questi parametri
#        ordine  = codice o nome identificativo
#        next_dv = tratta successiva in deviata
#        next_ct = tratta successiva su corretto tracciato
# la posizione dello scambio e' determita dal parametro 
# stato  = 0 ->> Deviata 
#              1 ->> Corretto Tracciato (default)
#
#----------------------------------------------------------------------------------------------
class scambio (object):

    print "\n\n\n========================\n Definita Classe Scambio\n========================"
  
    def __init__(self,ordine,next_dv,next_ct,stato): 
        self.nome="scambio"

        if str(type(ordine)) <> "<type 'str'>":
            self.id = str(ordine)
        else:
            self.id=ordine
        self.r = Resource(capacity=1, name='scambio', unitName=self.id)

        if str(type(next_dv)) <> "<type 'str'>":
            self.dv = str(next_dv)
        else:
            self.dv=next_dv

        if str(type(next_ct)) <> "<type 'str'>":
            self.ct = str(next_ct)
        else:
            self.ct=next_ct
        self.stato= stato                 

        if self.stato==1 :
            out_file3.write(" Scambio  %s su Corretto Tracciato-->>%s  ( Deviata -->>%s) \n" % (self.id,self.ct,self.dv))
        
        if self.stato==0 :
            out_file3.write(" Scambio  %s su Deviata -->>%s (Corretto Tracciato-->>%s) \n" % (self.id,self.dv,self.ct))

    def set_ct(self):
            self.stato=0
    def set_dv(self):
            self.stato=1
                
                
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
# Scambio di Linea :
#
#  Elemento che serve a modificare la linea sulla quale viaggia una risorsa Treno
#      
#     La configurazione dello scambio e' data da questi parametri
#        ordine  = codice o nome identificativo
#        change_name = nome della nuova linea
#        change_next = tratta della nuova linea in cui si immette il treno
#        next_cont= nome della vecchia tratta
# la posizione dello scambio e' determita dal parametro 
# stato  = 0 ->> se cambia linea
#          1 ->> stessa linea
#
#----------------------------------------------------------------------------------------------
class cambio_linea (object):

    print "\n\n\n================================\n Definita Classe cambio di linea\n================================"
  
    def __init__(self,ordine,change_name,change_next,next_cont,stato): 
        self.nome="cambio_linea"

        if str(type(ordine)) <> "<type 'str'>":
            self.id = str(ordine)
        else:
            self.id=ordine
        self.r = Resource(capacity=1, name='cambio_linea', unitName=self.id)

        if str(type(change_name)) <> "<type 'str'>":
            self.change_name = str(change_name)
        else:
            self.change_name=change_name
        if str(type(change_next)) <> "<type 'str'>":
            self.change_next = str(change_next)
        else:
            self.change_next=change_next
        if str(type(next_cont)) <> "<type 'str'>":
            self.next_cont = str(next_cont)
        else:
            self.next_cont=next_cont
        self.stato= stato                 

        if self.stato==1 :print "cambio linea"
        
        if self.stato==0 :print "stessa linea"
        
    def set_cont(self):
            self.stato=0
    def set_change(self):
            self.stato=1
              
#----------------------------------------------------------------------------------------------
#Stazione:
#             Gestita come una tratta particolare con piu' risorse a disposizione.
#                 Caratteristica della stazione sono il numero dei Binari disponibili
#             che vengono gestiti fino a riempimento totale: Un treno non ha un binario particolare ma
#                occupa il primo libero. In caso di completa occupazione il treno attebnde fuori della
#                stazione.
#
#----------------------------------------------------------------------------------------------
class stazione (object):

    print "\n\n\n=========================\n Definita Classe Stazione\n========================="

    def __init__(self,nome_stazione,n_binari,next,stop_time):
        self.id= nome_stazione
        self.nome= "stazione"
        self.nome_st = nome_stazione
        self.n_binari=n_binari
        self.tempo_attesa=stop_time
        self.r = Resource(capacity=n_binari, name=self.id, unitName=self.id)

        if str(type(next)) <> "<type 'str'>":
            self.next = str(next)
        else:
            self.next=next
            
        out_file3.write(" |%s|%s|%s|%s|\n" % (self.nome_st.ljust(24,' '),str(n_binari).center(8,' '),self.tempo_attesa.center(17,' '),self.next.center(6,' ')))

#----------------------------------------------------------------------------------------------
#
#----------------------------------------------------------------------------------------------
# Treno e' il processo che modella l'attivita' di un treno su una linea
#    Un  treno e' definito da;
#        nome : stringa che ha lo scopo di identificare univocamkente il treno
#         lunghezza: per rapportare l'impegno residuo sulla tratta appena percorsa
#     Velocita' Massima : confrontata con la velocita' massima della tratta che sta percorrendo deve risultare inferiore o uguale
#        Velocita' assegnata: deve essere inferiore o uguale a quella massima di treno e quella di tratta      
#        Tabella Orario: Dizionario la cui chiave e' una stringa identificativa del nome di stazione:
#                                        Stazione    Ora Arrivo    Ora Partenza
#                                        ========= ==========  ============
#                                        'Firenze'|'10:35:00' |'10:45:00'        
#
#----------------------------------------------------------------------------------------------
class treno(Process):

    def __init__(self,nome,lunghezza,v_max):
        Process.__init__(self, name=nome)
        self.nome = nome
        self.lunghezza=lunghezza
        self.v_max = v_max
        self.tabella_orario= {}
        self.scambi={}
        self.cambi={}
        out_file2.write("Creato Treno %s  Lunghezza = %d m  --  Velocita' Massima = %d Km/h\n"% (self.nome,self.lunghezza,self.v_max))
        #print "Creato Treno %s  Lunghezza = %d m  --  Velocita' Massima = %d Km/h"% (self.nome,self.lunghezza,self.v_max)

    def partenza(self):
        linea_attuale=self.linea
        sezione=cerca_linea(linea_attuale)[indice(self.tratta_in,cerca_linea(linea_attuale))]
        ciclo_stop=0
        if len(sezione.r.activeQ)==0:
            out_file4.write("%s  Treno %3s in linea %s in partenza dalla stazione di %s \n"% (ora(now()),self.nome,cerca_linea(linea_attuale)[0],sezione.nome_st))
        while ciclo_stop == 0:
            if sezione.nome == "tratta":     
                veleff=min(self.vel,sezione.v_max)       
                tempo= 3600*sezione.length/(veleff*1000)
                if len(sezione.r.activeQ)<> 0:
                    out_file4.write("%s  Treno %3s in linea %s in attesa ingresso alla tratta %s, occupata dal treno %s\n"% (ora(now()),self.nome,cerca_linea(linea_attuale)[0],sezione.r.unitName,sezione.r.activeQ[0].name))
                yield request,self,sezione.r 
                out_file4.write("%s  Treno %3s in linea %s entrato nella tratta %s per %d secondi\n"% (ora(now()),self.nome,cerca_linea(linea_attuale)[0],sezione.r.unitName,tempo))
                yield hold,self,tempo
                yield release,self,sezione.r
                if sezione.next <> '-1':
                    sezione = cerca_linea(linea_attuale)[indice(sezione.next,cerca_linea(linea_attuale))]
                else:
                    ciclo_stop = 1
            elif sezione.nome == "scambio":
                out_file4.write("%s  Treno %3s in linea %s attraversa lo scambio %s \n"%(ora(now()),self.nome,cerca_linea(linea_attuale)[0],sezione.id))
                sezione.stato=self.scambi[sezione.id]
                if sezione.stato == 1 :
                    sezione = cerca_linea(linea_attuale)[indice(sezione.dv,cerca_linea(linea_attuale))]
                else:
                    sezione = cerca_linea(linea_attuale)[indice(sezione.ct,cerca_linea(linea_attuale))]
                out_file4.write("%s  Treno %3s in linea %s deviato nella tratta %s \n"% (ora(now()),self.nome,cerca_linea(linea_attuale)[0],sezione.r.unitName))
            elif sezione.nome == "cambio_linea":
                sezione.stato=self.cambi[sezione.id]
                if sezione.stato == 1:
                    linea_attuale=cerca_linea(sezione.change_name)[0]
                    sezione=cerca_sezione(sezione.change_next,linea_attuale)
                    out_file4.write("%s  Treno %3s devia nella linea %s\n" %(ora(now()),self.nome,linea_attuale))
                else:
                    sezione=cerca_linea(linea_attuale)[indice(sezione.next_cont,cerca_linea(linea_attuale))]
            elif sezione.nome == "stazione":
                out_file4.write("ffss "+sezione.nome_st+"\n")
                if sezione.next != '-1':
                    for x in self.tabella_orario.keys():
                        if x==sezione.nome_st:
                            yield request,self,sezione.r
                            if sezione.nome_st!=self.stazione_partenza:
                                out_file4.write("%s  Treno %3s entrato in stazione %s\n"% (ora(now()),self.nome,sezione.r.unitName))
                            if self.tabella_orario[sezione.nome_st][0]>=ora(now())[4:]:
                                yield hold,self,max(tempo_distanza("00:00:00",sezione.tempo_attesa),tempo_distanza(ora(now())[4:],self.tabella_orario[sezione.nome_st][1]))
                                yield release,self,sezione.r
                                out_file4.write("%s  Treno %3s esce dalla stazione %s\n"% (ora(now()),self.nome,sezione.r.unitName))
                            else:
                                yield hold,self, max(tempo_distanza("00:00:00",sezione.tempo_attesa),min(abs(tempo_distanza(ora(now())[4:],self.tabella_orario[sezione.nome_st][1])),tempo_distanza("00:00:00",sezione.tempo_attesa)))
                                yield release,self,sezione.r 
                                out_file4.write("%s  Treno %3s esce dalla stazione %s\n"% (ora(now()),self.nome,sezione.r.unitName))
                    sezione = cerca_linea(linea_attuale)[indice(sezione.next,cerca_linea(linea_attuale))]
                else:
                    ciclo_stop = 1
        out_file4.write(mark+"%s  Treno %3s Arrivato a destinazione \n"% (ora(now()),self.nome)+mark)
    
    def formazione (self,linea,tratta):
        out_file2.write("Formato Treno %s su sezione %s\n\n" % (self.nome,tratta))
        out_file2.write(" -----------------------------------------------------------------------\n\n")
        self.linea = linea
        if str(type(tratta)) <> "<type 'str'>":
            self.tratta_in = str(tratta)
        else:
            self.tratta_in=tratta

    def set_scambi(self,s,p):
        self.scambi[s]=p
        
    def set_cambi(self,s,p):
        self.cambi[s]=p
        
    def devlinea (self, linea,tratta):
        self.linea=linea
        if str(type(tratta)) <> "<type 'str'>":
            self.tratta_in = str(tratta)
        else:
            self.tratta_in=tratta
    
    def set_vel(self,vel):
        self.vel=vel

    def compila_tabella (self,stazione,ora_arrivo,ora_partenza):
        self.tabella_orario[stazione]=[ora_arrivo,ora_partenza]
        self.ora_arrivo=ora_arrivo
        self.ora_partenza=ora_partenza
        
    def arrivo_previsto(self,stazione,ora):
        self.ora_arrivo = ora
        self.stazione_arrivo=stazione 

    def partenza_prevista(self,stazione,ora):
        self.ora_partenza = ora
        self.stazione_partenza=stazione 
        
    def print_tabella(self):
        nuovalista={}
        for key,val in self.tabella_orario.items():
            nuovalista[tuple(val)]=key            
        out_file1.write(" |==============================================|\n")
        out_file1.write(" |       Stazione         |  Arrivo  | Partenza |\n")
        out_file1.write(" |==============================================|\n")       
        for value in sorted(nuovalista.keys()):           
            out_file1.write(" |%s | %s | %s |\n"% ( nuovalista[value].ljust(23, '.'),value[0],value[1])  )
        out_file1.write(" |==============================================|\n\n")

#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------
#  PICCOLA LIBRERIA LOCALE di funzioni ausiliarie 
#        **************************
#  - Stampa di una tabella orario
#     - Ricerca di un elemento in un lista
#  - Conversione delle unita' di tempo della simulazione in Giorni:Ore:Minuti:Secondi
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
# Ricerca un elemento in una lista
#                             Restituisce la posizione come indice 
# E' richiesto che tutti gli elementi della lista abbiano un campo .id definito di tipo stringa
#----------------------------------------------------------------------------------------------
def indice (elemento,lista):
    for i, e in enumerate(lista):
        if i!=0:
            if e.id == elemento:
                result= i
                break
            else:
                result = False
    return result
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
def tempo_distanza(a,b):
    return (3600*int(b[:2])+60*int(b[3:5])+int(b[6:]))-(3600*int(a[:2])+60*int(a[3:5])+int(a[6:]))

#----------------------------------------------------------------------------------------------
#Ricerca una sezione e ne estrare lo ID o nome e il tipo
def cerca_sezione(id_sezione,nome_linea):
    for l in rete:
        if l[0] == nome_linea:
            for s in l[1:]:
                if s.id == id_sezione:
                    return s
    return None
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
#Ricerca una linea in base al nome

def cerca_linea(nome_linea):
    for l in rete:
        if l[0] == nome_linea:
            return l
    return None
#----------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------
# Main Program 
#    ****
#----------------------------------------------------------------------------------------------
# definizione linee ferroviarie
#              ********
#----------------------------------------------------------------------------------------------
xml_data = minidom.parse("miaprova3.xml")
#
#===========================================================================
#
out_file1 = open("itinerario_treni.txt","w")
out_file1.write("                ITINERARIO TRENI\n\n")
out_file2 = open("formazione_treni.txt","w")
out_file2.write("                      CREAZIONE E FORMAZIONE TRENI\n\n")
out_file3 = open("configurazione_linee.txt","w")
out_file3.write("                      CONFIGURAZIONE LINEE")
out_file2.write(" -----------------------------------------------------------------------\n\n")
out_file4 = open("viaggio.txt","w")
out_file4.write("                                               VIAGGIO\n\n")
out_file4.write(" ---------------------------------------------------------------------------------------------------------------\n\n")
initialize()
#definizione contenitore linee
rete=[] 
#Scandisce tutte le linee della rete 
# per costruire le sezioni
for l in xml_data.getElementsByTagName("linea"):
    linea=[]
    linea.append(l.getAttribute("nome"))
    out_file3.write("\n\n -------------------------------------------------------------\n")
    out_file3.write("                          Linea "+linea[0]+"\n")
    out_file3.write(" -------------------------------------------------------------\n\n")
    out_file3.write(" |============================================================|\n")
    out_file3.write(" | Tratta | Vmax in Km/h | Lunghezza |          next          |\n")
    out_file3.write(" |============================================================|\n")
    cont=0
#Scandisce le sezioni di una linea per connetere gli elementi
# tratta scambio stazione
    for s in l.childNodes:
#Analizza l'elemento di sezione per istanziarlo 
        for e in s.childNodes:
            if e.nodeName =="tratta":
                a= e.getAttribute("id")
                b= e.getAttribute("v_max") 
                c= e.getAttribute("lunghezza")
                d= e.getAttribute("next")
                linea.append(tratta(a,int(b),int(c),d))
            if e.nodeName =="scambio":
                a= e.getAttribute("id")
                b= e.getAttribute("next_dv") 
                c= e.getAttribute("next_ct")
                d= e.getAttribute("stato")
                if d!='': linea.append(scambio(a,b,c,int(d)))
                else : linea.append(scambio(a,b,c,d))
            if e.nodeName =="stazione":
                if cont==0:
                    out_file3.write("\n |==========================================================|\n")
                    out_file3.write(" |        Stazione        | Binari | tempo di attesa | next |\n")
                    out_file3.write(" |==========================================================|\n")
                cont = cont+1
                a= e.getAttribute("nome")
                b= e.getAttribute("binari") 
                c= e.getAttribute("next")
                stop_time=e.getAttribute("tempo_fermata")
                linea.append(stazione(a,int(b),c,stop_time))
            if e.nodeName =="cambio":
                f=e.getAttribute("id")
                a= e.getAttribute("change_name")
                b= e.getAttribute("change_next") 
                c= e.getAttribute("next_cont")
                d=e.getAttribute("stato")
                linea.append(cambio_linea(f,a,b,c,d))
    rete.append(linea)
#==============================================================================================
#==============================================================================================
flotta=[] # definizione contenitore  treni
n_treni=-1
for t in xml_data.childNodes[1].getElementsByTagName("treno"):
    out_file1.write("--------------------------------------------------\n\n")
    out_file1.write(" Itinerario del treno %s:\n\n" %t.getAttribute("nome"))
    flotta.append(treno(t.getAttribute("nome"),int(t.getAttribute("v_max")),int(t.getAttribute("lunghezza"))))
    n_treni=n_treni+1
    for e in t.childNodes:
#----------------------------------------------------------------------------
# definisce la tabella di orario
#----------------------------------------------------------------------------
            if e.nodeName =="orario":
                flotta[n_treni].compila_tabella(e.getAttribute("stazione"),e.getAttribute("ora_arrivo"),e.getAttribute("ora_partenza"))
#----------------------------------------------------------------------------
# definisce Itinerario:
#                                Sezione di partenza sulla linea (Formazione)
#                                Ora di partenza (Formazione)
#                                Velocita' di crociera = Vmax di default (formazione)
#                                Stazione e ora di arrivo (arrivo)
#                                Posizione degli scambi in linea (switch)
#----------------------------------------------------------------------------                
            if e.nodeName =="itinerario":
                for i in e.childNodes:
                    if i.nodeName =="switch":
                        s=cerca_sezione(i.getAttribute("id"),i.getAttribute("linea"))
                        if s!=None :
                            if i.getAttribute("stato")=="ct":
                                flotta[n_treni].set_scambi(s.id,0)
                                out_file1.write( "   scambio %s su Corretto Tracciato\n" %i.getAttribute("id"))
                            if i.getAttribute("stato")=="dv":
                                flotta[n_treni].set_scambi(s.id,1)
                                out_file1.write( "   scambio %s su Deviata\n" %i.getAttribute("id"))
                    if i.nodeName =="cambio":
                        s=cerca_sezione(i.getAttribute("id"),l)
                        if s!=None :
                            if i.getAttribute("stato")=="0":
                                flotta[n_treni].set_cambi(s.id,0)
                                out_file1.write( "   deviazione %s non effettuata\n" %i.getAttribute("id"))
                            if i.getAttribute("stato")=="1":
                                flotta[n_treni].set_cambi(s.id,1)
                                out_file1.write( "   deviazione %s effettuata\n" %i.getAttribute("id"))
                    if i.nodeName =="formazione":
                        l=i.getAttribute("linea")
                        ora_partenza=i.getAttribute("ora")
                        L=cerca_linea(l)
                        flotta[n_treni].partenza_prevista(i.getAttribute("sezione"),i.getAttribute("ora"))
                        flotta[n_treni].formazione(i.getAttribute("linea"),i.getAttribute("sezione"))
                        flotta[n_treni].set_vel(flotta[n_treni].v_max)
                        activate(flotta[n_treni],flotta[n_treni].partenza(),at=tempo_distanza("00:00:00",i.getAttribute("ora")))
                        out_file1.write( "   Parte da "+cerca_sezione(i.getAttribute("sezione"),i.getAttribute("linea")).id+" alle "+i.getAttribute("ora")+"\n")
                        flotta[n_treni].compila_tabella(cerca_sezione(i.getAttribute("sezione"),i.getAttribute("linea")).id,"00:00:00",i.getAttribute("ora"))
                    if i.nodeName =="arrivo":
                        flotta[n_treni].arrivo_previsto(i.getAttribute("stazione"),i.getAttribute("ora"))
                        flotta[n_treni].compila_tabella(i.getAttribute("stazione"),i.getAttribute("ora"),"00:00:00")
    flotta[n_treni].print_tabella()
simulate(until=100000.0)
out_file1.close()
out_file2.close()
out_file3.close()
out_file4.close()
#-----------------------------------------------------------------------------


# coding: utf-8

# In[5]:


#calenderier
import tkinter as tk
import webbrowser 
from pymongo import MongoClient
import simplekml
import os 
import tkinter.ttk as ttk


url_2 = 'https://www.marinetraffic.com/en/ais/home/centerx:-12.0/centery:25.0/zoom:4'

root = tk.Tk()
root.title("IMT atlamtique PS4")
root.geometry('300x500')

#Affichier le nom de la liste déroulante
l1 = tk.Label(root, text="OpenYear", font=('Arial', 15))
l1.pack() 
#Créer une liste déroulante de year
openYearText = ttk.Combobox(root, values=[i for i in range(2009, 2050)])
openYearText.pack ()

#Affichier le nom de la liste déroulante
l2 = tk.Label(root, text="OpenMonth", font=('Arial', 15))
l2.pack() 
#Créer une liste déroulante de month
openMonthText = ttk.Combobox(root, values=[i for i in range(1, 13)])
openMonthText.pack()

#Affichier le nom de la liste déroulante
l3 = tk.Label(root, text="OpenDay", font=('Arial', 15))
l3.pack()
#Créer une liste déroulante de day  
openDayText = ttk.Combobox(root, values=[i for i in range(1, 31)])
openDayText.pack()

#Affichier le nom de la liste déroulante
l4 = tk.Label(root, text="CloseYear", font=('Arial', 15))
l4.pack()
#Créer une liste déroulante de year 
closeYearText = ttk.Combobox(root, values=[i for i in range(2009, 2050)])
closeYearText.pack()

#Affichier le nom de la liste déroulante
l5 = tk.Label(root, text="CloseMonth", font=('Arial', 15))
l5.pack() 
#Créer une liste déroulante de month
closeMonthText = ttk.Combobox(root, values=[i for i in range(1, 13)])
closeMonthText.pack()

#Affichier le nom de la liste déroulante
l6 = tk.Label(root, text="CloseDay", font=('Arial', 15))
l6.pack()
#Créer une liste déroulante de day  
closeDayText = ttk.Combobox(root, values=[i for i in range(1, 31)])
closeDayText.pack()

#Affichier le nom de la liste déroulante
l7 = tk.Label(root, text="Region", font=('Arial', 15))
l7.pack()
#Créer une liste déroulante de day  
regionText = ttk.Combobox(root, values=['Guyane française', 'China East Sea'])
regionText.pack()

#Affichier le nom de la liste déroulante
l8 = tk.Label(root, text="PortServeur", font=('Arial', 15))
l8.pack()
#Une espace de text pour saisir l'information  
portText = tk.StringVar()
port = tk.Entry(root, textvariable = portText)
#Verifier ecq useur a deja saisi numero de la porte, si oui, il va afficher l'informaton que 
#useur a saisi le dernier fois, sinon il va affichier rien. 
exists = os.path.isfile('portMessage.txt')
if exists:
    f = open('portMessage.txt', 'r')
    portText.set(f.read())
    f.close()
port.pack()

#Affichier le nom de la liste déroulante
l9 = tk.Label(root, text="AdresseServeurImage", font=('Arial', 15))
l9.pack()  
imageText = tk.StringVar()
image = tk.Entry(root, textvariable = imageText)
#Verifier ecq useur a deja saisi l'adreese du serveur, si oui, il va afficher l'informaton que 
# useur a saisi le dernier fois, sinon il va affichier rien. 
exists = os.path.isfile('adresseMessage.txt')
if exists:
    f = open('adresseMessage.txt', 'r')
    imageText.set(f.read())
    f.close()
image.pack()


def on_click():
    #Obtenir l'information des variables
    openYear = int(openYearText.get())
    openMonth = int(openMonthText.get())
    openDay = int(openDayText.get())
    closeYear = int(closeYearText.get())
    closeMonth = int(closeMonthText.get())
    closeDay = int(closeDayText.get())
    port = int(portText.get())
    image = str(imageText.get())
    
    #Enregistrer le numero de la porte dans le fichier txt
    f = open('portMessage.txt', 'w')
    f.write(str(port))
    f.close()
    
    #Enregistrer l'adresse du serveur dans le fichier txt
    f = open('adresseMessage.txt', 'w')
    f.write(image)
    f.close()
    
    #verifier la validation de la date 
    if(not(2008<openYear<2200)):
        master = tk.Tk()
        msg = tk.Message(master, text = "openYear is invalide.")
        msg.pack()
        tk.mainloop()
    if(not(0<openMonth<13)):
        master = tk.Tk()
        msg = tk.Message(master, text = "openMonth is invalide.")
        msg.pack()
        tk.mainloop()
    if(not(0<openDay<32)):
        master = tk.Tk()
        msg = tk.Message(master, text = "openDay is invalide.")
        msg.pack()
        tk.mainloop()
    if(not(2008<closeYear<2200)):
        master = tk.Tk()
        msg = tk.Message(master, text = "closeYear is invalide.")
        msg.pack()
        tk.mainloop()
    if(not(0<closeMonth<13)):
        master = tk.Tk()
        msg = tk.Message(master, text = "closeMonth is invalide.")
        msg.pack()
        tk.mainloop()
    if(not(0<closeDay<32)):
        master = tk.Tk()
        msg = tk.Message(master, text = "closeDay is invalide.")
        msg.pack()
        tk.mainloop()
    
    # changer le type de string a int
    openDate = openYear*10000 + openMonth*100 + openDay
    closeDate = closeYear*10000 + closeMonth*100 + closeDay
    openDate = int(openDate)
    closeDate = int(closeDate)
    if(openDate > closeDate):
        master = tk.Tk()
        msg = tk.Message(master, text = "openDate is later than closeDate")
        msg.pack()
        tk.mainloop()
    
    #Etablir la communication entre l'interface et la base de donnee et chercher l'information dans le db 
    client=MongoClient('tcp.ngrok.io',port) 
    db = client['ps4_test_1_May']
    collection = db['Detection']
    print(openDate, closeDate)
    results = collection.find({'date':{'$gte':openDate, '$lte':closeDate}})
 

    #dessiner le text
    
    root = tk.Tk()
    S = tk.Scrollbar(root)
    text1 = tk.Text(root, height=20, width=20)
    S.pack(side=tk.RIGHT, fill=tk.Y)
    text1.pack(side=tk.LEFT, fill=tk.Y)
    S.config(command=text1.yview)
    text1.config(yscrollcommand=S.set)
    kml = simplekml.Kml()
    #Affichier le progressbar 
    popup = tk.Toplevel()
    tk.Label(popup, text="Datas being processing").grid(row=0, column=0)
    
    progress = 0
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=100)
    progress_bar.grid(row=1, column=0)
    popup.pack_slaves()
    progress_step = float(100.0/results.count())
    for result in results:
        popup.update()
        pnt = kml.newpoint(name=result["ImId"]+"_"+str(result["target_number"]), coords=[(result["lon"],result["lat"])])
        pnt.description = '<![CDATA['+ '<img src= "'+ image +'/'+result["ImId"]+'_'+ str(result["target_number"])+ '" />]]>'
        text1.insert(tk.END,str(result))
        text1.insert(tk.END,'\n')
        progress+=progress_step
        progress_var.set(progress)
    #tk.mainloop()
    kml.save('/home/zan/Desktop/battleplaces.kml')
    print("fini!!!!!!")
    #text1.insert(tk.END, "finiiiiiiiii!!!!!!!!!")
        
   

def searchAIS():
    webbrowser.open_new(url_2)
    

tk.Button(root, text="Search", command = on_click, activebackground = '#40E0D0', font=('Arial', 15)).pack()
tk.Button(root, text ="Search AIS", command =searchAIS, activebackground = '#40E0D0',font=('Arial', 15)).pack()
root.mainloop()


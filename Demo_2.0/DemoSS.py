import json, glob, os

frames = 11 #Frames totales que conforman la animación

#Secciones de la imagen
img1 = 400  #Sección izquierda
img2 = 826  #Sección central

#Distancias que determinan el color de los vehículos
dmin = 0
dmed = 10
dmax = 20

#Colores para los distintos niveles de importancia
Red = "#f00"    #Autos detectados entre dmin y dmed
Yellow = "#fb0" #Autos detectados entre dmed y dmax
Gray = "#555"   #Autos despues de dmax

#Datos de los autos
nCar = 1    #Número de auto detectado
carID = "car-"  #Nombre del objeto que lo representa
lCar = 4.4  #Longitud del auto
wCar = 1.8  #Ancho del auto
hCar = 1.7  #Altura del auto

#Valores de tiempo
ti = 1000   #Tiempo inicial
dt = 0.2    #Diferencial de tiempo
tf = ti + (frames - 1)*dt #Tiempo final

s = 2.3 #Distancia de separación lateral entre autos

#Transforma el nombre de los archivos a int para ordenarlos
def sortFunction(k):
    return int(os.path.basename(k)[:-4])

#Obtiene la lista de archivos .txt ordenados numericamente
def txtFiles():
    texts = glob.glob("*.txt")
    texts.sort(key = sortFunction)
    return texts

#Adquiere y transforma los datos de los archivos .txt
def txtRead(name):
    carList = []    #Lista que almacena los datos de los autos encontrados
    txt = open(name, "r")
    data = txt.readlines()
    txt.close()
    data = [i.rstrip("\n") for i in data]
    for line in data:
        carList.append(dSideTrack(line))    #Agrega los datos del vehículo a la lista
    return carList    

#Función que obtiene la distancia y en que carril se encuentra el vehículo
def dSideTrack(line):
    line = line.split("_")
    d = int(line[-1])
    p1x = int(line[1].split(",")[0])
    p2x = int(line[2].split(",")[0])
    c = (p1x + p2x)/2   #Se calcula la posición del centro del vehículo
    #Se compara la posición calculada para ubicar el auto 
    #en el carril correspondiente
    if c <= img1:
        side = "left"
    elif c > img1 and c <= img2:
        side = "center"
    elif c > img2:
        side = "right"
    return d, side

#Función que genera el frame vacío
def Frame(i):
    frame = json.load(open("state_update.json"))    #Obtiene la estructura base de un frame
    track = json.load(open("line.json"))    #Obtiene la estructura base de un carril central
    lineR = json.load(open("lineR.json"))   #Obtiene la estructura base de una linea a la derecha
    lineL = json.load(open("lineL.json"))   #Obtiene la estructura base de una linea a la izquierda
    frame["data"]["updates"][0]["timestamp"] = ti + i*dt    #Actualiza el instante de tiempo del frame
    frame["data"]["updates"][0]["poses"]["/vehicle_pose"]["timestamp"] = ti + i*dt
    #Se agrega el carril y las líneas divisoras al frame
    frame["data"]["updates"][0]["primitives"]["/prediction/trajectory"]["polylines"].append(track)
    frame["data"]["updates"][0]["primitives"]["/prediction/trajectory"]["polylines"].append(lineR)
    frame["data"]["updates"][0]["primitives"]["/prediction/trajectory"]["polylines"].append(lineL)
    return frame

# Función que genera los prismas de los vehículos detectados y sus respectivas etiquetas
def Car(d, frame, side):
    global nCar
    car = json.load(open("prisma.json"))    #Obtiene la estructura base de un vehículo
    label = json.load(open("text.json"))    #Obtiene la estructura base de un label
    #Se indica la posición del vehículo con los datos obtenidos en el archivo txt
    if side == "left":
        car["vertices"] = [[d, s + wCar, 0], [d, s, 0], [d + lCar, s, 0], [d + lCar, s + wCar, 0]]
        label["position"] = [d, s + wCar, hCar]
    elif side == "right":
        car["vertices"] = [[d, -s, 0], [d, -s - wCar, 0], [d + lCar, -s - wCar, 0], [d + lCar, -s, 0]]
        label["position"] = [d, -s, hCar]
    #Se indica el color del vehículo en función de su distancia
    if d >= dmax:
        car["base"]["style"]["fill_color"] = Gray   #Autos lejanos
    elif d < dmax and d >= dmed:
        car["base"]["style"]["fill_color"] = Yellow     #Autos a distancia media
    elif d < dmed and d >= dmin:
        car["base"]["style"]["fill_color"] = Red    #Autos cercanos
    car["base"]["object_id"] = carID + str(nCar)    #Se establece el ID del vehículo
    label["text"] = carID + str(nCar) + ": " + str(d) + " m"    #Se establece un label con ID y distancia
    #Se agregan ambos objetos al frame
    frame["data"]["updates"][0]["primitives"]["/object/shape"]["polygons"].append(car)
    frame["data"]["updates"][0]["primitives"]["/object/label"]["texts"].append(label)
    nCar += 1
    return frame

#Función que genera el archivo .json del frame con el número correspondiente
def WriteJSON(frame, nFrame):
    with open(str(nFrame) + '-frame.json', 'w') as file:
        json.dump(frame, file)

#Función que genera el 0-frame (data index) de la simulación
def WriteIndex():
    dIndex = json.load(open("dataIndex.json"))  #Obtiene la estructura base del data index
    dIndex["startTime"] = ti    #Actualiza tiempo inicial
    dIndex["endTime"] = tf  #Actualiza tiempo final
    for x in range(frames):
        dIndex["timing"].append([ti + x*dt, ti + x*dt, x, str(x + 2) + "-frame"])   #Genera la lista "timing"
    with open('0-frame.json', 'w') as file:
        json.dump(dIndex, file)

#Función que genera el 1-frame (Metadata) de la simulación
def WriteMetadata():
    mdata = json.load(open("meta_data.json"))   #Obtiene la estructura base del metadata
    mdata["data"]["log_info"]["start_time"] = ti
    mdata["data"]["log_info"]["end_time"] = tf
    with open('1-frame.json', 'w') as file:
        json.dump(mdata, file)

def main():
    i = 0
    global nCar
    texts = txtFiles()
    for text in texts:  #Por cada archivo .txt
        carList = txtRead(text)
        frame = Frame(i)
        for car in carList: #Por cada vehículo
            frame = Car(car[0], frame, car[1])
        nCar = 1
        WriteJSON(frame, i + 2)
        i += 1
    WriteIndex()
    WriteMetadata()    

if __name__== "__main__":
    main()

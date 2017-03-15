import gpxpy
import gpxpy.gpx
import datetime
import iso8601
from math import radians, cos, sin, asin, sqrt
import numpy as np
import matplotlib.pyplot as plt
import datetime


#####################################################################
## Calcula la distancia entre dos puntos
#####################################################################
def distancia(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km*1000


#####################################################################
## Lee un fichero GPX
#####################################################################
def getTrack(fichero):

    gpx_file = open(fichero, 'r')
    gpx = gpxpy.parse(gpx_file)

    d_total = 0
    t_total = 0
    ritmos = []
    tramos = []

    for track in gpx.tracks:
        for segment in track.segments:
            for i in range(1,len(segment.points)):

                p1 = segment.points[i-1]
                p2 = segment.points[i]

                d = distancia(p1.longitude, p1.latitude, p2.longitude, p2.latitude)
                t = (p2.time - p1.time).seconds

                d_total = d_total + d
                t_total = t_total + t
                try:
                    ritmo = ((t) / (d))*(1000/60)
                except:
                    ritmo = 0
                ritmos.append(ritmo)

                tramo = {}
                tramo['DISTANCIA'] = d
                tramo['RITMO'] = ritmo
                tramos.append(tramo)


    return tramos, d_total, np.mean(ritmos), gpx.time


#####################################################################
## Calcula el histograma
#####################################################################
def getHistograma(tramos, zonas):


    histograma = {}

    for k in zonas.keys():

        r1 = float(str(zonas[k][0]).split(":")[0]) + float(str(zonas[k][0]).split(":")[1])/60
        r2 = float(str(zonas[k][1]).split(":")[0]) + float(str(zonas[k][1]).split(":")[1])/60

        ts = filter(lambda reg: reg['RITMO'] >= r1 and reg['RITMO'] < r2, tramos)
        dst = 0
        for t in ts:
            dst = dst + t['DISTANCIA']
        histograma[k] = dst/1000

    return histograma


#####################################################################
## Programa principal
#####################################################################
import zipfile
archive = zipfile.ZipFile('activities.zip', 'r')

zonas = {}
zonas['Z1'] = ['05:30','10:00']
zonas['Z2'] = ['04:50','05:30']
zonas['Z3'] = ['04:30','04:50']
zonas['Z4'] = ['04:10','04:30']
zonas['Z5'] = ['03:30','04:10']
zonas['Z6'] = ['03:00','03:30']


for f in archive.namelist():

    outpath = ".\\temp\\"
    archive.extract(f, outpath)
    track,  d_total, r_medio, fecha = getTrack(outpath + f)
    os.remove(outpath + f)

    if fecha.year == 2017:

        histograma = getHistograma(track, zonas)

        histograma['FECHA'] = fecha
        histograma['ANIO'] = fecha.year
        histograma['SEMANA'] = fecha.isocalendar()[1]

        cadena = str(histograma['FECHA']) + "," + str(histograma['ANIO']) + "," + str(histograma['SEMANA']) + "," + str(round(histograma['Z1'],2)) + "," + str(round(histograma['Z2'],2)) + "," + str(round(histograma['Z3'],2)) + "," + str(round(histograma['Z4'],2)) + "," + str(round(histograma['Z5'],2)) + "," + str(round(histograma['Z6'],2))

        print cadena




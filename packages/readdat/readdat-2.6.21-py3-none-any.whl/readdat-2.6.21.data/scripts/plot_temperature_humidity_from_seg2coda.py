#!python
"""
read temperature and humidity data
group the curves by channel (assumes that CHXX is in the filename)
plot them in UTC time
"""
import sys, glob, os
import numpy as np
import matplotlib.pyplot as plt
from readdat import read
from tempoo.timetick import timetick


def extract_temperature_humidity_from_seg2_coda(file_list: list) -> dict:
    """
    extrait les champs timestamp(temps local) / temperature / humidite
    des header seg2 
    renvoie un dictionnaire de la forme {"CHXX" : {"timestamp": [...], "temperature": [...], "humidity": [...]}} 
    """
    # prepare le stockage des donnees de temperature, humidite, temps dans un dict
    data = {
        "CH%02d" % i: \
            {"timestamp": [], 
             "temperature": [], 
             "humidity": []} 
        for i in range(24)}

    for f in file_list:
        print(f)
        assert os.path.isfile(f), IOError(f)
        # extrait le nom du channel dans le nom de fichier
        channel_name = "CH%02d" % int(f.split('CH')[-1].split('.')[0])

        # lit la donnees en tant que CODA, temps local
        stream = read(f, format="SEG2", acquisition_system="CODA")#, timezone="Europe/Paris")

        # extraction trace a trace
        for trace in stream:        
            timestamp = trace.stats.starttime.timestamp
            temperature = trace.stats.temperature_degc
            humidity = trace.stats.relative_humidity_percent

            # stockage
            data[channel_name]['timestamp'].append(timestamp)
            data[channel_name]['temperature'].append(temperature)
            data[channel_name]['humidity'].append(humidity)

    return data


def show_temperature_humidity_data(data: dict):
    """
    affichage courbes temperature humidite pour chaque channel
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(211, ylabel=r" Temperature $(^{\circ}C)$ ")
    ax2 = fig.add_subplot(212, ylabel=r" Relative Humidity (%) ", sharex=ax1)

    # boucle sur les voies
    for channel_name, curves in data.items():

        # conversion numpy array, tri temps 
        i = np.argsort(curves['timestamp'])
        if not len(i):
            continue

        timestamp = np.asarray(curves['timestamp'], float)[i]
        temperature = np.asarray(curves['temperature'], float)[i]
        humidity = np.asarray(curves['humidity'], float)[i]
        hdl, = ax1.plot(timestamp, temperature, label=channel_name)
        ax2.plot(timestamp, humidity, label=channel_name, color=hdl.get_color())
    ax1.legend(ncol=5)
    # ax2.legend(ncol=3)
    timetick(ax2, "x")

    plt.show()


if __name__ == "__main__":
    help_message = f"""
    usage :
        python {os.path.basename(__file__)} file1.sg2 [file2.sg2 [file3.sg2 ...]]
    """
    # liste tous les fichiers seg2 (argv)
    ls = sys.argv[1:]
    if not len(ls) or "-h" in ls or "help" in ls:
        print(help_message)
        sys.exit(1)
   
    data = extract_temperature_humidity_from_seg2_coda(ls)
    show_temperature_humidity_data(data)


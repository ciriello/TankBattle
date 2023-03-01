"""
Bestandsnaam  : vcdecorators.py
Module        : vcdecorators
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import time

LOGFILE = 'perf_monitoring.log'

def monitorPerformance(func):
    """
    Deze Decorator Functie kan worden gebruikt om methodes in de programmatuur
    te decoreren met een TIMER functie. Dat wil zeggen. Dat de methodes
    die deze decorator krijgen printen de uitvoertijd van de methode naar het
    scherm. Dit kan gebruikt worden voor PERFORMANCE monitoring i.d.

    :param func:
    :return:
    """
    def func_wrapper(*arg):
        start = 'Start {0}: {1}'.format(func, time.ctime())
        print(start)
        f = func(*arg)
        end = 'End {0}: {1}'.format(func, time.ctime())
        print(end)
        try:
            file = open(LOGFILE, 'a')
            file.write(start)
            file.write('\n')
            file.write(end)
            file.write('\n')
        except IOError:
            print('Error: kan niet schrijven naar {0}'.format(LOGFILE))
        finally:
            file.close()

        return f

    return func_wrapper

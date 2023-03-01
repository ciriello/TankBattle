"""
Bestandsnaam  : vcutils.py
Module        : vcutils
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""
import json
import os.path as path
from vcmodel import JSONDecodable
from vcexceptions import ConfigFileException

FNOTFOUND = 2

def parseConfig(fileName, ConfigClazz):
    """
    Deze functie leest het configuratie bestand in, welke is meegegeven als param fileName
    en valideert of het bestand een JSON bestand is.

    Vervolgens zal deze functie een instantie van de Klasse aanmaken welke als
    type is meegegeven aan de functie (ConfigClazz). Deze Klasse wordt dus run-time
    geinitieerd en gevalideerd of het van het type JSONDecodable is (de superklasse)

    Als deze run-time geinitieerde klasse een JSONDecodable is kan de klasse zichzelf
    instantieren met de JSON data.

    Het resultaat is een Configuratie Klasse met de properties van deze klasse gevuld
    aan de hand van het JSON bestand.

    Het voordeel hiervan is, dat elke JSON bestand met bijbehorende JSONDecodable sub-klasse
    op deze manier door deze functie geinstantieerd kan worden.

    :param fileName:
    :param ConfigClazz:
    :return: instance of type 'ConfigClazz' populated with the 'fileName' JSON data
    """
    try:
        with open(fileName, 'r') as f:
            config = json.load(f)
            parsedConfig = ConfigClazz()
            if isinstance(parsedConfig, JSONDecodable):
                return parsedConfig.decode(config)
            else:
                raise ConfigFileException('{0} ondersteund geen JSONDecodable.'.format(ConfigClazz))

    except IOError as e:
        currentPath = path.abspath(fileName)
        msg = 'Fout bij het laden van het configuratiebestand "{0}".'.format(currentPath)
        if e.errno == FNOTFOUND:
            msg += ' Bestand niet gevonden.'.format(fileName)
        raise ConfigFileException(msg)

    except json.decoder.JSONDecodeError:
        currentPath = path.abspath(fileName)
        msg = 'Fout bij het laden van de JSON gegevens uit configuratiebestand {0}. Bestand bevat geen of foutieve JSON data'.format(currentPath)
        raise ConfigFileException(msg)

    except Exception as e:
        raise ConfigFileException(e)



"""
Bestandsnaam  : vcexceptions.py
Module        : vcexceptions
Student       : V. Ciriello
Studentnummer : 800008924
Leerlijn      : Python
Datum:        : september 2018
"""

"""Custom Exception voor het inlezen van configuratie bestanden"""
class ConfigFileException(Exception): pass

"""Custom Exception voor het instantieren van een klasse aan de hand van JSON data"""
class JSONDecodableException(Exception): pass

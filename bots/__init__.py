import re

def get_player1():
    config_file = open('/Users/bbarr/Code/breve/hacdc/ctf/config', 'r')
    player1 = re.search('(?<=player1\s)[\w\*]+', config_file.read())
    config_file.close()
    if player1 != '*': 
        m = __import__('bots.'+player1.group(0))
        m = getattr(m, player1.group(0))
        m = getattr(m, player1.group(0))
        return m
    else:
       return get_random_class()

def get_player2():
    config_file = open('/Users/bbarr/Code/breve/hacdc/ctf/config', 'r')
    player2 = re.search('(?<=player2\s)[\w\*]+', config_file.read())
    config_file.close()
    if player2 != '*': 
        m = __import__('bots.'+player2.group(0))
        m = getattr(m, player2.group(0))
        m = getattr(m, player2.group(0))
        return m
    else:
        return get_random_class()

def get_random_class():
    pass

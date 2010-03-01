import re

def roundRobin(bots=None, sets=None):
    """ Generates a schedule of "fair" pairings. finds local bots by default, with list of bots an option """

    # I don't understand how to load all local classes
#    if not bots:
#        bots = import *

    if len(bots) % 2:
        bots.append(None)
    count    = len(bots)
    sets     = sets or (count - 1)
    half     = count / 2
    schedule = []
    for turn in range(sets):
        pairings = []
        for i in range(half):
            pairings.append((bots[i], bots[count-i-1]))
        bots.insert(1, bots.pop())
        schedule.append(pairings)
    return schedule


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


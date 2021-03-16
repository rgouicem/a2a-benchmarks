#!/usr/bin/env python3

class Config():

    store = {}

    def __init__(self, path):
        with open(path, 'r') as fp:
            lino = 1
            for l in fp:
                if l.startswith("#") or l.isspace():
                    continue
                try:
                    [key, val] = l.split('=')
                except:
                    print("[ERROR] Configuration file is not correctly formed at "+path+":"+str(lino))
                    exit(1)
                self.store[key] = val.strip()
                lino += 1

    def __str__(self):
        return self.store.__str__()

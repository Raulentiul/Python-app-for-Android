class Player:
    def __init__(self, name, health):
        self.name=name
        self.level=1
        self.health=health

    def find_strongest(l):
        strongest = l[0]
        for p in l:
            if p.level>strongest.level:
                strongest=p
        return p
    def compare(p1, p2):
        if p1.level > p2.level:
            return 1
        if p1.level < p2.level:
            return -1
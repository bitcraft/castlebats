from . import euclid, vec, bbox


class Body2(object):
    def __init__(self, thisbbox, acc, vel, o):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = vec.Vec2(acc)
        self.vel = vec.Vec2(vel)
        self.o = o


class Body3(object):
    def __init__(self, thisbbox, acc, vel, o):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = euclid.Vector3(*acc)
        self.vel = euclid.Vector3(*vel)
        self.o = o


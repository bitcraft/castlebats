from . import euclid, bbox


class Body2:
    def __init__(self, thisbbox, acc, vel, gravity=True):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = euclid.Vector2(*acc)
        self.vel = euclid.Vector2(*vel)
        self.gravity = gravity
        self.physicsgroup = None


class Body3:
    def __init__(self, thisbbox, acc, vel, gravity=True):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = euclid.Vector3(*acc)
        self.vel = euclid.Vector3(*vel)
        self.gravity = gravity
        self.physicsgroup = None

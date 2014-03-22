from . import euclid, vec, bbox


class Body2:
    def __init__(self, thisbbox, acc, vel, gravity=True):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = vec.Vec2(acc)
        self.vel = vec.Vec2(vel)
        self.gravity = gravity
        self.physicsgroup = None


class Body3:
    def __init__(self, thisbbox, acc, vel, gravity=True):
        self.bbox = bbox.BBox(thisbbox)
        self.acc = euclid.Vector3(*acc)
        self.vel = euclid.Vector3(*vel)
        self.gravity = gravity
        self.physicsgroup = None

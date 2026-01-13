# Not used yet

class MBIONetworkNode():
    def __init__(self, parent, name, data=None):
        self._parent=parent
        self._name=name.lower()
        self._children={}
        self._data=data
        self.onInit()

    def onInit(self):
        pass

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    def isRoot(self):
        if not self.parent:
            return True

    @property
    def children(self):
        return self._children.values()

    @property
    def data(self):
        return self._data

    def count(self):
        return len(self._children)

    def child(self, name):
        try:
            return self._children.get(name.lower())
        except:
            pass
        return None

    def childFactory(self, name) -> MBIONetworkNode:
        return None

    def addChild(self, name, data=None):
        try:
            name=name.lower()
            child=self.child(name):
            if not child:
                child=self.childFactory(name, data)
                if child:
                    self._children[name]=child
            return child
        except:
            pass

    def __repr__(self):
        t='children'
        if self._children:
            t=type(self._children[0])
        return '%s(%d %s)' % self.__class__.__name, self.count(), t)


# MBIONetworkTopylogy
# +----MBIONetworkNodeSwitch
#      +----MBIONetworkNodeGateway
#           +----MBIONetworkNodeDevice

class MBIONetworkTopology(MBIONetworkNode):
    def childFactory(self, name):
        return MBIONetworkNodeSwitch(self, name)

    def onInit(self):
        self.addChild('mbio')

    def switch(self, name):
        return self.child(name)

    @property
    def switches(self):
        return self.children

    def addSwitch(self, name) -> MBIONetworkNodeSwitch:
        return self.addChild(name)


class MBIONetworkNodeSwitch(MBIONetworkNode):
    def childFactory(self, name, data: MBIOGateway):
        return MBIONetworkNodeGateway(self, name, data)

    @property
    def data(self) -> MBIOGateway:
        return self._data

    def gateway(self, name):
        return self.child(name)

    @property
    def gateways(self):
        return self.children

    def isOnline(self):
        for child in self.gateways():
            data=child.data
            if data.isOnline():
                return True
        return False

    def connectTo(self, name):
        pass




class MBIONetworkNodeGateway(MBIONetworkNode):
    def childFactory(self, name, data: MBIODevice):
        return MBIONetworkNodeDevice(self, name, data)

    @property
    def data(self) -> MBIODevice:
        return self._data

    def device(self, name):
        return self.child(name)

    @property
    def devices(self):
        return self.children

    def connectToSwitch(self, name):
        switch=self.



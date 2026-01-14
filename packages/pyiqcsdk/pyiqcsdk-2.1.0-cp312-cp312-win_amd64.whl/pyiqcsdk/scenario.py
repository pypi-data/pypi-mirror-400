class Scenario(object):
    """
    Scenario base class.
    """
    def __init__(self, xca):
        self._whatToDo = {}
        self._client = xca
        self._ntwMgr = xca.networks
        self._profileMgr = xca.profiles
        self._apMgr = xca.aps
        self._rfMg = xca.rfmgmtprofiles
        self._siteMgr = xca.sites
        
    def set(self, input):
        """"
            'actionText' : 
                    [{'func': f, 'params': {'p1':v1}} for x in range(10)]}
        """
        self._whatToDo = input
        return self
    
    def run(self):
        for s in self._whatToDo:
            act = list(s.keys())[0]
            params = list(s.values())[0]
            if act.startswith("#") == False:
                print ('{a} total {t}'.format(a=s.keys(), t=len(params)))
                for n in list(s.values())[0]:
                    ret = n['func'](**n['params'])
                    if ret.__class__.__name__ == 'Response':
                        code = ret.status_code
                        #print(code)
                        assert (code in [200, 201, 422, 500])

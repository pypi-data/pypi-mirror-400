#----------------------------------------------
# EASING CLASSES
#----------------------------------------------
class Easing:
    def __init__(self,func):
        self.func = func

    def ease(self,x):
        return self.func(x)

class easeInOutQuart(Easing):
    def __init__(self):
        super().__init__(lambda x:8*x**4 if x < 0.5 else 1 - (-2*x + 2)**4 / 2)

class easeLinear(Easing):
    def __init__(self):
        super().__init__(lambda x:x)
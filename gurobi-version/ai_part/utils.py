
penalties = [] # store dispatcher and trader penalties
c_values = [] #To store cumulative sum of nomination flow difference


class dotdict(dict):
    def __getattr__(self, name):
        return self[name]

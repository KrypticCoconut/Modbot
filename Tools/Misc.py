import inspect

class FuncUtils:
    @classmethod
    def get_kwargs(cls, Frame) -> dict:  # whats the class type for frame lol
        if not Frame:
            frame = inspect.currentframe().f_back
        else:
            frame = Frame

        keys, _, _, values = inspect.getargvalues(frame)
        kwargs = {}
        for key in keys:
            if key != 'self':
                kwargs[key] = values[key]
        return kwargs

    @classmethod
    def checkargs(cls, argstocheck: list) -> str:
        if(argstocheck == []):
            return None
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe)[1][0]

        vars = FuncUtils.get_kwargs(calframe)

        for varname, varval in vars.items():
            if varval is None and varname in argstocheck:
                return str("{} value cannot be 'None'".format(varname))
        return None

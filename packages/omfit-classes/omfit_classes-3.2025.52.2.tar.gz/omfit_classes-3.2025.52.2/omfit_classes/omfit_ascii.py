try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise


from omfit_classes.omfit_path import OMFITpath

__all__ = ['OMFITascii', 'OMFITexecutionDiagram']


class OMFITascii(OMFITpath):
    r"""
    OMFIT class used to interface with ASCII files

    :param filename: filename passed to OMFITobject class

    :param fromString: string that is written to file

    :param \**kw: keyword dictionary passed to OMFITobject class
    """

    def __init__(self, filename, **kw):
        fromString = kw.pop('fromString', None)
        OMFITpath.__init__(self, filename, **kw)
        if fromString is not None:
            with open(self.filename, 'wb') as f:
                if isinstance(fromString, bytes):
                    f.write(fromString)
                else:
                    f.write(fromString.encode('utf-8'))

    def read(self):
        '''
        Read ASCII file and return content

        :return:  string with content of file
        '''
        with open(self.filename, 'r') as f:
            return f.read()

    def write(self, value):
        '''
        Write string value to ASCII file

        :param value: string to be written to file

        :return: string with content of file
        '''
        with open(self.filename, 'w') as f:
            f.write(value)
        return value

    def append(self, value):
        '''
        Append string value to ASCII file

        :param value: string to be written to file

        :return: string with content of file
        '''
        with open(self.filename, 'a') as f:
            f.write(value)
        return self.read()


class OMFITexecutionDiagram(OMFITascii, SortedDict):
    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        l = self.read().splitlines()
        stack = []
        for li in range(len(l)):
            if not l[li].startswith('*'):
                continue
            na = l[li].count('*')
            if len(stack) >= na:
                stack = stack[: na - 1]

            size = l[li].split()[-1].strip('[]')
            size = size.replace('GB', 'e9')
            size = size.replace('MB', 'e6')
            size = size.replace('kB', 'e3')
            size = size.replace('bytes', '')
            size = size.replace('N/A', '0')
            size = float(size)
            time = float(l[li].split()[-2][:-1])
            name = l[li].split()[-3].strip('[]')
            ptr = self
            for k in stack:
                ptr = ptr[k]
            if name in ptr:
                for ii in range(1, 10):
                    if f'{name}_{ii}' not in ptr:
                        name = f'{name}_{ii}'
                        break
            ptr[name] = SortedDict()
            ptr[name].size = size
            ptr[name].time = time
            stack.append(name)

        self.dynaLoad = False

    @dynaLoad
    def print_sorted(self, by='time'):
        paths = []
        vals = []

        def traverse(r, p):
            if len(p):
                paths.append(p)
                vals.append(getattr(r, by))

            for k, v in r.items():
                traverse(v, p + [k])

        traverse(self, [])
        pprint(sorted(list(zip(paths, vals)), key=lambda x: x[1])[-10:])

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

from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.sortedDict import SortedDict

__all__ = ['OMFITexecutionDiagram']


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
    def print_sorted(self, by='time', nitems=10):
        paths = []
        vals = []

        def traverse(r, p):
            if len(p):
                paths.append(p)
                vals.append(getattr(r, by))

            for k, v in r.items():
                traverse(v, p + [k])

        traverse(self, [])
        pprint(sorted(list(zip(paths, vals)), key=lambda x: x[1])[-nitems:])


if __name__ == '__main__':
    timings = OMFITexecutionDiagram(OMFITsrc + '/../samples/cake_timings_CORI_10_interactive.txt')
    timings.print_sorted(nitems=20)

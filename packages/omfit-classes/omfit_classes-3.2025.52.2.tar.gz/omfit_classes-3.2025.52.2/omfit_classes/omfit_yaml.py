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

import yaml

__all__ = ['OMFITyaml']


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=SortedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return yaml.load(stream, OrderedLoader)


def convert_to_ordered_dict(data):
    if isinstance(data, SortedDict):
        # Convert SortedDict to an OrderedDict, recursively handle nested SortedDict
        return OrderedDict((k, convert_to_ordered_dict(v)) for k, v in data.items())
    elif isinstance(data, list):
        # Also convert elements in lists, if necessary
        return [convert_to_ordered_dict(element) for element in data]
    else:
        return data


def ordered_dict_representer(dumper, data):
    # Treat OrderedDict like a regular dict for YAML representation
    return dumper.represent_dict(data.items())


# Register the custom representer for OrderedDict
yaml.add_representer(OrderedDict, ordered_dict_representer)


class OMFITyaml(SortedDict, OMFITascii):
    """
    OMFIT class to read/write yaml files
    """

    def __init__(self, filename, **kw):
        r"""
        OMFIT class to parse yaml files

        :param filename: filename of the yaml file

        :param \**kw: arguments passed to __init__ of OMFITascii
        """
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            data = ordered_load(f, yaml.SafeLoader)
        if data is None:
            pass
        elif isinstance(data, list):
            self["-"] = data
        else:
            self.update(data)

    @dynaSave
    def save(self):
        data = convert_to_ordered_dict(self)
        with open(self.filename, 'w', encoding='utf-8') as f:
            if "-" in data:
                yaml.dump(data["-"], f, allow_unicode=True)
            else:
                yaml.dump(data, f, allow_unicode=True)


############################################
if '__main__' == __name__:
    test_classes_main_header()

    tmp = OMFITyaml(OMFITsrc + '/../samples/sample.yaml')
    tmp.load()

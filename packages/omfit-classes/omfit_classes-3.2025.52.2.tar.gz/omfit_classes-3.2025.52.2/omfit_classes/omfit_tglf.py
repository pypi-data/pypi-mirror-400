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

import numpy as np
from omfit_classes.omfit_path import OMFITpath
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.sortedDict import OMFITdataset
from omfit_classes.omfit_dir import OMFITdir
from omfit_classes.omfit_gacode import OMFITgacode
from omfit_classes.omfit_asciitable import OMFITasciitable

__all__ = [
    'OMFITtglfEPinput',
    'OMFITalphaInput',
    'OMFITtglf_eig_spectrum',
    'OMFITtglf_wavefunction',
    'OMFITtglf_flux_spectrum',
    'OMFITtglf_nete_crossphase_spectrum',
    'OMFITtglf_potential_spectrum',
    'OMFITtglf_fluct_spectrum',
    'OMFITtglf_intensity_spectrum',
    'OMFITtglf',
    'OMFITtglf_nsts_crossphase_spectrum',
    'sum_ky_spectrum',
]


class OMFITtglfEPinput(OMFITascii, SortedDict):
    '''
    Class used to read/write TGLFEP input files
    '''

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read()

        widths = []
        for line in lines.split('\n'):
            if not len(line.strip()):
                continue
            try:
                if len(widths):
                    self['WIDTHS'] = widths
                value, key = line.split()
            except ValueError:  # not enough values to unpack
                widths.append(eval(line))
            else:
                if value == '.false.':
                    value = False
                elif value == '.true.':
                    value = True
                else:
                    value = eval(value)
                self[key] = value

    @dynaSave
    def save(self):
        txt = []
        for key, value in self.items():
            if key == 'WIDTHS':
                continue
            if value is False:
                value = '.false.'
            elif value is True:
                value = '.true.'
            txt.append(f'{value} {key}')
            if key == 'WIDTH_IN_FLAG' and 'WIDTHS' in self:
                txt.append('\n'.join(map(str, self['WIDTHS'])))
        with open(self.filename, 'w') as f:
            f.write('\n'.join(txt))


class OMFITalphaInput(OMFITascii, SortedDict):
    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.read().strip().split('\n')
        comment = lines[0]
        data = np.array(list(map(eval, lines[1:])))
        self['comment'] = comment
        self['data'] = data


def get_ky_spectrum(filename):
    with open(filename, 'r') as f:
        content = f.readlines()
    content = ''.join(content[2:]).split()
    ky = np.array(content, dtype=float)
    return ky


class OMFITtglf_QL_flux_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.QL_flux_spectrum file

    :param filename: Path to the out.tglf.QL_flux_spectrum file

    '''

    def __init__(self, filename, ky_file, field_labels, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.field_labels = self.OMFITproperties['field_labels'] = field_labels
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels
        self.n_species = len(spec_labels)
        self.n_fields = len(field_labels)

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        ntype, nspecies, nfield, nky, nmodes = list(map(int, lines[3].strip().split()))
        with open(self.filename) as f:
            content = f.read()
        tmpdict = SortedDict()
        ky = get_ky_spectrum(self.ky_file)
        ql = []
        for line in lines[6:]:
            line = line.strip().split()
            if any([x.startswith(("s", "m")) for x in line]):
                continue
            for x in line:
                ql.append(float(x))
        QLw = array(ql).reshape(nspecies, nfield, nmodes, nky, ntype)
        types = ['particle', 'energy', 'toroidal stress', 'parallel stress', 'exchange']
        self.labels = types  # used in plot.

        for i, t in enumerate(types):
            QL_data_array = DataArray(
                data=QLw[:, :, :, :, i],
                dims=["species", 'field', 'mode_num', 'ky'],
                coords={
                    "species": self.spec_labels,
                    "field": self.field_labels,
                    "mode_num": np.arange(nmodes) + 1,
                    "ky": ky,
                },
            )
            self.update({t: QL_data_array})

    def plot(self, fn=None):
        '''
        Plot the QL (flux) weights spectra

        :param fn: A FigureNotebook instance
        '''
        ns = self.n_species
        species = self.spec_labels
        nf = self.n_fields
        fields = self.field_labels
        if fn is None:
            from omfit_plot import FigureNotebook

            tabbed = FigureNotebook(nfig=0, name='TGLF QL (flux) weight spectra')
        else:
            tabbed = fn
        for k in self.labels:
            fig = tabbed.add_figure(label=k)
            fig.suptitle(k)
            for s in range(ns):
                for f in range(nf):
                    if s == 0 and f == 0:
                        ax0 = ax = axr = fig.use_subplot(ns, nf, s * nf + f + 1)
                    elif f == 0:
                        ax = axr = fig.use_subplot(ns, nf, s * nf + f + 1, sharex=ax0)
                    else:
                        ax = fig.use_subplot(ns, nf, s * nf + f + 1, sharex=ax0, sharey=axr)
                    if f == 0:
                        ax.set_ylabel('Species: %s' % (self.spec_labels[s]))
                    if s == 0:
                        ax.set_title([r'$\phi$', r'$B_{\perp}$', r'$B_{\parallel}$'][f])
                    # The actual data,
                    ax.plot(self['ky'], self[k].sel(species=species[s], field=fields[f], mode_num=1).data)
                    ax.set_xscale('log')
                    ax.axis('tight')
            autofmt_sharexy(fig=fig)
            fig.canvas.draw()


class OMFITtglf_QL_intensity_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.QL_intensity_spectrum file

    :param filename: Path to the out.tglf.QL_flux_spectrum file

    '''

    def __init__(self, filename, ky_file, n_species, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.n_species = self.OMFITproperties['n_species'] = n_species
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        ntype, nspecies, nky, nmodes = list(map(int, lines[4].strip().split()))
        with open(self.filename) as f:
            content = f.read()
        tmpdict = SortedDict()
        ky = get_ky_spectrum(self.ky_file)
        ql = []
        for line in lines[7:]:
            line = line.strip().split()
            if any([x.startswith(("s", "m")) for x in line]):
                continue
            for x in line:
                ql.append(float(x))
        QLw = array(ql).reshape(nspecies, nmodes, nky, ntype)
        types = ['density', 'temperature', 'U', 'Q']
        for i, t in enumerate(types):
            QL_data_array = DataArray(
                data=QLw[:, :, :, i],
                dims=["species", 'mode_num', 'ky'],
                coords={
                    "species": self.spec_labels,
                    "mode_num": np.arange(nmodes) + 1,
                    "ky": ky,
                },
            )
            self.update({t: QL_data_array})


class OMFITtglf_eig_spectrum(OMFITdataset, OMFITascii):
    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes

    @dynaLoad
    def load(self):
        nmodes = self.nmodes
        with open(self.filename, 'r') as f:
            content = f.readlines()
        content = ''.join(content[2:]).split()
        ky = get_ky_spectrum(self.ky_file)
        gamma = []
        freq = []
        for k in range(self.nmodes):
            gamma.append(np.array(content[2 * k :: nmodes * 2], dtype=float))
            freq.append(np.array(content[2 * k + 1 :: nmodes * 2], dtype=float))
        gamma = np.array(gamma)
        freq = np.array(freq)
        gamma = DataArray(gamma, dims=('mode_num', 'ky'), coords={'ky': ky, 'mode_num': np.arange(nmodes) + 1})
        freq = DataArray(freq, dims=('mode_num', 'ky'), coords={'ky': ky, 'mode_num': np.arange(nmodes) + 1})
        self.update({'gamma': gamma, 'freq': freq})

    def plot(self, axs=None):
        '''
        Plot the eigenvalue spectrum as growth rate and frequency

        :param axs: A length 2 sequence of matplotlib axes (growth rate, frequency)
        '''
        if axs is None:
            fig, axs = pyplot.subplots(2, 1, num=pyplot.gcf().number, squeeze=True, sharex=True)
        else:
            fig = axs[0].get_figure()
        for k in range(self.nmodes):
            axs[0].plot(self['ky'], self['gamma(%d)' % (k + 1)], label='Growth rate $\\gamma_{%d}$' % (k + 1))
            axs[1].plot(self['ky'], self['freq(%d)' % (k + 1)], label='Frequency $\\omega_{%d}$' % (k + 1))
        axs[0].set_ylabel('Growth rate $\\gamma$')
        with warnings.catch_warnings():
            # We don't care if matplotlib has an underflow while drawing
            warnings.filterwarnings('ignore', category=RuntimeWarning, message='underflow*')
            axs[0].set_yscale('symlog', linthresh=0.01)
            axs[1].set_yscale('symlog', linthresh=0.01)
            axs[1].set_ylabel('Frequency $\\omega$')
            axs[1].axhline(0, color='gray', ls='--')
            axs[1].set_xlabel('$k_\\perp \\rho$')
            axs[0].set_xscale('log')
            fig.canvas.draw()

    @dynaLoad
    def __getitem__(self, key):

        if key in self:
            return OMFITdataset.__getitem__(self, key)

        if key.startswith('gamma') and '(' in key:
            ind = int(key.split('(')[1].split(')')[0])
            return self['gamma'].sel(mode_num=ind).values

        if key.startswith('freq') and '(' in key:
            ind = int(key.split('(')[1].split(')')[0])
            return self['freq'].sel(mode_num=ind).values

        raise KeyError(key)


class OMFITtglf_wavefunction(OMFITascii, SortedDict):
    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        nmodes, nfields, npoints = list(map(int, lines[0].split()))
        self.nmodes = nmodes
        self.nfields = nfields
        keys = lines[1].split()
        self.headers = keys[1:]
        content = ''.join(lines[2:]).split()
        self['theta'] = np.array(content[0 :: nmodes * nfields * 2 + 1], dtype=float)
        for ik, k in enumerate(keys[1:]):
            for n in range(nmodes):
                self['%s(%d)' % (k, n + 1)] = np.array(content[2 * n * nfields + 1 + ik :: nmodes * nfields * 2 + 1], dtype=float)

    def plot(self):
        def pi_mult_formatter(x, pos):
            if x == 0:
                return '0'
            if x == np.pi:
                return r'$\pi$'
            if x == -np.pi:
                return r'$-\pi$'
            return r'$%d\pi$' % (int(round(x / np.pi, 0)))

        fig, axs = pyplot.subplots(self.nfields, self.nmodes, num=pyplot.gcf().number, sharex=True, sharey='row', squeeze=False)
        for n in range(self.nmodes):
            for ki, k in enumerate(self.headers):
                axs[int(ki // 2)][n].plot(self['theta'], self['%s(%d)' % (k, n + 1)], ls=['-', '--'][ki % 2])
                if n == 0:
                    axs[int(ki // 2)][n].set_ylabel(k.split('(')[1].split(')')[0])
                if ki == len(self.headers) - 1:
                    axs[int(ki // 2)][n].set_xlabel(r'$\theta$')
                    axs[int(ki // 2)][n].xaxis.set_major_locator(MultipleLocator(np.pi))
                    axs[int(ki // 2)][n].xaxis.set_major_formatter(FuncFormatter(pi_mult_formatter))
        fig.canvas.draw()


class OMFITtglf_flux_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.sum_flux_spectrum file and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.sum_flux_spectrum file

    :param n_species: Number of species

    :param n_fields: Number of fields
    '''

    def __init__(self, filename, ky_file, field_labels, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels
        self.field_labels = self.OMFITproperties['field_labels'] = field_labels
        self.n_species = len(self.spec_labels)
        self.n_fields = len(self.field_labels)

    @dynaLoad
    def load(self):
        ns = self.n_species
        nf = self.n_fields
        with open(self.filename) as f:
            content = f.read()
        tmpdict = SortedDict()
        ky = get_ky_spectrum(self.ky_file)
        tmpdict['ky'] = np.array(ky, dtype=float)
        for s in range(ns):
            for f in range(nf):
                ind1 = content.find('species =')
                ind2 = content.find('species =', ind1 + 10)
                data = content[ind1:ind2]
                first_two = data.splitlines()[:2]
                spec = int(first_two[0].split()[2])
                field = int(first_two[0].split()[5])
                spec_label = self.spec_labels[s]
                labels = [k.strip().replace('flux', '').strip() for k in first_two[1].split(',')]
                keys = [k + '_field_%d_spec_%s' % (field, spec_label) for k in labels]
                labels = labels[:]
                data = ''.join(data.splitlines()[2:]).split()
                for ki, k in enumerate(keys):
                    tmpdict[k] = np.array(data[ki :: len(keys)], dtype=float)
                content = content[content.find('species =', 10) :]
        ky = tmpdict['ky']
        tmparray = {}
        for label in labels:
            tmparray['_'.join(label.split())] = DataArray(
                np.zeros((ns, nf, len(ky))),
                dims=('species', 'field', 'ky'),
                coords={'species': self.spec_labels, 'field': self.field_labels, 'ky': ky},
            )
        for k, v in list(tmpdict.items()):
            if k == 'ky':
                continue
            quant, field = k.split('_field_', 2)
            quant = '_'.join(quant.split())
            field, spec_label = field.split('_spec_')
            spec_ind = self.spec_labels.index(spec_label)
            field_ind = int(field) - 1
            tmparray[quant][spec_ind, field_ind, :] = v
        self.update(tmparray)
        self._initialized = False
        self.labels = labels
        self._initialized = True

    @dynaLoad
    def plot(self, fn=None):
        '''
        Plot the flux spectra

        :param fn: A FigureNotebook instance
        '''
        ns = self.n_species
        nf = self.n_fields
        if fn is None:
            from omfit_plot import FigureNotebook

            tabbed = FigureNotebook(nfig=0, name='TGLF Flux Spectra')
        else:
            tabbed = fn
        for k in self.labels:
            fig = tabbed.add_figure(label=k)
            fig.suptitle(k)
            for s in range(ns):
                for f in range(nf):
                    if s == 0 and f == 0:
                        ax0 = ax = axr = fig.use_subplot(ns, nf, s * nf + f + 1)
                    elif f == 0:
                        ax = axr = fig.use_subplot(ns, nf, s * nf + f + 1, sharex=ax0)
                    else:
                        ax = fig.use_subplot(ns, nf, s * nf + f + 1, sharex=ax0, sharey=axr)
                    if f == 0:
                        ax.set_ylabel('Species: %s' % (self.spec_labels[s]))
                    if s == 0:
                        ax.set_title([r'$\phi$', r'$B_{\perp}$', r'$B_{\parallel}$'][f])
                    ax.plot(self['ky'], self[k + '_field_%d_spec_%s' % (f + 1, self.spec_labels[s])])
                    ax.set_xscale('log')
                    ax.axis('tight')
            autofmt_sharexy(fig=fig)
            fig.canvas.draw()

    @dynaLoad
    def __getitem__(self, key):
        if key in self:
            return OMFITdataset.__getitem__(self, key)
        try:
            quant, field = key.split('_field_', 2)
            quant = '_'.join(quant.split())
            field, spec_label = field.split('_spec_')
            spec_ind = self.spec_labels.index(spec_label)
            field_ind = int(field) - 1
            return self[quant].isel(field=field_ind, species=spec_ind)
        except Exception as _excp:
            print(_excp)
            raise KeyError(k)


class OMFITtglf_nete_crossphase_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.nete_crossphase_spectrum file and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.nete_crossphase_spectrum file

    :param nmodes: Number of modes computed by TGLF and used in the
    '''

    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file

    @dynaLoad
    def load(self):
        nmodes = self.nmodes
        with open(self.filename, 'r') as f:
            content = f.readlines()
        content = ''.join(content[2:]).split()
        ky = get_ky_spectrum(self.ky_file)
        tmparray = []
        for k in range(self.nmodes):
            tmparray.append(np.array(content[k::nmodes], dtype=float))
        self.update({'nete': DataArray(np.array(tmparray), dims=('mode_num', 'ky'), coords={'mode_num': np.arange(nmodes) + 1, 'ky': ky})})

    def plot(self, ax=None):
        '''
        Plot the nete crossphase spectrum

        :param ax: A matplotlib axes instance
        '''
        if ax is None:
            fig, ax = pyplot.subplots(1, 1, squeeze=True)
        ky = self['ky']
        nmodes = self.nmodes
        for k in range(nmodes):
            ax.plot(ky, self['nete_crossphase_spectrum(%d)' % (k + 1)] / np.pi, label='Mode %d' % (k + 1))
        ax.legend(loc='best')
        ax.set_xscale('log')
        ax.set_xlabel(r'$k_y$')
        ax.set_ylabel(r'$\delta n_e$ $\delta T_e$ crossphase')
        ax.set_title(r'$\Theta_{\delta n_e\delta T_e}$')
        ax.axis('tight')
        ax.set_yticks(np.linspace(-np.pi / 2.0, np.pi / 2.0, 5), [r'$-\pi/2$', r'$\pi/4$', '0', r'$\pi/4$', r'$\pi/2$'])
        fmt = pyplot.ScalarFormatter()
        fmt.set_scientific(False)
        ax.xaxis.set_major_formatter(fmt)

    @dynaLoad
    def __getitem__(self, key):
        if key in self:
            return OMFITdataset.__getitem__(self, key)
        if 'nete_crossphase_spectrum(' in key:
            ind = int(key.split('(')[1].split(')')[0])
            return self['nete'].sel(mode_num=ind)
        raise KeyError(key)


class OMFITtglf_nsts_crossphase_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the out.tglf.nsts_crossphase_spectrum file and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.nsts_crossphase_spectrum file

    :param nmodes: Number of modes computed by TGLF and used in the
    '''

    def __init__(self, filename, ky_file, nmodes, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            content = f.readlines()  # Remove the main header
        header = content.pop(0)
        nspec = int(header.strip().split()[-2])
        nmodes = self.nmodes
        for ci, c in enumerate(content):
            if ci == 0:
                continue
            if c.strip().startswith('species'):
                nk = ci - 2  # Two header lines
                break
        nsts = np.zeros((nspec, nmodes, nk), dtype=float)
        for si in range(nspec):
            block = ' '.join(content[(2 + nk) * si + 2 : (2 + nk) * (si + 1)]).split()
            if si == 0:
                ky = get_ky_spectrum(self.ky_file)
            for mi in range(nmodes):
                nsts[si, mi, :] = np.array(block[mi::nmodes], dtype=float)
        self.update(
            {
                'nsts': DataArray(
                    np.array(nsts),
                    dims=('species', 'mode_num', 'ky'),
                    coords={'species': self.spec_labels, 'mode_num': np.arange(nmodes) + 1, 'ky': ky},
                )
            }
        )

    def plot(self, axs=None):
        '''
        Plot the nsts crossphase spectrum

        :param axs: A sequence of matplotlib axes instances of length len(self['species'])
        '''
        ky = self['ky']
        nmodes = self.nmodes
        nspec = len(self['species'])
        if axs is None or len(np.atleast1d(axs)) != nspec:
            fig, axs = pyplot.subplots(nspec, 1, squeeze=True, sharex=True)
        fmt = pyplot.ScalarFormatter()
        fmt.set_scientific(False)
        for si, spec in enumerate(self['species']):
            ax = axs[si]
            ax.set_ylabel(f'Species: {spec.data}')
            ax.xaxis.set_major_formatter(fmt)
            ax.set_yticks(np.linspace(-1, 1, 5))
            ax.set_yticklabels([r'$-\pi/2$', r'$\pi/4$', '0', r'$\pi/4$', r'$\pi/2$'])
            for mi in range(nmodes):
                ax.plot(ky, self['nsts'].isel(species=si, mode_num=mi) / np.pi, label='Mode %d' % (mi + 1))
            ax.set_ylim([-1.1, 1.1])
        ax.legend(loc='best')
        ax.set_xscale('log')
        ax.set_xlabel(r'$k_y$')
        axs[0].set_title(r'$\Theta_{\delta n_s\delta T_s}$')
        ax.axis('tight')


class OMFITtglf_potential_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the potential fluctuation spectrum in out.tglf.potential_spectrum and
    provide a convenient means for plotting it.

    :param filename: Path to the out.tglf.potential_spectrum file
    '''

    def __init__(self, filename, ky_file, nmodes, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        nmodes = self.nmodes
        ky = get_ky_spectrum(self.ky_file)
        description = lines[0]
        columns = [x.strip() for x in lines[1].split(',')]
        nc = len(columns)
        content = ''.join(lines[6:]).split()
        tmpdict = {}
        tmpdict['ky'] = np.array(ky, dtype=float)
        for ik, k in enumerate(columns):
            tmp = []
            for nm in range(nmodes):
                tmp.append(np.array(content[ik + nm * nc :: nmodes * nc], dtype=float))
            tmpdict[k] = tmp
        for k, v in list(tmpdict.items()):
            if k == 'ky':
                continue
            self[k] = xarray.DataArray(v, dims=('mode_num', 'ky'), coords={'ky': tmpdict['ky'], 'mode_num': np.arange(nmodes) + 1})

    @dynaLoad
    def plot(self, fn=None):
        '''
        Plot the fields

        :param fn: A FigureNotebook instance
        '''
        from omfit_plot import FigureNotebook

        if fn is None:
            fn = FigureNotebook('Field spectra')
        nmodes = self.nmodes
        fmt = pyplot.ScalarFormatter()
        fmt.set_scientific(False)
        for k in self.data_vars:
            for nm in range(nmodes):
                if not np.any(self[k] != 0):
                    continue
                fig, ax = fn.subplots(label=k + ', mode = ' + str(nm + 1), squeeze=True)
                ax.plot(self['ky'], self[k][nm])
                ax.set_xscale('log')
                ax.axis('tight')
                ax.xaxis.set_major_formatter(fmt)
                ax.set_xlabel('$k_y$')


class OMFITtglf_fluct_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the {density,temperature} fluctuation spectrum in
    out.tglf.{density,temperature}_spectrum  and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.{density,temperature}_spectrum file

    :param ns: Number of species

    :param label: Type of fluctuations ('density' or 'temperature')
    '''

    pretty_names = {'density': r'\delta n ', 'temperature': r'\delta T '}

    def __init__(self, filename, ky_file, ns, label, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.ns = self.OMFITproperties['ns'] = ns
        self.label = self.OMFITproperties['label'] = label
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels

    @dynaLoad
    def load(self):
        ns = self.ns
        with open(self.filename, 'r') as f:
            content = f.readlines()
        content = ''.join(content[2:]).split()
        ky = get_ky_spectrum(self.ky_file)
        tmplist = []
        for s in range(ns):
            tmplist.append(np.array(content[s::ns], dtype=float))
        self[self.label] = xarray.DataArray(np.array(tmplist), dims=('species', 'ky'), coords={'species': self.spec_labels, 'ky': ky})

    @dynaLoad
    def plot(self, axs=None):
        '''
        Plot the fluctuation spectrum

        :param axs: A list of matplotlib axes of length self.ns
        '''
        from matplotlib import pyplot
        from matplotlib.ticker import ScalarFormatter

        if axs is None:
            fig, axs = pyplot.subplots(self.ns, 1, sharex=True, sharey=True)
        else:
            if len(axs) != self.ns:
                raise ValueError('Must pass length %s list of axes' % self.ns)
            fig = axs[0].get_figure()
        ns = self.ns
        lab_base = self.pretty_names[self.label]
        for s in range(ns):
            ax = axs[s]
            ax.plot(self['ky'], self[self.label + '_spec_%d' % (s + 1)], label=r'$%s_{%s}$' % (lab_base, self.spec_labels[s]))
            ax.legend()
            ax.set_xscale('log')
            ax.axis('tight')
            fmt = pyplot.ScalarFormatter()
            fmt.set_scientific(False)
            ax.xaxis.set_major_formatter(fmt)
        ax.set_xlabel(r'$k_y$')
        try:
            autofmt_sharexy(fig=fig)
        except NameError:
            pass

    def __getitem__(self, key):
        if key in self:
            return OMFITdataset.__getitem__(self, key)
        if key.startswith(self.label + '_spec_'):
            spec_ind = int(key.split('_')[-1]) - 1
            return self[self.label].isel(species=spec_ind)
        raise KeyError(key)


class OMFITtglf_intensity_spectrum(OMFITdataset, OMFITascii):
    '''
    Parse the intensity fluctuation spectrum in
    out.tglf.{density,temperature}_spectrum  and provide a convenient means for
    plotting it.

    :param filename: Path to the out.tglf.{density,temperature}_spectrum file

    :param ns: Number of species

    :param label: Type of fluctuations ('density' or 'temperature')
    '''

    def __init__(self, filename, ky_file, nmodes, ns, spec_labels, **kw):
        OMFITascii.__init__(self, filename, **kw)
        self.dynaLoad = True
        OMFITdataset.__init__(self)
        self.ky_file = self.OMFITproperties['ky_file'] = ky_file
        self.nmodes = self.OMFITproperties['nmodes'] = nmodes
        self.ns = self.OMFITproperties['ns'] = ns
        self.spec_labels = self.OMFITproperties['spec_labels'] = spec_labels

    @dynaLoad
    def load(self):
        ns = self.ns
        nmodes = self.nmodes
        ky = get_ky_spectrum(self.ky_file)
        nky = len(ky)
        with open(self.filename, 'r') as f:
            dens, temp, vpara, enpara = np.loadtxt(f, skiprows=4, unpack=True)

        dims = ("species", "ky", "mode_num")
        coords = dict(species=self.spec_labels, ky=ky, mode_num=np.arange(nmodes) + 1)

        density = dens.reshape(ns, nky, nmodes)
        self['density'] = xarray.DataArray(density, dims=dims, coords=coords)
        temperature = temp.reshape(ns, nky, nmodes)
        self['temperature'] = xarray.DataArray(temperature, dims=dims, coords=coords)
        parallel_vel = vpara.reshape(ns, nky, nmodes)
        self['parallel_velocity'] = xarray.DataArray(parallel_vel, dims=dims, coords=coords)
        parallel_energy = enpara.reshape(ns, nky, nmodes)
        self['parallel_energy'] = xarray.DataArray(parallel_energy, dims=dims, coords=coords)


class OMFITtglf(OMFITdir):
    '''
    The purpose of this class is to be able to store all results from a given
    TGLF run in its native format, but parsing the important parts into the tree

    :param filename: Path to TGLF run
    '''

    def __init__(self, filename, **kw):
        printd('Calling OMFITtglf init', topic='OMFITtglf')
        OMFITdir.__init__(self, filename, **kw)
        printd('print self.keys():', list(self.keys()), topic='OMFITtglf')

        # remove 'OMFIT_run_command.sh'
        if 'OMFIT_run_command.sh' in self:
            del self['OMFIT_run_command.sh']

        # convert OMFITpath to OMFITascii
        for item in list(self.keys()):
            if isinstance(self[item], OMFITpath):
                self[item].__class__ = OMFITascii

        # rename input.tglf.gen to input.tglf
        if 'input.tglf.gen' in self:
            input_tglf = self['input.tglf'] = OMFITgacode(self['input.tglf.gen'].filename, noCopyToCWD=True)
            del self['input.tglf.gen']

        # robust, consistent species labeling,
        ns = self['input.tglf']['NS']
        from omfit_classes.utils_math import element_symbol

        spec_labels = []
        lump_counter = 1
        for i in range(1, ns + 1):
            charge = self['input.tglf'][f'ZS_{i}']
            mass = self['input.tglf'][f'MASS_{i}']
            try:
                l = element_symbol(charge, round(mass, 1) * 2).lower()
            except ValueError:
                l = f"lump{lump_counter}"
                lump_counter += 1
            spec_labels += [l]
        self.spec_labels = spec_labels

        # consistent field labels,
        field_labels = ['phi']
        if self['input.tglf']['USE_BPER']:
            field_labels += ['B_perp']
        if self['input.tglf']['USE_BPAR']:
            field_labels += ['B_parallel']
        self.field_labels = field_labels

        # Note: as part of the parsing process, some entries under SELF are deleted.
        #      however we are not deleting the files these entries referred to,
        #      and because OMFITtglf inherits from OMFITdir these files will be carried
        #      through even if they are not visible in the OMFIT tree
        if np.any([str(k).startswith('out') for k in self]):
            self._parse_version()
            self._parse_prec()
            if not input_tglf['USE_TRANSPORT_MODEL']:  # linear run
                self['wavefunction'] = OMFITtglf_wavefunction(self['out.tglf.wavefunction'].filename, noCopyToCWD=True)
                del self['out.tglf.wavefunction']
            else:
                if 'out.tglf.eigenvalue_spectrum' in self:
                    self['eigenvalue_spectrum'] = OMFITtglf_eig_spectrum(
                        self['out.tglf.eigenvalue_spectrum'].filename,
                        self['out.tglf.ky_spectrum'].filename,
                        nmodes=input_tglf['NMODES'],
                        noCopyToCWD=True,
                    )
                    del self['out.tglf.eigenvalue_spectrum']
                try:
                    self._parse_potential_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_flucs_spectra()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_flux_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_QL_flux_spectrum()
                except Exception as _excp:
                    printe(_excp)
                # try: # Not currently a TGLF output, leave for future compatibility.
                #     self._parse_QL_intensity_spectrum()
                # except Exception as _excp:
                #     printe(_excp)
                try:
                    self._parse_nete_crossphase_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_nsts_crossphase_spectrum()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_gbflux()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_run()
                except Exception as _excp:
                    printe(_excp)
                try:
                    self._parse_intensity_spectrum()
                except Exception as _excp:
                    printe(_excp)

    def plot(self):
        for k in self:
            if hasattr(self[k], 'plot'):
                self[k].plot()

    def __delitem__(self, key):
        '''
        Deleting an item only deletes it from the tree, not from the underlying
        directory (which ``OMFITdir`` would do)
        '''
        super(OMFITdir, self).__delitem__(key)

    def _parse_flucs_spectra(self):
        '''
        Parse the fluctuation spectra in out.tglf.{density,temperature}_spectrum
        '''
        ns = self['input.tglf']['NS']
        result = SortedDict()
        for field in ['density', 'temperature']:
            if '%s_spectrum' % field in self:
                continue
            fn = 'out.tglf.%s_spectrum' % field
            if fn not in self:
                printe('No %s file to parse' % fn)
                continue
            self['%s_spectrum' % field] = OMFITtglf_fluct_spectrum(
                self[fn].filename, self['out.tglf.ky_spectrum'].filename, ns, field, self.spec_labels, noCopyToCWD=True
            )
            del self[fn]

    def _parse_potential_spectrum(self):
        '''
        Parse the potential fluctuation spectrum in out.tglf.potential_spectrum
        '''
        nm = self['input.tglf']['NMODES']
        if 'potential_spectrum' in self:
            return
        for fn in ['out.tglf.potential_spectrum', 'out.tglf.field_spectrum']:
            if fn not in self and fn == 'out.tglf.potential_spectrum':
                continue
            elif fn not in self and fn == 'out.tglf.field_spectrum':
                printe('No %s file to parse' % fn)
                return
        self['potential_spectrum'] = OMFITtglf_potential_spectrum(
            self[fn].filename, self['out.tglf.ky_spectrum'].filename, nmodes=nm, noCopyToCWD=True
        )
        del self[fn]

    def _parse_version(self):
        '''
        Parse the version information in out.tglf.version
        '''
        with open(self['out.tglf.version'].filename, 'r') as f:
            content = f.readlines()
        self['GACODE_VERSION'], self['GACODE_PLATFORM'], self['TIMESTAMP'] = [x.strip() for x in content[:3]]
        del self['out.tglf.version']

    def _parse_prec(self):
        '''
        Parse the out.tglf.prec file (a single number)
        '''
        self['regression_prec'] = None
        if 'out.tglf.prec' in self:
            with open(self['out.tglf.prec'].filename, 'r') as f:
                content = f.read()
            self['regression_prec'] = float(content.strip())
            del self['out.tglf.prec']

    def _parse_flux_spectrum(self):
        '''
        Parse the flux spectrum from out.tglf.sum_flux_spectrum
        '''
        self['sum_flux_spectrum'] = OMFITtglf_flux_spectrum(
            self['out.tglf.sum_flux_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            self.field_labels,
            self.spec_labels,
            noCopyToCWD=True,
        )
        del self['out.tglf.sum_flux_spectrum']

    def _parse_QL_flux_spectrum(self):
        '''
        Parse the QL weight spectrum from out.tglf.QL_flux_spectrum
        '''
        ns = self['input.tglf']['NS']
        self['QL_flux_spectrum'] = OMFITtglf_QL_flux_spectrum(
            self['out.tglf.QL_flux_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            self.field_labels,
            self.spec_labels,
            noCopyToCWD=False,
        )
        # del self['out.tglf.QL_flux_spectrum'] # some workflows still parse the raw QL flux file

    def _parse_QL_intensity_spectrum(self):
        '''
        Parse the QL weight spectrum from out.tglf.QL_intensity_spectrum
        '''
        ns = self['input.tglf']['NS']
        self['QL_intensity_spectrum'] = OMFITtglf_QL_intensity_spectrum(
            self['out.tglf.QL_intensity_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            ns,
            self.spec_labels,
            noCopyToCWD=False,
        )

    def _parse_nete_crossphase_spectrum(self):
        '''
        Parse the cross phase spectrum from out.tglf.nete_crossphase_spectrum
        '''
        input_tglf = self['input.tglf']
        self['nete_crossphase_spectrum'] = OMFITtglf_nete_crossphase_spectrum(
            self['out.tglf.nete_crossphase_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            nmodes=input_tglf['NMODES'],
            noCopyToCWD=True,
        )
        del self['out.tglf.nete_crossphase_spectrum']

    def _parse_nsts_crossphase_spectrum(self):
        '''
        Parse the cross phase spectrum from out.tglf.nsts_crossphase_spectrum
        '''
        input_tglf = self['input.tglf']
        self['nsts_crossphase_spectrum'] = OMFITtglf_nsts_crossphase_spectrum(
            self['out.tglf.nsts_crossphase_spectrum'].filename,
            self['out.tglf.ky_spectrum'].filename,
            input_tglf['NMODES'],
            self.spec_labels,
            noCopyToCWD=True,
        )
        del self['out.tglf.nsts_crossphase_spectrum']

    def _parse_gbflux(self):
        '''
        Parse the flux from the out.tglf.gbflux file
        '''
        try:
            with open(self['out.tglf.gbflux'].filename) as f:
                content = f.read()
            tmp = list(map(float, content.split()))
            if 'std.tglf.gbflux' in self:
                with open(self['std.tglf.gbflux'].filename) as f:
                    content = f.read()
                tmp = uarray(tmp, list(map(float, content.split())))
            tmp = tolist(np.reshape(tmp, (4, -1)))
            species = ['elec'] + ['ion' + str(k) for k in range(1, len(tmp[0]))]
            tmp.insert(0, species)
            printd('Right before out.tglf.run creation', topic='OMFITtglf')
            result = SortedDict()
            result['header'] = ''
            result['columns'] = ['.', 'Gam/Gam_GB', 'Q/Q_GB', 'Pi/Pi_GB', 'S/S_GB']
            result['data'] = torecarray(tmp, result['columns'])
            if 'out.tglf.gbflux' in self:
                del self['out.tglf.gbflux']
            if 'std.tglf.gbflux' in self:
                del self['std.tglf.gbflux']
        except ValueError:
            result = OMFITasciitable(self.filename + '/out.tglf.gbflux', noCopyToCWD=True)
        self['gbflux'] = result

    def _parse_run(self):
        '''
        Parse the flux from the out.tglf.run file
        data should be same as gbflux file, but also includes local MHD stability
        '''
        with open(self['out.tglf.run'].filename) as f:
            lines = f.readlines()
        results = SortedDict()
        lines = [line.split() for line in lines]
        for line in lines:
            if 'D(R)' in line:
                for i, item in enumerate(line):
                    try:
                        results[line[i - 2]] = float(item)
                    except Exception:
                        pass
            elif 'Gam' in line[0]:
                results['.'] = line

            elif 'elec' in line[0] or 'ion' in line[0]:
                line_name = line[0]
                line_split = [float(l) for l in line[1:]]
                results[line_name] = line_split

        self['run'] = results
        del self['out.tglf.run']

    def _parse_intensity_spectrum(self):
        input_tglf = self['input.tglf']
        self['intensity_spectrum'] = OMFITtglf_intensity_spectrum(
            self.filename + '/out.tglf.intensity_spectrum',
            self['out.tglf.ky_spectrum'].filename,
            input_tglf['NMODES'],
            input_tglf['NS'],
            self.spec_labels,
        )
        del self['out.tglf.intensity_spectrum']

    def saturation_rule(self, saturation_rule_name):
        ky_spect = np.asarray(self['eigenvalue_spectrum']['ky'])
        gammas = np.asarray(self['eigenvalue_spectrum']['gamma']).T
        potential = self['potential_spectrum']['potential'].T.values

        with open(self['out.tglf.QL_flux_spectrum'].filename, 'r') as f:
            lines = f.readlines()
        nky, nm, ns, nfield, ntype = list(map(int, lines[3].split()))

        # QL weights
        with open(self['out.tglf.QL_flux_spectrum'].filename, 'r') as f:
            QL_data = np.loadtxt(f, skiprows=4, unpack=True).reshape(nky, nm, ns, nfield, ntype)
        particle_QL = QL_data[:, :, :, :, 0]
        energy_QL = QL_data[:, :, :, :, 1]
        toroidal_stress_QL = QL_data[:, :, :, :, 2]
        parallel_stress_QL = QL_data[:, :, :, :, 3]
        exchange_QL = QL_data[:, :, :, :, 4]

        with open(self['out.tglf.spectral_shift'].filename, 'r') as f:
            kx0_e = np.loadtxt(f, skiprows=5, unpack=True)

        with open(self['out.tglf.scalar_saturation_parameters'].filename, 'r') as f:
            ave_p0, B_unit, R_unit, q_unit, SAT_geo0_out, kx_geo0_out = np.loadtxt(f, skiprows=5, unpack=True)

        R_unit = np.ones((21, 2)) * R_unit

        return sum_ky_spectrum(
            sat_rule_in=saturation_rule_name,
            ky_spect=ky_spect,
            gp=gammas,
            ave_p0=ave_p0,
            R_unit=R_unit,
            kx0_e=kx0_e,
            potential=potential,
            particle_QL=particle_QL,
            energy_QL=energy_QL,
            toroidal_stress_QL=toroidal_stress_QL,
            parallel_stress_QL=parallel_stress_QL,
            exchange_QL=exchange_QL,
            etg_fact=1.25,
            c0=32.48,
            c1=0.534,
            exp1=1.547,
            cx_cy=0.56,
            alpha_x=1.15,
            **self['input.tglf'],
        )


def intensity_desat(ky_spect, gradP, q, taus_2):
    '''
    Dummy Experimental SATuration rule

    :param ky_spect: poloidal wave number [nk]

    :param gradP: P_PRIME_LOC (pressure gradient - see tglf inputs: https://gacode.io/tglf/tglf_list.html)

    :param q: absolute value of safety factor (i.e. Q_LOC)

    :param taus_2: ratio of T_main_ion/ T_e
    '''
    intensity_desat = (0.0082 / abs(gradP) + 0.1 * log10(ky_spect)) / (ky_spect ** ((3.81 * q) / (q + taus_2)))
    intensity_desat = np.c_[intensity_desat, intensity_desat]
    return intensity_desat


def intensity_sat0(
    ky_spect,
    gp,
    ave_p0,
    R_unit,
    kx0_e,
    etg_fact,
    c0,
    c1,
    exp1,
    cx_cy,
    alpha_x,
    B_unit=1.0,
    as_1=1.0,
    zs_1=-1.0,
    taus_1=1.0,
    mass_2=1.0,
    alpha_quench=0,
):
    '''
    SAT0 template for modifying the TGLF SAT0 intensity function from [Staebler et al., Nuclear Fusion, 2013], still needs to be normalized (see below)

    nk --> number of elements in ky spectrum
    nm --> number of modes
    ns --> number of species
    nf --> number of fields (1: electrostatic, 2: electromagnetic parallel, 3:electromagnetic perpendicular)

    :param ky_spect: poloidal wave number [nk]

    :param gp: growth rates [nk, nm]

    :param ave_p0: scalar average pressure

    :param R_unit: scalar normalized major radius

    :param kx0_e: spectral shift of the radial wavenumber due to VEXB_SHEAR [nk]

    :param etg_fact: scalar TGLF calibration coefficient [1.25]

    :param c0: scalar TGLF calibration coefficient [32.48]

    :param c1: scalar TGLF calibration coefficient [0.534]

    :param exp1: scalar TGLF calibration coefficient [1.547]

    :param cx_cy: scalar TGLF calibration coefficient [0.56] (from Eq.13)

    :param alpha_x: scalar TGLF calibration coefficient [1.15] (from Eq.13)

    :param B_unit: scalar normalized magnetic field (set to 1.0)

    :param as_1: scalar ratio of electron density to itself (must be 1.0)

    :param zs_1: scalar ratio of electron charge to the first ion charge (very likely to be -1.0)

    :param taus_1: scalar ratio of electron temperature to itself (must be 1.0)

    :param mass_2: scalar ratio of first ion mass to itself (must be 1.0)

    :param alpha_quench: scalar if alpha_quench==0 and any element in spectral shift array is greater than zero (versus equal zero), apply spectral shift routine

    :return: intensity function [nk, nm]
    '''

    if as_1 != 1.0 or taus_1 != 1.0 or mass_2 != 1.0:
        raise ValueError('as_1, taus_1, mass_2 must be equal to 1.0')
    kp = np.c_[ky_spect, ky_spect]  # add column makes two column array for dependence on two modes
    # kx0_e = np.c_[kx0_e, kx0_e]
    ks = kp * np.sqrt(taus_1 * mass_2)
    pols = (ave_p0 / np.abs(as_1 * zs_1 * zs_1)) ** 2
    R_unit[R_unit == 0] = np.amax(R_unit)  # when EV solver does not converge, R_unit is 0.0, but should be nonzero and the same for all  ky
    wd0 = ks * np.sqrt(taus_1 / mass_2) / R_unit
    gnet = gp / wd0
    cond = (alpha_quench == 0) * (np.abs(kx0_e) > 0)
    notcond = (alpha_quench != 0) + (np.abs(kx0_e) == 0)
    # Calculate intensity_given using scalar TGLF calibration coefficients
    cnorm = c0 * pols
    cnorm = cnorm / ((ks**etg_fact) * (ks > 1) + 1 * (ks <= 1))
    intensity_out = cnorm * (wd0**2) * (gnet**exp1 + c1 * gnet) / (kp**4)
    intensity_out = intensity_out / (((1 + cx_cy * kx0_e**2) ** 2) * cond + 1 * notcond)
    intensity_out = intensity_out / (((1 + (alpha_x * kx0_e) ** 4) ** 2) * cond + 1 * notcond)
    intensity_out = intensity_out / B_unit**2
    intensity_out = np.nan_to_num(intensity_out)
    intensity_out[
        intensity_out == 0
    ] = 10e10  # when EV solver did not converge, intensity and potential are zero; change zeros to large number before division
    return intensity_out  # Careful: This still needs to be normalized; next operation is intensity_out = intensity_out * potential(TGLF SAT0 output) / intensity_out(default SAT0 params)
    # See example with default parameters below and regression test 'omfit/regression/test_tglf_satpy.py'


def get_zonal_mixing(
    ky_mix,
    gamma_mix,
    **kw,
):
    """
    :param ky_mix: poloidal wavenumber [nk]
    :param gamma_mix: most unstable growth rates [nk]
    :param **kw: keyword list in input.tglf
    """
    nky = len(ky_mix)
    gammamax1 = gamma_mix[0]
    kymax1 = ky_mix[0]
    testmax1 = gammamax1 / kymax1
    jmax1 = 0
    kymin = 0
    testmax = 0.0
    j1 = 0
    kycut = 0.8 / kw["rho_ion"]
    if kw["ALPHA_ZF"] < 0:
        kymin = 0.173 * np.sqrt(2.0) / kw["rho_ion"]
    if kw["SAT_RULE"] in [2, 3]:
        kycut = kw["grad_r0_out"] * kycut
        kymin = kw["grad_r0_out"] * kymin

    for j in range(0, nky - 1):
        if ky_mix[j] <= kycut and ky_mix[j + 1] >= kymin:
            j1 = j
            kymax1 = ky_mix[j]
            testmax1 = gamma_mix[j] / kymax1
            if testmax1 > testmax:
                testmax = testmax1
                jmax_mix = j
    if testmax == 0.0:
        jmax_mix = j1

    kymax1 = ky_mix[jmax_mix]
    gammamax1 = gamma_mix[jmax_mix]

    if kymax1 < kymin:
        kymax1 = kymin
        gammamax1 = gamma_mix[0] + (gamma_mix[1] - gamma_mix[0]) * (kymin - ky_mix[0]) / (ky_mix[1] - ky_mix[0])

    if jmax_mix > 0 and jmax_mix < j1:
        jmax1 = jmax_mix
        f0 = gamma_mix[jmax1 - 1] / ky_mix[jmax1 - 1]
        f1 = gamma_mix[jmax1] / ky_mix[jmax1]
        f2 = gamma_mix[jmax1 + 1] / ky_mix[jmax1 + 1]
        deltaky = ky_mix[jmax1 + 1] - ky_mix[jmax1 - 1]
        x1 = (ky_mix[jmax1] - ky_mix[jmax1 - 1]) / deltaky
        a = f0
        b = (f1 - f0 * (1 - x1 * x1) - f2 * x1 * x1) / (x1 - x1 * x1)
        c = f2 - f0 - b
        xmax = -b / (2.0 * c)
        if ky_mix[jmax1 - 1] < kymin:
            xmin = (kymin - ky_mix[jmax1 - 1]) / deltaky
        else:
            xmin = 0.0
        if xmax >= 1.0:
            kymax1 = ky_mix[jmax1 + 1]
            gammamax1 = f2 * kymax1
        elif xmax < xmin:
            if xmin > 0.0:
                kymax1 = kymin
                gammamax1 = (a + b * xmin + c * xmin * xmin) * kymin
            else:
                kymax1 = ky_mix[jmax1 - 1]
                gammamax1 = f0 * kymax1
        else:
            kymax1 = ky_mix[jmax1 - 1] + deltaky * xmax
            gammamax1 = (a + b * xmax + c * xmax * xmax) * kymax1

    vzf_mix = gammamax1 / kymax1
    kymax_mix = kymax1
    return vzf_mix, kymax_mix, jmax_mix


def get_sat_params(sat_rule_in, ky, gammas, mts=5.0, ms=128, small=0.00000001, **kw):
    """
    This function calculates the scalar saturation parameters and spectral shift needed
    for the TGLF saturation rules, dependent on changes to 'tglf_geometry.f90' by Gary Staebler

    :mts: the number of points in the s-grid (flux surface contour)
    :ms: number of points along the arclength
    :ds: the arc length differential on a flux surface
    :R(ms): the major radius on the s-grid
    :Z(ms): the vertical coordinate on the s-grid
    :Bp(ms): the poloidal magnetic field on the s-grid normalized to B_unit
    :**kw: input.tglf
    """
    drmajdx_loc = kw["DRMAJDX_LOC"]
    drmindx_loc = kw["DRMINDX_LOC"]
    kappa_loc = kw["KAPPA_LOC"]
    s_kappa_loc = kw["S_KAPPA_LOC"]
    rmin_loc = kw["RMIN_LOC"]
    rmaj_loc = kw["RMAJ_LOC"]
    zeta_loc = kw["ZETA_LOC"]
    q_s = kw["Q_LOC"]
    q_prime_s = kw["Q_PRIME_LOC"]
    p_prime_s = kw["P_PRIME_LOC"]
    delta_loc = kw["DELTA_LOC"]
    s_delta_loc = kw["S_DELTA_LOC"]
    s_zeta_loc = kw["S_ZETA_LOC"]
    alpha_e_in = kw["ALPHA_E"]
    vexb_shear = kw["VEXB_SHEAR"]
    sign_IT = kw["SIGN_IT"]
    units = kw["UNITS"]
    mass_2 = kw["MASS_2"]
    taus_2 = kw["TAUS_2"]
    zs_2 = kw["ZS_2"]

    zmaj_loc = 0.0
    dzmajdx_loc = 0.0
    norm_ave = 0.0
    SAT_geo1_out = 0.0
    SAT_geo2_out = 0.0
    dlp = 0.0

    R = np.zeros(ms + 1)
    Z = np.zeros(ms + 1)
    Bp = np.zeros(ms + 1)
    Bt = np.zeros(ms + 1)
    B = np.zeros(ms + 1)
    b_geo = np.zeros(ms + 1)
    qrat_geo = np.zeros(ms + 1)
    sin_u = np.zeros(ms + 1)
    s_p = np.zeros(ms + 1)
    r_curv = np.zeros(ms + 1)
    psi_x = np.zeros(ms + 1)
    costheta_geo = np.zeros(ms + 1)

    pi_2 = 2 * np.pi
    if rmin_loc < 0.00001:
        rmin_loc = 0.00001
    vs_2 = np.sqrt(taus_2 / mass_2)
    gamma_reference_kx0 = gammas[0, :]

    # Miller geo
    rmin_s = rmin_loc
    Rmaj_s = rmaj_loc

    # compute the arclength around the flux surface:
    # initial values define dtheta
    theta = 0.0
    x_delta = np.arcsin(delta_loc)
    arg_r = theta + x_delta * np.sin(theta)
    darg_r = 1.0 + x_delta * np.cos(theta)
    arg_z = theta + zeta_loc * np.sin(2.0 * theta)
    darg_z = 1.0 + zeta_loc * 2.0 * np.cos(2.0 * theta)
    r_t = -rmin_loc * np.sin(arg_r) * darg_r
    z_t = kappa_loc * rmin_loc * np.cos(arg_z) * darg_z
    l_t = np.sqrt(r_t**2 + z_t**2)

    # scale dtheta by l_t to keep mts points in each ds interval of size pi_2/ms
    dtheta = pi_2 / (mts * ms * l_t)
    l_t1 = l_t
    arclength = 0.0

    while theta < pi_2:
        theta = theta + dtheta
        if theta > pi_2:
            theta = theta - dtheta
            dtheta = pi_2 - theta
            theta = pi_2

        arg_r = theta + x_delta * np.sin(theta)
        darg_r = 1.0 + x_delta * np.cos(theta)  # d(arg_r)/dtheta
        r_t = -rmin_loc * np.sin(arg_r) * darg_r  # dR/dtheta
        arg_z = theta + zeta_loc * np.sin(2.0 * theta)
        darg_z = 1.0 + zeta_loc * 2.0 * np.cos(2.0 * theta)  # d(arg_z)/dtheta
        z_t = kappa_loc * rmin_loc * np.cos(arg_z) * darg_z  # dZ/dtheta
        l_t = np.sqrt(r_t**2 + z_t**2)  # dl/dtheta
        arclength = arclength + 0.50 * (l_t + l_t1) * dtheta  # arclength along flux surface in poloidal direction
        l_t1 = l_t

    # Find the theta points which map to an equally spaced s-grid of ms points along the arclength
    # going clockwise from the outboard midplane around the flux surface
    # by searching for the theta where dR**2 + dZ**2 >= ds**2 for a centered difference df=f(m+1)-f(m-1).
    # This keeps the finite difference error of dR/ds, dZ/ds on the s-grid small
    ds = arclength / ms
    t_s = np.zeros(ms + 1)
    t_s[ms] = -pi_2

    # Make a first guess based on theta = 0.0
    theta = 0.0
    arg_r = theta + x_delta * np.sin(theta)
    darg_r = 1.0 + x_delta * np.cos(theta)
    arg_z = theta + zeta_loc * np.sin(2.0 * theta)
    darg_z = 1.0 + zeta_loc * 2.0 * np.cos(2.0 * theta)
    r_t = -rmin_loc * np.sin(arg_r) * darg_r
    z_t = kappa_loc * rmin_loc * np.cos(arg_z) * darg_z
    l_t = np.sqrt(r_t**2 + z_t**2)
    dtheta = -ds / l_t
    theta = dtheta
    l_t1 = l_t

    for m in range(1, int(ms / 2) + 1):
        arg_r = theta + x_delta * np.sin(theta)
        darg_r = 1.0 + x_delta * np.cos(theta)
        arg_z = theta + zeta_loc * np.sin(2.0 * theta)
        darg_z = 1.0 + zeta_loc * 2.0 * np.cos(2.0 * theta)
        r_t = -rmin_loc * np.sin(arg_r) * darg_r
        z_t = kappa_loc * rmin_loc * np.cos(arg_z) * darg_z
        l_t = np.sqrt(r_t**2 + z_t**2)
        dtheta = -ds / (0.5 * (l_t + l_t1))
        t_s[m] = t_s[m - 1] + dtheta
        theta = t_s[m] + dtheta
        l_t1 = l_t

    # distribute endpoint error over interior points
    dtheta = (t_s[int(ms / 2)] - (-np.pi)) / (ms / 2)

    for m in range(1, int(ms / 2) + 1):
        t_s[m] = t_s[m] - (m) * dtheta
        t_s[ms - m] = -pi_2 - t_s[m]
    # Quinn additions,
    B_unit_out = np.zeros(ms + 1)
    grad_r_out = np.zeros(ms + 1)
    for m in range(0, ms + 1):
        theta = t_s[m]
        arg_r = theta + x_delta * np.sin(theta)
        darg_r = 1.0 + x_delta * np.cos(theta)
        arg_z = theta + zeta_loc * np.sin(2.0 * theta)
        darg_z = 1.0 + zeta_loc * 2.0 * np.cos(2.0 * theta)

        R[m] = rmaj_loc + rmin_loc * np.cos(arg_r)  # = R(theta)
        Z[m] = zmaj_loc + kappa_loc * rmin_loc * np.sin(arg_z)  # = Z(theta)

        R_t = -rmin_loc * np.sin(arg_r) * darg_r  # = dR/dtheta
        Z_t = kappa_loc * rmin_loc * np.cos(arg_z) * darg_z  # = dZ/dtheta

        l_t = np.sqrt(R_t**2 + Z_t**2)  # = dl/dtheta

        R_r = (
            drmajdx_loc + drmindx_loc * np.cos(arg_r) - np.sin(arg_r) * s_delta_loc * np.sin(theta) / np.sqrt(1.0 - delta_loc**2)
        )  # = dR/dr
        Z_r = (
            dzmajdx_loc
            + kappa_loc * np.sin(arg_z) * (drmindx_loc + s_kappa_loc)
            + kappa_loc * np.cos(arg_z) * s_zeta_loc * np.sin(2.0 * theta)
        )

        det = R_r * Z_t - R_t * Z_r  # Jacobian
        grad_r = abs(l_t / det)
        if m == 0:
            B_unit = 1.0 / grad_r  # B_unit choosen to make qrat_geo(0)/b_geo(0)=1.0
            if drmindx_loc == 1.0:
                B_unit = 1.0  # Waltz-Miller convention
        B_unit_out[m] = B_unit
        grad_r_out[m] = grad_r

        Bp[m] = (rmin_s / (q_s * R[m])) * grad_r * B_unit
        p_prime_s = p_prime_s * B_unit
        q_prime_s = q_prime_s / B_unit
        psi_x[m] = R[m] * Bp[m]

    delta_s = 12.0 * ds
    ds2 = 12.0 * ds**2
    for m in range(0, ms + 1):
        m1 = (ms + m - 2) % ms
        m2 = (ms + m - 1) % ms
        m3 = (m + 1) % ms
        m4 = (m + 2) % ms
        R_s = (R[m1] - 8.0 * R[m2] + 8.0 * R[m3] - R[m4]) / delta_s
        Z_s = (Z[m1] - 8.0 * Z[m2] + 8.0 * Z[m3] - Z[m4]) / delta_s
        s_p[m] = np.sqrt(R_s**2 + Z_s**2)
        R_ss = (-R[m1] + 16.0 * R[m2] - 30.0 * R[m] + 16.0 * R[m3] - R[m4]) / ds2
        Z_ss = (-Z[m1] + 16.0 * Z[m2] - 30.0 * Z[m] + 16.0 * Z[m3] - Z[m4]) / ds2
        r_curv[m] = (s_p[m] ** 3) / (R_s * Z_ss - Z_s * R_ss)
        sin_u[m] = -Z_s / s_p[m]

    # Compute f=R*Bt such that the eikonal S which solves
    # B*Grad(S)=0 has the correct quasi-periodicity S(s+Ls)=S(s)-2*pi*q_s, where Ls = arclength
    f = 0.0
    for m in range(1, ms + 1):
        f = f + 0.5 * ds * (s_p[m - 1] / (R[m - 1] * psi_x[m - 1]) + s_p[m] / (R[m] * psi_x[m]))
    f = pi_2 * q_s / f

    for m in range(0, ms + 1):
        Bt[m] = f / R[m]
        B[m] = np.sqrt(Bt[m] ** 2 + Bp[m] ** 2)
        qrat_geo[m] = (rmin_s / R[m]) * (B[m] / Bp[m]) / q_s
        b_geo[m] = B[m]
        costheta_geo[m] = -Rmaj_s * (Bp[m] / (B[m]) ** 2) * (Bp[m] / r_curv[m] - (f**2 / (Bp[m] * (R[m]) ** 3)) * sin_u[m])

    for m in range(1, ms + 1):
        dlp = s_p[m] * ds * (0.5 / Bp[m] + 0.5 / Bp[m - 1])
        norm_ave += dlp
        SAT_geo1_out += dlp * ((b_geo[0] / b_geo[m - 1]) ** 4 + (b_geo[0] / b_geo[m]) ** 4) / 2.0
        SAT_geo2_out += dlp * ((qrat_geo[0] / qrat_geo[m - 1]) ** 4 + (qrat_geo[0] / qrat_geo[m]) ** 4) / 2.0

    SAT_geo1_out = SAT_geo1_out / norm_ave
    SAT_geo2_out = SAT_geo2_out / norm_ave

    if units == "GYRO" and sat_rule_in == 1:
        SAT_geo1_out = 1.0
        SAT_geo2_out = 1.0

    R_unit = Rmaj_s * b_geo[0] / (qrat_geo[0] * costheta_geo[0])
    B_geo0_out = b_geo[0]
    Bt0_out = f / Rmaj_s
    grad_r0_out = b_geo[0] / qrat_geo[0]
    # Additional outputs for SAT2 G1(theta), Gq(theta)
    theta_out = t_s  # theta grid over which everything is calculated.
    Bt_out = B  # total magnetic field matching theta_out grid.

    # Compute spetral shift kx0_e
    vexb_shear_s = vexb_shear * sign_IT
    vexb_shear_kx0 = alpha_e_in * vexb_shear_s

    kx0_factor = abs(b_geo[0] / qrat_geo[0] ** 2)
    kx0_factor = 1.0 + 0.40 * (kx0_factor - 1.0) ** 2

    kyi = ky * vs_2 * mass_2 / abs(zs_2)
    wE = kx0_factor * np.array([min(x / 0.3, 1.0) for x in kyi]) * vexb_shear_kx0 / gamma_reference_kx0
    kx0_e = -(0.36 * vexb_shear_kx0 / gamma_reference_kx0 + 0.38 * wE * np.tanh((0.69 * wE) ** 6))

    if sat_rule_in == 1:
        if units == "CGYRO":
            wE = 0.0
            kx0_factor = 1.0
        kx0_e = -(0.53 * vexb_shear_kx0 / gamma_reference_kx0 + 0.25 * wE * np.tanh((0.69 * wE) ** 6))
    elif sat_rule_in == 2 or sat_rule_in == 3:
        kw["grad_r0_out"] = grad_r0_out
        kw["SAT_RULE"] = sat_rule_in
        if bool(kw["USE_AVE_ION_GRID"]):
            indices = [is_ for is_ in range(2, kw['NS'] + 1) if (kw[f'ZS_{is_}'] * kw[f'AS_{is_}']) / abs(kw['AS_1'] * kw['ZS_1']) > 0.1]

            charge = sum(kw[f'ZS_{is_}'] * kw[f'AS_{is_}'] for is_ in indices)
            rho_ion = sum(
                kw[f'ZS_{is_}'] * kw[f'AS_{is_}'] * (kw[f'MASS_{is_}'] * kw[f'TAUS_{is_}']) ** 0.5 / kw[f'ZS_{is_}'] for is_ in indices
            )

            rho_ion /= charge if charge != 0 else 1
        else:
            rho_ion = (kw['MASS_2'] * kw['TAUS_2']) ** 0.5 / kw['ZS_2']
        kw['rho_ion'] = rho_ion
        vzf_out, kymax_out, _ = get_zonal_mixing(ky, gamma_reference_kx0, **kw)
        if abs(kymax_out * vzf_out * vexb_shear_kx0) > small:
            kx0_e = -0.32 * ((ky / kymax_out) ** 0.3) * vexb_shear_kx0 / (ky * vzf_out)
        else:
            kx0_e = np.zeros(len(ky))
    a0 = 1.3
    if sat_rule_in == 1:
        a0 = 1.45
    elif sat_rule_in == 2 or sat_rule_in == 3:
        a0 = 1.6
    kx0_e = np.array([min(abs(x), a0) * x / abs(x) for x in kx0_e])
    kx0_e[np.isnan(kx0_e)] = 0

    return (
        kx0_e,
        SAT_geo1_out,
        SAT_geo2_out,
        R_unit,
        Bt0_out,
        B_geo0_out,
        grad_r0_out,
        theta_out,
        Bt_out,
        grad_r_out,
        B_unit_out,
    )


def mode_transition_function(x, y1, y2, x_ITG, x_TEM):
    if x < x_ITG:
        y = y1
    elif x > x_TEM:
        y = y2
    else:
        y = y1 * ((x_TEM - x) / (x_TEM - x_ITG)) + y2 * ((x - x_ITG) / (x_TEM - x_ITG))
    return y


def linear_interpolation(x, y, x0):
    i = 0
    while x[i] < x0:
        i += 1
    y0 = ((y[i] - y[i - 1]) * x0 + (x[i] * y[i - 1] - x[i - 1] * y[i])) / (x[i] - x[i - 1])
    return y0


def intensity_sat(
    sat_rule_in,
    ky_spect,
    gp,
    kx0_e,
    nmodes,
    QL_data,
    expsub=2.0,
    alpha_zf_in=1.0,
    kx_geo0_out=1.0,
    SAT_geo_out=1.0,
    bz1=0.0,
    bz2=0.0,
    return_phi_params=False,
    **kw,
):
    """
    TGLF SAT1 from [Staebler et al., 2016, PoP], SAT2 from [Staebler et al., NF, 2021] and [Staebler et al., PPCF, 2021],
    and SAT3 [Dudding et al., NF, 2022] takes both CGYRO and TGLF outputs as inputs

    :param sat_rule_in: saturation rule [1, 2, 3]

    :param ky_spect: poloidal wavenumber [nk]

    :param gp: growth rates [nk, nm]

    :param kx0_e: spectral shift of the radial wavenumber due to VEXB_SHEAR [nk]

    :param nmodes_in: number of modes stored in quasi-linear weights [1, ..., 5]

    :param QL_data: Quasi-linear weights [ky, nm, ns, nf, type (i.e. particle,energy,stress_tor,stress_para,exchange)]

    :param expsub: scalar exponent in gammaeff calculation [2.0]

    :param alpha_zf_in: scalar switch for the zonal flow coupling coefficient [1.0]

    :param kx_geo_out: scalar switch for geometry [1.0]

    :param SAT_geo_out: scalar switch for geoemtry [1.0]

    :param bz1: scalar correction to zonal flow mixing term [0.0]

    :param bz2: scalar correction to zonal flow mixing term [0.0]

    :param return_phi_params: bool, option to return parameters for calculing the SAT1, SAT2 model for phi [False]

    :param **kw: keyword list in input.tglf
    """
    if bool(kw["USE_AVE_ION_GRID"]):
        indices = [is_ for is_ in range(2, kw['NS'] + 1) if (kw[f'ZS_{is_}'] * kw[f'AS_{is_}']) / abs(kw['AS_1'] * kw['ZS_1']) > 0.1]

        charge = sum(kw[f'ZS_{is_}'] * kw[f'AS_{is_}'] for is_ in indices)
        rho_ion = sum(
            kw[f'ZS_{is_}'] * kw[f'AS_{is_}'] * (kw[f'MASS_{is_}'] * kw[f'TAUS_{is_}']) ** 0.5 / kw[f'ZS_{is_}'] for is_ in indices
        )

        rho_ion /= charge if charge != 0 else 1
    else:
        rho_ion = (kw['MASS_2'] * kw['TAUS_2']) ** 0.5 / kw['ZS_2']
    kw['rho_ion'] = rho_ion

    nky = len(ky_spect)
    if len(np.shape(gp)) > 1:
        gammas1 = gp[:, 0]  # SAT1 and SAT2 use the growth rates of the most unstable modes
    else:
        gammas1 = gp
    gamma_net = np.zeros(nky)

    if sat_rule_in == 1:
        etg_streamer = 1.05
        kyetg = etg_streamer / kw["rho_ion"]
        measure = np.sqrt(kw["TAUS_1"] * kw["MASS_2"])

    czf = abs(alpha_zf_in)
    small = 1.0e-10
    cz1 = 0.48 * czf
    cz2 = 1.0 * czf
    cky = 3.0
    sqcky = np.sqrt(cky)
    cnorm = 14.29

    if sat_rule_in in [2, 3]:
        kw["UNITS"] = "CGYRO"
        units_in = kw["UNITS"]
    else:
        units_in = kw["UNITS"]

    kycut = 0.8 / kw["rho_ion"]
    # ITG/ETG-scale separation (for TEM scales see [Creely et al., PPCF, 2019])

    vzf_out, kymax_out, jmax_out = get_zonal_mixing(ky_spect, gammas1, **kw)

    if kw["RLNP_CUTOFF"] > 0.0:
        ptot = 0
        dlnpdr = 0
        for i in range(1, kw["NS"] + 1, 1):
            ptot += kw["AS_%s" % i] * kw["TAUS_%s" % i]  # only kinetic species
            dlnpdr += kw["AS_%s" % i] * kw["TAUS_%s" % i] * (kw["RLNS_%s" % i] + kw["RLTS_%s" % i])
        dlnpdr = kw["RMAJ_LOC"] * dlnpdr / max(ptot, 0.01)

        if dlnpdr >= kw["RLNP_CUTOFF"]:
            dlnpdr = kw["RLNP_CUTOFF"]
        if dlnpdr < 4.0:
            dlnpdr = 4.0
    else:
        dlnpdr = 12.0

    if sat_rule_in == 2 or sat_rule_in == 3:
        # SAT2 fit for CGYRO linear modes NF 2021 paper
        b0 = 0.76
        b1 = 1.22
        b2 = 3.74
        if nmodes > 1:
            b2 = 3.55
        b3 = 1.0
        d1 = (kw["Bt0_out"] / kw["B_geo0_out"]) ** 4  # PPCF paper 2020
        d1 = d1 / kw["grad_r0_out"]
        # WARNING: this is correct, but it's the reciprocal in the paper (typo in paper)
        Gq = kw["B_geo0_out"] / kw["grad_r0_out"]
        d2 = b3 / Gq**2
        cnorm = b2 * (12.0 / dlnpdr)
        kyetg = 1000.0  # does not impact SAT2
        cky = 3.0
        sqcky = np.sqrt(cky)
        kycut = b0 * kymax_out
        cz1 = 0.0
        cz2 = 1.05 * czf
        measure = 1.0 / kymax_out

    if sat_rule_in == 3:
        kmax = kymax_out
        gmax = vzf_out * kymax_out
        kmin = 0.685 * kmax
        aoverb = -1.0 / (2 * kmin)
        coverb = -0.751 * kmax
        kT = 1.0 / kw["rho_ion"]  # SAT3 used up to ky rho_av = 1.0, then SAT2
        k0 = 0.6 * kmin
        kP = 2.0 * kmin
        c_1 = -2.42
        x_ITG = 0.8
        x_TEM = 1.0
        Y_ITG = 3.3 * (gmax**2) / (kmax**5)
        Y_TEM = 12.7 * (gmax**2) / (kmax**4)
        scal = 0.82  # Q(SAT3 GA D) / (2 * QLA(ITG,Q) * Q(SAT2 GA D))

        Ys = np.zeros(nmodes)
        xs = np.zeros(nmodes)

        for k in range(1, nmodes + 1):
            sum_W_i = 0

            # sum over ion species, requires electrons to be species 1
            for is_ in range(2, np.shape(QL_data)[2] + 1):
                sum_W_i += QL_data[:, k - 1, is_ - 1, 0, 1]

            # check for singularities in weight ratio near kmax
            i = 1
            while ky_spect[i - 1] < kmax:
                i += 1

            if sum_W_i[i - 1] == 0.0 or sum_W_i[i - 2] == 0.0:
                x = 0.5
            else:
                abs_W_ratio = np.abs(QL_data[:, k - 1, 0, 0, 1] / sum_W_i)
                abs_W_ratio = np.nan_to_num(abs_W_ratio)
                x = linear_interpolation(ky_spect, abs_W_ratio, kmax)

            xs[k - 1] = x
            Y = mode_transition_function(x, Y_ITG, Y_TEM, x_ITG, x_TEM)
            Ys[k - 1] = Y

    ax = 0.0
    ay = 0.0
    exp_ax = 1
    if kw["ALPHA_QUENCH"] == 0.0:
        if sat_rule_in == 1:
            # spectral shift model parameters
            ax = 1.15
            ay = 0.56
            exp_ax = 4
        elif sat_rule_in == 2 or sat_rule_in == 3:
            ax = 1.21
            ay = 1.0
            exp_ax = 2
            units_in = "CGYRO"

    for j in range(0, nky):
        kx = kx0_e[j]
        if sat_rule_in == 2 or sat_rule_in == 3:
            ky0 = ky_spect[j]
            if ky0 < kycut:
                kx_width = kycut / kw["grad_r0_out"]
            else:
                kx_width = kycut / kw["grad_r0_out"] + b1 * (ky0 - kycut) * Gq
            kx = kx * ky0 / kx_width
        gamma_net[j] = gammas1[j] / (1.0 + abs(ax * kx) ** exp_ax)

    if sat_rule_in == 1:
        vzf_out, kymax_out, jmax_out = get_zonal_mixing(ky_spect, gamma_net, **kw)
    else:
        vzf_out_fp = vzf_out
        vzf_out = vzf_out * gamma_net[jmax_out] / max(gammas1[jmax_out], small)

    gammamax1 = vzf_out * kymax_out
    kymax1 = kymax_out
    jmax1 = jmax_out
    vzf1 = vzf_out

    # include zonal flow effects on growth rate model:
    gamma_mix1 = np.zeros(nky)
    gamma = np.zeros(nky)

    for j in range(0, nky):
        gamma0 = gamma_net[j]
        ky0 = ky_spect[j]
        if sat_rule_in == 1:
            if ky0 < kymax1:
                gamma[j] = max(gamma0 - cz1 * (kymax1 - ky0) * vzf1, 0.0)
            else:
                gamma[j] = cz2 * gammamax1 + max(gamma0 - cz2 * vzf1 * ky0, 0.0)
        elif sat_rule_in == 2 or sat_rule_in == 3:
            if ky0 < kymax1:
                gamma[j] = gamma0
            else:
                gamma[j] = gammamax1 + max(gamma0 - cz2 * vzf1 * ky0, 0.0)
        gamma_mix1[j] = gamma[j]

    # Mix over ky>kymax with integration weight
    mixnorm1 = np.zeros(nky)
    for j in range(jmax1 + 2, nky):
        gamma_ave = 0.0
        mixnorm1 = ky_spect[j] * (
            np.arctan(sqcky * (ky_spect[nky - 1] / ky_spect[j] - 1.0)) - np.arctan(sqcky * (ky_spect[jmax1 + 1] / ky_spect[j] - 1.0))
        )
        for i in range(jmax1 + 1, nky - 1):
            ky_1 = ky_spect[i]
            ky_2 = ky_spect[i + 1]
            mix1 = ky_spect[j] * (np.arctan(sqcky * (ky_2 / ky_spect[j] - 1.0)) - np.arctan(sqcky * (ky_1 / ky_spect[j] - 1.0)))
            delta = (gamma[i + 1] - gamma[i]) / (ky_2 - ky_1)
            mix2 = ky_spect[j] * mix1 + (ky_spect[j] * ky_spect[j] / (2.0 * sqcky)) * (
                np.log(cky * (ky_2 - ky_spect[j]) ** 2 + ky_spect[j] ** 2) - np.log(cky * (ky_1 - ky_spect[j]) ** 2 + ky_spect[j] ** 2)
            )
            gamma_ave = gamma_ave + (gamma[i] - ky_1 * delta) * mix1 + delta * mix2
        gamma_mix1[j] = gamma_ave / mixnorm1

    if sat_rule_in == 3:
        gamma_fp = np.zeros_like(ky_spect)  # Assuming ky_spect is a numpy array
        gamma = np.zeros_like(ky_spect)  # Assuming ky_spect is a numpy array

        for j in range(1, nky + 1):
            gamma0 = gammas1[j - 1]
            ky0 = ky_spect[j - 1]

            if ky0 < kymax1:
                gamma[j - 1] = gamma0
            else:
                gamma[j - 1] = (gammamax1 * (vzf_out_fp / vzf_out)) + max(gamma0 - cz2 * vzf_out_fp * ky0, 0.0)

            gamma_fp[j - 1] = gamma[j - 1]

        # USE_MIX is true by default
        for j in range(jmax1 + 3, nky + 1):  # careful: I'm switching here to Fortran indexing, but found jmax1 using python indexing
            gamma_ave = 0.0
            ky0 = ky_spect[j - 1]
            kx = kx0_e[j - 1]

            mixnorm = ky0 * (np.arctan(sqcky * (ky_spect[nky - 1] / ky0 - 1.0)) - np.arctan(sqcky * (ky_spect[jmax1 + 1] / ky0 - 1.0)))

            for i in range(jmax1 + 2, nky):  # careful: I'm switching here to Fortran indexing, but found jmax1 using python indexing
                ky1 = ky_spect[i - 1]
                ky2 = ky_spect[i]
                mix1 = ky0 * (np.arctan(sqcky * (ky2 / ky0 - 1.0)) - np.arctan(sqcky * (ky1 / ky0 - 1.0)))
                delta = (gamma[i] - gamma[i - 1]) / (ky2 - ky1)
                mix2 = ky0 * mix1 + (ky0 * ky0 / (2.0 * sqcky)) * (
                    np.log(cky * (ky2 - ky0) ** 2 + ky0**2) - np.log(cky * (ky1 - ky0) ** 2 + ky0**2)
                )
                gamma_ave += (gamma[i - 1] - ky1 * delta) * mix1 + delta * mix2
            gamma_fp[j - 1] = gamma_ave / mixnorm

    if sat_rule_in == 3:
        if ky_spect[-1] >= kT:
            dummy_interp = np.zeros_like(ky_spect)
            k = 0
            while ky_spect[k] < kT:
                k += 1

            for i in range(k - 1, k + 1):
                gamma0 = gp[i, 0]
                ky0 = ky_spect[i]
                kx = kx0_e[i]

                if ky0 < kycut:
                    kx_width = kycut / kw["grad_r0_out"]
                    sat_geo_factor = kw["SAT_geo0_out"] * d1 * kw["SAT_geo1_out"]
                else:
                    kx_width = kycut / kw["grad_r0_out"] + b1 * (ky0 - kycut) * Gq
                    sat_geo_factor = kw["SAT_geo0_out"] * (d1 * kw["SAT_geo1_out"] * kycut + (ky0 - kycut) * d2 * kw["SAT_geo2_out"]) / ky0

                kx = kx * ky0 / kx_width
                gammaeff = 0.0
                if gamma0 > small:
                    gammaeff = gamma_fp[i]
                # potentials without multimode and ExB effects, added later
                dummy_interp[i] = scal * measure * cnorm * (gammaeff / (kx_width * ky0)) ** 2
                if units_in != "GYRO":
                    dummy_interp[i] = sat_geo_factor * dummy_interp[i]
            YT = linear_interpolation(ky_spect, dummy_interp, kT)
            YTs = np.array([YT] * nmodes)
        else:
            if aoverb * (kP**2) + kP + coverb - ((kP - kT) * (2 * aoverb * kP + 1)) == 0:
                YTs = np.zeros(nmodes)
            else:
                YTs = np.zeros(nmodes)
                for i in range(1, nmodes + 1):
                    YTs[i - 1] = Ys[i - 1] * (
                        ((aoverb * (k0**2) + k0 + coverb) / (aoverb * (kP**2) + kP + coverb - ((kP - kT) * (2 * aoverb * kP + 1))))
                        ** abs(c_1)
                    )

    # preallocate [nky] arrays for phi_params
    gammaeff_out = np.zeros((nky, nmodes))
    sig_ratio_out = np.zeros((nky, nmodes))  # SAT3
    kx_width_out = np.zeros(nky)
    sat_geo_factor_out = np.zeros(nky)
    # intensity
    field_spectrum_out = np.zeros((nky, nmodes))
    for j in range(0, nky):
        gamma0 = gp[j, 0]
        ky0 = ky_spect[j]
        kx = kx0_e[j]
        if sat_rule_in == 1:
            sat_geo_factor = kw["SAT_geo0_out"]
            kx_width = ky0
        if sat_rule_in == 2 or sat_rule_in == 3:
            if ky0 < kycut:
                kx_width = kycut / kw["grad_r0_out"]
                sat_geo_factor = kw["SAT_geo0_out"] * d1 * kw["SAT_geo1_out"]
            else:
                kx_width = kycut / kw["grad_r0_out"] + b1 * (ky0 - kycut) * Gq
                sat_geo_factor = kw["SAT_geo0_out"] * (d1 * kw["SAT_geo1_out"] * kycut + (ky0 - kycut) * d2 * kw["SAT_geo2_out"]) / ky0
            kx = kx * ky0 / kx_width

        if sat_rule_in == 1 or sat_rule_in == 2:
            for i in range(0, nmodes):
                gammaeff = 0.0
                if gamma0 > small:
                    gammaeff = gamma_mix1[j] * (gp[j, i] / gamma0) ** expsub
                if ky0 > kyetg:
                    gammaeff = gammaeff * np.sqrt(ky0 / kyetg)
                field_spectrum_out[j, i] = measure * cnorm * ((gammaeff / (kx_width * ky0)) / (1.0 + ay * kx**2)) ** 2
                if units_in != "GYRO":
                    field_spectrum_out[j, i] = sat_geo_factor * field_spectrum_out[j, i]
                # add these outputs
                gammaeff_out[j, i] = gammaeff
            kx_width_out[j] = kx_width
            sat_geo_factor_out[j] = sat_geo_factor

        elif sat_rule_in == 3:
            # First part
            if gamma_fp[j] == 0:
                Fky = 0.0
            else:
                Fky = (gamma_mix1[j] / gamma_fp[j]) ** 2 / (1.0 + ay * (kx**2)) ** 2
            for i in range(1, nmodes + 1):
                field_spectrum_out[j, i - 1] = 0.0
                gammaeff = 0.0
                if gamma0 > small:
                    if ky0 <= kP:  # initial quadratic
                        sig_ratio = (aoverb * (ky0**2) + ky0 + coverb) / (aoverb * (k0**2) + k0 + coverb)
                        field_spectrum_out[j, i - 1] = Ys[i - 1] * (sig_ratio**c_1) * Fky * (gp[j, i - 1] / gamma0) ** (2 * expsub)
                    elif ky0 <= kT:  # connecting quadratic
                        if YTs[i - 1] == 0.0 or kP == kT:
                            field_spectrum_out[j, i - 1] = 0.0
                        else:
                            doversig0 = ((Ys[i - 1] / YTs[i - 1]) ** (1.0 / abs(c_1))) - (
                                (aoverb * (kP**2) + kP + coverb - ((kP - kT) * (2 * aoverb * kP + 1)))
                                / (aoverb * (k0**2) + k0 + coverb)
                            )
                            doversig0 = doversig0 * (1.0 / ((kP - kT) ** 2))
                            eoversig0 = -2 * doversig0 * kP + ((2 * aoverb * kP + 1) / (aoverb * (k0**2) + k0 + coverb))
                            foversig0 = ((Ys[i - 1] / YTs[i - 1]) ** (1.0 / abs(c_1))) - eoversig0 * kT - doversig0 * (kT**2)
                            sig_ratio = doversig0 * (ky0**2) + eoversig0 * ky0 + foversig0
                            field_spectrum_out[j, i - 1] = Ys[i - 1] * (sig_ratio**c_1) * Fky * (gp[j, i - 1] / gamma0) ** (2 * expsub)
                    else:  # SAT2 for electron scale
                        gammaeff = gamma_mix1[j] * (gp[j, i - 1] / gamma0) ** expsub
                        if ky0 > kyetg:
                            gammaeff = gammaeff * np.sqrt(ky0 / kyetg)
                        field_spectrum_out[j, i - 1] = scal * measure * cnorm * ((gammaeff / (kx_width * ky0)) / (1.0 + ay * kx**2)) ** 2
                        if units_in != "GYRO":
                            field_spectrum_out[j, i - 1] = sat_geo_factor * field_spectrum_out[j, i - 1]
                # add these outputs
                gammaeff_out[j, i - 1] = gammaeff
                sig_ratio_out[j, i - 1] = sig_ratio
            kx_width_out[j] = kx_width
            sat_geo_factor_out[j] = sat_geo_factor

    # SAT3 QLA part
    QLA_P = 0.0
    QLA_E = 0.0
    if sat_rule_in == 3:
        QLA_P = np.zeros(nmodes)
        QLA_E = np.zeros(nmodes)
        for k in range(1, nmodes + 1):
            # factor of 2 included for real symmetry
            QLA_P[k - 1] = 2 * mode_transition_function(xs[k - 1], 1.1, 0.6, x_ITG, x_TEM)
            QLA_E[k - 1] = 2 * mode_transition_function(xs[k - 1], 0.75, 0.6, x_ITG, x_TEM)
        QLA_O = 2 * 0.8
    else:
        QLA_P = 1.0
        QLA_E = 1.0
        QLA_O = 1.0

    phinorm = field_spectrum_out
    # so the normal behavior doesn't change,
    if return_phi_params:
        out = dict(
            phinorm=phinorm,
            kx_width=kx_width_out,  # [nky] kx_model (kx rms width)
            gammaeff=gammaeff_out,  # [nky, nmodes] effective growthrate
            kx0_e=kx0_e,  # [nky] spectral shift in kx
            ax=ax,  # SAT1 (cx), SAT2 (alpha_x)
            ay=ay,  # SAT1 (cy)
            exp_ax=exp_ax,  # SAT2 (sigma_x)
            sat_geo_factor=sat_geo_factor_out,  # SAT2=G(theta)**2; SAT1=sat_geo0_out
        )
        if sat_rule_in == 2:
            # add G(theta) params,
            out.update(dict(d1=d1, d2=d2, kycut=kycut, b3=b3))
        if sat_rule_in == 3:
            out.update(dict(sig_ratio=sig_ratio_out, k0=k0))
    else:
        out = phinorm, QLA_P, QLA_E, QLA_O  # SAT123 intensity and QLA params
    return out


def reconstruct_kxky_phi(ky_grid, kx_grid, gammas, imode=0, theta_grid=None, make_plots=False, QL_data=None, **kw):
    '''Reconstruct the TGLF spectral shift model for the saturated potential spectrum.
    This function can be used for SAT1, SAT2, or SAT3 (experimental)
    The SAT2 SS-model also contains the \theta dim, the kxky_phi output may be thetakxky_phi (if len(theta_grid) > 1)

    :arg ky_grid: 1d np.array [nky], ky's from eigenvalue spectrum from TGLF run.

    :arg kx_grid: 1d np.array [nkx], kx's over which to reconstruct the kxky_phi spectrum.

    :arg gammas: 2d np.array [nky,nmodes], growthrates from eig.value spectrum from TGLF run.

    :kwarg imode: int, index of mode to use for reconstruction.

    :kwarg theta_grid: 1d np.array [ntheta], theta's over which to reconstruct (SAT2 only), None -> theta=0

    :kwarg QL_data: 5d np.array [ky, modes, species, fields, 5 (type)], QL (flux) weights used in SAT3 only.
        NOTE: type must be arranged: ["particle","energy","toroidal stress","parallel stress","exchange"]

    :kwarg make_plots: bool, for debugging.

    :kwarg **kw: input.tglf
    '''
    sat_rule_in = kw["SAT_RULE"]
    nmodes = kw["NMODES"]
    if sat_rule_in == 0:
        printe("ERROR: (reconstruct_kxky_phi) cannot reconstruct kxky_phi for SAT0")
        return
    elif sat_rule_in == 3:
        printw("WARN: (reconstruct_kxky_phi) SAT3 2D spectrum is underconstrained by design.")
        if QL_data is None:
            printe("ERROR: (reconstruct_kxky_phi) QL_data cannot be 'None' for SAT3")
            return
    if make_plots:
        import matplotlib.pyplot as plt

    if QL_data is None:
        # Not used by SAT1, 2
        # Must be shape: [ky, modes, species, fields, 5 (type)]
        QL_data = np.zeros((len(ky_grid), nmodes, 3, 3, 5))

    # call get_sat_params(),
    # NOTE: output has been expanded to include theta_out, Bt_out, grad_r_out, and B_unit_out.
    kx0_e, SAT_geo1_out, SAT_geo2_out, R_unit, Bt0_out, B_geo0_out, grad_r0_out, theta_out, Bt_out, grad_r_out, B_unit_out = get_sat_params(
        sat_rule_in, ky_grid, gammas.T, **kw
    )

    sat_params = dict(
        Bt0_out=Bt0_out,
        B_geo0_out=B_geo0_out,
        grad_r0_out=grad_r0_out,
        SAT_geo0_out=1.0,
        SAT_geo1_out=SAT_geo1_out,
        SAT_geo2_out=SAT_geo2_out,
    )

    # call intensity_sat(),
    # NOTE: the ouput is totally different when return_phi_params = True
    phi_params = intensity_sat(sat_rule_in, ky_grid, gammas, kx0_e, nmodes, QL_data=QL_data, return_phi_params=True, **sat_params, **kw)

    # --- --- --- SAT1 --- --- ---
    # eq. 13 of [1] Staebler et al. "New Paradigm..." (2013)
    #   - <k_x> is given around eq. 14 of [1]. kx0_e = spectral_shift_out = <kx>/ky
    #   - NOTE: kx_width = ky
    #   - ay (="cx/cy") constant = 0.56

    if sat_rule_in == 1:
        ay = 0.56
        phi2 = copy.deepcopy(phi_params["phinorm"][:, imode])
        # remove the geo-factor (for SAT1 sat_geo_factor = 1.0)
        phi2 /= phi_params["sat_geo_factor"]
        # remove the influence of evaluating at kx=<kx>,
        phi2 *= (1 + ay * kx0_e**2) ** 2
        kx_grid = np.atleast_2d(kx_grid).T  # broadcasting: [Nkx, 1]
        kx_factor = 1 + ay * kx0_e**2 + (ay / ky_grid**2) * (kx_grid - kx0_e * ky_grid) ** 2
        kxky_phi = np.sqrt(phi2) / kx_factor

    # --- --- --- SAT2 --- --- ---
    # eq. 34 of [1] Staebler et al. "Verification..." (2021).
    # Start with the |dphi|^2 = phinorm.
    # Remove the effect of evaluating at kx=kx0e and fs.averaging.
    # Then we re-inject the \theta and kx dependance.
    #
    # Therefore we need G(\theta), k_x0, k_x^model
    #   - kx0_e (="k_x0/ky") calculated by get_sat_params.
    #   - kx_width (="k_x^model") calculated by intensity_sat (eq. 21 of [1])
    #   - G(theta) is calculated below, more complicated becase sat_geo_factor includes a fs.avg.

    if sat_rule_in == 2:
        phi2 = copy.deepcopy(phi_params["phinorm"][:, imode])
        kx0 = kx0_e * ky_grid
        # remove the applied geo-factor:
        # NOTE: this factor is basically <G(\theta)^2>_theta
        phi2 /= phi_params["sat_geo_factor"]
        # remove the influence of evaluating at kx=kx0e,
        phi2 *= (1 + (kx0 / phi_params["kx_width"]) ** 2) ** 2
        kx_grid = np.atleast_2d(kx_grid).T  # broadcasting: [Nkx, 1]
        kx_factor = 1 + (kx0 / phi_params["kx_width"]) ** 2 + ((kx_grid - kx0) / phi_params["kx_width"]) ** 2
        kxky_phi = np.sqrt(phi2) / kx_factor

        # eqs. 16-20 of [1]
        # See also [2] Staebler et al. "Geometry dependence..." (2021)
        # Compute the geometry factor from scratch,
        if theta_grid is None:
            theta_grid = np.array([0.0])

        ntheta = len(theta_grid)
        nky = len(ky_grid)

        # apply eq. 19, 20 of [1]
        G1 = (B_geo0_out / Bt_out) ** 4  # = (B(0)/B(theta))**4
        Gq = grad_r_out * B_unit_out / Bt_out  # = |grad r|*B_unit/B(theta)
        Gq = 1 / Gq  # WARNING: There is a typo in [1], it's correct in [2]
        G2 = (Gq[0] / Gq) ** 4  # = (Gq(0)/Gq(theta))**4

        if make_plots:
            fig, ax = plt.subplots(1, 1, num="G-Factors SAT2")
            ax.plot(theta_out / np.pi, G1, label=r'$G_1(\theta)$')
            ax.plot(theta_out / np.pi, Gq, label=r'$G_q(\theta)$')
            ax.plot(theta_out / np.pi, G2, label=r'$G_2(\theta)$')
            ax.axhline(1.0, ls='--', color='k')  # both G1, G2 need to go to 1 at theta = 0.
            ax.set_xlabel(r"$\theta/\pi$")
            ax.legend()

        # Interpolate G1, G2 onto the target theta grid,
        from scipy.interpolate import interp1d

        G1 = interp1d(theta_out, G1)(theta_grid)
        G2 = interp1d(theta_out, G2)(theta_grid)

        G_theta = np.zeros((ntheta, nky))
        for i, ky0 in enumerate(ky_grid):
            if ky0 < phi_params["kycut"]:
                G_theta[:, i] = np.sqrt(phi_params["d1"] * G1)
            else:
                term1 = phi_params["d1"] * G1 * phi_params["kycut"]
                term2 = phi_params["b3"] * phi_params["d2"] * G2 * (ky0 - phi_params["kycut"])
                G_theta[:, i] = np.sqrt((term1 + term2) / ky0)

        # Following broadcasting rules we have,
        #   G_theta: [ntheta,nky]
        #   kxky_phi: [nkx,nky]
        # Make G_theta: [ntheta, 1, nky ] and kxky_phi [1, nkx, nky]
        # The result will be [ntheta, nkx, nky] (or squeezed to [nkx, nky])
        kxky_phi = np.atleast_2d(np.squeeze(kxky_phi[np.newaxis, :, :] * G_theta[:, np.newaxis, :]))

    # --- --- --- SAT3 --- --- ---
    # eq. 17 of Dudding et al. "A new quasilinear..." (2022).
    # SAT3 is completely different, the spectral shift and absolute 2D peak are not directly modeled.
    # Our approach is to FIX: <kx> and <|dphi|^2> at kx=<kx>, ky=k0
    # Then we use a nonlinear equation solver (scipy.optimize.fsolve) to build the 2D phi(kx, ky) spectrum.
    if sat_rule_in == 3:
        # The 1D potential spectrum (summed over kx and fs-avg.)
        phi2 = copy.deepcopy(phi_params["phinorm"][:, imode])
        peak_phi2_k0 = 1.0  # = <|dphi|^2> at kx=<kx>, ky=k0 (Numerator of Dudding eq. 17 eval at ky=k0)
        kx_shift = 0.0  # = <kx> In the future this can be kx0e
        printw(f"WARN: (reconstruct_kxky_phi) fixing <kx>={kx_shift} and <|phi|^2>(kx=<kx>;ky=k0) = {peak_phi2_k0}")
        # get the sig_ratio from the phi_params,
        sig_ratio = phi_params["sig_ratio"][:, imode]
        # given the selected value of peak_phi2_k0, we solve for sigma_ky=k0
        from scipy.interpolate import interp1d

        phi2_k0 = interp1d(ky_grid, phi2)(phi_params["k0"])
        phi2_ratio = peak_phi2_k0 / phi2_k0
        dkxi = 0.1
        kxi = np.arange(-4, 4 + dkxi, dkxi)

        def target_func(sigky0):
            c1 = 1 / sigky0**2 * ((np.pi * sigky0 * phi2_ratio / dkxi) ** 2 - 2)  # Equation 14 in Dudding.
            return np.sum(1 + c1 * (kxi - kx_shift) ** 2 + (kxi - kx_shift) ** 4 / sigky0**4) - phi2_ratio

        from scipy.optimize import fsolve

        print(f"INFO: (reconstruct_kxky_phi) solving for sigma_ky=k0 using...")
        print(f"\t k0 = {phi_params['k0']:.3f}")
        print(f"\t phinorm(ky=k0) = {phi2_k0:.3f}")
        print(f"\t init. guess = {min(sig_ratio):.3f}")
        sigky0 = fsolve(target_func, min(sig_ratio), maxfev=1000)[0]
        print(f"INFO: (reconstruct_kxky_phi) sigky0 = {sigky0}")
        # With this one value of sigma_ky=k0 we get all the values of sigma_ky,
        sigma_ky = sig_ratio * sigky0
        kxi = np.atleast_2d(kxi).T  # for broadcasting.

        def target_func(peak_phi2):
            c1 = 1 / sigma_ky**2 * ((np.pi * sigma_ky * peak_phi2 / phi2 / dkxi) ** 2 - 2)
            return peak_phi2 * np.sum(1 / (1 + c1 * (kxi - kx_shift) ** 2 + (kxi - kx_shift) ** 4 / sigma_ky**4), axis=0) - phi2

        # vectorized fsolve,
        print(f"INFO: (reconstruct_kxky_phi) solving for phi2(kx=<kx>,ky) using...")
        print(f"\t init. guess = phi2/Nky")
        peak_phi2 = fsolve(target_func, phi2 / len(ky_grid), maxfev=1000)

        # Now we can build the final function,
        c1 = 1 / sigma_ky**2 * ((np.pi * sigma_ky * peak_phi2 / phi2 / dkxi) ** 2 - 2)
        kx_grid = np.atleast_2d(kx_grid).T  # [Nkx, 1]
        kxky_phi = np.sqrt(peak_phi2 / (1 + c1 * (kx_grid - kx_shift) ** 2 + (kx_grid - kx_shift) ** 4 / sigma_ky**4))

    # NORMALIZATION: the kxky_phi matrix has the GB-norm.
    # to obtain "real" units it should be multiplied by: (rho_s,unit * Te) / (a * e)

    if make_plots:
        fig, ax = plt.subplots(1, 1, num=f"omfit_tglf.py: reconstruct_kxky_phi (mode_num={imode+1})")
        if sat_rule_in == 1:
            txt = ""
            phinorm_txt = r"$\sqrt{\langle|\delta\phi|^2(k_{x0e},ky)\rangle_\theta}$"
            ax.semilogx(ky_grid, kx0_e, 'g-', label=r'$k_{x,0}^e$')
        elif sat_rule_in == 2:
            theta0 = theta_grid[0] * 180 / np.pi
            txt = rf"$|_{{\theta={theta0:.1f}^\circ}}$"
            phinorm_txt = r"$\sqrt{\langle|\delta\phi|^2(k_{x0e},ky)\rangle_\theta}$"
            ax.semilogx(ky_grid, phi_params["sat_geo_factor"], '--', color="orange", label=r"$\langle G^2(\theta)\rangle_\theta$")
            ax.semilogx(ky_grid, G_theta[0, :], color='orange', label=rf'G($\theta={theta0:.1f}^\circ$)')
            ax.semilogx(ky_grid, kx0_e, 'g-', label=r'$k_{x,0}^e$')
            ax.semilogx(ky_grid, phi_params['kx_width'] / 10, 'r-', label=r'$k_{x,width}/10$')
        elif sat_rule_in == 3:
            txt = ""
            phinorm_txt = r"$\sqrt{\langle|\delta\phi|^2(k_y)\rangle_{x,\theta}}$"
            ax.semilogx(ky_grid, sigma_ky, color='orange', label=rf'$\sigma_{{ky}}$ | $\sigma_{{ky=k0}}$={sigky0:.2f}')
        # Always plot the 1D potential spectrum output by TGLF (sqrt)
        ax.semilogx(ky_grid, np.sqrt(phi_params["phinorm"][:, imode]), 'k-', label=phinorm_txt)
        # Always plot the kx=0 slice,
        ikx0 = np.argmin(abs(np.squeeze(kx_grid)))
        if kxky_phi.ndim == 3:
            ax.semilogx(ky_grid, kxky_phi[0, ikx0, :], 'b-', lw=3, label=r'$|\delta\phi|(0,k_y)$' + txt)
        else:
            ax.semilogx(ky_grid, kxky_phi[ikx0, :], 'b-', lw=3, label=r'$|\delta\phi|(0,k_y)$' + txt)

        ax.set_xlabel(r"$k_y$")
        ax.axhline(0, ls='--', color='k')
        ax.legend()

    return kxky_phi


def reconstruct_kxky_n(
    ky_grid,
    kx_grid,
    gammas,
    field_spectrum,
    intensity_spectrum,
    theta_grid=None,
    ispecies=0,
    imode=0,
    sum_modes=False,
    interp0=True,
    make_plots=False,
    **kw,
):
    '''Reconstruct the fluctuating density spectrum: kxky_n using,
        - the TGLF spectral shift model for the saturated potential spectrum (kxky_phi)
        - the QL weights for the density field
    Assumptions: the QL weights are independant of kx, theta (SAT2 only).

    :arg ky_grid: (np.array) [nky], ky's from eigenvalue spectrum from TGLF run.

    :arg kx_grid: (np.array) [nkx], kx's over which to reconstruct the kxky_phi spectrum.
        Hint: use something like: kx_grid = np.linspace(-4, 4, 64)

    :arg gammas: (np.array) [nky,nmodes], growthrates from eigenvvalue spectrum from TGLF run.

    :arg field_spectrum: (OMFITtglf_potential_spectrum) object from TGLF Experimental_spectra

    :arg intensity_spectrum: (OMFITtglf_intensity_spectrum) object from TGLF Experimental_spectra

    :kwarg theta_grid: (None or np.array) of theta values in [-2pi, 0], if None theta=0 is used.

    :kwarg ispecies: (int) species index for field, intensity spectra. electrons=0

    :kwarg imode: (int) mode_num index for field, intensity spectra.

    :kwarg sum_modes: (bool) sum over modes, if True the value of imode is irrelevant.

    :kwarg interp0: (bool) option to interpolate over zeros in the middle of the potential spectrum.

    :kwarg make_plots: (bool) for debugging.

    :kwarg **kw: input.tglf
    '''
    if interp0:
        from scipy.interpolate import interp1d
    if sum_modes:
        nmodes = kw["NMODES"]
        mode_inds = range(nmodes)
    else:
        nmodes = 1
        mode_inds = [imode]

    # To safeguard overwriting when masking.
    field_spectrum = copy.deepcopy(field_spectrum)
    intensity_spectrum = copy.deepcopy(intensity_spectrum)

    if make_plots:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, nmodes, num="omfit_tglf.py: reconstruct_kxky_n", sharex=True, sharey=True, squeeze=False)
        ax = ax.flatten()

    sum_kxky_n2 = 0.0
    for im in mode_inds:
        kxky_phi = reconstruct_kxky_phi(ky_grid, kx_grid, gammas, imode=im, theta_grid=theta_grid, make_plots=make_plots, **kw)
        # QL Weights for the density field are backed-out of other TGLF outputs,
        phi_bar_out = field_spectrum["potential"].isel(mode_num=im).data  # (nky,)
        n_intensity = intensity_spectrum["density"].isel(mode_num=im, species=ispecies).data  # (nky,)

        # n_weights is a reconstruction of the TGLF variable "N_weight"
        # "N_weight" is calculated in: tglf_LS.f90: subroutine get_QL_weights
        # Formally, for each ky, mode, and species we compute:
        #       N_weight[is] = SUM(j->N_BASIS) |dn[is,j]|^2 ! dn comes from the TGLF eigenvector.
        #       N_weight /= phi_norm ! phi_norm = SUM(j->N_BASIS) |dphi[j]|^2
        # cf. eq. 4 of Staebler et al. "Verification..." (2021).

        # TGLF does not write N_weight to a file (yet)... but it does write,
        #       intensity_spectrum_out(1, is, iky, imode) = phi2_bar*N_weight
        #       field_spectrum_out(2, iky, imode) = phi2_bar = phi_bar_out

        # To avoid div-by-zero,
        bad = phi_bar_out == 0
        if any(bad):
            printw(f"WARN: (reconstruct_kxky_n) zeros found in potential_spectrum for ky = {ky_grid[bad]}")
            if interp0:
                printw("WARN: (reconstruct_kxky_n) interpolating over zeros in potential_spectrum")
                phi_bar_out = interp1d(
                    ky_grid[~bad],
                    phi_bar_out[~bad],
                    bounds_error=False,
                    fill_value=np.nan,  # if there are zeros at the boundary we make them NaNs (then set to zero in n_weights)
                )(ky_grid)
            else:
                # fill with NaN,
                phi_bar_out[bad] = np.nan * phi_bar_out[bad]
        bad = n_intensity == 0
        if any(bad):
            printw(f"WARN: (reconstruct_kxky_n) zeros found in intensity_spectrum for ky = {ky_grid[bad]}")
            if interp0:
                printw("WARN: (reconstruct_kxky_n) interpolating over zeros in intensity_spectrum")
                n_intensity = interp1d(
                    ky_grid[~bad],
                    n_intensity[~bad],
                    bounds_error=False,
                    fill_value=np.nan,  # if there are zeros at the boundary we make them NaNs (then set to zero in n_weights)
                )(ky_grid)
            else:
                # fill with NaN,
                n_intensity[bad] = np.nan * n_intensity[bad]

        n_weights = n_intensity / phi_bar_out  # (nky,)
        # send NaN's to zero,
        n_weights = np.nan_to_num(n_weights)

        # Work with the square of the density spectrum until the end,
        kxky_n2 = n_weights * np.square(kxky_phi)  # (nky,) * ([ntheta], nkx, nky) --> ([ntheta], nkx, nky)
        # NORMALIZATION: this kxky_n matrix has the GB-norm.
        # to obtain "real" units it should be multiplied by: ne*(rho_s,unit/a)
        sum_kxky_n2 += kxky_n2

        if make_plots:
            ikx = np.argmin(abs(kx_grid))  # kx = 0
            ax[im].semilogx(ky_grid, phi_bar_out, 'b-', label="potential_spectrum")  # <|dphi|^2>
            ax[im].semilogx(ky_grid, n_intensity, 'g-', label="intensity_spectrum")  # <|dn|^2>
            ax[im].semilogx(ky_grid, n_weights, 'k-', label="QL n-weights")  # <|dn|^2>/<|dphi|^2>
            ax[im].axhline(1.0, ls='--', color='k')
            if kxky_n2.ndim == 3:
                itheta = 0
                txt = fr"$|_{{\theta={theta_grid[itheta]*180/np.pi:.1f}^\circ}}$"
                ax[im].semilogx(ky_grid, kxky_n2[itheta, ikx, :], 'r-', label=r"$|\delta n|^2$" + txt)
            else:
                ax[im].semilogx(ky_grid, kxky_n2[ikx, :], 'r-', label=r"$|\delta n|^2$")
            ax[im].set_xlabel(r"$k_y$")
            ax[im].set_title(f"mode_num={im+1}")

    if make_plots:
        ax[0].legend()

    # Note that we sum the squares of the modes, this is also done by TGLF when it creates the "density spectrum" object.
    kxky_n = np.sqrt(sum_kxky_n2)
    return kxky_n


def reconstruct_kxky_T(
    ky_grid, kx_grid, gammas, field_spectrum, intensity_spectrum, ispecies=-1, imode=0, theta_grid=None, make_plots=False, **kw
):
    '''Reconstruct the 2D fluctuating temperature spectrum: kxky_T using,
        - the TGLF spectral shift model for the saturated potential spectrum (kxky_phi)
        - the QL phase shifts of the temperature field
    This function is an extension of the method above (reconstruct_kxky_phi).
    See the :arg, :kwarg definitions above.

    :arg field_spectrum: OMFITtglf_potential_spectrum object.
    :arg intensity_spectrum: OMFITtglf_intensity_spectrum object.
    :kwarg ispecies: int, used to select the proper field for QL weights.
    '''

    kxky_phi = reconstruct_kxky_phi(ky_grid, kx_grid, gammas, imode=imode, theta_grid=theta_grid, make_plots=make_plots, **kw)

    # The TGLF output files: "out.tglf.intensity_spectrum", and "out.tglf.field_spectrum"
    # are needed to calculate the QL weights.
    phi_bar_out = field_spectrum["potential"].data[imode, :]  # (nky,)
    T_intensity = intensity_spectrum["temperature"].data[imode, :, ispecies]  # (nky,)

    # T_weights is a reconstruction of the TGLF variable "T_weight"
    # "T_weight" is calculated in: tglf_LS.f90: subroutine get_QL_weights
    # Formally, for each ky, mode, and species we compute:
    #       T_weight[is] = SUM(j->N_BASIS) |dtemp[is,j]|^2 ! wherein, dtemp = dpress - dn
    #       T_weight /= phi_norm ! phi_norm = SUM(j->N_BASIS) |dphi[j]|^2
    # cf. eq. 4 of Staebler et al. "Verification..." (2021).

    # TGLF does not write T_weight to a file... but it does write,
    #       intensity_spectrum_out(2, is, iky, imode) = phi2_bar*T_weight
    #       field_spectrum_out(2, iky, imode) = phi2_bar = phi_bar_out

    # To avoid div-by-zero,
    bad = phi_bar_out == 0
    if any(bad):
        printw("! zeros found in potential_spectrum - interpolate/extrapolate")
        from scipy.interpolate import interp1d

        phi_bar_out = interp1d(ky_grid[~bad], phi_bar_out[~bad], bounds_error=False, fill_value='extrapolate')(ky_grid)

    T_weights = T_intensity / phi_bar_out  # (nky,)

    # ASSUME: QL weights are independent of kx, theta
    # Take sqrt() to get "T" instead of T^2.
    kxky_T = np.sqrt(T_weights) * kxky_phi  # (nky,) * (nkx, nky, [ntheta]) --> (nkx, nky, [ntheta])

    # NORMALIZATION: this kxky_T matrix has the GB-norm.
    # to obtain "real" units it should be multiplied by: (rho_s,unit * Te) / a

    if make_plots:
        fig, ax = plt.subplots(1, 1, num="reconstruct_kxky_T")
        ax.semilogx(ky_grid, phi_bar_out, label='potential_spectrum')
        ax.semilogx(ky_grid, T_intensity, label='intensity_spectrum')
        ax.semilogx(ky_grid, T_weights, 'k-', lw=2, label='QL T-weights')
        ax.axhline(1.0, ls='--', color='k')  # N_weights = 1 --> no phase shift.
        ax.legend()

    return kxky_T


def flux_integrals(
    NM,
    NS,
    NF,
    i,
    ky,
    dky0,
    dky1,
    particle,
    energy,
    toroidal_stress,
    parallel_stress,
    exchange,
    particle_flux_out,
    energy_flux_out,
    stress_tor_out,
    stress_par_out,
    exchange_out,
    q_low_out,
    taus_1=1.0,
    mass_2=1.0,
):
    '''
    Compute the flux integrals
    '''
    for nm in range(NM):
        for ns in range(NS):
            for j in range(NF):
                particle_flux_out[nm][ns][j] += dky0 * (0 if i == 0 else particle[i - 1][nm][ns][j]) + dky1 * particle[i][nm][ns][j]
                energy_flux_out[nm][ns][j] += dky0 * (0 if i == 0 else energy[i - 1][nm][ns][j]) + dky1 * energy[i][nm][ns][j]
                stress_tor_out[nm][ns][j] += (
                    dky0 * (0 if i == 0 else toroidal_stress[i - 1][nm][ns][j]) + dky1 * toroidal_stress[i][nm][ns][j]
                )
                stress_par_out[nm][ns][j] += (
                    dky0 * (0 if i == 0 else parallel_stress[i - 1][nm][ns][j]) + dky1 * parallel_stress[i][nm][ns][j]
                )
                exchange_out[nm][ns][j] += dky0 * (0 if i == 0 else exchange[i - 1][nm][ns][j]) + dky1 * exchange[i][nm][ns][j]
            if ky * taus_1 * mass_2 <= 1:
                q_low_out[nm][ns] = energy_flux_out[nm][ns][0] + energy_flux_out[nm][ns][1]
    return particle_flux_out, energy_flux_out, stress_tor_out, stress_par_out, exchange_out, q_low_out


def sum_ky_spectrum(
    sat_rule_in,
    ky_spect,
    gp,
    ave_p0,
    R_unit,
    kx0_e,
    potential,
    particle_QL,
    energy_QL,
    toroidal_stress_QL,
    parallel_stress_QL,
    exchange_QL,
    etg_fact=1.25,
    c0=32.48,
    c1=0.534,
    exp1=1.547,
    cx_cy=0.56,
    alpha_x=1.15,
    **kw,
):
    '''
    Perform the sum over ky spectrum
    The inputs to this function should be already weighted by the intensity function

    nk --> number of elements in ky spectrum
    nm --> number of modes
    ns --> number of species
    nf --> number of fields (1: electrostatic, 2: electromagnetic parallel, 3:electromagnetic perpendicular)

    :param sat_rule_in:

    :param ky_spect: k_y spectrum [nk]

    :param gp: growth rates [nk, nm]

    :param ave_p0: scalar average pressure

    :param R_unit: scalar normalized major radius

    :param kx0_e: spectral shift of the radial wavenumber due to VEXB_SHEAR [nk]

    :param potential: input potential fluctuation spectrum  [nk, nm]

    :param particle_QL: input particle fluctuation spectrum [nk, nm, ns, nf]

    :param energy_QL: input energy fluctuation spectrum [nk, nm, ns, nf]

    :param toroidal_stress_QL: input toroidal_stress fluctuation spectrum [nk, nm, ns, nf]

    :param parallel_stress_QL: input parallel_stress fluctuation spectrum [nk, nm, ns, nf]

    :param exchange_QL: input exchange fluctuation spectrum [nk, nm, ns, nf]

    :param etg_fact: scalar TGLF SAT0 calibration coefficient [1.25]

    :param c0: scalar TGLF SAT0 calibration coefficient [32.48]

    :param c1: scalar TGLF SAT0 calibration coefficient [0.534]

    :param exp1: scalar TGLF SAT0 calibration coefficient [1.547]

    :param cx_cy: scalar TGLF SAT0 calibration coefficient [0.56] (from TGLF 2008 POP Eq.13)

    :param alpha_x: scalar TGLF SAT0 calibration coefficient [1.15] (from TGLF 2008 POP Eq.13)

    :param \**kw: any additional argument should follow the naming convention of the TGLF_inputs

    :return: dictionary with summations over ky spectrum:
            * particle_flux_integral: [nm, ns, nf]
            * energy_flux_integral: [nm, ns, nf]
            * toroidal_stresses_integral: [nm, ns, nf]
            * parallel_stresses_integral: [nm, ns, nf]
            * exchange_flux_integral: [nm, ns, nf]
    '''
    phi_bar_sum_out = 0
    NM = len(energy_QL[0, :, 0, 0])  # get the number of modes
    NS = len(energy_QL[0, 0, :, 0])  # get the number of species
    NF = len(energy_QL[0, 0, 0, :])  # get the number of fields
    particle_flux_out = np.zeros((NM, NS, NF))
    energy_flux_out = np.zeros((NM, NS, NF))
    stress_tor_out = np.zeros((NM, NS, NF))
    stress_par_out = np.zeros((NM, NS, NF))
    exchange_out = np.zeros((NM, NS, NF))
    q_low_out = np.zeros((NM, NS))

    QLA_P = 1
    QLA_E = 1
    QLA_O = 1
    QL_data = np.stack([particle_QL, energy_QL, toroidal_stress_QL, parallel_stress_QL, exchange_QL], axis=4)

    # Multiply QL weights with desired intensity
    if sat_rule_in in [0.0, 0, 'SAT0']:
        intensity_factor = (
            intensity_sat0(ky_spect, gp, ave_p0, R_unit, kx0_e, etg_fact, c0, c1, exp1, cx_cy, alpha_x)
            * potential
            / intensity_sat0(ky_spect, gp, ave_p0, R_unit, kx0_e, 1.25, 32.48, 0.534, 1.547, 0.56, 1.15)
        )
    elif sat_rule_in in [1.0, 1, 'SAT1', 2.0, 2, 'SAT2', 3.0, 3, 'SAT3']:
        intensity_factor, QLA_P, QLA_E, QLA_O = intensity_sat(sat_rule_in, ky_spect, gp, kx0_e, NM, QL_data, **kw)
    elif sat_rule_in in [-1.0, -1, 'DESAT']:
        intensity_factor = (
            intensity_desat(ky_spect, kw['P_PRIME_LOC'], kw['Q_LOC'], kw['TAUS_2'])
            * potential
            / intensity_sat0(ky_spect, gp, ave_p0, R_unit, kx0_e, 1.25, 32.48, 0.534, 1.547, 0.56, 1.15)
        )
    else:
        raise ValueError("sat_rule_in must be [0.0, 0, 'SAT0'] or [1.0, 1, 'SAT1']")

    shapes = [item.shape for item in [particle_QL, energy_QL, toroidal_stress_QL, parallel_stress_QL, exchange_QL] if item is not None][0]

    particle = np.zeros(shapes)
    energy = np.zeros(shapes)
    toroidal_stress = np.zeros(shapes)
    parallel_stress = np.zeros(shapes)
    exchange = np.zeros(shapes)

    for i in range(NS):  # iterate over the species
        for j in range(NF):  # iterate over the fields
            if particle_QL is not None:
                particle[:, :, i, j] = particle_QL[:, :, i, j] * intensity_factor * QLA_P
            if energy_QL is not None:
                energy[:, :, i, j] = energy_QL[:, :, i, j] * intensity_factor * QLA_E
            if toroidal_stress_QL is not None:
                toroidal_stress[:, :, i, j] = toroidal_stress_QL[:, :, i, j] * intensity_factor * QLA_O
            if parallel_stress_QL is not None:
                parallel_stress[:, :, i, j] = parallel_stress_QL[:, :, i, j] * intensity_factor * QLA_O
            if exchange_QL is not None:
                exchange[:, :, i, j] = exchange_QL[:, :, i, j] * intensity_factor * QLA_O

    dky0 = 0
    ky0 = 0
    for i in range(len(ky_spect)):
        ky = ky_spect[i]
        ky1 = ky
        if i == 0:
            dky1 = ky1
        else:
            dky = np.log(ky1 / ky0) / (ky1 - ky0)
            dky1 = ky1 * (1.0 - ky0 * dky)
            dky0 = ky0 * (ky1 * dky - 1.0)

        particle_flux_out, energy_flux_out, stress_tor_out, stress_par_out, exchange_out, q_low_out = flux_integrals(
            NM,
            NS,
            NF,
            i,
            ky,
            dky0,
            dky1,
            particle,
            energy,
            toroidal_stress,
            parallel_stress,
            exchange,
            particle_flux_out,
            energy_flux_out,
            stress_tor_out,
            stress_par_out,
            exchange_out,
            q_low_out,
        )
        ky0 = ky1
        results = {
            "particle_flux_integral": particle_flux_out,
            "energy_flux_integral": energy_flux_out,
            "toroidal_stresses_integral": stress_tor_out,
            "parallel_stresses_integral": stress_par_out,
            "exchange_flux_integral": exchange_out,
        }
    return results

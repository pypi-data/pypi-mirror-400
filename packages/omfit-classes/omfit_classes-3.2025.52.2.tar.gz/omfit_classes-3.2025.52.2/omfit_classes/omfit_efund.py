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

from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.fluxSurface import rz_miller
from omfit_classes.omfit_eqdsk import OMFITgeqdsk
from omfit_classes.namelist import NamelistName
import numpy as np
import fortranformat
from omfit_classes.utils_fusion import tokamak
import omas

__all__ = ['OMFITmhdin', 'OMFITdprobe', 'OMFITnstxMHD', 'get_mhdindat', 'green_to_omas']


class OMFITmhdin(OMFITnamelist):
    scaleSizes = 50
    invalid = 99

    @dynaLoad
    def load(self, *args, **kw):
        r"""
        Load OMFITmhdin file

        :param \*args: arguments passed to OMFITnamelist.load()

        :param \**kw: keyword arguments passed to OMFITnamelist.load()
        """

        # load namelist
        self.outsideOfNamelistIsComment = True
        self.noSpaceIsComment = True
        super().load(*args, **kw)
        if 'IN3' not in self:
            self['IN3'] = NamelistName()
        if 'MACHINEIN' not in self:
            self['MACHINEIN'] = NamelistName()
        # out-of-namelist format (DIII-D)

        if (
            'RF' not in self['IN3']
            or 'RSI' not in self['IN3']
            or 'RE' not in self['IN3']
            and self['IN3'].get('IECOIL', 0)
            or 'RVS' not in self['IN3']
            and self['IN3'].get('IVESEL', 0)
        ):
            comment_items = list(self.keys())
            for comment_item in comment_items:
                if '__comment' in comment_item and not isinstance(self, OMFITdprobe):

                    fformat = {}
                    fformat['FC'] = fortranformat.FortranRecordReader('(6e12.6)')
                    fformat['FLOOP'] = fortranformat.FortranRecordReader('(6e12.6)')
                    fformat['OH'] = fortranformat.FortranRecordReader('(5e10.4)')
                    fformat['VESSEL'] = fortranformat.FortranRecordReader('(6e12.6)')

                    lines = str(self[comment_item])

                    tmp = lines.split('comment')
                    if len(tmp) > 1:
                        lines, comment = tmp
                    else:
                        lines = tmp[0]
                        comment = ''
                    del self[comment_item]
                    lines = lines.split('\n')
                    lines = [line.expandtabs(12) for line in lines if len(line.strip()) and line.strip()[0] != '!']

                    # number of elements per section
                    if len(self['MACHINEIN']) > 0:
                        nfc = self['MACHINEIN'].get("nfcoil", 18)
                        nfl = self['MACHINEIN'].get("nsilop", 44)
                        ntf = self['MACHINEIN'].get("necoil", 122)
                        nve = self['MACHINEIN'].get("nvesel", 24)
                    else:
                        if 'FCID' not in self['IN3']:
                            raise ValueError('mhdin format not recognized')
                        nfc = len(self['IN3']['FCID'])
                        ntf = len(self['IN3']['ECTURN'])
                        nve = len(self['IN3']['VSID'])

                    if 'RF' in self['IN3']:
                        nfc = 0
                    if 'RE' in self['IN3'] or not self['IN5'].get('IECOIL', 0):
                        ntf = 0
                    if 'RVS' in self['IN3'] or not self['IN5'].get('IVESEL', 0):
                        nve = 0
                    if 'RSI' in self['IN3']:
                        nfl = 0
                    elif len(self['MACHINEIN']) == 0:
                        nfl = len(lines) - nfc - nve - ntf  # No better way to determine this unfortunately

                    if len(lines) - nfc - nfl - nve - ntf:
                        raise ValueError('mhdin format not recognized')

                    # poloidal field coils
                    # R,Z,DR,DZ,skew_angle1,skew_angle2
                    kk = 0
                    if not nfc:
                        self['FC'] = np.array([])
                    else:
                        self['FC'] = {}
                        for k in range(nfc):
                            lines[kk] += '%12d%12d' % (0, 0)
                            data = fformat['FC'].read(lines[kk])

                            # data[4] = '0.0' if not data[4].strip() or float(data[4]) == 0 else data[4]
                            # data[5] = '90.0' if not data[5].strip() or float(data[5]) == 0 else data[5]
                            data = np.array(list(map(float, data)))
                            self['FC']['%d' % (k + 1)] = data
                            kk += 1
                        self['FC'] = np.array(self['FC'].values())

                    # flux loops
                    # R,Z,DR,DZ,skew_angle1,skew_angle2
                    if not nfl:
                        self['FLOOP'] = np.array([])
                    else:
                        self['FLOOP'] = {}
                        for k in range(nfl):
                            lines[kk] += '%12d%12d' % (0, 0)
                            data = fformat['FLOOP'].read(lines[kk])
                            # data[4] = '0.0' if not data[4].strip() or float(data[4]) == 0 else data[4]
                            # data[5] = '90.0' if not data[5].strip() or float(data[5]) == 0 else data[5]
                            data = np.array(list(map(float, data)))
                            self['FLOOP']['%d' % (k + 1)] = data
                            kk += 1
                        self['FLOOP'] = np.array(self['FLOOP'].values())

                    # ohmic coils
                    # R,Z,DR,DZ,block
                    if not ntf:
                        self['OH'] = np.array([])
                    else:
                        self['OH'] = {}
                        for k in range(ntf):
                            data = fformat['OH'].read(lines[kk])
                            self['OH']['%d' % (k + 1)] = data
                            kk += 1
                        self['OH'] = np.array(self['OH'].values())

                    # conducting vessel segments
                    # R,Z,DR,DZ,skew_angle1,skew_angle2
                    if not nve:
                        self['VESSEL'] = np.array([])
                    else:
                        self['VESSEL'] = {}
                        for k in range(nve):
                            lines[kk] += '%12d%12d' % (0, 0)
                            data = fformat['VESSEL'].read(lines[kk])
                            # data[4] = '0.0' if not data[4].strip() or float(data[4]) == 0 else data[4]
                            # data[5] = '90.0' if not data[5].strip() or float(data[5]) == 0 else data[5]
                            data = np.array(list(map(float, data)))
                            self['VESSEL']['%d' % (k + 1)] = data
                            kk += 1
                        self['VESSEL'] = np.array(self['VESSEL'].values())

                    # create namelist elements
                    if len(self['FC']):
                        self['IN3']['RF'] = self['FC'][:, 0]
                        self['IN3']['ZF'] = self['FC'][:, 1]
                        self['IN3']['WF'] = self['FC'][:, 2]
                        self['IN3']['HF'] = self['FC'][:, 3]
                        self['IN3']['AF'] = self['FC'][:, 4]
                        self['IN3']['AF2'] = self['FC'][:, 5]
                    if len(self['FLOOP']):
                        self['IN3']['RSI'] = self['FLOOP'][:, 0]
                        self['IN3']['ZSI'] = self['FLOOP'][:, 1]
                        self['IN3']['WSI'] = self['FLOOP'][:, 2]
                        self['IN3']['HSI'] = self['FLOOP'][:, 3]
                        self['IN3']['ASI'] = self['FLOOP'][:, 4]
                        self['IN3']['ASI2'] = self['FLOOP'][:, 5]
                    if len(self['OH']):
                        self['IN3']['RE'] = self['OH'][:, 0]
                        self['IN3']['ZE'] = self['OH'][:, 1]
                        self['IN3']['WE'] = self['OH'][:, 2]
                        self['IN3']['HE'] = self['OH'][:, 3]
                        self['IN3']['ECID'] = self['OH'][:, 4]
                    if len(self['VESSEL']):
                        self['IN3']['RVS'] = self['VESSEL'][:, 0]
                        self['IN3']['ZVS'] = self['VESSEL'][:, 1]
                        self['IN3']['WVS'] = self['VESSEL'][:, 2]
                        self['IN3']['HVS'] = self['VESSEL'][:, 3]
                        self['IN3']['AVS'] = self['VESSEL'][:, 4]
                        self['IN3']['AVS2'] = self['VESSEL'][:, 5]

        else:
            # initialize namelist
            for geom in ['R{element}', 'Z{element}', 'W{element}', 'H{element}', 'A{element}', 'A{element}2']:
                for element in ['E', 'F', 'VS']:
                    item = geom.format(element=element)
                    if item not in self['IN3'] and item not in ['AE', 'AE2']:
                        self['IN3'][item] = []

        if 'FC' in self:
            del self['FC']
        if 'FLOOP' in self:
            del self['FLOOP']
        if 'OH' in self:
            del self['OH']
        if 'VESSEL' in self:
            del self['VESSEL']

    @dynaSave
    def save(self, *args, **kw):
        r"""
        Save OMFITmhdin file

        :param \*args: arguments passed to OMFITnamelist.save()

        :param \**kw: keyword arguments passed to OMFITnamelist.save()
        """

        # remove non-namelist components
        angle2_special = {}
        for item in ['AF2', 'AVS2']:
            if item not in self['IN3']:
                continue
            self['IN3'][item] = np.atleast_1d(self['IN3'][item])
            angle2_special[item] = self['IN3'][item].copy()
            self['IN3'][item][self['IN3'][item] == 90] = 0.0

        # save namelist section
        # restore angles
        empty = []
        for k in list(self['IN3'].keys()):
            if isinstance(self['IN3'][k], (list, np.ndarray)) and not len(self['IN3'][k]):
                empty.append(k)
                del self['IN3'][k]

        super().save(*args, **kw)
        for k in list(empty):
            self['IN3'][k] = []

    @staticmethod
    def plot_coil(data, patch_facecolor='lightgray', patch_edgecolor='black', label=None, ax=None):
        """
        plot individual coil

        :param data: FC, OH, VESSEL data array row

        :param patch_facecolor: face color

        :param patch_edgecolor: edge color

        :param label: [True, False]

        :param ax: axis

        :return: matplotlib rectangle patch
        """
        import matplotlib.transforms as mtransforms
        from matplotlib import patches

        if ax is None:
            ax = pyplot.gca()

        rect = patches.Rectangle((0, 0), data[2], data[3], facecolor=patch_facecolor, edgecolor=patch_edgecolor)
        if len(data) == 6:
            angle1, angle2 = 90 - data[5], data[4]
            if angle1 == 90:
                angle1 = 0
            rect.set_transform(
                mtransforms.Affine2D().translate(-data[2] / 2.0, -data[3] / 2.0)
                + mtransforms.Affine2D().skew_deg(angle1, angle2)
                + mtransforms.Affine2D().translate(data[0], data[1])
                + ax.transData
            )
        else:
            rect.set_transform(
                mtransforms.Affine2D().translate(-data[2] / 2.0, -data[3] / 2.0)
                + mtransforms.Affine2D().translate(data[0], data[1])
                + ax.transData
            )
        ax.add_patch(rect)

        if label:
            ax.text(data[0], data[1], label, color='w', size=8, ha='center', va='center', zorder=1000, weight='bold', clip_on=True)
            ax.text(data[0], data[1], label, color='m', size=8, ha='center', va='center', zorder=1001, clip_on=True)
        return rect

    def plot_flux_loops(self, display=None, colors=None, label=False, ax=None):
        """
        plot the flux loops

        :param display: array used to turn on/off display individual flux loops

        :param colors: array used to set the color of individual flux loops

        :param label: [True, False]

        :param ax: axis
        """
        if 'RSI' not in self['IN3'] or not hasattr(self['IN3']['RSI'], '__len__'):
            return
        if ax is None:
            ax = pyplot.gca()
        x0 = self['IN3']['RSI']
        y0 = self['IN3']['ZSI']
        if colors is not None:
            c0 = np.squeeze(colors)[: len(x0)]
        if display is not None:
            s0 = np.squeeze((display != 0))[: len(x0)]
        else:
            s0 = np.ones(x0.shape)
        s0 *= self.scaleSizes

        # trim
        x0 = x0[: len(s0)]
        y0 = y0[: len(s0)]

        # disable plotting of dummy flux loops
        x0 = x0[np.where(y0 != -self.invalid)]
        y0 = y0[np.where(y0 != -self.invalid)]

        # plot
        if colors is not None:
            ax.scatter(x0, y0, s=s0, c=c0, vmin=0, vmax=vmax, marker='o', cmap=cm, alpha=0.75, zorder=100)
        else:
            ax.scatter(x0, y0, s=s0, color='b', marker='o', alpha=0.75, zorder=100)

        # labels
        if label and 'LPNAME' in self['IN3']:
            for k, name in enumerate(self['IN3']['LPNAME']):
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='w', zorder=1000, weight='bold', clip_on=True)
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='b', zorder=1001, clip_on=True)

    def plot_magnetic_probes(self, display=None, colors=None, label=False, ax=None):
        """
        plot the magnetic probes

        :param display: array used to turn on/off the display of individual magnetic probes

        :param colors: array used to set the color of individual magnetic probes

        :param label: [True, False]

        :param ax: axis
        """
        # The magnetic probes are characterized by:
        #  - XMP2 and
        #  - YMP2, cartesian coordinates of the center of the probe,
        #  - SMP2, size/length of the probe in meters (read below!),
        #  - AMP2, angle/orientation of the probe in degrees.
        #
        # the usual magnetic probe in EFIT is a partial rogowski coil,
        # yet beware! the EFIT D3D probe file also models saddle loops,
        # which extend in the toroidal direction and provide integrated
        # signals. such loops are characterized by a negative length.
        #
        # in order to plot non-rogowski coils correctly, a forced 90 deg
        # counter-clockwise rotation has to be applied on the probe's angle.
        #
        # the probes are plotted with different linestyles: rogowski coils
        # are plotted with a segment centered around a dot, whereas
        # saddle loops are plotted with a segment with dots on the endpoints.
        #
        # FURTHER REFERENCE as explained by T. Strait on 19-jul-2016
        #
        # - The angle AMP2 always indicates the direction of the magnetic field
        #   component that is being measured.
        #
        # - The length SMP2 indicates the length (in the R-Z plane) over which
        #   the magnetic field is averaged by the sensor.
        #
        # - SMP2 > 0 indicates that the averaging length is in the direction of AMP2.
        #   SMP2 < 0 indicates that the averaging length is perpendicular to AMP2.
        #
        # - In predicting the measurement of the sensor for purposes of fitting,
        #   only the length SMP2 is considered.  The width of the sensor in the
        #   direction perpendicular to SMP2 (in the R-Z plane) is small and is
        #   therefore neglected.
        #   Since the EFIT equilibrium is assumed to be axisymmetric, the width
        #   of the sensor in the toroidal direction is not relevant.
        #
        if 'XMP2' not in self['IN3'] or 'YMP2' not in self['IN3'] or 'SMP2' not in self['IN3'] or 'AMP2' not in self['IN3']:
            return
        if ax is None:
            ax = pyplot.gca()
        # first, get the arrays and make sure that their dimensions match
        x0 = np.squeeze(self['IN3']['XMP2'])
        y0 = np.squeeze(self['IN3']['YMP2'])
        l0 = np.squeeze(self['IN3']['SMP2'])
        a0 = np.squeeze(self['IN3']['AMP2'])
        if colors is not None:
            c0 = np.squeeze(colors)[: len(x0)]
        if display is not None:
            s0 = np.squeeze((display != 0))[: len(x0)]
        else:
            s0 = np.ones(x0.shape)
        s0 *= self.scaleSizes

        # trim
        x0 = x0[: len(s0)]
        y0 = y0[: len(s0)]
        l0 = l0[: len(s0)]
        a0 = a0[: len(s0)]

        # disable plotting of dummy probes
        l0 = l0[np.where(y0 != -self.invalid)]
        a0 = a0[np.where(y0 != -self.invalid)]
        x0 = x0[np.where(y0 != -self.invalid)]
        y0 = y0[np.where(y0 != -self.invalid)]

        def probe_endpoints(x0, y0, a0, l0):
            boo = (1 - np.sign(l0)) / 2.0
            cor = boo * np.pi / 2.0

            # then, compute the two-point arrays to build the partial rogowskis
            # as segments rather than single points, applying the correction
            px = x0 - l0 / 2.0 * np.cos(a0 * np.pi / 180.0 + cor)
            py = y0 - l0 / 2.0 * np.sin(a0 * np.pi / 180.0 + cor)
            qx = x0 + l0 / 2.0 * np.cos(a0 * np.pi / 180.0 + cor)
            qy = y0 + l0 / 2.0 * np.sin(a0 * np.pi / 180.0 + cor)

            segx = []
            segy = []
            for k in range(len(x0)):
                segx.append([px[k], qx[k]])
                segy.append([py[k], qy[k]])
            return segx, segy

        # finally, plot
        segx, segy = probe_endpoints(x0, y0, a0, l0)
        for k in range(len(x0)):
            if colors is None:
                col = 'r'
            else:
                col = cm(c0[k])
            if l0[k] > 0:
                ax.plot(segx[k], segy[k], '-', lw=2, color=col, zorder=100, alpha=0.75)
                ax.plot(x0[k], y0[k], '.', color=col, zorder=100, alpha=0.75, mec='none')
            else:
                ax.plot(segx[k], segy[k], '.-', lw=2, color=col, zorder=100, alpha=0.75, mec='none')

        # labels
        if label and 'MPNAM2' in self['IN3']:
            for k, name in enumerate(self['IN3']['MPNAM2']):
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='w', zorder=1000, weight='bold', clip_on=True)
                ax.text(x0[k], y0[k], '\n ' + name, ha='left', va='top', size=8, color='r', zorder=1001, clip_on=True)

    def plot_poloidal_field_coils(self, edgecolor='none', facecolor='orange', label=False, ax=None):
        """
        Plot poloidal field coils

        :param label: [True, False]

        :param ax: axis
        """

        if 'RF' not in self['IN3'] or not hasattr(self['IN3']['RF'], '__len__') or len(self['IN3']['RF']) == 0:
            return
        if ax is None:
            ax = pyplot.gca()
        return self.plot_system('FC', edgecolor=edgecolor, facecolor=facecolor, label=label, ax=ax)

    def plot_ohmic_coils(self, edgecolor='none', facecolor='none', label=False, ax=None):
        """
        Plot ohmic coils

        :param label: [True, False]

        :param ax: axis
        """

        if 'RE' not in self['IN3'] or not hasattr(self['IN3']['RE'], '__len__') or len(self['IN3']['RE']) == 0:
            return
        if ax is None:
            ax = pyplot.gca()
        return self.plot_system('OH', edgecolor=edgecolor, facecolor=facecolor, label=label, ax=ax)

    def plot_vessel(self, edgecolor='none', facecolor='gray', label=False, ax=None):
        """
        Plot vacuum vessel

        :param label: [True, False]

        :param ax: axis
        """
        if 'RVS' not in self['IN3'] or not hasattr(self['IN3']['RVS'], '__len__') or len(self['IN3']['RVS']) == 0:
            return
        if ax is None:
            ax = pyplot.gca()
        return self.plot_system('VESSEL', edgecolor=edgecolor, facecolor=facecolor, label=label, ax=ax)

    def plot_system(self, system, edgecolor, facecolor, label=False, ax=None):
        """
        Plot coil/vessel system

        :param system: ['FC', 'OH', 'VESSEL']

        :param edgecolor: color of patch edges

        :param facecolor: color of patch fill

        :param label: [True, False]

        :param ax: axis
        """
        if ax is None:
            ax = pyplot.gca()
        kw = {'ax': ax}
        kw['patch_facecolor'] = facecolor
        kw['patch_edgecolor'] = edgecolor
        in3 = self['in3']
        if system == 'OH':
            bn = 'E'
            system_array = np.array(list(zip(in3[f'R{bn}'], in3[f'Z{bn}'], in3[f'W{bn}'], in3[f'H{bn}'], in3[f'{bn}CID'])))
        if system == 'FC':
            bn = 'F'
            system_array = np.array(list(zip(in3[f'R{bn}'], in3[f'Z{bn}'], in3[f'W{bn}'], in3[f'H{bn}'], in3[f'A{bn}'], in3[f'A{bn}2'])))
        if system == 'VESSEL':
            bn = 'VS'
            system_array = np.array(list(zip(in3[f'R{bn}'], in3[f'Z{bn}'], in3[f'W{bn}'], in3[f'H{bn}'], in3[f'A{bn}'], in3[f'A{bn}2'])))

        if system == 'OH':
            if len(in3['RE']) == 0:
                return
            n = int(max(system_array[:, -1]))
        for k in range(system_array.shape[0]):
            # disable plotting of dummy probes/loops
            if system_array[k, 1] == self.invalid:
                continue
            if system == 'OH' and facecolor == 'none':
                kw['patch_facecolor'] = pyplot.cm.viridis(np.linspace(0.0, 1.0, n))[int(system_array[k, -1]) - 1]
            if label:
                kw['label'] = '%d' % k
            self.plot_coil(system_array[k, :], **kw)
        ax.set_frame_on(False)
        ax.set_aspect('equal')
        ax.autoscale(tight=True)
        ax.set_xlim(ax.get_xlim() * np.array([0.98, 1.02]))
        ax.set_ylim(ax.get_ylim() * np.array([1.02, 1.02]))

    def plot_domain(self, ax=None):
        """
        plot EFUND computation domain

        :param ax: axis
        """
        if ax is None:
            ax = pyplot.gca()

        from matplotlib import patches

        rect = patches.Rectangle(
            (self['IN5']['RLEFT'], self['IN5']['ZBOTTO']),
            self['IN5']['RRIGHT'] - self['IN5']['RLEFT'],
            self['IN5']['ZTOP'] - self['IN5']['ZBOTTO'],
            facecolor='none',
            edgecolor='black',
            ls='--',
        )
        ax.add_patch(rect)

    def plot(self, label=False, plot_coils=True, plot_vessel=True, plot_measurements=True, plot_domain=True, ax=None):
        """
        Composite plot

        :param label: label coils and measurements

        :param plot_coils: plot poloidal field and oh coils

        :param plot_vessel: plot conducting vessel

        :param plot_measurements: plot flux loops and magnetic probes

        :param plot_domain: plot EFUND computing domain

        :param ax: axis
        """

        if ax is None:
            ax = pyplot.gca()
        if plot_coils:
            self.plot_poloidal_field_coils(label=label, ax=ax)
            self.plot_ohmic_coils(label=label, ax=ax)
        if plot_vessel:
            self.plot_vessel(label=label, ax=ax)
        if plot_measurements:
            self.plot_flux_loops(label=label, ax=ax)
            self.plot_magnetic_probes(label=label, ax=ax)
        if not isinstance(self, OMFITdprobe) and plot_domain:
            self.plot_domain(ax=ax)
        ax.autoscale(tight=True)

    def __call__(self, *args, **kw):
        r"""
        Done to override default OMFIT GUI behaviour for OMFITnamelist
        """
        return self.plotFigure(*args, **kw)

    def aggregate_oh_coils(self, index=None, group=None):
        """
        Aggregate selected OH coils into a single coil

        :param index of OH coils to aggregate

        :param group: group of OH coils to aggregate
        """
        if group is not None:
            index = np.where(self['OH'][:, 4] == group)[0]

        mx = np.min(self['IN3']['RE'][index, 0] - self['OH'][index, 2] / 2.0)
        MX = np.max(self['OH'][index, 0] + self['OH'][index, 2] / 2.0)
        my = np.min(self['OH'][index, 1] - self['OH'][index, 3] / 2.0)
        MY = np.max(self['OH'][index, 1] + self['OH'][index, 3] / 2.0)
        group = self['OH'][index, 4][0]

        aggregated_coil = [(MX + mx) / 2.0, (MY + my) / 2.0, (MX - mx), (MY - my), group]

        index = np.array(sorted(list(set(list(range(self['OH'].shape[0]))).difference(list(index)))))
        self['OH'] = self['OH'][index, :]
        self['OH'] = np.vstack((self['OH'], aggregated_coil))

    def disable_oh_group(self, group):
        """
        remove OH group

        :param group: group of OH coils to disable
        """
        index = np.where(self['OH'][:, 4] != group)[0]
        self['OH'] = self['OH'][index, :]
        groups = np.unique(self['OH'][:, 4])
        groups_mapper = dict(zip(groups, range(1, len(groups) + 1)))
        for k in range(self['OH'].shape[0]):
            self['OH'][k, 4] = groups_mapper[self['OH'][k, 4]]

    def change_R(self, deltaR=0.0):
        """
        add or subtract a deltaR to coils, flux loops and magnetic
        probes radial location effectively changing the aspect ratio

        :param deltaR: radial shift in m
        """

        for item in self['IN3']:
            if item[0].upper() in ['R', 'X']:
                self['IN3'][item] += deltaR

    def change_Z(self, deltaZ=0.0):
        """
        add or subtract a deltaZ to coils, flux loops and magnetic
        probes radial location effectively changing the aspect ratio

        :param deltaR: radial shift in m
        """

        for item in self['IN3']:
            if item[0].upper() in ['Z', 'Y']:
                self['IN3'][item] += deltaZ

    def scale_system(self, scale_factor=0.0):
        """
        scale coils, flux loops and magnetic
        probes radial location effectively changing the major radius
        holding aspect ratio fixed

        :param scale_factor: scaling factor to multiple system by
        """

        for item in self['IN3']:
            if item[0].upper() in ['R', 'X']:
                self['IN3'][item] *= scale_factor
            if item[0].upper() in ['Z', 'Y']:
                self['IN3'][item] *= scale_factor

    def fill_coils_from(self, mhdin):
        """
        Copy FC, OH, VESSEL from passed object into current object,
        without changing the number of elements in current object.

        This requires that the number of elements in the current object
        is greater or equal than the number of elements in the passed object.
        The extra elements in the current object will be placed at R=0, Z=0

        :param mhdin: other mhdin object
        """
        self['RF'][:, 0] = 0.01
        self['ZF'][:, 1] = self.invalid
        self['WF'][:, 2] = 0.01
        self['FC'][:, 3] = 0.01
        self['FC'][:, 4] = 0.0
        self['FC'][:, 5] = 90.0

        self['OH'][:, 0] = 0.01
        self['OH'][:, 1] = self.invalid
        self['OH'][:, 2] = 0.01
        self['OH'][:, 3] = 0.01
        if len(mhdin['OH']):
            delta_shape = self['OH'].shape[0] - mhdin['OH'].shape[0]
            if delta_shape and max(mhdin['OH'][:, 4]) >= max(self['OH'][:, 4]):
                raise ValueError('OMFITmhdin.fill_coils_from() has no space for an extra `invalid` OH group')
            self['OH'][mhdin['OH'].shape[0] :, 4] = np.linspace(
                max(mhdin['OH'][:, 4]) + 1, max(self['OH'][:, 4]) + 0.9999, delta_shape
            ).astype(int)
            self['OH'][: mhdin['OH'].shape[0], 4] = 0.0

        self['VESSEL'][:, 0] = 0.01
        self['VESSEL'][:, 1] = self.invalid
        self['VESSEL'][:, 2] = 0.01
        self['VESSEL'][:, 3] = 0.01
        self['VESSEL'][:, 4] = 0.0
        self['VESSEL'][:, 5] = 90.0
        self['IN3']['VSNAME'] = ['DUMMY_%d' % k for k in range(self['VESSEL'].shape[0])]
        if len(mhdin['VESSEL']):
            self['IN3']['VSNAME'][: self['VESSEL'].shape[0]] = mhdin['IN3'].get('VSNAME', ['vessel'] * self['VESSEL'].shape[0])

        for system in ['FC', 'OH', 'VESSEL']:
            if len(mhdin[system]):
                self[system][: len(mhdin[system])] = mhdin[system]

    def modify_vessel_elements(self, index, action=['keep', 'delete'][0]):
        """
        Utility function to remove vessel elements

        :param index: index of the vessel elements to either keep or delete

        :param action: can be either 'keep' or 'delete'
        """
        keep_index = index
        if action == 'delete':
            keep_index = [k for k in range(len(self['IN3']['VSNAME'])) if k not in index]
        self['VESSEL'] = self['VESSEL'][keep_index]
        self['IN3']['VSNAME'] = np.array(self['IN3']['VSNAME'])[keep_index]

    def fill_probes_loops_from(self, mhdin):
        """
        Copy flux loops and magnetic probes from other object into current object,
        without changing the number of elements in current object

        This requires that the number of elements in the current object
        is greater or equal than the number of elements in the passed object.
        The extra elements in the current object will be placed at R=0, Z=0

        :param mhdin: other mhdin object
        """
        for system in [['XMP2', 'YMP2', 'SMP2', 'AMP2', 'MPNAM2'], ['RSI', 'ZSI', 'LPNAME']]:
            for item in system:
                if item in ['MPNAM2', 'LPNAME']:
                    self['IN3'][item] = ['DUMMY_%d' % k for k in range(len(self['IN3'][item]))]
                    self['IN3'][item][: len(mhdin['IN3'][item])] = mhdin['IN3'][item]
                else:
                    self['IN3'][item] *= 0
                    if item[0] in ['X', 'R']:
                        self['IN3'][item] += 0.01
                    elif item[0] in ['Y', 'Z']:
                        self['IN3'][item] += -self.invalid
                    elif item[0] in ['S']:
                        self['IN3'][item] += 0.01
                    self['IN3'][item][: len(mhdin['IN3'][item])] = mhdin['IN3'][item]

    def fill_scalars_from(self, mhdin):
        """
        copy scalar quantities in IN3 and IN5 namelists
        without overwriting ['IFCOIL', 'IECOIL', 'IVESEL']

        :param mhdin: other mhdin object
        """
        for item in self['IN3']:
            if item in mhdin['IN3']:
                if isinstance(mhdin['IN3'][item], (int, float)):
                    self['IN3'][item] = mhdin['IN3'][item]
                else:
                    self['IN3'][item] = np.array(self['IN3'][item])

        for item in self['IN5']:
            if item in mhdin['IN5']:
                if isinstance(mhdin['IN5'][item], (int, float)):
                    if item not in ['IFCOIL', 'IECOIL', 'IVESEL']:
                        self['IN5'][item] = mhdin['IN5'][item]
                else:
                    self['IN5'][item] = np.array(self['IN5'][item])

    def pretty_print(self, default_tilt2=0):

        if 'RF' in self:
            print('# =======')
            print('# F-COILS')
            print('# =======')
            print('R_fcoil = ', end='')
            print(repr(self['IN3']['RF']))
            print('Z_fcoil = ', end='')
            print(repr(self['IN3']['ZF']))
            print('W_fcoil = ', end='')
            print(repr(self['IN3']['WF']))
            print('H_fcoil = ', end='')
            print(repr(self['IN3']['HF']))

        if 'RSI' in self:

            print('# ==========')
            print('# Flux loops')
            print('# ==========')
            print('R_flux_loop = ', end='')
            print(repr(self['IN3']['RSI']))
            print('Z_flux_loop = ', end='')
            print(repr(self['IN3']['ZSI']))
            print('name_flux_loop = ', end='')
            print(repr(self['IN3']['LPNAME']))

        if 'XMP2' in self:
            print('# ===============')
            print('# Magnetic probes')
            print('# ===============')
            print('R_magnetic = ', end='')
            print(repr(self['IN3']['XMP2']))
            print('Z_magnetic = ', end='')
            print(repr(self['IN3']['YMP2']))
            print('A_magnetic = ', end='')
            print(repr(self['IN3']['AMP2']))
            print('S_magnetic = ', end='')
            print(repr(self['IN3']['SMP2']))
            print('name_magnetic = ', end='')
            print(repr(self['IN3']['MPNAM2']))

        return self

    def efund_to_outline(self, coil_data, outline):

        """
        The routine converts efund data format to ods outline format

         :param coil_data: 6-index array, r,z,w,h,a1,a2

         :param outline: ods outline entry

         :return: outline
        """

        a1 = coil_data[4] * np.pi / 180.0
        a2 = coil_data[5] * np.pi / 180.0
        if abs(a1) < 1e-8 and abs(a2) > 1e-8:
            side = coil_data[3] / np.tan(a2)
            hw1 = (coil_data[2] + side) / 2.0
            hw2 = (coil_data[2] - side) / 2.0
            hh = coil_data[3] / 2.0
            outline['r'] = [
                coil_data[0] - hw1,
                coil_data[0] - hw2,
                coil_data[0] + hw1,
                coil_data[0] + hw2,
            ]
            outline['z'] = [
                coil_data[1] - hh,
                coil_data[1] + hh,
                coil_data[1] + hh,
                coil_data[1] - hh,
            ]
        else:
            side = coil_data[2] * np.tan(a1)
            hw = coil_data[2] / 2.0
            hh1 = (coil_data[3] + side) / 2.0
            hh2 = (coil_data[3] - side) / 2.0
            outline['r'] = [
                coil_data[0] - hw,
                coil_data[0] - hw,
                coil_data[0] + hw,
                coil_data[0] + hw,
            ]
            outline['z'] = [
                coil_data[1] - hh1,
                coil_data[1] + hh2,
                coil_data[1] + hh1,
                coil_data[1] - hh2,
            ]

        return outline

    def outline_to_efund(self, outline):

        """
        The routine converts ods outline format to efund data format
          Since efund only supports parallelograms and requires 2 sides
            to be either vertical or horizontal this will likely not match
            the outline very well.  Instead, the parallelogram will only
            match the angle of the lower left side, the height of the upper
            right side, and width of the the left most top side.

         :param outline: ods outline entry

         :return: 6-index array, r,z,w,h,a1,a2
        """

        rcent = np.mean(outline['r'])
        zcent = np.mean(outline['z'])
        rrel = outline['r'] - rcent
        zrel = outline['z'] - zcent

        angle = np.arctan2(zrel, rrel)
        rsort = [r for _, r in sorted(zip(angle, rrel))]
        zsort = [z for _, z in sorted(zip(angle, zrel))]

        r11, z11 = rsort[0], zsort[0]
        r01, z01 = rsort[1], zsort[1]
        r00, z00 = rsort[2], zsort[2]
        r10, z10 = rsort[3], zsort[3]

        # handle fringe cases that should be valid
        n = 0
        for i in range(4):
            if angle[i] <= -np.pi / 2:
                n += 1
        if n == 0:
            if r11**2 + z11**2 > r10**2 + z10**2:
                r11, z11 = rsort[3], zsort[3]
                r01, z01 = rsort[0], zsort[0]
                r00, z00 = rsort[1], zsort[1]
                r10, z10 = rsort[2], zsort[2]
        elif n == 2:
            if r11**2 + z11**2 < r01**2 + z01**2:
                r11, z11 = rsort[1], zsort[1]
                r01, z01 = rsort[2], zsort[2]
                r00, z00 = rsort[3], zsort[3]
                r10, z10 = rsort[0], zsort[0]

        height = z00 - z01
        width = r00 - r10
        a1 = np.arctan2(z01 - z11, r01 - r11)
        a2 = 0.0
        if abs(a1) < 1.0e-8:
            a1 = 0.0
            a2 = np.arctan2(z00 - z01, r00 - r01)

        return [rcent, zcent, width, height, scipy.degrees(a1), scipy.degrees(a2)]

    def rectangle_to_efund(self, rectangle):
        r = rectangle['r']
        z = rectangle['z']
        w = rectangle['width']
        h = rectangle['height']
        a1 = 0.0
        a2 = 0.0
        return [r, z, w, h, a1, a2]

    def annulus_to_efund(self, annulus):
        """
        The routine converts an ods annulus format to efund data format
          by approximating it as a square

         :param annulus: ods annulus entry

         :return: 6-index array, r,z,w,h,a1,a2
        """
        r = annulus['r']
        z = annulus['z']
        w = 2 * annulus['radius_outer']
        h = w
        a1 = 0.0
        a2 = 0.0
        return [r, z, w, h, a1, a2]

    def thick_line_to_efund(self, thick_line):

        """
        The routine converts ods thick_line format to efund data format
          The only time a thick line is a valid shape in efund is when
            it is vertical or horizontal.  All others will not be a
            great fit, but some approximation is used.

         :param thick_line: ods thick_line entry

         :return: 6-index array, r,z,w,h,a1,a2
        """

        r1, z1 = thick_line['first_point']['r'], thick_line['first_point']['z']
        r2, z2 = thick_line['second_point']['r'], thick_line['second_point']['z']
        a = np.pi / 2 - np.arctan2(z2 - z1, r2 - r1)
        dr = thick_line['thickness'] / 2.0 * np.cos(a)
        dz = thick_line['thickness'] / 2.0 * np.sin(a)

        r11, z11 = r1 - dr, z1 + dz
        r01, z01 = r1 + dr, z1 - dz
        r00, z00 = r2 - dr, z2 + dz
        r10, z10 = r2 + dr, z2 - dz
        outline = {"r": [r11, r10, r00, r01], "z": [z11, z10, z00, z01]}

        return self.outline_to_efund(outline)

    def annular_to_efund(self, annular):

        """
        The routine converts ods annular format to efund data format
          The only time annular segments are a valid shape in efund is when
            they are vertical or horizontal.  All others will not be a
            great fit, but some approximation is used.

         :param annular: ods annular entry

         :return: 6-index array, r,z,w,h,a1,a2 in which each is an array over
                  the number of segments
        """

        ns = len(annular['centreline.r']) - 1
        nt = ns + annular['centreline.closed']
        r, z = np.zeros(nt), np.zeros(nt)
        w, h = np.zeros(nt), np.zeros(nt)
        a1, a2 = np.zeros(nt), np.zeros(nt)

        for i in range(ns):
            fp = {"r": annular['centreline.r'][i], "z": annular['centreline.z'][i]}
            sp = {"r": annular['centreline.r'][i + 1], "z": annular['centreline.z'][i + 1]}
            thick_line = {"first_point": fp, "second_point": sp, "thickness": annular['thickness'][i]}
            [r[i], z[i], w[i], h[i], a1[i], a2[i]] = self.thick_line_to_efund(thick_line)

        if annular['centreline.closed']:
            fp = {"r": annular['centreline.r'][-1], "z": annular['centreline.z'][-1]}
            sp = {"r": annular['centreline.r'][0], "z": annular['centreline.z'][0]}
            thick_line = {"first_point": fp, "second_point": sp, "thickness": annular['thickness'][-1]}
            [r[-1], z[-1], w[-1], h[-1], a1[-1], a2[-1]] = self.thick_line_to_efund(thick_line)

        return [r, z, w, h, a1, a2]

    # Generate initial mhdin
    def init_mhdin(self, device):
        # mhdin = OMFITnamelist(filename = 'mhdin')
        self['MACHINEIN'] = NamelistName()
        self['MACHINEIN']['device'] = device
        self['MACHINEIN']['nfcoil'] = 1
        self['MACHINEIN']['nfsum'] = 1
        self['MACHINEIN']['nsilop'] = 1
        self['MACHINEIN']['magpri'] = 1
        self['MACHINEIN']['necoil'] = 1
        self['MACHINEIN']['nesum'] = 1
        self['MACHINEIN']['nvesel'] = 1
        self['MACHINEIN']['nvsum'] = 1
        self['MACHINEIN']['nacoil'] = 1

        self['IN3'] = NamelistName()
        self['IN3']['RF'] = []
        self['IN3']['ZF'] = []
        self['IN3']['WF'] = []
        self['IN3']['HF'] = []
        self['IN3']['AF'] = []
        self['IN3']['AF2'] = []
        self['IN3']['TURNFC'] = []
        self['IN3']['FCTURN'] = []
        self['IN3']['FCID'] = []
        self['IN3']['FCNAME'] = []

        self['IN3']['RE'] = []
        self['IN3']['ZE'] = []
        self['IN3']['WE'] = []
        self['IN3']['HE'] = []
        self['IN3']['ECTURN'] = []
        self['IN3']['ECID'] = []
        self['IN3']['ECNAME'] = []

        self['IN3']['RVS'] = []
        self['IN3']['ZVS'] = []
        self['IN3']['WVS'] = []
        self['IN3']['HVS'] = []
        self['IN3']['AVS'] = []
        self['IN3']['AVS2'] = []
        self['IN3']['RSISVS'] = []
        self['IN3']['VSID'] = []
        self['IN3']['VSNAME'] = []

        self['IN3']['RACOIL'] = []
        self['IN3']['ZACOIL'] = []
        self['IN3']['WACOIL'] = []
        self['IN3']['HACOIl'] = []

        self['IN3']['RSI'] = []
        self['IN3']['ZSI'] = []

        self['IN5'] = NamelistName()
        self['IN5']['IGRID'] = 1
        self['IN5']['RLEFT'] = 0.84
        self['IN5']['RRIGHT'] = 2.54
        self['IN5']['ZBOTTO'] = -1.6
        self['IN5']['ZTOP'] = 1.6
        self['IN5']['IFCOIL'] = 0
        self['IN5']['ISLPFC'] = 0
        self['IN5']['NSMP2'] = 25
        self['IN5']['IECOIL'] = 0
        self['IN5']['IVESEL'] = 0
        self['IN5']['IACOIL'] = 0
        self['IN5']['mgaus1'] = 8
        self['IN5']['mgaus2'] = 12
        return self

    def from_omas(self, ods, passive_map='VS'):

        if 'dataset_description.data_entry.machine' in ods:
            device = ods['dataset_description.data_entry.machine']
        else:
            device = 'my_device'

        self = self.init_mhdin(device)

        ncoil = {'F': 0, 'E': 0, 'ACOIL': 0, 'VS': 0}
        nsum = {'F': 0, 'E': 0, 'ACOIL': 0, 'VS': 0}
        # Generic
        coil_map = {'OH': 'E', 'PF': 'F'}
        # DIII-D
        coil_map['E'] = 'E'
        coil_map['F'] = 'F'
        coil_map['ADP'] = 'ACOIL'
        # ITER
        coil_map['CS'] = 'E'  # Central solenoid
        coil_map['VS'] = 'F'  # Vertical Stabilzation (in-vessel coils)
        coil_map['TF'] = 'ACOIL'  # TF coil busbars
        coil_map['VC'] = 'S'  # Virtual coils (skip)

        for coil_type in ['pf_active.coil', 'pf_passive.loop']:

            if not coil_type in ods:
                continue

            for isum in ods[coil_type]:

                coil = ods[coil_type][isum]
                efund_name = 'S'
                if coil_type == 'pf_passive.loop':
                    efund_name = passive_map
                else:
                    for i in coil_map.keys():
                        if i in coil['name']:
                            efund_name = coil_map[i]

                if efund_name == 'S':
                    continue

                nsum[efund_name] += 1
                if 'CS1L' in coil['name']:  # ITER
                    nsum[efund_name] -= 1
                elif efund_name == 'F':
                    if is_device(device, ['d3d', 'jet', 'cmod', 'pegasus']):
                        self['IN3']['TURNFC'].append(coil['element'][0]['turns_with_sign'])
                    else:
                        self['IN3']['TURNFC'].append(1.0)
                    self['IN3']['FCNAME'].append(coil['name'])
                elif efund_name == 'VS':
                    self['IN3']['VSNAME'].append(coil['name'])
                elif efund_name != 'ACOIL':
                    self['IN3'][f'{efund_name}CNAME'].append(coil['name'])

                for ielement in coil['element']:
                    ncoil[efund_name] += 1
                    element = coil['element'][ielement]
                    if 'rectangle' in element['geometry']:
                        [r, z, w, h, a1, a2] = self.rectangle_to_efund(element['geometry.rectangle'])
                    elif 'annulus' in element['geometry']:
                        [r, z, w, h, a1, a2] = self.annulus_to_efund(element['geometry.annulus'])
                    elif 'outline' in element['geometry']:
                        [r, z, w, h, a1, a2] = self.outline_to_efund(element['geometry.outline'])
                    elif 'thick_line' in element['geometry']:
                        [r, z, w, h, a1, a2] = self.thick_line_to_efund(element['geometry.thick_line'])
                    else:
                        raise ValueError(f'No conversion defined for geometry of {coil_type}.{isum}')

                    self['IN3'][f'R{efund_name}'].append(r)
                    self['IN3'][f'Z{efund_name}'].append(z)
                    self['IN3'][f'W{efund_name}'].append(w)
                    self['IN3'][f'H{efund_name}'].append(h)

                    if efund_name == 'F' or efund_name == 'VS':
                        self['IN3'][f'A{efund_name}'].append(a1)
                        self['IN3'][f'A{efund_name}2'].append(a2)

                    if efund_name == 'VS':
                        self['IN3'][f'VSID'].append(nsum[efund_name])
                        self['IN5'][f'IVESEL'] = 1
                        if 'resistance' in coil:
                            self['IN3']['RSISVS'].append(coil['resistance'])
                        else:
                            self['IN3']['RSISVS'].append(coil['resistivity'] / 2 / np.pi / r)
                    elif efund_name == 'F':
                        self['IN3']['FCID'].append(nsum[efund_name])
                        if is_device(device, ['d3d', 'jet', 'cmod', 'pegasus']):
                            self['IN3']['FCTURN'].append(1.0)
                        else:
                            self['IN3']['FCTURN'].append(element['turns_with_sign'])
                        self['IN5']['IFCOIL'] = 1
                    elif efund_name != 'ACOIL':
                        self['IN3'][f'{efund_name}CID'].append(nsum[efund_name])
                        self['IN3'][f'{efund_name}CTURN'].append(element['turns_with_sign'])
                        self['IN5'][f'I{efund_name}COIL'] = 1
                    else:
                        self['IN5'][f'I{efund_name}'] = 1

        self['MACHINEIN']['nfsum'] = nsum['F']
        self['machinein']['nfcoil'] = ncoil['F']
        self['MACHINEIN']['nesum'] = nsum['E']
        self['machinein']['necoil'] = ncoil['E']
        self['MACHINEIN']['nvsum'] = nsum['VS']
        self['machinein']['nvesel'] = ncoil['VS']

        self['MACHINEIN']['nacoil'] = ncoil['ACOIL']

        self['MACHINEIN']['magpri'] = 0
        self['MACHINEIN']['nsilop'] = 0
        if 'magnetics' in ods:
            if 'b_field_pol_probe' in ods['magnetics']:
                self['MACHINEIN']['magpri'] = nmp2 = len(list(filter(None, ods['magnetics.b_field_pol_probe.:.length'])))
                self['IN3']['XMP2'] = xmp2 = np.zeros(nmp2)
                self['IN3']['YMP2'] = ymp2 = np.zeros(nmp2)
                self['IN3']['SMP2'] = smp2 = np.zeros(nmp2)
                self['IN3']['AMP2'] = amp2 = np.zeros(nmp2)
                self['IN3']['MPNAM2'] = mpnam2 = np.chararray(nmp2, itemsize=10, unicode=True)
                n = 0
                for i in ods['magnetics.b_field_pol_probe']:
                    probe = ods['magnetics.b_field_pol_probe'][i]
                    if 'length' in probe:
                        xmp2[n] = probe['position.r']
                        ymp2[n] = probe['position.z']
                        smp2[n] = probe['length']
                        amp2[n] = -180 / np.pi * probe['poloidal_angle']
                        mpnam2[n] = probe['name']
                        n += 1

            self['MACHINEIN']['nsilop'] = 0
            if 'flux_loop' in ods['magnetics']:
                self['MACHINEIN']['nsilop'] = nsilop = len(
                    np.where(np.array(list(filter(None, ods['magnetics.flux_loop.:.type.index']))) == 1)[0]
                )
                self['IN3']['RSI'] = rsi = np.zeros(nsilop)
                self['IN3']['ZSI'] = zsi = np.zeros(nsilop)
                self['IN3']['LPNAME'] = lpname = np.chararray(nsilop, itemsize=10, unicode=True)
                for i in ods['magnetics.flux_loop']:
                    loop = ods['magnetics.flux_loop'][i]
                    if 'type' in loop and 'index' in loop['type'] and loop['type.index'] == 1:
                        rsi[i] = loop['position.0.r']
                        zsi[i] = loop['position.0.z']
                        lpname[i] = loop['name']

        # only use vessel described in wall if pf_passive hasn't been already
        # (these should be equivalent, but the annular wall type is harder to represent)
        if 'wall.description_2d[0].vessel.unit' in ods and not 'pf_passive.loop' in ods:
            self['IN5']['IVESEL'] = 1

            nvesel = 0
            for i in ods['wall.description_2d.0.vessel.unit']:
                unit = ods['wall.description_2d.0.vessel.unit'][i]
                if 'element' in unit:
                    nvesel += 1
                elif 'annular' in unit:
                    nvesel += len(unit['annular.centreline.r']) - 1 + unit['annular.centreline.closed']
                else:
                    raise ValueError(f'No conversion defined for geometry of vessel unit {iunit}')
            self['MACHINEIN']['nvesel'] = self['MACHINEIN']['nvsum'] = nvesel
            self['IN3']['RVS'] = rvs = np.zeros(nvesel)
            self['IN3']['ZVS'] = zvs = np.zeros(nvesel)
            self['IN3']['WVS'] = wvs = np.zeros(nvesel)
            self['IN3']['HVS'] = hvs = np.zeros(nvesel)
            self['IN3']['AVS'] = avs = np.zeros(nvesel)
            self['IN3']['AVS2'] = avs2 = np.zeros(nvesel)
            self['IN3']['RSISVS'] = rsisvs = np.zeros(nvesel)
            self['IN3']['VSID'] = vsid = np.zeros(nvesel, dtype=int)
            self['IN3']['VSNAME'] = vsname = np.chararray(nvesel, itemsize=10, unicode=True)
            n = 0
            for i in ods['wall.description_2d.0.vessel.unit']:
                unit = ods['wall.description_2d.0.vessel.unit'][i]
                if 'element' in unit:
                    rvs[n], zvs[n], wvs[n], hvs[n], avs[n], avs2[n] = self.outline_to_efund(unit['element.0.outline'])
                    if 'resistance' in unit['annular.0']:
                        rsisvs[n] = unit['element.0.resistance']
                    else:
                        rsisvs[n] = unit['element.0.resistivity'] / 2 / np.pi / rvs[n]
                    vsid[n] = n + 1
                    vsname[n] = unit['name']
                    n += 1
                elif 'annular' in unit:
                    nl = n + len(unit['annular.centreline.r']) - 1 + unit['annular.centreline.closed']
                    rvs[n:nl], zvs[n:nl], wvs[n:nl], hvs[n:nl], avs[n:nl], avs2[n:nl] = self.annular_to_efund(unit['annular'])
                    # IMAS data schema is missing annular resistance...
                    # if 'resistance' in unit['annular']:
                    #    rsisvs[n:nl] = unit['annular.resistance']
                    # else:
                    rsisvs[n:nl] = unit['annular.resistivity'] / 2 / np.pi / rvs[n:nl]
                    vsid[n:nl] = np.arange(n + 1, nl + 1)
                    vsname[n:nl] = unit['name']
                    n = nl

        # Set the grid to be 5% larger than the limiter, if it's in the file
        if 'wall.description_2d[0].limiter.unit[0].outline' in ods:
            rwall = ods['wall.description_2d[0].limiter.unit[0].outline.r']
            zwall = ods['wall.description_2d[0].limiter.unit[0].outline.z']
            rmin = min(rwall)
            rmax = max(rwall)
            zmin = min(zwall)
            zmax = max(zwall)
            drbound = 0.05 * (rmax - rmin)
            dzbound = 0.05 * (zmax - zmin)
            if rmin > drbound:
                self['IN5']['RLEFT'] = rmin - drbound
            else:
                self['IN5']['RLEFT'] = rmin / 2
            self['IN5']['RRIGHT'] = rmax + drbound
            self['IN5']['ZBOTTO'] = zmin - dzbound
            self['IN5']['ZTOP'] = zmax + dzbound

        # remove empty arrays from the IN3 namelist (these originate from init_mhdin as a convenience)
        for entry in self['IN3'].keys():
            if np.size(self['IN3'][entry]) == 0:
                self['IN3'].pop(entry)

        return self

    def to_omas(self, ods=None, update=['pf_active', 'flux_loop', 'b_field_pol_probe', 'vessel']):
        """
        Transfers data in EFIT mhdin.dat format to ODS

        WARNING: only rudimentary identifies are assigned for pf_active
        You should assign your own identifiers and only rely on this function to assign numerical geometry data.

        :param ods: ODS instance
            Data will be added in-place

        :param update: systems to populate
            ['oh', 'pf_active', 'flux_loop', 'b_field_pol_probe']
            ['magnetics'] will enable both ['flux_loop', 'b_field_pol_probe']
            NOTE that in IMAS the OH information goes under `pf_active`

        :return: ODS instance
        """

        from omas.omas_plot import geo_type_lookup
        from omas import omas_environment, ODS

        if ods is None:
            ods = ODS()

        device = ods['dataset_description.data_entry.machine'] = self['MACHINEIN']['DEVICE']

        # pf_active
        if 'pf_active' in update and 'RE' in self['IN3'] and len(np.atleast_1d(self['IN3']['RE'])) > 0:
            r = np.atleast_1d(self['IN3']['RE'])
            z = np.atleast_1d(self['IN3']['ZE'])
            width = np.atleast_1d(self['IN3']['WE'])
            height = np.atleast_1d(self['IN3']['HE'])
            turns = np.atleast_1d(self['IN3']['ECTURN'])
            elements_id = (np.atleast_1d(self['IN3']['ECID']) - 1).astype(int)
            if 'ECNAME' in self['IN3']:
                name = list(map(lambda x: x.strip(), np.atleast_1d(self['IN3']['ECNAME'])))
            else:
                name = np.array([f"OH_{i}" for i in range(len(r))])
            rect_code = geo_type_lookup('rectangle', 'pf_active', ods.imas_version, reverse=True)
            with omas_environment(ods, dynamic_path_creation='dynamic_array_structures'):
                for i in range(len(r)):
                    c = elements_id[i]
                    e = sum(elements_id[:i] == elements_id[i])
                    ods['pf_active.coil'][c]['name'] = name[c]
                    ods['pf_active.coil'][c]['identifier'] = name[c]
                    ods['pf_active.coil'][c]['element'][e]['name'] = f'{name[c]}_{e}'
                    ods['pf_active.coil'][c]['element'][e]['identifier'] = f'{name[c]}_{e}'
                    ods['pf_active.coil'][c]['element'][e]['turns_with_sign'] = turns[i]
                    rect = ods['pf_active.coil'][c]['element'][e]['geometry.rectangle']
                    rect['r'] = r[i]
                    rect['z'] = z[i]
                    rect['width'] = width[i]
                    rect['height'] = height[i]
                    ods['pf_active.coil'][c]['element'][e]['geometry.geometry_type'] = rect_code

        if 'pf_active' in update and 'RF' in self['IN3'] and len(np.atleast_1d(self['IN3']['RF'])) > 0:
            r = np.atleast_1d(self['IN3']['RF'])
            z = np.atleast_1d(self['IN3']['ZF'])
            width = np.atleast_1d(self['IN3']['WF'])
            height = np.atleast_1d(self['IN3']['HF'])
            angle1 = np.atleast_1d(self['IN3']['AF'])
            angle2 = np.atleast_1d(self['IN3']['AF2'])
            turns = np.atleast_1d(self['IN3']['FCTURN'])
            if 'TURNFC' in self['IN3']:
                turnfc = self['IN3']['TURNFC']
            else:
                turnfc = np.ones(int(max(self['IN3']['FCID'])))
            elements_id = (np.atleast_1d(self['IN3']['FCID']) - 1).astype(int)
            if 'FCNAME' in self['IN3']:
                name = list(map(lambda x: x.strip(), np.atleast_1d(self['IN3']['FCNAME'])))
            else:
                name = np.array([f"PF_{i}" for i in range(len(r))])
            rect_code = geo_type_lookup('rectangle', 'pf_active', ods.imas_version, reverse=True)
            outline_code = geo_type_lookup('outline', 'pf_active', ods.imas_version, reverse=True)
            offset = len(ods['pf_active.coil'])
            for i in range(len(r)):
                c = elements_id[i] + offset
                e = sum(elements_id[:i] == elements_id[i])
                ods['pf_active.coil'][c]['name'] = name[c - offset]
                ods['pf_active.coil'][c]['identifier'] = name[c - offset]
                ods['pf_active.coil'][c]['element'][e]['name'] = f'{name[c - offset]}_{e}'
                ods['pf_active.coil'][c]['element'][e]['identifier'] = f'{name[c - offset]}_{e}'
                ods['pf_active.coil'][c]['element'][e]['turns_with_sign'] = turns[i] * turnfc[elements_id[i]]
                if angle1[i] == 0 and angle2[i] == 0:
                    rect = ods['pf_active.coil'][c]['element'][e]['geometry.rectangle']
                    rect['r'] = r[i]
                    rect['z'] = z[i]
                    rect['width'] = width[i]
                    rect['height'] = height[i]
                    ods['pf_active.coil'][c]['element'][e]['geometry.geometry_type'] = rect_code
                else:
                    outline = ods['pf_active.coil'][c]['element'][e]['geometry.outline']
                    outline = self.efund_to_outline([r[i], z[i], width[i], height[i], angle1[i], angle2[i]], outline)

                    ods['pf_active.coil'][c]['element'][e]['geometry.geometry_type'] = outline_code

        # flux_loop
        if ('magnetics' in update or 'flux_loop' in update) and 'RSI' in self['IN3'] and len(np.atleast_1d(self['IN3']['RSI'])) > 0:
            R_flux_loop = np.atleast_1d(self['IN3']['RSI'])
            Z_flux_loop = np.atleast_1d(self['IN3']['ZSI'])
            if 'LPNAME' in self['IN3']:
                name_flux_loop = list(map(lambda x: x.strip(), np.atleast_1d(self['IN3']['LPNAME'])))
            else:
                name_flux_loop = np.array([f"FL_{i+1}" for i in range(len(R_flux_loop))])
            with omas_environment(ods, cocosio=1):
                for k, (r, z, name) in enumerate(zip(R_flux_loop, Z_flux_loop, name_flux_loop)):
                    ods[f'magnetics.flux_loop.{k}.name'] = name
                    ods[f'magnetics.flux_loop.{k}.identifier'] = name
                    ods[f'magnetics.flux_loop.{k}.position[0].r'] = r
                    ods[f'magnetics.flux_loop.{k}.position[0].z'] = z
                    ods[f'magnetics.flux_loop.{k}.type.index'] = 1

        # b_field_pol_probe
        if (
            ('magnetics' in update or 'b_field_pol_probe' in update)
            and 'XMP2' in self['IN3']
            and len(np.atleast_1d(self['IN3']['XMP2'])) > 0
        ):
            R_magnetic = self['IN3']['XMP2']
            Z_magnetic = self['IN3']['YMP2']
            A_magnetic = self['IN3']['AMP2']
            S_magnetic = self['IN3']['SMP2']
            if 'MPNAM2' in self['IN3']:
                name_magnetic = list(map(lambda x: x.strip(), self['IN3']['MPNAM2']))
            else:
                name_magnetic = np.array([f"MP_{i+1}" for i in range(len(R_magnetic))])
            with omas_environment(ods, cocosio=1):
                for k, (r, z, a, s, name) in enumerate(zip(R_magnetic, Z_magnetic, A_magnetic, S_magnetic, name_magnetic)):
                    ods[f'magnetics.b_field_pol_probe.{k}.name'] = name
                    ods[f'magnetics.b_field_pol_probe.{k}.identifier'] = name
                    ods[f'magnetics.b_field_pol_probe.{k}.position.r'] = r
                    ods[f'magnetics.b_field_pol_probe.{k}.position.z'] = z
                    ods[f'magnetics.b_field_pol_probe.{k}.length'] = s
                    ods[f'magnetics.b_field_pol_probe.{k}.poloidal_angle'] = -a / 180 * np.pi
                    ods[f'magnetics.b_field_pol_probe.{k}.toroidal_angle'] = 0.0 / 180 * np.pi
                    ods[f'magnetics.b_field_pol_probe.{k}.type.index'] = 1
                    ods[f'magnetics.b_field_pol_probe.{k}.turns'] = 1

        # Vessel
        if (
            'vessel' in update
            and 'RVS' in self['IN3']
            and len(np.atleast_1d(self['IN3']['RVS']))
            and len(np.atleast_1d(self['IN3']['RVS'])) > 0
        ):
            r = np.atleast_1d(self['IN3']['RVS'])
            z = np.atleast_1d(self['IN3']['ZVS'])
            width = np.atleast_1d(self['IN3']['WVS'])
            height = np.atleast_1d(self['IN3']['HVS'])
            angle1 = np.atleast_1d(self['IN3']['AVS'])
            angle2 = np.atleast_1d(self['IN3']['AVS2'])
            if 'RSISVS' in self['IN3']:
                resistance = np.atleast_1d(self['IN3']['RSISVS'])
            else:
                resistance = np.zeros(len(r))
            resistivity = resistance * 2 * np.pi * r
            elements_id = (np.atleast_1d(self['IN3']['VSID']) - 1).astype(int)
            if 'VSNAME' in self['IN3']:
                name = list(map(lambda x: x.strip(), self['IN3']['VSNAME']))
            else:
                name = np.array([f"VS_{i+1}" for i in range(len(r))])

            for i in range(len(r)):
                c = elements_id[i]
                e = sum(elements_id[:i] == elements_id[i])
                ods['pf_passive.loop'][c]['name'] = name[c]
                # ods['pf_passive.loop'][c]['identifier'] = f'PF{c}'
                ods['pf_passive.loop'][c]['element'][e]['name'] = f'{name[c]}_{e}'
                ods['pf_passive.loop'][c]['element'][e]['identifier'] = f'{name[c]}_{e}'
                ods['pf_passive.loop'][c]['element'][e]['turns_with_sign'] = 1.0
                ods['pf_passive.loop'][c]['resistance'] = resistance[c]
                ods['pf_passive.loop'][c]['resistivity'] = resistivity[c]
                if angle1[i] == 0 and angle2[i] == 0:
                    rect = ods['pf_passive.loop'][c]['element'][e]['geometry.rectangle']
                    rect['r'] = r[i]
                    rect['z'] = z[i]
                    rect['width'] = width[i]
                    rect['height'] = height[i]
                    ods['pf_passive.loop'][c]['element'][e]['geometry.geometry_type'] = 2
                else:
                    outline = ods['pf_passive.loop'][c]['element'][e]['geometry.outline']
                    outline = self.efund_to_outline([r[i], z[i], width[i], height[i], angle1[i], angle2[i]], outline)

                    ods['pf_passive.loop'][c]['element'][e]['geometry.geometry_type'] = 1

        return ods

    def from_miller(self, a=1.2, R=3.0, kappa=1.8, delta=0.4, zeta=0.0, zmag=0.0, nf=14, wf=0.05, hf=0.05, turns=100):

        self = self.init_mhdin('device')
        Rf, Zf = rz_miller(a=a, R=R, kappa=kappa, delta=delta, zeta=zeta, zmag=zmag, poloidal_resolution=nf + 2)
        Rf = Rf[1:-1]
        Zf = Zf[1:-1]

        # Conservatively set grid to include f-coils (bad idea for tokamak with blanket)
        self['IN5']['RLEFT'] = np.min(Rf) - 0.5 * wf
        self['IN5']['RRIGHT'] = np.max(Rf) + 0.5 * wf
        self['IN5']['ZTOP'] = np.max(Zf) + 0.5 * hf
        self['IN5']['ZBOTTO'] = np.min(Zf) - 0.5 * hf

        self['MACHINEIN']['nfsum'] = self['MACHINEIN']['nfcoil'] = nf

        self['IN5']['IFCOIL'] = 1
        self['IN3']['FCID'] = np.arange(1, nf + 1, 1)
        self['IN3']['RF'] = Rf
        self['IN3']['ZF'] = Zf
        self['IN3']['WF'] = np.ones(nf) * wf
        self['IN3']['HF'] = np.ones(nf) * hf
        self['IN3']['AF'] = np.zeros(nf)
        self['IN3']['AF2'] = 90 * np.ones(nf)

        self['IN3']['FCTURN'] = np.ones(nf)
        self['IN3']['TURNFC'] = turns * np.ones(nf)

        self['IN3']['RSI'] = np.min(Rf) - 1 * wf
        self['IN3']['RE'] = np.min(Rf) - 1 * wf
        self['IN3']['MPNAM2'] = 'MP_A'
        self['IN3']['LPNAME'] = 'LP_A'

        return self

    def fake_geqdsk(self, rbbbs, zbbbs, rlim, zlim, Bt, Ip, nw, nh):
        """
        This function generates a fake geqdsk that can be used for fixed boundary EFIT modeling


        :param rbbbs: R of last closed flux surface [m]

        :param zbbbs: Z of last closed flux surface [m]

        :param rlim: R of limiter [m]

        :param zlim: Z of limiter [m]

        :param Bt: Central magnetic field [T]

        :param Ip: Plasma current [A]
        """

        geqdsk = OMFITgeqdsk('geqdsk')
        geqdsk['CASE'] = ['1', '2', '3', '#999999', '1000ms', '6']
        geqdsk['NW'] = nw
        geqdsk['NH'] = nh
        geqdsk['RDIM'] = self['IN5']['RRIGHT'] - self['IN5']['RLEFT']
        geqdsk['ZDIM'] = self['IN5']['ZTOP'] - self['IN5']['ZBOTTO']
        geqdsk['RLEFT'] = self['IN5']['RLEFT']
        geqdsk['RCENTR'] = 0.5 * (self['IN5']['RRIGHT'] + self['IN5']['RLEFT'])
        geqdsk['ZMID'] = 0.5 * (self['IN5']['ZTOP'] + self['IN5']['ZBOTTO'])

        geqdsk['RMAXIS'] = 0.0
        geqdsk['ZMAXIS'] = 0.0

        geqdsk['SIMAG'] = 0.0
        geqdsk['SIBRY'] = 0.0
        geqdsk['BCENTR'] = Bt
        geqdsk['CURRENT'] = Ip

        geqdsk['FPOL'] = np.zeros(nw)
        geqdsk['PRES'] = np.zeros(nw)
        geqdsk['FFPRIM'] = -1 * np.ones(nw)
        geqdsk['PPRIME'] = -1 * np.ones(nw)
        geqdsk['PSIRZ'] = np.zeros([nw, nh])
        geqdsk['QPSI'] = np.zeros(nw)

        geqdsk['NBBBS'] = len(rbbbs)
        geqdsk['RBBBS'] = rbbbs
        geqdsk['ZBBBS'] = zbbbs

        geqdsk['LIMITR'] = len(rlim)
        geqdsk['RLIM'] = rlim
        geqdsk['ZLIM'] = zlim

        geqdsk['KVTOR'] = 0
        geqdsk['RVTOR'] = 1.0
        geqdsk['NMASS'] = 0
        geqdsk['RHOVN'] = np.zeros(nw)

        # Rederive AuxQuantities
        geqdsk.save()
        geqdsk.load()

        return geqdsk


class OMFITdprobe(OMFITmhdin):
    @dynaLoad
    def load(self, *args, **kw):
        self.outsideOfNamelistIsComment = True
        self.noSpaceIsComment = True
        OMFITnamelist.load(self, *args, **kw)

        for item in list(self['IN3'].keys()):
            if item.upper() not in [
                'RSISVS',
                'TURNFC',
                'VSNAME',
                'LPNAME',
                'MPNAM2',
                'RSI',
                'ZSI',
                'XMP2',
                'YMP2',
                'AMP2',
                'SMP2',
                'PATMP2',
            ]:
                del self['IN3'][item]


class OMFITnstxMHD(SortedDict, OMFITascii):
    """
    OMFIT class to read NSTX MHD device files such as `device01152015.dat`, `diagSpec01152015.dat` and `signals_020916_PF4.dat`
    """

    def __init__(self, filename, use_leading_comma=None, **kw):
        r"""
        OMFIT class to parse NSTX MHD device files

        :param filename: filename

        :param \**kw: arguments passed to __init__ of OMFITascii
        """
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        self.clear()
        with open(self.filename, 'r') as f:
            lines = f.read().split('\n')
        lines = [line for line in lines if len(line.strip()) and not line.startswith(';')]
        self['all'] = {}
        for line in lines:
            line, description = (line + ';').split(';', 1)
            line = line.split()
            if line[1] not in self:
                self[line[1]] = {}
            piece = len(self[line[1]])
            # signals.dat
            if len(line) in [16, 17]:
                self.type = 'signals'
                self[line[1]][piece] = dict(
                    zip(
                        'name type map_var map_index mds_tree read_sig rel_error abs_error sig_thresh use_err scale pri fitwt t_index t_smooth mds_name'.split(),
                        line,
                    )
                )
            # diagspec.dat
            elif len(line) == 12:
                self.type = 'diagspec'
                self[line[1]][piece] = dict(zip('name type id rc zc wc hc ac ac2 turns div material'.split(), line))
            # device.dat
            elif len(line) == 8:
                self.type = 'device'
                self[line[1]][piece] = dict(zip('tag type units rc zc pol_ang tor_ang1 tor_ang2'.split(), line))
            else:
                raise ValueError(f'Format not recognized {len(line)}')
            self[line[1]][piece]['description'] = description.strip(';')
            for item in self[line[1]][piece]:
                try:
                    self[line[1]][piece][item] = ast.literal_eval(self[line[1]][piece][item])
                except (ValueError, SyntaxError):
                    pass
            self['all'][line[0]] = self[line[1]][piece]

        # postprocess
        if self.type == 'signals':
            mds_tree_map = {'o': 'operations', 'e': 'engineering', 'a': 'activespec', 'r': 'radiatiion', 'E2': 'efit02', '-': 'computed'}
            for group in self:
                if group not in ['all']:
                    for item in self[group]:
                        self[group][item]['mds_tree'] = mds_tree_map.get(self[group][item]['mds_tree'], self[group][item]['mds_tree'])
            # sort entries according to their `map` fields
            self['mappings'] = {}
            for group in self:
                for item in self[group]:
                    map_var = self[group][item].get('map_var', 'none')
                    self['mappings'].setdefault(map_var, {})
                    map_index = self[group][item].get('map_index', len(self['mappings'][map_var]))
                    self['mappings'][map_var][map_index] = value = self[group][item]
                    if 'mds_tree' in value:
                        if value['mds_tree'] == 'computed' and value['mds_name'] in self['all']:
                            value['mds_tree_resolved'] = self['all'][value['mds_name']]['mds_tree']
                            value['mds_name_resolved'] = self['all'][value['mds_name']]['mds_name'] + '/' + str(value['scale'])
                        else:
                            value['mds_tree_resolved'] = value['mds_tree']
                            value['mds_name_resolved'] = value['mds_name']
        return self

    def pretty_print(self):
        """
        Print data in file as arrays, as it is needed for a fortran namelist
        """
        for group in self:
            for item in self[group][0]:
                print(f"{group.lower()}_{item.split('(')[0].lower()} = ", end='')
                print([self[group][k][item] for k in self[group]])
        return self


def get_mhdindat(
    device=None,
    pulse=None,
    select_from_dict=None,
    filenames=['dprobe.dat', 'mhdin.dat'],
):
    """
    :param device: name of the device to get the mhdin.dat file of

    :param pulse: for certain devices the mhdin.dat depends on the shot number

    :param select_from_dict: select from external dictionary

    :param filenames: filenames to get, typically 'mhdin.dat' and/or 'dprobe.dat'
                      NOTE: 'dprobe.dat' is a subset of 'mhdin.dat'

    :return: OMFITmhdin object
    """
    if device is None:
        selected_device = "*"
    else:
        selected_device = tokamak(device, 'OMAS').lower()

    mhd = dict()
    if select_from_dict is not None:
        for item in list(select_from_dict.keys()):
            if os.path.basename(select_from_dict[item].filename) in filenames:
                mhd[item] = select_from_dict[item]

    else:
        for device_dir in glob.glob(os.sep.join([omas.omas_dir, 'machine_mappings', 'support_files', '*'])):
            device = tokamak(os.path.basename(device_dir))
            for mhdin in filenames:
                if mhdin == 'mhdin.dat':
                    OMFIT_mhdclass = OMFITmhdin
                else:
                    OMFIT_mhdclass = OMFITdprobe
                filename = os.sep.join([device_dir, mhdin])
                if os.path.exists(filename):
                    mhd[f'{device}_000000'] = OMFIT_mhdclass(filename)
                else:
                    for device_dir_subdir in glob.glob(os.sep.join([device_dir, '*'])):
                        filename = os.sep.join([device_dir_subdir, mhdin])
                        ranges_filename = os.sep.join([device_dir_subdir, 'ranges.dat'])
                        if os.path.exists(filename) and os.path.exists(ranges_filename):
                            with open(os.sep.join([device_dir_subdir, 'ranges.dat']), 'r') as f:
                                start_at = int(f.read().split()[0])
                            mhd[f'{device}_{start_at:06d}'] = OMFIT_mhdclass(filename)

    if selected_device != '*':
        latest = None
        for item in list(sorted(mhd.keys())):
            try:
                device, shot = item.split("_")
                shot = int(shot)
            except Exception:
                continue
            if tokamak(selected_device) == device:
                latest = mhd[item]
            if tokamak(selected_device) == device and pulse is not None and shot >= pulse:
                return mhd[item]
        if latest is None:
            raise ValueError(
                f"No mhdin.dat for {selected_device}. Valid devices are " + str(np.unique([item.split("_")[0] for item in mhd]))
            )
        return latest

    return mhd


def green_to_omas(
    ods=None,
    filedir='/fusion/projects/codes/efit/efitai/efit_support_files/DIII-D/green/168191/',
    nw=129,
    nh=129,
    nsilop=44,
    magpri=76,
    nesum=6,
    nfsum=18,
    nvsum=24,
):

    """
    This function reads EFUND generate Green's function tables and put them into IMAS

    :param ods: input ods to populate

    :param filedir: directory which contains EFUND generated binary files

    :param nw: number of horizontal grid points

    :param nw: number of vertical grid points

    :param magpri: number of magnetic probes (will be overwritten if available in directory)

    :param nsilop: number of flux loops (will be overwritten if available in directory)

    :param nesum: number of e-coils (will be overwritten if available in directory)

    :param nfsum: number of f-coils (will be overwritten if available in directory)

    :param nvsum: number of vessel structures (will be overwritten if available in directory)

    returns ods

    """
    from omas import omas_environment, ODS

    try:
        filename = '/mhdin.dat'
        file = filedir + filename
        mhdin = OMFITnamelist(file)
        if 'machinein' in mhdin:
            nfsum = mhdin['machinein']['nfsum']
            nesum = mhdin['machinein']['nesum']
            nvsum = mhdin['machinein']['nvsum']
            magpri = mhdin['machinein']['magpri']
            nsilop = mhdin['machinein']['nsilop']
    except Exception:
        try:
            filename = '/dprobe.dat'  # pretend dprobe file is mhdin for coil names
            file = filedir + filename
            mhdin = OMFITnamelist(file)
            printw('could not read array sizes from mhdin.dat')
        except Exception:
            printw('could not read array sizes from mhdin.dat or dprobe.dat')

    if ods is None:
        ods = ODS()

    green = {}
    green['nesum'] = nesum
    green['nsilop'] = nsilop
    green['magpri'] = magpri
    green['nfsum'] = nfsum
    green['nvsum'] = nvsum
    green['nw'] = nw
    green['nh'] = nh

    ods['em_coupling.code.name'] = 'EFUND'
    ods['em_coupling.ids_properties.homogeneous_time'] = 2

    # Missing/TODO: These should be setup as URIs now but not sure how to do that... using names or madeup strings for now
    if magpri > 0:
        if 'mpnam2' in mhdin['in3']:
            ods['em_coupling.b_field_pol_probes'] = mhdin['in3']['mpnam2']
        else:
            ods['em_coupling.b_field_pol_probes'] = np.array([f"MP_{i+1}" for i in range(magpri)])
    else:
        ods['em_coupling.b_field_pol_probes'] = np.empty(0)
    if nsilop > 0:
        if 'lpname' in mhdin['in3']:
            ods['em_coupling.flux_loops'] = mhdin['in3']['lpname']
        else:
            ods['em_coupling.flux_loops'] = np.array([f"FL_{i+1}" for i in range(nsilop)])
    else:
        ods['em_coupling.flux_loops'] = np.empty(0)
    if nesum > 0 or nfsum > 0:
        if 'ecname' in mhdin['in3'] or 'fcname' in mhdin['in3']:
            ods['em_coupling.active_coils'] = [mhdin['in3']['ecname'], mhdin['in3']['fcname']]
        else:
            ods['em_coupling.active_coils'] = np.array([f"OH_{i+1}" for i in range(nesum)] + [f"PF_{i+1}" for i in range(nfsum)])
    else:
        ods['em_coupling.active_coils'] = np.empty(0)
    if nvsum > 0:
        if 'vsname' in mhdin['in3']:
            ods['em_coupling.passive_loops'] = mhdin['in3']['vsname']
        else:
            ods['em_coupling.passive_loops'] = np.array([f"VS_{i+1}" for i in range(nvsum)])
    else:
        ods['em_coupling.passive_loops'] = np.empty(0)
    ods['em_coupling.plasma_elements'] = np.chararray(nw * nh, itemsize=1, unicode=True)

    endian = '>'
    # Response of poloidal field (F) coils on grid, and grid on itself.
    filename = f'ec{nw}{nh}.ddd'
    file = filedir + filename
    f = scipy.io.FortranFile(file, 'r', f'{endian}i4')
    [mw, mh] = f.read_ints(f'{endian}i4')
    grid = f.read_reals(f'{endian}f8')
    green['rgrid'] = grid[:mw]
    green['zgrid'] = grid[mw:]
    green['RR'], green['ZZ'] = np.meshgrid(green['rgrid'], green['zgrid'])
    try:
        ods['equilibrium.time_slice.0.profiles_2d.0.grid.dim1'] = green['rgrid']
        ods['equilibrium.time_slice.0.profiles_2d.0.grid.dim2'] = green['zgrid']
    except Exception:
        printw('could not write grid sizes to equilibium')

    ggridfc = f.read_reals(f'{endian}f8').reshape([nfsum, mw * mh]).T
    ods['em_coupling.mutual_plasma_plasma'] = f.read_reals(f'{endian}f8').reshape(mw, mh * mw).T

    # Response of poloidal field coil on flux loops, magnetic probes, and grid
    filename = f'rfcoil.ddd'
    file = filedir + filename
    f = scipy.io.FortranFile(file, 'r', f'{endian}i4')
    rsilfc = f.read_reals(f'{endian}f8').reshape([nfsum, nsilop]).T
    rmp2fc = f.read_reals(f'{endian}f8').reshape([nfsum, magpri]).T

    # Response of Ohmic heating coil on flux loops, magnetic probes, and plasma
    try:
        filename = f're{nw}{nh}.ddd'
        file = filedir + filename
        f = scipy.io.FortranFile(file, 'r', f'{endian}i4')
        rsilec = f.read_reals(f'{endian}f8').reshape([nesum, nsilop]).T
        rmp2ec = f.read_reals(f'{endian}f8').reshape([nesum, magpri]).T
        gridec = f.read_reals(f'{endian}f8').reshape([nesum, mw * mh]).T
        ods['em_coupling.mutual_loops_active'] = np.append(rsilec, rsilfc, axis=1)
        ods['em_coupling.b_field_pol_probes_active'] = np.append(rmp2ec, rmp2fc, axis=1)
        ods['em_coupling.mutual_plasma_active'] = np.append(gridec, ggridfc, axis=1)
        no_ecoil = False
    except Exception:
        ods['em_coupling.mutual_loops_active'] = rsilfc
        ods['em_coupling.b_field_pol_probes_active'] = rmp2fc
        ods['em_coupling.mutual_plasma_active'] = ggridfc
        no_ecoil = True
        printw('Ohmic heating coil tables not available')

    # Response of vessel on flux loops, probes, and plasma
    try:
        filename = f'rv{nw}{nh}.ddd'
        file = filedir + filename
        f = scipy.io.FortranFile(file, 'r', f'{endian}i4')
        ods['em_coupling.mutual_loops_passive'] = f.read_reals(f'{endian}f8').reshape([nvsum, nsilop]).T
        ods['em_coupling.b_field_pol_probes_passive'] = f.read_reals(f'{endian}f8').reshape([nvsum, magpri]).T
        ods['em_coupling.mutual_plasma_passive'] = f.read_reals(f'{endian}f8').reshape([nvsum, mw * mh]).T

    except Exception:
        printw('Vessel not available')

    # Response of coils on vessel
    try:
        gfcvs = f.read_reals(f'{endian}f8').reshape([nvsum, nfsum])
        gecvs = f.read_reals(f'{endian}f8').reshape([nvsum, nesum])

        if not no_ecoil:
            ods['em_coupling.mutual_passive_active'] = np.append(gecvs, gfcvs, axis=1)
        else:
            ods['em_coupling.mutual_passive_active'] = gfcvs

        ods['em_coupling.mutual_passive_passive'] = f.read_reals(f'{endian}f8').reshape([nvsum, nvsum])

    except Exception:
        printw('Vessel-coil mutual inductances not available')

    # Response of magnetics flux loops and probes on plasma
    filename = f'ep{nw}{nh}.ddd'
    file = filedir + filename
    f = scipy.io.FortranFile(file, 'r', f'{endian}i4')
    ods['em_coupling.mutual_loops_plasma'] = f.read_reals(f'{endian}f8').reshape([mw * mh, nsilop]).T
    ods['em_coupling.b_field_pol_probes_plasma'] = f.read_reals(f'{endian}f8').reshape([mw * mh, magpri]).T
    ods['em_coupling.ids_properties.homogeneous_time'] = 2
    ods['em_coupling.code.parameters'] = green
    return ods


############################################
if '__main__' == __name__:
    from matplotlib import pyplot

    test_classes_main_header()
    for mhdin in get_mhdindat().values():
        mhdin.load()
        mhdin.pretty_print()
        mhdin.plot(label=True)
        pyplot.show()

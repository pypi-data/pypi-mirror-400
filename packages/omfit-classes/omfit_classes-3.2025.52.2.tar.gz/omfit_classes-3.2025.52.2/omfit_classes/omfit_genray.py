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

from omfit_classes.omfit_nc import OMFITnc
from omfit_classes.fluxSurface import *

__all__ = ['OMFITgenray']


class OMFITgenray(OMFITnc):
    def pr(self, inp):
        out = inp.T.copy()
        #        out[np.where(self,['wr']['data'].T==0)]=np.nan
        #        out[np.where(self,['wr']['data'].T is nan)]=np.nan
        return out

    def slow_fast(self):
        n_par = self.pr(self['wnpar']['data'])
        n_per = self.pr(self['wnper']['data'])

        S = self.pr(self['cweps11']['data'])
        S = S[:, :, 0] + 1.0j * S[:, :, 1]
        D = self.pr(self['cweps12']['data'])
        D = (D[:, :, 0] + 1.0j * D[:, :, 1]) / -1.0j
        P = self.pr(self['cweps33']['data'])
        P = P[:, :, 0] + 1.0j * P[:, :, 1]
        R = S + D
        L = S - D

        A = S
        B = R * L + P * S - P * n_par**2 - S * n_par**2
        C = P * (R * L - 2 * S * n_par**2 + n_par**4)
        n_per2_f = (B - np.sqrt(B**2 - 4 * A * C)) / (2 * A)
        n_per2_s = (B + np.sqrt(B**2 - 4 * A * C)) / (2 * A)

        tmp = np.zeros((n_per2_s.shape[0], n_per2_s.shape[1], 2))
        tmp[:, :, 0] = abs(n_per2_s - n_per**2)
        tmp[:, :, 1] = abs(n_per2_f - n_per**2)
        slow_fast = np.argmin(tmp, 2) * 1.0

        return slow_fast

    def to_omas(self, ods=None, time_index=0, new_sources=True, n_rho=201):
        """
        translate GENRAY class to OMAS data structure

        :param ods: input ods to which data is added

        :param time_index: time index to which data is added

        :param new_sources: wipe out existing sources

        :return: ODS
        """
        from omas import ODS, omas_environment

        if ods is None:
            ods = ODS()

        if new_sources or 'core_sources.source' not in ods:
            ods['core_sources']['source'] = ODS()
            s = 0
        else:
            s = len(ods['core_sources']['source'])

        freq = self['freqcy']['data'] / 1e9
        ergs_to_J = 1e-7
        cm_to_m = 1e-2
        with omas_environment(ods, cocosio=5):
            if self['freqcy']['data'] < 100e6:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY IC heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY IC'
                ods[f'core_sources.source.{s}.identifier.index'] = 5  # IC
            elif self['freqcy']['data'] < 1e9:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY Helicon heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY Helicon'
                ods[f'core_sources.source.{s}.identifier.index'] = 5  # Helicon
            elif self['freqcy']['data'] < 10e9:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY LH heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY LH'
                ods[f'core_sources.source.{s}.identifier.index'] = 4  # LH
            else:
                ods[f'core_sources.source.{s}.identifier.description'] = f"GENRAY EC heating source at {freq:3.3f} GHz"
                ods[f'core_sources.source.{s}.identifier.name'] = 'GENRAY EC'
                ods[f'core_sources.source.{s}.identifier.index'] = 3  # ECH
            source = ods[f'core_sources.source.{s}.profiles_1d'][time_index]

            source['j_parallel'] = self['s_cur_den_onetwo']['data'] / (cm_to_m**2)  # from A/cm^2 to A/m^2
            source['electrons']['energy'] = self['powden_e']['data'] * ergs_to_J / (cm_to_m**3)  # from erg/cm^3/s to J/m^3/s
            source['total_ion_energy'] = self['powden_i']['data'] * ergs_to_J / (cm_to_m**3)  # from erg/cm^3/s to J/m^3/s
            rho = np.linspace(0, 1, n_rho)
            rho_genray = self['rho_bin_center']['data']
            source['grid']['rho_tor_norm'] = rho
            source['j_parallel'] = interp1e(rho_genray, source['j_parallel'])(rho)
            source['electrons']['energy'] = interp1e(rho_genray, source['electrons']['energy'])(rho)
            source['total_ion_energy'] = interp1e(rho_genray, source['total_ion_energy'])(rho)
        return ods

    def plot(self, gEQDSK=None, showSlowFast=False):

        with pyplot.style.context('default'):
            fig = pyplot.gcf()
            fig.set_size_inches(16, 8)
            ax0 = pyplot.subplot(131)
            if gEQDSK is None:
                gEQDSK = {}
                gEQDSK['RHORZ'] = self['eqdsk_psi']['data']
                gEQDSK['R'] = self['eqdsk_r']['data']
                gEQDSK['Z'] = self['eqdsk_z']['data']

                n = 10
                flx = fluxSurfaces(
                    Rin=self['eqdsk_r']['data'],
                    Zin=self['eqdsk_z']['data'],
                    PSIin=self['eqdsk_psi']['data'],
                    Btin=self['eqdsk_psi']['data'] * 0,
                    levels=n,
                    quiet=True,
                    cocosin=1,
                )
                for k in range(n):
                    pyplot.plot(flx['flux'][k]['R'], flx['flux'][k]['Z'], 'k', linewidth=0.5)
                pyplot.xlabel('R')
                pyplot.ylabel('Z')
            else:
                gEQDSK.plot(only2D=True)
                flx = gEQDSK['fluxSurfaces']

            pyplot.title('Ray trajectories')

            rho = self['rho_bin_center']['data']
            powden = self['powden']['data']
            powden_e = self['powden_e']['data']
            powden_i = self['powden_i']['data']
            powtot_e = self['powtot_e']['data']
            powtot_i = self['powtot_i']['data']
            powtot = self['power_total']['data']
            cur_parallel = self['s_cur_den_parallel']['data']
            curtotal_parallel = self['parallel_cur_total']['data']

            powden = powden / 1e7  # ergs/sec/cm^3 to W/cm^3 = MW/m^3
            powden_e = powden_e / 1e7  # ergs/sec/cm^3 to W/cm^3 = MW/m^3
            powden_i = powden_i / 1e7  # ergs/sec/cm^3 to W/cm^3 = MW/m^3
            powtot_elec = powtot_e / 1e7 / 1e6  # from ergs/sec to W, and to MW
            powtot_ions = powtot_i / 1e7 / 1e6
            powtot = powtot / 1e7 / 1e6
            cur_parallel = cur_parallel / 1e2  # from A/cm^2 to MA/m^2
            curtotal_parallel = curtotal_parallel / 1e3  # from A to kA

            npar = self['wnpar']['data'].flatten()
            wr_vals = self['wr']['data'].flatten()
            wz_vals = self['wz']['data'].flatten()
            wphi_vals = self['wphi']['data'].flatten()
            rho_ray = self['spsi']['data'].flatten()
            btot_ray = self['sbtot']['data'].flatten()
            dpol = self['ws']['data'].flatten()
            dpol = dpol / 1e2  # from cm to m
            wr_vals = wr_vals / 1e2  # from cm to m
            wz_vals = wz_vals / 1e2  # from cm to m
            raypower = self['delpwr']['data'].flatten()
            raypower = raypower / 1e7 / 1e6  # from ergs/sec to W, and to MW
            deriv_raypower = abs(np.gradient(raypower, dpol))  # in MW/m
            deriv_raypower[np.isinf(deriv_raypower)] = 0

            dpolmax = max(dpol)
            wr_vals[wr_vals == 0] = np.nan
            wz_vals[wz_vals == 0] = np.nan
            wphi_vals[wphi_vals == 0] = np.nan
            dpol[dpol == 0] = np.nan

            ray_Te = self['ste']['data'].flatten()
            vpar = 3e10 / abs(npar)
            vthe = 4.19e7 * np.sqrt(2 * ray_Te * 1e3)  # ray_Te was in keV, using sqrt(2Te/m) as thermal velocity

            # ax0 = pyplot.subplot(131)
            pyplot.scatter(wr_vals, wz_vals, c='k', edgecolor='None', s=deriv_raypower / max(deriv_raypower) * 200, marker=',', alpha=0.1)
            myplot = pyplot.scatter(wr_vals, wz_vals, c=(raypower / max(raypower)), cmap='rainbow', edgecolor='None', marker='.')

            pyplot.xlabel('R (m)')
            pyplot.ylabel('Z (m)')
            pyplot.title('Ray trajectory')
            pyplot.axis('image')
            pyplot.colorbar(myplot, ax=ax0, norm=raypower, label='Power in ray (MW)')

            ax0 = pyplot.subplot(232)
            angles = np.arange(0, 6.3, 0.05)
            pyplot.scatter(
                wr_vals * np.cos(wphi_vals),
                wr_vals * np.sin(wphi_vals),
                c='k',
                edgecolor='None',
                s=deriv_raypower / max(deriv_raypower) * 200,
                marker=',',
                alpha=0.1,
            )
            myplot = pyplot.scatter(
                wr_vals * np.cos(wphi_vals),
                wr_vals * np.sin(wphi_vals),
                c=(raypower / max(raypower)),
                cmap='rainbow',
                edgecolor='None',
                marker='.',
            )
            Rmax_psin1 = max(flx['geo']['Rmax_centroid'])
            R_psin0 = min(flx['geo']['Rmax_centroid'])
            Rmin_psin1 = min(flx['geo']['Rmin_centroid'])
            pyplot.plot(Rmax_psin1 * np.cos(angles), Rmax_psin1 * np.sin(angles), 'k')
            pyplot.plot(R_psin0 * np.cos(angles), R_psin0 * np.sin(angles), 'k', linestyle='dashed')
            pyplot.plot(Rmin_psin1 * np.cos(angles), Rmin_psin1 * np.sin(angles), 'k')
            pyplot.xlabel('X (m)')
            pyplot.ylabel('Y (m)')
            pyplot.title('Ray trajectory')
            pyplot.axis('image')
            pyplot.colorbar(myplot, ax=ax0, norm=raypower, label='Power in ray (MW)')

            ax = pyplot.subplot(235)
            ax.clear()
            pyplot.plot(rho, powden, label='Total {:.2f} MW'.format(powtot), linewidth=1.5)
            pyplot.plot(rho, powden_e, label='Electrons {:.2f} MW'.format(powtot_elec), linewidth=1.5)
            pyplot.plot(rho, powden_i, label='Ions {:.2f} MW'.format(powtot_ions), linewidth=1.5)
            pyplot.legend(fontsize='medium', framealpha=0.2, frameon=0, loc='upper left')
            pyplot.xlabel('$\\rho$')
            pyplot.ylabel('Power density (MW/m$^3$)')
            pyplot.axis('tight')

            ax2 = ax.twinx()
            pyplot.plot(rho, cur_parallel, color='darkorange', label='$J_\parallel$ {:.1f} kA'.format(curtotal_parallel), linewidth=1.5)
            pyplot.ylabel('$J_\parallel$ (MA/m$^2$)')
            pyplot.title('$P_{abs}$ & CD')
            pyplot.legend(fontsize='medium', framealpha=0.2, frameon=0, loc='upper right')
            pyplot.axis('tight')

            ax3 = pyplot.subplot(233)
            ax3.clear()
            pyplot.plot(dpol, npar, c='r', label='Rainbow line: $n_\parallel$', linewidth=0)
            pyplot.scatter(dpol, npar, c='k', edgecolor='none', marker='.', s=deriv_raypower / max(deriv_raypower) * 1000, alpha=0.1)
            pyplot.scatter(dpol, npar, c=(raypower / max(raypower)), cmap='rainbow', edgecolor='none', marker='.')
            pyplot.xlabel('Distance along ray (m)')
            pyplot.ylabel('$n_\parallel$')

            ax4 = ax3.twinx()
            pyplot.plot(dpol, vpar / vthe, c='g', label='Green line: $v_\\parallel/v_{th,e}$', linewidth=0)
            pyplot.scatter(dpol, vpar / vthe, c='g', edgecolor='none', marker='.', s=deriv_raypower / max(deriv_raypower) * 1000, alpha=0.1)
            pyplot.plot(dpol, vpar / vthe, c='g')
            pyplot.ylabel('$v_\\parallel/v_{th,e}$')
            pyplot.xlim(0, dpolmax)
            pyplot.title('Green line: $v_\\parallel/v_{th,e}$  Rainbow line: $n_\parallel$')
            pyplot.axis('tight')

            ax5 = pyplot.subplot(236)
            pyplot.plot(vpar / vthe, deriv_raypower, c='b')
            pyplot.xlabel('$v_\\parallel/v_{th,e}$')
            pyplot.ylabel('Ray absorption (MW/m)')
            pyplot.xlim(0, 5)

            pyplot.subplots_adjust(hspace=0.4, left=0.03, wspace=0.4, right=0.95)

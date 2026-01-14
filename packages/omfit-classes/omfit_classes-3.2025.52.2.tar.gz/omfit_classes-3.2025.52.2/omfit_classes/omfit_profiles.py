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

from omfit_classes.utils_math import *
from omfit_classes.omfit_base import OMFITtree
from omfit_classes.omfit_osborne import OMFITpFile
from omfit_classes.omfit_eqdsk import OMFITgeqdsk
from omfit_classes.omfit_data import OMFITncDataset, OMFITncDynamicDataset, importDataset
from omas import ODS, omas_environment, cocos_transform, define_cocos
from omfit_classes.omfit_omas_utils import add_generic_OMFIT_info_to_ods
from omfit_classes.omfit_rdb import OMFITrdb

import inspect
import numpy as np
from uncertainties import unumpy, ufloat
from uncertainties.unumpy import std_devs, nominal_values
from scipy import constants

np.seterr(invalid='ignore', divide='ignore')

__all__ = ['OMFITprofiles', 'OMFITprofilesDynamic', 'available_profiles']

model_tree_species = ['e', '2H1', '4He2', '6Li3', '10B5', '12C6', '14N7', '20Ne10']

# fmt: off
model_tree_quantities = ['angular_momentum', 'angular_momentum_density', 'angular_momentum_density_{species}', 'angular_momentum_{species}',
'dn_{species}_dpsi', 'dT_{species}_dpsi', 'ELM_phase', 'ELM_since_last', 'ELM_until_next', 'epot_{species}', 'Er_{species}',
'Er_{species}_gradP', 'Er_{species}_gradP_Vtor', 'Er_{species}_Vpol', 'Er_{species}_Vtor', 'Er_{species}_VxB', 'f_Z',
'fpol', 'gamma_ExB_{species}', 'gamma_ExB_{species}_gradP', 'gamma_ExB_{species}_Vpol', 'gamma_ExB_{species}_Vtor', 'I_total', 'index',
'J_BS', 'J_efit_norm', 'J_ohm', 'J_tot', 'jboot_sauter', 'lnLambda', 'mass_density', 'n_fast_{species}', 'n_{species}',
'nclass_sigma', 'nu_star_{species}', 'nu_{species}', 'omega_E_{species}', 'omega_gyro_{species}_midplane',
'omega_LX_{species}_midplane', 'omega_N_{species}', 'omega_NTV0_{species}', 'omega_P_{species}', 'omega_plasma_{species}',
'omega_RX_{species}_midplane', 'omega_T_{species}', 'omega_tor_{species}', 'omega_tor_{species}_KDG', 'P_brem', 'p_fast_{species}', 'P_rad',
'P_rad_cNi', 'P_rad_cW', 'P_rad_int', 'P_rad_nNi', 'P_rad_nW', 'P_rad_ZnNi', 'P_rad_ZnW', 'p_thermal', 'p_tot', 'p_total', 'p_{species}',
'pres', 'psi', 'psi_n', 'psi_n_2d', 'psin_n_{species}', 'psin_T_{species}',
'psin_V_tor_{species}', 'q', 'R_midplane', 'raw_n_{species}', 'raw_T_{species}', 'raw_V_tor_{species}', 'resistivity', 'rho',
'SAWTOOTH_phase', 'SAWTOOTH_since_last', 'SAWTOOTH_until_next', 'sigma_nc', 'T_fast_{species}', 'T_i', 'T_i_T_e_ratio',
'T_{species}', 'time', 'Total_Zeff', 'V_pol_{species}_KDG', 'V_tor_{species}',
'Zavg_Ni', 'Zavg_W', 'Zeff']

# fmt: on


def ugrad1(a2d):
    """
    Gradient along second axis with uncertainty propagation.
    :param a2d: 2D array or uarray
    :return:
    """
    if isinstance(a2d, DataArray):
        a2d = a2d.values
    if is_uncertain(a2d):
        dy = np.gradient(nominal_values(a2d), axis=1)
        ye = std_devs(a2d)
        sigma = np.zeros_like(ye)
        sigma[:, 1:-1] = 0.5 * np.sqrt(ye[:, :-2] ** 2 + ye[:, 2:] ** 2)
        sigma[:, 0] = 0.5 * np.sqrt(ye[:, 0] ** 2 + ye[:, 1] ** 2)
        sigma[:, -1] = 0.5 * np.sqrt(ye[:, -2] ** 2 + ye[:, -1] ** 2)
        result = unumpy.uarray(dy, sigma)
    else:
        result = np.gradient(a2d, axis=1)
    return result


def mZ(species):
    """
    Parse subscript strings and return ion mass and charge

    :param species: subscript strings such as `e`, `12C6`, `2H1`, 'fast_2H1`, ...

    :return: m and Z
    """
    species = str(species).replace('fast_', '')
    if species == 'e':
        Z = -1
        m = constants.m_e
    else:
        m = int(re.sub('([0-9]+)([a-zA-Z]+)([0-9]+)', r'\1', species))
        name = re.sub('([0-9]+)([a-zA-Z]+)([0-9]+)', r'\2', species)
        Z = int(re.sub('([0-9]+)([a-zA-Z]+)([0-9]+)', r'\3', species))
        m *= constants.m_u
    return m, Z


def get_species(derived):
    """
    Identify species and ions that have density information
    """
    species = []
    for key in list(derived.data_vars.keys()):
        if not re.match('^[nT](_fast)?_([0-9]+[a-zA-Z]+[0-9]{1,2}|e)$', key):
            continue
        s = key.split('_')[-1]
        if '_fast_' in key:
            s = 'fast_' + s
        species.append(s)
    species = tolist(np.unique(species))
    ions = [s for s in species if s not in ['e']]
    ions_with_dens = [i for i in ions if 'n_' + i in derived]
    ions_with_fast = [i.replace('fast_', '') for i in ions if 'fast_' in i]
    return species, ions, ions_with_dens, ions_with_fast


def available_profiles(server, shot, device='DIII-D', verbose=True):
    out = {}
    db = OMFITrdb(db='code_rundb', server='d3drdb', by_column=True)
    runs = db.select(f"SELECT * FROM plasmas WHERE code_name='OMFITprofiles' AND experiment='{device}' AND shot={shot}")
    if len(runs) == 0:
        print("No run_id found for this shot.")
        return out
    else:
        for i, runid in enumerate(runs['run_id']):
            out[
                runid
            ] = f"runid={runid} by {runs['run_by'][i]} from {runs['start_time'][i]} to {runs['stop_time'][i]} with comment: {runs['run_comment'][i]}"

    return out


class OMFITprofiles(OMFITncDataset):
    """
    Data class used by OMFITprofiles, CAKE and other
    OMFIT modules for storing experimental profiles data
    """

    def __init__(self, filename, data_vars=None, coords=None, attrs=None, comment=''):
        """
        :param filename: filename of the NetCDF file where data will be saved

        :param data_vars: see xarray.Dataset

        :param coords: see xarray.Dataset

        :param attrs: see xarray.Dataset

        :param comment: String that if set will show in the OMFIT tree GUI
        """
        self.dynaLoad = False
        super().__init__(filename, data_vars=data_vars, coords=coords, attrs=attrs)
        self.OMFITproperties['comment'] = comment

    @property
    def comment(self):
        return self.OMFITproperties['comment']

    @comment.setter
    def comment(self, comment):
        self.OMFITproperties['comment'] = comment

    def __tree_repr__(self):
        if self.comment:
            return self.__class__.__name__ + ': ' + self.comment, []
        else:
            return super().__tree_repr__()

    def to_omas(self, ods=None, times=None):
        """
        :param ods: ODS to which data will be appended

        :return: ods
        """

        if ods is None:
            ods = ODS()
            eq_times = None
        else:
            # Determine if equilibrium is avaliable and for what times.
            eq_times = ods.time('equilibrium') * 1e3  # ODS times are in s, and omfit_profiles are in ms.

        if 'device' in self.attrs:
            ods['dataset_description.data_entry.machine'] = self.attrs['device']
        if 'shot' in self.attrs:
            ods['dataset_description.data_entry.pulse'] = self.attrs['shot']

        # identify fitting coordinate
        for fit_coordinate in ['rho', 'psi_n', None]:
            if fit_coordinate in self.dims:
                break
        if fit_coordinate is None:
            raise ValueError("Fit coordinate should be 'rho' or 'psi_n'")

        # general info
        species, ions, ions_with_dens, ions_with_fast = get_species(self)
        nion = len(ions)
        if times is None:
            times = self['time'].values
        else:
            times = np.atleast_1d(times)

        # figure out time match between eq (if available) and profiles
        if eq_times is None:
            printw("No equilibrium data is avaliable to to_omas(). Some info will not be stored.")
        elif np.all([time in eq_times for time in times]):  # aka is all times have avaliable eq
            printd("Matching equilibrium times found")
        elif np.any([time in eq_times for time in times]):
            printw("Some time slices don't have corresponding equilibria!")
            printw("These time slices will be missing some information.")
        else:
            printw("No equilibrium data is avaliable to to_omas(). Some info will not be stored.")

        # assign both core_profies and edge_profiles but with data from different spatial ranges
        idx_core = self[fit_coordinate].values <= 1.0
        idx_edge = self[fit_coordinate].values >= 0.8

        core_prof = ods['core_profiles']
        edge_prof = ods['edge_profiles']
        for prof in [core_prof, edge_prof]:
            prop = prof['ids_properties']
            prop['comment'] = 'Data from OMFITprofiles.to_omas()'
            prop['homogeneous_time'] = True

            prof['time'] = times / 1e3

        for ti, time in enumerate(times):
            for prof, idx_use, core in zip([core_prof, edge_prof], [idx_core, idx_edge], [True, False]):
                prof_1d = prof[f'profiles_1d.{ti}']
                prof_1d['time'] = time / 1e3

                # get corresponding eq and extract needed info
                geq = None
                R = None
                Bt = None
                Bp = None  # Make sure we don't accidentally use values from last timeslice
                if eq_times is not None and len(eq_times) > 0 and time in eq_times:
                    i_eq = np.where(time == eq_times)[0][0]  # just the first index
                    slice = ods[f'equilibrium.time_slice[{i_eq}]']
                    # get psin from profile
                    if fit_coordinate == 'psi_n':
                        psin = self['psi_n'].values
                    else:
                        psin = self['psi_n'].sel(time=time).values

                    # Now we need the psin basis of the equilibrium
                    psi_0 = slice['global_quantities.psi_axis']
                    psi_b = slice['global_quantities.psi_boundary']
                    psi_eq = slice['profiles_1d.psi']
                    psin_eq = (psi_eq - psi_0) / (psi_b - psi_0)

                    # Re-interpolate
                    R_interp = interp1e(psin_eq, slice['profiles_1d.r_outboard'])
                    R = R_interp(psin)
                    Z0 = R * 0 + slice[f'profiles_1d.geometric_axis.z'][0]  # need to make sure dimensions match

                    # Check the 2D profiles
                    if slice[f'profiles_2d[0].grid_type.index'] != 1:
                        printw(f"Unknow grid type in ODS's equilibrium. Aborting time slice idx = {ti}")
                        continue
                    RR = slice[f'profiles_2d[0].grid.dim1']
                    ZZ = slice[f'profiles_2d[0].grid.dim2']
                    Bt2D = slice[f'profiles_2d[0].b_field_tor']
                    Br2D = slice[f'profiles_2d[0].b_field_r']
                    Bz2D = slice[f'profiles_2d[0].b_field_z']

                    Bt = RectBivariateSplineNaN(RR, ZZ, Bt2D).ev(R, Z0)
                    Br = RectBivariateSplineNaN(RR, ZZ, Br2D).ev(R, Z0)
                    Bz = RectBivariateSplineNaN(RR, ZZ, Bz2D).ev(R, Z0)
                    Bp = np.sqrt(Br**2 + Bz**2)
                    # there is no Bp2D in standard ODSs for some reason, here we assume atleast cocos are already in order

                for q in self.variables:
                    fit = self[q]
                    if q in ['time']:
                        continue
                    if q == 'rho':
                        if fit_coordinate == 'rho':
                            prof_1d['grid.rho_tor_norm'] = self['rho'].values[idx_use]
                        else:
                            prof_1d['grid.rho_tor_norm'] = fit.sel(time=time).values[idx_use]
                    elif q == 'psi_n':
                        if fit_coordinate == 'psi_n':
                            prof_1d['grid.rho_pol_norm'] = np.sqrt(self['psi_n'].values[idx_use])
                        else:
                            prof_1d['grid.rho_pol_norm'] = np.sqrt(fit.sel(time=time).values[idx_use])
                    elif q == 'n_e':
                        prof_1d['electrons.density_thermal'] = fit.sel(time=time).values[idx_use]
                    elif q == 'T_e':
                        prof_1d['electrons.temperature'] = fit.sel(time=time).values[idx_use]
                    elif q == 'omega_P_e' and core:  # this location is not valid OMAS location for edge profiles
                        prof_1d['electrons.rotation.diamagnetic'] = fit.sel(time=time).values[idx_use]
                    elif '_' in q and q.split('_', 1)[1] in ions:
                        continue

                # thermal ions
                ni = 0
                for ion in ions[::-1]:
                    if ion == 'b' or ion.startswith('fast_'):
                        continue
                    profi = prof_1d[f'ion.{ni}']
                    profi['density_thermal'] = self[f'n_{ion}'].sel(time=time).values[idx_use]
                    if f'T_{ion}' in self:
                        profi['temperature'] = self[f'T_{ion}'].sel(time=time).values[idx_use]
                    ion_details = list(atomic_element(symbol=ion).values())[0]
                    profi['label'] = ion_details['symbol']
                    profi['z_ion'] = float(ion_details['Z_ion'])
                    profi['multiple_states_flag'] = 0
                    profi['element[0].atoms_n'] = 1
                    profi['element[0].z_n'] = float(ion_details['Z'])
                    profi['element[0].a'] = float(ion_details['A'])
                    profi['multiple_states_flag'] = 0
                    if f'V_tor_{ion}' in self and not (f'omega_tor_{ion}' in self and 'R_midplane' in self):
                        profi['velocity.toroidal'] = self[f'V_tor_{ion}'].sel(time=time).values[idx_use]
                    elif f'omega_tor_{ion}' in self and 'R_midplane' in self:
                        profi['velocity.toroidal'] = (self[f'omega_tor_{ion}'].sel(time=time) * self['R_midplane'].sel(time=time)).values[
                            idx_use
                        ]
                    if f'V_pol_{ion}' in self:
                        profi['velocity.poloidal'] = self[f'V_pol_{ion}'].sel(time=time).values[idx_use]
                    if core:  # extra rotation info for the core profiles. (Not valid nodes for edge)
                        if f'omega_P_{ion}' in self:
                            profi['rotation.diamagnetic'] = self[f'omega_P_{ion}'].sel(time=time).values[idx_use]
                        if f'omega_tor_{ion}' in self:
                            profi['rotation_frequency_tor'] = self[f'omega_tor_{ion}'].sel(time=time).values[idx_use]
                        if f'V_pol_{ion}' in self and Bp is not None:
                            # Save to parallel streaming function, this will allow omegp to be calculated from ods
                            profi['rotation.parallel_stream_function'] = self[f'V_pol_{ion}'].sel(time=time).values[idx_use] / Bp[idx_use]

                    # Advance ni; its important that if it is fast ion and the loop-iteration is skipped, then ni do not advance
                    ni += 1

                # fast ions
                for ion in ions:
                    if ion != 'b' and not ion.startswith('fast_'):
                        continue
                    # Get the 'base' ion for the fast population
                    if ion.startswith('fast_'):
                        base_ion = ion.replace('fast_', '')
                    elif ion == 'b':
                        base_ion == '2H1'  # back compat for '_b' notations
                    ion_details = list(atomic_element(symbol=base_ion).values())[0]

                    # Determin the corresponding ion index
                    ni = len(prof_1d['ion'])
                    for nii in prof_1d['ion']:
                        profi = prof_1d[f'ion.{nii}']
                        if profi['label'] == ion_details['symbol']:
                            ni = nii
                            break
                    profi = prof_1d[f'ion.{ni}']

                    # Add fast_ion data.
                    profi['density_fast'] = self[f'n_{ion}'].sel(time=time).values[idx_use]
                    if f'p_{ion}' in self:
                        pfast = self[f'p_{ion}'].sel(time=time)[idx_use]  #'ion' here would have the form 'fast_2H1' for example
                    else:
                        pfast = (
                            self[f'T_{ion}'].sel(time=time).values[idx_use] * constants.e * self[f'n_{ion}'].sel(time=time).values[idx_use]
                        )
                    profi['pressure_fast_perpendicular'] = (
                        1.0 / 3.0 * pfast
                    )  # Assume isotropic fast ions. Also OMAS treats p_xxx_perp as pressure in one of the perp directions, I think.
                    profi['pressure_fast_parallel'] = 1.0 / 3.0 * pfast

                    # Attach atomic data (from base_ion)
                    profi['label'] = ion_details['symbol']
                    profi['z_ion'] = float(ion_details['Z_ion'])
                    profi['multiple_states_flag'] = 0
                    profi['element[0].atoms_n'] = 1
                    profi['element[0].z_n'] = float(ion_details['Z'])
                    profi['element[0].a'] = float(ion_details['A'])
                    profi['multiple_states_flag'] = 0

                if 'Total_Zeff' in self:
                    prof_1d['zeff'] = self['Total_Zeff'].sel(time=time).values[idx_use]

        # Populate total pressure nodes under 'profiles_1d`
        ods.physics_core_profiles_pressures()
        # ods.physics_edge_profiles_pressures() # This function does not exist, but really should.
        return ods

    def model_tree_quantities(self, warn=True, no_update=False, details=False):
        """
        Returns list of MDSplus model_tree_quantities for all species.

        :param warn: [bool] If True, the function will warn if some of the `model_tree_quantities` are missing in
            OMFIT-source/omfit/omfit_classes/omfit_profiles.py and the model tree should be updated

        :param no_update: [bool] If True, the function will return only items that is in the object AND on the model
            tree, and ignore items that is not in model_tree_quantities.

        :return: list of strings
        """
        new_model_tree_quantities = set(model_tree_quantities)
        if not no_update:
            for item in self.variables:
                match = False
                dont_replace = ['T_i_T_e_ratio', 'J_efit_norm']  # Don't make this into T_i_T_{species} ratio please
                for s in model_tree_species:
                    if item not in dont_replace:
                        tmp = item.replace(f'_{s}', '_{species}')
                    if tmp != item:
                        match = True
                        break
                if match:
                    new_model_tree_quantities.add(tmp)
                elif not no_update:
                    new_model_tree_quantities.add(item)

        quant_set = set(model_tree_quantities)
        # using set compare...
        if len(new_model_tree_quantities - quant_set) > 0 and warn:
            import textwrap

            if details:

                printe('WARNING!: Update model_tree_quantities in OMFIT-source/omfit/omfit_classes/omfit_profiles.py')
                printe('WARNING!: and update the OMFIT_PROFS MDSplus model tree')
                printe(f'The missing quantities are {new_model_tree_quantities - quant_set}.')
                printe('-' * 140)
                printe('# fmt: off')
                printe(textwrap.fill(f'model_tree_quantities = {repr(new_model_tree_quantities)}', width=140))
                printe('# fmt: on')
                printe('-' * 140)
            else:
                printe("WARNING!: Profile vars mismatch with model tree!")
                printe("WARNING!: Consider using the 'relaxed' option with to_mds()")
                printe("WARNING!: Or use .model_tree_quantities(details=True) for instructions to update model tree.")
                printe(f"WARNING!: Here are the problem vars -> {new_model_tree_quantities - quant_set}")

        quantities = []
        for item in new_model_tree_quantities:
            if '{' in item:
                for s in model_tree_species:
                    quantities.append(item.format(species=s))
            else:
                quantities.append(item)
        return quantities

    def create_model_tree(self, server, treename='OMFIT_PROFS'):
        """
        Generate MDSplus model tree

        :param server: MDSplus server

        :param treename: MDSplus treename
        """
        from omfit_classes.omfit_mds import OMFITmdsConnection

        conn = OMFITmdsConnection(server)

        quantities = {self.mds_translator(k): None for k in self.model_tree_quantities()}
        quantities['__content__'] = ''
        quantities['__x_coord__'] = ''
        quantities['__coords__'] = ''
        quantities['__dsp_name__'] = ''
        quantities['__attrs__'] = ''
        quantities['__comment__'] = ''
        conn.create_model_tree(treename, '', quantities, clear_subtree=True)

    def check_attrs(self, quiet=False):
        """
        Checks that basic/standard attrs are present. If not, they will be fill with standby values (usually 'unknown')
        Also checks that ints are ints and not int64, which would prevent json from working properly.

        :param quiet: If set to True, the function will not print warnings. By default set to False.
        """

        basic_atts = ['shot', 'produced_by_module', 'produced_by_user']

    def to_mds(
        self,
        server,
        shot,
        times=None,
        treename='OMFIT_PROFS',
        skip_vars=[],
        comment=None,
        tag=None,
        relaxed=False,
        commit=True,
        iri_upload_metadata=None,
    ):
        """
        This script writes the OMFITproflies datase to DIII-D MDSplus and updates d3drdb accordingly

        :param server: MDSplus server

        :param shot: shot to store the data to

        :param treename: MDSplus treename

        :param skip_vars: variables to skip uploading. Array-like

        :param relaxed: if set to True, then the function will only try to upload vars in the model_tree_quantities
            list as recorded at the beginging of this file. If False, then this funct will attempt to upload all
            variables stored in self, and fail if a profile variable cannot be uploaded (usually due there not being a
            corresponding node on the MDSplus tree).

        :param commit (bool): If set to False, the SQL query will not commit the data to the coderunrdb. This is required to be
            false for a jenkins test or else if it tries to write data to SQL database twice it will throw an error.
        :param iri_upload_metadata: optionally, a dictionary with metadata for upload to iri_upload_log table in
            the code run RDB. Certain metadata are determined dynamically. If None, then it will not be logged
            to iri_upload_metadata.

        :return: runid, treename
        """

        if times is None:
            times = self['time'].values

        # Parse comments
        if comment is None:
            comment = self.comment
        else:
            self.comment = comment  # Update object comment to be consistent

        from omfit_classes.omfit_mds import OMFITmdsConnection, translate_MDSserver
        import json
        from omfit_classes.omfit_json import dumper

        conn = OMFITmdsConnection(server)

        if relaxed:
            quantities = self.model_tree_quantities(warn=False, no_update=True)
        else:
            quantities = self.model_tree_quantities()

        quantities = [x for x in quantities if x not in skip_vars]
        # Determine radial coord
        x_coord = None
        if 'psi_n' in self.coords.keys() and 'rho' in self.coords.keys():
            x_coord = 'unclear'
            # raise Exception("Confusion exist in radial coordinate used. Make sure dataset have a single radial coordinate.")
        elif 'psi_n' in self.coords.keys():
            x_coord = 'psi_n'
        elif 'rho' in self.coords.keys():
            x_coord = 'rho'

        # find next available runid in d3drdb for this shot
        from omfit_classes.omfit_rdb import OMFITrdb

        rdb = OMFITrdb(db='code_rundb', server='d3drdb', by_column=True)
        # add data to d3drdb (before MDSplus so that we can get a RUNID, only if it has not been allocated yet)
        data = {
            'shot': shot,
            'experiment': 'DIII-D',
            'run_type': 'user',
            'tree': treename,
            'start_time': np.min(times),
            'stop_time': np.max(times),
            'mdsserver': translate_MDSserver(server, ''),
            'run_comment': comment,
            #'runtag':tag
        }
        #'x_coord': x_coord,
        command = "SpGetNextOmfitProfsID"
        output = rdb.custom_procedure(command, commit=commit, **data)[-1]
        runid = output.run_id
        if runid == -1:
            print("Error fetching available runid from SQL database")
            return runid, treename
        print(f'Writing OMFITprofiles to MDSplus {runid}')

        # write to MDSplus
        subset = self.sel(time=times)
        quantities = conn.write_dataset(
            treename=treename,
            shot=runid,
            subtree='',
            xarray_dataset=subset,
            quantities=quantities,
            translator=lambda x: self.mds_translator(x),
        )
        # Store meta data
        # ====
        conn.write(treename=treename, shot=runid, node='__content__', data=';'.join(quantities))
        conn.write(treename=treename, shot=runid, node='__x_coord__', data=x_coord)

        # Upload meta to IRI table
        if iri_upload_metadata is not None and 'iri_id' in iri_upload_metadata:
            iri_upload_metadata['upload_server'] = translate_MDSserver(server, '')
            iri_upload_metadata['upload_tree'] = treename
            iri_upload_metadata['upload_id'] = runid

            rdb = OMFITrdb(db='code_rundb', server='d3drdb', by_column=True)
            output = rdb.custom_procedure('spNextIRIUploadID', **iri_upload_metadata)
            if output[-1].id == -1:
                printw('WARNING: Profile upload failed to update IRI upload log.')

        coords_string = ''
        disp_name_string = ''
        for quant in quantities:
            coords_string = ';'.join([coords_string, ','.join(self[quant].dims[::-1])])
            # Upload reverses coord order, and above line accounts for it. But if upload behavior changes, this should
            # also change.
            try:
                disp_name = self[quant].attrs['display_name']
            except KeyError:
                disp_name = ''
            disp_name_string = ';'.join([disp_name_string, disp_name])

        # Trim the initial ':' that result from the way this is built
        if len(coords_string) > 1:
            coords_string = coords_string[1:]
        if len(disp_name_string) > 1:
            disp_name_string = disp_name_string[1:]

        conn.write(treename=treename, shot=runid, node='__coords__', data=coords_string)
        conn.write(treename=treename, shot=runid, node='__dsp_name__', data=disp_name_string)
        conn.write(treename=treename, shot=runid, node='__comment__', data=comment)

        attrs_str = json.dumps(self.attrs, default=dumper)
        conn.write(treename=treename, shot=runid, node='__attrs__', data=attrs_str)

        pprint(data)

        return runid, treename

    def mds_translator(self, inv=None):
        """
        Converts strings OMFITprofiles dataset keys to MDSplus nodes less than 12 chars long

        :param inv: string to which to apply the transformation
                    if `None` the transformation is applied to all of the OMFITprofiles.model_tree_quantities for sanity check

        :param reverse: reverse the translation. Used to tranlate MDSplus node names back to OMFITprofile names

        :return: transformed sting or if inv is None the `mapped_model_2_mds` and `mapped_mds_2_model` dictionaries
        """
        mapper = SortedDict()
        mapper['_gradP_Vtor'] = 'gp_Vt'  # special case for 'Er_He_gradP_Vtor'
        mapper['SAWTOOTH_'] = 'ST_'
        mapper['angular_momentum_density'] = 'mom_dens'
        mapper['angular_momentum'] = 'mom'
        mapper['midplane'] = 'mid'
        mapper['omega_gyro_'] = 'gyrof_'
        mapper['omega_'] = 'w_'
        mapper['2H1'] = 'D'
        mapper['4He2'] = 'He'
        mapper['6Li3'] = 'Li'
        mapper['10B5'] = 'B'
        mapper['12C6'] = 'C'
        mapper['14N7'] = 'N'
        mapper['20Ne10'] = 'Ne'
        mapper['since_last'] = '_last'
        mapper['until_next'] = '_next'
        mapper['_total'] = '_tot'
        mapper['T_i_T_e'] = 'TiTe'
        mapper['gradP'] = 'gp'
        mapper['gamma'] = 'gm'
        mapper['_ExB'] = 'eb'
        mapper['psin_'] = 'ps_'
        mapper['raw_'] = 'rw_'
        mapper['axis_value'] = 'r0'

        if inv is not None:
            for match, sub in mapper.items():
                inv = inv.replace(match, sub)
            if len(inv) > 12:
                raise Exception(
                    f'MDSplus OMFITprofiles quantity is longer than 12 chars: {inv}\nUpdate the mds_translator function accordingly'
                )
            return inv
        else:
            model_tree_quantities = self.model_tree_quantities()
            mapped_model_2_mds = SortedDict()
            mapped_mds_2_model = SortedDict()
            for item0 in model_tree_quantities:
                item = item0
                for match, sub in mapper.items():
                    item = item.replace(match, sub)
                if len(item) > 12:
                    raise Exception(f'MDSplus string is longer than 12 chars: {item}')
                if item0 != item and item in model_tree_quantities:
                    raise Exception(f'MDSplus string shadows something else: {item}')
                if item in mapped_mds_2_model:
                    raise Exception(f'Multiple items map to the same quantity: {item0} {mapped_mds_2_model[item]}')
                mapped_model_2_mds[item0] = item
                mapped_mds_2_model[item] = item0
            return mapped_model_2_mds, mapped_mds_2_model

    def from_mds(self, server, runid):
        from omfit_classes.omfit_mds import OMFITmds
        import json

        tree = OMFITmds(server=server, treename='OMFIT_profs', shot=runid)
        contents = tree['__CONTENT__'].data()[0].split(";")
        x_coord = tree['__x_coord__'].data()[0]
        attrs_str = tree['__attrs__'].data()[0]
        coords = tree['__coords__'].data()[0].split(";")
        disp_names = tree['__dsp_name__'].data()[0].split(";")
        comment = tree['__comment__'].data()[0]
        if x_coord not in ['rho', 'psi_n']:
            raise Exception(f"x_coord was recorded as {x_coord}. It is not a recognized radial coordinate.")

        # Get the coords
        n_coord = {}
        for var in ['time', x_coord]:
            if var not in contents:
                # Tranlate exception to something that makes sense to user.
                raise Exception(f"Coordinate {var} missing from MDSplus data!")
            # Coord nodes by convention do not need translation, but might in the future
            dat = tree[var].xarray()
            dat = dat.rename(var)
            dat = dat.rename({'dim_0': var})
            self[var] = dat
            n_coord[var] = len(dat.values)

        for i, var in enumerate(contents):
            if var in ['time', x_coord]:
                # Skip, but process coord label and attrs
                self[var].attrs['display_name'] = disp_names[i]
            else:

                node = self.mds_translator(inv=var)
                dat = tree[node].xarray()
                dat = dat.rename(var)
                # Parse dims, and construct coord translator subset
                ndim_data = len(dat.dims)
                var_coords = coords[i].split(',')
                ndim_coords = len(var_coords)
                if ndim_data != ndim_coords:
                    printw(f"Dimension count does not match record for {var}.")
                else:
                    rename_dict = {}
                    for ii in np.arange(ndim_data):
                        rename_dict[f'dim_{ii}'] = var_coords[ii]
                    dat = dat.rename(rename_dict)
                self[var] = dat

        self.attrs = json.loads(attrs_str)
        self.comment = comment
        self.save()
        return self

    def to_pFiles(self, eq, times=None, shot=None):
        """
        :param eq: ODS() or dict. (OMFITtree() is a dict)  Needs to contain equilibria information, either in the form
            of the ODS with needed eq already loaded, or as OMFITgeqdsk() objects in the Dict with the time[ms] as
            keys. Times for the eq need to be strict matches to profiles times coord.

        :param times: array like. time for which you would like p files to be generated.

        :param shot: int. shot number, only relevant in generating p file names.

        :return: OMFITtree() containing a series of OMFITpfile objs.
        """

        # Generate times if needed
        if times is None:
            try:
                times = self['time'].values
            except KeyError:
                # Just here to add a helpful hint
                printw("Looking like your OMFITprofiles obj is missing 'time'. Is it properly initialized?")
                raise

        # Get shot if it can be found
        if shot is None:
            if 'shot' in self.attrs:
                shot = self.attrs['shot']
            else:
                shot = 0  # Dummy number for p file names.

        # get good_times
        good_times = []
        if isinstance(eq, ODS):
            # Check times
            good_times = [t for t in times if t in eq.time('equilibrium')]  # ODS().time('...') will throw error if time is inconsistent

        elif isinstance(eq, dict):
            for i, time in enumerate(times):
                d3_time = int(time)
                if d3_time in eq:
                    good_times.append(time)
                else:
                    printw(f"Missing eq data for {time}, it will be skipped!")
        else:
            printw("Input arg 'eq' is in unrecognized format. This will fail!")

        good_times = [t for t in good_times if t in self['time'].values]
        good_times = array(good_times)

        if len(good_times) == 0:
            printw("No valid time found! Each timesilce needs profiles and equilibrium.")
            return
        else:
            printd(f"The following time was found to be good: {good_times}")
            printd("pFiles will be produced for these times only.")

        ods = ODS()
        # Now inject eq info, but only for good_times
        if isinstance(eq, ODS):
            prof_ods.equilibrium.time = np.array(good_times)
            for i, time in enumerate(good_times):
                j = np.where(eq.times('equilibrium') == time)
                ods[f'equilibrium.time_slice.{i}'] = eq[f'equilibrium.time_slice.{j}']

            prof_ods.physics_consistent_times()  # Generate missing time array
        elif isinstance(eq, dict):
            for i, time in enumerate(good_times):
                d3_time = int(time)
                ods = eq[d3_time].to_omas(ods=ods, time_index=i)
                # This is not very efficient, but does make to_omas() more standardized. Open to change as needs change.
        ods = self.to_omas(times=good_times, ods=ods)

        out_tree = OMFITtree()
        for i, time in enumerate(good_times):
            d3_time = int(time)
            out_tree[d3_time] = OMFITpFile(f'p{shot:06}.{d3_time:05}').from_omas(ods, time_index=i)

        return out_tree

    def get_xkey(self):
        """
        Get the key of the x-coord associated with this data array.

        :returns: str. key of the x-coord associated with the profiles, like 'psi_n', 'psi' or 'rho'.
        """
        dims = list(self.dims.keys())
        options = ['rho', 'psi_n', 'psi']
        xaxis = [option for option in options if option in dims][0]
        return xaxis

    def Zeff(self, gas='2H1', ni_to_ne=1, xfit='rho', device='DIII-D', update=True, verbose=False):
        """
        Effective charge of plasma.

        Formula: Z_{eff} = \sum{n_s Z_s^2} / \sum{n_s Z_s}

        :return: DataArray.
        """
        result = xarray.Dataset()

        meas_species, meas_ions, meas_ions_with_dens, meas_ions_with_fast = get_species(self)

        # required data
        strt = datetime.datetime.now()
        # For the list of ions with a density measurement
        ions_with_dens = [i for i in meas_ions if 'n_' + i in self]
        chk = self.check_keys(['n_e'] + ['n_{}'.format(i) for i in ions_with_dens], name='Zeff')
        # determine n_i from n_e if there is nothing else available

        if len(ions_with_dens) == 0 and 'n_e' in self:
            if ni_to_ne > 0:
                self['n_' + gas] = ni_to_ne * self['n_e']
                ions_with_dens = [gas]
                printw(
                    f'  WARNING: No ions with a density measurement. Assuming a single ion species:{gas}, setting density n_{gas}={ni_to_ne}*ne'
                )

            else:
                printw('  WARNING: Could not form Zeff. Missing ion densities')
                chk = False
        if not chk:
            return result
        # determine main ion density from quasi-neutrality
        if 'n_' + gas not in self:
            mg, zg = mZ(gas)
            nz = self['n_e'] - np.sum([self['n_' + i].values * mZ(i)[1] for i in ions_with_dens], axis=0)

            # Check if any isotope fraction measurements are available
            H_isotopes = ['1H1', '2H1', '3H1']
            frac_meas = [iso for iso in H_isotopes if f'frac_{iso}' in self]
            if len(frac_meas) == 0:
                # Assume the only hydrogenic species is 'gas', this should be the typical case
                print(f"  Assuming a single main-ion species:{gas}, setting density based on (ne - nz)")
                self[f'n_{gas}'] = nz / zg
                self[f'n_{gas}'].attrs['long_name'] = f'$n_{{gas}}$'
                self[f'n_{gas}'].attrs['units'] = 'm^-3'
                main_ions = [gas]

                keys = [f'dn_{s}_d{xfit}' for s in ['e'] + ions_with_dens]
                if self.check_keys(keys, name=f'dn_{gas}_d{xfit}'):
                    self[f'dn_{gas}_d{xfit}'] = self[f'dn_e_d{xfit}'] - np.sum(
                        [self[f'dn_{i}_d{xfit}'].values * mZ(i)[1] for i in ions_with_dens], axis=0
                    )

            elif len(frac_meas) == 1:
                ion1 = frac_meas[0]
                print(f"  Hydrogenic isotope fraction measurement available: frac_{ion1}")
                if ion1 == '3H1':
                    raise Exception(" Tritium hydrogen fraction provided, not setup for this case")
                # Assume the other hydrogenic ion is either 1H1 or 2H1
                ion2 = '2H1' if ion1 == '1H1' else '1H1'
                # Clip frac so densities dont become 0
                printi(f"  Allocating non impurity electrons between 2 hydrogenic ions: {ion1}, {ion2}")
                frac = np.clip(self[f'frac_{ion1}'].values, 1e-3, 0.999)
                if np.sum(np.invert(np.isfinite(frac))):
                    raise Exception(" Fraction measurement has non finite values in it, fix before proceeding")
                self[f'n_{ion1}'] = nz * frac
                self[f'n_{ion1}'].attrs['long_name'] = f'$n_{{ion1}}$'
                self[f'n_{ion1}'].attrs['units'] = 'm^-3'
                self[f'n_{ion2}'] = nz * (1 - frac)
                self[f'n_{ion2}'].attrs['long_name'] = f'$n_{{ion2}}$'
                self[f'n_{ion2}'].attrs['units'] = 'm^-3'
                main_ions = [ion1, ion2]
                keys = [f'dn_{s}_d{xfit}' for s in ['e'] + ions_with_dens]
                if self.check_keys(keys, name=f'dn_{ion1}_d{xfit} & dn_{ion2}_d{xfit}'):
                    dnz = self[f'dn_e_d{xfit}'] - np.sum([self[f'dn_{i}_d{xfit}'].values * mZ(i)[1] for i in ions_with_dens], axis=0)
                    self[f'dn_{ion1}_d{xfit}'] = dnz * fac
                    self[f'dn_{ion2}_d{xfit}'] = dnz * (1 - fac)
            else:
                raise Exception("Multiple hydrogenic ion fractions specified")
            ions_with_temp = [k for k in meas_ions if not k.startswith('fast') and 'T_' + k in self]

            for cur_mi in main_ions:
                if len(np.where(self['n_' + cur_mi].values <= 0)[0]):
                    printe('  Had to force main ion density to be always positive!')
                    printe('  This will likely present a problem when running transport codes!')
                    self['n_' + cur_mi].values[np.where(self['n_' + cur_mi].values <= 0)] = np.max(self['n_' + cur_mi].values) * 0 + 1
                # If a temperature isnt available for this ion use whatever ion temperature is available
                if (cur_mi not in ions_with_temp) and len(ions_with_temp):
                    # Always prefer T_12C6 if available on DIII-D
                    if is_device(device, 'DIII-D') and ('12C6' in ions_with_temp):
                        T_ref_ion = '12C6'
                    else:
                        T_ref_ion = ions_with_temp[-1]
                    print('- Setting T_{:} equal to T_{:}'.format(cur_mi, T_ref_ion))
                    T_name = f'T_{cur_mi}'
                    self[T_name] = self['T_' + T_ref_ion] * 1
                    long_name = self[f'T_{T_ref_ion}'].attrs.get('long_name', T_name)
                    self[T_name].attrs['long_name'] = long_name.replace(T_ref_ion, cur_mi)
                    if f'dT_{T_ref_ion}_d{xfit}' in self:
                        self[f'dT_{cur_mi}_d{xfit}'] = self[f'dT_{T_ref_ion}_d{xfit}'] * 1
                        self[f'dT_{cur_mi}_d{xfit}'].attrs['units'] = (
                            self[f'dT_{T_ref_ion}_d{xfit}'].attrs.get('units', '?').replace(T_ref_ion, cur_mi)
                        )
                ions_with_dens.append(cur_mi)
        else:
            ions_with_dens.append(gas)

        if verbose:
            print('   > Finding gas density took {:}'.format(datetime.datetime.now() - strt))

        # calculate Zeff (not assuming quasi-neutrality)
        strt = datetime.datetime.now()
        nz_sum = np.sum([self['n_' + i].values * mZ(i)[1] for i in ions_with_dens], axis=0)
        nz2_sum = np.sum([self['n_' + i].values * mZ(i)[1] ** 2 for i in ions_with_dens], axis=0)

        z_eff = nz2_sum / nz_sum + 0 * self['n_e'].rename('Zeff')

        z_eff.attrs['long_name'] = r'$Z_{eff}$'
        if verbose:
            print(
                '   > Finding zeff took {:}'.format(datetime.datetime.now() - strt)
            )  # note without using .values in the sums this takes 10 seconds

        result.update({'Zeff': z_eff, 'Total_Zeff': z_eff * 1})

        if update:
            self.update(result)
        return result

    def pressure(self, species, xfit='rho', name=None, update=True, debug=False):
        """
        Species pressure.

        Formula: P = \sum{n_s T_s}

        :param species: list. Species included in calculation sum.
        :param name: str. subscript for name of result DataArray (i.e. it wil be called p_name)
        :return: DataArray. Pressure (Pa)
        """
        result = xarray.Dataset()

        # default name
        if name is None:
            name = '_'.join(species)
        # standard checks
        species = copy.deepcopy(species)
        good_species = []
        keys = []
        for s in species:
            chk = self.check_keys([f'n_{s}', f'T_{s}'], name=f'pressure of {name}')
            if chk:
                good_species.append(s)
                keys.append(f'n_{s}')
                keys.append(f'T_{s}')
        species = good_species
        if not len(species):
            return result

        # add sum total pressure
        da = 0
        for s in species:
            da = (self['n_' + s] * self['T_' + s] * scipy.constants.e) + da
        da.attrs['long_name'] = r'$p_{' + ','.join(species) + '}$'
        da.attrs['units'] = 'Pa'
        if any(not is_uncertain(self[k].values) for k in keys):
            if debug:
                printw(
                    f' > could not propagate error in pressure due to no std_dev in {[k for k in keys if not is_uncertain(self[k].values)]}'
                )
            da.values = nominal_values(da.values)  # remove error propagation if any fit doesn't include std_dev
        result.update({f'p_{name}': da})

        # add derivative with proper error propagation if available from the fits
        dkeys = [f'd{k}_d{xfit}' for k in keys]
        chk = self.check_keys(dkeys, name=f'pressure derivative for {name}', print_error=debug)
        if chk:
            dda = 0
            for s in species:
                dda = (self[f'dn_{s}_d{xfit}'] * self[f'dT_{s}_d{xfit}'] * scipy.constants.e) + dda
            if any(not is_uncertain(self[k].values) for k in dkeys):
                if debug or True:
                    printw(
                        f' > could not propagate error in pressure due to no std_dev in {[k for k in dkeys if not is_uncertain(self[k].values)]}'
                    )
                dda.values = nominal_values(dda.values)  # remove error propagation if any fit doesn't include std_dev
            dda.attrs['long_name'] = rf'd p_{",".join(species)} / d$\{xfit}$'
            dda.attrs['units'] = f'Pa per {xfit}'
            result.update({f'dp_{name}_d{xfit}': dda})

        if update:
            self.update(result)
        return result

    def inverse_scale_length(self, key, update=True):
        """
        Inverse scale length
        :param key: str. The variable for which the inverse scale length is computed
        :return: Dataset
        """
        result = xarray.Dataset()
        if not self.check_keys([key, 'd' + key + '_drho'], name='Inverse scale length'):
            return result
        val = self[key].values * 1.0
        val[nominal_values(val) == 0] *= np.nan
        isl = -self['d' + key + '_drho'] / val
        isl.attrs['units'] = ''
        isl.attrs['long_name'] = r'$\frac{d' + key + r'/d\rho}{' + key + r'}$'
        result[key + '_isl'] = isl

        if update:
            self.update(result)
        return result

    def log_lambda(self, update=True):
        """
        The Coulomb logarithm: the ratio of the maximum impact parameter to the
        classical distance of closest approach in Coulomb scattering.
        Lambda, the argument, is known as the plasma parameter.
        Formula: \ln \Lambda = 17.3 - \frac{1}{2}\ln(n_e/10^20)+\frac{3}{2}\ln(T_e/eV)
        :return:
        """
        result = xarray.Dataset()

        # approx
        chk = self.check_keys(keys=['n_e', 'T_e'], name='ln(Lambda)')
        if not chk:
            return result
        # assumes n in m^-3, T in eV
        da = 0 * self['n_e'].rename('lnLambda')
        ne = self['n_e'].values
        te = self['T_e'].values
        da.values = 17.3 - 0.5 * unumpy.log(ne / 1.0e20) + 1.5 * unumpy.log(te * 1e-3)
        da.attrs['long_name'] = r'$\ln \Lambda$'
        result.update({'lnLambda': da})

        if update:
            self.update(result)
        return result

    def collisionality(self, s, s2='e', eq=None, update=True):
        """
        Collisionality from J.D. Huba, "NRL FORMULARY", 2011.
        :param s: string. Species.
        :param s2: string. Colliding species (default elecctrons). **Currently not used**
        :return: Dataset
        """
        result = xarray.Dataset()

        if not eq:  # this is required as input in 8_postfit.py
            printe('WARNING!: Collisionality calculation requires an input equilibrium!')

        if self.check_keys(keys=['psi_n', 'n_' + s, 'T_' + s, 'lnLambda'], name='nu_' + s):
            m, Z = mZ(s)
            if s == 'e':
                fac = 2.91e-6
                lbl = '$\\nu_{' + s + '} = 2.91e-12\\/ n_{' + s + '} \\ln \\Lambda} T_{' + s + '}^{-3/2}$'
            else:
                fac = 4.80e-8 / np.sqrt(m / constants.m_u)
                lbl = '$\\nu_{' + s + '} = 4.80e-14\\/ \\mu^{-1/2} Z^4 n_{' + s + '} \\ln \\Lambda} T_{' + s + '}^{-3/2}$'
            nu = fac * (Z**4) * (self['n_' + s] / 1e6) * self.log_lambda()['lnLambda'] * (self['T_' + s]) ** -1.5
            nu.attrs['long_name'] = lbl
            result.update({'nu_' + s: nu})
            # normalize
            vth = usqrt(2 * self['T_' + s] * constants.eV / m)
            dR = self['R_midplane'] - eq['R_maxis']
            dR[np.where(dR < 1.0e-3)] = 1.0e-3
            epsr = dR / eq['R_maxis']
            epsr[np.where(epsr == 0)[0]] = np.nan
            nustar = nu * self['q'] * self['R_midplane'] / (vth * epsr**1.5)
            nustar.attrs['long_name'] = '$\\nu_{*,' + s + '} = \\nu_{' + s + '}  (qR_{midplane} / v_{th,' + s + '} \\epsilon_r^{3/2})$'
            result.update({'nu_star_' + s: nustar})

        if update:
            self.update(result)
        return result

    def spitzer(self, update=True):
        # transverse Spitzer resistivity
        # source: NRL plasma formulary, J. D. Huba, 2009
        result = xarray.Dataset()

        if self.check_keys(keys=['T_e', 'Zeff', 'lnLambda'], name='resistivity'):
            numerical_factor = 1.03e-4  # gives result in Ohm.m
            te = self['T_e']
            zeff = self['Zeff']
            lnlambda = self.log_lambda()['lnLambda']
            resist_mks = numerical_factor * zeff * lnlambda * te**-1.5
            ##Just in case someone needs this someday, here's the cgs version, units are seconds:
            # resist_cgs = 1.15e-14 * zeff * lnlambda * te**-1.5
            resist_mks.attrs['long_name'] = r'$\eta$'
            resist_mks.attrs['units'] = 'Ohm*m'
            result.update({'resistivity': resist_mks})

        if update:
            self.update(result)
        return result

    def plasma_frequency(self, s, relativistic=False, update=True, debug=False):
        """
        Calculate plasma frequency.
        :param s: string. Species.
        :param relativistic: bool. Make a relativistic correction for m_e (not actually the relativistic mass).
        :return : Dataset.
        """
        result = xarray.Dataset()

        if self.check_keys(keys=['n_' + s] + relativistic * ['T_' + s], name='omega_plasma_' + s):
            m, Z = mZ(s)
            if relativistic:
                if s == 'e':
                    m *= usqrt(1 + 5 * self['T_' + s] / 511e3)
                else:
                    printe('  WARNING: No relativistic correction applied for ions')

            if debug:
                Ze2 = (Z * constants.e) ** 2
                n_rename_to_omega_plasma = self['n_' + s].rename('omega_plasma_' + s)
                sqrt_of_n_rename = usqrt(n_rename_to_omega_plasma)
                meps = m * constants.epsilon_0

                print('Ze2 = ', Ze2)
                print('n_rename_to_omega_plasma = ', n_rename_to_omega_plasma)
                print('sqrt_of_n_rename = ', sqrt_of_n_rename)
                print('meps = ', meps)
                print(
                    'shapes of Ze2, n_rename_to_omega_plasma, sqrt_of_n_rename, meps = ',
                    np.shape(Ze2),
                    np.shape(n_rename_to_omega_plasma),
                    np.shape(sqrt_of_n_rename),
                    np.shape(meps),
                )

                omega_plasma = sqrt_of_n_rename * Ze2 * meps
                print('omega_plasma = ', omega_plasma)
                print('shape(omega_plasma) = ', np.shape(omega_plasma))

                omega_plasma = self['n_' + s].rename('omega_plasma_' + s) * 0 + omega_plasma

                print('omega_plasma (after adding attributes back) = ', omega_plasma)
            else:
                omega_plasma = usqrt((self['n_' + s].rename('omega_plasma_' + s) * (Z * constants.e) ** 2) / (m * constants.epsilon_0))
                omega_plasma = (
                    omega_plasma + self['n_' + s].rename('omega_plasma_' + s) * 0
                )  # this last bit is to reattach the dataArray attributes as they will not survive unumpy.sqrt()
                result.update({"omega_plasma_" + s: omega_plasma})

            result.update({"omega_plasma_" + s: omega_plasma})

        if update:
            self.update(result)
        return result

    def gyrofrequency(self, s, mag_field=None, relativistic=False, update=True):
        """
        Calculate gyrofrequency at the LFS midplane.
        :param s: string. Species.
        :param mag_field: external structure generated from OMFITlib_general.mag_field_components
        :param relativistic: bool. Make a relativistic correction for m_e (not actually the relativistic mass).
        :return : Dataset.
        """
        result = xarray.Dataset()

        xkey = self.get_xkey()

        if not mag_field:  # this is required as input in 8_postfit.py
            printe('WARNING!: Gyrofrequency calculation requires a mag_field input! See 8_postfit.py for format.')

        if self.check_keys(keys=['R_midplane'] + relativistic * ['T_' + s], name='omega_gyro_' + s):
            m, Z = mZ(s)
            if relativistic:
                if s == 'e':
                    m *= usqrt(1 + 5 * self['T_' + s] / 511e3)
                else:
                    printe('  WARNING: No relativistic correction applied for ions')

            # magnetic field on the midplane
            index = np.argmin(np.abs(mag_field['Z_grid'][0, :]))
            eq_R0 = mag_field['R_grid'][:, index]
            eq_B0 = mag_field['Bmod_arr'][:, index, :]
            fit_B0 = np.zeros_like(self['R_midplane'].transpose('time', xkey))
            for i, t in enumerate(self['time'].values):
                fit_B0[i, :] = np.interp(self['R_midplane'].isel(time=i), eq_R0, eq_B0[:, i])

            name = "omega_gyro_" + s + '_midplane'
            da = xarray.DataArray(np.abs(Z) * constants.e * fit_B0 / m, coords=self['R_midplane'].coords)
            result.update({name: da})

        if update:
            self.update(result)
        return result

    def xo_cutoffs(self, s, mag_field=None, relativistic=True, update=True):
        """
        Calculate X-mode R and L cutoffs.
        Note, O-mode cutoff is already stored as omega_plasma_e.
        :param s: string. Species.
        :param relativistic: bool. Make a relativistic correction for m_e (not actually the relativistic mass).
        :return : Dataset.
        """
        result = xarray.Dataset()

        if self.check_keys(keys=['R_midplane', 'n_' + s] + relativistic * ['T_' + s], name=s + ' cutoffs'):
            m, Z = mZ(s)
            omega_c = self.gyrofrequency(s, mag_field=mag_field, relativistic=relativistic)['omega_gyro_' + s + '_midplane']
            omega_p = self.plasma_frequency(s, relativistic=relativistic)['omega_plasma_' + s]
            omega_RX = +0.5 * omega_c + 0.5 * usqrt(omega_c**2 + 4 * omega_p**2)
            omega_LX = -0.5 * omega_c + 0.5 * usqrt(omega_c**2 + 4 * omega_p**2)
            result.update(
                {
                    'omega_RX_' + s + '_midplane': omega_RX.rename('omega_RX_' + s + '_midplane'),
                    'omega_LX_' + s + '_midplane': omega_LX.rename('omega_LX_' + s + '_midplane'),
                }
            )

        if update:
            self.update(result)
        return result

    def diamagnetic_frequencies(self, spc, update=True):
        """
        Calculate the diamagnetic frequency, and its density / temperature components.

        Formula: \omega_P = -\frac{T}{nZe}\frac{dn}{d\psi} - \frac{1}{Ze}\frac{dT}{d\psi}

        :param spc: Species for which temperature is fit

        :param update: bool. Set to true to update self, if False, only returns and does not update self.
            Gradients, if missing, will always update though.

        """
        freqs = xarray.Dataset()

        m, Z = mZ(spc)

        # calculate gradients if not avaliable
        if f'dn_{spc}_dpsi' not in self and f'n_{spc}' in self:
            dn_dpsi = self.xderiv('n_' + spc, coord='psi')

        if f'dT_{spc}_dpsi' not in self and f'T_{spc}' in self:
            dT_dpsi = self.xderiv('T_' + spc, coord='psi')

        # density part
        if self.check_keys(keys=[f'n_{spc}', f'T_{spc}'] + [f'dn_{spc}_dpsi'], name=f'omega_N_{spc}'):
            omega_N = -self[f'dn_{spc}_dpsi'] * self[f'T_{spc}'] * constants.eV / (self[f'n_{spc}'] * Z * constants.e)
            omega_N.attrs['long_name'] = r"$\omega_N = -\frac{T}{nZe}\frac{dn}{d\psi}$"
            freqs.update({f'omega_N_{spc}': omega_N})
        # temperature part
        if self.check_keys(keys=[f'T_{spc}'] + [f'dT_{spc}_dpsi'], name=f'omega_T_{spc}'):
            omega_T = -self[f'dT_{spc}_dpsi'] * constants.eV / (Z * constants.e)
            omega_T.attrs['long_name'] = r"$\omega_T = -\frac{1}{Ze}\frac{dT}{d\psi}$"
            freqs.update({f'omega_T_{spc}': omega_T})
        # total
        if len(freqs.data_vars) == 2:
            omega_P = omega_N + omega_T
            omega_P.attrs['long_name'] = r"$\omega_{p," + spc + r"} = -\frac{T}{nZe}\frac{dn}{d\psi} -\frac{1}{Ze}\frac{dT}{d\psi}$"
            freqs.update({f'omega_P_{spc}': omega_P})

        if update:
            self.update(freqs)
        return freqs

    def offset_frequency(self, s, ms=None, propagate_uncertainties=False, update=True):
        """
        Calculate the NTV offset frequency.
        Formula: \omega_NTV0 = - (3.5+/-1.5) * \frac{1}{Ze}\frac{dT}{d\psi}
        :param s: Species for which temperature is fit
        :param ms: Species to use for m,Z (default to fit species)
        """
        freqs = xarray.Dataset()

        if not ms:
            ms = s
        m, Z = mZ(ms)

        if self.check_keys(keys=['T_' + s] + ['dT_' + s + '_dpsi'], name='omega_NTV0_' + s):
            if propagate_uncertainties:
                fac = uncertainties.ufloat(3.5, 1.5)
            else:
                fac = 2.5
            omega_NTV0 = fac * self['dT_' + s + '_dpsi'] * constants.eV / (Z * constants.e)
            omega_NTV0.attrs['long_name'] = r"$\omega_{NTV0} = 2.5 * \frac{1}{Ze}\frac{dT}{d\psi}$"
            freqs.update({'omega_NTV0_' + ms: omega_NTV0})

        # include name os species used for profiles
        if ms != s:
            for key in list(freqs.data_vars.keys()):
                freqs = freqs.rename({key: key + '_' + s})

        if update:
            self.update(freqs)
        return freqs

    def radial_field(self, s, Er_vpol_zero=False, mag_field=None, eq=None, plot_debug_Er_plot=False, xfit='rho', update=True):
        """
        Radial electric field.
        Formula:
        :param s: Species which will be used to calculate Er
        :param mag_field: external structure generated from OMFITlib_general.mag_field_components
        """
        import scipy.interpolate as interp

        if not eq:  # this is required as input in 8_postfit.py
            printe('WARNING!: Er calculation requires an input equilibrium!')

        if not mag_field:  # this is required as input in 8_postfit.py
            printe('WARNING!: Er calculation requires a mag_field input! See 8_postfit.py for format.')

        xkey = self.get_xkey()
        species, ions, ions_with_dens, ions_with_fast = get_species(self)

        # Need to double check the logic of this, should the data be overwritten by zeros each time?
        # May be an issue with merging otherwise
        # req_data = ['V_pol_'+s,'T_'+s, 'n_'+s,'omega_tor_'+s]
        gradP_term = True if self.check_keys(keys=['T_' + s, 'n_' + s], name='Er_{}_gradP'.format(s), print_error=False) else False
        Vtor_term = True if self.check_keys(keys=['omega_tor_' + s], name='Er_{}_Vtor'.format(s), print_error=False) else False
        Vpol_term = True if self.check_keys(keys=['V_pol_' + s], name='Er_{}_Vpol'.format(s), print_error=False) else False
        if Er_vpol_zero:
            Vpol_term = True  # Assume Vpol = 0 if it does not exist
        Er_term = True if (gradP_term and Vtor_term and Vpol_term) else False

        # Extract mass, element and Z from the name of the impurity, then change to my naming convention
        m, Z = mZ(s)
        mass, Z_imp, impurity = m, Z, s
        print(' * Performing Er calculation for {}, mass:{:g}, Z:{}'.format(impurity, mass, Z_imp))

        Er_other_species = False
        for s_tmp in species:
            if 'Er_{}'.format(s_tmp) in self:
                Er_other = self['Er_{}'.format(s_tmp)].values
                Er_other_species = True
                print(' ' * 4 + 'Er already available from {}'.format(s_tmp))

        if (not Er_term) and (not Vpol_term) and (not Vtor_term) and (not gradP_term):
            return {}

        # P [N/m2] = (n/V) [m-3] T [J=Nm], for P in N/m2 need to make sure ni is in m-3 and ti is in Joules
        # for grad P we need to know the radius of each rho point (varies with time.. need to loop through time)
        # from eq we know R(rho)
        # We have the rho values of the profiles i.e ti_rho, we want to know what R they correspond to
        # Problem here is that np.interp is expecting a monotonic rho.
        # Need to split into cases on the HFS and LFS
        rho = self['rho'].values
        ntimes = self['time'].shape[0]
        nrho = self[xkey].shape[0]

        profile_Rmid_derived = np.zeros((ntimes, nrho), dtype=float)
        for i in range(ntimes):
            profile_Rmid_derived[i, :] = self['R_midplane'].isel(time=i).values
        # r_mid = R_midplane-R_midplane[0]
        r_mid = self['R_midplane'] * 0
        for i in range(ntimes):
            r_mid[i] = self['R_midplane'][i] - self['R_midplane'][i][0]
        # print(r_mid)
        if gradP_term:
            ti_values = self['T_{}'.format(impurity)].values  # eV
            ni_values = self['n_{}'.format(impurity)].values  # m-3
            pi_values = ni_values * (ti_values * constants.e)
            gradP_arr = pi_values * 0
            coords = self['T_{}'.format(impurity)].coords
        if Vpol_term:
            if Er_vpol_zero:
                pol_rot_data = np.zeros((ntimes, nrho), dtype=float)
                coords = self[next(iter(self.data_vars.keys()))].coords
            else:
                V_pol_DA = self['V_pol_{}'.format(impurity)]
                pol_rot_data = +V_pol_DA.values
                coords = V_pol_DA.coords

        # This is required if rho is 1D which is the case when the fits are done on rho (as opposed to psiN)
        if len(rho.shape) == 1:
            rho = np.tile(rho, (ntimes, 1))

        # Computation saving : can get away with just interpolating on the midplane
        midplane_ind = int(np.argmin(np.abs(mag_field['Z_grid'][0, :])))

        # Find the R values for the profiles vs time
        R_mag_axis_fun = interp1e(eq['time'].values, eq['profile_R_midplane'].values[0])
        iz0 = np.argmin(np.abs(eq['Z'].values))
        x = eq[xkey].values[:, iz0, :]
        r = (eq['R'].values[:, np.newaxis] * np.ones(x.shape)).T.ravel()
        t = (eq['time'].values[np.newaxis, :] * np.ones(x.shape)).T.ravel()
        x = x.T.ravel()
        if len(eq['time'].values) == 1:  # need finite spread for linear interp
            lt = len(t)
            x = np.tile(x, 2)
            t = np.tile(t, 2)
            r = np.tile(r, 2)
            t[lt:] += 1
            t[:lt] -= 1
            R_mag_axis = eq['profile_R_midplane'].values[0]
        else:
            R_mag_axis = R_mag_axis_fun(t)

        valid = (r > R_mag_axis) & isfinite(x) & isfinite(t) & isfinite(r)
        R_fun = LinearNDInterpolator(list(zip(x[valid], t[valid])), r[valid])
        R_near = NearestNDInterpolator(list(zip(x[valid], t[valid])), r[valid])
        points = np.reshape(np.meshgrid(self[xkey].values, self['time'].values), (2, -1)).T
        profile_R = R_fun(points)
        fill = isnan(profile_R)
        profile_R[fill] = R_near(points[fill])
        profile_R = profile_R.reshape((ntimes, nrho))

        if Vtor_term:
            omega_tor_DA = self['omega_tor_{}'.format(impurity)]
            omega_tor = omega_tor_DA.values
            tor_data = omega_tor * profile_R
            coords = omega_tor_DA.coords

        if gradP_term:
            # What to do about the ones that are on the HFS?
            dR = np.gradient(profile_R, axis=-1)
            # Modify the innermost pi_values so that dP will always be 0 on axis
            dP = ugrad1(pi_values)

            # Set onaxis dP to zero
            dP[:, 0] = 0
            # Need to make sure that dR is non zero, replace values of where dR=0 with min(positive dR)
            if not np.any(dR > 0):
                printe('gradP term in Er calculation had errors.  Bad equilibrium?')
            eps = 1e-9
            dR[dR <= eps] = np.min(dR[dR > eps])
            gradP_arr = dP / dR

        # Figure out the Bt, Bp values for each of the radii x time
        lt = len(eq['time'].values)
        in_R = eq['R'].values
        in_t = eq['time'].values
        in_Bt = +mag_field['Bt_arr'][:, midplane_ind, :]
        in_Bp = +mag_field['Bp_arr'][:, midplane_ind, :]
        # need finite spread in time for RegularGridInterpolator otherwise sometimes it returns nan with a single timeslice
        # Create a dummy spread in time with the same field data for both times
        if lt == 1:
            nR = in_Bt.shape[0]
            in_t = np.tile(in_t, 2)
            # Create a spread in time
            in_t[lt:] += 1
            in_t[:lt] -= 1
            cor_size = np.ones((nR, 2), dtype=float)
            in_Bt = (in_Bt[:, 0])[:, np.newaxis] * cor_size
            in_Bp = (in_Bp[:, 0])[:, np.newaxis] * cor_size
        Bt_midplane_fun = RegularGridInterpolator((in_R, in_t), in_Bt, bounds_error=False, fill_value=None)
        Bp_midplane_fun = RegularGridInterpolator((in_R, in_t), in_Bp, bounds_error=False, fill_value=None)
        # Assemble a set of profile_R, time values for interpolating Bt and Bp
        rt_points = list(zip(profile_R.flatten(), np.repeat(self['time'].values, profile_R.shape[1])))
        Bt_vals_midplane = Bt_midplane_fun(rt_points).reshape((ntimes, nrho))
        Bp_vals_midplane = Bp_midplane_fun(rt_points).reshape((ntimes, nrho))
        RBp_vals_midplane = profile_R * Bp_vals_midplane

        outputs = {}
        outputs_attrs = {}
        if gradP_term:
            outputs['Er_' + s + '_gradP'] = gradP_arr / (Z_imp * constants.e * ni_values)
            outputs_attrs['Er_' + s + '_gradP'] = {'units': 'V/m'}
        if Vtor_term:
            outputs['Er_' + s + '_Vtor'] = tor_data * Bp_vals_midplane
            outputs_attrs['Er_' + s + '_Vtor'] = {'units': 'V/m'}
        if Vpol_term:
            outputs['Er_' + s + '_Vpol'] = -pol_rot_data * Bt_vals_midplane
            outputs_attrs['Er_' + s + '_Vpol'] = {'units': 'V/m'}
        if Vtor_term and Vpol_term:
            outputs['Er_' + s + '_VxB'] = -pol_rot_data * Bt_vals_midplane + tor_data * Bp_vals_midplane
            outputs_attrs['Er_' + s + '_VxB'] = {'units': 'V/m'}
        if Er_term:
            outputs['Er_' + s] = outputs['Er_' + s + '_gradP'] + outputs['Er_' + s + '_Vtor'] + outputs['Er_' + s + '_Vpol']
            outputs_attrs['Er_' + s] = {'units': 'V/m'}
        if Er_other_species and gradP_term and Vtor_term:
            outputs['Er_' + s + '_Vpol'] = Er_other - outputs['Er_' + s + '_Vtor'] - outputs['Er_' + s + '_gradP']
            outputs_attrs['Er_' + s + '_Vpol'] = {'units': 'V/m'}
            outputs['V_pol_' + s] = -1.0 * outputs['Er_' + s + '_Vpol'] / Bt_vals_midplane
            outputs_attrs['V_pol_' + s] = {'units': 'm/s'}
        if gradP_term and Vtor_term:
            outputs['Er_' + s + '_gradP_Vtor'] = outputs['Er_' + s + '_gradP'] + outputs['Er_' + s + '_Vtor']
            outputs_attrs['Er_' + s + '_gradP_Vtor'] = {'units': 'V/m'}

        if plot_debug_Er_plot:
            fig, ax = plt.subplots(nrows=7, sharex=True)
            for i in range(ntimes):
                clr = plt.cm.viridis(float(i) / ntimes)
                x_axis_R = False
                if x_axis_R:
                    x = profile_R[i, :]
                    ax[-1].set_xlabel('R')
                else:
                    x = rho[i, :]
                    ax[-1].set_xlabel('rho')
                    for cur_ax in ax:
                        cur_ax.axvline(1)
                cnt = 0
                ax[cnt].plot(x, nominal_values(ni_values[i, :]), color=clr)
                ax[cnt].set_ylabel('n')
                cnt += 1
                ax[cnt].plot(x, nominal_values(pi_values[i, :]), color=clr)
                ax[cnt].set_ylabel('P')
                cnt += 1
                ax[cnt].plot(x, np.gradient(nominal_values(pi_values[i, :])) / np.gradient(rho[i, :]), color=clr)
                ax[cnt].set_ylabel('dP/drho')
                cnt += 1

                ax[cnt].plot(x, np.gradient(rho[i, :]) / np.gradient(profile_R[i, :]), color=clr)
                ax[cnt].set_ylabel('drho/dR')
                ax[cnt].plot(x, np.gradient(rho[i, :]) / np.gradient(profile_Rmid_derived[i, :]), color=clr, ls='--')
                ax[cnt].set_ylabel('drho/dR')
                cnt += 1
                ax[cnt].plot(x, nominal_values(gradP_arr[i, :]), color=clr)
                ax[cnt].set_ylabel('dP/dR')
                cnt += 1
                ax[cnt].plot(x, nominal_values(outputs['Er_' + s + '_gradP'][i, :]), color=clr)
                ax[cnt].set_ylabel('Er_{}_gradP'.format(s))
                cnt += 1
                ax[0].set_title("{}".format(s))
            fig.canvas.draw()

        output_DS = xarray.Dataset()
        # should really only output true flux functions!
        # need to include Omega and K

        # add omega_E_gradP, omega_E_Vtor and omega_E_Vpol to see the different contributions
        # calculate ExB shearing rate using Waltz-Miller derivation
        # gamma_ExB=(r/q)*omega_E_drho*(drho/dr)
        # calculation is made for the midplane
        if gradP_term:
            omega_E_gradP = xarray.DataArray(outputs['Er_' + s + '_gradP'] / RBp_vals_midplane, coords=coords)
            gamma_ExB_gradP = -1 * (r_mid / self['q']) * ugrad1(omega_E_gradP) / ugrad1(r_mid)
            gamma_ExB_gradP.attrs['long_name'] = r'$\gamma_{E,' + s + r'} = \frac{r}{q} \frac{dE_r}{d\rho} \frac{d\rho}{dr}$'
            gamma_ExB_gradP.attrs['units'] = '1/s'
            output_DS.update({'gamma_ExB_' + s + '_gradP': gamma_ExB_gradP})
        if Vtor_term:
            omega_E_Vtor = xarray.DataArray(outputs['Er_' + s + '_Vtor'] / RBp_vals_midplane, coords=coords)
            gamma_ExB_Vtor = -1 * (r_mid / self['q']) * ugrad1(omega_E_Vtor) / ugrad1(r_mid)
            gamma_ExB_Vtor.attrs['long_name'] = r'$\gamma_{E,' + s + r'} = \frac{r}{q} \frac{dE_r}{d\rho} \frac{d\rho}{dr}$'
            gamma_ExB_Vtor.attrs['units'] = '1/s'
            output_DS.update({'gamma_ExB_' + s + '_Vtor': gamma_ExB_Vtor})
        if Vpol_term:
            omega_E_Vpol = xarray.DataArray(outputs['Er_' + s + '_Vpol'] / RBp_vals_midplane, coords=coords)
            gamma_ExB_Vpol = -1 * (r_mid / self['q']) * ugrad1(omega_E_Vpol) / ugrad1(r_mid)
            gamma_ExB_Vpol.attrs['long_name'] = r'$\gamma_{E,' + s + r'} = \frac{r}{q} \frac{dE_r}{d\rho} \frac{d\rho}{dr}$'
            gamma_ExB_Vpol.attrs['units'] = '1/s'
            output_DS.update({'gamma_ExB_' + s + '_Vpol': gamma_ExB_Vpol})
        if Er_term:
            omega_E = xarray.DataArray(outputs['Er_' + s] / RBp_vals_midplane, coords=omega_tor_DA.coords)
            omega_E.attrs['long_name'] = r'$\omega_{E,' + s + r'} = E_r/RB_p$'
            omega_E.attrs['units'] = 'rad/s'
            output_DS.update({'omega_E_' + s: omega_E})
            gamma_ExB = -1 * (r_mid / self['q']) * ugrad1(omega_E) / ugrad1(r_mid)
            gamma_ExB.attrs['long_name'] = r'$\gamma_{E,' + s + r'} = \frac{r}{q} \frac{dE_r}{d\rho} \frac{d\rho}{dr}$'
            gamma_ExB.attrs['units'] = '1/s'
            output_DS.update({'gamma_ExB_' + s + '': gamma_ExB})

            # Electrostatic potential -dPhi/dpsi = Er/RBp
            # cumtrapz is the only method numerically accurate enough to recover omega_E via. deriv()
            # Perform the integral
            epot_s = -1.0 * cumtrapz(omega_E.values, x=self['psi'].values, axis=1)
            if xfit == 'rho':
                epotx = self['rho'].values
            elif xfit == 'psi_n':
                epotx = self['psi_n'].values
            if ntimes > 1:
                print(' * Electrostatic Potential (in time)')
                # Get boundary condition to remove making Phi(1.0) == 0.0
                epotBC = URegularGridInterpolator((self['time'].values, epotx), epot_s)((self['time'].values, 1.0))
                # Remove boundary condition
                epot_s -= epotBC[:, np.newaxis]
            else:
                print(' * Electrostatic Potential (snapshot)')
                epot_s -= uinterp1d(epotx, epot_s[0, :])(1.0)
            epot = xarray.DataArray(epot_s, coords=omega_tor_DA.coords)
            epot.attrs['long_name'] = 'Electrostatic Potential ' + s
            epot.attrs['units'] = 'V'
            output_DS.update({'epot_' + s: epot})

        for key, val in outputs.items():
            DA = xarray.DataArray(val, coords=coords)
            if key in outputs_attrs:
                for attr_name, attr_val in outputs_attrs[key].items():
                    DA.attrs[attr_name] = attr_val
            output_DS.update({key: DA})

        if update:
            self.update(output_DS)
        return output_DS

    def omega_perp(self, s, eq=None, update=True):
        """
        Perpendicular rotation frequency.

        Formula: \omega_{perp} = \omega_{E} + \sigma*\omega_P

        :param s: str. Species.
        :return: Dataset.

        """
        result = xarray.Dataset()

        if not eq:  # this is required as input in 8_postfit.py
            printe('WARNING!: Er calculation requires an input equilibrium!')

        species, ions, ions_with_dens, ions_with_fast = get_species(self)

        key_e = 'omega_E'
        for ie in species:
            if key_e + '_' + ie in self:
                key_e += '_' + ie
        if self.check_keys(keys=['psi_n'] + [key_e, 'omega_P_' + s], name='omega_perp_' + s):
            print('  > Using ' + key_e)
            helicity = np.sign(eq['plasma_current'])  # Correct on all machines?
            omega_perp = self[key_e] + self['omega_P_' + s]
            omega_perp.attrs['long_name'] = r'$\omega_{\perp,' + s + r'} = \omega_{E} + \omega_P$'
            result.update({'omega_perp_' + s: omega_perp})
            # J. Callen EPS 2016 - "true perpendicular rotation"
            if s == 'e' and self.check_keys(keys=['Zeff'], name='omega_alpha_' + s):
                # alpha coefficient from Eq. (25) in J.D. Callen, C.C. Hegna, and A.J. Cole, Nuclear Fusion 53, 113015 (2013).
                Zeff = self['Zeff']
                alphahat_flutt = 1 + (5 / 9.0) * (
                    ((45 * np.sqrt(2) / 16.0) * Zeff + (33.0 / 16.0) * Zeff**2)
                    / (1 + (151 * np.sqrt(2) / 72.0) * Zeff + (217 / 288.0) * Zeff**2)
                )
                omega_alpha = omega_perp + (alphahat_flutt - 1) * self['omega_T_e']
                omega_alpha.attrs['long_name'] = r'$\omega_{\alpha,e} = \omega_\perp + (\hat{\alpha}^{flutt}_\nu-1) \omega_{T,e}$'
                result.update({'omega_alpha_e': omega_alpha})

        if update:
            self.update(result)
        return result

    def angular_momentum(self, s, gas='2H1', xfit='rho', update=True):
        """
        Angular momentum.

        Formula: L_{\phi} = m * n * \omega_{tor} * <R^2>

        :param s: str. Species.
        :return: Dataset.

        """
        result = xarray.Dataset()

        wkey = 'omega_tor_' + s

        ions_with_rot = [key.replace('omega_tor_', '') for key in self.variables if key.startswith('omega_tor') and key != 'omega_tor_e']

        # common to measure an impurity rotation
        if s == gas:
            if wkey + '_KDG' in self:
                wkey = wkey + '_KDG'
                printi('  > Using KDG rotation for {:}'.format(s))
            elif wkey not in self and len(ions_with_rot) == 1:  # don't know which to choose if there are more than 1
                wkey = 'omega_tor_' + ions_with_rot[0]

        if self.check_keys(keys=['avg_R**2', 'avg_vp', 'geo_psi', 'n_' + s, wkey], name='angular_momentum_' + s):
            m, Z = mZ(s)
            # angular momentum density
            dlphi = m * self['n_' + s] * self[wkey] * self['avg_R**2']
            dlphi.attrs['long_name'] = r'$L_{\phi,' + s + r'} = m n \omega_{tor} <R^2>$'
            dlphi.attrs['units'] = 'Nms / m^3'
            # volume intagral (copied from omfit_classes.fluxSurface)
            lphi = integrate.cumtrapz(self['avg_vp'] * dlphi, self['geo_psi'], initial=0)
            vlphi = 1 * dlphi  # a DataArray like the others
            vlphi.values = lphi
            vlphi.attrs['long_name'] = r'$L_{\phi,' + s + r'} = \int_0^' + xfit + r' dV m n \omega_{tor} <R^2>$'
            vlphi.attrs['units'] = 'Nms'

            result.update({'angular_momentum_density_' + s: dlphi, 'angular_momentum_' + s: vlphi})

            # collect the total
            if 'angular_momentum_density' in self:
                self['angular_momentum_density'] += dlphi
            else:
                self['angular_momentum_density'] = 1.0 * dlphi
            self['angular_momentum_density'].attrs['long_name'] = r'$L_{\phi} = \sum_s m_s n_s \omega_{tor,s} <R^2>$'
            self['angular_momentum_density'].attrs['units'] = 'Nms / m^3'
            if 'angular_momentum' in self:
                self['angular_momentum'] += vlphi
            else:
                self['angular_momentum'] = 1.0 * vlphi
            self['angular_momentum'].attrs['long_name'] = r'$L_{\phi} = \int_0^' + xfit + r' dV \sum_s m_s n_s \omega_{tor,s} <R^2>$'
            self['angular_momentum'].attrs['units'] = 'Nms'

            # time derivative, with separate density and velocity terms
            if 'dn_{:}_dt'.format(s) in self:
                dlphidtn = m * self['dn_{:}_dt'.format(s)] * self[wkey] * self['avg_R**2']
                dlphidtn.attrs['long_name'] = r'$L_{\phi,' + s + r',t} = m dn/dt \omega_{tor} <R^2>$'
                dlphidtn.attrs['units'] = 'Nm / m^3'
                lphidtn = integrate.cumtrapz(self['avg_vp'] * dlphidtn, self['geo_psi'], initial=0)
                vlphidtn = 1 * dlphi
                vlphidtn.values = lphidtn
                vlphidtn.attrs['long_name'] = r'$L_{\phi,' + s + r',t} = \int_0^' + xfit + r' dV m dn/dt \omega_{tor} <R^2>$'
                vlphidtn.attrs['units'] = 'Nm'
                dltotdtn = self.get('dangular_momentum_density_dt_n', 0) + dlphidtn
                dltotdtn.attrs['long_name'] = r'$L_{\phi,t} = m dn/dt \omega_{tor} <R^2>$'
                dltotdtn.attrs['units'] = 'Nm / m^3'
                vltotdtn = self.get('dangular_momentum_dt_n', 0) + vlphidtn
                vltotdtn.attrs['long_name'] = r'$L_{\phi,t} = \int_0^' + xfit + r' dV m dn/dt \omega_{tor} <R^2>$'
                vltotdtn.attrs['units'] = 'Nm'
                result.update(
                    {
                        'dangular_momentum_density_{:}_dt_n'.format(s): dlphidtn,
                        'dangular_momentum_{:}_dt_n'.format(s): dlphidtn,
                        'dangular_momentum_density_dt_n': dltotdtn,
                        'dangular_momentum_dt_n': vltotdtn,
                    }
                )
            if 'd{:}_dt'.format(wkey) in self:
                dlphidtw = m * self['n_' + s] * self['d{:}_dt'.format(wkey)] * self['avg_R**2']
                dlphidtw.attrs['long_name'] = r'$L_{\phi,' + s + r',t} = m n d\omega_{tor}/dt <R^2>$'
                dlphidtw.attrs['units'] = 'Nm / m^3'
                lphidtw = integrate.cumtrapz(self['avg_vp'] * dlphidtw, self['geo_psi'], initial=0)
                vlphidtw = 1 * dlphi
                vlphidtw.values = lphidtw
                vlphidtw.attrs['long_name'] = r'$L_{\phi,' + s + r',t} = \int_0^' + xfit + r' dV m n d\omega_{tor}/dt <R^2>$'
                vlphidtw.attrs['units'] = 'Nm'
                dltotdtw = self.get('dangular_momentum_density_dt_v', 0) + dlphidtw
                dltotdtw.attrs['long_name'] = r'$L_{\phi,t} = m n d\omega_{tor}/dt <R^2>$'
                dltotdtw.attrs['units'] = 'Nm / m^3'
                vltotdtw = self.get('dangular_momentum_dt_v', 0) + vlphidtw
                vltotdtw.attrs['long_name'] = r'$L_{\phi,t} = \int_0^' + xfit + r' dV m n d\omega_{tor}/dt <R^2>$'
                vltotdtw.attrs['units'] = 'Nm'
                result.update(
                    {
                        'dangular_momentum_density_{:}_dt_v'.format(s): dlphidtw,
                        'dangular_momentum_{:}_dt_v'.format(s): dlphidtw,
                        'dangular_momentum_density_dt_v': dltotdtw,
                        'dangular_momentum_dt_v': vltotdtw,
                    }
                )

                if 'dn_{:}_dt'.format(s) in self:
                    result.update(
                        {
                            'dangular_momentum_density_{:}_dt_nv'.format(s): dlphidtn + dlphidtw,
                            'dangular_momentum_{:}_dt_nv'.format(s): dlphidtn + dlphidtw,
                            'dangular_momentum_density_dt_nv': dltotdtn + dltotdtw,
                            'dangular_momentum_dt_nv': vltotdtn + vltotdtw,
                        }
                    )

        if update:
            self.update(result)
        return result

    def xderiv(self, key, coord='psi', update=True):
        """
        Returns the derivative of the value corresponding to key on the spatial coordinate coord.

        :param key: str. The variable

        :param coord: str. The radial coordinate with respect to which the derivative is taken

        :param update: bool. Set to true to update self, if False, only returns and does not update self.

        :return: Dataset
        """
        result = xarray.Dataset()

        xkey = self.get_xkey()

        if not self.check_keys([key, coord], name=f'd{key}_d{coord}'):
            return result

        dc = np.gradient(np.atleast_2d(self[coord].values), axis=-1)
        dkey = 'd' + key + '_d' + xkey
        if dkey in self and any(isfinite(v) for v in nominal_values(self[dkey].values).flat) and coord != xkey:
            # if we have derivative UQ from the fit method, keep it and just swap coordinates
            dx = np.gradient(np.atleast_2d(self[xkey].values), axis=-1)
            dkdc = DataArray(self[dkey] * (dx / dc), coords=self[key].coords)
        else:
            # otherwise we have to calculate the derivative numerically - huge uncertainties when propagated
            try:
                dkdc = DataArray(ugrad1(self[key].values) / dc, coords=self[key].coords)
            except ZeroDivisionError:  # This happens if dc array have 0s and self[key].values is a uarray/has uncertainty.
                i_bad = dc == 0
                dc[i_bad] = 1
                dkdc_arr = ugrad1(self[key].values) / dc
                dkdc_arr[i_bad] = ufloat(np.nan, np.nan)
                dkdc = DataArray(ugrad1(self[key].values) / dc, coords=self[key].coords)
        if coord in ['rho', 'psi_n']:
            dkdc.attrs['units'] = self[key].attrs.get('units', '')
        dkdc.attrs['long_name'] = r'd{:} / d$\{:}$'.format(key, coord)
        result['d' + key + '_d' + coord] = dkdc

        if update:
            self.update(result)
        return result

    def find_pedestal(self, data_array, der=True, update=True):
        """
        Find the pedestal extent and values.

        :param data_array: DataArray. 2D fit/self profiles.
        :param der: bool. Find extent of high-derivative region (default is to find edge "bump" feature.

        :return: Dataset. Edge feature inner/center/outer radial coordinates and corresponding values.

        """
        result = xarray.Dataset()

        xkey = self.get_xkey()

        # get x,y values
        da = data_array.transpose('time', xkey)
        x = da[xkey].values
        ys = nominal_values(da.values)
        if der:
            ys = np.gradient(ys, axis=1) / np.gradient(x)
        # find bump feature (start, middle, stop) indexes
        indxs = np.apply_along_axis(find_feature, 1, ys, x=x, M=0.01, k=5)
        # get the corresponding x,y points
        xpts = np.array([x[i] for i in indxs]).T
        ypts = np.array([y[i] for y, i in zip(da.values, indxs)]).T
        # check for cases in which no feature was found (indexes are 0 or maximum)
        nx = x.shape[0]
        ok = []
        for i, j, k in indxs:
            if i in [0, nx] or k in [0, nx]:
                ok.append(np.nan)
            else:
                ok.append(1.0)

        # collect named DataArrays in a Dataset
        for i, key in enumerate(['inner', 'center', 'outer']):
            xname = '{:}_pedestal_{:}_{:}'.format(da.name, key, xkey)
            yname = '{:}_pedestal_{:}_{:}'.format(da.name, key, 'value')
            xda = xarray.DataArray(xpts[i] * ok, dims=['time'], coords={'time': da['time'].values}, name=xname)
            yda = xarray.DataArray(ypts[i] * ok, dims=['time'], coords={'time': da['time'].values}, name=yname)
            result.update({xname: xda, yname: yda})

        if update:
            self.update(result)
        return result

    def pedestal_mwidth(key):
        """
        Calculate the width of the pedestal in meters at the magnetic axis "midplane".

        :param key: str. Quantity that the pedestal extent has been calculated for.
        :return: Dataset. Time evolution of pedestal width.

        """

        xkey = self.get_xkey()

        # standard check
        if not self.check_keys(
            [xkey, 'R_midplane', key + '_pedestal_inner_' + xkey, key + '_pedestal_outer_' + xkey], name=key + ' pedestal width'
        ):
            return {}
        # calculate R_midplane width at each time
        width = []
        for t in self['time']:
            rin = self['R_midplane'].sel(**{'time': t, xkey: self[key + '_pedestal_inner_' + xkey].sel(time=t)})
            rout = self['R_midplane'].sel(**{'time': t, xkey: self[key + '_pedestal_outer_' + xkey].sel(time=t)})
            width.append(rout - rin)
        # form DataArray
        result = xarray.DataArray(width, dims=['time'], coords={'time': self['time'].values}, name=key + '_pedestal_width_R_midplane')
        result.attrs['long_name'] = xkey + ' pedestal width in meters at the midplane'
        result.attrs['units'] = 'm'

        if update:
            self.update(result)
        return result

    def calc_intrinsic_rotation(self, eq=None, update=True):
        """
        Evaluation of the omega_intrinsic function

        :return: omega_intrinsic
        """
        result = xarray.Dataset()

        if not eq:  # this is required as input in 8_postfit.py
            printe('WARNING!: Er calculation requires an input equilibrium!')

        chk = self.check_keys(
            keys=['geo_R', 'geo_a', 'rho', 'T_e', 'T_2H1', 'avg_q', 'avg_fc', 'avg_Btot', 'R_midplane', 'T_e_pedestal_inner_rho'],
            name='TSD & AA intrinsic rotation model',
        )
        if not chk:
            return result
        da = 0.0 * self['time'].rename('omega_ped_TSD')
        for itime, time in enumerate(self['time']):
            derivedt = self.isel(time=itime)
            eqt = eq.isel(time=itime)
            rho = derivedt['rho'].values
            derivedt = derivedt.isel(rho=np.where(rho <= 1)[0])
            geo_R = derivedt['geo_R'].values[-1]
            geo_a = derivedt['geo_a'].values[-1]
            geo_Rx = eqt['R_xpoint'].values
            rho = derivedt['rho'].values
            I_p_sgn = np.sign(eqt['plasma_current'].values)
            Te = nominal_values(derivedt['T_e'].values)
            Ti = nominal_values(derivedt['T_2H1'].values)
            q = nominal_values(derivedt['avg_q'].values)
            fc = nominal_values(derivedt['avg_fc'].values)
            B0 = nominal_values(derivedt['avg_Btot'].values[0])
            R_mp = nominal_values(derivedt['R_midplane'].values)
            rhoPed = derivedt['T_e_pedestal_inner_rho'].values
            rhoSep = 1.0  # derivedt['T_e_pedestal_outer_rho'].values

            # Call function with inputs
            da.values[itime] = utils_fusion.intrinsic_rotation(geo_a, geo_R, geo_Rx, R_mp, rho, I_p_sgn, Te, Ti, q, fc, B0, rhoPed, rhoSep)
            da.attrs['long_name'] = 'Tim Stoltzfus-Dueck & Arash Ashourvan intrinsic rotation model'
            da.attrs['units'] = 'rad/s'
            result.update({'omega_ped_TSD': da})

        if update:
            self.update(result)
        return result

    def P_rad_int(self, update=True):
        """
        Volume integral of the total radiated power

        Formula: P_{rad,int} = \int{P_{rad}}

        :return:
        """
        result = xarray.Dataset()

        chk = self.check_keys(keys=['P_rad', 'avg_vp', 'geo_psi'], name='Integrated radiated power')
        if not chk:
            return result

        da = 0 * self['P_rad'].rename('P_rad_int')
        pr = self['P_rad'].values  # assumed in W/cm^3
        # volume integral copied from omfit_classes.fluxSurface
        da.values = integrate.cumtrapz(self['avg_vp'] * pr, self['geo_psi'], initial=0)
        da.attrs['long_name'] = r'$\int{dV P_{rad}}$'
        da.attrs['units'] = 'MW'

        result.update({'P_rad_int': da})

        if update:
            self.update(result)
        return result

    def KDG_neoclassical(self, mag_field=None, xfit='rho', update=True):
        """
        Poloidal velocity from Kim, Diamond Groebner, Phys. Fluids B (1991)
        with poloidal in-out correction based on Ashourvan (2017)
        :return: Places poloidal velocity for main-ion and impurity on outboard midplane into
        DERIVED.  Places neoclassical approximation for main-ion toroidal flow based on measured
        impurity flow in self.
        """

        # Default to only work for D, C as primary and impurity ion
        if 'n_12C6' not in self:
            printe('  Cannot run KDG without n_12C6')
            return
        if 'n_2H1' not in self:
            printe('Cannot run KDG without n_2H1')
            return

        if not mag_field:  # this is required as input in 8_postfit.py
            printe('WARNING!: Er calculation requires a mag_field input! See 8_postfit.py for format.')

        # OMFITprofiles convenience
        nx = len(self[xfit])
        ntimes = len(self['time'])

        ####
        # Geometric Quantities
        ####
        # Midplane major radius R
        R_midplane = self['R_midplane'].values
        # Major radius of magnetic axis
        R0 = R_midplane[:, 0]
        # Midplane minor radius r = R-R0
        r_midplane = R_midplane - R0[:, np.newaxis]
        # Local inverse aspect ratio eps = r/R0
        epsilon = r_midplane / R0[:, np.newaxis]
        # Circulating (Eq. C18) and trapped fractions
        fc_KDG = 1.0 - 1.46 * usqrt(epsilon) + 0.46 * epsilon * usqrt(epsilon)
        ft_KDG = 1.0 - fc_KDG
        # g function (Eq. C16)
        g_KDG = ft_KDG / fc_KDG

        ####
        # Magnetic field quantities
        ####
        mag_field = OMFITlib_general.mag_field_components(eq, make_plots=False)
        Bt_midplane = np.zeros((ntimes, nx), dtype=float)
        Bp_midplane = np.zeros((ntimes, nx), dtype=float)
        for i in range(ntimes):
            newr = self['R_midplane'].isel(time=i)
            newz = eq['Z_maxis'].isel(time=i).values * np.ones_like(newr)
            newrz = np.vstack((newr, newz)).T
            Bt_midplane[i, :] = RegularGridInterpolator(
                (mag_field['R_grid'][:, 0], mag_field['Z_grid'][0, :]), mag_field['Bt_arr'][:, :, i], bounds_error=False, fill_value=None
            )(newrz)
            Bp_midplane[i, :] = RegularGridInterpolator(
                (mag_field['R_grid'][:, 0], mag_field['Z_grid'][0, :]), mag_field['Bp_arr'][:, :, i], bounds_error=False, fill_value=None
            )(newrz)
        # Total magnetic field on midplane
        Btot_midplane = usqrt(Bt_midplane**2 + Bp_midplane**2)
        # Flux-surface averaged <B**2>
        B2_fsa = self['avg_Btot**2'].values

        ####
        # Species dependent quantities
        ####
        # Main ion mass and charge
        mi, Zi = OMFITlib_general.mZ('2H1')
        # Impurity mass and charge
        mI, ZI = OMFITlib_general.mZ('12C6')

        # Main ion density
        ni = self['n_2H1'].values
        # Impurity density
        nI = self['n_12C6'].values

        # Main ion temperature
        Ti = self['T_2H1'].values
        # Impurity density
        TI = self['T_12C6'].values

        # Main ion pressure
        Pi = self['p_2H1'].values
        # Impurity pressure
        PI = self['p_12C6'].values

        # Impurity strength parameter (after Eq. 9)
        alpha = (nI * ZI**2) / (ni * Zi**2)

        # Main ion thermal speed (m/s) sqrt(2T/m) (after Eq. 34)
        vti = usqrt(2.0 * Ti * constants.e / mi)
        # Impurity ion thermal speed
        vtI = usqrt(2.0 * TI * constants.e / mI)

        # Larmor radius (m)
        rhoi = (mi * vti) / (Zi * constants.e * Btot_midplane)
        rhoI = (mI * vtI) / (ZI * constants.e * Btot_midplane)
        # Poloidal Larmor radius (m)
        rhoip = (mi * vti) / (Zi * constants.e * Bp_midplane)

        # Scale-lengths (1/m) and carries minus sign for decreasing profile,
        # i.e. LTi is negative (after Eq. 34)
        dR = ugrad1(R_midplane)
        dTi = ugrad1(Ti)
        dPi = ugrad1(Pi)
        dPI = ugrad1(PI)
        # 1/LTi
        LTi_inv = (1.0 / Ti) * (dTi / dR)
        # 1/LPi
        LPi_inv = (1.0 / Pi) * (dPi / dR)
        # 1/LPI
        LPI_inv = (1.0 / PI) * (dPI / dR)

        # Viscocities
        # main ion (Eq. C15)
        mu_00_i = g_KDG * (alpha + np.sqrt(2.0) - np.log(1.0 + np.sqrt(2.0)))
        mu_01_i = g_KDG * ((3.0 / 2.0) * alpha + 4.0 / np.sqrt(2.0) - (5.0 / 2.0) * np.log(1.0 + np.sqrt(2.0)))
        mu_11_i = g_KDG * ((13.0 / 4.0) * alpha + (39.0 / 4.0) / np.sqrt(2.0) - (25.0 / 4.0) * np.log(1.0 + np.sqrt(2.0)))
        # impurity (Eq. C15)
        alpha_inv = 1.0 / alpha
        mu_00_I = g_KDG * (alpha_inv + np.sqrt(2.0) - np.log(1.0 + np.sqrt(2.0)))
        mu_01_I = g_KDG * ((3.0 / 2.0) * alpha_inv + 4.0 / np.sqrt(2.0) - (5.0 / 2.0) * np.log(1.0 + np.sqrt(2.0)))
        mu_11_I = g_KDG * ((13.0 / 4.0) * alpha_inv + (39.0 / 4.0) / np.sqrt(2.0) - (25.0 / 4.0) * np.log(1.0 + np.sqrt(2.0)))

        # Eq. 32
        beta = (27.0 / 4.0) ** 2 * (mi / mI) ** 2 * (15.0 / 2.0 + usqrt(2.0 * alpha) * (vti / vtI)) ** (-1.0)

        # Eq. 31
        bigD = mu_00_i * (mu_11_i + np.sqrt(2.0) + alpha - alpha * beta) - mu_01_i**2
        bigD[bigD == 0] *= np.nan  # can happen if midplane mag_field interpolation was out of bounds

        # Eq. 29
        K1 = (1.0 / bigD) * mu_01_i * (np.sqrt(2.0) + alpha - alpha * beta)
        # Eq. 30
        K2 = (1.0 / bigD) * (mu_00_i * mu_11_i - mu_01_i**2)

        ####
        # Poloidal velocities
        ####
        # Eq. 33
        V_pol_i = (1.0 / 2.0) * vti * rhoi * (K1 * LTi_inv) * Btot_midplane * Bt_midplane / B2_fsa

        # Eq. 34
        V_pol_I = (
            (1.0 / 2.0)
            * vti
            * rhoi
            * ((K1 + (3.0 / 2.0) * K2) * LTi_inv - LPi_inv + (Zi / ZI) * (TI / Ti) * LPI_inv)
            * Btot_midplane
            * Bt_midplane
            / B2_fsa
        )

        ####
        # Toroidal rotation
        ####
        # Eq. 40
        # Sign w.r.t. Ip comes through Bpol in rhoip.
        omega_I_minus_omega_i = (3.0 / 4.0) * K2 * (vti / R_midplane) * rhoip * LTi_inv

        # Assume outer midplane omega_tor_12C6 is a flux surface averaged quantity (even if not accurate especially at the edge)
        omega_I = self['omega_tor_12C6'].values

        # Calculate KDG 2H1 omega toroidal
        # By algebra omega_i = omega_I - (omega_I - omega_i)
        omega_i = omega_I - omega_I_minus_omega_i

        # Add to self
        V_pol_i_ds = xarray.Dataset()
        V_pol_i_da = 0.0 * self['n_2H1'].rename('V_pol_2H1_KDG')
        V_pol_i_da.values = V_pol_i
        V_pol_i_da.attrs['long_name'] = 'Kim-Diamond-Groebner 2H1 V_pol'
        V_pol_i_da.attrs['units'] = 'm/s'
        V_pol_i_ds.update({'V_pol_2H1_KDG': V_pol_i_da})

        if update:
            self.update(V_pol_i_ds)

        V_pol_I_ds = xarray.Dataset()
        V_pol_I_da = 0.0 * self['n_12C6'].rename('V_pol_12C6_KDG')
        V_pol_I_da.values = V_pol_I
        V_pol_I_da.attrs['long_name'] = 'Kim-Diamond-Groebner 12C6 V_pol'
        V_pol_I_da.attrs['units'] = 'm/s'
        V_pol_I_ds.update({'V_pol_12C6_KDG': V_pol_I_da})

        if update:
            self.update(V_pol_I_ds)

        omega_i_ds = xarray.Dataset()
        omega_i_da = 0.0 * self['omega_tor_12C6'].rename('omega_tor_2H1_KDG')
        omega_i_da.values = omega_i
        omega_i_da.attrs['long_name'] = 'Kim-Diamond-Groebner 2H1 omega_tor'
        omega_i_da.attrs['units'] = 'rad/s'
        omega_i_ds.update({'omega_tor_2H1_KDG': omega_i_da})

        if update:
            self.update(omega_i_ds)

        if 'V_pol_12C6' in self:
            # Measured omega_tor_12C6 is not a flux surface averaged quantity.
            # Calculate what the 12C6 flux surface averaged omega toroidal should be based on Eq (7) in Ashourvan 2017 (unpublished work)
            # This correction includes the poloidal in-out assymetry which is not negligible in the edge region
            avg_omega_I = (
                self['omega_tor_12C6'].values
                + R_midplane * Bt_midplane * self['V_pol_12C6'] * (self['avg_1/R**2'] - (1 / (R_midplane**2))) / Bp_midplane
            )
            print(' * Poloidal in-out assymtery correction applied')

            # Calculate KDG flux surface averaged 2H1 omega toroidal
            avg_omega_i = avg_omega_I - omega_I_minus_omega_i

            # Add to DERIVED
            avg_omega_I_ds = xarray.Dataset()
            avg_omega_I_da = 0.0 * self['omega_tor_12C6'].rename('omega_tor_avg_12C6')
            avg_omega_I_da.values = avg_omega_I
            avg_omega_I_da.attrs['long_name'] = 'Flux surface averaged 12C6 omega_tor'
            avg_omega_I_da.attrs['units'] = 'rad/s'
            avg_omega_I_ds.update({'omega_tor_avg_12C6': avg_omega_I_da})

            if update:
                self.update(avg_omega_I_ds)

            avg_omega_i_ds = xarray.Dataset()
            avg_omega_i_da = 0.0 * self['omega_tor_12C6'].rename('omega_tor_avg_2H1_KDG')
            avg_omega_i_da.values = avg_omega_i
            avg_omega_i_da.attrs['long_name'] = 'Kim-Diamond-Groebner flux surface averaged 2H1 omega_tor'
            avg_omega_i_da.attrs['units'] = 'rad/s'
            avg_omega_i_ds.update({'omega_tor_avg_2H1_KDG': avg_omega_i_da})

            if update:
                self.update(avg_omega_i_ds)

    def get_nclass_conductivity_and_bootstrap(self, gas='2H1', xfit='rho', device=None, eq=None, debug=False, update=True):
        """
        Call the neoclassical conductivity and bootstrap calculations from utils_fusion

        :return: Dataset. COntaining conductivity and bootstrap DataArrays

        """
        result = Dataset()

        if not eq:  # this is required as input in 8_postfit.py
            printe('WARNING!: Er calculation requires an input equilibrium!')

        # standard checks

        species, ions, ions_with_dens, ions_with_fast = get_species(self)

        needed_keys = ['q', 'geo_eps', 'avg_fc', 'geo_R', 'n_e', 'T_e', 'psi_n', f'T_{gas}', f'dT_{gas}_dpsi']
        needed_keys += [f'n_{s}' for s in ions_with_dens if 'fast' not in s]
        needed_keys += [f'dn_{s}_dpsi' for s in ions_with_dens if 'fast' not in s]
        chk = self.check_keys(needed_keys, name='Conductivity')

        if chk:
            nis = []
            dnis_dpsi = []
            Zis = []
            for species in ions_with_dens:
                if 'fast' not in species:
                    s2 = ["".join(x) for _, x in itertools.groupby(species, key=lambda x: str(x).isdigit())]
                    charge_state = int(s2[-1])
                    Zis.append(charge_state)
                    nis.append(self['n_' + species].values)
                    dnis_dpsi.append(self['dn_' + species + '_dpsi'].values)

            # note, we assume all the thermal ions have equilibrated
            dTi_dpsi = self[f'dT_{gas}_dpsi'].values
            Ti = self[f'T_{gas}'].values

            sigma_nc = utils_fusion.nclass_conductivity(
                psi_N=self['psi_n'].values,  # this is only needed if you turn the plot on
                ne=self['n_e'].values,  # ne in m^-3
                Te=self['T_e'].values,  # Te in eV
                Ti=Ti,  # Ti in eV
                nis=nis,  # density of ion species in m^-3
                Zis=Zis,  # charge states of ion species
                q=self['q'].values,  # safety factor
                eps=self['geo_eps'].values,  # inverse aspect ratio
                fT=1 - self['avg_fc'].values,  # trapped particle fraction
                R=self['geo_R'].values,  # major radius in m
                version='neo_2021',  #  should be the same with utils_fusion.sauter_bootstrap;
            )
            signc_da = DataArray(
                sigma_nc,
                coords=[('time', self['time'].values), (xfit, self[xfit].values)],
                name='nclass_sigma',
                attrs=dict(units='Ohm^-1 m^-1', long_name='Neoclassical conductivity from Sauter 1999'),
            )
            result.update({'nclass_sigma': signc_da})

        needed_keys += ['avg_F', 'psi', 'p_thermal', 'dn_e_dpsi', 'dT_e_dpsi']
        chk = self.check_keys(needed_keys, name='Bootstrap')

        if chk:
            jb_kwargs = dict(
                psi_N=self['psi_n'].values,  # this is only needed if you turn the plot on
                ne=self['n_e'].values,  # ne in m^-3
                Te=self['T_e'].values,  # Te in eV
                Ti=Ti,  # Ti in eV
                nis=nis,  # density of ion species in m^-3
                Zis=Zis,  # charge states of ion species
                I_psi=abs(self['avg_F'].values),
                psiraw=self['psi'].values,
                device=device,
                p=self['p_thermal'].values,  # pressure in Pa
                q=self['q'].values,  # safety factor
                eps=self['geo_eps'].values,  # inverse aspect ratio
                fT=1 - self['avg_fc'].values,  # trapped particle fraction
                R=self['geo_R'].values,  # major radius in m
                charge_number_to_use_in_ion_collisionality='Koh',
                charge_number_to_use_in_ion_lnLambda='Zavg',
                return_units=False,
                dT_e_dpsi=self['dT_e_dpsi'].values,  # derivative of Te
                dT_i_dpsi=dTi_dpsi,  # derivative of Ti
                dn_e_dpsi=self['dn_e_dpsi'].values,  # derivative of ne
                dnis_dpsi=dnis_dpsi,  # derivative of ion densities
            )

            # Published Sauter bootstrap with units
            # neo_2021 a new set of analytical coefficients from A.Redl, et al
            # jboot1   'Bootstrap from Sauter 1999'
            jboot = DataArray(
                utils_fusion.sauter_bootstrap(version='neo_2021', **jb_kwargs),  # A/m^2
                coords=[('time', self['time'].values), (xfit, self[xfit].values)],
                attrs={'units': 'A m^-2', 'long_name': 'Bootstrap from A.Redl, et al 2021'},
            )
            result.update({'jboot_sauter': jboot})

            # J parallel normalized with EFIT standards
            jboot_efit = utils_fusion.sauter_bootstrap(version='osborne', **jb_kwargs)  # A/m^2
            # EFIT sign convention. It should match the sign of itot, no matter what
            itot = eq['plasma_current'].values
            jboot_efit *= np.sign(np.nanmean(nominal_values(jboot_efit))) * np.sign(itot)[:, np.newaxis]
            # EFIT normalization
            R0 = utils_fusion.device_specs(device)['R0']
            if 'R0' is None:
                R0 = np.nanmean(eq['R_center'].values)  # (m)
            inv_r = self['avg_1/R'].values
            cross_sec = self['geo_cxArea'].sel(**{xfit: 1.0, 'method': 'nearest'}).values
            if debug:
                print(' >> Normalizing to EFIT convention using')
                print(f' >> R0 = {R0}')
                print(f" >> 1/R = {self['avg_1/R'].sel(**{xfit: 1.0, 'method': 'nearest'}).values}")
                print(f' >> Cross sectional area = {cross_sec}')
                print(f' >> Total current = {itot}')
            jboot_efit = utils_fusion.current_to_efit_form(R0, inv_r.T, cross_sec, itot, jboot_efit.T).T
            jboot_efit_da = DataArray(
                jboot_efit,
                coords=[('time', self['time'].values), (xfit, self[xfit].values)],
                attrs=dict(units='Unitless', long_name='Normalized Boostrap Current for EFIT'),
            )
            result.update({'jboot_efit': jboot_efit_da})

            if debug:
                # see the larger error bars when errors are propagated through finite difference derivatives
                db_kwargs = dict([(k, v) for k, v in jb_kwargs.items() if 'dpsi' not in k])
                jboot_efit = utils_fusion.sauter_bootstrap(version='osborne', **db_kwargs)  # A/m^2
                # EFIT sign convention. It should match the sign of itot, no matter what
                jboot_efit *= np.sign(np.nanmean(nominal_values(jboot_efit))) * np.sign(itot)[:, np.newaxis]
                # EFIT normalization
                jboot_efit = utils_fusion.current_to_efit_form(R0, inv_r.T, cross_sec, itot, jboot_efit.T).T
                jboot_efit = DataArray(
                    jboot_efit,
                    coords=[('time', self['time'].values), (xfit, self[xfit].values)],
                    attrs=dict(
                        units='Unitless', long_name='Normalized Boostrap Current for EFIT without propagating fit derivative error bars'
                    ),
                )
                result.update({'jboot_efit_nodpsi': jboot_efit})

        if update:
            self.update(result)
        return result

    def check_keys(self, keys=[], name='', print_error=True):
        """
        Check to make sure required data is available
        """
        missing = []
        for k in keys:
            if not k in self:
                missing.append(k)
        if missing:
            if not name:
                name = 'value'
            if print_error:
                printw('  WARNING: Could not form {:}. Missing {:}'.format(name, ', '.join(['`%s`' % x for x in missing])))
            return False
        return True

    @dynaLoad
    def reset_coords(self, names=None, drop=False):
        """
        Pass through implementation of Dataset.reset_coords(). Given names of coordinates, convert them to variables.
        Unlike Dataset.reset_corrds(), however, this function modifies in place!

        param names: Names of coords to reset. Cannot be index coords. Default to all non-index coords.

        param drop: If True, drop coords instead of converting. Default False.
        """
        self._dataset = self._dataset.reset_coords(names=names, drop=drop)

        return self

    def combine(self, other, combine_attrs='drop_conflicts'):
        """
        Pass through implementation of xarray.combine_by_coords. Given another OMFITprofile, it seeks to combine the
        none conflicting data in the two objects.

        param other: Another instance of OMFITprofiles.

        param combine_attr: Keyword controlled behavior regarding conflicting attrs (as opposed to vars). Default to
            'drop_conflicts' where conflicting attrs are dropped from the result. (see xarray.combine_by_coords)
        """

        from xarray import combine_by_coords

        self.load()
        other.load()
        self._dataset = combine_by_coords([self._dataset, other._dataset], combine_attrs=combine_attrs)

        return self


class OMFITprofilesDynamic(OMFITncDynamicDataset):
    """
    Class for dynamic calculation of derived quantities

    :Examples:

    Initialize the class with a filename and FIT Dataset.
    >> tmp=OMFITprofiles('test.nc', fits=root['OUTPUTS']['FIT'], equilibrium=root['OUTPUTS']['SLICE']['EQ'], root['SETTINGS']['EXPERIMENT']['gas'])

    Accessing a quantity will dynamically calculate it.
    >> print tmp['Zeff']

    Quantities are then stored (they are not calculated twice).
    >> tmp=OMFITprofiles('test.nc',
                          fits=root['OUTPUTS']['FIT'],
                          equilibrium=root['OUTPUTS']['SLICE']['EQ'],
                          main_ion='2H1')
    >> uband(tmp['rho'],tmp['n_2H1'])
    """

    def __init__(self, filename, fits=None, equilibrium=None, main_ion='2H1', **kw):
        OMFITncDataset.__init__(self, filename, **kw)

        if fits:
            self.update(fits)

            # profile fit dimension
            dims = list(self.dims.keys())
            xkey = dims[dims.index('time') - 1]

            # collect some meta data about which particle species have what info available
            self.attrs['main_ion'] = str(main_ion)
            species, ions, ions_with_dens, ions_with_fast = get_species(self)
            self['species'] = DataArray(species, dims=['species'])
            ions += [self.attrs['main_ion']]
            self['ions'] = DataArray(ions, dims=['ions'])
            ions_with_dens += [self.attrs['main_ion']]
            self['ions_with_dens'] = DataArray(ions_with_dens, dims=['ions_with_dens'])
            ions_with_rot = [key.replace('omega_tor_', '') for key in self if key.startswith('omega_tor') and key != 'omega_tor_e']
            self['ions_with_rot'] = DataArray(ions_with_rot, dims=['ions_with_rot'])

            # interpolate other radial coordinates from equilibrium
            printd('- Interpolating equilibrium quantities')
            needed = {
                'avg_R',
                'avg_R**2',
                'avg_1/R',
                'avg_1/R**2',
                'avg_Btot',
                'avg_Btot**2',
                'avg_vp',
                'avg_q',
                'avg_fc',
                'avg_F',
                'avg_P',
                'geo_psi',
                'geo_R',
                'geo_Z',
                'geo_a',
                'geo_eps',
                'geo_vol',
            }
            eqcoords = needed.intersection(list(equilibrium.keys()))
            for meas in eqcoords:
                if 'profile_' + xkey != meas and 'profile_psi_n' in equilibrium[meas]:
                    yy = []
                    for t in self['time'].values:
                        eq_t = equilibrium.sel(time=t, method='nearest')
                        x = np.squeeze(eq_t['profile_' + xkey])
                        y = np.squeeze(nominal_values(eq_t[meas].values))
                        yy.append(interp1e(x, y)(self[xkey].values))

                        # Ensure that 'q' is not extrapolated outside the separatrix
                        if meas == 'profile_q':
                            mask = self[xkey].values > 1.0
                            yy[-1][mask] = np.nan
                    yy = np.array(yy)
                    key = meas.replace('profile_', '')
                    self[key] = DataArray(
                        yy, coords=[fits['time'], fits[xkey]], dims=['time', xkey], attrs=copy.deepcopy(equilibrium[meas].attrs)
                    )
            self.set_coords(eqcoords)
            # reassign global attrs clobbered when assigning eq DataArrays with attrs
            self.attrs['main_ion'] = str(main_ion)
            self.save()

        self.update_dynamic_keys(self.__class__)

    def __getitem__(self, key):
        # map specific quantities to class functions
        mapper = {}
        mapper['n_' + self.attrs['main_ion']] = 'calc_n_main_ion'
        mapper['T_' + self.attrs['main_ion']] = 'calc_T_main_ion'

        # resolve mappings
        if key not in self:
            if key in mapper:
                getattr(self, mapper[key])()
                if mapper[key] in self._dynamic_keys:
                    self._dynamic_keys.pop(self._dynamic_keys.index(mapper[key]))

        # return value
        return OMFITncDynamicDataset.__getitem__(self, key)

    def calc_n_main_ion(self):
        """
        Density of the main ion species.
        Assumes quasi-neutrality.

        :return: None. Updates the instance's Dataset in place.

        """
        main_ion = str(self.attrs['main_ion'])
        mg, zg = mZ(main_ion)
        nz = self['n_e']
        for key in self['ions_with_dens'].values:
            if key != main_ion:
                nz -= self['n_' + key].values * mZ(key)[1]
        self['n_' + main_ion] = nz / zg
        invalid = np.where(self['n_' + main_ion].values <= 0)[0]
        if len(invalid) > 0:
            printe('  Had to force main ion density to be always positive!')
            printe('  This will likely present a problem when running transport codes!')
            valid = np.where(self['n_' + main_ion].values > 0)[0]
            self['n_' + main_ion].values[invalid] = np.nanmin(self['n_' + main_ion].values[valid])

    def calc_T_main_ion(self):
        """
        Temperature of the main ion species.
        Assumes it is equal to the measured ion species temperature.
        If there are multiple impurity temperatures measured, it uses the first one.

        :return: None. Updates the instance's Dataset in place.

        """
        main_ion = str(self.attrs['main_ion'])
        impurities_with_temp = [k for k in self['ions'].values if k != 'b' and 'T_' + k in list(self.keys())]
        nwith = len(impurities_with_temp)
        if nwith == 0:
            raise OMFITexception("No main or impurity ion temperatures measured")
        if nwith > 1:
            printw(
                "WARNING: Multiple impurities temperatures measured, setting main ion temperature based on {:}".format(
                    impurities_with_temp[0]
                )
            )
        for ion in impurities_with_temp:
            self['T_' + main_ion] = self[f'T_{ion}'] * 1
            break

    def calc_Zeff(self):
        r"""
        Effective charge of plasma.

        Formula: Z_{eff} = \sum{n_s Z_s^2} / \sum{n_s Z_s}

        :return: None. Updates the instance's Dataset in place.

        """
        # calculate Zeff (not assuming quasi-neutrality)
        nz_sum = np.sum([self['n_' + i].values * mZ(i)[1] for i in self['ions_with_dens'].values], axis=0)
        nz2_sum = np.sum([self['n_' + i].values * mZ(i)[1] ** 2 for i in self['ions_with_dens'].values], axis=0)
        z_eff = nz2_sum / nz_sum + 0 * self['n_e'].rename('Zeff')
        z_eff.attrs['long_name'] = r'$Z_{eff}$'
        self['Zeff'] = z_eff

    def calc_Total_Zeff(self):
        r"""
        Effective charge of plasma.

        Formula: Z_{eff} = \sum{n_s Z_s^2} / \sum{n_s Z_s}

        :return: None. Updates the instance's Dataset in place.

        """
        main_ion = str(self.attrs['main_ion'])
        mg, zg = mZ(main_ion)
        nz = self['n_e']
        for key in self['ions_with_dens'].values:
            if key != main_ion:
                nz -= self['n_' + key].values * mZ(key)[1]
        self['n_' + main_ion] = nz / zg
        invalid = np.where(self['n_' + main_ion].values <= 0)[0]
        if len(invalid) > 0:
            printe('  Had to force main ion density to be always positive!')
            printe('  This will likely present a problem when running transport codes!')
            valid = np.where(self['n_' + main_ion].values > 0)[0]
            self['n_' + main_ion].values[invalid] = np.nanmin(self['n_' + main_ion].values[valid])


if __name__ == '__main__':

    # ensure that all specified model_tree_quantities can be translated to have <=12 chars
    for s in model_tree_species:
        for q in model_tree_quantities:
            item0 = q.format(species=s)
            item = OMFITprofiles.mds_translator(None, item0)

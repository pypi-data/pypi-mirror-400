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
from omfit_classes.omfit_eqdsk import OMFITgeqdsk, from_mds_plus
from omfit_classes.omfit_data import OMFITncDataset, OMFITncDynamicDataset, importDataset
from omas import ODS, omas_environment, cocos_transform, define_cocos
from omfit_classes.omfit_omas_utils import add_generic_OMFIT_info_to_ods
from omfit_classes.omfit_rdb import OMFITrdb
from omfit_classes.omfit_mds import OMFITmdsValue
from omfit_classes.omfit_profiles import OMFITprofiles

import inspect
import numpy as np
from uncertainties import unumpy, ufloat
from uncertainties.unumpy import std_devs, nominal_values
from scipy import constants

np.seterr(invalid='ignore', divide='ignore')


__all__ = ['available_iri_results', 'load_iri_results']


def available_iri_results(device='DIII-D', shot=-1, run_by=None, tag=None, settings=None, ignore_ignore=False):
    r"""
    Search for avaliable IRI runs by device and shot number. Optionally, also search with run_by and tag values.
    If multiple search criteria is given, then the search only returns records
    that satisfies all criteria. This function returns a dictionary containing
    all matching data that are

    :param device: string
        Name of device for which the analysis was done. Currently only DIII-D is supported.

    :param shot: int
        The shot number to search for.

    :param run_by: string [optional]
        The run_by username to search for in IRI records. Production runs are run by the user `d3dsf` which is the default

    :param tag: string [optional].
        The tag to search for in IRI records. There are currently three main tags: 'CAKE01' (no MSE), 'CAKE02'
        (with MSE) and 'CAKE_FDP'. 'CAKE01' and 'CAKE02' have 50 ms time resolution and 129x129 equilibria. 'CAKE_FDP'
        has 20 ms time resolution and 257x257 equilibria.

    :param settings: string [optional]
        The seetings string to search for in IRI records. For example '1FWDyrS` is defalut for knot optimized MSE
        constrained equilibria. See documentation for `code` in between_shot_autorun() in the CAKE module for full
        details.

    :param ignore_ignore: bool [optional]
        If this flag is set, then the 'ignore' field in the IRI metadata tables
        will be ignored. Thus this function will then return records that have
        been marked 'ignore'. Defaults to False.
    """

    if ignore_ignore:
        printw(
            """WARNING: You are ignoring the ignore flag. This will potentailly return results that are wrong,
            unphysical, or invalid! Use with EXTREAM CAUTION!"""
        )

    rdb = OMFITrdb(db='code_rundb', server='d3drdb')  # This where the iri metadata tables lives for now.
    select_string = f"SELECT * FROM iri_run_log WHERE experiment='{device}' AND shot={shot}"
    if shot != -1:
        select_string = select_string + f" AND shot={shot}"
    if run_by is not None:
        select_string = select_string + f" AND run_by='{run_by}'"
    if tag is not None:
        select_string = select_string + f" AND tag='{tag}'"
    if not ignore_ignore:
        select_string = select_string + f" AND ignore='False'"

    runs = rdb.select(select_string)
    n_runs = len(runs)
    if n_runs < 1:
        printw(f"No IRI runs found for {device} shot# {shot} run_by {run_by} with tag={tag}, settings={settings}.")
        return {}
    else:
        # we need to sort out the results in something easier to read and deal with.
        runs_dict = {}
        for ii in runs:
            run_dict = runs[ii]
            runid = run_dict['IRI_ID']
            run_dict[
                'description'
            ] = f"IRI_ID={runid} by {run_dict['RUN_BY']} with tag: {run_dict['TAG']} and comment: {run_dict['COMMENTS']}"

            # search for result uploads
            run_dict['results_uploaded'] = {}
            uploads = rdb.select(f"SELECT * FROM iri_upload_log WHERE iri_id={runid}")
            for jj in uploads:
                upload = uploads[jj]
                code = upload.pop('CODE_NAME', 'unknown code')
                run_dict['results_uploaded'][code] = upload

            runs_dict[runid] = run_dict

    return runs_dict


def load_iri_results(runs_dict):
    r"""
    Loads IRI results as described in a runs dictionary, and outputs to a OMFITtree()
    ex. OMFIT['iri_data'] = load_iri_results(runs_dict).

    :param runs_dict: dictionary
        Dictionary of metadata describing uploaded IRI data. It should come from
        the avaliable_iri_data() function. But editing and deleting of records
        is allowed as long as the hierarchy is preserved.
    """
    destination_tree = OMFITtree()
    for iri_id in runs_dict:
        destination_tree[iri_id] = OMFITtree()
        for code_upload in runs_dict[iri_id]['results_uploaded']:
            upload = runs_dict[iri_id]['results_uploaded'][code_upload]
            destination_tree[iri_id][code_upload] = load_by_code(
                code_upload, upload['UPLOAD_SERVER'], upload['UPLOAD_ID'], tree=upload['UPLOAD_TREE']
            )
    return destination_tree


def load_by_code(code, server, upload_id, tree=None):
    r"""
    Actual loading interface. It wraps underlying loading functions for various IRI related codes, and calls the
    appropriate one depending on which is needed. Returns OMFITtree() containing loaded results.

    :param runs_dict: 'string'
        The name of the code as recorded to the metadata. Currently supports 'OMFIT_CAKE_EFIT', and 'OMFIT_CAKE_PROF').

    :param server: 'string'
        The name of the sever where the data is stored. It should come from the metadata tables/record.

    :param upload_id: int
        The upload_id to load. Should come from the metadata record.
    """
    if code == 'OMFIT_CAKE_EFIT':
        eq_tree = OMFITtree()
        if tree is None:
            printd(f"No tree argument provided to load_by_code() for code = OMFIT_CAKE_EFIT. Tree assumed to be EFIT.")
            tree = 'EFIT'
        # from equilibriums, we need to find out the times that were uploaded.
        eq_times = get_EFIT_times_from_mds(server, tree, upload_id)
        eq_tree = from_mds_plus(device=server, shot=upload_id, times=eq_times, exact=True, snap_file=tree, get_afile=True, get_mfile=True)
        return eq_tree

    elif code == 'OMFIT_CAKE_PROF':
        prof = OMFITprofiles('')
        prof.from_mds(server, upload_id)
        return prof
    else:
        printw(f"OMFIT_IRI does not understand the code designation {code}. Results from that code is not loaded.")
        return OMFITtree()


def get_EFIT_times_from_mds(server, tree, upload_id):
    times_mds = OMFITmdsValue(server=server, treename=tree, shot=upload_id, TDI=f"dim_of(\{tree}::TOP.RESULTS.GEQDSK.CPASMA)")
    times = times_mds.data()
    return times

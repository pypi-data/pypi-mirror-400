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

import os
from omfit_classes.omfit_json import OMFITjson


class _OMFITclusters(OMFITjson):
    """
    This class finds the optimal batch submission configuration for a given system.
    Designed to work in conjunction with OMFITx.job_array.

    Reads in the configuration through the `omfit_clusters.json` file.
    Some notes on the json file:
    - `partitions_decision` and `qos_decision` describe the qualities of `partitions` and `qos`.
      The array of length 4 contains:
        - Minimum time for a queue: Used to indicate that another queue with a shorter maximum wall time exists.
                                    This allows the queue with the shortest maximum wall time that can fit the job
                                    is used.
        - Maximum time for a queue: Upper limit on wall time for queue.

        - Maximum number of concurrent cores: Makes sure that the queue can provide the resources requested by the job.

        - Total virtual memory provided by a single node: Used to calculate the amount of memory per core for the job.

    """

    def __init__(self):
        OMFITjson.__init__(self, OMFITsrc + os.sep + 'omfit_classes' + os.sep + 'omfit_clusters.json')

    def get_cluster_config(self, cluster):
        """
        Returns configuration of selected cluster.

        :param cluster: Name of the target cluster

        :return: Dictionary of cluster meta information.
        """
        try:
            cluster_config = self[cluster]
        except KeyError:
            raise NotImplementedError(
                f"""
                    The cluster {cluster} is not yet implemented.\n
                    Please consider adding its configuration to omfit_clusters.json
                    """
            )
        return cluster_config

    def get_cpus_per_node(self, cluster, constraint=None):
        """
        Returns maximum allowed concurrent cpu cores.
        Allows assignment to multiple nodes.

        :param cluster: Name of the target cluster

        :param wall_time: Wall time in hours

        :return: Maximum allowed concurrent cpu cores

        """
        cluster_config = self.get_cluster_config(cluster)
        if constraint is None:
            return cluster_config["cpus_per_node"]
        else:
            try:
                contraint_index = cluster_config["constraints"].index(constraint)
                return cluster_config["cpus_per_node"][contraint_index]
            except ValueError:
                raise NotImplementedError(
                    f"""
                    The cluster {self.cluster} does not have the contraint
                    {constraint} you requested implemented.
                    Please consider adding this constraint to omfit_clusters.json
                    """
                )

    def get_max_distriubted_cores_from_wall_time(self, cluster, wall_time):
        """
        Returns maximum allowed concurrent cpu cores.
        Allows assignment to multiple nodes.

        :param cluster: Name of the target cluster

        :param wall_time: Wall time in hours

        :return: Maximum allowed concurrent cpu cores

        """
        cluster_config = self.get_cluster_config(cluster)
        max_distributed_cores = 0
        for iqueue, queue_select in enumerate(["partitions", "qos"]):
            if cluster_config[queue_select] is not None:
                for queue, decision in zip(cluster_config[queue_select], cluster_config[queue_select + "_decision"]):
                    if wall_time > decision['t_min'] and wall_time <= decision['t_max'] and decision['max_cpus'] > max_distributed_cores:
                        max_distributed_cores = decision['max_cpus']
        return max_distributed_cores

    def get_batch_simple(
        self,
        cluster,
        wall_time,
        cpus_per_task,
        ntasks=1,
        mem_per_cpu=None,
        mem_per_task=None,
        partition=None,
        qos=None,
        constraint=None,
        vmem_per_node=None,
    ):
        """
        Generates the Slurm commands needed for OMFITx.job_array

        :param cluster: Name of the cluster (lowercase)

        :param wall_time: Wall time as a floating point number in hours

        :param ntasks: Number of MPI tasks every job in the job array uses

        :param cpus_per_task: Number of cpus allocated for each MPI task

        :param mem_per_cpu: Memory requirements of task [GB]

        :param mem_per_task: Memory requirements of task [GB]

        :param partition: Force the use of a certain partition. The routine will look up the most suitable partition otherwise.

        :param qos: Force the use of a certain quality-of-service. The routine will look up the most suitable qos otherwise.

        :param constraint: Additional constraint for Slurm. Used for example by NERSC.

        :param vmem_per_node: When specifying quality of service/partition manually you also need to provide the amount of vmem a node has [GB].

        :return: Returns dictionary that can be passed on to OMFITx.job_array via the ** operator
        """
        cluster_config = self.get_cluster_config(cluster)
        for mandatory_arg in cluster_config["mandatory_arguments_for_sbatch_simple"]:
            if locals()[mandatory_arg] is None:
                raise ValueError(f"For {cluster} {mandatory_arg} is a mandatory argument!")

        omfit_job_array_config = {}
        omfit_job_array_config["partition"] = ""
        queue_select_success = [False, False]
        cpu_count = ntasks * cpus_per_task
        query = []

        if partition is None:
            query.append("partitions")
        else:
            if "--partition=" not in partition:
                raise ValueError("Please provide the partition keyword in the form --partition==<your partition>")
            omfit_job_array_config["partition"] += partition

        if qos is None:
            query.append("qos")
        else:
            if "--qos=" not in qos:
                raise ValueError("Please provide the qos keyword in the form --qos=<your qos>")
            if not omfit_job_array_config["partition"].endswith(" ") and len(omfit_job_array_config["partition"]) > 0:
                omfit_job_array_config["partition"] += " "
            omfit_job_array_config["partition"] += qos

        for iqueue, queue_select in enumerate(query):
            if cluster_config[queue_select] is not None:
                # Note that omfit.job_array only takes "partition" as an argument and not qos
                if not omfit_job_array_config["partition"].endswith(" ") and len(omfit_job_array_config["partition"]) > 0:
                    omfit_job_array_config["partition"] += " "

                for queue_meta, decision in zip(cluster_config[queue_select], cluster_config[queue_select + "_decision"]):
                    if wall_time > decision['t_min'] and wall_time <= decision['t_max'] and decision['max_cpus'] >= cpu_count:
                        omfit_job_array_config["partition"] += queue_meta
                        queue_select_success[iqueue] = True
                        if vmem_per_node is None or decision['vmem_per_node'] < vmem_per_node:
                            vmem_per_node = decision['vmem_per_node']
                        break
            else:
                queue_select_success[iqueue] = True

        if vmem_per_node == -1:
            raise ValueError(
                f"""
                    Could not automatically detect memory per node. You might need to add
                    extra configuration data for the cluster/partition/qos you requested.
                    Requested cluster/partition/qos: {cluster} {partition} {qos}
                """
            )

        omfit_job_array_config["partition_flag"] = ""
        if constraint is None and cluster_config["constraints"] is not None:
            # Use primary constraint as default
            omfit_job_array_config["partition"] += " " + cluster_config["constraints"][0]
            constraint = cluster_config["constraints"][0]
        elif constraint is not None:
            omfit_job_array_config["partition"] += " " + constraint

        omfit_job_array_config["ntasks"] = ntasks
        omfit_job_array_config["nproc_per_task"] = cpus_per_task

        hours = int(wall_time)
        minutes = int(wall_time * 60 - hours * 60)
        seconds = int(wall_time * 3600 - hours * 3600 - minutes * 60)
        omfit_job_array_config["job_time"] = "{0:d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
        omfit_job_array_config["batch_type"] = cluster_config["batch_type"]

        n_max_cpus = self.get_cpus_per_node(cluster, constraint)
        # Since omfitx.job_array do not specify
        # the number of nodes explicitly, we will be sharing nodes.
        # Therefore, the memory should be limited to the amount of memory per cpu on the system

        if mem_per_task is None and mem_per_cpu is None:
            omfit_job_array_config["memory"] = f"{int(vmem_per_node / n_max_cpus * 0.9 * 1024)}M"
        else:
            if mem_per_task is not None:
                mem_per_node = mem_per_task * ntasks
                omfit_job_array_config["memory"] = f"{int(mem_per_task / cpus_per_task * 1024)}M"
            else:  # mem_per_cpu is not None
                mem_per_node = mem_per_cpu * cpus_per_task * ntasks
                omfit_job_array_config["memory"] = f"{int(mem_per_cpu * 1024)}M"

            if vmem_per_node < mem_per_node:
                raise ValueError(
                    f"Insufficient memory for {omfit_job_array_config['partition']}: Available: {vmem_per_node} Requested: {mem_per_node}"
                )

        return omfit_job_array_config


OMFITclusters = _OMFITclusters()
OMFITclusters.load()

__all__ = ["OMFITclusters"]
if __name__ == "__main__":
    OMFITclusters.get_batch_simple("perlmutter", 2.0, 1, 1, constraint="--constraint=cpu")

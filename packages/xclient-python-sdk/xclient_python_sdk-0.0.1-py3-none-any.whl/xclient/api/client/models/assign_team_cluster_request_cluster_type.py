from enum import Enum


class AssignTeamClusterRequestClusterType(str, Enum):
    K8S = "k8s"
    SLURM = "slurm"

    def __str__(self) -> str:
        return str(self.value)

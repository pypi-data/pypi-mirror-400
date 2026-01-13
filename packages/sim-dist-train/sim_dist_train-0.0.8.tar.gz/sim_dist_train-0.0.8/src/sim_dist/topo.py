import torch
import math
from typing import List
from enum import Enum


class Topology(str, Enum):
    COMPLETE = "complete"
    ONE_PEER_RING = "ring"
    ONE_PEER_EXPONENTIAL = "exp"


def get_mixing_matrices(
    topo: Topology, world_size: int, local_world_size: int
) -> List[torch.Tensor]:
    match topo:
        case Topology.COMPLETE:
            mix_matrices = [
                torch.ones((world_size, world_size), device="cuda") / world_size
            ]
        case Topology.ONE_PEER_RING:
            mix_matrices = [
                torch.zeros((world_size, world_size), device="cuda") for _ in range(2)
            ]
            for i in range(world_size):
                mix_matrices[0][i, i] = 0.5
                mix_matrices[1][i, i] = 0.5
                if i % 2 == 0:
                    mix_matrices[0][i, (i - 1 + world_size) % world_size] = 0.5
                    mix_matrices[1][i, (i + 1) % world_size] = 0.5
                else:
                    mix_matrices[0][i, (i + 1) % world_size] = 0.5
                    mix_matrices[1][i, (i - 1 + world_size) % world_size] = 0.5
        case Topology.ONE_PEER_EXPONENTIAL:
            rounds = round(math.log2(world_size))
            mix_matrices = [
                torch.zeros((world_size, world_size), device="cuda")
                for _ in range(rounds)
            ]
            for r in range(rounds):
                used = set()
                for i in range(world_size):
                    mix_matrices[r][i, i] = 0.5
                    if (i + round(2**r) < world_size) and (i not in used):
                        mix_matrices[r][i, i + round(2**r)] = 0.5
                        mix_matrices[r][i + round(2**r), i] = 0.5
                        used.add(i)
                        used.add(i + round(2**r))
        case _:
            raise ValueError(f"Invalid topology: {topo}")
    return mix_matrices

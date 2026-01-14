from typing import Any, List, Optional


class ObsNode:
    def __init__(self, obs: Any):
        self.obs = obs
        self.children: List["ObsNode"] = []
        self.parent: Optional["ObsNode"] = None

    def __repr__(self):
        return f"ObsNode(id={self.obs.id}, type={self.obs.type}, name={self.obs.name})"


def dfs_(observation_tree: List[ObsNode]) -> List[ObsNode]:
    ret = []
    for node in observation_tree:
        ret.append(node)
        ret.extend(dfs_(node.children))
    return ret

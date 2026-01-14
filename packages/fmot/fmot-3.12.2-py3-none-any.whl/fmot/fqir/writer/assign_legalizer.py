import logging
from fmot.fqir import GraphProto, NodeProto, TensorProto

logger = logging.getLogger(__name__)


class IllegalAssignError(Exception):
    ...


def legalize_assigns(graph: GraphProto):
    """Update graph in-place to legalize assign nodes for compilation.

    Arguments:
        graph (GraphProto): FQIR graph
    """
    # keeps track of {node: new_value} for each assign node in the graph
    assign_update_map: dict[TensorProto, TensorProto] = {}

    for node in graph.nodes:
        if node.subgraph is not None:
            legalize_assigns(node.subgraph)

        if node.opname == "assign":
            tgt = node.inputs["y"]
            src = node.inputs["x"]

            if tgt in assign_update_map:
                raise IllegalAssignError(
                    f"Tensor {tgt} has multiple assign nodes targeting it. Cannot have > 1."
                )
            assign_update_map[tgt] = src

        else:
            for key, x_orig in node.inputs.items():
                if x_orig in assign_update_map:
                    logger.debug(
                        f"assign buffer is being used in a node after update. Before: \n{node}"
                    )
                    node.inputs[key] = assign_update_map[x_orig]
                    logger.debug(
                        f"Updating to use a different referece. After:\n{node}"
                    )

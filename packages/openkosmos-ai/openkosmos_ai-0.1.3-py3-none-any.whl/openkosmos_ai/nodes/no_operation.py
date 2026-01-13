from openkosmos_ai.nodes.base_node import BaseFlowNode


class NoOperationNode(BaseFlowNode):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass

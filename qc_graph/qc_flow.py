# from typing import TypedDict, Dict, Any
# from langgraph.graph import StateGraph, END
# from agents.test_coverage_agent import TestCoverageAgent
# from agents.completeness_agent import CompletenessAgent
# from agents.consistency_agent import ConsistencyAgent
# from agents.clarity_agent import ClarityAgent
# from agents.implementation_agent import ImplementationReadinessAgent
# from agents.correction_agent import CorrectionAgent


# # Define the shared state type
# class QCState(TypedDict):
#     description: str
#     results: Dict[str, Any]
#     tmp_path: str  # ✅ Added



# class QCGraph:
#     def __init__(self):
#         self.completeness = CompletenessAgent()
#         self.consistency = ConsistencyAgent()
#         self.clarity = ClarityAgent()
#         self.readiness = ImplementationReadinessAgent()
#         self.correction = CorrectionAgent()
#         self.test_coverage = TestCoverageAgent()
#         self.graph = self._build_graph()

#     def _build_graph(self):
#         graph = StateGraph(QCState)

#         # Define all node functions
#         def run_completeness(state: QCState) -> QCState:
#             result = self.completeness.analyze(state["description"])
#             state["results"]["completeness"] = result
#             return state

#         def run_consistency(state: QCState) -> QCState:
#             result = self.consistency.analyze(state["description"], state["results"])
#             state["results"]["consistency"] = result
#             return state

#         def run_clarity(state: QCState) -> QCState:
#             result = self.clarity.analyze(state["description"], state["results"])
#             state["results"]["clarity"] = result
#             return state
        
#         def run_test_coverage(state: QCState) -> QCState:
#             result = self.test_coverage.analyze(state["description"], state["tmp_path"], state["results"])
#             state["results"]["test_coverage"] = result
#             return state

#         def run_implementation(state: QCState) -> QCState:
#             result = self.readiness.analyze(state["description"], state["results"])
#             state["results"]["implementation_readiness"] = result
#             return state
        
#         def run_correction(state: QCState) -> QCState:
#             result = self.correction.correct(state["description"], state["results"])
#             state["results"]["corrections"] = result
#             return state

#         # Register nodes
#         graph.add_node("CompletenessAgent", run_completeness)
#         graph.add_node("ConsistencyAgent", run_consistency)
#         graph.add_node("ClarityAgent", run_clarity)
#         graph.add_node("TestCoverageAgent", run_test_coverage)  # ✅ Added here
#         graph.add_node("ImplementationAgent", run_implementation)
#         graph.add_node("CorrectionAgent", run_correction)

#         # Add edges (connections)
#         graph.add_edge("CompletenessAgent", "ConsistencyAgent")
#         graph.add_edge("ConsistencyAgent", "ClarityAgent")
#         graph.add_edge("ClarityAgent", "TestCoverageAgent")  # ✅ Flow continues here
#         graph.add_edge("TestCoverageAgent", "ImplementationAgent")
#         graph.add_edge("ImplementationAgent", "CorrectionAgent")
#         graph.add_edge("CorrectionAgent", END)

#         # Define entry point
#         graph.set_entry_point("CompletenessAgent")

#         return graph.compile()

#     def execute(self, description: str, tmp_path: str) -> Dict[str, Any]:
#         state: QCState = {"description": description, "results": {}, "tmp_path": tmp_path}
#         final_state = self.graph.invoke(state)
#         return final_state["results"]


from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, START, END
from agents.test_coverage_agent import TestCoverageAgent
from agents.completeness_agent import CompletenessAgent
from agents.consistency_agent import ConsistencyAgent
from agents.clarity_agent import ClarityAgent
from agents.implementation_agent import ImplementationReadinessAgent
from agents.correction_agent import CorrectionAgent


# Shared state structure
class QCState(TypedDict):
    description: str
    results: Dict[str, Any]
    tmp_path: str


class QCGraph:
    def __init__(self):
        # Initialize agents
        self.completeness = CompletenessAgent()
        self.test_coverage = TestCoverageAgent()
        self.consistency = ConsistencyAgent()
        self.clarity = ClarityAgent()
        self.readiness = ImplementationReadinessAgent()
        self.correction = CorrectionAgent()

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(QCState)

        # Define node functions
        def run_completeness(state: QCState) -> QCState:
            result = self.completeness.analyze(state["description"])
            state["results"]["completeness"] = result
            return state

        def run_test_coverage(state: QCState) -> QCState:
            result = self.test_coverage.analyze(
                state["description"],
                state["tmp_path"],
                state["results"]
            )
            state["results"]["test_coverage"] = result
            return state

        def run_consistency(state: QCState) -> QCState:
            result = self.consistency.analyze(state["description"], state["results"])
            state["results"]["consistency"] = result
            return state

        def run_clarity(state: QCState) -> QCState:
            result = self.clarity.analyze(state["description"], state["results"])
            state["results"]["clarity"] = result
            return state

        def run_implementation(state: QCState) -> QCState:
            result = self.readiness.analyze(state["description"], state["results"])
            state["results"]["implementation_readiness"] = result
            return state

        def run_correction(state: QCState) -> QCState:
            result = self.correction.correct(state["description"], state["results"])
            state["results"]["corrections"] = result
            return state

        # Register all nodes
        graph.add_node("CompletenessAgent", run_completeness)
        graph.add_node("TestCoverageAgent", run_test_coverage)
        graph.add_node("ConsistencyAgent", run_consistency)
        graph.add_node("ClarityAgent", run_clarity)
        graph.add_node("ImplementationAgent", run_implementation)
        graph.add_node("CorrectionAgent", run_correction)

        # ✅ Parallel start: Completeness + TestCoverage both run first
        graph.add_edge(START, "CompletenessAgent")
        # graph.add_edge(START, "TestCoverageAgent")

        # ✅ Their results are merged and passed to ConsistencyAgent
        graph.add_edge("CompletenessAgent", "TestCoverageAgent")
        graph.add_edge("TestCoverageAgent", "ConsistencyAgent")

        # ✅ Then continue sequentially
        graph.add_edge("ConsistencyAgent", "ClarityAgent")
        graph.add_edge("ClarityAgent", "ImplementationAgent")
        graph.add_edge("ImplementationAgent", "CorrectionAgent")
        graph.add_edge("CorrectionAgent", END)

        return graph.compile()

    def execute(self, description: str, tmp_path: str) -> Dict[str, Any]:
        state: QCState = {"description": description, "results": {}, "tmp_path": tmp_path}
        final_state = self.graph.invoke(state)
        return final_state["results"]

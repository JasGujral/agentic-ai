"""Orchestration: the loop that wires the components and enforces termination."""
from src.reasoning.decision import Final, Clarify
from src.reasoning.engine import decide_resilient as decide     # tenacity-wrapped
from src.tools.registry import Registry
from src.evaluation.gate import evaluate
from src.memory.memory import Memory


class Agent:
    def __init__(self, tools: Registry, max_steps: int = 8, budget: int = 4000):
        self.tools = tools
        self.max_steps = max_steps
        self.memory = Memory(budget=budget)

    def run(self, goal: str, criteria: str, ask_user=input) -> str:
        for step in range(1, self.max_steps + 1):               # bounded loop
            history = "\n".join(self.memory.context(goal))
            decision = decide(goal, self.tools.describe(), history)      # reasoning

            if isinstance(decision, Final):                     # a candidate answer
                ok, feedback = evaluate(goal, decision.answer, criteria)  # evaluation gate
                if ok:
                    return decision.answer                      # soft exit: accepted
                self.memory.add(f"rejected (too weak): {feedback}")
                continue                                        # try again, with the feedback

            if isinstance(decision, Clarify):                   # ambiguous — ask the user
                answer = ask_user(decision.question)            # human in the loop
                self.memory.add(f"user answered: {answer}")
                continue

            observation = self.tools.dispatch(decision.tool, decision.args)   # tools
            self.memory.add(f"{decision.tool}({decision.args}) -> {observation}")  # remember

        return "stopped: reached max_steps"                     # hard stop

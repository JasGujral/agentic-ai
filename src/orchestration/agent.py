"""Orchestration: the loop that wires all seven components and enforces termination."""
from src.planning.planner import make_plan
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

    def run(self, goal: str, criteria: str, ask_user=input, checks: tuple = ()) -> str:
        plan = make_plan(goal, self.tools.describe())           # planning: decompose up front
        self.memory.add("plan:\n" + "\n".join(                  # seed steps AND their success bars
            f"- {s.action}  (done when: {s.success})" for s in plan.steps))
        pending = list(plan.steps)                              # step bars still to satisfy, in order
        for _ in range(self.max_steps):                         # bounded loop
            history = "\n".join(self.memory.context(goal))
            decision = decide(goal, self.tools.describe(), history)      # reasoning

            if isinstance(decision, Final):                     # a candidate answer
                ok, feedback = evaluate(goal, decision.answer, criteria, checks)  # final gate: hard checks + soft judge
                if ok:
                    return decision.answer                      # soft exit: accepted
                self.memory.add(f"rejected (too weak): {feedback}")
                continue                                        # try again, with the feedback

            if isinstance(decision, Clarify):                   # ambiguous — ask the user
                answer = ask_user(decision.question)            # human in the loop
                self.memory.add(f"user answered: {answer}")     # working memory: this run
                self.memory.remember(f"Q: {decision.question} -> A: {answer}",
                                     key=decision.question)      # long-term: don't ask this again
                continue

            observation = self.tools.dispatch(decision.tool, decision.args)   # tools
            self.memory.add(f"{decision.tool}({decision.args}) -> {observation}")  # remember

            if pending:                                         # per-step gate: vs this step's own bar
                ok, feedback = evaluate(goal, observation, pending[0].success)
                if ok:
                    self.memory.add(f"step confirmed: {pending[0].action}")
                    pending.pop(0)                              # bank the win, advance the plan
                else:
                    self.memory.add(f"step not yet met: {feedback}")   # keep going, with the note

        return "stopped: reached max_steps"                     # hard stop

from langgraph.graph import END, StateGraph

from src.domains.mock_calendar.mock_calendar import my_calendar, my_first_event
from src.graph.nodes.after_rescheduling_proposals.main import after_rescheduling_proposals
from src.graph.nodes.before_rescheduling_proposals.main import before_rescheduling_proposals
from src.graph.nodes.conclusion.main import conclusion
from src.graph.nodes.confirm_rescheduling_proposals.main import confirm_rescheduling_proposals
from src.graph.nodes.confirm_start.main import confirm_start
from src.graph.nodes.get_rescheduling_proposals.main import get_rescheduling_proposals
from src.graph.nodes.introduction.main import introduction
from src.graph.nodes.load_calendar.main import load_calendar
from src.graph.nodes.load_invitees.main import load_invitees
from src.graph.nodes.load_user.main import load_user
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.main import (
    invoke_send_rescheduling_proposal_to_invitee,
    send_rescheduling_proposal_to_invitees,
)
from src.graph.nodes.send_rescheduling_proposal_to_invitee_subgraph.main import (
    uncompiled_graph as send_rescheduling_proposal_to_invitee_uncompiled_subgraph,
)
from src.graph.nodes.summarize_calendar.main import summarize_calendar
from src.graph.nodes.update_calendar.main import update_calendar
from src.types.state import InitialState

send_rescheduling_proposal_to_invitee_subgraph = send_rescheduling_proposal_to_invitee_uncompiled_subgraph.compile()


initial_start_time = my_first_event.start_time
initial_end_time = my_first_event.end_time


async def reset_calendar(state: InitialState) -> None:
    await my_calendar.change_event_time(my_first_event.id, initial_start_time, initial_end_time)


uncompiled_graph = StateGraph(InitialState)

uncompiled_graph.set_entry_point("reset_calendar")

uncompiled_graph.add_node("reset_calendar", reset_calendar)
uncompiled_graph.add_node("load_user", load_user)
uncompiled_graph.add_node("introduction", introduction)
uncompiled_graph.add_node("confirm_start", confirm_start)
uncompiled_graph.add_node("summarize_calendar", summarize_calendar)
uncompiled_graph.add_node("load_calendar", load_calendar)
uncompiled_graph.add_node("load_invitees", load_invitees)
uncompiled_graph.add_node("before_rescheduling_proposals", before_rescheduling_proposals)
uncompiled_graph.add_node("get_rescheduling_proposals", get_rescheduling_proposals)
uncompiled_graph.add_node("confirm_rescheduling_proposals", confirm_rescheduling_proposals)
uncompiled_graph.add_node("send_rescheduling_proposal_to_invitees", send_rescheduling_proposal_to_invitees)
# NOTE: We intentionally disable the type checker for this node because the subgraph is invoked via Send
#       with a different input schema than the graph's.
uncompiled_graph.add_node("invoke_send_rescheduling_proposal_to_invitee", invoke_send_rescheduling_proposal_to_invitee)  # pyright: ignore reportArgumentType
uncompiled_graph.add_node("after_rescheduling_proposals", after_rescheduling_proposals)
uncompiled_graph.add_node("conclusion", conclusion)
uncompiled_graph.add_node("update_calendar", update_calendar)
uncompiled_graph.add_node("load_calendar_after_update", load_calendar)

uncompiled_graph.add_edge("reset_calendar", "load_user")
uncompiled_graph.add_edge("load_user", "introduction")
uncompiled_graph.add_edge("introduction", "confirm_start")
uncompiled_graph.add_edge("confirm_start", "load_calendar")
uncompiled_graph.add_edge("load_calendar", "summarize_calendar")
uncompiled_graph.add_edge("summarize_calendar", "load_invitees")
uncompiled_graph.add_edge("load_invitees", "before_rescheduling_proposals")
uncompiled_graph.add_edge("before_rescheduling_proposals", "get_rescheduling_proposals")
uncompiled_graph.add_edge("get_rescheduling_proposals", "confirm_rescheduling_proposals")
uncompiled_graph.add_conditional_edges(
    "confirm_rescheduling_proposals",
    send_rescheduling_proposal_to_invitees,
    ["invoke_send_rescheduling_proposal_to_invitee"],
)
uncompiled_graph.add_edge("invoke_send_rescheduling_proposal_to_invitee", "after_rescheduling_proposals")
uncompiled_graph.add_edge("after_rescheduling_proposals", "update_calendar")
uncompiled_graph.add_edge("update_calendar", "load_calendar_after_update")
uncompiled_graph.add_edge("load_calendar_after_update", "conclusion")
uncompiled_graph.add_edge("conclusion", END)


compiled_graph = uncompiled_graph.compile()

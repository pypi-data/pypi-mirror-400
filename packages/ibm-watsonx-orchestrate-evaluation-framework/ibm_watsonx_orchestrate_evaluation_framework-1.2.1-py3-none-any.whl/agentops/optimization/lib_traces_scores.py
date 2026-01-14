from langfuse import Langfuse

from agentops.otel_parser.parser import parse_session

langfuse = Langfuse()
langfuse.auth_check()


def get_session_ids():
    sessions = langfuse.api.sessions.list()
    res = []
    for session in sessions.data:
        res.append(session.id)
    return res


def get_scores_by_session(
    session_id, score_names=["Journey Success"], limit=10
):
    scores = langfuse.api.score_v_2.get(session_id=session_id, limit=limit)
    score_list = []
    for score in scores.data:
        print(score.name, score.value, score.session_id)
        if score.name in score_names:
            score_list.append({"score_name": score.name, "value": score.value})
    return score_list


# I did not test this function
def get_traces_by_session(session_id):
    messages = parse_session(session_id)
    return messages


def get_scores_by_session_print(
    session_id, score_name="Journey Success", limit=10
):
    scores = langfuse.api.score_v_2.get(session_id=session_id, limit=limit)
    for score in scores.data:
        print("--------------------------------")
        print(f"Score: {score.name} = {score.value}")
        print(f"Trace ID: {score.trace_id}")
        print("--------------------------------")


def get_traces_by_session_print(session_id, name=None, limit=10):
    # Query traces with specific name and session_id
    if name is None:
        traces = langfuse.api.trace.list(
            session_id=session_id,  # or session1_id
            limit=limit,  # Optional: adjust as needed
        )
    else:
        traces = langfuse.api.trace.list(
            name=name,  # Replace with your trace name
            session_id=session_id,  # or session1_id
            limit=limit,  # Optional: adjust as needed
        )
    for trace in traces.data:
        # Get full trace details including observations
        full_trace = langfuse.api.trace.get(trace.id)
        print("--------------------------------")
        print(f"[Trace ID]: {full_trace.id}")
        print(f"[Trace Name]: {full_trace.name}")
        print(f"[Session ID]: {full_trace.session_id}")
        print(f"[Input]: {full_trace.input}")
        # print the input key value pairs
        if full_trace.input is not None:
            for key, value in full_trace.input.items():
                print(f"    [{key}]: {value}")
        if full_trace.output is not None:
            print("======")
            print(full_trace.output)
            print("======")
            for key, value in full_trace.output.items():
                print(f"    [{key}]: {value}")
        if trace.metadata is not None:
            for key, value in trace.metadata.items():
                print(f"    [{key}]: {value}")
        print("--------------------------------")
        # Access observations (spans, generations, events)
        if hasattr(full_trace, "observations"):
            for obs in full_trace.observations:
                print(f"  [Observation Name]: {obs.name}")
                print(f"  [Observation ID]: {obs.id}")
                print(f"    [Input]: {obs.input}")
                print(f"    [Output]: {obs.output}")
                print("--------------------------------")
        print("--------------------------------")
        print()


def get_conversation_from_trace(trace):
    conversation = []
    for message in trace:
        conversation.append(f"{message.role}: {message.content}")
    conversation = "\n".join(conversation)
    return conversation


def get_traces_and_scores(
    session_id, name=None, limit=100, score_names=["Journey Success"]
):
    trace = get_traces_by_session(session_id)
    conversation = get_conversation_from_trace(trace)
    score = get_scores_by_session(session_id, score_names)
    return {
        "conversation": conversation,
        "session_id": session_id,
        "score": score,
    }

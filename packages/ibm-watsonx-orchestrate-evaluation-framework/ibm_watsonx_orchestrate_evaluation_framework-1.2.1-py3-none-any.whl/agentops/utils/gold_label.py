from agentops.type import ContentType


def get_gold_tool_calls(ground_truth):
    tool_dictionary = (
        {
            goal_detail.name: goal_detail
            for goal_detail in ground_truth.goal_details
            if goal_detail.type == ContentType.tool_call
        }
        if ground_truth.goal_details
        else {}
    )

    return tool_dictionary

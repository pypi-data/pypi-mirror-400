def dump_flow_result(result, user_content_block=False):
    if isinstance(result, dict):
        for m in result["messages"]:
            if user_content_block:
                for content_blocks in m.content_blocks:
                    print("---------------------------------------------------")
                    print(content_blocks)
            else:
                m.pretty_print()
    else:
        for e in result:
            if isinstance(e, tuple):
                e[0].pretty_print()
            else:
                messages = e.get("messages")
                if messages is not None:
                    messages[-1].pretty_print()

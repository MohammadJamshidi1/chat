from user_agents import parse

def get_device_info(request):
    user_id = request.META.get("HTTP_USER_AGENT", "")
    user_agent = parse(user_id)

    device_name = f"{user_agent.browser.family} on {user_agent.os.family}"
    return device_name

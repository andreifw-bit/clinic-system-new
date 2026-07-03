def format_fee(value):
    return f"${value:.2f}"

def priority_color(priority):
    if priority == "urgent":
        return "yellow"
    if priority == "emergency":
        return "red"
    return "green"

def priority_color_again(priority):
    if priority == "urgent":
        return "yellow"
    if priority == "emergency":
        return "red"
    return "green"

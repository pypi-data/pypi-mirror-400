def parse_options(ctx, param, value):
    options = {}
    for item in value:
        key, val = item.split("=", 1)
        options[key] = val
    return options

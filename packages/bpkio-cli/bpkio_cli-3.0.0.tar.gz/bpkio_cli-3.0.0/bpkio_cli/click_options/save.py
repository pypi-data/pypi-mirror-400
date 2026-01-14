import functools

from cloup import option, option_group


def save_options(fn):
    @option_group(
        "Content storing options",
        option(
            "--save",
            "output_directory",
            type=str,
            is_flag=False,
            default=None,
            flag_value=".",
            help="Directory in which to save the content (defaults to the current directory)",
        ),
    )
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper

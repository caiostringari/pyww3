"""
Helpers to deal with namelists.
"""

from logging import warning


def remove_namelist_block(text, block):

    if not block.startswith("&"):
        raise ValueError("Block must start with \'&\'")

    if block not in text:
        raise ValueError(f"Could not find block \'{block}\' in the text.")

    # initializing split word
    spl_word = block

    p1 = text.partition(spl_word)[0]
    p2 = text.partition(spl_word)[2]

    # this is the next occoring /
    p2 = p2.partition("/")[2]

    warn = f"\n! {block} WAS REMOVED by pyww3.namelists.remove_namelsit_block()."
    new_text = p1 + warn + p2  # rebuilt text

    return new_text


def add_namelist_block(text, block, index: int = -1):
    """Add a namelist block at an index in the text string."""

    warn = "\n! TEXT ADDED by pyww3.namelists.add_namelsit_block()."

    if not block.startswith("&"):
        raise ValueError("Block must start with \'&\'")

    if not block.endswith("/"):
        raise ValueError("Block must end with \'/\'")

    # block is already defined
    blockname = block.split("\n")[0]
    if blockname in text:
        warning(f"Block \'{blockname}\' is already in the text. I am trying to update it for you.")

        p1 = text.partition(blockname)[0]
        p2 = text.partition(blockname)[2]

        # this is the next occoring /
        p2 = p2.partition("/")[2]

        newtext = p1 + warn + "\n" + block + p2  # rebuilt text

        # raise NotImplementedError(warning)

    # block is not defined
    else:
        # append to the end of the file
        if index == -1:
            newtext = text + warn + "\n" + block + "\n"
        else:
            # append at a given location
            p1 = text[:index]
            p2 = text[index:]

            newtext = p1 + "\n" + block + p2 + "\n"

    return newtext

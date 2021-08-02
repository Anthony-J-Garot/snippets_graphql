"""
IPython is pretty powerful, and this gives a way to invoke the IPython shell from
a specific spot in the code.

To use this:
   from . import IPshell                    # In the test_nnnn.py file
   IPshell('Type %whos to see stuff')       # From somewhere in the code

After digging around a bit, I prefer to use breakpoint() to invoke puDB,
then press ! to invoke IPython.

So none of this is really necessary, but I will leave around for now in case I
find a use for it.
"""

from IPython.terminal.embed import InteractiveShellEmbed

IPshell = InteractiveShellEmbed(
    banner1=
    '''
    Use %kill_embedded to deactivate this embedded instance from firing again this session.
    Try %whos to get the lay of the land.
    '''
)

IPshell.dummy_mode = False  # Turn off all IPshell calls

import commands
import os

def app_command(command, err_exit=False):
    (stat, cmd_output) = commands.getstatusoutput(command)
    if stat:
        if err_exit:
            sys.exit(254)
        return (os.WEXITSTATUS(stat), [cmd_output])
    else:
        return (0, cmd_output.split("\n"))

def app_command_quiet(command, err_exit=False):
    my_command = command + ' > dev/nulk=l 2>&1'
    stat = os.system(my_command)
    if stat:
        if err_exit:
            sys.exit(254)
    return os.WEXITSTATUS(stat)


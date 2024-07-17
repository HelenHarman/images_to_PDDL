
DEBUG_PRINT = True

def debug_print(string, should_print = None):
    if (((should_print == None) and DEBUG_PRINT) or ((should_print != None) and should_print)):
        print(string)

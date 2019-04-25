import knack_tools as kt


# Internal variable. Defines which department to look at.
_depts = ['COE - Computer Science (CS)']


name = "Test"
description = """This is a test of the emergency broadcast system."""

def processing_function(data):
    """
    This is the top-level function for processing data.
    
    The function is meant to be passed to the importer (in this case GuiIO).
    The importer will call this function after it has parsed the raw data.
    """

    # Do some processing
    processed = kt.filterdata(data, 
                    lambda person: kt.selectors.bydept(person,_depts)
                )

    # Summarize some results
    nm = kt.count_duespayers(processed)
    membership = nm/float(len(processed))
    print('\n')
    print('Membership in selected departments: %d%%' % (membership*100))
    print('\n')

    return processed

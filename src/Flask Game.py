from bqueue import BoundedQueue
from bstack import BoundedStack
import os

DATA_FILE = "4f3c.txt"
UNITS_PER_CHEMICAL = 3
MAX_CAPACITY = 4

ANSI = {
"RESET": "\033[0m",
"CLEARLINE": "\033[0K"
}



def read_data_from_file(chemicals_file):
    """
    Reads flask initialization data from a given text file
    
    Inputs: chemicals_file - a text file containing data on the chemicals to be placed into flasks
    
    Returns: a tuple containing the total number of flasks we need to use, the number of different chemical types available and a list containing the chemicals that we need to assign into flasks
    """
    with open(chemicals_file,'r') as file:
        lines = file.readlines()
    num_flasks,num_chemicals = lines[0].split(' ')
    for i in range(len(lines)):
        lines[i] = lines[i].strip()             
        
    chemicals_data = lines[1:]
    
    return num_flasks,num_chemicals,chemicals_data


    
def create_flasks(num,capacity):
    
    """
    Creates a given number of flasks of a given capacity
    
    Inputs: num - the number of flasks to be created, capacity - the max capacity of each flask
    
    Returns: a list containing all of the flasks that have been created
    """
    flasks = []
    for i in range(int(num)):
        flask = BoundedStack(capacity)
        flasks.append(flask)
    return flasks

def fill_flasks(flasks, chemicals_data):
    """
    Initializes the flasks with chemicals by reading, queueing and dequeuing chemicals from a list of chemicals
    
    Inputs: flasks - a list containing all of the flasks to be filled, chemicals_data - a list containing chemicals and information on when to dequeue them to which flask
    
    Returns: None
    """
    chemicals_queue = BoundedQueue(4)
    for line in chemicals_data:
        
        if line[0].isdigit():  #checks for the line with dequeue instructions instead of a chemical name
            for i in range(int(line[0])):
                chemical = chemicals_queue.dequeue()
                flasks[int(line[2])-1].push(chemical)
                
        else:
            if not chemicals_queue.is_full():
                chemicals_queue.enqueue(line)

def is_sealed(flask):
    """
    Determines if a given flask is sealed (contains 3 of the same chemical)
    
    Inputs: flask - the flask whose sealed status is to be determined
    
    Returns: True if the flask is sealed, False if it is not
    """
    
    
    sealed = True
    elements_list = obtain_flask_elements(flask)
    if flask.is_empty():
        return False
    
    comparison_chemical = elements_list[0]
    for chemical in elements_list:
        if chemical != comparison_chemical:  #sets sealed to False if not all elements in the flask are the same chemical
            sealed = False
    if elements_list.count(comparison_chemical) != UNITS_PER_CHEMICAL: 
        sealed = False

    return sealed
        
def obtain_flask_elements(flask):
    """
    Obtains the elements(chemicals) in a flask as a list
    
    Inputs: flask - the flask whose elements we need
    
    Returns: a list of the elements of the flask
    """
    elements_list = []
    while not flask.is_empty():
        elements_list.append(flask.pop())
    for chemical in elements_list[::-1]:
        flask.push(chemical)  #restores the flask to its original state

    return elements_list[::-1]

def flask_to_printable_list(flask):
    """
    Converts a given flask to a 2D list containing each formatted row to be printed when displaying the flask
    
    Inputs: flask - the flask  which we need to convert to a printable list
    
    Returns: the printable list for the given flask
    """
    flask_list = []
    elements_list = obtain_flask_elements(flask)
    empty_slots = flask.capacity()-flask.size()
    for i in range(empty_slots):
        elements_list.append("  ")
   
    for element in elements_list[::-1]:
        row = []
        row.append(' |')
        if element != "  ":
            row.append(obtain_chemical_color(element)) # appends a colored version of each chemical
        else:
            row.append(element)
        row.append('| ')
        flask_list.append(row)
    border = [" +","-","-","+ "]
    flask_list.append(border)
    if is_sealed(flask):
        flask_list[0] = border
    return flask_list

def split_flasks(flasks):
    """
    Splits a list of flasks into sets of 4
    
    Inputs: flasks - a list of flasks
    
    Returns: a list containing a list for each set of 4 flasks
    
    """
    
    return [flasks[i:i+4] for i in range(0, len(flasks), 4)]


def format_flask_numbers(display_string, flasks,new_flasks,source,destination):
    """
    Formats the flask numbers displayed below each flask 
    
    Inputs: display_string - a string containing the formatted display of the flasks so far, flasks - a list of flasks, new_flasks - a list containing a list for each set of 4 flasks, source - the number of the flask from which a chemical is being transferred, destination - the number of the flask to which a chemical is being transferred
    
    Returns: the display string with flask numbers formatted
    """
    
    digit_colors = {"source": "\033[31m",
                    "destination": "\033[32m"}
    
    
    lower = 4*new_flasks.index(flasks)+1
    upper = lower + len(flasks) 
     
         
        
    for i in range(lower,upper): 
        if i == source:  #changes the digit color of the source flask
            display_string += digit_colors["source"] + str(i) + ANSI["RESET"]
        elif i == destination:  #changes the digit color of the destination flask
            display_string += digit_colors["destination"] + str(i) + ANSI["RESET"]
        else:
            display_string += str(i)
        display_string += "     "
    return display_string

def display_flasks(flasks_list,source,destination):
    """
    Displays all of the flasks with the correct formatting
    
    Inputs: flasks_list - a list containing all of the flasks, source - the number of the flask from which a chemical is being transferred, destination - the number of the flask to which a chemical is being transferred
    
    Returns: None
    """
    
    display_string = ""
    new_flasks = split_flasks(flasks_list)
    
    for flasks in new_flasks:
        for row in range(MAX_CAPACITY+1):
            for flask in flasks:
                flask_list = flask_to_printable_list(flask)
                display_string += "".join(flask_list[row])
            display_string += '\n'
        display_string += "   "
        display_string = format_flask_numbers(display_string,flasks,new_flasks,source,destination)
        display_string += '\n\n'
    move_cursor(6,0)
    print(display_string)
    
def check_flask_condition(flasks,user_input,flask_type):
    """
    Checks if the flask selected by the user is valid
    
    Inputs: flasks - a list of flasks, user_input - the initial user_input, flask_type - a string representing whether the input flask is a source or destination flask
    
    Returns: False if the flask is not valid, True if the flask is valid
    """
    source_flask = flasks[int(user_input)-1]
    destination_flask = flasks[int(user_input)-1]        
    if flask_type == "source":
        if source_flask.is_empty() or is_sealed(source_flask):
            print_location(5,0,'Cannot pour from that flask. Try again.')
            return False
            
    elif flask_type == "destination":
        if destination_flask.is_full() or is_sealed(destination_flask):
            print_location(5,0,'Cannot pour into that flask. Try again.')
            return False
            
    return True

def check_input_validity(user_input,flasks,flask_type):
    """
    Checks if the user input is valid
    
    Inputs: user_input - the initial user_input, flasks - a list of flasks, flask_type - a string representing whether the input flask is a source or destination flask
    
    Returns: a tuple containing the status of the input and the appropriate error message 
    """    
    valid_inputs = [str(i+1) for i in range(len(flasks))] + ['exit']
    
    if not user_input.isdigit():
        user_input = user_input.lower()
        valid_input = False
    if user_input in valid_inputs:
        if user_input.isdigit():
            move_cursor(5,0)
            print(ANSI["CLEARLINE"])             
            valid_input = check_flask_condition(flasks,user_input,flask_type)
            error_message = ""
        else:
            valid_input = True   
            error_message = ""
    else:
        valid_input = False
        error_message = "Invalid input, please try again!"
    return error_message,valid_input
        
def input_loop(flasks,user_input,cursor_pos,flask_type):
    """
    Repeatedly asks the user for an input until a valid input is entered
    
    Inputs: flasks - a list of flasks, user_input - the initial user_input, cursor_pos - the cursor position at which the user must enter the input, flask_type - a string representing whether the input flask is a source or destination flask
    
    Returns: the input once a valid input is entered
    """
    valid_input = False
    error_message,valid_input = check_input_validity(user_input,flasks,flask_type)
    while not valid_input: 
        if error_message:
            move_cursor(5,0)
            print(ANSI["CLEARLINE"]) #clears any previous error message  
            print_location(5,0,error_message)
        move_cursor(cursor_pos[0],cursor_pos[1])
        print(ANSI["CLEARLINE"])  #clears the previous input so the user can enter a new input
        move_cursor(cursor_pos[0],cursor_pos[1])
        user_input = input().strip()
        move_cursor(5,0)
        print(ANSI["CLEARLINE"])        
        error_message,valid_input = check_input_validity(user_input,flasks,flask_type)
        
    return user_input
    
    
def obtain_user_input(flasks):
    """
    Obtains a valid user input for the source and the destinaion flasks
    
    Inputs: flasks - a list of flasks
    
    Returns: a tuple containing the source and destination user inputs
    """    
    move_cursor(3,21)
    source = input().strip()
    source = input_loop(flasks,source,(3,21),"source")
    if type(source) == str:
        source = source.lower()
    if source == "exit": 
        return "exit","exit"  #immediately stops taking input if the source input is "exit"
    
    move_cursor(4,26)
    destination = input().strip()
    if type(destination) == str:
        destination = destination.lower()
    
    destination = input_loop(flasks,destination,(4,26),"destination")
           
    return source,destination


    

def transfer_between_flasks(flasks,source_num,destination_num):
    """
    Checks all transfer conditions and transfers chemicals between flasks, if possible
    
    Inputs: flasks - a list of flasks, source_num - the number of the flask from which a chemical is being transferred, destination_num - the number of the flask to which a chemical is being transferred
    
    Returns: True if a transfer if successful, False if no transfer occurs
    """
    
    source_flask = flasks[source_num-1]
    destination_flask = flasks[destination_num-1]

    if source_num == destination_num:
        print_location(5,0,'Cannot pour into the same flask. Try again.')
        return False
    
    else:
        destination_flask.push(source_flask.pop())
        return True
        
    
def is_game_won(flasks):
    """
    Determines if all flasks are sealed (and if, therefore, the game is won)
    
    Inputs - flasks - a list of flasks
    
    Returns: True if all flasks are sealed, False if at least one flask is not sealed
    """
    for flask in flasks:
        if not is_sealed(flask) and not flask.is_empty():
            return False
    return True

def print_location(x, y, text):
    '''
    Prints text at the specified location on the terminal.
    Input:
        - x (int): row number
        - y (int): column number
        - text (str): text to print
    Returns: N/A
    '''
    print ("\033[{1};{0}H{2}".format(y,x, text))
def move_cursor(x,y):
    '''
    Moves the cursor to the specified location on the terminal.
    Input:
        - x (int): row number
        - y (int): column number
    Returns: N/A
    '''
    print("\033[{1};{0}H".format(y,x), end='')

def obtain_chemical_color(chemical):
    """
    Obtains the correct ANSI color code for a given chemical
    
    Inputs: chemical - the chemical whose color code is required
    
    Returns: a string of the chemical with the appropriate color applied
    """
    chemical_colors = {
    "AA": "\033[41m",
    "BB": "\033[44m",
    "CC": "\033[42m",
    "DD": "\033[48;5;202m",
    "EE": "\033[43m",
    "FF": "\033[45m"}
    return chemical_colors[chemical] + chemical + ANSI["RESET"]

def main():
    
    if os.name == "nt": # for Windows
        os.system("cls")
    else: # for Mac/Linux
        os.system("clear")       
    print("Magical Flask Game")
    num_flasks,num_chemicals,chemicals_data = read_data_from_file(DATA_FILE)
    flasks = create_flasks(num_flasks,MAX_CAPACITY)
    fill_flasks(flasks,chemicals_data) 
    new_flasks = split_flasks(flasks)
    
    source= ""
    destination= ""
    while not is_game_won(flasks) and (source != 'exit' and destination != 'exit'):           
        print_location(3,0,"Select source flask:")
        print_location(4,0,"Select destination flask:")
        if source and destination and transfer_status:
            display_flasks(flasks,int(source),int(destination))
        else:
            display_flasks(flasks,0,0)
        source,destination = obtain_user_input(flasks)
        move_cursor(5,0)
        print(ANSI["CLEARLINE"])           
        if str(source).isdigit() and str(destination).isdigit():
            transfer_status = transfer_between_flasks(flasks,int(source),int(destination))
        move_cursor(4,26)
        print(ANSI["CLEARLINE"])
        move_cursor(3,21)
        print(ANSI["CLEARLINE"]) 
    
    if is_game_won(flasks):
        display_flasks(flasks,int(source),int(destination))
        print_location(20,0,"You Win!")
    else:
        print_location(20,0,"Play again next time!")
    
    
    
   
   
    
    
    
   


main()

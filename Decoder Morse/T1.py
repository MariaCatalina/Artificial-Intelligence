from T1testing import tt_TA
from copy import copy, deepcopy

#generate all characters that can be formed
def getListOfCharacters(alphabet, inputCode, position):
    
    #maximum length for one character
    maxCh = 4;
    result = [];
    
    if len(inputCode) <= maxCh:
        maxCh = len(inputCode);
    
    maxCh = maxCh + position;
    
    for i in range(position, maxCh + 1):
        if i > len(inputCode):
            break;

        ch = inputCode[position : i];
        for (key, value) in alphabet.iteritems():
            if value == ch:
                result.append((key, i));
    
    return result;

#search in tree the parrent of the node or if the position was already calculated
def searchAppearance(tree, parrent, position, check):
    new_tree = {}
    
    if not tree:
        return;
    
    if check == 0:
        if parrent == tree['ch'] and position == tree['pos']:
            return copy(tree);
    else:
        if position == tree['pos']:
            return copy(tree['children']);
    
    copy_tree = copy(tree)
    for d in copy_tree['children'].values():
        if not new_tree:
            new_tree = searchAppearance(copy(d), parrent, position, check);
    
    return new_tree;

def createTree(tree, alphabet, inputCode, dictionary, position, parrent):
    if position > len(inputCode):
        return;
    
    resultList = getListOfCharacters(alphabet, inputCode, position);
    if len(resultList) == 0:
        return;

    #get the specific tree after parrent
    new_tree = searchAppearance(tree, parrent, position, 0);
  
    #extract the number of children
    x = len(new_tree['children']);
  
    copy_res = resultList;
    for (key, value) in copy_res:
       
        #verify if the position was already generated and copy the tree
        generated = searchAppearance(tree, 0, value, 1);
     
        if generated:
            my_tree = {'ch': key, 'pos': value, 'children': copy(generated)};
            new_tree['children'][x] = my_tree;
            x = x + 1;
        else:
            #create a new child and continue the generation
            my_tree = {'ch': key, 'pos': value, 'children': {}};
            new_tree['children'][x] = my_tree;
        
            x = x + 1;
            if value < len(inputCode):
                createTree(copy(tree), alphabet, inputCode, dictionary, value, key);
                
    return;

def constructSolution(tree, word, pos, dictionary, lenInput, solution, final):
    
    #end of word
    if pos + 1 > len(word):
        for new_word in dictionary:
            constructSolution(tree, new_word, 0, dictionary, lenInput, copy(solution), final)
        return;
    
    check = 0;
    
    copy_t = copy(tree)
    for t in copy_t['children'].values():
        if t['ch'] == word[pos]:
            solution.append(t['ch'])
            check = 1;
            
            #verify if it reached the final position in the tree
            if t['pos'] == lenInput:
                
                #verify if it is the end of the current word
                if len(word) == pos + 1:
                    
                    final.append(''.join(solution));
                    return solution;
            else:
                constructSolution(copy(t), word, pos + 1, dictionary, lenInput, solution, final)
    
    #clear the bad solution
    if check == 0:
        del solution[:]
 
    return solution;
        
def findMatch(tree, dictionary, lenInput):
    finalResult = []
    
    #for each word from dictionary construct solution
    for word in dictionary:
        final = []
        result =[]
        
        a = constructSolution(tree, word, 0, dictionary, lenInput, result, final)
        finalResult += final;
 
    return finalResult;

def decode(alphabet, inputCode, dictionary):
    
    #root node
    tree = {'ch': None, 'pos': 0, 'children': {}} 
    createTree(tree, alphabet, inputCode, dictionary, 0, None);
    
    rez = findMatch(tree, list(dictionary), len(inputCode));

    return rez;

tt_TA(decode, False);
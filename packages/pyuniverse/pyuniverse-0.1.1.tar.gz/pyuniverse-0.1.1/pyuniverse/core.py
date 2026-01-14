import random 

listdirnum = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] 

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'] 

upperletters = [word.upper() for word in letters] 

punctuation = [',', "'", '"', '!', '?', '/', '>'] 

  

  

           

  

def generateNum(a): 

    global listdirnum 

    lenght = [] 

    i = 0 

    while i < a: 

        ran = random.randint(0, 9) 

        lenght.append(listdirnum[ran]) 

        i += 1 

         

    r = ''.join(lenght) 

  

    return r 

  

def generateLett(a): 

    global letters 

    lenght = [] 

    i = 0 

    while i < a: 

        ran = random.randint(0, 9) 

        lenght.append(letters[ran]) 

        i += 1 

         

    r = ''.join(lenght) 

  

    return r 

    

  

  

def generatewhole(a): 

    global listdirnum 

    global letters 

    global upperletters 

    global punctuation 

    lenght = [] 

    i = 0 

    while i < a: 

        chosen = random.randint(1, 3) 

        if chosen == 1: 

            ran = random.randint(0, 9) 

            lenght.append(listdirnum[ran]) 

            i += 1 

        elif chosen == 2: 

            ran = random.randint(0, 25) 

            lenght.append(letters[ran]) 

            i += 1 

        elif chosen == 3: 

            ran = random.randint(0, 25) 

            lenght.append(upperletters[ran]) 

            i += 1 

         

    r = ''.join(lenght) 

  

    return r 

    

def generatewholewithpunc(a): 

    global listdirnum 

    global letters 

    global upperletters 

    global punctuation 

    lenght = [] 

    i = 0 

    while i < a: 

        chosen = random.randint(1, 4) 

        if chosen == 1: 

            ran = random.randint(0, 9) 

            lenght.append(listdirnum[ran]) 

            i += 1 

        elif chosen == 2: 

            ran = random.randint(0, 25) 

            lenght.append(letters[ran]) 

            i += 1 

        elif chosen == 3: 

            ran = random.randint(0, 25) 

            lenght.append(upperletters[ran]) 

            i += 1 

        elif chosen == 4: 

            ran = random.randint(0, 6) 

            lenght.append(punctuation[ran]) 

            i += 1 

         

    r = ''.join(lenght) 

  

    return r 

    
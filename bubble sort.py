## bubble sort algor

from Tkinter import *

window = Tk()
canvas = Canvas(window, width=400, height = 400, bg = 'white')
canvas.pack()
objectrectangle = canvas.create_rectangle(50,80,100,120, fill = 'grey')




def bubbleSort():
        
    coins = 300
    ring = 23
    staff = 200
    chest = 10
    diamond = 6000
    listItems = [coins,ring,staff,chest,diamond]
    length = len(listItems) - 1

    unsorted = True
    while unsorted:
        for element in range(0,length):
            unsorted = False
            if listItems[element] > listItems[ element + 1]:
                hold = listItems[element + 1]
                listItems[element + 1] = listItems[element]
                listItems[element] = hold
                print listItems
            else:
                unsorted = True 


b = Button(window, text = 'SORT', command = lambda:bubbleSort())
#canvas.create_window( 10,10, anchor=NW, window = b)
b.pack()


window.mainloop()






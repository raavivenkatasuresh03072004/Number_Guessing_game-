import tkinter as tk
from number_game import NumberGuessingGame

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()
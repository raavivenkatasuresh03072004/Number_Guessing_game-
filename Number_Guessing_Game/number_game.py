import tkinter as tk
from tkinter import messagebox
import random
from playsound import playsound
import threading
import time
import os
import json
import math

class NumberGuessingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Guessing Game")
        self.root.geometry("600x550")
        self.dark_mode = False
        self.sound_on = True
        self.bg_light = "#f2f2f2"
        self.bg_dark = "#1c1c1c"
        self.fg_light = "#000000"
        self.fg_dark = "#ffffff"
        self.wins = 0
        self.losses = 0
        self.high_score = self.load_high_score()
        self.animation_label = None
        self.particles = []
        self.animation_running = False

        self.canvas = tk.Canvas(self.root, width=600, height=550, highlightthickness=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_difficulty_menu()
        self.start_background_animation()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.update_theme()

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.sound_button.config(text="🔊 Sound: ON" if self.sound_on else "🔇 Sound: OFF")

    def update_theme(self):
        bg = self.bg_dark if self.dark_mode else self.bg_light
        fg = self.fg_dark if self.dark_mode else self.fg_light
        self.root.configure(bg=bg)
        self.canvas.config(bg=bg)
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                try:
                    widget.configure(bg=bg, fg=fg)
                except:
                    pass

    def play_sound(self, sound_file):
        if self.sound_on and os.path.exists(sound_file):
            threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()

    def load_high_score(self):
        if os.path.exists("highscore.json"):
            with open("highscore.json", "r") as f:
                return json.load(f).get("high_score", float('inf'))
        return float('inf')

    def save_high_score(self, score):
        with open("highscore.json", "w") as f:
            json.dump({"high_score": score}, f)

    def create_difficulty_menu(self):
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()

        bg = self.bg_dark if self.dark_mode else self.bg_light
        fg = self.fg_dark if self.dark_mode else self.fg_light
        self.root.configure(bg=bg)

        menu_frame = tk.Frame(self.root, bg=bg)
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(menu_frame, text="🎯 Choose Difficulty", font=("Arial", 22, "bold"), bg=bg, fg=fg).pack(pady=20)

        tk.Button(menu_frame, text="Easy (1-50, 10 tries)", font=("Arial", 14),
                  command=lambda: self.start_game(1, 50, 10), bg="#4CAF50", fg="white").pack(pady=8)
        tk.Button(menu_frame, text="Medium (1-100, 7 tries)", font=("Arial", 14),
                  command=lambda: self.start_game(1, 100, 7), bg="#2196F3", fg="white").pack(pady=8)
        tk.Button(menu_frame, text="Hard (1-200, 5 tries)", font=("Arial", 14),
                  command=lambda: self.start_game(1, 200, 5), bg="#f44336", fg="white").pack(pady=8)

        settings_frame = tk.Frame(menu_frame, bg=bg)
        settings_frame.pack(pady=15)

        tk.Button(settings_frame, text="🌓 Toggle Theme", command=self.toggle_theme,
                  font=("Arial", 11), bg="#9C27B0", fg="white").pack(side=tk.LEFT, padx=5)
        self.sound_button = tk.Button(settings_frame, text="🔊 Sound: ON", command=self.toggle_sound,
                                      font=("Arial", 11), bg="#FF9800", fg="white")
        self.sound_button.pack(side=tk.LEFT, padx=5)

        stats_frame = tk.Frame(menu_frame, bg=bg)
        stats_frame.pack(pady=15, fill=tk.X)

        tk.Label(stats_frame, text=f"🏆 Wins: {self.wins}   ❌ Losses: {self.losses}",
                 font=("Arial", 13), bg=bg, fg=fg).pack(pady=5)
        if self.high_score != float('inf'):
            tk.Label(stats_frame, text=f"⏱️ Best Time: {self.high_score:.2f} seconds",
                     font=("Arial", 12), bg=bg, fg=fg).pack(pady=5)

    def start_game(self, start, end, attempts):
        self.secret_number = random.randint(start, end)
        self.range_text = f"between {start} and {end}"
        self.attempts_left = attempts
        self.initial_attempts = attempts  # ✅ Track initial for progress
        self.min_val = start
        self.max_val = end
        self.start_time = time.time()
        self.create_game_screen()

    def create_game_screen(self):
        for widget in self.root.winfo_children():
            if widget != self.canvas:
                widget.destroy()

        bg = self.bg_dark if self.dark_mode else self.bg_light
        fg = self.fg_dark if self.dark_mode else self.fg_light
        self.root.configure(bg=bg)

        game_frame = tk.Frame(self.root, bg=bg)
        game_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(game_frame, text=f"Guess the number {self.range_text}",
                 font=("Arial", 18, "bold"), bg=bg, fg=fg).pack(pady=15)

        entry_frame = tk.Frame(game_frame, bg=bg)
        entry_frame.pack(pady=10)

        self.entry = tk.Entry(entry_frame, font=("Arial", 16), width=10, justify='center')
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.focus()

        tk.Button(entry_frame, text="✅ Submit", command=self.check_guess,
                  font=("Arial", 14), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)

        self.entry.bind('<Return>', lambda event: self.check_guess())

        self.feedback = tk.Label(game_frame, text="", font=("Arial", 14, "bold"), bg=bg, fg="#FF5722")
        self.feedback.pack(pady=5)

        self.attempts_label = tk.Label(game_frame, text=f"Attempts left: {self.attempts_left}",
                                       font=("Arial", 14), bg=bg, fg=fg)
        self.attempts_label.pack()

        self.progress_canvas = tk.Canvas(game_frame, width=300, height=20, bg="#e0e0e0")
        self.progress_canvas.pack(pady=5)
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 300, 20, fill="#2196F3", outline="")

        self.update_progress_bar()

        tk.Button(game_frame, text="🔙 Back to Menu", command=self.create_difficulty_menu,
                  font=("Arial", 12), bg="#f44336", fg="white").pack(pady=10)

    def update_progress_bar(self):
        width = (self.attempts_left / self.initial_attempts) * 300
        width = max(0, width)  # ✅ Avoid negative bar
        self.progress_canvas.coords(self.progress_fill, 0, 0, width, 20)

        if self.attempts_left <= 1:
            color = "#f44336"
        elif self.attempts_left <= 3:
            color = "#FF9800"
        else:
            color = "#4CAF50"
        self.progress_canvas.itemconfig(self.progress_fill, fill=color)

    def check_guess(self):
        try:
            guess = int(self.entry.get())
            self.entry.delete(0, tk.END)
        except ValueError:
            self.feedback.config(text="Please enter a valid number.")
            return

        if guess < self.secret_number:
            self.feedback.config(text="Too low!")
            self.play_sound("assets/wrong2.wav")
        elif guess > self.secret_number:
            self.feedback.config(text="Too high!")
            self.play_sound("assets/wrong.wav")
        else:
            self.play_sound("assets/correct2.mp3")
            self.wins += 1
            elapsed = round(time.time() - self.start_time, 2)
            if elapsed < self.high_score:
                self.high_score = elapsed
                self.save_high_score(elapsed)
            messagebox.showinfo("🎉 Congratulations!", f"You guessed it! The number was {self.secret_number}.\nTime: {elapsed} seconds")
            self.create_difficulty_menu()
            return

        self.attempts_left -= 1
        self.attempts_left = max(0, self.attempts_left)  # ✅ Prevent negatives
        self.attempts_label.config(text=f"Attempts left: {self.attempts_left}")
        self.update_progress_bar()

        if self.attempts_left == 0:
            self.losses += 1
            self.play_sound("assets/game_over.wav")
            messagebox.showinfo("💀 Game Over", f"You ran out of attempts! The number was {self.secret_number}")
            self.create_difficulty_menu()

    def start_background_animation(self):
        self.animation_running = True

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()



















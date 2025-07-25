import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import pytz
import pygame
import random
import csv
from cryptography.fernet import Fernet
import os

class SolanaQuestRainbowPunksApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solana Quest: Rainbow Punks")
        self.root.geometry("600x700")

        # Initialize Pygame for sound
        pygame.mixer.init()

        # Initialize encryption
        self.key_file = "key.key"
        self.cipher = self.load_or_generate_key()

        # Initialize SQLite database
        self.conn = sqlite3.connect("rainbow_punks.db")
        self.create_tables()

        # Timezone (UTC+03:00)
        self.timezone = pytz.timezone("Asia/Riyadh")

        # Player variables
        self.player_sol = 0.0
        self.player_nfts = 0

        # NFT attributes
        self.hair_colors = ["Rainbow", "Red", "Blue", "Green", "Purple"]
        self.accessories = ["None", "Glasses", "Hat", "Headband", "Earring"]
        self.types = ["Human", "Robot", "Alien"]

        # Generate 10,000 Rainbow Punks if not already done
        self.generate_nfts()

        # GUI Elements
        self.theme = "dark"
        self.root.configure(bg="#2C2C2C" if self.theme == "dark" else "#FFFFFF")

        # Player stats
        self.stats_var = tk.StringVar(value="SOL: 0.00 | NFTs: 0")
        tk.Label(root, textvariable=self.stats_var, font=("Arial", 16, "bold"), fg="white" if self.theme == "dark" else "black", bg="#2C2C2C" if self.theme == "dark" else "#FFFFFF").pack(pady=10)

        # Theme selection
        tk.Label(root, text="Select Theme:", font=("Arial", 12), fg="white" if self.theme == "dark" else "black", bg="#2C2C2C" if self.theme == "dark" else "#FFFFFF").pack()
        self.theme_var = tk.StringVar(value="Dark")
        ttk.Combobox(root, textvariable=self.theme_var, values=["Dark", "Light"], state="readonly").pack()
        self.theme_var.trace("w", self.update_theme)

        # Quest selection
        tk.Label(root, text="Select Quest:", font=("Arial", 12), fg="white" if self.theme == "dark" else "black", bg="#2C2C2C" if self.theme == "dark" else "#FFFFFF").pack(pady=5)
        self.quests = ["Collect 10 Resources", "Defeat Enemy", "Build Base", "Trade in Marketplace"]
        self.quest_var = tk.StringVar()
        self.quest_combobox = ttk.Combobox(root, textvariable=self.quest_var, values=self.quests, state="readonly")
        self.quest_combobox.pack(pady=5)
        if self.quests:
            self.quest_var.set(self.quests[0])

        # Buttons
        tk.Button(root, text="Complete Quest", command=self.complete_quest, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="Trade NFT", command=self.trade_nft, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="View NFTs", command=self.view_nfts, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="View Quest History", command=self.view_quests, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="View Statistics", command=self.view_statistics, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="Export to CSV", command=self.export_to_csv, font=("Arial", 12)).pack(pady=5)

        # Update stats
        self.update_stats()

    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as key_file:
                key = key_file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as key_file:
                key_file.write(key)
        return Fernet(key)

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nfts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                punk_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                hair_color TEXT NOT NULL,
                accessory TEXT NOT NULL,
                owner TEXT,
                encrypted_metadata TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                quest_name TEXT NOT NULL,
                sol_reward REAL NOT NULL,
                nft_id INTEGER
            )
        ''')
        self.conn.commit()

    def generate_nfts(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM nfts")
        if cursor.fetchone()[0] >= 10000:
            return  # NFTs already generated
        for punk_id in range(1, 10001):
            punk_type = random.choice(self.types)
            hair_color = random.choice(self.hair_colors)
            accessory = random.choice(self.accessories)
            metadata = f"Rainbow Punk #{punk_id}: {punk_type}, {hair_color} Hair, {accessory}"
            encrypted_metadata = self.cipher.encrypt(metadata.encode()).decode()
            cursor.execute("INSERT INTO nfts (punk_id, type, hair_color, accessory, owner, encrypted_metadata) VALUES (?, ?, ?, ?, ?, ?)",
                          (punk_id, punk_type, hair_color, accessory, None, encrypted_metadata))
        self.conn.commit()
        messagebox.showinfo("Success", "Generated 10,000 Rainbow Punk NFTs!")

    def visual_feedback(self, success=True):
        color = "green" if success else "red"
        for _ in range(3):
            self.root.configure(bg=color)
            self.stats_var.set("SUCCESS!" if success else "ERROR!")
            self.root.update()
            self.root.after(100)
            self.root.configure(bg="#2C2C2C" if self.theme == "dark" else "#FFFFFF")
            self.update_stats()
            self.root.update()
            self.root.after(100)

    def play_sound(self, action="quest"):
        try:
            sound_file = {"quest": "quest.wav", "reward": "reward.wav", "mint": "mint.wav"}[action]
            pygame.mixer.Sound(sound_file).play()
        except:
            pass  # Skip sound if file not found

    def update_theme(self, *args):
        self.theme = self.theme_var.get().lower()
        bg_color = "#2C2C2C" if self.theme == "dark" else "#FFFFFF"
        fg_color = "white" if self.theme == "dark" else "black"
        self.root.configure(bg=bg_color)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=bg_color, fg=fg_color)

    def update_stats(self):
        self.stats_var.set(f"SOL: {self.player_sol:.2f} | NFTs: {self.player_nfts}")

    def complete_quest(self):
        quest_name = self.quest_var.get()
        if not quest_name:
            messagebox.showerror("Error", "Select a quest!")
            self.visual_feedback(success=False)
            return

        # Simulate quest rewards
        sol_reward = random.uniform(0.1, 1.0)
        nft_reward = random.randint(0, 1) if random.random() < 0.3 else 0  # 30% chance for NFT
        timestamp = datetime.now(self.timezone).strftime("%Y-%m-%d %H:%M:%S")
        nft_id = None

        if nft_reward:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM nfts WHERE owner IS NULL LIMIT 1")
            nft = cursor.fetchone()
            if nft:
                nft_id = nft[0]
                cursor.execute("UPDATE nfts SET owner = ? WHERE id = ?", ("player", nft_id))
                self.player_nfts += 1

        # Save quest to database
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO quests (timestamp, quest_name, sol_reward, nft_id) VALUES (?, ?, ?, ?)",
                      (timestamp, quest_name, sol_reward, nft_id))
        self.conn.commit()

        self.player_sol += sol_reward
        self.update_stats()
        messagebox.showinfo("Success", f"Quest '{quest_name}' completed!\nEarned: {sol_reward:.2f} SOL, {nft_reward} NFT(s)")
        self.visual_feedback(success=True)
        self.play_sound("quest")

        # Raffle for bonus rewards
        if random.random() < 0.2:  # 20% chance
            bonus_sol = random.uniform(0.5, 2.0)
            self.player_sol += bonus_sol
            self.update_stats()
            messagebox.showinfo("Raffle Win!", f"Congratulations! You won a bonus {bonus_sol:.2f} SOL in the raffle!")
            self.visual_feedback(success=True)
            self.play_sound("reward")

    def trade_nft(self):
        if self.player_nfts == 0:
            messagebox.showerror("Error", "No NFTs to trade!")
            self.visual_feedback(success=False)
            return
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, encrypted_metadata FROM nfts WHERE owner = 'player' LIMIT 1")
        nft = cursor.fetchone()
        if nft:
            sol_earned = random.uniform(0.5, 2.0)
            self.player_sol += sol_earned
            self.player_nfts -= 1
            cursor.execute("UPDATE nfts SET owner = NULL WHERE id = ?", (nft[0],))
            self.conn.commit()
            try:
                nft_name = self.cipher.decrypt(nft[1].encode()).decode()
            except:
                nft_name = "Unknown NFT"
            messagebox.showinfo("Success", f"Traded {nft_name} for {sol_earned:.2f} SOL!")
            self.visual_feedback(success=True)
            self.play_sound("reward")
        else:
            messagebox.showerror("Error", "No NFTs available!")
            self.visual_feedback(success=False)

    def view_nfts(self):
        window = tk.Toplevel(self.root)
        window.title("Rainbow Punk NFTs")
        window.geometry("600x400")
        tree = ttk.Treeview(window, columns=("ID", "Punk ID", "Type", "Hair Color", "Accessory", "Owner"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Punk ID", text="Punk ID")
        tree.heading("Type", text="Type")
        tree.heading("Hair Color", text="Hair Color")
        tree.heading("Accessory", text="Accessory")
        tree.heading("Owner", text="Owner")
        tree.column("ID", width=50)
        tree.column("Punk ID", width=80)
        tree.column("Type", width=100)
        tree.column("Hair Color", width=100)
        tree.column("Accessory", width=100)
        tree.column("Owner", width=100)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, punk_id, type, hair_color, accessory, owner FROM nfts WHERE owner = 'player'")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def view_quests(self):
        window = tk.Toplevel(self.root)
        window.title("Quest History")
        window.geometry("600x400")
        tree = ttk.Treeview(window, columns=("ID", "Timestamp", "Quest", "SOL", "NFT ID"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Timestamp", text="Timestamp")
        tree.heading("Quest", text="Quest")
        tree.heading("SOL", text="SOL Reward")
        tree.heading("NFT ID", text="NFT ID")
        tree.column("ID", width=50)
        tree.column("Timestamp", width=150)
        tree.column("Quest", width=150)
        tree.column("SOL", width=100)
        tree.column("NFT ID", width=100)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, timestamp, quest_name, sol_reward, nft_id FROM quests")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], f"{row[3]:.2f}", row[4] or "None"))

    def view_statistics(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(sol_reward), COUNT(nft_id) FROM quests")
        stats = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM nfts WHERE owner = 'player'")
        owned_nfts = cursor.fetchone()[0]
        if stats[0] == 0:
            messagebox.showinfo("Statistics", "No quests completed!")
            return
        messagebox.showinfo("Statistics", f"Quests Completed: {stats[0]}\nTotal SOL Earned: {stats[1]:.2f}\nTotal NFTs Earned: {stats[2]}\nNFTs Owned: {owned_nfts}")
        self.visual_feedback(success=True)

    def export_to_csv(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, timestamp, quest_name, sol_reward, nft_id FROM quests")
        with open("rainbow_punk_quests.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Timestamp", "Quest", "SOL Reward", "NFT ID"])
            writer.writerows(cursor.fetchall())
        cursor.execute("SELECT id, punk_id, type, hair_color, accessory, owner FROM nfts")
        with open("rainbow_punk_nfts.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Punk ID", "Type", "Hair Color", "Accessory", "Owner"])
            writer.writerows(cursor.fetchall())
        messagebox.showinfo("Success", "Quest and NFT data exported to CSV!")
        self.visual_feedback(success=True)
        self.play_sound("reward")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = SolanaQuestRainbowPunksApp(root)
    root.mainloop()
  pip install pygame pytz cryptography
python solana_quest_rainbow_punks.py
from solana.rpc.api import Client
def mint_nft_onchain(self, metadata):
    client = Client("https://api.devnet.solana.com")
    # Add Solana NFT minting logic (e.g., via GameShift)
  

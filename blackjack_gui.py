import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
from blackjack import BlackjackGame, Card, Suit

class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack")
        self.root.geometry("1100x800")
        self.root.configure(bg="#1a5d3a")  # Green table background
        
        self.game = BlackjackGame()
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")
        
        # Store PhotoImage objects to prevent garbage collection
        self.card_images = {}
        self.chip_image = None
        self.load_card_images()
        
        # State variables
        self.in_game = False
        self.betting_mode = False
        self.current_bet_display = 0
        
        # Create UI
        self.setup_ui()
    
    def load_card_images(self):
        """Load all card images into memory"""
        card_width = 80
        card_height = 120
        
        # Load back image
        back_path = os.path.join(self.assets_path, "back.png")
        if os.path.exists(back_path):
            img = Image.open(back_path)
            img = img.resize((card_width, card_height), Image.Resampling.LANCZOS)
            self.card_images['back'] = ImageTk.PhotoImage(img)
        
        # Load chip image
        chip_path = os.path.join(self.assets_path, "chips.png")
        if os.path.exists(chip_path):
            img = Image.open(chip_path)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            self.chip_image = ImageTk.PhotoImage(img)
        
        # Load all card images
        for suit in Suit:
            suit_name = suit.name.lower()
            
            # Number cards
            for num in range(2, 11):
                filename = f"{suit_name}_{num:02d}.png"
                self.load_single_image(filename, card_width, card_height)
            
            # Face cards and ace
            for card_type in ['ace', 'jack', 'queen', 'king']:
                filename = f"{suit_name}_{card_type}.png"
                self.load_single_image(filename, card_width, card_height)
    
    def load_single_image(self, filename, width, height):
        """Load a single card image"""
        path = os.path.join(self.assets_path, filename)
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            self.card_images[filename] = ImageTk.PhotoImage(img)
    
    def setup_ui(self):
        """Setup the main UI"""
        # Title
        title_frame = tk.Frame(self.root, bg="#1a5d3a")
        title_frame.pack(pady=10)
        tk.Label(title_frame, text="BLACKJACK", font=("Arial", 28, "bold"), 
                fg="white", bg="#1a5d3a").pack()
        
        # Dealer section
        dealer_frame = tk.LabelFrame(self.root, text="Dealer", font=("Arial", 12, "bold"),
                                     bg="#1a5d3a", fg="white", highlightthickness=0)
        dealer_frame.pack(pady=10, padx=20, fill="x")
        
        self.dealer_cards_frame = tk.Canvas(dealer_frame, bg="#1a5d3a", highlightthickness=0, height=130, width=500)
        self.dealer_cards_frame.pack(pady=10)
        
        self.dealer_value_label = tk.Label(dealer_frame, text="", font=("Arial", 14, "bold"),
                                           fg="yellow", bg="#1a5d3a")
        self.dealer_value_label.pack()
        
        # Player section
        player_frame = tk.LabelFrame(self.root, text="Player", font=("Arial", 12, "bold"),
                                     bg="#1a5d3a", fg="white", highlightthickness=0)
        player_frame.pack(pady=10, padx=20, fill="x")
        
        self.player_cards_frame = tk.Canvas(player_frame, bg="#1a5d3a", highlightthickness=0, height=130, width=500)
        self.player_cards_frame.pack(pady=10)
        
        self.player_value_label = tk.Label(player_frame, text="", font=("Arial", 14, "bold"),
                                           fg="yellow", bg="#1a5d3a")
        self.player_value_label.pack()
        
        # Game info section
        info_frame = tk.Frame(self.root, bg="#1a5d3a")
        info_frame.pack(pady=10)
        
        self.balance_label = tk.Label(info_frame, text="", font=("Arial", 12),
                                      fg="white", bg="#1a5d3a")
        self.balance_label.pack(side="left", padx=20)
        
        self.bet_label = tk.Label(info_frame, text="", font=("Arial", 12),
                                 fg="white", bg="#1a5d3a")
        self.bet_label.pack(side="left", padx=20)
        
        self.shoe_label = tk.Label(info_frame, text="", font=("Arial", 12),
                                  fg="white", bg="#1a5d3a")
        self.shoe_label.pack(side="left", padx=20)
        
        # Betting section (chip betting)
        self.betting_frame = tk.LabelFrame(self.root, text="Betting", font=("Arial", 12, "bold"),
                                          bg="#1a5d3a", fg="white", highlightthickness=0)
        self.betting_frame.pack(pady=10, padx=20, fill="x")
        
        self.bet_chips_frame = tk.Frame(self.betting_frame, bg="#1a5d3a")
        self.bet_chips_frame.pack(pady=10)
        
        # Chip buttons (100 dollar chips)
        self.chip_button = tk.Button(self.bet_chips_frame, image=self.chip_image, 
                                     command=self.add_chip, bg="#1a5d3a", 
                                     bd=0, highlightthickness=0)
        self.chip_button.pack(side="left", padx=10)
        
        chip_label = tk.Label(self.bet_chips_frame, text="$100", font=("Arial", 12, "bold"),
                             fg="white", bg="#1a5d3a")
        chip_label.pack(side="left", padx=5)
        
        self.current_bet_chips_label = tk.Label(self.betting_frame, text="Current Bet: $0",
                                               font=("Arial", 12, "bold"),
                                               fg="yellow", bg="#1a5d3a")
        self.current_bet_chips_label.pack(pady=5)
        
        # Message section
        self.message_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"),
                                      fg="gold", bg="#1a5d3a")
        self.message_label.pack(pady=10)
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg="#1a5d3a")
        button_frame.pack(pady=20)
        
        self.hit_button = tk.Button(button_frame, text="HIT", font=("Arial", 14, "bold"),
                                   width=10, bg="#ff6b6b", fg="white",
                                   command=self.hit, state="disabled")
        self.hit_button.pack(side="left", padx=5)
        
        self.stand_button = tk.Button(button_frame, text="STAND", font=("Arial", 14, "bold"),
                                      width=10, bg="#4ecdc4", fg="white",
                                      command=self.stand, state="disabled")
        self.stand_button.pack(side="left", padx=5)
        
        self.double_button = tk.Button(button_frame, text="DOUBLE DOWN", font=("Arial", 12, "bold"),
                                       width=12, bg="#ffa500", fg="white",
                                       command=self.double_down, state="disabled")
        self.double_button.pack(side="left", padx=5)
        
        self.split_button = tk.Button(button_frame, text="SPLIT", font=("Arial", 14, "bold"),
                                      width=10, bg="#9b59b6", fg="white",
                                      command=self.split, state="disabled")
        self.split_button.pack(side="left", padx=5)
        
        # Betting buttons
        bet_button_frame = tk.Frame(self.root, bg="#1a5d3a")
        bet_button_frame.pack(pady=10)
        
        self.deal_button = tk.Button(bet_button_frame, text="DEAL", font=("Arial", 14, "bold"),
                                    width=12, bg="#45b7d1", fg="white",
                                    command=self.deal)
        self.deal_button.pack(side="left", padx=10)
        
        self.clear_bet_button = tk.Button(bet_button_frame, text="CLEAR BET", font=("Arial", 12, "bold"),
                                         width=12, bg="#e74c3c", fg="white",
                                         command=self.clear_bet)
        self.clear_bet_button.pack(side="left", padx=10)
        
        self.next_hand_button = tk.Button(bet_button_frame, text="NEXT HAND", font=("Arial", 12, "bold"),
                                         width=12, bg="#2ecc71", fg="white",
                                         command=self.reset_for_next_game, state="disabled")
        self.next_hand_button.pack(side="left", padx=10)
        
        # Start in betting mode
        self.betting_mode = True
        self.update_info()
    
    def get_card_image(self, card):
        """Get PhotoImage for a card"""
        filename = card.get_image_filename()
        return self.card_images.get(filename, self.card_images.get('back'))
    
    def get_hand_breakdown(self, hand):
        """Get a string breakdown of hand like '10 + 9 = 19'"""
        if not hand.cards:
            return ""
        
        card_values = [str(card.get_value()) for card in hand.cards]
        total = hand.get_value()[0]
        return " + ".join(card_values) + f" = {total}"
    
    def add_chip(self):
        """Add a $100 chip to current bet"""
        if not self.betting_mode:
            return
        
        if self.current_bet_display + 100 > self.game.player_balance + self.current_bet_display:
            messagebox.showwarning("Insufficient Balance", "Not enough balance to add this chip")
            return
        
        self.current_bet_display += 100
        self.current_bet_chips_label.config(text=f"Current Bet: ${self.current_bet_display}")
    
    def clear_bet(self):
        """Clear the current bet"""
        if not self.betting_mode:
            return
        
        self.current_bet_display = 0
        self.current_bet_chips_label.config(text="Current Bet: $0")
    
    def deal(self):
        """Deal cards and start the game"""
        if not self.betting_mode:
            return
        
        if self.current_bet_display <= 0:
            messagebox.showwarning("No Bet", "Place a bet to play")
            return
        
        if self.game.player_balance <= 0:
            messagebox.showinfo("Game Over", f"You're out of money!\nFinal Balance: ${self.game.player_balance}")
            self.root.quit()
            return
        
        # Place bet
        if not self.game.place_bet(self.current_bet_display):
            messagebox.showerror("Invalid Bet", "Bet must be valid")
            return
        
        # Start game
        self.game.start_round()
        self.in_game = True
        self.betting_mode = False
        self.update_display()
        
        if not self.game.game_over:
            self.hit_button.config(state="normal")
            self.stand_button.config(state="normal")
            
            # Check if double down is possible
            if self.game.can_double_down():
                self.double_button.config(state="normal")
            
            # Check if split is possible
            if self.game.can_split():
                self.split_button.config(state="normal")
            
            self.deal_button.config(state="disabled")
            self.clear_bet_button.config(state="disabled")
            self.chip_button.config(state="disabled")
    
    def display_hand(self, hand, frame, show_all=True):
        """Display cards in a hand"""
        frame.delete("all")
        
        x = 10
        for i, card in enumerate(hand.cards):
            if not show_all and i == 0:
                # Show card back for first dealer card
                img = self.card_images.get('back')
            else:
                img = self.get_card_image(card)
            
            frame.create_image(x, 10, image=img, anchor="nw")
            x += 70
        
        frame.config(height=130, width=500)
    
    def new_game(self):
        """Start a new game"""
        if self.game.player_balance <= 0:
            messagebox.showinfo("Game Over", f"You're out of money!\nFinal Balance: ${self.game.player_balance}")
            self.root.quit()
            return
        
        # Get bet
        bet = simpledialog.askinteger("Place Bet", 
                                     f"Your balance: ${self.game.player_balance}\nEnter bet amount:",
                                     minvalue=1, maxvalue=self.game.player_balance)
        
        if bet is None:
            return
        
        if not self.game.place_bet(bet):
            messagebox.showerror("Invalid Bet", "Bet must be valid")
            return
        
        # Start game
        self.game.start_round()
        self.in_game = True
        self.update_display()
        
        if not self.game.game_over:
            self.hit_button.config(state="normal")
            self.stand_button.config(state="normal")
            self.new_game_button.config(state="disabled")
    
    def hit(self):
        """Player hits"""
        if not self.in_game:
            return
        
        self.game.player_hit()
        self.update_display()
        
        if self.game.game_over:
            self.end_round()
        else:
            # Update button states
            self.double_button.config(state="disabled")  # Can't double after hit
            if not self.game.can_split():
                self.split_button.config(state="disabled")
    
    def stand(self):
        """Player stands"""
        if not self.in_game:
            return
        
        self.game.player_stand()
        self.end_round()
    
    def double_down(self):
        """Player doubles down"""
        if not self.in_game:
            return
        
        if self.game.double_down():
            self.update_display()
            if self.game.game_over:
                # Player busted
                self.end_round()
            else:
                # Automatically stand after doubling down (one card rule)
                self.stand()
        else:
            messagebox.showerror("Can't Double Down", "Cannot double down at this time")
    
    def split(self):
        """Player splits hand"""
        if not self.in_game:
            return
        
        if self.game.split():
            self.update_display()
            self.split_button.config(state="disabled")
        else:
            messagebox.showerror("Can't Split", "Cannot split at this time")
    
    def end_round(self):
        """End the round"""
        self.in_game = False
        self.hit_button.config(state="disabled")
        self.stand_button.config(state="disabled")
        self.double_button.config(state="disabled")
        self.split_button.config(state="disabled")
        
        # Show dealer's hole card
        self.display_hand(self.game.dealer_hand, self.dealer_cards_frame, show_all=True)
        
        # Show dealer's hand breakdown
        dealer_breakdown = self.get_hand_breakdown(self.game.dealer_hand)
        self.dealer_value_label.config(text=dealer_breakdown)
        
        # Show result
        results = {
            "BLACKJACK": "🎉 BLACKJACK! You win!",
            "WIN": "✓ YOU WIN!",
            "LOSE": "✗ YOU LOSE!",
            "BUST": "✗ BUST! You went over 21!",
            "DEALER_BUST": "✓ DEALER BUST! You win!",
            "PUSH": "= PUSH! Tie!"
        }
        
        result_text = results.get(self.game.game_result, "Game Over")
        is_win = "WIN" in self.game.game_result or "BLACKJACK" in self.game.game_result or "DEALER_BUST" in self.game.game_result
        self.message_label.config(text=result_text, fg="gold" if is_win else "#ff6b6b")
        
        self.update_info()
        
        # Enable NEXT HAND button to continue
        self.next_hand_button.config(state="normal")
    
    def reset_for_next_game(self):
        """Reset game state for next round"""
        if self.game.player_balance <= 0:
            messagebox.showinfo("Game Over", f"You're out of money!\nFinal Balance: ${self.game.player_balance}")
            self.root.quit()
            return
        
        self.betting_mode = True
        self.current_bet_display = 0
        self.game.doubled_down = False
        self.game.split_hand = None
        
        self.deal_button.config(state="normal")
        self.clear_bet_button.config(state="normal")
        self.chip_button.config(state="normal")
        self.next_hand_button.config(state="disabled")
        
        self.current_bet_chips_label.config(text="Current Bet: $0")
        self.dealer_value_label.config(text="")
        self.message_label.config(text="")
        
        # Clear cards
        self.dealer_cards_frame.delete("all")
        self.player_cards_frame.delete("all")
        
        self.update_info()
    
    def update_display(self):
        """Update card displays"""
        # Dealer - hide hole card during play
        self.display_hand(self.game.dealer_hand, self.dealer_cards_frame, show_all=not self.in_game)
        
        # Show dealer value always (during play show first card value + hidden, at end show full value)
        if not self.in_game:
            self.dealer_value_label.config(text=f"Value: {self.game.dealer_hand.get_value()[0]}")
        else:
            # During play, show first card value (hidden card not counted in display)
            if len(self.game.dealer_hand.cards) > 0:
                dealer_first_card = self.game.dealer_hand.cards[0].get_value()
                self.dealer_value_label.config(text=f"Showing: {dealer_first_card} + [hidden]")
            else:
                self.dealer_value_label.config(text="Showing: [hidden]")
        
        # Player
        self.display_hand(self.game.player_hand, self.player_cards_frame, show_all=True)
        player_value, soft = self.game.player_hand.get_value()
        soft_str = " (soft)" if soft else ""
        self.player_value_label.config(text=f"Value: {player_value}{soft_str}")
        
        self.message_label.config(text="")
        self.update_info()
    
    def update_info(self):
        """Update balance, bet, and shoe info"""
        if self.betting_mode:
            avail_balance = self.game.player_balance
            self.balance_label.config(text=f"Available: ${avail_balance}")
            self.bet_label.config(text=f"Bet: ${self.current_bet_display}")
        else:
            self.balance_label.config(text=f"Balance: ${self.game.player_balance}")
            self.bet_label.config(text=f"Bet: ${self.game.current_bet}")
        
        self.shoe_label.config(text=f"Shoe: {self.game.deck.cards_remaining()} cards")

def main():
    root = tk.Tk()
    gui = BlackjackGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

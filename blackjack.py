import random
from enum import Enum
from typing import List, Tuple

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Card:
    def __init__(self, suit: Suit, rank: str):
        self.suit = suit
        self.rank = rank
    
    def get_value(self) -> int:
        """Returns the blackjack value of the card"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Will handle Aces as 1 or 11 in hand calculation
        else:
            return int(self.rank)
    
    def get_image_filename(self) -> str:
        """Returns the filename for this card's image"""
        suit_name = self.suit.name.lower()
        rank_name = self.rank.lower()
        
        # Convert rank to proper format
        if rank_name == 'a':
            rank_name = 'ace'
        elif rank_name == 'j':
            rank_name = 'jack'
        elif rank_name == 'q':
            rank_name = 'queen'
        elif rank_name == 'k':
            rank_name = 'king'
        else:
            rank_name = f'{int(rank_name):02d}'  # Format as 02-10
        
        return f"{suit_name}_{rank_name}.png"
    
    def __str__(self) -> str:
        return f"{self.rank}{self.suit.value}"

class Deck:
    def __init__(self, num_decks: int = 4):
        self.num_decks = num_decks
        self.shoe: List[Card] = []
        self.reshuffle_threshold = 52  # Reshuffle when 52 cards left
        self._create_shoe()
    
    def _create_shoe(self):
        """Create and shuffle a shoe of multiple decks"""
        self.shoe = []
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in ranks:
                    self.shoe.append(Card(suit, rank))
        
        random.shuffle(self.shoe)
    
    def draw_card(self) -> Card:
        """Draw a card from the shoe, reshuffle if needed"""
        if len(self.shoe) <= self.reshuffle_threshold:
            print("\n[Shoe running low - Reshuffling deck...]")
            self._create_shoe()
        
        return self.shoe.pop()
    
    def cards_remaining(self) -> int:
        """Return number of cards left in shoe"""
        return len(self.shoe)

class Hand:
    def __init__(self):
        self.cards: List[Card] = []
    
    def add_card(self, card: Card):
        """Add a card to the hand"""
        self.cards.append(card)
    
    def get_value(self) -> Tuple[int, bool]:
        """
        Calculate hand value considering Aces.
        Returns (value, has_soft_ace)
        Soft ace = can be counted as 11 without busting
        """
        total = 0
        aces = 0
        
        for card in self.cards:
            total += card.get_value()
            if card.rank == 'A':
                aces += 1
        
        # Adjust for Aces (count as 1 instead of 11 if needed)
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        has_soft_ace = aces > 0 and total + 10 <= 21
        return total, has_soft_ace
    
    def is_bust(self) -> bool:
        """Check if hand is over 21"""
        return self.get_value()[0] > 21
    
    def is_blackjack(self) -> bool:
        """Check if hand is blackjack (21 with 2 cards)"""
        return len(self.cards) == 2 and self.get_value()[0] == 21
    
    def display(self, hide_first: bool = False) -> str:
        """Return formatted hand display"""
        if hide_first and len(self.cards) > 0:
            return f"[Hidden] {self.cards[1]}"
        
        cards_str = ", ".join(str(card) for card in self.cards)
        value, soft = self.get_value()
        soft_str = " (soft)" if soft else ""
        return f"{cards_str} → {value}{soft_str}"

class BlackjackGame:
    def __init__(self):
        self.deck = Deck(num_decks=4)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.player_balance = 1000
        self.current_bet = 0
        self.game_over = False
        self.game_result = ""
        self.split_hand = None  # For split functionality
        self.doubled_down = False
    
    def get_status(self) -> str:
        """Return current game status"""
        return f"\nBalance: ${self.player_balance} | Cards in Shoe: {self.deck.cards_remaining()}"
    
    def place_bet(self, amount: int) -> bool:
        """Place a bet, return True if successful"""
        if amount <= 0:
            print("Bet must be greater than 0")
            return False
        if amount > self.player_balance:
            print(f"Insufficient balance. You have ${self.player_balance}")
            return False
        
        self.current_bet = amount
        self.player_balance -= amount
        return True
    
    def start_round(self):
        """Deal initial cards to player and dealer"""
        self.game_over = False
        self.game_result = ""
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        
        # Deal 2 cards to each
        for _ in range(2):
            self.player_hand.add_card(self.deck.draw_card())
            self.dealer_hand.add_card(self.deck.draw_card())
        
        # Check for blackjack
        if self.player_hand.is_blackjack():
            if self.dealer_hand.is_blackjack():
                self.game_result = "PUSH"
                self.player_balance += self.current_bet
            else:
                self.game_result = "BLACKJACK"
                self.player_balance += int(self.current_bet * 2.5)
            self.game_over = True
    
    def display_hands(self, hide_dealer_hole: bool = True):
        """Display both hands"""
        if hide_dealer_hole:
            print(f"\nDealer: {self.dealer_hand.display(hide_first=True)}")
        else:
            print(f"\nDealer: {self.dealer_hand.display()}")
        print(f"Player: {self.player_hand.display()}")
    
    def player_hit(self) -> bool:
        """Player hits. Return False if bust"""
        self.player_hand.add_card(self.deck.draw_card())
        if self.player_hand.is_bust():
            self.game_result = "BUST"
            self.game_over = True
            return False
        return True
    
    def player_stand(self):
        """Player stands, dealer plays"""
        self.dealer_play()
    
    def can_double_down(self) -> bool:
        """Check if player can double down (only on first 2 cards)"""
        return len(self.player_hand.cards) == 2 and not self.doubled_down
    
    def can_split(self) -> bool:
        """Check if player can split (same rank, first 2 cards)"""
        if len(self.player_hand.cards) != 2:
            return False
        return self.player_hand.cards[0].rank == self.player_hand.cards[1].rank
    
    def double_down(self) -> bool:
        """Player doubles down - doubles bet and hits once"""
        if not self.can_double_down():
            return False
        
        if self.current_bet > self.player_balance:
            return False
        
        # Double the bet
        self.player_balance -= self.current_bet
        self.current_bet *= 2
        self.doubled_down = True
        
        # Hit once
        self.player_hand.add_card(self.deck.draw_card())
        
        if self.player_hand.is_bust():
            self.game_result = "BUST"
            self.game_over = True
        
        return True
    
    def split(self) -> bool:
        """Player splits hand - only first split for now"""
        if not self.can_split():
            return False
        
        if self.current_bet > self.player_balance:
            return False
        
        # Create split hand with second card
        self.split_hand = Hand()
        self.split_hand.add_card(self.player_hand.cards.pop())
        
        # Deduct split bet from balance
        self.player_balance -= self.current_bet
        
        # Deal new card to main hand
        self.player_hand.add_card(self.deck.draw_card())
        
        return True
    
    def dealer_play(self):
        """Dealer plays until 17 or higher"""
        while self.dealer_hand.get_value()[0] < 17:
            self.dealer_hand.add_card(self.deck.draw_card())
        
        self.determine_winner()
        self.game_over = True
    
    def determine_winner(self):
        """Determine game result"""
        player_value = self.player_hand.get_value()[0]
        dealer_value = self.dealer_hand.get_value()[0]
        
        if self.dealer_hand.is_bust():
            self.game_result = "DEALER_BUST"
            self.player_balance += self.current_bet * 2
        elif player_value > dealer_value:
            self.game_result = "WIN"
            self.player_balance += self.current_bet * 2
        elif player_value == dealer_value:
            self.game_result = "PUSH"
            self.player_balance += self.current_bet
        else:
            self.game_result = "LOSE"
    
    def display_result(self):
        """Display game result"""
        self.display_hands(hide_dealer_hole=False)
        
        results = {
            "BLACKJACK": f"🎉 Blackjack! You win ${int(self.current_bet * 1.5)}",
            "WIN": f"✓ You win! Dealer has {self.dealer_hand.get_value()[0]}",
            "LOSE": f"✗ You lose. Dealer has {self.dealer_hand.get_value()[0]}",
            "BUST": f"✗ Bust! You went over 21",
            "DEALER_BUST": f"✓ Dealer bust! You win ${self.current_bet * 2}",
            "PUSH": f"= Push. Bet returned"
        }
        
        print(f"\n{results.get(self.game_result, 'Game Over')}")
        print(f"Balance: ${self.player_balance}")

def main():
    """Main game loop"""
    game = BlackjackGame()
    
    print("=" * 50)
    print("        WELCOME TO BLACKJACK")
    print("=" * 50)
    print("Rules: Get to 21 without going over. Beat the dealer!")
    print(f"Starting Balance: ${game.player_balance}\n")
    
    while True:
        print(game.get_status())
        
        # Betting
        while True:
            try:
                bet_input = input("\nEnter your bet (or 'quit' to exit): ").strip().lower()
                if bet_input == 'quit':
                    print(f"\nThanks for playing! Final balance: ${game.player_balance}")
                    return
                
                bet = int(bet_input)
                if game.place_bet(bet):
                    break
            except ValueError:
                print("Invalid input. Enter a number or 'quit'")
        
        # Start round
        game.start_round()
        game.display_hands()
        
        # Player's turn
        while not game.game_over:
            action = input("\n(h)it, (s)tand: ").strip().lower()
            
            if action == 'h':
                game.player_hit()
                game.display_hands()
                if game.game_over:
                    break
            elif action == 's':
                game.player_stand()
            else:
                print("Invalid input. Enter 'h' or 's'")
        
        # Show result
        game.display_result()
        
        if game.player_balance <= 0:
            print("\n💔 Game Over! You're out of money!")
            break

if __name__ == "__main__":
    main()

import streamlit as st
import random
import time

# --- YOUR ORIGINAL CLASSES & FUNCTIONS ---

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    def __str__(self):
        return f"{self.rank['rank']} of {self.suit}"

class Deck:
    def __init__(self):
        self.cards = []
        suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
        ranks = [
            {"rank": "A", "value": 11}, {"rank": "2", "value": 2}, {"rank": "3", "value": 3},
            {"rank": "4", "value": 4}, {"rank": "5", "value": 5}, {"rank": "6", "value": 6},
            {"rank": "7", "value": 7}, {"rank": "8", "value": 8}, {"rank": "9", "value": 9},
            {"rank": "10", "value": 10}, {"rank": "J", "value": 10}, {"rank": "Q", "value": 10},
            {"rank": "K", "value": 10},
        ]
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    def shuffle(self):
        if len(self.cards) > 1:
            random.shuffle(self.cards)

    def deal(self, number):
        cards_dealt = []
        for x in range(number):
            if len(self.cards) > 0:
                cards_dealt.append(self.cards.pop())
        return cards_dealt

class Hand:
    def __init__(self, dealer=False):
        self.cards = []
        self.value = 0
        self.dealer = dealer

    def add_card(self, card_list):
        self.cards.extend(card_list)

    def calculate_value(self):
        self.value = 0
        has_ace = False
        for card in self.cards:
            card_value = int(card.rank["value"])
            self.value += card_value
            if card.rank["rank"] == "A":
                has_ace = True
        if has_ace and self.value > 21:
            self.value -= 10

    def get_value(self):
        self.calculate_value()
        return self.value

    def is_blackjack(self):
        return self.get_value() == 21

# --- STREAMLIT FRONTEND SETUP ---

st.set_page_config(page_title="Blackjack Pro", layout="wide")

# Styling for the "Casino Look"
st.markdown("""
    <style>
    .main { background-color: #0b3d2e; color: whiteh }
    .card {
        background: white;
        color: black;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        border: 2px solid #ccc;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
        margin: 5px;
    }
    .Hearts, .Diamonds { color: red; }
    .Spades, .Clubs { color: black; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.player_hand = None
    st.session_state.dealer_hand = None
    st.session_state.deck = None
    st.session_state.game_over = False
    st.session_state.result_msg = ""

def start_game():
    st.session_state.deck = Deck()
    st.session_state.deck.shuffle()
    st.session_state.player_hand = Hand()
    st.session_state.dealer_hand = Hand(dealer=True)
    
    st.session_state.player_hand.add_card(st.session_state.deck.deal(2))
    st.session_state.dealer_hand.add_card(st.session_state.deck.deal(2))
    
    st.session_state.game_started = True
    st.session_state.game_over = False
    st.session_state.result_msg = ""

def render_cards(hand, hide_first=False):
    cols = st.columns(len(hand.cards))
    for i, card in enumerate(hand.cards):
        with cols[i]:
            if hide_first and i == 0:
                st.markdown('<div class="card" style="background: #1a3a6c; color: white;">??</div>', unsafe_allow_html=True)
            else:
                suit_sym = {"Hearts":"♥", "Diamonds":"♦", "Spades":"♠", "Clubs":"♣"}[card.suit]
                st.markdown(f'<div class="card {card.suit}">{card.rank["rank"]}<br>{suit_sym}</div>', unsafe_allow_html=True)

# --- GAME UI ---

st.title("🃏 Blackjack Professional")

if not st.session_state.game_started:
    if st.button("Start New Game", use_container_width=True):
        start_game()
        st.rerun()
else:
    # DEALER SECTION
    st.subheader("Dealer's Hand")
    render_cards(st.session_state.dealer_hand, hide_first=not st.session_state.game_over)
    
    st.divider()

    # PLAYER SECTION
    st.subheader(f"Your Hand (Value: {st.session_state.player_hand.get_value()})")
    render_cards(st.session_state.player_hand)

    # GAME LOGIC BUTTONS
    if not st.session_state.game_over:
        c1, c2, _ = st.columns([1,1,3])
        
        if c1.button("HIT ➕"):
            st.session_state.player_hand.add_card(st.session_state.deck.deal(1))
            if st.session_state.player_hand.get_value() > 21:
                st.session_state.game_over = True
                st.session_state.result_msg = "You busted! Dealer wins."
            st.rerun()

        if c2.button("STAND ✋"):
            st.session_state.game_over = True
            # Dealer Logic: Stand at 17
            while st.session_state.dealer_hand.get_value() < 17:
                st.session_state.dealer_hand.add_card(st.session_state.deck.deal(1))
            
            p_val = st.session_state.player_hand.get_value()
            d_val = st.session_state.dealer_hand.get_value()
            
            if d_val > 21:
                st.session_state.result_msg = "Dealer busted. You win!"
            elif p_val > d_val:
                st.session_state.result_msg = "You win!"
            elif p_val == d_val:
                st.session_state.result_msg = "Tie!"
            else:
                st.session_state.result_msg = "Dealer wins!"
            st.rerun()

    # RESULT DISPLAY
    else:
        st.divider()
        # Convert to lowercase to make checking easier
        msg_lower = st.session_state.result_msg.lower()

        # Specific winner checks
        if "you win" in msg_lower or "dealer busted" in msg_lower:
            st.success(f"### {st.session_state.result_msg}")
            st.balloons()
        elif "tie" in msg_lower:
            st.warning(f"### {st.session_state.result_msg}")
        else:
            # Dealer wins or Player busts
            st.error(f"### {st.session_state.result_msg}")
            # st.snow() # Use this for a "loss" effect if you like!
        
        if st.button("Play Again", use_container_width=True):
            start_game()
            st.rerun()

# Sidebar Info
with st.sidebar:
    st.header("Rules")
    st.write("- Goal: Get closer to 21 than the dealer.")
    st.write("- Aces are 11 (or 1 if you go over 21).")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import random
import matplotlib.pyplot as plt
import seaborn as sns

class Currency:
    def __init__(self, code: str, name: str, initial_strength: float = 1.0):
        """
        Initialize a currency
        
        Args:
            code: Three letter currency code (e.g. USD)
            name: Full name of currency (e.g. US Dollar)
            initial_strength: Base strength of the currency (default 1.0)
        """
        self.code = code
        self.name = name
        self.strength = initial_strength
        self.factors = {}  # Factors affecting this currency
        self.history = [initial_strength]  # Track strength over time
        
    def update_strength(self, factors: Dict[str, float]) -> None:
        """Update currency strength based on factors"""
        self.factors = factors
        
        # Calculate net effect of all factors
        factor_effect = sum(factors.values())
        
        # Apply some randomness to simulate market noise (0.98 to 1.02)
        market_noise = random.uniform(0.98, 1.02)
        
        # Update strength with factors and some randomness
        new_strength = self.strength * (1 + factor_effect) * market_noise
        
        # Ensure currency strength doesn't change too drastically
        max_change = 0.15  # Maximum 15% change per round
        if new_strength > self.strength * (1 + max_change):
            new_strength = self.strength * (1 + max_change)
        elif new_strength < self.strength * (1 - max_change):
            new_strength = self.strength * (1 - max_change)
            
        self.strength = new_strength
        self.history.append(new_strength)


class ForexMarket:
    def __init__(self):
        """Initialize the foreign exchange market"""
        self.currencies = {}
        self.exchange_rates = pd.DataFrame()
        self.round = 0
        self.rate_history = []  # Store exchange rate matrices for analysis
        
    def add_currency(self, code: str, name: str, initial_strength: float = 1.0) -> None:
        """Add a currency to the market"""
        self.currencies[code] = Currency(code, name, initial_strength)
        
    def calculate_exchange_rates(self) -> None:
        """Calculate exchange rates between all currency pairs"""
        codes = list(self.currencies.keys())
        rates = np.zeros((len(codes), len(codes)))
        
        # Calculate all exchange rates
        for i, base in enumerate(codes):
            base_currency = self.currencies[base]
            for j, quote in enumerate(codes):
                quote_currency = self.currencies[quote]
                # Exchange rate = quote currency strength / base currency strength
                rates[i, j] = quote_currency.strength / base_currency.strength
                
        # Create DataFrame for better visualization
        self.exchange_rates = pd.DataFrame(rates, index=codes, columns=codes)
        self.rate_history.append(self.exchange_rates.copy())
        
    def get_exchange_rate(self, base_code: str, quote_code: str) -> float:
        """Get the exchange rate between two currencies"""
        return self.exchange_rates.loc[base_code, quote_code]
        
    def update_market(self, factor_inputs: Dict[str, Dict[str, float]]) -> None:
        """
        Update the market based on factor inputs
        
        Args:
            factor_inputs: Dictionary with currency codes as keys and factor dictionaries as values
                           e.g., {"USD": {"interest_rate": 0.02, "inflation": -0.01}, ...}
        """
        self.round += 1
        
        # Update each currency's strength based on factors
        for currency_code, factors in factor_inputs.items():
            if currency_code in self.currencies:
                self.currencies[currency_code].update_strength(factors)
                
        # Recalculate all exchange rates
        self.calculate_exchange_rates()
        
    def display_rates(self) -> None:
        """Display current exchange rates"""
        print(f"\n--- ROUND {self.round} EXCHANGE RATES ---")
        
        # Format the DataFrame for display with better precision
        pd.set_option('display.precision', 4)
        print(self.exchange_rates.round(4))
        
    def plot_currency_strength(self) -> None:
        """Plot the history of currency strengths"""
        plt.figure(figsize=(10, 6))
        
        for code, currency in self.currencies.items():
            plt.plot(range(len(currency.history)), currency.history, label=code)
            
        plt.title('Currency Strength Over Time')
        plt.xlabel('Round')
        plt.ylabel('Strength')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    def plot_rate_heatmap(self) -> None:
        """Plot a heatmap of current exchange rates"""
        plt.figure(figsize=(10, 8))
        sns.heatmap(self.exchange_rates, annot=True, cmap="YlGnBu", fmt=".4f")
        plt.title(f"Exchange Rate Heatmap (Round {self.round})")
        plt.tight_layout()
        plt.show()


class Simulation:
    def __init__(self):
        """Initialize the simulation"""
        self.market = ForexMarket()
        self.common_factors = [
            "interest_rate",    # Central bank interest rate changes
            "inflation",        # Inflation rate
            "gdp_growth",       # GDP growth
            "political_stability", # Political stability
            "trade_balance",    # Trade balance
            "market_sentiment"  # Market sentiment
        ]
        
    def setup(self) -> None:
        """Set up the simulation with default currencies"""
        # Add currencies with somewhat realistic initial strengths
        self.market.add_currency("USD", "US Dollar", 1.0)
        self.market.add_currency("EUR", "Euro", 1.1)
        self.market.add_currency("GBP", "British Pound", 1.3)
        self.market.add_currency("JPY", "Japanese Yen", 0.009)
        self.market.add_currency("AUD", "Australian Dollar", 0.7)
        self.market.add_currency("CAD", "Canadian Dollar", 0.75)
        self.market.add_currency("CHF", "Swiss Franc", 1.05)
        self.market.add_currency("CNY", "Chinese Yuan", 0.15)
        self.market.add_currency("INR", "Indian Rupee", 0.014)
        
        # Calculate initial exchange rates
        self.market.calculate_exchange_rates()
        
    def get_factor_inputs(self) -> Dict[str, Dict[str, float]]:
        """Get factor inputs from the player"""
        factor_inputs = {}
        
        print("\n--- ENTER ECONOMIC FACTORS ---")
        print("Enter values between -0.1 (very negative) and 0.1 (very positive)")
        print("For example: interest_rate rise of 0.5% might be entered as 0.05")
        
        for currency_code in self.market.currencies:
            print(f"\nFactors for {currency_code}:")
            currency_factors = {}
            
            for factor in self.common_factors:
                while True:
                    try:
                        value = float(input(f"  {factor} (-0.1 to 0.1): "))
                        if -0.1 <= value <= 0.1:
                            currency_factors[factor] = value
                            break
                        else:
                            print("Value must be between -0.1 and 0.1")
                    except ValueError:
                        print("Please enter a valid number")
            
            factor_inputs[currency_code] = currency_factors
            
        return factor_inputs
    
    def run_round(self) -> None:
        """Run a single round of the simulation"""
        # Display current rates
        self.market.display_rates()
        
        # Get factor inputs from player
        factor_inputs = self.get_factor_inputs()
        
        # Update the market
        self.market.update_market(factor_inputs)
        
        # Display new rates
        self.market.display_rates()
        
    def run_simulation(self, num_rounds: int) -> None:
        """Run the simulation for a specified number of rounds"""
        self.setup()
        
        print("\n=== FOREX MARKET SIMULATION ===")
        print(f"Simulating {num_rounds} rounds with 9 currencies")
        
        for round_num in range(1, num_rounds + 1):
            print(f"\n--- ROUND {round_num} ---")
            self.run_round()
            
            if round_num < num_rounds:
                input("\nPress Enter to continue to next round...")
        
        # Show summary visualizations
        self.market.plot_currency_strength()
        self.market.plot_rate_heatmap()


def main():
    """Main function to run the simulation"""
    print("=== FOREX MARKET SIMULATOR ===")
    print("This program simulates a foreign exchange market with 9 currencies.")
    print("The exchange rates are updated each round based on economic factors.")
    
    try:
        num_rounds = int(input("Enter number of rounds to simulate: "))
        if num_rounds < 1:
            print("Number of rounds must be positive. Using default of 5.")
            num_rounds = 5
    except ValueError:
        print("Invalid input. Using default of 5 rounds.")
        num_rounds = 5
    
    sim = Simulation()
    sim.run_simulation(num_rounds)


if __name__ == "__main__":
    main()
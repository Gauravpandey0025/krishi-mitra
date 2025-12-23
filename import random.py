import random
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

class MontyHallGame:
    def _init_(self):
        self.doors = [1, 2, 3]
        self.prize_door = None
        self.player_choice = None
        self.host_opens = None
        self.remaining_door = None
    def setup_game(self):
        self.prize_door = random.choice(self.doors)
        self.player_choice = random.choice(self.doors)
    def host_action(self):
        available_doors = [door for door in self.doors if door != self.player_choice and door != self.prize_door]
        if len(available_doors) == 0:
            available_doors = [door for door in self.doors if door != self.player_choice]
            available_doors.remove(self.prize_door) if self.prize_door in available_doors else None
        self.host_opens = random.choice(available_doors) if available_doors else None
        remaining_doors = [door for door in self.doors if door != self.player_choice and door != self.host_opens]
        self.remaining_door = remaining_doors[0] if remaining_doors else None
    def play_stay_strategy(self):
        return self.player_choice == self.prize_door
    def play_switch_strategy(self):
        return self.remaining_door == self.prize_door
    def get_game_state(self):
        return {
            'prize_door': self.prize_door,
            'player_choice': self.player_choice,
            'host_opens': self.host_opens,
            'remaining_door': self.remaining_door,
            'stay_wins': self.play_stay_strategy(),
            'switch_wins': self.play_switch_strategy()
        }

class MontyHallSimulator:
    def _init_(self):
        self.results = []
        self.stay_wins = 0
        self.switch_wins = 0
        self.total_games = 0
    def run_single_game(self):
        game = MontyHallGame()
        game.setup_game()
        game.host_action()
        state = game.get_game_state()
        self.results.append(state)
        if state['stay_wins']:
            self.stay_wins += 1
        if state['switch_wins']:
            self.switch_wins += 1
        self.total_games += 1
        return state
    def run_simulation(self, num_games=1000):
        print(f"Running {num_games} Monty Hall simulations...")
        self.results = []
        self.stay_wins = 0
        self.switch_wins = 0
        self.total_games = 0
        for i in range(num_games):
            self.run_single_game()
            if (i + 1) % (num_games // 10) == 0:
                print(f"Completed {i + 1} games...")
        self.analyze_results()
    def analyze_results(self):
        stay_rate = self.stay_wins / self.total_games if self.total_games > 0 else 0
        switch_rate = self.switch_wins / self.total_games if self.total_games > 0 else 0
        print(f"\n{'='*60}")
        print("MONTY HALL SIMULATION RESULTS")
        print("="*60)
        print(f"Total Games Played: {self.total_games}")
        print(f"Stay Strategy Wins: {self.stay_wins} ({stay_rate:.1%})")
        print(f"Switch Strategy Wins: {self.switch_wins} ({switch_rate:.1%})")
        print(f"\nTheoretical Probabilities:")
        print(f"Stay Strategy: 33.33% (1/3)")
        print(f"Switch Strategy: 66.67% (2/3)")
        print(f"\nDifference from Theory:")
        print(f"Stay Strategy: {abs(stay_rate - 1/3):.1%} difference")
        print(f"Switch Strategy: {abs(switch_rate - 2/3):.1%} difference")
        return stay_rate, switch_rate
    def get_convergence_data(self, num_games=10000):
        print(f"Analyzing convergence over {num_games} games...")
        stay_wins_running = []
        switch_wins_running = []
        game_numbers = []
        temp_stay = 0
        temp_switch = 0
        for i in range(num_games):
            game = MontyHallGame()
            game.setup_game()
            game.host_action()
            state = game.get_game_state()
            if state['stay_wins']:
                temp_stay += 1
            if state['switch_wins']:
                temp_switch += 1
            if (i + 1) % 100 == 0:
                game_numbers.append(i + 1)
                stay_wins_running.append(temp_stay / (i + 1))
                switch_wins_running.append(temp_switch / (i + 1))
        return game_numbers, stay_wins_running, switch_wins_running

class MontyHallAnalyzer:
    def _init_(self, simulator):
        self.simulator = simulator
    def detailed_analysis(self):
        if not self.simulator.results:
            print("No simulation results available. Run simulation first.")
            return
        df = pd.DataFrame(self.simulator.results)
        print(f"\n{'='*60}")
        print("DETAILED ANALYSIS")
        print("="*60)
        print("\nPrize Distribution:")
        prize_dist = df['prize_door'].value_counts().sort_index()
        for door, count in prize_dist.items():
            print(f"Door {door}: {count} times ({count/len(df):.1%})")
        print("\nPlayer Initial Choice Distribution:")
        choice_dist = df['player_choice'].value_counts().sort_index()
        for door, count in choice_dist.items():
            print(f"Door {door}: {count} times ({count/len(df):.1%})")
        print("\nHost Opens Distribution:")
        host_dist = df['host_opens'].value_counts().sort_index()
        for door, count in host_dist.items():
            print(f"Door {door}: {count} times ({count/len(df):.1%})")
        print("\nWin Rate by Initial Door Choice:")
        for door in [1, 2, 3]:
            door_games = df[df['player_choice'] == door]
            if len(door_games) > 0:
                stay_rate = door_games['stay_wins'].mean()
                switch_rate = door_games['switch_wins'].mean()
                print(f"Initial Choice Door {door}:")
                print(f"  Stay Win Rate: {stay_rate:.1%}")
                print(f"  Switch Win Rate: {switch_rate:.1%}")
    def probability_explanation(self):
        print(f"\n{'='*60}")
        print("PROBABILITY EXPLANATION")
        print("="*60)
        print("\nWhy Switching is Better:")
        print("1. Initially, your door has 1/3 chance of having the prize")
        print("2. The other two doors together have 2/3 chance")
        print("3. When host opens one door (without prize), the remaining")
        print("   door inherits the full 2/3 probability")
        print("4. Therefore: Stay = 1/3, Switch = 2/3")
        print("\nBayesian Analysis:")
        print("P(Prize in your door | Host opens door X) = 1/3")
        print("P(Prize in remaining door | Host opens door X) = 2/3")
        print("\nConclusion: Always switch!")

def demonstrate_single_game():
    print("SINGLE GAME DEMONSTRATION")
    print("="*40)
    game = MontyHallGame()
    game.setup_game()
    print(f"Prize is behind door: {game.prize_door}")
    print(f"Player initially chooses door: {game.player_choice}")
    game.host_action()
    print(f"Host opens door: {game.host_opens}")
    print(f"Remaining door to switch to: {game.remaining_door}")
    state = game.get_game_state()
    print(f"\nResults:")
    print(f"Stay strategy wins: {'YES' if state['stay_wins'] else 'NO'}")
    print(f"Switch strategy wins: {'YES' if state['switch_wins'] else 'NO'}")
    print(f"Better choice: {'STAY' if state['stay_wins'] and not state['switch_wins'] else 'SWITCH'}")

def plot_convergence(game_numbers, stay_rates, switch_rates):
    plt.figure(figsize=(12, 8))
    plt.plot(game_numbers, stay_rates, label='Stay Strategy', linewidth=2, color='red')
    plt.plot(game_numbers, switch_rates, label='Switch Strategy', linewidth=2, color='blue')
    plt.axhline(y=1/3, color='red', linestyle='--', alpha=0.7, label='Theoretical Stay (1/3)')
    plt.axhline(y=2/3, color='blue', linestyle='--', alpha=0.7, label='Theoretical Switch (2/3)')
    plt.xlabel('Number of Games')
    plt.ylabel('Win Rate')
    plt.title('Monty Hall Problem: Convergence to Theoretical Probabilities')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    plt.show()

def plot_results_comparison(stay_rate, switch_rate):
    strategies = ['Stay', 'Switch']
    simulated_rates = [stay_rate, switch_rate]
    theoretical_rates = [1/3, 2/3]
    x_pos = np.arange(len(strategies))
    width = 0.35
    plt.figure(figsize=(10, 6))
    plt.bar(x_pos - width/2, simulated_rates, width, label='Simulated', alpha=0.8, color='lightblue')
    plt.bar(x_pos + width/2, theoretical_rates, width, label='Theoretical', alpha=0.8, color='orange')
    plt.xlabel('Strategy')
    plt.ylabel('Win Rate')
    plt.title('Monty Hall Problem: Simulated vs Theoretical Results')
    plt.xticks(x_pos, strategies)
    plt.legend()
    plt.ylim(0, 1)
    for i, (sim, theo) in enumerate(zip(simulated_rates, theoretical_rates)):
        plt.text(i - width/2, sim + 0.02, f'{sim:.1%}', ha='center', va='bottom')
        plt.text(i + width/2, theo + 0.02, f'{theo:.1%}', ha='center', va='bottom')
    plt.grid(True, alpha=0.3)
    plt.show()

def interactive_game():
    print(f"\n{'='*60}")
    print("INTERACTIVE MONTY HALL GAME")
    print("="*60)
    game = MontyHallGame()
    game.prize_door = random.choice([1, 2, 3])
    print("Welcome to the Monty Hall Game!")
    print("There are 3 doors. Behind one is a prize!")
    try:
        player_input = int(input("Choose a door (1, 2, or 3): "))
        if player_input not in [1, 2, 3]:
            print("Invalid choice, selecting door 1 for you.")
            player_input = 1
    except:
        print("Invalid input, selecting door 1 for you.")
        player_input = 1
    game.player_choice = player_input
    game.host_action()
    print(f"\nYou chose door {game.player_choice}")
    print(f"I (the host) will now open door {game.host_opens}, which has no prize.")
    print(f"You can now switch to door {game.remaining_door} or stay with door {game.player_choice}")
    try:
        switch_input = input("Do you want to switch? (y/n): ").lower()
        switch_decision = switch_input.startswith('y')
    except:
        switch_decision = False
    final_choice = game.remaining_door if switch_decision else game.player_choice
    won = final_choice == game.prize_door
    print(f"\nThe prize was behind door {game.prize_door}")
    print(f"You {'switched' if switch_decision else 'stayed'} and chose door {final_choice}")
    print(f"Result: You {'WON!' if won else 'LOST!'}")
    print(f"Strategy used: {'Switch' if switch_decision else 'Stay'}")

def main():
    print("MONTY HALL PROBLEM SIMULATION PROGRAM")
    print("="*60)
    demonstrate_single_game()
    simulator = MontyHallSimulator()
    simulator.run_simulation(10000)
    stay_rate, switch_rate = simulator.analyze_results()
    analyzer = MontyHallAnalyzer(simulator)
    analyzer.detailed_analysis()
    analyzer.probability_explanation()
    print(f"\n{'='*60}")
    print("CONVERGENCE ANALYSIS")
    print("="*60)
    game_numbers, stay_rates, switch_rates = simulator.get_convergence_data(10000)
    plot_convergence(game_numbers, stay_rates, switch_rates)
    plot_results_comparison(stay_rate, switch_rate)
    interactive_game()
    print(f"\n{'='*60}")
    print("SIMULATION COMPLETE")
    print("="*60)
    print("Key Takeaway: Always switch doors in the Monty Hall Problem!")

if __name__ == "_main_":
    main()
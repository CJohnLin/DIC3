from flask import Flask, render_template
import numpy as np
import matplotlib
matplotlib.use('Agg') # required for headless plotting
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    # True means
    means = {'A': 0.8, 'B': 0.7, 'C': 0.5}
    
    # Phase 1: Exploration (A/B testing)
    explore_budget = 2000
    pulls_per_arm = explore_budget // 2
    
    # Simulate A and B
    rewards_A = np.random.binomial(1, means['A'], pulls_per_arm)
    rewards_B = np.random.binomial(1, means['B'], pulls_per_arm)
    
    est_A = np.mean(rewards_A)
    est_B = np.mean(rewards_B)
    
    # Determine winner
    winner = 'A' if est_A > est_B else 'B'
    
    # Analytic parts
    expected_explore_reward = pulls_per_arm * means['A'] + pulls_per_arm * means['B']
    expected_exploit_reward = 8000 * means[winner]
    total_expected_reward = expected_explore_reward + expected_exploit_reward
    optimal_reward = 10000 * means['A']
    regret = optimal_reward - total_expected_reward
    
    ans1 = f"Analytical estimation: 1000 pulls of A (mean 0.8) + 1000 pulls of B (mean 0.7) = {pulls_per_arm * means['A']:.0f} + {pulls_per_arm * means['B']:.0f} = {expected_explore_reward:.0f}."
    ans2 = f"Simulation results: Estimated mean for A = {est_A:.3f}, B = {est_B:.3f}. Bandit {winner} is selected for exploitation."
    ans3 = f"Allocating remaining $8,000 to Bandit {winner}. Expected reward for exploitation = 8000 * {means[winner]:.1f} = {expected_exploit_reward:.0f}. Total expected reward = {expected_explore_reward:.0f} + {expected_exploit_reward:.0f} = {total_expected_reward:.0f}."
    ans4 = f"Optimal strategy is to pull Bandit A 10000 times. Optimal reward = 10000 * 0.8 = {optimal_reward:.0f}."
    ans5 = f"Regret = Optimal Reward - Total Expected Reward = {optimal_reward:.0f} - {total_expected_reward:.0f} = {regret:.0f}."
    ans6 = "Bandit algorithms (like UCB or Thompson Sampling) dynamically adapt to the observed rewards, balancing exploration and exploitation throughout the entire 10000 budget. They avoid spending as much exactly on suboptimal arms and would even test Bandit C briefly, ultimately converging on Bandit A much quicker and yielding lower regret compared to a rigid A/B test."

    # Plot 1: Cumulative Average Return
    all_rewards = []
    # Interleave to simulate parallel A/B test
    for i in range(pulls_per_arm):
        all_rewards.append(rewards_A[i])
        all_rewards.append(rewards_B[i])
        
    # Exploitation phase
    rewards_exploit = np.random.binomial(1, means[winner], 8000)
    all_rewards.extend(rewards_exploit)
    
    cumulative_rewards = np.cumsum(all_rewards)
    avg_returns = cumulative_rewards / np.arange(1, 10001)
    
    plt.figure(figsize=(10, 5))
    plt.plot(np.arange(1, 10001), avg_returns, label='Average Return per Pull', color='#1f77b4')
    plt.axvline(x=2000, color='orange', linestyle='--', label='End of A/B Test (Exploration)')
    plt.axhline(y=0.8, color='red', linestyle=':', label='Optimal Mean (Bandit A)')
    plt.axhspan(0, 0, color='white') # just to adjust ylim if needed, or rely on auto
    plt.ylim(0.5, 0.9)
    plt.title('A/B Test Simulation: Cumulative Average Return vs Dollars Spent')
    plt.xlabel('Dollars Spent (Total Budget)')
    plt.ylabel('Average Return per Dollar')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plot1 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    # Plot 2: True vs Estimated Means
    plt.figure(figsize=(8, 5))
    bandits = ['Bandit A', 'Bandit B', 'Bandit C']
    true_m = [0.8, 0.7, 0.5]
    est_m = [est_A, est_B, 0.0]
    
    x = np.arange(len(bandits))
    width = 0.35
    
    plt.bar(x - width/2, true_m, width, label='True Mean', color='#7eb0d5')
    plt.bar(x + width/2, est_m, width, label='Estimated Mean (after exploration)', color='#fdcce5')
    
    for i, v in enumerate(true_m):
        plt.text(x[i] - width/2, v + 0.02, str(v), ha='center', va='bottom', fontsize=9)
    for i, v in enumerate(est_m):
        if i < 2:
            plt.text(x[i] + width/2, v + 0.02, f"{v:.3f}", ha='center', va='bottom', fontsize=9)
            
    plt.ylabel('Mean Return')
    plt.title('True vs. Estimated Bandit Means (After Exploration Phase)')
    plt.xticks(x, bandits)
    plt.ylim(0, 1.0)
    plt.legend()
    
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', bbox_inches='tight')
    buf2.seek(0)
    plot2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    plt.close()

    return render_template('index.html', 
                           ans1=ans1, ans2=ans2, ans3=ans3, ans4=ans4, ans5=ans5, ans6=ans6,
                           plot1=plot1, plot2=plot2)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

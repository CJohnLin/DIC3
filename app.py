from flask import Flask, render_template, request, jsonify
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json or {}
    mean_A = float(data.get('mean_A', 0.8))
    mean_B = float(data.get('mean_B', 0.7))
    mean_C = float(data.get('mean_C', 0.5))
    explore_budget = int(data.get('explore_budget', 2000))
    total_budget = int(data.get('total_budget', 10000))
    
    means = {'A': mean_A, 'B': mean_B, 'C': mean_C}
    pulls_per_arm = explore_budget // 3
    
    # Exploration phase (A/B/C testing)
    rewards_A = np.random.binomial(1, means['A'], pulls_per_arm)
    rewards_B = np.random.binomial(1, means['B'], pulls_per_arm)
    rewards_C = np.random.binomial(1, means['C'], pulls_per_arm)
    
    est_A = float(np.mean(rewards_A))
    est_B = float(np.mean(rewards_B))
    est_C = float(np.mean(rewards_C))
    
    estimates = {'A': est_A, 'B': est_B, 'C': est_C}
    winner = max(estimates, key=estimates.get)
    
    remaining_budget = total_budget - (pulls_per_arm * 3)
    expected_explore_reward = pulls_per_arm * means['A'] + pulls_per_arm * means['B'] + pulls_per_arm * means['C']
    expected_exploit_reward = remaining_budget * means[winner]
    total_expected_reward = expected_explore_reward + expected_exploit_reward
    optimal_reward = total_budget * max(means.values())
    regret = optimal_reward - total_expected_reward
    
    all_rewards = []
    # Interleave parallel exploration
    for i in range(pulls_per_arm):
        all_rewards.append(int(rewards_A[i]))
        all_rewards.append(int(rewards_B[i]))
        all_rewards.append(int(rewards_C[i]))
        
    # Exploit phase
    if remaining_budget > 0:
        rewards_exploit = np.random.binomial(1, means[winner], remaining_budget)
        all_rewards.extend([int(r) for r in rewards_exploit])
    
    cumulative_rewards = np.cumsum(all_rewards)
    
    # Subsample data points for smooth and performant charting in JS
    step = max(1, total_budget // 200)
    indices = list(range(1, len(cumulative_rewards) + 1, step))
    explore_len = pulls_per_arm * 3
    if explore_len not in indices and explore_len <= len(cumulative_rewards):
        indices.append(explore_len)
    indices.sort()
    
    avg_returns = []
    for idx in indices:
        avg_returns.append(float(cumulative_rewards[idx-1] / idx))
        
    # Generate answers text
    ans1 = f"Analytical estimation: {pulls_per_arm} pulls each of A, B, and C = {pulls_per_arm * means['A']:.0f} + {pulls_per_arm * means['B']:.0f} + {pulls_per_arm * means['C']:.0f} = {expected_explore_reward:.0f}."
    ans2 = f"Simulation results: Estimated mean for A = {est_A:.3f}, B = {est_B:.3f}, C = {est_C:.3f}. Bandit {winner} is selected for exploitation."
    ans3 = f"Allocating remaining ${remaining_budget} to Bandit {winner}. Expected reward = {remaining_budget} * {means[winner]:.1f} = {expected_exploit_reward:.0f}. Total = {expected_explore_reward:.0f} + {expected_exploit_reward:.0f} = {total_expected_reward:.0f}."
    ans4 = f"Optimal strategy is to pull the best bandit {total_budget} times. Optimal reward = {total_budget} * {max(means.values()):.2f} = {optimal_reward:.0f}."
    ans5 = f"Regret = Optimal Reward - Total Expected Reward = {optimal_reward:.0f} - {total_expected_reward:.0f} = {regret:.0f}."
    ans6 = f"Bandit algorithms (like UCB or Thompson Sampling) dynamically adapt during exploration. Instead of a rigid A/B/C test that wastes {pulls_per_arm} pulls on the worst option, they constantly shift focus to the most promising arm, leading to much lower regret."

    return jsonify({
        'ans1': ans1, 'ans2': ans2, 'ans3': ans3, 'ans4': ans4, 'ans5': ans5, 'ans6': ans6,
        'true_means': [means['A'], means['B'], means['C']],
        'est_means': [est_A, est_B, est_C],
        'chart_x': indices,
        'chart_y': avg_returns,
        'winner': winner,
        'optimal_mean': max(means.values()),
        'explore_budget': explore_budget
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

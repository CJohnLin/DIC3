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
    pulls_per_arm = explore_budget // 2
    
    # Exploration phase (A/B testing)
    rewards_A = np.random.binomial(1, means['A'], pulls_per_arm)
    rewards_B = np.random.binomial(1, means['B'], pulls_per_arm)
    
    est_A = float(np.mean(rewards_A))
    est_B = float(np.mean(rewards_B))
    
    winner = 'A' if est_A > est_B else 'B'
    
    remaining_budget = total_budget - explore_budget
    expected_explore_reward = pulls_per_arm * means['A'] + pulls_per_arm * means['B']
    expected_exploit_reward = remaining_budget * means[winner]
    total_expected_reward = expected_explore_reward + expected_exploit_reward
    optimal_reward = total_budget * max(means.values())
    regret = optimal_reward - total_expected_reward
    
    all_rewards = []
    # Interleave parallel A/B
    for i in range(pulls_per_arm):
        all_rewards.append(int(rewards_A[i]))
        all_rewards.append(int(rewards_B[i]))
        
    # Exploit phase
    if remaining_budget > 0:
        rewards_exploit = np.random.binomial(1, means[winner], remaining_budget)
        all_rewards.extend([int(r) for r in rewards_exploit])
    
    cumulative_rewards = np.cumsum(all_rewards)
    
    # Subsample data points for smooth and performant charting in JS
    step = max(1, total_budget // 200)
    indices = list(range(1, len(cumulative_rewards) + 1, step))
    if explore_budget not in indices and explore_budget <= len(cumulative_rewards):
        indices.append(explore_budget)
    indices.sort()
    
    avg_returns = []
    for idx in indices:
        avg_returns.append(float(cumulative_rewards[idx-1] / idx))
        
    # Generate answers text
    ans1 = f"Analytical estimation: {pulls_per_arm} pulls of A (mean {means['A']:.2f}) + {pulls_per_arm} pulls of B (mean {means['B']:.2f}) = {pulls_per_arm * means['A']:.0f} + {pulls_per_arm * means['B']:.0f} = {expected_explore_reward:.0f}."
    ans2 = f"Simulation results: Estimated mean for A = {est_A:.3f}, B = {est_B:.3f}. Bandit {winner} is selected for exploitation."
    ans3 = f"Allocating remaining ${remaining_budget} to Bandit {winner}. Expected reward = {remaining_budget} * {means[winner]:.1f} = {expected_exploit_reward:.0f}. Total = {expected_explore_reward:.0f} + {expected_exploit_reward:.0f} = {total_expected_reward:.0f}."
    ans4 = f"Optimal strategy is to pull the best bandit {total_budget} times. Optimal reward = {total_budget} * {max(means.values()):.2f} = {optimal_reward:.0f}."
    ans5 = f"Regret = Optimal Reward - Total Expected Reward = {optimal_reward:.0f} - {total_expected_reward:.0f} = {regret:.0f}."
    ans6 = f"Bandit algorithms dynamically adapt, avoiding spending exactly {pulls_per_arm} on suboptimal arms and would even test Bandit C briefly, yielding lower regret compared to this rigid A/B test."

    return jsonify({
        'ans1': ans1, 'ans2': ans2, 'ans3': ans3, 'ans4': ans4, 'ans5': ans5, 'ans6': ans6,
        'true_means': [means['A'], means['B'], means['C']],
        'est_means': [est_A, est_B, 0.0], # C is unused in A/B test
        'chart_x': indices,
        'chart_y': avg_returns,
        'winner': winner,
        'optimal_mean': max(means.values()),
        'explore_budget': explore_budget
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

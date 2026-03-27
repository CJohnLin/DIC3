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
    winner = max(estimates.keys(), key=lambda k: estimates[k])
    
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
        
    # --- New: Convergence of each bandit independently for 3333 pulls ---
    convergence_pulls = total_budget // 3
    conv_A = np.cumsum(np.random.binomial(1, means['A'], convergence_pulls)) / np.arange(1, convergence_pulls + 1)
    conv_B = np.cumsum(np.random.binomial(1, means['B'], convergence_pulls)) / np.arange(1, convergence_pulls + 1)
    conv_C = np.cumsum(np.random.binomial(1, means['C'], convergence_pulls)) / np.arange(1, convergence_pulls + 1)
    
    c_step = max(1, convergence_pulls // 150)
    c_indices = list(range(1, convergence_pulls + 1, c_step))
    if convergence_pulls not in c_indices:
        c_indices.append(convergence_pulls)
    
    cv_A = [float(conv_A[i-1]) for i in c_indices]
    cv_B = [float(conv_B[i-1]) for i in c_indices]
    cv_C = [float(conv_C[i-1]) for i in c_indices]
    # -------------------------------------------------------------------

    # Generate answers text (Traditional Chinese)
    ans1 = f"理論估算：A、B、C 各試拉 {pulls_per_arm} 次 = {pulls_per_arm * means['A']:.0f} + {pulls_per_arm * means['B']:.0f} + {pulls_per_arm * means['C']:.0f} = 第 1 階段預期獎勵 {expected_explore_reward:.0f}。"
    ans2 = f"模擬結果：預估勝率 A = {est_A:.3f}, B = {est_B:.3f}, C = {est_C:.3f}。因此選擇主要對老虎機 {winner} 進行利用 (Exploitation)。"
    ans3 = f"將剩餘的 ${remaining_budget} 預算全數投入老虎機 {winner}。第 2 階段預期獎勵 = {remaining_budget} * {means[winner]:.1f} = {expected_exploit_reward:.0f}。總預期獎勵 = {expected_explore_reward:.0f} + {expected_exploit_reward:.0f} = {total_expected_reward:.0f}。"
    ans4 = f"理論上的最佳完美策略為：將所有 {total_budget} 次預算全部投入最佳的老虎機。最佳預期獎勵 = {total_budget} * {max(means.values()):.2f} = {optimal_reward:.0f}。"
    ans5 = f"此策略的遺憾值 (Regret) = 最佳預期獎勵 - 總預期獎勵 = {optimal_reward:.0f} - {total_expected_reward:.0f} = {regret:.0f}。"
    ans6 = f"多臂老虎機演算法 (如 UCB 或 Thompson Sampling) 會在探索時動態調整拉桿比例。相較於硬性盲測的 A/B/C 測試會白白浪費 {pulls_per_arm} 次在最差的選項上，動態演算法能更快將資源集中在勝率最高的老虎機，進而大幅降低系統的遺憾值。"

    return jsonify({
        'ans1': ans1, 'ans2': ans2, 'ans3': ans3, 'ans4': ans4, 'ans5': ans5, 'ans6': ans6,
        'true_means': [means['A'], means['B'], means['C']],
        'est_means': [est_A, est_B, est_C],
        'chart_x': indices,
        'chart_y': avg_returns,
        'conv_x': c_indices,
        'conv_A': cv_A,
        'conv_B': cv_B,
        'conv_C': cv_C,
        'winner': winner,
        'optimal_mean': max(means.values()),
        'explore_budget': explore_budget
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

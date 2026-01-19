import { useEffect, useMemo, useRef, useState } from "react";
import confetti from "canvas-confetti";
import {
  Bar,
  BarChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_BASE || "";

const formatMoney = (value) => `$${value.toFixed(2)}`;

const postJson = async (url, body) => {
  const response = await fetch(`${API_BASE}${url}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Something went wrong.");
  }

  return response.json();
};

const fetchJson = async (url) => {
  const response = await fetch(`${API_BASE}${url}`);
  if (!response.ok) {
    throw new Error("Unable to fetch data.");
  }
  return response.json();
};

export default function App() {
  const [user, setUser] = useState(null);
  const [goals, setGoals] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [activeTab, setActiveTab] = useState("active");
  const [error, setError] = useState("");
  const [newGoal, setNewGoal] = useState({
    title: "",
    target_amount: "",
    emoji: "\ud83d\udc96",
    image_url: "",
  });
  const [fundInputs, setFundInputs] = useState({});
  const [moveInputs, setMoveInputs] = useState({});
  const [closeTargets, setCloseTargets] = useState({});
  const celebratedGoals = useRef(new Set());
  const hasLoaded = useRef(false);

  const activeGoals = useMemo(
    () => goals.filter((goal) => goal.status === "active"),
    [goals]
  );
  const archivedGoals = useMemo(
    () => goals.filter((goal) => goal.status !== "active"),
    [goals]
  );

  const refreshAll = async () => {
    try {
      setError("");
      const [userData, goalsData, transactionsData, summaryData] =
        await Promise.all([
          fetchJson("/api/user"),
          fetchJson("/api/goals"),
          fetchJson("/api/transactions"),
          fetchJson("/api/summary"),
        ]);
      setUser(userData);
      setGoals(goalsData);
      setTransactions(transactionsData);
      setSummary(summaryData);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    refreshAll();
  }, []);

  useEffect(() => {
    if (!goals.length) return;

    if (!hasLoaded.current) {
      goals.forEach((goal) => {
        if (goal.saved_amount >= goal.target_amount) {
          celebratedGoals.current.add(goal.id);
        }
      });
      hasLoaded.current = true;
      return;
    }

    goals.forEach((goal) => {
      if (
        goal.saved_amount >= goal.target_amount &&
        !celebratedGoals.current.has(goal.id)
      ) {
        celebratedGoals.current.add(goal.id);
        confetti({
          particleCount: 120,
          spread: 70,
          origin: { y: 0.6 },
        });
      }
    });
  }, [goals]);

  const handleAddGoal = async (event) => {
    event.preventDefault();
    try {
      await postJson("/api/goals", {
        ...newGoal,
        target_amount: Number(newGoal.target_amount),
      });
      setNewGoal({ title: "", target_amount: "", emoji: "\ud83d\udc96", image_url: "" });
      refreshAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddFunds = async (goalId) => {
    const amount = Number(fundInputs[goalId] || 0);
    if (!amount) return;
    try {
      await postJson(`/api/goals/${goalId}/add-funds`, { amount });
      setFundInputs((prev) => ({ ...prev, [goalId]: "" }));
      refreshAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleMoveFunds = async (goalId) => {
    const input = moveInputs[goalId] || { amount: "", target_goal_id: "" };
    const amount = Number(input.amount || 0);
    const targetGoalId = Number(input.target_goal_id || 0);
    if (!amount || !targetGoalId) return;
    try {
      await postJson(`/api/goals/${goalId}/move-funds`, {
        amount,
        target_goal_id: targetGoalId,
      });
      setMoveInputs((prev) => ({ ...prev, [goalId]: { amount: "", target_goal_id: "" } }));
      refreshAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCloseGoal = async (goalId) => {
    const targetGoalId = Number(closeTargets[goalId] || 0);
    if (!targetGoalId) return;
    try {
      await postJson(`/api/goals/${goalId}/close`, {
        target_goal_id: targetGoalId,
      });
      setCloseTargets((prev) => ({ ...prev, [goalId]: "" }));
      refreshAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCompleteGoal = async (goalId) => {
    try {
      await postJson(`/api/goals/${goalId}/complete`, {});
      refreshAll();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-badge">\ud83c\udf1f</div>
          <div>
            <p className="logo-title">Savings Squad</p>
            <p className="logo-sub">Girl power money goals</p>
          </div>
        </div>
        <div className="balance-card">
          <p>Total Savings</p>
          <h2>{summary ? formatMoney(summary.total_saved) : "$0.00"}</h2>
        </div>
        <nav className="menu">
          <button type="button" className="menu-item active">
            Dashboard
          </button>
          <button type="button" className="menu-item">
            Goals
          </button>
          <button type="button" className="menu-item">
            Activity
          </button>
        </nav>
        <div className="sidebar-tip">
          <p>\ud83d\udca1 Tip of the day</p>
          <span>Small saves add up fast. Try the $1-a-day challenge!</span>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <h1>Hey {user ? user.name : "friend"}!</h1>
            <p>Your money goals are looking bright today.</p>
          </div>
          <div className="header-chip">\ud83d\udeb4\u200d\u2640\ufe0f Keep going!</div>
        </header>

        {error ? <div className="error">{error}</div> : null}

        <section className="dashboard-grid">
          <div className="card highlight">
            <h3>Closest Goal</h3>
            {summary?.closest_goal ? (
              <>
                <div className="goal-row">
                  <span className="goal-emoji">{summary.closest_goal.emoji}</span>
                  <div>
                    <h4>{summary.closest_goal.title}</h4>
                    <p>
                      {formatMoney(summary.closest_goal.saved_amount)} / {formatMoney(
                        summary.closest_goal.target_amount
                      )}
                    </p>
                  </div>
                </div>
                <div className="progress">
                  <div
                    className="progress-bar"
                    style={{
                      width: `${Math.min(
                        100,
                        (summary.closest_goal.saved_amount /
                          summary.closest_goal.target_amount) *
                          100
                      )}%`,
                    }}
                  />
                </div>
              </>
            ) : (
              <p>No goals yet. Add one to get started!</p>
            )}
          </div>

          <div className="card">
            <h3>Monthly Activity</h3>
            <div className="chart-wrap">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={summary?.monthly_activity || []}>
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="in" fill="#ff7bd5" name="Money in" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="out" fill="#ffa84f" name="Money out" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="section-header">
            <div>
              <h2>My Goals</h2>
              <p>Track progress, move funds, and celebrate wins.</p>
            </div>
            <div className="tab-group">
              <button
                type="button"
                className={activeTab === "active" ? "tab active" : "tab"}
                onClick={() => setActiveTab("active")}
              >
                Active
              </button>
              <button
                type="button"
                className={activeTab === "archived" ? "tab active" : "tab"}
                onClick={() => setActiveTab("archived")}
              >
                Archived
              </button>
            </div>
          </div>

          <form className="goal-form" onSubmit={handleAddGoal}>
            <input
              type="text"
              placeholder="Goal name"
              value={newGoal.title}
              onChange={(event) =>
                setNewGoal((prev) => ({ ...prev, title: event.target.value }))
              }
              required
            />
            <input
              type="number"
              min="1"
              placeholder="Target amount"
              value={newGoal.target_amount}
              onChange={(event) =>
                setNewGoal((prev) => ({ ...prev, target_amount: event.target.value }))
              }
              required
            />
            <input
              type="text"
              placeholder="Emoji"
              value={newGoal.emoji}
              onChange={(event) =>
                setNewGoal((prev) => ({ ...prev, emoji: event.target.value }))
              }
            />
            <input
              type="url"
              placeholder="Image URL (optional)"
              value={newGoal.image_url}
              onChange={(event) =>
                setNewGoal((prev) => ({ ...prev, image_url: event.target.value }))
              }
            />
            <button type="submit" className="primary">
              Add goal
            </button>
          </form>

          <div className="goal-grid">
            {(activeTab === "active" ? activeGoals : archivedGoals).map((goal) => (
              <div key={goal.id} className="goal-card">
                <div className="goal-header">
                  <div className="goal-avatar">
                    {goal.image_url ? (
                      <img src={goal.image_url} alt={goal.title} />
                    ) : (
                      <span>{goal.emoji}</span>
                    )}
                  </div>
                  <div>
                    <h4>{goal.title}</h4>
                    <p>
                      {formatMoney(goal.saved_amount)} / {formatMoney(goal.target_amount)}
                    </p>
                  </div>
                </div>

                <div className="progress">
                  <div
                    className="progress-bar"
                    style={{
                      width: `${Math.min(
                        100,
                        (goal.saved_amount / goal.target_amount) * 100
                      )}%`,
                    }}
                  />
                </div>

                {activeTab === "active" ? (
                  <div className="goal-actions">
                    <div className="action-row">
                      <input
                        type="number"
                        min="1"
                        placeholder="Add funds"
                        value={fundInputs[goal.id] || ""}
                        onChange={(event) =>
                          setFundInputs((prev) => ({
                            ...prev,
                            [goal.id]: event.target.value,
                          }))
                        }
                      />
                      <button type="button" onClick={() => handleAddFunds(goal.id)}>
                        Add
                      </button>
                    </div>

                    <div className="action-row">
                      <input
                        type="number"
                        min="1"
                        placeholder="Move amount"
                        value={moveInputs[goal.id]?.amount || ""}
                        onChange={(event) =>
                          setMoveInputs((prev) => ({
                            ...prev,
                            [goal.id]: {
                              amount: event.target.value,
                              target_goal_id: prev[goal.id]?.target_goal_id || "",
                            },
                          }))
                        }
                      />
                      <select
                        value={moveInputs[goal.id]?.target_goal_id || ""}
                        onChange={(event) =>
                          setMoveInputs((prev) => ({
                            ...prev,
                            [goal.id]: {
                              amount: prev[goal.id]?.amount || "",
                              target_goal_id: event.target.value,
                            },
                          }))
                        }
                      >
                        <option value="">Move to...</option>
                        {activeGoals
                          .filter((item) => item.id !== goal.id)
                          .map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.title}
                            </option>
                          ))}
                      </select>
                      <button type="button" onClick={() => handleMoveFunds(goal.id)}>
                        Move
                      </button>
                    </div>

                    <div className="action-row">
                      <select
                        value={closeTargets[goal.id] || ""}
                        onChange={(event) =>
                          setCloseTargets((prev) => ({
                            ...prev,
                            [goal.id]: event.target.value,
                          }))
                        }
                      >
                        <option value="">Close & move to...</option>
                        {activeGoals
                          .filter((item) => item.id !== goal.id)
                          .map((item) => (
                            <option key={item.id} value={item.id}>
                              {item.title}
                            </option>
                          ))}
                      </select>
                      <button type="button" onClick={() => handleCloseGoal(goal.id)}>
                        Close goal
                      </button>
                    </div>

                    {goal.saved_amount >= goal.target_amount ? (
                      <button
                        type="button"
                        className="primary"
                        onClick={() => handleCompleteGoal(goal.id)}
                      >
                        Mark as completed
                      </button>
                    ) : null}
                  </div>
                ) : (
                  <div className="goal-archive">
                    <span>Status: {goal.status}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      </main>

      <aside className="activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {transactions.map((transaction) => (
            <div key={transaction.id} className="activity-item">
              <div>
                <p className="activity-type">{transaction.type.replace("_", " ")}</p>
                <span className="activity-note">{transaction.note || "Activity"}</span>
              </div>
              <div className="activity-amount">
                {transaction.type === "transfer_out" || transaction.type === "complete"
                  ? "-"
                  : "+"}
                {formatMoney(transaction.amount)}
              </div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}

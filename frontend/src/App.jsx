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

const formatMoney = (value) =>
  `${new Intl.NumberFormat("da-DK", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)} kr.`;

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
  const [activeView, setActiveView] = useState("dashboard");
  const [error, setError] = useState("");
  const [activeTip, setActiveTip] = useState(0);
  const [newGoal, setNewGoal] = useState({
    title: "",
    target_amount: "",
    emoji: "💖",
    image_url: "",
  });
  const [fundInputs, setFundInputs] = useState({});
  const [moveInputs, setMoveInputs] = useState({});
  const [closeTargets, setCloseTargets] = useState({});
  const [activeModal, setActiveModal] = useState(null);
  const celebratedGoals = useRef(new Set());
  const hasLoaded = useRef(false);
  const tips = [
    "Make it social. A quick chat about priorities helps you pick one goal to fund this week.",
    "Name the why. Goals with a clear reason are easier to protect in your budget.",
    "Try a weekly micro-deposit. Small, steady moves keep priorities on track.",
  ];

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
      setNewGoal({ title: "", target_amount: "", emoji: "💖", image_url: "" });
      refreshAll();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddFunds = async (goalId) => {
    const amount = Number(fundInputs[goalId] || 0);
    if (!amount) return false;
    try {
      await postJson(`/api/goals/${goalId}/add-funds`, { amount });
      setFundInputs((prev) => ({ ...prev, [goalId]: "" }));
      refreshAll();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  const handleMoveFunds = async (goalId) => {
    const input = moveInputs[goalId] || { amount: "", target_goal_id: "" };
    const amount = Number(input.amount || 0);
    const targetGoalId = Number(input.target_goal_id || 0);
    if (!amount || !targetGoalId) return false;
    try {
      await postJson(`/api/goals/${goalId}/move-funds`, {
        amount,
        target_goal_id: targetGoalId,
      });
      setMoveInputs((prev) => ({ ...prev, [goalId]: { amount: "", target_goal_id: "" } }));
      refreshAll();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    }
  };

  const handleCloseGoal = async (goalId) => {
    const targetGoalId = Number(closeTargets[goalId] || 0);
    if (!targetGoalId) return false;
    try {
      await postJson(`/api/goals/${goalId}/close`, {
        target_goal_id: targetGoalId,
      });
      setCloseTargets((prev) => ({ ...prev, [goalId]: "" }));
      refreshAll();
      return true;
    } catch (err) {
      setError(err.message);
      return false;
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
          <div className="logo-badge">🌟</div>
          <div>
            <p className="logo-title">Priority Bank</p>
            <p className="logo-sub">Make every kr. match your priorities</p>
          </div>
        </div>
        <div className="balance-card">
          <p>Total Priority Savings</p>
          <h2>{summary ? formatMoney(summary.total_saved) : "kr. 0.00"}</h2>
        </div>
        <nav className="menu">
          <button
            type="button"
            className={activeView === "dashboard" ? "menu-item active" : "menu-item"}
            onClick={() => setActiveView("dashboard")}
          >
            Dashboard
          </button>
          <button
            type="button"
            className={activeView === "goals" ? "menu-item active" : "menu-item"}
            onClick={() => setActiveView("goals")}
          >
            Goals
          </button>
        </nav>
        <div className="sidebar-tip">
          <p>💡 Tip of the day</p>
          <span>
            Talk money with friends—sharing priorities makes it easier to choose
            the goals you want to back on purpose.
          </span>
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <h1>Priority check-in, {user ? user.name : "friend"}.</h1>
            <p>Every kr. has a job—line up the ones that matter most.</p>
          </div>
          <div className="header-chip">🚴‍♀️ Priority mode</div>
        </header>

        {error ? <div className="error">{error}</div> : null}

        {activeView === "dashboard" ? (
          <section className="dashboard-grid">
            <div className="card highlight">
              <h3>Top Priority Goal</h3>
              {summary?.closest_goal ? (
                <>
                  <div className="goal-row">
                    <span className="goal-emoji">{summary.closest_goal.emoji}</span>
                    <div>
                      <h4>{summary.closest_goal.title}</h4>
                      <p>
                        {formatMoney(summary.closest_goal.saved_amount)} /{" "}
                        {formatMoney(summary.closest_goal.target_amount)}
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

            <div className="card cta-card">
              <h3>Feed your priorities ✨</h3>
              <p>
                Give your goals a cheer. Pick a priority and drop in a quick boost today.
              </p>
              <button
                type="button"
                className="cta-button"
                onClick={() => setActiveView("goals")}
              >
                Boost a goal
              </button>
            </div>

            <div className="card">
              <h3>Monthly Priority Pulse</h3>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={summary?.monthly_activity || []}>
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip
                      cursor={{ fill: "rgba(47, 25, 95, 0.08)" }}
                      contentStyle={{
                        background: "rgba(255, 255, 255, 0.92)",
                        borderRadius: "12px",
                        border: "1px solid #efe6ff",
                      }}
                    />
                    <Legend />
                    <Bar
                      dataKey="in"
                      fill="#ff7bd5"
                      name="Money in"
                      radius={[6, 6, 0, 0]}
                    />
                    <Bar
                      dataKey="out"
                      fill="#ffa84f"
                      name="Money out"
                      radius={[6, 6, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card tips-card">
              <h3>Tips & tricks</h3>
              <p>{tips[activeTip]}</p>
              <div className="tips-dots" role="tablist" aria-label="Tips carousel">
                {tips.map((tip, index) => (
                  <button
                    key={tip}
                    type="button"
                    className={index === activeTip ? "dot-button active" : "dot-button"}
                    onClick={() => setActiveTip(index)}
                    aria-label={`Show tip ${index + 1}`}
                    aria-pressed={index === activeTip}
                  />
                ))}
              </div>
            </div>
          </section>
        ) : (
          <section className="card">
            <div className="section-header">
              <div>
                <h2>Priority Goals</h2>
                <p>Choose what matters, fund it, and celebrate momentum.</p>
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
                        {formatMoney(goal.saved_amount)} /{" "}
                        {formatMoney(goal.target_amount)}
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
                      <div className="goal-actions-buttons">
                        <button
                          type="button"
                          className="action-button"
                          onClick={() => setActiveModal({ goalId: goal.id, type: "add" })}
                        >
                          Add funds
                        </button>
                        <button
                          type="button"
                          className="action-button"
                          onClick={() => setActiveModal({ goalId: goal.id, type: "move" })}
                        >
                          Move funds
                        </button>
                        <button
                          type="button"
                          className="action-button"
                          onClick={() =>
                            setActiveModal({ goalId: goal.id, type: "close" })
                          }
                        >
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
        )}

        {activeModal ? (
          <div
            className="modal-backdrop"
            onClick={() => setActiveModal(null)}
            role="presentation"
          >
            <div className="modal" onClick={(event) => event.stopPropagation()}>
              <div className="modal-header">
                <div>
                  <p className="modal-label">
                    {goals.find((goal) => goal.id === activeModal.goalId)?.title ||
                      "Goal"}
                  </p>
                  <h3>
                    {activeModal.type === "add"
                      ? "Add funds"
                      : activeModal.type === "move"
                      ? "Move funds"
                      : "Close goal"}
                  </h3>
                </div>
                <button
                  type="button"
                  className="modal-close"
                  onClick={() => setActiveModal(null)}
                >
                  Close
                </button>
              </div>

              {activeModal.type === "add" ? (
                <div className="modal-fields">
                  <input
                    type="number"
                    min="1"
                    placeholder="Amount"
                    value={fundInputs[activeModal.goalId] || ""}
                    onChange={(event) =>
                      setFundInputs((prev) => ({
                        ...prev,
                        [activeModal.goalId]: event.target.value,
                      }))
                    }
                  />
                  <button
                    type="button"
                    className="primary"
                    onClick={async () => {
                      const ok = await handleAddFunds(activeModal.goalId);
                      if (ok) setActiveModal(null);
                    }}
                  >
                    Confirm add
                  </button>
                </div>
              ) : null}

              {activeModal.type === "move" ? (
                <div className="modal-fields">
                  <input
                    type="number"
                    min="1"
                    placeholder="Amount"
                    value={moveInputs[activeModal.goalId]?.amount || ""}
                    onChange={(event) =>
                      setMoveInputs((prev) => ({
                        ...prev,
                        [activeModal.goalId]: {
                          amount: event.target.value,
                          target_goal_id:
                            prev[activeModal.goalId]?.target_goal_id || "",
                        },
                      }))
                    }
                  />
                  <select
                    value={moveInputs[activeModal.goalId]?.target_goal_id || ""}
                    onChange={(event) =>
                      setMoveInputs((prev) => ({
                        ...prev,
                        [activeModal.goalId]: {
                          amount: prev[activeModal.goalId]?.amount || "",
                          target_goal_id: event.target.value,
                        },
                      }))
                    }
                  >
                    <option value="">Move to...</option>
                    {activeGoals
                      .filter((item) => item.id !== activeModal.goalId)
                      .map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.title}
                        </option>
                      ))}
                  </select>
                  <button
                    type="button"
                    className="primary"
                    onClick={async () => {
                      const ok = await handleMoveFunds(activeModal.goalId);
                      if (ok) setActiveModal(null);
                    }}
                  >
                    Confirm move
                  </button>
                </div>
              ) : null}

              {activeModal.type === "close" ? (
                <div className="modal-fields">
                  <select
                    value={closeTargets[activeModal.goalId] || ""}
                    onChange={(event) =>
                      setCloseTargets((prev) => ({
                        ...prev,
                        [activeModal.goalId]: event.target.value,
                      }))
                    }
                  >
                    <option value="">Close & move to...</option>
                    {activeGoals
                      .filter((item) => item.id !== activeModal.goalId)
                      .map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.title}
                        </option>
                      ))}
                  </select>
                  <button
                    type="button"
                    className="primary"
                    onClick={async () => {
                      const ok = await handleCloseGoal(activeModal.goalId);
                      if (ok) setActiveModal(null);
                    }}
                  >
                    Confirm close
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        ) : null}
      </main>

      <aside className="activity">
        <h3>Priority Moves</h3>
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

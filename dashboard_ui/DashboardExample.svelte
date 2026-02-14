<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { connect, call, disconnect, isConnected } from "../dashboard_client";

  // Camera
  let cameraFrame = "";
  let cameraLoading = false;

  // Motor
  let wheelSpeed = { left: 0, right: 0 };
  let servoAngle = { id: 1, angle: 90 };

  // Status
  let plugins = [];
  let motorStatus = {};
  let reflexes = [];
  let memories = [];
  let rewardState = { total_reward: 0, reward_count: 0 };

  // UI state
  let connected = false;
  let operatorMode = false;

  onMount(async () => {
    try {
      await connect();
      connected = true;
      console.log("Connected to ANSE");
      
      // Load initial data once - event-driven updates instead of polling
      await refreshAllData();
    } catch (e) {
      console.error("Failed to connect:", e);
      connected = false;
    }
  });

  onDestroy(() => {
    disconnect();
  });

  async function refreshAllData() {
    if (!isConnected()) return;
    
    try {
      [plugins, motorStatus, reflexes, memories, rewardState] = await Promise.all([
        call("get_plugin_status"),
        call("get_motor_status"),
        call("get_reflex_status"),
        call("get_memory_entries", { limit: 10 }),
        call("get_reward_state")
      ]);
    } catch (e) {
      console.warn("Refresh failed:", e);
    }
  }

  async function loadCameraFrame() {
    cameraLoading = true;
    try {
      cameraFrame = await call("get_camera_frame", {}, { timeout: 5000 });
    } catch (e) {
      console.error("Failed to load camera frame:", e);
      cameraFrame = "";
    } finally {
      cameraLoading = false;
    }
  }

  async function setWheels() {
    if (!operatorMode) {
      alert("Switch to Operator Mode first!");
      return;
    }
    try {
      const result = await call("set_wheel_speed", {
        left_speed: wheelSpeed.left,
        right_speed: wheelSpeed.right
      });
      console.log(result);
    } catch (e) {
      alert("Failed to set wheel speed: " + e);
    }
  }

  async function setServo() {
    if (!operatorMode) {
      alert("Switch to Operator Mode first!");
      return;
    }
    try {
      const result = await call("set_servo_angle", {
        id: servoAngle.id,
        angle: servoAngle.angle
      });
      console.log(result);
    } catch (e) {
      alert("Failed to set servo angle: " + e);
    }
  }

  async function handleEmergencyStop() {
    if (!confirm("Are you SURE? This will stop all motors!")) return;
    try {
      const result = await call("emergency_stop");
      alert(result);
      await refreshAllData();
    } catch (e) {
      alert("Emergency stop failed: " + e);
    }
  }

  async function deleteMemory(id: string) {
    try {
      await call("delete_memory_entry", { memory_id: id });
      await refreshAllData();
    } catch (e) {
      alert("Failed to delete memory: " + e);
    }
  }

  async function clearAllMemory() {
    if (!confirm("Delete ALL memories?")) return;
    try {
      await call("clear_memory");
      await refreshAllData();
    } catch (e) {
      alert("Failed to clear memory: " + e);
    }
  }
</script>

<div class="dashboard">
  <header>
    <h1>🤖 ANSE Dashboard</h1>
    <div class="status">
      <span class={connected ? "connected" : "disconnected"}>
        {connected ? "🟢 Connected" : "🔴 Disconnected"}
      </span>
      <button on:click={() => operatorMode = !operatorMode} class="mode-toggle">
        {operatorMode ? "⚠️ OPERATOR MODE" : "👁️ View Mode"}
      </button>
    </div>
  </header>

  <main>
    <!-- Camera Feed -->
    <section class="panel">
      <h2>📷 Camera Feed</h2>
      <button on:click={loadCameraFrame} disabled={cameraLoading}>
        {cameraLoading ? "Loading..." : "Refresh Frame"}
      </button>
      {#if cameraFrame}
        <img src={`data:image/jpeg;base64,${cameraFrame}`} alt="Camera" />
      {:else}
        <div class="placeholder">No camera frame</div>
      {/if}
    </section>

    <!-- Motor Control -->
    <section class="panel">
      <h2>⚙️ Motor Control</h2>
      {#if operatorMode}
        <div class="control-group">
          <label>
            Left Wheel Speed:
            <input type="range" min="-100" max="100" bind:value={wheelSpeed.left} />
            <span>{wheelSpeed.left}</span>
          </label>
          <label>
            Right Wheel Speed:
            <input type="range" min="-100" max="100" bind:value={wheelSpeed.right} />
            <span>{wheelSpeed.right}</span>
          </label>
          <button on:click={setWheels} class="action-btn">Set Wheel Speed</button>
        </div>

        <div class="control-group">
          <label>
            Servo ID:
            <input type="number" min="0" max="10" bind:value={servoAngle.id} />
          </label>
          <label>
            Servo Angle (0-180):
            <input type="range" min="0" max="180" bind:value={servoAngle.angle} />
            <span>{servoAngle.angle}°</span>
          </label>
          <button on:click={setServo} class="action-btn">Set Servo Angle</button>
        </div>
      {:else}
        <p>Switch to Operator Mode to control motors</p>
      {/if}

      <button on:click={handleEmergencyStop} class="danger-btn">🛑 EMERGENCY STOP</button>

      <div class="status-display">
        <strong>Current Status:</strong>
        <pre>{JSON.stringify(motorStatus, null, 2)}</pre>
      </div>
    </section>

    <!-- Reflexes -->
    <section class="panel">
      <h2>⚡ Reflex Rules</h2>
      {#if reflexes.length > 0}
        <ul>
          {#each reflexes as reflex (reflex.id)}
            <li>
              <strong>{reflex.sensor_name}</strong> {reflex.comparison} {reflex.threshold}
              → {reflex.action_tool} (triggered: {reflex.triggered_count}x)
            </li>
          {/each}
        </ul>
      {:else}
        <p>No reflexes configured</p>
      {/if}
    </section>

    <!-- Memory -->
    <section class="panel">
      <h2>🧠 Long-Term Memory</h2>
      {#if memories.length > 0}
        <button on:click={clearAllMemory} class="danger-btn">🗑️ Clear All Memory</button>
        <ul>
          {#each memories as mem (mem.id)}
            <li>
              <span class="category">[{mem.category}]</span>
              <span>{mem.text}</span>
              <button on:click={() => deleteMemory(mem.id)} class="delete-btn">×</button>
            </li>
          {/each}
        </ul>
      {:else}
        <p>No memories stored</p>
      {/if}
    </section>

    <!-- Rewards -->
    <section class="panel">
      <h2>🏆 Reward System</h2>
      <div class="reward-display">
        <div class="metric">
          <span class="label">Total Reward:</span>
          <span class="value">{rewardState.total_reward}</span>
        </div>
        <div class="metric">
          <span class="label">Event Count:</span>
          <span class="value">{rewardState.reward_count}</span>
        </div>
        {#if rewardState.goal_achieved}
          <div class="metric success">🎯 Goal Achieved!</div>
        {/if}
      </div>
    </section>

    <!-- Plugins -->
    <section class="panel">
      <h2>🔌 Loaded Plugins</h2>
      {#if plugins.length > 0}
        <ul>
          {#each plugins as plugin (plugin.name)}
            <li><strong>{plugin.name}</strong> v{plugin.version}</li>
          {/each}
        </ul>
      {:else}
        <p>No plugins loaded</p>
      {/if}
    </section>
  </main>
</div>

<style>
  .dashboard {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    padding: 20px;
    background: #0f0f0f;
    color: #e0e0e0;
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    border-bottom: 2px solid #333;
    padding-bottom: 15px;
  }

  h1 {
    margin: 0;
    font-size: 28px;
  }

  .status {
    display: flex;
    gap: 15px;
    align-items: center;
  }

  .connected,
  .disconnected {
    font-weight: 600;
    padding: 5px 10px;
    border-radius: 4px;
  }

  .connected {
    background: #1a3a1a;
    color: #4ade80;
  }

  .disconnected {
    background: #3a1a1a;
    color: #f87171;
  }

  .mode-toggle {
    padding: 8px 16px;
    background: #1e40af;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
  }

  .mode-toggle:hover {
    background: #1e3a8a;
  }

  main {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
  }

  .panel {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 20px;
  }

  .panel h2 {
    margin: 0 0 15px 0;
    font-size: 18px;
    border-bottom: 1px solid #444;
    padding-bottom: 10px;
  }

  img {
    width: 100%;
    max-width: 100%;
    border-radius: 4px;
    margin-top: 10px;
  }

  .placeholder {
    background: #2a2a2a;
    border: 1px dashed #555;
    border-radius: 4px;
    padding: 40px;
    text-align: center;
    color: #888;
  }

  .control-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #333;
  }

  label {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  input[type="range"],
  input[type="number"],
  input[type="text"] {
    background: #2a2a2a;
    border: 1px solid #444;
    color: #e0e0e0;
    padding: 5px 8px;
    border-radius: 4px;
  }

  input[type="range"] {
    flex: 1;
  }

  button {
    padding: 8px 12px;
    background: #365314;
    color: #86efac;
    border: 1px solid #4ade80;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.2s;
  }

  button:hover:not(:disabled) {
    background: #4a7c1c;
    border-color: #86efac;
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .action-btn {
    background: #0f766e;
    color: #5eead4;
    border-color: #5eead4;
  }

  .action-btn:hover {
    background: #155e75;
  }

  .danger-btn {
    background: #7f1d1d;
    color: #fca5a5;
    border-color: #f87171;
    margin-top: 10px;
  }

  .danger-btn:hover {
    background: #991b1b;
    border-color: #fca5a5;
  }

  .delete-btn {
    padding: 2px 6px;
    background: #5f2c2c;
    color: #fca5a5;
    border-color: #f87171;
    font-size: 12px;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    padding: 10px;
    background: #2a2a2a;
    margin-bottom: 8px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 10px;
    justify-content: space-between;
  }

  .category {
    background: #1e40af;
    color: #93c5fd;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
  }

  .status-display,
  .reward-display {
    background: #2a2a2a;
    padding: 15px;
    border-radius: 4px;
    margin-top: 10px;
  }

  pre {
    margin: 0;
    max-height: 200px;
    overflow-y: auto;
  }

  .metric {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #444;
  }

  .metric.success {
    color: #4ade80;
    border: none;
    font-weight: 600;
  }

  .label {
    color: #aaa;
  }

  .value {
    font-weight: 600;
    color: #4ade80;
  }
</style>

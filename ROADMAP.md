# ANSE Development Roadmap

**Status:** Production-ready core (v0.1) → Enterprise-ready platform (v0.3)

This document outlines the prioritized feature roadmap, implementation timeline, and rationale for ANSE's evolution from a production-ready research engine to a fully featured operator-controllable platform.

---

## Feature Prioritization Matrix

| Feature | Impact | Effort | Risk | Priority | Timeline |
|---------|--------|--------|------|----------|----------|
| **Operator UI & Approval Console** | Very High | Medium (2–4 wks) | Low | **P1** | Weeks 1–3 |
| **Simulated Sensor Suite** | High | Medium (2–3 wks) | Low | **P1** | Weeks 1–4 |
| **Health Endpoint & Diagnostics** | High | Low (1–3 days) | Very Low | **P1** | Days 0–3 |
| **LLM Function-Calling (Prod)** | High | Medium (1–2 wks) | Medium | **P2** | Weeks 3–5 |
| **Multiagent Isolation & Quotas** | High | Medium (3–5 wks) | Medium | **P2** | Weeks 4–8 |
| **Operator Audit UI & Replay** | Medium | Medium (2–3 wks) | Low | **P2** | Weeks 4–6 |
| **CI/CD & Release Artifacts** | Medium | Low–Medium (1–2 wks) | Low | **P2** | Parallel |
| **Additional Tools** (browser, SDR, robot) | Medium | Variable | Medium | **P3** | Post-P1 |
| **Benchmark Suite & Sim→Real Tests** | Medium | Medium (2–4 wks) | Medium | **P3** | Post-P1 |

---

## Why This Prioritization

### 🎯 P1: Safety, Visibility, Developer Experience (Weeks 1–4)

#### **Operator UI & Approval Console** (Highest leverage)
- **Why first:** Single most impactful addition. Gives humans complete visibility and control.
- **Impact:**
  - Enables non-developer operators to monitor and approve agent actions.
  - Builds trust with stakeholders (compliance, safety teams).
  - Dramatically improves onboarding for enterprise users.
- **Risk:** Low (pure UI; no core engine changes).

#### **Simulated Sensor Suite** (Unlocks safe training)
- **Why:** Enables offline agent development without hardware risk.
- **Impact:**
  - Deterministic replay for debugging and research.
  - Reduces hardware dependency and enables CI testing.
  - Accelerates agent development iteration.
- **Risk:** Low (runs in isolation; no hardware dependency).

#### **Health Endpoint & Diagnostics** (Quick win)
- **Why:** Solves immediate pain points (flaky WebSocket connects, hidden failures).
- **Impact:**
  - Improves test reliability and CI robustness.
  - Enables automated monitoring and alerting.
  - Cuts debugging time significantly.
- **Risk:** Very low (diagnostic endpoints only).

---

### 🔄 P2: Production Hardening & Scale (Weeks 3–8)

#### **LLM Production Adapter**
- **Why:** Converts demo-ready framework into autonomous agent platform.
- **Focus:**
  - Full function-calling loop for OpenAI, Claude, local models.
  - Context management (keep last N events + tool result).
  - Cost and sensitivity hints in prompts.
  - Rate limiting and token budgets.
- **Prerequisites:** Operator UI (for approval gating).
- **Risk:** Medium (API keys, cost control, prompt injection).

#### **Multiagent Isolation & Quotas**
- **Why:** Essential before community adoption or multi-tenant deployment.
- **Features:**
  - Per-agent resource accounting (CPU, storage, rate limits).
  - Namespaced world model views.
  - Prevent one agent from starving others.
- **Risk:** Medium (concurrency, accounting accuracy).

#### **CI/CD & Release Artifacts**
- **Why:** Reproducible builds, contributor confidence, distribution.
- **Includes:**
  - GitHub Actions: test on Python 3.11+, Windows/macOS/Linux.
  - Publish releases to PyPI.
  - Docker image with hardware passthrough.
  - Pre-built binaries (optional).
- **Risk:** Low.

#### **Operator Audit UI & Replay Viewer**
- **Why:** Makes audit logs actionable and validates compliance.
- **Features:**
  - Timeline view of agent actions.
  - Filter by agent, tool, severity, timestamp.
  - Replay button: re-run a specific call in sim mode.
  - Export audit trail as PDF/JSON.
- **Risk:** Low (read-only views on audit store).

---

### 📈 P3: Extended Capabilities (Post-v0.2)

#### **Additional Tools**
- **Browser automation:** `open_url`, `click`, `extract_text` (for research agents).
- **Software-defined radio (SDR):** `list_sdr_devices`, `receive_signal`, `transmit_signal`.
- **Robot actuators:** `move_arm`, `grip`, `open_gripper` (for embodied RL).
- **Network tools:** `ping`, `http_get`, `dns_lookup` (with strict approval).
- **Filesystem:** `read_file`, `write_file`, `list_directory` (sandboxed).
- **When:** After multiagent quotas are stable (prevents resource abuse).

#### **Benchmark Suite & Sim→Real Transfer Tests**
- **Why:** Validates claims, attracts academic users, guides research direction.
- **Includes:**
  - Standard agent tasks (e.g., "find and photograph object X").
  - Sim-to-real transfer validation: train in sim, test on real hardware.
  - Latency and throughput benchmarks.
  - Agent learning curves and tool usage patterns.
- **Risk:** Medium (requires ground truth data and real hardware for validation).

---

## Concrete Implementation Plan

### Phase 1: Developer Experience (Weeks 1–3)

#### **Days 0–3: Health Endpoint & Diagnostics**

**What to build:**

```python
# New route: GET /health
{
  "status": "running",
  "uptime_seconds": 3600,
  "version": "0.1.0",
  "bound_port": 8765,
  "agent_count": 2,
  "tool_count": 6,
  "last_event_time": "2026-02-12T14:30:45Z",
  "recent_errors": [],
  "memory_mb": 48.5
}

# New script: python -m anse.diagnostics
# - Checks port availability
# - Tests WebSocket handshake
# - Verifies tool schema responses
# - Streams last 10 audit events
```

**File changes:**
- `anse/health.py` — New health check module.
- `anse/engine_core.py` — Add `/health` route.
- `anse/diagnostics.py` — Standalone diagnostic CLI.

**Testing:**
- `tests/test_health.py` — Unit tests for health endpoint.
- CI step: `pytest tests/test_health.py && python -m anse.diagnostics`.

---

#### **Weeks 1–3: Operator UI & Approval Console MVP**

**What to build:**

```
anse-ui/
├── backend/
│   ├── app.py                 # Flask/FastAPI server
│   ├── routes/
│   │   ├── auth.py            # Token validation
│   │   ├── agents.py          # List active agents
│   │   ├── audit.py           # Stream audit events
│   │   └── approval.py        # Issue approval tokens
│   └── models.py              # SQLite: agents, sessions, tokens
└── frontend/
    ├── index.html             # Simple HTML + vanilla JS (no build step)
    ├── dashboard.js           # Live agent list, event stream
    ├── approval.js            # Token issuance form
    └── styles.css             # Dark theme
```

**Core APIs:**

```python
# Backend
GET /api/health                              # Overall system status
GET /api/agents                              # List active agents + session info
GET /api/audit?limit=50&agent_id=...        # Paginated audit stream (JSONL)
POST /api/approve                            # Issue token
  {
    "scope": "camera|microphone|filesystem",
    "agent_id": "agent-001",
    "ttl_seconds": 300
  }
  Returns: {"token": "signed_token", "expires_at": "..."}

# Frontend
- Dashboard: live list of agents, tabs per agent
- Audit stream: filterable event log (tool, status, timestamp)
- Approval form: scope dropdown, agent selector, issue token
- Replay: re-run a call in sim mode
```

**Security:**
- Basic auth for dev (operator username/password).
- OAuth 2.0 or local account system for production.
- Signed tokens for approval (HMAC-SHA256).
- HTTPS enforced in production.

**Integration:**
- `anse/agent_bridge.py` — Add `/api/...` routes.
- `anse/audit.py` — Add `get_audit_stream(limit, filters)`.
- `anse/tool_registry.py` — Check approval token before calling sensitive tools.

---

#### **Weeks 1–4: Simulated Sensor Suite**

**What to build:**

```python
# anse/tools/simulated.py

async def simulate_camera(width: int = 640, height: int = 480, seed: int = 0) -> dict:
    """Return a deterministic procedural frame."""
    # Generate a seeded frame (checkerboard, gradients, patterns)
    frame = generate_procedural_frame(width, height, seed)
    return {
        "status": "success",
        "format": "jpeg",
        "width": width,
        "height": height,
        "frame_id": f"sim-frame-{seed}",
        "metadata": {"simulated": True, "seed": seed}
    }

async def simulate_microphone(
    text: str,
    duration_sec: float = 5.0,
    seed: int = 0
) -> dict:
    """Return a deterministic audio clip (TTS + silence)."""
    audio = generate_procedural_audio(text, duration_sec, seed)
    return {
        "status": "success",
        "format": "wav",
        "duration_sec": duration_sec,
        "audio_id": f"sim-audio-{seed}",
        "metadata": {"simulated": True, "seed": seed, "text": text}
    }
```

**Features:**
- Seeded determinism: same seed → same output.
- Optional pre-rendered dataset of synthetic frames/audio.
- Same error codes and schemas as real tools.
- Environment variable to force sim mode: `ANSE_SIMULATE=1`.

**Integration:**
- `anse/engine_core.py` — Add sim mode flag.
- `anse/tools/__init__.py` — Register simulated tools.
- `anse/examples/scripted_agent.py` — Add `--simulate` flag.
- Tests: all tests run in sim mode by default.

---

### Phase 2: Production Hardening (Weeks 3–8)

#### **Weeks 3–5: LLM Production Adapter**

**What to build:**

```python
# anse/examples/llm_agent_adapter_prod.py

from openai import AsyncOpenAI
from anse.world_model import WorldModel
from anse.tool_registry import ToolRegistry

class ProductionLLMAgent:
    def __init__(self, api_key: str, model: str = "gpt-4", operator_token: str = None):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.operator_token = operator_token  # For approval gating
        self.context_window = 4000  # Adaptive context management

    async def run(self, task: str, max_steps: int = 10):
        """Execute task with function-calling loop."""
        messages = [{"role": "user", "content": task}]
        
        for step in range(max_steps):
            # Get tool list and recent events
            tools = await self.registry.list_tools()
            recent_events = await self.world_model.get_recent(limit=5)
            
            # Build context
            system_prompt = self._build_system_prompt(tools, recent_events)
            
            # Call LLM
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                tools=self._format_tools(tools),
                tool_choice="auto"
            )
            
            # Process response
            if response.stop_reason == "tool_calls":
                for tool_call in response.tool_calls:
                    # Check approval if sensitive
                    if self._requires_approval(tool_call):
                        if not self.operator_token:
                            print(f"❌ {tool_call.function.name} requires approval")
                            continue
                    
                    # Execute tool
                    result = await self.tool_registry.call_tool(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )
                    
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id
                    })
            else:
                # LLM finished
                return response.choices[0].message.content
        
        return "Max steps reached"

    def _build_system_prompt(self, tools, recent_events) -> str:
        """Build compact system prompt with context."""
        tool_descriptions = "\n".join([
            f"- {t['name']}: {t['description']} (cost: {t.get('cost', '?')})"
            for t in tools
        ])
        
        event_summary = "\n".join([
            f"  {e['timestamp']}: {e['agent_id']} called {e['tool']} → {e['status']}"
            for e in recent_events
        ])
        
        return f"""You are an autonomous agent with access to the following tools:

{tool_descriptions}

Recent event history:
{event_summary}

Sensitive tools (require operator approval): camera, microphone, network, filesystem:write.

Your task is to complete the user's request using available tools. Be concise. 
Always explain your plan before executing tools."""

    def _requires_approval(self, tool_call) -> bool:
        """Check if tool requires approval."""
        sensitive = {"capture_frame", "record_audio", "network:get", "filesystem:write"}
        return tool_call.function.name in sensitive
```

**Safety:**
- Cost hints in tool descriptions (`cost_per_call: 0.05`).
- Sensitivity labels: `public`, `private`, `sensitive`.
- Approval gating for high-risk tools.
- Rate limiting per agent.

**Integration:**
- Update `anse/examples/llm_agent_adapter.py` with production patterns.
- Document API key management (env vars, vaults).
- Add examples for Claude, Llama, Mistral, etc.

---

#### **Weeks 4–8: Multiagent Isolation & Quotas**

**What to build:**

```python
# anse/multiagent.py

class AgentQuota:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.cpu_budget_ms = 60_000        # 60 seconds per minute
        self.storage_quota_mb = 500
        self.tool_rate_limits = {
            "capture_frame": 30,
            "record_audio": 10,
            "say": 20
        }
        self.event_namespace = f"agent:{agent_id}"

class MultiagentEngine:
    def __init__(self):
        self.quotas: Dict[str, AgentQuota] = {}
        self.world_model = WorldModel()  # Shared

    async def register_agent(self, agent_id: str, quota: AgentQuota):
        """Register agent with quota."""
        self.quotas[agent_id] = quota

    async def call_tool(self, agent_id: str, tool_name: str, args: dict) -> dict:
        """Enforce quotas before calling tool."""
        quota = self.quotas.get(agent_id)
        
        # Check rate limit
        if not quota.check_rate_limit(tool_name):
            return {"status": "error", "reason": "rate_limit_exceeded"}
        
        # Check storage quota
        if quota.storage_used_mb >= quota.storage_quota_mb:
            return {"status": "error", "reason": "storage_quota_exceeded"}
        
        # Call tool
        start_cpu = time.process_time()
        result = await self.tool_registry.call_tool(tool_name, args)
        cpu_used_ms = (time.process_time() - start_cpu) * 1000
        
        # Update quota
        quota.cpu_used_ms += cpu_used_ms
        if "media_size_bytes" in result:
            quota.storage_used_mb += result["media_size_bytes"] / (1024 * 1024)
        
        # Namespaced event log
        await self.world_model.append_event({
            "agent_id": agent_id,
            "tool": tool_name,
            "status": result["status"],
            "cpu_used_ms": cpu_used_ms,
            "namespace": quota.event_namespace
        })
        
        return result

    async def get_agent_view(self, agent_id: str, limit: int = 10):
        """Return events visible to this agent only."""
        quota = self.quotas.get(agent_id)
        return await self.world_model.get_recent(
            limit=limit,
            filter={"namespace": quota.event_namespace}
        )
```

**Features:**
- Per-agent CPU budgets (prevents one agent hogging resources).
- Storage quotas (prevents media bloat).
- Isolated event namespaces (agents see only their own calls by default).
- Resource dashboard: show quota usage per agent.

**Integration:**
- Refactor `anse/engine_core.py` to use `MultiagentEngine`.
- Update `anse/agent_bridge.py` to accept `agent_id` in auth token.
- Add quota management to Operator UI.

---

### Phase 3: Extended Capabilities (Post-v0.2)

#### **Additional Tools** (P3)

After quotas and multiagent isolation are stable, add:

- **Browser automation:**
  ```python
  async def open_url(url: str) -> dict:  # Desktop browser integration
  async def click(selector: str) -> dict
  async def extract_text(selector: str) -> dict
  ```

- **Network tools:**
  ```python
  async def http_get(url: str, timeout: int = 5) -> dict
  async def ping(host: str, timeout: int = 5) -> dict
  ```

- **Filesystem (sandboxed):**
  ```python
  async def read_file(path: str) -> dict  # Only within allowed directories
  async def write_file(path: str, content: str) -> dict
  ```

- **Robot actuators:**
  ```python
  async def move_arm(x: float, y: float, z: float) -> dict
  async def grip(force_percent: int) -> dict
  ```

**Safety:** Each new tool requires:
- Sandbox boundaries (filesystem paths, network domains).
- Approval gating (operator must enable per agent).
- Resource accounting (CPU, network quota).
- Hardware verification (robot arm must be present to enable).

---

## Quick Implementation Timeline

### **Week 1**
- Days 1–3: Health endpoint + diagnostics CLI.
- Days 3–7: Operator UI MVP (backend routes + simple HTML frontend).

### **Week 2–3**
- Simulated sensor suite (deterministic camera, mic).
- Integration with examples and CI.
- Testing: all tests run in sim mode by default.

### **Week 3–4**
- LLM production adapter (OpenAI, context management, approval gating).
- Cost hints and sensitivity labels in tool metadata.

### **Week 4–8**
- Multiagent quotas and isolation.
- Audit UI and replay viewer.
- CI/CD: GitHub Actions, PyPI release.

---

## Success Criteria

### **After Phase 1 (Week 4)**
- ✅ Health endpoint + diagnostics reduce connection failures by 90%.
- ✅ Operator UI enables non-developer users to monitor agents.
- ✅ Simulated sensors enable deterministic testing; all CI tests pass in sim mode.

### **After Phase 2 (Week 8)**
- ✅ LLM adapter allows autonomous agents with real models (OpenAI, Claude).
- ✅ Multiagent isolation prevents resource starvation; quotas enforced.
- ✅ GitHub Actions CI passes on all platforms (Windows, macOS, Linux).
- ✅ PyPI package published; `pip install anse` works.

### **After Phase 3 (Week 12+)**
- ✅ Benchmark suite validates claims and guides research.
- ✅ Extended tools (browser, network, filesystem, robot) available.
- ✅ Community contributions flowing in via clear contribution guidelines.

---

## Personalized Recommendation

**Start with this trio in parallel (Weeks 1–4):**

1. **Health Endpoint + Diagnostics** — Immediate productivity boost.
2. **Operator UI MVP** — Makes the system trustworthy and visible.
3. **Simulated Sensors** — Unlocks safe, deterministic development.

Once those are solid and tested in production:

4. **LLM Production Adapter** — Turns research engine into autonomous agent platform.
5. **Multiagent Isolation** — Prepare for scale and community use.

This sequence gives you working code fast, builds operator confidence, and positions ANSE for adoption before you invest in scale features.

---

## Tracking & Communication

- **Issues:** Create a GitHub project with columns (Backlog, In Progress, Done).
- **Updates:** Weekly status on Discord or GitHub Discussions.
- **Blockers:** Flag early if P1 dependencies collide or timeline slips.
- **Community:** Invite beta testers for Operator UI once MVP is live.

---

**Status:** ANSE v0.1 production-ready. This roadmap guides v0.2–0.3.  
**Last Updated:** February 2026  
**Next Review:** After v0.1 is live in production (4 weeks).

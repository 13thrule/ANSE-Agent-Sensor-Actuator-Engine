# ANSE Roadmap — Remaining Work (Phase 4)

**Current Status:** Phase 3 is 40% complete (network + filesystem tools done)  
**Next Focus:** Phase 4 — Extended capabilities and production optimization

---

## What's LEFT TO DO

### Phase 4: Extended Tools & Performance (Q2 2026)

#### 🚀 High Priority (Next Sprint)

**1. Browser Automation Tools** — `browser/` module
- [ ] `open_url(url, timeout)` — Open URL, return page handle
- [ ] `take_screenshot(handle)` — Capture page screenshot
- [ ] `click(handle, selector)` — Click element by CSS selector
- [ ] `extract_text(handle, selector)` — Extract DOM text
- [ ] `fill_form(handle, data)` — Fill form fields
- Risk: Medium (requires Selenium/Playwright + memory management)
- Timeline: 2-3 weeks

**2. Benchmark Suite** — `benchmark/` module
- [ ] Standard agent task definitions (find object, navigate, etc.)
- [ ] Sim-to-real transfer validation framework
- [ ] Latency/throughput measurement tools
- [ ] Learning curve tracking
- [ ] Tool usage analytics
- Risk: Medium (requires ground truth data, real hardware)
- Timeline: 3-4 weeks

#### 📈 Medium Priority

**3. Robot/SDR Tools** — Extensible hardware interface
- [ ] Robotic arm control (`move_arm`, `grip`, `open_gripper`)
- [ ] Software-defined radio (`list_sdr_devices`, `receive_signal`, `transmit_signal`)
- [ ] Abstract hardware interface pattern
- [ ] Simulation mode for both
- Risk: High (requires hardware knowledge, testing)
- Timeline: 4-6 weeks

#### 🔧 Low Priority / Nice-to-Have

**4. Scripts & Utilities** — `scripts/` folder
- [ ] Deployment automation (Docker build, K8s manifests)
- [ ] Debugging utilities (trace tool calls, replay events)
- [ ] Performance profiling scripts
- [ ] Migration helpers

**5. Performance Optimization**
- [ ] WebSocket batching (multiple events per frame)
- [ ] World model compression (rolling archive)
- [ ] Memory usage profiling
- [ ] Latency benchmarking

**6. Advanced Examples**
- [ ] Multi-agent coordination tutorial
- [ ] Real-world sensor integration guide
- [ ] Custom plugin workshop

---

## What's ALREADY DONE (Phase 1-3)

### ✅ Phase 1: Developer Experience
- [x] Health endpoint & diagnostics
- [x] Operator UI & approval console
- [x] Simulated sensor suite

### ✅ Phase 2: Production Hardening
- [x] Multiagent isolation & quotas
- [x] LLM production adapter template
- [x] Operator audit UI

### ✅ Phase 3 (In Progress)
- [x] Network tools (http_get, ping, dns_lookup)
- [x] Filesystem tools (read_file, write_file, list_directory)
- [ ] Browser automation ← PHASE 4
- [ ] Robot tools ← PHASE 4
- [ ] Benchmark suite ← PHASE 4

---

## Dependency Chain

```
Phase 3 Complete
    ↓
Phase 4 can start:
  Browser Tools (independent)
  Benchmark Suite (uses browser tools for web-based tasks)
  Robot Tools (independent, parallel)
    ↓
Post-Phase 4:
  Performance optimization (measured with benchmarks)
  Advanced examples (using all tools)
  Community feedback loop
```

---

## Effort Estimate

| Task | Effort | Risk | Timeline |
|------|--------|------|----------|
| Browser automation | 2-3 wks | Medium | Weeks 1-3 |
| Benchmark suite | 3-4 wks | Medium | Weeks 2-5 |
| Robot/SDR tools | 4-6 wks | High | Weeks 4-10 |
| Scripts & utilities | 1-2 wks | Low | Weeks 6-8 |
| Performance optimization | 2-3 wks | Low | Weeks 8-11 |

**Total Phase 4 estimate:** 8-12 weeks (parallel work)

---

## Success Criteria

### Browser Tools ✓
- [ ] Can open URL, take screenshot, click elements
- [ ] Integration tests with example websites
- [ ] Rate limiting (max 10 opens/min, 30 clicks/min)
- [ ] Proper cleanup (close browsers, free memory)

### Benchmark Suite ✓
- [ ] 5+ standard agent tasks defined
- [ ] Sim mode passes 100% of benchmarks
- [ ] Real mode latency measured (target: <200ms per cycle)
- [ ] Documented benchmark results

### Robot Tools ✓
- [ ] Simulated robot arm controllable
- [ ] Real robot integration documented
- [ ] SDR interface pattern established
- [ ] Rate limiting for hardware

---

## Notes

- Phase 4 is **not blocking production use** — core engine is stable now
- Browser tools highest priority because they unlock research use cases
- Robot/SDR tools are extensible patterns; real hardware integration will be application-specific
- Benchmark suite validates that sim→real transfer works

---

**Last Updated:** February 14, 2026  
**Next Review:** When Phase 4 starts

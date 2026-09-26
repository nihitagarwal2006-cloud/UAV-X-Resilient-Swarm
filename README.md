# UAV-X: Resilient BVLOS Swarm

## UAV-X — Resilient BVLOS Swarm Challenge
### GC1 Preliminary Design Verification — Software Proof of Concept

**Team Members:**  
- **Nihit Agarwal** — B.Tech CSE (AI & ML), VIT-AP University
- **Anchal** — B.Tech ECE, MAHINDRA University

---

## 🚁 Project Overview

UAV-X is a simulation-first autonomous UAV swarm system designed for resilient disaster-response missions.

The system demonstrates autonomous task allocation, Point-of-Interest (PoI) surveying, communication-aware relay management, UAV failure recovery, safety enforcement, network reconfiguration, and Ground Control Station (GCS) reporting.

The current implementation is configured around the **GC1 Preliminary Design Verification scenario**.

---

# 🎯 GC1 Scenario

The simulator models:

- **1000 m × 1000 m operational arena**
- **Operational centre located 75 m outside the arena**
- **10 randomly generated Points of Interest (PoIs)**
- **100 m communication range**
- **5 m/s maximum UAV speed**
- **20 minute flight-time model**
- **20 m minimum inter-UAV separation**
- UAV deployment from the operational centre
- Autonomous PoI detection
- PoI reporting to the operational centre
- Communication degradation and failure
- UAV technical failures
- Automatic task reassignment
- Dynamic relay-role reconfiguration

---

# 🧠 Core Capabilities

## 1. Autonomous Task Allocation

The swarm dynamically assigns PoIs to available UAVs.

Task allocation considers:

- UAV availability
- Distance to the PoI
- Task priority
- Current mission state

High-priority tasks are handled preferentially.

Example:

```text
POI 01 assigned to UAV 1 [HIGH priority]
POI 02 assigned to UAV 2 [HIGH priority]
POI 03 assigned to UAV 3 [HIGH priority]

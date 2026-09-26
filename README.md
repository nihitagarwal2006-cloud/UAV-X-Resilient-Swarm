# UAV-X: Resilient BVLOS Swarm

### UAV-X — Resilient BVLOS Swarm Challenge
### GC1 Preliminary Design Verification — Software Proof of Concept

A simulation-first autonomous UAV swarm system designed for resilient disaster-response missions with dynamic task allocation, communication-aware relay management, UAV failure recovery, collision avoidance, and mission monitoring.

---

## 🚁 Project Overview

UAV-X simulates a swarm of autonomous UAVs operating in a disaster-response environment where terrestrial communication infrastructure may be unavailable.

The system models:

- Autonomous UAV task allocation
- Disaster Point-of-Interest (PoI) surveying
- Dynamic relay UAV assignment
- Multi-hop communication connectivity
- Communication degradation and outages
- UAV technical failures
- Automatic task reassignment
- Network reconfiguration
- Priority-aware task allocation
- Collision and minimum-separation safety
- Ground Control Station (GCS) reporting
- Mission performance metrics
- Interactive command-center visualization

The current implementation is configured for an official-style **GC1 scenario**.

---

# 🎯 GC1 Scenario

The simulator models a:

- **1000 m × 1000 m operational arena**
- **Operational centre located 75 m outside the arena**
- **10 randomly generated Points of Interest (PoIs)**
- **100 m communication range**
- **5 m/s maximum UAV speed**
- **20 minute maximum flight-time model**
- **20 m minimum inter-UAV separation**
- UAV deployment from the operational centre
- Autonomous PoI detection and reporting

The simulator also introduces communication and technical failures to evaluate swarm resilience.

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

---

## 2. Dynamic Relay UAV Management

UAVs can dynamically assume relay roles based on the current communication topology.

The communication layer continuously evaluates the swarm network and updates relay assignments when the network changes.

Example:

```text
RELAY ROLE UPDATE: UAV 2, UAV 4, UAV 5
RELAY ROLE UPDATE: UAV 4
RELAY ROLE UPDATE: UAV 5
RELAY ROLE UPDATE: UAV 3
RELAY ROLE UPDATE: UAV 1

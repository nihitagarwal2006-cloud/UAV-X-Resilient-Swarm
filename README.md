# UAV-X: Resilient BVIOS Swarm

## Project Overview

**UAV-X Resilient Swarm** is a software-based multi-UAV swarm simulation developed for the **UAV-X: Resilient BVIOS Swarm Challenge**.

The system demonstrates how a UAV swarm can maintain mission continuity despite UAV failures and communication disruptions through autonomous task allocation, path planning, communication monitoring, failure detection, task reassignment, recovery, and mission-level metrics.

---

## Key Features

### Multi-UAV Simulation
- Five UAV agents operating as a coordinated swarm
- UAV position and state tracking
- Dynamic task creation
- Automatic mission progression
- Mission completion monitoring

### Autonomous Task Allocation
- Automatic assignment of tasks to available UAVs
- Distance-based UAV selection
- UAV availability and current assignments considered
- Dynamic reassignment after UAV failures

### A* Path Planning
- Grid-based A* path planning
- Obstacle-aware route generation
- Flight-path visualization
- Path replanning after task reassignment

### Communication System
- UAV-to-UAV communication network
- Communication-range based connectivity
- Communication link monitoring
- Heartbeat-based UAV monitoring
- Communication failure detection

### Resilience and Recovery

When a UAV becomes unavailable, the system automatically:

1. Detects the UAV failure.
2. Identifies the affected task.
3. Searches for an available replacement UAV.
4. Considers communication connectivity.
5. Reassigns the task.
6. Calculates a new path.
7. Continues mission execution.

The recovery mechanism supports multiple UAV failures during a mission.

---

## Failure Scenarios

The simulator provides four selectable scenarios:

| Key | Scenario | Description |
|-----|----------|-------------|
| 1 | Normal Operation | Normal swarm operation without injected failures |
| 2 | Technical Failure | Simulated UAV technical failure |
| 3 | Communication Failure | Simulated communication loss and failure detection |
| 4 | Multiple Failure | Multiple UAV failures during the same mission |

Scenario selection can be performed using keys **1-4** or through the simulator interface.

---

## Mission Metrics

The system records and displays:

- Total tasks
- Completed tasks
- Completion rate
- UAV failures
- Recovery events
- Communication failures
- Mission steps
- Failed UAVs
- Recovered tasks

The metrics are displayed in the real-time mission-control dashboard.

---

## Interactive Mission-Control Dashboard

The Pygame-based interface provides:

- Mission overview
- Swarm map
- UAV fleet status
- Task status
- Mission progress
- Telemetry
- Resilience statistics
- System logs
- Mission statistics
- Failure and recovery information

The simulator also supports interactive task creation by clicking on the map.

---

## Geographic Map Visualization

The simulator includes a geographic map layer for a more realistic disaster-response environment.

Available map modes include:

- **OSM MAP** - OpenStreetMap-based geographic visualization
- **GEO MAP** - Geographic grid and basemap visualization
- **PATHS** - Flight-path focused visualization

A local map cache is included for previously loaded map tiles.

---

## System Architecture

```text
                    UAV-X RESILIENT SWARM
                              |
             +----------------+----------------+
             |                |                |
        Task Management   Communication    Simulation
             |                |                |
       Task Allocation    UAV Network      UAV State
             |             Heartbeat        Movement
             |                |                |
             +----------------+----------------+
                              |
                       Mission Planner
                              |
                    +---------+---------+
                    |                   |
                A* Planner        Resilience Manager
                    |                   |
              Flight Paths        Failure Detection
                                        |
                                Recovery Manager
                                        |
                              Task Reallocation
                                        |
                                Mission Completion
                                        |
                                  Mission Metrics

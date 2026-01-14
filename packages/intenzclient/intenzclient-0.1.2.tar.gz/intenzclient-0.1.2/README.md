# valorantclient.py

### API wrapper for VALORANT's client API



## Installation
```python
pip install intenzclient
```

## Example

```python
from intenzclient import Client

client = Client(region="eu")
client.activate()

print(client.is_lobby())
```

## Notes


## Game State

| Function | Description |
|----------|-------------|
| `in_agent_select()` | Checks if the player is currently in agent selection. Returns the MatchID if yes, otherwise `False`. |
| `is_ingame()` | Checks if the player is currently in a game. Returns the MatchID if yes, otherwise `False`. |
| `is_lobby()` | Checks if the player is currently in the lobby. |

## Party & Matchmaking

| Function | Description |
|----------|-------------|
| `party_id()` | Returns the player's current party ID. |
| `change_queue(queue_id)` | Changes the matchmaking queue for the current party. |
| `start_custom_game()` | Starts a custom game for the party. |
| `enter_matchmaking()` | Joins matchmaking. |
| `leave_matchmaking()` | Leaves matchmaking. |

## Agent Selection

| Function | Description |
|----------|-------------|
| `select_agent(agent_id)` | Selects an agent in agent selection. |
| `lock_agent(agent_id)` | Locks a selected agent. |
| `instalock_agent(agent_id)` | Instantly selects and locks an agent (Instant Lock). |

## Store & Inventory

| Function | Description |
|----------|-------------|
| `owned_items(item_type)` | Lists items the player owns (e.g., skins, agents, sprays). |
| `skin_map()` | Fetches all skins from the Valorant API. |
| `item_prices()` | Returns the prices of all store items. |
| `store_items()` | Shows currently available store items. |
| `wallet()` | Shows the amount of Valorant Points, Radianite, and Kingdom Credits the player has. |

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Union
import hashlib
import itertools
import random
import string
import os
import json

app = FastAPI()

# ---------- Persistence Helpers ----------
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def load_data(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_data(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f)

# ---------- Load Persistent Data ----------
field_map = load_data("map.json", [[0 for _ in range(10)] for _ in range(10)])
mines_db = load_data("mines.json", {})
rovers_db = load_data("rovers.json", {})
counters = load_data("counters.json", {"mine_id_counter": 1, "rover_id_counter": 1})
mine_id_counter = counters["mine_id_counter"]
rover_id_counter = counters["rover_id_counter"]

# ---------- Models ----------
class MapUpdate(BaseModel):
    height: int
    width: int

class Mine(BaseModel):
    id: Optional[int] = None
    x: int
    y: int
    serial_number: str

class Rover(BaseModel):
    id: Optional[int] = None
    status: str  # "Not Started", "Finished", "Moving", "Eliminated"
    position: Optional[List[int]] = [0, 0]  # [x, y]
    commands: Optional[str] = ""
    output: Optional[Union[str, List[List[str]]]] = ""
    pins: Optional[List[str]] = []

class RoverUpdate(BaseModel):
    commands: Optional[str] = None

# ---------- Utility Functions ----------
def find_valid_pin(serial_number: str) -> Optional[str]:
    charset = string.ascii_letters + string.digits
    for length in range(1, 6):
        for pin_tuple in itertools.product(charset, repeat=length):
            pin = ''.join(pin_tuple)
            temp_key = serial_number + pin
            hash_value = hashlib.sha256(temp_key.encode()).hexdigest()
            if hash_value.startswith('000000'):
                return pin
    return None

def get_serial_number(x: int, y: int) -> Optional[str]:
    for mine in mines_db.values():
        if mine["x"] == x and mine["y"] == y:
            return mine["serial_number"]
    return None

# ---------- MAP ENDPOINTS ----------
@app.get("/map")
def get_map():
    # Create a copy so as not to modify the original field_map
    field_with_mines = [row.copy() for row in field_map]
    for key in mines_db:
        mine = mines_db[key]
        field_with_mines[mine["y"]][mine["x"]] = 1
    return field_with_mines

@app.put("/map")
def update_map(map_update: MapUpdate):
    global field_map, mines_db
    field_map = [[0 for _ in range(map_update.width)] for _ in range(map_update.height)]
    # Remove mines out-of-bounds
    keys_to_delete = []
    for key in mines_db:
        mine = mines_db[key]
        if mine["x"] >= map_update.width or mine["y"] >= map_update.height:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        del mines_db[key]
    save_data("map.json", field_map)
    save_data("mines.json", mines_db)
    field_with_mines = [row.copy() for row in field_map]
    for key in mines_db:
        mine = mines_db[key]
        field_with_mines[mine["y"]][mine["x"]] = 1
    return {"message": "Map updated", "map": field_with_mines}

# ---------- MINES ENDPOINTS ----------
@app.get("/mines", response_model=List[Mine])
def get_mines():
    return list(mines_db.values())

@app.get("/mines/{mine_id}", response_model=Mine)
def get_mine(mine_id: int):
    if str(mine_id) not in mines_db:
        raise HTTPException(status_code=404, detail="Mine not found")
    return mines_db[str(mine_id)]

@app.post("/mines", response_model=Mine)
def create_mine(mine: Mine):
    global mine_id_counter, mines_db, counters
    mine.id = mine_id_counter
    mines_db[str(mine_id_counter)] = mine.dict()
    mine_id_counter += 1
    counters["mine_id_counter"] = mine_id_counter
    save_data("mines.json", mines_db)
    save_data("counters.json", counters)
    return mine

@app.put("/mines/{mine_id}", response_model=Mine)
def update_mine(mine_id: int, mine: Mine):
    if str(mine_id) not in mines_db:
        raise HTTPException(status_code=404, detail="Mine not found")
    stored_mine = mines_db[str(mine_id)]
    stored_mine["x"] = mine.x if mine.x is not None else stored_mine["x"]
    stored_mine["y"] = mine.y if mine.y is not None else stored_mine["y"]
    stored_mine["serial_number"] = mine.serial_number if mine.serial_number is not None else stored_mine["serial_number"]
    mines_db[str(mine_id)] = stored_mine
    save_data("mines.json", mines_db)
    return stored_mine

@app.delete("/mines/{mine_id}")
def delete_mine(mine_id: int):
    if str(mine_id) not in mines_db:
        raise HTTPException(status_code=404, detail="Mine not found")
    del mines_db[str(mine_id)]
    save_data("mines.json", mines_db)
    return {"message": "Mine deleted"}

# ---------- ROVERS ENDPOINTS ----------
@app.get("/rovers", response_model=List[Rover])
def get_rovers():
    return list(rovers_db.values())

@app.get("/rovers/{rover_id}", response_model=Rover)
def get_rover(rover_id: int):
    if str(rover_id) not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    return rovers_db[str(rover_id)]

@app.post("/rovers", response_model=Rover)
def create_rover(rover: Rover):
    global rover_id_counter, rovers_db, counters
    rover.id = rover_id_counter
    if rover.status not in ["Not Started", "Finished", "Moving", "Eliminated"]:
        rover.status = "Not Started"
    rovers_db[str(rover_id_counter)] = rover.dict()
    rover_id_counter += 1
    counters["rover_id_counter"] = rover_id_counter
    save_data("rovers.json", rovers_db)
    save_data("counters.json", counters)
    return rover

@app.delete("/rovers/{rover_id}")
def delete_rover(rover_id: int):
    if str(rover_id) not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    del rovers_db[str(rover_id)]
    save_data("rovers.json", rovers_db)
    return {"message": "Rover deleted"}

@app.put("/rovers/{rover_id}", response_model=Rover)
def update_rover_commands(rover_id: int, update: RoverUpdate):
    if str(rover_id) not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    rover = rovers_db[str(rover_id)]
    if rover["status"] not in ["Not Started", "Finished"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot update commands if rover is in Moving or Eliminated status"
        )
    if update.commands is not None:
        rover["commands"] = update.commands
    rovers_db[str(rover_id)] = rover
    save_data("rovers.json", rovers_db)
    return rover

@app.post("/rovers/{rover_id}/dispatch", response_model=Rover)
def dispatch_rover(rover_id: int):
    if str(rover_id) not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    rover = rovers_db[str(rover_id)]
    commands = rover["commands"] or ""
    rows = len(field_map)
    cols = len(field_map[0]) if rows > 0 else 0

    # Copy the map to mark mines
    rover_map = [row.copy() for row in field_map]
    for key in mines_db:
        mine = mines_db[key]
        rover_map[mine["y"]][mine["x"]] = 1

    x, y = 0, 0  # starting position
    i = 0
    success = True
    message = f"Rover {rover_id} executed all commands successfully."

    # Prepare an output grid to mark the rover's path
    output = [['0' for _ in range(cols)] for _ in range(rows)]
    if 0 <= y < rows and 0 <= x < cols:
        output[y][x] = "*"

    while i < len(commands) - 1:
        move = commands[i]
        dig_flag = commands[i+1]
        i += 1

        next_x, next_y = x, y
        if move == 'L':
            next_y -= 1
        elif move == 'R':
            next_y += 1
        elif move == 'M':
            next_x += 1
        else:
            continue

        if not (0 <= next_x < rows and 0 <= next_y < cols):
            continue

        if rover_map[next_x][next_y] == 1:
            if dig_flag == 'D':
                serial_number = get_serial_number(next_y, next_x)
                pin = find_valid_pin(serial_number) if serial_number else None
                if pin:
                    if "pins" not in rover or not rover["pins"]:
                        rover["pins"] = []
                    rover["pins"].append(pin)
                x, y = next_x, next_y
                output[x][y] = "*"
            else:
                x, y = next_x, next_y
                output[x][y] = "*"
                success = False
                message = f"Rover {rover_id} exploded at ({x}, {y})."
                break
        else:
            x, y = next_x, next_y
            output[x][y] = "*"

    rover["position"] = [x, y]
    rover["output"] = output
    rover["commands"] = commands  # preserve original commands
    rover["status"] = "Finished" if success else "Eliminated"
    rovers_db[str(rover_id)] = rover
    save_data("rovers.json", rovers_db)
    return rover

# ---------- WEBSOCKET ENDPOINT ----------
@app.websocket("/ws/rover/{rover_id}")
async def websocket_rover_control(websocket: WebSocket, rover_id: int):
    await websocket.accept()
    if str(rover_id) not in rovers_db:
        await websocket.send_text("Error: Rover not found")
        await websocket.close()
        return
    rover = rovers_db[str(rover_id)]
    if rover["status"] not in ["Not Started", "Finished"]:
        await websocket.send_text("Error: Rover is busy")
        await websocket.close()
        return
    rover["commands"] = ""
    rover["status"] = "Real-Time Control"
    rovers_db[str(rover_id)] = rover
    save_data("rovers.json", rovers_db)
    await websocket.send_text(f"Rover {rover_id} connected for real-time control.")
    try:
        while True:
            data = await websocket.receive_text()
            command = data.strip().upper()
            response = ""
            if command in ["L", "R"]:
                response = f"Command {command} executed: rotation successful."
            elif command == "M":
                pos = rover["position"]
                new_pos = [pos[0] + 1, pos[1] + 1]
                rover["position"] = new_pos
                response = f"Command M executed: new position {new_pos}."
            elif command == "D":
                fake_pin = ''.join(random.choices(string.digits, k=4))
                response = f"Command D executed: PIN {fake_pin}."
            else:
                response = f"Unknown command: {command}"
            rover["commands"] += command
            rovers_db[str(rover_id)] = rover
            save_data("rovers.json", rovers_db)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        rover["status"] = "Finished"
        rovers_db[str(rover_id)] = rover
        save_data("rovers.json", rovers_db)
        print(f"WebSocket disconnected for rover {rover_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
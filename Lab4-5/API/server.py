from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import random
import string
import os

app = FastAPI()

# -------------------------------
# MAP ENDPOINTS
# -------------------------------

# Global variable for the field map; defaulting to a 10x10 grid of zeros.
field_map = [[0 for _ in range(10)] for _ in range(10)]

class MapUpdate(BaseModel):
    height: int
    width: int

class Mine(BaseModel):
    id: Optional[int] = None
    x: int
    y: int
    serial_number: str

# In-memory storage for mines.
mines_db = {}
mine_id_counter = 1

class Rover(BaseModel):
    id: Optional[int] = None
    status: str  # Expected: "Not Started", "Finished", "Moving", "Eliminated"
    position: Optional[List[int]] = [0, 0]  # Represented as [x, y]
    commands: Optional[str] = ""  # List of commands as a string
    output: Optional[str] = ""  # Output path for the rover

class RoverUpdate(BaseModel):
    commands: Optional[str] = None  # List of commands as a string

# In-memory storage for rovers.
rovers_db = {}
rover_id_counter = 1

@app.get("/map")
def get_map():
    """
    Retrieve the 2D array of the field.
    """
    global field_map
    field_with_mines = [[0 for _ in range(len(field_map))] for _ in range(len(field_map[0]))]
    #field_with_mines = field_map.copy()
    print(f"Field without mines: {field_with_mines}")
    print(f"Field with mines: {mines_db}")
    for i in range(1, len(mines_db) + 1):
        print(f"Mine {i} added at ({mines_db[i].x}, {mines_db[i].y})")
        field_with_mines[mines_db[i].y][mines_db[i].x] = 1

    return field_with_mines

@app.put("/map")
def update_map(map_update: MapUpdate):
    """
    Update the height and width of the field.
    """
    global field_map
    field_map = [[0 for _ in range(map_update.width)] for _ in range(map_update.height)]
    for i in range(1, len(mines_db) + 1):
        x = mines_db[i].x
        y = mines_db[i].y
        if x >= map_update.height or y >= map_update.width:
            del mines_db[i]
            
    field_with_mines = field_map
    for i in range(1, len(mines_db) + 1):
        print(f"Mine {i} added at ({mines_db[i].x}, {mines_db[i].y})")
        field_with_mines[mines_db[i].y][mines_db[i].x] = 1
        
    return {"message": "Map updated", "map": field_map}

# -------------------------------
# MINES ENDPOINTS
# -------------------------------

@app.get("/mines", response_model=List[Mine])
def get_mines():
    """
    Retrieve the list of all mines.
    """
    return list(mines_db.values())

@app.get("/mines/{mine_id}", response_model=Mine)
def get_mine(mine_id: int):
    """
    Retrieve a mine by its id.
    """
    if mine_id not in mines_db:
        raise HTTPException(status_code=404, detail="Mine not found")
    return mines_db[mine_id]

@app.post("/mines", response_model=Mine)
def create_mine(mine: Mine):
    """
    Create a new mine with the given coordinates and serial number.
    Returns the created mine with its assigned id.
    """
    global mine_id_counter
    mine.id = mine_id_counter
    mines_db[mine_id_counter] = mine
    mine_id_counter += 1
    return mine

@app.put("/mines/{mine_id}", response_model=Mine)
def update_mine(mine_id: int, mine: Mine):
    """
    Update an existing mine. Only the provided fields are updated.
    Returns the full updated mine object.
    """
    if mine_id not in mines_db:
        raise HTTPException(status_code=404, detail="Mine not found")
    stored_mine = mines_db[mine_id]
    stored_mine.x = mine.x if mine.x is not None else stored_mine.x
    stored_mine.y = mine.y if mine.y is not None else stored_mine.y
    stored_mine.serial_number = mine.serial_number if mine.serial_number is not None else stored_mine.serial_number
    mines_db[mine_id] = stored_mine
    return stored_mine

@app.delete("/mines/{mine_id}")
def delete_mine(mine_id: int):
    """
    Delete the mine with the given id.
    """
    if mine_id not in mines_db:
        raise HTTPException(status_code=404, detail="Mine not found")
    del mines_db[mine_id]
    return {"message": "Mine deleted"}

# -------------------------------
# ROVERS ENDPOINTS
# -------------------------------

@app.get("/rovers", response_model=List[Rover])
def get_rovers():
    """
    Retrieve the list of all rovers.
    """
    return list(rovers_db.values())

@app.get("/rovers/{rover_id}", response_model=Rover)
def get_rover(rover_id: int):
    """
    Retrieve a specific rover by id.
    """
    if rover_id not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    return rovers_db[rover_id]

@app.post("/rovers", response_model=Rover)
def create_rover(rover: Rover):
    """
    Create a new rover. The request must include the list of commands.
    The rover is assigned an id and default status.
    """
    global rover_id_counter
    rover.id = rover_id_counter
    if rover.status not in ["Not Started", "Finished", "Moving", "Eliminated"]:
        rover.status = "Not Started"
    rovers_db[rover_id_counter] = rover
    rover_id_counter += 1
    return rover

@app.delete("/rovers/{rover_id}")
def delete_rover(rover_id: int):
    """
    Delete a rover by id.
    """
    if rover_id not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    del rovers_db[rover_id]
    return {"message": "Rover deleted"}

@app.put("/rovers/{rover_id}", response_model=Rover)
def update_rover_commands(rover_id: int, update: RoverUpdate):
    """
    Update the list of commands for a rover.
    This is allowed only if the rover status is "Not Started" or "Finished".
    """
    if rover_id not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")
    rover = rovers_db[rover_id]
    if rover.status not in ["Not Started", "Finished"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot update commands if rover is in Moving or Eliminated status"
        )
    rover.commands = update.commands
    rovers_db[rover_id] = rover
    return rover

@app.post("/rovers/{rover_id}/dispatch", response_model=Rover)
def dispatch_rover(rover_id: int):
    """
    Dispatch a rover using the step-by-step logic:
      - Parse rover.commands
      - For each move command, check boundaries
      - If cell has a mine and next command is 'D', dig it up
      - Otherwise, if cell has a mine and no 'D', rover explodes
      - Save final path in Output folder
      - Update rover's status and position
    """
    if rover_id not in rovers_db:
        raise HTTPException(status_code=404, detail="Rover not found")

    rover = rovers_db[rover_id]
    commands = rover.commands or ""
    rows = len(field_map)
    cols = len(field_map[0]) if rows > 0 else 0

    print(f"Rows: {rows}, Columns: {cols}")

    rover_map = field_map.copy()
    for i in range(1, len(mines_db) + 1):
        rover_map[mines_db[i].y][mines_db[i].x] = 1
    
    # Current position in (x, y) form
    x, y = 0, 0
    i = 0
    success = True
    message = f"Rover {rover_id} executed all commands successfully."

    # Prepare an output grid to mark the rover's path
    output = [['0' for _ in range(cols)] for _ in range(rows)]
    if 0 <= y < rows and 0 <= x < cols:
        output[y][x] = "*"  # mark starting position

    # Process commands in pairs: (move, nextCommandIfAnyForDig)
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
                
                # Move rover to the next cell
                x, y = next_x, next_y
                output[x][y] = '*'
            else:
                x, y = next_x, next_y
                output[x][y] = '*'
                success = False
                message = f"Rover {i} exploded at ({x}, {y})."
                break
        else:
            x, y = next_x, next_y
            output[x][y] = '*'

    # If we processed all commands (or exploded), mark final position
    # Save path to file
    output_folder = "Output"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    output_filename = os.path.join(output_folder, f"path_{rover_id}.txt")
    with open(output_filename, "w") as f:
        for row in output:
            f.write(" ".join(row) + "\n")

    # Update rover's final position and status
    rover.position = [x, y]
    rover.output = output
    if success:
        rover.status = "Finished"
    else:
        rover.status = "Eliminated"

    rovers_db[rover_id] = rover
    print(f"Rover {rover_id} finished execution with status: {message}")

    return rover

# -------------------------------
# WEBSOCKET ENDPOINT FOR REAL-TIME CONTROL
# -------------------------------

@app.websocket("/ws/rover/{rover_id}")
async def websocket_rover_control(websocket: WebSocket, rover_id: int):
    await websocket.accept()
    if rover_id not in rovers_db:
        await websocket.send_text("Error: Rover not found")
        await websocket.close()
        return

    rover = rovers_db[rover_id]
    # Only allow control if rover is "Not Started" or "Finished"
    if rover.status not in ["Not Started", "Finished"]:
        await websocket.send_text("Error: Rover is busy")
        await websocket.close()
        return

    # Clear the commands for real-time control and update status.
    rover.commands = ""
    rover.status = "Real-Time Control"
    rovers_db[rover_id] = rover

    await websocket.send_text(f"Rover {rover_id} connected for real-time control.")

    try:
        while True:
            # Wait for a command from the operator.
            data = await websocket.receive_text()
            command = data.strip().upper()
            response = ""
            if command in ["L", "R"]:
                # Simulate turning.
                response = f"Command {command} executed: rotation successful."
            elif command == "M":
                # Simulate movement: update rover position arbitrarily.
                pos = rover.position
                new_pos = [pos[0] + 1, pos[1] + 1]
                rover.position = new_pos
                response = f"Command M executed: new position {new_pos}."
            elif command == "D":
                # Simulate digging: generate a fake PIN.
                fake_pin = ''.join(random.choices(string.digits, k=4))
                response = f"Command D executed: PIN {fake_pin}."
            else:
                response = f"Unknown command: {command}"

            # Append the executed command.
            rover.commands += command
            rovers_db[rover_id] = rover

            # Send the response back to the operator.
            await websocket.send_text(response)
    except WebSocketDisconnect:
        # Reset rover status when client disconnects.
        rover.status = "Finished"
        rovers_db[rover_id] = rover
        print(f"WebSocket disconnected for rover {rover_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

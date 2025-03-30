"use client";
import React, { useState, useEffect } from "react";

interface Rover {
  id: number;
  status: string;
  position: number[];
  commands: string;
  output?: string[];
  message?: string;
  pins: string[];
}

const RoversPage: React.FC = () => {
  const [rovers, setRovers] = useState<Rover[]>([]);
  const [newRoverCmd, setNewRoverCmd] = useState<string>("");

  // Track which rover is currently dispatching (for showing spinner)
  const [loadingRoverId, setLoadingRoverId] = useState<number | null>(null);

  // Track dispatch results keyed by rover ID (e.g. final messages)
  const [dispatchResults, setDispatchResults] = useState<{ [roverId: number]: string }>({});

  // For inline editing of a rover's commands.
  const [editingRoverId, setEditingRoverId] = useState<number | null>(null);
  const [editRoverCmd, setEditRoverCmd] = useState<string>("");

  const fetchRovers = async () => {
    const res = await fetch(`/api/proxy/rovers`);
    const data = await res.json();
    setRovers(data);
  };

  useEffect(() => {
    fetchRovers();
  }, []);

  const createRover = async () => {
    // Create rover only if some commands have been entered.
    if (!newRoverCmd.trim()) return;
    await fetch(`/api/proxy/rovers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        commands: newRoverCmd,
        status: "Not Started",
        position: [0, 0],
      }),
    });
    setNewRoverCmd("");
    fetchRovers();
  };

  const dispatchRover = async (id: number) => {
    try {
      setLoadingRoverId(id); // show spinner for this rover
      setDispatchResults((prev) => ({ ...prev, [id]: "" })); // clear old result
      const res = await fetch(`/api/proxy/rovers/${id}/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const updatedRover = await res.json();

      let resultMsg = "";
      if (updatedRover.status === "Eliminated") {
        resultMsg = `Rover ${id} blew up!`;
      } else if (updatedRover.status === "Finished") {
        resultMsg = `Rover ${id} survived.`;
      }
      if (updatedRover.message) {
        resultMsg += ` ${updatedRover.message}`;
      }
      if (updatedRover.output && Array.isArray(updatedRover.output)) {
        resultMsg += `\nFinal output:\n${updatedRover.output.join("\n").replace(/,/g, " ")}`;
      }
      setDispatchResults((prev) => ({ ...prev, [id]: resultMsg.trim() }));
    } catch (err) {
      console.error("Dispatch error:", err);
      setDispatchResults((prev) => ({
        ...prev,
        [id]: "Error dispatching rover.",
      }));
    } finally {
      setLoadingRoverId(null); // hide spinner
      fetchRovers();
    }
  };

  const deleteRover = async (id: number) => {
    await fetch(`/api/proxy/rovers/${id}`, { method: "DELETE" });
    fetchRovers();
  };

  const startEditing = (rover: Rover) => {
    // Allow editing only if status is Not Started or Finished.
    if (rover.status === "Not Started" || rover.status === "Finished") {
      setEditingRoverId(rover.id);
      setEditRoverCmd(rover.commands);
    }
  };

  const cancelEditing = () => {
    setEditingRoverId(null);
    setEditRoverCmd("");
  };

  const updateRover = async (id: number) => {
    await fetch(`/api/proxy/rovers/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ commands: editRoverCmd }),
    });
    setEditingRoverId(null);
    fetchRovers();
  };

  return (
    <div className="80vh p-6">
      <div className="max-w-3xl mx-auto bg-white shadow-md rounded p-8 overflow-hidden">
        <h1 className="text-2xl font-bold mb-4">Rovers Management</h1>
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-2">Create New Rover</h2>
          <div className="flex items-center space-x-4">
            <input
              type="text"
              placeholder="Enter commands"
              value={newRoverCmd}
              onChange={(e) => setNewRoverCmd(e.target.value)}
              className="border rounded p-2 w-full"
            />
            <button
              onClick={createRover}
              disabled={!newRoverCmd.trim()}
              className={`px-4 py-2 text-white rounded ${
                !newRoverCmd.trim()
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-500 hover:bg-blue-600 cursor-pointer"
              }`}
            >
              Create Rover
            </button>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-2">All Rovers</h2>
          <ul className="space-y-4">
            {rovers.map((rover) => {
              const dispatchMsg = dispatchResults[rover.id] || "";
              const isLoading = loadingRoverId === rover.id;
              const isEditable = rover.status === "Not Started" || rover.status === "Finished";
              return (
                <li
                  key={rover.id}
                  className="w-full p-4 bg-gray-100 rounded flex flex-col md:flex-row items-center"
                >
                  {/* Details container with horizontal scrolling */}
                  <div className="flex-1 overflow-x-auto pr-4">
                    <p>
                      <strong>ID:</strong> {rover.id}
                    </p>
                    <p>
                      <strong>Status:</strong> {rover.status}
                    </p>
                    <p>
                      <strong>Position:</strong> {JSON.stringify(rover.position)}
                    </p>
                    <p>
                      <strong>Found Pins:</strong> {rover.pins.length > 0 ? rover.pins.join(", ") : "None"}
                    </p>
                    {editingRoverId === rover.id ? (
                      <div className="overflow-x-auto">
                        <input
                          type="text"
                          value={editRoverCmd}
                          onChange={(e) => setEditRoverCmd(e.target.value)}
                          className="border rounded p-1 w-full whitespace-nowrap"
                        />
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <p className="whitespace-nowrap">
                          <strong>Commands:</strong> {rover.commands}
                        </p>
                      </div>
                    )}
                    {dispatchMsg && (
                      <div className="mt-2 whitespace-pre-wrap">
                        <strong>Result:</strong> {dispatchMsg}
                      </div>
                    )}
                  </div>
                  {/* Actions column fixed on the right */}
                  <div className="flex-shrink-0 flex flex-col space-y-2 mt-4 md:mt-0">
                    {editingRoverId === rover.id ? (
                      <>
                        <button
                          onClick={() => updateRover(rover.id)}
                          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer"
                        >
                          Save
                        </button>
                        <button
                          onClick={cancelEditing}
                          className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 cursor-pointer"
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
                        {isEditable && (
                          <button
                            onClick={() => startEditing(rover)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 cursor-pointer"
                          >
                            Edit
                          </button>
                        )}
                        <button
                          onClick={() => dispatchRover(rover.id)}
                          disabled={isLoading}
                          className={`px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 cursor-pointer ${
                            isLoading ? "opacity-50" : ""
                          }`}
                        >
                          {isLoading ? "Dispatching..." : "Dispatch"}
                        </button>
                        {isLoading && (
                          <div
                            className="w-6 h-6 border-4 border-blue-500 border-t-transparent border-solid rounded-full animate-spin"
                            title="Dispatching..."
                          ></div>
                        )}
                        <button
                          onClick={() => deleteRover(rover.id)}
                          className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 cursor-pointer"
                        >
                          Delete
                        </button>
                      </>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default RoversPage;
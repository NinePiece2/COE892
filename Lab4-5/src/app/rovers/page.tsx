"use client";
import React, { useState, useEffect } from "react";

interface Rover {
  id: number;
  status: string;
  position: number[];
  commands: string;
  output?: string[];
  message?: string;
}

const RoversPage: React.FC = () => {
  const [rovers, setRovers] = useState<Rover[]>([]);
  const [newRoverCmd, setNewRoverCmd] = useState<string>("");

  // Track which rover is currently dispatching (for showing spinner)
  const [loadingRoverId, setLoadingRoverId] = useState<number | null>(null);

  // Track dispatch results keyed by rover ID (e.g. final messages)
  const [dispatchResults, setDispatchResults] = useState<{ [roverId: number]: string }>({});

  const fetchRovers = async () => {
    const res = await fetch(`/api/proxy/rovers`);
    const data = await res.json();
    setRovers(data);
  };

  useEffect(() => {
    fetchRovers();
  }, []);

  const createRover = async () => {
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
        body: JSON.stringify({
        }),
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

  return (
    <div className="min-h-screen p-6">
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
              className="px-4 py-2 text-white bg-green-500 rounded hover:bg-blue-600 cursor-pointer"
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
                    <div className="overflow-x-auto">
                      <p className="whitespace-nowrap">
                        <strong>Commands:</strong> {rover.commands}
                      </p>
                    </div>
                    {dispatchMsg && (
                      <div className="mt-2 whitespace-pre-wrap">
                        <strong>Result:</strong> {dispatchMsg}
                      </div>
                    )}
                  </div>
                  {/* Actions column fixed on the right */}
                  <div className="flex-shrink-0 flex flex-col space-y-2 mt-4 md:mt-0">
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
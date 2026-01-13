"""Flask-SocketIO server for EvoKernel dashboard with real-time updates."""

import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template
from flask_socketio import SocketIO

from ..openevolve_integration.runner import get_evolution_status


def get_island_data(run_path: Path) -> dict:
    """Read detailed island data from checkpoint or logs."""
    data = {"islands": [], "total_programs": 0, "num_islands": 0, "best_code": None}

    checkpoint_dir = run_path / "checkpoints"
    if checkpoint_dir.exists():
        checkpoints = sorted(checkpoint_dir.glob("checkpoint_*"))
        if checkpoints:
            latest = checkpoints[-1]
            metadata_path = latest / "metadata.json"

            if metadata_path.exists():
                try:
                    with open(metadata_path) as f:
                        metadata = json.load(f)

                    islands_data = metadata.get("islands", [])
                    island_best_ids = metadata.get("island_best_programs", [])
                    island_generations = metadata.get(
                        "island_generations", [0] * len(islands_data)
                    )
                    current_island = metadata.get("current_island", 0)
                    best_program_id = metadata.get("best_program_id")

                    data["num_islands"] = len(islands_data)
                    data["total_programs"] = sum(len(island) for island in islands_data)

                    programs = {}
                    programs_dir = latest / "programs"
                    if programs_dir.exists():
                        for prog_file in programs_dir.glob("*.json"):
                            try:
                                with open(prog_file) as f:
                                    prog = json.load(f)
                                programs[prog.get("id")] = prog
                            except Exception:
                                continue

                    if best_program_id and best_program_id in programs:
                        data["best_code"] = programs[best_program_id].get("code", "")

                    for i, island_program_ids in enumerate(islands_data):
                        island_info = {
                            "index": i,
                            "program_count": len(island_program_ids),
                            "generation": island_generations[i]
                            if i < len(island_generations)
                            else 0,
                            "is_current": i == current_island,
                            "best_score": 0.0,
                            "best_speedup": 0.0,
                            "best_code": None,
                        }

                        best_id = (
                            island_best_ids[i] if i < len(island_best_ids) else None
                        )
                        if best_id and best_id in programs:
                            prog = programs[best_id]
                            metrics = prog.get("metrics", {})
                            island_info["best_score"] = metrics.get(
                                "combined_score", 0.0
                            )
                            island_info["best_speedup"] = metrics.get("speedup", 0.0)
                            island_info["best_code"] = prog.get("code", "")

                        data["islands"].append(island_info)

                    if data["num_islands"] > 0:
                        return data
                except Exception:
                    pass

    log_path = run_path / "log" / "openevolve.log"
    if not log_path.exists():
        log_path = run_path / "openevolve.log"

    if log_path.exists():
        try:
            lines = log_path.read_text().strip().split("\n")

            for line in lines:
                match = re.search(r"island-based evolution with (\d+) islands", line)
                if match:
                    data["num_islands"] = int(match.group(1))
                    break

            island_info_map = {}
            for line in lines:
                match = re.search(r"Island (\d+): (\d+) programs, best=([\d.]+)", line)
                if match:
                    idx = int(match.group(1))
                    island_info_map[idx] = {
                        "index": idx,
                        "program_count": int(match.group(2)),
                        "best_score": float(match.group(3)),
                        "best_speedup": 0.0,
                        "generation": 0,
                        "is_current": False,
                        "best_code": None,
                    }

            if island_info_map:
                data["islands"] = [
                    island_info_map.get(
                        i,
                        {
                            "index": i,
                            "program_count": 0,
                            "best_score": 0.0,
                            "best_speedup": 0.0,
                            "generation": 0,
                            "is_current": False,
                            "best_code": None,
                        },
                    )
                    for i in range(data["num_islands"])
                ]
                data["total_programs"] = sum(
                    isl.get("program_count", 0) for isl in data["islands"]
                )
        except Exception:
            pass

    return data


def get_speedup_history(run_path: Path) -> list:
    """Extract speedup history from logs for charting."""
    history = []
    log_path = run_path / "openevolve.log"

    if log_path.exists():
        try:
            lines = log_path.read_text().strip().split("\n")
            for line in lines:
                match = re.search(r"speedup=([\d.]+)", line)
                if match:
                    history.append(float(match.group(1)))
        except Exception:
            pass

    return history


def get_tree_data(run_path: Path) -> dict | None:
    """Build evolution tree structure for D3 visualization."""
    checkpoint_dir = run_path / "checkpoints"
    if not checkpoint_dir.exists():
        return None

    checkpoints = sorted(checkpoint_dir.glob("checkpoint_*"))
    if not checkpoints:
        return None

    latest = checkpoints[-1]
    programs_dir = latest / "programs"
    if not programs_dir.exists():
        return None

    programs = {}
    for prog_file in programs_dir.glob("*.json"):
        try:
            with open(prog_file) as f:
                prog = json.load(f)
            programs[prog.get("id")] = prog
        except Exception:
            continue

    if not programs:
        return None

    # Build tree from parent relationships
    root = None
    nodes = {}

    for prog_id, prog in programs.items():
        metrics = prog.get("metrics", {})
        node = {
            "id": prog_id,
            "speedup": metrics.get("speedup", 0.0),
            "improved": metrics.get("speedup", 0.0) > 1.0,
            "children": [],
        }
        nodes[prog_id] = node

        parent_id = prog.get("parent_id")
        if not parent_id or parent_id not in programs:
            if root is None or metrics.get("combined_score", 0) > nodes.get(
                root, {}
            ).get("speedup", 0):
                root = prog_id

    if not root:
        root = list(nodes.keys())[0]

    # Link parents to children
    for prog_id, prog in programs.items():
        parent_id = prog.get("parent_id")
        if parent_id and parent_id in nodes:
            nodes[parent_id]["children"].append(nodes[prog_id])

    return nodes.get(root)


def get_gpu_type(run_path: Path) -> str | None:
    """Get GPU type from process info."""
    info_path = run_path / "process_info.json"
    if info_path.exists():
        try:
            with open(info_path) as f:
                info = json.load(f)
            return info.get("gpu_type")
        except Exception:
            pass
    return None


def get_config_info(run_path: Path) -> dict:
    """Extract configuration info for display."""
    config_info = {
        "models": [],
        "max_iterations": 100,
        "num_islands": 5,
        "evaluator": "modal",
        "task": None,
        "target_file": None,
    }

    # Try config.yaml first
    config_path = run_path / "config.yaml"
    if config_path.exists():
        try:
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)

            config_info["max_iterations"] = config.get("max_iterations", 100)
            config_info["num_islands"] = config.get("database", {}).get(
                "num_islands", 5
            )

            # Extract model names
            llm_config = config.get("llm", {})
            models = llm_config.get("models", [])
            for m in models:
                name = m.get("model_name", "")
                if name:
                    # Shorten long model names
                    short = name.split("/")[-1] if "/" in name else name
                    config_info["models"].append(short)
        except Exception:
            pass

    # Get task and target from process_info.json
    info_path = run_path / "process_info.json"
    if info_path.exists():
        try:
            with open(info_path) as f:
                info = json.load(f)
            config_info["task"] = info.get("task")
            config_info["evaluator"] = info.get("evaluator_mode", "modal")
            target = info.get("target")
            if target:
                config_info["target_file"] = Path(target).name
        except Exception:
            pass

    return config_info


def background_emitter(app, socketio, run_path: Path):
    """Background task that emits status updates every 2 seconds."""
    last_log_size = 0

    while True:
        socketio.sleep(2)

        with app.app_context():
            try:
                status = get_evolution_status(run_path)
                island_data = get_island_data(run_path)

                iteration = status.get("iteration", 0)
                max_iter = status.get("max_iterations", 100)

                # Calculate ETA
                eta = None
                if status.get("running") and iteration > 0:
                    info_path = run_path / "process_info.json"
                    if info_path.exists():
                        try:
                            start_time = info_path.stat().st_mtime
                            elapsed = time.time() - start_time
                            time_per_iter = elapsed / iteration
                            remaining = time_per_iter * (max_iter - iteration)
                            if remaining < 60:
                                eta = f"{int(remaining)}s"
                            elif remaining < 3600:
                                eta = f"{int(remaining / 60)}m {int(remaining % 60)}s"
                            else:
                                eta = f"{int(remaining / 3600)}h {int((remaining % 3600) / 60)}m"
                        except Exception:
                            pass

                socketio.emit(
                    "status_update",
                    {
                        **status,
                        **island_data,
                        "eta": eta,
                    },
                )

                # Emit new log lines
                log_path = run_path / "openevolve.log"
                if log_path.exists():
                    try:
                        current_size = log_path.stat().st_size
                        if current_size > last_log_size:
                            with open(log_path) as f:
                                f.seek(last_log_size)
                                new_content = f.read()
                            last_log_size = current_size

                            for line in new_content.strip().split("\n"):
                                if line:
                                    socketio.emit("log_update", {"line": line})
                    except Exception:
                        pass

                # Stop if evolution completed
                if not status.get("running") and status.get("completed"):
                    break

            except Exception as e:
                socketio.emit("status_update", {"error": str(e)})


def create_app(run_dir: Path) -> tuple[Flask, SocketIO]:
    """Create Flask app with SocketIO for real-time dashboard."""
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))
    app.config["run_dir"] = run_dir
    app.config["SECRET_KEY"] = "evokernel-secret"

    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

    @app.route("/")
    def index():
        run_path = Path(app.config["run_dir"])

        try:
            status = get_evolution_status(run_path)
        except Exception as e:
            status = {"error": str(e), "running": False, "completed": False}

        island_data = get_island_data(run_path)
        speedup_history = get_speedup_history(run_path)
        tree_data = get_tree_data(run_path)
        gpu_type = get_gpu_type(run_path)
        config_info = get_config_info(run_path)

        iteration = status.get("iteration", 0)
        max_iter = status.get("max_iterations", 100)
        progress_pct = (iteration / max_iter * 100) if max_iter > 0 else 0

        eta = None
        if status.get("running") and iteration > 0:
            info_path = run_path / "process_info.json"
            if info_path.exists():
                try:
                    start_time = info_path.stat().st_mtime
                    elapsed = time.time() - start_time
                    time_per_iter = elapsed / iteration
                    remaining = time_per_iter * (max_iter - iteration)
                    if remaining < 60:
                        eta = f"{int(remaining)}s"
                    elif remaining < 3600:
                        eta = f"{int(remaining / 60)}m {int(remaining % 60)}s"
                    else:
                        eta = (
                            f"{int(remaining / 3600)}h {int((remaining % 3600) / 60)}m"
                        )
                except Exception:
                    pass

        log_lines = []
        log_path = run_path / "openevolve.log"
        if log_path.exists():
            try:
                lines = log_path.read_text().strip().split("\n")
                log_lines = lines[-100:]
            except Exception:
                pass

        status.setdefault("best_speedup", 0.0)
        status.setdefault("best_score", 0.0)
        status.setdefault("iteration", 0)
        status.setdefault("max_iterations", 100)

        return render_template(
            "dashboard.html",
            run_name=run_path.name,
            status=status,
            progress_pct=progress_pct,
            eta=eta,
            islands=island_data["islands"],
            num_islands=island_data["num_islands"],
            total_programs=island_data["total_programs"],
            best_code=island_data["best_code"],
            log_lines=log_lines,
            speedup_history=speedup_history,
            tree_data=tree_data,
            gpu_type=gpu_type,
            config=config_info,
            last_updated=datetime.now().strftime("%H:%M:%S"),
        )

    @app.route("/api/status")
    def api_status():
        run_path = Path(app.config["run_dir"])
        try:
            status = get_evolution_status(run_path)
            island_data = get_island_data(run_path)
            return jsonify({**status, **island_data})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @socketio.on("connect")
    def handle_connect():
        run_path = Path(app.config["run_dir"])
        socketio.start_background_task(background_emitter, app, socketio, run_path)

    return app, socketio


def run_server(run_dir: Path, port: int = 5000, debug: bool = False):
    """Run the dashboard server."""
    app, socketio = create_app(run_dir)
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)

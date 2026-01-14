"""State file management for resumable downloads."""

import asyncio
from pathlib import Path
from typing import Any

import aiofiles
import yaml


class StateManager:
    """Manages state.yaml file for tracking download progress."""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self._lock = asyncio.Lock()

    async def load_state(self) -> dict[str, Any] | None:
        """Load state from YAML file.

        Returns:
            State dict if file exists and valid, None otherwise
        """
        if not self.state_file.exists():
            return None

        try:
            async with aiofiles.open(self.state_file) as f:
                content = await f.read()
                state = yaml.safe_load(content)

                # Validate state structure
                if not isinstance(state, dict):
                    raise ValueError("State file is not a valid dictionary")
                if "parts" not in state or not isinstance(state["parts"], list):
                    raise ValueError("State file missing 'parts' list")

                return state

        except (yaml.YAMLError, ValueError, OSError) as e:
            import logging

            logging.warning(
                f"Failed to load state file (corrupted or invalid): {e}. "
                "Starting fresh download."
            )
            return None

    async def save_state(self, state: dict[str, Any]) -> None:
        """Save state to YAML file (thread-safe)."""
        async with self._lock:
            await self._save_state_unlocked(state)

    async def _save_state_unlocked(self, state: dict[str, Any]) -> None:
        """Save state to YAML file (internal, assumes lock is held)."""
        async with aiofiles.open(self.state_file, "w") as f:
            await f.write(yaml.dump(state, default_flow_style=False))

    async def update_part_verified(self, part_id: int) -> None:
        """Mark a part as verified in the state file."""
        async with self._lock:
            state = await self.load_state()
            if state is None:
                raise RuntimeError("Cannot update part: state file does not exist")

            # Find the part and mark it verified
            for part in state["parts"]:
                if part["id"] == part_id:
                    part["verified"] = True
                    break

            await self._save_state_unlocked(state)

    def initialize_state(
        self, block_height: int, cdn_url: str, parts: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create new state from API metadata.

        All parts are initially marked as verified=false.

        Args:
            block_height: Bootstrap block height
            cdn_url: Base CDN URL
            parts: List of part metadata from API

        Returns:
            State dict ready to save
        """
        total_size = sum(p["bytes"] for p in parts)

        state_parts = []
        for i, part in enumerate(parts):
            state_parts.append(
                {
                    "id": i,
                    "path": part["path"],
                    "size": part["bytes"],
                    "sha256": part["sha256"],
                    "verified": False,
                }
            )

        return {
            "version": 1,
            "block_height": block_height,
            "cdn_url": cdn_url,
            "total_size": total_size,
            "parts": state_parts,
        }

    def get_verified_parts(self, state: dict[str, Any]) -> list[int]:
        """Get list of verified part IDs from state.

        Returns:
            Sorted list of part IDs that are verified
        """
        verified = [p["id"] for p in state["parts"] if p["verified"]]
        return sorted(verified)

    def get_first_unverified_part(self, state: dict[str, Any]) -> int | None:
        """Get the first unverified part ID.

        Returns:
            Part ID of first unverified part, or None if all verified
        """
        for part in state["parts"]:
            if not part["verified"]:
                return part["id"]
        return None

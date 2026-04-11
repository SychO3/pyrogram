#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

"""Per-entity update state tracking with gap detection."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Optional, Tuple

if TYPE_CHECKING:
    from pyrogram.bot_handle import BotHandle

log = logging.getLogger(__name__)


@dataclass
class EntityState:
    """Update state for a single entity (global=0, or channel_id)."""
    entity_id: int
    pts: int = 0
    qts: int = 0
    date: int = 0
    seq: int = 0

    def to_tuple(self) -> Tuple[int, int, int, int, int]:
        return (self.entity_id, self.pts, self.qts, self.date, self.seq)

    @classmethod
    def from_tuple(cls, t: tuple) -> "EntityState":
        return cls(
            entity_id=t[0],
            pts=t[1] or 0,
            qts=t[2] or 0,
            date=t[3] or 0,
            seq=t[4] or 0,
        )


@dataclass
class UpdateState:
    """Per-bot update state tracker with gap detection.

    Wraps the raw (id, pts, qts, date, seq) tuples from storage
    and provides structured gap detection.
    """

    bot_id: int
    _states: Dict[int, EntityState] = field(default_factory=dict)
    _gap_count: int = 0

    @property
    def global_state(self) -> EntityState:
        """The global (entity_id=0) state."""
        if 0 not in self._states:
            self._states[0] = EntityState(entity_id=0)
        return self._states[0]

    @property
    def gap_count(self) -> int:
        return self._gap_count

    def get_entity_state(self, entity_id: int) -> Optional[EntityState]:
        return self._states.get(entity_id)

    def get_or_create(self, entity_id: int) -> EntityState:
        if entity_id not in self._states:
            self._states[entity_id] = EntityState(entity_id=entity_id)
        return self._states[entity_id]

    async def load_from_storage(self, storage) -> None:
        """Load all states from storage into memory."""
        raw_states = await storage.update_state()
        if not raw_states:
            return
        for t in raw_states:
            self._states[t[0]] = EntityState.from_tuple(t)

    async def save_to_storage(self, storage) -> None:
        """Save all states to storage."""
        for state in self._states.values():
            await storage.update_state(state.to_tuple())

    def apply_pts(self, entity_id: int, pts: int, pts_count: int,
                  date: Optional[int] = None, seq: Optional[int] = None) -> bool:
        """Apply a pts update. Returns True if a gap is detected.

        Args:
            entity_id: 0 for global state, channel_id for channel state.
            pts: The new pts value from the update.
            pts_count: Number of pts this update consumes.
            date: Optional date to store.
            seq: Optional seq to store (global only).

        Returns:
            True if a gap was detected (pts jumped, some updates were missed).
        """
        state = self.get_or_create(entity_id)

        if state.pts == 0:
            # First time seeing state for this entity
            state.pts = pts
            if date is not None:
                state.date = date
            if seq is not None:
                state.seq = seq
            return False

        expected_pts = state.pts + pts_count

        if pts < state.pts:
            # Duplicate or old update
            return False

        if pts == expected_pts:
            # Normal progression
            state.pts = pts
            if date is not None:
                state.date = date
            if seq is not None:
                state.seq = seq
            return False

        if pts > expected_pts:
            # Gap detected
            self._gap_count += 1
            log.warning(
                "pts gap detected for entity %d: expected %d, got %d (gap=%d)",
                entity_id, expected_pts, pts, pts - expected_pts,
            )
            state.pts = pts
            if date is not None:
                state.date = date
            if seq is not None:
                state.seq = seq
            return True

        # pts == state.pts (duplicate)
        return False

    def apply_seq(self, seq: int, seq_start: Optional[int] = None) -> bool:
        """Apply a seq update (global only). Returns True if gap detected."""
        state = self.global_state
        if state.seq == 0:
            state.seq = seq
            return False

        start = seq_start if seq_start is not None else seq
        if start > state.seq + 1:
            self._gap_count += 1
            log.warning(
                "seq gap detected: stored=%d, seq_start=%d",
                state.seq, start,
            )
            state.seq = seq
            return True

        if seq > state.seq:
            state.seq = seq

        return False

    def apply_qts(self, qts: int) -> bool:
        """Apply a qts update (global only). Returns True if gap detected."""
        state = self.global_state
        if state.qts == 0:
            state.qts = qts
            return False

        if qts > state.qts + 1:
            self._gap_count += 1
            log.warning(
                "qts gap detected: stored=%d, got=%d",
                state.qts, qts,
            )
            state.qts = qts
            return True

        if qts > state.qts:
            state.qts = qts

        return False

    def remove_entity(self, entity_id: int) -> None:
        self._states.pop(entity_id, None)

    def all_states(self) -> list:
        return [s.to_tuple() for s in self._states.values()]

    def __repr__(self) -> str:
        return f"UpdateState(bot_id={self.bot_id}, entities={len(self._states)}, gaps={self._gap_count})"

    async def fill_gap(self, bot: "BotHandle") -> Tuple[int, int]:
        """Fill update gaps by calling getDifference/getChannelDifference.

        Iterates all tracked entity states and fetches missed updates from the
        server, dispatching recovered messages and updates.

        Returns:
            (message_count, update_count) recovered.
        """
        from pyrogram import raw
        from pyrogram.errors import (
            ChannelInvalid,
            ChannelPrivate,
            PersistentTimestampInvalid,
            PersistentTimestampOutdated,
        )
        from pyrogram.utils import ZERO_CHANNEL_ID

        msg_count = 0
        upd_count = 0

        states = list(self._states.values())
        if not states:
            return (msg_count, upd_count)

        log.info("Bot %d: starting gap recovery for %d entities", self.bot_id, len(states))

        for state in states:
            entity_id = state.entity_id
            local_pts = state.pts
            local_qts = state.qts
            local_date = state.date
            local_seq = state.seq

            if local_pts == 0:
                continue

            prev_pts = 0

            while True:
                try:
                    if entity_id != 0 and entity_id < ZERO_CHANNEL_ID:
                        # Channel — need to resolve the peer
                        try:
                            peer = await bot.storage.get_peer_by_id(entity_id)
                        except KeyError:
                            log.warning(
                                "Bot %d: cannot resolve peer for entity %d, skipping gap recovery",
                                self.bot_id, entity_id,
                            )
                            break

                        diff = await bot.invoke(
                            raw.functions.updates.GetChannelDifference(
                                channel=raw.types.InputChannel(
                                    channel_id=ZERO_CHANNEL_ID - entity_id,
                                    access_hash=peer.access_hash,
                                ),
                                filter=raw.types.ChannelMessagesFilterEmpty(),
                                pts=local_pts,
                                limit=10000,
                                force=False,
                            )
                        )
                    else:
                        # Global state
                        diff = await bot.invoke(
                            raw.functions.updates.GetDifference(
                                pts=local_pts,
                                date=local_date,
                                qts=0,
                            )
                        )
                except (ChannelPrivate, ChannelInvalid):
                    log.info("Bot %d: channel %d inaccessible, removing state", self.bot_id, entity_id)
                    self.remove_entity(entity_id)
                    await bot.storage.update_state(entity_id)
                    break
                except (PersistentTimestampOutdated, PersistentTimestampInvalid):
                    continue
                except Exception as e:
                    log.warning("Bot %d: gap recovery failed for entity %d: %s", self.bot_id, entity_id, e)
                    break

                # Handle diff types
                if isinstance(diff, raw.types.updates.DifferenceEmpty):
                    local_seq = diff.seq
                    local_date = diff.date
                    break
                elif isinstance(diff, raw.types.updates.DifferenceTooLong):
                    local_pts = diff.pts
                    continue
                elif isinstance(diff, raw.types.updates.Difference):
                    local_pts = diff.state.pts
                    local_date = diff.state.date
                    local_seq = diff.state.seq
                elif isinstance(diff, raw.types.updates.DifferenceSlice):
                    local_pts = diff.intermediate_state.pts
                    local_date = diff.intermediate_state.date
                    local_seq = diff.intermediate_state.seq
                    if prev_pts == local_pts:
                        break
                    prev_pts = local_pts
                elif isinstance(diff, raw.types.updates.ChannelDifferenceEmpty):
                    state.pts = diff.pts
                    break
                elif isinstance(diff, raw.types.updates.ChannelDifferenceTooLong):
                    local_pts = diff.dialog.pts
                    continue
                elif isinstance(diff, raw.types.updates.ChannelDifference):
                    local_pts = diff.pts

                # Dispatch recovered updates
                users = {i.id: i for i in diff.users}
                chats = {i.id: i for i in diff.chats}

                for message in diff.new_messages:
                    msg_count += 1
                    await bot._runtime.update_dispatcher.dispatch(
                        self.bot_id,
                        (
                            raw.types.UpdateNewMessage(
                                message=message,
                                pts=local_pts,
                                pts_count=-1,
                            ),
                            users,
                            chats,
                        ),
                    )

                for update in diff.other_updates:
                    upd_count += 1
                    await bot._runtime.update_dispatcher.dispatch(
                        self.bot_id, (update, users, chats)
                    )

                if isinstance(diff, (raw.types.updates.Difference, raw.types.updates.ChannelDifference)):
                    break

            # Update local state
            state.pts = local_pts
            state.date = local_date
            state.seq = local_seq

            await bot.storage.update_state(state.to_tuple())

        log.info(
            "Bot %d: gap recovery complete — %d messages, %d updates",
            self.bot_id, msg_count, upd_count,
        )
        return (msg_count, upd_count)

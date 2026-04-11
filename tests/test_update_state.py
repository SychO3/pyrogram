"""Comprehensive tests for UpdateState and EntityState."""

from unittest.mock import AsyncMock, call

import pytest

from pyrogram.update_state import EntityState, UpdateState


# ── EntityState ───────────────────────────────────────────────────────

class TestEntityState:
    def test_creation_defaults(self):
        state = EntityState(entity_id=42)
        assert state.entity_id == 42
        assert state.pts == 0
        assert state.qts == 0
        assert state.date == 0
        assert state.seq == 0

    def test_creation_with_values(self):
        state = EntityState(entity_id=7, pts=100, qts=50, date=999, seq=10)
        assert state.entity_id == 7
        assert state.pts == 100
        assert state.qts == 50
        assert state.date == 999
        assert state.seq == 10

    def test_to_tuple(self):
        state = EntityState(entity_id=1, pts=2, qts=3, date=4, seq=5)
        assert state.to_tuple() == (1, 2, 3, 4, 5)

    def test_to_tuple_defaults(self):
        state = EntityState(entity_id=0)
        assert state.to_tuple() == (0, 0, 0, 0, 0)

    def test_from_tuple(self):
        t = (10, 20, 30, 40, 50)
        state = EntityState.from_tuple(t)
        assert state.entity_id == 10
        assert state.pts == 20
        assert state.qts == 30
        assert state.date == 40
        assert state.seq == 50

    def test_from_tuple_with_none_values(self):
        """None values in the tuple should be coerced to 0."""
        t = (5, None, None, None, None)
        state = EntityState.from_tuple(t)
        assert state.entity_id == 5
        assert state.pts == 0
        assert state.qts == 0
        assert state.date == 0
        assert state.seq == 0

    def test_from_tuple_partial_none(self):
        t = (3, 10, None, 77, None)
        state = EntityState.from_tuple(t)
        assert state.pts == 10
        assert state.qts == 0
        assert state.date == 77
        assert state.seq == 0

    def test_roundtrip(self):
        original = EntityState(entity_id=99, pts=1000, qts=500, date=12345, seq=88)
        restored = EntityState.from_tuple(original.to_tuple())
        assert restored.entity_id == original.entity_id
        assert restored.pts == original.pts
        assert restored.qts == original.qts
        assert restored.date == original.date
        assert restored.seq == original.seq


# ── UpdateState: get_or_create & global_state ─────────────────────────

class TestUpdateStateBasic:
    def test_creation(self):
        us = UpdateState(bot_id=1)
        assert us.bot_id == 1
        assert us.gap_count == 0
        assert us.all_states() == []

    def test_repr(self):
        us = UpdateState(bot_id=42)
        assert "bot_id=42" in repr(us)
        assert "entities=0" in repr(us)
        assert "gaps=0" in repr(us)

    def test_repr_with_entities_and_gaps(self):
        us = UpdateState(bot_id=1)
        us.get_or_create(0)
        us.get_or_create(100)
        # Force a gap
        us.apply_pts(0, 10, 1)   # first-time
        us.apply_pts(0, 20, 1)   # gap
        assert "entities=2" in repr(us)
        assert "gaps=1" in repr(us)

    def test_get_or_create_new(self):
        us = UpdateState(bot_id=1)
        state = us.get_or_create(42)
        assert isinstance(state, EntityState)
        assert state.entity_id == 42
        assert state.pts == 0

    def test_get_or_create_existing(self):
        us = UpdateState(bot_id=1)
        first = us.get_or_create(42)
        first.pts = 100
        second = us.get_or_create(42)
        assert second is first
        assert second.pts == 100

    def test_global_state_auto_creates(self):
        us = UpdateState(bot_id=1)
        gs = us.global_state
        assert gs.entity_id == 0
        # Accessing again returns the same object
        assert us.global_state is gs

    def test_get_entity_state_exists(self):
        us = UpdateState(bot_id=1)
        us.get_or_create(55)
        result = us.get_entity_state(55)
        assert result is not None
        assert result.entity_id == 55

    def test_get_entity_state_missing(self):
        us = UpdateState(bot_id=1)
        assert us.get_entity_state(999) is None


# ── UpdateState: remove_entity ────────────────────────────────────────

class TestRemoveEntity:
    def test_remove_existing(self):
        us = UpdateState(bot_id=1)
        us.get_or_create(42)
        us.remove_entity(42)
        assert us.get_entity_state(42) is None

    def test_remove_nonexistent(self):
        """Removing a non-existent entity should not raise."""
        us = UpdateState(bot_id=1)
        us.remove_entity(999)  # no error

    def test_remove_global(self):
        us = UpdateState(bot_id=1)
        _ = us.global_state  # creates entity 0
        us.remove_entity(0)
        assert us.get_entity_state(0) is None
        # Accessing global_state should recreate it
        gs = us.global_state
        assert gs.entity_id == 0
        assert gs.pts == 0


# ── UpdateState: all_states ───────────────────────────────────────────

class TestAllStates:
    def test_empty(self):
        us = UpdateState(bot_id=1)
        assert us.all_states() == []

    def test_multiple_entities(self):
        us = UpdateState(bot_id=1)
        us.get_or_create(0).pts = 10
        us.get_or_create(100).pts = 20
        us.get_or_create(200).pts = 30

        result = us.all_states()
        assert len(result) == 3
        # Each result is a 5-tuple
        ids = {t[0] for t in result}
        assert ids == {0, 100, 200}
        pts_map = {t[0]: t[1] for t in result}
        assert pts_map[0] == 10
        assert pts_map[100] == 20
        assert pts_map[200] == 30


# ── UpdateState: apply_pts ────────────────────────────────────────────

class TestApplyPts:
    def test_first_time_entity(self):
        """First time seeing an entity: just store pts, no gap."""
        us = UpdateState(bot_id=1)
        gap = us.apply_pts(entity_id=42, pts=100, pts_count=1)
        assert gap is False
        assert us.get_entity_state(42).pts == 100
        assert us.gap_count == 0

    def test_first_time_with_date_and_seq(self):
        us = UpdateState(bot_id=1)
        gap = us.apply_pts(entity_id=0, pts=50, pts_count=1, date=1700000000, seq=10)
        assert gap is False
        state = us.get_entity_state(0)
        assert state.pts == 50
        assert state.date == 1700000000
        assert state.seq == 10

    def test_normal_progression(self):
        """pts advances exactly by pts_count: no gap."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)  # first time
        gap = us.apply_pts(0, pts=11, pts_count=1)  # 10 + 1 = 11
        assert gap is False
        assert us.get_entity_state(0).pts == 11
        assert us.gap_count == 0

    def test_normal_progression_multi_count(self):
        """pts advances by pts_count > 1."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        gap = us.apply_pts(0, pts=15, pts_count=5)  # 10 + 5 = 15
        assert gap is False
        assert us.get_entity_state(0).pts == 15

    def test_normal_updates_date_and_seq(self):
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1, date=100, seq=1)
        us.apply_pts(0, pts=11, pts_count=1, date=200, seq=2)
        state = us.get_entity_state(0)
        assert state.date == 200
        assert state.seq == 2

    def test_gap_detected(self):
        """pts jumps more than expected: gap detected."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        gap = us.apply_pts(0, pts=20, pts_count=1)  # expected 11, got 20
        assert gap is True
        assert us.get_entity_state(0).pts == 20
        assert us.gap_count == 1

    def test_gap_updates_state(self):
        """Even on gap, pts/date/seq should be updated."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        us.apply_pts(0, pts=50, pts_count=1, date=777, seq=99)
        state = us.get_entity_state(0)
        assert state.pts == 50
        assert state.date == 777
        assert state.seq == 99

    def test_duplicate_old_pts(self):
        """pts < current pts: duplicate/old update, ignored."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        gap = us.apply_pts(0, pts=5, pts_count=1)
        assert gap is False
        assert us.get_entity_state(0).pts == 10  # unchanged

    def test_duplicate_same_pts(self):
        """pts == current pts (but not first time): treated as duplicate via fallthrough."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        # pts=10, pts_count=0 => expected=10, and pts==expected => normal progression
        # But let's test with pts_count=1 => expected=11, pts=10 < expected
        # Actually pts < state.pts check fails (10 not < 10), pts != expected (10 != 11)
        # pts > expected? 10 > 11? No. Falls through to bottom: duplicate.
        gap = us.apply_pts(0, pts=10, pts_count=1)
        assert gap is False
        assert us.get_entity_state(0).pts == 10

    def test_multiple_gaps_increment_counter(self):
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        us.apply_pts(0, pts=20, pts_count=1)   # gap 1
        us.apply_pts(0, pts=100, pts_count=1)  # gap 2
        assert us.gap_count == 2

    def test_channel_entity(self):
        """apply_pts works with channel entity_ids."""
        us = UpdateState(bot_id=1)
        channel_id = 1234567890
        us.apply_pts(channel_id, pts=5, pts_count=1)
        gap = us.apply_pts(channel_id, pts=6, pts_count=1)
        assert gap is False
        assert us.get_entity_state(channel_id).pts == 6

    def test_channel_gap(self):
        us = UpdateState(bot_id=1)
        channel_id = 999
        us.apply_pts(channel_id, pts=10, pts_count=1)
        gap = us.apply_pts(channel_id, pts=50, pts_count=1)
        assert gap is True
        assert us.gap_count == 1

    def test_optional_date_seq_not_overwritten_when_none(self):
        """When date/seq are None, existing values should not change."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1, date=100, seq=5)
        us.apply_pts(0, pts=11, pts_count=1)  # date=None, seq=None
        state = us.get_entity_state(0)
        assert state.date == 100  # preserved
        assert state.seq == 5    # preserved


# ── UpdateState: apply_seq ────────────────────────────────────────────

class TestApplySeq:
    def test_first_time(self):
        us = UpdateState(bot_id=1)
        gap = us.apply_seq(seq=10)
        assert gap is False
        assert us.global_state.seq == 10

    def test_normal_progression(self):
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        gap = us.apply_seq(seq=11)
        assert gap is False
        assert us.global_state.seq == 11

    def test_same_seq_no_change(self):
        """seq == stored seq: no update, no gap."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        gap = us.apply_seq(seq=10)
        assert gap is False
        assert us.global_state.seq == 10

    def test_gap_detected(self):
        """seq jumps: gap detected."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        gap = us.apply_seq(seq=15)
        assert gap is True
        assert us.global_state.seq == 15
        assert us.gap_count == 1

    def test_seq_start_no_gap(self):
        """seq_start == stored_seq + 1: no gap."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        gap = us.apply_seq(seq=12, seq_start=11)
        assert gap is False
        assert us.global_state.seq == 12

    def test_seq_start_gap(self):
        """seq_start > stored_seq + 1: gap."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        gap = us.apply_seq(seq=20, seq_start=15)
        assert gap is True
        assert us.global_state.seq == 20
        assert us.gap_count == 1

    def test_lower_seq_ignored(self):
        """seq < stored seq and start <= stored+1: no update."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        gap = us.apply_seq(seq=5)
        assert gap is False
        assert us.global_state.seq == 10  # unchanged

    def test_multiple_gaps(self):
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=1)
        us.apply_seq(seq=10)   # gap 1
        us.apply_seq(seq=50)   # gap 2
        assert us.gap_count == 2

    def test_seq_start_below_threshold_no_gap(self):
        """seq_start exactly at stored_seq+1 boundary: no gap."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=5)
        # start=6 is exactly stored+1=6, no gap
        gap = us.apply_seq(seq=8, seq_start=6)
        assert gap is False
        assert us.global_state.seq == 8


# ── UpdateState: apply_qts ────────────────────────────────────────────

class TestApplyQts:
    def test_first_time(self):
        us = UpdateState(bot_id=1)
        gap = us.apply_qts(qts=100)
        assert gap is False
        assert us.global_state.qts == 100

    def test_normal_progression(self):
        us = UpdateState(bot_id=1)
        us.apply_qts(qts=10)
        gap = us.apply_qts(qts=11)
        assert gap is False
        assert us.global_state.qts == 11

    def test_same_qts_no_change(self):
        us = UpdateState(bot_id=1)
        us.apply_qts(qts=10)
        gap = us.apply_qts(qts=10)
        assert gap is False
        assert us.global_state.qts == 10

    def test_gap_detected(self):
        """qts jumps by more than 1: gap."""
        us = UpdateState(bot_id=1)
        us.apply_qts(qts=10)
        gap = us.apply_qts(qts=15)
        assert gap is True
        assert us.global_state.qts == 15
        assert us.gap_count == 1

    def test_lower_qts_ignored(self):
        us = UpdateState(bot_id=1)
        us.apply_qts(qts=10)
        gap = us.apply_qts(qts=5)
        assert gap is False
        assert us.global_state.qts == 10

    def test_gap_exactly_two(self):
        """qts == stored + 2: gap (since threshold is stored + 1)."""
        us = UpdateState(bot_id=1)
        us.apply_qts(qts=10)
        gap = us.apply_qts(qts=12)
        assert gap is True
        assert us.gap_count == 1

    def test_multiple_gaps(self):
        us = UpdateState(bot_id=1)
        us.apply_qts(qts=1)
        us.apply_qts(qts=10)  # gap 1
        us.apply_qts(qts=50)  # gap 2
        assert us.gap_count == 2


# ── UpdateState: storage integration ──────────────────────────────────

class TestStorageIntegration:
    @pytest.mark.asyncio
    async def test_load_from_storage_empty(self):
        storage = AsyncMock()
        storage.update_state = AsyncMock(return_value=None)
        us = UpdateState(bot_id=1)
        await us.load_from_storage(storage)
        assert us.all_states() == []

    @pytest.mark.asyncio
    async def test_load_from_storage_empty_list(self):
        storage = AsyncMock()
        storage.update_state = AsyncMock(return_value=[])
        us = UpdateState(bot_id=1)
        await us.load_from_storage(storage)
        assert us.all_states() == []

    @pytest.mark.asyncio
    async def test_load_from_storage_with_data(self):
        raw = [
            (0, 100, 50, 1700000000, 10),
            (999, 200, 0, 0, 0),
        ]
        storage = AsyncMock()
        storage.update_state = AsyncMock(return_value=raw)
        us = UpdateState(bot_id=1)
        await us.load_from_storage(storage)

        global_s = us.get_entity_state(0)
        assert global_s is not None
        assert global_s.pts == 100
        assert global_s.qts == 50
        assert global_s.date == 1700000000
        assert global_s.seq == 10

        channel_s = us.get_entity_state(999)
        assert channel_s is not None
        assert channel_s.pts == 200

    @pytest.mark.asyncio
    async def test_load_from_storage_with_none_fields(self):
        raw = [(5, None, None, None, None)]
        storage = AsyncMock()
        storage.update_state = AsyncMock(return_value=raw)
        us = UpdateState(bot_id=1)
        await us.load_from_storage(storage)

        state = us.get_entity_state(5)
        assert state is not None
        assert state.pts == 0
        assert state.qts == 0

    @pytest.mark.asyncio
    async def test_save_to_storage(self):
        storage = AsyncMock()
        storage.update_state = AsyncMock()
        us = UpdateState(bot_id=1)
        us.get_or_create(0).pts = 10
        us.get_or_create(100).pts = 20

        await us.save_to_storage(storage)

        assert storage.update_state.await_count == 2
        saved_tuples = [c.args[0] for c in storage.update_state.call_args_list]
        saved_ids = {t[0] for t in saved_tuples}
        assert saved_ids == {0, 100}

    @pytest.mark.asyncio
    async def test_save_empty_state(self):
        storage = AsyncMock()
        storage.update_state = AsyncMock()
        us = UpdateState(bot_id=1)
        await us.save_to_storage(storage)
        storage.update_state.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_roundtrip_via_storage(self):
        """Save then load: values should be preserved."""
        saved_data = []

        async def mock_update_state(*args):
            if args:
                saved_data.append(args[0])
            else:
                return list(saved_data)

        storage = AsyncMock()
        storage.update_state = mock_update_state

        # Build state and save
        us1 = UpdateState(bot_id=1)
        us1.apply_pts(0, pts=50, pts_count=1, date=999, seq=7)
        us1.apply_pts(42, pts=200, pts_count=1)
        await us1.save_to_storage(storage)

        # Load into a new UpdateState
        us2 = UpdateState(bot_id=1)
        await us2.load_from_storage(storage)

        s0 = us2.get_entity_state(0)
        assert s0.pts == 50
        assert s0.date == 999
        assert s0.seq == 7

        s42 = us2.get_entity_state(42)
        assert s42.pts == 200


# ── Cross-cutting: gap count shared across all apply methods ──────────

class TestGapCountAcrossMethods:
    def test_gaps_accumulate_across_methods(self):
        """Gap counter is shared across apply_pts, apply_seq, apply_qts."""
        us = UpdateState(bot_id=1)

        # pts gap
        us.apply_pts(0, pts=10, pts_count=1)
        us.apply_pts(0, pts=50, pts_count=1)
        assert us.gap_count == 1

        # seq gap
        us.apply_seq(seq=1)
        us.apply_seq(seq=20)
        assert us.gap_count == 2

        # qts gap
        us.apply_qts(qts=1)
        us.apply_qts(qts=30)
        assert us.gap_count == 3

    def test_no_gaps_keeps_counter_zero(self):
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        us.apply_pts(0, pts=11, pts_count=1)
        us.apply_seq(seq=1)
        us.apply_seq(seq=2)
        us.apply_qts(qts=1)
        us.apply_qts(qts=2)
        assert us.gap_count == 0


# ── Edge cases ────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_multiple_entities_independent(self):
        """Different entities track pts independently."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        us.apply_pts(100, pts=500, pts_count=1)

        assert us.get_entity_state(0).pts == 10
        assert us.get_entity_state(100).pts == 500

        # Gap on one doesn't affect the other
        gap0 = us.apply_pts(0, pts=11, pts_count=1)
        gap100 = us.apply_pts(100, pts=600, pts_count=1)
        assert gap0 is False
        assert gap100 is True  # 500+1=501 expected, got 600

    def test_apply_pts_zero_pts_count(self):
        """pts_count=0 means expected_pts == current pts."""
        us = UpdateState(bot_id=1)
        us.apply_pts(0, pts=10, pts_count=1)
        # expected = 10 + 0 = 10, incoming = 10 => normal
        gap = us.apply_pts(0, pts=10, pts_count=0)
        assert gap is False

    def test_large_pts_values(self):
        """System handles large pts values correctly."""
        us = UpdateState(bot_id=1)
        large_pts = 2**31
        us.apply_pts(0, pts=large_pts, pts_count=1)
        gap = us.apply_pts(0, pts=large_pts + 1, pts_count=1)
        assert gap is False
        assert us.get_entity_state(0).pts == large_pts + 1

    def test_global_state_used_by_seq_and_qts(self):
        """apply_seq and apply_qts both modify the global (entity_id=0) state."""
        us = UpdateState(bot_id=1)
        us.apply_seq(seq=10)
        us.apply_qts(qts=20)

        gs = us.global_state
        assert gs.seq == 10
        assert gs.qts == 20
        assert gs.entity_id == 0

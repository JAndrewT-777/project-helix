# ADR-001: Video Frame Lookup

**Status:** Proposed  
**Date:** 2026-09-21  
**Related:** ADR-NNN

---

## Context

Efficient lookup for the frames across all video files. 

> ```text
> How should Helix do frame lookup?
>      It should use a global-sample-index for accessing the frames from the .mp4 files.
>      The two available options are: 
>      1. mapping the frames based on the frame time-stamp, the timestamp mapping is delivered
>         as part of the Cholec80 video files 
>      2. mapping frames based on the frame index
> ```

---

## Decision

Using the timestamp as the lookup key introduces a layer of imprecision that the frame-index approach avoids — worth flagging before you build __getitem__ around it.

**Why timestamp-based seeking is risky here**

1. **Video seek APIs are unreliable by timestamp, reliable by frame number.** 
   With **cv2.VideoCapture**, seeking via **cv2.CAP_PROP_POS_MSEC** is a known source of frame-drift bugs — many codecs (h264 in particular) only have keyframes at intervals and the container's timestamp-to-frame mapping isn't always exact, so **cap.set(CAP_PROP_POS_MSEC, t)** can land you a frame or two off from what you expect. Seeking via **cv2.CAP_PROP_POS_FRAMES (an integer frame index)** is deterministic and exact.

2. **You'd be reconstructing something you already have.** 
   The rows in each **videoNN-timestamp.txt/videoNN-phase.txt** are already in frame order — row 0 is frame 0, row 1 is frame 1, etc. (Cholec80's annotations are literally "one row per frame" at 25 fps). So timestamp in your load_timestamps() output is a derived value (_timestamp_to_seconds computed from frame_index / fps), not an independent identifier. Going global_idx → timestamp → frame means converting an exact integer index to a float, then trying to convert that float back into a frame index for seeking — a round-trip that can introduce off-by-one errors from floating point rounding, especially deep into long videos (Cholec80 videos run up to ~100 minutes, so accumulated fps rounding matters).

3. **The local frame index is already free.**
   Since you're flattening into one global array with contiguous per-video blocks (per the previous message), **local_frame_idx = global_idx - self.video_offsets[video_id]** gives you the exact frame number with zero reconstruction — no float math, no rounding risk.





**Suggested approach**
Keep timestamp as a stored/display column (useful for debugging, logging, sanity checks, matching against tool annotations' 1fps grid), but drive the actual video frame retrieval off the frame index, not the timestamp:


---

## Alternatives Considered

**{Option A}** — {why we rejected it}

**{Option B}** — {why we rejected it}

---

## Consequences

- (+) {what gets easier}
- (-) {what gets harder}
- (~) {side effect}

---

## Open Questions

- {Anything still unresolved}

---

## References

- {Link, spec, or related ADR}

#!/usr/bin/env python3
"""CUDA IPC Ring Buffer - True Zero-Copy GPU Memory Sharing.

This module implements a ring buffer using CUDA IPC for cross-process
GPU memory sharing with ZERO CPU copies after initial decode.

Architecture:
============

    Producer (Streaming Gateway)              Consumer (Inference Server)
    ┌─────────────────────────────┐          ┌─────────────────────────────┐
    │ 1. NVDEC decode (GPU)       │          │ 1. Read IPC handle from SHM │
    │ 2. NV12 resize (GPU)        │  ──────> │ 2. cudaIpcOpenMemHandle()   │
    │ 3. Write to GPU ring buffer │   SHM    │ 3. Access SAME GPU memory   │
    │ 4. Export IPC handle to SHM │ (64 bytes│ 4. NV12→RGB→CHW→FP16 kernel │
    └─────────────────────────────┘  only!)  │ 5. Send to TensorRT         │
                                             └─────────────────────────────┘

Requirements:
=============
    - CuPy with CUDA support
    - CUDA driver >= 450 (for IPC support)
    - Docker: --ipc=host OR same IPC namespace
    - Same GPU visibility across containers

Usage:
======
    # Producer (streaming gateway)
    ring = CudaIpcRingBuffer.create_producer("cam_001", gpu_id=0, height=960, width=640)
    ring.write_frame(nv12_frame)  # (H*1.5, W, 1) uint8

    # Consumer (inference server)
    ring = CudaIpcRingBuffer.connect_consumer("cam_001", gpu_id=0)
    nv12_frame = ring.read_latest()  # Zero-copy GPU access!
"""

import os
import mmap
import struct
import time
import logging
from typing import Optional, Tuple, Dict

import numpy as np

logger = logging.getLogger(__name__)

try:
    import cupy as cp
    from cupy.cuda import runtime as cuda_runtime
    CUPY_AVAILABLE = True
except ImportError:
    CUPY_AVAILABLE = False
    cp = None
    cuda_runtime = None

CUDA_IPC_HANDLE_SIZE = 64

class CudaIpcRingBuffer:
    """CUDA IPC Ring Buffer for zero-copy cross-process GPU memory sharing.

    This class manages a ring buffer stored entirely in GPU memory, with
    metadata stored in POSIX shared memory for cross-process coordination.
    """

    # Header layout:
    # 0-7:   write_idx (8 bytes)
    # 8-15:  read_idx (8 bytes) - legacy, unused
    # 16-23: frame_count (8 bytes)
    # 24-31: timestamp_ns (8 bytes)
    # 32-35: gpu_id (4 bytes)
    # 36-39: num_slots (4 bytes)
    # 40-43: width (4 bytes)
    # 44-47: height (4 bytes)
    # 48-51: channels (4 bytes)
    # 52-55: dtype_code (4 bytes)
    # 56-63: flags (8 bytes)
    # 64-127: ipc_handle (64 bytes)
    # 128-135: consumer_done_idx (8 bytes) - NEW: last frame idx consumer finished processing
    HEADER_SIZE = 136  # Increased to include consumer_done_idx
    SLOT_META_SIZE = 24

    def __init__(self, camera_id: str, gpu_id: int, num_slots: int,
                 width: int, height: int, channels: int, is_producer: bool):
        if not CUPY_AVAILABLE:
            raise RuntimeError("CuPy is required for CUDA IPC ring buffer")

        self.camera_id = camera_id
        self.gpu_id = gpu_id
        self.num_slots = num_slots
        self.width = width
        self.height = height
        self.channels = channels
        self.is_producer = is_producer

        self.frame_shape = (height, width, channels)
        self.frame_elements = height * width * channels
        self.frame_bytes = self.frame_elements
        self.total_gpu_bytes = self.frame_bytes * num_slots

        self.meta_shm_name = f"cuda_ipc_{camera_id}"
        self.meta_shm_path = f"/dev/shm/{self.meta_shm_name}"
        self.meta_size = self.HEADER_SIZE + (self.SLOT_META_SIZE * num_slots)

        self.gpu_buffer: Optional[cp.ndarray] = None
        self._meta_fd: Optional[int] = None
        self._meta_mmap: Optional[mmap.mmap] = None
        self._initialized = False
        self._cached_write_idx = 0
        self._write_event: Optional[cp.cuda.Event] = None
        self._last_consumer_ack = 0  # Track last acknowledged consumer idx

    @classmethod
    def create_producer(cls, camera_id: str, gpu_id: int = 0,
                        num_slots: int = 8, width: int = 640, height: int = 640,
                        channels: int = 1) -> "CudaIpcRingBuffer":
        """Create a producer ring buffer.

        For NV12: height should be H*1.5 (e.g., 960 for 640x640 frames), channels=1
        """
        rb = cls(camera_id, gpu_id, num_slots, width, height, channels, is_producer=True)
        rb.initialize()
        return rb

    @classmethod
    def connect_consumer(cls, camera_id: str, gpu_id: int = 0) -> "CudaIpcRingBuffer":
        """Connect as consumer."""
        with cp.cuda.Device(gpu_id):
            _ = cp.zeros(1, dtype=cp.uint8)

        meta_shm_path = f"/dev/shm/cuda_ipc_{camera_id}"

        try:
            fd = os.open(meta_shm_path, os.O_RDONLY, 0o666)
            mm = mmap.mmap(fd, 128, mmap.MAP_SHARED, mmap.PROT_READ)

            mm.seek(32)
            _ = struct.unpack("<I", mm.read(4))[0]  # gpu_id_stored
            num_slots = struct.unpack("<I", mm.read(4))[0]
            width = struct.unpack("<I", mm.read(4))[0]
            height = struct.unpack("<I", mm.read(4))[0]
            channels = struct.unpack("<I", mm.read(4))[0]

            mm.close()
            os.close(fd)

        except FileNotFoundError:
            raise FileNotFoundError(f"Ring buffer for {camera_id} not found. Start producer first.")

        rb = cls(camera_id, gpu_id, num_slots, width, height, channels, is_producer=False)
        rb.connect()
        return rb

    def initialize(self) -> bool:
        """Initialize as producer - allocate GPU memory and create SHM."""
        if not self.is_producer:
            raise RuntimeError("Use connect() for consumer")

        try:
            with cp.cuda.Device(self.gpu_id):
                total_shape = (self.num_slots,) + self.frame_shape
                self.gpu_buffer = cp.zeros(total_shape, dtype=cp.uint8)
                base_ptr = self.gpu_buffer.data.ptr
                ipc_handle = cuda_runtime.ipcGetMemHandle(base_ptr)
                self._write_event = cp.cuda.Event()

            self._create_meta_shm()
            self._write_header(ipc_handle)

            for slot in range(self.num_slots):
                self._write_slot_meta(slot, frame_idx=0, timestamp_ns=0, flags=0)

            self._initialized = True
            logger.info(f"Producer initialized: {self.camera_id}, "
                       f"{self.total_gpu_bytes / 1024 / 1024:.1f} MB GPU buffer")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize producer: {e}")
            return False

    def connect(self) -> bool:
        """Connect as consumer - import CUDA IPC handle."""
        if self.is_producer:
            raise RuntimeError("Use initialize() for producer")

        try:
            self._open_meta_shm()

            self._meta_mmap.seek(64)
            ipc_handle = self._meta_mmap.read(CUDA_IPC_HANDLE_SIZE)

            with cp.cuda.Device(self.gpu_id):
                _ = cp.zeros(1, dtype=cp.uint8)
                imported_ptr = cuda_runtime.ipcOpenMemHandle(ipc_handle)

                total_shape = (self.num_slots,) + self.frame_shape
                total_elements = int(np.prod(total_shape))

                mem = cp.cuda.UnownedMemory(imported_ptr, total_elements, owner=None)
                memptr = cp.cuda.MemoryPointer(mem, 0)
                self.gpu_buffer = cp.ndarray(total_shape, dtype=cp.uint8, memptr=memptr)

            self._initialized = True
            logger.info(f"Consumer connected: {self.camera_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect consumer: {e}")
            return False

    def _create_meta_shm(self):
        """Create POSIX SHM for metadata."""
        try:
            os.unlink(self.meta_shm_path)
        except FileNotFoundError:
            pass

        self._meta_fd = os.open(self.meta_shm_path, os.O_CREAT | os.O_RDWR, 0o666)
        os.ftruncate(self._meta_fd, self.meta_size)
        self._meta_mmap = mmap.mmap(
            self._meta_fd, self.meta_size,
            mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE
        )

    def _open_meta_shm(self):
        """Open existing POSIX SHM for metadata."""
        self._meta_fd = os.open(self.meta_shm_path, os.O_RDWR, 0o666)
        self._meta_mmap = mmap.mmap(
            self._meta_fd, self.meta_size,
            mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE
        )

    def _write_header(self, ipc_handle: bytes):
        """Write header to SHM."""
        header = struct.pack(
            "<QQQQIIIIIIQ",
            0,  # write_idx
            0,  # read_idx
            0,  # frame_count
            time.time_ns(),
            self.gpu_id,
            self.num_slots,
            self.width,
            self.height,
            self.channels,
            0,  # dtype_code (always uint8)
            0,  # flags
        )
        header += bytes(ipc_handle)[:CUDA_IPC_HANDLE_SIZE].ljust(CUDA_IPC_HANDLE_SIZE, b'\x00')
        # Add consumer_done_idx (8 bytes) at offset 128
        header += struct.pack("<Q", 0)  # consumer_done_idx = 0

        self._meta_mmap.seek(0)
        self._meta_mmap.write(header)

    def _read_consumer_done_idx(self) -> int:
        """Read consumer_done_idx - last frame index consumer finished processing."""
        self._meta_mmap.seek(128)
        return struct.unpack("<Q", self._meta_mmap.read(8))[0]

    def _write_consumer_done_idx(self, idx: int):
        """Write consumer_done_idx - called by consumer when done with a frame."""
        self._meta_mmap.seek(128)
        self._meta_mmap.write(struct.pack("<Q", idx))
        self._meta_mmap.flush()

    def _update_write_idx(self, write_idx: int, timestamp_ns: int):
        """Update write index atomically."""
        header_data = struct.pack("<QQQQ", write_idx, 0, write_idx, timestamp_ns)
        self._meta_mmap.seek(0)
        self._meta_mmap.write(header_data)
        self._meta_mmap.flush()

    def _read_write_idx(self) -> int:
        """Read current write index."""
        self._meta_mmap.seek(0)
        return struct.unpack("<Q", self._meta_mmap.read(8))[0]

    def _write_slot_meta(self, slot: int, frame_idx: int, timestamp_ns: int, flags: int):
        """Write slot metadata."""
        offset = self.HEADER_SIZE + (slot * self.SLOT_META_SIZE)
        data = struct.pack("<QQQ", frame_idx, timestamp_ns, flags)
        self._meta_mmap.seek(offset)
        self._meta_mmap.write(data)

    def _read_slot_meta(self, slot: int) -> Tuple[int, int, int]:
        """Read slot metadata."""
        offset = self.HEADER_SIZE + (slot * self.SLOT_META_SIZE)
        self._meta_mmap.seek(offset)
        data = self._meta_mmap.read(self.SLOT_META_SIZE)
        return struct.unpack("<QQQ", data)

    # =========================================================================
    # Producer Operations
    # =========================================================================

    def _is_slot_safe_to_write(self, frame_idx: int) -> bool:
        """Check if a slot is safe to overwrite (consumer has finished with it).

        A slot is safe if the consumer has acknowledged processing frames up to
        at least (frame_idx - num_slots), meaning the slot has been freed.
        """
        if frame_idx <= self.num_slots:
            # First round of slots, always safe
            return True

        consumer_done = self._read_consumer_done_idx()
        slot_last_frame = frame_idx - self.num_slots  # Frame that was in this slot before
        return consumer_done >= slot_last_frame

    def write_frame(self, gpu_frame: cp.ndarray, max_wait_ms: float = 10.0) -> int:
        """Write a frame to the ring buffer with overwrite protection.

        Args:
            gpu_frame: NV12 frame to write
            max_wait_ms: Maximum time to wait for slot to become safe (0 = no wait)

        Returns:
            Frame index, or -1 if slot was not safe and max_wait exceeded
        """
        if not self.is_producer:
            raise RuntimeError("write_frame() only for producer")
        if not self._initialized:
            raise RuntimeError("Producer not initialized")

        if gpu_frame.shape != self.frame_shape:
            raise ValueError(f"Shape mismatch: expected {self.frame_shape}, got {gpu_frame.shape}")

        next_frame_idx = self._cached_write_idx + 1

        # Wait for slot to be safe (consumer done with old frame in this slot)
        if max_wait_ms > 0 and not self._is_slot_safe_to_write(next_frame_idx):
            deadline = time.perf_counter() + (max_wait_ms / 1000.0)
            while not self._is_slot_safe_to_write(next_frame_idx):
                if time.perf_counter() >= deadline:
                    logger.warning(
                        f"Slot not safe for frame {next_frame_idx}, consumer_done={self._read_consumer_done_idx()}"
                    )
                    return -1  # Slot not safe, would overwrite unprocessed data
                time.sleep(0.0001)  # 100us spin

        self._cached_write_idx = next_frame_idx
        frame_idx = next_frame_idx
        slot = (frame_idx - 1) % self.num_slots

        with cp.cuda.Device(self.gpu_id):
            cp.copyto(self.gpu_buffer[slot], gpu_frame)
            self._write_event.record()
            self._write_event.synchronize()

        timestamp_ns = time.time_ns()
        self._write_slot_meta(slot, frame_idx, timestamp_ns, 0)
        self._update_write_idx(frame_idx, timestamp_ns)

        return frame_idx

    def write_frame_fast(self, gpu_frame: cp.ndarray, sync: bool = True) -> int:
        """Fast write - minimal overhead."""
        self._cached_write_idx += 1
        frame_idx = self._cached_write_idx
        slot = (frame_idx - 1) % self.num_slots

        cp.copyto(self.gpu_buffer[slot], gpu_frame)

        if sync:
            self._write_event.record()
            self._write_event.synchronize()

        self._update_write_idx(frame_idx, 0)
        return frame_idx

    def sync_writes(self):
        """Sync all pending writes."""
        if self._write_event is not None:
            self._write_event.record()
            self._write_event.synchronize()

    # =========================================================================
    # Consumer Operations
    # =========================================================================

    def read_frame(self, slot: int) -> Optional[cp.ndarray]:
        """Read a frame from a specific slot (NO COPY - view)."""
        if self.is_producer:
            raise RuntimeError("read_frame() only for consumer")
        if not self._initialized:
            raise RuntimeError("Consumer not connected")

        if slot < 0 or slot >= self.num_slots:
            return None

        return self.gpu_buffer[slot]

    def read_latest(self) -> Tuple[Optional[cp.ndarray], int]:
        """Read the most recently written frame (NO COPY - view)."""
        if self.is_producer:
            raise RuntimeError("read_latest() only for consumer")
        if not self._initialized:
            raise RuntimeError("Consumer not connected")

        write_idx = self._read_write_idx()
        if write_idx == 0:
            return None, -1

        slot = (write_idx - 1) % self.num_slots
        return self.gpu_buffer[slot], write_idx

    def ack_frame_done(self, frame_idx: int):
        """Acknowledge that consumer has finished processing up to frame_idx.

        CRITICAL: Call this AFTER stream.synchronize() to ensure GPU kernel
        has completed reading the frame data. This signals to the producer
        that slots used by frames <= frame_idx can be safely overwritten.

        Args:
            frame_idx: The highest frame index that has been fully processed
        """
        if self.is_producer:
            raise RuntimeError("ack_frame_done() only for consumer")
        if not self._initialized:
            raise RuntimeError("Consumer not connected")

        # Only update if this is higher than current ack
        current_ack = self._read_consumer_done_idx()
        if frame_idx > current_ack:
            self._write_consumer_done_idx(frame_idx)

    def get_consumer_done_idx(self) -> int:
        """Get the current consumer_done_idx (for debugging/monitoring)."""
        return self._read_consumer_done_idx()

    def get_write_idx(self) -> int:
        """Get current write index."""
        return self._read_write_idx()

    def get_status(self) -> Dict:
        """Get ring buffer status."""
        if not self._initialized:
            return {"initialized": False}

        return {
            "initialized": True,
            "camera_id": self.camera_id,
            "gpu_id": self.gpu_id,
            "write_idx": self._read_write_idx(),
            "num_slots": self.num_slots,
            "frame_shape": self.frame_shape,
            "gpu_buffer_mb": self.total_gpu_bytes / 1024 / 1024,
        }

    # =========================================================================
    # Cleanup
    # =========================================================================

    def close(self):
        """Close and cleanup resources."""
        if self._meta_mmap:
            self._meta_mmap.close()
            self._meta_mmap = None

        if self._meta_fd:
            os.close(self._meta_fd)
            self._meta_fd = None

        if self.is_producer:
            try:
                os.unlink(self.meta_shm_path)
            except FileNotFoundError:
                pass

        self.gpu_buffer = None
        self._initialized = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class GlobalFrameCounter:
    """Global atomic frame counter for event-driven notification.

    Instead of polling N ring buffers, consumers watch ONE counter.
    When counter changes → new frames available somewhere.
    """

    SHM_PATH = "/dev/shm/global_frame_counter"
    SIZE = 8

    def __init__(self, is_producer: bool = True):
        self.is_producer = is_producer
        self._fd: Optional[int] = None
        self._mmap: Optional[mmap.mmap] = None
        self._local_counter = 0

    def initialize(self) -> bool:
        """Initialize counter (producer)."""
        try:
            try:
                os.unlink(self.SHM_PATH)
            except FileNotFoundError:
                pass

            self._fd = os.open(self.SHM_PATH, os.O_CREAT | os.O_RDWR, 0o666)
            os.ftruncate(self._fd, self.SIZE)
            self._mmap = mmap.mmap(self._fd, self.SIZE, mmap.MAP_SHARED,
                                   mmap.PROT_READ | mmap.PROT_WRITE)
            self._mmap.write(struct.pack("<Q", 0))
            return True
        except Exception as e:
            logger.error(f"Failed to initialize counter: {e}")
            return False

    def connect(self) -> bool:
        """Connect to counter (consumer)."""
        try:
            self._fd = os.open(self.SHM_PATH, os.O_RDWR, 0o666)
            self._mmap = mmap.mmap(self._fd, self.SIZE, mmap.MAP_SHARED,
                                   mmap.PROT_READ | mmap.PROT_WRITE)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to counter: {e}")
            return False

    def increment(self) -> int:
        """Increment and return new value."""
        self._local_counter += 1
        self._mmap.seek(0)
        self._mmap.write(struct.pack("<Q", self._local_counter))
        return self._local_counter

    def get(self) -> int:
        """Get current value."""
        self._mmap.seek(0)
        return struct.unpack("<Q", self._mmap.read(8))[0]

    def wait_for_change(self, last_value: int, timeout_ms: float = 100.0) -> Tuple[int, bool]:
        """Wait for counter to change."""
        deadline = time.perf_counter() + (timeout_ms / 1000.0)

        while True:
            current = self.get()
            if current != last_value:
                return current, True

            if time.perf_counter() >= deadline:
                return current, False

            time.sleep(0.00005)

    def close(self):
        """Close counter."""
        if self._mmap:
            self._mmap.close()
        if self._fd:
            os.close(self._fd)
        self._mmap = None
        self._fd = None


def benchmark_cuda_ipc():
    """Benchmark CUDA IPC ring buffer performance."""
    if not CUPY_AVAILABLE:
        print("CuPy not available")
        return

    print("\n" + "=" * 70)
    print("CUDA IPC RING BUFFER BENCHMARK")
    print("=" * 70)

    cam_id = "bench_cam"
    num_frames = 10000

    # NV12 dimensions: H*1.5 for 640x640 = 960x640
    producer = CudaIpcRingBuffer.create_producer(
        cam_id, gpu_id=0, num_slots=8,
        width=640, height=960, channels=1  # NV12: (H*1.5, W, 1)
    )

    with cp.cuda.Device(0):
        test_frame = cp.random.randint(0, 256, (960, 640, 1), dtype=cp.uint8)

        for _ in range(100):
            producer.write_frame(test_frame)
        cp.cuda.Stream.null.synchronize()

        print("\n--- GPU → GPU Write (Zero-Copy Ring Buffer) ---")
        start = time.perf_counter()
        for _ in range(num_frames):
            producer.write_frame(test_frame)
        cp.cuda.Stream.null.synchronize()
        elapsed = time.perf_counter() - start

        fps = num_frames / elapsed
        latency_us = (elapsed / num_frames) * 1e6
        bandwidth_gbps = (fps * 960 * 640) / 1e9

        print(f"  FPS: {fps:,.0f}")
        print(f"  Latency: {latency_us:.2f} µs/frame")
        print(f"  Bandwidth: {bandwidth_gbps:.2f} GB/s")

    producer.close()

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    benchmark_cuda_ipc()

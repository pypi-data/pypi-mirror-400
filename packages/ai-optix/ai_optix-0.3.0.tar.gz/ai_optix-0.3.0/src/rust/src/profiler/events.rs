// SPDX-FileCopyrightText: 2025 ai-foundation-software
// SPDX-License-Identifier: Apache-2.0

#[repr(C)]
#[derive(Clone, Copy, Debug)]
pub enum MetricKind {
    CpuUsageVcore(u16), // scaled by 100
    MemoryUsageMb(u32),
    GpuPowerW(u16),
    GpuTempC(i16),
    GpuUtil(u8),
    KernelStart { id: u64, payload: u64 },
    KernelEnd { id: u64, payload: u64 },
}

#[derive(Clone, Copy, Debug)]
pub struct MetricEvent {
    pub timestamp_ns: u64, // Relative to session start
    pub kind: MetricKind,
}

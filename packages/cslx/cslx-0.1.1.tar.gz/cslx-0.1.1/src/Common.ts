export type KernelStatus = 'connected' | 'available' | 'pending' | 'rejected';

export interface KernelSpecItem {
  id: string;
  name: string;
  status: KernelStatus;
  metadata?: string[];
  url?: string;
  token?: string;
}

export interface KernelRequest {
  name: string;
  allocation: string;
  computeResource: string;
  queue: string;
  nodeCount: number;
  coreCount: number;
  wallMinutes: number;
  memoryMB: number;
}
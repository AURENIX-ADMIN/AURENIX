'use server';

import { getTemporalClient } from '@/lib/temporal';

export async function approveWorkflow(workflowId: string, feedback: string = '') {
  try {
    const client = await getTemporalClient();
    const handle = client.workflow.getHandle(workflowId);
    
    await handle.signal('submit_approval', 'APPROVED', feedback);
    
    return { success: true };
  } catch (error) {
    console.error('Failed to approve workflow:', error);
    return { success: false, error: 'Failed to send approval signal' };
  }
}

export async function rejectWorkflow(workflowId: string, feedback: string = '') {
  try {
    const client = await getTemporalClient();
    const handle = client.workflow.getHandle(workflowId);
    
    await handle.signal('submit_approval', 'REJECTED', feedback);
    
    return { success: true };
  } catch (error) {
    console.error('Failed to reject workflow:', error);
    return { success: false, error: 'Failed to send rejection signal' };
  }
}

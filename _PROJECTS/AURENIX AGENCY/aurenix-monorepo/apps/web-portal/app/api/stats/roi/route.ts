import { NextResponse } from 'next/server';
import { prisma } from '@aurenix/data-layer';
import { auth } from '@clerk/nextjs/server';

export async function GET() {
  const { sessionClaims } = await auth();
  const organizationId = sessionClaims?.org_id as string;

  if (!organizationId) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  // 1. Calculate Costs (Total credit consumption or subscription cost)
  const usageRecords = await prisma.usageRecord.findMany({
    where: {
      organization_id: organizationId,
      timestamp: {
        gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1), // Start of month
      },
    },
  });

  const totalCreditsUsed = usageRecords.reduce((sum, record) => sum + (record.cost_credits?.toNumber() || 0), 0);
  // Assuming 1 credit = 1 cent for simplicity in calculation, or fixed rate
  const costEuro = totalCreditsUsed * 0.10; // e.g. 0.10€ per credit

  // 2. Calculate Savings (Time saved * Hourly Rate)
  const metrics = await prisma.organizationMetric.findFirst({
    where: {
      organization_id: organizationId,
      date: {
        gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
      },
    },
  });

  const hoursSaved = metrics?.time_saved_hours || 0;
  const savingsEuro = hoursSaved * 150; // Average rate of 150€/hr

  return NextResponse.json({
    spent: costEuro,
    saved: savingsEuro,
    hoursSaved,
    roi: costEuro > 0 ? savingsEuro / costEuro : 0,
  });
}

import { NextResponse } from 'next/server';
import { prisma } from '@aurenix/data-layer';
import { auth } from '@clerk/nextjs/server';

export async function POST(req: Request) {
  const { sessionClaims, userId } = await auth();
  const organizationId = sessionClaims?.org_id as string;

  if (!organizationId || !userId) {
    return new NextResponse('Unauthorized', { status: 401 });
  }

  try {
    const { prompt, completion, correction, rating, metadata } = await req.json();

    const feedback = await prisma.aiFeedback.create({
      data: {
        organization_id: organizationId,
        user_id: userId,
        prompt,
        completion,
        correction,
        rating,
        metadata: metadata || {},
      },
    });

    return NextResponse.json(feedback);
  } catch (error: any) {
    return new NextResponse(`Error saving feedback: ${error.message}`, { status: 500 });
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@aurenix/data-layer';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, email, phone, company, message, source, metadata } = body;

    if (!name || !email) {
      return NextResponse.json({ error: 'Name and email are required' }, { status: 400 });
    }

    // Check for existing lead to avoid duplicates
    const existingLead = await prisma.lead.findFirst({
      where: { email },
    });

    if (existingLead) {
      return NextResponse.json({ message: 'Lead already exists' }, { status: 409 });
    }

    const lead = await prisma.lead.create({
      data: {
        name,
        email,
        phone,
        company,
        notes: message,
        source: source || 'WEBSITE',
        // In a real scenario, we might want to store metadata as JSON
      },
    });

    return NextResponse.json({ success: true, lead }, { status: 201 });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

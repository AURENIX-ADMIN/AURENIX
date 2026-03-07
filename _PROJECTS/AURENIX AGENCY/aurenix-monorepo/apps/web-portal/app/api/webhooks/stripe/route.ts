import { NextResponse } from 'next/server';
import { headers } from 'next/headers';
import { getStripeClient } from '@aurenix/billing';
import { prisma } from '@aurenix/data-layer';
import Stripe from 'stripe';

export async function POST(req: Request) {
  const body = await req.text();
  const signature = headers().get('Stripe-Signature') as string;

  if (!signature) {
    console.error('[Stripe Webhook] Missing signature');
    return new NextResponse('Missing signature', { status: 400 });
  }

  const stripe = await getStripeClient();
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    console.error('[Stripe Webhook] Missing STRIPE_WEBHOOK_SECRET');
    return new NextResponse('Webhook secret not configured', { status: 500 });
  }

  let event: Stripe.Event;

  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err: any) {
    console.error('[Stripe Webhook] Signature verification failed:', err.message);
    return new NextResponse(`Webhook Error: ${err.message}`, { status: 400 });
  }

  console.log(`[Stripe Webhook] Received event: ${event.type}`);

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        await handleCheckoutCompleted(session, stripe);
        break;
      }

      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionUpdated(subscription);
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionDeleted(subscription);
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentSucceeded(invoice);
        break;
      }

      case 'invoice.payment_failed': {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentFailed(invoice);
        break;
      }

      default:
        console.log(`[Stripe Webhook] Unhandled event type: ${event.type}`);
    }

    return new NextResponse(JSON.stringify({ received: true }), { status: 200 });
  } catch (error) {
    console.error('[Stripe Webhook] Handler error:', error);
    return new NextResponse('Webhook handler failed', { status: 500 });
  }
}

async function handleCheckoutCompleted(session: Stripe.Checkout.Session, stripe: Stripe) {
  console.log('[Stripe Webhook] Processing checkout.session.completed:', session.id);

  const organizationId = session.metadata?.organizationId;
  const userId = session.metadata?.userId;
  const stripeSubscriptionId = session.subscription as string;
  const stripeCustomerId = session.customer as string;

  if (!organizationId) {
    console.error('[Stripe Webhook] No organizationId in metadata');
    return;
  }

  // Get subscription details for tier info
  const subscription = await stripe.subscriptions.retrieve(stripeSubscriptionId);
  const priceId = subscription.items.data[0]?.price.id;
  const productId = subscription.items.data[0]?.price.product as string;
  const product = await stripe.products.retrieve(productId);

  const tierName = product.metadata?.tier || product.name || 'PRO';

  // Upsert subscription
  await prisma.subscription.upsert({
    where: { organization_id: organizationId as string },
    update: {
      stripe_id: stripeSubscriptionId,
      stripe_customer_id: stripeCustomerId,
      stripe_price_id: priceId,
      status: 'ACTIVE',
      tier: tierName,
      current_period_start: new Date(subscription.current_period_start * 1000),
      current_period_end: new Date(subscription.current_period_end * 1000),
    },
    create: {
      organization_id: organizationId,
      stripe_id: stripeSubscriptionId,
      stripe_customer_id: stripeCustomerId,
      stripe_price_id: priceId,
      status: 'ACTIVE',
      plan_id: session.metadata?.planId || 'PRO',
      tier: tierName,
      current_period_start: new Date(subscription.current_period_start * 1000),
      current_period_end: new Date(subscription.current_period_end * 1000),
    },
  });

  // Initialize credit balance for new subscriptions
  await prisma.creditBalance.upsert({
    where: { organization_id: organizationId },
    update: {
      // Add credits on renewal if needed
    },
    create: {
      organization_id: organizationId,
      balance: 10000, // Initial credits based on tier
    },
  });

  console.log(`[Stripe Webhook] Subscription activated for org: ${organizationId}`);
}

async function handleSubscriptionUpdated(subscription: Stripe.Subscription) {
  console.log('[Stripe Webhook] Processing subscription update:', subscription.id);

  const status = mapStripeStatus(subscription.status);

  await prisma.subscription.updateMany({
    where: { stripe_id: subscription.id },
    data: {
      status,
      current_period_start: new Date(subscription.current_period_start * 1000),
      current_period_end: new Date(subscription.current_period_end * 1000),
      cancel_at_period_end: subscription.cancel_at_period_end,
    },
  });
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  console.log('[Stripe Webhook] Processing subscription deletion:', subscription.id);

  await prisma.subscription.updateMany({
    where: { stripe_id: subscription.id },
    data: {
      status: 'CANCELED',
      canceled_at: new Date(),
    },
  });
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  console.log('[Stripe Webhook] Payment succeeded for invoice:', invoice.id);

  // Log successful payment for audit
  // Optionally create invoice record in your database
  if (invoice.subscription) {
    await prisma.subscription.updateMany({
      where: { stripe_id: invoice.subscription as string },
      data: { status: 'ACTIVE' },
    });
  }
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  console.log('[Stripe Webhook] Payment failed for invoice:', invoice.id);

  // Mark subscription as past_due
  if (invoice.subscription) {
    await prisma.subscription.updateMany({
      where: { stripe_id: invoice.subscription as string },
      data: { status: 'PAST_DUE' },
    });
  }

  // TODO: Send notification email to customer
}

function mapStripeStatus(stripeStatus: Stripe.Subscription.Status): string {
  const statusMap: Record<string, string> = {
    active: 'ACTIVE',
    past_due: 'PAST_DUE',
    canceled: 'CANCELED',
    unpaid: 'PAST_DUE',
    trialing: 'TRIALING',
    incomplete: 'INCOMPLETE',
    incomplete_expired: 'CANCELED',
    paused: 'PAUSED',
  };
  return statusMap[stripeStatus] || 'ACTIVE';
}


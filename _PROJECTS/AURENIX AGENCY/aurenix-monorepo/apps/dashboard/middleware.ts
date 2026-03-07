import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Auth middleware — currently open for internal use
// To enable Clerk auth: uncomment the import and export below
// import { clerkMiddleware } from "@clerk/nextjs/server";
// export default clerkMiddleware();

export function middleware(request: NextRequest) {
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};

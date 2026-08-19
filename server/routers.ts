import { COOKIE_NAME } from "@shared/const";
import { z } from "zod";
import { createPersonalNote, deletePersonalNote, listPersonalNotes, updatePersonalNote } from "./db";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { noteDraftSchema, noteUpdateSchema } from "./noteSchemas";

export const appRouter = router({
    // if you need to use socket.io, read and register route in server/_core/index.ts, all api should start with '/api/' so that the gateway can route correctly
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),
  notes: router({
    list: protectedProcedure.query(({ ctx }) => listPersonalNotes(ctx.user.id)),
    create: protectedProcedure.input(noteDraftSchema).mutation(({ ctx, input }) => createPersonalNote(ctx.user.id, input)),
    update: protectedProcedure.input(noteUpdateSchema).mutation(({ ctx, input }) => {
      const { id, ...note } = input;
      return updatePersonalNote(ctx.user.id, id, note);
    }),
    delete: protectedProcedure.input(z.object({ id: z.number().int().positive() })).mutation(({ ctx, input }) => deletePersonalNote(ctx.user.id, input.id)),
  }),
});

export type AppRouter = typeof appRouter;

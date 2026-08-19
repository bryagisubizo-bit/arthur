import { z } from "zod";

export const noteCategorySchema = z.enum(["self", "people", "general"]);
export const learningStateSchema = z.enum(["draft", "studying", "held"]);
export const captureMethodSchema = z.enum(["typed", "voice_edit"]);

export const noteDraftSchema = z.object({
  category: noteCategorySchema,
  title: z.string().trim().min(1, "A short note title is required.").max(160),
  content: z.string().trim().min(1, "Write a note before saving.").max(12_000),
  learningState: learningStateSchema.default("draft"),
  captureMethod: captureMethodSchema.default("typed"),
});

export const noteUpdateSchema = noteDraftSchema.extend({
  id: z.number().int().positive(),
});

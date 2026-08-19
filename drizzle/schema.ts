import { index, int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/** Private, user-owned notes. Content is never shared across accounts. */
export const personalNotes = mysqlTable("personal_notes", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("user_id").notNull(),
  category: mysqlEnum("category", ["self", "people", "general"]).notNull().default("general"),
  title: varchar("title", { length: 160 }).notNull(),
  content: text("content").notNull(),
  learningState: mysqlEnum("learning_state", ["draft", "studying", "held"]).notNull().default("draft"),
  captureMethod: mysqlEnum("capture_method", ["typed", "voice_edit"]).notNull().default("typed"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
}, (table) => [index("personal_notes_user_updated_idx").on(table.userId, table.updatedAt)]);

export type PersonalNote = typeof personalNotes.$inferSelect;
export type InsertPersonalNote = typeof personalNotes.$inferInsert;

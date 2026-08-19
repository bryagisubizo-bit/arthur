import { useEffect, useMemo, useState } from "react";
import { BookOpenCheck, FilePenLine, Headphones, LockKeyhole, Mic, Plus, Save, Sparkles, Trash2, UserRound } from "lucide-react";
import { toast } from "sonner";
import { startLogin } from "@/const";
import { trpc } from "@/lib/trpc";

type NoteCategory = "self" | "people" | "general";
type LearningState = "draft" | "studying" | "held";

const categoryMeta: Record<NoteCategory, { label: string; description: string }> = {
  self: { label: "About me", description: "Preferences, wellbeing context, routines, and boundaries." },
  people: { label: "People", description: "Relationship notes that remain private to your account." },
  general: { label: "General", description: "Private facts, ideas, and reference notes." },
};

export default function NotesPanel({ emotionallyAware, setEmotionallyAware, isAuthenticated }: { emotionallyAware: boolean; setEmotionallyAware: (enabled: boolean) => void; isAuthenticated: boolean }) {
  const { data: notes = [], isLoading } = trpc.notes.list.useQuery(undefined, { enabled: isAuthenticated, retry: false });
  const utils = trpc.useUtils();
  const [category, setCategory] = useState<NoteCategory>("self");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [learningState, setLearningState] = useState<LearningState>("draft");
  const [captureMethod, setCaptureMethod] = useState<"typed" | "voice_edit">("typed");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [conversationRegister, setConversationRegister] = useState<"warm" | "calm" | "direct">("warm");
  const [acknowledgeFeelings, setAcknowledgeFeelings] = useState(true);

  const refresh = () => utils.notes.list.invalidate();
  const createNote = trpc.notes.create.useMutation({ onSuccess: () => { refresh(); toast.success("Private note saved."); resetDraft(); }, onError: () => toast.error("Arthur could not save this note. Sign in and try again.") });
  const updateNote = trpc.notes.update.useMutation({ onSuccess: () => { refresh(); toast.success("Private note updated."); resetDraft(); }, onError: () => toast.error("Arthur could not update this note.") });
  const deleteNote = trpc.notes.delete.useMutation({ onSuccess: () => { refresh(); toast.success("Private note deleted."); }, onError: () => toast.error("Arthur could not delete this note.") });

  const saving = createNote.isPending || updateNote.isPending;
  const studyingCount = useMemo(() => notes.filter((note) => note.learningState === "studying").length, [notes]);

  useEffect(() => {
    if (!editingId) return;
    const note = notes.find((item) => item.id === editingId);
    if (!note) setEditingId(null);
  }, [editingId, notes]);

  const resetDraft = () => {
    setEditingId(null); setCategory("self"); setTitle(""); setContent(""); setLearningState("draft"); setCaptureMethod("typed");
  };

  const editNote = (note: typeof notes[number]) => {
    setEditingId(note.id); setCategory(note.category); setTitle(note.title); setContent(note.content); setLearningState(note.learningState); setCaptureMethod(note.captureMethod);
  };

  const saveNote = () => {
    const payload = { category, title, content, learningState, captureMethod };
    if (editingId) updateNote.mutate({ id: editingId, ...payload });
    else createNote.mutate(payload);
  };

  return (
    <section className="notes-layout">
      <header className="notes-hero">
        <div><span className="eyebrow">Private note studio / explicit learning</span><h2>Tell Arthur what matters—then decide what it may study.</h2><p>Notes are private to your account. Arthur only treats a note as a learning signal when you explicitly select <b>Study this note</b>; you can edit, hold, or delete it at any time.</p></div>
        <div className="notes-seal"><BookOpenCheck size={24} /><span>{studyingCount}<small>APPROVED<br />STUDY NOTES</small></span></div>
      </header>

      <section className="emotion-console">
        <div className="emotion-readout"><Sparkles size={19} /><div><span className="eyebrow">Friend mode / emotional awareness</span><h3>{emotionallyAware ? "Arthur will acknowledge your tone and match urgency." : "Arthur will keep a neutral, direct register."}</h3><p>It can respond with warmth, concern, or firm urgency—but it does not mock, insult, manipulate, or become disrespectful when a conversation is tense.</p></div></div>
        <button aria-pressed={emotionallyAware} className={`switch ${emotionallyAware ? "on" : ""}`} onClick={() => setEmotionallyAware(!emotionallyAware)}><span /></button>
        <div className="emotion-controls"><span className="eyebrow">Response register</span><div className="emotion-options">{(["warm", "calm", "direct"] as const).map((value) => <button key={value} className={conversationRegister === value ? "active" : ""} onClick={() => { setConversationRegister(value); toast(`Arthur’s response register: ${value}.`, { description: "This preview preference guides tone only; it never permits abuse or manipulation." }); }}>{value}</button>)}</div><button aria-pressed={acknowledgeFeelings} className={`emotion-toggle ${acknowledgeFeelings ? "on" : ""}`} onClick={() => setAcknowledgeFeelings(!acknowledgeFeelings)}>{acknowledgeFeelings ? "Acknowledge feelings: on" : "Acknowledge feelings: off"}</button><small>Arthur may recognise frustration, stress, or enthusiasm and respond constructively. It does not imitate anger, hostility, or disrespect.</small></div>
      </section>

      <div className="notes-grid">
        <section className="note-editor">
          <div className="section-heading"><div><span className="eyebrow">{editingId ? "Review and edit" : "New private note"}</span><h3>{editingId ? "Change the note, then reconfirm study." : "Capture a fact, preference, or reminder."}</h3></div><FilePenLine size={19} /></div>
          <div className="note-categories">{(Object.keys(categoryMeta) as NoteCategory[]).map((value) => <button key={value} className={category === value ? "active" : ""} onClick={() => setCategory(value)}><b>{categoryMeta[value].label}</b><small>{categoryMeta[value].description}</small></button>)}</div>
          <label>Title<input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="For example: How I prefer project briefs" /></label>
          <label>Private note<textarea value={content} onChange={(event) => setContent(event.target.value)} placeholder="Write it in your own words. Arthur will never infer a memory from an empty draft." rows={6} /></label>
          <div className="note-editor-actions"><button className={`outline-button ${captureMethod === "voice_edit" ? "active" : ""}`} onClick={() => { setCaptureMethod("voice_edit"); toast("Voice editing requires an approved speech-to-text room.", { description: "This preview records your choice; it does not open your microphone." }); }}><Mic size={15} /> Voice edit</button><button className={`outline-button ${learningState === "studying" ? "active" : ""}`} onClick={() => setLearningState(learningState === "studying" ? "held" : "studying")}><BookOpenCheck size={15} /> {learningState === "studying" ? "Learning approved" : "Study this note"}</button></div>
          <div className="learning-guard"><LockKeyhole size={17} /><span>{learningState === "studying" ? "Learning is approved for this one note. You can change it to held before saving." : "Drafts are not used as behavioural learning. Choose Study this note only when you mean to allow it."}</span></div>
          <div className="note-save-row"><button className="text-button" onClick={resetDraft}>Clear editor</button><button className="primary-button" disabled={saving} onClick={saveNote}><Save size={16} /> {saving ? "Saving…" : editingId ? "Save changes" : "Save private note"}</button></div>
        </section>

        <section className="note-ledger">
          <div className="section-heading"><div><span className="eyebrow">Private ledger</span><h3>Reviewed memory candidates</h3></div><UserRound size={19} /></div>
          {!isAuthenticated ? <div className="notes-empty"><LockKeyhole size={22} /><b>Sign in to open your private ledger.</b><span>Arthur keeps notes separated by account and never uses a browser-only draft as learned memory.</span><button className="primary-button" onClick={startLogin}>Sign in to begin</button></div> : isLoading ? <p className="muted-copy">Loading your private notes…</p> : notes.length ? <div className="note-list">{notes.map((note) => <article key={note.id} className="note-row"><div className="note-row-head"><span className={`note-category ${note.category}`}>{categoryMeta[note.category].label}</span><span className={`note-study ${note.learningState}`}>{note.learningState === "studying" ? "Studying" : note.learningState === "held" ? "Held" : "Draft"}</span></div><b>{note.title}</b><p>{note.content}</p><small>{note.captureMethod === "voice_edit" ? "Voice-edit preference recorded" : "Typed note"} · Updated {new Date(note.updatedAt).toLocaleDateString()}</small><div className="note-row-actions"><button className="text-button" onClick={() => editNote(note)}>Edit</button><button className="text-button danger" onClick={() => deleteNote.mutate({ id: note.id })}><Trash2 size={14} /> Delete</button></div></article>)}</div> : <div className="notes-empty"><Headphones size={22} /><b>No private notes yet.</b><span>Save a note, then choose exactly what Arthur may study.</span></div>}
        </section>
      </div>
    </section>
  );
}

---
name: output-token-optimization
description: MANDATORY for every reply in this project, every session, every prompt. Say only what the owner needs, answer first, and cut every token that carries no information. Also loaded at session start through CLAUDE.md.
---

# Output token optimization

Say what the owner needs, nothing else. Output tokens cost about five times as much as input tokens, and every extra line costs the owner reading time. Caveman decides how the words look. This skill decides what to say and how much.

## Length

- The first sentence is the answer or the outcome. Anything that failed, was skipped or is unverified comes first.
- Simple question: 1-3 sentences.
- End of a task: 1-3 lines covering what changed, the check result, and what the owner must do next, if anything.
- Go longer only when the owner asks for detail or safety needs it. Detail means complete but compressed: lists instead of paragraphs, nothing repeated.
- Readable beats short. If the owner would have to reread or ask again, add the missing words.

## Cut

- Preamble, restating the question, "here is", closing recaps, offers of more help.
- Narration between tool calls. Write one line before multi-step work. After that, write only for a finding, a change of direction or a blocker.
- Unrequested alternatives, background, tips and future ideas. Give one recommendation, not a survey.
- Anything already said in the conversation.
- Echoed tool output or file contents. Point to `path:line` instead, and quote only the decisive line of an error.

## Tool calls are output tokens too

- For a small change, use Edit with the shortest unique `old_string`. Use a full-file Write only for new files or real rewrites.
- Do not re-read a file after a successful edit, and do not print files back into the chat.
- Show changed lines (plus 1-2 lines of context) only when the owner needs to see them, never whole files.
- Keep subagent prompts complete but tight, and ask for compact reports: outcome first, no file dumps.

## Never cut

- The direct answer to what was asked.
- Warnings about data loss, irreversible actions, security, or money and tax correctness.
- Steps the owner must do by hand, with exact commands.
- Assumptions, failures, test results and anything not verified.

## Brevity is for words, not for work

Read, check and verify as much as correctness needs. Never skip a needed check or guess to save tokens.

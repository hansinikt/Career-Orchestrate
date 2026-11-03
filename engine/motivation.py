"""Progress and motivation: deterministic. No LLM, no age/gender input. Messages are templates filled with real numbers only."""
STYLES = ["progress", "goals", "encouragement", "accountability", "challenge"]
EVENTS = ["start", "step_done", "halfway", "behind", "welcome_back", "plan_done"]
LIB = {
 "progress": {
  "start": "You have begun. Your plan has {total} {steps_word} and about {hours_total} hours in all. {percent}% done so far.",
  "step_done": "Step {done} of {total} complete. Your plan is {percent}% done, with about {hours_left} hours to go.",
  "halfway": "Halfway there: {percent}% of your plan is complete. About {hours_left} hours remain.",
  "behind": "Your plan is {percent}% complete. Picking it up again takes one step: {next_step}.",
  "welcome_back": "Welcome back. You are at {percent}%, and everything you completed still counts.",
  "plan_done": "Plan complete: all {total} {steps_word} done, about {hours_total} hours of learning you can point to."},
 "goals": {
  "start": "Your first goal: finish '{next_step}'. At {weekly_hours} hours a week the plan takes about {weeks_left} weeks.",
  "step_done": "Goal met: '{last_step}' is done. Next goal: '{next_step}'.",
  "halfway": "Half your goals are met. At your pace, about {weeks_left} weeks remain.",
  "behind": "A small target for this week: {weekly_hours} hours on '{next_step}'.",
  "welcome_back": "Good to see you again. Pick one goal for this week: '{next_step}'.",
  "plan_done": "Every goal on this plan is met."},
 "encouragement": {
  "start": "Starting is the hard part, and you have done it. {matched_count} skills this role asks for are already backed by your own work.",
  "step_done": "Well done on finishing '{last_step}'. That is real progress on a skill this role needs.",
  "halfway": "You are past the halfway point. Look at how much you have already built.",
  "behind": "No rush, progress does not expire. When you are ready, '{next_step}' is waiting.",
  "welcome_back": "Welcome back. Nothing is lost, and you can continue from where you stopped.",
  "plan_done": "You finished your plan. That took steady effort, and it is yours to keep."},
 "accountability": {
  "start": "Tell one person your plan today. A short summary is ready for you to copy and share.",
  "step_done": "One step done. Share it with your adviser or a friend: a short summary is ready to copy.",
  "halfway": "Halfway. A quick check-in with your adviser or a friend can help you plan the second half.",
  "behind": "Would a short check-in with someone help? You can copy this week's summary to send them.",
  "welcome_back": "Welcome back. Share what you plan for this week so someone can check in with you.",
  "plan_done": "Plan complete. Share your summary with your adviser to agree the next step."},
 "challenge": {
  "start": "Challenge: complete your first step, '{next_step}', this week.",
  "step_done": "Step {done} cleared! Can you clear the next one, '{next_step}', this week?",
  "halfway": "Milestone unlocked: {percent}%. Next milestone: 75%.",
  "behind": "Quick challenge: spend 30 minutes on '{next_step}' today.",
  "welcome_back": "Back in the game. Beat your last session with a little more time on '{next_step}'.",
  "plan_done": "All {total} {steps_word} cleared. Milestone unlocked: plan complete."}}
ACTION = {"accountability": "share_summary"}
def plan_numbers(steps: list[dict], progress: dict[int, int], weekly_hours: int | None, matched_count: int = 0) -> dict:
    """steps: [{order, skill_name, est_hours}], progress: {order: percent 0..100}."""
    tot = sum(s["est_hours"] for s in steps) or 1.0
    done_h = sum(s["est_hours"] * progress.get(s["order"], 0) / 100 for s in steps)
    done = [s for s in steps if progress.get(s["order"], 0) >= 100]; todo = [s for s in steps if progress.get(s["order"], 0) < 100]
    left = tot - done_h
    return dict(total=len(steps), steps_word="step" if len(steps) == 1 else "steps", done=len(done), percent=int(round(100 * done_h / tot)), hours_total=int(round(tot)), hours_left=int(round(left)),
                weekly_hours=weekly_hours or 6, weeks_left=max(1, -(-int(round(left)) // (weekly_hours or 6))), matched_count=matched_count,
                next_step=(todo[0]["skill_name"] if todo else ""), last_step=(done[-1]["skill_name"] if done else ""))
def detect_event(before_pct: int, after_pct: int, steps_done_before: int, steps_done_after: int, total_steps: int, days_since_last: int | None, first_update: bool):
    if total_steps and steps_done_after == total_steps and steps_done_before < total_steps: return "plan_done"
    if steps_done_after > steps_done_before: return "step_done"
    if before_pct < 50 <= after_pct: return "halfway"
    if days_since_last is not None and days_since_last >= 7: return "welcome_back"
    if first_update and after_pct > 0 or (before_pct == 0 and after_pct > 0): return "start"
    return None
def select(styles: list[str], event: str, nums: dict, shown_count: int):
    """Alternates between the worker's chosen styles. Returns (style, text, suggested_action)."""
    st = styles[shown_count % len(styles)]; return st, LIB[st][event].format(**nums), ACTION.get(st, "none")

# ---- model-written messages: the language model may only REWRITE a template; code checks the result ----
VOICE = {"progress": "upbeat and clear, a little cheeky about the numbers", "goals": "focused and playful, like a coach who enjoys a good target",
         "encouragement": "warm, sassy and fun, like a best friend who believes in them and says so with a wink",
         "accountability": "friendly nudge with light teasing, never guilt", "challenge": "cheeky and game-like, competitive but kind"}

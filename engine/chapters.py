"""Progress from chapters. Pure. Hours-weighted only when every chapter has hours; otherwise each chapter counts equally."""
def percent(chapters: list, done_ids: set) -> int:
    if not chapters: return 0
    if all(isinstance(c.get("est_hours"), (int, float)) and c["est_hours"] > 0 for c in chapters):
        tot = sum(c["est_hours"] for c in chapters); got = sum(c["est_hours"] for c in chapters if c["chapter_id"] in done_ids)
    else:
        tot, got = len(chapters), sum(1 for c in chapters if c["chapter_id"] in done_ids)
    return int(round(100 * got / tot))

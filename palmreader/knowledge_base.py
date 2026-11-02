"""Task 04: curated palmistry knowledge base + small TF-IDF retriever (RAG).

The passages paraphrase widely repeated *traditional* palmistry teaching. They are
cultural/entertainment material, not scientific facts.
"""
from __future__ import annotations
import math
import re
from collections import Counter

PASSAGES: list[dict] = [
    # --- major lines ---------------------------------------------------------
    dict(id="heart-1", topic="heart_line", text="Heart line: the crease running across the upper palm below the fingers. Tradition links it to emotional style, affection and how a person relates to others. A long, clear line is read as emotional openness; a short or faint one as reserve."),
    dict(id="heart-2", topic="heart_line", text="A heart line that curves upward toward the index/middle finger gap is traditionally read as warm and expressive in relationships; a straight, flatter line as more practical and measured about feelings."),
    dict(id="head-1", topic="head_line", text="Head line: the crease crossing the middle of the palm. Tradition links it to thinking style, focus and problem solving. A long line suggests thorough, detailed thinking; a short line is read as direct and decisive."),
    dict(id="head-2", topic="head_line", text="A sloping head line is traditionally read as imaginative and creative thinking; a straight head line as logical, practical and analytical. A line that begins joined to the life line is read as cautious in youth."),
    dict(id="life-1", topic="life_line", text="Life line: the curve around the base of the thumb. Tradition associates it with vitality, energy and major life changes. It is NOT a measure of lifespan in modern palmistry; length does not predict how long someone lives."),
    dict(id="life-2", topic="life_line", text="A deep, clear life line is read as steady energy and resilience; a faint or broken line as periods of change or adjustment. A wide curve is read as enthusiasm, a tight curve around the thumb as lower stamina."),
    dict(id="fate-1", topic="fate_line", text="Fate line (line of destiny): a vertical crease running up the centre of the palm toward the middle finger. Tradition links it to career path, direction and external influences. Many people have no fate line, which is considered normal and says nothing negative."),
    dict(id="fate-2", topic="fate_line", text="A strong fate line starting low in the palm is read as an early, focused career direction; one starting mid-palm as a path found later; a faint or absent one as a flexible, self-directed or changeable path."),
    # --- shape ---------------------------------------------------------------
    dict(id="shape-earth", topic="palm_shape", text="Earth hand: square palm, shorter fingers. Traditionally described as practical, reliable, grounded and hard-working."),
    dict(id="shape-air", topic="palm_shape", text="Air hand: square palm, longer fingers. Traditionally described as curious, communicative, analytical and sociable."),
    dict(id="shape-fire", topic="palm_shape", text="Fire hand: rectangular palm, shorter fingers. Traditionally described as energetic, spontaneous, confident and enthusiastic."),
    dict(id="shape-water", topic="palm_shape", text="Water hand: rectangular palm, longer fingers. Traditionally described as intuitive, sensitive, empathic and reflective."),
    # --- themes --------------------------------------------------------------
    dict(id="career-1", topic="career", text="Career themes in palmistry combine the fate line (direction), head line (working style) and the shape of the hand. Clear fate and head lines are read as focus and planning; absent or faint ones as adaptability and varied paths."),
    dict(id="money-1", topic="finance", text="Financial themes are traditionally read from the fate line, head line and the fullness of the palm base. A clear head line is linked with careful money thinking, a strong fate line with steady effort. These are folklore, not financial advice."),
    dict(id="love-1", topic="relationships", text="Relationship themes are read mainly from the heart line, with the head line showing how feelings are balanced with reasoning. Palmistry says nothing reliable about compatibility or whether a relationship will last."),
    dict(id="person-1", topic="personality", text="Personality themes combine hand type (Earth/Air/Fire/Water), the heart line (emotion) and the head line (thinking). Combinations are described as tendencies, never fixed traits."),
    dict(id="future-1", topic="future", text="Future narratives in palmistry are symbolic stories about possible directions, such as change, growth or focus. They are not predictions and must not be treated as forecasts of events."),
    # --- left vs right -------------------------------------------------------
    dict(id="lr-1", topic="left_right", text="Left versus right: a common tradition says the non-dominant hand shows inherited potential and the dominant hand shows how that potential has developed through life. Differences between hands are read as personal change or growth."),
    dict(id="lr-2", topic="left_right", text="When a line is clear on one hand and faint or absent on the other, tradition reads this as a theme that is emerging or fading. Lighting and pose can also cause such differences, so they should be treated cautiously."),
    # --- safeguards ----------------------------------------------------------
    dict(id="safe-1", topic="disclaimer", text="Palmistry is a cultural and entertainment practice. It has no scientific validity for predicting personality, health, wealth, relationships or future events. Never use it for medical, financial, employment or relationship decisions."),
]

_TOKEN = re.compile(r"[a-z]+")
_STOP = set("the a an of to in and or is are as it its be by for on with that this from at not no".split())


def _tok(s: str) -> list[str]:
    return [t for t in _TOKEN.findall(s.lower()) if t not in _STOP]


class Retriever:
    def __init__(self, passages=PASSAGES):
        self.passages = passages
        self.docs = [Counter(_tok(p["text"] + " " + p["topic"].replace("_", " "))) for p in passages]
        df = Counter(t for d in self.docs for t in d)
        n = len(self.docs)
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.norms = [self._norm(d) for d in self.docs]

    def _norm(self, d: Counter) -> float:
        return math.sqrt(sum((c * self.idf.get(t, 1.0)) ** 2 for t, c in d.items())) or 1.0

    def search(self, query: str, k: int = 4, topics: list[str] | None = None) -> list[dict]:
        q = Counter(_tok(query))
        qn = self._norm(q)
        scored = []
        for p, d, dn in zip(self.passages, self.docs, self.norms):
            s = sum(q[t] * d[t] * self.idf.get(t, 1.0) ** 2 for t in q if t in d) / (qn * dn)
            if topics and p["topic"] in topics:
                s += 0.5
            scored.append((s, p))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [dict(p, score=round(s, 3)) for s, p in scored[:k] if s > 0]

    def for_features(self, feats: dict[str, dict]) -> list[dict]:
        """Retrieve passages that match what was actually detected (plus general themes)."""
        wanted: list[str] = ["disclaimer", "left_right", "personality", "career", "finance", "relationships", "future"]
        seen: dict[str, dict] = {}
        for side_feats in feats.values():
            for name, d in side_feats.get("lines", {}).items():
                if d["status"] != "not_detected":
                    wanted.append(name)
            hand = side_feats.get("palm", {}).get("palmistry_hand_type")
            if hand:
                wanted.append(f"shape-{hand.lower()}")
        wanted.append("palm_shape")
        for p in self.passages:
            if p["topic"] in wanted or p["id"] in wanted:
                if p["topic"] == "palm_shape" and p["id"] not in wanted:
                    continue
                seen[p["id"]] = p
        return list(seen.values())

from devopsmind.state import load_state, save_state
from devopsmind.challenge_resolver import list_all_challenges
from devopsmind.mentor.rotation import load_rotation_memory, save_rotation_memory
from devopsmind.mentor.stagnation import detect_stagnation_once


class RuleBasedMentor:
    """
    Human-style mentor.
    Guides direction, enforces rotation, protects confidence.
    """

    def generate(self):
        state = load_state()

        progress = state.get("progress", {})
        completed = set(progress.get("completed", []))
        by_stack = progress.get("by_stack", {})
        attempts = state.get("attempts", {})

        # ---------------------------------------------
        # Detect stagnation (shown only once per challenge)
        # ---------------------------------------------
        stagnation = detect_stagnation_once()

        # Challenges failed too many times should be avoided
        stuck_challenges = {
            cid for cid, count in attempts.items()
            if count >= 3
        }

        # ---------------------------------------------
        # Load challenge metadata
        # ---------------------------------------------
        all_challenges = list_all_challenges()

        # Exclude completed & stuck challenges
        candidates = [
            c for c in all_challenges
            if c["id"] not in completed
            and c["id"] not in stuck_challenges
        ]

        # ---------------------------------------------
        # Confidence scoring per stack
        # ---------------------------------------------
        stack_scores = {}
        for c in all_challenges:
            stack = c["stack"]
            stack_scores.setdefault(stack, {"total": 0, "completed": 0})
            stack_scores[stack]["total"] += 1

        for stack, count in by_stack.items():
            if stack in stack_scores:
                stack_scores[stack]["completed"] = count

        for s in stack_scores.values():
            s["score"] = (
                s["completed"] / s["total"] if s["total"] else 0
            )

        # Sort stacks by lowest confidence first
        weak_stacks = sorted(
            stack_scores.items(),
            key=lambda x: x[1]["score"]
        )

        # ---------------------------------------------
        # Difficulty ordering (gentle progression)
        # ---------------------------------------------
        difficulty_order = ["Easy", "Medium", "Hard", "Expert", "Master"]

        # ---------------------------------------------
        # Rotation memory (never suggest same set twice)
        # ---------------------------------------------
        rotation_memory = load_rotation_memory()

        recommendations = []
        used_stacks = set()

        for stack, _ in weak_stacks:
            if len(recommendations) >= 3:
                break

            stack_candidates = [
                c for c in candidates
                if c["stack"] == stack
            ]

            stack_candidates.sort(
                key=lambda c: difficulty_order.index(c["difficulty"])
            )

            for c in stack_candidates:
                if c["id"] in rotation_memory:
                    continue
                if c["stack"] in used_stacks:
                    continue

                recommendations.append(c)
                used_stacks.add(c["stack"])
                break

        # Fallback if not enough recommendations
        if len(recommendations) < 3:
            for c in candidates:
                if len(recommendations) >= 3:
                    break
                if c["id"] in rotation_memory:
                    continue
                if c["stack"] in used_stacks:
                    continue
                recommendations.append(c)
                used_stacks.add(c["stack"])

        # Save rotation memory
        save_rotation_memory([c["id"] for c in recommendations])

        # ---------------------------------------------
        # Learning style detection
        # ---------------------------------------------
        stacks_touched = len(by_stack)
        total_completed = len(completed)

        if stacks_touched >= 4 and total_completed <= 10:
            learning_style = {
                "label": "🌍 Explorer",
                "explanation": (
                    "You spread effort across multiple stacks. "
                    "This builds wide intuition early."
                ),
            }
        else:
            learning_style = {
                "label": "🎯 Specialist",
                "explanation": (
                    "You prefer depth over breadth, staying with a topic "
                    "until it feels solid."
                ),
            }

        # ---------------------------------------------
        # Confidence snapshot
        # ---------------------------------------------
        confidence = {}
        for stack, meta in stack_scores.items():
            score = meta["score"]
            if score == 0:
                label = "🌱 Untouched"
            elif score < 0.4:
                label = "🧩 Emerging"
            else:
                label = "🧠 Familiar"

            confidence[stack.capitalize()] = {
                "label": label,
                "completed": meta["completed"],
                "total": meta["total"],
            }

        # ---------------------------------------------
        # Final mentor output
        # ---------------------------------------------
        return {
            "stagnation": stagnation,
            "recommendations": recommendations,
            "confidence": confidence,
            "learning_style": learning_style,
            "cadence": "3–4 focused sessions per week",
            "why": (
                "They sit in stacks where your confidence is still forming, "
                "and their difficulty nudges growth without overload."
            ),
        }

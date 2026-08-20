"""Regression checks for Arthur's optional local-only gesture classifier."""

from gesture_runtime import HandGestureClassifier


def hand_points(wrist_x=0.5, open_palm=False, pinched=False):
    points = [(0.5, 0.85)] * 21
    points[0] = (wrist_x, 0.8)
    points[4] = (0.15, 0.45)
    points[8] = (0.82, 0.72)
    points[12] = (0.65, 0.72)
    points[5] = (0.5, 0.65)
    if pinched:
        points[4] = (0.48, 0.43)
        points[8] = (0.50, 0.43)
    if open_palm:
        for tip, joint in ((8, 6), (12, 10), (16, 14), (20, 18)):
            points[tip] = (points[tip][0], 0.2)
            points[joint] = (points[joint][0], 0.62)
    return points


def main():
    classifier = HandGestureClassifier()
    assert classifier.classify(hand_points(pinched=True)).name == "pinch"
    assert classifier.classify(hand_points(open_palm=True)).name == "discard_request"
    classifier = HandGestureClassifier()
    assert classifier.classify(hand_points(wrist_x=0.2)) is None
    assert classifier.classify(hand_points(wrist_x=0.5)).name == "swipe_right"
    print("Arthur local gesture checks passed.")


if __name__ == "__main__":
    main()

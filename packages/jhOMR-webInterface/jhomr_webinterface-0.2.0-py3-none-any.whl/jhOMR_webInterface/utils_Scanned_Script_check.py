import cv2
import numpy as np
import os

def estimate_scanned_page_orientation(image_path):
    """
    Detect rectangles in the page and estimate orientation using soft criteria.
    Returns rotation in degrees: 0, 90, 180, 270
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image:", image_path)
        return None

    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to binary (invert so objects become white)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidate_rects = []

    # --- rectangle detection ---
    for cnt in contours:
        x, y, w_rect, h_rect = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)
        aspect_ratio = w_rect / float(h_rect)

        # Ignore border-touching or nearly-full-image rectangles
        if x <= 5 or y <= 5 or x + w_rect >= width - 5 or y + h_rect >= height - 5:
            continue
        if w_rect >= 0.95 * width and h_rect >= 0.95 * height:
            continue

        # Keep rectangles with reasonable aspect ratio
        if 0.7 < aspect_ratio < 5.0:
            candidate_rects.append({
                "center": (x + w_rect//2, y + h_rect//2),
                "area": area
            })

    if not candidate_rects:
        print("No candidate rectangles found!")
        return None

    # Sort candidates by area descending
    candidate_rects.sort(key=lambda r: r["area"], reverse=True)

    # Filter top rectangles where smallest >= 0.25 * largest, up to 3
    top_rects = []
    for rect in candidate_rects:
        if len(top_rects) < 3:
            if not top_rects or rect["area"] >= 0.25 * top_rects[0]["area"]:
                top_rects.append(rect)

    if len(top_rects) < 1:
        print("Not enough rectangles for orientation inference.")
        return None

    # --- orientation inference ---
    rotations = [0, 90, 180, 270]
    confidences = []

    for rot in rotations:
        score = 0.0

        for r in top_rects:
            cx, cy = r["center"]

            # Rotate coordinates virtually
            if rot == 0:
                rx, ry = cx, cy
            elif rot == 90:
                rx, ry = height - cy, cx
            elif rot == 180:
                rx, ry = width - cx, height - cy
            elif rot == 270:
                rx, ry = cy, width - cx

            # Soft criterion: closer to top -> higher score
            score += 1 - (ry / height)
        
        # Soft criterion: relative horizontal order (largest rectangle to right)
        if len(top_rects) > 1:
            # Compare smallest and largest
            small = min(top_rects, key=lambda r: r['area'])
            large = max(top_rects, key=lambda r: r['area'])
            scx, scy = small['center']
            lcx, lcy = large['center']
            # Rotate points
            if rot == 0:
                rsx, rsY = scx, scy
                rlx, rly = lcx, lcy
            elif rot == 90:
                rsx, rsY = height - scy, scx
                rlx, rly = height - lcy, lcx
            elif rot == 180:
                rsx, rsY = width - scx, height - scy
                rlx, rly = width - lcx, height - lcy
            elif rot == 270:
                rsx, rsY = scy, width - scx
                rlx, rly = lcy, width - lcx

            score += max(0, (rlx - rsx) / width)

        confidences.append(score)

    best_rot = rotations[np.argmax(confidences)]
    return best_rot


def estimate_scanned_page_orientation_long_omr(image_or_path):
    """
    Accepts either:
      - image path (str / Path)
      - OpenCV image (numpy ndarray)

    Returns:
      0 if largest rectangle is at bottom
      180 otherwise
    """

    # --- Load image if a path is provided ---
    if isinstance(image_or_path, (str, os.PathLike)):
        img = cv2.imread(str(image_or_path))
        if img is None:
            print("Failed to load image:", image_or_path)
            return None

    # --- Image already provided ---
    elif isinstance(image_or_path, np.ndarray):
        img = image_or_path.copy()

    else:
        raise TypeError(
            "image_or_path must be a file path or a numpy ndarray (OpenCV image)"
        )

    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to binary (invert so objects become white)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    candidate_rects = []

    for cnt in contours:
        x, y, w_rect, h_rect = cv2.boundingRect(cnt)
        area = cv2.contourArea(cnt)

        # Ignore border-touching or nearly-full-image rectangles
        if x <= 5 or y <= 5 or x + w_rect >= width - 5 or y + h_rect >= height - 5:
            continue
        if w_rect >= 0.95 * width and h_rect >= 0.95 * height:
            continue

        candidate_rects.append({
            "center": (x + w_rect // 2, y + h_rect // 2),
            "area": area
        })

    if not candidate_rects:
        print("No candidate rectangles found!")
        return None

    largest_rect = max(candidate_rects, key=lambda r: r["area"])
    _, cy = largest_rect["center"]

    return 0 if cy > height / 2 else 180



# -----------------------------
# Example usage
# -----------------------------
#img_path = '1.jpg'
#rotation = estimate_page_rotation(img_path)
#print(f"Estimated page rotation: {rotation} degrees")